"""Prueba de humo contra un sistema levantado: el compose o la nube.

Solo usa HTTP. Las URL llegan por variables; sin ellas, la prueba se omite:
    SVCA_HUMO_URL_NUCLEO, SVCA_HUMO_URL_PRONOSTICO, SVCA_HUMO_URL_SIMULADOR, SVCA_HUMO_URL_WEB
SVCA_HUMO_ESPERA_S (180 por defecto) da tiempo a que un contenedor dormido despierte (ADR-0003).
"""

from __future__ import annotations

import os
import time

import httpx
import pytest

pytestmark = pytest.mark.humo

ESPERA_S = float(os.environ.get("SVCA_HUMO_ESPERA_S", "180"))


def _url(nombre: str) -> str:
    url = os.environ.get(f"SVCA_HUMO_URL_{nombre}")
    if not url:
        pytest.skip(f"SVCA_HUMO_URL_{nombre} no está definida")
    return url.rstrip("/")


def _get(url: str, **kwargs: object) -> httpx.Response:
    """GET que tolera el arranque en frío: reintenta errores de red y 502, 503 y 504."""
    limite = time.monotonic() + ESPERA_S
    while True:
        try:
            r = httpx.get(url, timeout=30, follow_redirects=True, **kwargs)  # type: ignore[arg-type]
            if r.status_code not in (502, 503, 504) or time.monotonic() > limite:
                return r
        except httpx.TransportError:
            if time.monotonic() > limite:
                raise
        time.sleep(3)


@pytest.mark.parametrize(
    ("nombre", "ruta"),
    [("NUCLEO", "/salud"), ("PRONOSTICO", "/v1/salud"), ("SIMULADOR", "/v1/salud")],
)
@pytest.mark.parametrize("profundo", [False, True], ids=["simple", "profundo"])
def test_salud(nombre: str, ruta: str, profundo: bool) -> None:
    r = _get(_url(nombre) + ruta, params={"profundo": "true"} if profundo else {})
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "ok"


def test_nucleo_expone_los_cuatro_servicios() -> None:
    base = _url("NUCLEO")
    for prefijo in ("reloj", "ingesta", "normativo", "notificaciones"):
        assert _get(f"{base}/{prefijo}/v1/salud").status_code == 200, prefijo


def test_web_responde_y_las_apis_la_aceptan_por_cors() -> None:
    web = _url("WEB")
    r = _get(web + "/")
    assert r.status_code == 200
    assert '<div id="raiz">' in r.text
    origen = os.environ.get("SVCA_HUMO_ORIGEN", web)
    salud = _get(_url("NUCLEO") + "/salud", headers={"Origin": origen})
    assert salud.headers.get("access-control-allow-origin") == origen
