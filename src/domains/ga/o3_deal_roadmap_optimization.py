#!/usr/bin/env python3
"""
O3 Deal Roadmap Optimization

This module implements the Optimization-Oriented Operation (O3) process
for the Moneyball Deal Model, providing advanced hypergraph-based optimization
for complex multi-stakeholder deals.
"""

import os
import json
import random
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Set, Optional, Union, Callable
from datetime import datetime
from collections import defaultdict
import time
import argparse
import csv

class EntityNode:
    """
    Represents a stakeholder entity in the deal hypergraph.
    """
    def __init__(
        self, 
        id: str, 
        name: str, 
        entity_type: str, 
        capacity: Dict[str, float] = None,
        preferences: Dict[str, float] = None,
        constraints: Dict[str, Any] = None
    ):
        """
        Initialize an EntityNode.
        
        Args:
            id: Unique identifier for the entity
            name: Human-readable name
            entity_type: Type of entity (government, corporate, ngo, civilian)
            capacity: Dictionary of resource capacities
            preferences: Dictionary of value dimension preferences
            constraints: Dictionary of operational constraints
        """
        self.id = id
        self.name = name
        self.entity_type = entity_type.lower()
        self.capacity = capacity or {}
        self.preferences = preferences or {}
        self.constraints = constraints or {}
        self.value_received = 0.0
        self.value_contributed = 0.0
        self.deals = set()  # Set of deals this entity is participating in
        
        # Ensure entity type is valid
        valid_types = ["government", "corporate", "ngo", "civilian"]
        if self.entity_type not in valid_types:
            raise ValueError(f"Entity type must be one of {valid_types}")
        
        # Initialize preference weights if not provided
        if not self.preferences:
            if self.entity_type == "government":
                self.preferences = {"economic": 0.3, "social": 0.3, "mission": 0.3, "reputation": 0.1}
            elif self.entity_type == "corporate":
                self.preferences = {"economic": 0.7, "social": 0.1, "innovation": 0.1, "reputation": 0.1}
            elif self.entity_type == "ngo":
                self.preferences = {"economic": 0.1, "social": 0.6, "mission": 0.2, "reputation": 0.1}
            elif self.entity_type == "civilian":
                self.preferences = {"economic": 0.3, "social": 0.4, "service": 0.2, "reputation": 0.1}
    
    def get_subjective_value(self, value_object: Dict[str, float]) -> float:
        """
        Calculate the subjective value of a value object to this entity.
        
        Args:
            value_object: Dictionary of value dimensions and amounts
            
        Returns:
            Subjective value to this entity
        """
        subjective_value = 0.0
        
        for dimension, amount in value_object.items():
            weight = self.preferences.get(dimension, 0.0)
            subjective_value += amount * weight
        
        return subjective_value
    
    def add_deal(self, deal_id: str) -> None:
        """Add a deal to this entity's participation set."""
        self.deals.add(deal_id)
    
    def can_participate(self, required_capacity: Dict[str, float]) -> bool:
        """
        Check if this entity has sufficient capacity to participate in a deal.
        
        Args:
            required_capacity: Dictionary of required capacities
            
        Returns:
            True if entity has sufficient capacity, False otherwise
        """
        for resource, amount in required_capacity.items():
            available = self.capacity.get(resource, 0.0)
            if available < amount:
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "capacity": self.capacity,
            "preferences": self.preferences,
            "constraints": self.constraints,
            "value_received": self.value_received,
            "value_contributed": self.value_contributed,
            "deals": list(self.deals)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityNode':
        """Create an EntityNode from a dictionary representation."""
        entity = cls(
            id=data["id"],
            name=data["name"],
            entity_type=data["entity_type"],
            capacity=data["capacity"],
            preferences=data["preferences"],
            constraints=data["constraints"]
        )
        entity.value_received = data.get("value_received", 0.0)
        entity.value_contributed = data.get("value_contributed", 0.0)
        entity.deals = set(data.get("deals", []))
        return entity

class ValueEdge:
    """
    Represents a value transfer between entities in the deal hypergraph.
    """
    def __init__(
        self, 
        source_id: str, 
        target_id: str, 
        value: Dict[str, float],
        deal_id: str,
        conditions: Dict[str, Any] = None
    ):
        """
        Initialize a ValueEdge.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            value: Dictionary of value dimensions and amounts
            deal_id: ID of the deal this value transfer is part of
            conditions: Dictionary of conditions for the value transfer
        """
        self.source_id = source_id
        self.target_id = target_id
        self.value = value
        self.deal_id = deal_id
        self.conditions = conditions or {}
        self.id = f"{source_id}→{target_id}:{deal_id}"
        
    def get_total_value(self) -> float:
        """Calculate the total value across all dimensions."""
        return sum(self.value.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the value edge to a dictionary representation."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "value": self.value,
            "deal_id": self.deal_id,
            "conditions": self.conditions,
            "total_value": self.get_total_value()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValueEdge':
        """Create a ValueEdge from a dictionary representation."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            value=data["value"],
            deal_id=data["deal_id"],
            conditions=data["conditions"]
        )

class DealHyperedge:
    """
    Represents a deal as a hyperedge connecting multiple entities in the hypergraph.
    """
    def __init__(
        self, 
        id: str, 
        name: str, 
        entities: List[str],
        value_edges: List[ValueEdge] = None,
        intent: str = None,
        solutions: List[str] = None,
        financing: Dict[str, Any] = None,
        execution_plan: Dict[str, Any] = None,
        verification: Dict[str, Any] = None,
        status: str = "proposed"
    ):
        """
        Initialize a DealHyperedge.
        
        Args:
            id: Unique identifier for the deal
            name: Human-readable name
            entities: List of entity IDs participating in the deal
            value_edges: List of value transfers between entities
            intent: Description of the deal's intent
            solutions: List of solution components
            financing: Financing structure details
            execution_plan: Execution plan details
            verification: Verification mechanisms
            status: Deal status (proposed, active, completed, failed)
        """
        self.id = id
        self.name = name
        self.entities = set(entities)
        self.value_edges = value_edges or []
        self.intent = intent
        self.solutions = solutions or []
        self.financing = financing or {}
        self.execution_plan = execution_plan or {}
        self.verification = verification or {}
        self.status = status
        self.creation_time = datetime.now().isoformat()
        self.update_time = self.creation_time
        
        # Validate status
        valid_statuses = ["proposed", "active", "completed", "failed"]
        if self.status not in valid_statuses:
            raise ValueError(f"Deal status must be one of {valid_statuses}")
    
    def add_entity(self, entity_id: str) -> None:
        """Add an entity to the deal."""
        self.entities.add(entity_id)
        self.update_time = datetime.now().isoformat()
    
    def add_value_edge(self, edge: ValueEdge) -> None:
        """Add a value transfer to the deal."""
        # Ensure both entities are part of the deal
        if edge.source_id not in self.entities or edge.target_id not in self.entities:
            raise ValueError("Both source and target entities must be part of the deal")
        
        # Ensure the edge references this deal
        if edge.deal_id != self.id:
            raise ValueError("Value edge must reference this deal")
        
        self.value_edges.append(edge)
        self.update_time = datetime.now().isoformat()
    
    def get_total_value(self) -> float:
        """Calculate the total value created by this deal."""
        return sum(edge.get_total_value() for edge in self.value_edges)
    
    def get_entity_value(self, entity_id: str) -> Dict[str, float]:
        """
        Calculate the net value for a specific entity in this deal.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Dictionary of value dimensions and net amounts
        """
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} is not part of this deal")
        
        # Initialize net value by dimension
        net_value = defaultdict(float)
        
        # Add value received
        for edge in self.value_edges:
            if edge.target_id == entity_id:
                for dimension, amount in edge.value.items():
                    net_value[dimension] += amount
            
            # Subtract value given
            if edge.source_id == entity_id:
                for dimension, amount in edge.value.items():
                    net_value[dimension] -= amount
        
        return dict(net_value)
    
    def is_win_win(self, entity_preferences: Dict[str, Dict[str, float]]) -> Tuple[bool, Dict[str, float]]:
        """
        Check if this deal is a win-win for all participants.
        
        Args:
            entity_preferences: Dictionary mapping entity IDs to preference dictionaries
            
        Returns:
            Tuple of (is_win_win, entity_subjective_values)
        """
        entity_values = {}
        
        for entity_id in self.entities:
            # Get net value for this entity
            net_value = self.get_entity_value(entity_id)
            
            # Calculate subjective value based on preferences
            preferences = entity_preferences.get(entity_id, {})
            subjective_value = 0.0
            
            for dimension, amount in net_value.items():
                weight = preferences.get(dimension, 0.0)
                subjective_value += amount * weight
            
            entity_values[entity_id] = subjective_value
        
        # Check if all entities receive positive value
        is_win_win = all(value > 0 for value in entity_values.values())
        
        return is_win_win, entity_values
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the deal to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "entities": list(self.entities),
            "value_edges": [edge.to_dict() for edge in self.value_edges],
            "intent": self.intent,
            "solutions": self.solutions,
            "financing": self.financing,
            "execution_plan": self.execution_plan,
            "verification": self.verification,
            "status": self.status,
            "creation_time": self.creation_time,
            "update_time": self.update_time,
            "total_value": self.get_total_value()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DealHyperedge':
        """Create a DealHyperedge from a dictionary representation."""
        deal = cls(
            id=data["id"],
            name=data["name"],
            entities=data["entities"],
            intent=data["intent"],
            solutions=data["solutions"],
            financing=data["financing"],
            execution_plan=data["execution_plan"],
            verification=data["verification"],
            status=data["status"]
        )
        
        # Add value edges
        for edge_data in data.get("value_edges", []):
            edge = ValueEdge.from_dict(edge_data)
            deal.value_edges.append(edge)
        
        # Set timestamps
        deal.creation_time = data.get("creation_time", deal.creation_time)
        deal.update_time = data.get("update_time", deal.update_time)
        
        return deal

class DealRoadmap:
    """
    Represents a sequence of deals forming a roadmap for value creation.
    """
    def __init__(
        self, 
        id: str, 
        name: str, 
        deals: List[str],
        dependencies: Dict[str, List[str]] = None,
        timeline: Dict[str, Dict[str, Any]] = None,
        objectives: Dict[str, Any] = None
    ):
        """
        Initialize a DealRoadmap.
        
        Args:
            id: Unique identifier for the roadmap
            name: Human-readable name
            deals: List of deal IDs in the roadmap
            dependencies: Dictionary mapping deal IDs to lists of prerequisite deal IDs
            timeline: Dictionary mapping deal IDs to timeline information
            objectives: Objectives and success criteria for the roadmap
        """
        self.id = id
        self.name = name
        self.deals = deals
        self.dependencies = dependencies or {}
        self.timeline = timeline or {}
        self.objectives = objectives or {}
        self.creation_time = datetime.now().isoformat()
        self.update_time = self.creation_time
    
    def add_deal(self, deal_id: str, dependencies: List[str] = None, timeline: Dict[str, Any] = None) -> None:
        """
        Add a deal to the roadmap.
        
        Args:
            deal_id: ID of the deal to add
            dependencies: List of prerequisite deal IDs
            timeline: Timeline information for the deal
        """
        if deal_id not in self.deals:
            self.deals.append(deal_id)
        
        if dependencies:
            self.dependencies[deal_id] = dependencies
        
        if timeline:
            self.timeline[deal_id] = timeline
        
        self.update_time = datetime.now().isoformat()
    
    def get_critical_path(self) -> List[str]:
        """
        Calculate the critical path through the roadmap.
        
        Returns:
            List of deal IDs forming the critical path
        """
        # Build directed graph of dependencies
        graph = defaultdict(list)
        for deal_id, deps in self.dependencies.items():
            for dep in deps:
                graph[dep].append(deal_id)
        
        # Find all deals with no dependencies
        roots = [deal for deal in self.deals if deal not in self.dependencies or not self.dependencies[deal]]
        
        # Find all deals with no dependents
        leaves = set(self.deals)
        for deps in graph.values():
            for deal in deps:
                if deal in leaves:
                    leaves.remove(deal)
        
        # Calculate path lengths from each root to each leaf
        def find_longest_path(start, end, visited=None):
            if visited is None:
                visited = set()
            
            if start == end:
                return [start]
            
            visited.add(start)
            longest_path = None
            max_length = -1
            
            for next_deal in graph.get(start, []):
                if next_deal not in visited:
                    path = find_longest_path(next_deal, end, visited.copy())
                    if path and len(path) > max_length:
                        longest_path = path
                        max_length = len(path)
            
            if longest_path:
                return [start] + longest_path
            else:
                return None
        
        # Find the longest path from any root to any leaf
        critical_path = None
        max_path_length = -1
        
        for root in roots:
            for leaf in leaves:
                path = find_longest_path(root, leaf)
                if path and len(path) > max_path_length:
                    critical_path = path
                    max_path_length = len(path)
        
        return critical_path or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the roadmap to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "deals": self.deals,
            "dependencies": self.dependencies,
            "timeline": self.timeline,
            "objectives": self.objectives,
            "creation_time": self.creation_time,
            "update_time": self.update_time,
            "critical_path": self.get_critical_path()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DealRoadmap':
        """Create a DealRoadmap from a dictionary representation."""
        roadmap = cls(
            id=data["id"],
            name=data["name"],
            deals=data["deals"],
            dependencies=data["dependencies"],
            timeline=data["timeline"],
            objectives=data["objectives"]
        )
        
        # Set timestamps
        roadmap.creation_time = data.get("creation_time", roadmap.creation_time)
        roadmap.update_time = data.get("update_time", roadmap.update_time)
        
        return roadmap

class DealHypergraph:
    """
    A hypergraph representation of entities and deals for optimization.
    """
    def __init__(self):
        """Initialize an empty deal hypergraph."""
        self.entities = {}  # EntityNode objects by ID
        self.value_edges = {}  # ValueEdge objects by ID
        self.deals = {}  # DealHyperedge objects by ID
        self.roadmaps = {}  # DealRoadmap objects by ID
    
    def add_entity(self, entity: EntityNode) -> None:
        """Add an entity to the hypergraph."""
        self.entities[entity.id] = entity
    
    def add_value_edge(self, edge: ValueEdge) -> None:
        """Add a value edge to the hypergraph."""
        # Ensure source and target entities exist
        if edge.source_id not in self.entities:
            raise ValueError(f"Source entity {edge.source_id} does not exist")
        
        if edge.target_id not in self.entities:
            raise ValueError(f"Target entity {edge.target_id} does not exist")
        
        # Ensure deal exists
        if edge.deal_id not in self.deals:
            raise ValueError(f"Deal {edge.deal_id} does not exist")
        
        self.value_edges[edge.id] = edge
    
    def add_deal(self, deal: DealHyperedge) -> None:
        """Add a deal to the hypergraph."""
        # Ensure all entities exist
        for entity_id in deal.entities:
            if entity_id not in self.entities:
                raise ValueError(f"Entity {entity_id} does not exist")
        
        self.deals[deal.id] = deal
        
        # Update entity deal participation
        for entity_id in deal.entities:
            self.entities[entity_id].add_deal(deal.id)
        
        # Add deal's value edges
        for edge in deal.value_edges:
            if edge.id not in self.value_edges:
                self.value_edges[edge.id] = edge
    
    def add_roadmap(self, roadmap: DealRoadmap) -> None:
        """Add a roadmap to the hypergraph."""
        # Ensure all deals exist
        for deal_id in roadmap.deals:
            if deal_id not in self.deals:
                raise ValueError(f"Deal {deal_id} does not exist")
        
        self.roadmaps[roadmap.id] = roadmap
    
    def get_entity_deals(self, entity_id: str) -> List[DealHyperedge]:
        """Get all deals an entity is participating in."""
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        entity = self.entities[entity_id]
        return [self.deals[deal_id] for deal_id in entity.deals if deal_id in self.deals]
    
    def get_deal_entities(self, deal_id: str) -> List[EntityNode]:
        """Get all entities participating in a deal."""
        if deal_id not in self.deals:
            raise ValueError(f"Deal {deal_id} does not exist")
        
        deal = self.deals[deal_id]
        return [self.entities[entity_id] for entity_id in deal.entities if entity_id in self.entities]
    
    def get_entity_value(self, entity_id: str) -> Dict[str, float]:
        """
        Calculate the total value an entity receives across all deals.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Dictionary of value dimensions and amounts
        """
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        # Initialize total value by dimension
        total_value = defaultdict(float)
        
        # Sum value from all deals
        for deal_id in self.entities[entity_id].deals:
            if deal_id in self.deals:
                deal = self.deals[deal_id]
                deal_value = deal.get_entity_value(entity_id)
                
                for dimension, amount in deal_value.items():
                    total_value[dimension] += amount
        
        return dict(total_value)
    
    def get_total_value(self) -> float:
        """Calculate the total value created across all deals."""
        return sum(deal.get_total_value() for deal in self.deals.values())
    
    def get_value_distribution(self) -> Dict[str, float]:
        """
        Calculate the distribution of value across all entities.
        
        Returns:
            Dictionary mapping entity IDs to total subjective value
        """
        distribution = {}
        
        for entity_id, entity in self.entities.items():
            # Get total value for this entity
            value_by_dimension = self.get_entity_value(entity_id)
            
            # Calculate subjective value based on preferences
            subjective_value = 0.0
            for dimension, amount in value_by_dimension.items():
                weight = entity.preferences.get(dimension, 0.0)
                subjective_value += amount * weight
            
            distribution[entity_id] = subjective_value
        
        return distribution
    
    def find_potential_deals(self) -> List[List[str]]:
        """
        Find potential new deals based on entity relationships.
        
        Returns:
            List of potential entity groupings for deals
        """
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
        
        return potential_deals
    
    def create_deal_from_entities(self, entities: List[str], name: str = None) -> DealHyperedge:
        """
        Create a new deal from a group of entities, with auto-generated value edges.
        
        Args:
            entities: List of entity IDs to include in the deal
            name: Optional name for the deal
            
        Returns:
            New DealHyperedge object
        """
        # Generate a unique ID and name
        deal_id = f"deal_{len(self.deals) + 1}_{int(time.time())}"
        if name is None:
            name = f"Deal {len(self.deals) + 1}"
        
        # Create the deal
        deal = DealHyperedge(
            id=deal_id,
            name=name,
            entities=entities,
            intent="Auto-generated deal based on collaboration potential"
        )
        
        # Auto-generate value edges based on entity preferences
        for i, source_id in enumerate(entities):
            source = self.entities[source_id]
            
            # Each entity provides value in its strongest dimensions
            source_strengths = sorted(
                source.preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # And receives value in its most preferred dimensions
            source_preferences = sorted(
                source.preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Connect to all other entities
            for target_id in entities:
                if source_id == target_id:
                    continue
                
                target = self.entities[target_id]
                
                # Create value flowing from source to target
                source_to_target = {}
                if source_strengths:
                    # Source provides value in its strongest dimension
                    dimension, _ = source_strengths[0]
                    source_to_target[dimension] = 10.0  # Arbitrary initial value
                
                # Create value flowing from target to source
                target_to_source = {}
                if source_preferences:
                    # Source receives value in its most preferred dimension
                    dimension, _ = source_preferences[0]
                    target_to_source[dimension] = 10.0  # Arbitrary initial value
                
                # Create the edges
                if source_to_target:
                    edge = ValueEdge(
                        source_id=source_id,
                        target_id=target_id,
                        value=source_to_target,
                        deal_id=deal_id
                    )
                    deal.add_value_edge(edge)
                
                if target_to_source:
                    edge = ValueEdge(
                        source_id=target_id,
                        target_id=source_id,
                        value=target_to_source,
                        deal_id=deal_id
                    )
                    deal.add_value_edge(edge)
        
        return deal
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the hypergraph to a dictionary representation."""
        return {
            "entities": {id: entity.to_dict() for id, entity in self.entities.items()},
            "value_edges": {id: edge.to_dict() for id, edge in self.value_edges.items()},
            "deals": {id: deal.to_dict() for id, deal in self.deals.items()},
            "roadmaps": {id: roadmap.to_dict() for id, roadmap in self.roadmaps.items()},
            "stats": {
                "entity_count": len(self.entities),
                "edge_count": len(self.value_edges),
                "deal_count": len(self.deals),
                "roadmap_count": len(self.roadmaps),
                "total_value": self.get_total_value()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DealHypergraph':
        """Create a DealHypergraph from a dictionary representation."""
        graph = cls()
        
        # Add entities
        for entity_data in data.get("entities", {}).values():
            entity = EntityNode.from_dict(entity_data)
            graph.entities[entity.id] = entity
        
        # Add deals (which will validate entities)
        for deal_data in data.get("deals", {}).values():
            deal = DealHyperedge.from_dict(deal_data)
            graph.deals[deal.id] = deal
            
            # Update entity deal participation
            for entity_id in deal.entities:
                if entity_id in graph.entities:
                    graph.entities[entity_id].add_deal(deal.id)
        
        # Add value edges
        for edge_data in data.get("value_edges", {}).values():
            edge = ValueEdge.from_dict(edge_data)
            graph.value_edges[edge.id] = edge
        
        # Add roadmaps
        for roadmap_data in data.get("roadmaps", {}).values():
            roadmap = DealRoadmap.from_dict(roadmap_data)
            graph.roadmaps[roadmap.id] = roadmap
        
        return graph
    
    def save_to_file(self, file_path: str) -> None:
        """Save the hypergraph to a JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'DealHypergraph':
        """Load a hypergraph from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)

class O3Optimizer:
    """
    Optimization-Oriented Operation (O3) process for deal optimization.
    """
    def __init__(self, graph: DealHypergraph):
        """
        Initialize the O3 optimizer.
        
        Args:
            graph: DealHypergraph to optimize
        """
        self.graph = graph
    
    def optimize_deal_values(self, deal_id: str) -> Dict[str, Any]:
        """
        Optimize the value distribution within a deal to ensure win-win outcomes.
        
        Args:
            deal_id: ID of the deal to optimize
            
        Returns:
            Optimization results
        """
        if deal_id not in self.graph.deals:
            raise ValueError(f"Deal {deal_id} does not exist")
        
        deal = self.graph.deals[deal_id]
        
        # Get entity preferences
        entity_preferences = {
            entity_id: self.graph.entities[entity_id].preferences
            for entity_id in deal.entities
            if entity_id in self.graph.entities
        }
        
        # Check if the deal is currently win-win
        is_win_win, entity_values = deal.is_win_win(entity_preferences)
        
        # If already win-win, just return current state
        if is_win_win:
            return {
                "deal_id": deal_id,
                "status": "already_win_win",
                "entity_values": entity_values,
                "original_value_edges": [edge.to_dict() for edge in deal.value_edges],
                "optimized_value_edges": [edge.to_dict() for edge in deal.value_edges]
            }
        
        # Identify entities with negative value
        negative_entities = [
            entity_id for entity_id, value in entity_values.items()
            if value <= 0
        ]
        
        # Create a copy of value edges for optimization
        optimized_edges = [
            ValueEdge(
                source_id=edge.source_id,
                target_id=edge.target_id,
                value=edge.value.copy(),
                deal_id=edge.deal_id,
                conditions=edge.conditions.copy() if edge.conditions else None
            )
            for edge in deal.value_edges
        ]
        
        # Adjust value flows to make the deal win-win
        for entity_id in negative_entities:
            # Calculate how much value this entity needs
            value_needed = abs(entity_values[entity_id]) + 1.0  # Add buffer
            
            # Find other entities with positive value
            positive_entities = [
                other_id for other_id, value in entity_values.items()
                if value > 0 and other_id != entity_id
            ]
            
            if not positive_entities:
                # No entities to redistribute from, deal might not be viable
                continue
            
            # Calculate how much each positive entity can contribute
            total_positive_value = sum(entity_values[e] for e in positive_entities)
            
            for contributor_id in positive_entities:
                # Calculate fair share based on relative value
                fair_share = value_needed * (entity_values[contributor_id] / total_positive_value)
                
                # Find the most preferred dimension for the negative entity
                entity = self.graph.entities[entity_id]
                preferred_dimensions = sorted(
                    entity.preferences.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Find or create an edge from contributor to negative entity
                contributor_edge = None
                for edge in optimized_edges:
                    if edge.source_id == contributor_id and edge.target_id == entity_id:
                        contributor_edge = edge
                        break
                
                if not contributor_edge:
                    # Create a new edge
                    contributor_edge = ValueEdge(
                        source_id=contributor_id,
                        target_id=entity_id,
                        value={},
                        deal_id=deal_id
                    )
                    optimized_edges.append(contributor_edge)
                
                # Add value in preferred dimension
                if preferred_dimensions:
                    dimension, _ = preferred_dimensions[0]
                    contributor_edge.value[dimension] = contributor_edge.value.get(dimension, 0.0) + fair_share
        
        # Create a temporary deal with optimized edges to check if win-win
        temp_deal = DealHyperedge(
            id="temp_" + deal_id,
            name="Temporary " + deal.name,
            entities=list(deal.entities),
            value_edges=optimized_edges,
            intent=deal.intent,
            solutions=deal.solutions,
            financing=deal.financing,
            execution_plan=deal.execution_plan,
            verification=deal.verification
        )
        
        # Check if the optimized deal is win-win
        optimized_win_win, optimized_values = temp_deal.is_win_win(entity_preferences)
        
        return {
            "deal_id": deal_id,
            "status": "optimized" if optimized_win_win else "not_viable",
            "original_win_win": is_win_win,
            "original_entity_values": entity_values,
            "optimized_win_win": optimized_win_win,
            "optimized_entity_values": optimized_values,
            "original_value_edges": [edge.to_dict() for edge in deal.value_edges],
            "optimized_value_edges": [edge.to_dict() for edge in optimized_edges]
        }
    
    def apply_optimization(self, optimization_result: Dict[str, Any]) -> bool:
        """
        Apply optimization results to the deal in the graph.
        
        Args:
            optimization_result: Result from optimize_deal_values
            
        Returns:
            True if optimization was applied, False otherwise
        """
        # Only apply if the optimization succeeded
        if optimization_result["status"] != "optimized":
            return False
        
        deal_id = optimization_result["deal_id"]
        if deal_id not in self.graph.deals:
            return False
        
        deal = self.graph.deals[deal_id]
        
        # Replace the value edges with optimized ones
        deal.value_edges = []
        
        for edge_data in optimization_result["optimized_value_edges"]:
            edge = ValueEdge.from_dict(edge_data)
            deal.add_value_edge(edge)
            
            # Also update the edge in the graph
            self.graph.value_edges[edge.id] = edge
        
        return True
    
    def optimize_roadmap(
        self,
        entity_ids: List[str] = None,
        max_deals: int = 5,
        objective: str = "total_value",
        constraints: Dict[str, Any] = None
    ) -> DealRoadmap:
        """
        Optimize a deal roadmap to maximize value creation.
        
        Args:
            entity_ids: List of entity IDs to include in the roadmap (if None, use all)
            max_deals: Maximum number of deals in the roadmap
            objective: Optimization objective (total_value, balance, speed)
            constraints: Additional constraints on the optimization
            
        Returns:
            Optimized DealRoadmap
        """
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
        for entity_group in self.graph.find_potential_deals():
            # Only include groups with at least one target entity
            if any(entity_id in entity_ids for entity_id in entity_group):
                # Create a potential deal
                deal = self.graph.create_deal_from_entities(
                    entity_group,
                    name=f"Potential Deal {len(potential_deals) + 1}"
                )
                potential_deals.append(deal)
        
        # 3. Optimize each deal
        optimized_deals = []
        for deal in potential_deals:
            # Skip deals already in the graph
            if deal.id in self.graph.deals:
                optimized_deals.append(deal)
                continue
            
            # Create a temporary copy of the graph with this deal
            temp_graph = DealHypergraph()
            
            # Add all entities and existing deals
            for entity_id, entity in self.graph.entities.items():
                temp_graph.entities[entity_id] = entity
            
            for existing_deal_id, existing_deal in self.graph.deals.items():
                temp_graph.deals[existing_deal_id] = existing_deal
            
            # Add the potential deal
            temp_graph.add_deal(deal)
            
            # Optimize the deal
            temp_optimizer = O3Optimizer(temp_graph)
            optimization_result = temp_optimizer.optimize_deal_values(deal.id)
            
            # If optimizable to win-win, include it
            if optimization_result["status"] in ["optimized", "already_win_win"]:
                # Update the deal with optimized edges if needed
                if optimization_result["status"] == "optimized":
                    deal.value_edges = []
                    for edge_data in optimization_result["optimized_value_edges"]:
                        edge = ValueEdge.from_dict(edge_data)
                        deal.add_value_edge(edge)
                
                optimized_deals.append(deal)
        
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
        
        return roadmap
    
    def monte_carlo_roadmap_simulation(
        self,
        roadmap_id: str,
        num_simulations: int = 100,
        risk_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulations to assess roadmap risk and robustness.
        
        Args:
            roadmap_id: ID of the roadmap to simulate
            num_simulations: Number of simulations to run
            risk_params: Parameters for the risk simulation
            
        Returns:
            Simulation results
        """
        if roadmap_id not in self.graph.roadmaps:
            raise ValueError(f"Roadmap {roadmap_id} does not exist")
        
        roadmap = self.graph.roadmaps[roadmap_id]
        
        # Default risk parameters
        if risk_params is None:
            risk_params = {
                "deal_failure_prob": 0.1,  # Probability of a deal failing
                "value_variation": 0.2,  # Variation in realized value (+/-)
                "timeline_variation": 0.3,  # Variation in timeline (+/-)
                "dependency_failure_impact": 0.5  # Impact of dependency failure
            }
        
        # Simulation results
        results = {
            "roadmap_id": roadmap_id,
            "num_simulations": num_simulations,
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
        
        # Run simulations
        total_values = []
        successful_simulations = 0
        critical_deal_failures = defaultdict(int)
        
        for _ in range(num_simulations):
            simulation = {
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
                
                # Determine if deal succeeds
                deal_success = random.random() > failure_prob
                
                if not deal_success:
                    critical_deal_failures[deal_id] += 1
                
                # Calculate deal value with variation
                if deal_id in self.graph.deals:
                    deal = self.graph.deals[deal_id]
                    base_value = deal.get_total_value()
                else:
                    base_value = 10.0  # Default value for potential deals
                
                value_variation = 1.0 + (2 * random.random() - 1) * risk_params["value_variation"]
                simulated_value = base_value * value_variation if deal_success else 0.0
                
                # Calculate deal timeline with variation
                timeline_info = roadmap.timeline.get(deal_id, {"duration": 60})
                base_duration = timeline_info.get("duration", 60)
                
                duration_variation = 1.0 + (2 * random.random() - 1) * risk_params["timeline_variation"]
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
            
            # Save simulation results
            results["simulations"].append(simulation)
            
            total_values.append(simulation["total_value"])
            if simulation["success"]:
                successful_simulations += 1
        
        # Calculate summary statistics
        if total_values:
            results["summary"]["success_rate"] = successful_simulations / num_simulations
            results["summary"]["expected_value"] = np.mean(total_values)
            results["summary"]["value_at_risk"] = np.percentile(total_values, 5)  # 5% VaR
            
            # Calculate expected duration
            durations = [sim["duration"] for sim in results["simulations"]]
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
                        "failure_rate": count / num_simulations
                    }
                    for deal_id, count in critical_deals[:3]  # Top 3 critical deals
                ]
        
        return results
    
    def generate_alternative_roadmaps(
        self,
        entity_ids: List[str],
        num_alternatives: int = 3,
        objectives: List[str] = None
    ) -> List[DealRoadmap]:
        """
        Generate alternative roadmaps with different optimization objectives.
        
        Args:
            entity_ids: List of entity IDs to include
            num_alternatives: Number of alternative roadmaps to generate
            objectives: List of objectives to use
            
        Returns:
            List of alternative roadmaps
        """
        if objectives is None:
            objectives = ["total_value", "balance", "speed", "hybrid"]
        
        alternatives = []
        
        # Generate a roadmap for each objective
        for objective in objectives[:num_alternatives]:
            roadmap = self.optimize_roadmap(
                entity_ids=entity_ids,
                objective=objective
            )
            
            alternatives.append(roadmap)
        
        return alternatives
    
    def visualize_roadmap(self, roadmap_id: str, output_file: str = None) -> None:
        """
        Visualize a roadmap timeline as a Gantt chart.
        
        Args:
            roadmap_id: ID of the roadmap to visualize
            output_file: Optional file path to save the visualization
        """
        if roadmap_id not in self.graph.roadmaps:
            raise ValueError(f"Roadmap {roadmap_id} does not exist")
        
        roadmap = self.graph.roadmaps[roadmap_id]
        
        # Prepare data for visualization
        deals = []
        start_times = []
        durations = []
        colors = []
        
        for deal_id in roadmap.deals:
            # Get deal name
            if deal_id in self.graph.deals:
                deal_name = self.graph.deals[deal_id].name
            else:
                deal_name = f"Deal {deal_id}"
            
            # Get timeline info
            timeline_info = roadmap.timeline.get(deal_id, {})
            start_time = timeline_info.get("start", 0)
            duration = timeline_info.get("duration", 60)
            
            deals.append(deal_name)
            start_times.append(start_time)
            durations.append(duration)
            
            # Color based on dependencies
            if roadmap.dependencies.get(deal_id, []):
                colors.append('orange')
            else:
                colors.append('steelblue')
        
        # Create the figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the Gantt chart
        y_positions = range(len(deals))
        ax.barh(y_positions, durations, left=start_times, color=colors, alpha=0.8)
        
        # Customize the plot
        ax.set_yticks(y_positions)
        ax.set_yticklabels(deals)
        ax.set_xlabel('Timeline (days)')
        ax.set_title(f'Roadmap Timeline: {roadmap.name}')
        
        # Add a grid
        ax.grid(axis='x', alpha=0.3)
        
        # Add value annotations
        for i, deal_id in enumerate(roadmap.deals):
            if deal_id in self.graph.deals:
                deal = self.graph.deals[deal_id]
                value = deal.get_total_value()
                ax.text(
                    start_times[i] + durations[i] + 5,
                    i,
                    f'Value: {value:.1f}',
                    va='center'
                )
        
        # Add critical path
        critical_path = roadmap.get_critical_path()
        if critical_path:
            for i, deal_id in enumerate(roadmap.deals):
                if deal_id in critical_path:
                    # Highlight critical path deals
                    ax.barh(
                        i,
                        durations[i],
                        left=start_times[i],
                        color='crimson',
                        alpha=0.6,
                        edgecolor='black',
                        linewidth=2
                    )
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()
    
    def implement_roadmap(self, roadmap_id: str) -> Dict[str, Any]:
        """
        Implement a roadmap by adding all its deals to the graph.
        
        Args:
            roadmap_id: ID of the roadmap to implement
            
        Returns:
            Implementation results
        """
        if roadmap_id not in self.graph.roadmaps:
            raise ValueError(f"Roadmap {roadmap_id} does not exist")
        
        roadmap = self.graph.roadmaps[roadmap_id]
        
        results = {
            "roadmap_id": roadmap_id,
            "deals_added": [],
            "deals_optimized": [],
            "total_value_added": 0.0
        }
        
        # Implement deals in dependency order
        # First, find all deals without dependencies
        no_deps = [
            deal_id for deal_id in roadmap.deals
            if not roadmap.dependencies.get(deal_id, [])
        ]
        
        # Then, iteratively implement deals as their dependencies are satisfied
        implemented = set()
        pending = set(roadmap.deals)
        
        # Start with no-dependency deals
        next_batch = no_deps
        
        while next_batch:
            # Implement this batch
            for deal_id in next_batch:
                # Skip if already in the graph
                if deal_id in self.graph.deals:
                    implemented.add(deal_id)
                    pending.remove(deal_id)
                    continue
                
                # Skip if dependencies not met
                deps = roadmap.dependencies.get(deal_id, [])
                if not all(dep in implemented for dep in deps):
                    continue
                
                # Create the deal if it doesn't exist
                potential_deals = [d for d in self.graph.find_potential_deals() if deal_id.startswith("potential_")]
                if potential_deals:
                    for entities in potential_deals:
                        deal = self.graph.create_deal_from_entities(
                            entities,
                            name=f"Implemented Deal {deal_id}"
                        )
                        
                        # Optimize the deal
                        optimization_result = self.optimize_deal_values(deal.id)
                        
                        if optimization_result["status"] in ["optimized", "already_win_win"]:
                            # Apply optimization if needed
                            if optimization_result["status"] == "optimized":
                                self.apply_optimization(optimization_result)
                                results["deals_optimized"].append(deal.id)
                            
                            self.graph.add_deal(deal)
                            
                            results["deals_added"].append(deal.id)
                            results["total_value_added"] += deal.get_total_value()
                
                implemented.add(deal_id)
                pending.remove(deal_id)
            
            # Find the next batch of deals whose dependencies are now satisfied
            next_batch = [
                deal_id for deal_id in pending
                if all(dep in implemented for dep in roadmap.dependencies.get(deal_id, []))
            ]
        
        return results

def create_example_hypergraph() -> DealHypergraph:
    """Create an example DealHypergraph for testing."""
    graph = DealHypergraph()
    
    # Create some entities
    entities = [
        EntityNode(
            id="govt1",
            name="Department of Commerce",
            entity_type="government",
            capacity={"budget": 100.0, "staff": 50.0},
            preferences={"economic": 0.4, "social": 0.3, "mission": 0.2, "reputation": 0.1}
        ),
        EntityNode(
            id="govt2",
            name="Small Business Administration",
            entity_type="government",
            capacity={"budget": 80.0, "staff": 30.0},
            preferences={"economic": 0.3, "social": 0.4, "mission": 0.2, "reputation": 0.1}
        ),
        EntityNode(
            id="corp1",
            name="TechCorp Inc.",
            entity_type="corporate",
            capacity={"budget": 200.0, "staff": 100.0},
            preferences={"economic": 0.7, "innovation": 0.2, "reputation": 0.1}
        ),
        EntityNode(
            id="corp2",
            name="Global Finance Group",
            entity_type="corporate",
            capacity={"budget": 300.0, "staff": 80.0},
            preferences={"economic": 0.8, "reputation": 0.1, "innovation": 0.1}
        ),
        EntityNode(
            id="ngo1",
            name="Community Development Fund",
            entity_type="ngo",
            capacity={"budget": 50.0, "staff": 20.0},
            preferences={"social": 0.6, "mission": 0.3, "economic": 0.1}
        ),
        EntityNode(
            id="civ1",
            name="Local Business Association",
            entity_type="civilian",
            capacity={"budget": 20.0, "staff": 10.0},
            preferences={"economic": 0.5, "social": 0.3, "service": 0.2}
        )
    ]
    
    for entity in entities:
        graph.add_entity(entity)
    
    # Create some deals
    deal1 = DealHyperedge(
        id="deal1",
        name="Small Business Innovation Partnership",
        entities=["govt1", "govt2", "corp1"],
        intent="Accelerate technological innovation in small businesses"
    )
    
    deal2 = DealHyperedge(
        id="deal2",
        name="Community Finance Initiative",
        entities=["govt2", "corp2", "ngo1", "civ1"],
        intent="Increase access to capital in underserved communities"
    )
    
    # Add value edges to deal1
    value_edges_deal1 = [
        ValueEdge(
            source_id="govt1",
            target_id="corp1",
            value={"economic": 30.0, "innovation": 20.0},
            deal_id="deal1"
        ),
        ValueEdge(
            source_id="govt2",
            target_id="corp1",
            value={"economic": 25.0, "social": 10.0},
            deal_id="deal1"
        ),
        ValueEdge(
            source_id="corp1",
            target_id="govt1",
            value={"economic": 15.0, "reputation": 10.0},
            deal_id="deal1"
        ),
        ValueEdge(
            source_id="corp1",
            target_id="govt2",
            value={"economic": 20.0, "mission": 15.0},
            deal_id="deal1"
        )
    ]
    
    for edge in value_edges_deal1:
        deal1.add_value_edge(edge)
    
    # Add value edges to deal2
    value_edges_deal2 = [
        ValueEdge(
            source_id="govt2",
            target_id="ngo1",
            value={"economic": 20.0, "mission": 15.0},
            deal_id="deal2"
        ),
        ValueEdge(
            source_id="corp2",
            target_id="ngo1",
            value={"economic": 40.0, "social": 10.0},
            deal_id="deal2"
        ),
        ValueEdge(
            source_id="corp2",
            target_id="civ1",
            value={"economic": 30.0, "service": 15.0},
            deal_id="deal2"
        ),
        ValueEdge(
            source_id="ngo1",
            target_id="govt2",
            value={"social": 25.0, "reputation": 15.0},
            deal_id="deal2"
        ),
        ValueEdge(
            source_id="ngo1",
            target_id="corp2",
            value={"reputation": 20.0, "social": 10.0},
            deal_id="deal2"
        ),
        ValueEdge(
            source_id="civ1",
            target_id="corp2",
            value={"economic": 10.0, "reputation": 5.0},
            deal_id="deal2"
        ),
        ValueEdge(
            source_id="civ1",
            target_id="ngo1",
            value={"social": 15.0, "mission": 10.0},
            deal_id="deal2"
        )
    ]
    
    for edge in value_edges_deal2:
        deal2.add_value_edge(edge)
    
    # Add deals to the graph
    graph.add_deal(deal1)
    graph.add_deal(deal2)
    
    # Create a roadmap
    roadmap = DealRoadmap(
        id="roadmap1",
        name="Economic Development Roadmap",
        deals=["deal1", "deal2"],
        dependencies={"deal2": ["deal1"]},
        timeline={
            "deal1": {"start": 0, "duration": 90, "end": 90},
            "deal2": {"start": 90, "duration": 120, "end": 210}
        },
        objectives={
            "primary_objective": "total_value",
            "target_entities": ["govt1", "govt2", "corp1", "corp2", "ngo1", "civ1"],
            "constraints": {"max_duration": 365}
        }
    )
    
    graph.add_roadmap(roadmap)
    
    return graph

def main():
    """Main function for the O3 Deal Roadmap Optimization."""
    parser = argparse.ArgumentParser(description="O3 Deal Roadmap Optimization")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create example command
    create_parser = subparsers.add_parser("create-example", help="Create an example hypergraph")
    create_parser.add_argument("--output", required=True, help="Output file path")
    
    # Optimize deal command
    optimize_deal_parser = subparsers.add_parser("optimize-deal", help="Optimize a deal")
    optimize_deal_parser.add_argument("--graph", required=True, help="Path to hypergraph file")
    optimize_deal_parser.add_argument("--deal-id", required=True, help="ID of the deal to optimize")
    optimize_deal_parser.add_argument("--apply", action="store_true", help="Apply optimization to the graph")
    optimize_deal_parser.add_argument("--output", help="Output file path for the updated graph")
    
    # Optimize roadmap command
    optimize_roadmap_parser = subparsers.add_parser("optimize-roadmap", help="Optimize a roadmap")
    optimize_roadmap_parser.add_argument("--graph", required=True, help="Path to hypergraph file")
    optimize_roadmap_parser.add_argument("--entities", nargs="+", help="Entity IDs to include")
    optimize_roadmap_parser.add_argument("--max-deals", type=int, default=5, help="Maximum number of deals")
    optimize_roadmap_parser.add_argument("--objective", default="total_value", 
                                        choices=["total_value", "balance", "speed", "hybrid"],
                                        help="Optimization objective")
    optimize_roadmap_parser.add_argument("--output", help="Output file path for the updated graph")
    
    # Visualize roadmap command
    visualize_parser = subparsers.add_parser("visualize", help="Visualize a roadmap")
    visualize_parser.add_argument("--graph", required=True, help="Path to hypergraph file")
    visualize_parser.add_argument("--roadmap-id", required=True, help="ID of the roadmap to visualize")
    visualize_parser.add_argument("--output", help="Output file path for the visualization")
    
    # Monte Carlo simulation command
    simulation_parser = subparsers.add_parser("simulate", help="Run Monte Carlo simulation on a roadmap")
    simulation_parser.add_argument("--graph", required=True, help="Path to hypergraph file")
    simulation_parser.add_argument("--roadmap-id", required=True, help="ID of the roadmap to simulate")
    simulation_parser.add_argument("--simulations", type=int, default=100, help="Number of simulations")
    simulation_parser.add_argument("--output", help="Output file path for simulation results")
    
    # Generate alternatives command
    alternatives_parser = subparsers.add_parser("alternatives", help="Generate alternative roadmaps")
    alternatives_parser.add_argument("--graph", required=True, help="Path to hypergraph file")
    alternatives_parser.add_argument("--entities", nargs="+", required=True, help="Entity IDs to include")
    alternatives_parser.add_argument("--count", type=int, default=3, help="Number of alternatives")
    alternatives_parser.add_argument("--output", help="Output file path for the updated graph")
    
    # Implement roadmap command
    implement_parser = subparsers.add_parser("implement", help="Implement a roadmap")
    implement_parser.add_argument("--graph", required=True, help="Path to hypergraph file")
    implement_parser.add_argument("--roadmap-id", required=True, help="ID of the roadmap to implement")
    implement_parser.add_argument("--output", required=True, help="Output file path for the updated graph")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "create-example":
        # Create example hypergraph
        graph = create_example_hypergraph()
        graph.save_to_file(args.output)
        print(f"Created example hypergraph with {len(graph.entities)} entities, "
              f"{len(graph.deals)} deals, and {len(graph.roadmaps)} roadmaps.")
        print(f"Saved to: {args.output}")
    
    elif args.command == "optimize-deal":
        # Load hypergraph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimizer
        optimizer = O3Optimizer(graph)
        
        # Optimize deal
        result = optimizer.optimize_deal_values(args.deal_id)
        
        # Print result summary
        print(f"Deal: {args.deal_id}")
        print(f"Optimization status: {result['status']}")
        
        if result['status'] == 'already_win_win':
            print("Deal is already win-win for all participants.")
        elif result['status'] == 'optimized':
            print("Deal has been optimized to be win-win for all participants.")
            if args.apply:
                optimizer.apply_optimization(result)
                print("Optimization has been applied to the deal.")
        else:
            print("Deal could not be optimized to be win-win for all participants.")
        
        # Save updated graph if requested
        if args.output and args.apply:
            graph.save_to_file(args.output)
            print(f"Updated graph saved to: {args.output}")
        
        # Save result details to JSON
        if args.output and not args.apply:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Optimization result saved to: {args.output}")
    
    elif args.command == "optimize-roadmap":
        # Load hypergraph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimizer
        optimizer = O3Optimizer(graph)
        
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
    
    elif args.command == "visualize":
        # Load hypergraph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimizer
        optimizer = O3Optimizer(graph)
        
        # Visualize roadmap
        optimizer.visualize_roadmap(args.roadmap_id, args.output)
        
        if args.output:
            print(f"Visualization saved to: {args.output}")
    
    elif args.command == "simulate":
        # Load hypergraph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimizer
        optimizer = O3Optimizer(graph)
        
        # Run simulation
        result = optimizer.monte_carlo_roadmap_simulation(
            roadmap_id=args.roadmap_id,
            num_simulations=args.simulations
        )
        
        # Print simulation summary
        print(f"Roadmap: {args.roadmap_id}")
        print(f"Simulations: {args.simulations}")
        print(f"Success rate: {result['summary']['success_rate']:.2f}")
        print(f"Expected value: {result['summary']['expected_value']:.2f}")
        print(f"Value at risk (5%): {result['summary']['value_at_risk']:.2f}")
        print(f"Expected duration: {result['summary']['expected_duration']:.2f} days")
        
        if result['summary']['critical_deals']:
            print("\nCritical deals (highest failure rates):")
            for deal in result['summary']['critical_deals']:
                print(f"  - {deal['deal_id']}: {deal['failure_rate']:.2f}")
        
        # Save result details to JSON
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Simulation result saved to: {args.output}")
    
    elif args.command == "alternatives":
        # Load hypergraph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimizer
        optimizer = O3Optimizer(graph)
        
        # Generate alternatives
        alternatives = optimizer.generate_alternative_roadmaps(
            entity_ids=args.entities,
            num_alternatives=args.count
        )
        
        # Add alternatives to graph
        for roadmap in alternatives:
            graph.add_roadmap(roadmap)
        
        # Print alternatives summary
        print(f"Generated {len(alternatives)} alternative roadmaps:")
        for i, roadmap in enumerate(alternatives):
            objective = roadmap.objectives.get('primary_objective', 'unknown')
            deals = len(roadmap.deals)
            print(f"  {i+1}. {roadmap.name}: {deals} deals, objective: {objective}")
        
        # Save updated graph if requested
        if args.output:
            graph.save_to_file(args.output)
            print(f"Updated graph saved to: {args.output}")
    
    elif args.command == "implement":
        # Load hypergraph
        graph = DealHypergraph.load_from_file(args.graph)
        
        # Create optimizer
        optimizer = O3Optimizer(graph)
        
        # Implement roadmap
        result = optimizer.implement_roadmap(args.roadmap_id)
        
        # Print implementation summary
        print(f"Roadmap: {args.roadmap_id}")
        print(f"Deals added: {len(result['deals_added'])}")
        print(f"Deals optimized: {len(result['deals_optimized'])}")
        print(f"Total value added: {result['total_value_added']:.2f}")
        
        # Save updated graph
        graph.save_to_file(args.output)
        print(f"Updated graph saved to: {args.output}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()