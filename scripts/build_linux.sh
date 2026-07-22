#!/usr/bin/env bash
# Empaqueta TermSheet como ejecutable standalone para Linux usando PyInstaller.
# Requiere Python 3.10+ instalado. Ejecutar desde la raíz del repo:
#   chmod +x scripts/build_linux.sh && ./scripts/build_linux.sh
#
# Si tu `python3` del PATH es más antiguo que 3.10 (p.ej. hay otra versión
# instalada aparte, vía pyenv/Homebrew/etc.), indica cuál usar con la
# variable PYTHON en vez de tocar el script:
#   PYTHON=/ruta/a/python3.11 ./scripts/build_linux.sh

set -euo pipefail

PYTHON="${PYTHON:-python3}"

echo "Usando intérprete: $PYTHON ($("$PYTHON" --version 2>&1))"
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "ERROR: $PYTHON es más antiguo que 3.10 (requerido por termsheet)." >&2
    echo "Indica un intérprete más nuevo con la variable PYTHON, ej.:" >&2
    echo "  PYTHON=/usr/bin/python3.11 ./scripts/build_linux.sh" >&2
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
echo "la auto-extracción de --onefile en cada ejecución. Copia toda la carpeta dist/termsheet si"
echo "la mueves a otro sitio; para tenerlo en el PATH:"
echo "  ln -s \"\$(pwd)/dist/termsheet/termsheet\" /usr/local/bin/termsheet"
