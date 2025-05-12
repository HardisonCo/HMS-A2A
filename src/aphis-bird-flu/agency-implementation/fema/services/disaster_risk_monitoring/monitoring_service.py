"""
Disaster Risk Monitoring Service for the FEMA implementation.

This service provides functionality for monitoring disaster risks,
including hazard measurements, alerts, forecasting, and risk assessment.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import logging
import uuid
import json
import math

from agency_implementation.fema.models.disaster import (
    HazardZone, HazardMeasurement, DisasterEvent, DisasterAlert,
    RiskAssessment, ForecastModel, DisasterForecast
)
from agency_implementation.fema.models.base import (
    DisasterType, DisasterSeverity, AlertLevel, MeasurementUnit, DataSource
)
from .repository import (
    HazardZoneRepository, HazardMeasurementRepository, DisasterEventRepository,
    DisasterAlertRepository, RiskAssessmentRepository, ForecastModelRepository,
    DisasterForecastRepository
)
from .adapters import (
    MonitoringSystemAdapter, AlertNotificationAdapter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DisasterRiskMonitoringService:
    """
    Service for disaster risk monitoring.
    
    This service provides functionality for:
    1. Hazard zone management (create, update, query)
    2. Hazard measurement collection and analysis
    3. Disaster event tracking
    4. Alert generation and management
    5. Risk assessment
    6. Disaster forecasting
    """
    
    def __init__(
        self,
        hazard_zone_repository: HazardZoneRepository,
        hazard_measurement_repository: HazardMeasurementRepository,
        disaster_event_repository: DisasterEventRepository,
        disaster_alert_repository: DisasterAlertRepository,
        risk_assessment_repository: RiskAssessmentRepository,
        forecast_model_repository: ForecastModelRepository,
        disaster_forecast_repository: DisasterForecastRepository,
        monitoring_adapters: Dict[str, MonitoringSystemAdapter] = None,
        notification_adapters: Dict[str, AlertNotificationAdapter] = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the service.
        
        Args:
            hazard_zone_repository: Repository for hazard zones
            hazard_measurement_repository: Repository for hazard measurements
            disaster_event_repository: Repository for disaster events
            disaster_alert_repository: Repository for disaster alerts
            risk_assessment_repository: Repository for risk assessments
            forecast_model_repository: Repository for forecast models
            disaster_forecast_repository: Repository for disaster forecasts
            monitoring_adapters: Dict of adapters for external monitoring systems
            notification_adapters: Dict of adapters for alert notifications
            config: Service configuration
        """
        self.hazard_zone_repository = hazard_zone_repository
        self.hazard_measurement_repository = hazard_measurement_repository
        self.disaster_event_repository = disaster_event_repository
        self.disaster_alert_repository = disaster_alert_repository
        self.risk_assessment_repository = risk_assessment_repository
        self.forecast_model_repository = forecast_model_repository
        self.disaster_forecast_repository = disaster_forecast_repository
        self.monitoring_adapters = monitoring_adapters or {}
        self.notification_adapters = notification_adapters or {}
        self.config = config or {}
        
        # Initialize thresholds for hazard parameters
        self.thresholds = self.config.get('thresholds', {
            'wind_speed': 74.0,  # Hurricane force winds (mph)
            'precipitation': 2.0,  # Heavy rainfall (inches in 24 hours)
            'river_level': 15.0,  # Flood stage (feet)
            'wave_height': 20.0,  # Dangerous wave height (feet)
            'temperature': 100.0,  # Extreme heat (°F)
            'magnitude': 5.0,  # Moderate earthquake (Richter)
            'drought_index': 400,  # Severe drought (Palmer Index)
            'air_quality': 150.0,  # Unhealthy air quality (AQI)
            'snowfall': 12.0,  # Heavy snowfall (inches in 24 hours)
            'wildfire_danger': 4.0  # Very high fire danger (index)
        })
        
        # Set up automatic data validation
        self.auto_validate = self.config.get('auto_validate', True)
        
        # Initialize alert levels
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'wind_speed': {
                'ADVISORY': 30.0,
                'WATCH': 50.0,
                'WARNING': 65.0,
                'EMERGENCY': 74.0
            },
            'precipitation': {
                'ADVISORY': 0.5,
                'WATCH': 1.0,
                'WARNING': 2.0,
                'EMERGENCY': 4.0
            },
            'river_level': {
                'ADVISORY': 10.0,
                'WATCH': 12.0,
                'WARNING': 15.0,
                'EMERGENCY': 18.0
            },
            'magnitude': {
                'ADVISORY': 3.0,
                'WATCH': 4.0,
                'WARNING': 5.0,
                'EMERGENCY': 6.0
            }
        })
        
        logger.info("DisasterRiskMonitoringService initialized")
    
    # Hazard Zone Management Methods
    
    def get_hazard_zone(self, zone_id: str) -> Optional[HazardZone]:
        """
        Get a hazard zone by ID.
        
        Args:
            zone_id: The ID of the zone to retrieve
            
        Returns:
            The zone if found, None otherwise
        """
        return self.hazard_zone_repository.get_by_id(zone_id)
    
    def get_all_hazard_zones(self) -> List[HazardZone]:
        """
        Get all hazard zones.
        
        Returns:
            List of all zones
        """
        return self.hazard_zone_repository.get_all()
    
    def create_hazard_zone(self, zone_data: Dict[str, Any]) -> HazardZone:
        """
        Create a new hazard zone.
        
        Args:
            zone_data: Dictionary with zone data
            
        Returns:
            The created zone
            
        Raises:
            ValueError: If zone data is invalid
        """
        # Validate required fields
        required_fields = ['zone_name', 'hazard_type', 'risk_level', 'boundaries']
        for field in required_fields:
            if field not in zone_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the zone
        zone = HazardZone(**zone_data)
        
        # Save the zone
        created_zone = self.hazard_zone_repository.create(zone)
        
        logger.info(f"Created new hazard zone with ID: {created_zone.id}")
        return created_zone
    
    def update_hazard_zone(self, zone_id: str, updates: Dict[str, Any]) -> Optional[HazardZone]:
        """
        Update an existing hazard zone.
        
        Args:
            zone_id: ID of the zone to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated zone or None if zone not found
        """
        # Get the zone
        zone = self.hazard_zone_repository.get_by_id(zone_id)
        if not zone:
            logger.warning(f"Zone not found for update: {zone_id}")
            return None
        
        # Update the zone
        for key, value in updates.items():
            setattr(zone, key, value)
            
        # Update timestamp
        zone.updated_at = datetime.now().isoformat()
        
        # Save the updated zone
        updated_zone = self.hazard_zone_repository.update(zone)
        
        logger.info(f"Updated zone with ID: {zone_id}")
        return updated_zone
    
    def find_zones_by_hazard_type(self, hazard_type: str) -> List[HazardZone]:
        """
        Find zones for a specific hazard type.
        
        Args:
            hazard_type: Type of hazard
            
        Returns:
            List of zones for the specified hazard type
        """
        return self.hazard_zone_repository.find_by_hazard_type(hazard_type)
    
    def find_zones_by_risk_level(self, risk_level: str) -> List[HazardZone]:
        """
        Find zones with a specific risk level.
        
        Args:
            risk_level: Risk level
            
        Returns:
            List of zones with the specified risk level
        """
        return self.hazard_zone_repository.find_by_risk_level(risk_level)
    
    def find_zones_by_jurisdiction(self, jurisdiction: str) -> List[HazardZone]:
        """
        Find zones in a specific jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction name
            
        Returns:
            List of zones in the specified jurisdiction
        """
        return self.hazard_zone_repository.find_by_jurisdiction(jurisdiction)
    
    # Hazard Measurement Management Methods
    
    def get_measurement(self, measurement_id: str) -> Optional[HazardMeasurement]:
        """
        Get a hazard measurement by ID.
        
        Args:
            measurement_id: The ID of the measurement to retrieve
            
        Returns:
            The measurement if found, None otherwise
        """
        return self.hazard_measurement_repository.get_by_id(measurement_id)
    
    def create_measurement(self, measurement_data: Dict[str, Any]) -> HazardMeasurement:
        """
        Create a new hazard measurement.
        
        Args:
            measurement_data: Dictionary with measurement data
            
        Returns:
            The created measurement
            
        Raises:
            ValueError: If measurement data is invalid
        """
        # Validate required fields
        required_fields = ['parameter', 'value', 'unit', 'location', 'data_source']
        for field in required_fields:
            if field not in measurement_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the measurement
        measurement = HazardMeasurement(**measurement_data)
        
        # Perform automatic validation if enabled
        if self.auto_validate:
            self._validate_measurement(measurement)
        
        # Save the measurement
        created_measurement = self.hazard_measurement_repository.create(measurement)
        
        # Check for threshold exceedances
        self._check_thresholds(created_measurement)
        
        logger.info(f"Created new measurement with ID: {created_measurement.id}")
        return created_measurement
    
    def batch_create_measurements(self, measurements_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple hazard measurements in batch.
        
        Args:
            measurements_data: List of dictionaries with measurement data
            
        Returns:
            Dictionary with results including created measurements and errors
        """
        created_measurements = []
        errors = []
        
        for data in measurements_data:
            try:
                measurement = self.create_measurement(data)
                created_measurements.append(measurement)
            except Exception as e:
                error_info = {
                    "data": data,
                    "error": str(e)
                }
                errors.append(error_info)
                logger.error(f"Error creating measurement: {str(e)}")
        
        result = {
            "total": len(measurements_data),
            "created": len(created_measurements),
            "errors": len(errors),
            "measurements": [m.id for m in created_measurements],
            "error_details": errors[:10]  # Limit error details
        }
        
        logger.info(f"Batch created {len(created_measurements)} measurements with {len(errors)} errors")
        return result
    
    def find_measurements_by_parameter(self, parameter: str) -> List[HazardMeasurement]:
        """
        Find measurements for a specific parameter.
        
        Args:
            parameter: Measurement parameter
            
        Returns:
            List of measurements for the parameter
        """
        return self.hazard_measurement_repository.find_by_parameter(parameter)
    
    def find_measurements_by_hazard_type(self, hazard_type: str) -> List[HazardMeasurement]:
        """
        Find measurements for a specific hazard type.
        
        Args:
            hazard_type: Type of hazard
            
        Returns:
            List of measurements for the hazard type
        """
        return self.hazard_measurement_repository.find_by_hazard_type(hazard_type)
    
    def find_measurements_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[HazardMeasurement]:
        """
        Find measurements within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of measurements within the date range
        """
        # Convert to string if datetime objects
        if isinstance(start_date, datetime):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime):
            end_date = end_date.isoformat()
            
        return self.hazard_measurement_repository.find_by_date_range(start_date, end_date)
    
    def find_exceeded_thresholds(self) -> List[HazardMeasurement]:
        """
        Find measurements that exceed their respective thresholds.
        
        Returns:
            List of measurements exceeding thresholds
        """
        return self.hazard_measurement_repository.find_exceeded_thresholds(self.thresholds)
    
    def import_measurements_from_monitoring_system(
        self,
        system_key: str,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Import measurements from an external monitoring system.
        
        Args:
            system_key: Key for the monitoring system adapter
            params: Parameters for the import
            
        Returns:
            Dictionary with import results
            
        Raises:
            ValueError: If system_key is invalid
            RuntimeError: If monitoring adapter is not found
        """
        if not system_key:
            raise ValueError("System key is required")
            
        adapter = self.monitoring_adapters.get(system_key)
        if not adapter:
            raise RuntimeError(f"Monitoring system adapter '{system_key}' not configured")
        
        params = params or {}
        logger.info(f"Importing measurements from {system_key} with params: {params}")
        
        # Fetch data from monitoring system
        monitoring_data = adapter.fetch_data(**params)
        
        # Process results
        imported_count = 0
        errors = []
        
        for record in monitoring_data:
            try:
                # Convert to measurement
                measurement = adapter.convert_to_measurement(record)
                if not measurement:
                    errors.append(f"Failed to convert record: {record.get('id', 'unknown')}")
                    continue
                
                # Save the measurement
                self.hazard_measurement_repository.create(measurement)
                
                # Check for threshold exceedances
                self._check_thresholds(measurement)
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"Error processing record {record.get('id', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            'total_records': len(monitoring_data),
            'imported_count': imported_count,
            'error_count': len(errors),
            'errors': errors[:10]  # Limit error list
        }
        
        logger.info(f"Monitoring import complete: {imported_count} measurements imported, {len(errors)} errors")
        return result
    
    # Disaster Event Management Methods
    
    def get_disaster_event(self, event_id: str) -> Optional[DisasterEvent]:
        """
        Get a disaster event by ID.
        
        Args:
            event_id: The ID of the event to retrieve
            
        Returns:
            The event if found, None otherwise
        """
        return self.disaster_event_repository.get_by_id(event_id)
    
    def get_all_disaster_events(self) -> List[DisasterEvent]:
        """
        Get all disaster events.
        
        Returns:
            List of all events
        """
        return self.disaster_event_repository.get_all()
    
    def create_disaster_event(self, event_data: Dict[str, Any]) -> DisasterEvent:
        """
        Create a new disaster event.
        
        Args:
            event_data: Dictionary with event data
            
        Returns:
            The created event
            
        Raises:
            ValueError: If event data is invalid
        """
        # Validate required fields
        required_fields = ['event_name', 'disaster_type', 'severity', 'location']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set status to ACTIVE if not specified
        if 'status' not in event_data:
            event_data['status'] = "ACTIVE"
            
        # Set start time if not specified
        if 'start_time' not in event_data:
            event_data['start_time'] = datetime.now().isoformat()
        
        # Create the event
        event = DisasterEvent(**event_data)
        
        # Save the event
        created_event = self.disaster_event_repository.create(event)
        
        logger.info(f"Created new disaster event with ID: {created_event.id}")
        return created_event
    
    def update_disaster_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[DisasterEvent]:
        """
        Update an existing disaster event.
        
        Args:
            event_id: ID of the event to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated event or None if event not found
        """
        # Get the event
        event = self.disaster_event_repository.get_by_id(event_id)
        if not event:
            logger.warning(f"Event not found for update: {event_id}")
            return None
        
        # Update the event
        for key, value in updates.items():
            setattr(event, key, value)
            
        # Update timestamp
        event.updated_at = datetime.now().isoformat()
        
        # Save the updated event
        updated_event = self.disaster_event_repository.update(event)
        
        logger.info(f"Updated event with ID: {event_id}")
        return updated_event
    
    def close_disaster_event(self, event_id: str, end_time: str = None) -> Optional[DisasterEvent]:
        """
        Close a disaster event.
        
        Args:
            event_id: ID of the event to close
            end_time: Optional end time (defaults to now)
            
        Returns:
            The updated event or None if event not found
        """
        # Get the event
        event = self.disaster_event_repository.get_by_id(event_id)
        if not event:
            logger.warning(f"Event not found for closure: {event_id}")
            return None
        
        # Close the event
        event.close_event(end_time)
        
        # Save the updated event
        updated_event = self.disaster_event_repository.update(event)
        
        logger.info(f"Closed event with ID: {event_id}")
        return updated_event
    
    def find_active_events(self) -> List[DisasterEvent]:
        """
        Find active disaster events.
        
        Returns:
            List of active events
        """
        return self.disaster_event_repository.find_active_events()
    
    def find_events_by_disaster_type(self, disaster_type: str) -> List[DisasterEvent]:
        """
        Find events by disaster type.
        
        Args:
            disaster_type: Type of disaster
            
        Returns:
            List of events of the specified type
        """
        return self.disaster_event_repository.find_by_disaster_type(disaster_type)
    
    def find_events_by_severity(self, severity: str) -> List[DisasterEvent]:
        """
        Find events by severity.
        
        Args:
            severity: Severity level
            
        Returns:
            List of events with the specified severity
        """
        return self.disaster_event_repository.find_by_severity(severity)
    
    def find_events_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[DisasterEvent]:
        """
        Find events within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of events within the date range
        """
        # Convert to string if datetime objects
        if isinstance(start_date, datetime):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime):
            end_date = end_date.isoformat()
            
        return self.disaster_event_repository.find_by_date_range(start_date, end_date)
    
    # Alert Management Methods
    
    def get_alert(self, alert_id: str) -> Optional[DisasterAlert]:
        """
        Get a disaster alert by ID.
        
        Args:
            alert_id: The ID of the alert to retrieve
            
        Returns:
            The alert if found, None otherwise
        """
        return self.disaster_alert_repository.get_by_id(alert_id)
    
    def get_active_alerts(self) -> List[DisasterAlert]:
        """
        Get all active disaster alerts.
        
        Returns:
            List of active alerts
        """
        return self.disaster_alert_repository.find_active_alerts()
    
    def create_alert(self, alert_data: Dict[str, Any]) -> DisasterAlert:
        """
        Create a new disaster alert.
        
        Args:
            alert_data: Dictionary with alert data
            
        Returns:
            The created alert
            
        Raises:
            ValueError: If alert data is invalid
        """
        # Validate required fields
        required_fields = ['hazard_type', 'alert_level', 'affected_area', 'message']
        for field in required_fields:
            if field not in alert_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set status to ACTIVE if not specified
        if 'status' not in alert_data:
            alert_data['status'] = "ACTIVE"
            
        # Set timestamp if not specified
        if 'timestamp' not in alert_data:
            alert_data['timestamp'] = datetime.now().isoformat()
        
        # Create the alert
        alert = DisasterAlert(**alert_data)
        
        # Save the alert
        created_alert = self.disaster_alert_repository.create(alert)
        
        # Send notifications
        self._send_alert_notifications(created_alert)
        
        logger.info(f"Created new disaster alert with ID: {created_alert.id}")
        return created_alert
    
    def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> Optional[DisasterAlert]:
        """
        Update an existing disaster alert.
        
        Args:
            alert_id: ID of the alert to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated alert or None if alert not found
        """
        # Get the alert
        alert = self.disaster_alert_repository.get_by_id(alert_id)
        if not alert:
            logger.warning(f"Alert not found for update: {alert_id}")
            return None
        
        # Check if alert level is changing
        alert_level_changed = 'alert_level' in updates and updates['alert_level'] != alert.alert_level
        
        # Update the alert
        for key, value in updates.items():
            setattr(alert, key, value)
            
        # Update timestamp
        alert.updated_at = datetime.now().isoformat()
        
        # Save the updated alert
        updated_alert = self.disaster_alert_repository.update(alert)
        
        # Send notifications if alert level changed
        if alert_level_changed:
            self._send_alert_notifications(updated_alert, is_update=True)
        
        logger.info(f"Updated alert with ID: {alert_id}")
        return updated_alert
    
    def close_alert(self, alert_id: str, resolution_notes: str = None) -> Optional[DisasterAlert]:
        """
        Close a disaster alert.
        
        Args:
            alert_id: ID of the alert to close
            resolution_notes: Optional notes about resolution
            
        Returns:
            The updated alert or None if alert not found
        """
        # Get the alert
        alert = self.disaster_alert_repository.get_by_id(alert_id)
        if not alert:
            logger.warning(f"Alert not found for closure: {alert_id}")
            return None
        
        # Close the alert
        alert.close_alert(resolution_notes)
        
        # Save the updated alert
        updated_alert = self.disaster_alert_repository.update(alert)
        
        # Send notifications about closure
        self._send_alert_notifications(updated_alert, is_closure=True)
        
        logger.info(f"Closed alert with ID: {alert_id}")
        return updated_alert
    
    def find_alerts_by_hazard_type(self, hazard_type: str) -> List[DisasterAlert]:
        """
        Find alerts by hazard type.
        
        Args:
            hazard_type: Type of hazard
            
        Returns:
            List of alerts for the specified hazard type
        """
        return self.disaster_alert_repository.find_by_hazard_type(hazard_type)
    
    def find_alerts_by_level(self, alert_level: str) -> List[DisasterAlert]:
        """
        Find alerts by alert level.
        
        Args:
            alert_level: Alert level
            
        Returns:
            List of alerts with the specified level
        """
        return self.disaster_alert_repository.find_by_alert_level(alert_level)
    
    def find_alerts_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[DisasterAlert]:
        """
        Find alerts within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of alerts within the date range
        """
        # Convert to string if datetime objects
        if isinstance(start_date, datetime):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime):
            end_date = end_date.isoformat()
            
        return self.disaster_alert_repository.find_by_date_range(start_date, end_date)
    
    def generate_alert_from_measurements(self, parameter: str, location: Dict[str, Any] = None) -> Optional[DisasterAlert]:
        """
        Generate an alert based on recent measurements.
        
        Args:
            parameter: Parameter to check (e.g., 'wind_speed')
            location: Optional location to filter measurements
            
        Returns:
            Created alert or None if no threshold exceeded
        """
        # Get recent measurements for the parameter
        measurements = self.hazard_measurement_repository.find_by_parameter(parameter)
        
        # Filter by recency (last 24 hours)
        now = datetime.now()
        yesterday = now - timedelta(hours=24)
        yesterday_iso = yesterday.isoformat()
        
        recent_measurements = [
            m for m in measurements 
            if hasattr(m, 'timestamp') and m.timestamp >= yesterday_iso
        ]
        
        if not recent_measurements:
            logger.info(f"No recent measurements found for parameter: {parameter}")
            return None
        
        # Filter by location if specified
        if location:
            # Simple location filtering (would be more complex with real geospatial queries)
            lat = location.get('latitude')
            lon = location.get('longitude')
            radius = location.get('radius', 50)  # default 50 km radius
            
            filtered_measurements = []
            for m in recent_measurements:
                if hasattr(m, 'location') and m.location:
                    m_lat = getattr(m.location, 'latitude', None)
                    m_lon = getattr(m.location, 'longitude', None)
                    
                    if m_lat is not None and m_lon is not None:
                        # Simple distance calculation (not accounting for Earth's curvature)
                        distance = math.sqrt((m_lat - lat)**2 + (m_lon - lon)**2) * 111  # rough km conversion
                        if distance <= radius:
                            filtered_measurements.append(m)
            
            recent_measurements = filtered_measurements
            
            if not recent_measurements:
                logger.info(f"No measurements found in specified location for parameter: {parameter}")
                return None
        
        # Find maximum value
        max_measurement = max(recent_measurements, key=lambda m: m.value if hasattr(m, 'value') else 0)
        
        # Determine if alert should be generated
        if not hasattr(max_measurement, 'value'):
            return None
            
        max_value = max_measurement.value
        
        # Get alert thresholds for this parameter
        parameter_thresholds = self.alert_thresholds.get(parameter, {})
        if not parameter_thresholds:
            # If no specific thresholds, check against general threshold
            threshold = self.thresholds.get(parameter)
            if threshold and max_value > threshold:
                # Generate EMERGENCY alert
                alert_level = "EMERGENCY"
            else:
                return None
        else:
            # Determine alert level based on thresholds
            alert_level = None
            for level, threshold in sorted(parameter_thresholds.items(), key=lambda x: x[1], reverse=True):
                if max_value >= threshold:
                    alert_level = level
                    break
                    
            if not alert_level:
                return None
        
        # Map parameter to hazard type
        parameter_to_hazard = {
            'wind_speed': 'hurricane',
            'precipitation': 'flood',
            'river_level': 'flood',
            'wave_height': 'tsunami',
            'temperature': 'drought',
            'magnitude': 'earthquake',
            'snowfall': 'winter_storm',
            'wildfire_danger': 'wildfire'
        }
        
        hazard_type = parameter_to_hazard.get(parameter, 'other')
        
        # Construct alert message
        message = f"{parameter.replace('_', ' ').title()} reading of {max_value} exceeds safety threshold. "
        
        if alert_level == "ADVISORY":
            message += "Conditions are potentially hazardous. Monitor updates and use caution."
        elif alert_level == "WATCH":
            message += "Hazardous conditions are likely. Review preparedness plans and be ready to take action."
        elif alert_level == "WARNING":
            message += "Hazardous conditions are occurring or imminent. Take protective actions immediately."
        elif alert_level == "EMERGENCY":
            message += "Extreme hazard present. Life-threatening conditions. Take immediate protective actions."
        
        # Construct affected area
        affected_area = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    getattr(max_measurement.location, 'longitude', 0),
                    getattr(max_measurement.location, 'latitude', 0)
                ]
            },
            "properties": {
                "radius_km": 50  # Default radius
            }
        }
        
        # Create alert
        alert_data = {
            "hazard_type": hazard_type,
            "alert_level": alert_level,
            "affected_area": affected_area,
            "message": message,
            "source": "automatic_monitoring",
            "confidence_level": "medium",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add recommended actions based on hazard type and alert level
        alert_data["recommended_actions"] = self._get_recommended_actions(hazard_type, alert_level)
        
        return self.create_alert(alert_data)
    
    # Risk Assessment Methods
    
    def get_risk_assessment(self, assessment_id: str) -> Optional[RiskAssessment]:
        """
        Get a risk assessment by ID.
        
        Args:
            assessment_id: The ID of the assessment to retrieve
            
        Returns:
            The assessment if found, None otherwise
        """
        return self.risk_assessment_repository.get_by_id(assessment_id)
    
    def get_all_risk_assessments(self) -> List[RiskAssessment]:
        """
        Get all risk assessments.
        
        Returns:
            List of all assessments
        """
        return self.risk_assessment_repository.get_all()
    
    def create_risk_assessment(self, assessment_data: Dict[str, Any]) -> RiskAssessment:
        """
        Create a new risk assessment.
        
        Args:
            assessment_data: Dictionary with assessment data
            
        Returns:
            The created assessment
            
        Raises:
            ValueError: If assessment data is invalid
        """
        # Validate required fields
        required_fields = ['area_name', 'hazard_type', 'risk_level', 'boundaries']
        for field in required_fields:
            if field not in assessment_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set assessment date if not specified
        if 'assessment_date' not in assessment_data:
            assessment_data['assessment_date'] = datetime.now().isoformat()
        
        # Create the assessment
        assessment = RiskAssessment(**assessment_data)
        
        # Save the assessment
        created_assessment = self.risk_assessment_repository.create(assessment)
        
        logger.info(f"Created new risk assessment with ID: {created_assessment.id}")
        return created_assessment
    
    def update_risk_assessment(self, assessment_id: str, updates: Dict[str, Any]) -> Optional[RiskAssessment]:
        """
        Update an existing risk assessment.
        
        Args:
            assessment_id: ID of the assessment to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated assessment or None if assessment not found
        """
        # Get the assessment
        assessment = self.risk_assessment_repository.get_by_id(assessment_id)
        if not assessment:
            logger.warning(f"Assessment not found for update: {assessment_id}")
            return None
        
        # Update the assessment
        for key, value in updates.items():
            setattr(assessment, key, value)
            
        # Update timestamp
        assessment.updated_at = datetime.now().isoformat()
        
        # Save the updated assessment
        updated_assessment = self.risk_assessment_repository.update(assessment)
        
        logger.info(f"Updated assessment with ID: {assessment_id}")
        return updated_assessment
    
    def find_assessments_by_hazard_type(self, hazard_type: str) -> List[RiskAssessment]:
        """
        Find assessments by hazard type.
        
        Args:
            hazard_type: Type of hazard
            
        Returns:
            List of assessments for the specified hazard type
        """
        return self.risk_assessment_repository.find_by_hazard_type(hazard_type)
    
    def find_assessments_by_risk_level(self, risk_level: str) -> List[RiskAssessment]:
        """
        Find assessments by risk level.
        
        Args:
            risk_level: Risk level
            
        Returns:
            List of assessments with the specified risk level
        """
        return self.risk_assessment_repository.find_by_risk_level(risk_level)
    
    def find_assessments_by_area(self, area_name: str) -> List[RiskAssessment]:
        """
        Find assessments by area name.
        
        Args:
            area_name: Name of the area
            
        Returns:
            List of assessments for the specified area
        """
        return self.risk_assessment_repository.find_by_area(area_name)
    
    def find_current_assessments(self) -> List[RiskAssessment]:
        """
        Find current (non-expired) risk assessments.
        
        Returns:
            List of current assessments
        """
        return self.risk_assessment_repository.find_current_assessments()
    
    # Forecast Model Methods
    
    def get_forecast_model(self, model_id: str) -> Optional[ForecastModel]:
        """
        Get a forecast model by ID.
        
        Args:
            model_id: The ID of the model to retrieve
            
        Returns:
            The model if found, None otherwise
        """
        return self.forecast_model_repository.get_by_id(model_id)
    
    def get_all_forecast_models(self) -> List[ForecastModel]:
        """
        Get all forecast models.
        
        Returns:
            List of all models
        """
        return self.forecast_model_repository.get_all()
    
    def create_forecast_model(self, model_data: Dict[str, Any]) -> ForecastModel:
        """
        Create a new forecast model.
        
        Args:
            model_data: Dictionary with model data
            
        Returns:
            The created model
            
        Raises:
            ValueError: If model data is invalid
        """
        # Validate required fields
        required_fields = ['model_name', 'hazard_type', 'model_type']
        for field in required_fields:
            if field not in model_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set last updated if not specified
        if 'last_updated' not in model_data:
            model_data['last_updated'] = datetime.now().isoformat()
        
        # Create the model
        model = ForecastModel(**model_data)
        
        # Save the model
        created_model = self.forecast_model_repository.create(model)
        
        logger.info(f"Created new forecast model with ID: {created_model.id}")
        return created_model
    
    def update_forecast_model(self, model_id: str, updates: Dict[str, Any]) -> Optional[ForecastModel]:
        """
        Update an existing forecast model.
        
        Args:
            model_id: ID of the model to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated model or None if model not found
        """
        # Get the model
        model = self.forecast_model_repository.get_by_id(model_id)
        if not model:
            logger.warning(f"Model not found for update: {model_id}")
            return None
        
        # Update the model
        for key, value in updates.items():
            setattr(model, key, value)
            
        # Update timestamps
        model.updated_at = datetime.now().isoformat()
        model.last_updated = datetime.now().isoformat()
        
        # Save the updated model
        updated_model = self.forecast_model_repository.update(model)
        
        logger.info(f"Updated model with ID: {model_id}")
        return updated_model
    
    def find_models_by_hazard_type(self, hazard_type: str) -> List[ForecastModel]:
        """
        Find forecast models by hazard type.
        
        Args:
            hazard_type: Type of hazard
            
        Returns:
            List of models for the specified hazard type
        """
        return self.forecast_model_repository.find_by_hazard_type(hazard_type)
    
    def find_models_by_type(self, model_type: str) -> List[ForecastModel]:
        """
        Find forecast models by model type.
        
        Args:
            model_type: Type of model
            
        Returns:
            List of models of the specified type
        """
        return self.forecast_model_repository.find_by_model_type(model_type)
    
    # Disaster Forecast Methods
    
    def get_disaster_forecast(self, forecast_id: str) -> Optional[DisasterForecast]:
        """
        Get a disaster forecast by ID.
        
        Args:
            forecast_id: The ID of the forecast to retrieve
            
        Returns:
            The forecast if found, None otherwise
        """
        return self.disaster_forecast_repository.get_by_id(forecast_id)
    
    def get_all_disaster_forecasts(self) -> List[DisasterForecast]:
        """
        Get all disaster forecasts.
        
        Returns:
            List of all forecasts
        """
        return self.disaster_forecast_repository.get_all()
    
    def create_disaster_forecast(self, forecast_data: Dict[str, Any]) -> DisasterForecast:
        """
        Create a new disaster forecast.
        
        Args:
            forecast_data: Dictionary with forecast data
            
        Returns:
            The created forecast
            
        Raises:
            ValueError: If forecast data is invalid
        """
        # Validate required fields
        required_fields = ['model_id', 'hazard_type', 'forecast_area', 'prediction_values']
        for field in required_fields:
            if field not in forecast_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set forecast created if not specified
        if 'forecast_created' not in forecast_data:
            forecast_data['forecast_created'] = datetime.now().isoformat()
            
        # Set valid from if not specified
        if 'valid_from' not in forecast_data:
            forecast_data['valid_from'] = datetime.now().isoformat()
        
        # Create the forecast
        forecast = DisasterForecast(**forecast_data)
        
        # Save the forecast
        created_forecast = self.disaster_forecast_repository.create(forecast)
        
        logger.info(f"Created new disaster forecast with ID: {created_forecast.id}")
        return created_forecast
    
    def update_disaster_forecast(self, forecast_id: str, updates: Dict[str, Any]) -> Optional[DisasterForecast]:
        """
        Update an existing disaster forecast.
        
        Args:
            forecast_id: ID of the forecast to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated forecast or None if forecast not found
        """
        # Get the forecast
        forecast = self.disaster_forecast_repository.get_by_id(forecast_id)
        if not forecast:
            logger.warning(f"Forecast not found for update: {forecast_id}")
            return None
        
        # Update the forecast
        for key, value in updates.items():
            setattr(forecast, key, value)
            
        # Update timestamp
        forecast.updated_at = datetime.now().isoformat()
        
        # Save the updated forecast
        updated_forecast = self.disaster_forecast_repository.update(forecast)
        
        logger.info(f"Updated forecast with ID: {forecast_id}")
        return updated_forecast
    
    def find_forecasts_by_model(self, model_id: str) -> List[DisasterForecast]:
        """
        Find forecasts by model ID.
        
        Args:
            model_id: ID of the forecasting model
            
        Returns:
            List of forecasts from the specified model
        """
        return self.disaster_forecast_repository.find_by_model_id(model_id)
    
    def find_forecasts_by_hazard_type(self, hazard_type: str) -> List[DisasterForecast]:
        """
        Find forecasts by hazard type.
        
        Args:
            hazard_type: Type of hazard
            
        Returns:
            List of forecasts for the specified hazard type
        """
        return self.disaster_forecast_repository.find_by_hazard_type(hazard_type)
    
    def find_current_forecasts(self) -> List[DisasterForecast]:
        """
        Find current (valid) disaster forecasts.
        
        Returns:
            List of current forecasts
        """
        return self.disaster_forecast_repository.find_current_forecasts()
    
    def generate_alerts_from_forecast(self, forecast_id: str) -> List[DisasterAlert]:
        """
        Generate alerts based on a disaster forecast.
        
        Args:
            forecast_id: ID of the forecast to use
            
        Returns:
            List of created alerts
            
        Raises:
            ValueError: If forecast not found
        """
        # Get the forecast
        forecast = self.disaster_forecast_repository.get_by_id(forecast_id)
        if not forecast:
            raise ValueError(f"Forecast not found: {forecast_id}")
            
        # Check if forecast is current
        if not forecast.is_current:
            logger.warning(f"Forecast {forecast_id} is not currently valid")
            return []
            
        # Determine alert level based on forecast data
        alert_level = self._determine_alert_level_from_forecast(forecast)
        if not alert_level:
            logger.info(f"Forecast {forecast_id} does not meet alert criteria")
            return []
            
        # Format alert message
        message = self._format_alert_message_from_forecast(forecast, alert_level)
        
        # Construct alert data
        alert_data = {
            "hazard_type": forecast.hazard_type,
            "alert_level": alert_level,
            "affected_area": forecast.forecast_area,
            "message": message,
            "source": f"forecast_model_{forecast.model_id}",
            "confidence_level": str(forecast.confidence_level) if forecast.confidence_level else "medium",
            "expected_onset": forecast.valid_from,
            "expected_duration": "unknown",
            "recommended_actions": self._get_recommended_actions(forecast.hazard_type, alert_level)
        }
        
        # Create the alert
        alert = self.create_alert(alert_data)
        
        return [alert]
    
    # Helper methods
    
    def _validate_measurement(self, measurement: HazardMeasurement) -> None:
        """
        Validate a measurement for data quality and completeness.
        
        Args:
            measurement: The measurement to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check required fields
        if not hasattr(measurement, 'parameter') or not measurement.parameter:
            raise ValueError("Missing parameter")
        
        if not hasattr(measurement, 'value') or measurement.value is None:
            raise ValueError("Missing value")
        
        if not hasattr(measurement, 'unit') or not measurement.unit:
            raise ValueError("Missing unit")
        
        if not hasattr(measurement, 'location') or not measurement.location:
            raise ValueError("Missing location")
            
        if not hasattr(measurement, 'data_source') or not measurement.data_source:
            raise ValueError("Missing data source")
        
        # Validate value is reasonable (based on parameter-specific ranges)
        parameter = measurement.parameter
        value = measurement.value
        
        # Example validation based on parameter
        if parameter == "wind_speed" and (value < 0 or value > 500):
            raise ValueError(f"Invalid wind speed value: {value} (must be between 0 and 500)")
        
        if parameter == "precipitation" and value < 0:
            raise ValueError(f"Invalid precipitation value: {value} (must be non-negative)")
        
        if parameter == "magnitude" and (value < 0 or value > 10):
            raise ValueError(f"Invalid magnitude value: {value} (must be between 0 and 10)")
        
        # Add more parameter-specific validations as needed
        
        # Set quality flag if not already set
        if not hasattr(measurement, 'quality_flag') or not measurement.quality_flag:
            measurement.quality_flag = "VALID"
    
    def _check_thresholds(self, measurement: HazardMeasurement) -> None:
        """
        Check if a measurement exceeds thresholds and create alerts if needed.
        
        Args:
            measurement: The measurement to check
        """
        if not hasattr(measurement, 'parameter') or not hasattr(measurement, 'value'):
            return
            
        parameter = measurement.parameter
        value = measurement.value
        
        # Get alert thresholds for this parameter
        parameter_thresholds = self.alert_thresholds.get(parameter, {})
        
        # Determine if an alert should be generated
        if not parameter_thresholds:
            # If no specific thresholds, check against general threshold
            threshold = self.thresholds.get(parameter)
            if threshold and value > threshold:
                logger.info(f"Measurement {measurement.id} exceeds threshold: {value} > {threshold}")
                self.generate_alert_from_measurements(parameter)
        else:
            # Check through alert levels
            for level, threshold in sorted(parameter_thresholds.items(), key=lambda x: x[1]):
                if value >= threshold:
                    logger.info(f"Measurement {measurement.id} meets {level} criteria: {value} >= {threshold}")
                    self.generate_alert_from_measurements(parameter)
                    break
    
    def _send_alert_notifications(
        self, 
        alert: DisasterAlert, 
        is_update: bool = False,
        is_closure: bool = False
    ) -> None:
        """
        Send notifications for a disaster alert.
        
        Args:
            alert: The alert to send notifications for
            is_update: Whether this is an update to an existing alert
            is_closure: Whether this is a closure notification
        """
        if not self.notification_adapters:
            logger.info(f"No notification adapters configured, skipping notifications for alert {alert.id}")
            return
            
        for name, adapter in self.notification_adapters.items():
            try:
                # Format notification data
                notification_data = adapter.format_notification(alert)
                
                # Add flags for update or closure
                if is_update:
                    notification_data['is_update'] = True
                if is_closure:
                    notification_data['is_closure'] = True
                
                # Send notification
                success = adapter.send_notification(notification_data)
                
                if success:
                    logger.info(f"Sent {name} notification for alert {alert.id}")
                else:
                    logger.error(f"Failed to send {name} notification for alert {alert.id}")
                    
            except Exception as e:
                logger.error(f"Error sending {name} notification: {str(e)}")
    
    def _determine_alert_level_from_forecast(self, forecast: DisasterForecast) -> Optional[str]:
        """
        Determine appropriate alert level from forecast data.
        
        Args:
            forecast: The forecast to analyze
            
        Returns:
            Alert level or None if no alert needed
        """
        # Check severity prediction
        if hasattr(forecast, 'severity_prediction') and forecast.severity_prediction:
            severity = forecast.severity_prediction.upper()
            
            # Map severity to alert level
            severity_to_alert = {
                'MINOR': 'ADVISORY',
                'MODERATE': 'WATCH',
                'MAJOR': 'WARNING',
                'CATASTROPHIC': 'EMERGENCY'
            }
            
            return severity_to_alert.get(severity, 'WATCH')
            
        # Check probability
        if hasattr(forecast, 'probability') and forecast.probability is not None:
            prob = forecast.probability
            
            # Determine alert level based on probability
            if prob >= 0.75:
                return 'WARNING'
            elif prob >= 0.5:
                return 'WATCH'
            elif prob >= 0.25:
                return 'ADVISORY'
            else:
                return None
                
        # Check prediction values (simplified example)
        if hasattr(forecast, 'prediction_values') and forecast.prediction_values:
            values = forecast.prediction_values
            
            # Example for hurricane
            if forecast.hazard_type == 'hurricane' and 'wind_speed' in values:
                wind_speed = values['wind_speed']
                
                if wind_speed >= 74:
                    return 'WARNING'
                elif wind_speed >= 58:
                    return 'WATCH'
                elif wind_speed >= 39:
                    return 'ADVISORY'
            
            # Example for flood
            if forecast.hazard_type == 'flood' and 'flood_stage' in values:
                flood_stage = values['flood_stage']
                
                if flood_stage >= 18:
                    return 'WARNING'
                elif flood_stage >= 15:
                    return 'WATCH'
                elif flood_stage >= 12:
                    return 'ADVISORY'
        
        # Default to ADVISORY if we have a valid forecast but couldn't determine level
        return 'ADVISORY'
    
    def _format_alert_message_from_forecast(self, forecast: DisasterForecast, alert_level: str) -> str:
        """
        Format alert message from forecast data.
        
        Args:
            forecast: The forecast to use for message content
            alert_level: The determined alert level
            
        Returns:
            Formatted alert message
        """
        # Base message
        hazard_type = forecast.hazard_type.replace('_', ' ').title()
        message = f"FEMA {alert_level} for {hazard_type}. "
        
        # Add forecast information
        if forecast.scenario:
            message += f"{forecast.scenario}. "
            
        # Add probability if available
        if hasattr(forecast, 'probability') and forecast.probability is not None:
            probability_percent = int(forecast.probability * 100)
            message += f"Probability: {probability_percent}%. "
            
        # Add timing information
        valid_from = getattr(forecast, 'valid_from', None)
        valid_to = getattr(forecast, 'valid_to', None)
        
        if valid_from and valid_to:
            from_date = datetime.fromisoformat(valid_from)
            to_date = datetime.fromisoformat(valid_to)
            
            message += f"Valid from {from_date.strftime('%Y-%m-%d %H:%M')} to {to_date.strftime('%Y-%m-%d %H:%M')}. "
        elif valid_from:
            from_date = datetime.fromisoformat(valid_from)
            message += f"Valid from {from_date.strftime('%Y-%m-%d %H:%M')}. "
            
        # Add severity information
        if hasattr(forecast, 'severity_prediction') and forecast.severity_prediction:
            message += f"Predicted severity: {forecast.severity_prediction}. "
            
        # Add expected impacts if available
        if hasattr(forecast, 'expected_impacts') and forecast.expected_impacts:
            impacts = forecast.expected_impacts
            
            if isinstance(impacts, dict):
                impact_str = ", ".join([f"{k}: {v}" for k, v in impacts.items()])
                message += f"Expected impacts: {impact_str}. "
            else:
                message += f"Expected impacts: {impacts}. "
                
        # Add standard advice based on alert level
        if alert_level == "ADVISORY":
            message += "Conditions could potentially become hazardous. Monitor updates and use caution."
        elif alert_level == "WATCH":
            message += "Conditions are favorable for hazard development. Review preparedness plans and be ready to act."
        elif alert_level == "WARNING":
            message += "Hazardous conditions are likely or imminent. Take protective actions immediately."
        elif alert_level == "EMERGENCY":
            message += "Extreme hazard present. Life-threatening conditions likely. Take immediate protective actions."
            
        return message
    
    def _get_recommended_actions(self, hazard_type: str, alert_level: str) -> List[str]:
        """
        Get recommended actions based on hazard type and alert level.
        
        Args:
            hazard_type: Type of hazard
            alert_level: Alert level
            
        Returns:
            List of recommended actions
        """
        # Base recommendations for all hazards
        base_recommendations = {
            "ADVISORY": [
                "Monitor local news and official sources for updates",
                "Review emergency plans",
                "Check emergency supplies"
            ],
            "WATCH": [
                "Monitor local news and official sources for updates",
                "Prepare to act if a warning is issued",
                "Inform family members of situation",
                "Check emergency supplies and prepare go-bag",
                "Fuel vehicles and charge communication devices"
            ],
            "WARNING": [
                "Follow evacuation orders if issued",
                "Move to higher ground or designated safe area immediately",
                "Avoid flooded areas and downed power lines",
                "Monitor local news and emergency channels",
                "Bring pets and essential items inside"
            ],
            "EMERGENCY": [
                "Seek shelter immediately",
                "Follow all emergency instructions",
                "Call 911 for life-threatening situations",
                "Do not attempt to travel unless absolutely necessary",
                "If evacuation is ordered, leave immediately"
            ]
        }
        
        # Hazard-specific recommendations
        hazard_recommendations = {
            "hurricane": {
                "ADVISORY": [
                    "Secure loose outdoor items",
                    "Trim damaged trees and branches",
                    "Check hurricane shutters or plywood for windows"
                ],
                "WATCH": [
                    "Secure loose outdoor items",
                    "Cover windows with storm shutters or plywood",
                    "Fill containers with clean water",
                    "Move vehicles to higher ground if possible",
                    "Prepare for power outages"
                ],
                "WARNING": [
                    "Stay away from windows during the storm",
                    "Go to an interior room on the lowest floor",
                    "Do not go outside during the eye of the storm",
                    "If evacuation is ordered, leave immediately",
                    "Turn refrigerator/freezer to coldest settings"
                ],
                "EMERGENCY": [
                    "If unable to evacuate, shelter in the strongest part of your home",
                    "Keep mattresses nearby to protect from debris",
                    "Fill bathtubs and sinks with water for sanitary purposes",
                    "Stay tuned to emergency channels for instructions",
                    "Stay indoors until officials declare it safe"
                ]
            },
            "flood": {
                "ADVISORY": [
                    "Avoid camping or parking near streams or washes",
                    "Check sump pumps and drains",
                    "Prepare for possible power outages"
                ],
                "WATCH": [
                    "Move valuable items to higher floors",
                    "Prepare for possible evacuation",
                    "Fill your vehicle's gas tank",
                    "Check sump pumps",
                    "Prepare sandbags if available"
                ],
                "WARNING": [
                    "Move to higher ground immediately",
                    "Do not walk, swim, or drive through flood waters",
                    "Stay off bridges over fast-moving water",
                    "Evacuate if told to do so",
                    "Disconnect utilities if instructed by authorities"
                ],
                "EMERGENCY": [
                    "Get to the highest level of a building immediately",
                    "Only get on the roof if necessary and have signaling devices",
                    "Do not enter flood waters",
                    "Avoid electrical equipment if wet or standing in water",
                    "If trapped in a building, signal for help"
                ]
            },
            "earthquake": {
                "ADVISORY": [
                    "Secure heavy items and furniture",
                    "Identify safe spots in each room (under sturdy furniture, against interior walls)",
                    "Keep emergency supplies accessible"
                ],
                "WATCH": [
                    "Secure heavy items and furniture",
                    "Know how to shut off utilities",
                    "Have emergency supplies ready",
                    "Review drop, cover, and hold procedures",
                    "Keep mobile phones charged"
                ],
                "WARNING": [
                    "DROP to the ground, take COVER under sturdy furniture, and HOLD ON",
                    "Stay indoors until shaking stops",
                    "Stay away from windows and exterior walls",
                    "If outdoors, move to a clear area away from buildings",
                    "If in a vehicle, pull over safely away from buildings and trees"
                ],
                "EMERGENCY": [
                    "If trapped, cover mouth and nose from dust",
                    "Send text messages instead of calling",
                    "Tap on pipes or walls so rescuers can locate you",
                    "Check for injuries and provide first aid",
                    "Evacuate damaged buildings and be alert for aftershocks"
                ]
            }
        }
        
        # Get recommendations based on hazard type and alert level
        specific_recommendations = hazard_recommendations.get(hazard_type, {}).get(alert_level, [])
        
        # Combine with base recommendations (without duplicates)
        combined = []
        combined.extend(base_recommendations.get(alert_level, []))
        for rec in specific_recommendations:
            if rec not in combined:
                combined.append(rec)
                
        return combined