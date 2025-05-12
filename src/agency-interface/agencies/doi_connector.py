#!/usr/bin/env python3
"""
DOI Research Connector

A specialized connector for the Department of the Interior (DOI)
that provides access to interior-related research and implementation data.
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

class DOIException(Exception):
    """Custom exception for DOI connector errors."""
    pass

class DOIResearchConnector(AgencyResearchConnector):
    """
    DOI-specific research connector implementation.
    Provides access to interior research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the DOI research connector.
        
        Args:
            base_path: Base path to DOI data
        """
        super().__init__("DOI", base_path)
        self.interior_domains = self._load_interior_domains()
        self.interior_frameworks = self._load_interior_frameworks()
    
    def _load_interior_domains(self) -> Dict[str, Any]:
        """Load interior domain information."""
        domains_file = os.path.join(self.agency_dir, "interior_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DOIException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "land_management": {
                "description": "Management of public lands",
                "sub_domains": [
                        "public_lands",
                        "grazing",
                        "resource_management"
                ]
        },
        "conservation": {
                "description": "Conservation of natural resources",
                "sub_domains": [
                        "wildlife",
                        "habitat",
                        "endangered_species"
                ]
        },
        "national_parks": {
                "description": "Management of national parks and monuments",
                "sub_domains": [
                        "parks",
                        "monuments",
                        "recreation"
                ]
        },
        "indigenous_affairs": {
                "description": "Affairs related to indigenous peoples",
                "sub_domains": [
                        "tribal_governance",
                        "trust_responsibilities",
                        "services"
                ]
        },
        "natural_resources": {
                "description": "Management of natural resources",
                "sub_domains": [
                        "energy",
                        "minerals",
                        "water"
                ]
        }
}
    
    def _load_interior_frameworks(self) -> Dict[str, Any]:
        """Load DOI regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "interior_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DOIException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "flpma": {
                "name": "Federal Land Policy and Management Act",
                "description": "Framework for public land management",
                "components": [
                        "planning",
                        "multiple_use",
                        "withdrawals"
                ]
        },
        "esa": {
                "name": "Endangered Species Act",
                "description": "Protection for threatened and endangered species",
                "components": [
                        "listing",
                        "critical_habitat",
                        "recovery_plans"
                ]
        },
        "nps_organic_act": {
                "name": "National Park Service Organic Act",
                "description": "Establishment of National Park Service",
                "components": [
                        "conservation",
                        "enjoyment",
                        "management"
                ]
        },
        "blm_regulations": {
                "name": "Bureau of Land Management Regulations",
                "description": "Regulations for public lands",
                "components": [
                        "grazing",
                        "minerals",
                        "recreation"
                ]
        },
        "tribal_self_governance": {
                "name": "Tribal Self-Governance Act",
                "description": "Framework for tribal self-governance",
                "components": [
                        "compacts",
                        "funding_agreements",
                        "tribal_priority_allocations"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for DOI.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add DOI-specific status information
        status["domains"] = list(self.interior_domains.keys())
        status["frameworks"] = list(self.interior_frameworks.keys())
        
        return status
    
    def get_interior_recommendations(self) -> List[str]:
        """
        Get interior-specific recommendations.
        
        Returns:
            List of interior recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.interior_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.interior_frameworks.items():
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
        Generate Codex context for DOI.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_interior_recommendations()
        
        # Compile context
        context = {
            "agency": "DOI",
            "full_name": "Department of the Interior",
            "domains": self.interior_domains,
            "regulatory_frameworks": self.interior_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DOI Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to DOI data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the DOI connector
        connector = DOIResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_interior_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"DOI Implementation Status")
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
                print(f"DOI Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"DOI Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except DOIException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
