import express from 'express';
import bodyParser from 'body-parser';
import { v4 as uuidv4 } from 'uuid';
import { EventEmitter } from 'events';
import { createComponentLogger } from '../../utils/logger';
import { DistributedNode } from './distributed_node';
import { DistributedCluster } from './distributed_cluster';
import { NodeRole, NodeStatus, NodeInfo, TaskType } from './distributed_types';
import { DistributedError, tryCatch } from '../../utils/error_handling';
import { 
  A2ADistributedNodeIntegration, 
  A2AClient,
  AgentCard 
} from './a2a_integration';
import { 
  DistributedHealthMonitor, 
  NodeConnectionCircuitBreaker 
} from './distributed_error_handling';
import { AdvancedGeneticRepairEngine } from '../advanced/advanced_genetic_repair_engine';

const logger = createComponentLogger('self-organizing-node');

/**
 * Self-organizing node error
 */
export class SelfOrganizingNodeError extends DistributedError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'SELF_ORGANIZING_NODE_ERROR',
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Discovery mode for self-organizing nodes
 */
export enum DiscoveryMode {
  PASSIVE = 'passive',         // Wait for coordinator invite
  ACTIVE = 'active',           // Actively search for other nodes
  BOOTSTRAP = 'bootstrap',     // Create a new coordinator node
  MESH = 'mesh'                // Full P2P mesh network
}

/**
 * Role preference for self-organizing nodes
 */
export enum RolePreference {
  WORKER = 'worker',           // Prefer to be a worker
  COORDINATOR = 'coordinator', // Prefer to be a coordinator
  ADAPTIVE = 'adaptive'        // Adapt based on network needs
}

/**
 * Node metadata for service registry
 */
export interface NodeMetadata {
  id: string;
  name?: string;
  description?: string;
  capabilities: string[];
  tags: string[];
  resources: {
    cpu?: number;
    memory?: number;
    gpu?: boolean;
    score?: number;
  };
  location?: {
    region?: string;
    zone?: string;
    metadata?: Record<string, string>;
  };
}

/**
 * Network topology information
 */
export interface NetworkTopology {
  coordinators: Map<string, {
    info: NodeInfo;
    workers: string[];
    lastSeen: number;
  }>;
  workers: Map<string, {
    info: NodeInfo;
    coordinatorId?: string;
    lastSeen: number;
  }>;
  mesh: Map<string, {
    connections: string[];
    lastSeen: number;
  }>;
}

/**
 * Service definition for service clusters
 */
export interface ServiceDefinition {
  id: string;
  name: string;
  description: string;
  type: string;
  capabilities: string[];
  requirements?: {
    minNodes?: number;
    preferredNodes?: number;
    nodeCapabilities?: string[];
  };
  metadata?: Record<string, any>;
}

/**
 * Service registry entry
 */
export interface ServiceRegistryEntry {
  service: ServiceDefinition;
  nodes: string[];
  status: 'provisioning' | 'ready' | 'degraded' | 'failed';
  created: number;
  updated: number;
}

/**
 * Self-organizing node that can discover and join clusters
 */
export class SelfOrganizingNode extends EventEmitter {
  private nodeId: string;
  private distributedNode?: DistributedNode;
  private cluster?: DistributedCluster;
  private geneticEngine?: AdvancedGeneticRepairEngine;
  private a2aIntegration?: A2ADistributedNodeIntegration;
  private healthMonitor?: DistributedHealthMonitor;
  private circuitBreaker: NodeConnectionCircuitBreaker;
  private httpServer: express.Application;
  private httpPort: number;
  private baseUrl: string;
  private discoveryMode: DiscoveryMode;
  private rolePreference: RolePreference;
  private knownCoordinators: Map<string, {
    url: string;
    card: AgentCard;
    nodeInfo?: NodeInfo;
    lastSeen: number;
    priority: number;
  }> = new Map();
  private knownWorkers: Map<string, {
    url: string;
    card: AgentCard;
    nodeInfo?: NodeInfo;
    lastSeen: number;
    assignedCoordinator?: string;
  }> = new Map();
  private metadata: NodeMetadata;
  private services: Map<string, ServiceRegistryEntry> = new Map();
  private role: NodeRole = NodeRole.WORKER;
  private status: NodeStatus = NodeStatus.INITIALIZING;
  private discoveryEndpoints: string[] = [];
  private isRunning: boolean = false;
  private topologyInterval?: NodeJS.Timeout;
  private serviceManagementInterval?: NodeJS.Timeout;
  private resourceMonitorInterval?: NodeJS.Timeout;
  
  constructor(
    options: {
      nodeId?: string;
      httpPort?: number;
      baseUrl?: string;
      discoveryMode?: DiscoveryMode;
      rolePreference?: RolePreference;
      discoveryEndpoints?: string[];
      metadata?: Partial<NodeMetadata>;
      geneticEngine?: AdvancedGeneticRepairEngine;
    } = {}
  ) {
    super();
    this.nodeId = options.nodeId || uuidv4();
    this.httpPort = options.httpPort || 0; // 0 = random available port
    this.baseUrl = options.baseUrl || '';  // Will be set when server starts
    this.discoveryMode = options.discoveryMode || DiscoveryMode.ACTIVE;
    this.rolePreference = options.rolePreference || RolePreference.ADAPTIVE;
    this.discoveryEndpoints = options.discoveryEndpoints || [];
    this.geneticEngine = options.geneticEngine;
    this.circuitBreaker = new NodeConnectionCircuitBreaker();
    
    // Create metadata with defaults
    this.metadata = {
      id: this.nodeId,
      capabilities: ['genetic-algorithm', 'distributed-computing'],
      tags: [],
      resources: {
        cpu: require('os').cpus().length,
        memory: Math.floor(require('os').totalmem() / (1024 * 1024 * 1024)),
        gpu: false,
        score: 0 // Will be calculated
      }
    };
    
    // Merge provided metadata
    if (options.metadata) {
      this.metadata = {
        ...this.metadata,
        ...options.metadata,
        id: this.nodeId, // Ensure ID is consistent
        resources: {
          ...this.metadata.resources,
          ...options.metadata.resources
        }
      };
    }
    
    // Add more capabilities based on genetic engine
    if (this.geneticEngine) {
      this.metadata.capabilities.push('advanced-genetic');
      if (this.geneticEngine.constructor.name === 'AdaptiveGeneticEngine') {
        this.metadata.capabilities.push('adaptive-parameters');
      }
    }
    
    // Calculate resource score (simple heuristic)
    this.metadata.resources.score = this.calculateResourceScore();
    
    // Create HTTP server
    this.httpServer = express();
    this.setupHttpServer();
  }
  
  /**
   * Calculate resource score for node capability assessment
   */
  private calculateResourceScore(): number {
    const cpuScore = (this.metadata.resources.cpu || 1) * 10;
    const memoryScore = (this.metadata.resources.memory || 1) * 5;
    const gpuScore = this.metadata.resources.gpu ? 50 : 0;
    
    return cpuScore + memoryScore + gpuScore;
  }
  
  /**
   * Set up HTTP server for API and webhook endpoints
   */
  private setupHttpServer(): void {
    // Set up middleware
    this.httpServer.use(bodyParser.json());
    
    // Endpoint for health checks
    this.httpServer.get('/health', (req, res) => {
      res.json({
        id: this.nodeId,
        role: this.role,
        status: this.status,
        uptime: process.uptime()
      });
    });
    
    // Endpoint for node info
    this.httpServer.get('/info', (req, res) => {
      res.json({
        id: this.nodeId,
        role: this.role,
        status: this.status,
        metadata: this.metadata,
        discoveryMode: this.discoveryMode,
        rolePreference: this.rolePreference,
        knownCoordinators: this.knownCoordinators.size,
        knownWorkers: this.knownWorkers.size,
        services: Array.from(this.services.values()).map(entry => ({
          id: entry.service.id,
          name: entry.service.name,
          type: entry.service.type,
          status: entry.status,
          nodes: entry.nodes.length
        }))
      });
    });
    
    // API endpoint for node registration (worker -> coordinator)
    this.httpServer.post('/api/register', async (req, res) => {
      if (this.role !== NodeRole.COORDINATOR) {
        return res.status(400).json({
          error: 'This node is not a coordinator'
        });
      }
      
      try {
        const { nodeId, url, metadata } = req.body;
        
        if (!nodeId || !url) {
          return res.status(400).json({
            error: 'Missing required fields: nodeId, url'
          });
        }
        
        // Create A2A client to verify the node
        const client = new A2AClient(url);
        const card = await client.getAgentCard();
        
        // Register worker
        this.registerWorkerNode(nodeId, url, card, metadata);
        
        res.json({
          success: true,
          coordinatorId: this.nodeId,
          message: 'Node registered successfully'
        });
      } catch (error) {
        logger.error(`Error registering node: ${error}`);
        res.status(500).json({
          error: 'Failed to register node',
          message: error instanceof Error ? error.message : String(error)
        });
      }
    });
    
    // API endpoint for service registration
    this.httpServer.post('/api/services', async (req, res) => {
      try {
        const serviceDefinition: ServiceDefinition = req.body;
        
        if (!serviceDefinition.id || !serviceDefinition.name || !serviceDefinition.type) {
          return res.status(400).json({
            error: 'Missing required fields in service definition'
          });
        }
        
        const result = await this.registerService(serviceDefinition);
        
        res.json({
          success: true,
          service: result
        });
      } catch (error) {
        logger.error(`Error registering service: ${error}`);
        res.status(500).json({
          error: 'Failed to register service',
          message: error instanceof Error ? error.message : String(error)
        });
      }
    });
    
    // API endpoint for service list
    this.httpServer.get('/api/services', (req, res) => {
      res.json({
        services: Array.from(this.services.values())
      });
    });
    
    // API endpoint for topology
    this.httpServer.get('/api/topology', (req, res) => {
      res.json(this.getNetworkTopology());
    });
    
    // A2A agent card endpoint
    this.httpServer.get('/.well-known/agent.json', (req, res) => {
      res.json(this.getAgentCard());
    });
    
    // A2A agent card alternative endpoint
    this.httpServer.get('/agent-card', (req, res) => {
      res.json(this.getAgentCard());
    });
    
    // JSON-RPC API endpoint
    this.httpServer.post('/', async (req, res) => {
      const rpcRequest = req.body;
      
      if (!rpcRequest.jsonrpc || rpcRequest.jsonrpc !== '2.0' || !rpcRequest.method) {
        return res.status(400).json({
          jsonrpc: '2.0',
          id: rpcRequest.id || null,
          error: {
            code: -32600,
            message: 'Invalid Request'
          }
        });
      }
      
      try {
        const result = await this.handleRpcRequest(rpcRequest.method, rpcRequest.params || {});
        
        res.json({
          jsonrpc: '2.0',
          id: rpcRequest.id,
          result
        });
      } catch (error) {
        logger.error(`RPC error for method ${rpcRequest.method}: ${error}`);
        
        res.json({
          jsonrpc: '2.0',
          id: rpcRequest.id,
          error: {
            code: -32000,
            message: error instanceof Error ? error.message : String(error)
          }
        });
      }
    });
    
    // Webhook endpoint for A2A notifications
    this.httpServer.post('/webhook', async (req, res) => {
      try {
        const { event, data } = req.body;
        
        if (event === 'agent.discovered') {
          await this.handleAgentDiscovered(data);
        } else if (event === 'service.created') {
          await this.handleServiceCreated(data);
        }
        
        res.json({ success: true });
      } catch (error) {
        logger.error(`Webhook error: ${error}`);
        res.status(500).json({ error: 'Webhook processing failed' });
      }
    });
  }
  
  /**
   * Get agent card for A2A integration
   */
  private getAgentCard(): AgentCard {
    return {
      name: `distributed-genetic-${this.role.toLowerCase()}-${this.nodeId}`,
      version: '1.0.0',
      description: `Self-organizing genetic algorithm ${this.role.toLowerCase()} node`,
      capabilities: [
        {
          name: 'genetic-computation',
          description: 'Distributed genetic algorithm computation',
          tags: ['genetic-algorithm', 'distributed-computing', this.role.toLowerCase()]
        },
        {
          name: 'self-organizing',
          description: 'Self-organizing node capabilities',
          tags: ['service-discovery', 'adaptive-roles']
        },
        ...(this.role === NodeRole.COORDINATOR ? [
          {
            name: 'coordinator',
            description: 'Genetic algorithm coordinator capabilities',
            tags: ['task-distribution', 'worker-management']
          }
        ] : []),
        ...(this.role === NodeRole.WORKER ? [
          {
            name: 'worker',
            description: 'Genetic algorithm worker capabilities',
            tags: ['fitness-evaluation', 'task-execution']
          }
        ] : [])
      ],
      endpoints: {
        jsonrpc: this.baseUrl,
        sse: `${this.baseUrl}sse`
      }
    };
  }
  
  /**
   * Handle JSON-RPC requests
   */
  private async handleRpcRequest(method: string, params: any): Promise<any> {
    switch (method) {
      case 'node/info':
        return {
          id: this.nodeId,
          role: this.role,
          status: this.status,
          metadata: this.metadata
        };
      
      case 'discovery/list':
        return {
          coordinators: Array.from(this.knownCoordinators.entries()).map(([id, data]) => ({
            id,
            url: data.url,
            lastSeen: data.lastSeen
          })),
          workers: Array.from(this.knownWorkers.entries()).map(([id, data]) => ({
            id,
            url: data.url,
            assignedCoordinator: data.assignedCoordinator,
            lastSeen: data.lastSeen
          }))
        };
      
      case 'discovery/register':
        if (!params.agent) {
          throw new Error('Missing agent information');
        }
        
        // Register the agent as appropriate based on capabilities
        const isCoordinator = params.agent.capabilities.some(
          (cap: any) => cap.name === 'coordinator' || cap.tags.includes('coordinator')
        );
        
        const isWorker = params.agent.capabilities.some(
          (cap: any) => cap.name === 'worker' || cap.tags.includes('worker')
        );
        
        if (isCoordinator) {
          this.registerCoordinatorFromCard(params.agent);
        } else if (isWorker) {
          this.registerWorkerFromCard(params.agent);
        }
        
        return { success: true };
      
      case 'services/list':
        return {
          services: Array.from(this.services.values())
        };
      
      case 'services/register':
        if (!params.service) {
          throw new Error('Missing service definition');
        }
        
        const result = await this.registerService(params.service);
        return { success: true, service: result };
      
      case 'services/join':
        if (!params.serviceId || !params.nodeId) {
          throw new Error('Missing required parameters: serviceId, nodeId');
        }
        
        await this.joinService(params.serviceId, params.nodeId);
        return { success: true };
      
      case 'topology/get':
        return this.getNetworkTopology();
      
      default:
        throw new Error(`Unknown method: ${method}`);
    }
  }
  
  /**
   * Handle agent discovered notification
   */
  private async handleAgentDiscovered(data: any): Promise<void> {
    const { agentCard, url } = data;
    
    // Check if this is a genetic node
    const isGeneticNode = agentCard.capabilities.some(
      (cap: any) => cap.name === 'genetic-computation' || 
                   cap.tags.includes('genetic-algorithm')
    );
    
    if (!isGeneticNode) {
      return;
    }
    
    // Register as appropriate
    const isCoordinator = agentCard.capabilities.some(
      (cap: any) => cap.name === 'coordinator' || cap.tags.includes('coordinator')
    );
    
    const isWorker = agentCard.capabilities.some(
      (cap: any) => cap.name === 'worker' || cap.tags.includes('worker')
    );
    
    if (isCoordinator) {
      this.registerCoordinatorFromCard(agentCard, url);
    } else if (isWorker) {
      this.registerWorkerFromCard(agentCard, url);
    }
  }
  
  /**
   * Handle service created notification
   */
  private async handleServiceCreated(data: any): Promise<void> {
    const { service } = data;
    
    // Check if this is a service we're interested in
    if (service.type !== 'genetic-computation' && 
        !service.capabilities.includes('genetic-algorithm')) {
      return;
    }
    
    // Register the service
    await this.registerService(service);
  }
  
  /**
   * Register a coordinator from an agent card
   */
  private registerCoordinatorFromCard(card: AgentCard, url?: string): void {
    // Extract coordinator ID from name or endpoints
    const coordinatorUrl = url || card.endpoints.jsonrpc;
    const coordinatorId = card.name.split('-').pop() || uuidv4();
    
    if (coordinatorId === this.nodeId) {
      // Don't register ourselves
      return;
    }
    
    // Calculate priority based on capabilities
    let priority = 0;
    card.capabilities.forEach(cap => {
      if (cap.name === 'advanced-genetic' || cap.tags.includes('advanced-genetic')) {
        priority += 5;
      }
      if (cap.name === 'adaptive-parameters' || cap.tags.includes('adaptive-parameters')) {
        priority += 3;
      }
    });
    
    // Add to known coordinators
    this.knownCoordinators.set(coordinatorId, {
      url: coordinatorUrl,
      card,
      lastSeen: Date.now(),
      priority
    });
    
    logger.info(`Registered coordinator node ${coordinatorId} at ${coordinatorUrl}`);
    this.emit('coordinatorDiscovered', coordinatorId, coordinatorUrl, card);
  }
  
  /**
   * Register a worker from an agent card
   */
  private registerWorkerFromCard(card: AgentCard, url?: string): void {
    // Extract worker ID from name or endpoints
    const workerUrl = url || card.endpoints.jsonrpc;
    const workerId = card.name.split('-').pop() || uuidv4();
    
    if (workerId === this.nodeId) {
      // Don't register ourselves
      return;
    }
    
    // Add to known workers
    this.knownWorkers.set(workerId, {
      url: workerUrl,
      card,
      lastSeen: Date.now()
    });
    
    logger.info(`Registered worker node ${workerId} at ${workerUrl}`);
    this.emit('workerDiscovered', workerId, workerUrl, card);
  }
  
  /**
   * Register a worker node with this coordinator
   */
  private registerWorkerNode(
    nodeId: string,
    url: string,
    card: AgentCard,
    metadata?: NodeMetadata
  ): void {
    if (this.role !== NodeRole.COORDINATOR) {
      throw new Error('Only coordinator nodes can register workers');
    }
    
    // Add to known workers
    this.knownWorkers.set(nodeId, {
      url,
      card,
      nodeInfo: {
        id: nodeId,
        role: NodeRole.WORKER,
        status: NodeStatus.READY,
        tasks: {
          pending: 0,
          running: 0,
          completed: 0,
          failed: 0
        },
        capabilities: metadata?.capabilities || [],
        lastHeartbeat: Date.now()
      },
      lastSeen: Date.now(),
      assignedCoordinator: this.nodeId
    });
    
    logger.info(`Registered worker node ${nodeId} at ${url}`);
    this.emit('workerRegistered', nodeId, url, card, metadata);
    
    // Notify distributed node about the new worker if it exists
    if (this.distributedNode && this.role === NodeRole.COORDINATOR) {
      // Implementation would connect this to the actual distributed node
      // This is a placeholder for integration
    }
  }
  
  /**
   * Start the self-organizing node
   */
  public async start(): Promise<void> {
    if (this.isRunning) {
      return;
    }
    
    try {
      // Start HTTP server on specified or random port
      await new Promise<void>((resolve, reject) => {
        const server = this.httpServer.listen(this.httpPort, () => {
          const address = server.address();
          if (address && typeof address !== 'string') {
            // Update actual port if it was assigned randomly
            this.httpPort = address.port;
            
            // Set base URL if not provided
            if (!this.baseUrl) {
              this.baseUrl = `http://localhost:${this.httpPort}/`;
            }
            
            logger.info(`HTTP server started on port ${this.httpPort}`);
            resolve();
          } else {
            reject(new Error('Failed to get server address'));
          }
        });
        
        server.on('error', (error) => {
          reject(new Error(`Failed to start HTTP server: ${error}`));
        });
      });
      
      // Choose initial role based on preferences and discovery mode
      await this.determineInitialRole();
      
      // Initialize appropriate node type based on role
      await this.initializeNode();
      
      // Start A2A integration
      this.a2aIntegration = new A2ADistributedNodeIntegration(
        this.nodeId,
        this.role,
        this.status,
        this.httpPort,
        this.baseUrl,
        this.discoveryEndpoints
      );
      
      await this.a2aIntegration.start(this.httpServer);
      
      // Set up event handlers for A2A integration
      this.setupA2AEventHandlers();
      
      // Start periodic tasks
      this.startPeriodicTasks();
      
      this.isRunning = true;
      this.status = NodeStatus.READY;
      
      logger.info(`Self-organizing node started with role: ${this.role}`);
      this.emit('started', this.role);
    } catch (error) {
      this.status = NodeStatus.ERROR;
      logger.error(`Failed to start self-organizing node: ${error}`);
      throw new SelfOrganizingNodeError('Failed to start self-organizing node', {
        cause: error instanceof Error ? error : new Error(String(error))
      });
    }
  }
  
  /**
   * Determine the initial role based on preferences and discovery mode
   */
  private async determineInitialRole(): Promise<void> {
    // Default to worker
    let chosenRole = NodeRole.WORKER;
    
    switch (this.discoveryMode) {
      case DiscoveryMode.BOOTSTRAP:
        // Always start as coordinator in bootstrap mode
        chosenRole = NodeRole.COORDINATOR;
        break;
      
      case DiscoveryMode.ACTIVE:
        // In active mode, prefer role based on preference
        if (this.rolePreference === RolePreference.COORDINATOR) {
          chosenRole = NodeRole.COORDINATOR;
        } else if (this.rolePreference === RolePreference.ADAPTIVE) {
          // Try to find existing coordinators
          const existingCoordinators = await this.discoverExistingCoordinators();
          
          if (existingCoordinators.length === 0) {
            // No coordinators found, become one
            chosenRole = NodeRole.COORDINATOR;
          } else {
            // Coordinators exist, become worker
            chosenRole = NodeRole.WORKER;
          }
        }
        break;
      
      case DiscoveryMode.PASSIVE:
        // Always start as worker in passive mode
        chosenRole = NodeRole.WORKER;
        break;
      
      case DiscoveryMode.MESH:
        // In mesh mode, select based on resource score
        if (this.metadata.resources.score > 50) {
          // Higher resource nodes tend to become coordinators
          chosenRole = NodeRole.COORDINATOR;
        } else {
          chosenRole = NodeRole.WORKER;
        }
        break;
    }
    
    this.role = chosenRole;
  }
  
  /**
   * Discover existing coordinators in the network
   */
  private async discoverExistingCoordinators(): Promise<Array<{ 
    id: string; 
    url: string;
    priority: number;
  }>> {
    const results: Array<{ id: string; url: string; priority: number }> = [];
    
    // Use discovery endpoints to find coordinators
    for (const endpoint of this.discoveryEndpoints) {
      try {
        const client = new A2AClient(endpoint);
        const result = await client.callMethod<any>('discovery/list', {});
        
        if (result.coordinators && Array.isArray(result.coordinators)) {
          for (const coordinator of result.coordinators) {
            if (coordinator.id !== this.nodeId) {
              results.push({
                id: coordinator.id,
                url: coordinator.url,
                priority: coordinator.priority || 0
              });
            }
          }
        }
      } catch (error) {
        logger.warn(`Failed to discover coordinators from ${endpoint}: ${error}`);
      }
    }
    
    return results;
  }
  
  /**
   * Initialize the appropriate node type based on role
   */
  private async initializeNode(): Promise<void> {
    if (this.role === NodeRole.COORDINATOR) {
      // Initialize as coordinator
      this.distributedNode = new DistributedNode(
        NodeRole.COORDINATOR,
        this.httpPort + 1, // WebSocket port = HTTP port + 1
        undefined,
        this.geneticEngine
      );
      
      // Create cluster
      this.cluster = new DistributedCluster(
        this.httpPort + 1,
        0, // Start with no workers
        this.geneticEngine,
        true // Enable auto-scaling
      );
      
      // Set up health monitoring
      this.healthMonitor = new DistributedHealthMonitor(this.cluster, {
        onNodeUnhealthy: (nodeId, info) => {
          logger.warn(`Node ${nodeId} is unhealthy, role: ${info.role}`);
        }
      });
      
      this.healthMonitor.start();
    } else {
      // Initialize as worker
      // Find best coordinator to connect to
      let coordinatorUrl: string | undefined;
      let bestCoordinator: { id: string; priority: number } | undefined;
      
      if (this.knownCoordinators.size > 0) {
        // Choose coordinator with highest priority
        for (const [id, data] of this.knownCoordinators) {
          if (!bestCoordinator || data.priority > bestCoordinator.priority) {
            bestCoordinator = { id, priority: data.priority };
            coordinatorUrl = data.url;
          }
        }
      }
      
      if (!coordinatorUrl && this.discoveryEndpoints.length > 0) {
        // Try discovery endpoints
        const coordinators = await this.discoverExistingCoordinators();
        
        if (coordinators.length > 0) {
          // Sort by priority
          coordinators.sort((a, b) => b.priority - a.priority);
          bestCoordinator = { id: coordinators[0].id, priority: coordinators[0].priority };
          coordinatorUrl = coordinators[0].url;
        }
      }
      
      if (!coordinatorUrl) {
        if (this.discoveryMode === DiscoveryMode.ACTIVE) {
          // In active mode, convert to coordinator if no coordinators found
          logger.info('No coordinators found, converting to coordinator role');
          this.role = NodeRole.COORDINATOR;
          return this.initializeNode();
        } else {
          throw new SelfOrganizingNodeError('No coordinator found and not allowed to become one');
        }
      }
      
      // Connect WebSocket to coordinator
      const wsUrl = coordinatorUrl.replace(/^http/, 'ws');
      
      this.distributedNode = new DistributedNode(
        NodeRole.WORKER,
        0, // Worker doesn't need to listen
        wsUrl,
        this.geneticEngine
      );
      
      logger.info(`Worker node initialized, connected to coordinator at ${wsUrl}`);
      
      if (bestCoordinator) {
        // Register with the coordinator via HTTP API
        await this.registerWithCoordinator(bestCoordinator.id, coordinatorUrl);
      }
    }
  }
  
  /**
   * Register this worker with a coordinator
   */
  private async registerWithCoordinator(coordinatorId: string, url: string): Promise<void> {
    try {
      const client = new A2AClient(url);
      
      await client.callMethod('node/register', {
        nodeId: this.nodeId,
        url: this.baseUrl,
        metadata: this.metadata
      });
      
      logger.info(`Registered with coordinator ${coordinatorId} at ${url}`);
    } catch (error) {
      logger.error(`Failed to register with coordinator ${coordinatorId}: ${error}`);
      throw new SelfOrganizingNodeError('Failed to register with coordinator', {
        context: { coordinatorId, url },
        cause: error instanceof Error ? error : new Error(String(error))
      });
    }
  }
  
  /**
   * Set up event handlers for A2A integration
   */
  private setupA2AEventHandlers(): void {
    if (!this.a2aIntegration) {
      return;
    }
    
    this.a2aIntegration.on('agentDiscovered', (agentId, url, card) => {
      logger.debug(`A2A agent discovered: ${agentId} at ${url}`);
    });
    
    this.a2aIntegration.on('geneticServiceDiscovered', (agentId, url, card) => {
      logger.info(`Genetic service discovered: ${agentId} at ${url}`);
      
      // Check if this is a coordinator or worker
      const isCoordinator = card.capabilities.some(cap => 
        cap.name === 'coordinator' || cap.tags.includes('coordinator')
      );
      
      const isWorker = card.capabilities.some(cap => 
        cap.name === 'worker' || cap.tags.includes('worker')
      );
      
      if (isCoordinator) {
        // Add to known coordinators
        this.registerCoordinatorFromCard(card, url);
        
        // If we're a worker without a coordinator, consider connecting
        if (this.role === NodeRole.WORKER && 
           (!this.distributedNode || this.distributedNode.getStatus() === NodeStatus.DISCONNECTED)) {
          this.considerConnectingToCoordinator(agentId, url);
        }
      } else if (isWorker && this.role === NodeRole.COORDINATOR) {
        // If we're a coordinator, add to known workers
        this.registerWorkerFromCard(card, url);
      }
    });
  }

  /**
   * Consider connecting to a discovered coordinator
   */
  private considerConnectingToCoordinator(coordinatorId: string, url: string): void {
    // This would implement the logic to potentially switch coordinators
    // when a better one is discovered
    
    // For now, just log that we found a potential coordinator
    logger.info(`Found potential coordinator ${coordinatorId} at ${url}`);
  }
  
  /**
   * Start periodic tasks
   */
  private startPeriodicTasks(): void {
    // Network topology management
    this.topologyInterval = setInterval(() => {
      this.updateNetworkTopology();
    }, 30000); // Every 30 seconds
    
    // Service management
    this.serviceManagementInterval = setInterval(() => {
      this.manageServices();
    }, 60000); // Every minute
    
    // Resource monitoring
    this.resourceMonitorInterval = setInterval(() => {
      this.updateResourceMetrics();
    }, 15000); // Every 15 seconds
  }
  
  /**
   * Update network topology information
   */
  private async updateNetworkTopology(): Promise<void> {
    try {
      // Prune stale nodes
      this.pruneStaleNodes();
      
      // If we're a coordinator, broadcast our known topology
      if (this.role === NodeRole.COORDINATOR) {
        await this.broadcastTopology();
      }
      
      // If we're a worker, update our coordinator about our status
      if (this.role === NodeRole.WORKER) {
        await this.updateCoordinatorStatus();
      }
    } catch (error) {
      logger.error(`Error updating network topology: ${error}`);
    }
  }
  
  /**
   * Prune stale nodes from our registry
   */
  private pruneStaleNodes(): void {
    const now = Date.now();
    const staleThreshold = 5 * 60 * 1000; // 5 minutes
    
    // Prune stale coordinators
    for (const [id, data] of this.knownCoordinators.entries()) {
      if (now - data.lastSeen > staleThreshold) {
        logger.info(`Removing stale coordinator ${id}`);
        this.knownCoordinators.delete(id);
      }
    }
    
    // Prune stale workers
    for (const [id, data] of this.knownWorkers.entries()) {
      if (now - data.lastSeen > staleThreshold) {
        logger.info(`Removing stale worker ${id}`);
        this.knownWorkers.delete(id);
      }
    }
  }
  
  /**
   * Broadcast our network topology to other nodes
   */
  private async broadcastTopology(): Promise<void> {
    if (this.role !== NodeRole.COORDINATOR) {
      return;
    }
    
    const topology = this.getNetworkTopology();
    
    // Broadcast to all workers
    for (const [id, data] of this.knownWorkers.entries()) {
      if (data.assignedCoordinator === this.nodeId) {
        try {
          const client = new A2AClient(data.url);
          await tryCatch(() => client.callMethod('topology/update', { topology }));
        } catch (error) {
          logger.warn(`Failed to broadcast topology to worker ${id}: ${error}`);
        }
      }
    }
  }
  
  /**
   * Update our status with the coordinator
   */
  private async updateCoordinatorStatus(): Promise<void> {
    if (this.role !== NodeRole.WORKER) {
      return;
    }
    
    // Find our coordinator
    let coordinatorUrl: string | undefined;
    let coordinatorId: string | undefined;
    
    for (const [id, data] of this.knownCoordinators.entries()) {
      // Use the first one for now - could be more sophisticated
      coordinatorUrl = data.url;
      coordinatorId = id;
      break;
    }
    
    if (!coordinatorUrl || !coordinatorId) {
      logger.warn('No coordinator found to update status with');
      return;
    }
    
    try {
      const client = new A2AClient(coordinatorUrl);
      await client.callMethod('node/status', {
        nodeId: this.nodeId,
        status: this.status,
        resources: this.metadata.resources,
        tasks: this.distributedNode ? {
          // This would integrate with the actual distributed node
          pending: 0,
          running: 0,
          completed: 0,
          failed: 0
        } : undefined
      });
    } catch (error) {
      logger.warn(`Failed to update status with coordinator ${coordinatorId}: ${error}`);
    }
  }
  
  /**
   * Get current network topology
   */
  private getNetworkTopology(): NetworkTopology {
    const topology: NetworkTopology = {
      coordinators: new Map(),
      workers: new Map(),
      mesh: new Map()
    };
    
    // Add ourselves
    if (this.role === NodeRole.COORDINATOR) {
      const workerIds: string[] = [];
      
      for (const [id, data] of this.knownWorkers.entries()) {
        if (data.assignedCoordinator === this.nodeId) {
          workerIds.push(id);
        }
      }
      
      topology.coordinators.set(this.nodeId, {
        info: {
          id: this.nodeId,
          role: NodeRole.COORDINATOR,
          status: this.status,
          tasks: {
            pending: 0,
            running: 0,
            completed: 0,
            failed: 0
          },
          capabilities: this.metadata.capabilities,
          lastHeartbeat: Date.now()
        },
        workers: workerIds,
        lastSeen: Date.now()
      });
    } else {
      // Add as worker
      let coordinatorId: string | undefined;
      
      for (const [id, data] of this.knownCoordinators.entries()) {
        // Use the first one for simplicity
        coordinatorId = id;
        break;
      }
      
      topology.workers.set(this.nodeId, {
        info: {
          id: this.nodeId,
          role: NodeRole.WORKER,
          status: this.status,
          tasks: {
            pending: 0,
            running: 0,
            completed: 0,
            failed: 0
          },
          capabilities: this.metadata.capabilities,
          lastHeartbeat: Date.now()
        },
        coordinatorId,
        lastSeen: Date.now()
      });
    }
    
    // Add known coordinators
    for (const [id, data] of this.knownCoordinators.entries()) {
      if (id !== this.nodeId) {
        const workerIds: string[] = [];
        
        // Find workers assigned to this coordinator
        for (const [workerId, workerData] of this.knownWorkers.entries()) {
          if (workerData.assignedCoordinator === id) {
            workerIds.push(workerId);
          }
        }
        
        topology.coordinators.set(id, {
          info: data.nodeInfo || {
            id,
            role: NodeRole.COORDINATOR,
            status: NodeStatus.UNKNOWN,
            tasks: {
              pending: 0,
              running: 0,
              completed: 0,
              failed: 0
            },
            capabilities: [],
            lastHeartbeat: data.lastSeen
          },
          workers: workerIds,
          lastSeen: data.lastSeen
        });
      }
    }
    
    // Add known workers
    for (const [id, data] of this.knownWorkers.entries()) {
      if (id !== this.nodeId) {
        topology.workers.set(id, {
          info: data.nodeInfo || {
            id,
            role: NodeRole.WORKER,
            status: NodeStatus.UNKNOWN,
            tasks: {
              pending: 0,
              running: 0,
              completed: 0,
              failed: 0
            },
            capabilities: [],
            lastHeartbeat: data.lastSeen
          },
          coordinatorId: data.assignedCoordinator,
          lastSeen: data.lastSeen
        });
      }
    }
    
    // Add mesh connections
    if (this.discoveryMode === DiscoveryMode.MESH) {
      // In mesh mode, track connections between all nodes
      const allNodeIds = new Set([
        ...topology.coordinators.keys(),
        ...topology.workers.keys()
      ]);
      
      for (const nodeId of allNodeIds) {
        const connections: string[] = [];
        
        // In mesh mode, all nodes are potentially connected
        // We would need actual connection information here
        
        topology.mesh.set(nodeId, {
          connections,
          lastSeen: Date.now()
        });
      }
    }
    
    return topology;
  }
  
  /**
   * Manage services
   */
  private async manageServices(): Promise<void> {
    try {
      // Update service status
      this.updateServiceStatus();
      
      // If we're a coordinator, manage service node allocation
      if (this.role === NodeRole.COORDINATOR) {
        await this.manageServiceNodeAllocation();
      }
    } catch (error) {
      logger.error(`Error managing services: ${error}`);
    }
  }
  
  /**
   * Update service status based on node health
   */
  private updateServiceStatus(): void {
    for (const [serviceId, entry] of this.services.entries()) {
      // Check if all nodes for this service are healthy
      let nodeCount = 0;
      let healthyNodeCount = 0;
      
      for (const nodeId of entry.nodes) {
        nodeCount++;
        
        // Check if it's us
        if (nodeId === this.nodeId) {
          if (this.status === NodeStatus.READY || this.status === NodeStatus.BUSY) {
            healthyNodeCount++;
          }
          continue;
        }
        
        // Check if it's a known coordinator
        const coordinatorData = this.knownCoordinators.get(nodeId);
        if (coordinatorData) {
          const status = coordinatorData.nodeInfo?.status || NodeStatus.UNKNOWN;
          if (status === NodeStatus.READY || status === NodeStatus.BUSY) {
            healthyNodeCount++;
          }
          continue;
        }
        
        // Check if it's a known worker
        const workerData = this.knownWorkers.get(nodeId);
        if (workerData) {
          const status = workerData.nodeInfo?.status || NodeStatus.UNKNOWN;
          if (status === NodeStatus.READY || status === NodeStatus.BUSY) {
            healthyNodeCount++;
          }
          continue;
        }
      }
      
      // Update service status based on node health
      if (nodeCount === 0) {
        entry.status = 'provisioning';
      } else if (healthyNodeCount === 0) {
        entry.status = 'failed';
      } else if (healthyNodeCount < nodeCount) {
        entry.status = 'degraded';
      } else {
        entry.status = 'ready';
      }
      
      entry.updated = Date.now();
      this.services.set(serviceId, entry);
    }
  }
  
  /**
   * Manage service node allocation
   */
  private async manageServiceNodeAllocation(): Promise<void> {
    if (this.role !== NodeRole.COORDINATOR) {
      return;
    }
    
    for (const [serviceId, entry] of this.services.entries()) {
      // Check if we need to allocate more nodes
      const requirements = entry.service.requirements || {};
      const minNodes = requirements.minNodes || 1;
      const preferredNodes = requirements.preferredNodes || minNodes;
      
      if (entry.nodes.length < minNodes) {
        // We need to allocate more nodes
        await this.allocateNodesForService(serviceId, entry, minNodes - entry.nodes.length);
      } else if (entry.nodes.length < preferredNodes && entry.status === 'ready') {
        // We could use more nodes but not critical
        await this.allocateNodesForService(serviceId, entry, preferredNodes - entry.nodes.length);
      }
    }
  }
  
  /**
   * Allocate nodes for a service
   */
  private async allocateNodesForService(
    serviceId: string,
    entry: ServiceRegistryEntry,
    count: number
  ): Promise<void> {
    if (count <= 0) {
      return;
    }
    
    // Find available nodes that match the requirements
    const availableNodes: string[] = [];
    
    // Check our own node
    if (!entry.nodes.includes(this.nodeId)) {
      if (this.checkNodeMatchesServiceRequirements(entry.service)) {
        availableNodes.push(this.nodeId);
      }
    }
    
    // Check known workers
    for (const [nodeId, data] of this.knownWorkers.entries()) {
      if (!entry.nodes.includes(nodeId)) {
        // Check if this node has the required capabilities
        if (data.nodeInfo) {
          const hasRequiredCapabilities = this.checkNodeCapabilitiesMatchService(
            data.nodeInfo.capabilities || [],
            entry.service
          );
          
          if (hasRequiredCapabilities) {
            availableNodes.push(nodeId);
          }
        }
      }
    }
    
    // Allocate nodes up to the requested count
    const nodesToAllocate = availableNodes.slice(0, count);
    
    for (const nodeId of nodesToAllocate) {
      await this.addNodeToService(serviceId, nodeId);
    }
  }
  
  /**
   * Check if this node matches service requirements
   */
  private checkNodeMatchesServiceRequirements(service: ServiceDefinition): boolean {
    if (!service.requirements?.nodeCapabilities) {
      // No specific capability requirements
      return true;
    }
    
    return this.checkNodeCapabilitiesMatchService(
      this.metadata.capabilities,
      service
    );
  }
  
  /**
   * Check if node capabilities match service requirements
   */
  private checkNodeCapabilitiesMatchService(
    capabilities: string[],
    service: ServiceDefinition
  ): boolean {
    if (!service.requirements?.nodeCapabilities) {
      // No specific capability requirements
      return true;
    }
    
    // Check if node has all required capabilities
    for (const requiredCapability of service.requirements.nodeCapabilities) {
      if (!capabilities.includes(requiredCapability)) {
        return false;
      }
    }
    
    return true;
  }
  
  /**
   * Add a node to a service
   */
  private async addNodeToService(serviceId: string, nodeId: string): Promise<void> {
    const entry = this.services.get(serviceId);
    
    if (!entry) {
      throw new Error(`Service not found: ${serviceId}`);
    }
    
    // If already in the service, do nothing
    if (entry.nodes.includes(nodeId)) {
      return;
    }
    
    // Add to service
    entry.nodes.push(nodeId);
    entry.updated = Date.now();
    this.services.set(serviceId, entry);
    
    // If it's our node, nothing else to do
    if (nodeId === this.nodeId) {
      logger.info(`Added our node to service ${serviceId}`);
      this.emit('joinedService', serviceId, entry.service);
      return;
    }
    
    // For other nodes, notify them
    try {
      let nodeUrl: string | undefined;
      
      // Find node URL
      const workerData = this.knownWorkers.get(nodeId);
      if (workerData) {
        nodeUrl = workerData.url;
      } else {
        const coordinatorData = this.knownCoordinators.get(nodeId);
        if (coordinatorData) {
          nodeUrl = coordinatorData.url;
        }
      }
      
      if (!nodeUrl) {
        throw new Error(`Node URL not found: ${nodeId}`);
      }
      
      // Notify node
      const client = new A2AClient(nodeUrl);
      await client.callMethod('services/join', {
        serviceId,
        service: entry.service
      });
      
      logger.info(`Added node ${nodeId} to service ${serviceId}`);
    } catch (error) {
      // Remove from service on failure
      entry.nodes = entry.nodes.filter(id => id !== nodeId);
      entry.updated = Date.now();
      this.services.set(serviceId, entry);
      
      logger.error(`Failed to add node ${nodeId} to service ${serviceId}: ${error}`);
    }
  }
  
  /**
   * Join a service
   */
  public async joinService(serviceId: string, nodeId?: string): Promise<void> {
    const entry = this.services.get(serviceId);
    
    if (!entry) {
      throw new Error(`Service not found: ${serviceId}`);
    }
    
    const targetNodeId = nodeId || this.nodeId;
    
    // If already in the service, do nothing
    if (entry.nodes.includes(targetNodeId)) {
      return;
    }
    
    // Add to service
    entry.nodes.push(targetNodeId);
    entry.updated = Date.now();
    this.services.set(serviceId, entry);
    
    if (targetNodeId === this.nodeId) {
      logger.info(`Joined service ${serviceId}`);
      this.emit('joinedService', serviceId, entry.service);
    } else {
      logger.info(`Node ${targetNodeId} joined service ${serviceId}`);
    }
  }
  
  /**
   * Register a service
   */
  public async registerService(service: ServiceDefinition): Promise<ServiceRegistryEntry> {
    // Check if service already exists
    if (this.services.has(service.id)) {
      const existingEntry = this.services.get(service.id)!;
      
      // Update service definition
      existingEntry.service = service;
      existingEntry.updated = Date.now();
      
      this.services.set(service.id, existingEntry);
      
      logger.info(`Updated service ${service.id}`);
      
      return existingEntry;
    }
    
    // Create new service entry
    const newEntry: ServiceRegistryEntry = {
      service,
      nodes: [],
      status: 'provisioning',
      created: Date.now(),
      updated: Date.now()
    };
    
    this.services.set(service.id, newEntry);
    
    logger.info(`Registered new service ${service.id}`);
    this.emit('serviceRegistered', service.id, service);
    
    // If we're a coordinator, try to allocate nodes immediately
    if (this.role === NodeRole.COORDINATOR) {
      const requirements = service.requirements || {};
      const minNodes = requirements.minNodes || 1;
      
      await this.allocateNodesForService(service.id, newEntry, minNodes);
    }
    
    return newEntry;
  }
  
  /**
   * Update resource metrics
   */
  private updateResourceMetrics(): void {
    // Update CPU and memory metrics
    const cpuCount = require('os').cpus().length;
    const totalMemory = Math.floor(require('os').totalmem() / (1024 * 1024 * 1024));
    
    this.metadata.resources.cpu = cpuCount;
    this.metadata.resources.memory = totalMemory;
    
    // Recalculate resource score
    this.metadata.resources.score = this.calculateResourceScore();
  }
  
  /**
   * Stop the self-organizing node
   */
  public async stop(): Promise<void> {
    if (!this.isRunning) {
      return;
    }
    
    // Update status
    this.status = NodeStatus.SHUTDOWN;
    
    // Stop periodic tasks
    if (this.topologyInterval) {
      clearInterval(this.topologyInterval);
    }
    
    if (this.serviceManagementInterval) {
      clearInterval(this.serviceManagementInterval);
    }
    
    if (this.resourceMonitorInterval) {
      clearInterval(this.resourceMonitorInterval);
    }
    
    // Stop A2A integration
    if (this.a2aIntegration) {
      this.a2aIntegration.stop();
    }
    
    // Stop distributed node
    if (this.distributedNode) {
      this.distributedNode.stop();
    }
    
    // Stop cluster
    if (this.cluster) {
      this.cluster.stop();
    }
    
    // Stop health monitor
    if (this.healthMonitor) {
      this.healthMonitor.stop();
    }
    
    this.isRunning = false;
    
    logger.info('Self-organizing node stopped');
    this.emit('stopped');
  }
  
  /**
   * Get node ID
   */
  public getNodeId(): string {
    return this.nodeId;
  }
  
  /**
   * Get node role
   */
  public getRole(): NodeRole {
    return this.role;
  }
  
  /**
   * Get node status
   */
  public getStatus(): NodeStatus {
    return this.status;
  }
  
  /**
   * Get known coordinators
   */
  public getKnownCoordinators(): Map<string, {
    url: string;
    card: AgentCard;
    nodeInfo?: NodeInfo;
    lastSeen: number;
    priority: number;
  }> {
    return this.knownCoordinators;
  }
  
  /**
   * Get known workers
   */
  public getKnownWorkers(): Map<string, {
    url: string;
    card: AgentCard;
    nodeInfo?: NodeInfo;
    lastSeen: number;
    assignedCoordinator?: string;
  }> {
    return this.knownWorkers;
  }
  
  /**
   * Get services
   */
  public getServices(): Map<string, ServiceRegistryEntry> {
    return this.services;
  }
  
  /**
   * Get distributed node
   */
  public getDistributedNode(): DistributedNode | undefined {
    return this.distributedNode;
  }
  
  /**
   * Get distributed cluster
   */
  public getCluster(): DistributedCluster | undefined {
    return this.cluster;
  }
}