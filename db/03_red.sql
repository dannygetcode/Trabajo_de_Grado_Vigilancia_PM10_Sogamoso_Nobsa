-- Paquete de red de monitoreo: estaciones, variables y mantenimientos
SET search_path TO svca;

CREATE TABLE estacion (
  id         SERIAL PRIMARY KEY,
  codigo     VARCHAR(20) NOT NULL UNIQUE,
  nombre     VARCHAR(80) NOT NULL,
  municipio  VARCHAR(60) NOT NULL,
  latitud    NUMERIC(9,6) NOT NULL CHECK (latitud BETWEEN -90 AND 90),
  longitud   NUMERIC(9,6) NOT NULL CHECK (longitud BETWEEN -180 AND 180),
  altitud    INTEGER,
  estado     estado_estacion NOT NULL DEFAULT 'OPERATIVA'
);

CREATE TABLE variable (
  id            SMALLSERIAL PRIMARY KEY,
  codigo        VARCHAR(20) NOT NULL UNIQUE,
  nombre        VARCHAR(80) NOT NULL,
  unidad        VARCHAR(20) NOT NULL,
  minimo_fisico NUMERIC(10,3) NOT NULL,
  maximo_fisico NUMERIC(10,3) NOT NULL,
  CHECK (minimo_fisico < maximo_fisico)
);

CREATE TABLE estacion_variable (
  estacion_id  INTEGER  NOT NULL REFERENCES estacion (id),
  variable_id  SMALLINT NOT NULL REFERENCES variable (id),
  PRIMARY KEY (estacion_id, variable_id)
);

CREATE TABLE periodo_mantenimiento (
  id           SERIAL PRIMARY KEY,
  estacion_id  INTEGER NOT NULL REFERENCES estacion (id),
  inicio       TIMESTAMPTZ NOT NULL,
  fin          TIMESTAMPTZ NOT NULL,
  motivo       VARCHAR(200) NOT NULL,
  CHECK (inicio < fin)
);
