FROM python:3.9.7-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Update package list and install necessary packages
RUN apt-get -qq update && \
    apt-get -qq install -y git wget pv jq python3-dev ffmpeg mediainfo && \
    apt-get -qq clean

# Copy all files from the current directory to the working directory in the container
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Specify the command to run your application
CMD ["python3", "main.py"]
