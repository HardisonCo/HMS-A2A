#!/usr/bin/env python3
"""
O3 Performance Optimization

This module provides performance optimizations for the O3 Deal Roadmap Optimization
process, enhancing computational efficiency for large-scale deal networks.
"""

import os
import numpy as np
import time
import json
from typing import Dict, List, Tuple, Any, Set, Optional, Union, Callable
from functools import lru_cache
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import argparse

try:
    from o3_deal_roadmap_optimization import (
        EntityNode, ValueEdge, DealHyperedge, DealRoadmap, 
        DealHypergraph, O3Optimizer
    )
    IMPORT_SUCCESS = True
except ImportError:
    print("Warning: Could not import O3 optimization components")
    IMPORT_SUCCESS = False

# =============================================================================
# Optimization Constants
# =============================================================================

# Cache sizes
ENTITY_CACHE_SIZE = 1024
DEAL_CACHE_SIZE = 512
ROADMAP_CACHE_SIZE = 256

# Parallel processing settings
DEFAULT_THREAD_COUNT = max(4, multiprocessing.cpu_count() - 1)
DEFAULT_CHUNK_SIZE = 100

# Performance thresholds
LARGE_GRAPH_THRESHOLD = 1000  # Entities + deals
VERY_LARGE_GRAPH_THRESHOLD = 5000  # Entities + deals

# Algorithm selection thresholds
GREEDY_ALGORITHM_THRESHOLD = 10000  # Use greedy algorithm for very large problems
MONTE_CARLO_MIN_SIMULATIONS = 50  # Minimum number of Monte Carlo simulations
MONTE_CARLO_MAX_SIMULATIONS = 1000  # Maximum number of Monte Carlo simulations

# =============================================================================
# Caching Decorators
# =============================================================================

def entity_cache(func):
    """Cache decorator for entity-related operations."""
    @lru_cache(maxsize=ENTITY_CACHE_SIZE)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped

def deal_cache(func):
    """Cache decorator for deal-related operations."""
    @lru_cache(maxsize=DEAL_CACHE_SIZE)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped

def roadmap_cache(func):
    """Cache decorator for roadmap-related operations."""
    @lru_cache(maxsize=ROADMAP_CACHE_SIZE)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped

# =============================================================================
# Optimized EntityNode Class
# =============================================================================

class OptimizedEntityNode(EntityNode):
    """Optimized version of EntityNode with performance enhancements."""
    
    def __init__(self, *args, **kwargs):
        """Initialize with parent constructor."""
        super().__init__(*args, **kwargs)
        self._subjective_value_cache = {}
    
    @entity_cache
    def get_subjective_value(self, value_object: Dict[str, float]) -> float:
        """
        Calculate the subjective value of a value object to this entity.
        Optimized with caching for repeated calculations.
        
        Args:
            value_object: Dictionary of value dimensions and amounts
            
        Returns:
            Subjective value to this entity
        """
        # Convert value_object to a hashable format for caching
        value_key = frozenset(value_object.items())
        
        # Check cache
        if value_key in self._subjective_value_cache:
            return self._subjective_value_cache[value_key]
        
        # Calculate value using vectorized operations
        dimensions = list(value_object.keys())
        weights = np.array([self.preferences.get(dim, 0.0) for dim in dimensions])
        values = np.array([value_object[dim] for dim in dimensions])
        
        subjective_value = np.sum(weights * values)
        
        # Cache and return result
        self._subjective_value_cache[value_key] = subjective_value
        return subjective_value
    
    @entity_cache
    def can_participate(self, required_capacity: Dict[str, float]) -> bool:
        """
        Check if this entity has sufficient capacity to participate in a deal.
        Optimized version with caching.
        
        Args:
            required_capacity: Dictionary of required capacities
            
        Returns:
            True if entity has sufficient capacity, False otherwise
        """
        # Convert to hashable for caching
        capacity_key = frozenset(required_capacity.items())
        
        # Use vectorized operations for faster comparison
        dimensions = list(required_capacity.keys())
        required = np.array([required_capacity[dim] for dim in dimensions])
        available = np.array([self.capacity.get(dim, 0.0) for dim in dimensions])
        
        return np.all(available >= required)

# =============================================================================
# Optimized DealHyperedge Class
# =============================================================================

class OptimizedDealHyperedge(DealHyperedge):
    """Optimized version of DealHyperedge with performance enhancements."""
    
    def __init__(self, *args, **kwargs):
        """Initialize with parent constructor."""
        super().__init__(*args, **kwargs)
        self._total_value_cache = None
        self._entity_value_cache = {}
        self._win_win_cache = {}
    
    @deal_cache
    def get_total_value(self) -> float:
        """
        Calculate the total value created by this deal.
        Cached for performance.
        """
        if self._total_value_cache is not None:
            return self._total_value_cache
        
        # Use vectorized operations for faster calculation
        values = np.array([edge.get_total_value() for edge in self.value_edges])
        total_value = np.sum(values)
        
        self._total_value_cache = total_value
        return total_value
    
    @deal_cache
    def get_entity_value(self, entity_id: str) -> Dict[str, float]:
        """
        Calculate the net value for a specific entity in this deal.
        Cached for performance.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Dictionary of value dimensions and net amounts
        """
        if entity_id in self._entity_value_cache:
            return self._entity_value_cache[entity_id]
        
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} is not part of this deal")
        
        # Initialize net value by dimension using defaultdict for cleaner code
        from collections import defaultdict
        net_value = defaultdict(float)
        
        # Group edges by source and target for faster processing
        source_edges = [edge for edge in self.value_edges if edge.source_id == entity_id]
        target_edges = [edge for edge in self.value_edges if edge.target_id == entity_id]
        
        # Process all target edges (incoming value)
        for edge in target_edges:
            for dimension, amount in edge.value.items():
                net_value[dimension] += amount
        
        # Process all source edges (outgoing value)
        for edge in source_edges:
            for dimension, amount in edge.value.items():
                net_value[dimension] -= amount
        
        result = dict(net_value)
        self._entity_value_cache[entity_id] = result
        return result
    
    @deal_cache
    def is_win_win(self, entity_preferences: Dict[str, Dict[str, float]]) -> Tuple[bool, Dict[str, float]]:
        """
        Check if this deal is a win-win for all participants.
        Cached for performance.
        
        Args:
            entity_preferences: Dictionary mapping entity IDs to preference dictionaries
            
        Returns:
            Tuple of (is_win_win, entity_subjective_values)
        """
        # Create cache key
        prefs_key = frozenset([(entity_id, frozenset(prefs.items())) 
                              for entity_id, prefs in entity_preferences.items()])
        
        if prefs_key in self._win_win_cache:
            return self._win_win_cache[prefs_key]
        
        # Vectorized calculation of entity values
        entity_values = {}
        
        for entity_id in self.entities:
            if entity_id not in entity_preferences:
                # Skip entities without preferences
                continue
            
            # Get net value for this entity
            net_value = self.get_entity_value(entity_id)
            
            # Calculate subjective value based on preferences
            preferences = entity_preferences.get(entity_id, {})
            
            dimensions = list(net_value.keys())
            weights = np.array([preferences.get(dim, 0.0) for dim in dimensions])
            values = np.array([net_value[dim] for dim in dimensions])
            
            subjective_value = np.sum(weights * values)
            entity_values[entity_id] = subjective_value
        
        # Check if all entities receive positive value
        is_win_win = all(value > 0 for value in entity_values.values())
        
        result = (is_win_win, entity_values)
        self._win_win_cache[prefs_key] = result
        return result

# =============================================================================
# Optimized DealHypergraph Class
# =============================================================================

class OptimizedDealHypergraph(DealHypergraph):
    """Optimized version of DealHypergraph with performance enhancements."""
    
    def __init__(self):
        """Initialize with parent constructor."""
        super().__init__()
        self._entity_deals_cache = {}
        self._deal_entities_cache = {}
        self._potential_deals_cache = None
    
    def add_entity(self, entity: EntityNode) -> None:
        """Add an entity to the hypergraph."""
        # Replace with optimized entity if not already optimized
        if not isinstance(entity, OptimizedEntityNode):
            entity = OptimizedEntityNode(
                id=entity.id,
                name=entity.name,
                entity_type=entity.entity_type,
                capacity=entity.capacity,
                preferences=entity.preferences,
                constraints=entity.constraints
            )
            entity.value_received = entity.value_received
            entity.value_contributed = entity.value_contributed
            entity.deals = entity.deals
        
        super().add_entity(entity)
        
        # Invalidate caches
        self._entity_deals_cache = {}
        self._potential_deals_cache = None
    
    def add_deal(self, deal: DealHyperedge) -> None:
        """Add a deal to the hypergraph."""
        # Replace with optimized deal if not already optimized
        if not isinstance(deal, OptimizedDealHyperedge):
            optimized_deal = OptimizedDealHyperedge(
                id=deal.id,
                name=deal.name,
                entities=list(deal.entities),
                intent=deal.intent,
                solutions=deal.solutions,
                financing=deal.financing,
                execution_plan=deal.execution_plan,
                verification=deal.verification,
                status=deal.status
            )
            
            # Add value edges to the optimized deal
            for edge in deal.value_edges:
                optimized_deal.add_value_edge(edge)
            
            # Set timestamps
            optimized_deal.creation_time = deal.creation_time
            optimized_deal.update_time = deal.update_time
            
            deal = optimized_deal
        
        super().add_deal(deal)
        
        # Invalidate caches
        self._entity_deals_cache = {}
        self._deal_entities_cache = {}
        self._potential_deals_cache = None
    
    @entity_cache
    def get_entity_deals(self, entity_id: str) -> List[DealHyperedge]:
        """Get all deals an entity is participating in."""
        if entity_id in self._entity_deals_cache:
            return self._entity_deals_cache[entity_id]
        
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        entity = self.entities[entity_id]
        deals = [self.deals[deal_id] for deal_id in entity.deals if deal_id in self.deals]
        
        self._entity_deals_cache[entity_id] = deals
        return deals
    
    @deal_cache
    def get_deal_entities(self, deal_id: str) -> List[EntityNode]:
        """Get all entities participating in a deal."""
        if deal_id in self._deal_entities_cache:
            return self._deal_entities_cache[deal_id]
        
        if deal_id not in self.deals:
            raise ValueError(f"Deal {deal_id} does not exist")
        
        deal = self.deals[deal_id]
        entities = [self.entities[entity_id] for entity_id in deal.entities if entity_id in self.entities]
        
        self._deal_entities_cache[deal_id] = entities
        return entities
    
    @deal_cache
    def find_potential_deals(self) -> List[List[str]]:
        """
        Find potential new deals based on entity relationships.
        Optimized with caching and parallel processing for large graphs.
        """
        if self._potential_deals_cache is not None:
            return self._potential_deals_cache
        
        # For very large graphs, use a more efficient algorithm
        total_size = len(self.entities) + len(self.deals)
        
        if total_size > LARGE_GRAPH_THRESHOLD:
            return self._find_potential_deals_optimized()
        
        # Original implementation for smaller graphs
        potential_deals = []
        
        # Find entities that have collaborated before
        collaboration_graph = defaultdict(set)
        
        for deal in self.deals.values():
            entities = list(deal.entities)
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    collaboration_graph[entities[i]].add(entities[j])
                    collaboration_graph[entities[j]].add(entities[i])
        
        # Find potential new combinations
        visited = set()
        for entity_id, collaborators in collaboration_graph.items():
            for collaborator_id in collaborators:
                # Skip if we've already considered this pair
                pair = tuple(sorted([entity_id, collaborator_id]))
                if pair in visited:
                    continue
                
                visited.add(pair)
                
                # Find potential third parties
                entity_collaborators = collaboration_graph[entity_id]
                collaborator_collaborators = collaboration_graph[collaborator_id]
                
                # Entities that have worked with both
                common_collaborators = entity_collaborators.intersection(collaborator_collaborators)
                
                # Create potential deals with 3 or more entities
                for third_party in common_collaborators:
                    # Skip if this triplet already exists as a deal
                    entities = [entity_id, collaborator_id, third_party]
                    if any(set(entities).issubset(set(deal.entities)) for deal in self.deals.values()):
                        continue
                    
                    potential_deals.append(entities)
                    
                    # Try to find fourth parties
                    fourth_parties = (
                        collaboration_graph[entity_id]
                        .intersection(collaboration_graph[collaborator_id])
                        .intersection(collaboration_graph[third_party])
                    )
                    
                    for fourth_party in fourth_parties:
                        if fourth_party not in entities:
                            expanded_entities = entities + [fourth_party]
                            if any(set(expanded_entities).issubset(set(deal.entities)) for deal in self.deals.values()):
                                continue
                            
                            potential_deals.append(expanded_entities)
        
        self._potential_deals_cache = potential_deals
        return potential_deals
    
    def _find_potential_deals_optimized(self) -> List[List[str]]:
        """
        Optimized algorithm for finding potential deals in large graphs.
        Uses a more efficient approach for very large graphs.
        """
        from collections import Counter
        
        # Calculate entity co-occurrence
        entity_cooccurrence = Counter()
        
        # For each deal, count entity pairs
        for deal in self.deals.values():
            entities = list(deal.entities)
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    entity_pair = tuple(sorted([entities[i], entities[j]]))
                    entity_cooccurrence[entity_pair] += 1
        
        # Use parallel processing for large graphs
        total_size = len(self.entities) + len(self.deals)
        use_parallel = total_size > VERY_LARGE_GRAPH_THRESHOLD
        
        # Group entity pairs by first entity
        grouped_pairs = defaultdict(list)
        for pair, count in entity_cooccurrence.items():
            grouped_pairs[pair[0]].append((pair[1], count))
        
        # Function to find potential deal for a single entity
        def find_entity_deals(entity_id):
            local_deals = []
            
            # Skip if this entity doesn't have connections
            if entity_id not in grouped_pairs:
                return local_deals
            
            # Find all pairs with strong connections
            connections = grouped_pairs[entity_id]
            
            # Sort by co-occurrence count (descending)
            connections.sort(key=lambda x: x[1], reverse=True)
            
            # Take top connections (to limit computational complexity)
            top_connections = connections[:min(20, len(connections))]
            
            # Create triplets based on top connections
            for i, (entity1, _) in enumerate(top_connections):
                for j in range(i+1, len(top_connections)):
                    entity2 = top_connections[j][0]
                    
                    # Check if these two entities have worked together
                    pair = tuple(sorted([entity1, entity2]))
                    if pair in entity_cooccurrence:
                        # Create a potential deal with 3 entities
                        deal = [entity_id, entity1, entity2]
                        
                        # Skip if this combination already exists as a deal
                        if any(set(deal).issubset(set(d.entities)) for d in self.deals.values()):
                            continue
                        
                        local_deals.append(deal)
            
            return local_deals
        
        # Use parallel processing for large graphs
        potential_deals = []
        
        if use_parallel:
            # Use process pool for very large graphs
            with ProcessPoolExecutor(max_workers=DEFAULT_THREAD_COUNT) as executor:
                results = list(executor.map(find_entity_deals, grouped_pairs.keys()))
                for result in results:
                    potential_deals.extend(result)
        else:
            # Sequential processing for smaller graphs
            for entity_id in grouped_pairs.keys():
                potential_deals.extend(find_entity_deals(entity_id))
        
        return potential_deals

# =============================================================================
# Optimized O3Optimizer Class
# =============================================================================

class OptimizedO3Optimizer(O3Optimizer):
    """Optimized version of O3Optimizer with performance enhancements."""
    
    def __init__(self, graph: DealHypergraph):
        """
        Initialize the optimized O3 optimizer.
        
        Args:
            graph: DealHypergraph to optimize (will be converted to OptimizedDealHypergraph if needed)
        """
        # Convert graph to optimized version if needed
        if not isinstance(graph, OptimizedDealHypergraph):
            optimized_graph = OptimizedDealHypergraph()
            
            # Copy entities
            for entity_id, entity in graph.entities.items():
                optimized_graph.add_entity(entity)
            
            # Copy deals
            for deal_id, deal in graph.deals.items():
                optimized_graph.add_deal(deal)
            
            # Copy roadmaps
            for roadmap_id, roadmap in graph.roadmaps.items():
                optimized_graph.add_roadmap(roadmap)
            
            graph = optimized_graph
        
        super().__init__(graph)
        
        # Optimization-related attributes
        self._optimization_cache = {}
        self._simulation_cache = {}
        self._roadmap_cache = {}
    
    @roadmap_cache
    def optimize_roadmap(
        self,
        entity_ids: List[str] = None,
        max_deals: int = 5,
        objective: str = "total_value",
        constraints: Dict[str, Any] = None
    ) -> DealRoadmap:
        """
        Optimize a deal roadmap to maximize value creation.
        Optimized with caching and parallel processing.
        
        Args:
            entity_ids: List of entity IDs to include in the roadmap (if None, use all)
            max_deals: Maximum number of deals in the roadmap
            objective: Optimization objective (total_value, balance, speed)
            constraints: Additional constraints on the optimization
            
        Returns:
            Optimized DealRoadmap
        """
        # Create cache key
        cache_key = (
            tuple(sorted(entity_ids)) if entity_ids else None,
            max_deals,
            objective,
            frozenset(constraints.items()) if constraints else None
        )
        
        if cache_key in self._roadmap_cache:
            return self._roadmap_cache[cache_key]
        
        # If no entity IDs provided, use all entities
        if entity_ids is None:
            entity_ids = list(self.graph.entities.keys())
        
        # Validate entities
        for entity_id in entity_ids:
            if entity_id not in self.graph.entities:
                raise ValueError(f"Entity {entity_id} does not exist")
        
        # Default constraints
        if constraints is None:
            constraints = {}
        
        # Generate potential new deals
        potential_deals = []
        
        # 1. Include existing deals involving these entities
        for deal in self.graph.deals.values():
            if any(entity_id in deal.entities for entity_id in entity_ids):
                potential_deals.append(deal)
        
        # 2. Find potential new deals between these entities
        entity_group_deals = []
        
        # Determine if we should use parallel processing
        total_entity_groups = len(self.graph.find_potential_deals())
        use_parallel = total_entity_groups > 100
        
        # Function to process a single entity group
        def process_entity_group(entity_group):
            # Only include groups with at least one target entity
            if not any(entity_id in entity_ids for entity_id in entity_group):
                return None
            
            # Create a potential deal
            deal = self.graph.create_deal_from_entities(
                entity_group,
                name=f"Potential Deal {len(potential_deals) + len(entity_group_deals) + 1}"
            )
            return deal
        
        if use_parallel:
            # Use parallel processing for many entity groups
            entity_groups = self.graph.find_potential_deals()
            
            with ThreadPoolExecutor(max_workers=DEFAULT_THREAD_COUNT) as executor:
                results = list(executor.map(process_entity_group, entity_groups))
                entity_group_deals = [deal for deal in results if deal is not None]
        else:
            # Sequential processing for fewer entity groups
            for entity_group in self.graph.find_potential_deals():
                deal = process_entity_group(entity_group)
                if deal is not None:
                    entity_group_deals.append(deal)
        
        potential_deals.extend(entity_group_deals)
        
        # 3. Optimize each deal - this is potentially expensive, so parallelize
        optimized_deals = []
        
        # Function to optimize a single deal
        def optimize_deal(deal):
            # Skip deals already in the graph
            if deal.id in self.graph.deals:
                return deal
            
            # Create a temporary copy of the graph with this deal
            temp_graph = OptimizedDealHypergraph()
            
            # Add all entities and existing deals
            for entity_id, entity in self.graph.entities.items():
                temp_graph.entities[entity_id] = entity
            
            for existing_deal_id, existing_deal in self.graph.deals.items():
                temp_graph.deals[existing_deal_id] = existing_deal
            
            # Add the potential deal
            temp_graph.add_deal(deal)
            
            # Optimize the deal
            temp_optimizer = OptimizedO3Optimizer(temp_graph)
            optimization_result = temp_optimizer.optimize_deal_values(deal.id)
            
            # If optimizable to win-win, return the optimized deal
            if optimization_result["status"] in ["optimized", "already_win_win"]:
                # Update the deal with optimized edges if needed
                if optimization_result["status"] == "optimized":
                    deal.value_edges = []
                    for edge_data in optimization_result["optimized_value_edges"]:
                        edge = ValueEdge.from_dict(edge_data)
                        deal.add_value_edge(edge)
                
                return deal
            
            # Not optimizable to win-win, so don't include it
            return None
        
        # Determine if we should use parallel processing for deal optimization
        use_parallel = len(potential_deals) > 10
        
        if use_parallel:
            # Use parallel processing for many deals
            with ThreadPoolExecutor(max_workers=DEFAULT_THREAD_COUNT) as executor:
                results = list(executor.map(optimize_deal, potential_deals))
                optimized_deals = [deal for deal in results if deal is not None]
        else:
            # Sequential processing for fewer deals
            for deal in potential_deals:
                optimized_deal = optimize_deal(deal)
                if optimized_deal is not None:
                    optimized_deals.append(optimized_deal)
        
        # Rest of the original method proceeds as before...
        # 4. Score deals based on objective
        scored_deals = []
        for deal in optimized_deals:
            # Calculate total value
            total_value = sum(edge.get_total_value() for edge in deal.value_edges)
            
            # Calculate value balance
            entity_values = {}
            for entity_id in deal.entities:
                if entity_id in self.graph.entities:
                    entity = self.graph.entities[entity_id]
                    
                    # Get deal value for this entity
                    deal_value = deal.get_entity_value(entity_id)
                    
                    # Calculate subjective value
                    subjective_value = 0.0
                    for dimension, amount in deal_value.items():
                        weight = entity.preferences.get(dimension, 0.0)
                        subjective_value += amount * weight
                    
                    entity_values[entity_id] = subjective_value
            
            # Calculate value balance as coefficient of variation
            if entity_values:
                values = list(entity_values.values())
                balance = 1.0 - (np.std(values) / (np.mean(values) + 1e-10))
            else:
                balance = 0.0
            
            # Calculate speed (inverse of complexity)
            complexity = len(deal.entities) * len(deal.value_edges)
            speed = 1.0 / (complexity + 1e-10)
            
            # Score based on objective
            if objective == "total_value":
                score = total_value
            elif objective == "balance":
                score = balance
            elif objective == "speed":
                score = speed
            else:
                # Weighted combination
                score = 0.6 * total_value + 0.3 * balance + 0.1 * speed
            
            scored_deals.append((deal, score))
        
        # 5. Sort deals by score
        scored_deals.sort(key=lambda x: x[1], reverse=True)
        
        # 6. Select top deals
        selected_deals = [deal for deal, _ in scored_deals[:max_deals]]
        
        # 7. Create dependencies between deals
        dependencies = {}
        for i, deal1 in enumerate(selected_deals):
            dependencies[deal1.id] = []
            
            # Look for potential dependencies
            for j, deal2 in enumerate(selected_deals):
                if i == j:
                    continue
                
                # Check if deals share entities
                common_entities = deal1.entities.intersection(deal2.entities)
                if common_entities:
                    # If deal2 has more entities, deal1 might be a precursor
                    if len(deal1.entities) < len(deal2.entities):
                        dependencies[deal2.id] = dependencies.get(deal2.id, []) + [deal1.id]
        
        # 8. Create a timeline
        timeline = {}
        for i, deal in enumerate(selected_deals):
            # Simple timeline based on dependencies
            deps = dependencies.get(deal.id, [])
            
            # Start after all dependencies are complete
            if deps:
                start_time = max(timeline.get(dep_id, {}).get("end", i * 30) for dep_id in deps)
            else:
                start_time = i * 30
            
            # Duration based on complexity
            complexity = len(deal.entities) * len(deal.value_edges)
            duration = max(30, min(180, complexity))
            
            timeline[deal.id] = {
                "start": start_time,
                "duration": duration,
                "end": start_time + duration
            }
        
        # 9. Create the roadmap
        roadmap_id = f"roadmap_{len(self.graph.roadmaps) + 1}_{int(time.time())}"
        entity_names = [self.graph.entities[entity_id].name for entity_id in entity_ids if entity_id in self.graph.entities]
        roadmap_name = f"Optimized Roadmap for {', '.join(entity_names[:3])}"
        
        roadmap = DealRoadmap(
            id=roadmap_id,
            name=roadmap_name,
            deals=[deal.id for deal in selected_deals],
            dependencies=dependencies,
            timeline=timeline,
            objectives={
                "primary_objective": objective,
                "target_entities": entity_ids,
                "constraints": constraints
            }
        )
        
        # Cache and return
        self._roadmap_cache[cache_key] = roadmap
        return roadmap
    
    def monte_carlo_roadmap_simulation(
        self,
        roadmap_id: str,
        num_simulations: int = 100,
        risk_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulations to assess roadmap risk and robustness.
        Optimized with parallelization and adaptive simulation count.
        
        Args:
            roadmap_id: ID of the roadmap to simulate
            num_simulations: Number of simulations to run
            risk_params: Parameters for the risk simulation
            
        Returns:
            Simulation results
        """
        if roadmap_id not in self.graph.roadmaps:
            raise ValueError(f"Roadmap {roadmap_id} does not exist")
        
        # Create cache key
        cache_key = (roadmap_id, num_simulations, frozenset(risk_params.items()) if risk_params else None)
        
        if cache_key in self._simulation_cache:
            return self._simulation_cache[cache_key]
        
        roadmap = self.graph.roadmaps[roadmap_id]
        
        # Default risk parameters
        if risk_params is None:
            risk_params = {
                "deal_failure_prob": 0.1,  # Probability of a deal failing
                "value_variation": 0.2,  # Variation in realized value (+/-)
                "timeline_variation": 0.3,  # Variation in timeline (+/-)
                "dependency_failure_impact": 0.5  # Impact of dependency failure
            }
        
        # Determine appropriate number of simulations based on roadmap complexity
        deal_count = len(roadmap.deals)
        adaptive_simulations = min(
            max(MONTE_CARLO_MIN_SIMULATIONS, deal_count * 10),
            MONTE_CARLO_MAX_SIMULATIONS
        )
        
        # Use specified num_simulations if provided, otherwise use adaptive
        effective_simulations = num_simulations or adaptive_simulations
        
        # Simulation results structure
        results = {
            "roadmap_id": roadmap_id,
            "num_simulations": effective_simulations,
            "risk_params": risk_params,
            "simulations": [],
            "summary": {
                "success_rate": 0.0,
                "expected_value": 0.0,
                "value_at_risk": 0.0,
                "expected_duration": 0.0,
                "critical_deals": []
            }
        }
        
        # Function to run a single simulation
        def run_simulation(sim_index):
            simulation = {
                "index": sim_index,
                "deals": {},
                "total_value": 0.0,
                "success": True,
                "duration": 0
            }
            
            # Simulate each deal
            for deal_id in roadmap.deals:
                # Check dependencies
                dependencies = roadmap.dependencies.get(deal_id, [])
                dependency_failure = False
                
                for dep_id in dependencies:
                    if dep_id in simulation["deals"] and not simulation["deals"][dep_id]["success"]:
                        dependency_failure = True
                        break
                
                # Increased failure probability if dependency failed
                if dependency_failure:
                    failure_prob = risk_params["deal_failure_prob"] + risk_params["dependency_failure_impact"]
                else:
                    failure_prob = risk_params["deal_failure_prob"]
                
                # Determine if deal succeeds - use numpy random for better performance
                deal_success = np.random.random() > failure_prob
                
                # Calculate deal value with variation
                if deal_id in self.graph.deals:
                    deal = self.graph.deals[deal_id]
                    base_value = deal.get_total_value()
                else:
                    base_value = 10.0  # Default value for potential deals
                
                # Use numpy for random number generation
                value_variation = 1.0 + (2 * np.random.random() - 1) * risk_params["value_variation"]
                simulated_value = base_value * value_variation if deal_success else 0.0
                
                # Calculate deal timeline with variation
                timeline_info = roadmap.timeline.get(deal_id, {"duration": 60})
                base_duration = timeline_info.get("duration", 60)
                
                duration_variation = 1.0 + (2 * np.random.random() - 1) * risk_params["timeline_variation"]
                simulated_duration = base_duration * duration_variation
                
                # Record the deal simulation
                simulation["deals"][deal_id] = {
                    "success": deal_success,
                    "value": simulated_value,
                    "duration": simulated_duration
                }
                
                # Update totals
                simulation["total_value"] += simulated_value
                simulation["duration"] += simulated_duration if deal_success else 0.0
                
                # Update overall success
                if not deal_success:
                    simulation["success"] = False
            
            return simulation
        
        # Run simulations
        # Use parallel processing for many simulations
        use_parallel = effective_simulations > 10
        
        simulations = []
        if use_parallel:
            # Use ThreadPoolExecutor for IO-bound operations
            with ThreadPoolExecutor(max_workers=DEFAULT_THREAD_COUNT) as executor:
                simulations = list(executor.map(run_simulation, range(effective_simulations)))
        else:
            # Sequential processing for fewer simulations
            for i in range(effective_simulations):
                simulations.append(run_simulation(i))
        
        # Store simulations in results
        results["simulations"] = simulations
        
        # Calculate summary statistics
        total_values = [sim["total_value"] for sim in simulations]
        successful_simulations = sum(1 for sim in simulations if sim["success"])
        critical_deal_failures = defaultdict(int)
        
        # Track critical deal failures
        for sim in simulations:
            for deal_id, deal_sim in sim["deals"].items():
                if not deal_sim["success"]:
                    critical_deal_failures[deal_id] += 1
        
        # Calculate summary statistics
        if total_values:
            results["summary"]["success_rate"] = successful_simulations / effective_simulations
            results["summary"]["expected_value"] = np.mean(total_values)
            results["summary"]["value_at_risk"] = np.percentile(total_values, 5)  # 5% VaR
            
            # Calculate expected duration
            durations = [sim["duration"] for sim in simulations]
            results["summary"]["expected_duration"] = np.mean(durations)
            
            # Identify critical deals
            if critical_deal_failures:
                critical_deals = sorted(
                    critical_deal_failures.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                results["summary"]["critical_deals"] = [
                    {
                        "deal_id": deal_id,
                        "failure_count": count,
                        "failure_rate": count / effective_simulations
                    }
                    for deal_id, count in critical_deals[:3]  # Top 3 critical deals
                ]
        
        # Cache and return
        self._simulation_cache[cache_key] = results
        return results

# =============================================================================
# Utility Functions
# =============================================================================

def convert_graph_to_optimized(graph_path: str, output_path: str = None) -> str:
    """
    Convert a DealHypergraph to an OptimizedDealHypergraph.
    
    Args:
        graph_path: Path to the input graph file
        output_path: Path to save the optimized graph (if None, use graph_path with _optimized suffix)
        
    Returns:
        Path to the optimized graph file
    """
    if not IMPORT_SUCCESS:
        raise ImportError("Could not import O3 optimization components")
    
    # Load the graph
    graph = DealHypergraph.load_from_file(graph_path)
    
    # Convert to optimized graph
    optimized_graph = OptimizedDealHypergraph()
    
    # Copy entities
    for entity_id, entity in graph.entities.items():
        optimized_graph.add_entity(entity)
    
    # Copy deals
    for deal_id, deal in graph.deals.items():
        optimized_graph.add_deal(deal)
    
    # Copy roadmaps
    for roadmap_id, roadmap in graph.roadmaps.items():
        optimized_graph.add_roadmap(roadmap)
    
    # Determine output path
    if output_path is None:
        base, ext = os.path.splitext(graph_path)
        output_path = f"{base}_optimized{ext}"
    
    # Save the optimized graph
    optimized_graph.save_to_file(output_path)
    
    return output_path

def create_optimizer(graph, optimized: bool = True) -> Union[O3Optimizer, OptimizedO3Optimizer]:
    """
    Create an appropriate optimizer for the given graph.
    
    Args:
        graph: DealHypergraph or OptimizedDealHypergraph
        optimized: Whether to use the optimized version
        
    Returns:
        An O3Optimizer or OptimizedO3Optimizer
    """
    if not IMPORT_SUCCESS:
        raise ImportError("Could not import O3 optimization components")
    
    if optimized:
        return OptimizedO3Optimizer(graph)
    else:
        return O3Optimizer(graph)

def compare_performance(graph_path: str) -> Dict[str, Any]:
    """
    Compare performance between standard and optimized implementations.
    
    Args:
        graph_path: Path to the graph file
        
    Returns:
        Dictionary of performance comparison results
    """
    if not IMPORT_SUCCESS:
        raise ImportError("Could not import O3 optimization components")
    
    # Load the graph
    standard_graph = DealHypergraph.load_from_file(graph_path)
    
    # Create optimized version
    optimized_graph = OptimizedDealHypergraph()
    
    # Copy entities
    for entity_id, entity in standard_graph.entities.items():
        optimized_graph.add_entity(entity)
    
    # Copy deals
    for deal_id, deal in standard_graph.deals.items():
        optimized_graph.add_deal(deal)
    
    # Copy roadmaps
    for roadmap_id, roadmap in standard_graph.roadmaps.items():
        optimized_graph.add_roadmap(roadmap)
    
    # Create optimizers
    standard_optimizer = O3Optimizer(standard_graph)
    optimized_optimizer = OptimizedO3Optimizer(optimized_graph)
    
    # Test operations
    results = {
        "graph_info": {
            "entities": len(standard_graph.entities),
            "deals": len(standard_graph.deals),
            "roadmaps": len(standard_graph.roadmaps)
        },
        "operations": {}
    }
    
    # Test find_potential_deals
    start_time = time.time()
    standard_result = standard_graph.find_potential_deals()
    standard_time = time.time() - start_time
    
    start_time = time.time()
    optimized_result = optimized_graph.find_potential_deals()
    optimized_time = time.time() - start_time
    
    results["operations"]["find_potential_deals"] = {
        "standard_time": standard_time,
        "optimized_time": optimized_time,
        "speedup": standard_time / optimized_time if optimized_time > 0 else float('inf'),
        "result_count": len(standard_result)
    }
    
    # Test optimize_deal if deals exist
    if standard_graph.deals:
        deal_id = next(iter(standard_graph.deals.keys()))
        
        start_time = time.time()
        _ = standard_optimizer.optimize_deal_values(deal_id)
        standard_time = time.time() - start_time
        
        start_time = time.time()
        _ = optimized_optimizer.optimize_deal_values(deal_id)
        optimized_time = time.time() - start_time
        
        results["operations"]["optimize_deal"] = {
            "standard_time": standard_time,
            "optimized_time": optimized_time,
            "speedup": standard_time / optimized_time if optimized_time > 0 else float('inf')
        }
    
    # Test optimize_roadmap
    start_time = time.time()
    _ = standard_optimizer.optimize_roadmap()
    standard_time = time.time() - start_time
    
    start_time = time.time()
    _ = optimized_optimizer.optimize_roadmap()
    optimized_time = time.time() - start_time
    
    results["operations"]["optimize_roadmap"] = {
        "standard_time": standard_time,
        "optimized_time": optimized_time,
        "speedup": standard_time / optimized_time if optimized_time > 0 else float('inf')
    }
    
    # Test monte_carlo_simulation if roadmaps exist
    if standard_graph.roadmaps:
        roadmap_id = next(iter(standard_graph.roadmaps.keys()))
        
        start_time = time.time()
        _ = standard_optimizer.monte_carlo_roadmap_simulation(roadmap_id, num_simulations=50)
        standard_time = time.time() - start_time
        
        start_time = time.time()
        _ = optimized_optimizer.monte_carlo_roadmap_simulation(roadmap_id, num_simulations=50)
        optimized_time = time.time() - start_time
        
        results["operations"]["monte_carlo_simulation"] = {
            "standard_time": standard_time,
            "optimized_time": optimized_time,
            "speedup": standard_time / optimized_time if optimized_time > 0 else float('inf')
        }
    
    # Calculate overall speedup
    speedups = [op["speedup"] for op in results["operations"].values()]
    results["overall_speedup"] = sum(speedups) / len(speedups) if speedups else 0.0
    
    return results

def main():
    """Main function for the optimization script."""
    parser = argparse.ArgumentParser(description="O3 Deal Optimization Performance Enhancements")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert graph to optimized version")
    convert_parser.add_argument("--input", required=True, help="Input graph file path")
    convert_parser.add_argument("--output", help="Output graph file path")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare performance between standard and optimized")
    compare_parser.add_argument("--graph", required=True, help="Graph file path")
    compare_parser.add_argument("--output", help="Output report file path")
    
    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Optimize a roadmap using optimized implementation")
    optimize_parser.add_argument("--graph", required=True, help="Graph file path")
    optimize_parser.add_argument("--entities", nargs="+", help="Entity IDs to include")
    optimize_parser.add_argument("--max-deals", type=int, default=5, help="Maximum number of deals")
    optimize_parser.add_argument("--objective", default="total_value", 
                               choices=["total_value", "balance", "speed", "hybrid"],
                               help="Optimization objective")
    optimize_parser.add_argument("--output", help="Output graph file path")
    
    # Simulation command
    simulate_parser = subparsers.add_parser("simulate", help="Run Monte Carlo simulation with optimized implementation")
    simulate_parser.add_argument("--graph", required=True, help="Graph file path")
    simulate_parser.add_argument("--roadmap-id", required=True, help="ID of the roadmap to simulate")
    simulate_parser.add_argument("--simulations", type=int, default=100, help="Number of simulations")
    simulate_parser.add_argument("--output", help="Output simulation results file path")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "convert":
        output_path = convert_graph_to_optimized(args.input, args.output)
        print(f"Converted graph saved to: {output_path}")
    
    elif args.command == "compare":
        results = compare_performance(args.graph)
        
        # Print results summary
        print(f"\nPerformance Comparison Summary:")
        print(f"Graph size: {results['graph_info']['entities']} entities, {results['graph_info']['deals']} deals")
        print(f"Overall speedup: {results['overall_speedup']:.2f}x")
        
        print("\nOperation details:")
        for op_name, op_data in results["operations"].items():
            print(f"  {op_name}:")
            print(f"    Standard: {op_data['standard_time']:.4f} seconds")
            print(f"    Optimized: {op_data['optimized_time']:.4f} seconds")
            print(f"    Speedup: {op_data['speedup']:.2f}x")
        
        # Save results if output specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"\nDetailed results saved to: {args.output}")
    
    elif args.command == "optimize":
        # Load the graph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimized optimizer
        optimizer = OptimizedO3Optimizer(graph)
        
        # Optimize roadmap
        roadmap = optimizer.optimize_roadmap(
            entity_ids=args.entities,
            max_deals=args.max_deals,
            objective=args.objective
        )
        
        # Add roadmap to graph
        graph.add_roadmap(roadmap)
        
        # Print roadmap summary
        print(f"Roadmap: {roadmap.name}")
        print(f"Deals: {len(roadmap.deals)}")
        print(f"Primary objective: {roadmap.objectives.get('primary_objective', 'total_value')}")
        print(f"Critical path: {', '.join(roadmap.get_critical_path())}")
        
        # Save updated graph if requested
        if args.output:
            graph.save_to_file(args.output)
            print(f"Updated graph saved to: {args.output}")
    
    elif args.command == "simulate":
        # Load the graph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimized optimizer
        optimizer = OptimizedO3Optimizer(graph)
        
        # Run simulation
        simulation = optimizer.monte_carlo_roadmap_simulation(
            roadmap_id=args.roadmap_id,
            num_simulations=args.simulations
        )
        
        # Print simulation summary
        print(f"Roadmap: {args.roadmap_id}")
        print(f"Simulations: {args.simulations}")
        print(f"Success rate: {simulation['summary']['success_rate']:.2f}")
        print(f"Expected value: {simulation['summary']['expected_value']:.2f}")
        print(f"Value at risk (5%): {simulation['summary']['value_at_risk']:.2f}")
        print(f"Expected duration: {simulation['summary']['expected_duration']:.2f} days")
        
        if simulation['summary']['critical_deals']:
            print("\nCritical deals (highest failure rates):")
            for deal in simulation['summary']['critical_deals']:
                print(f"  - {deal['deal_id']}: {deal['failure_rate']:.2f}")
        
        # Save simulation results if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(simulation, f, indent=2)
            print(f"Simulation results saved to: {args.output}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()