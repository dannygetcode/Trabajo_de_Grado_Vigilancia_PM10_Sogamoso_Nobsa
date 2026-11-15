<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

# Capítulo I: Descripción del proyecto

Este capítulo plantea el problema que motiva el trabajo, justifica su desarrollo y fija los objetivos del software. La sección 1.1 describe la situación del sistema de vigilancia de la calidad del aire en el corredor industrial Sogamoso-Nobsa, formula la pregunta de investigación y delimita su alcance. La sección 1.2 justifica el proyecto desde lo normativo, lo técnico y lo práctico. La sección 1.3 presenta el objetivo general y los objetivos específicos.

## 1.1 Planteamiento del problema de investigación

El corredor industrial Sogamoso-Nobsa, en el departamento de Boyacá, concentra siderurgia, producción de cemento y cal y hornos de ladrillo, fuentes reconocidas de emisión de material particulado (Uribe Barón & Suárez Araque, 2009). La Corporación Autónoma Regional de Boyacá (Corpoboyacá) vigila la calidad del aire en la zona con una red de estaciones automáticas en Sogamoso, Nobsa, Tunja y Paipa. Cinco de ellas están en el corredor. Tres quedan en Sogamoso, que son UPTC, El Recreo y SENA, y dos en Nobsa, que son Nazaret y Bomberos (Corporación Autónoma Regional de Boyacá, 2025).

La Resolución 2254 de 2017 del Ministerio de Ambiente y Desarrollo Sostenible impone a las autoridades ambientales obligaciones que dependen de procesar los datos de forma continua. El artículo 25 obliga a migrar al Subsistema de Información sobre Calidad del Aire (SISAIRE) información actualizada y validada, y el artículo 24 exige informes mensuales, trimestrales y anuales. Los artículos 11 y 12 definen el cálculo de los niveles de prevención, alerta y emergencia a partir de promedios móviles de 24 horas con seguimiento horario. El artículo 11 permite además declarar un nivel de forma anticipada cuando lo indique un modelo de pronóstico calibrado y validado. Cuando se superan los niveles máximos permisibles, el parágrafo 2 del artículo 6 obliga a informar a las autoridades de salud y de gestión del riesgo (Ministerio de ambiente y desarrollo sostenible, 2017).

Los informes publicados por Corpoboyacá muestran que la red opera con un laboratorio acreditado, aplica los criterios de validación del manual de aseguramiento de la calidad de la Agencia de Protección Ambiental de los Estados Unidos y reporta la representatividad temporal de cada estación. En 2024, la representatividad anual de PM10 osciló entre 82,7 % en El Recreo y 99,7 % en SENA, por encima del mínimo de 75 % que fija el protocolo nacional (Corporación Autónoma Regional de Boyacá, 2025). La medición y la validación existen, y el problema está en la forma en que la información se procesa y se pone a disposición.

La revisión de los informes deja tres hallazgos. El primero es que los informes miran hacia atrás. Son documentos estáticos de entre 74 y 126 páginas que resumen un periodo que ya pasó. El anual de 2025, por ejemplo, tiene fecha de reporte del 16 de febrero de 2026 (Corporación Autónoma Regional de Boyacá, 2026). En los informes revisados, que son los anuales de 2022 a 2025, el trimestral de enero a marzo de 2024 y el mensual de junio de 2025, no aparecen pronósticos de calidad del aire, evaluación de niveles de prevención o alerta según el artículo 11, ni envío de datos al SISAIRE.

El segundo hallazgo apunta a un procesamiento manual. El informe trimestral de enero a marzo de 2024 tiene celdas con el error \#¡DIV/0\! de la hoja de cálculo, series en cero sin explicación, días marcados como no registrados y una estación móvil que figura en una tabla de resultados pero no en el listado oficial de estaciones (Corporación Autónoma Regional de Boyacá, 2024).

El tercer hallazgo está en el canal de datos abiertos. El conjunto de datos Calidad del aire en Colombia, publicado por el Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM) en el portal datos.gov.co, se descargó el 30 de agosto de 2026 y su último registro para las estaciones del corredor corresponde a diciembre de 2024, lo que implica un rezago superior a veinte meses. En el mismo conjunto se identificaron registros duplicados y una estación, Móvil Koica, asignada al municipio de Sogamoso pese a que sus coordenadas y los informes de Corpoboyacá la ubican en Tunja (Instituto de Hidrología, 2026).

El Protocolo para el Monitoreo y Seguimiento de la Calidad del Aire permite validar los datos de forma manual o con aplicativos de software. Recomienda mantener una base de datos con todas las mediciones y otra solo con los datos válidos, y describe cuatro pruebas, que son la de límites, la de total de datos, la de relación entre parámetros y la de comparación entre sitios (Ministerio de Ambiente, 2010a). En la región no se identificó ninguna herramienta de software que integre esas pruebas, la evaluación normativa horaria, el pronóstico de corto plazo, la notificación a las entidades de salud y la generación de informes en un mismo flujo de trabajo.

Con base en lo anterior, la pregunta de investigación es la siguiente.

¿Cómo desarrollar un software web de vigilancia de la calidad del aire y pronóstico de material particulado PM10 para el corredor industrial Sogamoso-Nobsa que integre en un solo flujo continuo la validación de los datos, la evaluación de la Resolución 2254 de 2017 y el pronóstico a 24 horas?

La delimitación tiene cuatro dimensiones. En lo conceptual, el pronóstico cubre solo el PM10, el único contaminante medido en las cinco estaciones del corredor. El PM2.5 se registra únicamente en El Recreo, Nazaret y Bomberos, así que el sistema lo admite en los módulos de vigilancia pero no lo pronostica. En lo espacial, el caso de estudio comprende esas cinco estaciones, y el diseño permite incorporar otras mediante configuración. En lo temporal, se usan los registros horarios del portal de datos abiertos entre 2020 y 2024, y el desarrollo se realiza durante 2026. En lo disciplinar, el trabajo pertenece a la ingeniería de software. No instala instrumentos de medición, no reemplaza el software de adquisición de las estaciones ni desarrolla modelos de dispersión atmosférica. Como no se tiene acceso a la operación real de la red, el sistema se valida en un entorno que reproduce los datos históricos como si llegaran en tiempo real.

## 1.2 Justificación en términos de necesidades y pertinencia de la investigación

La justificación normativa del proyecto se apoya en las obligaciones descritas en la sección anterior, y cada función del sistema corresponde a un artículo de la Resolución 2254 de 2017. La validación y la exportación de datos responden al artículo 25, la evaluación de niveles a los artículos 10, 11 y 12, la notificación al parágrafo 2 del artículo 6, el informe periódico al artículo 24 y la publicación del índice de calidad del aire a los artículos 18 a 22 (Ministerio de ambiente y desarrollo sostenible, 2017). Además, el artículo 11 reconoce el pronóstico calibrado y validado como fundamento para declarar niveles de forma anticipada, así que el componente de aprendizaje automático cumple una función regulatoria.

En lo técnico, la Resolución 650 de 2010, que adopta el protocolo nacional, contempla el uso de aplicativos de software para la validación y propone una arquitectura de datos con dos bases diferenciadas (Ministerio de Ambiente, 2010b). La literatura revisada muestra que otras autoridades ambientales del país han requerido herramientas similares. Bravo Rivera (2012) desarrolló para la Corporación Autónoma Regional para la Defensa de la Meseta de Bucaramanga un software de depuración y clasificación de datos de gases contaminantes, y Correa Builes y Morales Rodríguez (2020) documentaron un procedimiento de validación en tres niveles para el sistema de vigilancia de la Universidad Distrital. Ninguno de estos trabajos integra la evaluación normativa continua ni el pronóstico.

La necesidad práctica surge de los actores que gestionan la calidad del aire en el corredor. La Mesa Regional de Calidad del Aire del Corredor Industrial de Boyacá tiene a Corpoboyacá como secretaría técnica y reúne a las secretarías de salud, ambiente y tránsito de Sogamoso, Nobsa y Duitama (Ministerio de Ambiente y Desarrollo Sostenible, 2022). Un sistema que procese los datos de forma continua beneficiaría al personal técnico de la red, que tendría una cola de revisión e indicadores de calidad del dato. También a la coordinación, que contaría con propuestas de declaratoria sustentadas e informes generados a partir de datos validados, y a las entidades de salud, que recibirían notificaciones oportunas. La ciudadanía accede a la información mediante la publicación del índice de calidad del aire, en coherencia con la estrategia de comunicación que exige el artículo 22.

El problema surge del análisis de las obligaciones normativas, de los informes públicos de la autoridad ambiental y de los datos abiertos de la red, sin que una organización contratante lo haya planteado. Se aborda con un prototipo funcional que opera en un entorno simulado. Esta decisión permite verificar el sistema de forma reproducible, con fallas inyectadas de manera controlada, y deja el componente de ingesta listo para conectarse a una fuente real sin modificar el resto de la arquitectura.

Por último, el proyecto es pertinente para la línea de investigación en Desarrollo de Software del programa de Ingeniería de Software de la Universidad Manuela Beltrán. Exige ingeniería de requisitos, diseño de una arquitectura basada en servicios, modelado con el Lenguaje Unificado de Modelado (UML), aplicación de una metodología ágil, pruebas de software y documentación técnica y de usuario, todo sobre un problema con soporte normativo y datos reales.

## 1.3 Objetivos: General y específicos

### 1.3.1 Objetivo general

Desarrollar un software web de vigilancia de la calidad del aire y pronóstico de material particulado PM10 para el corredor industrial Sogamoso-Nobsa, en Boyacá, que integre la validación de datos, la evaluación normativa de la Resolución 2254 de 2017 y el pronóstico a 24 horas con aprendizaje automático, y que se verifique en un entorno que reproduce datos históricos.

### 1.3.2 Objetivos específicos

1.  Especificar los requisitos funcionales y no funcionales del sistema a partir de la Resolución 2254 de 2017, el Protocolo para el Monitoreo y Seguimiento de la Calidad del Aire y el análisis de los datos públicos de la red de monitoreo del corredor.

2.  Diseñar la arquitectura del software y su modelo de datos mediante diagramas UML, con un componente de ingesta desacoplado que permita sustituir el simulador de estaciones por una fuente de datos real.

3.  Implementar los módulos de ingesta, validación automática, revisión manual de datos, evaluación normativa, notificación, generación de informes y publicación del índice de calidad del aire.

4.  Entrenar y evaluar un modelo de pronóstico de PM10 a 24 horas frente a las líneas base de persistencia y climatología, e integrarlo al sistema con seguimiento de su desempeño.

5.  Verificar el sistema mediante pruebas funcionales, pruebas de detección de fallas inyectadas y de usabilidad con la escala de usabilidad del sistema (SUS).
