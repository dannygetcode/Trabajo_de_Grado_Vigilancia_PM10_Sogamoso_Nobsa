-- Paquete de difusión: contactos, notificaciones e informes
SET search_path TO svca;

CREATE TABLE contacto (
  id       SERIAL PRIMARY KEY,
  nombre   VARCHAR(120) NOT NULL,
  entidad  VARCHAR(120) NOT NULL,
  correo   VARCHAR(160) NOT NULL UNIQUE,
  activo   BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE notificacion (
  id              BIGSERIAL PRIMARY KEY,
  contacto_id     INTEGER NOT NULL REFERENCES contacto (id),
  declaratoria_id BIGINT REFERENCES declaratoria (id),
  pronostico_id   BIGINT REFERENCES pronostico (id),
  asunto          VARCHAR(200) NOT NULL,
  cuerpo          TEXT NOT NULL,
  creada_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
  enviada_en      TIMESTAMPTZ,
  intentos        SMALLINT NOT NULL DEFAULT 0 CHECK (intentos BETWEEN 0 AND 3),
  estado          estado_notificacion NOT NULL DEFAULT 'PENDIENTE',
  CHECK (num_nonnulls(declaratoria_id, pronostico_id) = 1)
);

CREATE TABLE informe (
  id             SERIAL PRIMARY KEY,
  periodo_inicio DATE NOT NULL,
  periodo_fin    DATE NOT NULL,
  archivo_pdf    VARCHAR(200),
  generado_por   INTEGER NOT NULL REFERENCES usuario (id),
  generado_en    TIMESTAMPTZ NOT NULL DEFAULT now(),
  aprobado_por   INTEGER REFERENCES usuario (id),
  aprobado_en    TIMESTAMPTZ,
  observaciones  TEXT,
  estado         estado_informe NOT NULL DEFAULT 'EN_GENERACION',
  CHECK (periodo_inicio <= periodo_fin)
);
