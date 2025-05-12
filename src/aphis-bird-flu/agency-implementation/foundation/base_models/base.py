"""
Base models for the APHIS Agency Implementation.
Defines common functionality for all domain models.
"""
from typing import Dict, Any, Optional, List, TypeVar, Generic
from datetime import datetime
import uuid
import json


class BaseModel:
    """Base model with common functionality for all domain models"""
    
    def __init__(self, **kwargs):
        """Initialize with provided attributes"""
        # Generate id if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        # Set creation and update timestamps
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now().isoformat()
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = kwargs['created_at']
        
        # Set attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseModel':
        """Create model instance from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update(self, **kwargs) -> None:
        """Update model attributes"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now().isoformat()


T = TypeVar('T')


class Repository(Generic[T]):
    """Base repository interface for data access operations"""
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        raise NotImplementedError
    
    def get_all(self) -> List[T]:
        """Get all entities"""
        raise NotImplementedError
    
    def create(self, entity: T) -> T:
        """Create a new entity"""
        raise NotImplementedError
    
    def update(self, entity: T) -> T:
        """Update an existing entity"""
        raise NotImplementedError
    
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID"""
        raise NotImplementedError
    
    def find(self, criteria: Dict[str, Any]) -> List[T]:
        """Find entities matching criteria"""
        raise NotImplementedError


class GeoLocation:
    """Geographic location with latitude and longitude coordinates"""
    
    def __init__(self, latitude: float, longitude: float, elevation: Optional[float] = None):
        """Initialize with coordinates"""
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'latitude': self.latitude,
            'longitude': self.longitude
        }
        if self.elevation is not None:
            result['elevation'] = self.elevation
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeoLocation':
        """Create from dictionary representation"""
        return cls(
            latitude=data['latitude'],
            longitude=data['longitude'],
            elevation=data.get('elevation')
        )
    
    def __str__(self) -> str:
        """String representation of coordinates"""
        if self.elevation is not None:
            return f"({self.latitude}, {self.longitude}, {self.elevation})"
        return f"({self.latitude}, {self.longitude})"


class Address:
    """Physical address representation"""
    
    def __init__(
        self,
        street: str,
        city: str,
        state: str,
        zip_code: str,
        country: str = "USA",
        address_line2: Optional[str] = None
    ):
        """Initialize with address components"""
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country
        self.address_line2 = address_line2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country
        }
        if self.address_line2:
            result['address_line2'] = self.address_line2
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """Create from dictionary representation"""
        return cls(
            street=data['street'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            country=data.get('country', 'USA'),
            address_line2=data.get('address_line2')
        )
    
    def __str__(self) -> str:
        """String representation of address"""
        address_str = f"{self.street}"
        if self.address_line2:
            address_str += f", {self.address_line2}"
        address_str += f", {self.city}, {self.state} {self.zip_code}, {self.country}"
        return address_str


class ContactInfo:
    """Contact information for individuals or organizations"""
    
    def __init__(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[Address] = None,
        position: Optional[str] = None,
        organization: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Initialize with contact details"""
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.position = position
        self.organization = organization
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'name': self.name
        }
        
        if self.email:
            result['email'] = self.email
        if self.phone:
            result['phone'] = self.phone
        if self.address:
            result['address'] = self.address.to_dict()
        if self.position:
            result['position'] = self.position
        if self.organization:
            result['organization'] = self.organization
        if self.notes:
            result['notes'] = self.notes
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContactInfo':
        """Create from dictionary representation"""
        address = None
        if 'address' in data and data['address']:
            address = Address.from_dict(data['address'])
            
        return cls(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=address,
            position=data.get('position'),
            organization=data.get('organization'),
            notes=data.get('notes')
        )