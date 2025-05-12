"""
Cached Genetic Recursive Adapter

This module extends the genetic adapter with caching capabilities
for improved performance.
"""

import os
import time
import json
import logging
from typing import Dict, List, Any, Optional
from .genetic_adapter import GeneticRecursiveAdapter
from .enhanced_recursive_thinking_cached import CachedRecursiveThinkingChat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("cached_genetic_adapter")

class CachedGeneticRecursiveAdapter(GeneticRecursiveAdapter):
    """
    Extends GeneticRecursiveAdapter with caching capabilities for improved performance.
    """
    
    def __init__(
        self, 
        api_key: str = None, 
        genetic_engine_path: str = None,
        cache_size: int = 1000,
        cache_ttl: int = 3600,
        cache_path: Optional[str] = None,
        cache_verbose: bool = False
    ):
        """
        Initialize the cached adapter.
        
        Args:
            api_key: OpenRouter API key for recursive thinking
            genetic_engine_path: Path to the genetic engine executable or script
            cache_size: Maximum number of items in the cache
            cache_ttl: Time-to-live for cache entries in seconds
            cache_path: Path to persist the cache (optional)
            cache_verbose: Enable verbose logging for cache operations
        """
        # Use cached recursive thinking
        self.recursive_thinking = CachedRecursiveThinkingChat(
            api_key=api_key,
            cache_size=cache_size,
            cache_ttl=cache_ttl,
            cache_path=cache_path,
            cache_verbose=cache_verbose
        )
        
        # Set genetic engine path
        self.genetic_engine_path = genetic_engine_path or "genetic_repair_engine"
        
        # Set up metrics
        self.metrics = {
            "hybrid_evolutions": 0,
            "genetic_calls": 0,
            "recursive_calls": 0,
            "total_time": 0
        }
        
        logger.info(f"Initialized cached genetic adapter with recursive thinking caching")
    
    def hybrid_evolve(
        self,
        candidates: List[str],
        constraints: List[Dict],
        fitness_function: str,
        recursion_rounds: int = 1,
        verbose: bool = True
    ) -> Dict:
        """
        Evolve solutions using both genetic algorithms and recursive thinking with caching.
        
        Args:
            candidates: Initial candidate solutions
            constraints: Constraints for the genetic algorithm
            fitness_function: The fitness function to use
            recursion_rounds: Number of hybrid rounds to perform
            verbose: Whether to print intermediate results
            
        Returns:
            A dictionary containing the final solution and metadata
        """
        start_time = time.time()
        self.metrics["hybrid_evolutions"] += 1
        
        # Run the hybrid evolution
        result = super().hybrid_evolve(
            candidates,
            constraints,
            fitness_function,
            recursion_rounds,
            verbose
        )
        
        elapsed_time = time.time() - start_time
        self.metrics["total_time"] += elapsed_time
        
        if verbose:
            logger.info(f"Hybrid evolution completed in {elapsed_time:.2f}s")
            
            # Show cache metrics
            thinking_metrics = self.recursive_thinking.get_metrics()
            logger.info(f"Thinking cache stats: {thinking_metrics['cache_hits']} hits, {thinking_metrics['cache_misses']} misses, {thinking_metrics['total_time_saved']:.2f}s saved")
        
        return result
    
    def _call_genetic_engine(self, candidates: List[str], constraints: List[Dict], fitness_function: str) -> Dict:
        """
        Call the genetic repair engine with metrics tracking.
        
        Args:
            candidates: List of candidate solutions
            constraints: List of constraints
            fitness_function: The fitness function to use
            
        Returns:
            The genetic engine results
        """
        self.metrics["genetic_calls"] += 1
        start_time = time.time()
        
        result = super()._call_genetic_engine(candidates, constraints, fitness_function)
        
        elapsed_time = time.time() - start_time
        if verbose:
            logger.debug(f"Genetic engine call completed in {elapsed_time:.2f}s")
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Dictionary with metrics
        """
        # Get recursive thinking metrics
        thinking_metrics = self.recursive_thinking.get_metrics()
        
        return {
            "hybrid_evolutions": self.metrics["hybrid_evolutions"],
            "genetic_calls": self.metrics["genetic_calls"],
            "recursive_calls": thinking_metrics["api_calls"],
            "total_time": self.metrics["total_time"],
            "thinking_cache": thinking_metrics
        }
    
    def clear_cache(self) -> None:
        """Clear the thinking cache."""
        self.recursive_thinking.clear_cache()
        logger.info("Thinking cache cleared")
    
    def clean_cache(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        return self.recursive_thinking.clean_cache()