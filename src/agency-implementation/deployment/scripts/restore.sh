#!/bin/bash
# Database and configuration restore script for Agency Implementation System

set -e

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${DEPLOYMENT_DIR}/backups"
LOG_FILE="${DEPLOYMENT_DIR}/restore.log"

# Function to log messages
log() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo "[$timestamp] $1"
  echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Check if backup file was provided
if [ $# -lt 1 ]; then
  log "Error: No backup file specified"
  echo "Usage: $0 <backup_file> [--force]"
  echo "Example: $0 backups/backup_20230101_120000.tar.gz"
  exit 1
fi

BACKUP_FILE="$1"
FORCE_RESTORE=false

# Check for force flag
if [ $# -gt 1 ] && [ "$2" = "--force" ]; then
  FORCE_RESTORE=true
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
  log "Error: Backup file not found: $BACKUP_FILE"
  exit 1
fi

# Verify backup integrity
log "Verifying backup integrity"
if ! tar -tzf "$BACKUP_FILE" >/dev/null 2>&1; then
  log "Error: Backup archive is corrupted"
  exit 1
fi

# Confirm restore operation
if [ "$FORCE_RESTORE" = false ]; then
  read -p "Warning: This will overwrite the current database and configuration. Continue? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Restore operation cancelled by user"
    exit 1
  fi
fi

# Prepare temporary directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Extract backup archive
log "Extracting backup archive"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Get the backup date directory
BACKUP_DATE_DIR=$(find "$TEMP_DIR" -type d | grep -v "^$TEMP_DIR$" | head -1)

# Stop the services
log "Stopping services"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" down

# Restore configuration files
log "Restoring configuration files"
cp -r "${BACKUP_DATE_DIR}/config/"* "${DEPLOYMENT_DIR}/config/"

# Start database and Redis services only
log "Starting database and Redis services"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" up -d postgres redis

# Wait for database to be ready
log "Waiting for database to be ready"
sleep 10

# Restore database
log "Restoring PostgreSQL database"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec -T postgres pg_restore \
  -U agency_admin \
  -d agency_system \
  -c --if-exists < "${BACKUP_DATE_DIR}/agency_system.dump"

# Restore Redis data
log "Restoring Redis data"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" stop redis
docker cp "${BACKUP_DATE_DIR}/redis.rdb" $(docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" ps -q redis):/data/dump.rdb
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" start redis

# Start all services
log "Starting all services"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" up -d

# Run post-deployment tasks
log "Running post-deployment tasks"
"${DEPLOYMENT_DIR}/scripts/post-deploy.sh"

log "Restore completed successfully"