"""
Adapters for integrating with external facility registry and compliance reporting systems.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import requests
from abc import ABC, abstractmethod

from agency_implementation.epa.models.compliance import (
    RegulatedFacility, Permit, ComplianceInspection, 
    EnforcementAction, ComplianceReport
)
from agency_implementation.foundation.base_models.base import GeoLocation, Address, ContactInfo

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


class FacilityRegistryAdapter(ExternalSystemAdapter):
    """
    Adapter for facility registry integration.
    
    Provides methods to fetch and send data to/from external facility registry systems,
    such as the EPA's Facility Registry Service (FRS).
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
        self.default_params = config.get('default_params', {})
        
        logger.info(f"FacilityRegistryAdapter initialized for {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from facility registry.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of data records from the facility registry
            
        Raises:
            ConnectionError: If connection to the facility registry fails
        """
        try:
            # In a real implementation, this would make an API call to the facility registry
            # For demonstration, we return mock data
            if not self.api_url:
                logger.warning("API URL not configured, returning mock data")
                return self._generate_mock_data(kwargs.get('count', 5))
            
            endpoint = kwargs.get('endpoint', 'facilities')
            url = f"{self.api_url}/{endpoint}"
            
            # Combine default params with provided kwargs
            params = {**self.default_params, **kwargs}
            if 'endpoint' in params:
                del params['endpoint']
                
            logger.info(f"Fetching data from {url} with params: {params}")
            
            # This is where an actual API call would happen
            # response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            # response.raise_for_status()
            # return response.json()
            
            # For demonstration, return mock data
            return self._generate_mock_data(kwargs.get('count', 5))
            
        except Exception as e:
            logger.error(f"Error fetching data from facility registry: {str(e)}")
            raise ConnectionError(f"Failed to connect to facility registry: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to facility registry.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the facility registry
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send data: {json.dumps(data, default=str)}")
                return True
            
            endpoint = data.get('endpoint', 'upload')
            url = f"{self.api_url}/{endpoint}"
            
            if 'endpoint' in data:
                data_to_send = {k: v for k, v in data.items() if k != 'endpoint'}
            else:
                data_to_send = data
                
            logger.info(f"Sending data to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data_to_send, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send data: {json.dumps(data_to_send, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to facility registry: {str(e)}")
            return False
    
    def convert_to_facility(self, data: Dict[str, Any]) -> Optional[RegulatedFacility]:
        """
        Convert external facility registry data to a RegulatedFacility object.
        
        Args:
            data: Data from facility registry
            
        Returns:
            Converted RegulatedFacility object or None if conversion fails
        """
        try:
            # Extract required fields
            facility_name = data.get('facility_name') or data.get('name')
            if not facility_name:
                logger.error("Missing facility name in registry data")
                return None
            
            facility_type = data.get('facility_type') or data.get('type')
            if not facility_type:
                logger.error("Missing facility type in registry data")
                return None
            
            location_data = data.get('location') or data.get('coordinates')
            if not location_data:
                logger.error("Missing location in registry data")
                return None
            
            # Extract additional fields
            registry_id = data.get('registry_id') or data.get('id')
            address_data = data.get('address')
            contact_data = data.get('contact_info') or data.get('contact')
            epa_region = data.get('epa_region') or data.get('region')
            naics_code = data.get('naics_code') or data.get('naics')
            permit_ids = data.get('permit_ids') or data.get('permits') or []
            operating_status = data.get('operating_status') or data.get('status') or "ACTIVE"
            first_operational_date = data.get('first_operational_date') or data.get('start_date')
            regulatory_programs = data.get('regulatory_programs') or data.get('programs') or []
            
            # Create location object
            location = None
            if location_data:
                lat = location_data.get('latitude') or location_data.get('lat')
                lon = location_data.get('longitude') or location_data.get('lon')
                if lat is not None and lon is not None:
                    location = GeoLocation(latitude=lat, longitude=lon)
            
            # Create address object
            address = None
            if address_data:
                street = address_data.get('street') or address_data.get('address_line1')
                city = address_data.get('city')
                state = address_data.get('state')
                zip_code = address_data.get('zip_code') or address_data.get('postal_code')
                country = address_data.get('country', 'USA')
                address_line2 = address_data.get('address_line2')
                
                if street and city and state and zip_code:
                    address = Address(
                        street=street,
                        city=city,
                        state=state,
                        zip_code=zip_code,
                        country=country,
                        address_line2=address_line2
                    )
            
            # Create contact info object
            contact_info = None
            if contact_data:
                name = contact_data.get('name')
                email = contact_data.get('email')
                phone = contact_data.get('phone')
                position = contact_data.get('position') or contact_data.get('title')
                organization = contact_data.get('organization')
                
                if name:
                    contact_info = ContactInfo(
                        name=name,
                        email=email,
                        phone=phone,
                        position=position,
                        organization=organization
                    )
            
            # Create facility object
            facility = RegulatedFacility(
                facility_name=facility_name,
                facility_type=facility_type,
                location=location,
                address=address,
                contact_info=contact_info,
                epa_region=epa_region,
                naics_code=naics_code,
                permit_ids=permit_ids,
                operating_status=operating_status,
                first_operational_date=first_operational_date,
                regulatory_programs=regulatory_programs,
                registry_id=registry_id
            )
            
            return facility
            
        except Exception as e:
            logger.error(f"Error converting registry data to facility: {str(e)}")
            return None
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock facility registry data for demonstration"""
        from random import choice, randint, random
        
        mock_data = []
        
        # Sample facility types
        facility_types = [
            "Chemical Manufacturing", 
            "Power Generation", 
            "Waste Management", 
            "Metal Production", 
            "Oil and Gas Extraction",
            "Paper Manufacturing",
            "Food Processing"
        ]
        
        # Sample EPA regions
        epa_regions = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        
        # Sample regulatory programs
        regulatory_programs = [
            "NPDES", "CAA", "RCRA", "CERCLA", "FIFRA", "TSCA", "SDWA"
        ]
        
        # Sample states
        states = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]
        
        # Sample operating statuses
        operating_statuses = ["ACTIVE", "INACTIVE", "TEMPORARILY_CLOSED", "PLANNED"]
        
        # Sample city names
        cities = [
            "Springfield", "Riverdale", "Franklin", "Clinton", "Salem", 
            "Georgetown", "Fairview", "Greenville", "Bristol", "Madison",
            "Oxford", "Washington", "Arlington", "Burlington", "Manchester"
        ]
        
        # Generate mock data
        for i in range(count):
            facility_type = choice(facility_types)
            state = choice(states)
            city = choice(cities)
            
            # Generate a realistic name
            company_types = ["LLC", "Inc.", "Corp.", "Company", "Industries"]
            industry_words = ["Chemical", "Environmental", "Processing", "Manufacturing", "Industrial", "Energy", "Waste"]
            company_name = f"{choice(industry_words)} {choice(industry_words + [''])}".strip()
            company_type = choice(company_types)
            facility_name = f"{company_name} {company_type}"
            
            # Generate between 1 and 3 random regulatory programs
            selected_programs = []
            for _ in range(randint(1, 3)):
                program = choice(regulatory_programs)
                if program not in selected_programs:
                    selected_programs.append(program)
            
            # Generate random coordinates
            lat = 35.0 + (random() * 10)
            lon = -90.0 - (random() * 20)
            
            # Generate data
            data = {
                "registry_id": f"FRS{1000000 + i}",
                "facility_name": facility_name,
                "facility_type": facility_type,
                "location": {
                    "latitude": lat,
                    "longitude": lon
                },
                "address": {
                    "street": f"{randint(100, 9999)} {choice(['Main', 'Oak', 'Maple', 'Industrial', 'Commerce'])} {choice(['St', 'Ave', 'Blvd', 'Rd', 'Pkwy'])}",
                    "city": city,
                    "state": state,
                    "zip_code": f"{randint(10000, 99999)}",
                    "country": "USA"
                },
                "contact_info": {
                    "name": f"{choice(['John', 'Jane', 'Michael', 'Robert', 'Mary', 'David', 'Lisa'])} {choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller'])}",
                    "email": f"contact{i}@{company_name.lower().replace(' ', '')}.com",
                    "phone": f"({randint(100, 999)})-{randint(100, 999)}-{randint(1000, 9999)}",
                    "position": choice(["Environmental Manager", "Facility Manager", "Compliance Officer", "Plant Manager", "Director of Operations"]),
                    "organization": facility_name
                },
                "epa_region": choice(epa_regions),
                "naics_code": f"{randint(311, 339)}{randint(100, 999)}",
                "permit_ids": [f"PERMIT-{facility_type[:3].upper()}-{randint(10000, 99999)}" for _ in range(randint(1, 3))],
                "operating_status": choice(operating_statuses),
                "first_operational_date": f"{randint(1950, 2020)}-{randint(1, 12):02d}-{randint(1, 28):02d}",
                "regulatory_programs": selected_programs
            }
            
            mock_data.append(data)
        
        return mock_data


class ComplianceReportingAdapter(ExternalSystemAdapter):
    """
    Adapter for compliance reporting system integration.
    
    Provides methods to fetch and send data to/from external compliance reporting systems,
    such as state and federal environmental databases.
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
        self.reporting_authority = config.get('reporting_authority', 'EPA')
        
        logger.info(f"ComplianceReportingAdapter initialized for {self.api_url}")
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from compliance reporting system.
        
        Args:
            **kwargs: Query parameters for the request
            
        Returns:
            List of data records from the compliance reporting system
            
        Raises:
            ConnectionError: If connection to the compliance reporting system fails
        """
        try:
            # In a real implementation, this would make an API call to the compliance reporting system
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
            logger.error(f"Error fetching data from compliance reporting system: {str(e)}")
            raise ConnectionError(f"Failed to connect to compliance reporting system: {str(e)}")
    
    def send_data(self, data: Any) -> bool:
        """
        Send data to compliance reporting system.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would make an API call to the compliance reporting system
            # For demonstration, we just log the data
            if not self.api_url:
                logger.warning("API URL not configured, simulating successful send")
                logger.debug(f"Would send compliance report: {json.dumps(data, default=str)}")
                return True
            
            endpoint = data.get('endpoint', 'submit')
            url = f"{self.api_url}/{endpoint}"
            
            if 'endpoint' in data:
                data_to_send = {k: v for k, v in data.items() if k != 'endpoint'}
            else:
                data_to_send = data
                
            logger.info(f"Sending data to {url}")
            
            # This is where an actual API call would happen
            # response = requests.post(url, headers=self.headers, json=data_to_send, timeout=self.timeout)
            # response.raise_for_status()
            # return True
            
            # For demonstration, return success
            logger.debug(f"Would send compliance report: {json.dumps(data_to_send, default=str)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to compliance reporting system: {str(e)}")
            return False
    
    def convert_to_compliance_report(self, data: Dict[str, Any]) -> Optional[ComplianceReport]:
        """
        Convert external compliance reporting system data to a ComplianceReport object.
        
        Args:
            data: Data from compliance reporting system
            
        Returns:
            Converted ComplianceReport object or None if conversion fails
        """
        try:
            # Extract required fields
            facility_id = data.get('facility_id') or data.get('facility_registry_id')
            if not facility_id:
                logger.error("Missing facility ID in compliance report data")
                return None
            
            report_type = data.get('report_type')
            if not report_type:
                logger.error("Missing report type in compliance report data")
                return None
            
            reporting_period_start = data.get('reporting_period_start') or data.get('period_start')
            if not reporting_period_start:
                logger.error("Missing reporting period start in compliance report data")
                return None
            
            reporting_period_end = data.get('reporting_period_end') or data.get('period_end')
            if not reporting_period_end:
                logger.error("Missing reporting period end in compliance report data")
                return None
            
            submission_date = data.get('submission_date') or data.get('submitted_at') or datetime.now().isoformat()
            
            # Extract additional fields
            permit_id = data.get('permit_id') or data.get('permit_number')
            report_status = data.get('report_status') or data.get('status') or "SUBMITTED"
            reported_data = data.get('reported_data') or data.get('data') or {}
            exceedances = data.get('exceedances') or data.get('exceedance_reports') or []
            certification = data.get('certification') or data.get('certifier_info') or {}
            reviewer_id = data.get('reviewer_id')
            review_date = data.get('review_date')
            review_comments = data.get('review_comments')
            
            # Create compliance report object
            report = ComplianceReport(
                facility_id=facility_id,
                report_type=report_type,
                reporting_period_start=reporting_period_start,
                reporting_period_end=reporting_period_end,
                submission_date=submission_date,
                permit_id=permit_id,
                report_status=report_status,
                reported_data=reported_data,
                exceedances=exceedances,
                certification=certification,
                reviewer_id=reviewer_id,
                review_date=review_date,
                review_comments=review_comments
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error converting compliance report data: {str(e)}")
            return None
    
    def _generate_mock_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock compliance reporting system data for demonstration"""
        from random import choice, randint, random, sample
        
        mock_data = []
        
        # Sample report types
        report_types = [
            "Monthly Discharge Monitoring Report", 
            "Annual Emissions Inventory", 
            "Hazardous Waste Biennial Report", 
            "TRI Report", 
            "NPDES Compliance Report"
        ]
        
        # Sample parameters
        parameters = [
            "TSS", "BOD", "pH", "Ammonia", "Copper", "Lead", "Mercury", 
            "NOx", "SO2", "PM", "VOCs", "CO", "HAPs"
        ]
        
        # Sample statuses
        statuses = ["SUBMITTED", "UNDER_REVIEW", "ACCEPTED", "REJECTED", "REQUIRES_REVISION"]
        
        # Generate mock data
        for i in range(count):
            # Generate a reporting period
            year = randint(2020, 2023)
            quarter = randint(1, 4)
            month_start = (quarter - 1) * 3 + 1
            month_end = month_start + 2
            
            if month_end > 12:
                month_end = 12
                
            period_start = f"{year}-{month_start:02d}-01"
            period_end = f"{year}-{month_end:02d}-{randint(28, 30)}"
            
            # Generate submission date after period end
            submission_month = month_end + randint(0, 1)
            submission_year = year
            
            if submission_month > 12:
                submission_month -= 12
                submission_year += 1
                
            submission_date = f"{submission_year}-{submission_month:02d}-{randint(1, 28):02d}"
            
            # Generate reported data with random parameters
            reported_data = {}
            
            # Select 3-5 random parameters
            selected_parameters = sample(parameters, randint(3, 5))
            
            for param in selected_parameters:
                # Generate a random value and limit
                limit = 100 * random()
                value = limit * (0.5 + random())
                
                reported_data[param] = {
                    "value": value,
                    "limit": limit,
                    "unit": choice(["mg/L", "μg/L", "tons/year", "lbs/day"]),
                    "exceedance": value > limit
                }
            
            # Generate exceedances if any
            exceedances = []
            
            for param, data in reported_data.items():
                if data["exceedance"]:
                    exceedance = {
                        "parameter": param,
                        "value": data["value"],
                        "limit": data["limit"],
                        "unit": data["unit"],
                        "exceedance_percentage": ((data["value"] - data["limit"]) / data["limit"]) * 100,
                        "explanation": choice([
                            "Equipment malfunction",
                            "Unusual operating conditions",
                            "Extreme weather event",
                            "Unexpected process upset",
                            "Instrument calibration error"
                        ]),
                        "corrective_action": choice([
                            "Equipment repair",
                            "Process adjustment",
                            "Staff training",
                            "Increased monitoring frequency",
                            "System upgrade"
                        ])
                    }
                    
                    exceedances.append(exceedance)
            
            # Generate certification info
            certification = {
                "certifier_name": f"{choice(['John', 'Jane', 'Michael', 'Robert', 'Mary', 'David', 'Lisa'])} {choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller'])}",
                "certifier_title": choice(["Environmental Manager", "Facility Manager", "Plant Manager", "Director of Operations", "VP of Environmental Affairs"]),
                "certification_date": submission_date,
                "certification_statement": "I certify under penalty of law that this document and all attachments were prepared under my direction or supervision in accordance with a system designed to assure that qualified personnel properly gather and evaluate the information submitted."
            }
            
            # Generate a review if not submitted
            review_status = choice(statuses)
            reviewer_id = None
            review_date = None
            review_comments = None
            
            if review_status in ["ACCEPTED", "REJECTED", "REQUIRES_REVISION"]:
                reviewer_id = f"REVIEWER-{randint(1000, 9999)}"
                
                # Review date after submission
                review_month = submission_month + randint(0, 1)
                review_year = submission_year
                
                if review_month > 12:
                    review_month -= 12
                    review_year += 1
                    
                review_date = f"{review_year}-{review_month:02d}-{randint(1, 28):02d}"
                
                if review_status == "ACCEPTED":
                    review_comments = "Report meets all requirements."
                elif review_status == "REJECTED":
                    review_comments = choice([
                        "Missing required data for key parameters.",
                        "Certification information incomplete.",
                        "Reported data inconsistent with previous reports.",
                        "Exceedance explanations inadequate."
                    ])
                elif review_status == "REQUIRES_REVISION":
                    review_comments = choice([
                        "Please provide additional information about exceedances.",
                        "Corrective action details insufficient.",
                        "Inconsistent units used for parameters.",
                        "Clarify sampling methodology."
                    ])
            
            data = {
                "facility_id": f"FACILITY-{1000 + i % 3}",
                "report_type": choice(report_types),
                "reporting_period_start": period_start,
                "reporting_period_end": period_end,
                "submission_date": submission_date,
                "permit_id": f"PERMIT-{2000 + i % 5}",
                "report_status": review_status,
                "reported_data": reported_data,
                "exceedances": exceedances,
                "certification": certification,
                "reviewer_id": reviewer_id,
                "review_date": review_date,
                "review_comments": review_comments
            }
            
            mock_data.append(data)
        
        return mock_data