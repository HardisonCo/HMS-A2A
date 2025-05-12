"""
Recovery models for FEMA implementation.
Defines domain models for recovery progress tracking and assessment.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from agency_implementation.foundation.base_models.base import BaseModel, GeoLocation, Address
from agency_implementation.fema.models.base import RecoveryPhase


class RecoveryProject(BaseModel):
    """
    Recovery project.
    Represents a specific recovery project or initiative after a disaster.
    """
    
    def __init__(
        self,
        project_name: str,
        event_id: str,
        project_type: str,
        location: Dict[str, Any],
        description: str = None,
        start_date: str = None,
        target_completion_date: str = None,
        actual_completion_date: str = None,
        status: str = "PLANNING",
        phase: str = None,
        allocated_budget: float = None,
        funds_disbursed: float = None,
        responsible_agency: str = None,
        primary_contact: Dict[str, Any] = None,
        beneficiaries: int = None,
        success_metrics: Dict[str, Any] = None,
        progress_updates: List[Dict[str, Any]] = None,
        project_attachments: List[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize recovery project"""
        super().__init__(**kwargs)
        self.project_name = project_name
        self.event_id = event_id
        self.project_type = project_type
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.description = description
        self.start_date = start_date
        self.target_completion_date = target_completion_date
        self.actual_completion_date = actual_completion_date
        self.status = status
        self.phase = phase or RecoveryPhase.INITIAL_RESPONSE.value
        self.allocated_budget = allocated_budget
        self.funds_disbursed = funds_disbursed or 0.0
        self.responsible_agency = responsible_agency
        self.primary_contact = primary_contact
        self.beneficiaries = beneficiaries
        self.success_metrics = success_metrics or {}
        self.progress_updates = progress_updates or []
        self.project_attachments = project_attachments or []
    
    @property
    def percent_complete(self) -> float:
        """Calculate percentage of project completion"""
        # If project is completed, return 100%
        if self.status == "COMPLETED" or self.actual_completion_date:
            return 100.0
            
        # If there are progress updates with percentages, use the latest one
        if self.progress_updates:
            latest_update = max(self.progress_updates, key=lambda x: x.get('timestamp', ''))
            if 'percent_complete' in latest_update:
                return latest_update['percent_complete']
                
        # Default values based on status
        status_percent = {
            "PLANNING": 5.0,
            "PENDING_APPROVAL": 10.0,
            "APPROVED": 15.0,
            "FUNDED": 20.0,
            "IN_PROGRESS": 50.0,
            "UNDER_REVIEW": 85.0,
            "ON_HOLD": None,  # Don't calculate for on-hold
            "CANCELLED": None  # Don't calculate for cancelled
        }
        
        return status_percent.get(self.status, 0.0)
    
    @property
    def budget_utilization(self) -> Optional[float]:
        """Calculate percentage of budget utilized"""
        if not self.allocated_budget or self.allocated_budget == 0:
            return None
            
        if not self.funds_disbursed:
            return 0.0
            
        return (self.funds_disbursed / self.allocated_budget) * 100
    
    def add_progress_update(self, update: Dict[str, Any]) -> None:
        """Add a progress update to the project"""
        if not self.progress_updates:
            self.progress_updates = []
            
        if 'timestamp' not in update:
            update['timestamp'] = datetime.now().isoformat()
            
        self.progress_updates.append(update)
        self.updated_at = datetime.now().isoformat()
    
    def update_status(self, new_status: str, notes: str = None) -> None:
        """Update project status"""
        old_status = self.status
        self.status = new_status
        
        # If completing project, set completion date
        if new_status == "COMPLETED" and not self.actual_completion_date:
            self.actual_completion_date = datetime.now().isoformat()
            
        # Add status change to progress updates
        update = {
            'type': 'STATUS_CHANGE',
            'timestamp': datetime.now().isoformat(),
            'old_status': old_status,
            'new_status': new_status
        }
        
        if notes:
            update['notes'] = notes
            
        self.add_progress_update(update)
    
    def update_phase(self, new_phase: str, notes: str = None) -> None:
        """Update recovery phase"""
        old_phase = self.phase
        self.phase = new_phase
        
        # Add phase change to progress updates
        update = {
            'type': 'PHASE_CHANGE',
            'timestamp': datetime.now().isoformat(),
            'old_phase': old_phase,
            'new_phase': new_phase
        }
        
        if notes:
            update['notes'] = notes
            
        self.add_progress_update(update)


class DamageAssessment(BaseModel):
    """
    Damage assessment for a disaster-affected area.
    """
    
    def __init__(
        self,
        event_id: str,
        assessment_area: Dict[str, Any],
        assessment_type: str,
        damage_level: str,
        assessment_date: str = None,
        completed_by: str = None,
        methodology: str = None,
        infrastructure_damage: Dict[str, Any] = None,
        housing_damage: Dict[str, Any] = None,
        economic_impact: Dict[str, Any] = None,
        environmental_impact: Dict[str, Any] = None,
        affected_population: int = None,
        comments: str = None,
        confidence_level: str = None,
        attachments: List[Dict[str, Any]] = None,
        status: str = "DRAFT",
        **kwargs
    ):
        """Initialize damage assessment"""
        super().__init__(**kwargs)
        self.event_id = event_id
        self.assessment_area = assessment_area  # GeoJSON polygon or multipolygon
        self.assessment_type = assessment_type
        self.damage_level = damage_level
        self.assessment_date = assessment_date or datetime.now().isoformat()
        self.completed_by = completed_by
        self.methodology = methodology
        self.infrastructure_damage = infrastructure_damage or {}
        self.housing_damage = housing_damage or {}
        self.economic_impact = economic_impact or {}
        self.environmental_impact = environmental_impact or {}
        self.affected_population = affected_population
        self.comments = comments
        self.confidence_level = confidence_level
        self.attachments = attachments or []
        self.status = status
    
    def finalize(self, approver: str = None) -> None:
        """Finalize the assessment"""
        self.status = "FINAL"
        if approver:
            self.approved_by = approver
        self.finalized_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    @property
    def total_damage_estimate(self) -> Optional[float]:
        """Calculate total estimated damage value"""
        total = 0.0
        
        # Add infrastructure damage
        if self.infrastructure_damage and 'value' in self.infrastructure_damage:
            total += self.infrastructure_damage['value']
            
        # Add housing damage
        if self.housing_damage and 'value' in self.housing_damage:
            total += self.housing_damage['value']
            
        # Add economic impact
        if self.economic_impact and 'value' in self.economic_impact:
            total += self.economic_impact['value']
            
        # Add environmental impact (if monetized)
        if self.environmental_impact and 'value' in self.environmental_impact:
            total += self.environmental_impact['value']
            
        return total if total > 0 else None


class RecoveryMetrics(BaseModel):
    """
    Metrics for tracking recovery progress.
    """
    
    def __init__(
        self,
        event_id: str,
        reporting_period: Dict[str, str],
        metrics_type: str,
        metrics_values: Dict[str, Any],
        reporting_area: Dict[str, Any] = None,
        reported_by: str = None,
        report_date: str = None,
        phase: str = None,
        comparison_values: Dict[str, Any] = None,
        targets: Dict[str, Any] = None,
        narrative: str = None,
        methodology: str = None,
        status: str = "DRAFT",
        **kwargs
    ):
        """Initialize recovery metrics"""
        super().__init__(**kwargs)
        self.event_id = event_id
        self.reporting_period = reporting_period
        self.metrics_type = metrics_type
        self.metrics_values = metrics_values
        self.reporting_area = reporting_area
        self.reported_by = reported_by
        self.report_date = report_date or datetime.now().isoformat()
        self.phase = phase or RecoveryPhase.INITIAL_RESPONSE.value
        self.comparison_values = comparison_values or {}
        self.targets = targets or {}
        self.narrative = narrative
        self.methodology = methodology
        self.status = status
    
    def finalize(self, approver: str = None) -> None:
        """Finalize the metrics report"""
        self.status = "FINAL"
        if approver:
            self.approved_by = approver
        self.finalized_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def calculate_progress(self) -> Dict[str, Any]:
        """Calculate progress against targets"""
        progress = {}
        
        if not self.targets:
            return progress
            
        for metric, target in self.targets.items():
            if metric in self.metrics_values:
                current = self.metrics_values[metric]
                
                # Handle numeric metrics
                if isinstance(current, (int, float)) and isinstance(target, (int, float)):
                    if target != 0:
                        progress[metric] = {
                            'percent': (current / target) * 100,
                            'current': current,
                            'target': target,
                            'remaining': target - current
                        }
                # Handle categorical metrics
                elif isinstance(current, str) and isinstance(target, str):
                    progress[metric] = {
                        'match': current == target,
                        'current': current,
                        'target': target
                    }
                    
        return progress


class RecoveryProgram(BaseModel):
    """
    Recovery assistance program.
    """
    
    def __init__(
        self,
        program_name: str,
        program_type: str,
        description: str,
        eligibility_criteria: List[str],
        available_funding: float = None,
        application_deadline: str = None,
        program_start: str = None,
        program_end: str = None,
        administering_agency: str = None,
        geographic_scope: Dict[str, Any] = None,
        application_process: str = None,
        assistance_types: List[str] = None,
        program_status: str = "ACTIVE",
        contact_info: Dict[str, Any] = None,
        website: str = None,
        related_events: List[str] = None,
        **kwargs
    ):
        """Initialize recovery program"""
        super().__init__(**kwargs)
        self.program_name = program_name
        self.program_type = program_type
        self.description = description
        self.eligibility_criteria = eligibility_criteria
        self.available_funding = available_funding
        self.application_deadline = application_deadline
        self.program_start = program_start or datetime.now().isoformat()
        self.program_end = program_end
        self.administering_agency = administering_agency
        self.geographic_scope = geographic_scope
        self.application_process = application_process
        self.assistance_types = assistance_types or []
        self.program_status = program_status
        self.contact_info = contact_info
        self.website = website
        self.related_events = related_events or []
    
    @property
    def is_active(self) -> bool:
        """Check if program is currently active"""
        if self.program_status != "ACTIVE":
            return False
            
        now = datetime.now()
        
        if self.program_start and now < datetime.fromisoformat(self.program_start):
            return False
            
        if self.program_end and now > datetime.fromisoformat(self.program_end):
            return False
            
        if self.application_deadline and now > datetime.fromisoformat(self.application_deadline):
            return False
            
        return True
    
    def close_program(self, reason: str = None) -> None:
        """Close the recovery program"""
        self.program_status = "CLOSED"
        self.program_end = datetime.now().isoformat()
        if reason:
            self.closure_reason = reason
        self.updated_at = datetime.now().isoformat()