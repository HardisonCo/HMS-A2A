#!/bin/bash
# Post-deployment script for Agency Implementation System

set -e

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${DEPLOYMENT_DIR}/deployment.log"

# Function to log messages
log() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo "[$timestamp] $1"
  echo "[$timestamp] $1" >> "$LOG_FILE"
}

log "Starting post-deployment tasks"

# Verify foundation API is responsive
log "Verifying foundation API"
timeout 30s bash -c 'until curl -s http://localhost:8000/health | grep -q "ok"; do sleep 2; done' || {
  log "Error: Foundation API is not responding"
  exit 1
}

# Verify federation gateway is responsive
log "Verifying federation gateway"
timeout 30s bash -c 'until curl -s http://localhost:8010/health | grep -q "ok"; do sleep 2; done' || {
  log "Error: Federation gateway is not responding"
  exit 1
}

# Verify unified dashboard is responsive
log "Verifying unified dashboard"
timeout 30s bash -c 'until curl -s http://localhost:8080/health | grep -q "ok"; do sleep 2; done' || {
  log "Error: Unified dashboard is not responding"
  exit 1
}

# Set up federation relationships
log "Setting up federation relationships"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec federation-gateway /app/scripts/setup-federation.sh

# Initialize notification channels
log "Initializing notification channels"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec notification-service /app/scripts/initialize-channels.sh

# Run integration tests
log "Running integration tests"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec foundation-api npm run test:integration

# Apply security hardening
log "Applying security hardening"
"${DEPLOYMENT_DIR}/scripts/security-hardening.sh"

# Backup configurations
log "Backing up configurations"
mkdir -p "${DEPLOYMENT_DIR}/backups/$(date +%Y%m%d)"
cp -r "${DEPLOYMENT_DIR}/config" "${DEPLOYMENT_DIR}/backups/$(date +%Y%m%d)/"

# Cleanup old backups (keep last 7 days)
find "${DEPLOYMENT_DIR}/backups/" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true

log "Post-deployment tasks completed successfully"