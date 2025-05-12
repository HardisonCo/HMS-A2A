#!/bin/bash
# Agency Implementation System Deployment Script

set -e

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${DEPLOYMENT_DIR}/config/deployment.env"
LOG_FILE="${DEPLOYMENT_DIR}/deployment.log"

# Function to log messages
log() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo "[$timestamp] $1"
  echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Load environment variables if file exists
if [ -f "$ENV_FILE" ]; then
  log "Loading environment variables from $ENV_FILE"
  source "$ENV_FILE"
else
  log "Warning: Environment file not found at $ENV_FILE"
fi

# Verify Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
  log "Error: Docker is not installed"
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  log "Error: Docker Compose is not installed"
  exit 1
fi

# Pull latest code if in a git repository
if [ -d "${DEPLOYMENT_DIR}/../.git" ]; then
  log "Pulling latest code from git repository"
  cd "${DEPLOYMENT_DIR}/.."
  git pull
  cd "$DEPLOYMENT_DIR"
else
  log "Not a git repository, skipping code update"
fi

# Create required directories
log "Creating required directories"
mkdir -p "${DEPLOYMENT_DIR}/logs"

# Check if containers are already running
if docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" ps | grep -q Up; then
  log "Stopping existing containers"
  docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" down
fi

# Pull latest images
log "Pulling latest Docker images"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" pull

# Start the services
log "Starting services"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" up -d

# Wait for services to be healthy
log "Waiting for services to be healthy"
sleep 10

# Verify deployment
log "Verifying deployment"
if docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" ps | grep -q Exit; then
  log "Error: Some containers failed to start"
  docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" ps
  docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" logs
  exit 1
else
  log "All containers started successfully"
fi

# Run database migrations if needed
log "Running database migrations"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec foundation-api npm run migrate

# Post-deployment tasks
log "Running post-deployment tasks"
"${DEPLOYMENT_DIR}/scripts/post-deploy.sh"

log "Deployment completed successfully"