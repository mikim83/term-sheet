# Empaqueta TermSheet como un .exe standalone para Windows usando PyInstaller.
# Requiere Python 3.10+ instalado en Windows. Ejecutar desde la raíz del repo:
#   powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
#
# Si `python` del PATH no es la versión que quieres usar (p.ej. tienes varias
# instaladas), pasa la ruta con -Python en vez de tocar el script:
#   powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1 -Python "C:\Python310\python.exe"

param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$pyVersion = & $Python --version 2>&1
Write-Host "Usando intérprete: $Python ($pyVersion)"
& $Python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: $Python es más antiguo que 3.10 (requerido por termsheet)." -ForegroundColor Red
    Write-Host "Indica un intérprete más nuevo con -Python, ej.:" -ForegroundColor Red
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1 -Python `"C:\Python310\python.exe`"" -ForegroundColor Red
    exit 1
}

Write-Host "Creando entorno virtual..."
& $Python -m venv .venv-build

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
