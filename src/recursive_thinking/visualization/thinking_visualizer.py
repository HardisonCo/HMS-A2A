import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import seaborn as sns
from ..types import RecursiveThinkingStats, ThinkingStep

class ThinkingVisualizer:
    """
    Visualization module for the recursive thinking process.
    
    Provides tools to visualize:
    - Thinking process flow
    - Performance metrics
    - Step-by-step improvements
    - Token usage and efficiency
    """
    
    def __init__(self, output_dir: str = "visualization_output"):
        """
        Initialize the visualizer
        
        Args:
            output_dir: Directory to save visualization files
        """
        self.output_dir = output_dir
        self.thinking_history: List[RecursiveThinkingStats] = []
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set default style for plots
        sns.set_style("whitegrid")
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
        plt.rcParams['axes.titlepad'] = 20
        
    def add_thinking_stats(self, stats: RecursiveThinkingStats) -> None:
        """
        Add a thinking process stat to the history
        
        Args:
            stats: Statistics from a recursive thinking process
        """
        self.thinking_history.append(stats)
    
    def add_thinking_stats_from_json(self, json_path: str) -> None:
        """
        Load thinking stats from a JSON file
        
        Args:
            json_path: Path to JSON file with thinking stats
        """
        with open(json_path, 'r') as file:
            data = json.load(file)
            
            # Convert JSON data to RecursiveThinkingStats
            for item in data:
                steps = []
                for step_data in item.get('steps', []):
                    step = ThinkingStep(
                        description=step_data.get('description', ''),
                        input=step_data.get('input', ''),
                        output=step_data.get('output', ''),
                        tokens=step_data.get('tokens', 0),
                        executionTime=step_data.get('executionTime', 0)
                    )
                    steps.append(step)
                
                stats = RecursiveThinkingStats(
                    input=item.get('input', ''),
                    steps=steps,
                    totalTokens=item.get('totalTokens', 0),
                    executionTime=item.get('executionTime', 0),
                    improvementScore=item.get('improvementScore', 0)
                )
                
                self.thinking_history.append(stats)
    
    def visualize_thinking_process(self, thinking_id: int = -1, save: bool = True) -> Optional[plt.Figure]:
        """
        Visualize a specific thinking process
        
        Args:
            thinking_id: ID of the thinking process (-1 for latest)
            save: Whether to save the visualization to file
            
        Returns:
            Matplotlib figure object if save is False, None otherwise
        """
        if not self.thinking_history:
            print("No thinking history available")
            return None
        
        # Get the thinking process to visualize
        thinking_index = thinking_id if thinking_id >= 0 else len(self.thinking_history) - 1
        if thinking_index >= len(self.thinking_history):
            print(f"Thinking ID {thinking_id} not found in history")
            return None
            
        thinking = self.thinking_history[thinking_index]
        
        # Create a figure with subplots
        fig = plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(4, 4, figure=fig)
        
        # Upper section: Thinking flow
        ax_flow = fig.add_subplot(gs[0:2, :])
        
        # Lower left: Execution time by step
        ax_time = fig.add_subplot(gs[2:, :2])
        
        # Lower right: Token usage by step
        ax_tokens = fig.add_subplot(gs[2:, 2:])
        
        # Create thinking flow diagram
        self._plot_thinking_flow(thinking, ax_flow)
        
        # Plot execution time by step
        self._plot_execution_time(thinking, ax_time)
        
        # Plot token usage by step
        self._plot_token_usage(thinking, ax_tokens)
        
        # Add title and layout adjustments
        fig.suptitle(f"Recursive Thinking Process Visualization", fontsize=16, weight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        
        if save:
            # Save figure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"thinking_process_{thinking_index}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"Saved visualization to: {filepath}")
            return None
        else:
            return fig
    
    def visualize_metrics_dashboard(self, save: bool = True) -> Optional[plt.Figure]:
        """
        Create a comprehensive dashboard of thinking metrics
        
        Args:
            save: Whether to save the visualization to file
            
        Returns:
            Matplotlib figure object if save is False, None otherwise
        """
        if not self.thinking_history:
            print("No thinking history available")
            return None
        
        # Create figure with subplots
        fig = plt.figure(figsize=(15, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig)
        
        # Subplots
        ax_improvement = fig.add_subplot(gs[0, 0])  # Improvement scores
        ax_tokens = fig.add_subplot(gs[0, 1])       # Token usage
        ax_time = fig.add_subplot(gs[0, 2])         # Execution time
        ax_steps = fig.add_subplot(gs[1, 0])        # Step counts
        ax_efficiency = fig.add_subplot(gs[1, 1:])  # Efficiency (tokens/sec)
        ax_correlation = fig.add_subplot(gs[2, :])  # Correlation matrix
        
        # Plot each component
        self._plot_improvement_scores(ax_improvement)
        self._plot_token_distribution(ax_tokens)
        self._plot_execution_time_distribution(ax_time)
        self._plot_step_count_distribution(ax_steps)
        self._plot_efficiency_trend(ax_efficiency)
        self._plot_correlation_matrix(ax_correlation)
        
        # Add title and layout adjustments
        fig.suptitle("Recursive Thinking Metrics Dashboard", fontsize=16, weight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        
        if save:
            # Save figure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"thinking_metrics_dashboard_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"Saved metrics dashboard to: {filepath}")
            return None
        else:
            return fig
    
    def visualize_improvement_progress(self, thinking_id: int = -1, save: bool = True) -> Optional[plt.Figure]:
        """
        Visualize the step-by-step improvement in a thinking process
        
        Args:
            thinking_id: ID of the thinking process (-1 for latest)
            save: Whether to save the visualization to file
            
        Returns:
            Matplotlib figure object if save is False, None otherwise
        """
        if not self.thinking_history:
            print("No thinking history available")
            return None
        
        # Get the thinking process to visualize
        thinking_index = thinking_id if thinking_id >= 0 else len(self.thinking_history) - 1
        if thinking_index >= len(self.thinking_history):
            print(f"Thinking ID {thinking_id} not found in history")
            return None
            
        thinking = self.thinking_history[thinking_index]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract improvement data
        improvement_scores = []
        step_labels = []
        
        for i, step in enumerate(thinking.steps):
            # For simplicity, use a random improvement score for demonstration
            # In a real implementation, you would calculate actual improvement between steps
            if i == 0:
                # First step can't have improvement, use 0
                improvement = 0
            else:
                # Calculate string similarity or use other metrics to measure improvement
                # For now, use a placeholder based on token count differences
                prev_tokens = thinking.steps[i-1].tokens
                curr_tokens = step.tokens
                # Simple placeholder metric: normalized token difference
                improvement = (curr_tokens - prev_tokens) / max(prev_tokens, 1) * 0.5 + 0.5
                
            improvement_scores.append(improvement)
            step_labels.append(f"Step {i+1}")
        
        # Plot improvement progression
        ax.plot(step_labels, improvement_scores, marker='o', linewidth=2, markersize=8)
        
        # Add a horizontal line at y=0.5 (neutral improvement)
        ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
        
        # Highlight significant improvements
        for i, score in enumerate(improvement_scores):
            if score > 0.7:  # Threshold for "significant" improvement
                ax.annotate("Significant\nimprovement", 
                           (i, score), 
                           xytext=(i, score + 0.15),
                           arrowprops=dict(arrowstyle="->", color="green"),
                           ha='center')
            elif score < 0.3:  # Threshold for regression
                ax.annotate("Regression", 
                           (i, score), 
                           xytext=(i, score - 0.15),
                           arrowprops=dict(arrowstyle="->", color="red"),
                           ha='center')
        
        # Add titles and labels
        ax.set_title("Step-by-Step Improvement in Thinking Process", fontsize=14, pad=20)
        ax.set_xlabel("Thinking Steps", fontsize=12)
        ax.set_ylabel("Improvement Score (relative to previous step)", fontsize=12)
        
        # Set y-axis limits with some padding
        ax.set_ylim(-0.1, 1.1)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add final score annotation
        final_score = thinking.improvementScore
        ax.text(0.02, 0.97, f"Overall Improvement Score: {final_score:.2f}", 
                transform=ax.transAxes, fontsize=12, 
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        plt.tight_layout()
        
        if save:
            # Save figure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"thinking_improvement_{thinking_index}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"Saved improvement visualization to: {filepath}")
            return None
        else:
            return fig
    
    def export_metrics_summary(self) -> Dict[str, Any]:
        """
        Export a summary of thinking metrics as a dictionary
        
        Returns:
            Dictionary with metrics summary
        """
        if not self.thinking_history:
            return {"error": "No thinking history available"}
        
        # Calculate statistics
        total_processes = len(self.thinking_history)
        
        # Get average step count
        step_counts = [len(thinking.steps) for thinking in self.thinking_history]
        avg_step_count = sum(step_counts) / total_processes
        
        # Get token usage stats
        tokens = [thinking.totalTokens for thinking in self.thinking_history]
        avg_tokens = sum(tokens) / total_processes
        max_tokens = max(tokens)
        min_tokens = min(tokens)
        
        # Get execution time stats
        execution_times = [thinking.executionTime for thinking in self.thinking_history]
        avg_execution_time = sum(execution_times) / total_processes
        max_execution_time = max(execution_times)
        min_execution_time = min(execution_times)
        
        # Get improvement score stats
        improvement_scores = [thinking.improvementScore for thinking in self.thinking_history]
        avg_improvement = sum(improvement_scores) / total_processes
        max_improvement = max(improvement_scores)
        min_improvement = min(improvement_scores)
        
        # Calculate efficiency (tokens per second)
        efficiency = avg_tokens / (avg_execution_time / 1000) if avg_execution_time > 0 else 0
        
        # Create summary
        return {
            "totalThinkingProcesses": total_processes,
            "stepCounts": {
                "average": avg_step_count,
                "min": min(step_counts),
                "max": max(step_counts)
            },
            "tokenUsage": {
                "average": avg_tokens,
                "min": min_tokens,
                "max": max_tokens,
                "total": sum(tokens)
            },
            "executionTime": {
                "average": avg_execution_time,  # in milliseconds
                "min": min_execution_time,
                "max": max_execution_time,
                "total": sum(execution_times)
            },
            "improvementScores": {
                "average": avg_improvement,
                "min": min_improvement,
                "max": max_improvement
            },
            "efficiency": {
                "tokensPerSecond": efficiency
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def save_metrics_summary(self, filename: str = "thinking_metrics_summary.json") -> str:
        """
        Save metrics summary to a JSON file
        
        Args:
            filename: Name of the output file
            
        Returns:
            Path to the saved file
        """
        summary = self.export_metrics_summary()
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as file:
            json.dump(summary, file, indent=2)
            
        print(f"Saved metrics summary to: {filepath}")
        return filepath
    
    def clear_history(self) -> None:
        """Clear the thinking history"""
        self.thinking_history = []
    
    def _plot_thinking_flow(self, thinking: RecursiveThinkingStats, ax: plt.Axes) -> None:
        """Plot the thinking flow diagram"""
        num_steps = len(thinking.steps)
        
        # Create node positions
        pos_x = np.linspace(0.1, 0.9, num_steps)
        pos_y = np.ones(num_steps) * 0.5
        
        # Draw nodes
        for i, (x, y) in enumerate(zip(pos_x, pos_y)):
            # Node color based on execution time (normalized)
            exec_times = [step.executionTime for step in thinking.steps]
            max_time = max(exec_times) if max(exec_times) > 0 else 1
            norm_time = thinking.steps[i].executionTime / max_time
            node_color = plt.cm.YlOrRd(norm_time)
            
            # Draw node
            circle = plt.Circle((x, y), 0.05, color=node_color, alpha=0.8)
            ax.add_patch(circle)
            
            # Add step number
            ax.text(x, y, str(i+1), ha='center', va='center', fontsize=10, 
                   weight='bold', color='white')
            
            # Add step description
            description = thinking.steps[i].description
            # Truncate if too long
            if len(description) > 50:
                description = description[:47] + "..."
                
            ax.text(x, y - 0.1, description, ha='center', va='top', fontsize=8,
                   wrap=True, bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
            
            # Draw arrow to next node
            if i < num_steps - 1:
                ax.annotate("", xy=(pos_x[i+1], pos_y[i+1]), xytext=(x, y),
                          arrowprops=dict(arrowstyle="->", color="gray"))
        
        # Remove axes and set limits
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Add title
        ax.set_title("Recursive Thinking Process Flow", fontsize=14, pad=20)
        
        # Add input snippet at the start
        input_text = thinking.input
        if len(input_text) > 100:
            input_text = input_text[:97] + "..."
        ax.text(0.1, 0.85, f"Input: {input_text}", fontsize=8, 
               bbox=dict(facecolor='lightyellow', alpha=0.7, boxstyle='round,pad=0.3'))
        
        # Add final result at the end
        if thinking.steps:
            final_output = thinking.steps[-1].output
            if len(final_output) > 100:
                final_output = final_output[:97] + "..."
            ax.text(0.9, 0.85, f"Result: {final_output}", fontsize=8, ha='right',
                   bbox=dict(facecolor='lightgreen', alpha=0.7, boxstyle='round,pad=0.3'))
        
        # Add execution summary
        ax.text(0.5, 0.05, f"Total Execution Time: {thinking.executionTime:.2f}ms | "
                          f"Total Tokens: {thinking.totalTokens} | "
                          f"Improvement Score: {thinking.improvementScore:.2f}",
               ha='center', fontsize=10, 
               bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
    
    def _plot_execution_time(self, thinking: RecursiveThinkingStats, ax: plt.Axes) -> None:
        """Plot execution time for each step"""
        steps = list(range(1, len(thinking.steps) + 1))
        times = [step.executionTime for step in thinking.steps]
        
        # Create bar chart
        bars = ax.bar(steps, times, color='skyblue', alpha=0.7)
        
        # Add value labels above bars
        for bar, time in zip(bars, times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f"{time:.0f}ms", ha='center', va='bottom', fontsize=8)
        
        # Add titles and labels
        ax.set_title("Execution Time by Step", fontsize=12)
        ax.set_xlabel("Step Number", fontsize=10)
        ax.set_ylabel("Execution Time (ms)", fontsize=10)
        
        # Add grid
        ax.grid(axis='y', alpha=0.3)
        
        # Set y-axis to start at 0
        ylim = ax.get_ylim()
        ax.set_ylim([0, ylim[1] * 1.15])  # Add 15% padding at the top
    
    def _plot_token_usage(self, thinking: RecursiveThinkingStats, ax: plt.Axes) -> None:
        """Plot token usage for each step"""
        steps = list(range(1, len(thinking.steps) + 1))
        tokens = [step.tokens for step in thinking.steps]
        
        # Create bar chart
        bars = ax.bar(steps, tokens, color='lightgreen', alpha=0.7)
        
        # Add value labels above bars
        for bar, token in zip(bars, tokens):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f"{token}", ha='center', va='bottom', fontsize=8)
        
        # Add titles and labels
        ax.set_title("Token Usage by Step", fontsize=12)
        ax.set_xlabel("Step Number", fontsize=10)
        ax.set_ylabel("Tokens", fontsize=10)
        
        # Add grid
        ax.grid(axis='y', alpha=0.3)
        
        # Set y-axis to start at 0
        ylim = ax.get_ylim()
        ax.set_ylim([0, ylim[1] * 1.15])  # Add 15% padding at the top
    
    def _plot_improvement_scores(self, ax: plt.Axes) -> None:
        """Plot distribution of improvement scores"""
        scores = [thinking.improvementScore for thinking in self.thinking_history]
        
        # Create histogram
        ax.hist(scores, bins=10, color='blue', alpha=0.7, edgecolor='black')
        
        # Add vertical line for average
        avg_score = sum(scores) / len(scores)
        ax.axvline(avg_score, color='red', linestyle='--', linewidth=1.5)
        ax.text(avg_score, ax.get_ylim()[1] * 0.9, f" Avg: {avg_score:.2f}", 
               color='red', ha='left', va='top', fontsize=8)
        
        # Add titles and labels
        ax.set_title("Improvement Score Distribution", fontsize=12)
        ax.set_xlabel("Improvement Score", fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)
        
        # Add grid
        ax.grid(alpha=0.3)
    
    def _plot_token_distribution(self, ax: plt.Axes) -> None:
        """Plot distribution of token usage"""
        tokens = [thinking.totalTokens for thinking in self.thinking_history]
        
        # Create histogram
        ax.hist(tokens, bins=10, color='green', alpha=0.7, edgecolor='black')
        
        # Add vertical line for average
        avg_tokens = sum(tokens) / len(tokens)
        ax.axvline(avg_tokens, color='red', linestyle='--', linewidth=1.5)
        ax.text(avg_tokens, ax.get_ylim()[1] * 0.9, f" Avg: {avg_tokens:.0f}", 
               color='red', ha='left', va='top', fontsize=8)
        
        # Add titles and labels
        ax.set_title("Token Usage Distribution", fontsize=12)
        ax.set_xlabel("Total Tokens", fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)
        
        # Add grid
        ax.grid(alpha=0.3)
    
    def _plot_execution_time_distribution(self, ax: plt.Axes) -> None:
        """Plot distribution of execution times"""
        times = [thinking.executionTime for thinking in self.thinking_history]
        
        # Create histogram
        ax.hist(times, bins=10, color='orange', alpha=0.7, edgecolor='black')
        
        # Add vertical line for average
        avg_time = sum(times) / len(times)
        ax.axvline(avg_time, color='red', linestyle='--', linewidth=1.5)
        ax.text(avg_time, ax.get_ylim()[1] * 0.9, f" Avg: {avg_time:.0f}ms", 
               color='red', ha='left', va='top', fontsize=8)
        
        # Add titles and labels
        ax.set_title("Execution Time Distribution", fontsize=12)
        ax.set_xlabel("Execution Time (ms)", fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)
        
        # Add grid
        ax.grid(alpha=0.3)
    
    def _plot_step_count_distribution(self, ax: plt.Axes) -> None:
        """Plot distribution of step counts"""
        step_counts = [len(thinking.steps) for thinking in self.thinking_history]
        
        # Create histogram
        ax.hist(step_counts, bins=max(len(set(step_counts)), 5), color='purple', alpha=0.7, edgecolor='black')
        
        # Add vertical line for average
        avg_steps = sum(step_counts) / len(step_counts)
        ax.axvline(avg_steps, color='red', linestyle='--', linewidth=1.5)
        ax.text(avg_steps, ax.get_ylim()[1] * 0.9, f" Avg: {avg_steps:.1f}", 
               color='red', ha='left', va='top', fontsize=8)
        
        # Add titles and labels
        ax.set_title("Step Count Distribution", fontsize=12)
        ax.set_xlabel("Number of Steps", fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)
        
        # Add grid
        ax.grid(alpha=0.3)
    
    def _plot_efficiency_trend(self, ax: plt.Axes) -> None:
        """Plot efficiency (tokens per second) trend"""
        if not self.thinking_history:
            return
            
        # Calculate tokens per second for each thinking process
        process_ids = list(range(1, len(self.thinking_history) + 1))
        efficiencies = []
        
        for thinking in self.thinking_history:
            execution_time_sec = thinking.executionTime / 1000  # convert ms to seconds
            if execution_time_sec > 0:
                efficiency = thinking.totalTokens / execution_time_sec
            else:
                efficiency = 0
            efficiencies.append(efficiency)
        
        # Plot trend line
        ax.plot(process_ids, efficiencies, marker='o', linestyle='-', color='blue', alpha=0.7)
        
        # Add moving average
        window_size = min(5, len(efficiencies))
        if window_size > 1:
            moving_avgs = []
            for i in range(len(efficiencies)):
                if i < window_size - 1:
                    # Not enough data for full window
                    window_avg = sum(efficiencies[:i+1]) / (i+1)
                else:
                    # Full window
                    window_avg = sum(efficiencies[i-window_size+1:i+1]) / window_size
                moving_avgs.append(window_avg)
            
            ax.plot(process_ids, moving_avgs, linestyle='--', color='red', 
                   alpha=0.8, label=f"{window_size}-process Moving Avg")
        
        # Add titles and labels
        ax.set_title("Efficiency Trend (Tokens per Second)", fontsize=12)
        ax.set_xlabel("Process ID", fontsize=10)
        ax.set_ylabel("Tokens per Second", fontsize=10)
        
        # Add grid
        ax.grid(alpha=0.3)
        
        # Add legend if we have a moving average
        if window_size > 1:
            ax.legend(fontsize=8)
        
        # Set y-axis to start at 0
        ax.set_ylim(bottom=0)
    
    def _plot_correlation_matrix(self, ax: plt.Axes) -> None:
        """Plot correlation matrix of various metrics"""
        if not self.thinking_history:
            return
            
        # Extract metrics
        step_counts = [len(thinking.steps) for thinking in self.thinking_history]
        tokens = [thinking.totalTokens for thinking in self.thinking_history]
        times = [thinking.executionTime for thinking in self.thinking_history]
        scores = [thinking.improvementScore for thinking in self.thinking_history]
        
        # Calculate tokens per step
        tokens_per_step = [t / max(s, 1) for t, s in zip(tokens, step_counts)]
        
        # Create correlation matrix data
        data = np.array([step_counts, tokens, times, scores, tokens_per_step]).T
        corr_matrix = np.corrcoef(data, rowvar=False)
        
        # Create labels
        labels = ['Step Count', 'Total Tokens', 'Exec Time', 'Improvement', 'Tokens/Step']
        
        # Plot heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f",
                   xticklabels=labels, yticklabels=labels, ax=ax)
        
        # Add title
        ax.set_title("Correlation Matrix of Thinking Metrics", fontsize=12)
        
        # Adjust tick labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        plt.setp(ax.get_yticklabels(), rotation=0)


class ThinkingProcessDiagram:
    """
    Generate diagrams of the recursive thinking process.
    
    Creates flow diagrams showing:
    - The sequence of thinking steps
    - Transformations between steps
    - Key improvements and annotations
    """
    
    def __init__(self, output_dir: str = "visualization_output"):
        """
        Initialize the diagram generator
        
        Args:
            output_dir: Directory to save diagram files
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_thinking_diagram(self, stats: RecursiveThinkingStats, 
                                 filename: Optional[str] = None) -> str:
        """
        Generate a Mermaid diagram for a thinking process
        
        Args:
            stats: Statistics from a recursive thinking process
            filename: Optional custom filename
            
        Returns:
            Path to the generated diagram file
        """
        # Create Mermaid diagram code
        mermaid_code = self._create_mermaid_diagram(stats)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"thinking_diagram_{timestamp}.md"
        
        # Ensure it has .md extension
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Write to file
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as file:
            file.write(mermaid_code)
        
        print(f"Generated thinking diagram at: {filepath}")
        return filepath
    
    def _create_mermaid_diagram(self, stats: RecursiveThinkingStats) -> str:
        """
        Create a Mermaid flowchart diagram for a thinking process
        
        Args:
            stats: Statistics from a recursive thinking process
            
        Returns:
            Mermaid diagram code as string
        """
        # Start building the Mermaid diagram
        lines = [
            "# Recursive Thinking Process Diagram",
            "",
            "```mermaid",
            "flowchart TD",
            "    %% Node style definitions",
            "    classDef stepNode fill:#f9f9f9,stroke:#333,stroke-width:1px,color:black,font-weight:bold;",
            "    classDef inputNode fill:#e6f7ff,stroke:#1890ff,stroke-width:1px;",
            "    classDef outputNode fill:#f6ffed,stroke:#52c41a,stroke-width:1px;",
            "    classDef improvementNode fill:#fff2e8,stroke:#fa8c16,stroke-width:1px;",
            ""
        ]
        
        # Add input node
        input_text = self._truncate_text(stats.input, 50)
        lines.append(f"    input[\"Input: {input_text}\"]")
        
        # Add thinking steps
        for i, step in enumerate(stats.steps):
            step_desc = self._truncate_text(step.description, 40)
            step_id = f"step{i+1}"
            lines.append(f"    {step_id}[\"{step_desc}\"]")
            
            # Add output for each step if relevant
            if step.output:
                output_text = self._truncate_text(step.output, 50)
                output_id = f"output{i+1}"
                lines.append(f"    {output_id}(\"{output_text}\")")
                lines.append(f"    {step_id} --> {output_id}")
                
                # Add metrics as notes
                lines.append(f"    {output_id} -- \"Tokens: {step.tokens}\" --> metrics{i+1}")
                lines.append(f"    metrics{i+1}[\"Time: {step.executionTime}ms\"]:::improvementNode")
            
            # Add class for styling
            lines.append(f"    class {step_id} stepNode;")
            if i+1 < len(stats.steps):
                next_step_id = f"step{i+2}"
                lines.append(f"    {step_id} --> {next_step_id}")
        
        # Connect input to first step
        lines.append(f"    input --> step1")
        
        # Add class for styling input
        lines.append(f"    class input inputNode;")
        
        # Add overall metrics
        lines.append(f"    subgraph metrics [\"Overall Metrics\"]")
        lines.append(f"        totalTime[\"Total Execution Time: {stats.executionTime}ms\"]")
        lines.append(f"        totalTokens[\"Total Tokens: {stats.totalTokens}\"]")
        lines.append(f"        improvementScore[\"Improvement Score: {stats.improvementScore:.2f}\"]")
        lines.append(f"    end")
        
        # Close the diagram
        lines.append("```")
        
        return "\n".join(lines)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text for the diagram
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if not text:
            return ""
            
        # Remove newlines and escape quotes
        text = text.replace("\n", " ").replace("\"", "'")
        
        if len(text) <= max_length:
            return text
            
        return text[:max_length-3] + "..."


# Convenience function to create the visualizer
def create_visualizer(output_dir: str = "visualization_output") -> ThinkingVisualizer:
    """
    Create a thinking visualizer
    
    Args:
        output_dir: Directory to save visualization files
        
    Returns:
        ThinkingVisualizer instance
    """
    return ThinkingVisualizer(output_dir)


# Convenience function to create the diagram generator
def create_diagram_generator(output_dir: str = "visualization_output") -> ThinkingProcessDiagram:
    """
    Create a thinking process diagram generator
    
    Args:
        output_dir: Directory to save diagram files
        
    Returns:
        ThinkingProcessDiagram instance
    """
    return ThinkingProcessDiagram(output_dir)