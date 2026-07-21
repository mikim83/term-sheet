"""QA de rendimiento con archivos .xlsx grandes (100/500/1000 MB): genera un
archivo sintético de cada tamaño y comprueba que `load_workbook` lo abre sin
reventar, midiendo tiempo y memoria pico.

Marcadas `@pytest.mark.slow` a propósito: generar y abrir un .xlsx de 1 GB
tarda varios minutos y puede necesitar varios GB de RAM, así que quedan
excluidas del `pytest` normal (ver `addopts` en pyproject.toml). Para
ejecutarlas explícitamente:

    pytest tests/test_benchmark_large_files.py -m slow -v -s

Los resultados medidos en este repositorio están documentados en el README,
sección "Benchmark: archivos .xlsx grandes".
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from benchmark_large_xlsx import benchmark_open, generate_xlsx  # noqa: E402

pytestmark = pytest.mark.slow

BENCH_DIR = Path("/tmp/termsheet_bench_pytest")
# Sin límite explícito en el test (0 = sin RLIMIT_AS) porque aquí solo
# comprobamos que abre correctamente, no medimos con la protección de
# memoria del script de benchmark manual (que sí la aplica por defecto
# para proteger al resto de servicios del servidor al ejecutarse a mano).
MEM_CAP_MB = 0


@pytest.fixture(scope="module", autouse=True)
def _cleanup_bench_dir():
    BENCH_DIR.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(BENCH_DIR, ignore_errors=True)


@pytest.mark.parametrize("target_mb", [100, 500, 1000])
def test_open_large_xlsx_reports_time_and_memory(target_mb):
    path = BENCH_DIR / f"bench_{target_mb}mb.xlsx"
    generate_xlsx(path, target_mb)
    real_mb = path.stat().st_size / (1024 * 1024)

    result = benchmark_open(path, mem_cap_mb=MEM_CAP_MB, timeout_seconds=1800)
    path.unlink(missing_ok=True)

    print(f"\n[{target_mb} MB objetivo, {real_mb:.1f} MB real] {result}")

    assert result["success"], f"No se pudo abrir el archivo de ~{target_mb} MB: {result['error']}"
    assert result["elapsed_seconds"] is not None
    assert result["peak_rss_mb"] is not None
