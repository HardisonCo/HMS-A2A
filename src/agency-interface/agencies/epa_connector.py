#!/usr/bin/env python3
"""
EPA Research Connector

A specialized connector for the Environmental Protection Agency (EPA)
that provides access to environment-related research and implementation data.
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

class EPAException(Exception):
    """Custom exception for EPA connector errors."""
    pass

class EPAResearchConnector(AgencyResearchConnector):
    """
    EPA-specific research connector implementation.
    Provides access to environment research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the EPA research connector.
        
        Args:
            base_path: Base path to EPA data
        """
        super().__init__("EPA", base_path)
        self.environment_domains = self._load_environment_domains()
        self.environment_frameworks = self._load_environment_frameworks()
    
    def _load_environment_domains(self) -> Dict[str, Any]:
        """Load environment domain information."""
        domains_file = os.path.join(self.agency_dir, "environment_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise EPAException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "air_quality": {
                "description": "Protection of air resources",
                "sub_domains": [
                        "air_pollution",
                        "emissions",
                        "standards"
                ]
        },
        "water_quality": {
                "description": "Protection of water resources",
                "sub_domains": [
                        "drinking_water",
                        "surface_water",
                        "groundwater"
                ]
        },
        "chemical_safety": {
                "description": "Management of chemicals and toxics",
                "sub_domains": [
                        "toxics",
                        "pesticides",
                        "risk_assessment"
                ]
        },
        "waste_management": {
                "description": "Management of waste",
                "sub_domains": [
                        "hazardous_waste",
                        "solid_waste",
                        "recycling"
                ]
        },
        "climate_change": {
                "description": "Addressing climate change",
                "sub_domains": [
                        "greenhouse_gases",
                        "adaptation",
                        "mitigation"
                ]
        }
}
    
    def _load_environment_frameworks(self) -> Dict[str, Any]:
        """Load EPA regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "environment_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise EPAException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "caa": {
                "name": "Clean Air Act",
                "description": "Framework for air quality",
                "components": [
                        "national_ambient_air_quality_standards",
                        "state_implementation_plans",
                        "emissions_standards"
                ]
        },
        "cwa": {
                "name": "Clean Water Act",
                "description": "Framework for water quality",
                "components": [
                        "water_quality_standards",
                        "discharge_permits",
                        "wetlands_protection"
                ]
        },
        "rcra": {
                "name": "Resource Conservation and Recovery Act",
                "description": "Framework for waste management",
                "components": [
                        "hazardous_waste",
                        "solid_waste",
                        "underground_storage_tanks"
                ]
        },
        "tsca": {
                "name": "Toxic Substances Control Act",
                "description": "Framework for chemical regulation",
                "components": [
                        "chemical_testing",
                        "new_chemicals",
                        "existing_chemicals"
                ]
        },
        "superfund": {
                "name": "Comprehensive Environmental Response, Compensation, and Liability Act",
                "description": "Framework for hazardous site cleanup",
                "components": [
                        "site_assessment",
                        "remedial_action",
                        "liability"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for EPA.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add EPA-specific status information
        status["domains"] = list(self.environment_domains.keys())
        status["frameworks"] = list(self.environment_frameworks.keys())
        
        return status
    
    def get_environment_recommendations(self) -> List[str]:
        """
        Get environment-specific recommendations.
        
        Returns:
            List of environment recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.environment_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.environment_frameworks.items():
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
        Generate Codex context for EPA.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_environment_recommendations()
        
        # Compile context
        context = {
            "agency": "EPA",
            "full_name": "Environmental Protection Agency",
            "domains": self.environment_domains,
            "regulatory_frameworks": self.environment_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EPA Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to EPA data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the EPA connector
        connector = EPAResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_environment_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"EPA Implementation Status")
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
                print(f"EPA Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"EPA Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except EPAException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
