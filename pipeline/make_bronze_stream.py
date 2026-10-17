"""Pecah bronze CSV jadi beberapa part kecil di data/bronze_stream/ supaya
spark_streaming_job.py punya sumber stream yang nyata (file source, maxFilesPerTrigger=1).

Contoh: jalankan job dulu, lalu seeder ini supaya terasa mengalir:
  terminal 1: spark-submit spark/spark_streaming_job.py
  terminal 2: python pipeline/make_bronze_stream.py
"""
import csv
import shutil
from pathlib import Path

SRC = Path("data/bronze/qris_raw.csv")
OUT = Path("data/bronze_stream")
PARTS = 10


def main():
    with SRC.open(newline="") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]

    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    size = (len(data) + PARTS - 1) // PARTS
    written = 0
    for i in range(PARTS):
        chunk = data[i * size:(i + 1) * size]
        if not chunk:
            continue
        with (OUT / f"part_{i:02d}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(chunk)
        written += 1
    print(f"wrote {written} part files to {OUT} ({len(data)} rows)")


if __name__ == "__main__":
    main()
