"""
API module for the FEMA implementation of the Adaptive Surveillance and Response System.

This module provides the FastAPI application that integrates the FEMA system supervisor
and exposes API endpoints for the FEMA implementation of the system.
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from .fema_supervisor import FEMASupervisor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="FEMA Adaptive Surveillance and Response System",
    description="API for disaster risk monitoring, resource deployment optimization, and recovery progress tracking",
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

# Create supervisor instance
supervisor = FEMASupervisor()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning system info."""
    return {
        "system": "FEMA Adaptive Surveillance and Response System",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint returning status of system components."""
    return supervisor.get_system_status()

# Workflow orchestration endpoints
@app.post("/api/v1/workflows/disaster-impact-prediction")
async def orchestrate_disaster_impact_prediction(params: Dict[str, Any]):
    """Orchestrate a disaster impact prediction workflow."""
    try:
        result = await supervisor.orchestrate_workflow("disaster_impact_prediction", params)
        return result
    except Exception as e:
        logger.error(f"Error orchestrating disaster impact prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.post("/api/v1/workflows/resource-deployment-planning")
async def orchestrate_resource_deployment_planning(params: Dict[str, Any]):
    """Orchestrate a resource deployment planning workflow."""
    try:
        result = await supervisor.orchestrate_workflow("resource_deployment_planning", params)
        return result
    except Exception as e:
        logger.error(f"Error orchestrating resource deployment planning: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.post("/api/v1/workflows/recovery-effectiveness-assessment")
async def orchestrate_recovery_effectiveness_assessment(params: Dict[str, Any]):
    """Orchestrate a recovery effectiveness assessment workflow."""
    try:
        result = await supervisor.orchestrate_workflow("recovery_effectiveness_assessment", params)
        return result
    except Exception as e:
        logger.error(f"Error orchestrating recovery effectiveness assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

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
    logger.info("FEMA Adaptive Surveillance and Response System API starting up")
    
    # Initialize the supervisor
    await supervisor.start()
    
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Executed when the application shuts down."""
    logger.info("FEMA Adaptive Surveillance and Response System API shutting down")
    
    # Shut down the supervisor
    await supervisor.stop()
    
    logger.info("API shutdown complete")