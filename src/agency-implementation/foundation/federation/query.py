"""
Federated Query System for secure cross-agency data queries.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Callable
import json
import asyncio
from datetime import datetime

from federation.models import Agency, FederationRequest, FederationResponse
from federation.exceptions import QueryError, AuthorizationError

logger = logging.getLogger(__name__)


class FederatedQueryBuilder:
    """
    Builder for constructing federated queries.
    
    This class provides a fluent interface for building queries
    that can be executed across multiple agencies.
    """
    
    def __init__(self, manager):
        """Initialize query builder with federation manager."""
        self._manager = manager
        self._dataset = None
        self._query = {}
        self._target_agencies = []
        self._timeout = 30.0  # Default timeout in seconds
        self._max_results = None
        self._options = {}
    
    def select(self, dataset: str) -> 'FederatedQueryBuilder':
        """
        Select the dataset to query.
        
        Args:
            dataset: Name of the dataset
            
        Returns:
            Self for chaining
        """
        self._dataset = dataset
        return self
    
    def where(self, conditions: Dict[str, Any]) -> 'FederatedQueryBuilder':
        """
        Add filter conditions to the query.
        
        Args:
            conditions: Dictionary of field-value pairs for filtering
            
        Returns:
            Self for chaining
        """
        self._query.setdefault("filters", {}).update(conditions)
        return self
    
    def aggregate(self, aggregations: Dict[str, str]) -> 'FederatedQueryBuilder':
        """
        Add aggregations to the query.
        
        Args:
            aggregations: Dictionary mapping output fields to aggregation functions
                          e.g. {"total_cases": "SUM(cases)"}
            
        Returns:
            Self for chaining
        """
        self._query.setdefault("aggregations", {}).update(aggregations)
        return self
    
    def limit(self, limit: int) -> 'FederatedQueryBuilder':
        """
        Set maximum number of results to return.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            Self for chaining
        """
        self._max_results = limit
        self._query["limit"] = limit
        return self
    
    def order_by(self, field: str, direction: str = "ASC") -> 'FederatedQueryBuilder':
        """
        Set result ordering.
        
        Args:
            field: Field to order by
            direction: "ASC" or "DESC"
            
        Returns:
            Self for chaining
        """
        self._query.setdefault("order_by", []).append({"field": field, "direction": direction})
        return self
    
    def from_agencies(self, agency_ids: List[str]) -> 'FederatedQueryBuilder':
        """
        Specify target agencies for the query.
        
        Args:
            agency_ids: List of agency IDs to query
            
        Returns:
            Self for chaining
        """
        self._target_agencies = agency_ids
        return self
    
    def with_timeout(self, seconds: float) -> 'FederatedQueryBuilder':
        """
        Set query timeout.
        
        Args:
            seconds: Timeout in seconds
            
        Returns:
            Self for chaining
        """
        self._timeout = seconds
        return self
    
    def with_option(self, key: str, value: Any) -> 'FederatedQueryBuilder':
        """
        Set additional query options.
        
        Args:
            key: Option name
            value: Option value
            
        Returns:
            Self for chaining
        """
        self._options[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build the query specification.
        
        Returns:
            Dictionary containing the complete query specification
        """
        if not self._dataset:
            raise QueryError("Dataset must be specified using select()")
        
        return {
            "dataset": self._dataset,
            "query": self._query,
            "target_agencies": self._target_agencies,
            "timeout": self._timeout,
            "max_results": self._max_results,
            "options": self._options
        }
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the federated query.
        
        Returns:
            Query results from all participating agencies
        """
        query_spec = self.build()
        return self._manager.execute_query(query_spec)


class QueryManager:
    """
    Manager for federated queries across agencies.
    """
    
    def __init__(self, federation_manager):
        """Initialize with federation manager reference."""
        self._federation = federation_manager
        self._http_client = None  # Will be initialized when needed
    
    def build(self) -> FederatedQueryBuilder:
        """
        Create a new query builder.
        
        Returns:
            FederatedQueryBuilder instance
        """
        return FederatedQueryBuilder(self)
    
    def execute_query(self, query_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a federated query across agencies.
        
        Args:
            query_spec: Query specification built by FederatedQueryBuilder
            
        Returns:
            Dictionary containing query results
        """
        dataset = query_spec["dataset"]
        target_agencies = query_spec.get("target_agencies", [])
        
        # If no specific agencies provided, query all partners with access to this dataset
        if not target_agencies:
            target_agencies = [
                agency.id for agency in self._federation.list_partners()
                if dataset in agency.allowed_datasets
            ]
        
        # Check if the local agency has access to this dataset
        # If so, add local results to the federation results
        local_results = self._execute_local_query(dataset, query_spec["query"])
        
        # Execute remote queries in parallel
        remote_results = self._execute_remote_queries(
            dataset, 
            query_spec["query"],
            target_agencies,
            query_spec.get("timeout", 30.0)
        )
        
        # Combine and process results
        combined_results = self._combine_results(local_results, remote_results)
        
        # Apply post-processing like global sorting and limiting
        processed_results = self._post_process_results(combined_results, query_spec)
        
        # Log audit event for the query
        self._federation.audit.log_event(
            event_type="FEDERATED_QUERY_EXECUTED",
            details={
                "dataset": dataset,
                "target_agencies": target_agencies,
                "result_count": len(processed_results.get("results", []))
            }
        )
        
        return processed_results
    
    def _execute_local_query(self, dataset: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute query against local agency data.
        
        Args:
            dataset: Target dataset
            query: Query specification
            
        Returns:
            Query results from local agency
        """
        # Here we would implement logic to query local data sources
        # For now, this is a placeholder
        logger.info(f"Executing local query on dataset: {dataset}")
        return {
            "agency_id": self._federation.local_agency_id,
            "dataset": dataset,
            "timestamp": datetime.now().isoformat(),
            "results": []  # Placeholder for actual results
        }
    
    def _execute_remote_queries(
        self, 
        dataset: str, 
        query: Dict[str, Any],
        target_agencies: List[str],
        timeout: float
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute queries against partner agencies.
        
        Args:
            dataset: Target dataset
            query: Query specification
            target_agencies: List of agency IDs to query
            timeout: Query timeout in seconds
            
        Returns:
            Dictionary mapping agency IDs to their results
        """
        results = {}
        
        # Create asyncio event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Create task list
        tasks = []
        for agency_id in target_agencies:
            agency = self._federation.get_partner(agency_id)
            if not agency:
                logger.warning(f"Skipping unknown agency: {agency_id}")
                continue
                
            if dataset not in agency.allowed_datasets:
                logger.warning(f"Agency {agency_id} does not have access to dataset {dataset}")
                continue
                
            task = self._query_agency(agency, dataset, query, timeout)
            tasks.append(task)
        
        # Execute all tasks and collect results
        agency_results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        
        # Process results, handling any exceptions
        for i, agency_id in enumerate(target_agencies):
            if i >= len(agency_results):
                continue
                
            result = agency_results[i]
            if isinstance(result, Exception):
                logger.error(f"Error querying agency {agency_id}: {result}")
                results[agency_id] = {
                    "agency_id": agency_id,
                    "dataset": dataset,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(result),
                    "results": []
                }
            else:
                results[agency_id] = result
        
        return results
    
    async def _query_agency(
        self, 
        agency: Agency, 
        dataset: str, 
        query: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """
        Send query to a specific agency and get results.
        
        Args:
            agency: Agency to query
            dataset: Target dataset
            query: Query specification
            timeout: Query timeout in seconds
            
        Returns:
            Query results from the agency
        """
        # This would normally make an HTTP/gRPC request to the agency's federation endpoint
        # For now, return a placeholder
        logger.info(f"Querying agency {agency.id} for dataset {dataset}")
        return {
            "agency_id": agency.id,
            "dataset": dataset,
            "timestamp": datetime.now().isoformat(),
            "results": []  # Placeholder for actual results
        }
    
    def _combine_results(
        self, 
        local_results: Dict[str, Any],
        remote_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Combine results from local and remote queries.
        
        Args:
            local_results: Results from local agency
            remote_results: Results from remote agencies
            
        Returns:
            Combined results
        """
        all_results = []
        
        # Add local results
        if local_results.get("results"):
            all_results.extend(local_results["results"])
        
        # Add remote results
        for agency_id, result in remote_results.items():
            if result.get("results"):
                all_results.extend(result["results"])
        
        return {
            "results": all_results,
            "metadata": {
                "local_agency": self._federation.local_agency_id,
                "remote_agencies": list(remote_results.keys()),
                "timestamp": datetime.now().isoformat(),
                "total_count": len(all_results)
            }
        }
    
    def _post_process_results(
        self, 
        results: Dict[str, Any],
        query_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply post-processing to combined results.
        
        Args:
            results: Combined query results
            query_spec: Original query specification
            
        Returns:
            Processed results
        """
        data = results["results"]
        
        # Apply sorting if specified
        order_by = query_spec.get("query", {}).get("order_by", [])
        if order_by:
            for sort_spec in reversed(order_by):
                field = sort_spec["field"]
                reverse = sort_spec["direction"].upper() == "DESC"
                data = sorted(data, key=lambda x: x.get(field), reverse=reverse)
        
        # Apply limit if specified
        limit = query_spec.get("max_results")
        if limit is not None and limit > 0:
            data = data[:limit]
        
        # Update results with processed data
        results["results"] = data
        results["metadata"]["processed_count"] = len(data)
        
        return results