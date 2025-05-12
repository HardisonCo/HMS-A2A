/**
 * Supervisor Gateway Entry Point
 * 
 * This is the main entry point for the Supervisor Gateway application.
 * It initializes all necessary components and starts the service.
 */

import { SupervisorGateway } from './core/supervisor_gateway';
import { AgentRegistry } from './core/agent_registry';
import { CoRTEngine } from './cort/cort_engine';
import { EconomicAnalysisCore } from './economic/economic_analysis_core';
import { TheoremProverClient } from './economic/theorem_prover_client';
import { GeneticAlgorithmClient } from './economic/genetic_algorithm_client';
import { MoneyballTradeClient } from './economic/moneyball_trade_client';
import { KnowledgeBaseManager } from './knowledge/knowledge_base_manager';
import { EconomicAgent } from './agents/economic_agent';
import { AgentId, AgentType } from './communication/message';

/**
 * Main function to initialize and start the Supervisor Gateway.
 */
async function main() {
  try {
    console.log('Starting Supervisor Gateway...');
    
    // Initialize clients for economic services
    const theoremProverClient = new TheoremProverClient();
    const geneticAlgorithmClient = new GeneticAlgorithmClient();
    const moneyballTradeClient = new MoneyballTradeClient();
    
    // Initialize knowledge base manager
    const knowledgeBaseManager = new KnowledgeBaseManager('../../../agent_knowledge_base');
    
    // Initialize CoRT engine
    const cortEngine = new CoRTEngine();
    await cortEngine.initialize();
    
    // Initialize Economic Analysis Core
    const economicAnalysisCore = new EconomicAnalysisCore(
      theoremProverClient,
      geneticAlgorithmClient,
      moneyballTradeClient
    );
    await economicAnalysisCore.initialize();
    
    // Initialize agent registry
    const agentRegistry = new AgentRegistry();
    
    // Initialize Economic Agent
    const economicAgent = new EconomicAgent(
      { id: 'economic-agent', type: AgentType.Economic },
      knowledgeBaseManager,
      theoremProverClient,
      geneticAlgorithmClient,
      moneyballTradeClient
    );
    await economicAgent.initialize();
    
    // Register agents with registry
    agentRegistry.registerAgent(economicAgent);
    
    // Start agents
    await economicAgent.start();
    
    // Initialize Supervisor Gateway
    const supervisorGateway = new SupervisorGateway(
      agentRegistry,
      cortEngine,
      economicAnalysisCore
    );
    await supervisorGateway.initialize();
    
    console.log('Supervisor Gateway started successfully');
    
    // Example message processing
    const response = await supervisorGateway.routeMessage(
      "Analyze the impact of current tariffs on inflation and recommend mitigation strategies for stagflation risks."
    );
    
    console.log('Example response:', JSON.stringify(response, null, 2));
    
    // Keep process running
    process.on('SIGINT', async () => {
      console.log('Shutting down Supervisor Gateway...');
      
      // Stop all agents
      await economicAgent.stop();
      
      console.log('Supervisor Gateway shut down successfully');
      process.exit(0);
    });
    
    console.log('Supervisor Gateway is running. Press Ctrl+C to shut down.');
    
  } catch (error) {
    console.error('Error starting Supervisor Gateway:', error);
    process.exit(1);
  }
}

// Run the main function
main().catch(error => {
  console.error('Unhandled error in main function:', error);
  process.exit(1);
});