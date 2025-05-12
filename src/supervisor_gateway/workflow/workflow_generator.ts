/**
 * Dynamic workflow generation system
 */

import { v4 as uuidv4 } from 'uuid';
import { 
  Workflow, 
  WorkflowOptions, 
  Task, 
  TaskOptions, 
  TaskType, 
  WorkflowExecutionMode,
  TaskCondition,
  CoordinationStrategy,
  WorkflowTemplate
} from './workflow_orchestrator';
import { 
  WorkflowPatternFactory, 
  DomainWorkflowFactory, 
  DomainTaskFactory,
  WorkflowPattern,
  FlowControlType
} from './workflow_models';

/**
 * Context for workflow generation
 */
export interface GenerationContext {
  domain: string;                  // Domain for the workflow
  taskTypes: string[];             // Types of tasks to include
  agentTypes: string[];            // Types of agents to include
  constraints: Record<string, any>; // Constraints for generation
  parameters: Record<string, any>;  // Parameters for generation
  objectives: string[];            // Objectives for the workflow
  requiredPatterns?: WorkflowPattern[]; // Patterns that must be included
  complexityLevel: number;         // Complexity level (1-10)
  maxTasks?: number;               // Maximum number of tasks
  seed?: string;                   // Seed for randomization
  metadata?: Record<string, any>;  // Additional metadata
}

/**
 * Strategy for workflow generation
 */
export interface GenerationStrategy {
  generateWorkflow(context: GenerationContext): Workflow;
  generateTask(context: GenerationContext, options?: Partial<TaskOptions>): Task;
  generateWorkflowTemplate(context: GenerationContext): WorkflowTemplate;
}

/**
 * Result of workflow generation
 */
export interface GenerationResult {
  workflow: Workflow;
  context: GenerationContext;
  metadata: {
    generationTime: number;
    taskCount: number;
    patternCount: number;
    complexity: number;
  };
  validationResult?: ValidationResult;
}

/**
 * Result of workflow validation
 */
export interface ValidationResult {
  isValid: boolean;
  issues: ValidationIssue[];
  score: number;
  metadata: Record<string, any>;
}

/**
 * Issue found during workflow validation
 */
export interface ValidationIssue {
  type: 'error' | 'warning' | 'info';
  message: string;
  taskId?: string;
  severity: number; // 1-10
  recommendation?: string;
}

/**
 * Base class for workflow generators
 */
export abstract class WorkflowGenerator implements GenerationStrategy {
  /**
   * Generates a workflow based on the given context
   * @param context Generation context
   * @returns Generated workflow
   */
  abstract generateWorkflow(context: GenerationContext): Workflow;
  
  /**
   * Generates a task based on the given context
   * @param context Generation context
   * @param options Optional task options
   * @returns Generated task
   */
  abstract generateTask(context: GenerationContext, options?: Partial<TaskOptions>): Task;
  
  /**
   * Generates a workflow template based on the given context
   * @param context Generation context
   * @returns Generated workflow template
   */
  abstract generateWorkflowTemplate(context: GenerationContext): WorkflowTemplate;
  
  /**
   * Validates a generated workflow
   * @param workflow Workflow to validate
   * @param context Generation context
   * @returns Validation result
   */
  validateWorkflow(workflow: Workflow, context: GenerationContext): ValidationResult {
    const issues: ValidationIssue[] = [];
    
    // Check for empty workflow
    if (workflow.tasks.size === 0) {
      issues.push({
        type: 'error',
        message: 'Workflow has no tasks',
        severity: 10,
        recommendation: 'Add at least one task to the workflow'
      });
    }
    
    // Check for disconnected tasks
    const connectedTasks = new Set<string>();
    const allTaskIds = Array.from(workflow.tasks.keys());
    
    // Start with tasks that have no dependencies
    const startTasks = Array.from(workflow.tasks.values())
      .filter(task => task.dependencies.length === 0)
      .map(task => task.id);
    
    if (startTasks.length === 0) {
      issues.push({
        type: 'error',
        message: 'Workflow has no starting tasks (tasks without dependencies)',
        severity: 9,
        recommendation: 'Add at least one task without dependencies'
      });
    }
    
    // Traverse the dependency graph
    const toVisit = [...startTasks];
    while (toVisit.length > 0) {
      const taskId = toVisit.shift()!;
      connectedTasks.add(taskId);
      
      // Find tasks that depend on this task
      const dependentTasks = Array.from(workflow.tasks.values())
        .filter(task => task.dependencies.includes(taskId))
        .map(task => task.id);
      
      // Add dependent tasks to visit queue if not already visited
      for (const dependentId of dependentTasks) {
        if (!connectedTasks.has(dependentId)) {
          toVisit.push(dependentId);
        }
      }
    }
    
    // Find disconnected tasks
    const disconnectedTasks = allTaskIds.filter(id => !connectedTasks.has(id));
    if (disconnectedTasks.length > 0) {
      issues.push({
        type: 'error',
        message: `Workflow has ${disconnectedTasks.length} disconnected tasks`,
        severity: 8,
        recommendation: 'Connect all tasks to the workflow or remove disconnected tasks'
      });
      
      // Add issues for each disconnected task
      for (const taskId of disconnectedTasks) {
        const task = workflow.getTask(taskId);
        if (task) {
          issues.push({
            type: 'error',
            message: `Task '${task.name}' (${taskId}) is disconnected from the workflow`,
            taskId,
            severity: 7,
            recommendation: 'Connect this task to the workflow or remove it'
          });
        }
      }
    }
    
    // Check for circular dependencies
    const circularDependencies = this.findCircularDependencies(workflow);
    if (circularDependencies.length > 0) {
      issues.push({
        type: 'error',
        message: `Workflow has ${circularDependencies.length} circular dependencies`,
        severity: 10,
        recommendation: 'Remove circular dependencies to ensure the workflow can execute'
      });
      
      // Add issues for each circular dependency
      for (const cycle of circularDependencies) {
        issues.push({
          type: 'error',
          message: `Circular dependency: ${cycle.join(' -> ')} -> ${cycle[0]}`,
          severity: 9,
          recommendation: 'Break the circular dependency by removing one of the dependencies'
        });
      }
    }
    
    // Check for missing agent types
    const requiredAgentTypes = new Set<string>();
    for (const task of workflow.tasks.values()) {
      if (task.agentType) {
        requiredAgentTypes.add(task.agentType);
      }
    }
    
    const missingAgentTypes = Array.from(requiredAgentTypes)
      .filter(agentType => !context.agentTypes.includes(agentType));
    
    if (missingAgentTypes.length > 0) {
      issues.push({
        type: 'warning',
        message: `Workflow requires agent types not provided in context: ${missingAgentTypes.join(', ')}`,
        severity: 6,
        recommendation: 'Add required agent types to the context or change task agent types'
      });
    }
    
    // Check for complex workflow structure
    if (workflow.tasks.size > 20 && context.complexityLevel < 8) {
      issues.push({
        type: 'warning',
        message: `Workflow is complex (${workflow.tasks.size} tasks) but complexity level is low (${context.complexityLevel})`,
        severity: 4,
        recommendation: 'Consider simplifying the workflow or increasing the complexity level'
      });
    }
    
    // Calculate validation score
    const errorCount = issues.filter(issue => issue.type === 'error').length;
    const warningCount = issues.filter(issue => issue.type === 'warning').length;
    const infoCount = issues.filter(issue => issue.type === 'info').length;
    
    // Calculate score (0-100)
    let score = 100;
    score -= errorCount * 20; // Each error reduces score by 20
    score -= warningCount * 5; // Each warning reduces score by 5
    score -= infoCount * 1; // Each info reduces score by 1
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(100, score));
    
    return {
      isValid: errorCount === 0,
      issues,
      score,
      metadata: {
        errorCount,
        warningCount,
        infoCount,
        taskCount: workflow.tasks.size,
        connectedTaskCount: connectedTasks.size,
        disconnectedTaskCount: disconnectedTasks.length,
        circularDependencyCount: circularDependencies.length
      }
    };
  }
  
  /**
   * Finds circular dependencies in a workflow
   * @param workflow Workflow to analyze
   * @returns Array of circular dependency paths
   */
  private findCircularDependencies(workflow: Workflow): string[][] {
    const cycles: string[][] = [];
    const visited = new Set<string>();
    const path: string[] = [];
    const pathSet = new Set<string>();
    
    // Helper function for DFS
    const dfs = (taskId: string): void => {
      if (pathSet.has(taskId)) {
        // Found a cycle
        const cycleStart = path.indexOf(taskId);
        cycles.push(path.slice(cycleStart));
        return;
      }
      
      if (visited.has(taskId)) {
        return;
      }
      
      visited.add(taskId);
      path.push(taskId);
      pathSet.add(taskId);
      
      const task = workflow.getTask(taskId);
      if (task) {
        for (const dependentId of this.findDependents(workflow, taskId)) {
          dfs(dependentId);
        }
      }
      
      path.pop();
      pathSet.delete(taskId);
    };
    
    // Start DFS from each task
    for (const taskId of workflow.tasks.keys()) {
      if (!visited.has(taskId)) {
        dfs(taskId);
      }
    }
    
    return cycles;
  }
  
  /**
   * Finds tasks that depend on a given task
   * @param workflow Workflow to analyze
   * @param taskId Task ID to find dependents for
   * @returns Array of task IDs that depend on the given task
   */
  private findDependents(workflow: Workflow, taskId: string): string[] {
    return Array.from(workflow.tasks.values())
      .filter(task => task.dependencies.includes(taskId))
      .map(task => task.id);
  }
  
  /**
   * Creates a workflow with validation
   * @param context Generation context
   * @returns Generation result
   */
  createWorkflow(context: GenerationContext): GenerationResult {
    const startTime = Date.now();
    
    // Generate workflow
    const workflow = this.generateWorkflow(context);
    
    // Validate workflow
    const validationResult = this.validateWorkflow(workflow, context);
    
    const endTime = Date.now();
    const generationTime = endTime - startTime;
    
    // Create result
    return {
      workflow,
      context,
      metadata: {
        generationTime,
        taskCount: workflow.tasks.size,
        patternCount: context.requiredPatterns?.length || 0,
        complexity: context.complexityLevel
      },
      validationResult
    };
  }
  
  /**
   * Creates a task from options
   * @param options Task options
   * @returns Task instance
   */
  protected createTask(options: TaskOptions): Task {
    return new Task(options);
  }
}

/**
 * Template-based workflow generator
 */
export class TemplateWorkflowGenerator extends WorkflowGenerator {
  private templates: Map<string, WorkflowTemplate> = new Map();
  
  /**
   * Registers a workflow template
   * @param template Workflow template to register
   */
  registerTemplate(template: WorkflowTemplate): void {
    this.templates.set(template.id, template);
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
   * Gets all registered templates
   * @returns Array of workflow templates
   */
  getTemplates(): WorkflowTemplate[] {
    return Array.from(this.templates.values());
  }
  
  /**
   * Gets templates for a specific domain
   * @param domain Domain name
   * @returns Array of workflow templates for the domain
   */
  getTemplatesForDomain(domain: string): WorkflowTemplate[] {
    return this.getTemplates().filter(template => 
      template.metadata.domain === domain
    );
  }
  
  /**
   * Generates a workflow based on the given context
   * @param context Generation context
   * @returns Generated workflow
   */
  generateWorkflow(context: GenerationContext): Workflow {
    // Find suitable template for the domain
    const templates = this.getTemplatesForDomain(context.domain);
    
    if (templates.length === 0) {
      // No templates found, create a new template first
      const template = this.generateWorkflowTemplate(context);
      this.registerTemplate(template);
      
      // Create workflow from template
      return template.createWorkflow(context.parameters);
    }
    
    // Find best matching template
    const template = this.findBestTemplate(templates, context);
    
    // Create workflow from template
    return template.createWorkflow(context.parameters);
  }
  
  /**
   * Generates a task based on the given context
   * @param context Generation context
   * @param options Optional task options
   * @returns Generated task
   */
  generateTask(context: GenerationContext, options: Partial<TaskOptions> = {}): Task {
    // Use domain-specific task factory based on context
    let taskOptions: TaskOptions;
    
    switch (context.domain) {
      case 'economic':
        taskOptions = {
          ...DomainTaskFactory.createEconomicDataGatheringTask('Economic Data Task'),
          ...options
        };
        break;
        
      case 'healthcare':
        taskOptions = {
          ...DomainTaskFactory.createHealthcareDataProcessingTask('Healthcare Data Task'),
          ...options
        };
        break;
        
      case 'governance':
        taskOptions = {
          ...DomainTaskFactory.createPolicyFormulationTask('Policy Task'),
          ...options
        };
        break;
        
      case 'data_analysis':
        taskOptions = {
          ...DomainTaskFactory.createDataVisualizationTask('Data Analysis Task'),
          ...options
        };
        break;
        
      case 'coordination':
        taskOptions = {
          ...DomainTaskFactory.createWorkflowCoordinationTask('Coordination Task'),
          ...options
        };
        break;
        
      default:
        // Default task options
        taskOptions = {
          name: options.name || 'Generic Task',
          description: options.description || 'A generic task',
          type: options.type || TaskType.SEQUENTIAL,
          timeout: options.timeout || 60000, // 1 minute
          retries: options.retries || 3,
          priority: options.priority || 5,
          ...options
        };
    }
    
    // Create task
    return this.createTask(taskOptions);
  }
  
  /**
   * Generates a workflow template based on the given context
   * @param context Generation context
   * @returns Generated workflow template
   */
  generateWorkflowTemplate(context: GenerationContext): WorkflowTemplate {
    // Use domain-specific template factory based on context
    let templateOptions: any;
    const templateId = `${context.domain}_${uuidv4().substring(0, 8)}`;
    const templateVersion = '1.0.0';
    
    switch (context.domain) {
      case 'economic':
        templateOptions = DomainWorkflowFactory.createEconomicAnalysisWorkflow(
          'Economic Analysis Workflow',
          templateVersion
        );
        break;
        
      case 'healthcare':
        templateOptions = DomainWorkflowFactory.createHealthcareWorkflow(
          'Healthcare Workflow',
          templateVersion
        );
        break;
        
      case 'governance':
        templateOptions = DomainWorkflowFactory.createPolicyAnalysisWorkflow(
          'Policy Analysis Workflow',
          templateVersion
        );
        break;
        
      case 'data_analysis':
        templateOptions = DomainWorkflowFactory.createDataAnalysisWorkflow(
          'Data Analysis Workflow',
          templateVersion
        );
        break;
        
      case 'coordination':
        templateOptions = DomainWorkflowFactory.createCoordinationWorkflow(
          'Coordination Workflow',
          templateVersion
        );
        break;
        
      default:
        // Default template options
        templateOptions = {
          id: templateId,
          name: 'Generic Workflow',
          description: 'A generic workflow template',
          version: templateVersion,
          executionMode: WorkflowExecutionMode.SEQUENTIAL,
          coordinationStrategy: CoordinationStrategy.CENTRALIZED,
          parameters: [],
          requiredAgentTypes: context.agentTypes,
          timeout: 3600000, // 1 hour
          metadata: {
            domain: context.domain,
            complexity: context.complexityLevel,
            estimatedDuration: 1800000 // 30 minutes
          },
          tags: [context.domain, 'generic', 'template']
        };
    }
    
    // Override ID if it was the same
    templateOptions.id = templateId;
    
    // Create template
    const template = new WorkflowTemplate(templateOptions);
    
    // Add tasks based on required patterns
    if (context.requiredPatterns && context.requiredPatterns.length > 0) {
      this.addPatternsToTemplate(template, context);
    } else {
      // Add default pattern based on context
      this.addDefaultPatternToTemplate(template, context);
    }
    
    return template;
  }
  
  /**
   * Finds the best matching template for the given context
   * @param templates Array of workflow templates
   * @param context Generation context
   * @returns Best matching template
   */
  private findBestTemplate(templates: WorkflowTemplate[], context: GenerationContext): WorkflowTemplate {
    // Simple scoring based on matching agent types
    let bestTemplate = templates[0];
    let bestScore = -1;
    
    for (const template of templates) {
      let score = 0;
      
      // Score based on matching agent types
      const matchingAgentTypes = template.requiredAgentTypes.filter(type => 
        context.agentTypes.includes(type)
      );
      score += matchingAgentTypes.length * 2;
      
      // Score based on template complexity matching context complexity
      const templateComplexity = template.taskTemplates.size;
      const complexityDiff = Math.abs(templateComplexity - context.complexityLevel);
      score -= complexityDiff;
      
      // Score based on matching task types
      const taskTypes = new Set<string>();
      for (const task of template.taskTemplates.values()) {
        if (task.type) {
          taskTypes.add(task.type.toString());
        }
      }
      
      const matchingTaskTypes = Array.from(taskTypes).filter(type => 
        context.taskTypes.includes(type)
      );
      score += matchingTaskTypes.length;
      
      // Update best template if score is higher
      if (score > bestScore) {
        bestScore = score;
        bestTemplate = template;
      }
    }
    
    return bestTemplate;
  }
  
  /**
   * Adds task patterns to a workflow template
   * @param template Workflow template
   * @param context Generation context
   */
  private addPatternsToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    if (!context.requiredPatterns) return;
    
    for (const pattern of context.requiredPatterns) {
      switch (pattern) {
        case WorkflowPattern.SEQUENTIAL:
          this.addSequentialPatternToTemplate(template, context);
          break;
          
        case WorkflowPattern.PARALLEL_SPLIT:
          this.addParallelSplitPatternToTemplate(template, context);
          break;
          
        case WorkflowPattern.EXCLUSIVE_CHOICE:
          this.addExclusiveChoicePatternToTemplate(template, context);
          break;
          
        case WorkflowPattern.STRUCTURED_LOOP:
          this.addStructuredLoopPatternToTemplate(template, context);
          break;
          
        case WorkflowPattern.MILESTONE:
          this.addMilestonePatternToTemplate(template, context);
          break;
          
        case WorkflowPattern.COMPENSATING_ACTION:
          this.addCompensatingActionPatternToTemplate(template, context);
          break;
      }
    }
  }
  
  /**
   * Adds a default pattern to a workflow template based on context
   * @param template Workflow template
   * @param context Generation context
   */
  private addDefaultPatternToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    // Choose pattern based on complexity
    if (context.complexityLevel <= 3) {
      // Simple sequential pattern for low complexity
      this.addSequentialPatternToTemplate(template, context);
    } else if (context.complexityLevel <= 6) {
      // Parallel split for medium complexity
      this.addParallelSplitPatternToTemplate(template, context);
    } else {
      // More complex patterns for high complexity
      this.addParallelSplitPatternToTemplate(template, context);
      this.addExclusiveChoicePatternToTemplate(template, context);
    }
  }
  
  /**
   * Adds a sequential pattern to a workflow template
   * @param template Workflow template
   * @param context Generation context
   */
  private addSequentialPatternToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    // Create tasks for sequential pattern
    const numTasks = Math.min(
      context.complexityLevel + 1, 
      context.maxTasks || 10
    );
    
    const tasks: TaskOptions[] = [];
    for (let i = 0; i < numTasks; i++) {
      // Generate task options
      const taskType = this.getRandomElement(context.taskTypes);
      const agentType = this.getRandomElement(context.agentTypes);
      
      const task = this.generateTask(context, {
        name: `Task ${i + 1}`,
        type: taskType as TaskType,
        agentType,
        priority: 5 + Math.floor(Math.random() * 5)
      });
      
      tasks.push({
        name: task.name,
        description: task.description,
        type: task.type,
        agentType: task.agentType,
        timeout: task.timeout,
        retries: task.maxRetries,
        priority: task.priority,
        metadata: { ...task.metadata, sequenceIndex: i }
      });
    }
    
    // Create pattern
    const patternOptions = WorkflowPatternFactory.createSequential(
      'Sequential Pattern',
      tasks
    );
    
    // Add tasks to template
    for (const taskOptions of patternOptions.nodes) {
      const task = this.createTask(taskOptions);
      template.addTaskTemplate(task);
    }
  }
  
  /**
   * Adds a parallel split pattern to a workflow template
   * @param template Workflow template
   * @param context Generation context
   */
  private addParallelSplitPatternToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    // Create initial task
    const initialTask = this.generateTask(context, {
      name: 'Initial Task',
      description: 'Starting point for parallel execution',
      type: TaskType.SEQUENTIAL
    });
    
    // Create parallel tasks
    const numParallelTasks = Math.min(
      context.complexityLevel,
      context.maxTasks || 5
    );
    
    const parallelTasks: TaskOptions[] = [];
    for (let i = 0; i < numParallelTasks; i++) {
      // Generate task options
      const taskType = this.getRandomElement(context.taskTypes);
      const agentType = this.getRandomElement(context.agentTypes);
      
      const task = this.generateTask(context, {
        name: `Parallel Task ${i + 1}`,
        type: taskType as TaskType,
        agentType,
        priority: 5 + Math.floor(Math.random() * 5)
      });
      
      parallelTasks.push({
        name: task.name,
        description: task.description,
        type: task.type,
        agentType: task.agentType,
        timeout: task.timeout,
        retries: task.maxRetries,
        priority: task.priority,
        metadata: { ...task.metadata, parallelIndex: i }
      });
    }
    
    // Create final task
    const finalTask = this.generateTask(context, {
      name: 'Final Task',
      description: 'Synchronization point after parallel execution',
      type: TaskType.SEQUENTIAL
    });
    
    // Create pattern
    const patternOptions = WorkflowPatternFactory.createParallelSplit(
      'Parallel Split Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      parallelTasks,
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
    
    // Add tasks to template
    for (const taskOptions of patternOptions.nodes) {
      const task = this.createTask(taskOptions);
      template.addTaskTemplate(task);
    }
  }
  
  /**
   * Adds an exclusive choice pattern to a workflow template
   * @param template Workflow template
   * @param context Generation context
   */
  private addExclusiveChoicePatternToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    // Create initial task
    const initialTask = this.generateTask(context, {
      name: 'Decision Task',
      description: 'Decision point for exclusive choice',
      type: TaskType.SEQUENTIAL
    });
    
    // Create branch tasks with conditions
    const numBranches = Math.min(
      context.complexityLevel - 2,
      context.maxTasks || 3
    );
    
    const branches: { task: TaskOptions, condition: TaskCondition }[] = [];
    for (let i = 0; i < numBranches; i++) {
      // Generate task options
      const taskType = this.getRandomElement(context.taskTypes);
      const agentType = this.getRandomElement(context.agentTypes);
      
      const task = this.generateTask(context, {
        name: `Branch Task ${i + 1}`,
        type: taskType as TaskType,
        agentType,
        priority: 5 + Math.floor(Math.random() * 5)
      });
      
      // Create condition based on index
      const condition: TaskCondition = {
        type: 'expression',
        value: `context.branchIndex === ${i}`
      };
      
      branches.push({
        task: {
          name: task.name,
          description: task.description,
          type: TaskType.CONDITIONAL,
          agentType: task.agentType,
          timeout: task.timeout,
          retries: task.maxRetries,
          priority: task.priority,
          metadata: { ...task.metadata, branchIndex: i }
        },
        condition
      });
    }
    
    // Create final task
    const finalTask = this.generateTask(context, {
      name: 'Merge Task',
      description: 'Merge point after exclusive choice',
      type: TaskType.SEQUENTIAL
    });
    
    // Create pattern
    const patternOptions = WorkflowPatternFactory.createExclusiveChoice(
      'Exclusive Choice Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      branches,
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
    
    // Add tasks to template
    for (const taskOptions of patternOptions.nodes) {
      const task = this.createTask(taskOptions);
      template.addTaskTemplate(task);
    }
  }
  
  /**
   * Adds a structured loop pattern to a workflow template
   * @param template Workflow template
   * @param context Generation context
   */
  private addStructuredLoopPatternToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    // Create initial task
    const initialTask = this.generateTask(context, {
      name: 'Loop Initialization',
      description: 'Initialization for loop execution',
      type: TaskType.SEQUENTIAL
    });
    
    // Create loop task
    const loopTask = this.generateTask(context, {
      name: 'Loop Body',
      description: 'Task to be executed repeatedly',
      type: TaskType.ITERATIVE
    });
    
    // Create loop condition
    const loopCondition: TaskCondition = {
      type: 'expression',
      value: 'context.loopCounter < context.maxIterations'
    };
    
    // Create final task
    const finalTask = this.generateTask(context, {
      name: 'Loop Completion',
      description: 'Task executed after loop completion',
      type: TaskType.SEQUENTIAL
    });
    
    // Create pattern
    const patternOptions = WorkflowPatternFactory.createStructuredLoop(
      'Structured Loop Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      {
        name: loopTask.name,
        description: loopTask.description,
        type: TaskType.ITERATIVE,
        timeout: loopTask.timeout,
        retries: loopTask.maxRetries,
        priority: loopTask.priority,
        metadata: loopTask.metadata
      },
      loopCondition,
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
    
    // Add tasks to template
    for (const taskOptions of patternOptions.nodes) {
      const task = this.createTask(taskOptions);
      template.addTaskTemplate(task);
    }
  }
  
  /**
   * Adds a milestone pattern to a workflow template
   * @param template Workflow template
   * @param context Generation context
   */
  private addMilestonePatternToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    // Create initial task
    const initialTask = this.generateTask(context, {
      name: 'Initial Task',
      description: 'Starting point for milestone pattern',
      type: TaskType.SEQUENTIAL
    });
    
    // Create milestone task
    const milestoneTask = this.generateTask(context, {
      name: 'Milestone Task',
      description: 'Represents a milestone in the workflow',
      type: TaskType.SEQUENTIAL
    });
    
    // Create dependent task
    const dependentTask = this.generateTask(context, {
      name: 'Dependent Task',
      description: 'Task dependent on milestone completion',
      type: TaskType.SEQUENTIAL
    });
    
    // Create final task
    const finalTask = this.generateTask(context, {
      name: 'Final Task',
      description: 'Task executed after dependent task completion',
      type: TaskType.SEQUENTIAL
    });
    
    // Create pattern
    const patternOptions = WorkflowPatternFactory.createMilestone(
      'Milestone Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      {
        name: milestoneTask.name,
        description: milestoneTask.description,
        type: milestoneTask.type,
        timeout: milestoneTask.timeout,
        retries: milestoneTask.maxRetries,
        priority: milestoneTask.priority,
        metadata: { ...milestoneTask.metadata, isMilestone: true }
      },
      {
        name: dependentTask.name,
        description: dependentTask.description,
        type: dependentTask.type,
        timeout: dependentTask.timeout,
        retries: dependentTask.maxRetries,
        priority: dependentTask.priority,
        metadata: dependentTask.metadata
      },
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
    
    // Add tasks to template
    for (const taskOptions of patternOptions.nodes) {
      const task = this.createTask(taskOptions);
      template.addTaskTemplate(task);
    }
  }
  
  /**
   * Adds a compensating action pattern to a workflow template
   * @param template Workflow template
   * @param context Generation context
   */
  private addCompensatingActionPatternToTemplate(template: WorkflowTemplate, context: GenerationContext): void {
    // Create main task
    const mainTask = this.generateTask(context, {
      name: 'Main Task',
      description: 'Main task that might fail',
      type: TaskType.SEQUENTIAL
    });
    
    // Create compensation task
    const compensationTask = this.generateTask(context, {
      name: 'Compensation Task',
      description: 'Task to compensate for main task failure',
      type: TaskType.SEQUENTIAL
    });
    
    // Create final task
    const finalTask = this.generateTask(context, {
      name: 'Final Task',
      description: 'Task executed after main task or compensation',
      type: TaskType.SEQUENTIAL
    });
    
    // Create pattern
    const patternOptions = WorkflowPatternFactory.createCompensatingAction(
      'Compensating Action Pattern',
      {
        name: mainTask.name,
        description: mainTask.description,
        type: mainTask.type,
        timeout: mainTask.timeout,
        retries: mainTask.maxRetries,
        priority: mainTask.priority,
        metadata: { ...mainTask.metadata, critical: true }
      },
      {
        name: compensationTask.name,
        description: compensationTask.description,
        type: compensationTask.type,
        timeout: compensationTask.timeout,
        retries: compensationTask.maxRetries,
        priority: compensationTask.priority,
        metadata: { ...compensationTask.metadata, isCompensation: true }
      },
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
    
    // Add tasks to template
    for (const taskOptions of patternOptions.nodes) {
      const task = this.createTask(taskOptions);
      template.addTaskTemplate(task);
    }
  }
  
  /**
   * Gets a random element from an array
   * @param array Array to get element from
   * @returns Random element
   */
  private getRandomElement<T>(array: T[]): T {
    return array[Math.floor(Math.random() * array.length)];
  }
}

/**
 * Pattern-based workflow generator
 */
export class PatternWorkflowGenerator extends WorkflowGenerator {
  private patternFactory: typeof WorkflowPatternFactory;
  
  constructor() {
    super();
    this.patternFactory = WorkflowPatternFactory;
  }
  
  /**
   * Generates a workflow based on the given context
   * @param context Generation context
   * @returns Generated workflow
   */
  generateWorkflow(context: GenerationContext): Workflow {
    // Create workflow options
    const workflowOptions: WorkflowOptions = {
      name: `${context.domain} Workflow`,
      description: `Workflow for ${context.domain} domain`,
      executionMode: this.determineExecutionMode(context),
      coordinationStrategy: this.determineCoordinationStrategy(context),
      requiredAgentTypes: context.agentTypes,
      knowledgeBaseScope: [],
      priority: Math.min(Math.ceil(context.complexityLevel / 2), 10),
      metadata: {
        ...context.metadata,
        domain: context.domain,
        generatedFrom: 'pattern',
        complexity: context.complexityLevel
      },
      tags: [context.domain, 'generated']
    };
    
    // Create workflow
    const workflow = new Workflow(workflowOptions);
    
    // Add patterns to workflow
    if (context.requiredPatterns && context.requiredPatterns.length > 0) {
      this.addPatternsToWorkflow(workflow, context);
    } else {
      // Add default patterns based on complexity
      this.addDefaultPatternsToWorkflow(workflow, context);
    }
    
    return workflow;
  }
  
  /**
   * Generates a task based on the given context
   * @param context Generation context
   * @param options Optional task options
   * @returns Generated task
   */
  generateTask(context: GenerationContext, options: Partial<TaskOptions> = {}): Task {
    // Use domain-specific task factory based on context
    let taskOptions: TaskOptions;
    
    switch (context.domain) {
      case 'economic':
        taskOptions = {
          ...DomainTaskFactory.createEconomicAnalysisTask('Economic Analysis Task'),
          ...options
        };
        break;
        
      case 'healthcare':
        taskOptions = {
          ...DomainTaskFactory.createHealthcareDataProcessingTask('Healthcare Data Task'),
          ...options
        };
        break;
        
      case 'governance':
        taskOptions = {
          ...DomainTaskFactory.createPolicyFormulationTask('Policy Task'),
          ...options
        };
        break;
        
      case 'data_analysis':
        taskOptions = {
          ...DomainTaskFactory.createDataVisualizationTask('Data Analysis Task'),
          ...options
        };
        break;
        
      case 'coordination':
        taskOptions = {
          ...DomainTaskFactory.createWorkflowCoordinationTask('Coordination Task'),
          ...options
        };
        break;
        
      default:
        // Default task options
        taskOptions = {
          name: options.name || 'Generic Task',
          description: options.description || 'A generic task',
          type: options.type || TaskType.SEQUENTIAL,
          timeout: options.timeout || 60000, // 1 minute
          retries: options.retries || 3,
          priority: options.priority || 5,
          ...options
        };
    }
    
    // Create task
    return this.createTask(taskOptions);
  }
  
  /**
   * Generates a workflow template based on the given context
   * @param context Generation context
   * @returns Generated workflow template
   */
  generateWorkflowTemplate(context: GenerationContext): WorkflowTemplate {
    // Create workflow
    const workflow = this.generateWorkflow(context);
    
    // Use domain-specific template factory based on context
    let templateOptions: any;
    const templateId = `${context.domain}_${uuidv4().substring(0, 8)}`;
    const templateVersion = '1.0.0';
    
    switch (context.domain) {
      case 'economic':
        templateOptions = DomainWorkflowFactory.createEconomicAnalysisWorkflow(
          workflow.name,
          templateVersion
        );
        break;
        
      case 'healthcare':
        templateOptions = DomainWorkflowFactory.createHealthcareWorkflow(
          workflow.name,
          templateVersion
        );
        break;
        
      case 'governance':
        templateOptions = DomainWorkflowFactory.createPolicyAnalysisWorkflow(
          workflow.name,
          templateVersion
        );
        break;
        
      case 'data_analysis':
        templateOptions = DomainWorkflowFactory.createDataAnalysisWorkflow(
          workflow.name,
          templateVersion
        );
        break;
        
      case 'coordination':
        templateOptions = DomainWorkflowFactory.createCoordinationWorkflow(
          workflow.name,
          templateVersion
        );
        break;
        
      default:
        // Default template options
        templateOptions = {
          id: templateId,
          name: workflow.name,
          description: workflow.description,
          version: templateVersion,
          executionMode: workflow.executionMode,
          coordinationStrategy: workflow.coordinationStrategy,
          parameters: [],
          requiredAgentTypes: workflow.requiredAgentTypes,
          timeout: workflow.timeout,
          metadata: workflow.metadata,
          tags: workflow.tags || []
        };
    }
    
    // Override ID if it was the same
    templateOptions.id = templateId;
    
    // Create template
    const template = new WorkflowTemplate(templateOptions);
    
    // Add tasks from workflow
    for (const task of workflow.tasks.values()) {
      template.addTaskTemplate(task);
    }
    
    return template;
  }
  
  /**
   * Determines the execution mode based on context
   * @param context Generation context
   * @returns Execution mode
   */
  private determineExecutionMode(context: GenerationContext): WorkflowExecutionMode {
    // Use complexity level to determine execution mode
    if (context.complexityLevel <= 3) {
      return WorkflowExecutionMode.SEQUENTIAL;
    } else if (context.complexityLevel <= 6) {
      return WorkflowExecutionMode.PARALLEL;
    } else if (context.complexityLevel <= 8) {
      return WorkflowExecutionMode.HYBRID;
    } else {
      return WorkflowExecutionMode.ADAPTIVE;
    }
  }
  
  /**
   * Determines the coordination strategy based on context
   * @param context Generation context
   * @returns Coordination strategy
   */
  private determineCoordinationStrategy(context: GenerationContext): CoordinationStrategy {
    // Use complexity level to determine coordination strategy
    if (context.complexityLevel <= 4) {
      return CoordinationStrategy.CENTRALIZED;
    } else if (context.complexityLevel <= 7) {
      return CoordinationStrategy.HIERARCHY;
    } else {
      return CoordinationStrategy.ADAPTIVE_HYBRID;
    }
  }
  
  /**
   * Adds patterns to a workflow
   * @param workflow Workflow
   * @param context Generation context
   */
  private addPatternsToWorkflow(workflow: Workflow, context: GenerationContext): void {
    if (!context.requiredPatterns) return;
    
    let previousPatternEndTaskId: string | undefined;
    
    for (const pattern of context.requiredPatterns) {
      let patternOptions: any;
      
      switch (pattern) {
        case WorkflowPattern.SEQUENTIAL:
          patternOptions = this.createSequentialPatternForWorkflow(context);
          break;
          
        case WorkflowPattern.PARALLEL_SPLIT:
          patternOptions = this.createParallelSplitPatternForWorkflow(context);
          break;
          
        case WorkflowPattern.EXCLUSIVE_CHOICE:
          patternOptions = this.createExclusiveChoicePatternForWorkflow(context);
          break;
          
        case WorkflowPattern.STRUCTURED_LOOP:
          patternOptions = this.createStructuredLoopPatternForWorkflow(context);
          break;
          
        case WorkflowPattern.MILESTONE:
          patternOptions = this.createMilestonePatternForWorkflow(context);
          break;
          
        case WorkflowPattern.COMPENSATING_ACTION:
          patternOptions = this.createCompensatingActionPatternForWorkflow(context);
          break;
          
        default:
          continue;
      }
      
      // Add task nodes to workflow
      const taskIds: string[] = [];
      
      for (const nodeOptions of patternOptions.nodes) {
        const task = this.createTask(nodeOptions);
        
        // Connect to previous pattern if this is not the first pattern
        if (previousPatternEndTaskId && taskIds.length === 0) {
          task.dependencies.push(previousPatternEndTaskId);
        }
        
        workflow.addTask(task);
        taskIds.push(task.id);
      }
      
      // Add connections between tasks
      for (const [fromNodeId, toNodeId] of patternOptions.connections) {
        const fromIndex = patternOptions.nodes.findIndex((node: any) => 
          node.metadata?.nodeId === fromNodeId
        );
        const toIndex = patternOptions.nodes.findIndex((node: any) => 
          node.metadata?.nodeId === toNodeId
        );
        
        if (fromIndex >= 0 && toIndex >= 0) {
          const fromTaskId = taskIds[fromIndex];
          const toTaskId = taskIds[toIndex];
          
          if (fromTaskId && toTaskId) {
            const toTask = workflow.getTask(toTaskId);
            if (toTask && !toTask.dependencies.includes(fromTaskId)) {
              toTask.dependencies.push(fromTaskId);
            }
          }
        }
      }
      
      // Set the end task of this pattern as the start point for the next pattern
      if (taskIds.length > 0) {
        previousPatternEndTaskId = taskIds[taskIds.length - 1];
      }
    }
  }
  
  /**
   * Adds default patterns to a workflow based on context
   * @param workflow Workflow
   * @param context Generation context
   */
  private addDefaultPatternsToWorkflow(workflow: Workflow, context: GenerationContext): void {
    // Choose patterns based on complexity
    if (context.complexityLevel <= 3) {
      // Simple sequential pattern for low complexity
      const patternOptions = this.createSequentialPatternForWorkflow(context);
      this.addPatternToWorkflow(workflow, patternOptions);
    } else if (context.complexityLevel <= 6) {
      // Sequential pattern followed by parallel split for medium complexity
      const sequentialOptions = this.createSequentialPatternForWorkflow({
        ...context,
        complexityLevel: Math.floor(context.complexityLevel / 2),
        maxTasks: context.maxTasks ? Math.floor(context.maxTasks / 2) : undefined
      });
      
      const parallelOptions = this.createParallelSplitPatternForWorkflow({
        ...context,
        complexityLevel: Math.ceil(context.complexityLevel / 2),
        maxTasks: context.maxTasks ? Math.ceil(context.maxTasks / 2) : undefined
      });
      
      // Add sequential pattern
      const sequentialTaskIds = this.addPatternToWorkflow(workflow, sequentialOptions);
      
      // Add parallel pattern
      if (sequentialTaskIds.length > 0) {
        const lastSequentialTaskId = sequentialTaskIds[sequentialTaskIds.length - 1];
        this.addPatternToWorkflow(workflow, parallelOptions, lastSequentialTaskId);
      } else {
        this.addPatternToWorkflow(workflow, parallelOptions);
      }
    } else {
      // More complex patterns for high complexity
      const sequentialOptions = this.createSequentialPatternForWorkflow({
        ...context,
        complexityLevel: 2,
        maxTasks: 3
      });
      
      const parallelOptions = this.createParallelSplitPatternForWorkflow({
        ...context,
        complexityLevel: Math.floor(context.complexityLevel / 3),
        maxTasks: context.maxTasks ? Math.floor(context.maxTasks / 3) : undefined
      });
      
      const choiceOptions = this.createExclusiveChoicePatternForWorkflow({
        ...context,
        complexityLevel: Math.floor(context.complexityLevel / 3),
        maxTasks: context.maxTasks ? Math.floor(context.maxTasks / 3) : undefined
      });
      
      // Add sequential pattern
      const sequentialTaskIds = this.addPatternToWorkflow(workflow, sequentialOptions);
      let lastTaskId = sequentialTaskIds.length > 0 ? 
        sequentialTaskIds[sequentialTaskIds.length - 1] : undefined;
      
      // Add parallel pattern
      const parallelTaskIds = this.addPatternToWorkflow(workflow, parallelOptions, lastTaskId);
      if (parallelTaskIds.length > 0) {
        lastTaskId = parallelTaskIds[parallelTaskIds.length - 1];
      }
      
      // Add choice pattern
      this.addPatternToWorkflow(workflow, choiceOptions, lastTaskId);
    }
  }
  
  /**
   * Adds a pattern to a workflow
   * @param workflow Workflow
   * @param patternOptions Pattern options
   * @param previousTaskId ID of previous task to connect to
   * @returns Array of task IDs added to the workflow
   */
  private addPatternToWorkflow(
    workflow: Workflow, 
    patternOptions: any, 
    previousTaskId?: string
  ): string[] {
    // Add task nodes to workflow
    const taskIds: string[] = [];
    
    for (const nodeOptions of patternOptions.nodes) {
      const task = this.createTask(nodeOptions);
      
      // Connect to previous task if specified and this is the first task in pattern
      if (previousTaskId && taskIds.length === 0) {
        task.dependencies.push(previousTaskId);
      }
      
      workflow.addTask(task);
      taskIds.push(task.id);
    }
    
    // Add connections between tasks
    for (const [fromNodeId, toNodeId] of patternOptions.connections) {
      const fromIndex = patternOptions.nodes.findIndex((node: any) => 
        node.metadata?.nodeId === fromNodeId
      );
      const toIndex = patternOptions.nodes.findIndex((node: any) => 
        node.metadata?.nodeId === toNodeId
      );
      
      if (fromIndex >= 0 && toIndex >= 0) {
        const fromTaskId = taskIds[fromIndex];
        const toTaskId = taskIds[toIndex];
        
        if (fromTaskId && toTaskId) {
          const toTask = workflow.getTask(toTaskId);
          if (toTask && !toTask.dependencies.includes(fromTaskId)) {
            toTask.dependencies.push(fromTaskId);
          }
        }
      }
    }
    
    return taskIds;
  }
  
  /**
   * Creates a sequential pattern for a workflow
   * @param context Generation context
   * @returns Pattern options
   */
  private createSequentialPatternForWorkflow(context: GenerationContext): any {
    // Create tasks for sequential pattern
    const numTasks = Math.min(
      context.complexityLevel + 1, 
      context.maxTasks || 10
    );
    
    const tasks: TaskOptions[] = [];
    for (let i = 0; i < numTasks; i++) {
      // Generate task options based on domain
      const task = this.generateDomainSpecificTask(context, i);
      tasks.push(task);
    }
    
    // Create pattern
    return WorkflowPatternFactory.createSequential(
      'Sequential Pattern',
      tasks
    );
  }
  
  /**
   * Creates a parallel split pattern for a workflow
   * @param context Generation context
   * @returns Pattern options
   */
  private createParallelSplitPatternForWorkflow(context: GenerationContext): any {
    // Create initial task
    const initialTaskType = this.getRandomElement(context.taskTypes);
    const initialAgentType = this.getRandomElement(context.agentTypes);
    
    const initialTask = this.generateTask(context, {
      name: 'Initial Task',
      description: 'Starting point for parallel execution',
      type: initialTaskType as TaskType,
      agentType: initialAgentType
    });
    
    // Create parallel tasks
    const numParallelTasks = Math.min(
      context.complexityLevel,
      context.maxTasks || 5
    );
    
    const parallelTasks: TaskOptions[] = [];
    for (let i = 0; i < numParallelTasks; i++) {
      // Generate task options based on domain
      const task = this.generateDomainSpecificTask(context, i);
      parallelTasks.push(task);
    }
    
    // Create final task
    const finalTaskType = this.getRandomElement(context.taskTypes);
    const finalAgentType = this.getRandomElement(context.agentTypes);
    
    const finalTask = this.generateTask(context, {
      name: 'Final Task',
      description: 'Synchronization point after parallel execution',
      type: finalTaskType as TaskType,
      agentType: finalAgentType
    });
    
    // Create pattern
    return WorkflowPatternFactory.createParallelSplit(
      'Parallel Split Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        agentType: initialTask.agentType,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      parallelTasks,
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        agentType: finalTask.agentType,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
  }
  
  /**
   * Creates an exclusive choice pattern for a workflow
   * @param context Generation context
   * @returns Pattern options
   */
  private createExclusiveChoicePatternForWorkflow(context: GenerationContext): any {
    // Create initial task
    const initialTaskType = this.getRandomElement(context.taskTypes);
    const initialAgentType = this.getRandomElement(context.agentTypes);
    
    const initialTask = this.generateTask(context, {
      name: 'Decision Task',
      description: 'Decision point for exclusive choice',
      type: initialTaskType as TaskType,
      agentType: initialAgentType
    });
    
    // Create branch tasks with conditions
    const numBranches = Math.min(
      context.complexityLevel - 2,
      context.maxTasks || 3
    );
    
    const branches: { task: TaskOptions, condition: TaskCondition }[] = [];
    for (let i = 0; i < numBranches; i++) {
      // Generate task options based on domain
      const task = this.generateDomainSpecificTask(context, i);
      
      // Create condition based on index
      const condition: TaskCondition = {
        type: 'expression',
        value: `context.branchIndex === ${i}`
      };
      
      branches.push({
        task: {
          ...task,
          type: TaskType.CONDITIONAL
        },
        condition
      });
    }
    
    // Create final task
    const finalTaskType = this.getRandomElement(context.taskTypes);
    const finalAgentType = this.getRandomElement(context.agentTypes);
    
    const finalTask = this.generateTask(context, {
      name: 'Merge Task',
      description: 'Merge point after exclusive choice',
      type: finalTaskType as TaskType,
      agentType: finalAgentType
    });
    
    // Create pattern
    return WorkflowPatternFactory.createExclusiveChoice(
      'Exclusive Choice Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        agentType: initialTask.agentType,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      branches,
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        agentType: finalTask.agentType,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
  }
  
  /**
   * Creates a structured loop pattern for a workflow
   * @param context Generation context
   * @returns Pattern options
   */
  private createStructuredLoopPatternForWorkflow(context: GenerationContext): any {
    // Create initial task
    const initialTaskType = this.getRandomElement(context.taskTypes);
    const initialAgentType = this.getRandomElement(context.agentTypes);
    
    const initialTask = this.generateTask(context, {
      name: 'Loop Initialization',
      description: 'Initialization for loop execution',
      type: initialTaskType as TaskType,
      agentType: initialAgentType
    });
    
    // Create loop task
    const loopTaskType = this.getRandomElement(context.taskTypes);
    const loopAgentType = this.getRandomElement(context.agentTypes);
    
    const loopTask = this.generateTask(context, {
      name: 'Loop Body',
      description: 'Task to be executed repeatedly',
      type: loopTaskType as TaskType,
      agentType: loopAgentType
    });
    
    // Create loop condition
    const loopCondition: TaskCondition = {
      type: 'expression',
      value: 'context.loopCounter < context.maxIterations'
    };
    
    // Create final task
    const finalTaskType = this.getRandomElement(context.taskTypes);
    const finalAgentType = this.getRandomElement(context.agentTypes);
    
    const finalTask = this.generateTask(context, {
      name: 'Loop Completion',
      description: 'Task executed after loop completion',
      type: finalTaskType as TaskType,
      agentType: finalAgentType
    });
    
    // Create pattern
    return WorkflowPatternFactory.createStructuredLoop(
      'Structured Loop Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        agentType: initialTask.agentType,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      {
        name: loopTask.name,
        description: loopTask.description,
        type: TaskType.ITERATIVE,
        agentType: loopTask.agentType,
        timeout: loopTask.timeout,
        retries: loopTask.maxRetries,
        priority: loopTask.priority,
        metadata: loopTask.metadata
      },
      loopCondition,
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        agentType: finalTask.agentType,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
  }
  
  /**
   * Creates a milestone pattern for a workflow
   * @param context Generation context
   * @returns Pattern options
   */
  private createMilestonePatternForWorkflow(context: GenerationContext): any {
    // Create initial task
    const initialTaskType = this.getRandomElement(context.taskTypes);
    const initialAgentType = this.getRandomElement(context.agentTypes);
    
    const initialTask = this.generateTask(context, {
      name: 'Initial Task',
      description: 'Starting point for milestone pattern',
      type: initialTaskType as TaskType,
      agentType: initialAgentType
    });
    
    // Create milestone task
    const milestoneTaskType = this.getRandomElement(context.taskTypes);
    const milestoneAgentType = this.getRandomElement(context.agentTypes);
    
    const milestoneTask = this.generateTask(context, {
      name: 'Milestone Task',
      description: 'Represents a milestone in the workflow',
      type: milestoneTaskType as TaskType,
      agentType: milestoneAgentType
    });
    
    // Create dependent task
    const dependentTaskType = this.getRandomElement(context.taskTypes);
    const dependentAgentType = this.getRandomElement(context.agentTypes);
    
    const dependentTask = this.generateTask(context, {
      name: 'Dependent Task',
      description: 'Task dependent on milestone completion',
      type: dependentTaskType as TaskType,
      agentType: dependentAgentType
    });
    
    // Create final task
    const finalTaskType = this.getRandomElement(context.taskTypes);
    const finalAgentType = this.getRandomElement(context.agentTypes);
    
    const finalTask = this.generateTask(context, {
      name: 'Final Task',
      description: 'Task executed after dependent task completion',
      type: finalTaskType as TaskType,
      agentType: finalAgentType
    });
    
    // Create pattern
    return WorkflowPatternFactory.createMilestone(
      'Milestone Pattern',
      {
        name: initialTask.name,
        description: initialTask.description,
        type: initialTask.type,
        agentType: initialTask.agentType,
        timeout: initialTask.timeout,
        retries: initialTask.maxRetries,
        priority: initialTask.priority,
        metadata: initialTask.metadata
      },
      {
        name: milestoneTask.name,
        description: milestoneTask.description,
        type: milestoneTask.type,
        agentType: milestoneTask.agentType,
        timeout: milestoneTask.timeout,
        retries: milestoneTask.maxRetries,
        priority: milestoneTask.priority,
        metadata: { ...milestoneTask.metadata, isMilestone: true }
      },
      {
        name: dependentTask.name,
        description: dependentTask.description,
        type: dependentTask.type,
        agentType: dependentTask.agentType,
        timeout: dependentTask.timeout,
        retries: dependentTask.maxRetries,
        priority: dependentTask.priority,
        metadata: dependentTask.metadata
      },
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        agentType: finalTask.agentType,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
  }
  
  /**
   * Creates a compensating action pattern for a workflow
   * @param context Generation context
   * @returns Pattern options
   */
  private createCompensatingActionPatternForWorkflow(context: GenerationContext): any {
    // Create main task
    const mainTaskType = this.getRandomElement(context.taskTypes);
    const mainAgentType = this.getRandomElement(context.agentTypes);
    
    const mainTask = this.generateTask(context, {
      name: 'Main Task',
      description: 'Main task that might fail',
      type: mainTaskType as TaskType,
      agentType: mainAgentType
    });
    
    // Create compensation task
    const compensationTaskType = this.getRandomElement(context.taskTypes);
    const compensationAgentType = this.getRandomElement(context.agentTypes);
    
    const compensationTask = this.generateTask(context, {
      name: 'Compensation Task',
      description: 'Task to compensate for main task failure',
      type: compensationTaskType as TaskType,
      agentType: compensationAgentType
    });
    
    // Create final task
    const finalTaskType = this.getRandomElement(context.taskTypes);
    const finalAgentType = this.getRandomElement(context.agentTypes);
    
    const finalTask = this.generateTask(context, {
      name: 'Final Task',
      description: 'Task executed after main task or compensation',
      type: finalTaskType as TaskType,
      agentType: finalAgentType
    });
    
    // Create pattern
    return WorkflowPatternFactory.createCompensatingAction(
      'Compensating Action Pattern',
      {
        name: mainTask.name,
        description: mainTask.description,
        type: mainTask.type,
        agentType: mainTask.agentType,
        timeout: mainTask.timeout,
        retries: mainTask.maxRetries,
        priority: mainTask.priority,
        metadata: { ...mainTask.metadata, critical: true }
      },
      {
        name: compensationTask.name,
        description: compensationTask.description,
        type: compensationTask.type,
        agentType: compensationTask.agentType,
        timeout: compensationTask.timeout,
        retries: compensationTask.maxRetries,
        priority: compensationTask.priority,
        metadata: { ...compensationTask.metadata, isCompensation: true }
      },
      {
        name: finalTask.name,
        description: finalTask.description,
        type: finalTask.type,
        agentType: finalTask.agentType,
        timeout: finalTask.timeout,
        retries: finalTask.maxRetries,
        priority: finalTask.priority,
        metadata: finalTask.metadata
      }
    );
  }
  
  /**
   * Generates a domain-specific task based on context
   * @param context Generation context
   * @param index Task index
   * @returns Task options
   */
  private generateDomainSpecificTask(context: GenerationContext, index: number): TaskOptions {
    // Generate task options based on domain
    const taskType = this.getRandomElement(context.taskTypes);
    const agentType = this.getRandomElement(context.agentTypes);
    
    let task: Task;
    
    switch (context.domain) {
      case 'economic':
        // Alternate between data gathering and analysis tasks
        if (index % 2 === 0) {
          task = this.generateTask(context, {
            name: `Economic Data Task ${index + 1}`,
            type: taskType as TaskType,
            agentType
          });
        } else {
          task = this.generateTask(context, {
            name: `Economic Analysis Task ${index + 1}`,
            type: taskType as TaskType,
            agentType
          });
        }
        break;
        
      case 'healthcare':
        task = this.generateTask(context, {
          name: `Healthcare Task ${index + 1}`,
          type: taskType as TaskType,
          agentType
        });
        break;
        
      case 'governance':
        task = this.generateTask(context, {
          name: `Policy Task ${index + 1}`,
          type: taskType as TaskType,
          agentType
        });
        break;
        
      case 'data_analysis':
        task = this.generateTask(context, {
          name: `Data Analysis Task ${index + 1}`,
          type: taskType as TaskType,
          agentType
        });
        break;
        
      case 'coordination':
        task = this.generateTask(context, {
          name: `Coordination Task ${index + 1}`,
          type: taskType as TaskType,
          agentType
        });
        break;
        
      default:
        task = this.generateTask(context, {
          name: `Task ${index + 1}`,
          type: taskType as TaskType,
          agentType
        });
    }
    
    return {
      name: task.name,
      description: task.description,
      type: task.type,
      agentType: task.agentType,
      timeout: task.timeout,
      retries: task.maxRetries,
      priority: task.priority,
      metadata: { ...task.metadata, index }
    };
  }
  
  /**
   * Gets a random element from an array
   * @param array Array to get element from
   * @returns Random element
   */
  private getRandomElement<T>(array: T[]): T {
    return array[Math.floor(Math.random() * array.length)];
  }
}

/**
 * Factory for creating workflow generators
 */
export class WorkflowGeneratorFactory {
  /**
   * Creates a workflow generator based on context
   * @param context Generation context
   * @returns Workflow generator
   */
  static createGenerator(context: GenerationContext): WorkflowGenerator {
    if (context.requiredPatterns && context.requiredPatterns.length > 0) {
      return new PatternWorkflowGenerator();
    } else {
      return new TemplateWorkflowGenerator();
    }
  }
  
  /**
   * Creates a template-based workflow generator
   * @returns Template-based workflow generator
   */
  static createTemplateGenerator(): TemplateWorkflowGenerator {
    return new TemplateWorkflowGenerator();
  }
  
  /**
   * Creates a pattern-based workflow generator
   * @returns Pattern-based workflow generator
   */
  static createPatternGenerator(): PatternWorkflowGenerator {
    return new PatternWorkflowGenerator();
  }
}

export default {
  WorkflowGeneratorFactory,
  TemplateWorkflowGenerator,
  PatternWorkflowGenerator
};