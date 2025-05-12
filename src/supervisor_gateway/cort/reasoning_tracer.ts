/**
 * Reasoning Tracer for Chain of Recursive Thought (CoRT)
 * 
 * The reasoning tracer tracks the reasoning process during economic analysis,
 * ensures logical consistency, and maintains an audit trail of thought chains.
 */

/**
 * Represents a reasoning step in a chain of thought.
 */
export interface ReasoningStep {
  id: string;
  timestamp: string;
  content: string;
  type: ReasoningStepType;
  source: ReasoningSource;
  confidence: number;
  metadata?: Record<string, any>;
}

/**
 * The type of reasoning step.
 */
export enum ReasoningStepType {
  Premise = 'premise',
  Inference = 'inference',
  Hypothesis = 'hypothesis',
  Evidence = 'evidence',
  Counterargument = 'counterargument',
  Conclusion = 'conclusion',
  Alternative = 'alternative',
  Rebuttal = 'rebuttal'
}

/**
 * The source of a reasoning step.
 */
export enum ReasoningSource {
  EconomicModel = 'economic_model',
  HistoricalData = 'historical_data',
  ExpertKnowledge = 'expert_knowledge',
  InferentialReasoning = 'inferential_reasoning',
  EmpiricalEvidence = 'empirical_evidence',
  TheoreticalFramework = 'theoretical_framework',
  Simulation = 'simulation'
}

/**
 * Represents a connection between reasoning steps.
 */
export interface ReasoningConnection {
  id: string;
  fromStepId: string;
  toStepId: string;
  type: ConnectionType;
  strength: number;
  metadata?: Record<string, any>;
}

/**
 * The type of connection between reasoning steps.
 */
export enum ConnectionType {
  Supports = 'supports',
  Contradicts = 'contradicts',
  Elaborates = 'elaborates',
  Implies = 'implies',
  Precedes = 'precedes',
  Alternatives = 'alternatives'
}

/**
 * Represents a detected logical issue in the reasoning chain.
 */
export interface LogicalIssue {
  id: string;
  type: LogicalIssueType;
  description: string;
  severity: 'low' | 'medium' | 'high';
  affectedStepIds: string[];
  suggestedResolution?: string;
}

/**
 * Types of logical issues that can be detected.
 */
export enum LogicalIssueType {
  Contradiction = 'contradiction',
  CircularReasoning = 'circular_reasoning',
  NonSequitur = 'non_sequitur',
  FalseCorrelation = 'false_correlation',
  IncompleteReasoning = 'incomplete_reasoning',
  UnwarrantedGeneralization = 'unwarranted_generalization',
  FalseEquivalence = 'false_equivalence',
  HiddenAssumption = 'hidden_assumption'
}

/**
 * Represents a complete chain of reasoning.
 */
export interface ReasoningChain {
  id: string;
  name: string;
  description: string;
  steps: ReasoningStep[];
  connections: ReasoningConnection[];
  issues: LogicalIssue[];
  metadata: {
    domain: string;
    created: string;
    lastUpdated: string;
    overallConfidence: number;
    completeness: number;
    coherence: number;
  };
}

/**
 * The synthesis of multiple reasoning chains into a coherent narrative.
 */
export interface ReasoningSynthesis {
  id: string;
  narrative: string;
  sourceChainIds: string[];
  confidenceScore: number;
  uncertaintyAreas: string[];
  keyInsights: string[];
}

/**
 * Configuration options for the reasoning tracer.
 */
export interface ReasoningTracerOptions {
  maxChainDepth?: number;
  confidenceThreshold?: number;
  issueDetectionEnabled?: boolean;
  storageEnabled?: boolean;
  tracePremises?: boolean;
  traceCounterarguments?: boolean;
  synthesizeResults?: boolean;
}

/**
 * The ReasoningTracer keeps track of chains of thought during economic analysis.
 */
export class ReasoningTracer {
  private chains: Map<string, ReasoningChain>;
  private currentChainId: string | null;
  private options: ReasoningTracerOptions;
  private isInitialized: boolean;
  
  /**
   * Creates a new ReasoningTracer instance.
   * 
   * @param options Configuration options
   */
  constructor(options: ReasoningTracerOptions = {}) {
    this.chains = new Map();
    this.currentChainId = null;
    this.options = {
      maxChainDepth: 10,
      confidenceThreshold: 0.5,
      issueDetectionEnabled: true,
      storageEnabled: true,
      tracePremises: true,
      traceCounterarguments: true,
      synthesizeResults: true,
      ...options
    };
    this.isInitialized = false;
  }
  
  /**
   * Initializes the reasoning tracer.
   * 
   * @returns A promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    console.log('Initializing CoRT Reasoning Tracer...');
    
    // In a real implementation, this would initialize storage and other resources
    
    this.isInitialized = true;
    console.log('CoRT Reasoning Tracer initialized successfully');
  }
  
  /**
   * Creates a new reasoning chain.
   * 
   * @param name The name of the chain
   * @param description The description of the chain
   * @param domain The domain of the chain
   * @returns The ID of the created chain
   */
  createChain(name: string, description: string, domain: string): string {
    if (!this.isInitialized) {
      throw new Error('Reasoning Tracer must be initialized before use');
    }
    
    const chainId = this.generateId('chain');
    const timestamp = new Date().toISOString();
    
    const chain: ReasoningChain = {
      id: chainId,
      name,
      description,
      steps: [],
      connections: [],
      issues: [],
      metadata: {
        domain,
        created: timestamp,
        lastUpdated: timestamp,
        overallConfidence: 1.0,
        completeness: 0.0,
        coherence: 1.0
      }
    };
    
    this.chains.set(chainId, chain);
    this.currentChainId = chainId;
    
    console.log(`Created reasoning chain: ${name} (${chainId})`);
    return chainId;
  }
  
  /**
   * Sets the current active reasoning chain.
   * 
   * @param chainId The ID of the chain to set as active
   */
  setCurrentChain(chainId: string): void {
    if (!this.chains.has(chainId)) {
      throw new Error(`Reasoning chain not found: ${chainId}`);
    }
    
    this.currentChainId = chainId;
  }
  
  /**
   * Adds a reasoning step to the current chain.
   * 
   * @param content The content of the reasoning step
   * @param type The type of reasoning step
   * @param source The source of the reasoning step
   * @param confidence The confidence in the reasoning step
   * @param metadata Additional metadata for the step
   * @returns The ID of the created step
   */
  addStep(
    content: string, 
    type: ReasoningStepType, 
    source: ReasoningSource, 
    confidence: number = 0.8,
    metadata: Record<string, any> = {}
  ): string {
    if (!this.currentChainId) {
      throw new Error('No active reasoning chain');
    }
    
    const chain = this.chains.get(this.currentChainId)!;
    const stepId = this.generateId('step');
    
    const step: ReasoningStep = {
      id: stepId,
      timestamp: new Date().toISOString(),
      content,
      type,
      source,
      confidence,
      metadata
    };
    
    chain.steps.push(step);
    chain.metadata.lastUpdated = step.timestamp;
    
    // Update chain metrics
    this.updateChainMetrics(chain);
    
    // Check for logical issues if enabled
    if (this.options.issueDetectionEnabled) {
      this.detectIssues(chain);
    }
    
    return stepId;
  }
  
  /**
   * Adds a connection between two reasoning steps.
   * 
   * @param fromStepId The ID of the source step
   * @param toStepId The ID of the target step
   * @param type The type of connection
   * @param strength The strength of the connection
   * @param metadata Additional metadata for the connection
   * @returns The ID of the created connection
   */
  addConnection(
    fromStepId: string, 
    toStepId: string, 
    type: ConnectionType, 
    strength: number = 0.8,
    metadata: Record<string, any> = {}
  ): string {
    if (!this.currentChainId) {
      throw new Error('No active reasoning chain');
    }
    
    const chain = this.chains.get(this.currentChainId)!;
    
    // Verify that steps exist
    const fromStepExists = chain.steps.some(step => step.id === fromStepId);
    const toStepExists = chain.steps.some(step => step.id === toStepId);
    
    if (!fromStepExists) {
      throw new Error(`Source step not found: ${fromStepId}`);
    }
    
    if (!toStepExists) {
      throw new Error(`Target step not found: ${toStepId}`);
    }
    
    const connectionId = this.generateId('conn');
    
    const connection: ReasoningConnection = {
      id: connectionId,
      fromStepId,
      toStepId,
      type,
      strength,
      metadata
    };
    
    chain.connections.push(connection);
    chain.metadata.lastUpdated = new Date().toISOString();
    
    // Update chain metrics after adding connection
    this.updateChainMetrics(chain);
    
    // Check for logical issues if enabled
    if (this.options.issueDetectionEnabled) {
      this.detectIssues(chain);
    }
    
    return connectionId;
  }
  
  /**
   * Gets all steps in the current chain.
   * 
   * @returns Array of reasoning steps
   */
  getSteps(): ReasoningStep[] {
    if (!this.currentChainId) {
      throw new Error('No active reasoning chain');
    }
    
    return [...this.chains.get(this.currentChainId)!.steps];
  }
  
  /**
   * Gets all connections in the current chain.
   * 
   * @returns Array of reasoning connections
   */
  getConnections(): ReasoningConnection[] {
    if (!this.currentChainId) {
      throw new Error('No active reasoning chain');
    }
    
    return [...this.chains.get(this.currentChainId)!.connections];
  }
  
  /**
   * Gets a specific reasoning chain by ID.
   * 
   * @param chainId The ID of the chain to retrieve
   * @returns The reasoning chain
   */
  getChain(chainId: string): ReasoningChain {
    const chain = this.chains.get(chainId);
    if (!chain) {
      throw new Error(`Reasoning chain not found: ${chainId}`);
    }
    
    return {...chain};
  }
  
  /**
   * Gets all reasoning chains.
   * 
   * @returns Array of reasoning chains
   */
  getAllChains(): ReasoningChain[] {
    return Array.from(this.chains.values()).map(chain => ({...chain}));
  }
  
  /**
   * Gets all logical issues detected in the current chain.
   * 
   * @returns Array of logical issues
   */
  getIssues(): LogicalIssue[] {
    if (!this.currentChainId) {
      throw new Error('No active reasoning chain');
    }
    
    return [...this.chains.get(this.currentChainId)!.issues];
  }
  
  /**
   * Synthesizes multiple reasoning chains into a coherent narrative.
   * 
   * @param chainIds The IDs of the chains to synthesize
   * @returns A reasoning synthesis
   */
  synthesizeChains(chainIds: string[]): ReasoningSynthesis {
    if (!this.options.synthesizeResults) {
      throw new Error('Synthesis is disabled in options');
    }
    
    console.log(`Synthesizing ${chainIds.length} reasoning chains...`);
    
    // Validate that all chains exist
    for (const chainId of chainIds) {
      if (!this.chains.has(chainId)) {
        throw new Error(`Reasoning chain not found: ${chainId}`);
      }
    }
    
    // Extract conclusions from all chains
    const conclusions: string[] = [];
    const allInsights: string[] = [];
    const uncertaintyAreas: string[] = [];
    let averageConfidence = 0;
    
    for (const chainId of chainIds) {
      const chain = this.chains.get(chainId)!;
      
      // Find conclusion steps
      const conclusionSteps = chain.steps.filter(
        step => step.type === ReasoningStepType.Conclusion
      );
      
      if (conclusionSteps.length > 0) {
        // Add the most confident conclusion
        const mostConfidentConclusion = conclusionSteps.reduce(
          (prev, current) => current.confidence > prev.confidence ? current : prev
        );
        
        conclusions.push(`${chain.name}: ${mostConfidentConclusion.content}`);
      } else {
        // If no conclusion, use the last step
        const lastStep = chain.steps[chain.steps.length - 1];
        if (lastStep) {
          conclusions.push(`${chain.name}: ${lastStep.content}`);
        }
      }
      
      // Extract key insights (high confidence inferences)
      const keyInferences = chain.steps.filter(
        step => step.type === ReasoningStepType.Inference && step.confidence > 0.8
      );
      
      keyInferences.forEach(inference => {
        allInsights.push(inference.content);
      });
      
      // Find areas of uncertainty (low confidence steps)
      const uncertainSteps = chain.steps.filter(step => step.confidence < 0.6);
      uncertainSteps.forEach(step => {
        uncertaintyAreas.push(`${step.type}: ${step.content}`);
      });
      
      // Add chain's overall confidence to average
      averageConfidence += chain.metadata.overallConfidence;
    }
    
    // Calculate average confidence
    averageConfidence = chainIds.length > 0 ? averageConfidence / chainIds.length : 0;
    
    // Deduplicate insights and uncertainty areas
    const keyInsights = Array.from(new Set(allInsights));
    const uniqueUncertaintyAreas = Array.from(new Set(uncertaintyAreas));
    
    // Create a narrative from conclusions
    const narrative = this.constructNarrative(conclusions, keyInsights, uniqueUncertaintyAreas);
    
    return {
      id: this.generateId('synth'),
      narrative,
      sourceChainIds: chainIds,
      confidenceScore: averageConfidence,
      uncertaintyAreas: uniqueUncertaintyAreas.slice(0, 5), // Limit to top 5
      keyInsights: keyInsights.slice(0, 7) // Limit to top 7
    };
  }
  
  /**
   * Exports a visualization of the reasoning chain.
   * 
   * @param format The format to export ('json', 'mermaid', or 'text')
   * @returns The visualization in the specified format
   */
  exportVisualization(format: 'json' | 'mermaid' | 'text' = 'json'): string {
    if (!this.currentChainId) {
      throw new Error('No active reasoning chain');
    }
    
    const chain = this.chains.get(this.currentChainId)!;
    
    switch (format) {
      case 'json':
        return JSON.stringify(chain, null, 2);
        
      case 'mermaid':
        return this.generateMermaidDiagram(chain);
        
      case 'text':
        return this.generateTextSummary(chain);
        
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }
  
  /**
   * Detects logical issues in a reasoning chain.
   * 
   * @param chain The reasoning chain to analyze
   */
  private detectIssues(chain: ReasoningChain): void {
    // Clear existing issues
    chain.issues = [];
    
    // Check for contradictions
    this.detectContradictions(chain);
    
    // Check for circular reasoning
    this.detectCircularReasoning(chain);
    
    // Check for non sequiturs
    this.detectNonSequiturs(chain);
    
    // Check for incomplete reasoning
    this.detectIncompleteReasoning(chain);
    
    // Check for hidden assumptions
    this.detectHiddenAssumptions(chain);
  }
  
  /**
   * Detects contradictions in a reasoning chain.
   * 
   * @param chain The reasoning chain to analyze
   */
  private detectContradictions(chain: ReasoningChain): void {
    const steps = chain.steps;
    
    // Simple keyword-based contradiction detection
    for (let i = 0; i < steps.length; i++) {
      for (let j = i + 1; j < steps.length; j++) {
        const step1 = steps[i];
        const step2 = steps[j];
        
        // Check for opposite claims
        if (this.haveContradictoryContent(step1.content, step2.content)) {
          const issue: LogicalIssue = {
            id: this.generateId('issue'),
            type: LogicalIssueType.Contradiction,
            description: `Potential contradiction between steps ${steps.indexOf(step1) + 1} and ${steps.indexOf(step2) + 1}`,
            severity: 'high',
            affectedStepIds: [step1.id, step2.id],
            suggestedResolution: 'Clarify the conditions under which each statement is valid, or revise one of the statements.'
          };
          
          chain.issues.push(issue);
        }
      }
    }
  }
  
  /**
   * Detects circular reasoning in a reasoning chain.
   * 
   * @param chain The reasoning chain to analyze
   */
  private detectCircularReasoning(chain: ReasoningChain): void {
    const connections = chain.connections;
    
    // Build a directed graph
    const graph: Record<string, string[]> = {};
    
    for (const connection of connections) {
      if (!graph[connection.fromStepId]) {
        graph[connection.fromStepId] = [];
      }
      
      graph[connection.fromStepId].push(connection.toStepId);
    }
    
    // Check for cycles
    const visited: Record<string, boolean> = {};
    const recursionStack: Record<string, boolean> = {};
    
    for (const stepId of Object.keys(graph)) {
      if (this.hasCycle(graph, stepId, visited, recursionStack)) {
        // Find the steps involved in the cycle
        const cycleSteps = Object.keys(recursionStack).filter(id => recursionStack[id]);
        
        const issue: LogicalIssue = {
          id: this.generateId('issue'),
          type: LogicalIssueType.CircularReasoning,
          description: `Circular reasoning detected in steps ${cycleSteps.map(id => chain.steps.findIndex(s => s.id === id) + 1).join(', ')}`,
          severity: 'high',
          affectedStepIds: cycleSteps,
          suggestedResolution: 'Break the circular chain by introducing external evidence or premises.'
        };
        
        chain.issues.push(issue);
      }
    }
  }
  
  /**
   * Detects non sequiturs (disconnected reasoning) in a reasoning chain.
   * 
   * @param chain The reasoning chain to analyze
   */
  private detectNonSequiturs(chain: ReasoningChain): void {
    // Check for steps that have no incoming connections (except premises)
    for (let i = 0; i < chain.steps.length; i++) {
      const step = chain.steps[i];
      
      // Skip premises and first step
      if (step.type === ReasoningStepType.Premise || i === 0) {
        continue;
      }
      
      // Check if this step has any incoming connections
      const hasIncoming = chain.connections.some(conn => conn.toStepId === step.id);
      
      if (!hasIncoming) {
        const issue: LogicalIssue = {
          id: this.generateId('issue'),
          type: LogicalIssueType.NonSequitur,
          description: `Step ${i + 1} lacks connection to previous reasoning`,
          severity: 'medium',
          affectedStepIds: [step.id],
          suggestedResolution: 'Connect this step to previous steps or add intermediate reasoning steps.'
        };
        
        chain.issues.push(issue);
      }
    }
  }
  
  /**
   * Detects incomplete reasoning in a reasoning chain.
   * 
   * @param chain The reasoning chain to analyze
   */
  private detectIncompleteReasoning(chain: ReasoningChain): void {
    // Check if there's a conclusion
    const hasConclusion = chain.steps.some(step => step.type === ReasoningStepType.Conclusion);
    
    if (!hasConclusion && chain.steps.length > 1) {
      const issue: LogicalIssue = {
        id: this.generateId('issue'),
        type: LogicalIssueType.IncompleteReasoning,
        description: 'Reasoning chain lacks a formal conclusion',
        severity: 'medium',
        affectedStepIds: [chain.steps[chain.steps.length - 1].id],
        suggestedResolution: 'Add a conclusion step that synthesizes the key inferences.'
      };
      
      chain.issues.push(issue);
    }
    
    // Check for premises
    const hasPremise = chain.steps.some(step => step.type === ReasoningStepType.Premise);
    
    if (!hasPremise && chain.steps.length > 1) {
      const issue: LogicalIssue = {
        id: this.generateId('issue'),
        type: LogicalIssueType.IncompleteReasoning,
        description: 'Reasoning chain lacks explicit premises',
        severity: 'medium',
        affectedStepIds: [chain.steps[0].id],
        suggestedResolution: 'Add premise steps to establish the foundation of your reasoning.'
      };
      
      chain.issues.push(issue);
    }
  }
  
  /**
   * Detects hidden assumptions in a reasoning chain.
   * 
   * @param chain The reasoning chain to analyze
   */
  private detectHiddenAssumptions(chain: ReasoningChain): void {
    // Keywords that often indicate assumptions
    const assumptionKeywords = [
      'assuming', 'assumes', 'assumed', 'assumption',
      'if', 'when', 'whenever', 'given that',
      'presupposes', 'presupposing', 'presupposition',
      'takes for granted', 'must be true',
      'necessarily', 'certainly', 'definitely', 'obviously'
    ];
    
    // Check for inferential leaps (big logical jumps)
    for (const connection of chain.connections) {
      const fromStep = chain.steps.find(step => step.id === connection.fromStepId);
      const toStep = chain.steps.find(step => step.id === connection.toStepId);
      
      if (!fromStep || !toStep) continue;
      
      // Skip non-inferential connections
      if (toStep.type !== ReasoningStepType.Inference && 
          toStep.type !== ReasoningStepType.Conclusion) {
        continue;
      }
      
      // Check for assumption keywords in the connection's target
      let hasExplicitAssumption = false;
      for (const keyword of assumptionKeywords) {
        if (toStep.content.toLowerCase().includes(keyword)) {
          hasExplicitAssumption = true;
          break;
        }
      }
      
      // Check if connection is weak but inference is strong
      if (!hasExplicitAssumption && 
          connection.strength < 0.7 && 
          toStep.confidence > 0.8) {
        const issue: LogicalIssue = {
          id: this.generateId('issue'),
          type: LogicalIssueType.HiddenAssumption,
          description: `Potential hidden assumption in the transition from step ${chain.steps.indexOf(fromStep) + 1} to ${chain.steps.indexOf(toStep) + 1}`,
          severity: 'medium',
          affectedStepIds: [fromStep.id, toStep.id],
          suggestedResolution: 'Add an explicit assumption or intermediate reasoning steps to clarify the logical connection.'
        };
        
        chain.issues.push(issue);
      }
    }
  }
  
  /**
   * Checks if a cycle exists in the graph from a given node.
   * 
   * @param graph The directed graph
   * @param node The current node
   * @param visited Record of visited nodes
   * @param recursionStack Record of nodes in the current recursion stack
   * @returns True if a cycle exists, false otherwise
   */
  private hasCycle(
    graph: Record<string, string[]>, 
    node: string, 
    visited: Record<string, boolean>, 
    recursionStack: Record<string, boolean>
  ): boolean {
    // Mark the current node as visited and add to recursion stack
    visited[node] = true;
    recursionStack[node] = true;
    
    // Visit all adjacent vertices
    const neighbors = graph[node] || [];
    for (const neighbor of neighbors) {
      // Not visited yet, so check recursively
      if (!visited[neighbor] && this.hasCycle(graph, neighbor, visited, recursionStack)) {
        return true;
      } else if (recursionStack[neighbor]) {
        // Already in recursion stack, so cycle exists
        return true;
      }
    }
    
    // Remove from recursion stack
    recursionStack[node] = false;
    return false;
  }
  
  /**
   * Checks if two statements potentially contradict each other.
   * 
   * @param content1 The first statement
   * @param content2 The second statement
   * @returns True if the statements contradict, false otherwise
   */
  private haveContradictoryContent(content1: string, content2: string): boolean {
    const c1 = content1.toLowerCase();
    const c2 = content2.toLowerCase();
    
    // Check for direct contradictions
    const contradictions = [
      { pos: 'will increase', neg: 'will decrease' },
      { pos: 'will rise', neg: 'will fall' },
      { pos: 'is effective', neg: 'is ineffective' },
      { pos: 'is sufficient', neg: 'is insufficient' },
      { pos: 'primarily demand', neg: 'primarily supply' },
      { pos: 'mainly demand', neg: 'mainly supply' },
      { pos: 'is sustainable', neg: 'is unsustainable' },
      { pos: 'will improve', neg: 'will worsen' },
      { pos: 'is necessary', neg: 'is unnecessary' },
      { pos: 'supports', neg: 'contradicts' }
    ];
    
    for (const pair of contradictions) {
      if ((c1.includes(pair.pos) && c2.includes(pair.neg)) || 
          (c1.includes(pair.neg) && c2.includes(pair.pos))) {
        return true;
      }
    }
    
    return false;
  }
  
  /**
   * Updates metrics for a reasoning chain.
   * 
   * @param chain The reasoning chain to update
   */
  private updateChainMetrics(chain: ReasoningChain): void {
    // Calculate overall confidence as average of step confidences
    const totalConfidence = chain.steps.reduce((sum, step) => sum + step.confidence, 0);
    chain.metadata.overallConfidence = chain.steps.length > 0 ? 
      totalConfidence / chain.steps.length : 1.0;
    
    // Calculate completeness based on presence of key step types
    let completeness = 0;
    
    // Check for premises
    if (chain.steps.some(step => step.type === ReasoningStepType.Premise)) {
      completeness += 0.2;
    }
    
    // Check for evidence
    if (chain.steps.some(step => step.type === ReasoningStepType.Evidence)) {
      completeness += 0.2;
    }
    
    // Check for counterarguments
    if (chain.steps.some(step => step.type === ReasoningStepType.Counterargument)) {
      completeness += 0.2;
    }
    
    // Check for inferences
    if (chain.steps.some(step => step.type === ReasoningStepType.Inference)) {
      completeness += 0.2;
    }
    
    // Check for conclusion
    if (chain.steps.some(step => step.type === ReasoningStepType.Conclusion)) {
      completeness += 0.2;
    }
    
    chain.metadata.completeness = completeness;
    
    // Calculate coherence based on connections and issues
    let coherence = 1.0;
    
    // Reduce coherence for each issue
    coherence -= chain.issues.length * 0.1;
    
    // Adjust based on connection strength
    if (chain.connections.length > 0) {
      const avgConnectionStrength = chain.connections.reduce((sum, conn) => sum + conn.strength, 0) / chain.connections.length;
      coherence *= avgConnectionStrength;
    }
    
    chain.metadata.coherence = Math.max(0, Math.min(1, coherence));
  }
  
  /**
   * Constructs a narrative from conclusions and insights.
   * 
   * @param conclusions Array of conclusion statements
   * @param insights Array of key insights
   * @param uncertainties Array of uncertainty areas
   * @returns A synthesized narrative
   */
  private constructNarrative(
    conclusions: string[], 
    insights: string[], 
    uncertainties: string[]
  ): string {
    let narrative = '';
    
    // Add a narrative introduction
    narrative += 'Based on the analysis of multiple reasoning chains, the following key findings emerge:\n\n';
    
    // Add conclusions
    if (conclusions.length > 0) {
      narrative += '**Key Conclusions:**\n';
      conclusions.forEach((conclusion, index) => {
        narrative += `${index + 1}. ${conclusion}\n`;
      });
      narrative += '\n';
    }
    
    // Add insights
    if (insights.length > 0) {
      narrative += '**Supporting Insights:**\n';
      insights.slice(0, 5).forEach((insight, index) => {
        narrative += `- ${insight}\n`;
      });
      narrative += '\n';
    }
    
    // Add uncertainties
    if (uncertainties.length > 0) {
      narrative += '**Areas of Uncertainty:**\n';
      uncertainties.slice(0, 3).forEach((uncertainty, index) => {
        narrative += `- ${uncertainty}\n`;
      });
      narrative += '\n';
    }
    
    // Add final synthesis
    narrative += 'These findings suggest a nuanced understanding of the economic situation, where multiple factors interact in complex ways. The analysis reveals both areas of confidence and uncertainty, with further investigation recommended for the latter.';
    
    return narrative;
  }
  
  /**
   * Generates a text summary of a reasoning chain.
   * 
   * @param chain The reasoning chain to summarize
   * @returns A text summary of the chain
   */
  private generateTextSummary(chain: ReasoningChain): string {
    let summary = `# Reasoning Chain: ${chain.name}\n\n`;
    summary += `${chain.description}\n\n`;
    
    summary += `- Domain: ${chain.metadata.domain}\n`;
    summary += `- Created: ${chain.metadata.created}\n`;
    summary += `- Last Updated: ${chain.metadata.lastUpdated}\n`;
    summary += `- Overall Confidence: ${(chain.metadata.overallConfidence * 100).toFixed(0)}%\n`;
    summary += `- Completeness: ${(chain.metadata.completeness * 100).toFixed(0)}%\n`;
    summary += `- Coherence: ${(chain.metadata.coherence * 100).toFixed(0)}%\n\n`;
    
    summary += '## Steps\n\n';
    chain.steps.forEach((step, index) => {
      summary += `### Step ${index + 1}: ${step.type} (${(step.confidence * 100).toFixed(0)}% confidence)\n`;
      summary += `${step.content}\n`;
      summary += `Source: ${step.source}\n\n`;
    });
    
    if (chain.issues.length > 0) {
      summary += '## Potential Issues\n\n';
      chain.issues.forEach((issue, index) => {
        summary += `### Issue ${index + 1}: ${issue.type} (${issue.severity} severity)\n`;
        summary += `${issue.description}\n`;
        summary += `Affected Steps: ${issue.affectedStepIds.map(id => {
          const stepIndex = chain.steps.findIndex(step => step.id === id);
          return stepIndex !== -1 ? stepIndex + 1 : 'unknown';
        }).join(', ')}\n`;
        
        if (issue.suggestedResolution) {
          summary += `Suggested Resolution: ${issue.suggestedResolution}\n`;
        }
        
        summary += '\n';
      });
    }
    
    return summary;
  }
  
  /**
   * Generates a Mermaid diagram of a reasoning chain.
   * 
   * @param chain The reasoning chain to visualize
   * @returns A Mermaid diagram
   */
  private generateMermaidDiagram(chain: ReasoningChain): string {
    let diagram = 'graph TD;\n';
    
    // Add nodes
    chain.steps.forEach(step => {
      const nodeShape = this.getNodeShape(step.type);
      const confidenceColor = this.getConfidenceColor(step.confidence);
      const stepIndex = chain.steps.indexOf(step) + 1;
      
      diagram += `  ${step.id}${nodeShape}["Step ${stepIndex}: ${step.type}<br/><span style='color:${confidenceColor}'>Confidence: ${(step.confidence * 100).toFixed(0)}%</span>"];\n`;
    });
    
    // Add connections
    chain.connections.forEach(conn => {
      const linkStyle = this.getLinkStyle(conn.type);
      const linkStrength = Math.max(1, Math.min(5, Math.round(conn.strength * 5)));
      
      diagram += `  ${conn.fromStepId} ${linkStyle}|"${conn.type}"| ${conn.toStepId};\n`;
      diagram += `  linkStyle ${chain.connections.indexOf(conn)} stroke-width:${linkStrength}px;\n`;
    });
    
    // Add issues if any
    if (chain.issues.length > 0) {
      diagram += '\n  subgraph Issues\n';
      
      chain.issues.forEach(issue => {
        const issueId = `issue_${issue.id}`;
        const issueColor = this.getIssueSeverityColor(issue.severity);
        
        diagram += `    ${issueId}["⚠️ ${issue.type}<br/><span style='color:${issueColor}'>${issue.severity}</span>"];\n`;
        
        // Connect issues to affected steps
        issue.affectedStepIds.forEach(stepId => {
          diagram += `    ${issueId} -.-> ${stepId};\n`;
        });
      });
      
      diagram += '  end\n';
    }
    
    return diagram;
  }
  
  /**
   * Gets the node shape for a reasoning step type.
   * 
   * @param type The reasoning step type
   * @returns The Mermaid node shape
   */
  private getNodeShape(type: ReasoningStepType): string {
    switch (type) {
      case ReasoningStepType.Premise:
        return '[()]'; // Circle
      case ReasoningStepType.Inference:
        return ''; // Default rectangle
      case ReasoningStepType.Hypothesis:
        return '{';  // Hexagon
      case ReasoningStepType.Evidence:
        return '[(]'; // Database
      case ReasoningStepType.Counterargument:
        return '{{';  // Hexagon
      case ReasoningStepType.Conclusion:
        return '[/]';  // Parallelogram
      case ReasoningStepType.Alternative:
        return '[\\]';  // Trapezoid
      case ReasoningStepType.Rebuttal:
        return '>';  // Double circle
      default:
        return '';  // Default rectangle
    }
  }
  
  /**
   * Gets the link style for a connection type.
   * 
   * @param type The connection type
   * @returns The Mermaid link style
   */
  private getLinkStyle(type: ConnectionType): string {
    switch (type) {
      case ConnectionType.Supports:
        return ' ===> ';
      case ConnectionType.Contradicts:
        return ' -. x .->';
      case ConnectionType.Elaborates:
        return ' --> ';
      case ConnectionType.Implies:
        return ' ==> ';
      case ConnectionType.Precedes:
        return ' --> ';
      case ConnectionType.Alternatives:
        return ' -.-> ';
      default:
        return ' --> ';
    }
  }
  
  /**
   * Gets a color based on confidence level.
   * 
   * @param confidence The confidence value (0-1)
   * @returns A color hex code
   */
  private getConfidenceColor(confidence: number): string {
    if (confidence >= 0.8) {
      return '#00aa00';  // Green
    } else if (confidence >= 0.6) {
      return '#aaaa00';  // Yellow
    } else {
      return '#aa0000';  // Red
    }
  }
  
  /**
   * Gets a color based on issue severity.
   * 
   * @param severity The issue severity
   * @returns A color hex code
   */
  private getIssueSeverityColor(severity: string): string {
    switch (severity) {
      case 'high':
        return '#aa0000';  // Red
      case 'medium':
        return '#aaaa00';  // Yellow
      case 'low':
        return '#0000aa';  // Blue
      default:
        return '#000000';  // Black
    }
  }
  
  /**
   * Generates a unique ID with a specific prefix.
   * 
   * @param prefix The ID prefix
   * @returns A unique ID
   */
  private generateId(prefix: string): string {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}