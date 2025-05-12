"""
Base module for CDC domain models.
Imports and extends foundation base models for CDC-specific needs.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json

from agency_implementation.foundation.base_models.base import (
    BaseModel, Repository, GeoLocation, Address, ContactInfo
)


class CDCBaseModel(BaseModel):
    """Base model with CDC-specific common functionality"""
    
    def __init__(self, **kwargs):
        """Initialize with CDC-specific attributes"""
        # Add CDC-specific tracking fields
        if 'cdc_tracking_id' not in kwargs:
            kwargs['cdc_tracking_id'] = None
        if 'reporting_jurisdiction' not in kwargs:
            kwargs['reporting_jurisdiction'] = None
        if 'public_health_status' not in kwargs:
            kwargs['public_health_status'] = "active"
            
        # Initialize base class
        super().__init__(**kwargs)
    
    def mark_reportable(self, is_reportable: bool = True) -> None:
        """Mark case as nationally notifiable or reportable condition"""
        self.is_reportable = is_reportable
        self.updated_at = datetime.now().isoformat()
    
    def update_public_health_status(self, status: str) -> None:
        """Update the public health tracking status"""
        self.public_health_status = status
        self.updated_at = datetime.now().isoformat()


class HealthcareFacility(BaseModel):
    """Healthcare facility model for hospitals, clinics, etc."""
    
    def __init__(
        self,
        name: str,
        facility_type: str,
        location: GeoLocation,
        address: Address,
        contact_info: Optional[ContactInfo] = None,
        facility_id: Optional[str] = None,
        beds: Optional[int] = None,
        services: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a healthcare facility"""
        super().__init__(
            name=name,
            facility_type=facility_type,
            location=location,
            address=address,
            contact_info=contact_info,
            facility_id=facility_id,
            beds=beds,
            services=services or {},
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if isinstance(result.get('location'), GeoLocation):
            result['location'] = result['location'].to_dict()
        
        if isinstance(result.get('address'), Address):
            result['address'] = result['address'].to_dict()
            
        if isinstance(result.get('contact_info'), ContactInfo):
            result['contact_info'] = result['contact_info'].to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthcareFacility':
        """Create from dictionary representation"""
        # Convert dictionaries to complex objects
        if 'location' in data and isinstance(data['location'], dict):
            data['location'] = GeoLocation.from_dict(data['location'])
            
        if 'address' in data and isinstance(data['address'], dict):
            data['address'] = Address.from_dict(data['address'])
            
        if 'contact_info' in data and isinstance(data['contact_info'], dict):
            data['contact_info'] = ContactInfo.from_dict(data['contact_info'])
            
        return cls(**data)


class CDCRepository(Repository):
    """Enhanced repository interface for CDC data access operations"""
    
    def find_by_jurisdiction(self, jurisdiction: str) -> list:
        """Find entities by jurisdiction"""
        raise NotImplementedError
    
    def find_reportable(self) -> list:
        """Find nationally notifiable or reportable cases"""
        raise NotImplementedError
    
    def generate_report(self, criteria: Dict[str, Any], format_type: str = "json") -> Any:
        """Generate a formatted report based on criteria"""
        raise NotImplementedError