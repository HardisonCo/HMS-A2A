"""
HMS-A2A Specialized Agents

This module provides a framework for standards-compliant specialized agents
that can collaborate using the Deals framework and MCP tools.
"""

from .standards_validation import StandardsValidator, StandardsRegistry
from .mcp_registry import register_tool, get_registered_tools

# Import domain-specific modules
from . import healthcare
from . import agriculture
from . import financial
from . import government
from . import legal
from . import education
from . import collaboration

__all__ = [
    'StandardsValidator',
    'StandardsRegistry',
    'register_tool',
    'get_registered_tools',
    'healthcare',
    'agriculture',
    'financial',
    'government',
    'legal',
    'education',
    'collaboration'
]