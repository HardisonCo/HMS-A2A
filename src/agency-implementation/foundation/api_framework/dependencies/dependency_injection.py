"""
Dependency injection module for standardized API dependency management.

This module provides a consistent approach to dependency injection
across all agency API implementations, making services and repositories
available to controllers in a standardized way.
"""

from typing import Any, Callable, Dict, Generic, Type, TypeVar
import inspect
from fastapi import Depends


# Generic service and repository types
ServiceType = TypeVar("ServiceType")
RepoType = TypeVar("RepoType")


class DependencyProvider:
    """
    Dependency provider for managing service and repository dependencies.
    
    This class centralizes the creation and management of dependencies,
    enabling consistent dependency injection across the API.
    """
    
    _instance = None
    _services = {}
    _repositories = {}
    _config = {}
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(DependencyProvider, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def register_service(cls, service_type: Type[ServiceType], implementation: Type[ServiceType], **kwargs):
        """
        Register a service implementation.
        
        Args:
            service_type: Interface or base class type
            implementation: Concrete implementation class
            **kwargs: Additional constructor arguments
        """
        cls._services[service_type] = {
            'implementation': implementation,
            'kwargs': kwargs
        }
    
    @classmethod
    def register_repository(cls, repo_type: Type[RepoType], implementation: Type[RepoType], **kwargs):
        """
        Register a repository implementation.
        
        Args:
            repo_type: Interface or base class type
            implementation: Concrete implementation class
            **kwargs: Additional constructor arguments
        """
        cls._repositories[repo_type] = {
            'implementation': implementation,
            'kwargs': kwargs
        }
    
    @classmethod
    def register_config(cls, name: str, value: Any):
        """
        Register a configuration value.
        
        Args:
            name: Configuration parameter name
            value: Configuration value
        """
        cls._config[name] = value
    
    @classmethod
    def get_service(cls, service_type: Type[ServiceType]) -> ServiceType:
        """
        Get a service instance of the specified type.
        
        Args:
            service_type: Service type to retrieve
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service is not registered
        """
        if service_type not in cls._services:
            raise KeyError(f"Service of type {service_type.__name__} is not registered")
        
        service_info = cls._services[service_type]
        implementation = service_info['implementation']
        kwargs = service_info['kwargs']
        
        # Inspect the constructor to resolve dependencies
        init_signature = inspect.signature(implementation.__init__)
        init_params = init_signature.parameters
        
        # Initialize constructor parameters
        constructor_args = {}
        
        # Process each parameter in the constructor
        for name, param in init_params.items():
            # Skip 'self' parameter
            if name == 'self':
                continue
                
            # If the parameter is in the kwargs, use that value
            if name in kwargs:
                constructor_args[name] = kwargs[name]
            # If the parameter type hint is a repository, inject the repository
            elif param.annotation != inspect.Parameter.empty:
                param_type = param.annotation
                if param_type in cls._repositories:
                    constructor_args[name] = cls.get_repository(param_type)
        
        # Create and return the service instance
        return implementation(**constructor_args)
    
    @classmethod
    def get_repository(cls, repo_type: Type[RepoType]) -> RepoType:
        """
        Get a repository instance of the specified type.
        
        Args:
            repo_type: Repository type to retrieve
            
        Returns:
            Repository instance
            
        Raises:
            KeyError: If repository is not registered
        """
        if repo_type not in cls._repositories:
            raise KeyError(f"Repository of type {repo_type.__name__} is not registered")
        
        repo_info = cls._repositories[repo_type]
        implementation = repo_info['implementation']
        kwargs = repo_info['kwargs']
        
        # Create and return the repository instance
        return implementation(**kwargs)
    
    @classmethod
    def get_config(cls, name: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            name: Configuration parameter name
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        return cls._config.get(name, default)


# Create dependency provider functions for FastAPI
def get_dependency_provider() -> DependencyProvider:
    """Get the dependency provider instance."""
    return DependencyProvider()


def service_provider(service_type: Type[ServiceType]) -> Callable[[], ServiceType]:
    """
    Create a FastAPI dependency for a service.
    
    Args:
        service_type: Service type to provide
        
    Returns:
        Dependency callable
    """
    def get_service_dependency(provider = Depends(get_dependency_provider)) -> ServiceType:
        return provider.get_service(service_type)
    return get_service_dependency


def repository_provider(repo_type: Type[RepoType]) -> Callable[[], RepoType]:
    """
    Create a FastAPI dependency for a repository.
    
    Args:
        repo_type: Repository type to provide
        
    Returns:
        Dependency callable
    """
    def get_repository_dependency(provider = Depends(get_dependency_provider)) -> RepoType:
        return provider.get_repository(repo_type)
    return get_repository_dependency