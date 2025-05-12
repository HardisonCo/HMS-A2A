"""
Repository implementation for the Human Disease Surveillance service.
Provides data access operations for human disease cases.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import date, datetime
import json
import os
import logging

from agency_implementation.cdc.models.base import CDCRepository
from agency_implementation.cdc.models.human_disease import (
    HumanDiseaseCase, CaseClassification, DiseaseType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HumanDiseaseRepository(CDCRepository):
    """
    Repository for human disease cases.
    
    Implements data access operations for HumanDiseaseCase entities.
    In a real implementation, this would interact with a database,
    but for this implementation we use an in-memory store.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            storage_path: Optional path to store data (for persistence)
        """
        self.storage_path = storage_path
        self.cases: Dict[str, HumanDiseaseCase] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"HumanDiseaseRepository initialized with {len(self.cases)} cases")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for case_data in data.get('cases', []):
                case = HumanDiseaseCase.from_dict(case_data)
                self.cases[case.id] = case
                
            logger.info(f"Loaded {len(self.cases)} cases from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'cases': [case.to_dict() for case in self.cases.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.cases)} cases to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[HumanDiseaseCase]:
        """
        Get a case by its ID.
        
        Args:
            entity_id: The ID of the case to retrieve
            
        Returns:
            The case if found, None otherwise
        """
        return self.cases.get(entity_id)
    
    def get_all(self) -> List[HumanDiseaseCase]:
        """
        Get all cases.
        
        Returns:
            List of all cases
        """
        return list(self.cases.values())
    
    def create(self, entity: HumanDiseaseCase) -> HumanDiseaseCase:
        """
        Create a new case.
        
        Args:
            entity: The case to create
            
        Returns:
            The created case
        """
        self.cases[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: HumanDiseaseCase) -> HumanDiseaseCase:
        """
        Update an existing case.
        
        Args:
            entity: The case to update
            
        Returns:
            The updated case
            
        Raises:
            ValueError: If the case does not exist
        """
        if entity.id not in self.cases:
            raise ValueError(f"Case with ID {entity.id} does not exist")
            
        self.cases[entity.id] = entity
        entity.updated_at = datetime.now().isoformat()
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete a case by ID.
        
        Args:
            entity_id: The ID of the case to delete
            
        Returns:
            True if the case was deleted, False otherwise
        """
        if entity_id in self.cases:
            del self.cases[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[HumanDiseaseCase]:
        """
        Find cases matching criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            List of matching cases
        """
        results = []
        
        for case in self.cases.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(case, key) or getattr(case, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(case)
                
        return results
    
    def find_by_jurisdiction(self, jurisdiction: str) -> List[HumanDiseaseCase]:
        """
        Find cases by jurisdiction.
        
        Args:
            jurisdiction: The jurisdiction to filter by
            
        Returns:
            List of cases in the specified jurisdiction
        """
        return [case for case in self.cases.values() 
                if hasattr(case, 'jurisdiction') and case.jurisdiction == jurisdiction]
    
    def find_reportable(self) -> List[HumanDiseaseCase]:
        """
        Find nationally notifiable or reportable cases.
        
        Returns:
            List of reportable cases
        """
        return [case for case in self.cases.values() 
                if hasattr(case, 'is_reportable') and case.is_reportable]
    
    def find_by_disease_type(self, disease_type: Union[DiseaseType, str]) -> List[HumanDiseaseCase]:
        """
        Find cases by disease type.
        
        Args:
            disease_type: The disease type to filter by
            
        Returns:
            List of cases with the specified disease type
        """
        if isinstance(disease_type, str):
            disease_type = DiseaseType(disease_type)
            
        return [case for case in self.cases.values() 
                if hasattr(case, 'disease_type') and case.disease_type == disease_type]
    
    def find_by_date_range(self, 
                           start_date: Union[date, str], 
                           end_date: Union[date, str], 
                           date_field: str = 'report_date') -> List[HumanDiseaseCase]:
        """
        Find cases within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            date_field: Field to filter by (report_date or onset_date)
            
        Returns:
            List of cases within the date range
        """
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
            
        results = []
        
        for case in self.cases.values():
            if not hasattr(case, date_field):
                continue
                
            case_date = getattr(case, date_field)
            
            # Convert string date to date object if needed
            if isinstance(case_date, str):
                case_date = date.fromisoformat(case_date)
                
            if start_date <= case_date <= end_date:
                results.append(case)
                
        return results
    
    def find_by_classification(self, classification: Union[CaseClassification, str]) -> List[HumanDiseaseCase]:
        """
        Find cases by classification.
        
        Args:
            classification: The classification to filter by
            
        Returns:
            List of cases with the specified classification
        """
        if isinstance(classification, str):
            classification = CaseClassification(classification)
            
        return [case for case in self.cases.values() 
                if hasattr(case, 'classification') and case.classification == classification]
    
    def generate_report(self, criteria: Dict[str, Any], format_type: str = "json") -> Any:
        """
        Generate a formatted report based on criteria.
        
        Args:
            criteria: Dictionary of criteria to filter cases
            format_type: Format of the report (json, csv, etc.)
            
        Returns:
            Report data in the specified format
        """
        # Find cases matching criteria
        cases = self.find(criteria)
        
        if format_type == "json":
            return {
                "report_date": datetime.now().isoformat(),
                "criteria": criteria,
                "total_cases": len(cases),
                "cases": [case.to_dict() for case in cases]
            }
        elif format_type == "summary":
            # Group by disease type
            disease_counts = {}
            jurisdiction_counts = {}
            classification_counts = {}
            
            for case in cases:
                # Count by disease type
                disease_type = case.disease_type.value if hasattr(case, 'disease_type') else "unknown"
                disease_counts[disease_type] = disease_counts.get(disease_type, 0) + 1
                
                # Count by jurisdiction
                jurisdiction = case.jurisdiction if hasattr(case, 'jurisdiction') else "unknown"
                jurisdiction_counts[jurisdiction] = jurisdiction_counts.get(jurisdiction, 0) + 1
                
                # Count by classification
                classification = case.classification.value if hasattr(case, 'classification') else "unknown"
                classification_counts[classification] = classification_counts.get(classification, 0) + 1
            
            return {
                "report_date": datetime.now().isoformat(),
                "criteria": criteria,
                "total_cases": len(cases),
                "by_disease": disease_counts,
                "by_jurisdiction": jurisdiction_counts,
                "by_classification": classification_counts
            }
        else:
            raise ValueError(f"Unsupported report format: {format_type}")
            
    def get_cases_with_related(self, case_id: str) -> List[HumanDiseaseCase]:
        """
        Get a case and all related cases.
        
        Args:
            case_id: ID of the primary case
            
        Returns:
            List containing the primary case and all related cases
        """
        results = []
        primary_case = self.get_by_id(case_id)
        
        if not primary_case:
            return results
            
        results.append(primary_case)
        
        # Add related cases if they exist
        if hasattr(primary_case, 'related_cases'):
            for related_id in primary_case.related_cases:
                related_case = self.get_by_id(related_id)
                if related_case and related_case not in results:
                    results.append(related_case)
        
        return results