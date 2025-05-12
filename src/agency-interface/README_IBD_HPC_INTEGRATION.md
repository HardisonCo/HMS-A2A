# HMS-GOV to HMS-CDF Integration with IBD Protocol and HPC Support

This documentation details the integration between HMS-GOV and HMS-CDF with special focus on Inflammatory Bowel Disease (IBD) Protocol Specification, High-Performance Computing (HPC) integration, and multi-institution data sharing capabilities.

## Overview

The integration includes several key components:

1. **Protocol Transformation Layer** - Enhanced to support IBD protocols, HPC-enabled trials, and CBER/CDER AI modules
2. **HPC Integration Service** - New service for high-performance computing integration
3. **AI Module Support** - Support for CBER.ai and CDER.ai modules via a proxy API
4. **IBD Protocol Visualization** - Specialized components for IBD protocol dashboards
5. **Multi-Institution Data Sharing** - Secure federated data sharing between institutions

## Components

### 1. Protocol Adapter

The protocol adapter has been enhanced to support IBD Protocol Specification with the following features:

- IBD-specific biomarkers (fecal calprotectin, CRP, CDAI, HBI, etc.)
- HPC configuration for multi-site trials
- Integration with CBER and CDER AI modules
- Support for complex treatment regimens for IBD

Key files:
- `/protocol_transformation/protocol_adapter.php`

### 2. HPC Integration Service

A new HPC Integration Service has been implemented to handle high-performance computing capabilities:

- Protocol submission to HPC clusters
- Job management and status monitoring
- AI module configuration for CBER.ai and CDER.ai
- Multi-institution data sharing initialization

Key files:
- `/hpc_integration/HPCIntegrationService.php`
- `/hpc_integration/HPCIntegrationController.php`
- `/hpc_integration/HPCWebhookMiddleware.php`
- `/hpc_integration/AIProxyController.php`
- `/config/hpc_integration.php`
- `/routes/hpc_integration.php`

### 3. Frontend Components

Several frontend components have been developed to visualize and manage IBD protocols:

- IBD Protocol Dashboard
- Biomarker Threshold Editor
- Endpoint Definition Editor
- Protocol Timeline Visualization
- Multi-Institution Data Sharing Panel

Key files:
- `/js/components/protocols/ibd/IBDProtocolDashboard.jsx`
- `/js/components/protocols/ibd/BiomarkerThresholdEditor.jsx`
- `/js/components/protocols/ibd/EndpointDefinitionEditor.jsx`
- `/js/components/protocols/ibd/IBDProtocolTimeline.jsx`
- `/js/components/protocols/sharing/MultiInstitutionDataSharingPanel.jsx`

### 4. Protocol Service

The Protocol Service JavaScript class provides a client-side interface for interacting with protocols and AI modules:

- Protocol CRUD operations
- HPC integration
- AI module interaction (CBER.ai and CDER.ai)
- IBD-specific protocol management
- Multi-institution data sharing management

Key files:
- `/js/services/ProtocolService.js`

## IBD Protocol Specification

The implementation adds support for the IBD Protocol Specification with the following features:

### Biomarkers

- **Inflammation Markers**: Fecal calprotectin, CRP, fecal lactoferrin
- **Clinical Activity Scores**: CDAI, HBI
- **Cytokines**: IL-6, TNF-alpha
- **Serological Markers**: ASCA_IgA, ASCA_IgG
- **Genetic Markers**: NOD2, IL23R, ATG16L1

### Endpoints

- **Primary**: Clinical remission at Week 16 (CDAI < 150)
- **Secondary**:
  - Mucosal healing at Week 16
  - Corticosteroid-free remission at Week 24
  - Fecal calprotectin normalization at Week 8
  - Quality of life improvement at Week 16

### Assessment Schedule

- **Endoscopic**: Baseline, Week 16
- **Blood Tests**: Baseline, Week 4, Week 8, Week 16, Week 24
- **Stool Tests**: Baseline, Week 4, Week 8, Week 16, Week 24
- **Clinical Scores**: Baseline, Week 4, Week 8, Week 16, Week 24

## HPC Integration

The HPC integration provides advanced computing capabilities for IBD protocols:

### Features

- **High-Performance Computing**: Parallel processing for large datasets
- **AI Module Integration**: Integration with CBER.ai and CDER.ai modules
- **Multi-Institution Data Sharing**: Federated learning for secure collaboration
- **Genetic Algorithm Optimization**: Protocol optimization using genetic algorithms

### Configuration Options

```php
// Default HPC configuration
$hpcConfig = [
    'nodes' => 8,
    'memoryPerNode' => '64GB',
    'storageAllocation' => '2TB',
    'maxRuntime' => '72h'
];
```

### AI Module Types

1. **CBER.ai (Center for Biologics Evaluation and Research)**
   - Biologics quality prediction
   - Immunogenicity analysis
   - Process development optimization
   - Stability prediction
   - Comparability assessment

2. **CDER.ai (Center for Drug Evaluation and Research)**
   - Drug interaction prediction
   - Adverse event prediction
   - Pharmacokinetic modeling
   - Dose optimization
   - Efficacy prediction

## Multi-Institution Data Sharing

The implementation includes a federated learning approach for secure data sharing between institutions:

### Features

- **Federated Learning**: Data remains at source institutions
- **Differential Privacy**: Mathematical guarantees for patient privacy
- **Role-Based Access Control**: Different access levels for different institutions
- **Secure Data Sharing Agreements**: Formalized data sharing agreements

### Institution Roles

- **Coordinator**: Manages the overall trial and has full access
- **Contributor**: Contributes data and participates in federated learning
- **Monitor**: Monitors trial progress with limited data access

### Privacy Protection

- **Differential Privacy**: Epsilon and delta parameters for privacy guarantees
- **Federated Learning**: Model training without sharing raw data
- **Secure Aggregation**: Privacy-preserving aggregation of model updates

## API Endpoints

### Protocol Management

- `POST /api/protocols` - Create a new protocol
- `GET /api/protocols/{id}` - Get protocol details
- `PUT /api/protocols/{id}` - Update a protocol
- `DELETE /api/protocols/{id}` - Delete a protocol

### HPC Integration

- `POST /api/hpc/protocols/{protocolId}/submit` - Submit protocol to HPC
- `GET /api/hpc/jobs/{jobId}` - Get HPC job status
- `DELETE /api/hpc/jobs/{jobId}` - Cancel HPC job
- `POST /api/hpc/protocols/{protocolId}/data-sharing` - Initialize data sharing
- `POST /api/hpc/protocols/{protocolId}/ai-module` - Configure AI module

### AI Module Proxy

- `GET /api/ai-proxy/{aiType}/models` - Get available AI models
- `POST /api/ai-proxy/{aiType}/predict` - Run model prediction
- `POST /api/ai-proxy/{aiType}/train` - Start model training
- `POST /api/ai-proxy/{aiType}/insights` - Generate insights

### Webhooks

- `POST /webhooks/hpc` - Webhook endpoint for HPC job notifications

## Usage Examples

### Submitting a Protocol to HPC

```php
$hpcService = new HPCIntegrationService($protocolAdapter);

$hpcOptions = [
    'nodes' => 16,
    'memory' => '128GB',
    'storage' => '5TB',
    'runtime' => '96h',
    'containerImage' => 'hms-gov/protocol-processor:latest'
];

$result = $hpcService->submitProtocolToHPC($protocol, $hpcOptions);
```

### Configuring an AI Module

```php
$aiConfig = [
    'version' => '2.1',
    'hpcRequirements' => [
        'nodes' => 4,
        'gpusPerNode' => 2,
        'memoryPerNode' => '128GB'
    ],
    'integrationPoints' => [
        'dataIngestion' => true,
        'modelTraining' => true,
        'inference' => true,
        'reporting' => true
    ]
];

$result = $hpcService->configureAIModule($protocol, 'cber.ai', $aiConfig);
```

### Initializing Multi-Institution Data Sharing

```php
$institutions = [
    [
        'id' => 'primary',
        'name' => 'Primary Research Center',
        'role' => 'coordinator',
        'dataAccessLevel' => 'full'
    ],
    [
        'id' => 'site_1',
        'name' => 'Collaborative Site 1',
        'role' => 'contributor',
        'dataAccessLevel' => 'limited'
    ],
    [
        'id' => 'site_2',
        'name' => 'Collaborative Site 2',
        'role' => 'contributor',
        'dataAccessLevel' => 'limited'
    ]
];

$result = $hpcService->initializeMultiInstitutionDataSharing($protocol, $institutions);
```

## Frontend Integration

To use the IBD Protocol Dashboard component:

```jsx
import IBDProtocolDashboard from './components/protocols/ibd/IBDProtocolDashboard';

// In your React component
<IBDProtocolDashboard 
  protocolId={123}
  readOnly={false}
/>
```

## Security Considerations

- **Authentication**: All API endpoints are secured with JWT authentication
- **Webhook Verification**: Webhooks use HMAC signature verification
- **Data Encryption**: All data is encrypted in transit
- **Privacy Protection**: Differential privacy for patient data protection
- **Access Control**: Role-based access control for institutions

## Environment Variables

```
HPC_CLUSTER_ENDPOINT=https://hpc.example.org/api/v1
HPC_AUTH_TOKEN=your-auth-token
HPC_WEBHOOK_SECRET=your-webhook-secret
HPC_NOTIFICATION_ENDPOINT=https://your-app.example.org/webhooks/hpc-callback
CBER_AI_ENDPOINT=https://cber.ai/api/v2
CBER_AI_TOKEN=your-cber-token
CDER_AI_ENDPOINT=https://cder.ai/api/v1
CDER_AI_TOKEN=your-cder-token
```

## Implementation Notes

1. The HPC integration assumes a cluster with sufficient resources for IBD protocol processing
2. CBER.ai and CDER.ai modules require appropriate API tokens for access
3. Multi-institution data sharing requires participating institutions to have compatible systems
4. IBD Protocol Specification is based on industry standards for Crohn's disease trials
5. All API endpoints include comprehensive validation and error handling

## Future Enhancements

1. **Real-time Data Synchronization**: Add support for real-time data updates across institutions
2. **Advanced Visualization**: Enhance visualization capabilities for IBD biomarker trends
3. **Expanded AI Capabilities**: Add support for additional AI modules and capabilities
4. **Mobile Integration**: Add support for mobile access to protocol dashboards
5. **Expanded Biomarker Support**: Add support for additional IBD biomarkers and endpoints