-- Paquete normativo: parámetros, evaluaciones y declaratorias
SET search_path TO svca;

CREATE TABLE parametro_normativo (
  id             SERIAL PRIMARY KEY,
  variable_id    SMALLINT NOT NULL REFERENCES variable (id),
  nivel          nivel_normativo NOT NULL,
  umbral_min     NUMERIC(10,3) NOT NULL,
  umbral_max     NUMERIC(10,3),
  ventana_horas  SMALLINT NOT NULL DEFAULT 24,
  vigente_desde  DATE NOT NULL,
  vigente_hasta  DATE,
  CHECK (umbral_max IS NULL OR umbral_min < umbral_max)
);

CREATE TABLE evaluacion_normativa (
  id                  BIGSERIAL PRIMARY KEY,
  variable_id         SMALLINT NOT NULL REFERENCES variable (id),
  parametro_id        INTEGER REFERENCES parametro_normativo (id),
  fecha_hora          TIMESTAMPTZ NOT NULL,
  nivel_propuesto     nivel_normativo,
  cobertura_pct       NUMERIC(5,2) NOT NULL
                      CHECK (cobertura_pct BETWEEN 0 AND 100),
  porcentaje_en_rango NUMERIC(5,2),
  UNIQUE (variable_id, fecha_hora)
);

CREATE TABLE evaluacion_promedio (
  evaluacion_id BIGINT NOT NULL REFERENCES evaluacion_normativa (id),
  promedio_id   BIGINT NOT NULL REFERENCES promedio_movil (id),
  PRIMARY KEY (evaluacion_id, promedio_id)
);

CREATE TABLE declaratoria (
  id              BIGSERIAL PRIMARY KEY,
  nivel           nivel_normativo NOT NULL,
  origen          origen_declaratoria NOT NULL,
  evaluacion_id   BIGINT REFERENCES evaluacion_normativa (id),
  pronostico_id   BIGINT REFERENCES pronostico (id),
  estado          estado_declaratoria NOT NULL DEFAULT 'PROPUESTA',
  soporte_tecnico TEXT,
  propuesta_en    TIMESTAMPTZ NOT NULL DEFAULT now(),
  decidida_por    INTEGER REFERENCES usuario (id),
  decidida_en     TIMESTAMPTZ,
  cerrada_en      TIMESTAMPTZ,
  CHECK ((origen = 'MEDICION' AND evaluacion_id IS NOT NULL)
      OR (origen = 'PRONOSTICO' AND pronostico_id IS NOT NULL)),
  CHECK (estado = 'PROPUESTA' OR decidida_por IS NOT NULL)
);

CREATE TABLE declaratoria_estacion (
  declaratoria_id BIGINT  NOT NULL REFERENCES declaratoria (id),
  estacion_id     INTEGER NOT NULL REFERENCES estacion (id),
  PRIMARY KEY (declaratoria_id, estacion_id)
);
