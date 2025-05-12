# Integration Guide

This guide provides detailed information on integrating agency implementations with other systems and components, including other agency implementations, external systems, and HMS components.

## Integration Overview

The Agency Implementation Framework is designed to facilitate seamless integration with various systems through well-defined interfaces and extension points. Integration points include:

1. **Cross-Agency Integration**: Integration with other agency implementations through the Federation Framework
2. **External System Integration**: Integration with agency-specific external systems
3. **HMS Component Integration**: Integration with other HMS components
4. **Data Source Integration**: Integration with various data sources
5. **Notification Channel Integration**: Integration with notification and communication systems
6. **API Integration**: Integration via RESTful APIs

## Cross-Agency Integration

The Federation Framework enables secure data sharing and collaboration between agency implementations.

### Setting Up Federation

To set up federation with other agencies:

1. **Configure the Federation Gateway**:

```yaml
# federation.yaml
federation:
  local_agency:
    id: "YOUR-AGENCY-CODE"
    name: "Your Agency Name"
    description: "Your agency description"
  
  gateway:
    host: "0.0.0.0"
    port: 8585
    tls:
      cert: "/path/to/cert.pem"
      key: "/path/to/key.pem"
```

2. **Initialize the Federation Manager**:

```python
from agency_implementation.foundation.federation import FederationManager
from agency_implementation.foundation.federation.gateway import FederationGateway

# Initialize federation
federation = FederationManager.from_config("config/federation.yaml")

# Or initialize programmatically
federation = FederationManager(local_agency_id="YOUR-AGENCY-CODE")

# Start the federation gateway
gateway = FederationGateway(federation)
await gateway.start()
```

### Registering Partner Agencies

To register partner agencies for federation:

```python
# Register via configuration
# federation.yaml
federation:
  # ... local agency config ...
  
  partners:
    - id: "PARTNER-AGENCY-1"
      name: "Partner Agency 1"
      endpoint: "https://partner1.agency.gov/federation"
      trust_level: "PARTNER"
      allowed_datasets: ["samples", "outbreaks"]
    
    - id: "PARTNER-AGENCY-2"
      name: "Partner Agency 2"
      endpoint: "https://partner2.agency.gov/federation"
      trust_level: "TRUSTED"
      allowed_datasets: ["surveillance_data"]

# Or register programmatically
federation.register_partner(
    agency_id="PARTNER-AGENCY-3",
    name="Partner Agency 3",
    endpoint="https://partner3.agency.gov/federation",
    trust_level="PARTNER",
    allowed_datasets=["samples", "outbreaks"]
)
```

### Executing Federated Queries

To query data across multiple agencies:

```python
# Build and execute a federated query
results = federation.query.build() \
    .select("samples") \
    .where({
        "collection_date": {"$gte": "2025-01-01", "$lte": "2025-05-01"},
        "result": "positive"
    }) \
    .include_agencies(["PARTNER-AGENCY-1", "PARTNER-AGENCY-2"]) \
    .limit(100) \
    .execute()

# Process the results
for result in results:
    print(f"Sample ID: {result['id']}, Source Agency: {result['source_agency']}")
```

### Synchronizing Data Between Agencies

To synchronize data between agencies:

```python
# Create a synchronization job
sync_job = federation.sync.create_job(
    target_agency="PARTNER-AGENCY-1",
    datasets=["outbreaks"],
    sync_mode="incremental",
    options={
        "since": "2025-01-01T00:00:00Z",
        "include_related": True
    }
)

# Execute the job
result = await sync_job.execute()

# Check the status
status = await sync_job.get_status()
print(f"Sync job status: {status}")
```

### Federation Security Considerations

When using federation, keep these security considerations in mind:

1. **TLS Configuration**: Always use valid TLS certificates for secure communication
2. **Authentication**: Implement proper authentication between federation gateways
3. **Authorization**: Use fine-grained permissions for shared datasets
4. **Audit Logging**: Enable comprehensive audit logging for all federation activities
5. **Data Classification**: Implement proper data classification for shared data

## External System Integration

The Integration Extension Point enables integration with agency-specific external systems.

### Creating an Integration Extension

To create an integration extension for an external system:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.integration import IntegrationExtensionPoint
from typing import Dict, Any

@registry.extension("integration", "external_lab_system")
class ExternalLabSystemIntegration(IntegrationExtensionPoint):
    """Integration with an external laboratory system."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the integration."""
        self.api_key = config.get("api_key", "")
        self.endpoint = config.get("endpoint", "")
        self.client = None
        
        try:
            # Initialize the client
            self.client = ExternalLabClient(self.endpoint, self.api_key)
            await self.client.connect()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize external lab integration: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shut down the integration."""
        if self.client:
            await self.client.disconnect()
    
    async def execute_operation(self, operation: str, data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an operation on the external system."""
        if not self.client:
            raise ValueError("Integration not initialized")
        
        options = options or {}
        
        try:
            if operation == "submit_sample":
                # Execute the operation
                result = await self.client.submit_sample(
                    sample_id=data.get("sample_id"),
                    sample_type=data.get("sample_type"),
                    collection_date=data.get("collection_date"),
                    metadata=data.get("metadata", {})
                )
                return {"status": "success", "result": result}
            elif operation == "get_results":
                # Execute the operation
                result = await self.client.get_results(
                    sample_id=data.get("sample_id")
                )
                return {"status": "success", "result": result}
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            self.logger.error(f"Failed to execute operation {operation}: {str(e)}")
            return {"status": "error", "error": str(e)}
```

### Using an Integration Extension

To use an integration extension:

```python
from agency_implementation.foundation.extension_points import registry

# Discover and register extensions
registry.discover_extensions("agency_implementation.agency_specific.integrations")

# Get the integration
lab_integration = registry.get("integration", "external_lab_system")

# Initialize the integration
await lab_integration.initialize({
    "api_key": "your-api-key",
    "endpoint": "https://lab.example.gov/api"
})

# Execute an operation
result = await lab_integration.execute_operation(
    "submit_sample",
    {
        "sample_id": "SAMPLE-123",
        "sample_type": "swab",
        "collection_date": "2025-05-01",
        "metadata": {
            "location": "Farm A",
            "species": "chicken"
        }
    },
    {
        "priority": "high",
        "notify_results": True
    }
)

# Check the result
if result["status"] == "success":
    print(f"Sample submitted successfully: {result['result']['confirmation_id']}")
else:
    print(f"Sample submission failed: {result['error']}")

# Shut down the integration when done
await lab_integration.shutdown()
```

## HMS Component Integration

The Agency Implementation Framework can integrate with other HMS components through standardized interfaces.

### HMS-API Integration

To integrate with the HMS-API component:

1. **Configure the HMS-API Connection**:

```yaml
# config/hms-api.yaml
hms_api:
  endpoint: "https://hms-api.example.gov"
  api_key: "your-api-key"
  version: "v1"
```

2. **Create an HMS-API Integration Extension**:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.integration import IntegrationExtensionPoint
from typing import Dict, Any
import aiohttp

@registry.extension("integration", "hms_api")
class HmsApiIntegration(IntegrationExtensionPoint):
    """Integration with the HMS-API component."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the integration."""
        self.endpoint = config.get("endpoint", "")
        self.api_key = config.get("api_key", "")
        self.version = config.get("version", "v1")
        self.session = None
        
        try:
            # Initialize the HTTP session
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize HMS-API integration: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shut down the integration."""
        if self.session:
            await self.session.close()
    
    async def execute_operation(self, operation: str, data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an operation on the HMS-API."""
        if not self.session:
            raise ValueError("Integration not initialized")
        
        options = options or {}
        base_url = f"{self.endpoint}/{self.version}"
        
        try:
            if operation == "get_data":
                # Execute the operation
                endpoint = f"{base_url}/{data.get('resource_type')}"
                params = data.get("params", {})
                
                async with self.session.get(endpoint, params=params) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return {"status": "success", "result": result}
            elif operation == "submit_data":
                # Execute the operation
                endpoint = f"{base_url}/{data.get('resource_type')}"
                payload = data.get("payload", {})
                
                async with self.session.post(endpoint, json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return {"status": "success", "result": result}
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            self.logger.error(f"Failed to execute operation {operation}: {str(e)}")
            return {"status": "error", "error": str(e)}
```

3. **Use the HMS-API Integration**:

```python
from agency_implementation.foundation.extension_points import registry

# Get the HMS-API integration
hms_api = registry.get("integration", "hms_api")

# Initialize the integration
await hms_api.initialize({
    "endpoint": "https://hms-api.example.gov",
    "api_key": "your-api-key",
    "version": "v1"
})

# Get data from HMS-API
result = await hms_api.execute_operation(
    "get_data",
    {
        "resource_type": "samples",
        "params": {
            "status": "positive",
            "date_range": "2025-01-01,2025-05-01"
        }
    }
)

# Submit data to HMS-API
result = await hms_api.execute_operation(
    "submit_data",
    {
        "resource_type": "samples",
        "payload": {
            "sample_id": "SAMPLE-123",
            "sample_type": "swab",
            "collection_date": "2025-05-01",
            "result": "positive"
        }
    }
)

# Shut down the integration when done
await hms_api.shutdown()
```

### HMS-CDF Integration

To integrate with the HMS-CDF (Collaborative Decision Framework) component:

1. **Configure the HMS-CDF Connection**:

```yaml
# config/hms-cdf.yaml
hms_cdf:
  endpoint: "https://hms-cdf.example.gov"
  api_key: "your-api-key"
  version: "v1"
```

2. **Create an HMS-CDF Integration Extension**:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.integration import IntegrationExtensionPoint
from typing import Dict, Any
import aiohttp

@registry.extension("integration", "hms_cdf")
class HmsCdfIntegration(IntegrationExtensionPoint):
    """Integration with the HMS-CDF component."""
    
    # Similar implementation to HMS-API Integration
    # ...
```

3. **Use the HMS-CDF Integration**:

```python
from agency_implementation.foundation.extension_points import registry

# Get the HMS-CDF integration
hms_cdf = registry.get("integration", "hms_cdf")

# Initialize the integration
await hms_cdf.initialize({
    "endpoint": "https://hms-cdf.example.gov",
    "api_key": "your-api-key",
    "version": "v1"
})

# Create a policy in HMS-CDF
result = await hms_cdf.execute_operation(
    "create_policy",
    {
        "policy": {
            "title": "Emergency Response Policy",
            "description": "Policy for emergency response to disease outbreaks",
            "content": "...",
            "status": "draft"
        }
    }
)

# Shut down the integration when done
await hms_cdf.shutdown()
```

## Data Source Integration

The Data Source Extension Point enables integration with various data sources.

### Database Integration

To integrate with a database:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint
from typing import Dict, Any, List
import asyncpg

@registry.extension("data_source", "postgresql_database")
class PostgreSQLDataSource(DataSourceExtensionPoint):
    """Data source for PostgreSQL databases."""
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to the database."""
        self.connection_string = config.get("connection_string", "")
        self.pool = None
        
        try:
            # Create a connection pool
            self.pool = await asyncpg.create_pool(self.connection_string)
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.pool:
            await self.pool.close()
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query the database."""
        if not self.pool:
            raise ValueError("Not connected to database")
        
        table = query_params.get("table", "")
        filters = query_params.get("filters", {})
        
        try:
            # Build the query
            query = f"SELECT * FROM {table}"
            
            # Add filters
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, dict):
                        # Handle range conditions
                        for op, val in value.items():
                            if op == "$gte":
                                conditions.append(f"{key} >= ${len(conditions) + 1}")
                            elif op == "$lte":
                                conditions.append(f"{key} <= ${len(conditions) + 1}")
                            elif op == "$eq":
                                conditions.append(f"{key} = ${len(conditions) + 1}")
                            elif op == "$ne":
                                conditions.append(f"{key} != ${len(conditions) + 1}")
                    else:
                        conditions.append(f"{key} = ${len(conditions) + 1}")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            # Execute the query
            async with self.pool.acquire() as connection:
                results = await connection.fetch(query, *filters.values())
                
                # Convert the results to dictionaries
                return [dict(result) for result in results]
        except Exception as e:
            self.logger.error(f"Database query failed: {str(e)}")
            raise
```

### API Integration

To integrate with an external API:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint
from typing import Dict, Any, List
import aiohttp

@registry.extension("data_source", "external_api")
class ExternalApiDataSource(DataSourceExtensionPoint):
    """Data source for external APIs."""
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to the API."""
        self.base_url = config.get("base_url", "")
        self.api_key = config.get("api_key", "")
        self.session = None
        
        try:
            # Create a session
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to external API: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the API."""
        if self.session:
            await self.session.close()
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query the API."""
        if not self.session:
            raise ValueError("Not connected to API")
        
        endpoint = query_params.get("endpoint", "")
        params = query_params.get("params", {})
        
        try:
            # Execute the query
            async with self.session.get(f"{self.base_url}/{endpoint}", params=params) as response:
                response.raise_for_status()
                result = await response.json()
                return result
        except Exception as e:
            self.logger.error(f"API query failed: {str(e)}")
            raise
```

### File Integration

To integrate with files:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.data_sources import DataSourceExtensionPoint
from typing import Dict, Any, List
import csv
import json
import os

@registry.extension("data_source", "file_system")
class FileSystemDataSource(DataSourceExtensionPoint):
    """Data source for files."""
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to the file system."""
        self.base_dir = config.get("base_dir", "")
        
        if not os.path.exists(self.base_dir):
            self.logger.error(f"Base directory {self.base_dir} does not exist")
            return False
        
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from the file system."""
        pass
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query the file system."""
        file_path = query_params.get("file_path", "")
        file_type = query_params.get("file_type", "")
        filters = query_params.get("filters", {})
        
        if not file_path:
            raise ValueError("No file path specified")
        
        full_path = os.path.join(self.base_dir, file_path)
        
        if not os.path.exists(full_path):
            raise ValueError(f"File {full_path} does not exist")
        
        try:
            # Read the file
            if file_type == "csv":
                # Read CSV file
                results = []
                with open(full_path, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Apply filters
                        if self._apply_filters(row, filters):
                            results.append(row)
                return results
            elif file_type == "json":
                # Read JSON file
                with open(full_path, 'r') as file:
                    data = json.load(file)
                    
                    # Handle different JSON structures
                    if isinstance(data, list):
                        # Filter list of objects
                        return [item for item in data if self._apply_filters(item, filters)]
                    elif isinstance(data, dict):
                        # Return the whole object or filter its contents
                        if "items" in data and isinstance(data["items"], list):
                            data["items"] = [item for item in data["items"] if self._apply_filters(item, filters)]
                        return [data]
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            self.logger.error(f"File query failed: {str(e)}")
            raise
    
    def _apply_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to an item."""
        if not filters:
            return True
        
        for key, value in filters.items():
            if key not in item:
                return False
            
            if isinstance(value, dict):
                # Handle range conditions
                for op, val in value.items():
                    if op == "$gte" and not item[key] >= val:
                        return False
                    elif op == "$lte" and not item[key] <= val:
                        return False
                    elif op == "$eq" and not item[key] == val:
                        return False
                    elif op == "$ne" and not item[key] != val:
                        return False
            elif item[key] != value:
                return False
        
        return True
```

## Notification Channel Integration

The Notification Channel Extension Point enables integration with various notification systems.

### Email Integration

To integrate with an email system:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.notification_channels import NotificationChannelExtensionPoint
from typing import Dict, Any, List
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@registry.extension("notification_channel", "email")
class EmailNotificationChannel(NotificationChannelExtensionPoint):
    """Notification channel for email."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the notification channel."""
        self.smtp_host = config.get("smtp_host", "localhost")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_user = config.get("smtp_user", "")
        self.smtp_password = config.get("smtp_password", "")
        self.use_tls = config.get("use_tls", True)
        self.default_sender = config.get("default_sender", "")
        
        try:
            # Test the connection
            self.smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls
            )
            await self.smtp.connect()
            
            if self.smtp_user and self.smtp_password:
                await self.smtp.login(self.smtp_user, self.smtp_password)
            
            await self.smtp.quit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize email notification channel: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shut down the notification channel."""
        pass
    
    async def send_notification(self, content: Dict[str, Any], recipients: List[str], options: Dict[str, Any] = None) -> bool:
        """Send a notification."""
        if not recipients:
            raise ValueError("No recipients specified")
        
        options = options or {}
        sender = options.get("sender", self.default_sender)
        
        if not sender:
            raise ValueError("No sender specified")
        
        try:
            # Create the email message
            message = MIMEMultipart()
            message["Subject"] = content.get("subject", "")
            message["From"] = sender
            message["To"] = ", ".join(recipients)
            
            # Add the body
            if "html_body" in content:
                message.attach(MIMEText(content["html_body"], "html"))
            elif "text_body" in content:
                message.attach(MIMEText(content["text_body"], "plain"))
            else:
                raise ValueError("No email body specified")
            
            # Connect to the SMTP server
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls
            )
            await smtp.connect()
            
            if self.smtp_user and self.smtp_password:
                await smtp.login(self.smtp_user, self.smtp_password)
            
            # Send the email
            await smtp.send_message(message)
            await smtp.quit()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False
```

### SMS Integration

To integrate with an SMS system:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.notification_channels import NotificationChannelExtensionPoint
from typing import Dict, Any, List
import aiohttp

@registry.extension("notification_channel", "sms")
class SmsNotificationChannel(NotificationChannelExtensionPoint):
    """Notification channel for SMS."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the notification channel."""
        self.api_key = config.get("api_key", "")
        self.api_url = config.get("api_url", "")
        self.default_sender = config.get("default_sender", "")
        self.session = None
        
        try:
            # Create a session
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize SMS notification channel: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shut down the notification channel."""
        if self.session:
            await self.session.close()
    
    async def send_notification(self, content: Dict[str, Any], recipients: List[str], options: Dict[str, Any] = None) -> bool:
        """Send a notification."""
        if not self.session:
            raise ValueError("Channel not initialized")
        
        if not recipients:
            raise ValueError("No recipients specified")
        
        options = options or {}
        sender = options.get("sender", self.default_sender)
        
        if not sender:
            raise ValueError("No sender specified")
        
        try:
            # Get the message body
            body = content.get("text_body", "")
            
            if not body:
                body = content.get("subject", "")
            
            if not body:
                raise ValueError("No message body specified")
            
            # Send the SMS to each recipient
            success = True
            for recipient in recipients:
                # Prepare the request
                payload = {
                    "from": sender,
                    "to": recipient,
                    "message": body
                }
                
                # Send the SMS
                async with self.session.post(self.api_url, json=payload) as response:
                    if response.status >= 400:
                        self.logger.error(f"Failed to send SMS to {recipient}: {response.status}")
                        success = False
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to send SMS notification: {str(e)}")
            return False
```

### Webhook Integration

To integrate with webhooks:

```python
from agency_implementation.foundation.extension_points import registry
from agency_implementation.foundation.extension_points.notification_channels import NotificationChannelExtensionPoint
from typing import Dict, Any, List
import aiohttp

@registry.extension("notification_channel", "webhook")
class WebhookNotificationChannel(NotificationChannelExtensionPoint):
    """Notification channel for webhooks."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the notification channel."""
        self.webhooks = config.get("webhooks", {})
        self.headers = config.get("headers", {})
        self.session = None
        
        try:
            # Create a session
            self.session = aiohttp.ClientSession(
                headers=self.headers
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize webhook notification channel: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shut down the notification channel."""
        if self.session:
            await self.session.close()
    
    async def send_notification(self, content: Dict[str, Any], recipients: List[str], options: Dict[str, Any] = None) -> bool:
        """Send a notification."""
        if not self.session:
            raise ValueError("Channel not initialized")
        
        options = options or {}
        
        try:
            # Prepare the payload
            payload = {
                "content": content,
                "recipients": recipients,
                "options": options
            }
            
            # Determine which webhooks to call
            webhook_urls = []
            
            if "webhook_id" in options:
                # Call a specific webhook
                webhook_id = options["webhook_id"]
                if webhook_id in self.webhooks:
                    webhook_urls.append(self.webhooks[webhook_id])
                else:
                    raise ValueError(f"Webhook {webhook_id} not found")
            else:
                # Call all webhooks or those specified for the recipients
                for recipient in recipients:
                    if recipient in self.webhooks:
                        webhook_urls.append(self.webhooks[recipient])
                
                if not webhook_urls and "default" in self.webhooks:
                    webhook_urls.append(self.webhooks["default"])
            
            if not webhook_urls:
                raise ValueError("No webhook URLs found")
            
            # Call the webhooks
            success = True
            for url in webhook_urls:
                async with self.session.post(url, json=payload) as response:
                    if response.status >= 400:
                        self.logger.error(f"Failed to call webhook {url}: {response.status}")
                        success = False
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {str(e)}")
            return False
```

## API Integration

The Agency Implementation Framework provides RESTful APIs that can be integrated with other systems.

### OpenAPI Documentation

The API is documented using OpenAPI Specification (OAS) 3.0:

```yaml
openapi: 3.0.0
info:
  title: Agency Implementation API
  version: 1.0.0
  description: API for the Agency Implementation
paths:
  /api/v1/samples:
    get:
      summary: Get samples
      description: Get a list of samples with optional filtering
      parameters:
        - name: status
          in: query
          description: Filter by status
          schema:
            type: string
        - name: date_range
          in: query
          description: Filter by date range (format: YYYY-MM-DD,YYYY-MM-DD)
          schema:
            type: string
      responses:
        '200':
          description: List of samples
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Sample'
    post:
      summary: Create a sample
      description: Create a new sample
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SampleInput'
      responses:
        '201':
          description: Sample created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Sample'
  /api/v1/samples/{sample_id}:
    get:
      summary: Get sample by ID
      description: Get a specific sample by its ID
      parameters:
        - name: sample_id
          in: path
          required: true
          description: ID of the sample
          schema:
            type: string
      responses:
        '200':
          description: Sample details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Sample'
        '404':
          description: Sample not found
components:
  schemas:
    Sample:
      type: object
      properties:
        id:
          type: string
        sample_type:
          type: string
        collection_date:
          type: string
          format: date
        location:
          type: string
        status:
          type: string
          enum: [pending, processing, completed]
        results:
          type: object
          additionalProperties: true
      required:
        - id
        - sample_type
        - collection_date
    SampleInput:
      type: object
      properties:
        sample_type:
          type: string
        collection_date:
          type: string
          format: date
        location:
          type: string
      required:
        - sample_type
        - collection_date
```

### API Client Implementation

To create a client for the API:

```python
import aiohttp
from typing import Dict, Any, List, Optional

class AgencyApiClient:
    """Client for the Agency Implementation API."""
    
    def __init__(self, base_url: str, api_key: str):
        """Initialize the client."""
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
    
    async def connect(self) -> None:
        """Connect to the API."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def disconnect(self) -> None:
        """Disconnect from the API."""
        if self.session:
            await self.session.close()
    
    async def get_samples(self, status: Optional[str] = None, date_range: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get samples with optional filtering."""
        if not self.session:
            raise ValueError("Client not connected")
        
        params = {}
        if status:
            params["status"] = status
        if date_range:
            params["date_range"] = date_range
        
        async with self.session.get(f"{self.base_url}/api/v1/samples", params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_sample(self, sample_id: str) -> Dict[str, Any]:
        """Get a sample by ID."""
        if not self.session:
            raise ValueError("Client not connected")
        
        async with self.session.get(f"{self.base_url}/api/v1/samples/{sample_id}") as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sample."""
        if not self.session:
            raise ValueError("Client not connected")
        
        async with self.session.post(f"{self.base_url}/api/v1/samples", json=sample) as response:
            response.raise_for_status()
            return await response.json()
```

### Using the API Client

To use the API client:

```python
# Create and connect the client
client = AgencyApiClient(
    base_url="https://agency.example.gov",
    api_key="your-api-key"
)
await client.connect()

try:
    # Get samples with filtering
    samples = await client.get_samples(
        status="positive",
        date_range="2025-01-01,2025-05-01"
    )
    
    # Get a specific sample
    sample = await client.get_sample("SAMPLE-123")
    
    # Create a new sample
    new_sample = await client.create_sample({
        "sample_type": "swab",
        "collection_date": "2025-05-01",
        "location": "Farm A"
    })
finally:
    # Disconnect the client
    await client.disconnect()
```

## Next Steps

This integration guide provides a comprehensive overview of how to integrate the Agency Implementation Framework with various systems and components. For more detailed information on specific integration points or implementation examples, refer to the following resources:

1. [Architecture Documentation](../architecture/README.md) for more details on the framework architecture
2. [API Reference](../api-reference/README.md) for detailed API documentation
3. [Customization Guide](../customization/README.md) for guidance on extending and customizing the framework
4. [Best Practices Guide](../best-practices/README.md) for recommendations on effective integration