"""
Agency Registry

This module provides a central registry for managing government agency agents.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import json
import os

from .base_agent import BaseAgent
from .government_agent import GovernmentAgent
from .civilian_agent import CivilianAgent
from .data_loader import load_agency_data, get_agency_list

# Configure logging
logger = logging.getLogger(__name__)


class AgencyRegistry:
    """Singleton registry for managing government agency agents.
    
    This class provides a central registry for creating, retrieving, and managing
    government agency agents. It follows the Singleton pattern to ensure only one
    registry exists in the application.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a new instance if one doesn't exist."""
        if cls._instance is None:
            cls._instance = super(AgencyRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry (only done once)."""
        if not self._initialized:
            self._government_agents = {}  # type: Dict[str, GovernmentAgent]
            self._civilian_agents = {}    # type: Dict[str, CivilianAgent]
            self._agency_data_cache = {}  # type: Dict[str, Dict[str, Any]]
            self._initialized = True
            logger.info("Agency Registry initialized")
    
    def get_government_agent(self, agency_label: str) -> Optional[GovernmentAgent]:
        """Get a government agent for a specific agency.
        
        If the agent doesn't exist, it will be created.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            
        Returns:
            GovernmentAgent instance or None if agency not found
        """
        # Check if we already have this agent
        if agency_label in self._government_agents:
            return self._government_agents[agency_label]
        
        # Load agency data
        agency_data = load_agency_data(agency_label)
        if not agency_data:
            logger.error(f"No data found for agency {agency_label}")
            return None
        
        # Create a new government agent
        try:
            agent = GovernmentAgent(
                agency_label=agency_label,
                agency_name=agency_data.get("agencyName", agency_label),
                domain=agency_data.get("domain", "government"),
                supported_standards=agency_data.get("supportedStandards", [])
            )
            
            # Store the agent in registry
            self._government_agents[agency_label] = agent
            logger.info(f"Created new government agent for {agency_label}")
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create government agent for {agency_label}: {e}")
            return None
    
    def get_civilian_agent(self, agency_label: str) -> Optional[CivilianAgent]:
        """Get a civilian agent for a specific agency.
        
        If the agent doesn't exist, it will be created.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            
        Returns:
            CivilianAgent instance or None if agency not found
        """
        # Check if we already have this agent
        if agency_label in self._civilian_agents:
            return self._civilian_agents[agency_label]
        
        # Load agency data
        agency_data = load_agency_data(agency_label)
        if not agency_data:
            logger.error(f"No data found for agency {agency_label}")
            return None
        
        # Create a new civilian agent
        try:
            agent = CivilianAgent(
                agency_label=agency_label,
                agency_name=agency_data.get("agencyName", agency_label),
                domain=agency_data.get("domain", "government"),
                supported_standards=agency_data.get("supportedStandards", [])
            )
            
            # Store the agent in registry
            self._civilian_agents[agency_label] = agent
            logger.info(f"Created new civilian agent for {agency_label}")
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create civilian agent for {agency_label}: {e}")
            return None
    
    def get_agent(self, agency_label: str, agent_type: str = "government") -> Optional[BaseAgent]:
        """Get an agent of the specified type for an agency.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            agent_type: The type of agent to retrieve ("government" or "civilian")
            
        Returns:
            BaseAgent instance or None if not found
        """
        if agent_type.lower() == "government":
            return self.get_government_agent(agency_label)
        elif agent_type.lower() == "civilian":
            return self.get_civilian_agent(agency_label)
        else:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
    
    def list_agencies(self) -> List[Dict[str, Any]]:
        """Get a list of available agencies.
        
        Returns:
            List of agency data dictionaries
        """
        return get_agency_list()
    
    def get_active_government_agents(self) -> Dict[str, GovernmentAgent]:
        """Get all active government agents.
        
        Returns:
            Dictionary of active government agents
        """
        return self._government_agents.copy()
    
    def get_active_civilian_agents(self) -> Dict[str, CivilianAgent]:
        """Get all active civilian agents.
        
        Returns:
            Dictionary of active civilian agents
        """
        return self._civilian_agents.copy()
    
    def shutdown_agent(self, agency_label: str, agent_type: str = "both") -> bool:
        """Shutdown an agent and remove it from the registry.
        
        Args:
            agency_label: The agency identifier
            agent_type: The type of agent to shutdown ("government", "civilian", or "both")
            
        Returns:
            Boolean indicating if shutdown was successful
        """
        success = True
        
        if agent_type in ["government", "both"]:
            if agency_label in self._government_agents:
                try:
                    # Cleanup agent (in a real implementation, release resources)
                    agent = self._government_agents[agency_label]
                    # agent.shutdown()  # Implement if needed
                    
                    # Remove from registry
                    del self._government_agents[agency_label]
                    logger.info(f"Shutdown government agent for {agency_label}")
                except Exception as e:
                    logger.error(f"Error shutting down government agent for {agency_label}: {e}")
                    success = False
        
        if agent_type in ["civilian", "both"]:
            if agency_label in self._civilian_agents:
                try:
                    # Cleanup agent (in a real implementation, release resources)
                    agent = self._civilian_agents[agency_label]
                    # agent.shutdown()  # Implement if needed
                    
                    # Remove from registry
                    del self._civilian_agents[agency_label]
                    logger.info(f"Shutdown civilian agent for {agency_label}")
                except Exception as e:
                    logger.error(f"Error shutting down civilian agent for {agency_label}: {e}")
                    success = False
        
        return success
    
    def shutdown_all(self) -> bool:
        """Shutdown all agents and clear the registry.
        
        Returns:
            Boolean indicating if all shutdowns were successful
        """
        success = True
        
        # Get all agency labels
        agency_labels = set(list(self._government_agents.keys()) + list(self._civilian_agents.keys()))
        
        # Shutdown each agency
        for agency_label in agency_labels:
            if not self.shutdown_agent(agency_label, "both"):
                success = False
        
        return success
    
    # Cache management methods
    def clear_cache(self) -> None:
        """Clear the agency data cache."""
        self._agency_data_cache.clear()
        logger.info("Agency data cache cleared")