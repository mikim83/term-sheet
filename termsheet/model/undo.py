"""Undo/redo stack using the Command pattern."""

from __future__ import annotations

from dataclasses import dataclass, field


class Command:
    def do(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError


@dataclass
class SetCellCommand(Command):
    sheet: object
    row: int
    col: int
    new_raw: str
    old_raw: str = field(default="", init=False)

    def do(self) -> None:
        self.old_raw = self.sheet.get_raw(self.row, self.col)
        self.sheet.set_raw(self.row, self.col, self.new_raw)

    def undo(self) -> None:
        self.sheet.set_raw(self.row, self.col, self.old_raw)


@dataclass
class BulkSetCommand(Command):
    """Sets multiple cells at once (paste, delete range)."""

    sheet: object
    changes: dict[tuple[int, int], str]  # (row, col) -> new raw value
    old_values: dict[tuple[int, int], str] = field(default_factory=dict, init=False)

    def do(self) -> None:
        for (row, col), new_raw in self.changes.items():
            self.old_values[(row, col)] = self.sheet.get_raw(row, col)
            self.sheet.set_raw(row, col, new_raw)

    def undo(self) -> None:
        for (row, col), old_raw in self.old_values.items():
            self.sheet.set_raw(row, col, old_raw)


@dataclass
class SetFormatCommand(Command):
    """Aplica un formato de número (moneda/fecha) a un rango de celdas."""

    sheet: object
    cells: list[tuple[int, int]]
    new_format: str | None
    old_formats: dict[tuple[int, int], str | None] = field(default_factory=dict, init=False)

    def do(self) -> None:
        for row, col in self.cells:
            cell = self.sheet.ensure_cell(row, col)
            self.old_formats[(row, col)] = cell.fmt.number_format
            cell.fmt.number_format = self.new_format

    def undo(self) -> None:
        for (row, col), old_format in self.old_formats.items():
            self.sheet.ensure_cell(row, col).fmt.number_format = old_format


class UndoStack:
    def __init__(self, limit: int = 100):
        self.limit = limit
        self._undo: list[Command] = []
        self._redo: list[Command] = []

    def execute(self, command: Command) -> None:
        command.do()
        self._undo.append(command)
        if len(self._undo) > self.limit:
            self._undo.pop(0)
        self._redo.clear()

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def undo(self) -> None:
        if not self._undo:
            return
        command = self._undo.pop()
        command.undo()
        self._redo.append(command)

    def redo(self) -> None:
        if not self._redo:
            return
        command = self._redo.pop()
        command.do()
        self._undo.append(command)
