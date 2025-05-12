import { 
  EvolutionMetrics, 
  GeneticOperationStats,
  OperatorType,
  AdaptiveParameterConfig, 
  ParameterAdjustmentStrategy 
} from '../types';
import { EventEmitter } from 'events';

/**
 * Manages adaptive parameters for genetic algorithms.
 * Adjusts parameters based on evolution metrics, performance, and operator statistics.
 */
export class AdaptiveParameterManager extends EventEmitter {
  private parameters: Map<string, number> = new Map();
  private defaultParameters: Map<string, number> = new Map();
  private constraints: Map<string, { min: number; max: number }> = new Map();
  private adjustmentStrategies: Map<string, ParameterAdjustmentStrategy> = new Map();
  private parameterHistory: Map<string, number[]> = new Map();
  private metricHistory: EvolutionMetrics[] = [];
  private operationHistory: GeneticOperationStats[] = [];
  private historyLimit: number;

  /**
   * Creates a new adaptive parameter manager
   * @param config Initial configuration for adaptive parameters
   * @param historyLimit Maximum number of history entries to keep
   */
  constructor(config: AdaptiveParameterConfig[] = [], historyLimit: number = 50) {
    super();
    this.historyLimit = historyLimit;
    
    // Initialize from config
    for (const param of config) {
      this.registerParameter(
        param.name,
        param.defaultValue,
        param.min,
        param.max,
        param.adjustmentStrategy
      );
    }
  }

  /**
   * Registers a new parameter to be managed
   * @param name Parameter name
   * @param defaultValue Default parameter value
   * @param min Minimum allowed value
   * @param max Maximum allowed value
   * @param adjustmentStrategy Strategy for adjusting the parameter
   */
  public registerParameter(
    name: string,
    defaultValue: number,
    min: number,
    max: number,
    adjustmentStrategy: ParameterAdjustmentStrategy
  ): void {
    if (min >= max) {
      throw new Error(`Invalid constraints for parameter ${name}: min must be less than max`);
    }

    if (defaultValue < min || defaultValue > max) {
      throw new Error(`Default value for parameter ${name} is outside constraints`);
    }

    this.parameters.set(name, defaultValue);
    this.defaultParameters.set(name, defaultValue);
    this.constraints.set(name, { min, max });
    this.adjustmentStrategies.set(name, adjustmentStrategy);
    this.parameterHistory.set(name, [defaultValue]);
  }

  /**
   * Gets the current value of a parameter
   * @param name Parameter name
   * @returns Current parameter value
   */
  public getParameter(name: string): number {
    if (!this.parameters.has(name)) {
      throw new Error(`Parameter ${name} is not registered`);
    }
    return this.parameters.get(name)!;
  }

  /**
   * Sets the value of a parameter, respecting constraints
   * @param name Parameter name
   * @param value New parameter value
   */
  public setParameter(name: string, value: number): void {
    if (!this.parameters.has(name)) {
      throw new Error(`Parameter ${name} is not registered`);
    }

    const constraints = this.constraints.get(name)!;
    const constrainedValue = Math.max(constraints.min, Math.min(constraints.max, value));
    
    const previousValue = this.parameters.get(name);
    this.parameters.set(name, constrainedValue);
    
    // Add to history
    const history = this.parameterHistory.get(name)!;
    history.push(constrainedValue);
    
    // Trim history if needed
    if (history.length > this.historyLimit) {
      history.shift();
    }
    
    // Emit event if value changed
    if (previousValue !== constrainedValue) {
      this.emit('parameterChanged', name, constrainedValue, previousValue);
    }
  }

  /**
   * Resets a parameter to its default value
   * @param name Parameter name
   */
  public resetParameter(name: string): void {
    if (!this.parameters.has(name)) {
      throw new Error(`Parameter ${name} is not registered`);
    }
    
    const defaultValue = this.defaultParameters.get(name)!;
    this.setParameter(name, defaultValue);
  }

  /**
   * Resets all parameters to their default values
   */
  public resetAllParameters(): void {
    for (const name of this.parameters.keys()) {
      this.resetParameter(name);
    }
  }

  /**
   * Gets the parameter history for a parameter
   * @param name Parameter name
   * @returns Array of historical values
   */
  public getParameterHistory(name: string): number[] {
    if (!this.parameterHistory.has(name)) {
      throw new Error(`Parameter ${name} is not registered`);
    }
    return [...this.parameterHistory.get(name)!];
  }

  /**
   * Adds evolution metrics to history for parameter adjustment
   * @param metrics Evolution metrics
   */
  public addEvolutionMetrics(metrics: EvolutionMetrics): void {
    this.metricHistory.push(metrics);
    
    // Trim history if needed
    if (this.metricHistory.length > this.historyLimit) {
      this.metricHistory.shift();
    }
    
    // Adjust parameters based on metrics
    this.adjustParameters();
  }

  /**
   * Adds operation stats to history for parameter adjustment
   * @param stats Operation statistics
   */
  public addOperationStats(stats: GeneticOperationStats): void {
    this.operationHistory.push(stats);
    
    // Trim history if needed
    if (this.operationHistory.length > this.historyLimit) {
      this.operationHistory.shift();
    }
  }

  /**
   * Adjusts parameters based on metrics and operation history
   */
  private adjustParameters(): void {
    if (this.metricHistory.length === 0) {
      return;
    }

    // Get latest metrics
    const latestMetrics = this.metricHistory[this.metricHistory.length - 1];
    
    // Calculate metrics for adjustment
    const diversityScore = latestMetrics.diversityScore;
    const convergenceRate = latestMetrics.convergenceRate;
    const generationsSinceImprovement = latestMetrics.generationsSinceImprovement;
    
    // Calculate operator statistics
    const operatorStats = this.calculateOperatorStats();
    
    // Context for adjustment strategies
    const context = {
      metrics: latestMetrics,
      metricHistory: this.metricHistory,
      operationHistory: this.operationHistory,
      operatorStats,
      diversity: diversityScore,
      convergence: convergenceRate,
      stagnation: generationsSinceImprovement
    };
    
    // Apply adjustment strategies to each parameter
    for (const [name, strategy] of this.adjustmentStrategies.entries()) {
      const currentValue = this.parameters.get(name)!;
      const newValue = strategy(currentValue, context);
      
      if (currentValue !== newValue) {
        this.setParameter(name, newValue);
      }
    }
  }

  /**
   * Calculates statistics for each operator type
   * @returns Statistics by operator type
   */
  private calculateOperatorStats(): Record<OperatorType, { 
    successRate: number; 
    improvementRate: number;
  }> {
    const result: Record<OperatorType, { 
      successRate: number; 
      improvementRate: number;
    }> = {
      selection: { successRate: 0, improvementRate: 0 },
      crossover: { successRate: 0, improvementRate: 0 },
      mutation: { successRate: 0, improvementRate: 0 }
    };
    
    // Count operations and successes by type
    const typeCounts: Record<OperatorType, number> = {
      selection: 0,
      crossover: 0,
      mutation: 0
    };
    
    const typeSuccesses: Record<OperatorType, number> = {
      selection: 0,
      crossover: 0,
      mutation: 0
    };
    
    const typeImprovements: Record<OperatorType, number> = {
      selection: 0,
      crossover: 0,
      mutation: 0
    };
    
    // Process operation history
    for (const stats of this.operationHistory) {
      const type = stats.operatorType;
      typeCounts[type] += stats.applyCount;
      typeSuccesses[type] += stats.successCount;
      typeImprovements[type] += stats.fitnessImprovement;
    }
    
    // Calculate rates
    for (const type of Object.keys(result) as OperatorType[]) {
      result[type].successRate = typeCounts[type] > 0 
        ? typeSuccesses[type] / typeCounts[type] 
        : 0;
        
      result[type].improvementRate = typeCounts[type] > 0 
        ? typeImprovements[type] / typeCounts[type] 
        : 0;
    }
    
    return result;
  }

  /**
   * Gets a snapshot of all current parameter values
   * @returns Record mapping parameter names to values
   */
  public getParameterSnapshot(): Record<string, number> {
    const snapshot: Record<string, number> = {};
    
    for (const [name, value] of this.parameters.entries()) {
      snapshot[name] = value;
    }
    
    return snapshot;
  }

  /**
   * Creates default adjustment strategies
   */
  public static createDefaultStrategies(): Record<string, ParameterAdjustmentStrategy> {
    return {
      /**
       * Default strategy for mutation rate
       * Increases when diversity is low or stagnation is high
       * Decreases when diversity is high and progress is good
       */
      mutationRate: (current, context) => {
        const { diversity, stagnation } = context;
        
        // Increase when diversity is low or stagnation is high
        if (diversity < 0.3 || stagnation > 5) {
          return Math.min(current * 1.5, 0.8);
        }
        
        // Decrease when diversity is high and no stagnation
        if (diversity > 0.7 && stagnation < 2) {
          return Math.max(current * 0.8, 0.01);
        }
        
        return current;
      },
      
      /**
       * Default strategy for crossover rate
       * Increases when convergence is high to exploit good solutions
       * Decreases when diversity is low to allow more mutation
       */
      crossoverRate: (current, context) => {
        const { diversity, convergence } = context;
        
        // Increase when convergence is high to exploit good solutions
        if (convergence > 0.6 && diversity > 0.4) {
          return Math.min(current * 1.1, 0.95);
        }
        
        // Decrease when diversity is low to allow more mutation
        if (diversity < 0.3) {
          return Math.max(current * 0.9, 0.5);
        }
        
        return current;
      },
      
      /**
       * Default strategy for tournament size
       * Increases when convergence is low to focus on best solutions
       * Decreases when convergence is high to maintain diversity
       */
      tournamentSize: (current, context) => {
        const { convergence, stagnation } = context;
        
        // Increase when convergence is low to focus on best solutions
        if (convergence < 0.3 && stagnation < 3) {
          return Math.min(current + 1, 7);
        }
        
        // Decrease when convergence is high to maintain diversity
        if (convergence > 0.7 || stagnation > 5) {
          return Math.max(current - 1, 2);
        }
        
        return current;
      },
      
      /**
       * Default strategy for elitism count
       * Increases when good solutions are found (high convergence)
       * Decreases when diversity is too low
       */
      elitismCount: (current, context) => {
        const { convergence, diversity, metrics } = context;
        const populationSize = metrics.populationSize;
        const maxElites = Math.max(1, Math.floor(populationSize * 0.1));
        
        // Increase when good solutions are found (high convergence)
        if (convergence > 0.7 && diversity > 0.3) {
          return Math.min(current + 1, maxElites);
        }
        
        // Decrease when diversity is too low
        if (diversity < 0.2) {
          return Math.max(current - 1, 1);
        }
        
        return current;
      },
      
      /**
       * Default strategy for population size
       * Increases when complexity increases or diversity is low
       * Decreases when convergence is high and stable
       */
      populationSize: (current, context) => {
        const { convergence, diversity, stagnation } = context;
        
        // Increase when diversity is very low
        if (diversity < 0.15) {
          return Math.min(current * 1.5, 500);
        }
        
        // Decrease when convergence is high and stable
        if (convergence > 0.8 && stagnation < 3 && diversity > 0.3) {
          return Math.max(current * 0.8, 20);
        }
        
        return current;
      }
    };
  }
}