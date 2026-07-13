from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

HELP_TEXT = """\
NAVEGACIÓN
  Flechas               Mover el cursor una celda
  PageUp / PageDown     Subir / bajar una página
  Home / End            Principio / fin de la fila
  Ctrl+Home             Ir a A1
  Ctrl+G                Ir a una celda por nombre (ej. B12)
  Ctrl+F                Buscar texto en la hoja activa

EDICIÓN
  Enter / F2            Editar la celda actual
  Esc                   Cancelar la edición en curso
  Tab                   Confirma la edición y avanza a la derecha
  Delete                Borrar el contenido de la celda o selección

SELECCIÓN DE RANGO (varias celdas a la vez)
  Shift+flechas         Extiende la selección desde la celda actual.
                        Ojo: algunos terminales (sobre todo en macOS) no
                        distinguen Shift+flecha de una flecha normal y esta
                        combinación puede no hacer nada — en ese caso usa F8.
  F8                    Alternativa a Shift+flechas: activa "modo selección"
                        (igual que en Excel). Con el modo activo, las flechas
                        normales extienden la selección; pulsa F8 otra vez
                        para desactivarlo. Funciona en cualquier terminal.
  Ctrl+C / Ctrl+X       Copiar / cortar la celda o el rango seleccionado
  Ctrl+V                Pegar en la celda actual (esquina superior izquierda)

FORMATO
  Ctrl+1                Formato de celda: moneda (varios tipos) o fecha
                        DD/MM/AAAA, aplicado a la celda o rango seleccionado

DESHACER
  Ctrl+Z / Ctrl+Y       Deshacer / rehacer (incluye contenido y formato)

ARCHIVO
  Ctrl+S                Guardar como .xlsx
  Ctrl+O                Abrir un .xlsx (incluye los exportados de Google Sheets)

HOJAS
  Ctrl+N                Nueva hoja (pestaña) en este mismo libro
  Ctrl+R                Renombrar la hoja activa
  Alt+PageUp/PageDown   Cambiar a la hoja anterior/siguiente
                        (la hoja activa aparece resaltada en la barra inferior)

VISTA Y AYUDA
  Ctrl+T                Cambiar el tema de color
  F1                    Esta ayuda · Esc o F1 para cerrar
  Ctrl+Q                Salir del programa
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
        width: 78;
        height: auto;
        max-height: 90%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
        overflow-y: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help_box"):
            yield Label("Atajos de teclado")
            yield Static(HELP_TEXT)

    def on_key(self, event) -> None:
        if event.key in ("escape", "f1"):
            self.dismiss(None)


class ChoiceDialog(ModalScreen[Optional[str]]):
    """Diálogo modal de lista: flechas/hjkl para moverse, Enter elige, Esc cancela.
    Usado tanto para el selector de tema como para el de formato de celda."""

    DEFAULT_CSS = """
    ChoiceDialog {
        align: center middle;
    }
    #choice_box {
        width: 55;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, prompt: str, choices: list[tuple[str, str]], current: str | None):
        super().__init__()
        self.prompt = prompt
        self.choices = choices
        self.current = current if current is not None else choices[0][0]

    def compose(self) -> ComposeResult:
        with Vertical(id="choice_box"):
            yield Label(self.prompt)
            for key, label in self.choices:
                marker = "›" if key == self.current else " "
                yield Static(f"{marker} {label}", id=f"choice_{key}")

    def on_key(self, event) -> None:
        keys = [k for k, _ in self.choices]
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
        for key, label in self.choices:
            widget = self.query_one(f"#choice_{key}", Static)
            marker = "›" if key == self.current else " "
            widget.update(f"{marker} {label}")
