import { describe, expect, it } from "vitest";
import { consultarHastaResponder, type EstadoConexion, type OpcionesConsulta } from "./consultar";

/** Reloj falso: `esperar` avanza el tiempo al instante, en orden. */
function relojFalso() {
  let t = 0;
  const pendientes: { hasta: number; resolver: () => void }[] = [];
  return {
    ahora: () => t,
    esperar: (ms: number) =>
      new Promise<void>((resolver) => {
        pendientes.push({ hasta: t + ms, resolver });
        pendientes.sort((a, b) => a.hasta - b.hasta);
        const siguiente = pendientes.shift()!;
        t = Math.max(t, siguiente.hasta);
        siguiente.resolver();
      }),
    avanzar: (ms: number) => {
      t += ms;
    },
  };
}

function opciones(reloj: ReturnType<typeof relojFalso>): OpcionesConsulta {
  return { limiteMs: 90_000, avisoMs: 3_000, intervaloMs: 3_000, intentoMs: 10_000, ...reloj };
}

describe("consultarHastaResponder", () => {
  it("queda en línea si el primer intento responde", async () => {
    const reloj = relojFalso();
    const estados: EstadoConexion[] = [];
    const final = await consultarHastaResponder(async () => true, (e) => estados.push(e), opciones(reloj));
    expect(final).toBe("en_linea");
    expect(estados[0]).toBe("consultando");
    expect(estados).toContain("en_linea");
  });

  it("avisa que está despertando y queda en línea cuando el servicio responde", async () => {
    const reloj = relojFalso();
    const estados: EstadoConexion[] = [];
    let intentos = 0;
    const intento = async () => {
      intentos += 1;
      reloj.avanzar(10_000); // cada intento agota su tiempo, como un contenedor dormido
      return intentos >= 4;
    };
    const final = await consultarHastaResponder(intento, (e) => estados.push(e), opciones(reloj));
    expect(final).toBe("en_linea");
    expect(estados).toEqual(["consultando", "despertando", "en_linea"]);
    expect(reloj.ahora()).toBeLessThan(90_000);
  });

  it("se rinde al vencer el límite", async () => {
    const reloj = relojFalso();
    const estados: EstadoConexion[] = [];
    const intento = async (max: number) => {
      reloj.avanzar(max);
      return false;
    };
    const final = await consultarHastaResponder(intento, (e) => estados.push(e), opciones(reloj));
    expect(final).toBe("sin_respuesta");
    expect(estados.at(-1)).toBe("sin_respuesta");
    expect(reloj.ahora()).toBeLessThanOrEqual(90_000);
  });

  it("ningún intento pasa del tiempo que queda", async () => {
    const reloj = relojFalso();
    const pedidos: number[] = [];
    await consultarHastaResponder(
      async (max) => {
        pedidos.push(max);
        reloj.avanzar(max);
        return false;
      },
      () => {},
      { ...opciones(reloj), limiteMs: 25_000 },
    );
    expect(pedidos.reduce((a, b) => a + b, 0)).toBeLessThanOrEqual(25_000);
  });

  it("no reporta nada tras cancelarse", async () => {
    const reloj = relojFalso();
    const estados: EstadoConexion[] = [];
    let cancelado = false;
    await consultarHastaResponder(
      async () => {
        cancelado = true;
        return false;
      },
      (e) => estados.push(e),
      opciones(reloj),
      () => cancelado,
    );
    expect(estados).not.toContain("sin_respuesta");
  });
});
