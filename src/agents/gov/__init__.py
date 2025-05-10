"""
Government Agent System

This module provides a framework for managing government agency AI agents and civilian engagement.
"""

from .base_agent import BaseAgentInterface, BaseAgent
from .government_agent import GovernmentAgent
from .civilian_agent import CivilianAgent
from .agency_registry import AgencyRegistry
from .agent_factory import AgentFactory
from .data_loader import load_agency_data, get_agency_list
from .mcp_integration import (
    GovAgentMCPTool,
    GovernmentAgentMCPTool,
    CivilianAgentMCPTool,
    GovAgentMCPRegistry,
    register_all_agencies_as_mcp_tools
)


__all__ = [
    'BaseAgentInterface',
    'BaseAgent',
    'GovernmentAgent',
    'CivilianAgent',
    'AgencyRegistry',
    'AgentFactory',
    'load_agency_data',
    'get_agency_list',
    'GovAgentMCPTool',
    'GovernmentAgentMCPTool',
    'CivilianAgentMCPTool',
    'GovAgentMCPRegistry',
    'register_all_agencies_as_mcp_tools'
]