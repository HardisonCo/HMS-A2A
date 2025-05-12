#!/usr/bin/env python3
"""
OPM Research Connector

A specialized connector for the Office of Personnel Management (OPM)
that provides access to personnel-related research and implementation data.
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

class OPMException(Exception):
    """Custom exception for OPM connector errors."""
    pass

class OPMResearchConnector(AgencyResearchConnector):
    """
    OPM-specific research connector implementation.
    Provides access to personnel research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the OPM research connector.
        
        Args:
            base_path: Base path to OPM data
        """
        super().__init__("OPM", base_path)
        self.personnel_domains = self._load_personnel_domains()
        self.personnel_frameworks = self._load_personnel_frameworks()
    
    def _load_personnel_domains(self) -> Dict[str, Any]:
        """Load personnel domain information."""
        domains_file = os.path.join(self.agency_dir, "personnel_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise OPMException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "employment": {
                "description": "Federal employment services",
                "sub_domains": [
                        "hiring",
                        "classification",
                        "compensation"
                ]
        },
        "benefits": {
                "description": "Federal employee benefits",
                "sub_domains": [
                        "health_benefits",
                        "retirement",
                        "insurance"
                ]
        },
        "workforce_management": {
                "description": "Federal workforce management",
                "sub_domains": [
                        "performance_management",
                        "training",
                        "labor_relations"
                ]
        },
        "oversight": {
                "description": "Federal personnel oversight",
                "sub_domains": [
                        "accountability",
                        "compliance",
                        "ethics"
                ]
        },
        "personnel_systems": {
                "description": "Federal personnel systems",
                "sub_domains": [
                        "systems",
                        "information_technology",
                        "records"
                ]
        }
}
    
    def _load_personnel_frameworks(self) -> Dict[str, Any]:
        """Load OPM regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "personnel_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise OPMException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "csra": {
                "name": "Civil Service Reform Act",
                "description": "Framework for civil service",
                "components": [
                        "merit_systems",
                        "performance_management",
                        "labor_relations"
                ]
        },
        "fehba": {
                "name": "Federal Employees Health Benefits Act",
                "description": "Framework for health benefits",
                "components": [
                        "health_plans",
                        "enrollment",
                        "premiums"
                ]
        },
        "fersa": {
                "name": "Federal Employees Retirement System Act",
                "description": "Framework for retirement",
                "components": [
                        "defined_benefit",
                        "thrift_savings_plan",
                        "social_security"
                ]
        },
        "personnel_assessment": {
                "name": "Federal Personnel Assessment Framework",
                "description": "Framework for assessments",
                "components": [
                        "job_analysis",
                        "assessment_methods",
                        "validation"
                ]
        },
        "performance_management": {
                "name": "Performance Management System",
                "description": "Framework for performance management",
                "components": [
                        "planning",
                        "monitoring",
                        "evaluating"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for OPM.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add OPM-specific status information
        status["domains"] = list(self.personnel_domains.keys())
        status["frameworks"] = list(self.personnel_frameworks.keys())
        
        return status
    
    def get_personnel_recommendations(self) -> List[str]:
        """
        Get personnel-specific recommendations.
        
        Returns:
            List of personnel recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.personnel_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.personnel_frameworks.items():
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
        Generate Codex context for OPM.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_personnel_recommendations()
        
        # Compile context
        context = {
            "agency": "OPM",
            "full_name": "Office of Personnel Management",
            "domains": self.personnel_domains,
            "regulatory_frameworks": self.personnel_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OPM Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to OPM data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the OPM connector
        connector = OPMResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_personnel_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"OPM Implementation Status")
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
                print(f"OPM Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"OPM Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except OPMException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
