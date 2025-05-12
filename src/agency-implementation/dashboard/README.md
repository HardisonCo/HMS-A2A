# Bird Flu Interagency Dashboard

A unified dashboard application that visualizes data from CDC, EPA, and FEMA implementations to provide a comprehensive view of bird flu monitoring and response activities across all agencies.

## Overview

This dashboard integrates with the Federation Hub to access data from multiple agencies, providing coordinated visualization of:

- Disease surveillance data from CDC
- Environmental quality monitoring from EPA
- Emergency resource coordination from FEMA

The application serves as a central monitoring tool for the interagency bird flu response, showing real-time data aggregation across organizational boundaries.

## Features

- **Summary Statistics**: Key metrics from each agency at a glance
- **Case Distribution Map**: Geographic visualization of bird flu cases
- **Virus Subtype Distribution**: Breakdown of detected virus subtypes
- **Environmental Quality Trends**: Air quality and other environmental metrics over time
- **Resource Allocation**: Emergency resource deployment visualization
- **Health-Environment Correlation**: Analysis of relationships between cases and environmental factors
- **System Status**: Real-time status of all agency APIs

## Architecture

The dashboard is built using:

- **Backend**: Flask (Python) application that communicates with the Federation Hub
- **Frontend**: HTML, CSS (Bootstrap), and JavaScript
- **Data Visualization**: Matplotlib for server-side chart generation
- **Data Access**: API calls to the Federation Hub which coordinates cross-agency data sharing

## Data Integration

This dashboard leverages the Federation Hub's capabilities:

1. **Federated Queries**: Standardized mechanism to query data across agencies
2. **Joint Analysis**: Coordinated analysis of data from multiple sources
3. **Shared Visualizations**: Combined views of multi-agency data
4. **Centralized Monitoring**: Unified system status tracking

## Requirements

- Python 3.10+
- Flask
- Matplotlib
- Numpy
- Pandas
- Seaborn
- Requests

## Setup and Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install flask matplotlib numpy pandas seaborn requests
   ```

3. Configure the Federation Hub endpoint:
   ```bash
   export FEDERATION_API_URL=http://localhost:8000/api/v1/federation
   ```

4. Start the dashboard application:
   ```bash
   python app.py
   ```

5. Access the dashboard in your browser at http://localhost:8050

## Development

### Project Structure

```
dashboard/
├── app.py                 # Flask application
├── README.md              # Documentation
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   │   └── dashboard.css  # Custom styling
│   ├── js/                # JavaScript
│   │   └── dashboard.js   # Dashboard functionality
│   └── img/               # Images
└── templates/             # HTML templates
    └── index.html         # Main dashboard template
```

### API Endpoints

The dashboard provides the following API endpoints:

- `/api/summary`: Summary statistics across all agencies
- `/api/cdc/cases`: CDC case data
- `/api/epa/air_quality`: EPA air quality data
- `/api/fema/resources`: FEMA resource data
- `/api/correlation`: Correlation analysis between cases and environmental factors
- `/api/case_map`: Case distribution map visualization
- `/api/subtype_distribution`: Virus subtype distribution visualization
- `/api/air_quality_trends`: Air quality trends visualization
- `/api/resource_allocation`: Resource allocation visualization
- `/api/correlation_chart`: Correlation chart visualization

## Federation API Integration

The dashboard integrates with these Federation Hub endpoints:

- `POST /api/v1/federation/query`: For federated queries across agencies
- `POST /api/v1/federation/analysis`: For joint analysis requests
- `GET /api/v1/federation/analysis/{analysis_id}`: To retrieve analysis results

## License

[License information]

## Contact

[Contact information]