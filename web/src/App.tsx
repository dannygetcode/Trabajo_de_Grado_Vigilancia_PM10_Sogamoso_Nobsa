import { EstadoServicio } from "./componentes/EstadoServicio";
import { useSalud } from "./salud/useSalud";

const URL_NUCLEO = import.meta.env.VITE_URL_NUCLEO ?? "http://localhost:8000";
const URL_PRONOSTICO = import.meta.env.VITE_URL_PRONOSTICO ?? "http://localhost:8001";
const URL_SIMULADOR = import.meta.env.VITE_URL_SIMULADOR ?? "http://localhost:8002";

export function App() {
  const nucleo = useSalud(`${URL_NUCLEO}/salud`);
  const pronostico = useSalud(`${URL_PRONOSTICO}/v1/salud`);
  const simulador = useSalud(`${URL_SIMULADOR}/v1/salud`);
  return (
    <main>
      <h1>Calidad del aire Sogamoso-Nobsa</h1>
      <p>Sistema en construcción (Sprint 0). Estado de los servicios:</p>
      <ul className="servicios">
        <EstadoServicio nombre="Núcleo" estado={nucleo} />
        <EstadoServicio nombre="Pronóstico" estado={pronostico} />
        <EstadoServicio nombre="Simulador" estado={simulador} />
      </ul>
    </main>
  );
}
