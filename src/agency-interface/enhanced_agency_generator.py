#!/usr/bin/env python3
"""
Enhanced Agency Generator

An enhanced version of the agency generator with parallel processing,
automatic domain classification, and integration with various system components.
"""

import os
import sys
import json
import argparse
import re
import concurrent.futures
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from string import Template
from datetime import datetime

# Templates for agency components will be imported from agency_generator.py
import agency_generator

# Import additional domain templates
from domain_templates import ADDITIONAL_DOMAIN_TEMPLATES, integrate_domain_templates

class EnhancedAgencyGenerator:
    """
    Enhanced generator for agency-specific components with parallel processing.
    """
    
    def __init__(self, base_dir: str, config_file: str, templates_dir: str,
                 max_workers: int = 4, timeout: int = 600) -> None:
        """
        Initialize the enhanced agency generator.

        Args:
            base_dir: Base directory for agency interface
            config_file: Path to configuration file
            templates_dir: Directory for ASCII art templates
            max_workers: Maximum number of parallel workers
            timeout: Maximum execution time in seconds
        """
        self.base_dir = base_dir
        self.config_file = config_file
        self.templates_dir = templates_dir
        self.max_workers = max_workers
        self.timeout = timeout
        self.config = self._load_config()

        # Import domain templates from agency_generator and integrate with additional templates
        self.domain_templates = integrate_domain_templates(
            agency_generator.DOMAIN_TEMPLATES,
            ADDITIONAL_DOMAIN_TEMPLATES
        )

        # Ensure directories exist
        self._ensure_dirs()
    
    def _load_config(self) -> dict:
        """Load configuration file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return {"agencies": [], "topics": {}}
    
    def _ensure_dirs(self) -> None:
        """Ensure required directories exist."""
        directories = [
            os.path.join(self.base_dir, "agency_issue_finder", "agencies"),
            os.path.join(self.base_dir, "agencies"),
            self.templates_dir,
            os.path.join(self.base_dir, "ffi"),
            os.path.join(self.base_dir, "prover_integration"),
            os.path.join(self.base_dir, "api_integration"),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def classify_agency_domain(self, agency_data: dict) -> str:
        """
        Automatically classify an agency's domain based on its name and description.
        
        Args:
            agency_data: Agency data dictionary
            
        Returns:
            Domain classification string
        """
        name = agency_data.get("name", "").lower()
        description = agency_data.get("description", "").lower()
        
        # Dictionary of domain keywords
        domain_keywords = {
            "healthcare": ["health", "medical", "medicine", "patient", "hospital", "disease", "care"],
            "defense": ["defense", "military", "army", "navy", "air force", "weapon", "security", "armed"],
            "finance": ["treasury", "financial", "banking", "currency", "money", "economic", "tax"],
            "agriculture": ["agriculture", "farm", "food", "crop", "rural", "forest", "livestock"],
            "justice": ["justice", "law", "legal", "court", "crime", "prison", "attorney"],
            "housing": ["housing", "urban", "development", "home", "apartment", "community"],
            "transportation": ["transportation", "highway", "transit", "railway", "aviation", "maritime"],
            "education": ["education", "school", "college", "student", "university", "teacher"],
            "veterans": ["veteran", "military service", "armed service"],
            "interior": ["interior", "land", "park", "conservation", "indigenous", "native"],
            "commerce": ["commerce", "business", "trade", "export", "import", "industry"],
            "labor": ["labor", "employment", "worker", "workplace", "job", "workforce"],
            "security": ["homeland", "security", "border", "emergency", "disaster", "cybersecurity"],
            "energy": ["energy", "power", "electricity", "nuclear", "renewable", "fossil"],
            "diplomacy": ["state", "diplomatic", "foreign", "embassy", "international", "ambassador"],
            "environment": ["environment", "pollution", "climate", "protection", "conservation"],
            "business": ["business", "enterprise", "entrepreneur", "small business", "company"],
            "social": ["social", "security", "welfare", "benefit", "retirement", "disability"],
            "space": ["space", "aeronautics", "aerospace", "satellite", "astronaut", "orbit"],
            "science": ["science", "research", "technology", "engineering", "innovation"],
            "development": ["development", "assistance", "aid", "poverty", "humanitarian"],
            "communications": ["communication", "telecommunications", "broadcasting", "spectrum"],
            "personnel": ["personnel", "human resources", "staffing", "employee", "federal employee"]
        }
        
        # Check name and description against domain keywords
        scores = {domain: 0 for domain in domain_keywords}
        
        for domain, keywords in domain_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    scores[domain] += 3
                if keyword in description:
                    scores[domain] += 1
        
        # Get the domain with the highest score
        max_score = 0
        best_domain = "general"
        
        for domain, score in scores.items():
            if score > max_score:
                max_score = score
                best_domain = domain
        
        # Default to general if no good match found
        return best_domain if max_score > 0 else "general"
    
    def generate_agencies_parallel(self, agency_acronyms: List[str], components: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Generate components for multiple agencies in parallel.
        
        Args:
            agency_acronyms: List of agency acronyms
            components: Optional list of specific components to generate
            
        Returns:
            Dictionary mapping agency acronyms to success status
        """
        results = {}
        
        # Create a generator instance from the original agency_generator
        generator = agency_generator.AgencyGenerator(self.base_dir, self.config_file, self.templates_dir)
        
        print(f"Generating components for {len(agency_acronyms)} agencies with {self.max_workers} workers...")
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            # Submit tasks for each agency
            for agency in agency_acronyms:
                if components and len(components) > 0:
                    # Submit one task per component
                    for component in components:
                        future = executor.submit(generator.generate_agency, agency, component)
                        futures[future] = (agency, component)
                else:
                    # Submit one task for all components
                    future = executor.submit(generator.generate_agency, agency)
                    futures[future] = (agency, None)
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(futures, timeout=self.timeout):
                agency, component = futures[future]
                component_str = f" ({component})" if component else ""
                
                try:
                    success = future.result()
                    print(f"{'✓' if success else '✗'} {agency}{component_str}")
                    
                    if agency not in results:
                        results[agency] = success
                    else:
                        # If any component fails, mark the whole agency as failed
                        results[agency] = results[agency] and success
                
                except Exception as e:
                    print(f"✗ {agency}{component_str} - Error: {e}")
                    results[agency] = False
        
        elapsed_time = time.time() - start_time
        print(f"Generation completed in {elapsed_time:.2f} seconds.")
        
        # Count successes and failures
        successes = sum(1 for success in results.values() if success)
        failures = sum(1 for success in results.values() if not success)
        
        print(f"\nSummary: {successes} succeeded, {failures} failed")
        
        if failures > 0:
            print("Failed agencies:")
            for agency, success in results.items():
                if not success:
                    print(f"  - {agency}")
        
        return results
    
    def generate_agencies_by_tier(self, tier: int, components: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Generate components for agencies in a specific tier.
        
        Args:
            tier: Agency tier
            components: Optional list of specific components to generate
            
        Returns:
            Dictionary mapping agency acronyms to success status
        """
        # Find agencies in the specified tier
        agency_acronyms = []
        
        for agency_data in self.config.get("agencies", []):
            agency_tier = agency_data.get("tier")
            agency = agency_data.get("acronym")
            
            if agency_tier == tier and agency:
                agency_acronyms.append(agency)
        
        if not agency_acronyms:
            print(f"No agencies found in Tier {tier}")
            return {}
        
        print(f"Found {len(agency_acronyms)} agencies in Tier {tier}")
        return self.generate_agencies_parallel(agency_acronyms, components)
    
    def generate_all_agencies(self, components: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Generate components for all agencies in the configuration.
        
        Args:
            components: Optional list of specific components to generate
            
        Returns:
            Dictionary mapping agency acronyms to success status
        """
        # Get all agency acronyms
        agency_acronyms = []
        
        for agency_data in self.config.get("agencies", []):
            agency = agency_data.get("acronym")
            if agency:
                agency_acronyms.append(agency)
        
        if not agency_acronyms:
            print("No agencies found in configuration")
            return {}
        
        print(f"Found {len(agency_acronyms)} agencies in configuration")
        return self.generate_agencies_parallel(agency_acronyms, components)
    
    def generate_agencies_from_file(self, file_path: str, components: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Generate components for agencies listed in a file.
        
        Args:
            file_path: Path to file containing agency acronyms
            components: Optional list of specific components to generate
            
        Returns:
            Dictionary mapping agency acronyms to success status
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract agency acronyms from file (ignore comments and empty lines)
            agency_acronyms = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    agency_acronyms.append(line)
            
            if not agency_acronyms:
                print(f"No agencies found in file {file_path}")
                return {}
            
            print(f"Found {len(agency_acronyms)} agencies in file {file_path}")
            return self.generate_agencies_parallel(agency_acronyms, components)
        
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
    
    def generate_ffi_bindings(self, agency_acronyms: List[str]) -> Dict[str, bool]:
        """
        Generate FFI bindings for agency context access.
        
        Args:
            agency_acronyms: List of agency acronyms
            
        Returns:
            Dictionary mapping agency acronyms to success status
        """
        results = {}
        
        # Create FFI directory if it doesn't exist
        ffi_dir = os.path.join(self.base_dir, "ffi")
        os.makedirs(ffi_dir, exist_ok=True)
        
        # FFI binding template for C
        c_binding_template = """// Agency FFI binding for ${AGENCY}
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// Get agency context for ${AGENCY}
const char* ${AGENCY_LOWER}_get_context() {
    // This would be replaced with actual implementation
    // that retrieves context from the agency system
    static const char* context = "${AGENCY_JSON}";
    return context;
}

// Free agency context
void ${AGENCY_LOWER}_free_context(char* context) {
    if (context != NULL) {
        free(context);
    }
}
"""
        
        # FFI binding template for Rust
        rust_binding_template = """// Agency FFI binding for ${AGENCY}
use std::ffi::{c_char, CStr, CString};
use std::os::raw::c_void;

#[no_mangle]
pub extern "C" fn ${AGENCY_LOWER}_get_context() -> *mut c_char {
    // This would be replaced with actual implementation
    // that retrieves context from the agency system
    let context = r#"${AGENCY_JSON}"#;
    let c_string = CString::new(context).unwrap();
    c_string.into_raw()
}

#[no_mangle]
pub extern "C" fn ${AGENCY_LOWER}_free_context(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe { CString::from_raw(ptr) };
    }
}
"""
        
        # Generate bindings for each agency
        for agency in agency_acronyms:
            try:
                # Find agency in config
                agency_data = None
                for a in self.config.get("agencies", []):
                    if a.get("acronym") == agency:
                        agency_data = a
                        break
                
                if not agency_data:
                    print(f"Error: Agency {agency} not found in configuration.")
                    results[agency] = False
                    continue
                
                # Create JSON representation of agency data
                agency_json = json.dumps(agency_data, indent=2).replace('"', '\\"')
                
                # Create template substitution dictionary
                substitutions = {
                    "AGENCY": agency,
                    "AGENCY_LOWER": agency.lower(),
                    "AGENCY_JSON": agency_json
                }
                
                # Generate C binding
                c_template = Template(c_binding_template)
                c_binding = c_template.substitute(**substitutions)
                
                c_binding_file = os.path.join(ffi_dir, f"{agency.lower()}_binding.c")
                with open(c_binding_file, 'w') as f:
                    f.write(c_binding)
                
                # Generate Rust binding
                rust_template = Template(rust_binding_template)
                rust_binding = rust_template.substitute(**substitutions)
                
                rust_binding_file = os.path.join(ffi_dir, f"{agency.lower()}_binding.rs")
                with open(rust_binding_file, 'w') as f:
                    f.write(rust_binding)
                
                results[agency] = True
                print(f"Generated FFI bindings for {agency}")
            
            except Exception as e:
                print(f"Error generating FFI bindings for {agency}: {e}")
                results[agency] = False
        
        return results
    
    def generate_prover_integration(self, agency_acronyms: List[str]) -> Dict[str, bool]:
        """
        Generate prover integration for agency theorem verification.
        
        Args:
            agency_acronyms: List of agency acronyms
            
        Returns:
            Dictionary mapping agency acronyms to success status
        """
        results = {}
        
        # Create prover integration directory if it doesn't exist
        prover_dir = os.path.join(self.base_dir, "prover_integration")
        os.makedirs(prover_dir, exist_ok=True)
        
        # Prover integration template
        prover_template = """#!/usr/bin/env python3
\"\"\"
${AGENCY} Theorem Prover Integration

Integration with the economic theorem prover for ${AGENCY_NAME}.
\"\"\"

import os
import sys
import json
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

class ${AGENCY}TheoremProver:
    \"\"\"
    Theorem prover integration for ${AGENCY}.
    \"\"\"
    
    def __init__(self, base_path: str) -> None:
        \"\"\"
        Initialize the ${AGENCY} theorem prover.
        
        Args:
            base_path: Base path to prover data
        \"\"\"
        self.base_path = base_path
        self.domain = "${DOMAIN}"
        self.theorems = self._load_domain_theorems()
    
    def _load_domain_theorems(self) -> List[Dict[str, Any]]:
        \"\"\"Load domain-specific theorems.\"\"\"
        theorems_file = os.path.join(self.base_path, "${DOMAIN}_theorems.json")
        
        if os.path.exists(theorems_file):
            try:
                with open(theorems_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON in theorems file: {e}")
                return []
        
        # Return default theorems if file not found
        return ${DEFAULT_THEOREMS}
    
    def verify_issue(self, issue: Dict[str, Any]) -> bool:
        \"\"\"
        Verify that an issue is valid according to domain theorems.
        
        Args:
            issue: Issue to verify
            
        Returns:
            True if the issue is valid, False otherwise
        \"\"\"
        # Implementation would be expanded with actual theorem proving logic
        # For now, we'll just check that the issue has required fields
        
        required_fields = ["id", "title", "description", "affected_areas"]
        for field in required_fields:
            if field not in issue:
                return False
        
        return True
    
    def generate_theorems(self, issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        \"\"\"
        Generate theorems from an issue.
        
        Args:
            issue: Issue to generate theorems from
            
        Returns:
            List of theorems
        \"\"\"
        # This would be expanded with actual theorem generation logic
        # For now, we'll just create a simple theorem
        
        theorem = {
            "name": f"Issue_{issue.get('id', 'unknown')}",
            "statement": issue.get('title', ''),
            "proof": f"Proof for {issue.get('title', '')}",
            "verified": True
        }
        
        return [theorem]


def main():
    \"\"\"Main entry point function.\"\"\"
    import argparse
    
    parser = argparse.ArgumentParser(description="${AGENCY} Theorem Prover Integration")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.abspath(__file__)),
                       help="Base path to prover data")
    parser.add_argument("--issue-file", help="Path to issue file to verify")
    parser.add_argument("--generate", action="store_true", help="Generate theorems from issue")
    
    args = parser.parse_args()
    
    try:
        # Initialize the prover
        prover = ${AGENCY}TheoremProver(args.base_path)
        
        if args.issue_file:
            # Load issue from file
            with open(args.issue_file, 'r') as f:
                issue = json.load(f)
            
            # Verify issue
            valid = prover.verify_issue(issue)
            print(f"Issue validity: {valid}")
            
            if args.generate and valid:
                # Generate theorems
                theorems = prover.generate_theorems(issue)
                print(f"Generated {len(theorems)} theorems:")
                for theorem in theorems:
                    print(f"  - {theorem['name']}: {theorem['statement']}")
        else:
            print("No issue file specified.")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
        
        # Default theorems for each domain
        default_theorems = {
            "healthcare": [
                {
                    "name": "Healthcare_Accessibility",
                    "statement": "Healthcare services should be accessible to all individuals",
                    "proof": "Proof for Healthcare_Accessibility",
                    "verified": True
                },
                {
                    "name": "Healthcare_Quality",
                    "statement": "Healthcare services should meet quality standards",
                    "proof": "Proof for Healthcare_Quality",
                    "verified": True
                }
            ],
            "defense": [
                {
                    "name": "Defense_Security",
                    "statement": "Defense systems should maintain national security",
                    "proof": "Proof for Defense_Security",
                    "verified": True
                }
            ],
            # Add default theorems for other domains...
            "general": [
                {
                    "name": "General_Effectiveness",
                    "statement": "Government programs should be effective and efficient",
                    "proof": "Proof for General_Effectiveness",
                    "verified": True
                }
            ]
        }
        
        # Generate prover integration for each agency
        for agency in agency_acronyms:
            try:
                # Find agency in config
                agency_data = None
                for a in self.config.get("agencies", []):
                    if a.get("acronym") == agency:
                        agency_data = a
                        break
                
                if not agency_data:
                    print(f"Error: Agency {agency} not found in configuration.")
                    results[agency] = False
                    continue
                
                # Get agency information
                name = agency_data["name"]
                domain = agency_data.get("domain", "general")
                
                # Get default theorems for domain
                domain_theorems = default_theorems.get(domain, default_theorems["general"])
                
                # Create template substitution dictionary
                substitutions = {
                    "AGENCY": agency,
                    "AGENCY_NAME": name,
                    "DOMAIN": domain,
                    "DEFAULT_THEOREMS": json.dumps(domain_theorems, indent=4)
                }
                
                # Generate prover integration
                template = Template(prover_template)
                prover_integration = template.substitute(**substitutions)
                
                prover_file = os.path.join(prover_dir, f"{agency.lower()}_prover.py")
                with open(prover_file, 'w') as f:
                    f.write(prover_integration)
                
                results[agency] = True
                print(f"Generated prover integration for {agency}")
            
            except Exception as e:
                print(f"Error generating prover integration for {agency}: {e}")
                results[agency] = False
        
        return results


def main():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="Enhanced Agency Generator for Codex CLI")
    parser.add_argument("--agency", help="Agency acronym to generate components for")
    parser.add_argument("--component", choices=["ascii_art", "issue_finder", "research_connector", "ffi", "prover"],
                      help="Specific component to generate (if --agency is specified)")
    parser.add_argument("--all", action="store_true", help="Generate components for all agencies")
    parser.add_argument("--tier", type=int, help="Generate components for agencies in a specific tier")
    parser.add_argument("--file", help="Path to file containing agency acronyms")
    parser.add_argument("--ffi", action="store_true", help="Generate FFI bindings for agencies")
    parser.add_argument("--prover", action="store_true", help="Generate prover integration for agencies")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of parallel workers")
    parser.add_argument("--timeout", type=int, default=600, help="Maximum execution time in seconds")
    parser.add_argument("--base-dir", default=os.path.dirname(os.path.abspath(__file__)),
                       help="Base directory for agency interface")
    parser.add_argument("--config-file", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                           "config", "agency_data.json"),
                       help="Path to configuration file")
    parser.add_argument("--templates-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                            "templates"),
                       help="Directory for ASCII art templates")
    
    args = parser.parse_args()
    
    generator = EnhancedAgencyGenerator(
        args.base_dir, 
        args.config_file, 
        args.templates_dir,
        args.max_workers,
        args.timeout
    )
    
    # Convert component to list of components
    components = [args.component] if args.component else None
    
    # Handle specific agency
    if args.agency:
        if args.ffi:
            success = generator.generate_ffi_bindings([args.agency])
            result_str = "succeeded" if success.get(args.agency, False) else "failed"
            print(f"FFI binding generation {result_str} for {args.agency}.")
        elif args.prover:
            success = generator.generate_prover_integration([args.agency])
            result_str = "succeeded" if success.get(args.agency, False) else "failed"
            print(f"Prover integration generation {result_str} for {args.agency}.")
        else:
            # Use the original agency generator for single agency
            original_generator = agency_generator.AgencyGenerator(args.base_dir, args.config_file, args.templates_dir)
            success = original_generator.generate_agency(args.agency, args.component)
            result_str = "succeeded" if success else "failed"
            component_str = f" ({args.component})" if args.component else ""
            print(f"Generation {result_str} for {args.agency}{component_str}.")
    
    # Handle agencies by tier
    elif args.tier is not None:
        if args.ffi:
            # Find agencies in tier
            agency_acronyms = []
            for agency_data in generator.config.get("agencies", []):
                if agency_data.get("tier") == args.tier and agency_data.get("acronym"):
                    agency_acronyms.append(agency_data["acronym"])
            
            if agency_acronyms:
                generator.generate_ffi_bindings(agency_acronyms)
            else:
                print(f"No agencies found in Tier {args.tier}")
        elif args.prover:
            # Find agencies in tier
            agency_acronyms = []
            for agency_data in generator.config.get("agencies", []):
                if agency_data.get("tier") == args.tier and agency_data.get("acronym"):
                    agency_acronyms.append(agency_data["acronym"])
            
            if agency_acronyms:
                generator.generate_prover_integration(agency_acronyms)
            else:
                print(f"No agencies found in Tier {args.tier}")
        else:
            generator.generate_agencies_by_tier(args.tier, components)
    
    # Handle agencies from file
    elif args.file:
        if args.ffi:
            # Read agencies from file
            with open(args.file, 'r') as f:
                content = f.read()
            
            agency_acronyms = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    agency_acronyms.append(line)
            
            if agency_acronyms:
                generator.generate_ffi_bindings(agency_acronyms)
            else:
                print(f"No agencies found in file {args.file}")
        elif args.prover:
            # Read agencies from file
            with open(args.file, 'r') as f:
                content = f.read()
            
            agency_acronyms = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    agency_acronyms.append(line)
            
            if agency_acronyms:
                generator.generate_prover_integration(agency_acronyms)
            else:
                print(f"No agencies found in file {args.file}")
        else:
            generator.generate_agencies_from_file(args.file, components)
    
    # Handle all agencies
    elif args.all:
        if args.ffi:
            # Get all agency acronyms
            agency_acronyms = []
            for agency_data in generator.config.get("agencies", []):
                if agency_data.get("acronym"):
                    agency_acronyms.append(agency_data["acronym"])
            
            if agency_acronyms:
                generator.generate_ffi_bindings(agency_acronyms)
            else:
                print("No agencies found in configuration")
        elif args.prover:
            # Get all agency acronyms
            agency_acronyms = []
            for agency_data in generator.config.get("agencies", []):
                if agency_data.get("acronym"):
                    agency_acronyms.append(agency_data["acronym"])
            
            if agency_acronyms:
                generator.generate_prover_integration(agency_acronyms)
            else:
                print("No agencies found in configuration")
        else:
            generator.generate_all_agencies(components)
    
    else:
        print("Error: No action specified. Use --agency, --tier, --file, or --all.")


if __name__ == "__main__":
    main()