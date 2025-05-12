#!/usr/bin/env python3
"""
NASA Research Connector

A specialized connector for the National Aeronautics and Space Administration (NASA)
that provides access to space-related research and implementation data.
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

class NASAException(Exception):
    """Custom exception for NASA connector errors."""
    pass

class NASAResearchConnector(AgencyResearchConnector):
    """
    NASA-specific research connector implementation.
    Provides access to space research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the NASA research connector.
        
        Args:
            base_path: Base path to NASA data
        """
        super().__init__("NASA", base_path)
        self.space_domains = self._load_space_domains()
        self.space_frameworks = self._load_space_frameworks()
    
    def _load_space_domains(self) -> Dict[str, Any]:
        """Load space domain information."""
        domains_file = os.path.join(self.agency_dir, "space_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise NASAException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "human_spaceflight": {
                "description": "Human exploration of space",
                "sub_domains": [
                        "international_space_station",
                        "commercial_crew",
                        "exploration"
                ]
        },
        "science": {
                "description": "Scientific investigation of space and Earth",
                "sub_domains": [
                        "earth_science",
                        "planetary_science",
                        "astrophysics"
                ]
        },
        "aeronautics": {
                "description": "Research and development for aviation",
                "sub_domains": [
                        "aviation_safety",
                        "airspace_operations",
                        "advanced_technologies"
                ]
        },
        "technology": {
                "description": "Development of space technologies",
                "sub_domains": [
                        "space_technology",
                        "mission_support",
                        "innovation"
                ]
        },
        "operations": {
                "description": "Operations of space missions",
                "sub_domains": [
                        "launch_services",
                        "mission_operations",
                        "communications"
                ]
        }
}
    
    def _load_space_frameworks(self) -> Dict[str, Any]:
        """Load NASA regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "space_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise NASAException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "space_act": {
                "name": "National Aeronautics and Space Act",
                "description": "Framework for NASA",
                "components": [
                        "research",
                        "development",
                        "operations"
                ]
        },
        "authorization_act": {
                "name": "NASA Authorization Act",
                "description": "Framework for NASA programs",
                "components": [
                        "human_spaceflight",
                        "science",
                        "aeronautics"
                ]
        },
        "space_policy": {
                "name": "National Space Policy",
                "description": "Framework for space activities",
                "components": [
                        "civil_space",
                        "commercial_space",
                        "national_security_space"
                ]
        },
        "earth_science": {
                "name": "Earth Science Program",
                "description": "Framework for Earth observation",
                "components": [
                        "earth_observing_system",
                        "applied_science",
                        "research"
                ]
        },
        "exploration_systems": {
                "name": "Exploration Systems Development",
                "description": "Framework for human exploration",
                "components": [
                        "orion",
                        "sls",
                        "ground_systems"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for NASA.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add NASA-specific status information
        status["domains"] = list(self.space_domains.keys())
        status["frameworks"] = list(self.space_frameworks.keys())
        
        return status
    
    def get_space_recommendations(self) -> List[str]:
        """
        Get space-specific recommendations.
        
        Returns:
            List of space recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.space_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.space_frameworks.items():
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
        Generate Codex context for NASA.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_space_recommendations()
        
        # Compile context
        context = {
            "agency": "NASA",
            "full_name": "National Aeronautics and Space Administration",
            "domains": self.space_domains,
            "regulatory_frameworks": self.space_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="NASA Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to NASA data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the NASA connector
        connector = NASAResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_space_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"NASA Implementation Status")
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
                print(f"NASA Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"NASA Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except NASAException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
