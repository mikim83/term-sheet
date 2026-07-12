"""Configuración persistente del usuario (tema, etc.) en ~/.termsheet/config.toml."""

from __future__ import annotations

from pathlib import Path

from .ui.themes import DEFAULT_THEME

CONFIG_DIR = Path.home() / ".termsheet"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def load_theme() -> str:
    if not CONFIG_FILE.exists():
        return DEFAULT_THEME
    try:
        for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("theme"):
                _, _, value = line.partition("=")
                return value.strip().strip('"')
    except OSError:
        pass
    return DEFAULT_THEME


def save_theme(theme_key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(f'theme = "{theme_key}"\n', encoding="utf-8")
