"""Portapapeles de rangos: copia/corta/pega múltiples celdas, con fallback al
portapapeles del sistema (pyperclip) para interoperar con otras aplicaciones."""

from __future__ import annotations

try:
    import pyperclip

    _HAS_SYSTEM_CLIPBOARD = True
except Exception:  # pragma: no cover - pyperclip puede fallar sin backend disponible
    _HAS_SYSTEM_CLIPBOARD = False


class RangeClipboard:
    def __init__(self):
        self.rows: list[list[str]] = []
        self.cut = False

    def set(self, rows: list[list[str]], cut: bool = False) -> None:
        self.rows = rows
        self.cut = cut
        if _HAS_SYSTEM_CLIPBOARD:
            text = "\n".join("\t".join(r) for r in rows)
            try:
                pyperclip.copy(text)
            except Exception:
                pass

    def get(self) -> list[list[str]]:
        if self.rows:
            return self.rows
        if _HAS_SYSTEM_CLIPBOARD:
            try:
                text = pyperclip.paste()
            except Exception:
                text = ""
            if text:
                return [line.split("\t") for line in text.splitlines()]
        return []

    def is_empty(self) -> bool:
        return not self.rows and not (_HAS_SYSTEM_CLIPBOARD and self._system_has_text())

    def _system_has_text(self) -> bool:
        try:
            return bool(pyperclip.paste())
        except Exception:
            return False
