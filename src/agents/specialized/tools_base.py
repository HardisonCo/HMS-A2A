"""
Standards-Compliant Tools Base Module

This module provides the base classes for creating standards-compliant tools
that can be used by specialized agents across various domains.
"""

from typing import Dict, Any, List, Optional, Type, Union, TypeVar, Generic, Callable
from pydantic import BaseModel, Field, create_model
from enum import Enum
import asyncio
import inspect
from src.agents.specialized.standards_validation import StandardsValidator, ValidationResult


# Type for tool input model
T = TypeVar('T', bound=BaseModel)
# Type for tool output
R = TypeVar('R')


class ToolMetadata(BaseModel):
    """Metadata about a tool's characteristics."""
    
    title: str
    read_only: bool = True
    destructive: bool = False
    idempotent: bool = True
    open_world: bool = False
    description: Optional[str] = None


class ContentPart(BaseModel):
    """A content part in a tool result."""
    
    class ContentType(str, Enum):
        TEXT = "text"
        DATA = "data"
        FILE = "file"
    
    type: ContentType
    content: Union[str, Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class StandardsCompliantTool(Generic[T, R]):
    """Base class for standards-compliant tools.
    
    This generic base class provides a framework for creating tools that
    enforce standards compliance across different domains.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Type[T],
        supported_standards: List[str],
        domain: str,
        metadata: ToolMetadata,
    ):
        """Initialize a standards-compliant tool.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            input_schema: The pydantic model that defines the tool's input schema
            supported_standards: List of standards supported by this tool
            domain: The industry domain this tool belongs to
            metadata: Tool metadata including title, destructiveness, etc.
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.supported_standards = supported_standards
        self.domain = domain
        self.metadata = metadata
        self.validator = StandardsValidator(domain, supported_standards)
    
    async def call(self, args: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call the tool with the provided arguments.
        
        Args:
            args: The arguments to pass to the tool
            session_context: Optional session context information
            
        Returns:
            Tool result
            
        Raises:
            ValueError: If arguments are invalid
            StandardsComplianceError: If the operation would violate standards
        """
        # Validate input against schema
        try:
            validated_input = self.input_schema(**args)
        except Exception as e:
            raise ValueError(f"Invalid arguments: {str(e)}")
        
        # Extract standards metadata if provided
        standards_metadata = None
        if session_context and "standards_metadata" in session_context:
            standards_metadata = session_context["standards_metadata"]
        
        # Pre-execution validation
        if not self.metadata.read_only:
            validation_result = self.validate_request(validated_input, standards_metadata)
            if not validation_result.valid:
                critical_issues = validation_result.get_critical_issues()
                if critical_issues:
                    issue_descriptions = [f"{i.severity}: {i.description}" for i in critical_issues]
                    raise StandardsComplianceError(
                        f"Operation would violate standards compliance: {', '.join(issue_descriptions)}"
                    )
        
        # Execute the tool
        result = await self.execute(validated_input, session_context)
        
        # Post-execution validation for non-read-only operations
        if not self.metadata.read_only:
            validation_result = self.validate_result(result, standards_metadata)
            if not validation_result.valid:
                critical_issues = validation_result.get_critical_issues()
                if critical_issues:
                    # This would typically log the issue but still return the result
                    # since the operation has already been performed
                    issue_descriptions = [f"{i.severity}: {i.description}" for i in critical_issues]
                    print(f"WARNING: Result may violate standards: {', '.join(issue_descriptions)}")
        
        # Format the result
        formatted_result = self.format_result(result)
        
        # Convert to dictionary for return
        return {
            "tool": self.name,
            "status": "success",
            "result": result if isinstance(result, dict) else self._convert_result_to_dict(result),
            "parts": [part.dict() for part in formatted_result],
            "requires_human_review": self.requires_human_review(validated_input, result)
        }
    
    async def execute(self, args: T, session_context: Optional[Dict[str, Any]] = None) -> R:
        """Execute the tool with validated arguments.
        
        This method should be implemented by subclasses.
        
        Args:
            args: The validated arguments
            session_context: Optional session context information
            
        Returns:
            Tool result
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def format_result(self, result: R) -> List[ContentPart]:
        """Format the result for display.
        
        Args:
            result: The tool result
            
        Returns:
            List of content parts
        """
        # Default implementation converts to string
        return [
            ContentPart(
                type=ContentPart.ContentType.TEXT,
                content=str(result)
            )
        ]
    
    def validate_request(self, args: T, standards_metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate the request against standards.
        
        Args:
            args: The validated arguments
            standards_metadata: Optional standards metadata
            
        Returns:
            ValidationResult containing validation status and issues
        """
        # Convert args to dict for validation
        args_dict = args.dict() if hasattr(args, "dict") else args
        
        # Use the standards validator
        return self.validator.validate_content(args_dict, standards_metadata)
    
    def validate_result(self, result: R, standards_metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate the result against standards.
        
        Args:
            result: The tool result
            standards_metadata: Optional standards metadata
            
        Returns:
            ValidationResult containing validation status and issues
        """
        # Convert result to string or dict for validation
        result_data = self._convert_result_to_dict(result)
        
        # Use the standards validator
        return self.validator.validate_content(result_data, standards_metadata)
    
    def requires_human_review(self, args: T, result: R) -> bool:
        """Determine if human review is required for this operation.
        
        Args:
            args: The validated arguments
            result: The tool result
            
        Returns:
            Boolean indicating if human review is required
        """
        # Default implementation requires human review for destructive operations
        return self.metadata.destructive
    
    def _convert_result_to_dict(self, result: R) -> Dict[str, Any]:
        """Convert the result to a dictionary.
        
        Args:
            result: The tool result
            
        Returns:
            Dictionary representation of the result
        """
        if hasattr(result, "dict") and callable(getattr(result, "dict")):
            return result.dict()
        elif isinstance(result, dict):
            return result
        else:
            # For simple types, create a wrapper dict
            return {"value": result}


class StandardsComplianceError(Exception):
    """Exception raised when an operation would violate standards compliance."""
    pass


def create_tool_input_model(
    name: str, 
    fields: Dict[str, Any], 
    docstring: Optional[str] = None
) -> Type[BaseModel]:
    """Create a pydantic model for tool input.
    
    Args:
        name: The name of the model
        fields: Dictionary of field names and types
        docstring: Optional docstring for the model
        
    Returns:
        Pydantic model class
    """
    model = create_model(name, **fields)
    
    if docstring:
        model.__doc__ = docstring
    
    return model