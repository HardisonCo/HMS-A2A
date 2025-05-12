import { EventEmitter } from 'events';
import { createComponentLogger } from '../../utils/logger';
import { SelfOrganizingNode, ServiceDefinition, ServiceRegistryEntry } from './self_organizing_node';
import { NodeStatus, NodeRole } from './distributed_types';
import { DistributedError, tryCatch } from '../../utils/error_handling';
import { DistributedGeneticEngine } from './distributed_genetic_engine';
import { A2AClient } from './a2a_integration';

const logger = createComponentLogger('service-cluster');

/**
 * Service cluster error
 */
export class ServiceClusterError extends DistributedError {
  constructor(
    message: string,
    options: {
      code?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: options.code || 'SERVICE_CLUSTER_ERROR',
      context: options.context,
      cause: options.cause
    });
  }
}

/**
 * Service cluster state 
 */
export enum ServiceClusterState {
  INITIALIZING = 'initializing',
  PROVISIONING = 'provisioning',
  READY = 'ready',
  DEGRADED = 'degraded',
  FAILED = 'failed',
  SHUTDOWN = 'shutdown'
}

/**
 * Service node entry
 */
export interface ServiceNodeEntry {
  id: string;
  url: string;
  role: NodeRole;
  status: NodeStatus;
  lastSeen: number;
  capabilities: string[];
  joined: number;
}

/**
 * Service cluster for managing a specific genetic algorithm service
 */
export class ServiceCluster extends EventEmitter {
  private serviceDefinition: ServiceDefinition;
  private selfNode: SelfOrganizingNode;
  private state: ServiceClusterState = ServiceClusterState.INITIALIZING;
  private nodes: Map<string, ServiceNodeEntry> = new Map();
  private coordinator?: { id: string; url: string };
  private geneticEngine?: DistributedGeneticEngine;
  private stateCheckInterval?: NodeJS.Timeout;
  private heartbeatInterval?: NodeJS.Timeout;
  private metrics: {
    totalTasks: number;
    completedTasks: number;
    failedTasks: number;
    averageTaskTime: number;
    taskTimes: number[];
  } = {
    totalTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    averageTaskTime: 0,
    taskTimes: []
  };
  
  constructor(
    serviceDefinition: ServiceDefinition,
    selfNode: SelfOrganizingNode,
    geneticEngine?: DistributedGeneticEngine
  ) {
    super();
    this.serviceDefinition = serviceDefinition;
    this.selfNode = selfNode;
    this.geneticEngine = geneticEngine;
    
    // Add self node
    this.addNode({
      id: selfNode.getNodeId(),
      url: '', // Don't need a URL for self
      role: selfNode.getRole(),
      status: selfNode.getStatus(),
      lastSeen: Date.now(),
      capabilities: [], // Will be filled in separately
      joined: Date.now()
    });
    
    // Set up event handlers
    this.setupEventHandlers();
  }
  
  /**
   * Set up event handlers
   */
  private setupEventHandlers(): void {
    // Listen for node status changes from self-organizing node
    this.selfNode.on('coordinatorDiscovered', (id, url) => {
      // If we're looking for a coordinator, check if this one is part of our service
      this.checkAndAddCoordinator(id, url);
    });
    
    this.selfNode.on('workerDiscovered', (id, url) => {
      // If we're a coordinator, check if this worker should be part of our service
      this.checkAndAddWorker(id, url);
    });
    
    this.selfNode.on('joinedService', (serviceId) => {
      // If this is our service, update state
      if (serviceId === this.serviceDefinition.id) {
        this.updateState();
      }
    });
  }
  
  /**
   * Start the service cluster
   */
  public async start(): Promise<void> {
    if (this.state !== ServiceClusterState.INITIALIZING) {
      return;
    }
    
    this.state = ServiceClusterState.PROVISIONING;
    
    // Register the service
    await this.registerService();
    
    // Discover existing nodes in the service
    await this.discoverExistingNodes();
    
    // Start state check interval
    this.stateCheckInterval = setInterval(() => {
      this.updateState();
    }, 30000); // Every 30 seconds
    
    // Start heartbeat interval
    this.heartbeatInterval = setInterval(() => {
      this.sendHeartbeat();
    }, 10000); // Every 10 seconds
    
    logger.info(`Service cluster started for service ${this.serviceDefinition.id}`);
    this.emit('started');
  }
  
  /**
   * Register the service with self-organizing node
   */
  private async registerService(): Promise<void> {
    try {
      await this.selfNode.registerService(this.serviceDefinition);
      logger.info(`Service ${this.serviceDefinition.id} registered`);
    } catch (error) {
      throw new ServiceClusterError('Failed to register service', {
        context: { serviceId: this.serviceDefinition.id },
        cause: error instanceof Error ? error : new Error(String(error))
      });
    }
  }
  
  /**
   * Discover existing nodes in the service
   */
  private async discoverExistingNodes(): Promise<void> {
    try {
      // Get service entry from self node
      const services = this.selfNode.getServices();
      const serviceEntry = services.get(this.serviceDefinition.id);
      
      if (!serviceEntry) {
        logger.warn(`Service ${this.serviceDefinition.id} not found in registry`);
        return;
      }
      
      // Add all nodes in the service
      for (const nodeId of serviceEntry.nodes) {
        if (nodeId === this.selfNode.getNodeId()) {
          // Skip self node, already added
          continue;
        }
        
        // Try to find node info
        const knownCoordinators = this.selfNode.getKnownCoordinators();
        const knownWorkers = this.selfNode.getKnownWorkers();
        
        let url: string | undefined;
        let role: NodeRole | undefined;
        let status: NodeStatus | undefined;
        let capabilities: string[] | undefined;
        
        const coordinatorInfo = knownCoordinators.get(nodeId);
        if (coordinatorInfo) {
          url = coordinatorInfo.url;
          role = NodeRole.COORDINATOR;
          status = coordinatorInfo.nodeInfo?.status || NodeStatus.UNKNOWN;
          capabilities = coordinatorInfo.nodeInfo?.capabilities || [];
        } else {
          const workerInfo = knownWorkers.get(nodeId);
          if (workerInfo) {
            url = workerInfo.url;
            role = NodeRole.WORKER;
            status = workerInfo.nodeInfo?.status || NodeStatus.UNKNOWN;
            capabilities = workerInfo.nodeInfo?.capabilities || [];
          }
        }
        
        if (url && role) {
          this.addNode({
            id: nodeId,
            url,
            role,
            status: status || NodeStatus.UNKNOWN,
            lastSeen: Date.now(),
            capabilities: capabilities || [],
            joined: Date.now()
          });
        }
      }
    } catch (error) {
      logger.error(`Error discovering existing nodes: ${error}`);
    }
  }
  
  /**
   * Check and add a coordinator
   */
  private async checkAndAddCoordinator(id: string, url: string): Promise<void> {
    try {
      // If this node is already part of our service, skip
      if (this.nodes.has(id)) {
        return;
      }
      
      // Check if this coordinator is part of our service
      const client = new A2AClient(url);
      const services = await client.callMethod<{
        services: ServiceRegistryEntry[];
      }>('services/list', {});
      
      const serviceEntry = services.services.find(
        entry => entry.service.id === this.serviceDefinition.id
      );
      
      if (serviceEntry && serviceEntry.nodes.includes(id)) {
        // This coordinator is part of our service
        try {
          const nodeInfo = await client.callMethod<{
            id: string;
            role: NodeRole;
            status: NodeStatus;
            metadata: { capabilities: string[] };
          }>('node/info', {});
          
          this.addNode({
            id,
            url,
            role: NodeRole.COORDINATOR,
            status: nodeInfo.status,
            lastSeen: Date.now(),
            capabilities: nodeInfo.metadata?.capabilities || [],
            joined: Date.now()
          });
          
          logger.info(`Added coordinator ${id} to service ${this.serviceDefinition.id}`);
        } catch (error) {
          logger.warn(`Failed to get node info for coordinator ${id}: ${error}`);
        }
      }
    } catch (error) {
      logger.warn(`Failed to check coordinator ${id}: ${error}`);
    }
  }
  
  /**
   * Check and add a worker
   */
  private async checkAndAddWorker(id: string, url: string): Promise<void> {
    try {
      // If this node is already part of our service, skip
      if (this.nodes.has(id)) {
        return;
      }
      
      // If we're not a coordinator, skip
      if (this.selfNode.getRole() !== NodeRole.COORDINATOR) {
        return;
      }
      
      // Check if this worker has the required capabilities
      const knownWorkers = this.selfNode.getKnownWorkers();
      const workerInfo = knownWorkers.get(id);
      
      if (!workerInfo) {
        return;
      }
      
      const capabilities = workerInfo.nodeInfo?.capabilities || [];
      
      // Check if worker has all required capabilities
      const requiredCapabilities = this.serviceDefinition.requirements?.nodeCapabilities || [];
      
      const hasAllRequired = requiredCapabilities.every(
        required => capabilities.includes(required)
      );
      
      if (hasAllRequired) {
        // This worker has the required capabilities, invite it to join the service
        try {
          const client = new A2AClient(url);
          await client.callMethod('services/join', {
            serviceId: this.serviceDefinition.id,
            service: this.serviceDefinition
          });
          
          this.addNode({
            id,
            url,
            role: NodeRole.WORKER,
            status: workerInfo.nodeInfo?.status || NodeStatus.UNKNOWN,
            lastSeen: Date.now(),
            capabilities,
            joined: Date.now()
          });
          
          logger.info(`Invited worker ${id} to join service ${this.serviceDefinition.id}`);
        } catch (error) {
          logger.warn(`Failed to invite worker ${id}: ${error}`);
        }
      }
    } catch (error) {
      logger.warn(`Failed to check worker ${id}: ${error}`);
    }
  }
  
  /**
   * Add a node to the service
   */
  private addNode(nodeEntry: ServiceNodeEntry): void {
    this.nodes.set(nodeEntry.id, nodeEntry);
    
    // If this is a coordinator, set as our coordinator
    if (nodeEntry.role === NodeRole.COORDINATOR) {
      this.coordinator = {
        id: nodeEntry.id,
        url: nodeEntry.url
      };
    }
    
    this.updateState();
    
    this.emit('nodeAdded', nodeEntry);
    logger.info(`Node ${nodeEntry.id} added to service ${this.serviceDefinition.id}`);
  }
  
  /**
   * Update a node's status
   */
  public updateNodeStatus(nodeId: string, status: NodeStatus): void {
    const nodeEntry = this.nodes.get(nodeId);
    
    if (nodeEntry) {
      nodeEntry.status = status;
      nodeEntry.lastSeen = Date.now();
      this.nodes.set(nodeId, nodeEntry);
      
      this.updateState();
    }
  }
  
  /**
   * Update service state
   */
  private updateState(): void {
    // Prune stale nodes
    this.pruneStaleNodes();
    
    // Count healthy nodes
    let healthyNodes = 0;
    let totalNodes = this.nodes.size;
    let hasHealthyCoordinator = false;
    
    for (const [nodeId, nodeEntry] of this.nodes.entries()) {
      if (nodeEntry.status === NodeStatus.READY || nodeEntry.status === NodeStatus.BUSY) {
        healthyNodes++;
        
        if (nodeEntry.role === NodeRole.COORDINATOR) {
          hasHealthyCoordinator = true;
        }
      }
    }
    
    // Update state based on node health
    const oldState = this.state;
    
    if (totalNodes === 0) {
      this.state = ServiceClusterState.PROVISIONING;
    } else if (healthyNodes === 0) {
      this.state = ServiceClusterState.FAILED;
    } else if (!hasHealthyCoordinator) {
      this.state = ServiceClusterState.DEGRADED;
    } else if (healthyNodes < totalNodes) {
      this.state = ServiceClusterState.DEGRADED;
    } else {
      this.state = ServiceClusterState.READY;
    }
    
    // Check if state changed
    if (oldState !== this.state) {
      logger.info(`Service ${this.serviceDefinition.id} state changed from ${oldState} to ${this.state}`);
      this.emit('stateChanged', oldState, this.state);
    }
  }
  
  /**
   * Prune stale nodes
   */
  private pruneStaleNodes(): void {
    const now = Date.now();
    const staleThreshold = 2 * 60 * 1000; // 2 minutes
    
    const staleNodeIds: string[] = [];
    
    for (const [nodeId, nodeEntry] of this.nodes.entries()) {
      if (nodeId === this.selfNode.getNodeId()) {
        // Don't prune self node
        continue;
      }
      
      if (now - nodeEntry.lastSeen > staleThreshold) {
        staleNodeIds.push(nodeId);
      }
    }
    
    for (const nodeId of staleNodeIds) {
      this.nodes.delete(nodeId);
      
      // If this was our coordinator, clear it
      if (this.coordinator && this.coordinator.id === nodeId) {
        this.coordinator = undefined;
      }
      
      this.emit('nodeRemoved', nodeId);
      logger.info(`Removed stale node ${nodeId} from service ${this.serviceDefinition.id}`);
    }
  }
  
  /**
   * Send heartbeat to other nodes
   */
  private async sendHeartbeat(): Promise<void> {
    try {
      // Update our own status
      this.updateNodeStatus(this.selfNode.getNodeId(), this.selfNode.getStatus());
      
      // If we're a coordinator, send heartbeat to all workers
      if (this.selfNode.getRole() === NodeRole.COORDINATOR) {
        const workerNodes = Array.from(this.nodes.values())
          .filter(node => node.role === NodeRole.WORKER && node.id !== this.selfNode.getNodeId());
        
        for (const workerNode of workerNodes) {
          await tryCatch(async () => {
            const client = new A2AClient(workerNode.url);
            await client.callMethod('service/heartbeat', {
              serviceId: this.serviceDefinition.id,
              coordinatorId: this.selfNode.getNodeId(),
              state: this.state
            });
            
            // Update last seen
            workerNode.lastSeen = Date.now();
          });
        }
      }
      
      // If we're a worker, send heartbeat to coordinator
      if (this.selfNode.getRole() === NodeRole.WORKER && this.coordinator) {
        await tryCatch(async () => {
          const client = new A2AClient(this.coordinator!.url);
          await client.callMethod('service/heartbeat', {
            serviceId: this.serviceDefinition.id,
            workerId: this.selfNode.getNodeId(),
            state: this.state
          });
        });
      }
    } catch (error) {
      logger.warn(`Error sending heartbeat: ${error}`);
    }
  }
  
  /**
   * Record task metrics
   */
  public recordTaskMetrics(
    taskId: string,
    metrics: {
      completed: boolean;
      durationMs: number;
    }
  ): void {
    this.metrics.totalTasks++;
    
    if (metrics.completed) {
      this.metrics.completedTasks++;
    } else {
      this.metrics.failedTasks++;
    }
    
    this.metrics.taskTimes.push(metrics.durationMs);
    
    // Keep only the last 100 task times
    if (this.metrics.taskTimes.length > 100) {
      this.metrics.taskTimes = this.metrics.taskTimes.slice(-100);
    }
    
    // Recalculate average
    this.metrics.averageTaskTime = this.metrics.taskTimes.reduce((a, b) => a + b, 0) / this.metrics.taskTimes.length;
  }
  
  /**
   * Get service metrics
   */
  public getMetrics(): any {
    return {
      serviceId: this.serviceDefinition.id,
      serviceName: this.serviceDefinition.name,
      state: this.state,
      nodes: {
        total: this.nodes.size,
        coordinators: Array.from(this.nodes.values()).filter(node => node.role === NodeRole.COORDINATOR).length,
        workers: Array.from(this.nodes.values()).filter(node => node.role === NodeRole.WORKER).length
      },
      tasks: {
        total: this.metrics.totalTasks,
        completed: this.metrics.completedTasks,
        failed: this.metrics.failedTasks,
        successRate: this.metrics.totalTasks > 0 ? this.metrics.completedTasks / this.metrics.totalTasks : 0
      },
      performance: {
        averageTaskTimeMs: this.metrics.averageTaskTime,
        recentTaskTimes: this.metrics.taskTimes.slice(-10)
      }
    };
  }
  
  /**
   * Get service state
   */
  public getState(): ServiceClusterState {
    return this.state;
  }
  
  /**
   * Get service nodes
   */
  public getNodes(): Map<string, ServiceNodeEntry> {
    return this.nodes;
  }
  
  /**
   * Stop the service cluster
   */
  public async stop(): Promise<void> {
    // Stop intervals
    if (this.stateCheckInterval) {
      clearInterval(this.stateCheckInterval);
    }
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    // Set state to shutdown
    this.state = ServiceClusterState.SHUTDOWN;
    
    // Notify other nodes
    try {
      await this.sendShutdownNotification();
    } catch (error) {
      logger.warn(`Error sending shutdown notification: ${error}`);
    }
    
    logger.info(`Service cluster stopped for service ${this.serviceDefinition.id}`);
    this.emit('stopped');
  }
  
  /**
   * Send shutdown notification to other nodes
   */
  private async sendShutdownNotification(): Promise<void> {
    // Notify all nodes except self
    const otherNodes = Array.from(this.nodes.values())
      .filter(node => node.id !== this.selfNode.getNodeId());
    
    for (const node of otherNodes) {
      await tryCatch(async () => {
        const client = new A2AClient(node.url);
        await client.callMethod('service/shutdown', {
          serviceId: this.serviceDefinition.id,
          nodeId: this.selfNode.getNodeId()
        });
      });
    }
  }
}