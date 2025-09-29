import os
import random
import shutil
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from validation.data_validator import validate_file
import csv
from datetime import datetime

RAW_DIR = "/opt/airflow/raw-data"
GOOD_DIR = "/opt/airflow/good_data"
BAD_DIR = "/opt/airflow/bad_data"
STATS_DIR = "/opt/airflow/stats"
# ---- TASK 1: Read random file ----
def read_data(**context):
    files = os.listdir(RAW_DIR)
    if not files:
        raise FileNotFoundError("No raw files available")
    file = random.choice(files)
    file_path = os.path.join(RAW_DIR, file)
    context["ti"].xcom_push(key="file_path", value=file_path)

# ---- TASK 2: Validate file ----
def validate_data(**context):
    file_path = context["ti"].xcom_pull(key="file_path", task_ids="read_data")
    if not file_path:
        raise ValueError("No file_path found in XCom")
    df, stats = validate_file(file_path)

    # Convert numpy.int64 to int
    stats["valid"] = int(stats["valid"])
    stats["invalid"] = int(stats["invalid"])
    stats["rows"] = int(stats["rows"])

    context["ti"].xcom_push(key="validation_stats", value=stats)
    context["ti"].xcom_push(key="df_pickle", value=df.to_dict())



# ---- TASK 3: Save statistics ----
def save_statistics(**context):
    stats = context["ti"].xcom_pull(key="validation_stats", task_ids="validate_data")
    file_path = context["ti"].xcom_pull(key="file_path", task_ids="read_data")
    file_name = os.path.basename(file_path) if file_path else "unknown_file"

    if stats is None:
        raise ValueError("No validation stats found in XCom for save_statistics")

    # Ensure the stats folder exists
    os.makedirs(STATS_DIR, exist_ok=True)

    # Create a timestamped CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_file = os.path.join(STATS_DIR, f"stats_{file_name}_{timestamp}.csv")

    # Write stats to CSV
    with open(stats_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file_name", "total_rows", "valid_rows", "invalid_rows", "errors"])
        writer.writerow([
            file_name,
            stats.get("rows", 0),
            stats.get("valid", 0),
            stats.get("invalid", 0),
            "; ".join(stats.get("errors", []))
        ])

    print(f"Stats saved to {stats_file}")


# ---- TASK 4: Send alerts ----
def send_alerts(**context):
    stats = context["ti"].xcom_pull(key="validation_stats", task_ids="validate_data")
    if stats is None:
        raise ValueError("No validation stats found in XCom")
    if stats["errors"]:
        print("ALERT 🚨:", stats["errors"])

# ---- TASK 5: Split and save ----
def split_and_save_data(**context):
    file_path = context["ti"].xcom_pull(key="file_path", task_ids="read_data")
    stats = context["ti"].xcom_pull(key="validation_stats", task_ids="validate_data")
    df_dict = context["ti"].xcom_pull(key="df_pickle", task_ids="validate_data")

    if file_path is None or stats is None or df_dict is None:
        raise ValueError("Missing XCom data in split_and_save_data")

    df = pd.DataFrame.from_dict(df_dict)

    if stats["invalid"] == 0:
        shutil.move(file_path, os.path.join(GOOD_DIR, os.path.basename(file_path)))
    elif stats["valid"] == 0:
        shutil.move(file_path, os.path.join(BAD_DIR, os.path.basename(file_path)))
    else:
        good_df = df.dropna()
        bad_df = df[df.isna().any(axis=1)]
        good_df.to_csv(os.path.join(GOOD_DIR, f"good_{os.path.basename(file_path)}"), index=False)
        bad_df.to_csv(os.path.join(BAD_DIR, f"bad_{os.path.basename(file_path)}"), index=False)
        os.remove(file_path)


# ---- DAG definition ----
with DAG(
    dag_id="data_ingestion_dag",
    start_date=datetime(2025, 8, 1),
    schedule=None,
    catchup=False,
    tags=["data_ingestion"],
) as dag:

    t1 = PythonOperator(task_id="read_data", python_callable=read_data)
    t2 = PythonOperator(task_id="validate_data", python_callable=validate_data)
    t3 = PythonOperator(task_id="save_statistics", python_callable=save_statistics)
    t4 = PythonOperator(task_id="send_alerts", python_callable=send_alerts)
    t5 = PythonOperator(task_id="split_and_save_data", python_callable=split_and_save_data)

    t1 >> t2 >> [t3, t4, t5]
