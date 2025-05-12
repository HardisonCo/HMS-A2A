"""
Visualization module for clinical trial abstractions and relationships.

This module provides visualizations for the abstractions and relationships
identified in clinical trial data.
"""
import json
import logging
import os
import base64
from typing import Dict, List, Any, Optional, Union
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure matplotlib to use a non-interactive backend
matplotlib.use('Agg')

class AbstractionVisualizer:
    """
    Class for generating visualizations of clinical trial abstractions and relationships.
    """
    
    def __init__(self, output_dir="output/visualizations"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory for saving visualizations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Initialized AbstractionVisualizer with output_dir={output_dir}")
        
        # Set custom color palette for better visualization
        self.colors = list(mcolors.TABLEAU_COLORS.values())
    
    def visualize_abstractions(self, abstraction_results):
        """
        Generate visualizations for the abstractions.
        
        Args:
            abstraction_results: Results from abstraction analysis
            
        Returns:
            Dictionary of visualization paths
        """
        if not abstraction_results:
            logger.warning("No abstraction results provided for visualization")
            return {}
            
        visualizations = {}
        
        # Create abstraction categories chart
        visualizations["abstraction_categories"] = self._create_abstraction_categories_chart(
            abstraction_results.get("abstractions", [])
        )
        
        # Create abstraction relationship graph
        if "relationships" in abstraction_results:
            visualizations["relationship_graph"] = self._create_relationship_graph(
                abstraction_results.get("abstractions", []),
                abstraction_results.get("relationships", {}).get("details", [])
            )
            
        # Create biomarker response heatmap
        if "biomarker_patterns" in abstraction_results:
            visualizations["biomarker_heatmap"] = self._create_biomarker_heatmap(
                abstraction_results.get("biomarker_patterns", [])
            )
            
        logger.info(f"Generated {len(visualizations)} visualizations")
        return visualizations
    
    def generate_html_report(self, abstraction_results, output_path):
        """
        Generate an HTML report for the abstraction results.
        
        Args:
            abstraction_results: Results from abstraction analysis
            output_path: Path to save the HTML report
            
        Returns:
            Path to the generated report
        """
        logger.info(f"Generating HTML report at {output_path}")
        
        # Generate visualizations
        visualizations = self.visualize_abstractions(abstraction_results)
        
        # Prepare HTML content
        html_content = self._generate_html_content(abstraction_results, visualizations)
        
        # Write HTML file
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        logger.info(f"HTML report generated at {output_path}")
        return output_path
    
    def _create_abstraction_categories_chart(self, abstractions):
        """
        Create a chart showing abstraction categories.
        
        Args:
            abstractions: List of abstraction dictionaries
            
        Returns:
            Path to the saved visualization
        """
        # Identify categories based on keyword matching
        categories = {
            "Biomarker": [],
            "Treatment": [],
            "Trial Design": [],
            "Data Processing": [],
            "Visualization": [],
            "Other": []
        }
        
        for i, abstraction in enumerate(abstractions):
            name = abstraction.get("name", "")
            description = abstraction.get("description", "")
            
            if any(term in name.lower() or term in description.lower() 
                   for term in ["biomarker", "genetic", "gene", "variant", "marker"]):
                categories["Biomarker"].append(i)
            elif any(term in name.lower() or term in description.lower() 
                     for term in ["treatment", "medication", "therapy", "drug"]):
                categories["Treatment"].append(i)
            elif any(term in name.lower() or term in description.lower() 
                     for term in ["trial", "adaptive", "protocol", "randomization"]):
                categories["Trial Design"].append(i)
            elif any(term in name.lower() or term in description.lower() 
                     for term in ["data", "process", "transform", "normalize"]):
                categories["Data Processing"].append(i)
            elif any(term in name.lower() or term in description.lower() 
                     for term in ["visual", "dashboard", "chart", "plot", "graph"]):
                categories["Visualization"].append(i)
            else:
                categories["Other"].append(i)
        
        # Filter out empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        labels = list(categories.keys())
        sizes = [len(v) for v in categories.values()]
        colors = self.colors[:len(categories)]
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        plt.title("Abstraction Categories")
        
        # Save visualization
        output_path = os.path.join(self.output_dir, "abstraction_categories.png")
        plt.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"Created abstraction categories chart at {output_path}")
        return output_path
    
    def _create_relationship_graph(self, abstractions, relationships):
        """
        Create a graph visualization of the relationships between abstractions.
        
        Args:
            abstractions: List of abstraction dictionaries
            relationships: List of relationship dictionaries
            
        Returns:
            Path to the saved visualization
        """
        # Create graph
        G = nx.DiGraph()
        
        # Add nodes for each abstraction
        for i, abstraction in enumerate(abstractions):
            G.add_node(i, label=abstraction.get("name", f"Abstraction {i}"))
        
        # Add edges for relationships
        for rel in relationships:
            from_idx = rel.get("from")
            to_idx = rel.get("to")
            label = rel.get("label", "")
            
            if from_idx < len(abstractions) and to_idx < len(abstractions):
                G.add_edge(from_idx, to_idx, label=label)
        
        # Create visualization
        plt.figure(figsize=(12, 10))
        
        # Set positions using spring layout
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color=self.colors[0], alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color=self.colors[2], arrows=True, arrowsize=20)
        
        # Draw node labels
        node_labels = {n: G.nodes[n]['label'] for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_family='sans-serif')
        
        # Draw edge labels
        edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        plt.title("Abstraction Relationships")
        plt.axis('off')
        
        # Save visualization
        output_path = os.path.join(self.output_dir, "relationship_graph.png")
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created relationship graph at {output_path}")
        return output_path
    
    def _create_biomarker_heatmap(self, biomarker_patterns):
        """
        Create a heatmap of biomarker response patterns.
        
        Args:
            biomarker_patterns: List of biomarker pattern dictionaries
            
        Returns:
            Path to the saved visualization
        """
        if not biomarker_patterns:
            return None
            
        # Extract all unique arms
        all_arms = set()
        for pattern in biomarker_patterns:
            all_arms.update(pattern.get("response_by_arm", {}).keys())
        all_arms = sorted(list(all_arms))
        
        # Extract data for heatmap
        cluster_names = []
        data = []
        
        for pattern in biomarker_patterns:
            cluster_names.append(pattern.get("cluster_name", f"Cluster {pattern.get('cluster_id', '')}"))
            
            row = []
            for arm_id in all_arms:
                if arm_id in pattern.get("response_by_arm", {}):
                    row.append(pattern["response_by_arm"][arm_id].get("response_rate", 0) * 100)
                else:
                    row.append(0)
            
            data.append(row)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create heatmap with imshow
        cmap = plt.cm.YlGnBu
        im = ax.imshow(data, cmap=cmap)
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Response Rate (%)", rotation=-90, va="bottom")
        
        # Set ticks and labels
        ax.set_xticks(range(len(all_arms)))
        ax.set_yticks(range(len(cluster_names)))
        ax.set_xticklabels(all_arms)
        ax.set_yticklabels(cluster_names)
        
        # Rotate the x tick labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add title and labels
        ax.set_title("Biomarker Cluster Response by Treatment Arm")
        ax.set_xlabel("Treatment Arm")
        ax.set_ylabel("Biomarker Cluster")
        
        # Add values in the cells
        for i in range(len(cluster_names)):
            for j in range(len(all_arms)):
                text = ax.text(j, i, f"{data[i][j]:.1f}%",
                               ha="center", va="center", color="black" if data[i][j] < 50 else "white")
        
        fig.tight_layout()
        
        # Save visualization
        output_path = os.path.join(self.output_dir, "biomarker_heatmap.png")
        plt.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"Created biomarker heatmap at {output_path}")
        return output_path
    
    def _generate_html_content(self, abstraction_results, visualizations):
        """
        Generate HTML content for the report.
        
        Args:
            abstraction_results: Results from abstraction analysis
            visualizations: Dictionary of visualization paths
            
        Returns:
            HTML content as string
        """
        abstractions = abstraction_results.get("abstractions", [])
        relationships = abstraction_results.get("relationships", {})
        summary = relationships.get("summary", "No summary available")
        
        # Convert visualizations to base64 for embedding
        embedded_visualizations = {}
        for name, path in visualizations.items():
            if path and os.path.exists(path):
                with open(path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    embedded_visualizations[name] = f"data:image/png;base64,{img_data}"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinical Trial Abstraction Analysis</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #f8f9fa;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .visualization {{
            margin: 20px 0;
            text-align: center;
        }}
        .visualization img {{
            max-width: 100%;
            height: auto;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .abstractions {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        .abstraction-card {{
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            background-color: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .relationships {{
            margin-top: 30px;
        }}
        .relationship-item {{
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        .relationship-arrow {{
            margin: 0 10px;
            font-size: 24px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #777;
        }}
    </style>
</head>
<body>
    <h1>Clinical Trial Abstraction Analysis</h1>
    
    <section class="summary">
        <h2>Summary</h2>
        <p>{summary}</p>
    </section>
    
    <section>
        <h2>Visualizations</h2>
        
        <div class="visualization">
            <h3>Abstraction Categories</h3>
            {f'<img src="{embedded_visualizations["abstraction_categories"]}" alt="Abstraction Categories">' if "abstraction_categories" in embedded_visualizations else '<p>No visualization available</p>'}
        </div>
        
        <div class="visualization">
            <h3>Relationship Graph</h3>
            {f'<img src="{embedded_visualizations["relationship_graph"]}" alt="Relationship Graph">' if "relationship_graph" in embedded_visualizations else '<p>No visualization available</p>'}
        </div>
        
        <div class="visualization">
            <h3>Biomarker Response Patterns</h3>
            {f'<img src="{embedded_visualizations["biomarker_heatmap"]}" alt="Biomarker Heatmap">' if "biomarker_heatmap" in embedded_visualizations else '<p>No visualization available</p>'}
        </div>
    </section>
    
    <section>
        <h2>Abstractions ({len(abstractions)})</h2>
        <div class="abstractions">
        """
        
        # Add abstraction cards
        for i, abstraction in enumerate(abstractions):
            html += f"""
            <div class="abstraction-card">
                <h3>{abstraction.get("name", f"Abstraction {i}")}</h3>
                <p>{abstraction.get("description", "No description available")}</p>
            </div>
            """
        
        html += """
        </div>
    </section>
    
    <section class="relationships">
        <h2>Key Relationships</h2>
        """
        
        # Add relationships
        for rel in relationships.get("details", []):
            from_idx = rel.get("from", 0)
            to_idx = rel.get("to", 0)
            
            if from_idx < len(abstractions) and to_idx < len(abstractions):
                from_name = abstractions[from_idx].get("name", f"Abstraction {from_idx}")
                to_name = abstractions[to_idx].get("name", f"Abstraction {to_idx}")
                label = rel.get("label", "relates to")
                
                html += f"""
                <div class="relationship-item">
                    <div><strong>{from_name}</strong></div>
                    <div class="relationship-arrow">→</div>
                    <div><strong>{to_name}</strong></div>
                    <div style="margin-left: 20px; color: #666;">({label})</div>
                </div>
                """
        
        html += """
    </section>
    
    <div class="footer">
        <p>Generated by the Crohn's Treatment System Abstraction Analysis module.</p>
        <p>© 2023 HMS Crohn's Treatment System</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def visualize_biomarker_efficacy(self, analysis_results, clinical_trials, output_path=None):
        """
        Create a visualization of biomarker efficacy across treatments.
        
        Args:
            analysis_results: Results from abstraction analysis
            clinical_trials: Clinical trial data
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the saved visualization or base64 encoded image
        """
        # Extract biomarker patterns
        biomarker_patterns = analysis_results.get("biomarker_patterns", [])
        
        if not biomarker_patterns:
            return None
            
        # Get treatment names from trials
        treatment_names = {}
        for trial in clinical_trials:
            for arm in trial.get("arms", []):
                arm_id = arm.get("armId")
                medication = arm.get("treatment", {}).get("medication", "Unknown")
                dosage = arm.get("treatment", {}).get("dosage", "")
                unit = arm.get("treatment", {}).get("unit", "")
                frequency = arm.get("treatment", {}).get("frequency", "")
                
                if arm_id:
                    treatment_names[arm_id] = f"{medication} {dosage}{unit} {frequency}"
        
        # Prepare data for visualization
        biomarkers = []
        treatments = []
        efficacy_data = []
        
        for pattern in biomarker_patterns:
            cluster_name = pattern.get("cluster_name", "Unknown Cluster")
            
            # Extract biomarker name from cluster name
            biomarker = cluster_name
            for known_biomarker in ["NOD2", "IL23R", "ATG16L1", "IRGM", "LRRK2", "TNF", "IL10", "JAK2", "STAT3"]:
                if known_biomarker in cluster_name:
                    biomarker = known_biomarker
                    break
            
            for arm_id, response_data in pattern.get("response_by_arm", {}).items():
                if arm_id in treatment_names:
                    treatment = treatment_names[arm_id]
                    response_rate = response_data.get("response_rate", 0)
                    significance = response_data.get("significance", "low")
                    
                    biomarkers.append(biomarker)
                    treatments.append(treatment)
                    
                    # Calculate marker size based on significance
                    if significance == "high":
                        size = 200
                    elif significance == "medium":
                        size = 100
                    else:
                        size = 50
                    
                    efficacy_data.append((response_rate, size))
        
        # Create bubble chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create a categorical colormap for biomarkers
        unique_biomarkers = list(set(biomarkers))
        colors = self.colors[:len(unique_biomarkers)]
        color_map = {biomarker: colors[i % len(colors)] for i, biomarker in enumerate(unique_biomarkers)}
        
        # Create bubble chart
        for i in range(len(biomarkers)):
            ax.scatter(
                i, 
                efficacy_data[i][0], 
                s=efficacy_data[i][1], 
                c=[color_map[biomarkers[i]]], 
                alpha=0.7, 
                edgecolors='black', 
                linewidth=1
            )
        
        # Set labels and title
        ax.set_title("Biomarker Treatment Response by Efficacy")
        ax.set_xlabel("Treatment-Biomarker Pairs")
        ax.set_ylabel("Response Rate")
        
        # Set x-axis ticks
        labels = [f"{biomarkers[i]}\n{treatments[i]}" for i in range(len(biomarkers))]
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        
        # Set y-axis limits
        ax.set_ylim(0, 1.0)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
        
        # Add legend for biomarkers
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                          label=biomarker,
                          markerfacecolor=color, markersize=10)
                  for biomarker, color in color_map.items()]
        ax.legend(handles=legend_elements, title="Biomarkers", loc="upper right")
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save or return visualization
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, bbox_inches='tight')
            plt.close(fig)
            logger.info(f"Created biomarker efficacy visualization at {output_path}")
            return output_path
        else:
            # Return as base64 encoded image
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            plt.close(fig)
            buffer.seek(0)
            img_data = base64.b64encode(buffer.read()).decode('utf-8')
            return f"data:image/png;base64,{img_data}"