"""
Base Genetic Agent for Economic Theorem Proving

This module defines the base genetic agent structure for theorem proving,
using principles from DeepSeek-Prover-V2 and genetic algorithms.
"""

from typing import Dict, List, Tuple, Any, Optional, Set, Union
import json
import numpy as np
import uuid
from dataclasses import dataclass, field
from enum import Enum
import time
import random


class GeneticTraits(Enum):
    """Traits that define a genetic agent's theorem proving capabilities."""
    DECOMPOSITION_DEPTH = "decomposition_depth"  # How deeply to break down theorems
    PROOF_METHOD_PREFERENCE = "proof_method_preference"  # Preference for different proof methods
    FORMAL_STRICTNESS = "formal_strictness"  # How strictly to adhere to formal methods
    COUNTEREXAMPLE_GENERATION = "counterexample_generation"  # Ability to generate counterexamples
    ECONOMIC_DOMAIN_KNOWLEDGE = "economic_domain_knowledge"  # Depth of economic knowledge
    AXIOM_SELECTION = "axiom_selection"  # Ability to select relevant axioms
    RESOURCE_ALLOCATION = "resource_allocation"  # How to allocate computational resources
    PROOF_TERM_REUSE = "proof_term_reuse"  # Tendency to reuse existing proof terms
    PROOF_LENGTH_PREFERENCE = "proof_length_preference"  # Preference for longer or shorter proofs
    VERIFICATION_THOROUGHNESS = "verification_thoroughness"  # How thoroughly to verify proofs
    UNCERTAINTY_HANDLING = "uncertainty_handling"  # How to handle uncertain or ambiguous cases
    EXPLORATION_TENDENCY = "exploration_tendency"  # Tendency to explore novel approaches


@dataclass
class GenotypeGene:
    """A single gene in a genetic agent's genotype."""
    trait: GeneticTraits
    value: float  # Normalized between 0.0 and 1.0
    mutation_probability: float = 0.05
    
    def mutate(self, mutation_strength: float = 0.1) -> bool:
        """
        Potentially mutate this gene.
        
        Args:
            mutation_strength: Controls how much the gene can change (0.0-1.0)
            
        Returns:
            bool: Whether the gene was mutated
        """
        if random.random() < self.mutation_probability:
            # Apply mutation with random direction (positive or negative)
            change = random.uniform(-mutation_strength, mutation_strength)
            self.value = max(0.0, min(1.0, self.value + change))  # Clamp between 0.0 and 1.0
            return True
        return False


@dataclass
class Genotype:
    """The genetic makeup of a theorem-proving agent."""
    genes: Dict[GeneticTraits, GenotypeGene] = field(default_factory=dict)
    
    @classmethod
    def random(cls) -> 'Genotype':
        """Create a random genotype."""
        genotype = cls()
        for trait in GeneticTraits:
            genotype.genes[trait] = GenotypeGene(
                trait=trait,
                value=random.random(),  # Random value between 0.0 and 1.0
                mutation_probability=0.05 + random.random() * 0.1  # Variable mutation probability
            )
        return genotype
    
    @classmethod
    def from_parent(cls, parent: 'Genotype', mutation_rate: float = 0.1) -> 'Genotype':
        """Create a genotype from a parent with potential mutations."""
        child = cls()
        for trait, gene in parent.genes.items():
            child_gene = GenotypeGene(
                trait=trait,
                value=gene.value,
                mutation_probability=gene.mutation_probability
            )
            child_gene.mutate(mutation_rate)
            child.genes[trait] = child_gene
        return child
    
    @classmethod
    def crossover(cls, parent1: 'Genotype', parent2: 'Genotype', 
                 crossover_points: int = 2) -> Tuple['Genotype', 'Genotype']:
        """Perform crossover between two parent genotypes."""
        # Convert traits to list to ensure consistent ordering
        traits = list(GeneticTraits)
        
        # Select crossover points
        points = sorted(random.sample(range(1, len(traits)), crossover_points))
        
        # Create children
        child1 = cls()
        child2 = cls()
        
        # Track which parent to use for each segment
        use_parent1_for_child1 = True
        
        current_point = 0
        for i, trait in enumerate(traits):
            # Check if we've reached a crossover point
            if current_point < len(points) and i >= points[current_point]:
                current_point += 1
                use_parent1_for_child1 = not use_parent1_for_child1
            
            # Assign genes based on the current segment
            if use_parent1_for_child1:
                child1.genes[trait] = GenotypeGene(
                    trait=trait,
                    value=parent1.genes[trait].value,
                    mutation_probability=parent1.genes[trait].mutation_probability
                )
                child2.genes[trait] = GenotypeGene(
                    trait=trait,
                    value=parent2.genes[trait].value,
                    mutation_probability=parent2.genes[trait].mutation_probability
                )
            else:
                child1.genes[trait] = GenotypeGene(
                    trait=trait,
                    value=parent2.genes[trait].value,
                    mutation_probability=parent2.genes[trait].mutation_probability
                )
                child2.genes[trait] = GenotypeGene(
                    trait=trait,
                    value=parent1.genes[trait].value,
                    mutation_probability=parent1.genes[trait].mutation_probability
                )
        
        return child1, child2
    
    def get_trait_value(self, trait: GeneticTraits) -> float:
        """Get the value of a specific trait."""
        return self.genes[trait].value if trait in self.genes else 0.5  # Default to middle value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert genotype to dictionary for serialization."""
        return {
            "genes": {
                trait.value: {
                    "value": gene.value,
                    "mutation_probability": gene.mutation_probability
                } for trait, gene in self.genes.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Genotype':
        """Create a genotype from a dictionary."""
        genotype = cls()
        for trait_str, gene_data in data["genes"].items():
            trait = GeneticTraits(trait_str)
            genotype.genes[trait] = GenotypeGene(
                trait=trait,
                value=gene_data["value"],
                mutation_probability=gene_data["mutation_probability"]
            )
        return genotype


@dataclass
class ProofAttempt:
    """Represents a single proof attempt by a genetic agent."""
    theorem_id: str
    steps: List[Dict[str, Any]]
    success: bool
    resources_used: Dict[str, float]  # Computational resources used
    time_taken: float
    verification_result: Optional[Dict[str, Any]] = None
    
    def calculate_efficiency(self) -> float:
        """Calculate the efficiency of this proof attempt (higher is better)."""
        if not self.success:
            return 0.0
        
        # Calculate based on steps count (fewer is better) and time taken (less is better)
        step_efficiency = 1.0 / (1.0 + len(self.steps) / 10.0)  # Normalize for typical proof sizes
        time_efficiency = 1.0 / (1.0 + self.time_taken / 5.0)  # Normalize for typical proof times
        
        # Weight step efficiency higher for successful proofs
        return 0.7 * step_efficiency + 0.3 * time_efficiency


class GeneticTheoremProverAgent:
    """Base class for genetic agents specialized in theorem proving."""
    
    def __init__(self, 
                 agent_id: Optional[str] = None,
                 genotype: Optional[Genotype] = None, 
                 specialization: Optional[str] = None):
        """
        Initialize a genetic theorem prover agent.
        
        Args:
            agent_id: Unique identifier for this agent. Generated if not provided.
            genotype: The genetic makeup of the agent. Random if not provided.
            specialization: Optional specialization area for this agent.
        """
        self.agent_id = agent_id or f"gtp_{uuid.uuid4().hex[:8]}"
        self.genotype = genotype or Genotype.random()
        self.specialization = specialization
        self.fitness_history = []
        self.proof_attempts = []
        self.proof_successes = 0
        self.creation_time = time.time()
        self.generation = 0
        self.parent_ids = []
    
    def prove_theorem(self, theorem_spec: Dict[str, Any]) -> ProofAttempt:
        """
        Attempt to prove a theorem based on the agent's genetic traits.
        
        Args:
            theorem_spec: The theorem specification to prove.
            
        Returns:
            A proof attempt containing the result and steps taken.
        """
        start_time = time.time()
        
        # This is a placeholder implementation. Subclasses should override this.
        # In a real implementation, this would:
        # 1. Apply the agent's genetic traits to guide the proof approach
        # 2. Use DeepSeek-Prover-V2 with appropriate parameters
        # 3. Track and return the results
        
        # Placeholder implementation
        decomposition_depth = self.genotype.get_trait_value(GeneticTraits.DECOMPOSITION_DEPTH)
        formal_strictness = self.genotype.get_trait_value(GeneticTraits.FORMAL_STRICTNESS)
        
        # Simulate proof steps (would be generated by DeepSeek-Prover-V2 in reality)
        steps = [
            {"step": 1, "description": "Initial formalization", "result": "Formalized theorem"},
            {"step": 2, "description": "Applied relevant axioms", "result": "Intermediate result"},
            {"step": 3, "description": "Completed proof by induction", "result": "Theorem proved"}
        ]
        
        # Simulate success or failure (would be determined by actual proof results)
        # Higher formal strictness and appropriate decomposition make success more likely
        success_probability = 0.3 + 0.4 * formal_strictness + 0.3 * (1.0 - abs(0.5 - decomposition_depth))
        success = random.random() < success_probability
        
        # Calculate resources used
        resources_used = {
            "memory": 100 + 200 * decomposition_depth,  # MB
            "computation": 50 + 100 * formal_strictness  # Arbitrary units
        }
        
        end_time = time.time()
        time_taken = end_time - start_time
        
        # Create and store the proof attempt
        attempt = ProofAttempt(
            theorem_id=theorem_spec["theorem_id"],
            steps=steps,
            success=success,
            resources_used=resources_used,
            time_taken=time_taken
        )
        
        self.proof_attempts.append(attempt)
        if success:
            self.proof_successes += 1
            
        return attempt
    
    def calculate_fitness(self) -> float:
        """
        Calculate this agent's fitness based on proof performance.
        
        Returns:
            A fitness score between 0.0 and 1.0 (higher is better).
        """
        if not self.proof_attempts:
            return 0.0
        
        # Calculate success rate
        success_rate = self.proof_successes / len(self.proof_attempts)
        
        # Calculate average efficiency of successful proofs
        successful_attempts = [a for a in self.proof_attempts if a.success]
        avg_efficiency = sum(a.calculate_efficiency() for a in successful_attempts) / len(successful_attempts) if successful_attempts else 0.0
        
        # Calculate resource efficiency (lower resource usage is better)
        if self.proof_attempts:
            total_memory = sum(a.resources_used.get("memory", 0) for a in self.proof_attempts)
            total_computation = sum(a.resources_used.get("computation", 0) for a in self.proof_attempts)
            avg_memory = total_memory / len(self.proof_attempts)
            avg_computation = total_computation / len(self.proof_attempts)
            
            # Normalize resource usage (lower is better)
            memory_efficiency = 1.0 / (1.0 + avg_memory / 500.0)  # Assuming 500MB is a reasonable baseline
            computation_efficiency = 1.0 / (1.0 + avg_computation / 100.0)  # Arbitrary baseline
            resource_efficiency = 0.5 * memory_efficiency + 0.5 * computation_efficiency
        else:
            resource_efficiency = 0.0
        
        # Combine metrics with appropriate weights
        # Success rate is most important, followed by efficiency, then resource usage
        fitness = 0.6 * success_rate + 0.3 * avg_efficiency + 0.1 * resource_efficiency
        
        # Store fitness history
        self.fitness_history.append((time.time(), fitness))
        
        return fitness
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "genotype": self.genotype.to_dict(),
            "fitness_history": [(timestamp, fitness) for timestamp, fitness in self.fitness_history],
            "proof_successes": self.proof_successes,
            "total_attempts": len(self.proof_attempts),
            "creation_time": self.creation_time,
            "generation": self.generation,
            "parent_ids": self.parent_ids
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneticTheoremProverAgent':
        """Create an agent from a dictionary."""
        agent = cls(
            agent_id=data["agent_id"],
            genotype=Genotype.from_dict(data["genotype"]),
            specialization=data.get("specialization")
        )
        
        agent.fitness_history = [(timestamp, fitness) for timestamp, fitness in data["fitness_history"]]
        agent.proof_successes = data["proof_successes"]
        agent.proof_attempts = []  # Proof attempts aren't stored in the dictionary for efficiency
        agent.creation_time = data["creation_time"]
        agent.generation = data["generation"]
        agent.parent_ids = data["parent_ids"]
        
        return agent


# Utility function for creating new generation of agents
def create_new_generation(agents: List[GeneticTheoremProverAgent], 
                          population_size: int,
                          elite_percentage: float = 0.1,
                          mutation_rate: float = 0.1) -> List[GeneticTheoremProverAgent]:
    """
    Create a new generation of agents through selection, crossover, and mutation.
    
    Args:
        agents: Current generation of agents
        population_size: Size of the new generation
        elite_percentage: Percentage of top agents to preserve unchanged
        mutation_rate: Rate of mutation in new agents
        
    Returns:
        A new generation of agents
    """
    # Calculate fitness for all agents
    for agent in agents:
        if not agent.fitness_history or time.time() - agent.fitness_history[-1][0] > 60:  # Recalculate if older than 1 minute
            agent.calculate_fitness()
    
    # Sort agents by fitness
    sorted_agents = sorted(agents, key=lambda a: a.fitness_history[-1][1] if a.fitness_history else 0.0, reverse=True)
    
    # Determine elite count
    elite_count = max(1, int(population_size * elite_percentage))
    
    # Create new generation
    new_generation = []
    
    # Add elites unchanged
    for i in range(elite_count):
        if i < len(sorted_agents):
            elite = sorted_agents[i]
            new_generation.append(elite)  # Keep elite unchanged
    
    # Fill remaining population through crossover and mutation
    while len(new_generation) < population_size:
        # Tournament selection
        parent1 = tournament_selection(sorted_agents)
        parent2 = tournament_selection(sorted_agents)
        
        # Crossover
        child1_genotype, child2_genotype = Genotype.crossover(parent1.genotype, parent2.genotype)
        
        # Create children
        child1 = GeneticTheoremProverAgent(
            genotype=child1_genotype,
            specialization=parent1.specialization  # Inherit specialization from parent
        )
        child1.generation = max(parent1.generation, parent2.generation) + 1
        child1.parent_ids = [parent1.agent_id, parent2.agent_id]
        
        child2 = GeneticTheoremProverAgent(
            genotype=child2_genotype,
            specialization=parent2.specialization  # Inherit specialization from parent
        )
        child2.generation = max(parent1.generation, parent2.generation) + 1
        child2.parent_ids = [parent1.agent_id, parent2.agent_id]
        
        new_generation.append(child1)
        if len(new_generation) < population_size:
            new_generation.append(child2)
    
    return new_generation


def tournament_selection(agents: List[GeneticTheoremProverAgent], tournament_size: int = 3) -> GeneticTheoremProverAgent:
    """
    Select an agent using tournament selection.
    
    Args:
        agents: List of agents to select from
        tournament_size: Number of agents in each tournament
        
    Returns:
        The selected agent
    """
    if not agents:
        raise ValueError("Cannot perform tournament selection on empty list")
    
    # Randomly select agents for the tournament
    tournament = random.sample(agents, min(tournament_size, len(agents)))
    
    # Select the best from the tournament
    return max(tournament, key=lambda a: a.fitness_history[-1][1] if a.fitness_history else 0.0)