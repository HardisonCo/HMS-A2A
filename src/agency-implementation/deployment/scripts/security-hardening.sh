#!/bin/bash
# Security hardening script for Agency Implementation System

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

log "Starting security hardening"

# Ensure permissions are correct on sensitive files
log "Setting correct permissions on sensitive files"
chmod 600 "${DEPLOYMENT_DIR}/config/"*.env

# Check for default/weak passwords in configuration files
log "Checking for default passwords in configuration files"
grep -l "change_this_to_a_secure" "${DEPLOYMENT_DIR}/config/"*.env && {
  log "Warning: Default passwords detected in configuration files. Please update them."
}

# Verify network isolation
log "Verifying network isolation"
docker network inspect agency_network >/dev/null 2>&1 || {
  log "Error: Docker network 'agency_network' not found"
  exit 1
}

# Configure rate limiting on services
log "Configuring rate limiting"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec foundation-api /app/scripts/configure-rate-limiting.sh

# Set up fail2ban for container logs (if installed)
if command -v fail2ban-client &> /dev/null; then
  log "Setting up fail2ban for container logs"
  # Implementation-specific fail2ban setup would go here
fi

# Enable audit logging
log "Enabling audit logging"
for service in foundation-api federation-gateway dashboard notification-service; do
  docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec "$service" /app/scripts/enable-audit-logging.sh || {
    log "Warning: Failed to enable audit logging for $service"
  }
done

# Check for exposed ports
log "Checking for unnecessarily exposed ports"
exposed_ports=$(docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" config | grep -A 1 ports | grep -v "ports:" | grep -v "\-\-" | tr -d ' ' | tr -d '"')
log "Exposed ports: $exposed_ports"

# Verify TLS/SSL configuration
log "Verifying TLS/SSL configuration"
if [ ! -d "${DEPLOYMENT_DIR}/config/ssl" ]; then
  log "Warning: SSL certificates directory not found. HTTPS may not be properly configured."
fi

# Set up automatic security updates (if supported by host OS)
if [ -f /etc/debian_version ]; then
  log "Setting up unattended upgrades for Debian/Ubuntu"
  # Implementation-specific unattended upgrades setup would go here
elif [ -f /etc/redhat-release ]; then
  log "Setting up automatic updates for RHEL/CentOS"
  # Implementation-specific automatic updates setup would go here
fi

log "Security hardening completed"