# Genetic Theorem Prover Evaluation Framework

This package provides a comprehensive evaluation framework for the Genetic Theorem Proving system, including metrics, benchmarks, and visualization capabilities.

## Overview

The evaluation framework includes:

1. **Metrics** - Comprehensive metrics for evaluating proofs, agents, populations, and the overall system
2. **Benchmarks** - Standard benchmark suites and customizable benchmark tools
3. **Visualization** - Tools for visualizing performance and results
4. **Examples** - Example scripts demonstrating the evaluation framework

## Components

### Metrics

The metrics module (`metrics.py`) provides classes for evaluating:

- **ProofMetrics** - Metrics for individual proofs, including correctness, completeness, elegance, and complexity
- **AgentMetrics** - Metrics for individual agents, including success rate, proof quality, and improvement trends
- **PopulationMetrics** - Metrics for agent populations, including diversity, fitness trends, and specialization
- **SystemMetrics** - System-wide metrics, including theorem coverage, dependencies, and gap analysis
- **EvaluationFramework** - An integrated framework that combines all metrics for comprehensive evaluation

### Benchmarks

The benchmark module (`benchmark.py`) provides tools for creating and running standardized benchmarks:

- **TheoremBenchmark** - Definition of a benchmark theorem with complexity rating and expected properties
- **BenchmarkSuite** - Collection of theorems organized into a benchmark suite with categories
- **BenchmarkResult** - Results of running a benchmark, including performance metrics
- **BenchmarkRunner** - Tool for running benchmarks and collecting results
- **StandardBenchmarks** - Pre-defined benchmark suites for economic theorem proving

### Visualization

The visualization module (`visualization.py`) provides tools for creating visualizations:

- **PerformanceVisualizer** - Creates visualizations for agent performance, population evolution, theorem coverage, and benchmark comparison

## Examples

The `examples/` directory contains example scripts demonstrating how to use the evaluation framework:

- **run_benchmarks.py** - Example script for running benchmarks with the genetic theorem proving system
- **custom_benchmark.py** - Example script for creating and running custom benchmarks
- **analyze_results.py** - Example script for analyzing theorem proving benchmark results

## Usage

### Basic Usage

```python
from genetic_theorem_prover.evaluation import (
    EvaluationFramework, BenchmarkRunner, StandardBenchmarks, PerformanceVisualizer
)

# Create benchmark suite
benchmark_suite = StandardBenchmarks.create_basic_economic_benchmarks()

# Initialize benchmark runner
runner = BenchmarkRunner()

# Run benchmark
result = runner.run_benchmark(
    suite=benchmark_suite,
    system_config=config,
    population_manager=population_manager
)

# Visualize results
visualizer = PerformanceVisualizer()
visualizer.visualize_benchmark_results(result)
```

### Custom Benchmarks

```python
from genetic_theorem_prover.evaluation import (
    TheoremBenchmark, BenchmarkSuite, BenchmarkRunner
)

# Create custom benchmark suite
suite = BenchmarkSuite("custom_suite", "My custom benchmark suite")

# Add theorems
suite.add_theorem(
    TheoremBenchmark(
        id="my_theorem",
        statement="A formal statement of the theorem",
        area="my_area",
        complexity=0.5,
        dependencies=[]
    ),
    categories=["category1", "category2"]
)

# Save benchmark suite
suite.save("my_benchmark.json")

# Load benchmark suite
loaded_suite = BenchmarkSuite.load("my_benchmark.json")

# Run benchmark
runner = BenchmarkRunner()
result = runner.run_benchmark(
    suite=loaded_suite,
    system_config=config,
    population_manager=population_manager
)
```

### Analyzing Results

```python
from genetic_theorem_prover.evaluation import (
    BenchmarkResult, PerformanceVisualizer
)

# Load benchmark result
result = BenchmarkResult.load("benchmark_result.json")

# Visualize result
visualizer = PerformanceVisualizer()
visualizer.visualize_benchmark_results(result)

# Compare multiple results
results = [
    BenchmarkResult.load("result1.json"),
    BenchmarkResult.load("result2.json"),
    BenchmarkResult.load("result3.json")
]

visualizer.visualize_benchmark_comparison(results)
```

## Running the Example Scripts

To run the example scripts:

```bash
# Run basic benchmarks
python -m genetic_theorem_prover.evaluation.examples.run_benchmarks

# Create and run a custom benchmark
python -m genetic_theorem_prover.evaluation.examples.custom_benchmark

# Analyze benchmark results
python -m genetic_theorem_prover.evaluation.examples.analyze_results --results-dir ./benchmark_results
```

## Extending the Framework

The evaluation framework is designed to be extensible:

1. Create custom benchmark suites with theorems specific to your domain
2. Define custom metrics for specialized evaluation
3. Create custom visualizations for domain-specific insights
4. Integrate with existing evaluation pipelines