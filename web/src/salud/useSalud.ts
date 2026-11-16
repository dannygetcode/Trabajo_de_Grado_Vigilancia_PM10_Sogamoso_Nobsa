import { useEffect, useState } from "react";
import {
  consultarHastaResponder,
  intentoHttp,
  OPCIONES_POR_DEFECTO,
  type EstadoConexion,
  type Intento,
} from "./consultar";

const esperarReal = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

/** Estado de conexión de un servicio; se reutiliza en toda la web antes de pedir datos. */
export function useSalud(url: string, intento: Intento = intentoHttp(url)): EstadoConexion {
  const [estado, setEstado] = useState<EstadoConexion>("consultando");
  useEffect(() => {
    let cancelado = false;
    void consultarHastaResponder(
      intento,
      (e) => {
        if (!cancelado) setEstado(e);
      },
      { ...OPCIONES_POR_DEFECTO, ahora: () => performance.now(), esperar: esperarReal },
      () => cancelado,
    );
    return () => {
      cancelado = true;
    };
    // El intento se crea por URL; cambiar la URL reinicia la consulta.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);
  return estado;
}
