import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EstadoServicio } from "./EstadoServicio";

describe("EstadoServicio", () => {
  it.each([
    ["en_linea", "en línea"],
    ["despertando", "despertando"],
    ["sin_respuesta", "sin respuesta"],
  ] as const)("muestra %s con texto, no solo con color", (estado, texto) => {
    render(<EstadoServicio nombre="Núcleo" estado={estado} />);
    expect(screen.getByRole("listitem")).toHaveTextContent(new RegExp(`Núcleo: ${texto}`));
  });
});
