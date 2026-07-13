"""TermSheet: hoja de cálculo de terminal, 100% teclado, compatible con .xlsx."""

from __future__ import annotations

import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Input, Static

from . import config
from .clipboard import RangeClipboard
from .grid import SheetGrid
from .io.xlsx_io import load_workbook, save_workbook
from .model.coords import a1_to_coord, coord_to_a1
from .model.formatting import FORMAT_ORDER, label_for
from .model.formula_engine import Engine
from .model.undo import BulkSetCommand, SetCellCommand, SetFormatCommand, UndoStack
from .model.workbook import Workbook
from .ui.dialogs import ChoiceDialog, HelpDialog, InputDialog
from .ui.statusbar import StatusBar
from .ui.themes import THEME_ORDER, get_theme


class TermSheetApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #formula_bar {
        dock: top;
        height: 3;
    }
    SheetGrid {
        height: 1fr;
    }
    StatusBar {
        dock: bottom;
        height: 1;
    }
    #sheet_tabs {
        dock: bottom;
        height: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Salir"),
        Binding("ctrl+s", "save", "Guardar"),
        Binding("ctrl+o", "open", "Abrir"),
        Binding("ctrl+n", "new_sheet", "Nueva hoja"),
        Binding("ctrl+z", "undo", "Deshacer"),
        Binding("ctrl+y", "redo", "Rehacer"),
        Binding("ctrl+g", "goto", "Ir a celda"),
        Binding("ctrl+f", "find", "Buscar"),
        Binding("ctrl+t", "cycle_theme", "Tema"),
        Binding("ctrl+c", "copy", "Copiar"),
        Binding("ctrl+x", "cut", "Cortar"),
        Binding("ctrl+v", "paste", "Pegar"),
        Binding("f1", "help", "Ayuda"),
        Binding("f2", "edit_cell", "Editar"),
        Binding("f8", "toggle_select_mode", "Modo selección"),
        Binding("ctrl+1", "format_cell", "Formato de celda"),
        Binding("ctrl+r", "rename_sheet", "Renombrar hoja"),
        Binding("delete", "delete_selection", "Borrar"),
        Binding("alt+pagedown", "next_sheet", "Hoja siguiente", show=False),
        Binding("alt+pageup", "prev_sheet", "Hoja anterior", show=False),
        Binding("shift+up", "extend_up", show=False),
        Binding("shift+down", "extend_down", show=False),
        Binding("shift+left", "extend_left", show=False),
        Binding("shift+right", "extend_right", show=False),
    ]

    def __init__(self, path: str | None = None):
        super().__init__()
        self.workbook = load_workbook(path) if path else Workbook()
        self.engine = Engine(self.workbook)
        self.undo_stack = UndoStack()
        self.range_clipboard = RangeClipboard()
        self.theme_key = config.load_theme()
        self.anchor: tuple[int, int] | None = None
        self.editing = False
        self.select_mode = False

    def compose(self) -> ComposeResult:
        yield Input(id="formula_bar")
        yield SheetGrid(id="grid")
        yield Static(id="sheet_tabs")
        yield StatusBar(id="statusbar")
        yield Footer()

    def on_mount(self) -> None:
        grid = self.query_one(SheetGrid)
        grid.build()
        self.engine.recalculate()
        grid.refresh_from_sheet(self.workbook.active_sheet)
        grid.move_to(1, 1)
        self.apply_theme()
        self.refresh_status()
        grid.focus()

    # -- theming ---------------------------------------------------------

    def apply_theme(self) -> None:
        theme = get_theme(self.theme_key)
        self.query_one(SheetGrid).styles.background = theme.background
        self.query_one(SheetGrid).styles.color = theme.foreground
        status = self.query_one(StatusBar)
        status.styles.background = theme.statusbar_bg
        status.styles.color = theme.statusbar_fg
        tabs = self.query_one("#sheet_tabs", Static)
        tabs.styles.background = theme.header_bg
        tabs.styles.color = theme.header_fg
        self.refresh_sheet_tabs()

    def action_cycle_theme(self) -> None:
        def on_choice(key: str | None) -> None:
            if key:
                self.theme_key = key
                config.save_theme(key)
                self.apply_theme()
                self.refresh_status()

        theme_list = [(k, get_theme(k).label) for k in THEME_ORDER]
        self.push_screen(
            ChoiceDialog("Elige un tema (flechas + Enter, Esc cancela)", theme_list, self.theme_key), on_choice
        )

    # -- status / tabs -----------------------------------------------------

    def refresh_status(self) -> None:
        grid = self.query_one(SheetGrid)
        row, col = grid.selected_coord()
        sheet = self.workbook.active_sheet
        addr = coord_to_a1(row, col)
        raw = sheet.get_raw(row, col)
        if self.editing:
            mode = "EDIT"
        elif self.select_mode:
            mode = "NAV·SEL (F8)"
        else:
            mode = "NAV"
        self.query_one(StatusBar).set_status(addr, mode, raw, sheet.name, get_theme(self.theme_key).label)

    def refresh_sheet_tabs(self) -> None:
        parts = []
        for i, sheet in enumerate(self.workbook.sheets):
            if i == self.workbook.active_index:
                parts.append(f"[reverse bold] {sheet.name} [/reverse bold]")
            else:
                parts.append(f" {sheet.name} ")
        self.query_one("#sheet_tabs", Static).update(" ".join(parts))

    # -- navigation / selection --------------------------------------------

    def _extend(self, drow: int, dcol: int) -> None:
        grid = self.query_one(SheetGrid)
        row, col = grid.selected_coord()
        if self.anchor is None:
            self.anchor = (row, col)
        grid.move_to(row + drow, col + dcol)
        self.refresh_status()

    def action_extend_up(self) -> None:
        self._extend(-1, 0)

    def action_extend_down(self) -> None:
        self._extend(1, 0)

    def action_extend_left(self) -> None:
        self._extend(0, -1)

    def action_extend_right(self) -> None:
        self._extend(0, 1)

    def action_toggle_select_mode(self) -> None:
        """Modo de selección estilo Excel (F8): útil cuando Shift+flechas no
        llega a la app (algunos terminales no distinguen esas combinaciones).
        Mientras está activo, las flechas normales extienden la selección en
        vez de moverse sueltas."""
        grid = self.query_one(SheetGrid)
        if self.select_mode:
            self.select_mode = False
        else:
            self.select_mode = True
            if self.anchor is None:
                self.anchor = grid.selected_coord()
        self.refresh_status()

    def on_data_table_cell_highlighted(self, event) -> None:
        self.refresh_status()

    def on_data_table_cell_selected(self, event) -> None:
        if not self.editing:
            self.action_edit_cell()

    def _selection_bounds(self) -> tuple[int, int, int, int]:
        grid = self.query_one(SheetGrid)
        row, col = grid.selected_coord()
        if self.anchor is None:
            return row, col, row, col
        arow, acol = self.anchor
        return min(row, arow), min(col, acol), max(row, arow), max(col, acol)

    # -- editing -------------------------------------------------------------

    def action_edit_cell(self) -> None:
        grid = self.query_one(SheetGrid)
        row, col = grid.selected_coord()
        sheet = self.workbook.active_sheet
        bar = self.query_one("#formula_bar", Input)
        bar.value = sheet.get_raw(row, col)
        self.editing = True
        bar.focus()
        self.refresh_status()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "formula_bar":
            return
        self._commit_edit(event.value)
        grid = self.query_one(SheetGrid)
        row, col = grid.selected_coord()
        grid.move_to(row + 1, col)
        grid.focus()

    def on_key(self, event) -> None:
        if self.editing and event.key == "escape":
            self.editing = False
            self.query_one(SheetGrid).focus()
            self.refresh_status()
            event.stop()
            return
        if not self.editing and not self.select_mode and event.key in ("up", "down", "left", "right"):
            self.anchor = None

    def _commit_edit(self, value: str) -> None:
        grid = self.query_one(SheetGrid)
        row, col = grid.selected_coord()
        sheet = self.workbook.active_sheet
        self.undo_stack.execute(SetCellCommand(sheet, row, col, value))
        self.engine.recalculate()
        grid.refresh_from_sheet(sheet)
        self.editing = False
        self.refresh_status()

    def action_format_cell(self) -> None:
        r1, c1, r2, c2 = self._selection_bounds()
        cells = [(r, c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        sheet = self.workbook.active_sheet
        current = sheet.get_cell(r1, c1).fmt.number_format

        def on_choice(choice: str | None) -> None:
            if choice is None:
                return
            new_format = None if choice == "__general__" else choice
            self.undo_stack.execute(SetFormatCommand(sheet, cells, new_format))
            self.engine.recalculate()
            self.query_one(SheetGrid).refresh_from_sheet(sheet)
            self.refresh_status()

        options = [("__general__", "General (sin formato)")]
        options += [(key, label_for(key)) for key in FORMAT_ORDER]
        self.push_screen(
            ChoiceDialog("Formato de celda (flechas + Enter, Esc cancela)", options, current or "__general__"),
            on_choice,
        )

    def action_delete_selection(self) -> None:
        r1, c1, r2, c2 = self._selection_bounds()
        sheet = self.workbook.active_sheet
        changes = {(r, c): "" for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)}
        self.undo_stack.execute(BulkSetCommand(sheet, changes))
        self.engine.recalculate()
        self.query_one(SheetGrid).refresh_from_sheet(sheet)
        self.refresh_status()

    # -- undo/redo -------------------------------------------------------

    def action_undo(self) -> None:
        self.undo_stack.undo()
        self.engine.recalculate()
        self.query_one(SheetGrid).refresh_from_sheet(self.workbook.active_sheet)
        self.refresh_status()

    def action_redo(self) -> None:
        self.undo_stack.redo()
        self.engine.recalculate()
        self.query_one(SheetGrid).refresh_from_sheet(self.workbook.active_sheet)
        self.refresh_status()

    # -- clipboard ---------------------------------------------------------

    def action_copy(self) -> None:
        self._copy_or_cut(cut=False)

    def action_cut(self) -> None:
        self._copy_or_cut(cut=True)

    def _copy_or_cut(self, cut: bool) -> None:
        r1, c1, r2, c2 = self._selection_bounds()
        sheet = self.workbook.active_sheet
        rows = [[sheet.get_raw(r, c) for c in range(c1, c2 + 1)] for r in range(r1, r2 + 1)]
        self.range_clipboard.set(rows, cut=cut)
        if cut:
            changes = {(r, c): "" for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)}
            self.undo_stack.execute(BulkSetCommand(sheet, changes))
            self.engine.recalculate()
            self.query_one(SheetGrid).refresh_from_sheet(sheet)
        self.refresh_status()

    def action_paste(self) -> None:
        rows = self.range_clipboard.get()
        if not rows:
            return
        grid = self.query_one(SheetGrid)
        row, col = grid.selected_coord()
        sheet = self.workbook.active_sheet
        changes = {}
        for dr, row_vals in enumerate(rows):
            for dc, val in enumerate(row_vals):
                changes[(row + dr, col + dc)] = val
        self.undo_stack.execute(BulkSetCommand(sheet, changes))
        self.engine.recalculate()
        grid.refresh_from_sheet(sheet)
        self.refresh_status()

    # -- file operations -----------------------------------------------------

    def action_save(self) -> None:
        def on_path(path: str | None) -> None:
            if path:
                save_workbook(self.workbook, path)
                self.notify(f"Guardado en {path}")

        default = self.workbook.path or "libro.xlsx"
        self.push_screen(InputDialog("Guardar como (.xlsx)", initial=default), on_path)

    def action_open(self) -> None:
        def on_path(path: str | None) -> None:
            if path:
                try:
                    self.workbook = load_workbook(path)
                except Exception as exc:  # noqa: BLE001 - shown to the user
                    self.notify(f"Error al abrir: {exc}", severity="error")
                    return
                self.engine = Engine(self.workbook)
                self.engine.recalculate()
                self.undo_stack = UndoStack()
                self.query_one(SheetGrid).refresh_from_sheet(self.workbook.active_sheet)
                self.refresh_sheet_tabs()
                self.refresh_status()

        self.push_screen(InputDialog("Abrir archivo (.xlsx)"), on_path)

    def action_rename_sheet(self) -> None:
        sheet = self.workbook.active_sheet

        def on_name(name: str | None) -> None:
            if name and name.strip():
                sheet.name = name.strip()
                self.refresh_sheet_tabs()
                self.refresh_status()

        self.push_screen(InputDialog("Renombrar hoja", initial=sheet.name), on_name)

    def action_new_sheet(self) -> None:
        self.workbook.add_sheet()
        self.query_one(SheetGrid).refresh_from_sheet(self.workbook.active_sheet)
        self.refresh_sheet_tabs()
        self.refresh_status()

    def action_next_sheet(self) -> None:
        self.workbook.next_sheet()
        self.query_one(SheetGrid).refresh_from_sheet(self.workbook.active_sheet)
        self.refresh_sheet_tabs()
        self.refresh_status()

    def action_prev_sheet(self) -> None:
        self.workbook.prev_sheet()
        self.query_one(SheetGrid).refresh_from_sheet(self.workbook.active_sheet)
        self.refresh_sheet_tabs()
        self.refresh_status()

    # -- goto / find ---------------------------------------------------------

    def action_goto(self) -> None:
        def on_ref(ref: str | None) -> None:
            if ref:
                try:
                    row, col = a1_to_coord(ref)
                except ValueError:
                    self.notify("Referencia inválida", severity="error")
                    return
                self.query_one(SheetGrid).move_to(row, col)
                self.refresh_status()

        self.push_screen(InputDialog("Ir a celda (ej. B12)"), on_ref)

    def action_find(self) -> None:
        def on_term(term: str | None) -> None:
            if not term:
                return
            sheet = self.workbook.active_sheet
            for row, col, cell in sorted(sheet.iter_cells()):
                if term.lower() in cell.display().lower() or term.lower() in cell.raw.lower():
                    self.query_one(SheetGrid).move_to(row, col)
                    self.refresh_status()
                    return
            self.notify("No encontrado", severity="warning")

        self.push_screen(InputDialog("Buscar"), on_term)

    def action_help(self) -> None:
        self.push_screen(HelpDialog())


def run() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else None
    TermSheetApp(path).run()


if __name__ == "__main__":
    run()
