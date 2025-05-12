"""
API module for the APHIS Bird Flu Tracking System.

This module provides the main FastAPI application that integrates
all controllers and exposes the API endpoints for the system.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime

from .controllers.predictive_controller import router as predictive_router
from .controllers.notification_controller import router as notification_router
from .controllers.visualization_controller import router as visualization_router
from .controllers.genetic_controller import router as genetic_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="APHIS Bird Flu Tracking System",
    description="API for avian influenza surveillance and predictive modeling",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictive_router)
app.include_router(notification_router)
app.include_router(visualization_router)
app.include_router(genetic_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning system info."""
    return {
        "system": "APHIS Bird Flu Tracking System",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "database": "operational",
            "predictive_models": "operational",
            "notification_services": "operational",
            "genetic_analysis": "operational"
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler for general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Executed when the application starts."""
    logger.info("APHIS Bird Flu Tracking System API starting up")
    
    # Initialize components that need setup
    # This would include database connections, loading models, etc.
    
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Executed when the application shuts down."""
    logger.info("APHIS Bird Flu Tracking System API shutting down")
    
    # Clean up resources
    # This would include closing database connections, etc.
    
    logger.info("API shutdown complete")