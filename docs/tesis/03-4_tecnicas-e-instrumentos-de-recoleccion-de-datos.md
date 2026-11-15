<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

## 3.4 Técnicas e instrumentos de recolección de datos

### 3.4.1 Talleres de requisitos

Como no se pueden hacer talleres con el personal de la autoridad ambiental, la elicitación se apoya en el análisis documental y en sesiones de refinamiento con la asesora. El análisis documental cubre la Resolución 2254 de 2017, el Protocolo para el Monitoreo y Seguimiento de la Calidad del Aire, los informes de Corpoboyacá entre 2022 y 2025 y el perfil de calidad del conjunto de datos abiertos. Cada artículo o criterio relevante queda en una matriz de trazabilidad que lo vincula con uno o más requerimientos funcionales, como muestra la Tabla 13. Las sesiones de refinamiento se hacen al inicio de cada sprint y sirven para priorizar las historias de usuario y aclarar los criterios de aceptación.

**Tabla** **13.** *Matriz de trazabilidad entre fuentes y requerimientos funcionales*

|                                      |                                                                                                                                             |                     |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| **Fuente**                           | **Disposición o hallazgo**                                                                                                                  | **Requerimientos**  |
| Res. 2254 de 2017, art. 25           | Migrar al SISAIRE información actualizada y validada                                                                                        | RF-01, RF-12        |
| Res. 2254 de 2017, art. 24           | Elaborar informes mensuales, trimestrales y anuales                                                                                         | RF-11               |
| Res. 2254 de 2017, arts. 10, 11 y 12 | Evaluar niveles de prevención, alerta y emergencia con promedios de 24 horas y seguimiento horario                                          | RF-05, RF-06        |
| Res. 2254 de 2017, art. 11           | Declarar niveles de forma anticipada con un modelo de pronóstico calibrado y validado                                                       | RF-07, RF-08, RF-09 |
| Res. 2254 de 2017, art. 6, par. 2    | Informar a las autoridades de salud y de gestión del riesgo                                                                                 | RF-10               |
| Res. 2254 de 2017, arts. 18 a 22     | Publicar el índice de calidad del aire con su estrategia de comunicación                                                                    | RF-13               |
| Protocolo, validación de datos       | Validar de forma manual o con aplicativos mediante pruebas de límites, total de datos, relación entre parámetros y comparación entre sitios | RF-02, RF-03        |
| Protocolo, manejo de bases de datos  | Mantener una base con todas las mediciones y otra solo con datos válidos                                                                    | RF-04               |
| Protocolo, representatividad         | Exigir 75 % de datos para que un promedio sea válido                                                                                        | RF-05               |
| Ley 1581 de 2012                     | Tratar con seguridad los datos de usuarios y contactos                                                                                      | RF-14               |
| Informes de Corpoboyacá 2022 a 2025  | Ausencia de pronósticos y errores de procesamiento manual                                                                                   | RF-02, RF-08        |
| Perfil de los datos abiertos         | Registros duplicados, estación mal georreferenciada y rezago de publicación                                                                 | RF-01, RF-15        |
| Diseño de la verificación            | Validar el sistema sin acceso a la operación real de la red                                                                                 | RF-16               |

Fuente: Elaboración propia.

### 3.4.2 Entrevistas y encuestas

En lugar de entrevistas con el operador de la red, se aplica un instrumento de validación por juicio de expertos. Dos o tres profesionales con experiencia en ingeniería ambiental o en desarrollo de software revisan los requerimientos y una demostración del sistema. Después califican, en una escala de cinco puntos, la pertinencia, la claridad y la suficiencia de cada grupo de requerimientos, y tienen un espacio para dejar observaciones. Las calificaciones se resumen con la mediana por grupo, y los grupos con mediana inferior a cuatro se revisan antes del sprint siguiente.

### 3.4.3 Pruebas de usabilidad

Las pruebas de usabilidad usan tareas guionadas que reproducen escenarios del sistema, por ejemplo, revisar los datos de un sensor con valores repetidos durante seis horas o confirmar una propuesta de declaratoria. En cada tarea se registran el éxito, el tiempo y los errores. Al terminar, cada participante responde el cuestionario SUS (Brooke, 1996). El criterio de aceptación es una puntuación promedio igual o superior a 68.
