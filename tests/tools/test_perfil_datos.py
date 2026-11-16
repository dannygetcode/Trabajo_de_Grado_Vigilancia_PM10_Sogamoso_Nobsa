"""Funciones puras del normalizador de datos IDEAM (tools/perfil_datos.py)."""

import pandas as pd
import pytest

from tools.perfil_datos import a_utc_iso, limpiar_valor

pytestmark = pytest.mark.unitaria


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [("47", "47"), ("0.50", "0.50"), ("12.86", "12.86"), ("1,091.39", "1091.39"), ("2,836", "2836")],
)
def test_limpiar_valor_conserva_los_digitos(texto: str, esperado: str) -> None:
    assert limpiar_valor(texto) == esperado


@pytest.mark.parametrize("texto", ["", "abc", "1,09", "1.2.3", "12,5"])
def test_limpiar_valor_rechaza_lo_que_no_es_numero(texto: str) -> None:
    with pytest.raises(ValueError, match="no numérico"):
        limpiar_valor(texto)


def test_a_utc_iso_suma_cinco_horas_y_cruza_el_dia() -> None:
    local = pd.Series(pd.to_datetime(["2020-01-01 00:00", "2020-12-31 20:00"]))
    assert a_utc_iso(local).tolist() == ["2020-01-01T05:00:00Z", "2021-01-01T01:00:00Z"]
