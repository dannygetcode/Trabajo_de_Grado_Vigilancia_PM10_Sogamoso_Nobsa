/**
 * Consulta un servicio que puede estar dormido (ADR-0003: en la nube gratuita un contenedor
 * tarda cerca de un minuto en despertar). Reintenta hasta `limiteMs` y avisa en qué estado está.
 *
 * Es lógica pura: el reloj y la espera se inyectan, así las pruebas no esperan de verdad.
 * Mide duraciones, no fecha datos; por eso usa un reloj monótono y no la hora de dominio.
 */
export type EstadoConexion = "consultando" | "despertando" | "en_linea" | "sin_respuesta";

export interface OpcionesConsulta {
  /** Tiempo total antes de rendirse. */
  limiteMs: number;
  /** Si no hay respuesta en este tiempo, se avisa que el servicio está despertando. */
  avisoMs: number;
  /** Espera entre intentos fallidos. */
  intervaloMs: number;
  /** Tiempo máximo de cada intento. */
  intentoMs: number;
  ahora: () => number;
  esperar: (ms: number) => Promise<void>;
}

export const OPCIONES_POR_DEFECTO: Omit<OpcionesConsulta, "ahora" | "esperar"> = {
  limiteMs: 90_000,
  avisoMs: 3_000,
  intervaloMs: 3_000,
  intentoMs: 10_000,
};

/** Un intento: resuelve true si el servicio respondió bien, false si no; nunca lanza. */
export type Intento = (tiempoMaximoMs: number) => Promise<boolean>;

export async function consultarHastaResponder(
  intento: Intento,
  alCambiar: (estado: EstadoConexion) => void,
  opciones: OpcionesConsulta,
  cancelado: () => boolean = () => false,
): Promise<EstadoConexion> {
  const inicio = opciones.ahora();
  let estado: EstadoConexion = "consultando";
  alCambiar(estado);
  const pasar = (nuevo: EstadoConexion) => {
    if (nuevo !== estado) {
      estado = nuevo;
      alCambiar(estado);
    }
  };
  const aviso = opciones.esperar(opciones.avisoMs).then(() => {
    if (estado === "consultando" && !cancelado()) pasar("despertando");
  });
  void aviso;

  while (!cancelado()) {
    const restante = opciones.limiteMs - (opciones.ahora() - inicio);
    if (restante <= 0) break;
    if (await intento(Math.min(opciones.intentoMs, restante))) {
      pasar("en_linea");
      return estado;
    }
    pasar("despertando");
    const tras = opciones.limiteMs - (opciones.ahora() - inicio);
    if (tras <= 0) break;
    await opciones.esperar(Math.min(opciones.intervaloMs, tras));
  }
  if (!cancelado()) pasar("sin_respuesta");
  return estado;
}

/** Intento real con fetch: responde true con un 200 de la ruta de salud. */
export function intentoHttp(url: string): Intento {
  return async (tiempoMaximoMs) => {
    const control = new AbortController();
    const temporizador = setTimeout(() => control.abort(), tiempoMaximoMs);
    try {
      const r = await fetch(url, { signal: control.signal, headers: { Accept: "application/json" } });
      return r.ok;
    } catch {
      return false;
    } finally {
      clearTimeout(temporizador);
    }
  };
}
