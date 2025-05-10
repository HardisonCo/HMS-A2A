"""
Evaluation metrics for theorem proving with genetic agents.

This module provides comprehensive metrics for evaluating:
1. Proof quality (correctness, completeness, elegance)
2. Agent performance (success rate, efficiency)
3. Population evolution (diversity, improvement rate)
4. System-wide performance (theorem coverage, complexity handling)
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass
import networkx as nx

@dataclass
class ProofMetrics:
    """Metrics for evaluating an individual proof."""
    correctness_score: float  # 0.0-1.0 measure of proof correctness
    completeness_score: float  # 0.0-1.0 measure of proof completeness
    elegance_score: float  # 0.0-1.0 measure of proof elegance/conciseness
    formal_verification_result: bool  # Whether the proof passed formal verification
    steps_count: int  # Number of steps in the proof
    lemmas_count: int  # Number of lemmas used
    axioms_count: int  # Number of axioms referenced
    depth: int  # Maximum depth of proof tree
    time_to_prove: float  # Time taken to generate the proof (seconds)
    
    @property
    def complexity_score(self) -> float:
        """Calculate proof complexity score (lower is better)."""
        return (0.4 * self.steps_count + 
                0.3 * self.lemmas_count + 
                0.2 * self.axioms_count + 
                0.1 * self.depth) / 100
    
    @property
    def overall_quality(self) -> float:
        """Calculate overall proof quality (higher is better)."""
        if not self.formal_verification_result:
            return 0.0
        
        quality = (0.4 * self.correctness_score + 
                   0.3 * self.completeness_score + 
                   0.3 * self.elegance_score)
        
        # Penalize overly complex proofs
        complexity_penalty = min(1.0, self.complexity_score)
        return quality * (1 - 0.2 * complexity_penalty)


class AgentMetrics:
    """Metrics for evaluating an individual genetic agent."""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.proof_attempts: List[Tuple[str, bool, ProofMetrics]] = []  # (theorem_id, success, metrics)
        self.time_per_attempt: List[float] = []
    
    def add_proof_attempt(self, 
                          theorem_id: str, 
                          success: bool, 
                          metrics: Optional[ProofMetrics] = None,
                          time_taken: float = 0.0) -> None:
        """Add a proof attempt to the agent's history."""
        self.proof_attempts.append((theorem_id, success, metrics))
        self.time_per_attempt.append(time_taken)
    
    @property
    def success_rate(self) -> float:
        """Calculate the agent's success rate in proving theorems."""
        if not self.proof_attempts:
            return 0.0
        return sum(1 for _, success, _ in self.proof_attempts if success) / len(self.proof_attempts)
    
    @property
    def average_proof_quality(self) -> float:
        """Calculate the average quality of successful proofs."""
        successful_metrics = [metrics for _, success, metrics in self.proof_attempts 
                              if success and metrics is not None]
        if not successful_metrics:
            return 0.0
        return sum(metrics.overall_quality for metrics in successful_metrics) / len(successful_metrics)
    
    @property
    def average_time_per_successful_proof(self) -> float:
        """Calculate the average time taken for successful proofs."""
        successful_times = [time for (_, success, _), time in zip(self.proof_attempts, self.time_per_attempt) 
                            if success]
        if not successful_times:
            return 0.0
        return sum(successful_times) / len(successful_times)
    
    @property
    def theorem_complexity_handling(self) -> Dict[str, float]:
        """Evaluate how the agent handles theorems of different complexity levels."""
        # Placeholder - in a real implementation this would categorize theorems by complexity
        # and calculate success rates per complexity category
        return {"low": 0.0, "medium": 0.0, "high": 0.0}

    def improvement_trend(self, window_size: int = 10) -> List[float]:
        """Calculate the agent's improvement trend over time using a sliding window."""
        if len(self.proof_attempts) < window_size:
            return []
        
        success_values = [1.0 if success else 0.0 for _, success, _ in self.proof_attempts]
        return [sum(success_values[i:i+window_size])/window_size 
                for i in range(len(success_values) - window_size + 1)]
    
    def visualize_performance(self) -> plt.Figure:
        """Visualize the agent's performance over time."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot success/failure
        attempts = range(len(self.proof_attempts))
        successes = [1 if success else 0 for _, success, _ in self.proof_attempts]
        
        ax.scatter(attempts, successes, c=['green' if s else 'red' for s in successes], 
                   alpha=0.6, label='Proof Attempts')
        
        # Plot trend line if enough data
        if len(self.proof_attempts) >= 10:
            trend = self.improvement_trend()
            ax.plot(range(5, 5 + len(trend)), trend, 'b-', label='Success Trend')
        
        ax.set_ylim(-0.1, 1.1)
        ax.set_xlabel('Attempt Number')
        ax.set_ylabel('Success (1) / Failure (0)')
        ax.set_title(f'Performance of Agent {self.agent_id} ({self.agent_type})')
        ax.legend()
        
        return fig


class PopulationMetrics:
    """Metrics for evaluating a population of genetic agents."""
    
    def __init__(self):
        self.generations: List[Dict[str, List[AgentMetrics]]] = []  # List of generations, each with agent metrics
        self.diversity_scores: List[float] = []  # Diversity score per generation
        self.avg_fitness_scores: List[float] = []  # Average fitness per generation
        self.best_fitness_scores: List[float] = []  # Best fitness per generation
    
    def add_generation(self, 
                       generation_id: int,
                       agent_metrics: List[AgentMetrics],
                       diversity_score: float,
                       avg_fitness: float,
                       best_fitness: float) -> None:
        """Add a generation's metrics to the population history."""
        # Group agents by type
        agents_by_type = {}
        for agent in agent_metrics:
            if agent.agent_type not in agents_by_type:
                agents_by_type[agent.agent_type] = []
            agents_by_type[agent.agent_type].append(agent)
        
        # Add to generations
        if len(self.generations) <= generation_id:
            # Add empty generations if needed
            self.generations.extend([{} for _ in range(generation_id - len(self.generations) + 1)])
        
        self.generations[generation_id] = agents_by_type
        self.diversity_scores.append(diversity_score)
        self.avg_fitness_scores.append(avg_fitness)
        self.best_fitness_scores.append(best_fitness)
    
    @property
    def improvement_rate(self) -> float:
        """Calculate the rate of improvement across generations."""
        if len(self.avg_fitness_scores) < 2:
            return 0.0
        
        # Linear regression slope
        x = np.arange(len(self.avg_fitness_scores))
        y = np.array(self.avg_fitness_scores)
        return np.polyfit(x, y, 1)[0]
    
    @property
    def plateau_detected(self) -> bool:
        """Detect if the population has reached a plateau in improvement."""
        if len(self.best_fitness_scores) < 5:
            return False
        
        # Check if the best fitness has not improved significantly in the last 5 generations
        recent_best = self.best_fitness_scores[-5:]
        return (max(recent_best) - min(recent_best)) / max(recent_best) < 0.01
    
    def success_rate_by_agent_type(self) -> Dict[str, List[float]]:
        """Calculate success rates by agent type across generations."""
        result = {}
        
        for gen in self.generations:
            for agent_type, agents in gen.items():
                if agent_type not in result:
                    result[agent_type] = []
                
                avg_success = sum(agent.success_rate for agent in agents) / len(agents)
                result[agent_type].append(avg_success)
        
        return result
    
    def visualize_evolution(self) -> plt.Figure:
        """Visualize the evolution of the population across generations."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Generation numbers
        x = range(len(self.generations))
        
        # Plot 1: Fitness trends
        ax1.plot(x, self.avg_fitness_scores, 'b-', label='Average Fitness')
        ax1.plot(x, self.best_fitness_scores, 'g-', label='Best Fitness')
        ax1.set_ylabel('Fitness Score')
        ax1.set_title('Population Fitness Over Generations')
        ax1.legend()
        
        # Plot 2: Diversity
        ax2.plot(x, self.diversity_scores, 'r-', label='Genetic Diversity')
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Diversity Score')
        ax2.set_title('Population Diversity Over Generations')
        
        plt.tight_layout()
        return fig


class SystemMetrics:
    """System-wide metrics for evaluating the theorem proving ecosystem."""
    
    def __init__(self):
        self.theorem_coverage: Dict[str, bool] = {}  # Map of theorem_id to whether it's been proved
        self.proof_distribution: Dict[str, int] = {}  # Distribution of proofs by theorem area
        self.agent_specialization: Dict[str, Dict[str, float]] = {}  # Agent type to theorem area success rate
        self.theorem_dependency_graph = nx.DiGraph()  # Graph of theorem dependencies
    
    def add_theorem(self, 
                    theorem_id: str, 
                    area: str, 
                    is_proved: bool = False,
                    dependencies: List[str] = None) -> None:
        """Add a theorem to the system metrics."""
        self.theorem_coverage[theorem_id] = is_proved
        
        # Add to proof distribution
        if area not in self.proof_distribution:
            self.proof_distribution[area] = 0
        if is_proved:
            self.proof_distribution[area] += 1
        
        # Add to dependency graph
        self.theorem_dependency_graph.add_node(theorem_id, area=area, proved=is_proved)
        if dependencies:
            for dep in dependencies:
                if dep not in self.theorem_dependency_graph:
                    self.theorem_dependency_graph.add_node(dep, area="unknown", proved=False)
                self.theorem_dependency_graph.add_edge(theorem_id, dep)
    
    def update_theorem_status(self, theorem_id: str, is_proved: bool) -> None:
        """Update the proof status of a theorem."""
        if theorem_id in self.theorem_coverage:
            old_status = self.theorem_coverage[theorem_id]
            self.theorem_coverage[theorem_id] = is_proved
            
            # Update proof distribution
            if old_status != is_proved:
                for node, attrs in self.theorem_dependency_graph.nodes(data=True):
                    if node == theorem_id:
                        area = attrs.get('area', 'unknown')
                        if area in self.proof_distribution:
                            if is_proved:
                                self.proof_distribution[area] += 1
                            else:
                                self.proof_distribution[area] -= 1
                        
                        # Update node attribute
                        self.theorem_dependency_graph.nodes[theorem_id]['proved'] = is_proved
                        break
    
    def record_agent_proof(self, agent_type: str, theorem_id: str, area: str, success: bool) -> None:
        """Record a proof attempt by an agent type for a specific theorem area."""
        if agent_type not in self.agent_specialization:
            self.agent_specialization[agent_type] = {}
        
        if area not in self.agent_specialization[agent_type]:
            self.agent_specialization[agent_type][area] = {'attempts': 0, 'successes': 0}
        
        self.agent_specialization[agent_type][area]['attempts'] += 1
        if success:
            self.agent_specialization[agent_type][area]['successes'] += 1
    
    @property
    def overall_coverage(self) -> float:
        """Calculate the overall theorem coverage (percentage of theorems proved)."""
        if not self.theorem_coverage:
            return 0.0
        return sum(1 for proved in self.theorem_coverage.values() if proved) / len(self.theorem_coverage)
    
    @property
    def coverage_by_area(self) -> Dict[str, float]:
        """Calculate theorem coverage by area."""
        # Count total theorems by area
        theorems_by_area = {}
        for node, attrs in self.theorem_dependency_graph.nodes(data=True):
            area = attrs.get('area', 'unknown')
            if area not in theorems_by_area:
                theorems_by_area[area] = {'total': 0, 'proved': 0}
            
            theorems_by_area[area]['total'] += 1
            if attrs.get('proved', False):
                theorems_by_area[area]['proved'] += 1
        
        # Calculate coverage percentages
        return {
            area: data['proved'] / data['total'] if data['total'] > 0 else 0.0
            for area, data in theorems_by_area.items()
        }
    
    @property
    def agent_specialization_scores(self) -> Dict[str, Dict[str, float]]:
        """Calculate specialization scores (success rates) by agent type and theorem area."""
        result = {}
        
        for agent_type, areas in self.agent_specialization.items():
            result[agent_type] = {}
            for area, counts in areas.items():
                if counts['attempts'] > 0:
                    result[agent_type][area] = counts['successes'] / counts['attempts']
                else:
                    result[agent_type][area] = 0.0
        
        return result
    
    def identify_coverage_gaps(self) -> List[Dict[str, Any]]:
        """Identify areas with low theorem coverage that need attention."""
        coverage = self.coverage_by_area
        return [
            {"area": area, "coverage": cov, "priority": 1.0 - cov}
            for area, cov in coverage.items()
            if cov < 0.5  # Areas with less than 50% coverage
        ]
    
    def identify_critical_unproved_theorems(self) -> List[str]:
        """Identify unproved theorems with many dependents (critical for proving others)."""
        unproved_theorems = []
        
        for node in self.theorem_dependency_graph.nodes():
            attrs = self.theorem_dependency_graph.nodes[node]
            if not attrs.get('proved', False):
                # Count dependents
                dependents = 0
                for _, target, _ in self.theorem_dependency_graph.in_edges(node, data=True):
                    if target == node:
                        dependents += 1
                
                if dependents >= 2:  # Theorems with at least 2 dependents
                    unproved_theorems.append((node, dependents))
        
        # Sort by dependency count (descending)
        unproved_theorems.sort(key=lambda x: x[1], reverse=True)
        return [thm for thm, _ in unproved_theorems]
    
    def visualize_theorem_coverage(self) -> plt.Figure:
        """Visualize theorem coverage by area."""
        coverage = self.coverage_by_area
        areas = list(coverage.keys())
        values = list(coverage.values())
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(areas, values, color='skyblue')
        
        # Add percentage labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1%}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax.set_ylim(0, 1.0)
        ax.set_ylabel('Coverage Percentage')
        ax.set_title('Theorem Coverage by Area')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return fig
    
    def visualize_dependency_graph(self) -> plt.Figure:
        """Visualize the theorem dependency graph."""
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # Create position layout
        pos = nx.spring_layout(self.theorem_dependency_graph)
        
        # Define node colors based on proof status
        node_colors = [
            'green' if self.theorem_dependency_graph.nodes[node].get('proved', False) else 'red'
            for node in self.theorem_dependency_graph.nodes()
        ]
        
        # Draw the graph
        nx.draw_networkx(
            self.theorem_dependency_graph,
            pos=pos,
            with_labels=True,
            node_color=node_colors,
            node_size=500,
            font_size=8,
            font_color='black',
            font_weight='bold',
            edge_color='gray',
            arrows=True,
            ax=ax
        )
        
        ax.set_title('Theorem Dependency Graph')
        ax.axis('off')
        
        return fig


class EvaluationFramework:
    """Framework for comprehensive evaluation of the genetic theorem proving system."""
    
    def __init__(self):
        self.proof_metrics = {}  # theorem_id -> ProofMetrics
        self.agent_metrics = {}  # agent_id -> AgentMetrics
        self.population_metrics = PopulationMetrics()
        self.system_metrics = SystemMetrics()
    
    def evaluate_proof(self, 
                       theorem_id: str, 
                       proof_data: Dict[str, Any],
                       verification_result: bool,
                       time_taken: float) -> ProofMetrics:
        """Evaluate a proof and return its metrics."""
        # Calculate metrics from proof data
        metrics = ProofMetrics(
            correctness_score=proof_data.get('correctness_score', 0.0),
            completeness_score=proof_data.get('completeness_score', 0.0),
            elegance_score=proof_data.get('elegance_score', 0.0),
            formal_verification_result=verification_result,
            steps_count=len(proof_data.get('steps', [])),
            lemmas_count=len(proof_data.get('lemmas', [])),
            axioms_count=len(proof_data.get('axioms', [])),
            depth=proof_data.get('depth', 0),
            time_to_prove=time_taken
        )
        
        # Store metrics
        self.proof_metrics[theorem_id] = metrics
        
        # Update system metrics
        self.system_metrics.update_theorem_status(theorem_id, verification_result)
        
        return metrics
    
    def record_proof_attempt(self, 
                             agent_id: str,
                             agent_type: str, 
                             theorem_id: str,
                             theorem_area: str,
                             success: bool,
                             proof_data: Optional[Dict[str, Any]] = None,
                             time_taken: float = 0.0) -> None:
        """Record a proof attempt by an agent."""
        # Ensure agent exists in metrics
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics(agent_id, agent_type)
        
        # Evaluate proof if successful
        proof_metrics = None
        if success and proof_data:
            verification_result = proof_data.get('verification_result', False)
            proof_metrics = self.evaluate_proof(theorem_id, proof_data, verification_result, time_taken)
        
        # Record attempt in agent metrics
        self.agent_metrics[agent_id].add_proof_attempt(
            theorem_id, success, proof_metrics, time_taken
        )
        
        # Record in system metrics
        self.system_metrics.record_agent_proof(agent_type, theorem_id, theorem_area, success)
    
    def record_generation(self,
                          generation_id: int,
                          agent_metrics_ids: List[str],
                          diversity_score: float,
                          fitness_scores: List[float]) -> None:
        """Record a generation's metrics for population evaluation."""
        agent_metrics_list = [
            self.agent_metrics[agent_id] for agent_id in agent_metrics_ids
            if agent_id in self.agent_metrics
        ]
        
        avg_fitness = sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0.0
        best_fitness = max(fitness_scores) if fitness_scores else 0.0
        
        self.population_metrics.add_generation(
            generation_id,
            agent_metrics_list,
            diversity_score,
            avg_fitness,
            best_fitness
        )
    
    def add_theorem_to_system(self,
                              theorem_id: str,
                              area: str,
                              is_proved: bool = False,
                              dependencies: List[str] = None) -> None:
        """Add a theorem to the system metrics."""
        self.system_metrics.add_theorem(theorem_id, area, is_proved, dependencies)
    
    def generate_evaluation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive evaluation report."""
        report = {
            "system_overview": {
                "total_theorems": len(self.system_metrics.theorem_coverage),
                "proved_theorems": sum(1 for proved in self.system_metrics.theorem_coverage.values() if proved),
                "overall_coverage": self.system_metrics.overall_coverage,
                "coverage_by_area": self.system_metrics.coverage_by_area,
                "coverage_gaps": self.system_metrics.identify_coverage_gaps(),
                "critical_unproved_theorems": self.system_metrics.identify_critical_unproved_theorems()
            },
            "population_performance": {
                "generations_evaluated": len(self.population_metrics.generations),
                "improvement_rate": self.population_metrics.improvement_rate,
                "plateau_detected": self.population_metrics.plateau_detected,
                "success_rate_by_agent_type": self.population_metrics.success_rate_by_agent_type()
            },
            "agent_performance": {
                agent_id: {
                    "type": agent.agent_type,
                    "success_rate": agent.success_rate,
                    "avg_proof_quality": agent.average_proof_quality,
                    "avg_time_per_success": agent.average_time_per_successful_proof,
                    "total_attempts": len(agent.proof_attempts)
                }
                for agent_id, agent in self.agent_metrics.items()
            },
            "proof_statistics": {
                "avg_correctness": np.mean([m.correctness_score for m in self.proof_metrics.values()]) 
                                  if self.proof_metrics else 0.0,
                "avg_completeness": np.mean([m.completeness_score for m in self.proof_metrics.values()])
                                   if self.proof_metrics else 0.0,
                "avg_elegance": np.mean([m.elegance_score for m in self.proof_metrics.values()])
                               if self.proof_metrics else 0.0,
                "verification_success_rate": np.mean([1.0 if m.formal_verification_result else 0.0 
                                                    for m in self.proof_metrics.values()])
                                            if self.proof_metrics else 0.0,
                "avg_complexity": np.mean([m.complexity_score for m in self.proof_metrics.values()])
                                if self.proof_metrics else 0.0,
                "avg_steps": np.mean([m.steps_count for m in self.proof_metrics.values()])
                           if self.proof_metrics else 0.0
            },
            "specialization_efficiency": self.system_metrics.agent_specialization_scores
        }
        
        return report
    
    def visualize_system_performance(self, output_dir: str) -> None:
        """Generate and save visualization of system performance."""
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # System Visualizations
        theorem_coverage_fig = self.system_metrics.visualize_theorem_coverage()
        theorem_coverage_fig.savefig(os.path.join(output_dir, "theorem_coverage.png"))
        
        dependency_graph_fig = self.system_metrics.visualize_dependency_graph()
        dependency_graph_fig.savefig(os.path.join(output_dir, "dependency_graph.png"))
        
        # Population Visualizations
        population_evolution_fig = self.population_metrics.visualize_evolution()
        population_evolution_fig.savefig(os.path.join(output_dir, "population_evolution.png"))
        
        # Agent Visualizations (sample of top agents)
        if self.agent_metrics:
            # Sort agents by success rate
            sorted_agents = sorted(self.agent_metrics.items(), 
                                  key=lambda x: x[1].success_rate, 
                                  reverse=True)
            
            # Visualize top 5 agents (or all if less than 5)
            for agent_id, agent in sorted_agents[:min(5, len(sorted_agents))]:
                agent_fig = agent.visualize_performance()
                agent_fig.savefig(os.path.join(output_dir, f"agent_{agent_id}_performance.png"))
        
        plt.close('all')