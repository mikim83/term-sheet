from termsheet.model.undo import BulkSetCommand, SetCellCommand, UndoStack
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
