#!/usr/bin/env python3
"""
HMS-A2A Main Entry Point for Crohn's Disease Treatment System

This module provides the main entry point for the HMS-A2A component,
setting up the agent system and API server for external communication.
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

from core import AgentSystem, AgentRole, MessageType, AgentMessage
from clinical_trial_agent import ClinicalTrialAgent, TrialDesign, AllocationStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hms-a2a.main')

# Initialize the agent system
agent_system = AgentSystem()

# Define API data models
class MessageRequest(BaseModel):
    """API request format for sending a message"""
    receiver_id: str
    message_type: str
    content: Dict[str, Any]
    correlation_id: Optional[str] = None
    priority: int = 1
    ttl: int = 300

class TrialCreateRequest(BaseModel):
    """API request format for creating a trial"""
    name: str
    description: str
    design: str
    allocation_strategy: str
    arms: List[Dict[str, Any]]

class PatientAddRequest(BaseModel):
    """API request format for adding a patient"""
    trial_id: str
    patient_data: Dict[str, Any]

class OutcomeRecordRequest(BaseModel):
    """API request format for recording an outcome"""
    trial_id: str
    patient_id: str
    outcome_data: Dict[str, Any]

class AnalysisRequest(BaseModel):
    """API request format for running an analysis"""
    trial_id: str
    analysis_params: Dict[str, Any]

class AdaptationRequest(BaseModel):
    """API request format for adapting a trial"""
    trial_id: str
    adaptations: List[Dict[str, Any]]

# Initialize agents on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create and register agents
    coordinator = agent_system.create_agent(AgentRole.COORDINATOR, "main_coordinator")
    
    # Create clinical trial agent
    trial_agent_id = "clinical_trial_agent"
    trial_agent = ClinicalTrialAgent(trial_agent_id, "crohns_trial_manager")
    agent_system.directory.register_agent(trial_agent)
    
    # Start the agent system
    await agent_system.start()
    logger.info("Agent system started")
    
    # Store agent IDs for API access
    app.state.coordinator_id = coordinator.agent_id
    app.state.trial_agent_id = trial_agent_id
    
    yield
    
    # Stop the agent system
    await agent_system.stop()
    logger.info("Agent system stopped")

# Create FastAPI app
app = FastAPI(
    title="HMS-A2A API",
    description="API for HMS-A2A Agent System in Crohn's Disease Treatment System",
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

# Message response queue for API clients
message_responses = {}

# Register a response handler for the coordinator
async def handle_coordinator_response(message: AgentMessage):
    """Handle responses to the coordinator"""
    if message.correlation_id:
        message_responses[message.correlation_id] = {
            "message_id": message.message_id,
            "content": message.content,
            "timestamp": message.timestamp
        }

@app.get("/")
async def root():
    """API root endpoint"""
    return {"status": "HMS-A2A Agent System is running"}

@app.post("/api/message")
async def send_message(request: MessageRequest):
    """Send a message to an agent"""
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Register response handler if not already registered
    if MessageType.RESPONSE not in coordinator.message_handlers or handle_coordinator_response not in coordinator.message_handlers[MessageType.RESPONSE]:
        coordinator.register_handler(MessageType.RESPONSE, handle_coordinator_response)
        coordinator.register_handler(MessageType.ERROR, handle_coordinator_response)
    
    # Convert message type string to enum
    try:
        message_type = MessageType(request.message_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid message type: {request.message_type}")
    
    # Send message
    message_id = await coordinator.send_message(
        request.receiver_id,
        message_type,
        request.content,
        request.correlation_id,
        request.priority,
        request.ttl
    )
    
    return {"message_id": message_id}

@app.get("/api/message/{message_id}")
async def get_message_response(message_id: str):
    """Get a response to a previously sent message"""
    if message_id in message_responses:
        response = message_responses[message_id]
        # Optionally cleanup after retrieving
        # del message_responses[message_id]
        return response
    else:
        return {"status": "pending"}

@app.post("/api/trials")
async def create_trial(request: TrialCreateRequest):
    """Create a new clinical trial"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Register response handler if not already registered
    if MessageType.RESPONSE not in coordinator.message_handlers or handle_coordinator_response not in coordinator.message_handlers[MessageType.RESPONSE]:
        coordinator.register_handler(MessageType.RESPONSE, handle_coordinator_response)
        coordinator.register_handler(MessageType.ERROR, handle_coordinator_response)
    
    # Convert design and allocation strategy to proper values
    try:
        design = TrialDesign(request.design).value
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid trial design: {request.design}")
    
    try:
        allocation_strategy = AllocationStrategy(request.allocation_strategy).value
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid allocation strategy: {request.allocation_strategy}")
    
    # Prepare trial data
    trial_data = {
        'name': request.name,
        'description': request.description,
        'design': design,
        'allocation_strategy': allocation_strategy,
        'arms': request.arms
    }
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.COMMAND,
        {
            'command': 'create_trial',
            'trial_data': trial_data
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.post("/api/trials/{trial_id}/patients")
async def add_patient(trial_id: str, request: PatientAddRequest):
    """Add a patient to a trial"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.COMMAND,
        {
            'command': 'add_patient',
            'trial_id': trial_id,
            'patient_data': request.patient_data
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.post("/api/trials/{trial_id}/outcomes/{patient_id}")
async def record_outcome(trial_id: str, patient_id: str, request: OutcomeRecordRequest):
    """Record a patient outcome"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.COMMAND,
        {
            'command': 'record_outcome',
            'trial_id': trial_id,
            'patient_id': patient_id,
            'outcome_data': request.outcome_data
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.post("/api/trials/{trial_id}/analyses")
async def run_analysis(trial_id: str, request: AnalysisRequest):
    """Run an interim analysis"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.COMMAND,
        {
            'command': 'run_interim_analysis',
            'trial_id': trial_id,
            'analysis_params': request.analysis_params
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.post("/api/trials/{trial_id}/adaptations")
async def adapt_trial(trial_id: str, request: AdaptationRequest):
    """Adapt a trial based on analysis"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.COMMAND,
        {
            'command': 'adapt_trial',
            'trial_id': trial_id,
            'adaptations': request.adaptations
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.get("/api/trials/{trial_id}")
async def get_trial_info(trial_id: str):
    """Get information about a trial"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.QUERY,
        {
            'query': 'trial_info',
            'trial_id': trial_id
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.get("/api/trials/{trial_id}/patients/{patient_id}")
async def get_patient_info(trial_id: str, patient_id: str):
    """Get information about a patient"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.QUERY,
        {
            'query': 'patient_info',
            'trial_id': trial_id,
            'patient_id': patient_id
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.get("/api/trials/{trial_id}/analyses/{analysis_id}")
async def get_analysis_result(trial_id: str, analysis_id: str):
    """Get the result of an analysis"""
    trial_agent_id = app.state.trial_agent_id
    coordinator = agent_system.get_agent(app.state.coordinator_id)
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator agent not available")
    
    # Send message to clinical trial agent
    message_id = await coordinator.send_message(
        trial_agent_id,
        MessageType.QUERY,
        {
            'query': 'analysis_result',
            'trial_id': trial_id,
            'analysis_id': analysis_id
        }
    )
    
    # Wait for response (in real system this would be async/webhook based)
    for _ in range(10):  # Try for 5 seconds
        if message_id in message_responses:
            return message_responses[message_id]["content"]
        await asyncio.sleep(0.5)
    
    return {"status": "pending", "message_id": message_id}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if not agent_system.running:
        raise HTTPException(status_code=503, detail="Agent system is not running")
    return {"status": "healthy"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HMS-A2A Agent System")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    args = parser.parse_args()
    
    uvicorn.run("main:app", host=args.host, port=args.port, reload=False)