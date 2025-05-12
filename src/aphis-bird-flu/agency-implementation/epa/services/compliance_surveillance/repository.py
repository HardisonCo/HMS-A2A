"""
Repository implementation for Compliance Surveillance service.
Provides data access operations for regulated facilities and compliance data.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import json
import os
import logging

from agency_implementation.epa.models.base import EPARepository, ComplianceStatus, RegulatoryFramework
from agency_implementation.epa.models.compliance import (
    RegulatedFacility, Permit, ComplianceInspection,
    EnforcementAction, ComplianceReport
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegulatedFacilityRepository(EPARepository):
    """Repository for regulated facilities"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.facilities: Dict[str, RegulatedFacility] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"RegulatedFacilityRepository initialized with {len(self.facilities)} facilities")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for facility_data in data.get('facilities', []):
                facility = RegulatedFacility.from_dict(facility_data)
                self.facilities[facility.id] = facility
                
            logger.info(f"Loaded {len(self.facilities)} facilities from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'facilities': [facility.to_dict() for facility in self.facilities.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.facilities)} facilities to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[RegulatedFacility]:
        """Get a facility by ID"""
        return self.facilities.get(entity_id)
    
    def get_all(self) -> List[RegulatedFacility]:
        """Get all facilities"""
        return list(self.facilities.values())
    
    def create(self, entity: RegulatedFacility) -> RegulatedFacility:
        """Create a new facility"""
        self.facilities[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: RegulatedFacility) -> RegulatedFacility:
        """Update an existing facility"""
        if entity.id not in self.facilities:
            raise ValueError(f"Facility with ID {entity.id} does not exist")
            
        self.facilities[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a facility by ID"""
        if entity_id in self.facilities:
            del self.facilities[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[RegulatedFacility]:
        """Find facilities matching criteria"""
        results = []
        
        for facility in self.facilities.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(facility, key) or getattr(facility, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(facility)
                
        return results
    
    def find_by_region(self, region: str) -> List[RegulatedFacility]:
        """Find facilities by EPA region"""
        return [f for f in self.facilities.values() 
                if hasattr(f, 'epa_region') and f.epa_region == region]
    
    def find_by_facility_type(self, facility_type: str) -> List[RegulatedFacility]:
        """Find facilities by type"""
        return [f for f in self.facilities.values() 
                if hasattr(f, 'facility_type') and f.facility_type == facility_type]
    
    def find_by_naics_code(self, naics_code: str) -> List[RegulatedFacility]:
        """Find facilities by NAICS code"""
        return [f for f in self.facilities.values() 
                if hasattr(f, 'naics_code') and f.naics_code == naics_code]
    
    def find_by_operating_status(self, status: str) -> List[RegulatedFacility]:
        """Find facilities by operating status"""
        return [f for f in self.facilities.values() 
                if hasattr(f, 'operating_status') and f.operating_status == status]
    
    def find_by_regulatory_program(self, program: str) -> List[RegulatedFacility]:
        """Find facilities participating in a specific regulatory program"""
        return [f for f in self.facilities.values() 
                if hasattr(f, 'regulatory_programs') and 
                program in f.regulatory_programs]
    
    def find_by_geographic_area(
        self, 
        min_lat: float, 
        min_lon: float, 
        max_lat: float, 
        max_lon: float
    ) -> List[RegulatedFacility]:
        """Find facilities within a geographic bounding box"""
        results = []
        
        for facility in self.facilities.values():
            if not hasattr(facility, 'location'):
                continue
                
            lat = facility.location.latitude
            lon = facility.location.longitude
            
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                results.append(facility)
                
        return results


class PermitRepository(EPARepository):
    """Repository for environmental permits"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.permits: Dict[str, Permit] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"PermitRepository initialized with {len(self.permits)} permits")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for permit_data in data.get('permits', []):
                permit = Permit.from_dict(permit_data)
                self.permits[permit.id] = permit
                
            logger.info(f"Loaded {len(self.permits)} permits from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'permits': [permit.to_dict() for permit in self.permits.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.permits)} permits to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[Permit]:
        """Get a permit by ID"""
        return self.permits.get(entity_id)
    
    def get_all(self) -> List[Permit]:
        """Get all permits"""
        return list(self.permits.values())
    
    def create(self, entity: Permit) -> Permit:
        """Create a new permit"""
        self.permits[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: Permit) -> Permit:
        """Update an existing permit"""
        if entity.id not in self.permits:
            raise ValueError(f"Permit with ID {entity.id} does not exist")
            
        self.permits[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a permit by ID"""
        if entity_id in self.permits:
            del self.permits[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[Permit]:
        """Find permits matching criteria"""
        results = []
        
        for permit in self.permits.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(permit, key) or getattr(permit, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(permit)
                
        return results
    
    def find_by_facility_id(self, facility_id: str) -> List[Permit]:
        """Find permits by facility ID"""
        return [p for p in self.permits.values() 
                if hasattr(p, 'facility_id') and p.facility_id == facility_id]
    
    def find_by_permit_type(self, permit_type: str) -> List[Permit]:
        """Find permits by type"""
        return [p for p in self.permits.values() 
                if hasattr(p, 'permit_type') and p.permit_type == permit_type]
    
    def find_by_status(self, status: str) -> List[Permit]:
        """Find permits by status"""
        return [p for p in self.permits.values() 
                if hasattr(p, 'status') and p.status == status]
    
    def find_by_regulatory_framework(self, framework: RegulatoryFramework) -> List[Permit]:
        """Find permits by regulatory framework"""
        if isinstance(framework, RegulatoryFramework):
            framework = framework.value
            
        return [p for p in self.permits.values() 
                if hasattr(p, 'regulatory_framework') and p.regulatory_framework == framework]
    
    def find_active_permits(self) -> List[Permit]:
        """Find all active permits"""
        today = datetime.now().date()
        results = []
        
        for permit in self.permits.values():
            if not hasattr(permit, 'status') or not hasattr(permit, 'expiration_date'):
                continue
                
            if permit.status != "ACTIVE":
                continue
                
            expiration = permit.expiration_date
            if isinstance(expiration, str):
                expiration = datetime.fromisoformat(expiration).date()
                
            if today <= expiration:
                results.append(permit)
                
        return results
    
    def find_expiring_permits(self, days_threshold: int = 90) -> List[Permit]:
        """Find permits expiring within the specified number of days"""
        today = datetime.now().date()
        results = []
        
        for permit in self.permits.values():
            if not hasattr(permit, 'status') or not hasattr(permit, 'expiration_date'):
                continue
                
            if permit.status != "ACTIVE":
                continue
                
            expiration = permit.expiration_date
            if isinstance(expiration, str):
                expiration = datetime.fromisoformat(expiration).date()
                
            days_until_expiration = (expiration - today).days
            if 0 <= days_until_expiration <= days_threshold:
                results.append(permit)
                
        return results
    
    def find_by_pollutant(self, pollutant: str) -> List[Permit]:
        """Find permits allowing a specific pollutant"""
        return [p for p in self.permits.values() 
                if hasattr(p, 'permitted_pollutants') and 
                pollutant in p.permitted_pollutants]


class ComplianceInspectionRepository(EPARepository):
    """Repository for compliance inspections"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.inspections: Dict[str, ComplianceInspection] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"ComplianceInspectionRepository initialized with {len(self.inspections)} inspections")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for inspection_data in data.get('inspections', []):
                inspection = ComplianceInspection.from_dict(inspection_data)
                self.inspections[inspection.id] = inspection
                
            logger.info(f"Loaded {len(self.inspections)} inspections from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'inspections': [inspection.to_dict() for inspection in self.inspections.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.inspections)} inspections to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[ComplianceInspection]:
        """Get an inspection by ID"""
        return self.inspections.get(entity_id)
    
    def get_all(self) -> List[ComplianceInspection]:
        """Get all inspections"""
        return list(self.inspections.values())
    
    def create(self, entity: ComplianceInspection) -> ComplianceInspection:
        """Create a new inspection"""
        self.inspections[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: ComplianceInspection) -> ComplianceInspection:
        """Update an existing inspection"""
        if entity.id not in self.inspections:
            raise ValueError(f"Inspection with ID {entity.id} does not exist")
            
        self.inspections[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete an inspection by ID"""
        if entity_id in self.inspections:
            del self.inspections[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[ComplianceInspection]:
        """Find inspections matching criteria"""
        results = []
        
        for inspection in self.inspections.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(inspection, key) or getattr(inspection, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(inspection)
                
        return results
    
    def find_by_facility_id(self, facility_id: str) -> List[ComplianceInspection]:
        """Find inspections by facility ID"""
        return [i for i in self.inspections.values() 
                if hasattr(i, 'facility_id') and i.facility_id == facility_id]
    
    def find_by_inspector_id(self, inspector_id: str) -> List[ComplianceInspection]:
        """Find inspections by inspector ID"""
        return [i for i in self.inspections.values() 
                if hasattr(i, 'inspector_id') and i.inspector_id == inspector_id]
    
    def find_by_inspection_type(self, inspection_type: str) -> List[ComplianceInspection]:
        """Find inspections by type"""
        return [i for i in self.inspections.values() 
                if hasattr(i, 'inspection_type') and i.inspection_type == inspection_type]
    
    def find_by_compliance_status(self, status: ComplianceStatus) -> List[ComplianceInspection]:
        """Find inspections by compliance status"""
        if isinstance(status, ComplianceStatus):
            status = status.value
            
        return [i for i in self.inspections.values() 
                if hasattr(i, 'compliance_status') and i.compliance_status == status]
    
    def find_by_regulatory_framework(self, framework: RegulatoryFramework) -> List[ComplianceInspection]:
        """Find inspections by regulatory framework"""
        if isinstance(framework, RegulatoryFramework):
            framework = framework.value
            
        return [i for i in self.inspections.values() 
                if hasattr(i, 'regulatory_framework') and i.regulatory_framework == framework]
    
    def find_by_date_range(
        self, 
        start_date: Union[date, str], 
        end_date: Union[date, str],
        date_field: str = 'inspection_date'
    ) -> List[ComplianceInspection]:
        """Find inspections within a date range"""
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
            
        results = []
        
        for inspection in self.inspections.values():
            if not hasattr(inspection, date_field):
                continue
                
            inspection_date = getattr(inspection, date_field)
            
            # Convert string date to date object if needed
            if isinstance(inspection_date, str):
                inspection_date = datetime.fromisoformat(inspection_date).date()
                
            if start_date <= inspection_date <= end_date:
                results.append(inspection)
                
        return results
    
    def find_requiring_followup(self) -> List[ComplianceInspection]:
        """Find inspections requiring followup"""
        return [i for i in self.inspections.values() 
                if hasattr(i, 'followup_required') and i.followup_required]


class EnforcementActionRepository(EPARepository):
    """Repository for enforcement actions"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize repository"""
        self.storage_path = storage_path
        self.actions: Dict[str, EnforcementAction] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"EnforcementActionRepository initialized with {len(self.actions)} actions")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for action_data in data.get('actions', []):
                action = EnforcementAction.from_dict(action_data)
                self.actions[action.id] = action
                
            logger.info(f"Loaded {len(self.actions)} actions from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'actions': [action.to_dict() for action in self.actions.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.actions)} actions to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[EnforcementAction]:
        """Get an action by ID"""
        return self.actions.get(entity_id)
    
    def get_all(self) -> List[EnforcementAction]:
        """Get all actions"""
        return list(self.actions.values())
    
    def create(self, entity: EnforcementAction) -> EnforcementAction:
        """Create a new action"""
        self.actions[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: EnforcementAction) -> EnforcementAction:
        """Update an existing action"""
        if entity.id not in self.actions:
            raise ValueError(f"Enforcement action with ID {entity.id} does not exist")
            
        self.actions[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete an action by ID"""
        if entity_id in self.actions:
            del self.actions[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[EnforcementAction]:
        """Find actions matching criteria"""
        results = []
        
        for action in self.actions.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(action, key) or getattr(action, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(action)
                
        return results
    
    def find_by_facility_id(self, facility_id: str) -> List[EnforcementAction]:
        """Find actions by facility ID"""
        return [a for a in self.actions.values() 
                if hasattr(a, 'facility_id') and a.facility_id == facility_id]
    
    def find_by_action_type(self, action_type: str) -> List[EnforcementAction]:
        """Find actions by type"""
        return [a for a in self.actions.values() 
                if hasattr(a, 'action_type') and a.action_type == action_type]
    
    def find_by_status(self, status: str) -> List[EnforcementAction]:
        """Find actions by status"""
        return [a for a in self.actions.values() 
                if hasattr(a, 'status') and a.status == status]
    
    def find_by_regulatory_framework(self, framework: RegulatoryFramework) -> List[EnforcementAction]:
        """Find actions by regulatory framework"""
        if isinstance(framework, RegulatoryFramework):
            framework = framework.value
            
        return [a for a in self.actions.values() 
                if hasattr(a, 'regulatory_framework') and a.regulatory_framework == framework]
    
    def find_by_inspector_id(self, inspector_id: str) -> List[EnforcementAction]:
        """Find actions by inspector ID"""
        return [a for a in self.actions.values() 
                if hasattr(a, 'inspector_id') and a.inspector_id == inspector_id]
    
    def find_by_date_range(
        self, 
        start_date: Union[date, str], 
        end_date: Union[date, str],
        date_field: str = 'issuance_date'
    ) -> List[EnforcementAction]:
        """Find actions within a date range"""
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
            
        results = []
        
        for action in self.actions.values():
            if not hasattr(action, date_field):
                continue
                
            action_date = getattr(action, date_field)
            
            # Convert string date to date object if needed
            if isinstance(action_date, str):
                action_date = datetime.fromisoformat(action_date).date()
                
            if start_date <= action_date <= end_date:
                results.append(action)
                
        return results
    
    def find_by_penalty_range(
        self, 
        min_penalty: float, 
        max_penalty: float,
        penalty_field: str = 'final_penalty'
    ) -> List[EnforcementAction]:
        """Find actions with penalties within a specific range"""
        results = []
        
        for action in self.actions.values():
            if not hasattr(action, penalty_field):
                continue
                
            penalty = getattr(action, penalty_field)
            if penalty is None:
                continue
                
            if min_penalty <= penalty <= max_penalty:
                results.append(action)
                
        return results