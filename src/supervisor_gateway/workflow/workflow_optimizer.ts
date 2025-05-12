/**
 * Performance optimization system for workflows
 */

import { EventEmitter } from 'events';
import { 
  Workflow, 
  Task, 
  TaskStatus, 
  WorkflowStatus,
  WorkflowExecutionMode,
  CoordinationStrategy,
  TaskType
} from './workflow_orchestrator';
import { TaskAllocator } from './task_allocator';
import { WorkflowPatternFactory } from './workflow_models';

/**
 * Performance metrics for a workflow
 */
export interface WorkflowPerformanceMetrics {
  workflowId: string;
  totalDuration: number;          // Total execution time in ms
  taskMetrics: {
    totalTasks: number;           // Total number of tasks
    completedTasks: number;       // Number of completed tasks
    failedTasks: number;          // Number of failed tasks
    averageTaskDuration: number;  // Average task duration in ms
    criticalPathDuration: number; // Duration of critical path in ms
    parallelismDegree: number;    // Average degree of parallelism
  };
  resourceMetrics: {
    agentUtilization: Map<string, number>; // Agent utilization (0-1)
    resourceEfficiency: number;            // Overall resource efficiency (0-1)
    loadBalance: number;                   // Load balance metric (0-1, higher is better)
    waitingTime: number;                   // Average waiting time in ms
  };
  qualityMetrics: {
    successRate: number;          // Task success rate (0-1)
    errorRate: number;            // Task error rate (0-1)
    completionRate: number;       // Workflow completion rate (0-1)
  };
}

/**
 * Performance bottleneck in a workflow
 */
export interface PerformanceBottleneck {
  type: 'task' | 'resource' | 'dependency' | 'communication' | 'error';
  severity: number;               // Severity (1-10)
  impact: number;                 // Impact on overall performance (0-1)
  description: string;            // Description of the bottleneck
  location: string[];             // Location of the bottleneck (task IDs or agent IDs)
  recommendations: string[];      // Recommendations for addressing the bottleneck
  metadata: Record<string, any>;  // Additional metadata
}

/**
 * Profile of a workflow execution
 */
export interface WorkflowExecutionProfile {
  workflowId: string;
  executionId: string;
  startTime: number;
  endTime?: number;
  status: WorkflowStatus;
  metrics: WorkflowPerformanceMetrics;
  bottlenecks: PerformanceBottleneck[];
  taskProfiles: Map<string, TaskExecutionProfile>;
  resourceProfiles: Map<string, ResourceUsageProfile>;
}

/**
 * Profile of a task execution
 */
export interface TaskExecutionProfile {
  taskId: string;
  startTime?: number;
  endTime?: number;
  agentId?: string;
  status: TaskStatus;
  duration?: number;
  waitTime?: number;
  processingTime?: number;
  dependencies: {
    id: string;
    type: 'data' | 'control';
    impact: number;
  }[];
  metrics: {
    efficiency: number;           // Task processing efficiency (0-1)
    criticalPathContribution: number; // Contribution to critical path (0-1)
    resourceUsage: number;        // Resource usage (0-1)
    errorRate: number;            // Error rate (0-1)
  };
}

/**
 * Profile of resource usage
 */
export interface ResourceUsageProfile {
  resourceId: string;
  resourceType: string;
  utilization: number;            // Resource utilization (0-1)
  taskAllocation: {
    taskId: string;
    startTime: number;
    endTime?: number;
    utilizationLevel: number;     // Utilization level for this task (0-1)
  }[];
  metrics: {
    efficiency: number;           // Resource usage efficiency (0-1)
    contention: number;           // Resource contention level (0-1)
    idleTime: number;             // Idle time in ms
    overloadTime: number;         // Overload time in ms
  };
}

/**
 * Options for workflow optimization
 */
export interface OptimizationOptions {
  optimizationGoal: 'performance' | 'resource_efficiency' | 'reliability' | 'balanced';
  constraints: {
    maxDuration?: number;         // Maximum acceptable duration in ms
    maxResourceUsage?: number;    // Maximum resource usage (0-1)
    minSuccessRate?: number;      // Minimum success rate (0-1)
    maxParallelism?: number;      // Maximum degree of parallelism
  };
  preferences: {
    parallelizationPreference?: number; // Preference for parallelization (0-1)
    resourceBalancePreference?: number; // Preference for resource balance (0-1)
    reliabilityPreference?: number;     // Preference for reliability (0-1)
    taskPriorityWeight?: number;        // Weight for task priority (0-1)
  };
  optimizationLevel: 'light' | 'moderate' | 'aggressive'; // How aggressive to be with changes
  excludedTaskIds?: string[];     // Tasks to exclude from optimization
  preserveTaskOrder?: boolean;    // Whether to preserve task order
  allowReallocations?: boolean;   // Whether to allow reallocation of tasks
}

/**
 * Result of workflow optimization
 */
export interface OptimizationResult {
  workflowId: string;
  originalWorkflow: Workflow;
  optimizedWorkflow: Workflow;
  optimizationId: string;
  changes: {
    taskReordering: {
      taskId: string;
      originalIndex: number;
      newIndex: number;
    }[];
    taskParallelization: {
      taskId: string;
      parallelizedWith: string[];
    }[];
    resourceReallocations: {
      taskId: string;
      originalResourceId?: string;
      newResourceId: string;
    }[];
    structuralChanges: {
      type: 'split' | 'merge' | 'insert' | 'remove';
      description: string;
      affectedTaskIds: string[];
    }[];
  };
  expectedImprovements: {
    durationReduction: number;    // Expected reduction in duration (%)
    resourceEfficiencyGain: number; // Expected gain in resource efficiency (%)
    reliabilityIncrease: number;  // Expected increase in reliability (%)
    overallImprovement: number;   // Overall improvement (%)
  };
  bottlenecksResolved: PerformanceBottleneck[];
  bottlenecksRemaining: PerformanceBottleneck[];
  recommendations: string[];
}

/**
 * Optimization strategy for workflows
 */
export interface OptimizationStrategy {
  name: string;
  description: string;
  optimize(workflow: Workflow, executionProfile: WorkflowExecutionProfile, options: OptimizationOptions): Promise<OptimizationResult>;
}

/**
 * Parallelization optimization strategy
 */
export class ParallelizationStrategy implements OptimizationStrategy {
  name = 'parallelization';
  description = 'Identifies tasks that can be executed in parallel to reduce overall execution time';
  
  async optimize(workflow: Workflow, executionProfile: WorkflowExecutionProfile, options: OptimizationOptions): Promise<OptimizationResult> {
    // Clone workflow for optimization
    const optimizedWorkflow = this.cloneWorkflow(workflow);
    
    // Find parallelization opportunities
    const parallelizationOpportunities = this.findParallelizationOpportunities(workflow, executionProfile);
    
    // Apply parallelization based on constraints and preferences
    const taskParallelization = this.applyParallelization(
      parallelizationOpportunities, 
      optimizedWorkflow, 
      options
    );
    
    // Update workflow execution mode if needed
    if (taskParallelization.length > 0 && 
        optimizedWorkflow.executionMode === WorkflowExecutionMode.SEQUENTIAL) {
      optimizedWorkflow.executionMode = WorkflowExecutionMode.HYBRID;
    }
    
    // Calculate expected improvements
    const expectedImprovements = this.calculateExpectedImprovements(
      workflow, 
      optimizedWorkflow, 
      executionProfile, 
      taskParallelization
    );
    
    // Identify resolved bottlenecks
    const { bottlenecksResolved, bottlenecksRemaining } = this.identifyResolvedBottlenecks(
      executionProfile.bottlenecks,
      taskParallelization
    );
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(
      bottlenecksResolved,
      bottlenecksRemaining,
      expectedImprovements
    );
    
    // Create optimization result
    return {
      workflowId: workflow.id,
      originalWorkflow: workflow,
      optimizedWorkflow,
      optimizationId: `parallelization_${Date.now()}`,
      changes: {
        taskReordering: [],
        taskParallelization,
        resourceReallocations: [],
        structuralChanges: []
      },
      expectedImprovements,
      bottlenecksResolved,
      bottlenecksRemaining,
      recommendations
    };
  }
  
  /**
   * Clones a workflow
   * @param workflow Workflow to clone
   * @returns Cloned workflow
   */
  private cloneWorkflow(workflow: Workflow): Workflow {
    // Create new workflow with same options
    const options = {
      name: workflow.name,
      description: workflow.description,
      executionMode: workflow.executionMode,
      coordinationStrategy: workflow.coordinationStrategy,
      timeout: workflow.timeout,
      maxRetries: workflow.maxRetries,
      priority: workflow.priority,
      requiredAgentTypes: [...workflow.requiredAgentTypes],
      knowledgeBaseScope: [...workflow.knowledgeBaseScope],
      metadata: { ...workflow.metadata },
      tags: [...workflow.tags]
    };
    
    const clonedWorkflow = new Workflow(options);
    
    // Clone all tasks
    const taskIdMap = new Map<string, string>();
    
    for (const task of workflow.tasks.values()) {
      // Clone task
      const clonedTask = new Task({
        name: task.name,
        description: task.description,
        type: task.type,
        agentType: task.agentType,
        agentId: task.agentId,
        inputMapping: { ...task.inputMapping },
        outputMapping: { ...task.outputMapping },
        timeout: task.timeout,
        retries: task.maxRetries,
        condition: task.condition ? { ...task.condition } : undefined,
        metadata: { ...task.metadata },
        priority: task.priority,
        subtasks: [],
        dependencies: [],
        fallbackTaskId: undefined,
        estimatedDuration: task.estimatedDuration,
        knowledgeBaseRequirements: [...task.knowledgeBaseRequirements],
        resourceRequirements: { ...task.resourceRequirements }
      });
      
      // Add to workflow
      clonedWorkflow.addTask(clonedTask);
      
      // Map original task ID to cloned task ID
      taskIdMap.set(task.id, clonedTask.id);
    }
    
    // Update task references
    for (const [originalId, clonedId] of taskIdMap.entries()) {
      const originalTask = workflow.getTask(originalId);
      const clonedTask = clonedWorkflow.getTask(clonedId);
      
      if (originalTask && clonedTask) {
        // Update dependencies
        clonedTask.dependencies = originalTask.dependencies
          .map(depId => taskIdMap.get(depId))
          .filter(Boolean) as string[];
        
        // Update subtasks
        clonedTask.subtasks = originalTask.subtasks
          .map(subId => taskIdMap.get(subId))
          .filter(Boolean) as string[];
        
        // Update fallback task
        if (originalTask.fallbackTaskId) {
          clonedTask.fallbackTaskId = taskIdMap.get(originalTask.fallbackTaskId);
        }
      }
    }
    
    return clonedWorkflow;
  }
  
  /**
   * Finds parallelization opportunities in a workflow
   * @param workflow Workflow to analyze
   * @param executionProfile Workflow execution profile
   * @returns Parallelization opportunities
   */
  private findParallelizationOpportunities(workflow: Workflow, executionProfile: WorkflowExecutionProfile): { 
    taskGroup: string[]; 
    estimatedSpeedup: number;
    dependenciesModified: boolean;
  }[] {
    const opportunities: { 
      taskGroup: string[]; 
      estimatedSpeedup: number;
      dependenciesModified: boolean;
    }[] = [];
    
    // Get tasks by execution order
    const tasksByExecutionOrder = this.getTasksByExecutionOrder(workflow, executionProfile);
    
    // Find independent tasks that can be executed in parallel
    for (let i = 0; i < tasksByExecutionOrder.length; i++) {
      const taskGroup: string[] = [tasksByExecutionOrder[i]];
      let dependenciesModified = false;
      
      // Check subsequent tasks for independence
      for (let j = i + 1; j < tasksByExecutionOrder.length; j++) {
        const candidateId = tasksByExecutionOrder[j];
        const candidate = workflow.getTask(candidateId);
        
        if (!candidate) continue;
        
        // Check if candidate depends on any task in the group
        const dependsOnGroup = candidate.dependencies.some(depId => taskGroup.includes(depId));
        
        // Check if any task in the group depends on the candidate
        const groupDependsOnCandidate = taskGroup.some(groupTaskId => {
          const groupTask = workflow.getTask(groupTaskId);
          return groupTask?.dependencies.includes(candidateId) || false;
        });
        
        // Check for data dependencies
        const hasDataDependency = this.hasDataDependency(workflow, taskGroup, candidateId);
        
        // If independent, add to group
        if (!dependsOnGroup && !groupDependsOnCandidate && !hasDataDependency) {
          taskGroup.push(candidateId);
        } 
        // If dependent but might be parallelizable with changes
        else if (!groupDependsOnCandidate && !hasDataDependency && taskGroup.length < 3) {
          // This would require modifying dependencies
          dependenciesModified = true;
          taskGroup.push(candidateId);
        }
      }
      
      // If we found a group of at least 2 tasks, add as an opportunity
      if (taskGroup.length >= 2) {
        // Calculate estimated speedup
        const estimatedSpeedup = this.calculateParallelizationSpeedup(workflow, executionProfile, taskGroup);
        
        opportunities.push({
          taskGroup,
          estimatedSpeedup,
          dependenciesModified
        });
        
        // Skip tasks that are already in this group
        i += taskGroup.length - 1;
      }
    }
    
    // Sort opportunities by estimated speedup (highest first)
    opportunities.sort((a, b) => b.estimatedSpeedup - a.estimatedSpeedup);
    
    return opportunities;
  }
  
  /**
   * Checks if there is a data dependency between a task group and a candidate task
   * @param workflow Workflow to check
   * @param taskGroup Group of task IDs
   * @param candidateId Candidate task ID
   * @returns True if there is a data dependency, false otherwise
   */
  private hasDataDependency(workflow: Workflow, taskGroup: string[], candidateId: string): boolean {
    const candidate = workflow.getTask(candidateId);
    if (!candidate) return false;
    
    // Check for input/output mappings that indicate data dependencies
    for (const groupTaskId of taskGroup) {
      const groupTask = workflow.getTask(groupTaskId);
      if (!groupTask) continue;
      
      // Check if candidate input depends on group task output
      for (const [candidateInput, candidateContextKey] of Object.entries(candidate.inputMapping)) {
        for (const [_, groupContextKey] of Object.entries(groupTask.outputMapping)) {
          if (candidateContextKey === groupContextKey) {
            return true;
          }
        }
      }
      
      // Check if group task input depends on candidate output
      for (const [groupInput, groupContextKey] of Object.entries(groupTask.inputMapping)) {
        for (const [_, candidateContextKey] of Object.entries(candidate.outputMapping)) {
          if (groupContextKey === candidateContextKey) {
            return true;
          }
        }
      }
    }
    
    return false;
  }
  
  /**
   * Gets tasks ordered by execution order
   * @param workflow Workflow to analyze
   * @param executionProfile Workflow execution profile
   * @returns Array of task IDs in execution order
   */
  private getTasksByExecutionOrder(workflow: Workflow, executionProfile: WorkflowExecutionProfile): string[] {
    // If we have execution profile with start times, use that
    if (executionProfile && executionProfile.taskProfiles.size > 0) {
      const taskProfiles = Array.from(executionProfile.taskProfiles.entries());
      
      // Sort by start time
      taskProfiles.sort((a, b) => {
        const aStart = a[1].startTime || 0;
        const bStart = b[1].startTime || 0;
        return aStart - bStart;
      });
      
      return taskProfiles.map(([taskId]) => taskId);
    }
    
    // Otherwise, use topological sort
    return this.topologicalSort(workflow);
  }
  
  /**
   * Performs a topological sort of the workflow tasks
   * @param workflow Workflow to sort
   * @returns Array of task IDs in topological order
   */
  private topologicalSort(workflow: Workflow): string[] {
    const result: string[] = [];
    const visited = new Set<string>();
    const temporaryMark = new Set<string>();
    
    // Helper function for DFS
    const visit = (taskId: string): void => {
      // Check for cycles
      if (temporaryMark.has(taskId)) {
        return; // Cycle detected, skip
      }
      
      // Skip if already visited
      if (visited.has(taskId)) {
        return;
      }
      
      // Mark temporarily
      temporaryMark.add(taskId);
      
      // Visit dependencies
      const task = workflow.getTask(taskId);
      if (task) {
        for (const dependencyId of task.dependencies) {
          visit(dependencyId);
        }
      }
      
      // Mark as visited
      visited.add(taskId);
      temporaryMark.delete(taskId);
      
      // Add to result
      result.push(taskId);
    };
    
    // Visit all tasks
    for (const taskId of workflow.tasks.keys()) {
      if (!visited.has(taskId)) {
        visit(taskId);
      }
    }
    
    return result.reverse();
  }
  
  /**
   * Calculates the estimated speedup from parallelizing a group of tasks
   * @param workflow Workflow to analyze
   * @param executionProfile Workflow execution profile
   * @param taskGroup Group of task IDs
   * @returns Estimated speedup factor
   */
  private calculateParallelizationSpeedup(workflow: Workflow, executionProfile: WorkflowExecutionProfile, taskGroup: string[]): number {
    // Calculate total sequential execution time
    let sequentialTime = 0;
    let maxParallelTime = 0;
    
    for (const taskId of taskGroup) {
      const task = workflow.getTask(taskId);
      if (!task) continue;
      
      // Get task duration from profile if available, otherwise use estimate
      let taskDuration: number;
      
      if (executionProfile.taskProfiles.has(taskId)) {
        const profile = executionProfile.taskProfiles.get(taskId)!;
        taskDuration = profile.duration || task.estimatedDuration || 60000; // Default to 1 minute
      } else {
        taskDuration = task.estimatedDuration || 60000; // Default to 1 minute
      }
      
      sequentialTime += taskDuration;
      maxParallelTime = Math.max(maxParallelTime, taskDuration);
    }
    
    // Calculate parallelization overhead (communication, coordination)
    const overhead = 0.1 * sequentialTime; // Assume 10% overhead
    
    // Calculate parallel execution time (max task time + overhead)
    const parallelTime = maxParallelTime + overhead;
    
    // Calculate speedup
    const speedup = sequentialTime / parallelTime;
    
    return speedup;
  }
  
  /**
   * Applies parallelization to a workflow
   * @param opportunities Parallelization opportunities
   * @param workflow Workflow to optimize
   * @param options Optimization options
   * @returns Applied parallelization changes
   */
  private applyParallelization(
    opportunities: { taskGroup: string[]; estimatedSpeedup: number; dependenciesModified: boolean }[],
    workflow: Workflow,
    options: OptimizationOptions
  ): { taskId: string; parallelizedWith: string[] }[] {
    const applied: { taskId: string; parallelizedWith: string[] }[] = [];
    
    // Determine how many opportunities to apply based on optimization level
    let numToApply: number;
    switch (options.optimizationLevel) {
      case 'light':
        numToApply = Math.min(1, opportunities.length);
        break;
      case 'moderate':
        numToApply = Math.min(Math.ceil(opportunities.length / 2), opportunities.length);
        break;
      case 'aggressive':
        numToApply = opportunities.length;
        break;
      default:
        numToApply = Math.min(1, opportunities.length);
    }
    
    // Apply parallelization
    for (let i = 0; i < numToApply; i++) {
      const opportunity = opportunities[i];
      
      // Skip if we would exceed max parallelism
      const currentParallelism = this.calculateCurrentParallelism(workflow, applied);
      if (
        options.constraints.maxParallelism !== undefined && 
        currentParallelism + opportunity.taskGroup.length > options.constraints.maxParallelism
      ) {
        continue;
      }
      
      // Skip if any task is excluded
      if (
        options.excludedTaskIds && 
        opportunity.taskGroup.some(taskId => options.excludedTaskIds?.includes(taskId))
      ) {
        continue;
      }
      
      // Apply the parallelization
      const mainTask = opportunity.taskGroup[0];
      const parallelTasks = opportunity.taskGroup.slice(1);
      
      // Modify task types
      const mainTaskObj = workflow.getTask(mainTask);
      if (mainTaskObj) {
        mainTaskObj.type = TaskType.PARALLEL;
      }
      
      for (const parallelTaskId of parallelTasks) {
        const parallelTask = workflow.getTask(parallelTaskId);
        if (parallelTask) {
          parallelTask.type = TaskType.PARALLEL;
          
          // If dependencies need to be modified, remove dependencies between group members
          if (opportunity.dependenciesModified) {
            parallelTask.dependencies = parallelTask.dependencies.filter(
              depId => !opportunity.taskGroup.includes(depId)
            );
          }
        }
      }
      
      // Record the parallelization
      applied.push({
        taskId: mainTask,
        parallelizedWith: parallelTasks
      });
    }
    
    return applied;
  }
  
  /**
   * Calculates the current parallelism degree in a workflow
   * @param workflow Workflow to analyze
   * @param applied Applied parallelization changes
   * @returns Current parallelism degree
   */
  private calculateCurrentParallelism(
    workflow: Workflow,
    applied: { taskId: string; parallelizedWith: string[] }[]
  ): number {
    // Count tasks that are already parallel
    let parallelTaskCount = 0;
    
    for (const task of workflow.tasks.values()) {
      if (task.type === TaskType.PARALLEL) {
        parallelTaskCount++;
      }
    }
    
    // Add tasks that will be parallelized
    for (const change of applied) {
      parallelTaskCount += change.parallelizedWith.length;
    }
    
    return parallelTaskCount;
  }
  
  /**
   * Calculates expected improvements from optimization
   * @param originalWorkflow Original workflow
   * @param optimizedWorkflow Optimized workflow
   * @param executionProfile Workflow execution profile
   * @param parallelization Applied parallelization changes
   * @returns Expected improvements
   */
  private calculateExpectedImprovements(
    originalWorkflow: Workflow,
    optimizedWorkflow: Workflow,
    executionProfile: WorkflowExecutionProfile,
    parallelization: { taskId: string; parallelizedWith: string[] }[]
  ): OptimizationResult['expectedImprovements'] {
    // Calculate speedup from parallelization
    let totalSequentialTime = 0;
    let totalParallelTime = 0;
    let totalOverhead = 0;
    
    for (const change of parallelization) {
      const taskGroup = [change.taskId, ...change.parallelizedWith];
      
      // Calculate sequential time
      let sequentialTime = 0;
      let maxParallelTime = 0;
      
      for (const taskId of taskGroup) {
        const task = originalWorkflow.getTask(taskId);
        if (!task) continue;
        
        // Get task duration from profile if available, otherwise use estimate
        let taskDuration: number;
        
        if (executionProfile.taskProfiles.has(taskId)) {
          const profile = executionProfile.taskProfiles.get(taskId)!;
          taskDuration = profile.duration || task.estimatedDuration || 60000;
        } else {
          taskDuration = task.estimatedDuration || 60000;
        }
        
        sequentialTime += taskDuration;
        maxParallelTime = Math.max(maxParallelTime, taskDuration);
      }
      
      // Calculate overhead
      const overhead = 0.1 * sequentialTime;
      
      totalSequentialTime += sequentialTime;
      totalParallelTime += maxParallelTime;
      totalOverhead += overhead;
    }
    
    // Calculate duration reduction percentage
    const originalDuration = executionProfile.metrics.totalDuration;
    const nonParallelizedDuration = originalDuration - totalSequentialTime;
    const optimizedDuration = nonParallelizedDuration + totalParallelTime + totalOverhead;
    
    const durationReduction = ((originalDuration - optimizedDuration) / originalDuration) * 100;
    
    // Calculate resource efficiency change
    // Parallelization often decreases resource efficiency due to overhead
    const resourceEfficiencyChange = -5; // Assume 5% decrease
    
    // Calculate reliability impact
    // Parallelization can slightly decrease reliability due to increased complexity
    const reliabilityChange = -2; // Assume 2% decrease
    
    // Calculate overall improvement
    // Weight duration reduction more heavily since that's the main goal
    const overallImprovement = durationReduction * 0.7 + resourceEfficiencyChange * 0.15 + reliabilityChange * 0.15;
    
    return {
      durationReduction: Math.max(0, durationReduction),
      resourceEfficiencyGain: resourceEfficiencyChange,
      reliabilityIncrease: reliabilityChange,
      overallImprovement: Math.max(0, overallImprovement)
    };
  }
  
  /**
   * Identifies bottlenecks that would be resolved by optimization
   * @param bottlenecks Original bottlenecks
   * @param parallelization Applied parallelization changes
   * @returns Resolved and remaining bottlenecks
   */
  private identifyResolvedBottlenecks(
    bottlenecks: PerformanceBottleneck[],
    parallelization: { taskId: string; parallelizedWith: string[] }[]
  ): { bottlenecksResolved: PerformanceBottleneck[]; bottlenecksRemaining: PerformanceBottleneck[] } {
    const bottlenecksResolved: PerformanceBottleneck[] = [];
    const bottlenecksRemaining: PerformanceBottleneck[] = [];
    
    // Determine which bottlenecks would be resolved
    const parallelizedTaskIds = new Set<string>();
    for (const change of parallelization) {
      parallelizedTaskIds.add(change.taskId);
      for (const taskId of change.parallelizedWith) {
        parallelizedTaskIds.add(taskId);
      }
    }
    
    for (const bottleneck of bottlenecks) {
      // Check if bottleneck is resolved by parallelization
      if (
        (bottleneck.type === 'task' || bottleneck.type === 'dependency') &&
        bottleneck.location.some(loc => parallelizedTaskIds.has(loc))
      ) {
        bottlenecksResolved.push(bottleneck);
      } else {
        bottlenecksRemaining.push(bottleneck);
      }
    }
    
    return { bottlenecksResolved, bottlenecksRemaining };
  }
  
  /**
   * Generates recommendations based on optimization results
   * @param resolvedBottlenecks Bottlenecks that were resolved
   * @param remainingBottlenecks Bottlenecks that remain
   * @param improvements Expected improvements
   * @returns Array of recommendations
   */
  private generateRecommendations(
    resolvedBottlenecks: PerformanceBottleneck[],
    remainingBottlenecks: PerformanceBottleneck[],
    improvements: OptimizationResult['expectedImprovements']
  ): string[] {
    const recommendations: string[] = [];
    
    // Add recommendations based on improvements
    if (improvements.durationReduction > 10) {
      recommendations.push(
        `Apply parallelization to reduce workflow duration by approximately ${Math.round(improvements.durationReduction)}%.`
      );
    } else if (improvements.durationReduction > 0) {
      recommendations.push(
        `Consider applying parallelization for a modest improvement of ${Math.round(improvements.durationReduction)}% in workflow duration.`
      );
    } else {
      recommendations.push(
        'Parallelization provides minimal performance benefits for this workflow. Consider other optimization strategies.'
      );
    }
    
    // Add recommendations based on resource efficiency
    if (improvements.resourceEfficiencyGain < -5) {
      recommendations.push(
        'Be aware that parallelization may decrease resource efficiency due to overhead. Consider monitoring resource usage.'
      );
    }
    
    // Add recommendations based on remaining bottlenecks
    if (remainingBottlenecks.length > 0) {
      // Group bottlenecks by type
      const bottlenecksByType = new Map<string, PerformanceBottleneck[]>();
      
      for (const bottleneck of remainingBottlenecks) {
        if (!bottlenecksByType.has(bottleneck.type)) {
          bottlenecksByType.set(bottleneck.type, []);
        }
        bottlenecksByType.get(bottleneck.type)?.push(bottleneck);
      }
      
      // Add recommendations for each type
      if (bottlenecksByType.has('resource')) {
        recommendations.push(
          'Consider optimizing resource allocation to address remaining resource bottlenecks.'
        );
      }
      
      if (bottlenecksByType.has('communication')) {
        recommendations.push(
          'Optimize communication patterns to reduce overhead in the parallelized workflow.'
        );
      }
      
      if (bottlenecksByType.has('error')) {
        recommendations.push(
          'Address error-prone tasks to improve overall workflow reliability.'
        );
      }
    }
    
    return recommendations;
  }
}

/**
 * Resource optimization strategy
 */
export class ResourceOptimizationStrategy implements OptimizationStrategy {
  name = 'resource_optimization';
  description = 'Optimizes resource allocation to improve resource utilization and efficiency';
  
  async optimize(workflow: Workflow, executionProfile: WorkflowExecutionProfile, options: OptimizationOptions): Promise<OptimizationResult> {
    // Clone workflow for optimization
    const optimizedWorkflow = this.cloneWorkflow(workflow);
    
    // Find resource optimization opportunities
    const resourceOpportunities = this.findResourceOpportunities(workflow, executionProfile);
    
    // Apply resource optimizations
    const resourceReallocations = this.applyResourceOptimizations(
      resourceOpportunities,
      optimizedWorkflow,
      options
    );
    
    // Calculate expected improvements
    const expectedImprovements = this.calculateExpectedImprovements(
      workflow,
      optimizedWorkflow,
      executionProfile,
      resourceReallocations
    );
    
    // Identify resolved bottlenecks
    const { bottlenecksResolved, bottlenecksRemaining } = this.identifyResolvedBottlenecks(
      executionProfile.bottlenecks,
      resourceReallocations
    );
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(
      bottlenecksResolved,
      bottlenecksRemaining,
      expectedImprovements
    );
    
    // Create optimization result
    return {
      workflowId: workflow.id,
      originalWorkflow: workflow,
      optimizedWorkflow,
      optimizationId: `resource_opt_${Date.now()}`,
      changes: {
        taskReordering: [],
        taskParallelization: [],
        resourceReallocations,
        structuralChanges: []
      },
      expectedImprovements,
      bottlenecksResolved,
      bottlenecksRemaining,
      recommendations
    };
  }
  
  /**
   * Clones a workflow
   * @param workflow Workflow to clone
   * @returns Cloned workflow
   */
  private cloneWorkflow(workflow: Workflow): Workflow {
    // Create new workflow with same options
    const options = {
      name: workflow.name,
      description: workflow.description,
      executionMode: workflow.executionMode,
      coordinationStrategy: workflow.coordinationStrategy,
      timeout: workflow.timeout,
      maxRetries: workflow.maxRetries,
      priority: workflow.priority,
      requiredAgentTypes: [...workflow.requiredAgentTypes],
      knowledgeBaseScope: [...workflow.knowledgeBaseScope],
      metadata: { ...workflow.metadata },
      tags: [...workflow.tags]
    };
    
    const clonedWorkflow = new Workflow(options);
    
    // Clone all tasks
    const taskIdMap = new Map<string, string>();
    
    for (const task of workflow.tasks.values()) {
      // Clone task
      const clonedTask = new Task({
        name: task.name,
        description: task.description,
        type: task.type,
        agentType: task.agentType,
        agentId: task.agentId,
        inputMapping: { ...task.inputMapping },
        outputMapping: { ...task.outputMapping },
        timeout: task.timeout,
        retries: task.maxRetries,
        condition: task.condition ? { ...task.condition } : undefined,
        metadata: { ...task.metadata },
        priority: task.priority,
        subtasks: [],
        dependencies: [],
        fallbackTaskId: undefined,
        estimatedDuration: task.estimatedDuration,
        knowledgeBaseRequirements: [...task.knowledgeBaseRequirements],
        resourceRequirements: { ...task.resourceRequirements }
      });
      
      // Add to workflow
      clonedWorkflow.addTask(clonedTask);
      
      // Map original task ID to cloned task ID
      taskIdMap.set(task.id, clonedTask.id);
    }
    
    // Update task references
    for (const [originalId, clonedId] of taskIdMap.entries()) {
      const originalTask = workflow.getTask(originalId);
      const clonedTask = clonedWorkflow.getTask(clonedId);
      
      if (originalTask && clonedTask) {
        // Update dependencies
        clonedTask.dependencies = originalTask.dependencies
          .map(depId => taskIdMap.get(depId))
          .filter(Boolean) as string[];
        
        // Update subtasks
        clonedTask.subtasks = originalTask.subtasks
          .map(subId => taskIdMap.get(subId))
          .filter(Boolean) as string[];
        
        // Update fallback task
        if (originalTask.fallbackTaskId) {
          clonedTask.fallbackTaskId = taskIdMap.get(originalTask.fallbackTaskId);
        }
      }
    }
    
    return clonedWorkflow;
  }
  
  /**
   * Finds resource optimization opportunities
   * @param workflow Workflow to analyze
   * @param executionProfile Workflow execution profile
   * @returns Resource optimization opportunities
   */
  private findResourceOpportunities(workflow: Workflow, executionProfile: WorkflowExecutionProfile): {
    taskId: string;
    currentResourceId?: string;
    candidateResourceIds: string[];
    estimatedImprovement: number;
  }[] {
    const opportunities: {
      taskId: string;
      currentResourceId?: string;
      candidateResourceIds: string[];
      estimatedImprovement: number;
    }[] = [];
    
    // Get resource profiles
    const resourceProfiles = executionProfile.resourceProfiles;
    
    // Find overloaded and underutilized resources
    const overloadedResources = new Map<string, number>(); // resourceId -> utilization
    const underutilizedResources = new Map<string, number>(); // resourceId -> utilization
    
    for (const [resourceId, profile] of resourceProfiles.entries()) {
      if (profile.utilization > 0.8) {
        overloadedResources.set(resourceId, profile.utilization);
      } else if (profile.utilization < 0.4) {
        underutilizedResources.set(resourceId, profile.utilization);
      }
    }
    
    // Find tasks on overloaded resources
    for (const [resourceId, utilization] of overloadedResources.entries()) {
      // Get tasks assigned to this resource
      const tasks = this.getTasksForResource(workflow, resourceId);
      
      // For each task, find candidate resources
      for (const taskId of tasks) {
        const task = workflow.getTask(taskId);
        if (!task) continue;
        
        // Find compatible resources with lower utilization
        const candidateResourceIds: string[] = [];
        
        for (const [candidateId, candidateUtilization] of underutilizedResources.entries()) {
          // Check if resource is compatible with task
          if (this.isResourceCompatibleWithTask(candidateId, task)) {
            candidateResourceIds.push(candidateId);
          }
        }
        
        if (candidateResourceIds.length > 0) {
          // Calculate estimated improvement
          const currentUtilization = utilization;
          const avgCandidateUtilization = candidateResourceIds.reduce(
            (sum, id) => sum + (underutilizedResources.get(id) || 0), 
            0
          ) / candidateResourceIds.length;
          
          const utilizationDiff = currentUtilization - avgCandidateUtilization;
          const estimatedImprovement = utilizationDiff * 0.5; // Scale to 0-1
          
          opportunities.push({
            taskId,
            currentResourceId: resourceId,
            candidateResourceIds,
            estimatedImprovement
          });
        }
      }
    }
    
    // Find tasks without resource profiles (might be assigned suboptimally)
    for (const task of workflow.tasks.values()) {
      // Skip tasks that are already in opportunities
      if (opportunities.some(o => o.taskId === task.id)) {
        continue;
      }
      
      // Skip tasks without assigned agents
      if (!task.assignedAgentId) {
        continue;
      }
      
      // Find compatible resources with low utilization
      const candidateResourceIds: string[] = [];
      
      for (const [candidateId, candidateUtilization] of underutilizedResources.entries()) {
        // Check if resource is compatible with task
        if (this.isResourceCompatibleWithTask(candidateId, task)) {
          candidateResourceIds.push(candidateId);
        }
      }
      
      if (candidateResourceIds.length > 0) {
        // Estimate improvement - lower for tasks without known issues
        const estimatedImprovement = 0.2; // Modest improvement
        
        opportunities.push({
          taskId: task.id,
          currentResourceId: task.assignedAgentId,
          candidateResourceIds,
          estimatedImprovement
        });
      }
    }
    
    // Sort opportunities by estimated improvement (highest first)
    opportunities.sort((a, b) => b.estimatedImprovement - a.estimatedImprovement);
    
    return opportunities;
  }
  
  /**
   * Gets tasks assigned to a resource
   * @param workflow Workflow to check
   * @param resourceId Resource ID
   * @returns Array of task IDs assigned to the resource
   */
  private getTasksForResource(workflow: Workflow, resourceId: string): string[] {
    const taskIds: string[] = [];
    
    for (const task of workflow.tasks.values()) {
      if (task.assignedAgentId === resourceId) {
        taskIds.push(task.id);
      }
    }
    
    return taskIds;
  }
  
  /**
   * Checks if a resource is compatible with a task
   * @param resourceId Resource ID
   * @param task Task to check
   * @returns True if compatible, false otherwise
   */
  private isResourceCompatibleWithTask(resourceId: string, task: Task): boolean {
    // In a real implementation, this would check resource capabilities
    // For now, assume resources are compatible if they match the agent type
    
    // Extract agent type from resource ID (assuming format agent_[type]_[id])
    const match = resourceId.match(/^agent_([^_]+)/);
    if (match && match[1] === task.agentType) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Applies resource optimizations to a workflow
   * @param opportunities Resource optimization opportunities
   * @param workflow Workflow to optimize
   * @param options Optimization options
   * @returns Applied resource reallocations
   */
  private applyResourceOptimizations(
    opportunities: {
      taskId: string;
      currentResourceId?: string;
      candidateResourceIds: string[];
      estimatedImprovement: number;
    }[],
    workflow: Workflow,
    options: OptimizationOptions
  ): { taskId: string; originalResourceId?: string; newResourceId: string }[] {
    const reallocations: { taskId: string; originalResourceId?: string; newResourceId: string }[] = [];
    
    // Skip if reallocations are not allowed
    if (options.allowReallocations === false) {
      return reallocations;
    }
    
    // Determine how many opportunities to apply based on optimization level
    let numToApply: number;
    switch (options.optimizationLevel) {
      case 'light':
        numToApply = Math.min(1, opportunities.length);
        break;
      case 'moderate':
        numToApply = Math.min(Math.ceil(opportunities.length / 2), opportunities.length);
        break;
      case 'aggressive':
        numToApply = opportunities.length;
        break;
      default:
        numToApply = Math.min(1, opportunities.length);
    }
    
    // Apply resource optimizations
    const resourceUtilization = new Map<string, number>(); // Track utilization changes
    
    for (let i = 0; i < numToApply; i++) {
      const opportunity = opportunities[i];
      
      // Skip if task is excluded
      if (options.excludedTaskIds?.includes(opportunity.taskId)) {
        continue;
      }
      
      // Choose best candidate resource
      const bestCandidateId = this.chooseBestResource(
        opportunity.candidateResourceIds,
        resourceUtilization
      );
      
      if (bestCandidateId) {
        // Update task
        const task = workflow.getTask(opportunity.taskId);
        if (task) {
          // Store original resource
          const originalResourceId = task.assignedAgentId;
          
          // Assign new resource
          task.assignedAgentId = bestCandidateId;
          
          // Update resource utilization tracking
          if (originalResourceId) {
            const originalUtilization = resourceUtilization.get(originalResourceId) || 0.5;
            resourceUtilization.set(originalResourceId, Math.max(0, originalUtilization - 0.1));
          }
          
          const newUtilization = resourceUtilization.get(bestCandidateId) || 0.3;
          resourceUtilization.set(bestCandidateId, Math.min(1, newUtilization + 0.1));
          
          // Record reallocation
          reallocations.push({
            taskId: opportunity.taskId,
            originalResourceId,
            newResourceId: bestCandidateId
          });
        }
      }
    }
    
    return reallocations;
  }
  
  /**
   * Chooses the best resource from candidates
   * @param candidateIds Candidate resource IDs
   * @param utilization Current resource utilization
   * @returns Best resource ID or undefined if none available
   */
  private chooseBestResource(candidateIds: string[], utilization: Map<string, number>): string | undefined {
    if (candidateIds.length === 0) {
      return undefined;
    }
    
    // Choose resource with lowest utilization
    let bestId = candidateIds[0];
    let lowestUtilization = utilization.get(bestId) || 0.5;
    
    for (let i = 1; i < candidateIds.length; i++) {
      const id = candidateIds[i];
      const util = utilization.get(id) || 0.5;
      
      if (util < lowestUtilization) {
        bestId = id;
        lowestUtilization = util;
      }
    }
    
    return bestId;
  }
  
  /**
   * Calculates expected improvements from optimization
   * @param originalWorkflow Original workflow
   * @param optimizedWorkflow Optimized workflow
   * @param executionProfile Workflow execution profile
   * @param reallocations Applied resource reallocations
   * @returns Expected improvements
   */
  private calculateExpectedImprovements(
    originalWorkflow: Workflow,
    optimizedWorkflow: Workflow,
    executionProfile: WorkflowExecutionProfile,
    reallocations: { taskId: string; originalResourceId?: string; newResourceId: string }[]
  ): OptimizationResult['expectedImprovements'] {
    // Calculate resource efficiency gain
    const resourceEfficiencyGain = reallocations.reduce(
      (sum, reallocation) => sum + 0.5, // Assume 0.5% gain per reallocation
      0
    );
    
    // Calculate duration reduction
    // Resource optimization typically has modest impact on duration
    const durationReduction = resourceEfficiencyGain * 0.5; // Half the efficiency gain
    
    // Calculate reliability increase
    // Balanced resource utilization can improve reliability
    const reliabilityIncrease = resourceEfficiencyGain * 0.3; // 30% of efficiency gain
    
    // Calculate overall improvement
    // Weight resource efficiency more heavily since that's the main goal
    const overallImprovement = durationReduction * 0.3 + resourceEfficiencyGain * 0.5 + reliabilityIncrease * 0.2;
    
    return {
      durationReduction,
      resourceEfficiencyGain,
      reliabilityIncrease,
      overallImprovement
    };
  }
  
  /**
   * Identifies bottlenecks that would be resolved by optimization
   * @param bottlenecks Original bottlenecks
   * @param reallocations Applied resource reallocations
   * @returns Resolved and remaining bottlenecks
   */
  private identifyResolvedBottlenecks(
    bottlenecks: PerformanceBottleneck[],
    reallocations: { taskId: string; originalResourceId?: string; newResourceId: string }[]
  ): { bottlenecksResolved: PerformanceBottleneck[]; bottlenecksRemaining: PerformanceBottleneck[] } {
    const bottlenecksResolved: PerformanceBottleneck[] = [];
    const bottlenecksRemaining: PerformanceBottleneck[] = [];
    
    // Track reallocated tasks and resources
    const reallocatedTasks = new Set<string>();
    const originalResources = new Set<string>();
    
    for (const reallocation of reallocations) {
      reallocatedTasks.add(reallocation.taskId);
      if (reallocation.originalResourceId) {
        originalResources.add(reallocation.originalResourceId);
      }
    }
    
    for (const bottleneck of bottlenecks) {
      // Check if bottleneck is resolved by resource optimization
      if (
        bottleneck.type === 'resource' &&
        bottleneck.location.some(loc => originalResources.has(loc))
      ) {
        bottlenecksResolved.push(bottleneck);
      } else if (
        bottleneck.type === 'task' &&
        bottleneck.location.some(loc => reallocatedTasks.has(loc))
      ) {
        bottlenecksResolved.push(bottleneck);
      } else {
        bottlenecksRemaining.push(bottleneck);
      }
    }
    
    return { bottlenecksResolved, bottlenecksRemaining };
  }
  
  /**
   * Generates recommendations based on optimization results
   * @param resolvedBottlenecks Bottlenecks that were resolved
   * @param remainingBottlenecks Bottlenecks that remain
   * @param improvements Expected improvements
   * @returns Array of recommendations
   */
  private generateRecommendations(
    resolvedBottlenecks: PerformanceBottleneck[],
    remainingBottlenecks: PerformanceBottleneck[],
    improvements: OptimizationResult['expectedImprovements']
  ): string[] {
    const recommendations: string[] = [];
    
    // Add recommendations based on improvements
    if (improvements.resourceEfficiencyGain > 5) {
      recommendations.push(
        `Apply resource optimizations to improve resource efficiency by approximately ${Math.round(improvements.resourceEfficiencyGain)}%.`
      );
    } else if (improvements.resourceEfficiencyGain > 0) {
      recommendations.push(
        `Consider applying resource optimizations for a modest improvement of ${Math.round(improvements.resourceEfficiencyGain)}% in resource efficiency.`
      );
    } else {
      recommendations.push(
        'Resource optimizations provide minimal benefits for this workflow. Consider other optimization strategies.'
      );
    }
    
    // Add recommendations based on remaining bottlenecks
    if (remainingBottlenecks.length > 0) {
      // Group bottlenecks by type
      const bottlenecksByType = new Map<string, PerformanceBottleneck[]>();
      
      for (const bottleneck of remainingBottlenecks) {
        if (!bottlenecksByType.has(bottleneck.type)) {
          bottlenecksByType.set(bottleneck.type, []);
        }
        bottlenecksByType.get(bottleneck.type)?.push(bottleneck);
      }
      
      // Add recommendations for each type
      if (bottlenecksByType.has('dependency')) {
        recommendations.push(
          'Consider optimizing task dependencies to further improve workflow performance.'
        );
      }
      
      if (bottlenecksByType.has('communication')) {
        recommendations.push(
          'Optimize communication patterns to reduce overhead between tasks and resources.'
        );
      }
      
      if (bottlenecksByType.has('error')) {
        recommendations.push(
          'Address error-prone tasks to improve overall workflow reliability.'
        );
      }
    }
    
    // Add general recommendations
    recommendations.push(
      'Consider implementing a resource monitoring system to track resource utilization and identify bottlenecks proactively.'
    );
    
    return recommendations;
  }
}

/**
 * Factory for creating optimization strategies
 */
export class OptimizationStrategyFactory {
  /**
   * Creates an optimization strategy based on optimization options
   * @param options Optimization options
   * @returns Optimization strategy
   */
  static createStrategy(options: OptimizationOptions): OptimizationStrategy {
    switch (options.optimizationGoal) {
      case 'performance':
        return new ParallelizationStrategy();
      case 'resource_efficiency':
        return new ResourceOptimizationStrategy();
      case 'balanced':
        // For balanced optimization, we'd typically choose based on profile
        // For simplicity, default to parallelization
        return new ParallelizationStrategy();
      default:
        return new ParallelizationStrategy();
    }
  }
}

/**
 * Workflow optimizer that analyzes and optimizes workflow performance
 */
export class WorkflowOptimizer extends EventEmitter {
  private executionProfiles: Map<string, WorkflowExecutionProfile> = new Map();
  private optimizationResults: Map<string, OptimizationResult> = new Map();
  private taskAllocator?: TaskAllocator;
  private isInitialized: boolean = false;
  
  /**
   * Initializes the workflow optimizer
   * @param taskAllocator Optional task allocator for resource optimization
   * @returns Promise that resolves when initialization is complete
   */
  async initialize(taskAllocator?: TaskAllocator): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    this.taskAllocator = taskAllocator;
    
    this.isInitialized = true;
    console.log('Workflow optimizer initialized');
  }
  
  /**
   * Creates an execution profile for a workflow
   * @param workflow Workflow to profile
   * @param executionId Optional execution ID
   * @returns Workflow execution profile
   */
  createExecutionProfile(workflow: Workflow, executionId?: string): WorkflowExecutionProfile {
    const profile: WorkflowExecutionProfile = {
      workflowId: workflow.id,
      executionId: executionId || `exec_${Date.now()}`,
      startTime: Date.now(),
      status: workflow.status,
      metrics: this.calculatePerformanceMetrics(workflow),
      bottlenecks: this.identifyBottlenecks(workflow),
      taskProfiles: this.createTaskProfiles(workflow),
      resourceProfiles: this.createResourceProfiles(workflow)
    };
    
    // Store profile
    this.executionProfiles.set(profile.executionId, profile);
    
    return profile;
  }
  
  /**
   * Updates an execution profile with new data
   * @param executionId Execution ID
   * @param updates Updates to apply
   * @returns Updated workflow execution profile
   */
  updateExecutionProfile(executionId: string, updates: Partial<WorkflowExecutionProfile>): WorkflowExecutionProfile | undefined {
    const profile = this.executionProfiles.get(executionId);
    if (!profile) {
      return undefined;
    }
    
    // Apply updates
    Object.assign(profile, updates);
    
    // If status is completed or failed, set end time
    if (
      (updates.status === WorkflowStatus.COMPLETED || updates.status === WorkflowStatus.FAILED) && 
      !profile.endTime
    ) {
      profile.endTime = Date.now();
      
      // Update metrics
      if (updates.metrics) {
        profile.metrics = updates.metrics;
      } else {
        profile.metrics.totalDuration = profile.endTime - profile.startTime;
      }
      
      // Emit event
      this.emit('executionCompleted', profile);
    }
    
    return profile;
  }
  
  /**
   * Gets an execution profile by ID
   * @param executionId Execution ID
   * @returns Workflow execution profile or undefined if not found
   */
  getExecutionProfile(executionId: string): WorkflowExecutionProfile | undefined {
    return this.executionProfiles.get(executionId);
  }
  
  /**
   * Gets execution profiles for a workflow
   * @param workflowId Workflow ID
   * @returns Array of workflow execution profiles
   */
  getExecutionProfilesForWorkflow(workflowId: string): WorkflowExecutionProfile[] {
    return Array.from(this.executionProfiles.values())
      .filter(profile => profile.workflowId === workflowId);
  }
  
  /**
   * Gets the latest execution profile for a workflow
   * @param workflowId Workflow ID
   * @returns Latest workflow execution profile or undefined if none found
   */
  getLatestExecutionProfile(workflowId: string): WorkflowExecutionProfile | undefined {
    const profiles = this.getExecutionProfilesForWorkflow(workflowId);
    
    if (profiles.length === 0) {
      return undefined;
    }
    
    // Sort by start time (descending)
    profiles.sort((a, b) => b.startTime - a.startTime);
    
    return profiles[0];
  }
  
  /**
   * Optimizes a workflow
   * @param workflow Workflow to optimize
   * @param options Optimization options
   * @returns Optimization result
   */
  async optimizeWorkflow(workflow: Workflow, options: OptimizationOptions): Promise<OptimizationResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    // Get execution profile
    let executionProfile = this.getLatestExecutionProfile(workflow.id);
    
    if (!executionProfile) {
      // Create a new profile if none exists
      executionProfile = this.createExecutionProfile(workflow);
    }
    
    // Create optimization strategy
    const strategy = OptimizationStrategyFactory.createStrategy(options);
    
    // Optimize workflow
    const result = await strategy.optimize(workflow, executionProfile, options);
    
    // Store result
    this.optimizationResults.set(result.optimizationId, result);
    
    // Emit event
    this.emit('workflowOptimized', result);
    
    return result;
  }
  
  /**
   * Gets an optimization result by ID
   * @param optimizationId Optimization ID
   * @returns Optimization result or undefined if not found
   */
  getOptimizationResult(optimizationId: string): OptimizationResult | undefined {
    return this.optimizationResults.get(optimizationId);
  }
  
  /**
   * Gets optimization results for a workflow
   * @param workflowId Workflow ID
   * @returns Array of optimization results
   */
  getOptimizationResultsForWorkflow(workflowId: string): OptimizationResult[] {
    return Array.from(this.optimizationResults.values())
      .filter(result => result.workflowId === workflowId);
  }
  
  /**
   * Calculates performance metrics for a workflow
   * @param workflow Workflow to analyze
   * @returns Workflow performance metrics
   */
  private calculatePerformanceMetrics(workflow: Workflow): WorkflowPerformanceMetrics {
    // Count tasks by status
    const totalTasks = workflow.tasks.size;
    const completedTasks = workflow.getCompletedTasks().length;
    const failedTasks = workflow.getFailedTasks().length;
    
    // Calculate success and completion rates
    const successRate = completedTasks / (completedTasks + failedTasks) || 0;
    const completionRate = (completedTasks + failedTasks) / totalTasks;
    
    // Calculate critical path duration and parallelism degree
    const criticalPathDuration = 0; // This would be calculated based on task durations and dependencies
    const parallelismDegree = 1; // This would be calculated based on task execution patterns
    
    // Calculate resource metrics
    const agentUtilization = new Map<string, number>();
    let resourceEfficiency = 0.7; // Default to moderate efficiency
    let loadBalance = 0.5; // Default to moderate balance
    let waitingTime = 0; // This would be calculated based on task waiting times
    
    // Collect agents
    const agentIds = new Set<string>();
    for (const task of workflow.tasks.values()) {
      if (task.assignedAgentId) {
        agentIds.add(task.assignedAgentId);
      }
    }
    
    // Calculate agent utilization (mock values)
    for (const agentId of agentIds) {
      agentUtilization.set(agentId, 0.5 + Math.random() * 0.5); // 0.5-1.0
    }
    
    // Calculate average task duration
    const averageTaskDuration = 60000; // Default to 1 minute
    
    return {
      workflowId: workflow.id,
      totalDuration: 0, // Will be set when workflow completes
      taskMetrics: {
        totalTasks,
        completedTasks,
        failedTasks,
        averageTaskDuration,
        criticalPathDuration,
        parallelismDegree
      },
      resourceMetrics: {
        agentUtilization,
        resourceEfficiency,
        loadBalance,
        waitingTime
      },
      qualityMetrics: {
        successRate,
        errorRate: 1 - successRate,
        completionRate
      }
    };
  }
  
  /**
   * Identifies performance bottlenecks in a workflow
   * @param workflow Workflow to analyze
   * @returns Array of performance bottlenecks
   */
  private identifyBottlenecks(workflow: Workflow): PerformanceBottleneck[] {
    const bottlenecks: PerformanceBottleneck[] = [];
    
    // Identify sequential execution bottlenecks
    if (workflow.executionMode === WorkflowExecutionMode.SEQUENTIAL && workflow.tasks.size > 5) {
      bottlenecks.push({
        type: 'dependency',
        severity: 7,
        impact: 0.6,
        description: 'Sequential execution of multiple tasks causing performance bottleneck',
        location: Array.from(workflow.tasks.keys()),
        recommendations: [
          'Consider parallelizing independent tasks',
          'Review task dependencies to identify parallelization opportunities'
        ],
        metadata: {
          taskCount: workflow.tasks.size,
          executionMode: workflow.executionMode
        }
      });
    }
    
    // Identify resource bottlenecks
    const resourceToTasks = new Map<string, string[]>();
    
    for (const task of workflow.tasks.values()) {
      if (task.assignedAgentId) {
        if (!resourceToTasks.has(task.assignedAgentId)) {
          resourceToTasks.set(task.assignedAgentId, []);
        }
        resourceToTasks.get(task.assignedAgentId)?.push(task.id);
      }
    }
    
    // Check for overloaded resources
    for (const [resourceId, taskIds] of resourceToTasks.entries()) {
      if (taskIds.length > 3) {
        bottlenecks.push({
          type: 'resource',
          severity: 6,
          impact: 0.5,
          description: `Resource ${resourceId} is overloaded with ${taskIds.length} tasks`,
          location: [resourceId, ...taskIds],
          recommendations: [
            'Redistribute tasks to underutilized resources',
            'Consider adding more resources of this type'
          ],
          metadata: {
            resourceId,
            taskCount: taskIds.length
          }
        });
      }
    }
    
    // Identify complex task dependencies
    for (const task of workflow.tasks.values()) {
      if (task.dependencies.length > 3) {
        bottlenecks.push({
          type: 'dependency',
          severity: 5,
          impact: 0.4,
          description: `Task ${task.name} has ${task.dependencies.length} dependencies, creating a potential bottleneck`,
          location: [task.id, ...task.dependencies],
          recommendations: [
            'Review task dependencies to simplify if possible',
            'Consider restructuring the workflow to reduce complex dependencies'
          ],
          metadata: {
            taskId: task.id,
            dependencyCount: task.dependencies.length
          }
        });
      }
    }
    
    return bottlenecks;
  }
  
  /**
   * Creates task execution profiles for a workflow
   * @param workflow Workflow to profile
   * @returns Map of task IDs to task execution profiles
   */
  private createTaskProfiles(workflow: Workflow): Map<string, TaskExecutionProfile> {
    const taskProfiles = new Map<string, TaskExecutionProfile>();
    
    for (const task of workflow.tasks.values()) {
      // Create task profile
      const profile: TaskExecutionProfile = {
        taskId: task.id,
        startTime: task.startTime,
        endTime: task.endTime,
        agentId: task.assignedAgentId,
        status: task.status,
        duration: task.startTime && task.endTime ? task.endTime - task.startTime : undefined,
        waitTime: 0, // This would be calculated based on task scheduling
        processingTime: task.startTime && task.endTime ? task.endTime - task.startTime : undefined,
        dependencies: task.dependencies.map(depId => ({
          id: depId,
          type: 'control',
          impact: 0.5 // Default impact
        })),
        metrics: {
          efficiency: 0.7, // Default to moderate efficiency
          criticalPathContribution: 0.5, // Default to moderate contribution
          resourceUsage: 0.5, // Default to moderate usage
          errorRate: task.status === TaskStatus.FAILED ? 1 : 0
        }
      };
      
      taskProfiles.set(task.id, profile);
    }
    
    return taskProfiles;
  }
  
  /**
   * Creates resource usage profiles for a workflow
   * @param workflow Workflow to profile
   * @returns Map of resource IDs to resource usage profiles
   */
  private createResourceProfiles(workflow: Workflow): Map<string, ResourceUsageProfile> {
    const resourceProfiles = new Map<string, ResourceUsageProfile>();
    
    // Collect resources
    const resourceToTasks = new Map<string, Task[]>();
    
    for (const task of workflow.tasks.values()) {
      if (task.assignedAgentId) {
        if (!resourceToTasks.has(task.assignedAgentId)) {
          resourceToTasks.set(task.assignedAgentId, []);
        }
        resourceToTasks.get(task.assignedAgentId)?.push(task);
      }
    }
    
    // Create resource profiles
    for (const [resourceId, tasks] of resourceToTasks.entries()) {
      // Create task allocations
      const taskAllocation = tasks.map(task => ({
        taskId: task.id,
        startTime: task.startTime || Date.now(),
        endTime: task.endTime,
        utilizationLevel: 0.7 // Default to moderate utilization
      }));
      
      // Calculate utilization
      const utilization = 0.5 + Math.random() * 0.5; // 0.5-1.0
      
      // Create resource profile
      const profile: ResourceUsageProfile = {
        resourceId,
        resourceType: 'agent',
        utilization,
        taskAllocation,
        metrics: {
          efficiency: 0.7, // Default to moderate efficiency
          contention: utilization > 0.8 ? 0.8 : 0.3, // High contention if utilization is high
          idleTime: (1 - utilization) * 3600000, // Idle time in ms (based on 1 hour)
          overloadTime: utilization > 0.8 ? 1800000 : 0 // Overload time in ms (30 minutes if overloaded)
        }
      };
      
      resourceProfiles.set(resourceId, profile);
    }
    
    return resourceProfiles;
  }
  
  /**
   * Gets all execution profiles
   * @returns Array of workflow execution profiles
   */
  getAllExecutionProfiles(): WorkflowExecutionProfile[] {
    return Array.from(this.executionProfiles.values());
  }
  
  /**
   * Gets all optimization results
   * @returns Array of optimization results
   */
  getAllOptimizationResults(): OptimizationResult[] {
    return Array.from(this.optimizationResults.values());
  }
  
  /**
   * Clears all execution profiles and optimization results
   */
  clearAllData(): void {
    this.executionProfiles.clear();
    this.optimizationResults.clear();
  }
}

export default WorkflowOptimizer;