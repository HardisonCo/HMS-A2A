"""
Resource Deployment Optimization Service for the FEMA implementation.

This service provides functionality for optimizing the deployment of resources during
disaster response, including resource management, deployment tracking, 
request processing, and allocation planning.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging
import uuid
import json
import math

from agency_implementation.fema.models.resource import (
    Resource, ResourceDeployment, ResourceRequest, ResourceAllocationPlan
)
from agency_implementation.fema.models.base import (
    ResourceType, ResourceStatus
)
from .repository import (
    ResourceRepository, ResourceDeploymentRepository, 
    ResourceRequestRepository, ResourceAllocationPlanRepository
)
from .adapters import (
    InventorySystemAdapter, DeploymentTrackingAdapter, OptimizationEngineAdapter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceDeploymentOptimizationService:
    """
    Service for resource deployment optimization.
    
    This service provides functionality for:
    1. Resource management (inventory, status tracking)
    2. Resource deployment (assignment, tracking, completion)
    3. Resource request processing (submission, approval, fulfillment)
    4. Resource allocation planning (optimization, strategy formulation)
    """
    
    def __init__(
        self,
        resource_repository: ResourceRepository,
        resource_deployment_repository: ResourceDeploymentRepository,
        resource_request_repository: ResourceRequestRepository,
        resource_allocation_plan_repository: ResourceAllocationPlanRepository,
        inventory_adapter: Optional[InventorySystemAdapter] = None,
        deployment_adapter: Optional[DeploymentTrackingAdapter] = None,
        optimization_adapter: Optional[OptimizationEngineAdapter] = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the service.
        
        Args:
            resource_repository: Repository for resources
            resource_deployment_repository: Repository for resource deployments
            resource_request_repository: Repository for resource requests
            resource_allocation_plan_repository: Repository for allocation plans
            inventory_adapter: Adapter for external inventory systems
            deployment_adapter: Adapter for deployment tracking systems
            optimization_adapter: Adapter for optimization engines
            config: Service configuration
        """
        self.resource_repository = resource_repository
        self.resource_deployment_repository = resource_deployment_repository
        self.resource_request_repository = resource_request_repository
        self.resource_allocation_plan_repository = resource_allocation_plan_repository
        self.inventory_adapter = inventory_adapter
        self.deployment_adapter = deployment_adapter
        self.optimization_adapter = optimization_adapter
        self.config = config or {}
        
        # Initialize deployment constraints
        self.deployment_constraints = self.config.get('deployment_constraints', {
            'max_distance': 500,  # Maximum deployment distance in km
            'max_deployment_time': 12,  # Maximum deployment time in hours
            'max_active_deployments_per_resource': 1,  # Maximum simultaneous deployments
            'min_resource_readiness': 0.8,  # Minimum readiness factor (0-1)
            'resource_cooldown_hours': 24  # Cooldown period between deployments
        })
        
        # Initialize optimization preferences
        self.optimization_preferences = self.config.get('optimization_preferences', {
            'method': 'multi_objective',  # Default optimization method
            'weights': {
                'priority': 0.4,
                'requirements': 0.3,
                'distance': 0.2,
                'deploy_time': 0.1
            }
        })
        
        logger.info("ResourceDeploymentOptimizationService initialized")
    
    # Resource Management Methods
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Get a resource by ID.
        
        Args:
            resource_id: The ID of the resource to retrieve
            
        Returns:
            The resource if found, None otherwise
        """
        return self.resource_repository.get_by_id(resource_id)
    
    def get_all_resources(self) -> List[Resource]:
        """
        Get all resources.
        
        Returns:
            List of all resources
        """
        return self.resource_repository.get_all()
    
    def create_resource(self, resource_data: Dict[str, Any]) -> Resource:
        """
        Create a new resource.
        
        Args:
            resource_data: Dictionary with resource data
            
        Returns:
            The created resource
            
        Raises:
            ValueError: If resource data is invalid
        """
        # Validate required fields
        required_fields = ['resource_name', 'resource_type']
        for field in required_fields:
            if field not in resource_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set status to AVAILABLE if not specified
        if 'status' not in resource_data:
            resource_data['status'] = "AVAILABLE"
        
        # Create the resource
        resource = Resource(**resource_data)
        
        # Save the resource
        created_resource = self.resource_repository.create(resource)
        
        # Update external inventory system if available
        if self.inventory_adapter:
            try:
                self.inventory_adapter.update_resource_status(
                    created_resource.id, 
                    created_resource.status, 
                    getattr(created_resource, 'current_location', None)
                )
            except Exception as e:
                logger.error(f"Error updating external inventory: {str(e)}")
        
        logger.info(f"Created new resource with ID: {created_resource.id}")
        return created_resource
    
    def update_resource(self, resource_id: str, updates: Dict[str, Any]) -> Optional[Resource]:
        """
        Update an existing resource.
        
        Args:
            resource_id: ID of the resource to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated resource or None if resource not found
        """
        # Get the resource
        resource = self.resource_repository.get_by_id(resource_id)
        if not resource:
            logger.warning(f"Resource not found for update: {resource_id}")
            return None
        
        # Update the resource
        for key, value in updates.items():
            setattr(resource, key, value)
            
        # Update timestamp
        resource.updated_at = datetime.now().isoformat()
        
        # Save the updated resource
        updated_resource = self.resource_repository.update(resource)
        
        # Update external inventory system if available
        if self.inventory_adapter and 'status' in updates:
            try:
                self.inventory_adapter.update_resource_status(
                    updated_resource.id, 
                    updated_resource.status, 
                    getattr(updated_resource, 'current_location', None)
                )
            except Exception as e:
                logger.error(f"Error updating external inventory: {str(e)}")
        
        logger.info(f"Updated resource with ID: {resource_id}")
        return updated_resource
    
    def update_resource_status(self, resource_id: str, status: str, location: Dict[str, Any] = None) -> Optional[Resource]:
        """
        Update the status of a resource.
        
        Args:
            resource_id: ID of the resource to update
            status: New status for the resource
            location: Optional new location for the resource
            
        Returns:
            The updated resource or None if resource not found
        """
        # Get the resource
        resource = self.resource_repository.get_by_id(resource_id)
        if not resource:
            logger.warning(f"Resource not found for status update: {resource_id}")
            return None
        
        # Prepare updates
        updates = {'status': status}
        if location:
            updates['current_location'] = location
            
        return self.update_resource(resource_id, updates)
    
    def find_resources_by_type(self, resource_type: str) -> List[Resource]:
        """
        Find resources by type.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            List of resources of the specified type
        """
        return self.resource_repository.find_by_type(resource_type)
    
    def find_resources_by_status(self, status: str) -> List[Resource]:
        """
        Find resources by status.
        
        Args:
            status: Resource status
            
        Returns:
            List of resources with the specified status
        """
        return self.resource_repository.find_by_status(status)
    
    def find_available_resources(self) -> List[Resource]:
        """
        Find available resources.
        
        Returns:
            List of available resources
        """
        return self.resource_repository.find_available_resources()
    
    def import_resources_from_inventory(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Import resources from an external inventory system.
        
        Args:
            params: Parameters for the import
            
        Returns:
            Dictionary with import results
            
        Raises:
            RuntimeError: If inventory adapter is not available
        """
        if not self.inventory_adapter:
            raise RuntimeError("Inventory system adapter not configured")
            
        params = params or {}
        logger.info(f"Importing resources with params: {params}")
        
        # Fetch resources from inventory system
        inventory_data = self.inventory_adapter.fetch_resources(**params)
        
        # Process results
        imported_count = 0
        updated_count = 0
        errors = []
        
        for record in inventory_data:
            try:
                # Convert to resource
                resource = self.inventory_adapter.convert_to_resource(record)
                if not resource:
                    errors.append(f"Failed to convert record: {record.get('id', 'unknown')}")
                    continue
                
                # Check if resource already exists
                existing_resource = self.resource_repository.get_by_id(resource.id)
                
                if existing_resource:
                    # Update existing resource
                    for key, value in resource.__dict__.items():
                        if key not in ('id', 'created_at') and value is not None:
                            setattr(existing_resource, key, value)
                            
                    existing_resource.updated_at = datetime.now().isoformat()
                    self.resource_repository.update(existing_resource)
                    updated_count += 1
                else:
                    # Create new resource
                    self.resource_repository.create(resource)
                    imported_count += 1
                
            except Exception as e:
                error_msg = f"Error processing record {record.get('id', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            'total_records': len(inventory_data),
            'imported_count': imported_count,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors[:10]  # Limit error list
        }
        
        logger.info(f"Inventory import complete: {imported_count} resources imported, {updated_count} updated, {len(errors)} errors")
        return result
    
    # Deployment Management Methods
    
    def get_deployment(self, deployment_id: str) -> Optional[ResourceDeployment]:
        """
        Get a resource deployment by ID.
        
        Args:
            deployment_id: The ID of the deployment to retrieve
            
        Returns:
            The deployment if found, None otherwise
        """
        return self.resource_deployment_repository.get_by_id(deployment_id)
    
    def get_all_deployments(self) -> List[ResourceDeployment]:
        """
        Get all resource deployments.
        
        Returns:
            List of all deployments
        """
        return self.resource_deployment_repository.get_all()
    
    def create_deployment(self, deployment_data: Dict[str, Any]) -> ResourceDeployment:
        """
        Create a new resource deployment.
        
        Args:
            deployment_data: Dictionary with deployment data
            
        Returns:
            The created deployment
            
        Raises:
            ValueError: If deployment data is invalid or resource is unavailable
        """
        # Validate required fields
        required_fields = ['resource_id', 'deployment_location']
        for field in required_fields:
            if field not in deployment_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set status to ASSIGNED if not specified
        if 'status' not in deployment_data:
            deployment_data['status'] = "ASSIGNED"
            
        # Set deployed_at if not specified
        if 'deployed_at' not in deployment_data:
            deployment_data['deployed_at'] = datetime.now().isoformat()
            
        # Check if resource is available
        resource_id = deployment_data['resource_id']
        resource = self.resource_repository.get_by_id(resource_id)
        
        if not resource:
            raise ValueError(f"Resource not found: {resource_id}")
            
        if not resource.is_deployable:
            raise ValueError(f"Resource {resource_id} is not deployable (current status: {resource.status})")
            
        # Check if resource is already deployed
        active_deployments = self.resource_deployment_repository.find_by_resource_id(resource_id)
        active_deployments = [d for d in active_deployments if d.is_active]
        
        if len(active_deployments) >= self.deployment_constraints['max_active_deployments_per_resource']:
            raise ValueError(f"Resource {resource_id} has reached maximum active deployments")
        
        # Create the deployment
        deployment = ResourceDeployment(**deployment_data)
        
        # Save the deployment
        created_deployment = self.resource_deployment_repository.create(deployment)
        
        # Update resource status
        self.update_resource_status(resource_id, "ASSIGNED")
        
        # Register with external deployment tracking system if available
        if self.deployment_adapter:
            try:
                self.deployment_adapter.register_deployment(created_deployment)
            except Exception as e:
                logger.error(f"Error registering with external deployment system: {str(e)}")
        
        logger.info(f"Created new deployment with ID: {created_deployment.id}")
        return created_deployment
    
    def update_deployment(self, deployment_id: str, updates: Dict[str, Any]) -> Optional[ResourceDeployment]:
        """
        Update an existing resource deployment.
        
        Args:
            deployment_id: ID of the deployment to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated deployment or None if deployment not found
        """
        # Get the deployment
        deployment = self.resource_deployment_repository.get_by_id(deployment_id)
        if not deployment:
            logger.warning(f"Deployment not found for update: {deployment_id}")
            return None
        
        # Check if status is changing
        status_changed = 'status' in updates and updates['status'] != deployment.status
        old_status = deployment.status
        
        # Update the deployment
        for key, value in updates.items():
            setattr(deployment, key, value)
            
        # Update timestamp
        deployment.updated_at = datetime.now().isoformat()
        
        # Save the updated deployment
        updated_deployment = self.resource_deployment_repository.update(deployment)
        
        # Update resource status if deployment status changed
        if status_changed:
            resource_id = deployment.resource_id
            new_status = updates['status']
            
            # Map deployment status to resource status
            status_map = {
                "ASSIGNED": "ASSIGNED",
                "DEPLOYED": "DEPLOYED",
                "IN_TRANSIT": "IN_TRANSIT",
                "RETURNING": "RETURNING",
                "RETURNED": "AVAILABLE"
            }
            
            if new_status in status_map:
                self.update_resource_status(resource_id, status_map[new_status])
            
            # Update external deployment tracking system if available
            if self.deployment_adapter:
                try:
                    self.deployment_adapter.update_deployment(
                        deployment_id,
                        new_status,
                        getattr(updated_deployment, 'deployment_location', None)
                    )
                except Exception as e:
                    logger.error(f"Error updating external deployment system: {str(e)}")
        
        logger.info(f"Updated deployment with ID: {deployment_id}")
        return updated_deployment
    
    def deploy_resource(self, deployment_id: str, deployment_notes: str = None) -> Optional[ResourceDeployment]:
        """
        Change a deployment from ASSIGNED to DEPLOYED.
        
        Args:
            deployment_id: ID of the deployment
            deployment_notes: Optional notes about the deployment
            
        Returns:
            The updated deployment or None if deployment not found
        """
        # Get the deployment
        deployment = self.resource_deployment_repository.get_by_id(deployment_id)
        if not deployment:
            logger.warning(f"Deployment not found: {deployment_id}")
            return None
            
        if deployment.status != "ASSIGNED":
            logger.warning(f"Deployment {deployment_id} has invalid status for deploy action: {deployment.status}")
            return deployment
            
        # Prepare updates
        updates = {'status': "DEPLOYED"}
        if deployment_notes:
            updates['deployment_notes'] = deployment_notes
            
        return self.update_deployment(deployment_id, updates)
    
    def mark_in_transit(self, deployment_id: str, origin_or_destination: str) -> Optional[ResourceDeployment]:
        """
        Mark a deployment as IN_TRANSIT to or from deployment location.
        
        Args:
            deployment_id: ID of the deployment
            origin_or_destination: "TO_SITE" or "TO_BASE" to indicate direction
            
        Returns:
            The updated deployment or None if deployment not found
        """
        # Get the deployment
        deployment = self.resource_deployment_repository.get_by_id(deployment_id)
        if not deployment:
            logger.warning(f"Deployment not found: {deployment_id}")
            return None
            
        # Validate transition
        valid_transitions = {
            "TO_SITE": ["ASSIGNED"],
            "TO_BASE": ["DEPLOYED"]
        }
        
        if origin_or_destination not in valid_transitions:
            raise ValueError(f"Invalid direction: {origin_or_destination}. Must be 'TO_SITE' or 'TO_BASE'")
            
        if deployment.status not in valid_transitions[origin_or_destination]:
            logger.warning(f"Deployment {deployment_id} has invalid status for transit action: {deployment.status}")
            return deployment
            
        # Prepare updates
        updates = {
            'status': "IN_TRANSIT",
            'transit_direction': origin_or_destination
        }
        
        return self.update_deployment(deployment_id, updates)
    
    def complete_deployment(self, deployment_id: str, performance_metrics: Dict[str, Any] = None, notes: str = None) -> Optional[ResourceDeployment]:
        """
        Complete a deployment.
        
        Args:
            deployment_id: ID of the deployment to complete
            performance_metrics: Optional performance metrics
            notes: Optional notes about the completion
            
        Returns:
            The updated deployment or None if deployment not found
        """
        # Get the deployment
        deployment = self.resource_deployment_repository.get_by_id(deployment_id)
        if not deployment:
            logger.warning(f"Deployment not found: {deployment_id}")
            return None
            
        if deployment.status == "RETURNED":
            logger.warning(f"Deployment {deployment_id} is already completed")
            return deployment
            
        # Prepare updates
        updates = {
            'status': "RETURNED",
            'returned_at': datetime.now().isoformat()
        }
        
        if performance_metrics:
            updates['performance_metrics'] = performance_metrics
            
        # Merge notes if provided
        if notes:
            if deployment.deployment_notes:
                updates['deployment_notes'] = f"{deployment.deployment_notes}\nReturn notes: {notes}"
            else:
                updates['deployment_notes'] = f"Return notes: {notes}"
        
        # Update deployment
        updated_deployment = self.update_deployment(deployment_id, updates)
        
        # Update external deployment tracking system if available
        if self.deployment_adapter:
            try:
                self.deployment_adapter.complete_deployment(
                    deployment_id,
                    updates['returned_at'],
                    performance_metrics
                )
            except Exception as e:
                logger.error(f"Error completing deployment in external system: {str(e)}")
        
        return updated_deployment
    
    def find_deployments_by_resource(self, resource_id: str) -> List[ResourceDeployment]:
        """
        Find deployments for a specific resource.
        
        Args:
            resource_id: ID of the resource
            
        Returns:
            List of deployments for the resource
        """
        return self.resource_deployment_repository.find_by_resource_id(resource_id)
    
    def find_deployments_by_event(self, event_id: str) -> List[ResourceDeployment]:
        """
        Find deployments for a specific event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            List of deployments for the event
        """
        return self.resource_deployment_repository.find_by_event_id(event_id)
    
    def find_active_deployments(self) -> List[ResourceDeployment]:
        """
        Find active deployments.
        
        Returns:
            List of active deployments
        """
        return self.resource_deployment_repository.find_active_deployments()
    
    # Request Management Methods
    
    def get_request(self, request_id: str) -> Optional[ResourceRequest]:
        """
        Get a resource request by ID.
        
        Args:
            request_id: The ID of the request to retrieve
            
        Returns:
            The request if found, None otherwise
        """
        return self.resource_request_repository.get_by_id(request_id)
    
    def get_all_requests(self) -> List[ResourceRequest]:
        """
        Get all resource requests.
        
        Returns:
            List of all requests
        """
        return self.resource_request_repository.get_all()
    
    def create_request(self, request_data: Dict[str, Any]) -> ResourceRequest:
        """
        Create a new resource request.
        
        Args:
            request_data: Dictionary with request data
            
        Returns:
            The created request
            
        Raises:
            ValueError: If request data is invalid
        """
        # Validate required fields
        required_fields = ['requesting_agency', 'resource_type', 'quantity']
        for field in required_fields:
            if field not in request_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults if not specified
        if 'requested_at' not in request_data:
            request_data['requested_at'] = datetime.now().isoformat()
            
        if 'request_status' not in request_data:
            request_data['request_status'] = "PENDING"
            
        if 'priority' not in request_data:
            request_data['priority'] = "NORMAL"
        
        # Create the request
        request = ResourceRequest(**request_data)
        
        # Save the request
        created_request = self.resource_request_repository.create(request)
        
        logger.info(f"Created new resource request with ID: {created_request.id}")
        return created_request
    
    def update_request(self, request_id: str, updates: Dict[str, Any]) -> Optional[ResourceRequest]:
        """
        Update an existing resource request.
        
        Args:
            request_id: ID of the request to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated request or None if request not found
        """
        # Get the request
        request = self.resource_request_repository.get_by_id(request_id)
        if not request:
            logger.warning(f"Request not found for update: {request_id}")
            return None
        
        # Update the request
        for key, value in updates.items():
            setattr(request, key, value)
            
        # Update timestamp
        request.updated_at = datetime.now().isoformat()
        
        # Save the updated request
        updated_request = self.resource_request_repository.update(request)
        
        logger.info(f"Updated request with ID: {request_id}")
        return updated_request
    
    def approve_request(self, request_id: str, approver: str, notes: str = None) -> Optional[ResourceRequest]:
        """
        Approve a resource request.
        
        Args:
            request_id: ID of the request to approve
            approver: Name or ID of the approver
            notes: Optional approval notes
            
        Returns:
            The updated request or None if request not found
        """
        # Get the request
        request = self.resource_request_repository.get_by_id(request_id)
        if not request:
            logger.warning(f"Request not found for approval: {request_id}")
            return None
            
        if request.request_status != "PENDING":
            logger.warning(f"Request {request_id} has invalid status for approval: {request.request_status}")
            return request
        
        # Call the request's approve method
        request.approve_request(approver, notes)
        
        # Save the updated request
        updated_request = self.resource_request_repository.update(request)
        
        logger.info(f"Approved request with ID: {request_id}")
        return updated_request
    
    def deny_request(self, request_id: str, reason: str, notes: str = None) -> Optional[ResourceRequest]:
        """
        Deny a resource request.
        
        Args:
            request_id: ID of the request to deny
            reason: Reason for denial
            notes: Optional denial notes
            
        Returns:
            The updated request or None if request not found
        """
        # Get the request
        request = self.resource_request_repository.get_by_id(request_id)
        if not request:
            logger.warning(f"Request not found for denial: {request_id}")
            return None
            
        if request.request_status != "PENDING":
            logger.warning(f"Request {request_id} has invalid status for denial: {request.request_status}")
            return request
        
        # Call the request's deny method
        request.deny_request(reason, notes)
        
        # Save the updated request
        updated_request = self.resource_request_repository.update(request)
        
        logger.info(f"Denied request with ID: {request_id}")
        return updated_request
    
    def fulfill_request(self, request_id: str, resource_ids: List[str]) -> Optional[ResourceRequest]:
        """
        Fulfill a resource request by assigning resources.
        
        Args:
            request_id: ID of the request to fulfill
            resource_ids: List of resource IDs to assign
            
        Returns:
            The updated request or None if request not found
            
        Raises:
            ValueError: If resources are unavailable or insufficient
        """
        # Get the request
        request = self.resource_request_repository.get_by_id(request_id)
        if not request:
            logger.warning(f"Request not found for fulfillment: {request_id}")
            return None
            
        if request.request_status != "APPROVED":
            raise ValueError(f"Request {request_id} must be approved before fulfillment (current status: {request.request_status})")
            
        # Check if the provided resources are sufficient
        if len(resource_ids) < request.quantity:
            raise ValueError(f"Insufficient resources provided. Request requires {request.quantity}, but only {len(resource_ids)} provided")
            
        # Check if resources are available
        for resource_id in resource_ids:
            resource = self.resource_repository.get_by_id(resource_id)
            if not resource:
                raise ValueError(f"Resource not found: {resource_id}")
                
            if not resource.is_deployable:
                raise ValueError(f"Resource {resource_id} is not deployable (current status: {resource.status})")
        
        # Assign resources to the request
        for resource_id in resource_ids:
            request.assign_resource(resource_id)
            
        # Save the updated request
        updated_request = self.resource_request_repository.update(request)
        
        # Create deployments for the assigned resources
        for resource_id in resource_ids:
            deployment_data = {
                'resource_id': resource_id,
                'event_id': request.event_id,
                'deployment_location': request.deployment_location,
                'assigned_mission': request.mission_details,
                'status': "ASSIGNED",
                'priority': request.priority,
                'authorizing_authority': request.approved_by
            }
            
            try:
                self.create_deployment(deployment_data)
            except Exception as e:
                logger.error(f"Error creating deployment for resource {resource_id}: {str(e)}")
        
        logger.info(f"Fulfilled request {request_id} with {len(resource_ids)} resources")
        return updated_request
    
    def find_requests_by_agency(self, requesting_agency: str) -> List[ResourceRequest]:
        """
        Find requests from a specific agency.
        
        Args:
            requesting_agency: Name of the requesting agency
            
        Returns:
            List of requests from the agency
        """
        return self.resource_request_repository.find_by_agency(requesting_agency)
    
    def find_requests_by_type(self, resource_type: str) -> List[ResourceRequest]:
        """
        Find requests for a specific resource type.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            List of requests for the specified resource type
        """
        return self.resource_request_repository.find_by_resource_type(resource_type)
    
    def find_requests_by_event(self, event_id: str) -> List[ResourceRequest]:
        """
        Find requests for a specific event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            List of requests for the event
        """
        return self.resource_request_repository.find_by_event_id(event_id)
    
    def find_requests_by_status(self, request_status: str) -> List[ResourceRequest]:
        """
        Find requests by status.
        
        Args:
            request_status: Request status
            
        Returns:
            List of requests with the specified status
        """
        return self.resource_request_repository.find_by_status(request_status)
    
    def find_pending_requests(self) -> List[ResourceRequest]:
        """
        Find pending resource requests.
        
        Returns:
            List of pending requests
        """
        return self.resource_request_repository.find_pending_requests()
    
    def find_approved_unfulfilled_requests(self) -> List[ResourceRequest]:
        """
        Find approved but unfulfilled resource requests.
        
        Returns:
            List of approved but unfulfilled requests
        """
        return self.resource_request_repository.find_approved_requests()
    
    # Allocation Planning Methods
    
    def get_allocation_plan(self, plan_id: str) -> Optional[ResourceAllocationPlan]:
        """
        Get a resource allocation plan by ID.
        
        Args:
            plan_id: The ID of the plan to retrieve
            
        Returns:
            The plan if found, None otherwise
        """
        return self.resource_allocation_plan_repository.get_by_id(plan_id)
    
    def get_all_allocation_plans(self) -> List[ResourceAllocationPlan]:
        """
        Get all resource allocation plans.
        
        Returns:
            List of all plans
        """
        return self.resource_allocation_plan_repository.get_all()
    
    def create_allocation_plan(self, plan_data: Dict[str, Any]) -> ResourceAllocationPlan:
        """
        Create a new resource allocation plan.
        
        Args:
            plan_data: Dictionary with plan data
            
        Returns:
            The created plan
            
        Raises:
            ValueError: If plan data is invalid
        """
        # Validate required fields
        required_fields = ['plan_name']
        for field in required_fields:
            if field not in plan_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults if not specified
        if 'created_at' not in plan_data:
            plan_data['created_at'] = datetime.now().isoformat()
            
        if 'status' not in plan_data:
            plan_data['status'] = "DRAFT"
            
        if 'approval_status' not in plan_data:
            plan_data['approval_status'] = "PENDING"
        
        # Create the plan
        plan = ResourceAllocationPlan(**plan_data)
        
        # Save the plan
        created_plan = self.resource_allocation_plan_repository.create(plan)
        
        logger.info(f"Created new allocation plan with ID: {created_plan.id}")
        return created_plan
    
    def update_allocation_plan(self, plan_id: str, updates: Dict[str, Any]) -> Optional[ResourceAllocationPlan]:
        """
        Update an existing resource allocation plan.
        
        Args:
            plan_id: ID of the plan to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated plan or None if plan not found
        """
        # Get the plan
        plan = self.resource_allocation_plan_repository.get_by_id(plan_id)
        if not plan:
            logger.warning(f"Plan not found for update: {plan_id}")
            return None
        
        # Update the plan
        for key, value in updates.items():
            setattr(plan, key, value)
            
        # Update timestamp
        plan.updated_at = datetime.now().isoformat()
        
        # Save the updated plan
        updated_plan = self.resource_allocation_plan_repository.update(plan)
        
        logger.info(f"Updated allocation plan with ID: {plan_id}")
        return updated_plan
    
    def approve_allocation_plan(self, plan_id: str, approver: str) -> Optional[ResourceAllocationPlan]:
        """
        Approve a resource allocation plan.
        
        Args:
            plan_id: ID of the plan to approve
            approver: Name or ID of the approver
            
        Returns:
            The updated plan or None if plan not found
        """
        # Get the plan
        plan = self.resource_allocation_plan_repository.get_by_id(plan_id)
        if not plan:
            logger.warning(f"Plan not found for approval: {plan_id}")
            return None
            
        if plan.approval_status != "PENDING":
            logger.warning(f"Plan {plan_id} has invalid status for approval: {plan.approval_status}")
            return plan
        
        # Call the plan's approve method
        plan.approve_plan(approver)
        
        # Save the updated plan
        updated_plan = self.resource_allocation_plan_repository.update(plan)
        
        logger.info(f"Approved allocation plan with ID: {plan_id}")
        return updated_plan
    
    def activate_allocation_plan(self, plan_id: str) -> Optional[ResourceAllocationPlan]:
        """
        Activate a resource allocation plan.
        
        Args:
            plan_id: ID of the plan to activate
            
        Returns:
            The updated plan or None if plan not found
            
        Raises:
            ValueError: If plan is not approved
        """
        # Get the plan
        plan = self.resource_allocation_plan_repository.get_by_id(plan_id)
        if not plan:
            logger.warning(f"Plan not found for activation: {plan_id}")
            return None
            
        if plan.approval_status != "APPROVED":
            raise ValueError(f"Plan {plan_id} must be approved before activation")
            
        if plan.status == "ACTIVE":
            logger.warning(f"Plan {plan_id} is already active")
            return plan
        
        # Call the plan's activate method
        plan.activate_plan()
        
        # Save the updated plan
        updated_plan = self.resource_allocation_plan_repository.update(plan)
        
        logger.info(f"Activated allocation plan with ID: {plan_id}")
        return updated_plan
    
    def deactivate_allocation_plan(self, plan_id: str, reason: str = None) -> Optional[ResourceAllocationPlan]:
        """
        Deactivate a resource allocation plan.
        
        Args:
            plan_id: ID of the plan to deactivate
            reason: Optional reason for deactivation
            
        Returns:
            The updated plan or None if plan not found
        """
        # Get the plan
        plan = self.resource_allocation_plan_repository.get_by_id(plan_id)
        if not plan:
            logger.warning(f"Plan not found for deactivation: {plan_id}")
            return None
            
        if plan.status != "ACTIVE":
            logger.warning(f"Plan {plan_id} is not active (current status: {plan.status})")
            return plan
        
        # Call the plan's deactivate method
        plan.deactivate_plan(reason)
        
        # Save the updated plan
        updated_plan = self.resource_allocation_plan_repository.update(plan)
        
        logger.info(f"Deactivated allocation plan with ID: {plan_id}")
        return updated_plan
    
    def find_plans_by_event(self, event_id: str) -> List[ResourceAllocationPlan]:
        """
        Find allocation plans for a specific event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            List of plans for the event
        """
        return self.resource_allocation_plan_repository.find_by_event_id(event_id)
    
    def find_plans_by_status(self, status: str) -> List[ResourceAllocationPlan]:
        """
        Find allocation plans by status.
        
        Args:
            status: Plan status
            
        Returns:
            List of plans with the specified status
        """
        return self.resource_allocation_plan_repository.find_by_status(status)
    
    def find_active_plans(self) -> List[ResourceAllocationPlan]:
        """
        Find active allocation plans.
        
        Returns:
            List of active plans
        """
        return self.resource_allocation_plan_repository.find_active_plans()
    
    def generate_allocation_plan(
        self, 
        event_id: str, 
        plan_name: str = None,
        resource_types: List[str] = None,
        optimization_method: str = None,
        constraints: Dict[str, Any] = None
    ) -> ResourceAllocationPlan:
        """
        Generate an optimized resource allocation plan.
        
        Args:
            event_id: ID of the event
            plan_name: Name for the plan (optional)
            resource_types: List of resource types to include (optional)
            optimization_method: Optimization method to use (optional)
            constraints: Additional constraints for optimization (optional)
            
        Returns:
            The generated allocation plan
            
        Raises:
            ValueError: If event does not have any associated requests
        """
        # Get requests for the event
        requests = self.resource_request_repository.find_by_event_id(event_id)
        
        # Filter approved requests
        approved_requests = [r for r in requests if r.request_status == "APPROVED"]
        
        if not approved_requests:
            raise ValueError(f"No approved resource requests found for event {event_id}")
            
        # Filter by resource types if specified
        if resource_types:
            approved_requests = [r for r in approved_requests if r.resource_type in resource_types]
            
        if not approved_requests:
            raise ValueError(f"No approved resource requests found for specified resource types")
            
        # Get available resources
        available_resources = self.resource_repository.find_deployable_resources()
        
        if not available_resources:
            raise ValueError("No deployable resources available")
            
        # Filter by resource types if specified
        if resource_types:
            available_resources = [r for r in available_resources if r.resource_type in resource_types]
            
        if not available_resources:
            raise ValueError(f"No deployable resources available for specified resource types")
            
        # Prepare data for optimization
        request_data = [r.to_dict() for r in approved_requests]
        resource_data = [r.to_dict() for r in available_resources]
        
        # Set optimization method
        method = optimization_method or self.optimization_preferences['method']
        
        # Combine constraints
        combined_constraints = {}
        if constraints:
            combined_constraints.update(constraints)
        if 'weights' in self.optimization_preferences:
            combined_constraints['weights'] = self.optimization_preferences['weights']
            
        # Perform optimization
        if self.optimization_adapter:
            try:
                optimization_result = self.optimization_adapter.optimize_allocation(
                    resource_data,
                    request_data,
                    method,
                    combined_constraints
                )
            except Exception as e:
                logger.error(f"Error during optimization: {str(e)}")
                raise RuntimeError(f"Optimization failed: {str(e)}")
        else:
            raise RuntimeError("Optimization adapter not configured")
            
        # Create allocation plan
        plan_name = plan_name or f"Allocation Plan for Event {event_id} - {datetime.now().strftime('%Y-%m-%d')}"
        
        allocations = optimization_result.get('allocations', [])
        
        if not allocations:
            logger.warning(f"Optimization produced no allocations for event {event_id}")
            
        # Convert optimization result to resource allocations
        resource_allocations = []
        
        for allocation in allocations:
            resource_id = allocation.get('resource_id')
            request_id = allocation.get('request_id')
            
            # Get request and resource details
            request = next((r for r in approved_requests if r.id == request_id), None)
            resource = next((r for r in available_resources if r.id == resource_id), None)
            
            if not request or not resource:
                continue
                
            # Add allocation to list
            resource_allocations.append({
                'resource_id': resource_id,
                'request_id': request_id,
                'deployment_location': allocation.get('deployment_location', request.deployment_location),
                'priority': request.priority,
                'expected_deploy_time': resource.deployment_time,
                'expected_cost': resource.cost_per_day,
                'score': allocation.get('score'),
                'notes': allocation.get('notes')
            })
        
        # Create priority areas from requests
        priority_areas = []
        for request in approved_requests:
            if hasattr(request, 'deployment_location') and request.deployment_location:
                area = {
                    'name': f"Request {request.id} Area",
                    'location': request.deployment_location,
                    'priority': request.priority,
                    'resource_types_needed': [request.resource_type]
                }
                priority_areas.append(area)
        
        # Create plan data
        plan_data = {
            'plan_name': plan_name,
            'event_id': event_id,
            'created_at': datetime.now().isoformat(),
            'status': "DRAFT",
            'allocation_strategy': method,
            'priority_areas': priority_areas,
            'resource_allocations': resource_allocations,
            'constraints': combined_constraints,
            'objectives': [
                "Minimize response time",
                "Maximize coverage of priority areas",
                "Optimize resource utilization"
            ],
            'approval_status': "PENDING",
            'performance_metrics': optimization_result.get('statistics')
        }
        
        # Create the plan
        return self.create_allocation_plan(plan_data)
    
    def execute_allocation_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute an approved and active allocation plan.
        
        Args:
            plan_id: ID of the plan to execute
            
        Returns:
            Dictionary with execution results
            
        Raises:
            ValueError: If plan is not approved or active
        """
        # Get the plan
        plan = self.resource_allocation_plan_repository.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
            
        if plan.approval_status != "APPROVED":
            raise ValueError(f"Plan {plan_id} must be approved before execution")
            
        if plan.status != "ACTIVE":
            raise ValueError(f"Plan {plan_id} must be active before execution")
            
        # Track execution results
        results = {
            'plan_id': plan_id,
            'execution_time': datetime.now().isoformat(),
            'successful_deployments': [],
            'failed_deployments': [],
            'undeployed_resources': []
        }
        
        # Process each allocation
        allocations = getattr(plan, 'resource_allocations', [])
        
        for allocation in allocations:
            resource_id = allocation.get('resource_id')
            request_id = allocation.get('request_id')
            
            # Check if resource is still available
            resource = self.resource_repository.get_by_id(resource_id)
            
            if not resource or not resource.is_deployable:
                results['failed_deployments'].append({
                    'resource_id': resource_id,
                    'request_id': request_id,
                    'reason': f"Resource unavailable (status: {getattr(resource, 'status', 'UNKNOWN')})"
                })
                continue
                
            # Create deployment
            try:
                # Get request for the allocation
                request = self.resource_request_repository.get_by_id(request_id)
                
                # Prepare deployment data
                deployment_data = {
                    'resource_id': resource_id,
                    'event_id': plan.event_id,
                    'deployment_location': allocation.get('deployment_location'),
                    'assigned_mission': request.mission_details if request else None,
                    'status': "ASSIGNED",
                    'priority': allocation.get('priority', "NORMAL"),
                    'deployment_notes': f"Allocated by plan {plan_id}",
                    'authorizing_authority': plan.approved_by
                }
                
                # Create deployment
                deployment = self.create_deployment(deployment_data)
                
                # Update request if needed
                if request and request.request_status == "APPROVED":
                    request.assign_resource(resource_id)
                    self.resource_request_repository.update(request)
                
                results['successful_deployments'].append({
                    'resource_id': resource_id,
                    'request_id': request_id,
                    'deployment_id': deployment.id
                })
                
            except Exception as e:
                results['failed_deployments'].append({
                    'resource_id': resource_id,
                    'request_id': request_id,
                    'reason': str(e)
                })
        
        # Calculate success rate
        total_allocations = len(allocations)
        successful = len(results['successful_deployments'])
        
        results['total_allocations'] = total_allocations
        results['success_rate'] = successful / total_allocations if total_allocations > 0 else 0
        
        # Update plan with execution results
        execution_metrics = {
            'execution_time': results['execution_time'],
            'allocations_attempted': total_allocations,
            'allocations_succeeded': successful,
            'success_rate': results['success_rate']
        }
        
        performance_metrics = getattr(plan, 'performance_metrics', {})
        performance_metrics['execution'] = execution_metrics
        
        self.update_allocation_plan(plan_id, {'performance_metrics': performance_metrics})
        
        logger.info(f"Executed allocation plan {plan_id}: {successful}/{total_allocations} deployments successful")
        return results
    
    # Helper Methods
    
    def calculate_deployment_cost(self, resource_id: str, days: int) -> float:
        """
        Calculate the cost of deploying a resource for a specified number of days.
        
        Args:
            resource_id: ID of the resource
            days: Number of days to deploy
            
        Returns:
            Calculated deployment cost
            
        Raises:
            ValueError: If resource not found
        """
        # Get the resource
        resource = self.resource_repository.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource not found: {resource_id}")
            
        # Get cost per day
        cost_per_day = getattr(resource, 'cost_per_day', 0)
        
        # Calculate total cost
        return cost_per_day * days
    
    def estimate_travel_time(self, resource_id: str, destination: Dict[str, Any]) -> float:
        """
        Estimate travel time for a resource to a deployment location.
        
        Args:
            resource_id: ID of the resource
            destination: Destination location
            
        Returns:
            Estimated travel time in hours
            
        Raises:
            ValueError: If resource not found
        """
        # Get the resource
        resource = self.resource_repository.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource not found: {resource_id}")
            
        # Get resource location
        resource_location = getattr(resource, 'current_location', None)
        
        # If location not available, use a default estimate
        if not resource_location or not destination:
            return 2.0  # Default estimate
            
        # Calculate distance
        lat1 = getattr(resource_location, 'latitude', 0)
        lon1 = getattr(resource_location, 'longitude', 0)
        lat2 = destination.get('latitude', 0)
        lon2 = destination.get('longitude', 0)
        
        # Simple Euclidean distance calculation
        # In a real implementation, this would use the Haversine formula or a routing service
        distance_km = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # Rough km conversion
        
        # Estimate travel time based on distance
        # Assuming average speed of 60 km/h
        travel_time_hours = distance_km / 60
        
        # Add deployment preparation time
        preparation_time = getattr(resource, 'deployment_time', 60) / 60  # Convert minutes to hours
        
        return travel_time_hours + preparation_time
    
    def get_resource_deployment_history(self, resource_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get deployment history for a resource.
        
        Args:
            resource_id: ID of the resource
            days: Number of past days to include
            
        Returns:
            List of deployment records
            
        Raises:
            ValueError: If resource not found
        """
        # Get the resource
        resource = self.resource_repository.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource not found: {resource_id}")
            
        # Get all deployments for the resource
        deployments = self.resource_deployment_repository.find_by_resource_id(resource_id)
        
        # Filter by time period
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        recent_deployments = [
            d for d in deployments 
            if hasattr(d, 'deployed_at') and d.deployed_at >= cutoff_date
        ]
        
        # Format deployment records
        history = []
        
        for deployment in recent_deployments:
            record = {
                'deployment_id': deployment.id,
                'event_id': getattr(deployment, 'event_id', None),
                'status': deployment.status,
                'deployed_at': deployment.deployed_at,
                'returned_at': getattr(deployment, 'returned_at', None),
                'duration_hours': deployment.duration_hours if hasattr(deployment, 'duration_hours') and deployment.duration_hours is not None else None,
                'priority': getattr(deployment, 'priority', None),
                'location': getattr(deployment, 'deployment_location', None)
            }
            
            history.append(record)
            
        # Sort by deployment date (newest first)
        history.sort(key=lambda x: x['deployed_at'], reverse=True)
        
        return history
    
    def calculate_deployment_statistics(self, event_id: str = None) -> Dict[str, Any]:
        """
        Calculate statistics on resource deployments.
        
        Args:
            event_id: Optional event ID to filter statistics
            
        Returns:
            Dictionary with deployment statistics
        """
        # Get deployments (filtered by event if specified)
        if event_id:
            deployments = self.resource_deployment_repository.find_by_event_id(event_id)
        else:
            deployments = self.resource_deployment_repository.get_all()
            
        # Init statistics
        stats = {
            'total_deployments': len(deployments),
            'active_deployments': 0,
            'completed_deployments': 0,
            'average_duration_hours': 0,
            'resource_type_distribution': {},
            'status_distribution': {},
            'priority_distribution': {}
        }
        
        # Count active deployments
        active_deployments = [d for d in deployments if d.is_active]
        stats['active_deployments'] = len(active_deployments)
        
        # Count completed deployments and calculate duration
        completed_deployments = [d for d in deployments if hasattr(d, 'returned_at') and d.returned_at]
        stats['completed_deployments'] = len(completed_deployments)
        
        if completed_deployments:
            total_hours = 0
            valid_durations = 0
            
            for deployment in completed_deployments:
                if hasattr(deployment, 'duration_hours') and deployment.duration_hours is not None:
                    total_hours += deployment.duration_hours
                    valid_durations += 1
                    
            if valid_durations > 0:
                stats['average_duration_hours'] = total_hours / valid_durations
        
        # Resource type distribution
        resource_ids = [d.resource_id for d in deployments]
        resources = [self.resource_repository.get_by_id(resource_id) for resource_id in resource_ids]
        resources = [r for r in resources if r is not None]
        
        for resource in resources:
            resource_type = resource.resource_type
            if resource_type not in stats['resource_type_distribution']:
                stats['resource_type_distribution'][resource_type] = 0
                
            stats['resource_type_distribution'][resource_type] += 1
            
        # Status distribution
        for deployment in deployments:
            status = deployment.status
            if status not in stats['status_distribution']:
                stats['status_distribution'][status] = 0
                
            stats['status_distribution'][status] += 1
            
        # Priority distribution
        for deployment in deployments:
            priority = getattr(deployment, 'priority', 'NORMAL')
            if priority not in stats['priority_distribution']:
                stats['priority_distribution'][priority] = 0
                
            stats['priority_distribution'][priority] += 1
            
        return stats