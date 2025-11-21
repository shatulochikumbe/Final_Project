# Multi-stage build for AI application
FROM nvidia/cuda:12.1-runtime-ubuntu22.04 as builder

WORKDIR /app

# Install system dependencies for AI/ML
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-venv \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.11 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash zanuri
WORKDIR /home/zanuri

# Copy virtual environment
COPY --from=builder /app/venv /home/zanuri/venv
COPY --chown=zanuri:zanuri . .

USER zanuri

# Set environment variables
ENV PATH="/home/zanuri/venv/bin:$PATH"
ENV PYTHONPATH="/home/zanuri"
ENV CUDA_VISIBLE_DEVICES=0

# Create necessary directories
RUN mkdir -p /home/zanuri/models /home/zanuri/data /home/zanuri/logs

# Expose port
EXPOSE 8000

# Health check for AI service
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120"]