"""Bucle del planificador (docs/planes/reloj-virtual.md, sección 5).

Esqueleto del Sprint 0: espera la señal de parada. HU-16 (Sprint 2) agrega el disparo de
los procesos horarios según el reloj de dominio.
"""

from __future__ import annotations

import asyncio


async def ejecutar(parar: asyncio.Event) -> None:
    """Corre hasta que `parar` se activa. No toca la base de datos (ADR-0003)."""
    await parar.wait()
