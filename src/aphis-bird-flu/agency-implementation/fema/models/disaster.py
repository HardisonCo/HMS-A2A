"""
Disaster models for FEMA implementation.
Defines domain models for disaster risk monitoring, events, and impacts.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from agency_implementation.foundation.base_models.base import BaseModel, GeoLocation, Address
from agency_implementation.fema.models.base import (
    DisasterType, DisasterSeverity, AlertLevel, MeasurementUnit, DataSource
)


class HazardZone(BaseModel):
    """
    Geographic zone with specific hazard risks.
    Represents an area with defined boundaries that has identified hazard risks.
    """
    
    def __init__(
        self,
        zone_name: str,
        hazard_type: str,
        risk_level: str,
        boundaries: Dict[str, Any],
        jurisdiction: str = None,
        population_affected: int = None,
        last_assessment_date: str = None,
        source: str = None,
        mitigation_measures: List[str] = None,
        zone_description: str = None,
        **kwargs
    ):
        """Initialize hazard zone"""
        super().__init__(**kwargs)
        self.zone_name = zone_name
        self.hazard_type = hazard_type
        self.risk_level = risk_level
        self.boundaries = boundaries  # GeoJSON polygon or multipolygon
        self.jurisdiction = jurisdiction
        self.population_affected = population_affected
        self.last_assessment_date = last_assessment_date or datetime.now().isoformat()
        self.source = source
        self.mitigation_measures = mitigation_measures or []
        self.zone_description = zone_description


class HazardMeasurement(BaseModel):
    """
    Measurement of a hazard parameter.
    Represents a single measurement related to disaster risk.
    """
    
    def __init__(
        self,
        parameter: str,
        value: float,
        unit: str,
        location: Dict[str, Any],
        data_source: str,
        timestamp: str = None,
        quality_flag: str = "VALID",
        hazard_type: str = None,
        instrument_id: str = None,
        uncertainty: float = None,
        **kwargs
    ):
        """Initialize hazard measurement"""
        super().__init__(**kwargs)
        self.parameter = parameter
        self.value = value
        self.unit = unit
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.data_source = data_source
        self.timestamp = timestamp or datetime.now().isoformat()
        self.quality_flag = quality_flag
        self.hazard_type = hazard_type
        self.instrument_id = instrument_id
        self.uncertainty = uncertainty
    
    def exceeds_threshold(self, threshold: float) -> bool:
        """Check if measurement exceeds a threshold value"""
        return self.value > threshold


class DisasterEvent(BaseModel):
    """
    Disaster event.
    Represents a disaster occurrence with its characteristics and impacts.
    """
    
    def __init__(
        self,
        event_name: str,
        disaster_type: str,
        severity: str,
        location: Dict[str, Any],
        affected_area: Dict[str, Any] = None,
        start_time: str = None,
        end_time: str = None,
        description: str = None,
        population_affected: int = None,
        infrastructure_affected: Dict[str, Any] = None,
        economic_impact: float = None,
        fatalities: int = None,
        injuries: int = None,
        displacements: int = None,
        status: str = "ACTIVE",
        declaration_status: str = None,
        declaration_number: str = None,
        **kwargs
    ):
        """Initialize disaster event"""
        super().__init__(**kwargs)
        self.event_name = event_name
        self.disaster_type = disaster_type
        self.severity = severity
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.affected_area = affected_area  # GeoJSON polygon or multipolygon
        self.start_time = start_time or datetime.now().isoformat()
        self.end_time = end_time
        self.description = description
        self.population_affected = population_affected
        self.infrastructure_affected = infrastructure_affected or {}
        self.economic_impact = economic_impact
        self.fatalities = fatalities
        self.injuries = injuries
        self.displacements = displacements
        self.status = status
        self.declaration_status = declaration_status
        self.declaration_number = declaration_number
    
    @property
    def is_active(self) -> bool:
        """Check if disaster is currently active"""
        return self.status == "ACTIVE" and self.end_time is None
    
    @property
    def duration_hours(self) -> Optional[float]:
        """Calculate duration in hours if event has ended"""
        if not self.end_time:
            return None
        
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        
        duration = end - start
        return duration.total_seconds() / 3600
    
    def close_event(self, end_time: str = None) -> None:
        """Mark event as ended"""
        self.status = "ENDED"
        self.end_time = end_time or datetime.now().isoformat()


class DisasterAlert(BaseModel):
    """
    Disaster alert for impending or current disaster risks.
    """
    
    def __init__(
        self,
        hazard_type: str,
        alert_level: str,
        affected_area: Dict[str, Any],
        message: str,
        expected_onset: str = None,
        expected_duration: str = None,
        recommended_actions: List[str] = None,
        source: str = None,
        confidence_level: str = None,
        status: str = "ACTIVE",
        timestamp: str = None,
        expiration: str = None,
        affected_population: int = None,
        **kwargs
    ):
        """Initialize disaster alert"""
        super().__init__(**kwargs)
        self.hazard_type = hazard_type
        self.alert_level = alert_level
        self.affected_area = affected_area  # GeoJSON polygon or multipolygon
        self.message = message
        self.expected_onset = expected_onset
        self.expected_duration = expected_duration
        self.recommended_actions = recommended_actions or []
        self.source = source
        self.confidence_level = confidence_level
        self.status = status
        self.timestamp = timestamp or datetime.now().isoformat()
        self.expiration = expiration
        self.affected_population = affected_population
    
    def update_alert_level(self, new_level: str) -> None:
        """Update alert level"""
        self.alert_level = new_level
        self.updated_at = datetime.now().isoformat()
    
    def close_alert(self, resolution_notes: str = None) -> None:
        """Mark alert as expired/resolved"""
        self.status = "EXPIRED"
        self.resolution_notes = resolution_notes
        self.resolution_timestamp = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    @property
    def is_active(self) -> bool:
        """Check if alert is currently active"""
        if self.status != "ACTIVE":
            return False
            
        if self.expiration:
            return datetime.now() < datetime.fromisoformat(self.expiration)
            
        return True


class RiskAssessment(BaseModel):
    """
    Disaster risk assessment for a specific area and hazard type.
    """
    
    def __init__(
        self,
        area_name: str,
        hazard_type: str,
        risk_level: str,
        boundaries: Dict[str, Any],
        assessment_date: str = None,
        methodology: str = None,
        confidence_level: str = None,
        contributing_factors: List[Dict[str, Any]] = None,
        mitigation_recommendations: List[str] = None,
        population_at_risk: int = None,
        critical_infrastructure: List[Dict[str, Any]] = None,
        economic_exposure: float = None,
        historical_events: List[str] = None,
        expires_at: str = None,
        **kwargs
    ):
        """Initialize risk assessment"""
        super().__init__(**kwargs)
        self.area_name = area_name
        self.hazard_type = hazard_type
        self.risk_level = risk_level
        self.boundaries = boundaries  # GeoJSON polygon or multipolygon
        self.assessment_date = assessment_date or datetime.now().isoformat()
        self.methodology = methodology
        self.confidence_level = confidence_level
        self.contributing_factors = contributing_factors or []
        self.mitigation_recommendations = mitigation_recommendations or []
        self.population_at_risk = population_at_risk
        self.critical_infrastructure = critical_infrastructure or []
        self.economic_exposure = economic_exposure
        self.historical_events = historical_events or []
        self.expires_at = expires_at
    
    @property
    def is_current(self) -> bool:
        """Check if assessment is current (not expired)"""
        if not self.expires_at:
            return True
            
        return datetime.now() < datetime.fromisoformat(self.expires_at)


class ForecastModel(BaseModel):
    """
    Forecasting model for disaster prediction.
    """
    
    def __init__(
        self,
        model_name: str,
        hazard_type: str,
        model_type: str,
        description: str = None,
        parameters: Dict[str, Any] = None,
        training_period: Dict[str, str] = None,
        accuracy_metrics: Dict[str, float] = None,
        last_updated: str = None,
        version: str = None,
        data_sources: List[str] = None,
        spatial_resolution: Dict[str, Any] = None,
        temporal_resolution: str = None,
        **kwargs
    ):
        """Initialize forecast model"""
        super().__init__(**kwargs)
        self.model_name = model_name
        self.hazard_type = hazard_type
        self.model_type = model_type
        self.description = description
        self.parameters = parameters or {}
        self.training_period = training_period
        self.accuracy_metrics = accuracy_metrics or {}
        self.last_updated = last_updated or datetime.now().isoformat()
        self.version = version
        self.data_sources = data_sources or []
        self.spatial_resolution = spatial_resolution
        self.temporal_resolution = temporal_resolution


class DisasterForecast(BaseModel):
    """
    Forecast prediction for a disaster risk.
    """
    
    def __init__(
        self,
        model_id: str,
        hazard_type: str,
        forecast_area: Dict[str, Any],
        prediction_values: Dict[str, Any],
        forecast_created: str = None,
        valid_from: str = None,
        valid_to: str = None,
        confidence_level: float = None,
        scenario: str = None,
        probability: float = None,
        severity_prediction: str = None,
        expected_impacts: Dict[str, Any] = None,
        alternative_scenarios: List[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize disaster forecast"""
        super().__init__(**kwargs)
        self.model_id = model_id
        self.hazard_type = hazard_type
        self.forecast_area = forecast_area  # GeoJSON polygon or multipolygon
        self.prediction_values = prediction_values
        self.forecast_created = forecast_created or datetime.now().isoformat()
        self.valid_from = valid_from or datetime.now().isoformat()
        self.valid_to = valid_to
        self.confidence_level = confidence_level
        self.scenario = scenario
        self.probability = probability
        self.severity_prediction = severity_prediction
        self.expected_impacts = expected_impacts or {}
        self.alternative_scenarios = alternative_scenarios or []
    
    @property
    def is_current(self) -> bool:
        """Check if forecast is currently valid"""
        now = datetime.now()
        
        if self.valid_from and now < datetime.fromisoformat(self.valid_from):
            return False
            
        if self.valid_to and now > datetime.fromisoformat(self.valid_to):
            return False
            
        return True