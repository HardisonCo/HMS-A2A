import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { SupervisorGateway } from '../core/supervisor_gateway';
import { AgentRegistry } from '../core/agent_registry';
import { Message, MessageType, MessagePriority } from '../communication/message';
import { Agent } from '../agents/agent_interface';
import { KnowledgeBaseManager } from '../knowledge/knowledge_base_manager';

/**
 * Represents the status of a workflow
 */
export enum WorkflowStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

/**
 * Represents the status of a task within a workflow
 */
export enum TaskStatus {
  PENDING = 'pending',
  ASSIGNED = 'assigned',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  SKIPPED = 'skipped',
  CANCELLED = 'cancelled'
}

/**
 * Represents the type of a task
 */
export enum TaskType {
  SEQUENTIAL = 'sequential',   // Must be executed in sequence
  PARALLEL = 'parallel',       // Can be executed in parallel
  CONDITIONAL = 'conditional', // Executed based on a condition
  ITERATIVE = 'iterative',     // Executed repeatedly until condition is met
  COMPOSITE = 'composite'      // A composite task containing subtasks
}

/**
 * Represents a condition for conditional or iterative tasks
 */
export interface TaskCondition {
  type: 'expression' | 'function' | 'message';
  value: string | Function | Message;
  metadata?: Record<string, any>;
}

/**
 * Represents the execution mode of a workflow
 */
export enum WorkflowExecutionMode {
  SEQUENTIAL = 'sequential',   // Tasks executed in sequence
  PARALLEL = 'parallel',       // Tasks executed in parallel
  HYBRID = 'hybrid',           // Combination of sequential and parallel execution
  ADAPTIVE = 'adaptive'        // Execution strategy determined at runtime
}

/**
 * Represents the coordination strategy for workflow execution
 */
export enum CoordinationStrategy {
  CENTRALIZED = 'centralized',           // Orchestrator maintains central control
  DECENTRALIZED = 'decentralized',       // Agents coordinate among themselves
  HIERARCHY = 'hierarchy',               // Multi-level control structure
  MARKET_BASED = 'market_based',         // Agents bid for tasks
  CONSENSUS = 'consensus',               // Agents reach consensus on execution
  ADAPTIVE_HYBRID = 'adaptive_hybrid'    // Strategy determined at runtime
}

/**
 * Options for creating a workflow
 */
export interface WorkflowOptions {
  name: string;
  description?: string;
  executionMode?: WorkflowExecutionMode;
  coordinationStrategy?: CoordinationStrategy;
  timeout?: number;                     // Timeout in milliseconds
  maxRetries?: number;                  // Maximum number of retries per task
  priority?: number;                    // Priority of the workflow (1-10, 10 is highest)
  requiredAgentTypes?: string[];        // Agent types required for this workflow
  knowledgeBaseScope?: string[];        // Knowledge base scopes accessible to this workflow
  metadata?: Record<string, any>;       // Additional metadata for the workflow
  tags?: string[];                      // Tags for categorizing workflows
}

/**
 * Options for creating a task
 */
export interface TaskOptions {
  name: string;
  description?: string;
  type?: TaskType;
  agentType?: string;                   // Type of agent required for this task
  agentId?: string;                     // Specific agent ID (if specified)
  inputMapping?: Record<string, string>; // Map workflow context to task input
  outputMapping?: Record<string, string>; // Map task output to workflow context
  timeout?: number;                     // Timeout in milliseconds
  retries?: number;                     // Number of retries
  condition?: TaskCondition;            // Condition for conditional/iterative tasks
  metadata?: Record<string, any>;       // Additional metadata for the task
  priority?: number;                    // Priority within the workflow (1-10)
  subtasks?: string[];                  // IDs of subtasks (for composite tasks)
  dependencies?: string[];              // IDs of tasks this task depends on
  fallbackTaskId?: string;              // Task to execute if this task fails
  estimatedDuration?: number;           // Estimated duration in milliseconds
  knowledgeBaseRequirements?: string[]; // Knowledge base access required
  resourceRequirements?: Record<string, any>; // Resources required for this task
}

/**
 * Represents a task within a workflow
 */
export class Task {
  id: string;
  name: string;
  description: string;
  type: TaskType;
  status: TaskStatus;
  agentType?: string;
  agentId?: string;
  assignedAgentId?: string;
  inputMapping: Record<string, string>;
  outputMapping: Record<string, string>;
  timeout: number;
  retries: number;
  maxRetries: number;
  condition?: TaskCondition;
  metadata: Record<string, any>;
  priority: number;
  subtasks: string[];
  dependencies: string[];
  fallbackTaskId?: string;
  estimatedDuration: number;
  actualDuration?: number;
  startTime?: number;
  endTime?: number;
  result?: any;
  error?: Error;
  knowledgeBaseRequirements: string[];
  resourceRequirements: Record<string, any>;
  
  constructor(options: TaskOptions) {
    this.id = uuidv4();
    this.name = options.name;
    this.description = options.description || '';
    this.type = options.type || TaskType.SEQUENTIAL;
    this.status = TaskStatus.PENDING;
    this.agentType = options.agentType;
    this.agentId = options.agentId;
    this.inputMapping = options.inputMapping || {};
    this.outputMapping = options.outputMapping || {};
    this.timeout = options.timeout || 60000; // Default: 60 seconds
    this.retries = 0;
    this.maxRetries = options.retries || 3;
    this.condition = options.condition;
    this.metadata = options.metadata || {};
    this.priority = options.priority || 5;
    this.subtasks = options.subtasks || [];
    this.dependencies = options.dependencies || [];
    this.fallbackTaskId = options.fallbackTaskId;
    this.estimatedDuration = options.estimatedDuration || 30000; // Default: 30 seconds
    this.knowledgeBaseRequirements = options.knowledgeBaseRequirements || [];
    this.resourceRequirements = options.resourceRequirements || {};
  }
  
  /**
   * Creates a deep copy of this task
   * @returns A new task instance with the same properties
   */
  clone(): Task {
    const clonedTask = new Task({
      name: this.name,
      description: this.description,
      type: this.type,
      agentType: this.agentType,
      agentId: this.agentId,
      inputMapping: { ...this.inputMapping },
      outputMapping: { ...this.outputMapping },
      timeout: this.timeout,
      retries: this.maxRetries,
      condition: this.condition ? { ...this.condition } : undefined,
      metadata: { ...this.metadata },
      priority: this.priority,
      subtasks: [...this.subtasks],
      dependencies: [...this.dependencies],
      fallbackTaskId: this.fallbackTaskId,
      estimatedDuration: this.estimatedDuration,
      knowledgeBaseRequirements: [...this.knowledgeBaseRequirements],
      resourceRequirements: { ...this.resourceRequirements }
    });
    
    return clonedTask;
  }
  
  /**
   * Updates the status of the task
   * @param status New status
   */
  updateStatus(status: TaskStatus): void {
    this.status = status;
    
    // Record timestamps
    if (status === TaskStatus.RUNNING && !this.startTime) {
      this.startTime = Date.now();
    } else if ([TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED].includes(status) && this.startTime && !this.endTime) {
      this.endTime = Date.now();
      if (this.startTime) {
        this.actualDuration = this.endTime - this.startTime;
      }
    }
  }
  
  /**
   * Sets the result of the task
   * @param result Task result
   */
  setResult(result: any): void {
    this.result = result;
  }
  
  /**
   * Sets an error that occurred during task execution
   * @param error Error object
   */
  setError(error: Error): void {
    this.error = error;
  }
  
  /**
   * Assigns an agent to this task
   * @param agentId ID of the agent
   */
  assignAgent(agentId: string): void {
    this.assignedAgentId = agentId;
  }
}

/**
 * Represents a workflow consisting of multiple tasks
 */
export class Workflow {
  id: string;
  name: string;
  description: string;
  tasks: Map<string, Task>;
  context: Map<string, any>;
  status: WorkflowStatus;
  executionMode: WorkflowExecutionMode;
  coordinationStrategy: CoordinationStrategy;
  timeout: number;
  maxRetries: number;
  priority: number;
  requiredAgentTypes: string[];
  knowledgeBaseScope: string[];
  metadata: Record<string, any>;
  tags: string[];
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
  taskOrder: string[];
  currentTaskIndex: number;
  errors: Error[];
  
  constructor(options: WorkflowOptions) {
    this.id = uuidv4();
    this.name = options.name;
    this.description = options.description || '';
    this.tasks = new Map<string, Task>();
    this.context = new Map<string, any>();
    this.status = WorkflowStatus.PENDING;
    this.executionMode = options.executionMode || WorkflowExecutionMode.SEQUENTIAL;
    this.coordinationStrategy = options.coordinationStrategy || CoordinationStrategy.CENTRALIZED;
    this.timeout = options.timeout || 3600000; // Default: 1 hour
    this.maxRetries = options.maxRetries || 3;
    this.priority = options.priority || 5;
    this.requiredAgentTypes = options.requiredAgentTypes || [];
    this.knowledgeBaseScope = options.knowledgeBaseScope || [];
    this.metadata = options.metadata || {};
    this.tags = options.tags || [];
    this.createdAt = Date.now();
    this.taskOrder = [];
    this.currentTaskIndex = 0;
    this.errors = [];
  }
  
  /**
   * Adds a task to the workflow
   * @param task Task to add
   * @returns ID of the added task
   */
  addTask(task: Task): string {
    this.tasks.set(task.id, task);
    this.taskOrder.push(task.id);
    return task.id;
  }
  
  /**
   * Adds multiple tasks to the workflow
   * @param tasks Tasks to add
   * @returns Array of task IDs
   */
  addTasks(tasks: Task[]): string[] {
    const taskIds: string[] = [];
    for (const task of tasks) {
      taskIds.push(this.addTask(task));
    }
    return taskIds;
  }
  
  /**
   * Removes a task from the workflow
   * @param taskId ID of the task to remove
   * @returns True if the task was removed, false otherwise
   */
  removeTask(taskId: string): boolean {
    const result = this.tasks.delete(taskId);
    if (result) {
      this.taskOrder = this.taskOrder.filter(id => id !== taskId);
      
      // Update dependencies in other tasks
      for (const task of this.tasks.values()) {
        task.dependencies = task.dependencies.filter(id => id !== taskId);
        task.subtasks = task.subtasks.filter(id => id !== taskId);
        if (task.fallbackTaskId === taskId) {
          task.fallbackTaskId = undefined;
        }
      }
    }
    return result;
  }
  
  /**
   * Gets a task by ID
   * @param taskId ID of the task
   * @returns Task or undefined if not found
   */
  getTask(taskId: string): Task | undefined {
    return this.tasks.get(taskId);
  }
  
  /**
   * Updates the status of the workflow
   * @param status New status
   */
  updateStatus(status: WorkflowStatus): void {
    this.status = status;
    
    // Record timestamps
    if (status === WorkflowStatus.RUNNING && !this.startedAt) {
      this.startedAt = Date.now();
    } else if ([WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED].includes(status) && !this.completedAt) {
      this.completedAt = Date.now();
    }
  }
  
  /**
   * Sets a value in the workflow context
   * @param key Context key
   * @param value Value to set
   */
  setContextValue(key: string, value: any): void {
    this.context.set(key, value);
  }
  
  /**
   * Gets a value from the workflow context
   * @param key Context key
   * @returns Value or undefined if not found
   */
  getContextValue(key: string): any {
    return this.context.get(key);
  }
  
  /**
   * Gets all pending tasks
   * @returns Array of pending tasks
   */
  getPendingTasks(): Task[] {
    return Array.from(this.tasks.values()).filter(task => task.status === TaskStatus.PENDING);
  }
  
  /**
   * Gets all running tasks
   * @returns Array of running tasks
   */
  getRunningTasks(): Task[] {
    return Array.from(this.tasks.values()).filter(task => task.status === TaskStatus.RUNNING);
  }
  
  /**
   * Gets all completed tasks
   * @returns Array of completed tasks
   */
  getCompletedTasks(): Task[] {
    return Array.from(this.tasks.values()).filter(task => task.status === TaskStatus.COMPLETED);
  }
  
  /**
   * Gets all failed tasks
   * @returns Array of failed tasks
   */
  getFailedTasks(): Task[] {
    return Array.from(this.tasks.values()).filter(task => task.status === TaskStatus.FAILED);
  }
  
  /**
   * Gets tasks that are ready to be executed (all dependencies are completed)
   * @returns Array of ready tasks
   */
  getReadyTasks(): Task[] {
    return Array.from(this.tasks.values()).filter(task => {
      // Task must be pending
      if (task.status !== TaskStatus.PENDING) {
        return false;
      }
      
      // All dependencies must be completed
      for (const dependencyId of task.dependencies) {
        const dependency = this.tasks.get(dependencyId);
        if (!dependency || dependency.status !== TaskStatus.COMPLETED) {
          return false;
        }
      }
      
      return true;
    });
  }
  
  /**
   * Gets the next task in sequence (for sequential execution mode)
   * @returns Next task or undefined if no more tasks
   */
  getNextSequentialTask(): Task | undefined {
    if (this.currentTaskIndex >= this.taskOrder.length) {
      return undefined;
    }
    
    const taskId = this.taskOrder[this.currentTaskIndex];
    const task = this.tasks.get(taskId);
    
    return task;
  }
  
  /**
   * Moves to the next task in sequence (for sequential execution mode)
   */
  advanceToNextTask(): void {
    this.currentTaskIndex++;
  }
  
  /**
   * Adds an error that occurred during workflow execution
   * @param error Error object
   */
  addError(error: Error): void {
    this.errors.push(error);
  }
  
  /**
   * Checks if the workflow has completed all tasks
   * @returns True if all tasks are completed, failed, cancelled, or skipped
   */
  isComplete(): boolean {
    for (const task of this.tasks.values()) {
      if (![TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.SKIPPED].includes(task.status)) {
        return false;
      }
    }
    return true;
  }
  
  /**
   * Gets workflow statistics
   * @returns Object with workflow statistics
   */
  getStatistics(): Record<string, any> {
    const totalTasks = this.tasks.size;
    const pendingTasks = this.getPendingTasks().length;
    const runningTasks = this.getRunningTasks().length;
    const completedTasks = this.getCompletedTasks().length;
    const failedTasks = this.getFailedTasks().length;
    const skippedTasks = Array.from(this.tasks.values()).filter(task => task.status === TaskStatus.SKIPPED).length;
    const cancelledTasks = Array.from(this.tasks.values()).filter(task => task.status === TaskStatus.CANCELLED).length;
    
    let progress = 0;
    if (totalTasks > 0) {
      progress = Math.round((completedTasks / totalTasks) * 100);
    }
    
    let duration = 0;
    if (this.startedAt) {
      const endTime = this.completedAt || Date.now();
      duration = endTime - this.startedAt;
    }
    
    return {
      totalTasks,
      pendingTasks,
      runningTasks,
      completedTasks,
      failedTasks,
      skippedTasks,
      cancelledTasks,
      progress,
      duration,
      status: this.status,
      errors: this.errors.length
    };
  }
  
  /**
   * Creates a visualization of the workflow as a directed graph
   * @returns String representation of the workflow graph in mermaid.js format
   */
  visualize(): string {
    let mermaid = 'graph TD;\n';
    
    // Add nodes for all tasks
    for (const task of this.tasks.values()) {
      let styleClass = '';
      switch (task.status) {
        case TaskStatus.PENDING:
          styleClass = 'classPending';
          break;
        case TaskStatus.RUNNING:
          styleClass = 'classRunning';
          break;
        case TaskStatus.COMPLETED:
          styleClass = 'classCompleted';
          break;
        case TaskStatus.FAILED:
          styleClass = 'classFailed';
          break;
        case TaskStatus.SKIPPED:
          styleClass = 'classSkipped';
          break;
        case TaskStatus.CANCELLED:
          styleClass = 'classCancelled';
          break;
      }
      
      mermaid += `  ${task.id}["${task.name}"]:::${styleClass};\n`;
    }
    
    // Add edges for task dependencies
    for (const task of this.tasks.values()) {
      for (const dependencyId of task.dependencies) {
        mermaid += `  ${dependencyId} --> ${task.id};\n`;
      }
      
      // Add edges for subtasks
      for (const subtaskId of task.subtasks) {
        mermaid += `  ${task.id} -.-> ${subtaskId};\n`;
      }
      
      // Add edges for fallback tasks
      if (task.fallbackTaskId) {
        mermaid += `  ${task.id} -. fallback .-> ${task.fallbackTaskId};\n`;
      }
    }
    
    // Add style definitions
    mermaid += '  classDef classPending fill:#fcf3cf,stroke:#f1c40f;\n';
    mermaid += '  classDef classRunning fill:#d4efdf,stroke:#2ecc71;\n';
    mermaid += '  classDef classCompleted fill:#a9dfbf,stroke:#27ae60;\n';
    mermaid += '  classDef classFailed fill:#f5b7b1,stroke:#e74c3c;\n';
    mermaid += '  classDef classSkipped fill:#d5dbdb,stroke:#7f8c8d;\n';
    mermaid += '  classDef classCancelled fill:#d5d8dc,stroke:#566573;\n';
    
    return mermaid;
  }
}

/**
 * Options for a workflow template
 */
export interface WorkflowTemplateOptions extends WorkflowOptions {
  id: string;
  version: string;
  parameters: {
    name: string;
    description: string;
    type: string;
    required: boolean;
    defaultValue?: any;
  }[];
}

/**
 * Represents a reusable workflow template
 */
export class WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  version: string;
  taskTemplates: Map<string, Task>;
  parameters: Map<string, {
    name: string;
    description: string;
    type: string;
    required: boolean;
    defaultValue?: any;
  }>;
  executionMode: WorkflowExecutionMode;
  coordinationStrategy: CoordinationStrategy;
  timeout: number;
  maxRetries: number;
  priority: number;
  requiredAgentTypes: string[];
  knowledgeBaseScope: string[];
  metadata: Record<string, any>;
  tags: string[];
  taskOrder: string[];
  
  constructor(options: WorkflowTemplateOptions) {
    this.id = options.id;
    this.name = options.name;
    this.description = options.description || '';
    this.version = options.version;
    this.taskTemplates = new Map<string, Task>();
    this.parameters = new Map();
    for (const param of options.parameters) {
      this.parameters.set(param.name, param);
    }
    this.executionMode = options.executionMode || WorkflowExecutionMode.SEQUENTIAL;
    this.coordinationStrategy = options.coordinationStrategy || CoordinationStrategy.CENTRALIZED;
    this.timeout = options.timeout || 3600000; // Default: 1 hour
    this.maxRetries = options.maxRetries || 3;
    this.priority = options.priority || 5;
    this.requiredAgentTypes = options.requiredAgentTypes || [];
    this.knowledgeBaseScope = options.knowledgeBaseScope || [];
    this.metadata = options.metadata || {};
    this.tags = options.tags || [];
    this.taskOrder = [];
  }
  
  /**
   * Adds a task template to the workflow template
   * @param task Task template to add
   * @returns ID of the added task template
   */
  addTaskTemplate(task: Task): string {
    this.taskTemplates.set(task.id, task);
    this.taskOrder.push(task.id);
    return task.id;
  }
  
  /**
   * Creates a workflow instance from this template
   * @param paramValues Values for the template parameters
   * @returns New workflow instance
   */
  createWorkflow(paramValues: Record<string, any> = {}): Workflow {
    // Validate parameters
    for (const [paramName, paramDef] of this.parameters.entries()) {
      if (paramDef.required && !(paramName in paramValues)) {
        throw new Error(`Required parameter '${paramName}' is missing`);
      }
    }
    
    // Create workflow
    const workflow = new Workflow({
      name: this.name,
      description: this.description,
      executionMode: this.executionMode,
      coordinationStrategy: this.coordinationStrategy,
      timeout: this.timeout,
      maxRetries: this.maxRetries,
      priority: this.priority,
      requiredAgentTypes: [...this.requiredAgentTypes],
      knowledgeBaseScope: [...this.knowledgeBaseScope],
      metadata: { ...this.metadata, templateId: this.id, templateVersion: this.version },
      tags: [...this.tags]
    });
    
    // Apply parameter values to workflow context
    for (const [paramName, paramValue] of Object.entries(paramValues)) {
      workflow.setContextValue(paramName, paramValue);
    }
    
    // Add default values for parameters not provided
    for (const [paramName, paramDef] of this.parameters.entries()) {
      if (!(paramName in paramValues) && 'defaultValue' in paramDef) {
        workflow.setContextValue(paramName, paramDef.defaultValue);
      }
    }
    
    // Clone task templates and add to workflow
    const taskIdMap = new Map<string, string>(); // Map template task IDs to workflow task IDs
    
    for (const taskTemplateId of this.taskOrder) {
      const taskTemplate = this.taskTemplates.get(taskTemplateId);
      if (taskTemplate) {
        const task = taskTemplate.clone();
        
        // Replace parameter references in task properties
        this.replaceParameterReferences(task, workflow.context);
        
        const newTaskId = workflow.addTask(task);
        taskIdMap.set(taskTemplateId, newTaskId);
      }
    }
    
    // Update task dependencies and subtasks with new IDs
    for (const task of workflow.tasks.values()) {
      // Update dependencies
      const newDependencies: string[] = [];
      for (const dependencyId of task.dependencies) {
        const newDependencyId = taskIdMap.get(dependencyId);
        if (newDependencyId) {
          newDependencies.push(newDependencyId);
        }
      }
      task.dependencies = newDependencies;
      
      // Update subtasks
      const newSubtasks: string[] = [];
      for (const subtaskId of task.subtasks) {
        const newSubtaskId = taskIdMap.get(subtaskId);
        if (newSubtaskId) {
          newSubtasks.push(newSubtaskId);
        }
      }
      task.subtasks = newSubtasks;
      
      // Update fallback task
      if (task.fallbackTaskId) {
        task.fallbackTaskId = taskIdMap.get(task.fallbackTaskId);
      }
    }
    
    return workflow;
  }
  
  /**
   * Replaces parameter references in task properties with actual values
   * @param task Task to update
   * @param context Workflow context with parameter values
   */
  private replaceParameterReferences(task: Task, context: Map<string, any>): void {
    // Helper function to replace parameter references in strings
    const replaceInString = (str: string): string => {
      return str.replace(/\${([^}]+)}/g, (match, paramName) => {
        const value = context.get(paramName);
        return value !== undefined ? String(value) : match;
      });
    };
    
    // Replace in name and description
    task.name = replaceInString(task.name);
    task.description = replaceInString(task.description);
    
    // Replace in input and output mappings
    for (const [key, value] of Object.entries(task.inputMapping)) {
      task.inputMapping[key] = replaceInString(value);
    }
    
    for (const [key, value] of Object.entries(task.outputMapping)) {
      task.outputMapping[key] = replaceInString(value);
    }
    
    // Replace in metadata
    for (const [key, value] of Object.entries(task.metadata)) {
      if (typeof value === 'string') {
        task.metadata[key] = replaceInString(value);
      }
    }
  }
}

/**
 * Interface for workflow execution strategies
 */
export interface WorkflowExecutionStrategy {
  executeWorkflow(workflow: Workflow): Promise<void>;
  executeTask(workflow: Workflow, task: Task): Promise<void>;
  handleTaskCompletion(workflow: Workflow, task: Task, result: any): Promise<void>;
  handleTaskFailure(workflow: Workflow, task: Task, error: Error): Promise<void>;
  pause(workflow: Workflow): Promise<void>;
  resume(workflow: Workflow): Promise<void>;
  cancel(workflow: Workflow): Promise<void>;
}

/**
 * Sequential execution strategy for workflows
 */
export class SequentialExecutionStrategy implements WorkflowExecutionStrategy {
  private orchestrator: WorkflowOrchestrator;
  
  constructor(orchestrator: WorkflowOrchestrator) {
    this.orchestrator = orchestrator;
  }
  
  async executeWorkflow(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.RUNNING);
    await this.executeNextTask(workflow);
  }
  
  async executeTask(workflow: Workflow, task: Task): Promise<void> {
    // Get context values for task input
    const taskInput: Record<string, any> = {};
    for (const [taskParam, contextKey] of Object.entries(task.inputMapping)) {
      taskInput[taskParam] = workflow.getContextValue(contextKey);
    }
    
    // Execute task
    task.updateStatus(TaskStatus.RUNNING);
    
    try {
      // Get agent for this task
      const agent = await this.orchestrator.getAgentForTask(workflow, task);
      if (!agent) {
        throw new Error(`No agent available for task ${task.id} (${task.name})`);
      }
      
      // Create a message for the agent
      const message = new Message({
        type: MessageType.TASK_REQUEST,
        sender: 'workflow_orchestrator',
        recipient: agent.getId(),
        content: {
          workflowId: workflow.id,
          taskId: task.id,
          taskName: task.name,
          taskInput
        },
        priority: MessagePriority.NORMAL,
        metadata: {
          workflowName: workflow.name,
          taskType: task.type
        }
      });
      
      // Send message to agent
      task.assignAgent(agent.getId());
      await this.orchestrator.sendMessageToAgent(message);
      
      // Set up timeout if specified
      if (task.timeout > 0) {
        setTimeout(() => {
          if (task.status === TaskStatus.RUNNING) {
            this.handleTaskFailure(workflow, task, new Error(`Task execution timed out after ${task.timeout}ms`));
          }
        }, task.timeout);
      }
    } catch (error) {
      await this.handleTaskFailure(workflow, task, error as Error);
    }
  }
  
  async handleTaskCompletion(workflow: Workflow, task: Task, result: any): Promise<void> {
    task.updateStatus(TaskStatus.COMPLETED);
    task.setResult(result);
    
    // Apply output mapping to workflow context
    for (const [taskOutput, contextKey] of Object.entries(task.outputMapping)) {
      if (taskOutput in result) {
        workflow.setContextValue(contextKey, result[taskOutput]);
      }
    }
    
    // Move to next task
    await this.executeNextTask(workflow);
  }
  
  async handleTaskFailure(workflow: Workflow, task: Task, error: Error): Promise<void> {
    task.updateStatus(TaskStatus.FAILED);
    task.setError(error);
    workflow.addError(error);
    
    // Retry the task if retries are available
    if (task.retries < task.maxRetries) {
      task.retries++;
      task.updateStatus(TaskStatus.PENDING);
      await this.executeTask(workflow, task);
      return;
    }
    
    // Try fallback task if available
    if (task.fallbackTaskId) {
      const fallbackTask = workflow.getTask(task.fallbackTaskId);
      if (fallbackTask && fallbackTask.status === TaskStatus.PENDING) {
        await this.executeTask(workflow, fallbackTask);
        return;
      }
    }
    
    // If this is a critical failure, fail the workflow
    if (task.metadata.critical === true) {
      workflow.updateStatus(WorkflowStatus.FAILED);
      this.orchestrator.emit('workflowFailed', workflow, error);
      return;
    }
    
    // Otherwise, continue with next task
    await this.executeNextTask(workflow);
  }
  
  async pause(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.PAUSED);
  }
  
  async resume(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.RUNNING);
    await this.executeNextTask(workflow);
  }
  
  async cancel(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.CANCELLED);
    
    // Cancel all running tasks
    for (const task of workflow.getRunningTasks()) {
      task.updateStatus(TaskStatus.CANCELLED);
    }
    
    // Mark all pending tasks as cancelled
    for (const task of workflow.getPendingTasks()) {
      task.updateStatus(TaskStatus.CANCELLED);
    }
    
    this.orchestrator.emit('workflowCancelled', workflow);
  }
  
  private async executeNextTask(workflow: Workflow): Promise<void> {
    // Check if workflow is complete
    if (workflow.isComplete()) {
      workflow.updateStatus(WorkflowStatus.COMPLETED);
      this.orchestrator.emit('workflowCompleted', workflow);
      return;
    }
    
    // Get next task
    const nextTask = workflow.getNextSequentialTask();
    if (!nextTask) {
      workflow.updateStatus(WorkflowStatus.COMPLETED);
      this.orchestrator.emit('workflowCompleted', workflow);
      return;
    }
    
    // If task has dependencies, check if they're all completed
    for (const dependencyId of nextTask.dependencies) {
      const dependency = workflow.getTask(dependencyId);
      if (!dependency || dependency.status !== TaskStatus.COMPLETED) {
        // Dependencies not satisfied, fail the workflow
        const error = new Error(`Task ${nextTask.id} (${nextTask.name}) dependencies not satisfied`);
        workflow.addError(error);
        workflow.updateStatus(WorkflowStatus.FAILED);
        this.orchestrator.emit('workflowFailed', workflow, error);
        return;
      }
    }
    
    // For conditional tasks, evaluate condition
    if (nextTask.type === TaskType.CONDITIONAL && nextTask.condition) {
      const shouldExecute = await this.evaluateCondition(nextTask.condition, workflow);
      if (!shouldExecute) {
        // Skip this task
        nextTask.updateStatus(TaskStatus.SKIPPED);
        workflow.advanceToNextTask();
        await this.executeNextTask(workflow);
        return;
      }
    }
    
    // Execute the task
    await this.executeTask(workflow, nextTask);
    workflow.advanceToNextTask();
  }
  
  private async evaluateCondition(condition: TaskCondition, workflow: Workflow): Promise<boolean> {
    switch (condition.type) {
      case 'expression':
        try {
          // Simple expression evaluation (not secure for production)
          // In a real implementation, use a proper expression evaluator
          const context = Object.fromEntries(workflow.context.entries());
          // eslint-disable-next-line no-new-func
          const result = new Function('context', `with(context) { return ${condition.value}; }`)(context);
          return Boolean(result);
        } catch (error) {
          console.error('Error evaluating condition expression:', error);
          return false;
        }
      
      case 'function':
        try {
          if (typeof condition.value === 'function') {
            return Boolean(await condition.value(workflow));
          }
          return false;
        } catch (error) {
          console.error('Error evaluating condition function:', error);
          return false;
        }
      
      case 'message':
        // Evaluate based on a message response
        // Implementation depends on message structure
        return false;
      
      default:
        return false;
    }
  }
}

/**
 * Parallel execution strategy for workflows
 */
export class ParallelExecutionStrategy implements WorkflowExecutionStrategy {
  private orchestrator: WorkflowOrchestrator;
  private runningTasks: Set<string> = new Set();
  
  constructor(orchestrator: WorkflowOrchestrator) {
    this.orchestrator = orchestrator;
  }
  
  async executeWorkflow(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.RUNNING);
    
    // Start all tasks that have no dependencies
    const tasksToStart = Array.from(workflow.tasks.values()).filter(task => 
      task.status === TaskStatus.PENDING && task.dependencies.length === 0
    );
    
    if (tasksToStart.length === 0) {
      // No tasks to execute
      workflow.updateStatus(WorkflowStatus.COMPLETED);
      this.orchestrator.emit('workflowCompleted', workflow);
      return;
    }
    
    // Execute all tasks in parallel
    await Promise.all(tasksToStart.map(task => this.executeTask(workflow, task)));
  }
  
  async executeTask(workflow: Workflow, task: Task): Promise<void> {
    // Get context values for task input
    const taskInput: Record<string, any> = {};
    for (const [taskParam, contextKey] of Object.entries(task.inputMapping)) {
      taskInput[taskParam] = workflow.getContextValue(contextKey);
    }
    
    // Execute task
    task.updateStatus(TaskStatus.RUNNING);
    this.runningTasks.add(task.id);
    
    try {
      // Get agent for this task
      const agent = await this.orchestrator.getAgentForTask(workflow, task);
      if (!agent) {
        throw new Error(`No agent available for task ${task.id} (${task.name})`);
      }
      
      // Create a message for the agent
      const message = new Message({
        type: MessageType.TASK_REQUEST,
        sender: 'workflow_orchestrator',
        recipient: agent.getId(),
        content: {
          workflowId: workflow.id,
          taskId: task.id,
          taskName: task.name,
          taskInput
        },
        priority: MessagePriority.NORMAL,
        metadata: {
          workflowName: workflow.name,
          taskType: task.type
        }
      });
      
      // Send message to agent
      task.assignAgent(agent.getId());
      await this.orchestrator.sendMessageToAgent(message);
      
      // Set up timeout if specified
      if (task.timeout > 0) {
        setTimeout(() => {
          if (task.status === TaskStatus.RUNNING) {
            this.handleTaskFailure(workflow, task, new Error(`Task execution timed out after ${task.timeout}ms`));
          }
        }, task.timeout);
      }
    } catch (error) {
      await this.handleTaskFailure(workflow, task, error as Error);
    }
  }
  
  async handleTaskCompletion(workflow: Workflow, task: Task, result: any): Promise<void> {
    task.updateStatus(TaskStatus.COMPLETED);
    task.setResult(result);
    this.runningTasks.delete(task.id);
    
    // Apply output mapping to workflow context
    for (const [taskOutput, contextKey] of Object.entries(task.outputMapping)) {
      if (taskOutput in result) {
        workflow.setContextValue(contextKey, result[taskOutput]);
      }
    }
    
    // Check for new tasks that can be started
    const tasksToStart = Array.from(workflow.tasks.values()).filter(t => {
      if (t.status !== TaskStatus.PENDING) {
        return false;
      }
      
      // Check if all dependencies are completed
      for (const dependencyId of t.dependencies) {
        const dependency = workflow.getTask(dependencyId);
        if (!dependency || dependency.status !== TaskStatus.COMPLETED) {
          return false;
        }
      }
      
      return true;
    });
    
    // Start all the new tasks
    await Promise.all(tasksToStart.map(t => this.executeTask(workflow, t)));
    
    // Check if workflow is complete
    this.checkWorkflowCompletion(workflow);
  }
  
  async handleTaskFailure(workflow: Workflow, task: Task, error: Error): Promise<void> {
    task.updateStatus(TaskStatus.FAILED);
    task.setError(error);
    workflow.addError(error);
    this.runningTasks.delete(task.id);
    
    // Retry the task if retries are available
    if (task.retries < task.maxRetries) {
      task.retries++;
      task.updateStatus(TaskStatus.PENDING);
      await this.executeTask(workflow, task);
      return;
    }
    
    // Try fallback task if available
    if (task.fallbackTaskId) {
      const fallbackTask = workflow.getTask(task.fallbackTaskId);
      if (fallbackTask && fallbackTask.status === TaskStatus.PENDING) {
        await this.executeTask(workflow, fallbackTask);
        return;
      }
    }
    
    // If this is a critical failure, fail the workflow
    if (task.metadata.critical === true) {
      workflow.updateStatus(WorkflowStatus.FAILED);
      this.orchestrator.emit('workflowFailed', workflow, error);
      return;
    }
    
    // Check if workflow is complete
    this.checkWorkflowCompletion(workflow);
  }
  
  async pause(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.PAUSED);
    // Note: This doesn't actually pause running tasks
    // In a real implementation, you would need to send pause signals to agents
  }
  
  async resume(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.RUNNING);
    
    // Start all tasks that have all dependencies completed
    const tasksToStart = Array.from(workflow.tasks.values()).filter(task => {
      if (task.status !== TaskStatus.PENDING) {
        return false;
      }
      
      // Check if all dependencies are completed
      for (const dependencyId of task.dependencies) {
        const dependency = workflow.getTask(dependencyId);
        if (!dependency || dependency.status !== TaskStatus.COMPLETED) {
          return false;
        }
      }
      
      return true;
    });
    
    // Start all the tasks
    await Promise.all(tasksToStart.map(task => this.executeTask(workflow, task)));
  }
  
  async cancel(workflow: Workflow): Promise<void> {
    workflow.updateStatus(WorkflowStatus.CANCELLED);
    
    // Cancel all running tasks
    for (const task of workflow.getRunningTasks()) {
      task.updateStatus(TaskStatus.CANCELLED);
    }
    
    // Mark all pending tasks as cancelled
    for (const task of workflow.getPendingTasks()) {
      task.updateStatus(TaskStatus.CANCELLED);
    }
    
    this.runningTasks.clear();
    this.orchestrator.emit('workflowCancelled', workflow);
  }
  
  private checkWorkflowCompletion(workflow: Workflow): void {
    // Check if all tasks are completed, failed, cancelled, or skipped
    if (workflow.isComplete()) {
      workflow.updateStatus(WorkflowStatus.COMPLETED);
      this.orchestrator.emit('workflowCompleted', workflow);
    } else if (this.runningTasks.size === 0 && workflow.getPendingTasks().length === 0) {
      // No running or pending tasks, but workflow is not complete
      // This can happen if there are tasks that can never be executed due to failed dependencies
      workflow.updateStatus(WorkflowStatus.FAILED);
      workflow.addError(new Error('Workflow stalled: no running or pending tasks, but workflow is not complete'));
      this.orchestrator.emit('workflowFailed', workflow, new Error('Workflow stalled'));
    }
  }
}

/**
 * Adaptive execution strategy for workflows
 */
export class AdaptiveExecutionStrategy implements WorkflowExecutionStrategy {
  private orchestrator: WorkflowOrchestrator;
  private sequentialStrategy: SequentialExecutionStrategy;
  private parallelStrategy: ParallelExecutionStrategy;
  private activeStrategy: WorkflowExecutionStrategy;
  
  constructor(orchestrator: WorkflowOrchestrator) {
    this.orchestrator = orchestrator;
    this.sequentialStrategy = new SequentialExecutionStrategy(orchestrator);
    this.parallelStrategy = new ParallelExecutionStrategy(orchestrator);
    this.activeStrategy = this.sequentialStrategy; // Default to sequential
  }
  
  async executeWorkflow(workflow: Workflow): Promise<void> {
    // Analyze workflow to determine best execution strategy
    const strategy = this.determineExecutionStrategy(workflow);
    this.activeStrategy = strategy;
    
    await strategy.executeWorkflow(workflow);
  }
  
  async executeTask(workflow: Workflow, task: Task): Promise<void> {
    await this.activeStrategy.executeTask(workflow, task);
  }
  
  async handleTaskCompletion(workflow: Workflow, task: Task, result: any): Promise<void> {
    await this.activeStrategy.handleTaskCompletion(workflow, task, result);
    
    // Re-evaluate strategy after task completion
    const newStrategy = this.determineExecutionStrategy(workflow);
    if (newStrategy !== this.activeStrategy) {
      this.activeStrategy = newStrategy;
    }
  }
  
  async handleTaskFailure(workflow: Workflow, task: Task, error: Error): Promise<void> {
    await this.activeStrategy.handleTaskFailure(workflow, task, error);
    
    // Re-evaluate strategy after task failure
    const newStrategy = this.determineExecutionStrategy(workflow);
    if (newStrategy !== this.activeStrategy) {
      this.activeStrategy = newStrategy;
    }
  }
  
  async pause(workflow: Workflow): Promise<void> {
    await this.activeStrategy.pause(workflow);
  }
  
  async resume(workflow: Workflow): Promise<void> {
    // Re-evaluate strategy before resuming
    const strategy = this.determineExecutionStrategy(workflow);
    this.activeStrategy = strategy;
    
    await strategy.resume(workflow);
  }
  
  async cancel(workflow: Workflow): Promise<void> {
    await this.activeStrategy.cancel(workflow);
  }
  
  private determineExecutionStrategy(workflow: Workflow): WorkflowExecutionStrategy {
    // Analyze workflow to determine best execution strategy
    // This is a simple implementation; in practice, this would be more sophisticated
    
    // Count tasks with dependencies
    let tasksWithDependencies = 0;
    for (const task of workflow.tasks.values()) {
      if (task.dependencies.length > 0) {
        tasksWithDependencies++;
      }
    }
    
    // Calculate dependency ratio
    const totalTasks = workflow.tasks.size;
    const dependencyRatio = totalTasks > 0 ? tasksWithDependencies / totalTasks : 0;
    
    // Check for branch patterns
    let hasBranches = false;
    for (const task of workflow.tasks.values()) {
      const dependents = Array.from(workflow.tasks.values()).filter(t => 
        t.dependencies.includes(task.id)
      );
      
      if (dependents.length > 1) {
        hasBranches = true;
        break;
      }
    }
    
    // Check for merge patterns
    let hasMerges = false;
    for (const task of workflow.tasks.values()) {
      if (task.dependencies.length > 1) {
        hasMerges = true;
        break;
      }
    }
    
    // Determine strategy based on analysis
    if (dependencyRatio < 0.3 && !hasMerges) {
      // Few dependencies and no merges, use parallel
      return this.parallelStrategy;
    } else if (hasBranches && hasMerges) {
      // Complex workflow with branches and merges, use parallel
      return this.parallelStrategy;
    } else {
      // Default to sequential
      return this.sequentialStrategy;
    }
  }
}

/**
 * Strategy factory for creating workflow execution strategies
 */
export class StrategyFactory {
  private orchestrator: WorkflowOrchestrator;
  
  constructor(orchestrator: WorkflowOrchestrator) {
    this.orchestrator = orchestrator;
  }
  
  createStrategy(mode: WorkflowExecutionMode): WorkflowExecutionStrategy {
    switch (mode) {
      case WorkflowExecutionMode.SEQUENTIAL:
        return new SequentialExecutionStrategy(this.orchestrator);
      
      case WorkflowExecutionMode.PARALLEL:
        return new ParallelExecutionStrategy(this.orchestrator);
      
      case WorkflowExecutionMode.ADAPTIVE:
        return new AdaptiveExecutionStrategy(this.orchestrator);
      
      case WorkflowExecutionMode.HYBRID:
        // For hybrid, we currently use adaptive since it can switch between strategies
        return new AdaptiveExecutionStrategy(this.orchestrator);
      
      default:
        return new SequentialExecutionStrategy(this.orchestrator);
    }
  }
}

/**
 * Orchestrates execution of workflows across multiple agents
 */
export class WorkflowOrchestrator extends EventEmitter {
  private workflows: Map<string, Workflow> = new Map();
  private templates: Map<string, WorkflowTemplate> = new Map();
  private runningWorkflows: Set<string> = new Set();
  private strategyFactory: StrategyFactory;
  private strategies: Map<string, WorkflowExecutionStrategy> = new Map();
  private supervisorGateway: SupervisorGateway;
  private agentRegistry: AgentRegistry;
  private knowledgeBaseManager: KnowledgeBaseManager;
  private isInitialized: boolean = false;
  private workflowSchedule: Map<string, NodeJS.Timeout> = new Map();
  
  constructor(
    supervisorGateway: SupervisorGateway,
    agentRegistry: AgentRegistry,
    knowledgeBaseManager: KnowledgeBaseManager
  ) {
    super();
    this.supervisorGateway = supervisorGateway;
    this.agentRegistry = agentRegistry;
    this.knowledgeBaseManager = knowledgeBaseManager;
    this.strategyFactory = new StrategyFactory(this);
  }
  
  /**
   * Initializes the workflow orchestrator
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    // Subscribe to agent messages
    this.supervisorGateway.on('message', this.handleMessage.bind(this));
    
    this.isInitialized = true;
    console.log('Workflow orchestrator initialized');
  }
  
  /**
   * Creates a new workflow
   * @param options Workflow options
   * @returns New workflow instance
   */
  createWorkflow(options: WorkflowOptions): Workflow {
    const workflow = new Workflow(options);
    this.workflows.set(workflow.id, workflow);
    return workflow;
  }
  
  /**
   * Creates a new workflow from a template
   * @param templateId Template ID
   * @param paramValues Parameter values for the template
   * @returns New workflow instance
   */
  createWorkflowFromTemplate(templateId: string, paramValues: Record<string, any> = {}): Workflow {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Workflow template '${templateId}' not found`);
    }
    
    const workflow = template.createWorkflow(paramValues);
    this.workflows.set(workflow.id, workflow);
    return workflow;
  }
  
  /**
   * Registers a workflow template
   * @param template Workflow template to register
   */
  registerTemplate(template: WorkflowTemplate): void {
    this.templates.set(template.id, template);
  }
  
  /**
   * Gets a workflow by ID
   * @param workflowId Workflow ID
   * @returns Workflow or undefined if not found
   */
  getWorkflow(workflowId: string): Workflow | undefined {
    return this.workflows.get(workflowId);
  }
  
  /**
   * Gets a workflow template by ID
   * @param templateId Template ID
   * @returns Workflow template or undefined if not found
   */
  getTemplate(templateId: string): WorkflowTemplate | undefined {
    return this.templates.get(templateId);
  }
  
  /**
   * Starts execution of a workflow
   * @param workflowId Workflow ID
   * @returns Promise that resolves when the workflow is started
   */
  async startWorkflow(workflowId: string): Promise<void> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow '${workflowId}' not found`);
    }
    
    if (workflow.status !== WorkflowStatus.PENDING) {
      throw new Error(`Workflow '${workflowId}' is already in progress or completed`);
    }
    
    // Create execution strategy
    const strategy = this.strategyFactory.createStrategy(workflow.executionMode);
    this.strategies.set(workflowId, strategy);
    
    // Mark workflow as running
    this.runningWorkflows.add(workflowId);
    
    // Set up workflow timeout if specified
    if (workflow.timeout > 0) {
      const timeoutId = setTimeout(() => {
        if (this.runningWorkflows.has(workflowId)) {
          const error = new Error(`Workflow execution timed out after ${workflow.timeout}ms`);
          this.handleWorkflowError(workflow, error);
        }
      }, workflow.timeout);
      
      this.workflowSchedule.set(workflowId, timeoutId);
    }
    
    // Emit event
    this.emit('workflowStarted', workflow);
    
    // Start execution
    try {
      await strategy.executeWorkflow(workflow);
    } catch (error) {
      this.handleWorkflowError(workflow, error as Error);
    }
  }
  
  /**
   * Pauses execution of a workflow
   * @param workflowId Workflow ID
   * @returns Promise that resolves when the workflow is paused
   */
  async pauseWorkflow(workflowId: string): Promise<void> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow '${workflowId}' not found`);
    }
    
    if (workflow.status !== WorkflowStatus.RUNNING) {
      throw new Error(`Workflow '${workflowId}' is not running`);
    }
    
    const strategy = this.strategies.get(workflowId);
    if (!strategy) {
      throw new Error(`No execution strategy found for workflow '${workflowId}'`);
    }
    
    await strategy.pause(workflow);
    this.emit('workflowPaused', workflow);
  }
  
  /**
   * Resumes execution of a paused workflow
   * @param workflowId Workflow ID
   * @returns Promise that resolves when the workflow is resumed
   */
  async resumeWorkflow(workflowId: string): Promise<void> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow '${workflowId}' not found`);
    }
    
    if (workflow.status !== WorkflowStatus.PAUSED) {
      throw new Error(`Workflow '${workflowId}' is not paused`);
    }
    
    const strategy = this.strategies.get(workflowId);
    if (!strategy) {
      throw new Error(`No execution strategy found for workflow '${workflowId}'`);
    }
    
    await strategy.resume(workflow);
    this.emit('workflowResumed', workflow);
  }
  
  /**
   * Cancels execution of a workflow
   * @param workflowId Workflow ID
   * @returns Promise that resolves when the workflow is cancelled
   */
  async cancelWorkflow(workflowId: string): Promise<void> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow '${workflowId}' not found`);
    }
    
    if (![WorkflowStatus.RUNNING, WorkflowStatus.PAUSED].includes(workflow.status)) {
      throw new Error(`Workflow '${workflowId}' is not running or paused`);
    }
    
    const strategy = this.strategies.get(workflowId);
    if (!strategy) {
      throw new Error(`No execution strategy found for workflow '${workflowId}'`);
    }
    
    await strategy.cancel(workflow);
    this.runningWorkflows.delete(workflowId);
    
    // Clear timeout if exists
    const timeoutId = this.workflowSchedule.get(workflowId);
    if (timeoutId) {
      clearTimeout(timeoutId);
      this.workflowSchedule.delete(workflowId);
    }
  }
  
  /**
   * Gets an agent for a task
   * @param workflow Workflow
   * @param task Task
   * @returns Agent for the task or undefined if no agent is available
   */
  async getAgentForTask(workflow: Workflow, task: Task): Promise<Agent | undefined> {
    // If specific agent ID is specified, use that
    if (task.agentId) {
      const agent = this.agentRegistry.getAgent(task.agentId);
      if (!agent) {
        throw new Error(`Agent '${task.agentId}' not found`);
      }
      return agent;
    }
    
    // If agent type is specified, find an agent of that type
    if (task.agentType) {
      const agents = this.agentRegistry.getAgentsByType(task.agentType);
      if (agents.length === 0) {
        throw new Error(`No agents of type '${task.agentType}' found`);
      }
      
      // Simple load balancing - select agent with fewest active tasks
      let bestAgent: Agent | undefined;
      let minActiveTasks = Number.MAX_SAFE_INTEGER;
      
      for (const agent of agents) {
        const activeTasks = this.getActiveTasksCount(agent.getId());
        if (activeTasks < minActiveTasks) {
          minActiveTasks = activeTasks;
          bestAgent = agent;
        }
      }
      
      return bestAgent;
    }
    
    // Otherwise, find any available agent that can handle the task
    // This would involve more complex logic in a real implementation
    
    return undefined;
  }
  
  /**
   * Gets the number of active tasks for an agent
   * @param agentId Agent ID
   * @returns Number of active tasks
   */
  private getActiveTasksCount(agentId: string): number {
    let count = 0;
    
    for (const workflow of this.workflows.values()) {
      if (workflow.status !== WorkflowStatus.RUNNING) {
        continue;
      }
      
      for (const task of workflow.getRunningTasks()) {
        if (task.assignedAgentId === agentId) {
          count++;
        }
      }
    }
    
    return count;
  }
  
  /**
   * Sends a message to an agent
   * @param message Message to send
   */
  async sendMessageToAgent(message: Message): Promise<void> {
    await this.supervisorGateway.sendMessage(message);
  }
  
  /**
   * Handles a message from an agent
   * @param message Message from agent
   */
  private async handleMessage(message: Message): Promise<void> {
    // Check if this is a task response
    if (message.type === MessageType.TASK_RESPONSE) {
      const content = message.content;
      if (content && content.workflowId && content.taskId) {
        await this.handleTaskResponse(content.workflowId, content.taskId, content);
      }
    }
  }
  
  /**
   * Handles a task response from an agent
   * @param workflowId Workflow ID
   * @param taskId Task ID
   * @param response Task response
   */
  private async handleTaskResponse(workflowId: string, taskId: string, response: any): Promise<void> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      console.error(`Workflow '${workflowId}' not found for task response`);
      return;
    }
    
    const task = workflow.getTask(taskId);
    if (!task) {
      console.error(`Task '${taskId}' not found in workflow '${workflowId}'`);
      return;
    }
    
    const strategy = this.strategies.get(workflowId);
    if (!strategy) {
      console.error(`No execution strategy found for workflow '${workflowId}'`);
      return;
    }
    
    if (response.error) {
      // Task failed
      await strategy.handleTaskFailure(workflow, task, new Error(response.error));
    } else {
      // Task completed successfully
      await strategy.handleTaskCompletion(workflow, task, response.result || {});
    }
  }
  
  /**
   * Handles a workflow error
   * @param workflow Workflow
   * @param error Error
   */
  private handleWorkflowError(workflow: Workflow, error: Error): void {
    workflow.addError(error);
    workflow.updateStatus(WorkflowStatus.FAILED);
    this.runningWorkflows.delete(workflow.id);
    
    // Clear timeout if exists
    const timeoutId = this.workflowSchedule.get(workflow.id);
    if (timeoutId) {
      clearTimeout(timeoutId);
      this.workflowSchedule.delete(workflow.id);
    }
    
    this.emit('workflowFailed', workflow, error);
  }
  
  /**
   * Gets all registered workflow templates
   * @returns Array of workflow templates
   */
  getTemplates(): WorkflowTemplate[] {
    return Array.from(this.templates.values());
  }
  
  /**
   * Gets all workflows
   * @returns Array of workflows
   */
  getWorkflows(): Workflow[] {
    return Array.from(this.workflows.values());
  }
  
  /**
   * Gets running workflows
   * @returns Array of running workflows
   */
  getRunningWorkflows(): Workflow[] {
    return this.getWorkflows().filter(wf => this.runningWorkflows.has(wf.id));
  }
  
  /**
   * Gets workflow statistics
   * @returns Object with workflow statistics
   */
  getStatistics(): Record<string, any> {
    const totalWorkflows = this.workflows.size;
    const runningWorkflows = this.runningWorkflows.size;
    const completedWorkflows = this.getWorkflows().filter(wf => wf.status === WorkflowStatus.COMPLETED).length;
    const failedWorkflows = this.getWorkflows().filter(wf => wf.status === WorkflowStatus.FAILED).length;
    const pendingWorkflows = this.getWorkflows().filter(wf => wf.status === WorkflowStatus.PENDING).length;
    const pausedWorkflows = this.getWorkflows().filter(wf => wf.status === WorkflowStatus.PAUSED).length;
    const cancelledWorkflows = this.getWorkflows().filter(wf => wf.status === WorkflowStatus.CANCELLED).length;
    
    return {
      totalWorkflows,
      runningWorkflows,
      completedWorkflows,
      failedWorkflows,
      pendingWorkflows,
      pausedWorkflows,
      cancelledWorkflows,
      templates: this.templates.size
    };
  }
}

export default WorkflowOrchestrator;