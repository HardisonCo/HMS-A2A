/**
 * Base Agent Implementation
 * 
 * Provides a common base implementation for all agents in the system.
 * Specialized agents can extend this class to inherit common functionality.
 */

import { Agent } from './agent_interface';
import { 
  Message, 
  MessageType, 
  AgentId, 
  ProcessingStatus, 
  Priority 
} from '../communication/message';
import { KnowledgeQuery, KnowledgeResult } from '../knowledge/knowledge_types';
import { Tool, ToolParameters, ToolResponse } from '../tools/tool_types';
import { HealthStatus, HealthState } from '../monitoring/health_types';
import { KnowledgeBaseManager } from '../knowledge/knowledge_base_manager';

/**
 * Base Agent class that implements the Agent interface.
 * Provides common functionality for all agents.
 */
export abstract class BaseAgent implements Agent {
  protected id: AgentId;
  protected tools: Map<string, Tool>;
  protected knowledgeBaseManager: KnowledgeBaseManager;
  protected isInitialized: boolean;
  protected isStarted: boolean;
  
  /**
   * Creates a new BaseAgent instance.
   * 
   * @param id The agent's unique identifier
   * @param knowledgeBaseManager The knowledge base manager to use
   */
  constructor(id: AgentId, knowledgeBaseManager: KnowledgeBaseManager) {
    this.id = id;
    this.tools = new Map<string, Tool>();
    this.knowledgeBaseManager = knowledgeBaseManager;
    this.isInitialized = false;
    this.isStarted = false;
  }
  
  /**
   * Gets the unique identifier for this agent.
   * 
   * @returns The agent ID object
   */
  getId(): AgentId {
    return this.id;
  }
  
  /**
   * Initializes the agent.
   * This is called once when the agent is first registered.
   * 
   * @returns A promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      console.log(`Agent ${this.id.id} is already initialized`);
      return;
    }
    
    console.log(`Initializing agent: ${this.id.id} (${this.id.type})`);
    
    // Load the appropriate knowledge base for this agent type
    await this.knowledgeBaseManager.loadKnowledgeBase(this.id.type);
    
    // Initialize any agent-specific resources
    await this.initializeResources();
    
    this.isInitialized = true;
    console.log(`Agent ${this.id.id} initialized successfully`);
  }
  
  /**
   * Initializes agent-specific resources.
   * Subclasses should override this method to perform specialized initialization.
   * 
   * @returns A promise that resolves when initialization is complete
   */
  protected async initializeResources(): Promise<void> {
    // Default implementation does nothing
    // Subclasses should override this method
  }
  
  /**
   * Processes a message sent to this agent.
   * 
   * @param message The message to process
   * @returns A promise that resolves to the response message
   */
  async processMessage(message: Message): Promise<Message> {
    // Ensure agent is initialized
    if (!this.isInitialized) {
      return message.createErrorResponse({
        code: 'AGENT_NOT_INITIALIZED',
        message: `Agent ${this.id.id} is not initialized`
      });
    }
    
    // Update message status to processing
    let response = message.withStatus(ProcessingStatus.Processing);
    
    try {
      // Process based on message type
      switch (message.messageType) {
        case MessageType.Query:
          response = await this.processQuery(message);
          break;
          
        case MessageType.ToolCall:
          response = await this.processToolCall(message);
          break;
          
        case MessageType.Broadcast:
          response = await this.processBroadcast(message);
          break;
          
        case MessageType.Event:
          response = await this.processEvent(message);
          break;
          
        default:
          return message.createErrorResponse({
            code: 'UNSUPPORTED_MESSAGE_TYPE',
            message: `Unsupported message type: ${message.messageType}`
          });
      }
      
      // Update message status to completed
      return response.withStatus(ProcessingStatus.Completed);
      
    } catch (error) {
      console.error(`Error processing message in agent ${this.id.id}:`, error);
      
      // Create error response
      return message.createErrorResponse({
        code: 'PROCESSING_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
        details: { error: error instanceof Error ? error.stack : String(error) }
      });
    }
  }
  
  /**
   * Processes a query message.
   * Subclasses should override this method to provide agent-specific query handling.
   * 
   * @param message The query message to process
   * @returns A promise that resolves to the response message
   */
  protected async processQuery(message: Message): Promise<Message> {
    // Default implementation returns a basic response
    // Subclasses should override this method
    return message.createResponse({
      body: `Default response from ${this.id.id}`,
      context: {}
    });
  }
  
  /**
   * Processes a tool call message.
   * 
   * @param message The tool call message to process
   * @returns A promise that resolves to the response message
   */
  protected async processToolCall(message: Message): Promise<Message> {
    // Extract tool call details
    const toolCall = message.content.tools?.[0];
    if (!toolCall) {
      return message.createErrorResponse({
        code: 'MISSING_TOOL_CALL',
        message: 'Tool call message contains no tool details'
      });
    }
    
    // Check if tool exists
    if (!this.tools.has(toolCall.tool_id)) {
      return message.createErrorResponse({
        code: 'UNKNOWN_TOOL',
        message: `Tool ${toolCall.tool_id} is not registered with agent ${this.id.id}`
      });
    }
    
    try {
      // Invoke the tool
      const tool = this.tools.get(toolCall.tool_id)!;
      const result = await tool.execute(toolCall.parameters);
      
      // Create response with tool result
      return message.createResponse({
        body: result,
        context: {
          tool_id: toolCall.tool_id,
          tool_name: toolCall.tool_name
        }
      });
      
    } catch (error) {
      return message.createErrorResponse({
        code: 'TOOL_EXECUTION_ERROR',
        message: error instanceof Error ? error.message : 'Tool execution failed',
        details: { tool_id: toolCall.tool_id }
      });
    }
  }
  
  /**
   * Processes a broadcast message.
   * 
   * @param message The broadcast message to process
   * @returns A promise that resolves to the response message
   */
  protected async processBroadcast(message: Message): Promise<Message> {
    // Default implementation acknowledges the broadcast
    // Subclasses can override to provide specialized handling
    return message.createResponse({
      body: `Broadcast received by ${this.id.id}`,
      context: {}
    });
  }
  
  /**
   * Processes an event message.
   * 
   * @param message The event message to process
   * @returns A promise that resolves to the response message
   */
  protected async processEvent(message: Message): Promise<Message> {
    // Default implementation acknowledges the event
    // Subclasses can override to provide specialized handling
    return message.createResponse({
      body: `Event processed by ${this.id.id}`,
      context: {}
    });
  }
  
  /**
   * Registers a tool with this agent.
   * 
   * @param tool The tool to register
   */
  registerTool(tool: Tool): void {
    if (this.tools.has(tool.getId())) {
      console.warn(`Tool ${tool.getId()} is already registered with agent ${this.id.id}`);
      return;
    }
    
    this.tools.set(tool.getId(), tool);
    console.log(`Tool ${tool.getId()} registered with agent ${this.id.id}`);
  }
  
  /**
   * Invokes a tool that this agent has registered.
   * 
   * @param toolId The ID of the tool to invoke
   * @param params The parameters to pass to the tool
   * @returns A promise that resolves to the tool response
   */
  async invokeTool(toolId: string, params: ToolParameters): Promise<ToolResponse> {
    // Check if tool exists
    if (!this.tools.has(toolId)) {
      throw new Error(`Tool ${toolId} is not registered with agent ${this.id.id}`);
    }
    
    // Invoke the tool
    const tool = this.tools.get(toolId)!;
    return await tool.execute(params);
  }
  
  /**
   * Queries the agent's knowledge base.
   * 
   * @param query The knowledge query
   * @returns A promise that resolves to the query result
   */
  async queryKnowledge(query: KnowledgeQuery): Promise<KnowledgeResult> {
    return await this.knowledgeBaseManager.queryKnowledgeBase(this.id.type, query);
  }
  
  /**
   * Updates the agent's knowledge base.
   * 
   * @param update The knowledge update
   * @returns A promise that resolves when the update is complete
   */
  async updateKnowledge(update: any): Promise<void> {
    await this.knowledgeBaseManager.updateKnowledgeBase(this.id.type, update);
  }
  
  /**
   * Starts the agent.
   * This is called when the system is starting up.
   * 
   * @returns A promise that resolves when startup is complete
   */
  async start(): Promise<void> {
    if (!this.isInitialized) {
      throw new Error(`Agent ${this.id.id} must be initialized before starting`);
    }
    
    if (this.isStarted) {
      console.log(`Agent ${this.id.id} is already started`);
      return;
    }
    
    console.log(`Starting agent: ${this.id.id}`);
    
    // Start any agent-specific services
    await this.startServices();
    
    this.isStarted = true;
    console.log(`Agent ${this.id.id} started successfully`);
  }
  
  /**
   * Starts agent-specific services.
   * Subclasses should override this method to start specialized services.
   * 
   * @returns A promise that resolves when startup is complete
   */
  protected async startServices(): Promise<void> {
    // Default implementation does nothing
    // Subclasses should override this method
  }
  
  /**
   * Stops the agent.
   * This is called when the system is shutting down.
   * 
   * @returns A promise that resolves when shutdown is complete
   */
  async stop(): Promise<void> {
    if (!this.isStarted) {
      console.log(`Agent ${this.id.id} is not started`);
      return;
    }
    
    console.log(`Stopping agent: ${this.id.id}`);
    
    // Stop any agent-specific services
    await this.stopServices();
    
    this.isStarted = false;
    console.log(`Agent ${this.id.id} stopped successfully`);
  }
  
  /**
   * Stops agent-specific services.
   * Subclasses should override this method to stop specialized services.
   * 
   * @returns A promise that resolves when shutdown is complete
   */
  protected async stopServices(): Promise<void> {
    // Default implementation does nothing
    // Subclasses should override this method
  }
  
  /**
   * Performs a health check on the agent.
   * This is used for monitoring and self-healing.
   * 
   * @returns A promise that resolves to the agent's health status
   */
  async healthCheck(): Promise<HealthStatus> {
    // Basic health check includes initialization and startup status
    const healthState = this.isInitialized && this.isStarted 
      ? HealthState.Healthy 
      : HealthState.Unhealthy;
    
    const details = {
      initialized: this.isInitialized,
      started: this.isStarted,
      toolCount: this.tools.size
    };
    
    // Allow subclasses to add agent-specific health checks
    const additionalChecks = await this.performAdditionalHealthChecks();
    
    return {
      agentId: this.id,
      state: this.determineOverallHealth(healthState, additionalChecks),
      timestamp: new Date().toISOString(),
      details: {
        ...details,
        ...additionalChecks
      }
    };
  }
  
  /**
   * Performs additional agent-specific health checks.
   * Subclasses should override this method to provide specialized health checks.
   * 
   * @returns A promise that resolves to additional health check details
   */
  protected async performAdditionalHealthChecks(): Promise<Record<string, any>> {
    // Default implementation returns no additional checks
    // Subclasses should override this method
    return {};
  }
  
  /**
   * Determines the overall health state based on base checks and additional checks.
   * 
   * @param baseState The base health state
   * @param additionalChecks Additional health check details
   * @returns The overall health state
   */
  private determineOverallHealth(
    baseState: HealthState,
    additionalChecks: Record<string, any>
  ): HealthState {
    // If base state is already unhealthy, overall state is unhealthy
    if (baseState !== HealthState.Healthy) {
      return baseState;
    }
    
    // Check if any additional check indicates unhealthy state
    const hasUnhealthyCheck = Object.values(additionalChecks).some(value => {
      if (typeof value === 'object' && value !== null && 'state' in value) {
        return value.state === HealthState.Unhealthy;
      }
      return false;
    });
    
    return hasUnhealthyCheck ? HealthState.Unhealthy : HealthState.Healthy;
  }
}