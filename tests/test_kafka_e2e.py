"""E2E Kafka opsional: producer jalan dulu (consumer belum ada), consumer menyusul.

Butuh broker lokal:
  docker compose -f docker-compose.kafka.yml up -d
  $env:QRIS_KAFKA="1"; python -m pytest -q     (Windows)
  QRIS_KAFKA=1 python -m pytest -q             (Linux/macOS)

Topik unik per run supaya sisa data dari run sebelumnya tidak mengacaukan hitungan.
"""
import csv
import os
import re
import uuid

import pytest

from _util import DIRTY_AMOUNT, DIRTY_DUP, DIRTY_TS, run_script

pytestmark = pytest.mark.skipif(
    os.environ.get("QRIS_KAFKA") != "1",
    reason="butuh Kafka lokal; set QRIS_KAFKA=1 setelah docker compose kafka jalan",
)


def test_consumer_catches_up_without_losing_events(workspace):
    topic = f"qris-e2e-{uuid.uuid4().hex[:8]}"
    env = {"QRIS_TOPIC": topic, "QRIS_CONSUMER_TIMEOUT_MS": "5000"}

    produced = run_script("produce.py", workspace, env=env)
    assert "DONE sent=100000" in produced.stdout

    consumed = run_script("consume.py", workspace, env=env)
    m = re.search(r"DONE clean=(\d+) dups=(\d+) bad_amount=(\d+) bad_ts=(\d+)", consumed.stdout)
    assert m is not None, f"ringkasan consumer tidak ditemukan:\n{consumed.stdout}"
    clean, dups, bad_amount, bad_ts = map(int, m.groups())
    # setiap event terhitung: masuk atau ditolak, tidak ada yang hilang diam-diam
    assert clean + dups + bad_amount + bad_ts == 100_000
    assert dups >= DIRTY_DUP and bad_amount >= DIRTY_AMOUNT and bad_ts >= DIRTY_TS, \
        "consumer harus menolak baris kotor yang sama seperti silver"

    rows = list(csv.DictReader((workspace / "data" / "qris_clean_live.csv").open(newline="")))
    assert len(rows) == clean
    assert len({r["txn_id"] for r in rows}) == len(rows)
