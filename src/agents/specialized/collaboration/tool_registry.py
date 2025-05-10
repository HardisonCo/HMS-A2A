"""
MCP Tool Registry

This module provides a registry for MCP-compliant tools and manages
collaboration sessions between specialized agents.
"""

from typing import Dict, Any, List, Optional, Type, Set, Union
from uuid import uuid4
import asyncio
import logging
from collections import defaultdict

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HumanFeedback(BaseModel):
    """Feedback from human reviewer."""
    
    approved: bool
    modifications: Dict[str, Any] = {}
    comments: Optional[str] = None
    reviewer_id: str


class PendingReview(BaseModel):
    """Information about a pending review."""
    
    id: str
    tool_name: str
    args: Dict[str, Any]
    preliminary_result: Any
    agent: str
    timestamp: str
    status: str = "pending"
    feedback: Optional[HumanFeedback] = None


class HITLManager:
    """Manager for human-in-the-loop reviews."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(HITLManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the HITL manager."""
        self.review_queue = {}
        self.review_callbacks = {}
    
    async def request_review(
        self,
        tool_name: str,
        args: Dict[str, Any],
        preliminary_result: Any,
        agent: str
    ) -> HumanFeedback:
        """Request a human review for a tool execution.
        
        Args:
            tool_name: Name of the tool being executed
            args: Tool arguments
            preliminary_result: Preliminary result from the tool
            agent: ID of the agent requesting review
            
        Returns:
            Human feedback once provided
        """
        request_id = str(uuid4())
        
        # Create the review request
        self.review_queue[request_id] = PendingReview(
            id=request_id,
            tool_name=tool_name,
            args=args,
            preliminary_result=preliminary_result,
            agent=agent,
            timestamp=asyncio.get_event_loop().time(),
            status="pending"
        )
        
        # Create a future that will be resolved when review is complete
        future = asyncio.Future()
        self.review_callbacks[request_id] = future
        
        # Notify that a review is pending (this could be a webhook, email, etc.)
        self._notify_reviewers(request_id)
        
        # Wait for the review to be submitted
        feedback = await future
        return feedback
    
    def submit_review(self, request_id: str, feedback: HumanFeedback) -> None:
        """Submit a review for a pending request.
        
        Args:
            request_id: ID of the review request
            feedback: Human feedback
        
        Raises:
            ValueError: If no pending review with the given ID exists
        """
        if request_id not in self.review_callbacks:
            raise ValueError(f"No pending review found for ID {request_id}")
        
        # Update the review status
        review = self.review_queue.get(request_id)
        if review:
            review.status = "approved" if feedback.approved else "rejected"
            review.feedback = feedback
        
        # Resolve the future
        future = self.review_callbacks.pop(request_id)
        future.set_result(feedback)
    
    def get_pending_reviews(self) -> List[PendingReview]:
        """Get all pending reviews.
        
        Returns:
            List of pending reviews
        """
        return [
            review for review in self.review_queue.values()
            if review.status == "pending"
        ]
    
    def _notify_reviewers(self, request_id: str) -> None:
        """Notify reviewers of a pending review.
        
        Args:
            request_id: ID of the review request
        """
        # This would be implemented based on the notification mechanism
        # (e.g., email, Slack, dashboard update)
        logger.info(f"Review request {request_id} is pending")


class CollaborationSession:
    """Manages a collaboration session between multiple agents."""
    
    def __init__(
        self,
        session_id: str,
        participants: List[str],
        registry: 'MCPToolRegistry'
    ):
        """Initialize a collaboration session.
        
        Args:
            session_id: Unique ID for the session
            participants: List of participating agent IDs
            registry: Reference to the tool registry
        """
        self.id = session_id
        self.participants = participants
        self.registry = registry
        self.tools = {}
        self.shared_context = {}
        
        # Collect all tools available to any participant
        for domain in participants:
            agent_tools = registry.get_tools_for_agent(domain)
            for tool in agent_tools:
                self.tools[tool.name] = tool
    
    async def call_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        calling_agent: str
    ) -> Dict[str, Any]:
        """Call a tool within this collaboration session.
        
        Args:
            tool_name: Name of the tool to call
            args: Tool arguments
            calling_agent: ID of the calling agent
            
        Returns:
            Tool result
            
        Raises:
            ValueError: If the tool doesn't exist or the agent is not a participant
        """
        # Check if the tool exists
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not available in this collaboration session")
        
        # Check if the agent is a participant
        if calling_agent not in self.participants:
            raise ValueError(f"Agent '{calling_agent}' is not a participant in this collaboration session")
        
        # Enhance args with session context
        enhanced_args = {
            **args,
            "__session": {
                "id": self.id,
                "calling_agent": calling_agent,
                "shared_context": self._get_relevant_context(tool_name)
            }
        }
        
        # Call the tool
        tool = self.tools[tool_name]
        result = await tool(**enhanced_args)
        
        # Update shared context with tool result
        self._update_shared_context(tool_name, calling_agent, args, result)
        
        return result
    
    def _get_relevant_context(self, tool_name: str) -> Dict[str, Any]:
        """Get context data relevant to a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing relevant context data
        """
        # In a more sophisticated implementation, this would filter
        # the context based on the tool's needs
        return self.shared_context
    
    def _update_shared_context(
        self,
        tool_name: str,
        calling_agent: str,
        args: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Update the shared context with a tool result.
        
        Args:
            tool_name: Name of the tool that was called
            calling_agent: ID of the agent that called the tool
            args: Tool arguments
            result: Tool result
        """
        # Update the shared context with the tool result
        # This is a simple implementation; a more sophisticated one would
        # extract and structure the data more carefully
        
        # Record the tool execution
        if "tool_executions" not in self.shared_context:
            self.shared_context["tool_executions"] = []
        
        self.shared_context["tool_executions"].append({
            "tool": tool_name,
            "agent": calling_agent,
            "args": args,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Extract data from the result
        for part in result:
            if part.get("type") == "data" and "data" in part:
                # Add the data to the shared context under the tool name
                self.shared_context[tool_name] = part["data"]


class MCPToolRegistry:
    """Registry for MCP-compliant tools."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(MCPToolRegistry, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the registry."""
        self.tools = {}
        self.agent_access_map = defaultdict(set)
        self.collaboration_sessions = {}
        self.hitl_manager = HITLManager()
    
    def register_tool(
        self,
        tool,
        allowed_agent_domains: List[str] = ["*"]
    ) -> None:
        """Register a tool with the registry.
        
        Args:
            tool: The tool to register
            allowed_agent_domains: List of agent domains allowed to use this tool
        """
        self.tools[tool.name] = tool
        
        # Set up access controls
        for domain in allowed_agent_domains:
            self.agent_access_map[domain].add(tool.name)
    
    def get_tools_for_agent(self, agent_domain: str) -> List[Any]:
        """Get tools available to a specific agent domain.
        
        Args:
            agent_domain: The agent domain
            
        Returns:
            List of available tools
        """
        tool_names = set()
        
        # Get domain-specific tools
        if agent_domain in self.agent_access_map:
            tool_names.update(self.agent_access_map[agent_domain])
        
        # Get universal tools
        if "*" in self.agent_access_map:
            tool_names.update(self.agent_access_map["*"])
        
        # Return tool instances
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def create_collaboration_session(
        self,
        session_id: str,
        agent_domains: List[str]
    ) -> CollaborationSession:
        """Create a collaboration session between multiple agents.
        
        Args:
            session_id: Unique ID for the session
            agent_domains: List of participating agent domains
            
        Returns:
            The created collaboration session
        """
        session = CollaborationSession(session_id, agent_domains, self)
        self.collaboration_sessions[session_id] = session
        return session
    
    def get_collaboration_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get an existing collaboration session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            The collaboration session, or None if it doesn't exist
        """
        return self.collaboration_sessions.get(session_id)
    
    def get_hitl_manager(self) -> HITLManager:
        """Get the HITL manager.
        
        Returns:
            The HITL manager
        """
        return self.hitl_manager