# Estado del proyecto

Actualizar al cerrar cada tarea. Es lo primero que lee Claude Code en cada sesión.

## Sprint actual: 0. Preparar entorno, analizar datos y construir backlog

Entregable según la Tabla 5: perfil de calidad de los datos, backlog priorizado y repositorio configurado.

### Hecho
- [x] Repositorio clonado y conectado a GitHub.
- [x] Documento convertido en base de conocimiento (`docs/tesis/`, `docs/MAPA.md`, `docs/diagramas/`) con `tools/docx_a_conocimiento.py`.
- [x] Scripts SQL extraídos a `db/`. Probados en PostgreSQL 16 sobre base vacía: 24 tablas, el disparador bloquea cambios a `valor_crudo` y la restricción única rechaza mediciones duplicadas.
- [x] `CLAUDE.md`, `docs/TRAZABILIDAD.md` y `.gitignore`.

### Siguiente
- [ ] (Fable) ADR-0001: servicios con base de datos compartida (esquema `svca`) y por qué no una base por servicio.
- [ ] (Fable) ADR-0002: stack. El documento no fija framework web, ORM ni frontend.
- [ ] (Fable) Backlog: historias de usuario HU-xx a partir de RF-01..16, con criterios de aceptación y sprint. Crear los Issues en GitHub.
- [ ] (Fable) Contratos OpenAPI entre simulador, ingesta y reloj (lo que necesita el Sprint 1).
- [ ] (Opus) Estructura de carpetas de la Tabla 19, `infra/docker-compose.yml` con PostgreSQL 16 que ejecute `db/` al iniciar, CI con lint y tests.
- [ ] (Opus) Perfil de calidad de los datos IDEAM: completitud por estación y año, duplicados, KOICA mal georreferenciada.

## Decisiones abiertas
- Stack (ADR-0002).
- Proveedor de nube para el despliegue (Sprint 6).

## Desviaciones respecto al documento
- Ninguna por ahora.

## Pendientes del documento (no del código)
- El documento salta del Capítulo III al Capítulo V; no hay Capítulo IV.
