#!/usr/bin/env python3
"""
Agency Generator

This script automates the generation of agency-specific components for the
Codex CLI agency interface. It creates issue finders, research connectors,
ASCII art, and configuration files for federal agencies.
"""

import os
import sys
import json
import argparse
from string import Template
from datetime import datetime
import re

# Templates for agency components
ISSUE_FINDER_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
${AGENCY} Issue Finder

A specialized issue finder for the ${AGENCY_NAME} (${AGENCY})
that identifies ${DOMAIN}-related issues and prepares research context for Codex CLI.
\"\"\"

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agency_issue_finder.issue_finder import AgencyIssueFinder, AgencyIssueFinderException

class ${AGENCY}IssueFinder(AgencyIssueFinder):
    \"\"\"
    ${AGENCY}-specific issue finder implementation.
    Identifies ${DOMAIN}-related issues and prepares research context.
    \"\"\"
    
    def __init__(self, config_dir: str, data_dir: str) -> None:
        \"\"\"
        Initialize the ${AGENCY} issue finder.
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing agency data
        \"\"\"
        super().__init__("${AGENCY}", config_dir, data_dir)
        self.${DOMAIN_VAR}_domains = self._load_${DOMAIN_VAR}_domains()
    
    def _load_${DOMAIN_VAR}_domains(self) -> Dict[str, List[str]]:
        \"\"\"Load ${DOMAIN} domain information.\"\"\"
        domains_file = os.path.join(self.data_dir, "${AGENCY_LOWER}", "${DOMAIN_VAR}_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise AgencyIssueFinderException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return ${DEFAULT_DOMAINS}
    
    def find_issues(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        \"\"\"
        Find current issues for ${AGENCY}.
        
        Args:
            topic: Optional topic to filter issues
            
        Returns:
            List of issues found
        \"\"\"
        # Start with empty issues list
        self.issues = []
        
        # If a specific topic is provided, find relevant issues
        if topic:
            # Check if topic matches any ${DOMAIN} domain
            for domain, subdomains in self.${DOMAIN_VAR}_domains.items():
                if topic.lower() in domain.lower() or topic.lower() in [s.lower() for s in subdomains]:
                    self.issues.extend(self._get_domain_issues(domain))
        
        # If no topic is specified or no issues found for topic, return all high-priority issues
        if not self.issues:
            for domain in self.${DOMAIN_VAR}_domains:
                self.issues.extend(self._get_domain_issues(domain, high_priority_only=True))
        
        # If still no issues found, add a default issue
        if not self.issues:
            self.issues.append({
                "id": "${AGENCY}-GEN-001",
                "title": "${DOMAIN_TITLE} Systems Integration Analysis",
                "status": "pending",
                "priority": "high",
                "description": "Analysis of integration points between ${DOMAIN} systems and components.",
                "affected_areas": ["All ${DOMAIN} domains"],
                "detection_date": datetime.now().strftime("%Y-%m-%d"),
                "resources": [
                    {"type": "implementation_plan", "path": "${AGENCY}-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-${AGENCY}/"}
                ]
            })
        
        return self.issues
    
    def _get_domain_issues(self, domain: str, high_priority_only: bool = False) -> List[Dict[str, Any]]:
        \"\"\"
        Get issues for a specific ${DOMAIN} domain.
        
        Args:
            domain: ${DOMAIN_TITLE} domain
            high_priority_only: Only return high priority issues
            
        Returns:
            List of domain issues
        \"\"\"
        issues = []
        
        # Add placeholder issue for domain
        issues.append({
            "id": f"${AGENCY}-{domain[:2].upper()}-001",
            "title": f"{domain.title()} Integration",
            "status": "pending",
            "priority": "high" if domain in ${HIGH_PRIORITY_DOMAINS} else "medium",
            "description": f"Integration of {domain} systems with HMS components.",
            "affected_areas": [subdomain.replace('_', ' ').title() for subdomain in self.${DOMAIN_VAR}_domains.get(domain, [])],
            "detection_date": datetime.now().strftime("%Y-%m-%d"),
            "resources": [
                {"type": "implementation_plan", "path": "${AGENCY}-IMPLEMENTATION-PLAN.md"},
                {"type": "codebase", "path": f"SYSTEM-COMPONENTS/HMS-${AGENCY}/"}
            ]
        })
        
        # Filter by priority if requested
        if high_priority_only:
            issues = [issue for issue in issues if issue["priority"] == "high"]
        
        return issues
    
    def prepare_context(self, issue_id: Optional[str] = None) -> Dict[str, Any]:
        \"\"\"
        Prepare context for Codex CLI based on ${AGENCY} issues.
        
        Args:
            issue_id: Optional issue ID to focus on
            
        Returns:
            Context dictionary for Codex CLI
        \"\"\"
        # Find the specified issue
        issue = None
        if issue_id and self.issues:
            issue = next((i for i in self.issues if i["id"] == issue_id), None)
        
        # If no specific issue is selected, use the highest priority issue
        if not issue and self.issues:
            issue = sorted(self.issues, key=lambda x: 0 if x["priority"] == "high" else 
                                                     1 if x["priority"] == "medium" else 2)[0]
        
        # If no issues are found, return empty context
        if not issue:
            return {
                "agency": "${AGENCY}",
                "issue": None,
                "resources": [],
                "codex_args": "--agency=${AGENCY_LOWER}"
            }
        
        # Prepare agency-specific context
        context = {
            "agency": "${AGENCY}",
            "issue": issue,
            "resources": issue.get("resources", []),
            "domains": self.${DOMAIN_VAR}_domains,
            "codex_args": f"--agency=${AGENCY_LOWER} --issue-id={issue['id']}"
        }
        
        # Add additional arguments for high priority issues
        if issue.get("priority") == "high":
            context["codex_args"] += " --priority=high"
        
        # Add domain-specific arguments if applicable
        for domain in self.${DOMAIN_VAR}_domains:
            domain_code = domain[:2].upper()
            if f"${AGENCY}-{domain_code}-" in issue["id"]:
                context["codex_args"] += f" --domain={domain}"
                break
        
        return context


def main():
    \"\"\"Main entry point for the ${AGENCY} issue finder.\"\"\"
    import argparse
    
    parser = argparse.ArgumentParser(description="${AGENCY} Issue Finder")
    parser.add_argument("--topic", help="Topic to filter issues")
    parser.add_argument("--config-dir", default=os.path.expanduser("~/.codex/agency-config"),
                       help="Directory containing configuration files")
    parser.add_argument("--data-dir", default=os.path.expanduser("~/.codex/agency-data"),
                       help="Directory containing agency data")
    parser.add_argument("--issue-id", help="Specific issue ID to prepare context for")
    parser.add_argument("--output-format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the ${AGENCY} issue finder
        finder = ${AGENCY}IssueFinder(args.config_dir, args.data_dir)
        
        # Find issues
        issues = finder.find_issues(args.topic)
        
        # Prepare context
        context = finder.prepare_context(args.issue_id)
        
        if args.output_format == "json":
            print(json.dumps(context, indent=2))
        else:
            print(f"Agency: {context['agency']}")
            
            if context.get("issue"):
                print(f"Issue ID: {context['issue']['id']}")
                print(f"Title: {context['issue']['title']}")
                print(f"Status: {context['issue']['status']}")
                print(f"Priority: {context['issue']['priority']}")
                print(f"Resources: {len(context['resources'])}")
                print(f"Codex Args: {context['codex_args']}")
            else:
                print("No issues found.")
    
    except AgencyIssueFinderException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
"""

RESEARCH_CONNECTOR_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
${AGENCY} Research Connector

A specialized connector for the ${AGENCY_NAME} (${AGENCY})
that provides access to ${DOMAIN}-related research and implementation data.
\"\"\"

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agency_issue_finder.base_connector import AgencyResearchConnector

class ${AGENCY}Exception(Exception):
    \"\"\"Custom exception for ${AGENCY} connector errors.\"\"\"
    pass

class ${AGENCY}ResearchConnector(AgencyResearchConnector):
    \"\"\"
    ${AGENCY}-specific research connector implementation.
    Provides access to ${DOMAIN} research and implementation data.
    \"\"\"
    
    def __init__(self, base_path: str) -> None:
        \"\"\"
        Initialize the ${AGENCY} research connector.
        
        Args:
            base_path: Base path to ${AGENCY} data
        \"\"\"
        super().__init__("${AGENCY}", base_path)
        self.${DOMAIN_VAR}_domains = self._load_${DOMAIN_VAR}_domains()
        self.${DOMAIN_VAR}_frameworks = self._load_${DOMAIN_VAR}_frameworks()
    
    def _load_${DOMAIN_VAR}_domains(self) -> Dict[str, Any]:
        \"\"\"Load ${DOMAIN} domain information.\"\"\"
        domains_file = os.path.join(self.agency_dir, "${DOMAIN_VAR}_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ${AGENCY}Exception(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return ${DEFAULT_DOMAINS_FULL}
    
    def _load_${DOMAIN_VAR}_frameworks(self) -> Dict[str, Any]:
        \"\"\"Load ${AGENCY} regulatory frameworks.\"\"\"
        frameworks_file = os.path.join(self.agency_dir, "${DOMAIN_VAR}_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ${AGENCY}Exception(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return ${DEFAULT_FRAMEWORKS}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        \"\"\"
        Get implementation status for ${AGENCY}.
        
        Returns:
            Implementation status dictionary
        \"\"\"
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add ${AGENCY}-specific status information
        status["domains"] = list(self.${DOMAIN_VAR}_domains.keys())
        status["frameworks"] = list(self.${DOMAIN_VAR}_frameworks.keys())
        
        return status
    
    def get_${DOMAIN_VAR}_recommendations(self) -> List[str]:
        \"\"\"
        Get ${DOMAIN}-specific recommendations.
        
        Returns:
            List of ${DOMAIN} recommendations
        \"\"\"
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.${DOMAIN_VAR}_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.${DOMAIN_VAR}_frameworks.items():
            recommendations.append(f"Ensure compliance with {info['name']} regulations")
        
        # Generate recommendations based on implementation status
        if "implementation_phases" in status:
            phases = status["implementation_phases"]
            
            # Find the first incomplete phase
            current_phase = None
            for phase_key, phase in sorted(phases.items()):
                if phase["percentage"] < 100:
                    current_phase = phase
                    break
            
            if current_phase:
                # Add recommendations for incomplete tasks in the current phase
                for task in current_phase["tasks"]:
                    if not task["completed"]:
                        recommendations.append(f"Complete task: {task['name']}")
        
        return recommendations
    
    def get_codex_context(self) -> Dict[str, Any]:
        \"\"\"
        Generate Codex context for ${AGENCY}.
        
        Returns:
            Codex context dictionary
        \"\"\"
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_${DOMAIN_VAR}_recommendations()
        
        # Compile context
        context = {
            "agency": "${AGENCY}",
            "full_name": "${AGENCY_NAME}",
            "domains": self.${DOMAIN_VAR}_domains,
            "regulatory_frameworks": self.${DOMAIN_VAR}_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    \"\"\"Main entry point function.\"\"\"
    import argparse
    
    parser = argparse.ArgumentParser(description="${AGENCY} Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to ${AGENCY} data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the ${AGENCY} connector
        connector = ${AGENCY}ResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_${DOMAIN_VAR}_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"${AGENCY} Implementation Status")
                print(f"-------------------------")
                
                if "overall_completion" in result:
                    overall = result["overall_completion"]
                    print(f"Overall Completion: {overall['completed_tasks']}/{overall['total_tasks']} "
                          f"({overall['percentage']:.1f}%)")
                
                if "implementation_phases" in result:
                    print("\\nPhases:")
                    for phase_key, phase in sorted(result["implementation_phases"].items()):
                        print(f"  {phase['name']}: {phase['completed_tasks']}/{phase['total_tasks']} "
                              f"({phase['percentage']:.1f}%)")
                
                print(f"\\nDomains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['frameworks'])}")
            
            elif args.output == "recommendations":
                print(f"${AGENCY} Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"${AGENCY} Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except ${AGENCY}Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
"""

ASCII_ART_TEMPLATE = """ █████████████████████████████████████████████████████████
 █                                                       █
 █   ${ASCII_LINE1}                    █
 █   ${ASCII_LINE2}                    █
 █   ${ASCII_LINE3}                    █
 █   ${ASCII_LINE4}                    █
 █   ${ASCII_LINE5}                    █
 █                                                       █
 █       ${AGENCY_FULL_NAME}      █
 █                                                       █
 █████████████████████████████████████████████████████████"""

# Domain-specific templates
DOMAIN_TEMPLATES = {
    "healthcare": {
        "DEFAULT_DOMAINS": {
            "public_health": ["epidemiology", "disease_prevention", "health_promotion"],
            "healthcare_delivery": ["primary_care", "hospital_care", "long_term_care"],
            "health_insurance": ["medicare", "medicaid", "private_insurance"],
            "medical_research": ["clinical_research", "biomedical_research", "health_services_research"],
            "health_policy": ["regulatory_policy", "payment_policy", "public_health_policy"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "public_health": {
                "description": "Protection and improvement of population health",
                "sub_domains": ["epidemiology", "disease_prevention", "health_promotion"]
            },
            "healthcare_delivery": {
                "description": "Systems and processes for delivering healthcare services",
                "sub_domains": ["primary_care", "hospital_care", "long_term_care"]
            },
            "health_insurance": {
                "description": "Coverage and financing of healthcare",
                "sub_domains": ["medicare", "medicaid", "private_insurance"]
            },
            "medical_research": {
                "description": "Scientific investigation to improve health",
                "sub_domains": ["clinical_research", "biomedical_research", "health_services_research"]
            },
            "health_policy": {
                "description": "Development and analysis of healthcare policies",
                "sub_domains": ["regulatory_policy", "payment_policy", "public_health_policy"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "description": "Privacy and security rules for health information",
                "components": ["privacy_rule", "security_rule", "breach_notification_rule"]
            },
            "aca": {
                "name": "Affordable Care Act",
                "description": "Comprehensive health insurance reform",
                "components": ["individual_mandate", "insurance_exchanges", "medicaid_expansion"]
            },
            "fda_regulations": {
                "name": "FDA Regulations",
                "description": "Regulations for drugs, devices, and biologics",
                "components": ["drug_approval", "device_approval", "biologic_approval"]
            },
            "cms_regulations": {
                "name": "CMS Regulations",
                "description": "Regulations for Medicare and Medicaid",
                "components": ["medicare_conditions", "medicaid_requirements", "payment_rules"]
            },
            "public_health_regulations": {
                "name": "Public Health Regulations",
                "description": "Regulations for public health protection",
                "components": ["disease_reporting", "vaccination", "emergency_response"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["public_health", "health_insurance", "health_policy"]
    },
    "defense": {
        "DEFAULT_DOMAINS": {
            "military_operations": ["planning", "execution", "evaluation"],
            "defense_procurement": ["acquisition", "contracting", "supply_chain"],
            "personnel_management": ["recruitment", "training", "retention"],
            "intelligence": ["collection", "analysis", "dissemination"],
            "cybersecurity": ["defense", "offense", "resilience"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "military_operations": {
                "description": "Planning and execution of military missions",
                "sub_domains": ["planning", "execution", "evaluation"]
            },
            "defense_procurement": {
                "description": "Acquisition of weapons systems and services",
                "sub_domains": ["acquisition", "contracting", "supply_chain"]
            },
            "personnel_management": {
                "description": "Management of military and civilian personnel",
                "sub_domains": ["recruitment", "training", "retention"]
            },
            "intelligence": {
                "description": "Collection and analysis of intelligence",
                "sub_domains": ["collection", "analysis", "dissemination"]
            },
            "cybersecurity": {
                "description": "Defense against cyber threats",
                "sub_domains": ["defense", "offense", "resilience"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "dod_5000": {
                "name": "DoD Directive 5000 Series",
                "description": "Defense acquisition system regulations",
                "components": ["acquisition_planning", "procurement", "lifecycle_management"]
            },
            "ucmj": {
                "name": "Uniform Code of Military Justice",
                "description": "Military legal framework",
                "components": ["judicial_procedures", "punitive_articles", "administration"]
            },
            "jcids": {
                "name": "Joint Capabilities Integration and Development System",
                "description": "Requirements generation process",
                "components": ["capability_assessment", "requirements_definition", "validation"]
            },
            "ppbe": {
                "name": "Planning, Programming, Budgeting, and Execution",
                "description": "Defense resource allocation process",
                "components": ["planning", "programming", "budgeting", "execution"]
            },
            "dsca": {
                "name": "Defense Security Cooperation",
                "description": "Foreign military sales and cooperation",
                "components": ["foreign_military_sales", "international_training", "security_assistance"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["military_operations", "cybersecurity", "intelligence"]
    },
    "finance": {
        "DEFAULT_DOMAINS": {
            "taxation": ["individual_tax", "corporate_tax", "tax_policy"],
            "banking": ["regulation", "supervision", "monetary_policy"],
            "public_finance": ["budgeting", "debt_management", "fiscal_policy"],
            "financial_markets": ["securities", "commodities", "derivatives"],
            "economic_policy": ["economic_analysis", "policy_development", "implementation"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "taxation": {
                "description": "Collection and administration of taxes",
                "sub_domains": ["individual_tax", "corporate_tax", "tax_policy"]
            },
            "banking": {
                "description": "Regulation and supervision of banking system",
                "sub_domains": ["regulation", "supervision", "monetary_policy"]
            },
            "public_finance": {
                "description": "Management of government finances",
                "sub_domains": ["budgeting", "debt_management", "fiscal_policy"]
            },
            "financial_markets": {
                "description": "Oversight of financial markets",
                "sub_domains": ["securities", "commodities", "derivatives"]
            },
            "economic_policy": {
                "description": "Development and implementation of economic policy",
                "sub_domains": ["economic_analysis", "policy_development", "implementation"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "banking_regulations": {
                "name": "Banking Regulations",
                "description": "Regulations for depository institutions",
                "components": ["capital_requirements", "liquidity_requirements", "risk_management"]
            },
            "tax_code": {
                "name": "Internal Revenue Code",
                "description": "Federal tax laws",
                "components": ["income_tax", "corporate_tax", "excise_tax"]
            },
            "securities_laws": {
                "name": "Securities Laws",
                "description": "Regulations for securities markets",
                "components": ["disclosure_requirements", "antifraud_provisions", "registration"]
            },
            "monetary_policy": {
                "name": "Monetary Policy Framework",
                "description": "Federal Reserve policy tools",
                "components": ["interest_rates", "open_market_operations", "reserve_requirements"]
            },
            "fiscal_policy": {
                "name": "Fiscal Policy Framework",
                "description": "Government spending and taxation",
                "components": ["budgeting", "debt_management", "revenue_collection"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["taxation", "banking", "public_finance"]
    },
    "agriculture": {
        "DEFAULT_DOMAINS": {
            "farming": ["crop_production", "livestock", "aquaculture"],
            "food_safety": ["inspection", "regulation", "certification"],
            "rural_development": ["economic_development", "housing", "infrastructure"],
            "conservation": ["soil", "water", "wildlife"],
            "research": ["agricultural_research", "economic_research", "technology_transfer"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "farming": {
                "description": "Agricultural production systems",
                "sub_domains": ["crop_production", "livestock", "aquaculture"]
            },
            "food_safety": {
                "description": "Ensuring safety of food supply",
                "sub_domains": ["inspection", "regulation", "certification"]
            },
            "rural_development": {
                "description": "Economic development in rural areas",
                "sub_domains": ["economic_development", "housing", "infrastructure"]
            },
            "conservation": {
                "description": "Protection of natural resources",
                "sub_domains": ["soil", "water", "wildlife"]
            },
            "research": {
                "description": "Scientific investigation to improve agriculture",
                "sub_domains": ["agricultural_research", "economic_research", "technology_transfer"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "farm_bill": {
                "name": "Farm Bill",
                "description": "Comprehensive agricultural legislation",
                "components": ["commodity_programs", "conservation", "rural_development"]
            },
            "fsis_regulations": {
                "name": "Food Safety and Inspection Service Regulations",
                "description": "Regulations for meat, poultry, and eggs",
                "components": ["inspection", "labeling", "pathogen_reduction"]
            },
            "organic_standards": {
                "name": "National Organic Program",
                "description": "Standards for organic products",
                "components": ["certification", "production", "handling"]
            },
            "aphis_regulations": {
                "name": "APHIS Regulations",
                "description": "Regulations for animal and plant health",
                "components": ["pest_management", "disease_prevention", "quarantine"]
            },
            "nrcs_programs": {
                "name": "Natural Resources Conservation Service Programs",
                "description": "Conservation programs",
                "components": ["easements", "financial_assistance", "technical_assistance"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["food_safety", "farming", "conservation"]
    },
    "justice": {
        "DEFAULT_DOMAINS": {
            "law_enforcement": ["federal_law_enforcement", "criminal_investigation", "intelligence"],
            "legal_affairs": ["litigation", "legal_counsel", "legal_policy"],
            "corrections": ["federal_prisons", "inmate_programs", "reentry"],
            "national_security": ["counterterrorism", "cybersecurity", "foreign_intelligence"],
            "civil_rights": ["enforcement", "policy", "education"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "law_enforcement": {
                "description": "Federal law enforcement activities",
                "sub_domains": ["federal_law_enforcement", "criminal_investigation", "intelligence"]
            },
            "legal_affairs": {
                "description": "Legal representation and counsel",
                "sub_domains": ["litigation", "legal_counsel", "legal_policy"]
            },
            "corrections": {
                "description": "Management of federal corrections system",
                "sub_domains": ["federal_prisons", "inmate_programs", "reentry"]
            },
            "national_security": {
                "description": "Protection of national security",
                "sub_domains": ["counterterrorism", "cybersecurity", "foreign_intelligence"]
            },
            "civil_rights": {
                "description": "Protection of civil rights and liberties",
                "sub_domains": ["enforcement", "policy", "education"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "federal_criminal_law": {
                "name": "Federal Criminal Law",
                "description": "Federal criminal statutes and procedures",
                "components": ["criminal_code", "rules_of_procedure", "sentencing_guidelines"]
            },
            "civil_rights_law": {
                "name": "Civil Rights Laws",
                "description": "Laws protecting civil rights and liberties",
                "components": ["voting_rights", "nondiscrimination", "equal_protection"]
            },
            "national_security_law": {
                "name": "National Security Law",
                "description": "Legal framework for national security",
                "components": ["surveillance", "counterterrorism", "foreign_intelligence"]
            },
            "immigration_law": {
                "name": "Immigration Law",
                "description": "Laws governing immigration and naturalization",
                "components": ["visas", "asylum", "enforcement"]
            },
            "federal_litigation": {
                "name": "Federal Litigation Procedures",
                "description": "Procedures for federal litigation",
                "components": ["civil_procedure", "criminal_procedure", "appellate_procedure"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["law_enforcement", "national_security", "civil_rights"]
    },
    "housing": {
        "DEFAULT_DOMAINS": {
            "housing_assistance": ["public_housing", "rental_assistance", "homelessness"],
            "community_development": ["block_grants", "economic_development", "infrastructure"],
            "fair_housing": ["enforcement", "education", "policy"],
            "housing_finance": ["mortgage_insurance", "secondary_market", "risk_management"],
            "housing_policy": ["affordable_housing", "homeownership", "research"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "housing_assistance": {
                "description": "Programs to assist individuals and families with housing",
                "sub_domains": ["public_housing", "rental_assistance", "homelessness"]
            },
            "community_development": {
                "description": "Support for local community development efforts",
                "sub_domains": ["block_grants", "economic_development", "infrastructure"]
            },
            "fair_housing": {
                "description": "Elimination of housing discrimination",
                "sub_domains": ["enforcement", "education", "policy"]
            },
            "housing_finance": {
                "description": "Support for housing finance markets",
                "sub_domains": ["mortgage_insurance", "secondary_market", "risk_management"]
            },
            "housing_policy": {
                "description": "Development and analysis of housing policies",
                "sub_domains": ["affordable_housing", "homeownership", "research"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "fair_housing_act": {
                "name": "Fair Housing Act",
                "description": "Prohibits discrimination in housing",
                "components": ["discrimination_prohibitions", "enforcement", "accessibility"]
            },
            "cdbg": {
                "name": "Community Development Block Grant",
                "description": "Funding for community development",
                "components": ["entitlement_communities", "housing_rehabilitation", "public_facilities"]
            },
            "housing_act": {
                "name": "Housing Act",
                "description": "Framework for federal housing programs",
                "components": ["public_housing", "mortgage_insurance", "urban_renewal"]
            },
            "homeless_assistance": {
                "name": "Homeless Assistance Programs",
                "description": "Programs addressing homelessness",
                "components": ["emergency_solutions", "continuum_of_care", "permanent_housing"]
            },
            "section_8": {
                "name": "Section 8 Housing Choice Voucher Program",
                "description": "Rental assistance for low-income households",
                "components": ["tenant_based", "project_based", "eligibility"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["housing_assistance", "fair_housing", "housing_policy"]
    },
    "transportation": {
        "DEFAULT_DOMAINS": {
            "aviation": ["air_traffic_control", "aviation_safety", "airports"],
            "surface_transportation": ["highways", "railroads", "transit"],
            "maritime": ["ports", "waterways", "shipping"],
            "safety": ["vehicle_safety", "operator_safety", "infrastructure_safety"],
            "transportation_policy": ["planning", "research", "environmental_impact"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "aviation": {
                "description": "Air transportation system",
                "sub_domains": ["air_traffic_control", "aviation_safety", "airports"]
            },
            "surface_transportation": {
                "description": "Land-based transportation",
                "sub_domains": ["highways", "railroads", "transit"]
            },
            "maritime": {
                "description": "Water-based transportation",
                "sub_domains": ["ports", "waterways", "shipping"]
            },
            "safety": {
                "description": "Ensuring safety across transportation modes",
                "sub_domains": ["vehicle_safety", "operator_safety", "infrastructure_safety"]
            },
            "transportation_policy": {
                "description": "Policy development for transportation",
                "sub_domains": ["planning", "research", "environmental_impact"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "faa_regulations": {
                "name": "FAA Regulations",
                "description": "Regulations for aviation",
                "components": ["airworthiness", "operations", "airports"]
            },
            "fmcsa_regulations": {
                "name": "FMCSA Regulations",
                "description": "Regulations for motor carriers",
                "components": ["safety", "licensing", "hours_of_service"]
            },
            "nhtsa_standards": {
                "name": "NHTSA Vehicle Safety Standards",
                "description": "Standards for vehicle safety",
                "components": ["crashworthiness", "crash_avoidance", "post_crash"]
            },
            "fra_regulations": {
                "name": "FRA Railroad Safety Regulations",
                "description": "Regulations for railroad safety",
                "components": ["track_safety", "equipment_safety", "operating_practices"]
            },
            "highway_programs": {
                "name": "Federal Highway Programs",
                "description": "Programs for highway funding",
                "components": ["federal_aid", "interstate", "safety"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["aviation", "safety", "surface_transportation"]
    },
    "education": {
        "DEFAULT_DOMAINS": {
            "k12_education": ["elementary", "secondary", "special_education"],
            "higher_education": ["colleges", "universities", "community_colleges"],
            "student_financial_aid": ["grants", "loans", "work_study"],
            "education_research": ["statistics", "evaluation", "innovation"],
            "civil_rights_education": ["accessibility", "nondiscrimination", "equal_opportunity"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "k12_education": {
                "description": "Primary and secondary education",
                "sub_domains": ["elementary", "secondary", "special_education"]
            },
            "higher_education": {
                "description": "Post-secondary education",
                "sub_domains": ["colleges", "universities", "community_colleges"]
            },
            "student_financial_aid": {
                "description": "Financial assistance for students",
                "sub_domains": ["grants", "loans", "work_study"]
            },
            "education_research": {
                "description": "Research on education methods and outcomes",
                "sub_domains": ["statistics", "evaluation", "innovation"]
            },
            "civil_rights_education": {
                "description": "Protection of civil rights in education",
                "sub_domains": ["accessibility", "nondiscrimination", "equal_opportunity"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "essa": {
                "name": "Every Student Succeeds Act",
                "description": "Framework for K-12 education",
                "components": ["accountability", "state_plans", "funding"]
            },
            "idea": {
                "name": "Individuals with Disabilities Education Act",
                "description": "Support for students with disabilities",
                "components": ["free_appropriate_education", "individualized_education_program", "procedural_safeguards"]
            },
            "hea": {
                "name": "Higher Education Act",
                "description": "Framework for higher education",
                "components": ["student_aid", "accreditation", "institutional_support"]
            },
            "ferpa": {
                "name": "Family Educational Rights and Privacy Act",
                "description": "Protection of student records",
                "components": ["access_rights", "consent_requirements", "directory_information"]
            },
            "education_civil_rights": {
                "name": "Education Civil Rights Laws",
                "description": "Protection against discrimination",
                "components": ["title_vi", "title_ix", "section_504"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["k12_education", "student_financial_aid", "civil_rights_education"]
    },
    "veterans": {
        "DEFAULT_DOMAINS": {
            "healthcare": ["medical_centers", "outpatient_clinics", "mental_health"],
            "benefits": ["disability_compensation", "education", "pensions"],
            "memorial_services": ["national_cemeteries", "headstones", "burial_benefits"],
            "transition_assistance": ["employment", "housing", "readjustment"],
            "veterans_policy": ["research", "advocacy", "planning"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "healthcare": {
                "description": "Healthcare services for veterans",
                "sub_domains": ["medical_centers", "outpatient_clinics", "mental_health"]
            },
            "benefits": {
                "description": "Benefits for veterans and dependents",
                "sub_domains": ["disability_compensation", "education", "pensions"]
            },
            "memorial_services": {
                "description": "Memorial and burial services",
                "sub_domains": ["national_cemeteries", "headstones", "burial_benefits"]
            },
            "transition_assistance": {
                "description": "Assistance with transition to civilian life",
                "sub_domains": ["employment", "housing", "readjustment"]
            },
            "veterans_policy": {
                "description": "Policy development for veterans",
                "sub_domains": ["research", "advocacy", "planning"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "gi_bill": {
                "name": "GI Bill",
                "description": "Education benefits for veterans",
                "components": ["tuition", "housing_allowance", "books_stipend"]
            },
            "va_healthcare": {
                "name": "VA Healthcare System",
                "description": "Healthcare system for veterans",
                "components": ["enrollment", "services", "copayments"]
            },
            "va_disability": {
                "name": "VA Disability Compensation",
                "description": "Compensation for service-connected disabilities",
                "components": ["rating_schedule", "claims_process", "appeals"]
            },
            "vba_programs": {
                "name": "Veterans Benefits Administration Programs",
                "description": "Benefits programs for veterans",
                "components": ["compensation_pension", "education", "loan_guaranty"]
            },
            "veteran_caregiver": {
                "name": "Veteran Caregiver Support Program",
                "description": "Support for caregivers of veterans",
                "components": ["comprehensive_assistance", "general_caregiver_support", "respite_care"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["healthcare", "benefits", "transition_assistance"]
    },
    "interior": {
        "DEFAULT_DOMAINS": {
            "land_management": ["public_lands", "grazing", "resource_management"],
            "conservation": ["wildlife", "habitat", "endangered_species"],
            "national_parks": ["parks", "monuments", "recreation"],
            "indigenous_affairs": ["tribal_governance", "trust_responsibilities", "services"],
            "natural_resources": ["energy", "minerals", "water"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "land_management": {
                "description": "Management of public lands",
                "sub_domains": ["public_lands", "grazing", "resource_management"]
            },
            "conservation": {
                "description": "Conservation of natural resources",
                "sub_domains": ["wildlife", "habitat", "endangered_species"]
            },
            "national_parks": {
                "description": "Management of national parks and monuments",
                "sub_domains": ["parks", "monuments", "recreation"]
            },
            "indigenous_affairs": {
                "description": "Affairs related to indigenous peoples",
                "sub_domains": ["tribal_governance", "trust_responsibilities", "services"]
            },
            "natural_resources": {
                "description": "Management of natural resources",
                "sub_domains": ["energy", "minerals", "water"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "flpma": {
                "name": "Federal Land Policy and Management Act",
                "description": "Framework for public land management",
                "components": ["planning", "multiple_use", "withdrawals"]
            },
            "esa": {
                "name": "Endangered Species Act",
                "description": "Protection for threatened and endangered species",
                "components": ["listing", "critical_habitat", "recovery_plans"]
            },
            "nps_organic_act": {
                "name": "National Park Service Organic Act",
                "description": "Establishment of National Park Service",
                "components": ["conservation", "enjoyment", "management"]
            },
            "blm_regulations": {
                "name": "Bureau of Land Management Regulations",
                "description": "Regulations for public lands",
                "components": ["grazing", "minerals", "recreation"]
            },
            "tribal_self_governance": {
                "name": "Tribal Self-Governance Act",
                "description": "Framework for tribal self-governance",
                "components": ["compacts", "funding_agreements", "tribal_priority_allocations"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["land_management", "conservation", "indigenous_affairs"]
    },
    "commerce": {
        "DEFAULT_DOMAINS": {
            "economic_development": ["business_development", "economic_assistance", "trade_promotion"],
            "technology": ["standards", "telecommunications", "innovation"],
            "environment": ["weather", "oceans", "climate"],
            "trade": ["export_control", "trade_agreements", "market_access"],
            "statistics": ["economic_statistics", "census", "analysis"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "economic_development": {
                "description": "Promotion of economic growth",
                "sub_domains": ["business_development", "economic_assistance", "trade_promotion"]
            },
            "technology": {
                "description": "Development and standards for technology",
                "sub_domains": ["standards", "telecommunications", "innovation"]
            },
            "environment": {
                "description": "Environmental monitoring and research",
                "sub_domains": ["weather", "oceans", "climate"]
            },
            "trade": {
                "description": "International trade promotion and regulation",
                "sub_domains": ["export_control", "trade_agreements", "market_access"]
            },
            "statistics": {
                "description": "Collection and analysis of statistical data",
                "sub_domains": ["economic_statistics", "census", "analysis"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "export_regulations": {
                "name": "Export Administration Regulations",
                "description": "Regulations for export control",
                "components": ["commodity_classification", "licensing", "enforcement"]
            },
            "noaa_regulations": {
                "name": "NOAA Regulations",
                "description": "Regulations for oceanic and atmospheric activities",
                "components": ["fisheries", "coastal_management", "weather_services"]
            },
            "nist_standards": {
                "name": "NIST Standards",
                "description": "Technical standards development",
                "components": ["measurement", "cybersecurity", "manufacturing"]
            },
            "uspto_regulations": {
                "name": "USPTO Regulations",
                "description": "Regulations for patents and trademarks",
                "components": ["patent_examination", "trademark_registration", "fees"]
            },
            "census_regulations": {
                "name": "Census Bureau Regulations",
                "description": "Regulations for census and surveys",
                "components": ["decennial_census", "economic_census", "data_protection"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["economic_development", "technology", "trade"]
    },
    "labor": {
        "DEFAULT_DOMAINS": {
            "workforce_development": ["job_training", "employment_services", "apprenticeship"],
            "worker_protection": ["occupational_safety", "wage_standards", "benefits"],
            "labor_statistics": ["employment", "prices", "productivity"],
            "labor_relations": ["labor_management", "union_democracy", "mediation"],
            "labor_policy": ["research", "policy_development", "international_labor"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "workforce_development": {
                "description": "Development of workforce skills",
                "sub_domains": ["job_training", "employment_services", "apprenticeship"]
            },
            "worker_protection": {
                "description": "Protection of workers' rights and safety",
                "sub_domains": ["occupational_safety", "wage_standards", "benefits"]
            },
            "labor_statistics": {
                "description": "Collection and analysis of labor data",
                "sub_domains": ["employment", "prices", "productivity"]
            },
            "labor_relations": {
                "description": "Management of labor-management relations",
                "sub_domains": ["labor_management", "union_democracy", "mediation"]
            },
            "labor_policy": {
                "description": "Development of labor policies",
                "sub_domains": ["research", "policy_development", "international_labor"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "flsa": {
                "name": "Fair Labor Standards Act",
                "description": "Standards for wages and hours",
                "components": ["minimum_wage", "overtime", "child_labor"]
            },
            "osha_regulations": {
                "name": "OSHA Regulations",
                "description": "Regulations for workplace safety",
                "components": ["safety_standards", "hazard_communication", "inspections"]
            },
            "erisa": {
                "name": "Employee Retirement Income Security Act",
                "description": "Regulation of employee benefits",
                "components": ["reporting", "fiduciary_duties", "enforcement"]
            },
            "nlra": {
                "name": "National Labor Relations Act",
                "description": "Protection of rights to organize",
                "components": ["representation", "unfair_labor_practices", "collective_bargaining"]
            },
            "wioa": {
                "name": "Workforce Innovation and Opportunity Act",
                "description": "Framework for workforce development",
                "components": ["one_stop_centers", "training_programs", "performance_accountability"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["worker_protection", "workforce_development", "labor_statistics"]
    },
    "security": {
        "DEFAULT_DOMAINS": {
            "border_security": ["customs", "immigration_enforcement", "ports_of_entry"],
            "emergency_management": ["preparedness", "response", "recovery"],
            "cybersecurity": ["critical_infrastructure", "incident_response", "information_sharing"],
            "counterterrorism": ["intelligence", "prevention", "response"],
            "transportation_security": ["aviation", "maritime", "surface"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "border_security": {
                "description": "Security of national borders",
                "sub_domains": ["customs", "immigration_enforcement", "ports_of_entry"]
            },
            "emergency_management": {
                "description": "Management of emergency situations",
                "sub_domains": ["preparedness", "response", "recovery"]
            },
            "cybersecurity": {
                "description": "Security of cyber systems",
                "sub_domains": ["critical_infrastructure", "incident_response", "information_sharing"]
            },
            "counterterrorism": {
                "description": "Prevention and response to terrorism",
                "sub_domains": ["intelligence", "prevention", "response"]
            },
            "transportation_security": {
                "description": "Security of transportation systems",
                "sub_domains": ["aviation", "maritime", "surface"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "ina": {
                "name": "Immigration and Nationality Act",
                "description": "Framework for immigration",
                "components": ["admissions", "removal", "enforcement"]
            },
            "stafford_act": {
                "name": "Robert T. Stafford Disaster Relief and Emergency Assistance Act",
                "description": "Framework for disaster assistance",
                "components": ["declarations", "assistance", "mitigation"]
            },
            "fisma": {
                "name": "Federal Information Security Modernization Act",
                "description": "Framework for information security",
                "components": ["risk_management", "security_controls", "monitoring"]
            },
            "atsa": {
                "name": "Aviation and Transportation Security Act",
                "description": "Framework for transportation security",
                "components": ["screening", "air_marshals", "security_directives"]
            },
            "homeland_security_act": {
                "name": "Homeland Security Act",
                "description": "Establishment of Department of Homeland Security",
                "components": ["organization", "authorities", "functions"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["cybersecurity", "counterterrorism", "border_security"]
    },
    "energy": {
        "DEFAULT_DOMAINS": {
            "energy_research": ["basic_science", "applied_research", "development"],
            "nuclear_security": ["weapons", "nonproliferation", "naval_reactors"],
            "electricity": ["generation", "transmission", "distribution"],
            "energy_efficiency": ["buildings", "industry", "transportation"],
            "renewable_energy": ["solar", "wind", "geothermal"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "energy_research": {
                "description": "Research on energy technologies",
                "sub_domains": ["basic_science", "applied_research", "development"]
            },
            "nuclear_security": {
                "description": "Security of nuclear materials and technology",
                "sub_domains": ["weapons", "nonproliferation", "naval_reactors"]
            },
            "electricity": {
                "description": "Electric power system",
                "sub_domains": ["generation", "transmission", "distribution"]
            },
            "energy_efficiency": {
                "description": "Efficient use of energy",
                "sub_domains": ["buildings", "industry", "transportation"]
            },
            "renewable_energy": {
                "description": "Development and deployment of renewable energy",
                "sub_domains": ["solar", "wind", "geothermal"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "aea": {
                "name": "Atomic Energy Act",
                "description": "Framework for nuclear energy",
                "components": ["licensing", "regulation", "export_control"]
            },
            "epact": {
                "name": "Energy Policy Act",
                "description": "Framework for energy policy",
                "components": ["efficiency", "production", "infrastructure"]
            },
            "fra": {
                "name": "Federal Power Act",
                "description": "Regulation of electricity",
                "components": ["wholesale_markets", "transmission", "reliability"]
            },
            "eisa": {
                "name": "Energy Independence and Security Act",
                "description": "Framework for energy security",
                "components": ["efficiency_standards", "renewable_fuels", "grid_modernization"]
            },
            "doe_orders": {
                "name": "DOE Orders",
                "description": "DOE management directives",
                "components": ["nuclear_safety", "security", "environment"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["nuclear_security", "renewable_energy", "energy_efficiency"]
    },
    "diplomacy": {
        "DEFAULT_DOMAINS": {
            "bilateral_relations": ["diplomacy", "economic_relations", "security_cooperation"],
            "multilateral_affairs": ["international_organizations", "treaties", "global_issues"],
            "consular_services": ["visas", "passport_services", "citizen_services"],
            "security_assistance": ["military_aid", "foreign_military_sales", "training"],
            "public_diplomacy": ["educational_exchanges", "cultural_programs", "information_programs"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "bilateral_relations": {
                "description": "Relations between countries",
                "sub_domains": ["diplomacy", "economic_relations", "security_cooperation"]
            },
            "multilateral_affairs": {
                "description": "Engagement with international organizations",
                "sub_domains": ["international_organizations", "treaties", "global_issues"]
            },
            "consular_services": {
                "description": "Services for citizens and foreign nationals",
                "sub_domains": ["visas", "passport_services", "citizen_services"]
            },
            "security_assistance": {
                "description": "Assistance for security cooperation",
                "sub_domains": ["military_aid", "foreign_military_sales", "training"]
            },
            "public_diplomacy": {
                "description": "Public engagement and outreach",
                "sub_domains": ["educational_exchanges", "cultural_programs", "information_programs"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "faa": {
                "name": "Foreign Assistance Act",
                "description": "Framework for foreign assistance",
                "components": ["development_assistance", "economic_support", "military_assistance"]
            },
            "aeca": {
                "name": "Arms Export Control Act",
                "description": "Framework for arms exports",
                "components": ["foreign_military_sales", "direct_commercial_sales", "end_use_monitoring"]
            },
            "ina_visa": {
                "name": "Immigration and Nationality Act (Visa Provisions)",
                "description": "Framework for visa issuance",
                "components": ["nonimmigrant_visas", "immigrant_visas", "visa_waivers"]
            },
            "diplomatic_relations_act": {
                "name": "Diplomatic Relations Act",
                "description": "Framework for diplomatic relations",
                "components": ["diplomatic_immunity", "consular_immunity", "property"]
            },
            "mutual_security_act": {
                "name": "Mutual Security Act",
                "description": "Framework for security cooperation",
                "components": ["military_assistance", "economic_assistance", "technical_cooperation"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["bilateral_relations", "consular_services", "security_assistance"]
    },
    "environment": {
        "DEFAULT_DOMAINS": {
            "air_quality": ["air_pollution", "emissions", "standards"],
            "water_quality": ["drinking_water", "surface_water", "groundwater"],
            "chemical_safety": ["toxics", "pesticides", "risk_assessment"],
            "waste_management": ["hazardous_waste", "solid_waste", "recycling"],
            "climate_change": ["greenhouse_gases", "adaptation", "mitigation"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "air_quality": {
                "description": "Protection of air resources",
                "sub_domains": ["air_pollution", "emissions", "standards"]
            },
            "water_quality": {
                "description": "Protection of water resources",
                "sub_domains": ["drinking_water", "surface_water", "groundwater"]
            },
            "chemical_safety": {
                "description": "Management of chemicals and toxics",
                "sub_domains": ["toxics", "pesticides", "risk_assessment"]
            },
            "waste_management": {
                "description": "Management of waste",
                "sub_domains": ["hazardous_waste", "solid_waste", "recycling"]
            },
            "climate_change": {
                "description": "Addressing climate change",
                "sub_domains": ["greenhouse_gases", "adaptation", "mitigation"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "caa": {
                "name": "Clean Air Act",
                "description": "Framework for air quality",
                "components": ["national_ambient_air_quality_standards", "state_implementation_plans", "emissions_standards"]
            },
            "cwa": {
                "name": "Clean Water Act",
                "description": "Framework for water quality",
                "components": ["water_quality_standards", "discharge_permits", "wetlands_protection"]
            },
            "rcra": {
                "name": "Resource Conservation and Recovery Act",
                "description": "Framework for waste management",
                "components": ["hazardous_waste", "solid_waste", "underground_storage_tanks"]
            },
            "tsca": {
                "name": "Toxic Substances Control Act",
                "description": "Framework for chemical regulation",
                "components": ["chemical_testing", "new_chemicals", "existing_chemicals"]
            },
            "superfund": {
                "name": "Comprehensive Environmental Response, Compensation, and Liability Act",
                "description": "Framework for hazardous site cleanup",
                "components": ["site_assessment", "remedial_action", "liability"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["air_quality", "water_quality", "chemical_safety"]
    },
    "business": {
        "DEFAULT_DOMAINS": {
            "lending": ["small_business_loans", "microloans", "disaster_loans"],
            "entrepreneurship": ["business_development", "mentoring", "training"],
            "contracting": ["government_contracting", "subcontracting", "certification"],
            "advocacy": ["regulatory_fairness", "policy", "research"],
            "disaster_assistance": ["loans", "grants", "recovery"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "lending": {
                "description": "Financial assistance for small businesses",
                "sub_domains": ["small_business_loans", "microloans", "disaster_loans"]
            },
            "entrepreneurship": {
                "description": "Development of entrepreneurs",
                "sub_domains": ["business_development", "mentoring", "training"]
            },
            "contracting": {
                "description": "Government contracting opportunities",
                "sub_domains": ["government_contracting", "subcontracting", "certification"]
            },
            "advocacy": {
                "description": "Advocacy for small businesses",
                "sub_domains": ["regulatory_fairness", "policy", "research"]
            },
            "disaster_assistance": {
                "description": "Assistance for disaster recovery",
                "sub_domains": ["loans", "grants", "recovery"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "small_business_act": {
                "name": "Small Business Act",
                "description": "Framework for small business programs",
                "components": ["loan_programs", "contracting_programs", "development_programs"]
            },
            "jobs_act": {
                "name": "Small Business Jobs Act",
                "description": "Framework for small business growth",
                "components": ["lending_programs", "tax_provisions", "contracting_provisions"]
            },
            "procurement_policy": {
                "name": "Federal Acquisition Regulation",
                "description": "Framework for federal procurement",
                "components": ["small_business_set_asides", "subcontracting_plans", "contract_bundling"]
            },
            "entrepreneurship_policy": {
                "name": "Small Business Development Centers",
                "description": "Framework for entrepreneurship development",
                "components": ["training", "counseling", "technical_assistance"]
            },
            "disaster_recovery": {
                "name": "Disaster Loan Program",
                "description": "Framework for disaster assistance",
                "components": ["economic_injury", "physical_damage", "mitigation"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["lending", "entrepreneurship", "contracting"]
    },
    "social": {
        "DEFAULT_DOMAINS": {
            "retirement": ["old_age_benefits", "survivors_benefits", "medicare"],
            "disability": ["disability_insurance", "evaluation", "appeals"],
            "supplemental_security": ["needs_based_assistance", "eligibility", "payments"],
            "program_integrity": ["fraud_prevention", "quality_review", "oversight"],
            "customer_service": ["field_offices", "online_services", "card_services"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "retirement": {
                "description": "Retirement and survivors benefits",
                "sub_domains": ["old_age_benefits", "survivors_benefits", "medicare"]
            },
            "disability": {
                "description": "Disability benefits",
                "sub_domains": ["disability_insurance", "evaluation", "appeals"]
            },
            "supplemental_security": {
                "description": "Needs-based assistance",
                "sub_domains": ["needs_based_assistance", "eligibility", "payments"]
            },
            "program_integrity": {
                "description": "Ensuring program integrity",
                "sub_domains": ["fraud_prevention", "quality_review", "oversight"]
            },
            "customer_service": {
                "description": "Service to beneficiaries",
                "sub_domains": ["field_offices", "online_services", "card_services"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "social_security_act": {
                "name": "Social Security Act",
                "description": "Framework for social security programs",
                "components": ["oasi", "di", "hi"]
            },
            "ssi": {
                "name": "Supplemental Security Income",
                "description": "Framework for needs-based assistance",
                "components": ["eligibility", "payments", "resources"]
            },
            "disability_determination": {
                "name": "Disability Determination Process",
                "description": "Framework for disability evaluation",
                "components": ["initial_determination", "reconsideration", "hearings"]
            },
            "earnings_record": {
                "name": "Earnings Record System",
                "description": "Framework for earnings records",
                "components": ["earnings_posting", "corrections", "reporting"]
            },
            "enumeration": {
                "name": "Social Security Number System",
                "description": "Framework for SSN issuance",
                "components": ["enumeration", "verification", "protection"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["retirement", "disability", "supplemental_security"]
    },
    "space": {
        "DEFAULT_DOMAINS": {
            "human_spaceflight": ["international_space_station", "commercial_crew", "exploration"],
            "science": ["earth_science", "planetary_science", "astrophysics"],
            "aeronautics": ["aviation_safety", "airspace_operations", "advanced_technologies"],
            "technology": ["space_technology", "mission_support", "innovation"],
            "operations": ["launch_services", "mission_operations", "communications"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "human_spaceflight": {
                "description": "Human exploration of space",
                "sub_domains": ["international_space_station", "commercial_crew", "exploration"]
            },
            "science": {
                "description": "Scientific investigation of space and Earth",
                "sub_domains": ["earth_science", "planetary_science", "astrophysics"]
            },
            "aeronautics": {
                "description": "Research and development for aviation",
                "sub_domains": ["aviation_safety", "airspace_operations", "advanced_technologies"]
            },
            "technology": {
                "description": "Development of space technologies",
                "sub_domains": ["space_technology", "mission_support", "innovation"]
            },
            "operations": {
                "description": "Operations of space missions",
                "sub_domains": ["launch_services", "mission_operations", "communications"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "space_act": {
                "name": "National Aeronautics and Space Act",
                "description": "Framework for NASA",
                "components": ["research", "development", "operations"]
            },
            "authorization_act": {
                "name": "NASA Authorization Act",
                "description": "Framework for NASA programs",
                "components": ["human_spaceflight", "science", "aeronautics"]
            },
            "space_policy": {
                "name": "National Space Policy",
                "description": "Framework for space activities",
                "components": ["civil_space", "commercial_space", "national_security_space"]
            },
            "earth_science": {
                "name": "Earth Science Program",
                "description": "Framework for Earth observation",
                "components": ["earth_observing_system", "applied_science", "research"]
            },
            "exploration_systems": {
                "name": "Exploration Systems Development",
                "description": "Framework for human exploration",
                "components": ["orion", "sls", "ground_systems"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["human_spaceflight", "science", "technology"]
    },
    "science": {
        "DEFAULT_DOMAINS": {
            "biological_sciences": ["molecular_biology", "organismal_biology", "environmental_biology"],
            "computer_science": ["foundations", "systems", "intelligent_systems"],
            "engineering": ["chemical_engineering", "civil_engineering", "electrical_engineering"],
            "geosciences": ["atmospheric_sciences", "earth_sciences", "ocean_sciences"],
            "social_sciences": ["economics", "political_science", "sociology"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "biological_sciences": {
                "description": "Research in biological sciences",
                "sub_domains": ["molecular_biology", "organismal_biology", "environmental_biology"]
            },
            "computer_science": {
                "description": "Research in computer science",
                "sub_domains": ["foundations", "systems", "intelligent_systems"]
            },
            "engineering": {
                "description": "Research in engineering",
                "sub_domains": ["chemical_engineering", "civil_engineering", "electrical_engineering"]
            },
            "geosciences": {
                "description": "Research in geosciences",
                "sub_domains": ["atmospheric_sciences", "earth_sciences", "ocean_sciences"]
            },
            "social_sciences": {
                "description": "Research in social sciences",
                "sub_domains": ["economics", "political_science", "sociology"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "nsf_act": {
                "name": "National Science Foundation Act",
                "description": "Framework for NSF",
                "components": ["research", "education", "infrastructure"]
            },
            "merit_review": {
                "name": "Merit Review Process",
                "description": "Framework for proposal review",
                "components": ["intellectual_merit", "broader_impacts", "review_criteria"]
            },
            "broader_impacts": {
                "name": "Broader Impacts Framework",
                "description": "Framework for societal impacts",
                "components": ["education", "participation", "infrastructure"]
            },
            "career_programs": {
                "name": "CAREER Program",
                "description": "Framework for early career development",
                "components": ["research", "education", "integration"]
            },
            "convergence_research": {
                "name": "Convergence Research",
                "description": "Framework for interdisciplinary research",
                "components": ["convergence", "interdisciplinary", "transdisciplinary"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["biological_sciences", "computer_science", "engineering"]
    },
    "development": {
        "DEFAULT_DOMAINS": {
            "global_health": ["maternal_health", "child_health", "infectious_diseases"],
            "democracy": ["governance", "civil_society", "human_rights"],
            "economic_growth": ["trade", "financial_sector", "private_sector"],
            "humanitarian_assistance": ["disaster_response", "refugees", "food_assistance"],
            "education": ["basic_education", "higher_education", "workforce_development"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "global_health": {
                "description": "Improving health outcomes globally",
                "sub_domains": ["maternal_health", "child_health", "infectious_diseases"]
            },
            "democracy": {
                "description": "Promoting democracy and governance",
                "sub_domains": ["governance", "civil_society", "human_rights"]
            },
            "economic_growth": {
                "description": "Promoting economic growth",
                "sub_domains": ["trade", "financial_sector", "private_sector"]
            },
            "humanitarian_assistance": {
                "description": "Providing humanitarian assistance",
                "sub_domains": ["disaster_response", "refugees", "food_assistance"]
            },
            "education": {
                "description": "Improving education outcomes",
                "sub_domains": ["basic_education", "higher_education", "workforce_development"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "foreign_assistance_act": {
                "name": "Foreign Assistance Act",
                "description": "Framework for foreign assistance",
                "components": ["development_assistance", "economic_support", "humanitarian_assistance"]
            },
            "pepfar": {
                "name": "President's Emergency Plan for AIDS Relief",
                "description": "Framework for HIV/AIDS programs",
                "components": ["prevention", "care", "treatment"]
            },
            "feed_the_future": {
                "name": "Feed the Future",
                "description": "Framework for food security",
                "components": ["agriculture", "nutrition", "resilience"]
            },
            "global_health_initiative": {
                "name": "Global Health Initiative",
                "description": "Framework for health programs",
                "components": ["maternal_health", "child_health", "infectious_diseases"]
            },
            "power_africa": {
                "name": "Power Africa",
                "description": "Framework for energy access",
                "components": ["generation", "distribution", "connections"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["global_health", "democracy", "economic_growth"]
    },
    "communications": {
        "DEFAULT_DOMAINS": {
            "wireless": ["mobile", "broadband", "spectrum"],
            "wireline": ["telephone", "broadband", "infrastructure"],
            "media": ["broadcasting", "cable", "satellite"],
            "public_safety": ["emergency_communications", "911", "alerting"],
            "consumer": ["privacy", "accessibility", "competition"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "wireless": {
                "description": "Wireless communications",
                "sub_domains": ["mobile", "broadband", "spectrum"]
            },
            "wireline": {
                "description": "Wireline communications",
                "sub_domains": ["telephone", "broadband", "infrastructure"]
            },
            "media": {
                "description": "Media communications",
                "sub_domains": ["broadcasting", "cable", "satellite"]
            },
            "public_safety": {
                "description": "Public safety communications",
                "sub_domains": ["emergency_communications", "911", "alerting"]
            },
            "consumer": {
                "description": "Consumer protection",
                "sub_domains": ["privacy", "accessibility", "competition"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "communications_act": {
                "name": "Communications Act",
                "description": "Framework for communications regulation",
                "components": ["common_carriers", "broadcasters", "cable"]
            },
            "telecommunications_act": {
                "name": "Telecommunications Act",
                "description": "Framework for telecommunications",
                "components": ["competition", "universal_service", "broadband"]
            },
            "spectrum_policy": {
                "name": "Spectrum Policy",
                "description": "Framework for spectrum management",
                "components": ["allocations", "auctions", "licensing"]
            },
            "media_ownership": {
                "name": "Media Ownership Rules",
                "description": "Framework for media ownership",
                "components": ["local_ownership", "national_ownership", "cross_ownership"]
            },
            "universal_service": {
                "name": "Universal Service Fund",
                "description": "Framework for universal service",
                "components": ["high_cost", "low_income", "schools_libraries"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["wireless", "wireline", "public_safety"]
    },
    "personnel": {
        "DEFAULT_DOMAINS": {
            "employment": ["hiring", "classification", "compensation"],
            "benefits": ["health_benefits", "retirement", "insurance"],
            "workforce_management": ["performance_management", "training", "labor_relations"],
            "oversight": ["accountability", "compliance", "ethics"],
            "personnel_systems": ["systems", "information_technology", "records"]
        },
        "DEFAULT_DOMAINS_FULL": {
            "employment": {
                "description": "Federal employment services",
                "sub_domains": ["hiring", "classification", "compensation"]
            },
            "benefits": {
                "description": "Federal employee benefits",
                "sub_domains": ["health_benefits", "retirement", "insurance"]
            },
            "workforce_management": {
                "description": "Federal workforce management",
                "sub_domains": ["performance_management", "training", "labor_relations"]
            },
            "oversight": {
                "description": "Federal personnel oversight",
                "sub_domains": ["accountability", "compliance", "ethics"]
            },
            "personnel_systems": {
                "description": "Federal personnel systems",
                "sub_domains": ["systems", "information_technology", "records"]
            }
        },
        "DEFAULT_FRAMEWORKS": {
            "csra": {
                "name": "Civil Service Reform Act",
                "description": "Framework for civil service",
                "components": ["merit_systems", "performance_management", "labor_relations"]
            },
            "fehba": {
                "name": "Federal Employees Health Benefits Act",
                "description": "Framework for health benefits",
                "components": ["health_plans", "enrollment", "premiums"]
            },
            "fersa": {
                "name": "Federal Employees Retirement System Act",
                "description": "Framework for retirement",
                "components": ["defined_benefit", "thrift_savings_plan", "social_security"]
            },
            "personnel_assessment": {
                "name": "Federal Personnel Assessment Framework",
                "description": "Framework for assessments",
                "components": ["job_analysis", "assessment_methods", "validation"]
            },
            "performance_management": {
                "name": "Performance Management System",
                "description": "Framework for performance management",
                "components": ["planning", "monitoring", "evaluating"]
            }
        },
        "HIGH_PRIORITY_DOMAINS": ["employment", "benefits", "workforce_management"]
    }
}

class AgencyGenerator:
    """
    Generator for agency-specific components.
    """
    
    def __init__(self, base_dir: str, config_file: str, templates_dir: str) -> None:
        """
        Initialize the agency generator.
        
        Args:
            base_dir: Base directory for agency interface
            config_file: Path to configuration file
            templates_dir: Directory for ASCII art templates
        """
        self.base_dir = base_dir
        self.config_file = config_file
        self.templates_dir = templates_dir
        self.config = self._load_config()
        
        # Ensure directories exist
        self._ensure_dirs()
    
    def _load_config(self) -> dict:
        """Load configuration file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return {"agencies": [], "topics": {}}
    
    def _ensure_dirs(self) -> None:
        """Ensure required directories exist."""
        directories = [
            os.path.join(self.base_dir, "agency_issue_finder", "agencies"),
            os.path.join(self.base_dir, "agencies"),
            self.templates_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def generate_agency(self, agency_acronym: str, component: str = None) -> bool:
        """
        Generate components for a specific agency.

        Args:
            agency_acronym: Agency acronym
            component: Specific component to generate (ascii_art, issue_finder, research_connector, or None for all)

        Returns:
            True if successful, False otherwise
        """
        # Find agency in config
        agency_data = None
        for agency in self.config.get("agencies", []):
            if agency.get("acronym") == agency_acronym:
                agency_data = agency
                break

        if not agency_data:
            print(f"Error: Agency {agency_acronym} not found in configuration.")
            return False

        # Get agency information
        agency = agency_data["acronym"]
        name = agency_data["name"]
        domain = agency_data.get("domain", "general")

        try:
            # If a specific component is specified, generate only that component
            if component:
                if component == "ascii_art":
                    print(f"Generating ASCII art for {agency}...")
                    if not self._generate_ascii_art(agency, name):
                        print(f"Warning: Failed to generate ASCII art for {agency}.")
                        return False
                elif component == "issue_finder":
                    print(f"Generating issue finder for {agency}...")
                    if not self._generate_issue_finder(agency, name, domain):
                        print(f"Warning: Failed to generate issue finder for {agency}.")
                        return False
                elif component == "research_connector":
                    print(f"Generating research connector for {agency}...")
                    if not self._generate_research_connector(agency, name, domain):
                        print(f"Warning: Failed to generate research connector for {agency}.")
                        return False
                else:
                    print(f"Error: Invalid component {component}. Valid components are: ascii_art, issue_finder, research_connector.")
                    return False

                print(f"Successfully generated {component} for {agency}.")
                return True

            # Otherwise generate all components
            else:
                # Generate ASCII art
                print(f"Generating ASCII art for {agency}...")
                if not self._generate_ascii_art(agency, name):
                    print(f"Warning: Failed to generate ASCII art for {agency}.")

                # Generate issue finder
                print(f"Generating issue finder for {agency}...")
                if not self._generate_issue_finder(agency, name, domain):
                    print(f"Warning: Failed to generate issue finder for {agency}.")

                # Generate research connector
                print(f"Generating research connector for {agency}...")
                if not self._generate_research_connector(agency, name, domain):
                    print(f"Warning: Failed to generate research connector for {agency}.")

                print(f"Successfully generated components for {agency}.")
                return True

        except Exception as e:
            print(f"Error generating components for {agency}: {e}")
            return False
    
    def _generate_ascii_art(self, agency: str, name: str) -> bool:
        """
        Generate ASCII art for an agency.
        
        Args:
            agency: Agency acronym
            name: Agency name
            
        Returns:
            True if successful, False otherwise
        """
        # Define ASCII art characters for agency acronym
        ascii_chars = {}
        for i, char in enumerate(agency):
            if char.isalpha():
                ascii_chars[f"ASCII_LINE{i+1}"] = self._generate_ascii_char(char)
            else:
                ascii_chars[f"ASCII_LINE{i+1}"] = " " * 10
        
        # Fill any remaining lines with spaces
        for i in range(len(agency) + 1, 6):
            ascii_chars[f"ASCII_LINE{i}"] = " " * 10
        
        # Create template substitution dictionary
        substitutions = {
            "AGENCY_FULL_NAME": name,
            **ascii_chars
        }
        
        # Generate ASCII art from template
        template = Template(ASCII_ART_TEMPLATE)
        ascii_art = template.substitute(**substitutions)
        
        # Write ASCII art to file
        ascii_art_file = os.path.join(self.templates_dir, f"{agency.lower()}_ascii.txt")
        try:
            with open(ascii_art_file, 'w') as f:
                f.write(ascii_art)
            return True
        except Exception as e:
            print(f"Error writing ASCII art file: {e}")
            return False
    
    def _generate_ascii_char(self, char: str) -> str:
        """
        Generate ASCII art for a single character.
        
        Args:
            char: Character to generate ASCII art for
            
        Returns:
            ASCII art for the character
        """
        char = char.upper()
        if char == 'A':
            return " █████  "
        elif char == 'B':
            return "██████  "
        elif char == 'C':
            return " █████  "
        elif char == 'D':
            return "██████  "
        elif char == 'E':
            return "███████ "
        elif char == 'F':
            return "███████ "
        elif char == 'G':
            return " █████  "
        elif char == 'H':
            return "██   ██ "
        elif char == 'I':
            return "███████ "
        elif char == 'J':
            return "     ██ "
        elif char == 'K':
            return "██  ███ "
        elif char == 'L':
            return "██      "
        elif char == 'M':
            return "██   ██ "
        elif char == 'N':
            return "███  ██ "
        elif char == 'O':
            return " █████  "
        elif char == 'P':
            return "██████  "
        elif char == 'Q':
            return " █████  "
        elif char == 'R':
            return "██████  "
        elif char == 'S':
            return " █████  "
        elif char == 'T':
            return "███████ "
        elif char == 'U':
            return "██   ██ "
        elif char == 'V':
            return "██   ██ "
        elif char == 'W':
            return "██   ██ "
        elif char == 'X':
            return "██   ██ "
        elif char == 'Y':
            return "██   ██ "
        elif char == 'Z':
            return "███████ "
        else:
            return "        "
    
    def _generate_issue_finder(self, agency: str, name: str, domain: str) -> bool:
        """
        Generate issue finder for an agency.
        
        Args:
            agency: Agency acronym
            name: Agency name
            domain: Agency domain
            
        Returns:
            True if successful, False otherwise
        """
        # Get domain templates
        domain_templates = DOMAIN_TEMPLATES.get(domain, DOMAIN_TEMPLATES["healthcare"])
        
        # Create template substitution dictionary
        substitutions = {
            "AGENCY": agency,
            "AGENCY_NAME": name,
            "AGENCY_LOWER": agency.lower(),
            "DOMAIN": domain,
            "DOMAIN_VAR": domain,
            "DOMAIN_TITLE": domain.title(),
            "DEFAULT_DOMAINS": json.dumps(domain_templates["DEFAULT_DOMAINS"], indent=8),
            "HIGH_PRIORITY_DOMAINS": json.dumps(domain_templates["HIGH_PRIORITY_DOMAINS"], indent=8)
        }
        
        # Generate issue finder from template
        template = Template(ISSUE_FINDER_TEMPLATE)
        issue_finder = template.substitute(**substitutions)
        
        # Write issue finder to file
        issue_finder_file = os.path.join(self.base_dir, "agency_issue_finder", "agencies", f"{agency.lower()}_finder.py")
        try:
            with open(issue_finder_file, 'w') as f:
                f.write(issue_finder)
            return True
        except Exception as e:
            print(f"Error writing issue finder file: {e}")
            return False
    
    def _generate_research_connector(self, agency: str, name: str, domain: str) -> bool:
        """
        Generate research connector for an agency.
        
        Args:
            agency: Agency acronym
            name: Agency name
            domain: Agency domain
            
        Returns:
            True if successful, False otherwise
        """
        # Get domain templates
        domain_templates = DOMAIN_TEMPLATES.get(domain, DOMAIN_TEMPLATES["healthcare"])
        
        # Create template substitution dictionary
        substitutions = {
            "AGENCY": agency,
            "AGENCY_NAME": name,
            "AGENCY_LOWER": agency.lower(),
            "DOMAIN": domain,
            "DOMAIN_VAR": domain,
            "DOMAIN_TITLE": domain.title(),
            "DEFAULT_DOMAINS_FULL": json.dumps(domain_templates["DEFAULT_DOMAINS_FULL"], indent=8),
            "DEFAULT_FRAMEWORKS": json.dumps(domain_templates["DEFAULT_FRAMEWORKS"], indent=8)
        }
        
        # Generate research connector from template
        template = Template(RESEARCH_CONNECTOR_TEMPLATE)
        research_connector = template.substitute(**substitutions)
        
        # Write research connector to file
        connector_file = os.path.join(self.base_dir, "agencies", f"{agency.lower()}_connector.py")
        try:
            with open(connector_file, 'w') as f:
                f.write(research_connector)
            return True
        except Exception as e:
            print(f"Error writing research connector file: {e}")
            return False
    
    def generate_all_agencies(self) -> dict:
        """
        Generate components for all agencies in the configuration.
        
        Returns:
            Dictionary with status for each agency
        """
        results = {}
        
        for agency_data in self.config.get("agencies", []):
            agency = agency_data.get("acronym")
            if agency:
                print(f"Generating components for {agency}...")
                results[agency] = self.generate_agency(agency)
        
        return results
    
    def generate_batch(self, tier: int) -> dict:
        """
        Generate components for agencies in a specific tier.
        
        Args:
            tier: Agency tier
            
        Returns:
            Dictionary with status for each agency
        """
        results = {}
        
        for agency_data in self.config.get("agencies", []):
            agency_tier = agency_data.get("tier")
            agency = agency_data.get("acronym")
            
            if agency_tier == tier and agency:
                print(f"Generating components for {agency} (Tier {tier})...")
                results[agency] = self.generate_agency(agency)
        
        return results


def main():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="Agency Generator for Codex CLI")
    parser.add_argument("--agency", help="Agency acronym to generate components for")
    parser.add_argument("--component", choices=["ascii_art", "issue_finder", "research_connector"],
                      help="Specific component to generate (if --agency is specified)")
    parser.add_argument("--all", action="store_true", help="Generate components for all agencies")
    parser.add_argument("--tier", type=int, help="Generate components for agencies in a specific tier")
    parser.add_argument("--base-dir", default=os.path.dirname(os.path.abspath(__file__)),
                       help="Base directory for agency interface")
    parser.add_argument("--config-file", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                            "config", "agency_data.json"),
                       help="Path to configuration file")
    parser.add_argument("--templates-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                             "templates"),
                       help="Directory for ASCII art templates")

    args = parser.parse_args()

    generator = AgencyGenerator(args.base_dir, args.config_file, args.templates_dir)

    if args.agency:
        # Generate components for a specific agency
        success = generator.generate_agency(args.agency, args.component)
        component_str = f" ({args.component})" if args.component else ""
        print(f"Generation {'succeeded' if success else 'failed'} for {args.agency}{component_str}.")
    elif args.tier is not None:
        # Generate components for agencies in a specific tier
        results = generator.generate_batch(args.tier)

        successes = sum(1 for success in results.values() if success)
        failures = sum(1 for success in results.values() if not success)

        print(f"Generation completed for Tier {args.tier}: {successes} succeeded, {failures} failed.")

        if failures > 0:
            print("Failed agencies:")
            for agency, success in results.items():
                if not success:
                    print(f"  - {agency}")
    elif args.all:
        # Generate components for all agencies
        results = generator.generate_all_agencies()

        successes = sum(1 for success in results.values() if success)
        failures = sum(1 for success in results.values() if not success)

        print(f"Generation completed: {successes} succeeded, {failures} failed.")

        if failures > 0:
            print("Failed agencies:")
            for agency, success in results.items():
                if not success:
                    print(f"  - {agency}")
    else:
        print("Error: No action specified. Use --agency, --tier, or --all.")


if __name__ == "__main__":
    main()