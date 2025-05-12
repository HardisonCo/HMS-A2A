import { 
  AdvancedGeneticRepairEngine 
} from '../operators/advanced_genetic_repair_engine';
import { 
  AdaptiveParameterManager 
} from './adaptive_parameter_manager';
import { 
  AdaptiveOperatorSelection 
} from './adaptive_operator_selection';
import { 
  AdaptiveStrategies 
} from './adaptive_strategies';
import { 
  Solution, 
  Population, 
  GeneticAlgorithmOptions,
  GeneticOperationStats,
  OperatorType,
  AdaptiveSystemConfig,
  AdaptiveControls,
  ParameterSnapshot,
  ParameterAdaptationEvent
} from '../types';

/**
 * Enhanced genetic algorithm engine with adaptive parameters and operators.
 * Automatically adjusts genetic algorithm parameters and operator selection
 * based on evolution progress and performance metrics.
 */
export class AdaptiveGeneticEngine extends AdvancedGeneticRepairEngine {
  protected parameterManager: AdaptiveParameterManager;
  protected operatorSelection: AdaptiveOperatorSelection;
  protected adaptiveControls: AdaptiveControls;
  protected parameterHistory: ParameterSnapshot[] = [];
  protected adaptationEvents: ParameterAdaptationEvent[] = [];
  
  /**
   * Creates a new adaptive genetic engine
   * @param options Genetic algorithm options
   * @param adaptiveConfig Configuration for the adaptive system
   */
  constructor(
    options: GeneticAlgorithmOptions,
    adaptiveConfig: Partial<AdaptiveSystemConfig> = {}
  ) {
    super(options);
    
    // Initialize adaptive controls
    this.adaptiveControls = {
      enabled: true,
      snapshotsEnabled: true,
      loggingEnabled: true,
      adaptationLevel: 'advanced'
    };
    
    // Create parameter configurations
    const parameterConfigs = this.createParameterConfigs();
    
    // Initialize parameter manager
    this.parameterManager = new AdaptiveParameterManager(
      parameterConfigs,
      adaptiveConfig.historyLimit || 50
    );
    
    // Initialize operator selection
    this.operatorSelection = new AdaptiveOperatorSelection(
      AdaptiveOperatorSelection.createStandardOperators(),
      {
        method: 'adaptive',
        creditAssignment: 'improvement',
        updateFrequency: 5,
        learningRate: 0.1
      }
    );
    
    // Listen for parameter changes
    this.parameterManager.on('parameterChanged', this.handleParameterChanged.bind(this));
  }

  /**
   * Creates default parameter configurations
   * @returns Array of parameter configurations
   */
  protected createParameterConfigs() {
    // Create default strategies
    const strategies = AdaptiveStrategies;
    
    return [
      {
        name: 'mutationRate',
        defaultValue: this.options.mutationRate,
        min: 0.01,
        max: 0.8,
        adjustmentStrategy: strategies.mutationRateStrategy()
      },
      {
        name: 'crossoverRate',
        defaultValue: this.options.crossoverRate,
        min: 0.5,
        max: 0.95,
        adjustmentStrategy: strategies.crossoverRateStrategy()
      },
      {
        name: 'tournamentSize',
        defaultValue: this.options.tournamentSize || 3,
        min: 2,
        max: 7,
        adjustmentStrategy: strategies.tournamentSizeStrategy()
      },
      {
        name: 'elitismCount',
        defaultValue: this.options.elitismCount,
        min: 1,
        max: Math.max(1, Math.floor(this.options.populationSize * 0.1)),
        adjustmentStrategy: strategies.elitismCountStrategy()
      },
      {
        name: 'populationSize',
        defaultValue: this.options.populationSize,
        min: 10,
        max: 500,
        adjustmentStrategy: strategies.populationSizeStrategy({
          adjustmentInterval: 10 // Only adjust every 10 generations
        })
      }
    ];
  }

  /**
   * Handle parameter change events
   * @param parameter Parameter name
   * @param newValue New parameter value
   * @param oldValue Old parameter value
   */
  protected handleParameterChanged(
    parameter: string, 
    newValue: number, 
    oldValue: number
  ): void {
    // Log event if enabled
    if (this.adaptiveControls.loggingEnabled) {
      console.log(`Parameter ${parameter} changed from ${oldValue} to ${newValue}`);
    }
    
    // Record adaptation event
    const event: ParameterAdaptationEvent = {
      parameter,
      oldValue,
      newValue,
      reason: 'adaptive_adjustment',
      metrics: {
        generation: this.currentGeneration,
        bestFitness: this.bestFitnessEver,
        diversityScore: this.lastDiversityScore,
        convergenceRate: this.currentConvergenceRate
      },
      generation: this.currentGeneration,
      timestamp: Date.now()
    };
    
    this.adaptationEvents.push(event);
    this.emit('parameterAdapted', event);
    
    // Apply new value to options
    switch (parameter) {
      case 'mutationRate':
        this.currentMutationRate = newValue;
        break;
      case 'crossoverRate':
        this.currentCrossoverRate = newValue;
        break;
      case 'tournamentSize':
        this.currentTournamentSize = Math.round(newValue);
        break;
      case 'elitismCount':
        this.options.elitismCount = Math.round(newValue);
        break;
      case 'populationSize':
        // Population size requires special handling
        this.handlePopulationSizeChange(Math.round(newValue));
        break;
    }
  }

  /**
   * Handle population size change
   * @param newSize New population size
   */
  protected handlePopulationSizeChange(newSize: number): void {
    const currentSize = this.options.populationSize;
    
    // Only apply if different
    if (newSize === currentSize) {
      return;
    }
    
    // Will be applied on next generation
    this.options.populationSize = newSize;
    
    // Emit event for external handling
    this.emit('populationSizeChanged', newSize, currentSize);
  }

  /**
   * Take a snapshot of current parameters
   */
  protected takeParameterSnapshot(): void {
    if (!this.adaptiveControls.snapshotsEnabled) {
      return;
    }
    
    const snapshot: ParameterSnapshot = {
      parameters: this.parameterManager.getParameterSnapshot(),
      metrics: this.getLastMetrics(),
      timestamp: Date.now(),
      generation: this.currentGeneration
    };
    
    this.parameterHistory.push(snapshot);
    
    // Trim history if needed
    const maxHistory = 100;
    if (this.parameterHistory.length > maxHistory) {
      this.parameterHistory.shift();
    }
  }

  /**
   * Update adaptive parameters based on evolution metrics
   * @param metrics Current evolution metrics
   */
  protected updateAdaptiveParameters(metrics: any): void {
    if (!this.adaptiveControls.enabled) {
      return;
    }
    
    // Update parameter manager with metrics
    this.parameterManager.addEvolutionMetrics(metrics);
    
    // Take parameter snapshot
    this.takeParameterSnapshot();
  }

  /**
   * Track operator performance
   * @param operatorType Type of operator
   * @param operatorName Name of operator
   * @param beforeFitness Fitness before operation
   * @param afterFitness Fitness after operation
   */
  protected trackOperatorPerformance(
    operatorType: OperatorType, 
    operatorName: string, 
    beforeFitness: number, 
    afterFitness: number
  ): void {
    super.trackOperatorPerformance(operatorType, operatorName, beforeFitness, afterFitness);
    
    // Get the most recent operation stats
    if (this.operationStats.length > 0) {
      const stats = this.operationStats[this.operationStats.length - 1];
      
      // Update operator selection system
      this.operatorSelection.updateOperatorPerformance(stats);
      
      // Update parameter manager
      this.parameterManager.addOperationStats(stats);
    }
  }

  /**
   * Override selection method to use adaptive operator selection
   * @param population Population to select from
   * @param count Number of solutions to select
   * @returns Selected solutions
   */
  protected select(population: Population, count: number): Solution[] {
    if (!this.adaptiveControls.enabled) {
      return super.select(population, count);
    }
    
    // Get the selection method from adaptive operator selection
    const selectionMethod = this.operatorSelection.selectOperator('selection');
    
    // Get selection parameters
    const tournamentSize = Math.round(
      this.parameterManager.getParameter('tournamentSize')
    );
    
    // Apply appropriate selection method
    let selected: Solution[];
    
    switch (selectionMethod) {
      case 'tournament':
        selected = this.selectionOperators.tournamentSelection(
          population, 
          count, 
          tournamentSize
        );
        break;
      case 'roulette':
        selected = this.selectionOperators.rouletteWheelSelection(
          population, 
          count
        );
        break;
      case 'rank':
        selected = this.selectionOperators.rankSelection(
          population, 
          count
        );
        break;
      case 'steady-state':
        selected = this.selectionOperators.steadyStateSelection(
          population, 
          count
        );
        break;
      default:
        selected = this.selectionOperators.tournamentSelection(
          population, 
          count, 
          tournamentSize
        );
    }
    
    // Apply elitism if enabled
    const elitismCount = Math.round(
      this.parameterManager.getParameter('elitismCount')
    );
    
    if (elitismCount > 0) {
      const elites = this.selectionOperators.elitism(population, elitismCount);
      
      // Replace random selected solutions with elites
      for (let i = 0; i < elites.length; i++) {
        const randomIndex = Math.floor(Math.random() * selected.length);
        selected[randomIndex] = elites[i];
      }
    }
    
    return selected;
  }

  /**
   * Override crossover method to use adaptive operator selection
   * @param parent1 First parent
   * @param parent2 Second parent
   * @returns Pair of child solutions
   */
  protected crossover(parent1: Solution, parent2: Solution): [Solution, Solution] {
    if (!this.adaptiveControls.enabled) {
      return super.crossover(parent1, parent2);
    }
    
    // Skip crossover probabilistically
    const crossoverRate = this.parameterManager.getParameter('crossoverRate');
    if (Math.random() > crossoverRate) {
      return [{ ...parent1 }, { ...parent2 }];
    }
    
    // Track fitness before
    const fitnessBefore = (parent1.fitness + parent2.fitness) / 2;
    
    // Get the crossover method from adaptive operator selection
    const crossoverMethod = this.operatorSelection.selectOperator('crossover');
    
    // Apply appropriate crossover method
    let children: [Solution, Solution];
    
    switch (crossoverMethod) {
      case 'single-point':
        children = this.crossoverOperators.singlePointCrossover(parent1, parent2);
        break;
      case 'multi-point':
        children = this.crossoverOperators.multiPointCrossover(parent1, parent2, 2);
        break;
      case 'uniform':
        children = this.crossoverOperators.uniformCrossover(parent1, parent2);
        break;
      case 'arithmetic':
        children = this.crossoverOperators.arithmeticCrossover(parent1, parent2);
        break;
      case 'semantic':
        children = this.crossoverOperators.semanticAwareCrossover(
          parent1, 
          parent2, 
          this.semanticSimilarityFunction
        );
        break;
      default:
        children = this.crossoverOperators.singlePointCrossover(parent1, parent2);
    }
    
    // Ensure fitness values are updated
    children[0].fitness = 0;
    children[1].fitness = 0;
    
    // Track operator performance
    Promise.all([
      this.evaluateFitness(children[0]),
      this.evaluateFitness(children[1])
    ]).then(([fitness1, fitness2]) => {
      children[0].fitness = fitness1;
      children[1].fitness = fitness2;
      
      const fitnessAfter = (fitness1 + fitness2) / 2;
      
      this.trackOperatorPerformance(
        'crossover', 
        crossoverMethod, 
        fitnessBefore, 
        fitnessAfter
      );
    });
    
    return children;
  }

  /**
   * Override mutation method to use adaptive operator selection
   * @param solution Solution to mutate
   * @returns Mutated solution
   */
  protected mutate(solution: Solution): Solution {
    if (!this.adaptiveControls.enabled) {
      return super.mutate(solution);
    }
    
    // Skip mutation probabilistically
    const mutationRate = this.parameterManager.getParameter('mutationRate');
    if (Math.random() > mutationRate) {
      return { ...solution };
    }
    
    // Track fitness before
    const fitnessBefore = solution.fitness;
    
    // Get the mutation method from adaptive operator selection
    const mutationMethod = this.operatorSelection.selectOperator('mutation');
    
    // Apply appropriate mutation method
    let mutated: Solution;
    
    switch (mutationMethod) {
      case 'point':
        mutated = this.mutationOperators.pointMutation(
          solution, 
          this.options.genePool || []
        );
        break;
      case 'swap':
        mutated = this.mutationOperators.swapMutation(solution);
        break;
      case 'insert':
        mutated = this.mutationOperators.insertMutation(
          solution, 
          this.options.genePool || []
        );
        break;
      case 'delete':
        mutated = this.mutationOperators.deleteMutation(solution);
        break;
      case 'scramble':
        mutated = this.mutationOperators.scrambleMutation(solution);
        break;
      case 'pattern':
        mutated = this.mutationOperators.patternBasedMutation(
          solution, 
          this.patterns
        );
        break;
      default:
        mutated = this.mutationOperators.pointMutation(
          solution, 
          this.options.genePool || []
        );
    }
    
    // Ensure fitness is updated
    mutated.fitness = 0;
    
    // Track operator performance
    this.evaluateFitness(mutated).then(fitness => {
      mutated.fitness = fitness;
      
      this.trackOperatorPerformance(
        'mutation', 
        mutationMethod, 
        fitnessBefore, 
        fitness
      );
    });
    
    return mutated;
  }

  /**
   * Override evolveGeneration to incorporate adaptive parameters
   * @param population Current population
   * @returns Evolved population for next generation
   */
  protected async evolveGeneration(population: Population): Promise<Population> {
    // Measure diversity
    const diversity = this.measurePopulationDiversity(population);
    this.lastDiversityScore = diversity;
    
    // Calculate convergence rate
    this.currentConvergenceRate = this.calculateConvergenceRate(population);
    
    // Generate evolution metrics
    const metrics = this.generateEvolutionMetrics(population);
    
    // Update adaptive parameters if enabled
    if (this.adaptiveControls.enabled) {
      this.updateAdaptiveParameters(metrics);
    }
    
    // Continue with standard evolution
    return super.evolveGeneration(population);
  }

  /**
   * Get adaptation event history
   * @returns Array of parameter adaptation events
   */
  public getAdaptationHistory(): ParameterAdaptationEvent[] {
    return [...this.adaptationEvents];
  }

  /**
   * Get parameter snapshot history
   * @returns Array of parameter snapshots
   */
  public getParameterHistory(): ParameterSnapshot[] {
    return [...this.parameterHistory];
  }

  /**
   * Get operator performance statistics
   * @returns Statistics for each operator
   */
  public getOperatorStatistics(): Record<string, any> {
    return this.operatorSelection.getOperatorPerformanceStats();
  }

  /**
   * Set adaptive control options
   * @param controls New control settings
   */
  public setAdaptiveControls(controls: Partial<AdaptiveControls>): void {
    this.adaptiveControls = {
      ...this.adaptiveControls,
      ...controls
    };
    
    // If disabled, reset to default parameters
    if (!this.adaptiveControls.enabled) {
      this.resetToDefaultParameters();
    }
  }

  /**
   * Reset all parameters to their default values
   */
  public resetToDefaultParameters(): void {
    this.parameterManager.resetAllParameters();
    
    // Also reset current rates
    this.currentMutationRate = this.options.mutationRate;
    this.currentCrossoverRate = this.options.crossoverRate;
    this.currentTournamentSize = this.options.tournamentSize || 3;
  }
}