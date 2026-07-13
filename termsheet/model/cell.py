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
