FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install TTS with all its dependencies (including PyTorch 2.6)
RUN pip install TTS
RUN pip install TTS[ja]

# Set working directory
WORKDIR /app

# Copy all necessary files
COPY tts_helper.py /app/
COPY patched_tts.py /app/
COPY pytorch_patch.py /app/
COPY run_tts.py /app/

# Create a volume to share files
VOLUME /app/data

# Create directories with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Create a directory for auto-import
RUN mkdir -p /app/patches

# Create an __init__.py file that applies the patch
RUN echo 'import os; import sys; exec(open("/app/pytorch_patch.py").read())' > /app/patches/__init__.py

# Set PYTHONPATH to load the patches directory automatically
ENV PYTHONPATH=/app/patches

# Make the script executable
RUN chmod +x /app/patched_tts.py
RUN chmod +x /app/run_tts.py

# Keep container running
CMD ["tail", "-f", "/dev/null"] 