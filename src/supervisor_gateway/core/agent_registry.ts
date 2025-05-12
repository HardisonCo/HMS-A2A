/**
 * Agent Registry
 * 
 * The Agent Registry maintains a collection of all agents in the system
 * and provides methods for registering, retrieving, and managing agents.
 */

import { AgentId, AgentType } from '../communication/message';
import { Agent } from '../agents/agent_interface';

export class AgentRegistry {
  private agents: Map<string, Agent>;
  
  constructor() {
    this.agents = new Map<string, Agent>();
  }
  
  /**
   * Registers a new agent in the registry.
   * 
   * @param agent The agent to register
   * @returns True if registration was successful, false if agent ID already exists
   */
  registerAgent(agent: Agent): boolean {
    const agentId = agent.getId().id;
    
    // Check if agent already exists
    if (this.agents.has(agentId)) {
      console.warn(`Agent with ID ${agentId} already exists in registry`);
      return false;
    }
    
    // Register the agent
    this.agents.set(agentId, agent);
    console.log(`Agent registered: ${agentId} (${agent.getId().type})`);
    return true;
  }
  
  /**
   * Retrieves an agent by ID.
   * 
   * @param agentId The ID of the agent to retrieve
   * @returns The agent instance, or undefined if not found
   */
  getAgentById(agentId: string): Agent | undefined {
    return this.agents.get(agentId);
  }
  
  /**
   * Retrieves all agents of a specific type.
   * 
   * @param type The type of agents to retrieve
   * @returns Array of agents of the specified type
   */
  getAgentsByType(type: AgentType): Agent[] {
    const result: Agent[] = [];
    
    for (const agent of this.agents.values()) {
      if (agent.getId().type === type) {
        result.push(agent);
      }
    }
    
    return result;
  }
  
  /**
   * Retrieves all registered agents.
   * 
   * @returns Array of all registered agents
   */
  getAllAgents(): Agent[] {
    return Array.from(this.agents.values());
  }
  
  /**
   * Unregisters an agent from the registry.
   * 
   * @param agentId The ID of the agent to unregister
   * @returns True if unregistration was successful, false if agent was not found
   */
  unregisterAgent(agentId: string): boolean {
    if (!this.agents.has(agentId)) {
      console.warn(`Agent with ID ${agentId} not found in registry`);
      return false;
    }
    
    this.agents.delete(agentId);
    console.log(`Agent unregistered: ${agentId}`);
    return true;
  }
  
  /**
   * Checks if an agent with the specified ID exists.
   * 
   * @param agentId The ID to check
   * @returns True if an agent with this ID exists, false otherwise
   */
  hasAgent(agentId: string): boolean {
    return this.agents.has(agentId);
  }
  
  /**
   * Returns the number of registered agents.
   * 
   * @returns The number of registered agents
   */
  getAgentCount(): number {
    return this.agents.size;
  }
  
  /**
   * Clears all agents from the registry.
   */
  clear(): void {
    this.agents.clear();
    console.log('Agent registry cleared');
  }
}