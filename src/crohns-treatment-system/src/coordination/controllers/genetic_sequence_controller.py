"""
Controller for genetic sequence analysis API endpoints.

This module provides API endpoints for Crohn's disease genetic sequence analysis,
enabling genetic profiling, risk assessment, and treatment optimization.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict, List, Any, Optional

from ..a2a-integration.genetic_sequence_ffi import (
    analyze_patient_sequences,
    get_crohns_variant_info
)
from ..services.patient_service import PatientService
from ..models.genetic_models import (
    PatientGeneticData,
    GeneticAnalysisResponse,
    VariantSignificanceRequest,
    VariantSignificanceResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/genetics/sequence", tags=["genetic-sequence"])

# Dependencies
async def get_patient_service():
    """Dependency for patient service."""
    return PatientService()

@router.post("/analyze", response_model=GeneticAnalysisResponse)
async def analyze_genetic_sequences(
    data: PatientGeneticData,
    patient_service: PatientService = Depends(get_patient_service)
):
    """
    Analyze genetic sequences for a patient to identify relevant Crohn's disease biomarkers.
    
    This endpoint performs:
    - Identification of genetic variants in key Crohn's disease genes
    - Risk assessment based on identified variants
    - Treatment response prediction
    - Personalized treatment recommendations
    
    Returns analysis results including identified variants, risk assessment,
    and treatment recommendations.
    """
    try:
        # Validate patient exists if patient_id is provided
        if data.patient_id:
            if not await patient_service.patient_exists(data.patient_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"Patient with ID {data.patient_id} not found"
                )
        
        # Convert to dict for FFI
        patient_data = data.dict()
        
        # Call FFI function
        analysis_result = await analyze_patient_sequences(patient_data)
        
        # Store results if patient_id is provided
        if data.patient_id:
            await patient_service.store_genetic_analysis(data.patient_id, analysis_result)
        
        return GeneticAnalysisResponse(**analysis_result)
    
    except Exception as e:
        logger.error(f"Error analyzing genetic sequences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze genetic sequences: {str(e)}"
        )

@router.get("/variant/{gene}/{variant}", response_model=VariantSignificanceResponse)
async def get_variant_significance(gene: str, variant: str):
    """
    Get detailed information about a specific genetic variant associated with Crohn's disease.
    
    This endpoint provides:
    - Clinical significance of the variant
    - Description of the variant's effects on disease risk
    - Treatment implications
    - References to scientific literature
    
    Parameters:
    - gene: Name of the gene (e.g., "NOD2", "IL23R", "ATG16L1")
    - variant: Specific variant identifier (e.g., "R702W", "G908R", "1007fs")
    """
    try:
        # Call FFI function
        variant_info = await get_crohns_variant_info(gene, variant)
        
        return VariantSignificanceResponse(**variant_info)
    
    except Exception as e:
        logger.error(f"Error getting variant significance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get variant significance: {str(e)}"
        )

@router.post("/batch-analyze", response_model=List[GeneticAnalysisResponse])
async def batch_analyze_sequences(
    data: List[PatientGeneticData],
    patient_service: PatientService = Depends(get_patient_service)
):
    """
    Analyze genetic sequences for multiple patients in a single request.
    
    This endpoint is useful for batch processing of genetic data for research,
    clinical trials, or population studies.
    """
    try:
        results = []
        
        for patient_data in data:
            # Convert to dict for FFI
            input_data = patient_data.dict()
            
            # Call FFI function
            analysis_result = await analyze_patient_sequences(input_data)
            
            # Store results if patient_id is provided
            if patient_data.patient_id:
                await patient_service.store_genetic_analysis(
                    patient_data.patient_id, 
                    analysis_result
                )
            
            results.append(GeneticAnalysisResponse(**analysis_result))
        
        return results
    
    except Exception as e:
        logger.error(f"Error in batch analysis of genetic sequences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform batch analysis: {str(e)}"
        )