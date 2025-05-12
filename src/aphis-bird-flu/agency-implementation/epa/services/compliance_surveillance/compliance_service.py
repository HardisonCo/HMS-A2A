"""
Compliance Surveillance Service for the EPA implementation.

This service provides functionality for monitoring regulatory compliance
of facilities, managing permits, conducting inspections, and enforcing
environmental regulations.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import logging
import uuid

from agency_implementation.epa.models.compliance import (
    RegulatedFacility, Permit, ComplianceInspection, 
    EnforcementAction, ComplianceReport
)
from agency_implementation.epa.models.base import ComplianceStatus, RegulatoryFramework
from .repository import (
    RegulatedFacilityRepository, PermitRepository,
    ComplianceInspectionRepository, EnforcementActionRepository
)
from .adapters import FacilityRegistryAdapter, ComplianceReportingAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceSurveillanceService:
    """
    Service for regulatory compliance surveillance.
    
    This service provides functionality for:
    1. Regulated facility management
    2. Permit issuance and tracking
    3. Compliance inspections
    4. Enforcement actions
    5. Compliance reporting and analysis
    """
    
    def __init__(
        self,
        facility_repository: RegulatedFacilityRepository,
        permit_repository: PermitRepository,
        inspection_repository: ComplianceInspectionRepository,
        enforcement_repository: EnforcementActionRepository,
        facility_registry_adapter: Optional[FacilityRegistryAdapter] = None,
        compliance_reporting_adapter: Optional[ComplianceReportingAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the service.
        
        Args:
            facility_repository: Repository for regulated facilities
            permit_repository: Repository for permits
            inspection_repository: Repository for compliance inspections
            enforcement_repository: Repository for enforcement actions
            facility_registry_adapter: Adapter for facility registry integration
            compliance_reporting_adapter: Adapter for compliance reporting
            config: Service configuration
        """
        self.facility_repository = facility_repository
        self.permit_repository = permit_repository
        self.inspection_repository = inspection_repository
        self.enforcement_repository = enforcement_repository
        self.facility_registry_adapter = facility_registry_adapter
        self.compliance_reporting_adapter = compliance_reporting_adapter
        self.config = config or {}
        
        # Initialize compliance thresholds
        self.violation_thresholds = self.config.get('violation_thresholds', {
            'minor': 1,  # 1+ minor findings
            'significant': 3,  # 3+ minor findings or 1+ significant findings
            'severe': 1,  # 1+ severe findings
        })
        
        # Initialize inspection frequency based on facility risk
        self.inspection_frequency = self.config.get('inspection_frequency', {
            'high_risk': 6,  # months
            'medium_risk': 12,  # months
            'low_risk': 24,  # months
        })
        
        logger.info("ComplianceSurveillanceService initialized")
    
    # Facility Management Methods
    
    def get_facility(self, facility_id: str) -> Optional[RegulatedFacility]:
        """
        Get a regulated facility by ID.
        
        Args:
            facility_id: The ID of the facility to retrieve
            
        Returns:
            The facility if found, None otherwise
        """
        return self.facility_repository.get_by_id(facility_id)
    
    def get_all_facilities(self) -> List[RegulatedFacility]:
        """
        Get all regulated facilities.
        
        Returns:
            List of all facilities
        """
        return self.facility_repository.get_all()
    
    def create_facility(self, facility_data: Dict[str, Any]) -> RegulatedFacility:
        """
        Create a new regulated facility.
        
        Args:
            facility_data: Dictionary with facility data
            
        Returns:
            The created facility
            
        Raises:
            ValueError: If facility data is invalid
        """
        # Validate required fields
        required_fields = ['facility_name', 'facility_type', 'location']
        for field in required_fields:
            if field not in facility_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create the facility
        facility = RegulatedFacility(**facility_data)
        
        # Save the facility
        created_facility = self.facility_repository.create(facility)
        
        logger.info(f"Created new regulated facility with ID: {created_facility.id}")
        return created_facility
    
    def update_facility(self, facility_id: str, updates: Dict[str, Any]) -> Optional[RegulatedFacility]:
        """
        Update an existing regulated facility.
        
        Args:
            facility_id: ID of the facility to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated facility or None if facility not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the facility
        facility = self.facility_repository.get_by_id(facility_id)
        if not facility:
            logger.warning(f"Facility not found for update: {facility_id}")
            return None
        
        # Update the facility
        for key, value in updates.items():
            setattr(facility, key, value)
            
        # Update timestamp
        facility.updated_at = datetime.now().isoformat()
        
        # Save the updated facility
        updated_facility = self.facility_repository.update(facility)
        
        logger.info(f"Updated facility with ID: {facility_id}")
        return updated_facility
    
    def find_facilities_by_type(self, facility_type: str) -> List[RegulatedFacility]:
        """
        Find facilities by type.
        
        Args:
            facility_type: Type of facility
            
        Returns:
            List of facilities of the specified type
        """
        return self.facility_repository.find_by_facility_type(facility_type)
    
    def find_facilities_in_region(self, region: str) -> List[RegulatedFacility]:
        """
        Find facilities in a specific EPA region.
        
        Args:
            region: EPA region code
            
        Returns:
            List of facilities in the specified region
        """
        return self.facility_repository.find_by_region(region)
    
    def find_facilities_by_program(self, program: str) -> List[RegulatedFacility]:
        """
        Find facilities participating in a specific regulatory program.
        
        Args:
            program: Regulatory program code
            
        Returns:
            List of facilities in the program
        """
        return self.facility_repository.find_by_regulatory_program(program)
    
    def import_facilities_from_registry(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Import facilities from an external facility registry.
        
        Args:
            params: Parameters for the import (e.g., region, facility type)
            
        Returns:
            Dictionary with import results
            
        Raises:
            RuntimeError: If facility registry adapter is not configured
        """
        if not self.facility_registry_adapter:
            raise RuntimeError("Facility registry adapter not configured")
        
        params = params or {}
        logger.info(f"Importing facilities from registry with params: {params}")
        
        # Fetch data from facility registry
        registry_data = self.facility_registry_adapter.fetch_data(**params)
        
        # Process results
        imported_count = 0
        updated_count = 0
        errors = []
        
        for record in registry_data:
            try:
                # Convert to facility
                facility = self.facility_registry_adapter.convert_to_facility(record)
                if not facility:
                    errors.append(f"Failed to convert record: {record.get('id', 'unknown')}")
                    continue
                
                # Check if facility already exists (by registry ID)
                registry_id = record.get('registry_id')
                if registry_id:
                    existing_facilities = self.facility_repository.find({
                        'registry_id': registry_id
                    })
                    
                    if existing_facilities:
                        # Update existing facility
                        existing_facility = existing_facilities[0]
                        
                        # Preserve ID and created_at
                        facility_dict = facility.to_dict()
                        facility_dict['id'] = existing_facility.id
                        facility_dict['created_at'] = existing_facility.created_at
                        
                        # Update the facility
                        for key, value in facility_dict.items():
                            if key not in ['id', 'created_at']:
                                setattr(existing_facility, key, value)
                        
                        existing_facility.updated_at = datetime.now().isoformat()
                        self.facility_repository.update(existing_facility)
                        updated_count += 1
                    else:
                        # Create new facility
                        self.facility_repository.create(facility)
                        imported_count += 1
                else:
                    # Create new facility without registry ID
                    self.facility_repository.create(facility)
                    imported_count += 1
                
            except Exception as e:
                error_msg = f"Error processing record {record.get('id', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            'total_records': len(registry_data),
            'imported_count': imported_count,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors[:10]  # Limit error list to avoid huge responses
        }
        
        logger.info(f"Registry import complete: {imported_count} facilities imported, {updated_count} updated, {len(errors)} errors")
        return result
    
    # Permit Management Methods
    
    def get_permit(self, permit_id: str) -> Optional[Permit]:
        """
        Get a permit by ID.
        
        Args:
            permit_id: The ID of the permit to retrieve
            
        Returns:
            The permit if found, None otherwise
        """
        return self.permit_repository.get_by_id(permit_id)
    
    def get_facility_permits(self, facility_id: str) -> List[Permit]:
        """
        Get all permits for a facility.
        
        Args:
            facility_id: ID of the facility
            
        Returns:
            List of permits for the facility
            
        Raises:
            ValueError: If facility does not exist
        """
        # Check facility exists
        facility = self.facility_repository.get_by_id(facility_id)
        if not facility:
            raise ValueError(f"Facility with ID {facility_id} does not exist")
        
        return self.permit_repository.find_by_facility_id(facility_id)
    
    def create_permit(self, permit_data: Dict[str, Any]) -> Permit:
        """
        Create a new permit.
        
        Args:
            permit_data: Dictionary with permit data
            
        Returns:
            The created permit
            
        Raises:
            ValueError: If permit data is invalid or facility does not exist
        """
        # Validate required fields
        required_fields = ['permit_number', 'facility_id', 'permit_type', 
                          'regulatory_framework', 'issuance_date', 'expiration_date']
        for field in required_fields:
            if field not in permit_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check facility exists
        facility = self.facility_repository.get_by_id(permit_data['facility_id'])
        if not facility:
            raise ValueError(f"Facility with ID {permit_data['facility_id']} does not exist")
        
        # Create the permit
        permit = Permit(**permit_data)
        
        # Save the permit
        created_permit = self.permit_repository.create(permit)
        
        # Update facility's permit IDs if needed
        if hasattr(facility, 'permit_ids'):
            if not facility.permit_ids:
                facility.permit_ids = []
            if created_permit.id not in facility.permit_ids:
                facility.permit_ids.append(created_permit.id)
                self.facility_repository.update(facility)
        
        logger.info(f"Created new permit with ID: {created_permit.id}")
        return created_permit
    
    def update_permit(self, permit_id: str, updates: Dict[str, Any]) -> Optional[Permit]:
        """
        Update an existing permit.
        
        Args:
            permit_id: ID of the permit to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated permit or None if permit not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the permit
        permit = self.permit_repository.get_by_id(permit_id)
        if not permit:
            logger.warning(f"Permit not found for update: {permit_id}")
            return None
        
        # Update the permit
        for key, value in updates.items():
            setattr(permit, key, value)
            
        # Update timestamp
        permit.updated_at = datetime.now().isoformat()
        
        # Save the updated permit
        updated_permit = self.permit_repository.update(permit)
        
        logger.info(f"Updated permit with ID: {permit_id}")
        return updated_permit
    
    def find_permits_by_type(self, permit_type: str) -> List[Permit]:
        """
        Find permits by type.
        
        Args:
            permit_type: Type of permit
            
        Returns:
            List of permits of the specified type
        """
        return self.permit_repository.find_by_permit_type(permit_type)
    
    def find_permits_by_framework(self, framework: Union[RegulatoryFramework, str]) -> List[Permit]:
        """
        Find permits by regulatory framework.
        
        Args:
            framework: Regulatory framework
            
        Returns:
            List of permits under the specified framework
        """
        return self.permit_repository.find_by_regulatory_framework(framework)
    
    def find_expiring_permits(self, days_threshold: int = 90) -> List[Permit]:
        """
        Find permits expiring within the specified number of days.
        
        Args:
            days_threshold: Number of days until expiration
            
        Returns:
            List of permits expiring within the threshold
        """
        return self.permit_repository.find_expiring_permits(days_threshold)
    
    # Inspection Management Methods
    
    def get_inspection(self, inspection_id: str) -> Optional[ComplianceInspection]:
        """
        Get a compliance inspection by ID.
        
        Args:
            inspection_id: The ID of the inspection to retrieve
            
        Returns:
            The inspection if found, None otherwise
        """
        return self.inspection_repository.get_by_id(inspection_id)
    
    def get_facility_inspections(self, facility_id: str) -> List[ComplianceInspection]:
        """
        Get all inspections for a facility.
        
        Args:
            facility_id: ID of the facility
            
        Returns:
            List of inspections for the facility
            
        Raises:
            ValueError: If facility does not exist
        """
        # Check facility exists
        facility = self.facility_repository.get_by_id(facility_id)
        if not facility:
            raise ValueError(f"Facility with ID {facility_id} does not exist")
        
        return self.inspection_repository.find_by_facility_id(facility_id)
    
    def create_inspection(self, inspection_data: Dict[str, Any]) -> ComplianceInspection:
        """
        Create a new compliance inspection.
        
        Args:
            inspection_data: Dictionary with inspection data
            
        Returns:
            The created inspection
            
        Raises:
            ValueError: If inspection data is invalid or facility does not exist
        """
        # Validate required fields
        required_fields = ['facility_id', 'inspection_date', 'inspector_id', 
                          'inspection_type', 'regulatory_framework']
        for field in required_fields:
            if field not in inspection_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check facility exists
        facility = self.facility_repository.get_by_id(inspection_data['facility_id'])
        if not facility:
            raise ValueError(f"Facility with ID {inspection_data['facility_id']} does not exist")
        
        # Create the inspection
        inspection = ComplianceInspection(**inspection_data)
        
        # Save the inspection
        created_inspection = self.inspection_repository.create(inspection)
        
        logger.info(f"Created new compliance inspection with ID: {created_inspection.id}")
        return created_inspection
    
    def update_inspection(self, inspection_id: str, updates: Dict[str, Any]) -> Optional[ComplianceInspection]:
        """
        Update an existing inspection.
        
        Args:
            inspection_id: ID of the inspection to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated inspection or None if inspection not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the inspection
        inspection = self.inspection_repository.get_by_id(inspection_id)
        if not inspection:
            logger.warning(f"Inspection not found for update: {inspection_id}")
            return None
        
        # Update the inspection
        for key, value in updates.items():
            setattr(inspection, key, value)
            
        # Update timestamp
        inspection.updated_at = datetime.now().isoformat()
        
        # Save the updated inspection
        updated_inspection = self.inspection_repository.update(inspection)
        
        logger.info(f"Updated inspection with ID: {inspection_id}")
        return updated_inspection
    
    def add_inspection_finding(
        self, 
        inspection_id: str, 
        finding_type: str, 
        description: str, 
        severity: str, 
        regulation_cited: str = None
    ) -> Optional[ComplianceInspection]:
        """
        Add a finding to an inspection.
        
        Args:
            inspection_id: ID of the inspection
            finding_type: Type of finding
            description: Description of the finding
            severity: Severity of the finding
            regulation_cited: Optional regulation citation
            
        Returns:
            The updated inspection or None if inspection not found
        """
        # Get the inspection
        inspection = self.inspection_repository.get_by_id(inspection_id)
        if not inspection:
            logger.warning(f"Inspection not found for adding finding: {inspection_id}")
            return None
        
        # Add the finding
        if not hasattr(inspection, 'add_finding'):
            logger.warning(f"Inspection {inspection_id} does not support add_finding method")
            # Fallback to manual addition
            if not hasattr(inspection, 'findings'):
                inspection.findings = []
                
            inspection.findings.append({
                "finding_type": finding_type,
                "description": description,
                "severity": severity,
                "regulation_cited": regulation_cited,
                "timestamp": datetime.now().isoformat()
            })
        else:
            inspection.add_finding(finding_type, description, severity, regulation_cited)
        
        # Determine compliance status based on findings
        self._update_compliance_status(inspection)
        
        # Save the updated inspection
        updated_inspection = self.inspection_repository.update(inspection)
        
        logger.info(f"Added finding to inspection with ID: {inspection_id}")
        return updated_inspection
    
    def recommend_inspections(self) -> List[Dict[str, Any]]:
        """
        Recommend facilities for inspection based on risk factors.
        
        Returns:
            List of recommended facilities with risk information
        """
        # Get all facilities
        facilities = self.facility_repository.get_all()
        
        # Get all inspections
        inspections = self.inspection_repository.get_all()
        
        # Group inspections by facility
        inspections_by_facility = {}
        for inspection in inspections:
            if hasattr(inspection, 'facility_id'):
                facility_id = inspection.facility_id
                if facility_id not in inspections_by_facility:
                    inspections_by_facility[facility_id] = []
                inspections_by_facility[facility_id].append(inspection)
        
        # Get all enforcement actions
        enforcement_actions = self.enforcement_repository.get_all()
        
        # Group enforcement actions by facility
        actions_by_facility = {}
        for action in enforcement_actions:
            if hasattr(action, 'facility_id'):
                facility_id = action.facility_id
                if facility_id not in actions_by_facility:
                    actions_by_facility[facility_id] = []
                actions_by_facility[facility_id].append(action)
        
        # Calculate risk factors and last inspection date for each facility
        recommendations = []
        
        for facility in facilities:
            # Skip inactive facilities
            if hasattr(facility, 'operating_status') and facility.operating_status != "ACTIVE":
                continue
                
            facility_id = facility.id
            
            # Get facility inspections
            facility_inspections = inspections_by_facility.get(facility_id, [])
            
            # Get facility enforcement actions
            facility_actions = actions_by_facility.get(facility_id, [])
            
            # Calculate last inspection date
            last_inspection_date = None
            if facility_inspections:
                # Sort by inspection date descending
                sorted_inspections = sorted(
                    facility_inspections,
                    key=lambda x: x.inspection_date if hasattr(x, 'inspection_date') else '1900-01-01',
                    reverse=True
                )
                last_inspection = sorted_inspections[0]
                last_inspection_date = last_inspection.inspection_date if hasattr(last_inspection, 'inspection_date') else None
            
            # Calculate risk factors
            num_violations = 0
            num_significant_violations = 0
            num_enforcement_actions = len(facility_actions)
            
            for inspection in facility_inspections:
                if hasattr(inspection, 'compliance_status'):
                    if inspection.compliance_status in [
                        ComplianceStatus.SIGNIFICANT_VIOLATION.value, 
                        ComplianceStatus.SEVERE_VIOLATION.value
                    ]:
                        num_significant_violations += 1
                    elif inspection.compliance_status == ComplianceStatus.MINOR_VIOLATION.value:
                        num_violations += 1
            
            # Determine risk level
            risk_level = 'low_risk'
            if num_significant_violations > 0 or num_enforcement_actions > 2:
                risk_level = 'high_risk'
            elif num_violations > 2 or num_enforcement_actions > 0:
                risk_level = 'medium_risk'
            
            # Calculate months since last inspection
            months_since_last_inspection = None
            if last_inspection_date:
                if isinstance(last_inspection_date, str):
                    last_inspection_date = datetime.fromisoformat(last_inspection_date)
                
                today = datetime.now().date()
                last_date = last_inspection_date.date() if isinstance(last_inspection_date, datetime) else last_inspection_date
                days_diff = (today - last_date).days
                months_since_last_inspection = days_diff / 30  # Approximation
            
            # Determine if inspection is due
            inspection_due = False
            inspection_frequency_months = self.inspection_frequency.get(risk_level, 12)
            
            if months_since_last_inspection is None:
                # No previous inspection, so it's due
                inspection_due = True
            elif months_since_last_inspection >= inspection_frequency_months:
                # It's been longer than the frequency, so it's due
                inspection_due = True
            
            if inspection_due:
                recommendation = {
                    'facility_id': facility_id,
                    'facility_name': facility.facility_name if hasattr(facility, 'facility_name') else 'Unknown',
                    'facility_type': facility.facility_type if hasattr(facility, 'facility_type') else 'Unknown',
                    'risk_level': risk_level,
                    'last_inspection_date': last_inspection_date.isoformat() if last_inspection_date else None,
                    'months_since_last_inspection': months_since_last_inspection,
                    'num_violations': num_violations,
                    'num_significant_violations': num_significant_violations,
                    'num_enforcement_actions': num_enforcement_actions,
                    'recommended_inspection_type': 'Comprehensive' if risk_level == 'high_risk' else 'Routine',
                    'priority': 'High' if risk_level == 'high_risk' else 'Medium' if risk_level == 'medium_risk' else 'Low'
                }
                
                recommendations.append(recommendation)
        
        # Sort recommendations by priority (High, Medium, Low) and then by months since last inspection
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        recommendations.sort(key=lambda x: (
            priority_order.get(x['priority'], 3),
            float('inf') if x['months_since_last_inspection'] is None else -x['months_since_last_inspection']
        ))
        
        return recommendations
    
    # Enforcement Action Methods
    
    def get_enforcement_action(self, action_id: str) -> Optional[EnforcementAction]:
        """
        Get an enforcement action by ID.
        
        Args:
            action_id: The ID of the action to retrieve
            
        Returns:
            The action if found, None otherwise
        """
        return self.enforcement_repository.get_by_id(action_id)
    
    def get_facility_enforcement_actions(self, facility_id: str) -> List[EnforcementAction]:
        """
        Get all enforcement actions for a facility.
        
        Args:
            facility_id: ID of the facility
            
        Returns:
            List of enforcement actions for the facility
            
        Raises:
            ValueError: If facility does not exist
        """
        # Check facility exists
        facility = self.facility_repository.get_by_id(facility_id)
        if not facility:
            raise ValueError(f"Facility with ID {facility_id} does not exist")
        
        return self.enforcement_repository.find_by_facility_id(facility_id)
    
    def create_enforcement_action(self, action_data: Dict[str, Any]) -> EnforcementAction:
        """
        Create a new enforcement action.
        
        Args:
            action_data: Dictionary with enforcement action data
            
        Returns:
            The created enforcement action
            
        Raises:
            ValueError: If action data is invalid or facility does not exist
        """
        # Validate required fields
        required_fields = ['facility_id', 'action_type', 'violation_description', 
                          'regulatory_framework', 'issuance_date']
        for field in required_fields:
            if field not in action_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check facility exists
        facility = self.facility_repository.get_by_id(action_data['facility_id'])
        if not facility:
            raise ValueError(f"Facility with ID {action_data['facility_id']} does not exist")
        
        # Create the enforcement action
        action = EnforcementAction(**action_data)
        
        # Save the enforcement action
        created_action = self.enforcement_repository.create(action)
        
        # Send to reporting system if adapter configured
        if self.compliance_reporting_adapter:
            try:
                report_data = self._format_action_for_reporting(created_action, facility)
                self.compliance_reporting_adapter.send_data(report_data)
                logger.info(f"Enforcement action {created_action.id} reported to compliance system")
            except Exception as e:
                logger.error(f"Error reporting enforcement action {created_action.id}: {str(e)}")
        
        logger.info(f"Created new enforcement action with ID: {created_action.id}")
        return created_action
    
    def update_enforcement_action(self, action_id: str, updates: Dict[str, Any]) -> Optional[EnforcementAction]:
        """
        Update an existing enforcement action.
        
        Args:
            action_id: ID of the action to update
            updates: Dictionary with fields to update
            
        Returns:
            The updated action or None if action not found
            
        Raises:
            ValueError: If updates are invalid
        """
        # Get the action
        action = self.enforcement_repository.get_by_id(action_id)
        if not action:
            logger.warning(f"Enforcement action not found for update: {action_id}")
            return None
        
        # Update the action
        for key, value in updates.items():
            setattr(action, key, value)
            
        # Update timestamp
        action.updated_at = datetime.now().isoformat()
        
        # Save the updated action
        updated_action = self.enforcement_repository.update(action)
        
        logger.info(f"Updated enforcement action with ID: {action_id}")
        return updated_action
    
    def resolve_enforcement_action(
        self, 
        action_id: str, 
        resolution_date: str, 
        resolution_details: str, 
        final_penalty: float = None
    ) -> Optional[EnforcementAction]:
        """
        Resolve an enforcement action.
        
        Args:
            action_id: ID of the action to resolve
            resolution_date: Date of resolution
            resolution_details: Details of the resolution
            final_penalty: Optional final penalty amount
            
        Returns:
            The updated action or None if action not found
            
        Raises:
            ValueError: If action is already resolved
        """
        # Get the action
        action = self.enforcement_repository.get_by_id(action_id)
        if not action:
            logger.warning(f"Enforcement action not found for resolution: {action_id}")
            return None
        
        # Check if action is already resolved
        if hasattr(action, 'status') and action.status == "RESOLVED":
            raise ValueError(f"Enforcement action {action_id} is already resolved")
        
        # Resolve the action
        if hasattr(action, 'resolve_action'):
            action.resolve_action(resolution_date, resolution_details, final_penalty)
        else:
            # Fallback if method not available
            action.status = "RESOLVED"
            action.resolution_date = resolution_date
            action.resolution_details = resolution_details
            if final_penalty is not None:
                action.final_penalty = final_penalty
        
        # Save the updated action
        updated_action = self.enforcement_repository.update(action)
        
        # Send to reporting system if adapter configured
        if self.compliance_reporting_adapter:
            try:
                facility = self.facility_repository.get_by_id(updated_action.facility_id)
                report_data = self._format_action_for_reporting(updated_action, facility, is_resolution=True)
                self.compliance_reporting_adapter.send_data(report_data)
                logger.info(f"Enforcement action resolution for {updated_action.id} reported to compliance system")
            except Exception as e:
                logger.error(f"Error reporting enforcement action resolution for {updated_action.id}: {str(e)}")
        
        logger.info(f"Resolved enforcement action with ID: {action_id}")
        return updated_action
    
    def add_corrective_action(
        self, 
        action_id: str, 
        description: str, 
        deadline: str, 
        requirements: str = None
    ) -> Optional[EnforcementAction]:
        """
        Add a corrective action to an enforcement action.
        
        Args:
            action_id: ID of the enforcement action
            description: Description of the corrective action
            deadline: Deadline for completing the corrective action
            requirements: Optional specific requirements
            
        Returns:
            The updated action or None if action not found
        """
        # Get the action
        action = self.enforcement_repository.get_by_id(action_id)
        if not action:
            logger.warning(f"Enforcement action not found for adding corrective action: {action_id}")
            return None
        
        # Check if action is resolved
        if hasattr(action, 'status') and action.status == "RESOLVED":
            raise ValueError(f"Cannot add corrective action to resolved enforcement action {action_id}")
        
        # Add corrective action
        if hasattr(action, 'add_corrective_action'):
            action.add_corrective_action(description, deadline, requirements)
        else:
            # Fallback if method not available
            if not hasattr(action, 'corrective_actions'):
                action.corrective_actions = []
                
            action.corrective_actions.append({
                "description": description,
                "deadline": deadline,
                "requirements": requirements,
                "status": "PENDING"
            })
        
        # Save the updated action
        updated_action = self.enforcement_repository.update(action)
        
        logger.info(f"Added corrective action to enforcement action with ID: {action_id}")
        return updated_action
    
    # Analysis Methods
    
    def generate_compliance_history(self, facility_id: str) -> Dict[str, Any]:
        """
        Generate compliance history for a facility.
        
        Args:
            facility_id: ID of the facility
            
        Returns:
            Dictionary with compliance history
            
        Raises:
            ValueError: If facility does not exist
        """
        # Check facility exists
        facility = self.facility_repository.get_by_id(facility_id)
        if not facility:
            raise ValueError(f"Facility with ID {facility_id} does not exist")
        
        # Get facility inspections
        inspections = self.inspection_repository.find_by_facility_id(facility_id)
        
        # Get facility enforcement actions
        enforcement_actions = self.enforcement_repository.find_by_facility_id(facility_id)
        
        # Sort inspections by date
        inspections = sorted(
            inspections,
            key=lambda x: x.inspection_date if hasattr(x, 'inspection_date') else '1900-01-01'
        )
        
        # Sort enforcement actions by date
        enforcement_actions = sorted(
            enforcement_actions,
            key=lambda x: x.issuance_date if hasattr(x, 'issuance_date') else '1900-01-01'
        )
        
        # Calculate compliance statistics
        total_inspections = len(inspections)
        compliant_inspections = 0
        minor_violations = 0
        significant_violations = 0
        severe_violations = 0
        
        for inspection in inspections:
            if hasattr(inspection, 'compliance_status'):
                if inspection.compliance_status == ComplianceStatus.COMPLIANT.value:
                    compliant_inspections += 1
                elif inspection.compliance_status == ComplianceStatus.MINOR_VIOLATION.value:
                    minor_violations += 1
                elif inspection.compliance_status == ComplianceStatus.SIGNIFICANT_VIOLATION.value:
                    significant_violations += 1
                elif inspection.compliance_status == ComplianceStatus.SEVERE_VIOLATION.value:
                    severe_violations += 1
        
        # Calculate enforcement statistics
        total_enforcement_actions = len(enforcement_actions)
        resolved_actions = 0
        pending_actions = 0
        total_penalties = 0.0
        
        for action in enforcement_actions:
            if hasattr(action, 'status'):
                if action.status == "RESOLVED":
                    resolved_actions += 1
                else:
                    pending_actions += 1
            
            # Sum penalties
            if hasattr(action, 'final_penalty') and action.final_penalty is not None:
                total_penalties += action.final_penalty
            elif hasattr(action, 'proposed_penalty') and action.proposed_penalty is not None:
                total_penalties += action.proposed_penalty
        
        # Build timeline of events
        timeline = []
        
        for inspection in inspections:
            inspection_date = inspection.inspection_date
            if isinstance(inspection_date, str):
                inspection_date = datetime.fromisoformat(inspection_date).date().isoformat()
            
            event = {
                "date": inspection_date,
                "type": "inspection",
                "id": inspection.id,
                "description": f"{inspection.inspection_type} Inspection",
                "status": inspection.compliance_status if hasattr(inspection, 'compliance_status') else "Unknown",
                "details": {}
            }
            
            # Add findings if available
            if hasattr(inspection, 'findings') and inspection.findings:
                event["details"]["findings"] = len(inspection.findings)
                event["details"]["finding_summary"] = ", ".join(
                    [f.get('finding_type', 'Unknown') for f in inspection.findings[:3]]
                )
                if len(inspection.findings) > 3:
                    event["details"]["finding_summary"] += f", and {len(inspection.findings) - 3} more"
            
            timeline.append(event)
        
        for action in enforcement_actions:
            issuance_date = action.issuance_date
            if isinstance(issuance_date, str):
                issuance_date = datetime.fromisoformat(issuance_date).date().isoformat()
            
            event = {
                "date": issuance_date,
                "type": "enforcement",
                "id": action.id,
                "description": f"{action.action_type} Enforcement Action",
                "status": action.status if hasattr(action, 'status') else "Unknown",
                "details": {}
            }
            
            # Add penalty if available
            if hasattr(action, 'proposed_penalty') and action.proposed_penalty is not None:
                event["details"]["proposed_penalty"] = action.proposed_penalty
            
            if hasattr(action, 'final_penalty') and action.final_penalty is not None:
                event["details"]["final_penalty"] = action.final_penalty
            
            # Add violation description if available
            if hasattr(action, 'violation_description'):
                event["details"]["violation"] = action.violation_description
            
            # Add resolution details if available
            if hasattr(action, 'resolution_date') and action.resolution_date:
                resolution_date = action.resolution_date
                if isinstance(resolution_date, str):
                    resolution_date = datetime.fromisoformat(resolution_date).date().isoformat()
                
                event["details"]["resolution_date"] = resolution_date
                
                if hasattr(action, 'resolution_details'):
                    event["details"]["resolution"] = action.resolution_details
            
            timeline.append(event)
        
        # Sort timeline by date
        timeline = sorted(timeline, key=lambda x: x["date"])
        
        # Calculate compliance rate
        compliance_rate = 0
        if total_inspections > 0:
            compliance_rate = (compliant_inspections / total_inspections) * 100
        
        # Determine current compliance status
        current_compliance_status = "Compliant"
        if pending_actions > 0:
            current_compliance_status = "Under Enforcement"
        elif severe_violations > 0:
            current_compliance_status = "Severe Violations"
        elif significant_violations > 0:
            current_compliance_status = "Significant Violations"
        elif minor_violations > 0:
            current_compliance_status = "Minor Violations"
        
        # Build result
        result = {
            "facility_id": facility_id,
            "facility_name": facility.facility_name if hasattr(facility, 'facility_name') else "Unknown",
            "facility_type": facility.facility_type if hasattr(facility, 'facility_type') else "Unknown",
            "inspection_summary": {
                "total_inspections": total_inspections,
                "compliant_inspections": compliant_inspections,
                "minor_violations": minor_violations,
                "significant_violations": significant_violations,
                "severe_violations": severe_violations,
                "compliance_rate": compliance_rate
            },
            "enforcement_summary": {
                "total_actions": total_enforcement_actions,
                "resolved_actions": resolved_actions,
                "pending_actions": pending_actions,
                "total_penalties": total_penalties
            },
            "current_compliance_status": current_compliance_status,
            "timeline": timeline
        }
        
        return result
    
    def generate_regional_compliance_report(
        self, 
        region: str, 
        start_date: Union[date, str] = None, 
        end_date: Union[date, str] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report for a specific EPA region.
        
        Args:
            region: EPA region code
            start_date: Optional start date for the report period
            end_date: Optional end date for the report period
            
        Returns:
            Dictionary with regional compliance report
        """
        # Set default date range if not provided
        if end_date is None:
            end_date = datetime.now().date()
        elif isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
            
        if start_date is None:
            start_date = end_date - timedelta(days=365)  # One year
        elif isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        
        # Get facilities in the region
        facilities = self.facility_repository.find_by_region(region)
        
        # Get all inspections in the date range
        all_inspections = []
        for inspection in self.inspection_repository.get_all():
            if not hasattr(inspection, 'inspection_date'):
                continue
                
            inspection_date = inspection.inspection_date
            if isinstance(inspection_date, str):
                inspection_date = datetime.fromisoformat(inspection_date).date()
                
            if start_date <= inspection_date <= end_date:
                all_inspections.append(inspection)
        
        # Filter inspections for facilities in the region
        region_inspections = []
        for inspection in all_inspections:
            if hasattr(inspection, 'facility_id'):
                facility_id = inspection.facility_id
                if any(f.id == facility_id for f in facilities):
                    region_inspections.append(inspection)
        
        # Get all enforcement actions in the date range
        all_actions = []
        for action in self.enforcement_repository.get_all():
            if not hasattr(action, 'issuance_date'):
                continue
                
            issuance_date = action.issuance_date
            if isinstance(issuance_date, str):
                issuance_date = datetime.fromisoformat(issuance_date).date()
                
            if start_date <= issuance_date <= end_date:
                all_actions.append(action)
        
        # Filter enforcement actions for facilities in the region
        region_actions = []
        for action in all_actions:
            if hasattr(action, 'facility_id'):
                facility_id = action.facility_id
                if any(f.id == facility_id for f in facilities):
                    region_actions.append(action)
        
        # Calculate compliance statistics
        total_facilities = len(facilities)
        active_facilities = len([f for f in facilities 
                               if hasattr(f, 'operating_status') and f.operating_status == "ACTIVE"])
        
        total_inspections = len(region_inspections)
        compliant_inspections = 0
        minor_violations = 0
        significant_violations = 0
        severe_violations = 0
        
        for inspection in region_inspections:
            if hasattr(inspection, 'compliance_status'):
                if inspection.compliance_status == ComplianceStatus.COMPLIANT.value:
                    compliant_inspections += 1
                elif inspection.compliance_status == ComplianceStatus.MINOR_VIOLATION.value:
                    minor_violations += 1
                elif inspection.compliance_status == ComplianceStatus.SIGNIFICANT_VIOLATION.value:
                    significant_violations += 1
                elif inspection.compliance_status == ComplianceStatus.SEVERE_VIOLATION.value:
                    severe_violations += 1
        
        # Calculate enforcement statistics
        total_enforcement_actions = len(region_actions)
        resolved_actions = 0
        pending_actions = 0
        total_penalties = 0.0
        
        for action in region_actions:
            if hasattr(action, 'status'):
                if action.status == "RESOLVED":
                    resolved_actions += 1
                else:
                    pending_actions += 1
            
            # Sum penalties
            if hasattr(action, 'final_penalty') and action.final_penalty is not None:
                total_penalties += action.final_penalty
            elif hasattr(action, 'proposed_penalty') and action.proposed_penalty is not None:
                total_penalties += action.proposed_penalty
        
        # Group inspections by facility type
        inspections_by_type = {}
        for inspection in region_inspections:
            if hasattr(inspection, 'facility_id'):
                facility_id = inspection.facility_id
                facility = next((f for f in facilities if f.id == facility_id), None)
                
                if facility and hasattr(facility, 'facility_type'):
                    facility_type = facility.facility_type
                    if facility_type not in inspections_by_type:
                        inspections_by_type[facility_type] = []
                    
                    inspections_by_type[facility_type].append(inspection)
        
        type_summary = []
        for facility_type, inspections in inspections_by_type.items():
            type_compliant = 0
            type_violations = 0
            
            for inspection in inspections:
                if hasattr(inspection, 'compliance_status'):
                    if inspection.compliance_status == ComplianceStatus.COMPLIANT.value:
                        type_compliant += 1
                    else:
                        type_violations += 1
            
            compliance_rate = (type_compliant / len(inspections)) * 100 if len(inspections) > 0 else 0
            
            type_summary.append({
                "facility_type": facility_type,
                "inspection_count": len(inspections),
                "compliant_count": type_compliant,
                "violation_count": type_violations,
                "compliance_rate": compliance_rate
            })
        
        # Sort type summary by violation count (descending)
        type_summary = sorted(type_summary, key=lambda x: x["violation_count"], reverse=True)
        
        # Calculate overall compliance rate
        compliance_rate = 0
        if total_inspections > 0:
            compliance_rate = (compliant_inspections / total_inspections) * 100
        
        # Build result
        result = {
            "region": region,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "facility_summary": {
                "total_facilities": total_facilities,
                "active_facilities": active_facilities
            },
            "inspection_summary": {
                "total_inspections": total_inspections,
                "compliant_inspections": compliant_inspections,
                "minor_violations": minor_violations,
                "significant_violations": significant_violations,
                "severe_violations": severe_violations,
                "compliance_rate": compliance_rate
            },
            "enforcement_summary": {
                "total_actions": total_enforcement_actions,
                "resolved_actions": resolved_actions,
                "pending_actions": pending_actions,
                "total_penalties": total_penalties
            },
            "facility_type_summary": type_summary
        }
        
        return result
    
    # Helper methods
    
    def _update_compliance_status(self, inspection: ComplianceInspection) -> None:
        """
        Update compliance status of an inspection based on findings.
        
        Args:
            inspection: The inspection to update
        """
        if not hasattr(inspection, 'findings') or not inspection.findings:
            # No findings, so compliant
            inspection.compliance_status = ComplianceStatus.COMPLIANT.value
            return
        
        # Count findings by severity
        finding_counts = {
            'minor': 0,
            'significant': 0,
            'severe': 0
        }
        
        for finding in inspection.findings:
            severity = finding.get('severity', '').lower()
            if severity in finding_counts:
                finding_counts[severity] += 1
        
        # Determine compliance status based on findings
        if finding_counts['severe'] >= self.violation_thresholds.get('severe', 1):
            inspection.compliance_status = ComplianceStatus.SEVERE_VIOLATION.value
        elif finding_counts['significant'] >= self.violation_thresholds.get('significant', 1) or finding_counts['minor'] >= self.violation_thresholds.get('significant', 3):
            inspection.compliance_status = ComplianceStatus.SIGNIFICANT_VIOLATION.value
        elif finding_counts['minor'] >= self.violation_thresholds.get('minor', 1):
            inspection.compliance_status = ComplianceStatus.MINOR_VIOLATION.value
        else:
            inspection.compliance_status = ComplianceStatus.COMPLIANT.value
    
    def _format_action_for_reporting(
        self, 
        action: EnforcementAction, 
        facility: RegulatedFacility,
        is_resolution: bool = False
    ) -> Dict[str, Any]:
        """
        Format an enforcement action for reporting.
        
        Args:
            action: The enforcement action to format
            facility: The related facility
            is_resolution: Whether this is a resolution report
            
        Returns:
            Dictionary formatted for reporting adapter
        """
        # Basic report data
        report_data = {
            "report_id": f"ENF-{action.id}",
            "report_type": "ENFORCEMENT_RESOLUTION" if is_resolution else "ENFORCEMENT_ACTION",
            "report_date": datetime.now().isoformat(),
            "regulatory_framework": action.regulatory_framework if hasattr(action, 'regulatory_framework') else "Unknown",
            "action": {
                "id": action.id,
                "type": action.action_type if hasattr(action, 'action_type') else "Unknown",
                "issuance_date": action.issuance_date if hasattr(action, 'issuance_date') else None,
                "violation_description": action.violation_description if hasattr(action, 'violation_description') else None,
                "status": action.status if hasattr(action, 'status') else "PENDING"
            },
            "facility": {
                "id": facility.id,
                "name": facility.facility_name if hasattr(facility, 'facility_name') else "Unknown",
                "type": facility.facility_type if hasattr(facility, 'facility_type') else "Unknown",
                "location": facility.location.to_dict() if hasattr(facility, 'location') and hasattr(facility.location, 'to_dict') else None,
                "epa_region": facility.epa_region if hasattr(facility, 'epa_region') else None
            }
        }
        
        # Add inspection reference if available
        if hasattr(action, 'inspection_id') and action.inspection_id:
            report_data["action"]["inspection_id"] = action.inspection_id
        
        # Add penalty information if available
        if hasattr(action, 'proposed_penalty') and action.proposed_penalty is not None:
            report_data["action"]["proposed_penalty"] = action.proposed_penalty
            
        if hasattr(action, 'final_penalty') and action.final_penalty is not None:
            report_data["action"]["final_penalty"] = action.final_penalty
        
        # Add corrective actions if available
        if hasattr(action, 'corrective_actions') and action.corrective_actions:
            report_data["action"]["corrective_actions"] = action.corrective_actions
        
        # Add resolution information if this is a resolution report
        if is_resolution:
            if hasattr(action, 'resolution_date') and action.resolution_date:
                report_data["action"]["resolution_date"] = action.resolution_date
                
            if hasattr(action, 'resolution_details') and action.resolution_details:
                report_data["action"]["resolution_details"] = action.resolution_details
        
        return report_data