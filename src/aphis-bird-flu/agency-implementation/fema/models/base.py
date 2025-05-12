"""
Base models for the FEMA Agency Implementation.
Defines common functionality and enumerations for FEMA-specific domain models.
"""
from enum import Enum, auto
from typing import Optional, Dict, Any, List


class DisasterType(Enum):
    """Types of disasters that FEMA responds to"""
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    FLOOD = "flood"
    WILDFIRE = "wildfire"
    EARTHQUAKE = "earthquake"
    WINTER_STORM = "winter_storm"
    DROUGHT = "drought"
    LANDSLIDE = "landslide"
    VOLCANIC_ACTIVITY = "volcanic_activity"
    TSUNAMI = "tsunami"
    BIOLOGICAL_HAZARD = "biological_hazard"
    CHEMICAL_HAZARD = "chemical_hazard"
    RADIOLOGICAL_HAZARD = "radiological_hazard"
    CYBER_INCIDENT = "cyber_incident"
    INDUSTRIAL_ACCIDENT = "industrial_accident"
    OTHER = "other"


class DisasterSeverity(Enum):
    """Severity levels for disasters"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"


class RecoveryPhase(Enum):
    """Phases of disaster recovery"""
    INITIAL_RESPONSE = "initial_response"
    SHORT_TERM_RECOVERY = "short_term_recovery"
    INTERMEDIATE_RECOVERY = "intermediate_recovery"
    LONG_TERM_RECOVERY = "long_term_recovery"
    COMPLETED = "completed"


class ResourceType(Enum):
    """Types of resources that can be deployed"""
    PERSONNEL = "personnel"
    SHELTER = "shelter"
    FOOD_WATER = "food_water"
    MEDICAL = "medical"
    TRANSPORTATION = "transportation"
    COMMUNICATION = "communication"
    POWER = "power"
    SEARCH_RESCUE = "search_rescue"
    SECURITY = "security"
    HEAVY_EQUIPMENT = "heavy_equipment"
    TECHNICAL_SPECIALIST = "technical_specialist"
    FINANCIAL_AID = "financial_aid"
    OTHER = "other"


class ResourceStatus(Enum):
    """Status of deployed resources"""
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    DEPLOYED = "deployed"
    IN_TRANSIT = "in_transit"
    RETURNING = "returning"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class AlertLevel(Enum):
    """Alert levels for disaster risk monitoring"""
    NORMAL = "normal"
    ADVISORY = "advisory"
    WATCH = "watch"
    WARNING = "warning"
    EMERGENCY = "emergency"


class MeasurementUnit(Enum):
    """Units of measurement for various parameters"""
    # Distance
    METERS = "m"
    KILOMETERS = "km"
    FEET = "ft"
    MILES = "mi"
    
    # Area
    SQUARE_METERS = "m²"
    SQUARE_KILOMETERS = "km²"
    SQUARE_FEET = "ft²"
    SQUARE_MILES = "mi²"
    ACRES = "acres"
    HECTARES = "ha"
    
    # Volume
    CUBIC_METERS = "m³"
    LITERS = "L"
    GALLONS = "gal"
    
    # Speed
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    MILES_PER_HOUR = "mph"
    KNOTS = "knots"
    
    # Temperature
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    
    # Precipitation
    MILLIMETERS = "mm"
    INCHES = "in"
    
    # Wind
    BEAUFORT = "beaufort"
    
    # Earthquake
    RICHTER = "richter"
    MOMENT_MAGNITUDE = "Mw"
    
    # Time
    SECONDS = "s"
    MINUTES = "min"
    HOURS = "hr"
    DAYS = "days"
    
    # Percentage
    PERCENT = "%"
    
    # Count
    COUNT = "count"
    
    # Currency
    USD = "USD"
    
    # Other
    CATEGORY = "category"
    INDEX = "index"


class DataSource(Enum):
    """Sources of data for disaster risk monitoring"""
    NOAA = "noaa"
    USGS = "usgs"
    EPA = "epa"
    NASA = "nasa"
    FEMA = "fema"
    STATE_AGENCY = "state_agency"
    LOCAL_GOVERNMENT = "local_government"
    NGO = "ngo"
    PRIVATE_SECTOR = "private_sector"
    SOCIAL_MEDIA = "social_media"
    CROWDSOURCED = "crowdsourced"
    IOT_SENSOR = "iot_sensor"
    SATELLITE = "satellite"
    DRONE = "drone"
    FIELD_OBSERVER = "field_observer"
    OTHER = "other"