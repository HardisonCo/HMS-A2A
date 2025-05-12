#!/bin/bash
# Monitoring script for Agency Implementation System

set -e

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="${DEPLOYMENT_DIR}/monitor.log"

# Function to log messages
log() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo "[$timestamp] $1"
  echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Function to check service health
check_service_health() {
  local service=$1
  local port=$2
  local endpoint=${3:-health}
  
  log "Checking health of $service on port $port"
  
  # Try to connect to the service
  if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/$endpoint" | grep -q "200\|204"; then
    log "$service is healthy"
    return 0
  else
    log "Warning: $service appears to be unhealthy"
    return 1
  fi
}

# Function to check container status
check_container_status() {
  local service=$1
  
  log "Checking container status for $service"
  
  # Check if container is running
  if docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" ps "$service" | grep -q "Up"; then
    log "$service container is running"
    return 0
  else
    log "Warning: $service container is not running"
    return 1
  fi
}

# Function to check for resource usage
check_resource_usage() {
  local service=$1
  local container_id=$(docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" ps -q "$service")
  
  if [ -z "$container_id" ]; then
    log "Warning: Cannot find container ID for $service"
    return 1
  fi
  
  # Get CPU and memory usage
  local stats=$(docker stats "$container_id" --no-stream --format "{{.CPUPerc}}|{{.MemPerc}}")
  local cpu_usage=$(echo "$stats" | cut -d'|' -f1)
  local mem_usage=$(echo "$stats" | cut -d'|' -f2)
  
  log "$service resource usage: CPU: $cpu_usage, Memory: $mem_usage"
  
  # Check if usage is above thresholds
  local cpu_threshold="80.00%"
  local mem_threshold="80.00%"
  
  if (( $(echo "${cpu_usage%\%} > ${cpu_threshold%\%}" | bc -l) )); then
    log "Warning: High CPU usage for $service: $cpu_usage"
  fi
  
  if (( $(echo "${mem_usage%\%} > ${mem_threshold%\%}" | bc -l) )); then
    log "Warning: High memory usage for $service: $mem_usage"
  fi
}

# Function to check database connections
check_database_connections() {
  log "Checking database connections"
  
  # Get active connections
  local connections=$(docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" exec -T postgres psql -U agency_admin -d agency_system -c "SELECT count(*) FROM pg_stat_activity;" | grep -v "count" | grep -v "row" | tr -d ' ')
  
  log "Active database connections: $connections"
  
  # Check if connections are above threshold
  local connection_threshold=100
  
  if (( connections > connection_threshold )); then
    log "Warning: High number of database connections: $connections"
  fi
}

# Function to check disk space
check_disk_space() {
  log "Checking disk space"
  
  # Get disk usage
  local disk_usage=$(df -h | grep "/var/lib/docker" || df -h | grep "/")
  local used_percent=$(echo "$disk_usage" | awk '{print $5}' | tr -d '%')
  
  log "Disk usage: $used_percent%"
  
  # Check if disk usage is above threshold
  local disk_threshold=80
  
  if (( used_percent > disk_threshold )); then
    log "Warning: High disk usage: $used_percent%"
  fi
}

# Main monitoring loop
log "Starting monitoring"

# Check container status for all services
for service in foundation-api core-services federation-gateway cdc-implementation epa-implementation fema-implementation dashboard notification-service postgres redis; do
  check_container_status "$service"
done

# Check service health
check_service_health "foundation-api" "8000"
check_service_health "federation-gateway" "8010"
check_service_health "dashboard" "8080"
check_service_health "cdc-implementation" "8001" "api/health"
check_service_health "epa-implementation" "8002" "api/health"
check_service_health "fema-implementation" "8003" "api/health"

# Check resource usage for all services
for service in foundation-api core-services federation-gateway cdc-implementation epa-implementation fema-implementation dashboard notification-service postgres redis; do
  check_resource_usage "$service"
done

# Check database connections
check_database_connections

# Check disk space
check_disk_space

# Check logs for errors
log "Checking logs for errors"
for service in foundation-api federation-gateway dashboard notification-service; do
  error_count=$(docker-compose -f "${DEPLOYMENT_DIR}/docker-compose.yaml" logs --tail=1000 "$service" | grep -i "error\|exception\|fail" | wc -l)
  if (( error_count > 0 )); then
    log "Warning: Found $error_count errors in $service logs"
  fi
done

log "Monitoring completed"