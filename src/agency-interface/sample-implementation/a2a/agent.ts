/**
 * Agent Framework for Agent-to-Agent (A2A) Communication
 * 
 * This module provides the core agent framework for A2A communication,
 * including agent interfaces, base implementations, and agent lifecycle
 * management.
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { 
  Message, 
  MessageType, 
  MessagePriority,
  MessageBuilder,
  MessageValidator,
  createRequestMessage,
  createNotificationMessage
} from './message';

/**
 * Agent state
 */
export enum AgentState {
  INITIALIZING = 'INITIALIZING',
  READY = 'READY',
  BUSY = 'BUSY',
  PAUSED = 'PAUSED',
  STOPPING = 'STOPPING',
  STOPPED = 'STOPPED',
  ERROR = 'ERROR'
}

/**
 * Agent capability interface
 */
export interface Capability {
  id: string;
  name: string;
  description: string;
  version: string;
  handles: string[];
}

/**
 * Agent handler function
 */
export type MessageHandler = (message: Message) => Promise<Message | void>;

/**
 * Agent options
 */
export interface AgentOptions {
  id?: string;
  name: string;
  description?: string;
  capabilities?: Capability[];
  messageHandlers?: Record<MessageType, MessageHandler>;
  agentRegistry?: AgentRegistry;
}

/**
 * Agent interface
 */
export interface Agent {
  id: string;
  name: string;
  description?: string;
  state: AgentState;
  capabilities: Capability[];
  
  initialize(): Promise<void>;
  start(): Promise<void>;
  stop(): Promise<void>;
  pause(): Promise<void>;
  resume(): Promise<void>;
  
  sendMessage(message: Message): Promise<void>;
  receiveMessage(message: Message): Promise<Message | void>;
  
  registerCapability(capability: Capability): void;
  unregisterCapability(capabilityId: string): void;
  hasCapability(capabilityId: string): boolean;
  getCapabilities(): Capability[];
  
  on(event: string, listener: (...args: any[]) => void): void;
  off(event: string, listener: (...args: any[]) => void): void;
}

/**
 * Base agent implementation
 */
export class BaseAgent extends EventEmitter implements Agent {
  public id: string;
  public name: string;
  public description?: string;
  public state: AgentState = AgentState.INITIALIZING;
  public capabilities: Capability[] = [];
  
  private messageHandlers: Record<MessageType, MessageHandler> = {};
  private agentRegistry?: AgentRegistry;
  private messageQueue: Message[] = [];
  private processingMessage = false;

  constructor(options: AgentOptions) {
    super();
    
    this.id = options.id || uuidv4();
    this.name = options.name;
    this.description = options.description;
    this.agentRegistry = options.agentRegistry;
    
    // Register initial capabilities
    if (options.capabilities) {
      for (const capability of options.capabilities) {
        this.registerCapability(capability);
      }
    }
    
    // Register message handlers
    if (options.messageHandlers) {
      this.messageHandlers = { ...options.messageHandlers };
    }
    
    // Register default message handlers
    if (!this.messageHandlers[MessageType.DISCOVERY]) {
      this.messageHandlers[MessageType.DISCOVERY] = this.handleDiscovery.bind(this);
    }
    
    if (!this.messageHandlers[MessageType.HEARTBEAT]) {
      this.messageHandlers[MessageType.HEARTBEAT] = this.handleHeartbeat.bind(this);
    }
  }

  /**
   * Initialize the agent
   */
  public async initialize(): Promise<void> {
    this.emit('initializing');
    
    // Register with agent registry if available
    if (this.agentRegistry) {
      await this.agentRegistry.registerAgent(this);
    }
    
    this.setState(AgentState.READY);
    this.emit('initialized');
  }

  /**
   * Start the agent
   */
  public async start(): Promise<void> {
    if (this.state === AgentState.INITIALIZING) {
      await this.initialize();
    }
    
    this.emit('starting');
    this.setState(AgentState.READY);
    this.emit('started');
    
    // Process any queued messages
    this.processMessageQueue();
  }

  /**
   * Stop the agent
   */
  public async stop(): Promise<void> {
    this.emit('stopping');
    this.setState(AgentState.STOPPING);
    
    // Unregister from agent registry if available
    if (this.agentRegistry) {
      await this.agentRegistry.unregisterAgent(this.id);
    }
    
    this.setState(AgentState.STOPPED);
    this.emit('stopped');
  }

  /**
   * Pause the agent
   */
  public async pause(): Promise<void> {
    if (this.state === AgentState.READY || this.state === AgentState.BUSY) {
      this.emit('pausing');
      this.setState(AgentState.PAUSED);
      this.emit('paused');
    }
  }

  /**
   * Resume the agent
   */
  public async resume(): Promise<void> {
    if (this.state === AgentState.PAUSED) {
      this.emit('resuming');
      this.setState(AgentState.READY);
      this.emit('resumed');
      
      // Process any queued messages
      this.processMessageQueue();
    }
  }

  /**
   * Send a message
   */
  public async sendMessage(message: Message): Promise<void> {
    if (this.state === AgentState.STOPPED || this.state === AgentState.STOPPING) {
      throw new Error(`Agent ${this.id} is stopped and cannot send messages`);
    }
    
    // Validate the message
    const validationResult = MessageValidator.validate(message);
    if (!validationResult.valid) {
      throw new Error(`Invalid message: ${validationResult.errors.join(', ')}`);
    }
    
    this.emit('messageSending', message);
    
    // Use agent registry to deliver the message if available
    if (this.agentRegistry) {
      await this.agentRegistry.routeMessage(message);
    } else {
      // If no registry, see if the recipient is this agent
      if (message.recipient === this.id) {
        await this.receiveMessage(message);
      } else {
        throw new Error(`No agent registry available to route message to ${message.recipient}`);
      }
    }
    
    this.emit('messageSent', message);
  }

  /**
   * Receive a message
   */
  public async receiveMessage(message: Message): Promise<Message | void> {
    if (this.state === AgentState.STOPPED || this.state === AgentState.STOPPING) {
      throw new Error(`Agent ${this.id} is stopped and cannot receive messages`);
    }
    
    // Validate the message
    const validationResult = MessageValidator.validate(message);
    if (!validationResult.valid) {
      throw new Error(`Invalid message: ${validationResult.errors.join(', ')}`);
    }
    
    this.emit('messageReceived', message);
    
    // If the agent is paused or busy, queue the message
    if (this.state === AgentState.PAUSED || (this.state === AgentState.BUSY && this.processingMessage)) {
      this.messageQueue.push(message);
      return;
    }
    
    // Process the message
    return await this.processMessage(message);
  }

  /**
   * Process a message
   */
  private async processMessage(message: Message): Promise<Message | void> {
    this.processingMessage = true;
    this.setState(AgentState.BUSY);
    
    try {
      // Find the appropriate handler
      const handler = this.messageHandlers[message.type];
      
      if (!handler) {
        this.emit('messageUnhandled', message);
        
        // Return an error message if no handler found
        const errorResponse = MessageBuilder.createErrorResponse(
          message,
          `No handler found for message type: ${message.type}`
        );
        
        return errorResponse;
      }
      
      // Handle the message
      this.emit('messageProcessing', message);
      const response = await handler(message);
      this.emit('messageProcessed', message, response);
      
      return response;
    } catch (error) {
      this.emit('messageError', message, error);
      
      // Return an error message
      return MessageBuilder.createErrorResponse(
        message,
        error as Error
      );
    } finally {
      this.processingMessage = false;
      
      // If there are queued messages and the agent is ready, process the next one
      if (this.state !== AgentState.PAUSED && this.state !== AgentState.STOPPED && this.state !== AgentState.STOPPING) {
        this.setState(AgentState.READY);
        this.processMessageQueue();
      }
    }
  }

  /**
   * Process the message queue
   */
  private async processMessageQueue(): Promise<void> {
    if (this.state !== AgentState.READY || this.processingMessage || this.messageQueue.length === 0) {
      return;
    }
    
    const message = this.messageQueue.shift();
    if (message) {
      await this.processMessage(message);
    }
  }

  /**
   * Set the agent state
   */
  private setState(state: AgentState): void {
    const oldState = this.state;
    this.state = state;
    this.emit('stateChanged', oldState, state);
  }

  /**
   * Register a capability
   */
  public registerCapability(capability: Capability): void {
    // Check if capability already exists
    const existingIndex = this.capabilities.findIndex(c => c.id === capability.id);
    
    if (existingIndex >= 0) {
      // Replace existing capability
      this.capabilities[existingIndex] = capability;
    } else {
      // Add new capability
      this.capabilities.push(capability);
    }
    
    this.emit('capabilityRegistered', capability);
  }

  /**
   * Unregister a capability
   */
  public unregisterCapability(capabilityId: string): void {
    const index = this.capabilities.findIndex(c => c.id === capabilityId);
    
    if (index >= 0) {
      const capability = this.capabilities[index];
      this.capabilities.splice(index, 1);
      this.emit('capabilityUnregistered', capability);
    }
  }

  /**
   * Check if agent has a capability
   */
  public hasCapability(capabilityId: string): boolean {
    return this.capabilities.some(c => c.id === capabilityId);
  }

  /**
   * Get all capabilities
   */
  public getCapabilities(): Capability[] {
    return [...this.capabilities];
  }

  /**
   * Handle discovery messages
   */
  private async handleDiscovery(message: Message): Promise<Message> {
    const content = message.content || {};
    
    // Prepare response
    const responseContent = {
      agent: {
        id: this.id,
        name: this.name,
        description: this.description,
        state: this.state
      },
      capabilities: content.requestCapabilities ? this.getCapabilities() : undefined
    };
    
    // Create response message
    return MessageBuilder.createResponse(message, responseContent);
  }

  /**
   * Handle heartbeat messages
   */
  private async handleHeartbeat(message: Message): Promise<Message> {
    // Create heartbeat response
    return MessageBuilder.createResponse(message, {
      timestamp: Date.now(),
      state: this.state
    });
  }

  /**
   * Create a request message from this agent
   */
  public createRequest(
    recipientId: string,
    subject: string,
    content: any,
    options: {
      priority?: MessagePriority;
      ttl?: number;
      replyTo?: string;
      metadata?: Record<string, any>;
    } = {}
  ): Message {
    return createRequestMessage(
      this.id,
      recipientId,
      subject,
      content,
      options
    );
  }

  /**
   * Create a notification message from this agent
   */
  public createNotification(
    recipientId: string,
    subject: string,
    content: any,
    options: {
      priority?: MessagePriority;
      ttl?: number;
      metadata?: Record<string, any>;
    } = {}
  ): Message {
    return createNotificationMessage(
      this.id,
      recipientId,
      subject,
      content,
      options
    );
  }
}

/**
 * Agent registry interface
 */
export interface AgentRegistry {
  registerAgent(agent: Agent): Promise<void>;
  unregisterAgent(agentId: string): Promise<void>;
  getAgent(agentId: string): Promise<Agent | null>;
  findAgents(filter?: (agent: Agent) => boolean): Promise<Agent[]>;
  routeMessage(message: Message): Promise<void>;
}

/**
 * In-memory agent registry
 */
export class InMemoryAgentRegistry implements AgentRegistry {
  private agents: Map<string, Agent> = new Map();
  private eventEmitter = new EventEmitter();
  
  /**
   * Register an agent
   */
  public async registerAgent(agent: Agent): Promise<void> {
    if (this.agents.has(agent.id)) {
      throw new Error(`Agent with ID ${agent.id} is already registered`);
    }
    
    this.agents.set(agent.id, agent);
    this.eventEmitter.emit('agentRegistered', agent);
  }
  
  /**
   * Unregister an agent
   */
  public async unregisterAgent(agentId: string): Promise<void> {
    const agent = this.agents.get(agentId);
    
    if (agent) {
      this.agents.delete(agentId);
      this.eventEmitter.emit('agentUnregistered', agent);
    }
  }
  
  /**
   * Get an agent by ID
   */
  public async getAgent(agentId: string): Promise<Agent | null> {
    return this.agents.get(agentId) || null;
  }
  
  /**
   * Find agents matching a filter
   */
  public async findAgents(filter?: (agent: Agent) => boolean): Promise<Agent[]> {
    const agents = Array.from(this.agents.values());
    
    if (filter) {
      return agents.filter(filter);
    }
    
    return agents;
  }
  
  /**
   * Route a message to its recipient
   */
  public async routeMessage(message: Message): Promise<void> {
    // Check if the recipient is a broadcast
    if (message.recipient === '*') {
      // Send to all agents except the sender
      const agents = Array.from(this.agents.values())
        .filter(agent => agent.id !== message.sender);
      
      for (const agent of agents) {
        try {
          await agent.receiveMessage(message);
        } catch (error) {
          // Log the error but continue with other agents
          console.error(`Error delivering message to agent ${agent.id}:`, error);
        }
      }
      
      return;
    }
    
    // Find the recipient agent
    const recipientAgent = this.agents.get(message.recipient);
    
    if (!recipientAgent) {
      throw new Error(`Recipient agent ${message.recipient} not found`);
    }
    
    // Deliver the message
    await recipientAgent.receiveMessage(message);
  }
  
  /**
   * Subscribe to events
   */
  public on(event: string, listener: (...args: any[]) => void): void {
    this.eventEmitter.on(event, listener);
  }
  
  /**
   * Unsubscribe from events
   */
  public off(event: string, listener: (...args: any[]) => void): void {
    this.eventEmitter.off(event, listener);
  }
}

/**
 * Create an agent
 */
export function createAgent(options: AgentOptions): Agent {
  return new BaseAgent(options);
}

/**
 * Create a capability
 */
export function createCapability(
  id: string,
  name: string,
  description: string,
  version: string,
  handles: string[]
): Capability {
  return {
    id,
    name,
    description,
    version,
    handles
  };
}

/**
 * Create a simple agent registry
 */
export function createAgentRegistry(): AgentRegistry {
  return new InMemoryAgentRegistry();
}