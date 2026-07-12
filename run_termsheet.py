"""Punto de entrada para PyInstaller.

PyInstaller ejecuta el script objetivo directamente (no como parte de un
paquete), lo que rompe los imports relativos usados dentro de `termsheet/`
(p. ej. `from . import config`). Este wrapper importa `termsheet.app` como
módulo normal, evitando ese problema.
"""

from termsheet.app import run

if __name__ == "__main__":
    run()
