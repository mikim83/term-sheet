"""QA end-to-end del navegador de ficheros (Ctrl+O / Ctrl+S): navegar
carpetas, abrir un .xlsx existente, guardar con un nombre distinto sin
sobrescribir el original, y cancelar con Esc.
"""

import asyncio
import tempfile
from pathlib import Path

from textual.widgets import Input, ListView

from termsheet.app import TermSheetApp
from termsheet.io.xlsx_io import save_workbook
from termsheet.model.workbook import Workbook


def run(coro):
    return asyncio.run(coro)


async def _select_entry(pilot, list_view: ListView, name: str) -> None:
    names = [item.name for item in list_view.children]
    idx = names.index(name)
    for _ in range(idx):
        await pilot.press("down")
        await pilot.pause()
    await pilot.press("enter")


def test_ctrl_o_opens_file_via_browser():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            wb = Workbook()
            wb.active_sheet.set_raw(1, 1, "hola")
            save_workbook(wb, str(tmp / "existing.xlsx"))

            app = TermSheetApp(str(tmp / "existing.xlsx"))
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("ctrl+o")
                await pilot.pause()
                await pilot.pause()
                screen = app.screen
                list_view = screen.query_one(ListView)
                await _select_entry(pilot, list_view, "file:existing.xlsx")
                await pilot.pause()
                await pilot.pause()
                return len(app.screen_stack), app.workbook.active_sheet.get_raw(1, 1)

    stack_len, a1 = run(scenario())
    assert stack_len == 1  # el diálogo se cerró
    assert a1 == "hola"


def test_ctrl_s_save_as_with_new_name_keeps_original_file():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            wb = Workbook()
            save_workbook(wb, str(tmp / "existing.xlsx"))

            app = TermSheetApp(str(tmp / "existing.xlsx"))
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("ctrl+s")
                await pilot.pause()
                await pilot.pause()
                screen = app.screen
                filename_input = screen.query_one("#filename_input", Input)
                filename_input.focus()
                filename_input.value = "nuevo_nombre.xlsx"
                await pilot.press("enter")
                await pilot.pause()
                await pilot.pause()
                return (
                    app.workbook.path,
                    (tmp / "nuevo_nombre.xlsx").exists(),
                    (tmp / "existing.xlsx").exists(),
                )

    path, new_exists, original_exists = run(scenario())
    assert path.endswith("nuevo_nombre.xlsx")
    assert new_exists is True
    assert original_exists is True  # "guardar como" no borra el fichero anterior


def test_save_dialog_prefills_current_filename():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            wb = Workbook()
            save_workbook(wb, str(tmp / "presupuesto.xlsx"))
            app = TermSheetApp(str(tmp / "presupuesto.xlsx"))
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("ctrl+s")
                await pilot.pause()
                await pilot.pause()
                filename_input = app.screen.query_one("#filename_input", Input)
                return filename_input.value

    assert run(scenario()) == "presupuesto.xlsx"


def test_navigate_into_subdirectory_and_back_with_backspace():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "sub").mkdir()
            wb = Workbook()
            save_workbook(wb, str(tmp / "existing.xlsx"))
            app = TermSheetApp(str(tmp / "existing.xlsx"))
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("ctrl+o")
                await pilot.pause()
                await pilot.pause()
                screen = app.screen
                list_view = screen.query_one(ListView)
                await _select_entry(pilot, list_view, "dir:sub")
                await pilot.pause()
                dir_after_entering = screen.current_dir

                await pilot.press("backspace")
                await pilot.pause()
                dir_after_backspace = screen.current_dir
                return str(dir_after_entering), str(dir_after_backspace)

    dir_after_entering, dir_after_backspace = run(scenario())
    assert dir_after_entering.endswith("sub")
    assert not dir_after_backspace.endswith("sub")


def test_escape_cancels_without_changing_workbook():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            wb = Workbook()
            save_workbook(wb, str(tmp / "existing.xlsx"))
            app = TermSheetApp(str(tmp / "existing.xlsx"))
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("ctrl+o")
                await pilot.pause()
                await pilot.press("escape")
                await pilot.pause()
                return len(app.screen_stack), app.workbook.path

    stack_len, path = run(scenario())
    assert stack_len == 1
    assert path.endswith("existing.xlsx")
