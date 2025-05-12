"""
Federation Hub for Interagency Data Sharing

This module implements the central hub for facilitating data sharing between agencies.
It provides a standardized interface for agencies to register, query data, and coordinate
across organizational boundaries.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AgencyRegistration(BaseModel):
    """Model for agency registration with the federation hub"""
    agency_id: str
    name: str
    endpoint_base_url: str
    api_version: str = "v1"
    capabilities: List[str] = Field(default_factory=list)
    last_heartbeat: Optional[datetime] = None

class FederationHub:
    """
    Central hub for interagency data sharing and coordination.
    
    This class manages agency registrations, handles federated queries,
    and coordinates cross-agency communications and alerts.
    """
    
    def __init__(self):
        self._registered_agencies: Dict[str, AgencyRegistration] = {}
        self._shared_services = {}
        self._adapters = {}
        logger.info("Federation Hub initialized")
    
    def register_agency(self, registration: AgencyRegistration) -> bool:
        """
        Register an agency with the federation hub
        
        Args:
            registration: AgencyRegistration object with agency details
            
        Returns:
            bool: True if registration was successful
        """
        if registration.agency_id in self._registered_agencies:
            logger.warning(f"Agency {registration.agency_id} is already registered, updating details")
            
        registration.last_heartbeat = datetime.now()
        self._registered_agencies[registration.agency_id] = registration
        logger.info(f"Agency {registration.name} ({registration.agency_id}) registered successfully")
        return True
    
    def get_registered_agencies(self) -> List[AgencyRegistration]:
        """
        Get list of all registered agencies
        
        Returns:
            List[AgencyRegistration]: List of agency registration details
        """
        return list(self._registered_agencies.values())
    
    def register_adapter(self, agency_id: str, adapter) -> None:
        """
        Register an adapter for a specific agency
        
        Args:
            agency_id: Agency identifier
            adapter: Adapter instance for the agency
        """
        self._adapters[agency_id] = adapter
        logger.info(f"Adapter registered for agency {agency_id}")

    def execute_federated_query(self, query: Dict[str, Any], agencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a federated query across multiple agencies
        
        Args:
            query: Query specification
            agencies: Optional list of agency IDs to query (None = all agencies)
            
        Returns:
            Dictionary containing results from each agency
        """
        target_agencies = agencies or list(self._registered_agencies.keys())
        results = {}
        
        for agency_id in target_agencies:
            if agency_id not in self._registered_agencies:
                logger.warning(f"Agency {agency_id} is not registered, skipping")
                continue
                
            if agency_id not in self._adapters:
                logger.warning(f"No adapter registered for agency {agency_id}, skipping")
                continue
                
            try:
                # Execute query through agency adapter
                agency_result = self._adapters[agency_id].execute_query(query)
                results[agency_id] = agency_result
            except Exception as e:
                logger.error(f"Error executing query for agency {agency_id}: {str(e)}")
                results[agency_id] = {"error": str(e)}
                
        return results
    
    def broadcast_alert(self, alert: Dict[str, Any], agencies: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Broadcast an alert to multiple agencies
        
        Args:
            alert: Alert details
            agencies: Optional list of agency IDs to alert (None = all agencies)
            
        Returns:
            Dictionary mapping agency IDs to delivery status
        """
        target_agencies = agencies or list(self._registered_agencies.keys())
        results = {}
        
        for agency_id in target_agencies:
            if agency_id not in self._registered_agencies:
                logger.warning(f"Agency {agency_id} is not registered, skipping alert")
                continue
                
            if agency_id not in self._adapters:
                logger.warning(f"No adapter registered for agency {agency_id}, skipping alert")
                continue
                
            try:
                # Send alert through agency adapter
                success = self._adapters[agency_id].send_alert(alert)
                results[agency_id] = success
            except Exception as e:
                logger.error(f"Error sending alert to agency {agency_id}: {str(e)}")
                results[agency_id] = False
                
        return results
    
    def coordinate_resources(self, resource_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate resource allocation across agencies
        
        Args:
            resource_request: Resource coordination request
            
        Returns:
            Response with coordinated resource allocation
        """
        # Implement resource coordination logic
        requesting_agency = resource_request.get("requesting_agency")
        resource_type = resource_request.get("resource_type")
        quantity = resource_request.get("quantity")
        priority = resource_request.get("priority", "medium")
        location = resource_request.get("location", {})
        
        logger.info(f"Processing resource coordination request from {requesting_agency} " 
                   f"for {quantity} units of {resource_type} (priority: {priority})")
        
        # Resource allocation logic would go here
        allocation_results = {}
        
        for agency_id, adapter in self._adapters.items():
            if agency_id == requesting_agency:
                continue  # Skip requesting agency
                
            try:
                # Check resource availability and allocate resources
                agency_allocation = adapter.allocate_resources(resource_type, quantity, location, priority)
                if agency_allocation and agency_allocation.get("allocated_quantity", 0) > 0:
                    allocation_results[agency_id] = agency_allocation
            except Exception as e:
                logger.error(f"Error coordinating resources with agency {agency_id}: {str(e)}")
        
        return {
            "request": resource_request,
            "allocations": allocation_results,
            "total_allocated": sum(a.get("allocated_quantity", 0) for a in allocation_results.values())
        }
    
    def run_joint_analysis(self, analysis_request: Dict[str, Any], agencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run a joint analysis across multiple agencies
        
        Args:
            analysis_request: Analysis specification
            agencies: Optional list of agency IDs to include (None = all agencies)
            
        Returns:
            Combined analysis results
        """
        target_agencies = agencies or list(self._registered_agencies.keys())
        agency_data = {}
        
        # Step 1: Collect relevant data from each agency
        for agency_id in target_agencies:
            if agency_id not in self._adapters:
                continue
                
            try:
                # Get data from each agency for analysis
                data = self._adapters[agency_id].get_analysis_data(analysis_request)
                agency_data[agency_id] = data
            except Exception as e:
                logger.error(f"Error getting analysis data from agency {agency_id}: {str(e)}")
        
        # Step 2: Perform joint analysis on combined data
        # This would typically use a specialized analytics service
        analysis_type = analysis_request.get("analysis_type", "default")
        analysis_params = analysis_request.get("parameters", {})
        
        # Mock implementation - in production this would call a proper analytics service
        combined_results = {
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "agency_contributions": {agency: len(data) for agency, data in agency_data.items()},
            "combined_result": f"Joint analysis of type {analysis_type} across {len(agency_data)} agencies"
        }
        
        return combined_results


# Singleton instance of the federation hub
_federation_hub_instance = None

def get_federation_hub() -> FederationHub:
    """Get the singleton instance of the federation hub"""
    global _federation_hub_instance
    if _federation_hub_instance is None:
        _federation_hub_instance = FederationHub()
    return _federation_hub_instance