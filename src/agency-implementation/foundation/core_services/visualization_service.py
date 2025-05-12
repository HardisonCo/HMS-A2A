"""Visualization service interface for creating maps, charts, and dashboards."""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union

from .base_service import BaseService

class VisualizationService(BaseService):
    """Abstract base class for visualization services.
    
    This service is responsible for generating visual representations of data,
    including maps, charts, graphs, and dashboards. It supports both static
    visualizations and interactive components.
    """
    
    def default_config(self) -> Dict[str, Any]:
        """Get the default configuration for visualization.
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            "default_figure_size": (12, 9),
            "default_dpi": 100,
            "color_scheme": "tableau",
            "map_provider": "default",
            "include_basemap": True,
            "default_projection": "mercator",
            "interactive": True,
            "export_formats": ["png", "svg", "json"],
        }
    
    @abstractmethod
    def create_map(self, data: Dict[str, Any], 
                parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a map visualization.
        
        Args:
            data: Data to visualize on the map
            parameters: Optional visualization parameters
            
        Returns:
            Dictionary with visualization data and metadata
        """
        pass
    
    @abstractmethod
    def create_chart(self, data: Dict[str, Any],
                   chart_type: str,
                   parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a chart visualization.
        
        Args:
            data: Data to visualize in the chart
            chart_type: Type of chart (e.g., 'bar', 'line', 'scatter')
            parameters: Optional visualization parameters
            
        Returns:
            Dictionary with visualization data and metadata
        """
        pass
    
    @abstractmethod
    def create_dashboard(self, components: List[Dict[str, Any]],
                       layout: Optional[Dict[str, Any]] = None,
                       parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a dashboard with multiple visualization components.
        
        Args:
            components: List of visualization components
            layout: Optional layout specification
            parameters: Optional dashboard parameters
            
        Returns:
            Dictionary with dashboard data and metadata
        """
        pass
    
    @abstractmethod
    def register_renderer(self, type_name: str, renderer: Any) -> None:
        """Register a custom visualization renderer.
        
        Args:
            type_name: Name for the renderer type
            renderer: Renderer object or function
        """
        pass
    
    @abstractmethod
    def create_animation(self, data: Dict[str, Any],
                       time_field: str,
                       parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an animated visualization.
        
        Args:
            data: Data to visualize with time dimension
            time_field: Field containing time information
            parameters: Optional animation parameters
            
        Returns:
            Dictionary with animation data and metadata
        """
        pass
    
    @abstractmethod
    def export_visualization(self, visualization: Dict[str, Any],
                          format: str,
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export a visualization to a specific format.
        
        Args:
            visualization: Visualization to export
            format: Export format (e.g., 'png', 'svg', 'json')
            parameters: Optional export parameters
            
        Returns:
            Dictionary with exported data and metadata
        """
        pass
