"""
Test fixtures and configuration for the Crohn's Disease Treatment System.

This module provides pytest fixtures for testing various components of the system.
"""

import os
import sys
import json
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import required modules
try:
    from coordination.a2a_integration.core import EventBus
    from coordination.a2a_integration.genetic_engine_ffi import GeneticEngineIntegration
    from coordination.a2a_integration.clinical_trial_agent import ClinicalTrialAgent
    from data_layer.ehr_integration.fhir_client import FHIRClient
    from data_layer.ehr_integration.patient_model import Patient, Observation, MedicationRequest
    from data_layer.trial_data.trial_data_transformer import TrialDataTransformer
except ImportError:
    # Mock the modules if they don't exist yet
    EventBus = MagicMock()
    GeneticEngineIntegration = MagicMock()
    ClinicalTrialAgent = MagicMock()
    FHIRClient = MagicMock()
    Patient = MagicMock()
    Observation = MagicMock()
    MedicationRequest = MagicMock()
    TrialDataTransformer = MagicMock()


@pytest.fixture
def event_loop():
    """Create an asyncio event loop for testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def genetic_engine_integration():
    """Create a mock genetic engine integration for testing."""
    integration = MagicMock(spec=GeneticEngineIntegration)
    
    async def optimize_patient_treatment(patient_data):
        """Mock optimize_patient_treatment method"""
        return {
            "treatment_plan": [
                {
                    "medication": "Ustekinumab",
                    "dosage": 90.0,
                    "unit": "mg",
                    "frequency": "every 8 weeks",
                    "duration": 24
                }
            ],
            "fitness": 0.85,
            "confidence": 0.78,
            "explanations": [
                "Treatment plan optimized with 0.85 fitness score.",
                "Ustekinumab selected based on patient's biomarker profile."
            ],
            "biomarker_influences": {
                "NOD2": 0.8,
                "IL23R": 0.7
            }
        }
    
    integration.optimize_patient_treatment.side_effect = optimize_patient_treatment
    return integration


@pytest.fixture
def clinical_trial_agent(event_bus, genetic_engine_integration):
    """Create a clinical trial agent for testing."""
    agent = MagicMock(spec=ClinicalTrialAgent)
    
    async def coordinate_treatment_plan(patient_data, trial_context):
        """Mock coordinate_treatment_plan method"""
        treatment_plan = await genetic_engine_integration.optimize_patient_treatment(patient_data)
        return {
            "patient_id": patient_data.get("patient_id"),
            "treatment_plan": treatment_plan,
            "trial_arm": "Ustekinumab",
            "enrollment_date": "2023-06-01",
            "next_assessment_date": "2023-07-01"
        }
    
    agent.coordinate_treatment_plan.side_effect = coordinate_treatment_plan
    return agent


@pytest.fixture
def fhir_client():
    """Create a mock FHIR client for testing."""
    client = MagicMock(spec=FHIRClient)
    
    async def get_patient(patient_id):
        """Mock get_patient method"""
        return Patient(
            id=patient_id,
            identifiers=[{"system": "urn:mrn", "value": f"MRN-{patient_id}"}],
            family_name="Doe",
            given_names=["John"],
            gender="male",
            birth_date="1980-01-01"
        )
    
    async def get_patient_observations(patient_id, observation_code=None):
        """Mock get_patient_observations method"""
        return [
            Observation(
                id=f"obs-{patient_id}-1",
                status="final",
                code={"coding": [{"system": "http://loinc.org", "code": "CDAI", "display": "Crohn's Disease Activity Index"}]},
                subject_id=patient_id,
                effective_date="2023-05-15",
                value_quantity={"value": 220, "unit": "score"}
            ),
            Observation(
                id=f"obs-{patient_id}-2",
                status="final",
                code={"coding": [{"system": "http://loinc.org", "code": "F-CALPROTECTIN", "display": "Fecal Calprotectin"}]},
                subject_id=patient_id,
                effective_date="2023-05-15",
                value_quantity={"value": 280, "unit": "µg/g"}
            )
        ]
    
    client.get_patient.side_effect = get_patient
    client.get_patient_observations.side_effect = get_patient_observations
    return client


@pytest.fixture
def trial_data_transformer():
    """Create a mock trial data transformer for testing."""
    transformer = MagicMock(spec=TrialDataTransformer)
    
    def transform_patient_for_genetic_engine(patient):
        """Mock transform_patient_for_genetic_engine method"""
        return {
            "patient_id": patient.get("id", "unknown"),
            "age": 42,
            "sex": "male",
            "weight": 70.0,
            "crohns_type": "ileocolonic",
            "severity": "moderate",
            "genetic_markers": {
                "NOD2": "variant",
                "IL23R": "variant"
            },
            "biomarker_values": {
                "CRP": 12.5,
                "ESR": 22
            }
        }
    
    transformer.transform_patient_for_genetic_engine.side_effect = transform_patient_for_genetic_engine
    return transformer


@pytest.fixture
def mock_rust_lib():
    """Create a mock Rust library for testing."""
    with patch("ctypes.CDLL") as mock_cdll:
        mock_lib = MagicMock()
        mock_cdll.return_value = mock_lib
        yield mock_lib


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "patient_id": "P12345",
        "demographics": {
            "age": 42,
            "sex": "female",
            "ethnicity": "Caucasian",
            "weight": 65.5,
            "height": 170.0
        },
        "clinical_data": {
            "crohns_type": "ileocolonic",
            "diagnosis_date": "2019-03-15",
            "disease_activity": {
                "CDAI": 220,
                "SES_CD": 12,
                "fecal_calprotectin": 280,
                "CRP": 12.5,
                "ESR": 22
            }
        },
        "biomarkers": {
            "genetic_markers": [
                {
                    "gene": "NOD2",
                    "variant": "variant",
                    "zygosity": "heterozygous"
                },
                {
                    "gene": "IL23R",
                    "variant": "variant",
                    "zygosity": "heterozygous"
                }
            ],
            "microbiome_profile": {
                "diversity_index": 0.65,
                "key_species": [
                    {
                        "name": "F. prausnitzii",
                        "abundance": 0.15
                    },
                    {
                        "name": "E. coli",
                        "abundance": 0.4
                    }
                ]
            },
            "serum_markers": {
                "CRP": 12.5,
                "ESR": 22
            }
        },
        "treatment_history": [
            {
                "medication": "Infliximab",
                "response": "partial",
                "start_date": "2019-05-01",
                "end_date": "2020-02-15",
                "adverse_events": ["infusion reaction"]
            },
            {
                "medication": "Azathioprine",
                "response": "none",
                "start_date": "2020-03-01",
                "end_date": "2020-09-15",
                "adverse_events": []
            }
        ]
    }


@pytest.fixture
def sample_treatment_plan():
    """Sample treatment plan for testing."""
    return {
        "treatment_plan": [
            {
                "medication": "Ustekinumab",
                "dosage": 90.0,
                "unit": "mg",
                "frequency": "every 8 weeks",
                "duration": 24
            }
        ],
        "fitness": 0.85,
        "confidence": 0.78,
        "explanations": [
            "Treatment plan optimized with 0.85 fitness score.",
            "Ustekinumab selected based on patient's biomarker profile."
        ],
        "biomarker_influences": {
            "NOD2": 0.8,
            "IL23R": 0.7
        }
    }


@pytest.fixture
def sample_trial_protocol():
    """Sample trial protocol for testing."""
    return {
        "trial_id": "CROHNS-001",
        "title": "Adaptive Trial of IL-23 Inhibitors in Crohn's Disease",
        "phase": 2,
        "arms": [
            {
                "armId": "ARM-001",
                "name": "Ustekinumab 90mg",
                "treatment": {
                    "medication": "Ustekinumab",
                    "dosage": "90",
                    "unit": "mg",
                    "frequency": "every 8 weeks"
                },
                "biomarkerStratification": [
                    {
                        "biomarker": "IL23R",
                        "criteria": "variant"
                    }
                ]
            },
            {
                "armId": "ARM-002",
                "name": "Guselkumab 100mg",
                "treatment": {
                    "medication": "Guselkumab",
                    "dosage": "100",
                    "unit": "mg",
                    "frequency": "every 8 weeks"
                },
                "biomarkerStratification": [
                    {
                        "biomarker": "IL23R",
                        "criteria": "variant"
                    }
                ]
            },
            {
                "armId": "ARM-003",
                "name": "Placebo",
                "treatment": {
                    "medication": "Placebo",
                    "dosage": "0",
                    "unit": "mg",
                    "frequency": "every 8 weeks"
                },
                "biomarkerStratification": []
            }
        ],
        "adaptiveRules": [
            {
                "triggerCondition": "interim_analysis_1",
                "action": "response_adaptive_randomization",
                "parameters": {
                    "min_allocation": 0.1
                }
            }
        ],
        "primaryEndpoints": [
            {
                "name": "Clinical Remission",
                "metric": "CDAI < 150",
                "timepoint": "Week 16"
            }
        ],
        "secondaryEndpoints": [
            {
                "name": "Endoscopic Improvement",
                "metric": "SES-CD decrease ≥ 50%",
                "timepoint": "Week 24"
            }
        ]
    }


@pytest.fixture
def sample_genetic_data():
    """Sample genetic sequence data for testing."""
    return {
        "patient_id": "P12345",
        "sequences": {
            "NOD2": "ATGGGCGAGAGGCTGGTCTTCAACCAGCTGCAGGCTGCCCGCAGGGCTCTGGCGGGCCGAGCAGCTGCTTGGCGGGACCCTGCTGCGCGGCAAGGAC",
            "IL23R": "ATGAAAAAATATATTCTTGTACGTGGTTATCTTCTTAGAGACATTGGTATTGCCATTCTTTATATTCTAAATAGTGTTCGGAATACTTCAGATATT",
            "ATG16L1": "ATGGAGTTACAGATTAGAAACAGGTTCCTGTTCCCAGTGCCAGTGTCCTTTCTGCCGGGATCAGCCTCCCAGGAGTGGATAAAAATCACTGAGCTA"
        },
        "demographic": {
            "age": 42,
            "sex": "female",
            "ethnicity": "Caucasian",
            "family_history": True
        },
        "clinical": {
            "diagnosis_age": 40,
            "disease_location": "ileocolonic",
            "disease_behavior": "inflammatory",
            "extraintestinal_manifestations": ["arthritis", "uveitis"],
            "previous_treatments": ["Infliximab", "Azathioprine"],
            "treatment_responses": {
                "Infliximab": "partial",
                "Azathioprine": "none"
            }
        }
    }


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_data_dir(temp_test_dir):
    """Create a test data directory with sample files."""
    data_dir = Path(temp_test_dir) / "test_data"
    data_dir.mkdir(exist_ok=True)
    
    # Create patient data file
    with open(data_dir / "patients.json", "w") as f:
        json.dump({"patients": [sample_patient_data()]}, f)
    
    # Create trial protocol file
    with open(data_dir / "trial_protocol.json", "w") as f:
        json.dump(sample_trial_protocol(), f)
    
    return data_dir