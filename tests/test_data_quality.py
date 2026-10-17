"""Kontrak data: generator deterministik, silver bersih, mart konsisten, forecast wajar."""
import json
from datetime import datetime, timedelta

from _util import BRONZE_COLS, read_rows, run_script


def test_generator_is_seeded_and_valid(tmp_path):
    runs = []
    for name in ["a", "b"]:
        ws = tmp_path / name
        (ws / "data" / "bronze").mkdir(parents=True)
        run_script("gen_qris.py", ws)
        runs.append(ws / "data" / "bronze" / "qris_raw.csv")

    assert runs[0].read_bytes() == runs[1].read_bytes(), \
        "seed=42 harus menghasilkan byte yang sama di run berbeda"

    rows = read_rows(runs[0])
    assert len(rows) == 100_000
    assert list(rows[0].keys()) == BRONZE_COLS

    fraud_rate = sum(int(r["is_fraud"]) for r in rows) / len(rows)
    assert 0.015 <= fraud_rate <= 0.025, f"fraud rate {fraud_rate:.3%} jauh dari target 2%"

    for r in rows:
        assert int(r["amount"]) > 0
        datetime.strptime(r["ts"], "%Y-%m-%d %H:%M")


def test_silver_cleans_without_losing_valid_rows(workspace):
    bronze = read_rows(workspace / "data" / "bronze" / "qris_raw.csv")
    silver = read_rows(workspace / "data" / "qris_clean.csv")

    assert len(silver) == len(bronze), "baris valid tidak boleh hilang di silver"
    ids = [r["txn_id"] for r in silver]
    assert len(ids) == len(set(ids)), "txn_id harus unik setelah dedup"
    for r in silver:
        assert int(r["amount"]) > 0
        assert r["is_fraud"] in {"0", "1"}
        datetime.strptime(r["ts"], "%Y-%m-%d %H:%M")


def test_gold_marts_are_consistent(workspace):
    silver = read_rows(workspace / "data" / "qris_clean.csv")
    volume = read_rows(workspace / "data" / "mart_merchant_volume.csv")
    fraud = read_rows(workspace / "data" / "mart_fraud_flags.csv")
    risk = read_rows(workspace / "data" / "mart_user_risk.csv")

    assert sum(int(r["txn_count"]) for r in volume) == len(silver)
    assert sum(int(r["total_amount"]) for r in volume) == sum(int(r["amount"]) for r in silver)

    fraud_users = {r["user_id"] for r in silver if r["is_fraud"] == "1"}
    assert sum(int(r["count"]) for r in fraud) == len(
        [r for r in silver if r["is_fraud"] == "1"])

    users = [r["user_id"] for r in risk]
    assert len(users) == len(set(users))
    assert set(users) == fraud_users, "risk mart harus berisi tepat user yang punya fraud"
    for r in risk:
        assert 0 <= int(r["risk_score"]) <= 10
        assert r["risk_band"] in {"low", "medium", "high"}


def test_forecast_covers_next_seven_days(workspace):
    silver = read_rows(workspace / "data" / "qris_clean.csv")
    forecast = read_rows(workspace / "data" / "forecast_next7.csv")

    last = datetime.strptime(max(r["ts"][:10] for r in silver), "%Y-%m-%d").date()
    expected = [(last + timedelta(days=i)).isoformat() for i in range(1, 8)]
    assert [r["day"] for r in forecast] == expected
    assert all(float(r["fraud_forecast"]) >= 0 for r in forecast)

    metrics = json.loads((workspace / "reports" / "forecast_metrics.json").read_text())
    assert metrics["mae_backtest_7d"] >= 0
    assert metrics["last_7d_avg"] > 0
