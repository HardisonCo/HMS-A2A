"""
API module for the EPA implementation of the Adaptive Surveillance and Response System.

This module provides the FastAPI application that integrates the EPA system supervisor
and exposes API endpoints for the EPA implementation of the system.
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from .epa_supervisor import EPASupervisor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="EPA Adaptive Surveillance and Response System",
    description="API for environmental quality monitoring, compliance surveillance, and enforcement resource optimization",
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
supervisor = EPASupervisor()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning system info."""
    return {
        "system": "EPA Adaptive Surveillance and Response System",
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
@app.post("/api/v1/workflows/pollution-impact-assessment")
async def orchestrate_pollution_impact_assessment(params: Dict[str, Any]):
    """Orchestrate a pollution impact assessment workflow."""
    try:
        result = await supervisor.orchestrate_workflow("pollution_impact_assessment", params)
        return result
    except Exception as e:
        logger.error(f"Error orchestrating pollution impact assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.post("/api/v1/workflows/compliance-risk-analysis")
async def orchestrate_compliance_risk_analysis(params: Dict[str, Any]):
    """Orchestrate a compliance risk analysis workflow."""
    try:
        result = await supervisor.orchestrate_workflow("compliance_risk_analysis", params)
        return result
    except Exception as e:
        logger.error(f"Error orchestrating compliance risk analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.post("/api/v1/workflows/enforcement-resource-allocation")
async def orchestrate_enforcement_resource_allocation(params: Dict[str, Any]):
    """Orchestrate an enforcement resource allocation workflow."""
    try:
        result = await supervisor.orchestrate_workflow("enforcement_resource_allocation", params)
        return result
    except Exception as e:
        logger.error(f"Error orchestrating enforcement resource allocation: {str(e)}")
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
    logger.info("EPA Adaptive Surveillance and Response System API starting up")
    
    # Initialize the supervisor
    await supervisor.start()
    
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Executed when the application shuts down."""
    logger.info("EPA Adaptive Surveillance and Response System API shutting down")
    
    # Shut down the supervisor
    await supervisor.stop()
    
    logger.info("API shutdown complete")