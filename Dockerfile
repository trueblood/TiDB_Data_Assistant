# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variables
# Set environment variables
ENV TIDB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com
ENV TIDB_PORT=4000
ENV TIDB_USER=
ENV TIDB_PASSWORD=
ENV TIDB_DB_NAME=
ENV CA_PATH=
ENV UNIVERSAL_SENTENCE_ENCODER_V4_API=
ENV X_API_KEY=]



# Run app.py when the container launches
CMD ["python", "app.py"]
