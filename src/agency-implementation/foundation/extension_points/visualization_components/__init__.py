"""
Visualization Extension Points

This module defines interfaces for extending the system with custom visualization components.
"""

from typing import Dict, List, Any, Optional, Union
import abc
from ..base import BaseExtensionPoint


class VisualizationExtensionPoint(BaseExtensionPoint):
    """
    Extension point for custom visualization components.
    
    Allows agencies to integrate custom visualization components for data,
    trends, maps, and other visual elements.
    """
    
    _extension_type: str = "visualization"
    
    @abc.abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the visualization component.
        
        Args:
            config: Configuration parameters for the visualization
            
        Returns:
            bool: True if initialization is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def shutdown(self) -> None:
        """Clean up resources used by the visualization component."""
        pass
    
    @abc.abstractmethod
    def render(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the visualization.
        
        Args:
            data: The data to visualize
            options: Rendering options
            
        Returns:
            Dict containing the visualization output (HTML, SVG, etc.)
        """
        pass
    
    @abc.abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get the output formats supported by this visualization.
        
        Returns:
            List of supported format identifiers (e.g., "html", "svg", "png")
        """
        pass
    
    @abc.abstractmethod
    def get_required_data_schema(self) -> Dict[str, Any]:
        """
        Get the schema of data required by this visualization.
        
        Returns:
            Dict describing the required data structure
        """
        pass
    
    @abc.abstractmethod
    def get_default_options(self) -> Dict[str, Any]:
        """
        Get the default rendering options.
        
        Returns:
            Dict of default option values
        """
        pass
    
    @abc.abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against the required schema.
        
        Args:
            data: The data to validate
            
        Returns:
            Dict with validation results (valid, errors)
        """
        pass
    
    @abc.abstractmethod
    def transform_data(self, data: Dict[str, Any], transformation: str) -> Dict[str, Any]:
        """
        Apply a transformation to the input data.
        
        Args:
            data: The data to transform
            transformation: Identifier of the transformation to apply
            
        Returns:
            Dict with transformed data
        """
        pass
    
    @abc.abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this visualization component.
        
        Returns:
            Dict with component metadata (name, description, version, etc.)
        """
        pass


# Import specific visualization implementations for easy access
from .choropleth_map import ChoroplethMapVisualization
from .time_series import TimeSeriesVisualization
from .heatmap import HeatmapVisualization
from .network_graph import NetworkGraphVisualization

__all__ = [
    'VisualizationExtensionPoint',
    'ChoroplethMapVisualization',
    'TimeSeriesVisualization',
    'HeatmapVisualization',
    'NetworkGraphVisualization',
]