"""tools/db_aplicar.py sobre PostgreSQL 16 real (tarea 3 del plan del Sprint 0)."""

from __future__ import annotations

import shutil
from pathlib import Path

import psycopg
import pytest

from tools.db_aplicar import RAIZ, ErrorMigracion, aplicar

pytestmark = pytest.mark.integracion

SCRIPTS = sorted(p.name for p in (RAIZ / "db").glob("*.sql"))


def _tablas(url: str, esquema: str = "svca") -> int:
    with psycopg.connect(url) as con:
        return con.execute(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = %s AND table_type = 'BASE TABLE'",
            (esquema,),
        ).fetchone()[0]


def _insertar_medicion(con: psycopg.Connection, valor: str = "41.2") -> int:
    return con.execute(
        """
        INSERT INTO svca.medicion (estacion_id, variable_id, inicio, fin, valor_crudo, recibida_en)
        SELECT e.id, v.id, '2022-03-01T05:00Z', '2022-03-01T06:00Z', %s, '2022-03-01T06:01Z'
        FROM svca.estacion e, svca.variable v WHERE e.codigo = 'UPTC' AND v.codigo = 'PM10'
        RETURNING id
        """,
        (valor,),
    ).fetchone()[0]


def test_base_vacia_queda_con_las_24_tablas(base_vacia: str) -> None:
    hechos = aplicar(base_vacia)
    assert hechos == SCRIPTS
    assert _tablas(base_vacia) == 24
    assert _tablas(base_vacia, "svca_meta") == 1


def test_segunda_ejecucion_no_hace_nada(base_vacia: str) -> None:
    aplicar(base_vacia)
    assert aplicar(base_vacia) == []
    with psycopg.connect(base_vacia) as con:
        assert con.execute("SELECT count(*) FROM svca.rol").fetchone()[0] == 5  # db/10 no se repitió


def test_hasta_aplica_solo_hasta_ese_numero(base_vacia: str) -> None:
    assert aplicar(base_vacia, hasta=3) == SCRIPTS[:3]
    assert aplicar(base_vacia) == SCRIPTS[3:]


def test_el_disparador_impide_cambiar_valor_crudo(base_vacia: str) -> None:
    aplicar(base_vacia)
    with psycopg.connect(base_vacia) as con:
        mid = _insertar_medicion(con)
        con.commit()
        with pytest.raises(psycopg.errors.RaiseException, match="no se puede modificar"):
            con.execute("UPDATE svca.medicion SET valor_crudo = 99 WHERE id = %s", (mid,))
        con.rollback()
        # Cambiar el estado sí se permite
        con.execute("UPDATE svca.medicion SET estado = 'VALIDO' WHERE id = %s", (mid,))


def test_medicion_duplicada_se_rechaza(base_vacia: str) -> None:
    aplicar(base_vacia)
    with psycopg.connect(base_vacia) as con:
        _insertar_medicion(con)
        with pytest.raises(psycopg.errors.UniqueViolation):
            _insertar_medicion(con, "50")


def test_script_aplicado_alterado_falla_sin_aplicar_nada(base_vacia: str, tmp_path: Path) -> None:
    carpeta = tmp_path / "db"
    shutil.copytree(RAIZ / "db", carpeta)
    aplicar(base_vacia, carpeta)
    with open(carpeta / "05_datos.sql", "a", encoding="utf-8") as f:
        f.write("\n-- cambio posterior\n")
    (carpeta / "99_nuevo.sql").write_text("CREATE TABLE svca.no_debe_existir (id int);\n", encoding="utf-8")

    with pytest.raises(ErrorMigracion, match="05_datos.sql"):
        aplicar(base_vacia, carpeta)
    assert _tablas(base_vacia) == 24


def test_script_que_falla_se_revierte_entero(base_vacia: str, tmp_path: Path) -> None:
    carpeta = tmp_path / "db"
    shutil.copytree(RAIZ / "db", carpeta)
    (carpeta / "99_roto.sql").write_text(
        "CREATE TABLE svca.a_medias (id int);\nSELECT * FROM tabla_que_no_existe;\n", encoding="utf-8"
    )
    with pytest.raises(ErrorMigracion, match="99_roto.sql"):
        aplicar(base_vacia, carpeta)
    assert _tablas(base_vacia) == 24  # 01 a 10 sí quedaron; 99 no dejó nada
    with psycopg.connect(base_vacia) as con:
        assert con.execute("SELECT count(*) FROM svca_meta.script_aplicado").fetchone()[0] == 10


def test_nombre_invalido_se_rechaza(tmp_path: Path) -> None:
    (tmp_path / "sin_numero.sql").write_text("SELECT 1;", encoding="utf-8")
    with pytest.raises(ErrorMigracion, match="nombre de script"):
        aplicar("postgresql://no-se-usa", tmp_path)
