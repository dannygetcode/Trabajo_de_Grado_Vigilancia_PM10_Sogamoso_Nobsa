-- Datos iniciales: roles, variables, estaciones del caso de estudio y
-- niveles de declaratoria para PM10 (Resolución 2254 de 2017)
SET search_path TO svca;

INSERT INTO rol (nombre, permisos) VALUES
  ('ADMINISTRADOR', '{usuarios,estaciones,parametros,simulacion}'),
  ('TECNICO',       '{revisar,consultar_red,exportar}'),
  ('COORDINADOR',   '{declaratorias,desempeno,informes}'),
  ('CONSULTA',      '{consultar_lectura}'),
  ('SERVICIO',      '{ingesta,procesos_programados}');

INSERT INTO variable (codigo, nombre, unidad, minimo_fisico, maximo_fisico)
VALUES ('PM10',  'Material particulado PM10',  'µg/m³', 0, 1000),
       ('PM2.5', 'Material particulado PM2.5', 'µg/m³', 0, 1000);

INSERT INTO estacion (codigo, nombre, municipio, latitud, longitud, altitud)
VALUES ('UPTC',      'UPTC',               'Sogamoso', 5.704583, -72.942778, 2523),
       ('RECREO',    'El Recreo',          'Sogamoso', 5.726272, -72.920917, 2483),
       ('SENA',      'SENA',               'Sogamoso', 5.757111, -72.908528, 2477),
       ('NAZARET',   'Nazaret',            'Nobsa',    5.766117, -72.897008, 2479),
       ('BOMBEROS',  'Bomberos (Móvil 1)', 'Nobsa',    5.770928, -72.937972, 2499);

-- PM10 en las cinco estaciones y PM2.5 en El Recreo, Nazaret y Bomberos
INSERT INTO estacion_variable (estacion_id, variable_id)
SELECT e.id, v.id FROM estacion e, variable v
WHERE v.codigo = 'PM10'
   OR (v.codigo = 'PM2.5' AND e.codigo IN ('RECREO', 'NAZARET', 'BOMBEROS'));

INSERT INTO parametro_normativo
  (variable_id, nivel, umbral_min, umbral_max, ventana_horas, vigente_desde)
SELECT v.id, p.nivel::nivel_normativo, p.umin, p.umax, 24, DATE '2017-11-01'
FROM variable v,
     (VALUES ('PREVENCION', 155, 254), ('ALERTA', 255, 354),
             ('EMERGENCIA', 355, NULL)) AS p (nivel, umin, umax)
WHERE v.codigo = 'PM10';
