/**
 * Enhanced Hybrid Genetic Repair Engine with WebSocket Communication
 * 
 * Extends the HybridGeneticRepairEngine with optimized WebSocket communication
 * for improved performance and streaming data transfer.
 */

import { GeneticRepairEngine, GeneticSolution, GeneticConstraint, FitnessFunction } from './genetic_repair_engine';
import { WebSocketCommunicator, MessageType, CommunicationOptions } from './communication/websocket_communicator';

/**
 * Interface for enhanced hybrid solution results
 */
export interface EnhancedHybridGeneticSolution extends GeneticSolution {
  recursiveImprovements: number;
  thinkingRounds: number;
  thinkingHistory?: any[];
  executionTime: number;
  memoryUsage: number;
}

/**
 * Configuration for the enhanced hybrid engine
 */
export interface EnhancedHybridEngineConfig extends CommunicationOptions {
  apiKey?: string;
  recursionRounds?: number;
  logProgress?: boolean;
}

/**
 * Enhanced Hybrid Genetic Repair Engine that combines genetic algorithms
 * with recursive thinking for solution refinement, using WebSocket communication
 * for improved performance.
 */
export class EnhancedHybridGeneticRepairEngine extends GeneticRepairEngine {
  private isHybridInitialized: boolean = false;
  private config: EnhancedHybridEngineConfig;
  private communicator: WebSocketCommunicator | null = null;
  private defaultConfig: EnhancedHybridEngineConfig = {
    pythonPath: 'python3',
    scriptPath: '../recursive_thinking/websocket_server.py',
    port: 8765,
    verbose: false,
    recursionRounds: 2,
    logProgress: true,
    timeout: 120000, // 2 minutes
  };
  
  /**
   * Initialize the enhanced hybrid genetic repair engine
   */
  async initialize(config?: EnhancedHybridEngineConfig): Promise<void> {
    // Initialize the base genetic engine
    await super.initialize();
    
    if (this.isHybridInitialized) return;
    
    console.log('Initializing Enhanced Hybrid Genetic Repair Engine');
    
    // Update config with any provided values
    this.config = { ...this.defaultConfig, ...config };
    
    // Initialize WebSocket communicator
    this.communicator = new WebSocketCommunicator({
      pythonPath: this.config.pythonPath,
      scriptPath: this.config.scriptPath,
      port: this.config.port,
      verbose: this.config.verbose,
      timeout: this.config.timeout,
    });
    
    // Set up progress event listener if logging is enabled
    if (this.config.logProgress) {
      this.communicator.on('progress', (progress) => {
        console.log(`[Progress] ${progress.message}`);
      });
    }
    
    // Initialize communicator
    await this.communicator.initialize();
    
    // Initialize components on the Python side
    await this.communicator.sendMessage(MessageType.INITIALIZE, {
      api_key: this.config.apiKey
    });
    
    this.isHybridInitialized = true;
    console.log('Enhanced Hybrid Genetic Repair Engine initialized successfully');
  }
  
  /**
   * Evolve a solution using the enhanced hybrid approach with WebSocket communication
   */
  async enhancedEvolve(
    candidateSolutions: string[],
    constraints: GeneticConstraint[] = [],
    fitnessFunction: FitnessFunction
  ): Promise<EnhancedHybridGeneticSolution> {
    if (!this.isHybridInitialized || !this.communicator) {
      await this.initialize();
    }
    
    const startTime = Date.now();
    const startMemory = process.memoryUsage().heapUsed;
    
    console.log(`Starting enhanced hybrid evolution with ${candidateSolutions.length} initial candidates`);
    
    try {
      // First, run genetic algorithm to get a head start
      const geneticSolution = await super.evolve(candidateSolutions, constraints, fitnessFunction);
      
      console.log(`Initial genetic solution found with fitness ${geneticSolution.fitness}`);
      
      // Send the results to Python for recursive thinking enhancement using WebSocket
      const fitnessAdapter = EnhancedHybridGeneticRepairEngine.createPythonFitnessAdapter(fitnessFunction);
      
      // Prepare the constraints in the format expected by Python
      const pythonConstraints = constraints.map(constraint => ({
        type: constraint.type,
        value: constraint.value
      }));
      
      // Evolve using WebSocket communication
      const hybridResult = await this.communicator.evolve(
        [geneticSolution.solution, ...candidateSolutions],
        pythonConstraints,
        'typescript_fitness',
        this.config.recursionRounds
      );
      
      // Calculate performance metrics
      const endTime = Date.now();
      const endMemory = process.memoryUsage().heapUsed;
      const executionTime = endTime - startTime;
      const memoryUsage = (endMemory - startMemory) / (1024 * 1024); // Convert to MB
      
      console.log(`Enhanced hybrid evolution completed in ${executionTime}ms, using ${memoryUsage.toFixed(2)}MB memory`);
      console.log(`Final solution fitness: ${hybridResult.fitness}`);
      
      // Return enhanced hybrid solution
      return {
        solution: hybridResult.solution,
        fitness: hybridResult.fitness,
        generation: geneticSolution.generation,
        recursiveImprovements: hybridResult.history ? hybridResult.history.length : 0,
        thinkingRounds: hybridResult.rounds || this.config.recursionRounds,
        thinkingHistory: hybridResult.history,
        executionTime,
        memoryUsage
      };
    } catch (error) {
      console.error('Error during enhanced hybrid evolution:', error);
      throw new Error(`Enhanced hybrid evolution failed: ${error.message}`);
    }
  }
  
  /**
   * Refine a solution using recursive thinking via WebSocket
   */
  async refineSolution(
    solution: string,
    constraints: GeneticConstraint[] = [],
  ): Promise<{
    original: string;
    refined: string;
    thinkingRounds: number;
  }> {
    if (!this.isHybridInitialized || !this.communicator) {
      await this.initialize();
    }
    
    console.log(`Refining solution: "${solution.substring(0, 50)}..."`);
    
    try {
      // Prepare the constraints in the format expected by Python
      const pythonConstraints = constraints.map(constraint => ({
        type: constraint.type,
        value: constraint.value
      }));
      
      // Refine using WebSocket communication
      const result = await this.communicator.refine(solution, pythonConstraints);
      
      return {
        original: solution,
        refined: result.solution,
        thinkingRounds: this.config.recursionRounds
      };
    } catch (error) {
      console.error('Error during solution refinement:', error);
      throw new Error(`Solution refinement failed: ${error.message}`);
    }
  }
  
  /**
   * Evaluate multiple solutions
   */
  async evaluateSolutions(
    solutions: string[],
    fitnessFunction: FitnessFunction
  ): Promise<Array<{
    solution: string;
    fitness: number;
  }>> {
    if (!this.isHybridInitialized || !this.communicator) {
      await this.initialize();
    }
    
    console.log(`Evaluating ${solutions.length} solutions`);
    
    try {
      // First, evaluate locally using the TypeScript fitness function
      const localResults = await Promise.all(
        solutions.map(async (solution) => ({
          solution,
          fitness: await fitnessFunction(solution)
        }))
      );
      
      return localResults;
    } catch (error) {
      console.error('Error during solution evaluation:', error);
      throw new Error(`Solution evaluation failed: ${error.message}`);
    }
  }
  
  /**
   * Close the engine and release resources
   */
  async close(): Promise<void> {
    if (this.communicator) {
      await this.communicator.close();
      this.communicator = null;
    }
    
    this.isHybridInitialized = false;
    console.log('Enhanced Hybrid Genetic Repair Engine closed');
  }
  
  /**
   * Create a fitness function adapter for the Python script
   */
  static createPythonFitnessAdapter(
    fitnessFunction: FitnessFunction
  ): (candidates: string[]) => Promise<number[]> {
    return async (candidates: string[]) => {
      const results: number[] = [];
      
      for (const candidate of candidates) {
        const fitness = await fitnessFunction(candidate);
        results.push(fitness);
      }
      
      return results;
    };
  }
}