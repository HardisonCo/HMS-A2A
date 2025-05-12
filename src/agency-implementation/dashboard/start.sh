#!/bin/bash

# Start the Bird Flu Interagency Dashboard

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set Federation Hub URL
export FEDERATION_API_URL=${FEDERATION_API_URL:-http://localhost:8000/api/v1/federation}

# Start the application
echo "Starting dashboard at http://localhost:8050..."
python app.py