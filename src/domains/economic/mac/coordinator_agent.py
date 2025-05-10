"""
Coordinator Agent for the Multi-Agent Collaboration (MAC) Model.

This module implements the asynchronous coordination component of the MAC architecture,
responsible for workflow management, agent scheduling, and ensuring proper execution
of the defined process across all agent types.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import logging
import time
import json
import asyncio
from uuid import uuid4
from enum import Enum

# A2A Imports
from a2a.core import Agent, Task, TaskResult
from graph.cort_react_agent import CoRTReactAgent

# MAC Imports
from mac.environment import StateStore
from mac.verification import ExternalChecker
from mac.human_interface import HumanQueryInterface


class WorkflowPhase(Enum):
    """Workflow phases based on the HMS-DEV process."""
    DISCOVERY = 1
    SPECIFICATION = 2
    DESIGN = 3
    DEVELOPMENT = 4
    VERIFICATION = 5
    INTEGRATION = 6
    DEPLOYMENT = 7
    MONITORING = 8
    IMPROVEMENT = 9
    RELEASE = 10


class SessionStatus(Enum):
    """Status of a Pomodoro session."""
    NOT_STARTED = 0
    DISCOVERY = 1  # 15 minutes
    SPECS = 2      # 10 minutes
    CODING = 3     # 25 minutes
    VERIFICATION = 4  # 5 minutes
    REFLECTION = 5    # 5 minutes
    COMPLETED = 6
    PAUSED = 7


class CoordinatorAgent:
    """
    Coordinator Agent implementation for the MAC architecture.
    
    The Coordinator Agent is responsible for asynchronous agent orchestration:
    1. Managing workflow phases and ensuring proper process execution
    2. Scheduling agent activities and handling concurrency
    3. Implementing the Pomodoro-based workflow structure
    4. Tracking task progress across the entire workflow
    5. Ensuring inter-agent communication follows proper protocols
    
    This agent acts as the workflow manager in the MAS, handling the complexity
    of multi-agent coordination while the Supervisor focuses on task decomposition
    and domain delegation.
    """
    
    def __init__(
        self, 
        name: str = "MAC-Coordinator",
        supervisor_agent = None,
        state_store: Optional[StateStore] = None,
        human_interface: Optional[HumanQueryInterface] = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the Coordinator Agent.
        
        Args:
            name: Name of the coordinator agent
            supervisor_agent: Reference to the SupervisorAgent
            state_store: Environment/State Store for persistent memory
            human_interface: Interface for human-in-the-loop interactions
            config: Additional configuration parameters
        """
        self.name = name
        self.config = config or {}
        self.supervisor = supervisor_agent
        self.state_store = state_store
        self.human_interface = human_interface
        
        # Task and workflow tracking
        self.active_sessions = {}
        self.workflow_status = {}
        self.agent_status = {}
        
        # Communication channels for agent-to-agent messaging
        self.communication_channels = {}
        
        # Locks for concurrency control
        self.locks = {}
        
        # Timer for Pomodoro sessions
        self.session_timers = {}
        
        # Set up logging
        self.logger = logging.getLogger(f"MAC.{name}")
        self.logger.info(f"Initialized MAC Coordinator Agent: {name}")
        
        # Initialize workflow tools integration
        self._init_workflow_tools()
    
    def _init_workflow_tools(self):
        """Initialize integration with workflow tools."""
        self.workflow_tools = {
            "session": {
                "start": self.start_session,
                "end": self.end_session,
                "pause": self.pause_session,
                "resume": self.resume_session
            },
            "feature": {
                "start": self.start_feature,
                "finish": self.finish_feature,
                "list": self.list_features
            },
            "agent": {
                "register": self.register_agent,
                "assign": self.assign_task_to_agent,
                "status": self.get_agent_status
            }
        }
        
        # Initialize GitFlow integration
        self.git_flow = {
            "main": None,
            "develop": None,
            "feature_branches": {},
            "release_branches": {},
            "hotfix_branches": {}
        }
    
    def register_workflow_handler(self, command: str, subcommand: str, handler: Callable):
        """
        Register a custom handler for workflow tools.
        
        Args:
            command: Main command (e.g., 'session', 'feature')
            subcommand: Subcommand (e.g., 'start', 'end')
            handler: Function to handle the command
        """
        if command not in self.workflow_tools:
            self.workflow_tools[command] = {}
        
        self.workflow_tools[command][subcommand] = handler
        self.logger.info(f"Registered custom handler for {command} {subcommand}")
    
    async def start_session(self, task_id: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new Pomodoro session.
        
        Args:
            task_id: ID of the task for this session
            agent_id: Optional agent ID to assign to the session
            
        Returns:
            Session information
        """
        session_id = f"session_{task_id}_{uuid4().hex[:8]}"
        
        session = {
            "id": session_id,
            "task_id": task_id,
            "agent_id": agent_id,
            "status": SessionStatus.DISCOVERY,
            "start_time": time.time(),
            "phase_timestamps": {
                "discovery": time.time(),
                "specs": None,
                "coding": None,
                "verification": None,
                "reflection": None,
                "completion": None
            },
            "journal": {
                "decisions": [],
                "blockers": []
            }
        }
        
        self.active_sessions[session_id] = session
        
        # Record in state store
        if self.state_store:
            self.state_store.record_session_start(session_id, task_id, agent_id)
        
        # Set discovery phase timer (15 minutes)
        self._schedule_phase_transition(session_id, SessionStatus.SPECS, 15 * 60)
        
        self.logger.info(f"Started session {session_id} for task {task_id}")
        
        return {
            "session_id": session_id,
            "status": "started",
            "current_phase": "discovery",
            "time_remaining": 15 * 60  # 15 minutes in seconds
        }
    
    async def transition_session_phase(self, session_id: str, new_status: SessionStatus) -> Dict[str, Any]:
        """
        Transition a session to a new phase.
        
        Args:
            session_id: ID of the session
            new_status: New session status
            
        Returns:
            Updated session information
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        old_status = session["status"]
        session["status"] = new_status
        
        # Record timestamp for the new phase
        if new_status == SessionStatus.SPECS:
            session["phase_timestamps"]["specs"] = time.time()
            # Schedule next transition (10 minutes)
            self._schedule_phase_transition(session_id, SessionStatus.CODING, 10 * 60)
            remaining_time = 10 * 60
            
        elif new_status == SessionStatus.CODING:
            session["phase_timestamps"]["coding"] = time.time()
            # Schedule next transition (25 minutes)
            self._schedule_phase_transition(session_id, SessionStatus.VERIFICATION, 25 * 60)
            remaining_time = 25 * 60
            
        elif new_status == SessionStatus.VERIFICATION:
            session["phase_timestamps"]["verification"] = time.time()
            # Schedule next transition (5 minutes)
            self._schedule_phase_transition(session_id, SessionStatus.REFLECTION, 5 * 60)
            remaining_time = 5 * 60
            
        elif new_status == SessionStatus.REFLECTION:
            session["phase_timestamps"]["reflection"] = time.time()
            # Schedule next transition (5 minutes) to completion
            self._schedule_phase_transition(session_id, SessionStatus.COMPLETED, 5 * 60)
            remaining_time = 5 * 60
            
        elif new_status == SessionStatus.COMPLETED:
            session["phase_timestamps"]["completion"] = time.time()
            remaining_time = 0
            
        elif new_status == SessionStatus.PAUSED:
            # Store time left in current phase for later resume
            current_phase_start = None
            phase_duration = 0
            
            if old_status == SessionStatus.DISCOVERY:
                current_phase_start = session["phase_timestamps"]["discovery"]
                phase_duration = 15 * 60
            elif old_status == SessionStatus.SPECS:
                current_phase_start = session["phase_timestamps"]["specs"]
                phase_duration = 10 * 60
            elif old_status == SessionStatus.CODING:
                current_phase_start = session["phase_timestamps"]["coding"]
                phase_duration = 25 * 60
            elif old_status == SessionStatus.VERIFICATION:
                current_phase_start = session["phase_timestamps"]["verification"]
                phase_duration = 5 * 60
            elif old_status == SessionStatus.REFLECTION:
                current_phase_start = session["phase_timestamps"]["reflection"]
                phase_duration = 5 * 60
            
            time_elapsed = time.time() - current_phase_start if current_phase_start else 0
            session["paused_time_remaining"] = max(0, phase_duration - time_elapsed)
            session["paused_status"] = old_status
            remaining_time = session["paused_time_remaining"]
            
            # Cancel any scheduled transitions
            if session_id in self.session_timers:
                self.session_timers[session_id].cancel()
                del self.session_timers[session_id]
            
        else:
            remaining_time = 0
        
        # Record in state store
        if self.state_store:
            self.state_store.update_session_status(
                session_id=session_id,
                status=new_status.name,
                timestamp=time.time()
            )
        
        self.logger.info(f"Transitioned session {session_id} from {old_status.name} to {new_status.name}")
        
        return {
            "session_id": session_id,
            "status": new_status.name.lower(),
            "previous_status": old_status.name.lower(),
            "time_remaining": remaining_time
        }
    
    def _schedule_phase_transition(self, session_id: str, next_phase: SessionStatus, delay_seconds: int):
        """
        Schedule a transition to the next session phase.
        
        Args:
            session_id: ID of the session
            next_phase: Next phase to transition to
            delay_seconds: Delay in seconds before transition
        """
        # Cancel any existing timer
        if session_id in self.session_timers:
            self.session_timers[session_id].cancel()
        
        # Create new timer
        loop = asyncio.get_event_loop()
        timer = loop.call_later(
            delay_seconds,
            lambda: asyncio.create_task(self._execute_phase_transition(session_id, next_phase))
        )
        
        self.session_timers[session_id] = timer
    
    async def _execute_phase_transition(self, session_id: str, next_phase: SessionStatus):
        """
        Execute a scheduled phase transition.
        
        Args:
            session_id: ID of the session
            next_phase: Next phase to transition to
        """
        try:
            await self.transition_session_phase(session_id, next_phase)
        except Exception as e:
            self.logger.error(f"Error transitioning session {session_id} to {next_phase.name}: {str(e)}")
    
    async def end_session(self, session_id: str, journal: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        End a Pomodoro session and log progress.
        
        Args:
            session_id: ID of the session
            journal: Optional journal entries for the session
            
        Returns:
            Session completion information
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Update journal if provided
        if journal:
            if "decisions" in journal:
                session["journal"]["decisions"].extend(journal["decisions"])
            if "blockers" in journal:
                session["journal"]["blockers"].extend(journal["blockers"])
        
        # Complete the session
        await self.transition_session_phase(session_id, SessionStatus.COMPLETED)
        
        # Calculate stats
        start_time = session["start_time"]
        total_duration = time.time() - start_time
        
        # Generate improvement tickets if needed
        improvement_tickets = await self._generate_improvement_tickets(session)
        
        # Record completion in state store
        if self.state_store:
            self.state_store.record_session_completion(
                session_id=session_id,
                duration=total_duration,
                journal=session["journal"],
                improvement_tickets=improvement_tickets
            )
        
        # Clean up timers
        if session_id in self.session_timers:
            self.session_timers[session_id].cancel()
            del self.session_timers[session_id]
        
        # Remove from active sessions
        completed_session = self.active_sessions.pop(session_id)
        
        self.logger.info(f"Ended session {session_id} with duration {total_duration:.2f} seconds")
        
        return {
            "session_id": session_id,
            "status": "completed",
            "duration": total_duration,
            "journal": completed_session["journal"],
            "improvement_tickets": improvement_tickets
        }
    
    async def pause_session(self, session_id: str) -> Dict[str, Any]:
        """
        Pause a Pomodoro session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session pause information
        """
        return await self.transition_session_phase(session_id, SessionStatus.PAUSED)
    
    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Resume a paused Pomodoro session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session resume information
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        if session["status"] != SessionStatus.PAUSED:
            raise ValueError(f"Session {session_id} is not paused")
        
        # Get the previous status and remaining time
        previous_status = session["paused_status"]
        remaining_time = session["paused_time_remaining"]
        
        # Restore the previous status
        session["status"] = previous_status
        
        # Clean up paused state
        if "paused_status" in session:
            del session["paused_status"]
        if "paused_time_remaining" in session:
            del session["paused_time_remaining"]
        
        # Schedule transition based on remaining time
        self._schedule_phase_transition(
            session_id=session_id,
            next_phase=self._get_next_status(previous_status),
            delay_seconds=remaining_time
        )
        
        # Record in state store
        if self.state_store:
            self.state_store.update_session_status(
                session_id=session_id,
                status=previous_status.name,
                timestamp=time.time()
            )
        
        self.logger.info(f"Resumed session {session_id} to {previous_status.name} with {remaining_time:.2f} seconds remaining")
        
        return {
            "session_id": session_id,
            "status": previous_status.name.lower(),
            "time_remaining": remaining_time
        }
    
    def _get_next_status(self, current_status: SessionStatus) -> SessionStatus:
        """
        Get the next status in the Pomodoro workflow.
        
        Args:
            current_status: Current session status
            
        Returns:
            Next session status
        """
        status_flow = {
            SessionStatus.DISCOVERY: SessionStatus.SPECS,
            SessionStatus.SPECS: SessionStatus.CODING,
            SessionStatus.CODING: SessionStatus.VERIFICATION,
            SessionStatus.VERIFICATION: SessionStatus.REFLECTION,
            SessionStatus.REFLECTION: SessionStatus.COMPLETED
        }
        
        return status_flow.get(current_status, SessionStatus.COMPLETED)
    
    async def _generate_improvement_tickets(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate improvement tickets based on session journal.
        
        Args:
            session: Session data including journal
            
        Returns:
            List of improvement tickets
        """
        if not session["journal"]["decisions"] and not session["journal"]["blockers"]:
            return []
        
        tickets = []
        
        # Create ticket for significant blockers
        if session["journal"]["blockers"]:
            blocker_ticket = {
                "id": f"IMP-{uuid4().hex[:6]}",
                "title": f"Address blockers from session {session['id']}",
                "description": "The following blockers were identified during the session:\n" +
                               "\n".join(f"- {b}" for b in session["journal"]["blockers"]),
                "priority": "medium",
                "assigned_to": session["agent_id"],
                "status": "pending"
            }
            tickets.append(blocker_ticket)
        
        # Use decisions to generate improvement opportunities
        if session["journal"]["decisions"]:
            # Analyze patterns in decisions to find improvement areas
            decisions_text = "\n".join(session["journal"]["decisions"])
            
            # Check for documentation needs
            if "documentation" in decisions_text.lower() or "docs" in decisions_text.lower():
                doc_ticket = {
                    "id": f"IMP-{uuid4().hex[:6]}",
                    "title": "Improve documentation based on session decisions",
                    "description": "Documentation improvements identified during session:\n" +
                                   "\n".join(f"- {d}" for d in session["journal"]["decisions"] 
                                             if "doc" in d.lower()),
                    "priority": "medium",
                    "assigned_to": session["agent_id"],
                    "status": "pending"
                }
                tickets.append(doc_ticket)
            
            # Check for refactoring opportunities
            if "refactor" in decisions_text.lower():
                refactor_ticket = {
                    "id": f"IMP-{uuid4().hex[:6]}",
                    "title": "Refactoring opportunities from session",
                    "description": "Potential refactoring identified during session:\n" +
                                   "\n".join(f"- {d}" for d in session["journal"]["decisions"] 
                                             if "refactor" in d.lower()),
                    "priority": "medium",
                    "assigned_to": session["agent_id"],
                    "status": "pending"
                }
                tickets.append(refactor_ticket)
        
        return tickets
    
    async def start_feature(self, feature_name: str) -> Dict[str, Any]:
        """
        Start a new feature branch.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Feature branch information
        """
        # Create feature ID
        feature_id = f"feature_{feature_name}_{uuid4().hex[:6]}"
        
        # Create feature branch info
        feature_branch = {
            "id": feature_id,
            "name": feature_name,
            "branch_name": f"feature/{feature_name}",
            "created_at": time.time(),
            "status": "active",
            "tasks": [],
            "sessions": [],
            "workflow_phase": WorkflowPhase.DISCOVERY
        }
        
        # Store in Git flow tracking
        self.git_flow["feature_branches"][feature_id] = feature_branch
        
        # Record in state store
        if self.state_store:
            self.state_store.record_feature_branch(feature_id, feature_branch)
        
        self.logger.info(f"Started feature branch: {feature_branch['branch_name']}")
        
        return {
            "feature_id": feature_id,
            "branch_name": feature_branch["branch_name"],
            "status": "active",
            "workflow_phase": "discovery"
        }
    
    async def finish_feature(self, feature_id: str) -> Dict[str, Any]:
        """
        Finish a feature branch.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            Feature completion information
        """
        if feature_id not in self.git_flow["feature_branches"]:
            raise ValueError(f"Feature {feature_id} not found")
        
        feature = self.git_flow["feature_branches"][feature_id]
        feature["status"] = "completed"
        feature["completed_at"] = time.time()
        
        # Record in state store
        if self.state_store:
            self.state_store.update_feature_status(feature_id, "completed")
        
        self.logger.info(f"Completed feature branch: {feature['branch_name']}")
        
        return {
            "feature_id": feature_id,
            "branch_name": feature["branch_name"],
            "status": "completed",
            "duration": feature["completed_at"] - feature["created_at"]
        }
    
    async def list_features(self) -> Dict[str, Any]:
        """
        List all feature branches.
        
        Returns:
            Dictionary of all feature branches
        """
        features = {
            "active": [],
            "completed": []
        }
        
        for feature_id, feature in self.git_flow["feature_branches"].items():
            feature_info = {
                "id": feature_id,
                "name": feature["name"],
                "branch_name": feature["branch_name"],
                "created_at": feature["created_at"],
                "workflow_phase": feature["workflow_phase"].name
            }
            
            if feature["status"] == "active":
                features["active"].append(feature_info)
            else:
                feature_info["completed_at"] = feature.get("completed_at")
                features["completed"].append(feature_info)
        
        return features
    
    async def update_feature_workflow_phase(self, feature_id: str, phase: WorkflowPhase) -> Dict[str, Any]:
        """
        Update the workflow phase of a feature.
        
        Args:
            feature_id: ID of the feature
            phase: New workflow phase
            
        Returns:
            Updated feature information
        """
        if feature_id not in self.git_flow["feature_branches"]:
            raise ValueError(f"Feature {feature_id} not found")
        
        feature = self.git_flow["feature_branches"][feature_id]
        old_phase = feature["workflow_phase"]
        feature["workflow_phase"] = phase
        
        # Record in state store
        if self.state_store:
            self.state_store.update_feature_phase(feature_id, phase.name)
        
        self.logger.info(f"Updated feature {feature_id} workflow phase from {old_phase.name} to {phase.name}")
        
        return {
            "feature_id": feature_id,
            "branch_name": feature["branch_name"],
            "previous_phase": old_phase.name,
            "current_phase": phase.name
        }
    
    async def register_agent(self, agent_name: str, capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Register a new agent with the coordinator.
        
        Args:
            agent_name: Name of the agent
            capabilities: List of agent capabilities
            
        Returns:
            Agent registration information
        """
        agent_id = f"agent_{agent_name}_{uuid4().hex[:6]}"
        
        agent_info = {
            "id": agent_id,
            "name": agent_name,
            "capabilities": capabilities or [],
            "registered_at": time.time(),
            "status": "available",
            "current_task": None,
            "task_history": []
        }
        
        self.agent_status[agent_id] = agent_info
        
        # Create communication channel for this agent
        self.communication_channels[agent_id] = asyncio.Queue()
        
        # Create concurrency lock for this agent
        self.locks[agent_id] = asyncio.Lock()
        
        # Record in state store
        if self.state_store:
            self.state_store.register_agent(
                agent_id=agent_id,
                agent_type="component",
                metadata={"name": agent_name, "capabilities": capabilities}
            )
        
        self.logger.info(f"Registered agent: {agent_name} with ID {agent_id}")
        
        return {
            "agent_id": agent_id,
            "name": agent_name,
            "status": "available"
        }
    
    async def assign_task_to_agent(self, agent_id: str, task_id: str) -> Dict[str, Any]:
        """
        Assign a task to an agent.
        
        Args:
            agent_id: ID of the agent
            task_id: ID of the task
            
        Returns:
            Task assignment information
        """
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agent_status[agent_id]
        
        # Check if agent is available
        if agent["status"] != "available":
            raise ValueError(f"Agent {agent_id} is not available (current status: {agent['status']})")
        
        # Get the task from state store if available
        task = None
        if self.state_store:
            task = await self.state_store.get_task(task_id)
        
        # Update agent status
        agent["status"] = "busy"
        agent["current_task"] = task_id
        
        # Record assignment in state store
        if self.state_store:
            self.state_store.assign_task(task_id, agent_id)
        
        self.logger.info(f"Assigned task {task_id} to agent {agent_id}")
        
        # Add task to agent's message queue
        if task:
            await self.communication_channels[agent_id].put({
                "type": "task_assignment",
                "task_id": task_id,
                "task": task
            })
        
        return {
            "agent_id": agent_id,
            "task_id": task_id,
            "status": "assigned"
        }
    
    async def complete_agent_task(self, agent_id: str, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark an agent's task as completed.
        
        Args:
            agent_id: ID of the agent
            task_id: ID of the task
            result: Task result
            
        Returns:
            Task completion information
        """
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agent_status[agent_id]
        
        if agent["current_task"] != task_id:
            raise ValueError(f"Agent {agent_id} is not working on task {task_id}")
        
        # Update agent status
        agent["status"] = "available"
        agent["task_history"].append({
            "task_id": task_id,
            "completed_at": time.time(),
            "result": result
        })
        agent["current_task"] = None
        
        # Record completion in state store
        if self.state_store:
            self.state_store.record_task_result(task_id, result)
            self.state_store.update_task_status(task_id, "completed")
        
        self.logger.info(f"Agent {agent_id} completed task {task_id}")
        
        return {
            "agent_id": agent_id,
            "task_id": task_id,
            "status": "completed"
        }
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get status information for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent status information
        """
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agent_status[agent_id]
        
        return {
            "agent_id": agent_id,
            "name": agent["name"],
            "status": agent["status"],
            "current_task": agent["current_task"],
            "task_count": len(agent["task_history"]),
            "capabilities": agent["capabilities"]
        }
    
    async def send_message_to_agent(self, recipient_id: str, sender_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to an agent through its communication channel.
        
        Args:
            recipient_id: ID of the recipient agent
            sender_id: ID of the sender agent
            message: Message content
            
        Returns:
            Message delivery information
        """
        if recipient_id not in self.communication_channels:
            raise ValueError(f"Agent {recipient_id} not found or does not have a communication channel")
        
        message_with_metadata = {
            "sender_id": sender_id,
            "timestamp": time.time(),
            "message_id": uuid4().hex,
            "content": message
        }
        
        # Add to recipient's message queue
        await self.communication_channels[recipient_id].put(message_with_metadata)
        
        # Record in state store
        if self.state_store:
            self.state_store.record_agent_message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                message=message_with_metadata
            )
        
        self.logger.info(f"Sent message from {sender_id} to {recipient_id}")
        
        return {
            "message_id": message_with_metadata["message_id"],
            "status": "sent",
            "recipient": recipient_id
        }
    
    async def receive_messages(self, agent_id: str, timeout: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Receive all pending messages for an agent.
        
        Args:
            agent_id: ID of the agent
            timeout: Optional timeout in seconds
            
        Returns:
            List of pending messages
        """
        if agent_id not in self.communication_channels:
            raise ValueError(f"Agent {agent_id} not found or does not have a communication channel")
        
        messages = []
        channel = self.communication_channels[agent_id]
        
        try:
            # If timeout is None, get only already queued messages without waiting
            if timeout is None:
                while not channel.empty():
                    message = channel.get_nowait()
                    messages.append(message)
                    channel.task_done()
            else:
                # Wait for at least one message with timeout
                start_time = time.time()
                remaining_time = timeout
                
                while remaining_time > 0:
                    try:
                        message = await asyncio.wait_for(channel.get(), timeout=remaining_time)
                        messages.append(message)
                        channel.task_done()
                        
                        # Check if there are more messages without waiting
                        while not channel.empty():
                            message = channel.get_nowait()
                            messages.append(message)
                            channel.task_done()
                        
                        # Exit if we have at least one message
                        break
                        
                    except asyncio.TimeoutError:
                        # No messages within timeout
                        break
                    
                    # Update remaining time
                    remaining_time = timeout - (time.time() - start_time)
        
        except Exception as e:
            self.logger.error(f"Error receiving messages for agent {agent_id}: {str(e)}")
        
        self.logger.info(f"Received {len(messages)} messages for agent {agent_id}")
        
        return messages
    
    async def execute_workflow_command(self, command: str, subcommand: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow command.
        
        Args:
            command: Main command (e.g., 'session', 'feature')
            subcommand: Subcommand (e.g., 'start', 'end')
            args: Command arguments
            
        Returns:
            Command execution result
        """
        if command not in self.workflow_tools:
            raise ValueError(f"Unknown command: {command}")
        
        if subcommand not in self.workflow_tools[command]:
            raise ValueError(f"Unknown subcommand: {command} {subcommand}")
        
        # Execute the command handler
        handler = self.workflow_tools[command][subcommand]
        result = await handler(**args)
        
        return result
    
    async def coordinate_task_execution(self, task_id: str, workflow_phase: WorkflowPhase) -> Dict[str, Any]:
        """
        Coordinate task execution according to the workflow.
        
        Args:
            task_id: ID of the task to coordinate
            workflow_phase: Target workflow phase
            
        Returns:
            Coordination result
        """
        # Get task information
        task = None
        if self.state_store:
            task = await self.state_store.get_task(task_id)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Initialize workflow tracking if not exists
        if task_id not in self.workflow_status:
            self.workflow_status[task_id] = {
                "current_phase": WorkflowPhase.DISCOVERY,
                "phases_completed": set(),
                "phase_results": {},
                "start_time": time.time()
            }
        
        workflow = self.workflow_status[task_id]
        target_phase = workflow_phase
        
        # Get the phase progression path
        phases_to_execute = self._get_phases_to_execute(
            workflow["current_phase"], 
            target_phase
        )
        
        results = {}
        
        # Execute each phase in sequence
        for phase in phases_to_execute:
            phase_result = await self._execute_workflow_phase(task_id, phase)
            results[phase.name] = phase_result
            
            # Update workflow tracking
            workflow["current_phase"] = phase
            workflow["phases_completed"].add(phase)
            workflow["phase_results"][phase.name] = phase_result
        
        return {
            "task_id": task_id,
            "workflow_phases_executed": [p.name for p in phases_to_execute],
            "current_phase": workflow["current_phase"].name,
            "results": results
        }
    
    def _get_phases_to_execute(self, current_phase: WorkflowPhase, target_phase: WorkflowPhase) -> List[WorkflowPhase]:
        """
        Get the sequential phases to execute from current to target.
        
        Args:
            current_phase: Current workflow phase
            target_phase: Target workflow phase
            
        Returns:
            List of phases to execute in order
        """
        all_phases = list(WorkflowPhase)
        
        # Get indices
        current_idx = all_phases.index(current_phase)
        target_idx = all_phases.index(target_phase)
        
        # Ensure we're moving forward
        if target_idx < current_idx:
            return []
        
        # Return phases from current to target inclusive
        return all_phases[current_idx:target_idx+1]
    
    async def _execute_workflow_phase(self, task_id: str, phase: WorkflowPhase) -> Dict[str, Any]:
        """
        Execute a specific workflow phase for a task.
        
        Args:
            task_id: ID of the task
            phase: Workflow phase to execute
            
        Returns:
            Phase execution result
        """
        self.logger.info(f"Executing workflow phase {phase.name} for task {task_id}")
        
        # Phase-specific implementations
        if phase == WorkflowPhase.DISCOVERY:
            return await self._execute_discovery_phase(task_id)
        elif phase == WorkflowPhase.SPECIFICATION:
            return await self._execute_specification_phase(task_id)
        elif phase == WorkflowPhase.DESIGN:
            return await self._execute_design_phase(task_id)
        elif phase == WorkflowPhase.DEVELOPMENT:
            return await self._execute_development_phase(task_id)
        elif phase == WorkflowPhase.VERIFICATION:
            return await self._execute_verification_phase(task_id)
        elif phase == WorkflowPhase.INTEGRATION:
            return await self._execute_integration_phase(task_id)
        elif phase == WorkflowPhase.DEPLOYMENT:
            return await self._execute_deployment_phase(task_id)
        elif phase == WorkflowPhase.MONITORING:
            return await self._execute_monitoring_phase(task_id)
        elif phase == WorkflowPhase.IMPROVEMENT:
            return await self._execute_improvement_phase(task_id)
        elif phase == WorkflowPhase.RELEASE:
            return await self._execute_release_phase(task_id)
        else:
            raise ValueError(f"Unknown workflow phase: {phase}")
    
    async def _execute_discovery_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Discovery phase for a task."""
        # In a real implementation, this would:
        # 1. Analyze requirements in detail
        # 2. Identify existing components to leverage
        # 3. Define integration points
        # 4. Create user stories
        
        # Start a Pomodoro session for discovery if supervisor exists
        discovery_session = None
        if self.supervisor:
            discovery_session = await self.start_session(task_id, "discovery_agent")
        
        # For now, we'll simulate this phase
        return {
            "phase": "discovery",
            "task_id": task_id,
            "completed": True,
            "session_id": discovery_session["session_id"] if discovery_session else None,
            "artifacts": {
                "requirements_analysis": f"Requirements analysis for task {task_id}",
                "integration_points": ["point1", "point2"],
                "user_stories": ["story1", "story2"]
            }
        }
    
    async def _execute_specification_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Specification phase for a task."""
        # Implementation would create technical specifications,
        # define API contracts, and establish verification criteria
        return {
            "phase": "specification",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "technical_spec": f"Technical specification for task {task_id}",
                "api_contracts": ["contract1", "contract2"],
                "verification_criteria": ["criteria1", "criteria2"]
            }
        }
    
    async def _execute_design_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Design phase for a task."""
        # Implementation would create architecture design,
        # component structure, and data flow mapping
        return {
            "phase": "design",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "architecture_design": f"Architecture design for task {task_id}",
                "component_structure": ["component1", "component2"],
                "data_flow": ["flow1", "flow2"]
            }
        }
    
    async def _execute_development_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Development phase for a task."""
        # If we have a supervisor, delegate the actual implementation
        if self.supervisor:
            # Create a subtask for implementation
            implementation_task = Task(
                id=f"{task_id}_implementation",
                description=f"Implement the solution for task {task_id}",
                domain="development",
                parent_id=task_id
            )
            
            # Execute the task through the supervisor
            result = await self.supervisor.execute_task(implementation_task)
            
            return {
                "phase": "development",
                "task_id": task_id,
                "completed": result.status == "completed",
                "implementation_task_id": implementation_task.id,
                "implementation_result": result.to_dict()
            }
        else:
            # Simulated implementation
            return {
                "phase": "development",
                "task_id": task_id,
                "completed": True,
                "artifacts": {
                    "implementation": f"Implementation for task {task_id}",
                    "unit_tests": ["test1", "test2"],
                    "documentation": "API documentation"
                }
            }
    
    async def _execute_verification_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Verification phase for a task."""
        # Implementation would perform component testing, integration testing,
        # security validation, and performance testing
        return {
            "phase": "verification",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "component_tests": f"Component tests for task {task_id}",
                "integration_tests": ["test1", "test2"],
                "security_validation": "Security report",
                "performance_tests": "Performance report"
            }
        }
    
    async def _execute_integration_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Integration phase for a task."""
        # Implementation would handle system integration, cross-component testing,
        # API conformance testing, and error handling validation
        return {
            "phase": "integration",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "system_integration": f"Integration report for task {task_id}",
                "cross_component_tests": ["test1", "test2"],
                "api_conformance": "API conformance report",
                "error_handling": "Error handling report"
            }
        }
    
    async def _execute_deployment_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Deployment phase for a task."""
        # Implementation would prepare the environment, execute deployment,
        # perform health checks, and establish rollback procedures
        return {
            "phase": "deployment",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "environment_preparation": f"Environment preparation for task {task_id}",
                "deployment_execution": "Deployment log",
                "health_checks": ["check1", "check2"],
                "rollback_procedures": "Rollback documentation"
            }
        }
    
    async def _execute_monitoring_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Monitoring phase for a task."""
        # Implementation would set up metric collection, performance analysis,
        # error tracking, and usage monitoring
        return {
            "phase": "monitoring",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "metric_collection": f"Metrics configuration for task {task_id}",
                "performance_analysis": "Performance baseline",
                "error_tracking": "Error monitoring setup",
                "usage_monitoring": "Usage tracking configuration"
            }
        }
    
    async def _execute_improvement_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Improvement phase for a task."""
        # Implementation would analyze feedback, identify optimizations,
        # plan improvements, and update documentation
        return {
            "phase": "improvement",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "feedback_analysis": f"Feedback analysis for task {task_id}",
                "optimization_opportunities": ["opt1", "opt2"],
                "improvement_plan": "Improvement roadmap",
                "documentation_updates": "Updated documentation"
            }
        }
    
    async def _execute_release_phase(self, task_id: str) -> Dict[str, Any]:
        """Execute the Release phase for a task."""
        # Implementation would finalize version, create release notes,
        # update user documentation, and make component announcement
        return {
            "phase": "release",
            "task_id": task_id,
            "completed": True,
            "artifacts": {
                "version_finalization": f"Version finalization for task {task_id}",
                "release_notes": "Release notes content",
                "user_documentation": "Updated user documentation",
                "component_announcement": "Announcement message"
            }
        }
    
    async def verify_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Verify an agent's capabilities and knowledge.
        
        Args:
            agent_id: ID of the agent to verify
            
        Returns:
            Verification result
        """
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")
        
        # In a real implementation, this would:
        # 1. Run a trivia quiz about HMS architecture
        # 2. Test component understanding
        # 3. Ensure security advisory acknowledgment
        
        # For now, we'll simulate verification
        verification_token = f"verify_{uuid4().hex}"
        
        # Update agent status
        self.agent_status[agent_id]["verified"] = True
        self.agent_status[agent_id]["verification_token"] = verification_token
        self.agent_status[agent_id]["verification_expiry"] = time.time() + (30 * 24 * 60 * 60)  # 30 days
        
        return {
            "agent_id": agent_id,
            "verification_status": "verified",
            "verification_token": verification_token,
            "expiry": self.agent_status[agent_id]["verification_expiry"]
        }


# Factory function for creating coordinator
def create_coordinator(
    supervisor_agent = None,
    state_store: Optional[StateStore] = None,
    human_interface: Optional[HumanQueryInterface] = None,
    config_path: Optional[str] = None
) -> CoordinatorAgent:
    """
    Create and configure a Coordinator Agent.
    
    Args:
        supervisor_agent: Reference to the SupervisorAgent
        state_store: Environment/State Store for persistent memory
        human_interface: Human-in-the-loop interface
        config_path: Path to configuration file
        
    Returns:
        Configured CoordinatorAgent
    """
    # Load configuration if path provided
    config = {}
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading coordinator configuration: {str(e)}")
    
    # Create coordinator
    coordinator = CoordinatorAgent(
        name=config.get("name", "MAC-Coordinator"),
        supervisor_agent=supervisor_agent,
        state_store=state_store,
        human_interface=human_interface,
        config=config
    )
    
    # Register state store with coordinator reference if needed
    if state_store:
        state_store.register_coordinator(coordinator)
    
    return coordinator