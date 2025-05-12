# Agency Implementation Guide

This comprehensive guide provides step-by-step instructions for agencies to create their own implementations using the HMS foundation components. The guide covers the entire process from initial setup to deployment and maintenance, with detailed examples and best practices.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Architecture Overview](#architecture-overview)
5. [Core Components](#core-components)
6. [Customization Points](#customization-points)
7. [Data Integration](#data-integration)
8. [Federation and Interoperability](#federation-and-interoperability)
9. [Testing and Validation](#testing-and-validation)
10. [Deployment](#deployment)
11. [Maintenance and Updates](#maintenance-and-updates)
12. [Troubleshooting](#troubleshooting)
13. [Advanced Topics](#advanced-topics)
14. [Reference Implementation Examples](#reference-implementation-examples)
15. [Resources and Support](#resources-and-support)

## Introduction

The HMS Agency Implementation framework provides a standardized approach for government agencies to build, deploy, and maintain specialized systems tailored to their specific requirements. This framework follows a modular architecture that enables:

- Rapid development through reusable components
- Standardized integration with other government systems
- Customization for agency-specific needs
- Consistent security and compliance
- Federation capabilities for cross-agency collaboration

This guide will walk you through the complete process of creating an agency-specific implementation using the foundation components.

## Prerequisites

Before beginning your implementation, ensure you have the following prerequisites in place:

### Technical Requirements

- Python 3.8+ or Rust 1.54+ (depending on your implementation language)
- Docker and Docker Compose
- Git
- Access to agency network and resources
- Node.js 16+ (for frontend components)

### Knowledge Requirements

- Basic understanding of REST APIs
- Familiarity with containerization concepts
- Understanding of your agency's data structures and workflows
- Knowledge of security and compliance requirements for your agency

### Resource Access

- HMS Component Registry access
- Agency data sources and APIs
- Development environment with necessary permissions

## Initial Setup

Follow these steps to set up your initial development environment:

### 1. Clone the Template Repository

```bash
# Clone the template repository
git clone https://github.com/hms-gov/agency-implementation-template your-agency-name
cd your-agency-name

# Initialize the project structure
./initialize_project.sh YOUR_AGENCY_CODE
```

### 2. Configure Your Environment

Create an `.env` file for local development:

```bash
# Create from the template
cp .env.template .env

# Edit the file with your specific configuration values
nano .env
```

Required configuration values:

```
AGENCY_CODE=YOUR_AGENCY_CODE
AGENCY_NAME="Your Agency Name"
API_BASE_URL=http://localhost:5000/api
HMS_REGISTRY_URL=https://registry.hms-gov.org
```

### 3. Install Dependencies

```bash
# For Python-based implementations
pip install -r requirements.txt

# For Rust-based implementations
cargo build
```

### 4. Initialize Database

```bash
# Set up the database schema
python scripts/init_db.py

# Load seed data (if applicable)
python scripts/seed_data.py
```

### 5. Run the Development Server

```bash
# Start the development server
docker-compose up -d
```

Verify the setup by accessing:
- API: http://localhost:5000/api/v1/health
- Documentation: http://localhost:5000/docs

## Architecture Overview

The HMS Agency Implementation architecture consists of several layers:

### Core Architecture Layers

1. **Foundation Layer**: Common utilities, data models, and services used across all agency implementations
2. **Extension Points**: Customizable interfaces for agency-specific functionality
3. **Agency Implementation Layer**: Agency-specific models, business logic, and workflows
4. **Federation Layer**: Tools for cross-agency data sharing and interoperability
5. **Presentation Layer**: API endpoints and visualization tools

### Key Design Principles

- **Modularity**: Each component has a single responsibility and can be replaced independently
- **Extensibility**: Clear extension points allow for customization without modifying core code
- **Standardization**: Common interfaces ensure consistent behavior across implementations
- **Security-First**: Security and compliance are built into the architecture
- **Data Federation**: Designed for seamless cross-agency data integration

### Directory Structure

```
agency-implementation/
├── config/                 # Configuration files
├── docs/                   # Documentation
├── src/                    # Source code
│   ├── api/                # API controllers and routes
│   ├── models/             # Data models
│   ├── services/           # Business logic services
│   ├── integrations/       # External system integrations
│   └── utilities/          # Utility functions
├── tests/                  # Test suite
├── scripts/                # Setup and maintenance scripts
└── docker-compose.yml      # Containerization configuration
```

## Core Components

The foundation includes several core components that can be leveraged for your implementation:

### 1. API Framework

The API framework provides a standardized way to expose endpoints and handle requests:

```python
# Example of creating an API endpoint
from foundation.api_framework import app_factory
from foundation.api_framework.controllers import BaseController

class YourAgencyController(BaseController):
    @app_factory.route('/api/v1/resources', methods=['GET'])
    def get_resources(self):
        # Your implementation here
        return self.respond_with_json(resources)

# Register the controller
app = app_factory.create_app()
app.register_controller(YourAgencyController())
```

### 2. Core Services

Services implement business logic and processing capabilities:

```python
# Example of extending a core service
from foundation.core_services import BaseService

class YourAgencyService(BaseService):
    def process_agency_data(self, input_data):
        # Your implementation here
        return processed_data
```

Key available services:
- `detection_service`: For identifying patterns or anomalies
- `prediction_service`: For forecasting based on historical data
- `notification_service`: For sending alerts and notifications
- `visualization_service`: For generating visualizations
- `genetic_analysis_service`: For advanced data analysis

### 3. Data Models

Define your agency-specific data models by extending the base models:

```python
# Example of creating an agency-specific model
from foundation.base_models import BaseEntity
from sqlalchemy import Column, String, Integer, Date

class AgencySpecificEntity(BaseEntity):
    __tablename__ = 'agency_specific_entities'
    
    field1 = Column(String(255), nullable=False)
    field2 = Column(Integer)
    field3 = Column(Date)
```

### 4. Utility Functions

Leverage common utilities for frequent operations:

```javascript
// Example of using utility functions
const { logger, validation, httpClient } = require('foundation/utilities');

async function fetchAndValidateData() {
  try {
    const data = await httpClient.get('https://api.example.gov/data');
    if (validation.isValid(data, 'agency-schema')) {
      return data;
    }
    logger.error('Invalid data received');
  } catch (error) {
    logger.error('Error fetching data', error);
  }
}
```

## Customization Points

The framework provides several extension points for agency-specific customization:

### 1. Register Custom Extensions

```python
# Example of registering a custom extension
from foundation.extension_points import registry
from foundation.extension_points.data_sources import BaseDataSource

class AgencySpecificDataSource(BaseDataSource):
    def fetch_data(self, parameters):
        # Your implementation here
        return agency_data

# Register the extension
registry.register_extension('data_source', 'agency_specific', AgencySpecificDataSource)
```

### 2. Custom Predictive Models

```python
# Example of implementing a custom predictive model
from foundation.extension_points.predictive_models import BaseModel
import sklearn.ensemble

class AgencyPredictiveModel(BaseModel):
    def __init__(self):
        self.model = sklearn.ensemble.RandomForestRegressor()
        
    def train(self, X, y):
        self.model.fit(X, y)
        
    def predict(self, X):
        return self.model.predict(X)

# Register the model
registry.register_extension('predictive_model', 'agency_forecast', AgencyPredictiveModel)
```

### 3. Custom Visualization Components

```python
# Example of implementing a custom visualization component
from foundation.extension_points.visualization_components import BaseVisualization

class AgencyDashboard(BaseVisualization):
    def generate(self, data, options=None):
        # Implementation to generate a custom dashboard
        return dashboard_html

# Register the visualization
registry.register_extension('visualization', 'agency_dashboard', AgencyDashboard)
```

### 4. Custom Notification Channels

```python
# Example of implementing a custom notification channel
from foundation.extension_points.notification_channels import BaseChannel

class AgencyAlertSystem(BaseChannel):
    def send(self, recipient, message, metadata=None):
        # Implementation to send alert through agency system
        # ...
        return success

# Register the channel
registry.register_extension('notification', 'agency_alert', AgencyAlertSystem)
```

## Data Integration

Integrating with agency-specific data sources is a critical aspect of implementation.

### 1. Configure Data Sources

In your `config/data_sources.yaml` file:

```yaml
data_sources:
  - name: agency_database
    type: database
    config:
      connection_string: "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
      table_prefix: "agency_"
  
  - name: external_api
    type: api_based
    config:
      base_url: "https://api.partner-agency.gov"
      auth_method: "bearer_token"
      token_env_var: "PARTNER_API_TOKEN"
```

### 2. Implement Data Access Layer

```python
# Example data repository implementation
from foundation.api_framework.repositories import SqlAlchemyRepository
from .models import AgencySpecificEntity

class AgencyDataRepository(SqlAlchemyRepository):
    def __init__(self):
        super().__init__(AgencySpecificEntity)
    
    def find_by_criteria(self, criteria):
        # Implement custom query logic
        return self.query.filter_by(**criteria).all()
```

### 3. Data Transformation

```python
# Example data transformation service
from foundation.core_services import BaseService

class DataTransformationService(BaseService):
    def transform_for_agency_use(self, raw_data):
        # Transform external data format to agency-specific format
        transformed = []
        for item in raw_data:
            transformed.append({
                'agency_id': item.get('external_id'),
                'timestamp': self._format_timestamp(item.get('event_time')),
                'value': self._normalize_value(item.get('reading')),
                # Additional transformations...
            })
        return transformed
    
    def _format_timestamp(self, timestamp):
        # Format conversion logic
        pass
        
    def _normalize_value(self, value):
        # Normalization logic
        pass
```

## Federation and Interoperability

Enable cross-agency data sharing and interoperability through the federation layer.

### 1. Configure Federation Settings

In your `config/federation.yaml` file:

```yaml
federation:
  agency_id: "YOUR_AGENCY_CODE"
  node_url: "https://api.your-agency.gov/federation"
  shared_datasets:
    - name: "public_dataset"
      path: "/api/v1/public-data"
      update_frequency: "daily"
      schema: "schemas/public_data_schema.json"
  
  partner_agencies:
    - agency_id: "PARTNER_AGENCY"
      node_url: "https://api.partner-agency.gov/federation"
      shared_endpoints:
        - path: "/api/v1/shared-resource"
          local_cache: true
          cache_ttl: 3600
```

### 2. Implement Federation API

```python
# Example of implementing the federation API
from foundation.federation import FederationManager, FederationAPI
from .services import AgencyDataService

class AgencyFederationAPI(FederationAPI):
    def __init__(self, data_service):
        self.data_service = data_service
    
    def get_public_dataset(self):
        # Implementation to retrieve public dataset
        return self.data_service.get_public_data()
    
    def handle_partner_request(self, request):
        # Logic to authenticate and process partner agency requests
        pass

# Initialize federation
data_service = AgencyDataService()
federation_api = AgencyFederationAPI(data_service)
federation_manager = FederationManager(federation_api)
```

### 3. Query Federated Data

```python
# Example of querying federated data
from foundation.federation import FederationClient

client = FederationClient()

# Query data from partner agency
partner_data = client.query("PARTNER_AGENCY", "/api/v1/shared-resource", {
    "start_date": "2023-01-01",
    "end_date": "2023-01-31"
})

# Process the federated data
processed_result = your_agency_service.process_federated_data(partner_data)
```

## Testing and Validation

Implement comprehensive testing to ensure your agency implementation meets requirements.

### 1. Unit Testing

```python
# Example unit test for an agency service
import unittest
from unittest.mock import MagicMock
from src.services import AgencyService

class TestAgencyService(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.service = AgencyService(self.repository)
    
    def test_process_data(self):
        # Arrange
        mock_data = [{"id": 1, "value": "test"}]
        self.repository.find_all.return_value = mock_data
        
        # Act
        result = self.service.process_data()
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["processed_value"], "TEST")
        self.repository.find_all.assert_called_once()
```

### 2. Integration Testing

```python
# Example integration test
import pytest
from src.app import create_app
from src.models import db as _db

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_api_endpoint(client):
    # Test the API endpoint
    response = client.get('/api/v1/agency-resources')
    assert response.status_code == 200
    data = response.get_json()
    assert 'resources' in data
    assert len(data['resources']) > 0
```

### 3. Validation Against Requirements

Create a `tests/validation/requirements_validation.py` script:

```python
import yaml
import requests
import json

def validate_against_requirements():
    # Load requirements
    with open('requirements/api_requirements.yaml', 'r') as f:
        requirements = yaml.safe_load(f)
    
    # Test each required endpoint
    base_url = "http://localhost:5000"
    results = []
    
    for req in requirements['endpoints']:
        try:
            url = f"{base_url}{req['path']}"
            response = requests.get(url)
            
            # Validate status code
            status_valid = response.status_code == req['expected_status']
            
            # Validate schema if specified
            schema_valid = True
            if 'schema' in req:
                schema_valid = validate_schema(response.json(), req['schema'])
            
            results.append({
                'endpoint': req['path'],
                'status_valid': status_valid,
                'schema_valid': schema_valid,
                'passed': status_valid and schema_valid
            })
        except Exception as e:
            results.append({
                'endpoint': req['path'],
                'error': str(e),
                'passed': False
            })
    
    # Generate validation report
    with open('validation_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return all(r['passed'] for r in results)

def validate_schema(data, schema_path):
    # Implementation of schema validation
    pass

if __name__ == "__main__":
    success = validate_against_requirements()
    exit(0 if success else 1)
```

## Deployment

Guidelines for deploying your agency implementation to various environments.

### 1. Environment Configuration

Create environment-specific configuration files:

```bash
# Create environment configuration files
mkdir -p config/environments
touch config/environments/development.env
touch config/environments/staging.env
touch config/environments/production.env
```

Example production environment configuration:

```
ENVIRONMENT=production
LOG_LEVEL=INFO
DB_CONNECTION_STRING=postgresql://user:password@production-db:5432/agency_db
API_BASE_URL=https://api.your-agency.gov
HMS_REGISTRY_URL=https://registry.hms-gov.org
ENABLE_FEDERATION=true
```

### 2. Containerization

Create a production-ready Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Expose port
EXPOSE 5000

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.app:create_app()"]
```

### 3. Deployment Script

Create a `scripts/deploy.sh` script:

```bash
#!/bin/bash
set -e

# Usage: ./deploy.sh <environment>
environment=${1:-development}

echo "Deploying to ${environment} environment..."

# Load environment variables
set -a
source config/environments/${environment}.env
set +a

# Build the Docker image
docker build -t agency-implementation:${environment} .

# Tag the image
docker tag agency-implementation:${environment} registry.your-agency.gov/agency-implementation:${environment}

# Push to registry
docker push registry.your-agency.gov/agency-implementation:${environment}

# Apply Kubernetes manifests
kubectl apply -f k8s/${environment}/

echo "Deployment completed successfully!"
```

### 4. Kubernetes Configuration

Example Kubernetes deployment manifest (`k8s/production/deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agency-implementation
  namespace: your-agency
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agency-implementation
  template:
    metadata:
      labels:
        app: agency-implementation
    spec:
      containers:
      - name: agency-implementation
        image: registry.your-agency.gov/agency-implementation:production
        ports:
        - containerPort: 5000
        env:
        - name: ENVIRONMENT
          value: production
        # Additional environment variables
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Maintenance and Updates

Guidelines for maintaining and updating your agency implementation over time.

### 1. Backup Strategy

Create a backup strategy in `scripts/backup.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./backup.sh <environment>
environment=${1:-production}

# Set variables
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="backups/${timestamp}_${environment}"

# Create backup directory
mkdir -p ${backup_dir}

# Backup database
echo "Backing up database..."
pg_dump -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -f ${backup_dir}/database.sql

# Backup configuration
echo "Backing up configuration..."
cp config/environments/${environment}.env ${backup_dir}/
cp config/*.yaml ${backup_dir}/

# Backup logs
echo "Backing up logs..."
cp -r logs/* ${backup_dir}/logs/

# Compress backup
tar -czf ${backup_dir}.tar.gz ${backup_dir}
rm -rf ${backup_dir}

echo "Backup completed: ${backup_dir}.tar.gz"
```

### 2. Update Process

Create an update script in `scripts/update.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./update.sh <environment>
environment=${1:-development}

echo "Updating agency implementation in ${environment}..."

# Pull latest changes
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python scripts/migrate.py ${environment}

# Run tests
python -m pytest

# Rebuild and redeploy
./scripts/deploy.sh ${environment}

echo "Update completed successfully!"
```

### 3. Monitoring and Logging

Configure monitoring and logging in your application:

```python
# Example monitoring configuration
from foundation.utilities import logger
import prometheus_client

# Set up metrics
request_count = prometheus_client.Counter(
    'request_count', 'Count of API requests',
    ['endpoint', 'status']
)

# Start metrics server
prometheus_client.start_http_server(8000)

# Configure logging
logger.setup(
    log_level=os.environ.get('LOG_LEVEL', 'INFO'),
    log_file='/var/log/agency-implementation/app.log',
    rotate=True,
    max_size_mb=100,
    backup_count=10
)
```

### 4. Version Management

Create a version management script in `scripts/version.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./version.sh <version>
version=${1}

if [ -z "$version" ]; then
    echo "Usage: ./version.sh <version>"
    exit 1
fi

# Update version file
echo "$version" > VERSION

# Update version in application
sed -i "s/__version__ = .*/__version__ = \"$version\"/" src/__init__.py

# Commit and tag
git add VERSION src/__init__.py
git commit -m "Bump version to $version"
git tag -a "v$version" -m "Version $version"

echo "Version updated to $version"
```

## Troubleshooting

Common issues and their resolutions.

### 1. Database Connection Issues

**Problem**: Application fails to connect to the database

**Solutions**:

1. Verify database connection string in configuration:
   ```bash
   grep DB_CONNECTION_STRING config/environments/$(ENVIRONMENT).env
   ```

2. Check database server is accessible:
   ```bash
   telnet ${DB_HOST} ${DB_PORT}
   ```

3. Validate credentials:
   ```bash
   PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1"
   ```

### 2. API Integration Failures

**Problem**: External API integrations are failing

**Solutions**:

1. Verify API credentials and configuration:
   ```bash
   # Check configuration
   cat config/integrations.yaml
   
   # Test API connection
   curl -H "Authorization: Bearer ${API_TOKEN}" ${API_URL}/health
   ```

2. Enable detailed logging:
   ```python
   # In your integration service
   logger.set_level('DEBUG')
   ```

3. Implement retry logic:
   ```python
   from foundation.utilities import retry

   @retry(max_attempts=3, backoff_factor=2)
   def call_external_api(endpoint, params):
       # API call implementation
       pass
   ```

### 3. Performance Issues

**Problem**: System is responding slowly

**Solutions**:

1. Enable performance logging:
   ```python
   # Add performance logging middleware
   from foundation.api_framework.middleware import PerformanceLoggingMiddleware
   
   app.use_middleware(PerformanceLoggingMiddleware)
   ```

2. Analyze database queries:
   ```python
   # Enable query logging
   from foundation.api_framework.repositories import enable_query_logging
   
   enable_query_logging(True)
   ```

3. Implement caching:
   ```python
   # Add caching to expensive operations
   from foundation.utilities import cache
   
   @cache(ttl=3600)  # Cache for 1 hour
   def expensive_operation(params):
       # Implementation
       pass
   ```

## Advanced Topics

Advanced techniques and patterns for enhancing your agency implementation.

### 1. Implementing Event-Driven Architecture

```python
# Example of implementing event-driven patterns
from foundation.core_services import EventBus

# Initialize the event bus
event_bus = EventBus()

# Define an event handler
@event_bus.subscribe('data.updated')
def handle_data_update(event_data):
    # Handle the data update event
    agency_service.process_updated_data(event_data)

# Publish an event
event_bus.publish('data.updated', {
    'resource_id': '12345',
    'changed_fields': ['status', 'priority'],
    'timestamp': '2023-06-15T14:30:00Z'
})
```

### 2. Advanced Data Federation Patterns

```python
# Example of implementing a federated query resolver
from foundation.federation import FederatedQueryResolver

class AgencyQueryResolver(FederatedQueryResolver):
    def resolve_multi_agency_query(self, query_spec):
        # Parse the query specification
        agencies = query_spec.get('agencies', [])
        data_points = query_spec.get('data_points', [])
        time_range = query_spec.get('time_range', {})
        
        # Collect data from each agency
        results = {}
        for agency in agencies:
            agency_client = self.get_federation_client(agency)
            agency_data = agency_client.query('/api/v1/data', {
                'data_points': data_points,
                'start_date': time_range.get('start'),
                'end_date': time_range.get('end')
            })
            results[agency] = agency_data
        
        # Aggregate and normalize the results
        return self.aggregate_results(results, query_spec.get('aggregation'))
    
    def aggregate_results(self, results, aggregation_method):
        # Implementation of various aggregation methods
        # ...
        return aggregated_data
```

### 3. Implementing Custom Authentication

```python
# Example of implementing custom authentication
from foundation.api_framework.auth import BaseAuthProvider
import jwt

class AgencyJWTAuthProvider(BaseAuthProvider):
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def authenticate(self, request):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            # Decode and verify the token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Extract user information
            user_id = payload.get('sub')
            roles = payload.get('roles', [])
            
            # Return authentication context
            return {
                'user_id': user_id,
                'roles': roles,
                'authenticated': True
            }
        except jwt.PyJWTError:
            return None
    
    def generate_token(self, user_data, expiration=3600):
        # Generate a new JWT token
        payload = {
            'sub': user_data.get('user_id'),
            'roles': user_data.get('roles', []),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration)
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )
```

## Reference Implementation Examples

Study these reference implementations to understand common patterns and best practices.

### CDC Implementation Example

The CDC implementation provides an example of disease surveillance and monitoring:

```python
# Example from CDC implementation
from foundation.core_services import detection_service
from foundation.extension_points.predictive_models import disease_spread_model

class DiseaseOutbreakDetector:
    def __init__(self):
        self.detection_service = detection_service.DetectionService()
        self.prediction_model = disease_spread_model.DiseaseSpreadModel()
    
    def analyze_surveillance_data(self, surveillance_data):
        # Process surveillance data to detect potential outbreaks
        anomalies = self.detection_service.detect_anomalies(
            surveillance_data,
            baseline_period='30d',
            threshold=2.5
        )
        
        if anomalies:
            # Predict potential spread
            prediction = self.prediction_model.predict_spread(
                initial_cases=anomalies,
                region=surveillance_data['region'],
                timeframe='14d'
            )
            
            return {
                'detected_anomalies': anomalies,
                'prediction': prediction,
                'risk_level': self._calculate_risk_level(prediction)
            }
        
        return {'risk_level': 'normal'}
    
    def _calculate_risk_level(self, prediction):
        # Risk level calculation logic
        pass
```

### FEMA Implementation Example

The FEMA implementation provides an example of emergency response coordination:

```python
# Example from FEMA implementation
from foundation.core_services import notification_service
from foundation.extension_points.visualization_components import choropleth_map

class DisasterResponseCoordinator:
    def __init__(self):
        self.notification_service = notification_service.NotificationService()
        self.map_service = choropleth_map.ChoroplethMap()
    
    def coordinate_response(self, disaster_data):
        # Analyze affected areas
        affected_regions = self._analyze_affected_areas(disaster_data)
        
        # Generate response map
        response_map = self.map_service.generate({
            'regions': affected_regions,
            'color_scale': 'impact_level',
            'popup_data': ['resources_needed', 'evacuation_status']
        })
        
        # Notify relevant agencies
        for region in affected_regions:
            if region['impact_level'] >= 3:  # High impact
                self.notification_service.send_alert(
                    recipients=self._get_regional_coordinators(region['id']),
                    message=f"High impact disaster in {region['name']}",
                    severity='high',
                    data={
                        'disaster_type': disaster_data['type'],
                        'impact_level': region['impact_level'],
                        'resources_needed': region['resources_needed']
                    }
                )
        
        return {
            'response_map': response_map,
            'affected_regions': affected_regions,
            'notifications_sent': len(affected_regions)
        }
    
    def _analyze_affected_areas(self, disaster_data):
        # Analysis implementation
        pass
    
    def _get_regional_coordinators(self, region_id):
        # Lookup implementation
        pass
```

## Resources and Support

### Documentation

- [HMS Foundation Component Reference](https://docs.hms-gov.org/foundation)
- [API Reference](https://api.hms-gov.org/docs)
- [Implementation Guidelines](https://docs.hms-gov.org/guidelines)
- [Security Best Practices](https://docs.hms-gov.org/security)

### Support Channels

- **Email Support**: support@hms-gov.org
- **Issue Tracker**: https://github.com/hms-gov/agency-implementation/issues
- **Community Forum**: https://community.hms-gov.org

### Training Resources

- **Onboarding Workshops**: Quarterly virtual workshops for new agency implementers
- **Documentation Library**: Comprehensive documentation and examples
- **Video Tutorials**: Step-by-step implementation guides

### Contribution Guidelines

To contribute improvements to the HMS foundation components:

1. Fork the repository at https://github.com/hms-gov/foundation
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes with appropriate tests
4. Submit a pull request with a clear description of the improvements

---

This implementation guide serves as your comprehensive resource for creating, deploying, and maintaining agency-specific implementations using the HMS foundation components. Follow the step-by-step instructions, leverage the provided examples, and refer to the reference implementations to create a robust and compliant solution for your agency.

For additional assistance or to report issues with this guide, please contact support@hms-gov.org.