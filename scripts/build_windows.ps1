# Empaqueta TermSheet como un .exe standalone para Windows usando PyInstaller.
# Requiere Python 3.11+ instalado en Windows. Ejecutar desde la raíz del repo:
#   powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1

$ErrorActionPreference = "Stop"

Write-Host "Creando entorno virtual..."
python -m venv .venv-build

Write-Host "Instalando dependencias..."
.\.venv-build\Scripts\pip install --upgrade pip
.\.venv-build\Scripts\pip install -e ".[dev]"

Write-Host "Construyendo termsheet.exe con PyInstaller..."
.\.venv-build\Scripts\pyinstaller `
    --onedir `
    --name termsheet `
    --console `
    run_termsheet.py

Write-Host "Listo. Ejecutable en dist\termsheet\termsheet.exe"
Write-Host "Se genera una carpeta (no un .exe suelto) para que arranque al instante: --onedir evita la auto-extraccion de --onefile en cada ejecucion. Copia toda la carpeta dist\termsheet si la mueves a otro sitio."
