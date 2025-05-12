"""
Adapters for integrating with external monitoring systems and notification services.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import requests
from abc import ABC, abstractmethod

from agency_implementation.epa.models.environmental_quality import (
    EnvironmentalMeasurement, WaterQualityMeasurement, 
    SoilQualityMeasurement, EnvironmentalAlert
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExternalSystemAdapter(ABC):
    """Base class for external system adapters"""
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch data from external system"""
        pass
    
    @abstractmethod
    def send_data(self, data: Any) -> bool:
        """Send data to external system"""
        pass


class MonitoringSystemAdapter(ExternalSystemAdapter):
    """
    Adapter for external monitoring system integration.
    
    Provides methods to fetch and send data to/from external monitoring systems,
    such as air quality networks, water quality monitoring systems, etc.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration dictionary with connection details
        """
        self.config = config
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = config.get('timeout', 30)
        self.default_params = config.get('default_params', {})
        
        logger.info(f"MonitoringSystemAdapter initialized for {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from external monitoring system.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of data records from the monitoring system
            
        Raises:
            ConnectionError: If connection to the monitoring system fails
        """
        try:
            # In a real implementation, this would make an API call to the monitoring system
            # For demonstration, we return mock data
            if not self.api_url:
                logger.warning("API URL not configured, returning mock data")
                return self._generate_mock_data(kwargs.get('count', 5))
            
            endpoint = kwargs.get('endpoint', 'measurements')
            url = f"{self.api_url}/{endpoint}"
            
            # Combine default params with provided kwargs
            params = {**self.default_params, **kwargs}
            if 'endpoint' in params:
                del params['endpoint']
                
            logger.info(f"Fetching data from {url} with params: {params}")
            
            # This is where an actual API call would happen
            # response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, return mock data
            return self._generate_mock_data(kwargs.get('count', 5))
            
        except Exception as e:
            logger.error(f"Error fetching data from monitoring system: {str(e)}")
            raise ConnectionError(f"Failed to connect to monitoring system: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to monitoring system.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the monitoring system
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send data: {json.dumps(data, default=str)}")
                return True
            
            endpoint = data.get('endpoint', 'upload')
            url = f"{self.api_url}/{endpoint}"
            
            if 'endpoint' in data:
                data_to_send = {k: v for k, v in data.items() if k != 'endpoint'}
            else:
                data_to_send = data
                
            logger.info(f"Sending data to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data_to_send, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send data: {json.dumps(data_to_send, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to monitoring system: {str(e)}")
            return False
    
    def convert_to_measurement(self, data: Dict[str, Any]) -> Optional[EnvironmentalMeasurement]:
        """
        Convert external monitoring system data to an EnvironmentalMeasurement object.
        
        Args:
            data: Data from monitoring system
            
        Returns:
            Converted EnvironmentalMeasurement object or None if conversion fails
        """
        try:
            # Extract required fields
            site_id = data.get('site_id') or data.get('station_id')
            if not site_id:
                logger.error("Missing site ID in monitoring data")
                return None
            
            parameter = data.get('parameter') or data.get('metric')
            if not parameter:
                logger.error("Missing parameter in monitoring data")
                return None
            
            value = data.get('value') or data.get('reading')
            if value is None:
                logger.error("Missing value in monitoring data")
                return None
            
            unit = data.get('unit') or data.get('unit_of_measure')
            if not unit:
                logger.error("Missing unit in monitoring data")
                return None
            
            # Extract timestamp
            timestamp = data.get('timestamp') or data.get('reading_time') or datetime.now().isoformat()
            
            # Determine measurement type based on data
            measurement_type = data.get('measurement_type') or data.get('media_type')
            
            # Create appropriate measurement object based on type
            if measurement_type == 'water':
                # Extract water-specific fields
                water_body_type = data.get('water_body_type') or 'unknown'
                water_body_name = data.get('water_body_name')
                depth = data.get('depth')
                flow_rate = data.get('flow_rate')
                
                measurement = WaterQualityMeasurement(
                    site_id=site_id,
                    parameter=parameter,
                    value=value,
                    unit=unit,
                    timestamp=timestamp,
                    water_body_type=water_body_type,
                    water_body_name=water_body_name,
                    depth=depth,
                    flow_rate=flow_rate,
                    collection_method=data.get('collection_method'),
                    quality_flag=data.get('quality_flag', 'VALID'),
                    pollutant_type=data.get('pollutant_type')
                )
            elif measurement_type == 'soil':
                # Extract soil-specific fields
                soil_type = data.get('soil_type') or 'unknown'
                depth = data.get('depth')
                land_use = data.get('land_use')
                
                measurement = SoilQualityMeasurement(
                    site_id=site_id,
                    parameter=parameter,
                    value=value,
                    unit=unit,
                    timestamp=timestamp,
                    soil_type=soil_type,
                    depth=depth,
                    land_use=land_use,
                    soil_moisture=data.get('soil_moisture'),
                    soil_temperature=data.get('soil_temperature'),
                    collection_method=data.get('collection_method'),
                    quality_flag=data.get('quality_flag', 'VALID'),
                    pollutant_type=data.get('pollutant_type')
                )
            else:
                # Default to basic environmental measurement
                measurement = EnvironmentalMeasurement(
                    site_id=site_id,
                    parameter=parameter,
                    value=value,
                    unit=unit,
                    timestamp=timestamp,
                    collection_method=data.get('collection_method'),
                    quality_flag=data.get('quality_flag', 'VALID'),
                    instrument_id=data.get('instrument_id'),
                    detection_limit=data.get('detection_limit'),
                    uncertainty=data.get('uncertainty'),
                    pollutant_type=data.get('pollutant_type')
                )
            
            return measurement
            
        except Exception as e:
            logger.error(f"Error converting monitoring data to measurement: {str(e)}")
            return None
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock monitoring system data for demonstration"""
        from random import random, choice, uniform
        
        mock_data = []
        
        # Sample parameters by media type
        air_parameters = ["PM25", "PM10", "OZONE", "CO", "NO2", "SO2"]
        water_parameters = ["PH", "DISSOLVED_OXYGEN", "TEMPERATURE", "NITRATES", "PHOSPHATES", "E_COLI"]
        soil_parameters = ["PH", "MOISTURE", "NITROGEN", "PHOSPHORUS", "POTASSIUM", "LEAD"]
        
        # Sample units
        units = {
            "PM25": "μg/m³",
            "PM10": "μg/m³",
            "OZONE": "ppm",
            "CO": "ppm",
            "NO2": "ppb",
            "SO2": "ppb",
            "PH": "pH units",
            "DISSOLVED_OXYGEN": "mg/L",
            "TEMPERATURE": "°C",
            "NITRATES": "mg/L",
            "PHOSPHATES": "mg/L",
            "E_COLI": "CFU/100mL",
            "MOISTURE": "%",
            "NITROGEN": "mg/kg",
            "PHOSPHORUS": "mg/kg",
            "POTASSIUM": "mg/kg",
            "LEAD": "mg/kg"
        }
        
        # Sample media types
        media_types = ["air", "water", "soil"]
        
        # Generate mock data
        for i in range(count):
            media_type = choice(media_types)
            
            if media_type == "air":
                parameter = choice(air_parameters)
                # Generate realistic value ranges for air parameters
                if parameter == "PM25":
                    value = uniform(1, 50)
                elif parameter == "PM10":
                    value = uniform(5, 150)
                elif parameter == "OZONE":
                    value = uniform(0.01, 0.1)
                elif parameter == "CO":
                    value = uniform(0.1, 10)
                elif parameter == "NO2":
                    value = uniform(1, 100)
                elif parameter == "SO2":
                    value = uniform(1, 75)
                else:
                    value = random() * 100
                
                data = {
                    "site_id": f"SITE-{1000 + i % 3}",
                    "parameter": parameter,
                    "value": value,
                    "unit": units.get(parameter, "unknown"),
                    "timestamp": datetime.now().isoformat(),
                    "measurement_type": "air",
                    "quality_flag": "VALID",
                    "instrument_id": f"INSTR-{2000 + i % 5}",
                    "pollutant_type": parameter
                }
            elif media_type == "water":
                parameter = choice(water_parameters)
                # Generate realistic value ranges for water parameters
                if parameter == "PH":
                    value = uniform(6, 9)
                elif parameter == "DISSOLVED_OXYGEN":
                    value = uniform(4, 12)
                elif parameter == "TEMPERATURE":
                    value = uniform(10, 25)
                elif parameter == "NITRATES":
                    value = uniform(0, 15)
                elif parameter == "PHOSPHATES":
                    value = uniform(0, 2)
                elif parameter == "E_COLI":
                    value = uniform(0, 200)
                else:
                    value = random() * 10
                
                data = {
                    "site_id": f"SITE-{1000 + i % 3}",
                    "parameter": parameter,
                    "value": value,
                    "unit": units.get(parameter, "unknown"),
                    "timestamp": datetime.now().isoformat(),
                    "measurement_type": "water",
                    "water_body_type": choice(["river", "lake", "stream", "reservoir"]),
                    "water_body_name": choice(["Potomac", "Mississippi", "Ohio", "Colorado"]),
                    "depth": uniform(0.5, 10),
                    "flow_rate": uniform(0, 5) if random() > 0.5 else None,
                    "quality_flag": "VALID",
                    "pollutant_type": parameter if parameter in ["NITRATES", "PHOSPHATES", "E_COLI"] else None
                }
            else:  # soil
                parameter = choice(soil_parameters)
                # Generate realistic value ranges for soil parameters
                if parameter == "PH":
                    value = uniform(5, 8)
                elif parameter == "MOISTURE":
                    value = uniform(10, 40)
                elif parameter == "NITROGEN":
                    value = uniform(0, 100)
                elif parameter == "PHOSPHORUS":
                    value = uniform(0, 50)
                elif parameter == "POTASSIUM":
                    value = uniform(0, 300)
                elif parameter == "LEAD":
                    value = uniform(0, 400)
                else:
                    value = random() * 100
                
                data = {
                    "site_id": f"SITE-{1000 + i % 3}",
                    "parameter": parameter,
                    "value": value,
                    "unit": units.get(parameter, "unknown"),
                    "timestamp": datetime.now().isoformat(),
                    "measurement_type": "soil",
                    "soil_type": choice(["clay", "silt", "sand", "loam"]),
                    "depth": uniform(0, 30),
                    "land_use": choice(["agricultural", "industrial", "residential", "forest"]),
                    "soil_moisture": uniform(10, 40) if random() > 0.5 else None,
                    "soil_temperature": uniform(5, 25) if random() > 0.5 else None,
                    "quality_flag": "VALID",
                    "pollutant_type": parameter if parameter == "LEAD" else None
                }
            
            mock_data.append(data)
        
        return mock_data


class AlertNotificationAdapter(ExternalSystemAdapter):
    """
    Adapter for alert notification delivery.
    
    Provides methods to send notifications about environmental alerts to
    various notification channels like email, SMS, mobile apps, etc.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration dictionary with connection details
        """
        self.config = config
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = config.get('timeout', 10)
        self.default_channels = config.get('default_channels', ['email'])
        self.recipients = config.get('recipients', {})
        
        logger.info(f"AlertNotificationAdapter initialized for {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch notification status data from notification system.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of notification status records
            
        Raises:
            ConnectionError: If connection to the notification system fails
        """
        try:
            # In a real implementation, this would make an API call to the notification system
            # For demonstration, we return mock data
            if not self.api_url:
                logger.warning("API URL not configured, returning mock data")
                return self._generate_mock_data(kwargs.get('count', 5))
            
            endpoint = kwargs.get('endpoint', 'status')
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Fetching notification status from {url} with params: {kwargs}")
            
            # This is where an actual API call would happen
            # response = requests.get(url, headers=self.headers, params=kwargs, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, return mock data
            return self._generate_mock_data(kwargs.get('count', 5))
            
        except Exception as e:
            logger.error(f"Error fetching data from notification system: {str(e)}")
            raise ConnectionError(f"Failed to connect to notification system: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to notification system.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the notification system
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send notification: {json.dumps(data, default=str)}")
                return True
            
            endpoint = 'send'
            if isinstance(data, dict) and 'endpoint' in data:
                endpoint = data.pop('endpoint')
                
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Sending notification to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send notification: {json.dumps(data, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    def send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        Send a notification about an environmental alert.
        
        Args:
            notification_data: Notification data including title, message, etc.
            
        Returns:
            True if successful, False otherwise
        """
        # Determine notification channels based on severity
        channels = notification_data.get('channels', self.default_channels)
        severity = notification_data.get('severity', 'MINOR')
        
        # Add additional channels for higher severity
        if severity in ['MAJOR', 'SEVERE', 'CRITICAL']:
            if 'sms' not in channels:
                channels.append('sms')
            if 'app' not in channels:
                channels.append('app')
        
        # Determine recipients based on channels
        recipients = {}
        for channel in channels:
            channel_recipients = self.recipients.get(channel, [])
            if channel_recipients:
                recipients[channel] = channel_recipients
        
        # Add recipients to notification data
        notification_data['channels'] = channels
        notification_data['recipients'] = recipients
        
        # Add timestamp if not provided
        if 'timestamp' not in notification_data:
            notification_data['timestamp'] = datetime.now().isoformat()
        
        # Send notification
        return self.send_data(notification_data)
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock notification status data for demonstration"""
        from random import choice
        
        mock_data = []
        
        statuses = ['DELIVERED', 'FAILED', 'PENDING']
        channels = ['email', 'sms', 'app']
        severities = ['MINOR', 'MODERATE', 'MAJOR', 'SEVERE', 'CRITICAL']
        
        for i in range(count):
            status = choice(statuses)
            channel = choice(channels)
            severity = choice(severities)
            
            mock_data.append({
                'notification_id': f"NOTIF-{10000 + i}",
                'alert_id': f"ALERT-{20000 + i}",
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'channel': channel,
                'severity': severity,
                'recipient': f"recipient-{i}@example.com" if channel == 'email' else f"+1555555{1000 + i}",
                'delivery_timestamp': datetime.now().isoformat() if status == 'DELIVERED' else None,
                'failure_reason': "Connection timeout" if status == 'FAILED' else None
            })
        
        return mock_data