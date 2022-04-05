# VM SSH Setup

1. [Create a ssh key](https://cloud.google.com/compute/docs/connect/create-ssh-keys#linux-and-macos) in your local system: <your-home-directory>/.ssh/
2. [Add the public key](https://cloud.google.com/compute/docs/connect/add-ssh-keys#expandable-2) (.pub) to your VM instance. 
3. Create a config file in your .ssh folder:
    `touch ~/.ssh/config`
4. Copy the following snippet where External IP Address is the that of your VM, username is your username for the VM and the path is where your private SSH key file is stored:
    ```
    Host your-vm
        HostName <External IP Address>
        User <username>
        IdentityFile <path/to/home/.ssh/gcp>
    ```
5. You can now SSH into the VM and install any base requirements (ie. Python, Docker, etc.) with the following command:
    `ssh your-vm`