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

      - name: Send Slack Notification with Build Status and Report
        if: always()  # Send notification regardless of success or failure
        uses: kpritam/slack-job-status-action@v1
        with:
          job-status: ${{ job.status }}
          slack-bot-token: ${{ secrets.SLACK_BOT_TOKEN }}
          channel: '#vulnerability-reports'  # Replace with your actual Slack channel name or ID
          message-format: |
            {
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
            }
```

Explanation of Steps:
```bash
Checkout Code:

The actions/checkout action checks out the latest code from the repository to the GitHub runner.

Set up Docker:

The docker/setup-buildx-action sets up Docker Buildx to enable multi-platform support.

Build Docker Image:

This step builds the Docker image from the vulnerable-python-app/Dockerfile file and tags it as vulnerable-python-app.

Install Trivy:

Trivy is installed by downloading the .deb package and installing it via dpkg. Trivy is a security scanner for vulnerabilities in container images.

Scan Image for Vulnerabilities:

The Trivy scan is run on the built Docker image, and the report is generated in json format, saved to trivy-report.json. The scan focuses on vulnerabilities with a severity of CRITICAL or HIGH.

Install SSH Client:

Installs the SSH client on the runner so that it can use scp to transfer the report to the EC2 instance.

Configure SSH for EC2:

Sets up SSH by placing the SSH private key (${{ secrets.AZURE_SSH_KEY }}) and configuring known hosts (${{ secrets.AZURE_VM_IP }}) to enable secure file transfers.

Push Report to EC2:

Uses scp to securely copy the trivy-report.json to an EC2 instance at the specified path (/home/azureuser/reports/).

Send Slack Notification:

Sends a Slack notification using the kpritam/slack-job-status-action GitHub Action. The message includes the build status (success or failure) and the location of the report on the EC2 instance.

The report file is attached to the message.
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
