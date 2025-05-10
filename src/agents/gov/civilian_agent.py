"""
Civilian Agent

This module provides a civilian-focused agent implementation for public engagement with federal agencies.
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


class CivilianAgent(BaseAgent):
    """Civilian-focused agent for federal agencies.
    
    This agent represents a public-facing interface for a government agency,
    designed for use by civilians and the general public.
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
        """Initialize a civilian agent.
        
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
            agent_type="civilian",
            port=port
        )
        
        # Set up LLM and tools
        self.model_name = model_name
        self.model = ChatGoogleGenerativeAI(model=model_name)
        
        # Register the required tools from agency data
        self._register_public_tools()
        
        # Create the agent graph
        self.graph = create_react_agent(
            self.model, 
            tools=list(self.tools), 
            checkpointer=memory, 
            prompt=self.getDomainPromptInstructions()
        )
        
        logger.info(f"Initialized Civilian Agent for {agency_name} with {len(self.tools)} tools")
    
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
                    message="We cannot process this request due to policy restrictions. Please rephrase your question or visit our official website for more information.",
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
            logger.info(f"Running Civilian Agent for {self.agency_label} with query: {task.query}")
            
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
            logger.error(f"Error processing task with Civilian Agent: {e}")
            return TaskResponse(
                id=task.id,
                status="error",
                message=f"I'm sorry, but I'm having trouble processing your request right now. Please try again later or contact {self.agency_label} through our official channels for assistance.",
                artifacts=None,
                needs_human_review=True
            )
    
    def validateDomainCompliance(self, task: Any) -> ValidationResult:
        """Validate civilian-specific compliance.
        
        Checks for compliance with citizen engagement guidelines and public information policies.
        
        Args:
            task: The task to validate
            
        Returns:
            ValidationResult for civilian-specific validation
        """
        # Extract content to validate
        content = self._extract_content_from_task(task)
        
        # List to collect issues
        issues = []
        
        # Check for requests asking for non-public information
        non_public_patterns = [
            "internal memo", "internal document", "not published", "internal only",
            "classified", "confidential", "secret", "top secret", "sensitive but unclassified",
            "for official use only", "restricted", "personnel file", "employee records"
        ]
        
        # Check for non-public information requests
        content_lower = content.lower()
        for pattern in non_public_patterns:
            if pattern in content_lower:
                issues.append(
                    f"Your request appears to be seeking non-public information: '{pattern}'. "
                    f"The {self.agency_label} civilian engagement system can only provide information "
                    f"that is publicly available."
                )
        
        # Check for potentially inappropriate civilian requests
        inappropriate_patterns = [
            "expedite my application", "special treatment", "bypass the queue", "speed up",
            "faster than normal", "ahead of others", "preferential", "know someone who works",
            "pull strings", "off the record", "bypass", "under the table"
        ]
        
        for pattern in inappropriate_patterns:
            if pattern in content_lower:
                issues.append(
                    f"Your request contains language that suggests seeking preferential treatment: '{pattern}'. "
                    f"All {self.agency_label} processes follow standard procedures that apply equally to everyone."
                )
        
        # Return validation result
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues
        )
    
    def getDomainPromptInstructions(self) -> str:
        """Get civilian-specific prompt instructions.
        
        Returns:
            String containing prompt instructions for civilian agents
        """
        agency_mission = self.agency_data.get("agencyMission", "No mission statement available")
        
        return f"""
        You are an AI assistant representing the public-facing services of the {self.agency_name} ({self.agency_label}),
        a federal agency with the following mission:
        
        MISSION: {agency_mission}
        
        As a civilian engagement representative for this agency, you must adhere to these specific guidelines:

        1. Provide accurate, helpful information about {self.agency_label}'s public services, programs, and policies.
        2. Only share information that is publicly available and appropriate for general audiences.
        3. Explain complex government processes and requirements in clear, simple language.
        4. Maintain a helpful, respectful, and professional tone in all interactions.
        5. Do not speculate about internal agency decisions or non-public information.
        6. Direct users to appropriate official resources, forms, or contact information when needed.
        7. Do not offer opinions on policy matters or political questions beyond factual information.
        8. Protect user privacy and never ask for sensitive personal information.
        9. Clarify that you cannot provide case-specific assistance that requires human review.
        10. Make it clear you are an AI assistant, not a human government employee.
        
        Your purpose is to help members of the public understand and access government services.
        Focus on being informative, accessible, and helpful while following these guidelines.
        """
    
    def _register_public_tools(self) -> None:
        """Register public-facing tools for civilian engagement."""
        # Get all MCP tools for this agency
        mcp_tools = get_mcp_tools_for_agency(self.agency_label)
        
        # Filter to only public-facing tools (In a real implementation, this would check tool metadata)
        public_tools = [t for t in mcp_tools if self._is_public_facing_tool(t)]
        
        # For each public tool, create and register it
        for tool_data in public_tools:
            tool_name = tool_data.get("toolName", "")
            if not tool_name:
                continue
                
            # Create and add a public tool for this MCP tool
            tool = self._create_public_tool_for_mcp(tool_data)
            if tool:
                self.addTool(tool)
    
    def _is_public_facing_tool(self, tool_data: Dict[str, Any]) -> bool:
        """Determine if a tool should be exposed to civilians.
        
        Args:
            tool_data: The MCP tool data
            
        Returns:
            Boolean indicating if the tool is public-facing
        """
        # In a real implementation, this would check tool metadata or data fields
        # For now, we'll use a simple heuristic based on the tool name
        
        tool_name = tool_data.get("toolName", "").lower()
        
        # Tool names that suggest they're not public-facing
        internal_keywords = [
            "internal", "classified", "sensitive", "confidential", "administration",
            "employee", "interagency", "inspector", "audit", "investigation", 
            "enforcement", "intelligence", "security", "compliance", "monitor",
            "assessment", "underwriting", "examiner", "surveillance"
        ]
        
        # Tool names that suggest they are public-facing
        public_keywords = [
            "public", "citizen", "civilian", "service", "information", "assistance",
            "help", "resource", "guide", "benefit", "application", "form", "portal",
            "calculator", "estimator", "finder", "locator", "search"
        ]
        
        # Check if tool name contains internal keywords
        for keyword in internal_keywords:
            if keyword in tool_name:
                return False
        
        # Check if tool name contains public keywords
        for keyword in public_keywords:
            if keyword in tool_name:
                return True
        
        # Default to not public-facing if not clear
        return False
    
    def _create_public_tool_for_mcp(self, tool_data: Dict[str, Any]) -> Optional[Any]:
        """Create a public-facing tool for an MCP tool definition.
        
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
        def public_mcp_tool(query: str = "") -> Dict[str, Any]:
            """Use this tool to access public information and services.
            
            Args:
                query: The query to process with the public tool
                
            Returns:
                Tool result
            """
            return {
                "name": tool_name,
                "description": description,
                "agency": self.agency_label,
                "result": f"Public information from {tool_name} for query: {query}",
                "status": "success"
            }
        
        # Set name and description
        public_mcp_tool.name = "public_" + tool_name.lower().replace(" ", "_")
        public_mcp_tool.description = description or f"Get public information about {tool_name}."
        
        return public_mcp_tool
    
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
                message="I'm sorry, but I'm having trouble processing your request right now. Please try again or visit our website for more information.",
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