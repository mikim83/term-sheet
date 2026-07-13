"""Formatos de celda: moneda y fecha.

`CellFormat.number_format` guarda una de las claves de `FORMATS` (o `None`
para "General"). `format_display` traduce esa clave + el valor calculado de
la celda al texto final que se muestra en la grilla. `xlsx_io` traduce esas
mismas claves a códigos de formato de Excel al guardar, y viceversa al leer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional


@dataclass(frozen=True)
class NumberFormat:
    key: str
    label: str
    xlsx_code: str
    kind: str  # "currency" o "date"


def _format_currency(value: object, thousands: str, decimal: str, symbol: str, after: bool) -> Optional[str]:
    try:
        num = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    negative = num < 0
    text = f"{abs(num):,.2f}"
    text = text.replace(",", "\x00").replace(".", decimal).replace("\x00", thousands)
    text = f"{text} {symbol}" if after else f"{symbol}{text}"
    return f"-{text}" if negative else text


_DATE_INPUT_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y")


def _format_date_dmy(raw: str) -> Optional[str]:
    raw = raw.strip()
    if not raw:
        return None
    for fmt in _DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return None


FORMATS: dict[str, NumberFormat] = {
    "eur_es": NumberFormat("eur_es", "Euro — 1.234,56 €", '#,##0.00" €"', "currency"),
    "eur_prefix": NumberFormat("eur_prefix", "Euro — €1.234,56", '"€"#,##0.00', "currency"),
    "usd": NumberFormat("usd", "Dólar — $1,234.56", '"$"#,##0.00', "currency"),
    "gbp": NumberFormat("gbp", "Libra — £1,234.56", '"£"#,##0.00', "currency"),
    "date_dmy": NumberFormat("date_dmy", "Fecha — DD/MM/AAAA", "DD/MM/YYYY", "date"),
}

FORMAT_ORDER = ["eur_es", "eur_prefix", "usd", "gbp", "date_dmy"]

_CURRENCY_RENDER: dict[str, Callable[[object], Optional[str]]] = {
    "eur_es": lambda v: _format_currency(v, ".", ",", "€", after=True),
    "eur_prefix": lambda v: _format_currency(v, ".", ",", "€", after=False),
    "usd": lambda v: _format_currency(v, ",", ".", "$", after=False),
    "gbp": lambda v: _format_currency(v, ",", ".", "£", after=False),
}

XLSX_CODE_TO_KEY: dict[str, str] = {fmt.xlsx_code: key for key, fmt in FORMATS.items()}


def format_display(format_key: Optional[str], raw: str, value: object) -> Optional[str]:
    """Texto formateado para (raw, value) según format_key, o None si no aplica
    (en cuyo caso se usa el display por defecto de la celda)."""
    if not format_key:
        return None
    fmt = FORMATS.get(format_key)
    if fmt is None:
        return None
    if fmt.kind == "currency":
        return _CURRENCY_RENDER[format_key](value)
    if fmt.kind == "date":
        return _format_date_dmy(raw)
    return None


def label_for(format_key: Optional[str]) -> str:
    if not format_key:
        return "General (sin formato)"
    fmt = FORMATS.get(format_key)
    return fmt.label if fmt else "General (sin formato)"
