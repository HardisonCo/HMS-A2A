"""
Extension Point Registry

This module provides a registry for managing extension points across the system.
It enables dynamic registration, discovery, and usage of extension points.
"""

import logging
from typing import Dict, List, Type, TypeVar, Generic, Any, Optional, Callable

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ExtensionRegistry:
    """Central registry for all extension points in the system."""
    
    def __init__(self):
        self._extensions: Dict[str, Dict[str, Any]] = {}
    
    def register(self, extension_type: str, name: str, implementation: Any) -> None:
        """
        Register an extension implementation.
        
        Args:
            extension_type: The type of extension point (e.g., 'data_source', 'notification')
            name: A unique name for this implementation within its type
            implementation: The extension implementation
        """
        if extension_type not in self._extensions:
            self._extensions[extension_type] = {}
            
        if name in self._extensions[extension_type]:
            logger.warning(f"Overwriting existing extension {name} of type {extension_type}")
            
        self._extensions[extension_type][name] = implementation
        logger.info(f"Registered extension '{name}' of type '{extension_type}'")
    
    def unregister(self, extension_type: str, name: str) -> bool:
        """
        Unregister an extension implementation.
        
        Args:
            extension_type: The type of extension point
            name: The name of the extension to unregister
            
        Returns:
            bool: True if successfully unregistered, False otherwise
        """
        if extension_type in self._extensions and name in self._extensions[extension_type]:
            del self._extensions[extension_type][name]
            logger.info(f"Unregistered extension '{name}' of type '{extension_type}'")
            return True
        return False
    
    def get(self, extension_type: str, name: str) -> Optional[Any]:
        """
        Get a specific extension implementation.
        
        Args:
            extension_type: The type of extension point
            name: The name of the extension
            
        Returns:
            The extension implementation or None if not found
        """
        if extension_type in self._extensions and name in self._extensions[extension_type]:
            return self._extensions[extension_type][name]
        return None
    
    def get_all(self, extension_type: str) -> Dict[str, Any]:
        """
        Get all extensions of a specific type.
        
        Args:
            extension_type: The type of extension point
            
        Returns:
            Dict mapping extension names to their implementations
        """
        return self._extensions.get(extension_type, {})
    
    def discover_extensions(self, package_path: str) -> None:
        """
        Discover and register extensions from a specific package path.
        
        Args:
            package_path: The Python package path to scan for extensions
        """
        import importlib
        import pkgutil
        import inspect
        
        from . import BaseExtensionPoint
        
        try:
            package = importlib.import_module(package_path)
            
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                if is_pkg:
                    continue
                
                try:
                    module = importlib.import_module(name)
                    
                    for _, obj in inspect.getmembers(module):
                        # Check if this is a class that extends BaseExtensionPoint and is not itself BaseExtensionPoint
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseExtensionPoint) and 
                            obj is not BaseExtensionPoint and
                            hasattr(obj, '_extension_type') and
                            hasattr(obj, '_extension_name')):
                            
                            self.register(obj._extension_type, obj._extension_name, obj)
                            
                except (ImportError, AttributeError) as e:
                    logger.error(f"Error discovering extensions in {name}: {str(e)}")
                    
        except ImportError as e:
            logger.error(f"Error importing package {package_path}: {str(e)}")
            
    def clear(self) -> None:
        """Clear all registered extensions."""
        self._extensions = {}
        logger.info("Cleared all registered extensions")