"""
MCP Tools Registry

This module provides a registry for MCP-compliant tools that can be used by specialized
agents across different domains. It migrates the functionality from HMS-SME/lib/MCP.
"""

from typing import Dict, Any, List, Optional, Type, Union
import importlib
import logging

logger = logging.getLogger(__name__)


class MCPToolsRegistry:
    """Registry for MCP tools."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(MCPToolsRegistry, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the registry."""
        self.tools = {}
        self.domain_tools = {}
        self.tool_categories = {}
    
    def register_tool(
        self, 
        name: str, 
        tool_obj: Any, 
        domains: List[str],
        category: Optional[str] = None
    ) -> None:
        """Register a tool with the registry.
        
        Args:
            name: Tool name
            tool_obj: Tool object
            domains: List of domains this tool is available to
            category: Optional category for the tool
        """
        self.tools[name] = tool_obj
        
        # Register with domains
        for domain in domains:
            if domain not in self.domain_tools:
                self.domain_tools[domain] = []
            
            if name not in self.domain_tools[domain]:
                self.domain_tools[domain].append(name)
        
        # Register with category
        if category:
            if category not in self.tool_categories:
                self.tool_categories[category] = []
            
            if name not in self.tool_categories[category]:
                self.tool_categories[category].append(name)
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool object or None if not found
        """
        return self.tools.get(name)
    
    def get_tools_for_domain(self, domain: str) -> List[Any]:
        """Get tools for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of tool objects
        """
        tool_names = self.domain_tools.get(domain, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_tools_by_category(self, category: str) -> List[Any]:
        """Get tools by category.
        
        Args:
            category: Category name
            
        Returns:
            List of tool objects
        """
        tool_names = self.tool_categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_tool_definition(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tool definition by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool definition or None if not found
        """
        tool = self.get_tool(name)
        if tool is None:
            return None
        
        # If tool has a get_definition method, use it
        if hasattr(tool, "get_definition") and callable(tool.get_definition):
            return tool.get_definition()
        
        # Otherwise, build a basic definition
        schema = {}
        if hasattr(tool, "input_schema") and hasattr(tool.input_schema, "schema"):
            schema = tool.input_schema.schema()
        
        metadata = {}
        if hasattr(tool, "metadata"):
            metadata = tool.metadata
            if hasattr(metadata, "dict"):
                metadata = metadata.dict()
        
        return {
            "name": name,
            "description": getattr(tool, "description", ""),
            "schema": schema,
            "metadata": metadata
        }
    
    def load_tools_for_domain(self, domain: str) -> List[str]:
        """Load and register tools for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of tool names that were registered
        """
        # Try to import the domain-specific tools module
        try:
            module_name = f"specialized_agents.{domain.lower()}.tools"
            module = importlib.import_module(module_name)
            
            # Check if the module has a register function
            if hasattr(module, "register_tools") and callable(module.register_tools):
                return module.register_tools()
            
            logger.warning(f"No register_tools function found in {module_name}")
            return []
        except ImportError:
            logger.warning(f"No tools module found for domain {domain}")
            return []
        except Exception as e:
            logger.error(f"Error loading tools for domain {domain}: {e}")
            return []


# Create a singleton instance
registry = MCPToolsRegistry()


def load_all_domain_tools() -> Dict[str, List[str]]:
    """Load tools for all domains.
    
    Returns:
        Dictionary mapping domains to lists of tool names
    """
    # These are the domains we know about from HMS-SME
    domains = [
        "accounting",
        "agriculture",
        "educational",
        "financial",
        "government",
        "healthcare",
        "legal",
        "nutrition",
        "social_work",
        "technology"
    ]
    
    # Load tools for each domain
    result = {}
    for domain in domains:
        tools = registry.load_tools_for_domain(domain)
        if tools:
            result[domain] = tools
    
    return result


def get_tool(name: str) -> Optional[Any]:
    """Get a tool by name.
    
    Args:
        name: Tool name
        
    Returns:
        Tool object or None if not found
    """
    return registry.get_tool(name)


def get_tools_for_domain(domain: str) -> List[Any]:
    """Get tools for a specific domain.
    
    Args:
        domain: Domain name
        
    Returns:
        List of tool objects
    """
    return registry.get_tools_for_domain(domain)