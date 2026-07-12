from termsheet.model.formula_engine import Engine
from termsheet.model.workbook import Workbook


def make_engine():
    wb = Workbook()
    return wb, wb.active_sheet, Engine(wb)


def test_basic_arithmetic():
    wb, sheet, eng = make_engine()
    sheet.set_raw(1, 1, "10")
    sheet.set_raw(1, 2, "20")
    sheet.set_raw(1, 3, "=A1+B1*2")
    eng.recalculate()
    assert sheet.get_cell(1, 3).value == 50


def test_sum_range():
    wb, sheet, eng = make_engine()
    for c in range(1, 4):
        sheet.set_raw(1, c, str(c * 10))
    sheet.set_raw(2, 1, "=SUMA(A1:C1)")
    eng.recalculate()
    assert sheet.get_cell(2, 1).value == 60


def test_if_function():
    wb, sheet, eng = make_engine()
    sheet.set_raw(1, 1, "10")
    sheet.set_raw(1, 2, '=SI(A1>5,"grande","pequeno")')
    eng.recalculate()
    assert sheet.get_cell(1, 2).value == "grande"


def test_div_zero_error():
    wb, sheet, eng = make_engine()
    sheet.set_raw(1, 1, "=1/0")
    eng.recalculate()
    assert sheet.get_cell(1, 1).error == "#DIV/0!"


def test_circular_reference():
    wb, sheet, eng = make_engine()
    sheet.set_raw(1, 1, "=B1")
    sheet.set_raw(1, 2, "=A1")
    eng.recalculate()
    assert sheet.get_cell(1, 1).error == "#CIRC!"
    assert sheet.get_cell(1, 2).error == "#CIRC!"


def test_vlookup():
    wb, sheet, eng = make_engine()
    sheet.set_raw(1, 1, "1")
    sheet.set_raw(1, 2, "uno")
    sheet.set_raw(2, 1, "2")
    sheet.set_raw(2, 2, "dos")
    sheet.set_raw(3, 1, "=BUSCARV(2,A1:B2,2)")
    eng.recalculate()
    assert sheet.get_cell(3, 1).value == "dos"
