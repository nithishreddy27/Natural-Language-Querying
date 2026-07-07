# Dockerfile for NLP Query Understanding System

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY data/ ./data/
COPY examples/ ./examples/
COPY tests/ ./tests/

# Create directories for models and cache
RUN mkdir -p models .cache

# Set environment variables
ENV PYTHONPATH=/app
ENV TRANSFORMERS_CACHE=/app/.cache

# Expose port for API (if using FastAPI)
EXPOSE 8000

# Default command
CMD ["python", "examples/demo.py"]
