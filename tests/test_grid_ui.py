"""Tests de QA de la grilla/UI: navegación con teclado y protección de índices.

La columna de números de fila y la fila de letras de columna son "row
labels"/cabeceras nativas de Textual, no celdas de datos — por diseño el
cursor nunca puede aterrizar ahí, así que no son editables. Estos tests
protegen ese comportamiento tras la regresión donde una columna de índice
falsa sí era navegable y provocaba un crash (CellDoesNotExist) al editarla.
"""

import asyncio

from termsheet.app import TermSheetApp


def run(coro):
    return asyncio.run(coro)


def test_cursor_cannot_move_left_of_column_a():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            await pilot.press("left", "left", "left")
            await pilot.pause()
            return grid.selected_coord()

    assert run(scenario()) == (1, 1)


def test_cursor_cannot_move_above_row_1():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            await pilot.press("up", "up", "up")
            await pilot.pause()
            return grid.selected_coord()

    assert run(scenario()) == (1, 1)


def test_row_index_column_is_not_a_data_column():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            return len(grid.columns), [str(c.label) for c in grid.ordered_columns[:3]]

    n_cols, first_labels = run(scenario())
    assert n_cols == 26  # sin columna falsa de "rownum"
    assert first_labels == ["A", "B", "C"]


def test_editing_a1_does_not_crash_and_does_not_touch_row_label():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            await pilot.press("left", "left", "up", "up")  # intenta salir de la grilla
            await pilot.press("enter")
            await pilot.pause()
            for ch in "42":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause()
            return app.workbook.active_sheet.get_raw(1, 1)

    assert run(scenario()) == "42"
