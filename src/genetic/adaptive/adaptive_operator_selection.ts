import { 
  AdaptiveOperatorConfig, 
  OperatorSelectionConfig,
  GeneticOperationStats, 
  OperatorType
} from '../types';

/**
 * Adaptive Operator Selection (AOS) system.
 * Dynamically adjusts the probability of selecting different operators
 * based on their performance during evolution.
 */
export class AdaptiveOperatorSelection {
  private operators: Map<string, AdaptiveOperatorConfig> = new Map();
  private operatorPerformance: Map<string, {
    successRate: number;
    improvementRate: number;
    appliedCount: number;
    recentRewards: number[];
    recentResults: number[];
  }> = new Map();
  
  private config: OperatorSelectionConfig;
  private counter: number = 0;
  
  /**
   * Creates a new adaptive operator selection system
   * @param operators Array of operator configurations
   * @param config Configuration for the operator selection system
   */
  constructor(
    operators: AdaptiveOperatorConfig[],
    config: Partial<OperatorSelectionConfig> = {}
  ) {
    // Set default configuration
    this.config = {
      method: 'adaptive',
      creditAssignment: 'improvement',
      updateFrequency: 5,
      learningRate: 0.1,
      ...config
    };
    
    // Initialize operators
    for (const operator of operators) {
      this.operators.set(operator.name, operator);
      this.operatorPerformance.set(operator.name, {
        successRate: 0,
        improvementRate: 0,
        appliedCount: 0,
        recentRewards: [],
        recentResults: []
      });
    }
  }

  /**
   * Selects an operator based on the current selection method
   * @param type Type of operator to select
   * @returns Selected operator name
   */
  public selectOperator(type: OperatorType): string {
    // Filter operators by type
    const typeOperators = Array.from(this.operators.values())
      .filter(op => op.type === type);
    
    if (typeOperators.length === 0) {
      throw new Error(`No operators of type ${type} registered`);
    }
    
    // If only one operator, return it
    if (typeOperators.length === 1) {
      return typeOperators[0].name;
    }
    
    // Select based on method
    switch (this.config.method) {
      case 'probability':
        return this.selectByProbability(typeOperators);
      case 'roulette':
        return this.selectByRoulette(typeOperators);
      case 'adaptive':
        return this.selectAdaptively(typeOperators);
      default:
        return this.selectByProbability(typeOperators);
    }
  }

  /**
   * Selects an operator based on fixed probabilities
   * @param operators Array of operator configurations
   * @returns Selected operator name
   */
  private selectByProbability(operators: AdaptiveOperatorConfig[]): string {
    const randomValue = Math.random();
    let cumulativeProbability = 0;
    
    for (const operator of operators) {
      cumulativeProbability += operator.initialProbability;
      if (randomValue < cumulativeProbability) {
        return operator.name;
      }
    }
    
    // If we get here, return the last operator
    return operators[operators.length - 1].name;
  }

  /**
   * Selects an operator using roulette wheel selection based on performance
   * @param operators Array of operator configurations
   * @returns Selected operator name
   */
  private selectByRoulette(operators: AdaptiveOperatorConfig[]): string {
    let totalWeight = 0;
    const weights: Record<string, number> = {};
    
    // Calculate weights based on operator performance
    for (const operator of operators) {
      const performance = this.operatorPerformance.get(operator.name)!;
      
      // Weight based on success rate and application count
      let weight = operator.initialProbability;
      
      if (performance.appliedCount > 0) {
        if (this.config.creditAssignment === 'improvement') {
          weight = performance.improvementRate;
        } else {
          weight = performance.successRate;
        }
        
        // Ensure minimum probability
        weight = Math.max(weight, operator.minProbability);
      }
      
      weights[operator.name] = weight;
      totalWeight += weight;
    }
    
    // Normalize weights
    if (totalWeight > 0) {
      for (const name of Object.keys(weights)) {
        weights[name] /= totalWeight;
      }
    } else {
      // If no operator has been applied yet, use initial probabilities
      for (const operator of operators) {
        weights[operator.name] = operator.initialProbability;
        totalWeight += operator.initialProbability;
      }
      
      // Normalize
      for (const name of Object.keys(weights)) {
        weights[name] /= totalWeight;
      }
    }
    
    // Roulette wheel selection
    const randomValue = Math.random();
    let cumulativeProbability = 0;
    
    for (const operator of operators) {
      cumulativeProbability += weights[operator.name];
      if (randomValue < cumulativeProbability) {
        return operator.name;
      }
    }
    
    // If we get here, return the last operator
    return operators[operators.length - 1].name;
  }

  /**
   * Selects an operator using adaptive pursuit algorithm
   * @param operators Array of operator configurations
   * @returns Selected operator name
   */
  private selectAdaptively(operators: AdaptiveOperatorConfig[]): string {
    const probabilities: Record<string, number> = {};
    
    // First check if we have enough data for adaptive selection
    let enoughData = true;
    for (const operator of operators) {
      const performance = this.operatorPerformance.get(operator.name)!;
      
      if (performance.appliedCount < 5) {
        enoughData = false;
        break;
      }
    }
    
    // If not enough data, use exploration phase with uniform probabilities
    if (!enoughData) {
      // Initialize with equal probabilities during exploration
      const equalProb = 1.0 / operators.length;
      
      for (const operator of operators) {
        probabilities[operator.name] = equalProb;
      }
    } else {
      // Get latest rewards for each operator
      const rewards: Record<string, number> = {};
      let bestReward = -Infinity;
      let bestOperator = '';
      
      for (const operator of operators) {
        const performance = this.operatorPerformance.get(operator.name)!;
        
        // Calculate reward based on credit assignment method
        let reward = 0;
        
        if (this.config.creditAssignment === 'improvement') {
          // Average of recent improvements
          const recentRewards = performance.recentRewards;
          reward = recentRewards.length > 0 ? 
            recentRewards.reduce((acc, val) => acc + val, 0) / recentRewards.length : 
            0;
        } else {
          // Average of recent success rates
          const recentResults = performance.recentResults;
          reward = recentResults.length > 0 ? 
            recentResults.reduce((acc, val) => acc + val, 0) / recentResults.length : 
            0;
        }
        
        rewards[operator.name] = reward;
        
        // Track best operator
        if (reward > bestReward) {
          bestReward = reward;
          bestOperator = operator.name;
        }
      }
      
      // Update probabilities using adaptive pursuit
      // Get current probabilities
      for (const operator of operators) {
        const config = this.operators.get(operator.name)!;
        
        // Current probability is either stored or initial
        let currentProb = probabilities[operator.name];
        if (currentProb === undefined) {
          currentProb = config.initialProbability;
        }
        
        // Target probability
        const pMax = config.maxProbability;
        const pMin = config.minProbability;
        const targetProb = operator.name === bestOperator ? pMax : pMin;
        
        // Update rule: p(t+1) = p(t) + β(target - p(t))
        const beta = this.config.learningRate;
        probabilities[operator.name] = currentProb + beta * (targetProb - currentProb);
      }
      
      // Normalize probabilities
      let totalProb = 0;
      for (const prob of Object.values(probabilities)) {
        totalProb += prob;
      }
      
      for (const name of Object.keys(probabilities)) {
        probabilities[name] /= totalProb;
      }
    }
    
    // Select using updated probabilities
    const randomValue = Math.random();
    let cumulativeProbability = 0;
    
    for (const operator of operators) {
      cumulativeProbability += probabilities[operator.name];
      if (randomValue < cumulativeProbability) {
        return operator.name;
      }
    }
    
    // If we get here, return the last operator
    return operators[operators.length - 1].name;
  }

  /**
   * Updates operator performance statistics after application
   * @param stats Operation statistics
   */
  public updateOperatorPerformance(stats: GeneticOperationStats): void {
    const { operatorType, operatorName, applyCount, successCount, fitnessImprovement } = stats;
    
    // Check if operator exists
    if (!this.operators.has(operatorName)) {
      console.warn(`Unknown operator: ${operatorName}`);
      return;
    }
    
    // Get performance data
    const performance = this.operatorPerformance.get(operatorName)!;
    
    // Update statistics
    performance.appliedCount += applyCount;
    
    // Success rate
    const successRate = applyCount > 0 ? successCount / applyCount : 0;
    performance.successRate = 
      (performance.successRate * (performance.appliedCount - applyCount) + 
       successRate * applyCount) / 
      performance.appliedCount;
    
    // Improvement rate
    const improvementRate = applyCount > 0 ? fitnessImprovement / applyCount : 0;
    performance.improvementRate = 
      (performance.improvementRate * (performance.appliedCount - applyCount) + 
       improvementRate * applyCount) / 
      performance.appliedCount;
    
    // Add to recent results history
    performance.recentResults.push(successRate);
    performance.recentRewards.push(improvementRate);
    
    // Keep only recent history
    const maxHistory = 10;
    if (performance.recentResults.length > maxHistory) {
      performance.recentResults.shift();
    }
    if (performance.recentRewards.length > maxHistory) {
      performance.recentRewards.shift();
    }
    
    // Increment counter and update selection probabilities if needed
    this.counter++;
    if (this.counter >= this.config.updateFrequency) {
      this.updateSelectionProbabilities();
      this.counter = 0;
    }
  }

  /**
   * Updates operator selection probabilities based on performance
   */
  private updateSelectionProbabilities(): void {
    // Only needed for probability-based selection
    if (this.config.method !== 'probability') {
      return;
    }
    
    // Group operators by type
    const operatorsByType: Record<OperatorType, AdaptiveOperatorConfig[]> = {
      selection: [],
      crossover: [],
      mutation: []
    };
    
    for (const operator of this.operators.values()) {
      operatorsByType[operator.type].push(operator);
    }
    
    // Update probabilities for each type
    for (const type of Object.keys(operatorsByType) as OperatorType[]) {
      const typeOperators = operatorsByType[type];
      
      if (typeOperators.length <= 1) {
        continue;
      }
      
      // Calculate total performance for normalization
      let totalPerformance = 0;
      const performances: Record<string, number> = {};
      
      for (const operator of typeOperators) {
        const performance = this.operatorPerformance.get(operator.name)!;
        
        // Skip operators that haven't been applied yet
        if (performance.appliedCount === 0) {
          performances[operator.name] = operator.initialProbability;
          totalPerformance += operator.initialProbability;
          continue;
        }
        
        // Calculate performance metric
        let metric = 0;
        if (this.config.creditAssignment === 'improvement') {
          metric = performance.improvementRate;
        } else {
          metric = performance.successRate;
        }
        
        // Apply minimum probability
        metric = Math.max(metric, operator.minProbability);
        
        performances[operator.name] = metric;
        totalPerformance += metric;
      }
      
      // Normalize and update
      if (totalPerformance > 0) {
        for (const operator of typeOperators) {
          const normalizedPerformance = performances[operator.name] / totalPerformance;
          
          // Update operator probability with learning rate
          const currentProb = operator.initialProbability;
          const newProb = currentProb + 
            this.config.learningRate * (normalizedPerformance - currentProb);
          
          // Ensure bounds
          const boundedProb = Math.max(
            operator.minProbability,
            Math.min(operator.maxProbability, newProb)
          );
          
          // Update operator
          operator.initialProbability = boundedProb;
        }
      }
    }
  }

  /**
   * Gets performance statistics for all operators
   * @returns Performance statistics for each operator
   */
  public getOperatorPerformanceStats(): Record<string, {
    type: OperatorType;
    successRate: number;
    improvementRate: number;
    appliedCount: number;
    probability: number;
  }> {
    const result: Record<string, any> = {};
    
    for (const [name, operator] of this.operators.entries()) {
      const performance = this.operatorPerformance.get(name)!;
      
      result[name] = {
        type: operator.type,
        successRate: performance.successRate,
        improvementRate: performance.improvementRate,
        appliedCount: performance.appliedCount,
        probability: operator.initialProbability
      };
    }
    
    return result;
  }
  
  /**
   * Creates configurations for standard genetic operators
   * @returns Array of operator configurations
   */
  public static createStandardOperators(): AdaptiveOperatorConfig[] {
    return [
      // Selection operators
      {
        name: 'tournament',
        type: 'selection',
        initialProbability: 0.4,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'roulette',
        type: 'selection',
        initialProbability: 0.3,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'rank',
        type: 'selection',
        initialProbability: 0.2,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'steady-state',
        type: 'selection',
        initialProbability: 0.1,
        minProbability: 0.05,
        maxProbability: 0.5
      },
      
      // Crossover operators
      {
        name: 'single-point',
        type: 'crossover',
        initialProbability: 0.3,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'multi-point',
        type: 'crossover',
        initialProbability: 0.3,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'uniform',
        type: 'crossover',
        initialProbability: 0.2,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'arithmetic',
        type: 'crossover',
        initialProbability: 0.1,
        minProbability: 0.05,
        maxProbability: 0.5
      },
      {
        name: 'semantic',
        type: 'crossover',
        initialProbability: 0.1,
        minProbability: 0.05,
        maxProbability: 0.5
      },
      
      // Mutation operators
      {
        name: 'point',
        type: 'mutation',
        initialProbability: 0.3,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'swap',
        type: 'mutation',
        initialProbability: 0.2,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'insert',
        type: 'mutation',
        initialProbability: 0.1,
        minProbability: 0.05,
        maxProbability: 0.5
      },
      {
        name: 'delete',
        type: 'mutation',
        initialProbability: 0.1,
        minProbability: 0.05,
        maxProbability: 0.5
      },
      {
        name: 'scramble',
        type: 'mutation',
        initialProbability: 0.2,
        minProbability: 0.1,
        maxProbability: 0.7
      },
      {
        name: 'pattern',
        type: 'mutation',
        initialProbability: 0.1,
        minProbability: 0.05,
        maxProbability: 0.7
      }
    ];
  }
}