"""
Creacion de ToC con pymupdf
"""

from bisect import bisect_right
import argparse
import pymupdf
import re

ENTRY_RE = re.compile(r"^(?P<title>.+?)[\s….,]+(?P<page>\d+)$")
SKIP_TITLES = {"ÍNDICE", "Índice de términos"}   # luego se va al YAML de overrides

def detect_columns(xs: list[float], gap: float = 100.0) -> list[float]:
    """Agrupa coordenadas x en columnas y devuelve la x base (mínima) de cada una."""
    if not xs:
        raise ValueError("Lista de coordenadas no valida")
    ordenadas = sorted(xs)
    bases = [ordenadas[0]] + [cur for prev, cur in zip(ordenadas, ordenadas[1:]) if cur - prev > gap]
    return bases

def read_index_lines(pdf_path: str, page_index: int) -> tuple[list[dict], list[float]]:
    with pymupdf.open(pdf_path) as pdf:
        page = pdf.load_page(page_index)
        result =  page.get_text("dict")
        lines_out = []
        for block in result['blocks']:
            lines = block.get("lines", [])
            for line in lines:
                bbox = line["bbox"]
                spans = line.get("spans")
                span_line = []
                for span in spans:
                    text = span['text']
                    span_line.append(text)
                    # print(text)
                x0 = bbox[0]
                y0 = bbox[1]
                # col = int(x0 // (page.rect.width / 4))

                final_text = "".join(span_line).strip()
                if not final_text:
                    continue

                data = {"x0": x0, "y0": y0, "text": final_text}
                lines_out.append(data)
                # print(f"{col:>3} {x0:>6.1f} {y0:>7.1f}  {final_text}")
    xs = [l["x0"] for l in lines_out]
    bases = detect_columns(xs)
    for l in lines_out:
        l["col"] = bisect_right(bases, l["x0"]) - 1
    sorted_lines = sorted(lines_out, key=lambda l: (l["col"], l["y0"]))
    return sorted_lines, bases

def parse_entry(text:str) -> tuple[str, int] | None:
    m = ENTRY_RE.match(text.strip())
    if m is None:
        return None
    return m.group("title"), int(m.group("page"))


def merge_and_parse(lines: list[dict]) -> list[dict]:
    # data = {"col": col, "x0": x0, "y0": y0, "text": final_text} fromato ingresado
    entries = []
    buffer = None          # la línea incompleta que espera a la siguiente

    for line in lines:
        text = line["text"]
        if text in SKIP_TITLES:
            continue

        if buffer is not None:
            text = buffer["text"] + " " + text

        parsed_text = parse_entry(text)

        if parsed_text is None:
            if buffer is None:
                buffer = line
            else:
                buffer = {**buffer, "text": text}  # mismo origen, texto acumulado
            continue

        title, page = parsed_text
        if title in SKIP_TITLES:
            buffer = None
            continue
        origin = buffer if buffer is not None else line
        entries.append({"title": title, "page": page,
                        "col": origin["col"], "x0": origin["x0"], "y0": origin["y0"]})
        buffer = None

    if buffer is not None:
        raise ValueError(f"Línea incompleta al final: {buffer['text']!r}")
    return entries



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", type=str, help="PDF file")
    parser.add_argument("page_index", type=int, help="Page index")
    args = parser.parse_args()
    lines, bases = read_index_lines(args.pdf_path, args.page_index)
    entries = merge_and_parse(lines)
    print("bases:", [round(b, 1) for b in bases])
    print("entradas:", len(entries))
