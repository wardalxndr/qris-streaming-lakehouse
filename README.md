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
Roadmap: replace file landing with Kafka + Spark Structured Streaming (same schema, same marts).

## Results
- 100,000 txns, 1.95% fraud (velocity / night / round_amount / new_device)
- 0 duplicates, 0 corrupt rows after quality gates
- 39 high-risk users (score >= 8)

## How to run
```
python generator/gen_qris.py
python silver/clean.py
python gold/marts.py
python load_to_bq.py   # needs service-account JSON, see Epoch project
```

## Source
Synthetic data (own generator). Fraud patterns modeled on common e-wallet typologies.
