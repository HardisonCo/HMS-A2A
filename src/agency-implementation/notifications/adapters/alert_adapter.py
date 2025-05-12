"""
Alert Adapter Base Class

Defines the base class for agency-specific alert adapters.
"""

import logging
from typing import Dict, List, Any, Optional, Type
from abc import ABC, abstractmethod

from ..models.alert import Alert

logger = logging.getLogger(__name__)


class AlertAdapter(ABC):
    """
    Base class for agency-specific alert adapters.
    
    Adapters are responsible for retrieving alerts from specific agency
    sources and converting them to the unified Alert format.
    """
    
    # Registry of adapter classes by type
    _adapter_registry: Dict[str, Type['AlertAdapter']] = {}
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the alert adapter.
        
        Args:
            config: Configuration for the adapter
        """
        self.config = config
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the alert adapter.
        
        Returns:
            bool: True if initialization was successful
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the alert adapter."""
        pass
    
    @abstractmethod
    async def get_alerts(self) -> List[Alert]:
        """
        Get alerts from the agency source.
        
        Returns:
            List of alerts
        """
        pass
    
    @classmethod
    def register_adapter(cls, adapter_type: str):
        """
        Decorator to register an adapter class.
        
        Args:
            adapter_type: The type name for this adapter
            
        Returns:
            Decorator function
        """
        def decorator(adapter_class):
            cls._adapter_registry[adapter_type] = adapter_class
            return adapter_class
        return decorator
    
    @classmethod
    def get_adapter(cls, adapter_type: str) -> Optional[Type['AlertAdapter']]:
        """
        Get adapter class by type.
        
        Args:
            adapter_type: Type name of the adapter
            
        Returns:
            Adapter class or None if not found
        """
        return cls._adapter_registry.get(adapter_type)