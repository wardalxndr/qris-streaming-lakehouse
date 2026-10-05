"""Silver: bersihin bronze + deteksi velocity + laporan kualitas.
Kecepatan = jumlah transaksi 1 user dalam 10 menit >= 5 -> flag.
"""
import csv
from collections import defaultdict
from datetime import datetime

WINDOW_MIN = 10
VELOCITY_MIN = 5


def parse_ts(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def main():
    seen, dups = set(), 0
    bad_amount, bad_ts = 0, 0
    rows = []
    with open("data/bronze/qris_raw.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["txn_id"] in seen:  # buang duplikat
                dups += 1
                continue
            seen.add(r["txn_id"])
            try:
                amt = int(r["amount"])
            except ValueError:
                amt = -1
            if amt <= 0:
                bad_amount += 1
                continue
            ts = parse_ts(r["ts"])
            if ts is None:
                bad_ts += 1
                continue
            r["amount"] = amt
            r["_ts"] = ts
            rows.append(r)

    # deteksi velocity: hitung per user per jendela 10 menit
    buckets = defaultdict(list)
    for r in rows:
        key = (r["user_id"], r["_ts"].replace(minute=(r["_ts"].minute // WINDOW_MIN) * WINDOW_MIN,
                                             second=0, microsecond=0))
        buckets[key].append(r)
    velo_hits = 0
    for key, grp in buckets.items():
        if len(grp) >= VELOCITY_MIN:
            for r in grp:
                if r["fraud_type"] == "-":
                    r["fraud_type"] = "velocity_detected"
                    r["is_fraud"] = "1"
                    velo_hits += 1

    cols = ["txn_id", "ts", "user_id", "merchant_id", "merchant_cat", "amount",
            "city", "device_id", "channel", "is_fraud", "fraud_type"]
    with open("data/qris_clean.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r[c] for c in cols})

    print(f"clean={len(rows)} dups={dups} bad_amount={bad_amount} "
          f"bad_ts={bad_ts} velocity_new_flags={velo_hits}")


if __name__ == "__main__":
    main()
