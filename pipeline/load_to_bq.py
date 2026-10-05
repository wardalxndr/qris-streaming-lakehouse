"""Load 3 mart gold ke BigQuery (dataset qris_analytics)."""
from google.cloud import bigquery
from google.oauth2 import service_account
import glob, os

KEY = r"C:\Users\lexdw\OneDrive\Documents\Default Project\data-engineering-zoomcamp-2026\01-docker-terraform\epoch-ai-data-center-04c3c8ec7e85.json"
PROJECT = "epoch-ai-data-center"
DATASET = "qris_analytics"

creds = service_account.Credentials.from_service_account_file(KEY)
bq = bigquery.Client(project=PROJECT, credentials=creds)
bq.query(f"CREATE SCHEMA IF NOT EXISTS `{PROJECT}.{DATASET}` OPTIONS(location='US')").result()

job_cfg = bigquery.LoadJobConfig(source_format="CSV", skip_leading_rows=1,
                                 autodetect=True, write_disposition="WRITE_TRUNCATE")
for path in sorted(glob.glob("data/mart_*.csv")):
    table = f"{PROJECT}.{DATASET}.{os.path.splitext(os.path.basename(path))[0]}"
    with open(path, "rb") as f:
        bq.load_table_from_file(f, table, job_config=job_cfg).result()
    print(table, "->", bq.get_table(table).num_rows, "rows")
