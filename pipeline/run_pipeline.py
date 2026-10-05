"""Orkestrasi 1 perintah: bronze -> silver -> gold -> forecast."""
import subprocess, sys

STEPS = [
    [sys.executable, "pipeline/gen_qris.py"],
    [sys.executable, "pipeline/clean_silver.py"],
    [sys.executable, "pipeline/build_gold.py"],
    [sys.executable, "pipeline/forecast.py"],
]

for cmd in STEPS:
    print(">>>", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {cmd}")
print("PIPELINE OK")
