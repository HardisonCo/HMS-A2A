#!/usr/bin/env python3
"""
Deal Visualization Tools

This module provides MCP-compliant tools for visualizing deals and collaboration
structures in different formats, including text, JSON, DOT (Graphviz), and SVG.
"""

import os
import sys
import json
import uuid
import logging
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import networkx as nx
from enum import Enum
import io
import base64

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specialized_agents.collaboration.deals import Deal, Problem, Solution, Player, Transaction
from specialized_agents.tools.tool_interface import (
    tool_decorator, 
    ToolCategory,
    ToolContext,
    BaseMCPTool
)

# Configure logging
logger = logging.getLogger(__name__)


class VisualizationFormat(str, Enum):
    """Supported visualization formats."""
    TEXT = "text"
    JSON = "json"
    DOT = "dot"
    SVG = "svg"
    MERMAID = "mermaid"


class DealVisualizationInput(BaseModel):
    """Input schema for visualizing a deal."""
    deal_dict: Dict[str, Any]
    format: VisualizationFormat = VisualizationFormat.TEXT
    include_metadata: bool = False
    highlight_nodes: Optional[List[str]] = None
    theme: str = "default"


class NodeHighlightInput(BaseModel):
    """Input schema for highlighted nodes in a visualization."""
    deal_dict: Dict[str, Any]
    node_ids: List[str]
    highlight_color: str = "yellow"
    format: VisualizationFormat = VisualizationFormat.DOT


class PathHighlightInput(BaseModel):
    """Input schema for highlighting paths in a deal graph."""
    deal_dict: Dict[str, Any]
    start_node: str
    end_node: str
    format: VisualizationFormat = VisualizationFormat.DOT
    path_color: str = "red"


class GraphMetricsInput(BaseModel):
    """Input schema for calculating graph metrics."""
    deal_dict: Dict[str, Any]
    metrics: List[str] = ["centrality", "density", "diameter"]


@tool_decorator(
    name="visualize_deal_graph",
    description="Generate a visualization of a deal graph in multiple formats",
    tool_type="collaboration",
    collaboration_type="visualization",
    domains=["agent_collaboration", "deal_making", "visualization"],
    standards=["DealFramework", "VisualizationStandards"],
    tags=["deal", "visualization", "graph"],
    require_human_review=False
)
def visualize_deal_graph(
    deal_dict: Dict[str, Any],
    format: str = "text",
    include_metadata: bool = False,
    highlight_nodes: Optional[List[str]] = None,
    theme: str = "default",
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Generate a visualization of a deal graph in multiple formats.
    
    Args:
        deal_dict: Dictionary representation of a Deal
        format: Format of the visualization (text, json, dot, svg, mermaid)
        include_metadata: Whether to include detailed metadata in the visualization
        highlight_nodes: Optional list of node IDs to highlight
        theme: Visual theme to apply (default, light, dark, colorful)
        context: Tool execution context
        
    Returns:
        Visualization result in the specified format
    """
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Get the graph from the deal
    graph = deal.graph
    
    # Apply theme colors
    node_colors = _get_theme_colors(theme)
    
    visualization = None
    
    if format == "text":
        visualization = _text_visualization(deal, graph, include_metadata, highlight_nodes)
    elif format == "json":
        visualization = _json_visualization(deal, graph, include_metadata, highlight_nodes)
    elif format == "dot":
        visualization = _dot_visualization(deal, graph, node_colors, highlight_nodes)
    elif format == "svg":
        try:
            # First generate DOT format
            dot_string = _dot_visualization(deal, graph, node_colors, highlight_nodes)
            
            # Try to use graphviz to convert to SVG if available
            visualization = _convert_dot_to_svg(dot_string)
        except Exception as e:
            logger.error(f"Error converting to SVG: {str(e)}")
            # Fallback to DOT format
            visualization = _dot_visualization(deal, graph, node_colors, highlight_nodes)
            format = "dot"  # Update format to reflect what we actually returned
    elif format == "mermaid":
        visualization = _mermaid_visualization(deal, graph, node_colors, highlight_nodes)
    else:
        raise ValueError(f"Unsupported visualization format: {format}")
    
    # Return result with appropriate type based on format
    if format == "json":
        return visualization
    else:
        return {"visualization": visualization, "format": format}


@tool_decorator(
    name="highlight_deal_nodes",
    description="Create a visualization with specific nodes highlighted",
    tool_type="collaboration",
    collaboration_type="visualization",
    domains=["agent_collaboration", "deal_making", "visualization"],
    standards=["DealFramework", "VisualizationStandards"],
    tags=["deal", "visualization", "highlight"],
    require_human_review=False
)
def highlight_deal_nodes(
    deal_dict: Dict[str, Any],
    node_ids: List[str],
    highlight_color: str = "yellow",
    format: str = "dot",
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Create a visualization with specific nodes highlighted.
    
    Args:
        deal_dict: Dictionary representation of a Deal
        node_ids: List of node IDs to highlight
        highlight_color: Color to use for highlighting
        format: Format of the visualization (dot, svg, mermaid)
        context: Tool execution context
        
    Returns:
        Visualization with highlighted nodes
    """
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Get the graph from the deal
    graph = deal.graph
    
    # Verify node IDs exist in the graph
    existing_nodes = []
    for node_id in node_ids:
        if node_id in graph:
            existing_nodes.append(node_id)
        else:
            logger.warning(f"Node ID {node_id} not found in the graph")
    
    # Create visualization with highlighting
    visualization = None
    
    if format == "dot":
        # Generate DOT with custom node attributes for highlighting
        visualization = _dot_visualization(
            deal, 
            graph, 
            _get_theme_colors("default"),
            existing_nodes,
            highlight_color
        )
    elif format == "svg":
        try:
            # First generate DOT format with highlighting
            dot_string = _dot_visualization(
                deal, 
                graph, 
                _get_theme_colors("default"),
                existing_nodes,
                highlight_color
            )
            
            # Convert to SVG
            visualization = _convert_dot_to_svg(dot_string)
        except Exception as e:
            logger.error(f"Error converting to SVG: {str(e)}")
            # Fallback to DOT format
            visualization = _dot_visualization(
                deal, 
                graph, 
                _get_theme_colors("default"),
                existing_nodes,
                highlight_color
            )
            format = "dot"  # Update format to reflect what we actually returned
    elif format == "mermaid":
        visualization = _mermaid_visualization(
            deal, 
            graph, 
            _get_theme_colors("default"),
            existing_nodes,
            highlight_color
        )
    else:
        raise ValueError(f"Unsupported highlight format: {format}")
    
    return {"visualization": visualization, "format": format, "highlighted_nodes": existing_nodes}


@tool_decorator(
    name="highlight_deal_path",
    description="Create a visualization with a path between nodes highlighted",
    tool_type="collaboration",
    collaboration_type="visualization",
    domains=["agent_collaboration", "deal_making", "visualization"],
    standards=["DealFramework", "VisualizationStandards"],
    tags=["deal", "visualization", "path"],
    require_human_review=False
)
def highlight_deal_path(
    deal_dict: Dict[str, Any],
    start_node: str,
    end_node: str,
    format: str = "dot",
    path_color: str = "red",
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Create a visualization with a path between nodes highlighted.
    
    Args:
        deal_dict: Dictionary representation of a Deal
        start_node: ID of the starting node
        end_node: ID of the ending node
        format: Format of the visualization (dot, svg, mermaid)
        path_color: Color to use for highlighting the path
        context: Tool execution context
        
    Returns:
        Visualization with highlighted path
    """
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Get the graph from the deal
    graph = deal.graph
    
    # Verify nodes exist
    if start_node not in graph:
        raise ValueError(f"Start node {start_node} not found in the graph")
    
    if end_node not in graph:
        raise ValueError(f"End node {end_node} not found in the graph")
    
    # Find shortest path between nodes
    try:
        path = nx.shortest_path(graph, start_node, end_node)
    except nx.NetworkXNoPath:
        return {
            "error": f"No path exists between {start_node} and {end_node}",
            "format": format
        }
    
    # Get path edges
    path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
    
    # Create visualization with highlighted path
    visualization = None
    
    if format == "dot":
        # Generate DOT with custom edge attributes for highlighting
        visualization = _dot_visualization_with_path(
            deal, 
            graph, 
            path,
            path_edges,
            _get_theme_colors("default"),
            path_color
        )
    elif format == "svg":
        try:
            # First generate DOT format with highlighting
            dot_string = _dot_visualization_with_path(
                deal, 
                graph, 
                path,
                path_edges,
                _get_theme_colors("default"),
                path_color
            )
            
            # Convert to SVG
            visualization = _convert_dot_to_svg(dot_string)
        except Exception as e:
            logger.error(f"Error converting to SVG: {str(e)}")
            # Fallback to DOT format
            visualization = _dot_visualization_with_path(
                deal, 
                graph, 
                path,
                path_edges,
                _get_theme_colors("default"),
                path_color
            )
            format = "dot"  # Update format to reflect what we actually returned
    elif format == "mermaid":
        visualization = _mermaid_visualization_with_path(
            deal, 
            graph, 
            path,
            path_edges,
            _get_theme_colors("default"),
            path_color
        )
    else:
        raise ValueError(f"Unsupported highlight format: {format}")
    
    return {
        "visualization": visualization, 
        "format": format, 
        "path": path,
        "path_length": len(path) - 1
    }


@tool_decorator(
    name="calculate_deal_graph_metrics",
    description="Calculate metrics for a deal graph",
    tool_type="collaboration",
    collaboration_type="analytics",
    domains=["agent_collaboration", "deal_making", "analytics"],
    standards=["DealFramework", "AnalyticsStandards"],
    tags=["deal", "analytics", "metrics", "graph"],
    require_human_review=False
)
def calculate_deal_graph_metrics(
    deal_dict: Dict[str, Any],
    metrics: List[str] = ["centrality", "density", "diameter"],
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Calculate metrics for a deal graph.
    
    Args:
        deal_dict: Dictionary representation of a Deal
        metrics: List of metrics to calculate
        context: Tool execution context
        
    Returns:
        Calculated metrics
    """
    # Reconstruct the Deal object from dict
    deal = Deal.from_dict(deal_dict)
    
    # Get the graph from the deal
    graph = deal.graph
    
    # Calculate requested metrics
    result = {
        "deal_id": deal_dict.get("id", "unknown"),
        "deal_name": deal.name,
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "metrics": {}
    }
    
    # Node type counts
    node_types = {}
    for node, data in graph.nodes(data=True):
        node_type = data.get("type", "unknown")
        if node_type not in node_types:
            node_types[node_type] = 0
        node_types[node_type] += 1
    
    result["node_types"] = node_types
    
    # Calculate additional metrics
    if "density" in metrics:
        result["metrics"]["density"] = nx.density(graph)
    
    if "diameter" in metrics:
        try:
            # Convert to undirected for diameter calculation
            undirected_graph = graph.to_undirected()
            
            # Check if graph is connected
            if nx.is_connected(undirected_graph):
                result["metrics"]["diameter"] = nx.diameter(undirected_graph)
            else:
                # Get diameter of largest connected component
                largest_cc = max(nx.connected_components(undirected_graph), key=len)
                subgraph = undirected_graph.subgraph(largest_cc)
                result["metrics"]["diameter"] = nx.diameter(subgraph)
                result["metrics"]["connected"] = False
                result["metrics"]["components"] = nx.number_connected_components(undirected_graph)
        except Exception as e:
            logger.warning(f"Error calculating diameter: {str(e)}")
            result["metrics"]["diameter"] = "Error: Could not calculate"
    
    if "centrality" in metrics:
        try:
            # Calculate degree centrality
            degree_centrality = nx.degree_centrality(graph)
            
            # Find most central nodes
            top_central_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            
            central_nodes = []
            for node_id, centrality in top_central_nodes:
                node_data = graph.nodes[node_id]
                central_nodes.append({
                    "id": node_id,
                    "type": node_data.get("type", "unknown"),
                    "name": node_data.get("name", node_id),
                    "centrality": centrality
                })
            
            result["metrics"]["central_nodes"] = central_nodes
        except Exception as e:
            logger.warning(f"Error calculating centrality: {str(e)}")
            result["metrics"]["central_nodes"] = "Error: Could not calculate"
    
    if "clustering" in metrics:
        try:
            # Convert to undirected for clustering calculation
            undirected_graph = graph.to_undirected()
            result["metrics"]["avg_clustering"] = nx.average_clustering(undirected_graph)
        except Exception as e:
            logger.warning(f"Error calculating clustering: {str(e)}")
            result["metrics"]["avg_clustering"] = "Error: Could not calculate"
    
    return result


# Helper functions for visualization

def _text_visualization(
    deal: Deal, 
    graph: nx.DiGraph, 
    include_metadata: bool, 
    highlight_nodes: Optional[List[str]]
) -> str:
    """Generate a text visualization of a deal graph."""
    output = []
    output.append(f"DEAL: {deal.name}")
    output.append(f"Description: {deal.description}")
    output.append(f"Status: {deal.status}")
    output.append(f"Domains: {', '.join(deal.domains)}")
    
    if include_metadata and deal.metadata:
        output.append("\nMETADATA:")
        for key, value in deal.metadata.items():
            output.append(f"  - {key}: {value}")
    
    output.append("\nPLAYERS:")
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'player':
            name = data.get('name', node)
            highlighted = " [HIGHLIGHTED]" if highlight_nodes and node in highlight_nodes else ""
            output.append(f"  - {name} ({data.get('role', 'unknown')}){highlighted}")
            if include_metadata and "capabilities" in data:
                output.append(f"    Capabilities: {', '.join(data.get('capabilities', []))}")
    
    output.append("\nPROBLEMS:")
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'problem':
            name = data.get('name', node)
            highlighted = " [HIGHLIGHTED]" if highlight_nodes and node in highlight_nodes else ""
            output.append(f"  - {name}{highlighted}")
            output.append(f"    Description: {data.get('description', '')}")
            
            if data.get('constraints'):
                output.append(f"    Constraints: {', '.join(data.get('constraints'))}")
            
            if data.get('success_criteria'):
                output.append(f"    Success Criteria: {', '.join(data.get('success_criteria'))}")
            
            # Find owner if exists
            for s, t, d in graph.edges(data=True):
                if t == node and d.get('relationship') == 'owns':
                    owner = graph.nodes[s].get('name')
                    output.append(f"    Owner: {owner}")
    
    output.append("\nSOLUTIONS:")
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'solution':
            name = data.get('name', node)
            highlighted = " [HIGHLIGHTED]" if highlight_nodes and node in highlight_nodes else ""
            output.append(f"  - {name}{highlighted}")
            output.append(f"    Description: {data.get('description', '')}")
            output.append(f"    Approach: {data.get('approach', '')}")
            
            if data.get('status'):
                output.append(f"    Status: {data.get('status')}")
            
            # Find problem it solves
            for s, t, d in graph.edges(data=True):
                if s == node and d.get('relationship') == 'solves':
                    problem = graph.nodes[t].get('name')
                    output.append(f"    Solves: {problem}")
            
            # Find who proposed it
            for s, t, d in graph.edges(data=True):
                if t == node and d.get('relationship') == 'proposed':
                    proposer = graph.nodes[s].get('name')
                    output.append(f"    Proposed by: {proposer}")
            
            # Show evaluation if exists
            if 'evaluation' in data:
                eval_data = data['evaluation']
                output.append(f"    Evaluated by: {eval_data.get('evaluator')}")
                output.append(f"    Meets criteria: {eval_data.get('meets_criteria')}")
                output.append(f"    Evaluation notes: {eval_data.get('evaluation_notes')}")
    
    output.append("\nTRANSACTIONS:")
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'transaction':
            name = data.get('name', node)
            highlighted = " [HIGHLIGHTED]" if highlight_nodes and node in highlight_nodes else ""
            output.append(f"  - {data.get('transaction_type')} ({name}){highlighted}")
            output.append(f"    Status: {data.get('status', 'unknown')}")
            output.append(f"    Amount: {data.get('amount')} {data.get('currency', 'USD')}")
            
            # Find sender and receiver
            sender = data.get('from_player')
            receiver = data.get('to_player')
            
            if sender and receiver:
                output.append(f"    From {sender} to {receiver}")
            
            if data.get('description'):
                output.append(f"    Description: {data.get('description')}")
    
    return "\n".join(output)


def _json_visualization(
    deal: Deal, 
    graph: nx.DiGraph, 
    include_metadata: bool, 
    highlight_nodes: Optional[List[str]]
) -> Dict[str, Any]:
    """Generate a JSON visualization of a deal graph."""
    nodes = []
    for node, data in graph.nodes(data=True):
        node_data = {
            "id": node,
            "type": data.get("type"),
            "name": data.get("name", "Unknown"),
            "highlighted": node in highlight_nodes if highlight_nodes else False,
            "data": {}
        }
        
        # Include key attributes based on node type
        if data.get("type") == "player":
            node_data["data"]["role"] = data.get("role", "unknown")
            if "capabilities" in data:
                node_data["data"]["capabilities"] = data.get("capabilities", [])
        
        elif data.get("type") == "problem":
            node_data["data"]["description"] = data.get("description", "")
            if "constraints" in data:
                node_data["data"]["constraints"] = data.get("constraints", [])
            if "success_criteria" in data:
                node_data["data"]["success_criteria"] = data.get("success_criteria", [])
        
        elif data.get("type") == "solution":
            node_data["data"]["description"] = data.get("description", "")
            node_data["data"]["approach"] = data.get("approach", "")
            if "status" in data:
                node_data["data"]["status"] = data.get("status")
            if "evaluation" in data:
                node_data["data"]["evaluation"] = data.get("evaluation")
        
        elif data.get("type") == "transaction":
            node_data["data"]["transaction_type"] = data.get("transaction_type", "unknown")
            node_data["data"]["status"] = data.get("status", "unknown")
            node_data["data"]["amount"] = data.get("amount")
            node_data["data"]["currency"] = data.get("currency", "USD")
            node_data["data"]["from_player"] = data.get("from_player")
            node_data["data"]["to_player"] = data.get("to_player")
        
        # Include all metadata if requested
        if include_metadata:
            for k, v in data.items():
                if k not in ["type", "name"] and k not in node_data["data"]:
                    node_data["data"][k] = v
        
        nodes.append(node_data)
        
    edges = []
    for s, t, data in graph.edges(data=True):
        edge_data = {
            "source": s,
            "target": t,
            "relationship": data.get("relationship", "unknown")
        }
        if include_metadata:
            edge_data["data"] = {k: v for k, v in data.items() if k != "relationship"}
        edges.append(edge_data)
        
    deal_data = {
        "deal_id": deal.id if hasattr(deal, "id") else "unknown",
        "deal_name": deal.name,
        "deal_description": deal.description,
        "deal_status": deal.status,
        "deal_domains": deal.domains,
        "nodes": nodes,
        "edges": edges
    }
    
    if include_metadata:
        deal_data["metadata"] = deal.metadata
    
    return deal_data


def _dot_visualization(
    deal: Deal, 
    graph: nx.DiGraph,
    node_colors: Dict[str, str],
    highlight_nodes: Optional[List[str]] = None,
    highlight_color: str = "yellow"
) -> str:
    """Generate a DOT visualization of a deal graph."""
    lines = ['digraph DealGraph {']
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=box, style=filled, fontname="Arial"];')
    lines.append('  edge [fontname="Arial", fontsize=10];')
    lines.append('  label="Deal: ' + deal.name.replace('"', '\\"') + '";')
    lines.append('  labelloc="t";')
    
    # Add nodes with different colors by type
    for node, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        name = data.get('name', node)
        
        # Determine node color
        if node_type in node_colors:
            color = node_colors[node_type]
        else:
            color = node_colors.get('default', 'white')
        
        # Highlight nodes if requested
        if highlight_nodes and node in highlight_nodes:
            color = highlight_color
        
        # Add status to label if available
        label = name
        if 'status' in data:
            label = f"{name}\\n({data['status']})"
        
        # Escape special characters in label
        label = label.replace('"', '\\"')
        
        # Add node
        lines.append(f'  "{node}" [label="{label}", fillcolor="{color}"];')
    
    # Add edges with labels
    for s, t, data in graph.edges(data=True):
        relationship = data.get('relationship', '')
        
        # Escape special characters in relationship
        relationship = relationship.replace('"', '\\"')
        
        lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
    
    # Group nodes by type
    lines.append('  // Group players')
    lines.append('  subgraph cluster_players {')
    lines.append('    label="Players";')
    lines.append('    style=dotted;')
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'player':
            lines.append(f'    "{node}";')
    lines.append('  }')
    
    lines.append('  // Group problems')
    lines.append('  subgraph cluster_problems {')
    lines.append('    label="Problems";')
    lines.append('    style=dotted;')
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'problem':
            lines.append(f'    "{node}";')
    lines.append('  }')
    
    lines.append('  // Group solutions')
    lines.append('  subgraph cluster_solutions {')
    lines.append('    label="Solutions";')
    lines.append('    style=dotted;')
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'solution':
            lines.append(f'    "{node}";')
    lines.append('  }')
    
    lines.append('  // Group transactions')
    lines.append('  subgraph cluster_transactions {')
    lines.append('    label="Transactions";')
    lines.append('    style=dotted;')
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'transaction':
            lines.append(f'    "{node}";')
    lines.append('  }')
    
    lines.append('}')
    return '\n'.join(lines)


def _dot_visualization_with_path(
    deal: Deal,
    graph: nx.DiGraph,
    path: List[str],
    path_edges: List[tuple],
    node_colors: Dict[str, str],
    path_color: str = "red"
) -> str:
    """Generate a DOT visualization with a highlighted path."""
    lines = ['digraph DealGraph {']
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=box, style=filled, fontname="Arial"];')
    lines.append('  edge [fontname="Arial", fontsize=10];')
    lines.append('  label="Deal: ' + deal.name.replace('"', '\\"') + ' - Path Visualization";')
    lines.append('  labelloc="t";')
    
    # Add nodes with different colors by type
    for node, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        name = data.get('name', node)
        
        # Determine node color
        if node in path:
            # Highlight nodes in the path
            color = path_color
            style = "filled,bold"
        else:
            if node_type in node_colors:
                color = node_colors[node_type]
            else:
                color = node_colors.get('default', 'white')
            style = "filled"
        
        # Add status to label if available
        label = name
        if 'status' in data:
            label = f"{name}\\n({data['status']})"
        
        # Escape special characters in label
        label = label.replace('"', '\\"')
        
        # Add node
        lines.append(f'  "{node}" [label="{label}", fillcolor="{color}", style="{style}"];')
    
    # Add edges with labels
    for s, t, data in graph.edges(data=True):
        relationship = data.get('relationship', '')
        
        # Escape special characters in relationship
        relationship = relationship.replace('"', '\\"')
        
        # Highlight edges in the path
        if (s, t) in path_edges:
            lines.append(f'  "{s}" -> "{t}" [label="{relationship}", color="{path_color}", penwidth=2];')
        else:
            lines.append(f'  "{s}" -> "{t}" [label="{relationship}"];')
    
    # Add legend
    lines.append('  // Legend')
    lines.append('  subgraph cluster_legend {')
    lines.append('    label="Path Legend";')
    lines.append('    style=filled;')
    lines.append('    fillcolor=lightgray;')
    lines.append('    node [style=filled, shape=plaintext];')
    lines.append(f'    "path_node" [label="Path Node", fillcolor="{path_color}"];')
    lines.append('    "other_node" [label="Other Node", fillcolor="lightblue"];')
    lines.append('  }')
    
    lines.append('}')
    return '\n'.join(lines)


def _mermaid_visualization(
    deal: Deal, 
    graph: nx.DiGraph,
    node_colors: Dict[str, str],
    highlight_nodes: Optional[List[str]] = None,
    highlight_color: str = "yellow"
) -> str:
    """Generate a Mermaid visualization of a deal graph."""
    lines = ['```mermaid', 'graph LR']
    
    # Title
    lines.append(f"  title[Deal: {deal.name}]")
    lines.append("  style title fill:#fff,stroke:#fff")
    
    # Add nodes with styling
    for node, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        name = data.get('name', node)
        
        # Escape special characters
        clean_name = name.replace('"', '\\"')
        
        # Determine node color
        if highlight_nodes and node in highlight_nodes:
            color = highlight_color
        elif node_type in node_colors:
            color = node_colors[node_type]
        else:
            color = node_colors.get('default', 'white')
        
        # Add node
        lines.append(f"  {node}[\"{clean_name}\"]")
        
        # Add style
        lines.append(f"  style {node} fill:{color}")
    
    # Add edges with labels
    for s, t, data in graph.edges(data=True):
        relationship = data.get('relationship', '')
        
        # Escape special characters
        clean_relationship = relationship.replace('"', '\\"')
        
        lines.append(f"  {s} -->|{clean_relationship}| {t}")
    
    # Add style definitions
    lines.append("  classDef player fill:lightblue;")
    lines.append("  classDef problem fill:salmon;")
    lines.append("  classDef solution fill:lightgreen;")
    lines.append("  classDef transaction fill:lightyellow;")
    
    # Apply classes
    for node, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        if node_type in ['player', 'problem', 'solution', 'transaction']:
            lines.append(f"  class {node} {node_type};")
    
    lines.append("```")
    return '\n'.join(lines)


def _mermaid_visualization_with_path(
    deal: Deal, 
    graph: nx.DiGraph,
    path: List[str],
    path_edges: List[tuple],
    node_colors: Dict[str, str],
    path_color: str = "red"
) -> str:
    """Generate a Mermaid visualization with a highlighted path."""
    lines = ['```mermaid', 'graph LR']
    
    # Title
    lines.append(f"  title[Deal: {deal.name} - Path Visualization]")
    lines.append("  style title fill:#fff,stroke:#fff")
    
    # Add nodes with styling
    for node, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        name = data.get('name', node)
        
        # Escape special characters
        clean_name = name.replace('"', '\\"')
        
        # Determine node color and style
        if node in path:
            color = path_color
            node_class = "pathNode"
        elif node_type in node_colors:
            color = node_colors[node_type]
            node_class = node_type
        else:
            color = node_colors.get('default', 'white')
            node_class = "default"
        
        # Add node
        lines.append(f"  {node}[\"{clean_name}\"]")
        
        # Add style
        lines.append(f"  style {node} fill:{color}")
    
    # Add edges with labels
    for s, t, data in graph.edges(data=True):
        relationship = data.get('relationship', '')
        
        # Escape special characters
        clean_relationship = relationship.replace('"', '\\"')
        
        # Highlight edges in the path
        if (s, t) in path_edges:
            lines.append(f"  {s} -->|{clean_relationship}| {t}")
            lines.append(f"  linkStyle {len(lines) - 2} stroke:{path_color},stroke-width:2px;")
        else:
            lines.append(f"  {s} -->|{clean_relationship}| {t}")
    
    # Add style definitions
    lines.append("  classDef player fill:lightblue;")
    lines.append("  classDef problem fill:salmon;")
    lines.append("  classDef solution fill:lightgreen;")
    lines.append("  classDef transaction fill:lightyellow;")
    lines.append(f"  classDef pathNode fill:{path_color},stroke:#333,stroke-width:2px;")
    
    # Apply classes
    for node, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        if node in path:
            lines.append(f"  class {node} pathNode;")
        elif node_type in ['player', 'problem', 'solution', 'transaction']:
            lines.append(f"  class {node} {node_type};")
    
    lines.append("```")
    return '\n'.join(lines)


def _convert_dot_to_svg(dot_string: str) -> str:
    """Convert DOT visualization to SVG if graphviz is available."""
    try:
        # Try to import graphviz
        import graphviz
        
        # Create a graphviz Source object
        source = graphviz.Source(dot_string)
        
        # Render to SVG
        svg_data = source.pipe(format='svg')
        
        # Convert bytes to string
        svg_string = svg_data.decode('utf-8')
        
        return svg_string
    except ImportError:
        raise ImportError("Graphviz Python package not installed. Install with: pip install graphviz")


def _get_theme_colors(theme: str) -> Dict[str, str]:
    """Get node colors based on theme."""
    themes = {
        "default": {
            "player": "lightblue",
            "problem": "salmon",
            "solution": "lightgreen",
            "transaction": "lightyellow",
            "default": "white"
        },
        "light": {
            "player": "#e6f3ff",
            "problem": "#ffe6e6",
            "solution": "#e6ffe6",
            "transaction": "#fffde6",
            "default": "#f5f5f5"
        },
        "dark": {
            "player": "#003366",
            "problem": "#660000",
            "solution": "#006600",
            "transaction": "#666600",
            "default": "#333333"
        },
        "colorful": {
            "player": "#8dd3c7",
            "problem": "#fb8072",
            "solution": "#b3de69",
            "transaction": "#fdb462",
            "default": "#cccccc"
        }
    }
    
    return themes.get(theme, themes["default"])


class VisualizationToolsRegistry:
    """Registry of MCP-compliant visualization tools."""
    
    @staticmethod
    def register_tools():
        """Register all visualization tools with the MCP Tool Registry."""
        from specialized_agents.tools.mcp_registry import registry
        
        # The tools are registered via decorators, but we can explicitly add them here if needed
        # Additional initialization can be done here
        
        logger.info("Visualization tools registered with MCP Tool Registry")
        
        # Return list of registered tool names
        return [
            "visualize_deal_graph",
            "highlight_deal_nodes",
            "highlight_deal_path",
            "calculate_deal_graph_metrics"
        ]


# Register tools when module is imported
VisualizationToolsRegistry.register_tools()