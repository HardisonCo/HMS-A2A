"""
Integration Module

This module provides integration capabilities for HMS-A2A with external systems.
"""

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

from .hms_svc_mcp_tools import (
    ProgramMCPTool,
    ProtocolMCPTool,
    ModuleMCPTool,
    WorkflowMCPTool,
    AssessmentModuleTool,
    KPIModuleTool,
    NudgeModuleTool,
    register_hms_svc_tools
)

__all__ = [
    'HMSSVCClient',
    'ProgramWorkflow',
    'ProgramStatus',
    'ProtocolStatus',
    'ModuleType',
    'Program',
    'Protocol',
    'Module',
    'ProgramMCPTool',
    'ProtocolMCPTool',
    'ModuleMCPTool',
    'WorkflowMCPTool',
    'AssessmentModuleTool',
    'KPIModuleTool',
    'NudgeModuleTool',
    'register_hms_svc_tools'
]