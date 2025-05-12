#!/usr/bin/env python3
"""
Patient Model for Crohn's Disease Treatment System

This module defines the data models for patient records in the context
of Crohn's disease treatment.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import datetime
import json

class Gender(Enum):
    """Patient gender"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"

class CrohnsLocation(Enum):
    """Crohn's disease location"""
    ILEAL = "ileal"
    COLONIC = "colonic"
    ILEOCOLONIC = "ileocolonic"
    PERIANAL = "perianal"
    UPPER_GI = "upper_gi"
    UNKNOWN = "unknown"

class DiseaseSeverity(Enum):
    """Disease severity"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    UNKNOWN = "unknown"

class TreatmentResponse(Enum):
    """Response to treatment"""
    COMPLETE = "complete"
    PARTIAL = "partial"
    NONE = "none"
    ADVERSE = "adverse"
    UNKNOWN = "unknown"

@dataclass
class Address:
    """Patient address"""
    line: List[str] = field(default_factory=list)
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

@dataclass
class Contact:
    """Patient contact information"""
    name: Optional[str] = None
    relationship: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Address] = None

@dataclass
class GeneralInfo:
    """General patient information"""
    medical_record_number: Optional[str] = None
    gender: Gender = Gender.UNKNOWN
    birth_date: Optional[str] = None
    deceased: bool = False
    deceased_date: Optional[str] = None
    address: Optional[Address] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    language: Optional[str] = None
    marital_status: Optional[str] = None
    contacts: List[Contact] = field(default_factory=list)

@dataclass
class GeneticMarker:
    """Genetic marker"""
    name: str
    value: str
    interpretation: Optional[str] = None
    date: Optional[str] = None

@dataclass
class BiomarkerValue:
    """Biomarker value"""
    value: float
    unit: str
    date: str
    reference_range: Optional[Dict[str, float]] = None
    abnormal: Optional[bool] = None

@dataclass
class Biomarker:
    """Biomarker information"""
    name: str
    code: Optional[str] = None
    system: Optional[str] = None  # e.g., "LOINC"
    values: List[BiomarkerValue] = field(default_factory=list)

@dataclass
class Medication:
    """Medication information"""
    name: str
    code: Optional[str] = None
    system: Optional[str] = None  # e.g., "RxNorm"
    dosage: Optional[str] = None
    unit: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None  # active, completed, stopped
    reason_stopped: Optional[str] = None

@dataclass
class TreatmentHistory:
    """Treatment history"""
    medication: Medication
    response: TreatmentResponse = TreatmentResponse.UNKNOWN
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    side_effects: List[str] = field(default_factory=list)
    notes: Optional[str] = None

@dataclass
class Surgery:
    """Surgery information"""
    procedure: str
    date: str
    site: Optional[str] = None
    indication: Optional[str] = None
    outcome: Optional[str] = None
    complications: List[str] = field(default_factory=list)
    notes: Optional[str] = None

@dataclass
class Hospitalization:
    """Hospitalization information"""
    admission_date: str
    discharge_date: Optional[str] = None
    reason: Optional[str] = None
    procedures: List[str] = field(default_factory=list)
    diagnoses: List[str] = field(default_factory=list)
    notes: Optional[str] = None

@dataclass
class CrohnsInfo:
    """Crohn's disease specific information"""
    diagnosis_date: Optional[str] = None
    locations: List[CrohnsLocation] = field(default_factory=list)
    severity: DiseaseSeverity = DiseaseSeverity.UNKNOWN
    disease_activity_index: Optional[float] = None  # CDAI or similar
    extraintestinal_manifestations: List[str] = field(default_factory=list)
    complications: List[str] = field(default_factory=list)
    treatment_history: List[TreatmentHistory] = field(default_factory=list)
    surgeries: List[Surgery] = field(default_factory=list)
    hospitalizations: List[Hospitalization] = field(default_factory=list)
    family_history: bool = False
    notes: Optional[str] = None

@dataclass
class Assessment:
    """Clinical assessment"""
    date: str
    provider: Optional[str] = None
    setting: Optional[str] = None  # office, hospital, virtual
    symptoms: List[str] = field(default_factory=list)
    physical_findings: Dict[str, Any] = field(default_factory=dict)
    disease_activity_index: Optional[float] = None  # CDAI or similar
    severity_assessment: Optional[DiseaseSeverity] = None
    plan: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class PatientRecord:
    """Complete patient record for Crohn's disease treatment"""
    id: str
    general_info: GeneralInfo = field(default_factory=GeneralInfo)
    crohns_info: CrohnsInfo = field(default_factory=CrohnsInfo)
    genetic_markers: List[GeneticMarker] = field(default_factory=list)
    biomarkers: List[Biomarker] = field(default_factory=list)
    current_medications: List[Medication] = field(default_factory=list)
    assessments: List[Assessment] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    comorbidities: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "general_info": {
                "medical_record_number": self.general_info.medical_record_number,
                "gender": self.general_info.gender.value,
                "birth_date": self.general_info.birth_date,
                "deceased": self.general_info.deceased,
                "deceased_date": self.general_info.deceased_date,
                "address": vars(self.general_info.address) if self.general_info.address else None,
                "phone": self.general_info.phone,
                "email": self.general_info.email,
                "language": self.general_info.language,
                "marital_status": self.general_info.marital_status,
                "contacts": [vars(contact) for contact in self.general_info.contacts]
            },
            "crohns_info": {
                "diagnosis_date": self.crohns_info.diagnosis_date,
                "locations": [location.value for location in self.crohns_info.locations],
                "severity": self.crohns_info.severity.value,
                "disease_activity_index": self.crohns_info.disease_activity_index,
                "extraintestinal_manifestations": self.crohns_info.extraintestinal_manifestations,
                "complications": self.crohns_info.complications,
                "treatment_history": [
                    {
                        "medication": {
                            "name": th.medication.name,
                            "code": th.medication.code,
                            "system": th.medication.system,
                            "dosage": th.medication.dosage,
                            "unit": th.medication.unit,
                            "route": th.medication.route,
                            "frequency": th.medication.frequency,
                            "start_date": th.medication.start_date,
                            "end_date": th.medication.end_date,
                            "status": th.medication.status,
                            "reason_stopped": th.medication.reason_stopped
                        },
                        "response": th.response.value,
                        "start_date": th.start_date,
                        "end_date": th.end_date,
                        "side_effects": th.side_effects,
                        "notes": th.notes
                    }
                    for th in self.crohns_info.treatment_history
                ],
                "surgeries": [vars(surgery) for surgery in self.crohns_info.surgeries],
                "hospitalizations": [vars(hosp) for hosp in self.crohns_info.hospitalizations],
                "family_history": self.crohns_info.family_history,
                "notes": self.crohns_info.notes
            },
            "genetic_markers": [vars(marker) for marker in self.genetic_markers],
            "biomarkers": [
                {
                    "name": biomarker.name,
                    "code": biomarker.code,
                    "system": biomarker.system,
                    "values": [vars(value) for value in biomarker.values]
                }
                for biomarker in self.biomarkers
            ],
            "current_medications": [vars(med) for med in self.current_medications],
            "assessments": [vars(assessment) for assessment in self.assessments],
            "allergies": self.allergies,
            "comorbidities": self.comorbidities,
            "notes": self.notes,
            "last_updated": self.last_updated
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientRecord':
        """Create from dictionary"""
        # Create general info
        general_data = data.get("general_info", {})
        address = None
        if general_data.get("address"):
            address = Address(**general_data["address"])
        
        contacts = []
        for contact_data in general_data.get("contacts", []):
            contact_address = None
            if contact_data.get("address"):
                contact_address = Address(**contact_data["address"])
            contact_data["address"] = contact_address
            contacts.append(Contact(**contact_data))
        
        general_info = GeneralInfo(
            medical_record_number=general_data.get("medical_record_number"),
            gender=Gender(general_data.get("gender", "unknown")),
            birth_date=general_data.get("birth_date"),
            deceased=general_data.get("deceased", False),
            deceased_date=general_data.get("deceased_date"),
            address=address,
            phone=general_data.get("phone"),
            email=general_data.get("email"),
            language=general_data.get("language"),
            marital_status=general_data.get("marital_status"),
            contacts=contacts
        )
        
        # Create Crohn's info
        crohns_data = data.get("crohns_info", {})
        
        treatment_history = []
        for th_data in crohns_data.get("treatment_history", []):
            med_data = th_data.get("medication", {})
            medication = Medication(
                name=med_data.get("name", ""),
                code=med_data.get("code"),
                system=med_data.get("system"),
                dosage=med_data.get("dosage"),
                unit=med_data.get("unit"),
                route=med_data.get("route"),
                frequency=med_data.get("frequency"),
                start_date=med_data.get("start_date"),
                end_date=med_data.get("end_date"),
                status=med_data.get("status"),
                reason_stopped=med_data.get("reason_stopped")
            )
            
            treatment_history.append(TreatmentHistory(
                medication=medication,
                response=TreatmentResponse(th_data.get("response", "unknown")),
                start_date=th_data.get("start_date"),
                end_date=th_data.get("end_date"),
                side_effects=th_data.get("side_effects", []),
                notes=th_data.get("notes")
            ))
        
        surgeries = []
        for surgery_data in crohns_data.get("surgeries", []):
            surgeries.append(Surgery(**surgery_data))
        
        hospitalizations = []
        for hosp_data in crohns_data.get("hospitalizations", []):
            hospitalizations.append(Hospitalization(**hosp_data))
        
        crohns_info = CrohnsInfo(
            diagnosis_date=crohns_data.get("diagnosis_date"),
            locations=[CrohnsLocation(loc) for loc in crohns_data.get("locations", [])],
            severity=DiseaseSeverity(crohns_data.get("severity", "unknown")),
            disease_activity_index=crohns_data.get("disease_activity_index"),
            extraintestinal_manifestations=crohns_data.get("extraintestinal_manifestations", []),
            complications=crohns_data.get("complications", []),
            treatment_history=treatment_history,
            surgeries=surgeries,
            hospitalizations=hospitalizations,
            family_history=crohns_data.get("family_history", False),
            notes=crohns_data.get("notes")
        )
        
        # Create genetic markers
        genetic_markers = []
        for marker_data in data.get("genetic_markers", []):
            genetic_markers.append(GeneticMarker(**marker_data))
        
        # Create biomarkers
        biomarkers = []
        for biomarker_data in data.get("biomarkers", []):
            values = []
            for value_data in biomarker_data.get("values", []):
                values.append(BiomarkerValue(**value_data))
            
            biomarkers.append(Biomarker(
                name=biomarker_data.get("name", ""),
                code=biomarker_data.get("code"),
                system=biomarker_data.get("system"),
                values=values
            ))
        
        # Create current medications
        current_medications = []
        for med_data in data.get("current_medications", []):
            current_medications.append(Medication(**med_data))
        
        # Create assessments
        assessments = []
        for assessment_data in data.get("assessments", []):
            severity_value = assessment_data.get("severity_assessment")
            severity = None
            if severity_value:
                severity = DiseaseSeverity(severity_value)
            
            assessment_data["severity_assessment"] = severity
            assessments.append(Assessment(**assessment_data))
        
        # Create patient record
        return cls(
            id=data.get("id", ""),
            general_info=general_info,
            crohns_info=crohns_info,
            genetic_markers=genetic_markers,
            biomarkers=biomarkers,
            current_medications=current_medications,
            assessments=assessments,
            allergies=data.get("allergies", []),
            comorbidities=data.get("comorbidities", []),
            notes=data.get("notes"),
            last_updated=data.get("last_updated", datetime.datetime.now().isoformat())
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PatientRecord':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

# Example usage
def main():
    # Create a sample patient record
    patient = PatientRecord(
        id="P12345",
        general_info=GeneralInfo(
            medical_record_number="MRN123456",
            gender=Gender.MALE,
            birth_date="1975-05-15",
            address=Address(
                line=["123 Main St"],
                city="Anytown",
                state="CA",
                postal_code="12345",
                country="USA"
            ),
            phone="555-123-4567",
            email="patient@example.com"
        ),
        crohns_info=CrohnsInfo(
            diagnosis_date="2015-03-10",
            locations=[CrohnsLocation.ILEOCOLONIC],
            severity=DiseaseSeverity.MODERATE,
            disease_activity_index=220,
            extraintestinal_manifestations=["Arthralgia"],
            complications=["Stricture"],
            treatment_history=[
                TreatmentHistory(
                    medication=Medication(
                        name="Infliximab",
                        dosage="5",
                        unit="mg/kg",
                        frequency="Every 8 weeks",
                        start_date="2015-04-15",
                        end_date="2018-06-20",
                        status="stopped",
                        reason_stopped="Loss of response"
                    ),
                    response=TreatmentResponse.PARTIAL,
                    start_date="2015-04-15",
                    end_date="2018-06-20",
                    side_effects=["Infusion reaction"]
                )
            ]
        ),
        genetic_markers=[
            GeneticMarker(
                name="NOD2",
                value="variant",
                interpretation="Associated with increased risk of Crohn's disease"
            )
        ],
        biomarkers=[
            Biomarker(
                name="C-Reactive Protein",
                code="1988-5",
                system="LOINC",
                values=[
                    BiomarkerValue(
                        value=15.3,
                        unit="mg/L",
                        date="2023-01-15",
                        reference_range={"low": 0, "high": 5},
                        abnormal=True
                    )
                ]
            ),
            Biomarker(
                name="Fecal Calprotectin",
                code="2857-1",
                system="LOINC",
                values=[
                    BiomarkerValue(
                        value=350,
                        unit="µg/g",
                        date="2023-01-10",
                        reference_range={"low": 0, "high": 50},
                        abnormal=True
                    )
                ]
            )
        ],
        current_medications=[
            Medication(
                name="Upadacitinib",
                dosage="15",
                unit="mg",
                frequency="Once daily",
                start_date="2022-10-15",
                status="active"
            )
        ],
        assessments=[
            Assessment(
                date="2023-01-20",
                provider="Dr. Smith",
                setting="office",
                symptoms=["Abdominal pain", "Diarrhea"],
                disease_activity_index=210,
                severity_assessment=DiseaseSeverity.MODERATE,
                plan="Continue current medication, follow up in 3 months"
            )
        ],
        allergies=["Penicillin"],
        comorbidities=["Hypertension"]
    )
    
    # Convert to JSON and print
    json_data = patient.to_json()
    print(json_data)
    
    # Convert back to patient record
    patient2 = PatientRecord.from_json(json_data)
    print(f"Patient ID: {patient2.id}")
    print(f"Name: {patient2.general_info.medical_record_number}")
    print(f"Diagnosis date: {patient2.crohns_info.diagnosis_date}")
    print(f"Current medications: {[med.name for med in patient2.current_medications]}")

if __name__ == "__main__":
    main()