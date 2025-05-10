"""
Standards-Compliant MCP Tool

This module provides the base class for standards-compliant MCP tools
that support collaboration between specialized agents.
"""

from typing import Dict, Any, List, Optional, Type, Set, Union
from pydantic import BaseModel
import json
import uuid
import logging
import asyncio

from specialized_agents.collaboration.tool_registry import MCPToolRegistry, HITLManager

logger = logging.getLogger(__name__)


class StandardsCompliantMCPTool:
    """Base class for standards-compliant MCP tools.
    
    This class provides common functionality for all MCP tools that need to:
    1. Validate inputs/outputs against domain-specific standards
    2. Support human-in-the-loop (HITL) review
    3. Collaborate with other agents
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        schema_model: Type[BaseModel],
        supported_standards: List[str],
        domain: str,
        tool_metadata: Dict[str, Any] = None
    ):
        """Initialize a standards-compliant MCP tool.
        
        Args:
            name: Tool name
            description: Tool description
            schema_model: Pydantic model defining the input schema
            supported_standards: List of standards supported by this tool
            domain: Industry domain (e.g., "Agriculture")
            tool_metadata: Additional metadata for the tool
        """
        self.name = name
        self.description = description
        self.schema_model = schema_model
        self.supported_standards = supported_standards
        self.domain = domain
        self.tool_metadata = tool_metadata or {}
        
        # Get the HITL manager
        self.hitl_manager = MCPToolRegistry().get_hitl_manager()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for registration with MCP.
        
        Returns:
            Dictionary containing the tool definition
        """
        schema = self.schema_model.model_json_schema()
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": schema,
            "metadata": {
                "domain": self.domain,
                "supportedStandards": self.supported_standards,
                **self.tool_metadata
            }
        }
    
    async def __call__(self, **kwargs) -> List[Dict[str, Any]]:
        """Execute the tool with the given arguments.
        
        Args:
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result
        """
        try:
            # Extract session information if this is a collaboration call
            session_info = kwargs.pop("__session", None)
            calling_agent = session_info["calling_agent"] if session_info else "unknown"
            
            # Validate input against schema and standards
            input_validation = self.validate_input(kwargs)
            if not input_validation["valid"]:
                return self._create_error_response(input_validation)
            
            # Parse and validate arguments
            validated_args = self.schema_model(**kwargs)
            args_dict = validated_args.model_dump()
            
            # Execute the tool's core logic
            result = await self.execute(args_dict)
            
            # Validate output against standards
            output_validation = self.validate_output(result)
            
            # Check if human review is required
            needs_review = self.requires_human_review(args_dict, result)
            human_verified = False
            
            if needs_review:
                # Request human review
                human_feedback = await self.hitl_manager.request_review(
                    self.name,
                    args_dict,
                    result,
                    calling_agent
                )
                
                # Apply human feedback to result
                if human_feedback.approved:
                    if human_feedback.modifications:
                        # Apply modifications to the result
                        # This is a simplified approach; a real implementation
                        # would need to handle modifications more carefully
                        result = {**result, **human_feedback.modifications}
                    human_verified = True
                else:
                    # Human rejected the result
                    return self._create_error_response({
                        "valid": False,
                        "violations": [
                            {
                                "field": "result",
                                "description": "Result rejected by human reviewer",
                                "recommendation": human_feedback.comments or "Contact administrator for details"
                            }
                        ]
                    })
            
            # Format the result
            formatted_result = self.format_result(result)
            
            # Add metadata to the result
            collaborating_agents = self._get_collaborating_agents(session_info)
            
            for part in formatted_result:
                if "metadata" not in part:
                    part["metadata"] = {}
                
                part["metadata"].update({
                    "standardsCompliance": output_validation,
                    "humanVerified": human_verified,
                    "collaboratingAgents": collaborating_agents
                })
            
            return formatted_result
            
        except Exception as e:
            logger.exception(f"Error executing tool {self.name}: {str(e)}")
            return self._create_error_response(str(e))
    
    async def execute(self, args: Dict[str, Any]) -> Any:
        """Execute the tool with the given arguments.
        
        This method must be implemented by subclasses.
        
        Args:
            args: Validated tool arguments
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Tool execution not implemented")
    
    def format_result(self, result: Any) -> List[Dict[str, Any]]:
        """Format the result for return to the agent.
        
        This method should be overridden by subclasses to provide
        a domain-specific formatting of the result.
        
        Args:
            result: Tool execution result
            
        Returns:
            List of formatted result parts
        """
        return [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    
    def validate_input(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the input against domain-specific standards.
        
        This method should be overridden by subclasses to provide
        domain-specific validation logic.
        
        Args:
            args: Tool arguments
            
        Returns:
            Dictionary containing validation results
        """
        return {
            "valid": True,
            "violations": [],
            "warnings": []
        }
    
    def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate the output against domain-specific standards.
        
        This method should be overridden by subclasses to provide
        domain-specific validation logic.
        
        Args:
            result: Tool execution result
            
        Returns:
            Dictionary containing validation results
        """
        return {
            "valid": True,
            "violations": [],
            "warnings": []
        }
    
    def requires_human_review(self, args: Dict[str, Any], result: Any) -> bool:
        """Determine if the result requires human review.
        
        This method should be overridden by subclasses to provide
        domain-specific criteria for when human review is needed.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            Boolean indicating if human review is required
        """
        return False
    
    def _create_error_response(self, error: Union[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create an error response.
        
        Args:
            error: Error information
            
        Returns:
            Formatted error response
        """
        if isinstance(error, str):
            message = f"Error: {error}"
        else:
            # Handle structured validation errors
            message = "Validation failed:\n"
            if "violations" in error:
                for violation in error["violations"]:
                    field = violation.get("field", "general")
                    desc = violation.get("description", "Unknown error")
                    rec = violation.get("recommendation", "")
                    message += f"- {field}: {desc}"
                    if rec:
                        message += f" ({rec})"
                    message += "\n"
        
        return [
            {
                "type": "text",
                "text": message,
                "metadata": {
                    "isError": True
                }
            }
        ]
    
    def _get_collaborating_agents(self, session_info: Dict[str, Any]) -> List[str]:
        """Get the list of collaborating agents for this tool execution.
        
        Args:
            session_info: Information about the collaboration session
            
        Returns:
            List of collaborating agent IDs
        """
        if not session_info:
            return []
        
        # Get the collaboration session
        session_id = session_info.get("id")
        if not session_id:
            return []
        
        registry = MCPToolRegistry()
        session = registry.get_collaboration_session(session_id)
        if not session:
            return []
        
        return session.participants