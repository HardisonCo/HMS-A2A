"""
Repository implementation for Environmental Quality Monitoring service.
Provides data access operations for environmental measurements and monitoring sites.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import json
import os
import logging

from agency_implementation.epa.models.base import EPARepository, PollutantType
from agency_implementation.epa.models.environmental_quality import (
    MonitoringSite, EnvironmentalMeasurement, AirQualityIndex,
    WaterQualityMeasurement, SoilQualityMeasurement, EnvironmentalAlert
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringSiteRepository(EPARepository):
    """Repository for environmental monitoring sites"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.sites: Dict[str, MonitoringSite] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"MonitoringSiteRepository initialized with {len(self.sites)} sites")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for site_data in data.get('sites', []):
                site = MonitoringSite.from_dict(site_data)
                self.sites[site.id] = site
                
            logger.info(f"Loaded {len(self.sites)} sites from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'sites': [site.to_dict() for site in self.sites.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.sites)} sites to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[MonitoringSite]:
        """Get a site by ID"""
        return self.sites.get(entity_id)
    
    def get_all(self) -> List[MonitoringSite]:
        """Get all sites"""
        return list(self.sites.values())
    
    def create(self, entity: MonitoringSite) -> MonitoringSite:
        """Create a new site"""
        self.sites[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: MonitoringSite) -> MonitoringSite:
        """Update an existing site"""
        if entity.id not in self.sites:
            raise ValueError(f"Site with ID {entity.id} does not exist")
            
        self.sites[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a site by ID"""
        if entity_id in self.sites:
            del self.sites[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[MonitoringSite]:
        """Find sites matching criteria"""
        results = []
        
        for site in self.sites.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(site, key) or getattr(site, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(site)
                
        return results
    
    def find_by_region(self, region: str) -> List[MonitoringSite]:
        """Find sites by EPA region"""
        return [site for site in self.sites.values() 
                if hasattr(site, 'epa_region') and site.epa_region == region]
    
    def find_by_parameters_monitored(self, parameter: str) -> List[MonitoringSite]:
        """Find sites monitoring a specific parameter"""
        return [site for site in self.sites.values() 
                if hasattr(site, 'parameters_monitored') and 
                parameter in site.parameters_monitored]
    
    def find_active_sites(self) -> List[MonitoringSite]:
        """Find active monitoring sites"""
        return [site for site in self.sites.values() 
                if hasattr(site, 'active') and site.active]
    
    def find_by_site_type(self, site_type: str) -> List[MonitoringSite]:
        """Find sites by type"""
        return [site for site in self.sites.values() 
                if hasattr(site, 'site_type') and site.site_type == site_type]
    
    def find_by_geographic_area(
        self, 
        min_lat: float, 
        min_lon: float, 
        max_lat: float, 
        max_lon: float
    ) -> List[MonitoringSite]:
        """Find sites within a geographic bounding box"""
        results = []
        
        for site in self.sites.values():
            if not hasattr(site, 'location'):
                continue
                
            lat = site.location.latitude
            lon = site.location.longitude
            
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                results.append(site)
                
        return results
    
    def find_by_operating_agency(self, agency: str) -> List[MonitoringSite]:
        """Find sites by operating agency"""
        return [site for site in self.sites.values() 
                if hasattr(site, 'operating_agency') and site.operating_agency == agency]
    
    def find_by_pollutant_type(self, pollutant_type: PollutantType) -> List[MonitoringSite]:
        """Find sites monitoring a specific pollutant type"""
        if isinstance(pollutant_type, PollutantType):
            pollutant_type = pollutant_type.value
            
        return [site for site in self.sites.values() 
                if hasattr(site, 'parameters_monitored') and 
                pollutant_type in site.parameters_monitored]
    
    def find_by_maintenance_needed(self, days_threshold: int = 180) -> List[MonitoringSite]:
        """Find sites that may need maintenance based on last maintenance date"""
        results = []
        today = datetime.now().date()
        
        for site in self.sites.values():
            if not hasattr(site, 'last_maintenance_date') or not site.last_maintenance_date:
                results.append(site)
                continue
                
            maint_date = site.last_maintenance_date
            if isinstance(maint_date, str):
                maint_date = datetime.fromisoformat(maint_date).date()
                
            days_since_maintenance = (today - maint_date).days
            if days_since_maintenance >= days_threshold:
                results.append(site)
                
        return results


class EnvironmentalMeasurementRepository(EPARepository):
    """Repository for environmental measurements"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.measurements: Dict[str, EnvironmentalMeasurement] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"EnvironmentalMeasurementRepository initialized with {len(self.measurements)} measurements")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for measurement_data in data.get('measurements', []):
                # Determine the correct class based on data
                if 'water_body_type' in measurement_data:
                    measurement = WaterQualityMeasurement.from_dict(measurement_data)
                elif 'soil_type' in measurement_data:
                    measurement = SoilQualityMeasurement.from_dict(measurement_data)
                else:
                    measurement = EnvironmentalMeasurement.from_dict(measurement_data)
                    
                self.measurements[measurement.id] = measurement
                
            logger.info(f"Loaded {len(self.measurements)} measurements from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'measurements': [measurement.to_dict() for measurement in self.measurements.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.measurements)} measurements to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[EnvironmentalMeasurement]:
        """Get a measurement by ID"""
        return self.measurements.get(entity_id)
    
    def get_all(self) -> List[EnvironmentalMeasurement]:
        """Get all measurements"""
        return list(self.measurements.values())
    
    def create(self, entity: EnvironmentalMeasurement) -> EnvironmentalMeasurement:
        """Create a new measurement"""
        self.measurements[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: EnvironmentalMeasurement) -> EnvironmentalMeasurement:
        """Update an existing measurement"""
        if entity.id not in self.measurements:
            raise ValueError(f"Measurement with ID {entity.id} does not exist")
            
        self.measurements[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a measurement by ID"""
        if entity_id in self.measurements:
            del self.measurements[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[EnvironmentalMeasurement]:
        """Find measurements matching criteria"""
        results = []
        
        for measurement in self.measurements.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(measurement, key) or getattr(measurement, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(measurement)
                
        return results
    
    def find_by_site_id(self, site_id: str) -> List[EnvironmentalMeasurement]:
        """Find measurements by site ID"""
        return [m for m in self.measurements.values() 
                if hasattr(m, 'site_id') and m.site_id == site_id]
    
    def find_by_parameter(self, parameter: str) -> List[EnvironmentalMeasurement]:
        """Find measurements by parameter type"""
        return [m for m in self.measurements.values() 
                if hasattr(m, 'parameter') and m.parameter == parameter]
    
    def find_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str],
        date_field: str = 'timestamp'
    ) -> List[EnvironmentalMeasurement]:
        """Find measurements within a date range"""
        # Convert string dates to datetime objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
            
        results = []
        
        for measurement in self.measurements.values():
            if not hasattr(measurement, date_field):
                continue
                
            measurement_date = getattr(measurement, date_field)
            
            # Convert string date to datetime object if needed
            if isinstance(measurement_date, str):
                measurement_date = datetime.fromisoformat(measurement_date)
                
            if start_date <= measurement_date <= end_date:
                results.append(measurement)
                
        return results
    
    def find_by_pollutant_type(self, pollutant_type: PollutantType) -> List[EnvironmentalMeasurement]:
        """Find measurements by pollutant type"""
        if isinstance(pollutant_type, PollutantType):
            pollutant_type = pollutant_type.value
            
        return [m for m in self.measurements.values() 
                if hasattr(m, 'pollutant_type') and m.pollutant_type == pollutant_type]
    
    def find_by_quality_flag(self, quality_flag: str) -> List[EnvironmentalMeasurement]:
        """Find measurements by quality flag"""
        return [m for m in self.measurements.values() 
                if hasattr(m, 'quality_flag') and m.quality_flag == quality_flag]
    
    def find_exceeded_thresholds(self, threshold_values: Dict[str, float]) -> List[EnvironmentalMeasurement]:
        """Find measurements exceeding specified threshold values"""
        results = []
        
        for measurement in self.measurements.values():
            parameter = getattr(measurement, 'parameter', None)
            value = getattr(measurement, 'value', None)
            
            if parameter and value is not None and parameter in threshold_values:
                if value > threshold_values[parameter]:
                    results.append(measurement)
                    
        return results
    
    def find_water_quality_measurements(self) -> List[WaterQualityMeasurement]:
        """Find all water quality measurements"""
        return [m for m in self.measurements.values() if isinstance(m, WaterQualityMeasurement)]
    
    def find_soil_quality_measurements(self) -> List[SoilQualityMeasurement]:
        """Find all soil quality measurements"""
        return [m for m in self.measurements.values() if isinstance(m, SoilQualityMeasurement)]
    
    def find_by_geographic_area(
        self, 
        min_lat: float, 
        min_lon: float, 
        max_lat: float, 
        max_lon: float
    ) -> List[EnvironmentalMeasurement]:
        """Find measurements within a geographic area by joining with monitoring sites"""
        # This would typically be done with a JOIN in a real database
        # For this implementation, we assume site_id refers to MonitoringSite.id
        # and we need a reference to a MonitoringSiteRepository
        raise NotImplementedError("Geographic filtering requires site repository integration")


class EnvironmentalAlertRepository(EPARepository):
    """Repository for environmental alerts"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.alerts: Dict[str, EnvironmentalAlert] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"EnvironmentalAlertRepository initialized with {len(self.alerts)} alerts")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for alert_data in data.get('alerts', []):
                alert = EnvironmentalAlert.from_dict(alert_data)
                self.alerts[alert.id] = alert
                
            logger.info(f"Loaded {len(self.alerts)} alerts from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'alerts': [alert.to_dict() for alert in self.alerts.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.alerts)} alerts to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[EnvironmentalAlert]:
        """Get an alert by ID"""
        return self.alerts.get(entity_id)
    
    def get_all(self) -> List[EnvironmentalAlert]:
        """Get all alerts"""
        return list(self.alerts.values())
    
    def create(self, entity: EnvironmentalAlert) -> EnvironmentalAlert:
        """Create a new alert"""
        self.alerts[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: EnvironmentalAlert) -> EnvironmentalAlert:
        """Update an existing alert"""
        if entity.id not in self.alerts:
            raise ValueError(f"Alert with ID {entity.id} does not exist")
            
        self.alerts[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete an alert by ID"""
        if entity_id in self.alerts:
            del self.alerts[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[EnvironmentalAlert]:
        """Find alerts matching criteria"""
        results = []
        
        for alert in self.alerts.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(alert, key) or getattr(alert, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(alert)
                
        return results
    
    def find_by_site_id(self, site_id: str) -> List[EnvironmentalAlert]:
        """Find alerts by site ID"""
        return [a for a in self.alerts.values() 
                if hasattr(a, 'site_id') and a.site_id == site_id]
    
    def find_by_parameter(self, parameter: str) -> List[EnvironmentalAlert]:
        """Find alerts by parameter"""
        return [a for a in self.alerts.values() 
                if hasattr(a, 'parameter') and a.parameter == parameter]
    
    def find_by_severity(self, severity: str) -> List[EnvironmentalAlert]:
        """Find alerts by severity level"""
        return [a for a in self.alerts.values() 
                if hasattr(a, 'severity') and a.severity == severity]
    
    def find_by_status(self, status: str) -> List[EnvironmentalAlert]:
        """Find alerts by status"""
        return [a for a in self.alerts.values() 
                if hasattr(a, 'status') and a.status == status]
    
    def find_active_alerts(self) -> List[EnvironmentalAlert]:
        """Find all active alerts"""
        return self.find_by_status("ACTIVE")
    
    def find_by_date_range(
        self, 
        start_date: Union[datetime, str], 
        end_date: Union[datetime, str],
        date_field: str = 'timestamp'
    ) -> List[EnvironmentalAlert]:
        """Find alerts within a date range"""
        # Convert string dates to datetime objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
            
        results = []
        
        for alert in self.alerts.values():
            if not hasattr(alert, date_field):
                continue
                
            alert_date = getattr(alert, date_field)
            
            # Convert string date to datetime object if needed
            if isinstance(alert_date, str):
                alert_date = datetime.fromisoformat(alert_date)
                
            if start_date <= alert_date <= end_date:
                results.append(alert)
                
        return results
    
    def find_by_exceedance_percentage(self, min_percentage: float) -> List[EnvironmentalAlert]:
        """Find alerts with exceedance percentage above minimum"""
        results = []
        
        for alert in self.alerts.values():
            if (hasattr(alert, 'value') and hasattr(alert, 'threshold') and 
                    alert.threshold > 0):
                exceedance = ((alert.value - alert.threshold) / alert.threshold) * 100
                if exceedance >= min_percentage:
                    results.append(alert)
                    
        return results