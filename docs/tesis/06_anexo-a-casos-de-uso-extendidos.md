<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

# Anexo A: Casos de uso extendidos

Este anexo completa los casos de uso extendidos de la sección 3.2.4. Cada caso usa la misma plantilla y se identifica con el código de la Tabla 9. Los doce casos se presentan entre la Tabla 20 y la Tabla 31.

**Tabla** **20.** *Caso de uso extendido CU-01 Enviar mediciones*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Simulador de estaciones |
| Precondiciones | Existe un escenario de simulación en ejecución y el simulador tiene una credencial de servicio válida. |
| Flujo básico | 1. El simulador consulta la hora del servicio de reloj.<br>2. El simulador lee del archivo histórico las mediciones de la última hora.<br>3. El simulador aplica las fallas activas del escenario.<br>4. El simulador envía el lote a la interfaz de recepción.<br>5. El sistema registra cada medición en estado CRUDO.<br>6. El sistema ejecuta la validación del lote (CU-02).<br>7. El sistema responde con el número de mediciones recibidas y duplicadas. |
| Flujos alternos | 4a. Si el lote no cumple el contrato, el sistema responde con los errores y no registra ninguna medición.<br>5a. Si una medición ya existe para la misma estación, variable y hora, el sistema la cuenta como duplicada y continúa. |
| Postcondiciones | Las mediciones del lote quedan registradas y validadas. |
| Requerimientos asociados | RF-01, RF-04, RF-16 |

Fuente: Elaboración propia.

**Tabla** **21.** *Caso de uso extendido CU-02 Validar mediciones*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Incluido en CU-01 |
| Precondiciones | Existen mediciones en estado CRUDO. |
| Flujo básico | 1. El sistema carga los rangos físicos, los periodos de mantenimiento y las horas vecinas de cada serie.<br>2. El sistema aplica las pruebas de rango físico, mantenimiento, valor repetido, cambio brusco y comparación entre estaciones.<br>3. El sistema asigna a cada medición la bandera VÁLIDO, SOSPECHOSO o INVÁLIDO y la regla aplicada.<br>4. El sistema envía a la cola de revisión las mediciones sospechosas.<br>5. El sistema solicita el recálculo de los promedios afectados. |
| Flujos alternos | 2a. Si la estación está en mantenimiento, la medición queda INVÁLIDO sin aplicar las demás reglas.<br>2b. Si no hay datos de otras estaciones a la misma hora, se omite la comparación entre estaciones y se registra la omisión. |
| Postcondiciones | Ninguna medición del lote queda en estado CRUDO. |
| Requerimientos asociados | RF-02, RF-04 |

Fuente: Elaboración propia.

**Tabla** **22.** *Caso de uso extendido CU-04 Consultar estado de la red*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Técnico del SVCA |
| Actores secundarios | Coordinador del SVCA |
| Precondiciones | El usuario inició sesión con rol de técnico o coordinador. |
| Flujo básico | 1. El usuario abre el tablero de la red.<br>2. El sistema muestra cada estación con su estado, la hora del último dato y la completitud del día y del mes.<br>3. El sistema muestra el número de datos pendientes de revisión.<br>4. El usuario selecciona una estación y un periodo.<br>5. El sistema grafica la serie con la bandera de cada dato. |
| Flujos alternos | 2a. Si una estación está SIN_TRANSMISION, el sistema la resalta y muestra desde cuándo no transmite.<br>4a. Si el periodo no tiene datos, el sistema lo informa. |
| Postcondiciones | El usuario conoce el estado de la red sin modificar datos. |
| Requerimientos asociados | RF-05, RF-15, RNF-03 |

Fuente: Elaboración propia.

**Tabla** **23.** *Caso de uso extendido CU-05 Evaluar nivel normativo*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Planificador |
| Actores secundarios | Coordinador del SVCA |
| Precondiciones | Existen promedios móviles calculados para la hora evaluada y un parámetro normativo vigente. |
| Flujo básico | 1. El planificador dispara la evaluación cada hora según el reloj del sistema.<br>2. El sistema obtiene los promedios representativos de cada estación.<br>3. El sistema compara los promedios con los umbrales de prevención, alerta y emergencia.<br>4. El sistema calcula la cobertura de estaciones y el porcentaje de tiempo en el rango.<br>5. El sistema guarda la evaluación normativa.<br>6. Si el nivel alcanza prevención y no hay declaratoria abierta, el sistema crea una propuesta y avisa al coordinador. |
| Flujos alternos | 2a. Si ninguna estación tiene un promedio representativo, el sistema registra la evaluación sin nivel propuesto.<br>6a. Si existe una declaratoria confirmada y las condiciones dejaron de cumplirse, el sistema la cierra. |
| Postcondiciones | La evaluación de la hora queda registrada y, si aplica, existe una propuesta de declaratoria. |
| Requerimientos asociados | RF-05, RF-06 |

Fuente: Elaboración propia.

**Tabla** **24.** *Caso de uso extendido CU-08 Consultar desempeño del pronóstico*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Coordinador del SVCA |
| Precondiciones | El coordinador inició sesión y existen pronósticos con valores observados. |
| Flujo básico | 1. El coordinador abre el tablero de desempeño.<br>2. El sistema muestra el MAE y el RMSE de la versión activa frente a persistencia y climatología.<br>3. El sistema muestra la exhaustividad y la precisión sobre el umbral de 75 µg/m³ y la cobertura del intervalo.<br>4. El coordinador selecciona una estación y un periodo.<br>5. El sistema grafica los valores pronosticados, el intervalo y los valores observados. |
| Flujos alternos | 2a. Si la versión activa aún no tiene pronósticos evaluados, el sistema muestra solo sus métricas de validación. |
| Postcondiciones | El coordinador conoce el desempeño del modelo para sustentar declaratorias por pronóstico. |
| Requerimientos asociados | RF-09, RNF-06 |

Fuente: Elaboración propia.

**Tabla** **25.** *Caso de uso extendido CU-09 Notificar a entidades*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Planificador |
| Actores secundarios | Entidad de salud o gestión del riesgo |
| Precondiciones | Existe una declaratoria confirmada o un pronóstico de riesgo, y hay contactos activos. |
| Flujo básico | 1. El sistema obtiene los contactos activos.<br>2. El sistema redacta el mensaje con el nivel, las estaciones, la vigencia y las recomendaciones del ICA.<br>3. El sistema crea una notificación por contacto.<br>4. El sistema envía cada notificación al servidor de correo.<br>5. El sistema registra la hora de envío. |
| Flujos alternos | 4a. Si el envío falla, el sistema reintenta hasta tres veces y después marca la notificación como FALLIDA y alerta al administrador.<br>1a. Si no hay contactos activos, el sistema alerta al administrador. |
| Postcondiciones | Cada contacto activo tiene una notificación con estado final registrado. |
| Requerimientos asociados | RF-10 |

Fuente: Elaboración propia.

**Tabla** **26.** *Caso de uso extendido CU-10 Generar informe mensual*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Coordinador del SVCA |
| Precondiciones | El coordinador inició sesión y el mes solicitado ya terminó. |
| Flujo básico | 1. El coordinador selecciona el mes.<br>2. El sistema consulta los datos validados, los promedios, las excedencias, la representatividad y las declaratorias del periodo.<br>3. El sistema genera el PDF con tablas y gráficas.<br>4. El sistema muestra la vista previa.<br>5. El coordinador aprueba el informe.<br>6. El sistema marca el informe como APROBADO y lo deja disponible para consulta. |
| Flujos alternos | 5a. El coordinador devuelve el informe con observaciones y el sistema lo marca como DEVUELTO.<br>2a. Si quedan datos pendientes de revisión en el periodo, el sistema lo advierte antes de generar. |
| Postcondiciones | El informe del mes queda generado y con su decisión registrada. |
| Requerimientos asociados | RF-11 |

Fuente: Elaboración propia.

**Tabla** **27.** *Caso de uso extendido CU-11 Exportar datos validados*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Técnico del SVCA |
| Precondiciones | El técnico inició sesión. |
| Flujo básico | 1. El técnico selecciona periodo, estaciones y variables.<br>2. El sistema consulta la vista de datos válidos.<br>3. El sistema genera el archivo en el formato de carga configurado.<br>4. El sistema registra la exportación en la auditoría.<br>5. El técnico descarga el archivo. |
| Flujos alternos | 2a. Si no hay datos válidos en el periodo, el sistema lo informa y no genera archivo. |
| Postcondiciones | El archivo exportado contiene solo datos habilitados. |
| Requerimientos asociados | RF-12, RNF-12 |

Fuente: Elaboración propia.

**Tabla** **28.** *Caso de uso extendido CU-12 Consultar ICA y pronóstico*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Ciudadano |
| Actores secundarios | Entidad de salud o gestión del riesgo |
| Precondiciones | La vista pública está disponible. No requiere sesión. |
| Flujo básico | 1. El ciudadano abre la vista pública.<br>2. El sistema muestra un mapa con cada estación y la categoría vigente del ICA en color y en texto.<br>3. El sistema muestra el pronóstico del día siguiente por estación con su categoría.<br>4. El ciudadano selecciona una estación.<br>5. El sistema muestra la serie de las últimas 48 horas y las recomendaciones de la categoría. |
| Flujos alternos | 2a. Si una estación no tiene un promedio representativo, el sistema muestra que no hay dato suficiente en lugar de una categoría. |
| Postcondiciones | El ciudadano consulta la información sin modificar nada. |
| Requerimientos asociados | RF-13, RNF-14 |

Fuente: Elaboración propia.

**Tabla** **29.** *Caso de uso extendido CU-13 Gestionar configuración*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Administrador |
| Precondiciones | El administrador inició sesión. |
| Flujo básico | 1. El administrador abre la configuración.<br>2. El administrador elige usuarios, estaciones, variables, parámetros normativos o contactos.<br>3. El sistema muestra la lista del elemento elegido.<br>4. El administrador crea, edita o desactiva un registro.<br>5. El sistema valida los datos y guarda el cambio.<br>6. El sistema registra el cambio en la auditoría. |
| Flujos alternos | 5a. Si los datos no son válidos, por ejemplo un umbral mínimo mayor que el máximo, el sistema indica el error.<br>4a. Si el administrador intenta desactivar su propia cuenta, el sistema lo impide. |
| Postcondiciones | La configuración queda actualizada sin cambios en el código. |
| Requerimientos asociados | RF-14, RF-15 |

Fuente: Elaboración propia.

**Tabla** **30.** *Caso de uso extendido CU-14 Configurar simulación*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Administrador |
| Actores secundarios | Simulador de estaciones |
| Precondiciones | El administrador inició sesión y el archivo histórico está cargado. |
| Flujo básico | 1. El administrador crea un escenario con nombre y periodo.<br>2. El administrador define la velocidad del reloj.<br>3. El administrador agrega fallas con tipo, estación, variable e intervalo.<br>4. El sistema valida que las fallas estén dentro del periodo.<br>5. El sistema guarda el escenario como CONFIGURADO.<br>6. El administrador inicia el escenario y el simulador comienza a enviar lotes. |
| Flujos alternos | 4a. Si una falla queda fuera del periodo, el sistema lo indica y no guarda.<br>6a. El administrador puede pausar, reanudar o detener el escenario en ejecución. |
| Postcondiciones | El escenario queda listo o en ejecución con sus fallas programadas. |
| Requerimientos asociados | RF-16 |

Fuente: Elaboración propia.

**Tabla** **31.** *Caso de uso extendido CU-15 Iniciar sesión*

| **Elemento** | **Descripción** |
|---|---|
| Actor principal | Usuario autenticado |
| Precondiciones | El usuario tiene una cuenta ACTIVA. |
| Flujo básico | 1. El usuario ingresa correo y contraseña.<br>2. El sistema compara la contraseña con su resumen almacenado.<br>3. El sistema reinicia el contador de intentos fallidos.<br>4. El sistema emite un token de sesión con los permisos del rol.<br>5. El sistema registra el acceso en la auditoría.<br>6. El sistema muestra el menú correspondiente al rol. |
| Flujos alternos | 2a. Si la contraseña no coincide, el sistema suma un intento fallido y muestra un mensaje genérico.<br>2b. Al quinto intento fallido, el sistema bloquea la cuenta.<br>1a. Si la cuenta está BLOQUEADA o INACTIVA, el sistema niega el acceso. |
| Postcondiciones | El usuario queda autenticado con los permisos de su rol o el intento queda registrado. |
| Requerimientos asociados | RF-14, RNF-05, RNF-17 |

Fuente: Elaboración propia.
