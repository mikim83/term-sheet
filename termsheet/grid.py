"""Widget de grilla: tabla de celdas basada en DataTable de Textual."""

from __future__ import annotations

from rich.text import Text
from textual.coordinate import Coordinate
from textual.widgets import DataTable

from .model.coords import col_to_letters
from .model.workbook import Sheet
from .model.cell import Cell

DEFAULT_ROWS = 200
DEFAULT_COLS = 26


def _cell_render(cell: Cell) -> str | Text:
    """Texto plano si la celda no tiene color propio (caso común, barato);
    si tiene font_color/bg_color, un rich.text.Text con ese estilo — DataTable
    de Textual acepta objetos Text como valor de celda y respeta su estilo."""
    text = cell.display()
    fg = cell.fmt.font_color
    bg = cell.fmt.bg_color
    if not fg and not bg:
        return text
    style_parts = []
    if fg:
        style_parts.append(f"#{fg}")
    if bg:
        style_parts.append(f"on #{bg}")
    return Text(text, style=" ".join(style_parts))


class SheetGrid(DataTable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "cell"
        self.zebra_stripes = False
        self.show_row_labels = True
        self.n_rows = DEFAULT_ROWS
        self.n_cols = DEFAULT_COLS

    def build(self) -> None:
        self.clear(columns=True)
        for c in range(1, self.n_cols + 1):
            self.add_column(col_to_letters(c), key=f"c{c}", width=10)
        for r in range(1, self.n_rows + 1):
            row_values = ["" for _ in range(self.n_cols)]
            self.add_row(*row_values, key=f"r{r}", label=str(r))

    def refresh_from_sheet(self, sheet: Sheet) -> None:
        # Clear all data cells first (cheap enough for the default grid size).
        for r in range(1, self.n_rows + 1):
            for c in range(1, self.n_cols + 1):
                self.update_cell(f"r{r}", f"c{c}", "", update_width=False)
        for row, col, cell in sheet.iter_cells():
            if row <= self.n_rows and col <= self.n_cols:
                self.update_cell(f"r{row}", f"c{col}", _cell_render(cell), update_width=False)

    def selected_coord(self) -> tuple[int, int]:
        coord: Coordinate = self.cursor_coordinate
        return coord.row + 1, coord.column + 1  # both 1-indexed; row labels aren't a real column

    def move_to(self, row: int, col: int) -> None:
        row = max(1, min(row, self.n_rows))
        col = max(1, min(col, self.n_cols))
        self.cursor_coordinate = Coordinate(row - 1, col - 1)
