# Agency Implementation of Adaptive Surveillance and Response System

This directory contains agency-specific implementations of the Adaptive Surveillance and Response System, modeled after the successful APHIS Bird Flu Tracking System.

## Available Agency Implementations

### CDC (Centers for Disease Control and Prevention)

The CDC implementation focuses on:
- Human disease surveillance
- Contact tracing components
- Healthcare system integration
- Outbreak detection and response

### EPA (Environmental Protection Agency)

The EPA implementation focuses on:
- Environmental quality monitoring
- Compliance surveillance
- Enforcement resource optimization
- Pollution impact modeling

### FEMA (Federal Emergency Management Agency)

The FEMA implementation focuses on:
- Disaster risk monitoring
- Resource deployment optimization
- Recovery progress tracking
- Disaster impact prediction

## System Supervisor Pattern

Each agency implementation follows the system-supervisor pattern established in the APHIS Bird Flu system:

1. **Supervisor Component** - Coordinates all agency-specific services
2. **Health Monitoring** - Continuously monitors component status
3. **Component Lifecycle Management** - Handles startup, shutdown, and recovery
4. **Cross-Component Orchestration** - Manages workflows across multiple services
5. **API Integration** - FastAPI endpoints for system access

## Directory Structure

```
agency-implementation/
├── foundation/                # Shared foundation code
│   ├── base_models/           # Base models for all implementations
├── cdc/                       # CDC implementation
│   ├── system-supervisors/    # CDC system supervisor
│       ├── cdc_supervisor.py  # CDC supervisor implementation
│       ├── api.py             # CDC API endpoints
├── epa/                       # EPA implementation
│   ├── system-supervisors/    # EPA system supervisor
│       ├── epa_supervisor.py  # EPA supervisor implementation
│       ├── api.py             # EPA API endpoints
├── fema/                      # FEMA implementation
│   ├── system-supervisors/    # FEMA system supervisor
│       ├── fema_supervisor.py # FEMA supervisor implementation
│       ├── api.py             # FEMA API endpoints
```

## Running an Agency Implementation

You can start any agency implementation using the provided launcher script:

```bash
# Start the CDC implementation
./start_agency_api.py cdc

# Start the EPA implementation
./start_agency_api.py epa

# Start the FEMA implementation
./start_agency_api.py fema
```

By default, each agency runs on a different port:
- CDC: Port 8001
- EPA: Port 8002
- FEMA: Port 8003

You can override the port using the `--port` flag:

```bash
./start_agency_api.py cdc --port 9000
```

During development, you can enable automatic reload with:

```bash
./start_agency_api.py cdc --reload
```

## API Documentation

Each agency implementation includes Swagger documentation available at:

- CDC: http://localhost:8001/docs
- EPA: http://localhost:8002/docs
- FEMA: http://localhost:8003/docs

## Component Health Monitoring

All agency implementations include comprehensive health monitoring:

- Access the health check endpoint at `/health`
- View system status with component details
- Monitor component initialization and recovery

## Workflow Orchestration

Each agency implementation provides workflow orchestration endpoints:

### CDC Workflows

- `/api/v1/workflows/outbreak-investigation` - Orchestrate outbreak investigation
- `/api/v1/workflows/disease-forecasting` - Forecast disease spread
- `/api/v1/workflows/surveillance-optimization` - Optimize surveillance resources

### EPA Workflows

- `/api/v1/workflows/pollution-impact-assessment` - Assess pollution impact
- `/api/v1/workflows/compliance-risk-analysis` - Analyze compliance risks
- `/api/v1/workflows/enforcement-resource-allocation` - Allocate enforcement resources

### FEMA Workflows

- `/api/v1/workflows/disaster-impact-prediction` - Predict disaster impact
- `/api/v1/workflows/resource-deployment-planning` - Plan resource deployment
- `/api/v1/workflows/recovery-effectiveness-assessment` - Assess recovery effectiveness

## Extension Points

Each agency implementation includes extension points for customization:

1. **Agency-specific models** - Extend foundation models for agency needs
2. **Custom workflows** - Add new cross-component workflows
3. **Specialized services** - Implement agency-specific services
4. **Visualization components** - Create agency-specific visualizations
5. **External integrations** - Connect to agency-specific systems