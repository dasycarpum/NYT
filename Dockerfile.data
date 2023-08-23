# Use a parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project into the container
COPY . .

# Set the main script as the container's entrypoint
CMD ["python", "src/data_main/main.py"]
