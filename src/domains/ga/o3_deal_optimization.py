"""
O3 Optimization Process for Moneyball Deal Model

This module implements an O3 (Optimization-Oriented Operation) process for
optimizing Moneyball Deal Models across the HMS ecosystem. It uses hypergraph-based
optimization to identify high-value deals and create optimal roadmaps for implementation.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional, Union, Set
from dataclasses import dataclass
import json
import datetime
import math
import hashlib
import itertools
from collections import defaultdict
import io
import base64

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class EntityNode:
    """An entity node in the deal hypergraph."""
    id: str
    name: str
    type: str  # government, corporate, ngo, civilian
    attributes: Dict[str, Any]
    capabilities: Dict[str, float]
    needs: Dict[str, float]
    constraints: Dict[str, Any]
    connections: Set[str]  # IDs of connected entities
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, EntityNode):
            return False
        return self.id == other.id

@dataclass
class ValueEdge:
    """A value edge in the deal hypergraph."""
    id: str
    source_ids: List[str]
    target_ids: List[str]
    value_type: str  # economic, social, environmental, etc.
    value_amount: float
    conditions: Dict[str, Any]
    probability: float
    verification_method: str
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, ValueEdge):
            return False
        return self.id == other.id

@dataclass
class DealHyperedge:
    """A hyperedge representing a potential deal."""
    id: str
    entity_ids: List[str]
    value_edge_ids: List[str]
    deal_type: str
    total_value: float
    complexity: float
    implementation_time: int  # in time units (days, weeks, etc.)
    dependencies: List[str]  # IDs of deals this depends on
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, DealHyperedge):
            return False
        return self.id == other.id

@dataclass
class DealRoadmap:
    """A roadmap of deals to implement."""
    id: str
    deal_ids: List[str]
    total_value: float
    total_time: int
    critical_path: List[str]
    milestones: Dict[int, List[str]]
    dependencies: Dict[str, List[str]]
    
    @property
    def deal_count(self) -> int:
        """Get the number of deals in the roadmap."""
        return len(self.deal_ids)

@dataclass
class OptimizationResult:
    """Result of an optimization run."""
    roadmap: DealRoadmap
    value_curve: Dict[int, float]
    entity_value: Dict[str, float]
    constraint_satisfaction: Dict[str, bool]
    risk_assessment: Dict[str, float]
    
    @property
    def is_feasible(self) -> bool:
        """Check if the optimization result is feasible."""
        return all(self.constraint_satisfaction.values())

# =============================================================================
# Hypergraph Implementation
# =============================================================================

class DealHypergraph:
    """
    Hypergraph representation of deal opportunities.
    
    This class implements a hypergraph where entities are nodes, value transfers
    are edges, and potential deals are hyperedges connecting multiple entities.
    """
    
    def __init__(self):
        """Initialize an empty deal hypergraph."""
        self.entities = {}  # Dictionary of entities by ID
        self.value_edges = {}  # Dictionary of value edges by ID
        self.deals = {}  # Dictionary of deals by ID
        
        # Indexes for faster lookup
        self.entity_to_deals = defaultdict(set)  # Entity ID -> Deal IDs
        self.value_to_deals = defaultdict(set)  # Value edge ID -> Deal IDs
        self.entity_to_values = defaultdict(set)  # Entity ID -> Value edge IDs
    
    def add_entity(self, entity: EntityNode) -> None:
        """
        Add an entity to the hypergraph.
        
        Args:
            entity: EntityNode object
        """
        self.entities[entity.id] = entity
    
    def add_value_edge(self, edge: ValueEdge) -> None:
        """
        Add a value edge to the hypergraph.
        
        Args:
            edge: ValueEdge object
        """
        self.value_edges[edge.id] = edge
        
        # Update indexes
        for entity_id in edge.source_ids + edge.target_ids:
            self.entity_to_values[entity_id].add(edge.id)
    
    def add_deal(self, deal: DealHyperedge) -> None:
        """
        Add a deal hyperedge to the hypergraph.
        
        Args:
            deal: DealHyperedge object
        """
        self.deals[deal.id] = deal
        
        # Update indexes
        for entity_id in deal.entity_ids:
            self.entity_to_deals[entity_id].add(deal.id)
        
        for value_id in deal.value_edge_ids:
            self.value_to_deals[value_id].add(deal.id)
    
    def get_entity_deals(self, entity_id: str) -> List[DealHyperedge]:
        """
        Get all deals involving an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of DealHyperedge objects
        """
        deal_ids = self.entity_to_deals.get(entity_id, set())
        return [self.deals[deal_id] for deal_id in deal_ids]
    
    def get_deal_entities(self, deal_id: str) -> List[EntityNode]:
        """
        Get all entities involved in a deal.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            List of EntityNode objects
        """
        deal = self.deals.get(deal_id)
        if not deal:
            return []
        
        return [self.entities[entity_id] for entity_id in deal.entity_ids if entity_id in self.entities]
    
    def get_deal_value_edges(self, deal_id: str) -> List[ValueEdge]:
        """
        Get all value edges in a deal.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            List of ValueEdge objects
        """
        deal = self.deals.get(deal_id)
        if not deal:
            return []
        
        return [self.value_edges[edge_id] for edge_id in deal.value_edge_ids if edge_id in self.value_edges]
    
    def get_entity_value_edges(self, entity_id: str) -> List[ValueEdge]:
        """
        Get all value edges connected to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of ValueEdge objects
        """
        edge_ids = self.entity_to_values.get(entity_id, set())
        return [self.value_edges[edge_id] for edge_id in edge_ids if edge_id in self.value_edges]
    
    def get_entity_net_value(self, entity_id: str) -> float:
        """
        Calculate the net value for an entity across all deals.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Net value for the entity
        """
        deals = self.get_entity_deals(entity_id)
        
        incoming_value = 0.0
        outgoing_value = 0.0
        
        for deal in deals:
            for value_edge_id in deal.value_edge_ids:
                if value_edge_id in self.value_edges:
                    edge = self.value_edges[value_edge_id]
                    
                    # Calculate value flowing to this entity
                    if entity_id in edge.target_ids:
                        incoming_value += edge.value_amount * edge.probability
                    
                    # Calculate value flowing from this entity
                    if entity_id in edge.source_ids:
                        outgoing_value += edge.value_amount * edge.probability
        
        return incoming_value - outgoing_value
    
    def get_deal_dependencies(self, deal_id: str) -> List[DealHyperedge]:
        """
        Get all deals that a given deal depends on.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            List of DealHyperedge objects
        """
        deal = self.deals.get(deal_id)
        if not deal:
            return []
        
        return [self.deals[dep_id] for dep_id in deal.dependencies if dep_id in self.deals]
    
    def get_deal_dependents(self, deal_id: str) -> List[DealHyperedge]:
        """
        Get all deals that depend on a given deal.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            List of DealHyperedge objects
        """
        dependents = []
        
        for other_id, other_deal in self.deals.items():
            if deal_id in other_deal.dependencies:
                dependents.append(other_deal)
        
        return dependents
    
    def generate_entity_graph(self) -> nx.Graph:
        """
        Generate a NetworkX graph of entity relationships.
        
        Returns:
            NetworkX Graph object
        """
        G = nx.Graph()
        
        # Add nodes
        for entity_id, entity in self.entities.items():
            G.add_node(entity_id, 
                       name=entity.name, 
                       type=entity.type,
                       **entity.attributes)
        
        # Add edges based on shared deals
        for deal_id, deal in self.deals.items():
            # Add edges between all pairs of entities in this deal
            for i, entity1_id in enumerate(deal.entity_ids):
                for entity2_id in deal.entity_ids[i+1:]:
                    if G.has_edge(entity1_id, entity2_id):
                        # Increment weight if edge already exists
                        G[entity1_id][entity2_id]['weight'] += 1
                        G[entity1_id][entity2_id]['deals'].append(deal_id)
                    else:
                        # Create new edge
                        G.add_edge(entity1_id, entity2_id, 
                                  weight=1, 
                                  deals=[deal_id])
        
        return G
    
    def generate_deal_graph(self) -> nx.DiGraph:
        """
        Generate a NetworkX directed graph of deal dependencies.
        
        Returns:
            NetworkX DiGraph object
        """
        G = nx.DiGraph()
        
        # Add nodes
        for deal_id, deal in self.deals.items():
            G.add_node(deal_id, 
                      value=deal.total_value,
                      complexity=deal.complexity,
                      time=deal.implementation_time,
                      type=deal.deal_type)
        
        # Add edges based on dependencies
        for deal_id, deal in self.deals.items():
            for dep_id in deal.dependencies:
                if dep_id in self.deals:
                    G.add_edge(dep_id, deal_id)
        
        return G
    
    def find_critical_path(self) -> List[str]:
        """
        Find the critical path of deals.
        
        Returns:
            List of deal IDs in the critical path
        """
        # Generate deal graph
        G = self.generate_deal_graph()
        
        # Find sources and sinks
        sources = [n for n in G.nodes() if G.in_degree(n) == 0]
        sinks = [n for n in G.nodes() if G.out_degree(n) == 0]
        
        # Calculate longest path
        critical_path = []
        max_length = 0
        
        for source in sources:
            for sink in sinks:
                try:
                    paths = list(nx.all_simple_paths(G, source, sink))
                    for path in paths:
                        # Calculate path length (sum of implementation times)
                        path_length = sum(self.deals[deal_id].implementation_time for deal_id in path)
                        
                        if path_length > max_length:
                            max_length = path_length
                            critical_path = path
                except nx.NetworkXNoPath:
                    continue
        
        return critical_path
    
    def generate_value_matrix(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Generate a matrix of value flows between entities.
        
        Returns:
            Tuple of (value matrix, entity IDs, value types)
        """
        # Get sorted list of entity IDs and value types
        entity_ids = sorted(self.entities.keys())
        value_types = sorted(set(edge.value_type for edge in self.value_edges.values()))
        
        # Initialize value matrix
        # Dimensions: [source_entity, target_entity, value_type]
        n_entities = len(entity_ids)
        n_value_types = len(value_types)
        value_matrix = np.zeros((n_entities, n_entities, n_value_types))
        
        # Entity ID to index mapping
        entity_to_idx = {entity_id: i for i, entity_id in enumerate(entity_ids)}
        value_to_idx = {value_type: i for i, value_type in enumerate(value_types)}
        
        # Fill value matrix
        for edge in self.value_edges.values():
            value_idx = value_to_idx[edge.value_type]
            
            # For each source-target pair, add value
            for source_id in edge.source_ids:
                if source_id not in entity_to_idx:
                    continue
                    
                source_idx = entity_to_idx[source_id]
                
                for target_id in edge.target_ids:
                    if target_id not in entity_to_idx:
                        continue
                        
                    target_idx = entity_to_idx[target_id]
                    
                    # Add expected value (value * probability)
                    value_matrix[source_idx, target_idx, value_idx] += edge.value_amount * edge.probability
        
        return value_matrix, entity_ids, value_types
    
    def calculate_network_metrics(self) -> Dict[str, Any]:
        """
        Calculate network metrics for the deal hypergraph.
        
        Returns:
            Dictionary of network metrics
        """
        # Generate entity graph
        G = self.generate_entity_graph()
        
        # Calculate basic metrics
        metrics = {
            "entity_count": len(self.entities),
            "deal_count": len(self.deals),
            "value_edge_count": len(self.value_edges),
            "density": nx.density(G),
            "connected_components": nx.number_connected_components(G),
            "average_clustering": nx.average_clustering(G),
            "entity_metrics": {}
        }
        
        # Calculate centrality metrics
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        eigenvector_centrality = nx.eigenvector_centrality_numpy(G)
        
        # Calculate entity-specific metrics
        for entity_id, entity in self.entities.items():
            entity_deals = self.get_entity_deals(entity_id)
            entity_value_edges = self.get_entity_value_edges(entity_id)
            
            metrics["entity_metrics"][entity_id] = {
                "deal_count": len(entity_deals),
                "value_edge_count": len(entity_value_edges),
                "net_value": self.get_entity_net_value(entity_id),
                "degree_centrality": degree_centrality.get(entity_id, 0.0),
                "betweenness_centrality": betweenness_centrality.get(entity_id, 0.0),
                "eigenvector_centrality": eigenvector_centrality.get(entity_id, 0.0)
            }
        
        # Calculate deal-specific metrics
        deal_graph = self.generate_deal_graph()
        metrics["max_path_length"] = nx.dag_longest_path_length(deal_graph) if deal_graph.nodes() else 0
        metrics["critical_path_length"] = len(self.find_critical_path())
        
        return metrics
    
    def visualize_entity_network(self) -> str:
        """
        Generate a visualization of the entity network.
        
        Returns:
            Base64-encoded PNG image
        """
        G = self.generate_entity_graph()
        
        # Set up plot
        plt.figure(figsize=(12, 10))
        
        # Define node colors based on entity type
        color_map = {
            'government': '#1f77b4',  # blue
            'corporate': '#2ca02c',   # green
            'ngo': '#d62728',         # red
            'civilian': '#9467bd'     # purple
        }
        
        node_colors = [color_map.get(self.entities[node].type, '#7f7f7f') for node in G.nodes()]
        
        # Define node sizes based on degree
        node_sizes = [300 * (1 + G.degree(node)) for node in G.nodes()]
        
        # Define edge widths based on weight
        edge_widths = [data['weight'] for _, _, data in G.edges(data=True)]
        
        # Create position layout
        pos = nx.spring_layout(G, seed=42)
        
        # Draw network
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(G, pos, {node: self.entities[node].name for node in G.nodes()})
        
        plt.title("Entity Network")
        plt.axis('off')
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def visualize_deal_dependencies(self) -> str:
        """
        Generate a visualization of deal dependencies.
        
        Returns:
            Base64-encoded PNG image
        """
        G = self.generate_deal_graph()
        
        # Set up plot
        plt.figure(figsize=(14, 10))
        
        # Define node colors based on deal type
        deal_types = list(set(self.deals[node].deal_type for node in G.nodes()))
        color_map = {}
        for i, deal_type in enumerate(deal_types):
            color_map[deal_type] = plt.cm.tab10(i % 10)
        
        node_colors = [color_map.get(self.deals[node].deal_type, '#7f7f7f') for node in G.nodes()]
        
        # Define node sizes based on value
        max_value = max(self.deals[node].total_value for node in G.nodes()) if G.nodes() else 1.0
        node_sizes = [500 * (0.1 + self.deals[node].total_value / max_value) for node in G.nodes()]
        
        # Create position layout using hierarchical layout
        pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
        
        # Find critical path
        critical_path = self.find_critical_path()
        critical_path_edges = [(critical_path[i], critical_path[i+1]) 
                              for i in range(len(critical_path)-1)]
        
        # Draw network
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        
        # Draw regular edges
        regular_edges = [(u, v) for u, v in G.edges() if (u, v) not in critical_path_edges]
        nx.draw_networkx_edges(G, pos, edgelist=regular_edges, alpha=0.5, edge_color='gray')
        
        # Draw critical path edges
        nx.draw_networkx_edges(G, pos, edgelist=critical_path_edges, alpha=1.0, 
                             edge_color='red', width=2.0)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, {node: f"{node}\n({self.deals[node].total_value:.1f})" 
                                        for node in G.nodes()})
        
        plt.title("Deal Dependencies (Critical Path in Red)")
        plt.axis('off')
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')

    def export_to_json(self) -> Dict[str, Any]:
        """
        Export the hypergraph to a JSON-compatible dictionary.
        
        Returns:
            Dictionary representation of the hypergraph
        """
        export_data = {
            "entities": {entity_id: self._entity_to_dict(entity) 
                       for entity_id, entity in self.entities.items()},
            "value_edges": {edge_id: self._value_edge_to_dict(edge) 
                          for edge_id, edge in self.value_edges.items()},
            "deals": {deal_id: self._deal_to_dict(deal) 
                    for deal_id, deal in self.deals.items()}
        }
        
        # Add metadata
        export_data["metadata"] = {
            "entity_count": len(self.entities),
            "value_edge_count": len(self.value_edges),
            "deal_count": len(self.deals),
            "export_date": datetime.datetime.now().isoformat()
        }
        
        return export_data
    
    def _entity_to_dict(self, entity: EntityNode) -> Dict[str, Any]:
        """Convert an entity to a dictionary."""
        return {
            "id": entity.id,
            "name": entity.name,
            "type": entity.type,
            "attributes": entity.attributes,
            "capabilities": entity.capabilities,
            "needs": entity.needs,
            "constraints": entity.constraints,
            "connections": list(entity.connections)
        }
    
    def _value_edge_to_dict(self, edge: ValueEdge) -> Dict[str, Any]:
        """Convert a value edge to a dictionary."""
        return {
            "id": edge.id,
            "source_ids": edge.source_ids,
            "target_ids": edge.target_ids,
            "value_type": edge.value_type,
            "value_amount": edge.value_amount,
            "conditions": edge.conditions,
            "probability": edge.probability,
            "verification_method": edge.verification_method
        }
    
    def _deal_to_dict(self, deal: DealHyperedge) -> Dict[str, Any]:
        """Convert a deal to a dictionary."""
        return {
            "id": deal.id,
            "entity_ids": deal.entity_ids,
            "value_edge_ids": deal.value_edge_ids,
            "deal_type": deal.deal_type,
            "total_value": deal.total_value,
            "complexity": deal.complexity,
            "implementation_time": deal.implementation_time,
            "dependencies": deal.dependencies
        }
    
    @classmethod
    def import_from_json(cls, data: Dict[str, Any]) -> 'DealHypergraph':
        """
        Import a hypergraph from a JSON-compatible dictionary.
        
        Args:
            data: Dictionary representation of a hypergraph
            
        Returns:
            DealHypergraph object
        """
        # Create new hypergraph
        hypergraph = cls()
        
        # Import entities
        for entity_id, entity_data in data.get("entities", {}).items():
            entity = EntityNode(
                id=entity_data["id"],
                name=entity_data["name"],
                type=entity_data["type"],
                attributes=entity_data["attributes"],
                capabilities=entity_data["capabilities"],
                needs=entity_data["needs"],
                constraints=entity_data["constraints"],
                connections=set(entity_data["connections"])
            )
            hypergraph.add_entity(entity)
        
        # Import value edges
        for edge_id, edge_data in data.get("value_edges", {}).items():
            edge = ValueEdge(
                id=edge_data["id"],
                source_ids=edge_data["source_ids"],
                target_ids=edge_data["target_ids"],
                value_type=edge_data["value_type"],
                value_amount=edge_data["value_amount"],
                conditions=edge_data["conditions"],
                probability=edge_data["probability"],
                verification_method=edge_data["verification_method"]
            )
            hypergraph.add_value_edge(edge)
        
        # Import deals
        for deal_id, deal_data in data.get("deals", {}).items():
            deal = DealHyperedge(
                id=deal_data["id"],
                entity_ids=deal_data["entity_ids"],
                value_edge_ids=deal_data["value_edge_ids"],
                deal_type=deal_data["deal_type"],
                total_value=deal_data["total_value"],
                complexity=deal_data["complexity"],
                implementation_time=deal_data["implementation_time"],
                dependencies=deal_data["dependencies"]
            )
            hypergraph.add_deal(deal)
        
        return hypergraph

# =============================================================================
# O3 Optimization
# =============================================================================

class O3Optimizer:
    """
    Optimization-Oriented Operation (O3) optimizer for deal roadmaps.
    
    This class implements optimization algorithms for finding optimal deal
    roadmaps given constraints and objectives.
    """
    
    def __init__(self, hypergraph: DealHypergraph):
        """
        Initialize the optimizer with a deal hypergraph.
        
        Args:
            hypergraph: DealHypergraph object
        """
        self.hypergraph = hypergraph
        
        # Default settings
        self.settings = {
            "max_roadmap_length": 20,
            "max_implementation_time": 36,  # e.g., months
            "max_complexity": 100.0,
            "min_entity_value": 0.0,  # Minimum value for each entity
            "value_discount_rate": 0.05,  # Annual discount rate for future value
            "risk_aversion_factor": 1.0  # 1.0 = risk neutral
        }
    
    def set_optimization_parameters(self, **kwargs) -> None:
        """
        Set optimization parameters.
        
        Args:
            **kwargs: Parameter key-value pairs
        """
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value
    
    def optimize_roadmap(
        self,
        objective: str = "total_value",
        constraints: Dict[str, Any] = None,
        required_deals: List[str] = None,
        excluded_deals: List[str] = None
    ) -> OptimizationResult:
        """
        Optimize a deal roadmap.
        
        Args:
            objective: Optimization objective ("total_value", "time", "roi", etc.)
            constraints: Dictionary of additional constraints
            required_deals: List of deals that must be included
            excluded_deals: List of deals that must be excluded
            
        Returns:
            OptimizationResult object
        """
        # Apply default settings for constraints
        if constraints is None:
            constraints = {}
        
        # Ensure required and excluded deals are lists
        if required_deals is None:
            required_deals = []
        if excluded_deals is None:
            excluded_deals = []
        
        # Define the candidate deal set
        candidate_deals = {
            deal_id: deal for deal_id, deal in self.hypergraph.deals.items()
            if deal_id not in excluded_deals
        }
        
        # If no candidate deals, return empty roadmap
        if not candidate_deals:
            return self._create_empty_optimization_result()
        
        # Build dependency graph
        G = self.hypergraph.generate_deal_graph()
        
        # Add required deals and their dependencies
        required_with_deps = set(required_deals)
        for deal_id in required_deals:
            # Add all ancestors (dependencies)
            if deal_id in G:
                ancestors = nx.ancestors(G, deal_id)
                required_with_deps.update(ancestors)
        
        # Calculate total implementation time for each deal including dependencies
        deal_total_times = {}
        for deal_id, deal in candidate_deals.items():
            # Get all dependencies
            if deal_id in G:
                dependencies = nx.ancestors(G, deal_id)
                dep_deals = [candidate_deals[dep_id] for dep_id in dependencies if dep_id in candidate_deals]
                
                # Calculate total time including dependencies
                deal_total_times[deal_id] = deal.implementation_time + sum(d.implementation_time for d in dep_deals)
            else:
                deal_total_times[deal_id] = deal.implementation_time
        
        # Filter deals based on time constraint
        if "max_implementation_time" in constraints:
            max_time = constraints["max_implementation_time"]
        else:
            max_time = self.settings["max_implementation_time"]
        
        time_feasible_deals = {
            deal_id: deal for deal_id, deal in candidate_deals.items()
            if deal_total_times.get(deal_id, float('inf')) <= max_time or deal_id in required_with_deps
        }
        
        # Create optimization problem based on objective
        if objective == "total_value":
            return self._optimize_total_value(time_feasible_deals, G, required_with_deps, constraints)
        elif objective == "time":
            return self._optimize_time(time_feasible_deals, G, required_with_deps, constraints)
        elif objective == "roi":
            return self._optimize_roi(time_feasible_deals, G, required_with_deps, constraints)
        else:
            # Default to total value optimization
            return self._optimize_total_value(time_feasible_deals, G, required_with_deps, constraints)
    
    def _optimize_total_value(
        self,
        candidate_deals: Dict[str, DealHyperedge],
        dependency_graph: nx.DiGraph,
        required_deals: Set[str],
        constraints: Dict[str, Any]
    ) -> OptimizationResult:
        """
        Optimize roadmap for maximum total value.
        
        Args:
            candidate_deals: Dictionary of candidate deals
            dependency_graph: NetworkX DiGraph of deal dependencies
            required_deals: Set of deals that must be included
            constraints: Dictionary of additional constraints
            
        Returns:
            OptimizationResult object
        """
        # Get max roadmap length
        if "max_roadmap_length" in constraints:
            max_length = constraints["max_roadmap_length"]
        else:
            max_length = self.settings["max_roadmap_length"]
        
        # If max_length is less than the number of required deals, adjust it
        if max_length < len(required_deals):
            max_length = len(required_deals)
        
        # Start with required deals
        selected_deals = list(required_deals)
        
        # Calculate remaining capacity
        remaining_capacity = max_length - len(selected_deals)
        
        # If no remaining capacity, finalize the roadmap with required deals
        if remaining_capacity <= 0:
            return self._finalize_roadmap(selected_deals, dependency_graph)
        
        # Calculate priority score for each deal (value / time)
        priority_scores = {}
        for deal_id, deal in candidate_deals.items():
            if deal_id not in selected_deals:
                # Calculate time-discounted value
                discount_factor = 1.0 / (1.0 + self.settings["value_discount_rate"]) ** (deal.implementation_time / 12.0)
                discounted_value = deal.total_value * discount_factor
                
                # Calculate priority score (value per unit time)
                if deal.implementation_time > 0:
                    priority_scores[deal_id] = discounted_value / deal.implementation_time
                else:
                    priority_scores[deal_id] = discounted_value
        
        # Sort deals by priority score
        sorted_deals = sorted(
            (deal_id for deal_id in priority_scores.keys() if deal_id not in selected_deals),
            key=lambda d: priority_scores[d],
            reverse=True
        )
        
        # Add deals until capacity is reached or no more deals
        for deal_id in sorted_deals:
            # Skip if already selected
            if deal_id in selected_deals:
                continue
            
            # Check if adding this deal and its dependencies exceeds capacity
            missing_deps = [d for d in nx.ancestors(dependency_graph, deal_id) 
                          if d not in selected_deals and d in candidate_deals]
            
            if len(missing_deps) + 1 <= remaining_capacity:
                # Add missing dependencies
                selected_deals.extend(missing_deps)
                
                # Add the deal itself
                selected_deals.append(deal_id)
                
                # Update remaining capacity
                remaining_capacity -= (len(missing_deps) + 1)
                
                # If no more capacity, break
                if remaining_capacity <= 0:
                    break
        
        # Finalize the roadmap
        return self._finalize_roadmap(selected_deals, dependency_graph)
    
    def _optimize_time(
        self,
        candidate_deals: Dict[str, DealHyperedge],
        dependency_graph: nx.DiGraph,
        required_deals: Set[str],
        constraints: Dict[str, Any]
    ) -> OptimizationResult:
        """
        Optimize roadmap to minimize implementation time.
        
        Args:
            candidate_deals: Dictionary of candidate deals
            dependency_graph: NetworkX DiGraph of deal dependencies
            required_deals: Set of deals that must be included
            constraints: Dictionary of additional constraints
            
        Returns:
            OptimizationResult object
        """
        # Set minimum value constraint
        if "min_total_value" in constraints:
            min_value = constraints["min_total_value"]
        else:
            min_value = 0.0  # No minimum by default
        
        # Start with required deals
        selected_deals = list(required_deals)
        
        # Calculate current total value
        current_value = sum(candidate_deals[deal_id].total_value for deal_id in selected_deals if deal_id in candidate_deals)
        
        # If current value is already at or above minimum, finalize the roadmap
        if current_value >= min_value:
            return self._finalize_roadmap(selected_deals, dependency_graph)
        
        # Calculate value gap
        value_gap = min_value - current_value
        
        # Calculate efficiency score for each deal (value / time)
        efficiency_scores = {}
        for deal_id, deal in candidate_deals.items():
            if deal_id not in selected_deals and deal.total_value > 0:
                # Calculate efficiency score (value per unit time)
                if deal.implementation_time > 0:
                    efficiency_scores[deal_id] = deal.total_value / deal.implementation_time
                else:
                    efficiency_scores[deal_id] = deal.total_value
        
        # Sort deals by efficiency score
        sorted_deals = sorted(
            (deal_id for deal_id in efficiency_scores.keys() if deal_id not in selected_deals),
            key=lambda d: efficiency_scores[d],
            reverse=True
        )
        
        # Add deals until minimum value is reached or no more deals
        for deal_id in sorted_deals:
            # Skip if already selected
            if deal_id in selected_deals:
                continue
            
            # Check dependencies
            missing_deps = [d for d in nx.ancestors(dependency_graph, deal_id) 
                          if d not in selected_deals and d in candidate_deals]
            
            # Calculate value of deal and dependencies
            deal_value = candidate_deals[deal_id].total_value
            deps_value = sum(candidate_deals[d].total_value for d in missing_deps if d in candidate_deals)
            total_added_value = deal_value + deps_value
            
            # Add deal and dependencies if it helps meet the minimum value
            if total_added_value > 0:
                # Add missing dependencies
                selected_deals.extend(missing_deps)
                
                # Add the deal itself
                selected_deals.append(deal_id)
                
                # Update current value
                current_value += total_added_value
                
                # If value requirement is met, break
                if current_value >= min_value:
                    break
        
        # Finalize the roadmap
        return self._finalize_roadmap(selected_deals, dependency_graph)
    
    def _optimize_roi(
        self,
        candidate_deals: Dict[str, DealHyperedge],
        dependency_graph: nx.DiGraph,
        required_deals: Set[str],
        constraints: Dict[str, Any]
    ) -> OptimizationResult:
        """
        Optimize roadmap for maximum return on investment (ROI).
        
        Args:
            candidate_deals: Dictionary of candidate deals
            dependency_graph: NetworkX DiGraph of deal dependencies
            required_deals: Set of deals that must be included
            constraints: Dictionary of additional constraints
            
        Returns:
            OptimizationResult object
        """
        # Get max roadmap length and implementation time
        if "max_roadmap_length" in constraints:
            max_length = constraints["max_roadmap_length"]
        else:
            max_length = self.settings["max_roadmap_length"]
        
        if "max_implementation_time" in constraints:
            max_time = constraints["max_implementation_time"]
        else:
            max_time = self.settings["max_implementation_time"]
        
        # Start with required deals
        selected_deals = list(required_deals)
        
        # Calculate current implementation time
        subgraph = dependency_graph.subgraph(selected_deals)
        current_time = self._calculate_critical_path_time(subgraph, candidate_deals)
        
        # Calculate remaining capacity and time
        remaining_capacity = max_length - len(selected_deals)
        remaining_time = max_time - current_time
        
        # If no remaining capacity or time, finalize the roadmap
        if remaining_capacity <= 0 or remaining_time <= 0:
            return self._finalize_roadmap(selected_deals, dependency_graph)
        
        # Calculate ROI score for each deal (value / complexity)
        roi_scores = {}
        for deal_id, deal in candidate_deals.items():
            if deal_id not in selected_deals:
                # Calculate ROI score (value per unit complexity)
                if deal.complexity > 0:
                    roi_scores[deal_id] = deal.total_value / deal.complexity
                else:
                    roi_scores[deal_id] = deal.total_value
        
        # Sort deals by ROI score
        sorted_deals = sorted(
            (deal_id for deal_id in roi_scores.keys() if deal_id not in selected_deals),
            key=lambda d: roi_scores[d],
            reverse=True
        )
        
        # Add deals until capacity or time is reached or no more deals
        for deal_id in sorted_deals:
            # Skip if already selected
            if deal_id in selected_deals:
                continue
            
            # Check dependencies
            missing_deps = [d for d in nx.ancestors(dependency_graph, deal_id) 
                          if d not in selected_deals and d in candidate_deals]
            
            # Check if adding this deal and its dependencies exceeds capacity
            if len(missing_deps) + 1 > remaining_capacity:
                continue
            
            # Check if adding this deal and its dependencies exceeds time
            test_selected = selected_deals + missing_deps + [deal_id]
            test_subgraph = dependency_graph.subgraph(test_selected)
            test_time = self._calculate_critical_path_time(test_subgraph, candidate_deals)
            
            if test_time <= max_time:
                # Add missing dependencies
                selected_deals.extend(missing_deps)
                
                # Add the deal itself
                selected_deals.append(deal_id)
                
                # Update remaining capacity and time
                remaining_capacity -= (len(missing_deps) + 1)
                current_time = test_time
                remaining_time = max_time - current_time
                
                # If no more capacity or time, break
                if remaining_capacity <= 0 or remaining_time <= 0:
                    break
        
        # Finalize the roadmap
        return self._finalize_roadmap(selected_deals, dependency_graph)
    
    def _calculate_critical_path_time(
        self, 
        subgraph: nx.DiGraph, 
        candidate_deals: Dict[str, DealHyperedge]
    ) -> int:
        """
        Calculate the total time of the critical path in a deal subgraph.
        
        Args:
            subgraph: NetworkX DiGraph representing a subset of the deal graph
            candidate_deals: Dictionary of candidate deals
            
        Returns:
            Total implementation time of the critical path
        """
        if not subgraph.nodes():
            return 0
        
        # Find sources and sinks
        sources = [n for n in subgraph.nodes() if subgraph.in_degree(n) == 0]
        sinks = [n for n in subgraph.nodes() if subgraph.out_degree(n) == 0]
        
        # Calculate longest path
        max_time = 0
        
        for source in sources:
            for sink in sinks:
                try:
                    for path in nx.all_simple_paths(subgraph, source, sink):
                        path_time = sum(candidate_deals[deal_id].implementation_time 
                                      for deal_id in path if deal_id in candidate_deals)
                        max_time = max(max_time, path_time)
                except nx.NetworkXNoPath:
                    continue
        
        return max_time
    
    def _finalize_roadmap(
        self, 
        selected_deals: List[str], 
        dependency_graph: nx.DiGraph
    ) -> OptimizationResult:
        """
        Finalize a roadmap based on selected deals.
        
        Args:
            selected_deals: List of selected deal IDs
            dependency_graph: NetworkX DiGraph of deal dependencies
            
        Returns:
            OptimizationResult object
        """
        # Ensure all deals are valid
        valid_deals = [deal_id for deal_id in selected_deals if deal_id in self.hypergraph.deals]
        
        # If no valid deals, return empty result
        if not valid_deals:
            return self._create_empty_optimization_result()
        
        # Extract subgraph of selected deals
        subgraph = dependency_graph.subgraph(valid_deals)
        
        # Determine critical path
        critical_path = []
        
        # Find sources and sinks
        sources = [n for n in subgraph.nodes() if subgraph.in_degree(n) == 0]
        sinks = [n for n in subgraph.nodes() if subgraph.out_degree(n) == 0]
        
        # Calculate critical path
        max_time = 0
        
        for source in sources:
            for sink in sinks:
                try:
                    for path in nx.all_simple_paths(subgraph, source, sink):
                        path_time = sum(self.hypergraph.deals[deal_id].implementation_time 
                                      for deal_id in path)
                        
                        if path_time > max_time:
                            max_time = path_time
                            critical_path = path
                except nx.NetworkXNoPath:
                    continue
        
        # Calculate total value
        total_value = sum(self.hypergraph.deals[deal_id].total_value for deal_id in valid_deals)
        
        # Get earliest possible start time for each deal
        earliest_start_times = {}
        for deal_id in valid_deals:
            # Get all dependencies
            predecessors = list(nx.ancestors(dependency_graph, deal_id))
            
            # Ensure only valid deals are considered
            valid_predecessors = [p for p in predecessors if p in valid_deals]
            
            if not valid_predecessors:
                # No dependencies, can start at time 0
                earliest_start_times[deal_id] = 0
            else:
                # Calculate earliest start time based on dependencies
                max_end_time = 0
                for pred_id in valid_predecessors:
                    pred_start = earliest_start_times.get(pred_id, 0)
                    pred_duration = self.hypergraph.deals[pred_id].implementation_time
                    pred_end = pred_start + pred_duration
                    max_end_time = max(max_end_time, pred_end)
                
                earliest_start_times[deal_id] = max_end_time
        
        # Create milestones based on start times
        milestones = defaultdict(list)
        for deal_id, start_time in earliest_start_times.items():
            milestones[start_time].append(deal_id)
        
        # Convert to regular dictionary
        milestones_dict = {time: deals for time, deals in milestones.items()}
        
        # Create dependencies dictionary
        dependencies_dict = {}
        for deal_id in valid_deals:
            # Get direct dependencies (predecessors)
            direct_deps = list(dependency_graph.predecessors(deal_id))
            
            # Only include valid deals
            valid_deps = [d for d in direct_deps if d in valid_deals]
            
            if valid_deps:
                dependencies_dict[deal_id] = valid_deps
        
        # Create roadmap
        roadmap = DealRoadmap(
            id=f"ROADMAP-{int(time.time())}-{hash(''.join(sorted(valid_deals))) % 10000:04d}",
            deal_ids=valid_deals,
            total_value=total_value,
            total_time=max_time,
            critical_path=critical_path,
            milestones=milestones_dict,
            dependencies=dependencies_dict
        )
        
        # Calculate entity values
        entity_values = {}
        for entity_id in self.hypergraph.entities:
            # Calculate value for this entity from selected deals
            entity_value = 0.0
            
            for deal_id in valid_deals:
                deal = self.hypergraph.deals[deal_id]
                
                if entity_id in deal.entity_ids:
                    # Get value edges for this entity in this deal
                    value_edges = [
                        self.hypergraph.value_edges[edge_id]
                        for edge_id in deal.value_edge_ids
                        if edge_id in self.hypergraph.value_edges
                    ]
                    
                    # Calculate incoming and outgoing value
                    for edge in value_edges:
                        # Incoming value
                        if entity_id in edge.target_ids:
                            entity_value += edge.value_amount * edge.probability
                        
                        # Outgoing value
                        if entity_id in edge.source_ids:
                            entity_value -= edge.value_amount * edge.probability
            
            entity_values[entity_id] = entity_value
        
        # Check constraint satisfaction
        constraint_satisfaction = {
            "min_entity_value": all(v >= self.settings["min_entity_value"] for v in entity_values.values()),
            "max_complexity": sum(self.hypergraph.deals[d].complexity for d in valid_deals) <= self.settings["max_complexity"],
            "max_implementation_time": max_time <= self.settings["max_implementation_time"],
            "max_roadmap_length": len(valid_deals) <= self.settings["max_roadmap_length"]
        }
        
        # Calculate risk assessment
        risk_assessment = {
            "complexity_risk": sum(self.hypergraph.deals[d].complexity for d in valid_deals) / self.settings["max_complexity"],
            "time_risk": max_time / self.settings["max_implementation_time"],
            "dependency_risk": len(dependencies_dict) / (len(valid_deals) if valid_deals else 1),
            "overall_risk": 0.0  # Will be calculated below
        }
        
        # Calculate overall risk (weighted average)
        risk_assessment["overall_risk"] = (
            risk_assessment["complexity_risk"] * 0.4 +
            risk_assessment["time_risk"] * 0.4 +
            risk_assessment["dependency_risk"] * 0.2
        )
        
        # Calculate value curve
        value_curve = self._calculate_value_curve(valid_deals, earliest_start_times)
        
        # Create optimization result
        result = OptimizationResult(
            roadmap=roadmap,
            value_curve=value_curve,
            entity_value=entity_values,
            constraint_satisfaction=constraint_satisfaction,
            risk_assessment=risk_assessment
        )
        
        return result
    
    def _calculate_value_curve(
        self, 
        deal_ids: List[str], 
        start_times: Dict[str, int]
    ) -> Dict[int, float]:
        """
        Calculate the cumulative value curve over time.
        
        Args:
            deal_ids: List of deal IDs
            start_times: Dictionary mapping deal IDs to start times
            
        Returns:
            Dictionary mapping time points to cumulative value
        """
        # Calculate end time for each deal
        end_times = {}
        for deal_id in deal_ids:
            if deal_id in self.hypergraph.deals and deal_id in start_times:
                deal = self.hypergraph.deals[deal_id]
                start_time = start_times[deal_id]
                end_times[deal_id] = start_time + deal.implementation_time
        
        # Get all time points
        time_points = sorted(set(list(start_times.values()) + list(end_times.values())))
        
        # Calculate cumulative value at each time point
        value_curve = {}
        cumulative_value = 0.0
        
        for time_point in time_points:
            # Add value for deals completed at this time
            for deal_id, end_time in end_times.items():
                if end_time == time_point:
                    deal = self.hypergraph.deals[deal_id]
                    cumulative_value += deal.total_value
            
            # Store cumulative value at this time point
            value_curve[time_point] = cumulative_value
        
        return value_curve
    
    def _create_empty_optimization_result(self) -> OptimizationResult:
        """
        Create an empty optimization result.
        
        Returns:
            OptimizationResult object
        """
        roadmap = DealRoadmap(
            id=f"EMPTY-ROADMAP-{int(time.time())}",
            deal_ids=[],
            total_value=0.0,
            total_time=0,
            critical_path=[],
            milestones={},
            dependencies={}
        )
        
        return OptimizationResult(
            roadmap=roadmap,
            value_curve={0: 0.0},
            entity_value={},
            constraint_satisfaction={
                "min_entity_value": True,
                "max_complexity": True,
                "max_implementation_time": True,
                "max_roadmap_length": True
            },
            risk_assessment={
                "complexity_risk": 0.0,
                "time_risk": 0.0,
                "dependency_risk": 0.0,
                "overall_risk": 0.0
            }
        )
    
    def generate_alternative_roadmaps(
        self,
        base_result: OptimizationResult,
        num_alternatives: int = 3,
        variation_factor: float = 0.3
    ) -> List[OptimizationResult]:
        """
        Generate alternative roadmaps by varying the base roadmap.
        
        Args:
            base_result: Base optimization result
            num_alternatives: Number of alternatives to generate
            variation_factor: Factor controlling how different alternatives should be
            
        Returns:
            List of alternative OptimizationResult objects
        """
        alternatives = []
        
        # Get base roadmap deals
        base_deals = set(base_result.roadmap.deal_ids)
        
        # If base roadmap is empty, return empty list
        if not base_deals:
            return alternatives
        
        # Get all deals not in the base roadmap
        other_deals = set(self.hypergraph.deals.keys()) - base_deals
        
        for i in range(num_alternatives):
            # Determine how many deals to swap
            num_to_swap = max(1, int(len(base_deals) * variation_factor))
            
            # Randomly select deals to remove from base roadmap
            if len(base_deals) <= num_to_swap:
                deals_to_remove = list(base_deals)
            else:
                deals_to_remove = list(np.random.choice(list(base_deals), num_to_swap, replace=False))
            
            # Randomly select deals to add from other deals
            if len(other_deals) <= num_to_swap:
                deals_to_add = list(other_deals)
            else:
                deals_to_add = list(np.random.choice(list(other_deals), num_to_swap, replace=False))
            
            # Create new deal selection
            new_deals = list((base_deals - set(deals_to_remove)) | set(deals_to_add))
            
            # Optimize with the new selection
            new_result = self._finalize_roadmap(new_deals, self.hypergraph.generate_deal_graph())
            
            # Add to alternatives
            alternatives.append(new_result)
        
        return alternatives
    
    def visualize_roadmap(self, result: OptimizationResult) -> Dict[str, str]:
        """
        Generate visualizations for an optimization result.
        
        Args:
            result: OptimizationResult object
            
        Returns:
            Dictionary mapping visualization names to base64-encoded PNG images
        """
        visualizations = {}
        
        # Generate Gantt chart for the roadmap
        visualizations["gantt_chart"] = self._generate_gantt_chart(result)
        
        # Generate value curve chart
        visualizations["value_curve"] = self._generate_value_curve_chart(result)
        
        # Generate entity value chart
        visualizations["entity_value"] = self._generate_entity_value_chart(result)
        
        # Generate risk assessment chart
        visualizations["risk_assessment"] = self._generate_risk_assessment_chart(result)
        
        return visualizations
    
    def _generate_gantt_chart(self, result: OptimizationResult) -> str:
        """
        Generate a Gantt chart for the roadmap.
        
        Args:
            result: OptimizationResult object
            
        Returns:
            Base64-encoded PNG image
        """
        # Get roadmap
        roadmap = result.roadmap
        
        # Get deal start times
        start_times = {}
        for time, deals in roadmap.milestones.items():
            for deal_id in deals:
                start_times[deal_id] = int(time)
        
        # Get critical path
        critical_path = set(roadmap.critical_path)
        
        # Calculate end times and collect deal information
        deals_info = []
        for deal_id in roadmap.deal_ids:
            if deal_id in self.hypergraph.deals and deal_id in start_times:
                deal = self.hypergraph.deals[deal_id]
                start_time = start_times[deal_id]
                end_time = start_time + deal.implementation_time
                
                deals_info.append({
                    "id": deal_id,
                    "name": deal.deal_type,
                    "start": start_time,
                    "end": end_time,
                    "value": deal.total_value,
                    "is_critical": deal_id in critical_path
                })
        
        # Sort by start time
        deals_info.sort(key=lambda d: (d["start"], -d["value"]))
        
        # Set up plot
        fig, ax = plt.figure(figsize=(12, 8)), plt.gca()
        
        # Plot bars
        for i, deal in enumerate(deals_info):
            if deal["is_critical"]:
                color = 'crimson'
                alpha = 0.7
                edgecolor = 'darkred'
            else:
                color = 'steelblue'
                alpha = 0.6
                edgecolor = 'navy'
            
            # Draw bar
            ax.barh(i, deal["end"] - deal["start"], left=deal["start"], 
                   height=0.5, alpha=alpha, color=color, edgecolor=edgecolor)
            
            # Add text label
            ax.text(deal["start"] + (deal["end"] - deal["start"]) / 2, i, 
                   f"{deal['id']}\n({deal['value']:.1f})", 
                   ha='center', va='center', color='white', fontweight='bold')
        
        # Set y-ticks and labels
        ax.set_yticks(range(len(deals_info)))
        ax.set_yticklabels([f"{deal['name']}" for deal in deals_info])
        
        # Set x-axis label
        ax.set_xlabel('Time')
        
        # Set title
        plt.title(f"Deal Roadmap Gantt Chart (Total Value: {roadmap.total_value:.1f}, Time: {roadmap.total_time})")
        
        # Add grid
        ax.grid(axis='x', alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _generate_value_curve_chart(self, result: OptimizationResult) -> str:
        """
        Generate a value curve chart.
        
        Args:
            result: OptimizationResult object
            
        Returns:
            Base64-encoded PNG image
        """
        # Set up plot
        plt.figure(figsize=(10, 6))
        
        # Get value curve data
        times = sorted(result.value_curve.keys())
        values = [result.value_curve[t] for t in times]
        
        # Plot value curve
        plt.plot(times, values, 'b-', marker='o')
        
        # Fill area under curve
        plt.fill_between(times, values, alpha=0.2)
        
        # Set labels and title
        plt.xlabel('Time')
        plt.ylabel('Cumulative Value')
        plt.title('Value Accumulation Over Time')
        
        # Add grid
        plt.grid(alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _generate_entity_value_chart(self, result: OptimizationResult) -> str:
        """
        Generate an entity value chart.
        
        Args:
            result: OptimizationResult object
            
        Returns:
            Base64-encoded PNG image
        """
        # Set up plot
        plt.figure(figsize=(12, 8))
        
        # Get entity values
        entities = []
        values = []
        colors = []
        
        # Define colors by entity type
        color_map = {
            'government': 'royalblue',
            'corporate': 'forestgreen',
            'ngo': 'firebrick',
            'civilian': 'darkviolet'
        }
        
        # Collect entity information
        for entity_id, value in result.entity_value.items():
            if entity_id in self.hypergraph.entities:
                entity = self.hypergraph.entities[entity_id]
                entities.append(entity.name)
                values.append(value)
                colors.append(color_map.get(entity.type, 'gray'))
        
        # Sort by value (descending)
        sorted_data = sorted(zip(entities, values, colors), key=lambda x: x[1], reverse=True)
        sorted_entities, sorted_values, sorted_colors = zip(*sorted_data) if sorted_data else ([], [], [])
        
        # Plot horizontal bars
        y_pos = range(len(sorted_entities))
        plt.barh(y_pos, sorted_values, color=sorted_colors)
        
        # Set y-ticks and labels
        plt.yticks(y_pos, sorted_entities)
        
        # Set labels and title
        plt.xlabel('Value')
        plt.title('Value Distribution by Entity')
        
        # Add reference line at 0
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Add grid
        plt.grid(axis='x', alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _generate_risk_assessment_chart(self, result: OptimizationResult) -> str:
        """
        Generate a risk assessment chart.
        
        Args:
            result: OptimizationResult object
            
        Returns:
            Base64-encoded PNG image
        """
        # Set up plot
        plt.figure(figsize=(10, 8))
        
        # Get risk factors
        categories = ['Complexity Risk', 'Time Risk', 'Dependency Risk', 'Overall Risk']
        values = [
            result.risk_assessment['complexity_risk'],
            result.risk_assessment['time_risk'],
            result.risk_assessment['dependency_risk'],
            result.risk_assessment['overall_risk']
        ]
        
        # Create barplot
        colors = ['#ff9999', '#ffcc99', '#ffff99', '#ff6666']
        y_pos = range(len(categories))
        
        plt.barh(y_pos, values, color=colors)
        
        # Add risk level indicator lines
        plt.axvline(x=0.33, color='g', linestyle='--', alpha=0.7, label='Low Risk')
        plt.axvline(x=0.66, color='y', linestyle='--', alpha=0.7, label='Medium Risk')
        plt.axvline(x=1.0, color='r', linestyle='--', alpha=0.7, label='High Risk')
        
        # Set y-ticks and labels
        plt.yticks(y_pos, categories)
        
        # Set labels and title
        plt.xlabel('Risk Level')
        plt.title('Risk Assessment')
        
        # Add legend
        plt.legend()
        
        # Add grid
        plt.grid(axis='x', alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')

# =============================================================================
# Utility Functions
# =============================================================================

def generate_example_hypergraph() -> DealHypergraph:
    """
    Generate an example deal hypergraph for testing.
    
    Returns:
        DealHypergraph object
    """
    # Create hypergraph
    hypergraph = DealHypergraph()
    
    # Create entities
    entities = [
        EntityNode(
            id="GOV-001",
            name="Federal Agency",
            type="government",
            attributes={"level": "federal", "domain": "regulation"},
            capabilities={"policy": 0.9, "funding": 0.8, "coordination": 0.7},
            needs={"data": 0.8, "expertise": 0.6},
            constraints={"budget": 1000000, "timeline": 36},
            connections=set()
        ),
        EntityNode(
            id="GOV-002",
            name="State Agency",
            type="government",
            attributes={"level": "state", "domain": "implementation"},
            capabilities={"local_knowledge": 0.9, "implementation": 0.8},
            needs={"funding": 0.8, "guidance": 0.7},
            constraints={"budget": 500000, "timeline": 24},
            connections=set()
        ),
        EntityNode(
            id="CORP-001",
            name="Technology Company",
            type="corporate",
            attributes={"industry": "technology", "size": "large"},
            capabilities={"technology": 0.9, "implementation": 0.8, "innovation": 0.9},
            needs={"market_access": 0.8, "regulatory_clarity": 0.7},
            constraints={"roi": 0.15, "timeline": 18},
            connections=set()
        ),
        EntityNode(
            id="NGO-001",
            name="Environmental NGO",
            type="ngo",
            attributes={"focus": "environment", "reach": "national"},
            capabilities={"stakeholder_engagement": 0.9, "expertise": 0.8},
            needs={"data": 0.7, "influence": 0.8},
            constraints={"mission_alignment": 0.8, "timeline": 30},
            connections=set()
        ),
        EntityNode(
            id="CIV-001",
            name="Community Group",
            type="civilian",
            attributes={"region": "urban", "focus": "local"},
            capabilities={"local_knowledge": 0.9, "grassroots_support": 0.8},
            needs={"resources": 0.9, "voice": 0.8},
            constraints={"capacity": 0.5, "timeline": 12},
            connections=set()
        )
    ]
    
    # Add entities to hypergraph
    for entity in entities:
        hypergraph.add_entity(entity)
        
        # Update connections
        entity.connections = set(e.id for e in entities if e.id != entity.id)
    
    # Create value edges
    value_edges = [
        ValueEdge(
            id="EDGE-001",
            source_ids=["GOV-001"],
            target_ids=["GOV-002"],
            value_type="economic",
            value_amount=500000,
            conditions={"deliverables": ["implementation_plan", "quarterly_reports"]},
            probability=0.9,
            verification_method="financial_audit"
        ),
        ValueEdge(
            id="EDGE-002",
            source_ids=["CORP-001"],
            target_ids=["GOV-001", "GOV-002"],
            value_type="economic",
            value_amount=300000,
            conditions={"deliverables": ["technology_platform", "training"]},
            probability=0.8,
            verification_method="system_acceptance"
        ),
        ValueEdge(
            id="EDGE-003",
            source_ids=["GOV-001", "CORP-001"],
            target_ids=["NGO-001"],
            value_type="social",
            value_amount=200000,
            conditions={"deliverables": ["community_engagement", "impact_assessment"]},
            probability=0.7,
            verification_method="impact_evaluation"
        ),
        ValueEdge(
            id="EDGE-004",
            source_ids=["NGO-001"],
            target_ids=["CIV-001"],
            value_type="social",
            value_amount=100000,
            conditions={"deliverables": ["local_programs", "capacity_building"]},
            probability=0.8,
            verification_method="community_feedback"
        ),
        ValueEdge(
            id="EDGE-005",
            source_ids=["CIV-001"],
            target_ids=["GOV-002"],
            value_type="political",
            value_amount=50000,
            conditions={"deliverables": ["local_support", "feedback"]},
            probability=0.6,
            verification_method="surveys"
        ),
        ValueEdge(
            id="EDGE-006",
            source_ids=["CORP-001"],
            target_ids=["CIV-001"],
            value_type="economic",
            value_amount=75000,
            conditions={"deliverables": ["jobs", "training"]},
            probability=0.7,
            verification_method="employment_records"
        ),
        ValueEdge(
            id="EDGE-007",
            source_ids=["GOV-001"],
            target_ids=["CORP-001"],
            value_type="regulatory",
            value_amount=150000,
            conditions={"deliverables": ["regulatory_framework", "permits"]},
            probability=0.8,
            verification_method="compliance_audit"
        ),
        ValueEdge(
            id="EDGE-008",
            source_ids=["GOV-002", "NGO-001"],
            target_ids=["GOV-001"],
            value_type="informational",
            value_amount=80000,
            conditions={"deliverables": ["data", "insights"]},
            probability=0.9,
            verification_method="data_quality_assessment"
        )
    ]
    
    # Add value edges to hypergraph
    for edge in value_edges:
        hypergraph.add_value_edge(edge)
    
    # Create deals
    deals = [
        DealHyperedge(
            id="DEAL-001",
            entity_ids=["GOV-001", "GOV-002", "CORP-001"],
            value_edge_ids=["EDGE-001", "EDGE-002", "EDGE-007"],
            deal_type="technology_implementation",
            total_value=950000,
            complexity=0.6,
            implementation_time=18,
            dependencies=[]
        ),
        DealHyperedge(
            id="DEAL-002",
            entity_ids=["GOV-001", "CORP-001", "NGO-001"],
            value_edge_ids=["EDGE-003", "EDGE-007"],
            deal_type="public_private_partnership",
            total_value=350000,
            complexity=0.7,
            implementation_time=24,
            dependencies=["DEAL-001"]
        ),
        DealHyperedge(
            id="DEAL-003",
            entity_ids=["NGO-001", "CIV-001", "GOV-002"],
            value_edge_ids=["EDGE-004", "EDGE-005"],
            deal_type="community_engagement",
            total_value=150000,
            complexity=0.5,
            implementation_time=12,
            dependencies=["DEAL-002"]
        ),
        DealHyperedge(
            id="DEAL-004",
            entity_ids=["CORP-001", "CIV-001"],
            value_edge_ids=["EDGE-006"],
            deal_type="workforce_development",
            total_value=75000,
            complexity=0.4,
            implementation_time=12,
            dependencies=[]
        ),
        DealHyperedge(
            id="DEAL-005",
            entity_ids=["GOV-002", "NGO-001", "GOV-001"],
            value_edge_ids=["EDGE-008"],
            deal_type="data_sharing",
            total_value=80000,
            complexity=0.3,
            implementation_time=6,
            dependencies=["DEAL-003"]
        )
    ]
    
    # Add deals to hypergraph
    for deal in deals:
        hypergraph.add_deal(deal)
    
    return hypergraph

def optimize_example():
    """Run an example optimization and print results."""
    # Generate example hypergraph
    hypergraph = generate_example_hypergraph()
    
    # Create optimizer
    optimizer = O3Optimizer(hypergraph)
    
    # Set optimization parameters
    optimizer.set_optimization_parameters(
        max_roadmap_length=5,
        max_implementation_time=36,
        max_complexity=2.0,
        min_entity_value=0.0,
        value_discount_rate=0.05,
        risk_aversion_factor=1.0
    )
    
    # Optimize roadmap
    result = optimizer.optimize_roadmap(
        objective="total_value",
        constraints={
            "max_implementation_time": 30
        },
        required_deals=["DEAL-001"],
        excluded_deals=[]
    )
    
    # Print results
    print(f"Optimization Result:")
    print(f"  Roadmap ID: {result.roadmap.id}")
    print(f"  Total Value: {result.roadmap.total_value:.2f}")
    print(f"  Total Time: {result.roadmap.total_time}")
    print(f"  Deal Count: {result.roadmap.deal_count}")
    print(f"  Critical Path: {' -> '.join(result.roadmap.critical_path)}")
    print(f"  Constraints Satisfied: {all(result.constraint_satisfaction.values())}")
    print(f"  Risk Assessment:")
    for risk_type, risk_value in result.risk_assessment.items():
        print(f"    {risk_type}: {risk_value:.2f}")
    
    # Generate alternative roadmaps
    alternatives = optimizer.generate_alternative_roadmaps(result, num_alternatives=2)
    
    # Print alternatives
    for i, alt in enumerate(alternatives):
        print(f"\nAlternative {i+1}:")
        print(f"  Total Value: {alt.roadmap.total_value:.2f}")
        print(f"  Total Time: {alt.roadmap.total_time}")
        print(f"  Deal Count: {alt.roadmap.deal_count}")

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Run example
    optimize_example()