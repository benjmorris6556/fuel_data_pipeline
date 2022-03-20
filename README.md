# Fuel Data Pipeline

This data pipeline is a Dockerised Airflow instance that contains DAGs to retrieve the daily average wholesale (TGP) diesel fuel prices from the Australian Institute of Petroleum (https://www.aip.com.au).

The DAGs perform the following tasks:

  1. Retrieve the data from their respective sources. For historical prices they will come directly from a XLSX file, for the most recent prices they must be scraped from the HTML of the website itself.
  2. Format the retrieved data locally using Pandas, convert to CSV.
  3. Convert the file to Parquet for efficient storage.
  4. Upload the Parquet file to a pre-defined GCS bucket. 
  5. Delete local CSV and Parquet files.
  6. Create an external table in a pre-defined BigQuery dataset in order to query the data. 

## Useage

Ensure a .env file exists in the main directory that specifies the required enviroment variables. For example:

```
GOOGLE_APPLICATION_CREDENTIALS=<PATH_TO_YOUR_GCP_SERVICE_ACCOUNT_CREDS>
GCP_PROJECT_ID=<YOUR_GCP_PROJECT_ID>
GCP_GCS_BUCKET=<YOUR_GCP_BUCKET_ID>
```

Run `docker-compose build` to create the required Docker containers. 
Run `docker-compose up` to initiate the Docker containers. 

If all was successful, you should be able to login to Airflow in your browser via localhost:8080 and schedule the DAGs to run as required. 
