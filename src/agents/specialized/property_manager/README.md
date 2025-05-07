# Property Manager Specialized Agent

This directory contains specialized tools and resources for the Property Manager domain. These tools are MCP-compliant and designed to be used by specialized agents working in this field.

## Domain Overview

The Property Manager domain encompasses professionals who provide specialized services in property manager. This includes knowledge areas such as:

- Key knowledge area 1
- Key knowledge area 2
- Key knowledge area 3

## Tools

The following specialized tools are available for Property Manager agents:

### example_property_manager_tool

This tool provides basic functionality for Property Manager agents. It allows for:

- Example capability 1
- Example capability 2

## Standards

This agent adheres to the following standards:

- DomainStandards: General standards for all specialized agents
- PropertyManagerStandards: Industry-specific standards for Property Manager

## Integration

To use these tools in your agent implementation:

```python
from src.agents.specialized.property_manager.tools import register_property_manager_tools

# Register all property_manager tools
tool_names = register_property_manager_tools()
```

## Development

When extending these tools, please ensure:

1. All tools are MCP-compliant
2. Tools are properly registered with the MCP registry
3. Tools validate against relevant standards
4. Comprehensive documentation is provided
5. Test cases are added to the test suite
