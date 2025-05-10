"""
HMS-SVC Integration Module

This module provides integration between the HMS-A2A framework and the HMS-SVC
API for Program and Protocol management. This enables A2A agents to work with
structured government and NGO programs and workflows.
"""

import logging
import json
import asyncio
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic, cast
import httpx

# Custom type definitions
from pydantic import BaseModel, Field

# A2A imports
from ..common.types import ValidationResult
from ..common.client.client import Client

# Configure logging
logger = logging.getLogger(__name__)


class ProgramStatus(str, Enum):
    """Status of a Program in HMS-SVC."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProtocolStatus(str, Enum):
    """Status of a Protocol in HMS-SVC."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ModuleType(str, Enum):
    """Types of modules available in HMS-SVC."""
    ACTIVITY = "activity"
    ASSESSMENT = "assessment"
    CHALLENGE = "challenge"
    CHECKPOINT = "checkpoint"
    DOCUMENT = "document"
    EVENT = "event"
    FOCUS = "focus"
    KPI = "kpi"
    NUDGE = "nudge"
    RESOURCE = "resource"
    SURVEY = "survey"
    TODO = "todo"


class Program(BaseModel):
    """Representation of a Program from HMS-SVC."""
    id: str
    name: str
    description: str
    status: ProgramStatus
    protocols: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class Protocol(BaseModel):
    """Representation of a Protocol from HMS-SVC."""
    id: str
    name: str
    description: str
    program_id: str
    status: ProtocolStatus
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str
    updated_at: str


class Module(BaseModel):
    """Representation of a Module from HMS-SVC."""
    id: str
    type: ModuleType
    name: str
    description: str
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class HMSSVCClient:
    """Client for interacting with the HMS-SVC API.
    
    This client provides methods for working with Programs, Protocols,
    and Modules in the HMS-SVC system.
    """
    
    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """Initialize the HMS-SVC client.
        
        Args:
            base_url: Base URL for the HMS-SVC API
            api_token: API token for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        
        # If token provided, add auth headers
        if self.api_token:
            self.client.headers.update({
                "Authorization": f"Bearer {self.api_token}"
            })
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the HMS-SVC API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Form data
            json_data: JSON data
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise Exception(f"HMS-SVC API error: {e.response.status_code} - {e.response.text}")
            
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise Exception(f"HMS-SVC API request failed: {str(e)}")
    
    #
    # Program methods
    #
    
    async def get_programs(
        self,
        status: Optional[ProgramStatus] = None,
        search: Optional[str] = None,
        limit: int = 10,
        page: int = 1
    ) -> List[Program]:
        """Get a list of programs.
        
        Args:
            status: Filter by program status
            search: Search term
            limit: Number of results per page
            page: Page number
            
        Returns:
            List of Program objects
        """
        params = {"limit": limit, "page": page}
        
        if status:
            params["status"] = status
        
        if search:
            params["search"] = search
        
        response = await self._request("GET", "api/programs", params=params)
        programs = [Program(**program) for program in response.get("data", [])]
        
        return programs
    
    async def get_program(self, program_id: str) -> Program:
        """Get a specific program by ID.
        
        Args:
            program_id: The ID of the program
            
        Returns:
            Program object
        """
        response = await self._request("GET", f"api/programs/{program_id}")
        return Program(**response.get("data", {}))
    
    async def create_program(
        self,
        name: str,
        description: str,
        status: ProgramStatus = ProgramStatus.DRAFT
    ) -> Program:
        """Create a new program.
        
        Args:
            name: Program name
            description: Program description
            status: Program status
            
        Returns:
            Created Program object
        """
        data = {
            "name": name,
            "description": description,
            "status": status
        }
        
        response = await self._request("POST", "api/programs", json_data=data)
        return Program(**response.get("data", {}))
    
    async def update_program(
        self,
        program_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ProgramStatus] = None
    ) -> Program:
        """Update an existing program.
        
        Args:
            program_id: The ID of the program to update
            name: New program name
            description: New program description
            status: New program status
            
        Returns:
            Updated Program object
        """
        data = {}
        
        if name is not None:
            data["name"] = name
        
        if description is not None:
            data["description"] = description
        
        if status is not None:
            data["status"] = status
        
        response = await self._request("PUT", f"api/programs/{program_id}", json_data=data)
        return Program(**response.get("data", {}))
    
    #
    # Protocol methods
    #
    
    async def get_protocols(
        self,
        program_id: Optional[str] = None,
        status: Optional[ProtocolStatus] = None,
        limit: int = 10,
        page: int = 1
    ) -> List[Protocol]:
        """Get a list of protocols.
        
        Args:
            program_id: Filter by program ID
            status: Filter by protocol status
            limit: Number of results per page
            page: Page number
            
        Returns:
            List of Protocol objects
        """
        params = {"limit": limit, "page": page}
        
        if program_id:
            params["program_id"] = program_id
        
        if status:
            params["status"] = status
        
        response = await self._request("GET", "api/protocols", params=params)
        protocols = [Protocol(**protocol) for protocol in response.get("data", [])]
        
        return protocols
    
    async def get_protocol(self, protocol_id: str) -> Protocol:
        """Get a specific protocol by ID.
        
        Args:
            protocol_id: The ID of the protocol
            
        Returns:
            Protocol object
        """
        response = await self._request("GET", f"api/protocols/{protocol_id}")
        return Protocol(**response.get("data", {}))
    
    async def create_protocol(
        self,
        program_id: str,
        name: str,
        description: str,
        steps: List[Dict[str, Any]] = None
    ) -> Protocol:
        """Create a new protocol.
        
        Args:
            program_id: ID of the program this protocol belongs to
            name: Protocol name
            description: Protocol description
            steps: List of protocol steps
            
        Returns:
            Created Protocol object
        """
        data = {
            "program_id": program_id,
            "name": name,
            "description": description
        }
        
        if steps:
            data["steps"] = steps
        
        response = await self._request("POST", "api/protocols", json_data=data)
        return Protocol(**response.get("data", {}))
    
    #
    # Module methods
    #
    
    async def get_modules(
        self,
        type: Optional[ModuleType] = None,
        search: Optional[str] = None,
        limit: int = 10,
        page: int = 1
    ) -> List[Module]:
        """Get a list of modules.
        
        Args:
            type: Filter by module type
            search: Search term
            limit: Number of results per page
            page: Page number
            
        Returns:
            List of Module objects
        """
        params = {"limit": limit, "page": page}
        
        if type:
            params["type"] = type
        
        if search:
            params["search"] = search
        
        response = await self._request("GET", "api/modules", params=params)
        modules = [Module(**module) for module in response.get("data", [])]
        
        return modules
    
    async def get_module(self, module_id: str) -> Module:
        """Get a specific module by ID.
        
        Args:
            module_id: The ID of the module
            
        Returns:
            Module object
        """
        response = await self._request("GET", f"api/modules/{module_id}")
        return Module(**response.get("data", {}))
    
    async def execute_module(
        self,
        module_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a module with the given input data.
        
        Args:
            module_id: The ID of the module to execute
            input_data: Input data for the module
            
        Returns:
            Module execution results
        """
        response = await self._request(
            "POST",
            f"api/modules/{module_id}/execute",
            json_data=input_data
        )
        
        return response.get("data", {})


class ProgramWorkflow:
    """Helper class for working with Program workflows.
    
    This class provides methods for working with Programs and their
    Protocols as a unified workflow.
    """
    
    def __init__(self, client: HMSSVCClient):
        """Initialize with an HMS-SVC client.
        
        Args:
            client: HMSSVCClient instance
        """
        self.client = client
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        protocols: List[Dict[str, Any]]
    ) -> Program:
        """Create a complete workflow with a program and protocols.
        
        Args:
            name: Program name
            description: Program description
            protocols: List of protocol configurations
            
        Returns:
            Created Program object
        """
        # Create the program
        program = await self.client.create_program(name, description)
        
        # Create each protocol
        for protocol_config in protocols:
            protocol_name = protocol_config.get("name", "Untitled Protocol")
            protocol_desc = protocol_config.get("description", "")
            protocol_steps = protocol_config.get("steps", [])
            
            await self.client.create_protocol(
                program_id=program.id,
                name=protocol_name,
                description=protocol_desc,
                steps=protocol_steps
            )
        
        # Return the updated program
        return await self.client.get_program(program.id)
    
    async def execute_workflow_step(
        self,
        protocol_id: str,
        step_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific step in a protocol workflow.
        
        Args:
            protocol_id: ID of the protocol
            step_id: ID of the step within the protocol
            input_data: Input data for the step
            
        Returns:
            Step execution results
        """
        response = await self.client._request(
            "POST",
            f"api/protocols/{protocol_id}/steps/{step_id}/execute",
            json_data=input_data
        )
        
        return response.get("data", {})
    
    async def get_workflow_status(self, program_id: str) -> Dict[str, Any]:
        """Get the status of a complete workflow.
        
        Args:
            program_id: ID of the program
            
        Returns:
            Workflow status information
        """
        program = await self.client.get_program(program_id)
        protocols = await self.client.get_protocols(program_id=program_id)
        
        protocol_statuses = {}
        for protocol in protocols:
            protocol_statuses[protocol.id] = {
                "name": protocol.name,
                "status": protocol.status,
                "steps": protocol.steps
            }
        
        return {
            "program": {
                "id": program.id,
                "name": program.name,
                "status": program.status
            },
            "protocols": protocol_statuses
        }