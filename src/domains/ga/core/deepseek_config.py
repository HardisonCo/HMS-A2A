"""
DeepSeek-Prover-V2 Configuration

This module provides configuration management for the DeepSeek-Prover-V2 integration,
allowing genetic algorithms to tune parameters for optimal theorem proving.
"""

import os
import json
import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProverMode(Enum):
    """Operating modes for DeepSeek-Prover-V2."""
    DEFAULT = "default"  # Standard proving mode
    COT = "chain_of_thought"  # Chain of Thought mode for transparent reasoning
    NON_COT = "non_chain_of_thought"  # Non-Chain of Thought mode for efficiency
    DSP = "decomposition"  # Decomposition mode for breaking down complex proofs


class TacticStyle(Enum):
    """Tactic selection style for the prover."""
    STANDARD = "standard"  # Standard Lean tactics
    MATHLIB = "mathlib"  # Mathlib tactics library
    ECONOMIC = "economic"  # Economic-domain specific tactics
    ADAPTIVE = "adaptive"  # Adaptive tactics based on theorem structure


@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek-Prover-V2 that can be tuned by genetic algorithms."""
    
    # Core parameters
    mode: ProverMode = ProverMode.DEFAULT
    temperature: float = 0.1
    max_tokens: int = 4096
    subgoal_depth: int = 2
    timeout_seconds: int = 180
    
    # Advanced parameters
    tactic_style: TacticStyle = TacticStyle.STANDARD
    tactic_weights: Dict[str, float] = field(default_factory=lambda: {
        "simp": 1.0,
        "intro": 1.0,
        "apply": 1.0,
        "rewrite": 1.0,
        "exact": 1.0,
        "have": 1.0,
        "cases": 1.0,
        "induction": 1.0
    })
    
    # System parameters
    lean_lib_path: str = field(default_factory=lambda: os.environ.get('LEAN_LIB_PATH', './hms/lean_libs'))
    api_url: Optional[str] = field(default_factory=lambda: os.environ.get('DEEPSEEK_API_URL'))
    api_key: Optional[str] = field(default_factory=lambda: os.environ.get('DEEPSEEK_API_KEY'))
    model_path: Optional[str] = field(default_factory=lambda: os.environ.get('DEEPSEEK_MODEL_PATH'))
    
    # Theorem-specific parameters
    max_proof_steps: int = 50
    max_term_size: int = 1000
    max_decomposition_branches: int = 5
    
    # Genetic algorithm parameters
    fitness_history: List[float] = field(default_factory=list)
    mutation_count: int = 0
    generation: int = 0
    agent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary, handling enum values."""
        config_dict = asdict(self)
        # Convert enums to strings
        config_dict['mode'] = self.mode.value
        config_dict['tactic_style'] = self.tactic_style.value
        # Remove non-serializable fields
        config_dict.pop('fitness_history')
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DeepSeekConfig":
        """Create config from dictionary, handling enum values."""
        # Convert string values to enums
        if 'mode' in config_dict:
            config_dict['mode'] = ProverMode(config_dict['mode'])
        if 'tactic_style' in config_dict:
            config_dict['tactic_style'] = TacticStyle(config_dict['tactic_style'])
        
        return cls(**config_dict)
    
    def save(self, file_path: str) -> None:
        """Save configuration to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, file_path: str) -> "DeepSeekConfig":
        """Load configuration from a JSON file."""
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def mutate(self, mutation_rate: float = 0.1) -> "DeepSeekConfig":
        """
        Create a mutated copy of this configuration for genetic algorithm evolution.
        
        Args:
            mutation_rate: Probability of mutating each parameter
            
        Returns:
            Mutated configuration
        """
        import random
        
        # Create a copy of the current config
        mutated = DeepSeekConfig(**self.to_dict())
        
        # Increment mutation count
        mutated.mutation_count = self.mutation_count + 1
        
        # Copy fitness history
        mutated.fitness_history = self.fitness_history.copy()
        
        # Potentially mutate mode
        if random.random() < mutation_rate:
            mutated.mode = random.choice(list(ProverMode))
        
        # Potentially mutate temperature
        if random.random() < mutation_rate:
            # Temperature between 0.05 and 0.5
            mutated.temperature = random.uniform(0.05, 0.5)
        
        # Potentially mutate max_tokens
        if random.random() < mutation_rate:
            # Max tokens between 2048 and 8192, in steps of 512
            mutated.max_tokens = random.choice([2048, 2560, 3072, 3584, 4096, 4608, 5120, 5632, 6144, 6656, 7168, 7680, 8192])
        
        # Potentially mutate subgoal_depth
        if random.random() < mutation_rate:
            # Subgoal depth between 1 and 5
            mutated.subgoal_depth = random.randint(1, 5)
        
        # Potentially mutate timeout_seconds
        if random.random() < mutation_rate:
            # Timeout between 60 and 600 seconds
            mutated.timeout_seconds = random.randint(60, 600)
        
        # Potentially mutate tactic_style
        if random.random() < mutation_rate:
            mutated.tactic_style = random.choice(list(TacticStyle))
        
        # Potentially mutate tactic_weights
        if random.random() < mutation_rate:
            # Choose a random tactic to mutate
            tactic = random.choice(list(mutated.tactic_weights.keys()))
            # Adjust its weight by a random factor between 0.5 and 2.0
            adjustment = random.uniform(0.5, 2.0)
            mutated.tactic_weights[tactic] *= adjustment
            # Normalize weights so they sum to the same total
            total_weight = sum(mutated.tactic_weights.values())
            for tactic in mutated.tactic_weights:
                mutated.tactic_weights[tactic] /= total_weight
                mutated.tactic_weights[tactic] *= len(mutated.tactic_weights)
        
        # Potentially mutate max_proof_steps
        if random.random() < mutation_rate:
            # Max proof steps between 20 and 100
            mutated.max_proof_steps = random.randint(20, 100)
        
        # Potentially mutate max_term_size
        if random.random() < mutation_rate:
            # Max term size between 500 and 2000
            mutated.max_term_size = random.randint(500, 2000)
        
        # Potentially mutate max_decomposition_branches
        if random.random() < mutation_rate:
            # Max decomposition branches between 3 and 10
            mutated.max_decomposition_branches = random.randint(3, 10)
        
        return mutated
    
    def crossover(self, other: "DeepSeekConfig") -> "DeepSeekConfig":
        """
        Create a new configuration by crossing over with another configuration.
        
        Args:
            other: Another configuration to cross over with
            
        Returns:
            New configuration created by crossover
        """
        import random
        
        # Create a new config with random selection of parameters from parents
        crossover_dict = {}
        self_dict = self.to_dict()
        other_dict = other.to_dict()
        
        # For each parameter, randomly choose from one parent
        for key in self_dict:
            if key in ['fitness_history', 'mutation_count', 'generation', 'agent_id']:
                continue
            if random.random() < 0.5:
                crossover_dict[key] = self_dict[key]
            else:
                crossover_dict[key] = other_dict[key]
        
        # Create new config
        crossed = DeepSeekConfig.from_dict(crossover_dict)
        
        # Set generation and mutation info
        crossed.generation = max(self.generation, other.generation) + 1
        crossed.mutation_count = 0
        
        return crossed
    
    def update_fitness(self, fitness: float) -> None:
        """
        Update fitness history with a new fitness value.
        
        Args:
            fitness: New fitness value
        """
        self.fitness_history.append(fitness)
    
    def get_avg_fitness(self) -> Optional[float]:
        """
        Get average fitness across history.
        
        Returns:
            Average fitness or None if no history
        """
        if not self.fitness_history:
            return None
        return sum(self.fitness_history) / len(self.fitness_history)
    
    def get_fitness_trend(self) -> Optional[float]:
        """
        Calculate fitness trend (positive means improving).
        
        Returns:
            Fitness trend or None if insufficient history
        """
        if len(self.fitness_history) < 2:
            return None
        
        # Simple trend: last value - first value
        return self.fitness_history[-1] - self.fitness_history[0]


# Default configurations for different theorem types
DEFAULT_CONFIGS = {
    "economic_simple": DeepSeekConfig(
        mode=ProverMode.DEFAULT,
        temperature=0.1,
        max_tokens=4096,
        subgoal_depth=1,
        timeout_seconds=120,
        tactic_style=TacticStyle.ECONOMIC
    ),
    "economic_complex": DeepSeekConfig(
        mode=ProverMode.DSP,
        temperature=0.2,
        max_tokens=6144,
        subgoal_depth=3,
        timeout_seconds=300,
        tactic_style=TacticStyle.ECONOMIC
    ),
    "decomposition": DeepSeekConfig(
        mode=ProverMode.DSP,
        temperature=0.1,
        max_tokens=8192,
        subgoal_depth=4,
        timeout_seconds=600,
        tactic_style=TacticStyle.ADAPTIVE
    ),
    "cot_explanation": DeepSeekConfig(
        mode=ProverMode.COT,
        temperature=0.3,
        max_tokens=8192,
        subgoal_depth=2,
        timeout_seconds=300,
        tactic_style=TacticStyle.MATHLIB
    )
}


def get_config_for_theorem(theorem_id: str, complexity: str = "simple") -> DeepSeekConfig:
    """
    Get an appropriate configuration for a given theorem.
    
    Args:
        theorem_id: ID of the theorem
        complexity: Complexity level (simple, complex)
        
    Returns:
        Configuration for the theorem
    """
    # Check for theorem-specific config
    if theorem_id.startswith("war_score"):
        return DEFAULT_CONFIGS["economic_simple"]
    elif theorem_id.startswith("drp"):
        return DEFAULT_CONFIGS["economic_simple"]
    elif theorem_id.startswith("sps"):
        return DEFAULT_CONFIGS["economic_simple"]
    elif "integrated" in theorem_id.lower() or "economic_analysis" in theorem_id.lower():
        return DEFAULT_CONFIGS["economic_complex"]
    elif complexity == "complex":
        return DEFAULT_CONFIGS["decomposition"]
    else:
        return DEFAULT_CONFIGS["economic_simple"]


def create_population(size: int = 10) -> List[DeepSeekConfig]:
    """
    Create a diverse initial population of configurations.
    
    Args:
        size: Population size
        
    Returns:
        List of configurations
    """
    population = []
    
    # Add default configurations
    for config in DEFAULT_CONFIGS.values():
        population.append(config)
    
    # Fill the rest with mutations of the defaults
    while len(population) < size:
        # Choose a random default config
        base_config = random.choice(list(DEFAULT_CONFIGS.values()))
        # Create a mutation
        mutated = base_config.mutate(mutation_rate=0.3)
        population.append(mutated)
    
    return population[:size]  # Ensure correct size


# Import at the end to avoid circular imports
import random