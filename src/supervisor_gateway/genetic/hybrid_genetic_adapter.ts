/**
 * Hybrid Genetic Adapter for Supervisor Gateway
 * 
 * This adapter integrates the Enhanced Hybrid Genetic Repair Engine with the
 * Supervisor Gateway, allowing supervisors to utilize genetic algorithms with
 * recursive thinking for solution generation and refinement.
 */

import { Injectable } from '@hms/hive';
import { Logger } from '@hms/logger';
import { EnhancedHybridGeneticRepairEngine, EnhancedHybridEngineConfig } from '../../genetic/enhanced_hybrid_genetic_repair_engine';
import { GeneticConstraint, FitnessFunction } from '../../genetic/hybrid_genetic_repair_engine';
import { TOKENS } from '../../hms-sys/genetic/framework/cells';
import { GeneticHealthManager } from '../../hms-sys/genetic/framework/health';
import { GeneticMetricsExporter } from '../../hms-sys/genetic/framework/metrics';
import { ConfigurationManager } from '../../hms-sys/genetic/framework/config';
import { GeneticEventHub, GeneticEventType } from '../../hms-sys/genetic/framework/events';

/**
 * Configuration for the hybrid genetic adapter
 */
export interface HybridGeneticAdapterConfig {
  engineId: string;
  apiKey?: string;
  recursionRounds?: number;
  logProgress?: boolean;
  pythonPath?: string;
  scriptPath?: string;
  useCache?: boolean;
  visualizeThinking?: boolean;
}

/**
 * Solution result interface
 */
export interface SolutionResult {
  solution: string;
  fitness: number;
  thinkingRounds: number;
  executionTime: number;
  memoryUsage: number;
}

/**
 * Adapter for hybrid genetic algorithms in the Supervisor Gateway
 */
@Injectable()
export class HybridGeneticAdapter {
  private engine: EnhancedHybridGeneticRepairEngine;
  private isInitialized = false;
  private logger: Logger;
  private engineId: string;
  
  constructor(
    logger: Logger,
    @Injectable(TOKENS.GENETIC_HEALTH_MANAGER) private healthManager: GeneticHealthManager,
    @Injectable(TOKENS.GENETIC_METRICS_EXPORTER) private metricsExporter: GeneticMetricsExporter,
    @Injectable(TOKENS.GENETIC_EVENT_HUB) private eventHub: GeneticEventHub,
    @Injectable(TOKENS.CONFIGURATION_MANAGER) private configManager: ConfigurationManager
  ) {
    this.logger = logger.child({ component: 'hybrid-genetic-adapter' });
    this.engine = new EnhancedHybridGeneticRepairEngine();
    this.engineId = `hybrid-genetic-${Date.now()}`;
  }
  
  /**
   * Initialize the hybrid genetic adapter
   */
  public async initialize(config?: HybridGeneticAdapterConfig): Promise<void> {
    if (this.isInitialized) return;
    
    this.logger.info('Initializing hybrid genetic adapter');
    
    try {
      // Set engine ID from config if provided
      if (config?.engineId) {
        this.engineId = config.engineId;
      }
      
      // Get engine configuration from config manager
      const engineConfig = this.configManager.configureHybridEngine(this.engine);
      
      // Override with provided config values
      if (config) {
        if (config.apiKey) engineConfig.apiKey = config.apiKey;
        if (config.recursionRounds) engineConfig.recursionRounds = config.recursionRounds;
        if (config.logProgress !== undefined) engineConfig.logProgress = config.logProgress;
        if (config.pythonPath) engineConfig.pythonPath = config.pythonPath;
        if (config.scriptPath) engineConfig.scriptPath = config.scriptPath;
      }
      
      // Initialize engine
      await this.engine.initialize(engineConfig);
      
      // Register with health manager
      this.healthManager.registerComponent(`hybrid-genetic-${this.engineId}`, async () => {
        return {
          status: this.engine['isHybridInitialized'] ? 'healthy' : 'unhealthy',
          details: {
            engineId: this.engineId,
            wsConnected: this.engine['communicator'] ? true : false
          }
        };
      });
      
      // Register with metrics exporter
      this.metricsExporter.registerHybridGeneticEngineMetrics(this.engine, this.engineId);
      
      // Register event handlers
      this.eventHub.emit(GeneticEventType.NODE_READY, {
        component: `hybrid-genetic-${this.engineId}`,
        status: 'ready'
      });
      
      this.isInitialized = true;
      this.logger.info(`Hybrid genetic adapter initialized with ID: ${this.engineId}`);
    } catch (error) {
      this.logger.error('Failed to initialize hybrid genetic adapter', error);
      throw error;
    }
  }
  
  /**
   * Generate a solution using the hybrid genetic algorithm
   */
  public async generateSolution(
    candidateSolutions: string[],
    constraints: GeneticConstraint[] = [],
    fitnessFunction: FitnessFunction,
    options?: { recursionRounds?: number }
  ): Promise<SolutionResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    this.logger.info(`Generating solution with ${candidateSolutions.length} candidate solutions`);
    
    try {
      // Run hybrid evolution
      const result = await this.engine.enhancedEvolve(
        candidateSolutions,
        constraints,
        fitnessFunction
      );
      
      // Return the solution result
      return {
        solution: result.solution,
        fitness: result.fitness,
        thinkingRounds: result.thinkingRounds,
        executionTime: result.executionTime,
        memoryUsage: result.memoryUsage
      };
    } catch (error) {
      this.logger.error('Failed to generate solution', error);
      throw error;
    }
  }
  
  /**
   * Refine an existing solution using recursive thinking
   */
  public async refineSolution(
    solution: string,
    constraints: GeneticConstraint[] = [],
    fitnessFunction: FitnessFunction
  ): Promise<SolutionResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    this.logger.info('Refining solution using recursive thinking');
    
    try {
      // First refine the solution
      const refinementResult = await this.engine.refineSolution(solution, constraints);
      
      // Then evaluate the fitness
      const refinedFitness = await fitnessFunction(refinementResult.refined);
      
      // Create a solution result
      return {
        solution: refinementResult.refined,
        fitness: refinedFitness,
        thinkingRounds: refinementResult.thinkingRounds,
        executionTime: 0, // Not available in refineSolution
        memoryUsage: 0    // Not available in refineSolution
      };
    } catch (error) {
      this.logger.error('Failed to refine solution', error);
      throw error;
    }
  }
  
  /**
   * Close the hybrid genetic adapter and release resources
   */
  public async close(): Promise<void> {
    if (!this.isInitialized) return;
    
    this.logger.info('Closing hybrid genetic adapter');
    
    try {
      // Close the engine
      await this.engine.close();
      
      // Unregister from health manager
      this.healthManager.unregisterComponent(`hybrid-genetic-${this.engineId}`);
      
      // Emit event
      this.eventHub.emit(GeneticEventType.NODE_STOPPED, {
        component: `hybrid-genetic-${this.engineId}`,
      });
      
      this.isInitialized = false;
      this.logger.info('Hybrid genetic adapter closed');
    } catch (error) {
      this.logger.error('Error closing hybrid genetic adapter', error);
      throw error;
    }
  }
  
  /**
   * Get the status of the hybrid genetic adapter
   */
  public getStatus(): {
    isInitialized: boolean;
    engineId: string;
    websocketConnected: boolean;
  } {
    return {
      isInitialized: this.isInitialized,
      engineId: this.engineId,
      websocketConnected: this.engine['communicator'] && this.engine['communicator']['isConnected'] ? true : false
    };
  }
}