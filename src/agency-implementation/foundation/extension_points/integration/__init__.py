"""
Integration Extension Points

This module defines interfaces for extending the system with custom integrations
to external systems and services.
"""

from typing import Dict, List, Any, Optional, Union
import abc
from ..base import BaseExtensionPoint


class IntegrationExtensionPoint(BaseExtensionPoint):
    """
    Extension point for custom system integrations.
    
    Allows agencies to integrate with external systems, databases, services,
    and other third-party resources.
    """
    
    _extension_type: str = "integration"
    
    @abc.abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the integration.
        
        Args:
            config: Configuration parameters for connecting to the external system
            
        Returns:
            bool: True if initialization is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def shutdown(self) -> None:
        """Clean up resources and connections used by the integration."""
        pass
    
    @abc.abstractmethod
    async def execute_operation(self, operation: str, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation on the external system.
        
        Args:
            operation: The name of the operation to perform
            params: Parameters for the operation
            context: Execution context information
            
        Returns:
            Dict with operation results
        """
        pass
    
    @abc.abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this integration.
        
        Returns:
            Dict describing the integration's features and capabilities
        """
        pass
    
    @abc.abstractmethod
    def get_operations(self) -> List[Dict[str, Any]]:
        """
        Get the list of available operations for this integration.
        
        Returns:
            List of operation descriptions
        """
        pass
    
    @abc.abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the integration.
        
        Returns:
            Dict with status information (connected, error state, etc.)
        """
        pass
    
    @abc.abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the external system.
        
        Returns:
            Dict with test results
        """
        pass
    
    @abc.abstractmethod
    def validate_params(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters for an operation.
        
        Args:
            operation: The name of the operation
            params: The parameters to validate
            
        Returns:
            Dict with validation results
        """
        pass
    
    @abc.abstractmethod
    def get_schema(self, entity_type: str) -> Dict[str, Any]:
        """
        Get the schema for an entity type in the external system.
        
        Args:
            entity_type: The type of entity to get the schema for
            
        Returns:
            Dict describing the entity schema
        """
        pass


# Import specific integration implementations for easy access
from .rest_api_integration import RestAPIIntegration
from .database_integration import DatabaseIntegration
from .file_system_integration import FileSystemIntegration
from .messaging_integration import MessagingIntegration

__all__ = [
    'IntegrationExtensionPoint',
    'RestAPIIntegration',
    'DatabaseIntegration',
    'FileSystemIntegration',
    'MessagingIntegration',
]