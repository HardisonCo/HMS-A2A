"""
Specialized Agent Tool for LangGraph Agent

This module provides a tool that connects to standards-compliant specialized agents.
"""

import uuid
from typing import ClassVar, Optional, Dict, Any, List
from langchain_core.tools import BaseTool
from pydantic import Field

from specialized_agents.registry import AgentRegistry


class SpecializedAgentTool(BaseTool):
    """Tool for connecting to specialized standards-compliant agents."""
    
    name: ClassVar[str] = "specialized_agent"
    description: ClassVar[str] = """
    Use this tool to interact with specialized industry-compliant agents.
    Send domain-specific queries to agents that will process them according to industry standards.
    
    Examples:
    - "Agriculture: What are the best organic pest management practices for tomatoes?"
    - "Agriculture: How should I apply fertilizer to my apple orchard while following USDA guidelines?"
    - "Agriculture: What are the proper safety protocols for pesticide application near water?"
    
    The query should start with the domain name followed by a colon and your specific question.
    """
    
    domain: Optional[str] = Field(None, description="Domain to route the query to (e.g., 'Agriculture')")
    job_role: Optional[str] = Field(None, description="Specific job role within the domain")
    session_id: Optional[str] = Field(None, description="Session ID for tracking conversations")
    
    def _init_session(self) -> str:
        """Initialize a session ID if it doesn't exist."""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        return self.session_id
    
    def _extract_domain_and_query(self, query: str) -> tuple[str, str]:
        """Extract the domain and the actual query from the input string.
        
        Args:
            query: Input string in format "Domain: query"
            
        Returns:
            Tuple of (domain, query)
        """
        parts = query.split(":", 1)
        if len(parts) == 2:
            domain = parts[0].strip()
            actual_query = parts[1].strip()
            return domain, actual_query
        
        # If no domain is specified, use the default domain if set
        if self.domain:
            return self.domain, query
        
        # If no domain is specified and no default, assume it's a general query
        return "general", query
    
    def _get_or_create_agent(self, domain: str) -> Any:
        """Get or create an agent for the specified domain.
        
        Args:
            domain: The domain to get an agent for
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If no agent is available for the domain
        """
        registry = AgentRegistry()
        
        # First try to find existing agents for this domain
        domain_agents = registry.get_domain_agents(domain)
        if domain_agents:
            # Return the first available agent
            return next(iter(domain_agents.values()))
        
        # If no agents exist, try to create one with default job role
        try:
            job_role = self.job_role or "Specialist"
            return registry.create_agent(domain, job_role)
        except ValueError as e:
            raise ValueError(f"No agent available for domain '{domain}': {str(e)}")
    
    def _run(self, query: str) -> str:
        """Execute the tool with the given query.
        
        Args:
            query: Query string in format "Domain: query"
            
        Returns:
            Agent response
        """
        domain, actual_query = self._extract_domain_and_query(query)
        session_id = self._init_session()
        
        try:
            # Get or create an agent for this domain
            agent = self._get_or_create_agent(domain)
            
            # Process the query through the appropriate validation and execution logic
            validation_result = agent.validateTask({"query": actual_query})
            
            if not validation_result.valid:
                issues = "\n".join([f"- {issue}" for issue in validation_result.issues])
                return f"""
                ⚠️ Your request could not be processed due to compliance issues:
                
                {issues}
                
                Please revise your query to comply with {domain} industry standards and regulations.
                """
            
            # In a real implementation, this would use the agent to process the query
            # For now, we'll simulate a response based on the domain
            if domain.lower() == "agriculture":
                return self._simulate_agriculture_response(actual_query, agent)
            else:
                return f"No specialized agent available for domain '{domain}'. Available domains: Agriculture"
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def _simulate_agriculture_response(self, query: str, agent: Any) -> str:
        """Simulate a response from an agriculture agent.
        
        In a real implementation, this would call the agent's process method.
        
        Args:
            query: The query to process
            agent: The agriculture agent instance
            
        Returns:
            Simulated agent response
        """
        # Check what standards might be relevant to this query
        standards = []
        if any(keyword in query.lower() for keyword in ["organic", "natural", "chemical-free"]):
            standards.append("ORGANIC_CERTIFICATION_REQUIREMENTS")
        
        if any(keyword in query.lower() for keyword in ["pesticide", "herbicide", "insecticide", "spray"]):
            standards.append("PESTICIDE_USAGE_GUIDELINES")
            standards.append("AGRICULTURAL_SAFETY_STANDARDS")
        
        if any(keyword in query.lower() for keyword in ["sustainable", "conservation", "rotation", "cover crop"]):
            standards.append("SUSTAINABLE_FARMING_PRACTICES")
        
        if any(keyword in query.lower() for keyword in ["food", "produce", "harvest", "storage", "contamination"]):
            standards.append("FOOD_SAFETY_REGULATIONS")
        
        if any(keyword in query.lower() for keyword in ["animal", "livestock", "welfare", "cattle", "poultry"]):
            standards.append("ANIMAL_WELFARE_STANDARDS")
        
        # Build a response that references relevant standards
        if standards:
            standards_text = ", ".join(standards)
            return f"""
            Based on your query about {query}, I've consulted the following standards: {standards_text}.
            
            According to these standards, here are the recommendations:
            
            1. [Simulated recommendation based on query and standards]
            2. [Simulated recommendation based on query and standards]
            3. [Simulated recommendation based on query and standards]
            
            These recommendations comply with all relevant USDA regulations and industry best practices.
            """
        else:
            return f"""
            I've analyzed your query about {query} according to general agricultural best practices.
            
            Here are my recommendations:
            
            1. [Simulated general recommendation]
            2. [Simulated general recommendation]
            3. [Simulated general recommendation]
            
            For more specific advice, please provide details about your specific agricultural context.
            """