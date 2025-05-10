#!/usr/bin/env python3
"""
Example script for creating and running custom benchmarks with the genetic theorem proving system.

This script demonstrates how to:
1. Define custom theorem benchmarks
2. Create a custom benchmark suite
3. Run the benchmark and analyze results
"""

import os
import sys
import argparse
from pathlib import Path
import json

# Add parent directory to path for importing
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from genetic_theorem_prover.core.base_agent import GeneticTheoremProverAgent
from genetic_theorem_prover.evolution.population_manager import PopulationManager
from genetic_theorem_prover.agents.specialized_agents import (
    AxiomAgent, DecompositionAgent, ProofStrategyAgent, 
    CounterexampleAgent, VerificationAgent, GeneralizationAgent
)
from genetic_theorem_prover.evaluation import (
    TheoremBenchmark, BenchmarkSuite, BenchmarkRunner, PerformanceVisualizer
)


def create_custom_benchmark_suite():
    """Create a custom benchmark suite for monetary theory."""
    suite = BenchmarkSuite(
        "monetary_theory",
        "Custom benchmark suite for monetary economic theory theorems"
    )
    
    # Basic money demand theorem
    suite.add_theorem(
        TheoremBenchmark(
            id="money_demand_theory",
            statement="The demand for money is a function of income and interest rates, "
                     "where demand increases with income and decreases with interest rates.",
            area="monetary_economics",
            complexity=0.5,
            dependencies=[]
        ),
        categories=["monetary_theory", "money_demand"]
    )
    
    # Quantity theory of money
    suite.add_theorem(
        TheoremBenchmark(
            id="quantity_theory_of_money",
            statement="In the long run, an increase in the money supply leads to a proportional "
                     "increase in the price level, assuming velocity and output are constant.",
            area="monetary_economics",
            complexity=0.6,
            dependencies=["money_neutrality"]
        ),
        categories=["monetary_theory", "price_levels"]
    )
    
    # Money neutrality
    suite.add_theorem(
        TheoremBenchmark(
            id="money_neutrality",
            statement="In the long run, changes in the money supply affect nominal variables "
                     "but do not affect real variables such as output or unemployment.",
            area="monetary_economics",
            complexity=0.7,
            dependencies=[]
        ),
        categories=["monetary_theory", "neutrality"]
    )
    
    # Fisher equation
    suite.add_theorem(
        TheoremBenchmark(
            id="fisher_equation",
            statement="The nominal interest rate equals the real interest rate plus "
                     "the expected inflation rate.",
            area="monetary_economics",
            complexity=0.4,
            dependencies=[]
        ),
        categories=["monetary_theory", "interest_rates"]
    )
    
    # Superneutrality of money
    suite.add_theorem(
        TheoremBenchmark(
            id="money_superneutrality",
            statement="Changes in the growth rate of the money supply do not affect real "
                     "variables in the long run.",
            area="monetary_economics",
            complexity=0.8,
            dependencies=["money_neutrality"]
        ),
        categories=["monetary_theory", "neutrality"]
    )
    
    # Optimum quantity of money
    suite.add_theorem(
        TheoremBenchmark(
            id="optimum_quantity_of_money",
            statement="The optimal quantity of money is achieved when the nominal interest "
                     "rate is zero, which requires deflation at the rate of time preference.",
            area="monetary_economics",
            complexity=0.9,
            dependencies=["fisher_equation"]
        ),
        categories=["monetary_theory", "optimal_policy"]
    )
    
    # Money multiplier
    suite.add_theorem(
        TheoremBenchmark(
            id="money_multiplier",
            statement="The money multiplier is the ratio of the money supply to the monetary base, "
                     "and is determined by the reserve ratio and the currency-deposit ratio.",
            area="banking",
            complexity=0.5,
            dependencies=[]
        ),
        categories=["monetary_theory", "banking"]
    )
    
    # Tobin effect
    suite.add_theorem(
        TheoremBenchmark(
            id="tobin_effect",
            statement="Higher inflation leads to substitution from money to capital, "
                     "potentially increasing the capital-labor ratio and output per worker.",
            area="monetary_economics",
            complexity=0.7,
            dependencies=["money_neutrality"]
        ),
        categories=["monetary_theory", "inflation"]
    )
    
    # Impossible trinity
    suite.add_theorem(
        TheoremBenchmark(
            id="impossible_trinity",
            statement="A country cannot simultaneously maintain a fixed exchange rate, "
                     "free capital movement, and an independent monetary policy.",
            area="international_finance",
            complexity=0.8,
            dependencies=[]
        ),
        categories=["monetary_theory", "international"]
    )
    
    return suite


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


def save_custom_benchmark(benchmark_suite, output_file):
    """Save a custom benchmark to a JSON file."""
    benchmark_suite.save(output_file)
    print(f"Custom benchmark saved to: {output_file}")


def run_custom_benchmark(config, benchmark_suite, output_dir="./benchmark_results"):
    """Run a custom benchmark suite."""
    print(f"Running custom benchmark suite: {benchmark_suite.name}")
    print(f"Description: {benchmark_suite.description}")
    print(f"Theorems: {len(benchmark_suite.theorems)}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize benchmark runner
    runner = BenchmarkRunner(output_dir=output_dir)
    
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


def main():
    """Main function for creating and running custom benchmarks."""
    parser = argparse.ArgumentParser(description="Create and run custom genetic theorem proving benchmarks")
    parser.add_argument("--output-dir", default="./benchmark_results", 
                        help="Directory to store benchmark results")
    parser.add_argument("--config", default=None,
                        help="Path to JSON configuration file")
    parser.add_argument("--save-benchmark", action="store_true",
                        help="Save the custom benchmark to a file")
    parser.add_argument("--benchmark-file", default="custom_benchmark.json",
                        help="File to save/load benchmark from")
    parser.add_argument("--load-benchmark", action="store_true",
                        help="Load a custom benchmark from a file instead of creating one")
    parser.add_argument("--category-filter", default=None,
                        help="Filter theorems by category")
    parser.add_argument("--complexity-min", type=float, default=0.0,
                        help="Minimum theorem complexity to include")
    parser.add_argument("--complexity-max", type=float, default=1.0,
                        help="Maximum theorem complexity to include")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = create_default_system_config()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create or load benchmark suite
    if args.load_benchmark:
        # Load benchmark from file
        benchmark_suite = BenchmarkSuite.load(args.benchmark_file)
        print(f"Loaded benchmark suite from {args.benchmark_file}")
    else:
        # Create new custom benchmark
        benchmark_suite = create_custom_benchmark_suite()
        
        if args.save_benchmark:
            save_custom_benchmark(benchmark_suite, args.benchmark_file)
    
    # Filter theorems if requested
    filtered_theorems = benchmark_suite.theorems
    
    if args.category_filter:
        filtered_theorems = benchmark_suite.get_theorems_by_category(args.category_filter)
        print(f"Filtered to {len(filtered_theorems)} theorems in category '{args.category_filter}'")
    
    if args.complexity_min > 0.0 or args.complexity_max < 1.0:
        filtered_theorems = benchmark_suite.get_theorems_by_complexity(
            min_complexity=args.complexity_min,
            max_complexity=args.complexity_max
        )
        print(f"Filtered to {len(filtered_theorems)} theorems with complexity between "
              f"{args.complexity_min} and {args.complexity_max}")
    
    if len(filtered_theorems) != len(benchmark_suite.theorems):
        # Create a new filtered benchmark suite
        filtered_suite = BenchmarkSuite(
            f"{benchmark_suite.name}_filtered",
            f"Filtered version of {benchmark_suite.description}"
        )
        
        for theorem in filtered_theorems:
            filtered_suite.add_theorem(theorem)
        
        benchmark_suite = filtered_suite
    
    # Run the benchmark
    result = run_custom_benchmark(config, benchmark_suite, args.output_dir)
    
    print("\nCustom benchmark completed successfully.")


if __name__ == "__main__":
    main()