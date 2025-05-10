# Exercise Physiologist Specialized Agent

This directory contains specialized tools and resources for the Exercise Physiologist domain. These tools are MCP-compliant and designed to be used by specialized agents working in this field.

## Domain Overview

The Exercise Physiologist domain encompasses professionals who provide specialized services in exercise physiologist. This includes knowledge areas such as:

- Key knowledge area 1
- Key knowledge area 2
- Key knowledge area 3

## Tools

The following specialized tools are available for Exercise Physiologist agents:

### example_exercise_physiologist_tool

This tool provides basic functionality for Exercise Physiologist agents. It allows for:

- Example capability 1
- Example capability 2

## Standards

This agent adheres to the following standards:

- DomainStandards: General standards for all specialized agents
- ExercisePhysiologistStandards: Industry-specific standards for Exercise Physiologist

## Integration

To use these tools in your agent implementation:

```python
from src.agents.specialized.exercise_physiologist.tools import register_exercise_physiologist_tools

# Register all exercise_physiologist tools
tool_names = register_exercise_physiologist_tools()
```

## Development

When extending these tools, please ensure:

1. All tools are MCP-compliant
2. Tools are properly registered with the MCP registry
3. Tools validate against relevant standards
4. Comprehensive documentation is provided
5. Test cases are added to the test suite
