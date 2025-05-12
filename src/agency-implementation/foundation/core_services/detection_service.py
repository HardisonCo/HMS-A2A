"""Detection service interface for identifying signals and patterns."""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .base_service import BaseService

class DetectionService(BaseService):
    """Abstract base class for detection services.
    
    This service is responsible for analyzing data to detect signals,
    outbreaks, anomalies, or other patterns of interest. It implements
    various detection algorithms and statistical methods.
    """
    
    def default_config(self) -> Dict[str, Any]:
        """Get the default configuration for detection.
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            "default_significance_level": 0.05,
            "minimum_cluster_size": 3,
            "temporal_window_days": 30,
            "spatial_window_km": 50,
            "baseline_method": "historical_average",
            "adjustment_factors": {"seasonal": True, "day_of_week": True}
        }
    
    @abstractmethod
    def detect_temporal_clusters(self, cases: List[Dict[str, Any]], 
                             parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Detect temporal clusters in case data.
        
        Args:
            cases: List of cases with timestamps
            parameters: Optional detection parameters
            
        Returns:
            List of detected clusters with statistics
        """
        pass
    
    @abstractmethod
    def detect_spatial_clusters(self, cases: List[Dict[str, Any]], 
                             parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Detect spatial clusters in geo-located case data.
        
        Args:
            cases: List of cases with geo coordinates
            parameters: Optional detection parameters
            
        Returns:
            List of detected spatial clusters with statistics
        """
        pass
    
    @abstractmethod
    def detect_spatiotemporal_clusters(self, cases: List[Dict[str, Any]], 
                                    parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Detect clusters in both space and time.
        
        Args:
            cases: List of cases with geo coordinates and timestamps
            parameters: Optional detection parameters
            
        Returns:
            List of detected spatiotemporal clusters with statistics
        """
        pass
    
    @abstractmethod
    def detect_anomalies(self, data: List[Dict[str, Any]], 
                       baseline_period: Tuple[datetime, datetime],
                       parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Detect anomalies compared to a baseline period.
        
        Args:
            data: Time series or other data to analyze
            baseline_period: Start and end dates of baseline period
            parameters: Optional detection parameters
            
        Returns:
            List of detected anomalies with statistics
        """
        pass
    
    @abstractmethod
    def evaluate_outbreak_probability(self, signals: List[Dict[str, Any]],
                                    context: Dict[str, Any]) -> float:
        """Evaluate the probability that detected signals represent a true outbreak.
        
        Args:
            signals: Detected signals/clusters/anomalies
            context: Contextual information for evaluation
            
        Returns:
            Probability (0-1) that signals represent a true outbreak
        """
        pass
    
    @abstractmethod
    def get_detection_threshold(self, data_type: str, significance_level: float,
                              parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get detection thresholds for a specific data type and significance level.
        
        Args:
            data_type: Type of data being analyzed
            significance_level: Statistical significance level (e.g., 0.05)
            parameters: Optional parameters for threshold calculation
            
        Returns:
            Dictionary with threshold values and metadata
        """
        pass
