#!/usr/bin/env python3
"""
Agency Theorem Prover Integration

This module provides integration with the economic theorem prover for agency verification.
It allows agency issues to be verified against domain-specific theorems.
"""

import os
import sys
import json
import importlib
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Default theorem models path
THEOREM_MODELS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theorem_models")


class ProverException(Exception):
    """Exception raised for errors in the prover integration."""
    pass


class AgencyProverIntegration:
    """
    Main class for integrating agencies with the theorem prover.
    """
    
    def __init__(self, config_path: str = None, models_path: str = None):
        """
        Initialize the prover integration.
        
        Args:
            config_path: Path to configuration file
            models_path: Path to theorem models directory
        """
        self.config_path = config_path or os.path.join(parent_dir, "config", "agency_data.json")
        self.models_path = models_path or THEOREM_MODELS_PATH
        self.config = self._load_config()
        self.domain_theorems = {}
        
        # Load domain theorems
        self._load_domain_theorems()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {"agencies": []}
    
    def _load_domain_theorems(self) -> None:
        """
        Load theorem models for all domains.
        """
        # Get all domain files
        domain_files = [f for f in os.listdir(self.models_path) 
                      if f.endswith("_theorems.json") and os.path.isfile(os.path.join(self.models_path, f))]
        
        # Load each domain's theorems
        for domain_file in domain_files:
            domain = domain_file.replace("_theorems.json", "")
            theorem_path = os.path.join(self.models_path, domain_file)
            
            try:
                with open(theorem_path, 'r') as f:
                    self.domain_theorems[domain] = json.load(f)
                    logger.info(f"Loaded theorems for domain: {domain}")
            except Exception as e:
                logger.error(f"Error loading theorems for domain {domain}: {e}")
    
    def get_agency_theorems(self, agency: str) -> List[Dict[str, Any]]:
        """
        Get theorems for a specific agency.
        
        Args:
            agency: Agency acronym
            
        Returns:
            List of theorems
        """
        # Find agency in config
        agency_data = None
        for a in self.config.get("agencies", []):
            if a.get("acronym") == agency:
                agency_data = a
                break
        
        if not agency_data:
            logger.error(f"Agency not found: {agency}")
            return []
        
        # Get domain
        domain = agency_data.get("domain", "general")
        
        # Get theorems for domain
        if domain in self.domain_theorems:
            return self.domain_theorems[domain]
        else:
            logger.warning(f"No theorems found for domain: {domain}")
            return []
    
    def verify_issue(self, agency: str, issue: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify an issue against agency theorems.
        
        Args:
            agency: Agency acronym
            issue: Issue to verify
            
        Returns:
            Tuple of (validity, results)
        """
        # Get agency theorems
        theorems = self.get_agency_theorems(agency)
        
        if not theorems:
            logger.warning(f"No theorems available for {agency}")
            return False, {"error": "No theorems available"}
        
        # Validate issue structure
        if not self._validate_issue_structure(issue):
            logger.error(f"Invalid issue structure: {issue}")
            return False, {"error": "Invalid issue structure"}
        
        # Apply each theorem to verify the issue
        results = {
            "agency": agency,
            "issue_id": issue.get("id", "unknown"),
            "valid": True,
            "theorem_results": []
        }
        
        for theorem in theorems:
            theorem_result = self._apply_theorem(theorem, issue)
            results["theorem_results"].append(theorem_result)
            
            # If any theorem fails, the issue is invalid
            if not theorem_result.get("valid", False):
                results["valid"] = False
        
        return results["valid"], results
    
    def _validate_issue_structure(self, issue: Dict[str, Any]) -> bool:
        """
        Validate the structure of an issue.
        
        Args:
            issue: Issue to validate
            
        Returns:
            True if the issue structure is valid, False otherwise
        """
        # Required fields
        required_fields = ["id", "title", "description", "affected_areas"]
        
        for field in required_fields:
            if field not in issue:
                logger.error(f"Missing required field in issue: {field}")
                return False
        
        return True
    
    def _apply_theorem(self, theorem: Dict[str, Any], issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a theorem to an issue.
        
        Args:
            theorem: Theorem to apply
            issue: Issue to verify
            
        Returns:
            Theorem verification result
        """
        # Basic theorem application - this would be expanded with actual theorem proving logic
        result = {
            "theorem_name": theorem.get("name", "unknown"),
            "theorem_statement": theorem.get("statement", ""),
            "valid": True,
            "verification_steps": []
        }
        
        # Simple verification: check if issue description contains theorem keywords
        statement = theorem.get("statement", "").lower()
        description = issue.get("description", "").lower()
        
        keywords = statement.split()
        for keyword in keywords:
            if len(keyword) > 4 and keyword in description:  # Only check keywords longer than 4 characters
                result["verification_steps"].append({
                    "step": "keyword_check",
                    "keyword": keyword,
                    "found": True
                })
            elif len(keyword) > 4:
                result["verification_steps"].append({
                    "step": "keyword_check",
                    "keyword": keyword,
                    "found": False
                })
                result["valid"] = False
        
        # Additional verification logic would be added here
        
        return result
    
    def generate_theorem(self, issue: Dict[str, Any], domain: str = "general") -> Dict[str, Any]:
        """
        Generate a theorem from an issue.
        
        Args:
            issue: Issue to generate theorem from
            domain: Domain for the theorem
            
        Returns:
            Generated theorem
        """
        # This would be expanded with actual theorem generation logic
        
        # Basic theorem generation
        theorem = {
            "name": f"Issue_{issue.get('id', 'unknown')}",
            "statement": issue.get("title", ""),
            "proof": f"Automatic proof generated for issue: {issue.get('id', 'unknown')}",
            "verified": True,
            "domain": domain,
            "generated_from": issue.get("id", "unknown"),
            "timestamp": None,  # Added at runtime
            "components": []
        }
        
        # Extract components from affected areas
        if "affected_areas" in issue:
            theorem["components"] = [area.lower().replace(" ", "_") for area in issue["affected_areas"]]
        
        return theorem
    
    def save_theorem(self, theorem: Dict[str, Any], domain: str = "general") -> bool:
        """
        Save a theorem to the theorem models.
        
        Args:
            theorem: Theorem to save
            domain: Domain for the theorem
            
        Returns:
            True if the theorem was saved successfully, False otherwise
        """
        # Get the domain theorems
        theorems = self.domain_theorems.get(domain, [])
        
        # Check if the theorem already exists
        for i, existing_theorem in enumerate(theorems):
            if existing_theorem.get("name") == theorem.get("name"):
                # Update existing theorem
                theorems[i] = theorem
                break
        else:
            # Add new theorem
            theorems.append(theorem)
        
        # Update domain theorems
        self.domain_theorems[domain] = theorems
        
        # Save theorems to file
        theorem_path = os.path.join(self.models_path, f"{domain}_theorems.json")
        try:
            with open(theorem_path, 'w') as f:
                json.dump(theorems, indent=2, fp=f)
            return True
        except Exception as e:
            logger.error(f"Error saving theorem: {e}")
            return False
    
    def get_theorem_model_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the theorem models.
        
        Returns:
            Dictionary with theorem model statistics
        """
        stats = {
            "domains": [],
            "total_theorems": 0,
            "verified_theorems": 0,
            "domain_stats": {}
        }
        
        for domain, theorems in self.domain_theorems.items():
            domain_stats = {
                "name": domain,
                "total_theorems": len(theorems),
                "verified_theorems": sum(1 for t in theorems if t.get("verified", False)),
                "coverage": len(set(t.get("components", []) for t in theorems))
            }
            
            stats["domains"].append(domain)
            stats["total_theorems"] += domain_stats["total_theorems"]
            stats["verified_theorems"] += domain_stats["verified_theorems"]
            stats["domain_stats"][domain] = domain_stats
        
        return stats


def main():
    """Main entry point function."""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Agency Theorem Prover Integration")
    parser.add_argument("--agency", help="Agency acronym")
    parser.add_argument("--issue-file", help="Path to issue file to verify")
    parser.add_argument("--generate", action="store_true", help="Generate theorem from issue")
    parser.add_argument("--save", action="store_true", help="Save generated theorem")
    parser.add_argument("--domain", help="Domain for generated theorem")
    parser.add_argument("--stats", action="store_true", help="Show theorem model statistics")
    parser.add_argument("--config", help="Path to agency configuration file")
    parser.add_argument("--models", help="Path to theorem models directory")
    
    args = parser.parse_args()
    
    try:
        # Initialize prover integration
        prover = AgencyProverIntegration(args.config, args.models)
        
        if args.stats:
            # Show theorem model statistics
            stats = prover.get_theorem_model_stats()
            print("Theorem Model Statistics:")
            print(f"Total Theorems: {stats['total_theorems']}")
            print(f"Verified Theorems: {stats['verified_theorems']}")
            print(f"Domains: {', '.join(stats['domains'])}")
            print("\nDomain Statistics:")
            for domain, domain_stats in stats["domain_stats"].items():
                print(f"  {domain}:")
                print(f"    Total Theorems: {domain_stats['total_theorems']}")
                print(f"    Verified Theorems: {domain_stats['verified_theorems']}")
                print(f"    Coverage: {domain_stats['coverage']} components")
        
        elif args.agency and args.issue_file:
            # Load issue from file
            with open(args.issue_file, 'r') as f:
                issue = json.load(f)
            
            # Verify issue
            valid, results = prover.verify_issue(args.agency, issue)
            print(f"Issue Validity: {valid}")
            print("Verification Results:")
            print(json.dumps(results, indent=2))
            
            if args.generate:
                # Generate theorem from issue
                domain = args.domain or "general"
                theorem = prover.generate_theorem(issue, domain)
                
                # Add timestamp
                theorem["timestamp"] = datetime.now().isoformat()
                
                print("\nGenerated Theorem:")
                print(json.dumps(theorem, indent=2))
                
                if args.save:
                    # Save theorem
                    success = prover.save_theorem(theorem, domain)
                    print(f"\nTheorem {'saved successfully' if success else 'could not be saved'}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()