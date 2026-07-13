"""Carga y guarda libros en formato .xlsx real usando openpyxl.

Compatible con archivos de Excel y con .xlsx exportados manualmente desde
Google Sheets (Archivo -> Descargar -> Microsoft Excel).
"""

from __future__ import annotations

from openpyxl import Workbook as XlWorkbook
from openpyxl import load_workbook as xl_load_workbook
from openpyxl.utils import get_column_letter

from ..model.cell import CellFormat
from ..model.formatting import FORMATS, XLSX_CODE_TO_KEY
from ..model.workbook import Sheet, Workbook


def load_workbook(path: str) -> Workbook:
    xl_wb = xl_load_workbook(path, data_only=False)
    wb = Workbook(sheets=[])
    for xl_sheet in xl_wb.worksheets:
        sheet = Sheet(xl_sheet.title)
        for row in xl_sheet.iter_rows():
            for xl_cell in row:
                if xl_cell.value is None:
                    continue
                raw = _to_raw(xl_cell.value)
                cell = sheet.set_raw(xl_cell.row, xl_cell.column, raw)
                xl_format = xl_cell.number_format
                number_format = XLSX_CODE_TO_KEY.get(xl_format, xl_format if xl_format != "General" else None)
                cell.fmt = CellFormat(
                    bold=bool(xl_cell.font and xl_cell.font.bold),
                    italic=bool(xl_cell.font and xl_cell.font.italic),
                    align=(xl_cell.alignment.horizontal or "left") if xl_cell.alignment else "left",
                    number_format=number_format,
                )
        for col_letter, dim in xl_sheet.column_dimensions.items():
            if dim.width:
                from openpyxl.utils import column_index_from_string

                sheet.col_widths[column_index_from_string(col_letter)] = int(dim.width)
        wb.sheets.append(sheet)
    if not wb.sheets:
        wb.sheets.append(Sheet("Hoja1"))
    wb.path = path
    return wb


def _to_raw(value) -> str:
    if isinstance(value, str) and value.startswith("="):
        return value
    return str(value)


def save_workbook(workbook: Workbook, path: str) -> None:
    xl_wb = XlWorkbook()
    xl_wb.remove(xl_wb.active)
    for sheet in workbook.sheets:
        xl_sheet = xl_wb.create_sheet(title=sheet.name)
        for row, col, cell in sheet.iter_cells():
            xl_cell = xl_sheet.cell(row=row, column=col)
            xl_cell.value = _cell_value_for_xlsx(cell)
            if cell.fmt.bold or cell.fmt.italic:
                xl_cell.font = xl_cell.font.copy(bold=cell.fmt.bold, italic=cell.fmt.italic)
            if cell.fmt.align != "left":
                xl_cell.alignment = xl_cell.alignment.copy(horizontal=cell.fmt.align)
            if cell.fmt.number_format:
                known = FORMATS.get(cell.fmt.number_format)
                xl_cell.number_format = known.xlsx_code if known else cell.fmt.number_format
        for col, width in sheet.col_widths.items():
            xl_sheet.column_dimensions[get_column_letter(col)].width = width
    xl_wb.save(path)
    workbook.path = path


def _cell_value_for_xlsx(cell):
    if cell.is_formula:
        return cell.raw
    raw = cell.raw
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw
