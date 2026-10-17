"""Contoh Airflow DAG harian (produksi). Lokal: python pipeline/run_pipeline.py.

Kompatibel Airflow 2.9+ dan 3.x:
- pakai `schedule=` (argumen `schedule_interval` dihapus di Airflow 3).
- import DAG/BashOperator dicoba dari lokasi baru dulu, fallback ke lama.
- perintah pakai `cd` absolut supaya tidak bergantung working directory task.
"""
from datetime import datetime, timedelta
from pathlib import Path

try:  # Airflow 3.x
    from airflow.sdk import DAG
except ImportError:  # Airflow 2.9.x
    from airflow import DAG

try:  # Airflow 3.x
    from airflow.providers.standard.operators.bash import BashOperator
except ImportError:  # Airflow 2.9.x
    from airflow.operators.bash import BashOperator

PROJECT_ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("generate", "gen_qris.py"),
    ("silver", "clean_silver.py"),
    ("gold", "build_gold.py"),
    ("forecast", "forecast.py"),
    ("score", "score.py"),
    ("reconcile", "reconcile.py"),
    ("retrain", "retrain.py"),
]

with DAG("qris_lakehouse",
         start_date=datetime(2026, 10, 1),
         schedule="@daily",
         catchup=False,
         default_args={"retries": 1, "retry_delay": timedelta(minutes=5)}) as dag:
    tasks = [
        BashOperator(task_id=name,
                     bash_command=f"cd '{PROJECT_ROOT}' && python pipeline/{script}")
        for name, script in STEPS
    ]
    for upstream, downstream in zip(tasks, tasks[1:]):
        upstream >> downstream
