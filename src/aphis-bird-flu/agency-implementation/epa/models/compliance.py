"""
Compliance models for EPA implementation.
Defines domain models for regulatory compliance and enforcement.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from agency_implementation.foundation.base_models.base import BaseModel, GeoLocation, Address, ContactInfo
from agency_implementation.epa.models.base import ComplianceStatus, RegulatoryFramework


class RegulatedFacility(BaseModel):
    """
    Regulated industrial or commercial facility.
    Represents a facility that is subject to environmental regulations.
    """
    
    def __init__(
        self,
        facility_name: str,
        facility_type: str,
        location: Dict[str, Any],
        address: Dict[str, Any] = None,
        contact_info: Dict[str, Any] = None,
        epa_region: str = None,
        naics_code: str = None,
        permit_ids: List[str] = None,
        operating_status: str = "ACTIVE",
        first_operational_date: str = None,
        regulatory_programs: List[str] = None,
        **kwargs
    ):
        """Initialize regulated facility"""
        super().__init__(**kwargs)
        self.facility_name = facility_name
        self.facility_type = facility_type
        self.location = GeoLocation.from_dict(location) if isinstance(location, dict) else location
        self.address = Address.from_dict(address) if isinstance(address, dict) else address
        self.contact_info = ContactInfo.from_dict(contact_info) if isinstance(contact_info, dict) else contact_info
        self.epa_region = epa_region
        self.naics_code = naics_code
        self.permit_ids = permit_ids or []
        self.operating_status = operating_status
        self.first_operational_date = first_operational_date
        self.regulatory_programs = regulatory_programs or []


class Permit(BaseModel):
    """
    Environmental permit for a regulated facility.
    Represents authorization for specific activities with environmental impact.
    """
    
    def __init__(
        self,
        permit_number: str,
        facility_id: str,
        permit_type: str,
        regulatory_framework: str,
        issuance_date: str,
        expiration_date: str,
        status: str = "ACTIVE",
        permitted_activities: List[str] = None,
        permitted_pollutants: List[str] = None,
        limitations: Dict[str, Any] = None,
        reporting_requirements: List[str] = None,
        **kwargs
    ):
        """Initialize permit"""
        super().__init__(**kwargs)
        self.permit_number = permit_number
        self.facility_id = facility_id
        self.permit_type = permit_type
        self.regulatory_framework = regulatory_framework
        self.issuance_date = issuance_date
        self.expiration_date = expiration_date
        self.status = status
        self.permitted_activities = permitted_activities or []
        self.permitted_pollutants = permitted_pollutants or []
        self.limitations = limitations or {}
        self.reporting_requirements = reporting_requirements or []
    
    @property
    def is_active(self) -> bool:
        """Check if permit is currently active"""
        today = datetime.now().date()
        expiration = datetime.fromisoformat(self.expiration_date).date() if isinstance(self.expiration_date, str) else self.expiration_date
        return self.status == "ACTIVE" and today <= expiration
    
    @property
    def days_until_expiration(self) -> int:
        """Calculate days until permit expires"""
        today = datetime.now().date()
        expiration = datetime.fromisoformat(self.expiration_date).date() if isinstance(self.expiration_date, str) else self.expiration_date
        return (expiration - today).days


class ComplianceInspection(BaseModel):
    """
    Compliance inspection record.
    Represents a regulatory inspection of a facility.
    """
    
    def __init__(
        self,
        facility_id: str,
        inspection_date: str,
        inspector_id: str,
        inspection_type: str,
        regulatory_framework: str,
        findings: List[Dict[str, Any]] = None,
        compliance_status: str = None,
        recommendations: List[str] = None,
        followup_required: bool = False,
        followup_date: str = None,
        attachments: List[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize compliance inspection"""
        super().__init__(**kwargs)
        self.facility_id = facility_id
        self.inspection_date = inspection_date
        self.inspector_id = inspector_id
        self.inspection_type = inspection_type
        self.regulatory_framework = regulatory_framework
        self.findings = findings or []
        self.compliance_status = compliance_status
        self.recommendations = recommendations or []
        self.followup_required = followup_required
        self.followup_date = followup_date
        self.attachments = attachments or []
    
    def add_finding(self, finding_type: str, description: str, severity: str, regulation_cited: str = None) -> None:
        """Add a finding to the inspection"""
        self.findings.append({
            "finding_type": finding_type,
            "description": description,
            "severity": severity,
            "regulation_cited": regulation_cited,
            "timestamp": datetime.now().isoformat()
        })


class EnforcementAction(BaseModel):
    """
    Environmental enforcement action.
    Represents an enforcement response to non-compliance.
    """
    
    def __init__(
        self,
        facility_id: str,
        action_type: str,
        violation_description: str,
        regulatory_framework: str,
        issuance_date: str,
        status: str = "PENDING",
        inspector_id: str = None,
        inspection_id: str = None,
        proposed_penalty: float = None,
        final_penalty: float = None,
        corrective_actions: List[Dict[str, Any]] = None,
        compliance_deadline: str = None,
        resolution_date: str = None,
        resolution_details: str = None,
        **kwargs
    ):
        """Initialize enforcement action"""
        super().__init__(**kwargs)
        self.facility_id = facility_id
        self.action_type = action_type
        self.violation_description = violation_description
        self.regulatory_framework = regulatory_framework
        self.issuance_date = issuance_date
        self.status = status
        self.inspector_id = inspector_id
        self.inspection_id = inspection_id
        self.proposed_penalty = proposed_penalty
        self.final_penalty = final_penalty
        self.corrective_actions = corrective_actions or []
        self.compliance_deadline = compliance_deadline
        self.resolution_date = resolution_date
        self.resolution_details = resolution_details
    
    def resolve_action(self, resolution_date: str, resolution_details: str, final_penalty: float = None) -> None:
        """Resolve the enforcement action"""
        self.status = "RESOLVED"
        self.resolution_date = resolution_date
        self.resolution_details = resolution_details
        if final_penalty is not None:
            self.final_penalty = final_penalty
    
    def add_corrective_action(self, description: str, deadline: str, requirements: str = None) -> None:
        """Add a required corrective action"""
        self.corrective_actions.append({
            "description": description,
            "deadline": deadline,
            "requirements": requirements,
            "status": "PENDING"
        })


class ComplianceReport(BaseModel):
    """
    Compliance report submitted by a regulated facility.
    Represents self-reported compliance information.
    """
    
    def __init__(
        self,
        facility_id: str,
        report_type: str,
        reporting_period_start: str,
        reporting_period_end: str,
        submission_date: str,
        permit_id: str = None,
        report_status: str = "SUBMITTED",
        reported_data: Dict[str, Any] = None,
        exceedances: List[Dict[str, Any]] = None,
        certification: Dict[str, Any] = None,
        reviewer_id: str = None,
        review_date: str = None,
        review_comments: str = None,
        **kwargs
    ):
        """Initialize compliance report"""
        super().__init__(**kwargs)
        self.facility_id = facility_id
        self.report_type = report_type
        self.reporting_period_start = reporting_period_start
        self.reporting_period_end = reporting_period_end
        self.submission_date = submission_date
        self.permit_id = permit_id
        self.report_status = report_status
        self.reported_data = reported_data or {}
        self.exceedances = exceedances or []
        self.certification = certification or {}
        self.reviewer_id = reviewer_id
        self.review_date = review_date
        self.review_comments = review_comments
    
    def review_report(self, reviewer_id: str, status: str, comments: str = None) -> None:
        """Record review of the report"""
        self.reviewer_id = reviewer_id
        self.report_status = status
        self.review_date = datetime.now().isoformat()
        self.review_comments = comments