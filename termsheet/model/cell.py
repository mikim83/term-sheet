from __future__ import annotations

from dataclasses import dataclass, field

from .formatting import format_display


@dataclass
class CellFormat:
    bold: bool = False
    italic: bool = False
    align: str = "left"  # left, right, center
    number_format: str | None = None
    col_width: int | None = None
    font_color: str | None = None  # hex "RRGGBB", None = color por defecto del tema
    bg_color: str | None = None  # hex "RRGGBB", None = sin relleno
    # Grosor/estilo de línea aplicado a los 4 lados de la celda al exportar a
    # .xlsx (nombres de estilo de openpyxl: thin/medium/thick/dashed/dotted/
    # double/hair/...). Por defecto una línea gris discontinua fina, para que
    # el libro se vea con la rejilla clásica de Excel al abrirlo. La terminal
    # no puede dibujar distintos grosores de línea de forma fiable (ver
    # decisión en README), así que este valor se respeta al leer/escribir
    # .xlsx mucho pero no cambia el renderizado dentro de la app.
    border_style: str | None = "dashed"
    border_color: str = "808080"


@dataclass
class Cell:
    """A single cell: raw input (formula or literal) plus cached computed value."""

    raw: str = ""
    value: object = ""
    error: str | None = None
    fmt: CellFormat = field(default_factory=CellFormat)

    @property
    def is_formula(self) -> bool:
        return self.raw.startswith("=")

    def display(self) -> str:
        if self.error:
            return self.error
        formatted = format_display(self.fmt.number_format, self.raw, self.value)
        if formatted is not None:
            return formatted
        if self.value is None:
            return ""
        if isinstance(self.value, float):
            if self.value == int(self.value):
                return str(int(self.value))
            return f"{self.value:g}"
        return str(self.value)
