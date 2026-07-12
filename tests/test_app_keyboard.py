"""Tests de QA end-to-end de flujos de teclado en TermSheetApp: nueva hoja,
cambio de pestañas, selección de rango con Shift, copiar/cortar/pegar, y salir.

Usan el modo headless de Textual (`run_test()` + `Pilot.press`) para simular
pulsaciones de teclado reales, igual que las probaría un usuario.
"""

import asyncio

from termsheet.app import TermSheetApp


def run(coro):
    return asyncio.run(coro)


# -- Nueva hoja / pestañas --------------------------------------------------


def test_ctrl_n_creates_a_new_sheet():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            names_before = [s.name for s in app.workbook.sheets]
            await pilot.press("ctrl+n")
            await pilot.pause()
            names_after = [s.name for s in app.workbook.sheets]
            return names_before, names_after, app.workbook.active_index

    before, after, active_index = run(scenario())
    assert before == ["Hoja1"]
    assert after == ["Hoja1", "Hoja2"]
    assert active_index == 1  # la nueva hoja pasa a ser la activa


def test_ctrl_pageup_pagedown_switch_sheets_and_wrap_around():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("ctrl+n")  # Hoja1, Hoja2
            await pilot.press("ctrl+n")  # Hoja1, Hoja2, Hoja3 (activa)
            await pilot.pause()
            idx_after_creating = app.workbook.active_index

            await pilot.press("alt+pageup")
            await pilot.pause()
            idx_after_prev = app.workbook.active_index

            await pilot.press("alt+pageup", "alt+pageup")
            await pilot.pause()
            idx_wrapped = app.workbook.active_index  # debe volver a envolver

            await pilot.press("alt+pagedown")
            await pilot.pause()
            idx_after_next = app.workbook.active_index

            return idx_after_creating, idx_after_prev, idx_wrapped, idx_after_next

    idx_created, idx_prev, idx_wrapped, idx_next = run(scenario())
    assert idx_created == 2
    assert idx_prev == 1
    assert idx_wrapped == 2  # 1 -> 0 -> 2 (wrap)
    assert idx_next == 0


def test_switching_sheets_preserves_independent_data():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            grid.move_to(1, 1)
            await pilot.press("enter")
            await pilot.pause()
            for ch in "hoja1valor":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause()

            await pilot.press("ctrl+n")
            await pilot.pause()
            sheet2_a1 = app.workbook.active_sheet.get_raw(1, 1)

            await pilot.press("alt+pageup")
            await pilot.pause()
            sheet1_a1 = app.workbook.active_sheet.get_raw(1, 1)

            return sheet2_a1, sheet1_a1

    sheet2_a1, sheet1_a1 = run(scenario())
    assert sheet2_a1 == ""  # la hoja nueva está en blanco
    assert sheet1_a1 != ""  # la hoja original conserva su contenido


# -- Selección de rango con Shift -------------------------------------------


def test_shift_arrows_extend_selection_in_all_directions():
    """Cada caso arranca en C3 con el anchor limpio (sin pasar por movimiento
    normal previo, que ya se prueba aparte en test_plain_arrow_after..."""

    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")

            grid.move_to(3, 3)
            app.anchor = None
            await pilot.press("shift+right", "shift+right")
            await pilot.pause()
            bounds_right = app._selection_bounds()

            grid.move_to(3, 3)
            app.anchor = None
            await pilot.press("shift+down", "shift+down")
            await pilot.pause()
            bounds_down = app._selection_bounds()

            grid.move_to(3, 3)
            app.anchor = None
            await pilot.press("shift+left")
            await pilot.pause()
            bounds_left = app._selection_bounds()

            grid.move_to(3, 3)
            app.anchor = None
            await pilot.press("shift+up")
            await pilot.pause()
            bounds_up = app._selection_bounds()

            return bounds_right, bounds_down, bounds_left, bounds_up

    bounds_right, bounds_down, bounds_left, bounds_up = run(scenario())
    assert bounds_right == (3, 3, 3, 5)   # C3:E3
    assert bounds_down == (3, 3, 5, 3)    # C3:C5
    assert bounds_left == (3, 2, 3, 3)    # B3:C3
    assert bounds_up == (2, 3, 3, 3)      # C2:C3


def test_plain_arrow_after_shift_selection_collapses_it():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            grid.move_to(3, 3)
            await pilot.press("shift+right", "shift+right")
            await pilot.pause()
            had_anchor = app.anchor is not None
            await pilot.press("right")
            await pilot.pause()
            return had_anchor, app.anchor

    had_anchor, anchor_after = run(scenario())
    assert had_anchor is True
    assert anchor_after is None


# -- Copiar / cortar / pegar rango ------------------------------------------


def test_copy_paste_range_via_keyboard():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            sheet = app.workbook.active_sheet
            sheet.set_raw(1, 1, "10")
            sheet.set_raw(1, 2, "20")
            app.engine.recalculate()
            grid.refresh_from_sheet(sheet)

            grid.move_to(1, 1)
            await pilot.press("shift+right")
            await pilot.pause()
            await pilot.press("ctrl+c")
            await pilot.pause()

            grid.move_to(5, 1)
            await pilot.press("ctrl+v")
            await pilot.pause()

            return sheet.get_raw(5, 1), sheet.get_raw(5, 2)

    a5, b5 = run(scenario())
    assert (a5, b5) == ("10", "20")


def test_cut_clears_source_range():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            sheet = app.workbook.active_sheet
            sheet.set_raw(1, 1, "x")
            app.engine.recalculate()
            grid.refresh_from_sheet(sheet)

            grid.move_to(1, 1)
            await pilot.press("ctrl+x")
            await pilot.pause()
            return sheet.get_raw(1, 1)

    assert run(scenario()) == ""


def test_delete_clears_selected_range():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            grid = app.query_one("SheetGrid")
            sheet = app.workbook.active_sheet
            sheet.set_raw(2, 2, "a")
            sheet.set_raw(2, 3, "b")
            app.engine.recalculate()
            grid.refresh_from_sheet(sheet)

            grid.move_to(2, 2)
            await pilot.press("shift+right")
            await pilot.pause()
            await pilot.press("delete")
            await pilot.pause()
            return sheet.get_raw(2, 2), sheet.get_raw(2, 3)

    b2, c2 = run(scenario())
    assert (b2, c2) == ("", "")


# -- Salir --------------------------------------------------------------


def test_ctrl_q_quits_the_app():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            running_before = app.is_running
            await pilot.press("ctrl+q")
            await pilot.pause()
            return running_before, app.is_running

    running_before, running_after = run(scenario())
    assert running_before is True
    assert running_after is False
