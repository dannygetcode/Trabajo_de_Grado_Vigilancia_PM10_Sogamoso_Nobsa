-- Índices de consulta y vista de datos válidos (segunda base del protocolo)
SET search_path TO svca;

CREATE INDEX ix_medicion_estado ON medicion (estado)
  WHERE estado = 'SOSPECHOSO';
CREATE INDEX ix_medicion_serie ON medicion (estacion_id, variable_id, inicio);
CREATE INDEX ix_promedio_hora ON promedio_movil (hora_fin);
CREATE INDEX ix_valor_objetivo ON valor_pronosticado (hora_objetivo);
CREATE INDEX ix_auditoria_fecha ON registro_auditoria (fecha);

-- El valor efectivo es el de la última corrección o, si no la hay, el crudo
CREATE VIEW v_medicion_valida AS
SELECT m.id, m.estacion_id, m.variable_id, m.inicio, m.fin, m.estado,
       COALESCE(r.valor_nuevo, m.valor_crudo) AS valor
FROM medicion m
LEFT JOIN LATERAL (
  SELECT valor_nuevo FROM revision
  WHERE medicion_id = m.id AND accion = 'CORREGIR'
  ORDER BY fecha DESC LIMIT 1
) r ON true
WHERE m.estado IN ('VALIDO', 'VALIDADO_MANUAL', 'CORREGIDO');

-- El valor crudo de una medición nunca se modifica (RF-04)
CREATE FUNCTION fn_proteger_valor_crudo() RETURNS trigger AS $$
BEGIN
  IF NEW.valor_crudo IS DISTINCT FROM OLD.valor_crudo THEN
    RAISE EXCEPTION 'El valor crudo de la medición % no se puede modificar',
      OLD.id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_proteger_valor_crudo
  BEFORE UPDATE ON medicion
  FOR EACH ROW EXECUTE FUNCTION fn_proteger_valor_crudo();
