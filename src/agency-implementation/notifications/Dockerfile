FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create volume for configuration
VOLUME /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH=/app/config/notification_config.json

# Run the notification system
CMD ["python", "main.py", "--config", "${CONFIG_PATH}"]