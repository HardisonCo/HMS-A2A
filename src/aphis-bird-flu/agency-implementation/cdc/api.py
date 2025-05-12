"""
API entry point for the CDC implementation of the Adaptive Surveillance and Response System.

This module provides FastAPI endpoints for the CDC-specific implementation, including
human disease surveillance, outbreak detection, and contact tracing.
"""
from typing import Dict, List, Any, Optional
from datetime import date, datetime
import logging
import json

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from .system-supervisors.cdc_supervisor import CDCSupervisor
from .models.human_disease import (
    HumanDiseaseCase, Contact, Cluster, CaseClassification, 
    DiseaseType, DiseaseOutcome, TransmissionMode, RiskLevel
)
from .services.human_disease_surveillance import (
    HumanDiseaseSurveillanceService, HumanDiseaseRepository
)
from .services.outbreak_detection import (
    OutbreakDetectionService, OutbreakRepository
)
from .services.contact_tracing import (
    ContactTracingService, ContactRepository
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cdc_api")

# Initialize FastAPI app
app = FastAPI(
    title="CDC Adaptive Surveillance and Response System API",
    description="API for the CDC implementation of the Adaptive Surveillance and Response System",
    version="1.0.0"
)

# Initialize repositories and services
disease_repository = HumanDiseaseRepository()
outbreak_repository = OutbreakRepository()
contact_repository = ContactRepository()

disease_service = HumanDiseaseSurveillanceService(disease_repository)
outbreak_service = OutbreakDetectionService(outbreak_repository)
contact_service = ContactTracingService(contact_repository)

# Initialize CDC supervisor
cdc_supervisor = CDCSupervisor()


# Dependency to get the CDC supervisor
def get_supervisor() -> CDCSupervisor:
    return cdc_supervisor


# Dependency to get the human disease service
def get_disease_service() -> HumanDiseaseSurveillanceService:
    return disease_service


# Dependency to get the outbreak detection service
def get_outbreak_service() -> OutbreakDetectionService:
    return outbreak_service


# Dependency to get the contact tracing service
def get_contact_service() -> ContactTracingService:
    return contact_service


# Pydantic models for API requests and responses
class SystemStatus(BaseModel):
    status: str
    timestamp: str
    components: Dict[str, str]
    last_health_check: Dict[str, str]


class CaseRequest(BaseModel):
    patient_id: str
    disease_type: str
    onset_date: str
    report_date: str
    location: Dict[str, float]
    classification: Optional[str] = None
    outcome: Optional[str] = None
    transmission_mode: Optional[str] = None
    risk_level: Optional[str] = None
    jurisdiction: Optional[str] = None
    demographics: Optional[Dict[str, Any]] = None
    symptoms: Optional[List[str]] = None
    laboratory_results: Optional[List[Dict[str, Any]]] = None


class CaseResponse(BaseModel):
    id: str
    patient_id: str
    disease_type: str
    onset_date: str
    report_date: str
    location: Dict[str, float]
    classification: str
    outcome: str
    created_at: str
    updated_at: str


class ContactRequest(BaseModel):
    person_id: str
    case_id: str
    contact_date: str
    location: Dict[str, float]
    contact_type: str
    risk_assessment: Optional[str] = None
    risk_factors: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    demographics: Optional[Dict[str, Any]] = None
    symptoms: Optional[List[str]] = None
    exposure_duration_minutes: Optional[int] = None
    monitoring_status: Optional[str] = "pending"
    isolation_status: Optional[str] = "not_isolated"


class ContactResponse(BaseModel):
    id: str
    person_id: str
    case_id: str
    contact_date: str
    contact_type: str
    risk_assessment: str
    monitoring_status: str
    isolation_status: str
    created_at: str
    updated_at: str


class ClusterRequest(BaseModel):
    name: str
    disease_type: str
    cases: List[str]
    start_date: str
    end_date: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    regions: Optional[List[str]] = None
    status: Optional[str] = "active"
    transmission_mode: Optional[str] = None
    risk_level: Optional[str] = None
    index_case_id: Optional[str] = None


class ClusterResponse(BaseModel):
    id: str
    name: str
    disease_type: str
    cases: List[str]
    start_date: str
    end_date: Optional[str] = None
    status: str
    risk_level: str
    created_at: str
    updated_at: str


# Routes for system status
@app.get("/status", response_model=SystemStatus)
async def get_system_status(supervisor: CDCSupervisor = Depends(get_supervisor)):
    """Get the current status of the CDC system"""
    return supervisor.get_system_status()


# Routes for human disease surveillance
@app.get("/cases")
async def get_cases(
    disease_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    service: HumanDiseaseSurveillanceService = Depends(get_disease_service)
):
    """Get disease cases with optional filtering"""
    # Apply filters if provided
    if disease_type:
        cases = service.find_cases_by_disease(disease_type)
    elif start_date and end_date:
        cases = service.find_cases_by_date_range(start_date, end_date)
    else:
        criteria = {}
        if jurisdiction:
            criteria['jurisdiction'] = jurisdiction
        cases = service.find_cases(criteria) if criteria else service.get_all_cases()
    
    # Convert to dictionary format for API response
    return [case.to_dict() for case in cases]


@app.get("/cases/{case_id}")
async def get_case(
    case_id: str,
    service: HumanDiseaseSurveillanceService = Depends(get_disease_service)
):
    """Get a specific disease case by ID"""
    case = service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.to_dict()


@app.post("/cases", response_model=CaseResponse)
async def create_case(
    case_data: CaseRequest,
    service: HumanDiseaseSurveillanceService = Depends(get_disease_service)
):
    """Create a new disease case"""
    try:
        case = service.create_case(case_data.dict())
        return case.to_dict()
    except Exception as e:
        logger.error(f"Error creating case: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    case_updates: Dict[str, Any],
    service: HumanDiseaseSurveillanceService = Depends(get_disease_service)
):
    """Update an existing disease case"""
    case = service.update_case(case_id, case_updates)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.to_dict()


@app.get("/cases/summary")
async def get_case_summary(
    disease_type: Optional[str] = None,
    service: HumanDiseaseSurveillanceService = Depends(get_disease_service)
):
    """Get a summary of disease cases"""
    filters = {}
    if disease_type:
        filters['disease_type'] = disease_type
    
    return service.generate_summary_report(filters)


@app.get("/cases/statistics")
async def get_case_statistics(
    disease_type: Optional[str] = None,
    service: HumanDiseaseSurveillanceService = Depends(get_disease_service)
):
    """Get statistics about disease cases"""
    return service.get_case_statistics(disease_type)


# Routes for outbreak detection
@app.get("/outbreaks/detection-status")
async def get_detection_status(
    service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Get the current outbreak detection status"""
    return service.get_detection_status()


@app.post("/outbreaks/detect")
async def detect_outbreaks(
    case_ids: List[str],
    disease_service: HumanDiseaseSurveillanceService = Depends(get_disease_service),
    outbreak_service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Run outbreak detection on a set of cases"""
    # Get the cases
    cases = [disease_service.get_case(case_id) for case_id in case_ids]
    cases = [case for case in cases if case]  # Filter out None values
    
    if not cases:
        raise HTTPException(status_code=400, detail="No valid cases provided")
    
    # Run detection
    detection_results = outbreak_service.detect_outbreaks(cases)
    return detection_results


@app.get("/outbreaks/clusters")
async def get_clusters(
    disease_type: Optional[str] = None,
    active_only: bool = False,
    service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Get outbreak clusters with optional filtering"""
    if disease_type:
        clusters = service.find_clusters_by_disease(disease_type)
    elif active_only:
        clusters = service.find_active_clusters()
    else:
        clusters = service.get_all_clusters()
    
    # Convert to dictionary format for API response
    return [cluster.to_dict() for cluster in clusters]


@app.get("/outbreaks/clusters/{cluster_id}")
async def get_cluster(
    cluster_id: str,
    service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Get a specific outbreak cluster by ID"""
    cluster = service.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster.to_dict()


@app.post("/outbreaks/clusters", response_model=ClusterResponse)
async def create_cluster(
    cluster_data: ClusterRequest,
    service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Create a new outbreak cluster"""
    try:
        cluster = service.create_cluster(cluster_data.dict())
        return cluster.to_dict()
    except Exception as e:
        logger.error(f"Error creating cluster: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/outbreaks/clusters/{cluster_id}", response_model=ClusterResponse)
async def update_cluster(
    cluster_id: str,
    cluster_updates: Dict[str, Any],
    service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Update an existing outbreak cluster"""
    cluster = service.update_cluster(cluster_id, cluster_updates)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster.to_dict()


@app.post("/outbreaks/clusters/{cluster_id}/close")
async def close_cluster(
    cluster_id: str,
    service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Close an outbreak cluster"""
    cluster = service.close_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"success": True, "message": f"Cluster {cluster_id} closed successfully"}


@app.get("/outbreaks/summary")
async def get_outbreak_summary(
    days: int = Query(30, description="Number of days to include in the summary"),
    service: OutbreakDetectionService = Depends(get_outbreak_service)
):
    """Get a summary of outbreak activity"""
    return service.generate_outbreak_summary(days)


# Routes for contact tracing
@app.get("/contacts")
async def get_contacts(
    case_id: Optional[str] = None,
    person_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    active_only: bool = False,
    service: ContactTracingService = Depends(get_contact_service)
):
    """Get contacts with optional filtering"""
    if case_id:
        contacts = service.find_contacts_by_case(case_id)
    elif person_id:
        contacts = service.find_contacts_by_person(person_id)
    elif risk_level:
        contacts = service.find_contacts_by_risk_level(risk_level)
    elif active_only:
        contacts = service.find_active_monitoring()
    else:
        contacts = service.get_all_contacts()
    
    # Convert to dictionary format for API response
    return [contact.to_dict() for contact in contacts]


@app.get("/contacts/{contact_id}")
async def get_contact(
    contact_id: str,
    service: ContactTracingService = Depends(get_contact_service)
):
    """Get a specific contact by ID"""
    contact = service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact.to_dict()


@app.post("/contacts", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactRequest,
    service: ContactTracingService = Depends(get_contact_service)
):
    """Create a new contact"""
    try:
        contact = service.create_contact(contact_data.dict())
        return contact.to_dict()
    except Exception as e:
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact_updates: Dict[str, Any],
    service: ContactTracingService = Depends(get_contact_service)
):
    """Update an existing contact"""
    contact = service.update_contact(contact_id, contact_updates)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact.to_dict()


@app.post("/contacts/{contact_id}/monitoring-status")
async def update_monitoring_status(
    contact_id: str,
    status: str,
    service: ContactTracingService = Depends(get_contact_service)
):
    """Update the monitoring status of a contact"""
    contact = service.update_monitoring_status(contact_id, status)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"success": True, "message": f"Monitoring status updated to {status}"}


@app.post("/contacts/{contact_id}/isolation-status")
async def update_isolation_status(
    contact_id: str,
    status: str,
    service: ContactTracingService = Depends(get_contact_service)
):
    """Update the isolation status of a contact"""
    contact = service.update_isolation_status(contact_id, status)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"success": True, "message": f"Isolation status updated to {status}"}


@app.post("/contacts/{contact_id}/test-result")
async def add_test_result(
    contact_id: str,
    result: Dict[str, Any],
    service: ContactTracingService = Depends(get_contact_service)
):
    """Add a test result for a contact"""
    contact = service.add_test_result(contact_id, result)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"success": True, "message": "Test result added successfully"}


@app.post("/contacts/{contact_id}/recommend-testing")
async def recommend_testing(
    contact_id: str,
    test_location: str,
    test_date: str,
    service: ContactTracingService = Depends(get_contact_service)
):
    """Recommend testing for a contact"""
    success = service.recommend_testing(contact_id, test_location, test_date)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send test recommendation")
    return {"success": True, "message": "Test recommendation sent successfully"}


@app.get("/contacts/prioritize")
async def prioritize_contacts(
    case_ids: Optional[List[str]] = Query(None),
    service: ContactTracingService = Depends(get_contact_service)
):
    """Prioritize contacts for follow-up"""
    prioritized = service.prioritize_contacts(case_ids)
    
    # Convert contact objects to dictionaries
    result = []
    for item in prioritized:
        contact_dict = item['contact'].to_dict()
        result.append({
            'contact': contact_dict,
            'priority_score': item['priority_score'],
            'days_since_contact': item['days_since_contact'],
            'has_symptoms': item['has_symptoms']
        })
    
    return result


@app.get("/contacts/monitoring-report")
async def get_monitoring_report(
    days: int = Query(14, description="Number of days to include in the report"),
    service: ContactTracingService = Depends(get_contact_service)
):
    """Get a report of contact monitoring activities"""
    return service.generate_monitoring_report(days)


@app.get("/contacts/transmission-network")
async def get_transmission_network(
    case_ids: List[str],
    service: ContactTracingService = Depends(get_contact_service)
):
    """Get transmission network for a set of cases"""
    return service.construct_transmission_network(case_ids)


# Start the CDC supervisor when the API starts
@app.on_event("startup")
async def startup_event():
    await cdc_supervisor.start()
    logger.info("CDC API started")


# Stop the CDC supervisor when the API stops
@app.on_event("shutdown")
async def shutdown_event():
    await cdc_supervisor.stop()
    logger.info("CDC API stopped")