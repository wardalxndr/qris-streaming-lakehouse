"""Consumer streaming: baca Kafka -> clean -> tulis silver live + flag velocity.
State velocity disimpan di memori per jendela 10 menit (demo; produksi pakai state store).
Topik dan idle timeout bisa dioverride lewat env QRIS_TOPIC / QRIS_CONSUMER_TIMEOUT_MS
(dipakai test E2E; default sama seperti sebelumnya)."""
import csv, json, os
from collections import defaultdict
from datetime import datetime
from kafka import KafkaConsumer

TOPIC = os.environ.get("QRIS_TOPIC", "qris-txns")
TIMEOUT_MS = int(os.environ.get("QRIS_CONSUMER_TIMEOUT_MS", "30000"))

seen, dups, bad, velo = set(), 0, 0, 0
buckets = defaultdict(int)
out = open("data/qris_clean_live.csv", "w", newline="")
w = csv.DictWriter(out, fieldnames=["txn_id", "ts", "user_id", "merchant_id", "merchant_cat",
                                    "amount", "city", "device_id", "channel", "is_fraud", "fraud_type"])
w.writeheader()

c = KafkaConsumer(TOPIC, bootstrap_servers="localhost:9092",
                  value_deserializer=lambda v: json.loads(v.decode()),
                  auto_offset_reset="earliest", enable_auto_commit=True,
                  consumer_timeout_ms=TIMEOUT_MS)
n = 0
for m in c:
    r = m.value
    if r["txn_id"] in seen:
        dups += 1
        continue
    seen.add(r["txn_id"])
    if int(r["amount"]) <= 0:
        bad += 1
        continue
    ts = datetime.strptime(r["ts"], "%Y-%m-%d %H:%M")
    key = (r["user_id"], ts.replace(minute=(ts.minute // 10) * 10, second=0, microsecond=0))
    buckets[key] += 1
    if buckets[key] >= 5 and r["fraud_type"] == "-":  # velocity live
        r["fraud_type"], r["is_fraud"], velo = "velocity_detected", "1", velo + 1
    w.writerow({k: r[k] for k in w.fieldnames})
    n += 1
    if n % 20000 == 0:
        print(f"consumed {n} (dups={dups} bad={bad} velo={velo})")
out.close()
print(f"DONE clean={n} dups={dups} bad={bad} velocity_new={velo}")
