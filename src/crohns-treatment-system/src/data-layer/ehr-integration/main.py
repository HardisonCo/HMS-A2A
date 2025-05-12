#!/usr/bin/env python3
"""
HMS-EHR Main Entry Point for Crohn's Disease Treatment System

This module provides the main entry point for the HMS-EHR component,
setting up the FHIR client, patient service, and API server.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import uvicorn
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from fhir_client import FHIRClient, ResourceType
from patient_service import PatientService
from patient_model import (
    PatientRecord, GeneralInfo, CrohnsInfo, GeneticMarker, Biomarker, BiomarkerValue,
    Medication, TreatmentHistory, Surgery, Hospitalization, Assessment, Address, Contact,
    Gender, CrohnsLocation, DiseaseSeverity, TreatmentResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ehr.main')

# Initialize services
fhir_client = None
patient_service = None

# Define API data models
class PatientSearchParams(BaseModel):
    """Search parameters for patients"""
    name: Optional[str] = None
    identifier: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None

class BiomarkerValueModel(BaseModel):
    """Model for biomarker value"""
    value: float
    unit: str
    date: str
    reference_range: Optional[Dict[str, float]] = None
    abnormal: Optional[bool] = None

class AssessmentModel(BaseModel):
    """Model for clinical assessment"""
    date: str
    provider: Optional[str] = None
    setting: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    physical_findings: Dict[str, Any] = Field(default_factory=dict)
    disease_activity_index: Optional[float] = None
    severity_assessment: Optional[str] = None
    plan: Optional[str] = None
    notes: Optional[str] = None

class MedicationModel(BaseModel):
    """Model for medication"""
    name: str
    code: Optional[str] = None
    system: Optional[str] = None
    dosage: Optional[str] = None
    unit: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    reason_stopped: Optional[str] = None

# Initialize services on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize FHIR client
    global fhir_client
    fhir_base_url = os.environ.get("FHIR_BASE_URL", "http://hapi.fhir.org/baseR4/")
    fhir_api_key = os.environ.get("FHIR_API_KEY", "")
    fhir_client_id = os.environ.get("FHIR_CLIENT_ID", "")
    fhir_client_secret = os.environ.get("FHIR_CLIENT_SECRET", "")
    
    fhir_client = FHIRClient(
        base_url=fhir_base_url,
        api_key=fhir_api_key,
        client_id=fhir_client_id,
        client_secret=fhir_client_secret
    )
    
    # Initialize patient service
    global patient_service
    local_storage_path = os.environ.get("PATIENT_DATA_PATH", "./patient_data")
    os.makedirs(local_storage_path, exist_ok=True)
    
    patient_service = PatientService(
        fhir_client=fhir_client,
        local_storage_path=local_storage_path
    )
    
    logger.info("EHR services initialized")
    
    yield
    
    logger.info("EHR services shutdown")

# Create FastAPI app
app = FastAPI(
    title="HMS-EHR API",
    description="API for HMS-EHR Component in Crohn's Disease Treatment System",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {"status": "HMS-EHR System is running"}

@app.get("/api/patients")
async def search_patients(
    name: Optional[str] = None,
    identifier: Optional[str] = None,
    gender: Optional[str] = None,
    birthdate: Optional[str] = None
):
    """Search for patients"""
    if not patient_service:
        raise HTTPException(status_code=503, detail="Patient service not initialized")
    
    # Build search params
    params = {}
    if name:
        params["name"] = name
    if identifier:
        params["identifier"] = identifier
    if gender:
        params["gender"] = gender
    if birthdate:
        params["birthdate"] = birthdate
    
    try:
        patients = await patient_service.search_patients(params)
        return {"patients": [patient.to_dict() for patient in patients]}
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    """Get a patient record"""
    if not patient_service:
        raise HTTPException(status_code=503, detail="Patient service not initialized")
    
    try:
        patient = await patient_service.get_patient_record(patient_id)
        return patient.to_dict()
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patients/{patient_id}/assessments")
async def add_assessment(patient_id: str, assessment: AssessmentModel):
    """Add a clinical assessment to a patient record"""
    if not patient_service:
        raise HTTPException(status_code=503, detail="Patient service not initialized")
    
    try:
        # Convert model to Assessment object
        severity = None
        if assessment.severity_assessment:
            try:
                severity = DiseaseSeverity(assessment.severity_assessment)
            except ValueError:
                severity = DiseaseSeverity.UNKNOWN
        
        assessment_obj = Assessment(
            date=assessment.date,
            provider=assessment.provider,
            setting=assessment.setting,
            symptoms=assessment.symptoms,
            physical_findings=assessment.physical_findings,
            disease_activity_index=assessment.disease_activity_index,
            severity_assessment=severity,
            plan=assessment.plan,
            notes=assessment.notes
        )
        
        # Add to patient record
        patient = await patient_service.add_assessment(patient_id, assessment_obj)
        return patient.to_dict()
    except Exception as e:
        logger.error(f"Error adding assessment for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patients/{patient_id}/medications")
async def add_medication(patient_id: str, medication: MedicationModel):
    """Add a medication to a patient record"""
    if not patient_service:
        raise HTTPException(status_code=503, detail="Patient service not initialized")
    
    try:
        # Convert model to Medication object
        medication_obj = Medication(
            name=medication.name,
            code=medication.code,
            system=medication.system,
            dosage=medication.dosage,
            unit=medication.unit,
            route=medication.route,
            frequency=medication.frequency,
            start_date=medication.start_date,
            end_date=medication.end_date,
            status=medication.status,
            reason_stopped=medication.reason_stopped
        )
        
        # Add to patient record
        patient = await patient_service.add_medication(patient_id, medication_obj)
        return patient.to_dict()
    except Exception as e:
        logger.error(f"Error adding medication for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patients/{patient_id}/biomarkers/{biomarker_name}")
async def add_biomarker_value(
    patient_id: str, 
    biomarker_name: str, 
    value: BiomarkerValueModel
):
    """Add a biomarker value to a patient record"""
    if not patient_service:
        raise HTTPException(status_code=503, detail="Patient service not initialized")
    
    try:
        # Convert model to BiomarkerValue object
        value_obj = BiomarkerValue(
            value=value.value,
            unit=value.unit,
            date=value.date,
            reference_range=value.reference_range,
            abnormal=value.abnormal
        )
        
        # Add to patient record
        patient = await patient_service.add_biomarker_value(patient_id, biomarker_name, value_obj)
        return patient.to_dict()
    except Exception as e:
        logger.error(f"Error adding biomarker value for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients/crohns")
async def get_patients_with_crohns():
    """Get all patients with Crohn's disease"""
    if not patient_service:
        raise HTTPException(status_code=503, detail="Patient service not initialized")
    
    try:
        patients = await patient_service.get_patients_with_crohns()
        return {"patients": [patient.to_dict() for patient in patients]}
    except Exception as e:
        logger.error(f"Error getting patients with Crohn's: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if not fhir_client or not patient_service:
        raise HTTPException(status_code=503, detail="EHR services not fully initialized")
    return {"status": "healthy"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HMS-EHR System")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8002, help="Port to bind to")
    args = parser.parse_args()
    
    uvicorn.run("main:app", host=args.host, port=args.port, reload=False)