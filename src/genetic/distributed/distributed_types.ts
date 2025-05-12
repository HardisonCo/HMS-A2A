import { 
  Solution, 
  Population, 
  EvolutionMetrics, 
  GeneticOperationStats 
} from '../types';

/**
 * Types of distributed computing tasks
 */
export enum TaskType {
  EVALUATE_POPULATION = 'evaluate_population',
  EVOLVE_GENERATION = 'evolve_generation',
  CROSSOVER = 'crossover',
  MUTATION = 'mutation',
  SELECTION = 'selection',
  FITNESS_EVALUATION = 'fitness_evaluation',
  NODE_STATUS = 'node_status',
  HEARTBEAT = 'heartbeat'
}

/**
 * Task status values
 */
export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  TIMEOUT = 'timeout'
}

/**
 * Node role in the distributed system
 */
export enum NodeRole {
  COORDINATOR = 'coordinator',
  WORKER = 'worker',
  HYBRID = 'hybrid'
}

/**
 * Node status
 */
export enum NodeStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  BUSY = 'busy',
  IDLE = 'idle',
  STARTING = 'starting',
  STOPPING = 'stopping',
  ERROR = 'error'
}

/**
 * Distributed task interface
 */
export interface DistributedTask<T = any, R = any> {
  id: string;
  type: TaskType;
  data: T;
  status: TaskStatus;
  priority?: number;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
  result?: R;
  error?: string;
  assignedTo?: string;
  timeoutMs?: number;
  attempts?: number;
  maxAttempts?: number;
  dependencies?: string[];
}

/**
 * Task to evaluate fitness of a population
 */
export interface EvaluatePopulationTask {
  population: Population;
  batchId?: string;
  options?: {
    parallelism?: number;
    timeoutPerSolution?: number;
  };
}

/**
 * Result of population evaluation
 */
export interface EvaluatePopulationResult {
  population: Population;
  batchId?: string;
  executionTimeMs: number;
}

/**
 * Task to evolve a population for a single generation
 */
export interface EvolveGenerationTask {
  population: Population;
  generation: number;
  options?: {
    selectionStrategy: string;
    crossoverRate: number;
    mutationRate: number;
    elitismCount: number;
    tournamentSize?: number;
  };
}

/**
 * Result of generation evolution
 */
export interface EvolveGenerationResult {
  population: Population;
  generation: number;
  metrics: EvolutionMetrics;
  operationStats: GeneticOperationStats[];
  executionTimeMs: number;
}

/**
 * Task to perform crossover on parents
 */
export interface CrossoverTask {
  parents: Solution[];
  method: string;
  options?: Record<string, any>;
}

/**
 * Result of crossover operation
 */
export interface CrossoverResult {
  children: Solution[];
  executionTimeMs: number;
}

/**
 * Task to perform mutation on solutions
 */
export interface MutationTask {
  solutions: Solution[];
  method: string;
  genePool?: string[];
  options?: Record<string, any>;
}

/**
 * Result of mutation operation
 */
export interface MutationResult {
  mutatedSolutions: Solution[];
  executionTimeMs: number;
}

/**
 * Task to evaluate fitness of solutions
 */
export interface FitnessEvaluationTask {
  solutions: Solution[];
  batchId?: string;
}

/**
 * Result of fitness evaluation
 */
export interface FitnessEvaluationResult {
  solutions: Solution[];
  batchId?: string;
  executionTimeMs: number;
}

/**
 * Task to check node status
 */
export interface NodeStatusTask {
  requestDetails?: boolean;
}

/**
 * Result of node status check
 */
export interface NodeStatusResult {
  nodeId: string;
  status: NodeStatus;
  role: NodeRole;
  uptime: number;
  load: number;
  memoryUsage: number;
  activeTaskCount: number;
  completedTaskCount: number;
  failedTaskCount: number;
  queuedTaskCount: number;
  capabilities?: string[];
  version?: string;
  startTime: number;
}

/**
 * Heartbeat task
 */
export interface HeartbeatTask {
  timestamp: number;
}

/**
 * Heartbeat result
 */
export interface HeartbeatResult {
  nodeId: string;
  timestamp: number;
  status: NodeStatus;
  load: number;
  activeTaskCount: number;
}

/**
 * Node discovery information
 */
export interface NodeDiscoveryInfo {
  nodeId: string;
  role: NodeRole;
  url: string;
  capabilities: string[];
  status: NodeStatus;
  priority: number;
  maxConcurrentTasks: number;
}

/**
 * Task scheduling strategy
 */
export enum SchedulingStrategy {
  ROUND_ROBIN = 'round_robin',
  LEAST_BUSY = 'least_busy',
  FASTEST_NODE = 'fastest_node',
  RANDOM = 'random',
  SPECIALIZED = 'specialized'
}

/**
 * Distributed system configuration
 */
export interface DistributedSystemConfig {
  nodeId: string;
  role: NodeRole;
  coordinatorUrl?: string;
  port?: number;
  discoveryUrls?: string[];
  schedulingStrategy?: SchedulingStrategy;
  maxConcurrentTasks?: number;
  taskTimeout?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  taskRetryCount?: number;
  enableMetrics?: boolean;
  logLevel?: string;
  capabilities?: string[];
}

/**
 * Task progress update
 */
export interface TaskProgressUpdate {
  taskId: string;
  progress: number;
  status: TaskStatus;
  message?: string;
  intermediateResult?: any;
  timestamp: number;
}

/**
 * System metrics
 */
export interface SystemMetrics {
  timestamp: number;
  nodeId: string;
  activeNodes: number;
  totalTasksCreated: number;
  totalTasksCompleted: number;
  totalTasksFailed: number;
  averageTaskTime: number;
  averageQueueTime: number;
  systemLoad: number;
  throughput: number;
}

/**
 * Node metrics
 */
export interface NodeMetrics {
  timestamp: number;
  nodeId: string;
  activeTaskCount: number;
  completedTaskCount: number;
  failedTaskCount: number;
  queuedTaskCount: number;
  averageTaskTime: number;
  averageQueueTime: number;
  cpuUsage: number;
  memoryUsage: number;
  networkUsage: number;
  taskThroughput: number;
  taskSuccessRate: number;
}

/**
 * Distributed compute error
 */
export class DistributedComputeError extends Error {
  code: string;
  details?: any;
  
  constructor(message: string, code: string, details?: any) {
    super(message);
    this.name = 'DistributedComputeError';
    this.code = code;
    this.details = details;
  }
}