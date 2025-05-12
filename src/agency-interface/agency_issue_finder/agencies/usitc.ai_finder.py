#!/usr/bin/env python3
"""
usitc.ai Issue Finder

A specialized issue finder for the USITC – U.S. International Trade Commission (usitc.ai)
that identifies healthcare-related issues in AI applications.
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

class usitc.aiIssueFinder(AgencyIssueFinder):
    """
    usitc.ai-specific issue finder implementation.
    Identifies AI-driven healthcare issues and prepares research context.
    """
    
    def __init__(self, config_dir: str, data_dir: str) -> None:
        """
        Initialize the usitc.ai issue finder.
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing agency data
        """
        super().__init__("usitc.ai", config_dir, data_dir)
        self.healthcare_domains = self._load_healthcare_domains()
    
    def _load_healthcare_domains(self) -> Dict[str, List[str]]:
        """Load healthcare domain information."""
        domains_file = os.path.join(self.data_dir, "usitc.ai", "healthcare_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise AgencyIssueFinderException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "clinical_trials": [
                "trial_design",
                "participant_recruitment",
                "result_analysis"
        ],
        "diagnostics": [
                "imaging_analysis",
                "biomarker_detection",
                "predictive_diagnostics"
        ],
        "treatment_planning": [
                "personalized_medicine",
                "therapy_optimization",
                "outcome_prediction"
        ],
        "drug_discovery": [
                "target_identification",
                "lead_optimization",
                "safety_assessment"
        ],
        "regulatory_compliance": [
                "standards_adherence",
                "documentation_validation",
                "approval_process"
        ]
}
    
    def find_issues(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find current issues for usitc.ai.
        
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
        
        # If still no issues found, add a default issue
        if not self.issues:
            self.issues.append({
                "id": "usitc.ai-GEN-001",
                "title": "AI-Driven Healthcare System Integration",
                "status": "pending",
                "priority": "high",
                "description": "Integration of AI capabilities into healthcare systems and workflows.",
                "affected_areas": ["All healthcare domains"],
                "detection_date": datetime.now().strftime("%Y-%m-%d"),
                "resources": [
                    {"type": "implementation_plan", "path": "usitc.ai-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-usitc.ai/"}
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
        
        # Add AI-specific issue for domain
        issues.append({
            "id": f"usitc.ai-{domain[:2].upper()}-001",
            "title": f"AI-Powered {domain.title()} Implementation",
            "status": "pending",
            "priority": "high" if domain in [
        "diagnostics",
        "treatment_planning",
        "regulatory_compliance"
] else "medium",
            "description": f"Implementation of AI capabilities for {domain} in the healthcare context.",
            "affected_areas": [subdomain.replace('_', ' ').title() for subdomain in self.healthcare_domains.get(domain, [])],
            "detection_date": datetime.now().strftime("%Y-%m-%d"),
            "resources": [
                {"type": "implementation_plan", "path": "usitc.ai-IMPLEMENTATION-PLAN.md"},
                {"type": "codebase", "path": f"SYSTEM-COMPONENTS/HMS-usitc.ai/"}
            ]
        })
        
        # Add model validation issue for high-priority domains
        if domain in [
        "diagnostics",
        "treatment_planning",
        "regulatory_compliance"
]:
            issues.append({
                "id": f"usitc.ai-{domain[:2].upper()}-002",
                "title": f"AI Model Validation for {domain.title()}",
                "status": "pending",
                "priority": "high",
                "description": f"Validation framework for AI models used in {domain} applications.",
                "affected_areas": ["Model Validation", "Regulatory Compliance", "Quality Assurance"],
                "detection_date": datetime.now().strftime("%Y-%m-%d"),
                "resources": [
                    {"type": "implementation_plan", "path": "usitc.ai-IMPLEMENTATION-PLAN.md"},
                    {"type": "guidance", "path": "usitc.ai-AI-VALIDATION-GUIDE.md"}
                ]
            })
        
        # Filter by priority if requested
        if high_priority_only:
            issues = [issue for issue in issues if issue["priority"] == "high"]
        
        return issues
    
    def prepare_context(self, issue_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare context for Codex CLI based on usitc.ai issues.
        
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
                "agency": "usitc.ai",
                "issue": None,
                "resources": [],
                "codex_args": "--agency=usitc.ai"
            }
        
        # Prepare agency-specific context
        context = {
            "agency": "usitc.ai",
            "issue": issue,
            "resources": issue.get("resources", []),
            "domains": self.healthcare_domains,
            "codex_args": f"--agency=usitc.ai --issue-id={issue['id']}"
        }
        
        # Add additional arguments for high priority issues
        if issue.get("priority") == "high":
            context["codex_args"] += " --priority=high"
        
        # Add domain-specific arguments if applicable
        for domain in self.healthcare_domains:
            domain_code = domain[:2].upper()
            if f"usitc.ai-{domain_code}-" in issue["id"]:
                context["codex_args"] += f" --domain={domain}"
                break
        
        # Add AI-specific context
        context["ai_capabilities"] = {
            "machine_learning": ["supervised", "unsupervised", "reinforcement"],
            "natural_language_processing": ["entity_recognition", "sentiment_analysis", "text_generation"],
            "computer_vision": ["image_classification", "object_detection", "segmentation"],
            "predictive_analytics": ["forecasting", "anomaly_detection", "risk_assessment"]
        }
        
        return context


def main():
    """Main entry point for the usitc.ai issue finder."""
    import argparse
    
    parser = argparse.ArgumentParser(description="usitc.ai AI Issue Finder")
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
        # Initialize the usitc.ai issue finder
        finder = usitc.aiIssueFinder(args.config_dir, args.data_dir)
        
        # Find issues
        issues = finder.find_issues(args.topic)
        
        # Prepare context
        context = finder.prepare_context(args.issue_id)
        
        if args.output_format == "json":
            print(json.dumps(context, indent=2))
        else:
            print(f"Agency: {context['agency']} (AI-Powered Healthcare)")
            
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
