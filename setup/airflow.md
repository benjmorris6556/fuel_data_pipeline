# Setting up Airflow using Docker Compose

The Airflow instance we'll be using will be setup using multiple Docker containers. All required Python packages are installed on `docker-compose build`, including dbt.

1. Establish SSH connection to your VM (if required)...
`ssh your-vm`

2. Clone the git repo...
```
git clone https://github.com/benjmorris6556/fuel_data_pipeline.git
cd fuel_data_pipeline
```

3. Install required software (Anaconda, Docker & Docker Compose)...
```
bash ~/fuel_data_pipeline/scripts/vm_setup.sh && \
exec newgrp docker
```
4. Create the logs folder for Airflow...
```
mkdir logs
```

5. Ensure your Google credentials json file for your service account is in the `~/.google/credentials/` directory and named `google_credentials.json`. As mentioned, this file can be transferred from your local machine using [SFTP](https://www.ssh.com/academy/ssh/sftp).

6. Create a `.env` file in the main project directory containing the variables needed for your project. For example:
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

7. Build and intialise your Airflow instance...
```
cd ~/fuel_data_pipeline
docker-compose build

docker-compose up airflow-init

docker-compose up -d
```

8. Once completed, Airflow will be running and the UI available in your browser at `localhost:8080`. To terminate Airflow and the Docker containers, execute `docker-compose down`.

## DAGS

## dbt