# HMS Integration User Guide

This guide provides instructions for using the integration between the Crohn's Treatment System, HMS-DOC, and HMS-MFE.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Publishing Abstractions to HMS-DOC](#publishing-abstractions-to-hms-doc)
4. [Publishing Clinical Trials to HMS-MFE](#publishing-clinical-trials-to-hms-mfe)
5. [Generating Integrated Documentation](#generating-integrated-documentation)
6. [Using the Integration Dashboard](#using-the-integration-dashboard)
7. [Monitoring Publications](#monitoring-publications)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

The HMS Integration System provides a seamless bridge between the Crohn's Treatment System and HMS components:

- **HMS-DOC**: Documentation generation system for creating comprehensive documentation
- **HMS-MFE**: Multi-frontend system with editing capabilities through the writer component

This integration enables researchers to:
- Publish abstraction analysis results as documentation
- Export clinical trial data for editing and visualization
- Generate comprehensive documentation combining insights from both systems

## Getting Started

### Prerequisites

- Crohn's Treatment System installed and configured
- HMS-DOC and HMS-MFE components available at the standard paths
- Web browser for accessing the user interface

### Accessing the Integration Features

1. Launch the Crohn's Treatment System
2. Navigate to the Clinical Trial Publisher interface
3. Select abstractions and clinical trials of interest
4. Use the "Publish to HMS-DOC" or "Publish to HMS-MFE" buttons to initiate publication

## Publishing Abstractions to HMS-DOC

Abstractions are patterns and relationships identified in clinical trial data. To publish them to HMS-DOC:

1. **Select Abstractions**: In the Clinical Trial Publisher, select the abstractions you want to publish
2. **Generate Relationships**: The system will automatically generate relationships between selected abstractions
3. **Publish to HMS-DOC**: Click the "Publish to HMS-DOC" button
4. **Monitor Progress**: The system will display progress and notify you when complete
5. **View Documentation**: Once complete, you can navigate to the output path to view the generated documentation

**Example:**

```json
// Selected abstractions
[
  {
    "id": "abst-001",
    "name": "Biomarker Response Patterns",
    "description": "Patterns of response to treatment based on specific biomarkers",
    "confidence": 0.92
  },
  {
    "id": "abst-002",
    "name": "Treatment Efficacy Correlations",
    "description": "Correlations between treatments and efficacy for patient subgroups",
    "confidence": 0.87
  }
]

// Generated documentation path
"/Users/arionhardison/Desktop/Codify/output/documentation/Crohns-Abstractions-20240509"
```

## Publishing Clinical Trials to HMS-MFE

Clinical trial data can be published to the HMS-MFE writer component for editing:

1. **Select Clinical Trials**: In the Clinical Trial Publisher, select the trials you want to publish
2. **Select Related Abstractions**: Optionally, select abstractions related to the trials
3. **Publish to HMS-MFE**: Click the "Publish to HMS-MFE" button
4. **Monitor Progress**: The system will display progress and notify you when complete
5. **Open in Writer**: Once complete, you can open the published data in the HMS-MFE writer

**Example:**

```json
// Selected clinical trial
{
  "id": "trial-001",
  "title": "Adaptive Trial of JAK Inhibitors in Crohn's Disease",
  "phase": "PHASE_2",
  "status": "COMPLETED",
  "description": "Evaluating efficacy of JAK inhibitors with adaptive design"
}

// Publication result
{
  "publication_id": "mfe-1683644825",
  "file_path": "/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/json-server/data/publication.json",
  "writer_component": "/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue"
}
```

## Generating Integrated Documentation

To create comprehensive documentation that combines abstractions and clinical trials:

1. **Select Abstractions and Trials**: In the Clinical Trial Publisher, select both abstractions and clinical trials
2. **Generate Integrated Documentation**: Click the "Generate Comprehensive Documentation" button in the Integration Dashboard
3. **Monitor Progress**: The system will display progress and notify you when complete
4. **View Documentation**: Once complete, you can access both the HMS-DOC documentation and HMS-MFE publications

**Example:**

```json
// Integrated documentation result
{
  "documentation_path": "/Users/arionhardison/Desktop/Codify/output/documentation/Integrated-Documentation-20240509",
  "published_trials": [
    {
      "publication_id": "mfe-1683644830",
      "file_path": "/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/json-server/data/publication_trial001.json"
    }
  ],
  "project_name": "Integrated-Documentation-20240509"
}
```

## Using the Integration Dashboard

The Integration Dashboard provides a central interface for managing all HMS integrations:

1. **System Status**: View the connection status of HMS-DOC and HMS-MFE
2. **Publication Metrics**: See counts of publications for each system
3. **Actions**: Perform integration actions like generating documentation
4. **Publications**: Browse and manage publications for HMS-DOC and HMS-MFE
5. **Tasks**: Monitor background tasks for long-running operations

**Dashboard Features:**

- **Tabs**: Switch between HMS-DOC and HMS-MFE publications
- **Publication Cards**: View summary information about each publication
- **Action Buttons**: Perform key integration actions
- **Details View**: View detailed information about publications
- **Task Monitoring**: Check the status of scheduled tasks

## Monitoring Publications

To monitor publications across systems:

1. **Open Integration Dashboard**: Navigate to the Integration Dashboard
2. **View Publications**: Use the tabs to switch between HMS-DOC and HMS-MFE publications
3. **Publication Details**: Click "Details" on any publication card to view detailed information
4. **Open Publications**: Click "Open" to view the publication in its native format
5. **Status Monitoring**: Check the status of each publication (completed, failed, etc.)

**Publication States:**

- **Completed**: Publication successfully completed
- **Failed**: Publication failed (check details for error information)
- **In Progress**: Publication is currently being processed
- **Archived**: Publication has been archived

## Troubleshooting

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| HMS-DOC Disconnected | HMS-DOC path incorrect | Check configuration for correct path |
| HMS-MFE Disconnected | HMS-MFE path incorrect | Check configuration for correct path |
| Publication Failed | Error during processing | Check error message in publication details |
| Writer Not Found | Writer component path incorrect | Update writer path in configuration |
| Task Timeout | Operation took too long | Check system resources, try again with fewer items |

### Checking System Status

To check the status of the integration system:

```bash
# API endpoint
curl http://localhost:8000/api/doc-integration/status

# Response
{
  "status": "success",
  "data": {
    "hms_doc": "connected",
    "hms_mfe": "connected",
    "timestamp": "2023-05-09T14:30:45Z",
    "doc_publications_count": 5,
    "mfe_publications_count": 3,
    "integrated_publications_count": 2
  }
}
```

### Checking Publication History

To view publication history:

```bash
# API endpoint
curl http://localhost:8000/api/doc-integration/publications?type=hms_doc

# Response
{
  "status": "success",
  "data": [
    {
      "id": "doc-1683644825",
      "project_name": "Crohns-Abstractions-20230509",
      "output_path": "/Users/arionhardison/Desktop/Codify/output/documentation/Crohns-Abstractions-20230509",
      "timestamp": "2023-05-09T14:20:25Z",
      "status": "completed",
      "type": "hms_doc"
    }
  ]
}
```

## FAQ

### General Questions

**Q: Can I publish to both HMS-DOC and HMS-MFE simultaneously?**  
A: Yes, use the "Generate Integrated Documentation" feature to publish to both systems at once.

**Q: Where are publications stored?**  
A: HMS-DOC publications are stored in the output directory. HMS-MFE publications are stored in the HMS-MFE json-server/data directory.

**Q: Can I edit publications after they are created?**  
A: Yes, HMS-MFE publications can be edited using the writer component. HMS-DOC publications are static but can be regenerated.

**Q: How long do publications take to generate?**  
A: Small publications take a few seconds. Larger publications with many abstractions and trials may take 1-2 minutes.

### Technical Questions

**Q: What happens if HMS-DOC or HMS-MFE is unavailable?**  
A: The system will operate in simulation mode, creating placeholders for the unavailable systems.

**Q: Can I schedule regular documentation updates?**  
A: Yes, use the scheduling API endpoints to set up regular documentation generation.

**Q: How are relationships between abstractions determined?**  
A: Relationships are either extracted from the related_entities field of abstractions, or generated using a simple heuristic chain if none exist.

**Q: Is there a limit to how many abstractions I can publish?**  
A: There is no hard limit, but performance may degrade with very large numbers (100+) of abstractions.

**Q: Can I customize the documentation format?**  
A: Currently the format is fixed, but future versions will support customization options.