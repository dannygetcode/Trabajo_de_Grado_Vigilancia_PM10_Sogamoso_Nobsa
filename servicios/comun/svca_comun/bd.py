"""Motor de SQLAlchemy Core sobre psycopg 3 (ADR-0002).

- Las sentencias preparadas del servidor se desactivan (`prepare_threshold=None`): en la nube la
  base se usa a través del agrupador de Neon en modo transacción, que no las admite (ADR-0003).
- El grupo no abre conexiones hasta que se usan; el ajuste fino para que una base ociosa pueda
  suspenderse (cerrar conexiones inactivas) se decide con HU-07, cuando haya acceso real a datos.
"""

from __future__ import annotations

from sqlalchemy import Engine, create_engine, text


def url_sqlalchemy(url: str) -> str:
    """Acepta `postgresql://` (la forma de Neon y de psql) y fija el controlador psycopg 3."""
    for prefijo in ("postgresql+psycopg://", "postgresql://", "postgres://"):
        if url.startswith(prefijo):
            return "postgresql+psycopg://" + url[len(prefijo) :]
    raise ValueError("la cadena de conexión debe empezar por postgresql://")


def crear_motor(url: str, *, tamano: int = 5) -> Engine:
    return create_engine(
        url_sqlalchemy(url),
        pool_size=tamano,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"prepare_threshold": None, "connect_timeout": 10},
    )


def comprobar(motor: Engine) -> None:
    """`SELECT 1`. Lanza la excepción del controlador si la base no responde."""
    with motor.connect() as con:
        con.execute(text("SELECT 1"))
