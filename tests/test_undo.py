from termsheet.model.undo import BulkSetCommand, SetCellCommand, SetStyleCommand, UndoStack
from termsheet.model.workbook import Workbook


def test_set_cell_undo_redo():
    wb = Workbook()
    sheet = wb.active_sheet
    stack = UndoStack()

    stack.execute(SetCellCommand(sheet, 1, 1, "10"))
    assert sheet.get_raw(1, 1) == "10"

    stack.execute(SetCellCommand(sheet, 1, 1, "20"))
    assert sheet.get_raw(1, 1) == "20"

    stack.undo()
    assert sheet.get_raw(1, 1) == "10"

    stack.undo()
    assert sheet.get_raw(1, 1) == ""

    stack.redo()
    assert sheet.get_raw(1, 1) == "10"


def test_bulk_set_undo():
    wb = Workbook()
    sheet = wb.active_sheet
    stack = UndoStack()

    stack.execute(BulkSetCommand(sheet, {(1, 1): "a", (1, 2): "b"}))
    assert sheet.get_raw(1, 1) == "a"
    assert sheet.get_raw(1, 2) == "b"

    stack.undo()
    assert sheet.get_raw(1, 1) == ""
    assert sheet.get_raw(1, 2) == ""


def test_set_style_undo_only_touches_the_updated_keys():
    wb = Workbook()
    sheet = wb.active_sheet
    stack = UndoStack()
    cell = sheet.ensure_cell(1, 1)
    cell.fmt.bold = True  # atributo NO tocado por el comando, debe sobrevivir intacto

    stack.execute(SetStyleCommand(sheet, [(1, 1)], {"font_color": "FF0000", "bg_color": "00FF00"}))
    assert cell.fmt.font_color == "FF0000"
    assert cell.fmt.bg_color == "00FF00"
    assert cell.fmt.bold is True

    stack.undo()
    assert cell.fmt.font_color is None
    assert cell.fmt.bg_color is None
    assert cell.fmt.bold is True

    stack.redo()
    assert cell.fmt.font_color == "FF0000"
    assert cell.fmt.bg_color == "00FF00"
