"""
Service for patient data operations including genetic analysis storage and retrieval.

This module handles patient data operations for the Crohn's treatment system,
including storing and retrieving genetic analysis results.
"""

import json
import logging
import aiofiles
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid

# Configure logging
logger = logging.getLogger(__name__)

class PatientService:
    """Service for patient data operations."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the patient service.
        
        Args:
            data_dir: Directory for patient data. Defaults to data/patients.
        """
        if data_dir is None:
            base_dir = Path(__file__).parent.parent.parent.parent
            self.data_dir = base_dir / "data" / "patients"
        else:
            self.data_dir = Path(data_dir)
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Cache for patient data
        self._patient_cache = {}
    
    async def patient_exists(self, patient_id: str) -> bool:
        """
        Check if a patient exists.
        
        Args:
            patient_id: Unique identifier for the patient
        
        Returns:
            True if the patient exists, False otherwise
        """
        patient_file = self.data_dir / f"{patient_id}.json"
        return patient_file.exists()
    
    async def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient data.
        
        Args:
            patient_id: Unique identifier for the patient
        
        Returns:
            Dictionary containing patient data
        
        Raises:
            FileNotFoundError: If the patient does not exist
        """
        # Check cache first
        if patient_id in self._patient_cache:
            return self._patient_cache[patient_id]
        
        patient_file = self.data_dir / f"{patient_id}.json"
        if not patient_file.exists():
            raise FileNotFoundError(f"Patient with ID {patient_id} not found")
        
        async with aiofiles.open(patient_file, "r") as f:
            patient_data = json.loads(await f.read())
            
            # Cache the data
            self._patient_cache[patient_id] = patient_data
            
            return patient_data
    
    async def store_patient(self, patient_data: Dict[str, Any]) -> str:
        """
        Store patient data.
        
        Args:
            patient_data: Dictionary containing patient data
                Must include a patient_id field or one will be generated
        
        Returns:
            Patient ID
        """
        # Generate patient ID if not provided
        if "patient_id" not in patient_data or not patient_data["patient_id"]:
            patient_data["patient_id"] = str(uuid.uuid4())
        
        patient_id = patient_data["patient_id"]
        
        # Update timestamps
        if "created_at" not in patient_data:
            patient_data["created_at"] = datetime.now().isoformat()
        
        patient_data["updated_at"] = datetime.now().isoformat()
        
        # Store data
        patient_file = self.data_dir / f"{patient_id}.json"
        async with aiofiles.open(patient_file, "w") as f:
            await f.write(json.dumps(patient_data, indent=2))
        
        # Update cache
        self._patient_cache[patient_id] = patient_data
        
        return patient_id
    
    async def store_genetic_analysis(
        self, patient_id: str, analysis_result: Dict[str, Any]
    ) -> None:
        """
        Store genetic analysis results for a patient.
        
        Args:
            patient_id: Unique identifier for the patient
            analysis_result: Dictionary containing analysis results
        
        Raises:
            FileNotFoundError: If the patient does not exist
        """
        try:
            # Get existing patient data
            patient_data = await self.get_patient(patient_id)
            
            # Add analysis ID and timestamp if not present
            if "analysis_id" not in analysis_result:
                analysis_result["analysis_id"] = str(uuid.uuid4())
            
            if "analysis_timestamp" not in analysis_result:
                analysis_result["analysis_timestamp"] = datetime.now().isoformat()
            
            # Store analysis in patient data
            if "genetic_analyses" not in patient_data:
                patient_data["genetic_analyses"] = []
            
            patient_data["genetic_analyses"].append(analysis_result)
            
            # Update patient data
            await self.store_patient(patient_data)
            
            # Store detailed analysis separately for faster retrieval
            analysis_dir = self.data_dir / patient_id / "genetic_analyses"
            os.makedirs(analysis_dir, exist_ok=True)
            
            analysis_file = analysis_dir / f"{analysis_result['analysis_id']}.json"
            async with aiofiles.open(analysis_file, "w") as f:
                await f.write(json.dumps(analysis_result, indent=2))
            
            logger.info(f"Stored genetic analysis {analysis_result['analysis_id']} for patient {patient_id}")
            
        except FileNotFoundError:
            # Create new patient record if it doesn't exist
            patient_data = {
                "patient_id": patient_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "genetic_analyses": [analysis_result]
            }
            
            # Add analysis ID and timestamp if not present
            if "analysis_id" not in analysis_result:
                analysis_result["analysis_id"] = str(uuid.uuid4())
            
            if "analysis_timestamp" not in analysis_result:
                analysis_result["analysis_timestamp"] = datetime.now().isoformat()
            
            # Store patient data
            await self.store_patient(patient_data)
            
            # Store detailed analysis separately for faster retrieval
            analysis_dir = self.data_dir / patient_id / "genetic_analyses"
            os.makedirs(analysis_dir, exist_ok=True)
            
            analysis_file = analysis_dir / f"{analysis_result['analysis_id']}.json"
            async with aiofiles.open(analysis_file, "w") as f:
                await f.write(json.dumps(analysis_result, indent=2))
            
            logger.info(f"Created new patient {patient_id} with genetic analysis {analysis_result['analysis_id']}")
    
    async def get_genetic_analyses(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all genetic analyses for a patient.
        
        Args:
            patient_id: Unique identifier for the patient
        
        Returns:
            List of dictionaries containing analysis results
        
        Raises:
            FileNotFoundError: If the patient does not exist
        """
        patient_data = await self.get_patient(patient_id)
        
        return patient_data.get("genetic_analyses", [])
    
    async def get_genetic_analysis(self, patient_id: str, analysis_id: str) -> Dict[str, Any]:
        """
        Get a specific genetic analysis for a patient.
        
        Args:
            patient_id: Unique identifier for the patient
            analysis_id: Unique identifier for the analysis
        
        Returns:
            Dictionary containing analysis results
        
        Raises:
            FileNotFoundError: If the patient or analysis does not exist
        """
        # Try to get from detailed storage first
        analysis_file = self.data_dir / patient_id / "genetic_analyses" / f"{analysis_id}.json"
        
        if analysis_file.exists():
            async with aiofiles.open(analysis_file, "r") as f:
                return json.loads(await f.read())
        
        # Fall back to patient data
        patient_data = await self.get_patient(patient_id)
        
        for analysis in patient_data.get("genetic_analyses", []):
            if analysis.get("analysis_id") == analysis_id:
                return analysis
        
        raise FileNotFoundError(f"Genetic analysis {analysis_id} for patient {patient_id} not found")