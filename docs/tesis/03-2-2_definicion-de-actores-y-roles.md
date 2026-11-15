<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

### 3.2.2 Definición de actores y Roles

Los actores del sistema salen de las responsabilidades que la Resolución 2254 de 2017 y el protocolo nacional asignan a la autoridad ambiental y a las entidades relacionadas. La Tabla 6 describe cada uno.

**Tabla** **6.** *Actores del sistema*

|                                       |                |                                                                                                                                                       |
| ------------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Actor**                             | **Tipo**       | **Responsabilidad**                                                                                                                                   |
| Técnico del SVCA                      | Humano         | Revisa los datos marcados como sospechosos, los aprueba, corrige o invalida con justificación, consulta el estado de la red y exporta datos validados |
| Coordinador del SVCA                  | Humano         | Confirma o descarta las propuestas de declaratoria, consulta el desempeño del pronóstico y aprueba los informes                                       |
| Entidad de salud o gestión del riesgo | Humano externo | Recibe notificaciones y consulta información de solo lectura                                                                                          |
| Ciudadano                             | Humano externo | Consulta el ICA vigente y el pronóstico en la vista pública                                                                                           |
| Administrador                         | Humano         | Gestiona usuarios, roles, estaciones, parámetros normativos y escenarios de simulación                                                                |
| Simulador de estaciones               | Sistema        | Emite las mediciones históricas según el reloj virtual e inyecta fallas controladas                                                                   |
| Planificador                          | Sistema        | Dispara los procesos periódicos de validación, evaluación horaria y pronóstico diario                                                                 |

Fuente: Elaboración propia.

Un actor describe quién interactúa con el sistema y un rol define qué puede hacer dentro de él. El control de acceso se implementa por roles (RF-14), de modo que cada cuenta de usuario tiene exactamente un rol y cada rol agrupa un conjunto de permisos. El simulador y el planificador no usan cuentas personales. Se autentican con una credencial de servicio que solo habilita la ingesta y los procesos programados. El ciudadano no tiene cuenta, porque la vista pública es de solo lectura. La Tabla 7 presenta los roles y la Tabla 8 cruza cada caso de uso con los roles que lo pueden ejecutar.

**Tabla** **7.** *Roles de la aplicación*

|                      |                                        |                                                                                                                                        |
| -------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Rol**              | **Actor**                              | **Permisos**                                                                                                                           |
| ADMINISTRADOR        | Administrador                          | Gestionar usuarios, roles, estaciones, variables, parámetros normativos y escenarios de simulación. Consultar el registro de auditoría |
| TECNICO              | Técnico del SVCA                       | Revisar datos sospechosos, consultar el estado de la red y exportar datos validados                                                    |
| COORDINADOR          | Coordinador del SVCA                   | Confirmar o descartar declaratorias, consultar el desempeño del pronóstico, consultar el estado de la red y generar y aprobar informes |
| CONSULTA             | Entidad de salud o gestión del riesgo  | Consultar en modo de solo lectura el ICA, los pronósticos, las declaratorias y los informes aprobados. Recibir notificaciones          |
| SERVICIO             | Simulador de estaciones y planificador | Enviar lotes de mediciones y disparar los procesos programados mediante credencial de servicio                                         |
| Público (sin cuenta) | Ciudadano                              | Consultar la vista pública del ICA y del pronóstico                                                                                    |

Fuente: Elaboración propia.

**Tabla** **8.** *Matriz de casos de uso y roles*

|                                          |         |         |         |         |          |         |
| ---------------------------------------- | ------- | ------- | ------- | ------- | -------- | ------- |
| **Caso de uso**                          | **ADM** | **TEC** | **COO** | **CON** | **SERV** | **PÚB** |
| CU-01 Enviar mediciones                  |         |         |         |         | X        |         |
| CU-02 Validar mediciones                 |         |         |         |         | X        |         |
| CU-03 Revisar dato sospechoso            |         | X       |         |         |          |         |
| CU-04 Consultar estado de la red         |         | X       | X       |         |          |         |
| CU-05 Evaluar nivel normativo            |         |         |         |         | X        |         |
| CU-06 Confirmar o descartar declaratoria |         |         | X       |         |          |         |
| CU-07 Generar pronóstico diario          |         |         |         |         | X        |         |
| CU-08 Consultar desempeño del pronóstico |         |         | X       |         |          |         |
| CU-09 Notificar a entidades              |         |         |         |         | X        |         |
| CU-10 Generar informe mensual            |         |         | X       |         |          |         |
| CU-11 Exportar datos validados           |         | X       |         |         |          |         |
| CU-12 Consultar ICA y pronóstico         | X       | X       | X       | X       |          | X       |
| CU-13 Gestionar configuración            | X       |         |         |         |          |         |
| CU-14 Configurar simulación              | X       |         |         |         |          |         |
| CU-15 Iniciar sesión                     | X       | X       | X       | X       |          |         |

Fuente: Elaboración propia.
