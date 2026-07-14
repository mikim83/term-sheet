import tempfile
from pathlib import Path

from termsheet.io.xlsx_io import load_workbook, save_workbook
from termsheet.model.formula_engine import Engine
from termsheet.model.workbook import Workbook


def test_roundtrip_preserves_formulas_and_multi_sheet():
    wb = Workbook(sheets=[])
    s1 = wb.add_sheet("Datos")
    s1.set_raw(1, 1, "5")
    s1.set_raw(1, 2, "=A1*2")
    s2 = wb.add_sheet("Resumen")
    s2.set_raw(1, 1, "hola")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "test.xlsx")
        save_workbook(wb, path)

        wb2 = load_workbook(path)
        assert [s.name for s in wb2.sheets] == ["Datos", "Resumen"]
        datos = wb2.sheet_by_name("Datos")
        assert datos.get_raw(1, 1) == "5"
        assert datos.get_raw(1, 2) == "=A1*2"

        eng = Engine(wb2)
        eng.recalculate()
        assert datos.get_cell(1, 2).value == 10


def test_roundtrip_preserves_currency_and_date_format():
    wb = Workbook(sheets=[])
    sheet = wb.add_sheet("Datos")
    sheet.set_raw(1, 1, "1234.5")
    sheet.get_cell(1, 1).fmt.number_format = "eur_es"
    sheet.set_raw(2, 1, "2026-07-13")
    sheet.get_cell(2, 1).fmt.number_format = "date_dmy"

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "formatos.xlsx")
        save_workbook(wb, path)

        wb2 = load_workbook(path)
        datos = wb2.sheet_by_name("Datos")
        Engine(wb2).recalculate()
        assert datos.get_cell(1, 1).fmt.number_format == "eur_es"
        assert datos.get_cell(1, 1).display() == "1.234,50 €"
        assert datos.get_cell(2, 1).fmt.number_format == "date_dmy"
        assert datos.get_cell(2, 1).display() == "13/07/2026"


def test_roundtrip_preserves_cross_sheet_formula():
    wb = Workbook(sheets=[])
    s1 = wb.add_sheet("Datos")
    s2 = wb.add_sheet("Resumen")
    s1.set_raw(1, 1, "100")
    s2.set_raw(1, 1, "=Datos!A1*2")

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "cross_sheet.xlsx")
        save_workbook(wb, path)

        wb2 = load_workbook(path)
        resumen = wb2.sheet_by_name("Resumen")
        assert resumen.get_raw(1, 1) == "=Datos!A1*2"

        Engine(wb2).recalculate()
        assert resumen.get_cell(1, 1).value == 200
