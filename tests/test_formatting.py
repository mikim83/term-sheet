from termsheet.model.cell import Cell, CellFormat
from termsheet.model.formatting import FORMATS, format_display, label_for


def test_eur_es_format():
    assert format_display("eur_es", "1234.5", 1234.5) == "1.234,50 €"


def test_eur_prefix_format():
    assert format_display("eur_prefix", "1234.5", 1234.5) == "€1.234,50"


def test_usd_format():
    assert format_display("usd", "1234.5", 1234.5) == "$1,234.50"


def test_gbp_format():
    assert format_display("gbp", "1234.5", 1234.5) == "£1,234.50"


def test_negative_currency():
    assert format_display("eur_es", "-50", -50) == "-50,00 €"


def test_date_dmy_from_iso():
    assert format_display("date_dmy", "2026-07-13", "2026-07-13") == "13/07/2026"


def test_date_dmy_passthrough_already_formatted():
    assert format_display("date_dmy", "13/07/2026", "13/07/2026") == "13/07/2026"


def test_date_dmy_unparseable_falls_back_to_none():
    assert format_display("date_dmy", "no es una fecha", "no es una fecha") is None


def test_currency_on_non_numeric_falls_back_to_none():
    assert format_display("eur_es", "hola", "hola") is None


def test_general_format_returns_none():
    assert format_display(None, "42", 42) is None


def test_cell_display_applies_currency_format():
    cell = Cell(raw="1234.5", value=1234.5, fmt=CellFormat(number_format="eur_es"))
    assert cell.display() == "1.234,50 €"


def test_cell_display_error_takes_priority_over_format():
    cell = Cell(raw="=1/0", error="#DIV/0!", fmt=CellFormat(number_format="eur_es"))
    assert cell.display() == "#DIV/0!"


def test_all_formats_have_distinct_xlsx_codes():
    codes = [fmt.xlsx_code for fmt in FORMATS.values()]
    assert len(codes) == len(set(codes))


def test_label_for_general_and_known_key():
    assert "General" in label_for(None)
    assert "€" in label_for("eur_es")
