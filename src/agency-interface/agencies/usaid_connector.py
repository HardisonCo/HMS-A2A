#!/usr/bin/env python3
"""
USAID Research Connector

A specialized connector for the U.S. Agency for International Development (USAID)
that provides access to development-related research and implementation data.
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

class USAIDException(Exception):
    """Custom exception for USAID connector errors."""
    pass

class USAIDResearchConnector(AgencyResearchConnector):
    """
    USAID-specific research connector implementation.
    Provides access to development research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the USAID research connector.
        
        Args:
            base_path: Base path to USAID data
        """
        super().__init__("USAID", base_path)
        self.development_domains = self._load_development_domains()
        self.development_frameworks = self._load_development_frameworks()
    
    def _load_development_domains(self) -> Dict[str, Any]:
        """Load development domain information."""
        domains_file = os.path.join(self.agency_dir, "development_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise USAIDException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "global_health": {
                "description": "Improving health outcomes globally",
                "sub_domains": [
                        "maternal_health",
                        "child_health",
                        "infectious_diseases"
                ]
        },
        "democracy": {
                "description": "Promoting democracy and governance",
                "sub_domains": [
                        "governance",
                        "civil_society",
                        "human_rights"
                ]
        },
        "economic_growth": {
                "description": "Promoting economic growth",
                "sub_domains": [
                        "trade",
                        "financial_sector",
                        "private_sector"
                ]
        },
        "humanitarian_assistance": {
                "description": "Providing humanitarian assistance",
                "sub_domains": [
                        "disaster_response",
                        "refugees",
                        "food_assistance"
                ]
        },
        "education": {
                "description": "Improving education outcomes",
                "sub_domains": [
                        "basic_education",
                        "higher_education",
                        "workforce_development"
                ]
        }
}
    
    def _load_development_frameworks(self) -> Dict[str, Any]:
        """Load USAID regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "development_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise USAIDException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "foreign_assistance_act": {
                "name": "Foreign Assistance Act",
                "description": "Framework for foreign assistance",
                "components": [
                        "development_assistance",
                        "economic_support",
                        "humanitarian_assistance"
                ]
        },
        "pepfar": {
                "name": "President's Emergency Plan for AIDS Relief",
                "description": "Framework for HIV/AIDS programs",
                "components": [
                        "prevention",
                        "care",
                        "treatment"
                ]
        },
        "feed_the_future": {
                "name": "Feed the Future",
                "description": "Framework for food security",
                "components": [
                        "agriculture",
                        "nutrition",
                        "resilience"
                ]
        },
        "global_health_initiative": {
                "name": "Global Health Initiative",
                "description": "Framework for health programs",
                "components": [
                        "maternal_health",
                        "child_health",
                        "infectious_diseases"
                ]
        },
        "power_africa": {
                "name": "Power Africa",
                "description": "Framework for energy access",
                "components": [
                        "generation",
                        "distribution",
                        "connections"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for USAID.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add USAID-specific status information
        status["domains"] = list(self.development_domains.keys())
        status["frameworks"] = list(self.development_frameworks.keys())
        
        return status
    
    def get_development_recommendations(self) -> List[str]:
        """
        Get development-specific recommendations.
        
        Returns:
            List of development recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.development_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.development_frameworks.items():
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
        Generate Codex context for USAID.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_development_recommendations()
        
        # Compile context
        context = {
            "agency": "USAID",
            "full_name": "U.S. Agency for International Development",
            "domains": self.development_domains,
            "regulatory_frameworks": self.development_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="USAID Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to USAID data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the USAID connector
        connector = USAIDResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_development_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"USAID Implementation Status")
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
                print(f"USAID Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"USAID Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except USAIDException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
