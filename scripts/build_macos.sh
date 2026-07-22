#!/usr/bin/env bash
# Empaqueta TermSheet como ejecutable standalone para macOS usando PyInstaller.
# Requiere Python 3.10+ instalado (via Homebrew o python.org). Ejecutar desde
# la raíz del repo:
#   chmod +x scripts/build_macos.sh && ./scripts/build_macos.sh
#
# En macOS es habitual que `python3` del PATH sea el de Xcode Command Line
# Tools (a menudo 3.9, demasiado antiguo) aunque tengas uno más nuevo
# instalado por Homebrew. Indica cuál usar con la variable PYTHON en vez de
# tocar el script:
#   PYTHON=/opt/homebrew/bin/python3.10 ./scripts/build_macos.sh
# (en Mac Intel suele ser /usr/local/bin/python3.xx en vez de /opt/homebrew/...)

set -euo pipefail

PYTHON="${PYTHON:-python3}"

echo "Usando intérprete: $PYTHON ($("$PYTHON" --version 2>&1))"
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "ERROR: $PYTHON es más antiguo que 3.10 (requerido por termsheet)." >&2
    echo "Indica un intérprete más nuevo con la variable PYTHON, ej.:" >&2
    echo "  PYTHON=/opt/homebrew/bin/python3.10 ./scripts/build_macos.sh" >&2
    exit 1
fi

echo "Creando entorno virtual..."
"$PYTHON" -m venv .venv-build

echo "Instalando dependencias..."
.venv-build/bin/pip install --upgrade pip
.venv-build/bin/pip install -e ".[dev]"

echo "Construyendo termsheet con PyInstaller..."
.venv-build/bin/pyinstaller \
    --onedir \
    --name termsheet \
    --console \
    run_termsheet.py

echo "Listo. Ejecutable en dist/termsheet/termsheet"
echo "Se genera una carpeta (no un binario suelto) para que arranque al instante: --onedir evita"
echo "la auto-extracción de --onefile en cada ejecución (en macOS esto además evita que Gatekeeper"
echo "re-escanee un binario temporal distinto cada vez, que es la causa más común de arranque lento)."
echo "Copia toda la carpeta dist/termsheet si la mueves a otro sitio; para tenerlo en el PATH:"
echo "  ln -s \"\$(pwd)/dist/termsheet/termsheet\" /usr/local/bin/termsheet"
