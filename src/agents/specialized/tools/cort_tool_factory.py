"""
CoRT Tool Factory

This module provides factory functions to enhance existing tools with
Chain of Recursive Thoughts capabilities for improved reasoning and decision making.
"""

from typing import Dict, List, Any, Optional, Callable, Union
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from specialized_agents.tools_base import StandardsCompliantTool
from specialized_agents.tools.cort_enhanced_tool import CoRTEnhancedTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def enhance_tool_with_cort(
    tool: StandardsCompliantTool,
    llm_generator: Optional[Callable[[str], str]] = None,
    model_name: str = "gemini-2.0-flash",
    max_rounds: int = 3,
    generate_alternatives: int = 3
) -> CoRTEnhancedTool:
    """
    Enhance a standards-compliant tool with Chain of Recursive Thoughts capabilities.
    
    Args:
        tool: The tool to enhance
        llm_generator: Optional function that processes a prompt and returns a response
        model_name: The LLM model to use if no generator is provided
        max_rounds: Maximum number of thinking rounds
        generate_alternatives: Number of alternatives to generate per round
        
    Returns:
        CoRT-enhanced version of the tool
    """
    # If no LLM generator was provided, create one with the specified model
    if llm_generator is None:
        # Create a Gemini model
        try:
            model = ChatGoogleGenerativeAI(model=model_name)
            
            # Create a generator function
            def default_generator(prompt: str) -> str:
                """Generate a response using the Gemini model."""
                try:
                    response = model.invoke(prompt).content
                    return response
                except Exception as e:
                    logger.error(f"Error in LLM generation: {e}")
                    return f"Error generating response: {str(e)}"
            
            llm_generator = default_generator
            
        except Exception as e:
            logger.error(f"Error creating default LLM generator: {e}")
            raise ValueError(f"Could not create default LLM generator: {str(e)}")
    
    # Create and return the enhanced tool
    return CoRTEnhancedTool(
        wrapped_tool=tool,
        max_rounds=max_rounds,
        generate_alternatives=generate_alternatives,
        dynamic_rounds=True,
        llm_generator=llm_generator
    )


def enhance_tools_with_cort(
    tools: List[StandardsCompliantTool],
    llm_generator: Optional[Callable[[str], str]] = None,
    model_name: str = "gemini-2.0-flash",
    max_rounds: int = 3,
    generate_alternatives: int = 3
) -> List[CoRTEnhancedTool]:
    """
    Enhance multiple standards-compliant tools with CoRT capabilities.
    
    Args:
        tools: The tools to enhance
        llm_generator: Optional function that processes a prompt and returns a response
        model_name: The LLM model to use if no generator is provided
        max_rounds: Maximum number of thinking rounds
        generate_alternatives: Number of alternatives to generate per round
        
    Returns:
        List of CoRT-enhanced tools
    """
    # Create a default LLM generator if needed
    if llm_generator is None and tools:
        # Create a Gemini model
        try:
            model = ChatGoogleGenerativeAI(model=model_name)
            
            # Create a generator function
            def default_generator(prompt: str) -> str:
                """Generate a response using the Gemini model."""
                try:
                    response = model.invoke(prompt).content
                    return response
                except Exception as e:
                    logger.error(f"Error in LLM generation: {e}")
                    return f"Error generating response: {str(e)}"
            
            llm_generator = default_generator
            
        except Exception as e:
            logger.error(f"Error creating default LLM generator: {e}")
            raise ValueError(f"Could not create default LLM generator: {str(e)}")
    
    # Enhance each tool
    enhanced_tools = []
    for tool in tools:
        try:
            enhanced_tool = enhance_tool_with_cort(
                tool=tool,
                llm_generator=llm_generator,
                max_rounds=max_rounds,
                generate_alternatives=generate_alternatives
            )
            enhanced_tools.append(enhanced_tool)
        except Exception as e:
            logger.error(f"Error enhancing tool {tool.name}: {e}")
            # Keep the original tool if enhancement fails
            enhanced_tools.append(tool)
    
    return enhanced_tools