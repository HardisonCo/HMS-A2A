/**
 * Population Manager
 * 
 * This module provides specialized population management strategies for economic
 * solution evolution. It extends the genetic algorithm framework with domain-specific
 * population management techniques for economic policy optimization.
 */

import { HealthState } from '../monitoring/health_types';
import {
  Individual,
  Population,
  GeneticParameter,
  GeneType,
  GeneticOperatorType
} from './genetic_algorithm_framework';

/**
 * Population diversity strategy types.
 */
export enum DiversityStrategy {
  Standard = 'standard',
  EnhancedDiversity = 'enhanced_diversity',
  NichedConservation = 'niched_conservation',
  MultiPopulation = 'multi_population',
  AdaptiveImmigration = 'adaptive_immigration',
  Speciation = 'speciation',
  DynamicNiching = 'dynamic_niching',
  ConstraintClustering = 'constraint_clustering',
  HistoricallyInformedPreservation = 'historically_informed_preservation'
}

/**
 * Policy constraint handling strategy types.
 */
export enum ConstraintStrategy {
  PenaltyFunction = 'penalty_function',
  RepairOperator = 'repair_operator',
  DeathPenalty = 'death_penalty',
  SeparableConstraint = 'separable_constraint',
  FeasibilityRules = 'feasibility_rules',
  StochasticRanking = 'stochastic_ranking',
  EpsilonConstraint = 'epsilon_constraint',
  FuzzyConstraint = 'fuzzy_constraint',
  AdaptiveConstraint = 'adaptive_constraint'
}

/**
 * Population initialization strategy types.
 */
export enum InitializationStrategy {
  Random = 'random',
  LatinHypercube = 'latin_hypercube',
  QuasiRandom = 'quasi_random',
  HistoricallyInformed = 'historically_informed',
  GradientBased = 'gradient_based',
  KnowledgeSeeded = 'knowledge_seeded',
  ExpertSystem = 'expert_system',
  CaseBasedReasoning = 'case_based_reasoning',
  BlendedStrategy = 'blended_strategy'
}

/**
 * Population management strategy options.
 */
export interface PopulationManagementOptions {
  // Basic parameters
  populationSize: number;
  maxGenerations: number;
  elitismCount: number;
  
  // Diversity management
  diversityStrategy: DiversityStrategy;
  diversityThreshold?: number;
  nicheRadius?: number;
  subpopulationCount?: number;
  immigrationRate?: number;
  speciationThreshold?: number;
  
  // Constraint handling
  constraintStrategy: ConstraintStrategy;
  constraintPenaltyFactor?: number;
  constraintViolationThreshold?: number;
  repairAttempts?: number;
  feasibilityProbability?: number;
  epsilonLevel?: number;
  
  // Initialization
  initializationStrategy: InitializationStrategy;
  seedingPercentage?: number;
  historyWeight?: number;
  gradientSamples?: number;
  knowledgeBaseInfluence?: number;
  
  // Domain-specific options
  economicDomainParams?: {
    fiscalConstraintWeight?: number;
    monetaryPolicyBounds?: [number, number];
    tradeBalanceSensitivity?: number;
    inflationRiskPenalty?: number;
    growthInflationTradeoff?: number;
    equityWeight?: number;
    structuralAdjustmentPenalty?: number;
    politicalFeasibilityThreshold?: number;
    implementationComplexityPenalty?: number;
  };
  
  // Adaptive parameters
  enableAdaptiveControl?: boolean;
  adaptationRate?: number;
  dynamicNichingInterval?: number;
  speciationReassessmentInterval?: number;
}

/**
 * Diversity metrics for a population.
 */
export interface DiversityMetrics {
  geneticDiversity: number;
  phenotypicDiversity: number;
  nicheCount: number;
  entropyMeasure: number;
  distributionStats: {
    mean: Record<string, number>;
    variance: Record<string, number>;
    skewness: Record<string, number>;
  };
  paretoFrontDiversity?: number;
  constraintSatisfactionDiversity?: number;
}

/**
 * Population evolution statistics.
 */
export interface EvolutionStats {
  generation: number;
  populationSize: number;
  bestFitness: number;
  meanFitness: number;
  fitnessVariance: number;
  diversityMetrics: DiversityMetrics;
  speciesStats?: Array<{
    id: string;
    size: number;
    meanFitness: number;
    bestFitness: number;
  }>;
  immigrantCount?: number;
  extinctionCount?: number;
  elitismImpact?: number;
  constraintViolationRate?: number;
  feasibleSolutionRate?: number;
  adaptiveParameterValues?: Record<string, number>;
}

/**
 * Sub-population information.
 */
export interface Subpopulation {
  id: string;
  focus: string;
  individuals: Individual[];
  exchangeRate: number;
  isolationDuration: number;
  currentIsolation: number;
  specializedOperators?: GeneticOperatorType[];
  customParameters?: Record<string, any>;
}

/**
 * Population management strategy for economics-focused evolution.
 */
export class PopulationManager {
  private isInitialized: boolean = false;
  private options: PopulationManagementOptions;
  private populations: Map<string, Population> = new Map();
  private subpopulations: Map<string, Subpopulation[]> = new Map();
  private evolutionHistory: Map<string, EvolutionStats[]> = new Map();
  private diversityStrategies: Map<DiversityStrategy, DiversityFunction> = new Map();
  private constraintStrategies: Map<ConstraintStrategy, ConstraintFunction> = new Map();
  private initializationStrategies: Map<InitializationStrategy, InitializationFunction> = new Map();

  /**
   * Creates a new PopulationManager instance.
   * 
   * @param options Population management options
   */
  constructor(options?: Partial<PopulationManagementOptions>) {
    // Set default options
    this.options = {
      populationSize: 100,
      maxGenerations: 100,
      elitismCount: 5,
      diversityStrategy: DiversityStrategy.EnhancedDiversity,
      constraintStrategy: ConstraintStrategy.PenaltyFunction,
      initializationStrategy: InitializationStrategy.HistoricallyInformed,
      ...options
    };
  }

  /**
   * Initializes the population manager.
   */
  async initialize(): Promise<void> {
    console.log('Initializing Population Manager...');

    // Register diversity strategies
    this.registerDiversityStrategies();
    
    // Register constraint strategies
    this.registerConstraintStrategies();
    
    // Register initialization strategies
    this.registerInitializationStrategies();

    this.isInitialized = true;
    console.log('Population Manager initialized successfully');
  }

  /**
   * Creates a new population for a genetic algorithm run.
   * 
   * @param runId The run ID
   * @param parameters The genetic parameters
   * @param options Population management options
   * @returns The created population
   */
  async createPopulation(
    runId: string,
    parameters: GeneticParameter[],
    options?: Partial<PopulationManagementOptions>
  ): Promise<Population> {
    if (!this.isInitialized) {
      throw new Error('Population Manager must be initialized first');
    }

    // Merge options
    const mergedOptions = {
      ...this.options,
      ...options
    };

    // Create population
    const population = await this.initializePopulation(runId, parameters, mergedOptions);
    
    // Store population
    this.populations.set(runId, population);
    
    // Create subpopulations if using multi-population strategy
    if (mergedOptions.diversityStrategy === DiversityStrategy.MultiPopulation) {
      await this.createSubpopulations(runId, parameters, mergedOptions);
    }
    
    // Initialize evolution history
    this.evolutionHistory.set(runId, []);

    return population;
  }

  /**
   * Evolves a population to the next generation.
   * 
   * @param runId The run ID
   * @param selectionResults Selection results from genetic algorithm
   * @param parameters The genetic parameters
   * @param options Population management options
   * @returns The evolved population
   */
  async evolvePopulation(
    runId: string,
    selectionResults: {
      parents: Individual[];
      offspring: Individual[];
      currentPopulation: Population;
    },
    parameters: GeneticParameter[],
    options?: Partial<PopulationManagementOptions>
  ): Promise<Population> {
    if (!this.isInitialized) {
      throw new Error('Population Manager must be initialized first');
    }

    if (!this.populations.has(runId)) {
      throw new Error(`Population for run ID ${runId} not found`);
    }

    // Merge options
    const mergedOptions = {
      ...this.options,
      ...options
    };

    const { parents, offspring, currentPopulation } = selectionResults;

    // Apply diversity strategy
    const diversityFunction = this.diversityStrategies.get(mergedOptions.diversityStrategy);
    if (!diversityFunction) {
      throw new Error(`Diversity strategy ${mergedOptions.diversityStrategy} not found`);
    }

    // Apply constraint strategy
    const constraintFunction = this.constraintStrategies.get(mergedOptions.constraintStrategy);
    if (!constraintFunction) {
      throw new Error(`Constraint strategy ${mergedOptions.constraintStrategy} not found`);
    }

    // Create next generation
    let nextGeneration: Individual[];
    
    // If using multi-population strategy, evolve subpopulations
    if (mergedOptions.diversityStrategy === DiversityStrategy.MultiPopulation) {
      nextGeneration = await this.evolveSubpopulations(runId, selectionResults, parameters, mergedOptions);
    } else {
      // Apply diversity strategy
      const diversifiedOffspring = await diversityFunction(offspring, currentPopulation, mergedOptions);
      
      // Apply constraint strategy
      const constrainedOffspring = await constraintFunction(diversifiedOffspring, parameters, mergedOptions);
      
      // Apply elitism (keep best individuals from current population)
      const elites = this.selectElites(currentPopulation.individuals, mergedOptions.elitismCount);
      
      // Combine elites and offspring
      nextGeneration = [...elites, ...constrainedOffspring.slice(0, mergedOptions.populationSize - elites.length)];
    }

    // Create next generation population
    const nextPopulation: Population = {
      id: `pop_${runId}_${currentPopulation.generation + 1}`,
      generation: currentPopulation.generation + 1,
      individuals: nextGeneration,
      timestamp: new Date().toISOString(),
      metadata: {
        diversityMetrics: this.calculateDiversityMetrics(nextGeneration, parameters),
        bestFitness: Math.max(...nextGeneration.map(ind => ind.fitness as number)),
        averageFitness: nextGeneration.reduce((sum, ind) => sum + (ind.fitness as number), 0) / nextGeneration.length,
        worstFitness: Math.min(...nextGeneration.map(ind => ind.fitness as number)),
        improvementRate: nextGeneration[0].fitness as number - currentPopulation.individuals[0].fitness as number,
        stagnationCounter: nextGeneration[0].fitness <= currentPopulation.individuals[0].fitness ?
          (currentPopulation.metadata?.stagnationCounter || 0) + 1 : 0
      }
    };

    // Store evolution statistics
    await this.storeEvolutionStats(runId, nextPopulation, parameters, mergedOptions);

    // Update population
    this.populations.set(runId, nextPopulation);

    return nextPopulation;
  }

  /**
   * Manages population diversity through injection of new solutions.
   * 
   * @param runId The run ID
   * @param parameters The genetic parameters
   * @param options Population management options
   * @returns The updated population
   */
  async manageDiversity(
    runId: string,
    parameters: GeneticParameter[],
    options?: Partial<PopulationManagementOptions>
  ): Promise<Population> {
    if (!this.isInitialized) {
      throw new Error('Population Manager must be initialized first');
    }

    if (!this.populations.has(runId)) {
      throw new Error(`Population for run ID ${runId} not found`);
    }

    // Merge options
    const mergedOptions = {
      ...this.options,
      ...options
    };

    // Get current population
    const currentPopulation = this.populations.get(runId)!;

    // Calculate diversity metrics
    const diversityMetrics = this.calculateDiversityMetrics(currentPopulation.individuals, parameters);

    // Check if diversity injection is needed
    if (diversityMetrics.geneticDiversity < (mergedOptions.diversityThreshold || 0.3)) {
      // Inject new individuals
      const newIndividuals = await this.createDiverseIndividuals(
        runId,
        parameters,
        currentPopulation,
        Math.floor(currentPopulation.individuals.length * (mergedOptions.immigrationRate || 0.1)),
        mergedOptions
      );

      // Replace worst individuals with new ones
      const sortedIndividuals = [...currentPopulation.individuals]
        .sort((a, b) => (b.fitness as number) - (a.fitness as number));
      
      const eliteCount = Math.floor(sortedIndividuals.length * 0.2); // Keep top 20%
      const retained = sortedIndividuals.slice(0, sortedIndividuals.length - newIndividuals.length);
      
      // Ensure we always keep the elites
      const elites = sortedIndividuals.slice(0, eliteCount);
      const nonElites = retained.slice(eliteCount);
      
      // Combine elites, remaining non-elites, and new individuals
      const updatedIndividuals = [
        ...elites,
        ...nonElites.slice(0, sortedIndividuals.length - newIndividuals.length - eliteCount),
        ...newIndividuals
      ];

      // Create updated population
      const updatedPopulation: Population = {
        ...currentPopulation,
        individuals: updatedIndividuals,
        metadata: {
          ...currentPopulation.metadata,
          diversityMetrics: this.calculateDiversityMetrics(updatedIndividuals, parameters),
          immigrantCount: newIndividuals.length
        }
      };

      // Update population
      this.populations.set(runId, updatedPopulation);

      return updatedPopulation;
    }

    return currentPopulation;
  }

  /**
   * Creates subpopulations for a genetic algorithm run.
   * 
   * @param runId The run ID
   * @param parameters The genetic parameters
   * @param options Population management options
   */
  private async createSubpopulations(
    runId: string,
    parameters: GeneticParameter[],
    options: PopulationManagementOptions
  ): Promise<void> {
    const subpopulationCount = options.subpopulationCount || 3;
    const population = this.populations.get(runId)!;
    
    // Domain-specific subpopulation focuses for economic optimization
    const economicFocuses = [
      'growth_optimization',
      'inflation_control',
      'employment_maximization',
      'deficit_reduction',
      'trade_balance_improvement',
      'wealth_distribution_optimization',
      'resource_allocation_efficiency',
      'market_stability'
    ];
    
    // Create subpopulations array
    const subpopulations: Subpopulation[] = [];
    
    // Calculate individuals per subpopulation
    const individualsPerSubpop = Math.floor(population.individuals.length / subpopulationCount);
    
    // Create specialized subpopulations
    for (let i = 0; i < subpopulationCount; i++) {
      const focus = economicFocuses[i % economicFocuses.length];
      
      // Determine specialized operators based on focus
      const specializedOperators = this.getSpecializedOperators(focus);
      
      // Create subpopulation
      const subpopulation: Subpopulation = {
        id: `subpop_${runId}_${i}`,
        focus,
        individuals: population.individuals.slice(i * individualsPerSubpop, (i + 1) * individualsPerSubpop),
        exchangeRate: 0.1, // 10% exchange between subpopulations
        isolationDuration: 5, // Generations before exchange
        currentIsolation: 0,
        specializedOperators,
        customParameters: this.getCustomParameters(focus, options)
      };
      
      subpopulations.push(subpopulation);
    }
    
    // Store subpopulations
    this.subpopulations.set(runId, subpopulations);
  }
  
  /**
   * Evolves subpopulations for a genetic algorithm run.
   * 
   * @param runId The run ID
   * @param selectionResults Selection results from genetic algorithm
   * @param parameters The genetic parameters
   * @param options Population management options
   * @returns The evolved individuals
   */
  private async evolveSubpopulations(
    runId: string,
    selectionResults: {
      parents: Individual[];
      offspring: Individual[];
      currentPopulation: Population;
    },
    parameters: GeneticParameter[],
    options: PopulationManagementOptions
  ): Promise<Individual[]> {
    if (!this.subpopulations.has(runId)) {
      throw new Error(`Subpopulations for run ID ${runId} not found`);
    }
    
    const subpopulations = this.subpopulations.get(runId)!;
    const { offspring } = selectionResults;
    
    // Map offspring to subpopulations
    const offspringGroups: Individual[][] = [];
    const offspringPerSubpop = Math.floor(offspring.length / subpopulations.length);
    
    for (let i = 0; i < subpopulations.length; i++) {
      offspringGroups.push(offspring.slice(i * offspringPerSubpop, (i + 1) * offspringPerSubpop));
    }
    
    // Evolve each subpopulation
    const evolvedSubpopulations: Subpopulation[] = [];
    
    for (let i = 0; i < subpopulations.length; i++) {
      const subpop = subpopulations[i];
      
      // Increment isolation counter
      subpop.currentIsolation++;
      
      // Apply diversity strategy to subpopulation
      const diversityFunction = this.diversityStrategies.get(options.diversityStrategy);
      if (!diversityFunction) {
        throw new Error(`Diversity strategy ${options.diversityStrategy} not found`);
      }
      
      // Apply constraint strategy to subpopulation
      const constraintFunction = this.constraintStrategies.get(options.constraintStrategy);
      if (!constraintFunction) {
        throw new Error(`Constraint strategy ${options.constraintStrategy} not found`);
      }
      
      // Apply specialized operators based on focus
      const diversifiedOffspring = await diversityFunction(offspringGroups[i], {
        ...selectionResults.currentPopulation,
        individuals: subpop.individuals
      }, {
        ...options,
        customParameters: subpop.customParameters
      });
      
      // Apply constraint strategy
      const constrainedOffspring = await constraintFunction(diversifiedOffspring, parameters, {
        ...options,
        customParameters: subpop.customParameters
      });
      
      // Apply elitism (keep best individuals from current subpopulation)
      const elites = this.selectElites(subpop.individuals, Math.floor(options.elitismCount / subpopulations.length));
      
      // Combine elites and offspring
      const nextGeneration = [...elites, ...constrainedOffspring.slice(0, subpop.individuals.length - elites.length)];
      
      // Create evolved subpopulation
      evolvedSubpopulations.push({
        ...subpop,
        individuals: nextGeneration
      });
    }
    
    // Check if exchange between subpopulations is needed
    const shouldExchange = subpopulations.some(subpop => subpop.currentIsolation >= subpop.isolationDuration);
    
    if (shouldExchange) {
      this.exchangeBetweenSubpopulations(evolvedSubpopulations);
    }
    
    // Store evolved subpopulations
    this.subpopulations.set(runId, evolvedSubpopulations);
    
    // Combine all individuals from subpopulations
    return evolvedSubpopulations.flatMap(subpop => subpop.individuals);
  }
  
  /**
   * Exchanges individuals between subpopulations.
   * 
   * @param subpopulations The subpopulations
   */
  private exchangeBetweenSubpopulations(subpopulations: Subpopulation[]): void {
    for (let i = 0; i < subpopulations.length; i++) {
      const subpop = subpopulations[i];
      
      // Reset isolation counter
      subpop.currentIsolation = 0;
      
      // Calculate number of individuals to exchange
      const exchangeCount = Math.floor(subpop.individuals.length * subpop.exchangeRate);
      
      if (exchangeCount > 0) {
        // Select individuals to exchange (worst individuals)
        const sortedIndividuals = [...subpop.individuals]
          .sort((a, b) => (b.fitness as number) - (a.fitness as number));
        
        const individualsToExchange = sortedIndividuals.slice(sortedIndividuals.length - exchangeCount);
        
        // Calculate next subpopulation index (round-robin)
        const nextIndex = (i + 1) % subpopulations.length;
        const nextSubpop = subpopulations[nextIndex];
        
        // Select individuals to replace in next subpopulation (worst individuals)
        const nextSortedIndividuals = [...nextSubpop.individuals]
          .sort((a, b) => (b.fitness as number) - (a.fitness as number));
        
        const indicesToReplace = Array.from(
          { length: exchangeCount },
          (_, i) => nextSubpop.individuals.indexOf(nextSortedIndividuals[nextSortedIndividuals.length - 1 - i])
        );
        
        // Exchange individuals
        for (let j = 0; j < exchangeCount; j++) {
          nextSubpop.individuals[indicesToReplace[j]] = individualsToExchange[j];
        }
      }
    }
  }
  
  /**
   * Gets specialized operators for a specific focus.
   * 
   * @param focus The focus area
   * @returns Specialized operators
   */
  private getSpecializedOperators(focus: string): GeneticOperatorType[] {
    // Determine specialized operators based on focus
    switch (focus) {
      case 'growth_optimization':
        return [
          GeneticOperatorType.BlendCrossover,
          GeneticOperatorType.AdaptiveMutation,
          GeneticOperatorType.ElitistSelection
        ];
      
      case 'inflation_control':
        return [
          GeneticOperatorType.SinglePointCrossover,
          GeneticOperatorType.GaussianMutation,
          GeneticOperatorType.TournamentSelection
        ];
      
      case 'employment_maximization':
        return [
          GeneticOperatorType.TwoPointCrossover, 
          GeneticOperatorType.BoundaryMutation,
          GeneticOperatorType.RankSelection
        ];
      
      case 'deficit_reduction':
        return [
          GeneticOperatorType.UniformCrossover,
          GeneticOperatorType.GaussianMutation,
          GeneticOperatorType.TournamentSelection
        ];
      
      case 'trade_balance_improvement':
        return [
          GeneticOperatorType.BlendCrossover,
          GeneticOperatorType.SwapMutation,
          GeneticOperatorType.RankSelection
        ];
      
      default:
        return [
          GeneticOperatorType.BlendCrossover,
          GeneticOperatorType.GaussianMutation,
          GeneticOperatorType.TournamentSelection
        ];
    }
  }
  
  /**
   * Gets custom parameters for a specific focus.
   * 
   * @param focus The focus area
   * @param options Population management options
   * @returns Custom parameters
   */
  private getCustomParameters(focus: string, options: PopulationManagementOptions): Record<string, any> {
    const baseParams = options.economicDomainParams || {};
    
    // Determine custom parameters based on focus
    switch (focus) {
      case 'growth_optimization':
        return {
          ...baseParams,
          growthWeight: 0.7,
          inflationWeight: 0.1,
          employmentWeight: 0.2,
          fiscalConstraintWeight: baseParams.fiscalConstraintWeight || 0.3,
          equityWeight: baseParams.equityWeight || 0.1
        };
      
      case 'inflation_control':
        return {
          ...baseParams,
          growthWeight: 0.2,
          inflationWeight: 0.7,
          employmentWeight: 0.1,
          monetaryPolicyBounds: baseParams.monetaryPolicyBounds || [-2, 5],
          inflationRiskPenalty: baseParams.inflationRiskPenalty || 0.5
        };
      
      case 'employment_maximization':
        return {
          ...baseParams,
          growthWeight: 0.3,
          inflationWeight: 0.1,
          employmentWeight: 0.6,
          structuralAdjustmentPenalty: baseParams.structuralAdjustmentPenalty || 0.4,
          equityWeight: baseParams.equityWeight || 0.3
        };
      
      case 'deficit_reduction':
        return {
          ...baseParams,
          growthWeight: 0.2,
          inflationWeight: 0.2,
          employmentWeight: 0.1,
          deficitWeight: 0.5,
          fiscalConstraintWeight: baseParams.fiscalConstraintWeight || 0.8,
          politicalFeasibilityThreshold: baseParams.politicalFeasibilityThreshold || 0.6
        };
      
      case 'trade_balance_improvement':
        return {
          ...baseParams,
          growthWeight: 0.3,
          inflationWeight: 0.2,
          employmentWeight: 0.1,
          tradeBalanceWeight: 0.4,
          tradeBalanceSensitivity: baseParams.tradeBalanceSensitivity || 0.7,
          implementationComplexityPenalty: baseParams.implementationComplexityPenalty || 0.3
        };
      
      default:
        return baseParams;
    }
  }

  /**
   * Initializes a population for a genetic algorithm run.
   * 
   * @param runId The run ID
   * @param parameters The genetic parameters
   * @param options Population management options
   * @returns The initialized population
   */
  private async initializePopulation(
    runId: string,
    parameters: GeneticParameter[],
    options: PopulationManagementOptions
  ): Promise<Population> {
    // Get initialization strategy
    const initializationFunction = this.initializationStrategies.get(options.initializationStrategy);
    if (!initializationFunction) {
      throw new Error(`Initialization strategy ${options.initializationStrategy} not found`);
    }

    // Initialize population
    const individuals = await initializationFunction(runId, parameters, options);

    // Create population
    const population: Population = {
      id: `pop_${runId}_0`,
      generation: 0,
      individuals,
      timestamp: new Date().toISOString(),
      metadata: {
        diversityMetrics: this.calculateDiversityMetrics(individuals, parameters),
        bestFitness: 0, // Will be updated after evaluation
        averageFitness: 0, // Will be updated after evaluation
        worstFitness: 0, // Will be updated after evaluation
        improvementRate: 0,
        stagnationCounter: 0
      }
    };

    return population;
  }

  /**
   * Selects elite individuals from a population.
   * 
   * @param individuals The individuals
   * @param count The number of elites to select
   * @returns The elite individuals
   */
  private selectElites(individuals: Individual[], count: number): Individual[] {
    // Sort individuals by fitness (descending)
    const sortedIndividuals = [...individuals]
      .sort((a, b) => (b.fitness as number) - (a.fitness as number));

    // Select top individuals
    return sortedIndividuals.slice(0, count);
  }

  /**
   * Creates diverse individuals for diversity injection.
   * 
   * @param runId The run ID
   * @param parameters The genetic parameters
   * @param currentPopulation The current population
   * @param count The number of individuals to create
   * @param options Population management options
   * @returns The created individuals
   */
  private async createDiverseIndividuals(
    runId: string,
    parameters: GeneticParameter[],
    currentPopulation: Population,
    count: number,
    options: PopulationManagementOptions
  ): Promise<Individual[]> {
    // Get initialization strategy
    const initializationFunction = this.initializationStrategies.get(InitializationStrategy.Random);
    if (!initializationFunction) {
      throw new Error(`Initialization strategy ${InitializationStrategy.Random} not found`);
    }

    // Create random individuals
    const randomIndividuals = await initializationFunction(`${runId}_diverse`, parameters, {
      ...options,
      populationSize: count * 2 // Create more than needed to allow for filtering
    });

    // Calculate distance to existing individuals
    const distances = randomIndividuals.map(individual => {
      const minDistance = Math.min(
        ...currentPopulation.individuals.map(existing => 
          this.calculateDistance(individual.chromosome, existing.chromosome)
        )
      );
      return { individual, distance: minDistance };
    });

    // Sort by distance (descending) and select most diverse individuals
    distances.sort((a, b) => b.distance - a.distance);

    return distances.slice(0, count).map(d => d.individual);
  }

  /**
   * Calculates the Euclidean distance between two chromosomes.
   * 
   * @param chromosome1 The first chromosome
   * @param chromosome2 The second chromosome
   * @returns The distance between the chromosomes
   */
  private calculateDistance(chromosome1: any[], chromosome2: any[]): number {
    let sum = 0;

    for (let i = 0; i < chromosome1.length; i++) {
      // Handle different types of gene values
      if (typeof chromosome1[i] === 'number' && typeof chromosome2[i] === 'number') {
        sum += Math.pow(chromosome1[i] - chromosome2[i], 2);
      } else if (chromosome1[i] !== chromosome2[i]) {
        sum += 1; // For non-numeric values, count 1 if different
      }
    }

    return Math.sqrt(sum);
  }

  /**
   * Calculates diversity metrics for a population.
   * 
   * @param individuals The individuals
   * @param parameters The genetic parameters
   * @returns The diversity metrics
   */
  private calculateDiversityMetrics(individuals: Individual[], parameters: GeneticParameter[]): DiversityMetrics {
    // Calculate genetic diversity (average distance between individuals)
    let totalDistance = 0;
    let pairCount = 0;

    for (let i = 0; i < individuals.length; i++) {
      for (let j = i + 1; j < individuals.length; j++) {
        totalDistance += this.calculateDistance(
          individuals[i].chromosome,
          individuals[j].chromosome
        );
        pairCount++;
      }
    }

    const geneticDiversity = pairCount > 0 ? totalDistance / pairCount : 0;

    // Calculate phenotypic diversity (diversity of fitness values)
    const fitnessValues = individuals.map(ind => ind.fitness as number);
    const uniqueFitnessValues = new Set(fitnessValues.map(f => f.toFixed(4))).size;
    const phenotypicDiversity = uniqueFitnessValues / individuals.length;

    // Calculate distribution statistics for each parameter
    const distributionStats = {
      mean: {} as Record<string, number>,
      variance: {} as Record<string, number>,
      skewness: {} as Record<string, number>
    };

    for (let i = 0; i < parameters.length; i++) {
      const param = parameters[i];
      const values = individuals.map(ind => ind.chromosome[i]);

      // Calculate mean
      const mean = values.reduce((sum, val) => {
        if (typeof val === 'number') {
          return sum + val;
        }
        return sum;
      }, 0) / values.length;

      // Calculate variance
      const variance = values.reduce((sum, val) => {
        if (typeof val === 'number') {
          return sum + Math.pow(val - mean, 2);
        }
        return sum;
      }, 0) / values.length;

      // Calculate skewness
      const skewness = values.reduce((sum, val) => {
        if (typeof val === 'number') {
          return sum + Math.pow(val - mean, 3);
        }
        return sum;
      }, 0) / (values.length * Math.pow(variance, 1.5) || 1);

      distributionStats.mean[param.name] = mean;
      distributionStats.variance[param.name] = variance;
      distributionStats.skewness[param.name] = skewness;
    }

    // Calculate entropy measure (Shannon entropy of parameter values)
    const entropy = this.calculateEntropyMeasure(individuals, parameters);

    // Count niches (clusters of similar individuals)
    const nicheCount = this.countNiches(individuals);

    return {
      geneticDiversity,
      phenotypicDiversity,
      nicheCount,
      entropyMeasure: entropy,
      distributionStats
    };
  }

  /**
   * Calculates the entropy measure for a population.
   * 
   * @param individuals The individuals
   * @param parameters The genetic parameters
   * @returns The entropy measure
   */
  private calculateEntropyMeasure(individuals: Individual[], parameters: GeneticParameter[]): number {
    let totalEntropy = 0;

    for (let i = 0; i < parameters.length; i++) {
      const param = parameters[i];

      // Skip non-categorical parameters
      if (param.type !== GeneType.Nominal && param.type !== GeneType.Binary) {
        continue;
      }

      // Count frequency of each value
      const valueCounts = new Map<any, number>();
      
      for (const individual of individuals) {
        const value = individual.chromosome[i];
        valueCounts.set(value, (valueCounts.get(value) || 0) + 1);
      }

      // Calculate entropy for this parameter
      let paramEntropy = 0;
      
      for (const count of valueCounts.values()) {
        const p = count / individuals.length;
        paramEntropy -= p * Math.log2(p);
      }

      totalEntropy += paramEntropy;
    }

    // Normalize by number of parameters
    return totalEntropy / parameters.length;
  }

  /**
   * Counts the niches in a population.
   * 
   * @param individuals The individuals
   * @returns The number of niches
   */
  private countNiches(individuals: Individual[]): number {
    // Simple clustering: count how many different "clusters" of similar individuals exist
    // This is a simplified implementation - in a real system, would use a more sophisticated
    // clustering algorithm like DBSCAN or hierarchical clustering

    const visited = new Set<string>();
    let nicheCount = 0;

    for (const individual of individuals) {
      if (visited.has(individual.id)) {
        continue;
      }

      // Found a new niche
      nicheCount++;
      visited.add(individual.id);

      // Find all individuals in the same niche
      for (const other of individuals) {
        if (other.id !== individual.id && !visited.has(other.id)) {
          const distance = this.calculateDistance(individual.chromosome, other.chromosome);
          
          // Use a simple threshold to determine if in the same niche
          if (distance < 0.3) {
            visited.add(other.id);
          }
        }
      }
    }

    return nicheCount;
  }

  /**
   * Stores evolution statistics for a population.
   * 
   * @param runId The run ID
   * @param population The population
   * @param parameters The genetic parameters
   * @param options Population management options
   */
  private async storeEvolutionStats(
    runId: string,
    population: Population,
    parameters: GeneticParameter[],
    options: PopulationManagementOptions
  ): Promise<void> {
    if (!this.evolutionHistory.has(runId)) {
      this.evolutionHistory.set(runId, []);
    }

    const history = this.evolutionHistory.get(runId)!;
    
    // Calculate evolution statistics
    const stats: EvolutionStats = {
      generation: population.generation,
      populationSize: population.individuals.length,
      bestFitness: population.metadata?.bestFitness || 0,
      meanFitness: population.metadata?.averageFitness || 0,
      fitnessVariance: this.calculateFitnessVariance(population.individuals),
      diversityMetrics: population.metadata?.diversityMetrics || this.calculateDiversityMetrics(population.individuals, parameters),
      constraintViolationRate: this.calculateConstraintViolationRate(population.individuals, parameters, options),
      feasibleSolutionRate: 1 - this.calculateConstraintViolationRate(population.individuals, parameters, options)
    };

    // Add species stats if using multi-population strategy
    if (options.diversityStrategy === DiversityStrategy.MultiPopulation && this.subpopulations.has(runId)) {
      const subpopulations = this.subpopulations.get(runId)!;
      
      stats.speciesStats = subpopulations.map(subpop => ({
        id: subpop.id,
        size: subpop.individuals.length,
        meanFitness: subpop.individuals.reduce((sum, ind) => sum + (ind.fitness as number), 0) / subpop.individuals.length,
        bestFitness: Math.max(...subpop.individuals.map(ind => ind.fitness as number))
      }));
    }

    // Add adaptive parameter values if enabled
    if (options.enableAdaptiveControl) {
      stats.adaptiveParameterValues = {
        mutationRate: options.mutationRate || 0.1,
        crossoverRate: options.crossoverRate || 0.8,
        selectionPressure: 0.5, // Example value
        nichingRadius: options.nicheRadius || 0.1
      };
    }

    // Store statistics
    history.push(stats);

    // Limit history size
    const maxHistorySize = 100;
    if (history.length > maxHistorySize) {
      // Keep first, last, and evenly spaced entries
      const toKeep = [0, history.length - 1];
      const step = history.length / (maxHistorySize - 2);
      
      for (let i = 1; i < maxHistorySize - 1; i++) {
        toKeep.push(Math.floor(i * step));
      }
      
      const newHistory = toKeep.sort((a, b) => a - b).map(i => history[i]);
      this.evolutionHistory.set(runId, newHistory);
    }
  }

  /**
   * Calculates the variance of fitness values in a population.
   * 
   * @param individuals The individuals
   * @returns The fitness variance
   */
  private calculateFitnessVariance(individuals: Individual[]): number {
    const fitnessValues = individuals.map(ind => ind.fitness as number);
    const mean = fitnessValues.reduce((sum, val) => sum + val, 0) / fitnessValues.length;
    
    return fitnessValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / fitnessValues.length;
  }

  /**
   * Calculates the constraint violation rate in a population.
   * 
   * @param individuals The individuals
   * @param parameters The genetic parameters
   * @param options Population management options
   * @returns The constraint violation rate
   */
  private calculateConstraintViolationRate(
    individuals: Individual[],
    parameters: GeneticParameter[],
    options: PopulationManagementOptions
  ): number {
    // In a real implementation, this would check actual constraints
    // For now, return a random value between 0 and 0.3
    return Math.random() * 0.3;
  }

  /**
   * Gets information about a population.
   * 
   * @param runId The run ID
   * @returns Information about the population
   */
  getPopulationInfo(runId: string): any {
    if (!this.populations.has(runId)) {
      throw new Error(`Population for run ID ${runId} not found`);
    }

    const population = this.populations.get(runId)!;
    const evolutionHistory = this.evolutionHistory.get(runId) || [];
    const subpopulations = this.subpopulations.get(runId) || [];

    return {
      runId,
      generation: population.generation,
      populationSize: population.individuals.length,
      bestFitness: population.metadata?.bestFitness,
      averageFitness: population.metadata?.averageFitness,
      diversityMetrics: population.metadata?.diversityMetrics,
      subpopulationCount: subpopulations.length,
      historyLength: evolutionHistory.length,
      stagnationCounter: population.metadata?.stagnationCounter || 0
    };
  }

  /**
   * Gets evolution history for a population.
   * 
   * @param runId The run ID
   * @returns Evolution history
   */
  getEvolutionHistory(runId: string): EvolutionStats[] {
    if (!this.evolutionHistory.has(runId)) {
      throw new Error(`Evolution history for run ID ${runId} not found`);
    }

    return this.evolutionHistory.get(runId)!;
  }

  /**
   * Gets the convergence status of a population.
   * 
   * @param runId The run ID
   * @param parameters The genetic parameters
   * @returns Convergence status
   */
  getConvergenceStatus(runId: string, parameters: GeneticParameter[]): {
    isConverged: boolean;
    convergenceMeasure: number;
    diversityMeasure: number;
    stagnationGenerations: number;
  } {
    if (!this.populations.has(runId)) {
      throw new Error(`Population for run ID ${runId} not found`);
    }

    const population = this.populations.get(runId)!;
    const evolutionHistory = this.evolutionHistory.get(runId) || [];

    // Calculate convergence measure (normalized improvement rate over last 10 generations)
    let convergenceMeasure = 0;
    
    if (evolutionHistory.length >= 10) {
      const recentHistory = evolutionHistory.slice(-10);
      const initialFitness = recentHistory[0].bestFitness;
      const finalFitness = recentHistory[recentHistory.length - 1].bestFitness;
      
      convergenceMeasure = (finalFitness - initialFitness) / Math.abs(initialFitness || 1);
    }

    // Get diversity measure
    const diversityMeasure = population.metadata?.diversityMetrics?.geneticDiversity || 0;
    
    // Get stagnation generations
    const stagnationGenerations = population.metadata?.stagnationCounter || 0;
    
    // Check if converged
    const isConverged = convergenceMeasure < 0.01 && stagnationGenerations > 5;

    return {
      isConverged,
      convergenceMeasure,
      diversityMeasure,
      stagnationGenerations
    };
  }

  /**
   * Gets health status information.
   * 
   * @returns Health status
   */
  getHealthStatus(): any {
    return {
      component: "population_manager",
      state: this.isInitialized ? HealthState.Healthy : HealthState.Unhealthy,
      message: this.isInitialized ? 
        "Population Manager is healthy" : 
        "Population Manager is not initialized",
      timestamp: new Date().toISOString(),
      details: {
        initialized: this.isInitialized,
        managedPopulations: this.populations.size,
        diversityStrategies: Array.from(this.diversityStrategies.keys()),
        constraintStrategies: Array.from(this.constraintStrategies.keys()),
        initializationStrategies: Array.from(this.initializationStrategies.keys())
      }
    };
  }

  /**
   * Registers diversity strategies.
   */
  private registerDiversityStrategies(): void {
    // Diversity functions
    type DiversityFunction = (
      offspring: Individual[],
      currentPopulation: Population,
      options: any
    ) => Promise<Individual[]>;

    // Standard diversity strategy
    const standardDiversity: DiversityFunction = async (offspring, currentPopulation, options) => {
      return offspring;
    };

    // Enhanced diversity strategy
    const enhancedDiversity: DiversityFunction = async (offspring, currentPopulation, options) => {
      // Calculate average distance from each offspring to all current individuals
      const distances = offspring.map(ind => {
        const avgDistance = currentPopulation.individuals.reduce(
          (sum, current) => sum + this.calculateDistance(ind.chromosome, current.chromosome),
          0
        ) / currentPopulation.individuals.length;

        return { individual: ind, distance: avgDistance };
      });

      // Sort by distance (descending)
      distances.sort((a, b) => b.distance - a.distance);

      // Choose diverse individuals
      const selectionCount = Math.min(offspring.length, options.populationSize - (options.elitismCount || 0));

      return distances.slice(0, selectionCount).map(d => d.individual);
    };

    // Niched conservation strategy
    const nichedConservation: DiversityFunction = async (offspring, currentPopulation, options) => {
      // Group individuals into niches
      const niches = this.clusterIntoNiches(
        [...currentPopulation.individuals, ...offspring],
        options.nicheRadius || 0.1
      );

      // Select representatives from each niche
      const selected: Individual[] = [];
      const nicheOrder = [...niches.keys()].sort(() => Math.random() - 0.5); // Randomize order

      // Keep picking from niches until we have enough individuals
      while (selected.length < options.populationSize - (options.elitismCount || 0)) {
        for (const nicheId of nicheOrder) {
          const niche = niches.get(nicheId)!;
          
          if (niche.length > 0) {
            // Sort niche by fitness
            niche.sort((a, b) => (b.fitness as number) - (a.fitness as number));
            
            // Select best individual from niche
            selected.push(niche.shift()!);
            
            if (selected.length >= options.populationSize - (options.elitismCount || 0)) {
              break;
            }
          }
        }
        
        // If we've exhausted all niches but still need individuals, create duplicates
        if (selected.length < options.populationSize - (options.elitismCount || 0) && 
            niches.size === 0) {
          break;
        }
      }

      return selected;
    };

    // Dynamic niching strategy
    const dynamicNiching: DiversityFunction = async (offspring, currentPopulation, options) => {
      // This strategy adapts niche radius based on population diversity
      const diversity = currentPopulation.metadata?.diversityMetrics?.geneticDiversity || 0;
      
      // Adjust niche radius based on diversity
      const adaptiveRadius = Math.max(0.05, Math.min(0.3, 0.2 - diversity));
      
      // Use niched conservation with adaptive radius
      const niches = this.clusterIntoNiches(
        [...currentPopulation.individuals, ...offspring],
        adaptiveRadius
      );

      // Rest of the algorithm is similar to niched conservation
      const selected: Individual[] = [];
      const nicheOrder = [...niches.keys()].sort(() => Math.random() - 0.5);

      while (selected.length < options.populationSize - (options.elitismCount || 0)) {
        for (const nicheId of nicheOrder) {
          const niche = niches.get(nicheId)!;
          
          if (niche.length > 0) {
            niche.sort((a, b) => (b.fitness as number) - (a.fitness as number));
            selected.push(niche.shift()!);
            
            if (selected.length >= options.populationSize - (options.elitismCount || 0)) {
              break;
            }
          }
        }
        
        if (selected.length < options.populationSize - (options.elitismCount || 0) && 
            niches.size === 0) {
          break;
        }
      }

      return selected;
    };

    // Register strategies
    this.diversityStrategies.set(DiversityStrategy.Standard, standardDiversity);
    this.diversityStrategies.set(DiversityStrategy.EnhancedDiversity, enhancedDiversity);
    this.diversityStrategies.set(DiversityStrategy.NichedConservation, nichedConservation);
    this.diversityStrategies.set(DiversityStrategy.DynamicNiching, dynamicNiching);
  }

  /**
   * Registers constraint strategies.
   */
  private registerConstraintStrategies(): void {
    // Constraint functions
    type ConstraintFunction = (
      individuals: Individual[],
      parameters: GeneticParameter[],
      options: any
    ) => Promise<Individual[]>;

    // Penalty function strategy
    const penaltyFunction: ConstraintFunction = async (individuals, parameters, options) => {
      // In a real implementation, this would apply penalties to fitness values
      // based on constraint violations
      return individuals;
    };

    // Repair operator strategy
    const repairOperator: ConstraintFunction = async (individuals, parameters, options) => {
      // Clone individuals to avoid modifying originals
      const repairedIndividuals = individuals.map(ind => ({
        ...ind,
        chromosome: [...ind.chromosome]
      }));

      // Apply economic domain-specific repair rules
      for (const individual of repairedIndividuals) {
        // Enforce bounds on parameters
        for (let i = 0; i < parameters.length; i++) {
          const param = parameters[i];
          
          if (param.type === GeneType.Real || param.type === GeneType.Integer) {
            if (param.min !== undefined && individual.chromosome[i] < param.min) {
              individual.chromosome[i] = param.min;
            }
            
            if (param.max !== undefined && individual.chromosome[i] > param.max) {
              individual.chromosome[i] = param.max;
            }
          }
        }

        // Apply economic policy constraints if they exist
        if (options.economicDomainParams) {
          // Example: Enforce monetary policy bounds
          const monetaryPolicyIndex = parameters.findIndex(p => p.name === 'interest_rate_adjustment');
          if (monetaryPolicyIndex >= 0 && options.economicDomainParams.monetaryPolicyBounds) {
            const [min, max] = options.economicDomainParams.monetaryPolicyBounds;
            individual.chromosome[monetaryPolicyIndex] = Math.max(
              min,
              Math.min(max, individual.chromosome[monetaryPolicyIndex])
            );
          }

          // Example: Enforce fiscal constraint (total spending adjustments sum to zero)
          const fiscalIndices = parameters
            .map((p, i) => p.name.includes('spending') ? i : -1)
            .filter(i => i >= 0);
          
          if (fiscalIndices.length > 1 && options.economicDomainParams.fiscalConstraintWeight) {
            const totalAdjustment = fiscalIndices.reduce(
              (sum, i) => sum + individual.chromosome[i],
              0
            );
            
            // If total adjustment is not close to zero, distribute the difference
            if (Math.abs(totalAdjustment) > 0.01) {
              const correction = totalAdjustment / fiscalIndices.length;
              
              for (const i of fiscalIndices) {
                individual.chromosome[i] -= correction;
              }
            }
          }
        }
      }

      return repairedIndividuals;
    };

    // Death penalty strategy
    const deathPenalty: ConstraintFunction = async (individuals, parameters, options) => {
      // Filter out individuals that violate constraints
      // In a real implementation, would check actual constraints
      
      // For now, ensure we don't eliminate too many individuals
      const minIndividuals = Math.max(10, Math.floor(options.populationSize * 0.5));
      
      if (individuals.length <= minIndividuals) {
        return individuals;
      }
      
      // Randomly mark some individuals as violating constraints
      return individuals.filter(() => Math.random() > 0.1);
    };

    // Register strategies
    this.constraintStrategies.set(ConstraintStrategy.PenaltyFunction, penaltyFunction);
    this.constraintStrategies.set(ConstraintStrategy.RepairOperator, repairOperator);
    this.constraintStrategies.set(ConstraintStrategy.DeathPenalty, deathPenalty);
  }

  /**
   * Registers initialization strategies.
   */
  private registerInitializationStrategies(): void {
    // Initialization functions
    type InitializationFunction = (
      runId: string,
      parameters: GeneticParameter[],
      options: any
    ) => Promise<Individual[]>;

    // Random initialization strategy
    const randomInitialization: InitializationFunction = async (runId, parameters, options) => {
      const individuals: Individual[] = [];
      
      for (let i = 0; i < options.populationSize; i++) {
        const chromosome: any[] = [];
        
        // Generate random values for each parameter
        for (const param of parameters) {
          switch (param.type) {
            case GeneType.Binary:
              chromosome.push(Math.random() > 0.5 ? 1 : 0);
              break;
            
            case GeneType.Integer:
              if (param.min !== undefined && param.max !== undefined) {
                const range = param.max - param.min;
                chromosome.push(Math.floor(Math.random() * range) + param.min);
              } else {
                chromosome.push(Math.floor(Math.random() * 100));
              }
              break;
            
            case GeneType.Real:
              if (param.min !== undefined && param.max !== undefined) {
                const range = param.max - param.min;
                let value = Math.random() * range + param.min;
                
                // Apply precision if specified
                if (param.precision !== undefined) {
                  const precision = 1 / param.precision;
                  value = Math.round(value * precision) / precision;
                }
                
                chromosome.push(value);
              } else {
                chromosome.push(Math.random() * 100);
              }
              break;
            
            case GeneType.Nominal:
              if (param.options && param.options.length > 0) {
                const randomIndex = Math.floor(Math.random() * param.options.length);
                chromosome.push(param.options[randomIndex]);
              } else {
                chromosome.push(null);
              }
              break;
            
            default:
              chromosome.push(param.defaultValue !== undefined ? param.defaultValue : 0);
              break;
          }
        }
        
        // Create individual
        individuals.push({
          id: `ind_${runId}_${i}_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
          chromosome,
          fitness: 0, // Will be evaluated later
          age: 0,
          metadata: {
            creationTimestamp: new Date().toISOString(),
            fitnessHistory: []
          },
          decoded: this.decodeChromosome(chromosome, parameters)
        });
      }
      
      return individuals;
    };

    // Historically informed initialization strategy
    const historicallyInformedInitialization: InitializationFunction = async (runId, parameters, options) => {
      // This strategy would use historical data to seed the initial population
      // For demonstration, create a mix of random and "informed" individuals
      
      const individuals: Individual[] = [];
      const randomCount = Math.floor(options.populationSize * 0.7); // 70% random
      const informedCount = options.populationSize - randomCount; // 30% informed
      
      // Create random individuals
      const randomOptions = { ...options, populationSize: randomCount };
      const randomIndividuals = await randomInitialization(runId, parameters, randomOptions);
      individuals.push(...randomIndividuals);
      
      // Create "informed" individuals based on economic domain knowledge
      for (let i = 0; i < informedCount; i++) {
        const chromosome: any[] = [];
        
        // Generate values for each parameter based on domain knowledge
        for (const param of parameters) {
          // For specific economic parameters, use informed values
          if (param.name === 'interest_rate_adjustment') {
            // Based on historical effective ranges
            chromosome.push(Math.random() * 0.5 + 0.25); // 0.25 to 0.75
          } else if (param.name === 'fiscal_stimulus_percentage') {
            // Based on typical stimulus packages
            chromosome.push(Math.random() * 1.5 + 0.5); // 0.5 to 2.0
          } else if (param.name === 'tariff_rate_adjustment') {
            // Historically effective tariff adjustments
            chromosome.push(Math.random() * 10 - 5); // -5 to 5
          } else if (param.name.includes('tax')) {
            // Tax adjustments tend to be small
            chromosome.push(Math.random() * 2 - 1); // -1 to 1
          } else {
            // Use random initialization for other parameters
            switch (param.type) {
              case GeneType.Binary:
                chromosome.push(Math.random() > 0.5 ? 1 : 0);
                break;
              
              case GeneType.Integer:
                if (param.min !== undefined && param.max !== undefined) {
                  const range = param.max - param.min;
                  chromosome.push(Math.floor(Math.random() * range) + param.min);
                } else {
                  chromosome.push(Math.floor(Math.random() * 100));
                }
                break;
              
              case GeneType.Real:
                if (param.min !== undefined && param.max !== undefined) {
                  const range = param.max - param.min;
                  let value = Math.random() * range + param.min;
                  
                  // Apply precision if specified
                  if (param.precision !== undefined) {
                    const precision = 1 / param.precision;
                    value = Math.round(value * precision) / precision;
                  }
                  
                  chromosome.push(value);
                } else {
                  chromosome.push(Math.random() * 100);
                }
                break;
              
              case GeneType.Nominal:
                if (param.options && param.options.length > 0) {
                  const randomIndex = Math.floor(Math.random() * param.options.length);
                  chromosome.push(param.options[randomIndex]);
                } else {
                  chromosome.push(null);
                }
                break;
              
              default:
                chromosome.push(param.defaultValue !== undefined ? param.defaultValue : 0);
                break;
            }
          }
        }
        
        // Create individual
        individuals.push({
          id: `ind_${runId}_h${i}_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
          chromosome,
          fitness: 0, // Will be evaluated later
          age: 0,
          metadata: {
            creationTimestamp: new Date().toISOString(),
            fitnessHistory: [],
            creationMethod: 'historically_informed'
          },
          decoded: this.decodeChromosome(chromosome, parameters)
        });
      }
      
      return individuals;
    };

    // Register strategies
    this.initializationStrategies.set(InitializationStrategy.Random, randomInitialization);
    this.initializationStrategies.set(InitializationStrategy.HistoricallyInformed, historicallyInformedInitialization);
  }

  /**
   * Clusters individuals into niches.
   * 
   * @param individuals The individuals to cluster
   * @param radius The niche radius
   * @returns A map of niche IDs to individuals
   */
  private clusterIntoNiches(individuals: Individual[], radius: number): Map<string, Individual[]> {
    const niches = new Map<string, Individual[]>();
    const assigned = new Set<string>();

    // Assign each individual to a niche
    for (const individual of individuals) {
      // Skip if already assigned
      if (assigned.has(individual.id)) {
        continue;
      }

      // Found a new niche
      const nicheId = `niche_${niches.size}`;
      const niche: Individual[] = [individual];
      assigned.add(individual.id);

      // Find all individuals in the same niche
      for (const other of individuals) {
        if (other.id !== individual.id && !assigned.has(other.id)) {
          const distance = this.calculateDistance(individual.chromosome, other.chromosome);
          
          // Check if within niche radius
          if (distance < radius) {
            niche.push(other);
            assigned.add(other.id);
          }
        }
      }

      // Store niche
      niches.set(nicheId, niche);
    }

    return niches;
  }

  /**
   * Decodes a chromosome into parameter values.
   * 
   * @param chromosome The chromosome
   * @param parameters The parameters
   * @returns Decoded parameter values
   */
  private decodeChromosome(chromosome: any[], parameters: GeneticParameter[]): Record<string, any> {
    const decoded: Record<string, any> = {};
    
    for (let i = 0; i < parameters.length; i++) {
      const param = parameters[i];
      decoded[param.name] = chromosome[i];
    }
    
    return decoded;
  }
}

/**
 * Type definition for diversity function.
 */
type DiversityFunction = (
  offspring: Individual[],
  currentPopulation: Population,
  options: any
) => Promise<Individual[]>;

/**
 * Type definition for constraint function.
 */
type ConstraintFunction = (
  individuals: Individual[],
  parameters: GeneticParameter[],
  options: any
) => Promise<Individual[]>;

/**
 * Type definition for initialization function.
 */
type InitializationFunction = (
  runId: string,
  parameters: GeneticParameter[],
  options: any
) => Promise<Individual[]>;