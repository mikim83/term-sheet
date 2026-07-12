"""Widget de grilla: tabla de celdas basada en DataTable de Textual."""

from __future__ import annotations

from textual.coordinate import Coordinate
from textual.widgets import DataTable

from .model.coords import col_to_letters
from .model.workbook import Sheet

DEFAULT_ROWS = 200
DEFAULT_COLS = 26


class SheetGrid(DataTable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "cell"
        self.zebra_stripes = False
        self.n_rows = DEFAULT_ROWS
        self.n_cols = DEFAULT_COLS

    def build(self) -> None:
        self.clear(columns=True)
        self.add_column("", key="rownum", width=5)
        for c in range(1, self.n_cols + 1):
            self.add_column(col_to_letters(c), key=f"c{c}", width=10)
        for r in range(1, self.n_rows + 1):
            row_values = [str(r)] + ["" for _ in range(self.n_cols)]
            self.add_row(*row_values, key=f"r{r}")

    def refresh_from_sheet(self, sheet: Sheet) -> None:
        # Clear all data cells first (cheap enough for the default grid size).
        for r in range(1, self.n_rows + 1):
            for c in range(1, self.n_cols + 1):
                self.update_cell(f"r{r}", f"c{c}", "", update_width=False)
        for row, col, cell in sheet.iter_cells():
            if row <= self.n_rows and col <= self.n_cols:
                self.update_cell(f"r{row}", f"c{col}", cell.display(), update_width=False)

    def selected_coord(self) -> tuple[int, int]:
        coord: Coordinate = self.cursor_coordinate
        return coord.row + 1, coord.column  # row 1-indexed, column already skips rownum col

    def move_to(self, row: int, col: int) -> None:
        row = max(1, min(row, self.n_rows))
        col = max(1, min(col, self.n_cols))
        self.cursor_coordinate = Coordinate(row - 1, col)
