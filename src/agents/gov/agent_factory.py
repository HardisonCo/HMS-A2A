"""
Agent Factory

This module provides a factory for creating government agency agents.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from .base_agent import BaseAgent
from .government_agent import GovernmentAgent
from .civilian_agent import CivilianAgent
from .data_loader import load_agency_data, get_agency_list
from .agency_registry import AgencyRegistry

# Configure logging
logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating government agency agents.
    
    This class provides methods for creating different types of government
    agency agents based on the specified parameters and requirements.
    """
    
    @staticmethod
    def create_agent(
        agency_label: str,
        agent_type: str = "government",
        **kwargs
    ) -> Optional[BaseAgent]:
        """Create an agent for a specific agency.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            agent_type: The type of agent to create ("government" or "civilian")
            **kwargs: Additional parameters to pass to the agent constructor
            
        Returns:
            BaseAgent instance or None if creation failed
        """
        # Get registry to manage agent lifecycle
        registry = AgencyRegistry()
        
        # First, try to get an existing agent from the registry
        agent = registry.get_agent(agency_label, agent_type)
        if agent:
            logger.info(f"Retrieved existing {agent_type} agent for {agency_label}")
            return agent
        
        # If registry couldn't create it, we'll try manually
        logger.info(f"Creating new {agent_type} agent for {agency_label} with custom parameters")
        
        # Load agency data
        agency_data = load_agency_data(agency_label)
        if not agency_data:
            logger.error(f"No data found for agency {agency_label}")
            return None
        
        # Set required parameters
        params = {
            "agency_label": agency_label,
            "agency_name": agency_data.get("agencyName", agency_label),
            "domain": agency_data.get("domain", "government"),
            "supported_standards": agency_data.get("supportedStandards", [])
        }
        
        # Update with custom parameters
        params.update(kwargs)
        
        # Create the appropriate agent type
        try:
            if agent_type.lower() == "government":
                agent = GovernmentAgent(**params)
            elif agent_type.lower() == "civilian":
                agent = CivilianAgent(**params)
            else:
                logger.error(f"Unknown agent type: {agent_type}")
                return None
                
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create {agent_type} agent for {agency_label}: {e}")
            return None
    
    @staticmethod
    def create_government_agent(
        agency_label: str,
        **kwargs
    ) -> Optional[GovernmentAgent]:
        """Create a government agent for a specific agency.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            **kwargs: Additional parameters to pass to the agent constructor
            
        Returns:
            GovernmentAgent instance or None if creation failed
        """
        agent = AgentFactory.create_agent(agency_label, "government", **kwargs)
        return agent if isinstance(agent, GovernmentAgent) else None
    
    @staticmethod
    def create_civilian_agent(
        agency_label: str,
        **kwargs
    ) -> Optional[CivilianAgent]:
        """Create a civilian agent for a specific agency.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            **kwargs: Additional parameters to pass to the agent constructor
            
        Returns:
            CivilianAgent instance or None if creation failed
        """
        agent = AgentFactory.create_agent(agency_label, "civilian", **kwargs)
        return agent if isinstance(agent, CivilianAgent) else None
    
    @staticmethod
    def create_all_government_agents() -> Dict[str, GovernmentAgent]:
        """Create government agents for all available agencies.
        
        Returns:
            Dictionary of created government agents
        """
        agencies = get_agency_list()
        agents = {}
        
        for agency_data in agencies:
            agency_label = agency_data.get("agencyLabel")
            if not agency_label:
                continue
                
            agent = AgentFactory.create_government_agent(agency_label)
            if agent:
                agents[agency_label] = agent
        
        logger.info(f"Created {len(agents)} government agents")
        return agents
    
    @staticmethod
    def create_all_civilian_agents() -> Dict[str, CivilianAgent]:
        """Create civilian agents for all available agencies.
        
        Returns:
            Dictionary of created civilian agents
        """
        agencies = get_agency_list()
        agents = {}
        
        for agency_data in agencies:
            agency_label = agency_data.get("agencyLabel")
            if not agency_label:
                continue
                
            agent = AgentFactory.create_civilian_agent(agency_label)
            if agent:
                agents[agency_label] = agent
        
        logger.info(f"Created {len(agents)} civilian agents")
        return agents