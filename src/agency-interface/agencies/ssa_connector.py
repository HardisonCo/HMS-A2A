#!/usr/bin/env python3
"""
SSA Research Connector

A specialized connector for the Social Security Administration (SSA)
that provides access to social-related research and implementation data.
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

class SSAException(Exception):
    """Custom exception for SSA connector errors."""
    pass

class SSAResearchConnector(AgencyResearchConnector):
    """
    SSA-specific research connector implementation.
    Provides access to social research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the SSA research connector.
        
        Args:
            base_path: Base path to SSA data
        """
        super().__init__("SSA", base_path)
        self.social_domains = self._load_social_domains()
        self.social_frameworks = self._load_social_frameworks()
    
    def _load_social_domains(self) -> Dict[str, Any]:
        """Load social domain information."""
        domains_file = os.path.join(self.agency_dir, "social_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise SSAException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "retirement": {
                "description": "Retirement and survivors benefits",
                "sub_domains": [
                        "old_age_benefits",
                        "survivors_benefits",
                        "medicare"
                ]
        },
        "disability": {
                "description": "Disability benefits",
                "sub_domains": [
                        "disability_insurance",
                        "evaluation",
                        "appeals"
                ]
        },
        "supplemental_security": {
                "description": "Needs-based assistance",
                "sub_domains": [
                        "needs_based_assistance",
                        "eligibility",
                        "payments"
                ]
        },
        "program_integrity": {
                "description": "Ensuring program integrity",
                "sub_domains": [
                        "fraud_prevention",
                        "quality_review",
                        "oversight"
                ]
        },
        "customer_service": {
                "description": "Service to beneficiaries",
                "sub_domains": [
                        "field_offices",
                        "online_services",
                        "card_services"
                ]
        }
}
    
    def _load_social_frameworks(self) -> Dict[str, Any]:
        """Load SSA regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "social_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise SSAException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "social_security_act": {
                "name": "Social Security Act",
                "description": "Framework for social security programs",
                "components": [
                        "oasi",
                        "di",
                        "hi"
                ]
        },
        "ssi": {
                "name": "Supplemental Security Income",
                "description": "Framework for needs-based assistance",
                "components": [
                        "eligibility",
                        "payments",
                        "resources"
                ]
        },
        "disability_determination": {
                "name": "Disability Determination Process",
                "description": "Framework for disability evaluation",
                "components": [
                        "initial_determination",
                        "reconsideration",
                        "hearings"
                ]
        },
        "earnings_record": {
                "name": "Earnings Record System",
                "description": "Framework for earnings records",
                "components": [
                        "earnings_posting",
                        "corrections",
                        "reporting"
                ]
        },
        "enumeration": {
                "name": "Social Security Number System",
                "description": "Framework for SSN issuance",
                "components": [
                        "enumeration",
                        "verification",
                        "protection"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for SSA.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add SSA-specific status information
        status["domains"] = list(self.social_domains.keys())
        status["frameworks"] = list(self.social_frameworks.keys())
        
        return status
    
    def get_social_recommendations(self) -> List[str]:
        """
        Get social-specific recommendations.
        
        Returns:
            List of social recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.social_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.social_frameworks.items():
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
        Generate Codex context for SSA.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_social_recommendations()
        
        # Compile context
        context = {
            "agency": "SSA",
            "full_name": "Social Security Administration",
            "domains": self.social_domains,
            "regulatory_frameworks": self.social_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSA Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to SSA data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the SSA connector
        connector = SSAResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_social_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"SSA Implementation Status")
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
                print(f"SSA Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"SSA Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except SSAException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
