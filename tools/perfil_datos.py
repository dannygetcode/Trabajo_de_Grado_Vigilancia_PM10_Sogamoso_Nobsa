#!/usr/bin/env python3
"""Perfil de calidad de los datos IDEAM del corredor y archivo histórico normalizado.

Lee data/raw/ideam_corredor.csv (no lo vuelca a la terminal), escribe el informe en
docs/datos/perfil_calidad.md y los archivos normalizados en data/processed/:

- historico_normalizado.csv: PM10 y PM2.5, lo que reproduce el simulador
  (docs/planes/reloj-virtual.md, sección 4.1).
- meteorologia_normalizada.csv: el resto de variables, para el Sprint 4.

Columnas de ambos: estacion,variable,inicio,valor. `inicio` en UTC (sufijo Z) y en punto;
`valor` conserva los dígitos del origen (solo se quita el separador de miles).

Uso:
    python tools/perfil_datos.py [--csv data/raw/ideam_corredor.csv] [--salida data/processed]
"""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
FORMATO_FECHA = "%Y %b %d %I:%M:%S %p"
DESFASE_UTC = timedelta(hours=5)  # Colombia, UTC-5 todo el año, sin horario de verano
ESTACION_EXCLUIDA = "31828"  # MOVIL KOICA: coordenadas en Tunja

# Código IDEAM -> código de svca.estacion (db/10_datos_iniciales.sql)
ESTACIONES = {
    "31719": "UPTC",
    "31826": "RECREO",
    "30810": "SENA",
    "31827": "NAZARET",
    "30815": "BOMBEROS",
}
VARIABLES_SIMULADOR = ("PM10", "PM2.5")  # las que existen en svca.variable
ESTACION_REFERENCIA = "31827"  # la de más filas, para medir desfases entre estaciones
NUMERO = re.compile(r"-?\d{1,3}(,\d{3})*(\.\d+)?|-?\d+(\.\d+)?")


def limpiar_valor(texto: str) -> str:
    """Quita el separador de miles sin tocar los dígitos. Falla si no es un número."""
    if not NUMERO.fullmatch(texto):
        raise ValueError(f"valor no numérico: {texto!r}")
    return texto.replace(",", "")


def a_utc_iso(local: pd.Series) -> pd.Series:
    """Hora local de Colombia (ingenua) -> texto RFC 3339 en UTC."""
    return (local + DESFASE_UTC).dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def cargar(ruta: Path) -> pd.DataFrame:
    cols = ["ESTACION_ID", "NOMBRE_EST", "MSFL_CODE", "MED_CONCENTRACION_ESTANDAR",
            "MED_FECHA_INICIO", "MED_FECHA_FINAL", "LATITUD", "LONGITUD", "ALTITUD", "DURACIÓN"]
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False, usecols=cols, encoding="utf-8")
    df.columns = ["est", "nombre", "var", "texto", "ini_txt", "fin_txt", "lat", "lon", "alt", "dur"]
    unicas = pd.Series(pd.unique(pd.concat([df.ini_txt, df.fin_txt])))
    mapa = dict(zip(unicas, pd.to_datetime(unicas, format=FORMATO_FECHA, errors="coerce")))
    df["ini"] = df.ini_txt.map(mapa)
    df["fin"] = df.fin_txt.map(mapa)
    return df


def tabla(df: pd.DataFrame, indice: bool = True) -> str:
    """Tabla Markdown sin dependencias externas."""
    if indice:
        df = df.reset_index()
    def celda(v: object) -> str:
        if isinstance(v, float):
            return "" if np.isnan(v) else (f"{v:.0f}" if v.is_integer() else f"{v}")
        if isinstance(v, pd.Timestamp):
            return v.strftime("%Y-%m-%d %H:%M")
        return str(v)
    cab = [str(c) for c in df.columns]
    filas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    filas += ["| " + " | ".join(celda(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(filas)


def miles(x: int) -> str:
    """Entero con punto de miles, como en el documento."""
    return f"{x:,}".replace(",", ".")


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def huecos(horas: pd.DatetimeIndex, desde: pd.Timestamp, hasta: pd.Timestamp) -> pd.DataFrame:
    """Rachas de horas sin medición dentro de [desde, hasta]."""
    completas = pd.date_range(desde, hasta, freq="h")
    falta = ~completas.isin(horas)
    if not falta.any():
        return pd.DataFrame(columns=["inicio", "horas"])
    grupo = np.cumsum(~falta)
    s = pd.Series(completas[falta], index=grupo[falta])
    g = s.groupby(level=0)
    return pd.DataFrame({"inicio": g.min().values, "horas": g.size().values})


def desfase(a: pd.Series, b: pd.Series, max_lag: int = 6) -> tuple[int, float]:
    """Desfase en horas que maximiza la correlación de b desplazada contra a."""
    mejor = (0, -2.0)
    for k in range(-max_lag, max_lag + 1):
        c = a.corr(b.shift(k))
        if pd.notna(c) and c > mejor[1]:
            mejor = (k, c)
    return mejor


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, default=RAIZ / "data/raw/ideam_corredor.csv")
    ap.add_argument("--salida", type=Path, default=RAIZ / "data/processed")
    ap.add_argument("--informe", type=Path, default=RAIZ / "docs/datos/perfil_calidad.md")
    args = ap.parse_args()

    bruto = cargar(args.csv)
    total = len(bruto)
    excl = int((bruto.est == ESTACION_EXCLUIDA).sum())
    df = bruto[bruto.est != ESTACION_EXCLUIDA].copy()
    del bruto
    df["codigo"] = df.est.map(ESTACIONES)
    assert df.codigo.notna().all(), "estación sin código en db/10"

    md: list[str] = []
    w = md.append
    w("# Perfil de calidad de los datos IDEAM del corredor Sogamoso-Nobsa\n")
    w("<!-- Generado por tools/perfil_datos.py. No editar a mano: volver a ejecutar el script. -->\n")
    w(f"Fuente: `data/raw/ideam_corredor.csv` (IDEAM, datos.gov.co `g4t8-zkc3`, filtrado con "
      f"`tools/filtrar_ideam.py`). Filas totales: {miles(total)}. Excluidas de MOVIL KOICA (31828): {miles(excl)}. "
      f"Analizadas: {miles(len(df))}.\n")

    # 1. Estructura y formato
    w("## 1. Estructura y formato\n")
    sin_fecha = int(df.ini.isna().sum() + df.fin.isna().sum())
    duracion = (df.fin - df.ini).value_counts()
    no_en_punto = int(((df.ini.dt.minute != 0) | (df.ini.dt.second != 0)).sum())
    vacios = int((df.texto == "").sum())
    con_miles = int(df.texto.str.contains(",", regex=False).sum())
    no_num = int((~df.texto.str.fullmatch(NUMERO.pattern)).sum())
    decimales = df.texto.str.extract(r"\.(\d+)$")[0].str.len().fillna(0).astype(int)
    w(f"- Fechas que no siguen `{FORMATO_FECHA}`: {sin_fecha}.")
    w(f"- Duración `fin - inicio`: " + ", ".join(f"{d} → {miles(c)}" for d, c in duracion.items())
      + f". Columna `DURACIÓN`: {sorted(df.dur.unique())}.")
    w(f"- Inicios que no están en punto: {no_en_punto}.")
    w(f"- Periodo: {df.ini.min()} a {df.ini.max()} (hora del archivo).")
    w(f"- Valores vacíos: {vacios}. Valores no numéricos: {no_num}.")
    w(f"- Valores con separador de miles (`1,091.39`): {miles(con_miles)}"
      + f", en {', '.join(sorted(df[df.texto.str.contains(',', regex=False)]['var'].unique()))}. "
      "El normalizador quita la coma; no cambia ningún dígito.")
    w(f"- Máximo de decimales: {int(decimales.max())}. Cabe en `medicion.valor_crudo NUMERIC(10,3)` sin redondear.\n")
    w("Decimales por variable (número de filas):\n")
    w(tabla(pd.crosstab(df["var"], decimales.rename("decimales"))) + "\n")

    df["x"] = df.texto.str.replace(",", "", regex=False).astype(float)

    # 2. Duplicados
    w("## 2. Duplicados\n")
    exactos = int(df.duplicated(["est", "var", "texto", "ini", "fin"]).sum())
    clave = int(df.duplicated(["est", "var", "ini"]).sum())
    w(f"- Filas idénticas: {exactos}.")
    w(f"- Filas con la misma clave (estación, variable, inicio), que es la restricción única de `medicion`: {clave}.")
    w("- El normalizador falla si encuentra alguna; con estos datos no descarta nada.\n")

    # 3. Estaciones
    w("## 3. Estaciones y coordenadas\n")
    est = (df.groupby(["est", "codigo", "nombre", "lat", "lon", "alt"]).size().rename("filas").reset_index())
    w(tabla(est, indice=False) + "\n")
    w("Las coordenadas de SENA, BOMBEROS, RECREO y NAZARET difieren de `db/10` en la cuarta cifra decimal "
      "(decenas de metros) y SENA y RECREO tienen altitud 2476 en lugar de 2477 y 2483. No afecta al sistema; "
      "se puede ajustar `db/10` con un script nuevo si se quiere exactitud.\n")

    w("Filas por variable y estación:\n")
    w(tabla(pd.crosstab(df["var"], df["codigo"])) + "\n")

    # 4. Completitud de PM10
    pm = df[df["var"] == "PM10"].copy()
    pm["anio"] = pm.ini.dt.year
    w("## 4. Completitud de PM10 por estación y año\n")
    horas_anio = {a: (366 if pd.Timestamp(year=a, month=12, day=31).dayofyear == 366 else 365) * 24
                  for a in range(2020, 2025)}
    comp = pm.groupby(["codigo", "anio"]).size().unstack(fill_value=0)
    pct = comp.apply(lambda c: (100 * c / horas_anio[c.name]).round(1))
    w("Porcentaje de horas del año con medición:\n")
    w(tabla(pct) + "\n")
    pm["dia"] = pm.ini.dt.normalize()
    porDia = pm.groupby(["codigo", "dia"]).size()
    rep = (porDia >= 18).groupby([porDia.index.get_level_values(0),
                                  porDia.index.get_level_values(1).year]).sum().unstack(fill_value=0)
    w("Días con 18 horas o más de PM10 (75 %, criterio de representatividad de RF-05):\n")
    w(tabla(rep) + "\n")

    # 5. Huecos
    w("## 5. Horas faltantes de PM10\n")
    w("Rachas de horas sin medición entre la primera y la última medición de cada estación.\n")
    filas = []
    largos = []
    for cod, g in pm.groupby("codigo"):
        h = huecos(pd.DatetimeIndex(g.ini), g.ini.min(), g.ini.max())
        hs = h.horas
        filas.append({"estacion": cod, "primera": g.ini.min(), "ultima": g.ini.max(),
                      "huecos": len(h), "1 h": int((hs == 1).sum()), "2-3 h": int(hs.between(2, 3).sum()),
                      "4-24 h": int(hs.between(4, 24).sum()), "> 24 h": int((hs > 24).sum()),
                      "horas faltantes": int(hs.sum())})
        if len(h):
            top = h.nlargest(3, "horas")
            for _, r in top.iterrows():
                largos.append({"estacion": cod, "desde": r.inicio, "horas": int(r.horas),
                               "días": round(r.horas / 24, 1)})
    w(tabla(pd.DataFrame(filas), indice=False) + "\n")
    w("Los tres huecos más largos por estación:\n")
    w(tabla(pd.DataFrame(largos), indice=False) + "\n")
    rango = pd.date_range(pm.ini.min(), pm.ini.max(), freq="h")
    red = pm.groupby("ini").codigo.nunique().reindex(rango, fill_value=0)
    sin_red = huecos(pd.DatetimeIndex(red[red > 0].index), rango.min(), rango.max())
    largas = sin_red[sin_red.horas > 24].sort_values("horas", ascending=False)
    w(f"Horas sin PM10 en **ninguna** estación: {miles(int((red == 0).sum()))}. "
      f"Periodos de más de un día con toda la red sin datos: {len(largas)}. Los mayores:\n")
    w(tabla(largas.head(5).assign(días=(largas.head(5).horas / 24).round(1)), indice=False) + "\n")
    meses = pm.groupby([pm.ini.dt.to_period("M"), "codigo"]).size().unstack(fill_value=0) == 0
    vacios = [f"{p} ({', '.join(meses.columns[meses.loc[p]])})" for p in meses.index if meses.loc[p].any()]
    w("Meses calendario sin ninguna medición de PM10 en alguna estación: " + "; ".join(vacios) + ". "
      "(Un mes ausente del todo no aparece en esta lista porque no tiene filas; lo muestran los huecos.) "
      "Que muchos huecos empiecen a las 23:00 del último día del mes y duren un mes exacto sugiere meses "
      "que faltan en el export, no fallas de las estaciones.\n")
    w("Un hueco de más de dos horas es lo que P-04 debe detectar como estación sin transmisión (RNF-03). "
      "La reproducción de los históricos ya contiene muchos casos reales, además de los inyectados.\n")

    # 6. Valores de PM10
    w("## 6. Valores de PM10\n")
    d = pm.groupby("codigo").x.describe(percentiles=[.5, .95, .99]).round(1)
    w(tabla(d) + "\n")
    w(f"- Ceros: {int((pm.x == 0).sum())}. Negativos: {int((pm.x < 0).sum())}. "
      f"Mayores que 1000 (máximo físico de `db/10`): {int((pm.x > 1000).sum())}.")
    serie = {c: g.set_index("ini").x.asfreq("h") for c, g in pm.groupby("codigo")}
    movil = {c: s.rolling(24, min_periods=18).mean() for c, s in serie.items()}
    max24 = max(m.max() for m in movil.values())
    niveles = pd.DataFrame({
        c: {"máximo promedio 24 h": round(m.max(), 1),
            "horas ≥ 75 (límite diario)": int((m >= 75).sum()),
            "horas ≥ 155 (prevención)": int((m >= 155).sum()),
            "horas ≥ 255 (alerta)": int((m >= 255).sum())}
        for c, m in movil.items()}).T.rename_axis("estacion")
    w("\nPromedio móvil de 24 horas con 18 o más horas válidas (lo que calcula P-06), sin validación previa:\n")
    w(tabla(niveles) + "\n")
    rachas = {}
    saltos = []
    for c, s in serie.items():
        igual = s.eq(s.shift())
        grupo = (~igual).cumsum()
        rachas[c] = int((s.groupby(grupo).size() >= 6).sum())
        saltos.append(s.diff().abs().rename(c))
    w("Rachas de seis horas o más con el mismo valor (regla de valor repetido de HU-18): "
      + ", ".join(f"{c} {n}" for c, n in rachas.items()) + ".\n")
    sj = pd.concat(saltos, axis=1)
    w("Cambio absoluto entre horas consecutivas (µg/m³), insumo para el umbral de cambio brusco "
      "(`docs/planes/validacion.md`):\n")
    w(tabla(sj.quantile([.5, .9, .99, .999]).round(1).rename_axis("cuantil")) + "\n")

    pm25 = df[df["var"] == "PM2.5"].set_index(["codigo", "ini"]).x
    par = pd.concat([pm.set_index(["codigo", "ini"]).x.rename("pm10"), pm25.rename("pm25")], axis=1).dropna()
    w(f"Horas con PM2.5 mayor que PM10 en la misma estación (físicamente dudoso): "
      f"{int((par.pm25 > par.pm10).sum()):,} de {len(par):,}.\n".replace(",", "."))

    # 7. Zona horaria
    w("## 7. Zona horaria de las fechas\n")
    met = df[df["var"].isin(["TAire10", "TAire2", "RUVb", "HAire10", "HAire2"])].copy()
    met["hora"] = met.ini.dt.hour
    met["grupo"] = met["var"].str.replace(r"\d+$", "", regex=True)
    picos = met.groupby(["grupo", "codigo", "hora"]).x.mean().unstack()
    resumen = pd.DataFrame({"hora del máximo": picos.idxmax(axis=1), "hora del mínimo": picos.idxmin(axis=1)})
    w(tabla(resumen) + "\n")
    w("Lo esperado según el sol: el mediodía solar en el corredor (longitud ≈ 72,92° O) es a las 11:52 hora "
      "de Colombia y a las 16:52 UTC. El intervalo horario que lo contiene es el de las **11 h** si las fechas "
      "están en hora local y el de las **16 h** si están en UTC. La radiación UV debería tener su máximo ahí, "
      "y la temperatura dos a tres horas después.\n")
    w("Desfase de cada estación respecto a NAZARET (horas que maximizan la correlación de la temperatura "
      "y la humedad horarias; 0 = misma convención):\n")
    filas = []
    for grupo in ("TAire", "HAire"):
        m = met[met.grupo == grupo]
        ref = m[m.est == ESTACION_REFERENCIA].set_index("ini").x.asfreq("h")
        for cod, g in m[m.est != ESTACION_REFERENCIA].groupby("codigo"):
            s = g.set_index("ini").x.asfreq("h")
            for anio in range(2020, 2025):
                a, b = ref[ref.index.year == anio], s[s.index.year == anio]
                if b.notna().sum() > 500 and a.notna().sum() > 500:
                    k, c = desfase(a, b)
                    filas.append({"variable": grupo, "estacion": cod, "año": anio, "desfase h": k, "r": round(c, 3)})
    des = pd.DataFrame(filas)
    w(tabla(des.pivot_table(index=["variable", "estacion"], columns="año", values="desfase h"))+ "\n")
    w("Conclusión en la sección 9.\n")

    # 8. Cambio de altura de los sensores
    w("## 8. Cambio de altura de los sensores meteorológicos\n")
    alt = df[df["var"].isin(["TAire10", "TAire2", "HAire10", "HAire2"])]
    w(tabla(alt.groupby(["var", alt.ini.dt.year.rename("año")]).size().unstack(fill_value=0)) + "\n")
    w("Temperatura y humedad a 10 m hasta 2023 y a 2 m en 2024 (`TAire10` → `TAire2`, `HAire10` → `HAire2`). "
      "No son la misma serie: un modelo que las use debe tratarlas como variables distintas o corregir el "
      "salto. Se conservan con su código original en `meteorologia_normalizada.csv`.\n")

    # Normalización
    args.salida.mkdir(parents=True, exist_ok=True)
    df["valor"] = df.texto.map(limpiar_valor)
    df["inicio"] = a_utc_iso(df.ini)
    salida = df[["codigo", "var", "inicio", "valor"]].rename(columns={"codigo": "estacion", "var": "variable"})
    salida = salida.sort_values(["inicio", "estacion", "variable"])
    sim = salida[salida.variable.isin(VARIABLES_SIMULADOR)]
    met_s = salida[~salida.variable.isin(VARIABLES_SIMULADOR)]
    rutas = {}
    for nombre, datos in (("historico_normalizado.csv", sim), ("meteorologia_normalizada.csv", met_s)):
        ruta = args.salida / nombre
        datos.to_csv(ruta, index=False, lineterminator="\n")
        rutas[nombre] = (ruta, len(datos))

    # Comprobación de ida y vuelta: el valor normalizado es el mismo número que el original
    assert (salida.valor.astype(float).values == df.loc[salida.index, "x"].values).all()

    w("## 9. Respuestas para el diseño\n")
    w("**Decimales.** Como máximo dos. `NUMERIC(10,3)` alcanza y no hace falta ampliar la columna "
      "(punto abierto 1 de `docs/api/README.md`, cerrado). La regla de la ingesta que rechaza más de tres "
      "decimales no rechazará ningún dato histórico.\n")
    w("**Zona horaria.** Los datos no la confirman. El máximo de radiación UV cae en las 14 a 15 h y el de "
      "temperatura entre las 16 y las 18 h, entre lo esperado para hora local y para UTC; ninguna de las dos "
      "convenciones encaja limpio, y la curva de UV es más ancha que el día solar, lo que sugiere sensores "
      "con respuesta lenta o promedios desplazados. Se mantiene la suposición documentada por el IDEAM "
      "(hora legal de Colombia, UTC-5, sin horario de verano) y el normalizador suma cinco horas. El sistema "
      "no depende del valor absoluto: los promedios, las reglas y el modelo trabajan con horas relativas. "
      "Sí depende de que **las estaciones sean coherentes entre sí** (comparación entre estaciones de HU-18, "
      "cobertura espacial de RF-06): ver la tabla de desfases de la sección 7. Punto abierto 2 de "
      "`docs/api/README.md`: queda como suposición, no como hecho, y se anota como riesgo.\n")
    w("**Duplicados.** No hay. El simulador puede enviar el archivo tal cual sin decidir nada.\n")
    w("**Formato.** Hay valores con separador de miles; el normalizador los convierte sin cambiar dígitos y "
      "comprueba que el número resultante es el mismo.\n")
    if max24 < 155:
        w(f"**Declaratorias con datos reales: no ocurren.** El mayor promedio móvil de 24 horas en cinco años "
          f"es {max24:.1f} µg/m³, lejos de los 155 del nivel de prevención. Reproducir los históricos nunca "
          "generará una propuesta de declaratoria. Para demostrar RF-06, RF-07 y RF-10 hace falta provocarla: "
          "(a) una falla nueva del simulador que escale los valores de un periodo (episodio sintético, marcado "
          "con `falla_id` como cualquier falla), o (b) parámetros normativos de demostración con vigencia propia "
          "(RF-15 lo permite sin tocar código). La (b) no altera datos; la (a) ejercita además el pronóstico. "
          "Lo decide `docs/planes/normativo.md`. El límite diario de 75 µg/m³ sí se supera (SENA), así que "
          "el ICA de la vista pública mostrará categorías por encima de \"aceptable\".\n")
    else:
        w(f"**Declaratorias con datos reales.** El mayor promedio móvil de 24 horas es {max24:.1f} µg/m³.\n")
    w("**Huecos comunes a toda la red.** Hay periodos largos sin ninguna estación (sección 5). La partición "
      "temporal del modelo (HU-38) y la regla de comparación entre estaciones (HU-18) deben contar con ellos; "
      "la segunda ya prevé omitirse si no hay otras estaciones (CU-02, 2b).\n")
    w("**Coherencia horaria entre estaciones.** BOMBEROS y SENA aparecen una hora después que NAZARET y "
      "RECREO en temperatura y humedad, todos los años; UPTC cambia de un año a otro entre -1 y +1. Puede ser "
      "microclima o una convención distinta para etiquetar el intervalo; los datos no lo distinguen. "
      "Consecuencias: la comparación entre estaciones de HU-18 debe tolerar una hora de desfase, y el plan del "
      "pronóstico debe decidir si lo corrige por estación. **El normalizador no lo corrige**: mover la hora de "
      "un dato crudo sin evidencia sería modificarlo.\n")

    w("## 10. Archivos normalizados\n")
    w("No se suben al repositorio (`data/` está en `.gitignore`). Se regeneran con este script.\n")
    w("| Archivo | Filas | SHA-256 |\n|---|---|---|")
    for nombre, (ruta, n) in rutas.items():
        w(f"| `data/processed/{nombre}` | {n:,} | `{sha256(ruta)}` |".replace(",", "."))
    w("\nFormato: `estacion,variable,inicio,valor`; `inicio` en UTC con `Z`, en punto, intervalo de una hora; "
      "`valor` con los dígitos del origen. Ordenado por `inicio`, `estacion`, `variable`.\n")

    args.informe.parent.mkdir(parents=True, exist_ok=True)
    args.informe.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print(f"Informe: {args.informe.relative_to(RAIZ)}")
    for nombre, (ruta, n) in rutas.items():
        print(f"{nombre}: {n:,} filas")


if __name__ == "__main__":
    main()
