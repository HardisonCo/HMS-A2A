"""
Resource Coordination Service

This module implements a service for coordinating resource allocation and
deployment across multiple agencies through the federation hub.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..core.federation_hub import get_federation_hub

logger = logging.getLogger(__name__)

class ResourceRequest(BaseModel):
    """Model for cross-agency resource requests"""
    request_id: str
    requesting_agency: str
    resource_type: str
    quantity: int
    priority: str = "medium"  # low, medium, high, critical
    location: Dict[str, Any]
    requested_delivery: Optional[datetime] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class ResourceAllocation(BaseModel):
    """Model for resource allocation from an agency"""
    allocation_id: str
    request_id: str
    providing_agency: str
    resource_type: str
    allocated_quantity: int
    estimated_arrival: Optional[datetime] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class ResourceCoordinationService:
    """
    Service for coordinating resource allocation across multiple agencies.
    
    This service provides capabilities for requesting resources, tracking
    allocations, and optimizing resource deployment across agency boundaries.
    """
    
    def __init__(self):
        self.federation_hub = get_federation_hub()
        self._resource_requests = {}  # Dictionary mapping request IDs to requests
        self._resource_allocations = {}  # Dictionary mapping request IDs to allocations
        logger.info("Resource Coordination Service initialized")
    
    def request_resources(self, resource_request: ResourceRequest) -> Dict[str, Any]:
        """
        Submit a resource request for coordination across agencies
        
        Args:
            resource_request: Resource request details
            
        Returns:
            Coordination results with agency allocations
        """
        logger.info(f"Processing resource request {resource_request.request_id} "
                   f"from {resource_request.requesting_agency}")
        
        # Store the request
        self._resource_requests[resource_request.request_id] = resource_request
        
        # Convert to dictionary for federation hub
        request_dict = resource_request.dict()
        
        # Submit to federation hub for coordination
        coordination_results = self.federation_hub.coordinate_resources(request_dict)
        
        # Process and store allocations
        allocations = []
        for agency_id, allocation in coordination_results.get("allocations", {}).items():
            allocation_id = f"{resource_request.request_id}-{agency_id}"
            
            resource_allocation = ResourceAllocation(
                allocation_id=allocation_id,
                request_id=resource_request.request_id,
                providing_agency=agency_id,
                resource_type=resource_request.resource_type,
                allocated_quantity=allocation.get("allocated_quantity", 0),
                estimated_arrival=allocation.get("estimated_arrival"),
                details=allocation.get("details", {})
            )
            
            # Store the allocation
            if resource_request.request_id not in self._resource_allocations:
                self._resource_allocations[resource_request.request_id] = []
            
            self._resource_allocations[resource_request.request_id].append(resource_allocation)
            allocations.append(resource_allocation.dict())
        
        # Return the coordination results
        return {
            "request": resource_request.dict(),
            "allocations": allocations,
            "total_allocated": coordination_results.get("total_allocated", 0)
        }
    
    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get the status of a resource request including allocations
        
        Args:
            request_id: Resource request identifier
            
        Returns:
            Status of the resource request and allocations
        """
        if request_id not in self._resource_requests:
            return {"error": f"Request {request_id} not found"}
        
        request = self._resource_requests[request_id]
        allocations = self._resource_allocations.get(request_id, [])
        
        total_allocated = sum(allocation.allocated_quantity for allocation in allocations)
        fulfillment_percentage = (total_allocated / request.quantity) * 100 if request.quantity > 0 else 0
        
        return {
            "request": request.dict(),
            "allocations": [allocation.dict() for allocation in allocations],
            "total_allocated": total_allocated,
            "fulfillment_percentage": fulfillment_percentage,
            "status": "fulfilled" if total_allocated >= request.quantity else "partial"
        }
    
    def get_active_requests(self, agency_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get active resource requests with optional agency filter
        
        Args:
            agency_id: Optional agency identifier to filter requests
            
        Returns:
            List of active resource requests
        """
        active_requests = []
        
        for request_id, request in self._resource_requests.items():
            # Skip if filtering by agency and this request is not from that agency
            if agency_id and request.requesting_agency != agency_id:
                continue
            
            # Get allocations for this request
            allocations = self._resource_allocations.get(request_id, [])
            total_allocated = sum(allocation.allocated_quantity for allocation in allocations)
            
            # Skip if the request is fully fulfilled
            if total_allocated >= request.quantity:
                continue
            
            # Add request with allocation summary
            active_requests.append({
                "request": request.dict(),
                "total_allocated": total_allocated,
                "still_needed": request.quantity - total_allocated,
                "allocations_count": len(allocations)
            })
        
        return active_requests
    
    def create_resource_request(self,
                               requesting_agency: str,
                               resource_type: str,
                               quantity: int,
                               location: Dict[str, Any],
                               priority: str = "medium",
                               requested_delivery: Optional[datetime] = None,
                               details: Optional[Dict[str, Any]] = None) -> ResourceRequest:
        """
        Create a new resource request with automatic ID generation
        
        Args:
            requesting_agency: Agency requesting resources
            resource_type: Type of resource requested
            quantity: Quantity of resources requested
            location: Location details
            priority: Priority level
            requested_delivery: Optional requested delivery time
            details: Optional additional details
            
        Returns:
            Created ResourceRequest object
        """
        # Generate a unique request ID
        request_id = f"{requesting_agency}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create the resource request
        resource_request = ResourceRequest(
            request_id=request_id,
            requesting_agency=requesting_agency,
            resource_type=resource_type,
            quantity=quantity,
            priority=priority,
            location=location,
            requested_delivery=requested_delivery,
            details=details or {},
            timestamp=datetime.now()
        )
        
        return resource_request