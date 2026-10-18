"""Load silver CSV ke BigQuery (dataset qris_analytics, tabel silver_transactions).

Creds 100% env, tanpa hardcode:
  set GCP_PROJECT_ID=your-gcp-project
  set GOOGLE_APPLICATION_CREDENTIALS=C:\\path\\key.json
Jalankan dari mana saja (path sudah absolut):  python pipeline/load_to_bq.py

Mart gold DIBANGUN dbt (qris_analytics/models), bukan script ini.
Versi lama file ini yang load mart CSV langsung sudah pensiun.
"""
import os
from pathlib import Path

from google.cloud import bigquery

DATA = Path(__file__).resolve().parents[1] / "data"
PROJECT = os.environ["GCP_PROJECT_ID"]
DATASET = "qris_analytics"
TABLE = "silver_transactions"

SCHEMA = [
    bigquery.SchemaField("txn_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ts", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("merchant_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("merchant_cat", "STRING"),
    bigquery.SchemaField("amount", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("city", "STRING"),
    bigquery.SchemaField("device_id", "STRING"),
    bigquery.SchemaField("channel", "STRING"),
    bigquery.SchemaField("is_fraud", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("fraud_type", "STRING"),
]


def main():
    bq = bigquery.Client(project=PROJECT)
    bq.create_dataset(f"{PROJECT}.{DATASET}", exists_ok=True)
    job_cfg = bigquery.LoadJobConfig(
        source_format="CSV",
        skip_leading_rows=1,
        schema=SCHEMA,
        write_disposition="WRITE_TRUNCATE",
    )
    table = f"{PROJECT}.{DATASET}.{TABLE}"
    with open(DATA / "qris_clean.csv", "rb") as f:
        bq.load_table_from_file(f, table, job_config=job_cfg).result()
    print(table, "->", bq.get_table(table).num_rows, "rows")


if __name__ == "__main__":
    main()
