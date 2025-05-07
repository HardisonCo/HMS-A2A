#!/usr/bin/env python3
"""
Standards Converter for HMS-A2A

This module converts HMS-SME standards format to HMS-A2A format.
It handles the migration of standards database from legacy format to the new
HMS-A2A format with proper structure and validation.
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("standards_converter")

class StandardsConverter:
    """
    Converts standards from HMS-SME format to HMS-A2A format.
    
    This class handles the transformation of standards database files
    ensuring proper structure, validation rules, and metadata are preserved.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the standards converter with configuration.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.cache = {}
        self.domain_mappings = self._load_domain_mappings()
        
    def _load_domain_mappings(self) -> Dict[str, List[str]]:
        """
        Load domain mappings for standards categories.
        
        Returns:
            Dictionary mapping domains to standard categories
        """
        # Default domain mappings
        mappings = {
            "healthcare": [
                "NUTRITION_CARE_PROCESS", "MEDICAL_RECORDS", "HEALTHCARE_STANDARDS",
                "PATIENT_SAFETY", "MEDICAL_CODING", "HIPAA", "HL7", "CDISC", "FHIR"
            ],
            "finance": [
                "ACCOUNTING_STANDARDS", "FINANCIAL_REPORTING", "BANKING_STANDARDS",
                "INVESTMENT_GUIDELINES", "ACORD", "SWIFT"
            ],
            "legal": [
                "CONTRACT_STANDARDS", "LEGAL_DOCUMENTATION", "COMPLIANCE_REQUIREMENTS",
                "REGULATORY_FRAMEWORKS", "CASE_CITATIONS"
            ],
            "technology": [
                "DATA_FORMATS", "API_STANDARDS", "SECURITY_PROTOCOLS",
                "SYSTEM_REQUIREMENTS", "INFRASTRUCTURE_STANDARDS", "BIM", "CCSDS"
            ],
            "general": [
                "DOCUMENTATION_STANDARDS", "COMMUNICATION_PROTOCOLS", "PROJECT_MANAGEMENT",
                "QUALITY_ASSURANCE", "ISO_STANDARDS"
            ]
        }
        
        # Attempt to load custom mappings from config
        custom_mappings_path = self.config.get("domain_mappings_path")
        if custom_mappings_path and os.path.exists(custom_mappings_path):
            try:
                with open(custom_mappings_path, 'r', encoding='utf-8') as f:
                    custom_mappings = json.load(f)
                # Merge with default mappings
                for domain, standards in custom_mappings.items():
                    if domain in mappings:
                        mappings[domain].extend(standards)
                    else:
                        mappings[domain] = standards
                logger.info(f"Loaded custom domain mappings from {custom_mappings_path}")
            except Exception as e:
                logger.error(f"Error loading custom domain mappings: {str(e)}")
        
        return mappings
    
    def _get_standard_domain(self, standard_id: str, metadata: Dict[str, Any]) -> str:
        """
        Determine the domain for a standard based on ID and metadata.
        
        Args:
            standard_id: The standard identifier
            metadata: Standard metadata
            
        Returns:
            Domain name (healthcare, finance, legal, etc.)
        """
        # Check if standard ID is directly mapped to a domain
        for domain, standards in self.domain_mappings.items():
            if standard_id in standards:
                return domain
        
        # Check industry field if available
        industry = metadata.get("industry", [])
        if isinstance(industry, list) and industry:
            # Map common industry names to domains
            industry_domain_map = {
                "Healthcare": "healthcare",
                "Health": "healthcare",
                "Medical": "healthcare",
                "Clinical": "healthcare",
                "Finance": "finance",
                "Financial": "finance",
                "Banking": "finance",
                "Investment": "finance",
                "Insurance": "finance",
                "Legal": "legal",
                "Law": "legal",
                "Compliance": "legal",
                "Regulatory": "legal",
                "Technology": "technology",
                "IT": "technology",
                "Software": "technology",
                "Computing": "technology",
                "Engineering": "technology"
            }
            
            for ind in industry:
                for key, domain in industry_domain_map.items():
                    if key in ind:
                        return domain
        
        # Default to general
        return "general"
    
    def _generate_standard_id(self, original_id: str, metadata: Dict[str, Any]) -> str:
        """
        Generate a consistent standard ID for HMS-A2A format.
        
        Args:
            original_id: Original standard identifier
            metadata: Standard metadata
            
        Returns:
            HMS-A2A standard identifier
        """
        # If original ID follows naming conventions, use it with prefix
        if original_id and original_id.isupper() and "_" in original_id:
            return f"STD-{original_id}"
        
        # Otherwise, generate from name or description
        name = metadata.get("name", "")
        if not name:
            org = metadata.get("organization", {})
            if isinstance(org, dict):
                name = org.get("name", "")
            elif isinstance(org, str):
                name = org
                
        desc = metadata.get("description", "")
        source = name if name else desc
        
        if not source:
            # If no useful source, use hash of original ID
            return f"STD-{hashlib.md5(original_id.encode()).hexdigest()[:8].upper()}"
            
        # Create a standardized ID from the name
        words = source.split()[:3]  # Use first 3 words
        id_base = "_".join([w.upper() for w in words if w])
        
        return f"STD-{id_base}"
    
    def _convert_validation_rules(self, rules: Any) -> List[Dict[str, Any]]:
        """
        Convert validation rules to HMS-A2A format.
        
        Args:
            rules: Original validation rules
            
        Returns:
            List of validation rules in HMS-A2A format
        """
        result = []
        
        if not rules:
            return result
            
        if isinstance(rules, dict):
            # Process different rule categories
            for category, category_rules in rules.items():
                if isinstance(category_rules, list):
                    for rule in category_rules:
                        if isinstance(rule, dict):
                            # Extract rule details
                            rule_text = rule.get("rule", "")
                            required_fields = rule.get("required_fields", [])
                            approved_methods = rule.get("approved_methods", [])
                            
                            # Convert to HMS-A2A format
                            converted_rule = {
                                "id": f"RULE-{hashlib.md5(rule_text.encode()).hexdigest()[:8].upper()}",
                                "name": category,
                                "description": rule_text,
                                "severity": "error",
                                "type": "structure"
                            }
                            
                            # Add validation criteria
                            criteria = {}
                            if required_fields:
                                criteria["required_fields"] = required_fields
                            if approved_methods:
                                criteria["allowed_values"] = approved_methods
                                
                            if criteria:
                                converted_rule["criteria"] = criteria
                                
                            result.append(converted_rule)
        
        return result
    
    def _extract_test_cases(self, test_scenarios: Any) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract test cases from test scenarios.
        
        Args:
            test_scenarios: Test scenarios from original standard
            
        Returns:
            Dictionary with passing and failing test cases
        """
        result = {
            "passing": [],
            "failing": []
        }
        
        if not test_scenarios or not isinstance(test_scenarios, dict):
            return result
        
        # Process passing cases
        passing_cases = test_scenarios.get("passing_cases", [])
        if isinstance(passing_cases, list):
            for case in passing_cases:
                if isinstance(case, dict):
                    result["passing"].append({
                        "description": case.get("description", ""),
                        "data": case.get("data", {})
                    })
        
        # Process failing cases
        failing_cases = test_scenarios.get("failing_cases", [])
        if isinstance(failing_cases, list):
            for case in failing_cases:
                if isinstance(case, dict):
                    result["failing"].append({
                        "description": case.get("description", ""),
                        "data": case.get("data", {}),
                        "expected_errors": case.get("expected_errors", [])
                    })
        
        return result
    
    def _convert_to_a2a_format(self, standard_id: str, standard_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a single standard to HMS-A2A format.
        
        Args:
            standard_id: Original standard identifier
            standard_data: Original standard data
            
        Returns:
            Standard in HMS-A2A format
        """
        # Get domain for this standard
        domain = self._get_standard_domain(standard_id, standard_data)
        
        # Generate HMS-A2A standard ID
        a2a_id = self._generate_standard_id(standard_id, standard_data)
        
        # Extract organization information
        org_info = standard_data.get("organization", {})
        organization = {}
        
        if isinstance(org_info, dict):
            organization = {
                "name": org_info.get("name", ""),
                "website": org_info.get("website", ""),
                "type": org_info.get("type", ""),
                "headquarters": org_info.get("headquarters", ""),
                "founded": org_info.get("founded", ""),
                "mission": org_info.get("mission", "")
            }
        elif isinstance(org_info, str):
            organization = {
                "name": org_info
            }
        
        # Extract specification information
        spec_info = standard_data.get("specification", {})
        specification = {}
        
        if isinstance(spec_info, dict):
            specification = {
                "version": spec_info.get("version", "1.0"),
                "documentation_url": spec_info.get("documentation", spec_info.get("documentation_url", "")),
                "overview": spec_info.get("overview", "")
            }
        
        # Extract industries and applications
        industries = []
        applications = []
        
        industry_apps = standard_data.get("industry_applications", {})
        if isinstance(industry_apps, dict):
            sectors = industry_apps.get("sectors", [])
            if isinstance(sectors, list):
                industries.extend(sectors)
                
            use_cases = industry_apps.get("use_cases", [])
            if isinstance(use_cases, list):
                applications.extend(use_cases)
        
        # Also check direct industry field
        direct_industry = standard_data.get("industry", [])
        if isinstance(direct_industry, list):
            industries.extend(direct_industry)
        
        # Check direct applications field
        direct_apps = standard_data.get("applications", [])
        if isinstance(direct_apps, list):
            applications.extend(direct_apps)
        
        # Extract resources
        resources = []
        res_info = standard_data.get("resources", {})
        
        if isinstance(res_info, dict):
            for category, items in res_info.items():
                if isinstance(items, list):
                    resources.extend(items)
        
        # Extract actors/roles
        actors = []
        actor_info = standard_data.get("actors", [])
        
        if isinstance(actor_info, list):
            for actor in actor_info:
                if isinstance(actor, dict):
                    actors.append({
                        "role": actor.get("role", ""),
                        "responsibilities": actor.get("responsibilities", [])
                    })
                elif isinstance(actor, str):
                    actors.append({
                        "role": actor,
                        "responsibilities": []
                    })
        
        # Convert validation rules
        validation_rules = self._convert_validation_rules(standard_data.get("validation_rules", {}))
        
        # Extract test cases
        test_cases = self._extract_test_cases(standard_data.get("test_scenarios", {}))
        
        # Create HMS-A2A format standard
        a2a_standard = {
            "id": a2a_id,
            "name": standard_id.replace("_", " ").title(),
            "domain": domain,
            "description": standard_data.get("description", ""),
            "version": "1.0",
            "created_date": datetime.now().isoformat(),
            "updated_date": datetime.now().isoformat(),
            "organization": organization,
            "specification": specification,
            "industries": list(set(industries)),
            "applications": list(set(applications)),
            "resources": resources,
            "actors": actors,
            "validation_rules": validation_rules,
            "test_cases": test_cases,
            "source_format": "HMS-SME",
            "source_id": standard_id
        }
        
        return a2a_standard
    
    def convert_standards_file(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Convert an entire standards file to HMS-A2A format.
        
        Args:
            input_file: Path to input file in HMS-SME format
            output_file: Path to output file for HMS-A2A format
            
        Returns:
            Dictionary with conversion statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting conversion of {input_file} to HMS-A2A format")
        
        try:
            # Load input file
            with open(input_file, 'r', encoding='utf-8') as f:
                standards_data = json.load(f)
            
            if not standards_data:
                logger.error("No standards data found in input file")
                return {"error": "No standards data found", "standards_count": 0}
            
            # Process each standard
            a2a_standards = {}
            processed_count = 0
            error_count = 0
            
            for standard_id, standard_data in standards_data.items():
                try:
                    a2a_standard = self._convert_to_a2a_format(standard_id, standard_data)
                    a2a_standards[a2a_standard["id"]] = a2a_standard
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error converting standard {standard_id}: {str(e)}")
                    error_count += 1
            
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save converted standards
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(a2a_standards, f, indent=2)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Conversion completed in {duration:.2f} seconds")
            logger.info(f"Processed {processed_count} standards with {error_count} errors")
            logger.info(f"Output saved to {output_file}")
            
            return {
                "standards_count": processed_count,
                "error_count": error_count,
                "duration_seconds": duration,
                "input_file": input_file,
                "output_file": output_file,
                "completion_time": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing standards file: {str(e)}")
            return {"error": str(e), "standards_count": 0}
    
    def convert_industry_standards(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Convert industry standards file to HMS-A2A format.
        
        This method is specialized for the industry standards format
        which has a slightly different structure.
        
        Args:
            input_file: Path to input file with industry standards
            output_file: Path to output file for HMS-A2A format
            
        Returns:
            Dictionary with conversion statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting conversion of industry standards from {input_file}")
        
        try:
            # Load input file
            with open(input_file, 'r', encoding='utf-8') as f:
                standards_data = json.load(f)
            
            if not standards_data:
                logger.error("No standards data found in input file")
                return {"error": "No standards data found", "standards_count": 0}
            
            # Process each industry standard
            a2a_standards = {}
            processed_count = 0
            error_count = 0
            
            for standard_id, standard_data in standards_data.items():
                try:
                    # Add specification_url as documentation if available
                    spec_url = standard_data.get("specification_url", "")
                    if spec_url and "specification" not in standard_data:
                        standard_data["specification"] = {
                            "documentation": spec_url,
                            "version": "1.0"
                        }
                    
                    a2a_standard = self._convert_to_a2a_format(standard_id, standard_data)
                    a2a_standards[a2a_standard["id"]] = a2a_standard
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error converting industry standard {standard_id}: {str(e)}")
                    error_count += 1
            
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save converted standards
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(a2a_standards, f, indent=2)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Industry standards conversion completed in {duration:.2f} seconds")
            logger.info(f"Processed {processed_count} standards with {error_count} errors")
            logger.info(f"Output saved to {output_file}")
            
            return {
                "standards_count": processed_count,
                "error_count": error_count,
                "duration_seconds": duration,
                "input_file": input_file,
                "output_file": output_file,
                "completion_time": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing industry standards file: {str(e)}")
            return {"error": str(e), "standards_count": 0}
    
    def merge_standards_files(self, input_files: List[str], output_file: str) -> Dict[str, Any]:
        """
        Merge multiple HMS-A2A standards files into one.
        
        Args:
            input_files: List of HMS-A2A standards files to merge
            output_file: Path to output merged file
            
        Returns:
            Dictionary with merge statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting merge of {len(input_files)} standards files")
        
        try:
            # Initialize merged standards
            merged_standards = {}
            processed_count = 0
            
            # Process each input file
            for input_file in input_files:
                logger.info(f"Processing {input_file}")
                
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        standards_data = json.load(f)
                    
                    if not standards_data:
                        logger.warning(f"No standards data found in {input_file}")
                        continue
                    
                    # Add standards to merged collection
                    for standard_id, standard_data in standards_data.items():
                        if standard_id in merged_standards:
                            # If duplicate, keep the newer one based on updated_date
                            existing_date = merged_standards[standard_id].get("updated_date", "")
                            new_date = standard_data.get("updated_date", "")
                            
                            if new_date > existing_date:
                                merged_standards[standard_id] = standard_data
                                logger.debug(f"Updated standard {standard_id} with newer version")
                        else:
                            merged_standards[standard_id] = standard_data
                            processed_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing file {input_file}: {str(e)}")
            
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save merged standards
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(merged_standards, f, indent=2)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Merge completed in {duration:.2f} seconds")
            logger.info(f"Merged {processed_count} standards")
            logger.info(f"Output saved to {output_file}")
            
            return {
                "standards_count": processed_count,
                "input_files": input_files,
                "output_file": output_file,
                "duration_seconds": duration,
                "completion_time": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error merging standards files: {str(e)}")
            return {"error": str(e), "standards_count": 0}


def main():
    """
    Main function to run the standards converter.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert standards from HMS-SME format to HMS-A2A format'
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert a standards file')
    convert_parser.add_argument('--input', '-i', required=True, help='Input standards file (HMS-SME format)')
    convert_parser.add_argument('--output', '-o', required=True, help='Output file (HMS-A2A format)')
    convert_parser.add_argument('--type', '-t', choices=['standard', 'industry'], default='standard',
                               help='Type of standards file')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple HMS-A2A standards files')
    merge_parser.add_argument('--input', '-i', required=True, nargs='+', help='Input standards files (HMS-A2A format)')
    merge_parser.add_argument('--output', '-o', required=True, help='Output merged file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize converter
    converter = StandardsConverter()
    
    # Process based on command
    if args.command == 'convert':
        if args.type == 'industry':
            result = converter.convert_industry_standards(args.input, args.output)
        else:
            result = converter.convert_standards_file(args.input, args.output)
        
        print(f"Converted {result.get('standards_count', 0)} standards")
        print(f"Output saved to {args.output}")
        
    elif args.command == 'merge':
        result = converter.merge_standards_files(args.input, args.output)
        
        print(f"Merged {result.get('standards_count', 0)} standards")
        print(f"Output saved to {args.output}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()