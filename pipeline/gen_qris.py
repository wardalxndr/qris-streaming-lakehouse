import csv, random

SEED = 42
N = 100_000  # total event: baris valid + baris kotor
FRAUD_RATE = 0.02
# ~1% baris kotor supaya quality gate di silver beneran pernah menolak,
# bukan cuma klaim. Kontrak: dihitung persis di tests/test_data_quality.py.
DIRTY_DUP = 300      # txn_id persis sama dengan baris lain -> ketangkap dedup
DIRTY_AMOUNT = 350   # amount kosong / negatif -> reject validasi amount
DIRTY_TS = 200       # ts tidak bisa diparse -> reject validasi ts

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


def dirty_rows(clean: list[list]) -> list[list]:
    """Baris kotor deterministik. Sumber diambil dari rentang index yang
    tidak tumpang tindih supaya kategori reject tidak saling makan
    (tanpa itu, salinan amount hancur bisa terhitung sebagai dup)."""
    out = []
    for i in range(DIRTY_DUP):
        out.append(list(clean[i]))  # salinan persis -> txn_id dobel
    for i in range(DIRTY_AMOUNT):
        r = list(clean[DIRTY_DUP + i])
        r[5] = "" if i % 2 == 0 else "-500"
        out.append(r)
    for i in range(DIRTY_TS):
        r = list(clean[DIRTY_DUP + DIRTY_AMOUNT + i])
        # hour 25-29 = di luar range %H (0-23), pasti gagal diparse
        r[1] = "2026-09-32 08:99" if i % 2 == 0 else f"2026-09-10 {25 + (i % 5)}:15"
        out.append(r)
    return out


def main():
    cols = ["txn_id", "ts", "user_id", "merchant_id", "merchant_cat", "amount",
            "city", "device_id", "channel", "is_fraud", "fraud_type"]
    n_valid = N - DIRTY_DUP - DIRTY_AMOUNT - DIRTY_TS
    n_fraud = 0
    clean = []
    for _ in range(n_valid):
        fraud = rng.random() < FRAUD_RATE
        row = fraud_txn() if fraud else normal_txn()
        n_fraud += fraud
        clean.append(row)
    rows = clean + dirty_rows(clean)
    with open("data/bronze/qris_raw.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    print(f"total={N} valid={n_valid} fraud={n_fraud} ({n_fraud / n_valid:.2%} "
          f"dari baris valid) dirty: {DIRTY_DUP} dup, {DIRTY_AMOUNT} amount, {DIRTY_TS} ts")


if __name__ == "__main__":
    main()
