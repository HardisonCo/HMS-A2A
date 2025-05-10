"""
Accounting Standards-Compliant Agent

This module provides a standards-compliant agent for accounting professionals.
"""

from specialized_agents import StandardsCompliantAgent, ValidationResult
from typing import Any, Dict, List, Optional


class AccountingAgent(StandardsCompliantAgent):
    """A standards-compliant agent for accounting professionals.
    
    Ensures compliance with accounting standards and regulations such as
    GAAP, IFRS, and other professional accounting standards.
    """
    
    def __init__(self, job_role: str, port: int = None):
        """Create a new accounting agent.
        
        Args:
            job_role: The specific accounting profession
            port: Optional port number for the agent server
        """
        supported_standards = [
            "GAAP",  # Generally Accepted Accounting Principles
            "IFRS",  # International Financial Reporting Standards
            "XBRL",  # eXtensible Business Reporting Language
            "SASB_STANDARDS",  # Sustainability Accounting Standards Board
            "SOX",  # Sarbanes-Oxley Act
            "AICPA_CODE_OF_ETHICS",  # American Institute of CPAs Code of Ethics
            "IIA_STANDARDS",  # Institute of Internal Auditors Standards
        ]
        super().__init__(job_role, "Accounting", supported_standards, port)
        
        # Register accounting domain tools
        from specialized_agents.accounting.tools import register_accounting_tools
        tools = register_accounting_tools()
        for tool in tools:
            self.addTool(tool)
    
    def getDomainPromptInstructions(self) -> str:
        """Provides domain-specific prompt instructions for accounting professionals."""
        return """
As an accounting professional, you must adhere to these specific guidelines:

1. Maintain objectivity and professional skepticism in all analyses and recommendations.
2. Ensure all financial information follows relevant accounting frameworks (GAAP, IFRS).
3. Respect confidentiality of financial information and business data.
4. Disclose when information provided is general guidance rather than financial advice.
5. Include appropriate disclaimers about the limitations of accounting information.
6. Avoid providing tax advice unless clearly qualified to do so in the relevant jurisdiction.
7. Present financial information with appropriate context and time periods.
8. Acknowledge limitations in your analysis when working with incomplete information.
9. Ensure compliance with relevant regulatory frameworks when discussing financial reporting.
10. Maintain transparency about accounting methods, estimates, and judgments.
11. Flag potential issues related to internal controls or fraud risks when identified.
12. Disclose potential conflicts of interest in financial analyses or recommendations.
"""
    
    def validateDomainCompliance(self, task: Any) -> ValidationResult:
        """Validates compliance with accounting-specific standards.
        
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
        
        # Create a validator for the accounting domain with our supported standards
        validator = StandardsValidator("accounting", self.supported_standards)
        
        # Perform validation using the enhanced validation framework
        validation_result = validator.validate_content(content)
        
        # Collect issues from the validation
        if not validation_result.valid:
            for issue in validation_result.issues:
                issues.append(f"{issue.severity.upper()}: {issue.description} - {issue.recommendation}")
        
        # Additional domain-specific checks
        
        # Check for proper accounting framework references
        if (any(keyword in content.lower() for keyword in 
                ["financial statement", "balance sheet", "income statement", "cash flow statement"]) and
            not any(keyword in content.lower() for keyword in
                   ["gaap", "ifrs", "accounting standards", "accounting principles"])):
            issues.append('Response discusses financial statements without referencing applicable accounting standards')
        
        # Check for auditing guidance 
        if (any(keyword in content.lower() for keyword in 
                ["audit", "auditing", "assurance"]) and
            not any(keyword in content.lower() for keyword in
                   ["reasonable assurance", "material misstatement", "audit evidence", "scope limitation"])):
            issues.append('Response contains audit-related guidance without proper audit terminology or limitations')
        
        # Check for appropriate tax disclaimer
        if (any(keyword in content.lower() for keyword in 
                ["tax", "taxation", "deduction", "tax-deductible", "tax planning"]) and
            not any(keyword in content.lower() for keyword in
                   ["consult", "tax professional", "not tax advice", "tax laws vary", "subject to change"])):
            issues.append('Response provides tax-related information without proper disclaimers')
        
        # Check for proper estimation language
        if (any(keyword in content.lower() for keyword in 
                ["estimate", "projection", "forecast", "future", "valuation"]) and
            not any(keyword in content.lower() for keyword in
                   ["assumption", "judgment", "uncertainty", "may differ", "not guaranteed", "estimate"])):
            issues.append('Response contains projections or estimates without acknowledging uncertainties')
            
        # Check for tax evasion suggestions (from TS implementation)
        if any(pattern in content.lower() for pattern in [
                "hide income", "unreported cash", "conceal revenue", "off the books", 
                "don't report", "avoid reporting", "hide from IRS"
            ]):
            issues.append('CRITICAL: Content appears to suggest tax evasion or concealing income, which violates tax compliance standards')
        
        # Check for financial statement manipulation (from TS implementation)
        if any(pattern in content.lower() for pattern in [
                "manipulate statement", "window dress", "make financials look", 
                "enhance the numbers", "hide liability", "inflate asset", "mislead investors"
            ]):
            issues.append('CRITICAL: Content suggests manipulating financial statements or misrepresenting financial position')
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues
        )