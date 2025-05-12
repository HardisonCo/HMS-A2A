#!/usr/bin/env python3
"""
DHS Research Connector

A specialized connector for the Department of Homeland Security (DHS)
that provides access to security-related research and implementation data.
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

class DHSException(Exception):
    """Custom exception for DHS connector errors."""
    pass

class DHSResearchConnector(AgencyResearchConnector):
    """
    DHS-specific research connector implementation.
    Provides access to security research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the DHS research connector.
        
        Args:
            base_path: Base path to DHS data
        """
        super().__init__("DHS", base_path)
        self.security_domains = self._load_security_domains()
        self.security_frameworks = self._load_security_frameworks()
    
    def _load_security_domains(self) -> Dict[str, Any]:
        """Load security domain information."""
        domains_file = os.path.join(self.agency_dir, "security_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DHSException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
        "public_health": {
                "description": "Protection and improvement of population health",
                "sub_domains": [
                        "epidemiology",
                        "disease_prevention",
                        "health_promotion"
                ]
        },
        "healthcare_delivery": {
                "description": "Systems and processes for delivering healthcare services",
                "sub_domains": [
                        "primary_care",
                        "hospital_care",
                        "long_term_care"
                ]
        },
        "health_insurance": {
                "description": "Coverage and financing of healthcare",
                "sub_domains": [
                        "medicare",
                        "medicaid",
                        "private_insurance"
                ]
        },
        "medical_research": {
                "description": "Scientific investigation to improve health",
                "sub_domains": [
                        "clinical_research",
                        "biomedical_research",
                        "health_services_research"
                ]
        },
        "health_policy": {
                "description": "Development and analysis of healthcare policies",
                "sub_domains": [
                        "regulatory_policy",
                        "payment_policy",
                        "public_health_policy"
                ]
        }
}
    
    def _load_security_frameworks(self) -> Dict[str, Any]:
        """Load DHS regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "security_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise DHSException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
        "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "description": "Privacy and security rules for health information",
                "components": [
                        "privacy_rule",
                        "security_rule",
                        "breach_notification_rule"
                ]
        },
        "aca": {
                "name": "Affordable Care Act",
                "description": "Comprehensive health insurance reform",
                "components": [
                        "individual_mandate",
                        "insurance_exchanges",
                        "medicaid_expansion"
                ]
        },
        "fda_regulations": {
                "name": "FDA Regulations",
                "description": "Regulations for drugs, devices, and biologics",
                "components": [
                        "drug_approval",
                        "device_approval",
                        "biologic_approval"
                ]
        },
        "cms_regulations": {
                "name": "CMS Regulations",
                "description": "Regulations for Medicare and Medicaid",
                "components": [
                        "medicare_conditions",
                        "medicaid_requirements",
                        "payment_rules"
                ]
        },
        "public_health_regulations": {
                "name": "Public Health Regulations",
                "description": "Regulations for public health protection",
                "components": [
                        "disease_reporting",
                        "vaccination",
                        "emergency_response"
                ]
        }
}
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for DHS.
        
        Returns:
            Implementation status dictionary
        """
        # Get base implementation status
        status = super().get_implementation_status()
        
        # Add DHS-specific status information
        status["domains"] = list(self.security_domains.keys())
        status["frameworks"] = list(self.security_frameworks.keys())
        
        return status
    
    def get_security_recommendations(self) -> List[str]:
        """
        Get security-specific recommendations.
        
        Returns:
            List of security recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.security_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.security_frameworks.items():
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
        Generate Codex context for DHS.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_security_recommendations()
        
        # Compile context
        context = {
            "agency": "DHS",
            "full_name": "Department of Homeland Security",
            "domains": self.security_domains,
            "regulatory_frameworks": self.security_frameworks,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DHS Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to DHS data")
    parser.add_argument("--output", choices=["status", "recommendations", "context"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the DHS connector
        connector = DHSResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_security_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"DHS Implementation Status")
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
                print(f"DHS Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"DHS Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'])}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
    
    except DHSException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
