"""
CDC Federation Adapter Implementation

This module implements the Federation Adapter for the CDC,
enabling integration with the interagency federation hub.
"""

import logging
import requests
from typing import Dict, List, Any, Optional

from .base_adapter import FederationAdapter
from ...cdc.services.human_disease_surveillance.surveillance_service import HumanDiseaseSurveillanceService
from ...cdc.services.outbreak_detection.detection_service import OutbreakDetectionService
from ...cdc.services.contact_tracing.tracing_service import ContactTracingService
from ...cdc.system_supervisors.cdc_supervisor import CDCSupervisor

logger = logging.getLogger(__name__)

class CDCFederationAdapter(FederationAdapter):
    """
    Federation adapter for the CDC implementation
    
    Connects CDC services to the interagency federation hub,
    enabling data sharing, alerts, and cross-agency coordination.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("cdc", config)
        self.surveillance_service = HumanDiseaseSurveillanceService()
        self.detection_service = OutbreakDetectionService()
        self.tracing_service = ContactTracingService()
        self.supervisor = CDCSupervisor()
        self.api_base_url = config.get("api_base_url", "http://localhost:8001/api/v1/cdc")
        logger.info("CDC Federation Adapter initialized")
    
    def execute_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a federated query from the federation hub
        
        Args:
            query: Query specification with parameters
            
        Returns:
            Query results from CDC systems
        """
        query_type = query.get("type", "")
        parameters = query.get("parameters", {})
        
        if query_type == "disease_surveillance":
            return self._execute_disease_surveillance_query(parameters)
        elif query_type == "outbreak_detection":
            return self._execute_outbreak_detection_query(parameters)
        elif query_type == "contact_tracing":
            return self._execute_contact_tracing_query(parameters)
        else:
            logger.warning(f"Unsupported query type for CDC: {query_type}")
            return {
                "error": f"Unsupported query type: {query_type}",
                "supported_types": ["disease_surveillance", "outbreak_detection", "contact_tracing"]
            }
    
    def _execute_disease_surveillance_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a disease surveillance query"""
        try:
            # Call the surveillance service with the provided parameters
            region = parameters.get("region")
            disease_type = parameters.get("disease_type")
            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")
            
            # Get surveillance data
            surveillance_data = self.surveillance_service.get_surveillance_data(
                region=region,
                disease_type=disease_type,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "status": "success",
                "data": surveillance_data,
                "metadata": {
                    "record_count": len(surveillance_data),
                    "region": region,
                    "disease_type": disease_type,
                    "time_range": f"{start_date} to {end_date}"
                }
            }
        except Exception as e:
            logger.error(f"Error executing disease surveillance query: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_outbreak_detection_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an outbreak detection query"""
        try:
            # Call the outbreak detection service with the provided parameters
            region = parameters.get("region")
            disease_type = parameters.get("disease_type")
            threshold = parameters.get("threshold", 0.05)
            
            # Get outbreak detection results
            detection_results = self.detection_service.detect_outbreaks(
                region=region,
                disease_type=disease_type,
                threshold=threshold
            )
            
            return {
                "status": "success",
                "data": detection_results,
                "metadata": {
                    "region": region,
                    "disease_type": disease_type,
                    "threshold": threshold,
                    "detection_count": len(detection_results)
                }
            }
        except Exception as e:
            logger.error(f"Error executing outbreak detection query: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_contact_tracing_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a contact tracing query"""
        try:
            # Call the contact tracing service with the provided parameters
            case_id = parameters.get("case_id")
            depth = parameters.get("depth", 2)
            
            # Get contact tracing results
            tracing_results = self.tracing_service.trace_contacts(
                case_id=case_id,
                depth=depth
            )
            
            return {
                "status": "success",
                "data": tracing_results,
                "metadata": {
                    "case_id": case_id,
                    "depth": depth,
                    "contact_count": len(tracing_results)
                }
            }
        except Exception as e:
            logger.error(f"Error executing contact tracing query: {str(e)}")
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
            if alert_type == "disease_outbreak":
                # Process disease outbreak alert
                self.detection_service.process_external_alert(
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
            # Process the resource allocation request through the CDC supervisor
            allocation_result = self.supervisor.allocate_resources(
                resource_type=resource_type,
                quantity=quantity,
                location=location,
                priority=priority
            )
            
            # Convert the result to the standardized federation format
            return {
                "agency_id": "cdc",
                "resource_type": resource_type,
                "allocated_quantity": allocation_result.get("allocated_quantity", 0),
                "estimated_arrival": allocation_result.get("estimated_arrival"),
                "details": allocation_result.get("details", {})
            }
        except Exception as e:
            logger.error(f"Error allocating resources: {str(e)}")
            return {
                "agency_id": "cdc",
                "resource_type": resource_type,
                "allocated_quantity": 0,
                "error": str(e)
            }
    
    def get_analysis_data(self, analysis_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve CDC data for joint analysis
        
        Args:
            analysis_request: Details of the requested analysis
            
        Returns:
            List of CDC data records for analysis
        """
        try:
            analysis_type = analysis_request.get("analysis_type", "")
            parameters = analysis_request.get("parameters", {})
            
            if analysis_type == "disease_spread":
                # Get disease spread data for joint analysis
                region = parameters.get("region")
                disease_type = parameters.get("disease_type")
                start_date = parameters.get("start_date")
                end_date = parameters.get("end_date")
                
                # Retrieve the appropriate data
                spread_data = self.surveillance_service.get_spread_data(
                    region=region,
                    disease_type=disease_type,
                    start_date=start_date,
                    end_date=end_date
                )
                
                return spread_data
            elif analysis_type == "contact_network":
                # Get contact network data for joint analysis
                case_ids = parameters.get("case_ids", [])
                depth = parameters.get("depth", 1)
                
                # Retrieve contact network data
                network_data = []
                for case_id in case_ids:
                    contacts = self.tracing_service.get_contact_network(
                        case_id=case_id,
                        depth=depth
                    )
                    network_data.extend(contacts)
                
                return network_data
            else:
                logger.warning(f"Unsupported analysis type for CDC: {analysis_type}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving analysis data: {str(e)}")
            return []
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of federation capabilities supported by CDC
        
        Returns:
            List of capability identifiers
        """
        return [
            "disease_surveillance",
            "outbreak_detection",
            "contact_tracing",
            "medical_resource_coordination",
            "health_alerts"
        ]