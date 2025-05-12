/**
 * Tests for the task allocator
 */

import { 
  TaskAllocator, 
  AllocationConstraints,
  RoundRobinStrategy,
  PerformanceBasedStrategy,
  MarketBasedStrategy,
  AdaptiveAllocationStrategy
} from '../task_allocator';
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
import { Agent } from '../../agents/agent_interface';
import { SkillLevel } from '../workflow_models';

/**
 * Mock agent registry for testing
 */
class MockAgentRegistry implements AgentRegistry {
  private agents: Map<string, Agent> = new Map();
  
  constructor() {
    this.initializeMockAgents();
  }
  
  private initializeMockAgents(): void {
    // Create mock agents for testing
    const mockAgents = [
      this.createMockAgent('agent1', 'economic'),
      this.createMockAgent('agent2', 'economic'),
      this.createMockAgent('agent3', 'economic'),
      this.createMockAgent('agent4', 'healthcare'),
      this.createMockAgent('agent5', 'healthcare'),
      this.createMockAgent('agent6', 'policy'),
      this.createMockAgent('agent7', 'policy'),
      this.createMockAgent('agent8', 'data_analysis')
    ];
    
    // Register agents
    for (const agent of mockAgents) {
      this.agents.set(agent.getId(), agent);
    }
  }
  
  private createMockAgent(id: string, type: string): Agent {
    return {
      getId: () => id,
      getType: () => type,
      isAvailable: () => true,
      getName: () => `Mock Agent ${id}`,
      initialize: async () => {},
      start: async () => {},
      stop: async () => {},
      handleMessage: async () => ({})
    } as Agent;
  }
  
  getAgent(agentId: string): Agent | undefined {
    return this.agents.get(agentId);
  }
  
  getAgentsByType(agentType: string): Agent[] {
    return Array.from(this.agents.values())
      .filter(agent => agent.getType() === agentType);
  }
  
  getAllAgents(): Agent[] {
    return Array.from(this.agents.values());
  }
  
  registerAgent(agent: Agent): void {
    this.agents.set(agent.getId(), agent);
  }
  
  unregisterAgent(agentId: string): void {
    this.agents.delete(agentId);
  }
}

/**
 * Creates a test workflow with tasks
 * @returns Workflow with tasks
 */
function createTestWorkflow(): Workflow {
  // Create workflow
  const workflowOptions: WorkflowOptions = {
    name: 'Test Workflow',
    description: 'A test workflow for task allocation',
    executionMode: WorkflowExecutionMode.PARALLEL,
    coordinationStrategy: CoordinationStrategy.CENTRALIZED,
    priority: 5,
    requiredAgentTypes: ['economic', 'healthcare', 'policy', 'data_analysis'],
    knowledgeBaseScope: []
  };
  
  const workflow = new Workflow(workflowOptions);
  
  // Add economic tasks
  for (let i = 0; i < 3; i++) {
    const task = new Task({
      name: `Economic Task ${i + 1}`,
      description: `An economic analysis task ${i + 1}`,
      type: TaskType.SEQUENTIAL,
      agentType: 'economic',
      priority: 5 + i,
      metadata: {
        domain: 'economic',
        complexity: 'medium'
      }
    });
    
    workflow.addTask(task);
  }
  
  // Add healthcare tasks
  for (let i = 0; i < 2; i++) {
    const task = new Task({
      name: `Healthcare Task ${i + 1}`,
      description: `A healthcare data task ${i + 1}`,
      type: TaskType.SEQUENTIAL,
      agentType: 'healthcare',
      priority: 6 + i,
      metadata: {
        domain: 'healthcare',
        complexity: 'high'
      }
    });
    
    workflow.addTask(task);
  }
  
  // Add policy tasks
  for (let i = 0; i < 2; i++) {
    const task = new Task({
      name: `Policy Task ${i + 1}`,
      description: `A policy analysis task ${i + 1}`,
      type: TaskType.SEQUENTIAL,
      agentType: 'policy',
      priority: 7 + i,
      metadata: {
        domain: 'governance',
        complexity: 'high'
      }
    });
    
    workflow.addTask(task);
  }
  
  // Add data analysis task
  const dataTask = new Task({
    name: 'Data Analysis Task',
    description: 'A data analysis task',
    type: TaskType.SEQUENTIAL,
    agentType: 'data_analysis',
    priority: 6,
    metadata: {
      domain: 'data_analysis',
      complexity: 'medium'
    }
  });
  
  workflow.addTask(dataTask);
  
  return workflow;
}

/**
 * Tests the task allocator
 */
async function testTaskAllocator(): Promise<void> {
  console.log('Starting task allocator test...\n');
  
  // Create agent registry and task allocator
  const agentRegistry = new MockAgentRegistry();
  const taskAllocator = new TaskAllocator(agentRegistry);
  
  // Initialize task allocator
  await taskAllocator.initialize();
  
  // Create test workflow
  const workflow = createTestWorkflow();
  console.log(`Created test workflow with ${workflow.tasks.size} tasks`);
  
  // Get all tasks
  const tasks = Array.from(workflow.tasks.values());
  console.log('Tasks to allocate:');
  for (const task of tasks) {
    console.log(`- ${task.name} (Priority: ${task.priority}, Agent Type: ${task.agentType})`);
  }
  
  // ======= Test Round Robin Strategy =======
  console.log('\n=== Round Robin Strategy Test ===');
  
  const roundRobinAllocations = await taskAllocator.allocateTasks(
    workflow,
    tasks,
    'round_robin'
  );
  
  console.log(`Allocated ${roundRobinAllocations.size} tasks using Round Robin strategy`);
  console.log('Round Robin allocations:');
  for (const [taskId, allocation] of roundRobinAllocations.entries()) {
    const task = workflow.getTask(taskId);
    console.log(`- ${task?.name} -> Agent ${allocation.agentId} (Score: ${allocation.score.toFixed(2)})`);
  }
  
  // ======= Test Performance-Based Strategy =======
  console.log('\n=== Performance-Based Strategy Test ===');
  
  // Reset task assignments
  for (const task of tasks) {
    task.assignedAgentId = undefined;
  }
  
  // Set up some performance history
  taskAllocator.updateTaskStatus('task1', TaskStatus.COMPLETED);
  taskAllocator.updateTaskStatus('task2', TaskStatus.FAILED);
  taskAllocator.updateTaskStatus('task3', TaskStatus.COMPLETED);
  
  const performanceAllocations = await taskAllocator.allocateTasks(
    workflow,
    tasks,
    'performance_based'
  );
  
  console.log(`Allocated ${performanceAllocations.size} tasks using Performance-Based strategy`);
  console.log('Performance-Based allocations:');
  for (const [taskId, allocation] of performanceAllocations.entries()) {
    const task = workflow.getTask(taskId);
    console.log(`- ${task?.name} -> Agent ${allocation.agentId} (Score: ${allocation.score.toFixed(2)})`);
    console.log(`  Metrics: Match=${allocation.metrics.matchScore.toFixed(2)}, Load=${allocation.metrics.loadScore.toFixed(2)}, Performance=${allocation.metrics.performanceScore.toFixed(2)}, Priority=${allocation.metrics.priorityScore.toFixed(2)}`);
  }
  
  // ======= Test Market-Based Strategy =======
  console.log('\n=== Market-Based Strategy Test ===');
  
  // Reset task assignments
  for (const task of tasks) {
    task.assignedAgentId = undefined;
  }
  
  const marketAllocations = await taskAllocator.allocateTasks(
    workflow,
    tasks,
    'market_based'
  );
  
  console.log(`Allocated ${marketAllocations.size} tasks using Market-Based strategy`);
  console.log('Market-Based allocations:');
  for (const [taskId, allocation] of marketAllocations.entries()) {
    const task = workflow.getTask(taskId);
    console.log(`- ${task?.name} -> Agent ${allocation.agentId} (Score: ${allocation.score.toFixed(2)})`);
  }
  
  // ======= Test Adaptive Strategy =======
  console.log('\n=== Adaptive Strategy Test ===');
  
  // Reset task assignments
  for (const task of tasks) {
    task.assignedAgentId = undefined;
  }
  
  const adaptiveAllocations = await taskAllocator.allocateTasks(
    workflow,
    tasks,
    'adaptive'
  );
  
  console.log(`Allocated ${adaptiveAllocations.size} tasks using Adaptive strategy`);
  console.log('Adaptive allocations:');
  for (const [taskId, allocation] of adaptiveAllocations.entries()) {
    const task = workflow.getTask(taskId);
    console.log(`- ${task?.name} -> Agent ${allocation.agentId} (Score: ${allocation.score.toFixed(2)}, Strategy: ${allocation.allocatedBy})`);
  }
  
  // ======= Test Allocation with Constraints =======
  console.log('\n=== Allocation with Constraints Test ===');
  
  // Reset task assignments
  for (const task of tasks) {
    task.assignedAgentId = undefined;
  }
  
  // Define constraints
  const constraints: AllocationConstraints = {
    maxTasksPerAgent: 2,
    loadBalancingFactor: 0.8,
    priorityBoost: 5,
    domainPriorities: {
      economic: 3,
      healthcare: 2,
      governance: 1,
      data_analysis: 2
    },
    preferredAgentIds: ['agent1', 'agent4']
  };
  
  console.log('Allocation constraints:');
  console.log(`- Max tasks per agent: ${constraints.maxTasksPerAgent}`);
  console.log(`- Load balancing factor: ${constraints.loadBalancingFactor}`);
  console.log(`- Priority boost: ${constraints.priorityBoost}`);
  console.log(`- Domain priorities: ${JSON.stringify(constraints.domainPriorities)}`);
  console.log(`- Preferred agents: ${constraints.preferredAgentIds?.join(', ')}`);
  
  const constrainedAllocations = await taskAllocator.allocateTasks(
    workflow,
    tasks,
    'adaptive',
    constraints
  );
  
  console.log(`Allocated ${constrainedAllocations.size} tasks using Adaptive strategy with constraints`);
  console.log('Constrained allocations:');
  for (const [taskId, allocation] of constrainedAllocations.entries()) {
    const task = workflow.getTask(taskId);
    console.log(`- ${task?.name} -> Agent ${allocation.agentId} (Score: ${allocation.score.toFixed(2)}, Strategy: ${allocation.allocatedBy})`);
  }
  
  // ======= Test Task Status Updates =======
  console.log('\n=== Task Status Updates Test ===');
  
  // Simulate task execution
  const taskUpdates: [string, TaskStatus][] = [
    [tasks[0].id, TaskStatus.RUNNING],
    [tasks[1].id, TaskStatus.RUNNING],
    [tasks[0].id, TaskStatus.COMPLETED],
    [tasks[1].id, TaskStatus.FAILED],
    [tasks[2].id, TaskStatus.RUNNING],
    [tasks[2].id, TaskStatus.COMPLETED],
    [tasks[3].id, TaskStatus.RUNNING],
    [tasks[3].id, TaskStatus.COMPLETED],
    [tasks[4].id, TaskStatus.RUNNING],
    [tasks[4].id, TaskStatus.COMPLETED]
  ];
  
  console.log('Simulating task status updates:');
  for (const [taskId, status] of taskUpdates) {
    const task = workflow.getTask(taskId);
    console.log(`- ${task?.name}: ${status}`);
    taskAllocator.updateTaskStatus(taskId, status);
  }
  
  // Get metrics summary
  console.log('\nAgent metrics summary:');
  const metrics = taskAllocator.getMetricsSummary();
  for (const [agentId, summary] of metrics.entries()) {
    console.log(`Agent ${agentId}:`);
    console.log(`- Total tasks: ${summary.taskCount}`);
    console.log(`- Completed tasks: ${summary.completedCount}`);
    console.log(`- Failed tasks: ${summary.failedCount}`);
    console.log(`- Success rate: ${(summary.successRate * 100).toFixed(1)}%`);
    console.log(`- Average duration: ${summary.avgDuration.toFixed(0)}ms`);
  }
  
  // Get strategy usage stats
  console.log('\nStrategy usage statistics:');
  const strategyStats = taskAllocator.getStrategyUsageStats();
  for (const [strategy, stats] of strategyStats.entries()) {
    console.log(`${strategy}:`);
    console.log(`- Used ${stats.count} times`);
    console.log(`- Average score: ${(stats.avgScore * 100).toFixed(1)}%`);
  }
  
  console.log('\nTask allocator test completed');
}

// Execute test function
if (require.main === module) {
  testTaskAllocator().catch(console.error);
}

export { testTaskAllocator };