"""
Base service module for standardized service implementation.

This module provides a base service class that standardizes how
services are implemented across all agency implementations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel


# Define generic types
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    """
    Base service class with standard CRUD operations.
    
    This class provides standard methods that all services will implement,
    ensuring consistent service behavior across all agency implementations.
    
    Attributes:
        repository: The repository used for data access
    """
    
    def __init__(self, repository: RepositoryType):
        """
        Initialize the service with a repository.
        
        Args:
            repository: Repository for data access
        """
        self.repository = repository
    
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
        return await self.repository.get_many(skip=skip, limit=limit, **filter_params)
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get a single item by ID.
        
        Args:
            id: Item identifier
            
        Returns:
            Item if found, None otherwise
        """
        return await self.repository.get_by_id(id)
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new item.
        
        Args:
            obj_in: Item creation data
            
        Returns:
            Created item
        """
        return await self.repository.create(obj_in)
    
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> ModelType:
        """
        Update an existing item.
        
        Args:
            id: Item identifier
            obj_in: Item update data
            
        Returns:
            Updated item
        """
        return await self.repository.update(id, obj_in)
    
    async def delete(self, id: Any) -> bool:
        """
        Delete an item.
        
        Args:
            id: Item identifier
            
        Returns:
            True if deleted, False otherwise
        """
        return await self.repository.delete(id)