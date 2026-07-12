from __future__ import annotations

from textual.widgets import Static


class StatusBar(Static):
    def set_status(self, cell_addr: str, mode: str, raw: str, sheet_name: str, theme_label: str) -> None:
        self.update(f" {sheet_name} | {cell_addr} | {mode} | {theme_label}  ›  {raw}")
