"""
Theorem Repository Analyzer

This module provides tools for analyzing a theorem repository,
identifying patterns, gaps, and opportunities for improvement.
"""

from typing import Dict, List, Tuple, Any, Optional, Set, Union, Callable
import json
import os
import time
import logging
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from enum import Enum
import community as community_louvain
import matplotlib.cm as cm
from collections import Counter, defaultdict
from datetime import datetime

from .theorem_repository import (
    TheoremRepository, Theorem, Proof, Counterexample, TheoremStatus, ProofStatus, TheoremMetadata
)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class RepositoryHealthMetrics:
    """Metrics about the health of a theorem repository."""
    total_theorems: int
    proven_theorems: int
    unproven_theorems: int
    in_progress_theorems: int
    disproven_theorems: int
    axioms: int
    proof_success_rate: float
    avg_verification_level: float
    domain_coverage: Dict[str, float]
    tag_distribution: Dict[str, int]
    dependency_graph_stats: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_theorems": self.total_theorems,
            "proven_theorems": self.proven_theorems,
            "unproven_theorems": self.unproven_theorems,
            "in_progress_theorems": self.in_progress_theorems,
            "disproven_theorems": self.disproven_theorems,
            "axioms": self.axioms,
            "proof_success_rate": self.proof_success_rate,
            "avg_verification_level": self.avg_verification_level,
            "domain_coverage": self.domain_coverage,
            "tag_distribution": self.tag_distribution,
            "dependency_graph_stats": self.dependency_graph_stats
        }


@dataclass
class TheoremGap:
    """Represents a gap or opportunity in the theorem repository."""
    gap_id: str
    gap_type: str  # "missing_theorem", "weak_proof", "domain_gap", etc.
    description: str
    importance: int  # 1-5, where 5 is most important
    related_theorems: List[str] = field(default_factory=list)
    suggested_approaches: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type,
            "description": self.description,
            "importance": self.importance,
            "related_theorems": self.related_theorems,
            "suggested_approaches": self.suggested_approaches
        }


class RepositoryAnalyzer:
    """
    Analyzer for theorem repositories.
    
    This class provides tools to analyze a theorem repository,
    generate health metrics, identify gaps, and visualize the repository.
    """
    
    def __init__(self, repository: TheoremRepository):
        """
        Initialize a repository analyzer.
        
        Args:
            repository: The theorem repository to analyze
        """
        self.repository = repository
        self.output_dir: Optional[str] = None
    
    def set_output_directory(self, output_dir: str) -> None:
        """
        Set the output directory for analysis results.
        
        Args:
            output_dir: Directory to save analysis outputs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Create subdirectories
        os.makedirs(os.path.join(output_dir, "health_reports"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "gap_reports"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "visualizations"), exist_ok=True)
    
    def analyze_repository_health(self) -> RepositoryHealthMetrics:
        """
        Analyze the health of the repository.
        
        Returns:
            Repository health metrics
        """
        # Count theorems by status
        status_counts = defaultdict(int)
        for theorem in self.repository.theorems.values():
            status_counts[theorem.status.value] += 1
        
        # Calculate verification level
        verification_levels = [
            theorem.metadata.verification_level 
            for theorem in self.repository.theorems.values()
        ]
        avg_verification = np.mean(verification_levels) if verification_levels else 0.0
        
        # Calculate domain coverage
        domains = [theorem.metadata.domain for theorem in self.repository.theorems.values()]
        domain_counter = Counter(domains)
        domain_coverage = {
            domain: count / len(self.repository.theorems) if self.repository.theorems else 0.0
            for domain, count in domain_counter.items()
        }
        
        # Calculate tag distribution
        all_tags = []
        for theorem in self.repository.theorems.values():
            all_tags.extend(theorem.metadata.tags)
        tag_distribution = dict(Counter(all_tags))
        
        # Calculate proof success rate
        successful_proofs = sum(1 for proof in self.repository.proofs.values() 
                               if proof.status == ProofStatus.VALID)
        proof_success_rate = successful_proofs / len(self.repository.proofs) if self.repository.proofs else 0.0
        
        # Calculate graph statistics
        graph_stats = self._calculate_graph_statistics()
        
        # Create health metrics
        health_metrics = RepositoryHealthMetrics(
            total_theorems=len(self.repository.theorems),
            proven_theorems=status_counts.get(TheoremStatus.PROVEN.value, 0),
            unproven_theorems=status_counts.get(TheoremStatus.UNPROVEN.value, 0),
            in_progress_theorems=status_counts.get(TheoremStatus.IN_PROGRESS.value, 0),
            disproven_theorems=status_counts.get(TheoremStatus.DISPROVEN.value, 0),
            axioms=status_counts.get(TheoremStatus.AXIOM.value, 0),
            proof_success_rate=proof_success_rate,
            avg_verification_level=avg_verification,
            domain_coverage=domain_coverage,
            tag_distribution=tag_distribution,
            dependency_graph_stats=graph_stats
        )
        
        # Save metrics if output directory is set
        if self.output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_path = os.path.join(
                self.output_dir, 
                "health_reports", 
                f"health_metrics_{timestamp}.json"
            )
            with open(metrics_path, 'w') as f:
                json.dump(health_metrics.to_dict(), f, indent=2)
            
            logger.info(f"Saved health metrics to {metrics_path}")
        
        return health_metrics
    
    def _calculate_graph_statistics(self) -> Dict[str, Any]:
        """
        Calculate statistics about the theorem dependency graph.
        
        Returns:
            Dictionary of graph statistics
        """
        graph = self.repository.graph
        
        if not graph or graph.number_of_nodes() == 0:
            return {
                "node_count": 0,
                "edge_count": 0,
                "average_degree": 0.0,
                "connected_components": 0,
                "average_clustering": 0.0,
                "diameter": 0
            }
        
        # Basic statistics
        node_count = graph.number_of_nodes()
        edge_count = graph.number_of_edges()
        avg_degree = 2 * edge_count / node_count if node_count > 0 else 0
        
        # Connected components
        connected_components = 0
        if node_count > 0:
            if hasattr(nx, 'number_connected_components'):
                # For older NetworkX versions
                connected_components = nx.number_connected_components(graph.to_undirected())
            else:
                # For newer NetworkX versions
                connected_components = len(list(nx.connected_components(graph.to_undirected())))
        
        # Clustering coefficient
        try:
            avg_clustering = nx.average_clustering(graph.to_undirected())
        except:
            avg_clustering = 0.0
        
        # Diameter (longest shortest path)
        diameter = 0
        try:
            # Convert to undirected and get largest connected component
            undirected = graph.to_undirected()
            if hasattr(nx, 'connected_components'):
                largest_cc = max(nx.connected_components(undirected), key=len)
            else:
                largest_cc = max(nx.connected_components(undirected), key=len)
            largest_cc_graph = undirected.subgraph(largest_cc)
            diameter = nx.diameter(largest_cc_graph)
        except:
            pass
        
        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "average_degree": avg_degree,
            "connected_components": connected_components,
            "average_clustering": avg_clustering,
            "diameter": diameter
        }
    
    def identify_gaps(self) -> List[TheoremGap]:
        """
        Identify gaps and opportunities in the repository.
        
        Returns:
            List of identified theorem gaps
        """
        gaps = []
        
        # Gap type 1: Missing theorems based on patterns in the existing theorems
        missing_theorem_gaps = self._identify_missing_theorem_gaps()
        gaps.extend(missing_theorem_gaps)
        
        # Gap type 2: Domain coverage gaps
        domain_gaps = self._identify_domain_gaps()
        gaps.extend(domain_gaps)
        
        # Gap type 3: Weak proofs (low verification level)
        weak_proof_gaps = self._identify_weak_proof_gaps()
        gaps.extend(weak_proof_gaps)
        
        # Gap type 4: Isolated theorems (no connections)
        isolated_theorem_gaps = self._identify_isolated_theorem_gaps()
        gaps.extend(isolated_theorem_gaps)
        
        # Save gaps if output directory is set
        if self.output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gaps_path = os.path.join(
                self.output_dir, 
                "gap_reports", 
                f"theorem_gaps_{timestamp}.json"
            )
            with open(gaps_path, 'w') as f:
                json.dump([gap.to_dict() for gap in gaps], f, indent=2)
            
            logger.info(f"Saved {len(gaps)} theorem gaps to {gaps_path}")
        
        return gaps
    
    def _identify_missing_theorem_gaps(self) -> List[TheoremGap]:
        """
        Identify missing theorems based on patterns in the repository.
        
        Returns:
            List of missing theorem gaps
        """
        gaps = []
        
        # Strategy 1: Look for "sibling" theorems
        # If theorems A and C exist but B is missing in a sequence
        theorem_names = [t.theorem_id for t in self.repository.theorems.values()]
        
        # Find numeric sequences
        sequences = defaultdict(list)
        for name in theorem_names:
            # Extract base name and number
            parts = name.split('_')
            if len(parts) > 1 and parts[-1].isdigit():
                base_name = '_'.join(parts[:-1])
                number = int(parts[-1])
                sequences[base_name].append(number)
        
        # Check for gaps in sequences
        for base_name, numbers in sequences.items():
            numbers.sort()
            if len(numbers) >= 2:
                expected_sequence = list(range(min(numbers), max(numbers) + 1))
                missing_numbers = set(expected_sequence) - set(numbers)
                
                for missing_number in missing_numbers:
                    missing_theorem_id = f"{base_name}_{missing_number}"
                    
                    # Get adjacent theorems for context
                    related_theorems = [
                        f"{base_name}_{n}" for n in numbers
                        if abs(n - missing_number) <= 2 and f"{base_name}_{n}" in self.repository.theorems
                    ]
                    
                    gap = TheoremGap(
                        gap_id=f"gap_missing_{missing_theorem_id}",
                        gap_type="missing_theorem",
                        description=f"Missing theorem in sequence: {missing_theorem_id}",
                        importance=3,  # Medium importance
                        related_theorems=related_theorems,
                        suggested_approaches=[
                            "Examine adjacent theorems in the sequence for patterns",
                            "Interpolate between theorems if they form a logical progression"
                        ]
                    )
                    gaps.append(gap)
        
        # Strategy 2: Look for common generalizations
        # If multiple theorems share similar patterns, a common generalization might be missing
        if len(self.repository.theorems) >= 3:
            # Group theorems by domain
            domain_theorems = defaultdict(list)
            for theorem in self.repository.theorems.values():
                domain_theorems[theorem.metadata.domain].append(theorem)
            
            # For each domain with sufficient theorems
            for domain, theorems in domain_theorems.items():
                if len(theorems) >= 3:
                    # Check if there are multiple theorems with no generalizations
                    ungeneralized = [t for t in theorems 
                                    if not t.generalizations and t.status == TheoremStatus.PROVEN]
                    
                    if len(ungeneralized) >= 3:
                        gap = TheoremGap(
                            gap_id=f"gap_generalization_{domain}_{hash(tuple(t.theorem_id for t in ungeneralized)) % 10000}",
                            gap_type="missing_generalization",
                            description=f"Potential missing generalization for {len(ungeneralized)} theorems in {domain} domain",
                            importance=4,  # High importance
                            related_theorems=[t.theorem_id for t in ungeneralized[:5]],  # Include up to 5 related theorems
                            suggested_approaches=[
                                "Analyze common patterns across the ungeneralized theorems",
                                "Use generalization agent to propose a common abstraction",
                                "Look for similar generalizations in adjacent domains"
                            ]
                        )
                        gaps.append(gap)
        
        return gaps
    
    def _identify_domain_gaps(self) -> List[TheoremGap]:
        """
        Identify gaps in domain coverage.
        
        Returns:
            List of domain gap opportunities
        """
        gaps = []
        
        # Get counts of theorems by domain
        domain_counts = defaultdict(int)
        for theorem in self.repository.theorems.values():
            domain_counts[theorem.metadata.domain] += 1
        
        # Define expected economic domains
        expected_domains = [
            "microeconomics", "macroeconomics", "game_theory", "decision_theory",
            "behavioral_economics", "finance", "market_design", "welfare_economics",
            "public_economics", "labor_economics", "trade_economics", "development_economics"
        ]
        
        # Check for missing or underrepresented domains
        for domain in expected_domains:
            count = domain_counts.get(domain, 0)
            
            if count == 0:
                # Missing domain
                gap = TheoremGap(
                    gap_id=f"gap_domain_missing_{domain}",
                    gap_type="domain_gap",
                    description=f"Missing theorems in the {domain} domain",
                    importance=4,  # High importance
                    related_theorems=[],
                    suggested_approaches=[
                        f"Identify key theorems from {domain} literature",
                        "Use domain-specific extraction to find theorems",
                        "Focus on fundamental results in this area"
                    ]
                )
                gaps.append(gap)
            elif count < 3:
                # Underrepresented domain
                related_theorems = [
                    t.theorem_id for t in self.repository.theorems.values()
                    if t.metadata.domain == domain
                ]
                
                gap = TheoremGap(
                    gap_id=f"gap_domain_under_{domain}",
                    gap_type="domain_gap",
                    description=f"Underrepresented domain: only {count} theorems in {domain}",
                    importance=3,  # Medium importance
                    related_theorems=related_theorems,
                    suggested_approaches=[
                        f"Expand theorem coverage in {domain}",
                        "Focus on theorems that connect this domain to well-represented domains",
                        "Look for generalizations that apply to this domain"
                    ]
                )
                gaps.append(gap)
        
        return gaps
    
    def _identify_weak_proof_gaps(self) -> List[TheoremGap]:
        """
        Identify theorems with weak or incomplete proofs.
        
        Returns:
            List of weak proof gaps
        """
        gaps = []
        
        # Strategy 1: Theorems with low verification level
        low_verification_theorems = [
            theorem for theorem in self.repository.theorems.values()
            if theorem.status == TheoremStatus.PROVEN and theorem.metadata.verification_level < 2
        ]
        
        for theorem in low_verification_theorems:
            gap = TheoremGap(
                gap_id=f"gap_weak_proof_{theorem.theorem_id}",
                gap_type="weak_proof",
                description=f"Theorem {theorem.theorem_id} has a low verification level ({theorem.metadata.verification_level})",
                importance=3,  # Medium importance
                related_theorems=[theorem.theorem_id],
                suggested_approaches=[
                    "Use a verification agent to formally verify the proof",
                    "Apply multiple proving methods to strengthen confidence",
                    "Check for edge cases and boundary conditions"
                ]
            )
            gaps.append(gap)
        
        # Strategy 2: Theorems with few or simple proofs
        for theorem_id, theorem in self.repository.theorems.items():
            if theorem.status == TheoremStatus.PROVEN:
                # Get all proofs for this theorem
                proofs = self.repository.get_proofs_for_theorem(theorem_id)
                
                if len(proofs) == 1:
                    # Only one proof might indicate opportunity for alternative approaches
                    proof = proofs[0]
                    
                    # Check if the proof is simple (few steps)
                    if len(proof.steps) < 3:
                        gap = TheoremGap(
                            gap_id=f"gap_single_simple_proof_{theorem_id}",
                            gap_type="proof_variety",
                            description=f"Theorem {theorem_id} has only one simple proof",
                            importance=2,  # Lower importance
                            related_theorems=[theorem_id],
                            suggested_approaches=[
                                "Develop alternative proof approaches",
                                "Try different proof methods (direct, contradiction, induction)",
                                "Use proof strategy agent to find novel approaches"
                            ]
                        )
                        gaps.append(gap)
        
        return gaps
    
    def _identify_isolated_theorem_gaps(self) -> List[TheoremGap]:
        """
        Identify isolated theorems with few connections.
        
        Returns:
            List of isolated theorem gaps
        """
        gaps = []
        
        # Check theorem connectivity in the graph
        for theorem_id, theorem in self.repository.theorems.items():
            if theorem_id in self.repository.graph:
                # Count connections (both incoming and outgoing)
                in_degree = self.repository.graph.in_degree(theorem_id)
                out_degree = self.repository.graph.out_degree(theorem_id)
                total_connections = in_degree + out_degree
                
                if total_connections <= 1 and theorem.status != TheoremStatus.AXIOM:
                    gap = TheoremGap(
                        gap_id=f"gap_isolated_{theorem_id}",
                        gap_type="isolated_theorem",
                        description=f"Theorem {theorem_id} is isolated with few connections",
                        importance=2,  # Lower importance
                        related_theorems=[theorem_id],
                        suggested_approaches=[
                            "Identify related theorems in the same domain",
                            "Look for applications of this theorem to other results",
                            "Consider if this theorem is a special case of a more general result",
                            "Use repository analysis to find potential connections"
                        ]
                    )
                    gaps.append(gap)
        
        return gaps
    
    def visualize_theorem_graph(self, filename: Optional[str] = None) -> str:
        """
        Generate a visualization of the theorem dependency graph.
        
        Args:
            filename: Optional filename for the visualization
            
        Returns:
            Path to the saved visualization file
        """
        if not self.repository.graph or self.repository.graph.number_of_nodes() == 0:
            logger.warning("Cannot visualize empty graph")
            return ""
        
        # Create a copy of the graph for visualization
        graph = self.repository.graph.copy()
        
        # Set node colors based on theorem status
        status_colors = {
            TheoremStatus.UNPROVEN.value: "#aaaaaa",  # Gray
            TheoremStatus.IN_PROGRESS.value: "#ffaa44",  # Orange
            TheoremStatus.PROVEN.value: "#44aa44",  # Green
            TheoremStatus.DISPROVEN.value: "#aa4444",  # Red
            TheoremStatus.AXIOM.value: "#4444aa"  # Blue
        }
        
        node_colors = []
        for node in graph.nodes():
            if "type" in graph.nodes[node] and graph.nodes[node]["type"] == "theorem":
                status = graph.nodes[node].get("status", TheoremStatus.UNPROVEN.value)
                node_colors.append(status_colors.get(status, "#aaaaaa"))
            elif "type" in graph.nodes[node] and graph.nodes[node]["type"] == "proof":
                node_colors.append("#44ffff")  # Cyan for proofs
            elif "type" in graph.nodes[node] and graph.nodes[node]["type"] == "counterexample":
                node_colors.append("#ff44ff")  # Magenta for counterexamples
            else:
                node_colors.append("#dddddd")  # Light gray for other nodes
        
        # Set edge colors based on edge type
        edge_colors = []
        for u, v, data in graph.edges(data=True):
            edge_type = data.get("type", "")
            if edge_type == "assumption":
                edge_colors.append("#4444aa")  # Blue for assumptions
            elif edge_type in ["proves", "disproves"]:
                edge_colors.append("#aa4444")  # Red for proofs/counterexamples
            elif edge_type in ["uses_theorem", "uses_axiom"]:
                edge_colors.append("#44aa44")  # Green for usage
            elif edge_type in ["generalization", "specialization"]:
                edge_colors.append("#aaaa44")  # Yellow for generalizations/specializations
            elif edge_type == "related":
                edge_colors.append("#444444")  # Dark gray for related
            else:
                edge_colors.append("#aaaaaa")  # Light gray for other edges
        
        # Create figure and draw the graph
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=200, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, width=1.0, alpha=0.5)
        
        # Draw labels for theorems, axioms, etc.
        theorem_labels = {
            node: node for node in graph.nodes()
            if "type" in graph.nodes[node] and graph.nodes[node]["type"] in ["theorem", "axiom"]
        }
        nx.draw_networkx_labels(graph, pos, labels=theorem_labels, font_size=8)
        
        plt.title("Theorem Dependency Graph")
        plt.axis("off")
        
        # Save visualization if output directory is set
        if self.output_dir:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"theorem_graph_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, "visualizations", filename)
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()
            
            logger.info(f"Saved theorem graph visualization to {filepath}")
            return filepath
        else:
            plt.show()
            return ""
    
    def visualize_domain_statistics(self, filename: Optional[str] = None) -> str:
        """
        Generate a visualization of theorem statistics by domain.
        
        Args:
            filename: Optional filename for the visualization
            
        Returns:
            Path to the saved visualization file
        """
        if not self.repository.theorems:
            logger.warning("Cannot visualize statistics for empty repository")
            return ""
        
        # Count theorems by domain and status
        domain_status_counts = defaultdict(lambda: defaultdict(int))
        for theorem in self.repository.theorems.values():
            domain_status_counts[theorem.metadata.domain][theorem.status.value] += 1
        
        # Sort domains by total count
        domain_total_counts = {
            domain: sum(counts.values()) 
            for domain, counts in domain_status_counts.items()
        }
        sorted_domains = sorted(domain_total_counts.keys(), 
                               key=lambda d: domain_total_counts[d], 
                               reverse=True)
        
        # Prepare data for stacked bar chart
        status_labels = [
            TheoremStatus.PROVEN.value,
            TheoremStatus.UNPROVEN.value,
            TheoremStatus.IN_PROGRESS.value,
            TheoremStatus.DISPROVEN.value,
            TheoremStatus.AXIOM.value
        ]
        
        status_colors = {
            TheoremStatus.PROVEN.value: "#44aa44",  # Green
            TheoremStatus.UNPROVEN.value: "#aaaaaa",  # Gray
            TheoremStatus.IN_PROGRESS.value: "#ffaa44",  # Orange
            TheoremStatus.DISPROVEN.value: "#aa4444",  # Red
            TheoremStatus.AXIOM.value: "#4444aa"  # Blue
        }
        
        # Create the stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 8))
        bottom = np.zeros(len(sorted_domains))
        
        for status in status_labels:
            values = [domain_status_counts[domain].get(status, 0) for domain in sorted_domains]
            ax.bar(sorted_domains, values, bottom=bottom, 
                  label=status, color=status_colors.get(status, "#aaaaaa"))
            bottom += values
        
        ax.set_title("Theorems by Domain and Status")
        ax.set_xlabel("Domain")
        ax.set_ylabel("Number of Theorems")
        
        # Rotate domain labels for readability
        plt.xticks(rotation=45, ha="right")
        
        # Add legend
        plt.legend(title="Status")
        
        plt.tight_layout()
        
        # Save visualization if output directory is set
        if self.output_dir:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"domain_statistics_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, "visualizations", filename)
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()
            
            logger.info(f"Saved domain statistics visualization to {filepath}")
            return filepath
        else:
            plt.show()
            return ""
    
    def visualize_theorem_community_structure(self, filename: Optional[str] = None) -> str:
        """
        Generate a visualization of theorem communities.
        
        Args:
            filename: Optional filename for the visualization
            
        Returns:
            Path to the saved visualization file
        """
        if not self.repository.graph or self.repository.graph.number_of_nodes() == 0:
            logger.warning("Cannot visualize communities for empty graph")
            return ""
        
        # Create an undirected copy of the graph for community detection
        undirected_graph = self.repository.graph.to_undirected()
        
        # Find node type mask (theorems only)
        theorem_nodes = [
            node for node, attrs in self.repository.graph.nodes(data=True)
            if attrs.get("type") == "theorem"
        ]
        theorem_graph = undirected_graph.subgraph(theorem_nodes)
        
        # Detect communities
        try:
            partition = community_louvain.best_partition(theorem_graph)
            
            # Calculate modularity
            modularity = community_louvain.modularity(partition, theorem_graph)
            
            # Create figure and draw the graph
            plt.figure(figsize=(12, 10))
            pos = nx.spring_layout(theorem_graph)
            
            # Color nodes by community
            cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
            community_colors = [cmap(partition[node]) for node in theorem_graph.nodes()]
            
            # Draw nodes and edges
            nx.draw_networkx_nodes(theorem_graph, pos, node_color=community_colors, 
                                  node_size=200, alpha=0.8)
            nx.draw_networkx_edges(theorem_graph, pos, width=1.0, alpha=0.3)
            
            # Draw labels
            nx.draw_networkx_labels(theorem_graph, pos, font_size=8)
            
            plt.title(f"Theorem Communities (Modularity: {modularity:.3f})")
            plt.axis("off")
            
            # Save visualization if output directory is set
            if self.output_dir:
                if not filename:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"theorem_communities_{timestamp}.png"
                
                filepath = os.path.join(self.output_dir, "visualizations", filename)
                plt.savefig(filepath, dpi=300, bbox_inches="tight")
                plt.close()
                
                logger.info(f"Saved theorem communities visualization to {filepath}")
                return filepath
            else:
                plt.show()
                return ""
                
        except Exception as e:
            logger.error(f"Error in community detection: {e}")
            return ""
    
    def recommend_theorems_for_proving(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Recommend theorems that should be prioritized for proving.
        
        Args:
            count: Number of theorems to recommend
            
        Returns:
            List of recommended theorems with metadata
        """
        if not self.repository.theorems:
            return []
        
        # Get all unproven and in-progress theorems
        candidate_theorems = [
            theorem for theorem in self.repository.theorems.values()
            if theorem.status in [TheoremStatus.UNPROVEN, TheoremStatus.IN_PROGRESS]
        ]
        
        if not candidate_theorems:
            return []
        
        # Calculate scores for each theorem
        scored_theorems = []
        for theorem in candidate_theorems:
            # Base score from metadata
            base_score = (
                (6 - theorem.metadata.priority) +  # Priority (1-5, lower is higher)
                theorem.metadata.importance          # Importance (1-5, higher is higher)
            )
            
            # Adjust score based on connectivity
            connectivity_score = 0
            if theorem.theorem_id in self.repository.graph:
                # Count how many proven theorems depend on this theorem
                dependents = list(self.repository.graph.successors(theorem.theorem_id))
                proven_dependents = sum(
                    1 for dependent in dependents
                    if dependent in self.repository.theorems and 
                    self.repository.theorems[dependent].status == TheoremStatus.PROVEN
                )
                
                # Count how many proven theorems this theorem depends on
                dependencies = list(self.repository.graph.predecessors(theorem.theorem_id))
                proven_dependencies = sum(
                    1 for dependency in dependencies
                    if dependency in self.repository.theorems and 
                    self.repository.theorems[dependency].status == TheoremStatus.PROVEN
                )
                
                # More proven dependencies make a theorem more provable
                # More proven dependents make a theorem more valuable to prove
                connectivity_score = 0.5 * proven_dependencies + 1.0 * proven_dependents
            
            # Adjust score based on domain coverage
            domain = theorem.metadata.domain
            domain_counts = sum(1 for t in self.repository.theorems.values() 
                               if t.metadata.domain == domain and 
                               t.status == TheoremStatus.PROVEN)
            
            # Prioritize underrepresented domains
            domain_score = 3.0 if domain_counts == 0 else (3.0 / (domain_counts + 1))
            
            # Combine scores
            total_score = base_score + connectivity_score + domain_score
            
            # Add to scored list
            scored_theorems.append((theorem, total_score))
        
        # Sort by score
        scored_theorems.sort(key=lambda x: x[1], reverse=True)
        
        # Format recommendations
        recommendations = []
        for theorem, score in scored_theorems[:count]:
            recommendations.append({
                "theorem_id": theorem.theorem_id,
                "natural_language": theorem.natural_language,
                "formal_expression": theorem.formal_expression,
                "domain": theorem.metadata.domain,
                "importance": theorem.metadata.importance,
                "priority": theorem.metadata.priority,
                "score": score,
                "assumptions": len(theorem.assumptions),
                "status": theorem.status.value
            })
        
        return recommendations
    
    def export_analysis_report(self, filename: Optional[str] = None) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            filename: Optional filename for the report
            
        Returns:
            Path to the saved report file
        """
        if not self.output_dir:
            raise ValueError("Output directory must be set to export report")
        
        # Gather all analysis data
        health_metrics = self.analyze_repository_health()
        gaps = self.identify_gaps()
        recommendations = self.recommend_theorems_for_proving(10)
        
        # Generate visualizations
        theorem_graph_path = self.visualize_theorem_graph()
        domain_stats_path = self.visualize_domain_statistics()
        community_graph_path = self.visualize_theorem_community_structure()
        
        # Create report data
        report = {
            "report_title": "Economic Theorem Repository Analysis Report",
            "generated_at": datetime.now().isoformat(),
            "repository_metrics": health_metrics.to_dict(),
            "identified_gaps": [gap.to_dict() for gap in gaps],
            "theorem_recommendations": recommendations,
            "visualizations": {
                "theorem_graph": os.path.basename(theorem_graph_path) if theorem_graph_path else None,
                "domain_statistics": os.path.basename(domain_stats_path) if domain_stats_path else None,
                "community_structure": os.path.basename(community_graph_path) if community_graph_path else None
            }
        }
        
        # Save report
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repository_analysis_report_{timestamp}.json"
        
        report_path = os.path.join(self.output_dir, filename)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Saved analysis report to {report_path}")
        return report_path