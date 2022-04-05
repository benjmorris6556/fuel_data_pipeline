# GCP
## Initial Setup

1. Create a GCP account
2. Set up a new project or use one created for you (My First Project)
3. Setup [service account & authentication](https://cloud.google.com/docs/authentication/getting-started) for this project
    * Grant Viewer role to begin with.
    * Download service-account-keys (.json) for auth. (Please do not share this key file publicly. Keep it secure!)
    * Rename the .json key file to google_credentials.json
    **NOTE: If you're using a VM such as Google Compute Engine, you'll have to move the credentials json file to the machine for the pipeline to work. This can be done using [SFTP](https://www.ssh.com/academy/ssh/sftp).**
4. Download [SDK](https://cloud.google.com/sdk/docs/install-sdk) (if setting up locally)
5. Set environment variable to point to your downloaded GCP keys:
    ```
    export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/google_credentials.json>"

    # Refresh token/session, and verify authentication
    gcloud auth application-default login
    ```

## Setup for Access

1. IAM Roles for Service account:

    * Go to the IAM section of IAM & Admin: https://console.cloud.google.com/iam-admin/iam
    * Click the Edit principal icon for your service account.
    * Add these roles in addition to Viewer : Storage Admin + Storage Object Admin + BigQuery Admin
2. Enable the follwing APIs for your project:
    * https://console.cloud.google.com/apis/library/iam.googleapis.com
    * https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com
    **NOTE: There may be additional API's you'll need to enable along the way but you should be prompted to do so.**
3. Ensure `GOOGLE_APPLICATION_CREDENTIALS` enviroment variable is set:

    ```
    export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
    ```