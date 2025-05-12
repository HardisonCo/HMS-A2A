"""
Base Adapter for Federation Integration

This module defines the base adapter interface that each agency will implement
to connect with the Federation Hub.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class FederationAdapter(ABC):
    """
    Abstract base class for agency federation adapters.
    
    Each agency must implement this interface to participate in the 
    federation hub's data sharing, alert coordination, and resource management.
    """
    
    def __init__(self, agency_id: str, config: Optional[Dict[str, Any]] = None):
        self.agency_id = agency_id
        self.config = config or {}
    
    @abstractmethod
    def execute_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a federated query from the federation hub
        
        Args:
            query: Query specification with parameters
            
        Returns:
            Query results from this agency
        """
        pass
    
    @abstractmethod
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Process an alert received from the federation hub
        
        Args:
            alert: Alert details
            
        Returns:
            True if alert was successfully processed
        """
        pass
    
    @abstractmethod
    def allocate_resources(self, resource_type: str, quantity: int, 
                           location: Dict[str, Any], priority: str) -> Dict[str, Any]:
        """
        Allocate resources in response to a coordination request
        
        Args:
            resource_type: Type of resource requested
            quantity: Quantity of resources requested
            location: Location details where resources are needed
            priority: Priority level of the request
            
        Returns:
            Details of allocated resources
        """
        pass
    
    @abstractmethod
    def get_analysis_data(self, analysis_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve agency data for joint analysis
        
        Args:
            analysis_request: Details of the requested analysis
            
        Returns:
            List of data records for analysis
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the list of federation capabilities supported by this agency
        
        Returns:
            List of capability identifiers
        """
        pass