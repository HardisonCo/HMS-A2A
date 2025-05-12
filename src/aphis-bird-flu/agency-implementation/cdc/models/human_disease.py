"""
Human disease models for the CDC implementation of the Adaptive Surveillance and Response System.
Defines data models for human disease cases and related entities.
"""
from typing import Dict, Any, Optional, List, Union
from datetime import date, datetime
from enum import Enum

from .base import CDCBaseModel, GeoLocation, HealthcareFacility


class CaseClassification(str, Enum):
    """Classification of a human disease case"""
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    SUSPECTED = "suspected"
    DISCARDED = "discarded"
    UNKNOWN = "unknown"


class DiseaseOutcome(str, Enum):
    """Outcome of a disease case"""
    RECOVERED = "recovered"
    HOSPITALIZED = "hospitalized"
    ICU = "icu"
    DECEASED = "deceased"
    UNKNOWN = "unknown"
    ONGOING = "ongoing"


class TransmissionMode(str, Enum):
    """Mode of disease transmission"""
    PERSON_TO_PERSON = "person_to_person"
    FOODBORNE = "foodborne"
    WATERBORNE = "waterborne"
    VECTORBORNE = "vectorborne"
    AIRBORNE = "airborne"
    CONTACT = "contact"
    NOSOCOMIAL = "nosocomial"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Risk level for disease cases"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class DiseaseType(str, Enum):
    """Types of diseases for disease cases"""
    COVID19 = "covid19"
    INFLUENZA = "influenza"
    MEASLES = "measles"
    TUBERCULOSIS = "tuberculosis"
    SALMONELLOSIS = "salmonellosis"
    E_COLI = "e_coli"
    HEPATITIS = "hepatitis"
    LYME = "lyme"
    WEST_NILE = "west_nile"
    DENGUE = "dengue"
    ZIKA = "zika"
    OTHER = "other"


class HumanDiseaseCase(CDCBaseModel):
    """A human disease case for CDC surveillance"""
    
    def __init__(
        self,
        patient_id: str,
        disease_type: Union[DiseaseType, str],
        onset_date: Union[date, str],
        report_date: Union[date, str],
        location: Union[GeoLocation, Dict[str, Any]],
        classification: Union[CaseClassification, str] = CaseClassification.SUSPECTED,
        outcome: Union[DiseaseOutcome, str] = DiseaseOutcome.ONGOING,
        transmission_mode: Union[TransmissionMode, str] = TransmissionMode.UNKNOWN,
        risk_level: Union[RiskLevel, str] = RiskLevel.UNKNOWN,
        jurisdiction: Optional[str] = None,
        treating_facility: Optional[Union[HealthcareFacility, Dict[str, Any], str]] = None,
        demographics: Optional[Dict[str, Any]] = None,
        vaccination_status: Optional[Dict[str, Any]] = None,
        symptoms: Optional[List[str]] = None,
        hospitalization_status: Optional[Dict[str, Any]] = None,
        travel_history: Optional[List[Dict[str, Any]]] = None,
        related_cases: Optional[List[str]] = None,
        exposure_events: Optional[List[Dict[str, Any]]] = None,
        laboratory_results: Optional[List[Dict[str, Any]]] = None,
        genetic_data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a human disease case"""
        # Convert location dict to GeoLocation if needed
        if isinstance(location, dict):
            location = GeoLocation.from_dict(location)
        
        # Convert date strings to date objects if needed
        if isinstance(onset_date, str):
            try:
                onset_date = date.fromisoformat(onset_date)
            except ValueError:
                # Try with datetime format and extract date
                onset_date = datetime.fromisoformat(onset_date).date()
        
        if isinstance(report_date, str):
            try:
                report_date = date.fromisoformat(report_date)
            except ValueError:
                # Try with datetime format and extract date
                report_date = datetime.fromisoformat(report_date).date()
        
        # Convert string enums to Enum values if needed
        if isinstance(disease_type, str):
            disease_type = DiseaseType(disease_type)
        
        if isinstance(classification, str):
            classification = CaseClassification(classification)
        
        if isinstance(outcome, str):
            outcome = DiseaseOutcome(outcome)
        
        if isinstance(transmission_mode, str):
            transmission_mode = TransmissionMode(transmission_mode)
        
        if isinstance(risk_level, str):
            risk_level = RiskLevel(risk_level)
        
        # Handle treating facility
        if isinstance(treating_facility, dict):
            treating_facility = HealthcareFacility.from_dict(treating_facility)
        
        # Set defaults for optional parameters
        demographics = demographics or {}
        vaccination_status = vaccination_status or {}
        symptoms = symptoms or []
        hospitalization_status = hospitalization_status or {}
        travel_history = travel_history or []
        related_cases = related_cases or []
        exposure_events = exposure_events or []
        laboratory_results = laboratory_results or []
        genetic_data = genetic_data or {}
        
        # Initialize the case
        super().__init__(
            patient_id=patient_id,
            disease_type=disease_type,
            onset_date=onset_date,
            report_date=report_date,
            location=location,
            classification=classification,
            outcome=outcome,
            transmission_mode=transmission_mode,
            risk_level=risk_level,
            jurisdiction=jurisdiction,
            treating_facility=treating_facility,
            demographics=demographics,
            vaccination_status=vaccination_status,
            symptoms=symptoms,
            hospitalization_status=hospitalization_status,
            travel_history=travel_history,
            related_cases=related_cases,
            exposure_events=exposure_events,
            laboratory_results=laboratory_results,
            genetic_data=genetic_data,
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if isinstance(result.get('location'), GeoLocation):
            result['location'] = result['location'].to_dict()
        
        if isinstance(result.get('treating_facility'), HealthcareFacility):
            result['treating_facility'] = result['treating_facility'].to_dict()
        
        # Convert date objects to strings
        for field in ['onset_date', 'report_date']:
            if field in result and isinstance(result[field], date):
                result[field] = result[field].isoformat()
        
        # Convert enum values to strings
        for field in ['disease_type', 'classification', 'outcome', 'transmission_mode', 'risk_level']:
            if field in result and isinstance(result[field], Enum):
                result[field] = result[field].value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HumanDiseaseCase':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_laboratory_result(self, result: Dict[str, Any]) -> None:
        """Add a laboratory test result"""
        if 'laboratory_results' not in self.__dict__:
            self.laboratory_results = []
        
        # Add timestamp if not provided
        if 'date' not in result:
            result['date'] = datetime.now().isoformat()
        
        self.laboratory_results.append(result)
        self.updated_at = datetime.now().isoformat()
    
    def add_related_case(self, case_id: str) -> None:
        """Add a related case ID"""
        if 'related_cases' not in self.__dict__:
            self.related_cases = []
        
        if case_id not in self.related_cases:
            self.related_cases.append(case_id)
            self.updated_at = datetime.now().isoformat()
    
    def update_classification(self, classification: Union[CaseClassification, str]) -> None:
        """Update the case classification"""
        if isinstance(classification, str):
            classification = CaseClassification(classification)
        
        self.classification = classification
        self.updated_at = datetime.now().isoformat()
    
    def update_outcome(self, outcome: Union[DiseaseOutcome, str]) -> None:
        """Update the disease outcome"""
        if isinstance(outcome, str):
            outcome = DiseaseOutcome(outcome)
        
        self.outcome = outcome
        self.updated_at = datetime.now().isoformat()
    
    def add_exposure_event(self, exposure_event: Dict[str, Any]) -> None:
        """Add an exposure event"""
        if 'exposure_events' not in self.__dict__:
            self.exposure_events = []
        
        # Add timestamp if not provided
        if 'date' not in exposure_event:
            exposure_event['date'] = datetime.now().isoformat()
        
        self.exposure_events.append(exposure_event)
        self.updated_at = datetime.now().isoformat()
    
    def calculate_days_since_onset(self) -> Optional[int]:
        """Calculate days since symptom onset"""
        if hasattr(self, 'onset_date') and self.onset_date:
            if isinstance(self.onset_date, str):
                onset = date.fromisoformat(self.onset_date)
            else:
                onset = self.onset_date
            return (date.today() - onset).days
        return None


class Contact(CDCBaseModel):
    """A contact of a disease case for contact tracing"""
    
    def __init__(
        self,
        person_id: str,
        case_id: str,
        contact_date: Union[date, str],
        location: Union[GeoLocation, Dict[str, Any]],
        contact_type: str,
        risk_assessment: Union[RiskLevel, str] = RiskLevel.UNKNOWN,
        contact_info: Optional[Dict[str, Any]] = None,
        demographics: Optional[Dict[str, Any]] = None,
        symptoms: Optional[List[str]] = None,
        exposure_duration_minutes: Optional[int] = None,
        monitoring_status: str = "pending",
        isolation_status: str = "not_isolated",
        test_results: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a contact"""
        # Convert location dict to GeoLocation if needed
        if isinstance(location, dict):
            location = GeoLocation.from_dict(location)
        
        # Convert date string to date if needed
        if isinstance(contact_date, str):
            try:
                contact_date = date.fromisoformat(contact_date)
            except ValueError:
                # Try with datetime format and extract date
                contact_date = datetime.fromisoformat(contact_date).date()
        
        # Convert string enum to Enum value if needed
        if isinstance(risk_assessment, str):
            risk_assessment = RiskLevel(risk_assessment)
        
        # Set defaults for optional parameters
        contact_info = contact_info or {}
        demographics = demographics or {}
        symptoms = symptoms or []
        test_results = test_results or []
        
        # Initialize the contact
        super().__init__(
            person_id=person_id,
            case_id=case_id,
            contact_date=contact_date,
            location=location,
            contact_type=contact_type,
            risk_assessment=risk_assessment,
            contact_info=contact_info,
            demographics=demographics,
            symptoms=symptoms,
            exposure_duration_minutes=exposure_duration_minutes,
            monitoring_status=monitoring_status,
            isolation_status=isolation_status,
            test_results=test_results,
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if isinstance(result.get('location'), GeoLocation):
            result['location'] = result['location'].to_dict()
        
        # Convert date to string
        if isinstance(result.get('contact_date'), date):
            result['contact_date'] = result['contact_date'].isoformat()
        
        # Convert enum values to strings
        for field in ['risk_assessment']:
            if field in result and isinstance(result[field], Enum):
                result[field] = result[field].value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Create from dictionary representation"""
        return cls(**data)
    
    def update_monitoring_status(self, status: str) -> None:
        """Update the monitoring status"""
        self.monitoring_status = status
        self.updated_at = datetime.now().isoformat()
    
    def update_isolation_status(self, status: str) -> None:
        """Update the isolation status"""
        self.isolation_status = status
        self.updated_at = datetime.now().isoformat()
    
    def add_test_result(self, result: Dict[str, Any]) -> None:
        """Add a test result"""
        if 'test_results' not in self.__dict__:
            self.test_results = []
        
        # Add timestamp if not provided
        if 'date' not in result:
            result['date'] = datetime.now().isoformat()
        
        self.test_results.append(result)
        self.updated_at = datetime.now().isoformat()
    
    def add_symptoms(self, symptoms: List[str]) -> None:
        """Add symptoms"""
        if 'symptoms' not in self.__dict__:
            self.symptoms = []
        
        for symptom in symptoms:
            if symptom not in self.symptoms:
                self.symptoms.append(symptom)
        
        self.updated_at = datetime.now().isoformat()
    
    def calculate_days_since_contact(self) -> Optional[int]:
        """Calculate days since contact"""
        if hasattr(self, 'contact_date') and self.contact_date:
            if isinstance(self.contact_date, str):
                contact_date = date.fromisoformat(self.contact_date)
            else:
                contact_date = self.contact_date
            return (date.today() - contact_date).days
        return None


class Cluster(CDCBaseModel):
    """A cluster of related disease cases"""
    
    def __init__(
        self,
        name: str,
        disease_type: Union[DiseaseType, str],
        cases: List[str],
        start_date: Union[date, str],
        end_date: Optional[Union[date, str]] = None,
        location: Optional[Union[GeoLocation, Dict[str, Any]]] = None,
        regions: Optional[List[str]] = None,
        status: str = "active",
        transmission_mode: Union[TransmissionMode, str] = TransmissionMode.UNKNOWN,
        risk_level: Union[RiskLevel, str] = RiskLevel.UNKNOWN,
        index_case_id: Optional[str] = None,
        common_exposures: Optional[List[Dict[str, Any]]] = None,
        genetic_relatedness: Optional[Dict[str, Any]] = None,
        interventions: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a disease cluster"""
        # Convert location dict to GeoLocation if needed
        if isinstance(location, dict):
            location = GeoLocation.from_dict(location)
        
        # Convert date strings to date objects if needed
        if isinstance(start_date, str):
            try:
                start_date = date.fromisoformat(start_date)
            except ValueError:
                # Try with datetime format and extract date
                start_date = datetime.fromisoformat(start_date).date()
        
        if end_date and isinstance(end_date, str):
            try:
                end_date = date.fromisoformat(end_date)
            except ValueError:
                # Try with datetime format and extract date
                end_date = datetime.fromisoformat(end_date).date()
        
        # Convert string enums to Enum values if needed
        if isinstance(disease_type, str):
            disease_type = DiseaseType(disease_type)
        
        if isinstance(transmission_mode, str):
            transmission_mode = TransmissionMode(transmission_mode)
        
        if isinstance(risk_level, str):
            risk_level = RiskLevel(risk_level)
        
        # Set defaults for optional parameters
        regions = regions or []
        common_exposures = common_exposures or []
        genetic_relatedness = genetic_relatedness or {}
        interventions = interventions or []
        
        # Initialize the cluster
        super().__init__(
            name=name,
            disease_type=disease_type,
            cases=cases,
            start_date=start_date,
            end_date=end_date,
            location=location,
            regions=regions,
            status=status,
            transmission_mode=transmission_mode,
            risk_level=risk_level,
            index_case_id=index_case_id,
            common_exposures=common_exposures,
            genetic_relatedness=genetic_relatedness,
            interventions=interventions,
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if isinstance(result.get('location'), GeoLocation):
            result['location'] = result['location'].to_dict()
        
        # Convert date objects to strings
        for field in ['start_date', 'end_date']:
            if field in result and isinstance(result[field], date):
                result[field] = result[field].isoformat()
        
        # Convert enum values to strings
        for field in ['disease_type', 'transmission_mode', 'risk_level']:
            if field in result and isinstance(result[field], Enum):
                result[field] = result[field].value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cluster':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_case(self, case_id: str) -> None:
        """Add a case to the cluster"""
        if case_id not in self.cases:
            self.cases.append(case_id)
            self.updated_at = datetime.now().isoformat()
    
    def remove_case(self, case_id: str) -> None:
        """Remove a case from the cluster"""
        if case_id in self.cases:
            self.cases.remove(case_id)
            self.updated_at = datetime.now().isoformat()
    
    def update_status(self, status: str) -> None:
        """Update the cluster status"""
        self.status = status
        self.updated_at = datetime.now().isoformat()
    
    def close_cluster(self) -> None:
        """Close the cluster with end date of today"""
        self.status = "closed"
        self.end_date = date.today()
        self.updated_at = datetime.now().isoformat()
    
    def add_intervention(self, intervention: Dict[str, Any]) -> None:
        """Add an intervention applied to the cluster"""
        if 'interventions' not in self.__dict__:
            self.interventions = []
        
        # Add timestamp if not provided
        if 'date' not in intervention:
            intervention['date'] = datetime.now().isoformat()
        
        self.interventions.append(intervention)
        self.updated_at = datetime.now().isoformat()
    
    def get_case_count(self) -> int:
        """Get the number of cases in the cluster"""
        return len(self.cases)
    
    def calculate_duration_days(self) -> Optional[int]:
        """Calculate the duration of the cluster in days"""
        if hasattr(self, 'start_date') and self.start_date:
            start = self.start_date if isinstance(self.start_date, date) else date.fromisoformat(self.start_date)
            end = None
            
            if hasattr(self, 'end_date') and self.end_date:
                end = self.end_date if isinstance(self.end_date, date) else date.fromisoformat(self.end_date)
            else:
                end = date.today()
            
            return (end - start).days
        return None