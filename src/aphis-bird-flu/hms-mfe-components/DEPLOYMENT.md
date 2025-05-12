# APHIS Bird Flu HMS-MFE Deployment Guide

This document provides detailed instructions for deploying the APHIS Bird Flu HMS-MFE components to various environments, including staging and production.

## Overview

The APHIS Bird Flu HMS-MFE solution is designed to be deployed as a containerized application in a Kubernetes environment. The deployment process is automated through a CI/CD pipeline, but manual deployment is also supported.

## Prerequisites

### For Automated Deployment
- GitHub Actions configured with appropriate secrets
- Kubernetes cluster access configured via secrets
- Docker registry access (GitHub Container Registry)

### For Manual Deployment
- Docker and Docker Compose
- Kubernetes CLI (kubectl)
- Helm
- Access credentials for the target environment

## Deployment Architecture

The system is deployed using a blue/green deployment strategy in production to minimize downtime and risk:

1. **Staging Environment**
   - Single deployment instance
   - Used for testing and validation

2. **Production Environment**
   - Blue/Green deployment model
   - Traffic is switched between two identical environments
   - Zero-downtime deployments

## Environment Configuration

Configuration for different environments is managed through:

1. **Environment Variables**
   - Passed to the container at runtime
   - Managed through Kubernetes ConfigMaps and Secrets

2. **Application Config**
   - Runtime configuration stored in ConfigMaps
   - Different values for staging and production

3. **Feature Flags**
   - Enable/disable features per environment
   - Controlled via ConfigMaps

## Automated Deployment Process

The CI/CD pipeline is defined in `.github/workflows/deployment.yml` and executes the following steps:

### 1. Build and Test
- Lint and security audit
- Build the application
- Run comprehensive integration tests

### 2. Container Creation
- Build Docker container
- Tag with appropriate version
- Push to container registry

### 3. Staging Deployment
- Deploy to staging environment
- Run smoke tests
- Await approval for production deployment

### 4. Production Deployment
- Deploy to inactive environment (blue or green)
- Run smoke tests against new deployment
- Switch traffic to new deployment
- Verify deployment success

## Manual Deployment

### Local Development Environment

```bash
# Start the development environment
cd hms-mfe-components
npm install
npm run dev

# Run with mock API
docker-compose up -d
```

### Staging Environment

```bash
# Build the container
docker build -t ghcr.io/hardisonco/aphis-bird-flu-mfe:latest .

# Push to registry
docker push ghcr.io/hardisonco/aphis-bird-flu-mfe:latest

# Deploy with Helm
helm upgrade --install aphis-bird-flu-mfe ./helm \
  --namespace hms-mfe-staging \
  --set image.repository=ghcr.io/hardisonco/aphis-bird-flu-mfe \
  --set image.tag=latest \
  --set ingress.hosts[0].host=staging.aphis-bird-flu.hms-mfe.gov \
  --set apiBaseUrl=https://api-staging.aphis-bird-flu.hms-mfe.gov \
  --set federationHubUrl=https://federation-staging.hms-mfe.gov
```

### Production Environment

Manual production deployment using the blue/green strategy:

```bash
# Get current active color
CURRENT_COLOR=$(kubectl get configmap aphis-bird-flu-mfe-config -n hms-mfe-production -o jsonpath='{.data.activeColor}')

# Set new color
if [ "$CURRENT_COLOR" == "blue" ]; then
  NEW_COLOR="green"
else
  NEW_COLOR="blue"
fi

# Deploy to new color
helm upgrade --install aphis-bird-flu-mfe-$NEW_COLOR ./helm \
  --namespace hms-mfe-production \
  --set image.repository=ghcr.io/hardisonco/aphis-bird-flu-mfe \
  --set image.tag=latest \
  --set nameOverride=aphis-bird-flu-mfe-$NEW_COLOR \
  --set ingress.enabled=false \
  --set apiBaseUrl=https://api.aphis-bird-flu.hms-mfe.gov \
  --set federationHubUrl=https://federation.hms-mfe.gov

# Run smoke tests
cd tests
npm run test:smoke

# Switch traffic to new deployment
kubectl patch ingress aphis-bird-flu-mfe -n hms-mfe-production --type=json \
  -p='[{"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/name", "value":"aphis-bird-flu-mfe-'$NEW_COLOR'"}]'

# Update configmap with new active color
kubectl patch configmap aphis-bird-flu-mfe-config -n hms-mfe-production --type=merge \
  -p='{"data":{"activeColor":"'$NEW_COLOR'"}}'
```

## Environment-Specific Configuration

### Staging Environment

| Parameter | Value |
|-----------|-------|
| API Base URL | https://api-staging.aphis-bird-flu.hms-mfe.gov |
| Federation Hub URL | https://federation-staging.hms-mfe.gov |
| Log Level | debug |
| Environment | staging |

### Production Environment

| Parameter | Value |
|-----------|-------|
| API Base URL | https://api.aphis-bird-flu.hms-mfe.gov |
| Federation Hub URL | https://federation.hms-mfe.gov |
| Log Level | info |
| Environment | production |

## Monitoring and Observability

The deployment includes monitoring and observability features:

1. **Health Endpoints**
   - `/health` - Basic health check
   - `/health/detailed` - Detailed component status

2. **Metrics**
   - Prometheus metrics exposed on port 9113
   - Standard metrics for HTTP requests, errors, and latency
   - Custom metrics for business processes

3. **Logging**
   - Structured JSON logs
   - Log level configurable per environment
   - Log forwarding to centralized logging system

## Rollback Procedure

If issues are detected after deployment:

### Automated Rollback (Blue/Green)

In production, simply switch the ingress back to the previous color:

```bash
kubectl patch ingress aphis-bird-flu-mfe -n hms-mfe-production --type=json \
  -p='[{"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/name", "value":"aphis-bird-flu-mfe-'$CURRENT_COLOR'"}]'

kubectl patch configmap aphis-bird-flu-mfe-config -n hms-mfe-production --type=merge \
  -p='{"data":{"activeColor":"'$CURRENT_COLOR'"}}'
```

### Manual Rollback (Helm)

```bash
# Roll back to the previous release
helm rollback aphis-bird-flu-mfe -n hms-mfe-staging
```

## Security Considerations

1. **Container Security**
   - Images are scanned for vulnerabilities
   - Non-root user in containers
   - Read-only file system where possible

2. **Network Security**
   - TLS for all ingress traffic
   - Network policies limit pod-to-pod communication
   - API authentication for all backend services

3. **Secrets Management**
   - Sensitive values stored in Kubernetes Secrets
   - Secrets mounted as environment variables
   - Rotation schedule for all credentials

## Troubleshooting

### Common Issues

1. **Deployment Fails**
   - Check pipeline logs for build/test failures
   - Verify Kubernetes cluster has sufficient resources
   - Check for networking or registry access issues

2. **Application Unhealthy**
   - Check health endpoint logs
   - Verify API and Federation Hub connectivity
   - Check for configuration errors

3. **Performance Issues**
   - Check resource utilization (CPU/memory)
   - Examine API response times
   - Review network connectivity between services

### Support Contacts

For deployment issues, contact:
- HMS-MFE DevOps Team: hms-mfe-devops@example.gov
- APHIS Technical Lead: aphis-technical-lead@example.gov