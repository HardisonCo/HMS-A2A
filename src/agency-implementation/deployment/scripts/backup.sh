#!/bin/bash
# Database and configuration backup script for Agency Implementation System

set -e

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${DEPLOYMENT_DIR}/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${DEPLOYMENT_DIR}/backup.log"

# Function to log messages
log() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo "[$timestamp] $1"
  echo "[$timestamp] $1" >> "$LOG_FILE"
}

log "Starting backup process"

# Create backup directory
mkdir -p "${BACKUP_DIR}/${DATE}"

# Backup database
log "Backing up PostgreSQL database"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec -T postgres pg_dump \
  -U agency_admin \
  -d agency_system \
  -F c > "${BACKUP_DIR}/${DATE}/agency_system.dump"

# Backup Redis data
log "Backing up Redis data"
docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec -T redis redis-cli \
  -a "${REDIS_PASSWORD:-redis_secure_password}" \
  --rdb "${BACKUP_DIR}/${DATE}/redis.rdb"

# Backup configuration files
log "Backing up configuration files"
cp -r "${DEPLOYMENT_DIR}/config" "${BACKUP_DIR}/${DATE}/config"

# Create archive of the backup
log "Creating archive of the backup"
tar -czf "${BACKUP_DIR}/backup_${DATE}.tar.gz" -C "${BACKUP_DIR}" "${DATE}"

# Clean up temporary files
rm -rf "${BACKUP_DIR}/${DATE}"

# Remove backups older than 30 days
log "Removing backups older than 30 days"
find "${BACKUP_DIR}" -name "backup_*.tar.gz" -type f -mtime +30 -delete

# Verify backup integrity
log "Verifying backup integrity"
if tar -tzf "${BACKUP_DIR}/backup_${DATE}.tar.gz" >/dev/null 2>&1; then
  log "Backup integrity verified"
else
  log "Error: Backup archive is corrupted"
  exit 1
fi

# Log backup size
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/backup_${DATE}.tar.gz" | cut -f1)
log "Backup completed successfully. Size: ${BACKUP_SIZE}"

# Optional: Copy backup to remote storage
if [ -n "${REMOTE_BACKUP_ENABLED}" ] && [ "${REMOTE_BACKUP_ENABLED}" = "true" ]; then
  log "Copying backup to remote storage"
  # Implementation-specific remote backup command would go here
  # Example: aws s3 cp "${BACKUP_DIR}/backup_${DATE}.tar.gz" "s3://agency-system-backups/"
fi