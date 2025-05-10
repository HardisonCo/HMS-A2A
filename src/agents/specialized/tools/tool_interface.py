#!/usr/bin/env python3
"""
MCP Tool Interface

This module defines the standard interface that all MCP tools must implement,
including common validation patterns, input/output handling, and integration
with the standards validation framework.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Type, Union, Callable
from pydantic import BaseModel, Field, create_model
import inspect
import json
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Standard tool categories in MCP."""
    
    DATA_RETRIEVAL = "data_retrieval"
    DATA_TRANSFORMATION = "data_transformation"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_GENERATION = "content_generation"
    DECISION_SUPPORT = "decision_support"
    COLLABORATION = "collaboration"
    INFORMATION_EXCHANGE = "information_exchange"
    STANDARDS_VALIDATION = "standards_validation"
    DOMAIN_SPECIFIC = "domain_specific"
    UTILITY = "utility"


class ToolContext(BaseModel):
    """Context data for a tool session."""
    
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    calling_domain: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    previous_results: List[Dict[str, Any]] = []
    shared_data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class ToolResult(BaseModel):
    """Standard result format for all MCP tools."""
    
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}


class MCPToolInterface(ABC):
    """Base interface for all MCP-compliant tools."""
    
    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """Get the tool definition.
        
        Returns:
            Tool definition including schema, metadata, etc.
        """
        pass
    
    @abstractmethod
    def validate_input(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input against schema and standards.
        
        Args:
            args: Tool arguments
            
        Returns:
            Validation result
        """
        pass
    
    @abstractmethod
    def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output against standards.
        
        Args:
            result: Tool execution result
            
        Returns:
            Validation result
        """
        pass
    
    @abstractmethod
    def execute(self, args: Dict[str, Any], context: Optional[ToolContext] = None) -> ToolResult:
        """Execute the tool.
        
        Args:
            args: Tool arguments
            context: Tool execution context
            
        Returns:
            Tool execution result
        """
        pass
    
    @abstractmethod
    def requires_human_review(self, args: Dict[str, Any], result: Any) -> bool:
        """Determine if the result requires human review.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            True if human review is required, False otherwise
        """
        pass


class BaseMCPTool(MCPToolInterface):
    """Base implementation of the MCP tool interface."""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        version: str = "1.0.0",
        category: Union[str, ToolCategory] = ToolCategory.UTILITY,
        domains: List[str] = None,
        standards: List[str] = None,
        tags: List[str] = None,
        schema_model: Type[BaseModel] = None,
        metadata: Dict[str, Any] = None,
        require_human_review: bool = False
    ):
        """Initialize a base MCP tool.
        
        Args:
            name: Tool name
            description: Tool description
            func: Function implementing the tool
            version: Tool version
            category: Tool category
            domains: Domains the tool belongs to
            standards: Standards the tool complies with
            tags: Tags for tool discovery
            schema_model: Input schema model
            metadata: Additional metadata
            require_human_review: Whether the tool requires human review
        """
        self.name = name
        self.description = description
        self.func = func
        self.version = version
        self.category = category
        self.domains = domains or []
        self.standards = standards or []
        self.tags = tags or []
        self._schema_model = schema_model
        self.metadata = metadata or {}
        self.require_human_review = require_human_review
        
        # Set tool ID
        self.id = f"{self.name}-{self.version}"
        
        # Create schema model if not provided
        if not self._schema_model:
            self._create_schema_from_signature()
    
    def _create_schema_from_signature(self):
        """Create a Pydantic model from function signature."""
        sig = inspect.signature(self.func)
        fields = {}
        
        for name, param in sig.parameters.items():
            # Skip 'self' for methods
            if name == 'self':
                continue
                
            # Determine type annotation
            if param.annotation is inspect.Parameter.empty:
                type_annotation = Any
            else:
                type_annotation = param.annotation
            
            # Determine default value
            if param.default is inspect.Parameter.empty:
                fields[name] = (type_annotation, ...)
            else:
                fields[name] = (type_annotation, param.default)
        
        # Create and store the schema model
        self._schema_model = create_model(f"{self.name.capitalize()}Schema", **fields)
    
    def get_definition(self) -> Dict[str, Any]:
        """Get the tool definition.
        
        Returns:
            Tool definition
        """
        schema = self._schema_model.model_json_schema()
        
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category if isinstance(self.category, str) else self.category.value,
            "domains": self.domains,
            "standards": self.standards,
            "tags": self.tags,
            "schema": schema,
            "metadata": self.metadata,
            "require_human_review": self.require_human_review
        }
    
    def validate_input(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input against schema and standards.
        
        Args:
            args: Tool arguments
            
        Returns:
            Validation result
        """
        try:
            # Validate against schema
            validated_args = self._schema_model(**args)
            
            # Basic validation successful
            result = {
                "valid": True,
                "validated_args": validated_args.model_dump(),
                "warnings": []
            }
            
            # Additional validation against standards
            if self.standards:
                try:
                    # Import locally to avoid circular imports
                    from specialized_agents.standards_validation import StandardsValidator
                    
                    validator = StandardsValidator()
                    for standard in self.standards:
                        # Validate tool inputs against standard
                        std_result = validator.validate_content(
                            args, 
                            standard_id=standard,
                            context={"tool": self.name, "input_validation": True}
                        )
                        
                        # Add warnings for minor violations
                        for violation in std_result.violations:
                            if violation.get("severity") == "warning":
                                result["warnings"].append(violation)
                            
                            # Fail validation for serious violations
                            elif violation.get("severity") in ["error", "critical"]:
                                result["valid"] = False
                                if "violations" not in result:
                                    result["violations"] = []
                                result["violations"].append(violation)
                
                except ImportError:
                    # Standards validator not available, skip standards validation
                    result["warnings"].append(
                        {"message": "Standards validation skipped: validator not available"}
                    )
            
            return result
            
        except Exception as e:
            # Failed schema validation
            return {
                "valid": False,
                "violations": [
                    {
                        "field": str(e).split()[0].strip("'") if hasattr(e, "__str__") else "unknown",
                        "message": str(e),
                        "severity": "error"
                    }
                ]
            }
    
    def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output against standards.
        
        Args:
            result: Tool execution result
            
        Returns:
            Validation result
        """
        # Basic validation
        output_valid = True
        violations = []
        warnings = []
        
        # Check if result is valid
        if result is None:
            violations.append({
                "field": "result",
                "message": "Tool returned None",
                "severity": "error"
            })
            output_valid = False
        
        # Additional validation against standards
        if self.standards and output_valid:
            try:
                # Import locally to avoid circular imports
                from specialized_agents.standards_validation import StandardsValidator
                
                validator = StandardsValidator()
                for standard in self.standards:
                    # Validate tool output against standard
                    std_result = validator.validate_content(
                        result, 
                        standard_id=standard,
                        context={"tool": self.name, "output_validation": True}
                    )
                    
                    # Add warnings for minor violations
                    for violation in std_result.violations:
                        if violation.get("severity") == "warning":
                            warnings.append(violation)
                        
                        # Add serious violations
                        elif violation.get("severity") in ["error", "critical"]:
                            violations.append(violation)
            
            except ImportError:
                # Standards validator not available, skip standards validation
                warnings.append(
                    {"message": "Standards validation skipped: validator not available"}
                )
        
        # Determine overall validity
        if violations:
            output_valid = False
        
        return {
            "valid": output_valid,
            "violations": violations,
            "warnings": warnings
        }
    
    def execute(self, args: Dict[str, Any], context: Optional[ToolContext] = None) -> ToolResult:
        """Execute the tool.
        
        Args:
            args: Tool arguments
            context: Tool execution context
            
        Returns:
            Tool execution result
        """
        try:
            # Validate input
            input_validation = self.validate_input(args)
            if not input_validation["valid"]:
                return ToolResult(
                    success=False,
                    error="Input validation failed",
                    metadata={
                        "tool": self.name,
                        "validation_errors": input_validation.get("violations", [])
                    }
                )
            
            # Get validated args
            validated_args = input_validation.get("validated_args", args)
            
            # Include context if needed
            if context and inspect.signature(self.func).parameters.get("context"):
                result = self.func(**validated_args, context=context)
            else:
                result = self.func(**validated_args)
            
            # Validate output
            output_validation = self.validate_output(result)
            
            # Build result
            metadata = {
                "tool": self.name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "validation_warnings": output_validation.get("warnings", [])
            }
            
            # Include context in metadata if provided
            if context:
                metadata["session_id"] = context.session_id
                metadata["calling_domain"] = context.calling_domain
            
            # Check if validation failed
            if not output_validation["valid"]:
                return ToolResult(
                    success=False,
                    error="Output validation failed",
                    data=result,  # Include the result even though validation failed
                    metadata={
                        **metadata,
                        "validation_errors": output_validation.get("violations", [])
                    }
                )
            
            # Return successful result
            return ToolResult(
                success=True,
                data=result,
                warnings=[w.get("message") for w in output_validation.get("warnings", [])],
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Error executing tool {self.name}: {str(e)}")
            
            return ToolResult(
                success=False,
                error=str(e),
                metadata={
                    "tool": self.name,
                    "version": self.version,
                    "timestamp": datetime.now().isoformat(),
                    "exception_type": type(e).__name__
                }
            )
    
    def requires_human_review(self, args: Dict[str, Any], result: Any) -> bool:
        """Determine if the result requires human review.
        
        This base implementation checks the tool's require_human_review flag.
        Subclasses can override this method to implement more sophisticated logic.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            True if human review is required, False otherwise
        """
        return self.require_human_review
    
    def __call__(self, *args, **kwargs):
        """Make the tool callable."""
        context = kwargs.pop("__context", None)
        return self.execute(kwargs, context)


class DomainTool(BaseMCPTool):
    """Tool for a specific domain."""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        domain: str,
        standards: List[str] = None,
        **kwargs
    ):
        """Initialize a domain-specific tool.
        
        Args:
            name: Tool name
            description: Tool description
            func: Function implementing the tool
            domain: Primary domain
            standards: Standards the tool complies with
            **kwargs: Additional arguments for BaseMCPTool
        """
        super().__init__(
            name=name,
            description=description,
            func=func,
            domains=[domain],
            standards=standards,
            category=ToolCategory.DOMAIN_SPECIFIC,
            **kwargs
        )
        self.domain = domain
    
    def requires_human_review(self, args: Dict[str, Any], result: Any) -> bool:
        """Determine if the result requires human review.
        
        For domain tools, check sensitivity of the domain and result impact.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            True if human review is required, False otherwise
        """
        # Always require review if the base flag is set
        if self.require_human_review:
            return True
        
        # Check for sensitive domains that always need review
        sensitive_domains = ["healthcare", "legal", "financial"]
        if self.domain in sensitive_domains:
            # Check result for potentially sensitive information
            if result and isinstance(result, dict):
                # Check for high impact indicators
                if result.get("impact") == "high":
                    return True
                
                # Check for monetary values above thresholds
                if isinstance(result.get("amount"), (int, float)) and result.get("amount", 0) > 10000:
                    return True
        
        return False


class ValidationTool(BaseMCPTool):
    """Tool for standards validation."""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        standards: List[str],
        **kwargs
    ):
        """Initialize a validation tool.
        
        Args:
            name: Tool name
            description: Tool description
            func: Function implementing the tool
            standards: Standards the tool validates against
            **kwargs: Additional arguments for BaseMCPTool
        """
        super().__init__(
            name=name,
            description=description,
            func=func,
            standards=standards,
            category=ToolCategory.STANDARDS_VALIDATION,
            **kwargs
        )
    
    def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output for validation tools.
        
        For validation tools, the result should be a ValidationResult.
        
        Args:
            result: Tool execution result
            
        Returns:
            Validation result
        """
        # Basic validation
        if result is None:
            return {
                "valid": False,
                "violations": [
                    {
                        "field": "result",
                        "message": "Validation tool returned None",
                        "severity": "error"
                    }
                ]
            }
        
        # Check if result has expected validation fields
        expected_fields = ["is_valid", "violations"]
        missing_fields = [field for field in expected_fields if not hasattr(result, field)]
        
        if missing_fields:
            return {
                "valid": False,
                "violations": [
                    {
                        "field": "result",
                        "message": f"Validation result missing required fields: {', '.join(missing_fields)}",
                        "severity": "error"
                    }
                ]
            }
        
        # Validation passed
        return {
            "valid": True,
            "warnings": []
        }


class CollaborationTool(BaseMCPTool):
    """Tool for agent collaboration."""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        collaboration_type: str,
        **kwargs
    ):
        """Initialize a collaboration tool.
        
        Args:
            name: Tool name
            description: Tool description
            func: Function implementing the tool
            collaboration_type: Type of collaboration
            **kwargs: Additional arguments for BaseMCPTool
        """
        super().__init__(
            name=name,
            description=description,
            func=func,
            category=ToolCategory.COLLABORATION,
            **kwargs
        )
        self.collaboration_type = collaboration_type
        
        # Add collaboration type to metadata
        self.metadata["collaboration_type"] = collaboration_type
    
    def execute(self, args: Dict[str, Any], context: Optional[ToolContext] = None) -> ToolResult:
        """Execute the collaboration tool.
        
        Collaboration tools require a context.
        
        Args:
            args: Tool arguments
            context: Tool execution context
            
        Returns:
            Tool execution result
        """
        if not context:
            # Create minimal context if none provided
            context = ToolContext(
                calling_domain="unknown",
                metadata={"auto_created": True}
            )
        
        # Add collaboration type to context
        context.metadata["collaboration_type"] = self.collaboration_type
        
        # Execute with enhanced context
        return super().execute(args, context)


def create_tool(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tool_type: str = "base",
    **kwargs
) -> MCPToolInterface:
    """Factory function to create the appropriate tool type.
    
    Args:
        func: Function implementing the tool
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        tool_type: Type of tool to create
        **kwargs: Additional arguments for the tool constructor
        
    Returns:
        Created tool
        
    Raises:
        ValueError: If an invalid tool type is specified
    """
    # Use function name if not provided
    if name is None:
        name = func.__name__
    
    # Use function docstring if description not provided
    if description is None and func.__doc__:
        description = func.__doc__.strip()
    elif description is None:
        description = f"Tool for {name}"
    
    # Create the appropriate tool type
    if tool_type == "base":
        return BaseMCPTool(name=name, description=description, func=func, **kwargs)
    elif tool_type == "domain":
        return DomainTool(name=name, description=description, func=func, **kwargs)
    elif tool_type == "validation":
        return ValidationTool(name=name, description=description, func=func, **kwargs)
    elif tool_type == "collaboration":
        return CollaborationTool(name=name, description=description, func=func, **kwargs)
    else:
        raise ValueError(f"Invalid tool type: {tool_type}")


def tool_decorator(
    name: Optional[str] = None,
    description: Optional[str] = None,
    tool_type: str = "base",
    **kwargs
):
    """Decorator to create and register a tool.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        tool_type: Type of tool to create
        **kwargs: Additional arguments for the tool constructor
        
    Returns:
        Decorator function
    """
    def decorator(func):
        tool = create_tool(func, name, description, tool_type, **kwargs)
        
        # Register tool if registry is available
        try:
            from specialized_agents.tools.mcp_registry import registry
            registry.register_tool(tool)
        except ImportError:
            logger.warning("MCP Tool Registry not available, tool not registered")
        
        return tool
    
    return decorator