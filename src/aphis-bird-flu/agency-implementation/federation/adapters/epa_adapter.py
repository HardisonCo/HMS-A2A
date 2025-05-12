"""
EPA Federation Adapter Implementation

This module implements the Federation Adapter for the EPA,
enabling integration with the interagency federation hub.
"""

import logging
import requests
from typing import Dict, List, Any, Optional

from .base_adapter import FederationAdapter
from ...epa.services.env_quality_monitoring.monitoring_service import EnvQualityMonitoringService
from ...epa.services.compliance_surveillance.compliance_service import ComplianceSurveillanceService
from ...epa.services.pollution_modeling.modeling_service import PollutionModelingService
from ...epa.system_supervisors.epa_supervisor import EPASupervisor

logger = logging.getLogger(__name__)

class EPAFederationAdapter(FederationAdapter):
    """
    Federation adapter for the EPA implementation
    
    Connects EPA services to the interagency federation hub,
    enabling data sharing, alerts, and cross-agency coordination.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("epa", config)
        self.monitoring_service = EnvQualityMonitoringService()
        self.compliance_service = ComplianceSurveillanceService()
        self.modeling_service = PollutionModelingService()
        self.supervisor = EPASupervisor()
        self.api_base_url = config.get("api_base_url", "http://localhost:8002/api/v1/epa")
        logger.info("EPA Federation Adapter initialized")
    
    def execute_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a federated query from the federation hub
        
        Args:
            query: Query specification with parameters
            
        Returns:
            Query results from EPA systems
        """
        query_type = query.get("type", "")
        parameters = query.get("parameters", {})
        
        if query_type == "env_quality":
            return self._execute_env_quality_query(parameters)
        elif query_type == "compliance":
            return self._execute_compliance_query(parameters)
        elif query_type == "pollution_impact":
            return self._execute_pollution_impact_query(parameters)
        else:
            logger.warning(f"Unsupported query type for EPA: {query_type}")
            return {
                "error": f"Unsupported query type: {query_type}",
                "supported_types": ["env_quality", "compliance", "pollution_impact"]
            }
    
    def _execute_env_quality_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an environmental quality query"""
        try:
            # Call the monitoring service with the provided parameters
            region = parameters.get("region")
            parameter_type = parameters.get("parameter_type")  # air, water, soil, etc.
            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")
            
            # Get quality monitoring data
            monitoring_data = self.monitoring_service.get_monitoring_data(
                region=region,
                parameter_type=parameter_type,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "status": "success",
                "data": monitoring_data,
                "metadata": {
                    "record_count": len(monitoring_data),
                    "region": region,
                    "parameter_type": parameter_type,
                    "time_range": f"{start_date} to {end_date}"
                }
            }
        except Exception as e:
            logger.error(f"Error executing environmental quality query: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_compliance_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a compliance query"""
        try:
            # Call the compliance service with the provided parameters
            region = parameters.get("region")
            facility_type = parameters.get("facility_type")
            compliance_status = parameters.get("compliance_status")
            
            # Get compliance data
            compliance_data = self.compliance_service.get_compliance_data(
                region=region,
                facility_type=facility_type,
                compliance_status=compliance_status
            )
            
            return {
                "status": "success",
                "data": compliance_data,
                "metadata": {
                    "record_count": len(compliance_data),
                    "region": region,
                    "facility_type": facility_type,
                    "compliance_status": compliance_status
                }
            }
        except Exception as e:
            logger.error(f"Error executing compliance query: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_pollution_impact_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pollution impact query"""
        try:
            # Call the modeling service with the provided parameters
            region = parameters.get("region")
            pollutant_type = parameters.get("pollutant_type")
            scenario = parameters.get("scenario", "baseline")
            
            # Get pollution impact model results
            impact_data = self.modeling_service.get_pollution_impact(
                region=region,
                pollutant_type=pollutant_type,
                scenario=scenario
            )
            
            return {
                "status": "success",
                "data": impact_data,
                "metadata": {
                    "region": region,
                    "pollutant_type": pollutant_type,
                    "scenario": scenario,
                    "model_version": self.modeling_service.get_model_version()
                }
            }
        except Exception as e:
            logger.error(f"Error executing pollution impact query: {str(e)}")
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
            if alert_type == "environmental_hazard":
                # Process environmental hazard alert
                self.supervisor.handle_environmental_alert(
                    severity=alert_severity,
                    details=alert_details,
                    source=source_agency
                )
            elif alert_type == "disease_outbreak":
                # Process disease outbreak alert that may have environmental implications
                self.supervisor.handle_disease_alert(
                    severity=alert_severity,
                    details=alert_details,
                    source=source_agency
                )
            elif alert_type == "emergency_response":
                # Process emergency response alert
                self.supervisor.handle_emergency_alert(
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
            # Process the resource allocation request through the EPA supervisor
            allocation_result = self.supervisor.allocate_resources(
                resource_type=resource_type,
                quantity=quantity,
                location=location,
                priority=priority
            )
            
            # Convert the result to the standardized federation format
            return {
                "agency_id": "epa",
                "resource_type": resource_type,
                "allocated_quantity": allocation_result.get("allocated_quantity", 0),
                "estimated_arrival": allocation_result.get("estimated_arrival"),
                "details": allocation_result.get("details", {})
            }
        except Exception as e:
            logger.error(f"Error allocating resources: {str(e)}")
            return {
                "agency_id": "epa",
                "resource_type": resource_type,
                "allocated_quantity": 0,
                "error": str(e)
            }
    
    def get_analysis_data(self, analysis_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve EPA data for joint analysis
        
        Args:
            analysis_request: Details of the requested analysis
            
        Returns:
            List of EPA data records for analysis
        """
        try:
            analysis_type = analysis_request.get("analysis_type", "")
            parameters = analysis_request.get("parameters", {})
            
            if analysis_type == "environmental_health_correlation":
                # Get environmental data for correlation with health outcomes
                region = parameters.get("region")
                env_factor = parameters.get("env_factor")
                start_date = parameters.get("start_date")
                end_date = parameters.get("end_date")
                
                # Retrieve the appropriate data
                env_data = self.monitoring_service.get_correlation_data(
                    region=region,
                    parameter_type=env_factor,
                    start_date=start_date,
                    end_date=end_date
                )
                
                return env_data
            elif analysis_type == "disaster_impact_assessment":
                # Get environmental data for disaster impact assessment
                region = parameters.get("region")
                disaster_type = parameters.get("disaster_type")
                date = parameters.get("date")
                
                # Get environmental impact data
                impact_data = self.modeling_service.get_disaster_impact_data(
                    region=region,
                    disaster_type=disaster_type,
                    date=date
                )
                
                return impact_data
            else:
                logger.warning(f"Unsupported analysis type for EPA: {analysis_type}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving analysis data: {str(e)}")
            return []
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of federation capabilities supported by EPA
        
        Returns:
            List of capability identifiers
        """
        return [
            "environmental_quality_monitoring",
            "compliance_surveillance",
            "pollution_impact_modeling",
            "environmental_resource_coordination",
            "environmental_alerts"
        ]