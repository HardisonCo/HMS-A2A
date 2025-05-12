# Federation Framework

This federation framework enables secure cross-agency data sharing and collaboration within the APHIS Bird Flu monitoring and response system. It provides a standardized approach for agencies to share data while maintaining security, privacy, and governance controls.

## Core Components

1. **Query Federation** - Enables distributed queries across multiple agency data sources
2. **Data Synchronization** - Manages secure replication of data between agencies
3. **Access Control** - Enforces fine-grained permissions for shared resources
4. **Audit Logging** - Tracks all federation activities for compliance and security
5. **Schema Registry** - Maintains standardized data schemas across agencies
6. **Identity Federation** - Enables secure cross-agency authentication and authorization
7. **Governance** - Defines policies and controls for federation activities

## Key Features

- Secure multi-agency data sharing
- Privacy-preserving federated queries
- Real-time and batch synchronization options
- Comprehensive audit trails for all federation activities
- Fine-grained access control with security classifications
- Support for data sovereignty and geographic restrictions
- Federation gateway pattern for controlled data exchange

## Usage

```python
from federation import FederationManager
from federation.query import FederatedQueryBuilder
from federation.sync import SyncManager

# Initialize federation with local agency ID
federation = FederationManager(local_agency_id="USDA-APHIS")

# Register partner agencies
federation.register_partner(
    agency_id="STATE-DOA-WA",
    endpoint="https://wa-agriculture.gov/federation",
    trust_level="PARTNER"
)

# Execute federated query
results = federation.query.build() \
    .select("outbreak_reports") \
    .where({"state": "WA", "date_range": "last_30_days"}) \
    .execute()

# Synchronize specific datasets
sync_job = federation.sync.create_job(
    target_agency="STATE-DOA-WA",
    datasets=["poultry_farm_status"],
    sync_mode="incremental"
)
sync_job.execute()
```

## Security Considerations

- All communications are encrypted using TLS 1.3+
- Data classification tagging enforced for all shared resources
- Authentication via JWT with short-lived tokens
- Multiple authorization layers (agency, role, user, data)
- Comprehensive audit logging for all federation activities

## Configuration

Configuration is managed through environment variables or a federation.yaml file:

```yaml
federation:
  local_agency: "USDA-APHIS"
  gateway:
    host: "0.0.0.0"
    port: 8585
    tls:
      cert: "/path/to/cert.pem"
      key: "/path/to/key.pem"
  
  partners:
    - id: "STATE-DOA-WA"
      endpoint: "https://wa-agriculture.gov/federation"
      trust_level: "PARTNER"
      allowed_datasets: ["outbreak_reports", "poultry_farm_status"]
    
    - id: "CDC"
      endpoint: "https://cdc.gov/federation"
      trust_level: "TRUSTED"
      allowed_datasets: ["human_exposure"]
```