"""
Rate limiting middleware for standardized API request throttling.

This module provides consistent rate limiting across all agency API
implementations to prevent abuse and ensure fair resource allocation.
"""

import time
from typing import Dict, Optional, Callable
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import logging


# Configure logging
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter for API request throttling.
    
    This class implements a sliding window rate limiting algorithm
    to restrict the number of requests per client over a time period.
    """
    
    def __init__(self, limit: int = 60, window: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            limit: Maximum number of requests allowed per window
            window: Time window in seconds (default: 60)
        """
        self.limit = limit
        self.window = window
        self.clients: Dict[str, Dict[str, float]] = {}
    
    def is_allowed(self, client_id: str) -> tuple[bool, int, int]:
        """
        Check if a request is allowed for a client.
        
        Args:
            client_id: Client identifier (IP address, API key, etc.)
            
        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        # Get current time
        now = time.time()
        
        # Get or create client record
        if client_id not in self.clients:
            self.clients[client_id] = {'requests': [], 'last_reset': now}
        
        client = self.clients[client_id]
        
        # Remove expired timestamps
        client['requests'] = [ts for ts in client['requests'] if now - ts < self.window]
        
        # Check if limit is reached
        request_count = len(client['requests'])
        allowed = request_count < self.limit
        
        # Add current timestamp if allowed
        if allowed:
            client['requests'].append(now)
        
        # Calculate reset time
        if request_count > 0:
            oldest_timestamp = min(client['requests']) if client['requests'] else now
            reset_time = int(oldest_timestamp + self.window - now)
        else:
            reset_time = 0
        
        return allowed, self.limit - len(client['requests']), reset_time
    
    def clean_up(self):
        """Remove old client records to prevent memory leaks."""
        now = time.time()
        expired_clients = []
        
        for client_id, client in self.clients.items():
            if now - max(client['requests']) if client['requests'] else 0 > self.window * 2:
                expired_clients.append(client_id)
        
        for client_id in expired_clients:
            del self.clients[client_id]


class RateLimitingMiddleware:
    """
    Middleware for API rate limiting.
    
    This class adds rate limiting to a FastAPI application,
    controlling the number of requests allowed per client.
    """
    
    def __init__(
        self,
        app: FastAPI,
        limit: int = 60,
        window: int = 60,
        client_id_func: Optional[Callable[[Request], str]] = None,
        key_prefix: str = "global",
        exclude_paths: list[str] = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            limit: Maximum number of requests allowed per window
            window: Time window in seconds (default: 60)
            client_id_func: Function to extract client ID from request
            key_prefix: Prefix for rate limit keys
            exclude_paths: List of paths to exclude from rate limiting
        """
        self.app = app
        self.limiter = RateLimiter(limit, window)
        self.client_id_func = client_id_func or self._default_client_id
        self.key_prefix = key_prefix
        self.exclude_paths = exclude_paths or []
        
        # Register middleware
        @app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            # Skip rate limiting for excluded paths
            if any(request.url.path.startswith(path) for path in self.exclude_paths):
                return await call_next(request)
            
            # Get client ID
            client_id = self.client_id_func(request)
            rate_limit_key = f"{self.key_prefix}:{client_id}"
            
            # Check rate limit
            allowed, remaining, reset = self.limiter.is_allowed(rate_limit_key)
            
            # If not allowed, return 429 response
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "status": "error",
                        "message": "Rate limit exceeded",
                        "detail": f"Too many requests. Please try again in {reset} seconds."
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.limiter.limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset),
                        "Retry-After": str(reset)
                    }
                )
            
            # Process the request
            response = await call_next(request)
            
            # Add rate limit headers to the response
            response.headers["X-RateLimit-Limit"] = str(self.limiter.limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset)
            
            return response
    
    @staticmethod
    def _default_client_id(request: Request) -> str:
        """
        Extract client ID from request using client IP.
        
        Args:
            request: FastAPI request
            
        Returns:
            Client ID string
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get the first IP in the list
            client_ip = forwarded.split(",")[0].strip()
        else:
            # Get client IP from request
            client_ip = request.client.host if request.client else "unknown"
        
        return client_ip


def setup_rate_limiting(
    app: FastAPI,
    standard_limit: int = 60,
    intensive_limit: int = 10,
    window: int = 60,
    intensive_paths: list[str] = None
) -> None:
    """
    Set up rate limiting for a FastAPI application.
    
    Args:
        app: FastAPI application
        standard_limit: Standard rate limit
        intensive_limit: Rate limit for resource-intensive endpoints
        window: Time window in seconds
        intensive_paths: List of resource-intensive endpoint paths
    """
    # Set up standard rate limiting for all endpoints
    RateLimitingMiddleware(
        app, 
        limit=standard_limit, 
        window=window,
        key_prefix="standard",
        exclude_paths=intensive_paths or []
    )
    
    # Set up stricter rate limiting for resource-intensive endpoints
    if intensive_paths:
        intensive_exclude = [path for path in app.routes if not any(
            str(path).startswith(intensive_path) for intensive_path in intensive_paths
        )]
        
        RateLimitingMiddleware(
            app,
            limit=intensive_limit,
            window=window,
            key_prefix="intensive",
            exclude_paths=intensive_exclude
        )