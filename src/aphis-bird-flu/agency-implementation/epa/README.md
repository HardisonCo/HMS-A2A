# EPA Implementation for Adaptive Surveillance and Response System

This directory contains the EPA implementation of the Adaptive Surveillance and Response System (ASRS) architecture, based on the successful APHIS Bird Flu Tracking System model.

## Core Service Components

The EPA implementation includes three primary service components:

1. **Environmental Quality Monitoring Service**
   - Manages monitoring sites, environmental measurements, and threshold alerts
   - Supports air, water, and soil quality monitoring
   - Provides AQI calculation and statistical analysis
   - Implements automated data validation and quality assurance

2. **Compliance Surveillance Service**
   - Tracks regulated facilities, permits, and compliance status
   - Manages inspections and enforcement actions
   - Prioritizes inspections based on risk assessment
   - Generates compliance history and regional reports

3. **Pollution Modeling Service**
   - Manages pollution dispersion models and emission sources
   - Executes model runs and analyzes results
   - Performs scenario comparisons
   - Conducts environmental impact assessments

## Domain Models

The implementation includes domain models for all key aspects of environmental regulation:

- **Environmental Quality**
  - Monitoring sites, measurements, and alerts
  - Air, water, and soil quality parameters
  - Standards and thresholds for regulatory compliance

- **Regulatory Compliance**
  - Regulated facilities, permits, and inspection records
  - Enforcement actions and corrective measures
  - Compliance reports and regulatory frameworks

- **Pollution Modeling**
  - Dispersion models and emission sources
  - Modeling runs, scenarios, and results
  - Impact assessments and receptors

## External System Integration

Each service component includes adapters for integration with external systems:

- **Environmental Quality**
  - Monitoring system integration for automated data collection
  - Alert notification system for threshold exceedances

- **Compliance Surveillance**
  - Facility registry for regulated entity information
  - Compliance reporting system for state/federal reporting

- **Pollution Modeling**
  - External modeling systems for advanced simulations
  - Result visualization and post-processing services

## Usage

Each service can be used independently or together through the EPA supervisor module. Key functionalities include:

### Environmental Quality

```python
# Initialize monitoring service
monitoring_service = EnvironmentalQualityMonitoringService(
    site_repository, 
    measurement_repository,
    alert_repository
)

# Create monitoring site
site = monitoring_service.create_monitoring_site({
    'site_name': 'Downtown Air Quality',
    'location': {'latitude': 38.8977, 'longitude': -77.0365},
    'site_type': 'ambient_air',
    'parameters_monitored': ['PM25', 'PM10', 'OZONE', 'NO2']
})

# Record measurement
measurement = monitoring_service.create_measurement({
    'site_id': site.id,
    'parameter': 'PM25',
    'value': 12.5,
    'unit': 'μg/m³',
    'timestamp': '2025-05-09T08:00:00'
})

# Calculate AQI
aqi = monitoring_service.calculate_aqi(site.id)
```

### Compliance Surveillance

```python
# Initialize compliance service
compliance_service = ComplianceSurveillanceService(
    facility_repository,
    permit_repository,
    inspection_repository,
    enforcement_repository
)

# Create regulated facility
facility = compliance_service.create_facility({
    'facility_name': 'ABC Manufacturing',
    'facility_type': 'Chemical Manufacturing',
    'location': {'latitude': 39.1031, 'longitude': -77.5366},
    'epa_region': '03'
})

# Create inspection
inspection = compliance_service.create_inspection({
    'facility_id': facility.id,
    'inspection_date': '2025-05-01',
    'inspector_id': 'INS-001',
    'inspection_type': 'Routine',
    'regulatory_framework': 'CLEAN_AIR_ACT'
})

# Generate compliance history
history = compliance_service.generate_compliance_history(facility.id)
```

### Pollution Modeling

```python
# Initialize modeling service
modeling_service = PollutionModelingService(
    model_repository,
    source_repository,
    run_repository,
    result_repository
)

# Create emission source
source = modeling_service.create_emission_source({
    'source_name': 'Stack 1',
    'source_type': 'point',
    'location': {'latitude': 39.1031, 'longitude': -77.5366},
    'pollutant_types': ['PM25', 'SO2', 'NOX'],
    'emission_rates': {'PM25': 2.5, 'SO2': 10.0, 'NOX': 15.0}
})

# Create and execute model run
run = modeling_service.create_model_run(
    model_id='model-001',
    emission_source_ids=[source.id],
    start_time='2025-05-09T00:00:00',
    end_time='2025-05-09T23:59:59',
    spatial_domain={
        'min_latitude': 39.0,
        'max_latitude': 39.2,
        'min_longitude': -77.6,
        'max_longitude': -77.4
    }
)

result = modeling_service.execute_model_run(run.id)
```

## Implementation

This implementation follows the guidance provided in the [Federal Agency Implementation Plan](../../FEDERAL_AGENCY_IMPLEMENTATION_PLAN.md) and builds on the patterns established in the APHIS Bird Flu Tracking System. It addresses the specific focus areas for the EPA:

- Environmental quality monitoring
- Compliance surveillance
- Enforcement resource optimization
- Pollution impact modeling
- Violation risk assessment