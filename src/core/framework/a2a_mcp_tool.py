"""
A2A MCP Tool for LangGraph Agent

This module provides a tool that connects to a generic A2A agent through the MCP protocol.
"""

import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, ClassVar
from langchain_core.tools import BaseTool
from pydantic import Field

from common.client.a2a_agent_manager import AgentManager
from common.client.a2a_mcp_client import Message, MessagePart, TaskSendParams


class A2AMCPTool(BaseTool):
    """Tool for connecting to generic A2A agents via MCP."""
    
    name: ClassVar[str] = "a2a_generic_agent"
    description: ClassVar[str] = """
    Use this tool to connect to and interact with generic A2A-compatible agents.
    Send natural language queries to agents that will process them and return results.
    
    Examples:
    - "Create a Python function that calculates the Fibonacci sequence"
    - "Write a JavaScript module for handling user authentication"
    - "Help me debug this error message: TypeError: Cannot read property 'length' of undefined"
    """
    
    agent_manager: Optional[AgentManager] = None
    
    def _init_agent_manager(self) -> AgentManager:
        """Initialize the agent manager if needed."""
        if not self.agent_manager:
            self.agent_manager = AgentManager()
            # Initialize connections (in synchronous context)
            asyncio.run(self.agent_manager.initialize())
        return self.agent_manager
    
    def _run(self, query: str) -> str:
        """Execute the tool with the given query."""
        manager = self._init_agent_manager()
        
        # Get clients
        clients = manager.get_all_clients()
        if not clients:
            return "No A2A agents are available. Please check your configuration."
        
        # Use the first available client
        client_id, client = next(iter(clients.items()))
        
        # Create a message
        message = Message(
            role="user",
            parts=[MessagePart(text=query)]
        )
        
        # Create a task
        task_id = str(uuid.uuid4())
        params = TaskSendParams(id=task_id, message=message)
        
        try:
            # Send the task and get the result
            task = asyncio.run(client.send_task(params))
            
            if not task:
                return "No response received from the A2A agent."
            
            # Check if there are artifacts
            if task.artifacts and len(task.artifacts) > 0:
                # Return the text from the first artifact
                return task.artifacts[0].parts[0].text
            
            # If no artifacts, return the status message if available
            if task.status and task.status.message:
                return task.status.message.parts[0].text
            
            # Last resort is to return the entire response as JSON
            return f"Received response: {json.dumps(task.model_dump(), indent=2)}"
            
        except Exception as e:
            return f"Error communicating with A2A agent: {str(e)}"