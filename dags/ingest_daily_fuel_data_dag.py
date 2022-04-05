import logging
import os
from datetime import datetime

import pyarrow.csv as pv
import pyarrow.parquet as pq
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import \
    BigQueryCreateExternalTableOperator
from google.cloud import storage

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'daily_fuel_data')
DBT_PROFILE_PATH = os.environ.get("DBT_PROFILES_DIR")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
csv_file = 'daily_fuel_data_{{ execution_date.strftime(\'%d-%b-%Y\') }}.csv'
parquet_file = csv_file.replace('.csv', '.parquet')

def get_current_fuel_data(file_destination):
    import json

    import pandas as pd
    import requests

    url = "https://www.aip.com.au/aip-api-request?api-path=public/api&call=tgpTables&location="
    results = requests.get(url)
    fuel_data_json = results.json()

    def create_rows(result_rows, data):
        row = {}
        row['date'] = data['date']
        row['location'] = data['location']
        row['fuel_price'] = data['fuelPrice']
        row['date_created'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_rows.append(row)
        
    result_rows = []

    for location, daily_data in fuel_data_json.items():
        for day, data in daily_data.items():
            if data['fuelType'] == 'DIESEL' and day == '0':
                create_rows(result_rows, data)
            
    df = pd.DataFrame.from_dict(result_rows)
    df.to_csv(file_destination, index=False)

def format_to_parquet(src_file, dest_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, dest_file)

def upload_to_gcs(bucket, object_name, local_file):
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 3, 25),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="daily_fuel_data_ingestion",
    schedule_interval="30 10 * * 1-5",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=['fuel_data'],
) as dag:

    create_dataset_task = PythonOperator(
        task_id="create_fuel_dataset",
        python_callable=get_current_fuel_data,
        op_kwargs={
            "file_destination": f"{path_to_local_home}/{csv_file}",
        },
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{path_to_local_home}/{csv_file}",
            "dest_file": f"{path_to_local_home}/{parquet_file}"
        },
    )

    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"fuel_prices/raw/daily_fuel_prices/{parquet_file}",
            "local_file": f"{path_to_local_home}/{parquet_file}",
        },
    )

    delete_local_file_task = BashOperator(
        task_id="delete_local_files_task",
        bash_command=f"rm {path_to_local_home}/{csv_file} {path_to_local_home}/{parquet_file}"
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "raw_daily_fuel_prices",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/fuel_prices/raw/daily_fuel_prices/*"]
            },
        },
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {path_to_local_home}/dbt && pwd && dbt deps && dbt run --profiles-dir ."
    )

    create_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> delete_local_file_task >> bigquery_external_table_task >> dbt_run