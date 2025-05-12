"""
Case models for the APHIS Bird Flu Tracking System.
Defines data models for avian influenza cases and related entities.
"""
from typing import Dict, Any, Optional, List, Union
from datetime import date, datetime
from enum import Enum

from .base import BaseModel, GeoLocation


class CaseStatus(str, Enum):
    """Status of a bird flu case"""
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    RULED_OUT = "ruled_out"
    RECOVERED = "recovered"
    DECEASED = "deceased"
    UNKNOWN = "unknown"


class DetectionMethod(str, Enum):
    """Method used to detect avian influenza"""
    PCR_TEST = "pcr_test"
    RAPID_TEST = "rapid_test"
    SEROLOGY = "serology"
    CLINICAL_SIGNS = "clinical_signs"
    NECROPSY = "necropsy"
    SURVEILLANCE = "routine_surveillance"
    OTHER = "other"


class VirusSubtype(str, Enum):
    """Common avian influenza virus subtypes"""
    H5N1 = "h5n1"
    H5N2 = "h5n2"
    H5N8 = "h5n8"
    H7N3 = "h7n3"
    H7N9 = "h7n9"
    H9N2 = "h9n2"
    OTHER = "other"
    UNKNOWN = "unknown"


class PathogenicityLevel(str, Enum):
    """Levels of pathogenicity for avian influenza viruses"""
    HPAI = "highly_pathogenic"
    LPAI = "low_pathogenic"
    UNKNOWN = "unknown"


class SpeciesCategory(str, Enum):
    """Categories of avian species"""
    DOMESTIC_POULTRY = "domestic_poultry"
    DOMESTIC_WATERFOWL = "domestic_waterfowl"
    WILD_WATERFOWL = "wild_waterfowl"
    WILD_GALLINACEOUS = "wild_gallinaceous"
    WILD_OTHER = "wild_other"
    CAPTIVE_WILD = "captive_wild"
    OTHER = "other"


class BirdFluCase(BaseModel):
    """A confirmed or suspected bird flu case"""
    
    def __init__(
        self,
        location: Union[GeoLocation, Dict[str, Any]],
        detection_date: Union[date, str],
        species: str,
        species_category: Union[SpeciesCategory, str],
        status: Union[CaseStatus, str] = CaseStatus.SUSPECTED,
        subtype: Union[VirusSubtype, str] = VirusSubtype.UNKNOWN,
        pathogenicity: Union[PathogenicityLevel, str] = PathogenicityLevel.UNKNOWN,
        detection_method: Union[DetectionMethod, str] = DetectionMethod.SURVEILLANCE,
        sample_id: Optional[str] = None,
        genetic_sequence_id: Optional[str] = None,
        reported_by: Optional[str] = None,
        related_cases: Optional[List[str]] = None,
        flock_size: Optional[int] = None,
        mortality_count: Optional[int] = None,
        site_id: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a bird flu case"""
        # Convert location dict to GeoLocation if needed
        if isinstance(location, dict):
            location = GeoLocation.from_dict(location)
        
        # Convert date string to date if needed
        if isinstance(detection_date, str):
            try:
                detection_date = date.fromisoformat(detection_date)
            except ValueError:
                # Try with datetime format and extract date
                detection_date = datetime.fromisoformat(detection_date).date()
        
        # Convert string enums to Enum values if needed
        if isinstance(status, str):
            status = CaseStatus(status)
        
        if isinstance(subtype, str):
            subtype = VirusSubtype(subtype)
        
        if isinstance(pathogenicity, str):
            pathogenicity = PathogenicityLevel(pathogenicity)
        
        if isinstance(detection_method, str):
            detection_method = DetectionMethod(detection_method)
        
        if isinstance(species_category, str):
            species_category = SpeciesCategory(species_category)
        
        # Set case properties
        super().__init__(
            location=location,
            detection_date=detection_date,
            species=species,
            species_category=species_category,
            status=status,
            subtype=subtype,
            pathogenicity=pathogenicity,
            detection_method=detection_method,
            sample_id=sample_id,
            genetic_sequence_id=genetic_sequence_id,
            reported_by=reported_by,
            related_cases=related_cases or [],
            flock_size=flock_size,
            mortality_count=mortality_count,
            site_id=site_id,
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
        if isinstance(result.get('detection_date'), date):
            result['detection_date'] = result['detection_date'].isoformat()
        
        # Convert enum values to strings
        for field in ['status', 'subtype', 'pathogenicity', 'detection_method', 'species_category']:
            if field in result and isinstance(result[field], Enum):
                result[field] = result[field].value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BirdFluCase':
        """Create from dictionary representation"""
        return cls(**data)
    
    def calculate_mortality_rate(self) -> Optional[float]:
        """Calculate mortality rate if flock size and mortality count are available"""
        if self.flock_size and self.flock_size > 0 and self.mortality_count is not None:
            return self.mortality_count / self.flock_size
        return None
    
    def add_related_case(self, case_id: str) -> None:
        """Add a related case ID"""
        if case_id not in self.related_cases:
            self.related_cases.append(case_id)
            self.updated_at = datetime.now().isoformat()
    
    def update_status(self, new_status: Union[CaseStatus, str]) -> None:
        """Update the case status"""
        if isinstance(new_status, str):
            new_status = CaseStatus(new_status)
        
        self.status = new_status
        self.updated_at = datetime.now().isoformat()


class LaboratorySample(BaseModel):
    """A laboratory sample associated with a bird flu case"""
    
    def __init__(
        self,
        case_id: str,
        collection_date: Union[date, str],
        sample_type: str,
        collected_by: str,
        lab_id: Optional[str] = None,
        received_date: Optional[Union[date, str]] = None,
        testing_status: str = "pending",
        results: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a laboratory sample"""
        # Convert date strings to date objects if needed
        if isinstance(collection_date, str):
            collection_date = date.fromisoformat(collection_date)
        
        if isinstance(received_date, str) and received_date:
            received_date = date.fromisoformat(received_date)
        
        super().__init__(
            case_id=case_id,
            collection_date=collection_date,
            sample_type=sample_type,
            collected_by=collected_by,
            lab_id=lab_id,
            received_date=received_date,
            testing_status=testing_status,
            results=results or {},
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert date objects to strings
        for field in ['collection_date', 'received_date']:
            if field in result and isinstance(result[field], date):
                result[field] = result[field].isoformat()
        
        return result
    
    def add_result(self, test_name: str, result: Any, test_date: Union[date, str] = None) -> None:
        """Add a test result"""
        if test_date is None:
            test_date = date.today()
        elif isinstance(test_date, str):
            test_date = date.fromisoformat(test_date)
        
        if 'results' not in self.__dict__:
            self.results = {}
        
        self.results[test_name] = {
            'result': result,
            'test_date': test_date.isoformat()
        }
        
        # Update testing status if we have results
        if self.results:
            self.testing_status = "completed"
        
        self.updated_at = datetime.now().isoformat()


class GeneticSequence(BaseModel):
    """A genetic sequence from a bird flu virus"""
    
    def __init__(
        self,
        case_id: str,
        sample_id: str,
        sequence_data: str,
        sequencing_method: str,
        sequencing_date: Union[date, str],
        gene_segments: List[str],
        sequence_quality: float,
        external_database_ids: Optional[Dict[str, str]] = None,
        analysis_results: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a genetic sequence"""
        # Convert date string to date if needed
        if isinstance(sequencing_date, str):
            sequencing_date = date.fromisoformat(sequencing_date)
        
        super().__init__(
            case_id=case_id,
            sample_id=sample_id,
            sequence_data=sequence_data,
            sequencing_method=sequencing_method,
            sequencing_date=sequencing_date,
            gene_segments=gene_segments,
            sequence_quality=sequence_quality,
            external_database_ids=external_database_ids or {},
            analysis_results=analysis_results or {},
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert date to string
        if isinstance(result.get('sequencing_date'), date):
            result['sequencing_date'] = result['sequencing_date'].isoformat()
        
        return result
    
    def add_analysis_result(self, analysis_type: str, result: Any) -> None:
        """Add an analysis result"""
        if 'analysis_results' not in self.__dict__:
            self.analysis_results = {}
        
        self.analysis_results[analysis_type] = {
            'result': result,
            'analysis_date': datetime.now().isoformat()
        }
        
        self.updated_at = datetime.now().isoformat()
    
    def add_external_id(self, database_name: str, external_id: str) -> None:
        """Add an external database ID"""
        if 'external_database_ids' not in self.__dict__:
            self.external_database_ids = {}
        
        self.external_database_ids[database_name] = external_id
        self.updated_at = datetime.now().isoformat()