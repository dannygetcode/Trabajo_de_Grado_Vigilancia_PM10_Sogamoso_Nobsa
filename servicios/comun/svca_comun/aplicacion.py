"""Fábrica de aplicaciones FastAPI con lo que todo servicio comparte.

Cada servicio llama a `crear_aplicacion` desde su `api/` y agrega sus rutas. Incluye:
el formato común de errores, `GET /v1/salud` (anónima) y, si la aplicación es la raíz del
proceso, CORS con `SVCA_ORIGENES`. Cuando el núcleo monta varios servicios, solo el núcleo
aplica CORS (`independiente=False` en los montados), para no duplicar cabeceras.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine

from svca_comun.bd import comprobar, crear_motor
from svca_comun.configuracion import ConfiguracionBase
from svca_comun.errores import ErrorDeServicio, Problema, registrar_manejadores


def version_de(paquete: str) -> str:
    try:
        return version(paquete)
    except PackageNotFoundError:
        return "0.0.0"


def aplicar_cors(app: FastAPI, origenes: list[str]) -> None:
    """Lista cerrada de orígenes; los tokens viajan en `Authorization`, nunca en cookies."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origenes,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=600,
    )


class _MotorPerezoso:
    """Crea el motor en la primera consulta: arrancar no debe abrir conexiones ni exigir la base."""

    def __init__(self, url: str | None) -> None:
        self._url = url
        self._motor: Engine | None = None

    def obtener(self) -> Engine | None:
        if self._motor is None and self._url:
            self._motor = crear_motor(self._url, tamano=2)
        return self._motor

    def cerrar(self) -> None:
        if self._motor is not None:
            self._motor.dispose()


def crear_aplicacion(
    servicio: str,
    paquete: str,
    config: ConfiguracionBase,
    *,
    independiente: bool = True,
    **opciones_fastapi: Any,
) -> FastAPI:
    ver = version_de(paquete)
    app = FastAPI(title=f"svca {servicio}", version=ver, **opciones_fastapi)
    registrar_manejadores(app)
    motor = _MotorPerezoso(config.db_url)
    app.state.motor = motor

    @app.get(
        "/v1/salud",
        tags=["salud"],
        summary="Comprobación de vida",
        operation_id="salud",
        responses={503: {"model": Problema}},
    )
    def salud(profundo: bool = Query(default=False)) -> dict[str, str]:
        cuerpo = {"estado": "ok", "servicio": servicio, "version": ver}
        if profundo:
            try:
                m = motor.obtener()
                if m is None:
                    raise ErrorDeServicio(503, "BASE_NO_DISPONIBLE", "No hay base de datos configurada.")
                comprobar(m)
            except ErrorDeServicio:
                raise
            except Exception as e:  # cadena mal formada o base caída: "no disponible"
                raise ErrorDeServicio(503, "BASE_NO_DISPONIBLE", "La base de datos no respondió.") from e
            cuerpo["base"] = "ok"
        return cuerpo

    if independiente:
        aplicar_cors(app, config.lista_origenes)
    return app
