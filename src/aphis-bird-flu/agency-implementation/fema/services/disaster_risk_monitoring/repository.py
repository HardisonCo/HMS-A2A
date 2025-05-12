"""
Repository implementations for Disaster Risk Monitoring service.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import os

from agency_implementation.foundation.base_models.base import Repository
from agency_implementation.fema.models.disaster import (
    HazardZone, HazardMeasurement, DisasterEvent, DisasterAlert,
    RiskAssessment, ForecastModel, DisasterForecast
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HazardZoneRepository(Repository[HazardZone]):
    """Repository for managing hazard zones"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "hazard_zones"
    
    def get_by_id(self, entity_id: str) -> Optional[HazardZone]:
        """Get a hazard zone by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return HazardZone.from_dict(data)
    
    def get_all(self) -> List[HazardZone]:
        """Get all hazard zones"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [HazardZone.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: HazardZone) -> HazardZone:
        """Create a new hazard zone"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created hazard zone: {entity.id}")
        
        return entity
    
    def update(self, entity: HazardZone) -> HazardZone:
        """Update an existing hazard zone"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated hazard zone: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a hazard zone by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted hazard zone: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[HazardZone]:
        """Find hazard zones matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(HazardZone.from_dict(data))
                
        return results
    
    def find_by_hazard_type(self, hazard_type: str) -> List[HazardZone]:
        """Find hazard zones by hazard type"""
        return self.find({"hazard_type": hazard_type})
    
    def find_by_risk_level(self, risk_level: str) -> List[HazardZone]:
        """Find hazard zones by risk level"""
        return self.find({"risk_level": risk_level})
    
    def find_by_jurisdiction(self, jurisdiction: str) -> List[HazardZone]:
        """Find hazard zones by jurisdiction"""
        return self.find({"jurisdiction": jurisdiction})


class HazardMeasurementRepository(Repository[HazardMeasurement]):
    """Repository for managing hazard measurements"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "hazard_measurements"
    
    def get_by_id(self, entity_id: str) -> Optional[HazardMeasurement]:
        """Get a hazard measurement by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return HazardMeasurement.from_dict(data)
    
    def get_all(self) -> List[HazardMeasurement]:
        """Get all hazard measurements"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [HazardMeasurement.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: HazardMeasurement) -> HazardMeasurement:
        """Create a new hazard measurement"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created hazard measurement: {entity.id}")
        
        return entity
    
    def update(self, entity: HazardMeasurement) -> HazardMeasurement:
        """Update an existing hazard measurement"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated hazard measurement: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a hazard measurement by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted hazard measurement: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[HazardMeasurement]:
        """Find hazard measurements matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(HazardMeasurement.from_dict(data))
                
        return results
    
    def find_by_parameter(self, parameter: str) -> List[HazardMeasurement]:
        """Find hazard measurements by parameter"""
        return self.find({"parameter": parameter})
    
    def find_by_hazard_type(self, hazard_type: str) -> List[HazardMeasurement]:
        """Find hazard measurements by hazard type"""
        return self.find({"hazard_type": hazard_type})
    
    def find_by_data_source(self, data_source: str) -> List[HazardMeasurement]:
        """Find hazard measurements by data source"""
        return self.find({"data_source": data_source})
    
    def find_by_date_range(self, start_date: str, end_date: str) -> List[HazardMeasurement]:
        """Find hazard measurements within a date range"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if 'timestamp' in data:
                measurement_date = data['timestamp']
                if start_date <= measurement_date <= end_date:
                    results.append(HazardMeasurement.from_dict(data))
                    
        return results
    
    def find_exceeded_thresholds(self, thresholds: Dict[str, float]) -> List[HazardMeasurement]:
        """Find measurements that exceed specified thresholds"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if 'parameter' in data and 'value' in data:
                parameter = data['parameter']
                value = data['value']
                
                if parameter in thresholds and value > thresholds[parameter]:
                    results.append(HazardMeasurement.from_dict(data))
                    
        return results


class DisasterEventRepository(Repository[DisasterEvent]):
    """Repository for managing disaster events"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "disaster_events"
    
    def get_by_id(self, entity_id: str) -> Optional[DisasterEvent]:
        """Get a disaster event by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return DisasterEvent.from_dict(data)
    
    def get_all(self) -> List[DisasterEvent]:
        """Get all disaster events"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [DisasterEvent.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: DisasterEvent) -> DisasterEvent:
        """Create a new disaster event"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created disaster event: {entity.id}")
        
        return entity
    
    def update(self, entity: DisasterEvent) -> DisasterEvent:
        """Update an existing disaster event"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated disaster event: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a disaster event by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted disaster event: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[DisasterEvent]:
        """Find disaster events matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(DisasterEvent.from_dict(data))
                
        return results
    
    def find_active_events(self) -> List[DisasterEvent]:
        """Find active disaster events"""
        return self.find({"status": "ACTIVE"})
    
    def find_by_disaster_type(self, disaster_type: str) -> List[DisasterEvent]:
        """Find disaster events by type"""
        return self.find({"disaster_type": disaster_type})
    
    def find_by_severity(self, severity: str) -> List[DisasterEvent]:
        """Find disaster events by severity"""
        return self.find({"severity": severity})
    
    def find_by_date_range(self, start_date: str, end_date: str) -> List[DisasterEvent]:
        """Find disaster events within a date range"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if 'start_time' in data:
                event_start = data['start_time']
                
                # Check if event started within the range
                if start_date <= event_start <= end_date:
                    results.append(DisasterEvent.from_dict(data))
                    continue
                    
                # Check if event was active during the range
                if event_start <= start_date and ('end_time' not in data or data['end_time'] is None or data['end_time'] >= start_date):
                    results.append(DisasterEvent.from_dict(data))
                    
        return results


class DisasterAlertRepository(Repository[DisasterAlert]):
    """Repository for managing disaster alerts"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "disaster_alerts"
    
    def get_by_id(self, entity_id: str) -> Optional[DisasterAlert]:
        """Get a disaster alert by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return DisasterAlert.from_dict(data)
    
    def get_all(self) -> List[DisasterAlert]:
        """Get all disaster alerts"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [DisasterAlert.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: DisasterAlert) -> DisasterAlert:
        """Create a new disaster alert"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created disaster alert: {entity.id}")
        
        return entity
    
    def update(self, entity: DisasterAlert) -> DisasterAlert:
        """Update an existing disaster alert"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated disaster alert: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a disaster alert by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted disaster alert: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[DisasterAlert]:
        """Find disaster alerts matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(DisasterAlert.from_dict(data))
                
        return results
    
    def find_active_alerts(self) -> List[DisasterAlert]:
        """Find active disaster alerts"""
        return self.find({"status": "ACTIVE"})
    
    def find_by_hazard_type(self, hazard_type: str) -> List[DisasterAlert]:
        """Find disaster alerts by hazard type"""
        return self.find({"hazard_type": hazard_type})
    
    def find_by_alert_level(self, alert_level: str) -> List[DisasterAlert]:
        """Find disaster alerts by alert level"""
        return self.find({"alert_level": alert_level})
    
    def find_by_date_range(self, start_date: str, end_date: str) -> List[DisasterAlert]:
        """Find disaster alerts within a date range"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if 'timestamp' in data:
                alert_date = data['timestamp']
                if start_date <= alert_date <= end_date:
                    results.append(DisasterAlert.from_dict(data))
                    
        return results


class RiskAssessmentRepository(Repository[RiskAssessment]):
    """Repository for managing risk assessments"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "risk_assessments"
    
    def get_by_id(self, entity_id: str) -> Optional[RiskAssessment]:
        """Get a risk assessment by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return RiskAssessment.from_dict(data)
    
    def get_all(self) -> List[RiskAssessment]:
        """Get all risk assessments"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [RiskAssessment.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: RiskAssessment) -> RiskAssessment:
        """Create a new risk assessment"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created risk assessment: {entity.id}")
        
        return entity
    
    def update(self, entity: RiskAssessment) -> RiskAssessment:
        """Update an existing risk assessment"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated risk assessment: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a risk assessment by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted risk assessment: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[RiskAssessment]:
        """Find risk assessments matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(RiskAssessment.from_dict(data))
                
        return results
    
    def find_by_hazard_type(self, hazard_type: str) -> List[RiskAssessment]:
        """Find risk assessments by hazard type"""
        return self.find({"hazard_type": hazard_type})
    
    def find_by_risk_level(self, risk_level: str) -> List[RiskAssessment]:
        """Find risk assessments by risk level"""
        return self.find({"risk_level": risk_level})
    
    def find_by_area(self, area_name: str) -> List[RiskAssessment]:
        """Find risk assessments by area name"""
        return self.find({"area_name": area_name})
    
    def find_current_assessments(self) -> List[RiskAssessment]:
        """Find current (non-expired) risk assessments"""
        now = datetime.now().isoformat()
        
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            # Include if no expiration or expiration is in the future
            if 'expires_at' not in data or data['expires_at'] is None or data['expires_at'] >= now:
                results.append(RiskAssessment.from_dict(data))
                
        return results


class ForecastModelRepository(Repository[ForecastModel]):
    """Repository for managing forecast models"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "forecast_models"
    
    def get_by_id(self, entity_id: str) -> Optional[ForecastModel]:
        """Get a forecast model by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return ForecastModel.from_dict(data)
    
    def get_all(self) -> List[ForecastModel]:
        """Get all forecast models"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [ForecastModel.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: ForecastModel) -> ForecastModel:
        """Create a new forecast model"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created forecast model: {entity.id}")
        
        return entity
    
    def update(self, entity: ForecastModel) -> ForecastModel:
        """Update an existing forecast model"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated forecast model: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a forecast model by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted forecast model: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[ForecastModel]:
        """Find forecast models matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(ForecastModel.from_dict(data))
                
        return results
    
    def find_by_hazard_type(self, hazard_type: str) -> List[ForecastModel]:
        """Find forecast models by hazard type"""
        return self.find({"hazard_type": hazard_type})
    
    def find_by_model_type(self, model_type: str) -> List[ForecastModel]:
        """Find forecast models by model type"""
        return self.find({"model_type": model_type})


class DisasterForecastRepository(Repository[DisasterForecast]):
    """Repository for managing disaster forecasts"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "disaster_forecasts"
    
    def get_by_id(self, entity_id: str) -> Optional[DisasterForecast]:
        """Get a disaster forecast by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return DisasterForecast.from_dict(data)
    
    def get_all(self) -> List[DisasterForecast]:
        """Get all disaster forecasts"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [DisasterForecast.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: DisasterForecast) -> DisasterForecast:
        """Create a new disaster forecast"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created disaster forecast: {entity.id}")
        
        return entity
    
    def update(self, entity: DisasterForecast) -> DisasterForecast:
        """Update an existing disaster forecast"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated disaster forecast: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a disaster forecast by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted disaster forecast: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[DisasterForecast]:
        """Find disaster forecasts matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(DisasterForecast.from_dict(data))
                
        return results
    
    def find_by_model_id(self, model_id: str) -> List[DisasterForecast]:
        """Find disaster forecasts by model ID"""
        return self.find({"model_id": model_id})
    
    def find_by_hazard_type(self, hazard_type: str) -> List[DisasterForecast]:
        """Find disaster forecasts by hazard type"""
        return self.find({"hazard_type": hazard_type})
    
    def find_current_forecasts(self) -> List[DisasterForecast]:
        """Find current (valid) disaster forecasts"""
        now = datetime.now().isoformat()
        
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            # Include if within valid time range
            valid_from = data.get('valid_from')
            valid_to = data.get('valid_to')
            
            if valid_from is None or now >= valid_from:
                if valid_to is None or now <= valid_to:
                    results.append(DisasterForecast.from_dict(data))
                    
        return results