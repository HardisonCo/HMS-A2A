# 🤖 Agent-to-Everything (A2E) with LangGraph and MCP 🤖

[![Language: Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project demonstrates an Agent-to-Everything (A2E) implementation that combines multiple capabilities through the A2A protocol. It showcases how specialized agents can be used as tools by a central orchestrating agent using [LangGraph](https://langchain-ai.github.io/langgraph/) and the [Model Context Protocol (MCP)](https://github.com/google/model-context-protocol).

## 🆕 Newest Features

### Chain of Recursive Thoughts (CoRT)

The framework now includes Chain of Recursive Thoughts (CoRT) capabilities for enhanced agent reasoning:

- **Recursive Self-Critique** - Agents can evaluate their own responses through multiple rounds
- **Alternative Generation** - Produces multiple potential responses for comparison
- **Dynamic Thinking Depth** - Automatically determines the optimal number of thinking rounds
- **Thinking Trace** - Provides transparent reasoning process for all decisions
- **Tool-Aware Reasoning** - CoRT-enhanced reasoning that's aware of available tools

This implementation enables all agents in the HMS-A2A framework to engage in deeper, more nuanced thinking when tackling complex problems.

#### Using CoRT

To enable CoRT for all agents in the system:

```bash
# Enable CoRT with unified start command
./start.sh --cort

# Run the complete test suite and start with CoRT enabled
./start_cort_demo.sh

# Run the basic demo
./examples/cort_basic_demo.py
```

To use CoRT in specific contexts:

```python
# Using CoRT with the React Agent
from graph.cort_react_agent import CoRTReactAgent

agent = CoRTReactAgent(
    use_cort=True,
    max_rounds=3,
    generate_alternatives=3
)

# Using the CoRT Deal Negotiator for enhanced deal evaluation
from specialized_agents.collaboration.cort_deal_negotiator import CoRTDealEvaluator

deal_evaluator = CoRTDealEvaluator(llm=llm)
evaluation = await deal_evaluator.evaluate_deal(
    deal_proposal, 
    context,
    prompt_instructions="Focus on sustainability and long-term value"  # Domain-specific guidance
)

# The evaluation includes explicit approval status
approval_status = evaluation.get("approval_status")  # "approved", "rejected", or "conditional"

# Access the complete thinking trace
thinking_rounds = evaluation.get("thinking_trace", [])
```

#### CoRT Technical Capabilities

The Chain of Recursive Thoughts implementation provides several advanced capabilities:

- **Dynamic Thinking Depth**: Automatically adjusts the number of thinking rounds based on problem complexity
- **Multi-Alternative Generation**: Creates and evaluates multiple solution approaches
- **Self-Critique**: Recursively improves responses through systematic evaluation
- **Domain-Specific Instructions**: Uses tailored guidance for specialized scenarios
- **Tool Integration**: Seamlessly works with agent tools for more informed decisions
- **Prompt Instructions**: Supports specific instructions for guiding the reasoning process
- **Comprehensive Testing**: Includes detailed specification tests for all functionality
- **Unified Start Command**: Simple way to enable CoRT across all system components

For more detailed information, see the [recursive thought documentation](docs/recursive_thought.md) and [CoRT deal negotiation documentation](docs/cort_deal_negotiation.md).

### Government Agent System

The framework includes a specialized Government Agent System for creating AI agents that represent government agencies:

- **Government Agents** - Internal government operations with access to all agency tools
- **Civilian Agents** - Public-facing agents for civilian interactions with agencies
- **Agency Registry** - Central registry for managing all agency agents
- **Standards Compliance** - Validation against government standards and regulations

### HMS-SVC Integration

The A2A framework integrates with HMS-SVC to provide structured program and protocol management:

- **Program Management** - Create and manage government program workflows
- **Protocol Execution** - Step-by-step protocol execution with compliance validation
- **Specialized Modules** - Assessment, KPI, and notification modules as MCP tools
- **End-to-End Workflows** - Complete civilian journey management

## System Architecture

HMS-A2A functions as the core AI/ML Agent layer in the CodifyHQ platform:

```
                     ┌───────────────┐
                     │    HMS-SYS    │
                     │(Infrastructure)│
                     └───────┬───────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
    ┌───────▼──────┐                 ┌────────▼────────┐
    │    HMS-SVC   │◄───────────────►│     HMS-A2A     │
    │(Core Backend)│                 │  (AI/ML Agents)  │
    └───────┬──────┘                 └────────┬─────────┘
            │                                 │
            │                       ┌─────────┴─────────┐
            │                       │                   │
            │              ┌────────▼────────┐  ┌───────▼───────┐
            │              │ Specialized     │  │  Government   │
            │              │   Agents        │  │    Agents     │
            │              └────────┬────────┘  └───────┬───────┘
            │                       │                   │
    ┌───────▼───────┐      ┌────────▼────────┐  ┌───────▼───────┐
    │   HMS-DTA/NFO │◄─────┤  A2A Protocol   │  │  MCP Protocol │
    │ (Data & ETL)  │      │  Integration    │  │  Integration  │
    └───────────────┘      └─────────────────┘  └───────────────┘
```

The HMS-A2A component provides AI agent capabilities through:

1. **Core Integration** with HMS-SVC for accessing backend services
2. **Specialized Agents** for domain-specific expertise (agriculture, telemedicine, etc.)
3. **Government Agents** representing government agencies and services
4. **Data Pipeline** connection with HMS-DTA/NFO for data transformation
5. **Protocol Support** for A2A and MCP to enable agent communication

This architecture enables A2A to function as a specialized AI layer that can be accessed by other components in the system while maintaining its own internal agent ecosystem.

## A2A Component Architecture

![A2A Architecture Diagram](docs/diagram.png)

## Project Structure

The repository is organized into the following components:

- `finala2e/`: The main A2E implementation combining math, currency, and generic A2A capabilities
- `graph/`: Core LangGraph agent implementation with A2A tool integration
- `test_mcp/`: MCP server implementations and testing clients
- `common/`: Shared components, including A2A client and server implementations
- `specialized_agents/`: Standards-compliant specialized agents for various industry domains
- `gov_agents/`: Government agency agents with internal and civilian-facing capabilities
- `integration/`: Integration with external systems like HMS-SVC
- `examples/`: Example implementations demonstrating key features

## Features

- **Chain of Recursive Thoughts (CoRT)**: Enhanced agent reasoning with multi-round thinking
- **Math Operations**: Perform basic mathematical calculations
- **Currency Conversions**: Get exchange rates and convert between currencies
- **Generic A2A Integration**: Connect to any A2A-compatible agent
- **Specialized Industry Agents**: Standards-compliant agents for specific domains
  - Agriculture: Provides guidance following USDA and other agricultural standards
  - Telemedicine: Provides guidance following HIPAA, ATA guidelines, and telehealth regulations
  - Nutrition: Provides guidance following evidence-based nutrition guidelines and dietetic practice standards
  - Government: Specialized agents representing federal agencies and departments
  - More domains can be added using the modular framework (200+ planned)
- **Government Program Management**: Create and manage structured government program workflows
  - Programs: Top-level entities representing complete service offerings
  - Protocols: Step-by-step workflows within programs
  - Modules: Specialized components for assessment, tracking, and notifications
- **Standards Compliance Framework**: Common validation patterns for enforcing regulations and standards
- **Human-in-the-Loop (HITL) Review**: Flags high-risk operations for human review
- **Standards Compliance**: Validates responses against industry standards and regulations
- **Streaming Support**: Provides incremental updates during processing
- **Checkpoint Memory**: Maintains conversation state between turns
- **Push Notification System**: Webhook-based updates with JWK authentication

## Documentation

For more detailed information, see the documentation in the `docs` directory:

- [`agent.md`](docs/agent.md): Details about the agent architecture
- [`mcp_langchain.md`](docs/mcp_langchain.md): Using MCP with LangChain
- [`integration.md`](docs/integration.md): HMS-SVC integration details
- [`government_agents.md`](docs/government_agents.md): Government agents system
- [`recursive_thought.md`](docs/recursive_thought.md): Chain of Recursive Thoughts implementation
- [`cort_deal_negotiation.md`](docs/cort_deal_negotiation.md): CoRT for deal evaluation and negotiation
- [`migration.md`](docs/migration.md): Migration guidance

## Prerequisites

- Python 3.10 or higher
- Google API Key for Gemini model
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (optional, for containerized deployment)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/a2a-langgraph.git
   cd a2a-langgraph
   ```

2. Create an environment file with your API key:

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. Install dependencies with uv:

   ```bash
   uv pip install .
   ```

4. (Optional) Configure external A2A endpoints:

   ```bash
   # Set a single endpoint
   export A2A_ENDPOINT_URL=http://localhost:41241
   
   # Or set multiple endpoints (comma-separated)
   export A2A_ENDPOINT_URLS=http://localhost:41241,http://localhost:41242
   ```

### Unified Start Command

The project includes a unified start command that simplifies launching all services with a single command:

```bash
# Start all services with default settings
./start.sh

# Start all services with CoRT enabled
./start.sh --cort

# Run tests before starting services
./start.sh --test

# Start a specific service
./start.sh --service a2a  # Options: all, a2a, graph, gov

# Specify host and port
./start.sh --host 0.0.0.0 --port 8000
```

## Running the A2E Agent

You can now use the unified start command to launch all services, or continue using the individual commands below.

### Option 1: Use the Unified Start Command (Recommended)

The easiest way to start all required services:

```bash
# Start all services with default settings
./start.sh

# Enable Chain of Recursive Thoughts for enhanced reasoning
./start.sh --cort

# Run tests before starting services
./start.sh --test
```

### Option 2: Start Individual Servers Manually

If you prefer to start servers individually:

#### Start the Required Servers

First, start the component A2A servers:

```bash
# Start the Currency, Math, and A2A MCP servers (keep running in a separate terminal)
uv run -m finala2e.start_servers
```

This starts:
- Currency Agent server on port 10000
- Math Agent server on port 10001
- A2A MCP server for connecting to external A2A agents

#### Run the A2E Server

In a separate terminal, run the A2E agent as an A2A-compatible server:

```bash
uv run -m finala2e
```

By default, the server runs on localhost:10003. You can specify a different host and port:

```bash
uv run -m finala2e --host 0.0.0.0 --port 8000
```

### Testing with the Graph Agent CLI

You can test the integrated agent with the Graph Agent CLI:

```bash
# Run the graph agent in chat mode
uv run -m graph.cli --chat

# Run tests for all agent capabilities
uv run -m graph.cli --test
```

### Direct Testing with the Client

You can test the agent directly using the client:

```bash
# Run a single query
uv run -m finala2e.client_stdio --query "What is 5 + 7?"

# Start an interactive chat session
uv run -m finala2e.client_stdio --chat
```

### Test the Integrated Functionality

To verify that all components are working correctly together:

```bash
# Run the integrated test suite
uv run test_integrated_agent.py
```

## Using Specialized Agents

The project includes standards-compliant specialized agents for various industry domains. Currently, the following domains are supported:

### Agriculture Agent

The Agriculture Agent provides guidance following USDA regulations, organic certification requirements, sustainable farming practices, and other agricultural standards.

To use the Agriculture Agent through the A2E interface:

```
Agriculture: What are the best organic pest management practices for tomatoes?
```

#### Agriculture Agent Tools

The Agriculture Agent provides the following tools:

1. **Soil Analysis Tool**: Analyzes soil samples and provides recommendations
2. **Crop Management Tool**: Provides crop-specific management guidance
3. **Pesticide Application Tool**: Offers guidance on safe and compliant pesticide use

### Telemedicine Agent

The Telemedicine Agent provides guidance following HIPAA regulations, American Telemedicine Association (ATA) guidelines, ISO 13131 standards, and other telehealth requirements.

To use the Telemedicine Agent through the A2E interface:

```
Telemedicine: What are the HIPAA requirements for telehealth platforms?
```

#### Telemedicine Agent Tools

The Telemedicine Agent provides the following tools:

1. **Telehealth Platform Evaluation Tool**: Evaluates and recommends telehealth platforms based on organizational needs, clinical use cases, and regulatory requirements
2. **Telehealth Workflow Design Tool**: Creates telehealth clinical and operational workflows tailored to specific practice settings
3. **Telehealth Regulatory Compliance Tool**: Analyzes telehealth programs for compliance across multiple jurisdictions

Each tool enforces compliance with relevant standards and regulations.

### Nutrition Agent

The Nutrition Agent provides guidance following evidence-based nutrition guidelines, Nutrition Care Process standards, Medical Nutrition Therapy protocols, and other dietetic practice standards.

To use the Nutrition Agent through the A2E interface:

```
Nutrition: What are the best approaches for nutritional assessment of elderly patients?
```

#### Nutrition Agent Tools

The Nutrition Agent provides the following tools:

1. **Nutritional Assessment Tool**: Evaluates nutritional status and provides evidence-based recommendations
2. **Meal Plan Generator Tool**: Creates personalized meal plans based on health conditions, preferences, and requirements
3. **Dietary Analysis Tool**: Analyzes food intake patterns and provides nutritional insights

Each tool enforces compliance with relevant standards and regulations.

## MCP Integration

The `test_mcp` directory provides examples of integrating A2A agents with MCP.

### Start MCP Servers

```bash
uv run test_mcp/start_sse_servers.py
```

### Using STDIO Transport Client

```bash
# Run with a specific query
uv run test_mcp/client/client_stdio.py --query "What is 5 + 7?"

# Run in interactive chat mode
uv run test_mcp/client/client_stdio.py --chat
```

### Using SSE Transport Client

```bash
# Run with a specific query
uv run test_mcp/client/client_sse.py --query "What is 5 + 7?"

# Run in interactive chat mode
uv run test_mcp/client/client_sse.py --chat
```

## Technical Implementation

- **LangGraph ReAct Agent**: Uses the ReAct pattern for reasoning and tool usage
- **Chain of Recursive Thoughts (CoRT)**: Enhances agent reasoning through recursive self-critique
- **MCP Integration**: Connects to A2A agents via Model Context Protocol
- **A2A Tools**: Specialized tools for math, currency, and domain-specific operations
- **Standards-Compliant Agents**: Domain-specific agents that enforce industry standards
- **Agent Collaboration Framework**: Enables cross-domain collaboration between specialized agents
- **Human-in-the-Loop (HITL)**: Provides human review for critical operations
- **A2A Client in Python**: Connects to external A2A agents via JSON-RPC
- **Streaming Support**: Provides incremental updates during processing
- **Checkpoint Memory**: Maintains conversation state between turns
- **Push Notification System**: Webhook-based updates with JWK authentication
- **Unified Start System**: Simple command to launch all services with configurable options

## Standards-Compliant Agent Collaboration

The A2E framework includes a powerful collaboration system that enables standards-compliant agents from different domains to work together on complex tasks.

### Key Collaboration Features

- **Cross-Domain Tool Sharing**: Tools can be shared across multiple specialized agents
- **Standards Validation**: All tool inputs and outputs are validated against domain-specific standards
- **Human-in-the-Loop (HITL)**: Critical decisions can be reviewed by humans
- **Shared Context**: Agents maintain a shared context for collaboration
- **Collaboration Sessions**: Sessions manage interactions between multiple agents

### Collaboration Architecture

The collaboration framework is built around these key components:

1. **MCPToolRegistry**: Central registry for MCP-compliant tools
2. **CollaborationSession**: Manages collaboration between multiple agents
3. **HITLManager**: Handles human-in-the-loop review requests
4. **StandardsCompliantMCPTool**: Base class for all MCP tools

### Example: Agriculture + Nutrition Collaboration

The framework enables powerful cross-domain collaborations, such as between Agriculture and Nutrition agents:

```python
# Start a collaboration session
session_id = await agriculture_agent.start_collaboration(["agriculture", "nutrition"])

# Agriculture agent analyzes soil and crop management
crop_result = await agriculture_agent.collaborate(
    session_id, 
    "crop_management", 
    {"cropType": "spinach", "farmingSystem": "organic", ...}
)

# Nutrition agent analyzes the nutritional value
nutrition_result = await nutrition_agent.collaborate(
    session_id, 
    "nutritional_assessment", 
    {"foodItem": "spinach", "productionMethod": "organic", ...}
)

# Nutrition agent generates a meal plan using the crop
meal_plan_result = await nutrition_agent.collaborate(
    session_id, 
    "meal_plan_generator", 
    {"primaryIngredients": ["spinach"], ...}
)
```

This collaboration allows multiple specialized agents to contribute their domain expertise to solve complex problems that span multiple domains, all while maintaining standards compliance.

### Running the Collaboration Example

To try out the agent collaboration capabilities:

```bash
# Run the Agriculture + Nutrition collaboration example
uv run -m specialized_agents.collaboration.examples.agriculture_nutrition_collaboration
```

This example demonstrates:
1. Starting a collaboration session between the Agriculture and Nutrition agents
2. Agriculture agent providing crop management recommendations
3. Nutrition agent analyzing the nutritional content of the crop
4. Nutrition agent generating meal plans using the crop
5. Agriculture agent optimizing soil conditions for maximum nutritional value
6. All tool executions being validated against domain-specific standards
7. Human-in-the-loop review for critical decisions

## Example Queries

### Basic Operations
- "What is 7 + 12?"
- "Multiply 8 and 15"
- "What is the exchange rate between USD and EUR?"
- "Convert 100 USD to JPY"
- "Add 23 and 45, then convert the result from USD to GBP"

### Development Assistance
- "Create a Python function to find the longest substring without repeating characters"
- "Explain how to implement authentication with JWT"

### Specialized Domains
- "Agriculture: What are the best organic pest management practices for tomatoes?"
- "Agriculture: How should I apply fertilizer to my apple orchard while following USDA guidelines?"
- "Agriculture: What are the proper safety protocols for pesticide application near water?"
- "Telemedicine: What are the requirements for HIPAA-compliant telehealth platforms?"
- "Telemedicine: How should I design workflows for a new telehealth program in my clinic?"
- "Telemedicine: What are the licensing requirements for providing telehealth across state lines?"
- "Nutrition: What are the best approaches for nutritional assessment of elderly patients?"
- "Nutrition: Can you create a meal plan for someone with type 2 diabetes?"
- "Nutrition: What nutrition interventions are effective for patients with chronic kidney disease?"

### Government Agencies
- "FBI: What is the process for reporting internet fraud?"
- "SBA: How do I apply for a small business loan?"
- "IRS: What tax forms do I need for a small business?"
- "USDA: What organic certification requirements apply to my farm?"

### Program Workflows
- "Create a small business loan application program"
- "Execute the eligibility assessment for my loan application"
- "What documents do I need to complete the next step in my benefits application?"
- "Send a reminder notification to applicants who haven't completed their forms"

## Implementing Standards-Compliant Agents and Tools

This project follows a consistent pattern for implementing standards-compliant agents and their associated tools. Below is a detailed guide on how to implement new agents and tools following this pattern.

### Implementation Pattern for Agents

All specialized agents follow a consistent implementation pattern based on the `StandardsCompliantAgent` base class:

1. **Create Agent Module**:
   ```python
   # in specialized_agents/your_domain/__init__.py
   from specialized_agents import StandardsCompliantAgent
   
   class YourDomainAgent(StandardsCompliantAgent):
       """A standards-compliant agent for your domain."""
       
       def __init__(self, job_role: str, port: int = None):
           supported_standards = [
               "STANDARD_1",
               "STANDARD_2",
               "STANDARD_3"
           ]
           super().__init__(job_role, "Your Domain Name", supported_standards, port)
           
           # Register MCP tools for collaboration
           from specialized_agents.your_domain.tools import (
               YourDomainTool1,
               YourDomainTool2,
               YourDomainTool3
           )
           
           # Register MCP tools for collaboration
           self.register_mcp_tool(YourDomainTool1())
           self.register_mcp_tool(YourDomainTool2())
           self.register_mcp_tool(YourDomainTool3())
   
       def getDomainPromptInstructions(self) -> str:
           """Return domain-specific instructions for the agent."""
           return """
           You are a specialized {job_role} in {domain}. 
           You must follow these domain-specific guidelines:
           1. First guideline specific to your domain
           2. Second guideline specific to your domain
           3. Third guideline specific to your domain
           
           You have access to specialized tools for {domain} tasks.
           """
   
       def validateDomainCompliance(self, content: str) -> dict:
           """Validate domain-specific compliance of content."""
           violations = []
           warnings = []
           
           # Add domain-specific validation rules
           # For example:
           if "non-compliant term" in content.lower():
               violations.append({
                   "standard": "STANDARD_1",
                   "description": "Content contains non-compliant terminology.",
                   "recommendation": "Replace with compliant alternative."
               })
           
           return {
               "compliant": len(violations) == 0,
               "violations": violations,
               "warnings": warnings
           }
   ```

2. **Implement Domain-Specific MCP Tools**:
   ```python
   # in specialized_agents/your_domain/tools.py
   from pydantic import BaseModel, Field
   from typing import Dict, Any, List, Optional
   from specialized_agents.collaboration.mcp_tool import StandardsCompliantMCPTool
   
   class YourToolInputSchema(BaseModel):
       """Input schema for YourDomainTool."""
       parameter1: str = Field(..., description="Description of parameter1")
       parameter2: int = Field(..., description="Description of parameter2")
       optional_param: Optional[str] = Field(None, description="Optional parameter")
   
   class YourDomainTool(StandardsCompliantMCPTool):
       """Tool for your domain operations."""
       
       def __init__(self):
           """Initialize the domain tool."""
           super().__init__(
               name="your_domain_tool",
               description="Performs specialized operations for your domain.",
               schema_model=YourToolInputSchema,
               supported_standards=["STANDARD_1", "STANDARD_2"],
               domain="Your Domain Name",
               tool_metadata={
                   "title": "Your Domain Tool",
                   "readOnlyHint": False,
                   "destructiveHint": False,
                   "idempotentHint": True,
                   "openWorldHint": False
               }
           )
       
       async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
           """Execute the tool functionality."""
           parameter1 = args.get("parameter1")
           parameter2 = args.get("parameter2")
           optional_param = args.get("optional_param")
           
           # Check if this is a collaboration call
           session_info = args.get("__session")
           
           # Add your tool's core logic here
           result = {
               "status": "success",
               "data": {
                   "result_field1": "Value based on processing",
                   "result_field2": parameter2 * 2  # Example calculation
               }
           }
           
           return result
       
       def format_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
           """Format the result for display."""
           if result.get("status") == "success":
               data = result.get("data", {})
               return [
                   {
                       "type": "data",
                       "data": result
                   },
                   {
                       "type": "text",
                       "text": f"""
                       ## Your Domain Tool Results
                       
                       - Result Field 1: {data.get('result_field1')}
                       - Result Field 2: {data.get('result_field2')}
                       
                       These results comply with [relevant standards].
                       """
                   }
               ]
           else:
               return [
                   {
                       "type": "text",
                       "text": f"Error: {result.get('error', 'Unknown error')}"
                   }
               ]
       
       def validate_input(self, args: Dict[str, Any]) -> Dict[str, Any]:
           """Validate input according to domain standards."""
           validation_result = {
               "valid": True,
               "violations": [],
               "warnings": []
           }
           
           parameter1 = args.get("parameter1", "")
           
           # Add domain-specific validation logic
           if "invalid term" in parameter1.lower():
               validation_result["valid"] = False
               validation_result["violations"].append({
                   "field": "parameter1",
                   "description": "Contains invalid terminology.",
                   "recommendation": "Use compliant alternatives."
               })
           
           return validation_result
       
       def requires_human_review(self, args: Dict[str, Any], result: Dict[str, Any]) -> bool:
           """Determine if human review is required."""
           parameter1 = args.get("parameter1", "")
           parameter2 = args.get("parameter2", 0)
           
           # Add logic to determine if human review is needed
           if parameter2 > 100 or "review required term" in parameter1.lower():
               return True
           
           return False
   ```

3. **Implementing Cross-Domain Collaboration**:
   ```python
   # Example of using the collaboration framework
   
   # 1. Start a collaboration session with multiple domains
   session_id = await your_agent.start_collaboration(["your_domain", "other_domain"])
   
   # 2. Call a tool using the collaboration session
   result = await your_agent.collaborate(
       session_id,
       "your_domain_tool",
       {
           "parameter1": "some value",
           "parameter2": 42
       }
   )
   
   # 3. Access results from other domains' tools
   other_domain_result = await your_agent.collaborate(
       session_id,
       "other_domain_tool",
       {
           "otherParam1": "value from your domain",
           "otherParam2": "context-specific value"
       }
   )
   
   # 4. The collaboration session maintains a shared context
   # that all agents can access during the collaboration
   ```

4. **Register the Agent**:
   ```python
   # In specialized_agents/registry.py
   # Import and register your domain agent
   from specialized_agents.your_domain import YourDomainAgent
   registry.register_agent_class("your_domain", YourDomainAgent)
   ```

4. **Initialize the Agent**:
   ```python
   # In run_graph_agent.py
   # Create a your_domain agent if it doesn't exist yet
   your_domain_agent_id = "your_domain_specialist"
   if your_domain_agent_id not in registry.get_all_agents():
       try:
           your_domain_agent = registry.create_agent("your_domain", "Specialist")
           print(f"✅ Created Your Domain Agent with {len(your_domain_agent.supported_standards)} supported standards")
       except Exception as e:
           print(f"❌ Failed to create Your Domain Agent: {str(e)}")
   else:
       print(f"✅ Your Domain Agent already initialized")
   ```

5. **Add Tests**:
   ```python
   # In graph/cli.py and test_integrated_agent.py
   # Add test cases for your new agent
   ```

6. **Update Documentation**:
   ```
   # In README.md
   # Document your new agent and its tools
   ```

### Example Tool Types

You can implement various types of tools for your domain agent:

1. **Analysis Tools**: Process input data and provide insights
2. **Generator Tools**: Create content, plans, or recommendations
3. **Evaluation Tools**: Assess compliance or quality against standards
4. **Resource Lookup Tools**: Retrieve relevant information from databases
5. **Workflow Tools**: Guide users through step-by-step processes

### Progress Tracking

We've successfully implemented the following specialized agents:

| Domain | Status | Description | Tools |
|--------|--------|-------------|-------|
| Agriculture | ✅ Completed | Provides guidance following USDA and other agricultural standards | <ul><li>Soil Analysis Tool</li><li>Crop Management Tool</li><li>Pesticide Application Tool</li></ul> |
| Telemedicine | ✅ Completed | Provides guidance following HIPAA, ATA guidelines, and telehealth regulations | <ul><li>Telehealth Platform Evaluation Tool</li><li>Telehealth Workflow Design Tool</li><li>Telehealth Regulatory Compliance Tool</li></ul> |
| Nutrition | ✅ Completed | Provides guidance following evidence-based nutrition guidelines and dietetic practice standards | <ul><li>Nutritional Assessment Tool</li><li>Meal Plan Generator Tool</li><li>Dietary Analysis Tool</li></ul> |
| Finance | 🔄 Planned | Will provide guidance following financial regulations and standards | <ul><li>Risk Assessment Tool</li><li>Investment Analysis Tool</li><li>Compliance Checker Tool</li></ul> |
| Education | 🔄 Planned | Will provide guidance following educational standards and best practices | <ul><li>Curriculum Development Tool</li><li>Assessment Design Tool</li><li>Learning Pathway Tool</li></ul> |
| Legal | 🔄 Planned | Will provide guidance following legal ethics and practice standards | <ul><li>Legal Research Tool</li><li>Document Analysis Tool</li><li>Compliance Assessment Tool</li></ul> |

### Implementation Roadmap

The project aims to implement over 200 specialized agent/tool pairs following the established pattern. Each implementation follows the same consistent structure:

1. Create the agent class with domain-specific compliance validation
2. Implement 3-5 specialized tools for the domain 
3. Register the agent in the registry
4. Add initialization in the runner script
5. Create tests for the new agent and tools
6. Update documentation

### Current Implementation Progress

| Category | Completed | Planned | Progress |
|----------|-----------|---------|----------|
| Specialized Agents | 3 | 200+ | 1.5% |
| Domain-Specific Tools | 9 | 600+ | 1.5% |
| Standards Validation Rules | 12 | 1000+ | 1.2% |
| Test Cases | 6 | 400+ | 1.5% |
| Deal-Based Collaboration | ✅ Implemented | - | 100% |

Upcoming domain implementations include:
- Finance/Banking
- Legal/Compliance
- Healthcare/Medical
- Education/Training
- Marketing/Advertising
- Human Resources
- Manufacturing
- Real Estate
- Insurance
- Cybersecurity

## Deals-Based Collaboration

With the recent migration from HMS-SME, this project now includes a powerful deals-based collaboration framework for structured interaction between specialized agents:

```python
# Start a deal-based collaboration
session_id = await agent_registry.create_collaboration_session(["agriculture", "nutrition"])

# Agriculture agent creates a deal
create_deal_args = {
    "name": "Nutritional Crop Optimization",
    "description": "Collaborative project to optimize crop farming for nutritional value",
    "deal_type": "collaboration",
    "participants": ["agriculture", "nutrition"]
}
deal_result = await session.call_tool("create_deal", create_deal_args, "agriculture")

# Nutrition agent joins the deal
join_deal_args = {
    "deal_id": deal_id,
    "role": "nutritional_advisor"
}
join_result = await session.call_tool("join_deal", join_deal_args, "nutrition")
```

The deals framework provides:

- **Structured Collaboration**: Organizes agent interactions around deals containing problems, solutions, and transactions
- **Graph-Based Relationships**: Models complex relationships between deal components
- **Standards Compliance**: Ensures all interactions adhere to domain-specific standards
- **Human Review**: Flags high-risk operations for human review

For more information, see the [Migration Guide](docs/migration.md).

This modular approach allows for rapid expansion to new domains while maintaining a consistent user experience and integration with the A2E framework.

## Docker Deployment (Optional)

```bash
# Build Image
docker build -t a2a-langgraph .

# Run Image
docker run -p 10003:10003 -e GOOGLE_API_KEY=your_api_key_here --name a2e a2a-langgraph

# Check Logs
docker logs -f a2e
```

## Troubleshooting

If you encounter issues:

1. Make sure the start_servers.py script is running and has successfully started the Currency, Math, and A2A MCP servers
2. Check that the required ports (10000, 10001, 10003) are not in use by other applications
3. Verify that your GOOGLE_API_KEY is valid and set correctly
4. For external A2A agents, ensure they are running and accessible at the URLs specified in A2A_ENDPOINT_URLS
5. Check the server logs for detailed error messages

## Learn More

- [A2A Protocol Documentation](https://google.github.io/A2A/#/documentation)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Model Context Protocol](https://github.com/google/model-context-protocol)
- [Google Gemini API](https://ai.google.dev/gemini-api)