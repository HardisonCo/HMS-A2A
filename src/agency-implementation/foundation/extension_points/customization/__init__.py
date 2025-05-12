"""
Customization Extension Points

This module defines interfaces for extending the system with custom UI, workflow,
and general customization components.
"""

from typing import Dict, List, Any, Optional, Union, Callable
import abc
from ..base import BaseExtensionPoint


class WorkflowExtensionPoint(BaseExtensionPoint):
    """
    Extension point for custom workflow processes.
    
    Allows agencies to customize business processes, approval workflows,
    data processing pipelines, and other workflow elements.
    """
    
    _extension_type: str = "workflow"
    
    @abc.abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the workflow extension.
        
        Args:
            config: Configuration parameters for the workflow
            
        Returns:
            bool: True if initialization is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def shutdown(self) -> None:
        """Clean up resources used by the workflow extension."""
        pass
    
    @abc.abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow process.
        
        Args:
            input_data: The input data for the workflow
            context: The execution context (user, permissions, etc.)
            
        Returns:
            Dict with execution results
        """
        pass
    
    @abc.abstractmethod
    def get_workflow_definition(self) -> Dict[str, Any]:
        """
        Get the definition of this workflow.
        
        Returns:
            Dict describing the workflow (steps, transitions, etc.)
        """
        pass
    
    @abc.abstractmethod
    def register_hook(self, hook_point: str, callback: Callable) -> str:
        """
        Register a callback hook for a specific point in the workflow.
        
        Args:
            hook_point: The name of the hook point
            callback: The callback function to register
            
        Returns:
            str: The ID of the registered hook
        """
        pass
    
    @abc.abstractmethod
    def unregister_hook(self, hook_id: str) -> bool:
        """
        Unregister a callback hook.
        
        Args:
            hook_id: The ID of the hook to unregister
            
        Returns:
            bool: True if the hook was successfully unregistered
        """
        pass
    
    @abc.abstractmethod
    def get_available_hook_points(self) -> List[str]:
        """
        Get the list of available hook points in this workflow.
        
        Returns:
            List of hook point names
        """
        pass
    
    @abc.abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data for the workflow.
        
        Args:
            input_data: The input data to validate
            
        Returns:
            Dict with validation results
        """
        pass


class UIExtensionPoint(BaseExtensionPoint):
    """
    Extension point for custom UI components.
    
    Allows agencies to customize UI elements, layouts, forms, and other
    presentation components.
    """
    
    _extension_type: str = "ui"
    
    @abc.abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the UI extension.
        
        Args:
            config: Configuration parameters for the UI component
            
        Returns:
            bool: True if initialization is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def shutdown(self) -> None:
        """Clean up resources used by the UI extension."""
        pass
    
    @abc.abstractmethod
    def render(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the UI component.
        
        Args:
            data: The data to render
            context: The rendering context (user, theme, etc.)
            
        Returns:
            Dict with rendered content (HTML, JSON, etc.)
        """
        pass
    
    @abc.abstractmethod
    def get_component_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this UI component.
        
        Returns:
            Dict with component metadata (name, type, version, etc.)
        """
        pass
    
    @abc.abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data for rendering.
        
        Args:
            data: The data to validate
            
        Returns:
            Dict with validation results
        """
        pass
    
    @abc.abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get the output formats supported by this UI component.
        
        Returns:
            List of supported format identifiers (e.g., "html", "json", "react")
        """
        pass
    
    @abc.abstractmethod
    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get the events that can be triggered by this UI component.
        
        Returns:
            List of event descriptions
        """
        pass


# Import specific customization implementations for easy access
from .approval_workflow import ApprovalWorkflow
from .data_processing_workflow import DataProcessingWorkflow
from .custom_form import CustomFormComponent
from .dashboard_widget import DashboardWidgetComponent

__all__ = [
    'WorkflowExtensionPoint',
    'UIExtensionPoint',
    'ApprovalWorkflow',
    'DataProcessingWorkflow',
    'CustomFormComponent',
    'DashboardWidgetComponent',
]