"""Interfaz HTTP del servicio normativo.

Arranque individual: `uvicorn --factory svca_normativo.api:crear_app`.
"""

from __future__ import annotations

from fastapi import FastAPI

from svca_comun.aplicacion import crear_aplicacion
from svca_comun.configuracion import ConfiguracionBase, cargar


class Configuracion(ConfiguracionBase):
    """Variables `SVCA_*` de este servicio. Por ahora solo las comunes."""


def crear_app(config: Configuracion | None = None, *, independiente: bool = True) -> FastAPI:
    """`independiente=False` cuando lo monta el núcleo: entonces el núcleo aplica CORS."""
    return crear_aplicacion(
        "normativo", "svca-normativo", config or cargar(Configuracion), independiente=independiente
    )
