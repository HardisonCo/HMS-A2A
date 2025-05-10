# HMS-A2A Integration with HMS-SVC

This module provides integration between HMS-A2A (Agent-to-Agent framework) and HMS-SVC (Program Management API), allowing HMS-A2A agents to work with structured government and NGO program workflows.

## Integration Benefits

### A2A + SVC = Powerful Civilian Assistance

This integration creates a comprehensive platform that combines:

1. **AI-Powered Assistance** (A2A) - Intelligent, conversational agents with specialized knowledge
2. **Structured Workflows** (SVC) - Compliant, step-by-step processes for government services
3. **End-to-End Journeys** - Complete civilian guidance from initial inquiry to final outcome

## Overview

The HMS-SVC integration allows HMS-A2A agents to:

1. Create and manage Programs (structured series of government/NGO engagements)
2. Define and execute Protocols (step-by-step workflows within programs)
3. Utilize specialized Modules (Assessment, KPI, Nudge, etc.) as tools
4. Monitor and orchestrate end-to-end civilian workflows

This integration bridges the flexible, AI-driven capabilities of HMS-A2A with the structured, compliance-focused workflows of HMS-SVC.

## Architecture

The integration consists of:

1. **HMS-SVC Client** - Direct API client for the HMS-SVC system
2. **HMS-SVC MCP Tools** - MCP-compatible tools exposing HMS-SVC functionality to A2A agents
3. **Program Workflow Helpers** - Utilities for creating and managing complete workflows

## Key Components

### HMS-SVC Client

The `HMSSVCClient` provides direct API access to HMS-SVC:

```python
from src.server import HMSSVCClient

# Create a client
client = HMSSVCClient(
    base_url="https://api.hms-svc.example.com",
    api_token="your_api_token"
)

# Create a program
program = await client.create_program(
    name="Benefit Application Process",
    description="Application workflow for citizen benefits"
)

# Create a protocol within the program
protocol = await client.create_protocol(
    program_id=program.id,
    name="Eligibility Verification",
    description="Steps to verify eligibility for benefits",
    steps=[
        {"type": "assessment", "module_id": "eligibility_assessment"},
        {"type": "document", "module_id": "document_upload"},
        {"type": "checkpoint", "module_id": "verification_checkpoint"}
    ]
)
```

### MCP Tools

The MCP tools expose HMS-SVC functionality to A2A agents:

```python
from src.server import register_hms_svc_tools
from src.core.framework.a2a_tools import ToolRegistry

# Create and register tools
registry = ToolRegistry()
tools = register_hms_svc_tools(
    registry=registry,
    base_url="https://api.hms-svc.example.com",
    api_token="your_api_token"
)

# Tools are now available for agents to use
```

Available MCP tools:
- `hms_svc_program` - Work with Programs
- `hms_svc_protocol` - Work with Protocols
- `hms_svc_module` - Work with Modules (general)
- `hms_svc_workflow` - Work with complete workflows
- `hms_svc_assessment` - Work specifically with Assessment modules
- `hms_svc_kpi` - Work specifically with KPI modules
- `hms_svc_nudge` - Work specifically with Nudge modules

### Program Workflow Helper

The `ProgramWorkflow` helper simplifies working with complete workflows:

```python
from src.server import HMSSVCClient, ProgramWorkflow

# Create client and workflow helper
client = HMSSVCClient(base_url="https://api.hms-svc.example.com")
workflow = ProgramWorkflow(client)

# Create a complete workflow
program = await workflow.create_workflow(
    name="Loan Application Process",
    description="Process for applying for a government loan",
    protocols=[
        {
            "name": "Initial Application",
            "description": "Submit initial application details",
            "steps": [
                {"type": "form", "module_id": "personal_details_form"},
                {"type": "document", "module_id": "income_verification"}
            ]
        },
        {
            "name": "Review Process",
            "description": "Review and approval steps",
            "steps": [
                {"type": "assessment", "module_id": "eligibility_check"},
                {"type": "checkpoint", "module_id": "approval_checkpoint"}
            ]
        }
    ]
)

# Check workflow status
status = await workflow.get_workflow_status(program.id)
```

## Use Cases

1. **Automated Civilian Assistance** - Agents help civilians navigate complex government programs and requirements
2. **Program Compliance Monitoring** - Track and ensure compliance with program requirements using KPI modules
3. **Document Collection and Verification** - Automate document collection using Assessment modules
4. **Personalized Guidance** - Provide tailored assistance through each step of a government process
5. **Progress Tracking** - Monitor a civilian's progress through a program workflow

## Benefits of Integration

1. **Structured Compliance** - HMS-SVC provides rigorous, compliance-focused workflow structures
2. **AI-Powered Assistance** - HMS-A2A provides flexible, intelligent agent capabilities
3. **End-to-End Workflows** - Complete citizen journeys from initial inquiry to final outcome
4. **Personalized Support** - Agents can provide context-aware assistance at each step
5. **Standardized Processes** - Consistent handling of government processes while allowing for personalization

## Example: Complete Integration Workflow

```python
# 1. Import necessary components
from src.server import (
    register_hms_svc_tools,
    HMSSVCClient,
    ProgramWorkflow
)
from src.core.framework.a2a_tools import ToolRegistry
from src.core.framework.react_agent import create_agent

# 2. Set up HMS-SVC integration
client = HMSSVCClient(
    base_url="https://api.hms-svc.example.com",
    api_token="your_api_token"
)

# 3. Register HMS-SVC tools with the agent's tool registry
registry = ToolRegistry()
hms_svc_tools = register_hms_svc_tools(registry, client.base_url, client.api_token)

# 4. Create an agent with access to HMS-SVC tools
agent = create_agent(
    "government_program_assistant",
    registry=registry,
    system_message="""You are a Government Program Assistant that helps 
    civilians navigate government programs and services."""
)

# 5. The agent can now use HMS-SVC tools to:
#    - Create programs and protocols
#    - Execute assessment modules 
#    - Track KPIs
#    - Send notifications
#    - Manage end-to-end workflows
```