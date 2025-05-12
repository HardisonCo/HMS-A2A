"""
Models for genetic sequence analysis and related operations.

This module defines data models for Crohn's disease genetic analysis,
including patient genetic data, analysis results, and variant information.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union

class GeneticSequence(BaseModel):
    """Model for a genetic sequence."""
    gene: str = Field(..., description="Name of the gene")
    sequence: str = Field(..., description="Nucleotide sequence")
    source: Optional[str] = Field(None, description="Source of the sequence data")
    quality_score: Optional[float] = Field(None, description="Quality score of the sequence")

class DemographicInfo(BaseModel):
    """Model for patient demographic information."""
    age: Optional[int] = Field(None, description="Patient age")
    sex: Optional[str] = Field(None, description="Patient biological sex")
    ethnicity: Optional[str] = Field(None, description="Patient ethnicity")
    family_history: Optional[bool] = Field(None, description="Family history of Crohn's disease")

class ClinicalInfo(BaseModel):
    """Model for patient clinical information."""
    diagnosis_age: Optional[int] = Field(None, description="Age at diagnosis")
    disease_location: Optional[str] = Field(None, description="Location of disease (ileal, colonic, ileocolonic)")
    disease_behavior: Optional[str] = Field(None, description="Disease behavior (inflammatory, stricturing, penetrating)")
    extraintestinal_manifestations: Optional[List[str]] = Field(None, description="Extraintestinal manifestations")
    previous_treatments: Optional[List[str]] = Field(None, description="Previous treatments")
    treatment_responses: Optional[Dict[str, str]] = Field(None, description="Responses to previous treatments")

class PatientGeneticData(BaseModel):
    """Model for patient genetic data input."""
    patient_id: Optional[str] = Field(None, description="Unique identifier for the patient")
    sequences: Dict[str, str] = Field(..., description="Dictionary mapping gene names to sequences")
    demographic: Optional[DemographicInfo] = Field(None, description="Demographic information")
    clinical: Optional[ClinicalInfo] = Field(None, description="Clinical information")
    
    @validator('sequences')
    def validate_sequences(cls, v):
        """Validate that required genes are present."""
        required_genes = ['NOD2', 'IL23R', 'ATG16L1']
        missing_genes = [gene for gene in required_genes if gene not in v]
        if missing_genes:
            raise ValueError(f"Missing required gene sequences: {', '.join(missing_genes)}")
        return v

class GeneticVariant(BaseModel):
    """Model for a genetic variant."""
    gene: str = Field(..., description="Name of the gene")
    variant_id: str = Field(..., description="Identifier of the variant")
    nucleotide_change: str = Field(..., description="Nucleotide change description")
    protein_change: Optional[str] = Field(None, description="Protein change description")
    zygosity: str = Field(..., description="Zygosity (heterozygous, homozygous)")
    clinical_significance: str = Field(..., description="Clinical significance")
    impact_score: float = Field(..., description="Impact score (0-1)")
    description: str = Field(..., description="Description of the variant")

class RiskAssessment(BaseModel):
    """Model for genetic risk assessment."""
    overall_risk: str = Field(..., description="Overall risk level (low, moderate, high)")
    risk_score: float = Field(..., description="Numeric risk score (0-1)")
    contributing_factors: List[Dict[str, Any]] = Field(..., description="Factors contributing to risk")
    confidence: float = Field(..., description="Confidence in the risk assessment (0-1)")

class TreatmentRecommendation(BaseModel):
    """Model for treatment recommendation."""
    treatment: str = Field(..., description="Recommended treatment")
    expected_efficacy: float = Field(..., description="Expected efficacy score (0-1)")
    genetic_basis: List[Dict[str, Any]] = Field(..., description="Genetic basis for recommendation")
    confidence: float = Field(..., description="Confidence in recommendation (0-1)")
    contraindications: Optional[List[str]] = Field(None, description="Potential contraindications")

class GeneticAnalysisResponse(BaseModel):
    """Model for genetic analysis response."""
    variants: List[GeneticVariant] = Field(..., description="List of identified genetic variants")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")
    treatment_recommendations: List[TreatmentRecommendation] = Field(..., description="Treatment recommendations")
    analysis_id: Optional[str] = Field(None, description="Unique identifier for the analysis")
    analysis_timestamp: Optional[str] = Field(None, description="Timestamp of the analysis")

class VariantSignificanceRequest(BaseModel):
    """Model for variant significance request."""
    gene: str = Field(..., description="Name of the gene")
    variant: str = Field(..., description="Identifier of the variant")

class LiteratureReference(BaseModel):
    """Model for a literature reference."""
    title: str = Field(..., description="Title of the publication")
    authors: List[str] = Field(..., description="Authors of the publication")
    journal: str = Field(..., description="Journal of publication")
    year: int = Field(..., description="Year of publication")
    doi: Optional[str] = Field(None, description="DOI of the publication")
    pubmed_id: Optional[str] = Field(None, description="PubMed ID")
    key_findings: str = Field(..., description="Key findings related to the variant")

class VariantSignificanceResponse(BaseModel):
    """Model for variant significance response."""
    gene: str = Field(..., description="Name of the gene")
    variant: str = Field(..., description="Identifier of the variant")
    significance: str = Field(..., description="Clinical significance")
    description: str = Field(..., description="Description of the variant's effects")
    impact_on_disease: str = Field(..., description="Impact on Crohn's disease")
    frequency: Optional[Dict[str, float]] = Field(None, description="Frequency in different populations")
    treatment_implications: List[Dict[str, Any]] = Field(..., description="Implications for treatment")
    literature: List[LiteratureReference] = Field(..., description="Scientific literature references")