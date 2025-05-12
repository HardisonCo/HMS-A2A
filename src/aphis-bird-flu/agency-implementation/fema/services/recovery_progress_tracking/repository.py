"""
Repository implementations for Recovery Progress Tracking service.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import os

from agency_implementation.foundation.base_models.base import Repository
from agency_implementation.fema.models.recovery import (
    RecoveryProject, DamageAssessment, RecoveryMetrics, RecoveryProgram
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecoveryProjectRepository(Repository[RecoveryProject]):
    """Repository for managing recovery projects"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "recovery_projects"
    
    def get_by_id(self, entity_id: str) -> Optional[RecoveryProject]:
        """Get a recovery project by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return RecoveryProject.from_dict(data)
    
    def get_all(self) -> List[RecoveryProject]:
        """Get all recovery projects"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [RecoveryProject.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: RecoveryProject) -> RecoveryProject:
        """Create a new recovery project"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created recovery project: {entity.id}")
        
        return entity
    
    def update(self, entity: RecoveryProject) -> RecoveryProject:
        """Update an existing recovery project"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated recovery project: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a recovery project by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted recovery project: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[RecoveryProject]:
        """Find recovery projects matching criteria"""
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
                results.append(RecoveryProject.from_dict(data))
                
        return results
    
    def find_by_event_id(self, event_id: str) -> List[RecoveryProject]:
        """Find projects for a specific disaster event"""
        return self.find({"event_id": event_id})
    
    def find_by_project_type(self, project_type: str) -> List[RecoveryProject]:
        """Find projects by type"""
        return self.find({"project_type": project_type})
    
    def find_by_status(self, status: str) -> List[RecoveryProject]:
        """Find projects by status"""
        return self.find({"status": status})
    
    def find_by_phase(self, phase: str) -> List[RecoveryProject]:
        """Find projects by recovery phase"""
        return self.find({"phase": phase})
    
    def find_by_agency(self, responsible_agency: str) -> List[RecoveryProject]:
        """Find projects by responsible agency"""
        return self.find({"responsible_agency": responsible_agency})
    
    def find_active_projects(self) -> List[RecoveryProject]:
        """Find active (non-completed) projects"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if 'status' in data and data['status'] not in ['COMPLETED', 'CANCELLED']:
                results.append(RecoveryProject.from_dict(data))
                
        return results
    
    def find_overdue_projects(self) -> List[RecoveryProject]:
        """Find overdue projects (past target completion date but not completed)"""
        now = datetime.now().isoformat()
        
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if ('status' in data and data['status'] not in ['COMPLETED', 'CANCELLED'] and
                'target_completion_date' in data and data['target_completion_date'] and
                data['target_completion_date'] < now):
                results.append(RecoveryProject.from_dict(data))
                
        return results


class DamageAssessmentRepository(Repository[DamageAssessment]):
    """Repository for managing damage assessments"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "damage_assessments"
    
    def get_by_id(self, entity_id: str) -> Optional[DamageAssessment]:
        """Get a damage assessment by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return DamageAssessment.from_dict(data)
    
    def get_all(self) -> List[DamageAssessment]:
        """Get all damage assessments"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [DamageAssessment.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: DamageAssessment) -> DamageAssessment:
        """Create a new damage assessment"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created damage assessment: {entity.id}")
        
        return entity
    
    def update(self, entity: DamageAssessment) -> DamageAssessment:
        """Update an existing damage assessment"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated damage assessment: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a damage assessment by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted damage assessment: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[DamageAssessment]:
        """Find damage assessments matching criteria"""
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
                results.append(DamageAssessment.from_dict(data))
                
        return results
    
    def find_by_event_id(self, event_id: str) -> List[DamageAssessment]:
        """Find assessments for a specific disaster event"""
        return self.find({"event_id": event_id})
    
    def find_by_assessment_type(self, assessment_type: str) -> List[DamageAssessment]:
        """Find assessments by type"""
        return self.find({"assessment_type": assessment_type})
    
    def find_by_damage_level(self, damage_level: str) -> List[DamageAssessment]:
        """Find assessments by damage level"""
        return self.find({"damage_level": damage_level})
    
    def find_by_status(self, status: str) -> List[DamageAssessment]:
        """Find assessments by status"""
        return self.find({"status": status})
    
    def find_final_assessments(self) -> List[DamageAssessment]:
        """Find finalized assessments"""
        return self.find({"status": "FINAL"})


class RecoveryMetricsRepository(Repository[RecoveryMetrics]):
    """Repository for managing recovery metrics"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "recovery_metrics"
    
    def get_by_id(self, entity_id: str) -> Optional[RecoveryMetrics]:
        """Get recovery metrics by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return RecoveryMetrics.from_dict(data)
    
    def get_all(self) -> List[RecoveryMetrics]:
        """Get all recovery metrics"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [RecoveryMetrics.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: RecoveryMetrics) -> RecoveryMetrics:
        """Create new recovery metrics"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created recovery metrics: {entity.id}")
        
        return entity
    
    def update(self, entity: RecoveryMetrics) -> RecoveryMetrics:
        """Update existing recovery metrics"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated recovery metrics: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete recovery metrics by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted recovery metrics: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[RecoveryMetrics]:
        """Find recovery metrics matching criteria"""
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
                results.append(RecoveryMetrics.from_dict(data))
                
        return results
    
    def find_by_event_id(self, event_id: str) -> List[RecoveryMetrics]:
        """Find metrics for a specific disaster event"""
        return self.find({"event_id": event_id})
    
    def find_by_metrics_type(self, metrics_type: str) -> List[RecoveryMetrics]:
        """Find metrics by type"""
        return self.find({"metrics_type": metrics_type})
    
    def find_by_phase(self, phase: str) -> List[RecoveryMetrics]:
        """Find metrics by recovery phase"""
        return self.find({"phase": phase})
    
    def find_by_status(self, status: str) -> List[RecoveryMetrics]:
        """Find metrics by status"""
        return self.find({"status": status})
    
    def find_latest_by_event(self, event_id: str, metrics_type: str = None) -> Optional[RecoveryMetrics]:
        """Find latest metrics for an event, optionally filtered by type"""
        metrics = self.find_by_event_id(event_id)
        
        if metrics_type:
            metrics = [m for m in metrics if hasattr(m, 'metrics_type') and m.metrics_type == metrics_type]
            
        if not metrics:
            return None
            
        # Return the most recent metrics (by report_date)
        return max(metrics, key=lambda m: getattr(m, 'report_date', ''))


class RecoveryProgramRepository(Repository[RecoveryProgram]):
    """Repository for managing recovery programs"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "recovery_programs"
    
    def get_by_id(self, entity_id: str) -> Optional[RecoveryProgram]:
        """Get a recovery program by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return RecoveryProgram.from_dict(data)
    
    def get_all(self) -> List[RecoveryProgram]:
        """Get all recovery programs"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [RecoveryProgram.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: RecoveryProgram) -> RecoveryProgram:
        """Create a new recovery program"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created recovery program: {entity.id}")
        
        return entity
    
    def update(self, entity: RecoveryProgram) -> RecoveryProgram:
        """Update an existing recovery program"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated recovery program: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a recovery program by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted recovery program: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[RecoveryProgram]:
        """Find recovery programs matching criteria"""
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
                results.append(RecoveryProgram.from_dict(data))
                
        return results
    
    def find_by_program_type(self, program_type: str) -> List[RecoveryProgram]:
        """Find programs by type"""
        return self.find({"program_type": program_type})
    
    def find_by_agency(self, administering_agency: str) -> List[RecoveryProgram]:
        """Find programs by administering agency"""
        return self.find({"administering_agency": administering_agency})
    
    def find_by_status(self, program_status: str) -> List[RecoveryProgram]:
        """Find programs by status"""
        return self.find({"program_status": program_status})
    
    def find_active_programs(self) -> List[RecoveryProgram]:
        """Find active programs"""
        programs = self.find({"program_status": "ACTIVE"})
        
        # Filter by dates
        now = datetime.now().isoformat()
        
        return [
            p for p in programs if 
            (not hasattr(p, 'program_start') or not p.program_start or p.program_start <= now) and
            (not hasattr(p, 'program_end') or not p.program_end or p.program_end >= now) and
            (not hasattr(p, 'application_deadline') or not p.application_deadline or p.application_deadline >= now)
        ]
    
    def find_by_related_event(self, event_id: str) -> List[RecoveryProgram]:
        """Find programs related to a specific disaster event"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if 'related_events' in data and data['related_events'] and event_id in data['related_events']:
                results.append(RecoveryProgram.from_dict(data))
                
        return results