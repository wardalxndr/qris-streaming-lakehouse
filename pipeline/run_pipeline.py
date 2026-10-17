"""Orkestrasi 1 perintah: bronze -> silver -> gold -> forecast -> model.
Script dipanggil lewat path absolut (relatif ke repo), cwd diwariskan dari pemanggil
supaya data/ dan reports/ tetap mengikuti direktori kerja aktif."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    [sys.executable, str(ROOT / "pipeline/gen_qris.py")],
    [sys.executable, str(ROOT / "pipeline/clean_silver.py")],
    [sys.executable, str(ROOT / "pipeline/build_gold.py")],
    [sys.executable, str(ROOT / "pipeline/forecast.py")],
    [sys.executable, str(ROOT / "pipeline/model.py")],
]

for cmd in STEPS:
    print(">>>", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {cmd}")
print("PIPELINE OK")
