#!/usr/bin/env python3
"""
HMS-AGX Main Entry Point for Crohn's Disease Treatment System

This module provides the main entry point for the HMS-AGX research component,
setting up the research agent and API server for external communication.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import uvicorn
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Path manipulation to import from a2a-integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../coordination/a2a-integration'))
from core import Agent, AgentRole, MessageType, AgentMessage

from research_agent import ResearchAgent, ResearchTopic, ResearchDepth
from agx_adapter import AGXAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hms-agx.main')

# Initialize the research agent and adapter
research_agent = None
agx_adapter = None

# Define API data models
class ResearchRequest(BaseModel):
    """API request format for research"""
    query: str
    depth: str = ResearchDepth.MODERATE
    topics: List[str] = []

class BiomarkerRequest(BaseModel):
    """API request format for biomarker analysis"""
    biomarker: str
    depth: str = ResearchDepth.MODERATE

class ComparisonRequest(BaseModel):
    """API request format for treatment comparison"""
    medications: List[str]
    depth: str = ResearchDepth.MODERATE

class LiteratureRequest(BaseModel):
    """API request format for literature search"""
    query: str
    max_results: int = 10
    start_year: Optional[int] = None
    end_year: Optional[int] = None

# Initialize agents on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure HMS-AGX adapter
    global agx_adapter
    agx_base_url = os.environ.get("AGX_BASE_URL", "http://localhost:8000/api/v1")
    agx_api_key = os.environ.get("AGX_API_KEY", "")
    agx_adapter = AGXAdapter(base_url=agx_base_url, api_key=agx_api_key)
    
    # Create research agent
    global research_agent
    agent_id = "agx_research_agent"
    research_agent = ResearchAgent(agent_id, "crohns_research_agent", agx_base_url=agx_base_url)
    
    # Start the research agent
    await research_agent.start()
    logger.info("Research agent started")
    
    yield
    
    # Stop the research agent
    await research_agent.stop()
    logger.info("Research agent stopped")

# Create FastAPI app
app = FastAPI(
    title="HMS-AGX Research API",
    description="API for HMS-AGX Research Component in Crohn's Disease Treatment System",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {"status": "HMS-AGX Research System is running"}

@app.post("/api/research")
async def perform_research(request: ResearchRequest):
    """Perform deep research on a topic"""
    if not agx_adapter:
        raise HTTPException(status_code=500, detail="AGX adapter not initialized")
    
    # Convert depth string to numeric value
    depth_map = {
        ResearchDepth.SHALLOW: 1,
        ResearchDepth.MODERATE: 2,
        ResearchDepth.DEEP: 3,
        ResearchDepth.EXHAUSTIVE: 5
    }
    depth_value = depth_map.get(request.depth, 2)
    
    # Call AGX adapter
    try:
        result = await agx_adapter.research(
            query=request.query,
            depth=depth_value,
            breadth=4,
            topics=request.topics
        )
        return result
    except Exception as e:
        logger.error(f"Research request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research/treatment")
async def research_treatment(request: ResearchRequest):
    """Research a specific treatment for Crohn's disease"""
    if not research_agent:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    # Extract medication name from query
    medication = request.query
    if "research" in medication.lower() and "treatment" in medication.lower():
        parts = medication.lower().split("treatment")
        if len(parts) > 1:
            medication = parts[0].strip()
    
    # Create a message to send to the research agent
    message = AgentMessage(
        message_id=f"web_request_{id(request)}",
        sender_id="web_api",
        receiver_id=research_agent.agent_id,
        message_type=MessageType.COMMAND,
        content={
            'command': 'research_treatment',
            'medication': medication,
            'depth': request.depth,
            'topics': request.topics or [ResearchTopic.TREATMENT_EFFICACY]
        }
    )
    
    # Process the message and wait for response
    await research_agent.receive_message(message)
    
    # Wait for processing (in a real system, this would be async/webhook based)
    for _ in range(10):
        if not research_agent.outbox.empty():
            response = await research_agent.outbox.get()
            if response.correlation_id == message.message_id:
                return response.content
        await asyncio.sleep(0.5)
    
    # Return pending status if no immediate response
    return {"status": "pending", "message": "Research job started, check later for results"}

@app.post("/api/research/biomarker")
async def research_biomarker(request: BiomarkerRequest):
    """Research a biomarker for Crohn's disease"""
    if not research_agent:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    # Create a message to send to the research agent
    message = AgentMessage(
        message_id=f"web_request_{id(request)}",
        sender_id="web_api",
        receiver_id=research_agent.agent_id,
        message_type=MessageType.COMMAND,
        content={
            'command': 'research_biomarker',
            'biomarker': request.biomarker,
            'depth': request.depth
        }
    )
    
    # Process the message and wait for response
    await research_agent.receive_message(message)
    
    # Wait for processing (in a real system, this would be async/webhook based)
    for _ in range(10):
        if not research_agent.outbox.empty():
            response = await research_agent.outbox.get()
            if response.correlation_id == message.message_id:
                return response.content
        await asyncio.sleep(0.5)
    
    # Return pending status if no immediate response
    return {"status": "pending", "message": "Research job started, check later for results"}

@app.post("/api/research/comparison")
async def compare_treatments(request: ComparisonRequest):
    """Compare multiple treatments for Crohn's disease"""
    if not research_agent:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    # Create a message to send to the research agent
    message = AgentMessage(
        message_id=f"web_request_{id(request)}",
        sender_id="web_api",
        receiver_id=research_agent.agent_id,
        message_type=MessageType.COMMAND,
        content={
            'command': 'research_treatment_comparison',
            'medications': request.medications,
            'depth': request.depth
        }
    )
    
    # Process the message and wait for response
    await research_agent.receive_message(message)
    
    # Wait for processing (in a real system, this would be async/webhook based)
    for _ in range(10):
        if not research_agent.outbox.empty():
            response = await research_agent.outbox.get()
            if response.correlation_id == message.message_id:
                return response.content
        await asyncio.sleep(0.5)
    
    # Return pending status if no immediate response
    return {"status": "pending", "message": "Research job started, check later for results"}

@app.post("/api/literature")
async def search_literature(request: LiteratureRequest):
    """Search scientific literature"""
    if not agx_adapter:
        raise HTTPException(status_code=500, detail="AGX adapter not initialized")
    
    try:
        results = await agx_adapter.search_literature(
            query=request.query,
            max_results=request.max_results,
            start_year=request.start_year,
            end_year=request.end_year
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Literature search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/research/job/{job_id}")
async def get_research_job(job_id: str):
    """Get the status and results of a research job"""
    if not research_agent:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    # Create a message to send to the research agent
    message = AgentMessage(
        message_id=f"web_request_job_{job_id}",
        sender_id="web_api",
        receiver_id=research_agent.agent_id,
        message_type=MessageType.QUERY,
        content={
            'query': 'research_status',
            'job_id': job_id
        }
    )
    
    # Process the message and wait for response
    await research_agent.receive_message(message)
    
    # Wait for processing
    for _ in range(5):
        if not research_agent.outbox.empty():
            response = await research_agent.outbox.get()
            if response.correlation_id == message.message_id:
                return response.content
        await asyncio.sleep(0.2)
    
    # Return error if no response
    raise HTTPException(status_code=404, detail=f"Research job {job_id} not found")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if not research_agent or not research_agent.running:
        raise HTTPException(status_code=503, detail="Research agent is not running")
    return {"status": "healthy"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HMS-AGX Research System")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()
    
    uvicorn.run("main:app", host=args.host, port=args.port, reload=False)