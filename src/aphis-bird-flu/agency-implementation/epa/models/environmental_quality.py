"""
Environmental Quality models for EPA implementation.
Defines domain models for environmental monitoring and quality data.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from agency_implementation.foundation.base_models.base import BaseModel, GeoLocation
from agency_implementation.epa.models.base import MeasurementUnit, PollutantType


class MonitoringSite(BaseModel):
    """
    Environmental monitoring site.
    Represents a physical location where environmental quality is monitored.
    """
    
    def __init__(
        self,
        site_name: str,
        location: Dict[str, Any],
        site_type: str,
        parameters_monitored: List[str],
        active: bool = True,
        epa_region: str = None,
        installation_date: str = None,
        last_maintenance_date: str = None,
        site_description: str = None,
        operating_agency: str = None,
        **kwargs
    ):
        """Initialize monitoring site"""
        super().__init__(**kwargs)
        self.site_name = site_name
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.site_type = site_type
        self.parameters_monitored = parameters_monitored
        self.active = active
        self.epa_region = epa_region
        self.installation_date = installation_date
        self.last_maintenance_date = last_maintenance_date
        self.site_description = site_description
        self.operating_agency = operating_agency


class EnvironmentalMeasurement(BaseModel):
    """
    Environmental measurement record.
    Represents a single measurement of an environmental parameter.
    """
    
    def __init__(
        self,
        site_id: str,
        parameter: str,
        value: float,
        unit: str,
        timestamp: str = None,
        quality_flag: str = "VALID",
        collection_method: str = None,
        instrument_id: str = None,
        detection_limit: float = None,
        uncertainty: float = None,
        pollutant_type: str = None,
        **kwargs
    ):
        """Initialize environmental measurement"""
        super().__init__(**kwargs)
        self.site_id = site_id
        self.parameter = parameter
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.now().isoformat()
        self.quality_flag = quality_flag
        self.collection_method = collection_method
        self.instrument_id = instrument_id
        self.detection_limit = detection_limit
        self.uncertainty = uncertainty
        self.pollutant_type = pollutant_type
    
    def exceeds_threshold(self, threshold: float) -> bool:
        """Check if measurement exceeds a threshold value"""
        return self.value > threshold
    
    def get_normalized_value(self, target_unit: str) -> float:
        """Get value normalized to a target unit (placeholder for unit conversion)"""
        # In a real implementation, this would have unit conversion logic
        if self.unit == target_unit:
            return self.value
        else:
            # Placeholder for conversion logic
            return self.value
    
    @property
    def is_valid(self) -> bool:
        """Check if measurement is valid"""
        return self.quality_flag == "VALID"


class AirQualityIndex(BaseModel):
    """
    Air Quality Index (AQI) calculation.
    Represents a calculated AQI value for a specific location and time.
    """
    
    def __init__(
        self,
        site_id: str,
        aqi_value: int,
        category: str,
        dominant_pollutant: str,
        timestamp: str = None,
        location: Dict[str, Any] = None,
        health_implications: str = None,
        sensitive_groups: str = None,
        forecast_next_day: Optional[int] = None,
        **kwargs
    ):
        """Initialize AQI calculation"""
        super().__init__(**kwargs)
        self.site_id = site_id
        self.aqi_value = aqi_value
        self.category = category
        self.dominant_pollutant = dominant_pollutant
        self.timestamp = timestamp or datetime.now().isoformat()
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.health_implications = health_implications
        self.sensitive_groups = sensitive_groups
        self.forecast_next_day = forecast_next_day
    
    @property
    def is_unhealthy(self) -> bool:
        """Check if AQI indicates unhealthy conditions"""
        return self.aqi_value > 100
    
    @property
    def is_hazardous(self) -> bool:
        """Check if AQI indicates hazardous conditions"""
        return self.aqi_value > 300


class WaterQualityMeasurement(EnvironmentalMeasurement):
    """
    Water quality measurement.
    Extends environmental measurement with water-specific attributes.
    """
    
    def __init__(
        self,
        water_body_type: str,
        water_body_name: str = None,
        depth: float = None,
        flow_rate: float = None,
        sampling_method: str = None,
        trophic_state: str = None,
        **kwargs
    ):
        """Initialize water quality measurement"""
        super().__init__(**kwargs)
        self.water_body_type = water_body_type
        self.water_body_name = water_body_name
        self.depth = depth
        self.flow_rate = flow_rate
        self.sampling_method = sampling_method
        self.trophic_state = trophic_state


class SoilQualityMeasurement(EnvironmentalMeasurement):
    """
    Soil quality measurement.
    Extends environmental measurement with soil-specific attributes.
    """
    
    def __init__(
        self,
        soil_type: str,
        depth: float = None,
        land_use: str = None,
        soil_moisture: float = None,
        soil_temperature: float = None,
        sampling_method: str = None,
        **kwargs
    ):
        """Initialize soil quality measurement"""
        super().__init__(**kwargs)
        self.soil_type = soil_type
        self.depth = depth
        self.land_use = land_use
        self.soil_moisture = soil_moisture
        self.soil_temperature = soil_temperature
        self.sampling_method = sampling_method


class EnvironmentalAlert(BaseModel):
    """
    Environmental alert for exceeded thresholds or hazardous conditions.
    """
    
    def __init__(
        self,
        site_id: str,
        parameter: str,
        value: float,
        threshold: float,
        severity: str,
        timestamp: str = None,
        location: Dict[str, Any] = None,
        status: str = "ACTIVE",
        message: str = None,
        recommended_actions: List[str] = None,
        affected_area: Dict[str, Any] = None,
        **kwargs
    ):
        """Initialize environmental alert"""
        super().__init__(**kwargs)
        self.site_id = site_id
        self.parameter = parameter
        self.value = value
        self.threshold = threshold
        self.severity = severity
        self.timestamp = timestamp or datetime.now().isoformat()
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.status = status
        self.message = message
        self.recommended_actions = recommended_actions or []
        self.affected_area = affected_area
    
    def close_alert(self, resolution_notes: str = None) -> None:
        """Mark alert as resolved"""
        self.status = "RESOLVED"
        self.resolution_notes = resolution_notes
        self.resolution_timestamp = datetime.now().isoformat()
    
    @property
    def exceedance_percentage(self) -> float:
        """Calculate percentage by which threshold is exceeded"""
        if self.threshold == 0:
            return float('inf')
        return ((self.value - self.threshold) / self.threshold) * 100