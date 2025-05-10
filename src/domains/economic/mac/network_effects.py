"""
Network Effects modeling for Agent-Based Computational Economics (ACE).

This module implements advanced network effect models for multi-agent systems,
including knowledge diffusion, spillover effects, collaborative efficiency gains,
and emergent behavior patterns.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple, Set, Union
import logging
import math
import random
import numpy as np
from enum import Enum
from collections import defaultdict, deque
import networkx as nx


class NetworkType(Enum):
    """Types of agent networks."""
    HIERARCHICAL = "hierarchical"
    RANDOM = "random"
    SMALL_WORLD = "small_world"
    SCALE_FREE = "scale_free"
    CLUSTERED = "clustered"
    COMPLETE = "complete"


class EffectType(Enum):
    """Types of network effects."""
    DIRECT = "direct"             # Value increases with number of users
    INDIRECT = "indirect"         # Value increases via complementary goods/services
    LOCAL = "local"               # Value depends on local neighborhood
    LEARNING = "learning"         # Value increases with knowledge accumulation
    COORDINATION = "coordination" # Value depends on coordination among agents
    CONGESTION = "congestion"     # Value decreases with network saturation


class DiffusionType(Enum):
    """Types of knowledge/innovation diffusion."""
    INNOVATION = "innovation"     # Spread of new capabilities
    KNOWLEDGE = "knowledge"       # Spread of information
    BEHAVIOR = "behavior"         # Spread of behavioral patterns
    CAPABILITY = "capability"     # Spread of agent capabilities
    TRUST = "trust"               # Spread of trust relationships


class AgentNetwork:
    """
    Represents a network of connections between agents.
    
    This class uses NetworkX to model and analyze the structure of 
    agent relationships and how they affect economic outcomes.
    """
    
    def __init__(
        self,
        network_id: str,
        network_type: NetworkType,
        config: Dict[str, Any] = None
    ):
        """
        Initialize an agent network.
        
        Args:
            network_id: Unique identifier for this network
            network_type: Type of network structure
            config: Additional configuration parameters
        """
        self.network_id = network_id
        self.network_type = network_type
        self.config = config or {}
        
        # Initialize network graph
        self.graph = self._create_network_graph()
        
        # Node and edge attributes
        self.node_attributes = {}
        self.edge_weights = {}
        
        # Network statistics
        self.statistics = {}
        
        # Network effects
        self.effects = {}
        
        # Setup logging
        self.logger = logging.getLogger(f"Network.{network_id}")
    
    def _create_network_graph(self) -> nx.Graph:
        """
        Create a network graph based on the specified network type.
        
        Returns:
            NetworkX graph instance
        """
        # Default parameters
        n = self.config.get("initial_nodes", 20)
        
        # Create graph based on network type
        if self.network_type == NetworkType.HIERARCHICAL:
            # Create a hierarchical/tree-like network
            r = self.config.get("branching_factor", 2)
            h = self.config.get("height", 3)
            g = nx.balanced_tree(r, h)
            
        elif self.network_type == NetworkType.RANDOM:
            # Create an Erdős-Rényi random graph
            p = self.config.get("edge_probability", 0.2)
            g = nx.erdos_renyi_graph(n, p)
            
        elif self.network_type == NetworkType.SMALL_WORLD:
            # Create a Watts-Strogatz small-world graph
            k = self.config.get("nearest_neighbors", 4)
            p = self.config.get("rewiring_probability", 0.1)
            g = nx.watts_strogatz_graph(n, k, p)
            
        elif self.network_type == NetworkType.SCALE_FREE:
            # Create a Barabási-Albert scale-free graph
            m = self.config.get("new_edges", 2)
            g = nx.barabasi_albert_graph(n, m)
            
        elif self.network_type == NetworkType.CLUSTERED:
            # Create a graph with distinct clusters
            clusters = self.config.get("clusters", 4)
            cluster_size = n // clusters
            g = nx.Graph()
            
            # Add nodes
            for i in range(n):
                g.add_node(i)
                
            # Add edges within clusters
            for c in range(clusters):
                nodes = list(range(c * cluster_size, (c + 1) * cluster_size))
                for i in range(len(nodes)):
                    for j in range(i + 1, len(nodes)):
                        if random.random() < 0.7:  # High intra-cluster connectivity
                            g.add_edge(nodes[i], nodes[j])
            
            # Add some inter-cluster edges
            for _ in range(n // 5):  # Add n/5 inter-cluster edges
                c1 = random.randint(0, clusters - 1)
                c2 = random.randint(0, clusters - 1)
                while c2 == c1:
                    c2 = random.randint(0, clusters - 1)
                    
                n1 = random.randint(c1 * cluster_size, (c1 + 1) * cluster_size - 1)
                n2 = random.randint(c2 * cluster_size, (c2 + 1) * cluster_size - 1)
                g.add_edge(n1, n2)
                
        elif self.network_type == NetworkType.COMPLETE:
            # Create a fully connected graph
            g = nx.complete_graph(n)
            
        else:
            # Default to an empty graph
            g = nx.Graph()
            
        return g
    
    def add_agent(self, agent_id: str, attributes: Dict[str, Any] = None) -> None:
        """
        Add an agent to the network.
        
        Args:
            agent_id: Unique identifier for the agent
            attributes: Node attributes for the agent
        """
        if agent_id not in self.graph:
            self.graph.add_node(agent_id)
            self.node_attributes[agent_id] = attributes or {}
            
            # Apply network growth model to connect new agent
            self._connect_new_agent(agent_id)
            
            self.logger.info(f"Added agent {agent_id} to network {self.network_id}")
    
    def _connect_new_agent(self, agent_id: str) -> None:
        """
        Connect a newly added agent to the network according to network type.
        
        Args:
            agent_id: ID of the new agent
        """
        # Skip if network is empty (first node)
        if len(self.graph) <= 1:
            return
            
        existing_nodes = list(self.graph.nodes())
        existing_nodes.remove(agent_id)
        
        if self.network_type == NetworkType.HIERARCHICAL:
            # Connect to parent node (node with fewest children)
            parent_candidates = sorted(
                existing_nodes, 
                key=lambda n: len(list(self.graph.neighbors(n)))
            )
            if parent_candidates:
                parent = parent_candidates[0]
                self.add_connection(agent_id, parent)
                
        elif self.network_type == NetworkType.RANDOM:
            # Connect randomly with probability p
            p = self.config.get("edge_probability", 0.2)
            for node in existing_nodes:
                if random.random() < p:
                    self.add_connection(agent_id, node)
                    
        elif self.network_type == NetworkType.SMALL_WORLD:
            # Connect to k nearest neighbors (by node ID proximity)
            k = min(self.config.get("nearest_neighbors", 4), len(existing_nodes))
            nearest = existing_nodes[:k]  # Simple approximation
            for node in nearest:
                self.add_connection(agent_id, node)
                
        elif self.network_type == NetworkType.SCALE_FREE:
            # Preferential attachment - connect to nodes with higher degree
            m = min(self.config.get("new_edges", 2), len(existing_nodes))
            degrees = [self.graph.degree(n) for n in existing_nodes]
            total_degree = sum(degrees)
            
            if total_degree > 0:
                # Select nodes with probability proportional to degree
                probabilities = [d/total_degree for d in degrees]
                selected = np.random.choice(existing_nodes, size=m, replace=False, p=probabilities)
                for node in selected:
                    self.add_connection(agent_id, node)
            else:
                # If all nodes have degree 0, connect randomly
                selected = random.sample(existing_nodes, min(m, len(existing_nodes)))
                for node in selected:
                    self.add_connection(agent_id, node)
                    
        elif self.network_type == NetworkType.CLUSTERED:
            # Assign to a cluster and connect within that cluster
            clusters = self.config.get("clusters", 4)
            cluster = random.randint(0, clusters - 1)
            
            # Find nodes in the same cluster
            cluster_size = len(self.graph) // clusters
            cluster_nodes = [
                n for n in existing_nodes 
                if self.node_attributes.get(n, {}).get("cluster") == cluster
            ]
            
            # Mark this node as part of the cluster
            self.node_attributes[agent_id]["cluster"] = cluster
            
            # Connect to nodes in the same cluster with high probability
            for node in cluster_nodes:
                if random.random() < 0.7:  # High intra-cluster connectivity
                    self.add_connection(agent_id, node)
            
            # Add a few connections to other clusters
            if random.random() < 0.3:  # 30% chance of inter-cluster edge
                other_nodes = [n for n in existing_nodes if n not in cluster_nodes]
                if other_nodes:
                    other_node = random.choice(other_nodes)
                    self.add_connection(agent_id, other_node)
                    
        elif self.network_type == NetworkType.COMPLETE:
            # Connect to all existing nodes
            for node in existing_nodes:
                self.add_connection(agent_id, node)
    
    def add_connection(self, agent1_id: str, agent2_id: str, weight: float = 1.0) -> None:
        """
        Add a connection between two agents.
        
        Args:
            agent1_id: ID of first agent
            agent2_id: ID of second agent
            weight: Connection strength/weight
        """
        if agent1_id not in self.graph:
            self.add_agent(agent1_id)
            
        if agent2_id not in self.graph:
            self.add_agent(agent2_id)
            
        # Add the edge
        self.graph.add_edge(agent1_id, agent2_id, weight=weight)
        
        # Store edge weight
        self.edge_weights[(agent1_id, agent2_id)] = weight
        self.edge_weights[(agent2_id, agent1_id)] = weight
        
        self.logger.debug(f"Added connection between {agent1_id} and {agent2_id} with weight {weight}")
    
    def update_connection(self, agent1_id: str, agent2_id: str, weight: float) -> None:
        """
        Update the weight of a connection between two agents.
        
        Args:
            agent1_id: ID of first agent
            agent2_id: ID of second agent
            weight: New connection strength/weight
        """
        if self.graph.has_edge(agent1_id, agent2_id):
            self.graph[agent1_id][agent2_id]['weight'] = weight
            self.edge_weights[(agent1_id, agent2_id)] = weight
            self.edge_weights[(agent2_id, agent1_id)] = weight
            
            self.logger.debug(f"Updated connection between {agent1_id} and {agent2_id} to weight {weight}")
        else:
            self.logger.warning(f"Cannot update non-existent connection between {agent1_id} and {agent2_id}")
    
    def remove_connection(self, agent1_id: str, agent2_id: str) -> None:
        """
        Remove a connection between two agents.
        
        Args:
            agent1_id: ID of first agent
            agent2_id: ID of second agent
        """
        if self.graph.has_edge(agent1_id, agent2_id):
            self.graph.remove_edge(agent1_id, agent2_id)
            
            # Clean up edge weights
            if (agent1_id, agent2_id) in self.edge_weights:
                del self.edge_weights[(agent1_id, agent2_id)]
            if (agent2_id, agent1_id) in self.edge_weights:
                del self.edge_weights[(agent2_id, agent1_id)]
                
            self.logger.debug(f"Removed connection between {agent1_id} and {agent2_id}")
        else:
            self.logger.warning(f"Cannot remove non-existent connection between {agent1_id} and {agent2_id}")
    
    def update_agent_attribute(self, agent_id: str, attribute: str, value: Any) -> None:
        """
        Update an attribute for an agent.
        
        Args:
            agent_id: ID of the agent
            attribute: Name of the attribute
            value: New attribute value
        """
        if agent_id in self.node_attributes:
            self.node_attributes[agent_id][attribute] = value
            self.logger.debug(f"Updated attribute {attribute} for agent {agent_id}")
        else:
            self.logger.warning(f"Cannot update attribute for non-existent agent {agent_id}")
    
    def get_agent_attribute(self, agent_id: str, attribute: str, default: Any = None) -> Any:
        """
        Get an attribute value for an agent.
        
        Args:
            agent_id: ID of the agent
            attribute: Name of the attribute
            default: Default value if attribute not found
            
        Returns:
            Attribute value or default
        """
        return self.node_attributes.get(agent_id, {}).get(attribute, default)
    
    def get_neighbors(self, agent_id: str) -> List[str]:
        """
        Get all neighbors of an agent in the network.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of neighbor agent IDs
        """
        if agent_id in self.graph:
            return list(self.graph.neighbors(agent_id))
        return []
    
    def get_weighted_neighbors(self, agent_id: str) -> Dict[str, float]:
        """
        Get all neighbors of an agent with their connection weights.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary mapping neighbor IDs to connection weights
        """
        result = {}
        if agent_id in self.graph:
            for neighbor in self.graph.neighbors(agent_id):
                result[neighbor] = self.graph[agent_id][neighbor].get('weight', 1.0)
        return result
    
    def add_network_effect(
        self, 
        effect_id: str, 
        effect_type: EffectType,
        strength: float,
        config: Dict[str, Any] = None
    ) -> None:
        """
        Add a network effect to the network.
        
        Args:
            effect_id: Unique identifier for this effect
            effect_type: Type of network effect
            strength: Effect strength [0, 1]
            config: Additional configuration parameters
        """
        self.effects[effect_id] = {
            "effect_id": effect_id,
            "effect_type": effect_type,
            "strength": strength,
            "config": config or {},
            "is_active": True
        }
        
        self.logger.info(f"Added network effect {effect_id} of type {effect_type.value}")
    
    def apply_network_effects(self, agent_values: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """
        Apply network effects to transform agent values.
        
        Args:
            agent_values: Dictionary mapping agent IDs to their value dictionaries
            
        Returns:
            Updated values with network effects applied
        """
        result = {agent_id: values.copy() for agent_id, values in agent_values.items()}
        
        # Apply each active network effect
        for effect_id, effect in self.effects.items():
            if not effect["is_active"]:
                continue
                
            effect_type = effect["effect_type"]
            strength = effect["strength"]
            config = effect["config"]
            
            if effect_type == EffectType.DIRECT:
                result = self._apply_direct_network_effect(result, strength, config)
            elif effect_type == EffectType.INDIRECT:
                result = self._apply_indirect_network_effect(result, strength, config)
            elif effect_type == EffectType.LOCAL:
                result = self._apply_local_network_effect(result, strength, config)
            elif effect_type == EffectType.LEARNING:
                result = self._apply_learning_network_effect(result, strength, config)
            elif effect_type == EffectType.COORDINATION:
                result = self._apply_coordination_network_effect(result, strength, config)
            elif effect_type == EffectType.CONGESTION:
                result = self._apply_congestion_network_effect(result, strength, config)
        
        return result
    
    def _apply_direct_network_effect(
        self, 
        agent_values: Dict[str, Dict[str, float]], 
        strength: float,
        config: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Apply direct network effect (Metcalfe's Law).
        
        Direct network effects occur when the value increases with the number
        of users in the network, like phones, social media, etc.
        
        Args:
            agent_values: Agent value dictionaries
            strength: Effect strength
            config: Effect configuration
            
        Returns:
            Updated values
        """
        # Number of participants
        n = len(agent_values)
        if n <= 1:
            return agent_values
            
        # Calculate network effect multiplier
        # Traditional Metcalfe's Law: V ∝ n²
        # Alternative: V ∝ n * log(n)
        if config.get("model", "metcalfe") == "metcalfe":
            # Metcalfe's Law (n²)
            multiplier = 1.0 + strength * (n / 100.0)  # Scale with strength
        else:
            # Odlyzko's adjustment: n * log(n)
            multiplier = 1.0 + strength * (math.log(n) / 5.0)  # Smaller effect
            
        # Apply multiplier to all agents
        result = {agent_id: values.copy() for agent_id, values in agent_values.items()}
        
        # Only apply to configured resource types
        resource_types = config.get("resource_types", [])
        
        for agent_id in result:
            for resource_type in resource_types:
                if resource_type in result[agent_id]:
                    result[agent_id][resource_type] *= multiplier
        
        return result
    
    def _apply_indirect_network_effect(
        self, 
        agent_values: Dict[str, Dict[str, float]], 
        strength: float,
        config: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Apply indirect network effect (complementary goods/platforms).
        
        Indirect network effects occur when value increases due to complementary
        goods or services, like game consoles and games.
        
        Args:
            agent_values: Agent value dictionaries
            strength: Effect strength
            config: Effect configuration
            
        Returns:
            Updated values
        """
        # Get the primary and complementary resource types
        primary_type = config.get("primary_type")
        complementary_types = config.get("complementary_types", [])
        
        if not primary_type or not complementary_types:
            return agent_values
            
        result = {agent_id: values.copy() for agent_id, values in agent_values.items()}
        
        # Calculate total availability of complementary resources
        complementary_total = 0.0
        for agent_id, values in agent_values.items():
            for comp_type in complementary_types:
                complementary_total += values.get(comp_type, 0.0)
                
        # Apply effect to primary resource based on complementary resources
        if complementary_total > 0:
            for agent_id in result:
                if primary_type in result[agent_id]:
                    # Indirect effect follows a logarithmic curve
                    effect = 1.0 + strength * math.log(1 + complementary_total / 100.0)
                    result[agent_id][primary_type] *= effect
        
        return result
    
    def _apply_local_network_effect(
        self, 
        agent_values: Dict[str, Dict[str, float]], 
        strength: float,
        config: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Apply local network effect (neighborhood-based).
        
        Local network effects depend on the local neighborhood rather than
        the entire network, like messaging apps where you care about your
        immediate contacts, not all users.
        
        Args:
            agent_values: Agent value dictionaries
            strength: Effect strength
            config: Effect configuration
            
        Returns:
            Updated values
        """
        result = {agent_id: values.copy() for agent_id, values in agent_values.items()}
        
        # Resource types affected by local network effect
        resource_types = config.get("resource_types", [])
        
        # Apply neighborhood-based effect for each agent
        for agent_id in result:
            # Get agent's neighbors
            neighbors = self.get_weighted_neighbors(agent_id)
            
            if not neighbors:
                continue
                
            # Calculate local network value based on neighbors
            local_value = 0.0
            for neighbor_id, weight in neighbors.items():
                if neighbor_id in agent_values:
                    # Add weighted value from each neighbor
                    for resource_type in resource_types:
                        local_value += weight * agent_values[neighbor_id].get(resource_type, 0.0)
            
            # Apply effect to agent's resources
            local_effect = 1.0 + strength * math.tanh(local_value / 100.0)  # Bounded effect
            
            for resource_type in resource_types:
                if resource_type in result[agent_id]:
                    result[agent_id][resource_type] *= local_effect
        
        return result
    
    def _apply_learning_network_effect(
        self, 
        agent_values: Dict[str, Dict[str, float]], 
        strength: float,
        config: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Apply learning network effect (knowledge accumulation).
        
        Learning effects increase value through knowledge accumulation
        and information sharing.
        
        Args:
            agent_values: Agent value dictionaries
            strength: Effect strength
            config: Effect configuration
            
        Returns:
            Updated values
        """
        result = {agent_id: values.copy() for agent_id, values in agent_values.items()}
        
        # Knowledge attribute to track
        knowledge_attr = config.get("knowledge_attribute", "knowledge_level")
        resource_types = config.get("resource_types", [])
        
        # Apply learning effect for each agent
        for agent_id in result:
            # Get agent's knowledge level
            knowledge = self.get_agent_attribute(agent_id, knowledge_attr, 1.0)
            
            # Get agent's neighbors and their knowledge
            neighbors = self.get_neighbors(agent_id)
            neighbor_knowledge = 0.0
            
            for neighbor_id in neighbors:
                neighbor_knowledge += self.get_agent_attribute(neighbor_id, knowledge_attr, 1.0)
            
            # Calculate learning effect
            if neighbors:
                avg_neighbor_knowledge = neighbor_knowledge / len(neighbors)
                # Knowledge diffusion - learn from neighbors
                learning_rate = config.get("learning_rate", 0.1)
                new_knowledge = knowledge + learning_rate * (avg_neighbor_knowledge - knowledge)
                # Update agent's knowledge
                self.update_agent_attribute(agent_id, knowledge_attr, new_knowledge)
                
                # Apply productivity boost from knowledge
                knowledge_effect = 1.0 + strength * math.log(1 + new_knowledge)
                
                for resource_type in resource_types:
                    if resource_type in result[agent_id]:
                        result[agent_id][resource_type] *= knowledge_effect
        
        return result
    
    def _apply_coordination_network_effect(
        self, 
        agent_values: Dict[str, Dict[str, float]], 
        strength: float,
        config: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Apply coordination network effect (alignment benefit).
        
        Coordination effects depend on how well agents are aligned
        or coordinated in their strategies or behaviors.
        
        Args:
            agent_values: Agent value dictionaries
            strength: Effect strength
            config: Effect configuration
            
        Returns:
            Updated values
        """
        result = {agent_id: values.copy() for agent_id, values in agent_values.items()}
        
        # Coordination attribute to track
        coord_attr = config.get("coordination_attribute", "strategy")
        resource_types = config.get("resource_types", [])
        
        # Calculate strategy entropy and coordination
        strategies = {}
        for agent_id in result:
            agent_strategy = self.get_agent_attribute(agent_id, coord_attr, "default")
            strategies[agent_id] = agent_strategy
        
        # Count strategy frequencies
        strategy_counts = defaultdict(int)
        for strategy in strategies.values():
            strategy_counts[strategy] += 1
            
        total_agents = len(strategies)
        
        # Apply coordination effect for each agent
        for agent_id in result:
            agent_strategy = strategies.get(agent_id, "default")
            
            # Calculate coordination level based on how many other agents
            # have the same strategy
            if total_agents > 1:
                same_strategy_count = strategy_counts[agent_strategy]
                coordination_level = (same_strategy_count - 1) / (total_agents - 1)
                
                # Apply coordination effect
                # Higher coordination = higher boost, scaled by strength
                coord_effect = 1.0 + strength * coordination_level
                
                for resource_type in resource_types:
                    if resource_type in result[agent_id]:
                        result[agent_id][resource_type] *= coord_effect
        
        return result
    
    def _apply_congestion_network_effect(
        self, 
        agent_values: Dict[str, Dict[str, float]], 
        strength: float,
        config: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Apply congestion network effect (negative scaling).
        
        Congestion effects represent diminishing returns or negative
        network effects when the network gets too crowded.
        
        Args:
            agent_values: Agent value dictionaries
            strength: Effect strength
            config: Effect configuration
            
        Returns:
            Updated values
        """
        result = {agent_id: values.copy() for agent_id, values in agent_values.items()}
        
        # Resource types affected by congestion
        resource_types = config.get("resource_types", [])
        
        # Calculate total usage/congestion
        total_usage = {}
        for resource_type in resource_types:
            total_usage[resource_type] = sum(
                values.get(resource_type, 0.0) 
                for values in agent_values.values()
            )
        
        # Apply congestion effect
        for agent_id in result:
            for resource_type in resource_types:
                if resource_type in result[agent_id]:
                    # Calculate congestion level
                    capacity = config.get(f"{resource_type}_capacity", 1000.0)
                    usage = total_usage.get(resource_type, 0.0)
                    
                    if capacity > 0:
                        congestion_level = usage / capacity
                        
                        # Apply congestion effect (reduces value as congestion increases)
                        # Use a sigmoid function to model congestion
                        congestion_threshold = config.get("congestion_threshold", 0.7)
                        if congestion_level > congestion_threshold:
                            # Calculate penalty (stronger as congestion increases)
                            x = (congestion_level - congestion_threshold) / (1 - congestion_threshold)
                            penalty = strength * (1 / (1 + math.exp(-10 * (x - 0.5))))
                            congestion_effect = 1.0 - penalty
                            result[agent_id][resource_type] *= max(0.1, congestion_effect)
        
        return result
    
    def calculate_network_statistics(self) -> Dict[str, Any]:
        """
        Calculate various network statistics and properties.
        
        Returns:
            Dictionary of network statistics
        """
        # Basic statistics
        nodes = len(self.graph)
        edges = self.graph.number_of_edges()
        
        stats = {
            "nodes": nodes,
            "edges": edges,
            "density": 0.0
        }
        
        # Skip detailed analysis for empty or singleton graphs
        if nodes <= 1:
            return stats
            
        # Network density
        stats["density"] = 2 * edges / (nodes * (nodes - 1))
        
        try:
            # Connected components
            components = list(nx.connected_components(self.graph))
            stats["components"] = len(components)
            
            # Largest component size
            stats["largest_component_size"] = len(max(components, key=len))
            
            # Average degree
            degrees = dict(self.graph.degree())
            stats["avg_degree"] = sum(degrees.values()) / nodes
            stats["max_degree"] = max(degrees.values()) if degrees else 0
            
            # Check if graph is connected before calculating path-based metrics
            if nx.is_connected(self.graph):
                # Average shortest path length
                stats["avg_path_length"] = nx.average_shortest_path_length(self.graph)
                
                # Diameter (maximum shortest path)
                stats["diameter"] = nx.diameter(self.graph)
                
                # Calculate average clustering coefficient
                stats["clustering_coefficient"] = nx.average_clustering(self.graph)
                
                # Network centralization
                centrality = nx.degree_centrality(self.graph)
                max_centrality = max(centrality.values())
                sum_centrality_diff = sum(max_centrality - c for c in centrality.values())
                max_sum_diff = (nodes - 1) * (nodes - 1) / nodes
                stats["centralization"] = sum_centrality_diff / max_sum_diff if max_sum_diff > 0 else 0
            else:
                # For disconnected graphs, calculate metrics on largest component
                largest_component = max(components, key=len)
                subgraph = self.graph.subgraph(largest_component)
                
                stats["note"] = "Graph is disconnected. Path metrics calculated on largest component."
                stats["avg_path_length"] = nx.average_shortest_path_length(subgraph)
                stats["diameter"] = nx.diameter(subgraph)
                stats["clustering_coefficient"] = nx.average_clustering(subgraph)
        
        except Exception as e:
            stats["error"] = str(e)
            self.logger.warning(f"Error calculating network statistics: {str(e)}")
        
        # Store statistics
        self.statistics = stats
        return stats
    
    def calculate_centrality(self, centrality_type: str = "degree") -> Dict[str, float]:
        """
        Calculate node centrality measures.
        
        Args:
            centrality_type: Type of centrality measure
                             ("degree", "betweenness", "closeness", "eigenvector")
                             
        Returns:
            Dictionary mapping node IDs to centrality values
        """
        if len(self.graph) <= 1:
            return {node: 0.0 for node in self.graph.nodes()}
            
        try:
            if centrality_type == "degree":
                return nx.degree_centrality(self.graph)
            elif centrality_type == "betweenness":
                return nx.betweenness_centrality(self.graph)
            elif centrality_type == "closeness":
                if nx.is_connected(self.graph):
                    return nx.closeness_centrality(self.graph)
                else:
                    # For disconnected graphs, calculate on largest component
                    components = list(nx.connected_components(self.graph))
                    largest_component = max(components, key=len)
                    subgraph = self.graph.subgraph(largest_component)
                    closeness = nx.closeness_centrality(subgraph)
                    # Assign zero to nodes not in largest component
                    return {node: closeness.get(node, 0.0) for node in self.graph.nodes()}
            elif centrality_type == "eigenvector":
                try:
                    return nx.eigenvector_centrality(self.graph, max_iter=1000)
                except:
                    # Fallback to degree centrality if eigenvector doesn't converge
                    return nx.degree_centrality(self.graph)
            else:
                self.logger.warning(f"Unknown centrality type: {centrality_type}")
                return {node: 0.0 for node in self.graph.nodes()}
                
        except Exception as e:
            self.logger.warning(f"Error calculating {centrality_type} centrality: {str(e)}")
            return {node: 0.0 for node in self.graph.nodes()}
    
    def identify_communities(self) -> Dict[str, int]:
        """
        Identify communities/clusters in the network.
        
        Returns:
            Dictionary mapping node IDs to community IDs
        """
        if len(self.graph) <= 1:
            return {node: 0 for node in self.graph.nodes()}
            
        try:
            # Use Louvain method for community detection
            communities = nx.community.louvain_communities(self.graph)
            
            # Map nodes to community IDs
            result = {}
            for i, community in enumerate(communities):
                for node in community:
                    result[node] = i
                    
            return result
            
        except Exception as e:
            self.logger.warning(f"Error identifying communities: {str(e)}")
            return {node: 0 for node in self.graph.nodes()}
    
    def simulate_diffusion(
        self, 
        diffusion_type: DiffusionType,
        initial_adopters: List[str],
        steps: int = 10,
        config: Dict[str, Any] = None
    ) -> Dict[int, Dict[str, float]]:
        """
        Simulate the diffusion of innovations, knowledge, or behavior.
        
        Args:
            diffusion_type: Type of diffusion process
            initial_adopters: List of nodes that start with the innovation
            steps: Number of diffusion steps to simulate
            config: Additional configuration parameters
            
        Returns:
            Dictionary mapping time steps to adoption levels
        """
        result = {}
        cfg = config or {}
        
        # Initialize adoption levels
        adoption = {node: 0.0 for node in self.graph.nodes()}
        for node in initial_adopters:
            if node in adoption:
                adoption[node] = 1.0
        
        # Store initial state
        result[0] = adoption.copy()
        
        # Get diffusion parameters
        adoption_threshold = cfg.get("adoption_threshold", 0.5)
        social_influence = cfg.get("social_influence", 0.3)
        individual_factors = cfg.get("individual_factors", {})
        decay_rate = cfg.get("decay_rate", 0.05)
        
        # Simulation parameters based on diffusion type
        if diffusion_type == DiffusionType.INNOVATION:
            # Innovations often follow S-curve adoption
            adoption_threshold = cfg.get("adoption_threshold", 0.6)  # Higher threshold
            social_influence = cfg.get("social_influence", 0.4)  # Higher social influence
            
        elif diffusion_type == DiffusionType.KNOWLEDGE:
            # Knowledge spreads more easily
            adoption_threshold = cfg.get("adoption_threshold", 0.3)  # Lower threshold
            decay_rate = cfg.get("decay_rate", 0.02)  # Slower decay
            
        elif diffusion_type == DiffusionType.BEHAVIOR:
            # Behaviors are influenced by social norms
            adoption_threshold = cfg.get("adoption_threshold", 0.4)  # Medium threshold
            social_influence = cfg.get("social_influence", 0.5)  # High social influence
            
        elif diffusion_type == DiffusionType.CAPABILITY:
            # Capabilities require time to develop
            adoption_threshold = cfg.get("adoption_threshold", 0.7)  # Higher threshold
            social_influence = cfg.get("social_influence", 0.2)  # Lower social influence
            
        elif diffusion_type == DiffusionType.TRUST:
            # Trust builds gradually
            adoption_threshold = cfg.get("adoption_threshold", 0.8)  # Higher threshold
            social_influence = cfg.get("social_influence", 0.6)  # Higher social influence
            decay_rate = cfg.get("decay_rate", 0.1)  # Faster decay
        
        # Run simulation for specified steps
        for step in range(1, steps + 1):
            # Calculate new adoption levels
            new_adoption = adoption.copy()
            
            for node in self.graph.nodes():
                # Get node's current adoption level
                current_level = adoption[node]
                
                # Apply decay
                if current_level > 0:
                    current_level = max(0, current_level - decay_rate)
                
                # Get neighbors and their adoption levels
                neighbors = self.get_weighted_neighbors(node)
                if not neighbors:
                    new_adoption[node] = current_level
                    continue
                
                # Calculate social influence from neighbors
                social_pressure = 0.0
                total_weight = 0.0
                
                for neighbor, weight in neighbors.items():
                    social_pressure += weight * adoption[neighbor]
                    total_weight += weight
                
                if total_weight > 0:
                    avg_neighbor_adoption = social_pressure / total_weight
                else:
                    avg_neighbor_adoption = 0.0
                
                # Get individual adoption factor
                individual_factor = individual_factors.get(node, 1.0)
                
                # Calculate new adoption level
                # Bass diffusion model: combines individual adoption and social influence
                p = cfg.get("innovation_coefficient", 0.03)  # Individual adoption
                q = social_influence  # Social influence
                
                # Probability of adoption at this step
                non_adopters = 1.0 - current_level
                adoption_prob = (p + q * avg_neighbor_adoption) * non_adopters
                
                # Apply individual factor
                adoption_prob *= individual_factor
                
                # Calculate new level
                new_level = current_level + adoption_prob
                
                # Apply threshold effects
                if new_level > adoption_threshold and current_level < adoption_threshold:
                    # Crossing threshold gives a boost
                    new_level += 0.2
                
                # Ensure bounds
                new_level = max(0.0, min(1.0, new_level))
                
                # Update adoption
                new_adoption[node] = new_level
            
            # Update adoption for next step
            adoption = new_adoption
            
            # Store state for this step
            result[step] = adoption.copy()
        
        return result
    
    def get_network_visualization_data(self) -> Dict[str, Any]:
        """
        Get data for visualizing the network.
        
        Returns:
            Dictionary with network visualization data
        """
        # Calculate positions using spring layout
        try:
            pos = nx.spring_layout(self.graph)
            
            # Extract nodes with positions
            nodes = []
            for node in self.graph.nodes():
                x, y = pos[node]
                node_data = {
                    "id": node,
                    "x": float(x),
                    "y": float(y),
                    "attributes": self.node_attributes.get(node, {})
                }
                nodes.append(node_data)
            
            # Extract edges with weights
            edges = []
            for source, target in self.graph.edges():
                weight = self.graph[source][target].get('weight', 1.0)
                edge_data = {
                    "source": source,
                    "target": target,
                    "weight": weight
                }
                edges.append(edge_data)
            
            # Get community structure
            communities = self.identify_communities()
            
            # Calculate centrality
            degree_centrality = self.calculate_centrality("degree")
            
            # Add centrality and community data to nodes
            for node_data in nodes:
                node_id = node_data["id"]
                node_data["centrality"] = degree_centrality.get(node_id, 0.0)
                node_data["community"] = communities.get(node_id, 0)
            
            return {
                "nodes": nodes,
                "edges": edges,
                "communities": len(set(communities.values())),
                "statistics": self.statistics
            }
            
        except Exception as e:
            self.logger.warning(f"Error generating visualization data: {str(e)}")
            return {
                "nodes": [],
                "edges": [],
                "error": str(e)
            }


class KnowledgeDiffusionModel:
    """
    Models the diffusion of knowledge, skills, and capabilities across agent networks.
    """
    
    def __init__(
        self,
        network: AgentNetwork,
        config: Dict[str, Any] = None
    ):
        """
        Initialize a knowledge diffusion model.
        
        Args:
            network: Agent network
            config: Configuration parameters
        """
        self.network = network
        self.config = config or {}
        
        # Knowledge tracking
        self.knowledge_domains = {}
        self.agent_knowledge = {}
        
        # Learning parameters
        self.learning_rates = {}
        self.time_step = 0
        
        # Setup logging
        self.logger = logging.getLogger(f"KnowledgeDiffusion.{network.network_id}")
    
    def add_knowledge_domain(
        self, 
        domain_id: str, 
        complexity: float,
        prerequisites: List[str] = None
    ) -> None:
        """
        Add a knowledge domain to the model.
        
        Args:
            domain_id: Unique identifier for the domain
            complexity: Complexity level [0, 1]
            prerequisites: List of prerequisite domains
        """
        self.knowledge_domains[domain_id] = {
            "domain_id": domain_id,
            "complexity": complexity,
            "prerequisites": prerequisites or []
        }
        
        self.logger.info(f"Added knowledge domain {domain_id} with complexity {complexity}")
    
    def initialize_agent_knowledge(
        self,
        agent_id: str,
        domains: Dict[str, float] = None,
        learning_rate: float = 0.1
    ) -> None:
        """
        Initialize an agent's knowledge levels.
        
        Args:
            agent_id: Agent ID
            domains: Dictionary mapping domain IDs to knowledge levels
            learning_rate: Agent's learning rate
        """
        # Ensure agent is in the network
        if agent_id not in self.network.graph:
            self.network.add_agent(agent_id)
            
        # Initialize knowledge
        self.agent_knowledge[agent_id] = domains or {}
        
        # Set learning rate
        self.learning_rates[agent_id] = learning_rate
        
        # Initialize domains not included
        for domain_id in self.knowledge_domains:
            if domain_id not in self.agent_knowledge[agent_id]:
                self.agent_knowledge[agent_id][domain_id] = 0.0
                
        self.logger.debug(f"Initialized knowledge for agent {agent_id}")
    
    def update_knowledge(self, steps: int = 1) -> Dict[str, Dict[str, float]]:
        """
        Update knowledge levels for all agents.
        
        Args:
            steps: Number of update steps
            
        Returns:
            Updated agent knowledge levels
        """
        for _ in range(steps):
            self._perform_knowledge_update()
            self.time_step += 1
            
        return self.agent_knowledge
    
    def _perform_knowledge_update(self) -> None:
        """Perform a single knowledge update step."""
        # For each agent, update knowledge based on neighbors and self-learning
        new_knowledge = {agent_id: domains.copy() for agent_id, domains in self.agent_knowledge.items()}
        
        for agent_id, domains in self.agent_knowledge.items():
            # Get agent's learning rate
            learning_rate = self.learning_rates.get(agent_id, 0.1)
            
            # Get agent's neighbors
            neighbors = self.network.get_weighted_neighbors(agent_id)
            
            # Update each knowledge domain
            for domain_id, level in domains.items():
                if domain_id not in self.knowledge_domains:
                    continue
                    
                domain = self.knowledge_domains[domain_id]
                
                # Check prerequisites
                prerequisites_met = True
                for prereq in domain.get("prerequisites", []):
                    if prereq in domains and domains[prereq] < 0.5:
                        prerequisites_met = False
                        break
                
                if not prerequisites_met:
                    continue
                
                # Calculate knowledge transfer from neighbors
                if neighbors:
                    neighbor_knowledge = 0.0
                    total_weight = 0.0
                    
                    for neighbor_id, weight in neighbors.items():
                        if neighbor_id in self.agent_knowledge and domain_id in self.agent_knowledge[neighbor_id]:
                            neighbor_level = self.agent_knowledge[neighbor_id][domain_id]
                            # Only learn from neighbors with higher knowledge
                            if neighbor_level > level:
                                neighbor_knowledge += weight * neighbor_level
                                total_weight += weight
                    
                    if total_weight > 0:
                        # Social learning
                        social_learning = neighbor_knowledge / total_weight
                        
                        # Calculate complexity factor (harder domains are harder to learn)
                        complexity = domain.get("complexity", 0.5)
                        complexity_factor = 1.0 - 0.5 * complexity
                        
                        # Apply learning
                        knowledge_gap = social_learning - level
                        new_knowledge[agent_id][domain_id] += learning_rate * complexity_factor * knowledge_gap
                
                # Independent learning (diminishing returns)
                if level > 0:  # Can only improve through practice if some knowledge exists
                    # Sigmoid curve for independent learning
                    independent_learning = 0.01 * (1.0 / (1 + math.exp(-10 * (level - 0.5))))
                    new_knowledge[agent_id][domain_id] += independent_learning
                
                # Ensure bounds
                new_knowledge[agent_id][domain_id] = max(0.0, min(1.0, new_knowledge[agent_id][domain_id]))
        
        # Update knowledge
        self.agent_knowledge = new_knowledge
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about knowledge distribution.
        
        Returns:
            Dictionary of knowledge statistics
        """
        if not self.agent_knowledge:
            return {"error": "No agent knowledge initialized"}
            
        stats = {
            "time_step": self.time_step,
            "agents": len(self.agent_knowledge),
            "domains": len(self.knowledge_domains),
            "domain_stats": {},
            "overall": {}
        }
        
        # Calculate statistics for each domain
        for domain_id in self.knowledge_domains:
            domain_levels = [
                agent_domains.get(domain_id, 0.0) 
                for agent_domains in self.agent_knowledge.values()
            ]
            
            stats["domain_stats"][domain_id] = {
                "mean": np.mean(domain_levels),
                "median": np.median(domain_levels),
                "max": np.max(domain_levels),
                "min": np.min(domain_levels),
                "std": np.std(domain_levels),
                "experts": sum(1 for level in domain_levels if level > 0.8),
                "intermediates": sum(1 for level in domain_levels if 0.4 <= level <= 0.8),
                "novices": sum(1 for level in domain_levels if 0.1 <= level < 0.4),
                "uninitiated": sum(1 for level in domain_levels if level < 0.1)
            }
        
        # Calculate overall statistics
        all_levels = [
            level
            for agent_domains in self.agent_knowledge.values()
            for level in agent_domains.values()
        ]
        
        stats["overall"] = {
            "mean": np.mean(all_levels),
            "median": np.median(all_levels),
            "max": np.max(all_levels),
            "min": np.min(all_levels),
            "std": np.std(all_levels)
        }
        
        # Calculate expertise distribution
        all_domains = list(self.knowledge_domains.keys())
        expertise_counts = defaultdict(int)
        
        for agent_id, domains in self.agent_knowledge.items():
            expert_domains = sum(1 for d in all_domains if domains.get(d, 0.0) > 0.8)
            expertise_counts[expert_domains] += 1
            
        stats["expertise_distribution"] = dict(expertise_counts)
        
        return stats
    
    def find_knowledge_gaps(self) -> Dict[str, List[str]]:
        """
        Find knowledge gaps for each agent.
        
        Returns:
            Dictionary mapping agent IDs to lists of domains with gaps
        """
        gaps = {}
        
        for agent_id, domains in self.agent_knowledge.items():
            agent_gaps = []
            
            for domain_id in self.knowledge_domains:
                level = domains.get(domain_id, 0.0)
                
                # Check if this is a gap (knowledge below threshold)
                if level < 0.4:
                    # Check if prerequisites are met
                    prerequisites_met = True
                    for prereq in self.knowledge_domains[domain_id].get("prerequisites", []):
                        if prereq in domains and domains[prereq] < 0.5:
                            prerequisites_met = False
                            break
                    
                    # Only include as a gap if prerequisites are met
                    if prerequisites_met:
                        agent_gaps.append(domain_id)
            
            gaps[agent_id] = agent_gaps
            
        return gaps
    
    def find_optimal_teams(self, task_requirements: Dict[str, float], team_size: int = 3) -> List[Dict[str, Any]]:
        """
        Find optimal teams for a task based on knowledge requirements.
        
        Args:
            task_requirements: Dictionary mapping domains to required levels
            team_size: Desired team size
            
        Returns:
            List of team configurations
        """
        if not self.agent_knowledge:
            return []
            
        # Calculate scores for each agent
        agent_scores = {}
        
        for agent_id, domains in self.agent_knowledge.items():
            score = 0.0
            coverage = 0.0
            
            for domain_id, required_level in task_requirements.items():
                if domain_id in domains:
                    agent_level = domains[domain_id]
                    # Score based on how well agent meets requirements
                    if agent_level >= required_level:
                        score += 1.0
                        coverage += 1.0
                    else:
                        score += agent_level / required_level
                        coverage += agent_level / required_level
            
            agent_scores[agent_id] = {
                "agent_id": agent_id,
                "score": score,
                "coverage": coverage / len(task_requirements) if task_requirements else 0.0,
                "domains": domains
            }
        
        # Find top individual agents
        top_individuals = sorted(
            agent_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )[:10]  # Consider top 10 individuals
        
        # Find optimal teams
        best_teams = []
        
        # Try different team compositions
        from itertools import combinations
        
        for combo in combinations([a["agent_id"] for a in top_individuals], min(team_size, len(top_individuals))):
            team = list(combo)
            
            # Calculate team score
            team_coverage = {}
            
            for agent_id in team:
                domains = self.agent_knowledge[agent_id]
                for domain_id, level in domains.items():
                    if domain_id in task_requirements:
                        # Track maximum level across team for each domain
                        team_coverage[domain_id] = max(
                            team_coverage.get(domain_id, 0.0),
                            level
                        )
            
            # Calculate team score
            score = 0.0
            coverage = 0.0
            
            for domain_id, required_level in task_requirements.items():
                team_level = team_coverage.get(domain_id, 0.0)
                if team_level >= required_level:
                    score += 1.0
                    coverage += 1.0
                else:
                    score += team_level / required_level
                    coverage += team_level / required_level
            
            # Add to best teams
            best_teams.append({
                "team": team,
                "score": score,
                "coverage": coverage / len(task_requirements) if task_requirements else 0.0,
                "domain_coverage": team_coverage
            })
        
        # Sort by score
        best_teams.sort(key=lambda x: x["score"], reverse=True)
        
        return best_teams[:5]  # Return top 5 teams
"""