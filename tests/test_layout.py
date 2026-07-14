"""QA de layout: las filas de chrome inferiores (pestañas de hoja, barra de
estado, footer de atajos) deben apilarse en filas distintas, no solaparse.

Regresión real: al tener tres widgets con `dock: bottom` como hermanos
directos de Screen, Textual no los apila automáticamente — todos acaban
pintándose en la misma fila y el de más arriba (Footer) tapaba el nombre
de la hoja activa, que quedaba invisible para el usuario.
"""

import asyncio

from termsheet.app import TermSheetApp


def run(coro):
    return asyncio.run(coro)


def test_bottom_bars_do_not_overlap():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            tabs = app.query_one("#sheet_tabs")
            status = app.query_one("#statusbar")
            footer = app.query_one("Footer")
            return tabs.region, status.region, footer.region

    tabs_region, status_region, footer_region = run(scenario())
    ys = {tabs_region.y, status_region.y, footer_region.y}
    assert len(ys) == 3  # cada barra en su propia fila
    # orden esperado de arriba a abajo: pestañas, estado, footer
    assert tabs_region.y < status_region.y < footer_region.y


def test_active_sheet_name_is_visible_in_status_bar():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app.workbook.add_sheet("Presupuesto")
            app.refresh_sheet_tabs()
            app.refresh_status()
            await pilot.pause()
            status = app.query_one("#statusbar")
            return status.visual

    text = str(run(scenario()))
    assert "Presupuesto" in text


def test_active_sheet_tab_is_visible_in_tabs_bar():
    async def scenario():
        app = TermSheetApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app.workbook.add_sheet("Gastos")
            app.refresh_sheet_tabs()
            await pilot.pause()
            tabs = app.query_one("#sheet_tabs")
            return tabs.visual

    text = str(run(scenario()))
    assert "Gastos" in text
