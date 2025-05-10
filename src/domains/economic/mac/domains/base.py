"""
Base domain agent definition for the MAC architecture.

This module defines the base DomainAgent class that all domain-specific
agents will inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple

from mac.environment.state_store import StateStore
from mac.verification.checker import ExternalChecker
from mac.human_interface.interface import HumanQueryInterface


class DomainAgent(ABC):
    """
    Base class for all domain-specialist agents in the MAC architecture.
    
    Domain agents are responsible for handling tasks within their specific
    domain of expertise. They analyze problems, propose solutions, and coordinate
    with component agents to implement those solutions.
    
    Attributes:
        name: The name of the domain agent
        domain: The specific domain of expertise
        capabilities: Set of capabilities this agent provides
        state_store: Reference to the shared state store
        external_checker: Reference to the external checker for verification
        human_interface: Reference to the human query interface
        config: Domain-specific configuration
    """
    
    def __init__(
        self,
        name: str,
        domain: str,
        capabilities: Set[str],
        state_store: StateStore,
        external_checker: ExternalChecker,
        human_interface: HumanQueryInterface,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the domain agent.
        
        Args:
            name: The name of the domain agent
            domain: The specific domain of expertise
            capabilities: Set of capabilities this agent provides
            state_store: Reference to the shared state store
            external_checker: Reference to the external checker
            human_interface: Reference to the human query interface
            config: Domain-specific configuration
        """
        self.name = name
        self.domain = domain
        self.capabilities = capabilities
        self.state_store = state_store
        self.external_checker = external_checker
        self.human_interface = human_interface
        self.config = config or {}
        
        # Component agents managed by this domain agent
        self.component_agents = {}
        
    async def analyze_task(self, task_id: str) -> Dict[str, Any]:
        """
        Analyze a task to determine if and how this domain can contribute.
        
        Args:
            task_id: The ID of the task to analyze
            
        Returns:
            Analysis results with domain-specific insights and contribution plan
        """
        # Get task details from state store
        task = await self.state_store.get_task(task_id)
        
        # Perform domain-specific analysis
        analysis = await self._domain_specific_analysis(task)
        
        # Record analysis in state store
        await self.state_store.record_domain_analysis(
            task_id=task_id,
            domain=self.domain,
            analysis=analysis
        )
        
        return analysis
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        Execute a task using domain-specific expertise and component agents.
        
        Args:
            task_id: The ID of the task to execute
            
        Returns:
            Task execution results
        """
        # Get task details and previous analysis
        task = await self.state_store.get_task(task_id)
        analysis = await self.state_store.get_domain_analysis(task_id, self.domain)
        
        # Execute the domain-specific implementation
        results = await self._domain_specific_execution(task, analysis)
        
        # Verify results using external checker
        verification = await self.external_checker.verify(
            domain=self.domain,
            task_id=task_id,
            results=results
        )
        
        # If verification fails and needs human intervention
        if not verification.success and verification.needs_human:
            human_response = await self.human_interface.request_feedback(
                domain=self.domain,
                task_id=task_id,
                results=results,
                verification=verification
            )
            # Update results based on human feedback
            results = await self._incorporate_human_feedback(results, human_response)
        
        # Record execution results in state store
        await self.state_store.record_domain_execution(
            task_id=task_id,
            domain=self.domain,
            results=results,
            verification=verification
        )
        
        return results
    
    async def get_capabilities(self) -> Set[str]:
        """
        Get the capabilities of this domain agent.
        
        Returns:
            Set of capability identifiers
        """
        return self.capabilities
    
    async def register_component_agent(self, name: str, agent: Any) -> None:
        """
        Register a component agent with this domain agent.
        
        Args:
            name: Name of the component agent
            agent: The component agent instance
        """
        self.component_agents[name] = agent
    
    @abstractmethod
    async def _domain_specific_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform domain-specific analysis of a task.
        
        Args:
            task: The task to analyze
            
        Returns:
            Domain-specific analysis results
        """
        pass
    
    @abstractmethod
    async def _domain_specific_execution(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform domain-specific execution of a task.
        
        Args:
            task: The task to execute
            analysis: Previous analysis results
            
        Returns:
            Domain-specific execution results
        """
        pass
    
    @abstractmethod
    async def _incorporate_human_feedback(
        self, results: Dict[str, Any], feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Incorporate human feedback into execution results.
        
        Args:
            results: Original execution results
            feedback: Human feedback
            
        Returns:
            Updated execution results
        """
        pass