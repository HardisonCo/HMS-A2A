import { DistributedError, CircuitBreaker, retry } from '../../utils/error_handling';
import { createComponentLogger } from '../../utils/logger';
import { NodeInfo, NodeStatus, TaskType } from './distributed_types';
import { DistributedNode } from './distributed_node';
import { DistributedCluster } from './distributed_cluster';

const logger = createComponentLogger('distributed-error-handler');

/**
 * Node connection error 
 */
export class NodeConnectionError extends DistributedError {
  constructor(
    message: string,
    options: {
      nodeId?: string;
      coordinatorUrl?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: 'NODE_CONNECTION_ERROR',
      context: {
        nodeId: options.nodeId,
        coordinatorUrl: options.coordinatorUrl,
        ...options.context
      },
      cause: options.cause
    });
  }
}

/**
 * Task execution error
 */
export class TaskExecutionError extends DistributedError {
  constructor(
    message: string,
    options: {
      taskId?: string;
      taskType?: TaskType;
      nodeId?: string;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: 'TASK_EXECUTION_ERROR',
      context: {
        taskId: options.taskId,
        taskType: options.taskType,
        nodeId: options.nodeId,
        ...options.context
      },
      cause: options.cause
    });
  }
}

/**
 * Node failure error
 */
export class NodeFailureError extends DistributedError {
  constructor(
    message: string,
    options: {
      nodeId?: string;
      nodeRole?: string;
      lastStatus?: NodeStatus;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: 'NODE_FAILURE_ERROR',
      context: {
        nodeId: options.nodeId,
        nodeRole: options.nodeRole,
        lastStatus: options.lastStatus,
        ...options.context
      },
      cause: options.cause
    });
  }
}

/**
 * Task timeout error
 */
export class TaskTimeoutError extends DistributedError {
  constructor(
    message: string,
    options: {
      taskId?: string;
      taskType?: TaskType;
      nodeId?: string;
      elapsedTimeMs?: number;
      timeoutMs?: number;
      context?: Record<string, any>;
    } = {}
  ) {
    super(message, {
      code: 'TASK_TIMEOUT_ERROR',
      context: {
        taskId: options.taskId,
        taskType: options.taskType,
        nodeId: options.nodeId,
        elapsedTimeMs: options.elapsedTimeMs,
        timeoutMs: options.timeoutMs,
        ...options.context
      }
    });
  }
}

/**
 * Cluster initialization error
 */
export class ClusterInitializationError extends DistributedError {
  constructor(
    message: string,
    options: {
      basePort?: number;
      workerCount?: number;
      context?: Record<string, any>;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: 'CLUSTER_INITIALIZATION_ERROR',
      context: {
        basePort: options.basePort,
        workerCount: options.workerCount,
        ...options.context
      },
      cause: options.cause
    });
  }
}

/**
 * Circuit breaker for node connections
 */
export class NodeConnectionCircuitBreaker {
  private circuitBreakers: Map<string, CircuitBreaker> = new Map();

  /**
   * Get or create a circuit breaker for a specific node
   */
  public getCircuitBreaker(nodeId: string): CircuitBreaker {
    if (!this.circuitBreakers.has(nodeId)) {
      const circuitBreaker = new CircuitBreaker({
        failureThreshold: 3,
        resetTimeout: 30000, // 30 seconds
        onStateChange: (from, to) => {
          logger.info(`Circuit breaker for node ${nodeId} changed from ${from} to ${to}`);
        }
      });
      this.circuitBreakers.set(nodeId, circuitBreaker);
    }
    
    return this.circuitBreakers.get(nodeId)!;
  }

  /**
   * Execute a function with circuit breaker protection for a specific node
   */
  public async executeForNode<T>(nodeId: string, fn: () => Promise<T>): Promise<T> {
    const circuitBreaker = this.getCircuitBreaker(nodeId);
    return circuitBreaker.execute(fn);
  }

  /**
   * Get the status of all circuit breakers
   */
  public getStatus(): Record<string, { state: string; failures: number }> {
    const status: Record<string, { state: string; failures: number }> = {};
    
    this.circuitBreakers.forEach((breaker, nodeId) => {
      status[nodeId] = {
        state: breaker.getState(),
        failures: breaker.getFailureCount()
      };
    });
    
    return status;
  }

  /**
   * Reset the circuit breaker for a specific node
   */
  public resetNode(nodeId: string): void {
    const circuitBreaker = this.circuitBreakers.get(nodeId);
    if (circuitBreaker) {
      circuitBreaker.reset();
    }
  }

  /**
   * Reset all circuit breakers
   */
  public resetAll(): void {
    this.circuitBreakers.forEach(breaker => breaker.reset());
  }
}

/**
 * Health monitoring system for distributed nodes
 */
export class DistributedHealthMonitor {
  private isMonitoring: boolean = false;
  private monitorInterval?: NodeJS.Timeout;
  private nodeHealthHistory: Map<string, { 
    checks: Array<{ timestamp: number; healthy: boolean; reason?: string }> 
  }> = new Map();
  private circuitBreaker: NodeConnectionCircuitBreaker;
  
  constructor(
    private readonly cluster: DistributedCluster,
    private readonly options: {
      checkIntervalMs?: number;
      nodeTimeoutMs?: number;
      healthHistorySize?: number;
      onNodeUnhealthy?: (nodeId: string, info: NodeInfo, reason: string) => void;
      onNodeRecovered?: (nodeId: string, info: NodeInfo) => void;
    } = {}
  ) {
    this.circuitBreaker = new NodeConnectionCircuitBreaker();
  }

  /**
   * Start health monitoring
   */
  public start(): void {
    if (this.isMonitoring) {
      return;
    }
    
    this.isMonitoring = true;
    const checkInterval = this.options.checkIntervalMs || 30000; // 30 seconds
    
    this.monitorInterval = setInterval(() => {
      this.checkNodesHealth();
    }, checkInterval);
    
    logger.info(`Started health monitoring with ${checkInterval}ms interval`);
  }

  /**
   * Stop health monitoring
   */
  public stop(): void {
    if (!this.isMonitoring) {
      return;
    }
    
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
    }
    
    this.isMonitoring = false;
    logger.info('Stopped health monitoring');
  }

  /**
   * Check the health of all nodes
   */
  private checkNodesHealth(): void {
    const clusterStatus = this.cluster.getClusterStatus();
    const now = Date.now();
    const nodeTimeout = this.options.nodeTimeoutMs || 60000; // 60 seconds
    
    // Check coordinator
    if (clusterStatus.coordinator) {
      this.checkNodeHealth(clusterStatus.coordinator, now, nodeTimeout);
    }
    
    // Check workers
    clusterStatus.workers.forEach(worker => {
      this.checkNodeHealth(worker, now, nodeTimeout);
    });
  }

  /**
   * Check the health of a specific node
   */
  private checkNodeHealth(node: NodeInfo, now: number, nodeTimeout: number): void {
    // Initialize history if needed
    if (!this.nodeHealthHistory.has(node.id)) {
      this.nodeHealthHistory.set(node.id, { checks: [] });
    }
    
    const history = this.nodeHealthHistory.get(node.id)!;
    const historySize = this.options.healthHistorySize || 10;
    
    // Check if node is healthy
    let isHealthy = true;
    let reason = '';
    
    // Check last heartbeat
    if (now - node.lastHeartbeat > nodeTimeout) {
      isHealthy = false;
      reason = `No heartbeat received in ${(now - node.lastHeartbeat) / 1000} seconds`;
    }
    
    // Check status
    if (node.status === NodeStatus.ERROR || node.status === NodeStatus.SHUTDOWN) {
      isHealthy = false;
      reason = `Node has ${node.status} status`;
    }
    
    // Add to history
    history.checks.push({
      timestamp: now,
      healthy: isHealthy,
      reason: isHealthy ? undefined : reason
    });
    
    // Trim history if needed
    if (history.checks.length > historySize) {
      history.checks = history.checks.slice(-historySize);
    }
    
    // Check for state changes
    const previousChecks = history.checks.slice(0, -1);
    const wasPreviouslyHealthy = previousChecks.length === 0 || 
      previousChecks[previousChecks.length - 1].healthy;
    
    if (!isHealthy && wasPreviouslyHealthy) {
      // Node just became unhealthy
      logger.warn(`Node ${node.id} is unhealthy: ${reason}`);
      
      if (this.options.onNodeUnhealthy) {
        this.options.onNodeUnhealthy(node.id, node, reason);
      }
    } else if (isHealthy && !wasPreviouslyHealthy) {
      // Node just recovered
      logger.info(`Node ${node.id} has recovered`);
      
      // Reset circuit breaker
      this.circuitBreaker.resetNode(node.id);
      
      if (this.options.onNodeRecovered) {
        this.options.onNodeRecovered(node.id, node);
      }
    }
  }

  /**
   * Get health history for all nodes
   */
  public getHealthHistory(): Record<string, Array<{ timestamp: number; healthy: boolean; reason?: string }>> {
    const history: Record<string, Array<{ timestamp: number; healthy: boolean; reason?: string }>> = {};
    
    this.nodeHealthHistory.forEach((nodeHistory, nodeId) => {
      history[nodeId] = nodeHistory.checks;
    });
    
    return history;
  }

  /**
   * Get circuit breaker status
   */
  public getCircuitBreakerStatus(): Record<string, { state: string; failures: number }> {
    return this.circuitBreaker.getStatus();
  }

  /**
   * Get the circuit breaker for node connections
   */
  public getCircuitBreaker(): NodeConnectionCircuitBreaker {
    return this.circuitBreaker;
  }
}

/**
 * Apply error handling to a distributed node
 */
export function applyDistributedErrorHandling(
  node: DistributedNode
): { 
  sendWithRetry: <T>(nodeId: string, fn: () => Promise<T>) => Promise<T>;
} {
  const circuitBreaker = new NodeConnectionCircuitBreaker();
  
  // Add error handling for task execution
  node.on('error', (error: Error) => {
    if (!(error instanceof DistributedError)) {
      error = new DistributedError('Distributed node error', {
        code: 'NODE_ERROR',
        context: { nodeId: node.getId(), role: node.getRole() },
        cause: error
      });
    }
    
    logger.error(`Node ${node.getId()} error:`, error);
  });
  
  /**
   * Send a message to a node with retry and circuit breaker
   */
  async function sendWithRetry<T>(nodeId: string, fn: () => Promise<T>): Promise<T> {
    return circuitBreaker.executeForNode(nodeId, () => {
      return retry(fn, {
        maxRetries: 3,
        initialDelay: 100,
        maxDelay: 3000,
        shouldRetry: (error) => {
          // Determine if we should retry based on error type
          if (error instanceof TaskTimeoutError) {
            return true;
          }
          
          if (error instanceof NodeConnectionError) {
            return true;
          }
          
          return false;
        }
      });
    });
  }
  
  return { sendWithRetry };
}