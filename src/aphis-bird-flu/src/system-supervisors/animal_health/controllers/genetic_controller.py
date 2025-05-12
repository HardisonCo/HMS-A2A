"""
Controller for avian influenza genetic analysis services.

This module provides API endpoints for analyzing viral genetic sequences,
identifying mutations, tracking lineages, and inferring transmission
pathways between cases.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from ..models.case import Case
from ..services.genetic_analysis import SequenceAnalyzerService

# Define API models
class SequenceData(BaseModel):
    """Genetic sequence data."""
    sequence: str = Field(..., description="The genetic sequence to analyze")
    subtype: str = Field(..., description="Virus subtype (e.g., H5N1)")
    gene: Optional[str] = Field(None, description="Specific gene (e.g., HA, NA)")
    
    class Config:
        schema_extra = {
            "example": {
                "sequence": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGCAAACAACTCGACAGAGCAGGTTGACACAATAATGGAAAAGAACGTTACTGTTACACATGCCCAAGACATACTGGAAAAGACACACA",
                "subtype": "H5N1",
                "gene": "HA"
            }
        }

class MutationRequest(BaseModel):
    """Parameters for mutation analysis."""
    sequence_data: SequenceData = Field(..., description="Sequence data to analyze")
    
    class Config:
        schema_extra = {
            "example": {
                "sequence_data": {
                    "sequence": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGCAAACAACTCGACAGAGCAGGTTGACACAATAATGGAAAAGAACGTTACTGTTACACATGCCCAAGACATACTGGAAAAGACACACA",
                    "subtype": "H5N1",
                    "gene": "HA"
                }
            }
        }

class LineageRequest(BaseModel):
    """Parameters for lineage assessment."""
    mutations: List[Dict[str, Any]] = Field(..., description="List of mutations identified in the sequence")
    subtype: str = Field(..., description="Virus subtype (e.g., H5N1)")
    
    class Config:
        schema_extra = {
            "example": {
                "mutations": [
                    {
                        "position": 123,
                        "reference": "A",
                        "alternate": "T",
                        "mutation": "A123T",
                        "gene": "HA",
                        "significance": {
                            "phenotype": "unknown",
                            "drug_resistance": False,
                            "transmission": "unknown",
                            "severity": "unknown"
                        }
                    }
                ],
                "subtype": "H5N1"
            }
        }

class AntigenicRequest(BaseModel):
    """Parameters for antigenic property prediction."""
    mutations: List[Dict[str, Any]] = Field(..., description="List of mutations identified in the sequence")
    subtype: str = Field(..., description="Virus subtype (e.g., H5N1)")
    
    class Config:
        schema_extra = {
            "example": {
                "mutations": [
                    {
                        "position": 123,
                        "reference": "A",
                        "alternate": "T",
                        "mutation": "A123T",
                        "gene": "HA",
                        "significance": {
                            "phenotype": "unknown",
                            "drug_resistance": False,
                            "transmission": "unknown",
                            "severity": "unknown"
                        }
                    }
                ],
                "subtype": "H5N1"
            }
        }

class ZoonoticRequest(BaseModel):
    """Parameters for zoonotic potential assessment."""
    mutations: List[Dict[str, Any]] = Field(..., description="List of mutations identified in the sequence")
    subtype: str = Field(..., description="Virus subtype (e.g., H5N1)")
    
    class Config:
        schema_extra = {
            "example": {
                "mutations": [
                    {
                        "position": 123,
                        "reference": "A",
                        "alternate": "T",
                        "mutation": "A123T",
                        "gene": "HA",
                        "significance": {
                            "phenotype": "unknown",
                            "drug_resistance": False,
                            "transmission": "unknown",
                            "severity": "unknown"
                        }
                    }
                ],
                "subtype": "H5N1"
            }
        }

class SequenceComparisonRequest(BaseModel):
    """Parameters for sequence comparison analysis."""
    sequences: Dict[str, str] = Field(..., description="Dictionary mapping sequence identifiers to sequences")
    subtype: str = Field(..., description="Virus subtype (e.g., H5N1)")
    
    class Config:
        schema_extra = {
            "example": {
                "sequences": {
                    "seq1": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGC",
                    "seq2": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGCTACCATGC"
                },
                "subtype": "H5N1"
            }
        }

class PhylogeneticRequest(BaseModel):
    """Parameters for phylogenetic tree construction."""
    sequences: Dict[str, str] = Field(..., description="Dictionary mapping sequence identifiers to sequences")
    method: str = Field("upgma", description="Phylogenetic tree construction method (upgma, nj, ml)")
    
    class Config:
        schema_extra = {
            "example": {
                "sequences": {
                    "seq1": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGC",
                    "seq2": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGCTACCATGC",
                    "seq3": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAATTGATCAGATTTGCATTGGTTACCATGC"
                },
                "method": "upgma"
            }
        }

class TransmissionNetworkRequest(BaseModel):
    """Parameters for transmission network inference."""
    genetic_threshold: float = Field(0.05, description="Maximum genetic distance for potential transmission")
    temporal_window: int = Field(30, description="Maximum time (in days) between potential transmission events")
    spatial_threshold: float = Field(100.0, description="Maximum distance (in km) between potential transmission events")
    
    class Config:
        schema_extra = {
            "example": {
                "genetic_threshold": 0.05,
                "temporal_window": 30,
                "spatial_threshold": 100.0
            }
        }

class TransmissionPatternRequest(BaseModel):
    """Parameters for transmission pattern assessment."""
    network: Dict[str, Any] = Field(..., description="Transmission network from infer_transmission_network")
    
    class Config:
        schema_extra = {
            "example": {
                "network": {
                    "cases": 10,
                    "links": [
                        {
                            "source": "case_1",
                            "target": "case_2",
                            "likelihood": 0.85,
                            "days_apart": 7,
                            "distance_km": 45.2,
                            "genetic_distance": 0.03
                        }
                    ],
                    "network_metrics": {
                        "node_count": 10,
                        "edge_count": 8
                    },
                    "clusters": [
                        {
                            "id": "cluster_1",
                            "cases": ["case_1", "case_2", "case_3"],
                            "metrics": {
                                "size": 3,
                                "edge_count": 2,
                                "density": 0.67
                            }
                        }
                    ]
                }
            }
        }

class SpreadTrajectoryRequest(BaseModel):
    """Parameters for spread trajectory prediction."""
    network: Dict[str, Any] = Field(..., description="Transmission network from infer_transmission_network")
    days_ahead: int = Field(14, description="Number of days to predict ahead")
    
    class Config:
        schema_extra = {
            "example": {
                "network": {
                    "cases": 10,
                    "links": [
                        {
                            "source": "case_1",
                            "target": "case_2",
                            "likelihood": 0.85,
                            "days_apart": 7,
                            "distance_km": 45.2,
                            "genetic_distance": 0.03
                        }
                    ]
                },
                "days_ahead": 14
            }
        }

# Create router
router = APIRouter(
    prefix="/api/v1/genetic",
    tags=["genetic analysis"],
    responses={404: {"description": "Not found"}},
)

# Service dependencies
def get_sequence_analyzer_service():
    """Dependency to get sequence analyzer service instance."""
    # In production, this would load reference sequences and mutation database
    return SequenceAnalyzerService()

# Data access dependencies
def get_case_repository():
    """Dependency to get case repository."""
    # This would be implemented based on your data access layer
    return None

# API endpoints
@router.post("/sequences/analyze", response_model=Dict[str, Any])
async def analyze_sequence(
    sequence_data: SequenceData,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Perform comprehensive analysis of a viral sequence, including mutation identification,
    lineage assessment, antigenic property prediction, and zoonotic potential assessment.
    """
    result = service.analyze_sequence(
        sequence_data=sequence_data.sequence,
        subtype=sequence_data.subtype,
        gene=sequence_data.gene
    )

    return result

@router.post("/sequences/mutations", response_model=List[Dict[str, Any]])
async def identify_mutations(
    request: MutationRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Identify mutations in a viral genetic sequence compared to a reference sequence.
    """
    sequence_data = request.sequence_data

    mutations = service.identify_mutations(
        sequence=sequence_data.sequence,
        subtype=sequence_data.subtype,
        gene=sequence_data.gene
    )

    return mutations

@router.post("/sequences/lineage", response_model=Dict[str, Any])
async def assess_lineage(
    request: LineageRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Determine the lineage of a virus based on its mutations.
    """
    lineage_info = service.assess_lineage(
        mutations=request.mutations,
        subtype=request.subtype
    )

    return lineage_info

@router.post("/sequences/antigenic", response_model=Dict[str, Any])
async def predict_antigenic_properties(
    request: AntigenicRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Predict antigenic properties based on identified mutations.
    """
    antigenic_properties = service.predict_antigenic_properties(
        mutations=request.mutations,
        subtype=request.subtype
    )

    return antigenic_properties

@router.post("/sequences/zoonotic", response_model=Dict[str, Any])
async def assess_zoonotic_potential(
    request: ZoonoticRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Assess the zoonotic potential of a virus based on its mutations.
    """
    zoonotic_potential = service.assess_zoonotic_potential(
        mutations=request.mutations,
        subtype=request.subtype
    )

    return zoonotic_potential

@router.post("/sequences/compare", response_model=Dict[str, Any])
async def compare_sequences(
    request: SequenceComparisonRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Perform comparative analysis of multiple sequences.
    """
    comparison_result = service.compare_sequences(
        sequences=request.sequences,
        subtype=request.subtype
    )

    return comparison_result

@router.post("/phylogenetic/tree", response_model=Dict[str, Any])
async def build_phylogenetic_tree(
    request: PhylogeneticRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Build a phylogenetic tree from a set of sequences.
    """
    tree = service.build_phylogenetic_tree(
        sequences=request.sequences,
        method=request.method
    )

    return tree

@router.post("/transmission/network", response_model=Dict[str, Any])
async def infer_transmission_network(
    request: TransmissionNetworkRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service),
    case_repo = Depends(get_case_repository)
):
    """
    Infer a transmission network from a set of cases.
    """
    # Get all recent cases
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Get cases from the last 90 days
    cases = case_repo.get_cases_by_date_range(
        start_date.isoformat(),
        end_date.isoformat()
    )

    # Infer transmission network
    network = service.infer_transmission_network(
        cases=cases,
        genetic_threshold=request.genetic_threshold,
        temporal_window=request.temporal_window,
        spatial_threshold=request.spatial_threshold
    )

    return network

@router.post("/transmission/pattern", response_model=Dict[str, Any])
async def assess_transmission_pattern(
    request: TransmissionPatternRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service)
):
    """
    Assess the overall transmission pattern from a network.
    """
    pattern = service.assess_transmission_pattern(
        network=request.network
    )

    return pattern

@router.post("/transmission/trajectory", response_model=Dict[str, Any])
async def predict_spread_trajectory(
    request: SpreadTrajectoryRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service),
    case_repo = Depends(get_case_repository)
):
    """
    Predict the spread trajectory based on the transmission network.
    """
    # Get all recent cases
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Get cases from the last 90 days
    cases = case_repo.get_cases_by_date_range(
        start_date.isoformat(),
        end_date.isoformat()
    )

    # Predict trajectory
    trajectory = service.predict_spread_trajectory(
        network=request.network,
        cases=cases,
        days_ahead=request.days_ahead
    )

    return trajectory

@router.post("/transmission/dynamics", response_model=Dict[str, Any])
async def analyze_transmission_dynamics(
    request: TransmissionNetworkRequest,
    service: SequenceAnalyzerService = Depends(get_sequence_analyzer_service),
    case_repo = Depends(get_case_repository)
):
    """
    Perform comprehensive analysis of transmission dynamics.
    """
    # Get all recent cases
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Get cases from the last 90 days
    cases = case_repo.get_cases_by_date_range(
        start_date.isoformat(),
        end_date.isoformat()
    )

    # Analyze dynamics
    dynamics = service.analyze_transmission_dynamics(
        cases=cases,
        temporal_window=request.temporal_window,
        spatial_threshold=request.spatial_threshold
    )

    return dynamics