"""
Python FFI Bridge for Theorem Prover

This module provides the Python Foreign Function Interface (FFI) bridge for the 
Economic Theorem Prover, allowing Rust components to interact with the Python-based
theorem proving capabilities.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
import traceback
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the core directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(current_dir, "core")
sys.path.append(core_dir)

# Now import from core modules
from lean_theorem_extractor import LeanTheoremExtractor, create_theorem_request
from deepseek_config import DeepSeekConfig, ProverMode
from deepseek_prover import DeepSeekProverClient, ProverConfig, ProverRequest, ProverResponse


class TheoremProverFFI:
    """
    FFI bridge for the Economic Theorem Prover.
    
    This class provides an interface for Rust components to use the Python-based
    theorem proving capabilities through FFI.
    """
    
    def __init__(self, lean_lib_path: Optional[str] = None):
        """
        Initialize the FFI bridge.
        
        Args:
            lean_lib_path: Path to the Lean library
        """
        # Use environment variable or default path
        self.lean_lib_path = lean_lib_path or os.environ.get(
            'LEAN_LIB_PATH', 
            os.path.join(os.path.dirname(os.path.dirname(current_dir)), "hms/lean_libs")
        )
        logger.info(f"Using Lean library path: {self.lean_lib_path}")
        
        # Initialize extractor and default prover client
        self.extractor = LeanTheoremExtractor(self.lean_lib_path)
        self._init_prover_client()
    
    def _init_prover_client(self):
        """Initialize the prover client based on environment settings."""
        # Check for API environment variables
        api_url = os.environ.get("DEEPSEEK_PROVER_API_URL")
        api_key = os.environ.get("DEEPSEEK_PROVER_API_KEY")
        
        if api_url and api_key:
            # Use remote API
            self.prover_config = ProverConfig(
                mode=ProverMode.DEFAULT,
                api_url=api_url,
                api_key=api_key
            )
        else:
            # Use simulated client (in a real implementation, this would use local model)
            model_path = os.environ.get("DEEPSEEK_MODEL_PATH", "simulated")
            self.prover_config = ProverConfig(
                mode=ProverMode.DEFAULT,
                model_path=model_path
            )
        
        self.prover_client = DeepSeekProverClient(self.prover_config)
    
    def list_theorems(self) -> List[Dict[str, Any]]:
        """
        List all available theorems in the Lean library.
        
        Returns:
            List of theorem information dictionaries
        """
        try:
            libraries = self.extractor.extract_theorems_from_directory()
            
            theorems = []
            for file_path, library in libraries.items():
                for theorem_id, theorem in library.theorems.items():
                    theorems.append({
                        "theorem_id": theorem_id,
                        "namespace": theorem.namespace,
                        "file_path": theorem.file_path,
                        "line_number": theorem.line_number,
                        "has_proof_outline": theorem.proof_outline is not None
                    })
            
            return theorems
        except Exception as e:
            logger.error(f"Error listing theorems: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def get_theorem_details(self, theorem_id: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a theorem.
        
        Args:
            theorem_id: ID of the theorem
            namespace: Optional namespace to search in
            
        Returns:
            Dictionary with theorem details
        """
        try:
            theorem = self.extractor.find_theorem(theorem_id, namespace)
            
            if theorem is None:
                return {"error": f"Theorem {theorem_id} not found"}
            
            return {
                "theorem_id": theorem.theorem_id,
                "namespace": theorem.namespace,
                "formal_expression": theorem.formal_expression,
                "variables": [{"name": v.name, "type": v.type_, "implicit": v.implicit} 
                             for v in theorem.variables],
                "hypotheses": [{"name": h.name, "expression": h.expression} 
                              for h in theorem.hypotheses],
                "proof_outline": theorem.proof_outline,
                "file_path": theorem.file_path,
                "line_number": theorem.line_number
            }
        except Exception as e:
            logger.error(f"Error getting theorem details: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def prove_theorem(self, theorem_id: str, config: Optional[Dict[str, Any]] = None, 
                     namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Prove a theorem using the DeepSeek-Prover-V2.
        
        Args:
            theorem_id: ID of the theorem to prove
            config: Optional configuration for the prover
            namespace: Optional namespace to search in
            
        Returns:
            Dictionary with proof results
        """
        try:
            # Find the theorem
            theorem = self.extractor.find_theorem(theorem_id, namespace)
            
            if theorem is None:
                return {"error": f"Theorem {theorem_id} not found"}
            
            # Create request dictionary
            request_dict = create_theorem_request(theorem)
            
            # Create config
            if config:
                prover_config = ProverConfig(**config)
            else:
                prover_config = self.prover_config
            
            # Create request
            request = ProverRequest(
                theorem_id=request_dict["theorem_id"],
                formal_expression=request_dict["formal_expression"],
                assumptions=request_dict["assumptions"],
                variables=request_dict["variables"],
                config=prover_config,
                context=request_dict.get("context"),
            )
            
            # Get proof
            response = self.prover_client.prove_theorem(request)
            
            # Convert response to dictionary
            return {
                "task_id": response.task_id,
                "theorem_id": response.theorem_id,
                "success": response.success,
                "proof": response.proof,
                "proof_steps": response.proof_steps,
                "verification_result": response.verification_result,
                "error": response.error,
                "duration_seconds": response.duration_seconds,
                "tokens_used": response.tokens_used,
                "mode": response.mode.value
            }
        except Exception as e:
            logger.error(f"Error proving theorem: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def verify_proof(self, theorem_id: str, proof: str, 
                    namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify a proof using Lean.
        
        Args:
            theorem_id: ID of the theorem
            proof: Proof to verify
            namespace: Optional namespace to search in
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Find the theorem
            theorem = self.extractor.find_theorem(theorem_id, namespace)
            
            if theorem is None:
                return {"error": f"Theorem {theorem_id} not found"}
            
            # Verify the proof
            verification_result = self.prover_client.verify_proof(
                theorem_id=theorem_id,
                proof=proof
            )
            
            return verification_result
        except Exception as e:
            logger.error(f"Error verifying proof: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def get_genetic_config(self, theorem_id: str, complexity: str = "simple") -> Dict[str, Any]:
        """
        Get a genetic algorithm configuration for a theorem.
        
        Args:
            theorem_id: ID of the theorem
            complexity: Complexity level (simple, complex)
            
        Returns:
            Dictionary with configuration
        """
        try:
            # Import here to avoid circular imports
            from deepseek_config import get_config_for_theorem
            
            # Get config
            config = get_config_for_theorem(theorem_id, complexity)
            
            # Convert to dictionary
            return config.to_dict()
        except Exception as e:
            logger.error(f"Error getting genetic config: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def mutate_config(self, config_dict: Dict[str, Any], 
                     mutation_rate: float = 0.1) -> Dict[str, Any]:
        """
        Mutate a configuration for genetic algorithm evolution.
        
        Args:
            config_dict: Configuration dictionary
            mutation_rate: Mutation rate
            
        Returns:
            Mutated configuration dictionary
        """
        try:
            # Convert to config object
            config = DeepSeekConfig.from_dict(config_dict)
            
            # Mutate
            mutated = config.mutate(mutation_rate)
            
            # Convert back to dictionary
            return mutated.to_dict()
        except Exception as e:
            logger.error(f"Error mutating config: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def update_config_fitness(self, config_dict: Dict[str, Any], 
                             fitness: float) -> Dict[str, Any]:
        """
        Update fitness history for a configuration.
        
        Args:
            config_dict: Configuration dictionary
            fitness: Fitness value
            
        Returns:
            Updated configuration dictionary
        """
        try:
            # Convert to config object
            config = DeepSeekConfig.from_dict(config_dict)
            
            # Update fitness
            config.update_fitness(fitness)
            
            # Convert back to dictionary (note: fitness_history is not included)
            result = config.to_dict()
            result["avg_fitness"] = config.get_avg_fitness()
            result["fitness_trend"] = config.get_fitness_trend()
            
            return result
        except Exception as e:
            logger.error(f"Error updating config fitness: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}


# Create a function to be called from FFI
def ffi_handle_request(request_json: str) -> str:
    """
    Handle a JSON request from Rust FFI.
    
    Args:
        request_json: JSON string with request
        
    Returns:
        JSON string with response
    """
    try:
        # Parse request
        request = json.loads(request_json)
        
        # Get action
        action = request.get("action")
        if not action:
            return json.dumps({"error": "No action specified"})
        
        # Initialize FFI bridge if not already done
        lean_lib_path = request.get("lean_lib_path")
        ffi_bridge = TheoremProverFFI(lean_lib_path)
        
        # Handle action
        if action == "list_theorems":
            result = ffi_bridge.list_theorems()
        elif action == "get_theorem_details":
            theorem_id = request.get("theorem_id")
            namespace = request.get("namespace")
            result = ffi_bridge.get_theorem_details(theorem_id, namespace)
        elif action == "prove_theorem":
            theorem_id = request.get("theorem_id")
            config = request.get("config")
            namespace = request.get("namespace")
            result = ffi_bridge.prove_theorem(theorem_id, config, namespace)
        elif action == "verify_proof":
            theorem_id = request.get("theorem_id")
            proof = request.get("proof")
            namespace = request.get("namespace")
            result = ffi_bridge.verify_proof(theorem_id, proof, namespace)
        elif action == "get_genetic_config":
            theorem_id = request.get("theorem_id")
            complexity = request.get("complexity", "simple")
            result = ffi_bridge.get_genetic_config(theorem_id, complexity)
        elif action == "mutate_config":
            config_dict = request.get("config")
            mutation_rate = request.get("mutation_rate", 0.1)
            result = ffi_bridge.mutate_config(config_dict, mutation_rate)
        elif action == "update_config_fitness":
            config_dict = request.get("config")
            fitness = request.get("fitness")
            result = ffi_bridge.update_config_fitness(config_dict, fitness)
        else:
            result = {"error": f"Unknown action: {action}"}
        
        # Return JSON response
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})


# Test function to run from command line
def main():
    """Run a test of the FFI bridge."""
    # Initialize FFI bridge
    ffi_bridge = TheoremProverFFI()
    
    # List theorems
    theorems = ffi_bridge.list_theorems()
    print(f"Found {len(theorems)} theorems:")
    for i, theorem in enumerate(theorems[:5]):  # Show first 5
        print(f"  {i+1}. {theorem['theorem_id']} (namespace: {theorem['namespace']})")
    
    if theorems:
        # Get details for the first theorem
        theorem_id = theorems[0]["theorem_id"]
        details = ffi_bridge.get_theorem_details(theorem_id)
        print(f"\nDetails for {theorem_id}:")
        print(f"  Expression: {details['formal_expression']}")
        print(f"  Hypotheses: {len(details['hypotheses'])}")
        if details.get("proof_outline"):
            print(f"  Proof outline: {details['proof_outline'][:100]}...")
        
        # Get genetic config
        config = ffi_bridge.get_genetic_config(theorem_id)
        print(f"\nGenetic config for {theorem_id}:")
        print(f"  Mode: {config['mode']}")
        print(f"  Temperature: {config['temperature']}")
        
        # Mutate config
        mutated = ffi_bridge.mutate_config(config, 0.5)
        print(f"\nMutated config:")
        print(f"  Mode: {mutated['mode']}")
        print(f"  Temperature: {mutated['temperature']}")
        
        # Test FFI request handler
        request = {
            "action": "get_theorem_details",
            "theorem_id": theorem_id
        }
        response = ffi_handle_request(json.dumps(request))
        print(f"\nFFI response for {theorem_id}:")
        print(f"  {response[:100]}...")


if __name__ == "__main__":
    main()