#!/usr/bin/env python3
"""
DOL Research Connector

A specialized connector for the Department of Labor (DOL)
that provides access to labor-related research and implementation data.
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

class DOLException(Exception):
    """Custom exception for DOL connector errors."""
    pass

class DOLResearchConnector(AgencyResearchConnector):
    """
    DOL-specific research connector implementation.
    Provides access to labor research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the DOL research connector.
        
        Args:
            base_path: Base path to DOL data
        """
        super().__init__("DOL", base_path)
        self.labor_domains = self._load_labor_domains()
        self.labor_frameworks = self._load_labor_frameworks()
    
    def _load_labor_domains(self) -> Dict[str, Any]:
        """Load labor domain information."""
        domains_file = os.path.join(self.agency_dir, "labor_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DOLException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "workforce_development": {
                "description": "Development of workforce skills",
                "sub_domains": [
                        "job_training",
                        "employment_services",
                        "apprenticeship"
                ]
        },
        "worker_protection": {
                "description": "Protection of workers' rights and safety",
                "sub_domains": [
                        "occupational_safety",
                        "wage_standards",
                        "benefits"
                ]
        },
        "labor_statistics": {
                "description": "Collection and analysis of labor data",
                "sub_domains": [
                        "employment",
                        "prices",
                        "productivity"
                ]
        },
        "labor_relations": {
                "description": "Management of labor-management relations",
                "sub_domains": [
                        "labor_management",
                        "union_democracy",
                        "mediation"
                ]
        },
        "labor_policy": {
                "description": "Development of labor policies",
                "sub_domains": [
                        "research",
                        "policy_development",
                        "international_labor"
                ]
        }
}
    
    def _load_labor_frameworks(self) -> Dict[str, Any]:
        """Load DOL regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "labor_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DOLException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "flsa": {
                "name": "Fair Labor Standards Act",
                "description": "Standards for wages and hours",
                "components": [
                        "minimum_wage",
                        "overtime",
                        "child_labor"
                ]
        },
        "osha_regulations": {
                "name": "OSHA Regulations",
                "description": "Regulations for workplace safety",
                "components": [
                        "safety_standards",
                        "hazard_communication",
                        "inspections"
                ]
        },
        "erisa": {
                "name": "Employee Retirement Income Security Act",
                "description": "Regulation of employee benefits",
                "components": [
                        "reporting",
                        "fiduciary_duties",
                        "enforcement"
                ]
        },
        "nlra": {
                "name": "National Labor Relations Act",
                "description": "Protection of rights to organize",
                "components": [
                        "representation",
                        "unfair_labor_practices",
                        "collective_bargaining"
                ]
        },
        "wioa": {
                "name": "Workforce Innovation and Opportunity Act",
                "description": "Framework for workforce development",
                "components": [
                        "one_stop_centers",
                        "training_programs",
                        "performance_accountability"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for DOL.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add DOL-specific status information
        status["domains"] = list(self.labor_domains.keys())
        status["frameworks"] = list(self.labor_frameworks.keys())
        
        return status
    
    def get_labor_recommendations(self) -> List[str]:
        """
        Get labor-specific recommendations.
        
        Returns:
            List of labor recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.labor_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.labor_frameworks.items():
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
        Generate Codex context for DOL.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_labor_recommendations()
        
        # Compile context
        context = {
            "agency": "DOL",
            "full_name": "Department of Labor",
            "domains": self.labor_domains,
            "regulatory_frameworks": self.labor_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DOL Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to DOL data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the DOL connector
        connector = DOLResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_labor_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"DOL Implementation Status")
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
                print(f"DOL Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"DOL Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except DOLException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
