#!/usr/bin/env python3
"""
Patient Service for Crohn's Disease Treatment System

This module provides services for managing patient records, including
retrieving from FHIR servers and mapping to internal data models.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
import datetime

from fhir_client import FHIRClient, ResourceType
from patient_model import (
    PatientRecord, GeneralInfo, CrohnsInfo, GeneticMarker, Biomarker, BiomarkerValue,
    Medication, TreatmentHistory, Surgery, Hospitalization, Assessment, Address, Contact,
    Gender, CrohnsLocation, DiseaseSeverity, TreatmentResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ehr.patient-service')

class PatientService:
    """Service for managing patient records"""
    
    def __init__(self, fhir_client: FHIRClient, local_storage_path: Optional[str] = None):
        """Initialize the patient service"""
        self.fhir_client = fhir_client
        self.local_storage_path = local_storage_path
        self.logger = logging.getLogger('ehr.patient-service')
    
    async def get_patient_record(self, patient_id: str) -> PatientRecord:
        """Get a comprehensive patient record for Crohn's disease treatment"""
        # Check if we have a local record first
        local_record = await self._get_local_record(patient_id)
        if local_record:
            self.logger.info(f"Retrieved local record for patient {patient_id}")
            return local_record
        
        # Retrieve from FHIR server
        self.logger.info(f"Retrieving record from FHIR server for patient {patient_id}")
        
        # Get patient demographics
        patient_data = await self.fhir_client.get_patient(patient_id)
        
        # Get Crohn's conditions
        conditions = await self.fhir_client.get_crohns_conditions(patient_id)
        
        # Get medications
        medications = await self.fhir_client.get_medications(patient_id)
        
        # Get observations (labs)
        observations = await self.fhir_client.get_observations(patient_id)
        
        # Get procedures
        procedures = await self.fhir_client.get_procedures(patient_id)
        
        # Create patient record
        record = self._create_patient_record(
            patient_id, patient_data, conditions, medications, observations, procedures
        )
        
        # Save locally
        if self.local_storage_path:
            await self._save_local_record(record)
        
        return record
    
    async def update_patient_record(self, record: PatientRecord) -> PatientRecord:
        """Update a patient record"""
        # Update local storage
        if self.local_storage_path:
            record.last_updated = datetime.datetime.now().isoformat()
            await self._save_local_record(record)
        
        # In a real implementation, we would update the FHIR server here
        self.logger.info(f"Record for patient {record.id} updated")
        
        return record
    
    async def search_patients(self, query: Dict[str, str]) -> List[PatientRecord]:
        """Search for patients matching criteria"""
        # Search FHIR server
        patient_resources = await self.fhir_client.search_patients(query)
        
        # Convert to patient records
        records = []
        for resource in patient_resources:
            patient_id = resource.get("id")
            if patient_id:
                record = self._create_basic_patient_record(patient_id, resource)
                records.append(record)
        
        return records
    
    async def get_patients_with_crohns(self) -> List[PatientRecord]:
        """Get all patients with Crohn's disease"""
        # In a real implementation, we would search for patients with Crohn's disease
        # For now, we'll just search for patients
        return await self.search_patients({})
    
    async def get_patients_for_trial(self, criteria: Dict[str, Any]) -> List[PatientRecord]:
        """Get patients matching clinical trial criteria"""
        # This would be a more specific search for patients matching trial criteria
        # For now, we'll just return all patients with Crohn's
        return await self.get_patients_with_crohns()
    
    async def add_assessment(self, patient_id: str, assessment: Assessment) -> PatientRecord:
        """Add a clinical assessment to a patient record"""
        record = await self.get_patient_record(patient_id)
        record.assessments.append(assessment)
        record.last_updated = datetime.datetime.now().isoformat()
        
        # Update record
        return await self.update_patient_record(record)
    
    async def add_medication(self, patient_id: str, medication: Medication) -> PatientRecord:
        """Add a medication to a patient record"""
        record = await self.get_patient_record(patient_id)
        record.current_medications.append(medication)
        record.last_updated = datetime.datetime.now().isoformat()
        
        # Update record
        return await self.update_patient_record(record)
    
    async def add_biomarker_value(self, patient_id: str, biomarker_name: str, 
                                value: BiomarkerValue) -> PatientRecord:
        """Add a biomarker value to a patient record"""
        record = await self.get_patient_record(patient_id)
        
        # Find existing biomarker or create new one
        biomarker = None
        for b in record.biomarkers:
            if b.name.lower() == biomarker_name.lower():
                biomarker = b
                break
        
        if not biomarker:
            biomarker = Biomarker(name=biomarker_name)
            record.biomarkers.append(biomarker)
        
        # Add value
        biomarker.values.append(value)
        record.last_updated = datetime.datetime.now().isoformat()
        
        # Update record
        return await self.update_patient_record(record)
    
    async def add_treatment_history(self, patient_id: str, 
                                  treatment: TreatmentHistory) -> PatientRecord:
        """Add treatment history to a patient record"""
        record = await self.get_patient_record(patient_id)
        record.crohns_info.treatment_history.append(treatment)
        record.last_updated = datetime.datetime.now().isoformat()
        
        # Update record
        return await self.update_patient_record(record)
    
    async def _get_local_record(self, patient_id: str) -> Optional[PatientRecord]:
        """Get a local patient record if available"""
        if not self.local_storage_path:
            return None
        
        file_path = os.path.join(self.local_storage_path, f"{patient_id}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                json_data = f.read()
            
            return PatientRecord.from_json(json_data)
        except Exception as e:
            self.logger.error(f"Error reading local record for patient {patient_id}: {e}")
            return None
    
    async def _save_local_record(self, record: PatientRecord) -> None:
        """Save a patient record locally"""
        if not self.local_storage_path:
            return
        
        # Ensure directory exists
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        file_path = os.path.join(self.local_storage_path, f"{record.id}.json")
        try:
            with open(file_path, 'w') as f:
                f.write(record.to_json())
        except Exception as e:
            self.logger.error(f"Error saving local record for patient {record.id}: {e}")
    
    def _create_patient_record(self, patient_id: str, patient_data: Dict[str, Any],
                             conditions: List[Dict[str, Any]], medications: List[Dict[str, Any]],
                             observations: List[Dict[str, Any]], 
                             procedures: List[Dict[str, Any]]) -> PatientRecord:
        """Create a patient record from FHIR resources"""
        # Create basic record with demographics
        record = self._create_basic_patient_record(patient_id, patient_data)
        
        # Process Crohn's conditions
        self._process_conditions(record, conditions)
        
        # Process medications
        self._process_medications(record, medications)
        
        # Process observations
        self._process_observations(record, observations)
        
        # Process procedures
        self._process_procedures(record, procedures)
        
        return record
    
    def _create_basic_patient_record(self, patient_id: str, 
                                   patient_data: Dict[str, Any]) -> PatientRecord:
        """Create a basic patient record with demographics"""
        # Extract general info
        general_info = GeneralInfo()
        
        # Medical record number
        identifier = _get_first_value(patient_data, "identifier", [])
        for id_obj in identifier:
            if id_obj.get("type", {}).get("coding", [{}])[0].get("code") == "MR":
                general_info.medical_record_number = id_obj.get("value")
                break
        
        # Gender
        gender_value = patient_data.get("gender", "unknown")
        try:
            general_info.gender = Gender(gender_value)
        except ValueError:
            general_info.gender = Gender.UNKNOWN
        
        # Birth date
        general_info.birth_date = patient_data.get("birthDate")
        
        # Deceased
        general_info.deceased = patient_data.get("deceasedBoolean", False)
        general_info.deceased_date = patient_data.get("deceasedDateTime")
        
        # Address
        addresses = _get_first_value(patient_data, "address", [])
        if addresses:
            address = addresses[0]
            general_info.address = Address(
                line=address.get("line", []),
                city=address.get("city"),
                state=address.get("state"),
                postal_code=address.get("postalCode"),
                country=address.get("country")
            )
        
        # Contact info
        telecom = _get_first_value(patient_data, "telecom", [])
        for contact in telecom:
            system = contact.get("system")
            value = contact.get("value")
            if system == "phone":
                general_info.phone = value
            elif system == "email":
                general_info.email = value
        
        # Language
        communication = _get_first_value(patient_data, "communication", [])
        if communication:
            language = communication[0].get("language", {}).get("coding", [{}])[0].get("code")
            general_info.language = language
        
        # Marital status
        marital_status = patient_data.get("maritalStatus", {}).get("coding", [{}])[0].get("display")
        general_info.marital_status = marital_status
        
        # Contacts
        contacts = []
        for contact_data in _get_first_value(patient_data, "contact", []):
            name = _format_name(contact_data.get("name", {}))
            relationship = _get_first_value(contact_data, "relationship", [{}])[0].get("text")
            
            contact_telecom = _get_first_value(contact_data, "telecom", [])
            phone = None
            email = None
            for t in contact_telecom:
                system = t.get("system")
                value = t.get("value")
                if system == "phone":
                    phone = value
                elif system == "email":
                    email = value
            
            contact_address = None
            if contact_data.get("address"):
                addr = contact_data.get("address")
                contact_address = Address(
                    line=addr.get("line", []),
                    city=addr.get("city"),
                    state=addr.get("state"),
                    postal_code=addr.get("postalCode"),
                    country=addr.get("country")
                )
            
            contacts.append(Contact(
                name=name,
                relationship=relationship,
                phone=phone,
                email=email,
                address=contact_address
            ))
        
        general_info.contacts = contacts
        
        # Create basic patient record
        return PatientRecord(
            id=patient_id,
            general_info=general_info
        )
    
    def _process_conditions(self, record: PatientRecord, 
                          conditions: List[Dict[str, Any]]) -> None:
        """Process Crohn's disease conditions"""
        if not conditions:
            return
        
        # Find earliest Crohn's condition for diagnosis date
        earliest_date = None
        for condition in conditions:
            onset_date = condition.get("onsetDateTime", "9999-99-99")
            if earliest_date is None or onset_date < earliest_date:
                earliest_date = onset_date
        
        record.crohns_info.diagnosis_date = earliest_date
        
        # Extract Crohn's locations
        locations = []
        for condition in conditions:
            # Look for body site information
            body_sites = _get_first_value(condition, "bodySite", [])
            for site in body_sites:
                coding = _get_first_value(site, "coding", [])
                for code in coding:
                    display = code.get("display", "").lower()
                    if "ileum" in display or "small bowel" in display:
                        locations.append(CrohnsLocation.ILEAL)
                    elif "colon" in display:
                        locations.append(CrohnsLocation.COLONIC)
                    elif "perianal" in display:
                        locations.append(CrohnsLocation.PERIANAL)
                    elif "upper gi" in display or "esophagus" in display or "stomach" in display:
                        locations.append(CrohnsLocation.UPPER_GI)
            
            # Look in notes as well
            notes = condition.get("note", [])
            for note in notes:
                text = note.get("text", "").lower()
                if "ileum" in text or "small bowel" in text:
                    locations.append(CrohnsLocation.ILEAL)
                elif "colon" in text:
                    locations.append(CrohnsLocation.COLONIC)
                elif "perianal" in text:
                    locations.append(CrohnsLocation.PERIANAL)
                elif "upper gi" in text or "esophagus" in text or "stomach" in text:
                    locations.append(CrohnsLocation.UPPER_GI)
        
        # If both ileal and colonic, use ileocolonic
        if CrohnsLocation.ILEAL in locations and CrohnsLocation.COLONIC in locations:
            locations = [loc for loc in locations if loc not in [CrohnsLocation.ILEAL, CrohnsLocation.COLONIC]]
            locations.append(CrohnsLocation.ILEOCOLONIC)
        
        # Remove duplicates
        record.crohns_info.locations = list(set(locations))
        
        # Extract severity
        for condition in conditions:
            severity = condition.get("severity", {}).get("coding", [{}])[0].get("code")
            if severity == "24484000":  # SNOMED code for "Severe"
                record.crohns_info.severity = DiseaseSeverity.SEVERE
                break
            elif severity == "6736007":  # SNOMED code for "Moderate"
                record.crohns_info.severity = DiseaseSeverity.MODERATE
            elif severity == "255604002":  # SNOMED code for "Mild"
                if record.crohns_info.severity != DiseaseSeverity.MODERATE:
                    record.crohns_info.severity = DiseaseSeverity.MILD
        
        # Extract complications and extraintestinal manifestations
        complications = []
        extraintestinal = []
        
        for condition in conditions:
            # Check if it's a complication
            is_complication = False
            is_extraintestinal = False
            
            category = _get_first_value(condition, "category", [])
            for cat in category:
                coding = _get_first_value(cat, "coding", [])
                for code in coding:
                    if code.get("code") == "116223007":  # SNOMED code for "Complication"
                        is_complication = True
                    elif code.get("code") == "55607006":  # SNOMED code for "Problem"
                        is_extraintestinal = True
            
            condition_display = ""
            condition_coding = _get_first_value(condition, "code", {}).get("coding", [{}])
            if condition_coding:
                condition_display = condition_coding[0].get("display", "")
            
            if is_complication:
                complications.append(condition_display)
            elif is_extraintestinal:
                extraintestinal.append(condition_display)
        
        record.crohns_info.complications = complications
        record.crohns_info.extraintestinal_manifestations = extraintestinal
    
    def _process_medications(self, record: PatientRecord, 
                           medications: List[Dict[str, Any]]) -> None:
        """Process medications"""
        if not medications:
            return
        
        current_medications = []
        treatment_history = []
        
        for med_request in medications:
            # Extract medication details
            medication_coding = _get_first_value(med_request, "medicationCodeableConcept", {}).get("coding", [{}])
            if not medication_coding:
                continue
            
            medication_code = medication_coding[0].get("code")
            medication_display = medication_coding[0].get("display", "")
            medication_system = medication_coding[0].get("system")
            
            # Extract dosage
            dosage_instruction = _get_first_value(med_request, "dosageInstruction", [])
            dosage = None
            unit = None
            route = None
            frequency = None
            
            if dosage_instruction:
                dose_and_rate = _get_first_value(dosage_instruction[0], "doseAndRate", [])
                if dose_and_rate:
                    dose_quantity = dose_and_rate[0].get("doseQuantity", {})
                    dosage = dose_quantity.get("value")
                    unit = dose_quantity.get("unit")
                
                route_coding = _get_first_value(dosage_instruction[0].get("route", {}), "coding", [{}])
                if route_coding:
                    route = route_coding[0].get("display")
                
                timing = dosage_instruction[0].get("timing", {})
                frequency_text = timing.get("code", {}).get("text")
                if frequency_text:
                    frequency = frequency_text
            
            # Extract dates
            authored_date = med_request.get("authoredOn")
            start_date = authored_date
            end_date = None
            
            # Check if it's a current medication
            status = med_request.get("status")
            reason_stopped = None
            
            if status == "active":
                # Current medication
                medication = Medication(
                    name=medication_display,
                    code=medication_code,
                    system=medication_system,
                    dosage=str(dosage) if dosage else None,
                    unit=unit,
                    route=route,
                    frequency=frequency,
                    start_date=start_date,
                    status=status
                )
                current_medications.append(medication)
            else:
                # Past medication
                end_date = med_request.get("dispenseRequest", {}).get("validityPeriod", {}).get("end")
                
                # Check for reason stopped
                extension = _get_first_value(med_request, "extension", [])
                for ext in extension:
                    if ext.get("url") == "http://hl7.org/fhir/StructureDefinition/servicerequest-reasonRefused":
                        reason_stopped = ext.get("valueString")
                
                medication = Medication(
                    name=medication_display,
                    code=medication_code,
                    system=medication_system,
                    dosage=str(dosage) if dosage else None,
                    unit=unit,
                    route=route,
                    frequency=frequency,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    reason_stopped=reason_stopped
                )
                
                # Check for response in notes
                response = TreatmentResponse.UNKNOWN
                notes = _get_first_value(med_request, "note", [])
                for note in notes:
                    text = note.get("text", "").lower()
                    if "complete response" in text or "remission" in text:
                        response = TreatmentResponse.COMPLETE
                    elif "partial response" in text or "improvement" in text:
                        response = TreatmentResponse.PARTIAL
                    elif "no response" in text or "failure" in text:
                        response = TreatmentResponse.NONE
                    elif "adverse" in text or "reaction" in text or "intolerance" in text:
                        response = TreatmentResponse.ADVERSE
                
                # Add to treatment history
                treatment_history.append(TreatmentHistory(
                    medication=medication,
                    response=response,
                    start_date=start_date,
                    end_date=end_date,
                    side_effects=[]  # Would extract from adverse event resources in a real implementation
                ))
        
        record.current_medications = current_medications
        record.crohns_info.treatment_history = treatment_history
    
    def _process_observations(self, record: PatientRecord, 
                            observations: List[Dict[str, Any]]) -> None:
        """Process observations (labs)"""
        if not observations:
            return
        
        # Group observations by code
        grouped_observations = {}
        for obs in observations:
            code_coding = _get_first_value(obs, "code", {}).get("coding", [{}])
            if not code_coding:
                continue
            
            code = code_coding[0].get("code")
            if code:
                if code not in grouped_observations:
                    grouped_observations[code] = []
                grouped_observations[code].append(obs)
        
        # Process each group
        biomarkers = []
        for code, obs_list in grouped_observations.items():
            if not obs_list:
                continue
            
            # Get biomarker name and system
            code_coding = _get_first_value(obs_list[0], "code", {}).get("coding", [{}])
            biomarker_name = code_coding[0].get("display", "")
            biomarker_system = code_coding[0].get("system", "")
            
            # Process values
            values = []
            for obs in obs_list:
                # Get value
                value_quantity = obs.get("valueQuantity", {})
                if not value_quantity:
                    continue
                
                value = value_quantity.get("value")
                unit = value_quantity.get("unit")
                if value is None or unit is None:
                    continue
                
                # Get date
                effective_date = obs.get("effectiveDateTime")
                if not effective_date:
                    continue
                
                # Get reference range
                reference_range = None
                for ref_range in _get_first_value(obs, "referenceRange", []):
                    low = ref_range.get("low", {}).get("value")
                    high = ref_range.get("high", {}).get("value")
                    if low is not None or high is not None:
                        reference_range = {"low": low, "high": high}
                        break
                
                # Check if abnormal
                abnormal = None
                if reference_range:
                    low = reference_range.get("low")
                    high = reference_range.get("high")
                    if low is not None and value < low:
                        abnormal = True
                    elif high is not None and value > high:
                        abnormal = True
                    else:
                        abnormal = False
                
                # Add value
                values.append(BiomarkerValue(
                    value=value,
                    unit=unit,
                    date=effective_date,
                    reference_range=reference_range,
                    abnormal=abnormal
                ))
            
            # Sort values by date (newest first)
            values.sort(key=lambda v: v.date, reverse=True)
            
            # Add biomarker
            if values:
                biomarkers.append(Biomarker(
                    name=biomarker_name,
                    code=code,
                    system=biomarker_system,
                    values=values
                ))
        
        record.biomarkers = biomarkers
        
        # Check for genetic markers specifically
        genetic_markers = []
        for obs in observations:
            # Check if it's a genetic observation
            category = _get_first_value(obs, "category", [])
            is_genetic = False
            for cat in category:
                coding = _get_first_value(cat, "coding", [])
                for code in coding:
                    if code.get("code") == "genetics":
                        is_genetic = True
                        break
                if is_genetic:
                    break
            
            if not is_genetic:
                continue
            
            # Get marker details
            code_coding = _get_first_value(obs, "code", {}).get("coding", [{}])
            marker_name = code_coding[0].get("display", "")
            
            # Get value
            value = None
            if obs.get("valueString"):
                value = obs.get("valueString")
            elif obs.get("valueCodeableConcept"):
                value_coding = _get_first_value(obs.get("valueCodeableConcept", {}), "coding", [{}])
                if value_coding:
                    value = value_coding[0].get("display")
            
            if not value:
                continue
            
            # Get interpretation
            interpretation = None
            interpretation_coding = _get_first_value(obs, "interpretation", [])
            if interpretation_coding:
                coding = _get_first_value(interpretation_coding[0], "coding", [{}])
                if coding:
                    interpretation = coding[0].get("display")
            
            # Get date
            effective_date = obs.get("effectiveDateTime")
            
            # Add genetic marker
            genetic_markers.append(GeneticMarker(
                name=marker_name,
                value=value,
                interpretation=interpretation,
                date=effective_date
            ))
        
        record.genetic_markers = genetic_markers
    
    def _process_procedures(self, record: PatientRecord, 
                          procedures: List[Dict[str, Any]]) -> None:
        """Process procedures"""
        if not procedures:
            return
        
        surgeries = []
        for proc in procedures:
            # Check if it's a surgery
            category = proc.get("category", {}).get("coding", [{}])[0].get("code")
            if category != "surgery":
                continue
            
            # Get procedure details
            code_coding = _get_first_value(proc, "code", {}).get("coding", [{}])
            procedure_name = code_coding[0].get("display", "")
            
            # Get date
            performed_date = None
            if proc.get("performedDateTime"):
                performed_date = proc.get("performedDateTime")
            elif proc.get("performedPeriod"):
                performed_date = proc.get("performedPeriod", {}).get("start")
            
            if not performed_date:
                continue
            
            # Get body site
            site = None
            body_sites = _get_first_value(proc, "bodySite", [])
            if body_sites:
                site_coding = _get_first_value(body_sites[0], "coding", [{}])
                if site_coding:
                    site = site_coding[0].get("display")
            
            # Get reason
            indication = None
            reason_reference = _get_first_value(proc, "reasonReference", [])
            if reason_reference:
                ref = reason_reference[0]
                if "reference" in ref:
                    # In a real implementation, we would resolve this reference
                    # For now, we'll just use the display text
                    indication = ref.get("display")
            
            # Get outcome
            outcome = None
            outcome_coding = _get_first_value(proc, "outcome", {}).get("coding", [{}])
            if outcome_coding:
                outcome = outcome_coding[0].get("display")
            
            # Get complications
            complications = []
            complication_refs = _get_first_value(proc, "complication", [])
            for comp_ref in complication_refs:
                comp_coding = _get_first_value(comp_ref, "coding", [{}])
                if comp_coding:
                    complications.append(comp_coding[0].get("display"))
            
            # Get notes
            notes = None
            note_list = _get_first_value(proc, "note", [])
            if note_list:
                notes = note_list[0].get("text")
            
            # Add surgery
            surgeries.append(Surgery(
                procedure=procedure_name,
                date=performed_date,
                site=site,
                indication=indication,
                outcome=outcome,
                complications=complications,
                notes=notes
            ))
        
        record.crohns_info.surgeries = surgeries

def _get_first_value(obj: Dict[str, Any], key: str, default: Any) -> Any:
    """Get the first value of a key from a dictionary, or return a default"""
    if key not in obj:
        return default
    value = obj[key]
    if isinstance(value, list) and not value:
        return default
    return value

def _format_name(name_obj: Dict[str, Any]) -> Optional[str]:
    """Format a FHIR name object into a string"""
    if not name_obj:
        return None
    
    # Check for text
    if "text" in name_obj:
        return name_obj["text"]
    
    # Build from parts
    given = name_obj.get("given", [])
    family = name_obj.get("family", "")
    prefix = name_obj.get("prefix", [])
    suffix = name_obj.get("suffix", [])
    
    name_parts = []
    if prefix:
        name_parts.append(" ".join(prefix))
    if given:
        name_parts.append(" ".join(given))
    if family:
        name_parts.append(family)
    if suffix:
        name_parts.append(" ".join(suffix))
    
    if name_parts:
        return " ".join(name_parts)
    
    return None

# Example usage
async def main():
    # Create FHIR client (using HAPI FHIR public test server)
    fhir_client = FHIRClient("http://hapi.fhir.org/baseR4/")
    
    # Create patient service
    patient_service = PatientService(fhir_client, "./patient_data")
    
    try:
        # Search for patients
        patients = await patient_service.search_patients({"family": "Smith", "_count": "5"})
        print(f"Found {len(patients)} patients")
        
        if patients:
            # Get first patient
            patient = patients[0]
            print(f"Patient ID: {patient.id}")
            print(f"MRN: {patient.general_info.medical_record_number}")
            
            # Add a mock assessment
            assessment = Assessment(
                date=datetime.datetime.now().isoformat(),
                provider="Dr. Test",
                setting="office",
                symptoms=["Abdominal pain", "Diarrhea"],
                disease_activity_index=200,
                severity_assessment=DiseaseSeverity.MODERATE,
                plan="Continue current medication"
            )
            
            patient = await patient_service.add_assessment(patient.id, assessment)
            print(f"Added assessment, patient now has {len(patient.assessments)} assessments")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())