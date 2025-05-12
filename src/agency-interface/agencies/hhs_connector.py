#!/usr/bin/env python3
"""
HHS Research Connector

A specialized connector for the Department of Health and Human Services (HHS)
that provides access to healthcare-related research and implementation data.
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

class HHSException(Exception):
    """Custom exception for HHS connector errors."""
    pass

class HHSResearchConnector(AgencyResearchConnector):
    """
    HHS-specific research connector implementation.
    Provides access to healthcare research and implementation data.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the HHS research connector.
        
        Args:
            base_path: Base path to HHS data
        """
        super().__init__("HHS", base_path)
        self.healthcare_domains = self._load_healthcare_domains()
        self.regulatory_frameworks = self._load_regulatory_frameworks()
        self.cms_resources = self._load_cms_resources()
    
    def _load_healthcare_domains(self) -> Dict[str, Any]:
        """Load healthcare domain information."""
        domains_file = os.path.join(self.agency_dir, "healthcare_domains.json")
        
        if os.path.exists(domains_file):
            try:
                with open(domains_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise HHSException(f"Invalid JSON in domains file: {e}")
        
        # Return default domains if file not found
        return {
            "public_health": {
                "description": "Protection and improvement of population health",
                "sub_domains": ["epidemiology", "disease_prevention", "health_promotion"]
            },
            "healthcare_delivery": {
                "description": "Systems and processes for delivering healthcare services",
                "sub_domains": ["primary_care", "hospital_care", "long_term_care"]
            },
            "health_insurance": {
                "description": "Coverage and financing of healthcare",
                "sub_domains": ["medicare", "medicaid", "private_insurance"]
            },
            "medical_research": {
                "description": "Scientific investigation to improve health",
                "sub_domains": ["clinical_research", "biomedical_research", "health_services_research"]
            },
            "health_policy": {
                "description": "Development and analysis of healthcare policies",
                "sub_domains": ["regulatory_policy", "payment_policy", "public_health_policy"]
            }
        }
    
    def _load_regulatory_frameworks(self) -> Dict[str, Any]:
        """Load HHS regulatory frameworks."""
        frameworks_file = os.path.join(self.agency_dir, "regulatory_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise HHSException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "description": "Privacy and security rules for health information",
                "components": ["privacy_rule", "security_rule", "breach_notification_rule"]
            },
            "aca": {
                "name": "Affordable Care Act",
                "description": "Comprehensive health insurance reform",
                "components": ["individual_mandate", "insurance_exchanges", "medicaid_expansion"]
            },
            "fda_regulations": {
                "name": "FDA Regulations",
                "description": "Regulations for drugs, devices, and biologics",
                "components": ["drug_approval", "device_approval", "biologic_approval"]
            },
            "cms_regulations": {
                "name": "CMS Regulations",
                "description": "Regulations for Medicare and Medicaid",
                "components": ["medicare_conditions", "medicaid_requirements", "payment_rules"]
            },
            "public_health_regulations": {
                "name": "Public Health Regulations",
                "description": "Regulations for public health protection",
                "components": ["disease_reporting", "vaccination", "emergency_response"]
            }
        }
    
    def _load_cms_resources(self) -> Dict[str, Any]:
        """Load CMS-specific resources."""
        cms_file = os.path.join(self.agency_dir, "cms_resources.json")
        
        if os.path.exists(cms_file):
            try:
                with open(cms_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise HHSException(f"Invalid JSON in CMS resources file: {e}")
        
        # Return default CMS resources if file not found
        return {
            "medicare": {
                "description": "Healthcare coverage for those 65+ or with disabilities",
                "components": ["part_a", "part_b", "part_c", "part_d"],
                "implementation_status": "operational"
            },
            "medicaid": {
                "description": "Healthcare coverage for low-income individuals",
                "components": ["traditional", "expansion", "chip"],
                "implementation_status": "operational"
            },
            "marketplace": {
                "description": "Health insurance exchanges",
                "components": ["individual", "shop"],
                "implementation_status": "operational"
            }
        }
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for HHS.
        
        Returns:
            Implementation status dictionary
        """
        # Extract implementation status from implementation plan if available
        status = {
            "agency": "HHS",
            "domains": list(self.healthcare_domains.keys()),
            "frameworks": list(self.regulatory_frameworks.keys()),
            "last_updated": datetime.now().isoformat()
        }
        
        # Parse implementation plan if available
        if "implementation_plan" in self.data:
            # Extract phases and tasks
            plan_content = self.data["implementation_plan"]
            phases = {}
            
            # Extract phase sections
            phase_matches = re.finditer(r'## Phase (\d+): (.*?)\n(.*?)(?=##|\Z)', 
                                        plan_content, re.DOTALL)
            
            for match in phase_matches:
                phase_num = match.group(1)
                phase_name = match.group(2)
                phase_content = match.group(3)
                
                # Extract tasks and their status
                tasks = []
                task_matches = re.finditer(r'- \[([ x])\] (.*?)$', phase_content, re.MULTILINE)
                
                for task_match in task_matches:
                    completed = task_match.group(1) == 'x'
                    task_name = task_match.group(2).strip()
                    
                    tasks.append({
                        "name": task_name,
                        "completed": completed
                    })
                
                # Calculate phase completion percentage
                completed_tasks = sum(1 for task in tasks if task["completed"])
                percentage = (completed_tasks / len(tasks)) * 100 if tasks else 0
                
                phases[f"phase_{phase_num}"] = {
                    "name": phase_name,
                    "tasks": tasks,
                    "completed_tasks": completed_tasks,
                    "total_tasks": len(tasks),
                    "percentage": percentage
                }
            
            status["implementation_phases"] = phases
            
            # Calculate overall completion
            all_tasks = [task for phase in phases.values() for task in phase["tasks"]]
            completed_all = sum(1 for task in all_tasks if task["completed"])
            overall_percentage = (completed_all / len(all_tasks)) * 100 if all_tasks else 0
            
            status["overall_completion"] = {
                "completed_tasks": completed_all,
                "total_tasks": len(all_tasks),
                "percentage": overall_percentage
            }
        
        # Add CMS-specific status
        cms_status = {
            name: info.get("implementation_status", "unknown") 
            for name, info in self.cms_resources.items()
        }
        status["cms_status"] = cms_status
        
        return status
    
    def get_healthcare_recommendations(self) -> List[str]:
        """
        Get healthcare-specific recommendations.
        
        Returns:
            List of healthcare recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate domain-specific recommendations
        for domain, info in self.healthcare_domains.items():
            recommendations.append(f"Enhance {domain} capabilities with focus on {', '.join(info['sub_domains'])}")
        
        # Generate framework-specific recommendations
        for framework, info in self.regulatory_frameworks.items():
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
        
        # Add CMS-specific recommendations
        for program, info in self.cms_resources.items():
            if isinstance(info, dict) and info.get("implementation_status") != "operational":
                recommendations.append(f"Prioritize implementation of {program} components")
        
        return recommendations
    
    def get_codex_context(self) -> Dict[str, Any]:
        """
        Generate Codex context for HHS.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_healthcare_recommendations()
        
        # Compile context
        context = {
            "agency": "HHS",
            "full_name": "Department of Health and Human Services",
            "domains": self.healthcare_domains,
            "regulatory_frameworks": self.regulatory_frameworks,
            "cms_resources": self.cms_resources,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context
    
    def get_cms_integration_status(self) -> Dict[str, Any]:
        """
        Get CMS integration status with HMS-EHR.
        
        Returns:
            CMS integration status dictionary
        """
        cms_status = {
            "agency": "CMS",
            "parent_agency": "HHS",
            "integration": {
                "hms_ehr": {
                    "status": "complete",
                    "components": [
                        {"name": "Medicare API", "status": "operational"},
                        {"name": "Medicaid API", "status": "operational"},
                        {"name": "Marketplace API", "status": "operational"}
                    ],
                    "last_updated": datetime.now().isoformat()
                }
            }
        }
        
        return cms_status


def main():
    """Main entry point function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="HHS Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to HHS data")
    parser.add_argument("--output", choices=["status", "recommendations", "context", "cms"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    
    args = parser.parse_args()
    
    try:
        # Initialize the HHS connector
        connector = HHSResearchConnector(args.base_path)
        
        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_healthcare_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        elif args.output == "cms":
            result = connector.get_cms_integration_status()
        
        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"HHS Implementation Status")
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
                
                if "cms_status" in result:
                    print("\nCMS Programs:")
                    for program, status in result["cms_status"].items():
                        print(f"  {program}: {status}")
            
            elif args.output == "recommendations":
                print(f"HHS Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "context":
                print(f"HHS Codex Context Summary")
                print(f"-------------------------")
                print(f"Domains: {', '.join(result['domains'].keys())}")
                print(f"Frameworks: {', '.join(result['regulatory_frameworks'].keys())}")
                print(f"CMS Resources: {', '.join(result['cms_resources'].keys())}")
                
                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")
                
                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")
            
            elif args.output == "cms":
                print(f"CMS Integration Status")
                print(f"----------------------")
                integration = result["integration"]["hms_ehr"]
                print(f"Status: {integration['status']}")
                print(f"\nComponents:")
                for component in integration["components"]:
                    print(f"  {component['name']}: {component['status']}")
                print(f"\nLast Updated: {integration['last_updated']}")
    
    except HHSException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()