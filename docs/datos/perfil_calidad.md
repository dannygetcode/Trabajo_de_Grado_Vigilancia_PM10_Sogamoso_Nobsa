# Perfil de calidad de los datos IDEAM del corredor Sogamoso-Nobsa

<!-- Generado por tools/perfil_datos.py. No editar a mano: volver a ejecutar el script. -->

Fuente: `data/raw/ideam_corredor.csv` (IDEAM, datos.gov.co `g4t8-zkc3`, filtrado con `tools/filtrar_ideam.py`). Filas totales: 1.803.476. Excluidas de MOVIL KOICA (31828): 221.751. Analizadas: 1.581.725.

## 1. Estructura y formato

- Fechas que no siguen `%Y %b %d %I:%M:%S %p`: 0.
- Duración `fin - inicio`: 0 days 01:00:00 → 1.581.725. Columna `DURACIÓN`: ['60'].
- Inicios que no están en punto: 0.
- Periodo: 2020-01-01 00:00:00 a 2024-12-31 22:00:00 (hora del archivo).
- Valores vacíos: 0. Valores no numéricos: 0.
- Valores con separador de miles (`1,091.39`): 8.529, en CO, RUVb. El normalizador quita la coma; no cambia ningún dígito.
- Máximo de decimales: 2. Cabe en `medicion.valor_crudo NUMERIC(10,3)` sin redondear.

Decimales por variable (número de filas):

| var | 0 | 1 | 2 |
|---|---|---|---|
| CO | 7261 | 17246 | 25131 |
| DViento | 21902 | 52487 | 86581 |
| HAire10 | 8288 | 47196 | 62211 |
| HAire2 | 3217 | 14672 | 16858 |
| NO2 | 615 | 4926 | 49154 |
| O3 | 7291 | 23570 | 63619 |
| P | 36319 | 42781 | 82682 |
| PLiquida | 161111 | 6229 | 6635 |
| PM10 | 35743 | 14802 | 114440 |
| PM2.5 | 1047 | 8852 | 82961 |
| RUVb | 30870 | 3452 | 35241 |
| SO2 | 11879 | 13442 | 66966 |
| TAire10 | 4858 | 32961 | 78491 |
| TAire2 | 1849 | 15770 | 18789 |
| VViento | 10859 | 77909 | 72562 |

## 2. Duplicados

- Filas idénticas: 0.
- Filas con la misma clave (estación, variable, inicio), que es la restricción única de `medicion`: 0.
- El normalizador falla si encuentra alguna; con estos datos no descarta nada.

## 3. Estaciones y coordenadas

| est | codigo | nombre | lat | lon | alt | filas |
|---|---|---|---|---|---|---|
| 30810 | SENA | SENA | 5.756944 | -72.908333 | 2,476 | 247577 |
| 30815 | BOMBEROS | BOMBEROS | 5.770917 | -72.937964 | 2,499 | 293221 |
| 31719 | UPTC | UPTC | 5.704583333333 | -72.942777777778 | 2,523 | 217041 |
| 31826 | RECREO | EL RECREO | 5.726325 | -72.920905 | 2,476 | 417572 |
| 31827 | NAZARET | NAZARETH-JAC | 5.766163 | -72.896959 | 2,479 | 406314 |

Las coordenadas de SENA, BOMBEROS, RECREO y NAZARET difieren de `db/10` en la cuarta cifra decimal (decenas de metros) y SENA y RECREO tienen altitud 2476 en lugar de 2477 y 2483. No afecta al sistema; se puede ajustar `db/10` con un script nuevo si se quiere exactitud.

Filas por variable y estación:

| var | BOMBEROS | NAZARET | RECREO | SENA | UPTC |
|---|---|---|---|---|---|
| CO | 0 | 18482 | 31156 | 0 | 0 |
| DViento | 30373 | 35149 | 35667 | 30196 | 29585 |
| HAire10 | 23579 | 28437 | 29183 | 12980 | 23516 |
| HAire2 | 7457 | 6622 | 5920 | 7196 | 7552 |
| NO2 | 0 | 31375 | 23320 | 0 | 0 |
| O3 | 22623 | 24002 | 21329 | 26526 | 0 |
| P | 32320 | 34331 | 34469 | 30270 | 30392 |
| PLiquida | 33323 | 37613 | 38015 | 32404 | 32620 |
| PM10 | 32159 | 30931 | 33232 | 34691 | 33972 |
| PM2.5 | 28121 | 32236 | 32503 | 0 | 0 |
| RUVb | 5877 | 31754 | 31932 | 0 | 0 |
| SO2 | 15014 | 25794 | 29311 | 22168 | 0 |
| TAire10 | 23607 | 27729 | 29180 | 13716 | 22078 |
| TAire2 | 8161 | 6836 | 6656 | 7199 | 7556 |
| VViento | 30607 | 35023 | 35699 | 30231 | 29770 |

## 4. Completitud de PM10 por estación y año

Porcentaje de horas del año con medición:

| codigo | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| BOMBEROS | 72.3 | 52.7 | 63.3 | 90.9 | 87.5 |
| NAZARET | 59.4 | 59.8 | 74.2 | 83.6 | 75.7 |
| RECREO | 69.5 | 59.3 | 86.4 | 94.7 | 69.2 |
| SENA | 69 | 69.1 | 84 | 91.6 | 81.9 |
| UPTC | 68.3 | 68.8 | 85.9 | 84.8 | 79.6 |

Días con 18 horas o más de PM10 (75 %, criterio de representatividad de RF-05):

| codigo | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| BOMBEROS | 267 | 184 | 234 | 343 | 320 |
| NAZARET | 214 | 219 | 277 | 312 | 277 |
| RECREO | 253 | 219 | 321 | 355 | 251 |
| SENA | 266 | 268 | 321 | 353 | 303 |
| UPTC | 263 | 270 | 336 | 331 | 294 |

## 5. Horas faltantes de PM10

Rachas de horas sin medición entre la primera y la última medición de cada estación.

| estacion | primera | ultima | huecos | 1 h | 2-3 h | 4-24 h | > 24 h | horas faltantes |
|---|---|---|---|---|---|---|---|---|
| BOMBEROS | 2020-01-01 00:00 | 2024-12-31 22:00 | 2165 | 1471 | 533 | 125 | 36 | 11688 |
| NAZARET | 2020-01-30 07:00 | 2024-12-31 22:00 | 1140 | 836 | 182 | 75 | 47 | 12213 |
| RECREO | 2020-01-01 00:00 | 2024-12-31 01:00 | 1186 | 892 | 169 | 98 | 27 | 10594 |
| SENA | 2020-01-01 00:00 | 2024-12-31 22:00 | 1896 | 1514 | 329 | 44 | 9 | 9156 |
| UPTC | 2020-01-01 00:00 | 2024-12-31 17:00 | 1996 | 1642 | 285 | 32 | 37 | 9870 |

Los tres huecos más largos por estación:

| estacion | desde | horas | días |
|---|---|---|---|
| BOMBEROS | 2021-08-31 23:00 | 3862 | 160.9 |
| BOMBEROS | 2022-05-31 23:00 | 721 | 30 |
| BOMBEROS | 2020-01-05 10:00 | 589 | 24.5 |
| NAZARET | 2021-08-31 23:00 | 2185 | 91 |
| NAZARET | 2021-12-28 10:00 | 1025 | 42.7 |
| NAZARET | 2021-01-08 17:00 | 792 | 33 |
| RECREO | 2021-08-31 23:00 | 2186 | 91.1 |
| RECREO | 2024-10-01 00:00 | 744 | 31 |
| RECREO | 2022-05-31 23:00 | 721 | 30 |
| SENA | 2021-08-31 23:00 | 2185 | 91 |
| SENA | 2020-10-15 15:00 | 795 | 33.1 |
| SENA | 2024-07-31 23:00 | 745 | 31 |
| UPTC | 2021-08-31 23:00 | 2185 | 91 |
| UPTC | 2023-02-28 23:00 | 745 | 31 |
| UPTC | 2024-09-30 23:00 | 745 | 31 |

Horas sin PM10 en **ninguna** estación: 3.164. Periodos de más de un día con toda la red sin datos: 7. Los mayores:

| inicio | horas | días |
|---|---|---|
| 2021-08-31 23:00 | 2185 | 91 |
| 2020-09-04 11:00 | 51 | 2.1 |
| 2020-09-11 18:00 | 44 | 1.8 |
| 2024-10-14 22:00 | 43 | 1.8 |
| 2020-09-02 15:00 | 43 | 1.8 |

Meses calendario sin ninguna medición de PM10 en alguna estación: 2021-12 (BOMBEROS); 2022-01 (BOMBEROS, NAZARET); 2022-06 (BOMBEROS, NAZARET, RECREO, SENA); 2023-03 (UPTC); 2024-08 (SENA); 2024-10 (NAZARET, RECREO, SENA, UPTC). (Un mes ausente del todo no aparece en esta lista porque no tiene filas; lo muestran los huecos.) Que muchos huecos empiecen a las 23:00 del último día del mes y duren un mes exacto sugiere meses que faltan en el export, no fallas de las estaciones.

Un hueco de más de dos horas es lo que P-04 debe detectar como estación sin transmisión (RNF-03). La reproducción de los históricos ya contiene muchos casos reales, además de los inyectados.

## 6. Valores de PM10

| codigo | count | mean | std | min | 50% | 95% | 99% | max |
|---|---|---|---|---|---|---|---|---|
| BOMBEROS | 32159 | 22.6 | 14.3 | 0 | 19.4 | 51 | 63.6 | 138.4 |
| NAZARET | 30931 | 28.1 | 14.6 | 0 | 25.7 | 55.7 | 68 | 163.1 |
| RECREO | 33232 | 27 | 14.8 | 0 | 24.8 | 55.3 | 67 | 129 |
| SENA | 34691 | 42.8 | 22.5 | 0 | 39.5 | 85.1 | 103.6 | 318.7 |
| UPTC | 33972 | 31.3 | 26 | 0 | 24 | 84 | 103 | 249 |

- Ceros: 629. Negativos: 0. Mayores que 1000 (máximo físico de `db/10`): 0.

Promedio móvil de 24 horas con 18 o más horas válidas (lo que calcula P-06), sin validación previa:

| estacion | máximo promedio 24 h | horas ≥ 75 (límite diario) | horas ≥ 155 (prevención) | horas ≥ 255 (alerta) |
|---|---|---|---|---|
| BOMBEROS | 54.8 | 0 | 0 | 0 |
| NAZARET | 62.2 | 0 | 0 | 0 |
| RECREO | 60 | 0 | 0 | 0 |
| SENA | 91.9 | 397 | 0 | 0 |
| UPTC | 72.5 | 0 | 0 | 0 |

Rachas de seis horas o más con el mismo valor (regla de valor repetido de HU-18): BOMBEROS 1, NAZARET 1, RECREO 0, SENA 0, UPTC 6.

Cambio absoluto entre horas consecutivas (µg/m³), insumo para el umbral de cambio brusco (`docs/planes/validacion.md`):

| cuantil | BOMBEROS | NAZARET | RECREO | SENA | UPTC |
|---|---|---|---|---|---|
| 0.5 | 5.4 | 6.2 | 6 | 10.1 | 10 |
| 0.9 | 14.7 | 15.5 | 15.1 | 28.6 | 29 |
| 0.99 | 22.4 | 23.9 | 22.9 | 46 | 46.3 |
| 0.999 | 38.3 | 34 | 30.8 | 89 | 78 |

Horas con PM2.5 mayor que PM10 en la misma estación (físicamente dudoso): 0 de 86.727.

## 7. Zona horaria de las fechas

| grupo | codigo | hora del máximo | hora del mínimo |
|---|---|---|---|
| HAire | BOMBEROS | 8 | 17 |
| HAire | NAZARET | 6 | 17 |
| HAire | RECREO | 7 | 17 |
| HAire | SENA | 8 | 18 |
| HAire | UPTC | 6 | 16 |
| RUVb | BOMBEROS | 15 | 0 |
| RUVb | NAZARET | 14 | 4 |
| RUVb | RECREO | 15 | 5 |
| TAire | BOMBEROS | 18 | 8 |
| TAire | NAZARET | 17 | 6 |
| TAire | RECREO | 17 | 7 |
| TAire | SENA | 18 | 8 |
| TAire | UPTC | 16 | 6 |

Lo esperado según el sol: el mediodía solar en el corredor (longitud ≈ 72,92° O) es a las 11:52 hora de Colombia y a las 16:52 UTC. El intervalo horario que lo contiene es el de las **11 h** si las fechas están en hora local y el de las **16 h** si están en UTC. La radiación UV debería tener su máximo ahí, y la temperatura dos a tres horas después.

Desfase de cada estación respecto a NAZARET (horas que maximizan la correlación de la temperatura y la humedad horarias; 0 = misma convención):

| variable | estacion | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| HAire | BOMBEROS | -1 | -1 | -1 | -1 | -1 |
| HAire | RECREO | 0 | 0 | 0 | 0 | 0 |
| HAire | SENA |  |  | -1 | -1 | -1 |
| HAire | UPTC | 0 | 1 | 1 | 0 | 0 |
| TAire | BOMBEROS | -1 | -1 | -1 | -1 | -1 |
| TAire | RECREO | 0 | 0 | 0 | 0 | 0 |
| TAire | SENA |  |  | -1 | -1 | -1 |
| TAire | UPTC | -1 | 1 | 1 | 0 | -1 |

Conclusión en la sección 9.

## 8. Cambio de altura de los sensores meteorológicos

| var | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| HAire10 | 16965 | 24930 | 36495 | 39305 | 0 |
| HAire2 | 0 | 0 | 0 | 0 | 34747 |
| TAire10 | 16271 | 24218 | 35787 | 40034 | 0 |
| TAire2 | 0 | 0 | 0 | 0 | 36408 |

Temperatura y humedad a 10 m hasta 2023 y a 2 m en 2024 (`TAire10` → `TAire2`, `HAire10` → `HAire2`). No son la misma serie: un modelo que las use debe tratarlas como variables distintas o corregir el salto. Se conservan con su código original en `meteorologia_normalizada.csv`.

## 9. Respuestas para el diseño

**Decimales.** Como máximo dos. `NUMERIC(10,3)` alcanza y no hace falta ampliar la columna (punto abierto 1 de `docs/api/README.md`, cerrado). La regla de la ingesta que rechaza más de tres decimales no rechazará ningún dato histórico.

**Zona horaria.** Los datos no la confirman. El máximo de radiación UV cae en las 14 a 15 h y el de temperatura entre las 16 y las 18 h, entre lo esperado para hora local y para UTC; ninguna de las dos convenciones encaja limpio, y la curva de UV es más ancha que el día solar, lo que sugiere sensores con respuesta lenta o promedios desplazados. Se mantiene la suposición documentada por el IDEAM (hora legal de Colombia, UTC-5, sin horario de verano) y el normalizador suma cinco horas. El sistema no depende del valor absoluto: los promedios, las reglas y el modelo trabajan con horas relativas. Sí depende de que **las estaciones sean coherentes entre sí** (comparación entre estaciones de HU-18, cobertura espacial de RF-06): ver la tabla de desfases de la sección 7. Punto abierto 2 de `docs/api/README.md`: queda como suposición, no como hecho, y se anota como riesgo.

**Duplicados.** No hay. El simulador puede enviar el archivo tal cual sin decidir nada.

**Formato.** Hay valores con separador de miles; el normalizador los convierte sin cambiar dígitos y comprueba que el número resultante es el mismo.

**Declaratorias con datos reales: no ocurren.** El mayor promedio móvil de 24 horas en cinco años es 91.9 µg/m³, lejos de los 155 del nivel de prevención. Reproducir los históricos nunca generará una propuesta de declaratoria. Para demostrar RF-06, RF-07 y RF-10 hace falta provocarla: (a) una falla nueva del simulador que escale los valores de un periodo (episodio sintético, marcado con `falla_id` como cualquier falla), o (b) parámetros normativos de demostración con vigencia propia (RF-15 lo permite sin tocar código). La (b) no altera datos; la (a) ejercita además el pronóstico. Lo decide `docs/planes/normativo.md`. El límite diario de 75 µg/m³ sí se supera (SENA), así que el ICA de la vista pública mostrará categorías por encima de "aceptable".

**Huecos comunes a toda la red.** Hay periodos largos sin ninguna estación (sección 5). La partición temporal del modelo (HU-38) y la regla de comparación entre estaciones (HU-18) deben contar con ellos; la segunda ya prevé omitirse si no hay otras estaciones (CU-02, 2b).

**Coherencia horaria entre estaciones.** BOMBEROS y SENA aparecen una hora después que NAZARET y RECREO en temperatura y humedad, todos los años; UPTC cambia de un año a otro entre -1 y +1. Puede ser microclima o una convención distinta para etiquetar el intervalo; los datos no lo distinguen. Consecuencias: la comparación entre estaciones de HU-18 debe tolerar una hora de desfase, y el plan del pronóstico debe decidir si lo corrige por estación. **El normalizador no lo corrige**: mover la hora de un dato crudo sin evidencia sería modificarlo.

## 10. Archivos normalizados

No se suben al repositorio (`data/` está en `.gitignore`). Se regeneran con este script.

| Archivo | Filas | SHA-256 |
|---|---|---|
| `data/processed/historico_normalizado.csv` | 257.845 | `b328f3da69f03daa9a57fb19259d73fb53707f1014eafcae35b79e79cef3b1d6` |
| `data/processed/meteorologia_normalizada.csv` | 1.323.880 | `5946b7a6ab893e0c981be864148f0c2f21652d45651bbaf345393b270f5a71f2` |

Formato: `estacion,variable,inicio,valor`; `inicio` en UTC con `Z`, en punto, intervalo de una hora; `valor` con los dígitos del origen. Ordenado por `inicio`, `estacion`, `variable`.

