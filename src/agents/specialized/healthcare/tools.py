"""
MCP Tools for Healthcare Domain.

This module provides MCP-compliant tools for working with healthcare data
and standards such as HIPAA.
"""
from typing import Dict, List, Any, Optional
import json

from ..tools_base import StandardsCompliantTool
from ..standards_validation import StandardsValidator
from ..mcp_registry import register_tool


class HealthcareTools:
    """Collection of MCP-compliant tools for healthcare domain."""

    @register_tool(
        name="validate_phi_handling",
        description="Validate Protected Health Information handling against HIPAA requirements",
        domains=["healthcare", "data_privacy"],
        standard="HIPAA"
    )
    def validate_phi_handling(
        operation_type: str,
        data_elements: List[str],
        purpose: str,
        access_control: Dict[str, Any],
        encryption_used: bool
    ) -> Dict[str, Any]:
        """
        Validate that PHI handling complies with HIPAA requirements.

        Args:
            operation_type: Type of operation ("store", "transfer", "access", "delete")
            data_elements: List of data elements being handled
            purpose: Purpose for handling the data
            access_control: Access control mechanisms in place
            encryption_used: Whether encryption is used

        Returns:
            Dictionary with validation results and compliance issues
        """
        validator = StandardsValidator()
        
        # Define PHI elements that require special protection
        phi_elements = [
            "name", "address", "dob", "ssn", "medical_record_number", 
            "health_plan_id", "phone_number", "email", "biometric_id",
            "account_number", "certificate_number", "vehicle_identifiers",
            "device_identifiers", "web_url", "ip_address", "finger_print",
            "photograph", "any_unique_identifier"
        ]
        
        # Check if data contains PHI
        contains_phi = any(element.lower() in phi_elements for element in data_elements)
        
        if contains_phi:
            # Validate against HIPAA requirements
            
            # Check encryption requirements
            if not encryption_used and operation_type.lower() in ["store", "transfer"]:
                validator.add_violation(
                    standard="HIPAA",
                    rule="phi_protection",
                    message="PHI must be encrypted during storage and transmission",
                    severity="critical"
                )
            
            # Check purpose specification
            if not purpose:
                validator.add_violation(
                    standard="HIPAA",
                    rule="minimum_necessary",
                    message="Purpose for PHI handling must be specified",
                    severity="high"
                )
            
            # Check access controls
            required_controls = ["role_based_access", "authentication", "access_logs"]
            for control in required_controls:
                if control not in access_control or not access_control[control]:
                    validator.add_violation(
                        standard="HIPAA",
                        rule="phi_protection",
                        message=f"Required access control '{control}' not implemented",
                        severity="high"
                    )
            
            # Check for minimum necessary principle
            if not access_control.get("minimum_necessary_review"):
                validator.add_violation(
                    standard="HIPAA",
                    rule="minimum_necessary",
                    message="Minimum necessary principle review not conducted",
                    severity="medium"
                )
        
        # Return validation results
        violations = validator.get_violations()
        
        return {
            "operation_type": operation_type,
            "contains_phi": contains_phi,
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": [
                "Implement encryption for all PHI at rest and in transit",
                "Document purpose for all PHI access and disclosure",
                "Implement role-based access controls",
                "Maintain detailed access logs",
                "Conduct regular security risk assessments"
            ] if contains_phi else []
        }

    @register_tool(
        name="check_authorization",
        description="Check if an agent is authorized to access specific healthcare data",
        domains=["healthcare", "data_privacy"],
        standard="HIPAA"
    )
    def check_authorization(
        agent_id: str,
        agent_role: str,
        data_category: str,
        purpose: str,
        patient_consent: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Check if an agent is authorized to access specific healthcare data.

        Args:
            agent_id: Identifier for the requesting agent
            agent_role: Role of the agent (e.g., "physician", "researcher")
            data_category: Category of data being accessed
            purpose: Purpose for accessing the data
            patient_consent: Whether patient consent has been obtained

        Returns:
            Dictionary with authorization decision and reasoning
        """
        validator = StandardsValidator()
        
        # Define role-based access permissions
        role_permissions = {
            "physician": ["diagnosis", "treatment", "medication", "lab_results", "medical_history"],
            "nurse": ["vital_signs", "medication", "lab_results", "care_notes"],
            "researcher": ["anonymized_data", "consented_research_data"],
            "administrator": ["billing", "scheduling", "facility_management"],
            "patient": ["own_records", "own_billing"]
        }
        
        # Define data sensitivity levels
        data_sensitivity = {
            "diagnosis": "high",
            "treatment": "high",
            "medication": "high",
            "lab_results": "high",
            "medical_history": "high",
            "vital_signs": "medium",
            "care_notes": "high",
            "anonymized_data": "low",
            "consented_research_data": "high",
            "billing": "medium",
            "scheduling": "low",
            "facility_management": "low",
            "own_records": "high",
            "own_billing": "medium"
        }
        
        # Check if role exists
        if agent_role not in role_permissions:
            validator.add_violation(
                standard="HIPAA",
                rule="phi_protection",
                message=f"Unknown role: {agent_role}",
                severity="critical"
            )
            authorized = False
            reason = f"Unknown role: {agent_role}"
        
        # Check if data category exists
        elif data_category not in data_sensitivity:
            validator.add_violation(
                standard="HIPAA",
                rule="phi_protection",
                message=f"Unknown data category: {data_category}",
                severity="high"
            )
            authorized = False
            reason = f"Unknown data category: {data_category}"
        
        # Check role-based permissions
        elif data_category not in role_permissions.get(agent_role, []):
            validator.add_violation(
                standard="HIPAA",
                rule="phi_protection",
                message=f"Role {agent_role} not authorized to access {data_category}",
                severity="high"
            )
            authorized = False
            reason = f"Role {agent_role} not authorized to access {data_category}"
        
        # Check if purpose is specified
        elif not purpose:
            validator.add_violation(
                standard="HIPAA",
                rule="minimum_necessary",
                message="Purpose must be specified for data access",
                severity="high"
            )
            authorized = False
            reason = "Purpose must be specified for data access"
        
        # Check if patient consent is required but not provided
        elif data_sensitivity.get(data_category) == "high" and patient_consent is None:
            validator.add_violation(
                standard="HIPAA",
                rule="patient_rights",
                message="Patient consent status must be specified for sensitive data",
                severity="high"
            )
            authorized = False
            reason = "Patient consent status must be specified for sensitive data"
        
        # Check if patient consent is required but denied
        elif data_category == "consented_research_data" and patient_consent is False:
            validator.add_violation(
                standard="HIPAA",
                rule="patient_rights",
                message="Patient consent required for research data access",
                severity="critical"
            )
            authorized = False
            reason = "Patient consent required for research data access"
        
        # If all checks pass, authorize access
        else:
            authorized = True
            reason = f"Role {agent_role} is authorized to access {data_category} for specified purpose"
        
        # Return authorization decision
        violations = validator.get_violations()
        
        return {
            "agent_id": agent_id,
            "agent_role": agent_role,
            "data_category": data_category,
            "purpose": purpose,
            "patient_consent": patient_consent,
            "authorized": authorized,
            "reason": reason,
            "violations": violations
        }

    @register_tool(
        name="generate_hipaa_compliant_report",
        description="Generate a HIPAA-compliant healthcare report",
        domains=["healthcare", "data_privacy"],
        standard="HIPAA"
    )
    def generate_hipaa_compliant_report(
        report_type: str,
        data_elements: Dict[str, Any],
        recipient_role: str,
        include_phi: bool,
        purpose: str
    ) -> Dict[str, Any]:
        """
        Generate a HIPAA-compliant healthcare report.

        Args:
            report_type: Type of report (e.g., "discharge_summary", "lab_results")
            data_elements: Dictionary of data elements to include
            recipient_role: Role of the recipient
            include_phi: Whether to include PHI in the report
            purpose: Purpose for generating the report

        Returns:
            Dictionary with report content and compliance metadata
        """
        validator = StandardsValidator()
        
        # Define required elements for different report types
        required_elements = {
            "discharge_summary": ["admission_date", "discharge_date", "diagnosis", "treatment", "follow_up"],
            "lab_results": ["test_name", "test_date", "result", "reference_range", "interpretation"],
            "medication_list": ["medication_name", "dosage", "frequency", "start_date"],
            "billing_statement": ["service_date", "service_description", "charges", "insurance_info"],
            "referral": ["referring_provider", "referred_to", "reason", "medical_history_summary"]
        }
        
        # Define authorized recipients for different report types
        authorized_recipients = {
            "discharge_summary": ["physician", "nurse", "patient", "authorized_caregiver"],
            "lab_results": ["physician", "nurse", "patient", "lab_technician"],
            "medication_list": ["physician", "nurse", "pharmacist", "patient"],
            "billing_statement": ["patient", "billing_staff", "insurance_provider"],
            "referral": ["physician", "specialist", "patient"]
        }
        
        # Validate report type
        if report_type not in required_elements:
            validator.add_violation(
                standard="HIPAA",
                rule="phi_protection",
                message=f"Unknown report type: {report_type}",
                severity="medium"
            )
            
            return {
                "error": f"Unknown report type: {report_type}",
                "valid_report_types": list(required_elements.keys()),
                "compliant": False,
                "violations": validator.get_violations()
            }
        
        # Check recipient authorization
        if recipient_role not in authorized_recipients.get(report_type, []):
            validator.add_violation(
                standard="HIPAA",
                rule="phi_protection",
                message=f"Recipient role '{recipient_role}' is not authorized for {report_type}",
                severity="high"
            )
        
        # Check for required elements
        missing_elements = []
        for element in required_elements[report_type]:
            if element not in data_elements:
                missing_elements.append(element)
        
        if missing_elements:
            validator.add_violation(
                standard="HIPAA",
                rule="phi_protection",
                message=f"Missing required elements: {', '.join(missing_elements)}",
                severity="medium"
            )
        
        # Check if purpose is specified for PHI
        if include_phi and not purpose:
            validator.add_violation(
                standard="HIPAA",
                rule="minimum_necessary",
                message="Purpose must be specified when including PHI",
                severity="high"
            )
        
        # Generate report content
        report_content = {}
        
        # Add metadata
        report_content["metadata"] = {
            "report_type": report_type,
            "generation_date": "2023-01-01",  # In a real implementation, use current date
            "purpose": purpose,
            "recipient_role": recipient_role,
            "contains_phi": include_phi,
            "minimum_necessary_reviewed": True,  # In a real implementation, this would be a check
            "hipaa_compliant": len(validator.get_violations()) == 0
        }
        
        # Add content
        report_content["content"] = {}
        
        # Add required elements from the input data
        for element in required_elements[report_type]:
            if element in data_elements:
                report_content["content"][element] = data_elements[element]
            else:
                report_content["content"][element] = "Missing required information"
        
        # Add optional elements
        for key, value in data_elements.items():
            if key not in required_elements[report_type]:
                report_content["content"][key] = value
        
        # Add PHI warning if needed
        if include_phi:
            report_content["phi_notice"] = {
                "warning": "This document contains Protected Health Information (PHI).",
                "handling": "Handle according to HIPAA requirements.",
                "disclosure": "Unauthorized disclosure is prohibited by law."
            }
        
        # Add compliance information
        violations = validator.get_violations()
        report_content["compliance"] = {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": [
                "Ensure all required elements are included",
                "Verify recipient authorization",
                "Document purpose for PHI disclosure",
                "Implement minimum necessary principle"
            ] if violations else []
        }
        
        return report_content

    @register_tool(
        name="validate_hipaa_compliance",
        description="Validate a healthcare process or system against HIPAA requirements",
        domains=["healthcare", "data_privacy"],
        standard="HIPAA"
    )
    def validate_hipaa_compliance(
        system_name: str,
        data_types: List[str],
        security_measures: Dict[str, Any],
        access_controls: Dict[str, Any],
        patient_rights_procedures: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a healthcare system or process against HIPAA requirements.

        Args:
            system_name: Name of the system or process
            data_types: Types of data handled by the system
            security_measures: Dictionary of security measures in place
            access_controls: Dictionary of access control mechanisms
            patient_rights_procedures: Dictionary of patient rights procedures

        Returns:
            Dictionary with compliance assessment results
        """
        validator = StandardsValidator()
        
        # Define PHI types that require special protection
        phi_types = [
            "name", "address", "ssn", "medical_record", "health_plan_id",
            "contact_info", "biometric_identifiers", "photos", "dates"
        ]
        
        # Check if system handles PHI
        contains_phi = any(data_type.lower() in phi_types for data_type in data_types)
        
        # Required security measures for PHI
        if contains_phi:
            required_security = [
                "encryption_at_rest", 
                "encryption_in_transit",
                "access_logging",
                "automatic_logoff",
                "authentication",
                "backup_procedures",
                "disaster_recovery",
                "emergency_mode",
                "audit_controls"
            ]
            
            for measure in required_security:
                if measure not in security_measures or not security_measures[measure]:
                    validator.add_violation(
                        standard="HIPAA",
                        rule="phi_protection",
                        message=f"Required security measure '{measure}' not implemented",
                        severity="high" if measure in ["encryption_at_rest", "encryption_in_transit"] else "medium"
                    )
            
            # Required access controls
            required_access = [
                "role_based_access", 
                "unique_user_ids",
                "emergency_access",
                "automatic_logoff",
                "audit_controls"
            ]
            
            for control in required_access:
                if control not in access_controls or not access_controls[control]:
                    validator.add_violation(
                        standard="HIPAA",
                        rule="phi_protection",
                        message=f"Required access control '{control}' not implemented",
                        severity="medium"
                    )
            
            # Required patient rights procedures
            required_rights = [
                "access_to_phi",
                "amendment_requests",
                "accounting_of_disclosures",
                "restrictions_requests",
                "confidential_communications"
            ]
            
            for right in required_rights:
                if right not in patient_rights_procedures or not patient_rights_procedures[right]:
                    validator.add_violation(
                        standard="HIPAA",
                        rule="patient_rights",
                        message=f"Required patient right procedure '{right}' not implemented",
                        severity="medium"
                    )
        
        # Get validation results
        violations = validator.get_violations()
        
        # Create recommendations based on violations
        recommendations = []
        if violations:
            for violation in violations:
                if violation["rule"] == "phi_protection":
                    if "encryption" in violation["message"]:
                        recommendations.append("Implement encryption for all PHI at rest and in transit")
                    elif "access" in violation["message"]:
                        recommendations.append("Strengthen access controls with role-based permissions")
                    else:
                        recommendations.append(f"Address security issue: {violation['message']}")
                elif violation["rule"] == "patient_rights":
                    recommendations.append(f"Implement procedure for {violation['message'].split('\'')[1]}")
        
        # Remove duplicate recommendations
        unique_recommendations = []
        for rec in recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)
        
        return {
            "system_name": system_name,
            "contains_phi": contains_phi,
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": unique_recommendations,
            "next_steps": [
                "Document all compliance measures in policies and procedures",
                "Conduct regular risk assessments",
                "Train staff on HIPAA requirements and your specific procedures",
                "Implement technical safeguards for all identified gaps",
                "Develop a breach notification protocol"
            ] if violations else [
                "Maintain documentation of compliance measures",
                "Conduct regular audits and risk assessments",
                "Update policies and procedures as regulations change"
            ]
        }


def register_healthcare_tools() -> List[str]:
    """Register all healthcare tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a real implementation, this would register tools with a central registry
    tools = [
        HealthcareTools.validate_phi_handling,
        HealthcareTools.check_authorization,
        HealthcareTools.generate_hipaa_compliant_report,
        HealthcareTools.validate_hipaa_compliance
    ]
    
    return [tool.__name__ for tool in tools]