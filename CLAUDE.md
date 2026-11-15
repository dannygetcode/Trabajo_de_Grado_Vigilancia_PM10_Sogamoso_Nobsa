# CLAUDE.md

Software web de vigilancia de la calidad del aire y pronóstico de PM10 en el corredor Sogamoso-Nobsa (Boyacá).
Trabajo de grado de Ingeniería de Software, UMB. Un solo autor. Scrum con sprints de dos semanas, CRISP-DM para el modelo.

## Cómo cargar contexto (ahorro de tokens)

1. Lee `docs/ESTADO.md`: en qué sprint vamos, qué está hecho y qué sigue.
2. Lee `docs/MAPA.md`: índice de todo el documento con el peso en tokens de cada sección.
3. Abre solo las secciones de `docs/tesis/` que la tarea necesita. Para requisitos: `03-6-1`. Para arquitectura: `03-6-6` y `03-6-7`. Para datos: `03-6-8` y `db/`.
4. Para saber qué RF va en qué servicio, carpeta, tabla y sprint: `docs/TRAZABILIDAD.md`.

No abras el `.docx` de `docs/archivos/`. No leas las imágenes de `docs/diagramas/` salvo que la tarea dependa de un diagrama concreto: cada una cuesta tanto como una sección de texto y el texto de la sección casi siempre basta.

## Fuente de verdad

- El documento (`docs/archivos/*.docx`) manda sobre el diseño. `docs/tesis/` es una copia generada: no se edita a mano.
- Si el documento cambia: `python tools/docx_a_conocimiento.py docs/archivos/Trabajo_de_Grado_Vigilancia_PM10_Sogamoso_Nobsa.docx`.
- Si el código necesita apartarse del documento, no lo hagas en silencio: anótalo en `docs/ESTADO.md` (sección Desviaciones) o escribe un ADR en `docs/adr/`.

## Arquitectura (resumen de 3.6.6 y 3.6.7)

- Servicios con responsabilidad acotada y API documentada con OpenAPI (RNF-09): ingesta y validación, normativo, pronóstico, notificaciones e informes.
- Simulador de estaciones como adaptador de entrada (RNF-04): reproduce datos históricos con reloj virtual e inyecta fallas.
- Planificador común y servicio de reloj: todos los servicios toman la hora del reloj, nunca de `now()` del sistema.
- PostgreSQL, esquema `svca`, 24 tablas (`db/01` a `db/10`). Contenedores y un único archivo de orquestación (RNF-08, RNF-20).
- Dentro de cada servicio: capas `domain/` (sin dependencias externas), `application/` (casos de uso), `infrastructure/` (BD, HTTP, modelo), `api/`. Las dependencias apuntan hacia `domain`.

## Estructura (Tabla 19)

`db/` `docs/` `simulador/` `servicios/{ingesta,normativo,pronostico,notificaciones}/` `web/` `infra/` `tests/` `tools/`

## Reglas que no se negocian

- `medicion.valor_crudo` es inmutable (RF-04). Lo protege un disparador; el código tampoco lo intenta.
- El pronóstico solo usa datos anteriores al momento de emisión (RNF-02). Toda feature nueva lleva un test de fuga temporal.
- Reglas de validación y evaluación normativa con la cobertura que pide RNF-19.
- Ninguna hora se toma del sistema: se inyecta el reloj.
- Commits en español que referencian la historia de usuario: `HU-07: ingesta acepta lotes horarios`. Una rama por historia y PR a `main` (3.6.10).
- No subir datos crudos, modelos `.joblib` ni `.env`.

## Reparto de modelos

- Fable (`/model claude-fable-5-2`): planear y revisar lo difícil. Contratos entre servicios, reloj virtual, reglas normativas (Res. 2254, arts. 10 a 12), pipeline de pronóstico e intervalos, fuga temporal, revisión de seguridad, bugs que no salen.
- Opus (`/model claude-opus-5-5`): implementar planes ya escritos, CRUD, tests, migraciones, frontend, documentación y manuales.
- Patrón: Fable escribe el plan en `docs/planes/<tema>.md`, Opus lo implementa y Fable revisa el diff.

## Al terminar una tarea

Actualiza `docs/ESTADO.md` (hecho, siguiente, desviaciones). Es la memoria entre sesiones: si no queda ahí, la próxima sesión lo vuelve a descubrir leyendo código.
