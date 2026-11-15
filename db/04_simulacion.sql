-- Paquete de simulación: escenarios de reproducción y fallas inyectadas
SET search_path TO svca;

CREATE TABLE escenario_simulacion (
  id              SERIAL PRIMARY KEY,
  nombre          VARCHAR(80) NOT NULL,
  periodo_inicio  TIMESTAMPTZ NOT NULL,
  periodo_fin     TIMESTAMPTZ NOT NULL,
  velocidad_reloj NUMERIC(8,2) NOT NULL DEFAULT 1 CHECK (velocidad_reloj > 0),
  reloj_actual    TIMESTAMPTZ,
  estado          estado_escenario NOT NULL DEFAULT 'CONFIGURADO',
  CHECK (periodo_inicio < periodo_fin)
);

CREATE TABLE falla_inyectada (
  id           SERIAL PRIMARY KEY,
  escenario_id INTEGER  NOT NULL REFERENCES escenario_simulacion (id),
  estacion_id  INTEGER  NOT NULL REFERENCES estacion (id),
  variable_id  SMALLINT NOT NULL REFERENCES variable (id),
  tipo         tipo_falla NOT NULL,
  inicio       TIMESTAMPTZ NOT NULL,
  fin          TIMESTAMPTZ NOT NULL,
  estado       estado_falla NOT NULL DEFAULT 'PROGRAMADA',
  CHECK (inicio < fin)
);
