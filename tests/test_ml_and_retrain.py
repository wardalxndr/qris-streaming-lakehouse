"""Loop ML: model jujur (split waktu), scoring + reconcile konsisten, gate retrain benar."""
import json
import pickle

from _util import read_rows


def test_model_metrics_are_bounded_and_time_split(workspace):
    silver = read_rows(workspace / "data" / "qris_clean.csv")
    metrics = json.loads((workspace / "reports" / "model_metrics.json").read_text())

    assert metrics["train_rows"] + metrics["test_rows"] == len(silver)
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1"] <= 1
    assert metrics["threshold"] in [0.02, 0.05, 0.1, 0.2, 0.3, 0.5]

    pack = pickle.loads((workspace / "data" / "fraud_model.pkl").read_bytes())
    for key in ["model", "cats", "cities", "threshold"]:
        assert key in pack


def test_scoring_and_reconcile_line_up(retrain_workspace):
    ws = retrain_workspace
    silver = read_rows(ws / "data" / "qris_clean.csv")
    scored = read_rows(ws / "data" / "scored.csv")

    assert len(scored) == len(silver)
    for r in scored:
        assert 0.0 <= float(r["proba"]) <= 1.0
        assert r["pred"] in {"0", "1"}
        assert r["model_version"] == "seed", "tanpa registry, fallback harus ke model seed"

    met = json.loads((ws / "reports" / "reconcile_metrics.json").read_text())
    assert met["labeled_rows"] + met["unlabeled_rows"] == len(scored)
    assert met["labeled_rows"] > 0
    assert met["unlabeled_rows"] > 0, "label delay 2 hari harus menyisakan baris belum berlabel"
    assert 0 <= met["precision"] <= 1
    assert 0 <= met["recall"] <= 1


def test_retrain_gate_only_promotes_with_min_gain(retrain_workspace):
    ws = retrain_workspace
    report = json.loads((ws / "reports" / "retrain_report.json").read_text())

    assert report["champion_version"] == "seed"
    assert report["min_gain"] > 0
    if report["promoted"]:
        assert report["model_file"] is not None
        assert (ws / report["model_file"]).exists()
        registry = json.loads((ws / "reports" / "model_registry.json").read_text())
        assert registry["champion"]["version"].startswith("retrain-")
    else:
        assert report["model_file"] is None
