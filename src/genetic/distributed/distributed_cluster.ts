import { EventEmitter } from 'events';
import { DistributedNode } from './distributed_node';
import { NodeRole, NodeStatus, DistributedTask, NodeInfo } from './distributed_types';
import { GeneticRepairEngine } from '../genetic_repair_engine';
import { AdvancedGeneticRepairEngine } from '../advanced/advanced_genetic_repair_engine';
import { Chromosome } from '../chromosome';
import { FitnessFunction } from '../types';
import { logger } from '../../utils/logger';

/**
 * DistributedCluster class for managing a cluster of distributed nodes
 * 
 * Provides a high-level interface for distributed genetic algorithm operations
 * Handles node discovery, task distribution, and fault tolerance
 */
export class DistributedCluster extends EventEmitter {
  private coordinatorNode: DistributedNode;
  private workerNodes: Map<string, DistributedNode> = new Map();
  private geneticEngine?: GeneticRepairEngine | AdvancedGeneticRepairEngine;
  private basePort: number;
  private maxWorkers: number;
  private autoScaling: boolean;
  private isRunning: boolean = false;
  private clusterReady: boolean = false;
  private nodeMonitorInterval?: NodeJS.Timeout;

  /**
   * Create a new distributed cluster
   * 
   * @param basePort The port for the coordinator node
   * @param workerCount Initial number of worker nodes to create
   * @param geneticEngine Genetic engine to use for local computations
   * @param autoScaling Whether to automatically scale the cluster
   */
  constructor(
    basePort: number = 9000,
    workerCount: number = 0,
    geneticEngine?: GeneticRepairEngine | AdvancedGeneticRepairEngine,
    autoScaling: boolean = false
  ) {
    super();
    this.basePort = basePort;
    this.geneticEngine = geneticEngine;
    this.maxWorkers = workerCount;
    this.autoScaling = autoScaling;
    
    // Create coordinator node
    this.coordinatorNode = new DistributedNode(
      NodeRole.COORDINATOR,
      basePort,
      undefined,
      geneticEngine
    );
    
    // Set up coordinator event listeners
    this.setupCoordinatorEvents();
    
    // Start with initial worker nodes if specified
    if (workerCount > 0) {
      this.scaleToWorkerCount(workerCount);
    }
    
    // Start node monitoring if auto-scaling is enabled
    if (autoScaling) {
      this.startNodeMonitoring();
    }
    
    this.isRunning = true;
    logger.info(`Distributed cluster initialized with coordinator on port ${basePort}`);
  }

  /**
   * Set up event listeners for the coordinator node
   */
  private setupCoordinatorEvents(): void {
    this.coordinatorNode.on('ready', () => {
      logger.info(`Coordinator node ready with ID ${this.coordinatorNode.getId()}`);
      this.checkClusterReady();
    });
    
    this.coordinatorNode.on('error', (error) => {
      logger.error(`Coordinator node error: ${error}`);
      this.emit('error', error);
    });
    
    this.coordinatorNode.on('taskCompleted', (task: DistributedTask<any, any>) => {
      this.emit('taskCompleted', task);
    });
    
    this.coordinatorNode.on('taskFailed', (task: DistributedTask<any, any>, error: any) => {
      this.emit('taskFailed', task, error);
    });
  }

  /**
   * Start a worker node
   * 
   * @returns The ID of the created worker node
   */
  public startWorkerNode(): string {
    const workerId = `worker-${Date.now()}-${this.workerNodes.size}`;
    const coordinatorUrl = `ws://localhost:${this.basePort}`;
    
    const workerNode = new DistributedNode(
      NodeRole.WORKER,
      0, // Port not needed for workers
      coordinatorUrl,
      this.geneticEngine
    );
    
    workerNode.on('ready', () => {
      logger.info(`Worker node ${workerNode.getId()} ready`);
      this.checkClusterReady();
    });
    
    workerNode.on('error', (error) => {
      logger.error(`Worker node ${workerNode.getId()} error: ${error}`);
    });
    
    workerNode.on('shutdown', () => {
      logger.info(`Worker node ${workerNode.getId()} shutdown`);
      this.workerNodes.delete(workerNode.getId());
      this.checkClusterReady();
    });
    
    this.workerNodes.set(workerNode.getId(), workerNode);
    return workerNode.getId();
  }

  /**
   * Scale the cluster to a specific number of worker nodes
   * 
   * @param count Target number of worker nodes
   */
  public scaleToWorkerCount(count: number): void {
    const currentCount = this.workerNodes.size;
    
    if (count > currentCount) {
      // Scale up
      for (let i = 0; i < count - currentCount; i++) {
        this.startWorkerNode();
      }
    } else if (count < currentCount) {
      // Scale down
      const nodesToRemove = Array.from(this.workerNodes.values())
        .slice(0, currentCount - count);
      
      nodesToRemove.forEach(node => {
        node.stop();
        this.workerNodes.delete(node.getId());
      });
      
      logger.info(`Scaled down cluster by removing ${nodesToRemove.length} worker nodes`);
    }
    
    this.maxWorkers = count;
  }

  /**
   * Start monitoring nodes for auto-scaling
   */
  private startNodeMonitoring(): void {
    if (this.nodeMonitorInterval) {
      clearInterval(this.nodeMonitorInterval);
    }
    
    this.nodeMonitorInterval = setInterval(() => {
      if (!this.autoScaling || !this.isRunning) {
        return;
      }
      
      const nodes = this.coordinatorNode.getNodes();
      const workers = Array.from(nodes.values()).filter(node => 
        node.role === NodeRole.WORKER && 
        node.status !== NodeStatus.ERROR && 
        node.status !== NodeStatus.SHUTDOWN
      );
      
      // Calculate average load
      let totalRunningTasks = 0;
      let totalCapacity = 0;
      
      workers.forEach(worker => {
        totalRunningTasks += worker.tasks.running;
        
        // Estimate capacity based on CPU cores
        const cpuCore = worker.capabilities.find(cap => cap.startsWith('cpu-'));
        if (cpuCore) {
          const cores = parseInt(cpuCore.split('-')[1]);
          totalCapacity += cores;
        } else {
          totalCapacity += 2; // Default assumption if CPU info not available
        }
      });
      
      const loadFactor = workers.length > 0 ? totalRunningTasks / totalCapacity : 0;
      
      // Auto-scaling logic
      if (loadFactor > 0.8 && workers.length < this.maxWorkers) {
        // Scale up - high load
        logger.info(`Auto-scaling up due to high load (${loadFactor.toFixed(2)})`);
        this.startWorkerNode();
      } else if (loadFactor < 0.2 && workers.length > 1) {
        // Scale down - low load
        logger.info(`Auto-scaling down due to low load (${loadFactor.toFixed(2)})`);
        
        // Find idle worker
        const idleWorkers = workers.filter(w => w.tasks.running === 0);
        if (idleWorkers.length > 0) {
          const idleWorker = idleWorkers[0];
          const workerNode = this.workerNodes.get(idleWorker.id);
          if (workerNode) {
            workerNode.stop();
            this.workerNodes.delete(idleWorker.id);
          }
        }
      }
    }, 60000); // Check every minute
  }

  /**
   * Check if the cluster is ready (coordinator and at least one worker)
   */
  private checkClusterReady(): void {
    const wasReady = this.clusterReady;
    
    // Cluster is ready if coordinator is ready and we have at least one worker
    // or if we're not using workers (maxWorkers === 0)
    this.clusterReady = 
      this.coordinatorNode.getStatus() === NodeStatus.READY &&
      (this.workerNodes.size > 0 || this.maxWorkers === 0);
    
    if (this.clusterReady && !wasReady) {
      logger.info('Distributed cluster is now ready');
      this.emit('ready');
    } else if (!this.clusterReady && wasReady) {
      logger.warn('Distributed cluster is no longer ready');
      this.emit('notReady');
    }
  }

  /**
   * Get the status of all nodes in the cluster
   */
  public getClusterStatus(): { 
    coordinator: NodeInfo | undefined, 
    workers: NodeInfo[],
    isReady: boolean
  } {
    const nodes = this.coordinatorNode.getNodes();
    const coordinator = nodes.get(this.coordinatorNode.getId());
    const workers = Array.from(nodes.values()).filter(node => node.role === NodeRole.WORKER);
    
    return {
      coordinator,
      workers,
      isReady: this.clusterReady
    };
  }

  /**
   * Submit a distributed task to evaluate a population
   */
  public async evaluatePopulation(
    population: Chromosome[],
    fitnessFunction: FitnessFunction
  ): Promise<Chromosome[]> {
    if (!this.clusterReady) {
      throw new Error('Cluster is not ready');
    }
    
    return this.coordinatorNode.evaluatePopulationDistributed(population, fitnessFunction);
  }

  /**
   * Submit a distributed task to evolve a generation
   */
  public async evolveGeneration(
    population: Chromosome[],
    fitnessFunction: FitnessFunction,
    options: any
  ): Promise<Chromosome[]> {
    if (!this.clusterReady) {
      throw new Error('Cluster is not ready');
    }
    
    return this.coordinatorNode.evolveGenerationDistributed(population, fitnessFunction, options);
  }

  /**
   * Stop the cluster and all nodes
   */
  public stop(): void {
    logger.info('Stopping distributed cluster');
    this.isRunning = false;
    
    // Stop auto-scaling
    if (this.nodeMonitorInterval) {
      clearInterval(this.nodeMonitorInterval);
    }
    
    // Stop all worker nodes
    this.workerNodes.forEach(node => {
      node.stop();
    });
    this.workerNodes.clear();
    
    // Stop coordinator node
    this.coordinatorNode.stop();
    
    this.clusterReady = false;
    this.emit('shutdown');
  }
}