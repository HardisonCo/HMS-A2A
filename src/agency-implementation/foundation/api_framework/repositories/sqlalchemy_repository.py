"""
SQLAlchemy repository module for standardized database access.

This module provides a SQLAlchemy implementation of the base repository
pattern for consistent database access across agency implementations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .base_repository import BaseRepository


# Define generic types
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class SQLAlchemyRepository(BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    SQLAlchemy implementation of the base repository.
    
    This class provides a concrete implementation of the repository pattern
    using SQLAlchemy for database access.
    
    Attributes:
        model: The SQLAlchemy model class
        db_session: The SQLAlchemy async session
    """
    
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        """
        Initialize the repository with a model class and session.
        
        Args:
            model: SQLAlchemy model class
            db_session: SQLAlchemy async session
        """
        self.model = model
        self.db_session = db_session
    
    async def get_many(self, 
                     skip: int = 0, 
                     limit: int = 100, 
                     **filter_params) -> List[ModelType]:
        """
        Get multiple items with optional filtering, pagination.
        
        Args:
            skip: Number of items to skip (pagination)
            limit: Maximum number of items to return
            **filter_params: Optional filter parameters for the query
            
        Returns:
            List of items
        """
        query = select(self.model)
        
        # Apply filters
        for field, value in filter_params.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await self.db_session.execute(query)
        
        return list(result.scalars().all())
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get a single item by ID.
        
        Args:
            id: Item identifier
            
        Returns:
            Item if found, None otherwise
        """
        query = select(self.model).filter(self.model.id == id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new item.
        
        Args:
            obj_in: Item creation data
            
        Returns:
            Created item
        """
        # Convert pydantic model to dict
        obj_data = obj_in.model_dump()
        
        # Create instance of SQLAlchemy model
        db_obj = self.model(**obj_data)
        
        # Add to session
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        
        return db_obj
    
    async def update(self, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Update an existing item.
        
        Args:
            id: Item identifier
            obj_in: Item update data (pydantic model or dict)
            
        Returns:
            Updated item
        """
        # Get current item
        db_obj = await self.get_by_id(id)
        
        if db_obj is None:
            raise ValueError(f"Item with id {id} not found")
        
        # Convert input to dict if it's a pydantic model
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        
        # Create SQLAlchemy update statement
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )
        
        # Execute update
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        return result.scalar_one()
    
    async def delete(self, id: Any) -> bool:
        """
        Delete an item.
        
        Args:
            id: Item identifier
            
        Returns:
            True if deleted, False otherwise
        """
        # Check if item exists
        db_obj = await self.get_by_id(id)
        
        if db_obj is None:
            return False
        
        # Create delete statement
        stmt = delete(self.model).where(self.model.id == id)
        
        # Execute delete
        await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        return True