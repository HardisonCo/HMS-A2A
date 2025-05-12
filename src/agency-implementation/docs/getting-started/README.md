# Getting Started with the Agency Implementation Framework

This guide provides step-by-step instructions for setting up a new agency implementation using the Agency Implementation Framework.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or later
- Node.js 18 or later (for UI components)
- Docker and Docker Compose (for local development and testing)
- Git
- A text editor or IDE (VS Code recommended)
- Access to agency-specific requirements and configuration

## Setup Process

### 1. Create a New Implementation

Start by creating a new implementation based on the template:

```bash
# Clone the templates repository
git clone https://github.com/your-org/agency-implementation.git

# Copy the template to a new directory
cp -r agency-implementation/templates/ HMS-AGENCY

# Change to the new directory
cd HMS-AGENCY
```

### 2. Configure Environment

Set up the environment for development:

```bash
# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Node.js dependencies (if using UI components)
cd ui
npm install
cd ..
```

### 3. Update Configuration

Update the configuration files in the `config` directory:

#### Agency Configuration (config/agency.json)

```json
{
  "agency": {
    "code": "YOUR-AGENCY-CODE",
    "name": "Your Agency Name",
    "description": "Description of your agency's implementation",
    "contact_email": "contact@agency.gov",
    "api": {
      "base_url": "https://api.agency.gov",
      "version": "v1"
    },
    "features": {
      "sample_tracking": true,
      "outbreak_detection": true,
      "genetic_analysis": false,
      "visualization": true
    }
  },
  "datasources": [
    {
      "name": "primary_database",
      "type": "database",
      "connection_string": "postgresql://user:password@localhost:5432/agency_db"
    }
  ],
  "notification_channels": [
    {
      "name": "email",
      "type": "email",
      "config": {
        "smtp_host": "smtp.agency.gov",
        "smtp_port": 587,
        "use_tls": true,
        "default_sender": "notifications@agency.gov"
      }
    }
  ]
}
```

#### API Specification (config/hms-api-spec.yaml)

Review and update the API specification to match your agency's requirements:

```yaml
openapi: 3.0.0
info:
  title: HMS Agency API
  version: 1.0.0
  description: API for the HMS Agency Implementation
paths:
  /samples:
    get:
      summary: Get samples
      # ... (customize as needed)
  /outbreaks:
    get:
      summary: Get outbreaks
      # ... (customize as needed)
```

### 4. Customize Data Models

Extend the base models to include agency-specific fields and relationships:

1. Create a new file `src/models/AgencyEntity.rs` (for Rust implementations) or `src/models/agency_entity.py` (for Python implementations)

2. Define your agency-specific entity by extending the base model:

```rust
// For Rust implementation
use crate::foundation::base_models::BaseEntity;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgencyEntity {
    #[serde(flatten)]
    base: BaseEntity,
    
    // Add agency-specific fields
    agency_field1: String,
    agency_field2: i32,
    
    // Add relationships
    #[serde(skip_serializing_if = "Option::is_none")]
    related_entities: Option<Vec<RelatedEntity>>,
}
```

```python
# For Python implementation
from agency_implementation.foundation.base_models import BaseEntity
from pydantic import BaseModel, Field
from typing import Optional, List

class AgencyEntity(BaseModel):
    """Agency-specific entity extending the base entity."""
    
    # Inherit from base entity
    base: BaseEntity
    
    # Add agency-specific fields
    agency_field1: str
    agency_field2: int
    
    # Add relationships
    related_entities: Optional[List['RelatedEntity']] = None
```

### 5. Implement Agency-Specific Services

Create services to implement agency-specific business logic:

```rust
// For Rust implementation
use crate::foundation::core_services::BaseService;

pub struct AgencyService {
    // Dependencies
    repository: Box<dyn AgencyRepository>,
    notification_service: Box<dyn NotificationService>,
}

impl AgencyService {
    pub fn new(repository: Box<dyn AgencyRepository>, notification_service: Box<dyn NotificationService>) -> Self {
        Self {
            repository,
            notification_service,
        }
    }
    
    pub async fn process_entity(&self, entity_id: &str) -> Result<AgencyEntity, Error> {
        // Implementation of agency-specific business logic
        // ...
    }
}
```

```python
# For Python implementation
from agency_implementation.foundation.core_services import BaseService
from agency_implementation.repositories import AgencyRepository
from agency_implementation.services import NotificationService

class AgencyService(BaseService):
    """Service implementing agency-specific business logic."""
    
    def __init__(self, repository: AgencyRepository, notification_service: NotificationService):
        self.repository = repository
        self.notification_service = notification_service
    
    async def process_entity(self, entity_id: str) -> AgencyEntity:
        """Process an agency entity."""
        # Implementation of agency-specific business logic
        # ...
```

### 6. Implement API Controllers

Create API controllers to expose agency-specific endpoints:

```rust
// For Rust implementation
use crate::foundation::api_framework::BaseController;

pub struct AgencyController {
    service: Box<dyn AgencyService>,
}

impl AgencyController {
    pub fn new(service: Box<dyn AgencyService>) -> Self {
        Self { service }
    }
    
    pub async fn get_entity(&self, req: HttpRequest) -> Result<HttpResponse, Error> {
        let entity_id = req.match_info().get("id").unwrap();
        let entity = self.service.get_entity(entity_id).await?;
        Ok(HttpResponse::Ok().json(entity))
    }
    
    // Additional endpoint implementations
    // ...
}
```

```python
# For Python implementation
from agency_implementation.foundation.api_framework import BaseController
from agency_implementation.services import AgencyService
from fastapi import APIRouter, Depends, HTTPException

class AgencyController(BaseController):
    """Controller for agency-specific API endpoints."""
    
    def __init__(self, service: AgencyService):
        self.service = service
    
    def register_routes(self, router: APIRouter):
        """Register routes on the provided router."""
        router.add_api_route(
            "/entities/{entity_id}",
            self.get_entity,
            methods=["GET"],
            response_model=AgencyEntity
        )
        
        # Additional routes
        # ...
    
    async def get_entity(self, entity_id: str):
        """Get an entity by ID."""
        try:
            return await self.service.get_entity(entity_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
```

### 7. Configure Extensions

Configure and register any extensions required for your agency implementation:

```python
# For Python implementation
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint
from agency_implementation.foundation.extension_points.notification_channels import NotificationChannelExtensionPoint

# Create and register a custom data source
@registry.extension("data_source", "agency_specific_source")
class AgencyDataSource(DataSourceExtensionPoint):
    """Agency-specific data source implementation."""
    
    async def connect(self, config):
        # Implementation here
        pass
    
    async def query(self, query_params):
        # Implementation here
        pass
    
    # Other required methods...

# Register in the application startup
def register_extensions():
    registry.discover_extensions("your_agency_package.extensions")
```

### 8. Set Up Federation (if required)

If your agency will participate in federation with other agencies:

```python
# For Python implementation
from agency_implementation.foundation.federation import FederationManager
from agency_implementation.foundation.federation.gateway import FederationGateway

# Initialize federation
federation = FederationManager(local_agency_id="YOUR-AGENCY-CODE")

# Register partner agencies
federation.register_partner(
    agency_id="PARTNER-AGENCY",
    endpoint="https://partner-agency.gov/federation",
    trust_level="PARTNER"
)

# Configure the federation gateway
gateway = FederationGateway(federation)
```

### 9. Start the Development Server

Run the development server to test your implementation:

```bash
# For Python implementations
python src/main.py

# For Rust implementations
cargo run
```

### 10. Run Tests

Run the tests to ensure everything is working correctly:

```bash
# For Python implementations
pytest tests/

# For Rust implementations
cargo test
```

## Next Steps

Now that you have set up your agency implementation, you can:

1. Further customize the implementation following the [Customization Guide](../customization/README.md)
2. Learn about best practices in the [Best Practices Guide](../best-practices/README.md)
3. Explore integration options in the [Integration Guide](../integration/README.md)
4. Review the API reference in the [API Reference](../api-reference/README.md)

## Troubleshooting

If you encounter issues during setup, refer to the [Troubleshooting Guide](../troubleshooting/README.md) for solutions to common problems.