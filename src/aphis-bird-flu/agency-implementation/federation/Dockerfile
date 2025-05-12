FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY agency-implementation/federation/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agency-implementation/foundation /app/agency-implementation/foundation
COPY agency-implementation/cdc /app/agency-implementation/cdc
COPY agency-implementation/epa /app/agency-implementation/epa
COPY agency-implementation/fema /app/agency-implementation/fema
COPY agency-implementation/federation /app/agency-implementation/federation

# Set working directory to federation
WORKDIR /app/agency-implementation/federation

# Environment variables with defaults
ENV FEDERATION_HUB_HOST=0.0.0.0
ENV FEDERATION_HUB_PORT=8000
ENV CDC_API_BASE_URL=http://localhost:8001/api/v1/cdc
ENV EPA_API_BASE_URL=http://localhost:8002/api/v1/epa
ENV FEMA_API_BASE_URL=http://localhost:8003/api/v1/fema

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]