# Agency Customization Guide

This guide provides detailed instructions for customizing the template files to create a new agency implementation that meets your specific requirements.

## Table of Contents

1. [Basic Customization](#basic-customization)
2. [Data Model Customization](#data-model-customization)
3. [Service Layer Customization](#service-layer-customization)
4. [API Customization](#api-customization)
5. [Integration Customization](#integration-customization)
6. [Configuration Customization](#configuration-customization)
7. [Testing Strategy](#testing-strategy)
8. [Documentation](#documentation)

## Basic Customization

### Agency Metadata

1. Update the `config/agency.json` file with your agency's information:
   - `agencyCode`: Your agency's unique code (e.g., "HHS", "DOJ")
   - `agencyName`: Your agency's full name
   - `description`: A brief description of your agency's purpose
   - `maintainers`: Contact information for the agency implementation maintainers
   - `dependencies`: Required and optional HMS components
   - `features`: Enabled features for your agency

2. Update the `Cargo.toml` file:
   - Replace `name = "hms-agency-template"` with `name = "hms-<agency-code>"`
   - Update the `description` field
   - Update the `authors` field

### Directory Structure

Ensure your implementation follows the standard directory structure:

```
hms-<agency-code>/
├── config/              # Configuration files
├── docs/                # Documentation
├── src/                 # Source code
│   ├── api/             # API endpoints
│   ├── integrations/    # Integration with other HMS components
│   ├── models/          # Data models
│   └── services/        # Business logic
└── tests/               # Tests
```

## Data Model Customization

### Identify Core Domain Entities

1. Start by identifying the core domain entities specific to your agency
2. For each entity, create a new model file in `src/models/`
3. Use the `AgencyEntity.rs` template as a starting point

### Customizing Entity Models

For each model:

1. Define the appropriate fields and data types
2. Implement validation rules specific to your agency's requirements
3. Add any agency-specific methods needed
4. Update the serialization/deserialization logic if needed
5. Add comprehensive tests for each model

Example for a specialized entity:

```rust
// src/models/HealthRecord.rs for a health agency
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthRecord {
    #[serde(default = "Uuid::new_v4")]
    pub id: Uuid,
    pub patient_id: String,
    pub record_type: RecordType,
    pub content: String,
    pub created_by: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RecordType {
    Diagnosis,
    Treatment,
    Medication,
    LabResult,
}

impl HealthRecord {
    // Implement agency-specific methods here
}
```

## Service Layer Customization

### Service Implementation

1. Create service traits for each domain entity
2. Implement the business logic for your agency
3. Add agency-specific processing methods
4. Ensure proper error handling
5. Add comprehensive tests

Example for a health record service:

```rust
// src/services/HealthRecordService.rs
use async_trait::async_trait;
use crate::models::HealthRecord;

#[async_trait]
pub trait HealthRecordServiceTrait: Send + Sync {
    async fn get_record(&self, id: Uuid) -> Result<Option<HealthRecord>, String>;
    async fn create_record(&self, record: HealthRecord) -> Result<HealthRecord, String>;
    async fn update_record(&self, id: Uuid, record: HealthRecord) -> Result<HealthRecord, String>;
    
    // Agency-specific methods
    async fn verify_hipaa_compliance(&self, record: &HealthRecord) -> Result<bool, String>;
}

// Implement the service
pub struct HealthRecordService {
    // Implementation details
}

#[async_trait]
impl HealthRecordServiceTrait for HealthRecordService {
    // Implement methods here
}
```

## API Customization

### API Endpoints

1. Define the API structure for your agency
2. Implement controllers for each domain entity
3. Add agency-specific endpoints
4. Ensure proper request validation and error handling
5. Add comprehensive tests

Example for health record endpoints:

```rust
// src/api/HealthRecordController.rs
pub struct HealthRecordController {
    service: Arc<dyn HealthRecordServiceTrait>,
}

impl HealthRecordController {
    pub fn routes(&self) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {
        let base_path = warp::path("api").and(warp::path("health-records"));
        
        let get_record = base_path
            .and(warp::path::param::<String>())
            .and(warp::get())
            .and_then(move |id_str: String| {
                // Implementation
            });
            
        // More routes...
        
        get_record.or(create_record).or(update_record)
    }
}
```

## Integration Customization

### HMS API Integration

1. Customize the `HmsApiIntegration.rs` template for your agency's needs
2. Add agency-specific API calls
3. Ensure proper authentication and error handling
4. Add comprehensive tests

### Additional Integrations

For agency-specific integrations:

1. Create new integration files in `src/integrations/`
2. Implement the necessary client logic
3. Add agency-specific authentication if needed
4. Ensure proper error handling
5. Add comprehensive tests

Example for a specialized integration:

```rust
// src/integrations/FdaApiIntegration.rs for a health agency
pub struct FdaApiIntegration {
    client: Client,
    base_url: String,
    api_key: String,
}

impl FdaApiIntegration {
    // Implementation
}
```

## Configuration Customization

### Environment Variables

Define the environment variables needed for your agency:

```
# Required environment variables
AGENCY_CODE=YOUR_AGENCY_CODE
AGENCY_NAME=Your Agency Name
HMS_API_URL=https://api.hms.example.com
API_KEY=your-api-key

# Optional environment variables
LOG_LEVEL=info
PORT=3000
```

### Configuration Files

Add any additional configuration files needed for your agency in the `config/` directory.

## Testing Strategy

### Unit Tests

1. Add unit tests for all models, services, and API endpoints
2. Use mocks for external dependencies
3. Test all success and error scenarios

### Integration Tests

1. Add integration tests for the entire agency implementation
2. Test integration with other HMS components
3. Use the `integration_tests` feature for these tests

Example:

```rust
#[cfg(test)]
#[cfg(feature = "integration_tests")]
mod integration_tests {
    use super::*;
    
    #[tokio::test]
    async fn test_end_to_end_flow() {
        // Implementation
    }
}
```

## Documentation

### Required Documentation

1. Update the main `README.md` with your agency-specific information
2. Create agency-specific setup instructions in `docs/setup/`
3. Document any special features or requirements in `docs/customization/`
4. Add integration documentation in `docs/integration/`

### API Documentation

Document all API endpoints with:

- Endpoint URL
- HTTP method
- Request parameters
- Request body format
- Response format
- Error responses
- Example requests and responses

Example:

```markdown
## GET /api/health-records/{id}

Retrieves a health record by its ID.

**Parameters:**
- `id` (path parameter): The UUID of the health record

**Response:**
- 200 OK: Returns the health record
- 404 Not Found: Record not found
- 500 Internal Server Error: Server error

**Example Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "patient_id": "P12345",
    "record_type": "Diagnosis",
    "content": "Patient diagnosed with...",
    "created_by": "Dr. Smith",
    "created_at": "2023-04-01T10:30:00Z",
    "updated_at": "2023-04-01T10:30:00Z"
  },
  "error": null
}
```
```