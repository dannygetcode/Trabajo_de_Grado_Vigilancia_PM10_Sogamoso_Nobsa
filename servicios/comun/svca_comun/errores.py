"""Formato único de errores `{codigo, mensaje, errores[]}` (docs/api/README.md, Convenciones).

El programa decide por `codigo`; `mensaje` es para personas. Los errores de contrato responden
400 con la lista completa, no solo el primero.
"""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorDeCampo(BaseModel):
    codigo: str
    mensaje: str
    indice: int | None = None
    campo: str | None = None


class Problema(BaseModel):
    codigo: str
    mensaje: str
    errores: list[ErrorDeCampo] = []


class ErrorDeServicio(Exception):
    """Error esperado que se responde con el formato común."""

    def __init__(
        self, estado_http: int, codigo: str, mensaje: str, errores: Sequence[ErrorDeCampo] = ()
    ) -> None:
        super().__init__(f"{codigo}: {mensaje}")
        self.estado_http = estado_http
        self.problema = Problema(codigo=codigo, mensaje=mensaje, errores=list(errores))


_CODIGOS_HTTP = {
    401: ("NO_AUTENTICADO", "Se requiere un token válido."),
    403: ("SIN_PERMISO", "El token no incluye el permiso requerido."),
    404: ("NO_ENCONTRADO", "La ruta no existe."),
    405: ("METODO_NO_PERMITIDO", "El método no está permitido en esta ruta."),
}


def _respuesta(estado: int, problema: Problema) -> JSONResponse:
    return JSONResponse(status_code=estado, content=problema.model_dump(exclude_none=True))


async def _de_servicio(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ErrorDeServicio)
    return _respuesta(exc.estado_http, exc.problema)


async def _de_validacion(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errores = [
        ErrorDeCampo(
            codigo="CAMPO_INVALIDO",
            mensaje=str(e.get("msg", "")),
            campo=".".join(str(p) for p in e.get("loc", ()) if p not in ("body", "query", "path")) or None,
        )
        for e in exc.errors()
    ]
    return _respuesta(
        400,
        Problema(codigo="SOLICITUD_INVALIDA", mensaje="La solicitud no cumple el contrato.", errores=errores),
    )


async def _de_http(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    codigo, mensaje = _CODIGOS_HTTP.get(exc.status_code, ("ERROR_HTTP", str(exc.detail)))
    return _respuesta(exc.status_code, Problema(codigo=codigo, mensaje=mensaje))


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorDeServicio, _de_servicio)
    app.add_exception_handler(RequestValidationError, _de_validacion)
    app.add_exception_handler(StarletteHTTPException, _de_http)
