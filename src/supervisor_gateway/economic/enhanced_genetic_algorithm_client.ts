/**
 * Enhanced Genetic Algorithm Client
 *
 * Client for interacting with the Enhanced Hybrid Genetic Repair Engine.
 * Provides an interface for optimizing economic strategies and policies
 * using a hybrid genetic algorithm with recursive thinking capabilities.
 */

import { HealthState } from '../monitoring/health_types';
import { GeneticAlgorithmClient, OptimizationRequest } from './genetic_algorithm_client';
import { HybridGeneticAdapter, SolutionResult } from '../genetic/hybrid_genetic_adapter';
import { Logger } from '@hms/logger';
import { Injectable } from '@hms/hive';
import { GeneticConstraint, FitnessFunction } from '../../genetic/hybrid_genetic_repair_engine';

/**
 * Enhanced optimization request parameters.
 */
export interface EnhancedOptimizationRequest extends OptimizationRequest {
  // Hybrid genetic algorithm parameters
  recursionRounds?: number;
  useHybridEngine?: boolean;
  thinkingVisualization?: boolean;
  
  // Recursive thinking parameters
  thinkingPrompt?: string;
  thinkingConstraints?: string[];
  
  // Cache parameters
  useCache?: boolean;
  cacheKey?: string;
}

/**
 * Enhanced genetic algorithm client that integrates with the hybrid genetic repair engine.
 */
@Injectable()
export class EnhancedGeneticAlgorithmClient extends GeneticAlgorithmClient {
  private hybridAdapter: HybridGeneticAdapter;
  private logger: Logger;
  private useHybridByDefault: boolean = true;
  
  /**
   * Creates a new EnhancedGeneticAlgorithmClient instance.
   *
   * @param endpoint The endpoint of the genetic algorithm service
   * @param hybridAdapter The hybrid genetic adapter
   * @param logger The logger
   */
  constructor(
    endpoint: string,
    hybridAdapter: HybridGeneticAdapter,
    logger: Logger
  ) {
    super(endpoint);
    this.hybridAdapter = hybridAdapter;
    this.logger = logger.child({ component: 'enhanced-genetic-algorithm-client' });
  }
  
  /**
   * Initializes the client.
   *
   * @returns A promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    // Initialize the base client
    await super.initialize();
    
    // Initialize the hybrid adapter
    await this.hybridAdapter.initialize({
      engineId: 'economic-optimizer',
      useCache: true
    });
    
    this.logger.info('Enhanced Genetic Algorithm Client initialized successfully');
  }
  
  /**
   * Optimizes parameters using the enhanced hybrid genetic algorithm.
   *
   * @param params Enhanced optimization parameters
   * @returns Optimization result
   */
  async enhancedOptimize(params: EnhancedOptimizationRequest): Promise<any> {
    // Determine whether to use hybrid engine
    const useHybrid = params.useHybridEngine !== undefined 
      ? params.useHybridEngine 
      : this.useHybridByDefault;
    
    // If not using hybrid engine, fall back to standard optimize
    if (!useHybrid) {
      return super.optimize(params);
    }
    
    this.logger.info(`Optimizing with hybrid engine: ${params.fitnessFunction}`);
    
    try {
      // Create fitness function
      const fitnessFunction = this.createFitnessFunction(params);
      
      // Create constraints
      const constraints = this.createConstraints(params);
      
      // Create candidate solutions
      const candidates = await this.createCandidateSolutions(params);
      
      // Run hybrid genetic algorithm
      const result = await this.hybridAdapter.generateSolution(
        candidates,
        constraints,
        fitnessFunction,
        {
          recursionRounds: params.recursionRounds || 2
        }
      );
      
      // Format result to match GA framework format
      return this.formatHybridResult(result, params);
    } catch (error) {
      this.logger.error('Error in enhanced optimization', error);
      throw error;
    }
  }
  
  /**
   * Creates a fitness function from optimization parameters.
   *
   * @param params Optimization parameters
   * @returns Fitness function
   */
  private createFitnessFunction(params: EnhancedOptimizationRequest): FitnessFunction {
    // In a real implementation, this would create a fitness function based on the parameters
    // For now, we'll create a simple fitness function
    return async (solution: string): Promise<number> => {
      // Parse solution as JSON if it's a valid JSON string
      let solutionObj;
      try {
        solutionObj = JSON.parse(solution);
      } catch (e) {
        // Not JSON, use as-is
        solutionObj = solution;
      }
      
      // Simulate fitness calculation based on the fitness function name
      switch (params.fitnessFunction) {
        case 'stagflation_mitigation': {
          // Extract parameters from solution
          const { 
            interest_rate_adjustment = 0,
            fiscal_stimulus_percentage = 0,
            supply_side_reform_intensity = 0
          } = typeof solutionObj === 'object' ? solutionObj : {};
          
          // Calculate fitness as weighted sum - this is a simplified example
          // In reality, this would use the economic model to calculate fitness
          const inflationControl = Math.exp(-Math.pow(interest_rate_adjustment - 0.5, 2));
          const growthStimulus = fiscal_stimulus_percentage * 0.8;
          const supplyEfficiency = supply_side_reform_intensity * 0.5;
          
          // Trade-off between inflation control, growth stimulus, and supply efficiency
          return 0.4 * inflationControl + 0.3 * growthStimulus + 0.3 * supplyEfficiency;
        }
        
        case 'trade_balance_optimization': {
          // Extract parameters from solution
          const { 
            tariff_rate_adjustment = 0,
            export_incentive_percentage = 0
          } = typeof solutionObj === 'object' ? solutionObj : {};
          
          // Calculate fitness as weighted sum - this is a simplified example
          const tradeBalance = export_incentive_percentage * 0.7 - Math.abs(tariff_rate_adjustment) * 0.3;
          const economicEfficiency = Math.exp(-Math.pow(tariff_rate_adjustment, 2) * 0.1);
          
          // Trade-off between trade balance and economic efficiency
          return 0.6 * tradeBalance + 0.4 * economicEfficiency;
        }
        
        default: {
          // Default fitness function for unknown fitness functions
          // Just return a random value between 0 and 1
          return Math.random();
        }
      }
    };
  }
  
  /**
   * Creates constraints from optimization parameters.
   *
   * @param params Optimization parameters
   * @returns Constraints
   */
  private createConstraints(params: EnhancedOptimizationRequest): GeneticConstraint[] {
    // Create constraints based on the fitness function
    // These constraints will be used by the hybrid genetic algorithm
    const constraints: GeneticConstraint[] = [];
    
    // Add constraints based on the parameters
    if (params.constraints && params.constraints.length > 0) {
      for (const constraint of params.constraints) {
        if (constraint.type === 'min_value' && constraint.parameter && constraint.value) {
          constraints.push({
            type: 'must_contain',
            value: `"${constraint.parameter}": ${constraint.value}`
          });
        } else if (constraint.type === 'max_value' && constraint.parameter && constraint.value) {
          constraints.push({
            type: 'must_not_contain',
            value: `"${constraint.parameter}": ${parseFloat(constraint.value) + 0.000001}`
          });
        }
      }
    }
    
    // Add standard constraints based on the optimization type
    switch (params.fitnessFunction) {
      case 'stagflation_mitigation':
        // Ensure it's a valid JSON object
        constraints.push({
          type: 'must_contain',
          value: '{'
        });
        constraints.push({
          type: 'must_contain',
          value: '}'
        });
        break;
        
      case 'trade_balance_optimization':
        // Ensure it's a valid JSON object
        constraints.push({
          type: 'must_contain',
          value: '{'
        });
        constraints.push({
          type: 'must_contain',
          value: '}'
        });
        break;
    }
    
    // Add thinking constraints if provided
    if (params.thinkingConstraints && params.thinkingConstraints.length > 0) {
      for (const constraint of params.thinkingConstraints) {
        constraints.push({
          type: 'must_contain',
          value: constraint
        });
      }
    }
    
    return constraints;
  }
  
  /**
   * Creates candidate solutions from optimization parameters.
   *
   * @param params Optimization parameters
   * @returns Candidate solutions
   */
  private async createCandidateSolutions(params: EnhancedOptimizationRequest): Promise<string[]> {
    // In a real implementation, this would create candidate solutions based on the parameters
    // For now, we'll create some simple example solutions
    const candidates: string[] = [];
    
    // Create initial candidate solutions based on the fitness function
    switch (params.fitnessFunction) {
      case 'stagflation_mitigation': {
        // Create 5 random candidate solutions
        for (let i = 0; i < 5; i++) {
          const interest_rate_adjustment = -2 + Math.random() * 4; // -2 to 2
          const fiscal_stimulus_percentage = Math.random() * 5; // 0 to 5
          const supply_side_reform_intensity = Math.random() * 10; // 0 to 10
          
          candidates.push(JSON.stringify({
            interest_rate_adjustment,
            fiscal_stimulus_percentage,
            supply_side_reform_intensity
          }));
        }
        
        // Add some predefined candidates
        candidates.push(JSON.stringify({
          interest_rate_adjustment: 1.0,
          fiscal_stimulus_percentage: 2.5,
          supply_side_reform_intensity: 7.0
        }));
        
        candidates.push(JSON.stringify({
          interest_rate_adjustment: -0.5,
          fiscal_stimulus_percentage: 3.0,
          supply_side_reform_intensity: 5.0
        }));
        break;
      }
      
      case 'trade_balance_optimization': {
        // Create 5 random candidate solutions
        for (let i = 0; i < 5; i++) {
          const tariff_rate_adjustment = -10 + Math.random() * 20; // -10 to 10
          const export_incentive_percentage = Math.random() * 5; // 0 to 5
          
          candidates.push(JSON.stringify({
            tariff_rate_adjustment,
            export_incentive_percentage
          }));
        }
        
        // Add some predefined candidates
        candidates.push(JSON.stringify({
          tariff_rate_adjustment: 2.0,
          export_incentive_percentage: 3.0
        }));
        
        candidates.push(JSON.stringify({
          tariff_rate_adjustment: -1.0,
          export_incentive_percentage: 4.0
        }));
        break;
      }
      
      default: {
        // For unknown fitness functions, create generic candidate solutions
        candidates.push(JSON.stringify({ param1: 0.5, param2: 0.5, param3: 0.5 }));
        candidates.push(JSON.stringify({ param1: 0.3, param2: 0.7, param3: 0.4 }));
        candidates.push(JSON.stringify({ param1: 0.7, param2: 0.3, param3: 0.6 }));
        break;
      }
    }
    
    // If initialConditions are provided, add them as candidate solutions
    if (params.initialConditions) {
      if (typeof params.initialConditions === 'string') {
        candidates.push(params.initialConditions);
      } else {
        candidates.push(JSON.stringify(params.initialConditions));
      }
    }
    
    return candidates;
  }
  
  /**
   * Formats a hybrid result to match the genetic algorithm framework format.
   *
   * @param result Hybrid solution result
   * @param params Optimization parameters
   * @returns Formatted result
   */
  private formatHybridResult(result: SolutionResult, params: EnhancedOptimizationRequest): any {
    // Parse solution as JSON if it's a valid JSON string
    let solutionObj;
    try {
      solutionObj = JSON.parse(result.solution);
    } catch (e) {
      // Not JSON, use as-is
      solutionObj = result.solution;
    }
    
    // Create parameter values from solution object
    const parameterValues: any[] = [];
    if (typeof solutionObj === 'object' && solutionObj !== null) {
      for (const [key, value] of Object.entries(solutionObj)) {
        parameterValues.push({
          name: key,
          value: value,
          type: typeof value
        });
      }
    }
    
    // Format result to match GA framework format
    return {
      runMetadata: {
        id: `hybrid-${Date.now()}`,
        problemConfigId: 'hybrid-config',
        startTime: new Date(Date.now() - result.executionTime).toISOString(),
        endTime: new Date().toISOString(),
        status: 'completed',
        createdBy: 'hybrid-genetic-engine',
        notes: 'Generated using hybrid genetic algorithm with recursive thinking'
      },
      solutions: [
        {
          id: `sol-${Date.now()}`,
          fitness: result.fitness,
          rank: 1,
          parameterValues,
          rawSolution: result.solution,
          metadata: {
            thinkingRounds: result.thinkingRounds,
            executionTime: result.executionTime,
            memoryUsage: result.memoryUsage
          }
        }
      ],
      problemSummary: {
        problemName: params.problemName || `${params.fitnessFunction} Optimization`,
        domainType: params.domain || 'economic',
        parametersOptimized: parameterValues.map(p => p.name),
        constraints: params.constraints || []
      },
      performanceMetrics: {
        totalRunTimeMs: result.executionTime,
        evaluationsPerSecond: 1000 / result.executionTime, // Rough estimate
        generationCount: 1, // Hybrid engine doesn't use generations in the same way
        improvementRate: [
          {
            generation: 0,
            fitness: 0
          },
          {
            generation: 1,
            fitness: result.fitness
          }
        ]
      },
      hybridThinkingMetrics: {
        thinkingRounds: result.thinkingRounds,
        memoryUsage: result.memoryUsage,
        hybridEngineUsed: true
      }
    };
  }
  
  /**
   * Sets whether to use the hybrid engine by default.
   *
   * @param useHybrid Whether to use the hybrid engine by default
   */
  setUseHybridByDefault(useHybrid: boolean): void {
    this.useHybridByDefault = useHybrid;
  }
  
  /**
   * Gets whether the hybrid engine is used by default.
   *
   * @returns Whether the hybrid engine is used by default
   */
  getUseHybridByDefault(): boolean {
    return this.useHybridByDefault;
  }
  
  /**
   * Refines a solution using recursive thinking.
   *
   * @param solution Solution to refine
   * @param params Optimization parameters
   * @returns Refined solution
   */
  async refineSolution(solution: string, params?: Partial<EnhancedOptimizationRequest>): Promise<any> {
    try {
      // Create fitness function
      const fitnessFunction = this.createFitnessFunction(params as EnhancedOptimizationRequest || {
        fitnessFunction: 'default'
      });
      
      // Create constraints
      const constraints = this.createConstraints(params as EnhancedOptimizationRequest || {});
      
      // Refine solution using hybrid adapter
      const result = await this.hybridAdapter.refineSolution(solution, constraints, fitnessFunction);
      
      return {
        originalSolution: solution,
        refinedSolution: result.solution,
        fitness: result.fitness,
        thinkingRounds: result.thinkingRounds,
        improvementPercentage: ((result.fitness - await fitnessFunction(solution)) / await fitnessFunction(solution)) * 100
      };
    } catch (error) {
      this.logger.error('Error refining solution', error);
      throw error;
    }
  }
  
  /**
   * Performs a health check on the client.
   *
   * @returns Health status
   */
  async healthCheck(): Promise<any> {
    // Get base health status
    const baseStatus = await super.healthCheck();
    
    // Get hybrid adapter status
    const hybridStatus = this.hybridAdapter.getStatus();
    
    // Determine health state
    const isHealthy = baseStatus.state === HealthState.Healthy && hybridStatus.isInitialized;
    
    return {
      component: "enhanced_genetic_algorithm",
      state: isHealthy ? HealthState.Healthy : HealthState.Unhealthy,
      message: isHealthy ? "Enhanced Genetic Algorithm Client is healthy" : "Enhanced Genetic Algorithm Client is not fully operational",
      timestamp: new Date().toISOString(),
      details: {
        ...baseStatus.details,
        hybridAdapter: hybridStatus
      }
    };
  }
}