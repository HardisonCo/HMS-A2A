# Customization Guide

This guide provides detailed information on how to customize the Agency Implementation Framework to meet your agency's specific needs.

## Customization Principles

The customization of the framework follows these principles:

1. **Extension over Modification**: Always extend the base components rather than modifying them
2. **Clear Extension Points**: Use the defined extension points for customization
3. **Consistent Patterns**: Follow consistent patterns for customization
4. **Documentation**: Document all customizations clearly
5. **Testability**: Ensure all customizations are testable

## Customization Areas

The framework can be customized in the following areas:

1. [Data Models](#data-model-customization)
2. [Business Logic](#business-logic-customization)
3. [API Endpoints](#api-customization)
4. [Data Sources](#data-source-customization)
5. [Notification Channels](#notification-channel-customization)
6. [Visualization Components](#visualization-customization)
7. [Predictive Models](#predictive-model-customization)
8. [Workflows](#workflow-customization)
9. [User Interface](#ui-customization)
10. [Integration Points](#integration-customization)

## Data Model Customization

### Extending Base Models

To extend a base model with agency-specific fields:

```rust
// Rust implementation
use crate::foundation::base_models::Sample;

/// Agency-specific sample model extending the base Sample model
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgencySample {
    /// Base sample fields
    #[serde(flatten)]
    base: Sample,
    
    /// Agency-specific fields
    #[serde(skip_serializing_if = "Option::is_none")]
    agency_id: Option<String>,
    
    #[serde(skip_serializing_if = "Option::is_none")]
    regulatory_status: Option<String>,
    
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    custom_attributes: Vec<CustomAttribute>,
}
```

```python
# Python implementation
from pydantic import BaseModel, Field
from typing import Optional, List
from agency_implementation.foundation.base_models import Sample

class CustomAttribute(BaseModel):
    """Custom attribute model for agency-specific attributes."""
    name: str
    value: str
    category: Optional[str] = None

class AgencySample(BaseModel):
    """Agency-specific sample model extending the base Sample model."""
    # Base sample fields
    base: Sample
    
    # Agency-specific fields
    agency_id: Optional[str] = None
    regulatory_status: Optional[str] = None
    custom_attributes: List[CustomAttribute] = Field(default_factory=list)
```

### Adding Relationships

To add relationships between agency-specific models:

```rust
// Rust implementation
use crate::foundation::base_models::Sample;

/// Agency-specific sample group model
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SampleGroup {
    id: String,
    name: String,
    description: Option<String>,
    
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    samples: Vec<AgencySample>,
}
```

```python
# Python implementation
from pydantic import BaseModel, Field
from typing import Optional, List
from .agency_sample import AgencySample

class SampleGroup(BaseModel):
    """Agency-specific sample group model."""
    id: str
    name: str
    description: Optional[str] = None
    samples: List[AgencySample] = Field(default_factory=list)
```

### Custom Validation

To add custom validation for agency-specific requirements:

```rust
// Rust implementation
impl AgencySample {
    pub fn validate(&self) -> Result<(), ValidationError> {
        // Validate base sample
        self.base.validate()?;
        
        // Agency-specific validation
        if let Some(regulatory_status) = &self.regulatory_status {
            if !["APPROVED", "PENDING", "REJECTED"].contains(&regulatory_status.as_str()) {
                return Err(ValidationError::new("Invalid regulatory status"));
            }
        }
        
        Ok(())
    }
}
```

```python
# Python implementation
from pydantic import validator

class AgencySample(BaseModel):
    # ... fields as defined above
    
    @validator("regulatory_status")
    def validate_regulatory_status(cls, v):
        if v is not None and v not in ["APPROVED", "PENDING", "REJECTED"]:
            raise ValueError("Invalid regulatory status")
        return v
```

## Business Logic Customization

### Extending Core Services

To extend a core service with agency-specific business logic:

```rust
// Rust implementation
use crate::foundation::core_services::detection_service::DetectionService;

pub struct AgencyDetectionService {
    /// Base detection service
    base_service: DetectionService,
    
    /// Agency-specific dependencies
    regulatory_service: Box<dyn RegulatoryService>,
}

impl AgencyDetectionService {
    pub fn new(
        base_service: DetectionService,
        regulatory_service: Box<dyn RegulatoryService>,
    ) -> Self {
        Self {
            base_service,
            regulatory_service,
        }
    }
    
    pub async fn detect_outbreaks_with_regulatory(&self, region: &str, date_range: DateRange) -> Result<Vec<Outbreak>, Error> {
        // Get outbreaks from the base service
        let outbreaks = self.base_service.detect_outbreaks(region, date_range).await?;
        
        // Apply agency-specific regulatory checks
        let mut result = Vec::new();
        for outbreak in outbreaks {
            if self.regulatory_service.check_reporting_requirements(&outbreak).await? {
                result.push(outbreak);
            }
        }
        
        Ok(result)
    }
}
```

```python
# Python implementation
from agency_implementation.foundation.core_services import DetectionService
from agency_implementation.agency_specific.services import RegulatoryService
from agency_implementation.foundation.base_models import DateRange, Outbreak
from typing import List

class AgencyDetectionService:
    """Agency-specific detection service extending the base detection service."""
    
    def __init__(self, base_service: DetectionService, regulatory_service: RegulatoryService):
        self.base_service = base_service
        self.regulatory_service = regulatory_service
    
    async def detect_outbreaks_with_regulatory(self, region: str, date_range: DateRange) -> List[Outbreak]:
        """Detect outbreaks with agency-specific regulatory checks."""
        # Get outbreaks from the base service
        outbreaks = await self.base_service.detect_outbreaks(region, date_range)
        
        # Apply agency-specific regulatory checks
        result = []
        for outbreak in outbreaks:
            if await self.regulatory_service.check_reporting_requirements(outbreak):
                result.append(outbreak)
        
        return result
```

### Implementing Agency-Specific Services

To implement an agency-specific service:

```rust
// Rust implementation
pub struct RegulatoryService {
    repository: Box<dyn RegulatoryRepository>,
}

impl RegulatoryService {
    pub fn new(repository: Box<dyn RegulatoryRepository>) -> Self {
        Self { repository }
    }
    
    pub async fn check_reporting_requirements(&self, outbreak: &Outbreak) -> Result<bool, Error> {
        // Implementation of agency-specific regulatory checks
        let requirements = self.repository.get_requirements(outbreak.region()).await?;
        
        // Check if the outbreak meets the reporting requirements
        let severity_threshold = requirements.get("severity_threshold").unwrap_or(&0);
        if outbreak.severity() < *severity_threshold {
            return Ok(false);
        }
        
        Ok(true)
    }
}
```

```python
# Python implementation
from agency_implementation.agency_specific.repositories import RegulatoryRepository
from agency_implementation.foundation.base_models import Outbreak

class RegulatoryService:
    """Agency-specific service for regulatory compliance."""
    
    def __init__(self, repository: RegulatoryRepository):
        self.repository = repository
    
    async def check_reporting_requirements(self, outbreak: Outbreak) -> bool:
        """Check if the outbreak meets the reporting requirements."""
        # Implementation of agency-specific regulatory checks
        requirements = await self.repository.get_requirements(outbreak.region)
        
        # Check if the outbreak meets the reporting requirements
        severity_threshold = requirements.get("severity_threshold", 0)
        if outbreak.severity < severity_threshold:
            return False
        
        return True
```

## API Customization

### Adding Agency-Specific Endpoints

To add agency-specific API endpoints:

```rust
// Rust implementation
use crate::foundation::api_framework::BaseController;

pub struct RegulatoryController {
    service: Box<dyn RegulatoryService>,
}

impl RegulatoryController {
    pub fn new(service: Box<dyn RegulatoryService>) -> Self {
        Self { service }
    }
    
    pub async fn get_requirements(&self, req: HttpRequest) -> Result<HttpResponse, Error> {
        let region = req.match_info().get("region").unwrap();
        let requirements = self.service.get_requirements(region).await?;
        Ok(HttpResponse::Ok().json(requirements))
    }
    
    pub fn register(self, cfg: &mut web::ServiceConfig) {
        cfg.service(
            web::resource("/regulatory/requirements/{region}")
                .route(web::get().to(move |req| self.get_requirements(req)))
        );
    }
}
```

```python
# Python implementation
from fastapi import APIRouter, Depends, HTTPException
from agency_implementation.agency_specific.services import RegulatoryService
from agency_implementation.foundation.api_framework import BaseController

class RegulatoryController(BaseController):
    """Controller for agency-specific regulatory endpoints."""
    
    def __init__(self, service: RegulatoryService):
        self.service = service
    
    def register_routes(self, router: APIRouter):
        """Register routes on the provided router."""
        router.add_api_route(
            "/regulatory/requirements/{region}",
            self.get_requirements,
            methods=["GET"],
            response_model=dict
        )
    
    async def get_requirements(self, region: str):
        """Get regulatory requirements for a region."""
        try:
            return await self.service.get_requirements(region)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
```

### Customizing API Responses

To customize the API response format:

```python
# Python implementation
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from agency_implementation.foundation.api_framework import middleware

class AgencyResponseMiddleware:
    """Middleware to customize API responses for agency requirements."""
    
    async def __call__(self, request: Request, call_next):
        # Process the request and get the response
        response = await call_next(request)
        
        # Only process JSON responses
        if response.headers.get("content-type") == "application/json":
            # Get the response body
            body = [chunk async for chunk in response.body_iterator]
            response_body = b"".join(body)
            
            # Parse the JSON
            data = json.loads(response_body)
            
            # Add agency-specific metadata
            agency_response = {
                "agency": "YOUR-AGENCY-CODE",
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "status": "success",
            }
            
            # Create a new response with the modified body
            return JSONResponse(
                content=agency_response,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        
        return response

# Register the middleware in your application
app = FastAPI()
app.add_middleware(AgencyResponseMiddleware)
```

## Data Source Customization

### Creating a Custom Data Source

To create a custom data source for agency-specific data:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint
from typing import Dict, Any, List

@registry.extension("data_source", "agency_legacy_system")
class AgencyLegacyDataSource(DataSourceExtensionPoint):
    """Data source for the agency's legacy system."""
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to the legacy system."""
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 1234)
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        
        # Implement connection logic here
        # ...
        
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from the legacy system."""
        # Implement disconnection logic here
        # ...
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query the legacy system."""
        # Implement query logic here
        # ...
        
        return results
```

### Registering the Data Source

To register and use the custom data source:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry

# Register the data source
registry.discover_extensions("agency_implementation.agency_specific.data_sources")

# Use the data source
async def fetch_legacy_data():
    # Get the data source from the registry
    data_source = registry.get("data_source", "agency_legacy_system")
    
    # Connect to the data source
    await data_source.connect({
        "host": "legacy-system.agency.gov",
        "port": 5678,
        "username": "api_user",
        "password": "api_password"
    })
    
    # Query the data source
    results = await data_source.query({
        "table": "samples",
        "filters": {
            "date_range": {
                "start": "2025-01-01",
                "end": "2025-05-01"
            },
            "status": "positive"
        }
    })
    
    # Disconnect from the data source
    await data_source.disconnect()
    
    return results
```

## Notification Channel Customization

### Creating a Custom Notification Channel

To create a custom notification channel for agency-specific communication:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.notification_channels import NotificationChannelExtensionPoint
from typing import Dict, Any, List

@registry.extension("notification_channel", "agency_alert_system")
class AgencyAlertSystem(NotificationChannelExtensionPoint):
    """Notification channel for the agency's alert system."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the alert system."""
        self.api_key = config.get("api_key", "")
        self.endpoint = config.get("endpoint", "https://alerts.agency.gov/api")
        
        # Implement initialization logic here
        # ...
        
        return True
    
    async def shutdown(self) -> None:
        """Shut down the alert system."""
        # Implement shutdown logic here
        # ...
    
    async def send_notification(self, content: Dict[str, Any], recipients: List[str], options: Dict[str, Any] = None) -> bool:
        """Send a notification through the alert system."""
        # Implement notification logic here
        # ...
        
        return True
```

### Using the Custom Notification Channel

To use the custom notification channel:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry

# Register the notification channel
registry.discover_extensions("agency_implementation.agency_specific.notification_channels")

# Use the notification channel
async def send_outbreak_alert(outbreak, recipients):
    # Get the notification channel from the registry
    alert_system = registry.get("notification_channel", "agency_alert_system")
    
    # Initialize the notification channel
    await alert_system.initialize({
        "api_key": "your-api-key",
        "endpoint": "https://alerts.agency.gov/api"
    })
    
    # Send a notification
    success = await alert_system.send_notification(
        content={
            "subject": f"Outbreak Alert: {outbreak.id}",
            "severity": outbreak.severity,
            "location": outbreak.location,
            "details": outbreak.details
        },
        recipients=recipients,
        options={
            "priority": "high",
            "expiration": "24h"
        }
    )
    
    # Shut down the notification channel
    await alert_system.shutdown()
    
    return success
```

## Visualization Customization

### Creating a Custom Visualization Component

To create a custom visualization component for agency-specific visualizations:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.visualization_components import VisualizationExtensionPoint
from typing import Dict, Any

@registry.extension("visualization", "agency_regulatory_map")
class RegulatoryMapVisualization(VisualizationExtensionPoint):
    """Visualization component for regulatory compliance maps."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the visualization component."""
        self.map_style = config.get("map_style", "default")
        self.color_scheme = config.get("color_scheme", "red_yellow_green")
        
        # Implement initialization logic here
        # ...
        
        return True
    
    async def shutdown(self) -> None:
        """Shut down the visualization component."""
        # Implement shutdown logic here
        # ...
    
    async def render(self, data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Render a regulatory compliance map."""
        # Implement rendering logic here
        # ...
        
        return {
            "type": "map",
            "format": "svg",
            "content": svg_content,
            "metadata": {
                "title": options.get("title", "Regulatory Compliance Map"),
                "description": options.get("description", "")
            }
        }
```

### Using the Custom Visualization Component

To use the custom visualization component:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry

# Register the visualization component
registry.discover_extensions("agency_implementation.agency_specific.visualization_components")

# Use the visualization component
async def generate_regulatory_map(region_data):
    # Get the visualization component from the registry
    visualization = registry.get("visualization", "agency_regulatory_map")
    
    # Initialize the visualization component
    await visualization.initialize({
        "map_style": "detailed",
        "color_scheme": "blue_scale"
    })
    
    # Render the visualization
    result = await visualization.render(
        data={
            "regions": region_data
        },
        options={
            "title": "Regulatory Compliance by Region",
            "description": "Map showing compliance levels across regions",
            "include_legend": True
        }
    )
    
    # Shut down the visualization component
    await visualization.shutdown()
    
    return result
```

## Predictive Model Customization

### Creating a Custom Predictive Model

To create a custom predictive model for agency-specific predictions:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.predictive_models import PredictiveModelExtensionPoint
from typing import Dict, Any

@registry.extension("predictive_model", "agency_risk_assessment")
class AgencyRiskAssessmentModel(PredictiveModelExtensionPoint):
    """Predictive model for agency-specific risk assessment."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the predictive model."""
        self.risk_factors = config.get("risk_factors", [])
        self.weights = config.get("weights", {})
        
        # Implement initialization logic here
        # ...
        
        return True
    
    async def shutdown(self) -> None:
        """Shut down the predictive model."""
        # Implement shutdown logic here
        # ...
    
    async def train(self, training_data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Train the predictive model."""
        # Implement training logic here
        # ...
        
        return {
            "model_id": model_id,
            "metrics": {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall
            }
        }
    
    async def predict(self, input_data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate predictions using the model."""
        # Implement prediction logic here
        # ...
        
        return {
            "predictions": predictions,
            "confidence": confidence
        }
```

### Using the Custom Predictive Model

To use the custom predictive model:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry

# Register the predictive model
registry.discover_extensions("agency_implementation.agency_specific.predictive_models")

# Use the predictive model
async def assess_regional_risk(region_data):
    # Get the predictive model from the registry
    model = registry.get("predictive_model", "agency_risk_assessment")
    
    # Initialize the model
    await model.initialize({
        "risk_factors": ["population_density", "previous_outbreaks", "vaccination_rate"],
        "weights": {
            "population_density": 0.3,
            "previous_outbreaks": 0.5,
            "vaccination_rate": 0.2
        }
    })
    
    # Train the model if needed
    training_result = await model.train(
        training_data={
            "historical_data": historical_data
        },
        options={
            "validation_split": 0.2,
            "epochs": 100
        }
    )
    
    # Generate predictions
    predictions = await model.predict(
        input_data={
            "regions": region_data
        },
        options={
            "threshold": 0.7,
            "include_confidence": True
        }
    )
    
    # Shut down the model
    await model.shutdown()
    
    return predictions
```

## Workflow Customization

### Creating a Custom Workflow

To create a custom workflow for agency-specific processes:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.customization import WorkflowExtensionPoint
from typing import Dict, Any

@registry.extension("workflow", "agency_approval_workflow")
class AgencyApprovalWorkflow(WorkflowExtensionPoint):
    """Workflow for agency-specific approval processes."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the workflow."""
        self.approval_levels = config.get("approval_levels", ["reviewer", "manager", "director"])
        self.required_fields = config.get("required_fields", [])
        
        # Implement initialization logic here
        # ...
        
        return True
    
    async def shutdown(self) -> None:
        """Shut down the workflow."""
        # Implement shutdown logic here
        # ...
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the workflow."""
        # Implement workflow logic here
        # ...
        
        return {
            "workflow_id": workflow_id,
            "status": status,
            "next_steps": next_steps,
            "result": result
        }
```

### Using the Custom Workflow

To use the custom workflow:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry

# Register the workflow
registry.discover_extensions("agency_implementation.agency_specific.workflows")

# Use the workflow
async def process_sample_approval(sample, user):
    # Get the workflow from the registry
    workflow = registry.get("workflow", "agency_approval_workflow")
    
    # Initialize the workflow
    await workflow.initialize({
        "approval_levels": ["lab_tech", "lab_manager", "regulatory_officer"],
        "required_fields": ["sample_id", "test_results", "collection_date", "location"]
    })
    
    # Execute the workflow
    result = await workflow.execute(
        input_data={
            "sample": sample.dict(),
            "action": "approve",
            "notes": "Sample meets all requirements"
        },
        context={
            "user": user.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Shut down the workflow
    await workflow.shutdown()
    
    return result
```

## UI Customization

### Creating a Custom UI Component

To create a custom UI component for agency-specific interfaces:

```typescript
// TypeScript implementation
import { BaseUIComponent } from 'agency-implementation/foundation/extension-points/ui';

export interface AgencyFormConfig {
  title: string;
  fields: Array<{
    name: string;
    label: string;
    type: 'text' | 'number' | 'date' | 'select';
    required?: boolean;
    options?: string[];
  }>;
  submitLabel?: string;
  cancelLabel?: string;
}

export class AgencyFormComponent extends BaseUIComponent<AgencyFormConfig> {
  constructor() {
    super('agency_form');
  }
  
  async initialize(config: AgencyFormConfig): Promise<boolean> {
    this.config = config;
    return true;
  }
  
  async render(data: any, options?: any): Promise<string> {
    // Implement rendering logic here
    // ...
    
    return html;
  }
  
  async handleEvent(event: string, data: any): Promise<any> {
    // Implement event handling logic here
    // ...
    
    return result;
  }
}

// Register the component
registerUIComponent('agency_form', new AgencyFormComponent());
```

### Using the Custom UI Component

To use the custom UI component:

```typescript
// TypeScript implementation
import { getUIComponent } from 'agency-implementation/foundation/extension-points/ui';

// Use the UI component
async function renderSampleForm() {
  const formComponent = getUIComponent('agency_form');
  
  await formComponent.initialize({
    title: 'Sample Submission Form',
    fields: [
      {
        name: 'sample_id',
        label: 'Sample ID',
        type: 'text',
        required: true
      },
      {
        name: 'collection_date',
        label: 'Collection Date',
        type: 'date',
        required: true
      },
      {
        name: 'sample_type',
        label: 'Sample Type',
        type: 'select',
        required: true,
        options: ['Blood', 'Tissue', 'Swab', 'Other']
      },
      {
        name: 'notes',
        label: 'Notes',
        type: 'text'
      }
    ],
    submitLabel: 'Submit Sample',
    cancelLabel: 'Cancel'
  });
  
  const html = await formComponent.render(
    {
      initial_values: {
        collection_date: new Date().toISOString().split('T')[0]
      }
    },
    {
      theme: 'agency',
      mode: 'create'
    }
  );
  
  return html;
}
```

## Integration Customization

### Creating a Custom Integration

To create a custom integration for agency-specific external systems:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.integration import IntegrationExtensionPoint
from typing import Dict, Any

@registry.extension("integration", "agency_lab_system")
class AgencyLabSystemIntegration(IntegrationExtensionPoint):
    """Integration with the agency's laboratory information system."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the integration."""
        self.api_key = config.get("api_key", "")
        self.endpoint = config.get("endpoint", "https://lab.agency.gov/api")
        
        # Implement initialization logic here
        # ...
        
        return True
    
    async def shutdown(self) -> None:
        """Shut down the integration."""
        # Implement shutdown logic here
        # ...
    
    async def execute_operation(self, operation: str, data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an operation on the external system."""
        # Implement operation execution logic here
        # ...
        
        return result
```

### Using the Custom Integration

To use the custom integration:

```python
# Python implementation
from agency_implementation.foundation.extension_points import registry

# Register the integration
registry.discover_extensions("agency_implementation.agency_specific.integrations")

# Use the integration
async def submit_sample_to_lab(sample):
    # Get the integration from the registry
    lab_integration = registry.get("integration", "agency_lab_system")
    
    # Initialize the integration
    await lab_integration.initialize({
        "api_key": "your-api-key",
        "endpoint": "https://lab.agency.gov/api"
    })
    
    # Execute an operation
    result = await lab_integration.execute_operation(
        "submit_sample",
        {
            "sample_id": sample.id,
            "collection_date": sample.collection_date,
            "sample_type": sample.type,
            "location": sample.location,
            "notes": sample.notes
        },
        {
            "priority": "high",
            "notify": True
        }
    )
    
    # Shut down the integration
    await lab_integration.shutdown()
    
    return result
```

## Next Steps

Now that you understand how to customize the framework, you can:

1. Review the [Best Practices Guide](../best-practices/README.md) for recommendations on effective customization
2. Explore integration options in the [Integration Guide](../integration/README.md)
3. Review the API reference in the [API Reference](../api-reference/README.md)
4. Check the [Troubleshooting Guide](../troubleshooting/README.md) if you encounter issues