# Fuel Data Pipeline

This data pipeline is a Dockerised Airflow instance that contains DAGs to retrieve the daily average wholesale (TGP) diesel fuel prices from the [Australian Institute of Petroleum](https://www.aip.com.au).

The DAGs perform the following tasks:

  1. Retrieve the data from their respective sources. For historical prices they will come directly from a XLSX file publish by AIP, for the most recent prices (past 5 weekdays) they must be scraped from the HTML of the website itself.
  2. Format the retrieved data locally using Pandas, convert to CSV.
  3. Convert the file to Parquet for efficient storage.
  4. Upload the Parquet file to a pre-defined GCS bucket that will act as our data lake. 
  5. Delete local CSV and Parquet files.
  6. Create an external table in a pre-defined BigQuery dataset in order to query the data. 

## Useage

For Airflow to interact with the GCP APIs required by the DAGs, please enable the relevant APIs - instructions on how to do so [here](https://cloud.google.com/apis/docs/getting-started).

Ensure a .env file exists in the main directory that specifies the required enviroment variables. For example:

```
GOOGLE_APPLICATION_CREDENTIALS=<LOCAL_PATH_TO_YOUR_GCP_CREDENTIALS_JSON>
AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=google-cloud-platform://?extra__google_cloud_platform__key_path=<LOCAL_PATH_TO_YOUR_GCP_CREDENTIALS_JSON>
AIRFLOW_UID=1001
GCP_PROJECT_ID=<YOUR_GCP_PROJECT_ID>
GCP_GCS_BUCKET=<YOUR_GCP_BUCKET_ID>

# Postgres
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

Run `docker-compose build` to create the required Docker containers. 
Run `docker-compose up` to initiate the Docker containers. 

If all was successful, you should be able to login to the Airflow webapp in your browser via localhost:8080 and schedule the DAGs to run as required. 
