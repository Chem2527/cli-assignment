# Setup Documentation for Prometheus, Trivy JSON Exporter and Grafana Dashboard


## Prerequisites

```bash
A Linux-based machine (Ubuntu in our case).

Proper network configurations, such as allowing the necessary ports for Grafana, Prometheus, and the Trivy JSON Exporter.

Administrative access to the machine (sudo privileges).
```

## Step 1: Install Prometheus

### Download and Extract Prometheus:

```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz
tar -xvzf prometheus-2.46.0.linux-amd64.tar.gz
cd prometheus-2.46.0.linux-amd64
```
### Move Prometheus binaries to /usr/local/bin/:

```bash
sudo mv prometheus /usr/local/bin/
sudo mv promtool /usr/local/bin/
```
### Create necessary directories for Prometheus:

```bash
sudo mkdir -p /etc/prometheus /var/lib/prometheus
Move the prometheus.yml configuration file to the /etc/prometheus/ directory:
```
```bash
sudo mv prometheus.yml /etc/prometheus/
```
### Configure Prometheus to scrape the Trivy JSON exporter: Edit the prometheus.yml file:

```bash
sudo vi /etc/prometheus/prometheus.yml
```
#### Add the following scrape configuration:

```bash

global:
  scrape_interval: 2m # Scrape every 2 minutes
  evaluation_interval: 2m # Evaluate rules every 2 minutes

scrape_configs:
  - job_name: 'trivy_json_exporter'
    static_configs:
      - targets: ['localhost:8001'] # Exporter port
```
### Create a systemd service for Prometheus: To run Prometheus as a service, create a prometheus.service file:

```bash
sudo vi /etc/systemd/system/prometheus.service
```
#### Add the following content:

```bash
[Unit]
Description=Prometheus Service
After=network.target

[Service]
User=root
ExecStart=/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/var/lib/prometheus/

[Install]
WantedBy=multi-user.target
```
### Reload systemd, start Prometheus, and enable it to start on boot:

```bash
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus
```
### Check Prometheus status:

```bash
sudo systemctl status prometheus
```
## Step 2: Install and Configure Trivy JSON Exporter

### Create the directory for the Trivy JSON Exporter:

```bash
mkdir ~/trivy-json-exporter
cd ~/trivy-json-exporter
```
### Create the Python script (trivy_json_exporter.py): This script reads the trivy-report.json file, extracts vulnerability data, and exposes it in Prometheus format.

```bash
vi trivy_json_exporter.py
```
### Paste the following Python code into the file:

```bash
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, CollectorRegistry
import json
from jsonpath_ng.ext import parse

app = Flask(__name__)

registry = CollectorRegistry()

critical_vulns = Gauge('trivy_critical_vulnerabilities', 'Number of critical vulnerabilities', registry=registry)
high_vulns = Gauge('trivy_high_vulnerabilities', 'Number of high vulnerabilities', registry=registry)
medium_vulns = Gauge('trivy_medium_vulnerabilities', 'Number of medium vulnerabilities', registry=registry)
low_vulns = Gauge('trivy_low_vulnerabilities', 'Number of low vulnerabilities', registry=registry)

JSON_FILE_PATH = '/home/azureuser/reports/trivy-report.json'

def update_metrics():
    try:
        with open(JSON_FILE_PATH, 'r') as f:
            data = json.load(f)

        # JSONPath expressions to extract vulnerability counts
        critical_expression = parse('$.Results[*].Vulnerabilities[?(@.Severity=="CRITICAL")]')
        high_expression = parse('$.Results[*].Vulnerabilities[?(@.Severity=="HIGH")]')
        medium_expression = parse('$.Results[*].Vulnerabilities[?(@.Severity=="MEDIUM")]')
        low_expression = parse('$.Results[*].Vulnerabilities[?(@.Severity=="LOW")]')

        # Evaluate JSONPath expressions and count results
        critical_count = len([match.value for match in critical_expression.find(data)])
        high_count = len([match.value for match in high_expression.find(data)])
        medium_count = len([match.value for match in medium_expression.find(data)])
        low_count = len([match.value for match in low_expression.find(data)])

        # Set Prometheus metrics
        critical_vulns.set(critical_count)
        high_vulns.set(high_count)
        medium_vulns.set(medium_count)
        low_vulns.set(low_count)

    except Exception as e:
        print(f"Error reading JSON file: {e}")

@app.route('/metrics')
def metrics():
    update_metrics()
    return Response(generate_latest(registry), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
```

### Install required Python libraries: Install the dependencies:

```bash
sudo apt update
sudo apt install python3-prometheus-client python3-jsonpath-ng python3-flask python3-gunicorn
```
### Create a systemd service for Trivy JSON Exporter: To run the exporter as a service, create a trivy-json-exporter.service file:

```bash
sudo vi /etc/systemd/system/trivy-json-exporter.service
```

#### Add the following content:

```bash
[Unit]
Description=Trivy JSON Exporter Service
After=network.target

[Service]
User=root
ExecStart=/usr/bin/python3 /home/azureuser/trivy-json-exporter/trivy_json_exporter.py

[Install]
WantedBy=multi-user.target
```
### Reload systemd, start the service, and enable it to start on boot:

```bash
sudo systemctl daemon-reload
sudo systemctl start trivy-json-exporter.service
sudo systemctl enable trivy-json-exporter.service
```
### Check Trivy JSON Exporter status:
```bash
sudo systemctl status trivy-json-exporter.service
```

## Step 3: Install Grafana

Download and Install Grafana:

```bash
wget https://dl.grafana.com/oss/release/grafana_9.5.3_amd64.deb
sudo dpkg -i grafana_9.5.3_amd64.deb
```
### Start and Enable Grafana:

```bash
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```
### Allow Grafana Port (3000) through the firewall:

```bash
sudo ufw allow 3000/tcp
sudo ufw reload
```

## Step 4: Configure Grafana to Use Prometheus as a Data Source
```bash
Access Grafana UI: Open a web browser and navigate to http://<your_vm_ip>:3000/ (in this case, http://52.175.212.104:3000/).
```
```bash
Login to Grafana: The default login is admin for both the username and password. You will be prompted to change the password upon first login.


Add Prometheus as a Data Source:

Click on the gear icon (⚙️) in the left sidebar to open the Configuration section.

Choose Data Sources and click Add data source.

Select Prometheus from the list of available data sources.

Set the URL to http://localhost:9090 (assuming Prometheus is running on the same machine).

Click Save & Test to ensure the connection works.

Create a Dashboard in Grafana:

Click on the + icon on the left sidebar and select Dashboard.

Click Add Query and choose Prometheus as the data source.

Enter queries for the different vulnerability metrics:

trivy_critical_vulnerabilities

trivy_high_vulnerabilities

trivy_medium_vulnerabilities

trivy_low_vulnerabilities
```

## Step 5: Accessing and Viewing the Dashboard
Once everything is set up, you can access your Grafana dashboard at http://<your_vm_ip>:3000/ and view the metrics for critical, high, medium, and low vulnerabilities.
