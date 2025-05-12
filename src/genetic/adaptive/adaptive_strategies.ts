import { 
  ParameterAdjustmentStrategy, 
  AdaptiveStrategyContext,
  OperatorType
} from '../types';

/**
 * Collection of advanced adaptive strategies for genetic algorithm parameters.
 * These strategies adjust parameters based on population performance,
 * diversity, convergence, and historical trends.
 */
export class AdaptiveStrategies {
  /**
   * Creates a strategy for adapting mutation rate
   * @param options Strategy configuration options
   * @returns A parameter adjustment strategy
   */
  public static mutationRateStrategy(options: {
    minRate?: number;
    maxRate?: number;
    diversityThresholdLow?: number;
    diversityThresholdHigh?: number;
    stagnationThreshold?: number;
    increaseRate?: number;
    decreaseRate?: number;
  } = {}): ParameterAdjustmentStrategy {
    // Default options
    const {
      minRate = 0.01,
      maxRate = 0.8,
      diversityThresholdLow = 0.3,
      diversityThresholdHigh = 0.7,
      stagnationThreshold = 5,
      increaseRate = 1.5,
      decreaseRate = 0.8
    } = options;

    return (current: number, context: AdaptiveStrategyContext): number => {
      const { diversity, stagnation, operatorStats } = context;
      
      // Get mutation operator statistics
      const mutationStats = operatorStats.mutation;
      
      // Basic strategy: adjust based on diversity and stagnation
      // Increase when diversity is low or stagnation is high
      if (diversity < diversityThresholdLow || stagnation > stagnationThreshold) {
        return Math.min(current * increaseRate, maxRate);
      }
      
      // Decrease when diversity is high and no stagnation
      if (diversity > diversityThresholdHigh && stagnation < stagnationThreshold / 2) {
        return Math.max(current * decreaseRate, minRate);
      }
      
      // Advanced strategy: adjust based on mutation effectiveness
      if (mutationStats.successRate < 0.2) {
        // Low success rate - increase to explore more
        return Math.min(current * 1.2, maxRate);
      } else if (mutationStats.successRate > 0.6) {
        // High success rate - mutation is working well, maintain or slightly increase
        return Math.min(current * 1.05, maxRate);
      }
      
      // Look at improvement trends for fine tuning
      if (mutationStats.improvementRate > 0.4) {
        // Strong improvements - slight increase to continue trend
        return Math.min(current * 1.1, maxRate);
      } else if (mutationStats.improvementRate < 0.1 && diversity > 0.4) {
        // Low improvement despite good diversity - slight decrease
        return Math.max(current * 0.95, minRate);
      }
      
      // Default: keep current rate
      return current;
    };
  }

  /**
   * Creates a strategy for adapting crossover rate
   * @param options Strategy configuration options
   * @returns A parameter adjustment strategy
   */
  public static crossoverRateStrategy(options: {
    minRate?: number;
    maxRate?: number;
    convergenceThresholdLow?: number;
    convergenceThresholdHigh?: number;
    diversityThreshold?: number;
    increaseRate?: number;
    decreaseRate?: number;
  } = {}): ParameterAdjustmentStrategy {
    // Default options
    const {
      minRate = 0.5,
      maxRate = 0.95,
      convergenceThresholdLow = 0.3,
      convergenceThresholdHigh = 0.7,
      diversityThreshold = 0.3,
      increaseRate = 1.1,
      decreaseRate = 0.9
    } = options;

    return (current: number, context: AdaptiveStrategyContext): number => {
      const { diversity, convergence, operatorStats } = context;
      
      // Get crossover operator statistics
      const crossoverStats = operatorStats.crossover;
      
      // Basic strategy: adjust based on convergence and diversity
      // Increase when convergence is high to exploit good solutions
      if (convergence > convergenceThresholdHigh && diversity > diversityThreshold) {
        return Math.min(current * increaseRate, maxRate);
      }
      
      // Decrease when diversity is low to allow more mutation
      if (diversity < diversityThreshold) {
        return Math.max(current * decreaseRate, minRate);
      }
      
      // Advanced strategy: adjust based on operator effectiveness
      if (crossoverStats.successRate > 0.6) {
        // High success rate - crossover is working well, increase
        return Math.min(current * 1.05, maxRate);
      } else if (crossoverStats.successRate < 0.2 && diversity > 0.4) {
        // Low success rate despite good diversity - decrease
        return Math.max(current * 0.95, minRate);
      }
      
      // Look at relative performance compared to mutation
      if (crossoverStats.improvementRate > operatorStats.mutation.improvementRate) {
        // Crossover more effective than mutation - increase
        return Math.min(current * 1.05, maxRate);
      } else if (crossoverStats.improvementRate < operatorStats.mutation.improvementRate * 0.5) {
        // Mutation much more effective than crossover - decrease
        return Math.max(current * 0.95, minRate);
      }
      
      // Default: keep current rate
      return current;
    };
  }

  /**
   * Creates a strategy for adapting tournament size
   * @param options Strategy configuration options
   * @returns A parameter adjustment strategy
   */
  public static tournamentSizeStrategy(options: {
    minSize?: number;
    maxSize?: number;
    convergenceThresholdLow?: number;
    convergenceThresholdHigh?: number;
    stagnationThreshold?: number;
  } = {}): ParameterAdjustmentStrategy {
    // Default options
    const {
      minSize = 2,
      maxSize = 7,
      convergenceThresholdLow = 0.3,
      convergenceThresholdHigh = 0.7,
      stagnationThreshold = 5
    } = options;

    return (current: number, context: AdaptiveStrategyContext): number => {
      const { convergence, stagnation, diversity, metrics } = context;
      
      // Increase selection pressure (larger tournament) when:
      // - Convergence is low (need to focus more on good solutions)
      // - Stagnation is low (not stuck yet)
      if (convergence < convergenceThresholdLow && stagnation < stagnationThreshold / 2) {
        return Math.min(Math.ceil(current + 1), maxSize);
      }
      
      // Decrease selection pressure (smaller tournament) when:
      // - Convergence is high (already focusing on good solutions)
      // - Stagnation is high (might be stuck in local optimum)
      if (convergence > convergenceThresholdHigh || stagnation > stagnationThreshold) {
        return Math.max(Math.floor(current - 1), minSize);
      }
      
      // Advanced strategy: adjust based on current generation
      const currentGeneration = metrics.generation;
      const maxGenerations = 100; // Estimate
      
      // Early generations: lower pressure to explore
      if (currentGeneration < maxGenerations * 0.2 && current > minSize + 1) {
        return current - 1;
      }
      
      // Later generations: higher pressure to exploit
      if (currentGeneration > maxGenerations * 0.7 && 
          diversity > 0.3 && 
          current < maxSize - 1) {
        return current + 1;
      }
      
      // Default: keep current size
      return current;
    };
  }

  /**
   * Creates a strategy for adapting population size
   * @param options Strategy configuration options
   * @returns A parameter adjustment strategy
   */
  public static populationSizeStrategy(options: {
    minSize?: number;
    maxSize?: number;
    diversityThreshold?: number;
    stagnationThreshold?: number;
    convergenceThreshold?: number;
    adjustmentInterval?: number;
  } = {}): ParameterAdjustmentStrategy {
    // Default options
    const {
      minSize = 10,
      maxSize = 500,
      diversityThreshold = 0.2,
      stagnationThreshold = 5,
      convergenceThreshold = 0.8,
      adjustmentInterval = 5
    } = options;

    let lastAdjustmentGeneration = 0;

    return (current: number, context: AdaptiveStrategyContext): number => {
      const { diversity, stagnation, convergence, metrics } = context;
      const currentGeneration = metrics.generation;
      
      // Only adjust population size periodically to allow adaptation to take effect
      if (currentGeneration - lastAdjustmentGeneration < adjustmentInterval) {
        return current;
      }
      
      lastAdjustmentGeneration = currentGeneration;
      
      // Increase population size when:
      // - Diversity is very low (need more variation)
      // - Stagnation is high (might need more exploration)
      if (diversity < diversityThreshold || stagnation > stagnationThreshold) {
        return Math.min(Math.round(current * 1.3), maxSize);
      }
      
      // Decrease population size when:
      // - Convergence is high and diversity is ok (can focus on fewer solutions)
      // - No stagnation (making progress)
      if (convergence > convergenceThreshold && 
          diversity > diversityThreshold * 1.5 && 
          stagnation < stagnationThreshold / 2) {
        return Math.max(Math.round(current * 0.8), minSize);
      }
      
      // Advanced strategy: balance computational cost vs. performance
      const operatorStats = context.operatorStats;
      const totalImprovementRate = (
        operatorStats.selection.improvementRate +
        operatorStats.crossover.improvementRate +
        operatorStats.mutation.improvementRate
      );
      
      // If improvement rate is low despite good population size, increase
      if (totalImprovementRate < 0.1 && current < maxSize / 2) {
        return Math.min(Math.round(current * 1.2), maxSize);
      }
      
      // If improvement rate is high with small population, try to optimize by reducing
      if (totalImprovementRate > 0.5 && current > minSize * 2) {
        return Math.max(Math.round(current * 0.9), minSize);
      }
      
      // Default: keep current size
      return current;
    };
  }

  /**
   * Creates a strategy for adapting elitism count
   * @param options Strategy configuration options
   * @returns A parameter adjustment strategy
   */
  public static elitismCountStrategy(options: {
    minCount?: number;
    maxRatio?: number;
    diversityThreshold?: number;
    convergenceThreshold?: number;
  } = {}): ParameterAdjustmentStrategy {
    // Default options
    const {
      minCount = 1,
      maxRatio = 0.1, // Max percentage of population to preserve as elites
      diversityThreshold = 0.2,
      convergenceThreshold = 0.7
    } = options;

    return (current: number, context: AdaptiveStrategyContext): number => {
      const { diversity, convergence, metrics } = context;
      const populationSize = metrics.populationSize;
      const maxElites = Math.max(minCount, Math.floor(populationSize * maxRatio));
      
      // Increase elitism when:
      // - High convergence (good solutions found)
      // - Sufficient diversity (not causing premature convergence)
      if (convergence > convergenceThreshold && diversity > diversityThreshold) {
        return Math.min(current + 1, maxElites);
      }
      
      // Decrease elitism when:
      // - Low diversity (need more exploration)
      if (diversity < diversityThreshold && current > minCount) {
        return current - 1;
      }
      
      // Dynamic based on progress
      if (metrics.generationsSinceImprovement > 3 && current > minCount) {
        // Reducing elitism to avoid local optima
        return Math.max(current - 1, minCount);
      }
      
      // Default: keep current count
      return current;
    };
  }

  /**
   * Creates a strategy for adapting selection method weights
   * Different selection methods work better at different stages of evolution
   * @returns A parameter adjustment strategy
   */
  public static selectionMethodWeightStrategy(): Record<string, ParameterAdjustmentStrategy> {
    return {
      tournamentWeight: (current, context) => {
        const { convergence, diversity } = context;
        
        // Tournament works well when moderate selection pressure is needed
        if (convergence < 0.5 && convergence > 0.2) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      rouletteWeight: (current, context) => {
        const { diversity, stagnation } = context;
        
        // Roulette works well when fitness differences should be emphasized
        if (diversity > 0.5 && stagnation < 3) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      rankWeight: (current, context) => {
        const { convergence, stagnation } = context;
        
        // Rank selection is good for avoiding premature convergence
        if (convergence > 0.7 || stagnation > 5) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      steadyStateWeight: (current, context) => {
        const { convergence, diversity } = context;
        
        // Steady state is good for late-stage optimization
        if (convergence > 0.8 && diversity < 0.3) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      }
    };
  }

  /**
   * Creates a strategy for adapting crossover method weights
   * Different crossover methods work better for different problem types
   * @returns A parameter adjustment strategy
   */
  public static crossoverMethodWeightStrategy(): Record<string, ParameterAdjustmentStrategy> {
    return {
      singlePointWeight: (current, context) => {
        const { convergence } = context;
        
        // Single-point works well for simpler problems and late-stage optimization
        if (convergence > 0.7) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      multiPointWeight: (current, context) => {
        const { diversity, convergence } = context;
        
        // Multi-point works well for problems with independent subcomponents
        if (diversity > 0.4 && convergence < 0.6) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      uniformWeight: (current, context) => {
        const { diversity, stagnation } = context;
        
        // Uniform works well when high disruption is needed
        if (diversity < 0.3 || stagnation > 5) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      semanticWeight: (current, context) => {
        const { convergence, stagnation } = context;
        
        // Semantic works well for preserving meaningful structures
        if (convergence > 0.5 && stagnation > 3) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      }
    };
  }

  /**
   * Creates a strategy for adapting mutation method weights
   * Different mutation methods work better at different stages
   * @returns A parameter adjustment strategy
   */
  public static mutationMethodWeightStrategy(): Record<string, ParameterAdjustmentStrategy> {
    return {
      pointWeight: (current, context) => {
        const { convergence } = context;
        
        // Point mutation works well for fine-tuning
        if (convergence > 0.7) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      swapWeight: (current, context) => {
        const { diversity, stagnation } = context;
        
        // Swap mutation works well for reordering
        if (diversity < 0.4 && stagnation > 2) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      insertWeight: (current, context) => {
        const { diversity, convergence } = context;
        
        // Insert mutation works well for growing solutions
        if (diversity < 0.3 && convergence < 0.5) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      deleteWeight: (current, context) => {
        const { convergence, stagnation } = context;
        
        // Delete mutation works well for removing bloat
        if (convergence > 0.6 && stagnation > 3) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      scrambleWeight: (current, context) => {
        const { diversity, stagnation } = context;
        
        // Scramble mutation works well for breaking patterns
        if (diversity < 0.2 || stagnation > 5) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      },
      
      patternWeight: (current, context) => {
        const { convergence } = context;
        
        // Pattern-based mutation works well with domain knowledge
        if (convergence > 0.4) {
          return Math.min(current * 1.2, 1.0);
        }
        
        return Math.max(current * 0.9, 0.1);
      }
    };
  }

  /**
   * Creates a self-tuning strategy that adjusts parameters based on their effectiveness
   * @param parameterName Name of the parameter being adjusted
   * @param options Strategy configuration options
   * @returns A parameter adjustment strategy
   */
  public static selfTuningStrategy(
    parameterName: string,
    options: {
      minValue?: number;
      maxValue?: number;
      exploreFactor?: number;
      exploitFactor?: number;
      adaptationRate?: number;
    } = {}
  ): ParameterAdjustmentStrategy {
    // Default options
    const {
      minValue = 0.01,
      maxValue = 1.0,
      exploreFactor = 0.2,
      exploitFactor = 0.1,
      adaptationRate = 0.05
    } = options;

    // Track effectiveness of parameter changes
    const recentResults: { value: number; fitness: number }[] = [];
    let lastChange = 0; // Generation when parameter was last changed
    let lastDirection = 0; // Direction of last change: -1 (decrease), 0 (none), 1 (increase)

    return (current: number, context: AdaptiveStrategyContext): number => {
      const { metrics, metricHistory } = context;
      const currentGeneration = metrics.generation;
      
      // Wait a few generations between changes to observe effect
      if (currentGeneration - lastChange < 3) {
        return current;
      }
      
      // Record result with current parameter value
      recentResults.push({
        value: current,
        fitness: metrics.bestFitness
      });
      
      // Keep only recent results
      if (recentResults.length > 5) {
        recentResults.shift();
      }
      
      // Not enough data to make intelligent decision
      if (recentResults.length < 2) {
        // Start with random exploration
        const randomChange = (Math.random() > 0.5 ? 1 : -1) * exploreFactor;
        lastChange = currentGeneration;
        lastDirection = randomChange > 0 ? 1 : -1;
        return Math.max(minValue, Math.min(maxValue, current + randomChange * current));
      }
      
      // Analyze effectiveness of recent parameter values
      recentResults.sort((a, b) => b.fitness - a.fitness);
      const bestValue = recentResults[0].value;
      
      // If current value is best, make smaller exploration around it
      if (Math.abs(bestValue - current) < 0.0001) {
        // Small random change for continued exploration
        const randomChange = (Math.random() > 0.5 ? 1 : -1) * exploreFactor * 0.5;
        lastChange = currentGeneration;
        lastDirection = randomChange > 0 ? 1 : -1;
        return Math.max(minValue, Math.min(maxValue, current + randomChange * current));
      } else {
        // Move toward best value we've seen
        const direction = bestValue > current ? 1 : -1;
        
        // If we're changing direction, reduce step size
        const stepSize = direction === lastDirection ? 
          exploitFactor : 
          exploitFactor * 0.5;
        
        lastChange = currentGeneration;
        lastDirection = direction;
        
        // Move toward best known value at adaptive rate
        const distance = Math.abs(bestValue - current);
        const step = Math.min(distance, current * stepSize);
        
        return Math.max(minValue, Math.min(maxValue, current + direction * step));
      }
    };
  }

  /**
   * Creates a time-based strategy that adjusts parameters based on evolution stage
   * @param options Strategy configuration options
   * @returns A parameter adjustment strategy
   */
  public static timeBasedStrategy(
    options: {
      earlyValue?: number;
      midValue?: number;
      lateValue?: number;
      earlyPhase?: number;
      latePhase?: number;
      maxGenerations?: number;
    } = {}
  ): ParameterAdjustmentStrategy {
    // Default options
    const {
      earlyValue = 0.0,
      midValue = 0.0,
      lateValue = 0.0,
      earlyPhase = 0.3, // First 30% of generations
      latePhase = 0.7,  // Last 30% of generations
      maxGenerations = 100
    } = options;

    return (current: number, context: AdaptiveStrategyContext): number => {
      const { metrics } = context;
      const currentGeneration = metrics.generation;
      
      // Calculate relative position in evolution
      const relativePosition = Math.min(1.0, currentGeneration / maxGenerations);
      
      // Early phase
      if (relativePosition < earlyPhase) {
        return earlyValue;
      }
      
      // Late phase
      if (relativePosition > latePhase) {
        return lateValue;
      }
      
      // Mid phase - linear interpolation
      const midPhasePosition = (relativePosition - earlyPhase) / (latePhase - earlyPhase);
      return midValue;
    };
  }
}