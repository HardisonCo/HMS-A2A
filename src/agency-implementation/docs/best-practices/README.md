# Best Practices

This guide outlines best practices for implementing and maintaining agency implementations using the Agency Implementation Framework.

## Architecture Best Practices

### Layered Architecture

**DO** follow the layered architecture pattern:
- Keep presentation logic separate from business logic
- Keep business logic separate from data access
- Use dependency injection to manage dependencies

**DON'T** create circular dependencies between layers:
- Higher layers should depend on lower layers, not vice versa
- Use interfaces to break circular dependencies when necessary

### Component Design

**DO** design components with single responsibilities:
- Each component should have a clear, focused purpose
- Use composition over inheritance
- Keep components small and focused

**DON'T** create monolithic components:
- Avoid components that have multiple responsibilities
- Avoid components with too many dependencies
- Avoid components that are difficult to test in isolation

### Extension Points

**DO** use the extension points framework for customization:
- Extend the base components rather than modifying them
- Use the defined extension points for agency-specific functionality
- Follow the interface contracts defined for each extension point

**DON'T** modify the foundation layer directly:
- Avoid changes to core foundation components
- Avoid modifying the extension point interfaces
- Avoid bypassing the extension registry

## Development Best Practices

### Code Organization

**DO** organize code logically:
- Use a consistent file and directory structure
- Group related functionality together
- Use a consistent naming scheme

```
agency_implementation/
├── agency_specific/
│   ├── data_sources/
│   ├── integrations/
│   ├── models/
│   ├── notification_channels/
│   ├── predictive_models/
│   ├── services/
│   ├── visualization_components/
│   └── workflows/
├── api/
│   ├── controllers/
│   ├── middleware/
│   └── routers/
├── config/
├── tests/
└── main.py
```

**DON'T** mix concerns or create deeply nested structures:
- Avoid mixing agency-specific and core components
- Avoid excessively deep directory hierarchies
- Avoid inconsistent naming schemes

### Code Style

**DO** follow consistent coding standards:
- Use a consistent coding style throughout the codebase
- Follow language-specific best practices
- Use comments to explain complex logic or business rules

**DON'T** compromise on code readability:
- Avoid cryptic variable or function names
- Avoid overly complex or deeply nested code
- Avoid inconsistent formatting or style

### Documentation

**DO** document code thoroughly:
- Document public APIs with clear descriptions, parameters, and return values
- Document extension points with usage examples
- Document agency-specific customizations

**DON'T** rely on self-documenting code:
- Avoid undocumented APIs
- Avoid undocumented extension points
- Avoid undocumented agency-specific customizations

### Testing

**DO** test code thoroughly:
- Write unit tests for individual components
- Write integration tests for component interactions
- Write end-to-end tests for workflows

**DON'T** skip testing of critical components:
- Avoid untested business logic
- Avoid untested extension points
- Avoid untested agency-specific customizations

## Data Model Best Practices

### Base Model Extension

**DO** extend base models properly:
- Use composition to include base models in agency-specific models
- Add agency-specific fields and relationships
- Implement proper validation for agency-specific fields

**DON'T** modify base models directly:
- Avoid changing the structure of base models
- Avoid removing fields from base models
- Avoid changing the behavior of base model methods

### Relationships

**DO** define clear relationships between models:
- Use explicit relationships rather than implicit ones
- Document relationships clearly
- Ensure referential integrity for relationships

**DON'T** create overly complex relationship structures:
- Avoid circular relationships
- Avoid excessively deep relationship hierarchies
- Avoid relationships that are difficult to navigate

### Validation

**DO** implement proper validation:
- Validate all user inputs
- Validate agency-specific business rules
- Use appropriate validation techniques for the language/framework

**DON'T** assume valid input:
- Avoid trusting input without validation
- Avoid incomplete validation
- Avoid validation that can be bypassed

## API Best Practices

### API Design

**DO** design APIs following REST principles:
- Use appropriate HTTP methods for operations
- Use appropriate status codes for responses
- Use consistent URL patterns

**DON'T** create inconsistent or confusing APIs:
- Avoid using GET for operations that modify state
- Avoid using non-standard status codes
- Avoid inconsistent URL patterns

### API Documentation

**DO** document APIs thoroughly:
- Use OpenAPI/Swagger for API documentation
- Document all endpoints, parameters, and responses
- Include examples for common use cases

**DON'T** leave APIs undocumented:
- Avoid undocumented endpoints
- Avoid undocumented parameters
- Avoid undocumented response formats

### Error Handling

**DO** implement proper error handling:
- Return appropriate status codes for errors
- Include useful error messages in responses
- Log errors for debugging

**DON'T** expose internal errors to clients:
- Avoid returning stack traces in responses
- Avoid exposing internal system details in errors
- Avoid inconsistent error formats

## Extension Point Best Practices

### Extension Point Implementation

**DO** implement extension points properly:
- Implement all required methods defined in the interface
- Follow the interface contract
- Document the extension point's purpose and usage

**DON'T** deviate from the interface contract:
- Avoid changing the behavior of interface methods
- Avoid adding required parameters not in the interface
- Avoid removing functionality required by the interface

### Extension Point Registration

**DO** register extension points properly:
- Use the extension registry for registration
- Use meaningful names for extension points
- Document the registration process

**DON'T** bypass the extension registry:
- Avoid direct instantiation of extensions without registration
- Avoid duplicate registration of extensions
- Avoid global state for extensions

### Configuration

**DO** make extensions configurable:
- Use configuration to customize extension behavior
- Document configuration options and defaults
- Validate configuration values

**DON'T** hardcode configuration:
- Avoid hardcoded configuration values
- Avoid assumptions about configuration
- Avoid undocumented configuration options

## Security Best Practices

### Authentication and Authorization

**DO** implement proper authentication and authorization:
- Use strong authentication mechanisms
- Implement role-based access control
- Follow the principle of least privilege

**DON'T** rely solely on network security:
- Avoid assuming secure network access
- Avoid lack of authorization checks
- Avoid hardcoded credentials

### Data Protection

**DO** protect sensitive data:
- Encrypt data in transit using TLS
- Encrypt sensitive data at rest
- Follow appropriate data classification policies

**DON'T** expose sensitive data unnecessarily:
- Avoid logging sensitive data
- Avoid including sensitive data in error messages
- Avoid unnecessary data exposure in responses

### Input Validation

**DO** validate all inputs:
- Validate input syntax and semantics
- Sanitize inputs to prevent injection attacks
- Validate against expected formats and ranges

**DON'T** trust input without validation:
- Avoid using input directly without validation
- Avoid assuming sanitized input
- Avoid insufficient validation

## Performance Best Practices

### Efficiency

**DO** write efficient code:
- Use appropriate data structures and algorithms
- Optimize database queries
- Use caching where appropriate

**DON'T** prematurely optimize:
- Avoid optimizing without measuring performance
- Avoid complex optimizations without clear benefits
- Avoid optimizations that reduce readability or maintainability

### Scalability

**DO** design for scalability:
- Use asynchronous processing for long-running operations
- Design for horizontal scaling
- Use appropriate connection pooling and resource management

**DON'T** create bottlenecks:
- Avoid single points of failure
- Avoid excessive resource usage
- Avoid designs that do not scale horizontally

### Monitoring and Metrics

**DO** implement proper monitoring:
- Add metrics for key operations
- Implement appropriate logging
- Monitor system health and performance

**DON'T** operate blind:
- Avoid lack of monitoring
- Avoid inadequate logging
- Avoid lack of alerting for critical issues

## Federation Best Practices

### Data Sharing

**DO** follow federation best practices:
- Use the federation framework for cross-agency data sharing
- Implement proper access controls for shared data
- Document shared data schemas and formats

**DON'T** create ad-hoc federation mechanisms:
- Avoid direct database access across agency boundaries
- Avoid insecure data sharing mechanisms
- Avoid undocumented or inconsistent data formats

### Identity Federation

**DO** implement proper identity federation:
- Use the federation framework for cross-agency authentication
- Implement appropriate trust levels for partner agencies
- Use short-lived tokens for federation authentication

**DON'T** compromise on security:
- Avoid insecure authentication mechanisms
- Avoid excessive trust across agency boundaries
- Avoid long-lived or unvalidated tokens

### Audit Logging

**DO** implement comprehensive audit logging:
- Log all federation activities
- Include sufficient details in audit logs
- Protect audit logs from tampering

**DON'T** neglect audit requirements:
- Avoid inadequate audit logging
- Avoid logs that cannot be correlated across agencies
- Avoid logs that do not meet compliance requirements

## Deployment Best Practices

### Environment Configuration

**DO** use environment-specific configuration:
- Use configuration files or environment variables for configuration
- Keep sensitive configuration out of source control
- Document configuration requirements

**DON'T** hardcode environment-specific values:
- Avoid hardcoded endpoints or credentials
- Avoid environment-specific code paths
- Avoid undocumented configuration requirements

### Containerization

**DO** use containers for deployment:
- Create properly configured Docker images
- Use Docker Compose for local development
- Document container configuration and usage

**DON'T** create brittle container configurations:
- Avoid excessive or unnecessary dependencies
- Avoid hardcoded paths or configurations
- Avoid undocumented container requirements

### CI/CD

**DO** implement continuous integration and deployment:
- Automate testing and deployment
- Use environment-specific pipelines
- Implement proper quality gates

**DON'T** rely on manual processes:
- Avoid manual testing or deployment
- Avoid inconsistent deployment processes
- Avoid lack of deployment documentation

## Maintenance Best Practices

### Version Management

**DO** use proper version management:
- Use semantic versioning for releases
- Document changes between versions
- Maintain backwards compatibility when possible

**DON'T** break compatibility unnecessarily:
- Avoid breaking changes in minor or patch versions
- Avoid undocumented breaking changes
- Avoid unnecessary major version increments

### Dependency Management

**DO** manage dependencies properly:
- Pin dependency versions to avoid drift
- Regularly update dependencies for security fixes
- Document dependency requirements

**DON'T** use unstable or insecure dependencies:
- Avoid dependencies with known security issues
- Avoid dependencies that are no longer maintained
- Avoid unnecessary dependencies

### Documentation Maintenance

**DO** maintain documentation:
- Keep documentation in sync with code changes
- Document deprecated features or APIs
- Provide migration guides for breaking changes

**DON'T** let documentation drift:
- Avoid outdated documentation
- Avoid conflicting documentation
- Avoid lack of documentation for new features

## Integration Best Practices

### External System Integration

**DO** implement proper integration with external systems:
- Use the integration extension points for external system integration
- Implement proper error handling and retry logic
- Document integration requirements and configurations

**DON'T** create brittle integrations:
- Avoid hardcoded endpoints or credentials
- Avoid tight coupling with external systems
- Avoid lack of error handling or resilience

### API Integration

**DO** implement proper API integration:
- Use appropriate authentication mechanisms
- Implement proper error handling and retry logic
- Document API usage and requirements

**DON'T** create insecure or brittle API integrations:
- Avoid insecure authentication mechanisms
- Avoid lack of error handling
- Avoid undocumented API dependencies

### Message Queue Integration

**DO** implement proper message queue integration:
- Use appropriate message formats and schemas
- Implement proper error handling and dead-letter queues
- Document message formats and processing requirements

**DON'T** create brittle message queue integrations:
- Avoid undocumented message formats
- Avoid lack of error handling or dead-letter queues
- Avoid tight coupling with message queue implementation

## Example Best Practices

### Example: Model Extension

**Good Example**:
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from agency_implementation.foundation.base_models import Sample

class AgencySample(BaseModel):
    """Agency-specific sample model extending the base Sample model."""
    # Base sample fields
    base: Sample
    
    # Agency-specific fields
    agency_id: Optional[str] = None
    regulatory_status: Optional[str] = None
    
    # Validation
    @validator("regulatory_status")
    def validate_regulatory_status(cls, v):
        if v is not None and v not in ["APPROVED", "PENDING", "REJECTED"]:
            raise ValueError("Invalid regulatory status")
        return v
```

**Bad Example**:
```python
from agency_implementation.foundation.base_models import Sample

class AgencySample(Sample):  # Directly inheriting is not recommended
    """Agency-specific sample model extending the base Sample model."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agency_id = kwargs.get("agency_id")
        self.regulatory_status = kwargs.get("regulatory_status")
        
        # No validation
```

### Example: Extension Point Implementation

**Good Example**:
```python
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
        
        try:
            # Implementation details
            self.client = LegacyClient(self.host, self.port)
            await self.client.login(self.username, self.password)
            self.connected = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to legacy system: {str(e)}")
            self.connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the legacy system."""
        if hasattr(self, "client") and self.connected:
            await self.client.logout()
            self.connected = False
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query the legacy system."""
        if not hasattr(self, "client") or not self.connected:
            raise ValueError("Not connected to legacy system")
        
        try:
            table = query_params.get("table")
            filters = query_params.get("filters", {})
            
            # Implementation details
            result = await self.client.query(table, filters)
            return result
        except Exception as e:
            self.logger.error(f"Legacy system query failed: {str(e)}")
            raise
```

**Bad Example**:
```python
class AgencyLegacyDataSource:  # Not implementing the interface
    """Data source for the agency's legacy system."""
    
    def connect(self, config):  # Missing type hints
        """Connect to the legacy system."""
        self.host = config["host"]  # Will fail if host is not provided
        self.port = config["port"]
        self.username = config["username"]
        self.password = config["password"]
        
        # No error handling
        self.client = LegacyClient(self.host, self.port)
        self.client.login(self.username, self.password)  # Not async
        return True
    
    def disconnect(self):  # Not async
        """Disconnect from the legacy system."""
        self.client.logout()
    
    def query(self, query_params):  # Missing type hints, not async
        """Query the legacy system."""
        # No connection check
        table = query_params["table"]  # Will fail if table is not provided
        filters = query_params["filters"]
        
        # No error handling
        result = self.client.query(table, filters)  # Not async
        return result
```

### Example: API Controller Implementation

**Good Example**:
```python
from fastapi import APIRouter, Depends, HTTPException
from agency_implementation.agency_specific.services import AgencyService
from agency_implementation.foundation.api_framework import BaseController
from typing import List

class AgencyController(BaseController):
    """Controller for agency-specific API endpoints."""
    
    def __init__(self, service: AgencyService):
        self.service = service
    
    def register_routes(self, router: APIRouter):
        """Register routes on the provided router."""
        router.add_api_route(
            "/entities",
            self.get_entities,
            methods=["GET"],
            response_model=List[AgencyEntity],
            summary="Get all entities",
            description="Get a list of all agency entities with optional filtering."
        )
        
        router.add_api_route(
            "/entities/{entity_id}",
            self.get_entity,
            methods=["GET"],
            response_model=AgencyEntity,
            summary="Get entity by ID",
            description="Get a specific agency entity by its ID."
        )
    
    async def get_entities(self, status: str = None):
        """Get all entities with optional filtering."""
        try:
            filters = {}
            if status:
                filters["status"] = status
            
            return await self.service.get_entities(filters)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_entity(self, entity_id: str):
        """Get an entity by ID."""
        try:
            entity = await self.service.get_entity(entity_id)
            if not entity:
                raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
            return entity
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))
```

**Bad Example**:
```python
from fastapi import APIRouter, Depends, HTTPException
from agency_implementation.agency_specific.services import AgencyService

class AgencyController:  # Not extending BaseController
    """Controller for agency-specific API endpoints."""
    
    def __init__(self, service: AgencyService):
        self.service = service
    
    def register_routes(self, router: APIRouter):
        """Register routes on the provided router."""
        # No documentation, no response models
        router.add_api_route("/entities", self.get_entities, methods=["GET"])
        router.add_api_route("/entities/{entity_id}", self.get_entity, methods=["GET"])
    
    async def get_entities(self, status: str = None):
        """Get all entities with optional filtering."""
        # No error handling
        filters = {}
        if status:
            filters["status"] = status
        
        return await self.service.get_entities(filters)
    
    async def get_entity(self, entity_id: str):
        """Get an entity by ID."""
        # No error handling
        entity = await self.service.get_entity(entity_id)
        return entity  # Might return None
```

## Next Steps

Now that you understand the best practices for agency implementation, you can:

1. Review the [Architecture Documentation](../architecture/README.md) for more details on the framework architecture
2. Explore the [Customization Guide](../customization/README.md) for extension options
3. Check the [Troubleshooting Guide](../troubleshooting/README.md) if you encounter issues