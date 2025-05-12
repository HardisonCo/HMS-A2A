#!/usr/bin/env python3
"""
EHR Data Synchronization Service for Crohn's Disease Treatment System
This module provides a service for synchronizing patient data between
external EHR systems and the internal adaptive trial system.
"""
import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum

# Import FHIR client and patient models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fhir_client import FHIRClient, FHIRException
from patient_model import (
    PatientRecord,
    CrohnsPatientProfile,
    MedicationRecord,
    ProcedureRecord,
    LabResult,
    DiseaseSeverity,
    AdaptiveTrialStatus
)
from patient_service import PatientService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ehr-sync")

class SyncDirection(Enum):
    """Direction of data synchronization"""
    IMPORT = "import"  # From external EHR to internal system
    EXPORT = "export"  # From internal system to external EHR
    BIDIRECTIONAL = "bidirectional"  # Both ways

class SyncStatus(Enum):
    """Status of a synchronization operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class SyncRecord:
    """Record of a synchronization operation"""
    def __init__(
        self,
        patient_id: str,
        direction: SyncDirection,
        resources: List[str],
        status: SyncStatus = SyncStatus.PENDING,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        errors: List[str] = None
    ):
        self.patient_id = patient_id
        self.direction = direction
        self.resources = resources
        self.status = status
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.errors = errors or []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "patient_id": self.patient_id,
            "direction": self.direction.value,
            "resources": self.resources,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "errors": self.errors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncRecord':
        """Create from dictionary representation"""
        return cls(
            patient_id=data["patient_id"],
            direction=SyncDirection(data["direction"]),
            resources=data["resources"],
            status=SyncStatus(data["status"]),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            errors=data.get("errors", [])
        )

class DataSyncService:
    """
    Service for synchronizing patient data between EHR systems and the adaptive trial system.
    Supports importing from external EHR systems, exporting to external systems,
    and bidirectional synchronization.
    """
    def __init__(
        self,
        fhir_client: FHIRClient,
        patient_service: PatientService,
        sync_interval: int = 3600,  # Default 1 hour
        data_dir: str = None
    ):
        self.fhir_client = fhir_client
        self.patient_service = patient_service
        self.sync_interval = sync_interval
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data"
        )
        self.sync_history_path = os.path.join(self.data_dir, "sync_history.json")
        self.sync_queue: List[Tuple[str, SyncDirection, List[str]]] = []
        self.running = False
        self.sync_history: List[SyncRecord] = []
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load sync history if available
        self._load_sync_history()
        
        logger.info(f"Data Sync Service initialized with sync interval: {sync_interval}s")
    
    def _load_sync_history(self) -> None:
        """Load synchronization history from file"""
        if not os.path.exists(self.sync_history_path):
            self.sync_history = []
            return
        
        try:
            with open(self.sync_history_path, 'r') as f:
                history_data = json.load(f)
                self.sync_history = [
                    SyncRecord.from_dict(record) for record in history_data
                ]
            logger.info(f"Loaded {len(self.sync_history)} sync records from history")
        except Exception as e:
            logger.error(f"Error loading sync history: {str(e)}")
            self.sync_history = []
    
    def _save_sync_history(self) -> None:
        """Save synchronization history to file"""
        try:
            # Keep only last 1000 records to prevent file growth
            history_to_save = self.sync_history[-1000:]
            with open(self.sync_history_path, 'w') as f:
                json.dump([record.to_dict() for record in history_to_save], f, indent=2)
            logger.info(f"Saved {len(history_to_save)} sync records to history")
        except Exception as e:
            logger.error(f"Error saving sync history: {str(e)}")
    
    def add_to_sync_queue(
        self,
        patient_id: str,
        direction: SyncDirection,
        resources: List[str] = None
    ) -> None:
        """
        Add a patient to the synchronization queue
        
        Args:
            patient_id: Patient identifier
            direction: Direction of synchronization
            resources: List of resource types to synchronize (e.g., ["Observation", "MedicationStatement"])
                      If None, all relevant resources will be synchronized
        """
        resources = resources or [
            "Patient", "Condition", "Observation", "MedicationStatement",
            "MedicationRequest", "Procedure", "CarePlan"
        ]
        self.sync_queue.append((patient_id, direction, resources))
        logger.info(f"Added patient {patient_id} to sync queue for {direction.value} sync")
    
    async def start(self) -> None:
        """Start the synchronization service"""
        if self.running:
            logger.warning("Data Sync Service is already running")
            return
        
        self.running = True
        logger.info("Data Sync Service started")
        
        try:
            while self.running:
                # Process sync queue
                await self._process_sync_queue()
                
                # Sleep until next sync interval
                await asyncio.sleep(self.sync_interval)
        except Exception as e:
            logger.error(f"Error in Data Sync Service: {str(e)}")
            self.running = False
    
    def stop(self) -> None:
        """Stop the synchronization service"""
        self.running = False
        logger.info("Data Sync Service stopped")
    
    async def _process_sync_queue(self) -> None:
        """Process the synchronization queue"""
        if not self.sync_queue:
            logger.debug("Sync queue is empty, nothing to process")
            return
        
        logger.info(f"Processing sync queue with {len(self.sync_queue)} items")
        
        queue_copy = self.sync_queue.copy()
        self.sync_queue = []
        
        for patient_id, direction, resources in queue_copy:
            sync_record = SyncRecord(
                patient_id=patient_id,
                direction=direction,
                resources=resources,
                status=SyncStatus.IN_PROGRESS
            )
            self.sync_history.append(sync_record)
            
            try:
                if direction == SyncDirection.IMPORT:
                    await self._import_patient_data(patient_id, resources, sync_record)
                elif direction == SyncDirection.EXPORT:
                    await self._export_patient_data(patient_id, resources, sync_record)
                elif direction == SyncDirection.BIDIRECTIONAL:
                    await self._bidirectional_sync(patient_id, resources, sync_record)
                
                sync_record.status = SyncStatus.COMPLETED
                sync_record.end_time = datetime.now()
            except Exception as e:
                error_message = f"Sync error for patient {patient_id}: {str(e)}"
                logger.error(error_message)
                sync_record.errors.append(error_message)
                sync_record.status = SyncStatus.FAILED
                sync_record.end_time = datetime.now()
        
        # Save updated sync history
        self._save_sync_history()
    
    async def _import_patient_data(
        self,
        patient_id: str,
        resources: List[str],
        sync_record: SyncRecord
    ) -> None:
        """
        Import patient data from external EHR to internal system
        
        Args:
            patient_id: Patient identifier
            resources: List of resource types to import
            sync_record: Record of the synchronization operation
        """
        logger.info(f"Importing data for patient {patient_id}, resources: {resources}")
        
        try:
            # Fetch patient data from FHIR server
            patient_data = await self.fhir_client.get_patient(patient_id)
            
            # Fetch additional resources
            resource_data = {}
            for resource_type in resources:
                if resource_type == "Patient":
                    continue  # Already fetched
                
                try:
                    resource_data[resource_type] = await self.fhir_client.search_resources(
                        resource_type=resource_type,
                        parameters={"patient": patient_id}
                    )
                except FHIRException as e:
                    logger.warning(f"Error fetching {resource_type} for patient {patient_id}: {str(e)}")
                    sync_record.errors.append(f"Error fetching {resource_type}: {str(e)}")
            
            # Map FHIR data to internal patient model
            patient_record = self.patient_service.map_fhir_to_patient_record(
                patient_data, resource_data
            )
            
            # Save or update patient record in internal system
            updated = await self.patient_service.save_patient_record(patient_record)
            
            logger.info(f"Successfully imported data for patient {patient_id}")
        except Exception as e:
            logger.error(f"Error importing data for patient {patient_id}: {str(e)}")
            raise
    
    async def _export_patient_data(
        self, 
        patient_id: str, 
        resources: List[str],
        sync_record: SyncRecord
    ) -> None:
        """
        Export patient data from internal system to external EHR
        
        Args:
            patient_id: Patient identifier
            resources: List of resource types to export
            sync_record: Record of the synchronization operation
        """
        logger.info(f"Exporting data for patient {patient_id}, resources: {resources}")
        
        try:
            # Get patient record from internal system
            patient_record = await self.patient_service.get_patient_record(patient_id)
            if not patient_record:
                raise ValueError(f"Patient {patient_id} not found in internal system")
            
            # Map internal patient model to FHIR resources
            fhir_resources = self.patient_service.map_patient_record_to_fhir(
                patient_record, resources
            )
            
            # Update resources in FHIR server
            for resource_type, resources_list in fhir_resources.items():
                for resource in resources_list:
                    try:
                        if "id" in resource:
                            # Update existing resource
                            await self.fhir_client.update_resource(
                                resource_type=resource_type,
                                resource_id=resource["id"],
                                resource=resource
                            )
                        else:
                            # Create new resource
                            await self.fhir_client.create_resource(
                                resource_type=resource_type,
                                resource=resource
                            )
                    except FHIRException as e:
                        logger.warning(f"Error updating {resource_type} for patient {patient_id}: {str(e)}")
                        sync_record.errors.append(f"Error updating {resource_type}: {str(e)}")
            
            logger.info(f"Successfully exported data for patient {patient_id}")
        except Exception as e:
            logger.error(f"Error exporting data for patient {patient_id}: {str(e)}")
            raise
    
    async def _bidirectional_sync(
        self,
        patient_id: str,
        resources: List[str],
        sync_record: SyncRecord
    ) -> None:
        """
        Perform bidirectional synchronization of patient data
        
        Args:
            patient_id: Patient identifier
            resources: List of resource types to synchronize
            sync_record: Record of the synchronization operation
        """
        logger.info(f"Performing bidirectional sync for patient {patient_id}")
        
        # First import data from external EHR
        import_record = SyncRecord(
            patient_id=patient_id,
            direction=SyncDirection.IMPORT,
            resources=resources,
            status=SyncStatus.IN_PROGRESS
        )
        
        try:
            await self._import_patient_data(patient_id, resources, import_record)
            import_record.status = SyncStatus.COMPLETED
            import_record.end_time = datetime.now()
        except Exception as e:
            import_record.status = SyncStatus.FAILED
            import_record.end_time = datetime.now()
            import_record.errors.append(str(e))
            sync_record.errors.append(f"Import phase failed: {str(e)}")
        
        # Then export data to external EHR
        export_record = SyncRecord(
            patient_id=patient_id,
            direction=SyncDirection.EXPORT,
            resources=resources,
            status=SyncStatus.IN_PROGRESS
        )
        
        try:
            await self._export_patient_data(patient_id, resources, export_record)
            export_record.status = SyncStatus.COMPLETED
            export_record.end_time = datetime.now()
        except Exception as e:
            export_record.status = SyncStatus.FAILED
            export_record.end_time = datetime.now()
            export_record.errors.append(str(e))
            sync_record.errors.append(f"Export phase failed: {str(e)}")
        
        # Update sync record status based on import and export phases
        if import_record.status == SyncStatus.COMPLETED and export_record.status == SyncStatus.COMPLETED:
            sync_record.status = SyncStatus.COMPLETED
        elif import_record.status == SyncStatus.FAILED and export_record.status == SyncStatus.FAILED:
            sync_record.status = SyncStatus.FAILED
        else:
            sync_record.status = SyncStatus.PARTIAL
        
        # Add detailed records to history
        self.sync_history.append(import_record)
        self.sync_history.append(export_record)
    
    async def force_sync_all_patients(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    ) -> None:
        """
        Force synchronization of all patients in the system
        
        Args:
            direction: Direction of synchronization
        """
        logger.info(f"Forcing synchronization of all patients in {direction.value} mode")
        
        # Get all patient IDs from internal system
        patient_ids = await self.patient_service.get_all_patient_ids()
        
        # Add all patients to sync queue
        for patient_id in patient_ids:
            self.add_to_sync_queue(patient_id, direction)
        
        # Process sync queue immediately
        await self._process_sync_queue()
    
    def get_sync_history(
        self,
        patient_id: Optional[str] = None,
        status: Optional[SyncStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get synchronization history
        
        Args:
            patient_id: Filter by patient ID
            status: Filter by sync status
            limit: Maximum number of records to return
            
        Returns:
            List of sync history records
        """
        filtered_history = self.sync_history
        
        if patient_id:
            filtered_history = [
                record for record in filtered_history
                if record.patient_id == patient_id
            ]
        
        if status:
            filtered_history = [
                record for record in filtered_history
                if record.status == status
            ]
        
        # Sort by start time (newest first) and limit results
        sorted_history = sorted(
            filtered_history,
            key=lambda record: record.start_time if record.start_time else datetime.min,
            reverse=True
        )
        
        return [record.to_dict() for record in sorted_history[:limit]]

# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='EHR Data Synchronization Service')
    parser.add_argument('--fhir-url', required=True, help='FHIR server URL')
    parser.add_argument('--patient-id', help='Patient ID to synchronize')
    parser.add_argument('--direction', choices=['import', 'export', 'bidirectional'],
                        default='bidirectional', help='Synchronization direction')
    parser.add_argument('--interval', type=int, default=3600,
                        help='Synchronization interval in seconds')
    
    args = parser.parse_args()
    
    # Create FHIR client
    fhir_client = FHIRClient(
        base_url=args.fhir_url,
        auth_token=os.getenv('FHIR_AUTH_TOKEN')
    )
    
    # Create patient service
    patient_service = PatientService(fhir_client)
    
    # Create sync service
    sync_service = DataSyncService(
        fhir_client=fhir_client,
        patient_service=patient_service,
        sync_interval=args.interval
    )
    
    # Add patient to sync queue if specified
    if args.patient_id:
        sync_service.add_to_sync_queue(
            patient_id=args.patient_id,
            direction=SyncDirection(args.direction)
        )
    
    # Start sync service
    try:
        asyncio.run(sync_service.start())
    except KeyboardInterrupt:
        print("Stopping sync service...")
        sync_service.stop()