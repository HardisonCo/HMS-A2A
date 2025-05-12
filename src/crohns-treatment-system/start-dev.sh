#!/bin/bash
# Development startup script for Crohn's Disease Treatment System

# Print ASCII banner
cat << "EOF"
 ____           _           _       ____                 _                    
/ ___|_ __ ___ | |__  _ __ ( )___  |  _ \  ___ ___ _ __ | | ___  _   _       
| |   | '__/ _ \| '_ \| '_ \|// __| | | | |/ __/ _ \ '_ \| |/ _ \| | | |      
| |___| | | (_) | | | | | | | \__ \ | |_| | (_|  __/ |_) | | (_) | |_| |_ _ _ 
 \____|_|  \___/|_| |_|_| |_| |___/ |____/ \___\___| .__/|_|\___/ \__, (_|_|_)
                                                   |_|            |___/       
 _____                _                      _      ____            _                 
|_   _| __ ___  __ _| |_ _ __ ___   ___ _ __ | |_   / ___| _   _ ___| |_ ___ _ __ ___ 
  | || '__/ _ \/ _` | __| '_ ` _ \ / _ \ '_ \| __| | |  _ | | | / __| __/ _ \ '_ ` _ \
  | || | |  __/ (_| | |_| | | | | |  __/ | | | |_  | |_| || |_| \__ \ ||  __/ | | | | |
  |_||_|  \___|\__,_|\__|_| |_| |_|\___|_| |_|\__|  \____| \__, |___/\__\___|_| |_| |_|
                                                           |___/                      
EOF

echo "Starting Crohn's Disease Treatment System in development mode..."
echo 

# Check for docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is required but not found."
    echo "Please install docker-compose and try again."
    exit 1
fi

# Create local environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating development .env file..."
    cat > .env << EOL
# Development environment variables
ENV=development
LOG_LEVEL=debug
PORT=8000
GENETIC_ENGINE_MOCK=true
EOL
    echo "Created .env file with default development settings."
fi

# Check if we should use mock genetic engine
if grep -q "GENETIC_ENGINE_MOCK=true" .env; then
    echo "Using mock genetic engine (no Rust compilation required)."
else
    echo "Building Rust genetic engine..."
    cd src/coordination/genetic-engine
    cargo build
    cd ../../..
fi

echo "Starting services using docker-compose..."
docker-compose -f infrastructure/docker-compose.yml up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Run HMS-A2A agent system
echo "Starting HMS-A2A agent system..."
cd src/coordination/a2a-integration
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
A2A_PID=$!
cd ../../..

# Display startup status
echo 
echo "------------------------------------------------------"
echo "Crohn's Disease Treatment System started successfully!"
echo "------------------------------------------------------"
echo 
echo "Services:"
echo "- HMS-A2A API: http://localhost:8001"
echo "- Genetic Engine: Running as $(grep -q "GENETIC_ENGINE_MOCK=true" .env && echo "mock" || echo "native")"
echo 
echo "To stop the system, press Ctrl+C"
echo 

# Handle shutdown
function cleanup {
    echo "Shutting down..."
    kill $A2A_PID
    docker-compose -f infrastructure/docker-compose.yml down
    echo "System stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
wait $A2A_PID