"""
Environmental Quality Monitoring Service for the EPA implementation.

This service provides functionality for monitoring environmental quality,
including air, water, and soil measurements, site management, and alerting.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import logging
import uuid

from agency_implementation.epa.models.environmental_quality import (
    MonitoringSite, EnvironmentalMeasurement, AirQualityIndex,
    WaterQualityMeasurement, SoilQualityMeasurement, EnvironmentalAlert
)
from agency_implementation.epa.models.base import PollutantType, MeasurementUnit
from .repository import (
    MonitoringSiteRepository, EnvironmentalMeasurementRepository,
    EnvironmentalAlertRepository
)
from .adapters import MonitoringSystemAdapter, AlertNotificationAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnvironmentalQualityMonitoringService:
    """
    Service for environmental quality monitoring.
    
    This service provides functionality for:
    1. Monitoring site management (create, update, query)
    2. Environmental measurement collection and analysis
    3. Alert generation and management
    4. Data validation and quality assurance
    5. Threshold monitoring and exceedance detection
    """
    
    def __init__(
        self,
        site_repository: MonitoringSiteRepository,
        measurement_repository: EnvironmentalMeasurementRepository,
        alert_repository: EnvironmentalAlertRepository,
        monitoring_adapter: Optional[MonitoringSystemAdapter] = None,
        notification_adapter: Optional[AlertNotificationAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the service.
        
        Args:
            site_repository: Repository for monitoring sites
            measurement_repository: Repository for environmental measurements
            alert_repository: Repository for environmental alerts
            monitoring_adapter: Adapter for external monitoring systems
            notification_adapter: Adapter for alert notifications
            config: Service configuration
        """
        self.site_repository = site_repository
        self.measurement_repository = measurement_repository
        self.alert_repository = alert_repository
        self.monitoring_adapter = monitoring_adapter
        self.notification_adapter = notification_adapter
        self.config = config or {}
        
        # Initialize thresholds for environmental parameters
        self.thresholds = self.config.get('thresholds', {
            'PM25': 35.0,  # EPA standard for PM2.5 (μg/m³, 24-hour)
            'PM10': 150.0,  # EPA standard for PM10 (μg/m³, 24-hour)
            'OZONE': 0.070,  # EPA standard for ozone (ppm, 8-hour)
            'NO2': 100.0,  # EPA standard for NO2 (ppb, 1-hour)
            'SO2': 75.0,  # EPA standard for SO2 (ppb, 1-hour)
            'CO': 9.0,  # EPA standard for CO (ppm, 8-hour)
            'LEAD': 0.15,  # EPA standard for lead (μg/m³, 3-month)
            'NITRATES': 10.0,  # EPA standard for nitrates in drinking water (mg/L)
            'E_COLI': 126.0,  # EPA standard for E. coli in recreational water (CFU/100mL)
            'PH_MIN': 6.5,  # EPA minimum pH for drinking water
            'PH_MAX': 8.5,  # EPA maximum pH for drinking water
            'DISSOLVED_OXYGEN_MIN': 5.0  # Minimum dissolved oxygen for aquatic life (mg/L)
        })
        
        # Set up automatic data validation
        self.auto_validate = self.config.get('auto_validate', True)
        
        # Initialize alert severities
        self.alert_severities = self.config.get('alert_severities', {
            'MINOR': 1.0,  # Threshold exceeded by up to 10%
            'MODERATE': 1.1,  # Threshold exceeded by 10-50%
            'MAJOR': 1.5,  # Threshold exceeded by 50-100%
            'SEVERE': 2.0,  # Threshold exceeded by more than 100%
            'CRITICAL': 5.0   # Threshold exceeded by more than 400%
        })
        
        logger.info("EnvironmentalQualityMonitoringService initialized")
    
    # Site Management Methods
    
    def get_monitoring_site(self, site_id: str) -> Optional[MonitoringSite]:
        """
        Get a monitoring site by ID.
        
        Args:
            site_id: The ID of the site to retrieve
            
        Returns:
            The site if found, None otherwise
        """
        return self.site_repository.get_by_id(site_id)
    
    def get_all_monitoring_sites(self) -> List[MonitoringSite]:
        """
        Get all monitoring sites.
        
        Returns:
            List of all sites
        """
        return self.site_repository.get_all()
    
    def create_monitoring_site(self, site_data: Dict[str, Any]) -> MonitoringSite:
        """
        Create a new monitoring site.
        
        Args:
            site_data: Dictionary with site data
            
        Returns:
            The created site
            
        Raises:
            ValueError: If site data is invalid
        """
        # Validate required fields
        required_fields = ['site_name', 'location', 'site_type', 'parameters_monitored']
        for field in required_fields:
            if field not in site_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the site
        site = MonitoringSite(**site_data)
        
        # Save the site
        created_site = self.site_repository.create(site)
        
        logger.info(f"Created new monitoring site with ID: {created_site.id}")
        return created_site
    
    def update_monitoring_site(self, site_id: str, updates: Dict[str, Any]) -> Optional[MonitoringSite]:
        """
        Update an existing monitoring site.
        
        Args:
            site_id: ID of the site to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated site or None if site not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the site
        site = self.site_repository.get_by_id(site_id)
        if not site:
            logger.warning(f"Site not found for update: {site_id}")
            return None
        
        # Update the site
        for key, value in updates.items():
            setattr(site, key, value)
            
        # Update timestamp
        site.updated_at = datetime.now().isoformat()
        
        # Save the updated site
        updated_site = self.site_repository.update(site)
        
        logger.info(f"Updated site with ID: {site_id}")
        return updated_site
    
    def find_sites_by_parameters(self, parameters: List[str]) -> List[MonitoringSite]:
        """
        Find sites that monitor specific parameters.
        
        Args:
            parameters: List of parameters to search for
            
        Returns:
            List of sites monitoring any of the specified parameters
        """
        results = []
        
        for site in self.site_repository.get_all():
            if hasattr(site, 'parameters_monitored'):
                if any(param in site.parameters_monitored for param in parameters):
                    results.append(site)
                    
        return results
    
    def find_sites_in_region(self, region: str) -> List[MonitoringSite]:
        """
        Find sites in a specific EPA region.
        
        Args:
            region: EPA region code
            
        Returns:
            List of sites in the specified region
        """
        return self.site_repository.find_by_region(region)
    
    def find_sites_by_type(self, site_type: str) -> List[MonitoringSite]:
        """
        Find sites by type.
        
        Args:
            site_type: Type of monitoring site
            
        Returns:
            List of sites of the specified type
        """
        return self.site_repository.find_by_site_type(site_type)
    
    def find_sites_needing_maintenance(self, days_threshold: int = 180) -> List[MonitoringSite]:
        """
        Find sites that may need maintenance based on last maintenance date.
        
        Args:
            days_threshold: Number of days since last maintenance to trigger inclusion
            
        Returns:
            List of sites needing maintenance
        """
        return self.site_repository.find_by_maintenance_needed(days_threshold)
    
    # Measurement Management Methods
    
    def get_measurement(self, measurement_id: str) -> Optional[EnvironmentalMeasurement]:
        """
        Get a measurement by ID.
        
        Args:
            measurement_id: The ID of the measurement to retrieve
            
        Returns:
            The measurement if found, None otherwise
        """
        return self.measurement_repository.get_by_id(measurement_id)
    
    def create_measurement(self, measurement_data: Dict[str, Any]) -> EnvironmentalMeasurement:
        """
        Create a new environmental measurement.
        
        Args:
            measurement_data: Dictionary with measurement data
            
        Returns:
            The created measurement
            
        Raises:
            ValueError: If measurement data is invalid
        """
        # Validate required fields
        required_fields = ['site_id', 'parameter', 'value', 'unit']
        for field in required_fields:
            if field not in measurement_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check site exists
        site = self.site_repository.get_by_id(measurement_data['site_id'])
        if not site:
            raise ValueError(f"Site with ID {measurement_data['site_id']} does not exist")
        
        # Determine measurement class based on data
        if 'water_body_type' in measurement_data:
            measurement = WaterQualityMeasurement(**measurement_data)
        elif 'soil_type' in measurement_data:
            measurement = SoilQualityMeasurement(**measurement_data)
        else:
            measurement = EnvironmentalMeasurement(**measurement_data)
        
        # Perform automatic validation if enabled
        if self.auto_validate:
            self._validate_measurement(measurement)
        
        # Save the measurement
        created_measurement = self.measurement_repository.create(measurement)
        
        # Check for threshold exceedances
        self._check_thresholds(created_measurement)
        
        logger.info(f"Created new measurement with ID: {created_measurement.id}")
        return created_measurement
    
    def batch_create_measurements(self, measurements_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple environmental measurements in batch.
        
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
    
    def find_measurements_by_site(self, site_id: str) -> List[EnvironmentalMeasurement]:
        """
        Find measurements for a specific site.
        
        Args:
            site_id: ID of the monitoring site
            
        Returns:
            List of measurements for the site
        """
        return self.measurement_repository.find_by_site_id(site_id)
    
    def find_measurements_by_parameter(self, parameter: str) -> List[EnvironmentalMeasurement]:
        """
        Find measurements for a specific parameter.
        
        Args:
            parameter: Environmental parameter
            
        Returns:
            List of measurements for the parameter
        """
        return self.measurement_repository.find_by_parameter(parameter)
    
    def find_measurements_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[EnvironmentalMeasurement]:
        """
        Find measurements within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of measurements within the date range
        """
        return self.measurement_repository.find_by_date_range(start_date, end_date)
    
    def find_exceeded_thresholds(self) -> List[EnvironmentalMeasurement]:
        """
        Find measurements that exceed their respective thresholds.
        
        Returns:
            List of measurements exceeding thresholds
        """
        return self.measurement_repository.find_exceeded_thresholds(self.thresholds)
    
    def import_measurements_from_monitoring_system(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Import measurements from an external monitoring system.
        
        Args:
            params: Parameters for the import (e.g., time range, sites)
            
        Returns:
            Dictionary with import results
            
        Raises:
            RuntimeError: If monitoring adapter is not configured
        """
        if not self.monitoring_adapter:
            raise RuntimeError("Monitoring system adapter not configured")
        
        params = params or {}
        logger.info(f"Importing measurements from monitoring system with params: {params}")
        
        # Fetch data from monitoring system
        monitoring_data = self.monitoring_adapter.fetch_data(**params)
        
        # Process results
        imported_count = 0
        errors = []
        
        for record in monitoring_data:
            try:
                # Convert to measurement
                measurement = self.monitoring_adapter.convert_to_measurement(record)
                if not measurement:
                    errors.append(f"Failed to convert record: {record.get('id', 'unknown')}")
                    continue
                
                # Save the measurement
                self.measurement_repository.create(measurement)
                
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
            'errors': errors[:10]  # Limit error list to avoid huge responses
        }
        
        logger.info(f"Monitoring import complete: {imported_count} measurements imported, {len(errors)} errors")
        return result
    
    # Alert Management Methods
    
    def get_alert(self, alert_id: str) -> Optional[EnvironmentalAlert]:
        """
        Get an alert by ID.
        
        Args:
            alert_id: The ID of the alert to retrieve
            
        Returns:
            The alert if found, None otherwise
        """
        return self.alert_repository.get_by_id(alert_id)
    
    def get_active_alerts(self) -> List[EnvironmentalAlert]:
        """
        Get all active alerts.
        
        Returns:
            List of active alerts
        """
        return self.alert_repository.find_active_alerts()
    
    def create_alert(self, alert_data: Dict[str, Any]) -> EnvironmentalAlert:
        """
        Create a new environmental alert.
        
        Args:
            alert_data: Dictionary with alert data
            
        Returns:
            The created alert
            
        Raises:
            ValueError: If alert data is invalid
        """
        # Validate required fields
        required_fields = ['site_id', 'parameter', 'value', 'threshold', 'severity']
        for field in required_fields:
            if field not in alert_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check site exists
        site = self.site_repository.get_by_id(alert_data['site_id'])
        if not site:
            raise ValueError(f"Site with ID {alert_data['site_id']} does not exist")
        
        # Create the alert
        alert = EnvironmentalAlert(**alert_data)
        
        # Save the alert
        created_alert = self.alert_repository.create(alert)
        
        # Send notification if adapter configured
        if self.notification_adapter:
            try:
                notification_data = self._format_alert_for_notification(created_alert)
                self.notification_adapter.send_notification(notification_data)
                logger.info(f"Notification sent for alert {created_alert.id}")
            except Exception as e:
                logger.error(f"Error sending notification for alert {created_alert.id}: {str(e)}")
        
        logger.info(f"Created new alert with ID: {created_alert.id}")
        return created_alert
    
    def close_alert(self, alert_id: str, resolution_notes: str = None) -> Optional[EnvironmentalAlert]:
        """
        Close an active alert.
        
        Args:
            alert_id: ID of the alert to close
            resolution_notes: Optional notes about how the alert was resolved
            
        Returns:
            The updated alert or None if alert not found
            
        Raises:
            ValueError: If alert is not active
        """
        # Get the alert
        alert = self.alert_repository.get_by_id(alert_id)
        if not alert:
            logger.warning(f"Alert not found for closure: {alert_id}")
            return None
        
        # Check if alert is active
        if hasattr(alert, 'status') and alert.status != "ACTIVE":
            raise ValueError(f"Alert {alert_id} is not active (current status: {alert.status})")
        
        # Close the alert
        alert.close_alert(resolution_notes)
        
        # Save the updated alert
        updated_alert = self.alert_repository.update(alert)
        
        # Send notification if adapter configured
        if self.notification_adapter:
            try:
                notification_data = self._format_alert_for_notification(updated_alert, is_closure=True)
                self.notification_adapter.send_notification(notification_data)
                logger.info(f"Closure notification sent for alert {updated_alert.id}")
            except Exception as e:
                logger.error(f"Error sending closure notification for alert {updated_alert.id}: {str(e)}")
        
        logger.info(f"Closed alert with ID: {alert_id}")
        return updated_alert
    
    def find_alerts_by_site(self, site_id: str) -> List[EnvironmentalAlert]:
        """
        Find alerts for a specific site.
        
        Args:
            site_id: ID of the monitoring site
            
        Returns:
            List of alerts for the site
        """
        return self.alert_repository.find_by_site_id(site_id)
    
    def find_alerts_by_parameter(self, parameter: str) -> List[EnvironmentalAlert]:
        """
        Find alerts for a specific parameter.
        
        Args:
            parameter: Environmental parameter
            
        Returns:
            List of alerts for the parameter
        """
        return self.alert_repository.find_by_parameter(parameter)
    
    def find_alerts_by_severity(self, severity: str) -> List[EnvironmentalAlert]:
        """
        Find alerts by severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            List of alerts with the specified severity
        """
        return self.alert_repository.find_by_severity(severity)
    
    def find_alerts_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str]
    ) -> List[EnvironmentalAlert]:
        """
        Find alerts within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of alerts within the date range
        """
        return self.alert_repository.find_by_date_range(start_date, end_date)
    
    # Analysis Methods
    
    def calculate_aqi(self, site_id: str, timestamp: str = None) -> Dict[str, Any]:
        """
        Calculate Air Quality Index (AQI) for a monitoring site.
        
        Args:
            site_id: ID of the monitoring site
            timestamp: Optional timestamp for calculation (defaults to latest)
            
        Returns:
            Dictionary with AQI calculation results
            
        Raises:
            ValueError: If site does not exist or doesn't monitor required parameters
        """
        # Check site exists
        site = self.site_repository.get_by_id(site_id)
        if not site:
            raise ValueError(f"Site with ID {site_id} does not exist")
        
        # Check site monitors air quality parameters
        air_parameters = ["PM25", "PM10", "OZONE", "CO", "NO2", "SO2"]
        if not hasattr(site, 'parameters_monitored') or not any(param in site.parameters_monitored for param in air_parameters):
            raise ValueError(f"Site {site_id} does not monitor air quality parameters")
        
        # Get measurements for the site
        site_measurements = self.measurement_repository.find_by_site_id(site_id)
        
        # Filter by timestamp if provided
        if timestamp:
            timestamp_dt = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
            # Get measurements within 24 hours of the timestamp
            time_window = timedelta(hours=24)
            start_time = timestamp_dt - time_window
            end_time = timestamp_dt
            site_measurements = [m for m in site_measurements if 
                                hasattr(m, 'timestamp') and 
                                start_time <= datetime.fromisoformat(m.timestamp) <= end_time]
        else:
            # Get latest measurements (within last 24 hours)
            now = datetime.now()
            yesterday = now - timedelta(hours=24)
            site_measurements = [m for m in site_measurements if 
                                hasattr(m, 'timestamp') and 
                                datetime.fromisoformat(m.timestamp) >= yesterday]
        
        # Group measurements by parameter
        by_parameter = {}
        for measurement in site_measurements:
            if hasattr(measurement, 'parameter'):
                if measurement.parameter not in by_parameter:
                    by_parameter[measurement.parameter] = []
                by_parameter[measurement.parameter].append(measurement)
        
        # Calculate AQI for each parameter
        aqi_values = {}
        for param, measurements in by_parameter.items():
            if not measurements:
                continue
                
            # Use the most recent measurement for each parameter
            latest = max(measurements, key=lambda m: m.timestamp)
            
            # Convert concentration to AQI (simplified calculation)
            if param == "PM25":
                aqi_values[param] = self._calculate_pm25_aqi(latest.value)
            elif param == "PM10":
                aqi_values[param] = self._calculate_pm10_aqi(latest.value)
            elif param == "OZONE":
                aqi_values[param] = self._calculate_ozone_aqi(latest.value)
            elif param == "CO":
                aqi_values[param] = self._calculate_co_aqi(latest.value)
            elif param == "NO2":
                aqi_values[param] = self._calculate_no2_aqi(latest.value)
            elif param == "SO2":
                aqi_values[param] = self._calculate_so2_aqi(latest.value)
        
        # Determine overall AQI (maximum of all parameters)
        if not aqi_values:
            return {
                "site_id": site_id,
                "timestamp": datetime.now().isoformat(),
                "message": "No recent air quality measurements available",
                "aqi_value": None,
                "category": "Unknown",
                "dominant_pollutant": None
            }
        
        max_aqi = max(aqi_values.items(), key=lambda x: x[1])
        aqi_value = max_aqi[1]
        dominant_pollutant = max_aqi[0]
        
        # Determine AQI category
        category = self._get_aqi_category(aqi_value)
        
        # Determine health implications and sensitive groups
        health_implications, sensitive_groups = self._get_aqi_health_info(aqi_value)
        
        result = {
            "site_id": site_id,
            "timestamp": datetime.now().isoformat(),
            "aqi_value": aqi_value,
            "category": category,
            "dominant_pollutant": dominant_pollutant,
            "health_implications": health_implications,
            "sensitive_groups": sensitive_groups,
            "parameter_values": aqi_values
        }
        
        return result
    
    def generate_statistical_summary(
        self, 
        parameter: str,
        start_date: Union[datetime, str],
        end_date: Union[datetime, str],
        site_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate statistical summary for a parameter over a date range.
        
        Args:
            parameter: Environmental parameter to analyze
            start_date: Start date of the analysis period
            end_date: End date of the analysis period
            site_ids: Optional list of site IDs to include (if None, include all)
            
        Returns:
            Dictionary with statistical summary
        """
        # Get measurements for the parameter
        measurements = self.measurement_repository.find_by_parameter(parameter)
        
        # Filter by date range
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
            
        measurements = [m for m in measurements if 
                       hasattr(m, 'timestamp') and 
                       start_date <= datetime.fromisoformat(m.timestamp) <= end_date]
        
        # Filter by site IDs if provided
        if site_ids:
            measurements = [m for m in measurements if 
                           hasattr(m, 'site_id') and 
                           m.site_id in site_ids]
        
        # Calculate statistics
        if not measurements:
            return {
                "parameter": parameter,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "message": "No measurements found for the specified criteria",
                "measurement_count": 0
            }
        
        values = [m.value for m in measurements if hasattr(m, 'value')]
        
        # Get unit from the first measurement (assuming consistent units)
        unit = measurements[0].unit if hasattr(measurements[0], 'unit') else "Unknown"
        
        # Calculate stats
        avg_value = sum(values) / len(values) if values else 0
        min_value = min(values) if values else 0
        max_value = max(values) if values else 0
        
        # Check if threshold exists for this parameter
        threshold = self.thresholds.get(parameter)
        threshold_exceeded = False
        exceedance_percentage = None
        
        if threshold is not None:
            threshold_exceeded = max_value > threshold
            if threshold_exceeded:
                exceedance_percentage = ((max_value - threshold) / threshold) * 100
        
        # Group by site
        by_site = {}
        for measurement in measurements:
            if hasattr(measurement, 'site_id'):
                site_id = measurement.site_id
                if site_id not in by_site:
                    by_site[site_id] = []
                by_site[site_id].append(measurement)
        
        site_stats = {}
        for site_id, site_measurements in by_site.items():
            site_values = [m.value for m in site_measurements if hasattr(m, 'value')]
            site_stats[site_id] = {
                "measurement_count": len(site_measurements),
                "average_value": sum(site_values) / len(site_values) if site_values else 0,
                "min_value": min(site_values) if site_values else 0,
                "max_value": max(site_values) if site_values else 0
            }
        
        result = {
            "parameter": parameter,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "measurement_count": len(measurements),
            "average_value": avg_value,
            "min_value": min_value,
            "max_value": max_value,
            "unit": unit,
            "sites_included": len(by_site),
            "threshold": threshold,
            "threshold_exceeded": threshold_exceeded
        }
        
        if exceedance_percentage is not None:
            result["exceedance_percentage"] = exceedance_percentage
            
        result["by_site"] = site_stats
        
        return result
    
    def generate_trend_analysis(
        self,
        parameter: str,
        site_id: str,
        days: int = 30,
        interval: str = "day"
    ) -> Dict[str, Any]:
        """
        Generate trend analysis for a parameter at a specific site.
        
        Args:
            parameter: Environmental parameter to analyze
            site_id: ID of the monitoring site
            days: Number of days to include in the analysis
            interval: Aggregation interval (day, week, month)
            
        Returns:
            Dictionary with trend analysis results
            
        Raises:
            ValueError: If site does not exist
        """
        # Check site exists
        site = self.site_repository.get_by_id(site_id)
        if not site:
            raise ValueError(f"Site with ID {site_id} does not exist")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get measurements for the site and parameter
        site_measurements = self.measurement_repository.find_by_site_id(site_id)
        parameter_measurements = [m for m in site_measurements if 
                                 hasattr(m, 'parameter') and 
                                 m.parameter == parameter]
        
        # Filter by date range
        filtered_measurements = [m for m in parameter_measurements if 
                               hasattr(m, 'timestamp') and 
                               start_date <= datetime.fromisoformat(m.timestamp) <= end_date]
        
        if not filtered_measurements:
            return {
                "parameter": parameter,
                "site_id": site_id,
                "site_name": site.site_name if hasattr(site, 'site_name') else "Unknown",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "message": "No measurements found for the specified criteria",
                "measurement_count": 0
            }
        
        # Group by interval
        grouped_data = {}
        
        for measurement in filtered_measurements:
            timestamp = datetime.fromisoformat(measurement.timestamp)
            
            if interval == "day":
                key = timestamp.date().isoformat()
            elif interval == "week":
                # Use the first day of the week as key
                key = (timestamp - timedelta(days=timestamp.weekday())).date().isoformat()
            elif interval == "month":
                key = f"{timestamp.year}-{timestamp.month:02d}-01"
            else:
                # Default to day
                key = timestamp.date().isoformat()
            
            if key not in grouped_data:
                grouped_data[key] = []
                
            grouped_data[key].append(measurement)
        
        # Calculate statistics for each interval
        trend_data = []
        
        for key, measurements in sorted(grouped_data.items()):
            values = [m.value for m in measurements if hasattr(m, 'value')]
            
            if not values:
                continue
                
            avg_value = sum(values) / len(values)
            min_value = min(values)
            max_value = max(values)
            
            interval_data = {
                "interval": key,
                "average_value": avg_value,
                "min_value": min_value,
                "max_value": max_value,
                "measurement_count": len(values)
            }
            
            trend_data.append(interval_data)
        
        # Get unit from the first measurement (assuming consistent units)
        unit = filtered_measurements[0].unit if hasattr(filtered_measurements[0], 'unit') else "Unknown"
        
        # Calculate overall trend (simple linear regression)
        if len(trend_data) > 1:
            # Convert data to points
            x = list(range(len(trend_data)))
            y = [data["average_value"] for data in trend_data]
            
            # Calculate slope (simple method)
            x_mean = sum(x) / len(x)
            y_mean = sum(y) / len(y)
            
            numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
            denominator = sum((xi - x_mean) ** 2 for xi in x)
            
            slope = numerator / denominator if denominator != 0 else 0
            
            # Determine trend direction
            if slope > 0.01:
                trend_direction = "increasing"
            elif slope < -0.01:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "unknown"
            slope = 0
        
        result = {
            "parameter": parameter,
            "site_id": site_id,
            "site_name": site.site_name if hasattr(site, 'site_name') else "Unknown",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "interval": interval,
            "unit": unit,
            "measurement_count": len(filtered_measurements),
            "trend_direction": trend_direction,
            "trend_slope": slope,
            "trend_data": trend_data
        }
        
        return result
    
    # Helper methods
    
    def _validate_measurement(self, measurement: EnvironmentalMeasurement) -> None:
        """
        Validate a measurement for data quality and completeness.
        
        Args:
            measurement: The measurement to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check required fields
        if not hasattr(measurement, 'site_id') or not measurement.site_id:
            raise ValueError("Missing site ID")
        
        if not hasattr(measurement, 'parameter') or not measurement.parameter:
            raise ValueError("Missing parameter")
        
        if not hasattr(measurement, 'value') or measurement.value is None:
            raise ValueError("Missing value")
        
        if not hasattr(measurement, 'unit') or not measurement.unit:
            raise ValueError("Missing unit")
        
        # Validate value is reasonable (based on parameter-specific ranges)
        parameter = measurement.parameter
        value = measurement.value
        
        # Example validation based on parameter
        if parameter == "PH" and (value < 0 or value > 14):
            raise ValueError(f"Invalid pH value: {value} (must be between 0 and 14)")
        
        if parameter == "TEMPERATURE" and (value < -100 or value > 100):
            raise ValueError(f"Invalid temperature value: {value} (must be between -100 and 100)")
        
        if "PM" in parameter and value < 0:
            raise ValueError(f"Invalid PM value: {value} (must be non-negative)")
        
        # Add more parameter-specific validations as needed
        
        # Set quality flag if not already set
        if not hasattr(measurement, 'quality_flag') or not measurement.quality_flag:
            measurement.quality_flag = "VALID"
    
    def _check_thresholds(self, measurement: EnvironmentalMeasurement) -> None:
        """
        Check if a measurement exceeds thresholds and create alerts if needed.
        
        Args:
            measurement: The measurement to check
        """
        if not hasattr(measurement, 'parameter') or not hasattr(measurement, 'value'):
            return
            
        parameter = measurement.parameter
        value = measurement.value
        
        # Get threshold for this parameter
        threshold = self.thresholds.get(parameter)
        
        if threshold is None:
            return
            
        # Check if value exceeds threshold
        if value > threshold:
            # Calculate exceedance ratio
            exceedance_ratio = value / threshold
            
            # Determine severity based on ratio
            severity = "MINOR"
            for level, ratio in sorted(self.alert_severities.items(), key=lambda x: x[1], reverse=True):
                if exceedance_ratio >= ratio:
                    severity = level
                    break
            
            # Create alert
            alert_data = {
                "site_id": measurement.site_id,
                "parameter": parameter,
                "value": value,
                "threshold": threshold,
                "severity": severity,
                "timestamp": measurement.timestamp if hasattr(measurement, 'timestamp') else datetime.now().isoformat(),
                "status": "ACTIVE",
                "message": f"{parameter} exceeds threshold ({value:.2f} > {threshold:.2f})"
            }
            
            # Add location if available
            if hasattr(measurement, 'location'):
                alert_data["location"] = measurement.location
            
            # Check if there's already an active alert for this site and parameter
            existing_alerts = self.alert_repository.find({
                "site_id": measurement.site_id,
                "parameter": parameter,
                "status": "ACTIVE"
            })
            
            if existing_alerts:
                # Update existing alert if value is higher
                existing = existing_alerts[0]
                if existing.value < value:
                    existing.value = value
                    existing.severity = severity
                    existing.timestamp = measurement.timestamp if hasattr(measurement, 'timestamp') else datetime.now().isoformat()
                    existing.message = alert_data["message"]
                    self.alert_repository.update(existing)
                    
                    # Send notification for updated alert
                    if self.notification_adapter:
                        try:
                            notification_data = self._format_alert_for_notification(existing, is_update=True)
                            self.notification_adapter.send_notification(notification_data)
                        except Exception as e:
                            logger.error(f"Error sending notification for updated alert: {str(e)}")
            else:
                # Create new alert
                try:
                    self.create_alert(alert_data)
                except Exception as e:
                    logger.error(f"Error creating alert: {str(e)}")
    
    def _format_alert_for_notification(
        self, 
        alert: EnvironmentalAlert, 
        is_closure: bool = False,
        is_update: bool = False
    ) -> Dict[str, Any]:
        """
        Format an alert for notification delivery.
        
        Args:
            alert: The alert to format
            is_closure: Whether this is a closure notification
            is_update: Whether this is an update notification
            
        Returns:
            Dictionary formatted for notification adapter
        """
        # Get site name if available
        site_name = "Unknown"
        site = self.site_repository.get_by_id(alert.site_id)
        if site and hasattr(site, 'site_name'):
            site_name = site.site_name
        
        # Format notification based on type
        if is_closure:
            notification_type = "ALERT_CLOSED"
            title = f"Environmental Alert Closed: {alert.parameter} at {site_name}"
            message = f"The {alert.severity} alert for {alert.parameter} has been resolved."
        elif is_update:
            notification_type = "ALERT_UPDATED"
            title = f"Environmental Alert Updated: {alert.parameter} at {site_name}"
            message = f"The {alert.severity} alert for {alert.parameter} has been updated. New value: {alert.value:.2f} (threshold: {alert.threshold:.2f})"
        else:
            notification_type = "ALERT_NEW"
            title = f"Environmental Alert: {alert.parameter} at {site_name}"
            message = f"A {alert.severity} alert has been detected for {alert.parameter}. Value: {alert.value:.2f} (threshold: {alert.threshold:.2f})"
        
        notification = {
            "type": notification_type,
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "alert_id": alert.id,
            "site_id": alert.site_id,
            "site_name": site_name,
            "parameter": alert.parameter,
            "value": alert.value,
            "threshold": alert.threshold,
            "severity": alert.severity,
            "status": getattr(alert, 'status', 'ACTIVE')
        }
        
        # Add location if available
        if hasattr(alert, 'location') and alert.location:
            notification["location"] = alert.location.to_dict() if hasattr(alert.location, 'to_dict') else alert.location
        
        # Add resolution info if closure
        if is_closure and hasattr(alert, 'resolution_notes'):
            notification["resolution_notes"] = alert.resolution_notes
            notification["resolution_timestamp"] = getattr(alert, 'resolution_timestamp', datetime.now().isoformat())
        
        return notification
    
    # AQI calculation methods (simplified versions)
    
    def _calculate_pm25_aqi(self, concentration: float) -> int:
        """Calculate AQI for PM2.5"""
        if concentration <= 12.0:
            return int(((50 - 0) / (12.0 - 0)) * (concentration - 0) + 0)
        elif concentration <= 35.4:
            return int(((100 - 51) / (35.4 - 12.1)) * (concentration - 12.1) + 51)
        elif concentration <= 55.4:
            return int(((150 - 101) / (55.4 - 35.5)) * (concentration - 35.5) + 101)
        elif concentration <= 150.4:
            return int(((200 - 151) / (150.4 - 55.5)) * (concentration - 55.5) + 151)
        elif concentration <= 250.4:
            return int(((300 - 201) / (250.4 - 150.5)) * (concentration - 150.5) + 201)
        elif concentration <= 500.4:
            return int(((500 - 301) / (500.4 - 250.5)) * (concentration - 250.5) + 301)
        else:
            return 500
    
    def _calculate_pm10_aqi(self, concentration: float) -> int:
        """Calculate AQI for PM10"""
        if concentration <= 54:
            return int(((50 - 0) / (54 - 0)) * (concentration - 0) + 0)
        elif concentration <= 154:
            return int(((100 - 51) / (154 - 55)) * (concentration - 55) + 51)
        elif concentration <= 254:
            return int(((150 - 101) / (254 - 155)) * (concentration - 155) + 101)
        elif concentration <= 354:
            return int(((200 - 151) / (354 - 255)) * (concentration - 255) + 151)
        elif concentration <= 424:
            return int(((300 - 201) / (424 - 355)) * (concentration - 355) + 201)
        elif concentration <= 604:
            return int(((500 - 301) / (604 - 425)) * (concentration - 425) + 301)
        else:
            return 500
    
    def _calculate_ozone_aqi(self, concentration: float) -> int:
        """Calculate AQI for Ozone (simplified, 8-hour average)"""
        concentration = concentration * 1000  # Convert from ppm to ppb
        if concentration <= 54:
            return int(((50 - 0) / (54 - 0)) * (concentration - 0) + 0)
        elif concentration <= 70:
            return int(((100 - 51) / (70 - 55)) * (concentration - 55) + 51)
        elif concentration <= 85:
            return int(((150 - 101) / (85 - 71)) * (concentration - 71) + 101)
        elif concentration <= 105:
            return int(((200 - 151) / (105 - 86)) * (concentration - 86) + 151)
        elif concentration <= 200:
            return int(((300 - 201) / (200 - 106)) * (concentration - 106) + 201)
        else:
            return 500
    
    def _calculate_co_aqi(self, concentration: float) -> int:
        """Calculate AQI for Carbon Monoxide"""
        if concentration <= 4.4:
            return int(((50 - 0) / (4.4 - 0)) * (concentration - 0) + 0)
        elif concentration <= 9.4:
            return int(((100 - 51) / (9.4 - 4.5)) * (concentration - 4.5) + 51)
        elif concentration <= 12.4:
            return int(((150 - 101) / (12.4 - 9.5)) * (concentration - 9.5) + 101)
        elif concentration <= 15.4:
            return int(((200 - 151) / (15.4 - 12.5)) * (concentration - 12.5) + 151)
        elif concentration <= 30.4:
            return int(((300 - 201) / (30.4 - 15.5)) * (concentration - 15.5) + 201)
        elif concentration <= 50.4:
            return int(((500 - 301) / (50.4 - 30.5)) * (concentration - 30.5) + 301)
        else:
            return 500
    
    def _calculate_no2_aqi(self, concentration: float) -> int:
        """Calculate AQI for Nitrogen Dioxide"""
        if concentration <= 53:
            return int(((50 - 0) / (53 - 0)) * (concentration - 0) + 0)
        elif concentration <= 100:
            return int(((100 - 51) / (100 - 54)) * (concentration - 54) + 51)
        elif concentration <= 360:
            return int(((150 - 101) / (360 - 101)) * (concentration - 101) + 101)
        elif concentration <= 649:
            return int(((200 - 151) / (649 - 361)) * (concentration - 361) + 151)
        elif concentration <= 1249:
            return int(((300 - 201) / (1249 - 650)) * (concentration - 650) + 201)
        elif concentration <= 2049:
            return int(((500 - 301) / (2049 - 1250)) * (concentration - 1250) + 301)
        else:
            return 500
    
    def _calculate_so2_aqi(self, concentration: float) -> int:
        """Calculate AQI for Sulfur Dioxide"""
        if concentration <= 35:
            return int(((50 - 0) / (35 - 0)) * (concentration - 0) + 0)
        elif concentration <= 75:
            return int(((100 - 51) / (75 - 36)) * (concentration - 36) + 51)
        elif concentration <= 185:
            return int(((150 - 101) / (185 - 76)) * (concentration - 76) + 101)
        elif concentration <= 304:
            return int(((200 - 151) / (304 - 186)) * (concentration - 186) + 151)
        elif concentration <= 604:
            return int(((300 - 201) / (604 - 305)) * (concentration - 305) + 201)
        elif concentration <= 1004:
            return int(((500 - 301) / (1004 - 605)) * (concentration - 605) + 301)
        else:
            return 500
    
    def _get_aqi_category(self, aqi: int) -> str:
        """Get AQI category from AQI value"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        elif aqi <= 500:
            return "Hazardous"
        else:
            return "Extremely Hazardous"
    
    def _get_aqi_health_info(self, aqi: int) -> tuple:
        """Get health implications and sensitive groups for AQI value"""
        if aqi <= 50:
            return "Air quality is considered satisfactory, and air pollution poses little or no risk.", "None"
        elif aqi <= 100:
            return "Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people.", "People who are unusually sensitive to air pollution."
        elif aqi <= 150:
            return "Members of sensitive groups may experience health effects. The general public is not likely to be affected.", "People with heart or lung disease, older adults, children, and people of lower socioeconomic status."
        elif aqi <= 200:
            return "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.", "People with heart or lung disease, older adults, children, and people of lower socioeconomic status."
        elif aqi <= 300:
            return "Health warnings of emergency conditions. The entire population is more likely to be affected.", "Everyone"
        else:
            return "Health alert: everyone may experience more serious health effects.", "Everyone"