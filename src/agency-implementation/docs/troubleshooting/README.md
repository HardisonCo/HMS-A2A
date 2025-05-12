# Troubleshooting Guide

This guide provides solutions for common issues encountered when implementing and working with the Agency Implementation Framework.

## Table of Contents

- [Setup and Configuration Issues](#setup-and-configuration-issues)
- [Extension Point Issues](#extension-point-issues)
- [API Issues](#api-issues)
- [Data Model Issues](#data-model-issues)
- [Federation Issues](#federation-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Deployment Issues](#deployment-issues)
- [Common Error Messages](#common-error-messages)
- [Diagnostic Tools](#diagnostic-tools)

## Setup and Configuration Issues

### Installation Failures

**Problem**: Dependency installation fails during setup.

**Solution**:
1. Ensure you have the correct Python version (3.10+)
2. Update pip to the latest version: `pip install --upgrade pip`
3. Check for conflicting dependencies in your environment
4. Try installing with the `--verbose` flag for more information: `pip install -r requirements.txt --verbose`

**Example Error**:
```
ERROR: Could not find a version that satisfies the requirement agency-implementation==1.0.0
```

**Solution**:
- Ensure you have access to the correct package repositories
- Check that the package name is correct
- Verify that the required version exists

### Configuration Errors

**Problem**: Application fails to start due to configuration errors.

**Solution**:
1. Verify that all required configuration files exist
2. Check that configuration files are valid JSON or YAML
3. Ensure all required configuration values are provided
4. Verify environment variables are set correctly

**Example Error**:
```
ConfigurationError: Required configuration value 'agency.api.base_url' is missing
```

**Solution**:
- Check the `config/agency.json` file for the missing value
- Add the missing configuration value: `"base_url": "https://api.agency.gov"`

### Environment Setup Issues

**Problem**: Virtual environment activation or setup fails.

**Solution**:
1. Ensure you have the correct Python version installed
2. Verify that virtualenv or venv is installed: `pip install virtualenv`
3. Create a new virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

**Example Error**:
```
venv/bin/activate: No such file or directory
```

**Solution**:
- Create the virtual environment first: `python -m venv venv`
- Check that the virtual environment directory exists

## Extension Point Issues

### Extension Not Found

**Problem**: Extension point not found in registry.

**Solution**:
1. Verify that the extension is registered correctly
2. Check that the extension type and name are correct
3. Ensure the extension registration code is executed
4. Check for import errors in the extension module

**Example Error**:
```
ExtensionNotFoundError: Extension of type 'data_source' with name 'agency_legacy_system' not found
```

**Solution**:
- Add extension registration code:
```python
from agency_implementation.foundation.extension_points import registry
registry.discover_extensions("agency_implementation.agency_specific.extensions")
```

### Extension Initialization Failure

**Problem**: Extension fails to initialize.

**Solution**:
1. Check that the extension's `initialize` method is implemented correctly
2. Verify that the configuration provided to the extension is valid
3. Check for exceptions in the extension's initialization code
4. Ensure all required dependencies for the extension are available

**Example Error**:
```
ExtensionInitializationError: Failed to initialize extension 'agency_legacy_system': Connection refused
```

**Solution**:
- Check that the external system is accessible
- Verify connection parameters (hostname, port, credentials, etc.)
- Implement better error handling in the extension's `initialize` method

### Extension Method Not Implemented

**Problem**: Required extension method not implemented.

**Solution**:
1. Verify that all required methods from the extension point interface are implemented
2. Check that method signatures match the interface definition
3. Implement missing methods in the extension class

**Example Error**:
```
NotImplementedError: Method 'query' not implemented in extension 'agency_legacy_system'
```

**Solution**:
- Implement the missing method:
```python
async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Query the legacy system."""
    # Implementation goes here
    pass
```

## API Issues

### API Endpoint Not Found

**Problem**: API endpoint returns 404 Not Found.

**Solution**:
1. Verify that the endpoint is registered correctly
2. Check that the URL pattern is correct
3. Ensure the controller is initialized and routes are registered
4. Verify that the application is running on the expected host and port

**Example Error**:
```
HTTP 404: Not Found
```

**Solution**:
- Check route registration in the controller:
```python
def register_routes(self, router: APIRouter):
    router.add_api_route(
        "/entities/{entity_id}",
        self.get_entity,
        methods=["GET"]
    )
```

### API Authorization Failure

**Problem**: API endpoint returns 401 Unauthorized or 403 Forbidden.

**Solution**:
1. Verify that authentication credentials are provided correctly
2. Check that the user has the required permissions
3. Ensure the authentication middleware is configured correctly
4. Verify that the token or credentials are valid and not expired

**Example Error**:
```
HTTP 401: Unauthorized
```

**Solution**:
- Check authentication configuration
- Verify token validity
- Ensure proper authentication headers are included in the request

### API Validation Error

**Problem**: API endpoint returns 400 Bad Request due to validation errors.

**Solution**:
1. Check the request payload against the API schema
2. Verify that all required fields are provided
3. Ensure field values match the expected formats and constraints
4. Check for detailed validation error messages in the response

**Example Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "sample_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution**:
- Add the missing field to the request payload: `"sample_id": "SAMPLE-123"`

## Data Model Issues

### Validation Errors

**Problem**: Data model validation fails.

**Solution**:
1. Check that all required fields are provided
2. Verify that field values match the expected formats and constraints
3. Ensure relationships are valid
4. Check for detailed validation error messages

**Example Error**:
```
ValidationError: 1 validation error for AgencySample
regulatory_status
  Invalid regulatory status (type=value_error)
```

**Solution**:
- Provide a valid value for the field: `"regulatory_status": "APPROVED"`
- Check the validator for the field:
```python
@validator("regulatory_status")
def validate_regulatory_status(cls, v):
    if v is not None and v not in ["APPROVED", "PENDING", "REJECTED"]:
        raise ValueError("Invalid regulatory status")
    return v
```

### Relationship Errors

**Problem**: Model relationships fail to load or save.

**Solution**:
1. Verify that the related entities exist
2. Check that relationship fields are correctly defined
3. Ensure relationship references are valid
4. Check for circular dependencies

**Example Error**:
```
RelationshipError: Related entity 'SampleGroup' with ID 'GROUP-123' not found
```

**Solution**:
- Create the related entity first
- Check the relationship definition in the model
- Verify that relationship references are consistent

### Serialization Errors

**Problem**: Model fails to serialize to JSON or other formats.

**Solution**:
1. Check for non-serializable fields in the model
2. Verify custom serialization methods
3. Ensure all field values can be serialized
4. Add proper serialization methods for complex types

**Example Error**:
```
TypeError: Object of type 'CustomType' is not JSON serializable
```

**Solution**:
- Add a custom serialization method for the type
- Convert non-serializable fields to serializable formats
- Exclude non-serializable fields from serialization

## Federation Issues

### Federation Connection Failures

**Problem**: Unable to connect to partner agencies.

**Solution**:
1. Verify that the partner agency endpoints are accessible
2. Check that the federation gateway is properly configured
3. Ensure that TLS certificates are valid
4. Verify network connectivity between agencies

**Example Error**:
```
FederationConnectionError: Failed to connect to partner agency 'PARTNER-AGENCY': Connection timed out
```

**Solution**:
- Check that the partner agency endpoint is correct and accessible
- Verify that the federation gateway is running
- Check network connectivity between the agencies
- Verify TLS certificate validity

### Federation Authentication Failures

**Problem**: Authentication with partner agencies fails.

**Solution**:
1. Verify that the authentication credentials are valid
2. Check that the agency is registered as a trusted partner
3. Ensure that the authentication tokens are not expired
4. Verify that the agency has the required trust level

**Example Error**:
```
FederationAuthenticationError: Authentication failed with partner agency 'PARTNER-AGENCY': Invalid token
```

**Solution**:
- Check the authentication configuration
- Verify that the agency is registered as a trusted partner
- Renew authentication tokens if expired
- Verify trust levels between agencies

### Federation Query Failures

**Problem**: Federated queries fail.

**Solution**:
1. Verify that the query is valid
2. Check that the agency has access to the requested data
3. Ensure that the query parameters are formatted correctly
4. Verify that the requested datasets are allowed for the partner agency

**Example Error**:
```
FederationQueryError: Query failed on partner agency 'PARTNER-AGENCY': Dataset 'confidential_data' not allowed
```

**Solution**:
- Check the dataset permissions in the federation configuration
- Modify the query to request only allowed datasets
- Update the federation configuration to allow access to the dataset
- Verify that the query format is correct

## Performance Issues

### Slow API Responses

**Problem**: API endpoints respond slowly.

**Solution**:
1. Identify bottlenecks in the API implementation
2. Optimize database queries
3. Implement caching for frequently accessed data
4. Use asynchronous processing for long-running operations

**Example Diagnosis**:
```
Endpoint: /samples
Response time: 3.5 seconds
Database query time: 3.2 seconds
```

**Solution**:
- Optimize the database query:
  - Add appropriate indexes
  - Limit the query results
  - Use query optimization techniques
- Implement caching for frequently accessed data

### Memory Usage Issues

**Problem**: Application uses excessive memory.

**Solution**:
1. Identify memory-intensive operations
2. Implement pagination for large result sets
3. Release resources properly after use
4. Optimize data structures and algorithms

**Example Diagnosis**:
```
Memory usage spike when loading large dataset
Peak memory usage: 1.2 GB
```

**Solution**:
- Implement pagination for large datasets
- Process data in smaller chunks
- Use generators for large data processing
- Release resources explicitly after use

### Connection Pool Exhaustion

**Problem**: Database or service connection pool is exhausted.

**Solution**:
1. Increase connection pool size
2. Reduce connection holding time
3. Implement connection timeouts
4. Add connection retry mechanisms

**Example Error**:
```
ConnectionPoolError: Connection pool exhausted, all 10 connections are in use
```

**Solution**:
- Increase the connection pool size:
```python
# PostgreSQL connection pool configuration
engine = create_engine(
    connection_string,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30
)
```
- Ensure connections are properly released
- Implement connection timeouts and retries

## Security Issues

### Authentication Failures

**Problem**: Users cannot authenticate.

**Solution**:
1. Verify that authentication credentials are correct
2. Check that the authentication service is configured properly
3. Ensure that user accounts are active
4. Verify that the authentication mechanism is working correctly

**Example Error**:
```
AuthenticationError: Invalid username or password
```

**Solution**:
- Check user credentials
- Verify authentication service configuration
- Ensure the user account is active
- Check for account lockouts or rate limiting

### Authorization Failures

**Problem**: Users cannot access resources they should have access to.

**Solution**:
1. Verify that the user has the required roles or permissions
2. Check that the authorization logic is implemented correctly
3. Ensure that role assignments are correct
4. Verify that permission checks are working correctly

**Example Error**:
```
AuthorizationError: User 'user@agency.gov' does not have permission 'samples:create'
```

**Solution**:
- Assign the required permission to the user's role
- Verify the authorization logic
- Check role assignments for the user
- Ensure permission checks are implemented correctly

### Data Leakage

**Problem**: Sensitive data is exposed in responses or logs.

**Solution**:
1. Identify sources of data leakage
2. Implement proper data filtering for responses
3. Configure logging to exclude sensitive data
4. Use data masking for sensitive fields

**Example Issue**:
```
Log message: "User authentication failed for username: user@agency.gov, password: SecureP@ss123"
```

**Solution**:
- Configure logging to exclude sensitive data:
```python
# Mask sensitive data in logs
log_record.msg = log_record.msg.replace(password, "********")
```
- Implement data filtering for API responses
- Use data masking for sensitive fields

## Deployment Issues

### Container Build Failures

**Problem**: Docker image build fails.

**Solution**:
1. Check the Dockerfile for errors
2. Verify that all required files are included in the build context
3. Ensure that build dependencies are available
4. Check for disk space or permission issues

**Example Error**:
```
Step 5/12 : RUN pip install -r requirements.txt
 ---> Running in 3a5d9f7c8b1e
ERROR: Could not find a version that satisfies the requirement agency-implementation==1.0.0
```

**Solution**:
- Verify that the requirements file is correctly included in the build context
- Check that all dependencies are available in the specified package repositories
- Update the base image to a compatible version

### Container Startup Failures

**Problem**: Container fails to start.

**Solution**:
1. Check container logs for error messages
2. Verify that required environment variables are set
3. Ensure that configuration files are correctly mounted
4. Check for permission issues with mounted volumes

**Example Error**:
```
ConfigurationError: Configuration file '/app/config/agency.json' not found
```

**Solution**:
- Check volume mounts in the Docker Compose file:
```yaml
volumes:
  - ./config:/app/config
```
- Verify that the configuration file exists
- Check permissions on the configuration file
- Ensure the file path is correct

### Service Discovery Issues

**Problem**: Services cannot discover or connect to each other.

**Solution**:
1. Verify that service hostnames are correct
2. Check that network configuration allows communication
3. Ensure services are running on the expected ports
4. Verify that service discovery mechanisms are working

**Example Error**:
```
ConnectionError: Failed to connect to database at 'db:5432': Connection refused
```

**Solution**:
- Check that the database service is running
- Verify network configuration between services
- Ensure the service hostname and port are correct
- Check for firewall or network policy issues

## Common Error Messages

### ExtensionNotFoundError

**Error**: `ExtensionNotFoundError: Extension of type 'X' with name 'Y' not found`

**Cause**: The specified extension is not registered in the extension registry.

**Solution**:
1. Register the extension explicitly:
```python
registry.register("data_source", "agency_legacy_system", AgencyLegacyDataSource())
```
2. Discover extensions in the module:
```python
registry.discover_extensions("agency_implementation.agency_specific.extensions")
```
3. Check that the extension class is decorated correctly:
```python
@registry.extension("data_source", "agency_legacy_system")
class AgencyLegacyDataSource(DataSourceExtensionPoint):
    # ...
```

### ValidationError

**Error**: `ValidationError: 1 validation error for X: Field required`

**Cause**: A required field is missing from a data model.

**Solution**:
1. Provide the required field:
```python
sample = AgencySample(
    base=base_sample,
    agency_id="AGENCY-123",
    regulatory_status="APPROVED"
)
```
2. Make the field optional in the model:
```python
class AgencySample(BaseModel):
    # ...
    agency_id: Optional[str] = None
    # ...
```

### ConfigurationError

**Error**: `ConfigurationError: Required configuration value 'X' is missing`

**Cause**: A required configuration value is missing.

**Solution**:
1. Provide the missing configuration value:
```json
{
  "agency": {
    "code": "YOUR-AGENCY-CODE",
    "api": {
      "base_url": "https://api.agency.gov"
    }
  }
}
```
2. Provide a default value in the code:
```python
api_base_url = config.get("agency", {}).get("api", {}).get("base_url", "http://localhost:8000")
```

### ConnectionError

**Error**: `ConnectionError: Failed to connect to X: Connection refused`

**Cause**: Unable to connect to a service or external system.

**Solution**:
1. Verify that the service is running
2. Check network connectivity
3. Verify hostname and port
4. Check firewall rules
5. Implement connection retry logic:
```python
for attempt in range(3):
    try:
        await connect_to_service()
        break
    except ConnectionError as e:
        if attempt == 2:  # Last attempt
            raise
        await asyncio.sleep(1)  # Wait before retry
```

### AuthenticationError

**Error**: `AuthenticationError: Invalid credentials`

**Cause**: Authentication credentials are invalid or expired.

**Solution**:
1. Verify authentication credentials
2. Renew expired tokens
3. Check authentication configuration
4. Implement proper error handling for authentication:
```python
try:
    token = await authenticate(username, password)
except AuthenticationError as e:
    logger.error(f"Authentication failed: {str(e)}")
    # Handle the authentication failure appropriately
```

## Diagnostic Tools

### Health Check Endpoints

The framework provides built-in health check endpoints to help diagnose issues:

- `/health`: Basic health check endpoint
- `/health/detailed`: Detailed health check with component status
- `/health/extensions`: Status of registered extensions

Example usage:
```bash
curl http://localhost:8000/health/detailed
```

Example response:
```json
{
  "status": "healthy",
  "components": {
    "api": {
      "status": "healthy",
      "details": {
        "uptime": "3h 42m 15s"
      }
    },
    "database": {
      "status": "healthy",
      "details": {
        "connection_pool": "10/20 connections active"
      }
    },
    "extensions": {
      "status": "healthy",
      "details": {
        "registered_extensions": 15,
        "active_extensions": 12
      }
    }
  }
}
```

### Logging

Enable detailed logging to diagnose issues:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable specific loggers
logging.getLogger('agency_implementation').setLevel(logging.DEBUG)
logging.getLogger('agency_implementation.foundation').setLevel(logging.INFO)
```

### Extension Registry Inspector

The extension registry provides methods to inspect registered extensions:

```python
from agency_implementation.foundation.extension_points import registry

# List all registered extensions
extensions = registry.list_all()
print(f"Registered extensions: {extensions}")

# Get details about a specific extension
extension_info = registry.get_info("data_source", "agency_legacy_system")
print(f"Extension info: {extension_info}")

# Check if an extension is registered
is_registered = registry.is_registered("data_source", "agency_legacy_system")
print(f"Extension registered: {is_registered}")
```

### Database Query Analyzer

For database performance issues, the framework includes a query analyzer:

```python
from agency_implementation.foundation.utilities import db_analyzer

# Analyze a specific query
analysis = await db_analyzer.analyze_query(
    "SELECT * FROM samples WHERE status = 'positive'"
)
print(f"Query analysis: {analysis}")

# Monitor all queries
await db_analyzer.start_monitoring(duration_threshold=500)  # ms
```

Example output:
```
Query analysis: {
  "execution_time": 1254,
  "rows_returned": 1500,
  "index_usage": {
    "used": false,
    "recommended_indexes": ["CREATE INDEX idx_samples_status ON samples(status)"]
  },
  "suggestions": [
    "Add an index on the status column",
    "Limit the number of rows returned",
    "Use a more specific WHERE clause"
  ]
}
```

### Extension Performance Monitor

For extension performance issues, use the extension performance monitor:

```python
from agency_implementation.foundation.utilities import extension_monitor

# Monitor a specific extension
await extension_monitor.monitor_extension("data_source", "agency_legacy_system", duration=60)  # seconds

# Get performance metrics for all extensions
metrics = extension_monitor.get_metrics()
print(f"Extension performance metrics: {metrics}")
```

Example output:
```
Extension performance metrics: {
  "data_source:agency_legacy_system": {
    "calls": 125,
    "avg_response_time": 350,
    "max_response_time": 1250,
    "errors": 3,
    "method_metrics": {
      "query": {
        "calls": 120,
        "avg_response_time": 345
      },
      "connect": {
        "calls": 5,
        "avg_response_time": 450
      }
    }
  }
}
```

### Configuration Validator

For configuration issues, use the configuration validator:

```python
from agency_implementation.foundation.utilities import config_validator

# Validate a configuration file
validation_result = config_validator.validate_file("config/agency.json")
print(f"Configuration validation: {validation_result}")

# Validate a specific configuration object
config = {
    "agency": {
        "code": "YOUR-AGENCY-CODE",
        "api": {
            "base_url": "https://api.agency.gov"
        }
    }
}
validation_result = config_validator.validate_config(config)
print(f"Configuration validation: {validation_result}")
```

Example output:
```
Configuration validation: {
  "valid": false,
  "errors": [
    {
      "path": "agency.features",
      "message": "Required field missing"
    },
    {
      "path": "datasources",
      "message": "At least one data source must be configured"
    }
  ],
  "warnings": [
    {
      "path": "agency.api.version",
      "message": "No API version specified, using default 'v1'"
    }
  ]
}
```

## Next Steps

If you are still experiencing issues after following this troubleshooting guide:

1. Check the [API Reference](../api-reference/README.md) for detailed API documentation
2. Review the [Architecture Documentation](../architecture/README.md) for a better understanding of the framework
3. Consult the [Best Practices Guide](../best-practices/README.md) for recommended approaches
4. Reach out to the agency implementation framework support team