#!/usr/bin/env python3
"""Filtra el export nacional del IDEAM (datos.gov.co, g4t8-zkc3) al corredor Sogamoso-Nobsa.

Lee el CSV nacional (~7 GB, ~32,8 millones de filas) línea a línea en binario y conserva
solo las filas cuyo MUNICIPIO es Sogamoso o Nobsa. No carga el archivo en memoria.
Resultado verificado el 2026-11-15: 1.803.476 filas, 6 estaciones, 2020-2024, ~382 MB.

Uso:
    python tools/filtrar_ideam.py <export_nacional.csv> data/raw/ideam_corredor.csv
"""
import re
import sys

# MUNICIPIO es la penúltima columna; la última es TIPO_ESTACION.
PATRON = re.compile(rb',"(?:sogamoso|nobsa)","[^"]*"\r?\n$', re.IGNORECASE)


def main(src, dst):
    n = 0
    with open(src, "rb") as fi, open(dst, "wb") as fo:
        fo.write(fi.readline())  # encabezado
        for line in fi:
            if PATRON.search(line):
                fo.write(line)
                n += 1
    print(f"Filas del corredor: {n:,}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
