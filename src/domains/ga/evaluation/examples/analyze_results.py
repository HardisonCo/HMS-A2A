#!/usr/bin/env python3
"""
Example script for analyzing theorem proving benchmark results.

This script demonstrates how to:
1. Load and analyze benchmark results
2. Create comparative visualizations
3. Generate detailed performance reports
4. Identify improvement opportunities
"""

import os
import sys
import argparse
from pathlib import Path
import json
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import networkx as nx

# Add parent directory to path for importing
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from genetic_theorem_prover.evaluation import (
    BenchmarkResult, PerformanceVisualizer
)


def load_benchmark_results(results_dir, limit=None):
    """Load benchmark results from a directory."""
    # Find all result JSON files
    result_files = glob.glob(os.path.join(results_dir, "benchmark_*.json"))
    
    # Sort by modification time (newest first)
    result_files.sort(key=os.path.getmtime, reverse=True)
    
    # Limit number of results if requested
    if limit and len(result_files) > limit:
        result_files = result_files[:limit]
    
    # Load results
    results = []
    for file_path in result_files:
        try:
            result = BenchmarkResult.load(file_path)
            results.append(result)
            print(f"Loaded benchmark result: {result.benchmark_id} ({result.timestamp})")
        except Exception as e:
            print(f"Error loading result from {file_path}: {e}")
    
    print(f"Loaded {len(results)} benchmark results")
    return results


def create_comparison_visualizations(results, output_dir):
    """Create comparison visualizations for multiple benchmark results."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create visualizer
    visualizer = PerformanceVisualizer(output_dir=output_dir)
    
    # Create visualizations
    visualization_files = visualizer.visualize_benchmark_comparison(results)
    
    print("Comparison visualizations saved to:")
    for viz_name, file_path in visualization_files.items():
        print(f"  - {viz_name}: {file_path}")
    
    return visualization_files


def analyze_theorem_difficulty(results):
    """Analyze theorem difficulty based on success rates across benchmarks."""
    # Collect success data for each theorem
    theorem_data = {}
    
    for result in results:
        for theorem_id, data in result.theorem_results.items():
            if theorem_id not in theorem_data:
                theorem_data[theorem_id] = {
                    "attempts": 0,
                    "successes": 0,
                    "area": data.get("area", "unknown"),
                    "complexity": data.get("complexity", 0.5),
                    "avg_proof_time": [],
                    "benchmark_ids": []
                }
            
            theorem_data[theorem_id]["attempts"] += 1
            theorem_data[theorem_id]["benchmark_ids"].append(result.benchmark_id)
            
            if data.get("success", False):
                theorem_data[theorem_id]["successes"] += 1
                
                if "proof_time" in data:
                    theorem_data[theorem_id]["avg_proof_time"].append(data["proof_time"])
    
    # Calculate success rate and average proof time
    for theorem_id, data in theorem_data.items():
        data["success_rate"] = data["successes"] / data["attempts"] if data["attempts"] > 0 else 0.0
        data["avg_proof_time"] = (sum(data["avg_proof_time"]) / len(data["avg_proof_time"])) 
                               if data["avg_proof_time"] else None
        
        # Estimate actual difficulty based on success rate and expected complexity
        expected_complexity = data["complexity"]
        actual_success_rate = data["success_rate"]
        
        # Invert success rate and normalize to 0-1 scale
        empirical_difficulty = 1.0 - actual_success_rate
        
        # Combine expected and empirical difficulty
        data["estimated_difficulty"] = 0.3 * expected_complexity + 0.7 * empirical_difficulty
    
    # Sort theorems by estimated difficulty (descending)
    sorted_theorems = sorted(theorem_data.items(), key=lambda x: x[1]["estimated_difficulty"], reverse=True)
    
    # Create result
    result = {
        "hardest_theorems": [
            {
                "id": theorem_id,
                "success_rate": data["success_rate"],
                "attempts": data["attempts"],
                "area": data["area"],
                "expected_complexity": data["complexity"],
                "estimated_difficulty": data["estimated_difficulty"],
                "avg_proof_time": data["avg_proof_time"]
            }
            for theorem_id, data in sorted_theorems[:10]  # Top 10 hardest
        ],
        "easiest_theorems": [
            {
                "id": theorem_id,
                "success_rate": data["success_rate"],
                "attempts": data["attempts"],
                "area": data["area"],
                "expected_complexity": data["complexity"],
                "estimated_difficulty": data["estimated_difficulty"],
                "avg_proof_time": data["avg_proof_time"]
            }
            for theorem_id, data in sorted_theorems[-10:]  # Top 10 easiest (reversed)
        ],
        "difficulty_by_area": {}
    }
    
    # Calculate average difficulty by area
    area_difficulties = {}
    for theorem_id, data in theorem_data.items():
        area = data["area"]
        if area not in area_difficulties:
            area_difficulties[area] = []
        
        area_difficulties[area].append(data["estimated_difficulty"])
    
    # Calculate average
    for area, difficulties in area_difficulties.items():
        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 0.0
        result["difficulty_by_area"][area] = avg_difficulty
    
    return result


def analyze_system_improvements(results):
    """Analyze performance trends and suggest improvements."""
    # Sort results by timestamp
    sorted_results = sorted(results, key=lambda r: r.timestamp)
    
    # Extract key performance metrics over time
    performance_over_time = {
        "timestamps": [r.timestamp for r in sorted_results],
        "coverage": [r.coverage_percentage for r in sorted_results],
        "avg_proof_time": [r.avg_proof_time for r in sorted_results],
        "success_by_complexity": {
            "easy": [r.success_by_complexity.get("easy", 0.0) for r in sorted_results],
            "medium": [r.success_by_complexity.get("medium", 0.0) for r in sorted_results],
            "hard": [r.success_by_complexity.get("hard", 0.0) for r in sorted_results]
        },
        "configurations": [r.system_config for r in sorted_results]
    }
    
    # Calculate trends
    trends = {}
    if len(sorted_results) >= 2:
        # Coverage trend
        coverage_values = performance_over_time["coverage"]
        if len(coverage_values) >= 2:
            coverage_change = coverage_values[-1] - coverage_values[0]
            coverage_percent_change = (coverage_change / coverage_values[0]) * 100 if coverage_values[0] > 0 else 0.0
            trends["coverage"] = {
                "direction": "improving" if coverage_change > 0 else "declining" if coverage_change < 0 else "stable",
                "change": coverage_change,
                "percent_change": coverage_percent_change
            }
        
        # Proof time trend
        proof_times = performance_over_time["avg_proof_time"]
        if len(proof_times) >= 2 and all(t is not None for t in proof_times):
            time_change = proof_times[-1] - proof_times[0]
            time_percent_change = (time_change / proof_times[0]) * 100 if proof_times[0] > 0 else 0.0
            trends["proof_time"] = {
                "direction": "improving" if time_change < 0 else "declining" if time_change > 0 else "stable",
                "change": time_change,
                "percent_change": time_percent_change
            }
        
        # Success by complexity trends
        for complexity, values in performance_over_time["success_by_complexity"].items():
            if len(values) >= 2:
                change = values[-1] - values[0]
                percent_change = (change / values[0]) * 100 if values[0] > 0 else 0.0
                trends[f"{complexity}_success"] = {
                    "direction": "improving" if change > 0 else "declining" if change < 0 else "stable",
                    "change": change,
                    "percent_change": percent_change
                }
    
    # Analyze configuration changes that improved performance
    config_impact = []
    if len(sorted_results) >= 3:  # Need at least 3 results for meaningful analysis
        for i in range(1, len(sorted_results)):
            prev_result = sorted_results[i-1]
            curr_result = sorted_results[i]
            
            # Compare performance
            coverage_change = curr_result.coverage_percentage - prev_result.coverage_percentage
            
            # If performance improved, analyze configuration differences
            if coverage_change > 0.05:  # 5% improvement threshold
                # Compare configurations
                prev_config = prev_result.system_config
                curr_config = curr_result.system_config
                
                # Find differences
                differences = {}
                for key in set(prev_config.keys()) | set(curr_config.keys()):
                    if key in prev_config and key in curr_config:
                        if prev_config[key] != curr_config[key]:
                            differences[key] = {
                                "from": prev_config[key],
                                "to": curr_config[key]
                            }
                    elif key in curr_config:
                        differences[key] = {
                            "from": None,
                            "to": curr_config[key]
                        }
                    elif key in prev_config:
                        differences[key] = {
                            "from": prev_config[key],
                            "to": None
                        }
                
                if differences:
                    config_impact.append({
                        "from_benchmark": prev_result.benchmark_id,
                        "to_benchmark": curr_result.benchmark_id,
                        "coverage_improvement": coverage_change,
                        "configuration_changes": differences
                    })
    
    # Generate improvement suggestions
    suggestions = []
    
    # Suggestion 1: Based on trends
    if "coverage" in trends:
        if trends["coverage"]["direction"] == "declining":
            suggestions.append({
                "priority": "high",
                "area": "overall_performance",
                "suggestion": "Overall theorem coverage is declining. Consider reviewing recent configuration changes "
                             "and reverting to previous successful configurations."
            })
    
    # Suggestion 2: Based on complexity performance
    if "hard_success" in trends and trends["hard_success"]["direction"] == "declining":
        suggestions.append({
            "priority": "medium",
            "area": "hard_theorems",
            "suggestion": "Performance on hard theorems is declining. Consider increasing population size, "
                         "adding more specialized agents, or extending evolution time for complex theorems."
        })
    
    # Suggestion 3: Based on proof time trends
    if "proof_time" in trends and trends["proof_time"]["direction"] == "declining":
        suggestions.append({
            "priority": "medium",
            "area": "efficiency",
            "suggestion": "Proof generation time is increasing. Consider optimizing agent evaluation, "
                         "implementing early stopping for unpromising approaches, or adjusting "
                         "theorem decomposition strategies."
        })
    
    # Suggestion 4: Based on configuration impact
    if config_impact:
        positive_changes = {}
        for impact in config_impact:
            for param, change in impact["configuration_changes"].items():
                if param not in positive_changes:
                    positive_changes[param] = []
                positive_changes[param].append({
                    "change": change,
                    "improvement": impact["coverage_improvement"]
                })
        
        # Suggest parameters that consistently improved performance
        for param, changes in positive_changes.items():
            if len(changes) >= 2:  # Parameter changed multiple times with positive impact
                suggestions.append({
                    "priority": "high",
                    "area": "configuration",
                    "suggestion": f"Adjusting '{param}' has consistently improved performance. "
                                 f"Consider further experiments with this parameter."
                })
    
    # Return consolidated analysis
    return {
        "performance_over_time": performance_over_time,
        "trends": trends,
        "configuration_impact": config_impact,
        "improvement_suggestions": suggestions
    }


def generate_detailed_report(results, theorem_analysis, system_analysis, output_file):
    """Generate a detailed performance report."""
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create report
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "results_analyzed": len(results),
        "result_summaries": [
            {
                "benchmark_id": r.benchmark_id,
                "timestamp": r.timestamp,
                "theorems_total": r.theorems_total,
                "theorems_proved": r.theorems_proved,
                "coverage_percentage": r.coverage_percentage,
                "avg_proof_time": r.avg_proof_time,
                "success_by_complexity": r.success_by_complexity
            }
            for r in results
        ],
        "theorem_difficulty_analysis": theorem_analysis,
        "system_performance_analysis": system_analysis
    }
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Detailed report saved to: {output_file}")
    return report


def create_report_visualizations(theorem_analysis, system_analysis, output_dir):
    """Create visualizations for the performance report."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Theorem difficulty by area
    fig, ax = plt.subplots(figsize=(12, 8))
    
    areas = list(theorem_analysis["difficulty_by_area"].keys())
    difficulties = list(theorem_analysis["difficulty_by_area"].values())
    
    # Sort by difficulty (descending)
    sorted_indices = np.argsort(difficulties)[::-1]
    sorted_areas = [areas[i] for i in sorted_indices]
    sorted_difficulties = [difficulties[i] for i in sorted_indices]
    
    # Create bar chart
    bars = ax.bar(sorted_areas, sorted_difficulties, color='skyblue')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Estimated Difficulty (0-1)')
    ax.set_title('Theorem Difficulty by Area')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save figure
    difficulty_file = os.path.join(output_dir, "theorem_difficulty_by_area.png")
    plt.savefig(difficulty_file)
    plt.close()
    
    # 2. Performance trends over time
    if "performance_over_time" in system_analysis and system_analysis["performance_over_time"]["timestamps"]:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
        
        timestamps = system_analysis["performance_over_time"]["timestamps"]
        # Convert to simpler format for display
        display_dates = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%m/%d %H:%M") 
                         for ts in timestamps]
        
        # Plot 1: Coverage
        coverage = system_analysis["performance_over_time"]["coverage"]
        ax1.plot(display_dates, [c * 100 for c in coverage], 'b-o', linewidth=2)
        ax1.set_ylabel('Coverage (%)')
        ax1.set_title('Theorem Coverage Over Time')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot 2: Proof time
        proof_times = system_analysis["performance_over_time"]["avg_proof_time"]
        if all(t is not None for t in proof_times):
            ax2.plot(display_dates, proof_times, 'g-o', linewidth=2)
            ax2.set_ylabel('Avg Proof Time (s)')
            ax2.set_title('Average Proof Time Over Time')
            ax2.grid(True, linestyle='--', alpha=0.7)
        else:
            ax2.text(0.5, 0.5, 'Insufficient proof time data',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, fontsize=14)
        
        # Plot 3: Success by complexity
        success_by_complexity = system_analysis["performance_over_time"]["success_by_complexity"]
        
        if "easy" in success_by_complexity and "medium" in success_by_complexity and "hard" in success_by_complexity:
            ax3.plot(display_dates, [s * 100 for s in success_by_complexity["easy"]], 'g-o', linewidth=2, label='Easy')
            ax3.plot(display_dates, [s * 100 for s in success_by_complexity["medium"]], 'y-o', linewidth=2, label='Medium')
            ax3.plot(display_dates, [s * 100 for s in success_by_complexity["hard"]], 'r-o', linewidth=2, label='Hard')
            ax3.set_ylabel('Success Rate (%)')
            ax3.set_title('Success Rate by Complexity Over Time')
            ax3.legend()
            ax3.grid(True, linestyle='--', alpha=0.7)
        else:
            ax3.text(0.5, 0.5, 'Insufficient complexity data',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax3.transAxes, fontsize=14)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save figure
        trends_file = os.path.join(output_dir, "performance_trends.png")
        plt.savefig(trends_file)
        plt.close()
    
    # Return file paths of created visualizations
    return {
        "theorem_difficulty": difficulty_file,
        "performance_trends": trends_file if "performance_over_time" in system_analysis else None
    }


def main():
    """Main function for analyzing theorem proving benchmark results."""
    parser = argparse.ArgumentParser(description="Analyze genetic theorem proving benchmark results")
    parser.add_argument("--results-dir", default="./benchmark_results", 
                        help="Directory containing benchmark results")
    parser.add_argument("--output-dir", default="./analysis_results", 
                        help="Directory to store analysis results")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of results to analyze (default: all)")
    parser.add_argument("--report-file", default="performance_report.json",
                        help="File to store the detailed performance report")
    
    args = parser.parse_args()
    
    # Load benchmark results
    results = load_benchmark_results(args.results_dir, args.limit)
    
    if not results:
        print("No benchmark results found. Exiting.")
        return
    
    # Create comparison visualizations
    visualizations_dir = os.path.join(args.output_dir, "visualizations")
    visualization_files = create_comparison_visualizations(results, visualizations_dir)
    
    # Analyze theorem difficulty
    theorem_analysis = analyze_theorem_difficulty(results)
    
    print("\nTheorem Difficulty Analysis:")
    print("\nHardest Theorems:")
    for theorem in theorem_analysis["hardest_theorems"][:5]:  # Show top 5
        print(f"  - {theorem['id']}: Estimated Difficulty={theorem['estimated_difficulty']:.2f}, "
              f"Success Rate={theorem['success_rate']:.2f}")
    
    print("\nDifficulty by Area:")
    for area, difficulty in sorted(theorem_analysis["difficulty_by_area"].items(), 
                                  key=lambda x: x[1], reverse=True):
        print(f"  - {area}: {difficulty:.2f}")
    
    # Analyze system improvements
    system_analysis = analyze_system_improvements(results)
    
    print("\nSystem Performance Analysis:")
    
    if "trends" in system_analysis:
        print("\nPerformance Trends:")
        for metric, trend in system_analysis["trends"].items():
            print(f"  - {metric}: {trend['direction']} "
                  f"({trend['percent_change']:+.1f}%)")
    
    if "improvement_suggestions" in system_analysis and system_analysis["improvement_suggestions"]:
        print("\nImprovement Suggestions:")
        for suggestion in system_analysis["improvement_suggestions"]:
            print(f"  - [{suggestion['priority'].upper()}] {suggestion['suggestion']}")
    
    # Generate detailed report
    report_path = os.path.join(args.output_dir, args.report_file)
    report = generate_detailed_report(results, theorem_analysis, system_analysis, report_path)
    
    # Create report visualizations
    report_viz_dir = os.path.join(args.output_dir, "report_visualizations")
    report_viz_files = create_report_visualizations(theorem_analysis, system_analysis, report_viz_dir)
    
    print("\nReport visualizations saved to:")
    for viz_name, file_path in report_viz_files.items():
        if file_path:
            print(f"  - {viz_name}: {file_path}")
    
    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()