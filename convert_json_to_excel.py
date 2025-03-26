import json
import pandas as pd

# Load the Trivy JSON report
with open('trivy_report.json', 'r') as json_file:
    data = json.load(json_file)

# Prepare the data for conversion (assuming the JSON has 'Vulnerabilities' key)
vulnerabilities = data.get('Vulnerabilities', [])

# Convert to DataFrame
df = pd.DataFrame(vulnerabilities)

# Save the DataFrame to an Excel file
df.to_excel('trivy_report.xlsx', index=False)

print("Excel report saved as trivy_report.xlsx")




