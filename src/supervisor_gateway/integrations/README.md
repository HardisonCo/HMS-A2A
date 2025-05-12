# Messaging-v1.vue Integration

This directory contains the implementation for integrating the Supervisor Gateway with the messaging-v1.vue frontend component. The integration enables communication between the frontend and the various agents in the system through HTTP and WebSocket protocols.

## Overview

The messaging integration provides a bridge between the messaging-v1.vue frontend component and the Supervisor Gateway. It transforms client messages into the internal message format used by the gateway, routes them to the appropriate agents, and converts the responses back to a format that can be rendered by the frontend.

## Components

### 1. MessagingIntegration Class

The main class that handles the conversion between client and internal message formats, and processes messages through the Supervisor Gateway.

Key features:
- Transforms client messages to internal format
- Routes messages through the Supervisor Gateway
- Converts internal responses to client-friendly format
- Handles error scenarios gracefully
- Supports both HTTP and WebSocket communication

### 2. MessagingV1 Vue Component

A Vue component that provides a user interface for interacting with the Supervisor Gateway.

Key features:
- Renders messages, visualizations, and UI components
- Supports both HTTP and WebSocket communication
- Provides action buttons for user interactions
- Handles loading states and error scenarios
- Responsive design for different screen sizes

### 3. Example Implementation

An example implementation showing how to set up the integration with:
- Express.js HTTP server
- WebSocket server
- Gov Policy and UI agents
- Basic HTML frontend

## Usage

### HTTP Integration

```typescript
import express from 'express';
import { SupervisorGateway } from '../core/supervisor_gateway';
import { createMessagingMiddleware } from './messaging_integration';

// Set up Express app
const app = express();
app.use(express.json());

// Create supervisor gateway
const supervisorGateway = /* initialize supervisor gateway */;

// Set up messaging endpoint
app.post('/api/messaging', createMessagingMiddleware(supervisorGateway, {
  agentId: 'supervisor',
  agentType: 'supervisor',
  defaultQueryType: 'general_query'
}));

// Start server
app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### WebSocket Integration

```typescript
import { createServer } from 'http';
import express from 'express';
import { WebSocketServer } from 'ws';
import { SupervisorGateway } from '../core/supervisor_gateway';
import { setupMessagingWebSocket } from './messaging_integration';

// Set up Express app and HTTP server
const app = express();
const server = createServer(app);

// Create WebSocket server
const wss = new WebSocketServer({ server });

// Create supervisor gateway
const supervisorGateway = /* initialize supervisor gateway */;

// Set up WebSocket integration
setupMessagingWebSocket(supervisorGateway, wss, {
  agentId: 'supervisor',
  agentType: 'supervisor',
  defaultQueryType: 'general_query'
});

// Start server
server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### Vue Component Usage

```html
<template>
  <div>
    <MessagingV1
      title="Government Policy Assistant"
      :api-endpoint="'/api/messaging'"
      :ws-endpoint="'ws://localhost:3000'"
      :use-web-socket="true"
      @message-received="handleMessageReceived"
      @action-clicked="handleActionClicked"
    />
  </div>
</template>

<script>
import MessagingV1 from './messaging-v1.vue';

export default {
  components: {
    MessagingV1
  },
  methods: {
    handleMessageReceived(message) {
      console.log('Message received:', message);
    },
    handleActionClicked(action) {
      console.log('Action clicked:', action);
      
      // Handle specific actions
      if (action.action === 'downloadReport') {
        // Implement download functionality
      }
    }
  }
};
</script>
```

## Message Format

### Client Message Format

```typescript
interface ClientMessage {
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
```

### Client Response Format

```typescript
interface ClientResponse {
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
```

## Running the Example

1. Install dependencies:
   ```
   npm install express ws
   ```

2. Build the project:
   ```
   npm run build
   ```

3. Run the example:
   ```
   node dist/integrations/messaging_example.js
   ```

4. Open a browser and navigate to `http://localhost:3000` to see the demo interface.

## Development

To extend the messaging integration, you can:

1. Enhance the message transformation logic in `MessagingIntegration`
2. Add support for new visualization types in the Vue component
3. Implement additional actions in the action handler
4. Add authentication and authorization to secure the communication

## Testing

When testing the integration, consider:

1. Message format compatibility
2. Error handling scenarios
3. WebSocket connection stability
4. Performance with large messages or visualizations
5. Cross-browser compatibility of the Vue component