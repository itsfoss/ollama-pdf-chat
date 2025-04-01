# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy source code and setup files
COPY src ./src
COPY setup.py .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p _temp _vectors

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS="ignore::DeprecationWarning,ignore::UserWarning"

# Labels
LABEL maintainer="Abhishek Kumar <abhishkkumar@gmail.com>"
LABEL version="1.0.0"
LABEL description="Local RAG System with Ollama integration"

# Expose Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "src/streamlit_app.py", "--server.address", "0.0.0.0"]
