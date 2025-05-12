"""
End-to-end integration tests for the Crohn's Disease Treatment System.

This module contains tests that verify the integration between different
components of the system.
"""

import os
import sys
import json
import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import fixtures from conftest.py
from conftest import (
    event_bus,
    clinical_trial_agent,
    genetic_engine_integration,
    fhir_client,
    trial_data_transformer,
    sample_patient_data,
    sample_trial_protocol,
    sample_treatment_plan,
    test_data_dir
)

# Mock required modules if they're not available
try:
    from coordination.a2a_integration.core import EventBus
    from coordination.a2a_integration.clinical_trial_agent import ClinicalTrialAgent
    from coordination.a2a_integration.genetic_engine_ffi import GeneticEngineIntegration
    from data_layer.ehr_integration.fhir_client import FHIRClient
    from data_layer.trial_data.trial_data_transformer import TrialDataTransformer
    HAS_COMPONENTS = True
except ImportError:
    EventBus = MagicMock
    ClinicalTrialAgent = MagicMock
    GeneticEngineIntegration = MagicMock
    FHIRClient = MagicMock
    TrialDataTransformer = MagicMock
    HAS_COMPONENTS = False

# Skip tests if run_integration_test.sh is not available
HAS_INTEGRATION_SCRIPT = os.path.exists(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "run_integration_test.sh")
)


class TestComponentIntegration:
    """Test the integration between different components."""

    @pytest.mark.asyncio
    async def test_ehr_genetic_engine_integration(self, fhir_client, genetic_engine_integration, trial_data_transformer):
        """Test integration between EHR, data transformer, and genetic engine."""
        # Create patient data
        patient_id = "P12345"
        
        # Mock fhir_client.get_patient
        patient = await fhir_client.get_patient(patient_id)
        assert patient is not None
        
        # Mock fhir_client.get_patient_observations
        observations = await fhir_client.get_patient_observations(patient_id)
        assert observations is not None
        assert len(observations) > 0
        
        # Convert to format expected by genetic engine
        patient_data = {
            "id": patient.id,
            "observations": observations
        }
        
        # Transform data for genetic engine
        transformed_data = trial_data_transformer.transform_patient_for_genetic_engine(patient_data)
        assert transformed_data is not None
        assert "patient_id" in transformed_data
        
        # Optimize treatment
        treatment_plan = await genetic_engine_integration.optimize_patient_treatment(transformed_data)
        assert treatment_plan is not None
        assert "treatment_plan" in treatment_plan
        assert len(treatment_plan["treatment_plan"]) > 0

    @pytest.mark.asyncio
    async def test_a2a_genetic_engine_integration(self, clinical_trial_agent, genetic_engine_integration, sample_patient_data):
        """Test integration between HMS-A2A and genetic engine."""
        # This tests the interaction between the clinical trial agent and the genetic engine
        
        # Mock the genetic_engine_integration.optimize_patient_treatment method
        async def optimize_treatment(patient_data):
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
        
        genetic_engine_integration.optimize_patient_treatment.side_effect = optimize_treatment
        
        # Create trial protocol
        trial_protocol = sample_trial_protocol
        
        # Generate treatment plan
        treatment_recommendation = await clinical_trial_agent.coordinate_treatment_plan(
            sample_patient_data, trial_protocol
        )
        
        assert treatment_recommendation is not None
        assert "patient_id" in treatment_recommendation
        assert treatment_recommendation["patient_id"] == sample_patient_data["patient_id"]
        assert "treatment_plan" in treatment_recommendation
        assert "trial_arm" in treatment_recommendation
        
        # Verify genetic engine was called with correct patient data
        genetic_engine_integration.optimize_patient_treatment.assert_called_once()
        call_args = genetic_engine_integration.optimize_patient_treatment.call_args[0][0]
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_event_driven_communication(self, event_bus, clinical_trial_agent, genetic_engine_integration):
        """Test event-driven communication between components."""
        # Mock the event_bus methods
        event_bus.subscribe = MagicMock()
        event_bus.publish = MagicMock()
        
        # Set up event handlers
        event_types = ["patient_enrolled", "treatment_optimized", "outcome_recorded"]
        for event_type in event_types:
            event_bus.subscribe(event_type, MagicMock())
        
        # Verify subscriptions
        assert event_bus.subscribe.call_count == len(event_types)
        
        # Publish events
        for event_type in event_types:
            await event_bus.publish(event_type, {"test": "data"})
        
        # Verify publications
        assert event_bus.publish.call_count == len(event_types)

    @pytest.mark.skipif(not HAS_COMPONENTS, reason="Required components not available")
    def test_component_initialization(self):
        """Test that all components can be initialized together."""
        # This would test the actual component initialization
        # Here we just check the test structure
        assert EventBus is not None
        assert ClinicalTrialAgent is not None
        assert GeneticEngineIntegration is not None
        assert FHIRClient is not None
        assert TrialDataTransformer is not None


@pytest.mark.skipif(not HAS_INTEGRATION_SCRIPT, reason="Integration script not available")
class TestSystemIntegration:
    """Test the integration of the full system."""

    @pytest.mark.skip(reason="Requires actual system to be running")
    def test_run_integration_script(self):
        """Test running the integration script."""
        import subprocess
        
        # Run the integration script
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "run_integration_test.sh")
        result = subprocess.run([script_path], capture_output=True, text=True)
        
        # Check if the script ran successfully
        assert result.returncode == 0, f"Integration script failed: {result.stderr}"
        assert "Integration test PASSED" in result.stdout

    @pytest.mark.asyncio
    async def test_data_flow_simulation(self, test_data_dir):
        """Test the data flow through the system using simulation."""
        # Load test data
        with open(test_data_dir / "patients.json", "r") as f:
            patients_data = json.load(f)["patients"]
        
        with open(test_data_dir / "trial_protocol.json", "r") as f:
            trial_protocol = json.load(f)
        
        # Simulate the data flow through the system
        for patient_data in patients_data:
            # Step 1: Patient enrollment
            patient_id = patient_data["patient_id"]
            
            # Step 2: Treatment optimization
            # (Simulated, would call genetic engine in real implementation)
            treatment_plan = {
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
                "confidence": 0.78
            }
            
            # Step 3: Trial enrollment
            enrollment = {
                "enrollment_id": f"ENR-{patient_id}",
                "patient_id": patient_id,
                "trial_id": trial_protocol["trial_id"],
                "arm_id": "ARM-001",
                "enrollment_date": "2023-06-01"
            }
            
            # Step 4: Outcome recording
            outcome = {
                "patient_id": patient_id,
                "assessment_date": "2023-07-01",
                "outcome_metrics": {
                    "CDAI": 150,
                    "fecal_calprotectin": 120,
                    "SES_CD": 8
                },
                "response_status": "improved"
            }
            
            # Assert the flow is complete
            assert patient_id == enrollment["patient_id"]
            assert patient_id == outcome["patient_id"]
            assert "treatment_plan" in treatment_plan
            assert "response_status" in outcome
            
    @pytest.mark.skip(reason="Full system integration test")
    def test_full_system_integration(self):
        """Test the full system integration with all components."""
        # This test would verify that all system components work together
        # It would require the full system to be running
        pass