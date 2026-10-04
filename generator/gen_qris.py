import csv, random

SEED = 42
N = 100_000
FRAUD_RATE = 0.02
CATS = ["kuliner", "ritel", "transport"]
CITIES = ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang"]

rng = random.Random(SEED)  # seed sekali di sini = run 2x hasil sama
MERCHANTS = [(f"M{i:03d}", CATS[i % 3], CITIES[i % 5]) for i in range(30)]
USERS = [f"U{i:05d}" for i in range(5000)]
seen_devices = set()


def normal_txn():
    day = 25 if rng.random() < 0.3 else rng.randint(1, 28)  # gajian rame
    hour = rng.choice([12, 13, 19, 20]) if rng.random() < 0.6 else rng.randint(0, 23)
    m = rng.choice(MERCHANTS)
    dev = f"D{rng.randint(1000, 9999)}"
    seen_devices.add(dev)
    return [f"T{rng.randint(10**9, 10**10-1)}", f"2026-09-{day:02d} {hour:02d}:{rng.randint(0,59):02d}",
            rng.choice(USERS), m[0], m[1], int(rng.lognormvariate(10.5, 0.8)),
            m[2], dev, "QRIS", 0, "-"]


def fraud_txn():
    t = rng.choice(["velocity", "night", "round_amount", "new_device"])
    r = normal_txn()
    r[9], r[10] = 1, t
    if t == "night":
        r[1] = r[1][:11] + f"0{rng.randint(1,4)}:{rng.randint(10,59)}"
    if t == "round_amount":
        r[5] = rng.choice([500000, 1000000, 2000000])
    if t == "new_device":
        r[7] = f"DX{rng.randint(1000,9999)}"  # belum pernah lihat = mencurigakan
    return r  # velocity: label aja dulu, deteksinya di silver nanti pakai window


def main():
    cols = ["txn_id", "ts", "user_id", "merchant_id", "merchant_cat", "amount",
            "city", "device_id", "channel", "is_fraud", "fraud_type"]
    n_fraud = 0
    with open("bronze/qris_raw.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for _ in range(N):
            fraud = rng.random() < FRAUD_RATE
            w.writerow(fraud_txn() if fraud else normal_txn())
            n_fraud += fraud
    print(f"total={N} fraud={n_fraud} ({n_fraud / N:.2%})")


if __name__ == "__main__":
    main()
