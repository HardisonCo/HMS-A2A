# Extension Points Framework

The Extension Points Framework provides a standardized way for agencies to customize and extend the system without modifying core components. This approach ensures that customizations are maintainable, upgradable, and isolated from the core codebase.

## Overview

The framework defines interfaces for various types of extensions, enabling agencies to:

1. **Integrate custom data sources** - Connect to agency-specific databases, APIs, or file formats
2. **Create custom notification channels** - Implement agency-specific communication methods
3. **Add custom visualization components** - Build specialized visualizations for specific data types
4. **Implement custom predictive models** - Develop domain-specific prediction algorithms
5. **Create customized workflows** - Define agency-specific business processes
6. **Build custom UI components** - Create specialized user interfaces
7. **Integrate with external systems** - Connect to agency-specific external services

## Architecture

The framework is built on a registry-based plugin architecture:

1. **Base Extension Point Interface** - Defines the contract for all extension points
2. **Type-Specific Interfaces** - Define contracts for each extension point type
3. **Registry** - Manages registration, discovery, and lifecycle of extensions
4. **Default Implementations** - Provides standard implementations for common needs

Each extension implements a specific interface and registers itself with the central registry. The core system uses the registry to discover and instantiate extensions as needed.

## Available Extension Points

### Data Sources

Data source extensions allow agencies to integrate custom data sources for disease tracking, sample analysis, and other inputs.

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint

# Register a custom data source
registry.register("data_source", "my_custom_source", MyCustomDataSource())

# Use a data source
data_source = registry.get("data_source", "my_custom_source")
results = await data_source.query({"filters": {"region": "northeast"}})
```

**Provided Implementations:**
- `FileDataSource` - For CSV, JSON, and other file-based data
- `DatabaseDataSource` - For SQL databases using SQLAlchemy, aiosqlite, or asyncpg
- `APIDataSource` - For REST and GraphQL API data sources

### Notification Channels

Notification channel extensions enable agencies to integrate custom communication methods for alerts and updates.

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.notification_channels import NotificationChannelExtensionPoint

# Send a notification
notification_channel = registry.get("notification_channel", "email")
await notification_channel.send_notification(
    {"subject": "Alert: Outbreak Detected", "html_body": "<p>Details...</p>"}, 
    ["user@example.gov"]
)
```

**Provided Implementations:**
- `EmailNotificationChannel` - For email notifications
- `SMSNotificationChannel` - For SMS text messages
- `WebhookNotificationChannel` - For integration with external notification systems

### Visualization Components

Visualization extensions allow agencies to create custom visualizations for specific data types.

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.visualization_components import VisualizationExtensionPoint

# Render a visualization
visualization = registry.get("visualization", "choropleth_map")
result = visualization.render(
    {"values": {"region1": 45, "region2": 72}},
    {"title": "Infection Rates by Region"}
)
```

**Provided Implementations:**
- `ChoroplethMapVisualization` - For geographic data visualization
- `TimeSeriesVisualization` - For temporal data visualization
- `HeatmapVisualization` - For density and correlation visualization
- `NetworkGraphVisualization` - For relationship visualization

### Predictive Models

Predictive model extensions enable agencies to implement custom algorithms for forecasting and analysis.

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.predictive_models import PredictiveModelExtensionPoint

# Train a model
model = registry.get("predictive_model", "disease_spread")
await model.train(training_data, {"validation_split": 0.2})

# Generate predictions
results = await model.predict(
    {"regions": {"region1": {"current_cases": 100, "population": 500000}}},
    {"forecast_days": 14}
)
```

**Provided Implementations:**
- `DiseaseSpreadModel` - For epidemic modeling using SIR/SEIR or ML models
- `TimeSeriesForecaster` - For general time series forecasting
- `RiskAssessmentModel` - For risk scoring and assessment
- `ClassificationModel` - For classification tasks

### Workflow Customization

Workflow extensions allow agencies to customize business processes and approval flows.

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.customization import WorkflowExtensionPoint

# Execute a workflow
workflow = registry.get("workflow", "sample_approval")
result = await workflow.execute(
    {"sample_id": "12345", "results": {"test1": "positive"}},
    {"user": "analyst1", "role": "lab_tech"}
)
```

**Provided Implementations:**
- `ApprovalWorkflow` - For multi-step review and approval processes
- `DataProcessingWorkflow` - For customizable data processing pipelines

### UI Components

UI extension points enable agencies to create custom interface elements.

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.customization import UIExtensionPoint

# Render a UI component
ui_component = registry.get("ui", "custom_form")
result = ui_component.render(
    {"fields": [{"name": "location", "type": "text"}]},
    {"theme": "agency", "mode": "edit"}
)
```

**Provided Implementations:**
- `CustomFormComponent` - For dynamic form generation
- `DashboardWidgetComponent` - For dashboard components

### External System Integration

Integration extensions allow agencies to connect to external systems and services.

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.integration import IntegrationExtensionPoint

# Use an integration
integration = registry.get("integration", "external_lab")
result = await integration.execute_operation(
    "submit_sample",
    {"sample_id": "12345", "type": "avian", "collection_date": "2025-05-01"},
    {"source": "field_collection"}
)
```

**Provided Implementations:**
- `RestAPIIntegration` - For REST API integrations
- `DatabaseIntegration` - For external database integrations
- `FileSystemIntegration` - For file system integrations
- `MessagingIntegration` - For message queue integrations

## Creating Custom Extensions

To create a custom extension:

1. **Identify the appropriate extension point type** that matches your customization needs
2. **Create a class that implements the interface** of that extension point
3. **Decorate your class with `@BaseExtensionPoint.extension_point`** to define its type and name
4. **Implement all required methods** defined in the interface
5. **Register your extension** with the central registry

### Example: Custom Data Source

```python
from agency_implementation.foundation.extension_points import base
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint

@base.BaseExtensionPoint.extension_point("data_source", "my_agency_db")
class MyAgencyDataSource(DataSourceExtensionPoint):
    """Custom data source for My Agency's database."""
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        # Implementation here
        pass
    
    async def disconnect(self) -> None:
        # Implementation here
        pass
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implementation here
        pass
    
    # Implement other required methods...
```

### Example: Usage in Core System

```python
from agency_implementation.foundation.extension_points import registry

# Get all available data sources
data_sources = registry.get_all("data_source")

# Initialize a specific data source
data_source = registry.get("data_source", "my_agency_db")
await data_source.connect({"connection_string": "..."})

# Use the data source
results = await data_source.query({"filters": {"status": "active"}})
```

## Extension Discovery

The framework supports automatic discovery of extensions in specified packages:

```python
from agency_implementation.foundation.extension_points import registry

# Discover extensions in a package
registry.discover_extensions("agency_implementation.agency_custom_extensions")
```

## Best Practices

1. **Keep extensions focused** - Each extension should have a single responsibility
2. **Validate inputs and handle errors** - Don't assume valid inputs
3. **Document your extensions** - Include purpose, configuration options, and examples
4. **Test extensions independently** - Create unit tests for your extensions
5. **Use async where appropriate** - Most extension points use async methods for better performance
6. **Follow the interface contract** - Implement all required methods
7. **Use proper typing** - Leverage Python's type hints for better code quality

## Configuration

Extensions are typically configured when initialized, allowing for flexible deployment:

```python
# Configure a data source
await data_source.connect({
    "db_type": "sqlalchemy",
    "connection_string": "postgresql+asyncpg://user:pass@localhost/mydb",
    "echo": False
})

# Configure a notification channel
await notification_channel.initialize({
    "smtp_host": "smtp.agency.gov",
    "smtp_port": 587,
    "use_tls": True,
    "default_sender": "alerts@agency.gov"
})
```

## Lifecycle Management

Extensions have a defined lifecycle that the system manages:

1. **Initialization** - Configure and prepare the extension for use
2. **Usage** - Extension performs its functions
3. **Shutdown** - Clean up resources when the extension is no longer needed

The registry ensures that extensions are properly initialized before use and cleaned up when no longer needed.

## Documentation and Support

For detailed information about specific extension points, refer to the following documentation:

- [Data Sources Documentation](./data_sources/README.md)
- [Notification Channels Documentation](./notification_channels/README.md)
- [Visualization Components Documentation](./visualization_components/README.md)
- [Predictive Models Documentation](./predictive_models/README.md)
- [Workflow Customization Documentation](./customization/README.md)
- [Integration Extensions Documentation](./integration/README.md)

For support with the Extension Points Framework, contact the system administrators or refer to the agency's support documentation.