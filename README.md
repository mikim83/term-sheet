# TermSheet

Hoja de cálculo de terminal, manejable 100% con teclado, compatible con archivos `.xlsx` reales (incluidos los exportados desde Google Sheets).

## Descargar un ejecutable ya compilado

En la sección [Releases](https://github.com/mikim83/term-sheet/releases) hay binarios standalone listos para Linux, macOS y Windows (no requieren tener Python instalado) — descarga el `.zip` de tu plataforma, descomprímelo y ejecuta `termsheet` (`termsheet.exe` en Windows). Se generan automáticamente vía GitHub Actions cada vez que se publica un tag `vX.Y.Z`.

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
| `Ctrl+2` | Estilo de celda: color de fuente, color de fondo y grosor/color de línea |
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

## Estilo de celda: colores y líneas

`Ctrl+2` abre un formulario (aplica a la celda actual o al rango seleccionado) con 4 campos:

- **Color de fuente** (hex, ej. `FF0000`) — se ve directamente en la terminal.
- **Color de fondo** (hex) — también se ve directamente en la terminal.
- **Grosor/estilo de línea**: `thin`, `medium`, `thick`, `dashed`, `dotted`, `double`, `hair`, o vacío/`none` para quitarlo.
- **Color de línea** (hex, gris `808080` por defecto).

Por defecto, toda celda nueva lleva una línea gris discontinua fina (`dashed` + `808080`), igual que la rejilla clásica de Excel, para que un `.xlsx` guardado desde TermSheet se abra con esa cuadrícula en Excel/Google Sheets. **Importante:** la terminal no puede dibujar líneas de distinto grosor de forma fiable, así que el grosor/estilo de línea se guarda y respeta al leer/escribir `.xlsx` (abrir un Excel con bordes gruesos y volver a guardarlo no los pierde) pero no se distingue visualmente dentro de TermSheet — solo al abrir el archivo en un programa que sí sepa dibujarlo. El color de fuente y de fondo, en cambio, sí se ven en la propia terminal.

Al abrir un `.xlsx` ya existente (de Excel, Google Sheets, etc.), TermSheet lee su color de fuente, color de relleno y grosor de línea reales y los conserva.

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

## Benchmark: archivos .xlsx grandes

`scripts/benchmark_large_xlsx.py` genera archivos `.xlsx` sintéticos (mezcla de texto, números, fechas y fórmulas en 20 columnas, similar a una hoja real) de un tamaño objetivo y mide cuánto tarda `load_workbook` en abrirlos y cuánta memoria RSS pico usa. La apertura corre en un subproceso aparte con un límite de memoria (`RLIMIT_AS`), para que un archivo que se dispare de memoria falle limpio con un `MemoryError` en su propio proceso en vez de arriesgar al resto de servicios de la máquina donde se ejecute:

```bash
python scripts/benchmark_large_xlsx.py --sizes 100 500 1000
```

También hay un test de QA equivalente (`tests/test_benchmark_large_files.py`), marcado `@pytest.mark.slow` a propósito — **no se ejecuta con el `pytest` normal** (excluido vía `addopts` en `pyproject.toml`, porque generar y abrir un `.xlsx` de 1 GB tarda decenas de minutos). Para correrlo explícitamente: `pytest tests/test_benchmark_large_files.py -m slow -v -s`.

### Resultados medidos (2026-07-21)

Máquina: servidor Linux compartido con **7.5 GB de RAM total** (con otros servicios corriendo a la vez — gifandria, tetrinet, cron jobs — así que la RAM realmente libre en el momento de cada prueba rondaba los 3.8-4.7 GB, no los 7.5 GB completos).

| Tamaño real del archivo | Tiempo de generación | Límite de memoria aplicado (dinámico, 70% de la RAM libre en ese momento) | Resultado al abrir | Memoria pico alcanzada |
|---|---|---|---|---|
| 100.3 MB | 289 s (~4.8 min) | 2650 MB | **Falló — `MemoryError`** | 2616.5 MB (justo en el límite) |
| 504.3 MB | 1408 s (~23.5 min) | 2963 MB | **Falló — `MemoryError`** | 2924.3 MB (justo en el límite) |
| 1010.9 MB | 2830 s (~47 min) | 3315 MB | **Falló — `MemoryError`** | 3270.9 MB (justo en el límite) |

**Conclusión — limitación real, no un fallo del test:** en los tres casos la apertura se quedó sin memoria justo al tope del límite dinámico aplicado, lo que indica que `load_workbook` (que usa `openpyxl` en modo normal, no `read_only`) necesita bastante más memoria que eso para terminar de construir el libro en memoria — el patrón sugiere que **ni siquiera el archivo de 100 MB llegó a abrirse del todo** con la RAM disponible en esta máquina en ese momento. `openpyxl` en modo no-`read_only` reconstruye cada celda como un objeto Python completo (con estilo, fórmula, tipo, etc.), lo que multiplica varias veces el tamaño en disco del `.xlsx` al cargarlo en memoria — con archivos de este tamaño el multiplicador observado fue de más de 25x sobre el tamaño del archivo.

Esto es una limitación real del enfoque actual de `xlsx_io.py` (carga todo el libro de golpe, sin *streaming*) frente a archivos muy grandes, no necesariamente del hardware del usuario final — en una máquina con más RAM libre estos mismos archivos probablemente sí abrirían, pero claramente el consumo de memoria escala muy mal. Si en el futuro hace falta soportar archivos de este tamaño con garantías, la vía a explorar es `openpyxl.load_workbook(path, read_only=True)` (modo *streaming*, mucho más ligero en memoria) en vez de una carga completa en memoria del libro entero.

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

### Publicar un release con los 3 binarios automáticamente

`.github/workflows/release.yml` corre estos mismos scripts en runners nativos de Linux, macOS y Windows (PyInstaller no permite compilar para otra plataforma distinta a la que lo ejecuta) cada vez que se empuja un tag `v*`:

```bash
git tag v0.2.0
git push origin v0.2.0
```

Al terminar, publica un Release de GitHub con `termsheet-linux.zip`, `termsheet-macos.zip` y `termsheet-windows.zip` adjuntos.
