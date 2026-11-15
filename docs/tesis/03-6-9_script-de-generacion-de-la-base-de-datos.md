<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. No editar a mano: editar el Word y regenerar. -->

### 3.6.9 Script de generación de la base de datos

El script de generación se organiza en diez archivos que se ejecutan en orden numérico, porque cada uno depende de las tablas creadas por los anteriores. Se probó en PostgreSQL 16 sobre una base vacía. Las 24 tablas se crearon sin errores y se verificó que la base rechaza la modificación de un valor crudo, una revisión sin justificación, una corrección sin valor nuevo, una medición duplicada, una segunda versión activa del modelo y una declaratoria por pronóstico sin pronóstico asociado. La ejecución completa se hace con el comando psql -f sobre cada archivo o con el archivo de orquestación del repositorio.

> Script completo en [`db/01_tipos.sql`](../../db/01_tipos.sql).

> Script completo en [`db/02_seguridad.sql`](../../db/02_seguridad.sql).

> Script completo en [`db/03_red.sql`](../../db/03_red.sql).

> Script completo en [`db/04_simulacion.sql`](../../db/04_simulacion.sql).

> Script completo en [`db/05_datos.sql`](../../db/05_datos.sql).

> Script completo en [`db/06_pronostico.sql`](../../db/06_pronostico.sql).

> Script completo en [`db/07_normativo.sql`](../../db/07_normativo.sql).

> Script completo en [`db/08_difusion.sql`](../../db/08_difusion.sql).

> Script completo en [`db/09_vistas_indices.sql`](../../db/09_vistas_indices.sql).

> Script completo en [`db/10_datos_iniciales.sql`](../../db/10_datos_iniciales.sql).
