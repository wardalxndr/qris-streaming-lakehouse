"""Scoring: nilai tiap transaksi pakai model champion + cap versi model per baris.
Input default data/qris_clean.csv. Output default data/scored.csv.
Kategori tak dikenal dianggap nol (wajar untuk data baru, tercatat di reconcile
lewat F1 yang turun). Model diambil dari registry, jatuh ke model seed.
"""
import csv
import json
import math
import pickle
import sys

inp = sys.argv[1] if len(sys.argv) > 1 else "data/qris_clean.csv"
outp = sys.argv[2] if len(sys.argv) > 2 else "data/scored.csv"


def load_champion():
    try:
        reg = json.load(open("reports/model_registry.json"))
        ch = reg["champion"]
        return ch["model_file"], float(ch.get("threshold", 0.05)), ch.get("version", "unknown")
    except (FileNotFoundError, KeyError, ValueError):
        met = json.load(open("reports/model_metrics.json"))
        return "data/fraud_model.pkl", float(met.get("threshold", 0.05)), "seed"


model_file, thr, version = load_champion()
pack = pickle.load(open(model_file, "rb"))
model, CATS, CITIES = pack["model"], pack["cats"], pack["cities"]
thr = float(pack.get("threshold", thr))


def feats(r):
    day = int(r["ts"][8:10])
    f = [math.log1p(int(r["amount"])), int(r["ts"][11:13]) / 24.0,
         1.0 if (day >= 25 or day <= 1) else 0.0]
    f += [1.0 if r["merchant_cat"] == c else 0.0 for c in CATS]
    f += [1.0 if r["city"] == c else 0.0 for c in CITIES]
    return f


rows = list(csv.DictReader(open(inp)))
probs = model.predict_proba([feats(r) for r in rows])[:, 1]
with open(outp, "w", newline="") as fout:
    w = csv.DictWriter(fout, fieldnames=["txn_id", "ts", "proba", "pred", "model_version", "threshold"])
    w.writeheader()
    for r, p in zip(rows, probs):
        w.writerow({"txn_id": r["txn_id"], "ts": r["ts"], "proba": round(float(p), 4),
                    "pred": 1 if p >= thr else 0, "model_version": version, "threshold": thr})
print(f"SCORED n={len(rows)} model={version} thr={thr} -> {outp}")
