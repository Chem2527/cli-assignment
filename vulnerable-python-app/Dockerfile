# Use specific Debian Bookworm Python image with no extra packages
FROM python:latest-slim-bookworm

# Set up minimal environment
WORKDIR /app

# Install only runtime dependencies (no build tools)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && \
    # Update apt sources and install necessary runtime libraries if required
    apt-get update && apt-get install -y \
        libaom3 libopenexr-3-1-30 zlib1g-dev || true && \
    # Remove unnecessary packages that might contain vulnerabilities (if they were installed)
    apt-get remove -y libaom3 libopenexr-3-1-30 zlib1g-dev || true && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . .

# Run as non-root
USER 1001

EXPOSE 7002
CMD ["python", "app.py"]
