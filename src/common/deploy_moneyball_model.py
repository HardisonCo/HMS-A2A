#!/usr/bin/env python3
"""
Moneyball Deal Model Deployment Script

This script orchestrates the phased deployment of the Moneyball Deal Model
across agency documentation, implementing the 5-agency checkpoint system
for quality control and continuous improvement.
"""

import os
import json
import argparse
import subprocess
import time
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re
import glob
import shutil

# Define the phases and checkpoint agencies
DEPLOYMENT_PHASES = [
    {
        "name": "Phase 1: Core Financial Agencies",
        "agencies": ["fed", "treasury", "sec", "fdic", "cfpb"],
        "focus": "Financial value optimization and risk management",
        "checkpoint_criteria": [
            "Financial value calculation accuracy",
            "Risk quantification methodology",
            "Deal structure adaptability for financial context",
            "Regulatory compliance integration"
        ]
    },
    {
        "name": "Phase 2: Social Service Agencies",
        "agencies": ["hhs", "ed", "ssa", "usaid", "peacecorps"],
        "focus": "Social impact measurement and stakeholder engagement",
        "checkpoint_criteria": [
            "Social value unit (SVU) calculation methodology",
            "Community stakeholder mapping accuracy",
            "Multi-dimensional value translation",
            "Social impact verification mechanisms"
        ]
    },
    {
        "name": "Phase 3: Security and Defense Agencies",
        "agencies": ["dod", "dhs", "cia", "fbi", "nsa"],
        "focus": "Security value optimization and inter-agency coordination",
        "checkpoint_criteria": [
            "Security value measurement methodology",
            "Classified information handling in deal structures",
            "Cross-agency coordination mechanisms",
            "National security value integration"
        ]
    },
    {
        "name": "Phase 4: Regulatory and Administrative Agencies",
        "agencies": ["gsa", "epa", "fcc", "ftc", "nrc"],
        "focus": "Regulatory value and compliance optimization",
        "checkpoint_criteria": [
            "Regulatory value calculation methodology",
            "Multi-stakeholder compliance mechanisms",
            "Public-private partnership structures",
            "Administrative efficiency measurement"
        ]
    },
    {
        "name": "Phase 5: Infrastructure and Technical Agencies",
        "agencies": ["doe", "dot", "nasa", "nsf", "nist"],
        "focus": "Technical value and infrastructure optimization",
        "checkpoint_criteria": [
            "Infrastructure value measurement methodology",
            "Technical innovation accounting",
            "Research and development value capture",
            "Long-term value sustainability"
        ]
    }
]

def run_command(cmd: List[str], verbose: bool = False) -> Tuple[int, str, str]:
    """
    Run a shell command and return exit code, stdout, and stderr.
    
    Args:
        cmd: Command to run as list of arguments
        verbose: Whether to print command output in real-time
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    if verbose:
        print(f"Running command: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout_lines = []
    stderr_lines = []
    
    # Read output in real-time
    for stdout_line in iter(process.stdout.readline, ""):
        if not stdout_line:
            break
        if verbose:
            print(stdout_line.rstrip())
        stdout_lines.append(stdout_line)
    
    for stderr_line in iter(process.stderr.readline, ""):
        if not stderr_line:
            break
        if verbose:
            print(f"ERROR: {stderr_line.rstrip()}")
        stderr_lines.append(stderr_line)
    
    exit_code = process.wait()
    stdout = "".join(stdout_lines)
    stderr = "".join(stderr_lines)
    
    return exit_code, stdout, stderr

def find_agency_files(agency_id: str) -> List[str]:
    """
    Find all documentation files for a specific agency.
    
    Args:
        agency_id: Agency identifier (e.g., 'fed', 'treasury')
        
    Returns:
        List of file paths for the agency
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define patterns to search for agency files
    patterns = [
        os.path.join(base_dir, "enhanced_agency_use_cases", f"{agency_id}_use_case_enhanced.md"),
        os.path.join(base_dir, "enhanced_agency_use_cases", "custom_agency_use_cases", f"{agency_id}_use_case.md"),
        os.path.join(base_dir, "path", "to", "docs", "**", agency_id.upper(), "04_use_cases.md"),
        os.path.join(base_dir, "path", "to", "docs", "**", agency_id, "04_use_cases.md")
    ]
    
    all_files = []
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        all_files.extend(files)
    
    # Filter out files in _ref directory
    all_files = [f for f in all_files if "/_ref/" not in f]
    
    return all_files

def evaluate_checkpoint(phase: Dict[str, Any], agency_files: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Evaluate the checkpoint criteria for a deployment phase.
    
    Args:
        phase: Phase definition dictionary
        agency_files: Dictionary mapping agency IDs to lists of file paths
        
    Returns:
        Evaluation results dictionary
    """
    results = {
        "phase": phase["name"],
        "timestamp": datetime.now().isoformat(),
        "agencies_evaluated": [],
        "criteria_results": {},
        "overall_score": 0.0,
        "recommendations": []
    }
    
    # Initialize criteria results
    for criterion in phase["checkpoint_criteria"]:
        results["criteria_results"][criterion] = {
            "score": 0.0,
            "observations": []
        }
    
    # Evaluate each agency
    for agency_id in phase["agencies"]:
        if agency_id not in agency_files or not agency_files[agency_id]:
            results["agencies_evaluated"].append({
                "agency_id": agency_id,
                "status": "missing",
                "files_found": 0
            })
            continue
        
        # Record agency evaluation
        results["agencies_evaluated"].append({
            "agency_id": agency_id,
            "status": "evaluated",
            "files_found": len(agency_files[agency_id])
        })
        
        # Evaluate implementation against criteria
        for file_path in agency_files[agency_id]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for Moneyball implementation
                if "Moneyball Deal Model" not in content:
                    continue
                
                # Evaluate each criterion
                for criterion in phase["checkpoint_criteria"]:
                    criterion_score = 0.0
                    
                    # Convert criterion to search keywords
                    keywords = re.sub(r'[^\w\s]', '', criterion.lower()).split()
                    
                    # Search for keyword matches in the implementation
                    matches = 0
                    for keyword in keywords:
                        if len(keyword) > 4 and keyword in content.lower():  # Only count significant words
                            matches += 1
                    
                    if matches > 0:
                        # Calculate score based on keyword matches
                        criterion_score = min(1.0, matches / len(keywords))
                        
                        # Record observation
                        results["criteria_results"][criterion]["observations"].append({
                            "agency_id": agency_id,
                            "file": os.path.basename(file_path),
                            "score": criterion_score,
                            "keywords_matched": matches,
                            "total_keywords": len(keywords)
                        })
                        
                        # Update overall criterion score
                        current_score = results["criteria_results"][criterion]["score"]
                        results["criteria_results"][criterion]["score"] = max(current_score, criterion_score)
            
            except Exception as e:
                print(f"Error evaluating {file_path}: {e}")
    
    # Calculate overall score
    total_score = 0.0
    for criterion, result in results["criteria_results"].items():
        total_score += result["score"]
    
    if phase["checkpoint_criteria"]:
        results["overall_score"] = total_score / len(phase["checkpoint_criteria"])
    
    # Generate recommendations
    if results["overall_score"] < 0.3:
        results["recommendations"].append("Critical improvement needed: Implementation shows minimal alignment with criteria")
    elif results["overall_score"] < 0.6:
        results["recommendations"].append("Significant improvement needed: Implementation partially meets criteria")
    elif results["overall_score"] < 0.8:
        results["recommendations"].append("Minor improvements needed: Implementation largely meets criteria with some gaps")
    else:
        results["recommendations"].append("Implementation successfully meets criteria, ready for next phase")
    
    # Add specific recommendations for low-scoring criteria
    for criterion, result in results["criteria_results"].items():
        if result["score"] < 0.5:
            results["recommendations"].append(f"Improve '{criterion}' implementation")
    
    return results

def deploy_phase(
    phase: Dict[str, Any], 
    template_path: str, 
    test_mode: bool = False,
    force: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Deploy the Moneyball Deal Model to agencies in a specific phase.
    
    Args:
        phase: Phase definition dictionary
        template_path: Path to the template file
        test_mode: If True, don't actually write changes
        force: If True, deploy even if previous phase didn't pass checkpoint
        verbose: If True, print verbose output
        
    Returns:
        Deployment results dictionary
    """
    results = {
        "phase": phase["name"],
        "timestamp": datetime.now().isoformat(),
        "agencies": [],
        "summary": {
            "total_agencies": len(phase["agencies"]),
            "successful_agencies": 0,
            "failed_agencies": 0,
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0
        }
    }
    
    # Deploy to each agency in the phase
    for agency_id in phase["agencies"]:
        agency_result = {
            "agency_id": agency_id,
            "files": [],
            "success": False,
            "error": None
        }
        
        try:
            # Run the update script for this agency
            cmd = [
                "python", 
                "update_agency_docs.py",
                "--template", template_path,
                "--agency", agency_id
            ]
            
            if test_mode:
                cmd.append("--test")
            
            exit_code, stdout, stderr = run_command(cmd, verbose=verbose)
            
            if exit_code != 0:
                agency_result["error"] = stderr or "Unknown error"
                results["summary"]["failed_agencies"] += 1
            else:
                agency_result["success"] = True
                results["summary"]["successful_agencies"] += 1
                
                # Parse the output to get file statistics
                files_processed = re.findall(r"Processing ([^\s]+)", stdout)
                agency_result["files"] = files_processed
                
                successful_match = re.search(r"Successful: (\d+)", stdout)
                failed_match = re.search(r"Failed: (\d+)", stdout)
                
                if successful_match:
                    successful_files = int(successful_match.group(1))
                    results["summary"]["successful_files"] += successful_files
                    results["summary"]["total_files"] += successful_files
                
                if failed_match:
                    failed_files = int(failed_match.group(1))
                    results["summary"]["failed_files"] += failed_files
                    results["summary"]["total_files"] += failed_files
        
        except Exception as e:
            agency_result["error"] = str(e)
            results["summary"]["failed_agencies"] += 1
        
        results["agencies"].append(agency_result)
    
    return results

def execute_deployment_plan(
    phases_to_deploy: List[int] = None,
    template_path: str = "agency_deal_template.md",
    test_mode: bool = False,
    force: bool = False,
    verbose: bool = False,
    checkpoint_threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Execute the phased deployment plan for the Moneyball Deal Model.
    
    Args:
        phases_to_deploy: List of phase indices to deploy (1-based). If None, deploy all phases.
        template_path: Path to the template file
        test_mode: If True, don't actually write changes
        force: If True, deploy even if previous phase didn't pass checkpoint
        verbose: If True, print verbose output
        checkpoint_threshold: Minimum score required to pass a checkpoint
        
    Returns:
        Deployment results dictionary
    """
    results = {
        "deployment_start": datetime.now().isoformat(),
        "deployment_end": None,
        "phases": [],
        "test_mode": test_mode,
        "force_mode": force,
        "overall_success": True
    }
    
    # Determine which phases to deploy
    if phases_to_deploy is None:
        phases_to_deploy = list(range(1, len(DEPLOYMENT_PHASES) + 1))
    
    # Ensure the template exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, template_path)
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        results["overall_success"] = False
        results["error"] = f"Template file not found at {template_path}"
        return results
    
    # Process each phase in order
    previous_checkpoint_passed = True
    
    for phase_index in range(1, len(DEPLOYMENT_PHASES) + 1):
        phase = DEPLOYMENT_PHASES[phase_index - 1]
        phase_result = {
            "phase_number": phase_index,
            "phase_name": phase["name"],
            "included_in_deployment": phase_index in phases_to_deploy,
            "deployment_attempted": False,
            "deployment_results": None,
            "checkpoint_results": None,
            "checkpoint_passed": False
        }
        
        # Skip phases not in the deployment list
        if phase_index not in phases_to_deploy:
            results["phases"].append(phase_result)
            continue
        
        print(f"\n{'-' * 80}")
        print(f"Phase {phase_index}: {phase['name']}")
        print(f"Focus: {phase['focus']}")
        print(f"{'-' * 80}\n")
        
        # Check if we should proceed based on previous checkpoint
        if not previous_checkpoint_passed and not force:
            print(f"Previous checkpoint did not pass. Skipping Phase {phase_index}.")
            print(f"Use --force to deploy anyway.")
            phase_result["error"] = "Skipped due to previous checkpoint failure"
            results["phases"].append(phase_result)
            continue
        
        # Find agency files first
        agency_files = {}
        for agency_id in phase["agencies"]:
            files = find_agency_files(agency_id)
            agency_files[agency_id] = files
            print(f"Found {len(files)} files for agency {agency_id}")
        
        # Deploy to this phase
        phase_result["deployment_attempted"] = True
        
        print(f"\nDeploying Moneyball Deal Model to {len(phase['agencies'])} agencies...")
        deployment_results = deploy_phase(
            phase=phase,
            template_path=template_path,
            test_mode=test_mode,
            force=force,
            verbose=verbose
        )
        
        phase_result["deployment_results"] = deployment_results
        
        # Give a little time for file system changes to complete
        time.sleep(1)
        
        # Evaluate checkpoint
        print(f"\nEvaluating checkpoint criteria for Phase {phase_index}...")
        checkpoint_results = evaluate_checkpoint(phase, agency_files)
        phase_result["checkpoint_results"] = checkpoint_results
        
        # Determine if checkpoint passed
        checkpoint_passed = checkpoint_results["overall_score"] >= checkpoint_threshold
        phase_result["checkpoint_passed"] = checkpoint_passed
        previous_checkpoint_passed = checkpoint_passed
        
        print(f"\nCheckpoint evaluation complete.")
        print(f"Overall score: {checkpoint_results['overall_score']:.2f}")
        print(f"Checkpoint {'PASSED' if checkpoint_passed else 'FAILED'} (threshold: {checkpoint_threshold})")
        
        if checkpoint_results["recommendations"]:
            print("\nRecommendations:")
            for rec in checkpoint_results["recommendations"]:
                print(f"- {rec}")
        
        results["phases"].append(phase_result)
        
        # Break if checkpoint failed and not forcing
        if not checkpoint_passed and not force and phase_index < len(DEPLOYMENT_PHASES):
            print(f"\nDeployment halted due to checkpoint failure. Use --force to continue anyway.")
            results["overall_success"] = False
            break
    
    results["deployment_end"] = datetime.now().isoformat()
    
    # Save results to file
    results_path = os.path.join(base_dir, f"moneyball_deployment_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDeployment results saved to: {results_path}")
    
    return results

def main():
    """Main function for the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy Moneyball Deal Model across agency documentation")
    parser.add_argument("--template", default="agency_deal_template.md", help="Path to the template file")
    parser.add_argument("--phases", type=int, nargs="+", help="Specific phases to deploy (1-based indices)")
    parser.add_argument("--threshold", type=float, default=0.7, help="Checkpoint passing threshold (0.0-1.0)")
    parser.add_argument("--test", action="store_true", help="Test mode (don't write changes)")
    parser.add_argument("--force", action="store_true", help="Force deployment even if checkpoints fail")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    args = parser.parse_args()
    
    print(f"Moneyball Deal Model Deployment")
    print(f"{'TEST MODE - ' if args.test else ''}Using template: {args.template}")
    print(f"Checkpoint threshold: {args.threshold}")
    
    if args.phases:
        print(f"Deploying phases: {', '.join(map(str, args.phases))}")
    else:
        print(f"Deploying all phases")
    
    execute_deployment_plan(
        phases_to_deploy=args.phases,
        template_path=args.template,
        test_mode=args.test,
        force=args.force,
        verbose=args.verbose,
        checkpoint_threshold=args.threshold
    )

if __name__ == "__main__":
    main()