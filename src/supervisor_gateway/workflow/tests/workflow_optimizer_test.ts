/**
 * Tests for the workflow optimizer
 */

import { 
  WorkflowOptimizer, 
  OptimizationOptions,
  ParallelizationStrategy,
  ResourceOptimizationStrategy,
  OptimizationStrategyFactory
} from '../workflow_optimizer';
import { 
  Workflow, 
  WorkflowOptions, 
  Task, 
  TaskStatus, 
  TaskType,
  WorkflowExecutionMode,
  CoordinationStrategy
} from '../workflow_orchestrator';
import { AgentRegistry } from '../../core/agent_registry';
import { TaskAllocator } from '../task_allocator';

/**
 * Mock agent registry
 */
class MockAgentRegistry implements AgentRegistry {
  private agents = new Map<string, any>();
  
  constructor() {
    this.initializeMockAgents();
  }
  
  private initializeMockAgents(): void {
    for (let i = 1; i <= 5; i++) {
      const agent = {
        getId: () => `agent${i}`,
        getType: () => i <= 2 ? 'economic' : i <= 4 ? 'policy' : 'data_analysis',
        getName: () => `Agent ${i}`,
        isAvailable: () => true
      };
      
      this.agents.set(agent.getId(), agent);
    }
  }
  
  getAgent(agentId: string): any {
    return this.agents.get(agentId);
  }
  
  getAgentsByType(agentType: string): any[] {
    return Array.from(this.agents.values())
      .filter(agent => agent.getType() === agentType);
  }
  
  getAllAgents(): any[] {
    return Array.from(this.agents.values());
  }
  
  registerAgent(agent: any): void {
    this.agents.set(agent.getId(), agent);
  }
  
  unregisterAgent(agentId: string): void {
    this.agents.delete(agentId);
  }
}

/**
 * Creates a test workflow
 * @returns Test workflow
 */
function createTestWorkflow(): Workflow {
  const options: WorkflowOptions = {
    name: 'Economic Analysis Workflow',
    description: 'Analyzes economic indicators and generates policy recommendations',
    executionMode: WorkflowExecutionMode.SEQUENTIAL,
    coordinationStrategy: CoordinationStrategy.CENTRALIZED,
    priority: 7,
    requiredAgentTypes: ['economic', 'policy', 'data_analysis'],
    knowledgeBaseScope: []
  };
  
  const workflow = new Workflow(options);
  
  // Add data gathering task
  const dataTask = new Task({
    name: 'Gather Economic Data',
    description: 'Collects economic indicators from various sources',
    type: TaskType.SEQUENTIAL,
    agentType: 'economic',
    estimatedDuration: 30000, // 30 seconds
    priority: 8,
    metadata: {
      domain: 'economic',
      dataSource: 'economic_indicators'
    }
  });
  
  // Add data processing task
  const processingTask = new Task({
    name: 'Process Economic Data',
    description: 'Processes raw economic data for analysis',
    type: TaskType.SEQUENTIAL,
    agentType: 'economic',
    dependencies: [], // Will be updated after adding tasks
    estimatedDuration: 45000, // 45 seconds
    priority: 7,
    metadata: {
      domain: 'economic',
      processingLevel: 'detailed'
    }
  });
  
  // Add analysis task
  const analysisTask = new Task({
    name: 'Analyze Economic Trends',
    description: 'Analyzes economic trends and identifies patterns',
    type: TaskType.SEQUENTIAL,
    agentType: 'economic',
    dependencies: [], // Will be updated after adding tasks
    estimatedDuration: 60000, // 60 seconds
    priority: 9,
    metadata: {
      domain: 'economic',
      analysisDepth: 'comprehensive'
    }
  });
  
  // Add policy analysis task
  const policyAnalysisTask = new Task({
    name: 'Analyze Policy Implications',
    description: 'Analyzes policy implications of economic trends',
    type: TaskType.SEQUENTIAL,
    agentType: 'policy',
    dependencies: [], // Will be updated after adding tasks
    estimatedDuration: 50000, // 50 seconds
    priority: 8,
    metadata: {
      domain: 'governance',
      policyScope: 'economic'
    }
  });
  
  // Add recommendation task
  const recommendationTask = new Task({
    name: 'Generate Policy Recommendations',
    description: 'Generates policy recommendations based on analysis',
    type: TaskType.SEQUENTIAL,
    agentType: 'policy',
    dependencies: [], // Will be updated after adding tasks
    estimatedDuration: 40000, // 40 seconds
    priority: 9,
    metadata: {
      domain: 'governance',
      recommendationType: 'actionable'
    }
  });
  
  // Add visualization task
  const visualizationTask = new Task({
    name: 'Create Data Visualizations',
    description: 'Creates visualizations of economic data and trends',
    type: TaskType.SEQUENTIAL,
    agentType: 'data_analysis',
    dependencies: [], // Will be updated after adding tasks
    estimatedDuration: 35000, // 35 seconds
    priority: 6,
    metadata: {
      domain: 'data_analysis',
      visualizationType: 'interactive'
    }
  });
  
  // Add report generation task
  const reportTask = new Task({
    name: 'Generate Final Report',
    description: 'Generates a comprehensive report with all findings',
    type: TaskType.SEQUENTIAL,
    agentType: 'data_analysis',
    dependencies: [], // Will be updated after adding tasks
    estimatedDuration: 55000, // 55 seconds
    priority: 9,
    metadata: {
      domain: 'data_analysis',
      reportFormat: 'comprehensive'
    }
  });
  
  // Add tasks to workflow
  const dataTaskId = workflow.addTask(dataTask);
  const processingTaskId = workflow.addTask(processingTask);
  const analysisTaskId = workflow.addTask(analysisTask);
  const policyAnalysisTaskId = workflow.addTask(policyAnalysisTask);
  const recommendationTaskId = workflow.addTask(recommendationTask);
  const visualizationTaskId = workflow.addTask(visualizationTask);
  const reportTaskId = workflow.addTask(reportTask);
  
  // Set dependencies
  const processingTask2 = workflow.getTask(processingTaskId);
  if (processingTask2) {
    processingTask2.dependencies = [dataTaskId];
  }
  
  const analysisTask2 = workflow.getTask(analysisTaskId);
  if (analysisTask2) {
    analysisTask2.dependencies = [processingTaskId];
  }
  
  const policyAnalysisTask2 = workflow.getTask(policyAnalysisTaskId);
  if (policyAnalysisTask2) {
    policyAnalysisTask2.dependencies = [analysisTaskId];
  }
  
  const recommendationTask2 = workflow.getTask(recommendationTaskId);
  if (recommendationTask2) {
    recommendationTask2.dependencies = [policyAnalysisTaskId];
  }
  
  const visualizationTask2 = workflow.getTask(visualizationTaskId);
  if (visualizationTask2) {
    visualizationTask2.dependencies = [processingTaskId];
  }
  
  const reportTask2 = workflow.getTask(reportTaskId);
  if (reportTask2) {
    reportTask2.dependencies = [recommendationTaskId, visualizationTaskId];
  }
  
  // Assign agents to tasks (for resource optimization testing)
  dataTask.assignedAgentId = 'agent1';
  processingTask.assignedAgentId = 'agent1';
  analysisTask.assignedAgentId = 'agent1';
  policyAnalysisTask.assignedAgentId = 'agent3';
  recommendationTask.assignedAgentId = 'agent3';
  visualizationTask.assignedAgentId = 'agent5';
  reportTask.assignedAgentId = 'agent5';
  
  return workflow;
}

/**
 * Simulates workflow execution
 * @param workflow Workflow to execute
 * @param optimizer Workflow optimizer
 * @returns Execution ID
 */
async function simulateWorkflowExecution(workflow: Workflow, optimizer: WorkflowOptimizer): Promise<string> {
  // Create execution profile
  const profile = optimizer.createExecutionProfile(workflow);
  
  // Simulate task execution (in sequential order based on dependencies)
  const executionOrder = getExecutionOrder(workflow);
  
  console.log('Simulating workflow execution...');
  console.log(`Execution order: ${executionOrder.map(id => {
    const task = workflow.getTask(id);
    return task ? task.name : id;
  }).join(' -> ')}`);
  
  // Update task statuses
  for (const taskId of executionOrder) {
    const task = workflow.getTask(taskId);
    if (!task) continue;
    
    // Update task status to running
    task.updateStatus(TaskStatus.RUNNING);
    
    // Update execution profile
    const taskProfiles = new Map(profile.taskProfiles);
    const taskProfile = taskProfiles.get(taskId);
    
    if (taskProfile) {
      taskProfile.startTime = Date.now();
      taskProfile.status = TaskStatus.RUNNING;
      taskProfiles.set(taskId, taskProfile);
      
      optimizer.updateExecutionProfile(profile.executionId, { taskProfiles });
    }
    
    // Simulate task execution time
    await new Promise(resolve => setTimeout(resolve, 10));
    
    // Update task status to completed
    task.updateStatus(TaskStatus.COMPLETED);
    
    // Update execution profile
    const updatedTaskProfiles = new Map(profile.taskProfiles);
    const updatedTaskProfile = updatedTaskProfiles.get(taskId);
    
    if (updatedTaskProfile) {
      updatedTaskProfile.endTime = Date.now();
      updatedTaskProfile.status = TaskStatus.COMPLETED;
      updatedTaskProfile.duration = updatedTaskProfile.endTime - (updatedTaskProfile.startTime || 0);
      updatedTaskProfiles.set(taskId, updatedTaskProfile);
      
      optimizer.updateExecutionProfile(profile.executionId, { taskProfiles: updatedTaskProfiles });
    }
  }
  
  // Update workflow status
  workflow.updateStatus(WorkflowStatus.COMPLETED);
  
  // Update execution profile
  optimizer.updateExecutionProfile(profile.executionId, { 
    status: WorkflowStatus.COMPLETED,
    endTime: Date.now()
  });
  
  return profile.executionId;
}

/**
 * Gets the execution order for a workflow
 * @param workflow Workflow to analyze
 * @returns Array of task IDs in execution order
 */
function getExecutionOrder(workflow: Workflow): string[] {
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
  
  return result;
}

/**
 * Tests the workflow optimizer
 */
async function testWorkflowOptimizer(): Promise<void> {
  console.log('Starting workflow optimizer test...\n');
  
  // Create agent registry and task allocator
  const agentRegistry = new MockAgentRegistry();
  const taskAllocator = new TaskAllocator(agentRegistry);
  
  // Initialize task allocator
  await taskAllocator.initialize();
  
  // Create workflow optimizer
  const optimizer = new WorkflowOptimizer();
  await optimizer.initialize(taskAllocator);
  
  // Create test workflow
  const workflow = createTestWorkflow();
  console.log(`Created test workflow: ${workflow.name}`);
  console.log(`Tasks: ${workflow.tasks.size}`);
  console.log(`Execution mode: ${workflow.executionMode}`);
  
  // Simulate workflow execution
  const executionId = await simulateWorkflowExecution(workflow, optimizer);
  console.log(`Workflow execution completed with ID: ${executionId}`);
  
  // Get execution profile
  const executionProfile = optimizer.getExecutionProfile(executionId);
  if (!executionProfile) {
    console.error('No execution profile found');
    return;
  }
  
  console.log('\nExecution profile:');
  console.log(`Start time: ${new Date(executionProfile.startTime).toISOString()}`);
  console.log(`End time: ${executionProfile.endTime ? new Date(executionProfile.endTime).toISOString() : 'N/A'}`);
  console.log(`Status: ${executionProfile.status}`);
  console.log(`Tasks: ${executionProfile.taskProfiles.size}`);
  
  // Print task profiles
  console.log('\nTask profiles:');
  for (const [taskId, profile] of executionProfile.taskProfiles.entries()) {
    const task = workflow.getTask(taskId);
    if (!task) continue;
    
    console.log(`- ${task.name}:`);
    console.log(`  Status: ${profile.status}`);
    console.log(`  Agent: ${profile.agentId || 'None'}`);
    console.log(`  Duration: ${profile.duration ? `${profile.duration}ms` : 'N/A'}`);
  }
  
  // Print bottlenecks
  console.log('\nIdentified bottlenecks:');
  for (const bottleneck of executionProfile.bottlenecks) {
    console.log(`- Type: ${bottleneck.type}`);
    console.log(`  Severity: ${bottleneck.severity}`);
    console.log(`  Description: ${bottleneck.description}`);
    console.log(`  Recommendations:`);
    for (const recommendation of bottleneck.recommendations) {
      console.log(`    - ${recommendation}`);
    }
  }
  
  // ======= Test Parallelization Strategy =======
  console.log('\n=== Parallelization Strategy Test ===');
  
  // Create optimization options
  const parallelizationOptions: OptimizationOptions = {
    optimizationGoal: 'performance',
    constraints: {
      maxDuration: 300000, // 5 minutes
      maxParallelism: 4
    },
    preferences: {
      parallelizationPreference: 0.8
    },
    optimizationLevel: 'moderate'
  };
  
  // Optimize workflow
  const parallelizationResult = await optimizer.optimizeWorkflow(workflow, parallelizationOptions);
  
  console.log('Parallelization optimization result:');
  console.log(`Optimization ID: ${parallelizationResult.optimizationId}`);
  console.log(`Changes:`);
  
  // Print task parallelization
  console.log('Task parallelization:');
  for (const parallelization of parallelizationResult.changes.taskParallelization) {
    const task = workflow.getTask(parallelization.taskId);
    if (!task) continue;
    
    console.log(`- ${task.name} parallelized with:`);
    for (const parallelTaskId of parallelization.parallelizedWith) {
      const parallelTask = workflow.getTask(parallelTaskId);
      if (parallelTask) {
        console.log(`  - ${parallelTask.name}`);
      }
    }
  }
  
  // Print expected improvements
  console.log('\nExpected improvements:');
  console.log(`- Duration reduction: ${parallelizationResult.expectedImprovements.durationReduction.toFixed(1)}%`);
  console.log(`- Resource efficiency gain: ${parallelizationResult.expectedImprovements.resourceEfficiencyGain.toFixed(1)}%`);
  console.log(`- Reliability increase: ${parallelizationResult.expectedImprovements.reliabilityIncrease.toFixed(1)}%`);
  console.log(`- Overall improvement: ${parallelizationResult.expectedImprovements.overallImprovement.toFixed(1)}%`);
  
  // Print optimized workflow
  console.log('\nOptimized workflow:');
  console.log(`Execution mode: ${parallelizationResult.optimizedWorkflow.executionMode}`);
  console.log('Task types:');
  for (const task of parallelizationResult.optimizedWorkflow.tasks.values()) {
    console.log(`- ${task.name}: ${task.type}`);
  }
  
  // Print recommendations
  console.log('\nRecommendations:');
  for (const recommendation of parallelizationResult.recommendations) {
    console.log(`- ${recommendation}`);
  }
  
  // ======= Test Resource Optimization Strategy =======
  console.log('\n=== Resource Optimization Strategy Test ===');
  
  // Create optimization options
  const resourceOptions: OptimizationOptions = {
    optimizationGoal: 'resource_efficiency',
    constraints: {
      maxResourceUsage: 0.8,
      minSuccessRate: 0.9
    },
    preferences: {
      resourceBalancePreference: 0.7
    },
    optimizationLevel: 'moderate',
    allowReallocations: true
  };
  
  // Optimize workflow
  const resourceResult = await optimizer.optimizeWorkflow(workflow, resourceOptions);
  
  console.log('Resource optimization result:');
  console.log(`Optimization ID: ${resourceResult.optimizationId}`);
  console.log(`Changes:`);
  
  // Print resource reallocations
  console.log('Resource reallocations:');
  for (const reallocation of resourceResult.changes.resourceReallocations) {
    const task = workflow.getTask(reallocation.taskId);
    if (!task) continue;
    
    console.log(`- ${task.name}: ${reallocation.originalResourceId || 'None'} -> ${reallocation.newResourceId}`);
  }
  
  // Print expected improvements
  console.log('\nExpected improvements:');
  console.log(`- Duration reduction: ${resourceResult.expectedImprovements.durationReduction.toFixed(1)}%`);
  console.log(`- Resource efficiency gain: ${resourceResult.expectedImprovements.resourceEfficiencyGain.toFixed(1)}%`);
  console.log(`- Reliability increase: ${resourceResult.expectedImprovements.reliabilityIncrease.toFixed(1)}%`);
  console.log(`- Overall improvement: ${resourceResult.expectedImprovements.overallImprovement.toFixed(1)}%`);
  
  // Print recommendations
  console.log('\nRecommendations:');
  for (const recommendation of resourceResult.recommendations) {
    console.log(`- ${recommendation}`);
  }
  
  // ======= Test Strategy Factory =======
  console.log('\n=== Strategy Factory Test ===');
  
  // Test strategy factory
  const performanceStrategy = OptimizationStrategyFactory.createStrategy({
    optimizationGoal: 'performance',
    constraints: {},
    preferences: {},
    optimizationLevel: 'moderate'
  });
  
  const resourceStrategy = OptimizationStrategyFactory.createStrategy({
    optimizationGoal: 'resource_efficiency',
    constraints: {},
    preferences: {},
    optimizationLevel: 'moderate'
  });
  
  const balancedStrategy = OptimizationStrategyFactory.createStrategy({
    optimizationGoal: 'balanced',
    constraints: {},
    preferences: {},
    optimizationLevel: 'moderate'
  });
  
  console.log('Strategy factory results:');
  console.log(`- Performance goal: ${performanceStrategy.name}`);
  console.log(`- Resource efficiency goal: ${resourceStrategy.name}`);
  console.log(`- Balanced goal: ${balancedStrategy.name}`);
  
  console.log('\nWorkflow optimizer test completed');
}

// Execute test function
if (require.main === module) {
  testWorkflowOptimizer().catch(console.error);
}

export { testWorkflowOptimizer };