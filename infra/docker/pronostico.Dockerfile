# Imagen `pronostico` (ADR-0001). Contexto: raíz del repositorio.
#   docker build -f infra/docker/pronostico.Dockerfile -t svca-pronostico .
# Un worker: cada worker cargaría su propia copia del modelo en 512 MB (ADR-0003).
FROM python:3.13-slim AS construccion
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
COPY servicios ./servicios
COPY simulador ./simulador
# Solo el paquete de esta unidad y sus dependencias, sin las de desarrollo, sin modo editable.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package svca-pronostico

FROM python:3.13-slim

RUN useradd --system --uid 10001 --home-dir /app --shell /usr/sbin/nologin svca
WORKDIR /app
COPY --from=construccion /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER svca
EXPOSE 8000
# Render entrega el puerto en PORT. Un solo worker (ver arriba). Las cabeceras X-Forwarded-*
# del proveedor se aceptan para conocer la IP del cliente (límite de intentos, HU-53).
CMD ["sh", "-c", "exec uvicorn --factory svca_pronostico.api:crear_app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers --forwarded-allow-ips '*'"]
