# Australian Fuel Data Pipeline

A data pipeline utilising Docker, Airflow, GCP, Terraform, dbt and more!

## Description

### Objective

This data pipeline is a Dockerised Airflow instance that contains DAGs to retrieve the daily average wholesale (TGP) diesel fuel prices from the [Australian Institute of Petroleum](https://www.aip.com.au).

The pipeline performs the following tasks:

  1. Retrieves the data from their respective sources. For historical prices they will come directly from a XLSX file published by the AIP, for the most recent prices (past 5 weekdays) they're retrieved directly from a public API.
  2. Converts the data to a Parquet format for efficient storage and upload to the data lake (GCS in this case).
  5. Creates external tables in BigQuery that contain the raw data for easy tracing of data lineage and future query flexibility. 
  6. Applies several transformations and customer calculations on the raw data to create a 'staging' layer.
  7. Materialises the most recent data in a fact table for use by end-users or production systems. 

### Datasets

Due to the availability and format of the two data sources, most of the complexity of the pipeline comes from recording the average TGP prices for each state on the day it's made available (this comes directly from the API), manually calculating the national average and then replacing that data in the final table as it becomes available in the historical dataset.

### Usage of Final Dataset

The final dataset is used in conjunction with my company's internal data relating to their customer's fuel levy requirements. For privacy reasons this can't be published publically, however each customer has different parameters for when and how the fuel levies that are applied to their ratecards in our operational systems are calculated. 

The final table created by this pipeline is integrated with our operational systems to automatically calculate those customer's fuel levies on the day that they're required to be recalculated. 

### Tools & Technologies

* Cloud - [Google Cloud Platform](https://cloud.google.com/)
* Containerisation - [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/)
* Orchestration - [Airflow](https://airflow.apache.org/)
* Transformation - [dbt](https://www.getdbt.com/)
* Data Lake - [Google Cloud Storage](https://cloud.google.com/storage)
* Data Warehouse - [Google BigQuery](https://cloud.google.com/bigquery)
* Language - [Python](https://www.python.org/)

### Architecture

![Pipeline architecture](images/architecture.png?raw=true "Pipeline architecture")

## Set Up

### Pre-Requisites

You'll require a Google Cloud account to use GCS as the data lake and BigQuery as the data warehouse. Set up instructions for GCP can be found [here](setup/gcp.md).

I've also been running this program on a Google Compute Engine instance which comes with the Google SDK packages pre-installed - if you want to run this pipeline locally, you'll need to install the [SDK](https://cloud.google.com/sdk/docs/install-sdk) package manually. 

If you'd also like to run the pipeline in a VM, the setup instructions can be found [here](setup/ssh.md).

### Running the Pipeline

  * Run Terraform to set up the required infrastructure for GCP.
  * [SSH into your VM](setup/ssh.md) and forward the relevant port to access the Airflow UI (default is 8080) once it's been intiated.
  * Setup Airflow and activate the DAGs to begin collecting the data. 

### Future Improvements
