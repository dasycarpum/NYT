# Use a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements.txt file into the container at /usr/src/app
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the useful file into the container at /usr/src/app
COPY config.py ./
COPY src/ ./src/

# # Make port 8050 available to the outside world (Dash default port)
EXPOSE 8050

# Set the main script as the container's entrypoint
CMD ["python", "./src/machine_learning/main.py"]
