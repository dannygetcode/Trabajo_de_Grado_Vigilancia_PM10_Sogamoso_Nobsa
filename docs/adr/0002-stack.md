# ADR-0002: Stack tecnológico

- Estado: Aceptado (reemplaza la versión anterior, "Stack tecnológico", ajustada a la restricción de costo cero y a ADR-0001 y ADR-0003)
- Fecha: 2026-11-15
- Sprint: 0
- Relacionado: 3.6.6, 3.6.7, 3.6.10; RNF-02, RNF-05, RNF-06, RNF-08, RNF-09, RNF-12, RNF-17, RNF-19, RNF-20; ADR-0001, ADR-0003

## Contexto

El documento fija PostgreSQL, contenedores, un único archivo de orquestación, APIs documentadas con OpenAPI y el reparto en servicios, pero no fija lenguaje, framework, acceso a datos ni frontend. Cuatro restricciones orientan la elección:

- **Un solo autor**: un único lenguaje en el backend y el menor número posible de piezas que operar.
- **El modelo de pronóstico** se entrena con CRISP-DM y se guarda en `.joblib`, lo que ya implica Python y scikit-learn.
- **Ninguna hora se toma del sistema**: todo lo que programe tareas debe obedecer al servicio de reloj, también cuando reproduce un año en 30 minutos (RNF-11).
- **Todo gratuito y permanente**: solo software libre, y nada que exija en ejecución más de lo que dan los planes de ADR-0003 (512 MB por contenedor, sin disco, sin puertos SMTP de salida, 1 GB de base de datos).

## Decisión

| Capa | Elección | Requisito que la justifica |
|---|---|---|
| Lenguaje backend | Python 3.13 | Un lenguaje para servicios, simulador, modelo y `tools/`. |
| Framework de API | FastAPI + Pydantic v2 + Uvicorn (un worker) | RNF-09 pide "documentación generada": FastAPI produce el OpenAPI desde el código. Pydantic valida el contrato del lote (RF-01). Permite montar varias aplicaciones en un proceso, que es lo que necesita el núcleo (ADR-0001). |
| Acceso a datos | SQLAlchemy 2 Core + psycopg 3 con `psycopg_pool`; **sin ORM** | El esquema lo define `db/` (ADR-0001) y `domain/` debe quedar sin dependencias externas; un ORM empuja a mapear entidades a tablas. Core da SQL componible y parámetros seguros. Las sentencias preparadas del lado del servidor se desactivan (`prepare_threshold=None`) porque la base gratuita se usa a través de un agrupador de conexiones en modo transacción (ADR-0003). |
| Migraciones | Scripts SQL numerados en `db/` aplicados por `tools/db_aplicar.py`; sin Alembic | Los scripts 01 a 10 son parte del documento (3.6.9). La herramienta lleva la cuenta de lo aplicado en un esquema aparte (`svca_meta`), de modo que `svca` conserva sus 24 tablas. |
| Comunicación entre servicios | HTTP con httpx; transporte ASGI en proceso dentro del núcleo, HTTPS hacia fuera; sin intermediario de mensajes | Las tres llamadas de la Figura 42 no justifican un broker, y ninguno gratuito es permanente. RNF-01 da cinco minutos de margen. |
| Planificador | Propio: un bucle que consulta el reloj y dispara por HTTP | APScheduler, Celery beat y cron leen la hora del sistema y no pueden seguir un reloj virtual acelerado o en pausa. Son unas cien líneas (`docs/planes/reloj-virtual.md`, sección 5). |
| Código compartido | `servicios/comun/` (cliente del reloj, verificación de tokens, errores, configuración) | Evita cuatro copias del cliente del reloj. No contiene reglas de negocio. |
| Autenticación | JWT RS256 (PyJWT + cryptography); contraseñas con Argon2id (argon2-cffi) | RNF-05, RNF-17. Detalle abajo. |
| **Aprendizaje automático** | **scikit-learn** (candidato principal `HistGradientBoostingRegressor`), pandas y numpy; artefactos con joblib | Corre en CPU y en 512 MB, sin GPU ni servicios externos. Admite pérdida por cuantiles y calibración conforme para el intervalo de RF-08. El algoritmo definitivo y el método del intervalo se eligen con evidencia en el Sprint 4 (`docs/planes/pronostico.md`), siempre dentro de scikit-learn. La versión se fija en el archivo de bloqueo: un `.joblib` solo es confiable con la versión que lo creó. |
| Correo | Un puerto `EnviadorCorreo` con dos adaptadores: SMTP (`smtplib`, para el servidor de pruebas Mailpit) y API HTTPS del proveedor (httpx) | 3.6.7 pide un servidor de pruebas que capture los correos. En la nube gratuita los puertos SMTP de salida están bloqueados, así que allí se usa la API (ADR-0003). |
| Informe PDF | Jinja2 + WeasyPrint, gráficas con matplotlib (importación diferida) | RF-11. HTML y CSS se mantienen mejor que dibujar el PDF a mano. Se importan solo al generar para no ocupar memoria del núcleo. |
| Exportación | Módulo `csv` de la biblioteca estándar, respuesta en flujo | RNF-12: CSV en UTF-8 sin cargar el periodo completo en memoria. |
| Frontend | React + TypeScript + Vite; tipos del cliente generados desde el OpenAPI (`openapi-typescript`); Leaflet con teselas de OpenStreetMap; Recharts para las series | 3.6.6: la web consume las APIs, así que es una aplicación de página única que se publica como archivos estáticos gratuitos. Generar los tipos desde el contrato convierte un cambio de API en error de compilación. |
| Origen cruzado | CORS con lista cerrada de orígenes (`SVCA_ORIGENES`); tokens en la cabecera `Authorization`, no en cookies | La web estática y las APIs quedan en dominios distintos del proveedor. Sin cookies no hay CSRF. Sustituye al proxy inverso de la versión anterior de este ADR: una pieza menos que desplegar. |
| Pruebas backend | pytest + pytest-cov + anyio; Hypothesis para las propiedades del reloj; integración contra PostgreSQL 16 real en contenedor | RNF-19. El disparador, los roles y las restricciones solo se prueban con PostgreSQL de verdad, no con SQLite. La prueba de fuga temporal de RNF-02 es una prueba de pytest por cada variable de entrada. |
| Pruebas frontend | Vitest + Testing Library; Playwright para los flujos críticos (revisión, declaratoria, vista pública) en el Sprint 6 | RNF-13, RNF-14 y el guion de la prueba SUS (RNF-07). |
| Contratos | `openapi-spec-validator` sobre `docs/api/` y una prueba que compara el OpenAPI generado con el de diseño | RNF-09. |
| Calidad | ruff (lint y formato, con la regla que prohíbe leer la hora del sistema), mypy en `domain/` y `application/`, `import-linter` para los límites entre servicios | Reglas de `CLAUDE.md` y ADR-0001, verificadas por máquina. |
| Dependencias | uv, un `pyproject.toml` por paquete y un archivo de bloqueo en la raíz | Instalación reproducible en CI y en las imágenes. |
| Contenedores | `python:3.13-slim`, una imagen por unidad de despliegue (`nucleo`, `pronostico`, `simulador`); `infra/docker-compose.yml` | RNF-08 y RNF-20. |

### Autenticación y dónde vive

La Figura 42 no dibuja ninguna interfaz para CU-13, CU-14 ni CU-15. Se decide:

- **El servicio de ingesta emite los tokens** (`POST /v1/sesiones`) y, desde el Sprint 2, administra usuarios y la red de monitoreo. Es el único que usa la llave privada. No se crea un servicio de seguridad aparte: la Tabla 19 y la Figura 42 tienen cuatro servicios de negocio.
- **Los demás verifican la firma con la llave pública**, sin llamar a nadie. Se elige firma asimétrica (RS256) y no un secreto compartido (HS256) porque el simulador y el pronóstico corren en otros contenedores: con HS256, quien verifica también puede firmar, y un simulador comprometido podría fabricarse un token de administrador. En la nube, la llave privada solo se configura en el contenedor `nucleo`.
- **Las cuentas de servicio son filas de `usuario` con rol `SERVICIO`** (ya está en `db/10`). El simulador y el planificador inician sesión igual que una persona y renuevan el token antes de que venza.
- **El simulador expone su propia API de control** para CU-14, porque en la Figura 30 es el simulador quien cambia el estado del escenario y de las fallas.
- **Límite de intentos por IP** en `POST /v1/sesiones`, dentro de la aplicación (contador en memoria; el núcleo es un solo proceso). Mitiga que el bloqueo al quinto intento de RNF-17 se use para bloquear cuentas ajenas. Antes se había previsto en el proxy, que ya no existe.

### El reloj y la hora de seguridad

La regla "ninguna hora se toma del sistema" aplica a la **hora de dominio**: mediciones, validación, promedios, evaluación, pronóstico, auditoría, `recibida_en`. Tiene una excepción deliberada: **el vencimiento de los tokens y el bloqueo de cuentas usan la hora real**. Con el reloj virtual, un token de 60 minutos vencería en dos décimas de segundo durante una reproducción acelerada, y al reproducir 2022 todos nacerían vencidos. Las duraciones (RNF-01, RNF-11) se miden con el reloj monótono del proceso.

Las columnas con `DEFAULT now()` (`medicion.recibida_en`, `revision.fecha`, `registro_auditoria.fecha`) se llenan siempre desde el código con la hora del reloj.

## Alternativas descartadas

- **Django + Django REST Framework.** Trae ORM, administración y autenticación hechos, pero su ORM quiere ser dueño del esquema y sus migraciones chocan con `db/`. El OpenAPI depende de un paquete adicional.
- **SQLAlchemy ORM o SQLModel.** Menos SQL a mano, a cambio de entidades de dominio atadas a la base. Pesa más la regla de capas.
- **Web renderizada en servidor (Jinja2 + HTMX).** Menos JavaScript, pero necesita un backend propio siempre encendido; una página estática se sirve gratis y no se duerme, que es lo que conviene a la vista pública (RF-13).
- **Proxy inverso (Caddy o Nginx) delante de todo.** Daba un solo origen, pero es un contenedor más que no cabe gratis y el proveedor ya termina HTTPS.
- **Celery, RabbitMQ o Redis.** Más piezas, ninguna gratuita de forma permanente y ninguna entiende el reloj virtual.
- **XGBoost, LightGBM, Prophet o redes neuronales (PyTorch, TensorFlow).** Añaden dependencias pesadas para un problema tabular de cinco estaciones; las de aprendizaje profundo no caben en 512 MB. Si en el Sprint 4 la evidencia mostrara una ventaja clara de LightGBM, se revisa este ADR; el contrato del servicio no cambia.
- **Node o Java en el backend.** Obligarían a un segundo lenguaje para el modelo.

## Consecuencias

- El contrato de `docs/api/*.yaml` es el diseño; el OpenAPI que genera FastAPI es la implementación. Una prueba por servicio los compara.
- Con SQLAlchemy Core se escriben a mano las consultas y los mapeos fila → entidad. Es más código que con ORM, pero queda todo en `infrastructure/`.
- CORS obliga a mantener la lista de orígenes por entorno; una prueba comprueba que un origen ajeno no recibe las cabeceras.
- El planificador propio debe probarse con un reloj falso: un disparo por hora, sin repetir ni saltar tras una pausa.
- Cargar un `.joblib` ejecuta código: el servicio de pronóstico solo carga artefactos cuyo SHA-256 coincide con el registrado (ADR-0003).
- React añade una cadena de construcción con Node. Conviene pasar a la LTS vigente antes del Sprint 2, cuando empieza `web/`.
- Las llaves RS256 se generan al instalar y no se suben al repositorio (misma regla que `.env`).
