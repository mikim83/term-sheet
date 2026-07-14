# TermSheet

Hoja de cálculo de terminal, manejable 100% con teclado, compatible con archivos `.xlsx` reales (incluidos los exportados desde Google Sheets).

## Requisitos

- Python 3.9+
- Windows, macOS o Linux (funciona en Windows Terminal / PowerShell / cmd)

## Instalación (desarrollo)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
```

## Ejecutar

```bash
python -m termsheet.app                 # libro nuevo en blanco
python -m termsheet.app ruta/libro.xlsx  # abrir un archivo existente
```

## Abrir y guardar archivos

`Ctrl+O` y `Ctrl+S` abren un navegador de carpetas dentro del propio programa (no hace falta cerrar TermSheet ni escribir rutas a ciegas): flechas + `Enter` para entrar en una carpeta o elegir un archivo, `Backspace` para subir un nivel, `Esc` para cancelar. Al guardar, el nombre actual viene precargado y es editable (`Tab` para saltar al campo de nombre) — cambia el nombre o navega a otra carpeta para hacer un "guardar como" sin sobrescribir el archivo original.

## Abrir hojas de Google Sheets

Google Sheets no se abre directamente por URL: en Google Sheets ve a **Archivo → Descargar → Microsoft Excel (.xlsx)** y abre ese archivo con TermSheet. Al guardar, se genera un `.xlsx` real que puedes volver a subir a Google Sheets (**Archivo → Importar**) o abrir en Excel.

## Atajos de teclado

| Tecla | Acción |
|---|---|
| Flechas | Mover cursor |
| `Enter` / `F2` | Editar celda |
| `Esc` | Cancelar edición |
| `Shift`+flechas | Extender selección de rango (puede no funcionar en algunos terminales, ver `F8`) |
| `F8` | Alternativa a `Shift`+flechas: activa "modo selección" (como en Excel) — con el modo activo, las flechas normales extienden la selección; pulsa `F8` otra vez para salir. Funciona en cualquier terminal |
| `Ctrl+C` / `Ctrl+X` / `Ctrl+V` | Copiar / Cortar / Pegar rango |
| `Delete` | Borrar contenido de la selección |
| `Ctrl+1` | Formato de celda: moneda o fecha, aplicado a la celda o rango seleccionado |
| `Ctrl+Z` / `Ctrl+Y` | Deshacer / Rehacer (incluye formato) |
| `Ctrl+S` | Guardar: navegador de carpetas con el nombre actual editable (sirve de "guardar como" si lo cambias) |
| `Ctrl+O` | Abrir: navegador de carpetas (solo `.xlsx`), sin cerrar el programa |
| `Ctrl+N` | Nueva hoja |
| `Ctrl+R` | Renombrar la hoja activa |
| `Alt+PageUp` / `Alt+PageDown` | Cambiar de hoja (la activa se resalta en la barra inferior) |
| `Ctrl+G` | Ir a celda (ej. `B12`) |
| `Ctrl+F` | Buscar |
| `Ctrl+T` | Cambiar tema de color |
| `F1` | Ayuda de atajos |
| `Ctrl+Q` | Salir del programa |

## Fórmulas soportadas

`SUMA/SUM`, `PROMEDIO/AVERAGE`, `CONTAR/COUNT`, `CONTARA/COUNTA`, `MAX`, `MIN`, `SI/IF`, `Y/AND`, `O/OR`, `BUSCARV/VLOOKUP`, `CONCATENAR/CONCAT`, `SI.ERROR/IFERROR`, `ABS`, `REDONDEAR/ROUND`, referencias entre celdas (`A1`), rangos (`A1:B10`), operadores aritméticos y de comparación, y **referencias a otras hojas** del mismo libro: `Hoja1!A1`, `SUMA(Datos!A1:B10)`, o con comillas si el nombre tiene espacios: `'Mi Hoja'!A1`.

Errores estilo Excel: `#DIV/0!`, `#REF!`, `#CIRC!` (referencia circular), `#NAME?`, `#VALUE!`, `#N/A`.

## Formato de celda

`Ctrl+1` abre el selector de formato (aplica a la celda actual o al rango seleccionado):

- **Moneda**: Euro estilo español (`1.234,56 €`), Euro con símbolo delante (`€1.234,56`), Dólar (`$1,234.56`), Libra (`£1,234.56`)
- **Fecha**: `DD/MM/AAAA`
- **General**: quita el formato

El formato se guarda en el `.xlsx` (compatible con Excel/Google Sheets) y es deshacible con `Ctrl+Z`.

## Temas de color

Cinco temas incluidos, seleccionables con `Ctrl+T` (se recuerda el último usado en `~/.termsheet/config.toml`):

1. Clásico (fondo negro / texto blanco)
2. Invertido (fondo blanco / texto negro)
3. Excel verde
4. Solarized Dark
5. Alto contraste (accesibilidad)

## Tests

```bash
pytest tests/
```

## Empaquetar como ejecutable standalone

Los tres scripts generan una **carpeta** (`dist/termsheet/`, no un único archivo) con `--onedir` de PyInstaller: arranca al instante porque no necesita auto-extraerse en un directorio temporal en cada ejecución (con `--onefile` el arranque tarda notablemente más, sobre todo en macOS por el rescaneo de Gatekeeper). Copia la carpeta entera si la mueves a otro sitio — el ejecutable dentro depende de los archivos que la acompañan.

**Windows**, con Python instalado:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

Genera `dist\termsheet\termsheet.exe`.

**macOS**, con Python instalado (Homebrew o python.org):

```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

Genera `dist/termsheet/termsheet`. Para tenerlo en el `PATH`: `ln -s "$(pwd)/dist/termsheet/termsheet" /usr/local/bin/termsheet`.

**Linux**, con Python instalado:

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

Genera `dist/termsheet/termsheet`. Para tenerlo en el `PATH`: `ln -s "$(pwd)/dist/termsheet/termsheet" /usr/local/bin/termsheet`.
