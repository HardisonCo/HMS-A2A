# Self-Organizing Distributed Genetic System

This module implements a self-organizing distributed genetic algorithm system that integrates with HMS-A2A for service discovery and ecosystem integration. The system enables nodes to dynamically discover each other, form service clusters, and collaborate on genetic algorithm computations.

## Key Features

- **Self-organizing nodes** that can discover and join each other to form computation clusters
- **Service-oriented architecture** where nodes can provide specific genetic algorithm services
- **MCP and A2A standards** integration for seamless connection to the HMS ecosystem
- **Dynamic role adaptation** where nodes can adapt between coordinator and worker roles
- **Fault tolerance** with automatic recovery from node failures
- **Efficient load balancing** across multiple machines
- **Service registry** for discovering available genetic computation services

## Architecture

The system follows a modular architecture with several key components:

### 1. Core Components

- **DistributedNode**: Base node that can function as coordinator or worker
- **DistributedCluster**: Manages a cluster of distributed nodes for genetic computation
- **DistributedGeneticEngine**: Extended genetic engine that distributes computation
- **SelfOrganizingNode**: Node that can discover and join clusters autonomously
- **ServiceCluster**: Manages a specific genetic algorithm service across multiple nodes
- **A2AIntegration**: Enables integration with the HMS-A2A ecosystem

### 2. Communication Layer

- **WebSocket**: For real-time communication between nodes
- **JSON-RPC**: For standardized API calls following A2A conventions
- **Server-Sent Events (SSE)**: For event streaming
- **HTTP API**: For node management and service discovery

### 3. Integration Standards

- **MCP Tools Registry**: For registering and discovering genetic algorithm tools
- **A2A Agent Interface**: For presenting capabilities as A2A agents
- **Service Registry**: For managing genetic algorithm services

## Usage

### 1. Starting a Self-Organizing Node

```typescript
// Create a self-organizing node
const node = new SelfOrganizingNode({
  httpPort: 8080,
  discoveryMode: DiscoveryMode.ACTIVE,
  rolePreference: RolePreference.ADAPTIVE,
  discoveryEndpoints: ['http://discovery-server:8000'],
  geneticEngine: new AdvancedGeneticRepairEngine()
});

// Start the node
await node.start();
```

### 2. Creating a Service Cluster

```typescript
// Define a genetic algorithm service
const serviceDefinition: ServiceDefinition = {
  id: 'genetic-optimization-service',
  name: 'Genetic Optimization Service',
  description: 'Distributed genetic algorithm optimization',
  type: 'genetic-computation',
  capabilities: ['genetic-algorithm', 'optimization'],
  requirements: {
    minNodes: 3,
    preferredNodes: 5,
    nodeCapabilities: ['advanced-genetic']
  }
};

// Create a service cluster
const serviceCluster = new ServiceCluster(
  serviceDefinition,
  node,
  distributedGeneticEngine
);

// Start the service cluster
await serviceCluster.start();
```

### 3. Using the Distributed Genetic Engine

```typescript
// Create a distributed genetic engine
const geneticEngine = new DistributedGeneticEngine();

// Run a genetic algorithm
const result = await geneticEngine.run(
  initialPopulation,
  fitnessFunction,
  100, // generations
  0.95 // target fitness
);
```

## Integration with HMS-A2A

The system integrates with HMS-A2A through several mechanisms:

### 1. Agent Card

Each node exposes an agent card following the A2A standard, accessible at:
- `/.well-known/agent.json`
- `/agent-card`

The agent card describes the node's capabilities, including:
- Genetic computation capabilities
- Advanced genetic operators available
- Node role and resources
- Service cluster memberships

### 2. JSON-RPC API

The system exposes a JSON-RPC API following the A2A standard, including methods like:
- `node/info`: Get information about the node
- `discovery/list`: List discovered nodes
- `services/list`: List available services
- `services/register`: Register a new service
- `topology/get`: Get the network topology

### 3. MCP Tools Registry

Genetic algorithm capabilities are exposed through the MCP Tools Registry, with tools like:
- `discoverGeneticServices`: Find available genetic computation services
- `getNodeInfo`: Get information about a node
- `getClusterStatus`: Get status of a distributed cluster
- `runGeneticAlgorithm`: Run a genetic algorithm computation

## Deployment

The system can be deployed in various configurations:

### 1. Single Machine

Run multiple nodes on a single machine with different ports:

```bash
# Start coordinator node
node dist/cli.js start-node --port 8080 --role coordinator

# Start worker nodes
node dist/cli.js start-node --port 8081 --role worker --coordinator http://localhost:8080
node dist/cli.js start-node --port 8082 --role worker --coordinator http://localhost:8080
```

### 2. Distributed Deployment

Run nodes across multiple machines:

```bash
# Start coordinator node on machine A
node dist/cli.js start-node --port 8080 --role coordinator --public-url http://machine-a:8080

# Start worker nodes on other machines
node dist/cli.js start-node --port 8080 --role worker --coordinator http://machine-a:8080
```

### 3. Container Deployment

Deploy using Docker and Docker Compose:

```yaml
services:
  coordinator:
    image: genetic-system
    ports:
      - "8080:8080"
    environment:
      - NODE_ROLE=COORDINATOR
      - PUBLIC_URL=http://coordinator:8080

  worker1:
    image: genetic-system
    environment:
      - NODE_ROLE=WORKER
      - COORDINATOR_URL=http://coordinator:8080

  worker2:
    image: genetic-system
    environment:
      - NODE_ROLE=WORKER
      - COORDINATOR_URL=http://coordinator:8080
```

## Advanced Features

### 1. Self-Healing

The system includes self-healing capabilities to handle node failures:

- **Circuit breakers** to prevent cascading failures
- **Health monitoring** to detect and respond to node failures
- **Automatic redistribution** of workload when nodes fail
- **Recovery strategies** based on failure patterns

### 2. Service Discovery

Nodes can discover services through multiple mechanisms:

- **Direct discovery** through known endpoints
- **A2A agent discovery** through the A2A ecosystem
- **Service registry** for specialized genetic algorithm services
- **Capability-based discovery** to find nodes with specific capabilities

### 3. Adaptive Roles

Nodes can adapt their roles based on the network needs:

- **Role negotiation** to determine the optimal role
- **Dynamic promotion** of workers to coordinators when needed
- **Resource-based allocation** where more capable nodes become coordinators
- **Service-specific roles** within service clusters

### 4. Mesh Networking

In mesh mode, nodes form a full peer-to-peer network:

- **Peer-to-peer task distribution** without central coordinator
- **Distributed consensus** for decision making
- **Resilient message routing** between nodes
- **Topology discovery and maintenance**

## API Reference

See the following files for detailed API documentation:

- `distributed_node.ts`: Base distributed node implementation
- `distributed_cluster.ts`: Cluster management
- `a2a_integration.ts`: A2A ecosystem integration
- `self_organizing_node.ts`: Self-organizing node capabilities
- `service_cluster.ts`: Service-oriented clustering

## License

This module is part of the HMS-DEV project and is licensed under the same terms.