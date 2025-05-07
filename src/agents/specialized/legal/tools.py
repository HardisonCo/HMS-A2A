"""
MCP Tools for Legal Domain.

This module provides MCP-compliant tools for legal services, document management,
and regulatory compliance.
"""
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime, date

from ..tools_base import StandardsCompliantTool
from ..standards_validation import StandardsValidator
from ..mcp_registry import register_tool


class LegalTools:
    """Collection of MCP-compliant tools for legal domain."""

    @register_tool(
        name="validate_legal_document",
        description="Validate a legal document against legal standards and formats",
        domains=["legal", "compliance"],
        standard="legal_ethics"
    )
    def validate_legal_document(
        document_type: str,
        document_content: Dict[str, Any],
        jurisdiction: str,
        parties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate a legal document against relevant standards and formats.

        Args:
            document_type: Type of legal document (e.g., "contract", "pleading", "opinion")
            document_content: Content and structure of the document
            jurisdiction: Legal jurisdiction (e.g., "US_Federal", "California", "UK")
            parties: List of parties involved in the document

        Returns:
            Dictionary with validation results and compliance issues
        """
        validator = StandardsValidator()
        
        # Define required elements for different document types
        required_elements = {
            "contract": [
                "title", "parties", "effective_date", "terms_and_conditions", 
                "signatures", "governing_law"
            ],
            "pleading": [
                "court_name", "case_caption", "title", "body", 
                "certificate_of_service", "signature_block"
            ],
            "opinion": [
                "court_name", "case_caption", "date", "judge_name", 
                "summary", "legal_analysis", "conclusion"
            ],
            "brief": [
                "court_name", "case_caption", "title", "table_of_contents", 
                "statement_of_facts", "argument", "conclusion", "signature_block"
            ],
            "memorandum": [
                "title", "date", "to", "from", "subject", 
                "discussion", "conclusion"
            ]
        }
        
        # Check if document type is valid
        if document_type not in required_elements:
            validator.add_violation(
                standard="legal_ethics",
                rule="document_format",
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
                    standard="legal_ethics",
                    rule="document_format",
                    message=f"Missing required element: {element}",
                    severity="high"
                )
        
        # Check party information
        for i, party in enumerate(parties):
            if "name" not in party or "role" not in party:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="party_information",
                    message=f"Party {i+1} missing required information (name or role)",
                    severity="high"
                )
        
        # Jurisdiction-specific validation
        if document_type == "contract" and jurisdiction in ["US_Federal", "US_State"]:
            # Check for consideration clause in US contracts
            if "consideration_clause" not in document_content:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="jurisdiction_specific",
                    message="US contracts should include a consideration clause",
                    severity="medium"
                )
        
        # Check document for potential ethical issues
        if document_type == "contract":
            # Check for unfair terms
            if "terms_and_conditions" in document_content:
                terms = document_content["terms_and_conditions"]
                if isinstance(terms, str):
                    problematic_patterns = [
                        r"waive\s+all\s+rights",
                        r"under\s+no\s+circumstances",
                        r"sole\s+discretion",
                        r"at\s+any\s+time\s+for\s+any\s+reason"
                    ]
                    
                    for pattern in problematic_patterns:
                        if re.search(pattern, terms, re.IGNORECASE):
                            validator.add_violation(
                                standard="legal_ethics",
                                rule="fair_dealing",
                                message=f"Potentially one-sided or unfair term detected",
                                severity="medium"
                            )
                            break
        
        elif document_type in ["pleading", "brief"]:
            # Check for citation format
            if "legal_authorities" in document_content:
                authorities = document_content["legal_authorities"]
                if isinstance(authorities, list):
                    for i, citation in enumerate(authorities):
                        if not re.search(r'\d+\s+[A-Za-z\.]+\s+\d+', citation):
                            validator.add_violation(
                                standard="legal_ethics",
                                rule="citation_format",
                                message=f"Citation {i+1} may not be properly formatted",
                                severity="low"
                            )
        
        # Check for confidentiality markings if needed
        if document_type == "memorandum" and document_content.get("confidential", False):
            if "confidentiality_notice" not in document_content:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="confidentiality",
                    message="Confidential document lacks proper confidentiality notice",
                    severity="high"
                )
        
        # Check signatures for contracts
        if document_type == "contract" and "signatures" in document_content:
            signatures = document_content["signatures"]
            if isinstance(signatures, list):
                # Check if all parties have signatures
                party_names = [p["name"] for p in parties]
                signature_names = [s.get("name") for s in signatures if isinstance(s, dict) and "name" in s]
                
                for party in party_names:
                    if party not in signature_names:
                        validator.add_violation(
                            standard="legal_ethics",
                            rule="execution",
                            message=f"Missing signature for party: {party}",
                            severity="high"
                        )
        
        # Return validation results
        violations = validator.get_violations()
        
        return {
            "valid": len(violations) == 0,
            "document_type": document_type,
            "jurisdiction": jurisdiction,
            "violations": violations,
            "recommendations": [
                "Include all required elements for this document type",
                "Ensure all parties are properly identified",
                "Address jurisdiction-specific requirements",
                "Verify document complies with ethical standards",
                "Ensure all signatures are present and valid"
            ] if violations else []
        }

    @register_tool(
        name="analyze_legal_risk",
        description="Analyze the legal risks associated with a scenario or decision",
        domains=["legal", "risk_management"],
        standard="legal_ethics"
    )
    def analyze_legal_risk(
        scenario_description: str,
        applicable_laws: List[str],
        industry_context: str,
        risk_factors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze the legal risks associated with a scenario or decision.

        Args:
            scenario_description: Description of the scenario or decision
            applicable_laws: List of applicable laws and regulations
            industry_context: The industry or business context
            risk_factors: List of specific risk factors to consider

        Returns:
            Dictionary with risk analysis results
        """
        validator = StandardsValidator()
        
        # Validate input parameters
        if not scenario_description or len(scenario_description) < 50:
            validator.add_violation(
                standard="legal_ethics",
                rule="risk_analysis",
                message="Scenario description too brief for meaningful analysis",
                severity="high"
            )
        
        if not applicable_laws:
            validator.add_violation(
                standard="legal_ethics",
                rule="risk_analysis",
                message="No applicable laws specified",
                severity="high"
            )
        
        # Check risk factors for required information
        for i, factor in enumerate(risk_factors):
            if "description" not in factor or "severity" not in factor:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="risk_analysis",
                    message=f"Risk factor {i+1} missing required information",
                    severity="medium"
                )
                continue
            
            severity = factor.get("severity", "").lower()
            if severity not in ["low", "medium", "high", "critical"]:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="risk_analysis",
                    message=f"Invalid severity level for risk factor {i+1}",
                    severity="low"
                )
        
        # Skip in-depth analysis if critical issues are found
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Provide more complete information for risk analysis"]
            }
        
        # Perform risk analysis
        risk_scores = {}
        for i, factor in enumerate(risk_factors):
            description = factor.get("description", "")
            severity = factor.get("severity", "medium").lower()
            likelihood = factor.get("likelihood", "medium").lower()
            
            # Convert severity to numerical score
            severity_score = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "critical": 4
            }.get(severity, 2)
            
            # Convert likelihood to numerical score
            likelihood_score = {
                "unlikely": 1,
                "possible": 2,
                "likely": 3,
                "very_likely": 4
            }.get(likelihood, 2)
            
            # Calculate risk score (severity * likelihood)
            risk_score = severity_score * likelihood_score
            
            # Store the risk assessment
            risk_scores[f"risk_{i+1}"] = {
                "description": description,
                "severity": severity,
                "severity_score": severity_score,
                "likelihood": likelihood,
                "likelihood_score": likelihood_score,
                "risk_score": risk_score,
                "risk_level": "Low" if risk_score <= 3 else ("Medium" if risk_score <= 8 else "High")
            }
        
        # Analyze legal exposure by applicable laws
        legal_exposure = {}
        for law in applicable_laws:
            # Determine exposure level based on risk factors and law
            related_risks = []
            for risk_id, risk in risk_scores.items():
                # Check if risk description mentions this law (simplified)
                if any(term in risk["description"].lower() for term in law.lower().split()):
                    related_risks.append({
                        "risk_id": risk_id,
                        "description": risk["description"],
                        "risk_level": risk["risk_level"]
                    })
            
            # Calculate exposure for this law
            if related_risks:
                max_risk_level = max([r["risk_level"] for r in related_risks], key=lambda x: {"Low": 1, "Medium": 2, "High": 3}.get(x, 0))
                legal_exposure[law] = {
                    "related_risks": related_risks,
                    "exposure_level": max_risk_level,
                    "mitigation_required": max_risk_level != "Low"
                }
            else:
                legal_exposure[law] = {
                    "related_risks": [],
                    "exposure_level": "Unknown",
                    "mitigation_required": "Further analysis needed"
                }
        
        # Generate mitigation recommendations
        mitigation_recommendations = []
        high_risk_areas = [risk for risk in risk_scores.values() if risk["risk_level"] == "High"]
        
        if high_risk_areas:
            mitigation_recommendations.append("Consult specialized legal counsel for high-risk areas")
            
            for risk in high_risk_areas:
                mitigation_recommendations.append(f"Develop specific mitigation plan for: {risk['description']}")
        
        medium_risk_areas = [risk for risk in risk_scores.values() if risk["risk_level"] == "Medium"]
        if medium_risk_areas:
            mitigation_recommendations.append("Review policies and procedures related to medium-risk areas")
            mitigation_recommendations.append("Consider additional contractual protections")
        
        # Add industry-specific recommendations
        if industry_context.lower() == "healthcare":
            mitigation_recommendations.append("Ensure HIPAA compliance program is up to date")
            mitigation_recommendations.append("Review Business Associate Agreements")
        elif industry_context.lower() == "financial":
            mitigation_recommendations.append("Review regulatory compliance procedures")
            mitigation_recommendations.append("Ensure proper customer disclosures")
        
        # Calculate overall risk profile
        overall_risk_score = sum(risk["risk_score"] for risk in risk_scores.values()) / len(risk_scores) if risk_scores else 0
        overall_risk_level = "Low"
        if overall_risk_score > 8:
            overall_risk_level = "High"
        elif overall_risk_score > 3:
            overall_risk_level = "Medium"
        
        # Compile final analysis
        analysis_results = {
            "scenario": scenario_description,
            "industry_context": industry_context,
            "applicable_laws": applicable_laws,
            "individual_risk_assessments": risk_scores,
            "legal_exposure_by_law": legal_exposure,
            "overall_risk_profile": {
                "score": overall_risk_score,
                "level": overall_risk_level,
                "assessment": f"{overall_risk_level} overall legal risk based on provided factors"
            },
            "mitigation_recommendations": mitigation_recommendations
        }
        
        # Add warnings about limitations
        analysis_results["limitations"] = [
            "This analysis is preliminary and should not substitute for professional legal advice",
            "Assessment based only on provided information and factors",
            "Legal landscape may change; regular reassessment recommended"
        ]
        
        # Add compliance information
        violations = validator.get_violations()
        if violations:
            analysis_results["analysis_limitations"] = violations
        
        return analysis_results

    @register_tool(
        name="generate_legal_citation",
        description="Generate properly formatted legal citations for various sources",
        domains=["legal", "documentation"],
        standard="legal_ethics"
    )
    def generate_legal_citation(
        source_type: str,
        source_details: Dict[str, Any],
        citation_style: str = "bluebook",
        jurisdiction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate properly formatted legal citations for various sources.

        Args:
            source_type: Type of legal source ("case", "statute", "regulation", "secondary")
            source_details: Details about the source to cite
            citation_style: Style guide to follow (default: "bluebook")
            jurisdiction: Relevant legal jurisdiction (optional)

        Returns:
            Dictionary with formatted citation and components
        """
        validator = StandardsValidator()
        
        # Define required fields for different source types
        required_fields = {
            "case": ["case_name", "reporter", "volume", "page", "court", "year"],
            "statute": ["title", "code", "section", "year"],
            "regulation": ["title", "code", "section", "year"],
            "secondary": ["author", "title", "publication", "page", "year"]
        }
        
        # Check if source type is valid
        if source_type not in required_fields:
            validator.add_violation(
                standard="legal_ethics",
                rule="citation_format",
                message=f"Invalid source type: {source_type}",
                severity="high"
            )
            return {
                "error": f"Invalid source type: {source_type}",
                "valid_types": list(required_fields.keys())
            }
        
        # Check for required fields
        for field in required_fields[source_type]:
            if field not in source_details:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="citation_format",
                    message=f"Missing required field for {source_type} citation: {field}",
                    severity="high"
                )
        
        # Skip citation generation if required fields are missing
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Provide all required fields for this citation type"]
            }
        
        # Generate citation based on source type and citation style
        citation = ""
        components = {}
        
        if citation_style.lower() == "bluebook":
            if source_type == "case":
                # Format case name (italicized in actual use)
                case_name = source_details["case_name"]
                if not case_name.endswith(","):
                    case_name += ","
                components["case_name"] = case_name
                
                # Format reporter citation
                reporter_citation = f"{source_details['volume']} {source_details['reporter']} {source_details['page']}"
                components["reporter_citation"] = reporter_citation
                
                # Format parenthetical with court and year
                court_year = f"({source_details['court']} {source_details['year']})"
                components["court_year"] = court_year
                
                # Combine all parts
                citation = f"{case_name} {reporter_citation} {court_year}"
                
                # Add pincite if provided
                if "pincite" in source_details:
                    citation += f", at {source_details['pincite']}"
                    components["pincite"] = f"at {source_details['pincite']}"
            
            elif source_type == "statute":
                # Format statute citation
                if jurisdiction and jurisdiction.lower() in ["us_federal", "federal"]:
                    # Federal statute
                    citation = f"{source_details['title']} U.S.C. § {source_details['section']} ({source_details['year']})"
                    components = {
                        "title": source_details['title'],
                        "code": "U.S.C.",
                        "section": f"§ {source_details['section']}",
                        "year": f"({source_details['year']})"
                    }
                else:
                    # State or other statute
                    code = source_details["code"]
                    citation = f"{source_details['title']} {code} § {source_details['section']} ({source_details['year']})"
                    components = {
                        "title": source_details['title'],
                        "code": code,
                        "section": f"§ {source_details['section']}",
                        "year": f"({source_details['year']})"
                    }
            
            elif source_type == "regulation":
                # Format regulation citation
                citation = f"{source_details['title']} {source_details['code']} § {source_details['section']} ({source_details['year']})"
                components = {
                    "title": source_details['title'],
                    "code": source_details['code'],
                    "section": f"§ {source_details['section']}",
                    "year": f"({source_details['year']})"
                }
            
            elif source_type == "secondary":
                # Format secondary source citation
                author = source_details["author"]
                title = source_details["title"]
                if not title.endswith(","):
                    title += ","
                
                publication = source_details["publication"]
                page = source_details["page"]
                year = source_details["year"]
                
                citation = f"{author}, {title} {publication} {page} ({year})"
                components = {
                    "author": author,
                    "title": title,
                    "publication": publication,
                    "page": page,
                    "year": f"({year})"
                }
                
                # Add pincite if provided
                if "pincite" in source_details and source_details["pincite"] != page:
                    citation = citation.replace(f"{page} (", f"{page}, {source_details['pincite']} (")
                    components["pincite"] = source_details["pincite"]
        
        else:
            # Handle other citation styles if needed
            validator.add_violation(
                standard="legal_ethics",
                rule="citation_format",
                message=f"Unsupported citation style: {citation_style}",
                severity="medium"
            )
            citation = "Citation style not supported"
        
        # Check citation quality
        if citation and not citation.startswith("Citation style not supported"):
            # Check for missing spaces
            if re.search(r'[a-zA-Z][0-9]|[0-9][a-zA-Z]', citation):
                validator.add_violation(
                    standard="legal_ethics",
                    rule="citation_format",
                    message="Citation may have formatting issues (missing spaces)",
                    severity="low"
                )
            
            # Check for proper section symbol
            if source_type in ["statute", "regulation"] and "§" not in citation:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="citation_format",
                    message="Section symbol missing in statute/regulation citation",
                    severity="low"
                )
        
        # Return formatted citation and components
        result = {
            "citation": citation,
            "components": components,
            "source_type": source_type,
            "citation_style": citation_style
        }
        
        # Add violations if any
        violations = validator.get_violations()
        if violations:
            result["format_issues"] = violations
        
        return result

    @register_tool(
        name="validate_client_confidentiality",
        description="Validate if sharing certain information would violate client confidentiality",
        domains=["legal", "ethics", "compliance"],
        standard="legal_ethics"
    )
    def validate_client_confidentiality(
        information_type: str,
        disclosure_context: Dict[str, Any],
        client_relationship: Dict[str, Any],
        potential_exceptions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate if sharing certain information would violate client confidentiality.

        Args:
            information_type: Type of information to be disclosed
            disclosure_context: Context of the proposed disclosure
            client_relationship: Details about the attorney-client relationship
            potential_exceptions: List of potential exceptions that might apply

        Returns:
            Dictionary with confidentiality assessment and recommendations
        """
        validator = StandardsValidator()
        
        # Define categories of protected information
        protected_categories = [
            "client_communication", "legal_advice", "work_product", 
            "client_identity", "fee_arrangements", "settlement_discussions"
        ]
        
        # Check if information type is valid
        if information_type not in protected_categories and not information_type.startswith("other:"):
            validator.add_violation(
                standard="legal_ethics",
                rule="confidentiality",
                message=f"Invalid information type: {information_type}",
                severity="medium"
            )
        
        # Check for required context fields
        required_context_fields = ["recipient", "purpose", "format"]
        for field in required_context_fields:
            if field not in disclosure_context:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="confidentiality",
                    message=f"Missing required disclosure context: {field}",
                    severity="high"
                )
        
        # Check for required client relationship fields
        required_relationship_fields = ["status", "consent_obtained"]
        for field in required_relationship_fields:
            if field not in client_relationship:
                validator.add_violation(
                    standard="legal_ethics",
                    rule="confidentiality",
                    message=f"Missing required client relationship information: {field}",
                    severity="high"
                )
        
        # Skip further assessment if critical information is missing
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Provide complete information for confidentiality assessment"]
            }
        
        # Determine if information is confidential
        is_confidential = True
        confidentiality_reasoning = []
        
        # Check if the information category is inherently protected
        if information_type in protected_categories:
            is_confidential = True
            confidentiality_reasoning.append(f"{information_type} is a protected category of information under attorney-client privilege and confidentiality rules")
        elif information_type.startswith("other:"):
            custom_type = information_type[6:].strip()
            is_confidential = True  # Assume confidential by default for custom types
            confidentiality_reasoning.append(f"Custom information type '{custom_type}' is assumed confidential under broad ethical obligations")
        
        # Check if the client relationship is active
        relationship_status = client_relationship.get("status", "").lower()
        if relationship_status not in ["current", "former", "prospective"]:
            validator.add_violation(
                standard="legal_ethics",
                rule="confidentiality",
                message=f"Invalid client relationship status: {relationship_status}",
                severity="medium"
            )
        
        if relationship_status == "current":
            confidentiality_reasoning.append("Current client relationships have the strongest confidentiality protections")
        elif relationship_status == "former":
            confidentiality_reasoning.append("Confidentiality obligations continue even after the attorney-client relationship ends")
        elif relationship_status == "prospective":
            confidentiality_reasoning.append("Information from prospective clients is also subject to confidentiality, even if no formal relationship formed")
        
        # Check for client consent
        consent_obtained = client_relationship.get("consent_obtained", False)
        if consent_obtained:
            consent_details = client_relationship.get("consent_details", {})
            consent_scope = consent_details.get("scope", "")
            consent_format = consent_details.get("format", "")
            
            if consent_scope and consent_format:
                # Check if the consent specifically covers this disclosure
                if information_type in consent_scope or "all" in consent_scope.lower():
                    is_confidential = False
                    confidentiality_reasoning.append(f"Client has provided specific consent for disclosure of {information_type}")
                else:
                    confidentiality_reasoning.append("Client consent obtained but does not specifically cover this information type")
            else:
                confidentiality_reasoning.append("Client consent claimed but details insufficient to verify scope")
        
        # Check for potential exceptions
        applicable_exceptions = []
        if potential_exceptions:
            valid_exceptions = [
                "prevent_crime", "prevent_harm", "legal_proceedings_defense", 
                "fee_dispute", "compliance_with_court_order", "required_by_law"
            ]
            
            for exception in potential_exceptions:
                if exception not in valid_exceptions:
                    validator.add_violation(
                        standard="legal_ethics",
                        rule="confidentiality_exceptions",
                        message=f"Invalid confidentiality exception: {exception}",
                        severity="medium"
                    )
                    continue
                
                # Check if the exception applies
                if exception == "prevent_crime" and disclosure_context.get("crime_prevention_details"):
                    applicable_exceptions.append("Prevention of crime or fraud")
                
                elif exception == "prevent_harm" and disclosure_context.get("harm_prevention_details"):
                    applicable_exceptions.append("Prevention of substantial bodily harm")
                
                elif exception == "legal_proceedings_defense" and disclosure_context.get("legal_proceedings_details"):
                    applicable_exceptions.append("Defense in legal proceedings between attorney and client")
                
                elif exception == "fee_dispute" and disclosure_context.get("fee_dispute_details"):
                    applicable_exceptions.append("Collection of fees")
                
                elif exception == "compliance_with_court_order" and disclosure_context.get("court_order_details"):
                    applicable_exceptions.append("Compliance with court order")
                
                elif exception == "required_by_law" and disclosure_context.get("legal_requirement_details"):
                    applicable_exceptions.append("Required by law or ethics rules")
        
        # Update confidentiality assessment based on exceptions
        if applicable_exceptions:
            confidentiality_reasoning.append(f"Potential exception(s) to confidentiality: {', '.join(applicable_exceptions)}")
            
            # Only certain exceptions can overcome confidentiality
            strong_exceptions = ["compliance_with_court_order", "required_by_law"]
            if any(exc in strong_exceptions for exc in potential_exceptions):
                is_confidential = False
                confidentiality_reasoning.append("Exception provides legal basis for limited disclosure")
            else:
                confidentiality_reasoning.append("Exception may apply but consultation with ethics counsel recommended")
        
        # Generate recommendations
        recommendations = []
        if is_confidential:
            recommendations.append("Do not disclose the information without addressing confidentiality concerns")
            
            if not consent_obtained:
                recommendations.append("Seek explicit client consent for this specific disclosure")
            
            if applicable_exceptions:
                recommendations.append("Consult with ethics counsel about applicability of exceptions")
            
            recommendations.append("Consider if information can be sufficiently anonymized")
        else:
            recommendations.append("Document the basis for disclosure (consent or exception)")
            recommendations.append("Limit disclosure to only essential information")
            recommendations.append("Ensure recipient understands confidential nature")
        
        # Compile final assessment
        assessment_result = {
            "information_type": information_type,
            "is_confidential": is_confidential,
            "confidentiality_reasoning": confidentiality_reasoning,
            "applicable_exceptions": applicable_exceptions,
            "disclosure_permitted": not is_confidential,
            "recommendations": recommendations
        }
        
        # Add disclaimer
        assessment_result["disclaimer"] = [
            "This assessment is preliminary guidance only",
            "Consult with ethics counsel for definitive advice",
            "Rules vary by jurisdiction; check local ethics rules"
        ]
        
        # Add violations if any
        violations = validator.get_violations()
        if violations:
            assessment_result["assessment_limitations"] = violations
        
        return assessment_result


def register_legal_tools() -> List[str]:
    """Register all legal tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a real implementation, this would register tools with a central registry
    tools = [
        LegalTools.validate_legal_document,
        LegalTools.analyze_legal_risk,
        LegalTools.generate_legal_citation,
        LegalTools.validate_client_confidentiality
    ]
    
    return [tool.__name__ for tool in tools]