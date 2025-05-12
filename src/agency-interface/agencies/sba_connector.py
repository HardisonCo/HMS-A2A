#!/usr/bin/env python3
"""
SBA Research Connector

A specialized connector for the Small Business Administration (SBA)
that provides access to business-related research and implementation data.
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

class SBAException(Exception):
    """Custom exception for SBA connector errors."""
    pass

class SBAResearchConnector(AgencyResearchConnector):
    """
    SBA-specific research connector implementation.
    Provides access to business research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the SBA research connector.
        
        Args:
            base_path: Base path to SBA data
        """
        super().__init__("SBA", base_path)
        self.business_domains = self._load_business_domains()
        self.business_frameworks = self._load_business_frameworks()
    
    def _load_business_domains(self) -> Dict[str, Any]:
        """Load business domain information."""
        domains_file = os.path.join(self.agency_dir, "business_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise SBAException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "lending": {
                "description": "Financial assistance for small businesses",
                "sub_domains": [
                        "small_business_loans",
                        "microloans",
                        "disaster_loans"
                ]
        },
        "entrepreneurship": {
                "description": "Development of entrepreneurs",
                "sub_domains": [
                        "business_development",
                        "mentoring",
                        "training"
                ]
        },
        "contracting": {
                "description": "Government contracting opportunities",
                "sub_domains": [
                        "government_contracting",
                        "subcontracting",
                        "certification"
                ]
        },
        "advocacy": {
                "description": "Advocacy for small businesses",
                "sub_domains": [
                        "regulatory_fairness",
                        "policy",
                        "research"
                ]
        },
        "disaster_assistance": {
                "description": "Assistance for disaster recovery",
                "sub_domains": [
                        "loans",
                        "grants",
                        "recovery"
                ]
        }
}
    
    def _load_business_frameworks(self) -> Dict[str, Any]:
        """Load SBA regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "business_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise SBAException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "small_business_act": {
                "name": "Small Business Act",
                "description": "Framework for small business programs",
                "components": [
                        "loan_programs",
                        "contracting_programs",
                        "development_programs"
                ]
        },
        "jobs_act": {
                "name": "Small Business Jobs Act",
                "description": "Framework for small business growth",
                "components": [
                        "lending_programs",
                        "tax_provisions",
                        "contracting_provisions"
                ]
        },
        "procurement_policy": {
                "name": "Federal Acquisition Regulation",
                "description": "Framework for federal procurement",
                "components": [
                        "small_business_set_asides",
                        "subcontracting_plans",
                        "contract_bundling"
                ]
        },
        "entrepreneurship_policy": {
                "name": "Small Business Development Centers",
                "description": "Framework for entrepreneurship development",
                "components": [
                        "training",
                        "counseling",
                        "technical_assistance"
                ]
        },
        "disaster_recovery": {
                "name": "Disaster Loan Program",
                "description": "Framework for disaster assistance",
                "components": [
                        "economic_injury",
                        "physical_damage",
                        "mitigation"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for SBA.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add SBA-specific status information
        status["domains"] = list(self.business_domains.keys())
        status["frameworks"] = list(self.business_frameworks.keys())
        
        return status
    
    def get_business_recommendations(self) -> List[str]:
        """
        Get business-specific recommendations.
        
        Returns:
            List of business recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.business_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.business_frameworks.items():
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
        Generate Codex context for SBA.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_business_recommendations()
        
        # Compile context
        context = {
            "agency": "SBA",
            "full_name": "Small Business Administration",
            "domains": self.business_domains,
            "regulatory_frameworks": self.business_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SBA Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to SBA data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the SBA connector
        connector = SBAResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_business_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"SBA Implementation Status")
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
                print(f"SBA Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"SBA Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except SBAException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
