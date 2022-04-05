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

historical_dataset_url = 'https://www.aip.com.au/sites/default/files/download-files/{{ execution_date.strftime(\'%Y-%m\') }}/AIP_TGP_Data_{{ execution_date.strftime(\'%d-%b-%Y\') }}.xlsx'
csv_file = 'historical_fuel_data_{{ execution_date.strftime(\'%d-%b-%Y\') }}.csv'
parquet_file = csv_file.replace('.csv', '.parquet')
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'daily_fuel_data')

def get_historical_fuel_data(source_url, dest_file):
    import pandas as pd
    import openpyxl

    fuel_prices_df = pd.read_excel(
        source_url, sheet_name="Diesel TGP", engine='openpyxl'
    )

    fuel_prices_df = fuel_prices_df.rename(
        columns={
            "National\nAverage": "national_average",
            "AVERAGE DIESEL TGPS\n(inclusive of GST)": "date",
        }
    )

    fuel_prices_df.columns = fuel_prices_df.columns.str.lower()
    fuel_prices_df = fuel_prices_df.tail(5)
    fuel_prices_df['date_created'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    fuel_prices_df.to_csv(dest_file, index=False)

def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, src_file.replace('.csv', '.parquet'))

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
    dag_id="historical_fuel_data_ingestion",
    schedule_interval="0 11 * * 5",
    default_args=default_args,
    catchup=False,
    max_active_runs=3,
    tags=['fuel_data'],
) as dag:

    create_dataset_task = PythonOperator(
        task_id="create_fuel_dataset",
        python_callable=get_historical_fuel_data,
        op_kwargs={
            "source_url": historical_dataset_url,
            "dest_file": f"{path_to_local_home}/{csv_file}",
        },
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{path_to_local_home}/{csv_file}",
        },
    )

    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"fuel_prices/raw/historical_fuel_prices/{parquet_file}",
            "local_file": f"{path_to_local_home}/{parquet_file}",
        },
    )

    delete_local_files_task = BashOperator(
        task_id="delete_local_files_task",
        bash_command=f"rm {path_to_local_home}/{csv_file} {path_to_local_home}/{parquet_file}"
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "raw_historical_fuel_prices",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/fuel_prices/raw/historical_fuel_prices/*"],
            },
        },
    )

    create_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> delete_local_files_task >> bigquery_external_table_task
