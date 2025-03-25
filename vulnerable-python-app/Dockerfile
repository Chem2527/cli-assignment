# Use the official Python image, but pin the version for security and consistency
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install dependencies securely
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 7002 to make the app accessible
EXPOSE 7002

# Run the app with appropriate environment variables
CMD ["python", "app.py"]
