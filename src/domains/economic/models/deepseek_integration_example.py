"""
Example script demonstrating integration of the Lean 4 economic foundations
with DeepSeek-Prover-V2.

This script shows how to load economic theorems from Lean files,
send them to DeepSeek-Prover-V2 for proving, and validate the results.
"""

import os
import sys
import json
import re
from typing import Dict, List, Optional, Any

# Assuming these modules are available in the HMS-A2A component
# Add appropriate imports for your environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genetic_theorem_prover.core.deepseek_prover import (
    DeepSeekProverClient, 
    ProverRequest, 
    ProverConfig, 
    ProverMode
)

def extract_theorem_from_lean(lean_file: str, theorem_name: str) -> Dict[str, Any]:
    """
    Extract a theorem and its assumptions from a Lean file.
    
    Args:
        lean_file: Path to the Lean file
        theorem_name: Name of the theorem to extract
        
    Returns:
        Dictionary with theorem details
    """
    with open(lean_file, "r") as f:
        content = f.read()
    
    # Extract theorem using regex (a basic approach)
    theorem_pattern = rf"/--.*?--/\s*theorem\s+{theorem_name}\s*(?:\{{.*?\}})?\s*\(([^)]*)\)\s*:\s*([^:=]*):=\s*begin"
    match = re.search(theorem_pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError(f"Theorem {theorem_name} not found in {lean_file}")
    
    # Extract parameters and their types
    params_str = match.group(1)
    formal_expression = match.group(2).strip()
    
    # Parse parameters and assumptions
    variables = {}
    assumptions = []
    
    # Simple parsing for demonstration purposes
    # In a real implementation, use a proper Lean parser
    param_lines = [p.strip() for p in params_str.split("\n") if p.strip()]
    for line in param_lines:
        if ":" in line:
            # Parameter with type
            param_name, param_type = line.split(":", 1)
            variables[param_name.strip()] = param_type.strip()
        elif line.startswith("h") and ":" in line:
            # Assumption
            _, assumption = line.split(":", 1)
            assumptions.append(assumption.strip())
    
    return {
        "theorem_id": theorem_name,
        "formal_expression": formal_expression,
        "variables": variables,
        "assumptions": assumptions
    }

def prove_theorem_with_deepseek(theorem_spec: Dict[str, Any], config: ProverConfig) -> Any:
    """
    Send a theorem to DeepSeek-Prover-V2 for proving.
    
    Args:
        theorem_spec: Theorem specification extracted from Lean
        config: ProverConfig with API details
        
    Returns:
        ProverResponse with the proof result
    """
    client = DeepSeekProverClient(config)
    
    request = ProverRequest(
        theorem_id=theorem_spec["theorem_id"],
        formal_expression=theorem_spec["formal_expression"],
        assumptions=theorem_spec["assumptions"],
        variables=theorem_spec["variables"],
        config=config
    )
    
    return client.prove_theorem(request)

def main():
    # Configuration for DeepSeek-Prover-V2
    config = ProverConfig(
        mode=ProverMode.COT,  # Use Chain of Thought mode
        temperature=0.1,
        max_tokens=4096,
        timeout_seconds=300
    )
    
    # If API keys are available in environment
    api_url = os.environ.get("DEEPSEEK_PROVER_API_URL")
    api_key = os.environ.get("DEEPSEEK_PROVER_API_KEY")
    
    if api_url and api_key:
        config.api_url = api_url
        config.api_key = api_key
        print(f"Using DeepSeek-Prover-V2 API at {api_url}")
    else:
        print("Using simulated prover (no API credentials found)")
    
    # Directory containing Lean files
    lean_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Example: Prove the SPS weights sum theorem
    lean_file = os.path.join(lean_dir, "EconomicFoundations", "DeepSeekExamples.lean")
    theorem_name = "sps_weights_sum_to_one"
    
    print(f"Extracting theorem '{theorem_name}' from {lean_file}")
    theorem_spec = extract_theorem_from_lean(lean_file, theorem_name)
    
    print(f"Sending theorem to DeepSeek-Prover-V2:")
    print(json.dumps(theorem_spec, indent=2))
    
    print("\nProving theorem...")
    response = prove_theorem_with_deepseek(theorem_spec, config)
    
    print(f"\nProof successful: {response.success}")
    if response.success:
        print(f"Proof steps: {len(response.proof_steps)}")
        print("\nProof:")
        print(response.proof)
    else:
        print(f"Error: {response.error}")

if __name__ == "__main__":
    main()