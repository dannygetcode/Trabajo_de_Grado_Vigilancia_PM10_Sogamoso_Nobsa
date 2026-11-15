<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

## 3.5 Técnicas de procesamiento y análisis de los datos

### 3.5.1 Análisis cualitativo y cuantitativo

El análisis cualitativo consiste en codificar los artículos normativos y los criterios del protocolo en categorías funcionales, y en consolidar las observaciones de los expertos y de los participantes de usabilidad. El análisis cuantitativo tiene cinco frentes. El primero es el perfil de los datos, con la completitud por estación, los huecos, los duplicados, los valores fuera de rango y las estaciones mal georreferenciadas. El segundo es la evaluación del modelo con partición temporal, que usa 2020 a 2022 para entrenamiento, 2023 para validación y calibración del intervalo y 2024 para prueba. Ahí se comparan el MAE y el RMSE frente a persistencia y climatología, se calculan la exhaustividad y la precisión sobre el umbral de 75 µg/m³ y se mide la cobertura real del intervalo de predicción. El tercero es la evaluación de las reglas de validación frente a fallas inyectadas de tipo y ubicación conocidos, medida con la precisión y la exhaustividad de la detección. El cuarto es la proporción de casos de prueba aprobados por requerimiento y la medición de los tiempos de procesamiento. El quinto es el cálculo de la puntuación SUS y de las métricas de las tareas.

Los días que superan 75 µg/m³ son pocos en el corredor, así que se espera una exhaustividad baja en la anticipación de excedencias. En la exploración preliminar con los datos de 2022 y 2023, la exhaustividad sobre el umbral de 50 µg/m³ fue cercana a 27 %. Por esa razón el resultado se reporta como limitación del modelo y la declaratoria por pronóstico siempre pasa por la decisión del coordinador, sin activarse de forma automática.

### 3.5.2 Lista de procesos

La Tabla 14 lista los procesos del sistema con su disparador y su resultado. Cada proceso tiene un diagrama de colaboración en la sección 3.6.4 y un diagrama de secuencia en la sección 3.6.5.

**Tabla** **14.** *Lista de procesos del sistema*

|            |                            |                                                |                                                                                     |
| ---------- | -------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Código** | **Proceso**                | **Disparador**                                 | **Resultado**                                                                       |
| P-01       | Reproducción de mediciones | Avance del reloj virtual                       | Lotes de mediciones enviados a la ingesta, con fallas inyectadas según el escenario |
| P-02       | Ingesta                    | Llegada de un lote                             | Mediciones almacenadas sin modificación en la base de datos cruda                   |
| P-03       | Validación automática      | Ingesta completada                             | Bandera VÁLIDO, SOSPECHOSO o INVÁLIDO para cada dato                                |
| P-04       | Detección de ausencia      | Cada hora                                      | Registro de horas sin dato y alerta de estación sin transmisión                     |
| P-05       | Revisión manual            | Acción del técnico                             | Dato aprobado, corregido o invalidado con auditoría                                 |
| P-06       | Agregación                 | Cada hora                                      | Promedios móviles de 24 horas y representatividad                                   |
| P-07       | Evaluación normativa       | Cada hora                                      | Propuesta de nivel según los artículos 11 y 12                                      |
| P-08       | Pronóstico                 | Diario a la hora configurada                   | Pronóstico por estación con intervalo y categoría del ICA                           |
| P-09       | Seguimiento del pronóstico | Llegada del dato observado                     | Error del pronóstico registrado                                                     |
| P-10       | Notificación               | Declaratoria confirmada o pronóstico de riesgo | Correo enviado a los contactos registrados                                          |
| P-11       | Informe mensual            | Solicitud del coordinador o fin de mes         | Informe en PDF con datos validados                                                  |
| P-12       | Exportación                | Solicitud del técnico                          | Archivo de datos validados en el formato de carga                                   |

Fuente: Elaboración propia.
