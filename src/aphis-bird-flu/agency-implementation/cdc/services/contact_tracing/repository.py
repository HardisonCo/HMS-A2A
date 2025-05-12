"""
Repository implementation for the Contact Tracing service.
Provides data access operations for contacts.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import date, datetime, timedelta
import json
import os
import logging

from agency_implementation.cdc.models.base import CDCRepository
from agency_implementation.cdc.models.human_disease import (
    Contact, HumanDiseaseCase, RiskLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactRepository(CDCRepository):
    """
    Repository for contact tracing entities.
    
    Implements data access operations for Contact entities.
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
        self.contacts: Dict[str, Contact] = {}
        
        # Load data from storage if available
        if storage_path and os.path.exists(storage_path):
            self._load_from_storage()
            
        logger.info(f"ContactRepository initialized with {len(self.contacts)} contacts")
    
    def _load_from_storage(self) -> None:
        """Load data from storage if available"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            for contact_data in data.get('contacts', []):
                contact = Contact.from_dict(contact_data)
                self.contacts[contact.id] = contact
                
            logger.info(f"Loaded {len(self.contacts)} contacts from storage")
        except Exception as e:
            logger.error(f"Error loading data from storage: {str(e)}")
    
    def _save_to_storage(self) -> None:
        """Save data to storage if path is provided"""
        if not self.storage_path:
            return
            
        try:
            data = {
                'contacts': [contact.to_dict() for contact in self.contacts.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.contacts)} contacts to storage")
        except Exception as e:
            logger.error(f"Error saving data to storage: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[Contact]:
        """
        Get a contact by its ID.
        
        Args:
            entity_id: The ID of the contact to retrieve
            
        Returns:
            The contact if found, None otherwise
        """
        return self.contacts.get(entity_id)
    
    def get_all(self) -> List[Contact]:
        """
        Get all contacts.
        
        Returns:
            List of all contacts
        """
        return list(self.contacts.values())
    
    def create(self, entity: Contact) -> Contact:
        """
        Create a new contact.
        
        Args:
            entity: The contact to create
            
        Returns:
            The created contact
        """
        self.contacts[entity.id] = entity
        self._save_to_storage()
        return entity
    
    def update(self, entity: Contact) -> Contact:
        """
        Update an existing contact.
        
        Args:
            entity: The contact to update
            
        Returns:
            The updated contact
            
        Raises:
            ValueError: If the contact does not exist
        """
        if entity.id not in self.contacts:
            raise ValueError(f"Contact with ID {entity.id} does not exist")
            
        self.contacts[entity.id] = entity
        entity.updated_at = datetime.now().isoformat()
        self._save_to_storage()
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete a contact by ID.
        
        Args:
            entity_id: The ID of the contact to delete
            
        Returns:
            True if the contact was deleted, False otherwise
        """
        if entity_id in self.contacts:
            del self.contacts[entity_id]
            self._save_to_storage()
            return True
        return False
    
    def find(self, criteria: Dict[str, Any]) -> List[Contact]:
        """
        Find contacts matching criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            List of matching contacts
        """
        results = []
        
        for contact in self.contacts.values():
            matches = True
            
            for key, value in criteria.items():
                if not hasattr(contact, key) or getattr(contact, key) != value:
                    matches = False
                    break
            
            if matches:
                results.append(contact)
                
        return results
    
    def find_by_case_id(self, case_id: str) -> List[Contact]:
        """
        Find contacts associated with a case.
        
        Args:
            case_id: The case ID to filter by
            
        Returns:
            List of contacts associated with the case
        """
        return [contact for contact in self.contacts.values() 
                if hasattr(contact, 'case_id') and contact.case_id == case_id]
    
    def find_by_person_id(self, person_id: str) -> List[Contact]:
        """
        Find contacts by person ID.
        
        Args:
            person_id: The person ID to filter by
            
        Returns:
            List of contacts for the person
        """
        return [contact for contact in self.contacts.values() 
                if hasattr(contact, 'person_id') and contact.person_id == person_id]
    
    def find_by_jurisdiction(self, jurisdiction: str) -> List[Contact]:
        """
        Find contacts by jurisdiction.
        
        Args:
            jurisdiction: The jurisdiction to filter by
            
        Returns:
            List of contacts in the specified jurisdiction
        """
        return [contact for contact in self.contacts.values() 
                if hasattr(contact, 'jurisdiction') and contact.jurisdiction == jurisdiction]
    
    def find_reportable(self) -> List[Contact]:
        """
        Find nationally notifiable or reportable contacts.
        
        Returns:
            List of reportable contacts
        """
        return [contact for contact in self.contacts.values() 
                if hasattr(contact, 'is_reportable') and contact.is_reportable]
    
    def find_by_risk_level(self, risk_level: Union[RiskLevel, str]) -> List[Contact]:
        """
        Find contacts by risk level.
        
        Args:
            risk_level: The risk level to filter by
            
        Returns:
            List of contacts with the specified risk level
        """
        if isinstance(risk_level, str):
            risk_level = RiskLevel(risk_level)
            
        return [contact for contact in self.contacts.values() 
                if hasattr(contact, 'risk_assessment') and contact.risk_assessment == risk_level]
    
    def find_by_date_range(self, 
                           start_date: Union[date, str], 
                           end_date: Union[date, str]) -> List[Contact]:
        """
        Find contacts within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of contacts within the date range
        """
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
            
        results = []
        
        for contact in self.contacts.values():
            if not hasattr(contact, 'contact_date'):
                continue
                
            contact_date = contact.contact_date
            
            # Convert string date to date object if needed
            if isinstance(contact_date, str):
                contact_date = date.fromisoformat(contact_date)
                
            if start_date <= contact_date <= end_date:
                results.append(contact)
                
        return results
    
    def find_by_monitoring_status(self, status: str) -> List[Contact]:
        """
        Find contacts by monitoring status.
        
        Args:
            status: The monitoring status to filter by
            
        Returns:
            List of contacts with the specified monitoring status
        """
        return [contact for contact in self.contacts.values() 
                if hasattr(contact, 'monitoring_status') and contact.monitoring_status == status]
    
    def find_active_monitoring(self) -> List[Contact]:
        """
        Find contacts under active monitoring.
        
        Returns:
            List of contacts under active monitoring
        """
        active_statuses = ['pending', 'active', 'monitoring']
        return [contact for contact in self.contacts.values() 
                if hasattr(contact, 'monitoring_status') and contact.monitoring_status in active_statuses]
    
    def generate_report(self, criteria: Dict[str, Any], format_type: str = "json") -> Any:
        """
        Generate a formatted report based on criteria.
        
        Args:
            criteria: Dictionary of criteria to filter contacts
            format_type: Format of the report (json, csv, etc.)
            
        Returns:
            Report data in the specified format
        """
        # Find contacts matching criteria
        contacts = self.find(criteria)
        
        if format_type == "json":
            return {
                "report_date": datetime.now().isoformat(),
                "criteria": criteria,
                "total_contacts": len(contacts),
                "contacts": [contact.to_dict() for contact in contacts]
            }
        elif format_type == "summary":
            # Group by risk assessment
            risk_counts = {}
            monitoring_counts = {}
            
            for contact in contacts:
                # Count by risk assessment
                risk = contact.risk_assessment.value if hasattr(contact, 'risk_assessment') else "unknown"
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
                
                # Count by monitoring status
                status = contact.monitoring_status if hasattr(contact, 'monitoring_status') else "unknown"
                monitoring_counts[status] = monitoring_counts.get(status, 0) + 1
            
            return {
                "report_date": datetime.now().isoformat(),
                "criteria": criteria,
                "total_contacts": len(contacts),
                "by_risk": risk_counts,
                "by_monitoring_status": monitoring_counts
            }
        else:
            raise ValueError(f"Unsupported report format: {format_type}")
    
    def count_by_risk_level(self) -> Dict[str, int]:
        """
        Count contacts by risk level.
        
        Returns:
            Dictionary with counts by risk level
        """
        counts = {}
        
        for contact in self.contacts.values():
            if hasattr(contact, 'risk_assessment'):
                risk = contact.risk_assessment.value if hasattr(contact.risk_assessment, 'value') else str(contact.risk_assessment)
                counts[risk] = counts.get(risk, 0) + 1
        
        return counts
    
    def count_by_monitoring_status(self) -> Dict[str, int]:
        """
        Count contacts by monitoring status.
        
        Returns:
            Dictionary with counts by monitoring status
        """
        counts = {}
        
        for contact in self.contacts.values():
            if hasattr(contact, 'monitoring_status'):
                status = contact.monitoring_status
                counts[status] = counts.get(status, 0) + 1
        
        return counts