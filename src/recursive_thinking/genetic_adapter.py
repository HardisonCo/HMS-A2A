"""
Genetic Repair Engine Adapter for Recursive Thinking

This module provides an adapter to integrate recursive thinking capabilities
with the genetic repair engine.
"""

import os
import json
import subprocess
from typing import List, Dict, Any, Optional
from .enhanced_recursive_thinking import EnhancedRecursiveThinkingChat

class GeneticRecursiveAdapter:
    """
    An adapter class that integrates the genetic repair engine with
    recursive thinking capabilities.
    """
    
    def __init__(self, api_key: str = None, genetic_engine_path: str = None):
        """
        Initialize the adapter.
        
        Args:
            api_key: OpenRouter API key for recursive thinking
            genetic_engine_path: Path to the genetic engine executable or script
        """
        self.recursive_thinking = EnhancedRecursiveThinkingChat(api_key=api_key)
        self.genetic_engine_path = genetic_engine_path or "genetic_repair_engine"
    
    def _call_genetic_engine(self, candidates: List[str], constraints: List[Dict], fitness_function: str) -> Dict:
        """
        Call the genetic repair engine with the given parameters.
        
        Args:
            candidates: List of candidate solutions
            constraints: List of constraints
            fitness_function: The fitness function to use
            
        Returns:
            The genetic engine results
        """
        # Prepare input data
        input_data = {
            "candidates": candidates,
            "constraints": constraints,
            "fitness_function": fitness_function
        }
        
        # Write input to a temporary file
        input_file = "genetic_input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)
        
        # Call the genetic engine
        result = subprocess.run(
            [self.genetic_engine_path, "--input", input_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Genetic engine failed: {result.stderr}")
        
        # Parse the output
        return json.loads(result.stdout)
    
    def hybrid_evolve(
        self,
        candidates: List[str],
        constraints: List[Dict],
        fitness_function: str,
        recursion_rounds: int = 1,
        verbose: bool = True
    ) -> Dict:
        """
        Evolve solutions using both genetic algorithms and recursive thinking.
        
        The process works as follows:
        1. Run the genetic algorithm to produce an initial solution
        2. Refine the genetic solution using recursive thinking
        3. Feed the refined solution back into the genetic algorithm
        4. Repeat for the specified number of rounds
        
        Args:
            candidates: Initial candidate solutions
            constraints: Constraints for the genetic algorithm
            fitness_function: The fitness function to use
            recursion_rounds: Number of hybrid rounds to perform
            verbose: Whether to print intermediate results
            
        Returns:
            A dictionary containing the final solution and metadata
        """
        current_candidates = candidates.copy()
        results_history = []
        
        for round_num in range(1, recursion_rounds + 1):
            if verbose:
                print(f"\nHybrid Evolution Round {round_num}/{recursion_rounds}")
                print(f"Running genetic algorithm with {len(current_candidates)} candidates...")
            
            # Run genetic algorithm
            genetic_result = self._call_genetic_engine(
                current_candidates, 
                constraints, 
                fitness_function
            )
            
            best_solution = genetic_result["solution"]
            best_fitness = genetic_result["fitness"]
            
            if verbose:
                print(f"Genetic algorithm produced solution with fitness: {best_fitness}")
                print(f"Solution: {best_solution[:100]}..." if len(best_solution) > 100 else f"Solution: {best_solution}")
            
            # Use recursive thinking to refine the solution
            if verbose:
                print("\nRefining solution with recursive thinking...")
            
            constraint_prompt = ""
            if constraints:
                constraint_prompt = "Consider these constraints:\n" + "\n".join([
                    f"- {c['type']}: {c['value']}" for c in constraints
                ])
            
            refinement_prompt = f"""
            Refine and improve the following solution:
            
            {best_solution}
            
            {constraint_prompt}
            
            Your refined solution should maintain or improve the fitness of the original solution.
            Be creative but also precise in your refinements.
            """
            
            thinking_result = self.recursive_thinking.think_and_respond(refinement_prompt, verbose)
            refined_solution = thinking_result["final_response"]
            
            if verbose:
                print(f"Refined solution: {refined_solution[:100]}..." if len(refined_solution) > 100 else f"Refined solution: {refined_solution}")
            
            # Save results for this round
            results_history.append({
                "round": round_num,
                "genetic_solution": best_solution,
                "genetic_fitness": best_fitness,
                "refined_solution": refined_solution,
                "thinking_history": thinking_result["thinking_history"]
            })
            
            # Update candidates for next round
            current_candidates = [refined_solution]
            if best_solution != refined_solution:
                current_candidates.append(best_solution)
            
            # Add some diversity for the next round
            if len(current_candidates) < 5 and len(candidates) > 0:
                num_to_add = min(3, len(candidates))
                for i in range(num_to_add):
                    current_candidates.append(candidates[i % len(candidates)])
        
        # Run final genetic algorithm on the refined solution
        final_genetic_result = self._call_genetic_engine(
            current_candidates, 
            constraints, 
            fitness_function
        )
        
        return {
            "solution": final_genetic_result["solution"],
            "fitness": final_genetic_result["fitness"],
            "history": results_history,
            "rounds": recursion_rounds
        }
    
    def evaluate_solutions(self, solutions: List[str], fitness_function: str) -> List[Dict]:
        """
        Evaluate multiple solutions using the fitness function.
        
        Args:
            solutions: List of solutions to evaluate
            fitness_function: The fitness function to use
            
        Returns:
            List of solutions with their fitness scores
        """
        # Prepare input data
        input_data = {
            "candidates": solutions,
            "evaluate_only": True,
            "fitness_function": fitness_function
        }
        
        # Write input to a temporary file
        input_file = "genetic_evaluate_input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)
        
        # Call the genetic engine
        result = subprocess.run(
            [self.genetic_engine_path, "--input", input_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Genetic engine evaluation failed: {result.stderr}")
        
        # Parse the output
        results = json.loads(result.stdout)
        
        return [
            {"solution": solution, "fitness": fitness}
            for solution, fitness in zip(solutions, results["fitness_scores"])
        ]

# Example usage when run as a script
if __name__ == "__main__":
    api_key = os.environ.get("OPENROUTER_API_KEY")
    adapter = GeneticRecursiveAdapter(api_key=api_key)
    
    # Example candidates
    candidates = [
        "function detectError() { if (x > 10) { return true; } }",
        "function detectError() { if (x > 10 && y < 5) { return true; } }",
        "function detectError() { return x > 10; }"
    ]
    
    # Example constraints
    constraints = [
        {"type": "must_contain", "value": "function detectError"},
        {"type": "must_contain", "value": "return"}
    ]
    
    # Example fitness function
    fitness_function = "error_detection_accuracy"
    
    result = adapter.hybrid_evolve(candidates, constraints, fitness_function, recursion_rounds=2)
    print("\nFinal hybrid solution:")
    print(f"Solution: {result['solution']}")
    print(f"Fitness: {result['fitness']}")