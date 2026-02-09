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

# Copy application code
COPY backend /app/backend
COPY coordination_agent /app/coordination_agent
COPY engineering_agent /app/engineering_agent
COPY finance_agent /app/finance_agent
COPY fire_agent /app/fire_agent
COPY health_agent /app/health_agent
COPY sanitation_agent /app/sanitation_agent
COPY water_agent /app/water_agent

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Change to backend directory
WORKDIR /app/backend

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Start command
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
