"""
Disaster model for FEMA implementation.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any


class DisasterType(Enum):
    """Classification of disasters by type."""
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    FLOOD = "flood"
    WILDFIRE = "wildfire"
    EARTHQUAKE = "earthquake"
    TSUNAMI = "tsunami"
    VOLCANIC_ERUPTION = "volcanic_eruption"
    WINTER_STORM = "winter_storm"
    DROUGHT = "drought"
    EXTREME_HEAT = "extreme_heat"
    LANDSLIDE = "landslide"
    PANDEMIC = "pandemic"
    CHEMICAL_SPILL = "chemical_spill"
    RADIOLOGICAL_INCIDENT = "radiological_incident"
    TERRORISM = "terrorism"
    CYBER_INCIDENT = "cyber_incident"
    DAM_FAILURE = "dam_failure"
    POWER_OUTAGE = "power_outage"


class DisasterCategory(Enum):
    """High-level categories of disasters."""
    NATURAL = "natural"
    TECHNOLOGICAL = "technological"
    HUMAN_CAUSED = "human_caused"
    BIOLOGICAL = "biological"


class DisasterPhase(Enum):
    """Phases of a disaster lifecycle."""
    POTENTIAL = "potential"  # Identified risk, not yet occurring
    IMMINENT = "imminent"    # About to occur (e.g., hurricane approaching)
    OCCURRING = "occurring"  # Currently taking place
    RESPONSE = "response"    # Immediate actions after disaster
    RECOVERY = "recovery"    # Longer term recovery efforts
    RESOLVED = "resolved"    # Disaster fully resolved


class SeverityLevel(Enum):
    """Severity levels for disasters."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"


@dataclass
class ImpactAssessment:
    """Assessment of disaster impacts across multiple dimensions."""
    casualties: Dict[str, int] = field(default_factory=lambda: {"fatalities": 0, "injuries": 0, "missing": 0})
    displaced_persons: int = 0
    structures_affected: Dict[str, int] = field(default_factory=lambda: {
        "destroyed": 0, "major_damage": 0, "minor_damage": 0, "affected": 0
    })
    infrastructure_damage: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    economic_impact: Dict[str, float] = field(default_factory=dict)
    environmental_impact: Dict[str, Any] = field(default_factory=dict)
    confidence_level: float = 0.5  # 0.0 to 1.0
    assessment_method: str = "preliminary"
    last_updated: datetime = field(default_factory=datetime.now)
    
    def total_human_impact(self) -> int:
        """Calculate total human impact (casualties + displaced)."""
        return sum(self.casualties.values()) + self.displaced_persons
    
    def total_structures_affected(self) -> int:
        """Calculate total number of affected structures."""
        return sum(self.structures_affected.values())
    
    def estimated_economic_loss(self) -> float:
        """Calculate total estimated economic loss in USD."""
        return sum(self.economic_impact.values())


@dataclass
class ResourceAllocation:
    """Resources allocated to a disaster response."""
    personnel: Dict[str, int] = field(default_factory=dict)
    equipment: Dict[str, int] = field(default_factory=dict)
    supplies: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    facilities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    funding: Dict[str, float] = field(default_factory=dict)
    
    def total_personnel(self) -> int:
        """Calculate total personnel allocated."""
        return sum(self.personnel.values())
    
    def total_funding(self) -> float:
        """Calculate total funding allocated in USD."""
        return sum(self.funding.values())


@dataclass
class DeclarationStatus:
    """Status of disaster declarations."""
    local_declaration: Optional[Dict[str, Any]] = None
    state_declaration: Optional[Dict[str, Any]] = None
    federal_declaration: Optional[Dict[str, Any]] = None
    
    def has_federal_declaration(self) -> bool:
        """Check if a federal disaster declaration is in place."""
        return self.federal_declaration is not None
    
    def declaration_level(self) -> str:
        """Get the highest level of declaration in place."""
        if self.federal_declaration:
            return "federal"
        elif self.state_declaration:
            return "state"
        elif self.local_declaration:
            return "local"
        else:
            return "none"


@dataclass
class Disaster:
    """Comprehensive disaster model for emergency management."""
    disaster_id: str
    name: str
    type: DisasterType
    category: DisasterCategory
    phase: DisasterPhase
    severity: SeverityLevel
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Dict[str, Any] = field(default_factory=dict)
    affected_area: Dict[str, Any] = field(default_factory=dict)
    population_affected: Optional[int] = None
    impact_assessment: ImpactAssessment = field(default_factory=ImpactAssessment)
    resource_allocation: ResourceAllocation = field(default_factory=ResourceAllocation)
    declaration_status: DeclarationStatus = field(default_factory=DeclarationStatus)
    hazard_data: Dict[str, Any] = field(default_factory=dict)
    related_disasters: List[str] = field(default_factory=list)
    response_actions: List[Dict[str, Any]] = field(default_factory=list)
    updates: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def is_active(self) -> bool:
        """Check if the disaster is currently active."""
        return self.phase in [DisasterPhase.IMMINENT, DisasterPhase.OCCURRING, DisasterPhase.RESPONSE] 
    
    def get_duration_hours(self) -> Optional[float]:
        """Get the duration of the disaster in hours, if it has ended."""
        if not self.end_time or self.phase != DisasterPhase.RESOLVED:
            return None
            
        duration = self.end_time - self.start_time
        return duration.total_seconds() / 3600
    
    def calculate_impact_index(self) -> float:
        """
        Calculate a comprehensive impact index for the disaster.
        
        Returns:
            Float from 0-10 representing overall impact (higher is more severe)
        """
        # Base impact on severity level
        base_impact = {
            SeverityLevel.MINOR: 2.0,
            SeverityLevel.MODERATE: 4.0,
            SeverityLevel.MAJOR: 7.0,
            SeverityLevel.CATASTROPHIC: 10.0
        }[self.severity]
        
        # Create component scores based on various impacts
        human_impact_score = 0.0
        if self.impact_assessment.total_human_impact() > 0:
            # Logarithmic scale for human impact
            human_impact_score = min(4.0, 0.5 * (1 + 
                                          (self.impact_assessment.casualties.get("fatalities", 0) * 2) + 
                                          (self.impact_assessment.casualties.get("injuries", 0) / 10) + 
                                          (self.impact_assessment.displaced_persons / 1000)))
            
        property_impact_score = 0.0
        if self.impact_assessment.total_structures_affected() > 0:
            # Calculate based on destroyed and damaged structures
            destroyed = self.impact_assessment.structures_affected.get("destroyed", 0)
            major_damage = self.impact_assessment.structures_affected.get("major_damage", 0)
            minor_damage = self.impact_assessment.structures_affected.get("minor_damage", 0)
            
            property_impact_score = min(3.0, (destroyed * 0.01) + 
                                        (major_damage * 0.001) + 
                                        (minor_damage * 0.0001))
            
        economic_impact_score = 0.0
        economic_loss = self.impact_assessment.estimated_economic_loss()
        if economic_loss > 0:
            # Logarithmic scale for economic impact, capped at 3.0
            economic_impact_score = min(3.0, economic_loss / 1_000_000_000)  # Billions of dollars
            
        # Calculate final impact index, weighted by confidence
        confidence = self.impact_assessment.confidence_level
        impact_components = [base_impact, human_impact_score, property_impact_score, economic_impact_score]
        weighted_impact = sum(impact_components) / len(impact_components)
        
        # Apply confidence adjustment - lower confidence pulls toward median value of 5.0
        confidence_adjusted_impact = (weighted_impact * confidence) + (5.0 * (1 - confidence))
        
        return min(10.0, max(0.0, confidence_adjusted_impact))
    
    def add_update(self, update_type: str, details: Dict[str, Any], source: str) -> None:
        """
        Add an update to the disaster record.
        
        Args:
            update_type: Type of update (e.g., "situation", "impact", "response")
            details: Details of the update
            source: Source of the update information
        """
        self.updates.append({
            "timestamp": datetime.now(),
            "type": update_type,
            "details": details,
            "source": source
        })
        self.last_updated = datetime.now()
    
    def update_phase(self, new_phase: DisasterPhase, reason: str) -> None:
        """
        Update the disaster phase.
        
        Args:
            new_phase: New disaster phase
            reason: Reason for the phase change
        """
        old_phase = self.phase
        self.phase = new_phase
        
        # Add to updates
        self.add_update(
            update_type="phase_change",
            details={
                "old_phase": old_phase.value,
                "new_phase": new_phase.value,
                "reason": reason
            },
            source="system"
        )
        
        # If moving to resolved, set end time
        if new_phase == DisasterPhase.RESOLVED and not self.end_time:
            self.end_time = datetime.now()
    
    def update_impact_assessment(self, new_assessment: Dict[str, Any], 
                                confidence: float, method: str) -> None:
        """
        Update the impact assessment with new data.
        
        Args:
            new_assessment: New impact assessment data
            confidence: Confidence level in the assessment
            method: Assessment method used
        """
        # Update casualties if provided
        if "casualties" in new_assessment:
            for category, count in new_assessment["casualties"].items():
                if category in self.impact_assessment.casualties:
                    self.impact_assessment.casualties[category] = count
        
        # Update displaced persons if provided
        if "displaced_persons" in new_assessment:
            self.impact_assessment.displaced_persons = new_assessment["displaced_persons"]
        
        # Update structures affected if provided
        if "structures_affected" in new_assessment:
            for damage_type, count in new_assessment["structures_affected"].items():
                if damage_type in self.impact_assessment.structures_affected:
                    self.impact_assessment.structures_affected[damage_type] = count
        
        # Update infrastructure damage if provided
        if "infrastructure_damage" in new_assessment:
            self.impact_assessment.infrastructure_damage.update(
                new_assessment["infrastructure_damage"]
            )
        
        # Update economic impact if provided
        if "economic_impact" in new_assessment:
            self.impact_assessment.economic_impact.update(
                new_assessment["economic_impact"]
            )
        
        # Update environmental impact if provided
        if "environmental_impact" in new_assessment:
            self.impact_assessment.environmental_impact.update(
                new_assessment["environmental_impact"]
            )
        
        # Update assessment metadata
        self.impact_assessment.confidence_level = confidence
        self.impact_assessment.assessment_method = method
        self.impact_assessment.last_updated = datetime.now()
        
        # Add update record
        self.add_update(
            update_type="impact_assessment",
            details={
                "new_assessment": new_assessment,
                "confidence": confidence,
                "method": method
            },
            source="system"
        )
        
        # Re-evaluate severity based on new impact data
        self._update_severity_from_impact()
    
    def _update_severity_from_impact(self) -> None:
        """Update the disaster severity level based on impact assessment."""
        impact_index = self.calculate_impact_index()
        
        # Determine severity based on impact index
        if impact_index >= 8.0:
            new_severity = SeverityLevel.CATASTROPHIC
        elif impact_index >= 5.0:
            new_severity = SeverityLevel.MAJOR
        elif impact_index >= 3.0:
            new_severity = SeverityLevel.MODERATE
        else:
            new_severity = SeverityLevel.MINOR
            
        # Update if changed
        if new_severity != self.severity:
            old_severity = self.severity
            self.severity = new_severity
            
            # Add to updates
            self.add_update(
                update_type="severity_change",
                details={
                    "old_severity": old_severity.value,
                    "new_severity": new_severity.value,
                    "impact_index": impact_index,
                    "reason": "Updated based on new impact assessment"
                },
                source="system"
            )
    
    def add_response_action(self, action_type: str, details: Dict[str, Any], 
                           status: str, assigned_to: str) -> None:
        """
        Add a response action to the disaster.
        
        Args:
            action_type: Type of response action
            details: Details of the action
            status: Status of the action (planned, in-progress, completed)
            assigned_to: Entity responsible for the action
        """
        self.response_actions.append({
            "id": f"RA-{len(self.response_actions) + 1}",
            "type": action_type,
            "details": details,
            "status": status,
            "assigned_to": assigned_to,
            "created": datetime.now(),
            "last_updated": datetime.now(),
            "updates": []
        })
        
        # Add update record
        self.add_update(
            update_type="response_action_added",
            details={
                "action_type": action_type,
                "status": status,
                "assigned_to": assigned_to
            },
            source="system"
        )
    
    def update_declaration_status(self, level: str, 
                                 declaration_data: Dict[str, Any]) -> None:
        """
        Update the disaster declaration status.
        
        Args:
            level: Declaration level (local, state, federal)
            declaration_data: Declaration details
        """
        if level == "local":
            self.declaration_status.local_declaration = declaration_data
        elif level == "state":
            self.declaration_status.state_declaration = declaration_data
        elif level == "federal":
            self.declaration_status.federal_declaration = declaration_data
        
        # Add update record
        self.add_update(
            update_type="declaration_status",
            details={
                "level": level,
                "declaration": declaration_data
            },
            source="system"
        )