"""
Adapters for the Disaster Risk Monitoring service.
Integrates with external monitoring systems and notification services.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import requests
from abc import ABC, abstractmethod

from agency_implementation.fema.models.disaster import (
    HazardMeasurement, DisasterAlert, DisasterForecast
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringSystemAdapter(ABC):
    """
    Base adapter for external monitoring systems.
    Provides interface for fetching data from external monitoring systems.
    """
    
    @abstractmethod
    def fetch_data(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch data from the monitoring system.
        
        Args:
            **params: Parameters for the data request
            
        Returns:
            List of data records
        """
        pass
    
    @abstractmethod
    def convert_to_measurement(self, record: Dict[str, Any]) -> Optional[HazardMeasurement]:
        """
        Convert a monitoring system record to a hazard measurement.
        
        Args:
            record: Data record from the monitoring system
            
        Returns:
            HazardMeasurement instance or None if conversion fails
        """
        pass


class WeatherMonitoringAdapter(MonitoringSystemAdapter):
    """
    Adapter for weather monitoring systems (e.g., NOAA, NWS).
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize weather monitoring adapter.
        
        Args:
            api_url: URL for the weather monitoring API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.default_params = self.config.get('default_params', {})
        
        logger.info("Initialized WeatherMonitoringAdapter")
    
    def fetch_data(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch weather data from the monitoring system.
        
        Args:
            **params: Parameters for the weather data request
            
        Returns:
            List of weather data records
            
        Raises:
            RuntimeError: If API request fails
        """
        # Combine default params with provided params
        request_params = {**self.default_params, **params}
        
        # If API is not configured, return mock data for testing
        if not self.api_url:
            logger.warning("API URL not configured, returning mock data")
            return self._get_mock_data(**request_params)
        
        try:
            # Add API key to parameters if available
            if self.api_key:
                request_params['apikey'] = self.api_key
                
            # Make API request
            response = requests.get(self.api_url, params=request_params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                raise RuntimeError(f"Weather API request failed with status {response.status_code}")
                
            # Parse response
            data = response.json()
            
            # Extract records from response (adjust based on actual API response structure)
            records = data.get('results', [])
            logger.info(f"Fetched {len(records)} weather records")
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            raise RuntimeError(f"Failed to fetch weather data: {str(e)}")
    
    def convert_to_measurement(self, record: Dict[str, Any]) -> Optional[HazardMeasurement]:
        """
        Convert a weather record to a hazard measurement.
        
        Args:
            record: Weather data record
            
        Returns:
            HazardMeasurement instance or None if conversion fails
        """
        try:
            # Extract required fields from record (adjust based on actual data structure)
            if 'parameter' not in record or 'value' not in record:
                logger.warning(f"Missing required fields in record: {record}")
                return None
                
            # Map weather parameters to hazard types
            parameter_to_hazard = {
                'wind_speed': 'hurricane',
                'precipitation': 'flood',
                'temperature': 'drought',
                'snowfall': 'winter_storm',
                'visibility': 'winter_storm'
            }
            
            # Create measurement object
            measurement = HazardMeasurement(
                parameter=record['parameter'],
                value=float(record['value']),
                unit=record.get('unit', 'unknown'),
                location={
                    'latitude': record.get('latitude'),
                    'longitude': record.get('longitude')
                },
                data_source=record.get('source', 'weather_api'),
                timestamp=record.get('timestamp', datetime.now().isoformat()),
                hazard_type=parameter_to_hazard.get(record['parameter']),
                quality_flag=record.get('quality', 'VALID')
            )
            
            return measurement
            
        except Exception as e:
            logger.error(f"Error converting weather record: {str(e)}")
            return None
    
    def _get_mock_data(self, **params) -> List[Dict[str, Any]]:
        """
        Generate mock weather data for testing.
        
        Args:
            **params: Parameters to customize mock data
            
        Returns:
            List of mock weather records
        """
        # Generate basic mock data
        mock_data = [
            {
                'id': '001',
                'parameter': 'wind_speed',
                'value': 45.5,
                'unit': 'mph',
                'latitude': 32.7157,
                'longitude': -117.1611,
                'source': 'mock_weather_api',
                'timestamp': datetime.now().isoformat(),
                'quality': 'VALID'
            },
            {
                'id': '002',
                'parameter': 'precipitation',
                'value': 3.2,
                'unit': 'in',
                'latitude': 32.7157,
                'longitude': -117.1611,
                'source': 'mock_weather_api',
                'timestamp': datetime.now().isoformat(),
                'quality': 'VALID'
            },
            {
                'id': '003',
                'parameter': 'temperature',
                'value': 98.6,
                'unit': '°F',
                'latitude': 32.7157,
                'longitude': -117.1611,
                'source': 'mock_weather_api',
                'timestamp': datetime.now().isoformat(),
                'quality': 'VALID'
            }
        ]
        
        # Customize based on parameters
        if 'parameter' in params:
            mock_data = [record for record in mock_data if record['parameter'] == params['parameter']]
            
        return mock_data


class SeismicMonitoringAdapter(MonitoringSystemAdapter):
    """
    Adapter for seismic monitoring systems (e.g., USGS).
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize seismic monitoring adapter.
        
        Args:
            api_url: URL for the seismic monitoring API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.default_params = self.config.get('default_params', {})
        
        logger.info("Initialized SeismicMonitoringAdapter")
    
    def fetch_data(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch seismic data from the monitoring system.
        
        Args:
            **params: Parameters for the seismic data request
            
        Returns:
            List of seismic data records
            
        Raises:
            RuntimeError: If API request fails
        """
        # Combine default params with provided params
        request_params = {**self.default_params, **params}
        
        # If API is not configured, return mock data for testing
        if not self.api_url:
            logger.warning("API URL not configured, returning mock data")
            return self._get_mock_data(**request_params)
        
        try:
            # Add API key to parameters if available
            if self.api_key:
                request_params['apikey'] = self.api_key
                
            # Make API request
            response = requests.get(self.api_url, params=request_params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                raise RuntimeError(f"Seismic API request failed with status {response.status_code}")
                
            # Parse response
            data = response.json()
            
            # Extract records from response (adjust based on actual API response structure)
            records = data.get('features', [])
            logger.info(f"Fetched {len(records)} seismic records")
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching seismic data: {str(e)}")
            raise RuntimeError(f"Failed to fetch seismic data: {str(e)}")
    
    def convert_to_measurement(self, record: Dict[str, Any]) -> Optional[HazardMeasurement]:
        """
        Convert a seismic record to a hazard measurement.
        
        Args:
            record: Seismic data record
            
        Returns:
            HazardMeasurement instance or None if conversion fails
        """
        try:
            # Extract required fields from record (adjust based on actual data structure)
            properties = record.get('properties', {})
            geometry = record.get('geometry', {})
            
            if not properties or 'mag' not in properties:
                logger.warning(f"Missing required fields in record: {record}")
                return None
                
            # Get coordinates from geometry
            coordinates = geometry.get('coordinates', [0, 0, 0])
            longitude, latitude, depth = coordinates
            
            # Create measurement object
            measurement = HazardMeasurement(
                parameter='magnitude',
                value=float(properties['mag']),
                unit='richter',
                location={
                    'latitude': latitude,
                    'longitude': longitude
                },
                data_source='usgs',
                timestamp=properties.get('time', datetime.now().isoformat()),
                hazard_type='earthquake',
                quality_flag='VALID',
                instrument_id=properties.get('net')
            )
            
            return measurement
            
        except Exception as e:
            logger.error(f"Error converting seismic record: {str(e)}")
            return None
    
    def _get_mock_data(self, **params) -> List[Dict[str, Any]]:
        """
        Generate mock seismic data for testing.
        
        Args:
            **params: Parameters to customize mock data
            
        Returns:
            List of mock seismic records
        """
        # Generate basic mock data
        mock_data = [
            {
                'type': 'Feature',
                'properties': {
                    'mag': 3.5,
                    'place': '15km NE of Los Angeles, CA',
                    'time': datetime.now().isoformat(),
                    'net': 'ci'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-118.2437, 34.0522, 10.0]
                },
                'id': 'ci38695658'
            },
            {
                'type': 'Feature',
                'properties': {
                    'mag': 2.1,
                    'place': '5km SW of San Francisco, CA',
                    'time': datetime.now().isoformat(),
                    'net': 'nc'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-122.4194, 37.7749, 5.0]
                },
                'id': 'nc73649170'
            }
        ]
        
        # Customize based on parameters
        if 'minmagnitude' in params:
            min_magnitude = float(params['minmagnitude'])
            mock_data = [
                record for record in mock_data 
                if record['properties']['mag'] >= min_magnitude
            ]
            
        return mock_data


class AlertNotificationAdapter(ABC):
    """
    Base adapter for alert notification services.
    Provides interface for sending alert notifications through various channels.
    """
    
    @abstractmethod
    def send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        Send an alert notification.
        
        Args:
            notification_data: Data for the notification
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def format_notification(self, alert: DisasterAlert) -> Dict[str, Any]:
        """
        Format an alert for notification delivery.
        
        Args:
            alert: The alert to format
            
        Returns:
            Formatted notification data
        """
        pass


class EmailNotificationAdapter(AlertNotificationAdapter):
    """
    Adapter for email notification services.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize email notification adapter.
        
        Args:
            api_url: URL for the email service API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.from_address = self.config.get('from_address', 'notifications@fema.gov')
        self.recipients = self.config.get('recipients', [])
        
        logger.info("Initialized EmailNotificationAdapter")
    
    def send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        Send an email notification.
        
        Args:
            notification_data: Data for the email notification
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info(f"Would send email: {notification_data['subject']}")
            return True
        
        try:
            # Prepare email data
            email_data = {
                'from': self.from_address,
                'to': notification_data.get('recipients', self.recipients),
                'subject': notification_data['title'],
                'text': notification_data['message'],
                'html': notification_data.get('html')
            }
            
            # Add API key to headers if available
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.post(
                self.api_url, 
                json=email_data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code not in (200, 201, 202):
                logger.error(f"Email API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"Email notification sent: {notification_data['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    def format_notification(self, alert: DisasterAlert) -> Dict[str, Any]:
        """
        Format an alert for email notification.
        
        Args:
            alert: The alert to format
            
        Returns:
            Formatted email notification data
        """
        # Get severity color
        severity_colors = {
            'ADVISORY': '#ffcc00',
            'WATCH': '#ff9900',
            'WARNING': '#ff3300',
            'EMERGENCY': '#cc0000'
        }
        color = severity_colors.get(alert.alert_level, '#333333')
        
        # Format basic notification
        notification = {
            'title': f"FEMA {alert.alert_level}: {alert.hazard_type.title()}",
            'message': alert.message,
            'recipients': self.recipients,
            'timestamp': datetime.now().isoformat(),
            'alert_id': alert.id,
            'alert_level': alert.alert_level,
            'hazard_type': alert.hazard_type
        }
        
        # Format HTML version
        html = f"""
        <html>
        <body>
            <h2 style="color: {color};">FEMA {alert.alert_level}: {alert.hazard_type.title()}</h2>
            <p>{alert.message}</p>
            
            <h3>Details:</h3>
            <ul>
                <li><strong>Alert ID:</strong> {alert.id}</li>
                <li><strong>Alert Level:</strong> {alert.alert_level}</li>
                <li><strong>Hazard Type:</strong> {alert.hazard_type}</li>
                <li><strong>Issued:</strong> {alert.timestamp}</li>
        """
        
        # Add optional details if available
        if hasattr(alert, 'expected_onset') and alert.expected_onset:
            html += f"<li><strong>Expected Onset:</strong> {alert.expected_onset}</li>\n"
            
        if hasattr(alert, 'expected_duration') and alert.expected_duration:
            html += f"<li><strong>Expected Duration:</strong> {alert.expected_duration}</li>\n"
            
        if hasattr(alert, 'affected_population') and alert.affected_population:
            html += f"<li><strong>Affected Population:</strong> {alert.affected_population:,}</li>\n"
            
        html += "</ul>\n"
        
        # Add recommended actions if available
        if hasattr(alert, 'recommended_actions') and alert.recommended_actions:
            html += "<h3>Recommended Actions:</h3>\n<ul>\n"
            for action in alert.recommended_actions:
                html += f"<li>{action}</li>\n"
            html += "</ul>\n"
            
        html += """
        <p>This is an official notification from the Federal Emergency Management Agency.</p>
        </body>
        </html>
        """
        
        notification['html'] = html
        
        return notification


class SMSNotificationAdapter(AlertNotificationAdapter):
    """
    Adapter for SMS notification services.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize SMS notification adapter.
        
        Args:
            api_url: URL for the SMS service API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.from_number = self.config.get('from_number')
        self.recipients = self.config.get('recipients', [])
        
        logger.info("Initialized SMSNotificationAdapter")
    
    def send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        Send an SMS notification.
        
        Args:
            notification_data: Data for the SMS notification
            
        Returns:
            True if SMS was sent successfully, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info(f"Would send SMS: {notification_data['message']}")
            return True
        
        try:
            # Prepare SMS data
            sms_data = {
                'from': self.from_number,
                'to': notification_data.get('recipients', self.recipients),
                'text': notification_data['message']
            }
            
            # Add API key to headers if available
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.post(
                self.api_url, 
                json=sms_data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code not in (200, 201, 202):
                logger.error(f"SMS API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"SMS notification sent: {notification_data['message'][:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
            return False
    
    def format_notification(self, alert: DisasterAlert) -> Dict[str, Any]:
        """
        Format an alert for SMS notification.
        
        Args:
            alert: The alert to format
            
        Returns:
            Formatted SMS notification data
        """
        # Format message with character limit for SMS
        message = f"FEMA {alert.alert_level}: {alert.hazard_type.title()}. {alert.message}"
        
        # Truncate if too long for SMS
        if len(message) > 160:
            message = message[:157] + "..."
            
        notification = {
            'message': message,
            'recipients': self.recipients,
            'alert_id': alert.id,
            'alert_level': alert.alert_level,
            'hazard_type': alert.hazard_type
        }
        
        return notification