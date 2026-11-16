"""Configuración por variables de entorno `SVCA_*` (ADR-0002).

Cada servicio define una subclase con sus campos. Un campo sin valor por defecto es obligatorio:
si falta, `cargar` falla al arrancar con la lista de variables que faltan, en lugar de que el
servicio arranque a medias.
"""

from __future__ import annotations

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfiguracionInvalida(Exception):
    """La configuración no permite arrancar el servicio."""


class ConfiguracionBase(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SVCA_", extra="ignore", frozen=True)

    db_url: str | None = None
    """Cadena PostgreSQL. Opcional en el esqueleto; con HU-06 cada servicio tendrá la suya."""

    origenes: str = ""
    """Orígenes permitidos por CORS, separados por comas (la URL de la web). Vacío: ninguno."""

    @property
    def lista_origenes(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.origenes.split(",") if o.strip()]


def cargar[C: ConfiguracionBase](clase: type[C]) -> C:
    """Lee la configuración del entorno o falla con un mensaje que nombra las variables."""
    try:
        return clase()
    except ValidationError as e:
        prefijo = clase.model_config.get("env_prefix", "")
        faltan = [f"{prefijo}{'_'.join(str(p) for p in err['loc']).upper()}" for err in e.errors()]
        raise ConfiguracionInvalida("Configuración inválida o incompleta: " + ", ".join(faltan)) from e
