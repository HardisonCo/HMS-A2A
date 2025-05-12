# CDF Integration for HMS-GOV

This document provides information on the integration between HMS-GOV and HMS-CDF via the protocol transformation layer in the agency interface.

## Overview

The CDF (Collaborative Decision Framework) integration enables HMS-GOV to connect to the HMS-CDF system via specialized domains (dnc.dev and rnc.dev), transforming protocols between different formats and synchronizing events between systems.

### Key Components

1. **CDF Connector**: A Python-based connector for interacting with the CDF API and handling events
2. **Protocol Transformation Layer**: PHP middleware for transforming protocols between HMS-API, CDF, and Adaptive Trial formats
3. **Event Synchronization**: Components for bidirectional event flow between systems
4. **Authentication Middleware**: Security layer for API access and webhook verification

## Configuration

The CDF connector is configured through the `cdf_config.json` file in the `agencies/cdf` directory. This file contains:

- API connection settings
- Domain configuration for dnc.dev and rnc.dev
- Protocol transformation mappings
- Event webhook configuration
- Legislative framework settings
- Integration options

Environment variables can be included in the configuration using the `{{ENV:VARIABLE_NAME}}` syntax.

## API Endpoints

### Connection Management

- `GET /api/v1/cdf/connections`: Get all connections
- `GET /api/v1/cdf/connections/{domain}`: Get specific connection
- `POST /api/v1/cdf/connections/{domain}`: Create/update connection
- `POST /api/v1/cdf/connections/{domain}/test`: Test connection
- `DELETE /api/v1/cdf/connections/{domain}`: Delete connection

### Protocol Management

- `GET /api/v1/cdf/protocols`: Get all protocols
- `GET /api/v1/cdf/protocols/{id}`: Get specific protocol
- `POST /api/v1/cdf/protocols/{id}/sync`: Synchronize protocol with CDF
- `GET /api/v1/cdf/protocols/{id}/transform`: Transform protocol to CDF format
- `POST /api/v1/cdf/protocols/import`: Import protocol from CDF

### Webhooks

The following webhook endpoints are available for receiving events from CDF:

- `POST /webhooks/cdf/protocol-update`: Protocol update events
- `POST /webhooks/cdf/decision-event`: Decision events
- `POST /webhooks/cdf/debate-event`: Debate events
- `POST /webhooks/cdf/vote-event`: Vote events

## Authentication

The CDF integration supports two authentication methods:

1. **Bearer Tokens**: All API endpoints require a bearer token for authentication.
2. **Webhook Signatures**: Webhooks are verified using HMAC signatures.

### Bearer Token Authentication

To authenticate API requests, include a bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

### Webhook Verification

Webhooks are verified using HMAC signatures. The CDF system sends a signature in the `X-CDF-Signature` header, which is validated against the webhook payload using the configured secret.

## Protocol Transformation

The Protocol Transformation Layer handles conversion between different protocol formats:

1. **HMS-API to CDF**: Transforms HMS-API protocols to CDF format for use in the CDF system
2. **CDF to HMS-API**: Transforms CDF protocols to HMS-API format for storage and processing
3. **HMS-API to Adaptive Trial**: Transforms HMS-API protocols to Adaptive Trial format for use in trial management

### Legislative Framework Mapping

The HMS-CDF integration includes mappings for legislative framework components:

- **Sections** are mapped from protocol chain modules
- **Debates** are mapped from assessment tasks
- **Voting Procedures** are mapped from decision tasks
- **Policy Modules** are mapped from protocol programs

## Command Line Usage

The CDF connector includes a command-line interface for interacting with the CDF system:

```bash
# Get CDF implementation status
python cdf_connector.py --output status

# Get CDF config
python cdf_connector.py --output config

# Connect to CDF
python cdf_connector.py --connect cdf --token <token>

# Connect to dnc.dev
python cdf_connector.py --connect dnc --token <token>

# Connect to rnc.dev
python cdf_connector.py --connect rnc --token <token>

# Handle a protocol update event
python cdf_connector.py --event protocol_update --event-data '{"protocol":{"id":"123"}}' --event-signature <signature>
```

## Event Flow

The integration supports bidirectional event flow between systems:

1. **HMS-API to CDF**:
   - Protocol updates are sent to CDF when protocols are created or modified
   - Protocol synchronization can be triggered manually or automatically

2. **CDF to HMS-API**:
   - Protocol updates from CDF are received via webhooks
   - Decision, debate, and vote events are handled through their respective webhooks

## Development

### Adding New Event Types

To add a new event type to the CDF integration:

1. Add the event type to the `events` section in `cdf_config.json`
2. Create a handler method in the `CDFWebhookController`
3. Add a route in `cdf_routes.php`
4. Add an event handler method to the `CDFResearchConnector`

### Extending Protocol Transformation

To extend the protocol transformation capabilities:

1. Add new mapping methods to the `ProtocolTransformationLayer`
2. Update the configuration mappings in `cdf_config.json`
3. Implement the transformation logic in the relevant components

## Security Considerations

- All API endpoints should be accessed over HTTPS
- Bearer tokens should be kept secure and rotated regularly
- Webhook secrets should be strong and unique for each environment
- Connection information should be stored securely and not committed to source control

## Troubleshooting

### Connection Issues

If you're experiencing connection issues with CDF:

1. Check the connection configuration in `cdf_config.json`
2. Verify the authentication token is valid
3. Check network connectivity and firewall settings
4. Review the application logs for error messages

### Webhook Issues

If webhooks are not being processed correctly:

1. Verify the webhook URL is configured correctly in the CDF system
2. Check the webhook secret matches between systems
3. Ensure the signature is being calculated and sent correctly
4. Review the webhook handler logic for any errors

### Transformation Issues

If protocol transformation is not working correctly:

1. Check the protocol format matches the expected structure
2. Verify the transformation mappings in the configuration
3. Review the transformation logic for errors or inconsistencies
4. Check for any validation failures in the logs