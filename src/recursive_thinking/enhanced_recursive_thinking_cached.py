"""
Enhanced Recursive Thinking Chat with Caching

This module extends the EnhancedRecursiveThinkingChat class with caching capabilities
for improved performance.
"""

import os
import time
import json
import logging
from typing import Dict, List, Any, Optional
from .enhanced_recursive_thinking import EnhancedRecursiveThinkingChat
from .cache.thinking_cache import ThinkingCache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("recursive_thinking_cached")

class CachedRecursiveThinkingChat(EnhancedRecursiveThinkingChat):
    """
    Extended version of EnhancedRecursiveThinkingChat with caching capabilities
    for improved performance.
    """
    
    def __init__(
        self, 
        api_key: str = None, 
        model: str = "mistralai/mistral-small-3.1-24b-instruct:free",
        cache_size: int = 1000,
        cache_ttl: int = 3600,
        cache_path: Optional[str] = None,
        cache_verbose: bool = False
    ):
        """
        Initialize the cached recursive thinking chat.
        
        Args:
            api_key: OpenRouter API key (defaults to environment variable OPENROUTER_API_KEY)
            model: The model to use for thinking
            cache_size: Maximum number of items in the cache
            cache_ttl: Time-to-live for cache entries in seconds
            cache_path: Path to persist the cache (optional)
            cache_verbose: Enable verbose logging for cache operations
        """
        super().__init__(api_key=api_key, model=model)
        
        # Initialize cache
        self.cache = ThinkingCache(
            max_size=cache_size,
            ttl=cache_ttl,
            persist_path=cache_path,
            verbose=cache_verbose
        )
        
        # Set up metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "api_calls": 0,
            "total_time_saved": 0
        }
        
        logger.info(f"Initialized cached recursive thinking with {cache_size} max cache entries")
    
    def _call_api(self, messages: List[Dict[str, str]]) -> Dict:
        """Make an API call to OpenRouter with metrics tracking."""
        start_time = time.time()
        self.metrics["api_calls"] += 1
        
        response = super()._call_api(messages)
        
        elapsed_time = time.time() - start_time
        logger.debug(f"API call completed in {elapsed_time:.2f}s")
        
        return response
    
    def think_and_respond(self, user_input: str, verbose: bool = True) -> Dict:
        """
        Process user input with recursive thinking to generate an improved response.
        Uses caching to improve performance.
        
        Args:
            user_input: The problem or prompt from the user
            verbose: Whether to print intermediate thinking steps
            
        Returns:
            A dictionary containing the final response and thinking history
        """
        # Check if we have a cached result
        cached_result = self.cache.get(user_input)
        if cached_result:
            self.metrics["cache_hits"] += 1
            avg_time = sum(thought["time_taken"] for thought in cached_result["thinking_history"])
            self.metrics["total_time_saved"] += avg_time
            
            if verbose:
                logger.info(f"Using cached result for prompt. Saved {avg_time:.2f}s")
            
            # Use the cached thinking history
            self.thinking_history = cached_result["thinking_history"]
            
            return cached_result
        
        # No cache hit, perform thinking
        self.metrics["cache_misses"] += 1
        start_time = time.time()
        
        result = super().think_and_respond(user_input, verbose)
        
        elapsed_time = time.time() - start_time
        
        # Cache the result
        self.cache.put(user_input, result)
        
        if verbose:
            logger.info(f"Cached new result for prompt. Took {elapsed_time:.2f}s")
        
        return result
    
    def refine_solution(self, solution: str, constraints: List[Dict] = None, verbose: bool = True) -> str:
        """
        Refine a solution using recursive thinking with caching.
        
        Args:
            solution: The solution to refine
            constraints: Optional constraints to consider during refinement
            verbose: Whether to print intermediate thinking steps
            
        Returns:
            The refined solution as a string
        """
        # Generate a cache key based on the solution and constraints
        cached_result = self.cache.get(solution, constraints)
        if cached_result:
            self.metrics["cache_hits"] += 1
            
            # Estimate time saved based on thinking history
            if isinstance(cached_result, dict) and "thinking_history" in cached_result:
                avg_time = sum(thought["time_taken"] for thought in cached_result["thinking_history"])
                self.metrics["total_time_saved"] += avg_time
                if verbose:
                    logger.info(f"Using cached refinement. Saved {avg_time:.2f}s")
                return cached_result["final_response"]
            
            # Direct string result
            if verbose:
                logger.info(f"Using cached refinement result.")
            return cached_result
        
        # No cache hit, perform refinement
        self.metrics["cache_misses"] += 1
        start_time = time.time()
        
        result = super().refine_solution(solution, constraints, verbose)
        
        elapsed_time = time.time() - start_time
        
        # Cache the result
        self.cache.put(solution, result, constraints)
        
        if verbose:
            logger.info(f"Cached new refinement. Took {elapsed_time:.2f}s")
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Dictionary with metrics
        """
        hit_rate = 0
        if self.metrics["cache_hits"] + self.metrics["cache_misses"] > 0:
            hit_rate = self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
        
        return {
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "hit_rate": hit_rate,
            "api_calls": self.metrics["api_calls"],
            "total_time_saved": self.metrics["total_time_saved"],
            "cache_stats": self.cache.stats()
        }
    
    def clear_cache(self) -> None:
        """Clear the thinking cache."""
        self.cache.clear()
        logger.info("Thinking cache cleared")
    
    def clean_cache(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        return self.cache.clean()