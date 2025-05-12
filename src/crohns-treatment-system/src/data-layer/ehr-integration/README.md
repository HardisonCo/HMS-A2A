# HMS-EHR Integration for Crohn's Disease Treatment System

This component provides integration with Electronic Health Record (EHR) systems to support the Crohn's Disease Treatment System. It handles patient data synchronization, privacy controls, and notifications for changes in patient records.

## Overview

The HMS-EHR integration component is responsible for:

1. **FHIR Integration**: Connecting to EHR systems using the FHIR (Fast Healthcare Interoperability Resources) standard
2. **Data Synchronization**: Bidirectional synchronization of patient data between EHR systems and the adaptive trial system
3. **Privacy Controls**: Managing patient consent and data access policies in compliance with HIPAA regulations
4. **Notifications**: Generating and handling notifications for critical changes in patient data

## Components

### FHIR Client

The `fhir_client.py` module provides a client for interacting with FHIR servers to retrieve and update patient records. It supports various FHIR operations, including:

- Retrieving patient demographics
- Searching for clinical resources by patient
- Updating patient records

### Patient Model

The `patient_model.py` module defines specialized data models for representing Crohn's disease patients, including:

- Patient demographics
- Crohn's disease severity and characteristics
- Medication regimens
- Lab test results
- Treatment history

### Patient Service

The `patient_service.py` module provides services for managing patient records, including:

- Mapping FHIR resources to internal data models
- Retrieving and updating patient records
- Analyzing treatment efficacy and patterns

### Sync Package

The `sync` package provides services for data synchronization, notifications, and privacy controls:

#### Data Synchronization Service

The `sync_service.py` module provides a service for synchronizing patient data between external EHR systems and the internal adaptive trial system. Features include:

- Importing data from EHR systems
- Exporting data to EHR systems
- Bidirectional synchronization
- Tracking sync history and handling errors

#### Notification Service

The `notification_service.py` module manages notifications about patient data changes, including:

- Medication changes
- Lab results
- Disease severity changes
- Adverse events
- Trial status changes

The service supports various notification handlers, including email, webhooks, and direct integration with the trial system.

#### Privacy Service

The `privacy_service.py` module provides privacy controls and data access policies for patient data, ensuring HIPAA compliance and proper patient consent management. Features include:

- Patient consent management
- Role-based access control
- De-identification of patient data
- Access request handling
- Audit logging

## Usage

### Basic EHR Synchronization

```python
from data_layer.ehr_integration.fhir_client import FHIRClient
from data_layer.ehr_integration.patient_service import PatientService
from data_layer.ehr_integration.sync import DataSyncService, SyncDirection

# Initialize components
fhir_client = FHIRClient(base_url="https://fhir.hospital.org/fhir")
patient_service = PatientService(fhir_client)
sync_service = DataSyncService(
    fhir_client=fhir_client,
    patient_service=patient_service
)

# Add patient to sync queue
sync_service.add_to_sync_queue(
    patient_id="P12345",
    direction=SyncDirection.IMPORT
)

# Start sync service
await sync_service.start()
```

### Managing Patient Consent

```python
from data_layer.ehr_integration.sync import (
    PrivacyService, PatientConsent, ConsentStatus, DataCategory
)
from datetime import datetime, timedelta

# Initialize privacy service
privacy_service = PrivacyService()

# Create patient consent
consent = PatientConsent(
    patient_id="P12345",
    status=ConsentStatus.GRANTED,
    scope=[
        DataCategory.DEMOGRAPHICS,
        DataCategory.DIAGNOSES,
        DataCategory.MEDICATIONS,
        DataCategory.LAB_RESULTS
    ],
    start_date=datetime.now(),
    expiration_date=datetime.now() + timedelta(days=365)
)

# Record patient consent
privacy_service.record_patient_consent(consent)

# Check access permissions
has_access = privacy_service.check_access(
    requester_id="PROVIDER123",
    requester_role=UserRole.PROVIDER,
    patient_id="P12345",
    category=DataCategory.MEDICATIONS,
    action="read"
)
```

### Notifications for Patient Data Changes

```python
from data_layer.ehr_integration.sync import (
    NotificationService, NotificationType,
    EmailNotificationHandler, TrialSystemNotificationHandler,
    create_medication_change_notification
)

# Initialize notification service
notification_service = NotificationService()

# Register notification handlers
notification_service.register_handler(
    NotificationType.MEDICATION_CHANGE,
    EmailNotificationHandler(
        smtp_server="smtp.example.com",
        sender_email="alerts@example.com",
        recipient_mapping={"default": "doctor@example.com"}
    )
)

notification_service.register_handler(
    NotificationType.MEDICATION_CHANGE,
    TrialSystemNotificationHandler(
        api_base_url="https://api.trial-system.org"
    )
)

# Create and publish notification
notification = create_medication_change_notification(
    patient_id="P12345",
    medication_name="Humira",
    change_type="dose_changed",
    details="Increased to 80mg every other week"
)

await notification_service.publish_notification(notification)
```

## Integration with Adaptive Trial System

The EHR integration component is designed to work seamlessly with the adaptive trial system:

1. **Data Flow**: Patient data from EHR systems is synchronized with the adaptive trial system, providing up-to-date information for trial management.

2. **Privacy Controls**: The privacy service ensures that only authorized users and components have access to patient data, with appropriate de-identification for research purposes.

3. **Notifications**: The notification service keeps the trial system informed about critical changes in patient status, enabling adaptive adjustments to treatment protocols.

## Testing

To run the integration tests:

```bash
python -m unittest tests/integration/test_ehr_sync.py
```

## Configuration

The component can be configured through environment variables or a configuration file:

- `FHIR_BASE_URL`: URL of the FHIR server
- `FHIR_AUTH_TOKEN`: Authentication token for the FHIR server
- `SYNC_INTERVAL`: Interval in seconds between synchronization runs
- `DATA_DIR`: Directory for storing local data