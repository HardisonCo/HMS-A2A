"""
MCP Tools Package

This package provides MCP-compliant tools for specialized agents, including:
- Tool Registry: Central registry for managing and discovering tools
- Tool Interfaces: Standard interfaces for creating MCP-compliant tools
- Deal Tools: Tools for creating and managing deals
- Collaboration Tools: Tools for facilitating agent collaboration
- Visualization Tools: Tools for visualizing deals and collaborations
"""

from .mcp_registry import (
    register_tool,
    get_tool,
    get_tools_for_domain,
    search_tools,
    execute_tool
)

from .tool_interface import (
    ToolCategory,
    ToolContext,
    BaseMCPTool,
    DomainTool,
    ValidationTool,
    CollaborationTool,
    create_tool,
    tool_decorator
)

__all__ = [
    # Registry functions
    "register_tool",
    "get_tool",
    "get_tools_for_domain",
    "search_tools",
    "execute_tool",
    
    # Tool interfaces
    "ToolCategory",
    "ToolContext",
    "BaseMCPTool",
    "DomainTool",
    "ValidationTool",
    "CollaborationTool",
    "create_tool",
    "tool_decorator"
]