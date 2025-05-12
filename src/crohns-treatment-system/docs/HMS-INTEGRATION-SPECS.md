# HMS Integration Specifications

## Overview

The HMS Integration System provides a comprehensive bridge between the Crohn's Treatment System and HMS components (HMS-DOC and HMS-MFE). This document outlines the technical specifications, architecture, and integration points.

## Architecture

The integration architecture follows a layered approach:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Crohn's Treatment System UI                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                         API Gateway                              │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                   Integration Coordinator                        │
└─┬─────────────────────────────┬────────────────────────────────┬┘
  │                             │                                │
┌─▼─────────────────┐    ┌──────▼───────────┐    ┌───────────────▼─┐
│  Doc Integration   │    │ Task Scheduler   │    │ Publication      │
│     Service        │    │                  │    │   Repository     │
└─┬─────────────────┬┘    └──────────────────┘    └─────────────────┘
  │                 │
┌─▼─────────────┐ ┌─▼────────────┐
│   HMS-DOC     │ │   HMS-MFE    │
└───────────────┘ └──────────────┘
```

## Core Components

### 1. API Gateway (`/src/api_gateway/doc_integration_controller.py`)

Exposes REST endpoints for:
- Exporting abstractions to HMS-DOC
- Publishing clinical trials to HMS-MFE
- Generating integrated documentation
- Scheduling background tasks
- Retrieving publication history and status

### 2. Integration Coordinator (`/src/coordination/doc_integration/integration_coordinator.py`)

Orchestrates the integration between systems:
- Manages task scheduling and execution
- Tracks publication history
- Monitors system status
- Coordinates between HMS-DOC and HMS-MFE

### 3. Doc Integration Service (`/src/coordination/doc_integration/doc_integration_service.py`)

Provides the core integration logic:
- Transforms data between systems
- Communicates with HMS-DOC for documentation generation
- Interfaces with HMS-MFE writer component
- Handles error cases and edge conditions

### 4. Vue Components

- `ClinicalTrialPublisher.vue`: Main UI for publishing clinical trials
- `IntegrationDashboard.vue`: Dashboard for monitoring integrations
- API client classes for frontend-backend communication

## Data Flow

### Abstraction Export to HMS-DOC

```sequence
Client->API Gateway: POST /doc-integration/export-abstractions
API Gateway->Integration Coordinator: publish_to_hms_doc()
Integration Coordinator->Doc Integration Service: export_abstractions_to_doc()
Doc Integration Service->HMS-DOC: Convert & export
HMS-DOC->Doc Integration Service: Documentation path
Doc Integration Service->Integration Coordinator: Publication info
Integration Coordinator->API Gateway: Publication result
API Gateway->Client: Success response
```

### Clinical Trial Publishing to HMS-MFE

```sequence
Client->API Gateway: POST /doc-integration/publish-trial
API Gateway->Integration Coordinator: publish_to_hms_mfe()
Integration Coordinator->Doc Integration Service: publish_clinical_trial()
Doc Integration Service->HMS-MFE: Convert & publish
HMS-MFE->Doc Integration Service: Publication info
Doc Integration Service->Integration Coordinator: Publication info
Integration Coordinator->API Gateway: Publication result
API Gateway->Client: Success response
```

### Integrated Documentation Generation

```sequence
Client->API Gateway: POST /doc-integration/generate-documentation
API Gateway->Integration Coordinator: schedule_documentation_task()
Integration Coordinator->Task Scheduler: Schedule background task
Task Scheduler->Doc Integration Service: generate_integrated_documentation()
Doc Integration Service->HMS-DOC: Export abstractions
Doc Integration Service->HMS-MFE: Publish trials
Doc Integration Service->Integration Coordinator: Documentation info
Integration Coordinator->Publication Repository: Store documentation
Task Scheduler->Client: Task status updates (polling)
```

## Integration Points

### HMS-DOC Integration

- **Path**: `/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-DOC`
- **Integration Method**: Command-line interface
- **Data Format**: YAML for abstractions and relationships

### HMS-MFE Integration

- **Path**: `/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE`
- **Writer Component**: `/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue`
- **Integration Method**: File-based JSON exchange
- **Data Format**: JSON for clinical trial data

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/doc-integration/export-abstractions` | POST | Export abstractions to HMS-DOC |
| `/api/doc-integration/publish-trial` | POST | Publish clinical trial to HMS-MFE |
| `/api/doc-integration/generate-documentation` | POST | Generate integrated documentation |

### Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/doc-integration/status` | GET | Get integration system status |
| `/api/doc-integration/publications` | GET | List publications |
| `/api/doc-integration/publications/:id` | GET | Get publication details |
| `/api/doc-integration/tasks` | GET | List background tasks |
| `/api/doc-integration/tasks/:id` | GET | Get task status |

### Scheduling Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/doc-integration/schedule/export-abstractions` | POST | Schedule abstraction export |
| `/api/doc-integration/schedule/publish-trial` | POST | Schedule trial publication |
| `/api/doc-integration/schedule/integrated-documentation` | POST | Schedule integrated doc generation |

## Data Models

### Abstraction

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "confidence": 0.95,
  "type": "string",
  "source": "string",
  "related_entities": [
    {
      "id": "string",
      "name": "string",
      "type": "string",
      "strength": 0.8,
      "evidence": ["string"]
    }
  ]
}
```

### Clinical Trial

```json
{
  "id": "string",
  "title": "string",
  "status": "RECRUITING|ONGOING|COMPLETED|PLANNED",
  "phase": "PHASE_1|PHASE_2|PHASE_3|PHASE_4",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "description": "string",
  "inclusion_criteria": ["string"],
  "exclusion_criteria": ["string"],
  "biomarkers": ["string"],
  "treatments": ["string"],
  "outcomes": ["string"],
  "abstraction_ids": ["string"]
}
```

### Publication

```json
{
  "id": "string",
  "project_name": "string",
  "timestamp": "2023-05-01T12:00:00Z",
  "status": "completed|failed",
  "type": "hms_doc|hms_mfe|integrated",
  "output_path": "string",
  "file_path": "string",
  "metadata": {
    "abstractions_count": 8,
    "relationships_count": 12,
    "clinical_trials_count": 5
  }
}
```

### Task

```json
{
  "id": "string",
  "type": "publish_doc|publish_mfe|generate_integrated",
  "status": "scheduled|running|completed|failed",
  "created_at": "2023-05-01T12:00:00Z",
  "updated_at": "2023-05-01T12:05:00Z",
  "params": {},
  "result": {},
  "error": null
}
```

## Configuration

The integration system can be configured through the following options:

```python
# Doc Integration Service Configuration
service = DocIntegrationService(
    doc_root_path='/path/to/HMS-DOC',
    mfe_root_path='/path/to/HMS-MFE',
    output_dir='/path/to/output'
)

# Task Scheduler Configuration
# - Maximum concurrent tasks: 5
# - Task timeout: 30 minutes
# - Retry attempts: 3
```

## Error Handling

The integration system implements the following error handling strategies:

1. **API Layer**: Returns appropriate HTTP status codes and error messages
2. **Coordinator Layer**: Records errors in task history and publication logs
3. **Service Layer**: Implements retries with exponential backoff
4. **HMS Integration**: Falls back to simulation mode if components unavailable

## Security Considerations

1. All data exchange between components occurs within the filesystem
2. No external network access required
3. Publication history is stored locally and not exposed externally
4. Task execution runs with limited system permissions

## Performance Considerations

1. Long-running tasks are executed asynchronously
2. Publication history is cached in memory for fast retrieval
3. Heavy processing is offloaded to background threads
4. Status polling uses efficient querying

## Future Enhancements

1. Real-time update notifications using WebSockets
2. Enhanced visualization options for publications
3. Integration with additional HMS components
4. Automated scheduling of regular documentation updates