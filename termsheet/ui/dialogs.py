from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

HELP_TEXT = """\
Navegación:  flechas / hjkl · PageUp/PageDown · Home/End · Ctrl+Home (A1)
Edición:     Enter/F2 editar · Esc cancelar · Tab confirma y avanza
Rangos:      Shift+flechas seleccionar · Ctrl+C copiar · Ctrl+X cortar · Ctrl+V pegar
Deshacer:    Ctrl+Z deshacer · Ctrl+Y rehacer
Archivo:     Ctrl+S guardar · Ctrl+O abrir · Ctrl+N nueva hoja
Buscar:      Ctrl+G ir a celda · Ctrl+F buscar
Hojas:       Alt+PageUp/PageDown cambiar de hoja
Vista:       Ctrl+T cambiar tema de color
Ayuda:       F1 esta ayuda · Esc o F1 para cerrar
Salir:       Ctrl+Q salir del programa
"""


class InputDialog(ModalScreen[Optional[str]]):
    """Diálogo modal genérico de una línea: ir a celda, buscar, guardar como, abrir."""

    DEFAULT_CSS = """
    InputDialog {
        align: center middle;
    }
    #dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, title: str, placeholder: str = "", initial: str = ""):
        super().__init__()
        self.title_text = title
        self.placeholder = placeholder
        self.initial = initial

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.title_text)
            yield Input(placeholder=self.placeholder, value=self.initial, id="dialog_input")

    def on_mount(self) -> None:
        self.query_one("#dialog_input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


class HelpDialog(ModalScreen[None]):
    DEFAULT_CSS = """
    HelpDialog {
        align: center middle;
    }
    #help_box {
        width: 70;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help_box"):
            yield Label("Atajos de teclado")
            yield Static(HELP_TEXT)

    def on_key(self, event) -> None:
        if event.key in ("escape", "f1"):
            self.dismiss(None)


class ThemeDialog(ModalScreen[Optional[str]]):
    DEFAULT_CSS = """
    ThemeDialog {
        align: center middle;
    }
    #theme_box {
        width: 50;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, themes: list[tuple[str, str]], current: str):
        super().__init__()
        self.themes = themes
        self.current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="theme_box"):
            yield Label("Elige un tema (flechas + Enter, Esc cancela)")
            for key, label in self.themes:
                marker = "›" if key == self.current else " "
                yield Static(f"{marker} {label}", id=f"theme_{key}")

    def on_key(self, event) -> None:
        keys = [k for k, _ in self.themes]
        if event.key == "escape":
            self.dismiss(None)
        elif event.key in ("down", "j"):
            idx = (keys.index(self.current) + 1) % len(keys)
            self.current = keys[idx]
            self._refresh_markers()
        elif event.key in ("up", "k"):
            idx = (keys.index(self.current) - 1) % len(keys)
            self.current = keys[idx]
            self._refresh_markers()
        elif event.key == "enter":
            self.dismiss(self.current)

    def _refresh_markers(self) -> None:
        for key, label in self.themes:
            widget = self.query_one(f"#theme_{key}", Static)
            marker = "›" if key == self.current else " "
            widget.update(f"{marker} {label}")
