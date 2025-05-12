/**
 * Models for multi-agent workflow components and patterns
 */

import { 
  TaskType, 
  TaskCondition, 
  WorkflowExecutionMode,
  CoordinationStrategy,
  TaskOptions
} from './workflow_orchestrator';

/**
 * Represents the flow control type for workflow nodes
 */
export enum FlowControlType {
  SEQUENCE = 'sequence',       // Tasks executed in sequence
  PARALLEL = 'parallel',       // Tasks executed in parallel
  CHOICE = 'choice',           // One branch is chosen based on condition
  JOIN = 'join',               // Wait for multiple branches to complete
  ITERATE = 'iterate',         // Repeat tasks until condition is met
  TERMINATE = 'terminate',     // End workflow execution
  COMPENSATE = 'compensate',   // Run compensation logic for failure
  DEFER = 'defer',             // Defer execution to a later time
  TIMEOUT = 'timeout',         // Execute with timeout control
  EVENT_DRIVEN = 'event'       // Execute based on external event
}

/**
 * Represents a pattern for common workflow structures
 */
export enum WorkflowPattern {
  SEQUENTIAL = 'sequential',             // Simple sequential execution
  PARALLEL_SPLIT = 'parallel_split',     // Split into parallel branches
  SYNCHRONIZATION = 'synchronization',   // Join parallel branches
  EXCLUSIVE_CHOICE = 'exclusive_choice', // Choose one path based on condition
  SIMPLE_MERGE = 'simple_merge',         // Merge exclusive paths
  MULTI_CHOICE = 'multi_choice',         // Choose multiple paths
  MULTI_MERGE = 'multi_merge',           // Merge multiple paths independently
  DISCRIMINATOR = 'discriminator',       // First path triggers continuation
  MILESTONE = 'milestone',               // Continue when milestone reached
  INTERLEAVED_PARALLEL = 'interleaved',  // Parallel but not simultaneously
  CANCEL_ACTIVITY = 'cancel_activity',   // Cancel ongoing activities
  CANCEL_CASE = 'cancel_case',           // Cancel entire workflow
  STRUCTURED_LOOP = 'structured_loop',   // Structured iteration
  ARBITRARY_LOOP = 'arbitrary_loop',     // Arbitrary iteration
  DEFERRED_CHOICE = 'deferred_choice',   // Choice made by external event
  CRITICAL_SECTION = 'critical_section', // Exclusive access to resource
  COMPENSATING_ACTION = 'compensation'   // Undo completed activities
}

/**
 * Represents the scope or impact level of a task or workflow
 */
export enum ScopeLevel {
  LOCAL = 'local',         // Impacts local components only
  INTRA_AGENT = 'intra',   // Impacts within a single agent
  INTER_AGENT = 'inter',   // Impacts multiple agents
  GLOBAL = 'global',       // Impacts the entire system
  EXTERNAL = 'external'    // Impacts external systems
}

/**
 * Represents the domain of a workflow or task
 */
export enum WorkflowDomain {
  ECONOMIC = 'economic',           // Economic analysis and modeling
  HEALTHCARE = 'healthcare',       // Healthcare systems and data
  GOVERNANCE = 'governance',       // Governance and policy
  DATA_ANALYSIS = 'data_analysis', // Data analysis and reporting
  PLANNING = 'planning',           // Planning and scheduling
  DECISION = 'decision',           // Decision making
  COORDINATION = 'coordination',   // Agent coordination
  INTEGRATION = 'integration',     // System integration
  MONITOR = 'monitor',             // System monitoring
  KNOWLEDGE = 'knowledge',         // Knowledge management
  LEARNING = 'learning',           // System learning
  USER_INTERACTION = 'user'        // User interaction
}

/**
 * Represents the skill level required for a task
 */
export enum SkillLevel {
  BASIC = 'basic',             // Basic skills
  INTERMEDIATE = 'intermediate', // Intermediate skills
  ADVANCED = 'advanced',       // Advanced skills
  EXPERT = 'expert',           // Expert skills
  SPECIALIZED = 'specialized'  // Specialized domain skills
}

/**
 * Defines agent capabilities
 */
export interface AgentCapability {
  domain: string;              // Domain of capability
  skillLevel: SkillLevel;      // Skill level
  functions: string[];         // Functions the agent can perform
  knowledgeBases: string[];    // Knowledge bases the agent can access
  resources: string[];         // Resources the agent can use
  metadata: Record<string, any>; // Additional metadata
}

/**
 * Options for defining a workflow pattern
 */
export interface PatternOptions {
  name: string;                  // Pattern name
  pattern: WorkflowPattern;      // Pattern type
  nodes: TaskOptions[];          // Tasks in the pattern
  flowControls: FlowControlType[]; // Flow control types
  connections: [string, string][]; // Connections between nodes (nodeId, nodeId)
  parameters: Record<string, any>; // Pattern parameters
  metadata: Record<string, any>;   // Additional metadata
}

/**
 * Factory for creating common workflow patterns
 */
export class WorkflowPatternFactory {
  /**
   * Creates a sequential workflow pattern
   * @param name Pattern name
   * @param tasks Tasks in sequence
   * @returns Pattern options
   */
  static createSequential(name: string, tasks: TaskOptions[]): PatternOptions {
    const connections: [string, string][] = [];
    
    // Connect tasks in sequence
    for (let i = 0; i < tasks.length - 1; i++) {
      connections.push([`task_${i}`, `task_${i + 1}`]);
    }
    
    return {
      name,
      pattern: WorkflowPattern.SEQUENTIAL,
      nodes: tasks.map((task, index) => ({
        ...task,
        name: task.name || `Task ${index + 1}`,
        metadata: { ...task.metadata, nodeId: `task_${index}` }
      })),
      flowControls: [FlowControlType.SEQUENCE],
      connections,
      parameters: {},
      metadata: {}
    };
  }
  
  /**
   * Creates a parallel split and synchronization pattern
   * @param name Pattern name
   * @param initialTask Initial task before split
   * @param parallelTasks Tasks to be executed in parallel
   * @param finalTask Final task after synchronization
   * @returns Pattern options
   */
  static createParallelSplit(
    name: string,
    initialTask: TaskOptions,
    parallelTasks: TaskOptions[],
    finalTask: TaskOptions
  ): PatternOptions {
    const connections: [string, string][] = [];
    
    // Connect initial task to all parallel tasks
    for (let i = 0; i < parallelTasks.length; i++) {
      connections.push(['initial', `parallel_${i}`]);
    }
    
    // Connect all parallel tasks to final task
    for (let i = 0; i < parallelTasks.length; i++) {
      connections.push([`parallel_${i}`, 'final']);
    }
    
    return {
      name,
      pattern: WorkflowPattern.PARALLEL_SPLIT,
      nodes: [
        {
          ...initialTask,
          name: initialTask.name || 'Initial Task',
          metadata: { ...initialTask.metadata, nodeId: 'initial' }
        },
        ...parallelTasks.map((task, index) => ({
          ...task,
          name: task.name || `Parallel Task ${index + 1}`,
          metadata: { ...task.metadata, nodeId: `parallel_${index}` }
        })),
        {
          ...finalTask,
          name: finalTask.name || 'Final Task',
          metadata: { ...finalTask.metadata, nodeId: 'final' }
        }
      ],
      flowControls: [FlowControlType.SEQUENCE, FlowControlType.PARALLEL, FlowControlType.JOIN],
      connections,
      parameters: {},
      metadata: {}
    };
  }
  
  /**
   * Creates an exclusive choice pattern
   * @param name Pattern name
   * @param initialTask Initial task before choice
   * @param branches Tasks for each branch with conditions
   * @param finalTask Optional final task after merge
   * @returns Pattern options
   */
  static createExclusiveChoice(
    name: string,
    initialTask: TaskOptions,
    branches: { task: TaskOptions, condition: TaskCondition }[],
    finalTask?: TaskOptions
  ): PatternOptions {
    const connections: [string, string][] = [];
    
    // Connect initial task to all branch tasks
    for (let i = 0; i < branches.length; i++) {
      connections.push(['initial', `branch_${i}`]);
    }
    
    // If final task exists, connect all branches to it
    if (finalTask) {
      for (let i = 0; i < branches.length; i++) {
        connections.push([`branch_${i}`, 'final']);
      }
    }
    
    const nodes: TaskOptions[] = [
      {
        ...initialTask,
        name: initialTask.name || 'Initial Task',
        metadata: { ...initialTask.metadata, nodeId: 'initial' }
      },
      ...branches.map((branch, index) => ({
        ...branch.task,
        name: branch.task.name || `Branch Task ${index + 1}`,
        condition: branch.condition,
        type: TaskType.CONDITIONAL,
        metadata: { ...branch.task.metadata, nodeId: `branch_${index}` }
      }))
    ];
    
    if (finalTask) {
      nodes.push({
        ...finalTask,
        name: finalTask.name || 'Final Task',
        metadata: { ...finalTask.metadata, nodeId: 'final' }
      });
    }
    
    return {
      name,
      pattern: WorkflowPattern.EXCLUSIVE_CHOICE,
      nodes,
      flowControls: [FlowControlType.SEQUENCE, FlowControlType.CHOICE],
      connections,
      parameters: {},
      metadata: {}
    };
  }
  
  /**
   * Creates a structured loop pattern
   * @param name Pattern name
   * @param initialTask Initial task before loop
   * @param loopTask Task to be executed repeatedly
   * @param loopCondition Condition for continuing the loop
   * @param finalTask Final task after loop
   * @returns Pattern options
   */
  static createStructuredLoop(
    name: string,
    initialTask: TaskOptions,
    loopTask: TaskOptions,
    loopCondition: TaskCondition,
    finalTask: TaskOptions
  ): PatternOptions {
    return {
      name,
      pattern: WorkflowPattern.STRUCTURED_LOOP,
      nodes: [
        {
          ...initialTask,
          name: initialTask.name || 'Initial Task',
          metadata: { ...initialTask.metadata, nodeId: 'initial' }
        },
        {
          ...loopTask,
          name: loopTask.name || 'Loop Task',
          type: TaskType.ITERATIVE,
          condition: loopCondition,
          metadata: { ...loopTask.metadata, nodeId: 'loop' }
        },
        {
          ...finalTask,
          name: finalTask.name || 'Final Task',
          metadata: { ...finalTask.metadata, nodeId: 'final' }
        }
      ],
      flowControls: [FlowControlType.SEQUENCE, FlowControlType.ITERATE],
      connections: [
        ['initial', 'loop'],
        ['loop', 'loop'], // Self-reference for iteration
        ['loop', 'final']
      ],
      parameters: {},
      metadata: {}
    };
  }
  
  /**
   * Creates a milestone pattern
   * @param name Pattern name
   * @param initialTask Initial task before milestone
   * @param milestoneTask Task representing the milestone
   * @param dependentTask Task dependent on milestone
   * @param finalTask Final task
   * @returns Pattern options
   */
  static createMilestone(
    name: string,
    initialTask: TaskOptions,
    milestoneTask: TaskOptions,
    dependentTask: TaskOptions,
    finalTask: TaskOptions
  ): PatternOptions {
    return {
      name,
      pattern: WorkflowPattern.MILESTONE,
      nodes: [
        {
          ...initialTask,
          name: initialTask.name || 'Initial Task',
          metadata: { ...initialTask.metadata, nodeId: 'initial' }
        },
        {
          ...milestoneTask,
          name: milestoneTask.name || 'Milestone Task',
          metadata: { ...milestoneTask.metadata, nodeId: 'milestone' }
        },
        {
          ...dependentTask,
          name: dependentTask.name || 'Dependent Task',
          dependencies: ['milestone'],
          metadata: { ...dependentTask.metadata, nodeId: 'dependent' }
        },
        {
          ...finalTask,
          name: finalTask.name || 'Final Task',
          metadata: { ...finalTask.metadata, nodeId: 'final' }
        }
      ],
      flowControls: [FlowControlType.SEQUENCE, FlowControlType.EVENT_DRIVEN],
      connections: [
        ['initial', 'milestone'],
        ['milestone', 'dependent'],
        ['dependent', 'final']
      ],
      parameters: {},
      metadata: {}
    };
  }
  
  /**
   * Creates a compensating action pattern
   * @param name Pattern name
   * @param mainTask Main task that might fail
   * @param compensationTask Task to execute if main task fails
   * @param finalTask Final task
   * @returns Pattern options
   */
  static createCompensatingAction(
    name: string,
    mainTask: TaskOptions,
    compensationTask: TaskOptions,
    finalTask: TaskOptions
  ): PatternOptions {
    return {
      name,
      pattern: WorkflowPattern.COMPENSATING_ACTION,
      nodes: [
        {
          ...mainTask,
          name: mainTask.name || 'Main Task',
          fallbackTaskId: 'compensation',
          metadata: { ...mainTask.metadata, nodeId: 'main', critical: true }
        },
        {
          ...compensationTask,
          name: compensationTask.name || 'Compensation Task',
          metadata: { ...compensationTask.metadata, nodeId: 'compensation' }
        },
        {
          ...finalTask,
          name: finalTask.name || 'Final Task',
          metadata: { ...finalTask.metadata, nodeId: 'final' }
        }
      ],
      flowControls: [FlowControlType.SEQUENCE, FlowControlType.COMPENSATE],
      connections: [
        ['main', 'final'],
        ['main', 'compensation'], // Failure path
        ['compensation', 'final']
      ],
      parameters: {},
      metadata: {}
    };
  }
}

/**
 * Factory for creating domain-specific workflow templates
 */
export class DomainWorkflowFactory {
  /**
   * Creates an economic analysis workflow template
   * @param name Template name
   * @param version Template version
   * @returns Template options
   */
  static createEconomicAnalysisWorkflow(name: string, version: string): any {
    return {
      id: `economic_analysis_${version}`,
      name,
      description: 'Template for economic analysis workflows',
      version,
      executionMode: WorkflowExecutionMode.SEQUENTIAL,
      coordinationStrategy: CoordinationStrategy.CENTRALIZED,
      parameters: [
        {
          name: 'analysisType',
          description: 'Type of economic analysis to perform',
          type: 'string',
          required: true
        },
        {
          name: 'dataSource',
          description: 'Source of economic data',
          type: 'string',
          required: true
        },
        {
          name: 'timeframe',
          description: 'Timeframe for analysis',
          type: 'string',
          required: true
        },
        {
          name: 'indicators',
          description: 'Economic indicators to analyze',
          type: 'array',
          required: false,
          defaultValue: []
        }
      ],
      requiredAgentTypes: ['economic', 'data_analysis'],
      timeout: 3600000, // 1 hour
      metadata: {
        domain: WorkflowDomain.ECONOMIC,
        complexity: 'medium',
        estimatedDuration: 1800000 // 30 minutes
      },
      tags: ['economic', 'analysis', 'template']
    };
  }
  
  /**
   * Creates a healthcare workflow template
   * @param name Template name
   * @param version Template version
   * @returns Template options
   */
  static createHealthcareWorkflow(name: string, version: string): any {
    return {
      id: `healthcare_${version}`,
      name,
      description: 'Template for healthcare workflows',
      version,
      executionMode: WorkflowExecutionMode.PARALLEL,
      coordinationStrategy: CoordinationStrategy.CENTRALIZED,
      parameters: [
        {
          name: 'patientId',
          description: 'Patient identifier',
          type: 'string',
          required: true
        },
        {
          name: 'analysisType',
          description: 'Type of healthcare analysis',
          type: 'string',
          required: true
        },
        {
          name: 'dataAccess',
          description: 'Level of data access',
          type: 'string',
          required: true
        }
      ],
      requiredAgentTypes: ['healthcare', 'ehr'],
      timeout: 1800000, // 30 minutes
      metadata: {
        domain: WorkflowDomain.HEALTHCARE,
        complexity: 'high',
        estimatedDuration: 900000 // 15 minutes
      },
      tags: ['healthcare', 'ehr', 'template']
    };
  }
  
  /**
   * Creates a policy analysis workflow template
   * @param name Template name
   * @param version Template version
   * @returns Template options
   */
  static createPolicyAnalysisWorkflow(name: string, version: string): any {
    return {
      id: `policy_analysis_${version}`,
      name,
      description: 'Template for policy analysis workflows',
      version,
      executionMode: WorkflowExecutionMode.HYBRID,
      coordinationStrategy: CoordinationStrategy.CENTRALIZED,
      parameters: [
        {
          name: 'policyArea',
          description: 'Area of policy to analyze',
          type: 'string',
          required: true
        },
        {
          name: 'jurisdiction',
          description: 'Jurisdiction for policy analysis',
          type: 'string',
          required: true
        },
        {
          name: 'stakeholders',
          description: 'Stakeholders affected by policy',
          type: 'array',
          required: false,
          defaultValue: []
        }
      ],
      requiredAgentTypes: ['gov', 'policy', 'economic'],
      timeout: 7200000, // 2 hours
      metadata: {
        domain: WorkflowDomain.GOVERNANCE,
        complexity: 'high',
        estimatedDuration: 3600000 // 1 hour
      },
      tags: ['policy', 'governance', 'analysis', 'template']
    };
  }
  
  /**
   * Creates a data analysis workflow template
   * @param name Template name
   * @param version Template version
   * @returns Template options
   */
  static createDataAnalysisWorkflow(name: string, version: string): any {
    return {
      id: `data_analysis_${version}`,
      name,
      description: 'Template for data analysis workflows',
      version,
      executionMode: WorkflowExecutionMode.PARALLEL,
      coordinationStrategy: CoordinationStrategy.CENTRALIZED,
      parameters: [
        {
          name: 'dataSource',
          description: 'Source of data to analyze',
          type: 'string',
          required: true
        },
        {
          name: 'analysisType',
          description: 'Type of analysis to perform',
          type: 'string',
          required: true
        },
        {
          name: 'outputFormat',
          description: 'Format for analysis output',
          type: 'string',
          required: false,
          defaultValue: 'json'
        }
      ],
      requiredAgentTypes: ['data_analysis'],
      timeout: 1800000, // 30 minutes
      metadata: {
        domain: WorkflowDomain.DATA_ANALYSIS,
        complexity: 'medium',
        estimatedDuration: 600000 // 10 minutes
      },
      tags: ['data', 'analysis', 'template']
    };
  }
  
  /**
   * Creates a coordination workflow template
   * @param name Template name
   * @param version Template version
   * @returns Template options
   */
  static createCoordinationWorkflow(name: string, version: string): any {
    return {
      id: `coordination_${version}`,
      name,
      description: 'Template for agent coordination workflows',
      version,
      executionMode: WorkflowExecutionMode.ADAPTIVE,
      coordinationStrategy: CoordinationStrategy.DECENTRALIZED,
      parameters: [
        {
          name: 'taskType',
          description: 'Type of task to coordinate',
          type: 'string',
          required: true
        },
        {
          name: 'agentTypes',
          description: 'Types of agents to coordinate',
          type: 'array',
          required: true
        },
        {
          name: 'coordinationStrategy',
          description: 'Strategy for coordination',
          type: 'string',
          required: false,
          defaultValue: 'consensus'
        }
      ],
      requiredAgentTypes: ['coordinator'],
      timeout: 3600000, // 1 hour
      metadata: {
        domain: WorkflowDomain.COORDINATION,
        complexity: 'high',
        estimatedDuration: 1800000 // 30 minutes
      },
      tags: ['coordination', 'multi-agent', 'template']
    };
  }
}

/**
 * Factory for creating domain-specific task templates
 */
export class DomainTaskFactory {
  /**
   * Creates an economic data gathering task
   * @param name Task name
   * @returns Task options
   */
  static createEconomicDataGatheringTask(name: string): TaskOptions {
    return {
      name,
      description: 'Gathers economic data from specified sources',
      type: TaskType.SEQUENTIAL,
      agentType: 'economic',
      inputMapping: {
        sources: 'dataSources',
        indicators: 'economicIndicators',
        timeframe: 'analysisTimeframe'
      },
      outputMapping: {
        economicData: 'economicData',
        dataQuality: 'dataQuality',
        coverage: 'dataCoverage'
      },
      timeout: 300000, // 5 minutes
      retries: 2,
      priority: 8,
      metadata: {
        domain: WorkflowDomain.ECONOMIC,
        skillLevel: SkillLevel.INTERMEDIATE,
        critical: true
      }
    };
  }
  
  /**
   * Creates an economic analysis task
   * @param name Task name
   * @returns Task options
   */
  static createEconomicAnalysisTask(name: string): TaskOptions {
    return {
      name,
      description: 'Performs analysis on economic data',
      type: TaskType.SEQUENTIAL,
      agentType: 'economic',
      inputMapping: {
        economicData: 'economicData',
        analysisType: 'analysisType',
        depth: 'analysisDepth',
        parameters: 'analysisParameters'
      },
      outputMapping: {
        analysisResults: 'economicAnalysisResults',
        insights: 'economicInsights',
        confidence: 'analysisConfidence'
      },
      timeout: 600000, // 10 minutes
      retries: 1,
      priority: 7,
      metadata: {
        domain: WorkflowDomain.ECONOMIC,
        skillLevel: SkillLevel.ADVANCED,
        critical: true
      }
    };
  }
  
  /**
   * Creates a policy formulation task
   * @param name Task name
   * @returns Task options
   */
  static createPolicyFormulationTask(name: string): TaskOptions {
    return {
      name,
      description: 'Formulates policy options based on analysis',
      type: TaskType.SEQUENTIAL,
      agentType: 'gov',
      inputMapping: {
        analysisResults: 'economicAnalysisResults',
        insights: 'economicInsights',
        constraints: 'policyConstraints',
        goals: 'policyGoals'
      },
      outputMapping: {
        policyOptions: 'policyOptions',
        recommendations: 'policyRecommendations',
        impacts: 'policyImpacts'
      },
      timeout: 900000, // 15 minutes
      retries: 1,
      priority: 8,
      metadata: {
        domain: WorkflowDomain.GOVERNANCE,
        skillLevel: SkillLevel.EXPERT,
        critical: true
      }
    };
  }
  
  /**
   * Creates a healthcare data processing task
   * @param name Task name
   * @returns Task options
   */
  static createHealthcareDataProcessingTask(name: string): TaskOptions {
    return {
      name,
      description: 'Processes healthcare data with privacy compliance',
      type: TaskType.SEQUENTIAL,
      agentType: 'ehr',
      inputMapping: {
        patientData: 'rawPatientData',
        compliance: 'complianceRequirements',
        anonymization: 'anonymizationLevel'
      },
      outputMapping: {
        processedData: 'processedHealthcareData',
        complianceReport: 'dataComplianceReport'
      },
      timeout: 600000, // 10 minutes
      retries: 2,
      priority: 9,
      metadata: {
        domain: WorkflowDomain.HEALTHCARE,
        skillLevel: SkillLevel.ADVANCED,
        critical: true
      }
    };
  }
  
  /**
   * Creates a data visualization task
   * @param name Task name
   * @returns Task options
   */
  static createDataVisualizationTask(name: string): TaskOptions {
    return {
      name,
      description: 'Creates visualizations from analysis results',
      type: TaskType.SEQUENTIAL,
      agentType: 'ui',
      inputMapping: {
        data: 'analysisResults',
        type: 'visualizationType',
        options: 'visualizationOptions'
      },
      outputMapping: {
        visualizations: 'dataVisualizations',
        interactive: 'interactiveVisualizations'
      },
      timeout: 300000, // 5 minutes
      retries: 1,
      priority: 6,
      metadata: {
        domain: WorkflowDomain.DATA_ANALYSIS,
        skillLevel: SkillLevel.INTERMEDIATE,
        critical: false
      }
    };
  }
  
  /**
   * Creates a workflow coordination task
   * @param name Task name
   * @returns Task options
   */
  static createWorkflowCoordinationTask(name: string): TaskOptions {
    return {
      name,
      description: 'Coordinates workflow execution across agents',
      type: TaskType.PARALLEL,
      agentType: 'coordinator',
      inputMapping: {
        agents: 'participatingAgents',
        strategy: 'coordinationStrategy',
        goals: 'coordinationGoals'
      },
      outputMapping: {
        coordinationResults: 'coordinationResults',
        communication: 'agentCommunication',
        performance: 'coordinationPerformance'
      },
      timeout: 1200000, // 20 minutes
      retries: 2,
      priority: 8,
      metadata: {
        domain: WorkflowDomain.COORDINATION,
        skillLevel: SkillLevel.EXPERT,
        critical: true
      }
    };
  }
}

export default {
  WorkflowPattern,
  FlowControlType,
  ScopeLevel,
  WorkflowDomain,
  SkillLevel,
  WorkflowPatternFactory,
  DomainWorkflowFactory,
  DomainTaskFactory
};