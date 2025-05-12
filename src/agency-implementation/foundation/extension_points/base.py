"""
Base Extension Point

This module defines the base class for all extension points in the system.
"""

import abc
from typing import ClassVar, Optional, Dict, Any, Type


class BaseExtensionPoint(abc.ABC):
    """Base class for all extension points."""
    
    _extension_type: ClassVar[str]
    _extension_name: ClassVar[str]
    
    @classmethod
    def register(cls) -> None:
        """Register this extension point with the global registry."""
        from . import registry
        registry.register(cls._extension_type, cls._extension_name, cls)
    
    @staticmethod
    def extension_point(extension_type: str, extension_name: str) -> Type['BaseExtensionPoint']:
        """
        Class decorator to mark a class as an extension point implementation.
        
        Args:
            extension_type: The type of extension point
            extension_name: A unique name for this implementation within its type
        
        Returns:
            The decorated class
        """
        def decorator(cls: Type[BaseExtensionPoint]) -> Type[BaseExtensionPoint]:
            cls._extension_type = extension_type
            cls._extension_name = extension_name
            return cls
        return decorator