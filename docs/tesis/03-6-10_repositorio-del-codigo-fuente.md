<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

### 3.6.10 Repositorio del código fuente

El código fuente se aloja en un repositorio público de GitHub, disponible en https://github.com/dannygetcode/Trabajo\_de\_Grado\_Vigilancia\_PM10\_Sogamoso\_Nobsa. Cada sprint se integra en la rama principal mediante solicitudes de cambio, y los mensajes de confirmación hacen referencia a la historia de usuario correspondiente, de modo que el historial sirve como registro de los eventos de Scrum. La Tabla 19 presenta la estructura de carpetas. Los scripts de la base de datos y las fuentes de los diagramas de esta sección se publican en las carpetas db y docs, y los servicios se incorporan a medida que se cierra el sprint que los implementa.

**Tabla** **19.** *Estructura del repositorio (se encuentra en construcción a la entrega de este informe)*

|                           |                                                                                              |            |
| ------------------------- | -------------------------------------------------------------------------------------------- | ---------- |
| **Carpeta**               | **Contenido**                                                                                | **Sprint** |
| db/                       | Scripts SQL 01 a 10 del esquema y datos iniciales                                            | 0 y 1      |
| docs/                     | Documento del trabajo de grado, fuentes de los diagramas UML y manuales técnico y de usuario | Todos      |
| simulador/                | Simulador de estaciones, reloj virtual y escenarios de fallas                                | 1          |
| servicios/ingesta/        | Servicio de ingesta y validación con su cola de revisión                                     | 1 y 2      |
| servicios/normativo/      | Agregación, evaluación normativa y declaratorias                                             | 3          |
| servicios/pronostico/     | Entrenamiento con CRISP-DM, registro de versiones y pronóstico diario                        | 4          |
| servicios/notificaciones/ | Correos e informes en PDF                                                                    | 5          |
| web/                      | Interfaz web interna y vista pública                                                         | 2 a 5      |
| infra/                    | Archivos de contenedores y de orquestación                                                   | 6          |
| tests/                    | Pruebas automatizadas unitarias, de integración y de fuga temporal                           | Todos      |

Fuente: Elaboración propia.
