"""
Extension Points Framework

This module provides a framework for agencies to customize and extend system functionality
without modifying core components. It defines interfaces and registration mechanisms for
various extension points.
"""

from .registry import ExtensionRegistry

# Create a global registry instance
registry = ExtensionRegistry()

# Import extension point interfaces for easy access
from .data_sources import DataSourceExtensionPoint
from .notification_channels import NotificationChannelExtensionPoint
from .visualization_components import VisualizationExtensionPoint
from .predictive_models import PredictiveModelExtensionPoint
from .customization import WorkflowExtensionPoint, UIExtensionPoint
from .integration import IntegrationExtensionPoint

__all__ = [
    'registry',
    'DataSourceExtensionPoint',
    'NotificationChannelExtensionPoint',
    'VisualizationExtensionPoint',
    'PredictiveModelExtensionPoint',
    'WorkflowExtensionPoint',
    'UIExtensionPoint',
    'IntegrationExtensionPoint',
]