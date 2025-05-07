#!/usr/bin/env python3
"""
MCP Tool Registry

This module provides a comprehensive registry for Model Context Protocol (MCP) tools,
including permission management, discovery mechanisms, and validation against standards.
It serves as the central registry for all tools across specialized agents.

This implementation migrates and enhances the functionality from HMS-SME/lib/MCP.
"""

import os
import sys
import inspect
import importlib
import logging
import uuid
import json
import time
from datetime import datetime
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional, Type, Set, Union, Callable, Tuple

from pydantic import BaseModel, Field, create_model

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from specialized_agents.standards_validation import StandardsValidator, ValidationResult

# Configure logging
logger = logging.getLogger(__name__)


class ToolMetadata(BaseModel):
    """Metadata for a tool registered with the MCP Tool Registry."""
    
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    domains: List[str] = []
    standards: List[str] = []
    tags: List[str] = []
    requires_human_review: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class PermissionLevel(str):
    """Permission levels for tools."""
    
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    NONE = "none"


class ToolPermissions(BaseModel):
    """Permissions for a tool."""
    
    tool_id: str
    permission_level: str
    granted_to: List[str] = []
    restrictions: Dict[str, Any] = {}
    requires_approval: bool = False
    approval_domains: List[str] = []


class ToolAccessRequest(BaseModel):
    """Request for tool access."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_id: str
    requesting_domain: str
    permission_level: str
    purpose: str
    status: str = "pending"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    decided_at: Optional[str] = None
    decided_by: Optional[str] = None
    decision_reason: Optional[str] = None


class Tool:
    """Base class for MCP tools."""
    
    def __init__(
        self,
        func: Callable,
        name: str,
        description: str,
        version: str = "1.0.0",
        domains: List[str] = [],
        standards: List[str] = [],
        metadata: Dict[str, Any] = None,
        schema_model: Type[BaseModel] = None
    ):
        """Initialize a tool.
        
        Args:
            func: The function implementing the tool
            name: Tool name
            description: Tool description
            version: Tool version
            domains: Domains the tool belongs to
            standards: Standards the tool complies with
            metadata: Additional metadata
            schema_model: Input schema for the tool
        """
        self.func = func
        self.name = name
        self.description = description
        self.version = version
        self.domains = domains
        self.standards = standards
        self._metadata = metadata or {}
        self._schema_model = schema_model
        
        # Create schema model from function signature if not provided
        if not self._schema_model:
            self._create_schema_from_signature()
        
        # Set up tool ID
        self.id = f"{self.name}-{self.version}"
        
        # Wrap the function
        self._wrap_function()
    
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
    
    def _wrap_function(self):
        """Wrap the function with validation and logging."""
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            # Extract session context if present
            session_context = kwargs.pop('__session', None)
            
            # Log tool invocation
            logger.info(f"Tool invocation: {self.name}")
            
            # Validate input against schema
            validated = self.validate_input(kwargs)
            if not validated.is_valid:
                return self._create_error_response(validated)
            
            # Validate against standards
            if self.standards:
                validator = StandardsValidator()
                std_result = validator.validate_content(kwargs, standard_id=self.standards[0])
                if not std_result.is_valid:
                    return self._create_error_response(std_result)
            
            # Execute the tool
            start_time = time.time()
            
            try:
                result = self.func(*args, **kwargs)
                
                # Record execution metrics
                execution_time = time.time() - start_time
                logger.debug(f"Tool execution time: {execution_time:.2f}s")
                
                # Format the result
                return self._format_result(result, execution_time, session_context)
                
            except Exception as e:
                logger.exception(f"Error executing tool {self.name}: {str(e)}")
                return self._create_error_response(str(e))
        
        self.wrapped_func = wrapper
    
    def validate_input(self, kwargs: Dict[str, Any]) -> ValidationResult:
        """Validate input against the schema.
        
        Args:
            kwargs: Input arguments
            
        Returns:
            ValidationResult
        """
        try:
            # Validate against schema
            self._schema_model(**kwargs)
            return ValidationResult(is_valid=True)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                violations=[{
                    "field": str(e).split()[0].strip("'"),
                    "message": str(e),
                    "severity": "error"
                }]
            )
    
    def _create_error_response(self, error: Union[str, ValidationResult]) -> Dict[str, Any]:
        """Create an error response.
        
        Args:
            error: Error information
            
        Returns:
            Error response
        """
        if isinstance(error, str):
            message = {"error": error}
        else:
            # Process ValidationResult
            message = {
                "error": "Validation error",
                "violations": error.violations
            }
        
        return {
            "success": False,
            "error": message,
            "metadata": {
                "tool": self.name,
                "version": self.version,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _format_result(
        self, 
        result: Any, 
        execution_time: float,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format the tool result.
        
        Args:
            result: Raw result from tool execution
            execution_time: Time taken to execute the tool
            session_context: Session context if available
            
        Returns:
            Formatted result
        """
        # If result is already a dict with proper structure, just add metadata
        if isinstance(result, dict) and "success" in result:
            if "metadata" not in result:
                result["metadata"] = {}
                
            result["metadata"].update({
                "tool": self.name,
                "version": self.version,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
        
        # Otherwise, wrap the result
        return {
            "success": True,
            "result": result,
            "metadata": {
                "tool": self.name,
                "version": self.version,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "session": session_context
            }
        }
    
    def __call__(self, *args, **kwargs):
        """Make the tool callable."""
        return self.wrapped_func(*args, **kwargs)
    
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
            "schema": schema,
            "domains": self.domains,
            "standards": self.standards,
            "metadata": self._metadata
        }


class MCPToolRegistry:
    """Comprehensive registry for MCP tools."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(MCPToolRegistry, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the registry."""
        self.tools = {}  # Tool objects by ID
        self.domain_tools = {}  # Tools by domain
        self.category_tools = {}  # Tools by category
        self.standard_tools = {}  # Tools by standard
        
        # Security and permissions
        self.permissions = {}  # Tool permissions by ID
        self.access_requests = {}  # Access requests by request ID
        self.domain_permissions = {}  # Domain permissions
        
        # Discovery
        self.tool_tags = {}  # Tools by tag
        self.discovery_index = {}  # Full-text search index

        # Human-in-the-loop 
        self.approval_queue = {}  # Tools requiring approval
        self.approval_callbacks = {}  # Callbacks for approvals

        # Tool contexts for memory
        self.tool_contexts = {}  # Context for tools
        
        # Load tools
        self._auto_discover_tools()
    
    def register_tool(
        self,
        func=None,
        *,
        name: str = None,
        description: str = None,
        version: str = "1.0.0",
        domains: List[str] = None,
        standards: List[str] = None,
        tags: List[str] = None,
        category: str = None,
        metadata: Dict[str, Any] = None,
        require_human_review: bool = False,
        schema_model: Type[BaseModel] = None
    ):
        """Register a function as a tool.
        
        This can be used as a decorator or a function.
        
        Args:
            func: Function to register
            name: Tool name (defaults to function name)
            description: Tool description (defaults to function docstring)
            version: Tool version
            domains: Domains the tool belongs to
            standards: Standards the tool complies with
            tags: Tags for tool discovery
            category: Tool category
            metadata: Additional metadata
            require_human_review: Whether the tool requires human review
            schema_model: Input schema for the tool
            
        Returns:
            Decorator function or registered tool
        """
        # Use as decorator
        if func is None:
            return lambda f: self.register_tool(
                f,
                name=name,
                description=description,
                version=version,
                domains=domains or [],
                standards=standards or [],
                tags=tags or [],
                category=category,
                metadata=metadata or {},
                require_human_review=require_human_review,
                schema_model=schema_model
            )
        
        # Use function name if not provided
        if name is None:
            name = func.__name__
        
        # Use function docstring if description not provided
        if description is None and func.__doc__:
            description = func.__doc__.strip()
        elif description is None:
            description = f"Tool for {name}"
        
        # Normalize domains
        if domains is None:
            domains = []
        
        # Normalize standards
        if standards is None:
            standards = []
        
        # Normalize tags
        if tags is None:
            tags = []
        
        # Normalize metadata
        if metadata is None:
            metadata = {}
        
        # Add human review metadata
        metadata["require_human_review"] = require_human_review
        
        # Create tool
        tool = Tool(
            func=func,
            name=name,
            description=description,
            version=version,
            domains=domains,
            standards=standards,
            metadata=metadata,
            schema_model=schema_model
        )
        
        # Register the tool
        self._register_tool_object(tool, category, tags)
        
        return tool
    
    def _register_tool_object(
        self,
        tool: Tool,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """Register a tool object.
        
        Args:
            tool: Tool object
            category: Tool category
            tags: Tool tags
        """
        # Register by ID
        self.tools[tool.id] = tool
        
        # Register by domain
        for domain in tool.domains:
            if domain not in self.domain_tools:
                self.domain_tools[domain] = []
            self.domain_tools[domain].append(tool.id)
        
        # Register by category
        if category:
            if category not in self.category_tools:
                self.category_tools[category] = []
            self.category_tools[category].append(tool.id)
        
        # Register by standard
        for standard in tool.standards:
            if standard not in self.standard_tools:
                self.standard_tools[standard] = []
            self.standard_tools[standard].append(tool.id)
        
        # Register by tag
        if tags:
            for tag in tags:
                if tag not in self.tool_tags:
                    self.tool_tags[tag] = []
                self.tool_tags[tag].append(tool.id)
        
        # Add to discovery index
        self._index_tool(tool)
        
        # Set up default permissions
        if tool.id not in self.permissions:
            self.permissions[tool.id] = {
                "tool_id": tool.id,
                "permission_level": PermissionLevel.EXECUTE,
                "granted_to": tool.domains,
                "restrictions": {},
                "requires_approval": tool._metadata.get("require_human_review", False),
                "approval_domains": []
            }
        
        logger.info(f"Registered tool: {tool.id}")
    
    def _index_tool(self, tool: Tool):
        """Index a tool for discovery.
        
        Args:
            tool: Tool to index
        """
        # Create searchable text from tool metadata
        text = f"{tool.name} {tool.description} {' '.join(tool.domains)} {' '.join(tool.standards)}"
        
        # Add to full text index
        self.discovery_index[tool.id] = text.lower()
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get a tool by ID.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Tool object or None if not found
        """
        return self.tools.get(tool_id)
    
    def get_tools_for_domain(self, domain: str) -> List[Tool]:
        """Get tools for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of tools for the domain
        """
        tool_ids = self.domain_tools.get(domain, [])
        return [self.tools[tool_id] for tool_id in tool_ids if tool_id in self.tools]
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get tools by category.
        
        Args:
            category: Category name
            
        Returns:
            List of tools in the category
        """
        tool_ids = self.category_tools.get(category, [])
        return [self.tools[tool_id] for tool_id in tool_ids if tool_id in self.tools]
    
    def get_tools_by_standard(self, standard: str) -> List[Tool]:
        """Get tools that comply with a standard.
        
        Args:
            standard: Standard ID
            
        Returns:
            List of tools complying with the standard
        """
        tool_ids = self.standard_tools.get(standard, [])
        return [self.tools[tool_id] for tool_id in tool_ids if tool_id in self.tools]
    
    def get_tools_by_tag(self, tag: str) -> List[Tool]:
        """Get tools by tag.
        
        Args:
            tag: Tag name
            
        Returns:
            List of tools with the tag
        """
        tool_ids = self.tool_tags.get(tag, [])
        return [self.tools[tool_id] for tool_id in tool_ids if tool_id in self.tools]
    
    def search_tools(self, query: str) -> List[Tool]:
        """Search for tools.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tools
        """
        query_terms = query.lower().split()
        results = []
        
        for tool_id, indexed_text in self.discovery_index.items():
            # Check if all query terms are in the indexed text
            if all(term in indexed_text for term in query_terms):
                if tool_id in self.tools:
                    results.append(self.tools[tool_id])
        
        return results
    
    def get_tool_definition(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get a tool's definition.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Tool definition or None if not found
        """
        tool = self.get_tool(tool_id)
        if tool:
            return tool.get_definition()
        return None
    
    def execute_tool(
        self,
        tool_id: str,
        args: Dict[str, Any],
        calling_domain: str,
        session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool if the domain has permission.
        
        Args:
            tool_id: Tool ID
            args: Tool arguments
            calling_domain: Domain executing the tool
            session_context: Session context
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If the tool doesn't exist or the domain doesn't have permission
        """
        # Check if tool exists
        tool = self.get_tool(tool_id)
        if not tool:
            raise ValueError(f"Tool not found: {tool_id}")
        
        # Check domain permission
        if not self._domain_has_permission(calling_domain, tool_id, PermissionLevel.EXECUTE):
            raise ValueError(f"Domain {calling_domain} does not have permission to execute tool {tool_id}")
        
        # Add session context if provided
        if session_context:
            args["__session"] = session_context
        
        # Execute the tool
        return tool(**args)
    
    def set_tool_permission(
        self,
        tool_id: str,
        domain: str,
        permission_level: str,
        restrictions: Dict[str, Any] = None,
        requires_approval: bool = False,
        approval_domains: List[str] = None
    ):
        """Set permission for a domain to use a tool.
        
        Args:
            tool_id: Tool ID
            domain: Domain to grant permission to
            permission_level: Permission level
            restrictions: Additional restrictions
            requires_approval: Whether execution requires approval
            approval_domains: Domains that can approve execution
        """
        if tool_id not in self.permissions:
            self.permissions[tool_id] = {
                "tool_id": tool_id,
                "permission_level": permission_level,
                "granted_to": [domain],
                "restrictions": restrictions or {},
                "requires_approval": requires_approval,
                "approval_domains": approval_domains or []
            }
        else:
            # Update existing permissions
            tool_perms = self.permissions[tool_id]
            
            # Add domain if not already granted
            if domain not in tool_perms["granted_to"]:
                tool_perms["granted_to"].append(domain)
            
            # Update permission level if more permissive
            if self._permission_hierarchy(permission_level) > self._permission_hierarchy(tool_perms["permission_level"]):
                tool_perms["permission_level"] = permission_level
            
            # Update restrictions if provided
            if restrictions:
                tool_perms["restrictions"].update(restrictions)
            
            # Update approval requirements if provided
            if requires_approval is not None:
                tool_perms["requires_approval"] = requires_approval
            
            # Update approval domains if provided
            if approval_domains:
                tool_perms["approval_domains"] = approval_domains
    
    def _permission_hierarchy(self, permission: str) -> int:
        """Get the hierarchy level of a permission.
        
        Args:
            permission: Permission level
            
        Returns:
            Hierarchy level (higher means more permissive)
        """
        hierarchy = {
            PermissionLevel.NONE: 0,
            PermissionLevel.READ: 1,
            PermissionLevel.EXECUTE: 2,
            PermissionLevel.WRITE: 3,
            PermissionLevel.ADMIN: 4
        }
        return hierarchy.get(permission, 0)
    
    def _domain_has_permission(
        self,
        domain: str,
        tool_id: str,
        required_level: str
    ) -> bool:
        """Check if a domain has the required permission level for a tool.
        
        Args:
            domain: Domain to check
            tool_id: Tool ID
            required_level: Required permission level
            
        Returns:
            True if the domain has the required permission, False otherwise
        """
        if tool_id not in self.permissions:
            return False
        
        tool_perms = self.permissions[tool_id]
        
        # Check if domain is granted access
        if domain in tool_perms["granted_to"]:
            # Check permission level
            domain_level = tool_perms["permission_level"]
            return self._permission_hierarchy(domain_level) >= self._permission_hierarchy(required_level)
        
        return False
    
    def request_tool_access(
        self,
        tool_id: str,
        requesting_domain: str,
        permission_level: str,
        purpose: str
    ) -> str:
        """Request access to a tool.
        
        Args:
            tool_id: Tool ID
            requesting_domain: Domain requesting access
            permission_level: Requested permission level
            purpose: Purpose of the request
            
        Returns:
            Request ID
            
        Raises:
            ValueError: If the tool doesn't exist
        """
        # Check if tool exists
        if tool_id not in self.tools:
            raise ValueError(f"Tool not found: {tool_id}")
        
        # Create request
        request = ToolAccessRequest(
            tool_id=tool_id,
            requesting_domain=requesting_domain,
            permission_level=permission_level,
            purpose=purpose
        )
        
        # Store request
        self.access_requests[request.request_id] = request
        
        logger.info(f"Access request created: {request.request_id}")
        return request.request_id
    
    def approve_access_request(
        self,
        request_id: str,
        approved: bool,
        decided_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """Approve or deny an access request.
        
        Args:
            request_id: Request ID
            approved: Whether to approve the request
            decided_by: Domain making the decision
            reason: Reason for the decision
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the request doesn't exist
        """
        if request_id not in self.access_requests:
            raise ValueError(f"Access request not found: {request_id}")
        
        request = self.access_requests[request_id]
        
        # Update request
        request.status = "approved" if approved else "denied"
        request.decided_at = datetime.now().isoformat()
        request.decided_by = decided_by
        request.decision_reason = reason
        
        # If approved, grant permission
        if approved:
            self.set_tool_permission(
                request.tool_id,
                request.requesting_domain,
                request.permission_level
            )
        
        logger.info(f"Access request {request_id} {request.status}")
        return True
    
    def get_pending_access_requests(self) -> List[ToolAccessRequest]:
        """Get all pending access requests.
        
        Returns:
            List of pending access requests
        """
        return [
            request for request in self.access_requests.values()
            if request.status == "pending"
        ]
    
    def _auto_discover_tools(self):
        """Auto-discover tools in the specialized_agents directory."""
        # These are the known domains from the existing code structure
        domains = [
            "accounting",
            "agriculture",
            "education",
            "financial",
            "government",
            "healthcare",
            "legal",
            "nutrition",
            "socialwork",
            "telemedicine"
        ]
        
        # Load tools for each domain in parallel
        with ThreadPoolExecutor(max_workers=len(domains)) as executor:
            executor.map(self._load_domain_tools, domains)
    
    def _load_domain_tools(self, domain: str):
        """Load tools for a domain.
        
        Args:
            domain: Domain name
        """
        try:
            # Try to import the domain-specific tools module
            module_name = f"specialized_agents.{domain}.tools"
            module = importlib.import_module(module_name)
            
            # Check if the module has a register_tools function
            if hasattr(module, "register_tools") and callable(module.register_tools):
                module.register_tools(self)
                logger.info(f"Loaded tools for domain: {domain}")
            else:
                logger.info(f"No register_tools function found in {module_name}")
        except ImportError:
            logger.info(f"No tools module found for domain: {domain}")
        except Exception as e:
            logger.error(f"Error loading tools for domain {domain}: {str(e)}")


# Create singleton instance
registry = MCPToolRegistry()


def get_tool(tool_id: str) -> Optional[Tool]:
    """Get a tool by ID.
    
    Args:
        tool_id: Tool ID
        
    Returns:
        Tool object or None if not found
    """
    return registry.get_tool(tool_id)


def register_tool(
    func=None,
    *,
    name: str = None,
    description: str = None,
    version: str = "1.0.0",
    domains: List[str] = None,
    standards: List[str] = None,
    tags: List[str] = None,
    category: str = None,
    metadata: Dict[str, Any] = None,
    require_human_review: bool = False,
    schema_model: Type[BaseModel] = None
):
    """Register a function as a tool.
    
    This can be used as a decorator or a function.
    
    Args:
        func: Function to register
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        version: Tool version
        domains: Domains the tool belongs to
        standards: Standards the tool complies with
        tags: Tags for tool discovery
        category: Tool category
        metadata: Additional metadata
        require_human_review: Whether the tool requires human review
        schema_model: Input schema for the tool
        
    Returns:
        Decorator function or registered tool
    """
    return registry.register_tool(
        func,
        name=name,
        description=description,
        version=version,
        domains=domains,
        standards=standards,
        tags=tags,
        category=category,
        metadata=metadata,
        require_human_review=require_human_review,
        schema_model=schema_model
    )


def execute_tool(
    tool_id: str,
    args: Dict[str, Any],
    calling_domain: str,
    session_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute a tool if the domain has permission.
    
    Args:
        tool_id: Tool ID
        args: Tool arguments
        calling_domain: Domain executing the tool
        session_context: Session context
        
    Returns:
        Tool execution result
        
    Raises:
        ValueError: If the tool doesn't exist or the domain doesn't have permission
    """
    return registry.execute_tool(tool_id, args, calling_domain, session_context)


def get_tools_for_domain(domain: str) -> List[Tool]:
    """Get tools for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        List of tools for the domain
    """
    return registry.get_tools_for_domain(domain)


def search_tools(query: str) -> List[Tool]:
    """Search for tools.
    
    Args:
        query: Search query
        
    Returns:
        List of matching tools
    """
    return registry.search_tools(query)


def get_tool_definition(tool_id: str) -> Optional[Dict[str, Any]]:
    """Get a tool's definition.
    
    Args:
        tool_id: Tool ID
        
    Returns:
        Tool definition or None if not found
    """
    return registry.get_tool_definition(tool_id)


def set_tool_permission(
    tool_id: str,
    domain: str,
    permission_level: str,
    restrictions: Dict[str, Any] = None,
    requires_approval: bool = False,
    approval_domains: List[str] = None
):
    """Set permission for a domain to use a tool.
    
    Args:
        tool_id: Tool ID
        domain: Domain to grant permission to
        permission_level: Permission level
        restrictions: Additional restrictions
        requires_approval: Whether execution requires approval
        approval_domains: Domains that can approve execution
    """
    registry.set_tool_permission(
        tool_id,
        domain,
        permission_level,
        restrictions,
        requires_approval,
        approval_domains
    )


def request_tool_access(
    tool_id: str,
    requesting_domain: str,
    permission_level: str,
    purpose: str
) -> str:
    """Request access to a tool.
    
    Args:
        tool_id: Tool ID
        requesting_domain: Domain requesting access
        permission_level: Requested permission level
        purpose: Purpose of the request
        
    Returns:
        Request ID
        
    Raises:
        ValueError: If the tool doesn't exist
    """
    return registry.request_tool_access(tool_id, requesting_domain, permission_level, purpose)


def approve_access_request(
    request_id: str,
    approved: bool,
    decided_by: str,
    reason: Optional[str] = None
) -> bool:
    """Approve or deny an access request.
    
    Args:
        request_id: Request ID
        approved: Whether to approve the request
        decided_by: Domain making the decision
        reason: Reason for the decision
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If the request doesn't exist
    """
    return registry.approve_access_request(request_id, approved, decided_by, reason)


def get_pending_access_requests() -> List[ToolAccessRequest]:
    """Get all pending access requests.
    
    Returns:
        List of pending access requests
    """
    return registry.get_pending_access_requests()


# Initialize tools
def initialize():
    """Initialize the MCP Tool Registry."""
    registry._auto_discover_tools()
    logger.info("MCP Tool Registry initialized")


# Auto-initialize when imported
initialize()