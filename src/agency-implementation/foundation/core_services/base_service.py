"""Base service class that all specific services should inherit from."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

class BaseService(ABC):
    """Abstract base class for all services in the agency implementation framework.
    
    This class defines the common interface and functionality that all services
    should implement. It provides utility methods for configuration, logging,
    and common operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the base service.
        
        Args:
            config: Optional configuration dictionary for this service
        """
        self.config = config or self.default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def default_config(self) -> Dict[str, Any]:
        """Get the default configuration for this service.
        
        Returns:
            A dictionary containing default configuration values
        """
        pass
    
    def validate_config(self) -> bool:
        """Validate that the current configuration is valid.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Default implementation just checks if config exists
        return self.config is not None
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update the service configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates to apply
        """
        if self.config is None:
            self.config = {}
            
        self.config.update(updates)
        
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of this service.
        
        Returns:
            Dictionary with status information about the service
        """
        return {
            "service": self.__class__.__name__,
            "status": "operational",
            "config": {k: v for k, v in self.config.items() if not k.startswith('_')}
        }
