"""
Government Agent

This module provides a government-focused agent implementation for federal agencies.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage

from specialized_agents import ValidationResult
from .base_agent import BaseAgent, TaskRequest, TaskResponse
from .data_loader import get_mcp_tools_for_agency

# Configure logging
logger = logging.getLogger(__name__)

# Initialize memory
memory = MemorySaver()


class GovernmentAgent(BaseAgent):
    """Government-focused agent for federal agencies.
    
    This agent represents a government agency and is designed for use by
    government officials and employees to perform agency-specific tasks.
    """
    
    def __init__(
        self,
        agency_label: str,
        agency_name: str,
        domain: str,
        supported_standards: List[str],
        model_name: str = "gemini-2.0-flash",
        port: int = None
    ):
        """Initialize a government agent.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            agency_name: The full agency name
            domain: The industry domain
            supported_standards: List of standards IDs supported by this agent
            model_name: The LLM model to use
            port: Optional port number for the agent server
        """
        # Call parent constructor
        super().__init__(
            agency_label=agency_label,
            agency_name=agency_name,
            domain=domain,
            supported_standards=supported_standards,
            agent_type="government",
            port=port
        )
        
        # Set up LLM and tools
        self.model_name = model_name
        self.model = ChatGoogleGenerativeAI(model=model_name)
        
        # Register the required tools from agency data
        self._register_agency_tools()
        
        # Create the agent graph
        self.graph = create_react_agent(
            self.model, 
            tools=list(self.tools), 
            checkpointer=memory, 
            prompt=self.getDomainPromptInstructions()
        )
        
        logger.info(f"Initialized Government Agent for {agency_name} with {len(self.tools)} tools")
    
    def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process a task and return a response.
        
        Args:
            task: The task request to process
            
        Returns:
            TaskResponse with the processing result
        """
        # Run validation first (inherited from BaseAgent)
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
        
        # Set up the agent's configuration
        session_id = task.session_id or task.id
        config = {"configurable": {"thread_id": session_id}}
        
        # Run the agent with the task's query
        try:
            logger.info(f"Running Government Agent for {self.agency_label} with query: {task.query}")
            
            # Invoke the agent graph
            self.graph.invoke({"messages": [("user", task.query)]}, config)
            
            # Get the response from the agent's state
            response = self._extract_response(config)
            
            # Store session data if session_id is provided
            if task.session_id:
                self.sessions[task.session_id] = self.sessions.get(task.session_id, {})
                self.sessions[task.session_id]["last_task"] = task
                self.sessions[task.session_id]["last_response"] = response
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing task with Government Agent: {e}")
            return TaskResponse(
                id=task.id,
                status="error",
                message=f"Error processing task: {str(e)}",
                artifacts=None,
                needs_human_review=True
            )
    
    def validateDomainCompliance(self, task: Any) -> ValidationResult:
        """Validate government-specific compliance.
        
        Checks for compliance with government-specific standards and regulations.
        
        Args:
            task: The task to validate
            
        Returns:
            ValidationResult for government-specific validation
        """
        # Extract content to validate
        content = self._extract_content_from_task(task)
        
        # List to collect issues
        issues = []
        
        # Check for sensitive government keywords that should be flagged
        sensitive_patterns = [
            "classified", "confidential", "secret", "top secret", "sensitive but unclassified",
            "for official use only", "restricted", "itar", "personnel file", "security clearance"
        ]
        
        # Check for sensitive keywords
        content_lower = content.lower()
        for pattern in sensitive_patterns:
            if pattern in content_lower:
                issues.append(
                    f"Content contains potentially sensitive government term: '{pattern}'. "
                    f"Ensure compliance with {self.agency_label} information handling procedures."
                )
        
        # Check for potentially inappropriate requests for government agents
        inappropriate_patterns = [
            "bypass regulation", "ignore policy", "unofficial channel", "off the record",
            "without oversight", "circumvent procedure", "hide from public", "cover up",
            "non-disclosure", "not for public knowledge", "keep this quiet"
        ]
        
        for pattern in inappropriate_patterns:
            if pattern in content_lower:
                issues.append(
                    f"Request contains potentially inappropriate language: '{pattern}'. "
                    f"All {self.agency_label} actions must follow official procedures and transparency requirements."
                )
        
        # Return validation result
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues
        )
    
    def getDomainPromptInstructions(self) -> str:
        """Get government-specific prompt instructions.
        
        Returns:
            String containing prompt instructions for government agents
        """
        agency_mission = self.agency_data.get("agencyMission", "No mission statement available")
        
        return f"""
        You are an AI assistant representing the {self.agency_name} ({self.agency_label}), a federal agency 
        with the following mission:
        
        MISSION: {agency_mission}
        
        As a government agency representative, you must adhere to these specific guidelines:

        1. Maintain the highest standards of accuracy, transparency, and ethical conduct.
        2. Provide information that is consistent with {self.agency_name}'s official policy positions and publicly available data.
        3. Clearly distinguish between established facts, policy positions, and your interpretations.
        4. Use neutral, balanced language that avoids political bias or partisan framing.
        5. Respect privacy, confidentiality, and classification requirements for sensitive information.
        6. Acknowledge limitations in your knowledge or authority when appropriate.
        7. Only provide guidance on matters within the jurisdiction and expertise of {self.agency_label}.
        8. Refer complex policy questions or sensitive matters to appropriate human officials.
        9. Follow all applicable federal regulations and ethical standards in your responses.
        10. Make it clear you are an AI assistant, not a human government official.
        
        Your purpose is to assist government employees and officials with their agency-related tasks.
        Ensure all your responses comply with these guidelines while being helpful and informative.
        """
    
    def _register_agency_tools(self) -> None:
        """Register agency-specific tools from agency data."""
        # Get the MCP tools for this agency
        mcp_tools = get_mcp_tools_for_agency(self.agency_label)
        
        # For each tool, create and register it
        for tool_data in mcp_tools:
            tool_name = tool_data.get("toolName", "")
            if not tool_name:
                continue
                
            # Create and add a tool for this MCP tool
            tool = self._create_tool_for_mcp(tool_data)
            if tool:
                self.addTool(tool)
    
    def _create_tool_for_mcp(self, tool_data: Dict[str, Any]) -> Optional[Any]:
        """Create a tool for an MCP tool definition.
        
        Args:
            tool_data: The MCP tool data
            
        Returns:
            Tool object or None if creation fails
        """
        # In a real implementation, this would create actual LangChain tools
        # based on the MCP tool definition. For now, we'll simulate it.
        
        tool_name = tool_data.get("toolName", "")
        description = tool_data.get("description", "")
        
        if not tool_name:
            return None
        
        # For now, we'll create a simple function that just returns info about the tool
        from langchain_core.tools import tool
        
        @tool
        def mcp_tool(query: str = "") -> Dict[str, Any]:
            """Use this tool to access MCP functionality.
            
            Args:
                query: The query to process with the MCP tool
                
            Returns:
                Tool result
            """
            return {
                "name": tool_name,
                "description": description,
                "agency": self.agency_label,
                "result": f"Simulated response from {tool_name} for query: {query}",
                "status": "success"
            }
        
        # Set name and description
        mcp_tool.name = tool_name.lower().replace(" ", "_")
        mcp_tool.description = description or f"Use {tool_name} to perform agency-specific tasks."
        
        return mcp_tool
    
    def _extract_response(self, config: Dict[str, Any]) -> TaskResponse:
        """Extract response from agent state.
        
        Args:
            config: The agent configuration containing thread_id
            
        Returns:
            TaskResponse object
        """
        # Get current state
        current_state = self.graph.get_state(config)
        
        # Extract the messages
        messages = current_state.values.get("messages", [])
        
        if not messages:
            return TaskResponse(
                id=config["configurable"]["thread_id"],
                status="error",
                message="No response generated.",
                artifacts=None
            )
        
        # Get the last message
        last_message = messages[-1]
        
        # Extract content based on message type
        content = ""
        if hasattr(last_message, "content"):
            content = last_message.content
        
        # Check if there are any tool calls or tool messages
        tool_results = []
        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls and len(msg.tool_calls) > 0:
                for tool_call in msg.tool_calls:
                    tool_results.append({
                        "type": "tool_call",
                        "content": {
                            "name": tool_call.name,
                            "args": tool_call.args
                        }
                    })
            elif isinstance(msg, ToolMessage):
                tool_results.append({
                    "type": "tool_result",
                    "content": msg.content
                })
        
        # Create artifacts if any tool results
        artifacts = None
        if tool_results:
            artifacts = [{
                "type": "tool_results",
                "content": tool_results
            }]
        
        # Create and return the response
        return TaskResponse(
            id=config["configurable"]["thread_id"],
            status="success",
            message=content,
            artifacts=artifacts,
            needs_human_review=False
        )