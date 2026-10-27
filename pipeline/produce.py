"""Producer: kirim bronze CSV ke topik qris-txns (simulasi event live).
Topik bisa dioverride lewat env QRIS_TOPIC (dipakai test E2E)."""
import csv, json, os, time
from kafka import KafkaProducer

TOPIC = os.environ.get("QRIS_TOPIC", "qris-txns")

p = KafkaProducer(bootstrap_servers="localhost:9092",
                  value_serializer=lambda v: json.dumps(v).encode())
n = 0
with open("data/bronze/qris_raw.csv", newline="") as f:
    for r in csv.DictReader(f):
        # amount dibiarkan string apa adanya; konversi+validasi di consumer,
        # supaya baris kotor ("" / negatif) ikut terkirim dan ditolak di sana.
        p.send(TOPIC, value=r)
        n += 1
        if n % 20000 == 0:
            print(f"sent {n}")
            time.sleep(0.2)  # biar kelihatan ngalir, bukan sekejap
p.flush()
print(f"DONE sent={n}")
