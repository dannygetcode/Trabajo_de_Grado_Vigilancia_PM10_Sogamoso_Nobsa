<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

### 3.2.4 Casos de uso extendidos

Esta sección desarrolla en formato extendido los tres casos de uso que concentran la lógica del sistema, que son la revisión de datos (CU-03) en la Tabla 10, la decisión sobre la declaratoria (CU-06) en la Tabla 11 y el pronóstico diario (CU-07) en la Tabla 12. La plantilla sigue la propuesta de Cockburn (2001), con actor principal, precondiciones, flujo básico, flujos alternos, postcondiciones y requerimientos asociados. Los otros doce casos usan la misma plantilla y están en el Anexo A.

**Tabla** **10.** *Caso de uso extendido CU-03 Revisar dato sospechoso*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Técnico del SVCA |
| Precondiciones | El técnico ha iniciado sesión. Existen mediciones con bandera SOSPECHOSO en la cola de revisión. |
| Flujo básico | 1. El técnico abre la cola de revisión.<br>2. El sistema lista los datos sospechosos con estación, hora, valor, regla que los marcó y contexto de las horas vecinas y de las otras estaciones.<br>3. El técnico selecciona un dato.<br>4. El técnico elige aprobar, corregir o invalidar.<br>5. El sistema solicita una justificación obligatoria.<br>6. El técnico registra la justificación y confirma.<br>7. El sistema actualiza el estado del dato, conserva el valor original y registra usuario, fecha y motivo.<br>8. El sistema recalcula los promedios afectados. |
| Flujos alternos | 2a. Si la cola está vacía, el sistema lo informa.<br>4a. Si elige corregir, el sistema solicita el nuevo valor y verifica que esté dentro del rango físico.<br>6a. Si la justificación está vacía, el sistema impide confirmar. |
| Postcondiciones | El dato queda como VALIDADO_MANUAL, CORREGIDO o INVALIDADO, con registro de auditoría. |
| Requerimientos asociados | RF-03, RF-04, RF-05 |

Fuente: Elaboración propia.

**Tabla** **11.** *Caso de uso extendido CU-06 Confirmar o descartar declaratoria*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Coordinador del SVCA |
| Actores secundarios | Entidad de salud o gestión del riesgo |
| Precondiciones | El proceso de evaluación normativa generó una propuesta de nivel por medición o por pronóstico. |
| Flujo básico | 1. El sistema notifica al coordinador la existencia de una propuesta.<br>2. El coordinador abre la propuesta.<br>3. El sistema muestra el nivel propuesto, la serie de promedios móviles de las últimas 48 horas, el porcentaje de tiempo en el rango, la cobertura de estaciones y, si aplica, el pronóstico que la originó.<br>4. El coordinador confirma la declaratoria y registra el soporte técnico.<br>5. El sistema cambia el estado a CONFIRMADA y genera la notificación a los contactos registrados. |
| Flujos alternos | 4a. El coordinador descarta la propuesta con justificación; el sistema la marca como DESCARTADA y no notifica.<br>3a. Si la cobertura es inferior al 50 % de las estaciones, el sistema indica que la declaratoria solo puede aplicarse a las estaciones individuales. |
| Postcondiciones | La decisión queda registrada con su soporte. Si fue confirmada, se envió la notificación. |
| Requerimientos asociados | RF-06, RF-07, RF-10 |

Fuente: Elaboración propia.

**Tabla** **12.** *Caso de uso extendido CU-07 Generar pronóstico diario*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Planificador |
| Precondiciones | Existe una versión del modelo registrada como activa. Hay datos validados de las horas previas. |
| Flujo básico | 1. El planificador dispara el proceso a la hora configurada según el reloj del sistema.<br>2. El sistema construye las variables de entrada usando solo datos anteriores al momento de emisión.<br>3. El sistema ejecuta el modelo para cada estación.<br>4. El sistema calcula el intervalo de predicción y la categoría del ICA.<br>5. El sistema almacena el pronóstico con la versión del modelo y el registro de ejecución.<br>6. Si el pronóstico supera el umbral configurado, el sistema genera una propuesta de declaratoria por pronóstico. |
| Flujos alternos | 2a. Si una estación no tiene datos suficientes, el sistema omite su pronóstico y registra el motivo.<br>3a. Si el modelo falla, el sistema registra el error y no publica pronóstico para ese día. |
| Postcondiciones | Los pronósticos quedan disponibles para el tablero, la vista pública y la comparación posterior con el valor observado. |
| Requerimientos asociados | RF-08, RF-09, RNF-02, RNF-06 |

Fuente: Elaboración propia.
