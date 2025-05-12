"""
FEMA Federation Adapter Implementation

This module implements the Federation Adapter for FEMA,
enabling integration with the interagency federation hub.
"""

import logging
import requests
from typing import Dict, List, Any, Optional

from .base_adapter import FederationAdapter
from ...fema.services.disaster_risk_monitoring.monitoring_service import DisasterRiskMonitoringService
from ...fema.services.resource_deployment_optimization.optimization_service import ResourceDeploymentOptimizationService
from ...fema.services.recovery_progress_tracking.tracking_service import RecoveryProgressTrackingService
from ...fema.system_supervisors.fema_supervisor import FEMASupervisor

logger = logging.getLogger(__name__)

class FEMAFederationAdapter(FederationAdapter):
    """
    Federation adapter for the FEMA implementation
    
    Connects FEMA services to the interagency federation hub,
    enabling data sharing, alerts, and cross-agency coordination.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("fema", config)
        self.risk_monitoring_service = DisasterRiskMonitoringService()
        self.resource_optimization_service = ResourceDeploymentOptimizationService()
        self.recovery_tracking_service = RecoveryProgressTrackingService()
        self.supervisor = FEMASupervisor()
        self.api_base_url = config.get("api_base_url", "http://localhost:8003/api/v1/fema")
        logger.info("FEMA Federation Adapter initialized")
    
    def execute_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a federated query from the federation hub
        
        Args:
            query: Query specification with parameters
            
        Returns:
            Query results from FEMA systems
        """
        query_type = query.get("type", "")
        parameters = query.get("parameters", {})
        
        if query_type == "disaster_risk":
            return self._execute_disaster_risk_query(parameters)
        elif query_type == "resource_deployment":
            return self._execute_resource_deployment_query(parameters)
        elif query_type == "recovery_progress":
            return self._execute_recovery_progress_query(parameters)
        else:
            logger.warning(f"Unsupported query type for FEMA: {query_type}")
            return {
                "error": f"Unsupported query type: {query_type}",
                "supported_types": ["disaster_risk", "resource_deployment", "recovery_progress"]
            }
    
    def _execute_disaster_risk_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a disaster risk query"""
        try:
            # Call the risk monitoring service with the provided parameters
            region = parameters.get("region")
            disaster_type = parameters.get("disaster_type")  # flood, fire, hurricane, etc.
            time_horizon = parameters.get("time_horizon", 30)  # days
            
            # Get risk monitoring data
            risk_data = self.risk_monitoring_service.get_risk_assessment(
                region=region,
                disaster_type=disaster_type,
                time_horizon=time_horizon
            )
            
            return {
                "status": "success",
                "data": risk_data,
                "metadata": {
                    "region": region,
                    "disaster_type": disaster_type,
                    "time_horizon": time_horizon,
                    "assessment_date": risk_data.get("assessment_date")
                }
            }
        except Exception as e:
            logger.error(f"Error executing disaster risk query: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_resource_deployment_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a resource deployment query"""
        try:
            # Call the resource optimization service with the provided parameters
            region = parameters.get("region")
            disaster_type = parameters.get("disaster_type")
            resource_types = parameters.get("resource_types", [])
            
            # Get resource deployment data
            deployment_data = self.resource_optimization_service.get_deployment_plan(
                region=region,
                disaster_type=disaster_type,
                resource_types=resource_types
            )
            
            return {
                "status": "success",
                "data": deployment_data,
                "metadata": {
                    "region": region,
                    "disaster_type": disaster_type,
                    "resource_types": resource_types,
                    "plan_generated": deployment_data.get("generation_timestamp")
                }
            }
        except Exception as e:
            logger.error(f"Error executing resource deployment query: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_recovery_progress_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a recovery progress query"""
        try:
            # Call the recovery tracking service with the provided parameters
            disaster_id = parameters.get("disaster_id")
            metrics = parameters.get("metrics", [])
            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")
            
            # Get recovery progress data
            progress_data = self.recovery_tracking_service.get_recovery_progress(
                disaster_id=disaster_id,
                metrics=metrics,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "status": "success",
                "data": progress_data,
                "metadata": {
                    "disaster_id": disaster_id,
                    "metrics": metrics,
                    "time_range": f"{start_date} to {end_date}"
                }
            }
        except Exception as e:
            logger.error(f"Error executing recovery progress query: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Process an alert received from the federation hub
        
        Args:
            alert: Alert details
            
        Returns:
            True if alert was successfully processed
        """
        try:
            alert_type = alert.get("type", "")
            alert_severity = alert.get("severity", "medium")
            alert_details = alert.get("details", {})
            source_agency = alert.get("source_agency", "")
            
            # Log the alert
            logger.info(f"Received {alert_severity} {alert_type} alert from {source_agency}")
            
            # Forward the alert to the appropriate internal system
            if alert_type == "emergency_response":
                # Process emergency response alert
                self.supervisor.handle_emergency_alert(
                    severity=alert_severity,
                    details=alert_details,
                    source=source_agency
                )
            elif alert_type == "disease_outbreak":
                # Process disease outbreak alert
                self.supervisor.handle_disease_alert(
                    severity=alert_severity,
                    details=alert_details,
                    source=source_agency
                )
            elif alert_type == "environmental_hazard":
                # Process environmental hazard alert
                self.supervisor.handle_environmental_alert(
                    severity=alert_severity,
                    details=alert_details,
                    source=source_agency
                )
            else:
                # Process generic alert
                self.supervisor.handle_generic_alert(
                    alert_type=alert_type,
                    severity=alert_severity,
                    details=alert_details,
                    source=source_agency
                )
            
            return True
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
            return False
    
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
        try:
            # Process the resource allocation request through the FEMA resource service
            allocation_result = self.resource_optimization_service.allocate_resources(
                resource_type=resource_type,
                quantity=quantity,
                location=location,
                priority=priority
            )
            
            # Convert the result to the standardized federation format
            return {
                "agency_id": "fema",
                "resource_type": resource_type,
                "allocated_quantity": allocation_result.get("allocated_quantity", 0),
                "estimated_arrival": allocation_result.get("estimated_arrival"),
                "details": allocation_result.get("details", {})
            }
        except Exception as e:
            logger.error(f"Error allocating resources: {str(e)}")
            return {
                "agency_id": "fema",
                "resource_type": resource_type,
                "allocated_quantity": 0,
                "error": str(e)
            }
    
    def get_analysis_data(self, analysis_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve FEMA data for joint analysis
        
        Args:
            analysis_request: Details of the requested analysis
            
        Returns:
            List of FEMA data records for analysis
        """
        try:
            analysis_type = analysis_request.get("analysis_type", "")
            parameters = analysis_request.get("parameters", {})
            
            if analysis_type == "disaster_impact_assessment":
                # Get disaster impact data
                region = parameters.get("region")
                disaster_type = parameters.get("disaster_type")
                start_date = parameters.get("start_date")
                end_date = parameters.get("end_date")
                
                # Retrieve the appropriate data
                impact_data = self.risk_monitoring_service.get_impact_data(
                    region=region,
                    disaster_type=disaster_type,
                    start_date=start_date,
                    end_date=end_date
                )
                
                return impact_data
            elif analysis_type == "response_resource_inventory":
                # Get resource inventory data
                region = parameters.get("region")
                resource_types = parameters.get("resource_types", [])
                
                # Get resource inventory data
                inventory_data = self.resource_optimization_service.get_resource_inventory(
                    region=region,
                    resource_types=resource_types
                )
                
                return inventory_data
            else:
                logger.warning(f"Unsupported analysis type for FEMA: {analysis_type}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving analysis data: {str(e)}")
            return []
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of federation capabilities supported by FEMA
        
        Returns:
            List of capability identifiers
        """
        return [
            "disaster_risk_monitoring",
            "resource_deployment_optimization",
            "recovery_progress_tracking",
            "emergency_resource_coordination",
            "emergency_alerts"
        ]