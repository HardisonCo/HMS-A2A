/**
 * Message Protocol for Agent-to-Agent (A2A) Communication
 * 
 * This module defines the message protocol used for communication between agents
 * in the A2A system. It includes message types, interfaces, and utility classes
 * for creating, validating, and processing messages.
 */

import { v4 as uuidv4 } from 'uuid';
import { createHash, createHmac } from 'crypto';

/**
 * Message types for agent communication
 */
export enum MessageType {
  REQUEST = 'REQUEST',
  RESPONSE = 'RESPONSE',
  NOTIFICATION = 'NOTIFICATION',
  ERROR = 'ERROR',
  HEARTBEAT = 'HEARTBEAT',
  DISCOVERY = 'DISCOVERY'
}

/**
 * Message priority levels
 */
export enum MessagePriority {
  LOW = 'LOW',
  NORMAL = 'NORMAL',
  HIGH = 'HIGH',
  URGENT = 'URGENT'
}

/**
 * Security context for message authentication and authorization
 */
export interface SecurityContext {
  principal: string;
  credentials?: any;
  permissions: string[];
  signature?: string;
  timestamp: number;
}

/**
 * Message interface for agent communication
 */
export interface Message {
  id: string;
  type: MessageType;
  sender: string;
  recipient: string;
  subject: string;
  content: any;
  timestamp: number;
  priority: MessagePriority;
  correlationId?: string;
  replyTo?: string;
  ttl?: number;
  security?: SecurityContext;
  metadata?: Record<string, any>;
}

/**
 * Message validation result
 */
export interface MessageValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * Message builder for creating new messages
 */
export class MessageBuilder {
  private message: Partial<Message>;

  constructor() {
    this.message = {
      id: uuidv4(),
      timestamp: Date.now(),
      priority: MessagePriority.NORMAL,
      metadata: {}
    };
  }

  /**
   * Set the message type
   */
  public withType(type: MessageType): MessageBuilder {
    this.message.type = type;
    return this;
  }

  /**
   * Set the message sender
   */
  public withSender(sender: string): MessageBuilder {
    this.message.sender = sender;
    return this;
  }

  /**
   * Set the message recipient
   */
  public withRecipient(recipient: string): MessageBuilder {
    this.message.recipient = recipient;
    return this;
  }

  /**
   * Set the message subject
   */
  public withSubject(subject: string): MessageBuilder {
    this.message.subject = subject;
    return this;
  }

  /**
   * Set the message content
   */
  public withContent(content: any): MessageBuilder {
    this.message.content = content;
    return this;
  }

  /**
   * Set the message priority
   */
  public withPriority(priority: MessagePriority): MessageBuilder {
    this.message.priority = priority;
    return this;
  }

  /**
   * Set the correlation ID
   */
  public withCorrelationId(correlationId: string): MessageBuilder {
    this.message.correlationId = correlationId;
    return this;
  }

  /**
   * Set the reply-to address
   */
  public withReplyTo(replyTo: string): MessageBuilder {
    this.message.replyTo = replyTo;
    return this;
  }

  /**
   * Set the time-to-live in milliseconds
   */
  public withTTL(ttl: number): MessageBuilder {
    this.message.ttl = ttl;
    return this;
  }

  /**
   * Set security context
   */
  public withSecurity(security: SecurityContext): MessageBuilder {
    this.message.security = security;
    return this;
  }

  /**
   * Add metadata to the message
   */
  public withMetadata(key: string, value: any): MessageBuilder {
    if (!this.message.metadata) {
      this.message.metadata = {};
    }
    this.message.metadata[key] = value;
    return this;
  }

  /**
   * Build the message
   */
  public build(): Message {
    // Ensure required fields are present
    if (!this.message.type) {
      throw new Error('Message type is required');
    }
    
    if (!this.message.sender) {
      throw new Error('Message sender is required');
    }
    
    if (!this.message.recipient) {
      throw new Error('Message recipient is required');
    }
    
    if (!this.message.subject) {
      throw new Error('Message subject is required');
    }
    
    return this.message as Message;
  }

  /**
   * Create a response to a given message
   */
  public static createResponse(request: Message, content: any): Message {
    const builder = new MessageBuilder()
      .withType(MessageType.RESPONSE)
      .withSender(request.recipient)
      .withRecipient(request.sender)
      .withSubject(`Re: ${request.subject}`)
      .withContent(content)
      .withCorrelationId(request.id);
    
    if (request.replyTo) {
      builder.withRecipient(request.replyTo);
    }
    
    return builder.build();
  }

  /**
   * Create an error response to a given message
   */
  public static createErrorResponse(request: Message, error: string | Error): Message {
    const errorMessage = typeof error === 'string' ? error : error.message;
    const errorContent = {
      error: errorMessage,
      stack: typeof error === 'string' ? undefined : error.stack
    };
    
    const builder = new MessageBuilder()
      .withType(MessageType.ERROR)
      .withSender(request.recipient)
      .withRecipient(request.sender)
      .withSubject(`Error: ${request.subject}`)
      .withContent(errorContent)
      .withCorrelationId(request.id);
    
    if (request.replyTo) {
      builder.withRecipient(request.replyTo);
    }
    
    return builder.build();
  }
}

/**
 * Message validator for ensuring message integrity
 */
export class MessageValidator {
  /**
   * Validate a message
   */
  public static validate(message: Message): MessageValidationResult {
    const errors: string[] = [];
    
    // Check required fields
    if (!message.id) {
      errors.push('Message ID is required');
    }
    
    if (!message.type) {
      errors.push('Message type is required');
    }
    
    if (!message.sender) {
      errors.push('Message sender is required');
    }
    
    if (!message.recipient) {
      errors.push('Message recipient is required');
    }
    
    if (!message.subject) {
      errors.push('Message subject is required');
    }
    
    if (message.content === undefined) {
      errors.push('Message content is required');
    }
    
    if (!message.timestamp) {
      errors.push('Message timestamp is required');
    }
    
    // Check TTL expiration
    if (message.ttl && message.timestamp) {
      const now = Date.now();
      const expirationTime = message.timestamp + message.ttl;
      
      if (now > expirationTime) {
        errors.push('Message has expired (TTL exceeded)');
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Verify message security
   */
  public static verifySignature(message: Message, secret: string): boolean {
    if (!message.security || !message.security.signature) {
      return false;
    }
    
    // Create a copy of the message without the signature
    const messageForSigning = { ...message };
    const securityContext = { ...message.security };
    delete securityContext.signature;
    messageForSigning.security = securityContext;
    
    // Calculate expected signature
    const data = JSON.stringify(messageForSigning);
    const expectedSignature = createHmac('sha256', secret)
      .update(data)
      .digest('hex');
    
    // Compare signatures
    return message.security.signature === expectedSignature;
  }

  /**
   * Sign a message
   */
  public static signMessage(message: Message, secret: string): Message {
    // Create a copy of the message
    const signedMessage = { ...message };
    
    if (!signedMessage.security) {
      signedMessage.security = {
        principal: message.sender,
        permissions: [],
        timestamp: Date.now()
      };
    }
    
    // Create a copy of the message without the signature
    const messageForSigning = { ...signedMessage };
    const securityContext = { ...signedMessage.security };
    delete securityContext.signature;
    messageForSigning.security = securityContext;
    
    // Calculate signature
    const data = JSON.stringify(messageForSigning);
    const signature = createHmac('sha256', secret)
      .update(data)
      .digest('hex');
    
    // Add signature to the message
    signedMessage.security = {
      ...signedMessage.security,
      signature
    };
    
    return signedMessage;
  }

  /**
   * Calculate message hash
   */
  public static calculateMessageHash(message: Message): string {
    const data = JSON.stringify(message);
    return createHash('sha256')
      .update(data)
      .digest('hex');
  }
}

/**
 * Message processor for handling message processing
 */
export class MessageProcessor {
  /**
   * Process a message
   */
  public static async process(
    message: Message,
    handlers: Record<MessageType, (message: Message) => Promise<Message | void>>
  ): Promise<Message | void> {
    // Validate the message
    const validationResult = MessageValidator.validate(message);
    if (!validationResult.valid) {
      const errorMessage = validationResult.errors.join(', ');
      return MessageBuilder.createErrorResponse(message, errorMessage);
    }
    
    // Find the appropriate handler
    const handler = handlers[message.type];
    if (!handler) {
      return MessageBuilder.createErrorResponse(message, `No handler found for message type: ${message.type}`);
    }
    
    try {
      // Process the message
      return await handler(message);
    } catch (error) {
      // Handle any errors during processing
      return MessageBuilder.createErrorResponse(message, error as Error);
    }
  }
}

/**
 * Create a request message
 */
export function createRequestMessage(
  sender: string,
  recipient: string,
  subject: string,
  content: any,
  options: {
    priority?: MessagePriority;
    ttl?: number;
    replyTo?: string;
    metadata?: Record<string, any>;
  } = {}
): Message {
  const builder = new MessageBuilder()
    .withType(MessageType.REQUEST)
    .withSender(sender)
    .withRecipient(recipient)
    .withSubject(subject)
    .withContent(content);
  
  if (options.priority) {
    builder.withPriority(options.priority);
  }
  
  if (options.ttl) {
    builder.withTTL(options.ttl);
  }
  
  if (options.replyTo) {
    builder.withReplyTo(options.replyTo);
  }
  
  if (options.metadata) {
    for (const [key, value] of Object.entries(options.metadata)) {
      builder.withMetadata(key, value);
    }
  }
  
  return builder.build();
}

/**
 * Create a notification message
 */
export function createNotificationMessage(
  sender: string,
  recipient: string,
  subject: string,
  content: any,
  options: {
    priority?: MessagePriority;
    ttl?: number;
    metadata?: Record<string, any>;
  } = {}
): Message {
  const builder = new MessageBuilder()
    .withType(MessageType.NOTIFICATION)
    .withSender(sender)
    .withRecipient(recipient)
    .withSubject(subject)
    .withContent(content);
  
  if (options.priority) {
    builder.withPriority(options.priority);
  }
  
  if (options.ttl) {
    builder.withTTL(options.ttl);
  }
  
  if (options.metadata) {
    for (const [key, value] of Object.entries(options.metadata)) {
      builder.withMetadata(key, value);
    }
  }
  
  return builder.build();
}

/**
 * Create a heartbeat message
 */
export function createHeartbeatMessage(sender: string, recipient: string): Message {
  return new MessageBuilder()
    .withType(MessageType.HEARTBEAT)
    .withSender(sender)
    .withRecipient(recipient)
    .withSubject('Heartbeat')
    .withContent({ timestamp: Date.now() })
    .withTTL(5000) // 5 seconds TTL
    .build();
}

/**
 * Create a discovery message
 */
export function createDiscoveryMessage(sender: string): Message {
  return new MessageBuilder()
    .withType(MessageType.DISCOVERY)
    .withSender(sender)
    .withRecipient('*') // Broadcast to all agents
    .withSubject('Agent Discovery')
    .withContent({ requestCapabilities: true })
    .build();
}