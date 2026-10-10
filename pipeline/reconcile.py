"""Reconcile: bandingkan prediksi vs label yang (simulasi) sudah datang.
Label produksi datang telat; di sini label dianggap datang setelah
--label-delay-days hari dari ts event (default 2). Baris lebih baru dari
batas dianggap belum berlabel dan dilaporkan terpisah, bukan ditebak.
Output reports/reconcile_metrics.json. Selalu exit 0: ini monitoring,
keputusan promosi ada di retrain.py, bukan di sini.
"""
import csv
import json
import sys
from datetime import datetime, timedelta


def arg(name, default):
    for a in sys.argv[1:]:
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return default


scored_path = arg("--scored", "data/scored.csv")
silver_path = arg("--silver", "data/qris_clean.csv")
delay = int(arg("--label-delay-days", "2"))
seed_baseline = float(arg("--seed-fraud-rate", "0.02"))

scored = {r["txn_id"]: r for r in csv.DictReader(open(scored_path))}
silver = {r["txn_id"]: r for r in csv.DictReader(open(silver_path))}
asof = max(r["ts"] for r in silver.values())
cutoff = (datetime.strptime(asof, "%Y-%m-%d %H:%M") - timedelta(days=delay)).strftime("%Y-%m-%d %H:%M")

tp = fp = fn = tn = unlabeled = fraud_labeled = 0
for tid, s in scored.items():
    lab = silver.get(tid)
    if lab is None or lab["ts"] >= cutoff:
        unlabeled += 1
        continue
    y = 1 if lab["is_fraud"] == "1" else 0
    p = int(s["pred"])
    fraud_labeled += y
    if p == 1 and y == 1:
        tp += 1
    elif p == 1:
        fp += 1
    elif y == 1:
        fn += 1
    else:
        tn += 1

n = tp + fp + fn + tn
prec = tp / max(tp + fp, 1)
rec = tp / max(tp + fn, 1)
f1 = 2 * prec * rec / max(prec + rec, 1e-9)
fraud_rate = fraud_labeled / max(n, 1)
pred_rate = (tp + fp) / max(n, 1)
flags = []
if n > 0 and abs(fraud_rate - seed_baseline) / seed_baseline > 0.5:
    flags.append("fraud_rate_drift_watch")

met = {"asof": asof, "label_delay_days": delay, "labeled_rows": n,
       "unlabeled_rows": unlabeled, "threshold": float(scored[next(iter(scored))]["threshold"]) if scored else None,
       "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3),
       "fraud_rate": round(fraud_rate, 4), "pred_rate": round(pred_rate, 4),
       "flags": flags,
       "note": "label simulasi dengan delay; baris muda dilaporkan, bukan ditebak"}
json.dump(met, open("reports/reconcile_metrics.json", "w"), indent=2)
print(met)
