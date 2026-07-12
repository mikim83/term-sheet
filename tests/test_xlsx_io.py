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
