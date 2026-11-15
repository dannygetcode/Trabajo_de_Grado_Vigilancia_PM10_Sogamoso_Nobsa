-- Paquete de seguridad: roles, usuarios y auditoría
SET search_path TO svca;

CREATE TABLE rol (
  id        SMALLSERIAL PRIMARY KEY,
  nombre    VARCHAR(30) NOT NULL UNIQUE,
  permisos  TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE usuario (
  id                 SERIAL PRIMARY KEY,
  rol_id             SMALLINT NOT NULL REFERENCES rol (id),
  nombre             VARCHAR(120) NOT NULL,
  correo             VARCHAR(160) NOT NULL UNIQUE,
  hash_contrasena    VARCHAR(255) NOT NULL,
  intentos_fallidos  SMALLINT NOT NULL DEFAULT 0
                     CHECK (intentos_fallidos BETWEEN 0 AND 5),
  estado             estado_usuario NOT NULL DEFAULT 'ACTIVO',
  creado_en          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE registro_auditoria (
  id          BIGSERIAL PRIMARY KEY,
  usuario_id  INTEGER REFERENCES usuario (id),
  fecha       TIMESTAMPTZ NOT NULL DEFAULT now(),
  accion      VARCHAR(60) NOT NULL,
  entidad     VARCHAR(60) NOT NULL,
  id_entidad  BIGINT,
  detalle     JSONB
);
