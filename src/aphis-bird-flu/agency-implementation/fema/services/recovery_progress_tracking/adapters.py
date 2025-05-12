"""
Adapters for the Recovery Progress Tracking service.
Integrates with external assessment systems and reporting services.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import requests
from abc import ABC, abstractmethod

from agency_implementation.fema.models.recovery import (
    RecoveryProject, DamageAssessment, RecoveryMetrics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssessmentSystemAdapter(ABC):
    """
    Base adapter for external damage assessment systems.
    Provides interface for fetching assessment data from external systems.
    """
    
    @abstractmethod
    def fetch_assessments(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch assessment data from the assessment system.
        
        Args:
            **params: Parameters for the assessment request
            
        Returns:
            List of assessment records
        """
        pass
    
    @abstractmethod
    def convert_to_assessment(self, record: Dict[str, Any]) -> Optional[DamageAssessment]:
        """
        Convert an assessment system record to a damage assessment.
        
        Args:
            record: Data record from the assessment system
            
        Returns:
            DamageAssessment instance or None if conversion fails
        """
        pass


class FEMAAssessmentAdapter(AssessmentSystemAdapter):
    """
    Adapter for FEMA's damage assessment system.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize FEMA assessment adapter.
        
        Args:
            api_url: URL for the assessment system API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.default_params = self.config.get('default_params', {})
        
        logger.info("Initialized FEMAAssessmentAdapter")
    
    def fetch_assessments(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch assessment data from the FEMA assessment system.
        
        Args:
            **params: Parameters for the assessment request
            
        Returns:
            List of assessment records
            
        Raises:
            RuntimeError: If API request fails
        """
        # Combine default params with provided params
        request_params = {**self.default_params, **params}
        
        # If API is not configured, return mock data for testing
        if not self.api_url:
            logger.warning("API URL not configured, returning mock data")
            return self._get_mock_data(**request_params)
        
        try:
            # Add API key to headers if available
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.get(
                self.api_url, 
                params=request_params, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                raise RuntimeError(f"Assessment API request failed with status {response.status_code}")
                
            # Parse response
            data = response.json()
            
            # Extract records from response (adjust based on actual API response structure)
            records = data.get('assessments', [])
            logger.info(f"Fetched {len(records)} assessment records")
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching assessment data: {str(e)}")
            raise RuntimeError(f"Failed to fetch assessment data: {str(e)}")
    
    def convert_to_assessment(self, record: Dict[str, Any]) -> Optional[DamageAssessment]:
        """
        Convert an assessment system record to a damage assessment.
        
        Args:
            record: Data record from the assessment system
            
        Returns:
            DamageAssessment instance or None if conversion fails
        """
        try:
            # Extract required fields from record (adjust based on actual data structure)
            required_fields = ['id', 'event_id', 'assessment_area', 'assessment_type', 'damage_level']
            for field in required_fields:
                if field not in record:
                    logger.warning(f"Missing required field '{field}' in record: {record}")
                    return None
            
            # Map record fields to assessment fields
            assessment_data = {
                'id': record['id'],
                'event_id': record['event_id'],
                'assessment_area': record['assessment_area'],
                'assessment_type': record['assessment_type'],
                'damage_level': record['damage_level']
            }
            
            # Add optional fields if present
            optional_fields = {
                'assessment_date': 'assessment_date',
                'completed_by': 'completed_by',
                'methodology': 'methodology',
                'infrastructure_damage': 'infrastructure_damage',
                'housing_damage': 'housing_damage',
                'economic_impact': 'economic_impact',
                'environmental_impact': 'environmental_impact',
                'affected_population': 'affected_population',
                'comments': 'comments',
                'confidence_level': 'confidence_level',
                'attachments': 'attachments',
                'status': 'status'
            }
            
            for src, dest in optional_fields.items():
                if src in record:
                    assessment_data[dest] = record[src]
            
            # Create assessment object
            assessment = DamageAssessment(**assessment_data)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error converting assessment record: {str(e)}")
            return None
    
    def _get_mock_data(self, **params) -> List[Dict[str, Any]]:
        """
        Generate mock assessment data for testing.
        
        Args:
            **params: Parameters to customize mock data
            
        Returns:
            List of mock assessment records
        """
        # Generate basic mock data
        event_id = params.get('event_id', 'evt-001')
        
        mock_data = [
            {
                'id': 'da-001',
                'event_id': event_id,
                'assessment_area': {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [-80.0, 25.0],
                                [-81.0, 25.0],
                                [-81.0, 26.0],
                                [-80.0, 26.0],
                                [-80.0, 25.0]
                            ]
                        ]
                    },
                    'properties': {
                        'name': 'County A'
                    }
                },
                'assessment_type': 'preliminary',
                'damage_level': 'moderate',
                'assessment_date': datetime.now().isoformat(),
                'completed_by': 'Field Team Alpha',
                'infrastructure_damage': {
                    'roads': 'moderate',
                    'bridges': 'minor',
                    'utilities': 'major',
                    'value': 2500000
                },
                'housing_damage': {
                    'destroyed': 12,
                    'major': 45,
                    'minor': 130,
                    'affected': 350,
                    'value': 5800000
                },
                'economic_impact': {
                    'business_disruption': 'moderate',
                    'job_losses': 85,
                    'value': 3700000
                },
                'affected_population': 1850,
                'status': 'DRAFT'
            },
            {
                'id': 'da-002',
                'event_id': event_id,
                'assessment_area': {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [-82.0, 26.0],
                                [-83.0, 26.0],
                                [-83.0, 27.0],
                                [-82.0, 27.0],
                                [-82.0, 26.0]
                            ]
                        ]
                    },
                    'properties': {
                        'name': 'County B'
                    }
                },
                'assessment_type': 'detailed',
                'damage_level': 'major',
                'assessment_date': datetime.now().isoformat(),
                'completed_by': 'Field Team Bravo',
                'infrastructure_damage': {
                    'roads': 'major',
                    'bridges': 'moderate',
                    'utilities': 'major',
                    'value': 7500000
                },
                'housing_damage': {
                    'destroyed': 85,
                    'major': 220,
                    'minor': 430,
                    'affected': 1200,
                    'value': 28500000
                },
                'economic_impact': {
                    'business_disruption': 'severe',
                    'job_losses': 350,
                    'value': 12800000
                },
                'affected_population': 5600,
                'status': 'FINAL'
            }
        ]
        
        # Filter based on parameters
        filtered_data = mock_data
        
        if 'assessment_type' in params:
            filtered_data = [r for r in filtered_data if r['assessment_type'] == params['assessment_type']]
            
        if 'damage_level' in params:
            filtered_data = [r for r in filtered_data if r['damage_level'] == params['damage_level']]
            
        if 'status' in params:
            filtered_data = [r for r in filtered_data if r['status'] == params['status']]
            
        return filtered_data


class ProjectTrackingAdapter(ABC):
    """
    Base adapter for external project tracking systems.
    Provides interface for tracking recovery projects.
    """
    
    @abstractmethod
    def fetch_projects(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch project data from the project tracking system.
        
        Args:
            **params: Parameters for the project request
            
        Returns:
            List of project records
        """
        pass
    
    @abstractmethod
    def convert_to_project(self, record: Dict[str, Any]) -> Optional[RecoveryProject]:
        """
        Convert a project tracking record to a recovery project.
        
        Args:
            record: Data record from the project tracking system
            
        Returns:
            RecoveryProject instance or None if conversion fails
        """
        pass
    
    @abstractmethod
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a project in the external tracking system.
        
        Args:
            project_id: ID of the project to update
            updates: Dictionary of updates to apply
            
        Returns:
            True if update was successful, False otherwise
        """
        pass


class FEMAProjectAdapter(ProjectTrackingAdapter):
    """
    Adapter for FEMA's project tracking system.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize FEMA project adapter.
        
        Args:
            api_url: URL for the project tracking API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        self.default_params = self.config.get('default_params', {})
        
        logger.info("Initialized FEMAProjectAdapter")
    
    def fetch_projects(self, **params) -> List[Dict[str, Any]]:
        """
        Fetch project data from the FEMA project tracking system.
        
        Args:
            **params: Parameters for the project request
            
        Returns:
            List of project records
            
        Raises:
            RuntimeError: If API request fails
        """
        # Combine default params with provided params
        request_params = {**self.default_params, **params}
        
        # If API is not configured, return mock data for testing
        if not self.api_url:
            logger.warning("API URL not configured, returning mock data")
            return self._get_mock_data(**request_params)
        
        try:
            # Add API key to headers if available
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.get(
                self.api_url, 
                params=request_params, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                raise RuntimeError(f"Project API request failed with status {response.status_code}")
                
            # Parse response
            data = response.json()
            
            # Extract records from response (adjust based on actual API response structure)
            records = data.get('projects', [])
            logger.info(f"Fetched {len(records)} project records")
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching project data: {str(e)}")
            raise RuntimeError(f"Failed to fetch project data: {str(e)}")
    
    def convert_to_project(self, record: Dict[str, Any]) -> Optional[RecoveryProject]:
        """
        Convert a project tracking record to a recovery project.
        
        Args:
            record: Data record from the project tracking system
            
        Returns:
            RecoveryProject instance or None if conversion fails
        """
        try:
            # Extract required fields from record (adjust based on actual data structure)
            required_fields = ['id', 'project_name', 'event_id', 'project_type', 'location']
            for field in required_fields:
                if field not in record:
                    logger.warning(f"Missing required field '{field}' in record: {record}")
                    return None
            
            # Map record fields to project fields
            project_data = {
                'id': record['id'],
                'project_name': record['project_name'],
                'event_id': record['event_id'],
                'project_type': record['project_type'],
                'location': record['location']
            }
            
            # Add optional fields if present
            optional_fields = {
                'description': 'description',
                'start_date': 'start_date',
                'target_completion_date': 'target_completion_date',
                'actual_completion_date': 'actual_completion_date',
                'status': 'status',
                'phase': 'phase',
                'allocated_budget': 'allocated_budget',
                'funds_disbursed': 'funds_disbursed',
                'responsible_agency': 'responsible_agency',
                'primary_contact': 'primary_contact',
                'beneficiaries': 'beneficiaries',
                'success_metrics': 'success_metrics',
                'progress_updates': 'progress_updates',
                'project_attachments': 'project_attachments'
            }
            
            for src, dest in optional_fields.items():
                if src in record:
                    project_data[dest] = record[src]
            
            # Create project object
            project = RecoveryProject(**project_data)
            
            return project
            
        except Exception as e:
            logger.error(f"Error converting project record: {str(e)}")
            return None
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a project in the external tracking system.
        
        Args:
            project_id: ID of the project to update
            updates: Dictionary of updates to apply
            
        Returns:
            True if update was successful, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info(f"Would update project {project_id} in external system")
            return True
        
        try:
            # Prepare update data
            update_data = {
                'id': project_id,
                **updates
            }
                
            # Add API key to headers if available
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.put(
                f"{self.api_url}/{project_id}", 
                json=update_data, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code not in (200, 201, 204):
                logger.error(f"API update failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"Updated project {project_id} in external system")
            return True
            
        except Exception as e:
            logger.error(f"Error updating project in external system: {str(e)}")
            return False
    
    def _get_mock_data(self, **params) -> List[Dict[str, Any]]:
        """
        Generate mock project data for testing.
        
        Args:
            **params: Parameters to customize mock data
            
        Returns:
            List of mock project records
        """
        # Generate basic mock data
        event_id = params.get('event_id', 'evt-001')
        
        mock_data = [
            {
                'id': 'proj-001',
                'project_name': 'Infrastructure Repair - Highway 101',
                'event_id': event_id,
                'project_type': 'infrastructure',
                'location': {
                    'latitude': 35.6895,
                    'longitude': -120.1245
                },
                'description': 'Repair and reconstruction of damaged sections of Highway 101',
                'start_date': '2025-04-15T00:00:00Z',
                'target_completion_date': '2025-09-30T00:00:00Z',
                'status': 'IN_PROGRESS',
                'phase': 'short_term_recovery',
                'allocated_budget': 4500000.00,
                'funds_disbursed': 1250000.00,
                'responsible_agency': 'DOT',
                'primary_contact': {
                    'name': 'John Smith',
                    'email': 'john.smith@dot.gov',
                    'phone': '202-555-1234'
                },
                'beneficiaries': 25000,
                'progress_updates': [
                    {
                        'type': 'STATUS_UPDATE',
                        'timestamp': '2025-04-20T14:30:00Z',
                        'percent_complete': 10,
                        'notes': 'Initial assessment and planning completed.'
                    },
                    {
                        'type': 'STATUS_UPDATE',
                        'timestamp': '2025-05-10T16:15:00Z',
                        'percent_complete': 25,
                        'notes': 'Debris removal completed, reconstruction begun on sections 1-3.'
                    }
                ]
            },
            {
                'id': 'proj-002',
                'project_name': 'Temporary Housing - County B',
                'event_id': event_id,
                'project_type': 'housing',
                'location': {
                    'latitude': 35.4528,
                    'longitude': -120.6544
                },
                'description': 'Establish temporary housing units for displaced residents',
                'start_date': '2025-04-10T00:00:00Z',
                'target_completion_date': '2025-06-15T00:00:00Z',
                'status': 'IN_PROGRESS',
                'phase': 'short_term_recovery',
                'allocated_budget': 3200000.00,
                'funds_disbursed': 2100000.00,
                'responsible_agency': 'HUD',
                'primary_contact': {
                    'name': 'Sarah Johnson',
                    'email': 'sarah.johnson@hud.gov',
                    'phone': '202-555-5678'
                },
                'beneficiaries': 450,
                'progress_updates': [
                    {
                        'type': 'STATUS_UPDATE',
                        'timestamp': '2025-04-15T09:45:00Z',
                        'percent_complete': 15,
                        'notes': 'Site preparation completed.'
                    },
                    {
                        'type': 'STATUS_UPDATE',
                        'timestamp': '2025-05-01T11:30:00Z',
                        'percent_complete': 40,
                        'notes': '120 temporary housing units installed and ready for occupancy.'
                    },
                    {
                        'type': 'STATUS_UPDATE',
                        'timestamp': '2025-05-15T14:00:00Z',
                        'percent_complete': 65,
                        'notes': '210 units installed, utilities connected for all completed units.'
                    }
                ]
            }
        ]
        
        # Filter based on parameters
        filtered_data = mock_data
        
        if 'project_type' in params:
            filtered_data = [r for r in filtered_data if r['project_type'] == params['project_type']]
            
        if 'status' in params:
            filtered_data = [r for r in filtered_data if r['status'] == params['status']]
            
        if 'phase' in params:
            filtered_data = [r for r in filtered_data if r['phase'] == params['phase']]
            
        return filtered_data


class ReportingServiceAdapter(ABC):
    """
    Base adapter for external reporting services.
    Provides interface for generating and submitting reports.
    """
    
    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a recovery report.
        
        Args:
            report_type: Type of report to generate
            data: Data for the report
            
        Returns:
            Generated report data
        """
        pass
    
    @abstractmethod
    def submit_report(self, report: Dict[str, Any]) -> bool:
        """
        Submit a report to the reporting service.
        
        Args:
            report: Report data to submit
            
        Returns:
            True if submission was successful, False otherwise
        """
        pass


class FEMAReportingAdapter(ReportingServiceAdapter):
    """
    Adapter for FEMA's reporting service.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None, config: Dict[str, Any] = None):
        """
        Initialize FEMA reporting adapter.
        
        Args:
            api_url: URL for the reporting service API
            api_key: API key for authentication
            config: Additional configuration
        """
        self.api_url = api_url
        self.api_key = api_key
        self.config = config or {}
        
        logger.info("Initialized FEMAReportingAdapter")
    
    def generate_report(self, report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a recovery report.
        
        Args:
            report_type: Type of report to generate
            data: Data for the report
            
        Returns:
            Generated report data
            
        Raises:
            ValueError: If report type is invalid
        """
        # Validate report type
        valid_report_types = ['progress', 'financial', 'impact', 'summary']
        if report_type not in valid_report_types:
            raise ValueError(f"Invalid report type: {report_type}. Valid types: {', '.join(valid_report_types)}")
        
        # Generate report
        report = {
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'data': data
        }
        
        # If API is configured, try to generate using the service
        if self.api_url:
            try:
                # Add API key to headers if available
                headers = {'Content-Type': 'application/json'}
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                    
                # Make API request
                response = requests.post(
                    f"{self.api_url}/generate",
                    json={
                        'report_type': report_type,
                        'data': data
                    },
                    headers=headers,
                    timeout=60  # Longer timeout for report generation
                )
                
                if response.status_code == 200:
                    # Use service-generated report
                    return response.json()
                else:
                    logger.warning(f"API report generation failed: {response.status_code}. Using local fallback.")
            except Exception as e:
                logger.warning(f"Error in API report generation: {str(e)}. Using local fallback.")
        
        # Add report-specific fields based on type
        if report_type == 'progress':
            report['metrics'] = self._calculate_progress_metrics(data)
            report['charts'] = self._generate_progress_charts(data)
            
        elif report_type == 'financial':
            report['metrics'] = self._calculate_financial_metrics(data)
            report['charts'] = self._generate_financial_charts(data)
            
        elif report_type == 'impact':
            report['metrics'] = self._calculate_impact_metrics(data)
            report['charts'] = self._generate_impact_charts(data)
            
        elif report_type == 'summary':
            report['metrics'] = self._calculate_summary_metrics(data)
            report['charts'] = self._generate_summary_charts(data)
            
        logger.info(f"Generated {report_type} report")
        return report
    
    def submit_report(self, report: Dict[str, Any]) -> bool:
        """
        Submit a report to the reporting service.
        
        Args:
            report: Report data to submit
            
        Returns:
            True if submission was successful, False otherwise
        """
        # If API is not configured, log and return mock success
        if not self.api_url:
            logger.info("Would submit report to external system")
            return True
        
        try:
            # Add API key to headers if available
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
            # Make API request
            response = requests.post(
                f"{self.api_url}/submit",
                json=report,
                headers=headers,
                timeout=30
            )
            
            if response.status_code not in (200, 201, 204):
                logger.error(f"API submission failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return False
                
            logger.info(f"Submitted {report.get('report_type', 'unknown')} report to external system")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting report to external system: {str(e)}")
            return False
    
    def _calculate_progress_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for progress report"""
        metrics = {
            'total_projects': 0,
            'completed_projects': 0,
            'in_progress_projects': 0,
            'not_started_projects': 0,
            'average_completion': 0.0,
            'on_schedule_percentage': 0.0,
            'projects_by_phase': {}
        }
        
        projects = data.get('projects', [])
        if not projects:
            return metrics
            
        # Calculate basic counts
        metrics['total_projects'] = len(projects)
        
        completion_values = []
        on_schedule = 0
        phase_counts = {}
        
        for project in projects:
            # Count by status
            status = project.get('status', 'UNKNOWN')
            if status == 'COMPLETED':
                metrics['completed_projects'] += 1
                completion_values.append(100.0)
            elif status in ['IN_PROGRESS', 'PLANNING', 'FUNDED']:
                metrics['in_progress_projects'] += 1
                completion_values.append(project.get('percent_complete', 0.0))
            else:
                metrics['not_started_projects'] += 1
                completion_values.append(0.0)
                
            # Count on-schedule projects
            target_date = project.get('target_completion_date')
            if target_date and datetime.now().isoformat() <= target_date:
                on_schedule += 1
                
            # Count by phase
            phase = project.get('phase', 'unknown')
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Calculate averages and percentages
        if completion_values:
            metrics['average_completion'] = sum(completion_values) / len(completion_values)
            
        if metrics['total_projects'] > 0:
            metrics['on_schedule_percentage'] = (on_schedule / metrics['total_projects']) * 100
            
        metrics['projects_by_phase'] = phase_counts
        
        return metrics
    
    def _generate_progress_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts for progress report"""
        # This would normally generate chart configurations
        # For this example, just return placeholders
        return [
            {
                'type': 'pie',
                'title': 'Projects by Status',
                'data_key': 'status_distribution'
            },
            {
                'type': 'bar',
                'title': 'Projects by Phase',
                'data_key': 'phase_distribution'
            },
            {
                'type': 'line',
                'title': 'Completion Progress Over Time',
                'data_key': 'completion_trend'
            }
        ]
    
    def _calculate_financial_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for financial report"""
        metrics = {
            'total_budget': 0.0,
            'total_disbursed': 0.0,
            'disbursement_rate': 0.0,
            'remaining_funds': 0.0,
            'budget_by_project_type': {}
        }
        
        projects = data.get('projects', [])
        if not projects:
            return metrics
            
        # Calculate financial totals
        type_budgets = {}
        
        for project in projects:
            budget = project.get('allocated_budget', 0.0)
            disbursed = project.get('funds_disbursed', 0.0)
            
            metrics['total_budget'] += budget
            metrics['total_disbursed'] += disbursed
            
            # Aggregate by project type
            project_type = project.get('project_type', 'unknown')
            if project_type not in type_budgets:
                type_budgets[project_type] = {'budget': 0.0, 'disbursed': 0.0}
                
            type_budgets[project_type]['budget'] += budget
            type_budgets[project_type]['disbursed'] += disbursed
        
        # Calculate derived metrics
        if metrics['total_budget'] > 0:
            metrics['disbursement_rate'] = (metrics['total_disbursed'] / metrics['total_budget']) * 100
            
        metrics['remaining_funds'] = metrics['total_budget'] - metrics['total_disbursed']
        
        # Format project type budgets
        for project_type, amounts in type_budgets.items():
            metrics['budget_by_project_type'][project_type] = {
                'budget': amounts['budget'],
                'disbursed': amounts['disbursed'],
                'remaining': amounts['budget'] - amounts['disbursed'],
                'disbursement_rate': (amounts['disbursed'] / amounts['budget']) * 100 if amounts['budget'] > 0 else 0
            }
            
        return metrics
    
    def _generate_financial_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts for financial report"""
        # This would normally generate chart configurations
        # For this example, just return placeholders
        return [
            {
                'type': 'pie',
                'title': 'Budget Allocation by Project Type',
                'data_key': 'budget_allocation'
            },
            {
                'type': 'bar',
                'title': 'Budget vs. Disbursed by Project Type',
                'data_key': 'budget_disbursed'
            },
            {
                'type': 'line',
                'title': 'Disbursement Rate Over Time',
                'data_key': 'disbursement_trend'
            }
        ]
    
    def _calculate_impact_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for impact report"""
        metrics = {
            'total_beneficiaries': 0,
            'economic_impact': 0.0,
            'affected_area': 0.0,
            'damage_by_type': {},
            'recovery_by_sector': {}
        }
        
        # Extract data
        projects = data.get('projects', [])
        assessments = data.get('assessments', [])
        
        # Calculate beneficiaries from projects
        for project in projects:
            metrics['total_beneficiaries'] += project.get('beneficiaries', 0)
            
        # Extract damage information from assessments
        for assessment in assessments:
            # Sum economic impact
            economic_impact = assessment.get('economic_impact', {})
            if isinstance(economic_impact, dict) and 'value' in economic_impact:
                metrics['economic_impact'] += economic_impact['value']
                
            # Extract damage by type
            for damage_type in ['infrastructure_damage', 'housing_damage', 'environmental_impact']:
                if damage_type in assessment:
                    damage_data = assessment[damage_type]
                    if isinstance(damage_data, dict) and 'value' in damage_data:
                        metrics['damage_by_type'][damage_type] = metrics['damage_by_type'].get(damage_type, 0) + damage_data['value']
        
        # Calculate recovery by sector from projects
        for project in projects:
            project_type = project.get('project_type', 'unknown')
            budget = project.get('allocated_budget', 0.0)
            percent_complete = project.get('percent_complete', 0)
            
            if project_type not in metrics['recovery_by_sector']:
                metrics['recovery_by_sector'][project_type] = {
                    'budget': 0.0,
                    'weighted_completion': 0.0,
                    'project_count': 0
                }
                
            metrics['recovery_by_sector'][project_type]['budget'] += budget
            metrics['recovery_by_sector'][project_type]['weighted_completion'] += percent_complete * budget
            metrics['recovery_by_sector'][project_type]['project_count'] += 1
            
        # Calculate weighted completion percentages
        for sector, data in metrics['recovery_by_sector'].items():
            if data['budget'] > 0:
                data['completion_percentage'] = data['weighted_completion'] / data['budget']
            else:
                data['completion_percentage'] = 0
                
            # Remove intermediate calculation
            del data['weighted_completion']
            
        return metrics
    
    def _generate_impact_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts for impact report"""
        # This would normally generate chart configurations
        # For this example, just return placeholders
        return [
            {
                'type': 'pie',
                'title': 'Damage by Type',
                'data_key': 'damage_distribution'
            },
            {
                'type': 'bar',
                'title': 'Recovery Progress by Sector',
                'data_key': 'sector_recovery'
            },
            {
                'type': 'geo',
                'title': 'Geographic Impact Distribution',
                'data_key': 'geographic_impact'
            }
        ]
    
    def _calculate_summary_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for summary report"""
        # Combine metrics from other report types
        progress_metrics = self._calculate_progress_metrics(data)
        financial_metrics = self._calculate_financial_metrics(data)
        impact_metrics = self._calculate_impact_metrics(data)
        
        summary_metrics = {
            'total_projects': progress_metrics['total_projects'],
            'completed_projects': progress_metrics['completed_projects'],
            'completion_percentage': progress_metrics['average_completion'],
            'total_budget': financial_metrics['total_budget'],
            'total_disbursed': financial_metrics['total_disbursed'],
            'disbursement_rate': financial_metrics['disbursement_rate'],
            'total_beneficiaries': impact_metrics['total_beneficiaries'],
            'economic_impact': impact_metrics['economic_impact'],
            'top_metrics_by_project_type': {}
        }
        
        # Get top metrics by project type
        project_types = set()
        for project in data.get('projects', []):
            project_types.add(project.get('project_type', 'unknown'))
            
        for project_type in project_types:
            projects = [p for p in data.get('projects', []) if p.get('project_type') == project_type]
            if not projects:
                continue
                
            # Calculate type-specific metrics
            type_budget = sum(p.get('allocated_budget', 0) for p in projects)
            type_disbursed = sum(p.get('funds_disbursed', 0) for p in projects)
            type_complete = sum(1 for p in projects if p.get('status') == 'COMPLETED')
            type_beneficiaries = sum(p.get('beneficiaries', 0) for p in projects)
            
            summary_metrics['top_metrics_by_project_type'][project_type] = {
                'project_count': len(projects),
                'completed_count': type_complete,
                'completion_rate': (type_complete / len(projects)) * 100 if projects else 0,
                'budget': type_budget,
                'disbursed': type_disbursed,
                'disbursement_rate': (type_disbursed / type_budget) * 100 if type_budget > 0 else 0,
                'beneficiaries': type_beneficiaries
            }
            
        return summary_metrics
    
    def _generate_summary_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts for summary report"""
        # This would normally generate chart configurations
        # For this example, just return combined charts
        return [
            {
                'type': 'dashboard',
                'title': 'Recovery Dashboard',
                'data_key': 'recovery_dashboard'
            },
            {
                'type': 'bar',
                'title': 'Project Completion by Type',
                'data_key': 'completion_by_type'
            },
            {
                'type': 'pie',
                'title': 'Budget Allocation',
                'data_key': 'budget_allocation'
            },
            {
                'type': 'line',
                'title': 'Recovery Progress Over Time',
                'data_key': 'recovery_trend'
            }
        ]