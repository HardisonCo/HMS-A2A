"""
Base controller module for standardized API controllers.

This module provides a base controller class that standardizes how
controllers are implemented across all agency implementations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel

# Define generic type for models
ModelType = TypeVar("ModelType")
# Define generic type for schemas
SchemaType = TypeVar("SchemaType", bound=BaseModel)
# Define generic type for create schemas
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Define generic type for update schemas
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseController(Generic[ModelType, SchemaType, CreateSchemaType, UpdateSchemaType]):
    """
    Base controller class with default CRUD operations.
    
    This class provides standard methods that all controllers will implement,
    ensuring consistent API behavior across all agency implementations.
    
    Attributes:
        service: The service instance used for data operations
        model: The model class used by this controller
    """
    
    def __init__(self, service: Any):
        """
        Initialize the controller with a service instance.
        
        Args:
            service: Service instance for data operations
        """
        self.service = service
    
    async def get_many(self, 
                      skip: int = 0, 
                      limit: int = 100, 
                      filter_params: Dict[str, Any] = None) -> List[SchemaType]:
        """
        Get multiple items with optional filtering, pagination.
        
        Args:
            skip: Number of items to skip (pagination)
            limit: Maximum number of items to return
            filter_params: Optional filter parameters
            
        Returns:
            List of items
        """
        filter_params = filter_params or {}
        try:
            return await self.service.get_many(skip=skip, limit=limit, **filter_params)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving items: {str(e)}"
            )
    
    async def get_one(self, id: Any) -> SchemaType:
        """
        Get a single item by ID.
        
        Args:
            id: Item identifier
            
        Returns:
            Single item
            
        Raises:
            HTTPException: If item not found
        """
        try:
            item = await self.service.get_by_id(id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item with id {id} not found"
                )
            return item
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving item: {str(e)}"
            )
    
    async def create(self, item_create: CreateSchemaType) -> SchemaType:
        """
        Create a new item.
        
        Args:
            item_create: Item creation data
            
        Returns:
            Created item
        """
        try:
            return await self.service.create(item_create)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating item: {str(e)}"
            )
    
    async def update(self, id: Any, item_update: UpdateSchemaType) -> SchemaType:
        """
        Update an existing item.
        
        Args:
            id: Item identifier
            item_update: Item update data
            
        Returns:
            Updated item
            
        Raises:
            HTTPException: If item not found
        """
        try:
            item = await self.service.get_by_id(id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item with id {id} not found"
                )
            return await self.service.update(id, item_update)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating item: {str(e)}"
            )
    
    async def delete(self, id: Any) -> Dict[str, Any]:
        """
        Delete an item.
        
        Args:
            id: Item identifier
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If item not found
        """
        try:
            item = await self.service.get_by_id(id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item with id {id} not found"
                )
            await self.service.delete(id)
            return {"status": "success", "message": f"Item with id {id} deleted"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting item: {str(e)}"
            )