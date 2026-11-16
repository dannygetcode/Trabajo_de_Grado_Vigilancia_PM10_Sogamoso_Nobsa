# Correcciones pendientes en el documento (Word)

Lista viva de lo que hay que cambiar en `docs/archivos/Trabajo_de_Grado_Vigilancia_PM10_Sogamoso_Nobsa.docx` para que coincida con las decisiones de diseño. Se aplican juntas al cierre del Sprint 0 y después se regenera `docs/tesis/` con `tools/docx_a_conocimiento.py`.

Prioridad: **A** contradice una decisión tomada y el jurado lo vería; **B** vacío o ambigüedad que el código ya resolvió; **C** forma.

## Arquitectura y despliegue (ADR-0001 y ADR-0003)

| N.º | Dónde | Qué cambia | Por qué | Prio. |
|---|---|---|---|---|
| 1 | 3.6.7, párrafo único | Reemplazar "En ese servidor corren en contenedores la interfaz web, la vista pública, los cuatro servicios de la Figura 42, el planificador y el servicio de reloj" por: los servicios se empaquetan en tres contenedores (núcleo: reloj, planificador, ingesta y validación, normativo, notificaciones e informes; pronóstico; simulador) y la interfaz web y la vista pública se publican como sitio estático | Ningún plan gratuito permanente aloja siete contenedores siempre encendidos. Los servicios siguen siendo los de 3.6.6; lo que se agrupa son procesos (ADR-0001) | A |
| 2 | Figura 43 | Redibujar los nodos: navegador; sitio estático; plataforma de contenedores con tres nodos de ejecución (`nucleo`, `pronostico`, `simulador`); PostgreSQL gestionado; servicio de correo; repositorio de modelos; integración continua (copias de seguridad). Conexiones HTTPS y SQL con TLS. El diagrama de referencia está en ADR-0003, "Topología" | La figura actual muestra un servidor único con un contenedor por servicio | A |
| 3 | 3.6.7 | Añadir una frase: el despliegue usa planes gratuitos permanentes; los contenedores se suspenden sin tráfico y se reactivan con la primera petición, por lo que el entorno en la nube es de demostración y los requisitos de desempeño (RNF-01, RNF-10, RNF-11) se verifican en el entorno de referencia local | Evita que el jurado mida tiempos sobre un contenedor recién despertado y lo tome por incumplimiento | A |
| 4 | 3.6.7, frase del correo | "Durante las pruebas, el servicio de notificaciones envía los correos por SMTP a un servidor de correo de pruebas" → precisar: en el entorno local, por SMTP a un servidor de pruebas que los captura; en la nube, por la interfaz HTTPS de un servicio de correo, con todos los mensajes redirigidos a un único buzón de prueba | El plan gratuito bloquea los puertos SMTP de salida. La garantía (no escribir a las entidades reales) se conserva | A |
| 5 | 3.6.6, último párrafo | Añadir: cada servicio conserva su propia interfaz OpenAPI y su propio rol de base de datos aunque varios se ejecuten en un mismo contenedor; la comunicación entre servicios se hace siempre por esas interfaces | Deja escrito en el documento el criterio que separa "servicio" de "contenedor" | A |
| 6 | Figura 42 | (a) Agregar las interfaces que faltan: sesiones y administración de usuarios y red (CU-13, CU-15) en ingesta; control de la simulación (CU-14) en el simulador. (b) Conectar el simulador a PostgreSQL, porque escribe `escenario_simulacion` y `falla_inyectada` (Figura 30). (c) Opcional: un marco punteado "núcleo" alrededor de reloj, planificador, ingesta, normativo y notificaciones | La figura no dibuja interfaz para tres casos de uso y contradice a la Figura 30 | B |
| 7 | Tabla 16, RNF-16, columna Verificación | "Restauración en un entorno de prueba" → "Restauración automatizada semanal en un entorno de prueba" | La verificación pasa de un acto único a uno repetido y con registro (ADR-0003) | C |
| 8 | Tabla 16, RNF-01, RNF-10 y RNF-11, columna Verificación | Añadir "en el entorno de referencia" | Ver corrección 3 | B |
| 9 | 3.6.7 o 3.6.10 | Mencionar que el repositorio de modelos es el almacén de versiones publicadas del repositorio de código (GitHub Releases) y que el servicio verifica el resumen SHA-256 del artefacto antes de cargarlo | 3.6.6 nombra un "repositorio de modelos" sin decir dónde vive; los contenedores gratuitos no tienen disco | B |

## Repositorio y base de datos

| N.º | Dónde | Qué cambia | Por qué | Prio. |
|---|---|---|---|---|
| 10 | Tabla 19 | Agregar filas: `servicios/comun/` (cliente del reloj, verificación de tokens, errores; Sprint 1), `servicios/nucleo/` (composición de los servicios del contenedor principal; Sprint 1), `servicios/planificador/` (Sprint 2), `tools/` (herramientas de datos, base y llaves; todos), `.github/` (integración continua, copias de seguridad; todos) | Carpetas que el diseño necesita y la tabla no lista | A |
| 11 | Tabla 19, fila `db/` | "Scripts SQL 01 a 10" → "Scripts SQL 01 a 12"; sprint "0, 1 y 5" | `db/11_roles_servicios.sql` (roles de PostgreSQL por servicio, rol `SIMULADOR`, permiso `consultar_red` al coordinador) y `db/12` (tabla `informe_archivo`) | A |
| 12 | Tabla 19, fila `infra/` | Sprint "6" → "0 a 6" | El despliegue empieza en el Sprint 0 (ADR-0003) | B |
| 13 | Tabla 19, fila `simulador/` | Aclarar que contiene dos paquetes: `reloj/` (se ejecuta en el núcleo) y `estaciones/` (contenedor propio) | El reloj debe existir sin el simulador (RNF-04) | B |
| 14 | 3.6.9 | Mencionar los scripts 11 y 12 y que los aplica una única herramienta en todos los entornos | Ídem 11 | A |
| 15 | 3.6.8, texto y Tabla 18; Figura 46 | 24 tablas → 25: agregar `informe_archivo` (contenido del PDF) relacionada con `informe` | Sin disco persistente, el PDF del informe mensual se guarda en la base (ADR-0003). Se aplica en el Sprint 5; si para entonces hubiera almacenamiento gratuito de archivos, se revisa | A |
| 16 | 3.6.8 o 3.6.9 | Añadir un párrafo: cada servicio se conecta con un rol propio de PostgreSQL que solo puede escribir sus tablas; ningún rol puede modificar ni borrar `registro_auditoria` | Es la forma en que se verifica RNF-18 y la regla de un escritor por tabla (ADR-0001) | B |
| 17 | `db/10` (Anexo o 3.6.9) y CU-04 | Dar el permiso `consultar_red` al rol `COORDINADOR` | CU-04 le da acceso al estado de la red y los datos iniciales no | B |

## Vacíos que el backlog ya resolvió (interpretaciones)

| N.º | Dónde | Qué cambia | Por qué | Prio. |
|---|---|---|---|---|
| 18 | Figura 32 y texto de P-03 | Decir cuáles reglas son críticas (rango físico, mantenimiento: invalidan) y cuáles de advertencia (valor repetido, cambio brusco, comparación entre estaciones: marcan sospechoso) | La figura distingue los dos tipos sin asignarlos (HU-17, HU-18) | B |
| 19 | CU-02 o P-03 | Una medición sin valor queda `INVALIDO` | No está definido (HU-17) | B |
| 20 | Figura 17 | Una falla de ausencia de dato queda `DETECTADA` si la estación pasó a `SIN_TRANSMISION` durante su intervalo | La figura define la detección por mediciones marcadas y una ausencia no deja mediciones (HU-21) | B |
| 21 | Figura 10 | `EVALUADO` con 18 o más horas observadas; `INCOMPLETO` con menos de 18 | La figura no cubre de 18 a 23 horas (HU-43) | B |
| 22 | Figura 8 | Una baja de nivel sin cese de condiciones no modifica la declaratoria | Solo se describe el aumento (HU-36) | B |
| 23 | 3.6.6, frase del reloj | Añadir: en reproducción acelerada el reloj no avanza a la hora siguiente hasta que los procesos de la hora actual confirman que terminaron, lo que hace repetibles los escenarios; el vencimiento de las sesiones usa la hora real | La barrera horaria y la excepción de seguridad son decisiones de diseño que sostienen la evaluación de 3.5.1 | B |
| 24 | CU-01 o RF-01 | La ingesta rechaza mediciones con fecha posterior al reloj y valores con más de tres decimales | Consecuencias de RNF-02 y de RF-04 (no redondear el dato crudo) | C |

## Forma y coherencia

| N.º | Dónde | Qué cambia | Por qué | Prio. |
|---|---|---|---|---|
| 25 | Numeración de capítulos | El documento salta del Capítulo III al V | Falta el Capítulo IV o hay que renumerar | A |
| 26 | Tabla 5 y 3.2.1 | Aclarar que son un sprint de preparación (0) y seis de construcción; en el Sprint 0, añadir al entregable "decisiones de arquitectura registradas y esqueleto desplegado"; en el Sprint 6, "despliegue en la nube" → "despliegue verificado y endurecido" | El despliegue empieza en el Sprint 0 | B |
| 27 | 3.2.1 | Mencionar que las decisiones de arquitectura se registran como ADR en `docs/adr/` | Artefacto que el jurado puede revisar y que el texto no menciona | C |
| 28 | `README.md` del repositorio (no es el Word) | Está desactualizado: habla de datos 2022 a 2024, PostGIS, carpetas `backend/` y `frontend/` y un diagrama que ya no corresponde | Lo primero que abre el jurado en el repositorio contradice al documento. **Hecho en S0-2.** | — |

## Qué no cambia

Los 16 RF, los 20 RNF, los casos de uso, los diagramas de clases, estados, colaboración y secuencia, el modelo relacional de las 24 tablas originales y los scripts 01 a 10 quedan como están. Ningún requisito se elimina ni se relaja; las correcciones 3 y 8 precisan dónde se mide, no qué se exige.
