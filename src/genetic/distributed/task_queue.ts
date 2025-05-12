import { 
  DistributedTask, 
  TaskStatus, 
  TaskProgressUpdate,
  SchedulingStrategy
} from './distributed_types';
import { EventEmitter } from 'events';

/**
 * Task queue for distributed task management.
 * Handles task submission, scheduling, tracking, and retrieval.
 */
export class TaskQueue extends EventEmitter {
  private pendingTasks: Map<string, DistributedTask> = new Map();
  private runningTasks: Map<string, DistributedTask> = new Map();
  private completedTasks: Map<string, DistributedTask> = new Map();
  private failedTasks: Map<string, DistributedTask> = new Map();
  private taskHistory: DistributedTask[] = [];
  private taskTimeout: NodeJS.Timeout | null = null;
  private maxHistorySize: number;
  private taskTimeoutMs: number;
  private schedulingStrategy: SchedulingStrategy;
  
  /**
   * Creates a new task queue
   * @param options Task queue options
   */
  constructor(options: TaskQueueOptions = {}) {
    super();
    
    this.maxHistorySize = options.maxHistorySize || 1000;
    this.taskTimeoutMs = options.taskTimeoutMs || 60000; // 1 minute default
    this.schedulingStrategy = options.schedulingStrategy || SchedulingStrategy.ROUND_ROBIN;
    
    // Start timeout checker
    this.startTimeoutChecker();
  }
  
  /**
   * Add a task to the queue
   * @param task Task to add
   * @returns The submitted task with generated ID
   */
  public submitTask<T, R>(task: Omit<DistributedTask<T, R>, 'id' | 'status' | 'createdAt'>): DistributedTask<T, R> {
    const taskId = this.generateTaskId();
    
    const fullTask: DistributedTask<T, R> = {
      ...task,
      id: taskId,
      status: TaskStatus.PENDING,
      createdAt: Date.now(),
      attempts: 0,
      maxAttempts: task.maxAttempts || 3
    };
    
    this.pendingTasks.set(taskId, fullTask);
    
    this.emit('taskSubmitted', fullTask);
    
    return fullTask;
  }
  
  /**
   * Generate a unique task ID
   * @returns Unique task ID
   */
  private generateTaskId(): string {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 10000);
    return `task_${timestamp}_${random}`;
  }
  
  /**
   * Get the next pending task based on scheduling strategy
   * @param nodeId ID of the node requesting a task
   * @param capabilities Capabilities of the node
   * @returns The next task to process, or undefined if no tasks are pending
   */
  public getNextTask(nodeId: string, capabilities: string[] = []): DistributedTask | undefined {
    if (this.pendingTasks.size === 0) {
      return undefined;
    }
    
    let selectedTask: DistributedTask | undefined;
    
    switch (this.schedulingStrategy) {
      case SchedulingStrategy.ROUND_ROBIN:
        // Simple round-robin: get the first task
        selectedTask = this.pendingTasks.values().next().value;
        break;
        
      case SchedulingStrategy.SPECIALIZED:
        // Find a task that matches node capabilities
        for (const task of this.pendingTasks.values()) {
          const taskType = task.type.toString();
          
          if (capabilities.includes(taskType)) {
            selectedTask = task;
            break;
          }
        }
        
        // If no specialized task found, fall back to first task
        if (!selectedTask) {
          selectedTask = this.pendingTasks.values().next().value;
        }
        break;
        
      case SchedulingStrategy.LEAST_BUSY:
      case SchedulingStrategy.FASTEST_NODE:
      case SchedulingStrategy.RANDOM:
      default:
        // These strategies are handled by the coordinator, so just return the first task
        selectedTask = this.pendingTasks.values().next().value;
        break;
    }
    
    if (selectedTask) {
      // Remove from pending and add to running
      this.pendingTasks.delete(selectedTask.id);
      
      selectedTask.status = TaskStatus.RUNNING;
      selectedTask.startedAt = Date.now();
      selectedTask.assignedTo = nodeId;
      selectedTask.attempts = (selectedTask.attempts || 0) + 1;
      
      this.runningTasks.set(selectedTask.id, selectedTask);
      
      this.emit('taskStarted', selectedTask);
    }
    
    return selectedTask;
  }
  
  /**
   * Update a task's progress
   * @param update Task progress update
   */
  public updateTaskProgress(update: TaskProgressUpdate): void {
    const { taskId, status, progress, message, intermediateResult } = update;
    
    const task = this.runningTasks.get(taskId);
    
    if (!task) {
      return;
    }
    
    // Update task status
    task.status = status;
    
    // If task is complete, move to completed tasks
    if (status === TaskStatus.COMPLETED) {
      task.completedAt = Date.now();
      this.runningTasks.delete(taskId);
      this.completedTasks.set(taskId, task);
      this.addToHistory(task);
      
      this.emit('taskCompleted', task);
    }
    // If task failed, move to failed tasks
    else if (status === TaskStatus.FAILED) {
      task.completedAt = Date.now();
      task.error = message;
      
      this.runningTasks.delete(taskId);
      
      // Check if task can be retried
      if ((task.attempts || 0) < (task.maxAttempts || 3)) {
        // Reset task status for retry
        task.status = TaskStatus.PENDING;
        task.startedAt = undefined;
        task.assignedTo = undefined;
        
        this.pendingTasks.set(taskId, task);
        
        this.emit('taskRetry', task);
      } else {
        this.failedTasks.set(taskId, task);
        this.addToHistory(task);
        
        this.emit('taskFailed', task);
      }
    }
    // Update intermediate result
    else if (intermediateResult) {
      task.result = intermediateResult;
      
      this.emit('taskProgress', update);
    }
  }
  
  /**
   * Complete a task with result
   * @param taskId Task ID
   * @param result Task result
   * @returns The completed task
   */
  public completeTask<T, R>(taskId: string, result: R): DistributedTask<T, R> | undefined {
    const task = this.runningTasks.get(taskId) as DistributedTask<T, R>;
    
    if (!task) {
      return undefined;
    }
    
    task.status = TaskStatus.COMPLETED;
    task.completedAt = Date.now();
    task.result = result;
    
    this.runningTasks.delete(taskId);
    this.completedTasks.set(taskId, task);
    this.addToHistory(task);
    
    this.emit('taskCompleted', task);
    
    return task;
  }
  
  /**
   * Mark a task as failed
   * @param taskId Task ID
   * @param error Error message
   * @returns The failed task
   */
  public failTask<T, R>(taskId: string, error: string): DistributedTask<T, R> | undefined {
    const task = this.runningTasks.get(taskId) as DistributedTask<T, R>;
    
    if (!task) {
      return undefined;
    }
    
    task.status = TaskStatus.FAILED;
    task.completedAt = Date.now();
    task.error = error;
    
    this.runningTasks.delete(taskId);
    
    // Check if task can be retried
    if ((task.attempts || 0) < (task.maxAttempts || 3)) {
      // Reset task status for retry
      task.status = TaskStatus.PENDING;
      task.startedAt = undefined;
      task.assignedTo = undefined;
      
      this.pendingTasks.set(taskId, task);
      
      this.emit('taskRetry', task);
    } else {
      this.failedTasks.set(taskId, task);
      this.addToHistory(task);
      
      this.emit('taskFailed', task);
    }
    
    return task;
  }
  
  /**
   * Get a task by ID
   * @param taskId Task ID
   * @returns The task, or undefined if not found
   */
  public getTask<T, R>(taskId: string): DistributedTask<T, R> | undefined {
    return (
      this.pendingTasks.get(taskId) ||
      this.runningTasks.get(taskId) ||
      this.completedTasks.get(taskId) ||
      this.failedTasks.get(taskId)
    ) as DistributedTask<T, R> | undefined;
  }
  
  /**
   * Get all tasks
   * @returns All tasks
   */
  public getAllTasks(): {
    pending: DistributedTask[];
    running: DistributedTask[];
    completed: DistributedTask[];
    failed: DistributedTask[];
  } {
    return {
      pending: Array.from(this.pendingTasks.values()),
      running: Array.from(this.runningTasks.values()),
      completed: Array.from(this.completedTasks.values()),
      failed: Array.from(this.failedTasks.values())
    };
  }
  
  /**
   * Get task counts
   * @returns Task counts
   */
  public getTaskCounts(): TaskCounts {
    return {
      pending: this.pendingTasks.size,
      running: this.runningTasks.size,
      completed: this.completedTasks.size,
      failed: this.failedTasks.size,
      total: this.pendingTasks.size + this.runningTasks.size + 
             this.completedTasks.size + this.failedTasks.size
    };
  }
  
  /**
   * Add a task to history
   * @param task Task to add to history
   */
  private addToHistory(task: DistributedTask): void {
    this.taskHistory.unshift(task);
    
    // Trim history if needed
    if (this.taskHistory.length > this.maxHistorySize) {
      this.taskHistory.pop();
    }
  }
  
  /**
   * Get task history
   * @param limit Maximum number of tasks to return
   * @returns Task history
   */
  public getTaskHistory(limit: number = 100): DistributedTask[] {
    return this.taskHistory.slice(0, limit);
  }
  
  /**
   * Check for timed out tasks
   */
  private checkTaskTimeouts(): void {
    const now = Date.now();
    
    for (const task of this.runningTasks.values()) {
      if (!task.startedAt) {
        continue;
      }
      
      const timeoutMs = task.timeoutMs || this.taskTimeoutMs;
      const elapsedTime = now - task.startedAt;
      
      if (elapsedTime > timeoutMs) {
        // Task has timed out
        task.status = TaskStatus.TIMEOUT;
        task.completedAt = now;
        task.error = `Task timed out after ${elapsedTime}ms`;
        
        this.runningTasks.delete(task.id);
        
        // Check if task can be retried
        if ((task.attempts || 0) < (task.maxAttempts || 3)) {
          // Reset task status for retry
          task.status = TaskStatus.PENDING;
          task.startedAt = undefined;
          task.assignedTo = undefined;
          
          this.pendingTasks.set(task.id, task);
          
          this.emit('taskRetry', task);
        } else {
          this.failedTasks.set(task.id, task);
          this.addToHistory(task);
          
          this.emit('taskTimeout', task);
        }
      }
    }
  }
  
  /**
   * Start the timeout checker
   */
  private startTimeoutChecker(): void {
    if (this.taskTimeout) {
      clearInterval(this.taskTimeout);
    }
    
    this.taskTimeout = setInterval(() => {
      this.checkTaskTimeouts();
    }, 5000); // Check every 5 seconds
  }
  
  /**
   * Stop the timeout checker
   */
  public stopTimeoutChecker(): void {
    if (this.taskTimeout) {
      clearInterval(this.taskTimeout);
      this.taskTimeout = null;
    }
  }
  
  /**
   * Clean up completed and failed tasks older than a certain age
   * @param maxAgeMs Maximum age in milliseconds
   */
  public cleanupOldTasks(maxAgeMs: number = 24 * 60 * 60 * 1000): void {
    const now = Date.now();
    
    // Clean up completed tasks
    for (const [taskId, task] of this.completedTasks.entries()) {
      if (task.completedAt && now - task.completedAt > maxAgeMs) {
        this.completedTasks.delete(taskId);
      }
    }
    
    // Clean up failed tasks
    for (const [taskId, task] of this.failedTasks.entries()) {
      if (task.completedAt && now - task.completedAt > maxAgeMs) {
        this.failedTasks.delete(taskId);
      }
    }
  }
}

/**
 * Task queue options
 */
export interface TaskQueueOptions {
  /**
   * Maximum number of tasks to keep in history
   */
  maxHistorySize?: number;
  
  /**
   * Default task timeout in milliseconds
   */
  taskTimeoutMs?: number;
  
  /**
   * Task scheduling strategy
   */
  schedulingStrategy?: SchedulingStrategy;
}

/**
 * Task counts
 */
export interface TaskCounts {
  /**
   * Number of pending tasks
   */
  pending: number;
  
  /**
   * Number of running tasks
   */
  running: number;
  
  /**
   * Number of completed tasks
   */
  completed: number;
  
  /**
   * Number of failed tasks
   */
  failed: number;
  
  /**
   * Total number of tasks
   */
  total: number;
}