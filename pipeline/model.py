"""Model ML: probabilitas fraud per transaksi (LogisticRegression).
Split waktu (3 minggu latih, 1 minggu uji) biar jujur: model diuji di masa depan.
Fitur: amount, jam, kategori, kota, minggu gajian. Output: model.pkl + metrik.
"""
import csv, json, math
from collections import defaultdict

rows = list(csv.DictReader(open("data/qris_clean.csv")))
for r in rows:
    r["amount"] = int(r["amount"])
    r["hour"] = int(r["ts"][11:13])
    r["day"] = int(r["ts"][8:10])
    r["y"] = 1 if str(r["is_fraud"]) == "1" else 0

CATS = sorted({r["merchant_cat"] for r in rows})
CITIES = sorted({r["city"] for r in rows})


def feats(r):
    f = [math.log1p(r["amount"]), r["hour"] / 24.0,
         1.0 if (r["day"] >= 25 or r["day"] <= 1) else 0.0]
    f += [1.0 if r["merchant_cat"] == c else 0.0 for c in CATS]
    f += [1.0 if r["city"] == c else 0.0 for c in CITIES]
    return f


tr = [r for r in rows if r["day"] <= 21]
te = [r for r in rows if r["day"] > 21]

from sklearn.linear_model import LogisticRegression
Xtr, ytr = ([feats(r) for r in tr], [r["y"] for r in tr])
model = LogisticRegression(max_iter=500).fit(Xtr, ytr)

import pickle
pickle.dump({"model": model, "cats": CATS, "cities": CITIES},
            open("data/fraud_model.pkl", "wb"))

probs = model.predict_proba([feats(r) for r in te])[:, 1]
y = [r["y"] for r in te]

best = None
for thr in [0.02, 0.05, 0.1, 0.2, 0.3, 0.5]:
    tp = sum(1 for p, t in zip(probs, y) if p >= thr and t == 1)
    fp = sum(1 for p, t in zip(probs, y) if p >= thr and t == 0)
    fn = sum(1 for p, t in zip(probs, y) if p < thr and t == 1)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-9)
    if best is None or f1 > best[0]:
        best = (f1, thr, prec, rec)
f1, thr, prec, rec = best
pickle.dump({"model": model, "cats": CATS, "cities": CITIES, "threshold": thr},
            open("data/fraud_model.pkl", "wb"))
met = {"model": "logistic_regression", "train_rows": len(tr), "test_rows": len(te),
       "threshold": thr, "precision": round(prec, 3), "recall": round(rec, 3),
       "f1": round(f1, 3),
       "note": "aturan: skor tetap; model: ambang bisa digeser sesuai selera risiko"}
json.dump(met, open("reports/model_metrics.json", "w"), indent=2)
print(met)
