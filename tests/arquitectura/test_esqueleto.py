"""Esqueleto de servicios (tarea 4 del plan del Sprint 0, ADR-0001 decisión 2)."""

from __future__ import annotations

import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import svca_ingesta.api
import svca_normativo.api
import svca_notificaciones.api
import svca_pronostico.api
import svca_reloj.api
import svca_simulador.api
from svca_comun.configuracion import ConfiguracionBase, ConfiguracionInvalida, cargar
from svca_nucleo.app import Configuracion as ConfigNucleo
from svca_nucleo.app import crear_app as crear_nucleo

WEB = "https://web.ejemplo"
SERVICIOS = {
    "reloj": svca_reloj.api,
    "ingesta": svca_ingesta.api,
    "normativo": svca_normativo.api,
    "notificaciones": svca_notificaciones.api,
    "pronostico": svca_pronostico.api,
    "simulador": svca_simulador.api,
}


@pytest.fixture(autouse=True)
def _entorno_limpio(monkeypatch: pytest.MonkeyPatch) -> None:
    """Quita la configuración del servicio, pero no las variables de las pruebas."""
    for var in [
        v for v in os.environ if v.startswith("SVCA_") and not v.startswith(("SVCA_PRUEBAS_", "SVCA_HUMO_"))
    ]:
        monkeypatch.delenv(var)


@pytest.mark.unitaria
@pytest.mark.parametrize("nombre", SERVICIOS)
def test_cada_servicio_arranca_solo(nombre: str) -> None:
    app: FastAPI = SERVICIOS[nombre].crear_app()
    with TestClient(app) as c:
        r = c.get("/v1/salud")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"
    assert r.json()["servicio"] == nombre


@pytest.mark.unitaria
def test_nucleo_monta_cuatro_servicios_y_el_planificador() -> None:
    with TestClient(crear_nucleo()) as c:
        for prefijo in ("reloj", "ingesta", "normativo", "notificaciones"):
            r = c.get(f"/{prefijo}/v1/salud")
            assert r.status_code == 200, prefijo
            assert r.json()["servicio"] == prefijo
        r = c.get("/salud")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["estado"] == "ok"
    assert set(cuerpo["servicios"]) == {"reloj", "ingesta", "normativo", "notificaciones", "planificador"}
    assert cuerpo["servicios"]["planificador"]["estado"] == "ok"


@pytest.mark.unitaria
def test_nucleo_detiene_el_planificador_al_apagar() -> None:
    app = crear_nucleo()
    with TestClient(app):
        tarea = app.state.planificador
        assert not tarea.done()
    assert tarea.done()


@pytest.mark.unitaria
@pytest.mark.parametrize(
    "app",
    [
        pytest.param(lambda: crear_nucleo(ConfigNucleo(origenes=WEB)), id="nucleo"),
        pytest.param(
            lambda: svca_pronostico.api.crear_app(svca_pronostico.api.Configuracion(origenes=WEB)),
            id="pronostico",
        ),
        pytest.param(
            lambda: svca_simulador.api.crear_app(svca_simulador.api.Configuracion(origenes=WEB)),
            id="simulador",
        ),
    ],
)
def test_cors_solo_para_los_origenes_configurados(app) -> None:  # type: ignore[no-untyped-def]
    ruta = "/salud" if "nucleo" in app().title else "/v1/salud"
    with TestClient(app()) as c:
        permitido = c.get(ruta, headers={"Origin": WEB})
        ajeno = c.get(ruta, headers={"Origin": "https://ajeno.ejemplo"})
        previo = c.options(ruta, headers={"Origin": WEB, "Access-Control-Request-Method": "GET"})
    assert permitido.headers.get("access-control-allow-origin") == WEB
    assert "access-control-allow-origin" not in ajeno.headers
    assert previo.status_code == 200
    assert "access-control-allow-credentials" not in permitido.headers


@pytest.mark.unitaria
def test_cors_del_nucleo_no_se_duplica_en_los_montados() -> None:
    with TestClient(crear_nucleo(ConfigNucleo(origenes=WEB))) as c:
        r = c.get("/ingesta/v1/salud", headers={"Origin": WEB})
    assert r.headers.get_list("access-control-allow-origin") == [WEB]


@pytest.mark.unitaria
def test_salud_profunda_sin_base_responde_503() -> None:
    with TestClient(svca_ingesta.api.crear_app()) as c:
        r = c.get("/v1/salud", params={"profundo": "1"})
    assert r.status_code == 503
    assert r.json()["codigo"] == "BASE_NO_DISPONIBLE"


@pytest.mark.unitaria
def test_salud_profunda_con_base_caida_responde_503() -> None:
    cfg = svca_ingesta.api.Configuracion(db_url="postgresql://x:y@127.0.0.1:1/nada")
    with TestClient(svca_ingesta.api.crear_app(cfg)) as c:
        r = c.get("/v1/salud", params={"profundo": "true"})
    assert r.status_code == 503


@pytest.mark.unitaria
def test_salud_profunda_con_cadena_mal_formada_responde_503() -> None:
    cfg = svca_ingesta.api.Configuracion(db_url="mysql://no/es/postgres")
    with TestClient(svca_ingesta.api.crear_app(cfg)) as c:
        r = c.get("/v1/salud", params={"profundo": "1"})
    assert r.status_code == 503


@pytest.mark.integracion
def test_salud_profunda_con_base(base_vacia: str) -> None:
    with TestClient(svca_pronostico.api.crear_app(svca_pronostico.api.Configuracion(db_url=base_vacia))) as c:
        r = c.get("/v1/salud", params={"profundo": "1"})
    assert r.status_code == 200
    assert r.json()["base"] == "ok"


@pytest.mark.unitaria
def test_errores_con_formato_comun() -> None:
    with TestClient(svca_reloj.api.crear_app()) as c:
        no_existe = c.get("/v1/no-existe")
        invalido = c.get("/v1/salud", params={"profundo": "talvez"})
    assert no_existe.status_code == 404
    assert no_existe.json()["codigo"] == "NO_ENCONTRADO"
    assert invalido.status_code == 400
    assert invalido.json()["codigo"] == "SOLICITUD_INVALIDA"
    assert invalido.json()["errores"][0]["campo"] == "profundo"


@pytest.mark.unitaria
def test_configuracion_obligatoria_falla_al_arrancar(monkeypatch: pytest.MonkeyPatch) -> None:
    class ConObligatoria(ConfiguracionBase):
        url_reloj: str

    with pytest.raises(ConfiguracionInvalida, match="SVCA_URL_RELOJ"):
        cargar(ConObligatoria)
    monkeypatch.setenv("SVCA_URL_RELOJ", "http://nucleo:8000/reloj")
    assert cargar(ConObligatoria).url_reloj == "http://nucleo:8000/reloj"


@pytest.mark.unitaria
def test_origenes_se_leen_separados_por_comas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SVCA_ORIGENES", "https://a.ejemplo/, https://b.ejemplo")
    assert cargar(ConfiguracionBase).lista_origenes == ["https://a.ejemplo", "https://b.ejemplo"]
