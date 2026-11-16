# Plan: autenticación y autorización

- Historias: HU-04 (inicio de sesión y token), HU-05 (autorización en cada API). Sirve de base a HU-25 y HU-26 del Sprint 2.
- Contratos: `POST /v1/sesiones` en `docs/api/ingesta.yaml`; esquema `tokenPortador` en los tres archivos.
- Decisiones de base: ADR-0002 (RS256, la ingesta emite, hora real para los tokens). **Ajustes por ADR-0001 y ADR-0003:** no hay proxy, así que el límite de intentos por IP de `POST /v1/sesiones` se implementa dentro de la ingesta (contador en memoria, tomando la IP de `X-Forwarded-For` que pone el proveedor); la llave privada se configura solo en el contenedor `nucleo`; y `SVCA_JWT_PRIVADA` y `SVCA_JWT_PUBLICA` aceptan una ruta o el contenido PEM, porque en la nube llegan como variables de entorno. Donde este plan dice "en el proxy (HU-53)" debe leerse "en la ingesta".
- Requisitos: RF-14, RNF-05, RNF-17, RNF-18; CU-15.

## 1. Modelo de amenazas, en corto

| Qué puede pasar | Cómo se evita |
|---|---|
| Un componente externo fabrica un token con más permisos | Firma asimétrica: solo la ingesta tiene la llave privada. El simulador, que corre fuera del servidor, solo tiene la pública |
| Confusión de algoritmo (`alg: none`, o HS256 usando la llave pública como secreto) | La lista de algoritmos aceptados es fija en el código (`["RS256"]`); nunca se lee del token |
| Adivinar contraseñas por fuerza bruta | Bloqueo al quinto intento (RNF-17) y Argon2id |
| Averiguar qué cuentas existen | Misma respuesta y trabajo similar para cuenta inexistente, bloqueada o contraseña equivocada |
| Fuga de la base de datos | Solo hay resúmenes Argon2id; ningún secreto reversible |
| Contraseñas en registros | Nunca se registra el cuerpo de `POST /v1/sesiones` ni la cabecera `Authorization` |

Riesgos que se aceptan y quedan escritos:

- **No hay revocación.** Un token sigue siendo válido hasta que vence (60 minutos), aunque la cuenta se bloquee o cambie de rol. Los cambios de permisos surten efecto en el siguiente inicio de sesión.
- **El bloqueo sirve para negar el servicio.** Cualquiera que conozca un correo puede bloquear esa cuenta con cinco intentos, incluidas las de servicio. RNF-17 lo exige así. Se mitiga con un límite de peticiones por IP en el proxy (HU-53) y con la herramienta de desbloqueo de la sección 6.

## 2. Llaves

- RSA de 2048 bits, en formato PEM. Las genera `tools/generar_llaves.py` en `infra/secretos/` (`jwt_privada.pem`, `jwt_publica.pem`). Si los archivos ya existen, la herramienta no los sobrescribe.
- `.gitignore` ya excluye `infra/secretos/` y `*.pem`.
- En el compose, la privada se monta **solo** en el contenedor de ingesta; la pública, en todos.
- Variables: `SVCA_JWT_PRIVADA` (ruta, solo ingesta), `SVCA_JWT_PUBLICA` (ruta), `SVCA_JWT_DURACION_S` (3600).
- Un servicio que no encuentra su llave no arranca.

## 3. Token

Cabecera: `{"alg": "RS256", "typ": "JWT"}`.

| Campo | Valor |
|---|---|
| `iss` | `svca-ingesta` |
| `aud` | `svca` |
| `sub` | `usuario.id` como texto; `servicio:ingesta` para el token propio de la ingesta (sección 5) |
| `rol` | Nombre del rol |
| `permisos` | Copia de `rol.permisos` al iniciar sesión |
| `iat`, `exp` | Hora **real** en segundos Unix; `exp = iat + SVCA_JWT_DURACION_S` |
| `jti` | UUID aleatorio |

Verificación, igual en todos los servicios (`svca_comun.seguridad`):

- `algorithms=["RS256"]`, `issuer` y `audience` obligatorios, campos requeridos `exp`, `iat`, `sub`, `permisos`; margen de 30 s para desfases de reloj.
- Cualquier fallo responde 401 con `codigo: NO_AUTENTICADO` y la cabecera `WWW-Authenticate: Bearer`, sin decir cuál fue el fallo.
- La autorización mira la lista `permisos`, no el nombre del rol: así un rol nuevo no obliga a cambiar código (RF-15).

El módulo que firma y verifica es, junto con el servicio de reloj, la única excepción a la regla de ruff que prohíbe leer la hora del sistema (`docs/planes/reloj-virtual.md`, sección 3.7).

## 4. Inicio de sesión (`POST /v1/sesiones`)

Todo ocurre en una transacción. La fecha de la auditoría es la del reloj de dominio; por eso se consulta antes de tocar la base.

```
ahora = reloj.ahora()                      # si falla: 503 RELOJ_NO_DISPONIBLE
correo = normalizar(correo)                # sin espacios y en minúsculas
u = SELECT ... FROM usuario JOIN rol WHERE correo = :correo FOR UPDATE

si u no existe:
    verificar la contraseña contra un resumen de relleno     # trabajo similar
    auditar(usuario=NULL, LOGIN_FALLIDO, {"motivo": "cuenta_inexistente"})
    -> 401
si u.estado != ACTIVO:
    verificar contra el resumen de relleno
    auditar(u, LOGIN_FALLIDO, {"motivo": "cuenta_" + estado})
    -> 401
si la contraseña coincide:
    u.intentos_fallidos = 0
    si el resumen usa parámetros viejos: volver a resumir y guardar
    auditar(u, LOGIN_EXITOSO)
    -> 200 con el token
si no:
    u.intentos_fallidos += 1
    si u.intentos_fallidos >= 5: u.estado = BLOQUEADO
    auditar(u, LOGIN_FALLIDO, {"motivo": "contrasena", "intentos": n, "bloqueada": sí/no})
    -> 401
```

Detalles que importan:

- **`FOR UPDATE`** sobre la fila del usuario: sin él, diez intentos simultáneos leerían todos el mismo contador y la cuenta nunca llegaría a cinco.
- **La auditoría se confirma en la misma transacción** que el cambio del contador. Si el `INSERT` de auditoría falla, no hay token.
- **Los cuatro 401 son idénticos**: mismo código (`CREDENCIALES_INVALIDAS`), mismo mensaje, mismas cabeceras.
- **No se guarda el correo intentado** cuando la cuenta no existe: es frecuente que alguien escriba la contraseña en el campo equivocado.
- **Correos en minúsculas.** La restricción `UNIQUE` de `usuario.correo` distingue mayúsculas, así que todo lo que escribe en esa columna normaliza antes. Es una regla de `domain/`, no de la API.
- **Argon2id** con los parámetros por defecto de `argon2-cffi` (`PasswordHasher()`), que incluyen la sal y los parámetros dentro del propio resumen. Cabe en `VARCHAR(255)`.
- La verificación de Argon2 tarda decenas de milisegundos a propósito y bloquea el hilo: ejecutarla con `asyncio.to_thread` para no detener la ingesta de lotes mientras alguien inicia sesión.
- Contraseñas nuevas: mínimo 12 caracteres, máximo 200. La regla se aplica al crear o cambiar, no al iniciar sesión.

## 5. Cuentas de servicio

| Quién | Cómo obtiene su token | Rol |
|---|---|---|
| Simulador | Inicia sesión con correo y contraseña de su cuenta | `SIMULADOR` |
| Planificador, normativo, pronóstico, notificaciones | Igual | `SERVICIO` |
| Ingesta (para llamar al reloj y, desde el Sprint 2, al normativo) | Se firma su propio token con la llave privada, `sub = servicio:ingesta`, permiso `procesos_programados` | — |
| Reloj | No llama a nadie | — |

La ingesta no inicia sesión contra sí misma por HTTP: ya tiene la llave, y hacerlo crearía una dependencia circular al arrancar.

`svca_comun.sesion.SesionServicio`:

- Lee `SVCA_CUENTA_CORREO` y `SVCA_CUENTA_CONTRASENA` del entorno.
- Inicia sesión al primer uso, guarda el token y lo renueva cuando le quedan menos de cinco minutos (medidos con el reloj monótono) o cuando recibe un 401, una sola vez por petición.
- Reintenta con espera creciente si la ingesta aún no responde: los contenedores arrancan en cualquier orden.

Orden de arranque que resulta: reloj (solo necesita la llave pública y la base) → ingesta (necesita el reloj para auditar) → todo lo demás.

## 6. Primer administrador y herramientas

`tools/usuarios.py`, que se conecta directamente a la base con una credencial de administración:

```
python tools/usuarios.py crear --correo ... --nombre ... --rol ADMINISTRADOR
python tools/usuarios.py desbloquear --correo ...
```

- La contraseña se pide por teclado sin mostrarla, o se genera y se imprime una sola vez con `--generar`. Nunca va como argumento, porque quedaría en el historial de la terminal.
- `desbloquear` existe porque, si el único administrador se bloquea, no hay nadie que pueda desbloquearlo desde la web.
- Cada uso deja una fila en `registro_auditoria` con `usuario_id` nulo y la acción correspondiente. Es el único caso en que la fecha la pone la base (`DEFAULT now()`): la herramienta se ejecuta fuera del sistema y puede usarse con el reloj caído.
- No hay usuarios ni contraseñas por defecto en `db/` ni en el compose. El `.env.example` trae los nombres de las variables con valores vacíos.

## 7. Piezas en `servicios/comun`

```python
# svca_comun/seguridad.py
@dataclass(frozen=True)
class Identidad:
    sujeto: str                 # valor de sub
    usuario_id: int | None      # None si es un token de servicio propio
    rol: str | None
    permisos: frozenset[str]

class VerificadorTokens:        # se construye una vez con la llave pública
    def verificar(self, token: str) -> Identidad: ...

def requiere(permiso: str | None = None):   # dependencia de FastAPI
    """401 si no hay identidad válida; 403 si falta el permiso. None = basta un token válido."""
```

- Las rutas declaran su permiso de forma visible: `Depends(requiere("ingesta"))`. No hay un middleware global que decida por ruta.
- La `Identidad` llega hasta los casos de uso para escribir `usuario_id` en la auditoría y en `revision`.
- El emisor (`EmisorTokens`, firma con la privada) vive solo en `servicios/ingesta/infrastructure/`, no en `comun`.

**Formato de errores** (`svca_comun/errores.py`), que también forma parte del contrato:

- FastAPI responde 422 con su propio formato cuando la entrada no valida. Los contratos dicen 400 con `{codigo, mensaje, errores[]}`. Hay que registrar un manejador de `RequestValidationError` que traduzca al formato `Problema` con código `FORMATO` en cada error, y otro para las excepciones de dominio.
- Un manejador genérico responde 500 con `ERROR_INTERNO` sin trazas ni mensajes de la base.

## 8. Pruebas

**Token:**

1. Un token emitido se verifica y devuelve los permisos del rol.
2. Vencido: 401. Con `exp` dentro del margen de 30 s: se acepta.
3. Firmado con otra llave RSA: 401.
4. `alg: none`: 401.
5. HS256 firmado usando la llave pública como secreto: 401.
6. `iss` o `aud` distintos, o sin `permisos`: 401.
7. Carga modificada tras la firma (un permiso agregado): 401.

**Inicio de sesión** (contra PostgreSQL real):

8. Correcto: 200, contador en cero, fila `LOGIN_EXITOSO`.
9. Los cuatro casos de 401 devuelven cuerpos idénticos byte a byte.
10. Cinco fallos seguidos bloquean; el sexto intento, con la contraseña correcta, sigue en 401.
11. Cuatro fallos y un acierto dejan el contador en cero.
12. Veinte intentos fallidos simultáneos: el contador termina en 5 y la cuenta bloqueada (prueba del `FOR UPDATE`).
13. Con el reloj caído: 503 y ningún cambio en la base.
14. La fecha de la auditoría es la del reloj falso, no la del sistema.
15. `Usuario@Dominio.co` y `usuario@dominio.co` son la misma cuenta.
16. Ninguna línea de registro contiene la contraseña ni el token (se captura la salida de registro durante las pruebas y se busca).

**Autorización** (HU-05):

17. Por cada servicio, recorrer las rutas de su OpenAPI generado: sin token, todas responden 401 salvo `/v1/salud` y `POST /v1/sesiones`. La prueba se alimenta del OpenAPI, así que una ruta nueva sin protección la hace fallar.
18. Token válido sin el permiso de la ruta: 403.
19. Una entrada mal formada responde 400 con el formato `Problema`, no 422.

**Cuentas de servicio:**

20. `SesionServicio` renueva antes del vencimiento y tras un 401.
21. La ingesta arranca después que el cliente: el cliente reintenta y termina con sesión.

## 9. Orden de implementación

1. `tools/generar_llaves.py` y variables en `.env.example`.
2. `svca_comun.seguridad` y `svca_comun.errores` con las pruebas 1 a 7 y 17 a 19. El servicio de reloj ya puede protegerse.
3. Inicio de sesión en la ingesta (pruebas 8 a 16).
4. `tools/usuarios.py`.
5. `SesionServicio` (pruebas 20 y 21) y su uso en el simulador.

El paso 2 va antes que cualquier ruta de negocio: es más barato nacer protegido que proteger después.

## 10. Lo que queda para después

- Sprint 2: administración de usuarios (HU-26), sesión en la web (HU-25). El token se guarda en memoria del navegador, no en `localStorage`; se decide el detalle en ese sprint.
- Sprint 6: HTTPS y límite de peticiones por IP en el proxy para `POST /v1/sesiones` (HU-53).
- Si algún día hace falta revocar, la salida es acortar la duración y agregar un token de renovación; no una lista negra consultada en cada petición.
