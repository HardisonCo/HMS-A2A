/**
 * Agent Interface
 * 
 * Defines the common interface that all agents must implement.
 * This ensures that the Supervisor Gateway can interact with
 * any agent in a consistent manner.
 */

import { Message, AgentId } from '../communication/message';
import { KnowledgeQuery, KnowledgeResult } from '../knowledge/knowledge_types';
import { Tool, ToolParameters, ToolResponse } from '../tools/tool_types';
import { HealthStatus } from '../monitoring/health_types';

/**
 * Interface that all agents must implement.
 */
export interface Agent {
  /**
   * Gets the unique identifier for this agent.
   * 
   * @returns The agent ID object
   */
  getId(): AgentId;
  
  /**
   * Initializes the agent.
   * This is called once when the agent is first registered.
   * 
   * @returns A promise that resolves when initialization is complete
   */
  initialize(): Promise<void>;
  
  /**
   * Processes a message sent to this agent.
   * 
   * @param message The message to process
   * @returns A promise that resolves to the response message
   */
  processMessage(message: Message): Promise<Message>;
  
  /**
   * Registers a tool with this agent.
   * 
   * @param tool The tool to register
   */
  registerTool(tool: Tool): void;
  
  /**
   * Invokes a tool that this agent has registered.
   * 
   * @param toolId The ID of the tool to invoke
   * @param params The parameters to pass to the tool
   * @returns A promise that resolves to the tool response
   */
  invokeTool(toolId: string, params: ToolParameters): Promise<ToolResponse>;
  
  /**
   * Queries the agent's knowledge base.
   * 
   * @param query The knowledge query
   * @returns A promise that resolves to the query result
   */
  queryKnowledge(query: KnowledgeQuery): Promise<KnowledgeResult>;
  
  /**
   * Updates the agent's knowledge base.
   * 
   * @param update The knowledge update
   * @returns A promise that resolves when the update is complete
   */
  updateKnowledge(update: any): Promise<void>;
  
  /**
   * Starts the agent.
   * This is called when the system is starting up.
   * 
   * @returns A promise that resolves when startup is complete
   */
  start(): Promise<void>;
  
  /**
   * Stops the agent.
   * This is called when the system is shutting down.
   * 
   * @returns A promise that resolves when shutdown is complete
   */
  stop(): Promise<void>;
  
  /**
   * Performs a health check on the agent.
   * This is used for monitoring and self-healing.
   * 
   * @returns A promise that resolves to the agent's health status
   */
  healthCheck(): Promise<HealthStatus>;
}