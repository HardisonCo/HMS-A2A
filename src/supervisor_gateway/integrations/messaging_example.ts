/**
 * Messaging Integration Example
 * 
 * This example demonstrates how to use the MessagingIntegration class
 * to connect the Supervisor Gateway with the messaging-v1.vue frontend.
 */

import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { SupervisorGateway } from '../core/supervisor_gateway';
import { AgentRegistry } from '../core/agent_registry';
import { KnowledgeBaseManager } from '../knowledge/knowledge_base_manager';
import { GovPolicyAgent } from '../agents/gov_policy_agent';
import { GovUIAgent } from '../agents/gov_ui_agent';
import { PolicyFormulator } from '../policy/policy_formulator';
import { RegulatoryAssessment } from '../policy/regulatory_assessment';
import { createMessagingMiddleware, setupMessagingWebSocket } from './messaging_integration';

/**
 * Main function to set up and run the messaging integration example
 */
async function main() {
  // Create the agent registry and supervisor gateway
  const agentRegistry = new AgentRegistry();
  const supervisorGateway = new SupervisorGateway(agentRegistry);
  
  // Create knowledge base manager
  const knowledgeBaseManager = new KnowledgeBaseManager();
  
  // Create policy-related services
  const policyFormulator = new PolicyFormulator(knowledgeBaseManager);
  const regulatoryAssessment = new RegulatoryAssessment(knowledgeBaseManager);
  
  // Create and register agents
  const govPolicyAgent = new GovPolicyAgent('gov-policy-agent', knowledgeBaseManager, policyFormulator, regulatoryAssessment);
  const govUIAgent = new GovUIAgent('gov-ui-agent', knowledgeBaseManager);
  
  agentRegistry.registerAgent(govPolicyAgent);
  agentRegistry.registerAgent(govUIAgent);
  
  // Initialize Express app
  const app = express();
  const port = process.env.PORT || 3000;
  
  // Configure middleware
  app.use(express.json());
  app.use(express.static('public')); // Serve static files
  
  // Create HTTP server
  const server = createServer(app);
  
  // Set up WebSocket server
  const wss = new WebSocketServer({ server });
  
  // Set up messaging integration
  const messagingConfig = {
    agentId: 'supervisor',
    agentType: 'supervisor',
    defaultQueryType: 'general_query'
  };
  
  // Set up HTTP endpoint
  app.post('/api/messaging', createMessagingMiddleware(supervisorGateway, messagingConfig));
  
  // Set up WebSocket integration
  setupMessagingWebSocket(supervisorGateway, wss, messagingConfig);
  
  // Start the server
  server.listen(port, () => {
    console.log(`Server is running on port ${port}`);
    console.log('HTTP endpoint: http://localhost:3000/api/messaging');
    console.log('WebSocket endpoint: ws://localhost:3000');
  });
}

// Run the example if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Error running messaging integration example:', error);
    process.exit(1);
  });
}

export { main };