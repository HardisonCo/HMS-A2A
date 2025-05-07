#!/usr/bin/env python3
"""
MCP-Compliant Collaboration Tools

This module provides MCP-compliant tools for facilitating collaboration between
specialized agents, including session management, context sharing, and coordination.
"""

import os
import sys
import json
import uuid
import logging
from typing import Dict, List, Any, Optional, Union, Set
from pydantic import BaseModel, Field
from datetime import datetime
import networkx as nx
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specialized_agents.tools.tool_interface import (
    tool_decorator, 
    ToolCategory,
    ToolContext,
    BaseMCPTool,
    CollaborationTool
)

# Configure logging
logger = logging.getLogger(__name__)


class SessionStatus(str, Enum):
    """Status of a collaboration session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionCreateInput(BaseModel):
    """Input schema for creating a collaboration session."""
    name: str
    description: str
    participants: List[str]
    domains: List[str]
    initial_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionInviteInput(BaseModel):
    """Input schema for inviting a participant to a session."""
    session_id: str
    participant: str
    role: str
    message: Optional[str] = None


class MessageInput(BaseModel):
    """Input schema for sending a message in a session."""
    session_id: str
    sender: str
    content: str
    message_type: str = "text"
    recipients: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class ContextUpdateInput(BaseModel):
    """Input schema for updating shared context in a session."""
    session_id: str
    updater: str
    context_key: str
    context_value: Any
    visibility: str = "all"  # "all" or specific domains


class SessionEndInput(BaseModel):
    """Input schema for ending a collaboration session."""
    session_id: str
    ended_by: str
    summary: Optional[str] = None
    outcomes: Optional[List[Dict[str, Any]]] = None
    status: SessionStatus = SessionStatus.COMPLETED


# Global session store - in a real implementation, this would be a database
_sessions: Dict[str, Dict[str, Any]] = {}
_session_messages: Dict[str, List[Dict[str, Any]]] = {}
_session_contexts: Dict[str, Dict[str, Any]] = {}
_session_participants: Dict[str, Set[str]] = {}


@tool_decorator(
    name="create_collaboration_session",
    description="Create a new collaboration session between specialized agents",
    tool_type="collaboration",
    collaboration_type="session_management",
    domains=["agent_collaboration"],
    standards=["CollaborationFramework"],
    tags=["collaboration", "session", "creation"],
    require_human_review=False
)
def create_collaboration_session(
    name: str,
    description: str,
    participants: List[str],
    domains: List[str],
    initial_context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Create a new collaboration session between specialized agents.
    
    Args:
        name: Name of the session
        description: Description of the session purpose
        participants: List of participating domain agents
        domains: Domains related to the collaboration
        initial_context: Initial shared context (optional)
        metadata: Additional metadata (optional)
        context: Tool execution context
        
    Returns:
        Session details including ID
    """
    session_id = str(uuid.uuid4())
    
    # Create session
    session = {
        "id": session_id,
        "name": name,
        "description": description,
        "participants": participants,
        "domains": domains,
        "status": SessionStatus.ACTIVE.value,
        "created_at": datetime.now().isoformat(),
        "created_by": context.calling_domain if context else "unknown",
        "metadata": metadata or {},
        "last_activity": datetime.now().isoformat()
    }
    
    # Store session
    _sessions[session_id] = session
    _session_participants[session_id] = set(participants)
    
    # Initialize message list
    _session_messages[session_id] = []
    
    # Initialize shared context
    _session_contexts[session_id] = initial_context or {}
    
    # Add system message about session creation
    system_message = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "sender": "system",
        "content": f"Collaboration session '{name}' created",
        "message_type": "system",
        "timestamp": datetime.now().isoformat(),
        "visibility": "all"
    }
    _session_messages[session_id].append(system_message)
    
    return {
        "session_id": session_id,
        "name": name,
        "description": description,
        "participants": participants,
        "domains": domains,
        "status": SessionStatus.ACTIVE.value,
        "created_at": session["created_at"],
        "initial_context": _session_contexts[session_id]
    }


@tool_decorator(
    name="invite_participant",
    description="Invite a new participant to an existing collaboration session",
    tool_type="collaboration",
    collaboration_type="session_management",
    domains=["agent_collaboration"],
    standards=["CollaborationFramework"],
    tags=["collaboration", "session", "invitation"],
    require_human_review=False
)
def invite_participant(
    session_id: str,
    participant: str,
    role: str,
    message: Optional[str] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Invite a new participant to an existing collaboration session.
    
    Args:
        session_id: ID of the collaboration session
        participant: Domain or identifier of the participant to invite
        role: Role of the participant in the session
        message: Optional message to the invited participant
        context: Tool execution context
        
    Returns:
        Updated session details
        
    Raises:
        ValueError: If the session doesn't exist or is not active
    """
    # Check if session exists
    if session_id not in _sessions:
        raise ValueError(f"Session with ID {session_id} not found")
    
    # Get session
    session = _sessions[session_id]
    
    # Check session status
    if session["status"] != SessionStatus.ACTIVE.value:
        raise ValueError(f"Cannot invite participants to a session with status {session['status']}")
    
    # Check if participant is already in the session
    if participant in _session_participants[session_id]:
        raise ValueError(f"Participant {participant} is already in the session")
    
    # Add participant
    session["participants"].append(participant)
    _session_participants[session_id].add(participant)
    
    # Add system message about invitation
    system_message = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "sender": "system",
        "content": f"Participant {participant} invited to the session with role: {role}",
        "message_type": "system",
        "timestamp": datetime.now().isoformat(),
        "visibility": "all"
    }
    _session_messages[session_id].append(system_message)
    
    # Add welcome message if provided
    if message:
        welcome_message = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "sender": context.calling_domain if context else "system",
            "content": message,
            "message_type": "text",
            "timestamp": datetime.now().isoformat(),
            "recipients": [participant],
            "visibility": "private"
        }
        _session_messages[session_id].append(welcome_message)
    
    # Update last activity
    session["last_activity"] = datetime.now().isoformat()
    
    return {
        "session_id": session_id,
        "participant": participant,
        "role": role,
        "status": "invited",
        "timestamp": datetime.now().isoformat()
    }


@tool_decorator(
    name="send_message",
    description="Send a message to participants in a collaboration session",
    tool_type="collaboration",
    collaboration_type="communication",
    domains=["agent_collaboration"],
    standards=["CollaborationFramework"],
    tags=["collaboration", "message", "communication"],
    require_human_review=False
)
def send_message(
    session_id: str,
    sender: str,
    content: str,
    message_type: str = "text",
    recipients: Optional[List[str]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Send a message to participants in a collaboration session.
    
    Args:
        session_id: ID of the collaboration session
        sender: Domain or identifier of the message sender
        content: Message content
        message_type: Type of message (text, data, system, etc.)
        recipients: Optional list of specific recipients (default: all participants)
        attachments: Optional list of attachments
        context: Tool execution context
        
    Returns:
        Message details
        
    Raises:
        ValueError: If the session doesn't exist or is not active
    """
    # Check if session exists
    if session_id not in _sessions:
        raise ValueError(f"Session with ID {session_id} not found")
    
    # Get session
    session = _sessions[session_id]
    
    # Check session status
    if session["status"] != SessionStatus.ACTIVE.value:
        raise ValueError(f"Cannot send messages to a session with status {session['status']}")
    
    # Verify sender is a participant
    if sender not in _session_participants[session_id]:
        raise ValueError(f"Sender {sender} is not a participant in the session")
    
    # Determine visibility
    visibility = "private" if recipients else "all"
    
    # Create message
    message_id = str(uuid.uuid4())
    message = {
        "id": message_id,
        "session_id": session_id,
        "sender": sender,
        "content": content,
        "message_type": message_type,
        "timestamp": datetime.now().isoformat(),
        "recipients": recipients,
        "attachments": attachments,
        "visibility": visibility
    }
    
    # Add message to session
    _session_messages[session_id].append(message)
    
    # Update last activity
    session["last_activity"] = datetime.now().isoformat()
    
    return {
        "message_id": message_id,
        "session_id": session_id,
        "sender": sender,
        "timestamp": message["timestamp"],
        "recipients": recipients,
        "status": "sent"
    }


@tool_decorator(
    name="update_shared_context",
    description="Update the shared context in a collaboration session",
    tool_type="collaboration",
    collaboration_type="context_management",
    domains=["agent_collaboration"],
    standards=["CollaborationFramework"],
    tags=["collaboration", "context", "sharing"],
    require_human_review=False
)
def update_shared_context(
    session_id: str,
    updater: str,
    context_key: str,
    context_value: Any,
    visibility: str = "all",
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Update the shared context in a collaboration session.
    
    Args:
        session_id: ID of the collaboration session
        updater: Domain or identifier of the agent updating the context
        context_key: Key for the context value
        context_value: Value to store in the context
        visibility: Visibility of the update ("all" or specific domains)
        context: Tool execution context
        
    Returns:
        Updated context details
        
    Raises:
        ValueError: If the session doesn't exist or is not active
    """
    # Check if session exists
    if session_id not in _sessions:
        raise ValueError(f"Session with ID {session_id} not found")
    
    # Get session
    session = _sessions[session_id]
    
    # Check session status
    if session["status"] != SessionStatus.ACTIVE.value:
        raise ValueError(f"Cannot update context in a session with status {session['status']}")
    
    # Verify updater is a participant
    if updater not in _session_participants[session_id]:
        raise ValueError(f"Updater {updater} is not a participant in the session")
    
    # Get session context
    session_context = _session_contexts[session_id]
    
    # Create context update
    if visibility == "all":
        # Update for all participants
        session_context[context_key] = context_value
    else:
        # Update for specific domains
        if "domain_specific" not in session_context:
            session_context["domain_specific"] = {}
        
        if visibility not in session_context["domain_specific"]:
            session_context["domain_specific"][visibility] = {}
        
        session_context["domain_specific"][visibility][context_key] = context_value
    
    # Add system message about context update
    system_message = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "sender": "system",
        "content": f"Shared context updated by {updater}: {context_key}",
        "message_type": "system",
        "timestamp": datetime.now().isoformat(),
        "visibility": visibility
    }
    _session_messages[session_id].append(system_message)
    
    # Update last activity
    session["last_activity"] = datetime.now().isoformat()
    
    return {
        "session_id": session_id,
        "updater": updater,
        "context_key": context_key,
        "visibility": visibility,
        "timestamp": datetime.now().isoformat(),
        "status": "updated"
    }


@tool_decorator(
    name="get_session_context",
    description="Get the current shared context from a collaboration session",
    tool_type="collaboration",
    collaboration_type="context_management",
    domains=["agent_collaboration"],
    standards=["CollaborationFramework"],
    tags=["collaboration", "context", "retrieval"],
    require_human_review=False
)
def get_session_context(
    session_id: str,
    requester: str,
    context_key: Optional[str] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Get the current shared context from a collaboration session.
    
    Args:
        session_id: ID of the collaboration session
        requester: Domain or identifier of the agent requesting the context
        context_key: Optional specific context key to retrieve
        context: Tool execution context
        
    Returns:
        Session context
        
    Raises:
        ValueError: If the session doesn't exist
    """
    # Check if session exists
    if session_id not in _sessions:
        raise ValueError(f"Session with ID {session_id} not found")
    
    # Verify requester is a participant
    if requester not in _session_participants[session_id]:
        raise ValueError(f"Requester {requester} is not a participant in the session")
    
    # Get session context
    session_context = _session_contexts[session_id]
    
    # Filter to specific key if requested
    if context_key:
        if context_key in session_context:
            return {
                "session_id": session_id,
                "context": {context_key: session_context[context_key]},
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "session_id": session_id,
                "context": {},
                "error": f"Context key '{context_key}' not found",
                "timestamp": datetime.now().isoformat()
            }
    
    # Get domain-specific context
    domain_specific = {}
    if "domain_specific" in session_context and requester in session_context["domain_specific"]:
        domain_specific = session_context["domain_specific"][requester]
    
    # Combine general and domain-specific context
    combined_context = {
        k: v for k, v in session_context.items() 
        if k != "domain_specific"
    }
    combined_context.update(domain_specific)
    
    return {
        "session_id": session_id,
        "context": combined_context,
        "timestamp": datetime.now().isoformat()
    }


@tool_decorator(
    name="get_session_messages",
    description="Get messages from a collaboration session",
    tool_type="collaboration",
    collaboration_type="communication",
    domains=["agent_collaboration"],
    standards=["CollaborationFramework"],
    tags=["collaboration", "message", "retrieval"],
    require_human_review=False
)
def get_session_messages(
    session_id: str,
    requester: str,
    limit: int = 20,
    before_timestamp: Optional[str] = None,
    after_timestamp: Optional[str] = None,
    from_sender: Optional[str] = None,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Get messages from a collaboration session.
    
    Args:
        session_id: ID of the collaboration session
        requester: Domain or identifier of the agent requesting messages
        limit: Maximum number of messages to return
        before_timestamp: Only return messages before this timestamp
        after_timestamp: Only return messages after this timestamp
        from_sender: Only return messages from this sender
        context: Tool execution context
        
    Returns:
        List of messages
        
    Raises:
        ValueError: If the session doesn't exist
    """
    # Check if session exists
    if session_id not in _sessions:
        raise ValueError(f"Session with ID {session_id} not found")
    
    # Verify requester is a participant
    if requester not in _session_participants[session_id]:
        raise ValueError(f"Requester {requester} is not a participant in the session")
    
    # Get messages
    all_messages = _session_messages[session_id]
    
    # Filter messages
    filtered_messages = []
    for message in all_messages:
        # Check visibility
        visibility = message.get("visibility", "all")
        recipients = message.get("recipients", [])
        
        if visibility == "private" and requester not in recipients and message.get("sender") != requester:
            continue
        
        # Check timestamps
        timestamp = message.get("timestamp", "")
        if before_timestamp and timestamp > before_timestamp:
            continue
        if after_timestamp and timestamp < after_timestamp:
            continue
        
        # Check sender
        if from_sender and message.get("sender") != from_sender:
            continue
        
        filtered_messages.append(message)
    
    # Sort messages by timestamp
    filtered_messages.sort(key=lambda m: m.get("timestamp", ""))
    
    # Apply limit
    limited_messages = filtered_messages[-limit:] if limit > 0 else filtered_messages
    
    return {
        "session_id": session_id,
        "messages": limited_messages,
        "count": len(limited_messages),
        "timestamp": datetime.now().isoformat()
    }


@tool_decorator(
    name="end_session",
    description="End a collaboration session",
    tool_type="collaboration",
    collaboration_type="session_management",
    domains=["agent_collaboration"],
    standards=["CollaborationFramework"],
    tags=["collaboration", "session", "end"],
    require_human_review=True
)
def end_session(
    session_id: str,
    ended_by: str,
    summary: Optional[str] = None,
    outcomes: Optional[List[Dict[str, Any]]] = None,
    status: str = SessionStatus.COMPLETED.value,
    context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    End a collaboration session.
    
    Args:
        session_id: ID of the collaboration session
        ended_by: Domain or identifier of the agent ending the session
        summary: Optional summary of the session
        outcomes: Optional list of session outcomes
        status: Final status of the session
        context: Tool execution context
        
    Returns:
        Final session details
        
    Raises:
        ValueError: If the session doesn't exist or is already completed
    """
    # Check if session exists
    if session_id not in _sessions:
        raise ValueError(f"Session with ID {session_id} not found")
    
    # Get session
    session = _sessions[session_id]
    
    # Check session status
    if session["status"] in [SessionStatus.COMPLETED.value, SessionStatus.FAILED.value]:
        raise ValueError(f"Session is already in final state: {session['status']}")
    
    # Verify requester is a participant
    if ended_by not in _session_participants[session_id]:
        raise ValueError(f"Agent {ended_by} is not a participant in the session")
    
    # Update session status
    session["status"] = status
    session["ended_at"] = datetime.now().isoformat()
    session["ended_by"] = ended_by
    
    if summary:
        session["summary"] = summary
    
    if outcomes:
        session["outcomes"] = outcomes
    
    # Add system message about session end
    system_message = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "sender": "system",
        "content": f"Session ended by {ended_by} with status: {status}",
        "message_type": "system",
        "timestamp": datetime.now().isoformat(),
        "visibility": "all"
    }
    _session_messages[session_id].append(system_message)
    
    # Prepare result
    result = {
        "session_id": session_id,
        "name": session["name"],
        "status": status,
        "ended_by": ended_by,
        "ended_at": session["ended_at"],
        "duration": _calculate_duration(session["created_at"], session["ended_at"]),
        "participants": list(_session_participants[session_id]),
        "message_count": len(_session_messages[session_id])
    }
    
    if summary:
        result["summary"] = summary
    
    if outcomes:
        result["outcomes"] = outcomes
    
    return result


def _calculate_duration(start_time: str, end_time: str) -> str:
    """
    Calculate the duration between two ISO format timestamps.
    
    Args:
        start_time: Start timestamp in ISO format
        end_time: End timestamp in ISO format
        
    Returns:
        Duration as a formatted string
    """
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    duration = end - start
    
    # Format duration
    seconds = duration.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"


class CollaborationToolsRegistry:
    """Registry of MCP-compliant collaboration tools."""
    
    @staticmethod
    def register_tools():
        """Register all collaboration tools with the MCP Tool Registry."""
        from specialized_agents.tools.mcp_registry import registry
        
        # The tools are registered via decorators, but we can explicitly add them here if needed
        # Additional initialization can be done here
        
        logger.info("Collaboration tools registered with MCP Tool Registry")
        
        # Return list of registered tool names
        return [
            "create_collaboration_session",
            "invite_participant",
            "send_message",
            "update_shared_context",
            "get_session_context",
            "get_session_messages",
            "end_session"
        ]


# Register tools when module is imported
CollaborationToolsRegistry.register_tools()