"""
Adapters for integrating with external healthcare and public health reporting systems.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import requests
from abc import ABC, abstractmethod

from agency_implementation.cdc.models.human_disease import HumanDiseaseCase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExternalSystemAdapter(ABC):
    """Base class for external system adapters"""
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch data from external system"""
        pass
    
    @abstractmethod
    def send_data(self, data: Any) -> bool:
        """Send data to external system"""
        pass


class HealthcareSystemAdapter(ExternalSystemAdapter):
    """
    Adapter for healthcare system integration.
    
    Provides methods to fetch and send data to/from healthcare information systems,
    such as electronic health records (EHR) and hospital information systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration dictionary with connection details
        """
        self.config = config
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = config.get('timeout', 30)
        
        logger.info(f"HealthcareSystemAdapter initialized for {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from healthcare system.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of data records from the healthcare system
            
        Raises:
            ConnectionError: If connection to the healthcare system fails
        """
        try:
            # In a real implementation, this would make an API call to the healthcare system
            # For demonstration, we return mock data
            if not self.api_url:
                logger.warning("API URL not configured, returning mock data")
                return self._generate_mock_data(kwargs.get('count', 5))
            
            endpoint = kwargs.get('endpoint', 'cases')
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Fetching data from {url} with params: {kwargs}")
            
            # This is where an actual API call would happen
            # response = requests.get(url, headers=self.headers, params=kwargs, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, return mock data
            return self._generate_mock_data(kwargs.get('count', 5))
            
        except Exception as e:
            logger.error(f"Error fetching data from healthcare system: {str(e)}")
            raise ConnectionError(f"Failed to connect to healthcare system: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to healthcare system.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the healthcare system
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send data: {json.dumps(data, default=str)}")
                return True
            
            endpoint = 'reports'
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Sending data to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send data: {json.dumps(data, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to healthcare system: {str(e)}")
            return False
    
    def convert_to_case(self, ehr_data: Dict[str, Any]) -> Optional[HumanDiseaseCase]:
        """
        Convert healthcare system data to a HumanDiseaseCase object.
        
        Args:
            ehr_data: Data from healthcare system
            
        Returns:
            Converted HumanDiseaseCase object or None if conversion fails
        """
        try:
            # Extract required fields
            patient_id = ehr_data.get('patient_id') or ehr_data.get('mrn')
            if not patient_id:
                logger.error("Missing patient ID in healthcare data")
                return None
            
            # Map disease type
            disease_name = ehr_data.get('diagnosis', '').lower()
            disease_type = 'other'
            if 'covid' in disease_name or 'sars-cov-2' in disease_name:
                disease_type = 'covid19'
            elif 'influenza' in disease_name or 'flu' in disease_name:
                disease_type = 'influenza'
            elif 'measles' in disease_name:
                disease_type = 'measles'
            elif 'tuberculosis' in disease_name or 'tb' in disease_name:
                disease_type = 'tuberculosis'
            
            # Extract dates
            onset_date = ehr_data.get('symptom_onset_date') or ehr_data.get('admission_date')
            report_date = ehr_data.get('report_date') or datetime.now().isoformat()
            
            # Create location
            location = {
                'latitude': ehr_data.get('location', {}).get('latitude', 0),
                'longitude': ehr_data.get('location', {}).get('longitude', 0)
            }
            
            # Map classification
            case_status = ehr_data.get('case_status', '').lower()
            classification = 'suspected'
            if 'confirmed' in case_status:
                classification = 'confirmed'
            elif 'probable' in case_status:
                classification = 'probable'
            
            # Extract demographics
            demographics = ehr_data.get('demographics', {})
            
            # Create case object
            case = HumanDiseaseCase(
                patient_id=patient_id,
                disease_type=disease_type,
                onset_date=onset_date,
                report_date=report_date,
                location=location,
                classification=classification,
                demographics=demographics,
                symptoms=ehr_data.get('symptoms', []),
                notes=ehr_data.get('notes'),
                source_system="healthcare_integration"
            )
            
            return case
            
        except Exception as e:
            logger.error(f"Error converting healthcare data to case: {str(e)}")
            return None
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock healthcare system data for demonstration"""
        mock_data = []
        
        for i in range(count):
            mock_data.append({
                'patient_id': f"EHR-{100000 + i}",
                'mrn': f"MRN-{200000 + i}",
                'diagnosis': 'COVID-19' if i % 3 == 0 else 'Influenza A',
                'symptom_onset_date': (datetime.now().replace(day=datetime.now().day - (i % 10))).isoformat(),
                'report_date': datetime.now().isoformat(),
                'location': {
                    'latitude': 38.8977 + (i * 0.01),
                    'longitude': -77.0365 - (i * 0.01)
                },
                'case_status': 'Confirmed' if i % 2 == 0 else 'Suspected',
                'demographics': {
                    'age': 30 + (i * 2),
                    'gender': 'Male' if i % 2 == 0 else 'Female',
                    'race': 'White' if i % 3 == 0 else 'Black' if i % 3 == 1 else 'Asian'
                },
                'symptoms': ['fever', 'cough', 'fatigue'] if i % 2 == 0 else ['fever', 'sore throat'],
                'notes': f"Mock EHR case record {i+1}"
            })
        
        return mock_data


class PublicHealthReportingAdapter(ExternalSystemAdapter):
    """
    Adapter for public health reporting system integration.
    
    Provides methods to fetch and send data to/from public health reporting systems,
    such as state health departments and national reporting systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration dictionary with connection details
        """
        self.config = config
        self.api_url = config.get('api_url')
        self.api_key = config.get('api_key')
        self.jurisdiction = config.get('jurisdiction', 'unknown')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = config.get('timeout', 30)
        
        logger.info(f"PublicHealthReportingAdapter initialized for {self.jurisdiction} at {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from public health reporting system.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of data records from the public health system
            
        Raises:
            ConnectionError: If connection to the public health system fails
        """
        try:
            # In a real implementation, this would make an API call to the public health system
            # For demonstration, we return mock data
            if not self.api_url:
                logger.warning("API URL not configured, returning mock data")
                return self._generate_mock_data(kwargs.get('count', 5))
            
            endpoint = kwargs.get('endpoint', 'reports')
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Fetching data from {url} with params: {kwargs}")
            
            # This is where an actual API call would happen
            # response = requests.get(url, headers=self.headers, params=kwargs, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, return mock data
            return self._generate_mock_data(kwargs.get('count', 5))
            
        except Exception as e:
            logger.error(f"Error fetching data from public health system: {str(e)}")
            raise ConnectionError(f"Failed to connect to public health system: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to public health reporting system.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the public health system
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send data: {json.dumps(data, default=str)}")
                return True
            
            endpoint = 'submit'
            url = f"{self.api_url}/{endpoint}"
            
            logger.info(f"Sending data to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send data: {json.dumps(data, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to public health system: {str(e)}")
            return False
    
    def format_case_for_reporting(self, case: HumanDiseaseCase) -> Dict[str, Any]:
        """
        Format a case for public health reporting.
        
        Args:
            case: The case to format
            
        Returns:
            Dictionary formatted for the public health reporting system
        """
        # Create a standardized report for public health authorities
        report = {
            'report_id': f"CDC-{case.id}",
            'report_date': datetime.now().isoformat(),
            'reporting_jurisdiction': self.jurisdiction,
            'reporting_agency': 'CDC',
            'case_data': {
                'patient_id': case.patient_id,
                'disease': case.disease_type.value if hasattr(case, 'disease_type') else 'unknown',
                'classification': case.classification.value if hasattr(case, 'classification') else 'unknown',
                'onset_date': case.onset_date.isoformat() if hasattr(case, 'onset_date') and not isinstance(case.onset_date, str) else case.onset_date,
                'report_date': case.report_date.isoformat() if hasattr(case, 'report_date') and not isinstance(case.report_date, str) else case.report_date,
                'outcome': case.outcome.value if hasattr(case, 'outcome') else 'unknown'
            },
            'location': {
                'latitude': case.location.latitude if hasattr(case, 'location') else None,
                'longitude': case.location.longitude if hasattr(case, 'location') else None,
                'jurisdiction': case.jurisdiction if hasattr(case, 'jurisdiction') else self.jurisdiction
            },
            'lab_results': case.laboratory_results if hasattr(case, 'laboratory_results') else [],
            'reportable_condition': hasattr(case, 'is_reportable') and case.is_reportable
        }
        
        # Add demographics if available (with privacy considerations)
        if hasattr(case, 'demographics') and case.demographics:
            report['demographics'] = {
                'age_group': case.demographics.get('age_group'),
                'gender': case.demographics.get('gender'),
                'race': case.demographics.get('race'),
                'ethnicity': case.demographics.get('ethnicity')
            }
        
        return report
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock public health reporting data for demonstration"""
        mock_data = []
        
        for i in range(count):
            mock_data.append({
                'report_id': f"PH-{300000 + i}",
                'patient_id': f"PH-PT-{400000 + i}",
                'disease': 'covid19' if i % 3 == 0 else 'influenza',
                'classification': 'confirmed' if i % 2 == 0 else 'probable',
                'onset_date': (datetime.now().replace(day=datetime.now().day - (i % 15))).isoformat(),
                'report_date': datetime.now().isoformat(),
                'jurisdiction': self.jurisdiction,
                'location': {
                    'latitude': 38.8977 + (i * 0.02),
                    'longitude': -77.0365 - (i * 0.02)
                },
                'demographics': {
                    'age_group': '18-49' if i % 3 == 0 else '50-64' if i % 3 == 1 else '65+',
                    'gender': 'Male' if i % 2 == 0 else 'Female',
                    'race': 'White' if i % 4 == 0 else 'Black' if i % 4 == 1 else 'Asian' if i % 4 == 2 else 'Other',
                    'ethnicity': 'Hispanic' if i % 3 == 0 else 'Non-Hispanic'
                },
                'lab_results': [
                    {
                        'test_type': 'PCR',
                        'result': 'positive' if i % 2 == 0 else 'negative',
                        'date': (datetime.now().replace(day=datetime.now().day - (i % 5))).isoformat()
                    }
                ],
                'reportable_condition': True
            })
        
        return mock_data