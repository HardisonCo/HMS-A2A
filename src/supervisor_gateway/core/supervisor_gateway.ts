/**
 * Supervisor Gateway
 * 
 * The Supervisor Gateway is the central orchestration component that routes messages
 * between the frontend (messaging-v1.vue) and multiple subsystem-specific agents.
 * It integrates with Chain-of-Recursive-Thought (CoRT) for deep economic analysis
 * and coordinates complex multi-agent workflows.
 */

import { Message, MessageType, AgentType, AgentId } from '../communication/message';
import { AgentRegistry } from './agent_registry';
import { CoRTEngine, CoRTAnalysisResult } from '../cort/cort_engine';
import { EvaluationEngine } from '../cort/evaluation_engine';
import { ReasoningTracer } from '../cort/reasoning_tracer';
import { EconomicAnalysisCore } from '../economic/economic_analysis_core';

export class SupervisorGateway {
  private agentRegistry: AgentRegistry;
  private cortEngine: CoRTEngine;
  private economicAnalysisCore: EconomicAnalysisCore;
  
  constructor(
    agentRegistry: AgentRegistry,
    cortEngine: CoRTEngine,
    economicAnalysisCore: EconomicAnalysisCore
  ) {
    this.agentRegistry = agentRegistry;
    this.cortEngine = cortEngine;
    this.economicAnalysisCore = economicAnalysisCore;
  }
  
  /**
   * Initializes the Supervisor Gateway and all registered agents.
   */
  async initialize(): Promise<void> {
    console.log('Initializing Supervisor Gateway...');
    
    // Initialize all registered agents
    const agents = this.agentRegistry.getAllAgents();
    for (const agent of agents) {
      await agent.initialize();
    }
    
    // Initialize CoRT Engine
    await this.cortEngine.initialize();
    
    // Initialize Economic Analysis Core
    await this.economicAnalysisCore.initialize();
    
    console.log('Supervisor Gateway initialized successfully');
  }
  
  /**
   * Routes a message from the frontend to the appropriate agent(s).
   * 
   * This is the main entry point for the Supervisor Gateway. It analyzes the
   * user message to determine intent and routes it to the appropriate agent(s).
   * For economic queries, it uses the CoRT Engine to perform deep analysis.
   * 
   * @param userMessage The message from the user via the frontend
   * @returns A response message to send back to the frontend
   */
  async routeMessage(userMessage: string): Promise<Message> {
    console.log(`Routing message: ${userMessage.substring(0, 50)}...`);
    
    // Analyze message intent to determine target agents
    const intent = await this.analyzeIntent(userMessage);
    const targetAgents = this.determineTargetAgents(intent);
    
    // For economic queries, use CoRT for deep analysis
    if (intent.domain === 'economic') {
      return this.handleEconomicQuery(userMessage, targetAgents);
    }
    
    // For multi-agent queries, orchestrate a workflow
    if (targetAgents.length > 1) {
      return this.orchestrateMultiAgentWorkflow(userMessage, targetAgents, intent);
    }
    
    // For single agent queries, route directly
    if (targetAgents.length === 1) {
      return this.routeToSingleAgent(userMessage, targetAgents[0]);
    }
    
    // If no agents were determined, handle with default response
    return this.handleUnknownIntent(userMessage);
  }
  
  /**
   * Analyzes the intent of a user message to determine domain, tasks, and entities.
   * 
   * @param userMessage The message from the user
   * @returns Intent analysis with domain, tasks, and entities
   */
  private async analyzeIntent(userMessage: string): Promise<any> {
    // TODO: Implement intent analysis using NLP or LLM
    // For now, return a simple mock intent
    
    // Check for economic keywords
    const economicKeywords = ['economy', 'inflation', 'tariff', 'stagflation', 'fiscal', 'monetary'];
    const hasEconomicTerms = economicKeywords.some(keyword => 
      userMessage.toLowerCase().includes(keyword)
    );
    
    if (hasEconomicTerms) {
      return {
        domain: 'economic',
        tasks: ['analyze'],
        entities: []
      };
    }
    
    // Check for government keywords
    const govKeywords = ['policy', 'legislation', 'law', 'regulation', 'government'];
    const hasGovTerms = govKeywords.some(keyword => 
      userMessage.toLowerCase().includes(keyword)
    );
    
    if (hasGovTerms) {
      return {
        domain: 'government',
        tasks: ['lookup'],
        entities: []
      };
    }
    
    // Check for health keywords
    const healthKeywords = ['health', 'medical', 'patient', 'doctor', 'hospital'];
    const hasHealthTerms = healthKeywords.some(keyword => 
      userMessage.toLowerCase().includes(keyword)
    );
    
    if (hasHealthTerms) {
      return {
        domain: 'health',
        tasks: ['lookup'],
        entities: []
      };
    }
    
    // Default to general domain
    return {
      domain: 'general',
      tasks: ['answer'],
      entities: []
    };
  }
  
  /**
   * Determines which agents should handle a message based on intent analysis.
   * 
   * @param intent The analyzed intent of the user message
   * @returns Array of agent IDs that should process the message
   */
  private determineTargetAgents(intent: any): AgentId[] {
    const targetAgents: AgentId[] = [];
    
    // Map intent domains to appropriate agents
    switch (intent.domain) {
      case 'economic':
        targetAgents.push({ id: 'economic-agent', type: AgentType.Economic });
        break;
        
      case 'government':
        targetAgents.push({ id: 'gov-policy-agent', type: AgentType.GovPolicy });
        targetAgents.push({ id: 'gov-ui-agent', type: AgentType.GovUI });
        break;
        
      case 'health':
        targetAgents.push({ id: 'ehr-agent', type: AgentType.EHR });
        break;
        
      default:
        // For unknown domains, consult the SME agent
        targetAgents.push({ id: 'sme-agent', type: AgentType.SME });
        break;
    }
    
    return targetAgents;
  }
  
  /**
   * Handles economic queries using the CoRT Engine for deep analysis.
   * 
   * @param query The user's economic query
   * @param agents The target agent IDs
   * @returns Response message with economic analysis
   */
  private async handleEconomicQuery(query: string, agents: AgentId[]): Promise<Message> {
    console.log('Handling economic query with CoRT...');

    // Use CoRT for deep economic analysis with evaluation and reasoning tracing
    const cortResult: CoRTAnalysisResult = await this.cortEngine.analyze(query);

    // Extract the most relevant information from evaluation
    let evaluationSummary = {};
    if (cortResult.evaluatedHypotheses && cortResult.evaluatedHypotheses.length > 0) {
      // Sort hypotheses by overall score
      const sortedHypotheses = [...cortResult.evaluatedHypotheses]
        .sort((a, b) => b.overall_score - a.overall_score);

      // Get the top hypothesis and its evaluations
      const topHypothesis = sortedHypotheses[0];

      evaluationSummary = {
        topHypothesis: topHypothesis.hypothesis.statement,
        topHypothesisScore: topHypothesis.overall_score,
        topHypothesisConfidence: topHypothesis.overall_confidence,
        recommendedRefinements: topHypothesis.recommended_refinements || [],
        criteriaEvaluations: topHypothesis.criterion_evaluations.map(ce => ({
          criterion: ce.criterion,
          score: ce.score
        }))
      };
    }

    // Get synthesis from reasoning if available
    let reasoningSynthesis = {};
    if (cortResult.synthesis) {
      reasoningSynthesis = {
        narrative: cortResult.synthesis.narrative,
        keyInsights: cortResult.synthesis.keyInsights,
        uncertaintyAreas: cortResult.synthesis.uncertaintyAreas,
        confidenceScore: cortResult.synthesis.confidenceScore
      };
    }

    // Create message with economic analysis metadata
    const message = new Message({
      messageType: MessageType.Query,
      sender: { id: 'supervisor', type: AgentType.Supervisor },
      recipients: agents,
      content: {
        queryType: 'economic_analysis',
        body: query,
        context: {
          evaluationSummary,
          reasoningSynthesis
        }
      },
      metadata: {
        requiresTheoremProving: true,
        economicIndicators: cortResult.indicators,
        cortDepth: cortResult.depth,
        reasoningQuality: cortResult.reasoningQuality,
        uncertainty: cortResult.uncertainty
      }
    });

    // Dispatch to economic agent
    const economicAgent = this.agentRegistry.getAgentById(agents[0].id);
    if (!economicAgent) {
      throw new Error(`Agent not found: ${agents[0].id}`);
    }

    const response = await economicAgent.processMessage(message);

    // Enhance response with additional economic analysis
    const enhancedResponse = await this.economicAnalysisCore.enhanceResponse(response, cortResult);

    return enhancedResponse;
  }
  
  /**
   * Orchestrates a workflow involving multiple agents.
   * 
   * @param query The user's query
   * @param agents The target agent IDs
   * @param intent The analyzed intent
   * @returns Aggregated response from multiple agents
   */
  private async orchestrateMultiAgentWorkflow(
    query: string, 
    agents: AgentId[], 
    intent: any
  ): Promise<Message> {
    console.log(`Orchestrating multi-agent workflow with ${agents.length} agents...`);
    
    // Create a base message
    const baseMessage = new Message({
      messageType: MessageType.Query,
      sender: { id: 'supervisor', type: AgentType.Supervisor },
      recipients: agents,
      content: {
        queryType: intent.tasks[0],
        body: query,
        context: {}
      }
    });
    
    // Process message with each agent in sequence
    // In a real implementation, this could be more sophisticated with parallel processing
    // and dependency management between agents
    let currentMessage = baseMessage;
    let finalResponse: Message | null = null;
    
    for (const agentId of agents) {
      const agent = this.agentRegistry.getAgentById(agentId.id);
      if (!agent) {
        console.warn(`Agent not found: ${agentId.id}`);
        continue;
      }
      
      // Update recipients to only the current agent
      currentMessage.recipients = [agentId];
      
      // Process with current agent
      const response = await agent.processMessage(currentMessage);
      
      // Update message for next agent
      currentMessage = new Message({
        ...response,
        sender: { id: 'supervisor', type: AgentType.Supervisor },
        recipients: [agentId]
      });
      
      // Store the final response
      finalResponse = response;
    }
    
    if (!finalResponse) {
      return this.handleUnknownIntent(query);
    }
    
    // Create an aggregated response
    return finalResponse;
  }
  
  /**
   * Routes a message to a single agent.
   * 
   * @param query The user's query
   * @param agentId The target agent ID
   * @returns Response from the agent
   */
  private async routeToSingleAgent(query: string, agentId: AgentId): Promise<Message> {
    console.log(`Routing to single agent: ${agentId.id}`);
    
    const agent = this.agentRegistry.getAgentById(agentId.id);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId.id}`);
    }
    
    // Create message for the agent
    const message = new Message({
      messageType: MessageType.Query,
      sender: { id: 'supervisor', type: AgentType.Supervisor },
      recipients: [agentId],
      content: {
        queryType: 'query',
        body: query,
        context: {}
      }
    });
    
    // Process with agent
    return await agent.processMessage(message);
  }
  
  /**
   * Handles messages with unknown intent.
   * 
   * @param query The user's query
   * @returns Default response for unknown intents
   */
  private handleUnknownIntent(query: string): Message {
    console.log('Handling unknown intent');
    
    // Create a default response
    return new Message({
      messageType: MessageType.Response,
      sender: { id: 'supervisor', type: AgentType.Supervisor },
      recipients: [{ id: 'frontend', type: AgentType.Frontend }],
      content: {
        body: "I'm not sure how to process this request. Could you provide more details or clarify your question?",
        context: {}
      }
    });
  }
}