<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

**Software Web de Vigilancia de la Calidad del Aire y Pronóstico de Material Particulado PM10 en el Corredor Industrial Sogamoso-Nobsa, Boyacá**

Barragán Chía, Daniel Fernando

Universidad Manuela Beltrán

Educación Virtual

Ingeniería de Software

Facultad de Ingeniería

Bogotá, Colombia

2026

**Software Web de Vigilancia de la Calidad del Aire y Pronóstico de Material Particulado PM10 en el Corredor Industrial Sogamoso-Nobsa, Boyacá**

Barragán Chía, Daniel Fernando

Trabajo de Grado presentado como requisito parcial para optar al título de:

Ingeniero de Software

Olga Lucía Roa Bohórquez

Mg. en Ingeniería de Sistemas y Computación.

Universidad Manuela Beltrán

Educación Virtual

Ingeniería de Software

Facultad de Ingeniería

Bogotá, Colombia

2026

**Tabla de Contenido**

[Capítulo I: Descripción del proyecto 10](#capítulo-i-descripción-del-proyecto)

[1.1 Planteamiento del problema de investigación 11](#planteamiento-del-problema-de-investigación)

[1.2 Justificación en términos de necesidades y pertinencia de la investigación 14](#justificación-en-términos-de-necesidades-y-pertinencia-de-la-investigación)

[1.3 Objetivos: General y específicos 15](#objetivos-general-y-específicos)

[1.3.1 Objetivo general 15](#objetivo-general)

[1.3.2 Objetivos específicos 16](#objetivos-específicos)

[Capítulo II: Marco teórico y Referencial 17](#capítulo-ii-marco-teórico-y-referencial)

[2.1 Antecedentes de la Investigación 17](#antecedentes-de-la-investigación)

[2.2 Bases o fundamentos teóricos 20](#bases-o-fundamentos-teóricos)

[2.2.1 Material particulado y norma de calidad del aire 20](#material-particulado-y-norma-de-calidad-del-aire)

[2.2.2 Sistemas de vigilancia y calidad del dato 20](#sistemas-de-vigilancia-y-calidad-del-dato)

[2.2.3 Pronóstico de series de tiempo y líneas base 21](#pronóstico-de-series-de-tiempo-y-líneas-base)

[2.2.4 Potenciación del gradiente 21](#potenciación-del-gradiente)

[2.2.5 Métricas de evaluación 22](#métricas-de-evaluación)

[2.2.6 Intervalos de predicción 22](#intervalos-de-predicción)

[2.2.7 Arquitectura de software 22](#arquitectura-de-software)

[2.2.8 Simulación con reloj virtual 23](#simulación-con-reloj-virtual)

[2.2.9 Metodologías y modelado 24](#metodologías-y-modelado)

[2.2.10 Calidad del producto y usabilidad 24](#calidad-del-producto-y-usabilidad)

[2.3 Antecedentes de la empresa o contexto 24](#antecedentes-de-la-empresa-o-contexto)

[2.4 Variables o categorías de la investigación 25](#variables-o-categorías-de-la-investigación)

[2.5 Bases legales de la investigación 26](#bases-legales-de-la-investigación)

[Capítulo III: Marco metodológico 28](#capítulo-iii-marco-metodológico)

[3.1 Tipo de Investigación 28](#tipo-de-investigación)

[3.2 Diseño de Investigación 28](#diseño-de-investigación)

[3.2.1 Metodología ágil 29](#metodología-ágil)

[3.2.2 Definición de actores y Roles 30](#definición-de-actores-y-roles)

[3.2.3 Casos de uso de alto nivel 31](#casos-de-uso-de-alto-nivel)

[3.2.4 Casos de uso extendidos 33](#casos-de-uso-extendidos)

[3.3 Población 35](#población)

[3.3.1 Desarrolladores 35](#desarrolladores)

[3.3.2 Usuarios finales 35](#usuarios-finales)

[3.4 Técnicas e instrumentos de recolección de datos 36](#técnicas-e-instrumentos-de-recolección-de-datos)

[3.4.1 Talleres de requisitos 36](#talleres-de-requisitos)

[3.4.2 Entrevistas y encuestas 37](#entrevistas-y-encuestas)

[3.4.3 Pruebas de usabilidad 37](#pruebas-de-usabilidad)

[3.5 Técnicas de procesamiento y análisis de los datos 37](#técnicas-de-procesamiento-y-análisis-de-los-datos)

[3.5.1 Análisis cualitativo y cuantitativo 37](#análisis-cualitativo-y-cuantitativo)

[3.5.2 Lista de procesos 38](#lista-de-procesos)

[3.6 Modelado y documentación del Sistema 39](#modelado-y-documentación-del-sistema)

[3.6.1 Requerimientos Funcionales y No Funcionales 39](#requerimientos-funcionales-y-no-funcionales)

[3.6.2 Diagramas de clases 42](#diagramas-de-clases)

[3.6.3 Diagramas de estados 47](#diagramas-de-estados)

[3.6.4 Diagramas de Colaboración 59](#diagramas-de-colaboración)

[3.6.5 Diagramas de Secuencia 70](#diagramas-de-secuencia)

[3.6.6 Diagramas de Componentes 82](#diagramas-de-componentes)

[3.6.7 Diagramas de Distribución 83](#diagramas-de-distribución)

[3.6.8 Modelo relacional de la base de datos 85](#modelo-relacional-de-la-base-de-datos)

[3.6.9 Script de generación de la base de datos 89](#script-de-generación-de-la-base-de-datos)

[3.6.10 Repositorio del código fuente 96](#repositorio-del-código-fuente)

[Capítulo V: Referencias 97](#capítulo-v-referencias)

[Anexo A: Casos de uso extendidos 100](#anexo-a-casos-de-uso-extendidos)

**Lista de Figuras**

[**Figura 1.** *Diagrama general de casos de uso* 33](#_Toc990009)

[**Figura 2.** *Diagrama de paquetes del modelo de dominio* 42](#_Toc990012)

[**Figura 3.** *Diagrama de clases de los paquetes Red de monitoreo, Datos y Simulación* 44](#_Toc990013)

[**Figura 4.** *Diagrama de clases de los paquetes Normativo y Pronóstico* 45](#_Toc990014)

[**Figura 5.** *Diagrama de clases de los paquetes Difusión y Seguridad* 46](#_Toc990015)

[**Figura 6.** *Enumeraciones del modelo de dominio* 47](#_Toc990016)

[**Figura 7.** *Diagrama de estados de la clase Medición* 49](#_Toc990018)

[**Figura 8.** *Diagrama de estados de la clase Declaratoria* 50](#_Toc990019)

[**Figura 9.** *Diagrama de estados de la clase Estación* 51](#_Toc990020)

[**Figura 10.** *Diagrama de estados de la clase Pronóstico* 52](#_Toc990021)

[**Figura 11.** *Diagrama de estados de la clase VersiónModelo* 53](#_Toc990022)

[**Figura 12.** *Diagrama de estados de la clase EjecuciónCiclo* 54](#_Toc990023)

[**Figura 13.** *Diagrama de estados de la clase Notificación* 55](#_Toc990024)

[**Figura 14.** *Diagrama de estados de la clase Informe* 56](#_Toc990025)

[**Figura 15.** *Diagrama de estados de la clase Usuario* 57](#_Toc990026)

[**Figura 16.** *Diagrama de estados de la clase EscenarioSimulación* 58](#_Toc990027)

[**Figura 17.** *Diagrama de estados de la clase FallaInyectada* 59](#_Toc990028)

[**Figura 18.** *Diagrama de colaboración del proceso P-01 Reproducción de mediciones* 60](#_Toc990029)

[**Figura 19.** *Diagrama de colaboración del proceso P-02 Ingesta* 61](#_Toc990030)

[**Figura 20.** *Diagrama de colaboración del proceso P-03 Validación automática* 62](#_Toc990031)

[**Figura 21.** *Diagrama de colaboración del proceso P-04 Detección de ausencia* 63](#_Toc990032)

[**Figura 22.** *Diagrama de colaboración del proceso P-05 Revisión manual* 64](#_Toc990033)

[**Figura 23.** *Diagrama de colaboración del proceso P-06 Agregación* 65](#_Toc990034)

[**Figura 24.** *Diagrama de colaboración del proceso P-07 Evaluación normativa* 66](#_Toc990035)

[**Figura 25.** *Diagrama de colaboración del proceso P-08 Pronóstico* 67](#_Toc990036)

[**Figura 26.** *Diagrama de colaboración del proceso P-09 Seguimiento del pronóstico* 67](#_Toc990037)

[**Figura 27.** *Diagrama de colaboración del proceso P-10 Notificación* 68](#_Toc990038)

[**Figura 28.** *Diagrama de colaboración del proceso P-11 Informe mensual* 69](#_Toc990039)

[**Figura 29.** *Diagrama de colaboración del proceso P-12 Exportación* 70](#_Toc990040)

[**Figura 30.** *Diagrama de secuencia del proceso P-01 Reproducción de mediciones* 71](#_Toc990041)

[**Figura 31.** *Diagrama de secuencia del proceso P-02 Ingesta* 72](#_Toc990042)

[**Figura 32.** *Diagrama de secuencia del proceso P-03 Validación automática* 73](#_Toc990043)

[**Figura 33.** *Diagrama de secuencia del proceso P-04 Detección de ausencia* 74](#_Toc990044)

[**Figura 34.** *Diagrama de secuencia del proceso P-05 Revisión manual* 75](#_Toc990045)

[**Figura 35.** *Diagrama de secuencia del proceso P-06 Agregación* 76](#_Toc990046)

[**Figura 36.** *Diagrama de secuencia del proceso P-07 Evaluación normativa* 77](#_Toc990047)

[**Figura 37.** *Diagrama de secuencia del proceso P-08 Pronóstico* 78](#_Toc990048)

[**Figura 38.** *Diagrama de secuencia del proceso P-09 Seguimiento del pronóstico* 79](#_Toc990049)

[**Figura 39.** *Diagrama de secuencia del proceso P-10 Notificación* 80](#_Toc990050)

[**Figura 40.** *Diagrama de secuencia del proceso P-11 Informe mensual* 81](#_Toc990051)

[**Figura 41.** *Diagrama de secuencia del proceso P-12 Exportación* 82](#_Toc990052)

[**Figura 42.** *Diagrama de componentes* 83](#_Toc990053)

[**Figura 43.** *Diagrama de distribución* 84](#_Toc990054)

[**Figura 44.** *Diagrama entidad relación de red de monitoreo, datos y simulación* 87](#_Toc990056)

[**Figura 45.** *Diagrama entidad relación de pronóstico y componente normativo* 88](#_Toc990057)

[**Figura 46.** *Diagrama entidad relación de difusión y seguridad* 89](#_Toc990058)

**Lista de Tablas**

[**Tabla 1.** *Síntesis de antecedentes* 19](#_Toc243253323)

[**Tabla 2.** *Estaciones de la red de monitoreo incluidas en el caso de estudio* 25](#_Toc243253324)

[**Tabla 3.** *Categorías e indicadores de la investigación* 26](#_Toc243253325)

[**Tabla 4.** *Marco legal aplicable* 27](#_Toc243253326)

[**Tabla 5.** *Planeación de sprints* 29](#_Toc243253327)

[**Tabla 6.** *Actores del sistema* 30](#_Toc243253328)

[**Tabla 7.** *Roles de la aplicación* 31](#_Toc990006)

[**Tabla 8.** *Matriz de casos de uso y roles* 31](#_Toc990007)

[**Tabla 9.** *Casos de uso de alto nivel* 32](#_Toc990008)

[**Tabla 10.** *Caso de uso extendido CU-03 Revisar dato sospechoso* 33](#_Toc243253330)

[**Tabla 11.** *Caso de uso extendido CU-06 Confirmar o descartar declaratoria* 34](#_Toc243253331)

[**Tabla 12.** *Caso de uso extendido CU-07 Generar pronóstico diario* 34](#_Toc243253332)

[**Tabla 13.** *Matriz de trazabilidad entre fuentes y requerimientos funcionales* 36](#_Toc990010)

[**Tabla 14.** *Lista de procesos del sistema* 38](#_Toc243253333)

[**Tabla 15.** *Requerimientos funcionales* 39](#_Toc243253334)

[**Tabla 16.** *Requerimientos no funcionales por tipo* 40](#_Toc990011)

[**Tabla 17.** *Clases sin diagrama de estados* 48](#_Toc990017)

[**Tabla 18.** *Tablas del modelo relacional* 85](#_Toc990055)

[**Tabla 19.** *Estructura del repositorio* 96](#_Toc990059)

[**Tabla 20.** *Caso de uso extendido CU-01 Enviar mediciones* 100](#_Toc990060)

[**Tabla 21.** *Caso de uso extendido CU-02 Validar mediciones* 100](#_Toc990061)

[**Tabla 22.** *Caso de uso extendido CU-04 Consultar estado de la red* 101](#_Toc990062)

[**Tabla 23.** *Caso de uso extendido CU-05 Evaluar nivel normativo* 101](#_Toc990063)

[**Tabla 24.** *Caso de uso extendido CU-08 Consultar desempeño del pronóstico* 102](#_Toc990064)

[**Tabla 25.** *Caso de uso extendido CU-09 Notificar a entidades* 102](#_Toc990065)

[**Tabla 26.** *Caso de uso extendido CU-10 Generar informe mensual* 102](#_Toc990066)

[**Tabla 27.** *Caso de uso extendido CU-11 Exportar datos validados* 103](#_Toc990067)

[**Tabla 28.** *Caso de uso extendido CU-12 Consultar ICA y pronóstico* 103](#_Toc990068)

[**Tabla 29.** *Caso de uso extendido CU-13 Gestionar configuración* 104](#_Toc990069)

[**Tabla 30.** *Caso de uso extendido CU-14 Configurar simulación* 104](#_Toc990070)

[**Tabla 31.** *Caso de uso extendido CU-15 Iniciar sesión* 104](#_Toc990071)

# 

#
