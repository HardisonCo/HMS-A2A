"""
Pollutant model for EPA implementation.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union


class PollutantCategory(Enum):
    """Classification of pollutants by type."""
    CRITERIA_AIR_POLLUTANT = "criteria_air_pollutant"
    HAZARDOUS_AIR_POLLUTANT = "hazardous_air_pollutant"
    GREENHOUSE_GAS = "greenhouse_gas"
    WATER_CONTAMINANT = "water_contaminant"
    SOIL_CONTAMINANT = "soil_contaminant"
    RADIATION = "radiation"
    NOISE = "noise"
    LIGHT = "light"
    THERMAL = "thermal"


class PollutantSource(Enum):
    """Sources of pollution."""
    INDUSTRIAL = "industrial"
    TRANSPORTATION = "transportation"
    AGRICULTURAL = "agricultural"
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    NATURAL = "natural"
    WASTE_MANAGEMENT = "waste_management"
    ENERGY_PRODUCTION = "energy_production"


class HealthRiskLevel(Enum):
    """Health risk levels for pollutants."""
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    SEVERE = "severe"


@dataclass
class RegulatoryStandard:
    """Regulatory standards for a pollutant."""
    standard_id: str
    standard_name: str
    issuing_authority: str  # EPA, WHO, State, etc.
    media: str  # air, water, soil
    value: float
    unit: str
    time_period: str  # 1-hour, 8-hour, annual, etc.
    effective_date: datetime
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    health_based: bool = True
    notes: str = ""


@dataclass
class HealthEffect:
    """Health effects associated with a pollutant."""
    effect_id: str
    name: str
    affected_systems: List[str]  # respiratory, cardiovascular, etc.
    severity: str
    exposure_route: str  # inhalation, ingestion, dermal
    exposure_duration: str  # acute, chronic
    population_sensitivity: Dict[str, float]  # e.g., {"children": 1.5, "elderly": 1.2}
    description: str
    evidence_level: str  # conclusive, probable, possible
    references: List[str] = field(default_factory=list)


@dataclass
class Pollutant:
    """Comprehensive pollutant model for monitoring and regulation."""
    pollutant_id: str
    name: str
    chemical_name: Optional[str] = None
    cas_number: Optional[str] = None  # Chemical Abstracts Service Registry Number
    formula: Optional[str] = None
    category: PollutantCategory
    common_sources: List[PollutantSource]
    measurement_units: List[str]
    detection_methods: List[str]
    regulatory_standards: List[RegulatoryStandard] = field(default_factory=list)
    health_effects: List[HealthEffect] = field(default_factory=list)
    environmental_effects: List[str] = field(default_factory=list)
    persistence: Optional[str] = None  # persistence in environment
    bioaccumulation: bool = False
    control_technologies: List[str] = field(default_factory=list)
    description: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_current_standard(self, media: str, authority: str = "EPA") -> Optional[RegulatoryStandard]:
        """
        Get the current applicable regulatory standard for this pollutant.
        
        Args:
            media: Environmental media (air, water, soil)
            authority: Regulatory authority (default: EPA)
            
        Returns:
            Current applicable standard or None if not found
        """
        applicable_standards = [
            std for std in self.regulatory_standards
            if std.media == media and std.issuing_authority == authority
        ]
        
        if not applicable_standards:
            return None
            
        # Return the most recently effective standard
        return max(applicable_standards, key=lambda std: std.effective_date)
    
    def calculate_health_risk(self, concentration: float, exposure_duration: str, 
                             sensitive_population: Optional[str] = None) -> HealthRiskLevel:
        """
        Calculate health risk level based on concentration and exposure.
        
        Args:
            concentration: Pollutant concentration in standard units
            exposure_duration: Duration of exposure ("acute" or "chronic")
            sensitive_population: Specific sensitive population group (if applicable)
            
        Returns:
            Health risk level enumeration
        """
        # This would implement a risk assessment algorithm based on:
        # - Comparison to regulatory standards
        # - Exposure duration
        # - Population sensitivity factors
        
        # Simplified example implementation:
        applicable_standard = self.get_current_standard("air")
        
        if not applicable_standard:
            return HealthRiskLevel.MODERATE  # Default if no standard exists
        
        # Calculate risk based on comparison to standard
        ratio = concentration / applicable_standard.value
        
        # Adjust for sensitive populations if specified
        if sensitive_population and any(effect.population_sensitivity.get(sensitive_population) 
                                      for effect in self.health_effects):
            # Find maximum sensitivity factor for this population
            sensitivity_factor = max(
                effect.population_sensitivity.get(sensitive_population, 1.0)
                for effect in self.health_effects
            )
            ratio *= sensitivity_factor
        
        # Determine risk level based on ratio to standard
        if ratio <= 0.5:
            return HealthRiskLevel.NEGLIGIBLE
        elif ratio <= 0.75:
            return HealthRiskLevel.LOW
        elif ratio <= 1.0:
            return HealthRiskLevel.MODERATE
        elif ratio <= 1.5:
            return HealthRiskLevel.HIGH
        elif ratio <= 2.0:
            return HealthRiskLevel.VERY_HIGH
        else:
            return HealthRiskLevel.SEVERE


@dataclass
class PollutionEvent:
    """Record of a pollution event or exceedance."""
    event_id: str
    pollutant: Pollutant
    location: Dict[str, Union[str, float]]
    start_time: datetime
    end_time: Optional[datetime] = None
    peak_concentration: float
    peak_time: Optional[datetime] = None
    average_concentration: float
    measurement_unit: str
    source: Optional[PollutantSource] = None
    source_details: Optional[str] = None
    status: str = "active"  # active, resolved, monitoring
    health_risk_level: HealthRiskLevel = HealthRiskLevel.MODERATE
    affected_area_km2: Optional[float] = None
    population_affected: Optional[int] = None
    weather_conditions: Dict[str, Any] = field(default_factory=dict)
    response_actions: List[str] = field(default_factory=list)
    notes: str = ""
    
    def is_active(self) -> bool:
        """Check if the pollution event is currently active."""
        return self.end_time is None and self.status in ["active", "monitoring"]
    
    def get_duration_hours(self) -> Optional[float]:
        """Get the duration of the event in hours, if it has ended."""
        if not self.end_time:
            return None
            
        duration = self.end_time - self.start_time
        return duration.total_seconds() / 3600
    
    def calculate_severity_index(self) -> float:
        """
        Calculate a severity index for the pollution event based on multiple factors.
        
        Returns:
            Float from 0-10 representing severity (higher is more severe)
        """
        # Base severity on health risk level
        base_severity = {
            HealthRiskLevel.NEGLIGIBLE: 1.0,
            HealthRiskLevel.LOW: 2.0,
            HealthRiskLevel.MODERATE: 4.0,
            HealthRiskLevel.HIGH: 6.0,
            HealthRiskLevel.VERY_HIGH: 8.0,
            HealthRiskLevel.SEVERE: 10.0
        }[self.health_risk_level]
        
        # Get the applicable standard
        standard = self.pollutant.get_current_standard("air")
        
        # Adjust for exceedance ratio if standard exists
        if standard:
            exceedance_ratio = self.peak_concentration / standard.value
            base_severity *= min(2.0, exceedance_ratio)  # Cap at 2x multiplier
        
        # Adjust for affected area and population if available
        area_factor = 1.0
        if self.affected_area_km2:
            # Normalize to 100 km² (smaller areas get less weight, larger more)
            area_factor = min(2.0, self.affected_area_km2 / 100.0)
        
        population_factor = 1.0
        if self.population_affected:
            # Normalize to 100,000 people
            population_factor = min(2.0, self.population_affected / 100000.0)
        
        # Calculate final severity index
        severity_index = base_severity * (area_factor * 0.3 + population_factor * 0.7)
        
        # Duration factor if event has ended
        if self.end_time:
            duration_hours = self.get_duration_hours()
            # Events lasting longer than 24 hours are considered more severe
            duration_factor = min(1.5, duration_hours / 24.0)
            severity_index *= duration_factor
            
        return min(10.0, severity_index)  # Cap at 10