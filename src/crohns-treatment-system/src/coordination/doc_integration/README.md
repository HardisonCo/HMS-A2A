# HMS Documentation Integration

This module provides integration between the Crohn's Treatment System, HMS-DOC, and HMS-MFE components. It enables the system to generate comprehensive documentation and visualizations for clinical trials, abstractions, and biomarker patterns.

## Overview

The HMS Documentation Integration module serves as a bridge between three key components:

1. **Crohn's Treatment System**: Provides clinical trial data, abstractions, and biomarker analysis
2. **HMS-DOC**: Generates comprehensive documentation from abstractions and relationships
3. **HMS-MFE**: Provides interactive visualization and editing through the writer component

## Architecture

```
┌────────────────────┐   ┌─────────────────────┐   ┌────────────────┐
│                    │   │                     │   │                │
│ Crohn's Treatment  │──▶│ DocIntegrationService│──▶│    HMS-DOC     │
│      System        │   │                     │   │                │
│                    │   └─────────────────────┘   └────────────────┘
│                    │           │   ▲              
│  Abstractions &    │           │   │              
│  Clinical Trials   │           ▼   │              
│                    │   ┌─────────────────────┐   ┌────────────────┐
│                    │   │                     │   │                │
│                    │──▶│ WriterIntegration   │──▶│    HMS-MFE     │
└────────────────────┘   │                     │   │                │
                         └─────────────────────┘   └────────────────┘
```

## Features

- **Export Abstractions to HMS-DOC**: Convert abstraction analysis results to HMS-DOC format
- **Publish Clinical Trials to HMS-MFE**: Export trial data to the writer component
- **Generate Integrated Documentation**: Combine abstractions and trial data into comprehensive docs
- **Relationship Generation**: Automatically generate relationship maps between abstractions
- **Web API**: REST endpoints for programmatic access to all functionality

## Usage

### Python API

```python
from src.coordination.doc_integration import create_doc_integration_service

# Create the service
service = create_doc_integration_service()

# Export abstractions to HMS-DOC
output_path = service.export_abstractions_to_doc(
    abstractions=abstractions,
    relationships=relationships,
    project_name="Crohns-Trial-Documentation"
)

# Publish clinical trial to HMS-MFE
publication_info = service.publish_clinical_trial(
    trial_data=trial,
    abstractions=trial_abstractions
)

# Generate comprehensive documentation
doc_info = service.generate_integrated_documentation(
    clinical_trials=trials,
    abstractions=abstractions,
    relationships=relationships,
    project_name="Comprehensive-Crohns-Documentation"
)
```

### REST API

```
# Export abstractions to HMS-DOC
POST /api/doc-integration/export-abstractions
{
    "abstractions": [...],
    "relationships": [...],
    "project_name": "Crohns-Treatment-Abstractions"
}

# Publish clinical trial to HMS-MFE
POST /api/doc-integration/publish-trial
{
    "trial_data": {...},
    "abstractions": [...],
    "writer_component_path": "..."
}

# Generate comprehensive documentation
POST /api/doc-integration/generate-documentation
{
    "clinical_trials": [...],
    "abstractions": [...],
    "relationships": [...],
    "project_name": "Crohns-Treatment-Documentation"
}
```

## Integration with HMS-MFE Writer

The integration with HMS-MFE uses the writer component at:
`/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue`

This component allows researchers to edit and enhance the automatically generated content before publication.

## Configuration

All integration paths can be configured in the `create_doc_integration_service()` function:

```python
service = DocIntegrationService(
    doc_root_path='/path/to/HMS-DOC',
    mfe_root_path='/path/to/HMS-MFE',
    output_dir='/path/to/output'
)
```

## Extending the Integration

To add support for additional HMS components:

1. Create a new integration service class in the `doc_integration` module
2. Add appropriate methods for data transformation and export
3. Register REST API endpoints in the API gateway
4. Update the UI component to expose the new functionality

## Sample Workflow

1. Researchers select relevant clinical trials and abstractions
2. System generates relationship mapping between abstractions
3. Integrated documentation is created in HMS-DOC format
4. Clinical trial data is exported to HMS-MFE writer for editing
5. Final documentation is published for consumption