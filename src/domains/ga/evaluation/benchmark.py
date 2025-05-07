"""
Benchmark framework for the genetic theorem proving system.

This module provides tools for:
1. Creating benchmark theorem sets
2. Running standardized benchmarks
3. Comparing performance across different system configurations
4. Analyzing benchmark results
"""

import time
import json
import datetime
import os
from typing import Dict, List, Any, Optional, Tuple, Callable
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field

from ..core.base_agent import GeneticTheoremProverAgent
from ..evolution.population_manager import PopulationManager
from .metrics import EvaluationFramework


@dataclass
class TheoremBenchmark:
    """A benchmark theorem for evaluating prover performance."""
    id: str
    statement: str
    area: str
    complexity: float  # 0.0-1.0 difficulty rating
    dependencies: List[str] = field(default_factory=list)
    expected_proof_exists: bool = True
    expected_proof_steps: Optional[int] = None
    timeout: float = 300.0  # seconds
    reference_implementation: Optional[str] = None


@dataclass
class BenchmarkResult:
    """Result of running a benchmark."""
    benchmark_id: str
    system_config: Dict[str, Any]
    timestamp: str
    theorems_total: int
    theorems_proved: int
    coverage_percentage: float
    avg_proof_time: float
    success_by_complexity: Dict[str, float]
    theorem_results: Dict[str, Dict[str, Any]]
    population_metrics: Dict[str, Any]
    report_file: Optional[str] = None
    
    def save(self, output_dir: str) -> str:
        """Save benchmark result to a JSON file."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filename = f"benchmark_{self.benchmark_id}_{self.timestamp.replace(':', '-').replace(' ', '_')}.json"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w') as f:
            # Convert to dict for serialization
            result_dict = {k: v for k, v in self.__dict__.items()}
            json.dump(result_dict, f, indent=2)
        
        self.report_file = file_path
        return file_path
    
    @classmethod
    def load(cls, file_path: str) -> 'BenchmarkResult':
        """Load benchmark result from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            return cls(**data)


class BenchmarkSuite:
    """A suite of theorem benchmarks for comprehensive evaluation."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.theorems: List[TheoremBenchmark] = []
        self.categories: Dict[str, List[str]] = {}  # Category name -> list of theorem IDs
    
    def add_theorem(self, theorem: TheoremBenchmark, categories: List[str] = None) -> None:
        """Add a theorem to the benchmark suite."""
        self.theorems.append(theorem)
        
        # Add to categories
        if categories:
            for category in categories:
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(theorem.id)
    
    def get_theorems_by_category(self, category: str) -> List[TheoremBenchmark]:
        """Get all theorems in a specific category."""
        if category not in self.categories:
            return []
        
        theorem_ids = self.categories[category]
        return [thm for thm in self.theorems if thm.id in theorem_ids]
    
    def get_theorems_by_complexity(self, min_complexity: float = 0.0, 
                                  max_complexity: float = 1.0) -> List[TheoremBenchmark]:
        """Get theorems within a complexity range."""
        return [
            thm for thm in self.theorems 
            if min_complexity <= thm.complexity <= max_complexity
        ]
    
    def save(self, file_path: str) -> None:
        """Save the benchmark suite to a JSON file."""
        data = {
            "name": self.name,
            "description": self.description,
            "theorems": [
                {
                    "id": thm.id,
                    "statement": thm.statement,
                    "area": thm.area,
                    "complexity": thm.complexity,
                    "dependencies": thm.dependencies,
                    "expected_proof_exists": thm.expected_proof_exists,
                    "expected_proof_steps": thm.expected_proof_steps,
                    "timeout": thm.timeout,
                    "reference_implementation": thm.reference_implementation
                }
                for thm in self.theorems
            ],
            "categories": self.categories
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, file_path: str) -> 'BenchmarkSuite':
        """Load a benchmark suite from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            suite = cls(data["name"], data["description"])
            
            # Load theorems
            for thm_data in data["theorems"]:
                theorem = TheoremBenchmark(
                    id=thm_data["id"],
                    statement=thm_data["statement"],
                    area=thm_data["area"],
                    complexity=thm_data["complexity"],
                    dependencies=thm_data.get("dependencies", []),
                    expected_proof_exists=thm_data.get("expected_proof_exists", True),
                    expected_proof_steps=thm_data.get("expected_proof_steps"),
                    timeout=thm_data.get("timeout", 300.0),
                    reference_implementation=thm_data.get("reference_implementation")
                )
                suite.theorems.append(theorem)
            
            # Load categories
            suite.categories = data.get("categories", {})
            
            return suite


class BenchmarkRunner:
    """Runs benchmarks on the genetic theorem proving system."""
    
    def __init__(self, 
                 output_dir: str = "./benchmark_results",
                 verbose: bool = True):
        self.output_dir = output_dir
        self.verbose = verbose
        self.evaluation_framework = EvaluationFramework()
        self.results: List[BenchmarkResult] = []
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _get_complexity_category(self, complexity: float) -> str:
        """Convert complexity score to category."""
        if complexity < 0.3:
            return "easy"
        elif complexity < 0.7:
            return "medium"
        else:
            return "hard"
    
    def run_benchmark(self, 
                      suite: BenchmarkSuite,
                      system_config: Dict[str, Any],
                      population_manager: PopulationManager,
                      max_generations: int = 10,
                      timeout_multiplier: float = 1.0) -> BenchmarkResult:
        """
        Run a benchmark suite against the genetic theorem proving system.
        
        Args:
            suite: The benchmark suite to run
            system_config: Configuration of the system (for recording)
            population_manager: The population manager to use for theorem proving
            max_generations: Maximum number of generations to run per theorem
            timeout_multiplier: Multiplier for theorem timeouts
            
        Returns:
            BenchmarkResult with the results of the benchmark
        """
        benchmark_id = f"{suite.name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize results storage
        theorem_results = {}
        total_theorems = len(suite.theorems)
        theorems_proved = 0
        total_proof_time = 0.0
        success_by_complexity = {"easy": 0, "medium": 0, "hard": 0}
        complexity_counts = {"easy": 0, "medium": 0, "hard": 0}
        
        # Add all theorems to the evaluation framework
        for theorem in suite.theorems:
            self.evaluation_framework.add_theorem_to_system(
                theorem.id,
                theorem.area,
                False,
                theorem.dependencies
            )
            
            # Count by complexity
            complexity_category = self._get_complexity_category(theorem.complexity)
            complexity_counts[complexity_category] += 1
        
        # Process each theorem
        for theorem in suite.theorems:
            if self.verbose:
                print(f"Benchmarking theorem: {theorem.id} (complexity: {theorem.complexity:.2f})")
            
            # Set up theorem-specific timeout
            timeout = theorem.timeout * timeout_multiplier
            
            # Record start time
            start_time = time.time()
            
            # Attempt to prove the theorem
            proof_result = population_manager.prove_theorem(
                theorem.id,
                theorem.statement,
                max_generations=max_generations,
                timeout=timeout
            )
            
            # Record end time
            end_time = time.time()
            proof_time = end_time - start_time
            
            # Process result
            success = proof_result.get("success", False)
            proof_data = proof_result.get("proof_data", {})
            
            if success:
                theorems_proved += 1
                total_proof_time += proof_time
                
                # Update success by complexity
                complexity_category = self._get_complexity_category(theorem.complexity)
                success_by_complexity[complexity_category] += 1
            
            # Record in theorem results
            theorem_results[theorem.id] = {
                "success": success,
                "proof_time": proof_time,
                "proof_data": proof_data,
                "complexity": theorem.complexity,
                "complexity_category": self._get_complexity_category(theorem.complexity),
                "area": theorem.area
            }
            
            # Update system metrics
            self.evaluation_framework.system_metrics.update_theorem_status(theorem.id, success)
            
            if self.verbose:
                print(f"  Result: {'Success' if success else 'Failure'} in {proof_time:.2f} seconds")
        
        # Calculate success rates by complexity
        success_by_complexity = {
            category: (count / complexity_counts[category] if complexity_counts[category] > 0 else 0.0)
            for category, count in success_by_complexity.items()
        }
        
        # Get population metrics
        population_metrics = {
            "generations": len(population_manager.generation_history),
            "improvement_rate": population_manager.calculate_improvement_rate(),
            "diversity_history": population_manager.diversity_history,
            "best_fitness_history": population_manager.best_fitness_history,
            "avg_fitness_history": population_manager.avg_fitness_history
        }
        
        # Create result
        result = BenchmarkResult(
            benchmark_id=benchmark_id,
            system_config=system_config,
            timestamp=timestamp,
            theorems_total=total_theorems,
            theorems_proved=theorems_proved,
            coverage_percentage=(theorems_proved / total_theorems) if total_theorems > 0 else 0.0,
            avg_proof_time=(total_proof_time / theorems_proved) if theorems_proved > 0 else 0.0,
            success_by_complexity=success_by_complexity,
            theorem_results=theorem_results,
            population_metrics=population_metrics
        )
        
        # Save result
        result_file = result.save(self.output_dir)
        if self.verbose:
            print(f"Benchmark results saved to: {result_file}")
        
        # Add to results history
        self.results.append(result)
        
        return result
    
    def compare_results(self, result_ids: List[str] = None) -> Dict[str, Any]:
        """
        Compare multiple benchmark results.
        
        Args:
            result_ids: List of result IDs to compare. If None, uses all results.
            
        Returns:
            Dictionary with comparison metrics
        """
        if not self.results:
            return {"error": "No benchmark results available"}
        
        # Filter results if IDs provided
        results_to_compare = self.results
        if result_ids:
            results_to_compare = [r for r in self.results if r.benchmark_id in result_ids]
            if not results_to_compare:
                return {"error": "No matching benchmark results found"}
        
        # Build comparison
        comparison = {
            "results": [
                {
                    "id": result.benchmark_id,
                    "timestamp": result.timestamp,
                    "config_summary": self._summarize_config(result.system_config),
                    "coverage": result.coverage_percentage,
                    "avg_proof_time": result.avg_proof_time,
                    "success_by_complexity": result.success_by_complexity
                }
                for result in results_to_compare
            ],
            "theorem_comparison": {}
        }
        
        # Compare individual theorem results
        all_theorem_ids = set()
        for result in results_to_compare:
            all_theorem_ids.update(result.theorem_results.keys())
        
        for theorem_id in all_theorem_ids:
            comparison["theorem_comparison"][theorem_id] = {
                result.benchmark_id: {
                    "success": result.theorem_results.get(theorem_id, {}).get("success", False),
                    "proof_time": result.theorem_results.get(theorem_id, {}).get("proof_time", None)
                }
                for result in results_to_compare
            }
        
        return comparison
    
    def _summarize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of system configuration for display."""
        # Extract key configuration details
        return {
            "population_size": config.get("population_size", "N/A"),
            "max_generations": config.get("max_generations", "N/A"),
            "mutation_rate": config.get("mutation_rate", "N/A"),
            "selection_method": config.get("selection_method", "N/A"),
            "agent_types": config.get("agent_types", "N/A")
        }
    
    def visualize_comparison(self, 
                            result_ids: List[str] = None,
                            output_file: str = None) -> plt.Figure:
        """
        Visualize a comparison of benchmark results.
        
        Args:
            result_ids: List of result IDs to compare. If None, uses all results.
            output_file: Path to save the visualization. If None, doesn't save.
            
        Returns:
            Matplotlib figure with the visualization
        """
        comparison = self.compare_results(result_ids)
        if "error" in comparison:
            raise ValueError(comparison["error"])
        
        results = comparison["results"]
        
        # Create figure
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
        
        # Plot 1: Overall coverage
        labels = [f"{r['id'].split('_')[0]}\n{r['timestamp'][:10]}" for r in results]
        coverage = [r["coverage"] * 100 for r in results]
        
        bars = ax1.bar(labels, coverage, color='skyblue')
        ax1.set_ylim(0, 100)
        ax1.set_ylabel('Coverage (%)')
        ax1.set_title('Theorem Coverage by Benchmark Run')
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # Plot 2: Average proof time
        avg_times = [r["avg_proof_time"] for r in results]
        bars = ax2.bar(labels, avg_times, color='lightgreen')
        ax2.set_ylabel('Average Proof Time (s)')
        ax2.set_title('Average Proof Time by Benchmark Run')
        
        # Add time labels
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height:.2f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # Plot 3: Success by complexity
        x = np.arange(len(labels))
        width = 0.25
        
        easy_success = [r["success_by_complexity"].get("easy", 0) * 100 for r in results]
        medium_success = [r["success_by_complexity"].get("medium", 0) * 100 for r in results]
        hard_success = [r["success_by_complexity"].get("hard", 0) * 100 for r in results]
        
        ax3.bar(x - width, easy_success, width, label='Easy', color='green')
        ax3.bar(x, medium_success, width, label='Medium', color='orange')
        ax3.bar(x + width, hard_success, width, label='Hard', color='red')
        
        ax3.set_xticks(x)
        ax3.set_xticklabels(labels)
        ax3.set_ylim(0, 100)
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_title('Success Rate by Theorem Complexity')
        ax3.legend()
        
        plt.tight_layout()
        
        # Save if output file provided
        if output_file:
            plt.savefig(output_file)
        
        return fig


class StandardBenchmarks:
    """Collection of standard benchmark suites for economic theorem proving."""
    
    @staticmethod
    def create_basic_economic_benchmarks() -> BenchmarkSuite:
        """Create a basic set of economic theorem benchmarks."""
        suite = BenchmarkSuite(
            "basic_economic",
            "Basic economic theorems for benchmarking"
        )
        
        # Add theorems
        suite.add_theorem(
            TheoremBenchmark(
                id="supply_demand_equilibrium",
                statement="For any market with a downward-sloping demand curve and an upward-sloping supply curve, "
                         "there exists a unique price and quantity at which the market clears.",
                area="microeconomics",
                complexity=0.4,
                dependencies=[]
            ),
            categories=["microeconomics", "equilibrium"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="profit_maximization",
                statement="A profit-maximizing firm chooses output level where marginal revenue equals marginal cost.",
                area="microeconomics",
                complexity=0.3,
                dependencies=[]
            ),
            categories=["microeconomics", "optimization"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="utility_maximization",
                statement="A utility-maximizing consumer allocates budget such that the marginal utility per dollar "
                         "is equal across all goods.",
                area="microeconomics",
                complexity=0.5,
                dependencies=[]
            ),
            categories=["microeconomics", "optimization"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="comparative_advantage",
                statement="Two countries can both gain from trade if they specialize in goods where they have "
                         "a comparative advantage, even if one country has an absolute advantage in all goods.",
                area="international_trade",
                complexity=0.6,
                dependencies=["opportunity_cost"]
            ),
            categories=["international_trade", "optimization"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="opportunity_cost",
                statement="The opportunity cost of producing a good is the value of the next best alternative "
                         "that must be foregone.",
                area="general_economics",
                complexity=0.2,
                dependencies=[]
            ),
            categories=["general_economics", "fundamentals"]
        )
        
        return suite
    
    @staticmethod
    def create_advanced_economic_benchmarks() -> BenchmarkSuite:
        """Create an advanced set of economic theorem benchmarks."""
        suite = BenchmarkSuite(
            "advanced_economic",
            "Advanced economic theorems for benchmarking"
        )
        
        # Add theorems
        suite.add_theorem(
            TheoremBenchmark(
                id="first_welfare_theorem",
                statement="Under perfect competition, a market equilibrium is Pareto efficient.",
                area="welfare_economics",
                complexity=0.8,
                dependencies=["perfect_competition", "pareto_efficiency"]
            ),
            categories=["welfare_economics", "equilibrium"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="second_welfare_theorem",
                statement="Any Pareto efficient allocation can be achieved as a competitive equilibrium with "
                         "appropriate lump-sum transfers.",
                area="welfare_economics",
                complexity=0.9,
                dependencies=["first_welfare_theorem"]
            ),
            categories=["welfare_economics", "equilibrium"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="perfect_competition",
                statement="In a perfectly competitive market, firms are price takers and economic profit is zero "
                         "in the long run.",
                area="microeconomics",
                complexity=0.5,
                dependencies=[]
            ),
            categories=["microeconomics", "market_structure"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="pareto_efficiency",
                statement="An allocation is Pareto efficient if no individual can be made better off without "
                         "making at least one individual worse off.",
                area="welfare_economics",
                complexity=0.4,
                dependencies=[]
            ),
            categories=["welfare_economics", "fundamentals"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="nash_equilibrium",
                statement="In a Nash equilibrium, no player can unilaterally deviate from their strategy "
                         "to increase their payoff.",
                area="game_theory",
                complexity=0.7,
                dependencies=[]
            ),
            categories=["game_theory", "equilibrium"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="coase_theorem",
                statement="In the absence of transaction costs, the initial allocation of property rights "
                         "does not affect economic efficiency.",
                area="law_and_economics",
                complexity=0.8,
                dependencies=["externalities"]
            ),
            categories=["law_and_economics", "externalities"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="externalities",
                statement="An externality occurs when the production or consumption of a good affects a third party "
                         "not involved in the market transaction.",
                area="public_economics",
                complexity=0.3,
                dependencies=[]
            ),
            categories=["public_economics", "market_failure"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="ricardian_equivalence",
                statement="Under certain assumptions, the method of financing government expenditure "
                         "(taxes vs. debt) does not affect the overall level of demand in an economy.",
                area="macroeconomics",
                complexity=0.8,
                dependencies=["rational_expectations"]
            ),
            categories=["macroeconomics", "fiscal_policy"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="rational_expectations",
                statement="Economic agents make decisions based on their expectations of future events, "
                         "and these expectations are not systematically biased.",
                area="macroeconomics",
                complexity=0.6,
                dependencies=[]
            ),
            categories=["macroeconomics", "expectations"]
        )
        
        return suite
    
    @staticmethod
    def create_specialized_international_trade_benchmarks() -> BenchmarkSuite:
        """Create specialized international trade theorem benchmarks."""
        suite = BenchmarkSuite(
            "international_trade",
            "Specialized international trade theorems for benchmarking"
        )
        
        # Add theorems
        suite.add_theorem(
            TheoremBenchmark(
                id="heckscher_ohlin",
                statement="Countries export goods that intensively use their relatively abundant factors "
                         "of production and import goods that intensively use their relatively scarce factors.",
                area="international_trade",
                complexity=0.7,
                dependencies=["factor_price_equalization"]
            ),
            categories=["international_trade", "factor_endowments"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="factor_price_equalization",
                statement="International trade tends to equalize the prices of factors of production across countries.",
                area="international_trade",
                complexity=0.6,
                dependencies=[]
            ),
            categories=["international_trade", "factor_endowments"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="stolper_samuelson",
                statement="An increase in the relative price of a good increases the real return to the factor "
                         "used intensively in that good's production and decreases the real return to the other factor.",
                area="international_trade",
                complexity=0.8,
                dependencies=["heckscher_ohlin"]
            ),
            categories=["international_trade", "factor_returns"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="rybczynski",
                statement="An increase in endowment of one factor leads to a more than proportional increase "
                         "in output of the good using that factor intensively, and a decrease in output of the other good.",
                area="international_trade",
                complexity=0.8,
                dependencies=["heckscher_ohlin"]
            ),
            categories=["international_trade", "production"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="lerner_samuelson",
                statement="Free trade in goods can substitute for free movement of factors of production.",
                area="international_trade",
                complexity=0.7,
                dependencies=["factor_price_equalization"]
            ),
            categories=["international_trade", "factor_mobility"]
        )
        
        suite.add_theorem(
            TheoremBenchmark(
                id="optimal_tariff",
                statement="A large country can improve its terms of trade and welfare by imposing "
                         "an optimal tariff on imports.",
                area="international_trade",
                complexity=0.6,
                dependencies=[]
            ),
            categories=["international_trade", "trade_policy"]
        )
        
        return suite