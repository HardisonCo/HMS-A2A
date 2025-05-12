"""
Base repository module for standardized data access.

This module provides a base repository class that standardizes how
data access is implemented across all agency implementations.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel


# Define generic types
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository class with standard CRUD operations.
    
    This class provides standard methods that all repositories will implement,
    ensuring consistent data access patterns across all agency implementations.
    """
    
    async def get_many(self, 
                     skip: int = 0, 
                     limit: int = 100, 
                     **filter_params) -> List[ModelType]:
        """
        Get multiple items with optional filtering, pagination.
        
        Args:
            skip: Number of items to skip (pagination)
            limit: Maximum number of items to return
            **filter_params: Optional filter parameters
            
        Returns:
            List of items
        """
        raise NotImplementedError("Subclasses must implement get_many()")
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get a single item by ID.
        
        Args:
            id: Item identifier
            
        Returns:
            Item if found, None otherwise
        """
        raise NotImplementedError("Subclasses must implement get_by_id()")
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new item.
        
        Args:
            obj_in: Item creation data
            
        Returns:
            Created item
        """
        raise NotImplementedError("Subclasses must implement create()")
    
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> ModelType:
        """
        Update an existing item.
        
        Args:
            id: Item identifier
            obj_in: Item update data
            
        Returns:
            Updated item
        """
        raise NotImplementedError("Subclasses must implement update()")
    
    async def delete(self, id: Any) -> bool:
        """
        Delete an item.
        
        Args:
            id: Item identifier
            
        Returns:
            True if deleted, False otherwise
        """
        raise NotImplementedError("Subclasses must implement delete()")