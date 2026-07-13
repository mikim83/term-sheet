"""Navegador de ficheros simple para abrir/guardar .xlsx sin salir del programa."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static


class FileBrowserDialog(ModalScreen[Optional[str]]):
    """Navega carpetas con flechas + Enter. En modo "save" añade un campo de
    nombre de archivo editable (Tab para saltar a él), siempre precargado
    con el nombre actual — así sirve tanto para guardar como para "guardar
    como" si se cambia el nombre o la carpeta."""

    DEFAULT_CSS = """
    FileBrowserDialog {
        align: center middle;
    }
    #browser_box {
        width: 72;
        height: 24;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    #file_list {
        height: 1fr;
    }
    #current_dir, #hint {
        color: $text-muted;
    }
    """

    def __init__(self, mode: str, start_path: Optional[str] = None):
        super().__init__()
        self.mode = mode  # "open" o "save"
        start = Path(start_path).expanduser() if start_path else Path.cwd()
        if start.is_dir():
            self.current_dir = start
            self.filename = "libro.xlsx"
        else:
            self.current_dir = start.parent if start.parent.exists() else Path.cwd()
            self.filename = start.name or "libro.xlsx"

    def compose(self) -> ComposeResult:
        title = "Abrir archivo .xlsx" if self.mode == "open" else "Guardar como (.xlsx)"
        hint = "Enter: abrir/entrar · Backspace: subir · Esc: cancelar"
        if self.mode == "save":
            hint += " · Tab: editar nombre, Enter para confirmar"
        with Vertical(id="browser_box"):
            yield Label(title)
            yield Static(str(self.current_dir), id="current_dir")
            yield ListView(id="file_list")
            if self.mode == "save":
                yield Input(value=self.filename, placeholder="nombre_archivo.xlsx", id="filename_input")
            yield Label(hint, id="hint")

    async def on_mount(self) -> None:
        await self._refresh_list()
        self.query_one(ListView).focus()

    def _entries(self) -> tuple[list[Path], list[Path]]:
        try:
            items = list(self.current_dir.iterdir())
        except OSError:
            items = []
        dirs = sorted(
            (p for p in items if p.is_dir() and not p.name.startswith(".")), key=lambda p: p.name.lower()
        )
        if self.mode == "open":
            files = sorted(
                (p for p in items if p.is_file() and p.suffix.lower() == ".xlsx"), key=lambda p: p.name.lower()
            )
        else:
            files = []
        return dirs, files

    async def _refresh_list(self) -> None:
        self.query_one("#current_dir", Static).update(str(self.current_dir))
        list_view = self.query_one(ListView)
        await list_view.clear()
        dirs, files = self._entries()
        if self.current_dir.parent != self.current_dir:
            await list_view.append(ListItem(Label(".. (subir)"), name="up"))
        for d in dirs:
            await list_view.append(ListItem(Label(f"\U0001f4c1 {d.name}/"), name=f"dir:{d.name}"))
        for f in files:
            await list_view.append(ListItem(Label(f"\U0001f4c4 {f.name}"), name=f"file:{f.name}"))
        if list_view.children:
            list_view.index = 0

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        name = event.item.name
        if name == "up":
            self.current_dir = self.current_dir.parent
            await self._refresh_list()
        elif name and name.startswith("dir:"):
            self.current_dir = self.current_dir / name[len("dir:") :]
            await self._refresh_list()
        elif name and name.startswith("file:"):
            self.dismiss(str(self.current_dir / name[len("file:") :]))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "filename_input":
            return
        filename = event.value.strip()
        if not filename:
            return
        if not filename.lower().endswith(".xlsx"):
            filename += ".xlsx"
        self.dismiss(str(self.current_dir / filename))

    async def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "backspace" and self.focused is self.query_one(ListView):
            if self.current_dir.parent != self.current_dir:
                self.current_dir = self.current_dir.parent
                await self._refresh_list()
