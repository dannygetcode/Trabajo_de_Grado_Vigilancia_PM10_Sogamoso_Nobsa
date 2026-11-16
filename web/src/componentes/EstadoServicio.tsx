import type { EstadoConexion } from "../salud/consultar";

const TEXTO: Record<EstadoConexion, string> = {
  consultando: "consultando…",
  despertando: "despertando… (puede tardar hasta un minuto)",
  en_linea: "en línea",
  sin_respuesta: "sin respuesta",
};

const SIMBOLO: Record<EstadoConexion, string> = {
  consultando: "○",
  despertando: "◐",
  en_linea: "●",
  sin_respuesta: "✕",
};

interface Props {
  nombre: string;
  estado: EstadoConexion;
}

/** Muestra el estado con texto y símbolo, no solo con color (mismo criterio que RNF-14). */
export function EstadoServicio({ nombre, estado }: Props) {
  return (
    <li className={`servicio servicio--${estado}`} aria-live="polite">
      <span aria-hidden="true">{SIMBOLO[estado]}</span> <strong>{nombre}</strong>: {TEXTO[estado]}
    </li>
  );
}
