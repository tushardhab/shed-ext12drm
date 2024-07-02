FROM python:3.9.7-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    pv \
    jq \
    python3-dev \
    ffmpeg \
    mediainfo \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy your application files
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# # Download and set up N_m3u8DL-RE
# RUN wget https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v3.3.0/N_m3u8DL-RE_Beta_linux-x64.tar.gz \
#     && tar -xzf N_m3u8DL-RE_Beta_linux-x64.tar.gz \
#     && chmod +x N_m3u8DL-RE \
#     && rm N_m3u8DL-RE_Beta_linux-x64.tar.gz

# Download and set up mp4decrypt (Bento4)
RUN wget https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-639.x86_64-unknown-linux.zip \
    && unzip Bento4-SDK-1-6-0-639.x86_64-unknown-linux.zip \
    && mv Bento4-SDK-1-6-0-639.x86_64-unknown-linux/bin/mp4decrypt . \
    && chmod +x mp4decrypt \
    && rm -rf Bento4-SDK-1-6-0-639.x86_64-unknown-linux.zip Bento4-SDK-1-6-0-639.x86_64-unknown-linux

# Set the PATH to include the current directory
ENV PATH="/app:${PATH}"

# Run your application
CMD ["python3", "main.py"]
