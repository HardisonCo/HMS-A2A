"""
Resource models for FEMA implementation.
Defines domain models for resource management, deployment, and allocation.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from agency_implementation.foundation.base_models.base import BaseModel, GeoLocation, Address, ContactInfo
from agency_implementation.fema.models.base import ResourceType, ResourceStatus


class Resource(BaseModel):
    """
    Emergency resource available for deployment.
    Represents a physical or human resource that can be deployed in response to a disaster.
    """
    
    def __init__(
        self,
        resource_name: str,
        resource_type: str,
        status: str = "AVAILABLE",
        current_location: Dict[str, Any] = None,
        home_location: Dict[str, Any] = None,
        capabilities: List[str] = None,
        capacity: Dict[str, Any] = None,
        jurisdiction: str = None,
        owning_agency: str = None,
        deployment_time: int = None,  # Time in minutes to deploy
        cost_per_day: float = None,
        contact_info: Dict[str, Any] = None,
        requirements: Dict[str, Any] = None,
        last_maintenance: str = None,
        expiration: str = None,
        **kwargs
    ):
        """Initialize resource"""
        super().__init__(**kwargs)
        self.resource_name = resource_name
        self.resource_type = resource_type
        self.status = status
        self.current_location = GeoLocation.from_dict(current_location) if isinstance(current_location, dict) else current_location
        self.home_location = GeoLocation.from_dict(home_location) if isinstance(home_location, dict) else home_location
        self.capabilities = capabilities or []
        self.capacity = capacity or {}
        self.jurisdiction = jurisdiction
        self.owning_agency = owning_agency
        self.deployment_time = deployment_time
        self.cost_per_day = cost_per_day
        self.contact_info = ContactInfo.from_dict(contact_info) if isinstance(contact_info, dict) else contact_info
        self.requirements = requirements or {}
        self.last_maintenance = last_maintenance
        self.expiration = expiration
    
    @property
    def is_deployable(self) -> bool:
        """Check if resource is available for deployment"""
        deployable_statuses = ["AVAILABLE", "RETURNING"]
        if self.status not in deployable_statuses:
            return False
            
        if self.expiration and datetime.now() > datetime.fromisoformat(self.expiration):
            return False
            
        return True
    
    def update_status(self, new_status: str) -> None:
        """Update resource status"""
        self.status = new_status
        self.updated_at = datetime.now().isoformat()


class ResourceDeployment(BaseModel):
    """
    Resource deployment for disaster response.
    Represents the assignment of a resource to a specific disaster event or location.
    """
    
    def __init__(
        self,
        resource_id: str,
        event_id: str = None,
        deployment_location: Dict[str, Any] = None,
        assigned_mission: str = None,
        status: str = "ASSIGNED",
        deployed_at: str = None,
        expected_return: str = None,
        returned_at: str = None,
        authorizing_authority: str = None,
        priority: str = "NORMAL",
        deployment_notes: str = None,
        actual_cost: float = None,
        performance_metrics: Dict[str, Any] = None,
        **kwargs
    ):
        """Initialize resource deployment"""
        super().__init__(**kwargs)
        self.resource_id = resource_id
        self.event_id = event_id
        self.deployment_location = GeoLocation.from_dict(deployment_location) if isinstance(deployment_location, dict) else deployment_location
        self.assigned_mission = assigned_mission
        self.status = status
        self.deployed_at = deployed_at or datetime.now().isoformat()
        self.expected_return = expected_return
        self.returned_at = returned_at
        self.authorizing_authority = authorizing_authority
        self.priority = priority
        self.deployment_notes = deployment_notes
        self.actual_cost = actual_cost
        self.performance_metrics = performance_metrics or {}
    
    @property
    def is_active(self) -> bool:
        """Check if deployment is currently active"""
        return self.status in ["ASSIGNED", "DEPLOYED", "IN_TRANSIT"] and not self.returned_at
    
    @property
    def duration_hours(self) -> Optional[float]:
        """Calculate deployment duration in hours if completed"""
        if not self.returned_at:
            return None
        
        deployed = datetime.fromisoformat(self.deployed_at)
        returned = datetime.fromisoformat(self.returned_at)
        
        duration = returned - deployed
        return duration.total_seconds() / 3600
    
    def complete_deployment(self, notes: str = None) -> None:
        """Mark deployment as completed"""
        self.status = "RETURNED"
        self.returned_at = datetime.now().isoformat()
        if notes:
            self.deployment_notes = (self.deployment_notes or "") + f"\nReturn notes: {notes}"
        self.updated_at = datetime.now().isoformat()


class ResourceRequest(BaseModel):
    """
    Request for resources.
    Represents a formal request for resources in response to a disaster.
    """
    
    def __init__(
        self,
        requesting_agency: str,
        resource_type: str,
        quantity: int,
        event_id: str = None,
        deployment_location: Dict[str, Any] = None,
        requested_at: str = None,
        needed_by: str = None,
        needed_until: str = None,
        priority: str = "NORMAL",
        request_status: str = "PENDING",
        mission_details: str = None,
        special_requirements: Dict[str, Any] = None,
        approved_by: str = None,
        approved_at: str = None,
        denial_reason: str = None,
        request_notes: str = None,
        assigned_resources: List[str] = None,
        **kwargs
    ):
        """Initialize resource request"""
        super().__init__(**kwargs)
        self.requesting_agency = requesting_agency
        self.resource_type = resource_type
        self.quantity = quantity
        self.event_id = event_id
        self.deployment_location = GeoLocation.from_dict(deployment_location) if isinstance(deployment_location, dict) else deployment_location
        self.requested_at = requested_at or datetime.now().isoformat()
        self.needed_by = needed_by
        self.needed_until = needed_until
        self.priority = priority
        self.request_status = request_status
        self.mission_details = mission_details
        self.special_requirements = special_requirements or {}
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.denial_reason = denial_reason
        self.request_notes = request_notes
        self.assigned_resources = assigned_resources or []
    
    def approve_request(self, approver: str, notes: str = None) -> None:
        """Approve the resource request"""
        self.request_status = "APPROVED"
        self.approved_by = approver
        self.approved_at = datetime.now().isoformat()
        if notes:
            self.request_notes = (self.request_notes or "") + f"\nApproval notes: {notes}"
        self.updated_at = datetime.now().isoformat()
    
    def deny_request(self, reason: str, notes: str = None) -> None:
        """Deny the resource request"""
        self.request_status = "DENIED"
        self.denial_reason = reason
        if notes:
            self.request_notes = (self.request_notes or "") + f"\nDenial notes: {notes}"
        self.updated_at = datetime.now().isoformat()
    
    def assign_resource(self, resource_id: str) -> None:
        """Assign a resource to fulfill this request"""
        if not self.assigned_resources:
            self.assigned_resources = []
            
        if resource_id not in self.assigned_resources:
            self.assigned_resources.append(resource_id)
            
        # Update status if all requested resources are assigned
        if len(self.assigned_resources) >= self.quantity:
            self.request_status = "FULFILLED"
            
        self.updated_at = datetime.now().isoformat()


class ResourceAllocationPlan(BaseModel):
    """
    Resource allocation plan for disaster response.
    Represents a strategic plan for allocating resources across multiple disaster areas.
    """
    
    def __init__(
        self,
        plan_name: str,
        event_id: str = None,
        created_at: str = None,
        effective_from: str = None,
        effective_until: str = None,
        status: str = "DRAFT",
        allocation_strategy: str = None,
        priority_areas: List[Dict[str, Any]] = None,
        resource_allocations: List[Dict[str, Any]] = None,
        constraints: Dict[str, Any] = None,
        objectives: List[str] = None,
        approval_status: str = "PENDING",
        approved_by: str = None,
        approved_at: str = None,
        performance_metrics: Dict[str, Any] = None,
        plan_notes: str = None,
        **kwargs
    ):
        """Initialize resource allocation plan"""
        super().__init__(**kwargs)
        self.plan_name = plan_name
        self.event_id = event_id
        self.created_at = created_at or datetime.now().isoformat()
        self.effective_from = effective_from
        self.effective_until = effective_until
        self.status = status
        self.allocation_strategy = allocation_strategy
        self.priority_areas = priority_areas or []
        self.resource_allocations = resource_allocations or []
        self.constraints = constraints or {}
        self.objectives = objectives or []
        self.approval_status = approval_status
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.performance_metrics = performance_metrics or {}
        self.plan_notes = plan_notes
    
    def approve_plan(self, approver: str) -> None:
        """Approve the allocation plan"""
        self.approval_status = "APPROVED"
        self.approved_by = approver
        self.approved_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def activate_plan(self) -> None:
        """Activate the allocation plan"""
        if self.approval_status != "APPROVED":
            raise ValueError("Cannot activate plan that has not been approved")
            
        self.status = "ACTIVE"
        if not self.effective_from:
            self.effective_from = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def deactivate_plan(self, reason: str = None) -> None:
        """Deactivate the allocation plan"""
        self.status = "INACTIVE"
        if reason:
            self.plan_notes = (self.plan_notes or "") + f"\nDeactivation reason: {reason}"
        self.updated_at = datetime.now().isoformat()
    
    @property
    def is_active(self) -> bool:
        """Check if plan is currently active"""
        if self.status != "ACTIVE":
            return False
            
        now = datetime.now()
        
        if self.effective_from and now < datetime.fromisoformat(self.effective_from):
            return False
            
        if self.effective_until and now > datetime.fromisoformat(self.effective_until):
            return False
            
        return True