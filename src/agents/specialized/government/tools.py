"""
MCP Tools for Government Administration Domain.

This module provides MCP-compliant tools for government administration,
public policy, and regulatory compliance.
"""
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime, date

from ..tools_base import StandardsCompliantTool
from ..standards_validation import StandardsValidator
from ..mcp_registry import register_tool


class GovernmentTools:
    """Collection of MCP-compliant tools for government administration domain."""

    @register_tool(
        name="validate_policy_document",
        description="Validate a policy document against government standards",
        domains=["government", "public_administration", "policy"],
        standard="USGovOps"
    )
    def validate_policy_document(
        document_type: str,
        document_content: Dict[str, Any],
        agency: str,
        accessibility_check: bool = True
    ) -> Dict[str, Any]:
        """
        Validate a government policy document against relevant standards.

        Args:
            document_type: Type of document ("policy", "regulation", "guidance", "directive")
            document_content: The content and structure of the document
            agency: The government agency or department issuing the document
            accessibility_check: Whether to check for accessibility compliance

        Returns:
            Dictionary with validation results and compliance issues
        """
        validator = StandardsValidator()
        
        # Define required elements for different document types
        required_elements = {
            "policy": [
                "title", "effective_date", "authority", "policy_statement", 
                "scope", "responsibilities", "procedures", "definitions"
            ],
            "regulation": [
                "title", "authority", "effective_date", "applicability", 
                "regulatory_text", "compliance_requirements"
            ],
            "guidance": [
                "title", "purpose", "background", "guidance_details", 
                "implementation", "contact_information"
            ],
            "directive": [
                "title", "issuance_date", "expiration_date", "authority", 
                "directive_details", "compliance_requirements"
            ]
        }
        
        # Check if document type is valid
        if document_type not in required_elements:
            validator.add_violation(
                standard="USGovOps",
                rule="document_structure",
                message=f"Invalid document type: {document_type}",
                severity="high"
            )
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": [f"Use one of: {', '.join(required_elements.keys())}"]
            }
        
        # Check for required elements
        for element in required_elements[document_type]:
            if element not in document_content:
                validator.add_violation(
                    standard="USGovOps",
                    rule="document_structure",
                    message=f"Missing required element: {element}",
                    severity="high"
                )
        
        # Check for basic formatting and clarity
        if "title" in document_content:
            title = document_content["title"]
            if len(title) > 150:
                validator.add_violation(
                    standard="USGovOps",
                    rule="clarity",
                    message="Title exceeds recommended length (150 characters)",
                    severity="medium"
                )
        
        # Check date formatting
        date_fields = ["effective_date", "issuance_date", "expiration_date"]
        for field in date_fields:
            if field in document_content:
                date_str = document_content[field]
                try:
                    # Try to parse the date to ensure it's valid
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    validator.add_violation(
                        standard="USGovOps",
                        rule="date_format",
                        message=f"Invalid date format in {field}: {date_str}. Use YYYY-MM-DD format.",
                        severity="medium"
                    )
        
        # Check for proper authority citation
        if "authority" in document_content:
            authority = document_content["authority"]
            if not (isinstance(authority, str) and len(authority) > 5):
                validator.add_violation(
                    standard="USGovOps",
                    rule="authority_citation",
                    message="Authority citation missing or inadequate",
                    severity="high"
                )
        
        # Check for plain language usage
        text_fields = ["policy_statement", "procedures", "regulatory_text", "guidance_details", "directive_details"]
        for field in text_fields:
            if field in document_content:
                text = document_content[field]
                if isinstance(text, str):
                    # Check for long sentences (over 30 words)
                    sentences = re.split(r'[.!?]', text)
                    for sentence in sentences:
                        words = sentence.split()
                        if len(words) > 30:
                            validator.add_violation(
                                standard="USGovOps",
                                rule="plain_language",
                                message=f"Sentence with more than 30 words found in {field}",
                                severity="medium"
                            )
                            break
                    
                    # Check for passive voice (simplified check)
                    passive_patterns = [
                        r'\b(?:is|are|was|were|be|been|being)\s+\w+ed\b',
                        r'\b(?:is|are|was|were|be|been|being)\s+\w+en\b'
                    ]
                    for pattern in passive_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            validator.add_violation(
                                standard="USGovOps",
                                rule="plain_language",
                                message=f"Passive voice detected in {field}",
                                severity="low"
                            )
                            break
        
        # Check for accessibility compliance
        if accessibility_check:
            # Check for alt text in images
            if "images" in document_content:
                images = document_content.get("images", [])
                for i, image in enumerate(images):
                    if not image.get("alt_text"):
                        validator.add_violation(
                            standard="USGovOps",
                            rule="accessibility",
                            message=f"Missing alt text for image {i+1}",
                            severity="high"
                        )
            
            # Check for table headers
            if "tables" in document_content:
                tables = document_content.get("tables", [])
                for i, table in enumerate(tables):
                    if not table.get("headers"):
                        validator.add_violation(
                            standard="USGovOps",
                            rule="accessibility",
                            message=f"Missing headers for table {i+1}",
                            severity="high"
                        )
        
        # Agency-specific validations
        if agency.lower() == "department of defense":
            if "classification" not in document_content:
                validator.add_violation(
                    standard="USGovOps",
                    rule="agency_specific",
                    message="DoD documents require classification marking",
                    severity="high"
                )
        elif agency.lower() == "department of health and human services":
            if "privacy_impact" not in document_content:
                validator.add_violation(
                    standard="USGovOps",
                    rule="agency_specific",
                    message="HHS policies require privacy impact assessment",
                    severity="medium"
                )
        
        # Return validation results
        violations = validator.get_violations()
        
        return {
            "valid": len(violations) == 0,
            "document_type": document_type,
            "agency": agency,
            "violations": violations,
            "recommendations": [
                "Ensure all required elements are included",
                "Use plain language and active voice",
                "Properly cite authority",
                "Include appropriate accessibility features",
                "Follow agency-specific requirements"
            ] if violations else []
        }

    @register_tool(
        name="analyze_regulatory_impact",
        description="Analyze the potential impact of a regulatory action",
        domains=["government", "regulatory", "policy_analysis"],
        standard="USGovOps"
    )
    def analyze_regulatory_impact(
        regulation_summary: Dict[str, Any],
        affected_entities: List[Dict[str, Any]],
        impact_areas: List[str],
        analysis_timeframe: Optional[int] = 5
    ) -> Dict[str, Any]:
        """
        Analyze the potential impact of a regulatory action on various stakeholders.

        Args:
            regulation_summary: Summary of the proposed regulation
            affected_entities: List of entities affected by the regulation
            impact_areas: Areas to analyze (e.g., "economic", "environmental", "social")
            analysis_timeframe: Number of years to consider in analysis (default: 5)

        Returns:
            Dictionary with impact analysis results
        """
        validator = StandardsValidator()
        
        # Validate input parameters
        valid_impact_areas = ["economic", "environmental", "social", "health", "administrative", "legal", "equity"]
        for area in impact_areas:
            if area.lower() not in [a.lower() for a in valid_impact_areas]:
                validator.add_violation(
                    standard="USGovOps",
                    rule="impact_analysis",
                    message=f"Invalid impact area: {area}",
                    severity="medium"
                )
        
        if analysis_timeframe <= 0:
            validator.add_violation(
                standard="USGovOps",
                rule="impact_analysis",
                message=f"Invalid analysis timeframe: {analysis_timeframe}",
                severity="medium"
            )
        
        # Check if regulation summary contains required elements
        required_elements = ["title", "description", "authority", "objectives"]
        for element in required_elements:
            if element not in regulation_summary:
                validator.add_violation(
                    standard="USGovOps",
                    rule="impact_analysis",
                    message=f"Regulation summary missing required element: {element}",
                    severity="high"
                )
        
        # Check if affected entities have required information
        for i, entity in enumerate(affected_entities):
            if "type" not in entity or "impact_level" not in entity:
                validator.add_violation(
                    standard="USGovOps",
                    rule="impact_analysis",
                    message=f"Affected entity {i+1} missing required information",
                    severity="high"
                )
        
        # Skip further analysis if there are critical issues
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Correct critical issues before proceeding with impact analysis"]
            }
        
        # Perform impact analysis
        impact_results = {}
        
        # Economic impact analysis
        if "economic" in impact_areas:
            economic_impact = {
                "costs": {},
                "benefits": {},
                "net_impact": {}
            }
            
            # Calculate costs for each affected entity type
            entity_types = set(entity["type"] for entity in affected_entities)
            for entity_type in entity_types:
                entities_of_type = [e for e in affected_entities if e["type"] == entity_type]
                
                # Calculate aggregate impact
                if all("estimated_cost" in e for e in entities_of_type):
                    total_cost = sum(e["estimated_cost"] for e in entities_of_type)
                    economic_impact["costs"][entity_type] = total_cost
                else:
                    economic_impact["costs"][entity_type] = "Unknown - insufficient data"
            
            # Add benefits if provided
            if "economic_benefits" in regulation_summary:
                economic_impact["benefits"] = regulation_summary["economic_benefits"]
            else:
                economic_impact["benefits"] = "Not specified in regulation summary"
            
            # Attempt to calculate net impact
            if all(isinstance(cost, (int, float)) for cost in economic_impact["costs"].values()):
                total_costs = sum(economic_impact["costs"].values())
                
                if isinstance(economic_impact["benefits"], dict) and all(isinstance(benefit, (int, float)) for benefit in economic_impact["benefits"].values()):
                    total_benefits = sum(economic_impact["benefits"].values())
                    economic_impact["net_impact"] = {
                        "value": total_benefits - total_costs,
                        "description": "Positive" if total_benefits > total_costs else "Negative"
                    }
                else:
                    economic_impact["net_impact"] = {
                        "value": -total_costs,
                        "description": "Costs only - benefits not quantified"
                    }
            else:
                economic_impact["net_impact"] = "Cannot calculate - insufficient quantitative data"
            
            impact_results["economic"] = economic_impact
        
        # Environmental impact analysis
        if "environmental" in impact_areas:
            environmental_impact = {
                "affected_resources": [],
                "mitigation_measures": [],
                "long_term_effects": []
            }
            
            # Extract environmental impacts if provided
            if "environmental_impacts" in regulation_summary:
                env_impacts = regulation_summary["environmental_impacts"]
                
                if isinstance(env_impacts, dict):
                    environmental_impact["affected_resources"] = env_impacts.get("affected_resources", [])
                    environmental_impact["mitigation_measures"] = env_impacts.get("mitigation_measures", [])
                    environmental_impact["long_term_effects"] = env_impacts.get("long_term_effects", [])
                elif isinstance(env_impacts, list):
                    environmental_impact["affected_resources"] = env_impacts
            
            # Check for missing environmental assessment
            if not environmental_impact["affected_resources"]:
                validator.add_violation(
                    standard="USGovOps",
                    rule="environmental_analysis",
                    message="Environmental impact assessment lacks detail on affected resources",
                    severity="medium"
                )
            
            impact_results["environmental"] = environmental_impact
        
        # Social impact analysis
        if "social" in impact_areas:
            social_impact = {
                "affected_groups": [],
                "equity_considerations": {},
                "community_effects": []
            }
            
            # Extract social impacts if provided
            if "social_impacts" in regulation_summary:
                social_impacts = regulation_summary["social_impacts"]
                
                if isinstance(social_impacts, dict):
                    social_impact["affected_groups"] = social_impacts.get("affected_groups", [])
                    social_impact["equity_considerations"] = social_impacts.get("equity_considerations", {})
                    social_impact["community_effects"] = social_impacts.get("community_effects", [])
            
            # Identify affected groups from affected entities
            for entity in affected_entities:
                if entity.get("type") in ["community", "demographic_group", "social_group"]:
                    if entity.get("name") not in social_impact["affected_groups"]:
                        social_impact["affected_groups"].append(entity.get("name"))
            
            impact_results["social"] = social_impact
        
        # Generate overall assessment
        overall_assessment = {
            "summary": f"Impact analysis over {analysis_timeframe} years",
            "key_findings": [],
            "recommendations": [],
            "data_limitations": []
        }
        
        # Add key findings
        if "economic" in impact_results:
            economic = impact_results["economic"]
            if isinstance(economic["net_impact"], dict) and "value" in economic["net_impact"]:
                if economic["net_impact"]["value"] > 0:
                    overall_assessment["key_findings"].append("Positive economic net benefit expected")
                else:
                    overall_assessment["key_findings"].append("Economic costs may exceed quantified benefits")
        
        if "environmental" in impact_results:
            environmental = impact_results["environmental"]
            if environmental["affected_resources"]:
                overall_assessment["key_findings"].append(f"Environmental impacts identified for {len(environmental['affected_resources'])} resource types")
            
            if not environmental["mitigation_measures"]:
                overall_assessment["recommendations"].append("Develop environmental mitigation measures")
        
        if "social" in impact_results:
            social = impact_results["social"]
            if social["affected_groups"]:
                overall_assessment["key_findings"].append(f"Social impacts identified for {len(social['affected_groups'])} groups")
            
            if not social["equity_considerations"]:
                overall_assessment["recommendations"].append("Conduct equity impact assessment")
        
        # Note data limitations
        for area in impact_areas:
            if area not in impact_results:
                overall_assessment["data_limitations"].append(f"Insufficient data for {area} impact analysis")
        
        impact_results["overall_assessment"] = overall_assessment
        
        # Add violations if any
        violations = validator.get_violations()
        if violations:
            impact_results["compliance_issues"] = violations
        
        return impact_results

    @register_tool(
        name="generate_public_notice",
        description="Generate a standards-compliant public notice document",
        domains=["government", "public_administration", "communications"],
        standard="USGovOps"
    )
    def generate_public_notice(
        notice_type: str,
        subject: str,
        content: Dict[str, Any],
        agency: str,
        publication_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a standards-compliant public notice document.

        Args:
            notice_type: Type of notice ("proposed_rule", "meeting", "funding", "procurement")
            subject: Subject or title of the notice
            content: Content sections of the notice
            agency: Issuing agency or department
            publication_details: Publication date, channel, and other details

        Returns:
            Dictionary with the generated notice document
        """
        validator = StandardsValidator()
        
        # Define required content for different notice types
        required_content = {
            "proposed_rule": [
                "summary", "dates", "addresses", "further_information", 
                "supplementary_information", "regulatory_text"
            ],
            "meeting": [
                "summary", "dates", "addresses", "agenda", 
                "public_participation", "contact_information"
            ],
            "funding": [
                "summary", "dates", "eligibility", "award_information", 
                "application_process", "evaluation_criteria", "contact_information"
            ],
            "procurement": [
                "summary", "solicitation_number", "response_date", 
                "requirements", "evaluation_criteria", "contact_information"
            ]
        }
        
        # Check if notice type is valid
        if notice_type not in required_content:
            validator.add_violation(
                standard="USGovOps",
                rule="notice_structure",
                message=f"Invalid notice type: {notice_type}",
                severity="high"
            )
            return {
                "error": f"Invalid notice type: {notice_type}",
                "valid_types": list(required_content.keys())
            }
        
        # Check for required content sections
        for section in required_content[notice_type]:
            if section not in content:
                validator.add_violation(
                    standard="USGovOps",
                    rule="notice_structure",
                    message=f"Missing required content section: {section}",
                    severity="high"
                )
        
        # Check for publication details
        required_pub_details = ["publication_date", "federal_register_category"]
        for detail in required_pub_details:
            if detail not in publication_details:
                validator.add_violation(
                    standard="USGovOps",
                    rule="publication_requirements",
                    message=f"Missing required publication detail: {detail}",
                    severity="medium"
                )
        
        # Title length check
        if len(subject) > 200:
            validator.add_violation(
                standard="USGovOps",
                rule="clarity",
                message="Notice title exceeds 200 characters",
                severity="low"
            )
        
        # Check plain language compliance for summary
        if "summary" in content:
            summary = content["summary"]
            
            # Check for sentence length
            sentences = re.split(r'[.!?]', summary)
            for sentence in sentences:
                words = sentence.split()
                if len(words) > 30:
                    validator.add_violation(
                        standard="USGovOps",
                        rule="plain_language",
                        message="Summary contains sentences longer than 30 words",
                        severity="medium"
                    )
                    break
        
        # Check for properly formatted dates
        if "dates" in content:
            dates_section = content["dates"]
            date_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b'
            
            # Check if dates are properly formatted
            if isinstance(dates_section, str) and not re.search(date_pattern, dates_section):
                validator.add_violation(
                    standard="USGovOps",
                    rule="date_format",
                    message="Dates section does not contain properly formatted dates",
                    severity="medium"
                )
        
        # Generate the notice document
        notice = {
            "document_type": "PUBLIC_NOTICE",
            "notice_type": notice_type,
            "title": subject,
            "agency": agency,
            "publication_details": publication_details,
            "content": {}
        }
        
        # Add header with generated information
        notice["header"] = {
            "document_number": f"{agency[:3]}-{publication_details.get('publication_date', 'DATE').replace('-', '')}-{notice_type[:3]}".upper(),
            "billing_code": publication_details.get("billing_code", "____-__-P"),
            "agency": agency,
            "agency_acronym": ''.join(word[0] for word in agency.split() if word[0].isupper()),
            "title": subject
        }
        
        # Add all provided content sections
        for section_name, section_content in content.items():
            notice["content"][section_name] = section_content
        
        # Add missing required sections with placeholders
        for section in required_content[notice_type]:
            if section not in notice["content"]:
                notice["content"][section] = "[Required: Add content for this section]"
        
        # Add standard footer
        notice["footer"] = {
            "signature_block": f"Dated: {publication_details.get('signature_date', publication_details.get('publication_date', 'DATE'))}.",
            "signatory": publication_details.get("signatory", "[NAME], [TITLE]"),
            "authority_citation": publication_details.get("authority_citation", "Authority: [CITE APPLICABLE AUTHORITY]"),
            "billing_code": publication_details.get("billing_code", "____-__-P")
        }
        
        # Add compliance information
        violations = validator.get_violations()
        if violations:
            notice["compliance_issues"] = violations
            
            notice["recommendations"] = [
                "Include all required sections for this notice type",
                "Use plain language in the summary section",
                "Ensure dates are clearly and properly formatted",
                "Provide complete publication details",
                "Include proper authority citation"
            ]
        
        return notice

    @register_tool(
        name="validate_records_management",
        description="Validate records management compliance for government documents",
        domains=["government", "records_management", "compliance"],
        standard="USGovOps"
    )
    def validate_records_management(
        record_type: str,
        record_metadata: Dict[str, Any],
        content_details: Dict[str, Any],
        retention_schedule: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate records management compliance for government documents.

        Args:
            record_type: Type of record ("administrative", "policy", "case_file", "correspondence")
            record_metadata: Metadata about the record
            content_details: Details about the record content
            retention_schedule: Optional retention schedule information

        Returns:
            Dictionary with validation results and compliance issues
        """
        validator = StandardsValidator()
        
        # Define valid record types
        valid_record_types = [
            "administrative", "policy", "case_file", "correspondence", 
            "financial", "legal", "personnel", "procurement"
        ]
        
        # Check if record type is valid
        if record_type not in valid_record_types:
            validator.add_violation(
                standard="USGovOps",
                rule="records_management",
                message=f"Invalid record type: {record_type}",
                severity="high"
            )
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": [f"Use one of: {', '.join(valid_record_types)}"]
            }
        
        # Check required metadata fields
        required_metadata = [
            "identifier", "creation_date", "creator", "office_of_origin", 
            "classification", "access_restrictions"
        ]
        
        for field in required_metadata:
            if field not in record_metadata:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_metadata",
                    message=f"Missing required metadata field: {field}",
                    severity="high"
                )
        
        # Check identifier format
        if "identifier" in record_metadata:
            identifier = record_metadata["identifier"]
            # Check for standard format (alphanumeric with possible separators)
            if not re.match(r'^[A-Za-z0-9\-_.]+$', identifier):
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_metadata",
                    message="Identifier contains invalid characters",
                    severity="medium"
                )
        
        # Check date format
        if "creation_date" in record_metadata:
            creation_date = record_metadata["creation_date"]
            try:
                datetime.strptime(creation_date, "%Y-%m-%d")
            except ValueError:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_metadata",
                    message="Invalid date format for creation_date. Use YYYY-MM-DD format.",
                    severity="medium"
                )
        
        # Check classification values
        if "classification" in record_metadata:
            classification = record_metadata["classification"]
            valid_classifications = [
                "unclassified", "confidential", "secret", "top_secret", 
                "controlled_unclassified", "for_official_use_only", "sensitive"
            ]
            
            if classification.lower() not in [c.lower() for c in valid_classifications]:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_metadata",
                    message=f"Invalid classification value: {classification}",
                    severity="high"
                )
        
        # Check content details
        required_content_fields = ["format", "size", "content_type"]
        for field in required_content_fields:
            if field not in content_details:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_content",
                    message=f"Missing required content detail: {field}",
                    severity="medium"
                )
        
        # Validate format
        if "format" in content_details:
            format = content_details["format"]
            valid_formats = [
                "pdf", "docx", "xlsx", "pptx", "txt", "csv", "xml", "json", 
                "tiff", "jpeg", "mp3", "mp4", "paper"
            ]
            
            if format.lower() not in [f.lower() for f in valid_formats]:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_content",
                    message=f"Potentially non-compliant format: {format}",
                    severity="low"
                )
        
        # Check retention schedule if provided
        if retention_schedule:
            required_retention_fields = ["schedule_identifier", "retention_period", "disposition_instructions"]
            for field in required_retention_fields:
                if field not in retention_schedule:
                    validator.add_violation(
                        standard="USGovOps",
                        rule="retention_schedule",
                        message=f"Missing required retention schedule field: {field}",
                        severity="high"
                    )
            
            # Check if retention period is specified
            if "retention_period" in retention_schedule:
                retention_period = retention_schedule["retention_period"]
                
                # Check for proper format (e.g., "7 years", "permanent")
                if not (isinstance(retention_period, str) and 
                       (re.match(r'^\d+\s+years?$', retention_period) or 
                        retention_period.lower() == "permanent")):
                    validator.add_violation(
                        standard="USGovOps",
                        rule="retention_schedule",
                        message="Retention period must be specified as 'X years' or 'permanent'",
                        severity="medium"
                    )
        else:
            # If retention schedule is not provided for certain record types, flag it
            if record_type in ["policy", "financial", "legal", "case_file"]:
                validator.add_violation(
                    standard="USGovOps",
                    rule="retention_schedule",
                    message=f"Retention schedule must be specified for {record_type} records",
                    severity="high"
                )
        
        # Special checks for different record types
        if record_type == "policy":
            if "superseded_documents" not in record_metadata:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_management",
                    message="Policy records should identify superseded documents",
                    severity="medium"
                )
        
        elif record_type == "case_file":
            if "case_identifier" not in record_metadata:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_management",
                    message="Case files must include a case identifier",
                    severity="high"
                )
            
            if "case_status" not in record_metadata:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_management",
                    message="Case files must include the case status",
                    severity="medium"
                )
        
        elif record_type == "correspondence":
            if "correspondent" not in record_metadata:
                validator.add_violation(
                    standard="USGovOps",
                    rule="records_management",
                    message="Correspondence records must identify the correspondent",
                    severity="medium"
                )
        
        # Return validation results
        violations = validator.get_violations()
        
        results = {
            "valid": len(violations) == 0,
            "record_type": record_type,
            "violations": violations,
            "recommendations": []
        }
        
        # Add specific recommendations based on violations
        if violations:
            if any(v["rule"] == "records_metadata" for v in violations):
                results["recommendations"].append("Complete all required metadata fields")
            
            if any(v["rule"] == "retention_schedule" for v in violations):
                results["recommendations"].append("Specify a retention schedule according to agency policy")
            
            if any(v["rule"] == "records_content" for v in violations):
                results["recommendations"].append("Ensure content format is compliant with record management standards")
            
            if any(v["severity"] == "high" for v in violations):
                results["recommendations"].append("Address critical compliance issues before finalizing the record")
        
        return results


def register_government_tools() -> List[str]:
    """Register all government administration tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a real implementation, this would register tools with a central registry
    tools = [
        GovernmentTools.validate_policy_document,
        GovernmentTools.analyze_regulatory_impact,
        GovernmentTools.generate_public_notice,
        GovernmentTools.validate_records_management
    ]
    
    return [tool.__name__ for tool in tools]