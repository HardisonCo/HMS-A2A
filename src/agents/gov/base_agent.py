"""
Base Agent classes for Government Agency AI Agents

This module provides the base interface and implementation for all government agency agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union
import uuid
from pydantic import BaseModel, Field
import json
import logging

from specialized_agents import StandardsValidator, ValidationResult
from specialized_agents.standards_validation import Standard


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskRequest(BaseModel):
    """Represents a task request to an agent."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Represents a response from an agent."""
    
    id: str
    status: str  # "success", "error", "partial"
    message: str
    artifacts: Optional[List[Dict[str, Any]]] = None
    needs_human_review: bool = False
    metadata: Optional[Dict[str, Any]] = None


class BaseAgentInterface(ABC):
    """Interface for all agency agents."""
    
    @abstractmethod
    def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process a task and return a response."""
        pass
    
    @abstractmethod
    def validateTask(self, task: Any) -> ValidationResult:
        """Validate a task against agency standards."""
        pass
    
    @abstractmethod
    def getDomainPromptInstructions(self) -> str:
        """Get domain-specific prompt instructions."""
        pass
    
    @abstractmethod
    def addTool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        pass
    
    @abstractmethod
    def getAgencyInfo(self) -> Dict[str, Any]:
        """Get information about the agency the agent represents."""
        pass


class BaseAgent(BaseAgentInterface):
    """Base implementation for government agency agents."""
    
    def __init__(
        self, 
        agency_label: str, 
        agency_name: str, 
        domain: str,
        supported_standards: List[str],
        agent_type: str = "base",
        port: int = None
    ):
        """Initialize a base agent.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            agency_name: The full agency name
            domain: The industry domain
            supported_standards: List of standards IDs supported by this agent
            agent_type: The type of agent (e.g., "government", "civilian")
            port: Optional port number for the agent server
        """
        self.agency_label = agency_label
        self.agency_name = agency_name
        self.domain = domain
        self.supported_standards = supported_standards
        self.agent_type = agent_type
        self.port = port
        self.tools = set()
        
        # Create the standards validator
        self.validator = StandardsValidator(domain, supported_standards)
        
        # Load agency-specific data if available
        self.agency_data = self._load_agency_data()
        
        # Initialize state
        self.sessions = {}  # Store session data
        
        logger.info(f"Initialized {agent_type} agent for {agency_name} ({agency_label})")
    
    def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process a task and return a response.
        
        Args:
            task: The task request to process
            
        Returns:
            TaskResponse with the processing result
        """
        # Validate the task first
        validation_result = self.validateTask(task)
        
        # If validation fails with critical issues, return early
        if not validation_result.valid:
            critical_issues = validation_result.get_critical_issues()
            if critical_issues:
                return TaskResponse(
                    id=task.id,
                    status="error",
                    message="Task validation failed due to critical compliance issues",
                    artifacts=[{
                        "type": "validation_result",
                        "content": {
                            "valid": False,
                            "issues": [issue.dict() for issue in critical_issues]
                        }
                    }],
                    needs_human_review=True
                )
        
        # Default implementation logs the request
        logger.info(f"Processing task {task.id} for {self.agency_name}")
        
        # Store session data if session_id is provided
        if task.session_id:
            self.sessions[task.session_id] = self.sessions.get(task.session_id, {})
            self.sessions[task.session_id]["last_task"] = task
        
        # Default implementation - to be overridden by subclasses
        return TaskResponse(
            id=task.id,
            status="error",
            message=f"Task processing not implemented for base agent {self.agency_label}",
            artifacts=None
        )
    
    def validateTask(self, task: Any) -> ValidationResult:
        """Validate a task against agency standards.
        
        Args:
            task: The task to validate
            
        Returns:
            ValidationResult indicating whether the task is valid
        """
        # Extract content to validate
        content = self._extract_content_from_task(task)
        
        # Use the standards validator
        validation_result = self.validator.validate_content(content)
        
        # Perform domain-specific validation
        domain_result = self.validateDomainCompliance(task)
        
        # If domain validation found issues, add them to the result
        if not domain_result.valid:
            for issue in domain_result.issues:
                if issue not in validation_result.issues:
                    validation_result.issues.append(issue)
            
            validation_result.valid = False
        
        return validation_result
    
    def validateDomainCompliance(self, task: Any) -> ValidationResult:
        """Validate domain-specific compliance.
        
        Args:
            task: The task to validate
            
        Returns:
            ValidationResult for domain-specific validation
        """
        # Default implementation returns valid
        return ValidationResult(valid=True, issues=[])
    
    def getDomainPromptInstructions(self) -> str:
        """Get domain-specific prompt instructions.
        
        Returns:
            String containing prompt instructions for the domain
        """
        return f"""
        As an AI agent for {self.agency_name}, you must adhere to these guidelines:
        
        1. Maintain accuracy and objectivity in all communications.
        2. Provide information consistent with {self.agency_name}'s mission and public data.
        3. Clearly distinguish between established facts and interpretations.
        4. Avoid politically charged or biased language.
        5. Respect the privacy of individuals and sensitive information.
        6. Do not provide specific advice on matters requiring human judgment.
        7. Acknowledge limitations in your knowledge or authority.
        8. Refer complex questions to appropriate human officials when necessary.
        """
    
    def addTool(self, tool: Any) -> None:
        """Add a tool to the agent.
        
        Args:
            tool: The tool to add
        """
        tool_name = getattr(tool, "name", str(tool))
        logger.info(f"Adding tool {tool_name} to {self.agency_label} agent")
        self.tools.add(tool)
    
    def getAgencyInfo(self) -> Dict[str, Any]:
        """Get information about the agency the agent represents.
        
        Returns:
            Dictionary with agency information
        """
        return {
            "agency_label": self.agency_label,
            "agency_name": self.agency_name,
            "domain": self.domain,
            "agent_type": self.agent_type,
            "supported_standards": self.supported_standards,
            "mission": self.agency_data.get("agencyMission", "No mission statement available"),
            "tool_count": len(self.tools)
        }
    
    def _extract_content_from_task(self, task: Any) -> str:
        """Extract content to validate from a task.
        
        Args:
            task: The task to extract content from
            
        Returns:
            String content extracted from the task
        """
        # Handle TaskRequest objects
        if isinstance(task, TaskRequest):
            return task.query
        
        # Handle dictionaries
        if isinstance(task, dict):
            if "query" in task:
                return task["query"]
            elif "message" in task:
                return task["message"]
            else:
                return json.dumps(task)
        
        # Handle strings
        if isinstance(task, str):
            return task
        
        # Handle other objects by converting to string
        return str(task)
    
    def _load_agency_data(self) -> Dict[str, Any]:
        """Load agency-specific data from source.
        
        Returns:
            Dictionary with agency data or empty dict if not found
        """
        try:
            # Import here to avoid circular imports
            from .data_loader import load_agency_data
            
            agency_data = load_agency_data(self.agency_label)
            logger.info(f"Loaded data for {self.agency_label}")
            return agency_data
        except Exception as e:
            logger.warning(f"Failed to load agency data for {self.agency_label}: {e}")
            return {}