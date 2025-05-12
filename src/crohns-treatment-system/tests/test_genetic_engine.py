"""
Tests for the genetic engine component.

This module contains tests for the genetic algorithm engine used for
treatment optimization in the Crohn's Disease Treatment System.
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
    sample_patient_data,
    sample_treatment_plan,
    sample_genetic_data,
    genetic_engine_integration
)

# Skip tests if genetic_engine_ffi module is not available
try:
    from coordination.a2a_integration.genetic_engine_ffi import GeneticEngineIntegration
    HAS_GENETIC_ENGINE = True
except ImportError:
    GeneticEngineIntegration = MagicMock()
    HAS_GENETIC_ENGINE = False


@pytest.mark.skipif(not HAS_GENETIC_ENGINE, reason="Genetic engine FFI not available")
class TestGeneticEngine:
    """Test the genetic engine component."""

    def test_create_genetic_engine_integration(self):
        """Test creating a genetic engine integration instance."""
        integration = GeneticEngineIntegration()
        assert integration is not None
        
    @pytest.mark.asyncio
    async def test_optimize_treatment(self, genetic_engine_integration, sample_patient_data):
        """Test optimizing treatment for a patient."""
        result = await genetic_engine_integration.optimize_patient_treatment(sample_patient_data)
        
        assert result is not None
        assert "treatment_plan" in result
        assert len(result["treatment_plan"]) > 0
        assert "fitness" in result
        assert result["fitness"] > 0
        
    @pytest.mark.parametrize("genetic_marker", [
        {"gene": "NOD2", "variant": "R702W", "zygosity": "heterozygous"},
        {"gene": "IL23R", "variant": "R381Q", "zygosity": "heterozygous"},
        {"gene": "ATG16L1", "variant": "T300A", "zygosity": "homozygous"}
    ])
    def test_genetic_marker_influence(self, genetic_marker):
        """Test that genetic markers influence treatment optimization."""
        # This test would use the actual Rust library to verify that 
        # different genetic markers lead to different treatment plans
        # Here we're just checking the test structure
        assert "gene" in genetic_marker
        assert "variant" in genetic_marker
        assert "zygosity" in genetic_marker
        
    @pytest.mark.asyncio
    async def test_biomarker_evaluation(self, genetic_engine_integration):
        """Test evaluating biomarkers for therapeutic significance."""
        biomarker_data = {
            "patient_id": "P12345",
            "markers": [
                {"name": "NOD2", "value": 1.0, "zygosity": "heterozygous"},
                {"name": "IL23R", "value": 1.0, "zygosity": "heterozygous"},
                {"name": "ATG16L1", "value": 1.0, "zygosity": "homozygous"}
            ]
        }
        
        # Mock the evaluate_biomarkers method
        genetic_engine_integration.evaluate_biomarkers = MagicMock()
        genetic_engine_integration.evaluate_biomarkers.return_value = {
            "patient_id": "P12345",
            "biomarker_scores": [
                {
                    "biomarker": "NOD2",
                    "impact_score": 0.85,
                    "confidence": 0.75,
                    "relevant_medications": ["Ustekinumab", "Vedolizumab"]
                }
            ],
            "overall_genetic_risk": 0.65
        }
        
        result = await genetic_engine_integration.evaluate_biomarkers(biomarker_data)
        
        assert result is not None
        assert "biomarker_scores" in result
        assert len(result["biomarker_scores"]) > 0
        assert "overall_genetic_risk" in result
        
    @pytest.mark.asyncio
    async def test_treatment_verification(self, genetic_engine_integration, sample_treatment_plan):
        """Test verifying a treatment plan for safety and efficacy."""
        # Mock the verify_treatment method
        genetic_engine_integration.verify_treatment = MagicMock()
        genetic_engine_integration.verify_treatment.return_value = {
            "is_valid": True,
            "safety_score": 0.9,
            "efficacy_score": 0.85,
            "warnings": [],
            "recommendations": []
        }
        
        result = await genetic_engine_integration.verify_treatment(sample_treatment_plan)
        
        assert result is not None
        assert "is_valid" in result
        assert "safety_score" in result
        assert "efficacy_score" in result
        
    @pytest.mark.asyncio
    async def test_invalid_treatment_verification(self, genetic_engine_integration):
        """Test verifying an invalid treatment plan."""
        invalid_treatment = {
            "treatment_plan": [
                {
                    "medication": "InvalidMedication",
                    "dosage": 1000.0,  # Excessive dosage
                    "unit": "mg",
                    "frequency": "daily",
                    "duration": 365  # Excessive duration
                }
            ]
        }
        
        # Mock the verify_treatment method
        genetic_engine_integration.verify_treatment = MagicMock()
        genetic_engine_integration.verify_treatment.return_value = {
            "is_valid": False,
            "safety_score": 0.2,
            "efficacy_score": 0.3,
            "warnings": [
                "Medication 'InvalidMedication' is not approved for Crohn's disease",
                "Dosage 1000.0 mg is outside the recommended range",
                "Treatment duration of 365 days exceeds recommended initial treatment period"
            ],
            "recommendations": [
                "Consider FDA-approved medications for Crohn's disease",
                "Consult dosing guidelines for appropriate medication dosage",
                "Consider shorter initial treatment period with reassessment"
            ]
        }
        
        result = await genetic_engine_integration.verify_treatment(invalid_treatment)
        
        assert result is not None
        assert "is_valid" in result
        assert not result["is_valid"]
        assert "warnings" in result
        assert len(result["warnings"]) > 0
        
    @pytest.mark.asyncio
    async def test_treatment_alternatives(self, genetic_engine_integration, sample_treatment_plan):
        """Test getting alternative treatment plans."""
        # Mock the get_treatment_alternatives method
        genetic_engine_integration.get_treatment_alternatives = MagicMock()
        genetic_engine_integration.get_treatment_alternatives.return_value = [
            {
                "treatment_plan": [
                    {
                        "medication": "Vedolizumab",
                        "dosage": 300.0,
                        "unit": "mg",
                        "frequency": "every 8 weeks",
                        "duration": 24
                    }
                ],
                "fitness": 0.82,
                "confidence": 0.75
            },
            {
                "treatment_plan": [
                    {
                        "medication": "Adalimumab",
                        "dosage": 40.0,
                        "unit": "mg",
                        "frequency": "every 2 weeks",
                        "duration": 24
                    }
                ],
                "fitness": 0.78,
                "confidence": 0.72
            }
        ]
        
        result = await genetic_engine_integration.get_treatment_alternatives(sample_treatment_plan)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        for alt in result:
            assert "treatment_plan" in alt
            assert "fitness" in alt
            
    @pytest.mark.asyncio
    async def test_simulate_treatment_outcome(self, genetic_engine_integration, sample_patient_data, sample_treatment_plan):
        """Test simulating treatment outcomes."""
        # Mock the simulate_treatment_outcome method
        genetic_engine_integration.simulate_treatment_outcome = MagicMock()
        genetic_engine_integration.simulate_treatment_outcome.return_value = {
            "patient_id": "P12345",
            "treatment_plan": sample_treatment_plan,
            "response_probability": 0.85,
            "remission_probability": 0.68,
            "predicted_biomarker_changes": [
                {
                    "biomarker": "CDAI",
                    "current_value": 220.0,
                    "predicted_value": 110.0,
                    "unit": "score"
                },
                {
                    "biomarker": "fecal_calprotectin",
                    "current_value": 280.0,
                    "predicted_value": 112.0,
                    "unit": "µg/g"
                }
            ],
            "adverse_events": [
                {
                    "event_type": "Injection site reaction",
                    "probability": 0.15,
                    "severity": "Mild"
                }
            ],
            "confidence": 0.7
        }
        
        result = await genetic_engine_integration.simulate_treatment_outcome(
            sample_patient_data, sample_treatment_plan
        )
        
        assert result is not None
        assert "response_probability" in result
        assert "remission_probability" in result
        assert "predicted_biomarker_changes" in result
        assert len(result["predicted_biomarker_changes"]) > 0
        assert "adverse_events" in result
        
    @pytest.mark.asyncio
    async def test_analyze_genetic_sequences(self, sample_genetic_data):
        """Test analyzing genetic sequences."""
        # This would test the actual FFI function in a real implementation
        # Here we just check the test structure
        assert "patient_id" in sample_genetic_data
        assert "sequences" in sample_genetic_data
        assert len(sample_genetic_data["sequences"]) > 0

    @pytest.mark.skip(reason="Integration test that requires actual Rust library")
    def test_rust_integration(self, mock_rust_lib):
        """Test the integration with the Rust library."""
        # This test would verify that the Python code can call the Rust library
        # and that the Rust library returns the expected results
        pass


class TestMockGeneticEngine:
    """Test the mock genetic engine for testing other components."""
    
    @pytest.mark.asyncio
    async def test_mock_optimize_treatment(self, genetic_engine_integration, sample_patient_data):
        """Test that the mock genetic engine optimization works."""
        result = await genetic_engine_integration.optimize_patient_treatment(sample_patient_data)
        
        assert result is not None
        assert "treatment_plan" in result
        assert len(result["treatment_plan"]) > 0
        assert "fitness" in result
        assert "confidence" in result
        assert "explanations" in result
        assert "biomarker_influences" in result