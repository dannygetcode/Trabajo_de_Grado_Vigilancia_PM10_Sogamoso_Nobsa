-- Paquete de datos: mediciones crudas, revisiones y promedios móviles
SET search_path TO svca;

CREATE TABLE medicion (
  id             BIGSERIAL PRIMARY KEY,
  estacion_id    INTEGER  NOT NULL REFERENCES estacion (id),
  variable_id    SMALLINT NOT NULL REFERENCES variable (id),
  falla_id       INTEGER  REFERENCES falla_inyectada (id),
  inicio         TIMESTAMPTZ NOT NULL,
  fin            TIMESTAMPTZ NOT NULL,
  valor_crudo    NUMERIC(10,3),
  estado         estado_medicion NOT NULL DEFAULT 'CRUDO',
  regla_aplicada VARCHAR(40),
  recibida_en    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (estacion_id, variable_id, inicio),
  CHECK (inicio < fin)
);

CREATE TABLE revision (
  id             BIGSERIAL PRIMARY KEY,
  medicion_id    BIGINT  NOT NULL REFERENCES medicion (id),
  usuario_id     INTEGER NOT NULL REFERENCES usuario (id),
  accion         accion_revision NOT NULL,
  valor_anterior NUMERIC(10,3),
  valor_nuevo    NUMERIC(10,3),
  justificacion  TEXT NOT NULL CHECK (length(trim(justificacion)) > 0),
  fecha          TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (accion <> 'CORREGIR' OR valor_nuevo IS NOT NULL)
);

CREATE TABLE promedio_movil (
  id            BIGSERIAL PRIMARY KEY,
  estacion_id   INTEGER  NOT NULL REFERENCES estacion (id),
  variable_id   SMALLINT NOT NULL REFERENCES variable (id),
  hora_fin      TIMESTAMPTZ NOT NULL,
  valor_24h     NUMERIC(10,3),
  horas_validas SMALLINT NOT NULL CHECK (horas_validas BETWEEN 0 AND 24),
  representativo BOOLEAN GENERATED ALWAYS AS (horas_validas >= 18) STORED,
  UNIQUE (estacion_id, variable_id, hora_fin)
);
