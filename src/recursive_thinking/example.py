#!/usr/bin/env python3
"""
Example demonstrating the use of the recursive thinking module
and genetic adapter.
"""

import os
import json
from enhanced_recursive_thinking import EnhancedRecursiveThinkingChat
from genetic_adapter import GeneticRecursiveAdapter

def main():
    """Main function to demonstrate the recursive thinking capabilities."""
    print("Recursive Thinking Module Example")
    print("--------------------------------")
    
    # Get API key from environment
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        print("Please set it and try again.")
        return 1
    
    # Create recursive thinking chat instance
    thinking_chat = EnhancedRecursiveThinkingChat(api_key=api_key)
    
    # Create genetic adapter
    adapter = GeneticRecursiveAdapter(api_key=api_key)
    
    # Example 1: Using recursive thinking directly
    print("\nExample 1: Recursive Thinking")
    print("----------------------------")
    prompt = """
    Design a function that detects system issues including:
    - Error conditions
    - Performance problems
    - Resource constraints
    
    The function should be efficient and well-documented.
    """
    
    print("Thinking about:", prompt.strip())
    result = thinking_chat.think_and_respond(prompt, verbose=True)
    
    print("\nFinal Response:")
    print(result["final_response"])
    
    # Example 2: Using genetic adapter
    print("\nExample 2: Hybrid Genetic-Recursive Approach")
    print("----------------------------------------")
    
    # Example candidates
    candidates = [
        """function detectSystemIssues(system) {
          if (system.status === 'error') {
            return true;
          }
          return false;
        }""",
        
        """function detectSystemIssues(system) {
          return system.status === 'error' || system.errorCount > 0;
        }""",
        
        """function detectSystemIssues(system) {
          if (system.status === 'error') {
            return true;
          } else if (system.errorCount > 0) {
            return true;
          }
          return false;
        }"""
    ]
    
    # Example constraints
    constraints = [
        {"type": "must_contain", "value": "function detectSystemIssues"},
        {"type": "must_contain", "value": "return"}
    ]
    
    # Since we can't directly use JavaScript fitness functions,
    # we'll create a simulation for demonstration purposes
    print("Creating mock genetic engine process...")
    
    # Create temporary input file for demonstration
    input_file = "mock_genetic_input.json"
    input_data = {
        "candidates": candidates,
        "constraints": constraints,
        "fitness_function": "system_issue_detection"
    }
    
    with open(input_file, "w") as f:
        json.dump(input_data, f, indent=2)
    
    print(f"Input data written to {input_file}")
    print("In a real scenario, you would run this with the genetic engine.")
    
    # Demonstrate solution refinement directly
    print("\nDemonstrating solution refinement with recursive thinking:")
    solution = candidates[1]  # Use one of the candidates
    
    refined = thinking_chat.refine_solution(
        solution,
        constraints=[{"type": "Description", "value": c["value"]} for c in constraints],
        verbose=True
    )
    
    print("\nOriginal Solution:")
    print(solution)
    print("\nRefined Solution:")
    print(refined)
    
    return 0

if __name__ == "__main__":
    exit(main())