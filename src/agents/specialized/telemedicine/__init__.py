"""
Telemedicine Standards-Compliant Agent

This module provides a standards-compliant agent for telemedicine professionals.
"""

from specialized_agents import StandardsCompliantAgent, ValidationResult
from typing import Any, Dict, List


class TelemedicineAgent(StandardsCompliantAgent):
    """A standards-compliant agent for telemedicine professionals.
    
    Ensures compliance with telehealth and virtual care standards.
    """
    
    def __init__(self, job_role: str, port: int = None):
        """Create a new telemedicine agent.
        
        Args:
            job_role: The specific telemedicine profession
            port: Optional port number for the agent server
        """
        supported_standards = [
            "ATA_GUIDELINES",  # American Telemedicine Association guidelines
            "HIPAA_TELEMEDICINE",  # Health Insurance Portability and Accountability Act telemedicine provisions
            "ISO_13131",  # Health informatics — Telehealth services
            "FSMB_TELEMEDICINE_POLICIES",  # Federation of State Medical Boards telemedicine policies
            "CMS_TELEHEALTH_REGULATIONS",  # Centers for Medicare & Medicaid Services telehealth regulations
        ]
        super().__init__(job_role, "Telemedicine", supported_standards, port)
        
        # Register telemedicine domain tools
        from specialized_agents.telemedicine.tools import register_telemedicine_tools
        tools = register_telemedicine_tools()
        for tool in tools:
            self.addTool(tool)
    
    def getDomainPromptInstructions(self) -> str:
        """Provides domain-specific prompt instructions for telemedicine professionals."""
        return """
As a telemedicine professional, you must adhere to these specific guidelines:

1. Reference appropriate licensure and credentialing requirements for interstate telehealth practice.
2. Address privacy and security considerations specific to virtual care platforms.
3. Present balanced information about appropriate and inappropriate conditions for telehealth management.
4. Reference appropriate informed consent requirements for telemedicine services.
5. Consider technical standards and requirements for telehealth platforms and connectivity.
6. Address documentation requirements specific to telemedicine encounters.
7. Present accurate information about telehealth reimbursement policies and limitations.
8. Consider patient-side requirements and preparations for effective telehealth visits.
9. Address emergency protocols and contingency planning for virtual care scenarios.
10. Reference appropriate quality and outcome measurement approaches for telehealth programs.
"""
    
    def validateDomainCompliance(self, task: Any) -> ValidationResult:
        """Validates compliance with telemedicine-specific standards.
        
        Args:
            task: The task to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        issues: List[str] = []
        
        # Extract the content to validate
        content = self._extract_content_from_task(task)
        
        # Check for potential compliance issues
        if (any(keyword in content.lower() for keyword in 
                ["licensure", "credential", "practice", "provider", "physician"]) and
            not any(keyword in content.lower() for keyword in
                   ["state requirement", "interstate compact", "jurisdiction", "board", "authority", "regulation"]) and
            any(keyword in content.lower() for keyword in
                ["telehealth", "telemedicine", "virtual care", "remote"])):
            issues.append('Response discusses telehealth practice without addressing licensure requirements across jurisdictions')
        
        # Check for privacy and security considerations
        if (any(keyword in content.lower() for keyword in 
                ["privacy", "security", "confidentiality", "data"]) and
            not any(keyword in content.lower() for keyword in
                   ["hipaa", "encryption", "secure platform", "authentication", "breach", "safeguard", "baa"]) and
            any(keyword in content.lower() for keyword in
                ["telehealth", "telemedicine", "virtual", "platform", "application"])):
            issues.append('Response mentions telehealth data without addressing privacy regulations or security requirements')
        
        # Check for appropriateness of conditions for telehealth
        if (any(keyword in content.lower() for keyword in 
                ["condition", "diagnosis", "treatment", "care", "patient"]) and
            not any(keyword in content.lower() for keyword in
                   ["appropriateness", "limitation", "clinical judgment", "in-person alternative", 
                    "guideline", "standard of care"]) and
            any(keyword in content.lower() for keyword in
                ["virtual", "telehealth", "remote", "manage", "treat"])):
            issues.append('Response discusses treating conditions via telehealth without addressing appropriateness or limitations')
        
        # Check for reimbursement and billing considerations
        if (any(keyword in content.lower() for keyword in 
                ["reimbursement", "payment", "coverage", "billing", "code"]) and
            not any(keyword in content.lower() for keyword in
                   ["parity law", "policy", "cms", "medicare", "medicaid", "insurance", 
                    "modifier", "documentation requirement"]) and
            any(keyword in content.lower() for keyword in
                ["telehealth", "telemedicine", "virtual visit", "remote"])):
            issues.append('Response mentions telehealth billing without addressing reimbursement policies or requirements')
        
        # Check for emergency protocols and contingency planning
        if (any(keyword in content.lower() for keyword in 
                ["emergency", "urgent", "crisis", "adverse event"]) and
            not any(keyword in content.lower() for keyword in
                   ["protocol", "plan", "procedure", "local resource", "escalation", "referral", "contingency"]) and
            any(keyword in content.lower() for keyword in
                ["telehealth", "virtual", "remote", "telemedicine"])):
            issues.append('Response discusses telehealth emergencies without addressing protocols or contingency planning')
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues
        )