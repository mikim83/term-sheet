# TermSheet

Hoja de cálculo de terminal, manejable 100% con teclado, compatible con archivos `.xlsx` reales (incluidos los exportados desde Google Sheets).

## Requisitos

- Python 3.11+
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

## Abrir hojas de Google Sheets

Google Sheets no se abre directamente por URL: en Google Sheets ve a **Archivo → Descargar → Microsoft Excel (.xlsx)** y abre ese archivo con TermSheet. Al guardar, se genera un `.xlsx` real que puedes volver a subir a Google Sheets (**Archivo → Importar**) o abrir en Excel.

## Atajos de teclado

| Tecla | Acción |
|---|---|
| Flechas | Mover cursor |
| `Enter` / `F2` | Editar celda |
| `Esc` | Cancelar edición |
| `Shift`+flechas | Extender selección de rango |
| `Ctrl+C` / `Ctrl+X` / `Ctrl+V` | Copiar / Cortar / Pegar rango |
| `Delete` | Borrar contenido de la selección |
| `Ctrl+Z` / `Ctrl+Y` | Deshacer / Rehacer |
| `Ctrl+S` | Guardar como `.xlsx` |
| `Ctrl+O` | Abrir `.xlsx` |
| `Ctrl+N` | Nueva hoja |
| `Ctrl+PageUp` / `Ctrl+PageDown` | Cambiar de hoja |
| `Ctrl+G` | Ir a celda (ej. `B12`) |
| `Ctrl+F` | Buscar |
| `Ctrl+T` | Cambiar tema de color |
| `F1` | Ayuda de atajos |

## Fórmulas soportadas

`SUMA/SUM`, `PROMEDIO/AVERAGE`, `CONTAR/COUNT`, `CONTARA/COUNTA`, `MAX`, `MIN`, `SI/IF`, `Y/AND`, `O/OR`, `BUSCARV/VLOOKUP`, `CONCATENAR/CONCAT`, `SI.ERROR/IFERROR`, `ABS`, `REDONDEAR/ROUND`, referencias entre celdas (`A1`), rangos (`A1:B10`), operadores aritméticos y de comparación.

Errores estilo Excel: `#DIV/0!`, `#REF!`, `#CIRC!` (referencia circular), `#NAME?`, `#VALUE!`, `#N/A`.

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

## Empaquetar como .exe para Windows

Desde Windows, con Python instalado:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

Genera `dist\termsheet.exe`, ejecutable sin necesidad de tener Python instalado.
