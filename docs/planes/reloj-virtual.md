# Plan: reloj virtual, reproducción y planificador

- Historias: HU-01, HU-02, HU-03 (reloj), HU-12, HU-13, HU-14 (simulador), HU-16 (planificador, Sprint 2)
- Contratos: `docs/api/reloj.yaml`, `docs/api/simulador.yaml`, `docs/api/ingesta.yaml`
- Decisiones de base: ADR-0001, ADR-0002, ADR-0003
- **Despliegue (ADR-0001):** el reloj y el planificador conservan su código y su API tal como se describen aquí, pero se ejecutan dentro del contenedor `nucleo`, junto a la ingesta. Donde este plan dice "contenedor del reloj" debe leerse "proceso del núcleo". El simulador sí es un contenedor aparte.
- Para quien implementa: sigue el orden de la sección 8. Si algo de este plan choca con un contrato, manda el contrato y se anota la duda en `docs/ESTADO.md`.

## 1. Qué problema resuelve

RNF-11 pide reproducir un año en 30 minutos: 8760 horas en 1800 segundos, unos 205 ms reales por hora virtual, velocidad 17 520. Con un reloj que simplemente corre más rápido, el sistema entra en una carrera: la evaluación de la hora `t` puede dispararse antes de que el lote de `t` termine de insertarse, y el resultado depende de la carga de la máquina. Eso invalida la medición de las reglas frente a fallas inyectadas (sección 3.5.1), que necesita que dos ejecuciones del mismo escenario den lo mismo.

La solución es que el reloj **espere al sistema**: avanza de forma continua a la velocidad pedida, pero no cruza una hora hasta que quienes trabajan en ella confirman que terminaron.

## 2. Dónde va el código

```
servicios/comun/svca_comun/
  reloj.py            # Protocol Reloj, RelojHttp, RelojFalso, modelo Hora
simulador/
  reloj/              # servicio de reloj (contenedor propio, un solo worker)
    domain/estado.py          # máquina de estados pura
    application/servicio.py   # espera, notificación, casos de uso
    infrastructure/escenarios.py  # lectura de escenario_simulacion al arrancar
    api/
  estaciones/         # simulador (contenedor propio)
    domain/fallas.py          # aplicar_fallas, puro
    domain/escenario.py       # transiciones de la Figura 16
    application/reproduccion.py   # bucle de P-01
    application/control.py        # casos de uso de CU-14
    infrastructure/historico.py   # ArchivoHistorico
    infrastructure/repositorio.py # escenario_simulacion, falla_inyectada
    infrastructure/clientes.py    # ingesta y reloj por HTTP
    api/
servicios/planificador/   # Sprint 2. No está en la Tabla 19: anotar la desviación
```

La Tabla 19 pone el reloj virtual dentro de `simulador/`; se respeta, pero son dos contenedores porque el reloj debe existir en producción sin el simulador (RNF-04).

## 3. El reloj

### 3.1 Estado (dominio puro, sin E/S)

```python
@dataclass(frozen=True)
class EstadoReloj:
    modo: Modo                      # REAL | VIRTUAL
    epoca: int
    # Solo en modo VIRTUAL:
    escenario_id: int | None
    velocidad: float
    fin: datetime | None
    ancla_virtual: datetime         # hora de dominio en el instante ancla_mono
    ancla_mono: float               # lectura del reloj monótono
    pausado: bool
    participantes: tuple[str, ...]  # ordenados
    confirmadas: Mapping[str, datetime]
```

El dominio nunca lee relojes: recibe `mono` (reloj monótono) y, para el modo real, `real` (hora UTC del sistema) como argumentos. Solo `application/` los obtiene, a través de una interfaz que las pruebas reemplazan.

### 3.2 Funciones

```
barrera(e)      = min( min(e.confirmadas.values()) + 1 h, e.fin )
ahora(e, mono)  = e.ancla_virtual                                  si e.pausado
                = min( e.ancla_virtual + (mono - e.ancla_mono) * e.velocidad, barrera(e) )   si no
estado(e, mono) = PAUSADO      si e.pausado
                  FINALIZADO   si ahora = e.fin
                  RETENIDO     si ahora = barrera(e)
                  CORRIENDO    en otro caso
retenido_por(e) = participantes cuya confirmación es la mínima, si el estado es RETENIDO
```

En modo `REAL`: `ahora = real`, estado `CORRIENDO`, velocidad 1, lo demás vacío.

### 3.3 Una sola regla para todas las mutaciones

**Toda operación que cambia el estado primero materializa el presente**: calcula `a = ahora(e, mono)` y fija `ancla_virtual = a`, `ancla_mono = mono`. Después aplica su cambio.

Con esa regla salen solas tres propiedades que de otro modo habría que programar caso por caso:

- El tiempo retenido en la barrera no se recupera: al subir la barrera, el reloj sigue desde ella.
- El tiempo en pausa no cuenta.
- `ahora` nunca retrocede dentro de una misma época.

| Operación | Después de materializar |
|---|---|
| `configurar_virtual(inicio, fin, velocidad, participantes, pausado)` | Estado nuevo con `ancla_virtual = inicio`, `confirmadas = {p: inicio}`, `epoca + 1` |
| `configurar_real()` | `modo = REAL`, `epoca + 1` |
| `pausar()` | `pausado = True` |
| `reanudar()` | `pausado = False` |
| `confirmar(p, hora)` | Si `hora > a`: error `HORA_FUTURA`. Si no, `confirmadas[p] = max(actual, hora)` |

Validaciones de `configurar_virtual`: `inicio` y `fin` en punto, `inicio < fin`, `velocidad > 0`. Si el reloj está en `VIRTUAL` con otro `escenario_id`: `RELOJ_OCUPADO`. Reconfigurar el mismo escenario sí se permite: es lo que hace el simulador al recuperarse.

### 3.4 Época

`epoca` debe crecer siempre, también entre reinicios, porque es lo único que le dice a un cliente que la hora pudo saltar. Al arrancar se inicializa con los segundos Unix de la hora real y cada reconfiguración suma uno. El servicio de reloj es el único lugar del sistema donde se permite leer la hora real para datos de dominio.

### 3.5 Arranque

1. Leer `escenario_simulacion` con estado `EN_EJECUCION` o `PAUSADO` (debe haber como mucho uno).
2. Si existe: modo `VIRTUAL`, `pausado = True`, `ancla_virtual = reloj_actual` (o `periodo_inicio` si es nulo), `participantes = ()`, `confirmadas = {}`. Con `confirmadas` vacío la barrera es la propia ancla. Queda a la espera de que el simulador lo reconfigure.
3. Si no existe, o si la base no responde tras reintentar: en el primer caso modo `REAL`; en el segundo **no arrancar**. Arrancar en `REAL` sin poder comprobar la base es justo el accidente que se quiere evitar: los servicios verían la hora de hoy en medio de una reproducción de 2022 y marcarían todas las estaciones sin transmisión.

### 3.6 Espera (`esperar_hasta`, `turno_de`)

Un solo `asyncio.Condition` en `application/`. Toda mutación hace `notify_all()`.

```
condición cumplida(t, turno) =
    epoca cambió desde que empezó la espera
 o  ( ahora >= t  y  todos los participantes anteriores a `turno` confirmaron >= t )

mientras no cumplida y no venció espera_max:
    eta = (t - ahora) / velocidad  si el reloj corre y t <= barrera;  infinito si no
    esperar la condición con tiempo límite min(eta, restante)
responder el estado actual
```

El servidor siempre responde 200 con el estado; es el cliente quien comprueba si ya llegó.

**Un solo proceso.** El estado vive en memoria: el contenedor `nucleo`, que aloja al reloj, se ejecuta con un único worker de Uvicorn. Dos workers serían dos relojes. Dejarlo fijo en el `Dockerfile` y comprobarlo con un comentario en el compose.

### 3.7 Cliente en `servicios/comun`

```python
class Reloj(Protocol):
    async def ahora(self) -> datetime: ...

class RelojHttp:      # ahora(), hora(), esperar(t, turno), confirmar(p, t)
class RelojFalso:     # para pruebas: fijar(t), avanzar(delta)
class RelojNoDisponible(Exception)
```

- `domain/` de cada servicio solo ve `Reloj`. Los casos de uso reciben el reloj por constructor.
- `RelojHttp.ahora()` **no guarda caché**: con el reloj acelerado una hora dura 200 ms.
- Un único `httpx.AsyncClient` por proceso, con conexiones persistentes.
- Si falla, lanza `RelojNoDisponible`. No hay respaldo a la hora del sistema.

**Prohibición en CI** (HU-01): regla `TID251` de ruff con `banned-api` para `datetime.datetime.now`, `datetime.datetime.utcnow`, `datetime.datetime.today`, `datetime.date.today` y `time.time`. Excepciones por archivo: `simulador/reloj/infrastructure/` y el módulo de tokens (ver `docs/planes/autenticacion.md`). `time.monotonic` y `time.perf_counter` están permitidos: miden duraciones, no fechan datos.

## 4. El simulador

### 4.1 Archivo histórico

El simulador no lee los archivos del IDEAM tal como vienen. Lee un archivo **normalizado** que produce la tarea del perfil de datos (`tools/`), con estas columnas:

```
estacion,variable,inicio,valor
UPTC,PM10,2022-03-01T05:00:00Z,41.2
```

- `inicio` en UTC y en punto; `valor` vacío significa que la estación reportó sin valor.
- Sin duplicados por (estación, variable, inicio). El normalizador decide qué hacer con los duplicados del origen y lo deja escrito en el perfil.
- Ruta en la variable `SIM_HISTORICO`, fuera del repositorio.
- Se carga completo en memoria al arrancar, indexado por `inicio` (cinco años son unas 350 000 filas). Los valores se leen como `Decimal` desde el texto y se envían con los mismos dígitos: pasar por `float` puede cambiar el dato crudo.

```python
class ArchivoHistorico(Protocol):
    def registros(self, desde: datetime, hasta: datetime) -> list[Registro]: ...  # [desde, hasta)
    def cobertura(self) -> Cobertura: ...
    def ultimo_valor_antes(self, estacion, variable, t, max_horas=24) -> Decimal | None: ...
```

### 4.2 Fallas (dominio puro)

`aplicar_fallas(registros, fallas, variables) -> list[MedicionSalida]`. Una falla afecta a los registros de su estación y variable con `falla.inicio <= inicio < falla.fin`. Sin azar: el efecto depende solo del registro, de la falla y de la configuración.

| Tipo | Efecto | Parámetro |
|---|---|---|
| `FUERA_DE_RANGO` | `valor = maximo_fisico + margen` si `falla.id` es par; `minimo_fisico - margen` si es impar | `SIM_MARGEN_RANGO` = 100 |
| `VALOR_REPETIDO` | `valor = ultimo_valor_antes(falla.inicio)`. Si no hay ninguno en 24 h, se usa el primer valor no nulo del intervalo | — |
| `CAMBIO_BRUSCO` | `valor = min(valor + salto, maximo_fisico)`. Un valor nulo queda nulo | `SIM_SALTO` = 150 |
| `AUSENCIA_DE_DATO` | El registro se elimina del lote | — |

- Los registros alterados salen con `falla_id`. Los eliminados no salen.
- Dos fallas no pueden tocar el mismo registro: al crear el escenario se rechazan las que se solapan en la misma estación y variable (`FALLAS_SOLAPADAS` en `simulador.yaml`). `aplicar_fallas` lo da por cierto y falla con un error de programación si no se cumple.
- `CAMBIO_BRUSCO` se limita al máximo físico para que lo detecte su regla y no la de rango.
- Los valores por defecto de `SIM_SALTO` se revisan en el Sprint 2 junto con los umbrales de las reglas (`docs/planes/validacion.md`).

### 4.3 Bucle de reproducción (P-01)

Una tarea de `asyncio` por escenario en ejecución. `mi_epoca` es la época que devolvió el último `PUT /v1/reloj` del simulador.

```
t = (escenario.reloj_actual o escenario.periodo_inicio) + 1 h

mientras t <= periodo_fin:
    h = reloj.esperar(t, turno="simulador")
    si se pidió pausa o detención: salir del bucle
    si h.epoca != mi_epoca: reconfigurar el reloj (4.4) y continuar
    si h.ahora < t: continuar                      # venció la espera, volver a esperar

    registros = historico.registros(t - 1 h, t)
    fallas    = repo.fallas_que_tocan(escenario, t - 1 h, t)
    lote      = aplicar_fallas(registros, fallas, variables)

    si lote no está vacío:
        enviar(lote)                               # ver errores abajo
    en una sola transacción:
        fallas PROGRAMADA con inicio < t  ->  INYECTADA
        escenario.reloj_actual = t
    reloj.confirmar("simulador", t)
    t = t + 1 h

escenario -> FINALIZADO
```

**El orden enviar → guardar → confirmar es lo que da consistencia ante caídas:**

| Se cae después de… | Al reiniciar | Resultado |
|---|---|---|
| enviar, antes de guardar | reenvía la hora `t` | La ingesta las cuenta como duplicadas; no hay daño |
| guardar, antes de confirmar | reconfigura el reloj en `reloj_actual = t` | El reloj nace con `t` confirmada |

**Errores al enviar:**

- Error de red, 5xx o 503: reintentar con espera creciente (0,5 s hasta 30 s) mientras el escenario siga `EN_EJECUCION`. No se confirma, así que el reloj queda `RETENIDO` y no se pierde ninguna hora. Guardar el mensaje en `avance.ultimo_error`.
- 401: renovar el token una vez y reintentar.
- 400 o 413: es un defecto del simulador o del archivo, no algo pasajero. No reintentar: pausar el escenario y dejar el detalle en `ultimo_error`.
- Un lote vacío no se envía (el contrato exige al menos una medición), pero la hora sí se guarda y se confirma.

### 4.4 Control del escenario y recuperación

Transiciones de la Figura 16, validadas en `domain/escenario.py`:

| Operación | Pasos, en este orden |
|---|---|
| Iniciar | Comprobar que no hay otro activo → `PUT /v1/reloj` (`inicio = periodo_inicio`, `participantes` de la configuración) → estado `EN_EJECUCION` → lanzar la tarea |
| Pausar | Señalar a la tarea y esperar a que termine la hora en curso → `POST /v1/reloj/pausa` → estado `PAUSADO` |
| Reanudar | `PUT /v1/reloj` con `inicio = reloj_actual` → estado `EN_EJECUCION` → lanzar la tarea |
| Detener | Señalar a la tarea → `POST /v1/reloj/pausa` → estado `FINALIZADO` |

- Si la llamada al reloj falla, el estado del escenario no cambia y se responde 503. Por eso el reloj va antes que la base.
- Reanudar usa `PUT` y no `POST /reanudacion`: así el mismo camino sirve para una pausa normal y para una recuperación tras un reinicio.
- "Un solo escenario activo" se comprueba con `SELECT ... FOR UPDATE` dentro de la transacción de inicio.
- Lista de participantes: variable `SIM_PARTICIPANTES`, `simulador` en el Sprint 1 y `simulador,planificador` desde el Sprint 2.

**Al arrancar el simulador:** si hay un escenario `EN_EJECUCION`, ejecutar "Reanudar". Si hay uno `PAUSADO`, no hacer nada: el reloj ya arrancó congelado.

**Mantenerse despierto (ADR-0003):** en la nube gratuita un contenedor sin tráfico entrante se duerme a los 15 minutos, y el simulador solo hace llamadas salientes. Mientras haya un escenario `EN_EJECUCION`, una tarea llama cada 10 minutos a las URL de `SIM_MANTENER_DESPIERTOS` (la salud pública del propio simulador y la de `pronostico`). Sin la variable, no hace nada: en el compose no se necesita. Si aun así el proveedor reinicia un contenedor, aplica la recuperación de arriba.

**Primera llamada tras un arranque en frío:** tiempo límite de 120 s y los 502 o 503 del proveedor se tratan como error pasajero (misma rama de reintento que un 5xx).

## 5. El planificador (HU-16, Sprint 2)

Un bucle, sin base de datos y sin bibliotecas de planificación (ADR-0002).

```
bucle:
    h = reloj.hora()
    si h.epoca != epoca_vista: epoca_vista = h.epoca; siguiente = None
    si siguiente es None:
        VIRTUAL: siguiente = confirmada("planificador") + 1 h
        REAL:    siguiente = hora en punto posterior a h.ahora

    VIRTUAL: h = reloj.esperar(siguiente, turno="planificador")
             si h.epoca cambió o no se cumple la condición: continuar
    REAL:    h = reloj.esperar(siguiente + retraso)        # PLAN_RETRASO_REAL, 10 min
             si h.ahora < siguiente + retraso: continuar

    para cada proceso de la tabla, en orden:
        POST al servicio con {"hora": siguiente}; si falla, registrar y seguir
    reloj.confirmar("planificador", siguiente)
    siguiente = siguiente + 1 h
```

| Orden | Proceso | Servicio | Cuándo |
|---|---|---|---|
| 1 | P-04 Detección de ausencia | ingesta | Cada hora |
| 2 | P-06 Agregación | normativo | Cada hora (Sprint 3) |
| 3 | P-07 Evaluación normativa | normativo | Cada hora (Sprint 3) |
| 4 | P-08 Pronóstico | pronóstico | Cuando la hora local coincide con la configurada (Sprint 4) |

Reglas:

- **Los procesos son idempotentes por hora.** Reciben `{"hora": t}` y ejecutarlos dos veces para la misma `t` deja el mismo resultado. Es lo que permite reintentar y recuperarse sin estado propio. Es un requisito para los contratos de los Sprints 2 a 4.
- **Un fallo no detiene la hora** (RNF-15): se registra, se sigue con el siguiente proceso y se confirma igual. Tiempo límite por llamada configurable.
- Las llamadas son secuenciales: P-07 necesita los promedios de P-06.
- En modo `REAL`, el retraso da tiempo a que lleguen los datos de la hora. Las horas que pasen con el planificador caído o dormido no se recuperan solas. En la nube gratuita el núcleo se duerme sin tráfico, así que allí el modo `REAL` no garantiza los procesos horarios; es una limitación aceptada y documentada (ADR-0003, Consecuencias), porque la única fuente de datos es el simulador y en modo `VIRTUAL` todo está despierto.
- En reposo el planificador solo consulta el reloj, que no toca la base: así la base gratuita puede suspenderse.

## 6. Presupuesto de tiempo para RNF-11

205 ms reales por hora virtual. En el Sprint 1 cada hora cuesta una espera, un `POST` de lote (que dentro hace un `GET /v1/hora` y un `INSERT` de hasta ocho filas) y una confirmación. Con conexiones persistentes en la red interna debería quedar muy por debajo, pero hay que medirlo (HU-15), no suponerlo. Desde el Sprint 2 el presupuesto incluye la validación, y desde el 3 los tres procesos horarios: por eso HU-15 se repite al cerrar el Sprint 3.

Si no alcanza, el orden de ataque es: insertar el lote en una sola sentencia, mantener en memoria el catálogo de estaciones y variables en la ingesta, y solo al final revisar el número de llamadas por hora. No se toca la barrera: con ella, quedarse corto de velocidad da una reproducción más lenta, nunca un resultado distinto.

## 7. Pruebas

**Dominio del reloj** (sin red, con `mono` como número):

1. Avanza `velocidad` segundos virtuales por segundo.
2. Nunca supera la barrera; el estado es `RETENIDO` y `retenido_por` es correcto.
3. Tras estar retenido 10 s y recibir la confirmación, continúa desde la barrera y no salta.
4. En pausa no avanza; al reanudar no cuenta el tiempo pausado.
5. Llega a `fin`, queda `FINALIZADO` y no lo pasa aunque se confirme `fin`.
6. `confirmar` con hora futura falla; repetida o antigua no cambia nada.
7. Con dos participantes, la barrera sigue al más atrasado.
8. Propiedad: para cualquier secuencia de operaciones con `mono` creciente dentro de una época, `ahora` no decrece y nunca supera `barrera`.

**Servicio de reloj** (HTTP, reloj monótono falso):

9. `esperar_hasta` responde al llegar la hora, al cambiar la época y al vencer `espera_max`.
10. `turno_de=planificador` no responde hasta que `simulador` confirma.
11. Arranque con escenario `EN_EJECUCION` en la base: `VIRTUAL`, `PAUSADO`, en `reloj_actual`.
12. Arranque sin base disponible: el servicio no queda listo.
13. La época tras un reinicio es mayor que la anterior.
14. Concurrencia (HU-03): velocidad 100 000, un participante que tarda 50 ms por hora y cien lectores en paralelo; ninguna lectura supera la barrera vigente.

**Simulador:**

15. Una prueba por tipo de falla, más los bordes del intervalo `[inicio, fin)`.
16. Mismo escenario, dos ejecuciones: lotes idénticos.
17. Un mes sin fallas contra una ingesta real en contenedor: `medicion` tiene exactamente las filas del archivo.
18. La ingesta responde 503 tres veces y luego 202: no hay huecos ni duplicados y el reloj estuvo `RETENIDO`.
19. Matar el simulador en cada uno de los dos puntos de la tabla de 4.3 y reiniciar: la base final es igual a la de una ejecución sin caídas.
20. Reiniciar el reloj a mitad de la reproducción: el simulador detecta la época nueva y continúa.
21. Un 400 de la ingesta pausa el escenario y no se reintenta.

**Planificador** (reloj y servicios falsos):

22. Dispara una vez por hora y en orden, con el reloj acelerado y tras una pausa.
23. No dispara la hora `t` antes de la confirmación del simulador.
24. Un proceso que falla no impide los siguientes ni la confirmación.
25. Al cambiar la época recalcula `siguiente` desde las confirmaciones.

## 8. Orden de implementación

1. `servicios/comun`: `Reloj`, `RelojFalso`, modelo `Hora`, regla de ruff (HU-01).
2. Dominio del reloj con las pruebas 1 a 8 (HU-02, HU-03).
3. Servicio de reloj: API, espera, arranque (pruebas 9 a 14). `RelojHttp`.
4. Ingesta (HU-07 a HU-09) usando `RelojHttp`. No depende del simulador.
5. Simulador: histórico, fallas, control, bucle (HU-11 a HU-14).
6. Medición de RNF-11 (HU-15).
7. Sprint 2: planificador (HU-16) y `SIM_PARTICIPANTES=simulador,planificador`.

## 9. Lo que este plan no decide

- El formato de los archivos originales del IDEAM y cómo se normalizan: lo resuelve la tarea del perfil de datos.
- Las rutas exactas de los procesos que dispara el planificador: van en los contratos de los Sprints 2 a 4, con la regla de idempotencia de la sección 5.
- Los umbrales de las reglas de validación y, con ellos, el valor definitivo de `SIM_SALTO`.
