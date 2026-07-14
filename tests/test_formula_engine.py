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


def test_cross_sheet_cell_reference():
    wb = Workbook(sheets=[])
    s1 = wb.add_sheet("Hoja1")
    s2 = wb.add_sheet("Hoja2")
    s1.set_raw(1, 1, "10")
    s2.set_raw(1, 1, "=Hoja1!A1+5")
    eng = Engine(wb)
    eng.recalculate()
    assert s2.get_cell(1, 1).value == 15
    assert s2.get_cell(1, 1).error is None


def test_cross_sheet_range_in_function():
    wb = Workbook(sheets=[])
    s1 = wb.add_sheet("Datos")
    s2 = wb.add_sheet("Resumen")
    s1.set_raw(1, 1, "10")
    s1.set_raw(1, 2, "20")
    s2.set_raw(1, 1, "=SUMA(Datos!A1:B1)")
    eng = Engine(wb)
    eng.recalculate()
    assert s2.get_cell(1, 1).value == 30


def test_cross_sheet_reference_with_quoted_name_with_spaces():
    wb = Workbook(sheets=[])
    s1 = wb.add_sheet("Mi Hoja Con Espacios")
    s2 = wb.add_sheet("Otra")
    s1.set_raw(1, 1, "7")
    s2.set_raw(1, 1, "='Mi Hoja Con Espacios'!A1*2")
    eng = Engine(wb)
    eng.recalculate()
    assert s2.get_cell(1, 1).value == 14


def test_cross_sheet_reference_chained_through_three_sheets():
    wb = Workbook(sheets=[])
    s1 = wb.add_sheet("A")
    s2 = wb.add_sheet("B")
    s3 = wb.add_sheet("C")
    s1.set_raw(1, 1, "1")
    s2.set_raw(1, 1, "=A!A1+1")
    s3.set_raw(1, 1, "=B!A1+1")
    eng = Engine(wb)
    eng.recalculate()
    assert s3.get_cell(1, 1).value == 3


def test_cross_sheet_reference_to_missing_sheet_gives_ref_error():
    wb, sheet, eng = make_engine()
    sheet.set_raw(1, 1, "=NoExiste!A1")
    eng.recalculate()
    assert sheet.get_cell(1, 1).error == "#REF!"
