"""Producer: kirim bronze CSV ke topik qris-txns (simulasi event live)."""
import csv, json, time
from kafka import KafkaProducer

p = KafkaProducer(bootstrap_servers="localhost:9092",
                  value_serializer=lambda v: json.dumps(v).encode())
n = 0
with open("data/bronze/qris_raw.csv", newline="") as f:
    for r in csv.DictReader(f):
        r["amount"] = int(r["amount"])
        p.send("qris-txns", value=r)
        n += 1
        if n % 20000 == 0:
            print(f"sent {n}")
            time.sleep(0.2)  # biar kelihatan ngalir, bukan sekejap
p.flush()
print(f"DONE sent={n}")
