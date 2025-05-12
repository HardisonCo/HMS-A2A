import { EventEmitter } from 'events';
import WebSocket from 'ws';
import { v4 as uuidv4 } from 'uuid';
import { 
  NodeRole, 
  NodeStatus, 
  TaskType, 
  DistributedTask, 
  NodeInfo,
  Message,
  MessageType,
  TaskResponse
} from './distributed_types';
import { TaskQueue } from './task_queue';
import { GeneticRepairEngine } from '../genetic_repair_engine';
import { AdvancedGeneticRepairEngine } from '../advanced/advanced_genetic_repair_engine';
import { logger } from '../../utils/logger';
import { Chromosome } from '../chromosome';
import { FitnessFunction } from '../types';

/**
 * DistributedNode class for genetic algorithm distributed computing
 * 
 * Can function as coordinator (master) or worker node in a distributed cluster
 * Handles node discovery, task distribution, and result collection
 */
export class DistributedNode extends EventEmitter {
  private id: string;
  private role: NodeRole;
  private status: NodeStatus = NodeStatus.INITIALIZING;
  private taskQueue: TaskQueue;
  private server?: WebSocket.Server;
  private clients: Map<string, WebSocket> = new Map();
  private coordinatorConnection?: WebSocket;
  private nodeInfo: Map<string, NodeInfo> = new Map();
  private geneticEngine?: GeneticRepairEngine | AdvancedGeneticRepairEngine;
  private heartbeatInterval?: NodeJS.Timeout;
  private reconnectTimeout?: NodeJS.Timeout;
  private discoveryBroadcastInterval?: NodeJS.Timeout;

  constructor(
    role: NodeRole = NodeRole.WORKER,
    port: number = 0,
    coordinatorUrl?: string,
    geneticEngine?: GeneticRepairEngine | AdvancedGeneticRepairEngine
  ) {
    super();
    this.id = uuidv4();
    this.role = role;
    this.taskQueue = new TaskQueue();
    this.geneticEngine = geneticEngine;

    if (this.role === NodeRole.COORDINATOR) {
      // Coordinator setup
      this.setupCoordinator(port);
    } else if (coordinatorUrl) {
      // Worker setup
      this.connectToCoordinator(coordinatorUrl);
    } else {
      throw new Error('Worker nodes must provide a coordinator URL');
    }

    // Set up task queue event handlers
    this.setupTaskQueueHandlers();
    
    // Set self node info
    this.nodeInfo.set(this.id, {
      id: this.id,
      role: this.role,
      status: this.status,
      tasks: {
        pending: 0,
        running: 0,
        completed: 0,
        failed: 0
      },
      capabilities: this.getNodeCapabilities(),
      lastHeartbeat: Date.now()
    });

    // Start heartbeat for either role
    this.startHeartbeat();
    
    // Set status to ready
    this.status = NodeStatus.READY;
    this.emit('ready', this.id);
    logger.info(`Node ${this.id} (${this.role}) is ready`);
  }

  /**
   * Get this node's ID
   */
  public getId(): string {
    return this.id;
  }

  /**
   * Get this node's role
   */
  public getRole(): NodeRole {
    return this.role;
  }

  /**
   * Get this node's current status
   */
  public getStatus(): NodeStatus {
    return this.status;
  }

  /**
   * Get information about all known nodes
   */
  public getNodes(): Map<string, NodeInfo> {
    return this.nodeInfo;
  }

  /**
   * Set up coordinator server and handlers
   */
  private setupCoordinator(port: number): void {
    this.server = new WebSocket.Server({ port });
    
    this.server.on('connection', (socket: WebSocket) => {
      let clientId: string | null = null;
      
      socket.on('message', (data: WebSocket.Data) => {
        try {
          const message = JSON.parse(data.toString()) as Message;
          
          if (message.type === MessageType.REGISTER) {
            clientId = message.senderId;
            this.clients.set(clientId, socket);
            this.nodeInfo.set(clientId, message.payload as NodeInfo);
            
            // Send acknowledgment
            this.sendMessage(socket, {
              type: MessageType.REGISTER_ACK,
              senderId: this.id,
              timestamp: Date.now(),
              payload: {
                id: clientId,
                coordinatorId: this.id
              }
            });
            
            // Broadcast updated node list to all clients
            this.broadcastNodeList();
            
            logger.info(`Node ${clientId} registered as ${(message.payload as NodeInfo).role}`);
          } else if (message.type === MessageType.HEARTBEAT) {
            if (clientId) {
              const nodeInfo = this.nodeInfo.get(clientId);
              if (nodeInfo) {
                nodeInfo.lastHeartbeat = Date.now();
                nodeInfo.status = (message.payload as NodeInfo).status;
                nodeInfo.tasks = (message.payload as NodeInfo).tasks;
                this.nodeInfo.set(clientId, nodeInfo);
              }
            }
          } else if (message.type === MessageType.TASK_RESULT) {
            const taskResult = message.payload as TaskResponse<any>;
            this.taskQueue.completeTask(taskResult.taskId, taskResult.result);
            logger.debug(`Received task result for ${taskResult.taskId} from ${clientId}`);
          } else if (message.type === MessageType.TASK_FAILED) {
            const taskResult = message.payload as TaskResponse<any>;
            this.taskQueue.failTask(taskResult.taskId, taskResult.error);
            logger.error(`Task ${taskResult.taskId} failed on ${clientId}: ${taskResult.error}`);
          } else if (message.type === MessageType.DISCOVERY_REQUEST) {
            // Send node list to the requesting client
            this.sendMessage(socket, {
              type: MessageType.DISCOVERY_RESPONSE,
              senderId: this.id,
              timestamp: Date.now(),
              payload: Array.from(this.nodeInfo.values())
            });
          }
        } catch (error) {
          logger.error(`Error processing message: ${error}`);
        }
      });
      
      socket.on('close', () => {
        if (clientId) {
          logger.info(`Node ${clientId} disconnected`);
          this.clients.delete(clientId);
          this.nodeInfo.delete(clientId);
          this.broadcastNodeList();
        }
      });
      
      socket.on('error', (error) => {
        logger.error(`WebSocket error with client ${clientId}: ${error}`);
        if (clientId) {
          this.clients.delete(clientId);
          this.nodeInfo.delete(clientId);
          this.broadcastNodeList();
        }
      });
    });
    
    this.server.on('error', (error) => {
      logger.error(`WebSocket server error: ${error}`);
      this.status = NodeStatus.ERROR;
      this.emit('error', error);
    });
    
    this.server.on('listening', () => {
      const address = this.server?.address();
      const actualPort = typeof address === 'object' && address ? address.port : port;
      logger.info(`Coordinator node listening on port ${actualPort}`);
      
      // Start discovery broadcast
      this.startDiscoveryBroadcast();
    });
  }

  /**
   * Connect to coordinator as a worker
   */
  private connectToCoordinator(coordinatorUrl: string): void {
    this.coordinatorConnection = new WebSocket(coordinatorUrl);
    
    this.coordinatorConnection.on('open', () => {
      logger.info(`Connected to coordinator at ${coordinatorUrl}`);
      
      // Register with coordinator
      this.sendToCoordinator({
        type: MessageType.REGISTER,
        senderId: this.id,
        timestamp: Date.now(),
        payload: {
          id: this.id,
          role: this.role,
          status: this.status,
          tasks: {
            pending: 0,
            running: 0,
            completed: 0,
            failed: 0
          },
          capabilities: this.getNodeCapabilities(),
          lastHeartbeat: Date.now()
        }
      });
      
      // Request node discovery
      this.sendToCoordinator({
        type: MessageType.DISCOVERY_REQUEST,
        senderId: this.id,
        timestamp: Date.now(),
        payload: null
      });
    });
    
    this.coordinatorConnection.on('message', (data: WebSocket.Data) => {
      try {
        const message = JSON.parse(data.toString()) as Message;
        
        if (message.type === MessageType.REGISTER_ACK) {
          logger.info(`Registration acknowledged by coordinator ${message.senderId}`);
        } else if (message.type === MessageType.DISCOVERY_RESPONSE) {
          const nodes = message.payload as NodeInfo[];
          nodes.forEach(node => {
            this.nodeInfo.set(node.id, node);
          });
          logger.debug(`Discovered ${nodes.length} nodes in the cluster`);
        } else if (message.type === MessageType.NODE_LIST_UPDATE) {
          const nodes = message.payload as NodeInfo[];
          // Clear existing nodes except self
          const selfInfo = this.nodeInfo.get(this.id);
          this.nodeInfo.clear();
          if (selfInfo) {
            this.nodeInfo.set(this.id, selfInfo);
          }
          
          // Update with new node list
          nodes.forEach(node => {
            if (node.id !== this.id) {
              this.nodeInfo.set(node.id, node);
            }
          });
          logger.debug(`Node list updated: ${nodes.length} nodes in the cluster`);
        } else if (message.type === MessageType.TASK_ASSIGNMENT) {
          const task = message.payload as DistributedTask<any, any>;
          this.handleTaskAssignment(task);
        }
      } catch (error) {
        logger.error(`Error processing message from coordinator: ${error}`);
      }
    });
    
    this.coordinatorConnection.on('close', () => {
      logger.warn('Disconnected from coordinator');
      this.status = NodeStatus.DISCONNECTED;
      this.scheduleReconnect(coordinatorUrl);
    });
    
    this.coordinatorConnection.on('error', (error) => {
      logger.error(`WebSocket error with coordinator: ${error}`);
      this.status = NodeStatus.ERROR;
      this.emit('error', error);
      this.scheduleReconnect(coordinatorUrl);
    });
  }

  /**
   * Schedule reconnection attempt to coordinator
   */
  private scheduleReconnect(coordinatorUrl: string): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    
    this.reconnectTimeout = setTimeout(() => {
      logger.info('Attempting to reconnect to coordinator...');
      this.connectToCoordinator(coordinatorUrl);
    }, 5000); // Try to reconnect every 5 seconds
  }

  /**
   * Set up handlers for task queue events
   */
  private setupTaskQueueHandlers(): void {
    this.taskQueue.on('taskAdded', (task: DistributedTask<any, any>) => {
      if (this.role === NodeRole.COORDINATOR) {
        this.assignTask(task);
      }
    });
    
    this.taskQueue.on('taskCompleted', (task: DistributedTask<any, any>) => {
      this.emit('taskCompleted', task);
      
      // Update task counts in node info
      const nodeInfo = this.nodeInfo.get(this.id);
      if (nodeInfo) {
        nodeInfo.tasks.completed++;
        nodeInfo.tasks.running--;
        this.nodeInfo.set(this.id, nodeInfo);
      }
    });
    
    this.taskQueue.on('taskFailed', (task: DistributedTask<any, any>, error: any) => {
      this.emit('taskFailed', task, error);
      
      // Update task counts in node info
      const nodeInfo = this.nodeInfo.get(this.id);
      if (nodeInfo) {
        nodeInfo.tasks.failed++;
        nodeInfo.tasks.running--;
        this.nodeInfo.set(this.id, nodeInfo);
      }
      
      if (this.role === NodeRole.COORDINATOR) {
        // Retry the task if allowed
        if (task.retries < task.maxRetries) {
          logger.info(`Retrying failed task ${task.id} (attempt ${task.retries + 1}/${task.maxRetries})`);
          const retryTask: DistributedTask<any, any> = {
            ...task,
            retries: task.retries + 1,
            status: 'pending',
            createdAt: Date.now()
          };
          this.taskQueue.submitTask(retryTask);
        }
      }
    });
  }

  /**
   * Start sending periodic heartbeats
   */
  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    this.heartbeatInterval = setInterval(() => {
      // Update our own node info
      const nodeInfo = this.nodeInfo.get(this.id);
      if (nodeInfo) {
        nodeInfo.lastHeartbeat = Date.now();
        nodeInfo.status = this.status;
        nodeInfo.tasks = {
          pending: this.taskQueue.getPendingCount(),
          running: this.taskQueue.getRunningCount(),
          completed: this.taskQueue.getCompletedCount(),
          failed: this.taskQueue.getFailedCount()
        };
        this.nodeInfo.set(this.id, nodeInfo);
      }
      
      if (this.role === NodeRole.WORKER && this.coordinatorConnection) {
        // Send heartbeat to coordinator
        this.sendToCoordinator({
          type: MessageType.HEARTBEAT,
          senderId: this.id,
          timestamp: Date.now(),
          payload: this.nodeInfo.get(this.id)
        });
      } else if (this.role === NodeRole.COORDINATOR) {
        // Check for dead nodes
        const now = Date.now();
        const deadNodeIds: string[] = [];
        
        this.nodeInfo.forEach((info, nodeId) => {
          if (nodeId !== this.id && now - info.lastHeartbeat > 30000) { // 30 seconds timeout
            deadNodeIds.push(nodeId);
          }
        });
        
        // Remove dead nodes
        deadNodeIds.forEach(nodeId => {
          logger.warn(`Node ${nodeId} is considered dead (no heartbeat)`);
          this.nodeInfo.delete(nodeId);
          this.clients.delete(nodeId);
          
          // Reassign tasks from dead node
          this.taskQueue.getRunningTasks().forEach(task => {
            if (task.assignedTo === nodeId) {
              logger.info(`Reassigning task ${task.id} from dead node ${nodeId}`);
              const reassignedTask: DistributedTask<any, any> = {
                ...task,
                status: 'pending',
                assignedTo: undefined
              };
              this.taskQueue.markTaskPending(task.id);
              this.assignTask(reassignedTask);
            }
          });
        });
        
        if (deadNodeIds.length > 0) {
          this.broadcastNodeList();
        }
      }
    }, 10000); // Heartbeat every 10 seconds
  }

  /**
   * Start discovery broadcast for coordinators
   */
  private startDiscoveryBroadcast(): void {
    if (this.role !== NodeRole.COORDINATOR) {
      return;
    }
    
    if (this.discoveryBroadcastInterval) {
      clearInterval(this.discoveryBroadcastInterval);
    }
    
    this.discoveryBroadcastInterval = setInterval(() => {
      this.broadcastNodeList();
    }, 30000); // Broadcast every 30 seconds
  }

  /**
   * Broadcast updated node list to all clients
   */
  private broadcastNodeList(): void {
    if (this.role !== NodeRole.COORDINATOR) {
      return;
    }
    
    const nodeList = Array.from(this.nodeInfo.values());
    
    this.clients.forEach((socket, nodeId) => {
      this.sendMessage(socket, {
        type: MessageType.NODE_LIST_UPDATE,
        senderId: this.id,
        timestamp: Date.now(),
        payload: nodeList
      });
    });
  }

  /**
   * Send a message to a specific socket
   */
  private sendMessage(socket: WebSocket, message: Message): void {
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  }

  /**
   * Send a message to the coordinator
   */
  private sendToCoordinator(message: Message): void {
    if (this.coordinatorConnection && this.coordinatorConnection.readyState === WebSocket.OPEN) {
      this.coordinatorConnection.send(JSON.stringify(message));
    }
  }

  /**
   * Assign a task to an available worker
   */
  private assignTask(task: DistributedTask<any, any>): void {
    if (this.role !== NodeRole.COORDINATOR) {
      return;
    }
    
    // Find available workers
    const availableWorkers = Array.from(this.nodeInfo.values())
      .filter(node => 
        node.role === NodeRole.WORKER && 
        node.status === NodeStatus.READY &&
        this.clients.has(node.id)
      )
      .sort((a, b) => {
        // Simple load balancing by task count
        const aLoad = a.tasks.running;
        const bLoad = b.tasks.running;
        return aLoad - bLoad;
      });
    
    if (availableWorkers.length === 0) {
      // No available workers, execute locally
      logger.info(`No available workers, executing task ${task.id} locally`);
      this.handleTaskAssignment(task);
      return;
    }
    
    // Assign to worker with least load
    const worker = availableWorkers[0];
    const workerSocket = this.clients.get(worker.id);
    
    if (workerSocket) {
      // Update task with assignment
      const assignedTask: DistributedTask<any, any> = {
        ...task,
        assignedTo: worker.id,
        assignedAt: Date.now()
      };
      
      // Update task in queue
      this.taskQueue.assignTask(assignedTask.id, worker.id);
      
      // Send task to worker
      this.sendMessage(workerSocket, {
        type: MessageType.TASK_ASSIGNMENT,
        senderId: this.id,
        timestamp: Date.now(),
        payload: assignedTask
      });
      
      logger.debug(`Assigned task ${task.id} to worker ${worker.id}`);
      
      // Update worker node info
      const nodeInfo = this.nodeInfo.get(worker.id);
      if (nodeInfo) {
        nodeInfo.tasks.running++;
        this.nodeInfo.set(worker.id, nodeInfo);
      }
    }
  }

  /**
   * Handle a task assignment (for workers or coordinator self-execution)
   */
  private async handleTaskAssignment(task: DistributedTask<any, any>): Promise<void> {
    // Update task counts
    const nodeInfo = this.nodeInfo.get(this.id);
    if (nodeInfo) {
      nodeInfo.tasks.running++;
      this.nodeInfo.set(this.id, nodeInfo);
    }
    
    // Set status to busy if we have tasks
    if (this.status === NodeStatus.READY) {
      this.status = NodeStatus.BUSY;
    }
    
    try {
      // Execute the task based on its type
      let result: any = null;
      
      switch (task.type) {
        case TaskType.EVALUATE_POPULATION:
          result = await this.evaluatePopulation(task.data);
          break;
        case TaskType.EVOLVE_GENERATION:
          result = await this.evolveGeneration(task.data);
          break;
        case TaskType.FITNESS_EVALUATION:
          result = await this.evaluateFitness(task.data);
          break;
        case TaskType.SELECTION:
        case TaskType.CROSSOVER:
        case TaskType.MUTATION:
          // These would be implemented similarly
          throw new Error(`Task type ${task.type} not yet implemented`);
        default:
          throw new Error(`Unknown task type: ${task.type}`);
      }
      
      // Task completed successfully
      if (this.role === NodeRole.COORDINATOR) {
        // If we're the coordinator, complete the task locally
        this.taskQueue.completeTask(task.id, result);
      } else if (this.coordinatorConnection) {
        // If we're a worker, send the result back to coordinator
        this.sendToCoordinator({
          type: MessageType.TASK_RESULT,
          senderId: this.id,
          timestamp: Date.now(),
          payload: {
            taskId: task.id,
            result
          }
        });
      }
      
      // Set status back to ready if we have no more tasks
      if (nodeInfo && nodeInfo.tasks.running <= 1) { // Including this one that's about to complete
        this.status = NodeStatus.READY;
      }
    } catch (error) {
      logger.error(`Error executing task ${task.id}: ${error}`);
      
      // Task failed
      if (this.role === NodeRole.COORDINATOR) {
        // If we're the coordinator, mark the task as failed locally
        this.taskQueue.failTask(task.id, error);
      } else if (this.coordinatorConnection) {
        // If we're a worker, send the failure back to coordinator
        this.sendToCoordinator({
          type: MessageType.TASK_FAILED,
          senderId: this.id,
          timestamp: Date.now(),
          payload: {
            taskId: task.id,
            error: error.toString()
          }
        });
      }
      
      // Set status back to ready if we have no more tasks
      if (nodeInfo && nodeInfo.tasks.running <= 1) { // Including this one that's about to fail
        this.status = NodeStatus.READY;
      }
    }
  }

  /**
   * Submit a task to the distributed system
   */
  public submitTask<T, R>(task: Omit<DistributedTask<T, R>, 'id' | 'status' | 'createdAt'>): Promise<R> {
    return new Promise((resolve, reject) => {
      const fullTask = this.taskQueue.submitTask<T, R>({
        ...task,
        id: uuidv4(),
        status: 'pending',
        createdAt: Date.now()
      });
      
      // Set up one-time event listeners for this specific task
      const onComplete = (completedTask: DistributedTask<any, any>) => {
        if (completedTask.id === fullTask.id) {
          this.taskQueue.removeListener('taskCompleted', onComplete);
          this.taskQueue.removeListener('taskFailed', onFail);
          resolve(completedTask.result as R);
        }
      };
      
      const onFail = (failedTask: DistributedTask<any, any>, error: any) => {
        if (failedTask.id === fullTask.id) {
          this.taskQueue.removeListener('taskCompleted', onComplete);
          this.taskQueue.removeListener('taskFailed', onFail);
          reject(error);
        }
      };
      
      this.taskQueue.on('taskCompleted', onComplete);
      this.taskQueue.on('taskFailed', onFail);
      
      return fullTask;
    });
  }

  /**
   * Submit a task to evaluate an entire population
   */
  public evaluatePopulationDistributed(
    population: Chromosome[],
    fitnessFunction: FitnessFunction
  ): Promise<Chromosome[]> {
    return this.submitTask({
      type: TaskType.EVALUATE_POPULATION,
      data: {
        population,
        fitnessFunction: fitnessFunction.toString() // Serialize the function
      },
      priority: 1,
      maxRetries: 3,
      timeout: 60000 // 1 minute timeout
    });
  }

  /**
   * Submit a task to evolve a generation
   */
  public evolveGenerationDistributed(
    population: Chromosome[],
    fitnessFunction: FitnessFunction,
    options: any
  ): Promise<Chromosome[]> {
    return this.submitTask({
      type: TaskType.EVOLVE_GENERATION,
      data: {
        population,
        fitnessFunction: fitnessFunction.toString(),
        options
      },
      priority: 1,
      maxRetries: 3,
      timeout: 120000 // 2 minute timeout
    });
  }

  /**
   * Evaluate population locally
   */
  private async evaluatePopulation(data: any): Promise<Chromosome[]> {
    if (!this.geneticEngine) {
      throw new Error('Genetic engine not available for population evaluation');
    }
    
    const { population, fitnessFunction } = data;
    const fitnessFn = new Function(`return ${fitnessFunction}`)();
    
    return this.geneticEngine.evaluatePopulation(population, fitnessFn);
  }

  /**
   * Evolve generation locally
   */
  private async evolveGeneration(data: any): Promise<Chromosome[]> {
    if (!this.geneticEngine) {
      throw new Error('Genetic engine not available for evolution');
    }
    
    const { population, fitnessFunction, options } = data;
    const fitnessFn = new Function(`return ${fitnessFunction}`)();
    
    if (this.geneticEngine instanceof AdvancedGeneticRepairEngine) {
      return this.geneticEngine.evolveGeneration(population, fitnessFn, options);
    } else {
      return this.geneticEngine.evolveGeneration(population, fitnessFn);
    }
  }

  /**
   * Evaluate fitness for a single chromosome locally
   */
  private async evaluateFitness(data: any): Promise<number> {
    if (!this.geneticEngine) {
      throw new Error('Genetic engine not available for fitness evaluation');
    }
    
    const { chromosome, fitnessFunction } = data;
    const fitnessFn = new Function(`return ${fitnessFunction}`)();
    
    return fitnessFn(chromosome);
  }

  /**
   * Get capabilities of this node
   */
  private getNodeCapabilities(): string[] {
    const capabilities = ['basic'];
    
    if (this.geneticEngine) {
      capabilities.push('genetic');
      
      if (this.geneticEngine instanceof AdvancedGeneticRepairEngine) {
        capabilities.push('advanced-genetic');
      }
    }
    
    // CPU cores
    const cpuCount = require('os').cpus().length;
    capabilities.push(`cpu-${cpuCount}`);
    
    // Memory
    const totalMemory = Math.floor(require('os').totalmem() / (1024 * 1024 * 1024));
    capabilities.push(`mem-${totalMemory}GB`);
    
    return capabilities;
  }
  
  /**
   * Stop the node and clean up resources
   */
  public stop(): void {
    logger.info(`Stopping node ${this.id}`);
    
    // Clear intervals
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    
    if (this.discoveryBroadcastInterval) {
      clearInterval(this.discoveryBroadcastInterval);
    }
    
    // Close server if coordinator
    if (this.server) {
      this.server.close();
    }
    
    // Close all client connections
    this.clients.forEach(client => {
      client.close();
    });
    
    // Close coordinator connection if worker
    if (this.coordinatorConnection) {
      this.coordinatorConnection.close();
    }
    
    this.status = NodeStatus.SHUTDOWN;
    this.emit('shutdown');
  }
}