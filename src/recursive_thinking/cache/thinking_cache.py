"""
Thinking Cache

Implements an LRU cache for recursive thinking results to improve performance
by avoiding redundant thinking operations.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("thinking_cache")

class ThinkingCache:
    """LRU cache for recursive thinking results."""
    
    def __init__(
        self, 
        max_size: int = 1000, 
        ttl: int = 3600, 
        persist_path: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize the thinking cache.
        
        Args:
            max_size: Maximum number of items in the cache
            ttl: Time-to-live for cache entries in seconds
            persist_path: Path to persist the cache (optional)
            verbose: Enable verbose logging
        """
        self.max_size = max_size
        self.ttl = ttl
        self.persist_path = persist_path
        self.verbose = verbose
        
        # Cache storage as OrderedDict for LRU functionality
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        
        # Set logging level
        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
        # Load persisted cache if available
        if persist_path and os.path.exists(persist_path):
            self._load_cache()
    
    def _generate_key(self, input_text: str, constraints: List[Dict] = None) -> str:
        """
        Generate a cache key for the input text and constraints.
        
        Args:
            input_text: Input text to generate a key for
            constraints: Optional constraints that affect the result
            
        Returns:
            Cache key as a string
        """
        # Create a string representation of constraints
        constraints_str = ""
        if constraints:
            # Sort constraints to ensure consistent order
            sorted_constraints = sorted(constraints, key=lambda x: (x.get('type', ''), str(x.get('value', ''))))
            constraints_str = json.dumps(sorted_constraints)
        
        # Combine input and constraints
        combined = f"{input_text}|{constraints_str}"
        
        # Generate hash
        key = hashlib.md5(combined.encode('utf-8')).hexdigest()
        
        if self.verbose:
            logger.debug(f"Generated cache key: {key} for input length {len(input_text)} chars")
        
        return key
    
    def get(self, input_text: str, constraints: List[Dict] = None) -> Optional[Any]:
        """
        Get a result from the cache.
        
        Args:
            input_text: Input text to look up
            constraints: Optional constraints that affect the result
            
        Returns:
            Cached result or None if not found
        """
        key = self._generate_key(input_text, constraints)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            
            # Check if the entry has expired
            if time.time() - timestamp > self.ttl:
                # Remove expired entry
                del self.cache[key]
                if self.verbose:
                    logger.debug(f"Cache miss (expired): {key}")
                return None
            
            # Move to the end (most recently used)
            self.cache.move_to_end(key)
            
            if self.verbose:
                logger.debug(f"Cache hit: {key}")
            
            return result
        
        if self.verbose:
            logger.debug(f"Cache miss: {key}")
        
        return None
    
    def put(self, input_text: str, result: Any, constraints: List[Dict] = None) -> None:
        """
        Put a result in the cache.
        
        Args:
            input_text: Input text to cache
            result: Result to cache
            constraints: Optional constraints that affect the result
        """
        key = self._generate_key(input_text, constraints)
        
        # Check if we need to evict to maintain max size
        if len(self.cache) >= self.max_size:
            # Remove the least recently used item (first item in OrderedDict)
            self.cache.popitem(last=False)
        
        # Store result with timestamp
        self.cache[key] = (result, time.time())
        
        if self.verbose:
            logger.debug(f"Cache put: {key}")
        
        # Persist cache if path is specified
        if self.persist_path:
            self._persist_cache()
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        logger.info("Cache cleared")
        
        # Remove persisted cache if it exists
        if self.persist_path and os.path.exists(self.persist_path):
            try:
                os.remove(self.persist_path)
                logger.info(f"Removed persisted cache at {self.persist_path}")
            except Exception as e:
                logger.error(f"Failed to remove persisted cache: {str(e)}")
    
    def _persist_cache(self) -> None:
        """Persist the cache to disk."""
        if not self.persist_path:
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            
            # Convert cache to serializable format
            serializable_cache = {}
            for key, (result, timestamp) in self.cache.items():
                serializable_cache[key] = {
                    "result": result,
                    "timestamp": timestamp
                }
            
            # Write to file
            with open(self.persist_path, 'w') as f:
                json.dump(serializable_cache, f)
            
            if self.verbose:
                logger.debug(f"Cache persisted to {self.persist_path}")
        except Exception as e:
            logger.error(f"Failed to persist cache: {str(e)}")
    
    def _load_cache(self) -> None:
        """Load the cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return
        
        try:
            # Read from file
            with open(self.persist_path, 'r') as f:
                serializable_cache = json.load(f)
            
            # Convert to cache format
            for key, entry in serializable_cache.items():
                self.cache[key] = (entry["result"], entry["timestamp"])
            
            # Enforce max size
            while len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
            
            if self.verbose:
                logger.debug(f"Cache loaded from {self.persist_path} with {len(self.cache)} entries")
        except Exception as e:
            logger.error(f"Failed to load cache: {str(e)}")
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        # Count expired entries
        now = time.time()
        expired = sum(1 for _, timestamp in self.cache.values() if now - timestamp > self.ttl)
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "expired": expired,
            "valid": len(self.cache) - expired,
            "persisted": self.persist_path is not None
        }
    
    def clean(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [key for key, (_, timestamp) in self.cache.items() if now - timestamp > self.ttl]
        
        for key in expired_keys:
            del self.cache[key]
        
        logger.info(f"Cleaned {len(expired_keys)} expired entries from cache")
        
        # Persist cache if path is specified
        if self.persist_path and expired_keys:
            self._persist_cache()
        
        return len(expired_keys)