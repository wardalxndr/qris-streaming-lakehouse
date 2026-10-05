# QRIS Streaming Lakehouse — Real-time Fraud Analytics

Simulated QRIS payment stream → bronze/silver/gold lakehouse → fraud marts + dashboard.
Built to be reproducible: one seed regenerates everything.

## Problem
QRIS money moves fast — fraud must be caught fast. This pipeline answers:
which merchants leak fraud volume, what fraud types trend daily, which users are high-risk.

## Architecture (simulated stream + batch)
```
generator/gen_qris.py (seed=42, 100k txns, 2% fraud, 4 types)
  -> bronze/qris_raw.csv            # raw stream landing
  -> silver/clean.py                # dedup, validate, velocity window flags
  -> silver/qris_clean.csv
  -> gold/marts.py                  # mart_merchant_volume, mart_fraud_flags, mart_user_risk
  -> load_to_bq.py                  # BigQuery dataset qris_analytics
  -> Looker dashboard (3 tiles)
```
## Real-time (Kafka lokal, Docker)
```
docker compose -f docker-compose.kafka.yml up -d   # broker KRaft + topik qris-txns (3 partisi)
python pipeline/produce.py    # kirim 100K event
python pipeline/consume.py    # bersihin live -> data/qris_clean_live.csv
```
Terbukti: consumer mati saat produce → catch-up 100.000/100.000, 0 duplikat, 0 hilang.
Roadmap: Spark Structured Streaming + deploy cloud.

## Results
- 100,000 txns, 1.95% fraud (velocity / night / round_amount / new_device)
- 0 duplicates, 0 corrupt rows after quality gates
- 39 high-risk users (score >= 8)

```
python pipeline/run_pipeline.py   # generate -> silver -> gold -> forecast (1 perintah)
python pipeline/load_to_bq.py   # BigQuery dataset qris_analytics (butuh service-account JSON)
```
Struktur ala lakehouse (mirip proyek retail Walmart, upgrade ke QRIS):
`pipeline/` runnable lokal, `spark/` referensi Spark Structured Streaming,
`dags/` contoh Airflow harian, `sql/` query analitik, `data/` output, `reports/` metrik.

## Forecast
`pipeline/forecast.py` meramal fraud harian 7 hari ke depan (rata-rata 7 hari x faktor
weekday x boost gajian, ala fitur holiday Walmart). Backtest 7 hari: MAE ~81 vs rata-rata
~136/hari — model naive v1, jujur dicatat di `reports/forecast_metrics.json`.

## Source
Synthetic data (own generator). Fraud patterns modeled on common e-wallet typologies.
