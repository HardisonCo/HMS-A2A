"""
Recovery Progress Tracking Service for the FEMA implementation.

This service provides functionality for tracking disaster recovery progress,
including project management, damage assessment, and recovery metrics.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import logging
import uuid
import json
import os

from agency_implementation.fema.models.recovery import (
    RecoveryProject, DamageAssessment, RecoveryMetrics, RecoveryProgram
)
from agency_implementation.fema.models.base import RecoveryPhase
from .repository import (
    RecoveryProjectRepository, DamageAssessmentRepository,
    RecoveryMetricsRepository, RecoveryProgramRepository
)
from .adapters import (
    AssessmentSystemAdapter, ProjectTrackingAdapter, ReportingServiceAdapter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecoveryProgressTrackingService:
    """
    Service for recovery progress tracking.
    
    This service provides functionality for:
    1. Recovery project management (create, update, track)
    2. Damage assessment management
    3. Recovery metrics collection and analysis
    4. Recovery program management
    5. Report generation and submission
    """
    
    def __init__(
        self,
        project_repository: RecoveryProjectRepository,
        assessment_repository: DamageAssessmentRepository,
        metrics_repository: RecoveryMetricsRepository,
        program_repository: RecoveryProgramRepository,
        assessment_adapter: Optional[AssessmentSystemAdapter] = None,
        project_adapter: Optional[ProjectTrackingAdapter] = None,
        reporting_adapter: Optional[ReportingServiceAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the service.
        
        Args:
            project_repository: Repository for recovery projects
            assessment_repository: Repository for damage assessments
            metrics_repository: Repository for recovery metrics
            program_repository: Repository for recovery programs
            assessment_adapter: Adapter for external assessment systems
            project_adapter: Adapter for external project tracking systems
            reporting_adapter: Adapter for external reporting services
            config: Service configuration
        """
        self.project_repository = project_repository
        self.assessment_repository = assessment_repository
        self.metrics_repository = metrics_repository
        self.program_repository = program_repository
        self.assessment_adapter = assessment_adapter
        self.project_adapter = project_adapter
        self.reporting_adapter = reporting_adapter
        self.config = config or {}
        
        logger.info("RecoveryProgressTrackingService initialized")
    
    # Recovery Project Management Methods
    
    def get_project(self, project_id: str) -> Optional[RecoveryProject]:
        """
        Get a recovery project by ID.
        
        Args:
            project_id: The ID of the project to retrieve
            
        Returns:
            The project if found, None otherwise
        """
        return self.project_repository.get_by_id(project_id)
    
    def get_all_projects(self) -> List[RecoveryProject]:
        """
        Get all recovery projects.
        
        Returns:
            List of all projects
        """
        return self.project_repository.get_all()
    
    def create_project(self, project_data: Dict[str, Any]) -> RecoveryProject:
        """
        Create a new recovery project.
        
        Args:
            project_data: Dictionary with project data
            
        Returns:
            The created project
            
        Raises:
            ValueError: If project data is invalid
        """
        # Validate required fields
        required_fields = ['project_name', 'event_id', 'project_type', 'location']
        for field in required_fields:
            if field not in project_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set default status if not specified
        if 'status' not in project_data:
            project_data['status'] = 'PLANNING'
            
        # Set default phase if not specified
        if 'phase' not in project_data:
            project_data['phase'] = RecoveryPhase.INITIAL_RESPONSE.value
        
        # Create the project
        project = RecoveryProject(**project_data)
        
        # Save the project
        created_project = self.project_repository.create(project)
        
        # Register with external tracking system if available
        if self.project_adapter:
            try:
                self.project_adapter.update_project(created_project.id, created_project.to_dict())
            except Exception as e:
                logger.error(f"Error registering project with external system: {str(e)}")
        
        logger.info(f"Created new recovery project with ID: {created_project.id}")
        return created_project
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[RecoveryProject]:
        """
        Update an existing recovery project.
        
        Args:
            project_id: ID of the project to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated project or None if project not found
        """
        # Get the project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            logger.warning(f"Project not found for update: {project_id}")
            return None
        
        # Save old status and phase for comparison
        old_status = project.status if hasattr(project, 'status') else None
        old_phase = project.phase if hasattr(project, 'phase') else None
        
        # Update the project
        for key, value in updates.items():
            setattr(project, key, value)
            
        # Update timestamp
        project.updated_at = datetime.now().isoformat()
        
        # Save the updated project
        updated_project = self.project_repository.update(project)
        
        # Update external tracking system if available
        if self.project_adapter:
            try:
                self.project_adapter.update_project(project_id, updates)
            except Exception as e:
                logger.error(f"Error updating project in external system: {str(e)}")
        
        # Create metrics if status or phase changed
        new_status = getattr(updated_project, 'status', None)
        new_phase = getattr(updated_project, 'phase', None)
        
        if (old_status != new_status and new_status == 'COMPLETED') or (old_phase != new_phase):
            try:
                self._create_project_milestone_metrics(updated_project)
            except Exception as e:
                logger.error(f"Error creating milestone metrics: {str(e)}")
        
        logger.info(f"Updated project with ID: {project_id}")
        return updated_project
    
    def update_project_status(self, project_id: str, new_status: str, notes: str = None) -> Optional[RecoveryProject]:
        """
        Update a project's status.
        
        Args:
            project_id: ID of the project to update
            new_status: New status for the project
            notes: Optional notes about the status change
            
        Returns:
            The updated project or None if project not found
        """
        # Get the project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            logger.warning(f"Project not found for status update: {project_id}")
            return None
        
        # Update the status
        project.update_status(new_status, notes)
        
        # Save the updated project
        updated_project = self.project_repository.update(project)
        
        # Update external tracking system if available
        if self.project_adapter:
            try:
                self.project_adapter.update_project(project_id, {'status': new_status})
            except Exception as e:
                logger.error(f"Error updating project status in external system: {str(e)}")
        
        logger.info(f"Updated project status to {new_status} for project ID: {project_id}")
        return updated_project
    
    def update_project_phase(self, project_id: str, new_phase: str, notes: str = None) -> Optional[RecoveryProject]:
        """
        Update a project's recovery phase.
        
        Args:
            project_id: ID of the project to update
            new_phase: New recovery phase for the project
            notes: Optional notes about the phase change
            
        Returns:
            The updated project or None if project not found
        """
        # Get the project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            logger.warning(f"Project not found for phase update: {project_id}")
            return None
        
        # Update the phase
        project.update_phase(new_phase, notes)
        
        # Save the updated project
        updated_project = self.project_repository.update(project)
        
        # Update external tracking system if available
        if self.project_adapter:
            try:
                self.project_adapter.update_project(project_id, {'phase': new_phase})
            except Exception as e:
                logger.error(f"Error updating project phase in external system: {str(e)}")
                
        # Create phase change metrics
        try:
            self._create_project_milestone_metrics(updated_project)
        except Exception as e:
            logger.error(f"Error creating milestone metrics: {str(e)}")
        
        logger.info(f"Updated project phase to {new_phase} for project ID: {project_id}")
        return updated_project
    
    def add_project_progress_update(self, project_id: str, update_data: Dict[str, Any]) -> Optional[RecoveryProject]:
        """
        Add a progress update to a project.
        
        Args:
            project_id: ID of the project to update
            update_data: Dictionary with progress update data
            
        Returns:
            The updated project or None if project not found
            
        Raises:
            ValueError: If update data is invalid
        """
        # Validate update data
        required_fields = ['type']
        for field in required_fields:
            if field not in update_data:
                raise ValueError(f"Missing required field in progress update: {field}")
                
        # Set timestamp if not specified
        if 'timestamp' not in update_data:
            update_data['timestamp'] = datetime.now().isoformat()
        
        # Get the project
        project = self.project_repository.get_by_id(project_id)
        if not project:
            logger.warning(f"Project not found for progress update: {project_id}")
            return None
        
        # Add the progress update
        project.add_progress_update(update_data)
        
        # Save the updated project
        updated_project = self.project_repository.update(project)
        
        # Update external tracking system if available
        if self.project_adapter and 'percent_complete' in update_data:
            try:
                self.project_adapter.update_project(project_id, {'progress_updates': getattr(updated_project, 'progress_updates', [])})
            except Exception as e:
                logger.error(f"Error updating project progress in external system: {str(e)}")
                
        # Create progress metrics if significant progress (25%, 50%, 75%, 100%)
        if 'percent_complete' in update_data:
            percent = update_data['percent_complete']
            if percent in [25, 50, 75, 100]:
                try:
                    self._create_project_progress_metrics(updated_project, percent)
                except Exception as e:
                    logger.error(f"Error creating progress metrics: {str(e)}")
        
        logger.info(f"Added progress update to project ID: {project_id}")
        return updated_project
    
    def find_projects_by_event(self, event_id: str) -> List[RecoveryProject]:
        """
        Find projects for a specific disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            List of projects for the event
        """
        return self.project_repository.find_by_event_id(event_id)
    
    def find_projects_by_type(self, project_type: str) -> List[RecoveryProject]:
        """
        Find projects by type.
        
        Args:
            project_type: Type of project
            
        Returns:
            List of projects of the specified type
        """
        return self.project_repository.find_by_project_type(project_type)
    
    def find_projects_by_status(self, status: str) -> List[RecoveryProject]:
        """
        Find projects by status.
        
        Args:
            status: Project status
            
        Returns:
            List of projects with the specified status
        """
        return self.project_repository.find_by_status(status)
    
    def find_projects_by_phase(self, phase: str) -> List[RecoveryProject]:
        """
        Find projects by recovery phase.
        
        Args:
            phase: Recovery phase
            
        Returns:
            List of projects in the specified phase
        """
        return self.project_repository.find_by_phase(phase)
    
    def find_active_projects(self) -> List[RecoveryProject]:
        """
        Find active (non-completed) projects.
        
        Returns:
            List of active projects
        """
        return self.project_repository.find_active_projects()
    
    def find_overdue_projects(self) -> List[RecoveryProject]:
        """
        Find overdue projects.
        
        Returns:
            List of overdue projects
        """
        return self.project_repository.find_overdue_projects()
    
    def import_projects_from_tracking_system(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Import projects from the external tracking system.
        
        Args:
            params: Parameters for the import
            
        Returns:
            Dictionary with import results
            
        Raises:
            RuntimeError: If project adapter is not configured
        """
        if not self.project_adapter:
            raise RuntimeError("Project tracking adapter not configured")
        
        params = params or {}
        logger.info(f"Importing projects from tracking system with params: {params}")
        
        # Fetch data from tracking system
        project_data = self.project_adapter.fetch_projects(**params)
        
        # Process results
        imported_count = 0
        updated_count = 0
        errors = []
        
        for record in project_data:
            try:
                # Convert to project
                project = self.project_adapter.convert_to_project(record)
                if not project:
                    errors.append(f"Failed to convert record: {record.get('id', 'unknown')}")
                    continue
                
                # Check if project already exists
                existing = self.project_repository.get_by_id(project.id)
                
                if existing:
                    # Update existing project
                    for key, value in project.to_dict().items():
                        if key != 'id':  # Don't update ID
                            setattr(existing, key, value)
                    
                    existing.updated_at = datetime.now().isoformat()
                    self.project_repository.update(existing)
                    updated_count += 1
                else:
                    # Save the new project
                    self.project_repository.create(project)
                    imported_count += 1
                
            except Exception as e:
                error_msg = f"Error processing record {record.get('id', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            'total_records': len(project_data),
            'imported_count': imported_count,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors[:10]  # Limit error list
        }
        
        logger.info(f"Project import complete: {imported_count} imported, {updated_count} updated, {len(errors)} errors")
        return result
    
    # Damage Assessment Management Methods
    
    def get_assessment(self, assessment_id: str) -> Optional[DamageAssessment]:
        """
        Get a damage assessment by ID.
        
        Args:
            assessment_id: The ID of the assessment to retrieve
            
        Returns:
            The assessment if found, None otherwise
        """
        return self.assessment_repository.get_by_id(assessment_id)
    
    def get_all_assessments(self) -> List[DamageAssessment]:
        """
        Get all damage assessments.
        
        Returns:
            List of all assessments
        """
        return self.assessment_repository.get_all()
    
    def create_assessment(self, assessment_data: Dict[str, Any]) -> DamageAssessment:
        """
        Create a new damage assessment.
        
        Args:
            assessment_data: Dictionary with assessment data
            
        Returns:
            The created assessment
            
        Raises:
            ValueError: If assessment data is invalid
        """
        # Validate required fields
        required_fields = ['event_id', 'assessment_area', 'assessment_type', 'damage_level']
        for field in required_fields:
            if field not in assessment_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set default status if not specified
        if 'status' not in assessment_data:
            assessment_data['status'] = 'DRAFT'
            
        # Set assessment date if not specified
        if 'assessment_date' not in assessment_data:
            assessment_data['assessment_date'] = datetime.now().isoformat()
        
        # Create the assessment
        assessment = DamageAssessment(**assessment_data)
        
        # Save the assessment
        created_assessment = self.assessment_repository.create(assessment)
        
        logger.info(f"Created new damage assessment with ID: {created_assessment.id}")
        return created_assessment
    
    def update_assessment(self, assessment_id: str, updates: Dict[str, Any]) -> Optional[DamageAssessment]:
        """
        Update an existing damage assessment.
        
        Args:
            assessment_id: ID of the assessment to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated assessment or None if assessment not found
        """
        # Get the assessment
        assessment = self.assessment_repository.get_by_id(assessment_id)
        if not assessment:
            logger.warning(f"Assessment not found for update: {assessment_id}")
            return None
        
        # Check if assessment is final (should not be updated)
        if hasattr(assessment, 'status') and assessment.status == 'FINAL':
            raise ValueError(f"Cannot update assessment with ID {assessment_id} because it is already finalized")
        
        # Update the assessment
        for key, value in updates.items():
            setattr(assessment, key, value)
            
        # Update timestamp
        assessment.updated_at = datetime.now().isoformat()
        
        # Save the updated assessment
        updated_assessment = self.assessment_repository.update(assessment)
        
        logger.info(f"Updated assessment with ID: {assessment_id}")
        return updated_assessment
    
    def finalize_assessment(self, assessment_id: str, approver: str = None) -> Optional[DamageAssessment]:
        """
        Finalize a damage assessment.
        
        Args:
            assessment_id: ID of the assessment to finalize
            approver: Optional name or ID of the approver
            
        Returns:
            The updated assessment or None if assessment not found
            
        Raises:
            ValueError: If assessment is already finalized
        """
        # Get the assessment
        assessment = self.assessment_repository.get_by_id(assessment_id)
        if not assessment:
            logger.warning(f"Assessment not found for finalization: {assessment_id}")
            return None
        
        # Check if assessment is already final
        if hasattr(assessment, 'status') and assessment.status == 'FINAL':
            raise ValueError(f"Assessment with ID {assessment_id} is already finalized")
        
        # Finalize the assessment
        assessment.finalize(approver)
        
        # Save the updated assessment
        updated_assessment = self.assessment_repository.update(assessment)
        
        # Create damage metrics based on this assessment
        try:
            self._create_damage_assessment_metrics(updated_assessment)
        except Exception as e:
            logger.error(f"Error creating damage assessment metrics: {str(e)}")
        
        logger.info(f"Finalized assessment with ID: {assessment_id}")
        return updated_assessment
    
    def find_assessments_by_event(self, event_id: str) -> List[DamageAssessment]:
        """
        Find assessments for a specific disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            List of assessments for the event
        """
        return self.assessment_repository.find_by_event_id(event_id)
    
    def find_assessments_by_type(self, assessment_type: str) -> List[DamageAssessment]:
        """
        Find assessments by type.
        
        Args:
            assessment_type: Type of assessment
            
        Returns:
            List of assessments of the specified type
        """
        return self.assessment_repository.find_by_assessment_type(assessment_type)
    
    def find_assessments_by_damage_level(self, damage_level: str) -> List[DamageAssessment]:
        """
        Find assessments by damage level.
        
        Args:
            damage_level: Damage level
            
        Returns:
            List of assessments with the specified damage level
        """
        return self.assessment_repository.find_by_damage_level(damage_level)
    
    def find_final_assessments(self) -> List[DamageAssessment]:
        """
        Find finalized assessments.
        
        Returns:
            List of finalized assessments
        """
        return self.assessment_repository.find_final_assessments()
    
    def import_assessments_from_system(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Import assessments from the external assessment system.
        
        Args:
            params: Parameters for the import
            
        Returns:
            Dictionary with import results
            
        Raises:
            RuntimeError: If assessment adapter is not configured
        """
        if not self.assessment_adapter:
            raise RuntimeError("Assessment system adapter not configured")
        
        params = params or {}
        logger.info(f"Importing assessments from assessment system with params: {params}")
        
        # Fetch data from assessment system
        assessment_data = self.assessment_adapter.fetch_assessments(**params)
        
        # Process results
        imported_count = 0
        updated_count = 0
        errors = []
        
        for record in assessment_data:
            try:
                # Convert to assessment
                assessment = self.assessment_adapter.convert_to_assessment(record)
                if not assessment:
                    errors.append(f"Failed to convert record: {record.get('id', 'unknown')}")
                    continue
                
                # Check if assessment already exists
                existing = self.assessment_repository.get_by_id(assessment.id)
                
                if existing:
                    # If existing is final, don't update
                    if hasattr(existing, 'status') and existing.status == 'FINAL':
                        logger.info(f"Skipping update of finalized assessment: {existing.id}")
                        continue
                        
                    # Update existing assessment
                    for key, value in assessment.to_dict().items():
                        if key != 'id':  # Don't update ID
                            setattr(existing, key, value)
                    
                    existing.updated_at = datetime.now().isoformat()
                    self.assessment_repository.update(existing)
                    updated_count += 1
                else:
                    # Save the new assessment
                    self.assessment_repository.create(assessment)
                    imported_count += 1
                
            except Exception as e:
                error_msg = f"Error processing record {record.get('id', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            'total_records': len(assessment_data),
            'imported_count': imported_count,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors[:10]  # Limit error list
        }
        
        logger.info(f"Assessment import complete: {imported_count} imported, {updated_count} updated, {len(errors)} errors")
        return result
    
    # Recovery Metrics Management Methods
    
    def get_metrics(self, metrics_id: str) -> Optional[RecoveryMetrics]:
        """
        Get recovery metrics by ID.
        
        Args:
            metrics_id: The ID of the metrics to retrieve
            
        Returns:
            The metrics if found, None otherwise
        """
        return self.metrics_repository.get_by_id(metrics_id)
    
    def get_all_metrics(self) -> List[RecoveryMetrics]:
        """
        Get all recovery metrics.
        
        Returns:
            List of all metrics
        """
        return self.metrics_repository.get_all()
    
    def create_metrics(self, metrics_data: Dict[str, Any]) -> RecoveryMetrics:
        """
        Create new recovery metrics.
        
        Args:
            metrics_data: Dictionary with metrics data
            
        Returns:
            The created metrics
            
        Raises:
            ValueError: If metrics data is invalid
        """
        # Validate required fields
        required_fields = ['event_id', 'reporting_period', 'metrics_type', 'metrics_values']
        for field in required_fields:
            if field not in metrics_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults if not specified
        if 'report_date' not in metrics_data:
            metrics_data['report_date'] = datetime.now().isoformat()
            
        if 'status' not in metrics_data:
            metrics_data['status'] = 'DRAFT'
        
        # Create the metrics
        metrics = RecoveryMetrics(**metrics_data)
        
        # Save the metrics
        created_metrics = self.metrics_repository.create(metrics)
        
        logger.info(f"Created new recovery metrics with ID: {created_metrics.id}")
        return created_metrics
    
    def update_metrics(self, metrics_id: str, updates: Dict[str, Any]) -> Optional[RecoveryMetrics]:
        """
        Update existing recovery metrics.
        
        Args:
            metrics_id: ID of the metrics to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated metrics or None if metrics not found
        """
        # Get the metrics
        metrics = self.metrics_repository.get_by_id(metrics_id)
        if not metrics:
            logger.warning(f"Metrics not found for update: {metrics_id}")
            return None
        
        # Check if metrics are finalized (should not be updated)
        if hasattr(metrics, 'status') and metrics.status == 'FINAL':
            raise ValueError(f"Cannot update metrics with ID {metrics_id} because they are already finalized")
        
        # Update the metrics
        for key, value in updates.items():
            setattr(metrics, key, value)
            
        # Update timestamp
        metrics.updated_at = datetime.now().isoformat()
        
        # Save the updated metrics
        updated_metrics = self.metrics_repository.update(metrics)
        
        logger.info(f"Updated metrics with ID: {metrics_id}")
        return updated_metrics
    
    def finalize_metrics(self, metrics_id: str, approver: str = None) -> Optional[RecoveryMetrics]:
        """
        Finalize recovery metrics.
        
        Args:
            metrics_id: ID of the metrics to finalize
            approver: Optional name or ID of the approver
            
        Returns:
            The updated metrics or None if metrics not found
            
        Raises:
            ValueError: If metrics are already finalized
        """
        # Get the metrics
        metrics = self.metrics_repository.get_by_id(metrics_id)
        if not metrics:
            logger.warning(f"Metrics not found for finalization: {metrics_id}")
            return None
        
        # Check if metrics are already final
        if hasattr(metrics, 'status') and metrics.status == 'FINAL':
            raise ValueError(f"Metrics with ID {metrics_id} are already finalized")
        
        # Finalize the metrics
        metrics.finalize(approver)
        
        # Save the updated metrics
        updated_metrics = self.metrics_repository.update(metrics)
        
        # Generate and submit report if reporting adapter is available
        if self.reporting_adapter:
            try:
                self._submit_metrics_report(updated_metrics)
            except Exception as e:
                logger.error(f"Error submitting metrics report: {str(e)}")
        
        logger.info(f"Finalized metrics with ID: {metrics_id}")
        return updated_metrics
    
    def find_metrics_by_event(self, event_id: str) -> List[RecoveryMetrics]:
        """
        Find metrics for a specific disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            List of metrics for the event
        """
        return self.metrics_repository.find_by_event_id(event_id)
    
    def find_metrics_by_type(self, metrics_type: str) -> List[RecoveryMetrics]:
        """
        Find metrics by type.
        
        Args:
            metrics_type: Type of metrics
            
        Returns:
            List of metrics of the specified type
        """
        return self.metrics_repository.find_by_metrics_type(metrics_type)
    
    def find_metrics_by_phase(self, phase: str) -> List[RecoveryMetrics]:
        """
        Find metrics by recovery phase.
        
        Args:
            phase: Recovery phase
            
        Returns:
            List of metrics for the specified phase
        """
        return self.metrics_repository.find_by_phase(phase)
    
    def get_latest_metrics_for_event(self, event_id: str, metrics_type: str = None) -> Optional[RecoveryMetrics]:
        """
        Get the latest metrics for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            metrics_type: Optional type of metrics to filter by
            
        Returns:
            The latest metrics if found, None otherwise
        """
        return self.metrics_repository.find_latest_by_event(event_id, metrics_type)
    
    def generate_recovery_progress_metrics(self, event_id: str) -> RecoveryMetrics:
        """
        Generate recovery progress metrics for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            The generated metrics
            
        Raises:
            ValueError: If no projects are found for the event
        """
        # Get projects for the event
        projects = self.project_repository.find_by_event_id(event_id)
        
        if not projects:
            raise ValueError(f"No projects found for event ID {event_id}")
            
        # Determine reporting period
        now = datetime.now()
        start_date = (now - timedelta(days=30)).isoformat()
        end_date = now.isoformat()
        
        # Calculate metrics
        metrics_values = self._calculate_recovery_progress_metrics(projects)
        
        # Create metrics record
        metrics_data = {
            'event_id': event_id,
            'reporting_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'metrics_type': 'recovery_progress',
            'metrics_values': metrics_values,
            'report_date': now.isoformat(),
            'phase': self._determine_overall_recovery_phase(projects)
        }
        
        return self.create_metrics(metrics_data)
    
    def generate_financial_progress_metrics(self, event_id: str) -> RecoveryMetrics:
        """
        Generate financial progress metrics for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            The generated metrics
            
        Raises:
            ValueError: If no projects are found for the event
        """
        # Get projects for the event
        projects = self.project_repository.find_by_event_id(event_id)
        
        if not projects:
            raise ValueError(f"No projects found for event ID {event_id}")
            
        # Determine reporting period
        now = datetime.now()
        start_date = (now - timedelta(days=30)).isoformat()
        end_date = now.isoformat()
        
        # Calculate metrics
        metrics_values = self._calculate_financial_progress_metrics(projects)
        
        # Create metrics record
        metrics_data = {
            'event_id': event_id,
            'reporting_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'metrics_type': 'financial_progress',
            'metrics_values': metrics_values,
            'report_date': now.isoformat(),
            'phase': self._determine_overall_recovery_phase(projects)
        }
        
        return self.create_metrics(metrics_data)
    
    def generate_impact_metrics(self, event_id: str) -> RecoveryMetrics:
        """
        Generate impact metrics for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            The generated metrics
            
        Raises:
            ValueError: If no assessments are found for the event
        """
        # Get assessments for the event
        assessments = self.assessment_repository.find_by_event_id(event_id)
        
        if not assessments:
            raise ValueError(f"No assessments found for event ID {event_id}")
            
        # Get projects for the event (for beneficiary data)
        projects = self.project_repository.find_by_event_id(event_id)
        
        # Determine reporting period
        now = datetime.now()
        
        # Find the earliest assessment date
        assessment_dates = [datetime.fromisoformat(a.assessment_date) for a in assessments if hasattr(a, 'assessment_date')]
        start_date = min(assessment_dates).isoformat() if assessment_dates else (now - timedelta(days=30)).isoformat()
        end_date = now.isoformat()
        
        # Calculate metrics
        metrics_values = self._calculate_impact_metrics(assessments, projects)
        
        # Create metrics record
        metrics_data = {
            'event_id': event_id,
            'reporting_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'metrics_type': 'impact',
            'metrics_values': metrics_values,
            'report_date': now.isoformat()
        }
        
        return self.create_metrics(metrics_data)
    
    def generate_comprehensive_metrics(self, event_id: str) -> RecoveryMetrics:
        """
        Generate comprehensive metrics for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            The generated metrics
        """
        # Get projects and assessments for the event
        projects = self.project_repository.find_by_event_id(event_id)
        assessments = self.assessment_repository.find_by_event_id(event_id)
        
        # Determine reporting period
        now = datetime.now()
        start_date = (now - timedelta(days=30)).isoformat()
        end_date = now.isoformat()
        
        # Calculate metrics
        metrics_values = {
            'recovery_progress': self._calculate_recovery_progress_metrics(projects) if projects else {},
            'financial_progress': self._calculate_financial_progress_metrics(projects) if projects else {},
            'impact': self._calculate_impact_metrics(assessments, projects) if assessments else {}
        }
        
        # Add summary metrics
        metrics_values['summary'] = self._calculate_summary_metrics(metrics_values)
        
        # Create metrics record
        metrics_data = {
            'event_id': event_id,
            'reporting_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'metrics_type': 'comprehensive',
            'metrics_values': metrics_values,
            'report_date': now.isoformat(),
            'phase': self._determine_overall_recovery_phase(projects) if projects else None
        }
        
        return self.create_metrics(metrics_data)
    
    # Recovery Program Management Methods
    
    def get_program(self, program_id: str) -> Optional[RecoveryProgram]:
        """
        Get a recovery program by ID.
        
        Args:
            program_id: The ID of the program to retrieve
            
        Returns:
            The program if found, None otherwise
        """
        return self.program_repository.get_by_id(program_id)
    
    def get_all_programs(self) -> List[RecoveryProgram]:
        """
        Get all recovery programs.
        
        Returns:
            List of all programs
        """
        return self.program_repository.get_all()
    
    def create_program(self, program_data: Dict[str, Any]) -> RecoveryProgram:
        """
        Create a new recovery program.
        
        Args:
            program_data: Dictionary with program data
            
        Returns:
            The created program
            
        Raises:
            ValueError: If program data is invalid
        """
        # Validate required fields
        required_fields = ['program_name', 'program_type', 'description', 'eligibility_criteria']
        for field in required_fields:
            if field not in program_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults if not specified
        if 'program_status' not in program_data:
            program_data['program_status'] = 'ACTIVE'
            
        if 'program_start' not in program_data:
            program_data['program_start'] = datetime.now().isoformat()
        
        # Create the program
        program = RecoveryProgram(**program_data)
        
        # Save the program
        created_program = self.program_repository.create(program)
        
        logger.info(f"Created new recovery program with ID: {created_program.id}")
        return created_program
    
    def update_program(self, program_id: str, updates: Dict[str, Any]) -> Optional[RecoveryProgram]:
        """
        Update an existing recovery program.
        
        Args:
            program_id: ID of the program to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated program or None if program not found
        """
        # Get the program
        program = self.program_repository.get_by_id(program_id)
        if not program:
            logger.warning(f"Program not found for update: {program_id}")
            return None
        
        # Update the program
        for key, value in updates.items():
            setattr(program, key, value)
            
        # Update timestamp
        program.updated_at = datetime.now().isoformat()
        
        # Save the updated program
        updated_program = self.program_repository.update(program)
        
        logger.info(f"Updated program with ID: {program_id}")
        return updated_program
    
    def close_program(self, program_id: str, reason: str = None) -> Optional[RecoveryProgram]:
        """
        Close a recovery program.
        
        Args:
            program_id: ID of the program to close
            reason: Optional reason for closure
            
        Returns:
            The updated program or None if program not found
        """
        # Get the program
        program = self.program_repository.get_by_id(program_id)
        if not program:
            logger.warning(f"Program not found for closure: {program_id}")
            return None
        
        # Close the program
        program.close_program(reason)
        
        # Save the updated program
        updated_program = self.program_repository.update(program)
        
        logger.info(f"Closed program with ID: {program_id}")
        return updated_program
    
    def find_programs_by_type(self, program_type: str) -> List[RecoveryProgram]:
        """
        Find programs by type.
        
        Args:
            program_type: Type of program
            
        Returns:
            List of programs of the specified type
        """
        return self.program_repository.find_by_program_type(program_type)
    
    def find_programs_by_agency(self, administering_agency: str) -> List[RecoveryProgram]:
        """
        Find programs by administering agency.
        
        Args:
            administering_agency: Administering agency
            
        Returns:
            List of programs administered by the specified agency
        """
        return self.program_repository.find_by_agency(administering_agency)
    
    def find_programs_by_status(self, program_status: str) -> List[RecoveryProgram]:
        """
        Find programs by status.
        
        Args:
            program_status: Program status
            
        Returns:
            List of programs with the specified status
        """
        return self.program_repository.find_by_status(program_status)
    
    def find_active_programs(self) -> List[RecoveryProgram]:
        """
        Find active programs.
        
        Returns:
            List of active programs
        """
        return self.program_repository.find_active_programs()
    
    def find_programs_for_event(self, event_id: str) -> List[RecoveryProgram]:
        """
        Find programs related to a specific disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            List of programs related to the event
        """
        return self.program_repository.find_by_related_event(event_id)
    
    # Report Generation Methods
    
    def generate_progress_report(self, event_id: str) -> Dict[str, Any]:
        """
        Generate a progress report for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            Generated report data
            
        Raises:
            ValueError: If no projects are found for the event
            RuntimeError: If reporting adapter is not configured
        """
        if not self.reporting_adapter:
            raise RuntimeError("Reporting service adapter not configured")
            
        # Get projects for the event
        projects = self.project_repository.find_by_event_id(event_id)
        
        if not projects:
            raise ValueError(f"No projects found for event ID {event_id}")
            
        # Prepare report data
        report_data = {
            'event_id': event_id,
            'projects': [p.to_dict() for p in projects],
            'report_type': 'progress',
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate report
        return self.reporting_adapter.generate_report('progress', report_data)
    
    def generate_financial_report(self, event_id: str) -> Dict[str, Any]:
        """
        Generate a financial report for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            Generated report data
            
        Raises:
            ValueError: If no projects are found for the event
            RuntimeError: If reporting adapter is not configured
        """
        if not self.reporting_adapter:
            raise RuntimeError("Reporting service adapter not configured")
            
        # Get projects for the event
        projects = self.project_repository.find_by_event_id(event_id)
        
        if not projects:
            raise ValueError(f"No projects found for event ID {event_id}")
            
        # Prepare report data
        report_data = {
            'event_id': event_id,
            'projects': [p.to_dict() for p in projects],
            'report_type': 'financial',
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate report
        return self.reporting_adapter.generate_report('financial', report_data)
    
    def generate_impact_report(self, event_id: str) -> Dict[str, Any]:
        """
        Generate an impact report for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            Generated report data
            
        Raises:
            ValueError: If no assessments are found for the event
            RuntimeError: If reporting adapter is not configured
        """
        if not self.reporting_adapter:
            raise RuntimeError("Reporting service adapter not configured")
            
        # Get assessments for the event
        assessments = self.assessment_repository.find_by_event_id(event_id)
        
        if not assessments:
            raise ValueError(f"No assessments found for event ID {event_id}")
            
        # Get projects for the event (for beneficiary data)
        projects = self.project_repository.find_by_event_id(event_id)
        
        # Prepare report data
        report_data = {
            'event_id': event_id,
            'assessments': [a.to_dict() for a in assessments],
            'projects': [p.to_dict() for p in projects] if projects else [],
            'report_type': 'impact',
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate report
        return self.reporting_adapter.generate_report('impact', report_data)
    
    def generate_summary_report(self, event_id: str) -> Dict[str, Any]:
        """
        Generate a summary report for a disaster event.
        
        Args:
            event_id: ID of the disaster event
            
        Returns:
            Generated report data
            
        Raises:
            RuntimeError: If reporting adapter is not configured
        """
        if not self.reporting_adapter:
            raise RuntimeError("Reporting service adapter not configured")
            
        # Get projects and assessments for the event
        projects = self.project_repository.find_by_event_id(event_id)
        assessments = self.assessment_repository.find_by_event_id(event_id)
        
        # Prepare report data
        report_data = {
            'event_id': event_id,
            'projects': [p.to_dict() for p in projects] if projects else [],
            'assessments': [a.to_dict() for a in assessments] if assessments else [],
            'report_type': 'summary',
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate report
        return self.reporting_adapter.generate_report('summary', report_data)
    
    def submit_report(self, report_data: Dict[str, Any]) -> bool:
        """
        Submit a report to the reporting service.
        
        Args:
            report_data: Report data to submit
            
        Returns:
            True if submission was successful, False otherwise
            
        Raises:
            RuntimeError: If reporting adapter is not configured
        """
        if not self.reporting_adapter:
            raise RuntimeError("Reporting service adapter not configured")
            
        return self.reporting_adapter.submit_report(report_data)
    
    # Helper Methods
    
    def _create_project_milestone_metrics(self, project: RecoveryProject) -> None:
        """
        Create metrics for a project milestone (status or phase change).
        
        Args:
            project: The project that reached a milestone
        """
        # Determine metrics type based on milestone
        if hasattr(project, 'status') and project.status == 'COMPLETED':
            metrics_type = 'project_completion'
        elif hasattr(project, 'phase'):
            metrics_type = f"phase_transition_{project.phase}"
        else:
            metrics_type = 'project_milestone'
            
        # Create metrics
        now = datetime.now()
        metrics_data = {
            'event_id': project.event_id,
            'reporting_period': {
                'start_date': (now - timedelta(days=1)).isoformat(),
                'end_date': now.isoformat()
            },
            'metrics_type': metrics_type,
            'metrics_values': {
                'project_id': project.id,
                'project_name': project.project_name,
                'project_type': project.project_type,
                'status': getattr(project, 'status', None),
                'phase': getattr(project, 'phase', None),
                'percent_complete': project.percent_complete,
                'budget_utilization': project.budget_utilization,
                'milestone_timestamp': now.isoformat()
            },
            'report_date': now.isoformat(),
            'phase': getattr(project, 'phase', None)
        }
        
        self.create_metrics(metrics_data)
    
    def _create_project_progress_metrics(self, project: RecoveryProject, progress_milestone: int) -> None:
        """
        Create metrics for a project progress milestone.
        
        Args:
            project: The project that reached a progress milestone
            progress_milestone: The progress percentage milestone (25, 50, 75, 100)
        """
        # Create metrics
        now = datetime.now()
        metrics_data = {
            'event_id': project.event_id,
            'reporting_period': {
                'start_date': (now - timedelta(days=1)).isoformat(),
                'end_date': now.isoformat()
            },
            'metrics_type': f"progress_milestone_{progress_milestone}",
            'metrics_values': {
                'project_id': project.id,
                'project_name': project.project_name,
                'project_type': project.project_type,
                'status': getattr(project, 'status', None),
                'phase': getattr(project, 'phase', None),
                'percent_complete': progress_milestone,
                'budget_utilization': project.budget_utilization,
                'milestone_timestamp': now.isoformat()
            },
            'report_date': now.isoformat(),
            'phase': getattr(project, 'phase', None)
        }
        
        self.create_metrics(metrics_data)
    
    def _create_damage_assessment_metrics(self, assessment: DamageAssessment) -> None:
        """
        Create metrics from a finalized damage assessment.
        
        Args:
            assessment: The finalized damage assessment
        """
        # Create metrics
        now = datetime.now()
        
        # Extract damage values
        damages = {}
        
        if hasattr(assessment, 'infrastructure_damage') and assessment.infrastructure_damage:
            if isinstance(assessment.infrastructure_damage, dict) and 'value' in assessment.infrastructure_damage:
                damages['infrastructure'] = assessment.infrastructure_damage['value']
                
        if hasattr(assessment, 'housing_damage') and assessment.housing_damage:
            if isinstance(assessment.housing_damage, dict) and 'value' in assessment.housing_damage:
                damages['housing'] = assessment.housing_damage['value']
                
        if hasattr(assessment, 'economic_impact') and assessment.economic_impact:
            if isinstance(assessment.economic_impact, dict) and 'value' in assessment.economic_impact:
                damages['economic'] = assessment.economic_impact['value']
                
        if hasattr(assessment, 'environmental_impact') and assessment.environmental_impact:
            if isinstance(assessment.environmental_impact, dict) and 'value' in assessment.environmental_impact:
                damages['environmental'] = assessment.environmental_impact['value']
        
        metrics_data = {
            'event_id': assessment.event_id,
            'reporting_period': {
                'start_date': assessment.assessment_date,
                'end_date': now.isoformat()
            },
            'metrics_type': 'damage_assessment',
            'metrics_values': {
                'assessment_id': assessment.id,
                'assessment_type': assessment.assessment_type,
                'damage_level': assessment.damage_level,
                'damages': damages,
                'affected_population': getattr(assessment, 'affected_population', None),
                'total_damage_estimate': assessment.total_damage_estimate,
                'assessment_date': assessment.assessment_date
            },
            'report_date': now.isoformat()
        }
        
        self.create_metrics(metrics_data)
    
    def _submit_metrics_report(self, metrics: RecoveryMetrics) -> None:
        """
        Submit a report based on finalized metrics.
        
        Args:
            metrics: The finalized metrics
        """
        if not self.reporting_adapter:
            return
            
        # Determine report type from metrics type
        metrics_type = getattr(metrics, 'metrics_type', '')
        
        if 'progress' in metrics_type:
            report_type = 'progress'
        elif 'financial' in metrics_type:
            report_type = 'financial'
        elif 'impact' in metrics_type:
            report_type = 'impact'
        elif 'comprehensive' in metrics_type:
            report_type = 'summary'
        else:
            report_type = 'progress'  # Default
            
        # Get projects and assessments for the event
        event_id = getattr(metrics, 'event_id', None)
        if not event_id:
            return
            
        projects = self.project_repository.find_by_event_id(event_id)
        assessments = self.assessment_repository.find_by_event_id(event_id)
        
        # Prepare report data
        report_data = {
            'event_id': event_id,
            'metrics': metrics.to_dict(),
            'projects': [p.to_dict() for p in projects] if projects else [],
            'assessments': [a.to_dict() for a in assessments] if assessments else [],
            'report_type': report_type,
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate and submit report
        report = self.reporting_adapter.generate_report(report_type, report_data)
        self.reporting_adapter.submit_report(report)
    
    def _calculate_recovery_progress_metrics(self, projects: List[RecoveryProject]) -> Dict[str, Any]:
        """
        Calculate recovery progress metrics from projects.
        
        Args:
            projects: List of recovery projects
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {
            'total_projects': len(projects),
            'completed_projects': 0,
            'in_progress_projects': 0,
            'planning_projects': 0,
            'average_completion': 0.0,
            'on_schedule_percentage': 0.0,
            'projects_by_phase': {},
            'projects_by_type': {}
        }
        
        if not projects:
            return metrics
            
        # Calculate counts and percentages
        completion_values = []
        on_schedule = 0
        phase_counts = {}
        type_counts = {}
        
        for project in projects:
            # Count by status
            status = getattr(project, 'status', 'UNKNOWN')
            if status == 'COMPLETED':
                metrics['completed_projects'] += 1
                completion_values.append(100.0)
            elif status in ['IN_PROGRESS']:
                metrics['in_progress_projects'] += 1
                completion_values.append(project.percent_complete)
            elif status in ['PLANNING', 'PENDING_APPROVAL']:
                metrics['planning_projects'] += 1
                completion_values.append(0.0)
                
            # Count on-schedule projects
            target_date = getattr(project, 'target_completion_date', None)
            if target_date and datetime.now().isoformat() <= target_date:
                on_schedule += 1
                
            # Count by phase
            phase = getattr(project, 'phase', 'unknown')
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
            
            # Count by type
            project_type = getattr(project, 'project_type', 'unknown')
            type_counts[project_type] = type_counts.get(project_type, 0) + 1
        
        # Calculate averages and percentages
        if completion_values:
            metrics['average_completion'] = sum(completion_values) / len(completion_values)
            
        if metrics['total_projects'] > 0:
            metrics['on_schedule_percentage'] = (on_schedule / metrics['total_projects']) * 100
            
        metrics['projects_by_phase'] = phase_counts
        metrics['projects_by_type'] = type_counts
        
        return metrics
    
    def _calculate_financial_progress_metrics(self, projects: List[RecoveryProject]) -> Dict[str, Any]:
        """
        Calculate financial progress metrics from projects.
        
        Args:
            projects: List of recovery projects
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {
            'total_budget': 0.0,
            'total_disbursed': 0.0,
            'disbursement_rate': 0.0,
            'remaining_funds': 0.0,
            'budget_by_project_type': {},
            'budget_by_phase': {}
        }
        
        if not projects:
            return metrics
            
        # Calculate financial totals
        type_budgets = {}
        phase_budgets = {}
        
        for project in projects:
            budget = getattr(project, 'allocated_budget', 0.0)
            disbursed = getattr(project, 'funds_disbursed', 0.0)
            
            metrics['total_budget'] += budget
            metrics['total_disbursed'] += disbursed
            
            # Aggregate by project type
            project_type = getattr(project, 'project_type', 'unknown')
            if project_type not in type_budgets:
                type_budgets[project_type] = {'budget': 0.0, 'disbursed': 0.0}
                
            type_budgets[project_type]['budget'] += budget
            type_budgets[project_type]['disbursed'] += disbursed
            
            # Aggregate by phase
            phase = getattr(project, 'phase', 'unknown')
            if phase not in phase_budgets:
                phase_budgets[phase] = {'budget': 0.0, 'disbursed': 0.0}
                
            phase_budgets[phase]['budget'] += budget
            phase_budgets[phase]['disbursed'] += disbursed
        
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
            
        # Format phase budgets
        for phase, amounts in phase_budgets.items():
            metrics['budget_by_phase'][phase] = {
                'budget': amounts['budget'],
                'disbursed': amounts['disbursed'],
                'remaining': amounts['budget'] - amounts['disbursed'],
                'disbursement_rate': (amounts['disbursed'] / amounts['budget']) * 100 if amounts['budget'] > 0 else 0
            }
            
        return metrics
    
    def _calculate_impact_metrics(self, assessments: List[DamageAssessment], projects: List[RecoveryProject] = None) -> Dict[str, Any]:
        """
        Calculate impact metrics from assessments and projects.
        
        Args:
            assessments: List of damage assessments
            projects: Optional list of recovery projects for beneficiary data
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {
            'total_assessments': len(assessments),
            'total_damage_estimate': 0.0,
            'damage_by_type': {},
            'affected_population': 0,
            'assessments_by_damage_level': {}
        }
        
        if not assessments:
            return metrics
            
        # Process assessments
        damage_by_type = {}
        damage_levels = {}
        affected_population = 0
        
        for assessment in assessments:
            # Only use final assessments for calculations
            if hasattr(assessment, 'status') and assessment.status != 'FINAL':
                continue
                
            # Count by damage level
            damage_level = getattr(assessment, 'damage_level', 'unknown')
            damage_levels[damage_level] = damage_levels.get(damage_level, 0) + 1
                
            # Sum affected population
            if hasattr(assessment, 'affected_population') and assessment.affected_population:
                affected_population += assessment.affected_population
                
            # Sum damage estimates by type
            for damage_type in ['infrastructure_damage', 'housing_damage', 'economic_impact', 'environmental_impact']:
                if hasattr(assessment, damage_type) and getattr(assessment, damage_type):
                    damage_data = getattr(assessment, damage_type)
                    if isinstance(damage_data, dict) and 'value' in damage_data:
                        damage_value = damage_data['value']
                        damage_by_type[damage_type] = damage_by_type.get(damage_type, 0.0) + damage_value
                        metrics['total_damage_estimate'] += damage_value
        
        metrics['damage_by_type'] = damage_by_type
        metrics['assessments_by_damage_level'] = damage_levels
        metrics['affected_population'] = affected_population
        
        # Add beneficiary data from projects if available
        if projects:
            beneficiaries = sum(getattr(p, 'beneficiaries', 0) for p in projects)
            metrics['beneficiaries'] = beneficiaries
            
        return metrics
    
    def _calculate_summary_metrics(self, metrics_values: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary metrics from other metrics.
        
        Args:
            metrics_values: Dictionary containing other metrics
            
        Returns:
            Dictionary of calculated summary metrics
        """
        summary = {
            'recovery_progress': {},
            'financial_progress': {},
            'impact': {}
        }
        
        # Extract key metrics from recovery progress
        recovery_metrics = metrics_values.get('recovery_progress', {})
        if recovery_metrics:
            summary['recovery_progress'] = {
                'total_projects': recovery_metrics.get('total_projects', 0),
                'completed_projects': recovery_metrics.get('completed_projects', 0),
                'completion_percentage': recovery_metrics.get('average_completion', 0.0),
                'on_schedule_percentage': recovery_metrics.get('on_schedule_percentage', 0.0)
            }
            
        # Extract key metrics from financial progress
        financial_metrics = metrics_values.get('financial_progress', {})
        if financial_metrics:
            summary['financial_progress'] = {
                'total_budget': financial_metrics.get('total_budget', 0.0),
                'total_disbursed': financial_metrics.get('total_disbursed', 0.0),
                'disbursement_rate': financial_metrics.get('disbursement_rate', 0.0),
                'remaining_funds': financial_metrics.get('remaining_funds', 0.0)
            }
            
        # Extract key metrics from impact
        impact_metrics = metrics_values.get('impact', {})
        if impact_metrics:
            summary['impact'] = {
                'total_damage_estimate': impact_metrics.get('total_damage_estimate', 0.0),
                'affected_population': impact_metrics.get('affected_population', 0),
                'beneficiaries': impact_metrics.get('beneficiaries', 0)
            }
            
        # Add overall recovery index (0-100)
        if recovery_metrics and financial_metrics:
            # Simple weighted average of completion and disbursement rates
            completion = recovery_metrics.get('average_completion', 0.0)
            disbursement = financial_metrics.get('disbursement_rate', 0.0)
            
            recovery_index = (completion * 0.6) + (disbursement * 0.4)
            summary['recovery_index'] = min(100, recovery_index)
            
        return summary
    
    def _determine_overall_recovery_phase(self, projects: List[RecoveryProject]) -> str:
        """
        Determine the overall recovery phase from projects.
        
        Args:
            projects: List of recovery projects
            
        Returns:
            Overall recovery phase
        """
        if not projects:
            return RecoveryPhase.INITIAL_RESPONSE.value
            
        # Count projects in each phase
        phase_counts = {}
        
        for project in projects:
            phase = getattr(project, 'phase', 'unknown')
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
            
        # Calculate weighted phase value
        weighted_phases = 0.0
        total_weight = 0.0
        
        phase_values = {
            RecoveryPhase.INITIAL_RESPONSE.value: 1.0,
            RecoveryPhase.SHORT_TERM_RECOVERY.value: 2.0,
            RecoveryPhase.INTERMEDIATE_RECOVERY.value: 3.0,
            RecoveryPhase.LONG_TERM_RECOVERY.value: 4.0,
            RecoveryPhase.COMPLETED.value: 5.0
        }
        
        for phase, count in phase_counts.items():
            if phase in phase_values:
                weighted_phases += phase_values[phase] * count
                total_weight += count
                
        if total_weight == 0:
            return RecoveryPhase.INITIAL_RESPONSE.value
            
        average_phase = weighted_phases / total_weight
        
        # Map average back to phase
        if average_phase < 1.5:
            return RecoveryPhase.INITIAL_RESPONSE.value
        elif average_phase < 2.5:
            return RecoveryPhase.SHORT_TERM_RECOVERY.value
        elif average_phase < 3.5:
            return RecoveryPhase.INTERMEDIATE_RECOVERY.value
        elif average_phase < 4.5:
            return RecoveryPhase.LONG_TERM_RECOVERY.value
        else:
            return RecoveryPhase.COMPLETED.value