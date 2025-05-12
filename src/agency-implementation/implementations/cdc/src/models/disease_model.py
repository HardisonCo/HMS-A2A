"""
Disease model for CDC implementation.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union


class DiseaseCategory(Enum):
    """Classification of diseases by type."""
    INFECTIOUS = "infectious"
    CHRONIC = "chronic"
    ZOONOTIC = "zoonotic"
    VECTOR_BORNE = "vector_borne"
    FOODBORNE = "foodborne"
    RESPIRATORY = "respiratory"


class TransmissionType(Enum):
    """Methods of disease transmission."""
    AIRBORNE = "airborne"
    DIRECT_CONTACT = "direct_contact"
    FECAL_ORAL = "fecal_oral"
    FOODBORNE = "foodborne"
    VECTOR_BORNE = "vector_borne"
    WATERBORNE = "waterborne"
    SEXUAL = "sexual"
    VERTICAL = "vertical"  # Mother to child
    BLOOD_BORNE = "blood_borne"


class SeverityLevel(Enum):
    """Levels of disease severity for public health response."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class GeneticSequence:
    """Representation of a pathogen's genetic sequence."""
    sequence_id: str
    raw_sequence: str
    sequencing_method: str
    collection_date: datetime
    source_lab: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class Variant:
    """Variant of a disease with its genetic and epidemiological characteristics."""
    variant_id: str
    name: str
    first_detected: datetime
    genetic_markers: List[str]
    transmissibility_modifier: float = 1.0  # 1.0 is baseline
    severity_modifier: float = 1.0  # 1.0 is baseline
    immune_escape_factor: float = 0.0  # 0.0 means no immune escape
    sequences: List[GeneticSequence] = field(default_factory=list)


@dataclass
class Disease:
    """Comprehensive disease model for surveillance and response."""
    disease_id: str
    name: str
    scientific_name: str
    category: DiseaseCategory
    transmission_types: List[TransmissionType]
    incubation_period_days: Dict[str, float]  # min, max, mean
    infectious_period_days: Dict[str, float]  # min, max, mean
    r0_estimate: float  # basic reproduction number
    case_fatality_rate: float
    severity_level: SeverityLevel
    reportable: bool  # whether it's a nationally notifiable disease
    description: str
    symptoms: List[str]
    preventive_measures: List[str]
    treatments: List[str]
    variants: List[Variant] = field(default_factory=list)
    emergence_date: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)

    def calculate_transmission_risk(self, population_density: float, 
                                    vaccination_rate: float = 0.0,
                                    mobility_factor: float = 1.0) -> float:
        """
        Calculate transmission risk based on disease characteristics and population factors.
        
        Args:
            population_density: Population density in persons per square km
            vaccination_rate: Proportion of population vaccinated (0-1)
            mobility_factor: Relative mobility level (1.0 is normal)
            
        Returns:
            Float representing relative transmission risk (higher is greater risk)
        """
        # Basic transmission risk based on R0
        base_risk = self.r0_estimate * mobility_factor
        
        # Adjust for population density
        density_factor = min(1.0, population_density / 1000)  # Normalize
        
        # Adjust for vaccination, accounting for current variants
        immune_escape = max([v.immune_escape_factor for v in self.variants]) if self.variants else 0.0
        effective_vaccination = vaccination_rate * (1.0 - immune_escape)
        
        # Calculate final risk
        transmission_risk = base_risk * (1 + density_factor) * (1 - (0.8 * effective_vaccination))
        
        return max(0.0, transmission_risk)


@dataclass
class OutbreakEvent:
    """Record of a disease outbreak event."""
    event_id: str
    disease: Disease
    variant: Optional[Variant]
    location: Dict[str, Union[str, float]]  # Flexible location representation
    start_date: datetime
    end_date: Optional[datetime]
    case_count: int
    death_count: int
    hospitalization_count: int
    status: str  # active, contained, monitoring, resolved
    transmission_setting: Optional[str]  # e.g., "healthcare", "school", "community"
    response_measures: List[str]
    data_sources: List[str]
    confidence_level: float  # 0-1, indicating confidence in the data
    notes: str = ""
    
    def is_active(self) -> bool:
        """Check if the outbreak is currently active."""
        return self.end_date is None and self.status in ["active", "monitoring"]
    
    def calculate_severity_index(self) -> float:
        """
        Calculate a severity index for the outbreak based on multiple factors.
        
        Returns:
            Float from 0-10 representing severity (higher is more severe)
        """
        if self.case_count == 0:
            return 0.0
            
        # Calculate key metrics
        case_fatality = self.death_count / self.case_count if self.case_count > 0 else 0
        hospitalization_rate = self.hospitalization_count / self.case_count if self.case_count > 0 else 0
        
        # Basic severity based on the disease's inherent severity
        base_severity = {
            SeverityLevel.LOW: 2.0,
            SeverityLevel.MODERATE: 4.0,
            SeverityLevel.HIGH: 6.0,
            SeverityLevel.SEVERE: 8.0,
            SeverityLevel.CRITICAL: 10.0
        }[self.disease.severity_level]
        
        # Adjust for outbreak-specific factors
        severity_index = base_severity
        severity_index += case_fatality * 10  # Add up to 10 points for 100% fatality
        severity_index += hospitalization_rate * 5  # Add up to 5 points for 100% hospitalization
        
        # Duration factor
        if self.end_date and self.start_date:
            duration_days = (self.end_date - self.start_date).days
            duration_factor = min(1.0, duration_days / 30)  # Normalize to 30 days
            severity_index *= (1.0 + (duration_factor * 0.5))  # Up to 50% increase for duration
            
        return min(10.0, severity_index)  # Cap at 10