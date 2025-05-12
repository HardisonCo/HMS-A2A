/**
 * Tests for the workflow generator
 */

import { 
  WorkflowGeneratorFactory, 
  GenerationContext,
  TemplateWorkflowGenerator,
  PatternWorkflowGenerator
} from '../workflow_generator';
import { WorkflowPattern, WorkflowDomain, SkillLevel } from '../workflow_models';
import { TaskType, WorkflowStatus, WorkflowExecutionMode } from '../workflow_orchestrator';
import { WorkflowVisualizationService } from '../workflow_visualization';

/**
 * Tests the workflow generator
 */
async function testWorkflowGenerator(): Promise<void> {
  console.log('Starting workflow generator test...\n');
  
  // ======= Test Template-Based Generator =======
  console.log('=== Template-Based Generator Test ===');
  
  const templateGenerator = WorkflowGeneratorFactory.createTemplateGenerator();
  
  // Define economic generation context
  const economicContext: GenerationContext = {
    domain: 'economic',
    taskTypes: [
      TaskType.SEQUENTIAL,
      TaskType.PARALLEL,
      TaskType.CONDITIONAL
    ],
    agentTypes: ['economic', 'data_analysis', 'gov'],
    constraints: {
      maxExecutionTime: 3600000 // 1 hour
    },
    parameters: {
      dataSource: 'economic_indicators',
      analysisType: 'stagflation',
      timeframe: 'quarterly'
    },
    objectives: [
      'Analyze economic indicators',
      'Generate policy recommendations'
    ],
    complexityLevel: 5,
    maxTasks: 8,
    metadata: {
      priority: 'high',
      department: 'treasury'
    }
  };
  
  // Generate workflow
  console.log('Generating workflow from economic context...');
  const economicResult = templateGenerator.createWorkflow(economicContext);
  
  // Print workflow info
  console.log(`Generated workflow: ${economicResult.workflow.name}`);
  console.log(`Execution mode: ${economicResult.workflow.executionMode}`);
  console.log(`Task count: ${economicResult.workflow.tasks.size}`);
  console.log(`Generation time: ${economicResult.metadata.generationTime}ms`);
  
  // Validate workflow
  console.log(`\nValidation result:`);
  console.log(`Valid: ${economicResult.validationResult?.isValid}`);
  console.log(`Score: ${economicResult.validationResult?.score}`);
  console.log(`Issues: ${economicResult.validationResult?.issues.length}`);
  
  // Display workflow visualization
  console.log('\nWorkflow visualization:');
  const economicVisualization = WorkflowVisualizationService.createVisualization(
    economicResult.workflow,
    { showStatus: true, format: 'mermaid' }
  );
  console.log(economicVisualization);
  
  // Generate template
  console.log('\nGenerating workflow template...');
  const economicTemplate = templateGenerator.generateWorkflowTemplate(economicContext);
  console.log(`Template ID: ${economicTemplate.id}`);
  console.log(`Template name: ${economicTemplate.name}`);
  console.log(`Task templates: ${economicTemplate.taskTemplates.size}`);
  
  // Register template
  templateGenerator.registerTemplate(economicTemplate);
  console.log(`Registered template: ${economicTemplate.id}`);
  
  // Generate workflow from template
  console.log('\nGenerating workflow from template...');
  const templateWorkflow = economicTemplate.createWorkflow(economicContext.parameters);
  console.log(`Generated workflow from template: ${templateWorkflow.name}`);
  console.log(`Task count: ${templateWorkflow.tasks.size}`);
  
  // ======= Test Pattern-Based Generator =======
  console.log('\n=== Pattern-Based Generator Test ===');
  
  const patternGenerator = WorkflowGeneratorFactory.createPatternGenerator();
  
  // Define healthcare generation context with required patterns
  const healthcareContext: GenerationContext = {
    domain: 'healthcare',
    taskTypes: [
      TaskType.SEQUENTIAL,
      TaskType.PARALLEL,
      TaskType.CONDITIONAL
    ],
    agentTypes: ['healthcare', 'ehr', 'data_analysis'],
    constraints: {
      hipaaCompliant: true,
      maxExecutionTime: 1800000 // 30 minutes
    },
    parameters: {
      patientId: 'PATIENT123',
      dataAccess: 'restricted',
      analysisType: 'diagnostic'
    },
    objectives: [
      'Process patient data',
      'Generate diagnostic report'
    ],
    requiredPatterns: [
      WorkflowPattern.SEQUENTIAL,
      WorkflowPattern.PARALLEL_SPLIT,
      WorkflowPattern.SYNCHRONIZATION
    ],
    complexityLevel: 7,
    maxTasks: 12,
    metadata: {
      priority: 'high',
      department: 'radiology'
    }
  };
  
  // Generate workflow
  console.log('Generating workflow from healthcare context...');
  const healthcareResult = patternGenerator.createWorkflow(healthcareContext);
  
  // Print workflow info
  console.log(`Generated workflow: ${healthcareResult.workflow.name}`);
  console.log(`Execution mode: ${healthcareResult.workflow.executionMode}`);
  console.log(`Task count: ${healthcareResult.workflow.tasks.size}`);
  console.log(`Generation time: ${healthcareResult.metadata.generationTime}ms`);
  
  // Validate workflow
  console.log(`\nValidation result:`);
  console.log(`Valid: ${healthcareResult.validationResult?.isValid}`);
  console.log(`Score: ${healthcareResult.validationResult?.score}`);
  console.log(`Issues: ${healthcareResult.validationResult?.issues.length}`);
  
  // Display workflow visualization
  console.log('\nWorkflow visualization:');
  const healthcareVisualization = WorkflowVisualizationService.createVisualization(
    healthcareResult.workflow,
    { showStatus: true, format: 'mermaid' }
  );
  console.log(healthcareVisualization);
  
  // ======= Test Factory-Based Generator Selection =======
  console.log('\n=== Factory-Based Generator Selection Test ===');
  
  // Define governance generation context
  const governanceContext: GenerationContext = {
    domain: 'governance',
    taskTypes: [
      TaskType.SEQUENTIAL,
      TaskType.CONDITIONAL,
      TaskType.ITERATIVE
    ],
    agentTypes: ['gov', 'policy', 'economic'],
    constraints: {
      securityLevel: 'high',
      maxExecutionTime: 7200000 // 2 hours
    },
    parameters: {
      policyArea: 'trade',
      jurisdiction: 'federal',
      stakeholders: ['industry', 'consumers', 'regulators']
    },
    objectives: [
      'Analyze policy impact',
      'Generate compliance guidelines'
    ],
    complexityLevel: 8,
    maxTasks: 15,
    metadata: {
      priority: 'medium',
      department: 'commerce'
    }
  };
  
  // Create generator from factory based on context
  console.log('Creating generator from factory...');
  const generator = WorkflowGeneratorFactory.createGenerator(governanceContext);
  console.log(`Generator type: ${generator.constructor.name}`);
  
  // Generate workflow
  console.log('\nGenerating workflow from governance context...');
  const governanceResult = generator.createWorkflow(governanceContext);
  
  // Print workflow info
  console.log(`Generated workflow: ${governanceResult.workflow.name}`);
  console.log(`Execution mode: ${governanceResult.workflow.executionMode}`);
  console.log(`Task count: ${governanceResult.workflow.tasks.size}`);
  console.log(`Generation time: ${governanceResult.metadata.generationTime}ms`);
  
  // ======= Test Different Complexity Levels =======
  console.log('\n=== Complexity Level Test ===');
  
  // Test low, medium, and high complexity
  const complexityLevels = [3, 6, 9];
  
  for (const complexity of complexityLevels) {
    console.log(`\nTesting complexity level ${complexity}...`);
    
    const complexityContext: GenerationContext = {
      ...economicContext,
      complexityLevel: complexity,
      maxTasks: complexity * 2,
      requiredPatterns: undefined // Use default pattern selection
    };
    
    const complexityGenerator = WorkflowGeneratorFactory.createGenerator(complexityContext);
    const complexityResult = complexityGenerator.createWorkflow(complexityContext);
    
    console.log(`Generated workflow with ${complexityResult.workflow.tasks.size} tasks`);
    console.log(`Execution mode: ${complexityResult.workflow.executionMode}`);
    console.log(`Validation score: ${complexityResult.validationResult?.score}`);
    
    // Print task count by type
    const taskCounts = new Map<TaskType, number>();
    for (const task of complexityResult.workflow.tasks.values()) {
      const count = taskCounts.get(task.type) || 0;
      taskCounts.set(task.type, count + 1);
    }
    
    console.log('Task counts by type:');
    for (const [type, count] of taskCounts.entries()) {
      console.log(`  ${type}: ${count}`);
    }
  }
  
  console.log('\nWorkflow generator test completed');
}

// Execute test function
if (require.main === module) {
  testWorkflowGenerator().catch(console.error);
}

export { testWorkflowGenerator };