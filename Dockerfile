# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (includes all agents in backend/agents/)
COPY backend /app/backend

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Change to backend directory
WORKDIR /app/backend

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Health check (uses PORT env var or defaults to 8000)
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\", \"8000\")}/health').read()"

# Start command (uses shell to expand $PORT)
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
