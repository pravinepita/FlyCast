import os
import pandas as pd
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

GOOD_DIR = "/opt/airflow/good_data"
PREDICTIONS_DIR = "/opt/airflow/predictions"
PROCESSED_LOG = os.path.join(PREDICTIONS_DIR, "processed_files.csv")
API_URL = "http://host.docker.internal:8000/predict"  # FastAPI service inside Docker

def check_for_new_data(**context):
    os.makedirs(PREDICTIONS_DIR, exist_ok=True)
    
    # Load processed file log (optional, here just for info)
    if os.path.exists(PROCESSED_LOG):
        processed_files = pd.read_csv(PROCESSED_LOG)['file_name'].tolist()
    else:
        processed_files = []

    all_files = os.listdir(GOOD_DIR)
    new_files = all_files  # Force all files to be treated as new for testing

    context["ti"].xcom_push(key="new_files", value=new_files)
    print("Files to process:", new_files)


def make_predictions(**context):
    new_files = context["ti"].xcom_pull(key="new_files")
    if not new_files:
        print("No files to process. Exiting.")
        return

    os.makedirs(PREDICTIONS_DIR, exist_ok=True)

    for file in new_files:
        file_path = os.path.join(GOOD_DIR, file)
        df = pd.read_csv(file_path)

        predictions = []
        for _, row in df.iterrows():
            payload = {
                'Airline': row['Airline'],
                'Source': row['Source'],
                'Destination': row['Destination'],
                'Total_Stops': row['Total_Stops'],
                'Date_of_Journey': row['Date_of_Journey'],
                'Dep_Time': row['Dep_Time'],
                'Arrival_Time': row['Arrival_Time'],
                'Duration': row['Duration']
            }
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                predictions.append(response.json()['predicted_price'])
            else:
                predictions.append(None)

        df['Predicted_Price'] = predictions

        # Save CSV with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pred_file = os.path.join(PREDICTIONS_DIR, f"pred_{file.split('.')[0]}_{timestamp}.csv")
        df.to_csv(pred_file, index=False)
        print(f"Predictions saved to {pred_file}")

        # Update processed log
        if os.path.exists(PROCESSED_LOG):
            processed_log = pd.read_csv(PROCESSED_LOG)
        else:
            processed_log = pd.DataFrame(columns=['file_name', 'processed_at'])
        processed_log = pd.concat([processed_log, pd.DataFrame([{'file_name': file, 'processed_at': datetime.now()}])], ignore_index=True)
        processed_log.to_csv(PROCESSED_LOG, index=False)


# DAG definition
with DAG(
    dag_id="prediction_dag",
    start_date=datetime(2025, 8, 17),
    schedule="*/2 * * * *",  # every 2 minutes
    catchup=False,
    tags=["prediction"],
) as dag:

    t1 = PythonOperator(task_id="check_for_new_data", python_callable=check_for_new_data)
    t2 = PythonOperator(task_id="make_predictions", python_callable=make_predictions)

    t1 >> t2
