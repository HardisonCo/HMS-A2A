#!/usr/bin/env python3
"""
DOT Issue Finder

A specialized issue finder for the Department of Transportation (DOT)
that identifies transportation-related issues and prepares research context for Codex CLI.
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

class DOTIssueFinder(AgencyIssueFinder):
    """
    DOT-specific issue finder implementation.
    Identifies transportation-related issues and prepares research context.
    """
    
    def __init__(self, config_dir: str, data_dir: str) -> None:
        """
        Initialize the DOT issue finder.
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing agency data
        """
        super().__init__("DOT", config_dir, data_dir)
        self.transportation_domains = self._load_transportation_domains()
    
    def _load_transportation_domains(self) -> Dict[str, List[str]]:
        """Load transportation domain information."""
        domains_file = os.path.join(self.data_dir, "dot", "transportation_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise AgencyIssueFinderException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "aviation": [
                "air_traffic_control",
                "aviation_safety",
                "airports"
        ],
        "surface_transportation": [
                "highways",
                "railroads",
                "transit"
        ],
        "maritime": [
                "ports",
                "waterways",
                "shipping"
        ],
        "safety": [
                "vehicle_safety",
                "operator_safety",
                "infrastructure_safety"
        ],
        "transportation_policy": [
                "planning",
                "research",
                "environmental_impact"
        ]
}
    
    def find_issues(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find current issues for DOT.
        
        Args:
            topic: Optional topic to filter issues
            
        Returns:
            List of issues found
        """
        # Start with empty issues list
        self.issues = []
        
        # If a specific topic is provided, find relevant issues
        if topic:
            # Check if topic matches any transportation domain
            for domain, subdomains in self.transportation_domains.items():
                if topic.lower() in domain.lower() or topic.lower() in [s.lower() for s in subdomains]:
                    self.issues.extend(self._get_domain_issues(domain))
        
        # If no topic is specified or no issues found for topic, return all high-priority issues
        if not self.issues:
            for domain in self.transportation_domains:
                self.issues.extend(self._get_domain_issues(domain, high_priority_only=True))
        
        # If still no issues found, add a default issue
        if not self.issues:
            self.issues.append({
                "id": "DOT-GEN-001",
                "title": "Transportation Systems Integration Analysis",
                "status": "pending",
                "priority": "high",
                "description": "Analysis of integration points between transportation systems and components.",
                "affected_areas": ["All transportation domains"],
                "detection_date": datetime.now().strftime("%Y-%m-%d"),
                "resources": [
                    {"type": "implementation_plan", "path": "DOT-IMPLEMENTATION-PLAN.md"},
                    {"type": "codebase", "path": "SYSTEM-COMPONENTS/HMS-DOT/"}
                ]
            })
        
        return self.issues
    
    def _get_domain_issues(self, domain: str, high_priority_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get issues for a specific transportation domain.
        
        Args:
            domain: Transportation domain
            high_priority_only: Only return high priority issues
            
        Returns:
            List of domain issues
        """
        issues = []
        
        # Add placeholder issue for domain
        issues.append({
            "id": f"DOT-{domain[:2].upper()}-001",
            "title": f"{domain.title()} Integration",
            "status": "pending",
            "priority": "high" if domain in [
        "aviation",
        "safety",
        "surface_transportation"
] else "medium",
            "description": f"Integration of {domain} systems with HMS components.",
            "affected_areas": [subdomain.replace('_', ' ').title() for subdomain in self.transportation_domains.get(domain, [])],
            "detection_date": datetime.now().strftime("%Y-%m-%d"),
            "resources": [
                {"type": "implementation_plan", "path": "DOT-IMPLEMENTATION-PLAN.md"},
                {"type": "codebase", "path": f"SYSTEM-COMPONENTS/HMS-DOT/"}
            ]
        })
        
        # Filter by priority if requested
        if high_priority_only:
            issues = [issue for issue in issues if issue["priority"] == "high"]
        
        return issues
    
    def prepare_context(self, issue_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare context for Codex CLI based on DOT issues.
        
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
                "agency": "DOT",
                "issue": None,
                "resources": [],
                "codex_args": "--agency=dot"
            }
        
        # Prepare agency-specific context
        context = {
            "agency": "DOT",
            "issue": issue,
            "resources": issue.get("resources", []),
            "domains": self.transportation_domains,
            "codex_args": f"--agency=dot --issue-id={issue['id']}"
        }
        
        # Add additional arguments for high priority issues
        if issue.get("priority") == "high":
            context["codex_args"] += " --priority=high"
        
        # Add domain-specific arguments if applicable
        for domain in self.transportation_domains:
            domain_code = domain[:2].upper()
            if f"DOT-{domain_code}-" in issue["id"]:
                context["codex_args"] += f" --domain={domain}"
                break
        
        return context


def main():
    """Main entry point for the DOT issue finder."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DOT Issue Finder")
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
        # Initialize the DOT issue finder
        finder = DOTIssueFinder(args.config_dir, args.data_dir)
        
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
