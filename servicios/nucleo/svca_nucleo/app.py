"""Raíz de composición del contenedor `nucleo` (ADR-0001, decisión 2).

Monta los servicios del núcleo bajo su prefijo, arranca el planificador y aplica CORS.
No contiene reglas de negocio ni rutas propias, salvo `/salud`, que pregunta a cada servicio
por su propio contrato HTTP (transporte en proceso), igual que lo haría desde fuera.

Arranque: `uvicorn --factory svca_nucleo.app:crear_app --workers 1`.
Un solo worker: el estado del reloj vive en memoria; dos workers serían dos relojes.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

import svca_ingesta.api
import svca_normativo.api
import svca_notificaciones.api
import svca_reloj.api
from svca_comun.aplicacion import aplicar_cors, version_de
from svca_comun.configuracion import ConfiguracionBase, cargar
from svca_comun.errores import registrar_manejadores
from svca_planificador.bucle import ejecutar as ejecutar_planificador

FabricaApp = Callable[..., FastAPI]

SERVICIOS: dict[str, FabricaApp] = {
    "reloj": svca_reloj.api.crear_app,
    "ingesta": svca_ingesta.api.crear_app,
    "normativo": svca_normativo.api.crear_app,
    "notificaciones": svca_notificaciones.api.crear_app,
}


class Configuracion(ConfiguracionBase):
    """Variables del núcleo. Cada servicio montado lee además las suyas."""


def crear_app(config: Configuracion | None = None) -> FastAPI:
    cfg = config or cargar(Configuracion)
    montados = {nombre: fabrica(independiente=False) for nombre, fabrica in SERVICIOS.items()}

    @asynccontextmanager
    async def ciclo(_: FastAPI) -> AsyncIterator[None]:
        # Starlette no ejecuta el ciclo de vida de las aplicaciones montadas: se encadena aquí.
        async with AsyncExitStack() as pila:
            for sub in montados.values():
                await pila.enter_async_context(sub.router.lifespan_context(sub))
            parar = asyncio.Event()
            tarea = asyncio.create_task(ejecutar_planificador(parar), name="planificador")
            app.state.planificador = tarea
            try:
                yield
            finally:
                parar.set()
                await asyncio.wait_for(tarea, timeout=10)

    app = FastAPI(title="svca nucleo", version=version_de("svca-nucleo"), lifespan=ciclo)
    registrar_manejadores(app)
    for nombre, sub in montados.items():
        app.mount(f"/{nombre}", sub)

    @app.get("/salud", tags=["salud"], summary="Estado de cada servicio del núcleo")
    async def salud(profundo: bool = Query(default=False)) -> JSONResponse:
        estados: dict[str, Any] = {}
        params = {"profundo": "true"} if profundo else {}
        for nombre, sub in montados.items():
            transporte = httpx.ASGITransport(app=sub)
            async with httpx.AsyncClient(transport=transporte, base_url="http://nucleo") as cliente:
                r = await cliente.get("/v1/salud", params=params)
            estados[nombre] = r.json() | {"http": r.status_code}
        tarea = getattr(app.state, "planificador", None)
        estados["planificador"] = {"estado": "ok" if tarea is not None and not tarea.done() else "detenido"}
        bien = all(e.get("estado") == "ok" for e in estados.values())
        cuerpo = {"estado": "ok" if bien else "degradado", "servicios": estados}
        return JSONResponse(status_code=200 if bien else 503, content=cuerpo)

    aplicar_cors(app, cfg.lista_origenes)
    return app
