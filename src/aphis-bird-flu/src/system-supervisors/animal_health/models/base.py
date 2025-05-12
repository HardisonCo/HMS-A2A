"""
Base models for the APHIS Bird Flu Tracking System.
Defines common functionality for all domain models.
"""
from typing import Dict, Any, Optional, List
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


class GeoRegion:
    """Geographic region defined by a boundary"""
    
    def __init__(
        self, 
        name: str, 
        boundary: List[GeoLocation],
        region_type: str = "custom",
        properties: Optional[Dict[str, Any]] = None
    ):
        """Initialize with boundary points"""
        self.name = name
        self.boundary = boundary
        self.region_type = region_type
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'region_type': self.region_type,
            'boundary': [point.to_dict() for point in self.boundary],
            'properties': self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeoRegion':
        """Create from dictionary representation"""
        return cls(
            name=data['name'],
            region_type=data['region_type'],
            boundary=[GeoLocation.from_dict(point) for point in data['boundary']],
            properties=data.get('properties', {})
        )
    
    def contains(self, location: GeoLocation) -> bool:
        """
        Check if the location is within this region
        Note: This is a simplified implementation using the ray casting algorithm
        For production, use a proper GIS library like Shapely
        """
        # Implementation of ray casting algorithm
        # For now, return a placeholder - this should be implemented with proper GIS libraries
        return True  # Placeholder