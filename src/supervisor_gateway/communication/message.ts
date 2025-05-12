/**
 * Message Protocol
 * 
 * Defines the standardized communication protocol between the Supervisor Gateway
 * and subsystem agents. This implements the protocol specified in the
 * implementation plan.
 */

import { v4 as uuidv4 } from 'uuid';

/**
 * Enumeration of message types supported by the protocol.
 */
export enum MessageType {
  Query = 'query',
  Response = 'response',
  Broadcast = 'broadcast',
  Event = 'event',
  ToolCall = 'tool_call',
  ToolResponse = 'tool_response'
}

/**
 * Enumeration of agent types in the system.
 */
export enum AgentType {
  Supervisor = 'supervisor',
  GovPolicy = 'gov_policy',
  GovUI = 'gov_ui',
  EHR = 'ehr',
  ESR = 'esr',
  SME = 'sme',
  Civ = 'civ',
  Economic = 'economic',
  Frontend = 'frontend'
}

/**
 * Enumeration of message priority levels.
 */
export enum Priority {
  High = 'high',
  Medium = 'medium',
  Low = 'low'
}

/**
 * Enumeration of processing status values.
 */
export enum ProcessingStatus {
  Received = 'received',
  Processing = 'processing',
  Completed = 'completed',
  Error = 'error'
}

/**
 * Interface for agent identification.
 */
export interface AgentId {
  id: string;
  type: AgentType;
}

/**
 * Interface for message tools.
 */
export interface Tool {
  tool_id: string;
  tool_name: string;
  parameters: Record<string, any>;
}

/**
 * Interface for message metadata.
 */
export interface MessageMetadata {
  conversation_id?: string;
  parent_message_id?: string;
  economic_indicators?: Record<string, any>;
  requires_theorem_proving?: boolean;
  cort_depth?: number;
  [key: string]: any;
}

/**
 * Interface for message content.
 */
export interface MessageContent {
  query_type?: string;
  body: string | Record<string, any>;
  context: Record<string, any>;
  tools?: Tool[];
}

/**
 * Interface for message error information.
 */
export interface MessageError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Interface for message state.
 */
export interface MessageState {
  processing_status: ProcessingStatus;
  error?: MessageError;
}

/**
 * Interface for message constructor options.
 */
export interface MessageOptions {
  messageId?: string;
  timestamp?: string;
  messageType: MessageType;
  sender: AgentId;
  recipients: AgentId[];
  priority?: Priority;
  content: MessageContent;
  metadata?: MessageMetadata;
  state?: MessageState;
}

/**
 * Message class representing a communication message between agents.
 */
export class Message {
  readonly messageId: string;
  readonly timestamp: string;
  readonly messageType: MessageType;
  readonly sender: AgentId;
  recipients: AgentId[];
  readonly priority: Priority;
  readonly content: MessageContent;
  readonly metadata: MessageMetadata;
  readonly state: MessageState;
  
  /**
   * Creates a new Message instance.
   * 
   * @param options Message creation options
   */
  constructor(options: MessageOptions) {
    this.messageId = options.messageId || uuidv4();
    this.timestamp = options.timestamp || new Date().toISOString();
    this.messageType = options.messageType;
    this.sender = options.sender;
    this.recipients = options.recipients;
    this.priority = options.priority || Priority.Medium;
    this.content = options.content;
    this.metadata = options.metadata || {};
    this.state = options.state || {
      processing_status: ProcessingStatus.Received
    };
    
    // Ensure conversation ID
    if (!this.metadata.conversation_id) {
      this.metadata.conversation_id = uuidv4();
    }
  }
  
  /**
   * Creates a response message to this message.
   * 
   * @param content The content for the response
   * @param status The processing status of the response
   * @returns A new message as a response to this message
   */
  createResponse(content: MessageContent, status: ProcessingStatus = ProcessingStatus.Completed): Message {
    return new Message({
      messageType: MessageType.Response,
      sender: this.recipients[0], // First recipient becomes sender
      recipients: [this.sender], // Original sender becomes recipient
      priority: this.priority,
      content: content,
      metadata: {
        conversation_id: this.metadata.conversation_id,
        parent_message_id: this.messageId
      },
      state: {
        processing_status: status
      }
    });
  }
  
  /**
   * Creates an error response to this message.
   * 
   * @param error The error information
   * @returns A new message as an error response to this message
   */
  createErrorResponse(error: MessageError): Message {
    return new Message({
      messageType: MessageType.Response,
      sender: this.recipients[0], // First recipient becomes sender
      recipients: [this.sender], // Original sender becomes recipient
      priority: this.priority,
      content: {
        body: error.message,
        context: {}
      },
      metadata: {
        conversation_id: this.metadata.conversation_id,
        parent_message_id: this.messageId
      },
      state: {
        processing_status: ProcessingStatus.Error,
        error: error
      }
    });
  }
  
  /**
   * Converts the message to a plain JavaScript object.
   * 
   * @returns Plain object representation of the message
   */
  toObject(): Record<string, any> {
    return {
      message_id: this.messageId,
      timestamp: this.timestamp,
      message_type: this.messageType,
      sender: this.sender,
      recipients: this.recipients,
      priority: this.priority,
      content: this.content,
      metadata: this.metadata,
      state: this.state
    };
  }
  
  /**
   * Creates a Message instance from a plain JavaScript object.
   * 
   * @param obj The object to convert
   * @returns A new Message instance
   */
  static fromObject(obj: Record<string, any>): Message {
    return new Message({
      messageId: obj.message_id,
      timestamp: obj.timestamp,
      messageType: obj.message_type as MessageType,
      sender: obj.sender as AgentId,
      recipients: obj.recipients as AgentId[],
      priority: obj.priority as Priority,
      content: obj.content as MessageContent,
      metadata: obj.metadata as MessageMetadata,
      state: obj.state as MessageState
    });
  }
  
  /**
   * Creates a new message with updated content.
   * 
   * @param updatedContent New content to merge with existing content
   * @returns A new Message instance with updated content
   */
  withUpdatedContent(updatedContent: Partial<MessageContent>): Message {
    return new Message({
      messageId: this.messageId,
      timestamp: new Date().toISOString(),
      messageType: this.messageType,
      sender: this.sender,
      recipients: this.recipients,
      priority: this.priority,
      content: {
        ...this.content,
        ...updatedContent
      },
      metadata: this.metadata,
      state: this.state
    });
  }
  
  /**
   * Updates the message processing status.
   * 
   * @param status The new processing status
   * @returns A new Message instance with updated status
   */
  withStatus(status: ProcessingStatus): Message {
    return new Message({
      messageId: this.messageId,
      timestamp: this.timestamp,
      messageType: this.messageType,
      sender: this.sender,
      recipients: this.recipients,
      priority: this.priority,
      content: this.content,
      metadata: this.metadata,
      state: {
        ...this.state,
        processing_status: status
      }
    });
  }
}