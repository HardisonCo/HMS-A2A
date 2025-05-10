#!/usr/bin/env python3
"""
Example script for running benchmarks with the genetic theorem proving system.

This script demonstrates how to:
1. Configure and initialize the genetic theorem proving system
2. Create and run standard benchmark suites
3. Visualize and analyze the results
"""

import os
import sys
import argparse
from pathlib import Path
import json
import matplotlib.pyplot as plt

# Add parent directory to path for importing
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from genetic_theorem_prover.core.base_agent import GeneticTheoremProverAgent, GeneticTraits
from genetic_theorem_prover.evolution.population_manager import PopulationManager
from genetic_theorem_prover.agents.specialized_agents import (
    AxiomAgent, DecompositionAgent, ProofStrategyAgent, 
    CounterexampleAgent, VerificationAgent, GeneralizationAgent
)
from genetic_theorem_prover.evaluation import (
    BenchmarkRunner, StandardBenchmarks, PerformanceVisualizer
)


def create_default_system_config():
    """Create a default system configuration for benchmarking."""
    return {
        "population_size": 50,
        "max_generations": 20,
        "mutation_rate": 0.3,
        "crossover_rate": 0.7,
        "selection_method": "tournament",
        "tournament_size": 5,
        "elitism_count": 2,
        "agent_types": [
            "AxiomAgent", 
            "DecompositionAgent", 
            "ProofStrategyAgent",
            "CounterexampleAgent", 
            "VerificationAgent", 
            "GeneralizationAgent"
        ],
        "agent_type_distribution": {
            "AxiomAgent": 0.2,
            "DecompositionAgent": 0.2,
            "ProofStrategyAgent": 0.2,
            "CounterexampleAgent": 0.1,
            "VerificationAgent": 0.2,
            "GeneralizationAgent": 0.1
        },
        "theorem_decomposition_depth": 3,
        "proof_timeout": 60.0,
        "verification_retries": 2
    }


def initialize_population_manager(config):
    """Initialize a population manager with the given configuration."""
    # Create initial population
    population_size = config["population_size"]
    initial_population = []
    
    # Create agents according to type distribution
    for agent_type, ratio in config["agent_type_distribution"].items():
        count = int(population_size * ratio)
        
        for i in range(count):
            if agent_type == "AxiomAgent":
                agent = AxiomAgent(agent_id=f"axiom_{i}")
            elif agent_type == "DecompositionAgent":
                agent = DecompositionAgent(agent_id=f"decomp_{i}")
            elif agent_type == "ProofStrategyAgent":
                agent = ProofStrategyAgent(agent_id=f"strategy_{i}")
            elif agent_type == "CounterexampleAgent":
                agent = CounterexampleAgent(agent_id=f"counter_{i}")
            elif agent_type == "VerificationAgent":
                agent = VerificationAgent(agent_id=f"verify_{i}")
            elif agent_type == "GeneralizationAgent":
                agent = GeneralizationAgent(agent_id=f"gen_{i}")
            else:
                # Default to base agent
                agent = GeneticTheoremProverAgent(agent_id=f"base_{i}")
            
            initial_population.append(agent)
    
    # Fill remaining slots with base agents if needed
    remaining = population_size - len(initial_population)
    for i in range(remaining):
        agent = GeneticTheoremProverAgent(agent_id=f"base_fill_{i}")
        initial_population.append(agent)
    
    # Create population manager
    manager = PopulationManager(
        initial_population=initial_population,
        mutation_rate=config["mutation_rate"],
        crossover_rate=config["crossover_rate"],
        selection_method=config["selection_method"],
        tournament_size=config["tournament_size"],
        elitism_count=config["elitism_count"]
    )
    
    return manager


def run_basic_benchmark(config, output_dir="./benchmark_results"):
    """Run a basic economic theorem benchmark."""
    print("Running basic economic theorem benchmark...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize benchmark runner
    runner = BenchmarkRunner(output_dir=output_dir)
    
    # Create benchmark suite
    benchmark_suite = StandardBenchmarks.create_basic_economic_benchmarks()
    
    # Initialize population manager
    population_manager = initialize_population_manager(config)
    
    # Run benchmark
    result = runner.run_benchmark(
        suite=benchmark_suite,
        system_config=config,
        population_manager=population_manager,
        max_generations=config["max_generations"]
    )
    
    print(f"Benchmark completed: {result.theorems_proved} of {result.theorems_total} theorems proved "
          f"({result.coverage_percentage:.1%} coverage)")
    
    # Visualize results
    visualizer = PerformanceVisualizer(output_dir=os.path.join(output_dir, "visualizations"))
    visualization_files = visualizer.visualize_benchmark_results(result)
    
    print("Benchmark visualizations saved to:")
    for viz_name, file_path in visualization_files.items():
        print(f"  - {viz_name}: {file_path}")
    
    return result


def run_advanced_benchmark(config, output_dir="./benchmark_results"):
    """Run an advanced economic theorem benchmark."""
    print("Running advanced economic theorem benchmark...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize benchmark runner
    runner = BenchmarkRunner(output_dir=output_dir)
    
    # Create benchmark suite
    benchmark_suite = StandardBenchmarks.create_advanced_economic_benchmarks()
    
    # Initialize population manager
    population_manager = initialize_population_manager(config)
    
    # Run benchmark
    result = runner.run_benchmark(
        suite=benchmark_suite,
        system_config=config,
        population_manager=population_manager,
        max_generations=config["max_generations"]
    )
    
    print(f"Benchmark completed: {result.theorems_proved} of {result.theorems_total} theorems proved "
          f"({result.coverage_percentage:.1%} coverage)")
    
    # Visualize results
    visualizer = PerformanceVisualizer(output_dir=os.path.join(output_dir, "visualizations"))
    visualization_files = visualizer.visualize_benchmark_results(result)
    
    print("Benchmark visualizations saved to:")
    for viz_name, file_path in visualization_files.items():
        print(f"  - {viz_name}: {file_path}")
    
    return result


def run_specialized_benchmark(config, output_dir="./benchmark_results"):
    """Run a specialized international trade theorem benchmark."""
    print("Running specialized international trade theorem benchmark...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize benchmark runner
    runner = BenchmarkRunner(output_dir=output_dir)
    
    # Create benchmark suite
    benchmark_suite = StandardBenchmarks.create_specialized_international_trade_benchmarks()
    
    # Initialize population manager
    population_manager = initialize_population_manager(config)
    
    # Run benchmark
    result = runner.run_benchmark(
        suite=benchmark_suite,
        system_config=config,
        population_manager=population_manager,
        max_generations=config["max_generations"]
    )
    
    print(f"Benchmark completed: {result.theorems_proved} of {result.theorems_total} theorems proved "
          f"({result.coverage_percentage:.1%} coverage)")
    
    # Visualize results
    visualizer = PerformanceVisualizer(output_dir=os.path.join(output_dir, "visualizations"))
    visualization_files = visualizer.visualize_benchmark_results(result)
    
    print("Benchmark visualizations saved to:")
    for viz_name, file_path in visualization_files.items():
        print(f"  - {viz_name}: {file_path}")
    
    return result


def compare_configurations(config_variations, output_dir="./benchmark_results"):
    """Run benchmarks with different configurations and compare results."""
    print(f"Comparing {len(config_variations)} different system configurations...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize benchmark runner
    runner = BenchmarkRunner(output_dir=output_dir)
    
    # Create benchmark suite (use basic suite for comparison)
    benchmark_suite = StandardBenchmarks.create_basic_economic_benchmarks()
    
    results = []
    
    # Run benchmark for each configuration
    for i, config in enumerate(config_variations):
        print(f"\nRunning configuration {i+1}/{len(config_variations)}...")
        
        # Initialize population manager with this configuration
        population_manager = initialize_population_manager(config)
        
        # Run benchmark
        result = runner.run_benchmark(
            suite=benchmark_suite,
            system_config=config,
            population_manager=population_manager,
            max_generations=config["max_generations"]
        )
        
        results.append(result)
        
        print(f"Configuration {i+1} completed: {result.theorems_proved} of {result.theorems_total} theorems proved "
              f"({result.coverage_percentage:.1%} coverage)")
    
    # Visualize comparison
    visualizer = PerformanceVisualizer(output_dir=os.path.join(output_dir, "comparisons"))
    comparison_files = visualizer.visualize_benchmark_comparison(results)
    
    print("\nComparison visualizations saved to:")
    for viz_name, file_path in comparison_files.items():
        print(f"  - {viz_name}: {file_path}")
    
    return results


def main():
    """Main function for running benchmarks."""
    parser = argparse.ArgumentParser(description="Run genetic theorem proving benchmarks")
    parser.add_argument("--output-dir", default="./benchmark_results", 
                        help="Directory to store benchmark results")
    parser.add_argument("--config", default=None,
                        help="Path to JSON configuration file")
    parser.add_argument("--benchmark", choices=["basic", "advanced", "specialized", "compare", "all"],
                        default="basic", help="Benchmark type to run")
    parser.add_argument("--population-size", type=int, default=50,
                        help="Population size for genetic algorithm")
    parser.add_argument("--max-generations", type=int, default=20,
                        help="Maximum generations to run")
    parser.add_argument("--mutation-rate", type=float, default=0.3,
                        help="Mutation rate for genetic algorithm")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = create_default_system_config()
        
        # Override with command line arguments
        config["population_size"] = args.population_size
        config["max_generations"] = args.max_generations
        config["mutation_rate"] = args.mutation_rate
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run selected benchmark
    if args.benchmark == "basic" or args.benchmark == "all":
        basic_result = run_basic_benchmark(config, args.output_dir)
        
    if args.benchmark == "advanced" or args.benchmark == "all":
        advanced_result = run_advanced_benchmark(config, args.output_dir)
        
    if args.benchmark == "specialized" or args.benchmark == "all":
        specialized_result = run_specialized_benchmark(config, args.output_dir)
        
    if args.benchmark == "compare" or args.benchmark == "all":
        # Create configuration variations
        config_variations = [
            # Base configuration
            config.copy(),
            
            # Larger population
            {**config.copy(), "population_size": config["population_size"] * 2},
            
            # Higher mutation rate
            {**config.copy(), "mutation_rate": min(0.8, config["mutation_rate"] * 2)},
            
            # Different selection method
            {**config.copy(), "selection_method": "roulette"},
            
            # Different agent type distribution
            {**config.copy(), "agent_type_distribution": {
                "AxiomAgent": 0.3,
                "DecompositionAgent": 0.3,
                "ProofStrategyAgent": 0.1,
                "CounterexampleAgent": 0.1,
                "VerificationAgent": 0.1,
                "GeneralizationAgent": 0.1
            }}
        ]
        
        comparison_results = compare_configurations(config_variations, args.output_dir)
    
    print("\nAll benchmarks completed successfully.")


if __name__ == "__main__":
    main()