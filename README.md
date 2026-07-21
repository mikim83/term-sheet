# TermSheet

Hoja de cálculo de terminal, manejable 100% con teclado, compatible con archivos `.xlsx` reales (incluidos los exportados desde Google Sheets).

## Descargar un ejecutable ya compilado

En la sección [Releases](https://github.com/mikim83/term-sheet/releases) hay binarios standalone listos para Linux, macOS y Windows (no requieren tener Python instalado) — descarga el `.zip` de tu plataforma, descomprímelo y ejecuta `termsheet` (`termsheet.exe` en Windows). Se generan automáticamente vía GitHub Actions cada vez que se publica un tag `vX.Y.Z`.

## Requisitos

- Python 3.10+ (antes se admitía 3.9, pero pasó a requerirse 3.10 para poder usar `@dataclass(slots=True)` en `Cell`/`CellFormat` — ver sección Benchmark)
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

### Resultados medidos (2026-07-21, antes de optimizar)

Máquina: servidor Linux compartido con **7.5 GB de RAM total** (con otros servicios corriendo a la vez — gifandria, tetrinet, cron jobs — así que la RAM realmente libre en el momento de cada prueba rondaba los 3.8-4.7 GB, no los 7.5 GB completos).

| Tamaño real del archivo | Tiempo de generación | Límite de memoria aplicado (dinámico, 70% de la RAM libre en ese momento) | Resultado al abrir | Memoria pico alcanzada |
|---|---|---|---|---|
| 100.3 MB | 289 s (~4.8 min) | 2650 MB | **Falló — `MemoryError`** | 2616.5 MB (justo en el límite) |
| 504.3 MB | 1408 s (~23.5 min) | 2963 MB | **Falló — `MemoryError`** | 2924.3 MB (justo en el límite) |
| 1010.9 MB | 2830 s (~47 min) | 3315 MB | **Falló — `MemoryError`** | 3270.9 MB (justo en el límite) |

Los tres casos se quedaron sin memoria justo al tope del límite dinámico aplicado — indicio claro de que hacía falta bastante más para terminar de abrirlos, no un fallo puntual del test.

### Investigación de la causa raíz

Antes de dar el problema por "así es Python" o plantear un cambio de lenguaje, se investigó **por qué** pasaba esto, con datos:

1. **El propio archivo de 100 MB del benchmark resultó tener ~21.6 millones de celdas no vacías.** Un `.xlsx` es un zip de XML, y el contenido real sin comprimir de ese "100 MB" eran **1220 MB de XML** (ratio de compresión 12.2x) — nada anómalo del test: se repitió el experimento con un generador de datos mucho menos repetitivo (más parecido a una hoja de ventas real) y el mismo "100 MB" seguía siendo **775 MB de XML** y **~16 millones de celdas**. Los `.xlsx` densos en celdas comprimen así de bien casi siempre, por lo repetitivo de las etiquetas XML de Excel.
2. **Aislando la causa:** abrir ese mismo archivo (21.6M celdas) con `openpyxl.load_workbook(path, read_only=True)` (modo *streaming*) en vez del modo normal usó solo **117 MB** de pico, en 302 s — un archivo que en modo normal necesitaba **más de 3.3 GB** y aun así no llegaba a abrirse. El modo normal de `openpyxl` reconstruye un grafo de objetos Python completo con cada celda del archivo; el modo `read_only` procesa el XML como un flujo, sin retenerlo todo en memoria.
3. **Segunda causa, más pequeña pero real:** el propio modelo de datos de TermSheet (`Cell`/`CellFormat`) creaba un objeto Python "normal" (con `__dict__`) por cada celda no vacía cargada, sin `__slots__` — overhead extra que se suma por cada una de esos millones de celdas.

### Optimizaciones aplicadas

- **`xlsx_io.py` ahora usa `read_only=True`** (streaming) en vez del modo normal de `openpyxl`. Como ese modo no expone `column_dimensions` (los anchos de columna), se añadió `_read_column_widths_streaming()`: un parseo aparte, también en streaming, que se detiene en cuanto encuentra `<sheetData>` (el bloque que sí pesa) — el bloque `<cols>` con los anchos siempre va antes en el XML, así que este parseo extra cuesta un puñado de KB sin importar lo grande que sea la hoja. El acceso a valor, fuente, relleno, borde y formato numérico por celda funciona exactamente igual en modo `read_only`, así que nada de lo añadido para colores/bordes se vio afectado.
- **`Cell` y `CellFormat` pasan a `@dataclass(slots=True)`**, lo que reduce el overhead de memoria por objeto. Esto obligó a subir el requisito mínimo de Python de 3.9 a **3.10** (`slots=True` en dataclasses no existe antes), cosa que ya recomendaban los scripts de empaquetado.

### Resultado tras optimizar

Con un archivo real y de tamaño grande-pero-plausible (200.000 filas, 1.6 millones de celdas, ~10 MB en disco — muy por encima de lo que alguien navegaría celda a celda en una terminal, pero representativo de un export/informe grande de verdad):

| | Antes | Después | Mejora |
|---|---|---|---|
| Tiempo de apertura | 53.0 s | 42.1 s | ~20% más rápido |
| Memoria pico | 1311.6 MB | 614.4 MB | **2.1x menos memoria** |

El archivo "peor caso" original del benchmark (100 MB pero con ~21.6 millones de celdas) **sigue fallando** incluso con ambos fixes aplicados (probado: falla igual con un límite de 3540 MB) — pero ya no por culpa de `openpyxl`: el punto (2) de arriba demuestra que la lectura en sí cuesta solo 117 MB. Lo que sigue costando gigabytes en ese caso extremo es que **TermSheet mantiene un objeto vivo en memoria por cada una de esas 21.6 millones de celdas**, para que se puedan editar todas individualmente — y eso es inherente a cómo funciona la app (una hoja completamente editable en memoria), no algo que un modo de lectura más eficiente pueda arreglar del todo.

### ¿Hace falta cambiar de lenguaje?

**No, no está justificado con lo que se ha encontrado.** La causa real del problema no era una limitación de Python como lenguaje, sino una elección de API concreta (el modo de carga de `openpyxl`) fácilmente sustituible por otra API de la misma librería — y el resultado ya está medido: 2.1x menos memoria en un caso de archivo grande y realista, sin reescribir nada más que el módulo de carga.

El límite que queda (archivos con decenas de millones de celdas) es un límite de **"cuántas celdas puede mantener vivas y editables en memoria a la vez"**, y esa es una restricción de **cualquier** lenguaje para una hoja de cálculo completamente en memoria: una hoja de N celdas editables necesita memoria proporcional a N sea cual sea el lenguaje. Un lenguaje con objetos más compactos (Rust, Go, C++) reduciría el coste *por celda* — probablemente varias veces menos que el equivalente en Python — pero no elimina el problema de fondo, y reescribir toda la app en otro lenguaje sería un proyecto enorme para un beneficio marginal frente a lo que ya se ha arreglado. Si en el futuro hace falta soportar de verdad hojas con millones de filas, el camino más razonable dentro de Python sería no cargarlas enteras en memoria (un modelo "perezoso"/paginado que solo materialice como objetos `Cell` las filas visibles o recientemente tocadas), no cambiar de lenguaje.

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
