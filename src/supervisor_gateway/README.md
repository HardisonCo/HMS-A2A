# Supervisor Gateway

The Supervisor Gateway is a central orchestration system that routes messages between the frontend (messaging-v1.vue) and multiple specialized agents. It integrates advanced economic modeling capabilities through Chain-of-Recursive-Thought (CoRT) methodology and theorem proving to address complex economic challenges like stagflation.

## Architecture

```
                 ┌─────────────────────────────┐
                 │     messaging-v1.vue        │
                 │    (Frontend Interface)     │
                 └───────────────┬─────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supervisor Gateway                         │
│  ┌──────────────┐  ┌────────────┐  ┌────────────────────────┐  │
│  │ Task Router  │  │ CoRT Engine│  │ Economic Analysis Core │  │
│  └──────┬───────┘  └─────┬──────┘  └──────────┬─────────────┘  │
└─────────┼────────────────┼───────────────────┼────────────────┘
          │                │                   │
          ▼                ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Agent Communication Layer                       │
│  (Standardized MCP-based protocol with FFI for theorem proving) │
└───┬────────────┬────────────┬─────────────┬──────────┬──────────┘
    │            │            │             │          │
    ▼            ▼            ▼             ▼          ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│Gov Agent│ │EHR Agent│ │SME Agent │ │Civ Agent │ │Economic Agent│
└────┬────┘ └────┬────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
     │           │           │            │              │
     ▼           ▼           ▼            ▼              ▼
┌──────────┐┌──────────┐┌──────────┐┌───────────┐┌──────────────────┐
│Government││Electronic ││Subject   ││Civilian   ││Economic Theorem  │
│Portal    ││Health    ││Matter    ││Information││Prover + Moneyball│
│System    ││Records   ││Expertise ││System     ││+ Genetic Algo    │
└──────────┘└──────────┘└──────────┘└───────────┘└──────────────────┘
```

## Core Components

### Supervisor Gateway

The central component that receives messages from the frontend and routes them to the appropriate specialized agents.

### Agent Registry

Maintains a registry of all available agents and provides methods for agent registration and retrieval.

### Communication Protocol

A standardized protocol for communication between the Supervisor Gateway and specialized agents, based on the Model Context Protocol (MCP).

### Chain-of-Recursive-Thought (CoRT) Engine

Implements the CoRT methodology for deep analysis of complex economic problems, enabling sophisticated recursive reasoning.

### Economic Analysis Core

Provides economic analysis capabilities including theorem proving, genetic algorithm optimization, and trade system integration.

### Knowledge Base Manager

Manages knowledge bases for all agents, providing access to domain-specific knowledge.

## Specialized Agents

### Economic Agent

Specializes in economic analysis, theorem proving, and policy recommendation. Integrates with the Economic Theorem Prover, Genetic Algorithm, and Moneyball Trade System.

### Government Agent (Gov)

Specializes in government policies, regulations, and legislative processes.

### Electronic Health Record Agent (EHR)

Specializes in health record data and healthcare systems.

### Subject Matter Expertise Agent (SME)

Provides domain-specific expertise across various fields.

### Civilian Agent (Civ)

Handles civilian/user-facing information and requests.

## Getting Started

### Prerequisites

- Node.js 18+
- TypeScript 5+
- Access to HMS component services

### Installation

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Start the server
npm start

# Development mode with auto-reload
npm run dev
```

### Running Tests

```bash
# Run all tests
npm test

# Run type checking
npm run typecheck

# Run linting
npm run lint
```

## Development

### File Structure

```
supervisor_gateway/
├── core/
│   ├── supervisor_gateway.ts
│   └── agent_registry.ts
├── agents/
│   ├── agent_interface.ts
│   ├── base_agent.ts
│   └── economic_agent.ts
├── communication/
│   └── message.ts
├── cort/
│   └── cort_engine.ts
├── economic/
│   ├── economic_analysis_core.ts
│   ├── theorem_prover_client.ts
│   ├── genetic_algorithm_client.ts
│   └── moneyball_trade_client.ts
├── knowledge/
│   ├── knowledge_base_manager.ts
│   └── knowledge_types.ts
├── monitoring/
│   └── health_types.ts
├── tools/
│   └── tool_types.ts
├── index.ts
└── package.json
```

## Key APIs

### Supervisor Gateway

```typescript
// Initialize the Supervisor Gateway
await supervisorGateway.initialize();

// Route a message from the frontend
const response = await supervisorGateway.routeMessage(userMessage);
```

### Agent Registry

```typescript
// Register an agent
agentRegistry.registerAgent(agent);

// Get an agent by ID
const agent = agentRegistry.getAgentById(agentId);

// Get agents by type
const agents = agentRegistry.getAgentsByType(AgentType.Economic);
```

### Agent Communication

```typescript
// Process a message
const response = await agent.processMessage(message);

// Invoke a tool
const result = await agent.invokeTool(toolId, parameters);

// Query knowledge
const result = await agent.queryKnowledge(query);
```

## Economic Features

The Supervisor Gateway integrates advanced economic capabilities:

- **Stagflation Analysis**: Detect and analyze stagflation conditions, identify causes, and recommend policies.
- **Tariff Impact Analysis**: Assess the impact of tariffs across sectors, on trade relationships, and consumer prices.
- **Economic Theorem Proving**: Formally verify economic statements and theories using mathematical reasoning.
- **Genetic Algorithm Optimization**: Optimize economic strategies and policies using evolutionary algorithms.
- **Moneyball Trade System**: Optimize trade relationships and agreements using data-driven approaches.

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT