#!/usr/bin/env bash
# Empaqueta TermSheet como ejecutable standalone para macOS usando PyInstaller.
# Requiere Python 3.11+ instalado (via Homebrew o python.org). Ejecutar desde
# la raíz del repo:
#   chmod +x scripts/build_macos.sh && ./scripts/build_macos.sh

set -euo pipefail

echo "Creando entorno virtual..."
python3 -m venv .venv-build

echo "Instalando dependencias..."
.venv-build/bin/pip install --upgrade pip
.venv-build/bin/pip install -e ".[dev]"

echo "Construyendo termsheet con PyInstaller..."
.venv-build/bin/pyinstaller \
    --onefile \
    --name termsheet \
    --console \
    termsheet/app.py

echo "Listo. Ejecutable en dist/termsheet"
echo "Puedes moverlo a /usr/local/bin/termsheet para tenerlo en el PATH."
