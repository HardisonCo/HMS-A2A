"""
Federation API

This module implements the FastAPI routes for the interagency federation hub,
providing endpoints for federated queries, alerts, resource coordination,
and joint analysis.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from .core.federation_hub import get_federation_hub, AgencyRegistration
from .services.federated_query_service import FederatedQueryService
from .services.cross_agency_alert_service import CrossAgencyAlertService, Alert
from .services.resource_coordination_service import (
    ResourceCoordinationService, ResourceRequest, ResourceAllocation
)
from .services.joint_analysis_service import (
    JointAnalysisService, AnalysisRequest, AnalysisResult
)
from .adapters import CDCFederationAdapter, EPAFederationAdapter, FEMAFederationAdapter

# Initialize API
api = FastAPI(title="Interagency Federation Hub API", 
              description="API for federated queries, alerts, resource coordination, and joint analysis across agencies",
              version="1.0.0")

# Initialize services
federated_query_service = FederatedQueryService()
cross_agency_alert_service = CrossAgencyAlertService()
resource_coordination_service = ResourceCoordinationService()
joint_analysis_service = JointAnalysisService()

# Register agency adapters
federation_hub = get_federation_hub()
cdc_adapter = CDCFederationAdapter()
epa_adapter = EPAFederationAdapter()
fema_adapter = FEMAFederationAdapter()

# Register adapters with the federation hub
federation_hub.register_adapter("cdc", cdc_adapter)
federation_hub.register_adapter("epa", epa_adapter)
federation_hub.register_adapter("fema", fema_adapter)

# Register agencies with the federation hub
federation_hub.register_agency(AgencyRegistration(
    agency_id="cdc",
    name="Centers for Disease Control and Prevention",
    endpoint_base_url="http://localhost:8001/api/v1/cdc",
    capabilities=cdc_adapter.get_capabilities()
))

federation_hub.register_agency(AgencyRegistration(
    agency_id="epa",
    name="Environmental Protection Agency",
    endpoint_base_url="http://localhost:8002/api/v1/epa",
    capabilities=epa_adapter.get_capabilities()
))

federation_hub.register_agency(AgencyRegistration(
    agency_id="fema",
    name="Federal Emergency Management Agency",
    endpoint_base_url="http://localhost:8003/api/v1/fema",
    capabilities=fema_adapter.get_capabilities()
))

# Setup logging
logger = logging.getLogger(__name__)

# API Models
class QueryRequest(BaseModel):
    """Model for federated query requests"""
    type: str
    parameters: Dict[str, Any]
    agencies: Optional[List[str]] = None

class AlertRequest(BaseModel):
    """Model for alert broadcasting requests"""
    type: str
    severity: str = "medium"
    title: str
    details: Dict[str, Any] = {}
    source_agency: str
    location: Optional[Dict[str, Any]] = None
    agencies: Optional[List[str]] = None

class ResourceRequestInput(BaseModel):
    """Model for resource request inputs"""
    resource_type: str
    quantity: int
    location: Dict[str, Any]
    priority: str = "medium"
    requesting_agency: str
    requested_delivery: Optional[datetime] = None
    details: Dict[str, Any] = {}

class AnalysisRequestInput(BaseModel):
    """Model for analysis request inputs"""
    analysis_type: str
    parameters: Dict[str, Any]
    requesting_agency: str
    target_agencies: Optional[List[str]] = None
    priority: str = "medium"

# Endpoints: Agency Registration
@api.get("/api/v1/federation/agencies", response_model=List[AgencyRegistration])
async def get_registered_agencies():
    """Get all registered agencies in the federation hub"""
    return federation_hub.get_registered_agencies()

# Endpoints: Federated Queries
@api.post("/api/v1/federation/query")
async def execute_federated_query(query_request: QueryRequest):
    """Execute a federated query across agencies"""
    try:
        results = federated_query_service.execute_query(
            query={
                "type": query_request.type,
                "parameters": query_request.parameters
            },
            agencies=query_request.agencies
        )
        return results
    except Exception as e:
        logger.error(f"Error executing federated query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/v1/federation/query/types")
async def get_query_types():
    """Get available query types for each agency"""
    return federated_query_service.get_available_query_types()

# Endpoints: Cross-Agency Alerts
@api.post("/api/v1/federation/alert")
async def broadcast_alert(alert_request: AlertRequest):
    """Broadcast an alert to multiple agencies"""
    try:
        alert = cross_agency_alert_service.create_alert(
            alert_type=alert_request.type,
            title=alert_request.title,
            source_agency=alert_request.source_agency,
            severity=alert_request.severity,
            details=alert_request.details,
            location=alert_request.location
        )
        
        results = cross_agency_alert_service.broadcast_alert(
            alert=alert,
            agencies=alert_request.agencies
        )
        
        return {
            "alert_id": alert.alert_id,
            "broadcast_results": results
        }
    except Exception as e:
        logger.error(f"Error broadcasting alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/v1/federation/alert/history")
async def get_alert_history(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    source_agency: Optional[str] = None,
    alert_types: Optional[str] = None,
    severity: Optional[str] = None
):
    """Get alert history with optional filtering"""
    alert_type_list = alert_types.split(",") if alert_types else None
    
    history = cross_agency_alert_service.get_alert_history(
        start_time=start_time,
        end_time=end_time,
        source_agency=source_agency,
        alert_types=alert_type_list,
        severity=severity
    )
    
    return history

# Endpoints: Resource Coordination
@api.post("/api/v1/federation/resource/request")
async def request_resources(resource_request_input: ResourceRequestInput):
    """Submit a resource request for cross-agency coordination"""
    try:
        resource_request = resource_coordination_service.create_resource_request(
            requesting_agency=resource_request_input.requesting_agency,
            resource_type=resource_request_input.resource_type,
            quantity=resource_request_input.quantity,
            location=resource_request_input.location,
            priority=resource_request_input.priority,
            requested_delivery=resource_request_input.requested_delivery,
            details=resource_request_input.details
        )
        
        results = resource_coordination_service.request_resources(resource_request)
        return results
    except Exception as e:
        logger.error(f"Error requesting resources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/v1/federation/resource/request/{request_id}")
async def get_resource_request_status(request_id: str):
    """Get status of a resource request"""
    try:
        status = resource_coordination_service.get_request_status(request_id)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource request status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/v1/federation/resource/active")
async def get_active_resource_requests(agency_id: Optional[str] = None):
    """Get active resource requests"""
    return resource_coordination_service.get_active_requests(agency_id)

# Endpoints: Joint Analysis
@api.post("/api/v1/federation/analysis")
async def submit_analysis(analysis_request_input: AnalysisRequestInput):
    """Submit a joint analysis request across agencies"""
    try:
        analysis_request = joint_analysis_service.create_analysis_request(
            analysis_type=analysis_request_input.analysis_type,
            parameters=analysis_request_input.parameters,
            requesting_agency=analysis_request_input.requesting_agency,
            target_agencies=analysis_request_input.target_agencies,
            priority=analysis_request_input.priority
        )
        
        result = joint_analysis_service.submit_analysis(analysis_request)
        return {
            "analysis_id": result.analysis_id,
            "status": result.status
        }
    except Exception as e:
        logger.error(f"Error submitting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/v1/federation/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get status of a joint analysis"""
    try:
        status = joint_analysis_service.get_analysis_status(analysis_id)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/v1/federation/analysis/types")
async def get_analysis_types():
    """Get available joint analysis types"""
    return joint_analysis_service.get_analysis_types()