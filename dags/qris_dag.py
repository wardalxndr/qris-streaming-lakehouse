"""Contoh Airflow DAG harian (produksi). Lokal: python pipeline/run_pipeline.py."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG("qris_lakehouse",
         start_date=datetime(2026, 10, 1),
         schedule_interval="@daily",
         catchup=False,
         default_args={"retries": 1, "retry_delay": timedelta(minutes=5)}) as dag:
    gen = BashOperator(task_id="generate", bash_command="python pipeline/gen_qris.py")
    clean = BashOperator(task_id="silver", bash_command="python pipeline/clean_silver.py")
    gold = BashOperator(task_id="gold", bash_command="python pipeline/build_gold.py")
    forecast = BashOperator(task_id="forecast", bash_command="python pipeline/forecast.py")
    gen >> clean >> gold >> forecast
