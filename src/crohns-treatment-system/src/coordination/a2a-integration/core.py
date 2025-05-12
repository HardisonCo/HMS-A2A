#!/usr/bin/env python3
"""
HMS-A2A Core Module for Crohn's Disease Treatment System

This module provides the core agent-to-agent coordination functionality
for the Crohn's Disease Treatment System. It manages communication between
different system components and orchestrates the adaptive clinical trial process.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hms-a2a')

class AgentRole(Enum):
    """Roles that agents can take in the system"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    OPTIMIZER = "optimizer"
    MONITOR = "monitor"
    VERIFIER = "verifier"
    CLINICAL = "clinical"
    SAFETY = "safety"
    PATIENT_ADVOCATE = "patient_advocate"

class MessageType(Enum):
    """Types of messages that can be exchanged between agents"""
    QUERY = "query"
    RESPONSE = "response"
    COMMAND = "command"
    EVENT = "event"
    DATA = "data"
    ERROR = "error"
    STATUS = "status"

@dataclass
class AgentMessage:
    """Message format for agent communication"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: MessageType = MessageType.DATA
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: import time; return time.time())
    correlation_id: Optional[str] = None
    priority: int = 1  # 1-5, where 1 is highest priority
    ttl: int = 300  # Time to live in seconds

    def to_json(self) -> str:
        """Convert message to JSON string"""
        msg_dict = {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "priority": self.priority,
            "ttl": self.ttl
        }
        return json.dumps(msg_dict)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Create message from JSON string"""
        msg_dict = json.loads(json_str)
        msg_dict["message_type"] = MessageType(msg_dict["message_type"])
        return cls(**msg_dict)

class Agent:
    """Base class for all agents in the system"""
    
    def __init__(self, agent_id: str, role: AgentRole, name: str = None):
        self.agent_id = agent_id
        self.role = role
        self.name = name or f"{role.value}_{agent_id[:8]}"
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        self.inbox: asyncio.Queue = asyncio.Queue()
        self.outbox: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.logger = logging.getLogger(f'hms-a2a.{self.name}')
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type].append(handler)
    
    async def send_message(self, receiver_id: str, message_type: MessageType, 
                          content: Dict[str, Any], correlation_id: Optional[str] = None,
                          priority: int = 1, ttl: int = 300) -> str:
        """Send a message to another agent"""
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            correlation_id=correlation_id,
            priority=priority,
            ttl=ttl
        )
        await self.outbox.put(message)
        self.logger.debug(f"Sent message {message.message_id} to {receiver_id}")
        return message.message_id
    
    async def receive_message(self, message: AgentMessage):
        """Process an incoming message"""
        await self.inbox.put(message)
        self.logger.debug(f"Received message {message.message_id} from {message.sender_id}")
    
    async def _process_messages(self):
        """Process messages from the inbox"""
        while self.running:
            try:
                message = await self.inbox.get()
                self.logger.debug(f"Processing message {message.message_id}")
                
                # Dispatch message to appropriate handlers
                handlers = self.message_handlers[message.message_type]
                for handler in handlers:
                    try:
                        await handler(message)
                    except Exception as e:
                        self.logger.error(f"Error in handler for message {message.message_id}: {e}")
                
                self.inbox.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing messages: {e}")
    
    async def start(self):
        """Start the agent"""
        self.running = True
        self.logger.info(f"Agent {self.name} starting")
        
        # Create task for processing messages
        self.message_task = asyncio.create_task(self._process_messages())
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        self.logger.info(f"Agent {self.name} stopping")
        
        # Cancel message processing task
        if hasattr(self, 'message_task'):
            self.message_task.cancel()
            try:
                await self.message_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info(f"Agent {self.name} stopped")

class AgentDirectory:
    """Directory service for agent discovery and management"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.roles: Dict[AgentRole, List[str]] = {role: [] for role in AgentRole}
        self.logger = logging.getLogger('hms-a2a.directory')
    
    def register_agent(self, agent: Agent):
        """Register an agent in the directory"""
        self.agents[agent.agent_id] = agent
        self.roles[agent.role].append(agent.agent_id)
        self.logger.info(f"Registered agent {agent.name} with ID {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the directory"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            self.roles[agent.role].remove(agent_id)
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with a specific role"""
        return [self.agents[agent_id] for agent_id in self.roles[role]]
    
    def find_agent(self, **criteria) -> List[Agent]:
        """Find agents matching the given criteria"""
        result = []
        for agent in self.agents.values():
            matches = True
            for key, value in criteria.items():
                if not hasattr(agent, key) or getattr(agent, key) != value:
                    matches = False
                    break
            if matches:
                result.append(agent)
        return result

class AgentCoordinator:
    """Coordinates communication between agents"""
    
    def __init__(self, directory: AgentDirectory):
        self.directory = directory
        self.running = False
        self.message_queue = asyncio.Queue()
        self.logger = logging.getLogger('hms-a2a.coordinator')
    
    async def route_message(self, message: AgentMessage):
        """Route a message to its intended recipient"""
        await self.message_queue.put(message)
    
    async def _process_messages(self):
        """Process messages in the queue"""
        while self.running:
            try:
                message = await self.message_queue.get()
                
                # Check if message has expired
                if message.ttl <= 0:
                    self.logger.warning(f"Message {message.message_id} expired")
                    self.message_queue.task_done()
                    continue
                
                # Find recipient agent
                recipient = self.directory.get_agent(message.receiver_id)
                if recipient:
                    await recipient.receive_message(message)
                else:
                    self.logger.warning(f"Unknown recipient {message.receiver_id} for message {message.message_id}")
                
                self.message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error routing message: {e}")
    
    async def start(self):
        """Start the coordinator"""
        self.running = True
        self.logger.info("Agent coordinator starting")
        
        # Create task for processing messages
        self.message_task = asyncio.create_task(self._process_messages())
        
        # Create tasks for processing outbox messages from each agent
        self.outbox_tasks = []
        for agent in self.directory.agents.values():
            task = asyncio.create_task(self._process_agent_outbox(agent))
            self.outbox_tasks.append(task)
    
    async def _process_agent_outbox(self, agent: Agent):
        """Process outbox messages from an agent"""
        while self.running:
            try:
                message = await agent.outbox.get()
                await self.route_message(message)
                agent.outbox.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing outbox for agent {agent.agent_id}: {e}")
    
    async def stop(self):
        """Stop the coordinator"""
        self.running = False
        self.logger.info("Agent coordinator stopping")
        
        # Cancel message processing task
        if hasattr(self, 'message_task'):
            self.message_task.cancel()
            try:
                await self.message_task
            except asyncio.CancelledError:
                pass
        
        # Cancel outbox processing tasks
        for task in getattr(self, 'outbox_tasks', []):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Agent coordinator stopped")

class AgentSystem:
    """Main system that manages all agents and their interactions"""
    
    def __init__(self):
        self.directory = AgentDirectory()
        self.coordinator = AgentCoordinator(self.directory)
        self.running = False
        self.logger = logging.getLogger('hms-a2a.system')
    
    def create_agent(self, role: AgentRole, name: Optional[str] = None) -> Agent:
        """Create and register a new agent"""
        agent_id = str(uuid.uuid4())
        agent = Agent(agent_id, role, name)
        self.directory.register_agent(agent)
        return agent
    
    async def start(self):
        """Start the agent system"""
        self.running = True
        self.logger.info("Agent system starting")
        
        # Start the coordinator
        await self.coordinator.start()
        
        # Start all registered agents
        for agent in self.directory.agents.values():
            await agent.start()
        
        self.logger.info("Agent system started")
    
    async def stop(self):
        """Stop the agent system"""
        self.running = False
        self.logger.info("Agent system stopping")
        
        # Stop all registered agents
        for agent in self.directory.agents.values():
            await agent.stop()
        
        # Stop the coordinator
        await self.coordinator.stop()
        
        self.logger.info("Agent system stopped")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.directory.get_agent(agent_id)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with a specific role"""
        return self.directory.get_agents_by_role(role)

# Example specialized agent for genetic optimization
class GeneticOptimizerAgent(Agent):
    """Agent that interfaces with the genetic engine for treatment optimization"""
    
    def __init__(self, agent_id: str, name: Optional[str] = None):
        super().__init__(agent_id, AgentRole.OPTIMIZER, name)
        
        # Register message handlers
        self.register_handler(MessageType.COMMAND, self._handle_command)
        self.register_handler(MessageType.QUERY, self._handle_query)
        self.register_handler(MessageType.DATA, self._handle_data)
        
        # Store for optimization jobs
        self.optimization_jobs = {}
        
        self.logger = logging.getLogger(f'hms-a2a.genetic-optimizer')
    
    async def _handle_command(self, message: AgentMessage):
        """Handle command messages"""
        command = message.content.get('command')
        if command == 'optimize_treatment':
            job_id = str(uuid.uuid4())
            patient_data = message.content.get('patient_data', {})
            
            # Store job info
            self.optimization_jobs[job_id] = {
                'status': 'pending',
                'patient_data': patient_data,
                'requestor': message.sender_id,
                'correlation_id': message.message_id
            }
            
            # Acknowledge receipt
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'accepted',
                    'job_id': job_id
                },
                correlation_id=message.message_id
            )
            
            # Start optimization job asynchronously
            asyncio.create_task(self._run_optimization_job(job_id))
    
    async def _run_optimization_job(self, job_id: str):
        """Run an optimization job"""
        try:
            job = self.optimization_jobs[job_id]
            job['status'] = 'running'
            
            # Send status update
            await self.send_message(
                job['requestor'],
                MessageType.STATUS,
                {
                    'job_id': job_id,
                    'status': 'running'
                },
                correlation_id=job['correlation_id']
            )
            
            # Here we would call the FFI interface to the genetic engine
            # For now, we'll simulate a delay and generate a fake result
            await asyncio.sleep(2)
            
            # Generate fake result
            result = {
                'treatment_plan': [
                    {
                        'medication': 'Upadacitinib',
                        'dosage': 15.0,
                        'unit': 'mg',
                        'frequency': 'daily',
                        'duration': 30
                    },
                    {
                        'medication': 'Azathioprine',
                        'dosage': 50.0,
                        'unit': 'mg',
                        'frequency': 'daily',
                        'duration': 30
                    }
                ],
                'fitness': 0.85,
                'confidence': 0.78
            }
            
            # Update job status
            job['status'] = 'completed'
            job['result'] = result
            
            # Send result
            await self.send_message(
                job['requestor'],
                MessageType.RESPONSE,
                {
                    'job_id': job_id,
                    'status': 'completed',
                    'result': result
                },
                correlation_id=job['correlation_id']
            )
        except Exception as e:
            self.logger.error(f"Error in optimization job {job_id}: {e}")
            
            # Update job status
            if job_id in self.optimization_jobs:
                self.optimization_jobs[job_id]['status'] = 'failed'
                self.optimization_jobs[job_id]['error'] = str(e)
            
            # Send error message
            try:
                await self.send_message(
                    job['requestor'],
                    MessageType.ERROR,
                    {
                        'job_id': job_id,
                        'status': 'failed',
                        'error': str(e)
                    },
                    correlation_id=job['correlation_id']
                )
            except Exception:
                pass
    
    async def _handle_query(self, message: AgentMessage):
        """Handle query messages"""
        query_type = message.content.get('query')
        
        if query_type == 'job_status':
            job_id = message.content.get('job_id')
            if job_id in self.optimization_jobs:
                job = self.optimization_jobs[job_id]
                await self.send_message(
                    message.sender_id,
                    MessageType.RESPONSE,
                    {
                        'job_id': job_id,
                        'status': job['status'],
                        'result': job.get('result')
                    },
                    correlation_id=message.message_id
                )
            else:
                await self.send_message(
                    message.sender_id,
                    MessageType.ERROR,
                    {
                        'error': f'Job {job_id} not found'
                    },
                    correlation_id=message.message_id
                )
    
    async def _handle_data(self, message: AgentMessage):
        """Handle data messages"""
        # Processing for data messages would go here
        pass

# Example usage
async def main():
    # Create agent system
    system = AgentSystem()
    
    # Create some agents
    coordinator = system.create_agent(AgentRole.COORDINATOR, "main_coordinator")
    
    # Create specialized genetic optimizer agent
    optimizer_id = str(uuid.uuid4())
    optimizer = GeneticOptimizerAgent(optimizer_id, "treatment_optimizer")
    system.directory.register_agent(optimizer)
    
    # Start the system
    await system.start()
    
    try:
        # Simulate coordinator sending an optimization request
        await coordinator.send_message(
            optimizer.agent_id,
            MessageType.COMMAND,
            {
                'command': 'optimize_treatment',
                'patient_data': {
                    'patient_id': 'P12345',
                    'age': 45,
                    'weight': 70.5,
                    'crohns_type': 'ileocolonic',
                    'severity': 'moderate',
                    'genetic_markers': {
                        'NOD2': 'variant',
                        'ATG16L1': 'normal',
                        'IL23R': 'variant'
                    },
                    'previous_treatments': [
                        {
                            'medication': 'Infliximab',
                            'response': 'partial'
                        }
                    ]
                }
            }
        )
        
        # Run for a while to let the messages process
        await asyncio.sleep(5)
    finally:
        # Stop the system
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())