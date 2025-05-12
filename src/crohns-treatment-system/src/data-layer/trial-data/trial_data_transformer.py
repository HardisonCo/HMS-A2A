#!/usr/bin/env python3
"""
Trial Data Transformer for Crohn's Disease Treatment System

This module provides the data transformation layer for Crohn's trial data,
converting between various formats and preparing it for use by the genetic engine
and other HMS components.
"""

import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hms.data-layer.trial-data-transformer')

class CrohnsType(str, Enum):
    """Crohn's disease location classification"""
    ILEAL = "ileal"
    COLONIC = "colonic"
    ILEOCOLONIC = "ileocolonic"
    PERIANAL = "perianal"

class DiseaseSeverity(str, Enum):
    """Crohn's disease severity classification"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class TreatmentResponse(str, Enum):
    """Treatment response classification"""
    COMPLETE = "complete"
    PARTIAL = "partial"
    NONE = "none"
    ADVERSE = "adverse"

class TrialDataTransformer:
    """
    Transforms trial data between different formats and prepares it for use
    by other components of the Crohn's Disease Treatment System.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the transformer with optional configuration.
        
        Args:
            config: Configuration options for the transformer
        """
        self.config = config or {}
        self.biomarker_normalizers = self._create_biomarker_normalizers()
        logger.info("Trial data transformer initialized")
    
    def _create_biomarker_normalizers(self) -> Dict[str, callable]:
        """
        Create normalizer functions for different biomarkers.
        
        Returns:
            Dictionary mapping biomarker names to normalizer functions
        """
        return {
            "CRP": lambda x: min(1.0, x / 10.0),  # Normalize CRP (0-10 mg/L range)
            "ESR": lambda x: min(1.0, x / 30.0),  # Normalize ESR (0-30 mm/h range)
            "fecal_calprotectin": lambda x: min(1.0, x / 250.0),  # Normalize FC (0-250 μg/g range)
            "microbiome_diversity": lambda x: x,  # Already normalized (0-1)
            "F_prausnitzii": lambda x: x,  # Already normalized (0-1)
            "E_coli": lambda x: x,  # Already normalized (0-1)
        }
    
    def csv_to_patient_profiles(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        Transform CSV trial data into patient profiles.
        
        Args:
            csv_path: Path to the CSV file containing trial data
            
        Returns:
            List of patient profile dictionaries
        """
        logger.info(f"Transforming CSV data from {csv_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            
            # Transform data
            patient_profiles = []
            
            for _, row in df.iterrows():
                profile = self._create_patient_profile_from_row(row)
                patient_profiles.append(profile)
            
            logger.info(f"Transformed {len(patient_profiles)} patient profiles from CSV")
            return patient_profiles
            
        except Exception as e:
            logger.error(f"Error transforming CSV data: {e}")
            raise
    
    def _create_patient_profile_from_row(self, row: pd.Series) -> Dict[str, Any]:
        """
        Create a patient profile from a DataFrame row.
        
        Args:
            row: Row from DataFrame containing patient data
            
        Returns:
            Patient profile dictionary
        """
        # Basic patient information
        profile = {
            "patient_id": str(row.get("patient_id", "")),
            "demographics": {
                "age": int(row.get("age", 0)),
                "sex": row.get("sex", ""),
                "ethnicity": row.get("ethnicity", ""),
                "weight": float(row.get("weight", 0.0)),
                "height": float(row.get("height", 0.0)),
            },
            "clinical_data": {
                "crohns_type": row.get("crohns_type", "").lower(),
                "diagnosis_date": row.get("diagnosis_date", ""),
                "disease_duration": self._calculate_disease_duration(row.get("diagnosis_date", "")),
                "disease_activity": {
                    "CDAI": float(row.get("CDAI", 0.0)),
                    "SES_CD": float(row.get("SES_CD", 0.0)),
                    "fecal_calprotectin": float(row.get("fecal_calprotectin", 0.0)),
                }
            },
            "biomarkers": {
                "genetic_markers": self._parse_genetic_markers(row),
                "microbiome_profile": self._parse_microbiome_profile(row),
                "serum_markers": {
                    "CRP": float(row.get("CRP", 0.0)),
                    "ESR": float(row.get("ESR", 0.0)),
                }
            },
            "treatment_history": self._parse_treatment_history(row),
            "extraintestinal_manifestations": self._parse_list_field(row.get("extraintestinal_manifestations", "")),
            "comorbidities": self._parse_list_field(row.get("comorbidities", "")),
        }
        
        return profile
    
    def _calculate_disease_duration(self, diagnosis_date: str) -> int:
        """
        Calculate disease duration in months from diagnosis date.
        
        Args:
            diagnosis_date: Date of diagnosis in ISO format
            
        Returns:
            Disease duration in months
        """
        if not diagnosis_date:
            return 0
        
        try:
            diagnosed = datetime.fromisoformat(diagnosis_date.replace('Z', '+00:00'))
            now = datetime.now()
            duration = (now.year - diagnosed.year) * 12 + (now.month - diagnosed.month)
            return max(0, duration)
        except Exception:
            return 0
    
    def _parse_genetic_markers(self, row: pd.Series) -> List[Dict[str, str]]:
        """
        Parse genetic marker data from row.
        
        Args:
            row: DataFrame row
            
        Returns:
            List of genetic marker dictionaries
        """
        markers = []
        
        # Add NOD2 variant if present
        if "NOD2" in row and row["NOD2"]:
            markers.append({
                "gene": "NOD2",
                "variant": row["NOD2"],
                "zygosity": row.get("NOD2_zygosity", "unknown")
            })
        
        # Add ATG16L1 variant if present
        if "ATG16L1" in row and row["ATG16L1"]:
            markers.append({
                "gene": "ATG16L1",
                "variant": row["ATG16L1"],
                "zygosity": row.get("ATG16L1_zygosity", "unknown")
            })
        
        # Add IL23R variant if present
        if "IL23R" in row and row["IL23R"]:
            markers.append({
                "gene": "IL23R",
                "variant": row["IL23R"],
                "zygosity": row.get("IL23R_zygosity", "unknown")
            })
        
        # Add LRRK2-MUC19 variant if present
        if "LRRK2_MUC19" in row and row["LRRK2_MUC19"]:
            markers.append({
                "gene": "LRRK2-MUC19",
                "variant": row["LRRK2_MUC19"],
                "zygosity": row.get("LRRK2_MUC19_zygosity", "unknown")
            })
        
        return markers
    
    def _parse_microbiome_profile(self, row: pd.Series) -> Dict[str, Any]:
        """
        Parse microbiome profile data from row.
        
        Args:
            row: DataFrame row
            
        Returns:
            Microbiome profile dictionary
        """
        profile = {
            "diversity_index": float(row.get("microbiome_diversity", 0.0)),
            "key_species": []
        }
        
        # Add F. prausnitzii if present
        if "F_prausnitzii" in row:
            profile["key_species"].append({
                "name": "F. prausnitzii",
                "abundance": float(row["F_prausnitzii"])
            })
        
        # Add E. coli if present
        if "E_coli" in row:
            profile["key_species"].append({
                "name": "E. coli",
                "abundance": float(row["E_coli"])
            })
        
        return profile
    
    def _parse_treatment_history(self, row: pd.Series) -> List[Dict[str, Any]]:
        """
        Parse treatment history data from row.
        
        Args:
            row: DataFrame row
            
        Returns:
            List of treatment history dictionaries
        """
        history = []
        
        # Parse treatment history from JSON or string format
        treatment_history_str = row.get("treatment_history", "[]")
        if treatment_history_str:
            try:
                if isinstance(treatment_history_str, str):
                    # Try to parse as JSON
                    history = json.loads(treatment_history_str)
                elif isinstance(treatment_history_str, list):
                    # Already a list
                    history = treatment_history_str
            except json.JSONDecodeError:
                # Try parsing as semicolon-separated string
                treatments = treatment_history_str.split(";")
                for treatment in treatments:
                    if ":" in treatment:
                        med, response = treatment.split(":", 1)
                        history.append({
                            "medication": med.strip(),
                            "response": response.strip(),
                            "start_date": "",
                            "end_date": "",
                            "adverse_events": []
                        })
        
        return history
    
    def _parse_list_field(self, field_value: str) -> List[str]:
        """
        Parse a comma or semicolon-separated string into a list.
        
        Args:
            field_value: String to parse
            
        Returns:
            List of parsed values
        """
        if not field_value:
            return []
        
        if isinstance(field_value, list):
            return field_value
        
        if ";" in field_value:
            return [item.strip() for item in field_value.split(";") if item.strip()]
        else:
            return [item.strip() for item in field_value.split(",") if item.strip()]
    
    def transform_patient_for_genetic_engine(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a patient profile into the format expected by the genetic engine.
        
        Args:
            patient: Patient profile dictionary
            
        Returns:
            Transformed patient data for genetic engine
        """
        logger.debug(f"Transforming patient {patient.get('patient_id')} for genetic engine")
        
        # Extract and transform the relevant fields
        try:
            demographics = patient.get("demographics", {})
            clinical_data = patient.get("clinical_data", {})
            biomarkers = patient.get("biomarkers", {})
            genetic_markers = biomarkers.get("genetic_markers", [])
            serum_markers = biomarkers.get("serum_markers", {})
            microbiome = biomarkers.get("microbiome_profile", {})
            
            # Map genetic markers to a dictionary
            genetic_dict = {}
            for marker in genetic_markers:
                gene = marker.get("gene")
                variant = marker.get("variant")
                if gene and variant:
                    genetic_dict[gene] = variant
            
            # Create the transformed data structure
            transformed = {
                "patient_id": patient.get("patient_id", ""),
                "age": demographics.get("age", 0),
                "weight": demographics.get("weight", 0.0),
                "sex": demographics.get("sex", ""),
                "crohns_type": clinical_data.get("crohns_type", ""),
                "severity": self._determine_severity(clinical_data),
                "disease_duration": clinical_data.get("disease_duration", 0),
                "genetic_markers": genetic_dict,
                "biomarker_values": {
                    "CRP": serum_markers.get("CRP", 0.0),
                    "ESR": serum_markers.get("ESR", 0.0),
                    "fecal_calprotectin": clinical_data.get("disease_activity", {}).get("fecal_calprotectin", 0.0),
                    "CDAI": clinical_data.get("disease_activity", {}).get("CDAI", 0.0),
                    "SES_CD": clinical_data.get("disease_activity", {}).get("SES_CD", 0.0),
                    "microbiome_diversity": microbiome.get("diversity_index", 0.0),
                },
                "normalized_biomarkers": self._normalize_biomarkers({
                    "CRP": serum_markers.get("CRP", 0.0),
                    "ESR": serum_markers.get("ESR", 0.0),
                    "fecal_calprotectin": clinical_data.get("disease_activity", {}).get("fecal_calprotectin", 0.0),
                    "microbiome_diversity": microbiome.get("diversity_index", 0.0),
                }),
                "previous_treatments": self._transform_treatment_history(patient.get("treatment_history", [])),
                "comorbidities": patient.get("comorbidities", []),
                "extraintestinal_manifestations": patient.get("extraintestinal_manifestations", []),
            }
            
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming patient data: {e}")
            # Return a minimal valid structure
            return {
                "patient_id": patient.get("patient_id", "unknown"),
                "age": 0,
                "weight": 0.0,
                "crohns_type": "",
                "severity": "unknown",
                "genetic_markers": {},
                "biomarker_values": {},
                "normalized_biomarkers": {},
                "previous_treatments": [],
            }
    
    def _determine_severity(self, clinical_data: Dict[str, Any]) -> str:
        """
        Determine disease severity based on clinical data.
        
        Args:
            clinical_data: Clinical data dictionary
            
        Returns:
            Disease severity string
        """
        if "severity" in clinical_data:
            return clinical_data["severity"]
        
        # Get disease activity measures
        disease_activity = clinical_data.get("disease_activity", {})
        cdai = disease_activity.get("CDAI", 0.0)
        calprotectin = disease_activity.get("fecal_calprotectin", 0.0)
        
        # Determine severity based on CDAI
        if cdai >= 450:
            return DiseaseSeverity.SEVERE.value
        elif cdai >= 220:
            return DiseaseSeverity.MODERATE.value
        elif cdai >= 150:
            return DiseaseSeverity.MILD.value
        
        # If CDAI isn't conclusive, check calprotectin
        if calprotectin >= 250:
            return DiseaseSeverity.MODERATE.value
        elif calprotectin >= 150:
            return DiseaseSeverity.MILD.value
        
        # Default
        return DiseaseSeverity.MILD.value
    
    def _normalize_biomarkers(self, biomarkers: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize biomarker values to a 0-1 range.
        
        Args:
            biomarkers: Biomarker dictionary
            
        Returns:
            Normalized biomarker dictionary
        """
        normalized = {}
        
        for name, value in biomarkers.items():
            if name in self.biomarker_normalizers:
                normalized[name] = self.biomarker_normalizers[name](value)
            else:
                normalized[name] = value
        
        return normalized
    
    def _transform_treatment_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform treatment history into the format expected by the genetic engine.
        
        Args:
            history: Treatment history list
            
        Returns:
            Transformed treatment history
        """
        transformed = []
        
        for entry in history:
            transformed_entry = {
                "medication": entry.get("medication", ""),
                "response": self._normalize_response(entry.get("response", "")),
            }
            
            # Add optional fields if present
            if "duration" in entry:
                transformed_entry["duration"] = entry["duration"]
            
            if "adverse_events" in entry:
                transformed_entry["adverse_events"] = entry["adverse_events"]
            
            transformed.append(transformed_entry)
        
        return transformed
    
    def _normalize_response(self, response: str) -> str:
        """
        Normalize treatment response string.
        
        Args:
            response: Original response string
            
        Returns:
            Normalized response string
        """
        response = response.lower()
        
        if response in ("complete", "complete response", "remission"):
            return TreatmentResponse.COMPLETE.value
        elif response in ("partial", "partial response", "improvement"):
            return TreatmentResponse.PARTIAL.value
        elif response in ("none", "no response", "failure", "ineffective"):
            return TreatmentResponse.NONE.value
        elif response in ("adverse", "adverse events", "intolerance", "side effects"):
            return TreatmentResponse.ADVERSE.value
        else:
            # Default
            return TreatmentResponse.NONE.value
    
    def transform_trial_protocol_for_adaptive_engine(self, protocol: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a trial protocol for use by the adaptive trial engine.
        
        Args:
            protocol: Trial protocol dictionary
            
        Returns:
            Transformed protocol for adaptive engine
        """
        logger.debug(f"Transforming trial protocol {protocol.get('trial_id')} for adaptive engine")
        
        # Extract and transform the relevant fields
        try:
            # Create the transformed protocol
            transformed = {
                "trial_id": protocol.get("trial_id", ""),
                "title": protocol.get("title", ""),
                "phase": protocol.get("phase", 0),
                "arms": self._transform_arms(protocol.get("arms", [])),
                "adaptive_rules": self._transform_adaptive_rules(protocol.get("adaptiveRules", [])),
                "endpoints": {
                    "primary": self._transform_endpoints(protocol.get("primaryEndpoints", [])),
                    "secondary": self._transform_endpoints(protocol.get("secondaryEndpoints", [])),
                },
                "eligibility": self._transform_eligibility(protocol.get("eligibility", {})),
                "enrollment_target": protocol.get("enrollmentTarget", 0),
                "interim_analyses": self._transform_interim_analyses(protocol.get("interimAnalyses", [])),
            }
            
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming trial protocol: {e}")
            # Return a minimal valid structure
            return {
                "trial_id": protocol.get("trial_id", "unknown"),
                "arms": [],
                "adaptive_rules": [],
                "endpoints": {"primary": [], "secondary": []},
                "eligibility": {"inclusion": [], "exclusion": []},
            }
    
    def _transform_arms(self, arms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform trial arms.
        
        Args:
            arms: List of trial arms
            
        Returns:
            Transformed trial arms
        """
        transformed = []
        
        for arm in arms:
            transformed_arm = {
                "arm_id": arm.get("armId", ""),
                "name": arm.get("name", ""),
                "treatment": arm.get("treatment", {}),
                "biomarker_stratification": arm.get("biomarkerStratification", []),
                "allocation_weight": arm.get("allocationWeight", 1.0),
                "max_subjects": arm.get("maxSubjects", 0),
            }
            
            transformed.append(transformed_arm)
        
        return transformed
    
    def _transform_adaptive_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform adaptive rules.
        
        Args:
            rules: List of adaptive rules
            
        Returns:
            Transformed adaptive rules
        """
        # Most fields can be passed through directly
        return rules
    
    def _transform_endpoints(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform endpoints.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Transformed endpoints
        """
        transformed = []
        
        for endpoint in endpoints:
            transformed_endpoint = {
                "name": endpoint.get("name", ""),
                "metric": endpoint.get("metric", ""),
                "timepoint": endpoint.get("timepoint", ""),
                "threshold": endpoint.get("threshold", None),
            }
            
            transformed.append(transformed_endpoint)
        
        return transformed
    
    def _transform_eligibility(self, eligibility: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Transform eligibility criteria.
        
        Args:
            eligibility: Eligibility dictionary
            
        Returns:
            Transformed eligibility criteria
        """
        return {
            "inclusion": eligibility.get("inclusion", []),
            "exclusion": eligibility.get("exclusion", []),
        }
    
    def _transform_interim_analyses(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform interim analyses.
        
        Args:
            analyses: List of interim analyses
            
        Returns:
            Transformed interim analyses
        """
        transformed = []
        
        for analysis in analyses:
            transformed_analysis = {
                "timing": analysis.get("timing", ""),
                "metrics": analysis.get("metrics", []),
                "decision_criteria": analysis.get("decisionCriteria", []),
            }
            
            transformed.append(transformed_analysis)
        
        return transformed

    def hms_ehr_to_patient_profile(self, ehr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform HMS-EHR data into a patient profile.
        
        Args:
            ehr_data: HMS-EHR data dictionary
            
        Returns:
            Patient profile dictionary
        """
        logger.debug(f"Transforming HMS-EHR data for patient {ehr_data.get('patient', {}).get('id')}")
        
        try:
            patient = ehr_data.get("patient", {})
            conditions = ehr_data.get("conditions", [])
            medications = ehr_data.get("medications", [])
            labs = ehr_data.get("labs", [])
            
            # Find Crohn's disease condition
            crohns_condition = None
            for condition in conditions:
                if "crohn" in condition.get("name", "").lower():
                    crohns_condition = condition
                    break
            
            # Extract demographics
            demographics = {
                "age": self._calculate_age(patient.get("birthDate")),
                "sex": patient.get("gender", ""),
                "ethnicity": patient.get("ethnicity", ""),
                "weight": self._extract_latest_weight(ehr_data.get("vitals", [])),
                "height": self._extract_latest_height(ehr_data.get("vitals", [])),
            }
            
            # Extract clinical data
            clinical_data = {
                "crohns_type": self._extract_crohns_type(crohns_condition),
                "diagnosis_date": crohns_condition.get("onsetDate") if crohns_condition else "",
                "disease_activity": self._extract_disease_activity(labs, ehr_data.get("procedures", [])),
            }
            
            # Extract treatment history
            treatment_history = self._extract_treatment_history(medications)
            
            # Extract biomarkers
            biomarkers = self._extract_biomarkers(labs, ehr_data.get("genetics", []))
            
            # Extract comorbidities and extraintestinal manifestations
            comorbidities = []
            extraintestinal_manifestations = []
            
            for condition in conditions:
                if condition != crohns_condition:  # Skip the Crohn's condition
                    condition_name = condition.get("name", "")
                    
                    # Check if it's an extraintestinal manifestation
                    if any(em in condition_name.lower() for em in ["arthritis", "uveitis", "erythema", "pyoderma"]):
                        extraintestinal_manifestations.append(condition_name)
                    else:
                        comorbidities.append(condition_name)
            
            # Create the patient profile
            profile = {
                "patient_id": patient.get("id", ""),
                "demographics": demographics,
                "clinical_data": clinical_data,
                "treatment_history": treatment_history,
                "biomarkers": biomarkers,
                "comorbidities": comorbidities,
                "extraintestinal_manifestations": extraintestinal_manifestations,
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error transforming HMS-EHR data: {e}")
            # Return a minimal valid structure
            return {
                "patient_id": ehr_data.get("patient", {}).get("id", "unknown"),
                "demographics": {},
                "clinical_data": {},
                "treatment_history": [],
                "biomarkers": {},
                "comorbidities": [],
                "extraintestinal_manifestations": [],
            }
    
    def _calculate_age(self, birth_date: Optional[str]) -> int:
        """
        Calculate age from birth date.
        
        Args:
            birth_date: Birth date string
            
        Returns:
            Age in years
        """
        if not birth_date:
            return 0
        
        try:
            born = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
            today = datetime.now()
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            return max(0, age)
        except Exception:
            return 0
    
    def _extract_latest_weight(self, vitals: List[Dict[str, Any]]) -> float:
        """
        Extract the latest weight from vitals.
        
        Args:
            vitals: List of vital measurements
            
        Returns:
            Latest weight in kg
        """
        weights = [v for v in vitals if v.get("type") == "weight"]
        
        if not weights:
            return 0.0
        
        # Sort by date, most recent first
        weights.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Extract the latest weight
        latest = weights[0]
        value = latest.get("value", 0.0)
        unit = latest.get("unit", "kg").lower()
        
        # Convert to kg if needed
        if unit == "lb" or unit == "lbs":
            return value * 0.453592
        else:
            return value
    
    def _extract_latest_height(self, vitals: List[Dict[str, Any]]) -> float:
        """
        Extract the latest height from vitals.
        
        Args:
            vitals: List of vital measurements
            
        Returns:
            Latest height in cm
        """
        heights = [v for v in vitals if v.get("type") == "height"]
        
        if not heights:
            return 0.0
        
        # Sort by date, most recent first
        heights.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Extract the latest height
        latest = heights[0]
        value = latest.get("value", 0.0)
        unit = latest.get("unit", "cm").lower()
        
        # Convert to cm if needed
        if unit == "in" or unit == "inches":
            return value * 2.54
        else:
            return value
    
    def _extract_crohns_type(self, condition: Optional[Dict[str, Any]]) -> str:
        """
        Extract Crohn's disease type from condition.
        
        Args:
            condition: Crohn's disease condition
            
        Returns:
            Crohn's disease type
        """
        if not condition:
            return ""
        
        # Check details or name for type indicators
        details = condition.get("details", "").lower()
        name = condition.get("name", "").lower()
        
        if "ileal" in details or "ileal" in name:
            return CrohnsType.ILEAL.value
        elif "colonic" in details or "colonic" in name:
            return CrohnsType.COLONIC.value
        elif "ileocolonic" in details or "ileocolonic" in name:
            return CrohnsType.ILEOCOLONIC.value
        elif "perianal" in details or "perianal" in name:
            return CrohnsType.PERIANAL.value
        else:
            return CrohnsType.ILEOCOLONIC.value  # Default
    
    def _extract_disease_activity(self, labs: List[Dict[str, Any]], procedures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract disease activity measures from labs and procedures.
        
        Args:
            labs: List of lab results
            procedures: List of procedures
            
        Returns:
            Disease activity dictionary
        """
        activity = {
            "CDAI": 0.0,
            "SES_CD": 0.0,
            "fecal_calprotectin": 0.0,
        }
        
        # Extract CDAI from procedures
        for procedure in procedures:
            if "crohn" in procedure.get("name", "").lower() and "index" in procedure.get("name", "").lower():
                if "result" in procedure and isinstance(procedure["result"], (int, float)):
                    activity["CDAI"] = float(procedure["result"])
        
        # Extract SES-CD from procedures
        for procedure in procedures:
            if "endoscop" in procedure.get("name", "").lower() and "score" in procedure.get("name", "").lower():
                if "result" in procedure and isinstance(procedure["result"], (int, float)):
                    activity["SES_CD"] = float(procedure["result"])
        
        # Extract fecal calprotectin from labs
        for lab in labs:
            if "calprotectin" in lab.get("name", "").lower():
                if "value" in lab and isinstance(lab["value"], (int, float)):
                    activity["fecal_calprotectin"] = float(lab["value"])
        
        return activity
    
    def _extract_treatment_history(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract treatment history from medications.
        
        Args:
            medications: List of medications
            
        Returns:
            Treatment history list
        """
        history = []
        
        for med in medications:
            # Skip if not a Crohn's medication
            if not self._is_crohns_medication(med.get("name", "")):
                continue
            
            entry = {
                "medication": med.get("name", ""),
                "start_date": med.get("startDate", ""),
                "end_date": med.get("endDate", ""),
                "dosage": f"{med.get('dose', '')} {med.get('unit', '')}",
                "frequency": med.get("frequency", ""),
                "response": med.get("response", ""),
                "adverse_events": self._extract_adverse_events(med),
            }
            
            history.append(entry)
        
        return history
    
    def _is_crohns_medication(self, medication: str) -> bool:
        """
        Check if a medication is commonly used for Crohn's disease.
        
        Args:
            medication: Medication name
            
        Returns:
            True if it's a Crohn's medication, False otherwise
        """
        crohns_meds = [
            "infliximab", "adalimumab", "certolizumab", "golimumab",  # TNF inhibitors
            "ustekinumab", "risankizumab",  # IL-23 inhibitors
            "vedolizumab",  # Integrin inhibitors
            "tofacitinib", "upadacitinib", "filgotinib",  # JAK inhibitors
            "azathioprine", "6-mercaptopurine", "methotrexate",  # Immunomodulators
            "prednisone", "budesonide", "methylprednisolone",  # Corticosteroids
            "mesalamine", "sulfasalazine",  # Aminosalicylates
        ]
        
        return any(med in medication.lower() for med in crohns_meds)
    
    def _extract_adverse_events(self, medication: Dict[str, Any]) -> List[str]:
        """
        Extract adverse events from medication.
        
        Args:
            medication: Medication dictionary
            
        Returns:
            List of adverse events
        """
        events = []
        
        if "adverseEvents" in medication and isinstance(medication["adverseEvents"], list):
            events = medication["adverseEvents"]
        elif "sideEffects" in medication and isinstance(medication["sideEffects"], list):
            events = medication["sideEffects"]
        
        return events
    
    def _extract_biomarkers(self, labs: List[Dict[str, Any]], genetics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract biomarkers from labs and genetics.
        
        Args:
            labs: List of lab results
            genetics: List of genetic test results
            
        Returns:
            Biomarkers dictionary
        """
        # Initialize biomarkers structure
        biomarkers = {
            "genetic_markers": [],
            "microbiome_profile": {
                "diversity_index": 0.0,
                "key_species": []
            },
            "serum_markers": {
                "CRP": 0.0,
                "ESR": 0.0,
            }
        }
        
        # Extract genetic markers
        for gene in genetics:
            marker = {
                "gene": gene.get("gene", ""),
                "variant": gene.get("variant", ""),
                "zygosity": gene.get("zygosity", "unknown"),
            }
            biomarkers["genetic_markers"].append(marker)
        
        # Extract serum markers
        for lab in labs:
            lab_name = lab.get("name", "").lower()
            
            if "crp" in lab_name or "c-reactive protein" in lab_name:
                biomarkers["serum_markers"]["CRP"] = float(lab.get("value", 0.0))
            
            elif "esr" in lab_name or "erythrocyte sedimentation rate" in lab_name:
                biomarkers["serum_markers"]["ESR"] = float(lab.get("value", 0.0))
            
            # Extract microbiome data if available
            elif "microbiome" in lab_name and "diversity" in lab_name:
                biomarkers["microbiome_profile"]["diversity_index"] = float(lab.get("value", 0.0))
            
            elif "f. prausnitzii" in lab_name:
                biomarkers["microbiome_profile"]["key_species"].append({
                    "name": "F. prausnitzii",
                    "abundance": float(lab.get("value", 0.0))
                })
            
            elif "e. coli" in lab_name:
                biomarkers["microbiome_profile"]["key_species"].append({
                    "name": "E. coli",
                    "abundance": float(lab.get("value", 0.0))
                })
        
        return biomarkers

# Simple test function
def main():
    """Test the trial data transformer"""
    transformer = TrialDataTransformer()
    
    # Example patient data (would normally come from CSV)
    patient_data = {
        "patient_id": "P12345",
        "age": 45,
        "sex": "female",
        "ethnicity": "Caucasian",
        "weight": 70.5,
        "height": 165.0,
        "crohns_type": "ileocolonic",
        "diagnosis_date": "2018-03-15",
        "CDAI": 220,
        "SES_CD": 15,
        "fecal_calprotectin": 350,
        "CRP": 15.5,
        "ESR": 25,
        "NOD2": "variant",
        "NOD2_zygosity": "heterozygous",
        "ATG16L1": "normal",
        "IL23R": "variant",
        "IL23R_zygosity": "heterozygous",
        "microbiome_diversity": 0.65,
        "F_prausnitzii": 0.15,
        "E_coli": 0.45,
        "treatment_history": '[{"medication": "Infliximab", "response": "partial", "start_date": "2018-05-01", "end_date": "2019-06-15", "adverse_events": ["infusion reaction"]}, {"medication": "Azathioprine", "response": "none", "start_date": "2019-07-01", "end_date": "2020-01-15"}]',
        "extraintestinal_manifestations": "arthritis, erythema nodosum",
        "comorbidities": "hypertension, asthma"
    }
    
    # Test creating patient profile from row
    row = pd.Series(patient_data)
    profile = transformer._create_patient_profile_from_row(row)
    print("Patient Profile:")
    print(json.dumps(profile, indent=2))
    
    # Test transforming for genetic engine
    genetic_format = transformer.transform_patient_for_genetic_engine(profile)
    print("\nGenetic Engine Format:")
    print(json.dumps(genetic_format, indent=2))

if __name__ == "__main__":
    main()