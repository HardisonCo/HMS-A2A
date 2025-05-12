"""
Federated Query Service

This module implements a service for executing federated queries across 
multiple agencies through the federation hub.
"""

import logging
from typing import Dict, List, Any, Optional
from ..core.federation_hub import get_federation_hub

logger = logging.getLogger(__name__)

class FederatedQueryService:
    """
    Service for executing federated queries across multiple agencies.
    
    This service provides capabilities for querying data from multiple 
    agencies with a unified interface and result format.
    """
    
    def __init__(self):
        self.federation_hub = get_federation_hub()
        logger.info("Federated Query Service initialized")
    
    def execute_query(self, query: Dict[str, Any], agencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a federated query across multiple agencies
        
        Args:
            query: Query specification
            agencies: Optional list of agency IDs to query (None = all agencies)
            
        Returns:
            Consolidated results from queried agencies
        """
        logger.info(f"Executing federated query of type '{query.get('type', 'unknown')}' across {len(agencies) if agencies else 'all'} agencies")
        
        # Execute the query through the federation hub
        results = self.federation_hub.execute_federated_query(query, agencies)
        
        # Process and consolidate results
        consolidated_results = self._consolidate_results(results, query)
        
        return consolidated_results
    
    def _consolidate_results(self, results: Dict[str, Any], query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate results from multiple agencies into a unified format
        
        Args:
            results: Results from individual agencies
            query: Original query specification
            
        Returns:
            Consolidated results
        """
        query_type = query.get("type", "")
        
        # Calculate statistics about the results
        total_records = sum(
            len(result.get("data", [])) 
            for agency_id, result in results.items() 
            if result.get("status") == "success"
        )
        
        successful_agencies = [
            agency_id for agency_id, result in results.items()
            if result.get("status") == "success"
        ]
        
        failed_agencies = [
            {"agency_id": agency_id, "error": result.get("message", "Unknown error")}
            for agency_id, result in results.items()
            if result.get("status") != "success"
        ]
        
        # Combine data from successful agencies
        combined_data = []
        for agency_id, result in results.items():
            if result.get("status") == "success":
                agency_data = result.get("data", [])
                # Add agency_id to each record
                for record in agency_data:
                    if isinstance(record, dict):
                        record["source_agency"] = agency_id
                    combined_data.append(record)
        
        return {
            "query_type": query_type,
            "parameters": query.get("parameters", {}),
            "total_records": total_records,
            "successful_agencies": successful_agencies,
            "failed_agencies": failed_agencies,
            "data": combined_data
        }
    
    def get_available_query_types(self) -> Dict[str, List[str]]:
        """
        Get available query types for each registered agency
        
        Returns:
            Dictionary mapping agency IDs to their supported query types
        """
        query_types = {}
        
        for agency in self.federation_hub.get_registered_agencies():
            agency_id = agency.agency_id
            
            # Mock implementation - in production this would query the agency's capabilities
            if agency_id == "cdc":
                query_types[agency_id] = ["disease_surveillance", "outbreak_detection", "contact_tracing"]
            elif agency_id == "epa":
                query_types[agency_id] = ["env_quality", "compliance", "pollution_impact"]
            elif agency_id == "fema":
                query_types[agency_id] = ["disaster_risk", "resource_deployment", "recovery_progress"]
            else:
                query_types[agency_id] = []
        
        return query_types