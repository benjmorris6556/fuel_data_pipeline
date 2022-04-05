# Terraform Infra Setup

1. Clone the repository in your local machine.

```
git clone https://github.com/benjmorris6556/fuel_data_pipeline.git
cd fuel_data_pipeline/terraform
```

2. Create the GCP infrastructure:

    * Intiate Terraform and download the required dependencies...
    `terraform init`
    * View the Terraform plan (you'll have to enter the name for you GCS bucket and the name of your GCP Project)...
    `terraform plan`
    * The plan should show the following services:
        * e2-standard-4 Compute Instance for Airflow
        * A GCS bucket
        * Two BigQuery datasets (one for staging, one for production)
    **NOTE: The provided Terraform plan will spin up a new VM - if you don't need one please remove this from the [main.tf](terraform/main.tf) file.**
    * Build the infrastrucure according to the plan...
    `terraform apply`
    * Once you're finished with the project, destroy the infrastructure to avoid unnecessary billing...
    `terraform destroy`