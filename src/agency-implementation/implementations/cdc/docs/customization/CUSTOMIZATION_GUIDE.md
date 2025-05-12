# CDC Implementation Customization Guide

This guide provides information on customizing and extending the CDC implementation of the agency foundation to meet specific public health requirements.

## Overview

The CDC implementation is designed to be highly customizable, allowing you to adapt the system to different disease surveillance needs, data sources, and reporting requirements. The main extension points include:

- Disease models and definitions
- Data source integrations
- Detection algorithms
- Notification channels
- Reporting templates
- Visualization components

## Configuration Customization

### Basic Configuration Changes

The primary configuration file is located at `/config/agency.json`. This file contains settings for:

- Agency information
- Enabled services
- Service-specific settings
- Integration points
- Extension configurations

Example of modifying the surveillance refresh interval:

```json
{
  "services": {
    "disease_surveillance": {
      "data_refresh_interval": 1800,  // Change from 3600 to 1800 seconds
      "notification_threshold": 0.75,
      "data_sources": [ ... ]
    }
  }
}
```

### Environment Variables

The following environment variables can be configured:

- `CDC_LAB_DB_CONNECTION`: Connection string for the clinical lab database
- `CDC_HAN_CREDENTIALS`: Credentials for the Health Alert Network
- `HMS_API_ENDPOINT`: URL of the HMS API endpoint
- `HMS_API_TOKEN`: Authentication token for HMS API

## Adding New Disease Definitions

Disease definitions are stored in a database (typically MongoDB). You can add new diseases by:

1. Creating a new disease model object
2. Setting appropriate parameters for transmission, severity, etc.
3. Adding to the disease registry

Example code for adding a new disease:

```python
from cdc.models.disease_model import Disease, DiseaseCategory, TransmissionType, SeverityLevel

# Create new disease
new_disease = Disease(
    disease_id="dengue_fever_2023",
    name="Dengue Fever",
    scientific_name="Dengue virus",
    category=DiseaseCategory.VECTOR_BORNE,
    transmission_types=[TransmissionType.VECTOR_BORNE],
    incubation_period_days={"min": 3, "max": 14, "mean": 7},
    infectious_period_days={"min": 4, "max": 10, "mean": 7},
    r0_estimate=2.5,
    case_fatality_rate=0.01,
    severity_level=SeverityLevel.MODERATE,
    reportable=True,
    description="Mosquito-borne viral disease that has rapidly spread globally",
    symptoms=["fever", "headache", "muscle and joint pain", "rash"],
    preventive_measures=["mosquito control", "personal protection"],
    treatments=["supportive care", "fluid management"]
)

# Register with disease registry
disease_registry.register_disease(new_disease)
```

## Adding Data Sources

### Supported Data Source Types

The CDC implementation supports these data source types:

1. **API-based**: REST/GraphQL APIs from state health departments, laboratories, etc.
2. **Database**: Direct database connections for internal data
3. **File-based**: Parsing structured files (CSV, JSON, FASTA sequences)

### Implementing a Custom Data Source

To add a new data source:

1. Create a class that extends one of the base data source types
2. Implement the required fetch_data method
3. Register it with the extension registry

Example of creating a custom API-based data source:

```python
from agency_implementation.foundation.extension_points.data_sources.api_based import APIBasedDataSource

class StateHealthDepartmentDataSource(APIBasedDataSource):
    """Data source for state health department API."""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.state_code = config.get("state_code")
        
    async def fetch_data(self):
        """Fetch disease surveillance data from state health department."""
        url = f"https://health.{self.state_code}.gov/api/v1/disease-data"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return self.transform_data(data)
            else:
                self.logger.error(f"Error fetching data: {response.status}")
                return None
                
    def transform_data(self, raw_data):
        """Transform API data into standardized format."""
        # Implementation specific to state health department format
        transformed_data = {
            "source": self.state_code,
            "timestamp": datetime.now().isoformat(),
            "cases": []
        }
        
        for record in raw_data.get("records", []):
            transformed_data["cases"].append({
                "disease": record.get("disease_name"),
                "count": record.get("case_count"),
                "location": {
                    "county": record.get("county"),
                    "state": self.state_code
                },
                "date": record.get("report_date")
            })
            
        return transformed_data

# Register with extension registry
extension_registry.register_data_source(
    "state_health_api",
    StateHealthDepartmentDataSource
)
```

## Customizing Detection Algorithms

### Available Detection Algorithms

The CDC implementation includes these anomaly detection algorithms:

1. **CUSUM** (Cumulative Sum Control Chart)
2. **EWMA** (Exponentially Weighted Moving Average)
3. **Regression-based** prediction models
4. **Spatial clustering** for geographic hotspot detection

### Adding a Custom Detection Algorithm

To add a new detection algorithm:

1. Create a class that implements the `DetectionAlgorithm` interface
2. Implement the detect method
3. Register with the detection service

Example:

```python
from typing import Dict, List, Any
from agency_implementation.foundation.core_services.detection_service import DetectionAlgorithm

class BayesianChangePointDetection(DetectionAlgorithm):
    """Bayesian change point detection algorithm."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_probability = config.get("min_probability", 0.8)
        
    async def detect(self, data: List[Dict[str, Any]], baseline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect change points using Bayesian methods.
        
        Args:
            data: Time series data to analyze
            baseline: Historical baseline data
            
        Returns:
            List of detected anomalies with confidence scores
        """
        anomalies = []
        
        # Implementation of Bayesian change point detection
        # This would use statistical libraries like PyMC3 or custom implementations
        
        return anomalies

# Register with detection service
detection_service.register_algorithm("bayesian_changepoint", BayesianChangePointDetection)
```

## Customizing Visualization Components

### Available Visualization Components

The CDC implementation includes these visualization components:

1. **Choropleth Maps**: Geographic disease distribution
2. **Time Series Charts**: Disease trends over time
3. **Heatmaps**: Correlation between factors
4. **Network Diagrams**: Disease transmission paths

### Creating a Custom Visualization Component

To add a new visualization component:

1. Create a class that extends `VisualizationComponent`
2. Implement the required render methods
3. Register with the visualization service

Example:

```python
from agency_implementation.foundation.extension_points.visualization_components import VisualizationComponent

class OutbreakClusterMap(VisualizationComponent):
    """
    Visualization component for displaying outbreak clusters.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.map_provider = config.get("map_provider", "leaflet")
        self.color_scheme = config.get("color_scheme", "viridis")
        
    async def render(self, data, options=None):
        """
        Render the outbreak cluster map.
        
        Args:
            data: Outbreak data to visualize
            options: Additional rendering options
            
        Returns:
            HTML/SVG representation of the visualization
        """
        # Implementation would use a visualization library like folium, plotly, or D3.js
        # to generate an interactive cluster map
        
        return html_content
        
    async def export(self, data, format="png", options=None):
        """
        Export the visualization to the specified format.
        
        Args:
            data: Data to visualize
            format: Output format (png, svg, pdf)
            options: Additional export options
            
        Returns:
            Binary data of the exported visualization
        """
        # Implementation for exporting the visualization
        
        return binary_data

# Register with visualization service
visualization_service.register_component("outbreak_cluster_map", OutbreakClusterMap)
```

## Integration with HMS

The CDC implementation integrates with the Health Management System (HMS) for:

1. **Data Exchange**: Sharing disease surveillance data
2. **Alert Distribution**: Distributing public health alerts
3. **Reporting**: Generating standardized reports

### Customizing HMS Integration

You can customize the HMS integration by:

1. Modifying the config in `agency.json`:

```json
"integrations": {
  "hms_api": {
    "enabled": true,
    "endpoint": "${HMS_API_ENDPOINT}",
    "auth_token_env": "HMS_API_TOKEN",
    "services": [
      "data_exchange",
      "alert_distribution",
      "reporting"
    ],
    "custom_settings": {
      "data_format_version": "2.1",
      "include_metadata": true
    }
  }
}
```

2. Extending the `HMSIntegration` class to add custom functionality:

```python
from cdc.src.integration.hms_integration import HMSIntegration

class EnhancedHMSIntegration(HMSIntegration):
    """
    Enhanced HMS integration with additional capabilities.
    """
    
    async def sync_vaccine_data(self, vaccine_data):
        """
        Sync vaccine inventory and administration data with HMS.
        
        Args:
            vaccine_data: Vaccine data to synchronize
            
        Returns:
            Synchronization result
        """
        # Implementation for vaccine data synchronization
        
        return result
```

## Best Practices

When customizing the CDC implementation:

1. **Maintain Separation of Concerns**:
   - Keep domain logic separate from integration code
   - Use the extension point system for customizations

2. **Follow Naming Conventions**:
   - Use descriptive names for custom components
   - Prefix CDC-specific extensions with "CDC"

3. **Document Customizations**:
   - Include detailed comments in custom code
   - Update this guide when adding major customizations

4. **Test Thoroughly**:
   - Write unit tests for custom components
   - Test integrations with mock data before deployment

5. **Version Control**:
   - Track customizations in version control
   - Document changes in commit messages

## Deployment Considerations

When deploying customized implementations:

1. **Configuration Management**:
   - Use environment-specific configuration files
   - Manage secrets securely (not in config files)

2. **Scaling**:
   - Ensure data sources can handle increased load
   - Consider horizontal scaling for processing services

3. **Monitoring**:
   - Set up alerts for service disruptions
   - Monitor data source connectivity

4. **Compliance**:
   - Ensure PII/PHI handling meets HIPAA requirements
   - Document compliance measures

## Support Resources

- [CDC Technical Documentation](https://your-docs-site.gov/cdc-implementation)
- [Agency Foundation Documentation](https://your-docs-site.gov/agency-foundation)
- [HMS Integration Guide](https://your-docs-site.gov/hms-integration)
- Technical Support: techsupport@your-agency.gov