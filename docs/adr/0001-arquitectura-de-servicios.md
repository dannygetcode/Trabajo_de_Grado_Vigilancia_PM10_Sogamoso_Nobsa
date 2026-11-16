# ADR-0001: Arquitectura de servicios, unidades de despliegue y base de datos compartida

- Estado: Aceptado (reemplaza la versión anterior de este ADR, "Servicios con una base de datos compartida", y la amplía con el agrupamiento en unidades de despliegue)
- Fecha: 2026-11-15
- Sprint: 0
- Relacionado: 3.6.6, 3.6.7, 3.6.8, 3.6.9; RNF-04, RNF-08, RNF-09, RNF-15, RNF-16, RNF-18, RNF-20; ADR-0002, ADR-0003

## Contexto

La sección 3.6.6 divide el sistema en servicios con responsabilidad acotada (ingesta y validación, normativo, pronóstico, notificaciones e informes) más el simulador, el planificador y el servicio de reloj. La sección 3.6.7 los dibuja como contenedores en un servidor en la nube, con el simulador aparte y PostgreSQL gestionado. La sección 3.6.8 define un único modelo relacional de 24 tablas en el esquema `svca`.

Hay tres fuerzas que el documento no resuelve:

1. **Costo cero permanente.** Ningún proveedor ofrece gratis y sin fecha de vencimiento un servidor donde quepan siete contenedores siempre encendidos. Los planes gratuitos que sí son permanentes (ADR-0003) dan contenedores de 512 MB que se duermen tras 15 minutos sin tráfico entrante, sin disco, con una bolsa de 750 horas al mes compartida entre todos.
2. **El reloj virtual con barrera** (`docs/planes/reloj-virtual.md`). Cada hora virtual cuesta entre seis y diez llamadas entre reloj, planificador, ingesta y normativo. RNF-11 da 205 ms por hora. Si esas llamadas cruzan internet entre contenedores que pueden estar dormidos, la reproducción deja de ser viable y un arranque en frío de un minuto se confunde con una falla.
3. **El modelo relacional cruza los límites de los servicios** con llaves foráneas (`medicion.falla_id`, `revision.usuario_id`, `declaratoria` → `pronostico`, `notificacion` → `declaratoria`), y dos reglas viven en la base y no en el código: el disparador de `valor_crudo` (RF-04) y la columna calculada `promedio_movil.representativo`.

Además hay un solo desarrollador y el jurado evalúa la arquitectura: la solución tiene que ser operable por una persona y defendible frente a las Figuras 42 y 43.

## Decisión

### 1. Siete servicios lógicos, tres unidades de despliegue

Se separa **qué es un servicio** de **en qué proceso corre**. Un servicio es un paquete con sus capas (`domain/`, `application/`, `infrastructure/`, `api/`), su propia aplicación FastAPI, su contrato OpenAPI, su rol de base de datos y su configuración. En qué contenedor se ejecuta es una decisión de despliegue que se toma en un único lugar.

| Unidad de despliegue (imagen) | Servicios lógicos que contiene | Por qué va ahí |
|---|---|---|
| `nucleo` | reloj, planificador, ingesta y validación, normativo, notificaciones e informes | Son los que conversan en cada hora virtual. Juntos, sus llamadas no salen del proceso |
| `pronostico` | pronóstico | RNF-15 exige poder detenerlo sin afectar al resto. Además carga pandas y scikit-learn, que no caben con holgura junto a lo demás en 512 MB |
| `simulador` | simulador de estaciones | RNF-04 y 3.6.7: es una fuente externa que solo conoce la interfaz de recepción y habla por HTTPS, como lo haría una red real |

La interfaz web y la vista pública son archivos estáticos y no son un contenedor de aplicación (ADR-0003).

**La misma topología se usa en todas partes**: en `infra/docker-compose.yml`, en CI y en la nube. No hay una topología "de desarrollo" con siete contenedores y otra "de nube" con tres: mantener dos duplicaría las pruebas de integración de un solo autor y la que se demostraría al jurado no sería la que se probó.

### 2. Reglas que mantienen separados a los servicios dentro del núcleo

Agrupar en un proceso no puede degradar el diseño a un monolito con otro nombre. Estas reglas lo impiden y todas se verifican de forma automática:

1. **Un servicio no importa código de otro.** Solo puede importar `servicios/comun` (cliente del reloj, verificación de tokens, formato de errores; sin reglas de negocio). Se comprueba en CI con `import-linter`.
2. **Los servicios se hablan solo por sus contratos HTTP**, también dentro del núcleo. El cliente es el mismo (`httpx`); lo que cambia es el transporte: dentro del núcleo se usa el transporte ASGI en proceso (`httpx.ASGITransport`), que entrega la petición a la aplicación destino sin pasar por la red, y hacia `pronostico` y desde `simulador` se usa HTTPS. Las peticiones llevan el mismo token y pasan por la misma validación en ambos casos.
3. **`servicios/nucleo/` es solo la raíz de composición.** Monta cada aplicación bajo su prefijo (`/reloj`, `/ingesta`, `/normativo`, `/notificaciones`), arranca el bucle del planificador y decide el transporte de cada cliente a partir de la configuración. No contiene reglas de negocio ni rutas propias, salvo `/salud`.
4. **Cada servicio arranca también solo** (`uvicorn svca_ingesta.api:app`). Una prueba de CI lo hace para cada uno y compara su OpenAPI con `docs/api/`. Así, pasar un servicio a su propio contenedor es cambiar una URL de configuración y una entrada del compose, no reescribir código.
5. **Cada servicio conserva su rol de PostgreSQL y su propio grupo de conexiones**, aunque comparta proceso (decisión 4).
6. **El núcleo corre con un único worker.** El estado del reloj vive en memoria; dos workers serían dos relojes.

### 3. Cómo queda cada requisito de arquitectura

| Requisito | Cómo se cumple |
|---|---|
| 3.6.6: servicios con responsabilidad acotada y API con OpenAPI (RNF-09) | Siete aplicaciones FastAPI con contrato propio; reglas 1 a 4 |
| RNF-04: fuente sustituible | El simulador es otra imagen, en otra máquina, y solo usa `ingesta.yaml` y `reloj.yaml` |
| RNF-15: si el pronóstico falla, lo demás sigue | `pronostico` es el único servicio del que nadie depende para ingerir, validar o evaluar, y es una unidad aparte: la prueba "con el servicio detenido" se hace igual en el compose (`docker compose stop pronostico`) y en la nube (servicio suspendido) |
| RNF-08: contenedores en un proveedor de nube | Tres imágenes desplegadas como contenedores (ADR-0003) |
| RNF-20: un único archivo de orquestación | `infra/docker-compose.yml` levanta base de datos, migrador, núcleo, pronóstico, simulador, web y servidor de correo de pruebas |

### 4. Una base de datos compartida, un escritor por tabla

Se usa **una sola base PostgreSQL con el esquema `svca` compartido**, con tres reglas que sustituyen el aislamiento que daría una base por servicio:

1. **Un solo servicio escribe cada tabla.** Los demás pueden leerla, pero para modificarla llaman a la API del dueño (las flechas `recalcular`, `proponer` y `notificar` de la Figura 42).
2. **La propiedad se hace cumplir con roles de PostgreSQL**, no por convención: cada servicio se conecta con su rol y solo tiene `INSERT/UPDATE/DELETE` sobre sus tablas.
3. **El esquema tiene un único dueño: `db/`.** Ningún servicio crea ni altera tablas al arrancar. Los cambios posteriores a los scripts 01 a 10 son scripts numerados nuevos (`db/11_...`) que se anotan en `docs/ESTADO.md`. Los aplica una sola herramienta, `tools/db_aplicar.py`, igual en el compose, en CI y en la nube.

| Servicio (rol de BD) | Escribe | Lee además |
|---|---|---|
| ingesta (`svca_ingesta`) | `medicion`, `revision`, `estacion`, `variable`, `estacion_variable`, `periodo_mantenimiento`, `usuario`, `rol` | `falla_inyectada` (solo para validar la llave) |
| simulador (`svca_simulador`) | `escenario_simulacion`, `falla_inyectada` | `estacion`, `variable`, `estacion_variable`, `medicion` (estado de las mediciones alteradas) |
| normativo (`svca_normativo`) | `promedio_movil`, `parametro_normativo`, `evaluacion_normativa`, `evaluacion_promedio`, `declaratoria`, `declaratoria_estacion` | `v_medicion_valida`, `estacion`, `variable`, `pronostico`, `valor_pronosticado` |
| pronóstico (`svca_pronostico`) | `version_modelo`, `ejecucion_ciclo`, `pronostico`, `valor_pronosticado` | `v_medicion_valida`, `estacion`, `variable`, `parametro_normativo` |
| notificaciones (`svca_notificaciones`) | `contacto`, `notificacion`, `informe` | lo necesario para el informe y la vista pública (solo lectura) |
| reloj (`svca_reloj`) | nada | `escenario_simulacion` (recuperar el estado al arrancar) |
| todos | `registro_auditoria`: solo `INSERT` y `SELECT` | |

`registro_auditoria` no concede `UPDATE` ni `DELETE` a ningún rol de servicio, con lo que RNF-18 se verifica con una prueba de permisos. El planificador no se conecta a la base: solo llama APIs. La gestión de usuarios y el inicio de sesión se alojan en el servicio de ingesta (ADR-0002). Los roles se crean en `db/11_roles_servicios.sql` (HU-06); las contraseñas no van en el script: las fija `tools/db_aplicar.py` desde variables de entorno.

## Alternativas descartadas

**Un contenedor por servicio (literal de la Figura 43).** Es lo que dibuja el documento. En un plan gratuito significa siete servicios que se duermen por separado: cada llamada entre ellos puede encontrar al destino dormido y esperar hasta un minuto, las siete instancias despiertas agotan la bolsa mensual de horas en cuatro días y medio, y las llamadas de la barrera horaria cruzarían internet miles de veces por reproducción. Con un servidor propio sería viable, pero el único gratuito permanente (Oracle Always Free) exige tarjeta, recortó su cuota en 2026 y recupera instancias inactivas (ADR-0003). Se conserva como posibilidad: la regla 4 garantiza que se puede volver a este esquema sin tocar código.

**Monolito modular (una sola aplicación, módulos internos).** Es lo más barato de operar, pero pierde lo que el jurado evalúa: no habría contratos OpenAPI por servicio, RNF-15 no se podría probar "con el servicio detenido" y nada impediría que un módulo llamara funciones de otro. La decisión tomada obtiene el mismo costo de operación sin renunciar a esos límites.

**Dos topologías: siete contenedores en local y agrupados en la nube.** Parece lo mejor de los dos mundos, pero la que se desplegaría sería la menos probada. Se prefiere una sola.

**Una base de datos por servicio.** Rompe las llaves foráneas entre paquetes y obliga a reemplazarlas por eventos, copias locales y consistencia eventual. La trazabilidad falla → medición → revisión, base de la evaluación de las reglas (3.5.1), quedaría repartida en tres bases. Exige un intermediario de mensajes que el documento no contempla, complica RNF-16 (una copia coherente) y multiplica por cinco el consumo de un plan gratuito de base de datos. Para cinco estaciones y unas 70 000 mediciones al año no compra nada.

**Un esquema por servicio en la misma base.** Hace más visible la propiedad, pero obliga a reescribir los scripts 01 a 10, que son parte del documento (3.6.9) y ya están probados. Los roles dan la misma garantía sin tocar el esquema.

## Consecuencias

A favor:

- Cabe en planes gratuitos permanentes con tres contenedores, y la reproducción acelerada no depende de la red entre servicios.
- El modelo relacional del documento se implementa sin cambios; las consultas que cruzan paquetes (informe, vista pública, tablero) son un `JOIN`.
- Una sola copia de seguridad y un solo procedimiento de restauración (RNF-16).
- Los límites entre servicios no dependen de la disciplina: los comprueban `import-linter`, los roles de la base y la prueba de arranque individual.

En contra, y cómo se mitiga:

- **Se aparta de la Figura 43**, que muestra un contenedor por servicio. Hay que corregir la figura y el texto de 3.6.7 (`docs/correcciones_documento.md`) y explicarlo en la sustentación: los servicios siguen siendo siete; lo que se agrupa son procesos.
- **Una falla de memoria o un bloqueo en un servicio del núcleo tumba a los cinco.** Se acepta: RNF-15 solo exige aislamiento frente al pronóstico. El trabajo pesado del núcleo (PDF con WeasyPrint y matplotlib) se importa solo al generar el informe.
- **No hay escalado independiente.** Irrelevante para el volumen del caso de estudio.
- **Acoplamiento por esquema.** Un cambio de tabla puede afectar a varios servicios. Cada servicio accede a la base solo desde `infrastructure/`, las lecturas de tablas ajenas se concentran en `infrastructure/lecturas_externas.py` y, cuando una se repite, se convierte en vista en `db/`, como `v_medicion_valida`.
- **Punto único de falla en la base.** 3.6.7 ya prevé un servicio gestionado; con una base por servicio la caída de la de ingesta detendría igual la cadena.
- **`servicios/nucleo/` no está en la Tabla 19.** Se anota como desviación junto con `servicios/comun/` y `servicios/planificador/`.

## Cómo se verifica

- `import-linter` en CI: ningún paquete de servicio importa otro; `domain/` no importa nada externo.
- Prueba de arranque individual por servicio y comparación de su OpenAPI con `docs/api/`.
- Prueba de integración por servicio: con su rol de BD, escribir en una tabla ajena falla por permisos.
- Prueba de RNF-18: `UPDATE` y `DELETE` sobre `registro_auditoria` fallan con todos los roles de servicio.
- Prueba de RNF-15: con `pronostico` detenido, una reproducción de 48 horas completa ingesta, validación y evaluación, y el planificador registra el fallo de P-08 sin detener la hora.
