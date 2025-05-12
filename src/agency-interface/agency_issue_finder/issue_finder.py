#!/usr/bin/env python3
"""
Agency Issue Finder

A tool for identifying current agency issues and preparing research context
for the Codex CLI. This is used by the agency-cli.sh script to dynamically
load relevant agency information and set up the appropriate context.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.codex/agency-config")
DEFAULT_DATA_PATH = os.path.expanduser("~/.codex/agency-data")

class AgencyIssueFinderException(Exception):
    """Custom exception for agency issue finder errors."""
    pass

class AgencyIssueFinder:
    """
    Agency Issue Finder main class.
    Identifies current agency issues and prepares research context.
    """
    
    def __init__(self, agency: str, config_dir: str = DEFAULT_CONFIG_PATH, 
                 data_dir: str = DEFAULT_DATA_PATH) -> None:
        """
        Initialize the agency issue finder.
        
        Args:
            agency: Agency identifier (HHS, USDA, APHIS, etc.)
            config_dir: Directory containing configuration files
            data_dir: Directory containing agency data
        """
        self.agency = agency.upper()
        self.config_dir = config_dir
        self.data_dir = data_dir
        self.issues = []
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load agency configuration
        self._load_agency_config()
    
    def _load_agency_config(self) -> None:
        """Load agency configuration from the config directory."""
        config_file = os.path.join(self.config_dir, f"{self.agency.lower()}_config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError as e:
                raise AgencyIssueFinderException(f"Invalid JSON in config file: {e}")
        else:
            # Create default configuration
            self.config = {
                "agency": self.agency,
                "priority_issues": [],
                "data_sources": [],
                "last_updated": datetime.now().isoformat()
            }
            self._save_agency_config()
    
    def _save_agency_config(self) -> None:
        """Save agency configuration to the config directory."""
        config_file = os.path.join(self.config_dir, f"{self.agency.lower()}_config.json")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            raise AgencyIssueFinderException(f"Failed to save config file: {e}")
    
    def find_issues(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find current issues for the specified agency.
        
        Args:
            topic: Optional topic to filter issues
            
        Returns:
            List of issues found
        """
        self.issues = []
        
        # For APHIS and bird-flu topic, return predefined issues
        if self.agency == "APHIS" and topic and topic.lower() in ["bird-flu", "avian-influenza"]:
            self.issues = self._get_bird_flu_issues()
        
        # Normally we would search databases or APIs here
        # This is a simplified implementation for the demo
        
        return self.issues
    
    def _get_bird_flu_issues(self) -> List[Dict[str, Any]]:
        """
        Get predefined bird flu issues for APHIS.
        
        Returns:
            List of bird flu related issues
        """
        return [
            {
                "id": "BF-001",
                "title": "H5N1 Outbreak in Commercial Poultry Operations",
                "status": "active",
                "priority": "high",
                "description": "Ongoing outbreak of highly pathogenic avian influenza (HPAI) H5N1 in commercial poultry operations across multiple states.",
                "affected_areas": ["Minnesota", "Iowa", "California", "Wisconsin"],
                "detection_date": "2023-02-15",
                "resources": [
                    {"type": "implementation_plan", "path": "APHIS-BIRD-FLU-IMPLEMENTATION-PLAN.md"},
                    {"type": "progress_tracking", "path": "APHIS-PROGRESS-TRACKING.md"},
                    {"type": "codebase", "path": "aphis-bird-flu/"}
                ]
            },
            {
                "id": "BF-002",
                "title": "Wild Bird Surveillance Program Enhancement",
                "status": "active",
                "priority": "medium",
                "description": "Enhancement of wild bird surveillance program to improve early detection capabilities for HPAI.",
                "affected_areas": ["Nationwide"],
                "detection_date": "2023-01-10",
                "resources": [
                    {"type": "implementation_plan", "path": "APHIS-BIRD-FLU-IMPLEMENTATION-PLAN.md"},
                    {"type": "progress_tracking", "path": "APHIS-PROGRESS-TRACKING.md"}
                ]
            },
            {
                "id": "BF-003",
                "title": "Adaptive Sampling Strategy Implementation",
                "status": "in_progress",
                "priority": "high",
                "description": "Implementation of adaptive sampling strategies to optimize surveillance resource allocation.",
                "affected_areas": ["Nationwide"],
                "detection_date": "2023-03-05",
                "resources": [
                    {"type": "implementation_plan", "path": "APHIS-BIRD-FLU-IMPLEMENTATION-PLAN.md"},
                    {"type": "progress_tracking", "path": "APHIS-PROGRESS-TRACKING.md"},
                    {"type": "source_code", "path": "aphis-bird-flu/src/system-supervisors/animal_health/services/adaptive_sampling/"}
                ]
            }
        ]
    
    def prepare_context(self, issue_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare context for Codex CLI based on the selected issue.
        
        Args:
            issue_id: Optional issue ID to prepare context for
            
        Returns:
            Dictionary with context information
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
                "agency": self.agency,
                "issue": None,
                "resources": [],
                "codex_args": ""
            }
        
        # Prepare context from the issue
        context = {
            "agency": self.agency,
            "issue": issue,
            "resources": issue.get("resources", []),
            "codex_args": f"--agency={self.agency.lower()} --issue-id={issue['id']}"
        }
        
        # Add additional arguments for high priority issues
        if issue.get("priority") == "high":
            context["codex_args"] += " --priority=high"
        
        return context
    
    def generate_report(self, issue_ids: Optional[List[str]] = None) -> str:
        """
        Generate a report of the issues found.
        
        Args:
            issue_ids: Optional list of issue IDs to include in the report
            
        Returns:
            Report as a string
        """
        if not self.issues:
            return "No issues found."
        
        # Filter issues if issue_ids is provided
        issues_to_report = self.issues
        if issue_ids:
            issues_to_report = [i for i in self.issues if i["id"] in issue_ids]
        
        # Build the report
        report = f"Agency Issue Report for {self.agency}\n"
        report += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for issue in issues_to_report:
            report += f"Issue ID: {issue['id']}\n"
            report += f"Title: {issue['title']}\n"
            report += f"Status: {issue['status']}\n"
            report += f"Priority: {issue['priority']}\n"
            report += f"Description: {issue['description']}\n"
            report += f"Affected Areas: {', '.join(issue['affected_areas'])}\n"
            report += f"Detection Date: {issue['detection_date']}\n"
            report += "Resources:\n"
            
            for resource in issue.get("resources", []):
                report += f"  - {resource['type']}: {resource['path']}\n"
            
            report += "\n"
        
        return report


def main():
    """Main entry point for the agency issue finder."""
    parser = argparse.ArgumentParser(description="Agency Issue Finder")
    parser.add_argument("agency", help="Agency identifier (HHS, USDA, APHIS, etc.)")
    parser.add_argument("--topic", help="Topic to filter issues")
    parser.add_argument("--config-dir", default=DEFAULT_CONFIG_PATH, 
                        help="Directory containing configuration files")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_PATH,
                        help="Directory containing agency data")
    parser.add_argument("--issue-id", help="Specific issue ID to prepare context for")
    parser.add_argument("--report", action="store_true", help="Generate a report of issues")
    parser.add_argument("--output-format", choices=["text", "json"], default="text",
                        help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the agency issue finder
        finder = AgencyIssueFinder(args.agency, args.config_dir, args.data_dir)
        
        # Find issues
        issues = finder.find_issues(args.topic)
        
        if args.report:
            # Generate a report
            report = finder.generate_report()
            print(report)
        else:
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