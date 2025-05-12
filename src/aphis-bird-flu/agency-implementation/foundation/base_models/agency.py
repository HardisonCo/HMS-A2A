"""
Agency models for the APHIS Agency Implementation.
Defines data models for government agencies and related entities.
"""
from typing import Dict, Any, Optional, List, Union
from datetime import date, datetime
from enum import Enum

from .base import BaseModel, GeoLocation, Address, ContactInfo


class AgencyType(str, Enum):
    """Types of government agencies"""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    TRIBAL = "tribal"
    INTERNATIONAL = "international"
    NON_GOVERNMENTAL = "non_governmental"
    OTHER = "other"


class AgencyStatus(str, Enum):
    """Status of an agency"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"


class Agency(BaseModel):
    """A government agency or organization"""
    
    def __init__(
        self,
        name: str,
        agency_type: Union[AgencyType, str],
        jurisdiction: str,
        address: Union[Address, Dict[str, Any]],
        status: Union[AgencyStatus, str] = AgencyStatus.ACTIVE,
        parent_agency_id: Optional[str] = None,
        website: Optional[str] = None,
        description: Optional[str] = None,
        contact_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize an agency"""
        # Convert address dict to Address if needed
        if isinstance(address, dict):
            address = Address.from_dict(address)
        
        # Convert string enums to Enum values if needed
        if isinstance(agency_type, str):
            agency_type = AgencyType(agency_type)
        
        if isinstance(status, str):
            status = AgencyStatus(status)
        
        # Set agency properties
        super().__init__(
            name=name,
            agency_type=agency_type,
            jurisdiction=jurisdiction,
            address=address,
            status=status,
            parent_agency_id=parent_agency_id,
            website=website,
            description=description,
            contact_info=contact_info or {},
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if isinstance(result.get('address'), Address):
            result['address'] = result['address'].to_dict()
        
        # Convert enum values to strings
        for field in ['agency_type', 'status']:
            if field in result and isinstance(result[field], Enum):
                result[field] = result[field].value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agency':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_contact(self, key: str, contact: Union[ContactInfo, Dict[str, Any]]) -> None:
        """Add a contact to the agency's contact list"""
        if isinstance(contact, dict):
            contact = ContactInfo.from_dict(contact)
            
        if not hasattr(self, 'contact_info'):
            self.contact_info = {}
            
        self.contact_info[key] = contact.to_dict()
        self.updated_at = datetime.now().isoformat()


class Department(BaseModel):
    """A department within an agency"""
    
    def __init__(
        self,
        name: str,
        agency_id: str,
        description: Optional[str] = None,
        parent_department_id: Optional[str] = None,
        head_contact: Optional[Union[ContactInfo, Dict[str, Any]]] = None,
        responsibilities: Optional[List[str]] = None,
        location: Optional[Union[Address, Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a department"""
        # Convert complex objects if needed
        if isinstance(head_contact, dict):
            head_contact = ContactInfo.from_dict(head_contact)
            
        if isinstance(location, dict):
            location = Address.from_dict(location)
        
        # Set department properties
        super().__init__(
            name=name,
            agency_id=agency_id,
            description=description,
            parent_department_id=parent_department_id,
            head_contact=head_contact.to_dict() if head_contact else None,
            responsibilities=responsibilities or [],
            location=location.to_dict() if location else None,
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Department':
        """Create from dictionary representation"""
        return cls(**data)


class Program(BaseModel):
    """A program or initiative run by an agency"""
    
    def __init__(
        self,
        name: str,
        agency_id: str,
        description: str,
        start_date: Union[date, str],
        end_date: Optional[Union[date, str]] = None,
        department_id: Optional[str] = None,
        status: str = "active",
        budget: Optional[float] = None,
        contacts: Optional[Dict[str, Any]] = None,
        objectives: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a program"""
        # Convert date strings to date objects if needed
        if isinstance(start_date, str):
            try:
                start_date = date.fromisoformat(start_date)
            except ValueError:
                # Try with datetime format and extract date
                start_date = datetime.fromisoformat(start_date).date()
                
        if isinstance(end_date, str) and end_date:
            try:
                end_date = date.fromisoformat(end_date)
            except ValueError:
                # Try with datetime format and extract date
                end_date = datetime.fromisoformat(end_date).date()
        
        # Set program properties
        super().__init__(
            name=name,
            agency_id=agency_id,
            description=description,
            start_date=start_date,
            end_date=end_date,
            department_id=department_id,
            status=status,
            budget=budget,
            contacts=contacts or {},
            objectives=objectives or [],
            metrics=metrics or {},
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert date objects to strings
        for field in ['start_date', 'end_date']:
            if field in result and isinstance(result[field], date):
                result[field] = result[field].isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Program':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_objective(self, objective: str) -> None:
        """Add an objective to the program"""
        if not hasattr(self, 'objectives'):
            self.objectives = []
            
        if objective not in self.objectives:
            self.objectives.append(objective)
            self.updated_at = datetime.now().isoformat()
    
    def update_status(self, new_status: str) -> None:
        """Update the program status"""
        self.status = new_status
        self.updated_at = datetime.now().isoformat()


class Regulation(BaseModel):
    """A regulation or policy issued by an agency"""
    
    def __init__(
        self,
        title: str,
        agency_id: str,
        description: str,
        issue_date: Union[date, str],
        regulation_number: str,
        regulation_type: str,
        text: str,
        effective_date: Optional[Union[date, str]] = None,
        expiration_date: Optional[Union[date, str]] = None,
        supersedes: Optional[List[str]] = None,
        citations: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a regulation"""
        # Convert date strings to date objects if needed
        for date_field, date_value in [
            ('issue_date', issue_date),
            ('effective_date', effective_date),
            ('expiration_date', expiration_date)
        ]:
            if isinstance(date_value, str) and date_value:
                try:
                    date_value = date.fromisoformat(date_value)
                except ValueError:
                    # Try with datetime format and extract date
                    date_value = datetime.fromisoformat(date_value).date()
                
                locals()[date_field] = date_value
        
        # Set regulation properties
        super().__init__(
            title=title,
            agency_id=agency_id,
            description=description,
            issue_date=issue_date,
            regulation_number=regulation_number,
            regulation_type=regulation_type,
            text=text,
            effective_date=effective_date,
            expiration_date=expiration_date,
            supersedes=supersedes or [],
            citations=citations or [],
            attachments=attachments or [],
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert date objects to strings
        for field in ['issue_date', 'effective_date', 'expiration_date']:
            if field in result and isinstance(result[field], date):
                result[field] = result[field].isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Regulation':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_citation(self, citation: str) -> None:
        """Add a citation to the regulation"""
        if not hasattr(self, 'citations'):
            self.citations = []
            
        if citation not in self.citations:
            self.citations.append(citation)
            self.updated_at = datetime.now().isoformat()
    
    def add_attachment(self, name: str, file_type: str, url: str, description: Optional[str] = None) -> None:
        """Add an attachment to the regulation"""
        if not hasattr(self, 'attachments'):
            self.attachments = []
            
        attachment = {
            'name': name,
            'file_type': file_type,
            'url': url,
            'upload_date': datetime.now().isoformat()
        }
        
        if description:
            attachment['description'] = description
            
        self.attachments.append(attachment)
        self.updated_at = datetime.now().isoformat()