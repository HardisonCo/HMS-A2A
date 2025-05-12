# Agency Implementation System Troubleshooting Guide

This guide provides solutions for common issues that may occur during deployment and operation of the Agency Implementation System.

## Table of Contents

1. [Deployment Issues](#deployment-issues)
2. [Database Issues](#database-issues)
3. [Federation Issues](#federation-issues)
4. [Agency Implementation Issues](#agency-implementation-issues)
5. [Dashboard Issues](#dashboard-issues)
6. [Notification System Issues](#notification-system-issues)
7. [Performance Issues](#performance-issues)
8. [Security Issues](#security-issues)
9. [Network Issues](#network-issues)
10. [Logging and Monitoring](#logging-and-monitoring)

## Deployment Issues

### Services Fail to Start

**Symptoms**:
- Docker containers exit immediately after starting
- `docker-compose ps` shows container status as "Exit"

**Solutions**:
1. Check container logs:
   ```bash
   docker-compose logs <service_name>
   ```

2. Verify environment variables:
   ```bash
   # Check if environment files are correctly formatted
   cat ./config/*.env | grep -v "^#" | grep -v "^$"
   ```

3. Check for port conflicts:
   ```bash
   # Check if ports are already in use
   netstat -tulpn | grep <port_number>
   ```

4. Verify Docker resource limits:
   ```bash
   # Check Docker daemon configuration
   docker info
   ```

### Deployment Script Fails

**Symptoms**:
- `deploy.sh` exits with an error
- Some services start but others fail

**Solutions**:
1. Check deployment logs:
   ```bash
   cat deployment.log
   ```

2. Run deployment with verbose logging:
   ```bash
   bash -x ./scripts/deploy.sh
   ```

3. Try manual deployment:
   ```bash
   docker-compose up -d foundation-api
   docker-compose up -d federation-gateway
   # Continue with other services
   ```

## Database Issues

### Database Connection Failures

**Symptoms**:
- Services log "could not connect to database"
- Database health checks fail

**Solutions**:
1. Check database container is running:
   ```bash
   docker-compose ps postgres
   ```

2. Verify database credentials:
   ```bash
   # Check environment variables match database configuration
   grep "DB_" ./config/*.env
   ```

3. Check database logs:
   ```bash
   docker-compose logs postgres
   ```

4. Connect to database directly:
   ```bash
   docker-compose exec postgres psql -U agency_admin -d agency_system
   ```

### Database Performance Issues

**Symptoms**:
- Slow query responses
- High CPU usage on database container

**Solutions**:
1. Check for slow queries:
   ```bash
   docker-compose exec postgres psql -U agency_admin -d agency_system -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
   ```

2. Optimize PostgreSQL configuration:
   ```bash
   # Adjust shared_buffers, work_mem, etc.
   docker-compose exec postgres cat /var/lib/postgresql/data/postgresql.conf
   ```

3. Add indexes to frequently queried columns:
   ```sql
   CREATE INDEX idx_alerts_created_at ON agency_system.alerts(created_at);
   ```

## Federation Issues

### Federation Gateway Connectivity

**Symptoms**:
- Agency implementations cannot connect to federation gateway
- Error logs showing "connection refused" or "authentication failed"

**Solutions**:
1. Check federation gateway is running:
   ```bash
   docker-compose ps federation-gateway
   ```

2. Verify network connectivity:
   ```bash
   docker-compose exec cdc-implementation ping federation-gateway
   ```

3. Check federation credentials:
   ```bash
   # Verify client credentials match in both services
   grep "FEDERATION_CLIENT" ./config/cdc.env
   grep "FEDERATION_CLIENT" ./config/federation.env
   ```

4. Verify federation logs:
   ```bash
   docker-compose logs federation-gateway | grep "auth"
   ```

### Data Synchronization Issues

**Symptoms**:
- Data is not appearing in federated queries
- Federation audit logs show sync failures

**Solutions**:
1. Check federation sync status:
   ```bash
   docker-compose exec federation-gateway /app/scripts/check-sync-status.sh
   ```

2. Manually trigger synchronization:
   ```bash
   docker-compose exec federation-gateway /app/scripts/trigger-sync.sh
   ```

3. Check data schema compatibility:
   ```bash
   # Verify schema versions across services
   docker-compose exec federation-gateway /app/scripts/schema-version.sh
   ```

## Agency Implementation Issues

### Agency-Specific Services Not Available

**Symptoms**:
- Agency API endpoints return 404 or connection refused
- Agency data not visible in dashboard

**Solutions**:
1. Check agency implementation container is running:
   ```bash
   docker-compose ps cdc-implementation
   ```

2. Verify agency configuration:
   ```bash
   docker-compose exec cdc-implementation cat /app/config/agency.json
   ```

3. Check agency service logs:
   ```bash
   docker-compose logs cdc-implementation
   ```

4. Test agency API directly:
   ```bash
   curl http://localhost:8001/api/health
   ```

### Custom Agency Extensions Not Loading

**Symptoms**:
- Agency-specific features not appearing
- Extension loading errors in logs

**Solutions**:
1. Verify extension files exist:
   ```bash
   docker-compose exec cdc-implementation ls -la /app/extensions/
   ```

2. Check extension configuration:
   ```bash
   docker-compose exec cdc-implementation cat /app/extensions/config.json
   ```

3. Enable extension debugging:
   ```bash
   # Update environment variable
   sed -i 's/EXTENSION_DEBUG=false/EXTENSION_DEBUG=true/' ./config/cdc.env
   docker-compose up -d cdc-implementation
   ```

## Dashboard Issues

### Dashboard Not Loading

**Symptoms**:
- Browser shows blank page or connection error
- Browser console shows API connection errors

**Solutions**:
1. Check dashboard container is running:
   ```bash
   docker-compose ps dashboard
   ```

2. Verify dashboard logs:
   ```bash
   docker-compose logs dashboard
   ```

3. Check if dashboard can connect to federation:
   ```bash
   docker-compose exec dashboard curl -s http://federation-gateway:8010/health
   ```

4. Verify frontend assets:
   ```bash
   docker-compose exec dashboard ls -la /app/static/
   ```

### Visualizations Not Displaying

**Symptoms**:
- Dashboard loads but charts or maps are missing
- Browser console shows JavaScript errors

**Solutions**:
1. Check browser console for errors
2. Verify data is available:
   ```bash
   # Test API endpoint directly
   curl http://localhost:8080/api/visualization-data
   ```

3. Clear browser cache and cookies
4. Update visualization libraries:
   ```bash
   docker-compose exec dashboard npm update
   ```

## Notification System Issues

### Notifications Not Being Sent

**Symptoms**:
- Alerts are created but notifications aren't delivered
- Notification logs show errors

**Solutions**:
1. Check notification service is running:
   ```bash
   docker-compose ps notification-service
   ```

2. Verify notification channels configuration:
   ```bash
   docker-compose exec notification-service cat /app/config/notification_config.json
   ```

3. Test notification delivery manually:
   ```bash
   docker-compose exec notification-service /app/scripts/test-notification.sh
   ```

4. Check third-party service connectivity:
   ```bash
   # Test SMTP connectivity
   docker-compose exec notification-service telnet smtp.example.com 587
   ```

### Notification Delays

**Symptoms**:
- Notifications are sent but delayed
- High message queue backlog

**Solutions**:
1. Check notification service load:
   ```bash
   docker-compose exec notification-service /app/scripts/queue-status.sh
   ```

2. Increase worker threads:
   ```bash
   # Update environment variable
   sed -i 's/NOTIFICATION_WORKERS=5/NOTIFICATION_WORKERS=10/' ./config/notifications.env
   docker-compose up -d notification-service
   ```

3. Monitor notification processing rate:
   ```bash
   docker-compose logs -f notification-service | grep "Processing"
   ```

## Performance Issues

### Slow API Responses

**Symptoms**:
- API requests take a long time to complete
- Timeout errors in application logs

**Solutions**:
1. Check service resource usage:
   ```bash
   docker stats
   ```

2. Enable performance profiling:
   ```bash
   # Update environment variable
   sed -i 's/ENABLE_PROFILING=false/ENABLE_PROFILING=true/' ./config/foundation.env
   docker-compose up -d foundation-api
   ```

3. Analyze slow queries:
   ```bash
   docker-compose exec postgres psql -U agency_admin -d agency_system -c "SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start ASC LIMIT 10;"
   ```

4. Implement caching for frequent queries:
   ```bash
   # Update environment variable
   sed -i 's/CACHE_ENABLED=false/CACHE_ENABLED=true/' ./config/foundation.env
   docker-compose up -d foundation-api
   ```

### High Memory Usage

**Symptoms**:
- Containers are using excessive memory
- OOM (Out of Memory) errors in logs

**Solutions**:
1. Check memory usage:
   ```bash
   docker stats | grep -v CONTAINER
   ```

2. Identify memory leaks:
   ```bash
   # Enable heap dumps
   sed -i 's/HEAP_DUMP_ENABLED=false/HEAP_DUMP_ENABLED=true/' ./config/foundation.env
   docker-compose up -d foundation-api
   ```

3. Adjust container memory limits:
   ```yaml
   # Update docker-compose.yaml
   services:
     foundation-api:
       deploy:
         resources:
           limits:
             memory: 2G
   ```

## Security Issues

### Authentication Failures

**Symptoms**:
- Users unable to log in
- Authentication errors in logs

**Solutions**:
1. Check authentication service logs:
   ```bash
   docker-compose logs foundation-api | grep "auth"
   ```

2. Verify JWT configuration:
   ```bash
   grep "JWT_" ./config/foundation.env
   ```

3. Test authentication manually:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login -d '{"username":"admin","password":"password"}'
   ```

### SSL/TLS Issues

**Symptoms**:
- Browser shows security warnings
- Certificate errors in logs

**Solutions**:
1. Verify SSL certificates:
   ```bash
   docker-compose exec dashboard ls -la /app/ssl/
   ```

2. Check certificate expiration:
   ```bash
   docker-compose exec dashboard openssl x509 -enddate -noout -in /app/ssl/server.crt
   ```

3. Update SSL configuration:
   ```bash
   # Copy new certificates
   docker cp ./new-certs/server.crt agency-implementation_dashboard_1:/app/ssl/
   docker cp ./new-certs/server.key agency-implementation_dashboard_1:/app/ssl/
   ```

## Network Issues

### Container Communication Problems

**Symptoms**:
- Services cannot communicate with each other
- "Connection refused" errors in logs

**Solutions**:
1. Check Docker network configuration:
   ```bash
   docker network inspect agency_network
   ```

2. Verify container IP addresses:
   ```bash
   docker-compose exec foundation-api ip addr
   ```

3. Test network connectivity:
   ```bash
   docker-compose exec foundation-api ping federation-gateway
   ```

4. Restart Docker networking:
   ```bash
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

### External Network Access Issues

**Symptoms**:
- Services cannot access external APIs
- Timeout errors when fetching external data

**Solutions**:
1. Check DNS resolution:
   ```bash
   docker-compose exec foundation-api nslookup example.com
   ```

2. Verify proxy configuration:
   ```bash
   grep "PROXY_" ./config/*.env
   ```

3. Test external connectivity:
   ```bash
   docker-compose exec foundation-api curl -v https://api.example.com
   ```

## Logging and Monitoring

### Missing Logs

**Symptoms**:
- Expected logs are not appearing
- Log files are empty or not updated

**Solutions**:
1. Check logging configuration:
   ```bash
   grep "LOG_" ./config/*.env
   ```

2. Verify log file permissions:
   ```bash
   docker-compose exec foundation-api ls -la /var/log/
   ```

3. Enable debug logging:
   ```bash
   # Update environment variable
   sed -i 's/LOG_LEVEL=info/LOG_LEVEL=debug/' ./config/foundation.env
   docker-compose up -d foundation-api
   ```

4. Check logging service status:
   ```bash
   docker-compose logs | grep "logging"
   ```

### Monitoring Alerts Not Triggering

**Symptoms**:
- System issues not generating alerts
- Monitoring dashboard shows no data

**Solutions**:
1. Check monitoring service configuration:
   ```bash
   cat ./config/prometheus.yml
   ```

2. Verify metrics endpoints:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. Test alert rules manually:
   ```bash
   # Access Prometheus UI
   open http://localhost:9090/alerts
   ```

4. Check alert manager configuration:
   ```bash
   cat ./config/alertmanager.yml
   ```

## Additional Resources

- [System Architecture Documentation](./ARCHITECTURE.md)
- [Scaling Guide](./SCALING.md)
- [Docker Troubleshooting Guide](https://docs.docker.com/engine/troubleshooting/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

If you encounter an issue not covered in this guide, please contact:

- Technical Support: support@example.com
- Issue Tracker: https://github.com/example/agency-implementation/issues