#!/usr/bin/env python3
"""Aplica los scripts de db/ que falten, en orden, igual en el compose, en CI y en la nube.

- Cada script `db/NN_*.sql` se aplica en su propia transacción.
- La cuenta de lo aplicado vive en `svca_meta.script_aplicado`, un esquema aparte para que
  `svca` conserve sus tablas (ADR-0001, decisión 4).
- Un script ya aplicado no se edita: si su SHA-256 cambió, la herramienta falla sin aplicar
  nada. Los cambios van en un script nuevo con el número siguiente.
- Espera a que la base acepte conexiones, para poder usarse como contenedor de arranque.

Uso:
    python tools/db_aplicar.py [--url postgresql://...] [--hasta 10] [--db db] [--espera 60]

Si no se da --url, se lee SVCA_DB_URL.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import psycopg

RAIZ = Path(__file__).resolve().parent.parent
PATRON = re.compile(r"^(\d{2})_[\w-]+\.sql$")

CREAR_META = """
CREATE SCHEMA IF NOT EXISTS svca_meta;
CREATE TABLE IF NOT EXISTS svca_meta.script_aplicado (
  nombre      TEXT PRIMARY KEY,
  sha256      CHAR(64) NOT NULL,
  -- Hora de la base: es metadato de operación, no hora de dominio, así que no viene del reloj.
  aplicado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


class ErrorMigracion(Exception):
    """Error que impide seguir. El script que falla se revierte; los anteriores quedan aplicados."""


@dataclass(frozen=True)
class Script:
    numero: int
    nombre: str
    ruta: Path
    sha256: str

    @property
    def sql(self) -> str:
        return self.ruta.read_text(encoding="utf-8")


def resumen(ruta: Path) -> str:
    """SHA-256 del contenido con fin de línea LF, para que dé igual en Windows y en Linux."""
    return hashlib.sha256(ruta.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def listar(carpeta: Path) -> list[Script]:
    scripts = []
    for ruta in sorted(carpeta.glob("*.sql")):
        m = PATRON.match(ruta.name)
        if not m:
            raise ErrorMigracion(f"nombre de script inválido: {ruta.name} (se espera NN_nombre.sql)")
        scripts.append(Script(int(m.group(1)), ruta.name, ruta, resumen(ruta)))
    numeros = [s.numero for s in scripts]
    if len(set(numeros)) != len(numeros):
        raise ErrorMigracion(f"números de script repetidos en {carpeta}")
    return scripts


def conectar(url: str, espera_s: float) -> psycopg.Connection:
    limite = time.monotonic() + espera_s
    while True:
        try:
            # autocommit: cada `transaction()` es una transacción real y no un savepoint de una
            # transacción implícita; así un script que falla no revierte los anteriores.
            return psycopg.connect(url, connect_timeout=5, autocommit=True)
        except psycopg.OperationalError as e:
            if time.monotonic() >= limite:
                raise ErrorMigracion(f"la base no acepta conexiones tras {espera_s:.0f} s: {e}") from e
            time.sleep(1)


def aplicar(
    url: str, carpeta: Path = RAIZ / "db", hasta: int | None = None, espera_s: float = 60
) -> list[str]:
    """Aplica los scripts pendientes y devuelve sus nombres. No hace nada si no hay pendientes."""
    scripts = [s for s in listar(carpeta) if hasta is None or s.numero <= hasta]
    with conectar(url, espera_s) as con:
        with con.transaction():
            con.execute(CREAR_META)
        aplicados = dict(con.execute("SELECT nombre, sha256 FROM svca_meta.script_aplicado").fetchall())

        alterados = [s.nombre for s in scripts if s.nombre in aplicados and aplicados[s.nombre] != s.sha256]
        if alterados:
            raise ErrorMigracion(
                "scripts ya aplicados cuyo contenido cambió: "
                + ", ".join(alterados)
                + ". No se editan: agrega un script nuevo con el número siguiente."
            )
        conocidos = {s.nombre for s in listar(carpeta)}
        perdidos = sorted(set(aplicados) - conocidos)
        if perdidos:
            raise ErrorMigracion("scripts aplicados que ya no existen en db/: " + ", ".join(perdidos))

        hechos = []
        for s in scripts:
            if s.nombre in aplicados:
                continue
            try:
                with con.transaction():
                    con.execute(s.sql)  # sin parámetros: psycopg admite varias sentencias
                    con.execute(
                        "INSERT INTO svca_meta.script_aplicado (nombre, sha256) VALUES (%s, %s)",
                        (s.nombre, s.sha256),
                    )
                    con.execute("RESET search_path")
            except psycopg.Error as e:
                raise ErrorMigracion(f"{s.nombre} falló y se revirtió: {e}") from e
            hechos.append(s.nombre)
    return hechos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("SVCA_DB_URL"))
    ap.add_argument("--db", type=Path, default=RAIZ / "db", help="carpeta de los scripts")
    ap.add_argument("--hasta", type=int, help="último número de script a aplicar")
    ap.add_argument("--espera", type=float, default=60, help="segundos de espera a que la base responda")
    args = ap.parse_args(argv)
    if not args.url:
        ap.error("falta --url o la variable SVCA_DB_URL")
    try:
        hechos = aplicar(args.url, args.db, args.hasta, args.espera)
    except ErrorMigracion as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("Aplicados: " + ", ".join(hechos) if hechos else "Nada que aplicar: la base está al día.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
