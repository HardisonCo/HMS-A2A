/**
 * Adaptive task allocation system for workflows
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { 
  Workflow, 
  Task, 
  TaskStatus, 
  WorkflowStatus,
  CoordinationStrategy 
} from './workflow_orchestrator';
import { AgentRegistry } from '../core/agent_registry';
import { Agent } from '../agents/agent_interface';
import { SkillLevel } from './workflow_models';

/**
 * Performance metrics for an agent
 */
export interface AgentPerformanceMetrics {
  agentId: string;
  agentType: string;
  successRate: number;         // Success rate for completed tasks (0-1)
  averageTaskDuration: number; // Average task duration in ms
  taskCount: number;           // Number of tasks completed
  errorRate: number;           // Error rate for tasks (0-1)
  utilization: number;         // Agent utilization (0-1)
  lastUpdated: number;         // Timestamp of last update
  domainSpecificMetrics: Record<string, number>; // Domain-specific metrics
}

/**
 * Allocation constraints for task assignment
 */
export interface AllocationConstraints {
  maxTasksPerAgent?: number;      // Maximum tasks per agent
  maxUtilization?: number;        // Maximum agent utilization (0-1)
  minSuccessRate?: number;        // Minimum success rate required (0-1)
  domainPriorities?: {            // Domain priority mapping
    [domain: string]: number;     // Higher number = higher priority
  };
  requiredSkillLevel?: SkillLevel; // Minimum skill level required
  excludedAgentIds?: string[];    // Agents to exclude from allocation
  preferredAgentIds?: string[];   // Preferred agents for allocation
  loadBalancingFactor?: number;   // Factor for load balancing (0-1, higher = more balanced)
  timeoutFactor?: number;         // Factor for timeout importance (0-1)
  priorityBoost?: number;         // Boost for high-priority tasks (0-10)
}

/**
 * Result of a task allocation
 */
export interface AllocationResult {
  taskId: string;
  agentId: string;
  score: number;                // Allocation score (higher is better)
  metrics: {
    matchScore: number;         // How well the agent matches the task (0-1)
    loadScore: number;          // Agent load score (higher = less loaded)
    performanceScore: number;   // Agent performance score (0-1)
    priorityScore: number;      // Task priority score (0-1)
  };
  timestamp: number;
  allocatedBy: string;          // Allocation strategy name
}

/**
 * Task allocation strategy
 */
export interface AllocationStrategy {
  name: string;
  allocateTasks(workflow: Workflow, tasks: Task[], constraints?: AllocationConstraints): Promise<Map<string, AllocationResult>>;
  calculateAgentScore(agent: Agent, task: Task, metrics: AgentPerformanceMetrics | undefined, constraints?: AllocationConstraints): number;
}

/**
 * Round robin allocation strategy
 */
export class RoundRobinStrategy implements AllocationStrategy {
  name = 'round_robin';
  private lastAgentIndex = new Map<string, number>(); // Maps agent types to last used index
  
  async allocateTasks(workflow: Workflow, tasks: Task[], constraints?: AllocationConstraints): Promise<Map<string, AllocationResult>> {
    const allocations = new Map<string, AllocationResult>();
    
    // Group tasks by agent type
    const tasksByAgentType = new Map<string, Task[]>();
    
    for (const task of tasks) {
      if (!task.agentType) continue;
      
      if (!tasksByAgentType.has(task.agentType)) {
        tasksByAgentType.set(task.agentType, []);
      }
      tasksByAgentType.get(task.agentType)?.push(task);
    }
    
    // Allocate tasks for each agent type
    for (const [agentType, agentTasks] of tasksByAgentType.entries()) {
      // Get available agents of this type
      const agents = await this.getAvailableAgents(agentType, constraints);
      if (agents.length === 0) continue;
      
      // Get last index used for this agent type
      let lastIndex = this.lastAgentIndex.get(agentType) || -1;
      
      // Allocate tasks in round robin fashion
      for (const task of agentTasks) {
        // Get next agent index
        lastIndex = (lastIndex + 1) % agents.length;
        
        // Get agent
        const agent = agents[lastIndex];
        
        // Create allocation result
        const result: AllocationResult = {
          taskId: task.id,
          agentId: agent.getId(),
          score: 0.7, // Default score for round robin
          metrics: {
            matchScore: 0.8,
            loadScore: 0.7,
            performanceScore: 0.6,
            priorityScore: task.priority / 10
          },
          timestamp: Date.now(),
          allocatedBy: this.name
        };
        
        // Add to allocations
        allocations.set(task.id, result);
      }
      
      // Update last index
      this.lastAgentIndex.set(agentType, lastIndex);
    }
    
    return allocations;
  }
  
  calculateAgentScore(agent: Agent, task: Task, metrics: AgentPerformanceMetrics | undefined, constraints?: AllocationConstraints): number {
    // For round robin, just return a default score
    return 0.7;
  }
  
  private async getAvailableAgents(agentType: string, constraints?: AllocationConstraints): Promise<Agent[]> {
    // In a real implementation, this would query the agent registry
    // For now, we'll return a mock list of agents
    const agents: Agent[] = [];
    
    // Create mock agents
    for (let i = 0; i < 3; i++) {
      const agent = {
        getId: () => `agent_${agentType}_${i}`,
        getType: () => agentType,
        isAvailable: () => true
      } as unknown as Agent;
      
      agents.push(agent);
    }
    
    return agents;
  }
}

/**
 * Performance-based allocation strategy
 */
export class PerformanceBasedStrategy implements AllocationStrategy {
  name = 'performance_based';
  private performanceTracker: TaskAllocationPerformanceTracker;
  private agentRegistry: AgentRegistry;
  
  constructor(performanceTracker: TaskAllocationPerformanceTracker, agentRegistry: AgentRegistry) {
    this.performanceTracker = performanceTracker;
    this.agentRegistry = agentRegistry;
  }
  
  async allocateTasks(workflow: Workflow, tasks: Task[], constraints?: AllocationConstraints): Promise<Map<string, AllocationResult>> {
    const allocations = new Map<string, AllocationResult>();
    
    for (const task of tasks) {
      if (!task.agentType) continue;
      
      // Get available agents of the required type
      const agents = this.agentRegistry.getAgentsByType(task.agentType)
        .filter(agent => this.isAgentAvailable(agent, constraints));
      
      if (agents.length === 0) continue;
      
      // Calculate scores for each agent
      const agentScores = new Map<string, number>();
      const allocationMetrics = new Map<string, AllocationResult['metrics']>();
      
      for (const agent of agents) {
        // Get performance metrics for agent
        const metrics = this.performanceTracker.getAgentMetrics(agent.getId());
        
        // Calculate score
        const score = this.calculateAgentScore(agent, task, metrics, constraints);
        
        // Calculate detailed metrics
        const detailedMetrics = this.calculateDetailedMetrics(agent, task, metrics, constraints);
        
        // Store score and metrics
        agentScores.set(agent.getId(), score);
        allocationMetrics.set(agent.getId(), detailedMetrics);
      }
      
      // Find agent with highest score
      let bestAgentId: string | null = null;
      let bestScore = -Infinity;
      
      for (const [agentId, score] of agentScores.entries()) {
        if (score > bestScore) {
          bestScore = score;
          bestAgentId = agentId;
        }
      }
      
      if (bestAgentId) {
        // Create allocation result
        const result: AllocationResult = {
          taskId: task.id,
          agentId: bestAgentId,
          score: bestScore,
          metrics: allocationMetrics.get(bestAgentId) || {
            matchScore: 0,
            loadScore: 0,
            performanceScore: 0,
            priorityScore: 0
          },
          timestamp: Date.now(),
          allocatedBy: this.name
        };
        
        // Add to allocations
        allocations.set(task.id, result);
      }
    }
    
    return allocations;
  }
  
  calculateAgentScore(agent: Agent, task: Task, metrics: AgentPerformanceMetrics | undefined, constraints?: AllocationConstraints): number {
    // Default metrics if none available
    const defaultMetrics: AgentPerformanceMetrics = {
      agentId: agent.getId(),
      agentType: agent.getType(),
      successRate: 0.8,
      averageTaskDuration: 60000, // 1 minute
      taskCount: 0,
      errorRate: 0.1,
      utilization: 0.5,
      lastUpdated: Date.now(),
      domainSpecificMetrics: {}
    };
    
    const agentMetrics = metrics || defaultMetrics;
    
    // Calculate score components
    const successScore = agentMetrics.successRate * 0.4;
    const utilizationScore = (1 - agentMetrics.utilization) * 0.3;
    const experienceScore = Math.min(1, agentMetrics.taskCount / 100) * 0.2;
    const errorPenalty = agentMetrics.errorRate * 0.1;
    
    // Apply domain-specific boost if available
    let domainBoost = 0;
    if (task.metadata.domain && agentMetrics.domainSpecificMetrics[task.metadata.domain]) {
      domainBoost = agentMetrics.domainSpecificMetrics[task.metadata.domain] * 0.2;
    }
    
    // Apply constraints
    let constraintMultiplier = 1.0;
    if (constraints) {
      // Apply load balancing factor
      if (constraints.loadBalancingFactor && constraints.loadBalancingFactor > 0) {
        constraintMultiplier *= (1 + constraints.loadBalancingFactor * (1 - agentMetrics.utilization));
      }
      
      // Apply priority boost
      if (constraints.priorityBoost && task.priority > 5) {
        const priorityFactor = (task.priority - 5) / 5; // 0-1 scale
        constraintMultiplier *= (1 + constraints.priorityBoost * 0.1 * priorityFactor);
      }
      
      // Apply preferred agent boost
      if (constraints.preferredAgentIds && constraints.preferredAgentIds.includes(agent.getId())) {
        constraintMultiplier *= 1.5;
      }
    }
    
    // Calculate final score
    let score = (successScore + utilizationScore + experienceScore - errorPenalty + domainBoost) * constraintMultiplier;
    
    // Ensure score is between 0 and 1
    return Math.max(0, Math.min(1, score));
  }
  
  private calculateDetailedMetrics(agent: Agent, task: Task, metrics: AgentPerformanceMetrics | undefined, constraints?: AllocationConstraints): AllocationResult['metrics'] {
    // Default metrics if none available
    const defaultMetrics: AgentPerformanceMetrics = {
      agentId: agent.getId(),
      agentType: agent.getType(),
      successRate: 0.8,
      averageTaskDuration: 60000, // 1 minute
      taskCount: 0,
      errorRate: 0.1,
      utilization: 0.5,
      lastUpdated: Date.now(),
      domainSpecificMetrics: {}
    };
    
    const agentMetrics = metrics || defaultMetrics;
    
    // Calculate match score (how well agent matches task)
    let matchScore = 0.8; // Default match score for agents of the correct type
    
    // Add domain-specific match score if available
    if (task.metadata.domain && agentMetrics.domainSpecificMetrics[task.metadata.domain]) {
      matchScore = 0.8 + 0.2 * agentMetrics.domainSpecificMetrics[task.metadata.domain];
    }
    
    // Calculate load score (higher = less loaded)
    const loadScore = 1 - agentMetrics.utilization;
    
    // Calculate performance score
    const performanceScore = agentMetrics.successRate * 0.7 + (1 - agentMetrics.errorRate) * 0.3;
    
    // Calculate priority score
    const priorityScore = task.priority / 10;
    
    return {
      matchScore,
      loadScore,
      performanceScore,
      priorityScore
    };
  }
  
  private isAgentAvailable(agent: Agent, constraints?: AllocationConstraints): boolean {
    // Check if agent is excluded
    if (constraints?.excludedAgentIds?.includes(agent.getId())) {
      return false;
    }
    
    // In a real implementation, this would check agent availability
    // For now, assume all agents are available
    return true;
  }
}

/**
 * Market-based allocation strategy
 */
export class MarketBasedStrategy implements AllocationStrategy {
  name = 'market_based';
  private performanceTracker: TaskAllocationPerformanceTracker;
  private agentRegistry: AgentRegistry;
  
  constructor(performanceTracker: TaskAllocationPerformanceTracker, agentRegistry: AgentRegistry) {
    this.performanceTracker = performanceTracker;
    this.agentRegistry = agentRegistry;
  }
  
  async allocateTasks(workflow: Workflow, tasks: Task[], constraints?: AllocationConstraints): Promise<Map<string, AllocationResult>> {
    const allocations = new Map<string, AllocationResult>();
    
    // Sort tasks by priority (highest first)
    const sortedTasks = [...tasks].sort((a, b) => b.priority - a.priority);
    
    // Step 1: Prepare the "market" by calculating bids
    const bids = new Map<string, Map<string, number>>(); // taskId -> agentId -> bid
    const allocationMetrics = new Map<string, Map<string, AllocationResult['metrics']>>(); // taskId -> agentId -> metrics
    
    for (const task of sortedTasks) {
      if (!task.agentType) continue;
      
      // Get available agents of the required type
      const agents = this.agentRegistry.getAgentsByType(task.agentType)
        .filter(agent => this.isAgentAvailable(agent, constraints));
      
      if (agents.length === 0) continue;
      
      // Get bids from agents
      const taskBids = new Map<string, number>();
      const taskMetrics = new Map<string, AllocationResult['metrics']>();
      
      for (const agent of agents) {
        // Get performance metrics for agent
        const metrics = this.performanceTracker.getAgentMetrics(agent.getId());
        
        // Calculate bid (agent score is the "bid")
        const bid = this.calculateAgentScore(agent, task, metrics, constraints);
        
        // Calculate detailed metrics
        const detailedMetrics = this.calculateDetailedMetrics(agent, task, metrics, constraints);
        
        // Store bid and metrics
        taskBids.set(agent.getId(), bid);
        taskMetrics.set(agent.getId(), detailedMetrics);
      }
      
      bids.set(task.id, taskBids);
      allocationMetrics.set(task.id, taskMetrics);
    }
    
    // Step 2: Run the auction
    const allocatedAgents = new Set<string>(); // Track allocated agents
    
    for (const task of sortedTasks) {
      const taskBids = bids.get(task.id);
      if (!taskBids || taskBids.size === 0) continue;
      
      // Find highest bidder that isn't already allocated
      let bestAgentId: string | null = null;
      let bestBid = -Infinity;
      
      for (const [agentId, bid] of taskBids.entries()) {
        // Skip agents that are already allocated (if constrained)
        if (constraints?.maxTasksPerAgent === 1 && allocatedAgents.has(agentId)) {
          continue;
        }
        
        if (bid > bestBid) {
          bestBid = bid;
          bestAgentId = agentId;
        }
      }
      
      if (bestAgentId) {
        // Create allocation result
        const result: AllocationResult = {
          taskId: task.id,
          agentId: bestAgentId,
          score: bestBid,
          metrics: allocationMetrics.get(task.id)?.get(bestAgentId) || {
            matchScore: 0,
            loadScore: 0,
            performanceScore: 0,
            priorityScore: 0
          },
          timestamp: Date.now(),
          allocatedBy: this.name
        };
        
        // Add to allocations
        allocations.set(task.id, result);
        
        // Mark agent as allocated
        allocatedAgents.add(bestAgentId);
      }
    }
    
    return allocations;
  }
  
  calculateAgentScore(agent: Agent, task: Task, metrics: AgentPerformanceMetrics | undefined, constraints?: AllocationConstraints): number {
    // Default metrics if none available
    const defaultMetrics: AgentPerformanceMetrics = {
      agentId: agent.getId(),
      agentType: agent.getType(),
      successRate: 0.8,
      averageTaskDuration: 60000, // 1 minute
      taskCount: 0,
      errorRate: 0.1,
      utilization: 0.5,
      lastUpdated: Date.now(),
      domainSpecificMetrics: {}
    };
    
    const agentMetrics = metrics || defaultMetrics;
    
    // Calculate bid components
    const qualityBid = agentMetrics.successRate * 0.35;
    const speedBid = (1 / (1 + agentMetrics.averageTaskDuration / 60000)) * 0.25; // Normalize by 1 minute
    const availabilityBid = (1 - agentMetrics.utilization) * 0.2;
    const experienceBid = Math.min(1, agentMetrics.taskCount / 100) * 0.2;
    
    // Apply task-specific factors
    let taskFactors = 1.0;
    
    // Higher priority tasks get higher bids
    taskFactors *= (0.5 + 0.1 * task.priority);
    
    // Tasks with higher expected duration get lower bids
    if (task.estimatedDuration > 0) {
      taskFactors *= (1 - Math.min(0.5, task.estimatedDuration / 300000)); // Normalize by 5 minutes
    }
    
    // Apply domain-specific boost if available
    if (task.metadata.domain && agentMetrics.domainSpecificMetrics[task.metadata.domain]) {
      taskFactors *= (1 + agentMetrics.domainSpecificMetrics[task.metadata.domain] * 0.3);
    }
    
    // Apply constraints
    if (constraints) {
      // Preferred agents bid higher
      if (constraints.preferredAgentIds?.includes(agent.getId())) {
        taskFactors *= 1.3;
      }
      
      // Apply domain priorities
      if (constraints.domainPriorities && task.metadata.domain) {
        const domainPriority = constraints.domainPriorities[task.metadata.domain] || 1;
        taskFactors *= (1 + (domainPriority - 1) * 0.1);
      }
    }
    
    // Calculate final bid
    const bid = (qualityBid + speedBid + availabilityBid + experienceBid) * taskFactors;
    
    // Ensure bid is between 0 and 1
    return Math.max(0, Math.min(1, bid));
  }
  
  private calculateDetailedMetrics(agent: Agent, task: Task, metrics: AgentPerformanceMetrics | undefined, constraints?: AllocationConstraints): AllocationResult['metrics'] {
    // Default metrics if none available
    const defaultMetrics: AgentPerformanceMetrics = {
      agentId: agent.getId(),
      agentType: agent.getType(),
      successRate: 0.8,
      averageTaskDuration: 60000, // 1 minute
      taskCount: 0,
      errorRate: 0.1,
      utilization: 0.5,
      lastUpdated: Date.now(),
      domainSpecificMetrics: {}
    };
    
    const agentMetrics = metrics || defaultMetrics;
    
    // Calculate match score based on experience in domain
    let matchScore = 0.6; // Base match for correct agent type
    if (task.metadata.domain && agentMetrics.domainSpecificMetrics[task.metadata.domain]) {
      matchScore = 0.6 + 0.4 * agentMetrics.domainSpecificMetrics[task.metadata.domain];
    } else {
      // Boost match score based on general experience
      matchScore += 0.2 * Math.min(1, agentMetrics.taskCount / 100);
    }
    
    // Calculate load score (higher = less loaded)
    const loadScore = 1 - agentMetrics.utilization;
    
    // Calculate performance score based on success and speed
    const successComponent = agentMetrics.successRate * 0.6;
    const speedComponent = (1 / (1 + agentMetrics.averageTaskDuration / 60000)) * 0.4;
    const performanceScore = successComponent + speedComponent;
    
    // Calculate priority score (0-1)
    const priorityScore = task.priority / 10;
    
    return {
      matchScore,
      loadScore,
      performanceScore,
      priorityScore
    };
  }
  
  private isAgentAvailable(agent: Agent, constraints?: AllocationConstraints): boolean {
    // Check if agent is excluded
    if (constraints?.excludedAgentIds?.includes(agent.getId())) {
      return false;
    }
    
    // Get agent metrics
    const metrics = this.performanceTracker.getAgentMetrics(agent.getId());
    
    // Check utilization constraint
    if (constraints?.maxUtilization && metrics && metrics.utilization > constraints.maxUtilization) {
      return false;
    }
    
    // Check success rate constraint
    if (constraints?.minSuccessRate && metrics && metrics.successRate < constraints.minSuccessRate) {
      return false;
    }
    
    // In a real implementation, this would check agent availability
    // For now, assume all agents are available
    return true;
  }
}

/**
 * Adaptive allocation strategy that chooses the best strategy based on context
 */
export class AdaptiveAllocationStrategy implements AllocationStrategy {
  name = 'adaptive';
  private strategies: Map<string, AllocationStrategy> = new Map();
  private performanceTracker: TaskAllocationPerformanceTracker;
  private strategyHistory: { strategy: string, score: number, timestamp: number }[] = [];
  
  constructor(performanceTracker: TaskAllocationPerformanceTracker, strategies: AllocationStrategy[]) {
    this.performanceTracker = performanceTracker;
    
    // Register strategies
    for (const strategy of strategies) {
      this.strategies.set(strategy.name, strategy);
    }
  }
  
  async allocateTasks(workflow: Workflow, tasks: Task[], constraints?: AllocationConstraints): Promise<Map<string, AllocationResult>> {
    // Select the best strategy for this workflow
    const bestStrategy = this.selectBestStrategy(workflow, tasks, constraints);
    
    // Use the selected strategy to allocate tasks
    const allocations = await bestStrategy.allocateTasks(workflow, tasks, constraints);
    
    // Record the strategy used
    this.recordStrategyUse(bestStrategy.name, allocations.size);
    
    return allocations;
  }
  
  calculateAgentScore(agent: Agent, task: Task, metrics: AgentPerformanceMetrics | undefined, constraints?: AllocationConstraints): number {
    // Select the best strategy for this task
    const bestStrategy = this.selectBestStrategyForTask(task, constraints);
    
    // Use the selected strategy to calculate the score
    return bestStrategy.calculateAgentScore(agent, task, metrics, constraints);
  }
  
  /**
   * Selects the best strategy for the given workflow and tasks
   * @param workflow Workflow
   * @param tasks Tasks to allocate
   * @param constraints Allocation constraints
   * @returns Best allocation strategy
   */
  private selectBestStrategy(workflow: Workflow, tasks: Task[], constraints?: AllocationConstraints): AllocationStrategy {
    // Strategy selection factors
    const workflowSize = workflow.tasks.size;
    const taskPriority = tasks.reduce((sum, task) => sum + task.priority, 0) / tasks.length;
    const hasConstraints = constraints !== undefined;
    const coordinationStrategy = workflow.coordinationStrategy;
    
    // Strategy scores
    const scores = new Map<string, number>();
    
    // Round Robin: Good for simple workflows with low priority and no constraints
    const roundRobinScore = 
      (workflowSize < 5 ? 0.8 : 0.4) * 
      (taskPriority < 6 ? 0.8 : 0.4) * 
      (hasConstraints ? 0.5 : 0.9);
    scores.set('round_robin', roundRobinScore);
    
    // Performance-based: Good for workflows with high priority tasks
    const performanceScore = 
      (workflowSize >= 3 ? 0.7 : 0.5) * 
      (taskPriority >= 6 ? 0.9 : 0.6) * 
      (hasConstraints ? 0.8 : 0.7);
    scores.set('performance_based', performanceScore);
    
    // Market-based: Good for complex workflows with specific coordination strategy
    const marketScore = 
      (workflowSize >= 5 ? 0.9 : 0.6) * 
      (taskPriority >= 7 ? 0.9 : 0.7) * 
      (hasConstraints ? 0.9 : 0.7) * 
      (coordinationStrategy === CoordinationStrategy.MARKET_BASED ? 1.0 : 0.8);
    scores.set('market_based', marketScore);
    
    // Find strategy with highest score
    let bestStrategy = 'round_robin';
    let bestScore = -Infinity;
    
    for (const [strategy, score] of scores.entries()) {
      if (score > bestScore && this.strategies.has(strategy)) {
        bestScore = score;
        bestStrategy = strategy;
      }
    }
    
    return this.strategies.get(bestStrategy) || this.strategies.values().next().value;
  }
  
  /**
   * Selects the best strategy for the given task
   * @param task Task
   * @param constraints Allocation constraints
   * @returns Best allocation strategy
   */
  private selectBestStrategyForTask(task: Task, constraints?: AllocationConstraints): AllocationStrategy {
    // Similar logic to selectBestStrategy but for a single task
    const taskPriority = task.priority;
    const hasConstraints = constraints !== undefined;
    
    // Strategy scores
    const scores = new Map<string, number>();
    
    // Round Robin: Good for simple tasks with low priority
    scores.set('round_robin', (taskPriority < 6 ? 0.8 : 0.4) * (hasConstraints ? 0.5 : 0.9));
    
    // Performance-based: Good for high priority tasks
    scores.set('performance_based', (taskPriority >= 6 ? 0.9 : 0.6) * (hasConstraints ? 0.8 : 0.7));
    
    // Market-based: Good for complex tasks with constraints
    scores.set('market_based', (taskPriority >= 7 ? 0.9 : 0.7) * (hasConstraints ? 0.9 : 0.7));
    
    // Find strategy with highest score
    let bestStrategy = 'round_robin';
    let bestScore = -Infinity;
    
    for (const [strategy, score] of scores.entries()) {
      if (score > bestScore && this.strategies.has(strategy)) {
        bestScore = score;
        bestStrategy = strategy;
      }
    }
    
    return this.strategies.get(bestStrategy) || this.strategies.values().next().value;
  }
  
  /**
   * Records the use of a strategy
   * @param strategyName Strategy name
   * @param taskCount Number of tasks allocated
   */
  private recordStrategyUse(strategyName: string, taskCount: number): void {
    // Add to history
    this.strategyHistory.push({
      strategy: strategyName,
      score: taskCount > 0 ? 1.0 : 0.0, // Simple score based on whether tasks were allocated
      timestamp: Date.now()
    });
    
    // Limit history size
    if (this.strategyHistory.length > 100) {
      this.strategyHistory.shift();
    }
  }
  
  /**
   * Gets strategy usage statistics
   * @returns Map of strategy names to usage counts
   */
  getStrategyUsageStats(): Map<string, { count: number, avgScore: number }> {
    const stats = new Map<string, { count: number, avgScore: number }>();
    
    // Initialize stats for all strategies
    for (const strategy of this.strategies.keys()) {
      stats.set(strategy, { count: 0, avgScore: 0 });
    }
    
    // Count strategy uses and calculate average scores
    for (const entry of this.strategyHistory) {
      const current = stats.get(entry.strategy) || { count: 0, avgScore: 0 };
      
      // Update count and running average
      const newCount = current.count + 1;
      const newAvgScore = (current.avgScore * current.count + entry.score) / newCount;
      
      stats.set(entry.strategy, { count: newCount, avgScore: newAvgScore });
    }
    
    return stats;
  }
}

/**
 * Tracks performance metrics for task allocation
 */
export class TaskAllocationPerformanceTracker {
  private metrics: Map<string, AgentPerformanceMetrics> = new Map();
  private taskHistory: Map<string, {
    agentId: string;
    startTime?: number;
    endTime?: number;
    status: TaskStatus;
    error?: Error;
  }> = new Map();
  
  /**
   * Registers a task with the performance tracker
   * @param taskId Task ID
   * @param agentId Agent ID
   */
  trackTaskAssignment(taskId: string, agentId: string): void {
    this.taskHistory.set(taskId, {
      agentId,
      status: TaskStatus.ASSIGNED
    });
  }
  
  /**
   * Updates the status of a task
   * @param taskId Task ID
   * @param status New task status
   * @param error Error if task failed
   */
  updateTaskStatus(taskId: string, status: TaskStatus, error?: Error): void {
    const task = this.taskHistory.get(taskId);
    if (!task) return;
    
    // Update task history
    const now = Date.now();
    let updatedTask = { ...task, status };
    
    if (status === TaskStatus.RUNNING && !task.startTime) {
      updatedTask.startTime = now;
    } else if ([TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED].includes(status)) {
      updatedTask.endTime = now;
      
      if (status === TaskStatus.FAILED && error) {
        updatedTask.error = error;
      }
      
      // Update agent metrics when task completes
      this.updateAgentMetrics(updatedTask.agentId, taskId, status, updatedTask.startTime, updatedTask.endTime, error);
    }
    
    this.taskHistory.set(taskId, updatedTask);
  }
  
  /**
   * Updates metrics for an agent based on task completion
   * @param agentId Agent ID
   * @param taskId Task ID
   * @param status Final task status
   * @param startTime Task start time
   * @param endTime Task end time
   * @param error Error if task failed
   */
  private updateAgentMetrics(
    agentId: string,
    taskId: string,
    status: TaskStatus,
    startTime?: number,
    endTime?: number,
    error?: Error
  ): void {
    // Get current metrics
    let metrics = this.getAgentMetrics(agentId);
    
    if (!metrics) {
      // Create new metrics
      metrics = {
        agentId,
        agentType: '',
        successRate: 1.0,
        averageTaskDuration: 0,
        taskCount: 0,
        errorRate: 0,
        utilization: 0,
        lastUpdated: Date.now(),
        domainSpecificMetrics: {}
      };
    }
    
    // Update metrics
    metrics.lastUpdated = Date.now();
    metrics.taskCount++;
    
    // Update success rate and error rate
    if (status === TaskStatus.COMPLETED) {
      // Update success rate using weighted average
      metrics.successRate = (metrics.successRate * (metrics.taskCount - 1) + 1) / metrics.taskCount;
    } else if (status === TaskStatus.FAILED) {
      // Update success rate
      metrics.successRate = (metrics.successRate * (metrics.taskCount - 1) + 0) / metrics.taskCount;
      
      // Update error rate
      metrics.errorRate = (metrics.errorRate * (metrics.taskCount - 1) + 1) / metrics.taskCount;
    }
    
    // Update average task duration
    if (startTime && endTime) {
      const duration = endTime - startTime;
      
      // Weighted average
      metrics.averageTaskDuration = (metrics.averageTaskDuration * (metrics.taskCount - 1) + duration) / metrics.taskCount;
    }
    
    // Store updated metrics
    this.setAgentMetrics(agentId, metrics);
  }
  
  /**
   * Gets metrics for an agent
   * @param agentId Agent ID
   * @returns Agent performance metrics or undefined if not found
   */
  getAgentMetrics(agentId: string): AgentPerformanceMetrics | undefined {
    return this.metrics.get(agentId);
  }
  
  /**
   * Sets metrics for an agent
   * @param agentId Agent ID
   * @param metrics Agent performance metrics
   */
  setAgentMetrics(agentId: string, metrics: AgentPerformanceMetrics): void {
    this.metrics.set(agentId, metrics);
  }
  
  /**
   * Resets metrics for an agent
   * @param agentId Agent ID
   */
  resetAgentMetrics(agentId: string): void {
    this.metrics.delete(agentId);
  }
  
  /**
   * Gets completed task count for an agent
   * @param agentId Agent ID
   * @returns Number of completed tasks
   */
  getCompletedTaskCount(agentId: string): number {
    let count = 0;
    
    for (const task of this.taskHistory.values()) {
      if (task.agentId === agentId && task.status === TaskStatus.COMPLETED) {
        count++;
      }
    }
    
    return count;
  }
  
  /**
   * Gets failed task count for an agent
   * @param agentId Agent ID
   * @returns Number of failed tasks
   */
  getFailedTaskCount(agentId: string): number {
    let count = 0;
    
    for (const task of this.taskHistory.values()) {
      if (task.agentId === agentId && task.status === TaskStatus.FAILED) {
        count++;
      }
    }
    
    return count;
  }
  
  /**
   * Gets metrics summary for all agents
   * @returns Map of agent IDs to metrics summaries
   */
  getMetricsSummary(): Map<string, { 
    taskCount: number, 
    completedCount: number, 
    failedCount: number, 
    successRate: number,
    avgDuration: number 
  }> {
    const summary = new Map<string, { 
      taskCount: number, 
      completedCount: number, 
      failedCount: number, 
      successRate: number,
      avgDuration: number 
    }>();
    
    for (const [agentId, metrics] of this.metrics.entries()) {
      const completedCount = this.getCompletedTaskCount(agentId);
      const failedCount = this.getFailedTaskCount(agentId);
      
      summary.set(agentId, {
        taskCount: metrics.taskCount,
        completedCount,
        failedCount,
        successRate: metrics.successRate,
        avgDuration: metrics.averageTaskDuration
      });
    }
    
    return summary;
  }
}

/**
 * Task allocator for assigning tasks to agents
 */
export class TaskAllocator extends EventEmitter {
  private agentRegistry: AgentRegistry;
  private performanceTracker: TaskAllocationPerformanceTracker;
  private strategies: Map<string, AllocationStrategy> = new Map();
  private defaultStrategy: AllocationStrategy;
  private adaptiveStrategy: AdaptiveAllocationStrategy;
  private isInitialized: boolean = false;
  
  constructor(agentRegistry: AgentRegistry) {
    super();
    this.agentRegistry = agentRegistry;
    this.performanceTracker = new TaskAllocationPerformanceTracker();
    
    // Create strategies
    const roundRobinStrategy = new RoundRobinStrategy();
    const performanceStrategy = new PerformanceBasedStrategy(this.performanceTracker, this.agentRegistry);
    const marketStrategy = new MarketBasedStrategy(this.performanceTracker, this.agentRegistry);
    
    // Register strategies
    this.registerStrategy(roundRobinStrategy);
    this.registerStrategy(performanceStrategy);
    this.registerStrategy(marketStrategy);
    
    // Create adaptive strategy
    this.adaptiveStrategy = new AdaptiveAllocationStrategy(
      this.performanceTracker,
      [roundRobinStrategy, performanceStrategy, marketStrategy]
    );
    this.registerStrategy(this.adaptiveStrategy);
    
    // Set default strategy
    this.defaultStrategy = this.adaptiveStrategy;
  }
  
  /**
   * Initializes the task allocator
   * @returns Promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    // Initialize performance tracker
    
    this.isInitialized = true;
    console.log('Task allocator initialized');
  }
  
  /**
   * Registers an allocation strategy
   * @param strategy Allocation strategy to register
   */
  registerStrategy(strategy: AllocationStrategy): void {
    this.strategies.set(strategy.name, strategy);
  }
  
  /**
   * Gets an allocation strategy by name
   * @param name Strategy name
   * @returns Allocation strategy or undefined if not found
   */
  getStrategy(name: string): AllocationStrategy | undefined {
    return this.strategies.get(name);
  }
  
  /**
   * Gets all registered allocation strategies
   * @returns Array of allocation strategies
   */
  getStrategies(): AllocationStrategy[] {
    return Array.from(this.strategies.values());
  }
  
  /**
   * Sets the default allocation strategy
   * @param strategyName Strategy name
   */
  setDefaultStrategy(strategyName: string): void {
    const strategy = this.strategies.get(strategyName);
    if (strategy) {
      this.defaultStrategy = strategy;
    }
  }
  
  /**
   * Allocates tasks for a workflow
   * @param workflow Workflow
   * @param tasks Tasks to allocate
   * @param strategyName Optional strategy name
   * @param constraints Optional allocation constraints
   * @returns Map of task IDs to allocation results
   */
  async allocateTasks(
    workflow: Workflow,
    tasks: Task[],
    strategyName?: string,
    constraints?: AllocationConstraints
  ): Promise<Map<string, AllocationResult>> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    // Get strategy
    const strategy = strategyName ? 
      this.strategies.get(strategyName) || this.defaultStrategy : 
      this.defaultStrategy;
    
    // Allocate tasks
    const allocations = await strategy.allocateTasks(workflow, tasks, constraints);
    
    // Track assignments
    for (const [taskId, allocation] of allocations.entries()) {
      this.performanceTracker.trackTaskAssignment(taskId, allocation.agentId);
      
      // Assign agent to task
      const task = workflow.getTask(taskId);
      if (task) {
        task.assignAgent(allocation.agentId);
      }
    }
    
    // Emit event
    this.emit('tasksAllocated', workflow, allocations);
    
    return allocations;
  }
  
  /**
   * Updates task status
   * @param taskId Task ID
   * @param status New task status
   * @param error Error if task failed
   */
  updateTaskStatus(taskId: string, status: TaskStatus, error?: Error): void {
    this.performanceTracker.updateTaskStatus(taskId, status, error);
  }
  
  /**
   * Gets performance metrics for an agent
   * @param agentId Agent ID
   * @returns Agent performance metrics or undefined if not found
   */
  getAgentMetrics(agentId: string): AgentPerformanceMetrics | undefined {
    return this.performanceTracker.getAgentMetrics(agentId);
  }
  
  /**
   * Gets metrics summary for all agents
   * @returns Map of agent IDs to metrics summaries
   */
  getMetricsSummary(): Map<string, { 
    taskCount: number, 
    completedCount: number, 
    failedCount: number, 
    successRate: number,
    avgDuration: number 
  }> {
    return this.performanceTracker.getMetricsSummary();
  }
  
  /**
   * Gets adaptive strategy usage statistics
   * @returns Map of strategy names to usage counts and scores
   */
  getStrategyUsageStats(): Map<string, { count: number, avgScore: number }> {
    return this.adaptiveStrategy.getStrategyUsageStats();
  }
}

export default TaskAllocator;