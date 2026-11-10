# tests/test_parse_index.py
from toc.parse_index import merge_and_parse, parse_entry
import pytest

@pytest.mark.parametrize("text, expected", [
    ("Colegio del valor……………………,………..67", ("Colegio del valor", 67)),
    ("Opciones de invocación", None),
    ("Brujo……68", ("Brujo", 68)),
    ("Sobrenatural……71", ("Sobrenatural", 71)),
])
def test_parse_entry_cases(text, expected):
    assert parse_entry(text) == expected

FAKE_LINES = [
    {"col": 1, "x0": 387.8, "y0": 165.9, "text": "Brujo……68"},
    {"col": 1, "x0": 397.7, "y0": 187.2, "text": "Opciones de invocación"},
    {"col": 1, "x0": 411.0, "y0": 205.1, "text": "Sobrenatural……71"},
]

def test_merge_keeps_first_line_coords():
    out = merge_and_parse(FAKE_LINES)
    assert len(out) == 2
    assert out[1]["title"] == "Opciones de invocación Sobrenatural"
    assert out[1]["page"] == 71
    assert out[1]["x0"] == 397.7     # el de la PRIMERA línea, no 411.0

