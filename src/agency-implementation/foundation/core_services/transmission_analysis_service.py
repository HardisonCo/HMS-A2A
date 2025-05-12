"""Transmission analysis service interface for analyzing spread patterns."""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union

from .base_service import BaseService

class TransmissionAnalysisService(BaseService):
    """Abstract base class for transmission analysis services.
    
    This service is responsible for analyzing transmission patterns,
    reconstructing transmission networks, and assessing factors
    affecting spread dynamics.
    """
    
    def default_config(self) -> Dict[str, Any]:
        """Get the default configuration for transmission analysis.
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            "temporal_window_days": 14,
            "spatial_threshold_km": 50,
            "minimum_link_probability": 0.2,
            "transmission_models": ["distance", "network", "gravity"],
            "include_uncertainty": True,
            "max_generation_links": 5,
        }
    
    @abstractmethod
    def reconstruct_transmission_network(self, cases: List[Dict[str, Any]],
                                      parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reconstruct a transmission network from case data.
        
        Args:
            cases: List of cases with temporal and spatial data
            parameters: Optional reconstruction parameters
            
        Returns:
            Dictionary with network structure and metadata
        """
        pass
    
    @abstractmethod
    def calculate_transmission_risk(self, source: Dict[str, Any],
                                 destination: Dict[str, Any],
                                 parameters: Optional[Dict[str, Any]] = None) -> float:
        """Calculate transmission risk between source and destination.
        
        Args:
            source: Source case or location
            destination: Destination case or location
            parameters: Optional risk calculation parameters
            
        Returns:
            Probability (0-1) of transmission
        """
        pass
    
    @abstractmethod
    def identify_superspreaders(self, network: Dict[str, Any],
                             parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Identify potential superspreaders in a transmission network.
        
        Args:
            network: Transmission network to analyze
            parameters: Optional analysis parameters
            
        Returns:
            List of potential superspreader nodes with metadata
        """
        pass
    
    @abstractmethod
    def analyze_transmission_dynamics(self, cases: List[Dict[str, Any]],
                                   network: Optional[Dict[str, Any]] = None,
                                   parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze transmission dynamics from case data and optional network.
        
        Args:
            cases: List of cases with temporal and spatial data
            network: Optional pre-constructed transmission network
            parameters: Optional analysis parameters
            
        Returns:
            Dictionary with transmission dynamics analysis
        """
        pass
    
    @abstractmethod
    def evaluate_intervention_impact(self, baseline_network: Dict[str, Any],
                                  intervention: Dict[str, Any],
                                  parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluate the potential impact of an intervention on transmission.
        
        Args:
            baseline_network: Baseline transmission network
            intervention: Intervention specification
            parameters: Optional evaluation parameters
            
        Returns:
            Dictionary with intervention impact assessment
        """
        pass
    
    @abstractmethod
    def visualize_transmission_network(self, network: Dict[str, Any],
                                    parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a visualization of a transmission network.
        
        Args:
            network: Transmission network to visualize
            parameters: Optional visualization parameters
            
        Returns:
            Dictionary with visualization data and metadata
        """
        pass
