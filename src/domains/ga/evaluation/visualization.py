"""
Visualization tools for genetic theorem proving evaluation.

This module provides visualization capabilities for:
1. Agent performance over time
2. Population evolution metrics
3. Theorem coverage and complexity analysis
4. Comparison of different system configurations
5. Visualizing theorem dependency networks
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pandas as pd
from datetime import datetime

from .metrics import EvaluationFramework, SystemMetrics, PopulationMetrics, AgentMetrics
from .benchmark import BenchmarkResult


class PerformanceVisualizer:
    """Visualizes performance metrics for genetic theorem proving."""
    
    def __init__(self, output_dir: str = "./visualization_output"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def save_figure(self, fig: plt.Figure, filename: str) -> str:
        """Save a figure to the output directory."""
        file_path = os.path.join(self.output_dir, filename)
        fig.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return file_path
    
    def visualize_agent_performance(self, agent: AgentMetrics) -> plt.Figure:
        """
        Visualize performance metrics for a single agent.
        
        Args:
            agent: The agent metrics to visualize
            
        Returns:
            Matplotlib figure with the visualization
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Success/Failure over time
        attempts = range(len(agent.proof_attempts))
        successes = [1 if success else 0 for _, success, _ in agent.proof_attempts]
        
        ax1.scatter(attempts, successes, c=['green' if s else 'red' for s in successes], 
                   alpha=0.6, s=100, label='Proof Attempts')
        
        # Plot trend line if enough data
        if len(agent.proof_attempts) >= 10:
            trend = agent.improvement_trend()
            ax1.plot(range(5, 5 + len(trend)), trend, 'b-', linewidth=2, label='Success Trend (10-attempt window)')
        
        ax1.set_ylim(-0.1, 1.1)
        ax1.set_xlabel('Attempt Number')
        ax1.set_ylabel('Success (1) / Failure (0)')
        ax1.set_title(f'Performance of Agent {agent.agent_id} ({agent.agent_type})')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 2: Proof quality over time
        successful_attempts = [(i, metrics) for i, (_, success, metrics) in enumerate(agent.proof_attempts) 
                              if success and metrics is not None]
        
        if successful_attempts:
            indices, metrics_list = zip(*successful_attempts)
            
            ax2.plot(indices, [m.correctness_score for m in metrics_list], 'bo-', label='Correctness')
            ax2.plot(indices, [m.completeness_score for m in metrics_list], 'go-', label='Completeness')
            ax2.plot(indices, [m.elegance_score for m in metrics_list], 'ro-', label='Elegance')
            ax2.plot(indices, [m.overall_quality for m in metrics_list], 'mo-', linewidth=2, label='Overall Quality')
            
            ax2.set_xlabel('Attempt Number')
            ax2.set_ylabel('Score (0-1)')
            ax2.set_ylim(0, 1.1)
            ax2.set_title('Proof Quality Metrics for Successful Proofs')
            ax2.legend()
            ax2.grid(True, linestyle='--', alpha=0.7)
        else:
            ax2.text(0.5, 0.5, 'No successful proofs with metrics available',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, fontsize=14)
        
        plt.tight_layout()
        return fig
    
    def visualize_population_evolution(self, population_metrics: PopulationMetrics) -> plt.Figure:
        """
        Visualize evolution metrics for a population of agents.
        
        Args:
            population_metrics: The population metrics to visualize
            
        Returns:
            Matplotlib figure with the visualization
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
        
        # Generation numbers
        x = range(len(population_metrics.diversity_scores))
        
        # Plot 1: Fitness trends
        ax1.plot(x, population_metrics.avg_fitness_scores, 'b-', linewidth=2, label='Average Fitness')
        ax1.plot(x, population_metrics.best_fitness_scores, 'g-', linewidth=2, label='Best Fitness')
        ax1.set_ylabel('Fitness Score')
        ax1.set_title('Population Fitness Over Generations')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 2: Diversity
        ax2.plot(x, population_metrics.diversity_scores, 'r-', linewidth=2)
        ax2.set_ylabel('Diversity Score')
        ax2.set_title('Population Genetic Diversity Over Generations')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 3: Success rates by agent type
        success_rates = population_metrics.success_rate_by_agent_type()
        
        for agent_type, rates in success_rates.items():
            if len(rates) > 0:  # Only plot if we have data
                ax3.plot(range(len(rates)), rates, '-o', linewidth=2, label=f'{agent_type}')
        
        ax3.set_xlabel('Generation')
        ax3.set_ylabel('Success Rate')
        ax3.set_ylim(0, 1.1)
        ax3.set_title('Success Rate by Agent Type')
        
        if success_rates:
            ax3.legend()
        else:
            ax3.text(0.5, 0.5, 'No success rate data available by agent type',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax3.transAxes, fontsize=14)
        
        ax3.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def visualize_theorem_coverage(self, system_metrics: SystemMetrics) -> plt.Figure:
        """
        Visualize theorem coverage metrics.
        
        Args:
            system_metrics: The system metrics to visualize
            
        Returns:
            Matplotlib figure with the visualization
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Plot 1: Coverage by area
        coverage = system_metrics.coverage_by_area
        areas = list(coverage.keys())
        values = list(coverage.values())
        
        # Sort by coverage (descending)
        sorted_indices = np.argsort(values)[::-1]
        sorted_areas = [areas[i] for i in sorted_indices]
        sorted_values = [values[i] for i in sorted_indices]
        
        bars = ax1.bar(sorted_areas, sorted_values, color='skyblue')
        
        # Add percentage labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.1%}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax1.set_ylim(0, 1.0)
        ax1.set_ylabel('Coverage Percentage')
        ax1.set_title('Theorem Coverage by Area')
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        ax1.grid(True, linestyle='--', alpha=0.3, axis='y')
        
        # Plot 2: Agent specialization heatmap
        specialization = system_metrics.agent_specialization_scores
        
        if specialization:
            # Convert to DataFrame for easy heatmap plotting
            agent_types = list(specialization.keys())
            areas = set()
            for area_dict in specialization.values():
                areas.update(area_dict.keys())
            areas = list(areas)
            
            # Create data matrix
            data = np.zeros((len(agent_types), len(areas)))
            for i, agent_type in enumerate(agent_types):
                for j, area in enumerate(areas):
                    data[i, j] = specialization.get(agent_type, {}).get(area, 0.0)
            
            # Create heatmap
            im = ax2.imshow(data, cmap='YlGnBu', interpolation='nearest', aspect='auto', vmin=0, vmax=1)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax2)
            cbar.set_label('Success Rate')
            
            # Add labels
            ax2.set_xticks(np.arange(len(areas)))
            ax2.set_yticks(np.arange(len(agent_types)))
            ax2.set_xticklabels(areas)
            ax2.set_yticklabels(agent_types)
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # Add text annotations
            for i in range(len(agent_types)):
                for j in range(len(areas)):
                    text = ax2.text(j, i, f'{data[i, j]:.2f}',
                                   ha="center", va="center", color="black" if data[i, j] < 0.7 else "white")
            
            ax2.set_title('Agent Type Specialization by Theorem Area')
        else:
            ax2.text(0.5, 0.5, 'No agent specialization data available',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, fontsize=14)
        
        plt.tight_layout()
        return fig
    
    def visualize_theorem_dependency_network(self, system_metrics: SystemMetrics) -> plt.Figure:
        """
        Visualize the theorem dependency network.
        
        Args:
            system_metrics: The system metrics containing the dependency graph
            
        Returns:
            Matplotlib figure with the network visualization
        """
        G = system_metrics.theorem_dependency_graph
        
        if len(G.nodes()) == 0:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'No theorem dependency data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        fig, ax = plt.subplots(figsize=(15, 12))
        
        # Create position layout
        pos = nx.spring_layout(G, k=0.15, iterations=50, seed=42)
        
        # Get node attributes for coloring
        node_colors = []
        for node in G.nodes():
            if G.nodes[node].get('proved', False):
                node_colors.append('green')
            else:
                node_colors.append('red')
        
        # Get node sizes based on importance (number of dependencies)
        node_sizes = []
        for node in G.nodes():
            # Count incoming edges (dependents)
            in_degree = len(list(G.in_edges(node)))
            size = 300 + (in_degree * 100)  # Base size + boost for important nodes
            node_sizes.append(min(size, 1500))  # Cap size
        
        # Group nodes by area for coloring edges
        areas = {}
        for node, attrs in G.nodes(data=True):
            area = attrs.get('area', 'unknown')
            if area not in areas:
                areas[area] = []
            areas[area].append(node)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8,
            ax=ax
        )
        
        # Draw edges with different colors by area
        area_colors = plt.cm.tab10(np.linspace(0, 1, len(areas)))
        for i, (area, nodes) in enumerate(areas.items()):
            # Get edges between nodes in this area
            area_edges = [e for e in G.edges() if G.nodes[e[0]].get('area', '') == area]
            if area_edges:
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=area_edges,
                    width=1.5, alpha=0.5, 
                    edge_color=[area_colors[i]],
                    connectionstyle='arc3,rad=0.1',
                    ax=ax
                )
        
        # Draw labels with smaller font for readability
        nx.draw_networkx_labels(
            G, pos,
            font_size=8,
            font_weight='bold',
            ax=ax
        )
        
        # Create legend for node colors
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Proved'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Unproven')
        ]
        
        # Add area colors to legend
        for i, area in enumerate(areas.keys()):
            if i < len(area_colors):  # Safety check
                legend_elements.append(
                    Line2D([0], [0], color=area_colors[i], lw=2, label=f'Area: {area}')
                )
        
        ax.legend(handles=legend_elements, loc='upper right')
        ax.set_title('Theorem Dependency Network')
        ax.axis('off')
        
        return fig
    
    def visualize_benchmark_results(self, result: BenchmarkResult) -> Dict[str, str]:
        """
        Create visualizations for benchmark results.
        
        Args:
            result: The benchmark result to visualize
            
        Returns:
            Dictionary mapping visualization name to file path
        """
        output_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        benchmark_id = result.benchmark_id.split('_')[0]  # Get base name
        
        # 1. Overall performance metrics
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Plot 1: Coverage by complexity
        categories = list(result.success_by_complexity.keys())
        values = list(result.success_by_complexity.values())
        
        bars = ax1.bar(categories, [v * 100 for v in values], color=['green', 'orange', 'red'])
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax1.set_ylim(0, 100)
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_title(f'Theorem Proving Success Rate by Complexity - {benchmark_id}')
        ax1.grid(True, linestyle='--', alpha=0.3, axis='y')
        
        # Plot 2: Proof time by complexity
        # Group data by complexity category
        proof_times_by_complexity = {"easy": [], "medium": [], "hard": []}
        
        for theorem_id, data in result.theorem_results.items():
            if data["success"]:
                category = data["complexity_category"]
                if category in proof_times_by_complexity:
                    proof_times_by_complexity[category].append(data["proof_time"])
        
        # Create boxplots
        boxplot_data = [proof_times_by_complexity[cat] for cat in categories if proof_times_by_complexity[cat]]
        boxplot_labels = [cat for cat in categories if proof_times_by_complexity[cat]]
        
        if any(boxplot_data):
            ax2.boxplot(boxplot_data, labels=boxplot_labels, patch_artist=True,
                       boxprops=dict(facecolor='lightblue'),
                       medianprops=dict(color='red'))
            ax2.set_ylabel('Proof Time (seconds)')
            ax2.set_title('Proof Time by Theorem Complexity')
            ax2.grid(True, linestyle='--', alpha=0.3, axis='y')
        else:
            ax2.text(0.5, 0.5, 'No successful proofs available for time analysis',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, fontsize=14)
        
        plt.tight_layout()
        file_path = self.save_figure(fig, f"benchmark_{benchmark_id}_performance_{timestamp}.png")
        output_files["overall_performance"] = file_path
        
        # 2. Theorem area analysis
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Group theorems by area
        areas = {}
        for theorem_id, data in result.theorem_results.items():
            area = data["area"]
            if area not in areas:
                areas[area] = {"total": 0, "proved": 0}
            
            areas[area]["total"] += 1
            if data["success"]:
                areas[area]["proved"] += 1
        
        # Calculate coverage percentage
        area_names = list(areas.keys())
        coverage_percentages = [
            (areas[area]["proved"] / areas[area]["total"]) * 100 if areas[area]["total"] > 0 else 0
            for area in area_names
        ]
        
        # Sort by coverage (descending)
        sorted_indices = np.argsort(coverage_percentages)[::-1]
        sorted_areas = [area_names[i] for i in sorted_indices]
        sorted_percentages = [coverage_percentages[i] for i in sorted_indices]
        
        # Create stacked bar chart
        total_counts = [areas[area]["total"] for area in sorted_areas]
        proved_counts = [areas[area]["proved"] for area in sorted_areas]
        unproved_counts = [total - proved for total, proved in zip(total_counts, proved_counts)]
        
        ax.bar(sorted_areas, proved_counts, label='Proved', color='green')
        ax.bar(sorted_areas, unproved_counts, bottom=proved_counts, label='Unproved', color='red')
        
        # Add coverage percentage labels
        for i, (area, percentage) in enumerate(zip(sorted_areas, sorted_percentages)):
            ax.annotate(f'{percentage:.1f}%',
                       xy=(i, total_counts[i] + 0.1),
                       ha='center', va='bottom')
        
        ax.set_ylabel('Theorem Count')
        ax.set_title(f'Theorem Coverage by Area - {benchmark_id}')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        file_path = self.save_figure(fig, f"benchmark_{benchmark_id}_areas_{timestamp}.png")
        output_files["area_analysis"] = file_path
        
        # 3. Population evolution (if available)
        if "diversity_history" in result.population_metrics:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
            
            # Generation numbers
            generations = range(len(result.population_metrics["diversity_history"]))
            
            # Plot fitness history
            if "best_fitness_history" in result.population_metrics and "avg_fitness_history" in result.population_metrics:
                best_fitness = result.population_metrics["best_fitness_history"]
                avg_fitness = result.population_metrics["avg_fitness_history"]
                
                if best_fitness and avg_fitness:
                    ax1.plot(generations, best_fitness, 'g-', linewidth=2, label='Best Fitness')
                    ax1.plot(generations, avg_fitness, 'b-', linewidth=2, label='Average Fitness')
                    ax1.set_ylabel('Fitness Score')
                    ax1.set_title(f'Population Fitness Evolution - {benchmark_id}')
                    ax1.legend()
                    ax1.grid(True, linestyle='--', alpha=0.7)
            
            # Plot diversity history
            diversity = result.population_metrics["diversity_history"]
            if diversity:
                ax2.plot(generations, diversity, 'r-', linewidth=2)
                ax2.set_xlabel('Generation')
                ax2.set_ylabel('Diversity Score')
                ax2.set_title('Population Genetic Diversity')
                ax2.grid(True, linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            file_path = self.save_figure(fig, f"benchmark_{benchmark_id}_evolution_{timestamp}.png")
            output_files["population_evolution"] = file_path
        
        return output_files
    
    def visualize_benchmark_comparison(self, results: List[BenchmarkResult]) -> Dict[str, str]:
        """
        Create visualizations comparing multiple benchmark results.
        
        Args:
            results: List of benchmark results to compare
            
        Returns:
            Dictionary mapping visualization name to file path
        """
        if not results:
            return {}
        
        output_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Overall coverage comparison
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data
        benchmark_ids = [r.benchmark_id.split('_')[0] for r in results]  # Get base names
        coverage_percentages = [r.coverage_percentage * 100 for r in results]
        
        # Sort by coverage (descending)
        sorted_indices = np.argsort(coverage_percentages)[::-1]
        sorted_benchmarks = [benchmark_ids[i] for i in sorted_indices]
        sorted_percentages = [coverage_percentages[i] for i in sorted_indices]
        
        # Create bar chart
        bars = ax.bar(sorted_benchmarks, sorted_percentages, color='skyblue')
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
        
        ax.set_ylim(0, 100)
        ax.set_ylabel('Coverage Percentage (%)')
        ax.set_title('Theorem Coverage Comparison Across Benchmark Runs')
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        file_path = self.save_figure(fig, f"benchmark_comparison_coverage_{timestamp}.png")
        output_files["coverage_comparison"] = file_path
        
        # 2. Complexity success rate comparison
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Prepare data for complexity success rates
        complexity_categories = ["easy", "medium", "hard"]
        x = np.arange(len(benchmark_ids))
        width = 0.25
        
        # Extract data
        easy_success = [r.success_by_complexity.get("easy", 0) * 100 for r in results]
        medium_success = [r.success_by_complexity.get("medium", 0) * 100 for r in results]
        hard_success = [r.success_by_complexity.get("hard", 0) * 100 for r in results]
        
        # Create grouped bar chart
        ax.bar(x - width, easy_success, width, label='Easy', color='green')
        ax.bar(x, medium_success, width, label='Medium', color='orange')
        ax.bar(x + width, hard_success, width, label='Hard', color='red')
        
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Success Rate by Theorem Complexity Across Benchmark Runs')
        ax.set_xticks(x)
        ax.set_xticklabels(benchmark_ids)
        ax.legend()
        ax.set_ylim(0, 100)
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        file_path = self.save_figure(fig, f"benchmark_comparison_complexity_{timestamp}.png")
        output_files["complexity_comparison"] = file_path
        
        # 3. Proof time comparison
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data
        avg_proof_times = [r.avg_proof_time for r in results]
        
        # Sort by proof time (ascending)
        sorted_indices = np.argsort(avg_proof_times)
        sorted_benchmarks = [benchmark_ids[i] for i in sorted_indices]
        sorted_times = [avg_proof_times[i] for i in sorted_indices]
        
        # Create bar chart
        bars = ax.bar(sorted_benchmarks, sorted_times, color='lightgreen')
        
        # Add time labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}s',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
        
        ax.set_ylabel('Average Proof Time (seconds)')
        ax.set_title('Average Proof Time Comparison Across Benchmark Runs')
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        file_path = self.save_figure(fig, f"benchmark_comparison_time_{timestamp}.png")
        output_files["time_comparison"] = file_path
        
        return output_files