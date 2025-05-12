"""
Standardized API framework for agency implementations.

This package provides a comprehensive set of tools and patterns for building
consistent API implementations across all agency systems. It includes controllers,
services, repositories, middleware, and other components that enforce standardized
API design and behavior.
"""

from .app_factory import create_app
from .controllers.base_controller import BaseController
from .services.base_service import BaseService
from .repositories.base_repository import BaseRepository
from .repositories.sqlalchemy_repository import SQLAlchemyRepository
from .routers.router_factory import RouterFactory
from .dependencies.dependency_injection import (
    DependencyProvider,
    service_provider,
    repository_provider
)

__all__ = [
    "create_app",
    "BaseController",
    "BaseService",
    "BaseRepository",
    "SQLAlchemyRepository",
    "RouterFactory",
    "DependencyProvider",
    "service_provider",
    "repository_provider",
]