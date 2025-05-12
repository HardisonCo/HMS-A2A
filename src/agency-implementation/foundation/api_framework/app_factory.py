"""
Application factory module for standardized FastAPI application creation.

This module provides a factory function for creating FastAPI applications
with consistent configuration and middleware across all agency implementations.
"""

from typing import Callable, Dict, List, Optional, Type
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .middleware.error_handling import setup_error_handling
from .middleware.rate_limiting import setup_rate_limiting


def create_app(
    title: str,
    description: str,
    version: str = "1.0.0",
    docs_url: str = "/docs",
    redoc_url: str = "/redoc",
    openapi_url: str = "/openapi.json",
    cors_origins: List[str] = None,
    rate_limit_standard: int = 60,
    rate_limit_intensive: int = 10,
    rate_limit_window: int = 60,
    intensive_paths: List[str] = None,
    middleware: List[Callable[[FastAPI], None]] = None,
    on_startup: List[Callable[[], None]] = None,
    on_shutdown: List[Callable[[], None]] = None,
    logger_name: str = None,
    log_level: int = logging.INFO
) -> FastAPI:
    """
    Create a standardized FastAPI application.
    
    Args:
        title: API title
        description: API description
        version: API version
        docs_url: Swagger UI URL
        redoc_url: ReDoc URL
        openapi_url: OpenAPI JSON URL
        cors_origins: List of allowed CORS origins
        rate_limit_standard: Standard rate limit
        rate_limit_intensive: Rate limit for intensive endpoints
        rate_limit_window: Rate limit window in seconds
        intensive_paths: List of intensive endpoint paths
        middleware: List of middleware setup functions
        on_startup: List of startup event handlers
        on_shutdown: List of shutdown event handlers
        logger_name: Logger name
        log_level: Logging level
        
    Returns:
        Configured FastAPI application
    """
    # Set up logging
    if logger_name:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        
        # Create console handler if none exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
    # Create FastAPI app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url
    )
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Set up error handling
    setup_error_handling(app)
    
    # Set up rate limiting
    setup_rate_limiting(
        app,
        standard_limit=rate_limit_standard,
        intensive_limit=rate_limit_intensive,
        window=rate_limit_window,
        intensive_paths=intensive_paths or []
    )
    
    # Add additional middleware
    if middleware:
        for mw_func in middleware:
            mw_func(app)
    
    # Add startup event handlers
    if on_startup:
        for handler in on_startup:
            app.add_event_handler("startup", handler)
    
    # Add default startup handler for logging
    @app.on_event("startup")
    async def startup_event():
        if logger_name:
            logger = logging.getLogger(logger_name)
            logger.info(f"Starting {title} API v{version}")
    
    # Add shutdown event handlers
    if on_shutdown:
        for handler in on_shutdown:
            app.add_event_handler("shutdown", handler)
    
    # Add default shutdown handler for logging
    @app.on_event("shutdown")
    async def shutdown_event():
        if logger_name:
            logger = logging.getLogger(logger_name)
            logger.info(f"Shutting down {title} API v{version}")
    
    # Add health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        import datetime
        return {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "api": title,
            "version": version
        }
    
    return app