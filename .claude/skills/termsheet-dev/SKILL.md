---
name: termsheet-dev
description: Guía para desarrollar, extender o depurar TermSheet (la hoja de cálculo de terminal de este repo) — añadir fórmulas, temas, atajos de teclado, cambios en el formato .xlsx, o cualquier modificación de termsheet/. Úsala siempre que el usuario pida cambios, nuevas funciones, bugs o mejoras sobre este proyecto, aunque no mencione explícitamente "TermSheet" o "skill".
---

# Desarrollo de TermSheet

TermSheet es una hoja de cálculo de terminal, 100% manejable con teclado, compatible con `.xlsx` real (incluidos archivos exportados de Google Sheets). Corre en Windows, macOS y Linux vía Textual.

## Arquitectura (dónde tocar cada cosa)

```
termsheet/
  model/
    cell.py             # Cell (raw, value, error, formato) y CellFormat
    coords.py            # Conversión A1 <-> (fila, columna)
    workbook.py           # Sheet (grid dispersa) y Workbook (lista de Sheets)
    formula_engine.py      # Tokenizer, parser, evaluador y FUNCTIONS{}
    undo.py                # Command pattern: SetCellCommand, BulkSetCommand, UndoStack
  io/
    xlsx_io.py           # load_workbook/save_workbook (openpyxl), mapeo con Google Sheets
  ui/
    themes.py             # THEMES{} y THEME_ORDER — los 5 temas de color
    dialogs.py             # InputDialog, HelpDialog, ThemeDialog (ModalScreen)
    statusbar.py            # Barra de estado inferior
  clipboard.py            # RangeClipboard (portapapeles interno + pyperclip)
  config.py               # Persistencia de tema en ~/.termsheet/config.toml
  grid.py                 # SheetGrid: DataTable de Textual, navegación y render
  app.py                  # TermSheetApp: bindings de teclado, orquesta todo lo anterior
tests/                   # pytest — un archivo por módulo del modelo
scripts/                 # build_windows.ps1, build_macos.sh (PyInstaller)
```

El modelo (`model/`) es independiente de Textual a propósito — así se puede testear fórmulas, undo y xlsx sin levantar la UI. Nunca importes Textual dentro de `model/` ni `io/`.

## Tareas comunes

**Añadir una función de fórmula** (ej. `PROMEDIO`, `SI`): edítala en `model/formula_engine.py`. Escribe la función `fn_xxx(args)` que reciba una lista de argumentos ya evaluados (usa `_flatten`/`_to_number` si mezclas números y rangos), y regístrala en el dict `FUNCTIONS` con su nombre en inglés y en español si aplica (ej. `"SUM": fn_sum, "SUMA": fn_sum`). Lanza `FormulaError("#COD!")` para errores estilo Excel. Añade un test en `tests/test_formula_engine.py`.

**Añadir un tema de color**: añade una entrada `Theme(...)` en `THEMES` y su key en `THEME_ORDER`, en `ui/themes.py`. El selector (`Ctrl+T`) y la persistencia en `config.py` ya recorren `THEME_ORDER` automáticamente, no hace falta tocar nada más.

**Añadir un atajo de teclado**: añade un `Binding(...)` en `TermSheetApp.BINDINGS` (`app.py`) y su método `action_xxx`. Ojo: `DataTable` (la clase base de `SheetGrid`) ya captura `enter`, las flechas, `pageup/down`, `home/end` y `ctrl+home/end` para su propia navegación — si necesitas interceptar una de esas teclas, hazlo vía el mensaje correspondiente (`on_data_table_cell_selected`, `on_data_table_cell_highlighted`) en vez de un `Binding`, porque el binding nunca burbujeará desde el widget con foco hasta la App.

**Cambiar el formato de guardado/lectura .xlsx**: todo vive en `io/xlsx_io.py`. `load_workbook` puebla el modelo a partir de un `openpyxl.Workbook` (usa `data_only=False` para preservar fórmulas, no valores calculados). `save_workbook` hace el camino inverso. Si tocas esto, verifica siempre con un test de round-trip (guardar y volver a cargar debe preservar fórmulas y multi-hoja) — hay un ejemplo en `tests/test_xlsx_io.py`.

**Cambiar undo/redo o portapapeles**: usa siempre el patrón Command (`model/undo.py`) para cualquier mutación de celdas desde la UI — nunca llames a `sheet.set_raw()` directamente desde `app.py`, pasa por `self.undo_stack.execute(SetCellCommand(...))` o `BulkSetCommand(...)` para que quede en la pila de deshacer.

## Recalculo de fórmulas

El motor (`model/formula_engine.py::Engine`) no mantiene un grafo de dependencias persistente: `Engine.recalculate()` reevalúa todas las celdas fórmula del workbook de forma perezosa y memoizada, con detección de ciclos vía un set `_visiting`. Esto significa que **después de cualquier cambio de celda hay que llamar a `self.engine.recalculate()` y luego `grid.refresh_from_sheet(sheet)`** — mira cualquier `action_*` en `app.py` que edite celdas como plantilla (siguen todas el mismo patrón: `undo_stack.execute(...)` → `engine.recalculate()` → `grid.refresh_from_sheet(sheet)` → `refresh_status()`).

## Cómo ejecutar y probar

```bash
cd ~/repos/term-sheet
source .venv/bin/activate        # el venv ya existe con las deps instaladas
python -m termsheet.app           # ejecutar interactivamente
pytest tests/ -q                  # tests unitarios del modelo (rápidos, sin UI)
```

Para probar cambios en la UI **sin terminal interactiva** (útil en este entorno de agente, donde no hay TTY), usa el modo headless de Textual con `run_test()` y `Pilot.press(...)`:

```python
import asyncio
from termsheet.app import TermSheetApp

async def main():
    app = TermSheetApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        grid = app.query_one("SheetGrid")
        grid.move_to(1, 1)
        await pilot.press("enter")          # entra en modo edición
        await pilot.pause()
        for ch in "=1+2":
            await pilot.press(ch)
        await pilot.press("enter")           # confirma
        await pilot.pause()
        print(app.workbook.active_sheet.get_cell(1, 1).display())  # -> 3

asyncio.run(main())
```

Este patrón (crear la app, `run_test()`, `pilot.press(...)`, `pilot.pause()` tras cada acción que dispare un mensaje async) es la forma de verificar de extremo a extremo cualquier flujo de teclado nuevo antes de darlo por terminado — no te fíes solo de que el código "se vea bien"; los mensajes de Textual son asíncronos y los bugs de foco/bindings no se detectan leyendo el código.

## Al terminar un cambio

1. Corre `pytest tests/ -q` — deben seguir pasando los tests existentes y cualquiera nuevo que añadas para la función/comportamiento tocado.
2. Si tocaste teclado o UI, verifica con el patrón headless de arriba el flujo concreto que cambiaste.
3. Si el cambio afecta al empaquetado (nuevas dependencias en `pyproject.toml`), recuerda que `scripts/build_windows.ps1` y `scripts/build_macos.sh` instalan desde `pyproject.toml` — no hace falta tocarlos salvo que cambie el punto de entrada.
