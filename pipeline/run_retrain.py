"""Loop hidup model: score -> reconcile -> retrain. Berhenti di langkah gagal.
Script dipanggil lewat path absolut (relatif ke repo), cwd diwariskan dari pemanggil
supaya data/ dan reports/ tetap mengikuti direktori kerja aktif."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    [sys.executable, str(ROOT / "pipeline/score.py")],
    [sys.executable, str(ROOT / "pipeline/reconcile.py")],
    [sys.executable, str(ROOT / "pipeline/retrain.py")],
]

for cmd in STEPS:
    print(">>>", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {cmd}")
print("RETRAIN LOOP OK")
