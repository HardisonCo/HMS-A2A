"""
CoRT-enhanced Government Agent

This module provides a government-focused agent implementation with Chain of Recursive Thoughts
capabilities, enabling more sophisticated reasoning and decision making.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage

from specialized_agents import ValidationResult
from .base_agent import TaskRequest, TaskResponse
from .government_agent import GovernmentAgent
from .cort_agent_mixin import CoRTAgentMixin
from .data_loader import get_mcp_tools_for_agency

# Configure logging
logger = logging.getLogger(__name__)

# Initialize memory
memory = MemorySaver()


class CoRTGovernmentAgent(CoRTAgentMixin, GovernmentAgent):
    """
    Government-focused agent with Chain of Recursive Thoughts capabilities.
    
    This agent enhances the standard GovernmentAgent with recursive thinking
    capabilities, allowing for more sophisticated reasoning and decision making.
    """
    
    def __init__(
        self,
        agency_label: str,
        agency_name: str,
        domain: str,
        supported_standards: List[str],
        model_name: str = "gemini-2.0-flash",
        port: int = None,
        cort_max_rounds: int = 3,
        cort_alternatives: int = 3,
        cort_enabled_by_default: bool = True
    ):
        """Initialize a CoRT-enhanced government agent.
        
        Args:
            agency_label: The agency identifier (e.g., "CIA", "USADF")
            agency_name: The full agency name
            domain: The industry domain
            supported_standards: List of standards IDs supported by this agent
            model_name: The LLM model to use
            port: Optional port number for the agent server
            cort_max_rounds: Maximum CoRT thinking rounds
            cort_alternatives: Number of alternatives to generate in each round
            cort_enabled_by_default: Whether CoRT is enabled by default
        """
        # Call parent constructor with CoRT parameters
        super().__init__(
            agency_label=agency_label,
            agency_name=agency_name,
            domain=domain,
            supported_standards=supported_standards,
            model_name=model_name,
            port=port,
            cort_max_rounds=cort_max_rounds,
            cort_alternatives=cort_alternatives
        )
        
        self.cort_enabled_by_default = cort_enabled_by_default
        logger.info(f"Initialized CoRT-enhanced Government Agent for {agency_name} with {len(self.tools)} tools")
    
    def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process a task with recursive thinking capabilities.
        
        Args:
            task: The task request to process
            
        Returns:
            TaskResponse with the processing result
        """
        # Determine if CoRT should be used - it can be disabled via task metadata
        use_cort = self.cort_enabled_by_default
        if task.metadata and "use_cort" in task.metadata:
            use_cort = bool(task.metadata["use_cort"])
        
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
        
        # For simple queries that don't need tools, use direct CoRT processing
        if self._task_needs_tools(task.query):
            # Process with React agent framework and CoRT enhancement
            return self._process_with_react_agent(task, use_cort)
        else:
            # Process with direct CoRT
            return self._process_with_direct_cort(task, use_cort)
    
    def _task_needs_tools(self, query: str) -> bool:
        """Determine if a task likely needs tools to process.
        
        Args:
            query: The task query
            
        Returns:
            True if tools are likely needed, False otherwise
        """
        # Use a simple heuristic - check for keywords that suggest tool usage
        tool_indicators = [
            "calculate", "convert", "lookup", "find", "search",
            "data", "information", "latest", "current", "analyze",
            "compare", "statistics", "numbers", "report"
        ]
        
        query_lower = query.lower()
        for indicator in tool_indicators:
            if indicator in query_lower:
                return True
        
        # Also check if the query is a question
        question_indicators = ["what", "how", "when", "where", "why", "who", "which", "?"]
        for indicator in question_indicators:
            if query_lower.startswith(indicator) or indicator in query_lower:
                return True
        
        return False
    
    def _process_with_react_agent(self, task: TaskRequest, use_cort: bool) -> TaskResponse:
        """Process a task using the React agent framework with CoRT enhancement.
        
        Args:
            task: The task request
            use_cort: Whether to use CoRT
            
        Returns:
            TaskResponse with the result
        """
        # Set up the agent's configuration
        session_id = task.session_id or task.id
        config = {"configurable": {"thread_id": session_id}}
        
        # Run the agent with the task's query
        try:
            logger.info(f"Running CoRT Government Agent for {self.agency_label} with query: {task.query}")
            
            # First, invoke the agent graph to get an initial response with tool usage
            self.graph.invoke({"messages": [("user", task.query)]}, config)
            
            # Extract the initial response
            initial_response = self._extract_raw_response(config)
            
            # If CoRT is disabled, return the response directly
            if not use_cort:
                logger.info("CoRT is disabled, returning direct response")
                return self._extract_response(config)
            
            # Process with CoRT to enhance the response
            logger.info("Enhancing response with CoRT")
            tool_executor = self._create_tool_executor()
            
            # Define a function to execute a tool call
            def execute_tool(tool_input: str, tool: Any) -> str:
                """Execute a tool call."""
                try:
                    return tool_executor(tool.name, tool_input)
                except Exception as e:
                    logger.error(f"Error executing tool {tool.name}: {e}")
                    return f"Error executing tool {tool.name}: {str(e)}"
            
            # Process with CoRT and tools
            cort_result = self.process_with_cort_and_tools(
                task=task,
                tools=list(self.tools),
                tool_executor=execute_tool,
                enable_cort=use_cort
            )
            
            # Create an enhanced response
            return self.cort_enhanced_task_response(task, cort_result)
            
        except Exception as e:
            logger.error(f"Error processing task with CoRT Government Agent: {e}")
            return TaskResponse(
                id=task.id,
                status="error",
                message=f"Error processing task: {str(e)}",
                artifacts=None,
                needs_human_review=True
            )
    
    def _process_with_direct_cort(self, task: TaskRequest, use_cort: bool) -> TaskResponse:
        """Process a task directly with CoRT (no tools).
        
        Args:
            task: The task request
            use_cort: Whether to use CoRT
            
        Returns:
            TaskResponse with the result
        """
        try:
            logger.info(f"Processing task directly with CoRT for {self.agency_label}")
            
            # Transform the query to include agency context
            def query_transformer(query: str) -> str:
                return f"""
                As a representative of the {self.agency_name} ({self.agency_label}), 
                please respond to the following query:
                
                {query}
                
                Remember to adhere to all agency policies and guidelines in your response.
                """
            
            # Process with CoRT
            cort_result = self.process_with_cort(
                task=task,
                query_transformer=query_transformer,
                enable_cort=use_cort
            )
            
            # Create a response
            return self.cort_enhanced_task_response(task, cort_result)
            
        except Exception as e:
            logger.error(f"Error processing task directly with CoRT: {e}")
            return TaskResponse(
                id=task.id,
                status="error",
                message=f"Error processing task: {str(e)}",
                artifacts=None,
                needs_human_review=True
            )
    
    def _extract_raw_response(self, config: Dict[str, Any]) -> str:
        """Extract the raw response text from agent state.
        
        Args:
            config: The agent configuration containing thread_id
            
        Returns:
            String with the raw response
        """
        # Get current state
        current_state = self.graph.get_state(config)
        
        # Extract the messages
        messages = current_state.values.get("messages", [])
        
        if not messages:
            return "No response generated."
        
        # Get the last message
        last_message = messages[-1]
        
        # Extract content based on message type
        if hasattr(last_message, "content"):
            return last_message.content
        
        return "Unable to extract response content."
    
    def _create_tool_executor(self) -> Callable[[str, str], str]:
        """Create a function that executes tool calls.
        
        Returns:
            Function that executes tool calls
        """
        # Create a mapping of tool names to tools
        tool_map = {tool.name: tool for tool in self.tools}
        
        # Define the executor function
        def execute_tool(tool_name: str, tool_input: str) -> str:
            """Execute a tool call.
            
            Args:
                tool_name: The name of the tool to execute
                tool_input: The input to the tool
                
            Returns:
                String with the tool result
            """
            if tool_name not in tool_map:
                return f"Error: Tool '{tool_name}' not found"
            
            try:
                tool = tool_map[tool_name]
                result = tool.invoke(tool_input)
                return str(result)
            except Exception as e:
                return f"Error executing tool '{tool_name}': {str(e)}"
        
        return execute_tool