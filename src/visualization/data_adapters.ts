import {
  Solution,
  Population,
  EvolutionMetrics,
  GeneticOperationStats,
  OperatorType,
  RecursiveThinkingStats
} from '../genetic/types';

/**
 * Data adapter for converting genetic algorithm data to visualization-friendly formats
 * Processes raw genetic algorithm data and transforms it into structures
 * that can be easily consumed by visualization components
 */
export class GeneticVisualizationAdapter {
  private historyData: EvolutionMetrics[] = [];
  private operationsHistory: GeneticOperationStats[] = [];
  private populationHistory: Population[] = [];
  private bestSolutionHistory: Solution[] = [];
  private maxHistoryLength: number;

  /**
   * @param maxHistoryLength - Maximum number of historical data points to store (default 100)
   */
  constructor(maxHistoryLength: number = 100) {
    this.maxHistoryLength = maxHistoryLength;
  }

  /**
   * Add evolution metrics to history
   * @param metrics - Evolution metrics from current generation
   */
  public addEvolutionMetrics(metrics: EvolutionMetrics): void {
    this.historyData.push(metrics);
    
    // Trim history if needed
    if (this.historyData.length > this.maxHistoryLength) {
      this.historyData.shift();
    }
  }

  /**
   * Add operation stats to history
   * @param stats - Genetic operation statistics
   */
  public addOperationStats(stats: GeneticOperationStats): void {
    this.operationsHistory.push(stats);
    
    // Trim history if needed
    if (this.operationsHistory.length > this.maxHistoryLength) {
      this.operationsHistory.shift();
    }
  }

  /**
   * Add population snapshot to history
   * @param population - Current population
   */
  public addPopulationSnapshot(population: Population): void {
    // Create a deep copy to prevent reference issues
    const populationCopy = population.map(solution => ({
      ...solution,
      genes: [...solution.genes]
    }));
    
    this.populationHistory.push(populationCopy);
    
    // Trim history if needed
    if (this.populationHistory.length > this.maxHistoryLength) {
      this.populationHistory.shift();
    }
    
    // Also track best solution
    const bestSolution = [...population].sort((a, b) => b.fitness - a.fitness)[0];
    this.bestSolutionHistory.push({
      ...bestSolution,
      genes: [...bestSolution.genes]
    });
    
    if (this.bestSolutionHistory.length > this.maxHistoryLength) {
      this.bestSolutionHistory.shift();
    }
  }

  /**
   * Get fitness trend data for visualization
   * @returns Array of fitness data points for best, average, and worst fitness
   */
  public getFitnessTrendData(): FitnessTrendData[] {
    return this.historyData.map((metrics, index) => ({
      generation: index,
      bestFitness: metrics.bestFitness,
      averageFitness: metrics.averageFitness,
      worstFitness: metrics.worstFitness
    }));
  }

  /**
   * Get diversity trend data for visualization
   * @returns Array of diversity data points
   */
  public getDiversityTrendData(): DiversityTrendData[] {
    return this.historyData.map((metrics, index) => ({
      generation: index,
      diversityScore: metrics.diversityScore,
      uniqueSolutionsRatio: metrics.uniqueSolutionsCount / metrics.populationSize
    }));
  }

  /**
   * Get operator effectiveness data for visualization
   * @returns Effectiveness data for genetic operators
   */
  public getOperatorEffectivenessData(): OperatorEffectivenessData {
    const operatorStats: Record<OperatorType, OperatorStats> = {
      selection: { successCount: 0, totalCount: 0, fitnessImprovements: [] },
      crossover: { successCount: 0, totalCount: 0, fitnessImprovements: [] },
      mutation: { successCount: 0, totalCount: 0, fitnessImprovements: [] }
    };
    
    // Process operation history
    for (const stats of this.operationsHistory) {
      const operatorType = stats.operatorType;
      
      operatorStats[operatorType].totalCount += stats.applyCount;
      operatorStats[operatorType].successCount += stats.successCount;
      operatorStats[operatorType].fitnessImprovements.push(stats.fitnessImprovement);
    }
    
    // Calculate average fitness improvements
    for (const type of Object.keys(operatorStats) as OperatorType[]) {
      const improvements = operatorStats[type].fitnessImprovements;
      const sum = improvements.reduce((acc, val) => acc + val, 0);
      operatorStats[type].avgImprovement = improvements.length > 0 ? sum / improvements.length : 0;
    }
    
    return { operatorStats };
  }

  /**
   * Get convergence data for visualization
   * @returns Convergence metrics
   */
  public getConvergenceData(): ConvergenceData {
    if (this.historyData.length === 0) {
      return {
        convergenceRate: 0,
        generationsSinceImprovement: 0,
        isConverged: false
      };
    }
    
    const latestMetrics = this.historyData[this.historyData.length - 1];
    
    return {
      convergenceRate: latestMetrics.convergenceRate,
      generationsSinceImprovement: latestMetrics.generationsSinceImprovement,
      isConverged: latestMetrics.convergenceRate >= 0.99
    };
  }

  /**
   * Get best solution trend for visualization
   * @returns Array of best solutions over time
   */
  public getBestSolutionTrend(): BestSolutionData[] {
    return this.bestSolutionHistory.map((solution, index) => ({
      generation: index,
      fitness: solution.fitness,
      solution: solution.genes.join('')
    }));
  }

  /**
   * Get population diversity visualization data
   * @param generationIndex - Generation index to retrieve (default is latest)
   * @returns Population diversity data
   */
  public getPopulationDiversityData(generationIndex?: number): PopulationDiversityData {
    if (this.populationHistory.length === 0) {
      return {
        populationSize: 0,
        uniqueSolutions: 0,
        solutionClusters: []
      };
    }
    
    // If no index specified, use the latest
    const index = generationIndex !== undefined ? 
      Math.min(generationIndex, this.populationHistory.length - 1) : 
      this.populationHistory.length - 1;
    
    const population = this.populationHistory[index];
    
    // Count unique solutions
    const uniqueSolutions = new Set(population.map(s => s.genes.join(''))).size;
    
    // Create solution clusters (for visualization)
    const solutionMap = new Map<string, number>();
    
    for (const solution of population) {
      const key = solution.genes.join('');
      solutionMap.set(key, (solutionMap.get(key) || 0) + 1);
    }
    
    const solutionClusters = Array.from(solutionMap.entries())
      .map(([solution, count]) => ({
        solution,
        count,
        fitness: population.find(s => s.genes.join('') === solution)?.fitness || 0
      }))
      .sort((a, b) => b.fitness - a.fitness);
    
    return {
      populationSize: population.length,
      uniqueSolutions,
      solutionClusters
    };
  }

  /**
   * Get full evolution history
   * @returns Complete evolution history data
   */
  public getEvolutionHistory(): EvolutionHistoryData {
    return {
      metrics: this.historyData,
      operations: this.operationsHistory,
      bestSolutions: this.bestSolutionHistory
    };
  }

  /**
   * Reset all history data
   */
  public reset(): void {
    this.historyData = [];
    this.operationsHistory = [];
    this.populationHistory = [];
    this.bestSolutionHistory = [];
  }
}

/**
 * Adapter for recursive thinking visualization data
 */
export class RecursiveThinkingVisualizationAdapter {
  private thinkingHistory: RecursiveThinkingStats[] = [];
  private maxHistoryLength: number;

  /**
   * @param maxHistoryLength - Maximum number of historical data points to store (default 50)
   */
  constructor(maxHistoryLength: number = 50) {
    this.maxHistoryLength = maxHistoryLength;
  }

  /**
   * Add thinking stats to history
   * @param stats - Recursive thinking statistics
   */
  public addThinkingStats(stats: RecursiveThinkingStats): void {
    this.thinkingHistory.push(stats);
    
    // Trim history if needed
    if (this.thinkingHistory.length > this.maxHistoryLength) {
      this.thinkingHistory.shift();
    }
  }

  /**
   * Get thinking process visualization data
   * @returns Thinking process data formatted for visualization
   */
  public getThinkingProcessData(): ThinkingProcessData[] {
    return this.thinkingHistory.map((stats, index) => ({
      id: index,
      input: stats.input.substring(0, 100) + (stats.input.length > 100 ? '...' : ''),
      stepCount: stats.steps.length,
      totalTokens: stats.totalTokens,
      executionTime: stats.executionTime,
      improvementScore: stats.improvementScore,
      steps: stats.steps.map((step, stepIndex) => ({
        id: stepIndex,
        description: step.description,
        tokens: step.tokens,
        executionTime: step.executionTime
      }))
    }));
  }

  /**
   * Get thinking effectiveness metrics
   * @returns Metrics about thinking effectiveness
   */
  public getThinkingEffectivenessMetrics(): ThinkingEffectivenessMetrics {
    if (this.thinkingHistory.length === 0) {
      return {
        averageStepCount: 0,
        averageTokensPerThinking: 0,
        averageExecutionTime: 0,
        averageImprovementScore: 0,
        tokensPerSecond: 0
      };
    }
    
    const avgStepCount = this.thinkingHistory.reduce(
      (acc, stats) => acc + stats.steps.length, 0
    ) / this.thinkingHistory.length;
    
    const avgTokens = this.thinkingHistory.reduce(
      (acc, stats) => acc + stats.totalTokens, 0
    ) / this.thinkingHistory.length;
    
    const avgTime = this.thinkingHistory.reduce(
      (acc, stats) => acc + stats.executionTime, 0
    ) / this.thinkingHistory.length;
    
    const avgImprovement = this.thinkingHistory.reduce(
      (acc, stats) => acc + stats.improvementScore, 0
    ) / this.thinkingHistory.length;
    
    const tokensPerSecond = avgTime > 0 ? avgTokens / (avgTime / 1000) : 0;
    
    return {
      averageStepCount: avgStepCount,
      averageTokensPerThinking: avgTokens,
      averageExecutionTime: avgTime,
      averageImprovementScore: avgImprovement,
      tokensPerSecond
    };
  }

  /**
   * Get thinking steps details for a specific thinking process
   * @param thinkingId - ID of the thinking process
   * @returns Detailed step information
   */
  public getThinkingStepsDetails(thinkingId: number): ThinkingStepDetails[] | null {
    if (thinkingId < 0 || thinkingId >= this.thinkingHistory.length) {
      return null;
    }
    
    const thinking = this.thinkingHistory[thinkingId];
    
    return thinking.steps.map((step, index) => ({
      id: index,
      description: step.description,
      input: step.input,
      output: step.output,
      tokens: step.tokens,
      executionTime: step.executionTime,
      improvement: index > 0 ? thinking.steps[index - 1].output !== step.output : false
    }));
  }

  /**
   * Reset all thinking history
   */
  public reset(): void {
    this.thinkingHistory = [];
  }
}

/**
 * Combined adapter for both genetic and recursive thinking visualization
 */
export class HybridVisualizationAdapter {
  private geneticAdapter: GeneticVisualizationAdapter;
  private thinkingAdapter: RecursiveThinkingVisualizationAdapter;

  /**
   * @param maxGeneticHistory - Maximum genetic history length
   * @param maxThinkingHistory - Maximum thinking history length
   */
  constructor(maxGeneticHistory: number = 100, maxThinkingHistory: number = 50) {
    this.geneticAdapter = new GeneticVisualizationAdapter(maxGeneticHistory);
    this.thinkingAdapter = new RecursiveThinkingVisualizationAdapter(maxThinkingHistory);
  }

  /**
   * Get genetic visualization adapter
   */
  public getGeneticAdapter(): GeneticVisualizationAdapter {
    return this.geneticAdapter;
  }

  /**
   * Get thinking visualization adapter
   */
  public getThinkingAdapter(): RecursiveThinkingVisualizationAdapter {
    return this.thinkingAdapter;
  }

  /**
   * Get combined hybrid metrics
   * @returns Combined metrics from genetic and recursive thinking processes
   */
  public getHybridMetrics(): HybridMetrics {
    const geneticData = this.geneticAdapter.getEvolutionHistory();
    const thinkingData = this.thinkingAdapter.getThinkingEffectivenessMetrics();
    
    // Calculate hybrid metrics
    const hybridEfficiency: HybridEfficiencyMetrics = {
      geneticGenerations: geneticData.metrics.length,
      thinkingSteps: this.thinkingAdapter.getThinkingProcessData().reduce(
        (acc, data) => acc + data.stepCount, 0
      ),
      thinkingExecutionTime: thinkingData.averageExecutionTime * 
        this.thinkingAdapter.getThinkingProcessData().length,
      totalImprovementScore: geneticData.metrics.length > 0 ?
        (geneticData.metrics[geneticData.metrics.length - 1].bestFitness / 
         geneticData.metrics[0].bestFitness) : 1,
      hybridSynergy: 0 // Calculated below
    };
    
    // Calculate hybrid synergy (improvement from recursive thinking vs pure genetic)
    if (geneticData.operations.length > 0) {
      const thinkingImprovements = thinkingData.averageImprovementScore;
      const geneticImprovements = geneticData.operations
        .filter(op => op.operatorType === 'mutation' || op.operatorType === 'crossover')
        .reduce((acc, op) => acc + op.fitnessImprovement, 0) / geneticData.operations.length;
      
      hybridEfficiency.hybridSynergy = 
        geneticImprovements > 0 ? thinkingImprovements / geneticImprovements : 0;
    }
    
    return {
      hybridEfficiency,
      geneticStats: {
        totalGenerations: geneticData.metrics.length,
        bestFitness: geneticData.metrics.length > 0 ? 
          geneticData.metrics[geneticData.metrics.length - 1].bestFitness : 0,
        convergenceRate: geneticData.metrics.length > 0 ?
          geneticData.metrics[geneticData.metrics.length - 1].convergenceRate : 0,
        diversityScore: geneticData.metrics.length > 0 ?
          geneticData.metrics[geneticData.metrics.length - 1].diversityScore : 0
      },
      thinkingStats: {
        totalThinkingProcesses: this.thinkingAdapter.getThinkingProcessData().length,
        averageStepCount: thinkingData.averageStepCount,
        averageImprovementScore: thinkingData.averageImprovementScore,
        tokensPerSecond: thinkingData.tokensPerSecond
      }
    };
  }

  /**
   * Reset all adapters
   */
  public reset(): void {
    this.geneticAdapter.reset();
    this.thinkingAdapter.reset();
  }
}

// Type definitions for visualization data structures

/**
 * Fitness trend data for visualization
 */
export interface FitnessTrendData {
  generation: number;
  bestFitness: number;
  averageFitness: number;
  worstFitness: number;
}

/**
 * Diversity trend data for visualization
 */
export interface DiversityTrendData {
  generation: number;
  diversityScore: number;
  uniqueSolutionsRatio: number;
}

/**
 * Statistics for a specific operator type
 */
export interface OperatorStats {
  totalCount: number;
  successCount: number;
  fitnessImprovements: number[];
  avgImprovement?: number;
}

/**
 * Effectiveness data for genetic operators
 */
export interface OperatorEffectivenessData {
  operatorStats: Record<OperatorType, OperatorStats>;
}

/**
 * Convergence data for visualization
 */
export interface ConvergenceData {
  convergenceRate: number;
  generationsSinceImprovement: number;
  isConverged: boolean;
}

/**
 * Best solution data for visualization
 */
export interface BestSolutionData {
  generation: number;
  fitness: number;
  solution: string;
}

/**
 * Solution cluster for population diversity visualization
 */
export interface SolutionCluster {
  solution: string;
  count: number;
  fitness: number;
}

/**
 * Population diversity data for visualization
 */
export interface PopulationDiversityData {
  populationSize: number;
  uniqueSolutions: number;
  solutionClusters: SolutionCluster[];
}

/**
 * Complete evolution history data
 */
export interface EvolutionHistoryData {
  metrics: EvolutionMetrics[];
  operations: GeneticOperationStats[];
  bestSolutions: Solution[];
}

/**
 * Thinking process data for visualization
 */
export interface ThinkingProcessData {
  id: number;
  input: string;
  stepCount: number;
  totalTokens: number;
  executionTime: number;
  improvementScore: number;
  steps: {
    id: number;
    description: string;
    tokens: number;
    executionTime: number;
  }[];
}

/**
 * Thinking effectiveness metrics for visualization
 */
export interface ThinkingEffectivenessMetrics {
  averageStepCount: number;
  averageTokensPerThinking: number;
  averageExecutionTime: number;
  averageImprovementScore: number;
  tokensPerSecond: number;
}

/**
 * Detailed thinking step information
 */
export interface ThinkingStepDetails {
  id: number;
  description: string;
  input: string;
  output: string;
  tokens: number;
  executionTime: number;
  improvement: boolean;
}

/**
 * Hybrid efficiency metrics
 */
export interface HybridEfficiencyMetrics {
  geneticGenerations: number;
  thinkingSteps: number;
  thinkingExecutionTime: number;
  totalImprovementScore: number;
  hybridSynergy: number;
}

/**
 * Combined hybrid metrics
 */
export interface HybridMetrics {
  hybridEfficiency: HybridEfficiencyMetrics;
  geneticStats: {
    totalGenerations: number;
    bestFitness: number;
    convergenceRate: number;
    diversityScore: number;
  };
  thinkingStats: {
    totalThinkingProcesses: number;
    averageStepCount: number;
    averageImprovementScore: number;
    tokensPerSecond: number;
  };
}