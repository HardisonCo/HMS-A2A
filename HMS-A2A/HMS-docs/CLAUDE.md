# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Install Python dependencies: `uv pip install .`
- Install TypeScript dependencies: `npm install`
- Build TypeScript: `npm run build`
- Run Python server: `uv run -m finala2e`
- Run TypeScript server: `npm start`
- Run single test (Python): `pytest path/to/test_file.py::test_function_name`
- Linting: 
  - Python: `ruff check .`
  - TypeScript: `npm run lint` (if added)

## Integration Plan: MCP-A2A with A2A-MCP

### Overview
Integrate the TypeScript MCP-A2A client with the Python A2A-MCP framework to enable unified access to both functionalities through a single application.

### Implementation Strategy
1. Create a Python wrapper for the TypeScript MCP-A2A client
2. Add the MCP-A2A agent as a tool to the A2A-MCP LangGraph agent
3. Enable bidirectional communication between components

### Specific Tasks
1. Add TypeScript dependencies to the A2A-MCP project
2. Create a Python interface to interact with the MCP-A2A client
3. Register the MCP-A2A client as a tool in the LangGraph agent
4. Update the server initialization to launch both components
5. Extend existing API endpoints to support the integrated functionality
6. Update documentation to reflect the unified capabilities

### Code Style
- Python: Use type hints, 4-space indentation, docstrings for public functions
- TypeScript: Follow standard TypeScript practices, 2-space indentation
- Error handling: Use appropriate try/except or try/catch with meaningful messages
- API naming: Maintain consistent naming conventions across languages