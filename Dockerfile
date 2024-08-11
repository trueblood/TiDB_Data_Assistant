# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variables
ENV TIDB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com \
    TIDB_PORT=4000 \
    TIDB_USER=EcFsmzHzn16sz32.root \
    TIDB_PASSWORD=4UTXzVBKxU10w2Z1 \
    TIDB_DB_NAME=embracepath \
    CA_PATH= \
    UNIVERSAL_SENTENCE_ENCODER_V4_API=53533f4f-3bb5-4b36-bc95-214f9414b8cc \
    X_API_KEY=b233fa3e-10d3-4616-a016-9f70ab96e1b8

# Run app.py when the container launches
CMD ["python", "app.py"]
