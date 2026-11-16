"""Accesorios comunes de las pruebas.

Las pruebas de integración necesitan un PostgreSQL 16 con un usuario que pueda crear bases.
La cadena va en SVCA_PRUEBAS_DB_URL; si no está, esas pruebas se omiten con un aviso.
En local:  docker run -d --name svca-pg-pruebas -e POSTGRES_PASSWORD=pruebas -p 55432:5432 postgres:16
           SVCA_PRUEBAS_DB_URL=postgresql://postgres:pruebas@localhost:55432/postgres
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from urllib.parse import urlsplit

import psycopg
import pytest


@pytest.fixture
def base_vacia() -> Iterator[str]:
    """Crea una base de datos vacía y desechable; devuelve su URL `postgresql://`."""
    url = os.environ.get("SVCA_PRUEBAS_DB_URL")
    if not url:
        pytest.skip("SVCA_PRUEBAS_DB_URL no está definida")
    nombre = f"svca_prueba_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(url, autocommit=True) as admin:
        admin.execute(f'CREATE DATABASE "{nombre}"')
    try:
        yield urlsplit(url)._replace(path=f"/{nombre}").geturl()
    finally:
        with psycopg.connect(url, autocommit=True) as admin:
            admin.execute(f'DROP DATABASE IF EXISTS "{nombre}" WITH (FORCE)')
