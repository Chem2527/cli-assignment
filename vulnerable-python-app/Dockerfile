# Use the official Python image from the Docker Hub
# This sets the base image to Python 3.9 slim version, which is a lightweight version of Python
FROM python:3.9-slim

# Set the working directory in the container
# This creates a directory named /app in the container and sets it as the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
# This copies the requirements.txt file from your local machine to the /app directory in the container
COPY requirements.txt .

# Install the dependencies
# This installs the Python dependencies listed in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This copies all the remaining application files from your local machine to the /app directory in the container
COPY . .

# Expose port 7002 to make it accessible from outside the container
EXPOSE 7002

# Specify the command to run the application
# This sets the default command to run the application using Python
CMD ["python", "app.py"]