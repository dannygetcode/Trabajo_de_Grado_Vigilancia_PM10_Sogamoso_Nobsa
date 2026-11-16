# Backlog del producto

Historias de usuario derivadas de RF-01 a RF-16 (Tabla 15), con los RNF de la Tabla 16 como criterios de aceptación o historias de verificación. El orden sigue la Tabla 5 y `docs/TRAZABILIDAD.md`. Las prioridades las valida la asesora como representante del dueño del producto (3.2.1).

- **Puntos**: estimación inicial relativa (1, 2, 3, 5, 8). Se ajustan en la planeación de cada sprint.
- **Modelo**: `Opus` implementa directo. `Fable→Opus` significa que antes hay que escribir el plan en `docs/planes/`.
- **Commits**: `HU-07: ingesta acepta lotes horarios`. Una rama por historia.
- Los criterios marcados con *(interpretación)* cubren algo que el documento no fija; están listados al final.

## Definición de terminado (aplica a todas)

- Pruebas automatizadas que cubren cada criterio de aceptación; CI en verde.
- Ninguna hora de dominio sale del sistema: se inyecta el reloj y las pruebas usan uno falso.
- Si la historia toca una API, el OpenAPI generado coincide con `docs/api/` (RNF-09).
- Reglas de validación y de evaluación normativa con cobertura de 70 % o más (RNF-19).
- Integrada en `main`, desplegada en la nube y con la prueba de humo en verde (ADR-0003). El despliegue no se deja para el Sprint 6.
- `docs/ESTADO.md` actualizado.

## Resumen

| Sprint | Objetivo (Tabla 5) | Historias | Puntos |
|---|---|---|---|
| 1 | Ingesta, simulador y reloj virtual | HU-01 a HU-15, HU-60 | 41 |
| 2 | Validación automática y revisión manual | HU-16 a HU-28 | 44 |
| 3 | Agregación y evaluación normativa | HU-29 a HU-36 | 32 |
| 4 | Modelo de pronóstico | HU-37 a HU-44 | 34 |
| 5 | Notificaciones, informe, exportación y vista pública | HU-45 a HU-51 | 30 |
| 6 | Pruebas, usabilidad y despliegue | HU-52 a HU-59 | 25 |
| | **Total** | **60 historias** | **206** |

Son seis sprints de construcción de dos semanas (1 a 6) más el Sprint 0 de preparación, cuyas tareas no son historias de usuario y están en `docs/planes/sprint-0-construccion.md`. La velocidad real se conoce al cerrar el Sprint 1; si queda por debajo de 34 puntos, lo primero que se recorta está marcado al final de este archivo.

El Sprint 2 es el más cargado porque ahí empieza `web/` y entran las historias transversales de RF-14. Si no cabe, HU-26 (administrar usuarios) puede pasar al Sprint 3 sin bloquear nada: los usuarios se pueden crear por SQL mientras tanto.

| RF | Historias |
|---|---|
| RF-01 | HU-07, HU-08, HU-09, HU-10 |
| RF-02 | HU-17, HU-18, HU-19, HU-20 |
| RF-03 | HU-22, HU-23 |
| RF-04 | HU-07, HU-09, HU-23, HU-24 |
| RF-05 | HU-31, HU-32 |
| RF-06 | HU-33, HU-34, HU-36 |
| RF-07 | HU-35 |
| RF-08 | HU-37 a HU-42 |
| RF-09 | HU-43, HU-44 |
| RF-10 | HU-45, HU-46, HU-47 |
| RF-11 | HU-48, HU-49 |
| RF-12 | HU-50 |
| RF-13 | HU-51 |
| RF-14 | HU-04, HU-05, HU-25, HU-26 |
| RF-15 | HU-29, HU-30, HU-45 |
| RF-16 | HU-01, HU-02, HU-03, HU-11 a HU-15, HU-21 |

| RNF | Historias que lo verifican |
|---|---|
| RNF-01 | HU-19, HU-56 |
| RNF-02 | HU-08, HU-31, HU-37 |
| RNF-03 | HU-20, HU-27 |
| RNF-04 | HU-13, HU-52 |
| RNF-05 | HU-04, HU-05, HU-24 |
| RNF-06 | HU-40, HU-41 |
| RNF-07 | HU-28, HU-57 |
| RNF-08 | HU-53 (y el esqueleto desplegado en el Sprint 0) |
| RNF-09 | HU-60 y la definición de terminado |
| RNF-10 | HU-55 |
| RNF-11 | HU-03, HU-15 |
| RNF-12 | HU-50 |
| RNF-13 | HU-23, HU-28, HU-35 |
| RNF-14 | HU-51 |
| RNF-15 | HU-16, HU-41 |
| RNF-16 | HU-54 |
| RNF-17 | HU-04, HU-53 |
| RNF-18 | HU-06, HU-24 |
| RNF-19 | HU-17, HU-18, HU-33, HU-58 |
| RNF-20 | HU-06, HU-53 |

---

## Sprint 1. Ingesta, simulador y reloj virtual

Entregable: API de ingesta operando con datos reproducidos y reloj virtual. Contratos en `docs/api/`.

### HU-01 · Hora de dominio única
`RF-16 · servicios/comun, simulador (reloj) · 2 pts · Opus`

Como servicio del sistema quiero pedir la hora a un único reloj para que todos trabajemos con la misma hora, real o simulada.

- [ ] `GET /v1/hora` en modo `REAL` devuelve la hora del sistema en UTC, estado `CORRIENDO` y velocidad 1.
- [ ] `servicios/comun` ofrece un cliente del reloj y un reloj falso para pruebas; `domain/` solo conoce la interfaz.
- [ ] Una comprobación en CI falla si aparece `datetime.now`, `utcnow` o `time.time` fuera del servicio de reloj y de la autenticación.
- [ ] Si el reloj no responde, el cliente lanza un error propio; nunca devuelve la hora del sistema.

### HU-02 · Reloj virtual configurable
`RF-16 · CU-14 · simulador (reloj) · 3 pts · Opus`

Como simulador quiero poner el reloj en modo virtual, con inicio, fin y velocidad, y pausarlo o reanudarlo.

- [ ] Tras `PUT /v1/reloj` en modo `VIRTUAL`, la hora avanza a `velocidad` segundos virtuales por segundo real desde `inicio` (probado con reloj monótono falso).
- [ ] En pausa la hora no cambia; al reanudar sigue desde donde quedó.
- [ ] Cada reconfiguración incrementa `epoca`; pausar y reanudar no.
- [ ] Al llegar a `fin` el estado es `FINALIZADO` y la hora no pasa de `fin`.
- [ ] Al arrancar con un escenario `EN_EJECUCION` o `PAUSADO` en la base, el reloj queda `VIRTUAL`, `PAUSADO`, en `reloj_actual`.
- [ ] Sin permiso `simulacion`, las operaciones de control responden 403.

### HU-03 · Barrera horaria
`RF-16, RNF-11 · simulador (reloj) · 3 pts · Fable→Opus (docs/planes/reloj-virtual.md)`

Como responsable de la verificación quiero que el reloj acelerado espere a que cada hora termine de procesarse, para que dos reproducciones del mismo escenario den el mismo resultado.

- [ ] El reloj no pasa de la menor hora confirmada más una hora; mientras espera, el estado es `RETENIDO` y `retenido_por` nombra a quien falta.
- [ ] Al subir la barrera el reloj continúa desde ella, sin saltar el tiempo que estuvo retenido.
- [ ] Confirmar una hora futura responde 409; repetir una confirmación no cambia nada.
- [ ] `GET /v1/hora?esperar_hasta=t` responde en cuanto la hora llega a `t`, cambia la época o vence `espera_max`.
- [ ] Prueba de concurrencia: con velocidad 100 000 y un participante lento, ninguna lectura de la hora supera la barrera.

### HU-04 · Inicio de sesión y token
`RF-14, RNF-05, RNF-17 · CU-15 · servicios/ingesta · 3 pts · Fable→Opus (docs/planes/autenticacion.md)`

Como usuario o cuenta de servicio quiero iniciar sesión con correo y contraseña y recibir un token con los permisos de mi rol.

- [ ] Credenciales correctas de una cuenta `ACTIVA` devuelven un JWT RS256 con `sub`, `rol`, `permisos` y `exp`, y reinician el contador de intentos.
- [ ] Contraseña equivocada, cuenta inexistente, `BLOQUEADA` o `INACTIVA` responden el mismo 401.
- [ ] Al quinto intento fallido seguido la cuenta queda `BLOQUEADA` y ni la contraseña correcta entra.
- [ ] Las contraseñas se guardan con Argon2id; nunca aparecen en registros ni respuestas.
- [ ] Cada intento, exitoso o no, queda en `registro_auditoria`.
- [ ] Una herramienta en `tools/` crea el primer administrador y las cuentas de servicio; no hay contraseñas por defecto en el repositorio.

### HU-05 · Autorización por permisos en cada API
`RF-14, RNF-05 · servicios/comun · 2 pts · Opus`

Como responsable del sistema quiero que cada operación exija un token válido y el permiso que le corresponde.

- [ ] Sin token, con token vencido o con firma inválida: 401. Con token válido sin el permiso: 403.
- [ ] Los servicios verifican con la llave pública; solo la ingesta usa la privada, que se configura únicamente en el contenedor `nucleo`.
- [ ] Un token firmado con otra llave o con algoritmo `none` o `HS256` se rechaza.
- [ ] Prueba por servicio que recorre todas las rutas del OpenAPI y comprueba que solo `/v1/salud` y `POST /v1/sesiones` responden sin token.

### HU-06 · Roles de base de datos por servicio
`ADR-0001, RNF-18 · db/11_roles_servicios.sql · 2 pts · Opus`

Como arquitecto quiero que cada servicio se conecte con un rol que solo puede escribir sus tablas.

- [ ] `db/11` crea los roles de la tabla de propiedad del ADR-0001 y el rol de aplicación `SIMULADOR` con `{ingesta, procesos_programados, simulacion}`.
- [ ] `db/11` agrega el permiso `consultar_red` al rol `COORDINADOR` (CU-04).
- [ ] Con el rol de un servicio, escribir en una tabla ajena falla por permisos.
- [ ] Ningún rol de servicio puede hacer `UPDATE` ni `DELETE` sobre `registro_auditoria`.
- [ ] `tools/db_aplicar.py` aplica los scripts 01 a 11 sobre una base vacía, igual en `infra/docker-compose.yml` y en Neon, y no repite los ya aplicados.
- [ ] Las contraseñas de los roles salen de variables de entorno; no hay ninguna en `db/11`.

### HU-07 · Ingesta acepta lotes horarios
`RF-01, RF-04 · CU-01 · P-02 · servicios/ingesta · 3 pts · Opus`

Como fuente de datos quiero enviar un lote de mediciones horarias y recibir un resumen de lo registrado.

- [ ] Un lote válido responde 202 con `recibidas`, `registradas`, `duplicadas` y `recibido_en`.
- [ ] Cada medición queda en estado `CRUDO` con `valor_crudo` idéntico al enviado, incluido `null`.
- [ ] `recibida_en` es la hora del reloj, no la del sistema ni el valor por defecto de la base.
- [ ] Un valor fuera del rango físico se registra igual: juzgarlo es tarea de la validación.
- [ ] Sin permiso `ingesta` responde 403; si el reloj no responde, 503 y no se registra nada.

### HU-08 · El lote que incumple el contrato se rechaza completo
`RF-01, RNF-02 · CU-01 (4a) · servicios/ingesta · 2 pts · Opus`

Como responsable de la calidad del dato quiero que un lote mal formado no deje nada registrado.

- [ ] Una prueba por cada código de la tabla de reglas de `ingesta.yaml`.
- [ ] La respuesta 400 trae todos los errores del lote, con el índice de la medición y el campo.
- [ ] Con una sola medición inválida entre cien válidas no se registra ninguna.
- [ ] Una medición con `fin` posterior a la hora del reloj se rechaza con `MEDICION_FUTURA`.
- [ ] Un valor con más de tres decimales se rechaza; no se redondea.

### HU-09 · Las duplicadas se cuentan sin detener el lote
`RF-01, RF-04 · CU-01 (5a) · servicios/ingesta · 1 pt · Opus`

Como fuente de datos quiero poder reenviar un lote sin crear datos repetidos ni recibir un error.

- [ ] Reenviar el mismo lote responde 202 con `registradas = 0` y `duplicadas = recibidas`.
- [ ] Una duplicada con valor distinto no cambia el `valor_crudo` ya guardado.
- [ ] Dos mediciones iguales en estación, variable e inicio dentro del mismo lote: se guarda la primera y la segunda cuenta como duplicada.

### HU-10 · Consultar las mediciones registradas
`RF-01 · CU-04 (parte) · servicios/ingesta · 2 pts · Opus`

Como técnico quiero consultar las mediciones de un periodo para comprobar qué llegó.

- [ ] Filtra por periodo obligatorio y, opcionalmente, por estación, variable y estado.
- [ ] Pagina con `limite` y `desplazamiento` y devuelve el total.
- [ ] La respuesta no incluye `falla_id`.
- [ ] Sin permiso `consultar_red` responde 403.

### HU-11 · Crear un escenario de simulación con fallas
`RF-16 · CU-14 (1 a 5) · simulador · 3 pts · Opus`

Como administrador quiero definir un escenario con periodo, velocidad y fallas para preparar una reproducción.

- [ ] El escenario queda `CONFIGURADO` y sus fallas `PROGRAMADA`.
- [ ] Una falla fuera del periodo, o sobre una variable que la estación no mide, responde 400 y no se guarda nada.
- [ ] Un periodo que el archivo histórico no cubre responde `PERIODO_SIN_HISTORICO`.
- [ ] `GET /v1/historico` informa la cobertura por estación y variable.
- [ ] Solo se puede reemplazar un escenario mientras está `CONFIGURADO`.

### HU-12 · Iniciar, pausar, reanudar y detener un escenario
`RF-16 · CU-14 (6, 6a) · simulador · 3 pts · Opus`

Como administrador quiero controlar la ejecución del escenario.

- [ ] Las transiciones siguen la Figura 16; cualquier otra responde 409 `TRANSICION_INVALIDA`.
- [ ] No se puede iniciar un escenario si otro está `EN_EJECUCION` o `PAUSADO`.
- [ ] Iniciar configura el reloj en modo virtual; pausar lo congela; detener deja el escenario `FINALIZADO`.
- [ ] Si el reloj no responde, el escenario no cambia de estado y la respuesta es 503.
- [ ] Tras reiniciar el simulador con un escenario `EN_EJECUCION`, la reproducción continúa desde `reloj_actual` sin horas perdidas ni repetidas.

### HU-13 · Reproducir los datos históricos hora a hora
`RF-16, RNF-04 · CU-01 · P-01 · simulador · 5 pts · Fable→Opus (docs/planes/reloj-virtual.md)`

Como responsable de la verificación quiero que el simulador envíe las mediciones históricas siguiendo el reloj virtual, como lo haría la red real.

- [ ] En cada hora `t` envía un lote con las mediciones cuyo inicio está en `[t - 1 h, t)`, guarda `reloj_actual = t` y confirma `t` al reloj.
- [ ] Reproducir un mes sin fallas deja en `medicion` exactamente los registros del archivo histórico de ese mes.
- [ ] Si la ingesta falla, el simulador reintenta y no confirma la hora; al recuperarse no hay huecos ni duplicados.
- [ ] Al llegar al fin del periodo el escenario queda `FINALIZADO`.
- [ ] El simulador solo usa `reloj.yaml` e `ingesta.yaml` para hablar con el resto: no escribe en `medicion`.
- [ ] El archivo histórico se lee desde una ruta configurada fuera del repositorio.

### HU-14 · Inyectar fallas controladas
`RF-16 · P-01 · simulador · 3 pts · Opus`

Como responsable de la verificación quiero alterar mediciones de forma conocida para medir después las reglas de validación.

- [ ] Una prueba por tipo de falla comprueba el efecto descrito en `simulador.yaml`.
- [ ] Las mediciones alteradas llegan a la ingesta con `falla_id`; las de `AUSENCIA_DE_DATO` no se envían.
- [ ] La falla pasa a `INYECTADA` cuando el reloj alcanza su inicio.
- [ ] El mismo escenario produce los mismos lotes en dos ejecuciones.
- [ ] Las mediciones fuera del intervalo de la falla llegan sin cambios.

### HU-15 · Reproducir un año en menos de 30 minutos
`RNF-11 · simulador, servicios/ingesta · 2 pts · Opus`

Como responsable de la verificación quiero reproducir un año de las cinco estaciones en menos de media hora.

- [ ] Un escenario de 365 días con velocidad 17 520 termina en menos de 30 minutos en el entorno de referencia (el compose en el equipo de desarrollo), con todas las mediciones registradas.
- [ ] La misma reproducción se mide en la nube y se reporta como dato informativo, sin umbral (ADR-0003).
- [ ] El resultado queda escrito en `docs/pruebas/` con la fecha, el equipo y el tiempo medido.
- [ ] Se repite la medición al cerrar el Sprint 3, con la validación y la evaluación activas.

### HU-60 · Núcleo: varios servicios en un contenedor sin mezclarlos
`RNF-08, RNF-09 · ADR-0001 · servicios/nucleo · 2 pts · Opus`

Como arquitecto quiero ejecutar el reloj y la ingesta en un mismo contenedor sin que dejen de ser servicios separados, para que el sistema quepa en un plan gratuito.

- [ ] `nucleo` monta cada aplicación bajo su prefijo (`/reloj`, `/ingesta`) y expone `/salud` con el estado de cada una.
- [ ] Dentro del núcleo, la ingesta consulta el reloj con el mismo cliente HTTP y el mismo token, por transporte en proceso; con `SVCA_URL_RELOJ` apuntando a otra máquina, usa la red sin cambiar código.
- [ ] Cada servicio arranca también solo y su OpenAPI coincide con `docs/api/`.
- [ ] `import-linter` falla en CI si un servicio importa a otro o si `domain/` importa algo externo.
- [ ] El contenedor arranca con un único worker; un comentario en el `Dockerfile` explica por qué.
- [ ] Las peticiones desde un origen que no está en `SVCA_ORIGENES` no reciben cabeceras CORS.

---

## Sprint 2. Validación automática y revisión manual

Entregable: reglas de validación, cola de revisión y auditoría de cambios.

### HU-16 · Planificador gobernado por el reloj
`P-04, P-06, P-07, RNF-15 · servicios/planificador (corre dentro de `nucleo`) · 3 pts · Fable→Opus (docs/planes/reloj-virtual.md)`

Como sistema quiero un planificador que dispare los procesos periódicos según el reloj de dominio.

- [ ] Dispara una vez por cada cambio de hora, en orden, también tras una pausa o con el reloj acelerado.
- [ ] Participa en la barrera: confirma la hora `t` cuando terminan los procesos de `t`.
- [ ] Si un proceso falla, lo registra, sigue con los demás y aun así confirma la hora (RNF-15).
- [ ] Al cambiar la época descarta lo que tenía pendiente.
- [ ] En reposo solo consulta el reloj: no abre conexiones a la base de datos (ADR-0003, cómputo de Neon).

### HU-17 · Reglas críticas: rango físico y mantenimiento
`RF-02 · CU-02 · P-03 · servicios/ingesta · 3 pts · Opus`

Como técnico quiero que los datos imposibles o tomados en mantenimiento se invaliden solos.

- [ ] Un valor fuera de `[minimo_fisico, maximo_fisico]` de la variable queda `INVALIDO` con la regla aplicada. *(interpretación)*
- [ ] Un valor `null` queda `INVALIDO`. *(interpretación)*
- [ ] Una medición dentro de un periodo de mantenimiento queda `INVALIDO` sin aplicar las demás reglas (CU-02, 2a).
- [ ] Las reglas son funciones puras de `domain/`; no leen `falla_id`.

### HU-18 · Reglas de advertencia: valor repetido, cambio brusco y comparación entre estaciones
`RF-02 · CU-02 · P-03 · servicios/ingesta · 5 pts · Fable→Opus (docs/planes/validacion.md)`

Como técnico quiero que los datos dudosos se marquen como sospechosos para revisarlos.

- [ ] El mismo valor durante seis horas seguidas marca `SOSPECHOSO`.
- [ ] Un salto mayor que el umbral configurado frente a la hora anterior marca `SOSPECHOSO`.
- [ ] Una diferencia mayor que el umbral frente a las demás estaciones a la misma hora marca `SOSPECHOSO`; si no hay datos de otras estaciones, la regla se omite y la omisión queda registrada (2b).
- [ ] Los umbrales son configuración, no constantes en el código.
- [ ] El orden es el de la Figura 32 y `regla_aplicada` guarda la primera regla que falló.

### HU-19 · Validar cada lote al recibirlo
`RF-02, RNF-01 · CU-01 (6), CU-02 · servicios/ingesta · 3 pts · Opus`

Como técnico quiero que ningún dato quede sin calificar.

- [ ] Tras responder un lote, ninguna de sus mediciones sigue en `CRUDO`.
- [ ] Las sospechosas aparecen en la cola de revisión.
- [ ] Al terminar se pide al servicio normativo recalcular los promedios afectados; si ese servicio no responde, la validación no falla y la petición se reintenta.
- [ ] Se registra la duración real entre la llegada del lote y el fin de la validación.

### HU-20 · Detectar una estación sin transmisión
`RF-02, RNF-03 · P-04 · servicios/ingesta · 3 pts · Opus`

Como técnico quiero saber cuándo una estación deja de transmitir.

- [ ] Una estación `OPERATIVA` sin datos durante más de dos horas pasa a `SIN_TRANSMISION`.
- [ ] La primera medición nueva la devuelve a `OPERATIVA`.
- [ ] Las estaciones `EN_MANTENIMIENTO` o `INACTIVA` no se marcan.
- [ ] Un escenario con una falla `AUSENCIA_DE_DATO` de cuatro horas demuestra la detección dentro del plazo.

### HU-21 · Cerrar las fallas y medir la detección
`RF-16 · sección 3.5.1 · simulador · 3 pts · Opus`

Como responsable de la verificación quiero saber qué fallas inyectadas detectaron las reglas.

- [ ] Al terminar una falla queda `DETECTADA` si alguna de sus mediciones fue `SOSPECHOSO` o `INVALIDO`, y `NO_DETECTADA` en caso contrario.
- [ ] Una falla `AUSENCIA_DE_DATO` queda `DETECTADA` si la estación pasó a `SIN_TRANSMISION` durante su intervalo. *(interpretación)*
- [ ] Un reporte por escenario da precisión y exhaustividad por tipo de falla.

### HU-22 · Cola de revisión
`RF-03 · CU-03 (1 a 3) · servicios/ingesta, web · 3 pts · Opus`

Como técnico quiero ver los datos sospechosos con su contexto para decidir sobre ellos.

- [ ] Lista estación, hora, valor, regla que lo marcó, las horas vecinas y las otras estaciones a la misma hora.
- [ ] Si la cola está vacía, lo dice (2a).
- [ ] Solo el permiso `revisar` da acceso.

### HU-23 · Aprobar, corregir o invalidar con justificación
`RF-03, RF-04, RNF-13 · CU-03 (4 a 8) · P-05 · servicios/ingesta, web · 5 pts · Opus`

Como técnico quiero decidir sobre un dato sospechoso dejando constancia del motivo.

- [ ] La decisión deja la medición en `VALIDADO_MANUAL`, `CORREGIDO` o `INVALIDADO` y crea una `revision` con usuario, fecha del reloj y justificación.
- [ ] Sin justificación no se puede confirmar (6a); invalidar pide además confirmación explícita.
- [ ] Al corregir, el valor nuevo debe estar dentro del rango físico (4a) y se guarda en la revisión; `valor_crudo` no cambia.
- [ ] Solo se revisan mediciones en `SOSPECHOSO`; dos técnicos sobre el mismo dato no producen dos revisiones.
- [ ] Se pide el recálculo de los promedios afectados.

### HU-24 · Auditoría que no se puede alterar
`RF-04, RNF-05, RNF-18 · db, servicios/comun · 2 pts · Opus`

Como coordinador quiero un registro confiable de quién hizo qué.

- [ ] Cada revisión, cambio de configuración e inicio de sesión queda con usuario, fecha, acción, entidad y detalle.
- [ ] Ninguna API permite modificar ni borrar registros de auditoría.
- [ ] La prueba de permisos de HU-06 se ejecuta en CI.

### HU-25 · Iniciar sesión en la web y ver el menú del rol
`RF-14 · CU-15 · web · 3 pts · Opus`

Como usuario interno quiero entrar a la web y ver solo lo que mi rol permite.

- [ ] El menú muestra solo las opciones de los permisos del token.
- [ ] Un error de credenciales muestra un mensaje genérico.
- [ ] Al vencer el token, la web vuelve a la pantalla de inicio de sesión.
- [ ] Entrar por URL directa a una pantalla sin permiso no muestra datos.

### HU-26 · Administrar usuarios
`RF-14 · CU-13 · servicios/ingesta, web · 3 pts · Opus`

Como administrador quiero crear, editar, desactivar y desbloquear cuentas.

- [ ] Crear y editar usuarios con uno de los roles existentes.
- [ ] Desbloquear una cuenta la deja `ACTIVA` con el contador en cero.
- [ ] El administrador no puede desactivar su propia cuenta (4a).
- [ ] Cada cambio queda en la auditoría.

### HU-27 · Tablero del estado de la red
`RF-05, RF-15, RNF-03 · CU-04 · servicios/ingesta, web · 5 pts · Opus`

Como técnico o coordinador quiero ver de un vistazo cómo está la red.

- [ ] Cada estación muestra estado, hora del último dato y completitud del día y del mes.
- [ ] Una estación `SIN_TRANSMISION` se resalta y dice desde cuándo (2a).
- [ ] Muestra cuántos datos esperan revisión.
- [ ] La serie de una estación y un periodo se grafica con la bandera de cada dato; un periodo sin datos lo informa (4a).

### HU-28 · Interfaz de revisión usable
`RNF-07, RNF-13 · web · 3 pts · Opus`

Como técnico quiero revisar la cola completa sin pasos de más.

- [ ] Revisar un dato toma como máximo tres acciones desde la cola.
- [ ] Los errores se muestran junto al campo y no borran lo escrito.
- [ ] Las tareas del guion de la prueba SUS (HU-57) se pueden completar de principio a fin.

---

## Sprint 3. Agregación y evaluación normativa

Entregable: promedios móviles, evaluación de los artículos 11 y 12 y flujo de declaratoria. Antes de empezar: `docs/planes/normativo.md` (Fable) con la lectura de los artículos 10 a 12 de la Resolución 2254 de 2017.

### HU-29 · Administrar estaciones, variables y mantenimientos
`RF-15 · CU-13 · servicios/ingesta, web · 3 pts · Opus`

Como administrador quiero mantener la red de monitoreo sin tocar el código.

- [ ] Crear, editar y dar de baja estaciones; asignar las variables que mide cada una.
- [ ] Registrar periodos de mantenimiento con motivo.
- [ ] Un rango físico con mínimo mayor o igual que el máximo se rechaza (5a).
- [ ] Una estación nueva recibe mediciones sin desplegar nada.

### HU-30 · Administrar parámetros normativos con vigencia
`RF-15 · CU-13 · servicios/normativo, web · 3 pts · Opus`

Como administrador quiero ajustar los umbrales si la norma cambia.

- [ ] Un parámetro nuevo tiene fecha de inicio de vigencia; el anterior no se borra.
- [ ] Un umbral mínimo mayor que el máximo se rechaza (5a).
- [ ] La evaluación de una hora usa el parámetro vigente en esa hora, no el más reciente.

### HU-31 · Promedios móviles de 24 horas y representatividad
`RF-05 · CU-05 · P-06 · servicios/normativo · 3 pts · Opus`

Como coordinador quiero el promedio móvil de 24 horas de cada estación con su representatividad.

- [ ] Cada hora se calcula el promedio de las 24 horas anteriores con los datos de `v_medicion_valida`.
- [ ] `horas_validas` cuenta los datos usados; con menos de 18 el promedio no es representativo.
- [ ] Un dato corregido entra con el valor corregido; uno invalidado no entra.
- [ ] El cálculo de la hora `t` no usa ningún dato posterior a `t`.

### HU-32 · Recalcular promedios cuando cambia un dato
`RF-05 · CU-02 (5), CU-03 (8) · servicios/normativo · 3 pts · Opus`

Como coordinador quiero que una revisión se refleje en los promedios.

- [ ] Cambiar el estado de una medición recalcula los 24 promedios que la incluyen.
- [ ] Recalcular dos veces da el mismo resultado.
- [ ] Solo la ingesta puede pedir el recálculo (permiso de servicio).

### HU-33 · Evaluación horaria de niveles y cobertura
`RF-06 · CU-05 (1 a 5) · P-07 · servicios/normativo · 8 pts · Fable→Opus (docs/planes/normativo.md)`

Como coordinador quiero que el sistema evalúe cada hora los niveles de prevención, alerta y emergencia.

- [ ] Compara cada promedio representativo con los umbrales vigentes y calcula la cobertura de estaciones y el porcentaje de tiempo en el rango.
- [ ] Guarda una `evaluacion_normativa` por hora con los promedios que usó.
- [ ] Si ninguna estación tiene promedio representativo, registra la evaluación sin nivel (2a).
- [ ] Casos de prueba tabulados para cada nivel y para los bordes de cada umbral.
- [ ] Cobertura de pruebas de 70 % o más en este módulo (RNF-19).

### HU-34 · Propuesta de declaratoria y cierre automático
`RF-06 · CU-05 (6, 6a) · servicios/normativo · 5 pts · Fable→Opus (docs/planes/normativo.md)`

Como coordinador quiero recibir una propuesta cuando se alcanza un nivel y que la declaratoria se cierre cuando cesa.

- [ ] Al alcanzar prevención sin declaratoria abierta se crea una `PROPUESTA` con las estaciones afectadas y se avisa al coordinador.
- [ ] No se crea una segunda propuesta mientras hay una abierta.
- [ ] Una declaratoria `CONFIRMADA` pasa a `CERRADA` cuando la evaluación indica que las condiciones cesaron.
- [ ] Ninguna declaratoria se confirma sola.

### HU-35 · Confirmar o descartar la propuesta
`RF-07, RNF-13 · CU-06 · servicios/normativo, web · 5 pts · Opus`

Como coordinador quiero decidir sobre la propuesta con el soporte técnico a la vista.

- [ ] La propuesta muestra nivel, promedios de las últimas 48 horas, porcentaje de tiempo en el rango, cobertura y, si aplica, el pronóstico que la originó.
- [ ] Confirmar exige soporte técnico; descartar exige justificación y confirmación explícita.
- [ ] Con cobertura menor al 50 % de las estaciones se indica que solo aplica a estaciones individuales (3a).
- [ ] Confirmar deja la declaratoria `CONFIRMADA` y solicita la notificación; descartar no notifica.
- [ ] La decisión queda en la auditoría.

### HU-36 · Aumento de nivel en una declaratoria confirmada
`RF-06 · Figura 8 · servicios/normativo · 2 pts · Opus`

Como coordinador quiero que la declaratoria refleje un empeoramiento.

- [ ] Si el nivel evaluado supera el de la declaratoria confirmada, esta se actualiza y se solicita una nueva notificación.
- [ ] Una baja de nivel sin cese no modifica la declaratoria. *(interpretación)*

---

## Sprint 4. Modelo de pronóstico

Entregable: servicio de pronóstico diario y tablero de desempeño. Antes de empezar: `docs/planes/pronostico.md` (Fable) con variables de entrada, algoritmo, método del intervalo y pruebas de fuga temporal.

### HU-37 · Variables de entrada sin fuga temporal
`RF-08, RNF-02 · CU-07 (2) · servicios/pronostico · 5 pts · Fable→Opus`

Como responsable del modelo quiero que las variables de entrada usen solo datos anteriores al momento de emisión.

- [ ] Cada variable de entrada tiene una prueba que falla si se le entrega un dato igual o posterior a la emisión.
- [ ] La misma función construye las variables en entrenamiento y en operación.
- [ ] Los datos salen de `v_medicion_valida`, con el valor corregido cuando lo hay.

### HU-38 · Entrenar, evaluar y registrar una versión del modelo
`RF-08, RF-09 · CRISP-DM · servicios/pronostico · 8 pts · Fable→Opus`

Como responsable del modelo quiero entrenar con partición temporal y dejar registradas las métricas.

- [ ] Entrenamiento con 2020 a 2022, validación y calibración del intervalo con 2023, prueba con 2024.
- [ ] Se reportan MAE y RMSE frente a persistencia y climatología, exhaustividad y precisión sobre 75 µg/m³ y cobertura real del intervalo.
- [ ] La versión queda `REGISTRADA` con sus métricas y el nombre del artefacto, que incluye su SHA-256. El `.joblib` no entra al árbol de git: se publica como adjunto de una versión en GitHub Releases (ADR-0003).
- [ ] El servicio rechaza un artefacto cuyo SHA-256 no coincide con el registrado.
- [ ] El entrenamiento lee el archivo histórico normalizado en el equipo de desarrollo, no la base de la nube.
- [ ] Con la misma semilla y los mismos datos se obtiene el mismo modelo.

### HU-39 · Activar una versión del modelo
`RF-08 · Figura 11 · servicios/pronostico · 2 pts · Opus`

Como coordinador quiero que solo esté activa una versión que supere las líneas base.

- [ ] Solo se activa una versión cuyo MAE es menor que el de persistencia y el de climatología.
- [ ] Al activar una, la anterior pasa a `RETIRADA`; nunca hay dos activas.

### HU-40 · Pronóstico diario con intervalo y categoría del ICA
`RF-08, RNF-06 · CU-07 · P-08 · servicios/pronostico · 5 pts · Opus`

Como coordinador quiero cada día el pronóstico de PM10 de las siguientes 24 horas por estación.

- [ ] El planificador lo dispara a la hora configurada según el reloj.
- [ ] Cada valor pronosticado tiene intervalo de predicción y categoría del ICA.
- [ ] Queda una `ejecucion_ciclo` con entradas, versión del modelo y resultado.
- [ ] Ejecutar dos veces el mismo día no duplica el pronóstico.

### HU-41 · El ciclo tolera datos insuficientes y errores del modelo
`RF-08, RNF-06, RNF-15 · CU-07 (2a, 3a) · servicios/pronostico · 3 pts · Opus`

Como coordinador quiero que un fallo del pronóstico no detenga el resto del sistema.

- [ ] Una estación sin datos suficientes se omite con su motivo y la ejecución queda `PARCIAL`.
- [ ] Si el modelo falla, la ejecución queda `FALLIDA` con el mensaje y no se publica pronóstico ese día.
- [ ] Con el contenedor `pronostico` detenido, una reproducción de 48 horas completa la ingesta, la validación y la evaluación normativa, y el planificador registra el fallo de P-08 sin detener la hora (prueba de RNF-15, automatizada en el compose y repetida a mano en la nube).
- [ ] El planificador espera hasta dos minutos la respuesta de `pronostico`, que puede estar despertando.

### HU-42 · Propuesta de declaratoria por pronóstico
`RF-08, RF-06 · CU-07 (6) · servicios/pronostico, servicios/normativo · 3 pts · Opus`

Como coordinador quiero una propuesta cuando el pronóstico supera el umbral configurado.

- [ ] El servicio de pronóstico la solicita al normativo; no escribe en `declaratoria`.
- [ ] La propuesta tiene origen `PRONOSTICO` y referencia el pronóstico que la generó.
- [ ] Nunca se confirma sola (sección 3.5.1).

### HU-43 · Seguimiento del pronóstico con el valor observado
`RF-09 · P-09 · servicios/pronostico · 3 pts · Opus`

Como coordinador quiero que cada pronóstico se compare con lo que ocurrió.

- [ ] Con el primer valor observado el pronóstico pasa a `EN_SEGUIMIENTO` y cada hora registra su error.
- [ ] Al vencer las 24 horas queda `EVALUADO` con 18 o más horas observadas e `INCOMPLETO` con menos. *(interpretación)*
- [ ] Las métricas de la versión activa se actualizan.

### HU-44 · Tablero de desempeño del pronóstico
`RF-09 · CU-08 · servicios/pronostico, web · 5 pts · Opus`

Como coordinador quiero ver qué tan bien pronostica el modelo antes de apoyarme en él.

- [ ] Muestra MAE y RMSE de la versión activa frente a persistencia y climatología.
- [ ] Muestra exhaustividad y precisión sobre 75 µg/m³ y la cobertura del intervalo.
- [ ] Grafica pronóstico, intervalo y observado por estación y periodo.
- [ ] Sin pronósticos evaluados, muestra solo las métricas de validación (2a).

---

## Sprint 5. Notificaciones, informe, exportación y vista pública

Entregable: correos de prueba, informe mensual en PDF y página pública del ICA.

### HU-45 · Administrar contactos
`RF-10, RF-15 · CU-13 · servicios/notificaciones, web · 2 pts · Opus`

Como administrador quiero mantener la lista de contactos de salud y gestión del riesgo.

- [ ] Crear, editar, activar y desactivar contactos.
- [ ] Cada cambio queda en la auditoría.

### HU-46 · Notificar por correo
`RF-10 · CU-09 · P-10 · servicios/notificaciones · 5 pts · Opus`

Como entidad de salud o de gestión del riesgo quiero recibir un correo cuando se confirma una declaratoria o se pronostica riesgo.

- [ ] Se crea una notificación por cada contacto activo.
- [ ] El mensaje incluye nivel, estaciones, vigencia y recomendaciones del ICA.
- [ ] El envío pasa por un puerto con dos adaptadores: SMTP (Mailpit, en local y CI) y API HTTPS del proveedor (nube).
- [ ] En pruebas locales, los correos llegan al servidor de captura y a nadie más.
- [ ] En la nube, con `SVCA_CORREO_REDIRIGIR_A` configurado, todos los mensajes van a ese único buzón con el destinatario original en el asunto; una prueba comprueba que ningún otro destinatario sale del sistema.
- [ ] Sin contactos activos se alerta al administrador (1a).

### HU-47 · Reintentos de envío
`RF-10 · CU-09 (4a) · servicios/notificaciones · 2 pts · Opus`

Como administrador quiero enterarme cuando un correo no se pudo entregar.

- [ ] Un envío fallido pasa a `EN_REINTENTO` y se reintenta hasta tres veces.
- [ ] Al tercer fallo queda `FALLIDA` y se alerta al administrador.
- [ ] Cada contacto activo termina con un estado final registrado.

### HU-48 · Generar el informe mensual en PDF
`RF-11 · CU-10 (1 a 4) · P-11 · servicios/notificaciones · 8 pts · Opus`

Como coordinador quiero el informe mensual hecho a partir de los datos validados.

- [ ] Solo se genera para un mes ya terminado.
- [ ] Incluye datos validados, promedios, excedencias, representatividad y declaratorias, con tablas y gráficas.
- [ ] Si quedan datos pendientes de revisión en el periodo, lo advierte antes de generar (2a).
- [ ] Usa solo datos de `v_medicion_valida`.
- [ ] El PDF se guarda en la base (`informe_archivo`, `db/12`), no en disco: los contenedores gratuitos no tienen disco persistente (ADR-0003).

### HU-49 · Aprobar o devolver el informe
`RF-11 · CU-10 (5, 6) · servicios/notificaciones, web · 2 pts · Opus`

Como coordinador quiero revisar el informe antes de dejarlo disponible.

- [ ] Aprobar lo deja `APROBADO` y disponible para consulta.
- [ ] Devolver exige observaciones y lo deja `DEVUELTO`; un informe devuelto se puede regenerar.

### HU-50 · Exportar los datos validados
`RF-12, RNF-12 · CU-11 · P-12 · servicios/ingesta, web · 3 pts · Opus`

Como técnico quiero descargar los datos validados en el formato de carga.

- [ ] Selecciona periodo, estaciones y variables; el archivo es CSV en UTF-8 con la estructura del formato configurado.
- [ ] Contiene solo datos de `v_medicion_valida`.
- [ ] Sin datos válidos en el periodo lo informa y no genera archivo (2a).
- [ ] La exportación queda en la auditoría.

### HU-51 · Vista pública del ICA y el pronóstico
`RF-13, RNF-14 · CU-12 · web, servicios/normativo, servicios/pronostico · 8 pts · Opus`

Como ciudadano quiero consultar la calidad del aire actual y el pronóstico sin iniciar sesión.

- [ ] Un mapa muestra cada estación con la categoría vigente del ICA en color y en texto.
- [ ] Muestra el pronóstico del día siguiente por estación con su categoría.
- [ ] Al elegir una estación muestra las últimas 48 horas y las recomendaciones de la categoría.
- [ ] Sin promedio representativo dice que no hay dato suficiente (2a).
- [ ] Las rutas públicas son de solo lectura y no exponen datos sospechosos ni personales.

---

## Sprint 6. Pruebas, usabilidad y despliegue

Entregable: informe de pruebas, resultados SUS, manuales y despliegue en la nube.

### HU-52 · Segunda fuente de datos por adaptador
`RNF-04 · tools o simulador · 3 pts · Opus`

Como responsable de la arquitectura quiero demostrar que la fuente de datos se puede sustituir.

- [ ] Un segundo adaptador (carga de un archivo CSV) envía mediciones con el mismo contrato.
- [ ] Ningún servicio cambia para aceptarlo.

### HU-53 · Despliegue en la nube endurecido y verificado
`RNF-08, RNF-17, RNF-20 · infra · 5 pts · Opus (ADR-0003)`

Como coordinador quiero usar el sistema desde internet de forma segura. El sistema ya está desplegado desde el Sprint 0; esta historia lo deja en estado de entrega.

- [ ] Todo el sistema se levanta en un equipo limpio con `infra/docker-compose.yml` y una sola orden; el resultado queda en `docs/pruebas/`.
- [ ] Los tres contenedores y la web están en línea en el proveedor de ADR-0003, definidos en `infra/render.yaml`, y se despliegan solos al integrar en `main` con CI en verde.
- [ ] Todo el tráfico externo va por HTTPS; HTTP redirige. La base de datos solo acepta conexiones con TLS (`sslmode=verify-full`).
- [ ] Cada servicio se conecta con su propio rol; ningún secreto está en el repositorio ni en las imágenes.
- [ ] `POST /v1/sesiones` limita los intentos por IP.
- [ ] Una prueba de humo programada recorre salud, inicio de sesión y una reproducción corta contra las URL públicas, y avisa si la base supera 700 MB.
- [ ] El manual técnico explica los límites del plan gratuito, cómo preparar una demostración y qué cambiaría en una operación real continua.

### HU-54 · Copia de seguridad diaria y restauración probada
`RNF-16 · infra, .github · 3 pts · Opus (ADR-0003)`

Como administrador quiero poder recuperar la base de datos.

- [ ] Un flujo programado genera cada día una copia con `pg_dump`, la cifra y la guarda 90 días.
- [ ] Un flujo semanal restaura la copia más reciente en un PostgreSQL limpio y comprueba tablas, disparador de `valor_crudo` y conteos.
- [ ] `docs/manuales/restauracion.md` describe la restauración manual, y una ejecución real queda documentada con su resultado.
- [ ] Si la copia o la restauración fallan, el flujo queda en rojo y GitHub avisa por correo.

### HU-55 · El tablero responde en menos de dos segundos
`RNF-10 · tests · 3 pts · Opus`

- [ ] Con un año de datos cargado, las consultas del tablero para 30 días responden en menos de dos segundos.
- [ ] El resultado queda en `docs/pruebas/`.

### HU-56 · Un dato queda validado y evaluado en menos de cinco minutos
`RNF-01 · tests · 2 pts · Opus`

- [ ] En una reproducción a velocidad 1 se mide la duración real desde la llegada del lote hasta su evaluación normativa.
- [ ] El resultado queda en `docs/pruebas/`.

### HU-57 · Pruebas de usabilidad
`RNF-07 · docs · 3 pts · Opus`

- [ ] Guion de tareas del técnico y cuestionario SUS aplicados a los participantes definidos en 3.3.
- [ ] Puntuación SUS promedio y métricas de las tareas reportadas; si es menor que 68, se registran los ajustes.

### HU-58 · Informe de pruebas por requerimiento
`RNF-19 · tests, docs · 3 pts · Opus`

- [ ] Tabla de casos de prueba aprobados por cada RF y RNF.
- [ ] Informe de cobertura de las reglas de validación y de la evaluación normativa, con 70 % o más.

### HU-59 · Manuales técnico y de usuario
`docs · 3 pts · Opus`

- [ ] Manual técnico: instalación, configuración, copias de seguridad y operación del simulador.
- [ ] Manual de usuario por rol.

---

## Interpretaciones que conviene confirmar con el documento

| Historia | El documento dice | Se asumió |
|---|---|---|
| HU-17 | La Figura 32 habla de reglas críticas y de advertencia sin decir cuáles son | Críticas: rango físico y mantenimiento. Advertencia: valor repetido, cambio brusco y comparación entre estaciones |
| HU-17 | No dice qué pasa con una medición sin valor | Queda `INVALIDO` |
| HU-21 | La Figura 17 define `DETECTADA` por mediciones marcadas, pero una ausencia no deja mediciones | Se detecta si la estación pasó a `SIN_TRANSMISION` |
| HU-36 | La Figura 8 solo describe el aumento de nivel | Una baja sin cese no cambia la declaratoria |
| HU-43 | `EVALUADO` si todas las horas tienen observación, `INCOMPLETO` si hay menos de 18; no cubre de 18 a 23 | `EVALUADO` con 18 o más |
| HU-27 | CU-04 da acceso al coordinador, pero `db/10` no le da el permiso `consultar_red` | Se agrega el permiso al rol `COORDINADOR` en `db/11` |

## Qué se recorta primero si la velocidad no alcanza

En este orden, y sin dejar ningún RF sin cubrir:

1. HU-26 (administrar usuarios en la web) pasa del Sprint 2 al 3; mientras tanto se usa la herramienta de `tools/`.
2. HU-44 muestra las métricas en tablas y deja las gráficas para el Sprint 6.
3. HU-36 (aumento de nivel) y HU-47 (reintentos) se reducen a su primer criterio.
4. HU-52 se demuestra con un guion de carga por CSV en `tools/`, sin interfaz.

No se recortan: HU-03, HU-13, HU-33, HU-37 ni las historias de verificación de RNF, que son las que sostienen la sustentación.
