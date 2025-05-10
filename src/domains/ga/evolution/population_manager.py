"""
Population Manager for Genetic Theorem Proving Agents

This module manages populations of genetic agents for theorem proving,
handling selection, breeding, and evolution across generations.
"""

from typing import Dict, List, Tuple, Any, Optional, Set, Union, Callable
import json
import time
import random
import uuid
import os
from dataclasses import dataclass, field
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pickle

from ..core.base_agent import (
    GeneticTheoremProverAgent, 
    create_new_generation,
    GeneticTraits,
    Genotype
)


@dataclass
class PopulationStats:
    """Statistics about a population of genetic agents."""
    generation: int
    timestamp: float
    population_size: int
    avg_fitness: float
    max_fitness: float
    min_fitness: float
    median_fitness: float
    avg_success_rate: float
    avg_proof_attempts: float
    trait_distributions: Dict[GeneticTraits, Tuple[float, float]]  # (mean, std_dev)
    elite_agent_ids: List[str]


class PopulationManager:
    """
    Manages the evolution of a population of genetic theorem proving agents.
    """
    
    def __init__(self, 
                 population_size: int = 50,
                 elite_percentage: float = 0.1,
                 mutation_rate: float = 0.1,
                 crossover_points: int = 2,
                 specializations: Optional[List[str]] = None,
                 checkpoint_dir: Optional[str] = None,
                 metrics_callback: Optional[Callable[[PopulationStats], None]] = None):
        """
        Initialize a population manager.
        
        Args:
            population_size: Number of agents in the population
            elite_percentage: Percentage of top agents to preserve unchanged
            mutation_rate: Rate of mutation in new agents
            crossover_points: Number of crossover points in breeding
            specializations: Optional list of specializations to initialize agents with
            checkpoint_dir: Directory to save population checkpoints
            metrics_callback: Optional callback for population metrics
        """
        self.population_size = population_size
        self.elite_percentage = elite_percentage
        self.mutation_rate = mutation_rate
        self.crossover_points = crossover_points
        self.specializations = specializations
        self.checkpoint_dir = checkpoint_dir
        self.metrics_callback = metrics_callback
        
        # Create checkpoint directory if specified
        if checkpoint_dir:
            os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Initialize population
        self.agents = []
        self.generation = 0
        self.history = []
        
        # Create initial population
        self._initialize_population()
    
    def _initialize_population(self):
        """Initialize the population with random agents."""
        self.agents = []
        
        # Distribute specializations if provided
        if self.specializations:
            for i in range(self.population_size):
                specialization = self.specializations[i % len(self.specializations)]
                agent = GeneticTheoremProverAgent(specialization=specialization)
                self.agents.append(agent)
        else:
            # Create generic agents if no specializations
            for i in range(self.population_size):
                agent = GeneticTheoremProverAgent()
                self.agents.append(agent)
        
        # Set initial generation
        self.generation = 0
        
        # Save initial stats
        self._collect_stats()
    
    def evolve(self, num_generations: int = 1) -> List[GeneticTheoremProverAgent]:
        """
        Evolve the population for a specified number of generations.
        
        Args:
            num_generations: Number of generations to evolve
            
        Returns:
            List of elite agents from the final generation
        """
        for i in range(num_generations):
            # Create new generation
            self.agents = create_new_generation(
                self.agents,
                self.population_size,
                self.elite_percentage,
                self.mutation_rate
            )
            
            # Update generation counter
            self.generation += 1
            
            # Collect stats
            self._collect_stats()
            
            # Save checkpoint if directory is specified
            if self.checkpoint_dir and self.generation % 10 == 0:
                self.save_checkpoint()
        
        # Return the elite agents
        return self.get_elite_agents()
    
    def _collect_stats(self) -> PopulationStats:
        """Collect and store statistics about the current population."""
        # Calculate fitness for all agents that don't have it
        for agent in self.agents:
            if not agent.fitness_history:
                agent.calculate_fitness()
        
        # Extract fitness values
        fitnesses = [agent.fitness_history[-1][1] if agent.fitness_history else 0.0 
                     for agent in self.agents]
        
        # Calculate success rates and attempt counts
        success_rates = [agent.proof_successes / max(1, len(agent.proof_attempts)) 
                         for agent in self.agents]
        proof_attempts = [len(agent.proof_attempts) for agent in self.agents]
        
        # Calculate trait distributions
        trait_distributions = {}
        for trait in GeneticTraits:
            trait_values = [agent.genotype.get_trait_value(trait) for agent in self.agents]
            trait_distributions[trait] = (np.mean(trait_values), np.std(trait_values))
        
        # Identify elite agents
        sorted_agents = sorted(
            self.agents, 
            key=lambda a: a.fitness_history[-1][1] if a.fitness_history else 0.0, 
            reverse=True
        )
        elite_count = max(1, int(self.population_size * self.elite_percentage))
        elite_agent_ids = [agent.agent_id for agent in sorted_agents[:elite_count]]
        
        # Create stats object
        stats = PopulationStats(
            generation=self.generation,
            timestamp=time.time(),
            population_size=len(self.agents),
            avg_fitness=np.mean(fitnesses),
            max_fitness=np.max(fitnesses),
            min_fitness=np.min(fitnesses),
            median_fitness=np.median(fitnesses),
            avg_success_rate=np.mean(success_rates),
            avg_proof_attempts=np.mean(proof_attempts),
            trait_distributions=trait_distributions,
            elite_agent_ids=elite_agent_ids
        )
        
        # Append to history
        self.history.append(stats)
        
        # Call metrics callback if provided
        if self.metrics_callback:
            self.metrics_callback(stats)
        
        return stats
    
    def get_elite_agents(self, percentage: Optional[float] = None) -> List[GeneticTheoremProverAgent]:
        """
        Get the top-performing agents from the current population.
        
        Args:
            percentage: Percentage of top agents to return (uses elite_percentage if not specified)
            
        Returns:
            List of top-performing agents
        """
        # Calculate fitness for all agents that don't have it
        for agent in self.agents:
            if not agent.fitness_history:
                agent.calculate_fitness()
        
        # Sort agents by fitness
        sorted_agents = sorted(
            self.agents, 
            key=lambda a: a.fitness_history[-1][1] if a.fitness_history else 0.0, 
            reverse=True
        )
        
        # Determine elite count
        pct = percentage if percentage is not None else self.elite_percentage
        elite_count = max(1, int(len(sorted_agents) * pct))
        
        return sorted_agents[:elite_count]
    
    def get_agent_by_id(self, agent_id: str) -> Optional[GeneticTheoremProverAgent]:
        """Get an agent by its ID."""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
    
    def add_agent(self, agent: GeneticTheoremProverAgent) -> None:
        """Add an agent to the population."""
        self.agents.append(agent)
    
    def save_checkpoint(self, custom_path: Optional[str] = None) -> str:
        """
        Save the current population state to a checkpoint file.
        
        Args:
            custom_path: Optional custom path to save the checkpoint
            
        Returns:
            Path to the saved checkpoint file
        """
        if not self.checkpoint_dir and not custom_path:
            raise ValueError("Checkpoint directory not specified")
        
        # Prepare data
        checkpoint_data = {
            "generation": self.generation,
            "timestamp": time.time(),
            "population_size": self.population_size,
            "elite_percentage": self.elite_percentage,
            "mutation_rate": self.mutation_rate,
            "crossover_points": self.crossover_points,
            "specializations": self.specializations,
            "agents": [agent.to_dict() for agent in self.agents],
            "history": [
                {
                    "generation": stats.generation,
                    "timestamp": stats.timestamp,
                    "avg_fitness": stats.avg_fitness,
                    "max_fitness": stats.max_fitness,
                    "min_fitness": stats.min_fitness,
                    "avg_success_rate": stats.avg_success_rate
                }
                for stats in self.history
            ]
        }
        
        # Determine filename
        if custom_path:
            filepath = custom_path
        else:
            filename = f"pop_gen{self.generation:04d}_{int(time.time())}.pkl"
            filepath = os.path.join(self.checkpoint_dir, filename)
        
        # Save checkpoint
        with open(filepath, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        return filepath
    
    @classmethod
    def load_checkpoint(cls, filepath: str) -> 'PopulationManager':
        """
        Load a population manager from a checkpoint file.
        
        Args:
            filepath: Path to the checkpoint file
            
        Returns:
            Restored PopulationManager instance
        """
        # Load checkpoint data
        with open(filepath, 'rb') as f:
            checkpoint_data = pickle.load(f)
        
        # Create manager instance
        manager = cls(
            population_size=checkpoint_data["population_size"],
            elite_percentage=checkpoint_data["elite_percentage"],
            mutation_rate=checkpoint_data["mutation_rate"],
            crossover_points=checkpoint_data["crossover_points"],
            specializations=checkpoint_data["specializations"],
            checkpoint_dir=os.path.dirname(filepath)
        )
        
        # Restore agents
        manager.agents = [
            GeneticTheoremProverAgent.from_dict(agent_data)
            for agent_data in checkpoint_data["agents"]
        ]
        
        # Restore generation and history
        manager.generation = checkpoint_data["generation"]
        
        # We can't fully restore the complex history objects, but we've saved the key metrics
        manager._collect_stats()  # Create at least one history entry
        
        return manager
    
    def plot_fitness_history(self, save_path: Optional[str] = None) -> None:
        """
        Plot the fitness history of the population.
        
        Args:
            save_path: Optional path to save the plot image
        """
        if not self.history:
            print("No history to plot")
            return
        
        generations = [stats.generation for stats in self.history]
        avg_fitness = [stats.avg_fitness for stats in self.history]
        max_fitness = [stats.max_fitness for stats in self.history]
        min_fitness = [stats.min_fitness for stats in self.history]
        
        plt.figure(figsize=(10, 6))
        plt.plot(generations, avg_fitness, label='Average Fitness', color='blue')
        plt.plot(generations, max_fitness, label='Max Fitness', color='green')
        plt.plot(generations, min_fitness, label='Min Fitness', color='red')
        plt.fill_between(generations, min_fitness, max_fitness, alpha=0.2, color='gray')
        
        plt.title('Genetic Theorem Prover Population Fitness History')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_trait_distributions(self, save_dir: Optional[str] = None) -> None:
        """
        Plot the distribution of genetic traits in the population.
        
        Args:
            save_dir: Optional directory to save the plot images
        """
        if not self.agents:
            print("No agents to plot")
            return
        
        # Create save directory if specified
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        # Plot distribution for each trait
        for trait in GeneticTraits:
            trait_values = [agent.genotype.get_trait_value(trait) for agent in self.agents]
            
            plt.figure(figsize=(8, 5))
            plt.hist(trait_values, bins=20, alpha=0.7, color='blue')
            plt.title(f'Distribution of {trait.value} Trait')
            plt.xlabel('Trait Value')
            plt.ylabel('Count')
            plt.grid(True, linestyle='--', alpha=0.7)
            
            if save_dir:
                filename = f"trait_{trait.value}.png"
                filepath = os.path.join(save_dir, filename)
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
            else:
                plt.show()
    
    def get_population_summary(self) -> Dict[str, Any]:
        """Get a summary of the current population state."""
        if not self.history:
            self._collect_stats()
        
        latest_stats = self.history[-1]
        
        return {
            "generation": self.generation,
            "population_size": self.population_size,
            "avg_fitness": latest_stats.avg_fitness,
            "max_fitness": latest_stats.max_fitness,
            "avg_success_rate": latest_stats.avg_success_rate,
            "elite_agents": [
                {
                    "agent_id": agent.agent_id,
                    "specialization": agent.specialization,
                    "fitness": agent.fitness_history[-1][1] if agent.fitness_history else 0.0,
                    "success_rate": agent.proof_successes / max(1, len(agent.proof_attempts)),
                    "generation": agent.generation
                }
                for agent in self.get_elite_agents()
            ],
            "trait_trends": {
                trait.value: {
                    "current_mean": latest_stats.trait_distributions[trait][0],
                    "current_std": latest_stats.trait_distributions[trait][1]
                }
                for trait in GeneticTraits
            }
        }