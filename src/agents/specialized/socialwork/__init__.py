"""
Social Work Standards-Compliant Agent

This module provides a standards-compliant agent for social work professionals.
"""

from specialized_agents import StandardsCompliantAgent, ValidationResult
from typing import Any, Dict, List, Optional


class SocialWorkAgent(StandardsCompliantAgent):
    """A standards-compliant agent for social work professionals.
    
    Ensures compliance with social work ethics, standards, and regulations such as
    the NASW Code of Ethics and other professional social work standards.
    """
    
    def __init__(self, job_role: str, port: int = None):
        """Create a new social work agent.
        
        Args:
            job_role: The specific social work profession
            port: Optional port number for the agent server
        """
        supported_standards = [
            "NASW_CODE_OF_ETHICS",  # National Association of Social Workers Code of Ethics
            "ASWB_STANDARDS",  # Association of Social Work Boards Standards
            "HIPAA",  # Health Insurance Portability and Accountability Act
            "CSWE_STANDARDS",  # Council on Social Work Education Standards
            "IFSW_ETHICS",  # International Federation of Social Workers Ethics
            "CULTURAL_COMPETENCE",  # Cultural Competence Standards
            "CLIENT_CONFIDENTIALITY",  # Client Confidentiality Standards
        ]
        super().__init__(job_role, "SocialWork", supported_standards, port)
        
        # Register social work domain tools
        from specialized_agents.socialwork.tools import register_socialwork_tools
        tools = register_socialwork_tools()
        for tool in tools:
            self.addTool(tool)
    
    def getDomainPromptInstructions(self) -> str:
        """Provides domain-specific prompt instructions for social work professionals."""
        return """
As a social work professional, you must adhere to these specific guidelines:

1. Protect the confidentiality and privacy of all client information at all times.
2. Recognize and respect the inherent dignity and worth of every person.
3. Prioritize client self-determination and informed consent in all interventions.
4. Maintain clear professional boundaries and avoid dual relationships with clients.
5. Acknowledge the importance of cultural competence and diversity considerations.
6. Apply evidence-based practices and stay current with relevant research.
7. Recognize when a human review is necessary for high-risk situations.
8. Always prioritize client safety and well-being in your assessments and interventions.
9. Consider the impact of social, economic, and environmental factors on client situations.
10. Identify when referrals to specialized services or professionals are appropriate.
11. Acknowledge the limits of your expertise when addressing complex client issues.
12. Ensure proposed interventions are consistent with relevant legal and ethical standards.
13. Consider potential impacts on marginalized and vulnerable populations.
14. Apply a trauma-informed approach when appropriate.
15. Maintain professional integrity and avoid any appearance of impropriety.
"""
    
    def validateDomainCompliance(self, task: Any) -> ValidationResult:
        """Validates compliance with social work-specific standards.
        
        Args:
            task: The task to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        issues: List[str] = []
        
        # Extract the content to validate
        content = self._extract_content_from_task(task)
        
        # Use the enhanced standards validation system
        from specialized_agents.standards_validation import StandardsValidator
        
        # Create a validator for the social work domain with our supported standards
        validator = StandardsValidator("socialwork", self.supported_standards)
        
        # Perform validation using the enhanced validation framework
        validation_result = validator.validate_content(content)
        
        # Collect issues from the validation
        if not validation_result.valid:
            for issue in validation_result.issues:
                issues.append(f"{issue.severity.upper()}: {issue.description} - {issue.recommendation}")
        
        # Additional domain-specific checks
        
        # Check for confidentiality considerations
        if (any(keyword in content.lower() for keyword in 
                ["client", "personal information", "case", "assessment", "history", "record"]) and
            not any(keyword in content.lower() for keyword in
                   ["confidential", "privacy", "consent", "authorization", "protected"])):
            issues.append('Response discusses client information without appropriate confidentiality considerations')
        
        # Check for cultural competence
        if (any(keyword in content.lower() for keyword in 
                ["culture", "race", "ethnicity", "religion", "identity", "diversity"]) and
            not any(keyword in content.lower() for keyword in
                   ["cultural competence", "cultural humility", "sensitivity", "respect", "diverse perspectives"])):
            issues.append('Response addresses cultural factors without demonstrating cultural competence')
        
        # Check for client self-determination
        if (any(keyword in content.lower() for keyword in 
                ["intervention", "plan", "treatment", "service", "approach"]) and
            not any(keyword in content.lower() for keyword in
                   ["self-determination", "client choice", "collaboration", "informed consent", "autonomy"])):
            issues.append('Response suggests interventions without emphasizing client self-determination')
        
        # Check for inappropriate therapeutic recommendations
        if (any(keyword in content.lower() for keyword in 
                ["therapy", "counseling", "treatment", "clinical", "diagnosis"]) and
            not any(keyword in content.lower() for keyword in
                   ["qualified", "licensed", "professional", "appropriate", "evidence-based", "supervised"])):
            issues.append('Response contains therapeutic recommendations without appropriate qualifications or considerations')
        
        # Check for mandated reporting considerations (from TS implementation)
        if any(pattern in content.lower() for pattern in [
                "child abuse", "elder abuse", "neglect", "harm to self", "harm to others", "suicidal"
            ]) and not any(pattern in content.lower() for pattern in [
                "mandated reporting", "legal obligation", "duty to report", "safety plan", "immediate concern"
            ]):
            issues.append('CRITICAL: Content addresses safety concerns that may require mandated reporting without acknowledging reporting obligations')
        
        # Check for ethical boundary considerations (from TS implementation)
        if any(pattern in content.lower() for pattern in [
                "dual relationship", "gift", "personal relationship", "outside contact", "social media"
            ]) and not any(pattern in content.lower() for pattern in [
                "professional boundary", "ethical consideration", "conflict of interest", "consult supervisor"
            ]):
            issues.append('CRITICAL: Content suggests practices that may violate professional boundaries without proper ethical considerations')
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues
        )