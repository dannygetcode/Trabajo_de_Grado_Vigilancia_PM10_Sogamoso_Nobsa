# Imagen `nucleo` (ADR-0001). Contexto: raíz del repositorio.
#   docker build -f infra/docker/nucleo.Dockerfile -t svca-nucleo .
# --workers 1 es obligatorio: el estado del reloj vive en memoria y dos workers serían dos
# relojes distintos (docs/planes/reloj-virtual.md, sección 3.6). No escalar este contenedor.
FROM python:3.13-slim AS construccion
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
COPY servicios ./servicios
COPY simulador ./simulador
# Solo el paquete de esta unidad y sus dependencias, sin las de desarrollo, sin modo editable.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package svca-nucleo

FROM python:3.13-slim
# Bibliotecas del sistema que WeasyPrint necesita para el informe PDF (Sprint 5).
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*
RUN useradd --system --uid 10001 --home-dir /app --shell /usr/sbin/nologin svca
WORKDIR /app
COPY --from=construccion /app/.venv /app/.venv
# El migrador del compose y de la nube usa esta misma imagen: python tools/db_aplicar.py
COPY db ./db
COPY tools/db_aplicar.py ./tools/db_aplicar.py
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Fontconfig y matplotlib necesitan una caché escribible; sin disco persistente, va en /tmp.
ENV XDG_CACHE_HOME=/tmp/cache MPLCONFIGDIR=/tmp/matplotlib
USER svca
EXPOSE 8000
# Render entrega el puerto en PORT. Un solo worker (ver arriba). Las cabeceras X-Forwarded-*
# del proveedor se aceptan para conocer la IP del cliente (límite de intentos, HU-53).
CMD ["sh", "-c", "exec uvicorn --factory svca_nucleo.app:crear_app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers --forwarded-allow-ips '*'"]
