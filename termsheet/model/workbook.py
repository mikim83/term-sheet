from __future__ import annotations

from dataclasses import dataclass, field

from .cell import Cell
from .coords import coord_to_a1


class Sheet:
    """A single sheet: sparse grid of cells keyed by (row, col), 1-indexed."""

    def __init__(self, name: str):
        self.name = name
        self.cells: dict[tuple[int, int], Cell] = {}
        self.max_row = 1
        self.max_col = 1
        self.col_widths: dict[int, int] = {}

    def get_cell(self, row: int, col: int) -> Cell:
        return self.cells.get((row, col), Cell())

    def get_raw(self, row: int, col: int) -> str:
        cell = self.cells.get((row, col))
        return cell.raw if cell else ""

    def set_raw(self, row: int, col: int, raw: str) -> Cell:
        if raw == "":
            self.cells.pop((row, col), None)
            cell = Cell()
        else:
            cell = self.cells.setdefault((row, col), Cell())
            cell.raw = raw
        self.max_row = max(self.max_row, row)
        self.max_col = max(self.max_col, col)
        return cell

    def clear_cell(self, row: int, col: int) -> None:
        self.cells.pop((row, col), None)

    def iter_cells(self):
        for (row, col), cell in self.cells.items():
            yield row, col, cell

    def a1(self, row: int, col: int) -> str:
        return coord_to_a1(row, col)


@dataclass
class Workbook:
    sheets: list[Sheet] | None = None
    active_index: int = 0
    path: str | None = None

    def __post_init__(self):
        if self.sheets is None:
            self.sheets = [Sheet("Hoja1")]

    @property
    def active_sheet(self) -> Sheet:
        return self.sheets[self.active_index]

    def add_sheet(self, name: str | None = None) -> Sheet:
        if name is None:
            name = f"Hoja{len(self.sheets) + 1}"
        sheet = Sheet(name)
        self.sheets.append(sheet)
        self.active_index = len(self.sheets) - 1
        return sheet

    def next_sheet(self) -> None:
        self.active_index = (self.active_index + 1) % len(self.sheets)

    def prev_sheet(self) -> None:
        self.active_index = (self.active_index - 1) % len(self.sheets)

    def sheet_by_name(self, name: str) -> Sheet | None:
        for sheet in self.sheets:
            if sheet.name == name:
                return sheet
        return None
