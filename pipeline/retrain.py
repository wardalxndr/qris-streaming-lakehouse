"""Retrain: latih challenger di jendela terbaru, uji di minggu holdout,
promosikan hanya jika F1 >= champion + MIN_GAIN. Model lama tak pernah dihapus.
Registry reports/model_registry.json adalah sumber kebenaran versi champion.
Laporan: reports/retrain_report.json. Exit 2 jika data kurang (jujur berhenti).
"""
import csv
import json
import math
import pickle
import sys
from datetime import datetime

MIN_GAIN = 0.005
THRESHOLDS = [0.02, 0.05, 0.1, 0.2, 0.3, 0.5]


def day_of(ts):
    return int(ts[8:10])


rows = list(csv.DictReader(open("data/qris_clean.csv")))
for r in rows:
    r["amount"] = int(r["amount"])
    r["y"] = 1 if str(r["is_fraud"]) == "1" else 0

max_day = max(day_of(r["ts"]) for r in rows)
train = [r for r in rows if max_day - 27 <= day_of(r["ts"]) <= max_day - 7]
hold = [r for r in rows if day_of(r["ts"]) > max_day - 7]
if len(train) < 1000 or len(hold) < 200:
    print(f"NOT ENOUGH DATA train={len(train)} holdout={len(hold)}, need 1000/200")
    raise SystemExit(2)

CATS = sorted({r["merchant_cat"] for r in train})
CITIES = sorted({r["city"] for r in train})


def feats(r):
    day = day_of(r["ts"])
    f = [math.log1p(r["amount"]), int(r["ts"][11:13]) / 24.0,
         1.0 if (day >= 25 or day <= 1) else 0.0]
    f += [1.0 if r["merchant_cat"] == c else 0.0 for c in CATS]
    f += [1.0 if r["city"] == c else 0.0 for c in CITIES]
    return f


from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=500).fit([feats(r) for r in train], [r["y"] for r in train])
probs = model.predict_proba([feats(r) for r in hold])[:, 1]
y = [r["y"] for r in hold]


def scores(thr):
    tp = sum(1 for p, t in zip(probs, y) if p >= thr and t == 1)
    fp = sum(1 for p, t in zip(probs, y) if p >= thr and t == 0)
    fn = sum(1 for p, t in zip(probs, y) if p < thr and t == 1)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    return 2 * prec * rec / max(prec + rec, 1e-9), prec, rec


best = max(((scores(t)[0], t) + scores(t)[1:] for t in THRESHOLDS), key=lambda x: x[0])
f1, thr, prec, rec = best


def load_champion():
    try:
        reg = json.load(open("reports/model_registry.json"))
        ch = reg["champion"]
        return reg, ch["version"], float(ch["f1"]), float(ch.get("threshold", 0.05))
    except (FileNotFoundError, KeyError, ValueError):
        met = json.load(open("reports/model_metrics.json"))
        return {"champion": None, "history": []}, "seed", float(met.get("f1", 0)), float(met.get("threshold", 0.05))


reg, ch_version, ch_f1, ch_thr = load_champion()
asof = max(r["ts"] for r in rows)
promoted = f1 >= ch_f1 + MIN_GAIN
report = {"asof": asof, "train_rows": len(train), "holdout_rows": len(hold),
          "challenger_f1": round(f1, 3), "challenger_threshold": thr,
          "champion_version": ch_version, "champion_f1": round(ch_f1, 3),
          "min_gain": MIN_GAIN, "promoted": promoted, "model_file": None}

if promoted:
    stamp = datetime.strptime(asof, "%Y-%m-%d %H:%M").strftime("%Y%m%d")
    model_file = f"data/fraud_model_{stamp}.pkl"
    pickle.dump({"model": model, "cats": CATS, "cities": CITIES, "threshold": thr},
                open(model_file, "wb"))
    entry = {"version": ch_version, "model_file": reg["champion"]["model_file"] if reg["champion"] else "data/fraud_model.pkl",
             "f1": round(ch_f1, 3), "threshold": ch_thr}
    reg["history"].append(entry)
    reg["champion"] = {"version": f"retrain-{stamp}", "model_file": model_file,
                       "f1": round(f1, 3), "threshold": thr,
                       "trained_on": f"days {max_day - 27}-{max_day - 7}"}
    json.dump(reg, open("reports/model_registry.json", "w"), indent=2)
    report["model_file"] = model_file

json.dump(report, open("reports/retrain_report.json", "w"), indent=2)
print(report)
