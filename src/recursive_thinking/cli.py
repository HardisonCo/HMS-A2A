#!/usr/bin/env python3
"""
Command-line interface for the Hybrid Genetic-Recursive System.

This CLI provides access to the hybrid genetic algorithm and recursive thinking
system for solution evolution and refinement.
"""

import os
import sys
import json
import argparse
from typing import List, Dict
from .genetic_adapter import GeneticRecursiveAdapter

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Hybrid Genetic-Recursive Thinking System"
    )
    
    parser.add_argument(
        "--input", "-i", 
        type=str, 
        help="Input JSON file with candidates, constraints, and fitness function"
    )
    
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default="hybrid_solution.json", 
        help="Output file to write results to"
    )
    
    parser.add_argument(
        "--rounds", "-r", 
        type=int, 
        default=2, 
        help="Number of hybrid evolution rounds to perform"
    )
    
    parser.add_argument(
        "--genetic-engine", "-g", 
        type=str, 
        help="Path to the genetic engine executable or script"
    )
    
    parser.add_argument(
        "--api-key", "-k", 
        type=str, 
        help="OpenRouter API key for recursive thinking (defaults to OPENROUTER_API_KEY env var)"
    )
    
    parser.add_argument(
        "--quiet", "-q", 
        action="store_true", 
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    # Check for input file
    if not args.input:
        parser.error("Please provide an input file with --input")
        return 1
    
    try:
        # Load input data
        with open(args.input, "r") as f:
            input_data = json.load(f)
        
        # Validate input data
        if "candidates" not in input_data:
            raise ValueError("Input must contain 'candidates' list")
        if "fitness_function" not in input_data:
            raise ValueError("Input must contain 'fitness_function'")
        
        # Setup adapter
        api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
        adapter = GeneticRecursiveAdapter(
            api_key=api_key,
            genetic_engine_path=args.genetic_engine
        )
        
        # Run hybrid evolution
        constraints = input_data.get("constraints", [])
        verbose = not args.quiet
        
        result = adapter.hybrid_evolve(
            input_data["candidates"],
            constraints,
            input_data["fitness_function"],
            recursion_rounds=args.rounds,
            verbose=verbose
        )
        
        # Write output
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        
        if verbose:
            print(f"\nResults written to {args.output}")
            print(f"Final solution fitness: {result['fitness']}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())