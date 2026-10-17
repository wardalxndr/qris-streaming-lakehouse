"""Helper bersama untuk test: jalankan script pipeline di direktori kerja sementara."""
from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "pipeline"

BRONZE_COLS = ["txn_id", "ts", "user_id", "merchant_id", "merchant_cat", "amount",
               "city", "device_id", "channel", "is_fraud", "fraud_type"]


def run_script(script: str, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, str(PIPELINE / script)],
        cwd=str(cwd), capture_output=True, text=True,
        env={**os.environ, **(env or {})},
    )
    assert result.returncode == 0, (
        f"{script} gagal (exit {result.returncode})\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return result


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))
