#!/usr/bin/env python3
"""
Integration Test for EHR Synchronization
This test demonstrates the end-to-end workflow from EHR data synchronization
through privacy controls to integration with the adaptive trial system.
"""
import os
import sys
import json
import asyncio
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import EHR integration components
from data_layer.ehr_integration.fhir_client import FHIRClient
from data_layer.ehr_integration.patient_model import (
    PatientRecord, CrohnsPatientProfile, MedicationRecord, 
    ProcedureRecord, LabResult, DiseaseSeverity
)
from data_layer.ehr_integration.patient_service import PatientService
from data_layer.ehr_integration.sync import (
    DataSyncService, SyncDirection, SyncStatus,
    NotificationService, NotificationType, NotificationPriority,
    PrivacyService, ConsentStatus, DataCategory, UserRole
)

class MockFHIRClient(FHIRClient):
    """Mock FHIR client for testing"""
    def __init__(self, test_data_dir=None):
        super().__init__(base_url="https://example.com/fhir")
        self.test_data_dir = test_data_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "test_data/fhir"
        )
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    async def get_patient(self, patient_id):
        """Mock get patient data"""
        patient_file = os.path.join(self.test_data_dir, f"patient_{patient_id}.json")
        
        # Create test data if it doesn't exist
        if not os.path.exists(patient_file):
            patient_data = {
                "resourceType": "Patient",
                "id": patient_id,
                "name": [{"family": "Test", "given": ["Patient"]}],
                "gender": "male",
                "birthDate": "1980-01-01"
            }
            os.makedirs(os.path.dirname(patient_file), exist_ok=True)
            with open(patient_file, 'w') as f:
                json.dump(patient_data, f)
            return patient_data
        
        # Load existing test data
        with open(patient_file, 'r') as f:
            return json.load(f)
    
    async def search_resources(self, resource_type, parameters=None):
        """Mock search resources"""
        patient_id = parameters.get("patient", "unknown")
        resource_file = os.path.join(
            self.test_data_dir, 
            f"{resource_type.lower()}_{patient_id}.json"
        )
        
        # Create test data if it doesn't exist
        if not os.path.exists(resource_file):
            os.makedirs(os.path.dirname(resource_file), exist_ok=True)
            
            if resource_type == "Condition":
                resources = [
                    {
                        "resourceType": "Condition",
                        "id": f"cond-{patient_id}-1",
                        "subject": {"reference": f"Patient/{patient_id}"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "34000006",
                                    "display": "Crohn's disease"
                                }
                            ]
                        },
                        "onsetDateTime": "2018-01-15",
                        "clinicalStatus": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                    "code": "active"
                                }
                            ]
                        }
                    }
                ]
            elif resource_type == "MedicationStatement":
                resources = [
                    {
                        "resourceType": "MedicationStatement",
                        "id": f"med-{patient_id}-1",
                        "subject": {"reference": f"Patient/{patient_id}"},
                        "status": "active",
                        "medicationCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                                    "code": "1557709",
                                    "display": "Humira 40 MG"
                                }
                            ],
                            "text": "Humira 40 MG"
                        },
                        "effectivePeriod": {
                            "start": "2022-01-01"
                        },
                        "dosage": [
                            {
                                "text": "40 mg every other week"
                            }
                        ]
                    }
                ]
            elif resource_type == "Observation":
                resources = [
                    {
                        "resourceType": "Observation",
                        "id": f"obs-{patient_id}-1",
                        "subject": {"reference": f"Patient/{patient_id}"},
                        "status": "final",
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "2093-3",
                                    "display": "C-reactive protein"
                                }
                            ]
                        },
                        "valueQuantity": {
                            "value": 8.2,
                            "unit": "mg/L",
                            "system": "http://unitsofmeasure.org",
                            "code": "mg/L"
                        },
                        "effectiveDateTime": "2023-01-15"
                    }
                ]
            else:
                resources = []
            
            with open(resource_file, 'w') as f:
                json.dump(resources, f)
            
            return resources
        
        # Load existing test data
        with open(resource_file, 'r') as f:
            return json.load(f)

class TestEHRSync(unittest.TestCase):
    """Test case for EHR synchronization"""
    
    def setUp(self):
        """Set up test environment"""
        # Create test directory
        self.test_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "test_data/ehr_sync"
        )
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create mock FHIR client
        self.fhir_client = MockFHIRClient()
        
        # Create patient service
        self.patient_service = PatientService(
            fhir_client=self.fhir_client,
            data_dir=os.path.join(self.test_dir, "patients")
        )
        
        # Create sync service
        self.sync_service = DataSyncService(
            fhir_client=self.fhir_client,
            patient_service=self.patient_service,
            sync_interval=60,  # 1 minute for testing
            data_dir=os.path.join(self.test_dir, "sync")
        )
        
        # Create notification service
        self.notification_service = NotificationService(
            data_dir=os.path.join(self.test_dir, "notifications")
        )
        
        # Create privacy service
        self.privacy_service = PrivacyService(
            data_dir=os.path.join(self.test_dir, "privacy")
        )
        
        # Create test patient consent
        test_consent = self.privacy_service.get_patient_consent("P12345")
        if not test_consent:
            from data_layer.ehr_integration.sync.privacy_service import PatientConsent
            
            test_consent = PatientConsent(
                patient_id="P12345",
                status=ConsentStatus.GRANTED,
                scope=[
                    DataCategory.DEMOGRAPHICS,
                    DataCategory.DIAGNOSES,
                    DataCategory.MEDICATIONS,
                    DataCategory.PROCEDURES,
                    DataCategory.LAB_RESULTS,
                    DataCategory.VITAL_SIGNS
                ],
                start_date=datetime.now(),
                expiration_date=datetime.now() + timedelta(days=365)
            )
            self.privacy_service.record_patient_consent(test_consent)
    
    async def async_test_sync_workflow(self):
        """Test the complete EHR sync workflow"""
        # 1. Add notification handlers
        email_handler = MagicMock()
        email_handler.handle = MagicMock(return_value=True)
        
        trial_handler = MagicMock()
        trial_handler.handle = MagicMock(return_value=True)
        
        self.notification_service.register_handler(
            NotificationType.MEDICATION_CHANGE, email_handler
        )
        self.notification_service.register_handler(
            NotificationType.LAB_RESULT, email_handler
        )
        
        self.notification_service.register_handler(
            NotificationType.MEDICATION_CHANGE, trial_handler
        )
        self.notification_service.register_handler(
            NotificationType.LAB_RESULT, trial_handler
        )
        
        # 2. Add patient to sync queue
        self.sync_service.add_to_sync_queue(
            patient_id="P12345",
            direction=SyncDirection.IMPORT
        )
        
        # 3. Process sync queue
        await self.sync_service._process_sync_queue()
        
        # 4. Verify patient data was imported
        patient_record = await self.patient_service.get_patient_record("P12345")
        self.assertIsNotNone(patient_record)
        self.assertEqual(patient_record.patient_id, "P12345")
        
        # 5. Check privacy controls
        provider_access = self.privacy_service.check_access(
            requester_id="PROVIDER123",
            requester_role=UserRole.PROVIDER,
            patient_id="P12345",
            category=DataCategory.MEDICATIONS,
            action="read"
        )
        self.assertTrue(provider_access)
        
        researcher_access = self.privacy_service.check_access(
            requester_id="RESEARCHER456",
            requester_role=UserRole.RESEARCHER,
            patient_id="P12345",
            category=DataCategory.MEDICATIONS,
            action="read"
        )
        self.assertTrue(researcher_access)
        
        # 6. Send notifications
        from data_layer.ehr_integration.sync.notification_service import (
            create_medication_change_notification,
            create_lab_result_notification
        )
        
        medication_notification = create_medication_change_notification(
            patient_id="P12345",
            medication_name="Humira",
            change_type="dose_changed",
            details="Increased to 80mg every other week",
            priority=NotificationPriority.HIGH
        )
        
        lab_notification = create_lab_result_notification(
            patient_id="P12345",
            test_name="C-reactive protein",
            result="12 mg/L",
            is_abnormal=True,
            reference_range="0-5 mg/L"
        )
        
        await self.notification_service.publish_notification(medication_notification)
        await self.notification_service.publish_notification(lab_notification)
        
        # 7. Verify notifications were processed
        self.assertEqual(email_handler.handle.call_count, 2)
        self.assertEqual(trial_handler.handle.call_count, 2)
        
        # 8. Perform bidirectional sync
        # First update patient data
        if patient_record:
            # Add new medication
            new_med = MedicationRecord(
                name="Azathioprine",
                dosage="50 mg",
                frequency="twice daily",
                start_date=datetime.now().date(),
                status="active"
            )
            patient_record.crohns_profile.medications.append(new_med)
            
            # Update disease severity
            patient_record.crohns_profile.disease_severity = DiseaseSeverity.MODERATE
            
            # Save updated record
            await self.patient_service.save_patient_record(patient_record)
        
        # Perform bidirectional sync
        self.sync_service.add_to_sync_queue(
            patient_id="P12345",
            direction=SyncDirection.BIDIRECTIONAL
        )
        
        await self.sync_service._process_sync_queue()
        
        # Check sync history
        sync_history = self.sync_service.get_sync_history(patient_id="P12345")
        self.assertGreaterEqual(len(sync_history), 2)
        
        # Verify most recent sync was successful
        latest_sync = sync_history[0]
        self.assertEqual(latest_sync["status"], "completed")
    
    def test_sync_workflow(self):
        """Run the async test"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_test_sync_workflow())

if __name__ == "__main__":
    unittest.main()