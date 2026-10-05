# QRIS Streaming Lakehouse — Real time Fraud Analytics

QRIS is Indonesia's national instant payment rail.
Simulated QRIS payment stream → bronze/silver/gold lakehouse → fraud marts + dashboard.
Built to be reproducible: one seed regenerates everything.

## Problem
QRIS money moves fast, so fraud must be caught fast. This pipeline answers:
which merchants leak fraud volume, what fraud types trend daily, which users are high risk.

## Architecture (simulated stream + batch)
```
pipeline/gen_qris.py (seed=42, 100k txns, 2% fraud, 4 types)
  -> data/bronze/qris_raw.csv       # raw stream landing
  -> pipeline/clean_silver.py       # dedup, validate, velocity window flags
  -> data/qris_clean.csv
  -> pipeline/build_gold.py         # mart_merchant_volume, mart_fraud_flags, mart_user_risk
  -> pipeline/load_to_bq.py         # BigQuery dataset qris_analytics
  -> Looker dashboard (3 tiles)
```
## Real time (local Kafka, Docker)
```
docker compose -f docker-compose.kafka.yml up -d   # KRaft broker + qris-txns topic (3 partitions)
python pipeline/produce.py    # send 100K events
python pipeline/consume.py    # clean live -> data/qris_clean_live.csv
```
Proven: consumer down during produce → caught up 100,000/100,000, 0 duplicates, 0 lost.
Roadmap: Spark Structured Streaming + cloud deploy.

## Results
- 100,000 txns, 1.95% fraud (velocity / night / round_amount / new_device)
- 0 duplicates, 0 corrupt rows after quality gates
- 39 high risk users (score >= 8)

```
python pipeline/run_pipeline.py   # generate -> silver -> gold -> forecast (one command)
python pipeline/load_to_bq.py   # BigQuery dataset qris_analytics (needs service-account JSON)
```
Lakehouse layout (same pattern as a retail Walmart project, upgraded to QRIS):
`pipeline/` runs locally, `spark/` is a Spark Structured Streaming reference,
`dags/` a daily Airflow example, `sql/` analytics queries, `data/` outputs, `reports/` metrics.

## Machine learning
`pipeline/model.py` trains a LogisticRegression (fraud probability per transaction,
time split: 3 weeks train, 1 week test). Honest metrics in `reports/model_metrics.json`
(precision/recall/F1 + chosen threshold). Rules stay alongside the model:
rules catch clear patterns (velocity needs history, a single-row model cannot see that),
the model gives a probability whose threshold shifts with risk appetite.

## Forecast
`pipeline/forecast.py` forecasts daily fraud 7 days ahead (7-day average x weekday
factor x payday boost, like Walmart holiday features). 7-day backtest: MAE ~81 vs
~136/day average — naive v1 model, honestly recorded in `reports/forecast_metrics.json`.

## Source
Synthetic data (own generator). Fraud patterns modeled on common e-wallet typologies.
