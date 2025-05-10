# Government Agent System

This module provides a framework for creating and managing AI agents that represent government agencies, enabling both government operations and civilian engagement with federal agencies.

## Overview

The Government Agent System is a specialized framework that enables the creation of AI agents representing government agencies. Each agency can have two types of agents:

1. **Government Agents** - Used for internal government operations with access to all tools and capabilities
2. **Civilian Agents** - Public-facing agents that provide services to civilians, with limited access to only public information

These agents integrate with the existing A2A (Agent-to-Agent) and MCP (Message Control Protocol) frameworks to enable seamless communication between agents and other systems.

## Key Components

- **Base Agent** - Shared functionality between government and civilian agents
- **Government Agent** - Specialized agent for internal government operations
- **Civilian Agent** - Public-facing agent for civilian interactions
- **Agency Registry** - Singleton registry for managing agent instances
- **Agent Factory** - Factory for creating and configuring agents
- **MCP Integration** - Adapters to expose agents as MCP tools

## Usage

### Creating Agents

```python
from gov_agents import AgentFactory

# Create a government agent for a specific agency
fbi_gov_agent = AgentFactory.create_government_agent("FBI")

# Create a civilian agent for the same agency
fbi_civilian_agent = AgentFactory.create_civilian_agent("FBI")

# Process tasks through the agents
gov_response = await fbi_gov_agent.process_task("Analyze internal threat assessment data")
civilian_response = await fbi_civilian_agent.process_task("How do I report suspicious activity?")
```

### Using the Registry

```python
from gov_agents import AgencyRegistry

# Get the registry (singleton)
registry = AgencyRegistry()

# Get an agent for a specific agency
cia_agent = registry.get_government_agent("CIA")

# List all available agencies
agencies = registry.list_agencies()
```

### MCP Integration

```python
from gov_agents import GovAgentMCPRegistry, register_all_agencies_as_mcp_tools

# Register all agencies as MCP tools
tools = register_all_agencies_as_mcp_tools()

# Get the MCP registry
mcp_registry = GovAgentMCPRegistry()

# List all public-facing tools
public_tools = mcp_registry.list_tools(access_level="public")

# Use a tool directly
ssa_tool = mcp_registry.get_tool("SSA_civilian_agent")
response = await ssa_tool("How do I apply for Social Security benefits?")
```

## Architecture

The Government Agent System uses a layered architecture:

1. **Base Layer** - Core abstractions and interfaces
2. **Agent Layer** - Government and civilian agent implementations
3. **Registry Layer** - Management of agent instances
4. **Integration Layer** - Adapters for MCP and other systems

Agents use the ReAct (Reasoning + Acting) pattern through LangGraph for intelligent decision-making and standard compliance validation.

## Standards Compliance

Government agents validate tasks against agency-specific standards and policies. The system supports:

- Information classification levels
- Privacy and data protection requirements
- Interagency information sharing protocols
- Civilian service standards

## Extending the System

New agency types can be added by:

1. Creating a new agent class extending BaseAgent
2. Implementing agency-specific validation and prompt engineering
3. Registering agency-specific tools and capabilities
4. Adding MCP tool integrations as needed