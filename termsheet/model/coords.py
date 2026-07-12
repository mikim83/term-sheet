from __future__ import annotations

import re

_CELL_RE = re.compile(r"^([A-Za-z]+)(\d+)$")


def col_to_letters(col: int) -> str:
    """1-indexed column number -> spreadsheet letters (1 -> A, 27 -> AA)."""
    letters = ""
    while col > 0:
        col, rem = divmod(col - 1, 26)
        letters = chr(ord("A") + rem) + letters
    return letters


def letters_to_col(letters: str) -> int:
    """Spreadsheet letters -> 1-indexed column number."""
    col = 0
    for ch in letters.upper():
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return col


def coord_to_a1(row: int, col: int) -> str:
    return f"{col_to_letters(col)}{row}"


def a1_to_coord(a1: str) -> tuple[int, int]:
    match = _CELL_RE.match(a1.strip())
    if not match:
        raise ValueError(f"Referencia de celda inválida: {a1!r}")
    letters, row = match.groups()
    return int(row), letters_to_col(letters)
