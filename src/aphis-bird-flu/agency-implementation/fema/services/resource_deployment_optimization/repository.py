"""
Repository implementations for Resource Deployment Optimization service.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import os

from agency_implementation.foundation.base_models.base import Repository
from agency_implementation.fema.models.resource import (
    Resource, ResourceDeployment, ResourceRequest, ResourceAllocationPlan
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceRepository(Repository[Resource]):
    """Repository for managing resources"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "resources"
    
    def get_by_id(self, entity_id: str) -> Optional[Resource]:
        """Get a resource by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return Resource.from_dict(data)
    
    def get_all(self) -> List[Resource]:
        """Get all resources"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [Resource.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: Resource) -> Resource:
        """Create a new resource"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created resource: {entity.id}")
        
        return entity
    
    def update(self, entity: Resource) -> Resource:
        """Update an existing resource"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated resource: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a resource by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted resource: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[Resource]:
        """Find resources matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(Resource.from_dict(data))
                
        return results
    
    def find_by_type(self, resource_type: str) -> List[Resource]:
        """Find resources by type"""
        return self.find({"resource_type": resource_type})
    
    def find_by_status(self, status: str) -> List[Resource]:
        """Find resources by status"""
        return self.find({"status": status})
    
    def find_by_jurisdiction(self, jurisdiction: str) -> List[Resource]:
        """Find resources by jurisdiction"""
        return self.find({"jurisdiction": jurisdiction})
    
    def find_available_resources(self) -> List[Resource]:
        """Find available resources"""
        resources = self.find_by_status("AVAILABLE")
        
        # Check expiration dates
        now = datetime.now().isoformat()
        return [r for r in resources if not hasattr(r, 'expiration') or not r.expiration or r.expiration > now]
    
    def find_deployable_resources(self) -> List[Resource]:
        """Find deployable resources (available or returning)"""
        available = self.find_by_status("AVAILABLE")
        returning = self.find_by_status("RETURNING")
        
        # Combine lists
        deployable = available + returning
        
        # Check expiration dates
        now = datetime.now().isoformat()
        return [r for r in deployable if not hasattr(r, 'expiration') or not r.expiration or r.expiration > now]


class ResourceDeploymentRepository(Repository[ResourceDeployment]):
    """Repository for managing resource deployments"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "resource_deployments"
    
    def get_by_id(self, entity_id: str) -> Optional[ResourceDeployment]:
        """Get a resource deployment by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return ResourceDeployment.from_dict(data)
    
    def get_all(self) -> List[ResourceDeployment]:
        """Get all resource deployments"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [ResourceDeployment.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: ResourceDeployment) -> ResourceDeployment:
        """Create a new resource deployment"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created resource deployment: {entity.id}")
        
        return entity
    
    def update(self, entity: ResourceDeployment) -> ResourceDeployment:
        """Update an existing resource deployment"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated resource deployment: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a resource deployment by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted resource deployment: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[ResourceDeployment]:
        """Find resource deployments matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(ResourceDeployment.from_dict(data))
                
        return results
    
    def find_by_resource_id(self, resource_id: str) -> List[ResourceDeployment]:
        """Find deployments for a specific resource"""
        return self.find({"resource_id": resource_id})
    
    def find_by_event_id(self, event_id: str) -> List[ResourceDeployment]:
        """Find deployments for a specific event"""
        return self.find({"event_id": event_id})
    
    def find_by_status(self, status: str) -> List[ResourceDeployment]:
        """Find deployments by status"""
        return self.find({"status": status})
    
    def find_active_deployments(self) -> List[ResourceDeployment]:
        """Find active deployments"""
        active_statuses = ["ASSIGNED", "DEPLOYED", "IN_TRANSIT"]
        
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            if 'status' in data and data['status'] in active_statuses and ('returned_at' not in data or not data['returned_at']):
                results.append(ResourceDeployment.from_dict(data))
                
        return results


class ResourceRequestRepository(Repository[ResourceRequest]):
    """Repository for managing resource requests"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "resource_requests"
    
    def get_by_id(self, entity_id: str) -> Optional[ResourceRequest]:
        """Get a resource request by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return ResourceRequest.from_dict(data)
    
    def get_all(self) -> List[ResourceRequest]:
        """Get all resource requests"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [ResourceRequest.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: ResourceRequest) -> ResourceRequest:
        """Create a new resource request"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created resource request: {entity.id}")
        
        return entity
    
    def update(self, entity: ResourceRequest) -> ResourceRequest:
        """Update an existing resource request"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated resource request: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a resource request by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted resource request: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[ResourceRequest]:
        """Find resource requests matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(ResourceRequest.from_dict(data))
                
        return results
    
    def find_by_agency(self, requesting_agency: str) -> List[ResourceRequest]:
        """Find requests from a specific agency"""
        return self.find({"requesting_agency": requesting_agency})
    
    def find_by_resource_type(self, resource_type: str) -> List[ResourceRequest]:
        """Find requests for a specific resource type"""
        return self.find({"resource_type": resource_type})
    
    def find_by_event_id(self, event_id: str) -> List[ResourceRequest]:
        """Find requests for a specific event"""
        return self.find({"event_id": event_id})
    
    def find_by_status(self, request_status: str) -> List[ResourceRequest]:
        """Find requests by status"""
        return self.find({"request_status": request_status})
    
    def find_by_priority(self, priority: str) -> List[ResourceRequest]:
        """Find requests by priority"""
        return self.find({"priority": priority})
    
    def find_pending_requests(self) -> List[ResourceRequest]:
        """Find pending resource requests"""
        return self.find({"request_status": "PENDING"})
    
    def find_approved_requests(self) -> List[ResourceRequest]:
        """Find approved but unfulfilled resource requests"""
        requests = self.find({"request_status": "APPROVED"})
        
        # Filter for unfulfilled requests
        return [r for r in requests if not hasattr(r, 'assigned_resources') or len(r.assigned_resources) < r.quantity]


class ResourceAllocationPlanRepository(Repository[ResourceAllocationPlan]):
    """Repository for managing resource allocation plans"""
    
    def __init__(self, data_store=None):
        """Initialize with optional data store"""
        self.data_store = data_store or {}
        self.collection_name = "resource_allocation_plans"
    
    def get_by_id(self, entity_id: str) -> Optional[ResourceAllocationPlan]:
        """Get a resource allocation plan by ID"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        data = self.data_store[self.collection_name].get(entity_id)
        
        if not data:
            return None
            
        return ResourceAllocationPlan.from_dict(data)
    
    def get_all(self) -> List[ResourceAllocationPlan]:
        """Get all resource allocation plans"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        return [ResourceAllocationPlan.from_dict(data) for data in self.data_store[self.collection_name].values()]
    
    def create(self, entity: ResourceAllocationPlan) -> ResourceAllocationPlan:
        """Create a new resource allocation plan"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Created resource allocation plan: {entity.id}")
        
        return entity
    
    def update(self, entity: ResourceAllocationPlan) -> ResourceAllocationPlan:
        """Update an existing resource allocation plan"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
            
        self.data_store[self.collection_name][entity.id] = entity.to_dict()
        logger.info(f"Updated resource allocation plan: {entity.id}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete a resource allocation plan by ID"""
        if self.collection_name not in self.data_store:
            return False
            
        if entity_id not in self.data_store[self.collection_name]:
            return False
            
        del self.data_store[self.collection_name][entity_id]
        logger.info(f"Deleted resource allocation plan: {entity_id}")
        
        return True
    
    def find(self, criteria: Dict[str, Any]) -> List[ResourceAllocationPlan]:
        """Find resource allocation plans matching criteria"""
        if self.collection_name not in self.data_store:
            return []
            
        results = []
        
        for data in self.data_store[self.collection_name].values():
            match = True
            
            for key, value in criteria.items():
                if key not in data or data[key] != value:
                    match = False
                    break
                    
            if match:
                results.append(ResourceAllocationPlan.from_dict(data))
                
        return results
    
    def find_by_event_id(self, event_id: str) -> List[ResourceAllocationPlan]:
        """Find plans for a specific event"""
        return self.find({"event_id": event_id})
    
    def find_by_status(self, status: str) -> List[ResourceAllocationPlan]:
        """Find plans by status"""
        return self.find({"status": status})
    
    def find_by_approval_status(self, approval_status: str) -> List[ResourceAllocationPlan]:
        """Find plans by approval status"""
        return self.find({"approval_status": approval_status})
    
    def find_active_plans(self) -> List[ResourceAllocationPlan]:
        """Find active allocation plans"""
        plans = self.find({"status": "ACTIVE"})
        
        # Filter by effective dates
        now = datetime.now().isoformat()
        
        return [
            p for p in plans if 
            (not hasattr(p, 'effective_from') or not p.effective_from or p.effective_from <= now) and 
            (not hasattr(p, 'effective_until') or not p.effective_until or p.effective_until >= now)
        ]