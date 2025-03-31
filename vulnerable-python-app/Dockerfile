# Dockerfile for vulnerable-python-app
FROM python:3.14-rc-bookworm

# Set up minimal environment
WORKDIR /app

# Install only runtime dependencies (no build tools)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove unnecessary packages that might contain vulnerabilities
RUN apt-get update && apt-get remove -y libaom3 libopenexr-3-1-30 zlib1g-dev && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . .

# Run as non-root
USER 1001

EXPOSE 7002
CMD ["python", "app.py"]
