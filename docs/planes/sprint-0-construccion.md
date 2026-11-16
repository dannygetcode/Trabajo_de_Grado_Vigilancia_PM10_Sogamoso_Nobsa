# Plan: construcción del Sprint 0 (estructura, compose, base de datos, CI y esqueleto en la nube)

- Para: Opus. Decisiones de base: ADR-0001 (tres unidades de despliegue), ADR-0002 (stack), ADR-0003 (proveedores gratuitos).
- Resultado: un repositorio donde `docker compose up` levanta el sistema vacío pero completo, CI lo comprueba en cada integración y el mismo esqueleto responde en la nube. Ninguna regla de negocio todavía: eso empieza en el Sprint 1 con HU-01.
- Rama: `sprint-0/estructura`. Commits `S0-<n>: ...` con el número de la tarea (no hay historia de usuario). Un PR por bloque (A, B, C, D) para que la revisión sea corta.
- Si algo de este plan choca con un ADR, manda el ADR y se anota la duda en `docs/ESTADO.md`.

## Antes de empezar (lo comprueba Opus, lo instala el autor si falta)

`docker --version` y `docker compose version`, `uv --version`, `node --version` (LTS vigente), `git`. Si falta alguno, detenerse y decirlo: no se sustituye por otra herramienta.

## Bloque A. Estructura y herramientas

### Tarea 1. Árbol de carpetas y espacio de trabajo de uv

```
pyproject.toml            # raíz: workspace de uv, ruff, mypy, pytest, import-linter
uv.lock
servicios/
  comun/           pyproject.toml  svca_comun/
  ingesta/         pyproject.toml  svca_ingesta/{domain,application,infrastructure,api}/
  normativo/       pyproject.toml  svca_normativo/{...}
  pronostico/      pyproject.toml  svca_pronostico/{...}
  notificaciones/  pyproject.toml  svca_notificaciones/{...}
  planificador/    pyproject.toml  svca_planificador/
  nucleo/          pyproject.toml  svca_nucleo/           # solo composición
simulador/
  reloj/           pyproject.toml  svca_reloj/{domain,application,infrastructure,api}/
  estaciones/      pyproject.toml  svca_simulador/{...}
web/                       # tarea 6
infra/
  docker-compose.yml
  docker/{nucleo,pronostico,simulador,web}.Dockerfile
  render.yaml
  .env.example
tests/
  <servicio>/              # unitarias e integración por servicio
  arquitectura/            # límites, arranque individual, contratos
  humo/                    # contra un sistema levantado
tools/
.github/workflows/
```

- Cada `pyproject.toml` declara solo lo que ese paquete usa. `svca_pronostico` es el único con pandas y scikit-learn; `svca_notificaciones` el único con WeasyPrint y matplotlib.
- Python 3.13 fijado en `.python-version`.

**Terminado cuando:** `uv sync` termina sin errores en un clon limpio y `uv run python -c "import svca_nucleo, svca_pronostico, svca_simulador"` funciona.

### Tarea 2. Calidad: ruff, mypy, import-linter, pytest

- ruff: lint y formato; regla `TID251` con `banned-api` para `datetime.datetime.now`, `utcnow`, `today`, `datetime.date.today` y `time.time` (excepciones por archivo según `docs/planes/reloj-virtual.md`, sección 3.7; por ahora ninguna).
- mypy estricto sobre `*/domain` y `*/application`.
- import-linter, tres contratos: (1) los paquetes de servicio son independientes entre sí; (2) solo `svca_nucleo` puede importar varios servicios; (3) en cada servicio las capas apuntan hacia `domain` (`api → application → domain`, `infrastructure → application, domain`) y `domain` no importa nada fuera de la biblioteca estándar.
- pytest con marcadores `unitaria`, `integracion` (necesita PostgreSQL) y `humo`; `pytest-cov` configurado, sin umbral todavía (los umbrales de RNF-19 se activan por módulo en los Sprints 2 y 3).
- Reescribir `README.md`: qué es, arquitectura en un párrafo con enlace a los ADR, cómo levantarlo (`docker compose`), estructura real de carpetas, enlace a `docs/`. Quitar PostGIS, `backend/`, `frontend/` y el periodo 2022 a 2024 (corrección 28 de `docs/correcciones_documento.md`).

**Terminado cuando:** `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run lint-imports` y `uv run pytest -m unitaria` pasan; y una prueba en `tests/arquitectura/` demuestra que la regla de ruff detecta un `datetime.now()` en un archivo de ejemplo.

## Bloque B. Base de datos

### Tarea 3. `tools/db_aplicar.py`

- Uso: `python tools/db_aplicar.py --url <cadena> [--hasta 10]`. Aplica en orden numérico los `db/NN_*.sql` que falten, cada uno en su transacción.
- Lleva la cuenta en `svca_meta.script_aplicado (nombre, sha256, aplicado_en)`. El esquema `svca_meta` lo crea la herramienta; `svca` no se toca (deben seguir siendo 24 tablas).
- Si un script ya aplicado cambió de contenido (SHA-256 distinto), falla con un mensaje claro y no aplica nada: los scripts aplicados no se editan, se agrega uno nuevo.
- Espera a que la base acepte conexiones (reintentos hasta 60 s) para poder usarse como contenedor de arranque.
- `aplicado_en` usa la hora de la base (`now()`): es metadato de operación, no hora de dominio. Dejarlo comentado.
- No modifica `db/01` a `db/10`.

**Terminado cuando** (pruebas de integración en `tests/arquitectura/test_db.py`): sobre una base vacía quedan 24 tablas en `svca`; una segunda ejecución no hace nada; cambiar `valor_crudo` de una medición falla por el disparador; una medición duplicada se rechaza; alterar un script ya aplicado hace fallar la herramienta.

## Bloque C. Esqueleto de servicios, contenedores y compose

### Tarea 4. `svca_comun` mínimo y una aplicación por servicio

- `svca_comun.configuracion`: lectura de variables `SVCA_*` con pydantic-settings; falla al arrancar si falta una obligatoria.
- `svca_comun.errores`: el formato `{codigo, mensaje, errores[]}` de `docs/api/README.md` y sus manejadores para FastAPI.
- `svca_comun.salud`: fábrica de la ruta `GET /v1/salud` (`{servicio, version, estado}`), anónima.
- Cada servicio (`svca_reloj`, `svca_ingesta`, `svca_normativo`, `svca_notificaciones`, `svca_pronostico`, `svca_simulador`) expone `crear_app() -> FastAPI` en `api/` con su `/v1/salud` y nada más. `svca_planificador` expone una corrutina `ejecutar()` que por ahora solo espera.
- `svca_nucleo.app`: monta reloj, ingesta, normativo y notificaciones en `/reloj`, `/ingesta`, `/normativo`, `/notificaciones`; `GET /salud` agrega el estado de las cuatro; arranca y detiene la tarea del planificador en el ciclo de vida; aplica CORS con `SVCA_ORIGENES`. Ni una línea de negocio.
- `/salud` del núcleo, de pronóstico y del simulador comprueba la conexión a la base con `SELECT 1` solo si recibe `?profundo=1` (la versión simple no debe despertar la base gratuita).

**Terminado cuando:** una prueba arranca cada aplicación por separado y obtiene 200 en `/v1/salud`; otra arranca el núcleo y obtiene 200 en `/reloj/v1/salud`, `/ingesta/v1/salud`, `/normativo/v1/salud`, `/notificaciones/v1/salud` y `/salud`; una petición con `Origin` no permitido no recibe `Access-Control-Allow-Origin`.

### Tarea 5. Imágenes

- `infra/docker/{nucleo,pronostico,simulador}.Dockerfile`, contexto en la raíz, base `python:3.13-slim`, instalación con `uv sync --frozen --no-dev --package <paquete>`, usuario sin privilegios, `CMD` con `uvicorn ... --workers 1 --port ${PORT:-8000}` (Render entrega el puerto en `PORT`).
- En `nucleo.Dockerfile`, un comentario junto a `--workers 1`: el estado del reloj vive en memoria; dos workers serían dos relojes.
- La imagen del núcleo incluye las bibliotecas del sistema que WeasyPrint necesita (pango), para no descubrirlo en el Sprint 5.
- `.dockerignore`: `data/`, `docs/`, `.git`, `node_modules`, `.venv`, `infra/secretos/`.

**Terminado cuando:** las tres imágenes construyen, cada contenedor responde su salud, corre como usuario no root y la imagen `nucleo` no contiene pandas ni scikit-learn (`pip list` dentro del contenedor).

### Tarea 6. Web mínima

- `web/`: Vite + React + TypeScript. Una sola página que consulta la salud del núcleo, de pronóstico y del simulador (URL en `VITE_URL_NUCLEO`, `VITE_URL_PRONOSTICO`, `VITE_URL_SIMULADOR`) y muestra para cada uno "en línea", "despertando..." (mientras espera, hasta 90 s) o "sin respuesta". Ese componente de espera se reutiliza después en toda la web.
- `infra/docker/web.Dockerfile`: construye y sirve `dist/` con un servidor de archivos estáticos.
- Scripts `lint`, `typecheck`, `test` (Vitest, una prueba del componente de estado) y `build`.

**Terminado cuando:** `npm ci && npm run lint && npm run typecheck && npm test && npm run build` pasan y la página muestra los tres servicios en línea contra el compose.

### Tarea 7. `infra/docker-compose.yml` (RNF-20)

| Servicio | Imagen | Puerto local | Notas |
|---|---|---|---|
| `bd` | `postgres:16` | 5432 | Volumen con nombre; `healthcheck` con `pg_isready` |
| `migrador` | la del núcleo, o `python:3.13-slim` con `tools/` y `db/` montados | — | Ejecuta `db_aplicar.py` y termina; los demás dependen de `service_completed_successfully` |
| `nucleo` | `nucleo.Dockerfile` | 8000 | |
| `pronostico` | `pronostico.Dockerfile` | 8001 | |
| `simulador` | `simulador.Dockerfile` | 8002 | Monta `${SIM_HISTORICO_DIR:-./vacio}` en solo lectura |
| `web` | `web.Dockerfile` | 8080 | |
| `correo` | `axllent/mailpit` | 8025 (web), 1025 (SMTP) | Servidor de pruebas de 3.6.7 |

- Todo configurable desde `infra/.env`; `infra/.env.example` versionado con valores que funcionan tal cual en local (contraseñas de desarrollo marcadas como tales). El compose debe levantar **sin** crear `.env`, con valores por defecto, para cumplir "equipo limpio".
- Una sola orden documentada en el README: `docker compose -f infra/docker-compose.yml up --build`.
- En este sprint todos los servicios usan la misma cadena de conexión; los roles por servicio llegan con HU-06, que ya tiene previstas las variables `SVCA_<SERVICIO>_DB_URL`.

**Terminado cuando:** en un clon limpio, sin `.env`, la orden levanta todo; `tests/humo/` (que solo usa HTTP) obtiene 200 en las saludes, incluida `?profundo=1`; `docker compose stop pronostico` deja al núcleo respondiendo; y `docker compose down -v && up` vuelve a dejar 24 tablas.

## Bloque D. CI y nube

### Tarea 8. `.github/workflows/ci.yml`

En cada PR y en `main`:

1. `calidad`: ruff (lint y formato), mypy, import-linter, validación de `docs/api/*.yaml` con `openapi-spec-validator`.
2. `pruebas`: pytest unitarias e integración con un servicio `postgres:16`; informe de cobertura como artefacto.
3. `web`: lint, tipos, pruebas y construcción.
4. `compose`: construye las imágenes, levanta `infra/docker-compose.yml`, ejecuta `tests/humo/` y lo apaga. Es la verificación continua de RNF-20.
5. Solo en `main`, tras los anteriores, `migrar`: ejecuta `db_aplicar.py` contra la base de la nube (`secrets.SVCA_NUBE_DB_URL`). Si el secreto no existe, el paso se omite sin fallar.

- Caché de uv y de npm. Sin ejecutores grandes ni servicios de terceros.
- Un segundo flujo, `humo-nube.yml`, manual y diario: llama a las saludes públicas con hasta tres minutos de espera por arranque en frío.

**Terminado cuando:** el PR del bloque D tiene los cuatro trabajos en verde, y un commit de prueba con `datetime.now()` en un `domain/` lo pone en rojo (se adjunta el enlace a esa ejecución en el PR y luego se revierte).

### Tarea 9. Esqueleto en la nube (el autor crea las cuentas; Opus deja todo listo)

Opus no crea cuentas ni escribe secretos. Prepara:

- `infra/render.yaml` con los tres servicios web gratuitos (entorno Docker, cada uno con su `Dockerfile`, ruta de salud, despliegue automático tras CI en verde) y el sitio estático de `web/`. Variables declaradas con `sync: false` para que los valores se pongan en el panel. Si Render exige que el archivo esté en la raíz del repositorio, se deja en la raíz y se anota en `docs/ESTADO.md`.
- `docs/manuales/despliegue.md`: pasos para el autor, en orden: (1) crear el proyecto en Neon, PostgreSQL 16, región del este de EE. UU., y copiar la cadena **con agrupador** y `sslmode=verify-full`; (2) crear la cuenta de Render, conectar el repositorio y aplicar `render.yaml` en la misma región; (3) poner las variables en Render y `SVCA_NUBE_DB_URL` en los secretos de GitHub; (4) crear la cuenta de Brevo y verificar el remitente (puede esperar al Sprint 5); (5) comprobar que **ningún paso pidió tarjeta** y que los límites coinciden con la tabla de ADR-0003; si algo difiere, anotarlo en `docs/ESTADO.md` antes de seguir.

**Terminado cuando:** las URL públicas responden la salud (incluida `?profundo=1` contra Neon), la página estática muestra los tres servicios en línea, `humo-nube.yml` pasa, y las URL quedan escritas en `docs/ESTADO.md`. Si el autor aún no ha creado las cuentas, la tarea queda "lista para desplegar" y así se anota.

### Tarea 10. Cierre

- `docs/ESTADO.md`: mover lo hecho, anotar desviaciones nuevas y las URL.
- Verificar la definición de terminado del Sprint 0 (Tabla 5): repositorio configurado ✔ con este plan; backlog priorizado ✔ (`docs/backlog.md`); **perfil de calidad de los datos**: es una tarea aparte ya descrita en `docs/ESTADO.md` y no forma parte de este plan, pero el Sprint 0 no cierra sin ella.

## Lo que este plan no hace

- No implementa el reloj, la autenticación ni la ingesta (Sprint 1, `docs/planes/reloj-virtual.md` y `autenticacion.md`).
- No crea `db/11` (HU-06) ni `db/12` (Sprint 5).
- No configura la copia de seguridad (HU-54). Si sobra tiempo es lo primero que conviene adelantar, porque RNF-16 es fácil de demostrar con historial y difícil de improvisar.
- No crea los Issues de GitHub: requiere `gh` instalado y autenticado por el autor.

## Revisión (Fable)

Al terminar los bloques C y D: revisar `svca_nucleo` (que no haya lógica), los contratos de import-linter (que de verdad fallen cuando deben) y `render.yaml` frente a ADR-0003.
