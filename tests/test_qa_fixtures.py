"""QA con un .xlsx real aportado por el usuario (qa_samples/QA.xlsx): tres
hojas, fórmulas dentro de hoja, referencias entre hojas (con y sin espacios
en el nombre), y columnas de fecha con formato nativo de Excel — cubre en
un solo archivo real varias de las funcionalidades más delicadas del motor.
"""

from pathlib import Path
import tempfile

from termsheet.io.xlsx_io import load_workbook, save_workbook
from termsheet.model.formula_engine import Engine

FIXTURE = Path(__file__).parent.parent / "qa_samples" / "QA.xlsx"


def _load_and_recalculate():
    wb = load_workbook(str(FIXTURE))
    Engine(wb).recalculate()
    return wb


def test_loads_all_three_sheets():
    wb = _load_and_recalculate()
    assert [s.name for s in wb.sheets] == ["Inicio", "Segunda Hoja", "Resultados"]


def test_same_sheet_formula_totals():
    wb = _load_and_recalculate()
    inicio = wb.sheet_by_name("Inicio")
    # Agua: 4 x 4.6
    assert inicio.get_cell(4, 5).value == 18.4
    # Detergente: 2 x 1.6132
    assert round(inicio.get_cell(7, 5).value, 4) == 3.2264
    assert all(inicio.get_cell(r, 5).error is None for r in range(4, 8))


def test_cross_sheet_formula_with_spaces_in_sheet_name():
    wb = _load_and_recalculate()
    resultados = wb.sheet_by_name("Resultados")
    # =Inicio!E4+'Segunda Hoja'!E5 -> 18.4 + 6.4
    cell = resultados.get_cell(5, 1)
    assert cell.error is None
    assert round(cell.value, 4) == 24.8


def test_chained_formula_referencing_cross_sheet_result():
    wb = _load_and_recalculate()
    resultados = wb.sheet_by_name("Resultados")
    # B5 = A5 * 1.16, donde A5 ya es una fórmula entre hojas
    assert resultados.get_cell(5, 2).error is None
    assert round(resultados.get_cell(5, 2).value, 3) == 28.768


def test_date_columns_import_with_clean_dmy_display():
    wb = _load_and_recalculate()
    inicio = wb.sheet_by_name("Inicio")
    date_cell = inicio.get_cell(4, 2)
    assert date_cell.fmt.number_format == "date_dmy"
    assert date_cell.display() == "10/10/2026"
    assert date_cell.error is None


def test_roundtrip_preserves_dates_and_cross_sheet_formulas():
    wb = _load_and_recalculate()
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "qa_roundtrip.xlsx")
        save_workbook(wb, path)

        wb2 = load_workbook(path)
        Engine(wb2).recalculate()

        inicio = wb2.sheet_by_name("Inicio")
        assert inicio.get_cell(4, 2).display() == "10/10/2026"

        resultados = wb2.sheet_by_name("Resultados")
        assert resultados.get_raw(5, 1) == "=Inicio!E4+'Segunda Hoja'!E5"
        assert round(resultados.get_cell(5, 1).value, 4) == 24.8
