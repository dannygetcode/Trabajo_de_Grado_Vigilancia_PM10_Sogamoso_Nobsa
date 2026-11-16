"""La regla de ruff que prohíbe leer la hora del sistema (HU-01, ADR-0002) de verdad la detecta."""

import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.unitaria


def _ruff(codigo: str, carpeta: Path) -> subprocess.CompletedProcess[str]:
    archivo = carpeta / "domain" / "ejemplo.py"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(codigo, encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--no-cache",
            "--config",
            str(RAIZ / "pyproject.toml"),
            "--select",
            "TID251",
            "--output-format",
            "concise",
            str(archivo),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "codigo",
    [
        "from datetime import datetime\nx = datetime.now()\n",
        "import datetime\nx = datetime.datetime.now()\n",
        "from datetime import datetime\nx = datetime.utcnow()\n",
        "from datetime import date\nx = date.today()\n",
        "import time\nx = time.time()\n",
    ],
    ids=["datetime.now", "datetime.datetime.now", "utcnow", "date.today", "time.time"],
)
def test_detecta_hora_del_sistema(codigo: str, tmp_path: Path) -> None:
    r = _ruff(codigo, tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "TID251" in r.stdout


@pytest.mark.parametrize(
    "codigo",
    [
        "import time\nx = time.monotonic()\n",
        "import time\nx = time.perf_counter()\n",
        "from datetime import datetime, UTC\nx = datetime(2022, 1, 1, tzinfo=UTC)\n",
    ],
    ids=["monotonic", "perf_counter", "fecha_construida"],
)
def test_permite_duraciones_y_fechas_construidas(codigo: str, tmp_path: Path) -> None:
    r = _ruff(codigo, tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
