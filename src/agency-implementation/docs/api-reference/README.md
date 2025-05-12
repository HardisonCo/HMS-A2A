# API Reference

This document provides a comprehensive reference for the API components of the Agency Implementation Framework.

## Foundation API Framework

The Foundation API Framework provides the core API components used in all agency implementations.

### AppFactory

The `AppFactory` class creates and configures API applications with consistent middleware, error handling, and routing.

#### Methods

##### `create_api(config: Dict[str, Any]) -> FastAPI`

Creates and configures a FastAPI application.

**Parameters**:
- `config`: Configuration dictionary with application settings

**Returns**:
- A configured FastAPI application

**Example**:
```python
from agency_implementation.foundation.api_framework import AppFactory

app = AppFactory.create_api({
    "title": "Agency API",
    "version": "1.0.0",
    "description": "API for the agency implementation",
    "middleware": {
        "cors": {
            "allow_origins": ["https://agency.gov"],
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"]
        },
        "authentication": {
            "enabled": True,
            "jwt_secret": "your-secret-key",
            "token_expiration": 3600
        },
        "rate_limiting": {
            "enabled": True,
            "rate": 100,
            "period": 60
        }
    }
})
```

### RouterFactory

The `RouterFactory` class creates and configures API routers for specific resource types.

#### Methods

##### `create_router(resource_type: str, config: Dict[str, Any] = None) -> APIRouter`

Creates an API router for a specific resource type.

**Parameters**:
- `resource_type`: The type of resource (e.g., "samples", "outbreaks")
- `config`: Optional configuration for the router

**Returns**:
- A configured APIRouter

**Example**:
```python
from agency_implementation.foundation.api_framework import RouterFactory

router = RouterFactory.create_router("samples", {
    "prefix": "/api/v1/samples",
    "tags": ["samples"],
    "responses": {
        404: {"description": "Sample not found"},
        400: {"description": "Invalid request"}
    }
})
```

### BaseController

The `BaseController` class is the base class for all API controllers, providing common functionality.

#### Methods

##### `register_routes(router: APIRouter) -> None`

Registers routes on the provided router. This method should be implemented by subclasses.

**Parameters**:
- `router`: The APIRouter to register routes on

**Example**:
```python
from fastapi import APIRouter, Depends, HTTPException
from agency_implementation.foundation.api_framework import BaseController

class SampleController(BaseController):
    def __init__(self, service):
        self.service = service
    
    def register_routes(self, router: APIRouter) -> None:
        router.add_api_route(
            "/",
            self.get_samples,
            methods=["GET"],
            response_model=List[Sample],
            summary="Get all samples",
            description="Get a list of all samples with optional filtering."
        )
        
        router.add_api_route(
            "/{sample_id}",
            self.get_sample,
            methods=["GET"],
            response_model=Sample,
            summary="Get sample by ID",
            description="Get a specific sample by its ID."
        )
```

### Error Handling Middleware

The error handling middleware provides consistent error handling for API requests.

#### ErrorHandlingMiddleware

Middleware that catches exceptions and returns appropriate HTTP responses.

**Example**:
```python
from fastapi import FastAPI
from agency_implementation.foundation.api_framework.middleware import ErrorHandlingMiddleware

app = FastAPI()
app.add_middleware(ErrorHandlingMiddleware)
```

#### Custom Exception Types

- `APIError`: Base class for API errors
- `NotFoundError`: Resource not found error (HTTP 404)
- `ValidationError`: Request validation error (HTTP 400)
- `AuthenticationError`: Authentication error (HTTP 401)
- `AuthorizationError`: Authorization error (HTTP 403)
- `ConflictError`: Resource conflict error (HTTP 409)
- `RateLimitError`: Rate limit exceeded error (HTTP 429)
- `InternalServerError`: Internal server error (HTTP 500)

**Example**:
```python
from agency_implementation.foundation.api_framework.errors import NotFoundError

async def get_sample(sample_id: str):
    sample = await service.get_sample(sample_id)
    if not sample:
        raise NotFoundError(f"Sample with ID {sample_id} not found")
    return sample
```

### Rate Limiting Middleware

The rate limiting middleware provides protection against excessive requests.

#### RateLimitingMiddleware

Middleware that limits the rate of requests per client.

**Example**:
```python
from fastapi import FastAPI
from agency_implementation.foundation.api_framework.middleware import RateLimitingMiddleware

app = FastAPI()
app.add_middleware(RateLimitingMiddleware, rate=100, period=60)
```

## Core Services API

The Core Services API provides interfaces for the shared business logic services.

### AdaptiveSamplingService

Service for optimizing resource allocation using adaptive sampling strategies.

#### Methods

##### `optimize_sampling_plan(region: str, resources: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]`

Generates an optimized sampling plan based on available resources and constraints.

**Parameters**:
- `region`: The region to optimize sampling for
- `resources`: Available resources for sampling
- `constraints`: Constraints on the sampling plan

**Returns**:
- An optimized sampling plan

**Example**:
```python
from agency_implementation.foundation.core_services import AdaptiveSamplingService

service = AdaptiveSamplingService()
sampling_plan = await service.optimize_sampling_plan(
    region="northeast",
    resources={
        "field_teams": 5,
        "lab_capacity": 100,
        "budget": 10000
    },
    constraints={
        "min_coverage": 0.8,
        "max_travel_distance": 50,
        "priority_locations": ["location1", "location2"]
    }
)
```

### DetectionService

Service for implementing statistical methods for outbreak detection.

#### Methods

##### `detect_outbreaks(region: str, date_range: DateRange, options: Dict[str, Any] = None) -> List[Outbreak]`

Detects potential outbreaks based on surveillance data.

**Parameters**:
- `region`: The region to detect outbreaks in
- `date_range`: The date range to consider
- `options`: Optional detection parameters

**Returns**:
- A list of detected outbreaks

**Example**:
```python
from agency_implementation.foundation.core_services import DetectionService
from agency_implementation.foundation.base_models import DateRange

service = DetectionService()
outbreaks = await service.detect_outbreaks(
    region="northeast",
    date_range=DateRange(start_date="2025-01-01", end_date="2025-05-01"),
    options={
        "algorithm": "spatial_scan",
        "significance_level": 0.05,
        "min_cases": 5
    }
)
```

### PredictionService

Service for forecasting disease spread and impact.

#### Methods

##### `generate_forecast(region: str, date_range: DateRange, options: Dict[str, Any] = None) -> Dict[str, Any]`

Generates a forecast for the specified region and time period.

**Parameters**:
- `region`: The region to generate a forecast for
- `date_range`: The date range to forecast
- `options`: Optional forecasting parameters

**Returns**:
- A forecast with predictions and confidence intervals

**Example**:
```python
from agency_implementation.foundation.core_services import PredictionService
from agency_implementation.foundation.base_models import DateRange

service = PredictionService()
forecast = await service.generate_forecast(
    region="northeast",
    date_range=DateRange(start_date="2025-05-01", end_date="2025-06-01"),
    options={
        "model": "ensemble",
        "include_confidence_intervals": True,
        "confidence_level": 0.95
    }
)
```

### GeneticAnalysisService

Service for analyzing genomic data to understand changes and patterns.

#### Methods

##### `analyze_sequences(sequences: List[Dict[str, Any]], options: Dict[str, Any] = None) -> Dict[str, Any]`

Analyzes genetic sequences to identify patterns, mutations, and relationships.

**Parameters**:
- `sequences`: The genetic sequences to analyze
- `options`: Optional analysis parameters

**Returns**:
- Analysis results including patterns, mutations, and relationships

**Example**:
```python
from agency_implementation.foundation.core_services import GeneticAnalysisService

service = GeneticAnalysisService()
analysis = await service.analyze_sequences(
    sequences=[
        {"id": "SEQ-001", "data": "ATCG...", "metadata": {...}},
        {"id": "SEQ-002", "data": "ATCG...", "metadata": {...}}
    ],
    options={
        "analysis_type": "phylogenetic",
        "include_mutations": True,
        "reference_sequence": "REF-001"
    }
)
```

### TransmissionAnalysisService

Service for analyzing transmission networks and patterns.

#### Methods

##### `analyze_transmission(cases: List[Dict[str, Any]], options: Dict[str, Any] = None) -> Dict[str, Any]`

Analyzes transmission patterns among cases to identify networks and chains.

**Parameters**:
- `cases`: The cases to analyze
- `options`: Optional analysis parameters

**Returns**:
- Analysis results including transmission networks, chains, and patterns

**Example**:
```python
from agency_implementation.foundation.core_services import TransmissionAnalysisService

service = TransmissionAnalysisService()
analysis = await service.analyze_transmission(
    cases=[
        {"id": "CASE-001", "location": "LOC-001", "date": "2025-01-15", "contacts": [...]},
        {"id": "CASE-002", "location": "LOC-002", "date": "2025-01-20", "contacts": [...]}
    ],
    options={
        "analysis_type": "network",
        "time_window": 14,
        "spatial_threshold": 10
    }
)
```

### NotificationService

Service for managing multi-channel notifications with role-based content.

#### Methods

##### `send_notification(content: Dict[str, Any], recipients: List[str], options: Dict[str, Any] = None) -> Dict[str, Any]`

Sends a notification to specified recipients through configured channels.

**Parameters**:
- `content`: The content of the notification
- `recipients`: The recipients of the notification
- `options`: Optional notification parameters

**Returns**:
- Status information about the sent notification

**Example**:
```python
from agency_implementation.foundation.core_services import NotificationService

service = NotificationService()
result = await service.send_notification(
    content={
        "subject": "Outbreak Alert",
        "body": "An outbreak has been detected in the northeast region.",
        "severity": "high",
        "details": {...}
    },
    recipients=["user1@agency.gov", "user2@agency.gov"],
    options={
        "channels": ["email", "sms"],
        "priority": "high",
        "expiration": "2025-05-02T12:00:00Z"
    }
)
```

### VisualizationService

Service for generating maps, charts, and comprehensive dashboards.

#### Methods

##### `generate_visualization(data: Dict[str, Any], visualization_type: str, options: Dict[str, Any] = None) -> Dict[str, Any]`

Generates a visualization of the specified type from the provided data.

**Parameters**:
- `data`: The data to visualize
- `visualization_type`: The type of visualization to generate
- `options`: Optional visualization parameters

**Returns**:
- The generated visualization

**Example**:
```python
from agency_implementation.foundation.core_services import VisualizationService

service = VisualizationService()
visualization = await service.generate_visualization(
    data={
        "regions": {
            "region1": {"cases": 25, "population": 100000},
            "region2": {"cases": 50, "population": 200000},
            "region3": {"cases": 10, "population": 150000}
        }
    },
    visualization_type="choropleth_map",
    options={
        "title": "Case Distribution by Region",
        "color_scale": "red",
        "normalize_by_population": True,
        "include_legend": True
    }
)
```

## Extension Points API

The Extension Points API provides interfaces for agency-specific extensions.

### BaseExtensionPoint

The `BaseExtensionPoint` class is the base interface for all extension points.

#### Methods

##### `initialize(config: Dict[str, Any]) -> bool`

Initializes the extension with the provided configuration.

**Parameters**:
- `config`: Configuration for the extension

**Returns**:
- `True` if initialization was successful, `False` otherwise

##### `shutdown() -> None`

Shuts down the extension and releases resources.

**Example**:
```python
from agency_implementation.foundation.extension_points import BaseExtensionPoint

class MyExtension(BaseExtensionPoint):
    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialization logic
        return True
    
    async def shutdown(self) -> None:
        # Shutdown logic
        pass
```

### ExtensionRegistry

The `ExtensionRegistry` class manages registration, discovery, and lifecycle of extensions.

#### Methods

##### `register(extension_type: str, extension_name: str, extension: BaseExtensionPoint) -> None`

Registers an extension in the registry.

**Parameters**:
- `extension_type`: The type of the extension (e.g., "data_source", "notification_channel")
- `extension_name`: The name of the extension
- `extension`: The extension instance

##### `get(extension_type: str, extension_name: str) -> BaseExtensionPoint`

Gets an extension from the registry.

**Parameters**:
- `extension_type`: The type of the extension
- `extension_name`: The name of the extension

**Returns**:
- The extension instance

##### `discover_extensions(module_name: str) -> None`

Discovers and registers extensions in the specified module.

**Parameters**:
- `module_name`: The name of the module to discover extensions in

**Example**:
```python
from agency_implementation.foundation.extension_points import registry

# Register an extension
registry.register("data_source", "my_data_source", MyDataSource())

# Get an extension
data_source = registry.get("data_source", "my_data_source")

# Discover extensions in a module
registry.discover_extensions("agency_implementation.agency_specific.extensions")
```

### DataSourceExtensionPoint

Interface for data source extensions that connect to agency-specific data sources.

#### Methods

##### `connect(config: Dict[str, Any]) -> bool`

Connects to the data source using the provided configuration.

**Parameters**:
- `config`: Configuration for the data source connection

**Returns**:
- `True` if connection was successful, `False` otherwise

##### `disconnect() -> None`

Disconnects from the data source.

##### `query(query_params: Dict[str, Any]) -> List[Dict[str, Any]]`

Queries the data source with the provided parameters.

**Parameters**:
- `query_params`: Parameters for the query

**Returns**:
- A list of results from the query

**Example**:
```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint

class MyDataSource(DataSourceExtensionPoint):
    async def connect(self, config: Dict[str, Any]) -> bool:
        # Connection logic
        return True
    
    async def disconnect(self) -> None:
        # Disconnection logic
        pass
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Query logic
        return results

# Register the data source
registry.register("data_source", "my_data_source", MyDataSource())

# Use the data source
data_source = registry.get("data_source", "my_data_source")
await data_source.connect({"connection_string": "..."})
results = await data_source.query({"filters": {"status": "active"}})
await data_source.disconnect()
```

### NotificationChannelExtensionPoint

Interface for notification channel extensions that implement agency-specific communication methods.

#### Methods

##### `initialize(config: Dict[str, Any]) -> bool`

Initializes the notification channel with the provided configuration.

**Parameters**:
- `config`: Configuration for the notification channel

**Returns**:
- `True` if initialization was successful, `False` otherwise

##### `shutdown() -> None`

Shuts down the notification channel and releases resources.

##### `send_notification(content: Dict[str, Any], recipients: List[str], options: Dict[str, Any] = None) -> bool`

Sends a notification through the channel.

**Parameters**:
- `content`: The content of the notification
- `recipients`: The recipients of the notification
- `options`: Optional notification parameters

**Returns**:
- `True` if the notification was sent successfully, `False` otherwise

**Example**:
```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.notification_channels import NotificationChannelExtensionPoint

class MyNotificationChannel(NotificationChannelExtensionPoint):
    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialization logic
        return True
    
    async def shutdown(self) -> None:
        # Shutdown logic
        pass
    
    async def send_notification(self, content: Dict[str, Any], recipients: List[str], options: Dict[str, Any] = None) -> bool:
        # Notification logic
        return True

# Register the notification channel
registry.register("notification_channel", "my_channel", MyNotificationChannel())

# Use the notification channel
channel = registry.get("notification_channel", "my_channel")
await channel.initialize({"api_key": "..."})
success = await channel.send_notification(
    {"subject": "Alert", "body": "Alert message"},
    ["user@agency.gov"],
    {"priority": "high"}
)
await channel.shutdown()
```

### VisualizationExtensionPoint

Interface for visualization extensions that create specialized visualizations.

#### Methods

##### `initialize(config: Dict[str, Any]) -> bool`

Initializes the visualization component with the provided configuration.

**Parameters**:
- `config`: Configuration for the visualization component

**Returns**:
- `True` if initialization was successful, `False` otherwise

##### `shutdown() -> None`

Shuts down the visualization component and releases resources.

##### `render(data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]`

Renders a visualization from the provided data.

**Parameters**:
- `data`: The data to visualize
- `options`: Optional visualization parameters

**Returns**:
- The rendered visualization

**Example**:
```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.visualization_components import VisualizationExtensionPoint

class MyVisualization(VisualizationExtensionPoint):
    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialization logic
        return True
    
    async def shutdown(self) -> None:
        # Shutdown logic
        pass
    
    async def render(self, data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Rendering logic
        return {"type": "svg", "content": svg_content}

# Register the visualization
registry.register("visualization", "my_visualization", MyVisualization())

# Use the visualization
visualization = registry.get("visualization", "my_visualization")
await visualization.initialize({"theme": "dark"})
result = await visualization.render(
    {"values": {"region1": 45, "region2": 72}},
    {"title": "Values by Region"}
)
await visualization.shutdown()
```

### PredictiveModelExtensionPoint

Interface for predictive model extensions that implement agency-specific prediction algorithms.

#### Methods

##### `initialize(config: Dict[str, Any]) -> bool`

Initializes the predictive model with the provided configuration.

**Parameters**:
- `config`: Configuration for the predictive model

**Returns**:
- `True` if initialization was successful, `False` otherwise

##### `shutdown() -> None`

Shuts down the predictive model and releases resources.

##### `train(training_data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]`

Trains the predictive model with the provided data.

**Parameters**:
- `training_data`: The data to train the model with
- `options`: Optional training parameters

**Returns**:
- Information about the trained model

##### `predict(input_data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]`

Generates predictions using the model.

**Parameters**:
- `input_data`: The input data for prediction
- `options`: Optional prediction parameters

**Returns**:
- The generated predictions

**Example**:
```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.predictive_models import PredictiveModelExtensionPoint

class MyPredictiveModel(PredictiveModelExtensionPoint):
    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialization logic
        return True
    
    async def shutdown(self) -> None:
        # Shutdown logic
        pass
    
    async def train(self, training_data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Training logic
        return {"model_id": "model-123", "metrics": {"accuracy": 0.95}}
    
    async def predict(self, input_data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Prediction logic
        return {"predictions": predictions}

# Register the predictive model
registry.register("predictive_model", "my_model", MyPredictiveModel())

# Use the predictive model
model = registry.get("predictive_model", "my_model")
await model.initialize({"parameters": {...}})
training_result = await model.train({"historical_data": data}, {"epochs": 100})
predictions = await model.predict({"features": features}, {"threshold": 0.7})
await model.shutdown()
```

### WorkflowExtensionPoint

Interface for workflow extensions that define agency-specific business processes.

#### Methods

##### `initialize(config: Dict[str, Any]) -> bool`

Initializes the workflow with the provided configuration.

**Parameters**:
- `config`: Configuration for the workflow

**Returns**:
- `True` if initialization was successful, `False` otherwise

##### `shutdown() -> None`

Shuts down the workflow and releases resources.

##### `execute(input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]`

Executes the workflow with the provided data and context.

**Parameters**:
- `input_data`: The input data for the workflow
- `context`: Optional context information

**Returns**:
- The result of the workflow execution

**Example**:
```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.customization import WorkflowExtensionPoint

class MyWorkflow(WorkflowExtensionPoint):
    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialization logic
        return True
    
    async def shutdown(self) -> None:
        # Shutdown logic
        pass
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Workflow execution logic
        return {"status": "completed", "result": result}

# Register the workflow
registry.register("workflow", "my_workflow", MyWorkflow())

# Use the workflow
workflow = registry.get("workflow", "my_workflow")
await workflow.initialize({"steps": [...]})
result = await workflow.execute(
    {"data": input_data},
    {"user": current_user}
)
await workflow.shutdown()
```

### IntegrationExtensionPoint

Interface for integration extensions that connect to agency-specific external systems.

#### Methods

##### `initialize(config: Dict[str, Any]) -> bool`

Initializes the integration with the provided configuration.

**Parameters**:
- `config`: Configuration for the integration

**Returns**:
- `True` if initialization was successful, `False` otherwise

##### `shutdown() -> None`

Shuts down the integration and releases resources.

##### `execute_operation(operation: str, data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]`

Executes an operation on the external system.

**Parameters**:
- `operation`: The operation to execute
- `data`: The data for the operation
- `options`: Optional operation parameters

**Returns**:
- The result of the operation

**Example**:
```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.integration import IntegrationExtensionPoint

class MyIntegration(IntegrationExtensionPoint):
    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialization logic
        return True
    
    async def shutdown(self) -> None:
        # Shutdown logic
        pass
    
    async def execute_operation(self, operation: str, data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Operation execution logic
        return {"status": "success", "result": result}

# Register the integration
registry.register("integration", "my_integration", MyIntegration())

# Use the integration
integration = registry.get("integration", "my_integration")
await integration.initialize({"api_key": "..."})
result = await integration.execute_operation(
    "submit_sample",
    {"sample_id": "SAMPLE-123", "data": {...}},
    {"priority": "high"}
)
await integration.shutdown()
```

## Federation API

The Federation API provides interfaces for cross-agency data sharing and collaboration.

### FederationManager

The `FederationManager` class manages federation capabilities and partner relationships.

#### Methods

##### `register_partner(agency_id: str, endpoint: str, trust_level: str) -> None`

Registers a partner agency for federation.

**Parameters**:
- `agency_id`: The ID of the partner agency
- `endpoint`: The federation endpoint of the partner agency
- `trust_level`: The trust level for the partner agency

##### `query`

The query interface for federated queries.

**Methods**:
- `build()`: Creates a query builder for constructing federated queries
- `execute(query: Dict[str, Any])`: Executes a federated query

##### `sync`

The synchronization interface for data synchronization between agencies.

**Methods**:
- `create_job(target_agency: str, datasets: List[str], sync_mode: str)`: Creates a synchronization job
- `execute_job(job_id: str)`: Executes a synchronization job

**Example**:
```python
from agency_implementation.foundation.federation import FederationManager

# Initialize federation
federation = FederationManager(local_agency_id="YOUR-AGENCY-CODE")

# Register partner agencies
federation.register_partner(
    agency_id="PARTNER-AGENCY",
    endpoint="https://partner-agency.gov/federation",
    trust_level="PARTNER"
)

# Execute federated query
results = federation.query.build() \
    .select("outbreak_reports") \
    .where({"state": "WA", "date_range": "last_30_days"}) \
    .execute()

# Create and execute synchronization job
sync_job = federation.sync.create_job(
    target_agency="PARTNER-AGENCY",
    datasets=["poultry_farm_status"],
    sync_mode="incremental"
)
sync_job.execute()
```

### FederatedQueryBuilder

The `FederatedQueryBuilder` class builds federated queries across multiple agencies.

#### Methods

##### `select(dataset: str) -> FederatedQueryBuilder`

Selects a dataset to query.

**Parameters**:
- `dataset`: The name of the dataset to query

**Returns**:
- The query builder for method chaining

##### `where(filters: Dict[str, Any]) -> FederatedQueryBuilder`

Adds filters to the query.

**Parameters**:
- `filters`: The filters to apply to the query

**Returns**:
- The query builder for method chaining

##### `limit(count: int) -> FederatedQueryBuilder`

Limits the number of results.

**Parameters**:
- `count`: The maximum number of results to return

**Returns**:
- The query builder for method chaining

##### `execute() -> List[Dict[str, Any]]`

Executes the query and returns the results.

**Returns**:
- The results of the query

**Example**:
```python
from agency_implementation.foundation.federation import FederationManager

federation = FederationManager(local_agency_id="YOUR-AGENCY-CODE")

# Build and execute a query
results = federation.query.build() \
    .select("samples") \
    .where({
        "collection_date": {"$gte": "2025-01-01", "$lte": "2025-05-01"},
        "result": "positive"
    }) \
    .limit(100) \
    .execute()
```

### SyncManager

The `SyncManager` class manages data synchronization between agencies.

#### Methods

##### `create_job(target_agency: str, datasets: List[str], sync_mode: str) -> SyncJob`

Creates a synchronization job.

**Parameters**:
- `target_agency`: The ID of the target agency
- `datasets`: The datasets to synchronize
- `sync_mode`: The synchronization mode ("full" or "incremental")

**Returns**:
- A synchronization job

##### `get_job(job_id: str) -> SyncJob`

Gets a synchronization job by ID.

**Parameters**:
- `job_id`: The ID of the job

**Returns**:
- The synchronization job

##### `list_jobs() -> List[SyncJob]`

Lists all synchronization jobs.

**Returns**:
- A list of synchronization jobs

**Example**:
```python
from agency_implementation.foundation.federation import FederationManager

federation = FederationManager(local_agency_id="YOUR-AGENCY-CODE")

# Create a synchronization job
sync_job = federation.sync.create_job(
    target_agency="PARTNER-AGENCY",
    datasets=["samples", "outbreaks"],
    sync_mode="incremental"
)

# Execute the job
result = sync_job.execute()

# Get job status
status = sync_job.get_status()

# List all jobs
jobs = federation.sync.list_jobs()
```

## Next Steps

This API reference provides a comprehensive overview of the core APIs in the Agency Implementation Framework. For more detailed information on specific components or implementation examples, refer to the following resources:

1. [Architecture Documentation](../architecture/README.md) for more details on how these APIs fit together
2. [Customization Guide](../customization/README.md) for guidance on extending and customizing these APIs
3. [Best Practices Guide](../best-practices/README.md) for recommendations on using these APIs effectively