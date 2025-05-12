#!/usr/bin/env python3
"""
FHIR Client for Crohn's Disease Treatment System

This module provides a client for interacting with FHIR (Fast Healthcare 
Interoperability Resources) servers to retrieve and update patient records.
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
import datetime
from urllib.parse import urljoin
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ehr.fhir-client')

class ResourceType(Enum):
    """FHIR resource types"""
    PATIENT = "Patient"
    CONDITION = "Condition"
    OBSERVATION = "Observation"
    MEDICATION = "Medication"
    MEDICATION_REQUEST = "MedicationRequest"
    MEDICATION_ADMINISTRATION = "MedicationAdministration"
    PROCEDURE = "Procedure"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    IMMUNIZATION = "Immunization"
    CARE_PLAN = "CarePlan"
    ENCOUNTER = "Encounter"
    DOCUMENT_REFERENCE = "DocumentReference"

class FHIRClient:
    """Client for interacting with FHIR servers"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the FHIR client"""
        self.base_url = base_url
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expiry = None
        self.logger = logging.getLogger('ehr.fhir-client')
        
        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 300  # Cache time-to-live in seconds (5 minutes)
    
    async def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """Get a patient resource by ID"""
        return await self._get_resource(ResourceType.PATIENT, patient_id)
    
    async def search_patients(self, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Search for patients matching criteria"""
        return await self._search_resources(ResourceType.PATIENT, params)
    
    async def get_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get conditions for a patient"""
        return await self._search_resources(ResourceType.CONDITION, {"patient": patient_id})
    
    async def get_crohns_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get Crohn's disease conditions for a patient"""
        # Crohn's disease ICD-10 code
        return await self._search_resources(ResourceType.CONDITION, {
            "patient": patient_id,
            "code": "K50.00,K50.01,K50.10,K50.11,K50.80,K50.81,K50.90,K50.91"
        })
    
    async def get_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get medications for a patient"""
        return await self._search_resources(ResourceType.MEDICATION_REQUEST, {"patient": patient_id})
    
    async def get_observations(self, patient_id: str, code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get observations for a patient, optionally filtered by code"""
        params = {"patient": patient_id}
        if code:
            params["code"] = code
        return await self._search_resources(ResourceType.OBSERVATION, params)
    
    async def get_inflammatory_markers(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get inflammatory markers (CRP, ESR, etc.) for a patient"""
        # LOINC codes for common inflammatory markers
        loinc_codes = "1988-5,30522-7,2857-1,2458-8"  # CRP, hs-CRP, Fecal Calprotectin, ESR
        return await self._search_resources(ResourceType.OBSERVATION, {
            "patient": patient_id,
            "code": loinc_codes
        })
    
    async def get_diagnostic_reports(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get diagnostic reports for a patient"""
        return await self._search_resources(ResourceType.DIAGNOSTIC_REPORT, {"patient": patient_id})
    
    async def get_procedures(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get procedures for a patient"""
        return await self._search_resources(ResourceType.PROCEDURE, {"patient": patient_id})
    
    async def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new patient resource"""
        return await self._create_resource(ResourceType.PATIENT, patient_data)
    
    async def create_condition(self, condition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new condition resource"""
        return await self._create_resource(ResourceType.CONDITION, condition_data)
    
    async def create_medication_request(self, medication_request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new medication request resource"""
        return await self._create_resource(ResourceType.MEDICATION_REQUEST, medication_request_data)
    
    async def create_observation(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new observation resource"""
        return await self._create_resource(ResourceType.OBSERVATION, observation_data)
    
    async def update_resource(self, resource_type: ResourceType, 
                            resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a resource"""
        url = urljoin(self.base_url, f"{resource_type.value}/{resource_id}")
        headers = await self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"FHIR API error: {response.status} - {error_text}")
    
    async def delete_resource(self, resource_type: ResourceType, resource_id: str) -> bool:
        """Delete a resource"""
        url = urljoin(self.base_url, f"{resource_type.value}/{resource_id}")
        headers = await self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                if response.status == 200 or response.status == 204:
                    return True
                else:
                    error_text = await response.text()
                    raise Exception(f"FHIR API error: {response.status} - {error_text}")
    
    async def _get_resource(self, resource_type: ResourceType, resource_id: str) -> Dict[str, Any]:
        """Get a resource by ID"""
        # Check cache
        cache_key = f"{resource_type.value}_{resource_id}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            # Check if cache entry is still valid
            if datetime.datetime.now().timestamp() - cache_entry["timestamp"] < self.cache_ttl:
                self.logger.debug(f"Cache hit for {resource_type.value}/{resource_id}")
                return cache_entry["data"]
        
        url = urljoin(self.base_url, f"{resource_type.value}/{resource_id}")
        headers = await self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        "timestamp": datetime.datetime.now().timestamp(),
                        "data": data
                    }
                    
                    return data
                else:
                    error_text = await response.text()
                    raise Exception(f"FHIR API error: {response.status} - {error_text}")
    
    async def _search_resources(self, resource_type: ResourceType, 
                              params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Search for resources matching criteria"""
        # Generate cache key
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        cache_key = f"{resource_type.value}_search_{param_str}"
        
        # Check cache
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            # Check if cache entry is still valid
            if datetime.datetime.now().timestamp() - cache_entry["timestamp"] < self.cache_ttl:
                self.logger.debug(f"Cache hit for {resource_type.value} search: {param_str}")
                return cache_entry["data"]
        
        url = urljoin(self.base_url, resource_type.value)
        headers = await self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract entries from bundle
                    entries = data.get("entry", [])
                    resources = [entry.get("resource", {}) for entry in entries]
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        "timestamp": datetime.datetime.now().timestamp(),
                        "data": resources
                    }
                    
                    return resources
                else:
                    error_text = await response.text()
                    raise Exception(f"FHIR API error: {response.status} - {error_text}")
    
    async def _create_resource(self, resource_type: ResourceType, 
                             data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource"""
        url = urljoin(self.base_url, resource_type.value)
        headers = await self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"FHIR API error: {response.status} - {error_text}")
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        headers = {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }
        
        # Add authorization if available
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        elif self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.client_id and self.client_secret:
            # Refresh token if needed
            await self._refresh_token()
            headers["Authorization"] = f"Bearer {self.token}"
        
        return headers
    
    async def _refresh_token(self) -> None:
        """Refresh the OAuth token"""
        if not self.client_id or not self.client_secret:
            return
        
        # Check if token is still valid
        if self.token and self.token_expiry:
            if datetime.datetime.now() < self.token_expiry:
                return
        
        # Get new token
        token_url = urljoin(self.base_url, "token")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("access_token")
                    expires_in = data.get("expires_in", 3600)
                    self.token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to refresh token: {response.status} - {error_text}")
    
    def invalidate_cache(self) -> None:
        """Invalidate the entire cache"""
        self.cache.clear()
    
    def invalidate_resource_cache(self, resource_type: ResourceType, resource_id: str) -> None:
        """Invalidate cache for a specific resource"""
        cache_key = f"{resource_type.value}_{resource_id}"
        if cache_key in self.cache:
            del self.cache[cache_key]
    
    def invalidate_search_cache(self, resource_type: ResourceType) -> None:
        """Invalidate cache for searches of a specific resource type"""
        prefix = f"{resource_type.value}_search_"
        keys_to_delete = [k for k in self.cache.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            del self.cache[key]

# Example usage
async def main():
    # Example FHIR server (using HAPI FHIR public test server)
    fhir_client = FHIRClient("http://hapi.fhir.org/baseR4/")
    
    try:
        # Get a patient
        patient = await fhir_client.get_patient("example")
        print(f"Patient: {json.dumps(patient, indent=2)}")
        
        # Search for patients
        patients = await fhir_client.search_patients({"name": "Smith"})
        print(f"Found {len(patients)} patients with name Smith")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())