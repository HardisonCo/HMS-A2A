"""
Specialized Agent Registry

This module provides a registry for all specialized standards-compliant agents.
"""

from typing import Dict, Any, List, Type, Optional
from src.agents.specialized import StandardsCompliantAgent


class AgentRegistry:
    """Registry for specialized standards-compliant agents."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern for the registry."""
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the registry."""
        self.agents = {}
        self.agent_classes = {}
    
    def register_agent_class(self, domain: str, agent_class: Type[StandardsCompliantAgent]) -> None:
        """Register an agent class for a specific domain.
        
        Args:
            domain: The industry domain (e.g., "Agriculture")
            agent_class: The agent class to register
        """
        self.agent_classes[domain.lower()] = agent_class
    
    def create_agent(self, domain: str, job_role: str, port: Optional[int] = None) -> StandardsCompliantAgent:
        """Create and register an agent instance.
        
        Args:
            domain: The industry domain (e.g., "Agriculture")
            job_role: The specific job role within the domain
            port: Optional port number for the agent
            
        Returns:
            Instantiated agent
            
        Raises:
            ValueError: If no agent class is registered for the domain
        """
        domain_lower = domain.lower()
        agent_class = self.agent_classes.get(domain_lower)
        
        if not agent_class:
            raise ValueError(f"No agent class registered for domain: {domain}")
        
        # Create the agent
        agent = agent_class(job_role, port)
        
        # Register the agent instance
        agent_id = f"{domain_lower}_{job_role.lower().replace(' ', '_')}"
        self.agents[agent_id] = agent
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[StandardsCompliantAgent]:
        """Get a registered agent by ID.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            The agent instance, or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, StandardsCompliantAgent]:
        """Get all registered agents.
        
        Returns:
            Dictionary of all registered agents by ID
        """
        return self.agents
    
    def get_domain_agents(self, domain: str) -> Dict[str, StandardsCompliantAgent]:
        """Get all agents for a specific domain.
        
        Args:
            domain: The industry domain
            
        Returns:
            Dictionary of domain agents by ID
        """
        domain_lower = domain.lower()
        return {
            agent_id: agent 
            for agent_id, agent in self.agents.items() 
            if agent_id.startswith(domain_lower)
        }


# Register all available agent classes
def register_all_agent_classes():
    """Register all available specialized agent classes."""
    registry = AgentRegistry()
    
    # Import and register the Agriculture agent
    from src.agents.specialized.agriculture import AgricultureAgent
    registry.register_agent_class("agriculture", AgricultureAgent)
    
    # Import and register the Telemedicine agent
    from src.agents.specialized.telemedicine import TelemedicineAgent
    registry.register_agent_class("telemedicine", TelemedicineAgent)
    
    # Import and register the Nutrition agent
    from src.agents.specialized.nutrition import NutritionAgent
    registry.register_agent_class("nutrition", NutritionAgent)
    
    # Import and register the Financial Services agent
    from src.agents.specialized.financial import FinancialServicesAgent
    registry.register_agent_class("financial", FinancialServicesAgent)
    
    # Import and register the Accounting agent
    from src.agents.specialized.accounting import AccountingAgent
    registry.register_agent_class("accounting", AccountingAgent)
    
    # Import and register the Social Work agent
    from src.agents.specialized.socialwork import SocialWorkAgent
    registry.register_agent_class("socialwork", SocialWorkAgent)
    
    # Import and register the Government Administration agent
    from src.agents.specialized.government import GovernmentAdministrationAgent
    registry.register_agent_class("government", GovernmentAdministrationAgent)
    
    # Register government specialized agency agents
    from src.agents.specialized.government import (
        USADFAgent, CIAAgent, CFTCAgent, CFPBAgent, CPSCAgent, DNFSBAgent, 
        EEOCAgent
    )
    registry.register_agent_class("usadf", USADFAgent)
    registry.register_agent_class("cia", CIAAgent)
    registry.register_agent_class("cftc", CFTCAgent)
    registry.register_agent_class("cfpb", CFPBAgent)
    registry.register_agent_class("cpsc", CPSCAgent)
    registry.register_agent_class("dnfsb", DNFSBAgent)
    registry.register_agent_class("eeoc", EEOCAgent)
    
    # Add more domains as they become available
    # registry.register_agent_class("healthcare", HealthcareAgent)
    # etc.


# Initialize the registry at import time
register_all_agent_classes()