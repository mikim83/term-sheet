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
    workbook.py           # Sheet (grid dispersa, con ensure_cell) y Workbook (lista de Sheets)
    formula_engine.py      # Tokenizer, parser, evaluador y FUNCTIONS{}
    formatting.py           # FORMATS{} — formatos de moneda/fecha, format_display()
    undo.py                # Command pattern: SetCellCommand, BulkSetCommand, SetFormatCommand, UndoStack
  io/
    xlsx_io.py           # load_workbook/save_workbook (openpyxl), mapeo con Google Sheets
  ui/
    themes.py             # THEMES{} y THEME_ORDER — los 5 temas de color
    dialogs.py             # InputDialog, HelpDialog, ChoiceDialog (lista genérica: temas y formatos)
    file_browser.py        # FileBrowserDialog — navegador de carpetas para Ctrl+O/Ctrl+S
    statusbar.py            # Barra de estado inferior
  clipboard.py            # RangeClipboard (portapapeles interno + pyperclip)
  config.py               # Persistencia de tema en ~/.termsheet/config.toml
  grid.py                 # SheetGrid: DataTable de Textual, navegación y render
  app.py                  # TermSheetApp: bindings de teclado, orquesta todo lo anterior
tests/                   # pytest — un archivo por módulo del modelo
qa_samples/              # .xlsx reales aportados por el usuario, usados como fixtures de QA
scripts/                 # build_windows.ps1, build_macos.sh, build_linux.sh (PyInstaller)
```

El modelo (`model/`) es independiente de Textual a propósito — así se puede testear fórmulas, undo y xlsx sin levantar la UI. Nunca importes Textual dentro de `model/` ni `io/`.

## Tareas comunes

**Añadir una función de fórmula** (ej. `PROMEDIO`, `SI`): edítala en `model/formula_engine.py`. Escribe la función `fn_xxx(args)` que reciba una lista de argumentos ya evaluados (usa `_flatten`/`_to_number` si mezclas números y rangos), y regístrala en el dict `FUNCTIONS` con su nombre en inglés y en español si aplica (ej. `"SUM": fn_sum, "SUMA": fn_sum`). Lanza `FormulaError("#COD!")` para errores estilo Excel. Añade un test en `tests/test_formula_engine.py`.

**Añadir un tema de color**: añade una entrada `Theme(...)` en `THEMES` y su key en `THEME_ORDER`, en `ui/themes.py`. El selector (`Ctrl+T`) y la persistencia en `config.py` ya recorren `THEME_ORDER` automáticamente, no hace falta tocar nada más.

**Añadir un atajo de teclado**: añade un `Binding(...)` en `TermSheetApp.BINDINGS` (`app.py`) y su método `action_xxx`. Ojo con dos trampas relacionadas con que `SheetGrid` (DataTable) casi siempre tiene el foco:

1. `DataTable` captura `enter`, las flechas, `pageup/down`, `home/end` y `ctrl+home/end` para su propia navegación — si necesitas interceptar una de esas teclas exactas, hazlo vía el mensaje correspondiente (`on_data_table_cell_selected`, `on_data_table_cell_highlighted`) en vez de un `Binding`, porque el binding de la App nunca burbujeará desde el widget con foco.
2. **Colisiones heredadas no obvias**: `DataTable` hereda de `ScrollView`, que trae bindings propios como `ctrl+pageup`/`ctrl+pagedown` (paginado horizontal) que no aparecen listados en `DataTable.BINDINGS` a simple vista. Un `Binding` en `TermSheetApp` con esa misma tecla se registra sin error, pero nunca se ejecuta: el chequeo de bindings recorre la cadena desde el widget con foco hacia arriba (`Screen._modal_binding_chain`), así que el binding del widget enfocado gana silenciosamente y el de la App queda "muerto". Esto pasó de verdad con `Ctrl+PageUp`/`Ctrl+PageDown` para cambiar de hoja (ahora son `Alt+PageUp`/`Alt+PageDown`). Antes de elegir una tecla nueva, verifica que no colisiona:
   ```python
   for namespace, bindings in app.screen._modal_binding_chain:
       print(namespace, bindings.key_to_bindings.get("tu+tecla", ()))
   ```

**Abrir/guardar archivos**: `Ctrl+O`/`Ctrl+S` usan `FileBrowserDialog` (`ui/file_browser.py`), no `InputDialog` — deja navegar carpetas con flechas/Enter en vez de escribir una ruta a ciegas. Un mismo widget sirve para abrir (`mode="open"`, lista solo `.xlsx`) y guardar (`mode="save"`, añade un `Input` de nombre de archivo precargado con el actual, así "guardar" y "guardar como" son el mismo flujo). Si necesitas otro diálogo que involucre elegir una ruta del sistema de archivos, reutiliza este widget en vez de volver a `InputDialog` con una ruta escrita a mano.

**Cambiar el formato de guardado/lectura .xlsx**: todo vive en `io/xlsx_io.py`. `load_workbook` puebla el modelo a partir de un `openpyxl.Workbook` (usa `data_only=False` para preservar fórmulas, no valores calculados). `save_workbook` hace el camino inverso. Si tocas esto, verifica siempre con un test de round-trip (guardar y volver a cargar debe preservar fórmulas y multi-hoja) — hay un ejemplo en `tests/test_xlsx_io.py`, y `qa_samples/QA.xlsx` + `tests/test_qa_fixtures.py` para un caso real con multi-hoja, fórmulas cruzadas y fechas.

**Celdas de fecha al importar un .xlsx**: openpyxl devuelve un `datetime.date`/`datetime.datetime` de Python para cualquier celda con formato de fecha, con el código de formato original de Excel en `xl_cell.number_format` (ej. `'d/MM/yyyy'`, `'dd-mm-yy'`...) — nunca coincide con nuestro `FORMATS["date_dmy"].xlsx_code`, así que **no** intentes mapearlo vía `XLSX_CODE_TO_KEY`. `load_workbook` detecta la fecha directamente por el tipo del valor (`isinstance(xl_cell.value, (datetime.date, datetime.datetime))`) y siempre le asigna nuestra única clave `"date_dmy"`, independientemente de qué código de formato traía Excel. `_to_raw` convierte el valor a ISO `YYYY-MM-DD` (lo que espera `formatting._format_date_dmy`), no al `str()` por defecto de un objeto `datetime` (que da algo feo tipo `2026-10-10 00:00:00`).

**Cambiar undo/redo o portapapeles**: usa siempre el patrón Command (`model/undo.py`) para cualquier mutación de celdas desde la UI — nunca llames a `sheet.set_raw()` ni mutes `cell.fmt` directamente desde `app.py`, pasa por `self.undo_stack.execute(SetCellCommand(...))`, `BulkSetCommand(...)` o `SetFormatCommand(...)` para que quede en la pila de deshacer. Para tocar una celda que puede estar vacía (formato sin contenido), usa `sheet.ensure_cell(row, col)`, no `sheet.get_cell(...)` — este último devuelve un `Cell()` desechable si la celda no existía en el dict disperso, y cualquier mutación sobre él se perdería.

**Añadir un formato de celda nuevo** (moneda, fecha u otro): añade una entrada a `FORMATS` en `model/formatting.py` con su `xlsx_code` (para que se guarde bien en el `.xlsx`) y su función de render en `_CURRENCY_RENDER` (o una rama nueva en `format_display` si no es moneda/fecha), y su key a `FORMAT_ORDER`. El diálogo (`Ctrl+1`, `ChoiceDialog` en `app.py::action_format_cell`) y el round-trip xlsx (`io/xlsx_io.py`, vía `XLSX_CODE_TO_KEY`) ya recorren `FORMATS`/`FORMAT_ORDER` automáticamente.

## La grilla y los índices de fila/columna

`SheetGrid` (`grid.py`) usa las **row labels nativas** de `DataTable` (`label=` en `add_row`, `show_row_labels=True`) para los números de fila, y las cabeceras nativas de columna (`add_column(letra, ...)`) para las letras A, B, C... **Nunca vuelvas a añadir una columna de datos falsa para el índice de fila** (hubo una regresión así: una columna `"rownum"` era navegable como si fuera una celda normal, y editarla crasheaba con `CellDoesNotExist` porque no existía en el modelo). Las row labels y las cabeceras de columna no son celdas navegables — el cursor solo puede moverse dentro del rango real de datos (columnas 1..n_cols, filas 1..n_rows), lo cual está cubierto por `tests/test_grid_ui.py`.

## Recalculo de fórmulas

El motor (`model/formula_engine.py::Engine`) no mantiene un grafo de dependencias persistente: `Engine.recalculate()` reevalúa todas las celdas fórmula del workbook de forma perezosa y memoizada, con detección de ciclos vía un set `_visiting`. Esto significa que **después de cualquier cambio de celda hay que llamar a `self.engine.recalculate()` y luego `grid.refresh_from_sheet(sheet)`** — mira cualquier `action_*` en `app.py` que edite celdas como plantilla (siguen todas el mismo patrón: `undo_stack.execute(...)` → `engine.recalculate()` → `grid.refresh_from_sheet(sheet)` → `refresh_status()`).

**Referencias entre hojas** (`Hoja1!A1`, `SUMA(Datos!A1:B10)`, `'Hoja Con Espacios'!A1`): tokens `SHEET_CELL`/`SHEET_RANGE` en el tokenizer (deben ir *antes* que `CELL`/`RANGE`/`ID` en `TOKEN_SPEC` — el matcher de regex prueba alternativas en orden y se queda con la primera que caza, no con la más larga). `CellNode`/`RangeNode` llevan un campo `sheet: str | None`; `Engine._resolve_cell`/`_resolve_range` resuelven ese nombre contra `workbook.sheet_by_name(...)` (`#REF!` si no existe) en vez de usar la hoja activa. Si algún día se soporta también `Hoja1:Hoja3!A1` (rango de hojas) o referencias absolutas `$A$1`, el sitio para tocar es este mismo bloque de tokenizer+parser+`_resolve_*`.

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

**Trampa con `push_screen(dialog, callback)`**: el callback que se pasa a `push_screen` (usado por `InputDialog`, `HelpDialog`, `ChoiceDialog`) no se ejecuta en el mismo ciclo que el `dismiss()` — hace falta un `await pilot.pause()` *extra* después del que procesa la tecla que cierra el diálogo (`enter`/`escape`) para que el callback (y por tanto el cambio de estado que aplica, ej. `SetFormatCommand`) ya se haya ejecutado. Si un test que interactúa con un diálogo modal falla con el estado "de antes" de aplicar el cambio, prueba a añadir un `pilot.pause()` más antes de leer el resultado — no asumas que es un bug real sin descartar esto primero.

**`ListView` empieza con `index = None`**: si construyes un `ListView` vacío y le añades `ListItem`s dinámicamente (como hace `FileBrowserDialog` al listar una carpeta), el cursor no resalta ningún elemento hasta la primera pulsación de flecha — `list_view.index` es `None`, no `0`. La primera flecha mueve a index `0` (el primer elemento), no al segundo. Si necesitas que el primer elemento esté seleccionado desde que se abre el diálogo (para que Enter sin tocar flechas ya haga algo razonable), pon `list_view.index = 0` explícitamente después de poblarlo.

**Varios `dock: bottom` (o `dock: top`) hermanos NO se apilan solos**: si dos o más widgets hijos directos de `Screen` tienen `dock: bottom`, Textual los pinta a *todos* pegados literalmente al mismo borde inferior, superpuestos unos sobre otros — no reservan espacio entre ellos automáticamente. Esto pasó de verdad: `#sheet_tabs`, `StatusBar` y `Footer` estaban los tres como hermanos con `dock: bottom`, y `Footer` tapaba completamente el nombre de la hoja activa (invisible para el usuario, sin ningún error). La solución es meterlos todos dentro de un único contenedor (`Vertical`) que sea el que tiene `dock: bottom`, y dejar que sus hijos fluyan en layout normal dentro de él — para `Footer` en concreto hace falta además `Footer { dock: none; }` en el CSS, porque su `DEFAULT_CSS` propio ya trae `dock: bottom` y si no se anula compite igualmente por el borde. Verifica cualquier disposición de chrome (barras, cabeceras) con `tests/test_layout.py` como plantilla: comprueba `widget.region` de cada pieza y confirma que no comparten fila.

**Empaquetado con `--onedir`, no `--onefile`**: los tres scripts de build usan `--onedir` a propósito. `--onefile` se auto-extrae a un directorio temporal en cada arranque, lo que en macOS además dispara un rescaneo de Gatekeeper — el usuario reportó arranques de varios segundos con `--onefile` que desaparecieron al cambiar a `--onedir`. Si tocas los scripts de build, no vuelvas a `--onefile` sin que el usuario lo pida explícitamente.

## Al terminar un cambio

1. Corre `pytest tests/ -q` — deben seguir pasando los tests existentes y cualquiera nuevo que añadas para la función/comportamiento tocado.
2. Si tocaste teclado o UI, verifica con el patrón headless de arriba el flujo concreto que cambiaste.
3. Si el cambio afecta al empaquetado (nuevas dependencias en `pyproject.toml`), recuerda que los tres scripts (`build_windows.ps1`, `build_macos.sh`, `build_linux.sh`) instalan desde `pyproject.toml` y apuntan a `run_termsheet.py` (no a `termsheet/app.py` directamente — PyInstaller rompe los imports relativos si apunta al módulo dentro del paquete). No hace falta tocarlos salvo que cambie el punto de entrada.
