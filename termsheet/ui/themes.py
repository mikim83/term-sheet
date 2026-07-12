"""Paleta de temas de color seleccionables en caliente con Ctrl+T."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    key: str
    label: str
    background: str
    foreground: str
    header_bg: str
    header_fg: str
    selection_bg: str
    selection_fg: str
    statusbar_bg: str
    statusbar_fg: str
    error_fg: str


THEMES: dict[str, Theme] = {
    "classic": Theme(
        key="classic",
        label="Clásico (negro/blanco)",
        background="#000000",
        foreground="#f0f0f0",
        header_bg="#1c1c1c",
        header_fg="#c0c0c0",
        selection_bg="#444444",
        selection_fg="#ffffff",
        statusbar_bg="#1c1c1c",
        statusbar_fg="#d0d0d0",
        error_fg="#ff5f5f",
    ),
    "inverted": Theme(
        key="inverted",
        label="Invertido (blanco/negro)",
        background="#ffffff",
        foreground="#101010",
        header_bg="#e0e0e0",
        header_fg="#202020",
        selection_bg="#c8c8c8",
        selection_fg="#000000",
        statusbar_bg="#e0e0e0",
        statusbar_fg="#101010",
        error_fg="#b00000",
    ),
    "excel_green": Theme(
        key="excel_green",
        label="Excel verde",
        background="#ffffff",
        foreground="#1a1a1a",
        header_bg="#1e6b3c",
        header_fg="#ffffff",
        selection_bg="#c6e6d1",
        selection_fg="#0b3d20",
        statusbar_bg="#1e6b3c",
        statusbar_fg="#ffffff",
        error_fg="#c0392b",
    ),
    "solarized_dark": Theme(
        key="solarized_dark",
        label="Solarized Dark",
        background="#002b36",
        foreground="#eee8d5",
        header_bg="#073642",
        header_fg="#93a1a1",
        selection_bg="#586e75",
        selection_fg="#fdf6e3",
        statusbar_bg="#073642",
        statusbar_fg="#b58900",
        error_fg="#dc322f",
    ),
    "high_contrast": Theme(
        key="high_contrast",
        label="Alto contraste (accesibilidad)",
        background="#000000",
        foreground="#ffff00",
        header_bg="#000000",
        header_fg="#ffffff",
        selection_bg="#ffffff",
        selection_fg="#000000",
        statusbar_bg="#000000",
        statusbar_fg="#ffff00",
        error_fg="#ff3030",
    ),
}

THEME_ORDER = ["classic", "inverted", "excel_green", "solarized_dark", "high_contrast"]

DEFAULT_THEME = "classic"


def get_theme(key: str) -> Theme:
    return THEMES.get(key, THEMES[DEFAULT_THEME])


def next_theme_key(current: str) -> str:
    idx = THEME_ORDER.index(current) if current in THEME_ORDER else -1
    return THEME_ORDER[(idx + 1) % len(THEME_ORDER)]
