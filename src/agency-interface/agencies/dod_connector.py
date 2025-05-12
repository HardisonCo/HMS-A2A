#!/usr/bin/env python3
"""
DOD Research Connector

A specialized connector for the Department of Defense (DOD)
that provides access to defense-related research and implementation data.
"""

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

class DODException(Exception):
    """Custom exception for DOD connector errors."""
    pass

class DODResearchConnector(AgencyResearchConnector):
    """
    DOD-specific research connector implementation.
    Provides access to defense research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the DOD research connector.
        
        Args:
            base_path: Base path to DOD data
        """
        super().__init__("DOD", base_path)
        self.defense_domains = self._load_defense_domains()
        self.defense_frameworks = self._load_defense_frameworks()
    
    def _load_defense_domains(self) -> Dict[str, Any]:
        """Load defense domain information."""
        domains_file = os.path.join(self.agency_dir, "defense_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DODException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "military_operations": {
                "description": "Planning and execution of military missions",
                "sub_domains": [
                        "planning",
                        "execution",
                        "evaluation"
                ]
        },
        "defense_procurement": {
                "description": "Acquisition of weapons systems and services",
                "sub_domains": [
                        "acquisition",
                        "contracting",
                        "supply_chain"
                ]
        },
        "personnel_management": {
                "description": "Management of military and civilian personnel",
                "sub_domains": [
                        "recruitment",
                        "training",
                        "retention"
                ]
        },
        "intelligence": {
                "description": "Collection and analysis of intelligence",
                "sub_domains": [
                        "collection",
                        "analysis",
                        "dissemination"
                ]
        },
        "cybersecurity": {
                "description": "Defense against cyber threats",
                "sub_domains": [
                        "defense",
                        "offense",
                        "resilience"
                ]
        }
}
    
    def _load_defense_frameworks(self) -> Dict[str, Any]:
        """Load DOD regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "defense_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DODException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "dod_5000": {
                "name": "DoD Directive 5000 Series",
                "description": "Defense acquisition system regulations",
                "components": [
                        "acquisition_planning",
                        "procurement",
                        "lifecycle_management"
                ]
        },
        "ucmj": {
                "name": "Uniform Code of Military Justice",
                "description": "Military legal framework",
                "components": [
                        "judicial_procedures",
                        "punitive_articles",
                        "administration"
                ]
        },
        "jcids": {
                "name": "Joint Capabilities Integration and Development System",
                "description": "Requirements generation process",
                "components": [
                        "capability_assessment",
                        "requirements_definition",
                        "validation"
                ]
        },
        "ppbe": {
                "name": "Planning, Programming, Budgeting, and Execution",
                "description": "Defense resource allocation process",
                "components": [
                        "planning",
                        "programming",
                        "budgeting",
                        "execution"
                ]
        },
        "dsca": {
                "name": "Defense Security Cooperation",
                "description": "Foreign military sales and cooperation",
                "components": [
                        "foreign_military_sales",
                        "international_training",
                        "security_assistance"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for DOD.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add DOD-specific status information
        status["domains"] = list(self.defense_domains.keys())
        status["frameworks"] = list(self.defense_frameworks.keys())
        
        return status
    
    def get_defense_recommendations(self) -> List[str]:
        """
        Get defense-specific recommendations.
        
        Returns:
            List of defense recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.defense_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.defense_frameworks.items():
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
        """
        Generate Codex context for DOD.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_defense_recommendations()
        
        # Compile context
        context = {
            "agency": "DOD",
            "full_name": "Department of Defense",
            "domains": self.defense_domains,
            "regulatory_frameworks": self.defense_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DOD Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to DOD data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the DOD connector
        connector = DODResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_defense_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"DOD Implementation Status")
                print(f"-------------------------")
                
                if "overall_completion" in result:
                    overall = result["overall_completion"]
                    print(f"Overall Completion: {overall['completed_tasks']}/{overall['total_tasks']} "
                          f"({overall['percentage']:.1f}%)")
                
                if "implementation_phases" in result:
                    print("\nPhases:")
                    for phase_key, phase in sorted(result["implementation_phases"].items()):
                        print(f"  {phase['name']}: {phase['completed_tasks']}/{phase['total_tasks']} "
                              f"({phase['percentage']:.1f}%)")
                
                print(f"\nDomains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['frameworks'])}")
            
            elif args.output == "recommendations":
                print(f"DOD Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"DOD Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except DODException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
