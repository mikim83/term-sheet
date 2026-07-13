#!/usr/bin/env bash
# Empaqueta TermSheet como ejecutable standalone para Linux usando PyInstaller.
# Requiere Python 3.11+ instalado. Ejecutar desde la raíz del repo:
#   chmod +x scripts/build_linux.sh && ./scripts/build_linux.sh

set -euo pipefail

echo "Creando entorno virtual..."
python3 -m venv .venv-build

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
