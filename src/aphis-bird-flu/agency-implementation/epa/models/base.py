"""
Base models for the EPA Agency Implementation.
Extends foundation models with EPA-specific functionality.
"""
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

from agency_implementation.foundation.base_models.base import BaseModel, Repository, GeoLocation


class MeasurementUnit(Enum):
    """Units for environmental measurements"""
    
    # Concentration units
    PPM = "parts per million"
    PPB = "parts per billion"
    UG_M3 = "micrograms per cubic meter"
    MG_L = "milligrams per liter"
    
    # Temperature units
    CELSIUS = "degrees Celsius"
    FAHRENHEIT = "degrees Fahrenheit"
    
    # Area units
    SQUARE_KM = "square kilometers"
    HECTARES = "hectares"
    ACRES = "acres"
    
    # Volume units
    CUBIC_M = "cubic meters"
    LITERS = "liters"
    GALLONS = "gallons"
    
    # Flow units
    M3_SEC = "cubic meters per second"
    L_MIN = "liters per minute"
    
    # Other units
    PERCENT = "percent"
    PH = "pH units"
    AQI = "air quality index"
    DECIBELS = "decibels"


class PollutantType(Enum):
    """Types of environmental pollutants"""
    
    # Air pollutants
    PM25 = "PM2.5"
    PM10 = "PM10"
    OZONE = "Ozone"
    CO = "Carbon Monoxide"
    NO2 = "Nitrogen Dioxide"
    SO2 = "Sulfur Dioxide"
    LEAD = "Lead"
    
    # Water pollutants
    NITRATES = "Nitrates"
    PHOSPHATES = "Phosphates"
    DISSOLVED_OXYGEN = "Dissolved Oxygen"
    HEAVY_METALS = "Heavy Metals"
    E_COLI = "E. coli"
    PESTICIDES = "Pesticides"
    
    # Soil pollutants
    PETROLEUM_HYDROCARBONS = "Petroleum Hydrocarbons"
    SOLVENTS = "Solvents"
    HEAVY_METALS_SOIL = "Heavy Metals (Soil)"
    PERSISTENT_ORGANICS = "Persistent Organic Pollutants"
    
    # Other pollutants
    RADIATION = "Radiation"
    NOISE = "Noise"
    LIGHT = "Light Pollution"
    HEAT = "Heat"
    
    # Generic
    OTHER = "Other"


class ComplianceStatus(Enum):
    """Status of compliance with environmental regulations"""
    
    COMPLIANT = "Compliant"
    MINOR_VIOLATION = "Minor Violation"
    SIGNIFICANT_VIOLATION = "Significant Violation"
    SEVERE_VIOLATION = "Severe Violation"
    UNDER_INVESTIGATION = "Under Investigation"
    PENDING_REVIEW = "Pending Review"
    EXEMPTED = "Exempted"
    NOT_APPLICABLE = "Not Applicable"


class RegulatoryFramework(Enum):
    """EPA regulatory frameworks"""
    
    CLEAN_AIR_ACT = "Clean Air Act"
    CLEAN_WATER_ACT = "Clean Water Act"
    SAFE_DRINKING_WATER_ACT = "Safe Drinking Water Act"
    RESOURCE_CONSERVATION_RECOVERY_ACT = "Resource Conservation and Recovery Act"
    CERCLA = "Comprehensive Environmental Response, Compensation, and Liability Act"
    TSCA = "Toxic Substances Control Act"
    FIFRA = "Federal Insecticide, Fungicide, and Rodenticide Act"
    NEPA = "National Environmental Policy Act"
    OTHER = "Other"


class EPARepository(Repository):
    """Base repository for EPA models with additional functionality"""
    
    def find_by_region(self, region: str) -> List[Any]:
        """Find entities by EPA region"""
        raise NotImplementedError
    
    def find_by_pollutant_type(self, pollutant_type: PollutantType) -> List[Any]:
        """Find entities by pollutant type"""
        raise NotImplementedError
    
    def find_by_compliance_status(self, status: ComplianceStatus) -> List[Any]:
        """Find entities by compliance status"""
        raise NotImplementedError
    
    def find_by_regulatory_framework(self, framework: RegulatoryFramework) -> List[Any]:
        """Find entities by regulatory framework"""
        raise NotImplementedError
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime, date_field: str) -> List[Any]:
        """Find entities within a date range"""
        raise NotImplementedError
    
    def find_by_geographic_area(self, min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> List[Any]:
        """Find entities within a geographic bounding box"""
        raise NotImplementedError
    
    def find_exceeded_thresholds(self, threshold_values: Dict[str, float]) -> List[Any]:
        """Find entities exceeding specified threshold values"""
        raise NotImplementedError