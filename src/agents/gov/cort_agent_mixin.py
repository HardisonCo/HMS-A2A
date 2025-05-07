"""
Chain of Recursive Thoughts (CoRT) Mixin for Government Agents

This module provides a mixin class that adds Chain of Recursive Thoughts capabilities
to government agents, enabling more sophisticated decision making and reasoning.
"""

from typing import Dict, List, Any, Optional, Callable
import logging
from common.utils.recursive_thought import CoRTProcessor, get_recursive_thought_processor
from .base_agent import TaskRequest, TaskResponse

# Configure logging
logger = logging.getLogger(__name__)


class CoRTAgentMixin:
    """
    Mixin class that adds Chain of Recursive Thoughts capabilities to agents.
    
    This mixin can be applied to any agent class to enable recursive thinking
    capabilities, allowing agents to generate, evaluate, and refine their responses.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the CoRT mixin."""
        # Initialize the CoRT processor with default settings
        # The actual processor will be created when needed
        self._cort_processor = None
        self._cort_max_rounds = kwargs.pop('cort_max_rounds', 3)
        self._cort_alternatives = kwargs.pop('cort_alternatives', 3)
        
        # Call the parent class's __init__
        super().__init__(*args, **kwargs)
    
    @property
    def cort_processor(self) -> CoRTProcessor:
        """Get the CoRT processor, creating it if needed."""
        if self._cort_processor is None:
            # Create a function that handles LLM generation
            def llm_generator(prompt: str) -> str:
                """Generate a response using the agent's LLM."""
                try:
                    response = self.model.invoke(prompt).content
                    return response
                except Exception as e:
                    logger.error(f"Error in LLM generation: {e}")
                    return f"Error generating response: {str(e)}"
            
            # Create the CoRT processor
            self._cort_processor = get_recursive_thought_processor(
                llm_fn=llm_generator,
                max_rounds=self._cort_max_rounds,
                generate_alternatives=self._cort_alternatives
            )
        
        return self._cort_processor
    
    def process_with_cort(
        self, 
        task: TaskRequest,
        query_transformer: Optional[Callable[[str], str]] = None,
        enable_cort: bool = True
    ) -> Dict[str, Any]:
        """
        Process a task using Chain of Recursive Thoughts.
        
        Args:
            task: The task request to process
            query_transformer: Optional function to transform the query
            enable_cort: Whether to enable CoRT processing
            
        Returns:
            Dictionary with the processing results including thinking trace
        """
        query = task.query
        
        # Apply query transformer if provided
        if query_transformer:
            query = query_transformer(query)
        
        # Skip CoRT if not enabled
        if not enable_cort:
            # Generate a direct response
            response = self.model.invoke(query).content
            return {
                "response": response,
                "cort_enabled": False,
                "thinking_trace": []
            }
        
        # Process with Chain of Recursive Thoughts
        logger.info(f"Processing task {task.id} with Chain of Recursive Thoughts")
        
        # Define task context
        task_context = {
            "agency_label": self.agency_label,
            "agency_name": self.agency_name,
            "domain": self.domain,
            "task_id": task.id,
            "session_id": task.session_id,
            "metadata": task.metadata
        }
        
        # Process with CoRT
        cort_result = self.cort_processor.process(
            query=query,
            task_context=task_context
        )
        
        logger.info(f"CoRT processing completed with {cort_result['rounds_completed']} rounds")
        
        return {
            "response": cort_result["final_response"],
            "cort_enabled": True,
            "initial_response": cort_result["initial_response"],
            "thinking_trace": cort_result["thinking_trace"],
            "rounds_completed": cort_result["rounds_completed"]
        }
    
    def process_with_cort_and_tools(
        self,
        task: TaskRequest,
        tools: List[Any],
        tool_executor: Callable[[str, Any], str],
        query_transformer: Optional[Callable[[str], str]] = None,
        enable_cort: bool = True
    ) -> Dict[str, Any]:
        """
        Process a task using Chain of Recursive Thoughts with tools.
        
        Args:
            task: The task request to process
            tools: List of available tools
            tool_executor: Function to execute tool calls
            query_transformer: Optional function to transform the query
            enable_cort: Whether to enable CoRT processing
            
        Returns:
            Dictionary with the processing results including thinking trace and tool usage
        """
        query = task.query
        
        # Apply query transformer if provided
        if query_transformer:
            query = query_transformer(query)
        
        # Skip CoRT if not enabled
        if not enable_cort:
            # Generate a direct response with tools
            # This would typically be handled by the agent's regular tool usage mechanism
            response = f"Direct response to: {query}"
            return {
                "response": response,
                "cort_enabled": False,
                "thinking_trace": [],
                "tool_usage": []
            }
        
        # Process with Chain of Recursive Thoughts and tools
        logger.info(f"Processing task {task.id} with Chain of Recursive Thoughts and tools")
        
        # Define task context
        task_context = {
            "agency_label": self.agency_label,
            "agency_name": self.agency_name,
            "domain": self.domain,
            "task_id": task.id,
            "session_id": task.session_id,
            "metadata": task.metadata,
            "available_tools": [getattr(tool, "name", str(tool)) for tool in tools]
        }
        
        # Process with CoRT and tools
        cort_result = self.cort_processor.process_with_tools(
            query=query,
            tools=tools,
            tool_executor=tool_executor,
            task_context=task_context
        )
        
        logger.info(f"CoRT processing with tools completed with {cort_result['rounds_completed']} rounds")
        
        return {
            "response": cort_result["final_response"],
            "cort_enabled": True,
            "initial_response": cort_result["initial_response"],
            "thinking_trace": cort_result["thinking_trace"],
            "rounds_completed": cort_result["rounds_completed"],
            "tool_usage": cort_result.get("tool_usage", [])
        }
    
    def cort_enhanced_task_response(
        self,
        task: TaskRequest,
        cort_result: Dict[str, Any]
    ) -> TaskResponse:
        """
        Create a TaskResponse with CoRT enhancement.
        
        Args:
            task: The original task request
            cort_result: The result from CoRT processing
            
        Returns:
            Enhanced TaskResponse with CoRT artifacts
        """
        # Extract the final response
        response_message = cort_result["response"]
        
        # Create artifacts with thinking trace
        artifacts = [{
            "type": "cort_thinking",
            "content": {
                "rounds_completed": cort_result.get("rounds_completed", 0),
                "thinking_trace": cort_result.get("thinking_trace", []),
                "tool_usage": cort_result.get("tool_usage", [])
            }
        }]
        
        # Add any other artifacts from the CoRT result
        if "tool_results" in cort_result:
            artifacts.append({
                "type": "tool_results",
                "content": cort_result["tool_results"]
            })
        
        # Create the response
        return TaskResponse(
            id=task.id,
            status="success",
            message=response_message,
            artifacts=artifacts,
            needs_human_review=False,
            metadata={
                "cort_enabled": cort_result.get("cort_enabled", True),
                "rounds_completed": cort_result.get("rounds_completed", 0)
            }
        )