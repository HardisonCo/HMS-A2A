"""
MCP Integration Module

This module provides integration between the Government Agent system and the
Message Control Protocol (MCP) framework, allowing Government and Civilian
agents to be exposed as MCP tools.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Callable
import json
import os

from .base_agent import BaseAgent
from .government_agent import GovernmentAgent
from .civilian_agent import CivilianAgent
from .agency_registry import AgencyRegistry
from .agent_factory import AgentFactory

# Configure logging
logger = logging.getLogger(__name__)


class GovAgentMCPTool:
    """Base class for exposing government agents as MCP tools.
    
    This class wraps a government or civilian agent as an MCP tool,
    allowing it to be used within the MCP framework.
    """
    
    def __init__(
        self,
        agent: BaseAgent,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Initialize the MCP tool with a government agent.
        
        Args:
            agent: The government or civilian agent to wrap
            name: Optional name for the tool (defaults to agent name)
            description: Optional description (defaults to agent description)
        """
        self.agent = agent
        self.name = name or f"{agent.agency_label}_{agent.agent_type}_agent"
        self.description = description or f"{agent.agency_name} {agent.agent_type.capitalize()} Agent"
        
        # Set up tool metadata
        self.tool_metadata = {
            "toolName": self.name,
            "description": self.description,
            "parameters": {
                "query": {
                    "type": "string",
                    "description": f"The task or query to send to the {agent.agency_name} {agent.agent_type} agent"
                }
            },
            "returns": {
                "type": "object",
                "description": "Response from the agent"
            },
            "usage": {
                "example": f"Use this tool to interact with the {agent.agency_name} as a {agent.agent_type}."
            }
        }
    
    async def __call__(self, query: str) -> Dict[str, Any]:
        """Execute the tool with the given query.
        
        Args:
            query: The task or query to send to the agent
            
        Returns:
            Response from the agent
        """
        try:
            # Process the task through the agent
            response = await self.agent.process_task(query)
            
            # Format the response for MCP
            return {
                "status": "success",
                "response": response.response,
                "metadata": {
                    "agency": self.agent.agency_label,
                    "agent_type": self.agent.agent_type,
                    "task_id": response.task_id
                }
            }
        except Exception as e:
            logger.error(f"Error executing {self.name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "agency": self.agent.agency_label,
                    "agent_type": self.agent.agent_type
                }
            }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the MCP tool definition.
        
        Returns:
            Tool definition in MCP format
        """
        return self.tool_metadata


class GovernmentAgentMCPTool(GovAgentMCPTool):
    """MCP tool for government agency internal operations.
    
    This class wraps a GovernmentAgent as an MCP tool, providing
    internal agency functionality to authorized users.
    """
    
    def __init__(
        self,
        agent: GovernmentAgent,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Initialize with a government agent.
        
        Args:
            agent: The government agent to wrap
            name: Optional name for the tool
            description: Optional description
        """
        super().__init__(agent, name, description)
        
        # Add government-specific metadata
        self.tool_metadata["authRequired"] = True
        self.tool_metadata["accessLevel"] = "government"
        self.tool_metadata["internalOnly"] = True
        
        # Update parameters to include authentication
        self.tool_metadata["parameters"]["credentials"] = {
            "type": "object",
            "description": "Government credentials for authorization",
            "required": True
        }
    
    async def __call__(self, query: str, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the tool with the given query and credentials.
        
        Args:
            query: The task or query to send to the agent
            credentials: Optional credentials for authentication
            
        Returns:
            Response from the agent
        """
        try:
            # Validate credentials (placeholder - implement actual validation)
            if not credentials:
                return {
                    "status": "error",
                    "error": "Authentication required for government operations",
                    "metadata": {
                        "agency": self.agent.agency_label,
                        "agent_type": self.agent.agent_type
                    }
                }
            
            # Process the task through the agent
            response = await self.agent.process_task(query)
            
            # Format the response for MCP
            return {
                "status": "success",
                "response": response.response,
                "metadata": {
                    "agency": self.agent.agency_label,
                    "agent_type": self.agent.agent_type,
                    "task_id": response.task_id,
                    "clearance_level": credentials.get("clearance_level", "unspecified")
                }
            }
        except Exception as e:
            logger.error(f"Error executing {self.name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "agency": self.agent.agency_label,
                    "agent_type": self.agent.agent_type
                }
            }


class CivilianAgentMCPTool(GovAgentMCPTool):
    """MCP tool for civilian interaction with government agencies.
    
    This class wraps a CivilianAgent as an MCP tool, providing
    public-facing agency functionality to civilians.
    """
    
    def __init__(
        self,
        agent: CivilianAgent,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Initialize with a civilian agent.
        
        Args:
            agent: The civilian agent to wrap
            name: Optional name for the tool
            description: Optional description
        """
        super().__init__(agent, name, description)
        
        # Add civilian-specific metadata
        self.tool_metadata["authRequired"] = False
        self.tool_metadata["accessLevel"] = "public"
        self.tool_metadata["internalOnly"] = False
        
        # Update parameters for civilian context
        self.tool_metadata["parameters"]["user_info"] = {
            "type": "object",
            "description": "Optional user information for personalized responses",
            "required": False
        }
    
    async def __call__(self, query: str, user_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the tool with the given query and user info.
        
        Args:
            query: The task or query to send to the agent
            user_info: Optional user information for personalized responses
            
        Returns:
            Response from the agent
        """
        try:
            # Add user context if provided
            context = ""
            if user_info:
                context = f"User context: {json.dumps(user_info)}\n"
            
            # Process the task through the agent
            full_query = f"{context}{query}"
            response = await self.agent.process_task(full_query)
            
            # Format the response for MCP
            return {
                "status": "success",
                "response": response.response,
                "metadata": {
                    "agency": self.agent.agency_label,
                    "agent_type": self.agent.agent_type,
                    "task_id": response.task_id,
                    "public": True
                }
            }
        except Exception as e:
            logger.error(f"Error executing {self.name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "agency": self.agent.agency_label,
                    "agent_type": self.agent.agent_type
                }
            }


class GovAgentMCPRegistry:
    """Registry for government agent MCP tools.
    
    This class provides a central registry for managing MCP tools
    that wrap government and civilian agents.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a new instance if one doesn't exist."""
        if cls._instance is None:
            cls._instance = super(GovAgentMCPRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry (only done once)."""
        if not self._initialized:
            self._tools = {}  # type: Dict[str, GovAgentMCPTool]
            self._initialized = True
            logger.info("Government Agent MCP Registry initialized")
    
    def register_tool(self, tool: GovAgentMCPTool) -> bool:
        """Register a government agent MCP tool.
        
        Args:
            tool: The MCP tool to register
            
        Returns:
            Boolean indicating if registration was successful
        """
        tool_id = tool.name
        
        if tool_id in self._tools:
            logger.warning(f"Tool {tool_id} already registered, updating")
            
        self._tools[tool_id] = tool
        logger.info(f"Registered MCP tool: {tool_id}")
        
        return True
    
    def get_tool(self, tool_id: str) -> Optional[GovAgentMCPTool]:
        """Get a registered MCP tool.
        
        Args:
            tool_id: The ID of the tool to retrieve
            
        Returns:
            The registered MCP tool or None if not found
        """
        return self._tools.get(tool_id)
    
    def list_tools(self, access_level: str = "public") -> Dict[str, Dict[str, Any]]:
        """List all registered MCP tools matching the access level.
        
        Args:
            access_level: The access level to filter by ("public", "government", or "all")
            
        Returns:
            Dictionary of tool definitions
        """
        result = {}
        
        for tool_id, tool in self._tools.items():
            tool_def = tool.get_tool_definition()
            
            # Filter by access level
            if access_level == "all" or tool_def.get("accessLevel") == access_level:
                result[tool_id] = tool_def
        
        return result
    
    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister an MCP tool.
        
        Args:
            tool_id: The ID of the tool to unregister
            
        Returns:
            Boolean indicating if unregistration was successful
        """
        if tool_id in self._tools:
            del self._tools[tool_id]
            logger.info(f"Unregistered MCP tool: {tool_id}")
            return True
        else:
            logger.warning(f"Tool {tool_id} not found, nothing to unregister")
            return False


def register_all_agencies_as_mcp_tools() -> Dict[str, GovAgentMCPTool]:
    """Register all government and civilian agents as MCP tools.
    
    This function creates MCP tools for all available government
    and civilian agents and registers them with the MCP registry.
    
    Returns:
        Dictionary of registered MCP tools
    """
    registry = GovAgentMCPRegistry()
    agency_registry = AgencyRegistry()
    
    # Get all agencies
    agencies = agency_registry.list_agencies()
    registered_tools = {}
    
    for agency_data in agencies:
        agency_label = agency_data.get("agencyLabel")
        if not agency_label:
            continue
        
        # Create government agent tool
        gov_agent = agency_registry.get_government_agent(agency_label)
        if gov_agent:
            tool = GovernmentAgentMCPTool(gov_agent)
            registry.register_tool(tool)
            registered_tools[tool.name] = tool
        
        # Create civilian agent tool
        civilian_agent = agency_registry.get_civilian_agent(agency_label)
        if civilian_agent:
            tool = CivilianAgentMCPTool(civilian_agent)
            registry.register_tool(tool)
            registered_tools[tool.name] = tool
    
    logger.info(f"Registered {len(registered_tools)} MCP tools for government agencies")
    return registered_tools