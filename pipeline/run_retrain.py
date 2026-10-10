"""Loop hidup model: score -> reconcile -> retrain. Berhenti di langkah gagal."""
import subprocess
import sys

STEPS = [
    [sys.executable, "pipeline/score.py"],
    [sys.executable, "pipeline/reconcile.py"],
    [sys.executable, "pipeline/retrain.py"],
]

for cmd in STEPS:
    print(">>>", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {cmd}")
print("RETRAIN LOOP OK")
