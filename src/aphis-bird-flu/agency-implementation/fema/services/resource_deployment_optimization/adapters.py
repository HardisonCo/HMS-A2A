"""
Adapters for the Resource Deployment Optimization service.
Integrates with external inventory systems and deployment tracking services.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import requests
from abc import ABC, abstractmethod

from agency_implementation.fema.models.resource import (
    Resource, ResourceDeployment, ResourceRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InventorySystemAdapter(ABC):
    """
    Base adapter for external inventory systems.
    Provides interface for fetching resource data from external systems.
    """
    
    @abstractmethod
    def fetch_resources(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch resource data from the inventory system.
        
        Args:
            **params: Parameters for the resource request
            
        Returns:
            List of resource records
        """
        pass
    
    @abstractmethod
    def convert_to_resource(self, record: Dict[str, Any]) -> Optional[Resource]:
        """
        Convert an inventory system record to a resource.
        
        Args:
            record: Data record from the inventory system
            
        Returns:
            Resource instance or None if conversion fails
        """
        pass
    
    @abstractmethod
    def update_resource_status(self, resource_id: str, status: str, location: Dict[str, Any] = None) -> bool:
        """
        Update resource status in the external inventory system.
        
        Args:
            resource_id: ID of the resource to update
            status: New status for the resource
            location: Optional new location for the resource
            
        Returns:
            True if update was successful, False otherwise
        """
        pass


class FEMAInventoryAdapter(InventorySystemAdapter):
    """
    Adapter for FEMA's inventory management system.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize FEMA inventory adapter.
        
        Args:
            api_url: URL for the inventory system API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.default_params = self.config.get('default_params', {})
        
        logger.info("Initialized FEMAInventoryAdapter")
    
    def fetch_resources(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch resource data from the FEMA inventory system.
        
        Args:
            **params: Parameters for the resource request
            
        Returns:
            List of resource records
            
        Raises:
            RuntimeError: If API request fails
        """
        # Combine default params with provided params
        request_params = {**self.default_params, **params}
        
        # If API is not configured, return mock data for testing
        if not self.api_url:
            logger.warning("API URL not configured, returning mock data")
            return self._get_mock_data(**request_params)
        
        try:
            # Add API key to headers if available
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.get(
                self.api_url, 
                params=request_params, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                raise RuntimeError(f"Inventory API request failed with status {response.status_code}")
                
            # Parse response
            data = response.json()
            
            # Extract records from response (adjust based on actual API response structure)
            records = data.get('resources', [])
            logger.info(f"Fetched {len(records)} resource records")
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching resource data: {str(e)}")
            raise RuntimeError(f"Failed to fetch resource data: {str(e)}")
    
    def convert_to_resource(self, record: Dict[str, Any]) -> Optional[Resource]:
        """
        Convert an inventory system record to a resource.
        
        Args:
            record: Data record from the inventory system
            
        Returns:
            Resource instance or None if conversion fails
        """
        try:
            # Extract required fields from record (adjust based on actual data structure)
            required_fields = ['id', 'name', 'type', 'status']
            for field in required_fields:
                if field not in record:
                    logger.warning(f"Missing required field '{field}' in record: {record}")
                    return None
            
            # Map record fields to resource fields
            resource_data = {
                'id': record['id'],
                'resource_name': record['name'],
                'resource_type': record['type'],
                'status': record['status'],
            }
            
            # Add optional fields if present
            optional_fields = {
                'location': 'current_location',
                'home_base': 'home_location',
                'capabilities': 'capabilities',
                'capacity': 'capacity',
                'jurisdiction': 'jurisdiction',
                'agency': 'owning_agency',
                'deploy_time': 'deployment_time',
                'cost': 'cost_per_day',
                'contact': 'contact_info',
                'requirements': 'requirements',
                'maintenance_date': 'last_maintenance',
                'expiration_date': 'expiration'
            }
            
            for src, dest in optional_fields.items():
                if src in record:
                    resource_data[dest] = record[src]
            
            # Create resource object
            resource = Resource(**resource_data)
            
            return resource
            
        except Exception as e:
            logger.error(f"Error converting inventory record: {str(e)}")
            return None
    
    def update_resource_status(self, resource_id: str, status: str, location: Dict[str, Any] = None) -> bool:
        """
        Update resource status in the FEMA inventory system.
        
        Args:
            resource_id: ID of the resource to update
            status: New status for the resource
            location: Optional new location for the resource
            
        Returns:
            True if update was successful, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info(f"Would update resource {resource_id} status to {status}")
            return True
        
        try:
            # Prepare update data
            update_data = {
                'id': resource_id,
                'status': status
            }
            
            if location:
                update_data['location'] = location
                
            # Add API key to headers if available
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.put(
                f"{self.api_url}/{resource_id}", 
                json=update_data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code not in (200, 201, 204):
                logger.error(f"API update failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"Updated resource {resource_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating resource status: {str(e)}")
            return False
    
    def _get_mock_data(self, **params) -> List[Dict[str, Any]]:
        """
        Generate mock resource data for testing.
        
        Args:
            **params: Parameters to customize mock data
            
        Returns:
            List of mock resource records
        """
        # Generate basic mock data
        mock_data = [
            {
                'id': 'res-001',
                'name': 'Mobile Emergency Response Vehicle',
                'type': 'transportation',
                'status': 'AVAILABLE',
                'location': {
                    'latitude': 38.889248,
                    'longitude': -77.050636
                },
                'home_base': {
                    'latitude': 38.889248,
                    'longitude': -77.050636
                },
                'capabilities': ['transportation', 'mobile_command', 'communications'],
                'capacity': {
                    'passengers': 6,
                    'equipment_weight': 2000
                },
                'jurisdiction': 'federal',
                'agency': 'FEMA',
                'deploy_time': 30,
                'cost': 1200.00,
                'contact': {
                    'name': 'Fleet Management',
                    'email': 'fleet@fema.example.gov',
                    'phone': '202-555-0123'
                },
                'maintenance_date': '2025-01-15T00:00:00Z',
                'expiration_date': '2026-01-01T00:00:00Z'
            },
            {
                'id': 'res-002',
                'name': 'Portable Water Purification System',
                'type': 'water',
                'status': 'AVAILABLE',
                'location': {
                    'latitude': 38.889248,
                    'longitude': -77.050636
                },
                'home_base': {
                    'latitude': 38.889248,
                    'longitude': -77.050636
                },
                'capabilities': ['water_purification', 'portable'],
                'capacity': {
                    'gallons_per_hour': 500
                },
                'jurisdiction': 'federal',
                'agency': 'FEMA',
                'deploy_time': 60,
                'cost': 500.00,
                'maintenance_date': '2025-02-20T00:00:00Z'
            },
            {
                'id': 'res-003',
                'name': 'Emergency Shelter Kit',
                'type': 'shelter',
                'status': 'AVAILABLE',
                'location': {
                    'latitude': 38.889248,
                    'longitude': -77.050636
                },
                'home_base': {
                    'latitude': 38.889248,
                    'longitude': -77.050636
                },
                'capabilities': ['temporary_shelter', 'portable'],
                'capacity': {
                    'persons': 50
                },
                'jurisdiction': 'federal',
                'agency': 'FEMA',
                'deploy_time': 120,
                'cost': 800.00
            }
        ]
        
        # Filter based on parameters
        filtered_data = mock_data
        
        if 'type' in params:
            filtered_data = [r for r in filtered_data if r['type'] == params['type']]
            
        if 'status' in params:
            filtered_data = [r for r in filtered_data if r['status'] == params['status']]
            
        if 'jurisdiction' in params:
            filtered_data = [r for r in filtered_data if r['jurisdiction'] == params['jurisdiction']]
            
        return filtered_data


class DeploymentTrackingAdapter(ABC):
    """
    Base adapter for deployment tracking systems.
    Provides interface for tracking resource deployments.
    """
    
    @abstractmethod
    def register_deployment(self, deployment: ResourceDeployment) -> bool:
        """
        Register a new deployment in the tracking system.
        
        Args:
            deployment: Deployment to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update_deployment(self, deployment_id: str, status: str, location: Dict[str, Any] = None) -> bool:
        """
        Update deployment status in the tracking system.
        
        Args:
            deployment_id: ID of the deployment to update
            status: New status for the deployment
            location: Optional new location
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def complete_deployment(self, deployment_id: str, return_date: str, performance_metrics: Dict[str, Any] = None) -> bool:
        """
        Complete a deployment in the tracking system.
        
        Args:
            deployment_id: ID of the deployment to complete
            return_date: Date when the resource returned
            performance_metrics: Optional performance metrics for the deployment
            
        Returns:
            True if completion was successful, False otherwise
        """
        pass


class FEMADeploymentAdapter(DeploymentTrackingAdapter):
    """
    Adapter for FEMA's deployment tracking system.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize FEMA deployment adapter.
        
        Args:
            api_url: URL for the deployment tracking API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        
        logger.info("Initialized FEMADeploymentAdapter")
    
    def register_deployment(self, deployment: ResourceDeployment) -> bool:
        """
        Register a new deployment in the FEMA tracking system.
        
        Args:
            deployment: Deployment to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info(f"Would register deployment for resource {deployment.resource_id}")
            return True
        
        try:
            # Prepare deployment data
            deployment_data = deployment.to_dict()
                
            # Add API key to headers if available
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.post(
                self.api_url, 
                json=deployment_data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code not in (200, 201):
                logger.error(f"API registration failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"Registered deployment for resource {deployment.resource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering deployment: {str(e)}")
            return False
    
    def update_deployment(self, deployment_id: str, status: str, location: Dict[str, Any] = None) -> bool:
        """
        Update deployment status in the FEMA tracking system.
        
        Args:
            deployment_id: ID of the deployment to update
            status: New status for the deployment
            location: Optional new location
            
        Returns:
            True if update was successful, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info(f"Would update deployment {deployment_id} status to {status}")
            return True
        
        try:
            # Prepare update data
            update_data = {
                'id': deployment_id,
                'status': status
            }
            
            if location:
                update_data['deployment_location'] = location
                
            # Add API key to headers if available
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.put(
                f"{self.api_url}/{deployment_id}", 
                json=update_data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code not in (200, 201, 204):
                logger.error(f"API update failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"Updated deployment {deployment_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating deployment status: {str(e)}")
            return False
    
    def complete_deployment(self, deployment_id: str, return_date: str, performance_metrics: Dict[str, Any] = None) -> bool:
        """
        Complete a deployment in the FEMA tracking system.
        
        Args:
            deployment_id: ID of the deployment to complete
            return_date: Date when the resource returned
            performance_metrics: Optional performance metrics for the deployment
            
        Returns:
            True if completion was successful, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info(f"Would complete deployment {deployment_id} with return date {return_date}")
            return True
        
        try:
            # Prepare completion data
            completion_data = {
                'id': deployment_id,
                'status': 'RETURNED',
                'returned_at': return_date
            }
            
            if performance_metrics:
                completion_data['performance_metrics'] = performance_metrics
                
            # Add API key to headers if available
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.put(
                f"{self.api_url}/{deployment_id}/complete", 
                json=completion_data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code not in (200, 201, 204):
                logger.error(f"API completion failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"Completed deployment {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing deployment: {str(e)}")
            return False


class OptimizationEngineAdapter:
    """
    Adapter for resource allocation optimization engines.
    Used to optimize resource allocation decisions.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize optimization engine adapter.
        
        Args:
            api_url: URL for the optimization engine API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.optimization_methods = {
            'greedy': self._greedy_allocation,
            'priority': self._priority_based_allocation,
            'distance': self._distance_based_allocation,
            'multi_objective': self._multi_objective_allocation
        }
        
        logger.info("Initialized OptimizationEngineAdapter")
    
    def optimize_allocation(
        self, 
        resources: List[Dict[str, Any]], 
        requests: List[Dict[str, Any]], 
        method: str = 'multi_objective',
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Optimize resource allocation based on requests and available resources.
        
        Args:
            resources: List of available resources
            requests: List of resource requests
            method: Optimization method to use
            constraints: Optional constraints for the optimization
            
        Returns:
            Optimized allocation plan
            
        Raises:
            ValueError: If method is invalid
        """
        # Validate method
        if method not in self.optimization_methods:
            raise ValueError(f"Invalid optimization method: {method}. Valid methods: {', '.join(self.optimization_methods.keys())}")
            
        # If API is not configured, use local implementation
        if not self.api_url:
            logger.info(f"Using local {method} optimization (API not configured)")
            return self.optimization_methods[method](resources, requests, constraints)
        
        try:
            # Prepare optimization request
            optimization_data = {
                'resources': resources,
                'requests': requests,
                'method': method,
                'constraints': constraints or {}
            }
                
            # Add API key to headers if available
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.post(
                self.api_url, 
                json=optimization_data, 
                headers=headers, 
                timeout=60  # Longer timeout for optimization
            )
            
            if response.status_code != 200:
                logger.error(f"API optimization failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                logger.info("Falling back to local optimization")
                return self.optimization_methods[method](resources, requests, constraints)
                
            # Parse response
            result = response.json()
            logger.info(f"Received optimization result with {len(result.get('allocations', []))} allocations")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in API optimization: {str(e)}")
            logger.info("Falling back to local optimization")
            return self.optimization_methods[method](resources, requests, constraints)
    
    def _greedy_allocation(
        self, 
        resources: List[Dict[str, Any]], 
        requests: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Simple greedy allocation algorithm.
        Assigns resources to requests in order of request priority.
        
        Args:
            resources: List of available resources
            requests: List of resource requests
            constraints: Optional constraints for the optimization
            
        Returns:
            Allocation plan
        """
        # Sort requests by priority (high, medium, low)
        priority_order = {'HIGH': 0, 'URGENT': 0, 'MEDIUM': 1, 'NORMAL': 1, 'LOW': 2}
        
        sorted_requests = sorted(
            requests, 
            key=lambda r: priority_order.get(r.get('priority', 'NORMAL').upper(), 1)
        )
        
        # Track allocations and used resources
        allocations = []
        used_resources = set()
        
        for request in sorted_requests:
            request_id = request.get('id')
            request_type = request.get('resource_type')
            request_quantity = request.get('quantity', 1)
            request_location = request.get('deployment_location')
            
            # Find matching resources
            matching_resources = [
                r for r in resources
                if r.get('resource_type') == request_type
                and r.get('id') not in used_resources
            ]
            
            # Allocate up to requested quantity
            allocated_resources = []
            for resource in matching_resources[:request_quantity]:
                resource_id = resource.get('id')
                used_resources.add(resource_id)
                allocated_resources.append(resource_id)
                
                allocations.append({
                    'request_id': request_id,
                    'resource_id': resource_id,
                    'deployment_location': request_location
                })
                
                # Break if we've met the request quantity
                if len(allocated_resources) >= request_quantity:
                    break
        
        return {
            'method': 'greedy',
            'allocations': allocations,
            'unallocated_requests': [
                r.get('id') for r in sorted_requests 
                if len([a for a in allocations if a['request_id'] == r.get('id')]) < r.get('quantity', 1)
            ],
            'unused_resources': [
                r.get('id') for r in resources 
                if r.get('id') not in used_resources
            ]
        }
    
    def _priority_based_allocation(
        self, 
        resources: List[Dict[str, Any]], 
        requests: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Priority-based allocation algorithm.
        Allocates resources based on request priority and resource suitability.
        
        Args:
            resources: List of available resources
            requests: List of resource requests
            constraints: Optional constraints for the optimization
            
        Returns:
            Allocation plan
        """
        # Sort requests by priority (high, medium, low)
        priority_order = {'HIGH': 0, 'URGENT': 0, 'MEDIUM': 1, 'NORMAL': 1, 'LOW': 2}
        
        sorted_requests = sorted(
            requests, 
            key=lambda r: priority_order.get(r.get('priority', 'NORMAL').upper(), 1)
        )
        
        # Track allocations and used resources
        allocations = []
        used_resources = set()
        
        for request in sorted_requests:
            request_id = request.get('id')
            request_type = request.get('resource_type')
            request_quantity = request.get('quantity', 1)
            request_location = request.get('deployment_location')
            special_requirements = request.get('special_requirements', {})
            
            # Find matching resources, prioritizing those with matching capabilities
            matching_resources = []
            
            for resource in resources:
                if resource.get('resource_type') != request_type or resource.get('id') in used_resources:
                    continue
                    
                # Calculate a score for this resource
                score = 0
                
                # Check capabilities match
                if 'capabilities' in resource and 'required_capabilities' in special_requirements:
                    resource_capabilities = set(resource.get('capabilities', []))
                    required_capabilities = set(special_requirements.get('required_capabilities', []))
                    
                    if required_capabilities.issubset(resource_capabilities):
                        # Bonus points for exact match
                        if resource_capabilities == required_capabilities:
                            score += 10
                        else:
                            score += 5
                    else:
                        # Skip if required capabilities aren't met
                        continue
                
                # Check capacity
                if 'capacity' in resource and 'minimum_capacity' in special_requirements:
                    resource_capacity = resource.get('capacity', {})
                    minimum_capacity = special_requirements.get('minimum_capacity', {})
                    
                    meets_capacity = True
                    for cap_key, min_value in minimum_capacity.items():
                        if cap_key not in resource_capacity or resource_capacity[cap_key] < min_value:
                            meets_capacity = False
                            break
                            
                    if meets_capacity:
                        score += 3
                    else:
                        # Skip if minimum capacity isn't met
                        continue
                
                # Check jurisdiction if important
                if 'preferred_jurisdiction' in special_requirements:
                    preferred = special_requirements.get('preferred_jurisdiction')
                    if resource.get('jurisdiction') == preferred:
                        score += 2
                
                # Add to matching resources with score
                matching_resources.append((resource, score))
            
            # Sort by score (highest first)
            matching_resources.sort(key=lambda x: x[1], reverse=True)
            
            # Allocate up to requested quantity
            allocated_resources = []
            for resource, _ in matching_resources[:request_quantity]:
                resource_id = resource.get('id')
                used_resources.add(resource_id)
                allocated_resources.append(resource_id)
                
                allocations.append({
                    'request_id': request_id,
                    'resource_id': resource_id,
                    'deployment_location': request_location,
                    'notes': f"Allocated based on priority and requirements"
                })
                
                # Break if we've met the request quantity
                if len(allocated_resources) >= request_quantity:
                    break
        
        return {
            'method': 'priority',
            'allocations': allocations,
            'unallocated_requests': [
                r.get('id') for r in sorted_requests 
                if len([a for a in allocations if a['request_id'] == r.get('id')]) < r.get('quantity', 1)
            ],
            'unused_resources': [
                r.get('id') for r in resources 
                if r.get('id') not in used_resources
            ]
        }
    
    def _distance_based_allocation(
        self, 
        resources: List[Dict[str, Any]], 
        requests: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Distance-based allocation algorithm.
        Allocates resources based on proximity to deployment location.
        
        Args:
            resources: List of available resources
            requests: List of resource requests
            constraints: Optional constraints for the optimization
            
        Returns:
            Allocation plan
        """
        import math
        
        # Helper to calculate distance between locations
        def calculate_distance(loc1, loc2):
            if not loc1 or not loc2:
                return float('inf')
                
            lat1 = loc1.get('latitude')
            lon1 = loc1.get('longitude')
            lat2 = loc2.get('latitude')
            lon2 = loc2.get('longitude')
            
            if None in (lat1, lon1, lat2, lon2):
                return float('inf')
                
            # Simple Euclidean distance (would use Haversine for real implementation)
            return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        
        # Sort requests by priority (high, medium, low)
        priority_order = {'HIGH': 0, 'URGENT': 0, 'MEDIUM': 1, 'NORMAL': 1, 'LOW': 2}
        
        sorted_requests = sorted(
            requests, 
            key=lambda r: priority_order.get(r.get('priority', 'NORMAL').upper(), 1)
        )
        
        # Track allocations and used resources
        allocations = []
        used_resources = set()
        
        for request in sorted_requests:
            request_id = request.get('id')
            request_type = request.get('resource_type')
            request_quantity = request.get('quantity', 1)
            request_location = request.get('deployment_location')
            
            # Find matching resources
            matching_resources = []
            
            for resource in resources:
                if resource.get('resource_type') != request_type or resource.get('id') in used_resources:
                    continue
                    
                # Calculate distance
                resource_location = resource.get('current_location')
                distance = calculate_distance(resource_location, request_location)
                
                # Add to matching resources with distance
                matching_resources.append((resource, distance))
            
            # Sort by distance (closest first)
            matching_resources.sort(key=lambda x: x[1])
            
            # Allocate up to requested quantity
            allocated_resources = []
            for resource, distance in matching_resources[:request_quantity]:
                resource_id = resource.get('id')
                used_resources.add(resource_id)
                allocated_resources.append(resource_id)
                
                allocations.append({
                    'request_id': request_id,
                    'resource_id': resource_id,
                    'deployment_location': request_location,
                    'distance': distance,
                    'notes': f"Allocated based on proximity to deployment location"
                })
                
                # Break if we've met the request quantity
                if len(allocated_resources) >= request_quantity:
                    break
        
        return {
            'method': 'distance',
            'allocations': allocations,
            'unallocated_requests': [
                r.get('id') for r in sorted_requests 
                if len([a for a in allocations if a['request_id'] == r.get('id')]) < r.get('quantity', 1)
            ],
            'unused_resources': [
                r.get('id') for r in resources 
                if r.get('id') not in used_resources
            ]
        }
    
    def _multi_objective_allocation(
        self, 
        resources: List[Dict[str, Any]], 
        requests: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Multi-objective allocation algorithm.
        Balances priority, requirements, distance, and deployment time.
        
        Args:
            resources: List of available resources
            requests: List of resource requests
            constraints: Optional constraints for the optimization
            
        Returns:
            Allocation plan
        """
        import math
        
        # Helper to calculate distance between locations
        def calculate_distance(loc1, loc2):
            if not loc1 or not loc2:
                return float('inf')
                
            lat1 = loc1.get('latitude')
            lon1 = loc1.get('longitude')
            lat2 = loc2.get('latitude')
            lon2 = loc2.get('longitude')
            
            if None in (lat1, lon1, lat2, lon2):
                return float('inf')
                
            # Simple Euclidean distance (would use Haversine for real implementation)
            return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        
        # Get weights from constraints or use defaults
        weights = {
            'priority': 0.4,
            'requirements': 0.3,
            'distance': 0.2,
            'deploy_time': 0.1
        }
        
        if constraints and 'weights' in constraints:
            weights.update(constraints['weights'])
            
        # Normalize weights
        total_weight = sum(weights.values())
        for key in weights:
            weights[key] /= total_weight
        
        # Sort requests by priority (high, medium, low)
        priority_order = {'HIGH': 0, 'URGENT': 0, 'MEDIUM': 1, 'NORMAL': 1, 'LOW': 2}
        
        sorted_requests = sorted(
            requests, 
            key=lambda r: priority_order.get(r.get('priority', 'NORMAL').upper(), 1)
        )
        
        # Track allocations and used resources
        allocations = []
        used_resources = set()
        
        for request in sorted_requests:
            request_id = request.get('id')
            request_type = request.get('resource_type')
            request_quantity = request.get('quantity', 1)
            request_location = request.get('deployment_location')
            special_requirements = request.get('special_requirements', {})
            request_priority = request.get('priority', 'NORMAL').upper()
            priority_score = 1.0 - (priority_order.get(request_priority, 1) / 2)  # 1.0 for HIGH, 0.5 for MEDIUM, 0.0 for LOW
            
            # Find matching resources
            matching_resources = []
            
            for resource in resources:
                if resource.get('resource_type') != request_type or resource.get('id') in used_resources:
                    continue
                    
                # Calculate multi-objective score
                scores = {}
                
                # 1. Priority score (already calculated)
                scores['priority'] = priority_score
                
                # 2. Requirements score
                req_score = 0.0
                
                # Check capabilities match
                if 'capabilities' in resource and 'required_capabilities' in special_requirements:
                    resource_capabilities = set(resource.get('capabilities', []))
                    required_capabilities = set(special_requirements.get('required_capabilities', []))
                    
                    if required_capabilities and required_capabilities.issubset(resource_capabilities):
                        # Calculate match percentage
                        match_pct = len(required_capabilities) / max(1, len(resource_capabilities))
                        req_score += match_pct
                    else:
                        # Skip if required capabilities aren't met
                        continue
                else:
                    req_score += 0.5  # Neutral score if no capability requirements
                
                # Check capacity
                if 'capacity' in resource and 'minimum_capacity' in special_requirements:
                    resource_capacity = resource.get('capacity', {})
                    minimum_capacity = special_requirements.get('minimum_capacity', {})
                    
                    meets_capacity = True
                    for cap_key, min_value in minimum_capacity.items():
                        if cap_key not in resource_capacity or resource_capacity[cap_key] < min_value:
                            meets_capacity = False
                            break
                            
                    if meets_capacity:
                        req_score += 0.5
                    else:
                        # Skip if minimum capacity isn't met
                        continue
                else:
                    req_score += 0.5  # Neutral score if no capacity requirements
                
                # Normalize requirements score
                scores['requirements'] = req_score / 2.0
                
                # 3. Distance score
                resource_location = resource.get('current_location')
                distance = calculate_distance(resource_location, request_location)
                
                # Convert distance to a score (0 = far, 1 = close)
                # Using an exponential decay function
                distance_score = math.exp(-distance)
                scores['distance'] = distance_score
                
                # 4. Deployment time score
                deploy_time = resource.get('deployment_time', 60)  # Default 60 minutes
                
                # Convert time to a score (0 = slow, 1 = fast)
                # Using an exponential decay function
                time_score = math.exp(-deploy_time / 60)  # Normalized by 1 hour
                scores['deploy_time'] = time_score
                
                # Calculate weighted score
                weighted_score = sum(scores[key] * weight for key, weight in weights.items())
                
                # Add to matching resources with score
                matching_resources.append((resource, weighted_score, scores))
            
            # Sort by score (highest first)
            matching_resources.sort(key=lambda x: x[1], reverse=True)
            
            # Allocate up to requested quantity
            allocated_resources = []
            for resource, score, component_scores in matching_resources[:request_quantity]:
                resource_id = resource.get('id')
                used_resources.add(resource_id)
                allocated_resources.append(resource_id)
                
                # Calculate estimated travel time based on distance (simplified)
                resource_location = resource.get('current_location')
                distance = calculate_distance(resource_location, request_location)
                est_travel_hours = distance * 0.5  # Simple approximation
                
                allocations.append({
                    'request_id': request_id,
                    'resource_id': resource_id,
                    'deployment_location': request_location,
                    'score': score,
                    'component_scores': component_scores,
                    'estimated_travel_time': est_travel_hours,
                    'notes': f"Allocated using multi-objective optimization"
                })
                
                # Break if we've met the request quantity
                if len(allocated_resources) >= request_quantity:
                    break
        
        # Calculate allocation statistics
        total_requests = len(sorted_requests)
        fulfilled_requests = len(set(a['request_id'] for a in allocations))
        allocated_resources = len(allocations)
        
        return {
            'method': 'multi_objective',
            'weights': weights,
            'allocations': allocations,
            'statistics': {
                'total_requests': total_requests,
                'fulfilled_requests': fulfilled_requests,
                'allocation_rate': fulfilled_requests / total_requests if total_requests > 0 else 0,
                'allocated_resources': allocated_resources
            },
            'unallocated_requests': [
                r.get('id') for r in sorted_requests 
                if len([a for a in allocations if a['request_id'] == r.get('id')]) < r.get('quantity', 1)
            ],
            'unused_resources': [
                r.get('id') for r in resources 
                if r.get('id') not in used_resources
            ]
        }