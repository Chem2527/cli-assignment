# Setting up Slack Notifications in GitHub Actions for Container Vulnerability Scan using Trivy

## 1. GitHub Actions Workflow File
Below is the YAML configuration for the GitHub Actions pipeline that does the following:

```bash
Checkout code from the repository.

Build the Docker image using the Dockerfile.

Install and run Trivy to scan the Docker image for vulnerabilities.

Push the vulnerability scan report to an EC2 instance.

Send Slack notifications with build status and report location.
```
### Github actions pipeline
```bash
name: Container Vulnerability Scan using Trivy

on:
  push:
    branches:
      - main  # Trigger action when changes are pushed to the main branch

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4  # Checkout the repository code

      - name: Set up Docker
        uses: docker/setup-buildx-action@v2  # Set up Docker Buildx (for multi-platform support)

      - name: Build the Docker image
        run: |
         docker build -t vulnerable-python-app -f vulnerable-python-app/Dockerfile vulnerable-python-app/  # Build the Docker image from the Dockerfile inside the vulnerable-python-app folder
      - name: Install Trivy
        run: |
          sudo apt-get update
          sudo apt-get install -y wget
          wget https://github.com/aquasecurity/trivy/releases/download/v0.41.0/trivy_0.41.0_Linux-64bit.deb
          sudo dpkg -i trivy_0.41.0_Linux-64bit.deb
      - name: Scan for vulnerabilities using Trivy
        uses: aquasecurity/trivy-action@master  # Trivy GitHub Action for scanning Docker images
        with:
          image-ref: 'vulnerable-python-app'
          format: 'json'
          output: 'trivy-report.json'
          severity: 'CRITICAL,HIGH'

      - name: Install SSH Client
        run: |
          sudo apt-get update
          sudo apt-get install -y openssh-client
      - name: Configure SSH for EC2
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.AZURE_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 400 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.AZURE_VM_IP }} >> ~/.ssh/known_hosts
      - name: Push report to EC2 instance
        run: |
          scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa \
          trivy-report.json azureuser@${{ secrets.AZURE_VM_IP }}:/home/azureuser/reports/
      - name: Send custom Slack Notification with Build Status and Report
        if: always()  # Send notification regardless of success or failure
        run: |
          curl -X POST -H 'Content-type: application/json' --data '{
            "text": "Build Status Update",
            "attachments": [
              {
                "color": "${{ job.status == 'success' && '#36a64f' || '#ff0000' }}",
                "fields": [
                  {
                    "title": "Job Status",
                    "value": "${{ job.status }}",
                    "short": true
                  },
                  {
                    "title": "Report Location",
                    "value": "The report has been pushed to EC2 at `/home/azureuser/reports/trivy-report.json`.",
                    "short": false
                  }
                ]
              }
            ]
          }' ${{ secrets.SLACK_WEBHOOK_URL }}
```

Explanation of Steps:

```bash
Checkout Code:
The `actions/checkout` action is used to check out the latest version of the repository's code to the GitHub runner, making it available for subsequent steps in the pipeline.

Set up Docker:
The `docker/setup-buildx-action` action is used to set up Docker Buildx, enabling multi-platform support. Buildx allows building images for different architectures and is required for modern Docker workflows.

Build Docker Image:
This step uses the `docker build` command to build a Docker image from the `vulnerable-python-app/Dockerfile` file. The image is tagged with the name `vulnerable-python-app`. This image will later be scanned for vulnerabilities.

Install Trivy:
Trivy, a security scanner for container images, is installed by downloading its `.deb` package from the official GitHub release page. The package is then installed using `dpkg`. Trivy scans the Docker images for known vulnerabilities.

Scan Image for Vulnerabilities:
In this step, the `aquasecurity/trivy-action` is used to scan the Docker image (`vulnerable-python-app`) for vulnerabilities. The scan is conducted with a severity filter set to `CRITICAL` and `HIGH` vulnerabilities. The scan output is in `JSON` format and saved as `trivy-report.json`.

Install SSH Client:
The SSH client is installed on the GitHub runner to allow secure file transfer using SCP. This is necessary to push the vulnerability report to an EC2 instance.

Configure SSH for EC2:
In this step, the SSH private key stored in the GitHub secrets (`${{ secrets.AZURE_SSH_KEY }}`) is used to configure the SSH client on the GitHub runner. The SSH key is saved as `~/.ssh/id_rsa` and permissions are set to `400` for security. The EC2 instance’s IP address (`${{ secrets.AZURE_VM_IP }}`) is added to the list of known hosts to prevent SSH warnings about unknown hosts during the file transfer.

Push Report to EC2:
The `scp` command is used to securely copy the `trivy-report.json` file to the EC2 instance at the path `/home/azureuser/reports/`. This ensures that the vulnerability report is uploaded to the EC2 instance for further analysis.

Send Slack Notification:
The notification is sent to Slack using a `curl` command that posts a JSON payload to the Slack webhook URL stored in GitHub secrets (`${{ secrets.SLACK_WEBHOOK_URL }}`). The message includes the build status (success or failure), and the location of the uploaded vulnerability report on the EC2 instance (`/home/azureuser/reports/trivy-report.json`). The color of the message is dynamically set based on the build status—green for success and red for failure.

```

## 2. Create a Slack App

```bash

Step 1: Create a Slack Channel
Open your Slack workspace.

In the left sidebar, click the "+" icon next to Channels.

Select Create a channel.

Give the channel a name (e.g., #vulnerability-reports).

Choose whether the channel is public or private.

Click Create.

Step 2: Create a Slack App
Go to Slack API and click Create New App.

Choose From scratch.

Give the app a name (e.g., GitHub Actions Notifier).

Select your Slack workspace.

Click Create App.

Step 3: Configure Permissions
In the Slack App settings, navigate to OAuth & Permissions.

Under OAuth Scopes, add the following:

chat:write: Allows the bot to send messages to channels.

chat:write.public: Allows the bot to send messages to public channels.

files:write: Allows the bot to upload files.

incoming-webhook: If you want to use an incoming webhook (for sending messages to Slack).

Save changes.

Step 4: Install the App to Your Workspace
Navigate to Install App in the app settings.

Click Install App.

Copy the Bot User OAuth Token for later use. This will be used in the GitHub Actions workflow to send Slack messages.
```
## 3. Secrets Configuration in GitHub

Ensure you set the following GitHub secrets to store sensitive data securely:

```bash

SLACK_BOT_TOKEN: The OAuth token you copied when installing the Slack app.

AZURE_SSH_KEY: The private SSH key to access your EC2 instance securely.

AZURE_VM_IP: The public IP address of your Azure VM (EC2 instance).
```

How to Add Secrets:
```bash
Go to your GitHub repository.

Navigate to Settings > Secrets > Actions.

Click New repository secret.

Add each of the required secrets (e.g., SLACK_BOT_TOKEN, AZURE_SSH_KEY, AZURE_VM_IP) with the respective values.
```
## 4. Run the Workflow

Once the GitHub Actions workflow is configured, the process will run automatically every time code is pushed to the main branch. The pipeline will:

```bash
Build the Docker image.

Run the Trivy vulnerability scan.

Push the report to the EC2 instance.

Send a Slack notification with the build status and report location.
```

## 5. Slack Notification Format
The notification sent to Slack will look like this:

Example Slack Message:

```bash
Build Status Update

Job Status: success

Report Location: The report has been pushed to EC2 at `/home/azureuser/reports/trivy-report.json`.
```
