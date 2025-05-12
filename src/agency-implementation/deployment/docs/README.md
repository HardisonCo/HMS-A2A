# Agency Implementation System Deployment

This directory contains all configuration and scripts needed to deploy the Agency Implementation System, including agency implementations, federation components, unified dashboard, and notification system.

## System Components

The Agency Implementation System consists of the following components:

1. **Foundation Layer**
   - Foundation API - Core API framework
   - Core Services - Shared business logic services

2. **Federation Layer**
   - Federation Gateway - Central coordination point for data sharing

3. **Agency Implementations**
   - CDC Implementation - Centers for Disease Control implementation
   - EPA Implementation - Environmental Protection Agency implementation
   - FEMA Implementation - Federal Emergency Management Agency implementation

4. **User Interface**
   - Unified Dashboard - Web interface for visualizing agency data

5. **Notification System**
   - Notification Service - Manages alerts and notifications

6. **Infrastructure Services**
   - PostgreSQL Database - Data storage
   - Redis - Caching and message brokering

## Directory Structure

- `config/` - Environment configurations and initialization scripts
- `scripts/` - Deployment, backup, and monitoring scripts
- `docs/` - Documentation on deployment, scaling, and troubleshooting

## Deployment Requirements

- Docker Engine 20.10.0+
- Docker Compose 2.0.0+
- 8GB RAM minimum (16GB recommended)
- 50GB disk space
- Network access for container communication
- SSL certificates (for production)

## Quick Start Guide

1. Clone the repository:
   ```
   git clone https://github.com/example/agency-implementation.git
   cd agency-implementation
   ```

2. Review and customize environment configuration files in `deployment/config/`:
   - Update database credentials
   - Configure API keys and secrets
   - Set up notification channel details

3. Run the deployment script:
   ```
   cd deployment
   chmod +x scripts/*.sh
   ./scripts/deploy.sh
   ```

4. Access the unified dashboard at `http://localhost:8080`

5. Monitor the system:
   ```
   ./scripts/monitor.sh
   ```

## Configuration Details

All configuration is managed through environment variables defined in the `.env` files in the `config/` directory:

- `foundation.env` - Foundation API configuration
- `core-services.env` - Core services configuration
- `federation.env` - Federation gateway configuration
- `cdc.env`, `epa.env`, `fema.env` - Agency implementation configs
- `dashboard.env` - Unified dashboard configuration
- `notifications.env` - Notification system configuration

## Deployment Scripts

The following scripts are available in the `scripts/` directory:

- `deploy.sh` - Main deployment script
- `post-deploy.sh` - Post-deployment verification and setup
- `security-hardening.sh` - Security hardening procedures
- `backup.sh` - Database and configuration backup
- `restore.sh` - Restore from a backup
- `monitor.sh` - Monitor system health

## Maintenance Procedures

### Backups

Schedule regular backups using the provided backup script:

```bash
# Manual backup
./scripts/backup.sh

# Scheduled backup (via cron)
0 2 * * * /path/to/agency-implementation/deployment/scripts/backup.sh
```

### Updates and Upgrades

To update the system:

1. Pull the latest code changes
2. Check for configuration changes
3. Run the deployment script:
   ```
   ./scripts/deploy.sh
   ```

### Scaling

The system can be scaled horizontally by adjusting the `docker-compose.yaml` file:

```yaml
services:
  foundation-api:
    deploy:
      replicas: 3
```

For larger deployments, consider using Docker Swarm or Kubernetes for orchestration.

## Troubleshooting

### Common Issues

1. **Database connection failures**
   - Check PostgreSQL logs: `docker-compose logs postgres`
   - Verify database credentials in environment files

2. **Federation gateway connectivity issues**
   - Check network connectivity between containers
   - Verify federation client credentials

3. **Dashboard not loading data**
   - Check browser console for JavaScript errors
   - Verify API endpoints are accessible

### Logs

Access container logs using:

```bash
docker-compose logs [service_name]

# Examples:
docker-compose logs foundation-api
docker-compose logs --tail=100 federation-gateway
docker-compose logs -f notification-service
```

### Health Checks

Use the monitoring script to check system health:

```bash
./scripts/monitor.sh
```

Or access individual health endpoints:

```
http://localhost:8000/health  # Foundation API
http://localhost:8010/health  # Federation Gateway
http://localhost:8080/health  # Unified Dashboard
```

## Security Considerations

- All production deployments should use HTTPS (SSL/TLS)
- Update default credentials in configuration files
- Restrict network access to the system
- Run the security hardening script after deployment
- Regularly update dependencies and images

## Support

For issues and support, please contact:

- Technical Support: support@example.com
- Documentation: docs@example.com
- Issue Tracker: https://github.com/example/agency-implementation/issues