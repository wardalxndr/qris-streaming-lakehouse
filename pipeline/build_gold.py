"""Gold: 3 mart siap dashboard dari silver."""
import csv, json
from collections import defaultdict

RISK_W = {"velocity": 4, "velocity_detected": 4, "night": 3, "round_amount": 2, "new_device": 2}


def main():
    rows = list(csv.DictReader(open("data/qris_clean.csv")))
    for r in rows:
        r["amount"] = int(r["amount"])
        r["day"] = r["ts"][:10]

    # 1. volume per merchant per hari
    vol = defaultdict(lambda: [0, 0])  # (merchant_id, day) -> [count, sum]
    for r in rows:
        k = (r["merchant_id"], r["merchant_cat"], r["city"], r["day"])
        vol[k][0] += 1
        vol[k][1] += r["amount"]
    with open("data/mart_merchant_volume.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["merchant_id", "merchant_cat", "city", "day", "txn_count", "total_amount"])
        for (mid, cat, city, day), (c, s) in sorted(vol.items()):
            w.writerow([mid, cat, city, day, c, s])

    # 2. fraud per tipe per hari
    fr = defaultdict(int)
    for r in rows:
        if str(r["is_fraud"]) == "1":
            fr[(r["day"], r["fraud_type"])] += 1
    with open("data/mart_fraud_flags.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["day", "fraud_type", "count"])
        for (day, t), c in sorted(fr.items()):
            w.writerow([day, t, c])

    # 3. skor risiko per user 0-10
    score = defaultdict(int)
    for r in rows:
        if str(r["is_fraud"]) == "1":
            score[r["user_id"]] += RISK_W.get(r["fraud_type"], 1)
    with open("data/mart_user_risk.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["user_id", "risk_score", "risk_band"])
        for u, s in sorted(score.items(), key=lambda x: -x[1]):
            band = "high" if s >= 8 else ("medium" if s >= 4 else "low")
            w.writerow([u, min(s, 10), band])

    rep = {"total": len(rows),
           "merchants": len({r["merchant_id"] for r in rows}),
           "high_risk_users": sum(1 for s in score.values() if s >= 8)}
    json.dump(rep, open("reports/quality_report.json", "w"), indent=2)
    print(rep)


if __name__ == "__main__":
    main()
