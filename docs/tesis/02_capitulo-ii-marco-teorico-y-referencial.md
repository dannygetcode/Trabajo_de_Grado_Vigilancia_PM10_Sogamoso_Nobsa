<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

# Capítulo II: Marco teórico y Referencial

Este capítulo presenta los referentes que sustentan el diseño del sistema. La sección 2.1 revisa trabajos de grado y estudios sobre software para calidad del aire, validación de datos de redes de monitoreo y pronóstico de material particulado. La sección 2.2 expone los fundamentos teóricos de calidad del aire, calidad del dato, pronóstico y arquitectura de software. La sección 2.3 describe el contexto institucional de la red de monitoreo del corredor. La sección 2.4 define las categorías de análisis y la sección 2.5 resume el marco legal aplicable.

## 2.1 Antecedentes de la Investigación

Los antecedentes se dividen en tres grupos, que son los sistemas de software para gestionar datos de calidad del aire, los procedimientos para validar datos de redes de monitoreo y los trabajos de modelación o pronóstico de material particulado.

En la primera línea, Bravo Rivera (2012) desarrolló en la Universidad Industrial de Santander un software para depurar y clasificar los datos de gases contaminantes que registran las estaciones de la autoridad ambiental de Bucaramanga. El documento de Bravo Rivera incluye veintiún casos de uso, el diagrama de clases y el diccionario de datos, y es el antecedente más cercano al módulo de validación del presente proyecto. Pérez López y Claro Pérez (2023) construyeron, también en la Universidad Industrial de Santander, un sistema de información basado en internet de las cosas para medir la calidad del aire a lo largo de rutas de transporte público. Su documento presenta los requerimientos funcionales y no funcionales, los diagramas de casos de uso, clases y actividades, la arquitectura y las pruebas funcionales, y publica el código del tablero y del prototipo. Para este trabajo sirve como referencia de la documentación. Su fuente de datos, en cambio, depende de sensores propios que aquí no se emplean.

En la segunda línea, Correa Builes y Morales Rodríguez (2020) describieron cómo la Universidad Distrital maneja la información de su sistema de vigilancia. El procedimiento valida los datos en tres niveles (dato crudo, validación en campo y validación en la estación central), usa banderas de validez y aplica el criterio de 75 % de completitud. Guzmán Bernal (2005) propuso un procedimiento de validación para una red de diez estaciones en Chile, con bases de datos separadas para los datos crudos, los identificados y los filtrados, y con límites de deriva de calibración. Los dos trabajos aportan reglas que el presente sistema automatiza, y ninguno de los dos las implementa en una herramienta de software integrada.

En la tercera línea, Uribe Barón y Suárez Araque (2009) aplicaron el modelo de dispersión AERMOD en el Valle de Sogamoso, a partir de un inventario de emisiones, para evaluar escenarios de reducción de PM10 con fines de planificación. Los autores reportaron un error bajo en los promedios anuales y un error considerable en los diarios. Gil Serrano y Tobo Paipilla (2022) analizaron con herramientas de sistemas de información geográfica la variación temporal y espacial del PM10 y el PM2.5 en Nobsa, Corrales y Sogamoso. Camelo Valera (2024) comparó modelos estadísticos y de aprendizaje automático para estimar PM2.5 en Medellín, y usó predicción conformal para cuantificar la incertidumbre. Su diseño tiene particiones explícitas de entrenamiento, validación y prueba, y compara contra líneas base. Ariza y Sierra (2025) integraron sensores de bajo costo con modelos de memoria de largo y corto plazo para pronosticar la calidad del aire en tres puntos de Bogotá. La Tabla 1 resume los antecedentes y su aporte.

**Tabla** **1.** *Síntesis de antecedentes*

|                                          |                            |                                                               |                                                                                |
| ---------------------------------------- | -------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Autor y año**                          | **Ámbito**                 | **Enfoque**                                                   | **Aporte al presente trabajo**                                                 |
| Bravo Rivera (2012)                      | Bucaramanga, Colombia      | Software de depuración y clasificación de datos de estaciones | Antecedente directo del módulo de validación y de su análisis con casos de uso |
| Pérez López y Claro Pérez (2023)         | Bucaramanga, Colombia      | Sistema de información IoT con tablero web                    | Estructura de documentación, requerimientos, UML y pruebas                     |
| Correa Builes y Morales Rodríguez (2020) | Bogotá, Colombia           | Procedimiento de manejo y validación de datos de un SVCA      | Niveles de validación, banderas y criterio de completitud                      |
| Guzmán Bernal (2005)                     | Valle del Huasco, Chile    | Procedimiento de validación de datos de gases                 | Separación entre datos crudos y datos validados                                |
| Uribe Barón y Suárez Araque (2009)       | Valle de Sogamoso          | Modelo de dispersión AERMOD para planificación                | Diferencia entre modelación de escenarios y pronóstico operativo               |
| Gil Serrano y Tobo Paipilla (2022)       | Nobsa, Corrales y Sogamoso | Análisis temporal y espacial de PM10 y PM2.5                  | Antecedente local sobre el comportamiento del material particulado             |
| Camelo Valera (2024)                     | Medellín, Colombia         | Comparación de modelos y predicción conformal para PM2.5      | Protocolo de evaluación con líneas base y tratamiento de la incertidumbre      |
| Ariza y Sierra (2025)                    | Bogotá, Colombia           | Sensores de bajo costo y redes LSTM                           | Antecedente nacional de pronóstico de calidad del aire                         |

Fuente: Elaboración propia a partir de las fuentes citadas.

En el ámbito operativo ya funcionan sistemas consolidados, como el Sistema de Alerta Temprana de Medellín y el Valle de Aburrá (SIATA), que publican mediciones y pronósticos, y plataformas de datos abiertos como OpenAQ y de carácter comercial como IQAir. Estas experiencias vienen de ciudades con más estaciones y más recursos, y ninguna resuelve el procesamiento normativo de una red regional como la del corredor. La revisión no encontró trabajos que reúnan en un solo sistema la validación de los datos, la evaluación de los artículos 11 y 12 de la Resolución 2254 de 2017 y el pronóstico a 24 horas para una autoridad ambiental regional.

## 2.2 Bases o fundamentos teóricos

### 2.2.1 Material particulado y norma de calidad del aire

El PM10 reúne las partículas suspendidas con diámetro aerodinámico igual o inferior a 10 micrómetros, que pueden ingresar a las vías respiratorias. La Organización Mundial de la Salud recomienda como guía un promedio de 24 horas de 45 µg/m³ y un promedio anual de 15 µg/m³ (World Health Organization, 2021). En Colombia, la Resolución 2254 de 2017 fija para el PM10 un nivel máximo permisible de 75 µg/m³ en 24 horas y de 50 µg/m³ anual (MADS, 2017). La misma resolución establece, a partir de promedios de 24 horas, los rangos para declarar los niveles de prevención (155 a 254 µg/m³), alerta (255 a 354 µg/m³) y emergencia (355 µg/m³ o más) (Ministerio de ambiente y desarrollo sostenible, 2017).

La misma resolución define el índice de calidad del aire (ICA) como un valor adimensional que relaciona las concentraciones con un código de colores y con los efectos generales sobre la salud. El índice tiene seis categorías, que van de buena a peligrosa, y sirve para reportar el estado actual de la calidad del aire y también para comunicar pronósticos (Ministerio de ambiente y desarrollo sostenible, 2017).

### 2.2.2 Sistemas de vigilancia y calidad del dato

Un sistema de vigilancia de la calidad del aire (SVCA) reúne estaciones de medición, procedimientos de operación y procesos de análisis, validación y reporte. El protocolo nacional, adoptado por la Resolución 650 de 2010, distingue tres niveles de validación, que son la validación en campo, la automática que hace el equipo y la que se hace en la estación central. Además, recomienda marcar los datos con banderas que identifiquen el problema, conservar los datos invalidados y mantener dos bases, una con todas las mediciones y otra solo con los datos válidos. Entre los criterios de revisión menciona los datos fuera de intervalo o negativos, los cambios repentinos, la comparación con otros sitios y las condiciones meteorológicas (Ministerio de Ambiente, 2010b). La representatividad temporal exige una cobertura mínima de 75 % de los datos posibles para que un promedio sea válido, criterio que Corpoboyacá aplica en sus informes anuales (Corporación Autónoma Regional de Boyacá, 2025).

### 2.2.3 Pronóstico de series de tiempo y líneas base

Un pronóstico de corto plazo estima el valor futuro de una variable a partir de su historia y de otras variables relacionadas. Hyndman y Athanasopoulos (2021) establecen que todo modelo debe compararse con métodos de referencia simples. Uno es el pronóstico ingenuo o de persistencia, que asigna al futuro el último valor observado. El otro es el pronóstico estacional o climatológico, que usa el promedio histórico para el mismo periodo. Un modelo que no supera estas referencias no aporta valor operativo. La evaluación debe respetar el orden temporal de los datos, de modo que el modelo nunca use información posterior al momento del pronóstico.

### 2.2.4 Potenciación del gradiente

La potenciación del gradiente construye un modelo aditivo de árboles de decisión. Cada árbol corrige los residuos del conjunto anterior siguiendo la dirección del gradiente de la función de pérdida (Friedman, 2001). La biblioteca scikit-learn (Pedregosa et al., 2011) incluye una implementación basada en histogramas que, antes del entrenamiento, agrupa los valores de cada variable en un máximo de 255 intervalos. Eso la hace mucho más rápida que la versión clásica en conjuntos de más de 10.000 registros, y además admite valores faltantes sin necesidad de imputarlos (scikit-learn developers, s. f.). Esas dos propiedades la hacen adecuada para series ambientales horarias con huecos frecuentes.

### 2.2.5 Métricas de evaluación

El error absoluto medio (MAE) y la raíz del error cuadrático medio (RMSE) miden el error del pronóstico de concentración en las mismas unidades de la variable. Cuando el pronóstico sirve para anticipar la superación de un umbral, el problema pasa a ser de clasificación con clases desbalanceadas, porque los episodios son escasos. En ese caso la exhaustividad (recall) y la precisión informan más que la exactitud, y la curva de precisión y exhaustividad es preferible a la curva ROC (Saito & Rehmsmeier, 2015).

### 2.2.6 Intervalos de predicción

Un pronóstico puntual no informa cuánto puede equivocarse. Un intervalo de predicción acompaña el valor estimado con un rango que debe contener el valor observado con una probabilidad fijada de antemano, por ejemplo 90 %. La predicción conformal construye ese rango sin suponer una distribución para los errores. En su versión dividida, el modelo se entrena con un conjunto de datos, se calculan los residuos absolutos sobre un conjunto de calibración distinto y un cuantil de esos residuos fija el ancho del intervalo (Angelopoulos y Bates, 2023). La garantía de cobertura supone datos intercambiables, una condición que las series de tiempo no cumplen del todo, así que la cobertura real se verifica sobre el periodo de prueba. Camelo Valera (2024) aplicó este enfoque al PM2.5 en Medellín. Otra opción es estimar los cuantiles directamente con la pérdida pinball, que la implementación de scikit-learn también admite (scikit-learn developers, s. f.).

### 2.2.7 Arquitectura de software

La arquitectura de software define los elementos de un sistema, sus relaciones y las propiedades que se derivan de ellas, y se evalúa por su capacidad para satisfacer atributos de calidad como la modificabilidad, el desempeño y la seguridad (Bass et al., 2021). La arquitectura de puertos y adaptadores, también llamada hexagonal, aísla la lógica de la aplicación de los mecanismos externos mediante interfaces, y así una fuente de datos puede reemplazarse por otra sin modificar el núcleo (Cockburn, 2005). En este proyecto, ese patrón permite que el simulador de estaciones y una futura conexión real compartan el mismo contrato de ingesta. Los servicios son independientes, cada uno con una responsabilidad acotada y desplegable por separado, como en el enfoque de microservicios que describe Newman (2021). El cliente se comunica con los servicios según el estilo arquitectónico REST (Fielding, 2000).

Los datos se almacenan en una base de datos relacional, que organiza la información en relaciones con claves que garantizan su integridad (Codd, 1970). Cada servicio se empaqueta en un contenedor, una unidad que incluye la aplicación con sus dependencias y se ejecuta igual en desarrollo, pruebas y producción (Merkel, 2014). Las interfaces de programación se describen con la especificación OpenAPI, un formato estándar para declarar las operaciones, los parámetros y las respuestas de cada servicio (OpenAPI Initiative, 2021).

### 2.2.8 Simulación con reloj virtual

La reproducción de datos históricos consiste en emitir los registros almacenados en el orden y con la cadencia con que fueron medidos, como si llegaran en tiempo real. Fujimoto (2000) distingue entre el tiempo de la simulación y el tiempo del reloj de pared, y describe la ejecución en tiempo real escalado, en la que el tiempo simulado avanza como un múltiplo del tiempo real. Para aplicar esa idea, todos los componentes toman la hora de un servicio de reloj común, que en modo de demostración avanza de forma acelerada. Con este mecanismo se pueden ejecutar meses de operación en minutos, repetir escenarios y comprobar que el pronóstico solo utiliza datos anteriores a su emisión.

### 2.2.9 Metodologías y modelado

Scrum es un marco de trabajo ágil que organiza el desarrollo en iteraciones de duración fija, llamadas sprints, y define sus roles, eventos y artefactos (Schwaber & Sutherland, 2020). Para el componente de aprendizaje automático se adopta el proceso CRISP-DM, que divide el trabajo en seis fases, que son comprensión del negocio, comprensión de los datos, preparación, modelado, evaluación y despliegue (Wirth & Hipp, 2000). El sistema se modela con UML, un lenguaje estándar para especificar, visualizar y documentar sistemas de software (Booch et al., 2005), y los casos de uso se redactan según la propuesta de Cockburn (2001).

### 2.2.10 Calidad del producto y usabilidad

La norma ISO/IEC 25010:2023 define el modelo de calidad del producto de software con características como la adecuación funcional, la eficiencia de desempeño, la compatibilidad, la capacidad de interacción, la fiabilidad, la seguridad, la mantenibilidad y la flexibilidad (International Organization for Standardization, 2023). Los requerimientos no funcionales de este sistema se clasifican según ese modelo. La usabilidad se mide con la escala SUS, un cuestionario de diez ítems cuya puntuación va de 0 a 100 (Brooke, 1996).

## 2.3 Antecedentes de la empresa o contexto

Corpoboyacá es la autoridad ambiental con jurisdicción en el corredor y opera el sistema de vigilancia de la calidad del aire con estaciones automáticas permanentes. Según su informe anual de 2024, la red tenía ocho estaciones en Sogamoso, Nobsa, Tunja y Paipa. La corporación clasifica su monitoreo como de tipo indicativo, orientado a determinar las concentraciones más altas, las concentraciones de fondo y el impacto de fuentes significativas (Corporación Autónoma Regional de Boyacá, 2025). La Tabla 2 presenta las estaciones del corredor incluidas en el caso de estudio.

**Tabla** **2.** *Estaciones de la red de monitoreo incluidas en el caso de estudio*

|                    |               |                                   |                          |                                 |                             |
| ------------------ | ------------- | --------------------------------- | ------------------------ | ------------------------------- | --------------------------- |
| **Estación**       | **Municipio** | **Coordenadas**                   | **Altitud (m s. n. m.)** | **Representatividad PM10 2024** | **PM2.5 en datos abiertos** |
| UPTC               | Sogamoso      | 5° 42' 16,5" N; 72° 56' 34,0" O   | 2.523                    | 86,2 %                          | No                          |
| El Recreo          | Sogamoso      | 5° 43' 34,58" N; 72° 55' 15,30" O | 2.483                    | 82,7 %                          | Sí                          |
| SENA               | Sogamoso      | 5° 45' 25,6" N; 72° 54' 30,7" O   | 2.477                    | 99,7 %                          | No                          |
| Nazaret            | Nobsa         | 5° 45' 58,02" N; 72° 53' 49,23" O | 2.479                    | 92,8 %                          | Sí                          |
| Bomberos (Móvil 1) | Nobsa         | 5° 46' 15,34" N; 72° 56' 16,70" O | 2.499                    | 88,5 %                          | Sí                          |

Fuente: Elaboración propia a partir de Corporación Autónoma Regional de Boyacá (2025) e Instituto de Hidrología, Meteorología y Estudios Ambientales (2026).

La gestión de la calidad del aire en la región se coordina en la Mesa Regional de Calidad del Aire del Corredor Industrial de Boyacá. Corpoboyacá ejerce la secretaría técnica, y participan el Ministerio de Ambiente, el Ministerio de Salud, el IDEAM, la Autoridad Nacional de Licencias Ambientales y las secretarías de salud, ambiente y tránsito de Sogamoso, Nobsa y Duitama (Ministerio de Ambiente y Desarrollo Sostenible, 2022). Esta composición identifica a los destinatarios de las notificaciones que prevé el sistema.

Los datos de la red se publican en el conjunto Calidad del aire en Colombia, del portal de datos abiertos. Los registros son horarios, por estación y variable, e incluyen las coordenadas, la unidad y el tipo de estación (Instituto de Hidrología, 2026). Para las estaciones del corredor, el conjunto contiene PM10, PM2.5, gases y variables meteorológicas entre 2020 y 2024, con las limitaciones descritas en la sección 1.1.

## 2.4 Variables o categorías de la investigación

Las categorías de análisis sirven para verificar si se cumplen los objetivos y se agrupan en cuatro dimensiones, que son calidad del dato, cumplimiento normativo, desempeño del pronóstico y calidad del producto de software. La Tabla 3 presenta sus indicadores.

**Tabla** **3.** *Categorías e indicadores de la investigación*

|                          |                             |                                                                                  |                       |
| ------------------------ | --------------------------- | -------------------------------------------------------------------------------- | --------------------- |
| **Categoría**            | **Variable**                | **Indicador**                                                                    | **Objetivo asociado** |
| Calidad del dato         | Completitud                 | Porcentaje de horas con dato válido por estación y periodo                       | OE1, OE3              |
| Calidad del dato         | Detección de fallas         | Precisión y exhaustividad de las reglas de validación frente a fallas inyectadas | OE3, OE5              |
| Cumplimiento normativo   | Promedio móvil de 24 horas  | Concentración en µg/m³ y categoría del ICA                                       | OE3                   |
| Cumplimiento normativo   | Nivel de declaratoria       | Nivel propuesto según los artículos 11 y 12                                      | OE3                   |
| Desempeño del pronóstico | Error de concentración      | MAE y RMSE a 24 horas frente a persistencia y climatología                       | OE4                   |
| Desempeño del pronóstico | Anticipación de excedencias | Exhaustividad y precisión sobre el umbral de 75 µg/m³                            | OE4                   |
| Calidad del software     | Adecuación funcional        | Porcentaje de casos de prueba aprobados por requerimiento                        | OE5                   |
| Calidad del software     | Eficiencia de desempeño     | Tiempo entre la llegada de un dato y su evaluación                               | OE5                   |
| Calidad del software     | Usabilidad                  | Puntuación SUS y tasa de éxito en tareas                                         | OE5                   |

Fuente: Elaboración propia.

## 2.5 Bases legales de la investigación

El proyecto se enmarca en la normativa ambiental sobre vigilancia de la calidad del aire y en la normativa sobre información pública, datos personales y uso de software. La Tabla 4 resume las normas aplicables y cómo se relacionan con el sistema.

**Tabla** **4.** *Marco legal aplicable*

|                                         |                                                                                                                   |                                                                                         |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Norma**                               | **Objeto**                                                                                                        | **Relación con el proyecto**                                                            |
| Ley 99 de 1993                          | Crea el Ministerio del Medio Ambiente y organiza el Sistema Nacional Ambiental                                    | Define a las corporaciones autónomas regionales como autoridades ambientales            |
| Decreto 1076 de 2015                    | Decreto Único Reglamentario del Sector Ambiente y Desarrollo Sostenible                                           | Compila la reglamentación sobre protección y control de la calidad del aire             |
| Resolución 650 de 2010 (MAVDT)          | Adopta el Protocolo para el Monitoreo y Seguimiento de la Calidad del Aire                                        | Fuente de los criterios de validación y representatividad                               |
| Resolución 2254 de 2017 (MADS)          | Adopta la norma de calidad del aire ambiente                                                                      | Límites, niveles de declaratoria, ICA, informes y migración a SISAIRE                   |
| CONPES 3943 de 2018                     | Política para el mejoramiento de la calidad del aire                                                              | Marco de política pública para la gestión de la información                             |
| Ley 1712 de 2014                        | Transparencia y acceso a la información pública                                                                   | Sustenta el uso de datos abiertos y la publicación del ICA                              |
| Ley 1581 de 2012 y Decreto 1074 de 2015 | Protección de datos personales. El Decreto 1074 compila el reglamento que antes estaba en el Decreto 1377 de 2013 | Tratamiento de los datos de usuarios y contactos del sistema                            |
| Ley 1273 de 2009                        | Protección de la información y de los datos                                                                       | Requerimientos de seguridad y control de acceso                                         |
| Ley 23 de 1982                          | Derechos de autor                                                                                                 | Protección del software desarrollado y uso de bibliotecas de terceros según su licencia |

Fuente: Elaboración propia.

Los datos de calidad del aire no son datos personales, así que su uso queda fuera del alcance de la Ley 1581 de 2012. La ley sí cubre la información de las cuentas de usuario y de los contactos de notificación, que en el prototipo son ficticios. El sistema incorpora autenticación, almacenamiento seguro de contraseñas, control de acceso por roles y registro de accesos.
