/**
 * Messaging Integration for the Supervisor Gateway
 * 
 * This module provides integration with the messaging-v1.vue frontend, handling
 * communication, component rendering, and message transformation between the 
 * frontend and the Supervisor Gateway.
 */

import { SupervisorGateway } from '../core/supervisor_gateway';
import { Message } from '../communication/message';
import { UIComponentDescriptor, VisualizationDescriptor } from '../agents/gov_ui_agent';

/**
 * Client message structure from messaging-v1.vue
 */
export interface ClientMessage {
  id: string;
  timestamp: string;
  sender: {
    id: string;
    type: string;
  };
  type: 'query' | 'response' | 'event' | 'command';
  content: {
    text?: string;
    components?: any[];
    command?: {
      name: string;
      args: any;
    };
  };
  metadata?: Record<string, any>;
}

/**
 * Client response structure for messaging-v1.vue
 */
export interface ClientResponse {
  id: string;
  timestamp: string;
  replyTo: string;
  sender: {
    id: string;
    type: string;
  };
  type: 'response';
  content: {
    text?: string;
    components?: any[];
    visualizations?: any[];
    actions?: any[];
  };
  status: 'success' | 'error' | 'partial';
  metadata?: Record<string, any>;
}

/**
 * Messaging Integration service for connecting with messaging-v1.vue
 */
export class MessagingIntegration {
  /**
   * Creates a new MessagingIntegration instance
   * 
   * @param supervisorGateway - The supervisor gateway instance
   * @param config - Optional configuration
   */
  constructor(
    private supervisorGateway: SupervisorGateway,
    private config: {
      agentId: string;
      agentType: string;
      defaultQueryType: string;
    } = {
      agentId: 'supervisor',
      agentType: 'supervisor',
      defaultQueryType: 'general_query'
    }
  ) {}
  
  /**
   * Processes a client message from the frontend
   * 
   * @param clientMessage - The client message to process
   * @returns A client response
   */
  async processClientMessage(clientMessage: ClientMessage): Promise<ClientResponse> {
    try {
      // Convert client message to internal message format
      const internalMessage = this.convertClientMessageToInternal(clientMessage);
      
      // Process the message through the supervisor gateway
      const response = await this.supervisorGateway.processMessage(internalMessage);
      
      // Convert internal response to client response format
      return this.convertInternalResponseToClient(response, clientMessage.id);
    } catch (error) {
      // Generate error response
      return this.createErrorResponse(
        clientMessage.id,
        `Error processing message: ${error.message}`
      );
    }
  }
  
  /**
   * Creates a WebSocket handler for the messaging integration
   * 
   * @param webSocket - The WebSocket instance
   * @returns A function that handles WebSocket messages
   */
  createWebSocketHandler(webSocket: WebSocket): (event: MessageEvent) => void {
    return async (event: MessageEvent) => {
      try {
        // Parse client message
        const clientMessage = JSON.parse(event.data) as ClientMessage;
        
        // Process the message
        const response = await this.processClientMessage(clientMessage);
        
        // Send response back through WebSocket
        webSocket.send(JSON.stringify(response));
      } catch (error) {
        // Send error response
        const errorResponse = this.createErrorResponse(
          'unknown', // We don't know the original message ID if parsing failed
          `WebSocket message processing error: ${error.message}`
        );
        
        webSocket.send(JSON.stringify(errorResponse));
      }
    };
  }
  
  /**
   * Creates an HTTP handler for the messaging integration
   * 
   * @returns A function that handles HTTP requests and responses
   */
  createHttpHandler(): (req: any, res: any) => void {
    return async (req: any, res: any) => {
      try {
        // Parse client message from request body
        const clientMessage = req.body as ClientMessage;
        
        // Process the message
        const response = await this.processClientMessage(clientMessage);
        
        // Send response
        res.json(response);
      } catch (error) {
        // Send error response
        const errorResponse = this.createErrorResponse(
          req.body?.id || 'unknown',
          `HTTP message processing error: ${error.message}`
        );
        
        res.status(500).json(errorResponse);
      }
    };
  }
  
  /**
   * Converts a client message to the internal message format
   */
  private convertClientMessageToInternal(clientMessage: ClientMessage): Message {
    // Determine query type from client message
    let queryType = this.config.defaultQueryType;
    
    // Extract query type from metadata if available
    if (clientMessage.metadata?.query_type) {
      queryType = clientMessage.metadata.query_type;
    } 
    // Or try to infer from message content
    else if (clientMessage.content.text) {
      queryType = this.inferQueryType(clientMessage.content.text);
    }
    
    // Determine recipients
    const recipients = [];
    
    // If client specified recipients in metadata, use those
    if (clientMessage.metadata?.recipients && Array.isArray(clientMessage.metadata.recipients)) {
      recipients.push(...clientMessage.metadata.recipients);
    } else {
      // Default to supervisor as recipient
      recipients.push({
        id: this.config.agentId,
        type: this.config.agentType
      });
    }
    
    // Create message body
    const body: any = {};
    
    // Add text content if provided
    if (clientMessage.content.text) {
      body.question = clientMessage.content.text;
    }
    
    // Add components if provided
    if (clientMessage.content.components && Array.isArray(clientMessage.content.components)) {
      body.components = clientMessage.content.components;
    }
    
    // Add command if provided
    if (clientMessage.content.command) {
      body.command = clientMessage.content.command;
    }
    
    // Create internal message
    return new Message(
      clientMessage.sender.id,
      clientMessage.sender.type,
      recipients,
      clientMessage.type,
      {
        query_type: queryType,
        body,
        context: {},
        tools: []
      },
      {
        client_message_id: clientMessage.id,
        timestamp: clientMessage.timestamp,
        ...clientMessage.metadata
      }
    );
  }
  
  /**
   * Converts an internal response to the client response format
   */
  private convertInternalResponseToClient(
    response: Message,
    originalMessageId: string
  ): ClientResponse {
    // Create base client response
    const clientResponse: ClientResponse = {
      id: `resp-${Date.now()}`,
      timestamp: new Date().toISOString(),
      replyTo: originalMessageId,
      sender: {
        id: response.sender.id,
        type: response.sender.type
      },
      type: 'response',
      content: {},
      status: response.state.processingStatus === 'error' ? 'error' : 'success',
      metadata: {
        query_type: response.content.query_type,
        ...response.metadata
      }
    };
    
    // Add text content if available
    if (response.content.body?.text || response.content.body?.result) {
      clientResponse.content.text = response.content.body.text || response.content.body.result;
    }
    
    // Add error message if there's an error
    if (response.state.processingStatus === 'error') {
      clientResponse.content.text = response.state.error?.message || 'Unknown error occurred';
    }
    
    // Convert visualizations if available
    if (response.content.body?.visualization || response.content.body?.visualizations) {
      clientResponse.content.visualizations = this.convertVisualizations(response.content.body);
    }
    
    // Convert UI components if available
    if (response.content.body?.component || response.content.body?.components) {
      clientResponse.content.components = this.convertUIComponents(response.content.body);
    }
    
    // Convert actions if available
    if (response.content.body?.actions) {
      clientResponse.content.actions = response.content.body.actions;
    } else {
      // Generate default actions based on response content
      clientResponse.content.actions = this.generateDefaultActions(response);
    }
    
    return clientResponse;
  }
  
  /**
   * Creates an error response
   */
  private createErrorResponse(originalMessageId: string, errorMessage: string): ClientResponse {
    return {
      id: `error-${Date.now()}`,
      timestamp: new Date().toISOString(),
      replyTo: originalMessageId,
      sender: {
        id: this.config.agentId,
        type: this.config.agentType
      },
      type: 'response',
      content: {
        text: errorMessage
      },
      status: 'error',
      metadata: {}
    };
  }
  
  /**
   * Infers the query type from message text
   */
  private inferQueryType(text: string): string {
    const lowercaseText = text.toLowerCase();
    
    // Check for policy-related queries
    if (lowercaseText.includes('policy') || lowercaseText.includes('regulation')) {
      return 'policy_analysis';
    }
    
    // Check for visualization requests
    if (lowercaseText.includes('visualize') || lowercaseText.includes('chart') || 
        lowercaseText.includes('graph') || lowercaseText.includes('plot')) {
      return 'generate_visualization';
    }
    
    // Check for dashboard requests
    if (lowercaseText.includes('dashboard')) {
      return 'dashboard_request';
    }
    
    // Check for UI component requests
    if (lowercaseText.includes('component') || lowercaseText.includes('ui') || 
        lowercaseText.includes('interface')) {
      return 'generate_ui_component';
    }
    
    // Default query type
    return this.config.defaultQueryType;
  }
  
  /**
   * Converts visualization descriptors from internal format to client format
   */
  private convertVisualizations(responseBody: any): any[] {
    const visualizations = [];
    
    // Handle single visualization
    if (responseBody.visualization) {
      visualizations.push(this.convertVisualization(responseBody.visualization));
    }
    
    // Handle visualization array
    if (responseBody.visualizations && Array.isArray(responseBody.visualizations)) {
      responseBody.visualizations.forEach(viz => {
        visualizations.push(this.convertVisualization(viz));
      });
    }
    
    return visualizations;
  }
  
  /**
   * Converts a single visualization from internal format to client format
   */
  private convertVisualization(visualization: VisualizationDescriptor): any {
    // Base conversion with common properties
    const clientViz = {
      id: visualization.id,
      type: visualization.type,
      title: visualization.title,
      data: visualization.data,
      config: visualization.config
    };
    
    // Add type-specific properties for the client
    switch (visualization.type) {
      case 'chart':
        return {
          ...clientViz,
          chartType: visualization.config.type || 'bar',
          height: visualization.config.height || 300,
          width: visualization.config.width || '100%',
          options: {
            legend: visualization.config.legend !== undefined ? visualization.config.legend : true,
            animations: visualization.config.animations !== undefined ? visualization.config.animations : true,
            ...visualization.config
          }
        };
        
      case 'table':
        return {
          ...clientViz,
          headers: visualization.data.headers || [],
          rows: visualization.data.rows || [],
          options: {
            pagination: visualization.config.pagination !== undefined ? visualization.config.pagination : true,
            pageSize: visualization.config.pageSize || 10,
            ...visualization.config
          }
        };
        
      case 'tree':
        return {
          ...clientViz,
          treeData: visualization.data,
          options: {
            nodeSize: visualization.config.nodeSize || 30,
            orientation: visualization.config.orientation || 'vertical',
            ...visualization.config
          }
        };
        
      case 'timeline':
        return {
          ...clientViz,
          events: visualization.data.events || [],
          options: {
            showLabels: visualization.config.showLabels !== undefined ? visualization.config.showLabels : true,
            zoomable: visualization.config.zoomable !== undefined ? visualization.config.zoomable : true,
            ...visualization.config
          }
        };
        
      case 'map':
        return {
          ...clientViz,
          geoData: visualization.data,
          options: {
            projection: visualization.config.projection || 'mercator',
            zoomable: visualization.config.zoomable !== undefined ? visualization.config.zoomable : true,
            ...visualization.config
          }
        };
        
      default:
        return clientViz;
    }
  }
  
  /**
   * Converts UI component descriptors from internal format to client format
   */
  private convertUIComponents(responseBody: any): any[] {
    const components = [];
    
    // Handle single component
    if (responseBody.component) {
      components.push(this.convertUIComponent(responseBody.component));
    }
    
    // Handle component array
    if (responseBody.components && Array.isArray(responseBody.components)) {
      responseBody.components.forEach(comp => {
        components.push(this.convertUIComponent(comp));
      });
    }
    
    // Handle dashboard with components
    if (responseBody.dashboard && responseBody.dashboard.components) {
      responseBody.dashboard.components.forEach(item => {
        if (item.type === 'component' && item.component) {
          components.push(this.convertUIComponent(item.component));
        } else if (item.type === 'visualization' && item.visualization) {
          components.push({
            type: 'Visualization',
            id: item.visualization.id,
            props: {
              visualization: this.convertVisualization(item.visualization)
            }
          });
        }
      });
    }
    
    return components;
  }
  
  /**
   * Converts a single UI component from internal format to client format
   */
  private convertUIComponent(component: UIComponentDescriptor): any {
    // Base conversion with common properties
    const clientComponent = {
      type: component.type,
      id: component.id,
      props: { ...component.props }
    };
    
    // Add children if available
    if (component.children && Array.isArray(component.children)) {
      clientComponent.props.children = component.children.map(child => this.convertUIComponent(child));
    }
    
    return clientComponent;
  }
  
  /**
   * Generates default actions based on response content
   */
  private generateDefaultActions(response: Message): any[] {
    const actions = [];
    
    // Add default actions based on query type
    if (response.content.query_type === 'policy_analysis') {
      actions.push({
        id: 'view-full-policy',
        label: 'View Full Policy Details',
        type: 'button',
        action: 'viewPolicy',
        args: { policyId: response.content.body?.policy?.id || 'unknown' }
      });
      
      actions.push({
        id: 'download-policy',
        label: 'Download Policy Report',
        type: 'button',
        action: 'downloadReport',
        args: { type: 'policy', id: response.content.body?.policy?.id || 'unknown' }
      });
    } else if (response.content.query_type === 'generate_visualization') {
      actions.push({
        id: 'download-visualization',
        label: 'Download Visualization',
        type: 'button',
        action: 'downloadVisualization',
        args: { id: response.content.body?.visualization?.id || 'unknown' }
      });
      
      actions.push({
        id: 'modify-visualization',
        label: 'Modify Visualization',
        type: 'button',
        action: 'modifyVisualization',
        args: { id: response.content.body?.visualization?.id || 'unknown' }
      });
    } else if (response.content.query_type === 'dashboard_request') {
      actions.push({
        id: 'refresh-dashboard',
        label: 'Refresh Dashboard',
        type: 'button',
        action: 'refreshDashboard',
        args: { id: response.content.body?.dashboard?.id || 'unknown' }
      });
      
      actions.push({
        id: 'customize-dashboard',
        label: 'Customize Dashboard',
        type: 'button',
        action: 'customizeDashboard',
        args: { id: response.content.body?.dashboard?.id || 'unknown' }
      });
    }
    
    // Add "ask follow-up" action for all responses
    actions.push({
      id: 'follow-up',
      label: 'Ask Follow-up Question',
      type: 'button',
      action: 'followUpQuestion',
      args: {}
    });
    
    return actions;
  }
}

/**
 * Creates messaging integration middleware for Express
 * 
 * @param supervisorGateway - The supervisor gateway instance
 * @param config - Optional configuration
 * @returns An Express middleware function
 */
export function createMessagingMiddleware(
  supervisorGateway: SupervisorGateway,
  config?: any
) {
  const integration = new MessagingIntegration(supervisorGateway, config);
  return integration.createHttpHandler();
}

/**
 * Creates a WebSocket server handler for messaging integration
 * 
 * @param supervisorGateway - The supervisor gateway instance
 * @param wsServer - WebSocket server instance
 * @param config - Optional configuration
 */
export function setupMessagingWebSocket(
  supervisorGateway: SupervisorGateway,
  wsServer: any,
  config?: any
) {
  const integration = new MessagingIntegration(supervisorGateway, config);
  
  wsServer.on('connection', (ws: WebSocket) => {
    const handler = integration.createWebSocketHandler(ws);
    ws.addEventListener('message', handler);
  });
}