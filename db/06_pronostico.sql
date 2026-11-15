-- Paquete de pronóstico: versiones del modelo, ciclos y pronósticos
SET search_path TO svca;

CREATE TABLE version_modelo (
  id              SERIAL PRIMARY KEY,
  algoritmo       VARCHAR(60) NOT NULL,
  ruta_artefacto  VARCHAR(200) NOT NULL,
  entrenada_en    TIMESTAMPTZ NOT NULL,
  mae_validacion  NUMERIC(8,3),
  rmse_validacion NUMERIC(8,3),
  estado          estado_version NOT NULL DEFAULT 'REGISTRADA'
);
-- Solo una versión del modelo puede estar activa a la vez
CREATE UNIQUE INDEX ux_version_activa ON version_modelo (estado)
  WHERE estado = 'ACTIVA';

CREATE TABLE ejecucion_ciclo (
  id            BIGSERIAL PRIMARY KEY,
  version_id    INTEGER REFERENCES version_modelo (id),
  inicio        TIMESTAMPTZ NOT NULL,
  fin           TIMESTAMPTZ,
  estado        estado_ejecucion NOT NULL DEFAULT 'EN_CURSO',
  entradas      JSONB,
  mensaje_error TEXT
);

CREATE TABLE pronostico (
  id              BIGSERIAL PRIMARY KEY,
  estacion_id     INTEGER NOT NULL REFERENCES estacion (id),
  version_id      INTEGER NOT NULL REFERENCES version_modelo (id),
  ejecucion_id    BIGINT  NOT NULL REFERENCES ejecucion_ciclo (id),
  emitido_en      TIMESTAMPTZ NOT NULL,
  horizonte_horas SMALLINT NOT NULL DEFAULT 24,
  categoria_ica   categoria_ica NOT NULL,
  supera_umbral   BOOLEAN NOT NULL DEFAULT false,
  estado          estado_pronostico NOT NULL DEFAULT 'EMITIDO',
  UNIQUE (estacion_id, emitido_en)
);

CREATE TABLE valor_pronosticado (
  id              BIGSERIAL PRIMARY KEY,
  pronostico_id   BIGINT NOT NULL REFERENCES pronostico (id),
  hora_objetivo   TIMESTAMPTZ NOT NULL,
  valor           NUMERIC(10,3) NOT NULL,
  limite_inferior NUMERIC(10,3) NOT NULL,
  limite_superior NUMERIC(10,3) NOT NULL,
  valor_observado NUMERIC(10,3),
  UNIQUE (pronostico_id, hora_objetivo),
  CHECK (limite_inferior <= valor AND valor <= limite_superior)
);
