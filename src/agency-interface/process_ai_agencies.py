#!/usr/bin/env python3
"""
Process AI Agencies

This script processes the list of AI domains and creates all necessary
components for integration with the Codex CLI and HMS-DEV.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Agency domain specifications
AI_DOMAINS = [
    "aphis.ai (APHIS – Animal and Plant Health Inspection Service) – Description: AI-driven agriculture and environment protection to prevent environmental damage.",
    "bsee.ai (BSEE – Bureau of Safety and Environmental Enforcement) – Description: AI-driven environment safety to prevent environmental damage.",
    "cber.ai (CBER – Center for Biologics Evaluation and Research) – Description: AI-powered testing and regulation of biologic drugs.",
    "cder.ai (CDER – Center for Drug Evaluation and Research) – Description: AI-powered testing and regulation of drugs.",
    "cfsan.ai (CFSAN – Center for Food Safety and Applied Nutrition) – Description: AI-driven approach for food safety to reduce recalls and improve nutrition.",
    "cnpp.ai (CNPP – Center for Nutrition Policy and Promotion) – Description: AI-powered nutrition policy and programs to prevent malnutrition.",
    "cpsc.ai (CPSC – Consumer Product Safety Commission) – Description: AI-powered consumer product safety oversight to prevent product recalls.",
    "crohns.ai (Crohn's Disease Prevention) – Description: AI solutions to detect, manage, and help prevent Crohn's disease.",
    "csfc.ai (CSFC – Commission on Security and Cooperation in Europe) – Description: AI-enhanced monitoring of human rights, security, and cooperation commitments in Europe.",
    "doed.ai (DOE – Department of Education) – Description: AI-supported educational policy planning and program management.",
    "fhfa.ai (FHFA – Federal Housing Finance Agency) – Description: AI-powered housing finance to prevent a 2008-style housing crisis.",
    "hrsa.ai (HRSA – Health Resources and Services Administration) – Description: AI-driven resource allocation and support for healthcare providers.",
    "hsin.ai (HSIN – Homeland Security Information Network) – Description: AI-enhanced secure information-sharing network for emergency response and security.",
    "naacp.ai (NAACP – National Association for the Advancement of Colored People) – Description: AI-powered urban health and wellness initiatives.",
    "nccih.ai (NCCIH – National Center for Complementary and Integrative Health) – Description: AI solutions for integrative health coverage to prevent insurance fraud.",
    "nhtsa.ai (NHTSA – National Highway Traffic Safety Administration) – Description: AI-powered traffic safety analysis to reduce vehicle accidents.",
    "niddk.ai (NIDDK – National Institute of Diabetes and Digestive and Kidney Diseases) – Description: AI coverage to prevent insurance fraud and improve disease management.",
    "nslp.ai (NSLP – National School Lunch Program) – Description: AI-assisted program planning and monitoring for school nutrition.",
    "ntsb.ai (NTSB – National Transportation Safety Board) – Description: AI-powered oversight to help prevent transportation accidents.",
    "oash.ai (OASH – Office of the Assistant Secretary for Health) – Description: AI-supported public health policy coordination.",
    "ondcp.ai (ONDCP – Office of National Drug Control Policy) – Description: AI-powered Office of National Drug Control Policy to prevent drug abuse.",
    "phm.ai (PHM – Population Health Management) – Description: Record / case management.",
    "spuhc.ai (SPUHC – Specialty Provider Utility Health Care) – Description: AI-powered insurance service to prevent fraud.",
    "tlnt.ai (TLNT – Talent Management) – Description: AI-driven talent management and workforce development.",
    "usich.ai (USICH – U.S. Interagency Council on Homelessness) – Description: AI-powered approach to prevent and end homelessness.",
    "usitc.ai (USITC – U.S. International Trade Commission) – Description: AI-assisted trade analysis and tariff investigations.",
    "ustda.ai (USTDA – U.S. Trade and Development Agency) – Description: Use data from UNDP to find opportunities for American trade deals that benefit the deficit."
]

# Phase 1 agency domains (high priority for immediate implementation)
PHASE_1_AGENCIES = [
    "cber.ai",  # Healthcare core
    "cder.ai",  # Healthcare core
    "hrsa.ai",  # Healthcare core
    "aphis.ai",  # Safety core
    "nhtsa.ai",  # Safety core
    "cpsc.ai"   # Safety core
]

# Phase 2 agency domains
PHASE_2_AGENCIES = [
    "fhfa.ai",  # Economic core
    "usitc.ai",  # Economic core
    "spuhc.ai",  # Economic core
    "cfsan.ai",  # Additional health
    "niddk.ai",  # Additional health
    "crohns.ai"  # Additional health
]

def write_agency_file(agencies, phase, output_dir):
    """
    Write agency list to a file.
    
    Args:
        agencies: List of agency domains
        phase: Phase number
        output_dir: Output directory
    """
    output_file = os.path.join(output_dir, f"phase{phase}_ai_agencies.txt")
    with open(output_file, 'w') as f:
        for agency in agencies:
            # Find the matching full agency spec
            for spec in AI_DOMAINS:
                if spec.startswith(agency):
                    f.write(f"{spec}\n")
                    break
    
    print(f"Created Phase {phase} agency file: {output_file}")
    return output_file

def create_setup_script(output_dir):
    """
    Create setup script for AI domains.
    
    Args:
        output_dir: Output directory
    """
    setup_script = os.path.join(output_dir, "setup_ai_domains.sh")
    
    script_content = """#!/bin/bash
# Setup AI Domains
#
# This script sets up the necessary components for AI domains integration
# with the HMS-DEV system.

# Create necessary directories
mkdir -p ~/.codex/agency-config/ai_domains
mkdir -p ~/.codex/agency-data/ai_domains

# Process Phase 1 (high priority) agencies
echo "Processing Phase 1 AI agencies..."
python ai_agency_generator.py --file phase1_ai_agencies.txt

# Create test domains data
mkdir -p ./config/ai_domains/data

# Create integration completion tracker
echo '{
  "ai_domains": {
    "last_updated": "'$(date -Iseconds)'",
    "phase1_complete": false,
    "phase2_complete": false,
    "overall_progress": 0,
    "domains_processed": []
  }
}' > ./config/ai_domains/integration_status.json

echo "Phase 1 AI domain setup complete."
echo "To process Phase 2 agencies, run: python ai_agency_generator.py --file phase2_ai_agencies.txt"
"""
    
    with open(setup_script, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(setup_script, 0o755)
    
    print(f"Created setup script: {setup_script}")
    return setup_script

def main():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="Process AI Agencies")
    parser.add_argument("--output-dir", default=os.path.dirname(os.path.abspath(__file__)),
                       help="Output directory for agency files")
    parser.add_argument("--setup", action="store_true", 
                       help="Create setup script")
    parser.add_argument("--run", action="store_true",
                       help="Run setup script after creating it")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Write agency files
    phase1_file = write_agency_file(PHASE_1_AGENCIES, 1, args.output_dir)
    phase2_file = write_agency_file(PHASE_2_AGENCIES, 2, args.output_dir)
    
    # Create setup script if requested
    if args.setup:
        setup_script = create_setup_script(args.output_dir)
        
        # Run setup script if requested
        if args.run:
            print(f"Running setup script: {setup_script}")
            result = subprocess.run([setup_script], cwd=args.output_dir, shell=True)
            print(f"Setup script completed with exit code {result.returncode}")
    
    print("AI agency processing complete.")

if __name__ == "__main__":
    main()