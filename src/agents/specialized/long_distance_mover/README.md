# Long Distance Mover Specialized Agent

This directory contains specialized tools and resources for the Long Distance Mover domain. These tools are MCP-compliant and designed to be used by specialized agents working in this field.

## Domain Overview

The Long Distance Mover domain encompasses professionals who provide specialized services in long distance mover. This includes knowledge areas such as:

- Key knowledge area 1
- Key knowledge area 2
- Key knowledge area 3

## Tools

The following specialized tools are available for Long Distance Mover agents:

### example_long_distance_mover_tool

This tool provides basic functionality for Long Distance Mover agents. It allows for:

- Example capability 1
- Example capability 2

## Standards

This agent adheres to the following standards:

- DomainStandards: General standards for all specialized agents
- LongDistanceMoverStandards: Industry-specific standards for Long Distance Mover

## Integration

To use these tools in your agent implementation:

```python
from src.agents.specialized.long_distance_mover.tools import register_long_distance_mover_tools

# Register all long_distance_mover tools
tool_names = register_long_distance_mover_tools()
```

## Development

When extending these tools, please ensure:

1. All tools are MCP-compliant
2. Tools are properly registered with the MCP registry
3. Tools validate against relevant standards
4. Comprehensive documentation is provided
5. Test cases are added to the test suite
