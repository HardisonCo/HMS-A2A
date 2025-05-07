"""
Domain Agent Factory for the MAC architecture.

This module provides a factory class for creating domain agents
based on configuration and requirements.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from mac.domains.base import DomainAgent
from mac.domains.development import DevelopmentDomainAgent
from mac.domains.operations import OperationsDomainAgent
from mac.domains.governance import GovernanceDomainAgent
from mac.environment.state_store import StateStore
from mac.verification.checker import ExternalChecker
from mac.human_interface.interface import HumanQueryInterface


class DomainAgentFactory:
    """
    Factory for creating domain agent instances.
    
    This factory provides methods for creating and configuring domain agents
    of different types based on task requirements and configurations.
    
    Attributes:
        state_store: Reference to the shared state store
        external_checker: Reference to the external checker
        human_interface: Reference to the human query interface
    """
    
    def __init__(
        self,
        state_store: StateStore,
        external_checker: ExternalChecker,
        human_interface: HumanQueryInterface,
    ):
        """
        Initialize the domain agent factory.
        
        Args:
            state_store: Reference to the shared state store
            external_checker: Reference to the external checker
            human_interface: Reference to the human query interface
        """
        self.state_store = state_store
        self.external_checker = external_checker
        self.human_interface = human_interface
        self.logger = logging.getLogger("mac.domains.factory")
        
        # Register domain agent types
        self.agent_types = {
            "development": DevelopmentDomainAgent,
            "operations": OperationsDomainAgent,
            "governance": GovernanceDomainAgent,
        }
    
    async def create_domain_agent(
        self, domain_type: str, name: str, config: Optional[Dict[str, Any]] = None
    ) -> DomainAgent:
        """
        Create a domain agent of the specified type.
        
        Args:
            domain_type: Type of domain agent to create (development, operations, governance)
            name: Name for the domain agent
            config: Domain-specific configuration
            
        Returns:
            Configured domain agent instance
            
        Raises:
            ValueError: If the domain type is not supported
        """
        self.logger.info(f"Creating domain agent of type '{domain_type}' with name '{name}'")
        
        # Get the domain agent class
        agent_class = self.agent_types.get(domain_type.lower())
        if not agent_class:
            raise ValueError(f"Unsupported domain agent type: {domain_type}")
        
        # Create the domain agent instance
        agent = agent_class(
            name=name,
            state_store=self.state_store,
            external_checker=self.external_checker,
            human_interface=self.human_interface,
            config=config,
        )
        
        return agent
    
    async def create_all_domain_agents(
        self, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, DomainAgent]:
        """
        Create one instance of each domain agent type.
        
        Args:
            config: Configuration for domain agents, keyed by domain type
            
        Returns:
            Dictionary of domain agents keyed by type
        """
        self.logger.info("Creating all domain agent types")
        
        config = config or {}
        domain_agents = {}
        
        for domain_type, agent_class in self.agent_types.items():
            domain_config = config.get(domain_type, {})
            name = domain_config.pop("name", f"{domain_type}_agent")
            
            try:
                agent = await self.create_domain_agent(domain_type, name, domain_config)
                domain_agents[domain_type] = agent
                self.logger.info(f"Created {domain_type} domain agent: {name}")
            except Exception as e:
                self.logger.error(f"Failed to create {domain_type} domain agent: {str(e)}", exc_info=True)
        
        return domain_agents
    
    def register_domain_agent_type(
        self, domain_type: str, agent_class: Type[DomainAgent]
    ) -> None:
        """
        Register a new domain agent type with the factory.
        
        Args:
            domain_type: Type identifier for the domain agent
            agent_class: Domain agent class to register
            
        Raises:
            ValueError: If the domain type is already registered
        """
        if domain_type in self.agent_types:
            raise ValueError(f"Domain agent type already registered: {domain_type}")
        
        self.agent_types[domain_type] = agent_class
        self.logger.info(f"Registered new domain agent type: {domain_type}")
    
    async def get_domain_agent_capabilities(
        self, domain_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get capabilities of domain agents.
        
        Args:
            domain_type: Specific domain type to get capabilities for, or None for all
            
        Returns:
            Dictionary of domain agent capabilities keyed by domain type
        """
        capabilities = {}
        
        if domain_type:
            # Get capabilities for a specific domain type
            if domain_type not in self.agent_types:
                raise ValueError(f"Unknown domain agent type: {domain_type}")
            
            # Create a temporary instance to get capabilities
            agent = await self.create_domain_agent(domain_type, f"temp_{domain_type}_agent")
            capabilities[domain_type] = list(await agent.get_capabilities())
        else:
            # Get capabilities for all domain types
            for domain_type in self.agent_types:
                agent = await self.create_domain_agent(domain_type, f"temp_{domain_type}_agent")
                capabilities[domain_type] = list(await agent.get_capabilities())
        
        return capabilities