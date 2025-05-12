import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { EventEmitter } from 'events';
import { createComponentLogger } from '../../utils/logger';
import { DistributedError, retry } from '../../utils/error_handling';
import { NodeRole, NodeStatus, NodeInfo } from './distributed_types';

const logger = createComponentLogger('a2a-integration');

/**
 * A2A integration error
 */
export class A2AIntegrationError extends DistributedError {
  constructor(
    message: string,
    options: {
      endpoint?: string;
      method?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: 'A2A_INTEGRATION_ERROR',
      context: {
        endpoint: options.endpoint,
        method: options.method,
        ...options.context
      },
      cause: options.cause
    });
  }
}

/**
 * Interface for agent card capabilities
 */
export interface Capability {
  name: string;
  description?: string;
  tags: string[];
  version?: string;
}

/**
 * Interface for A2A agent card
 */
export interface AgentCard {
  name: string;
  version: string;
  description?: string;
  capabilities: Capability[];
  endpoints: {
    [key: string]: string;
  };
  authentication?: {
    type: string;
    [key: string]: any;
  };
}

/**
 * A2A client for communicating with HMS-A2A agents
 */
export class A2AClient {
  private baseUrl: string;
  private timeout: number;
  private authToken?: string;

  constructor(baseUrl: string, timeout: number = 30000, authToken?: string) {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
    this.timeout = timeout;
    this.authToken = authToken;
  }

  /**
   * Get the agent card to discover capabilities
   */
  public async getAgentCard(): Promise<AgentCard> {
    try {
      // First try the well-known endpoint
      try {
        const response = await axios.get(`${this.baseUrl}.well-known/agent.json`, {
          timeout: this.timeout,
          headers: this.getAuthHeaders()
        });
        return response.data;
      } catch (error) {
        // Fall back to the agent-card endpoint
        const response = await axios.get(`${this.baseUrl}agent-card`, {
          timeout: this.timeout,
          headers: this.getAuthHeaders()
        });
        return response.data;
      }
    } catch (error) {
      throw new A2AIntegrationError('Failed to get agent card', {
        endpoint: this.baseUrl,
        cause: error instanceof Error ? error : new Error(String(error))
      });
    }
  }

  /**
   * Call an agent method using JSON-RPC
   */
  public async callMethod<T = any>(method: string, params: any): Promise<T> {
    try {
      const requestId = uuidv4();
      const request = {
        jsonrpc: '2.0',
        id: requestId,
        method,
        params
      };

      const response = await axios.post(this.baseUrl, request, {
        timeout: this.timeout,
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders()
        }
      });

      const result = response.data;

      if (result.error) {
        throw new A2AIntegrationError(result.error.message, {
          endpoint: this.baseUrl,
          method,
          context: {
            code: result.error.code,
            data: result.error.data
          }
        });
      }

      return result.result;
    } catch (error) {
      if (error instanceof A2AIntegrationError) {
        throw error;
      }
      
      throw new A2AIntegrationError(`Failed to call method ${method}`, {
        endpoint: this.baseUrl,
        method,
        cause: error instanceof Error ? error : new Error(String(error))
      });
    }
  }

  /**
   * Subscribe to an agent's server-sent events
   */
  public subscribeToEvents(method: string, params: any, onEvent: (data: any) => void, onError?: (error: Error) => void): () => void {
    const requestId = uuidv4();
    const request = {
      jsonrpc: '2.0',
      id: requestId,
      method: `${method}Subscribe`,
      params
    };

    const source = new EventSource(`${this.baseUrl}sse?request=${encodeURIComponent(JSON.stringify(request))}`);

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent(data.result);
      } catch (error) {
        if (onError) {
          onError(error instanceof Error ? error : new Error(String(error)));
        } else {
          logger.error(`Error processing SSE event: ${error}`);
        }
      }
    };

    source.onerror = (error) => {
      if (onError) {
        onError(new A2AIntegrationError('SSE connection error', {
          endpoint: this.baseUrl,
          method,
          cause: error instanceof Error ? error : new Error('SSE connection failed')
        }));
      } else {
        logger.error(`SSE connection error: ${error}`);
      }
    };

    // Return a function to close the connection
    return () => {
      source.close();
    };
  }

  /**
   * Register a webhook for notifications
   */
  public async registerWebhook(webhookUrl: string, events: string[]): Promise<string> {
    return this.callMethod<string>('notifications/register', {
      url: webhookUrl,
      events
    });
  }

  /**
   * Get authentication headers
   */
  private getAuthHeaders(): Record<string, string> {
    if (this.authToken) {
      return {
        'Authorization': `Bearer ${this.authToken}`
      };
    }
    return {};
  }
}

/**
 * Registry for tracking discovered A2A agents
 */
export class A2AAgentRegistry extends EventEmitter {
  private agents: Map<string, {
    url: string;
    card: AgentCard;
    lastSeen: number;
  }> = new Map();
  
  /**
   * Register a discovered agent
   */
  public registerAgent(agentUrl: string, card: AgentCard): void {
    const agentId = this.getAgentId(agentUrl);
    
    // Check if this is a new agent or an update
    const isNew = !this.agents.has(agentId);
    
    this.agents.set(agentId, {
      url: agentUrl,
      card,
      lastSeen: Date.now()
    });
    
    if (isNew) {
      this.emit('agentDiscovered', agentId, agentUrl, card);
      logger.info(`Discovered new A2A agent: ${card.name} at ${agentUrl}`);
    } else {
      this.emit('agentUpdated', agentId, agentUrl, card);
      logger.debug(`Updated A2A agent info: ${card.name} at ${agentUrl}`);
    }
  }
  
  /**
   * Remove an agent from the registry
   */
  public removeAgent(agentUrl: string): void {
    const agentId = this.getAgentId(agentUrl);
    
    if (this.agents.has(agentId)) {
      const agent = this.agents.get(agentId)!;
      this.agents.delete(agentId);
      
      this.emit('agentRemoved', agentId, agent.url, agent.card);
      logger.info(`Removed A2A agent: ${agent.card.name} at ${agent.url}`);
    }
  }
  
  /**
   * Get all registered agents
   */
  public getAllAgents(): Map<string, { url: string; card: AgentCard; lastSeen: number }> {
    return new Map(this.agents);
  }
  
  /**
   * Find agents by capability
   */
  public findAgentsByCapability(capabilityName: string, tag?: string): Array<{ 
    id: string; 
    url: string; 
    card: AgentCard; 
    capability: Capability;
    lastSeen: number;
  }> {
    const results: Array<{ 
      id: string; 
      url: string; 
      card: AgentCard; 
      capability: Capability;
      lastSeen: number;
    }> = [];
    
    this.agents.forEach((agent, agentId) => {
      agent.card.capabilities.forEach(capability => {
        if (capability.name === capabilityName || 
            capability.tags.includes(capabilityName)) {
          
          // Check for optional tag filter
          if (tag && !capability.tags.includes(tag)) {
            return;
          }
          
          results.push({
            id: agentId,
            url: agent.url,
            card: agent.card,
            capability,
            lastSeen: agent.lastSeen
          });
        }
      });
    });
    
    return results;
  }
  
  /**
   * Generate a consistent ID for an agent based on its URL
   */
  private getAgentId(url: string): string {
    // Normalize the URL by removing trailing slashes
    return url.replace(/\/$/, '');
  }
  
  /**
   * Prune agents that haven't been seen recently
   */
  public pruneStaleAgents(maxAgeSecs: number = 300): void {
    const now = Date.now();
    const staleThreshold = now - (maxAgeSecs * 1000);
    
    const staleAgents: string[] = [];
    
    this.agents.forEach((agent, agentId) => {
      if (agent.lastSeen < staleThreshold) {
        staleAgents.push(agentId);
      }
    });
    
    staleAgents.forEach(agentId => {
      const agent = this.agents.get(agentId)!;
      this.agents.delete(agentId);
      
      this.emit('agentStale', agentId, agent.url, agent.card);
      logger.info(`Removed stale A2A agent: ${agent.card.name} at ${agent.url}`);
    });
  }
}

/**
 * Discovery service for finding A2A agents and registering our service
 */
export class A2ADiscoveryService extends EventEmitter {
  private registry: A2AAgentRegistry;
  private discoveryEndpoints: string[] = [];
  private pruneInterval?: NodeJS.Timeout;
  private discoveryInterval?: NodeJS.Timeout;
  private ourAgentCard?: AgentCard;
  private ourWebhookUrl?: string;
  
  constructor(
    registry: A2AAgentRegistry,
    initialEndpoints: string[] = [],
    pruneIntervalSecs: number = 300
  ) {
    super();
    this.registry = registry;
    this.discoveryEndpoints = [...initialEndpoints];
    
    // Start the prune interval
    this.pruneInterval = setInterval(() => {
      this.registry.pruneStaleAgents(pruneIntervalSecs);
    }, pruneIntervalSecs * 1000);
  }
  
  /**
   * Start discovery process
   */
  public async startDiscovery(intervalSecs: number = 60): Promise<void> {
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
    }
    
    // Do initial discovery
    await this.discoverAgents();
    
    // Set up regular discovery
    this.discoveryInterval = setInterval(() => {
      this.discoverAgents().catch(error => {
        logger.error(`Error during agent discovery: ${error}`);
      });
    }, intervalSecs * 1000);
    
    logger.info(`Started A2A discovery with ${this.discoveryEndpoints.length} endpoints`);
  }
  
  /**
   * Stop discovery process
   */
  public stopDiscovery(): void {
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
      this.discoveryInterval = undefined;
    }
    
    if (this.pruneInterval) {
      clearInterval(this.pruneInterval);
      this.pruneInterval = undefined;
    }
    
    logger.info('Stopped A2A discovery');
  }
  
  /**
   * Add a discovery endpoint
   */
  public addDiscoveryEndpoint(endpoint: string): void {
    if (!this.discoveryEndpoints.includes(endpoint)) {
      this.discoveryEndpoints.push(endpoint);
      // Trigger immediate discovery for this endpoint
      this.discoverAgentAtEndpoint(endpoint).catch(error => {
        logger.warn(`Failed to discover agent at ${endpoint}: ${error}`);
      });
    }
  }
  
  /**
   * Register our service as an A2A agent
   */
  public registerOurService(
    serviceInfo: {
      name: string;
      version: string;
      description?: string;
      capabilities: Capability[];
      endpoints: { [key: string]: string };
      authentication?: { type: string; [key: string]: any };
    },
    webhookUrl?: string
  ): void {
    this.ourAgentCard = serviceInfo;
    this.ourWebhookUrl = webhookUrl;
    
    logger.info(`Registered our service as A2A agent: ${serviceInfo.name}`);
  }
  
  /**
   * Discover agents at known endpoints
   */
  private async discoverAgents(): Promise<void> {
    const discoveryPromises = this.discoveryEndpoints.map(endpoint => 
      this.discoverAgentAtEndpoint(endpoint)
    );
    
    // Wait for all discoveries to complete (successful or not)
    await Promise.allSettled(discoveryPromises);
    
    this.emit('discoveryComplete');
  }
  
  /**
   * Discover and register an agent at a specific endpoint
   */
  private async discoverAgentAtEndpoint(endpoint: string): Promise<void> {
    try {
      const client = new A2AClient(endpoint);
      
      // Retry getting the agent card a few times in case of temporary failures
      const agentCard = await retry(
        () => client.getAgentCard(),
        {
          maxRetries: 3,
          initialDelay: 1000
        }
      );
      
      // Register the agent
      this.registry.registerAgent(endpoint, agentCard);
      
      // If we have a service registered and the agent supports notifications,
      // register our webhook if we haven't already
      if (this.ourAgentCard && this.ourWebhookUrl && 
          agentCard.capabilities.some(cap => cap.name === 'notifications')) {
        try {
          // Register for agent discovery events
          await client.registerWebhook(this.ourWebhookUrl, ['agent.discovered']);
          logger.debug(`Registered webhook with ${agentCard.name} at ${endpoint}`);
        } catch (error) {
          logger.warn(`Failed to register webhook with ${agentCard.name}: ${error}`);
        }
        
        // Register our agent with this endpoint's registry
        try {
          await client.callMethod('discovery/register', {
            agent: this.ourAgentCard
          });
          logger.debug(`Registered our service with ${agentCard.name}`);
        } catch (error) {
          logger.warn(`Failed to register with ${agentCard.name}: ${error}`);
        }
      }
      
      // Check if this agent has discovery capabilities
      if (agentCard.capabilities.some(cap => cap.name === 'discovery')) {
        try {
          // Get other agents this one knows about
          const knownAgents = await client.callMethod<{
            agents: { url: string; card: AgentCard }[]
          }>('discovery/list', {});
          
          // Process each known agent
          knownAgents.agents.forEach(agent => {
            // Avoid adding ourselves
            if (this.ourAgentCard && agent.card.name === this.ourAgentCard.name) {
              return;
            }
            
            // Add to our registry
            this.registry.registerAgent(agent.url, agent.card);
            
            // Add as a discovery endpoint if it supports discovery
            if (agent.card.capabilities.some(cap => cap.name === 'discovery')) {
              this.addDiscoveryEndpoint(agent.url);
            }
          });
        } catch (error) {
          logger.warn(`Failed to list agents from ${agentCard.name}: ${error}`);
        }
      }
    } catch (error) {
      // Just log the error and continue with other endpoints
      logger.warn(`Failed to discover agent at ${endpoint}: ${error}`);
    }
  }
}

/**
 * Service registry for MCP tools integration
 */
export class MCPToolsRegistry {
  private tools: Map<string, {
    name: string;
    description: string;
    domains: string[];
    parameters: any;
    handler: (params: any) => Promise<any>;
  }> = new Map();
  
  /**
   * Register a tool
   */
  public registerTool(
    name: string,
    description: string,
    domains: string[],
    parameters: any,
    handler: (params: any) => Promise<any>
  ): void {
    this.tools.set(name, {
      name,
      description,
      domains,
      parameters,
      handler
    });
    
    logger.info(`Registered MCP tool: ${name} for domains ${domains.join(', ')}`);
  }
  
  /**
   * Get all tools for a domain
   */
  public getToolsForDomain(domain: string): Array<{
    name: string;
    description: string;
    domains: string[];
    parameters: any;
  }> {
    const domainTools: Array<{
      name: string;
      description: string;
      domains: string[];
      parameters: any;
    }> = [];
    
    this.tools.forEach(tool => {
      if (tool.domains.includes('*') || tool.domains.includes(domain)) {
        domainTools.push({
          name: tool.name,
          description: tool.description,
          domains: tool.domains,
          parameters: tool.parameters
        });
      }
    });
    
    return domainTools;
  }
  
  /**
   * Execute a tool
   */
  public async executeTool(name: string, params: any): Promise<any> {
    const tool = this.tools.get(name);
    
    if (!tool) {
      throw new Error(`Tool not found: ${name}`);
    }
    
    return tool.handler(params);
  }
}

/**
 * Self-organizing distributed node integration with A2A ecosystem
 */
export class A2ADistributedNodeIntegration extends EventEmitter {
  private nodeId: string;
  private nodeRole: NodeRole;
  private nodeStatus: NodeStatus;
  private registry: A2AAgentRegistry;
  private discovery: A2ADiscoveryService;
  private toolsRegistry: MCPToolsRegistry;
  private httpServer?: any; // Express or other HTTP server
  private httpPort: number;
  private baseUrl: string;
  
  constructor(
    nodeId: string,
    nodeRole: NodeRole,
    nodeStatus: NodeStatus,
    httpPort: number = 8080,
    baseUrl?: string,
    initialEndpoints: string[] = []
  ) {
    super();
    this.nodeId = nodeId;
    this.nodeRole = nodeRole;
    this.nodeStatus = nodeStatus;
    this.httpPort = httpPort;
    this.baseUrl = baseUrl || `http://localhost:${httpPort}/`;
    
    // Initialize registries
    this.registry = new A2AAgentRegistry();
    this.toolsRegistry = new MCPToolsRegistry();
    this.discovery = new A2ADiscoveryService(this.registry, initialEndpoints);
    
    // Set up event handlers
    this.setupEventHandlers();
  }
  
  /**
   * Set up event handlers for agent discovery
   */
  private setupEventHandlers(): void {
    this.registry.on('agentDiscovered', (agentId, url, card) => {
      this.emit('agentDiscovered', agentId, url, card);
      
      // Check if this is a distributed node service
      if (card.capabilities.some(cap => 
          cap.name === 'genetic-computation' || 
          cap.tags.includes('genetic-algorithm'))) {
        this.emit('geneticServiceDiscovered', agentId, url, card);
      }
    });
    
    this.registry.on('agentRemoved', (agentId, url, card) => {
      this.emit('agentRemoved', agentId, url, card);
      
      if (card.capabilities.some(cap => 
          cap.name === 'genetic-computation' || 
          cap.tags.includes('genetic-algorithm'))) {
        this.emit('geneticServiceRemoved', agentId, url, card);
      }
    });
  }
  
  /**
   * Start the integration
   */
  public async start(httpServer?: any): Promise<void> {
    this.httpServer = httpServer;
    
    // Register our service as an A2A agent
    this.discovery.registerOurService({
      name: `distributed-genetic-${this.nodeRole.toLowerCase()}-${this.nodeId}`,
      version: '1.0.0',
      description: `Distributed genetic algorithm ${this.nodeRole.toLowerCase()} node`,
      capabilities: this.getNodeCapabilities(),
      endpoints: {
        jsonrpc: `${this.baseUrl}`,
        sse: `${this.baseUrl}sse`
      }
    }, `${this.baseUrl}webhook`);
    
    // Register MCP tools
    this.registerMCPTools();
    
    // Start discovery
    await this.discovery.startDiscovery();
    
    logger.info(`Started A2A integration for node ${this.nodeId} (${this.nodeRole})`);
  }
  
  /**
   * Stop the integration
   */
  public stop(): void {
    this.discovery.stopDiscovery();
    logger.info(`Stopped A2A integration for node ${this.nodeId}`);
  }
  
  /**
   * Update node status
   */
  public updateNodeStatus(status: NodeStatus): void {
    this.nodeStatus = status;
  }
  
  /**
   * Get node capabilities based on role and status
   */
  private getNodeCapabilities(): Capability[] {
    const capabilities: Capability[] = [{
      name: 'genetic-computation',
      description: 'Distributed genetic algorithm computation',
      tags: ['genetic-algorithm', 'distributed-computing', this.nodeRole.toLowerCase()]
    }];
    
    if (this.nodeRole === NodeRole.COORDINATOR) {
      capabilities.push({
        name: 'task-distribution',
        description: 'Genetic algorithm task distribution',
        tags: ['task-queue', 'workload-distribution']
      });
      
      capabilities.push({
        name: 'node-management',
        description: 'Distributed node management',
        tags: ['node-registration', 'health-monitoring']
      });
    }
    
    if (this.nodeRole === NodeRole.WORKER) {
      capabilities.push({
        name: 'fitness-evaluation',
        description: 'Genetic algorithm fitness evaluation',
        tags: ['population-evaluation', 'parallel-processing']
      });
    }
    
    capabilities.push({
      name: 'discovery',
      description: 'Service discovery',
      tags: ['a2a-discovery']
    });
    
    return capabilities;
  }
  
  /**
   * Register MCP tools for this node
   */
  private registerMCPTools(): void {
    // Register discovery tool
    this.toolsRegistry.registerTool(
      'discoverGeneticServices',
      'Discover available genetic computation services',
      ['genetic', 'discovery', '*'],
      {
        type: 'object',
        properties: {}
      },
      async () => {
        const services = this.registry.findAgentsByCapability('genetic-computation');
        
        return {
          services: services.map(service => ({
            id: service.id,
            name: service.card.name,
            url: service.url,
            role: service.capability.tags.includes('coordinator') ? 'coordinator' : 'worker',
            lastSeen: service.lastSeen
          }))
        };
      }
    );
    
    // Register node information tool
    this.toolsRegistry.registerTool(
      'getNodeInfo',
      'Get information about this node',
      ['genetic', 'status', '*'],
      {
        type: 'object',
        properties: {}
      },
      async () => {
        return {
          id: this.nodeId,
          role: this.nodeRole,
          status: this.nodeStatus,
          baseUrl: this.baseUrl
        };
      }
    );
    
    // Additional tools based on node role
    if (this.nodeRole === NodeRole.COORDINATOR) {
      this.toolsRegistry.registerTool(
        'getClusterStatus',
        'Get status of the distributed cluster',
        ['genetic', 'status', '*'],
        {
          type: 'object',
          properties: {}
        },
        async () => {
          // This would be implemented to connect to the actual node
          return {
            nodeCount: 0, // To be implemented
            taskCount: 0, // To be implemented
            status: 'unknown' // To be implemented
          };
        }
      );
    }
  }
  
  /**
   * Get genetic computation services discovered in the network
   */
  public getGeneticServices(): Array<{ 
    id: string; 
    url: string; 
    card: AgentCard; 
    capability: Capability;
    lastSeen: number;
  }> {
    return this.registry.findAgentsByCapability('genetic-computation');
  }
  
  /**
   * Find coordinator nodes
   */
  public findCoordinatorNodes(): Array<{ 
    id: string; 
    url: string; 
    card: AgentCard; 
    capability: Capability;
    lastSeen: number;
  }> {
    return this.registry.findAgentsByCapability('genetic-computation', 'coordinator');
  }
  
  /**
   * Find worker nodes
   */
  public findWorkerNodes(): Array<{ 
    id: string; 
    url: string; 
    card: AgentCard; 
    capability: Capability;
    lastSeen: number;
  }> {
    return this.registry.findAgentsByCapability('genetic-computation', 'worker');
  }
  
  /**
   * Create an A2A client for a specific service
   */
  public createClientForService(serviceId: string): A2AClient | null {
    const services = this.getGeneticServices();
    const service = services.find(s => s.id === serviceId);
    
    if (!service) {
      return null;
    }
    
    return new A2AClient(service.url);
  }
  
  /**
   * Convert node info to A2A agent card
   */
  public static nodeInfoToAgentCard(nodeInfo: NodeInfo, baseUrl: string): AgentCard {
    const capabilities: Capability[] = [{
      name: 'genetic-computation',
      description: 'Distributed genetic algorithm computation',
      tags: ['genetic-algorithm', 'distributed-computing', nodeInfo.role.toLowerCase()]
    }];
    
    if (nodeInfo.role === NodeRole.COORDINATOR) {
      capabilities.push({
        name: 'task-distribution',
        description: 'Genetic algorithm task distribution',
        tags: ['task-queue', 'workload-distribution']
      });
      
      capabilities.push({
        name: 'node-management',
        description: 'Distributed node management',
        tags: ['node-registration', 'health-monitoring']
      });
    }
    
    if (nodeInfo.role === NodeRole.WORKER) {
      capabilities.push({
        name: 'fitness-evaluation',
        description: 'Genetic algorithm fitness evaluation',
        tags: ['population-evaluation', 'parallel-processing']
      });
    }
    
    // Add capabilities based on node capabilities
    if (nodeInfo.capabilities) {
      if (nodeInfo.capabilities.includes('advanced-genetic')) {
        capabilities.push({
          name: 'advanced-genetic-operators',
          description: 'Advanced genetic algorithm operators',
          tags: ['advanced-selection', 'advanced-crossover', 'advanced-mutation']
        });
      }
    }
    
    return {
      name: `distributed-genetic-${nodeInfo.role.toLowerCase()}-${nodeInfo.id}`,
      version: '1.0.0',
      description: `Distributed genetic algorithm ${nodeInfo.role.toLowerCase()} node`,
      capabilities,
      endpoints: {
        jsonrpc: baseUrl,
        sse: `${baseUrl}sse`
      }
    };
  }
}