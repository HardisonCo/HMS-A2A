"""
Router factory module for standardized API routers.

This module provides functionality to create standardized routers with
consistent endpoint patterns and behavior across all agency implementations.
"""

from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from pydantic import BaseModel

from ..controllers.base_controller import BaseController

# Define generic types
ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ControllerType = TypeVar("ControllerType", bound=BaseController)


class RouterFactory(Generic[ModelType, SchemaType, CreateSchemaType, UpdateSchemaType, ControllerType]):
    """
    Factory class for creating standardized API routers.
    
    This class generates routers with consistent endpoints and behaviors,
    enforcing standardization across all agency API implementations.
    """
    
    @staticmethod
    def create_router(
        *,
        schema: Type[SchemaType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        controller: Type[ControllerType],
        prefix: str,
        tags: List[str],
        get_controller: Callable[..., ControllerType],
        get_current_user: Optional[Callable] = None,
        responses: Dict[int, Dict[str, Any]] = None,
        get_many_responses: Dict[int, Dict[str, Any]] = None,
        get_one_responses: Dict[int, Dict[str, Any]] = None,
        create_responses: Dict[int, Dict[str, Any]] = None,
        update_responses: Dict[int, Dict[str, Any]] = None,
        delete_responses: Dict[int, Dict[str, Any]] = None,
        additional_responses: Dict[int, Dict[str, Any]] = None,
        include_get_many: bool = True,
        include_get_one: bool = True,
        include_create: bool = True,
        include_update: bool = True,
        include_delete: bool = True,
        get_many_description: str = "Get multiple items with optional filtering and pagination",
        get_one_description: str = "Get a single item by ID",
        create_description: str = "Create a new item",
        update_description: str = "Update an existing item",
        delete_description: str = "Delete an item"
    ) -> APIRouter:
        """
        Create a router with standardized CRUD endpoints.
        
        Args:
            schema: Schema for response models
            create_schema: Schema for item creation
            update_schema: Schema for item updates
            controller: Controller class
            prefix: Router prefix (e.g., '/api/v1/users')
            tags: OpenAPI tags for grouping endpoints
            get_controller: Dependency function for getting controller instance
            get_current_user: Optional dependency for user authentication
            responses: Default responses for all endpoints
            get_many_responses: Additional responses for get_many endpoint
            get_one_responses: Additional responses for get_one endpoint
            create_responses: Additional responses for create endpoint
            update_responses: Additional responses for update endpoint
            delete_responses: Additional responses for delete endpoint
            additional_responses: Additional responses for all endpoints
            include_get_many: Whether to include get_many endpoint (default True)
            include_get_one: Whether to include get_one endpoint (default True)
            include_create: Whether to include create endpoint (default True)
            include_update: Whether to include update endpoint (default True)
            include_delete: Whether to include delete endpoint (default True)
            get_many_description: Description for get_many endpoint
            get_one_description: Description for get_one endpoint
            create_description: Description for create endpoint
            update_description: Description for update endpoint
            delete_description: Description for delete endpoint
            
        Returns:
            APIRouter: Configured FastAPI router
        """
        
        # Prepare default responses
        default_responses = {
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Authentication failed"
            },
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "description": "Internal server error"
            }
        }
        
        # Update with any provided responses
        if responses:
            default_responses.update(responses)
        if additional_responses:
            default_responses.update(additional_responses)
        
        # Create router
        router = APIRouter(
            prefix=prefix,
            tags=tags,
            responses=default_responses,
        )
        
        # Define common dependencies
        deps = [Depends(get_controller)]
        if get_current_user:
            deps.append(Depends(get_current_user))
        
        # Add get_many endpoint
        if include_get_many:
            endpoint_responses = default_responses.copy()
            if get_many_responses:
                endpoint_responses.update(get_many_responses)
                
            @router.get(
                "/",
                response_model=List[schema],
                responses=endpoint_responses,
                summary="Get multiple items",
                description=get_many_description
            )
            async def get_many(
                skip: int = Query(0, description="Number of items to skip for pagination"),
                limit: int = Query(100, description="Maximum number of items to return"),
                controller: ControllerType = deps[0],
                *args,
                **kwargs
            ) -> List[SchemaType]:
                """Get multiple items with optional pagination."""
                filter_params = {}
                # Extract filter params from query parameters
                for key, value in kwargs.items():
                    if value is not None:
                        filter_params[key] = value
                        
                return await controller.get_many(skip=skip, limit=limit, filter_params=filter_params)
        
        # Add get_one endpoint
        if include_get_one:
            endpoint_responses = default_responses.copy()
            endpoint_responses[status.HTTP_404_NOT_FOUND] = {"description": "Item not found"}
            if get_one_responses:
                endpoint_responses.update(get_one_responses)
                
            @router.get(
                "/{id}",
                response_model=schema,
                responses=endpoint_responses,
                summary="Get item by ID",
                description=get_one_description
            )
            async def get_one(
                id: str = Path(..., description="The ID of the item to retrieve"),
                controller: ControllerType = deps[0]
            ) -> SchemaType:
                """Get a single item by ID."""
                return await controller.get_one(id)
        
        # Add create endpoint
        if include_create:
            endpoint_responses = default_responses.copy()
            endpoint_responses[status.HTTP_400_BAD_REQUEST] = {"description": "Invalid input"}
            if create_responses:
                endpoint_responses.update(create_responses)
                
            @router.post(
                "/",
                response_model=schema,
                status_code=status.HTTP_201_CREATED,
                responses=endpoint_responses,
                summary="Create item",
                description=create_description
            )
            async def create(
                item_create: create_schema = Body(..., description="Item creation data"),
                controller: ControllerType = deps[0]
            ) -> SchemaType:
                """Create a new item."""
                return await controller.create(item_create)
        
        # Add update endpoint
        if include_update:
            endpoint_responses = default_responses.copy()
            endpoint_responses[status.HTTP_400_BAD_REQUEST] = {"description": "Invalid input"}
            endpoint_responses[status.HTTP_404_NOT_FOUND] = {"description": "Item not found"}
            if update_responses:
                endpoint_responses.update(update_responses)
                
            @router.put(
                "/{id}",
                response_model=schema,
                responses=endpoint_responses,
                summary="Update item",
                description=update_description
            )
            async def update(
                id: str = Path(..., description="The ID of the item to update"),
                item_update: update_schema = Body(..., description="Item update data"),
                controller: ControllerType = deps[0]
            ) -> SchemaType:
                """Update an existing item."""
                return await controller.update(id, item_update)
        
        # Add delete endpoint
        if include_delete:
            endpoint_responses = default_responses.copy()
            endpoint_responses[status.HTTP_404_NOT_FOUND] = {"description": "Item not found"}
            if delete_responses:
                endpoint_responses.update(delete_responses)
                
            @router.delete(
                "/{id}",
                responses=endpoint_responses,
                summary="Delete item",
                description=delete_description
            )
            async def delete(
                id: str = Path(..., description="The ID of the item to delete"),
                controller: ControllerType = deps[0]
            ) -> Dict[str, Any]:
                """Delete an item."""
                return await controller.delete(id)
        
        return router