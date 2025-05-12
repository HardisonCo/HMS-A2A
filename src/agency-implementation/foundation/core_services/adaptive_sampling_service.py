"""Adaptive sampling service interface for optimizing resource allocation."""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Tuple

from .base_service import BaseService

class AdaptiveSamplingService(BaseService):
    """Abstract base class for adaptive sampling services.
    
    This service is responsible for optimizing resource allocation using
    response-adaptive strategies. It determines where to allocate sampling
    resources based on historical data, risk factors, and optimization objectives.
    """
    
    def default_config(self) -> Dict[str, Any]:
        """Get the default configuration for adaptive sampling.
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            "optimization_objective": "detection_probability",
            "min_allocation_percent": 5,
            "max_allocation_percent": 30,
            "learning_rate": 0.1,
            "spatial_correlation_factor": 0.5,
            "temporal_decay_factor": 0.9,
        }
    
    @abstractmethod
    def allocate_resources(self, sites: List[Dict[str, Any]], resource_limit: float) -> Dict[str, float]:
        """Allocate resources optimally across surveillance sites.
        
        Args:
            sites: List of surveillance sites with their attributes
            resource_limit: Total available resources to allocate
            
        Returns:
            Dictionary mapping site IDs to allocated resources
        """
        pass
    
    @abstractmethod
    def update_from_results(self, sites: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> None:
        """Update allocation strategy based on surveillance results.
        
        Args:
            sites: List of surveillance sites that were sampled
            results: Results from sampling activities at those sites
        """
        pass
    
    @abstractmethod
    def evaluate_allocation_performance(self, allocation: Dict[str, float], 
                                      results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate the performance of a resource allocation strategy.
        
        Args:
            allocation: The resource allocation that was used
            results: The results that were obtained with that allocation
            
        Returns:
            Dictionary with performance metrics for the allocation
        """
        pass
    
    @abstractmethod
    def get_allocation_explanation(self, allocation: Dict[str, float], 
                                  sites: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get an explanation of how the allocation was determined.
        
        Args:
            allocation: The resource allocation to explain
            sites: The sites that were part of the allocation decision
            
        Returns:
            Dictionary with explanations for the allocation decisions
        """
        pass
    
    @abstractmethod
    def optimize_spatial_coverage(self, sites: List[Dict[str, Any]], 
                               existing_allocation: Dict[str, float]) -> Dict[str, float]:
        """Optimize spatial coverage given an existing allocation.
        
        Args:
            sites: List of surveillance sites with geo attributes
            existing_allocation: Current resource allocation
            
        Returns:
            Updated allocation with improved spatial coverage
        """
        pass
