#!/usr/bin/env python3
"""Convierte el Trabajo de Grado (.docx) en una base de conocimiento liviana para Claude Code.

El .docx es la fuente de verdad del texto. Este script lo parte en archivos pequeños
para que Claude Code lea solo la sección que necesita, en lugar del documento entero.

Uso (desde la raíz del repo):
    python tools/docx_a_conocimiento.py docs/archivos/Trabajo_de_Grado_Vigilancia_PM10_Sogamoso_Nobsa.docx

Genera (y sobrescribe):
    docs/tesis/*.md         una sección del documento por archivo
    docs/diagramas/fig-*.png figuras con el número y título del documento
    db/NN_*.sql             los scripts SQL de la sección 3.6.9
    docs/MAPA.md            índice: qué hay, dónde está y cuánto pesa cada archivo

Requiere: pandoc y python-docx.
"""
import html
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parents[1]
TESIS = ROOT / "docs" / "tesis"
DIAG = ROOT / "docs" / "diagramas"
DB = ROOT / "db"
CAPTION = re.compile(r"\*\*(Figura|Tabla)\*\*\s*\*\*(\d+)\.\*\*\s*\*(.+?)\*\s*$")
CODE_CELL = re.compile(r"\|\s*((?:RF|RNF|CU|P)-\d+)\s*(?=\|)")
HEADING = re.compile(r"^(#{1,3})\s+(.*)$")
NUM = re.compile(r"^(\d+(?:\.\d+)*)\s")


def slug(s, n=48):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:n].rstrip("-")


def clean_cell(c):
    c = re.sub(r"</p>\s*<p>", "<br>", c)
    c = re.sub(r"</?p>", "", c)
    c = re.sub(r"<strong>(.*?)</strong>", r"**\1**", c, flags=re.S)
    c = re.sub(r"<em>(.*?)</em>", r"*\1*", c, flags=re.S)
    c = re.sub(r"<(?!br>)[^>]+>", "", c)
    return html.unescape(" ".join(c.split())).replace("|", "\\|")


def html_table_to_pipe(block):
    rows = [[clean_cell(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
            for r in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S)]
    rows = [r for r in rows if r]
    if not rows:
        return block
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def extract_sql(docx_path):
    """Los scripts están en tablas de una columna: fila 0 = nombre, fila 1 = código."""
    DB.mkdir(exist_ok=True)
    names = []
    for t in docx.Document(docx_path).tables:
        if len(t.rows) < 2:
            continue
        name = t.rows[0].cells[0].text.strip()
        if re.fullmatch(r"db/\d{2}_\w+\.sql", name):
            code = t.rows[1].cells[0].text.rstrip() + "\n"
            (ROOT / name).write_text(code, encoding="utf-8")
            names.append(name)
    return names


def main(docx_path):
    docx_path = Path(docx_path).resolve()
    sql_files = extract_sql(docx_path)

    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["pandoc", str(docx_path), "-t", "gfm", "--wrap=none",
                    f"--extract-media={tmp}", "-o", str(tmp / "t.md")], check=True)
    text = (tmp / "t.md").read_text(encoding="utf-8")

    text = re.sub(r'<span id="[^"]*" class="anchor"></span>', "", text)
    text = re.sub(r"\*\*(Figura|Tabla)\*\*\s*\*\*(\d+)\.\*\*", r"**\1** **\2.**", text)

    def table_sub(m):
        block = m.group(0)
        sql = re.search(r"<strong>(db/\d{2}_\w+\.sql)</strong>", block)
        if sql:
            return f"> Script completo en [`{sql.group(1)}`](../../{sql.group(1)})."
        return html_table_to_pipe(block)
    text = re.sub(r"<table>.*?</table>", table_sub, text, flags=re.S)

    # Figuras: renombrar con número y título del pie de figura que las precede.
    DIAG.mkdir(parents=True, exist_ok=True)
    lines, last_cap, figuras = text.split("\n"), None, []
    for i, ln in enumerate(lines):
        cap = CAPTION.search(ln)
        if cap:
            last_cap = (cap.group(1), int(cap.group(2)), cap.group(3).strip(), i)
            continue
        img = re.match(r"!\[\]\((.+?)\)", ln.strip())
        if img:
            src = Path(img.group(1))
            if last_cap and last_cap[0] == "Figura" and i - last_cap[3] <= 3:
                name = f"fig-{last_cap[1]:02d}-{slug(last_cap[2])}{src.suffix}"
                figuras.append((last_cap[1], last_cap[2], name))
            else:
                name = None  # logo de portada u otra imagen sin pie: no se copia
            if name:
                shutil.copy(src, DIAG / name)
                lines[i] = f"![{last_cap[2]}](../diagramas/{name})"
            else:
                lines[i] = ""

    # Partir por secciones.
    def split_level(num):
        if num is None:
            return 1
        parts = num.split(".")
        if len(parts) == 2 and parts[0] == "3":
            return 2
        if len(parts) == 3 and ".".join(parts[:2]) in {"3.2", "3.6"}:
            return 3
        return 0

    chunks, cur = [], {"title": "Preliminares", "key": "00_preliminares", "lines": []}
    for ln in lines:
        h = HEADING.match(ln)
        if h and h.group(2).strip():
            level, title = len(h.group(1)), h.group(2).strip()
            n = NUM.match(title)
            num = n.group(1) if n else None
            if level == 1 or (num and split_level(num) == level and level > 1):
                chunks.append(cur)
                if num:
                    key = num.replace(".", "-") + "_" + slug(title[len(num):])
                    key = ("0" + key) if num.split(".")[0].isdigit() and len(num.split(".")[0]) == 1 else key
                elif title.lower().startswith("capítulo v"):
                    key = "05_referencias"
                elif title.lower().startswith("anexo"):
                    key = "06_" + slug(title)
                else:
                    m = re.match(r"Capítulo (\w+)", title)
                    roman = {"I": "01", "II": "02", "III": "03", "IV": "04"}
                    key = (roman.get(m.group(1), "0x") + "_" + slug(title)) if m else slug(title)
                cur = {"title": title, "key": key, "lines": []}
        cur["lines"].append(ln)
    chunks.append(cur)

    # Se sobrescribe sin borrar: si una sección cambia de nombre, borra el archivo viejo a mano.
    TESIS.mkdir(parents=True, exist_ok=True)
    index = []
    for ch in chunks:
        body = re.sub(r"\n{3,}", "\n\n", "\n".join(ch["lines"])).strip()
        if not body:
            continue
        fname = ch["key"] + ".md"
        header = (f"<!-- Generado por tools/docx_a_conocimiento.py desde el .docx. "
                  f"No editar a mano: editar el Word y regenerar. -->\n\n")
        (TESIS / fname).write_text(header + body + "\n", encoding="utf-8")
        codes = sorted({c for l in ch["lines"] if l.startswith("|") for c in CODE_CELL.findall(l)},
                       key=lambda c: (c.split("-")[0], int(c.split("-")[1])))
        tablas = [f"T{c.group(2)}" for l in ch["lines"] if (c := CAPTION.search(l)) and c.group(1) == "Tabla"]
        figs = [f"F{c.group(2)}" for l in ch["lines"] if (c := CAPTION.search(l)) and c.group(1) == "Figura"]
        index.append((fname, ch["title"], len(body) // 4, codes, tablas, figs))

    write_mapa(index, figuras, sql_files, docx_path)
    print(f"{len(index)} secciones, {len(figuras)} figuras, {len(sql_files)} scripts SQL")


def compress(codes):
    """RF-01, RF-02, RF-03 -> RF-01..03"""
    out, prev = [], None
    for c in codes:
        p, n = c.split("-")[0], int(c.split("-")[1])
        if prev and prev[0] == p and prev[2] == n - 1:
            prev[2] = n
        else:
            if prev:
                out.append(prev)
            prev = [p, n, n]
    if prev:
        out.append(prev)
    return ", ".join(f"{p}-{a:02d}" + (f"..{b:02d}" if b != a else "") for p, a, b in out)


def write_mapa(index, figuras, sql_files, docx_path):
    rel = docx_path.relative_to(ROOT) if docx_path.is_relative_to(ROOT) else docx_path.name
    L = ["# Mapa del conocimiento del proyecto",
         "",
         "<!-- Generado por tools/docx_a_conocimiento.py. No editar a mano. -->",
         "",
         f"Fuente: `{rel}`. Lee este mapa primero y abre solo el archivo de la sección que necesitas.",
         "Tokens ≈ caracteres/4. La trazabilidad RF → servicio → carpeta → sprint está en `docs/TRAZABILIDAD.md`.",
         "",
         "## Secciones del documento",
         "",
         "| Archivo | Sección | ~Tokens | Códigos en tablas | Tablas | Figuras |",
         "|---|---|---|---|---|---|"]
    for fname, title, tok, codes, tablas, figs in index:
        L.append(f"| `docs/tesis/{fname}` | {title} | {tok:,} | {compress(codes)} | "
                 f"{', '.join(tablas)} | {', '.join(figs)} |")
    total = sum(i[2] for i in index)
    L += ["", f"Total ≈ {total:,} tokens. Ninguna tarea debería necesitar más de 2 o 3 secciones.",
          "", "## Figuras (`docs/diagramas/`)", "", "| N.º | Título | Archivo |", "|---|---|---|"]
    for n, t, f in figuras:
        L.append(f"| {n} | {t} | `{f}` |")
    L += ["", "## Scripts de base de datos (`db/`)", "",
          "Se ejecutan en orden numérico sobre PostgreSQL 16 (esquema `svca`).", ""]
    L += [f"- `{s}`" for s in sql_files]
    (ROOT / "docs" / "MAPA.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
