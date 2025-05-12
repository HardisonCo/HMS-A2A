# Interagency Data Federation Hub

This module implements the interagency data federation components that enable data sharing and coordination between CDC, EPA, FEMA, and other federal agencies as specified in Section 7 of the Federal Agency Implementation Plan.

## Overview

The Federation Hub provides a standardized framework for agencies to share data, coordinate resources, broadcast alerts, and conduct joint analyses across organizational boundaries. This implementation supports the 5 key integration capabilities outlined in the plan:

1. **Federated Queries**: Standardized mechanism for cross-agency data access
2. **Shared Visualizations**: Combined views of multi-agency data
3. **Coordinated Alerting**: Cross-agency notification capabilities
4. **Resource Coordination**: Collaborative resource management
5. **Joint Analysis**: Shared models and analysis tools

## Architecture

The Federation Hub follows this architecture:

```
┌───────────────────────────────────────────────────────────┐
│                Data Sharing Federation                     │
│                                                           │
│  ┌─────────────┐       ┌─────────────┐      ┌─────────────┐│
│  │ Agency A    │◄─────►│  Federation │◄────►│ Agency B    ││
│  │ Adapter     │       │   Hub       │      │ Adapter     ││
│  └─────────────┘       └─────────────┘      └─────────────┘│
│         ▲                                         ▲        │
│         │                                         │        │
│         ▼                                         ▼        │
│  ┌─────────────┐       ┌─────────────┐      ┌─────────────┐│
│  │ Agency A    │       │ Shared      │      │ Agency B    ││
│  │ System      │       │ Services    │      │ System      ││
│  └─────────────┘       └─────────────┘      └─────────────┘│
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Components

### Core

- **FederationHub**: Central hub for coordinating all cross-agency interactions
- **AgencyRegistration**: Model for registering agencies and their capabilities

### Adapters

- **FederationAdapter**: Abstract base class that each agency implements
- **CDCFederationAdapter**: Adapter for CDC systems
- **EPAFederationAdapter**: Adapter for EPA systems
- **FEMAFederationAdapter**: Adapter for FEMA systems

### Services

- **FederatedQueryService**: Service for executing queries across multiple agencies
- **CrossAgencyAlertService**: Service for broadcasting alerts between agencies
- **ResourceCoordinationService**: Service for coordinating resource allocation
- **JointAnalysisService**: Service for conducting analyses across agency boundaries

## API Endpoints

The Federation Hub exposes the following API endpoints:

### Agency Registration

- `GET /api/v1/federation/agencies` - List all registered agencies

### Federated Queries

- `POST /api/v1/federation/query` - Execute a federated query across agencies
- `GET /api/v1/federation/query/types` - Get available query types for each agency

### Cross-Agency Alerts

- `POST /api/v1/federation/alert` - Broadcast an alert to multiple agencies
- `GET /api/v1/federation/alert/history` - Get alert history with optional filtering

### Resource Coordination

- `POST /api/v1/federation/resource/request` - Submit a resource request for coordination
- `GET /api/v1/federation/resource/request/{request_id}` - Get status of a resource request
- `GET /api/v1/federation/resource/active` - Get active resource requests

### Joint Analysis

- `POST /api/v1/federation/analysis` - Submit a joint analysis request
- `GET /api/v1/federation/analysis/{analysis_id}` - Get status of a joint analysis
- `GET /api/v1/federation/analysis/types` - Get available joint analysis types

## Usage Examples

### Execute a Federated Query

```python
# Query disease outbreaks in a region that correlates with environmental factors
query = {
    "type": "disease_surveillance",
    "parameters": {
        "region": "northeast",
        "disease_type": "respiratory",
        "start_date": "2023-01-01",
        "end_date": "2023-03-31"
    },
    "agencies": ["cdc", "epa"]  # Optional: specify target agencies
}

# Submit the query to the federation hub
response = requests.post(
    "http://localhost:8000/api/v1/federation/query",
    json=query
)
results = response.json()
```

### Broadcast a Cross-Agency Alert

```python
# Alert about a disease outbreak with environmental implications
alert = {
    "type": "disease_outbreak",
    "severity": "high",
    "title": "Significant increase in respiratory cases in Northeast region",
    "details": {
        "disease": "respiratory",
        "cases": 250,
        "region": "northeast",
        "environmental_factors": ["air_quality_decline", "pollen_increase"]
    },
    "source_agency": "cdc",
    "location": {
        "region": "northeast",
        "coordinates": {
            "latitude": 42.5,
            "longitude": -71.3
        }
    },
    "agencies": ["epa", "fema"]  # Optional: specify target agencies
}

# Send the alert through the federation hub
response = requests.post(
    "http://localhost:8000/api/v1/federation/alert",
    json=alert
)
broadcast_result = response.json()
```

### Coordinate Resources

```python
# Request emergency medical resources
resource_request = {
    "resource_type": "emergency_medical_kits",
    "quantity": 500,
    "location": {
        "region": "northeast",
        "state": "Massachusetts",
        "coordinates": {
            "latitude": 42.5,
            "longitude": -71.3
        }
    },
    "priority": "high",
    "requesting_agency": "cdc",
    "details": {
        "disaster_type": "disease_outbreak",
        "population_affected": 50000
    }
}

# Submit the resource request
response = requests.post(
    "http://localhost:8000/api/v1/federation/resource/request",
    json=resource_request
)
coordination_result = response.json()
```

### Run a Joint Analysis

```python
# Request a joint analysis of disease spread and environmental factors
analysis_request = {
    "analysis_type": "environmental_health_correlation",
    "parameters": {
        "region": "northeast",
        "env_factor": "air_quality",
        "health_outcome": "respiratory_disease",
        "start_date": "2023-01-01",
        "end_date": "2023-03-31",
        "confidence_level": 0.95
    },
    "requesting_agency": "cdc",
    "target_agencies": ["cdc", "epa"]
}

# Submit the analysis request
response = requests.post(
    "http://localhost:8000/api/v1/federation/analysis",
    json=analysis_request
)
submission_result = response.json()

# Get the analysis result (after it has completed)
analysis_id = submission_result["analysis_id"]
response = requests.get(
    f"http://localhost:8000/api/v1/federation/analysis/{analysis_id}"
)
analysis_result = response.json()
```

## Setup and Deployment

### Prerequisites

- Python 3.8+
- FastAPI
- PostgreSQL with PostGIS
- Docker and Docker Compose (for containerized deployment)

### Environment Setup

1. Create and activate a virtual environment
2. Install required packages:
   ```
   pip install fastapi uvicorn pydantic sqlalchemy psycopg2-binary
   ```

### Configuration

Configure the federation hub by setting the following environment variables:

- `FEDERATION_HUB_HOST`: Hostname for the federation hub (default: localhost)
- `FEDERATION_HUB_PORT`: Port for the federation hub (default: 8000)
- `CDC_API_BASE_URL`: Base URL for CDC API
- `EPA_API_BASE_URL`: Base URL for EPA API
- `FEMA_API_BASE_URL`: Base URL for FEMA API

### Running the Federation Hub

Start the federation hub with:

```
uvicorn agency_implementation.federation.api:api --host 0.0.0.0 --port 8000
```

For production, deploy using Docker:

```
docker-compose -f docker-compose.federation.yml up -d
```

## Security Considerations

The Federation Hub implements several security measures:

1. **Authentication**: All agencies must register and authenticate before accessing federation services
2. **Authorization**: Access to specific data types and operations is controlled by agency-specific permissions
3. **Encryption**: All inter-agency communication is encrypted using TLS
4. **Audit Logging**: All federation operations are logged for accountability and auditing
5. **Data Filtering**: Agencies can specify which data elements are shareable across boundaries

## Extending the Framework

To add support for additional agencies:

1. Create a new adapter that implements the `FederationAdapter` interface
2. Register the new adapter with the federation hub
3. Update API documentation to include agency-specific query types and capabilities

## Contact

For questions or support, contact the Interagency Federation Team at federation-support@example.gov.