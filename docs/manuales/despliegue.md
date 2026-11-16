# Manual de despliegue en la nube gratuita

Para el autor. Despliega el esqueleto del Sprint 0 y deja todo listo para que cada sprint termine en línea. Las decisiones y los límites de cada plan están en [ADR-0003](../adr/0003-despliegue-gratuito.md).

Reglas para todo el proceso:

- **Si alguna cuenta pide tarjeta, detente.** No la registres: anota en `docs/ESTADO.md` qué servicio la pidió y se revisa ADR-0003 antes de seguir.
- Ningún secreto se escribe en el repositorio, ni en un commit, ni en un issue. Solo van en el panel del proveedor o en los secretos de GitHub.
- Al crear cada cuenta, compara sus límites con la tabla de ADR-0003. Si alguno difiere (horas, almacenamiento, correos al día), anótalo en `docs/ESTADO.md` antes de seguir.

## 1. Base de datos en Neon

1. Crea la cuenta en <https://neon.com> con el plan Free.
2. Crea un proyecto `svca` con **PostgreSQL 16** en la región **AWS US East (N. Virginia), `aws-us-east-1`**: la más cercana a la región `virginia` de Render.
3. En *Connection details*, activa **Connection pooling** y copia la cadena. El host lleva `-pooler`. Añade al final `?sslmode=verify-full` (o cambia `sslmode=require` por `verify-full`). Esta es la **URL de la base** de los pasos siguientes.
4. Comprueba desde tu equipo que la herramienta de migración llega a la base, sin aplicar nada todavía:

   ```bash
   uv run python tools/db_aplicar.py --url "<URL de la base>" --hasta 0
   ```

   Debe responder "Nada que aplicar". Esto solo crea el esquema `svca_meta`. Los scripts de `db/` los aplica CI en el paso 3.

## 2. Servicios en Render

1. Crea la cuenta en <https://render.com> (plan Hobby, gratuito) y conecta GitHub con acceso **solo** a este repositorio.
2. *New → Blueprint*, elige el repositorio y la rama `main`, y como ruta del Blueprint indica `infra/render.yaml`. Si Render no permite cambiar la ruta, mueve el archivo a la raíz del repositorio (en una rama y con PR) y anótalo en `docs/ESTADO.md`.
3. Render pide los valores marcados con `sync: false`. La primera vez algunos dependen de URL que aún no existen. Llena primero lo que ya sabes y vuelve después a completar el resto:

   | Servicio | Variable | Valor |
   |---|---|---|
   | svca-nucleo, svca-pronostico, svca-simulador | `SVCA_DB_URL` | URL de la base (paso 1.3) |
   | svca-nucleo, svca-pronostico, svca-simulador | `SVCA_ORIGENES` | `https://svca-web.onrender.com` (o la que asigne Render) |
   | svca-nucleo | `SVCA_CORREO_REDIRIGIR_A` | vacío por ahora (Sprint 5) |
   | svca-simulador | `SVCA_URL_NUCLEO` | `https://svca-nucleo.onrender.com` |
   | svca-simulador | `SIM_MANTENER_DESPIERTOS` | vacío por ahora (Sprint 1) |
   | svca-web | `VITE_URL_NUCLEO`, `VITE_URL_PRONOSTICO`, `VITE_URL_SIMULADOR` | URL públicas de los tres servicios, sin `/` final |

4. Comprueba en el panel que los cuatro servicios son del plan **Free** y que la web es un **Static Site**.
5. Hay dos puntos del Blueprint que no se pudieron confirmar en la documentación (`infra/render.yaml`, comentarios "a verificar"). Revísalos tras el primer despliegue:
   - Abre `https://svca-web.onrender.com/cualquier/ruta`: debe mostrar la página, no un 404. Si da 404, crea a mano la regla *Rewrite* `/*` → `/index.html` en *Redirects/Rewrites* y anota el nombre correcto de los campos.
   - La página debe mostrar los tres servicios "en línea". Si dice "sin respuesta" y las URL públicas sí responden, las variables `VITE_*` no llegaron a la construcción.

## 3. Secretos y variables de GitHub

En el repositorio: *Settings → Secrets and variables → Actions*.

- **Secrets:** `SVCA_NUBE_DB_URL` con la URL de la base. Con él, el trabajo `migrar` de CI aplica `db/` en Neon cada vez que se integra en `main`.
- **Variables:** `SVCA_NUBE_URL_NUCLEO`, `SVCA_NUBE_URL_PRONOSTICO`, `SVCA_NUBE_URL_SIMULADOR` y `SVCA_NUBE_URL_WEB`, con las URL públicas. Las usa el flujo *Humo en la nube*.

Después, en *Actions → Humo en la nube → Run workflow*, lánzalo a mano una vez. Debe quedar en verde. Puede tardar unos minutos si los contenedores estaban dormidos.

## 4. Correo en Brevo (puede esperar al Sprint 5)

1. Crea la cuenta gratuita en <https://www.brevo.com>.
2. En *Senders*, agrega y verifica la dirección remitente. No hace falta dominio propio.
3. Crea una clave de la API transaccional. Se guardará como variable de Render del núcleo cuando exista el adaptador (HU-46). No la escribas en ningún otro sitio.

## 5. Comprobación final

- [ ] Ninguna cuenta pidió tarjeta.
- [ ] Los límites coinciden con ADR-0003, o las diferencias quedaron en `docs/ESTADO.md`.
- [ ] `https://svca-nucleo.onrender.com/salud?profundo=true` responde 200, con `"base": "ok"` en cada servicio.
- [ ] `/v1/salud?profundo=true` de pronóstico y simulador responde 200.
- [ ] La página estática muestra los tres servicios "en línea".
- [ ] *Humo en la nube* en verde.
- [ ] Las URL públicas quedaron anotadas en `docs/ESTADO.md`.

## Qué esperar del plan gratuito

- **La primera petición tras 15 minutos sin tráfico tarda cerca de un minuto**: el contenedor está despertando. La web lo indica con "despertando…".
- La base de Neon se suspende a los 5 minutos sin consultas y despierta en menos de un segundo.
- **Antes de una demostración:** abre la web diez minutos antes y llama a las tres saludes. Desde el Sprint 1, deja corriendo un escenario: el simulador mantiene todo despierto mientras reproduce.
- **No dejes escenarios largos en la nube a velocidad 1:** tres servicios despiertos agotan las 750 horas mensuales en unos diez días. Esos escenarios se corren en el compose.
