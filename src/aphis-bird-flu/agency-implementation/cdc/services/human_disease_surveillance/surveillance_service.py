"""
Human Disease Surveillance Service for the CDC implementation.

This service provides functionality for human disease surveillance, including
case management, data integration from healthcare systems, and public health
reporting.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import date, datetime
import logging
import uuid

from agency_implementation.cdc.models.human_disease import (
    HumanDiseaseCase, CaseClassification, DiseaseType
)
from .repository import HumanDiseaseRepository
from .adapters import HealthcareSystemAdapter, PublicHealthReportingAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HumanDiseaseSurveillanceService:
    """
    Service for human disease surveillance.
    
    This service provides functionality for:
    1. Case management (create, update, query)
    2. Healthcare system integration
    3. Public health reporting
    4. Data import and export
    5. Quality assurance and validation
    """
    
    def __init__(
        self,
        repository: HumanDiseaseRepository,
        healthcare_adapter: Optional[HealthcareSystemAdapter] = None,
        reporting_adapter: Optional[PublicHealthReportingAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the service.
        
        Args:
            repository: Repository for human disease cases
            healthcare_adapter: Adapter for healthcare system integration
            reporting_adapter: Adapter for public health reporting
            config: Service configuration
        """
        self.repository = repository
        self.healthcare_adapter = healthcare_adapter
        self.reporting_adapter = reporting_adapter
        self.config = config or {}
        
        # Initialize reporter thresholds for automatic reporting
        self.reporting_thresholds = self.config.get('reporting_thresholds', {
            'covid19': 1,  # Always report COVID-19 cases
            'influenza': 5,  # Report 5+ influenza cases as an outbreak
            'measles': 1,  # Always report measles cases
            'default': 3  # Default threshold for other diseases
        })
        
        # Set up automatic case validation
        self.auto_validate = self.config.get('auto_validate', True)
        
        logger.info("HumanDiseaseSurveillanceService initialized")
    
    def get_case(self, case_id: str) -> Optional[HumanDiseaseCase]:
        """
        Get a case by ID.
        
        Args:
            case_id: The ID of the case to retrieve
            
        Returns:
            The case if found, None otherwise
        """
        return self.repository.get_by_id(case_id)
    
    def get_all_cases(self) -> List[HumanDiseaseCase]:
        """
        Get all cases.
        
        Returns:
            List of all cases
        """
        return self.repository.get_all()
    
    def create_case(self, case_data: Dict[str, Any]) -> HumanDiseaseCase:
        """
        Create a new case.
        
        Args:
            case_data: Dictionary with case data
            
        Returns:
            The created case
            
        Raises:
            ValueError: If case data is invalid
        """
        # Validate required fields
        required_fields = ['patient_id', 'disease_type', 'onset_date', 'report_date', 'location']
        for field in required_fields:
            if field not in case_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the case
        case = HumanDiseaseCase(**case_data)
        
        # Perform automatic validation if enabled
        if self.auto_validate:
            self._validate_case(case)
        
        # Save the case
        created_case = self.repository.create(case)
        
        # Check if case should be automatically reported
        if self._should_report_case(created_case):
            self._report_case(created_case)
        
        logger.info(f"Created new case with ID: {created_case.id}")
        return created_case
    
    def update_case(self, case_id: str, updates: Dict[str, Any]) -> Optional[HumanDiseaseCase]:
        """
        Update an existing case.
        
        Args:
            case_id: ID of the case to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated case or None if case not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the case
        case = self.repository.get_by_id(case_id)
        if not case:
            logger.warning(f"Case not found for update: {case_id}")
            return None
        
        # Update the case
        for key, value in updates.items():
            setattr(case, key, value)
            
        # Update timestamp
        case.updated_at = datetime.now().isoformat()
        
        # Perform automatic validation if enabled
        if self.auto_validate:
            self._validate_case(case)
        
        # Save the updated case
        updated_case = self.repository.update(case)
        
        # Check if the case status has changed to a reportable status
        if 'classification' in updates and self._should_report_case(updated_case):
            self._report_case(updated_case)
        
        logger.info(f"Updated case with ID: {case_id}")
        return updated_case
    
    def find_cases(self, criteria: Dict[str, Any]) -> List[HumanDiseaseCase]:
        """
        Find cases matching criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            List of matching cases
        """
        return self.repository.find(criteria)
    
    def find_cases_by_disease(self, disease_type: Union[DiseaseType, str]) -> List[HumanDiseaseCase]:
        """
        Find cases by disease type.
        
        Args:
            disease_type: The disease type to filter by
            
        Returns:
            List of cases with the specified disease type
        """
        return self.repository.find_by_disease_type(disease_type)
    
    def find_cases_by_date_range(
        self, 
        start_date: Union[date, str], 
        end_date: Union[date, str], 
        date_field: str = 'report_date'
    ) -> List[HumanDiseaseCase]:
        """
        Find cases within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            date_field: Field to filter by (report_date or onset_date)
            
        Returns:
            List of cases within the date range
        """
        return self.repository.find_by_date_range(start_date, end_date, date_field)
    
    def import_cases_from_healthcare_system(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Import cases from integrated healthcare system.
        
        Args:
            params: Parameters for the import (e.g., time range, facilities)
            
        Returns:
            Dictionary with import results
            
        Raises:
            RuntimeError: If healthcare adapter is not configured
        """
        if not self.healthcare_adapter:
            raise RuntimeError("Healthcare system adapter not configured")
        
        params = params or {}
        logger.info(f"Importing cases from healthcare system with params: {params}")
        
        # Fetch data from healthcare system
        healthcare_data = self.healthcare_adapter.fetch_data(**params)
        
        # Process results
        imported_count = 0
        errors = []
        
        for record in healthcare_data:
            try:
                # Convert to case
                case = self.healthcare_adapter.convert_to_case(record)
                if not case:
                    errors.append(f"Failed to convert record: {record.get('patient_id', 'unknown')}")
                    continue
                
                # Check if case already exists
                existing_cases = self.repository.find({
                    'patient_id': case.patient_id,
                    'disease_type': case.disease_type
                })
                
                if existing_cases:
                    # Update existing case
                    existing_case = existing_cases[0]
                    existing_case.update(**case.to_dict())
                    self.repository.update(existing_case)
                else:
                    # Create new case
                    self.repository.create(case)
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"Error processing record {record.get('patient_id', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            'total_records': len(healthcare_data),
            'imported_count': imported_count,
            'error_count': len(errors),
            'errors': errors[:10]  # Limit error list to avoid huge responses
        }
        
        logger.info(f"Healthcare import complete: {imported_count} cases imported, {len(errors)} errors")
        return result
    
    def report_case_to_public_health(self, case_id: str) -> bool:
        """
        Report a case to public health authorities.
        
        Args:
            case_id: ID of the case to report
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If reporting adapter is not configured
            ValueError: If case not found
        """
        if not self.reporting_adapter:
            raise RuntimeError("Public health reporting adapter not configured")
        
        # Get the case
        case = self.repository.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")
        
        return self._report_case(case)
    
    def _report_case(self, case: HumanDiseaseCase) -> bool:
        """
        Internal method to report a case to public health authorities.
        
        Args:
            case: The case to report
            
        Returns:
            True if successful, False otherwise
        """
        if not self.reporting_adapter:
            logger.warning("Cannot report case: Public health reporting adapter not configured")
            return False
        
        try:
            # Format case for reporting
            report_data = self.reporting_adapter.format_case_for_reporting(case)
            
            # Send to public health system
            result = self.reporting_adapter.send_data(report_data)
            
            if result:
                # Mark case as reported
                case.mark_reportable(True)
                self.repository.update(case)
                logger.info(f"Case {case.id} reported to public health authorities")
            
            return result
            
        except Exception as e:
            logger.error(f"Error reporting case {case.id} to public health: {str(e)}")
            return False
    
    def _should_report_case(self, case: HumanDiseaseCase) -> bool:
        """
        Determine if a case should be reported to public health authorities.
        
        Args:
            case: The case to check
            
        Returns:
            True if the case should be reported, False otherwise
        """
        # Always report confirmed cases
        if hasattr(case, 'classification') and case.classification == CaseClassification.CONFIRMED:
            return True
        
        # Check disease-specific thresholds
        if hasattr(case, 'disease_type'):
            disease = case.disease_type.value if hasattr(case.disease_type, 'value') else str(case.disease_type)
            
            # Get threshold for this disease or use default
            threshold = self.reporting_thresholds.get(disease, self.reporting_thresholds.get('default', 1))
            
            # If threshold is 1, always report
            if threshold == 1:
                return True
            
            # Check case count for this disease
            cases_of_type = self.repository.find_by_disease_type(disease)
            return len(cases_of_type) >= threshold
        
        return False
    
    def _validate_case(self, case: HumanDiseaseCase) -> None:
        """
        Validate a case for data quality and completeness.
        
        Args:
            case: The case to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check required fields
        if not hasattr(case, 'patient_id') or not case.patient_id:
            raise ValueError("Missing patient ID")
        
        if not hasattr(case, 'disease_type') or not case.disease_type:
            raise ValueError("Missing disease type")
        
        if not hasattr(case, 'onset_date') or not case.onset_date:
            raise ValueError("Missing onset date")
        
        if not hasattr(case, 'report_date') or not case.report_date:
            raise ValueError("Missing report date")
        
        if not hasattr(case, 'location') or not case.location:
            raise ValueError("Missing location")
        
        # Validate dates (onset date should not be in the future)
        onset_date = case.onset_date
        if isinstance(onset_date, str):
            onset_date = date.fromisoformat(onset_date)
        
        if onset_date > date.today():
            raise ValueError("Onset date cannot be in the future")
        
        # Add more validations as needed
        
        # If no errors, the case is valid
        return
    
    def generate_summary_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a summary report of cases based on filters.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Dictionary with summary report data
        """
        filters = filters or {}
        
        # Find cases matching filters
        cases = self.repository.find(filters)
        
        # Group by disease type
        by_disease = {}
        for case in cases:
            disease = case.disease_type.value if hasattr(case.disease_type, 'value') else 'unknown'
            by_disease[disease] = by_disease.get(disease, 0) + 1
        
        # Group by classification
        by_classification = {}
        for case in cases:
            classification = case.classification.value if hasattr(case.classification, 'value') else 'unknown'
            by_classification[classification] = by_classification.get(classification, 0) + 1
        
        # Group by date (last 7 days)
        by_date = {}
        for case in cases:
            report_date = case.report_date
            if isinstance(report_date, str):
                report_date = date.fromisoformat(report_date)
            date_str = report_date.isoformat()
            by_date[date_str] = by_date.get(date_str, 0) + 1
        
        # Generate report
        report = {
            'total_cases': len(cases),
            'by_disease': by_disease,
            'by_classification': by_classification,
            'by_date': by_date,
            'filters_applied': filters,
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def get_case_statistics(self, disease_type: Union[DiseaseType, str] = None) -> Dict[str, Any]:
        """
        Get statistics about cases, optionally filtered by disease type.
        
        Args:
            disease_type: Optional disease type to filter by
            
        Returns:
            Dictionary with case statistics
        """
        # Get cases, filtered by disease type if specified
        if disease_type:
            cases = self.repository.find_by_disease_type(disease_type)
        else:
            cases = self.repository.get_all()
        
        # Count by classification
        confirmed_count = 0
        probable_count = 0
        suspected_count = 0
        discarded_count = 0
        
        # Count by outcome
        recovered_count = 0
        hospitalized_count = 0
        icu_count = 0
        deceased_count = 0
        
        for case in cases:
            # Count by classification
            if hasattr(case, 'classification'):
                classification = case.classification
                if classification == CaseClassification.CONFIRMED:
                    confirmed_count += 1
                elif classification == CaseClassification.PROBABLE:
                    probable_count += 1
                elif classification == CaseClassification.SUSPECTED:
                    suspected_count += 1
                elif classification == CaseClassification.DISCARDED:
                    discarded_count += 1
            
            # Count by outcome
            if hasattr(case, 'outcome'):
                from agency_implementation.cdc.models.human_disease import DiseaseOutcome
                outcome = case.outcome
                if outcome == DiseaseOutcome.RECOVERED:
                    recovered_count += 1
                elif outcome == DiseaseOutcome.HOSPITALIZED:
                    hospitalized_count += 1
                elif outcome == DiseaseOutcome.ICU:
                    icu_count += 1
                elif outcome == DiseaseOutcome.DECEASED:
                    deceased_count += 1
        
        # Calculate rates
        total_cases = len(cases)
        fatality_rate = (deceased_count / total_cases) if total_cases > 0 else 0
        hospitalization_rate = ((hospitalized_count + icu_count) / total_cases) if total_cases > 0 else 0
        
        return {
            'total_cases': total_cases,
            'by_classification': {
                'confirmed': confirmed_count,
                'probable': probable_count,
                'suspected': suspected_count,
                'discarded': discarded_count
            },
            'by_outcome': {
                'recovered': recovered_count,
                'hospitalized': hospitalized_count,
                'icu': icu_count,
                'deceased': deceased_count
            },
            'rates': {
                'fatality_rate': fatality_rate,
                'hospitalization_rate': hospitalization_rate
            }
        }