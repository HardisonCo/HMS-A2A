"""
Chain of Recursive Thoughts Enhanced Tool

This module provides a wrapper that enhances standards-compliant tools with
Chain of Recursive Thoughts capabilities for improved reasoning and output quality.
"""

from typing import Any, Dict, List, Optional, Callable, Union
import logging
from common.utils.recursive_thought import CoRTProcessor, get_recursive_thought_processor
from specialized_agents.tools_base import StandardsCompliantTool
from specialized_agents.standards_validation import ValidationResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoRTEnhancedTool(StandardsCompliantTool):
    """
    A wrapper that enhances any standards-compliant tool with CoRT capabilities.
    
    This class wraps a StandardsCompliantTool and adds Chain of Recursive Thoughts
    capabilities to improve reasoning and output quality.
    """
    
    def __init__(
        self,
        wrapped_tool: StandardsCompliantTool,
        max_rounds: int = 3,
        generate_alternatives: int = 3,
        dynamic_rounds: bool = True,
        llm_generator: Optional[Callable[[str], str]] = None
    ):
        """
        Initialize a CoRT-enhanced tool.
        
        Args:
            wrapped_tool: The tool to enhance with CoRT
            max_rounds: Maximum number of thinking rounds
            generate_alternatives: Number of alternatives to generate in each round
            dynamic_rounds: Whether to dynamically determine the number of rounds
            llm_generator: Function that processes a prompt and returns a response
        """
        # Initialize with the wrapped tool's parameters
        super().__init__(
            name=f"cort_{wrapped_tool.name}",
            description=f"CoRT-enhanced: {wrapped_tool.description}",
            standards=wrapped_tool.standards,
            is_destructive=wrapped_tool.is_destructive,
            is_idempotent=wrapped_tool.is_idempotent
        )
        
        # Store the wrapped tool
        self.wrapped_tool = wrapped_tool
        
        # Configure CoRT settings
        self.max_rounds = max_rounds
        self.generate_alternatives = generate_alternatives
        self.dynamic_rounds = dynamic_rounds
        
        # Save or create the LLM generator
        self._llm_generator = llm_generator
        self._cort_processor = None
    
    @property
    def cort_processor(self) -> CoRTProcessor:
        """Get the CoRT processor, creating it if needed."""
        if self._cort_processor is None:
            # If no LLM generator was provided, raise an error
            if self._llm_generator is None:
                raise ValueError("No LLM generator was provided to the CoRT-enhanced tool")
            
            # Create the CoRT processor
            self._cort_processor = get_recursive_thought_processor(
                llm_fn=self._llm_generator,
                max_rounds=self.max_rounds,
                generate_alternatives=self.generate_alternatives
            )
        
        return self._cort_processor
    
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute the tool with CoRT enhancement.
        
        Args:
            input_data: The input data for the tool
            
        Returns:
            Dictionary with the enhanced result
        """
        # Validate the input
        validation_result = self.validate_input(input_data)
        if not validation_result.valid:
            return {
                "status": "error",
                "message": "Input validation failed",
                "validation_result": validation_result.dict()
            }
        
        # First, execute the wrapped tool to get an initial result
        try:
            logger.info(f"Executing wrapped tool: {self.wrapped_tool.name}")
            initial_result = self.wrapped_tool.execute(input_data)
            
            # Check if the wrapped tool execution failed
            if initial_result.get("status") == "error":
                logger.warning(f"Wrapped tool execution failed: {initial_result.get('message')}")
                return initial_result
            
            # Extract the result message
            initial_message = initial_result.get("message", "")
            if not initial_message:
                # Try to extract from result field if message is empty
                initial_message = initial_result.get("result", "No result provided")
            
            # Define the query for CoRT processing
            query = self._create_cort_query(input_data, initial_result)
            
            # Process with CoRT
            logger.info(f"Enhancing result with CoRT for tool: {self.name}")
            cort_result = self.cort_processor.process(
                query=query,
                initial_response=initial_message,
                task_context={
                    "tool_name": self.name,
                    "input_data": input_data,
                    "wrapped_tool": self.wrapped_tool.name,
                    "standards": self.standards
                }
            )
            
            # Get the enhanced result
            enhanced_message = cort_result["final_response"]
            
            # Validate the enhanced result
            logger.info(f"Validating enhanced result for tool: {self.name}")
            validation_result = self.validate_output(enhanced_message)
            if not validation_result.valid:
                # If validation fails, fall back to the original result
                logger.warning(f"Enhanced result validation failed, falling back to original result")
                return initial_result
            
            # Create the enhanced result
            enhanced_result = {
                "status": "success",
                "message": enhanced_message,
                "original_result": initial_result,
                "cort_metadata": {
                    "rounds_completed": cort_result["rounds_completed"],
                    "thinking_trace": cort_result["thinking_trace"]
                }
            }
            
            # Add any additional fields from the original result
            for key, value in initial_result.items():
                if key not in enhanced_result and key not in ["message", "status"]:
                    enhanced_result[key] = value
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in CoRT-enhanced execution: {e}")
            return {
                "status": "error",
                "message": f"Error in CoRT-enhanced execution: {str(e)}"
            }
    
    def _create_cort_query(self, input_data: Any, initial_result: Dict[str, Any]) -> str:
        """
        Create a query for CoRT processing.
        
        Args:
            input_data: The original input data
            initial_result: The result from the wrapped tool
            
        Returns:
            String with the CoRT query
        """
        # Extract the initial message
        initial_message = initial_result.get("message", "")
        if not initial_message:
            initial_message = initial_result.get("result", "No result provided")
        
        # Create a context-aware query
        query = f"""
        You are using the {self.wrapped_tool.name} tool, which has these standards: {', '.join(self.standards)}
        
        Original input: {input_data}
        
        Initial result: {initial_message}
        
        Your task is to improve this result by:
        1. Ensuring it fully addresses the input
        2. Making sure it complies with all required standards
        3. Improving clarity, accuracy, and completeness
        4. Ensuring it follows best practices for this domain
        
        Generate an improved version of this result.
        """
        
        return query
    
    def validate_input(self, input_data: Any) -> ValidationResult:
        """
        Validate the input data using the wrapped tool's validation.
        
        Args:
            input_data: The input data to validate
            
        Returns:
            ValidationResult indicating whether the input is valid
        """
        return self.wrapped_tool.validate_input(input_data)
    
    def validate_output(self, output_data: Any) -> ValidationResult:
        """
        Validate the output data using the wrapped tool's validation.
        
        Args:
            output_data: The output data to validate
            
        Returns:
            ValidationResult indicating whether the output is valid
        """
        return self.wrapped_tool.validate_output(output_data)