#!/usr/bin/env python3
"""
Integration tests for the Codex-RS integration with the Crohn's Treatment System.

These tests verify that the HMS-A2A coordination system can properly integrate
with the codex-rs components, including the genetic engine, supervisor framework,
and self-healing system.
"""

import os
import sys
import json
import asyncio
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coordination.a2a_integration.codex_rs_integration import CodexRsIntegration
from src.coordination.a2a_integration.genetic_engine_ffi import GeneticEngineFfi
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer

# Sample test data
SAMPLE_PATIENT = {
    "patient_id": "TEST001",
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
            "fecal_calprotectin": 280
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
    ],
    "extraintestinal_manifestations": ["arthritis"],
    "comorbidities": ["asthma"]
}

SAMPLE_TRIAL_PROTOCOL = {
    "trial_id": "CROHNS-001",
    "title": "Adaptive Trial of JAK Inhibitors in Crohn's Disease",
    "phase": 2,
    "arms": [
        {
            "armId": "ARM-001",
            "name": "Upadacitinib 15mg",
            "treatment": {
                "medication": "Upadacitinib",
                "dosage": "15",
                "unit": "mg",
                "frequency": "daily"
            },
            "biomarkerStratification": [
                {
                    "biomarker": "NOD2",
                    "criteria": "variant"
                }
            ]
        },
        {
            "armId": "ARM-002",
            "name": "Upadacitinib 30mg",
            "treatment": {
                "medication": "Upadacitinib",
                "dosage": "30",
                "unit": "mg",
                "frequency": "daily"
            },
            "biomarkerStratification": [
                {
                    "biomarker": "NOD2",
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
                "frequency": "daily"
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
        },
        {
            "triggerCondition": "interim_analysis_2",
            "action": "drop_arm",
            "parameters": {
                "efficacy_threshold": 0.3
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
        },
        {
            "name": "Biomarker Normalization",
            "metric": "CRP < 5 mg/L",
            "timepoint": "Week 16"
        }
    ]
}

class TestCodexRsIntegration(unittest.TestCase):
    """Test suite for the Codex-RS integration"""
    
    def setUp(self):
        """Set up the test environment"""
        self.integration = CodexRsIntegration()
        self.transformer = TrialDataTransformer()
        
        # Create sample data
        self.patient_data = SAMPLE_PATIENT
        self.trial_protocol = SAMPLE_TRIAL_PROTOCOL
        self.patient_cohort = [self.patient_data for _ in range(3)]
        
        # Set up mock responses
        self.mock_treatment_response = {
            "treatment_plan": [
                {
                    "medication": "Upadacitinib",
                    "dosage": 15.0,
                    "unit": "mg",
                    "frequency": "daily",
                    "duration": 30
                }
            ],
            "fitness": 0.85,
            "confidence": 0.78
        }
        
        self.mock_trial_results = {
            "trial_id": "CROHNS-001",
            "status": "completed",
            "patient_outcomes": [
                {
                    "patient_id": "TEST001",
                    "arm": "ARM-001",
                    "response": 0.75,
                    "adverse_events": []
                },
                {
                    "patient_id": "TEST002",
                    "arm": "ARM-002",
                    "response": 0.82,
                    "adverse_events": ["headache"]
                },
                {
                    "patient_id": "TEST003",
                    "arm": "ARM-003",
                    "response": 0.35,
                    "adverse_events": []
                }
            ],
            "adaptations": [
                {
                    "type": "response_adaptive_randomization",
                    "arm_weights": {
                        "ARM-001": 0.35,
                        "ARM-002": 0.55,
                        "ARM-003": 0.1
                    }
                }
            ]
        }
    
    @patch('src.coordination.a2a_integration.genetic_engine_ffi.genetic_engine.optimize_treatment')
    @patch('src.coordination.a2a_integration.genetic_engine_ffi.genetic_engine.initialize')
    async def test_optimize_patient_treatment(self, mock_initialize, mock_optimize):
        """Test optimizing treatment for a patient"""
        # Set up mocks
        mock_initialize.return_value = None
        mock_optimize.return_value = self.mock_treatment_response
        
        # Call the method
        result = await self.integration.optimize_patient_treatment(self.patient_data)
        
        # Check that the initialization was called
        mock_initialize.assert_called_once()
        
        # Check that the optimization was called with the patient data
        mock_optimize.assert_called_once()
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertIn('treatment_plan', result)
        self.assertIn('fitness', result)
        self.assertEqual(result['fitness'], 0.85)
        
        # Check that the treatment plan contains the expected medication
        medications = result['treatment_plan']
        self.assertEqual(len(medications), 1)
        self.assertEqual(medications[0]['medication'], 'Upadacitinib')
        self.assertEqual(medications[0]['dosage'], 15.0)
    
    @patch('src.coordination.a2a_integration.clinical_trial_agent.ClinicalTrialAgent.run_trial')
    @patch('src.coordination.a2a_integration.clinical_trial_agent.ClinicalTrialAgent.set_protocol')
    @patch('src.coordination.a2a_integration.clinical_trial_agent.ClinicalTrialAgent.initialize')
    async def test_run_adaptive_trial(self, mock_init, mock_set_protocol, mock_run_trial):
        """Test running an adaptive trial"""
        # Set up mocks
        mock_init.return_value = None
        mock_set_protocol.return_value = None
        mock_run_trial.return_value = self.mock_trial_results
        
        # Call the method
        result = await self.integration.run_adaptive_trial(
            self.trial_protocol, self.patient_cohort
        )
        
        # Check that the initialization was called
        mock_init.assert_called_once()
        
        # Check that the protocol was set
        mock_set_protocol.assert_called_once_with(self.trial_protocol)
        
        # Check that the trial was run with the patient cohort
        mock_run_trial.assert_called_once_with(self.patient_cohort)
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertEqual(result['trial_id'], 'CROHNS-001')
        self.assertEqual(result['status'], 'completed')
        
        # Check that the patient outcomes are present
        self.assertIn('patient_outcomes', result)
        outcomes = result['patient_outcomes']
        self.assertEqual(len(outcomes), 3)
        
        # Check the adaptations
        self.assertIn('adaptations', result)
        adaptations = result['adaptations']
        self.assertEqual(len(adaptations), 1)
        self.assertEqual(adaptations[0]['type'], 'response_adaptive_randomization')
    
    @patch('src.coordination.a2a_integration.codex_rs_integration.CodexRsIntegration._apply_self_healing')
    @patch('src.coordination.a2a_integration.codex_rs_integration.CodexRsIntegration._needs_healing')
    @patch('src.coordination.a2a_integration.clinical_trial_agent.ClinicalTrialAgent.run_trial')
    @patch('src.coordination.a2a_integration.clinical_trial_agent.ClinicalTrialAgent.set_protocol')
    async def test_self_healing_for_trial(self, mock_set_protocol, mock_run_trial, 
                                         mock_needs_healing, mock_apply_healing):
        """Test self-healing for trial results"""
        # Set up mocks
        mock_set_protocol.return_value = None
        
        # Create error results
        error_results = {
            'trial_id': 'CROHNS-001',
            'status': 'error',
            'patient_outcomes': [],
            'error': 'Simulation failure'
        }
        mock_run_trial.return_value = error_results
        
        # Set up healing needs and response
        mock_needs_healing.return_value = True
        
        # Create healed results
        healed_results = {
            'trial_id': 'CROHNS-001',
            'status': 'completed',
            'healing_applied': True,
            'patient_outcomes': [
                {
                    'patient_id': 'TEST001',
                    'arm': 'placeholder',
                    'response': 0.5,
                    'adverse_events': [],
                    'healed': True
                }
            ],
            'healing_summary': 'Self-healing applied to fix trial results anomalies'
        }
        mock_apply_healing.return_value = healed_results
        
        # Call the method
        result = await self.integration.run_adaptive_trial(
            self.trial_protocol, self.patient_cohort
        )
        
        # Check that healing was needed and applied
        mock_needs_healing.assert_called_once_with(error_results)
        mock_apply_healing.assert_called_once_with(
            error_results, self.trial_protocol, self.patient_cohort
        )
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'completed')
        self.assertTrue(result['healing_applied'])
        self.assertIn('healing_summary', result)
        
        # Check that placeholder outcomes were created
        self.assertIn('patient_outcomes', result)
        outcomes = result['patient_outcomes']
        self.assertEqual(len(outcomes), 1)
        self.assertTrue(outcomes[0]['healed'])
    
    async def test_monitor_system_health(self):
        """Test monitoring system health"""
        # We'll patch multiple methods since this is complex
        with patch('src.coordination.a2a_integration.genetic_engine_ffi.genetic_engine.initialize') as mock_ge_init, \
             patch('src.coordination.a2a_integration.clinical_trial_agent.ClinicalTrialAgent.check_health') as mock_agent_health, \
             patch('src.coordination.a2a_integration.codex_rs_integration.CodexRsIntegration.coordinate_with_supervisor') as mock_supervisor:
            
            # Set up mocks
            mock_ge_init.return_value = None
            mock_agent_health.return_value = {'healthy': True, 'status': 'online'}
            mock_supervisor.return_value = {
                'status': 'healthy',
                'components': {
                    'genetic_engine': 'online',
                    'trial_agent': 'online',
                    'self_healing': 'online'
                }
            }
            
            # Call the method
            health = await self.integration.monitor_system_health()
            
            # Check the result
            self.assertIsNotNone(health)
            self.assertIn('status', health)
            self.assertEqual(health['status'], 'healthy')
            
            # Check the components
            self.assertIn('components', health)
            components = health['components']
            self.assertIn('genetic_engine', components)
            self.assertIn('clinical_trial_agent', components)
            self.assertIn('supervisor', components)
            
            # All components should be healthy
            self.assertEqual(components['genetic_engine']['status'], 'healthy')
            self.assertEqual(components['clinical_trial_agent']['status'], 'healthy')
            self.assertEqual(components['supervisor']['status'], 'healthy')

def async_test(test_case):
    """Decorator for running async test methods"""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_case(*args, **kwargs))
    return wrapper

if __name__ == '__main__':
    unittest.main()