"""
HMS-SVC MCP Tools

This module provides MCP tools for integrating with HMS-SVC Programs, Protocols, and Modules.
These tools can be used by agents in the HMS-A2A framework.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, cast
from enum import Enum

from pydantic import BaseModel, Field

from ..graph.a2a_tools import BaseTool
from .hms_svc_integration import (
    HMSSVCClient,
    ProgramWorkflow,
    ProgramStatus,
    ProtocolStatus,
    ModuleType,
    Program,
    Protocol,
    Module
)

# Configure logging
logger = logging.getLogger(__name__)


class ProgramMCPTool(BaseTool):
    """MCP tool for working with HMS-SVC Programs.
    
    This tool allows agents to create, retrieve, and manage Programs
    in the HMS-SVC system.
    """
    
    name = "hms_svc_program"
    description = """
    Use this tool to work with HMS-SVC Programs.
    You can create, retrieve, update, and manage programs.
    
    Programs are top-level entities representing a series of government or NGO engagements
    that civilians follow, such as applying for benefits, complying with regulations, etc.
    """
    
    client: HMSSVCClient = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        **kwargs
    ):
        """Initialize the ProgramMCPTool.
        
        Args:
            base_url: Base URL for the HMS-SVC API
            api_token: API token for authentication
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)
        self.client = HMSSVCClient(base_url, api_token)
    
    async def _run(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute an action on HMS-SVC Programs.
        
        Args:
            action: The action to perform (list, get, create, update)
            **kwargs: Parameters for the action
            
        Returns:
            Results of the action
        """
        try:
            if action == "list":
                status = kwargs.get("status")
                if status and not isinstance(status, ProgramStatus):
                    status = ProgramStatus(status)
                
                programs = await self.client.get_programs(
                    status=status,
                    search=kwargs.get("search"),
                    limit=kwargs.get("limit", 10),
                    page=kwargs.get("page", 1)
                )
                
                return {
                    "status": "success",
                    "programs": [program.dict() for program in programs]
                }
                
            elif action == "get":
                program_id = kwargs.get("program_id")
                if not program_id:
                    return {
                        "status": "error",
                        "error": "program_id is required for get action"
                    }
                
                program = await self.client.get_program(program_id)
                return {
                    "status": "success",
                    "program": program.dict()
                }
                
            elif action == "create":
                name = kwargs.get("name")
                description = kwargs.get("description", "")
                
                if not name:
                    return {
                        "status": "error",
                        "error": "name is required for create action"
                    }
                
                status_str = kwargs.get("status", "draft")
                status = ProgramStatus(status_str)
                
                program = await self.client.create_program(
                    name=name,
                    description=description,
                    status=status
                )
                
                return {
                    "status": "success",
                    "program": program.dict()
                }
                
            elif action == "update":
                program_id = kwargs.get("program_id")
                if not program_id:
                    return {
                        "status": "error",
                        "error": "program_id is required for update action"
                    }
                
                name = kwargs.get("name")
                description = kwargs.get("description")
                
                status_str = kwargs.get("status")
                status = ProgramStatus(status_str) if status_str else None
                
                program = await self.client.update_program(
                    program_id=program_id,
                    name=name,
                    description=description,
                    status=status
                )
                
                return {
                    "status": "success",
                    "program": program.dict()
                }
                
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            logger.error(f"Error executing ProgramMCPTool: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class ProtocolMCPTool(BaseTool):
    """MCP tool for working with HMS-SVC Protocols.
    
    This tool allows agents to create, retrieve, and manage Protocols
    in the HMS-SVC system.
    """
    
    name = "hms_svc_protocol"
    description = """
    Use this tool to work with HMS-SVC Protocols.
    You can create, retrieve, and manage protocols in programs.
    
    Protocols define step-by-step workflows for programs, specifying the
    sequence of actions, assessments, and checkpoints that must be completed.
    """
    
    client: HMSSVCClient = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        **kwargs
    ):
        """Initialize the ProtocolMCPTool.
        
        Args:
            base_url: Base URL for the HMS-SVC API
            api_token: API token for authentication
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)
        self.client = HMSSVCClient(base_url, api_token)
    
    async def _run(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute an action on HMS-SVC Protocols.
        
        Args:
            action: The action to perform (list, get, create)
            **kwargs: Parameters for the action
            
        Returns:
            Results of the action
        """
        try:
            if action == "list":
                program_id = kwargs.get("program_id")
                
                status_str = kwargs.get("status")
                status = ProtocolStatus(status_str) if status_str else None
                
                protocols = await self.client.get_protocols(
                    program_id=program_id,
                    status=status,
                    limit=kwargs.get("limit", 10),
                    page=kwargs.get("page", 1)
                )
                
                return {
                    "status": "success",
                    "protocols": [protocol.dict() for protocol in protocols]
                }
                
            elif action == "get":
                protocol_id = kwargs.get("protocol_id")
                if not protocol_id:
                    return {
                        "status": "error",
                        "error": "protocol_id is required for get action"
                    }
                
                protocol = await self.client.get_protocol(protocol_id)
                return {
                    "status": "success",
                    "protocol": protocol.dict()
                }
                
            elif action == "create":
                program_id = kwargs.get("program_id")
                name = kwargs.get("name")
                description = kwargs.get("description", "")
                steps = kwargs.get("steps", [])
                
                if not program_id:
                    return {
                        "status": "error",
                        "error": "program_id is required for create action"
                    }
                
                if not name:
                    return {
                        "status": "error",
                        "error": "name is required for create action"
                    }
                
                protocol = await self.client.create_protocol(
                    program_id=program_id,
                    name=name,
                    description=description,
                    steps=steps
                )
                
                return {
                    "status": "success",
                    "protocol": protocol.dict()
                }
                
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            logger.error(f"Error executing ProtocolMCPTool: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class ModuleMCPTool(BaseTool):
    """MCP tool for working with HMS-SVC Modules.
    
    This tool allows agents to retrieve and execute Modules
    in the HMS-SVC system.
    """
    
    name = "hms_svc_module"
    description = """
    Use this tool to work with HMS-SVC Modules.
    You can list, retrieve, and execute modules.
    
    Modules are specialized components used within protocols for various purposes:
    - Assessment: Collect and evaluate information
    - KPI: Track key performance indicators
    - Nudge: Send notifications and reminders
    - Activity: Define tasks for users to complete
    - And more
    """
    
    client: HMSSVCClient = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        **kwargs
    ):
        """Initialize the ModuleMCPTool.
        
        Args:
            base_url: Base URL for the HMS-SVC API
            api_token: API token for authentication
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)
        self.client = HMSSVCClient(base_url, api_token)
    
    async def _run(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute an action on HMS-SVC Modules.
        
        Args:
            action: The action to perform (list, get, execute)
            **kwargs: Parameters for the action
            
        Returns:
            Results of the action
        """
        try:
            if action == "list":
                type_str = kwargs.get("type")
                type_enum = ModuleType(type_str) if type_str else None
                
                modules = await self.client.get_modules(
                    type=type_enum,
                    search=kwargs.get("search"),
                    limit=kwargs.get("limit", 10),
                    page=kwargs.get("page", 1)
                )
                
                return {
                    "status": "success",
                    "modules": [module.dict() for module in modules]
                }
                
            elif action == "get":
                module_id = kwargs.get("module_id")
                if not module_id:
                    return {
                        "status": "error",
                        "error": "module_id is required for get action"
                    }
                
                module = await self.client.get_module(module_id)
                return {
                    "status": "success",
                    "module": module.dict()
                }
                
            elif action == "execute":
                module_id = kwargs.get("module_id")
                input_data = kwargs.get("input_data", {})
                
                if not module_id:
                    return {
                        "status": "error",
                        "error": "module_id is required for execute action"
                    }
                
                result = await self.client.execute_module(
                    module_id=module_id,
                    input_data=input_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
                
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            logger.error(f"Error executing ModuleMCPTool: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class WorkflowMCPTool(BaseTool):
    """MCP tool for working with complete HMS-SVC workflows.
    
    This tool allows agents to create and execute complete workflows
    consisting of programs, protocols, and steps.
    """
    
    name = "hms_svc_workflow"
    description = """
    Use this tool to work with complete HMS-SVC workflows.
    You can create and execute end-to-end workflows that combine
    programs, protocols, and their steps.
    
    Workflows represent complete processes that civilians need to follow,
    such as applying for benefits, registering for services, or complying
    with regulations.
    """
    
    client: HMSSVCClient = Field(default=None, exclude=True)
    workflow: ProgramWorkflow = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        **kwargs
    ):
        """Initialize the WorkflowMCPTool.
        
        Args:
            base_url: Base URL for the HMS-SVC API
            api_token: API token for authentication
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)
        self.client = HMSSVCClient(base_url, api_token)
        self.workflow = ProgramWorkflow(self.client)
    
    async def _run(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute an action on HMS-SVC workflows.
        
        Args:
            action: The action to perform (create, execute_step, get_status)
            **kwargs: Parameters for the action
            
        Returns:
            Results of the action
        """
        try:
            if action == "create":
                name = kwargs.get("name")
                description = kwargs.get("description", "")
                protocols = kwargs.get("protocols", [])
                
                if not name:
                    return {
                        "status": "error",
                        "error": "name is required for create action"
                    }
                
                program = await self.workflow.create_workflow(
                    name=name,
                    description=description,
                    protocols=protocols
                )
                
                return {
                    "status": "success",
                    "program": program.dict()
                }
                
            elif action == "execute_step":
                protocol_id = kwargs.get("protocol_id")
                step_id = kwargs.get("step_id")
                input_data = kwargs.get("input_data", {})
                
                if not protocol_id:
                    return {
                        "status": "error",
                        "error": "protocol_id is required for execute_step action"
                    }
                
                if not step_id:
                    return {
                        "status": "error",
                        "error": "step_id is required for execute_step action"
                    }
                
                result = await self.workflow.execute_workflow_step(
                    protocol_id=protocol_id,
                    step_id=step_id,
                    input_data=input_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
                
            elif action == "get_status":
                program_id = kwargs.get("program_id")
                
                if not program_id:
                    return {
                        "status": "error",
                        "error": "program_id is required for get_status action"
                    }
                
                status = await self.workflow.get_workflow_status(program_id)
                
                return {
                    "status": "success",
                    "workflow_status": status
                }
                
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            logger.error(f"Error executing WorkflowMCPTool: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class SpecificModuleMCPTool(BaseTool):
    """Base class for specific HMS-SVC module type tools.
    
    This class serves as a base for tools that wrap specific
    module types like Assessment, KPI, Nudge, etc.
    """
    
    module_type: ModuleType = None
    client: HMSSVCClient = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        **kwargs
    ):
        """Initialize the specific module tool.
        
        Args:
            base_url: Base URL for the HMS-SVC API
            api_token: API token for authentication
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)
        self.client = HMSSVCClient(base_url, api_token)
    
    async def _run(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute an action on a specific HMS-SVC module type.
        
        Args:
            action: The action to perform (list, get, execute)
            **kwargs: Parameters for the action
            
        Returns:
            Results of the action
        """
        try:
            if action == "list":
                modules = await self.client.get_modules(
                    type=self.module_type,
                    search=kwargs.get("search"),
                    limit=kwargs.get("limit", 10),
                    page=kwargs.get("page", 1)
                )
                
                return {
                    "status": "success",
                    "modules": [module.dict() for module in modules]
                }
                
            elif action == "get":
                module_id = kwargs.get("module_id")
                if not module_id:
                    return {
                        "status": "error",
                        "error": "module_id is required for get action"
                    }
                
                module = await self.client.get_module(module_id)
                
                # Verify module type
                if module.type != self.module_type:
                    return {
                        "status": "error",
                        "error": f"Module is not of type {self.module_type}"
                    }
                
                return {
                    "status": "success",
                    "module": module.dict()
                }
                
            elif action == "execute":
                module_id = kwargs.get("module_id")
                input_data = kwargs.get("input_data", {})
                
                if not module_id:
                    return {
                        "status": "error",
                        "error": "module_id is required for execute action"
                    }
                
                # Get the module to verify its type
                module = await self.client.get_module(module_id)
                if module.type != self.module_type:
                    return {
                        "status": "error",
                        "error": f"Module is not of type {self.module_type}"
                    }
                
                result = await self.client.execute_module(
                    module_id=module_id,
                    input_data=input_data
                )
                
                return {
                    "status": "success",
                    "result": result
                }
                
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            logger.error(f"Error executing {self.__class__.__name__}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class AssessmentModuleTool(SpecificModuleMCPTool):
    """Tool for working with HMS-SVC Assessment modules."""
    
    name = "hms_svc_assessment"
    description = """
    Use this tool to work with HMS-SVC Assessment modules.
    Assessments collect and evaluate information from users,
    such as eligibility criteria, needs assessments, or feedback.
    """
    
    module_type = ModuleType.ASSESSMENT


class KPIModuleTool(SpecificModuleMCPTool):
    """Tool for working with HMS-SVC KPI modules."""
    
    name = "hms_svc_kpi"
    description = """
    Use this tool to work with HMS-SVC KPI modules.
    KPIs track key performance indicators and metrics
    for programs, such as completion rates, satisfaction scores,
    or time-to-completion.
    """
    
    module_type = ModuleType.KPI


class NudgeModuleTool(SpecificModuleMCPTool):
    """Tool for working with HMS-SVC Nudge modules."""
    
    name = "hms_svc_nudge"
    description = """
    Use this tool to work with HMS-SVC Nudge modules.
    Nudges send notifications, reminders, and prompts to users
    to encourage completion of tasks, provide updates, or request
    additional information.
    """
    
    module_type = ModuleType.NUDGE


def register_hms_svc_tools(registry: Any, base_url: str, api_token: Optional[str] = None) -> List[BaseTool]:
    """Register all HMS-SVC tools in the given registry.
    
    Args:
        registry: The registry to register tools in
        base_url: Base URL for the HMS-SVC API
        api_token: API token for authentication
        
    Returns:
        List of registered tools
    """
    tools = [
        ProgramMCPTool(base_url=base_url, api_token=api_token),
        ProtocolMCPTool(base_url=base_url, api_token=api_token),
        ModuleMCPTool(base_url=base_url, api_token=api_token),
        WorkflowMCPTool(base_url=base_url, api_token=api_token),
        AssessmentModuleTool(base_url=base_url, api_token=api_token),
        KPIModuleTool(base_url=base_url, api_token=api_token),
        NudgeModuleTool(base_url=base_url, api_token=api_token),
    ]
    
    for tool in tools:
        registry.register_tool(tool)
    
    return tools