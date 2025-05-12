# Government Agent System

The Government Agent System provides a framework for creating AI agents that represent government agencies, enabling both government operations and civilian engagement.

## Overview

The system consists of several key components:

1. **BaseAgent** - Abstract base class providing common functionality
2. **GovernmentAgent** - Internal agent for government operations
3. **CivilianAgent** - Public-facing agent for civilian interactions
4. **AgencyRegistry** - Singleton registry for managing agents
5. **AgentFactory** - Factory for creating and configuring agents
6. **MCP Integration** - Tools to expose agents via MCP

## Agent Types

### Government Agent

The `GovernmentAgent` class provides an agent for internal government operations:

- Access to all agency tools and capabilities
- Compliance with government-specific standards
- Specialized prompt instructions for government use
- Validation for internal government tasks
- Chain of Recursive Thoughts (CoRT) enhanced reasoning

```python
from src.agents.gov import AgentFactory

# Create a government agent for the FBI
fbi_agent = AgentFactory.create_government_agent("FBI", use_cort=True)

# Process a government task with enhanced reasoning
response = await fbi_agent.process_task(
    "Analyze internal threat assessment data",
    cort_max_rounds=3,
    cort_alternatives=3,
    prompt_instructions="Consider multiple interpretations and security implications"
)
```

### Civilian Agent

The `CivilianAgent` class provides a public-facing agent for civilians:

- Limited to public-facing tools only
- Specialized prompt instructions emphasizing public service
- Validation to prevent requests for non-public information
- Protection against attempts to gain preferential treatment

```python
from src.agents.gov import AgentFactory

# Create a civilian agent for the IRS
irs_agent = AgentFactory.create_civilian_agent("IRS")

# Process a civilian query
response = await irs_agent.process_task("How do I file for a tax extension?")
```

## Agency Registry

The `AgencyRegistry` provides centralized management of agency agents:

```python
from src.agents.gov import AgencyRegistry

# Get the registry singleton
registry = AgencyRegistry()

# Get an agent for a specific agency
cia_agent = registry.get_government_agent("CIA")
ssa_agent = registry.get_civilian_agent("SSA")

# List all available agencies
agencies = registry.list_agencies()
```

## MCP Integration

The system integrates with MCP through the `mcp_integration` module:

```python
from src.agents.gov import register_all_agencies_as_mcp_tools

# Register all agency agents as MCP tools
tools = register_all_agencies_as_mcp_tools()

# Get a specific agency MCP tool
from src.agents.gov import GovAgentMCPRegistry
mcp_registry = GovAgentMCPRegistry()
fbi_tool = mcp_registry.get_tool("FBI_government_agent")
```

## Implementation Architecture

The Government Agent System follows a layered architecture:

1. **Base Layer** (`base_agent.py`) - Core abstractions and interfaces
2. **Agent Layer** (`government_agent.py`, `civilian_agent.py`) - Agent implementations
3. **Registry Layer** (`agency_registry.py`, `agent_factory.py`) - Agent management
4. **Integration Layer** (`mcp_integration.py`) - MCP integration
5. **Reasoning Layer** - Chain of Recursive Thoughts integration

### CoRT Integration

Government agents leverage Chain of Recursive Thoughts for enhanced reasoning:

```python
from src.agents.gov.government_agent import GovernmentAgent
from src.common.utils.recursive_thought import get_recursive_thought_processor

# Create a government agent
agent = GovernmentAgent("Department of Defense", "DoD")

# Enable CoRT for complex security assessments
agent.enable_cort(
    max_rounds=4,              # More rounds for security-critical tasks
    generate_alternatives=4,   # Consider multiple security scenarios
    dynamic_rounds=True        # Adapt thinking depth to complexity
)

# Process a sensitive task with chain of thought reasoning
result = await agent.process_with_cort(
    "Evaluate potential security vulnerabilities in the proposed system",
    prompt_instructions="Consider both offensive and defensive perspectives"
)

# Access the complete thinking trace for audit
thinking_trace = result["thinking_trace"]
```

## Standards Compliance

All agents validate tasks against appropriate standards:

- GovernmentAgent validates against internal government standards
- CivilianAgent validates against public service standards
- Both enforce compliance with agency-specific regulations

## Data Loading

Agency data is loaded from the `data/fed.json` file, which contains information about federal agencies:

- Agency names and labels
- Agency missions and descriptions
- Supported standards and regulations
- Available MCP tools

## Example Use Case: Loan Application

A complete loan application process might involve:

1. **SBA CivilianAgent** - Provides information about loan programs
2. **HMS-SVC Integration** - Manages the application workflow
3. **SBA GovernmentAgent** - Handles internal loan review

This combination provides end-to-end assistance from initial inquiry to final approval.