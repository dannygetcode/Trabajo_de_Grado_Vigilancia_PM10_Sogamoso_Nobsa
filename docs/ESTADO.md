# Estado del proyecto

Actualizar al cerrar cada tarea. Es lo primero que lee Claude Code en cada sesión.

## Sprint actual: 0. Preparar entorno, analizar datos y construir backlog

Entregable según la Tabla 5: perfil de calidad de los datos, backlog priorizado y repositorio configurado.

### Hecho
- [x] Repositorio clonado y conectado a GitHub.
- [x] Documento convertido en base de conocimiento (`docs/tesis/`, `docs/MAPA.md`, `docs/diagramas/`) con `tools/docx_a_conocimiento.py`.
- [x] Scripts SQL extraídos a `db/`. Probados en PostgreSQL 16 sobre base vacía: 24 tablas, el disparador bloquea cambios a `valor_crudo` y la restricción única rechaza mediciones duplicadas.
- [x] `CLAUDE.md`, `docs/TRAZABILIDAD.md` y `.gitignore`.
- [x] Datos: `data/raw/ideam_corredor.csv` (no se sube a git) filtrado del export nacional con `tools/filtrar_ideam.py`. 1.803.476 filas, 382 MB, 2020-2024. Estaciones y filas: EL RECREO 31826 (417.572), NAZARETH-JAC 31827 (406.314), BOMBEROS 30815 (293.221), SENA 30810 (247.577), MOVIL KOICA 31828 (221.751, se excluye: mal georreferenciada), UPTC 31719 (217.041). PM10 tiene 183.625 filas.
- [x] ADR-0001 (`docs/adr/0001-arquitectura-de-servicios.md`, reemplaza a `0001-base-de-datos-compartida.md`): siete servicios lógicos en tres contenedores (`nucleo` = reloj, planificador, ingesta, normativo, notificaciones; `pronostico`; `simulador`), misma topología en compose, CI y nube; una base compartida, un escritor por tabla, roles de PostgreSQL por servicio.
- [x] ADR-0002 (`docs/adr/0002-stack.md`, reemplaza a `0002-stack-tecnologico.md`): Python 3.13, FastAPI, SQLAlchemy Core + psycopg 3, planificador propio, JWT RS256, scikit-learn, React + TypeScript + Vite, CORS en lugar de proxy, pytest, ruff, mypy, import-linter, uv.
- [x] ADR-0003 (`docs/adr/0003-despliegue-gratuito.md`): Render (tres contenedores gratuitos y sitio estático), Neon (PostgreSQL 16, 1 GB), Brevo por API (300 correos al día), GitHub Actions (CI, copia diaria cifrada, restauración semanal), GitHub Releases (modelos). Límites consultados el 2026-11-15.
- [x] Backlog (`docs/backlog.md`): 60 historias, HU-01 a HU-60, 206 puntos, con criterios de aceptación, RF y RNF, sprint, puntos y modelo; tabla RNF → historias y orden de recorte.
- [x] `docs/correcciones_documento.md`: 28 correcciones del Word con sección, cambio, motivo y prioridad.
- [x] Plan `docs/planes/sprint-0-construccion.md`: diez tareas para estructura, `db_aplicar.py`, esqueleto de servicios, imágenes, compose, CI y esqueleto en la nube, cada una con criterio de terminado.
- [x] Contratos OpenAPI 3.1 del Sprint 1 (`docs/api/reloj.yaml`, `ingesta.yaml`, `simulador.yaml` y `README.md`). Ajustados a ADR-0001 (dónde se publica cada servicio, sin proxy, CORS, arranque en frío) y validados de nuevo con `openapi-spec-validator`.
- [x] Plan `docs/planes/reloj-virtual.md`: máquina de estados del reloj, barrera, bucle de reproducción, recuperación ante caídas y planificador (HU-01 a HU-03, HU-12 a HU-14, HU-16).
- [x] Plan `docs/planes/autenticacion.md`: llaves, token, inicio de sesión con bloqueo, cuentas de servicio, formato de errores (HU-04, HU-05).
- [x] `.gitignore` excluye `infra/secretos/` y `*.pem`.

### Siguiente
- [ ] (Autor) Revisar los tres ADR y las interpretaciones del final de `docs/backlog.md`; validar las prioridades con la asesora. En especial ADR-0001: se aparta de la Figura 43 (correcciones 1 a 5 de `docs/correcciones_documento.md`).
- [ ] (Autor) Crear las cuentas de Neon, Render y Brevo siguiendo `docs/manuales/despliegue.md` (lo escribe la tarea 9 del plan del Sprint 0). Comprobar que ninguna pide tarjeta y que los límites coinciden con ADR-0003.
- [ ] (Autor) Aplicar al Word las correcciones de prioridad A y regenerar `docs/tesis/`.
- [ ] Crear los Issues en GitHub a partir de `docs/backlog.md`. No se hizo: `gh` no está instalado en este equipo. Con `gh` instalado y autenticado se generan desde el backlog (un Issue por historia, etiqueta por sprint).
- [ ] (Opus) Ejecutar `docs/planes/sprint-0-construccion.md`, tareas 1 a 10 en orden.
- [ ] (Opus) Perfil de calidad de los datos: completitud de PM10 por estación y año, duplicados, horas faltantes. Leer el CSV con un script; nunca abrirlo ni pegarlo en el chat. Además debe responder dos preguntas de `docs/api/README.md` (cuántos decimales traen los valores y en qué zona horaria vienen las fechas) y producir el archivo histórico normalizado que lee el simulador (`docs/planes/reloj-virtual.md`, sección 4.1).
- [ ] (Opus) Sprint 1: HU-01 a HU-15 y HU-60 según `docs/backlog.md`, `docs/api/` y los dos planes. Orden: sección 8 de `reloj-virtual.md` y sección 9 de `autenticacion.md`; la protección de rutas va antes que cualquier ruta de negocio.
- [ ] (Fable) Revisar el esqueleto del Sprint 0 (`svca_nucleo`, contratos de import-linter, `render.yaml`) y el diff de HU-03, HU-04, HU-13 y HU-60 cuando Opus las termine.
- [ ] (Fable) Antes del Sprint 2: `docs/planes/validacion.md` (umbrales de las reglas, HU-18) y los contratos de revisión, configuración y disparos del planificador.

## Decisiones abiertas
- Algoritmo del modelo y método del intervalo de predicción (Sprint 4, `docs/planes/pronostico.md`).
- Umbrales de las reglas de cambio brusco y comparación entre estaciones (Sprint 2, `docs/planes/validacion.md`).

## Decisiones tomadas que no están en el documento
- **Dónde viven CU-13, CU-14 y CU-15.** La Figura 42 no les dibuja interfaz. El inicio de sesión y la administración de usuarios y de la red van en el servicio de ingesta; el control de escenarios, en una API propia del simulador (ADR-0002).
- **Barrera horaria del reloj.** En modo virtual el reloj no avanza a la hora siguiente hasta que los participantes confirman la actual. Hace reproducible la reproducción acelerada (`docs/api/reloj.yaml`).
- **Procesos idempotentes por hora.** Todo proceso que dispare el planificador recibe `{"hora": t}` y puede repetirse sin cambiar el resultado. Es requisito para los contratos de los Sprints 2 a 4.
- **Riesgos de seguridad aceptados.** No hay revocación de tokens (duran 60 minutos) y el bloqueo al quinto intento permite bloquear cuentas ajenas; se mitiga con un límite de intentos por IP dentro de la ingesta (ya no hay proxy). La base de la nube es accesible desde internet, con TLS y un rol por servicio (ADR-0003).
- **Servicio no es contenedor.** Los límites entre servicios los hacen cumplir import-linter, los roles de la base y una prueba que arranca cada servicio solo; el agrupamiento en contenedores se decide solo en `servicios/nucleo/` (ADR-0001).
- **El despliegue empieza en el Sprint 0** y cada historia termina desplegada. Los RNF de desempeño (01, 10, 11) se verifican en el compose; en la nube se miden como dato informativo (ADR-0003).
- **La nube es un entorno de demostración.** Los contenedores gratuitos se duermen sin tráfico; el simulador mantiene todo despierto mientras hay un escenario en ejecución. En modo real continuo no se garantizan los procesos horarios.
- **Hora de seguridad.** El vencimiento de tokens y las duraciones usan la hora real; todo lo demás, el reloj. Es la única excepción a "ninguna hora se toma del sistema" (ADR-0002).
- **La ingesta rechaza mediciones futuras** respecto al reloj (RNF-02) y valores con más de tres decimales, para no redondear el dato crudo.
- **RF-12 (exportación)** va en el servicio de ingesta. **RF-14** empieza en el Sprint 1 (tokens) y sigue en el 2 (usuarios y web). **RF-15** se reparte: red en ingesta (Sprint 3), parámetros en normativo (Sprint 3), contactos en notificaciones (Sprint 5).

## Desviaciones respecto al documento
- `db/11_roles_servicios.sql` (previsto, HU-06): script nuevo fuera de los 01 a 10 de la sección 3.6.9. Crea los roles de PostgreSQL por servicio, el rol de aplicación `SIMULADOR` y agrega `consultar_red` al rol `COORDINADOR`.
- `servicios/comun/`, `servicios/planificador/` y `servicios/nucleo/` (previstos): no aparecen en la Tabla 19. El reloj va en `simulador/reloj/` y se ejecuta dentro del contenedor `nucleo`; el simulador va en `simulador/estaciones/`, en su propio contenedor.
- **Tres contenedores en lugar de uno por servicio** (Figura 43, 3.6.7). Motivo: costo cero permanente (ADR-0001, ADR-0003).
- **Sin proxy de entrada**: la web es un sitio estático y las APIs usan CORS (ADR-0002).
- **Correo en la nube por API HTTPS y con redirección a un buzón de prueba**, no por SMTP a un servidor de captura; Mailpit se mantiene en local y CI (ADR-0003).
- `db/12` (previsto, Sprint 5): tabla `informe_archivo` para guardar el PDF en la base; el modelo pasa de 24 a 25 tablas. `svca_meta.script_aplicado` (esquema aparte) lleva la cuenta de los scripts aplicados.
- Modelos `.joblib` como adjuntos de GitHub Releases, verificados por SHA-256; siguen fuera del árbol de git.
- La Figura 42 muestra al simulador sin interfaz propia y sin conexión a PostgreSQL; aquí expone la API de CU-14 y escribe `escenario_simulacion` y `falla_inyectada`, como indica la Figura 30.

## Pendientes del documento (no del código)
- Las correcciones del Word se hacen al final del Sprint 0. Lista completa y priorizada en `docs/correcciones_documento.md`; los puntos de abajo ya están incluidos allí.
- El documento salta del Capítulo III al Capítulo V; no hay Capítulo IV.
- La Figura 42 no tiene interfaces para la configuración (CU-13), la simulación (CU-14) ni el inicio de sesión (CU-15).
- La Figura 32 distingue reglas críticas y de advertencia, pero el texto no dice cuál regla es de cada tipo.
- La Figura 10 deja sin definir el estado de un pronóstico con 18 a 23 horas observadas.
- CU-04 permite al coordinador consultar el estado de la red, pero los datos iniciales (`db/10`) no le dan el permiso `consultar_red`.
- La Figura 17 no dice cómo se declara detectada una falla de ausencia de dato, que no deja mediciones marcadas.
