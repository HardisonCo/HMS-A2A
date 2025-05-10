# Speech Therapist Specialized Agent

This directory contains specialized tools and resources for the Speech Therapist domain. These tools are MCP-compliant and designed to be used by specialized agents working in this field.

## Domain Overview

The Speech Therapist domain encompasses professionals who provide specialized services in speech therapist. This includes knowledge areas such as:

- Key knowledge area 1
- Key knowledge area 2
- Key knowledge area 3

## Tools

The following specialized tools are available for Speech Therapist agents:

### example_speech_therapist_tool

This tool provides basic functionality for Speech Therapist agents. It allows for:

- Example capability 1
- Example capability 2

## Standards

This agent adheres to the following standards:

- DomainStandards: General standards for all specialized agents
- SpeechTherapistStandards: Industry-specific standards for Speech Therapist

## Integration

To use these tools in your agent implementation:

```python
from src.agents.specialized.speech_therapist.tools import register_speech_therapist_tools

# Register all speech_therapist tools
tool_names = register_speech_therapist_tools()
```

## Development

When extending these tools, please ensure:

1. All tools are MCP-compliant
2. Tools are properly registered with the MCP registry
3. Tools validate against relevant standards
4. Comprehensive documentation is provided
5. Test cases are added to the test suite
