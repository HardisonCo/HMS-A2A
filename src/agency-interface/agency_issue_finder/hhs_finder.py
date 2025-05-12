#!/usr/bin/env python3
"""
HHS Issue Finder

A specialized issue finder for the Department of Health and Human Services (HHS)
that identifies healthcare-related issues and prepares research context for Codex CLI.
"""

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

class HHSIssueFinder(AgencyIssueFinder):
    """
    HHS-specific issue finder implementation.
    Identifies healthcare-related issues and prepares research context.
    """
    
    def __init__(self, config_dir: str, data_dir: str) -> None:
        """
        Initialize the HHS issue finder.
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing agency data
        """
        super().__init__("HHS", config_dir, data_dir)
        self.healthcare_domains = self._load_healthcare_domains()
    
    def _load_healthcare_domains(self) -> Dict[str, List[str]]:
        """Load healthcare domain information."""
        domains_file = os.path.join(self.data_dir, "hhs", "healthcare_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise AgencyIssueFinderException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
            "public_health": ["epidemiology", "disease_prevention", "health_promotion"],
            "healthcare_delivery": ["primary_care", "hospital_care", "long_term_care"],
            "health_insurance": ["medicare", "medicaid", "private_insurance"],
            "medical_research": ["clinical_research", "biomedical_research", "health_services_research"],
            "health_policy": ["regulatory_policy", "payment_policy", "public_health_policy"]
        }
    
    def find_issues(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find current issues for HHS.
        
        Args:
            topic: Optional topic to filter issues
            
        Returns:
            List of issues found
        """
        # Start with empty issues list
        self.issues = []
        
        # If a specific topic is provided, find relevant issues
        if topic:
            # Check if topic matches any healthcare domain
            for domain, subdomains in self.healthcare_domains.items():
                if topic.lower() in domain.lower() or topic.lower() in [s.lower() for s in subdomains]:
                    self.issues.extend(self._get_domain_issues(domain))
        
        # If no topic is specified or no issues found for topic, return all high-priority issues
        if not self.issues:
            for domain in self.healthcare_domains:
                self.issues.extend(self._get_domain_issues(domain, high_priority_only=True))
        
        # If still no issues found, add a default healthcare issue
        if not self.issues:
            self.issues.append({
                "id": "HHS-GEN-001",
                "title": "Healthcare Systems Integration Analysis",
                "status": "pending",
                "priority": "high",
                "description": "Analysis of integration points between healthcare systems and components.",
                "affected_areas": ["All healthcare domains"],
                "detection_date": datetime.now().strftime("%Y-%m-%d"),
                "resources": [
                    {"type": "implementation_plan", "path": "HHS-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-EHR/"}
                ]
            })
        
        return self.issues
    
    def _get_domain_issues(self, domain: str, high_priority_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get issues for a specific healthcare domain.
        
        Args:
            domain: Healthcare domain
            high_priority_only: Only return high priority issues
            
        Returns:
            List of domain issues
        """
        issues = []
        
        # Healthcare domain-specific issues
        if domain == "public_health":
            issues.append({
                "id": "HHS-PH-001",
                "title": "Public Health Alert System Integration",
                "status": "active",
                "priority": "high",
                "description": "Integration of public health alert system with HMS components.",
                "affected_areas": ["Disease surveillance", "Emergency response", "Healthcare facilities"],
                "detection_date": "2023-05-01",
                "resources": [
                    {"type": "implementation_plan", "path": "HHS-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-EHR/"}
                ]
            })
        
        elif domain == "healthcare_delivery":
            issues.append({
                "id": "HHS-HD-001",
                "title": "Care Coordination System Enhancement",
                "status": "active",
                "priority": "medium",
                "description": "Enhancement of care coordination capabilities across healthcare settings.",
                "affected_areas": ["Primary care", "Specialty care", "Hospital care"],
                "detection_date": "2023-04-15",
                "resources": [
                    {"type": "implementation_plan", "path": "HHS-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-EHR/"}
                ]
            })
        
        elif domain == "health_insurance":
            issues.append({
                "id": "HHS-HI-001",
                "title": "CMS Integration with HMS-EHR",
                "status": "active",
                "priority": "high",
                "description": "Integration of Centers for Medicare & Medicaid Services with HMS-EHR.",
                "affected_areas": ["Medicare", "Medicaid", "Payment systems"],
                "detection_date": "2023-04-20",
                "resources": [
                    {"type": "implementation_plan", "path": "HHS-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-EHR/"},
                    {"type": "documentation", "path": "docs-p/SYSTEM/CMS_INTEGRATION.md"}
                ]
            })
        
        elif domain == "medical_research":
            issues.append({
                "id": "HHS-MR-001",
                "title": "Clinical Research Data Exchange",
                "status": "pending",
                "priority": "medium",
                "description": "Implementation of clinical research data exchange capabilities.",
                "affected_areas": ["Clinical trials", "Research institutions", "Data standards"],
                "detection_date": "2023-05-05",
                "resources": [
                    {"type": "implementation_plan", "path": "HHS-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-EHR/"}
                ]
            })
        
        elif domain == "health_policy":
            issues.append({
                "id": "HHS-HP-001",
                "title": "Regulatory Compliance Framework",
                "status": "active",
                "priority": "high",
                "description": "Implementation of regulatory compliance framework for healthcare components.",
                "affected_areas": ["HIPAA", "Meaningful Use", "Quality reporting"],
                "detection_date": "2023-04-10",
                "resources": [
                    {"type": "implementation_plan", "path": "HHS-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-EHR/"}
                ]
            })
        
        # Filter by priority if requested
        if high_priority_only:
            issues = [issue for issue in issues if issue["priority"] == "high"]
        
        return issues
    
    def prepare_context(self, issue_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare context for Codex CLI based on HHS issues.
        
        Args:
            issue_id: Optional issue ID to focus on
            
        Returns:
            Context dictionary for Codex CLI
        """
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
                "agency": "HHS",
                "issue": None,
                "resources": [],
                "codex_args": "--agency=hhs"
            }
        
        # Prepare HHS-specific context
        context = {
            "agency": "HHS",
            "issue": issue,
            "resources": issue.get("resources", []),
            "domains": self.healthcare_domains,
            "codex_args": f"--agency=hhs --issue-id={issue['id']}"
        }
        
        # Add additional arguments for high priority issues
        if issue.get("priority") == "high":
            context["codex_args"] += " --priority=high"
        
        # Add domain-specific arguments if applicable
        if "HHS-PH-" in issue["id"]:
            context["codex_args"] += " --domain=public_health"
        elif "HHS-HD-" in issue["id"]:
            context["codex_args"] += " --domain=healthcare_delivery"
        elif "HHS-HI-" in issue["id"]:
            context["codex_args"] += " --domain=health_insurance"
        elif "HHS-MR-" in issue["id"]:
            context["codex_args"] += " --domain=medical_research"
        elif "HHS-HP-" in issue["id"]:
            context["codex_args"] += " --domain=health_policy"
        
        return context


def main():
    """Main entry point for the HHS issue finder."""
    import argparse
    
    parser = argparse.ArgumentParser(description="HHS Issue Finder")
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
        # Initialize the HHS issue finder
        finder = HHSIssueFinder(args.config_dir, args.data_dir)
        
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