/**
 * Genetic Algorithm Client
 *
 * Client for interacting with the Genetic Algorithm service.
 * Provides an interface for optimizing economic strategies and policies
 * using a comprehensive genetic algorithm framework.
 */

import { HealthState } from '../monitoring/health_types';
import {
  GeneticAlgorithmFramework,
  GeneticProblemConfiguration,
  GeneticAlgorithmOptions,
  GeneticAlgorithmResult,
  AlgorithmRunStatus,
  GeneticOperatorType,
  TerminationCriteria,
  FrameworkComponent,
  GeneType,
  Individual,
  Population
} from './genetic_algorithm_framework';

import {
  PopulationManager,
  DiversityStrategy,
  ConstraintStrategy,
  InitializationStrategy,
  PopulationManagementOptions,
  EvolutionStats
} from './population_manager';

/**
 * Optimization request parameters.
 */
export interface OptimizationRequest {
  // Basic parameters
  fitnessFunction: string;
  domain?: string;
  populationSize?: number;
  maxGenerations?: number;

  // Problem-specific parameters
  problemName?: string;
  problemDescription?: string;
  parameters?: Array<{
    name: string;
    type?: string;
    min?: number;
    max?: number;
    options?: string[] | number[];
    defaultValue?: any;
  }>;

  // Algorithm control parameters
  crossoverRate?: number;
  mutationRate?: number;
  selectionMethod?: string;
  crossoverMethod?: string;
  mutationMethod?: string;

  // Advanced parameters
  initialConditions?: any;
  constraints?: Array<any>;
  multiObjective?: boolean;
  fitnessObjectives?: string[];

  // Configuration reference
  useConfigId?: string;

  // Population management parameters
  diversityStrategy?: string;
  constraintStrategy?: string;
  initializationStrategy?: string;
  nicheRadius?: number;
  diversityThreshold?: number;
  immigrationRate?: number;
  subpopulationCount?: number;
  enableAdaptiveControl?: boolean;

  // Economic domain parameters
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

  // Run control
  saveHistory?: boolean;
  waitForCompletion?: boolean;
  timeoutMs?: number;
}

/**
 * Domain-specific optimization presets.
 */
export enum OptimizationPreset {
  StagflationMitigation = 'stagflation_mitigation',
  TradeBalanceOptimization = 'trade_balance_optimization',
  FiscalPolicyOptimization = 'fiscal_policy_optimization',
  MonetaryPolicyOptimization = 'monetary_policy_optimization',
  LaborMarketOptimization = 'labor_market_optimization',
  SupplyChainResilience = 'supply_chain_resilience',
  SectoralCompetitiveAnalysis = 'sectoral_competitive_analysis',
  InfrastructureInvestmentOptimization = 'infrastructure_investment_optimization'
}

/**
 * Client for the Genetic Algorithm service.
 */
export class GeneticAlgorithmClient {
  private endpoint: string;
  private isInitialized: boolean;
  private isStarted: boolean;
  private framework: GeneticAlgorithmFramework;
  private populationManager: PopulationManager;
  private activeRuns: Map<string, string> = new Map(); // Maps requestId to runId
  private runPopulations: Map<string, string> = new Map(); // Maps runId to population runId

  /**
   * Creates a new GeneticAlgorithmClient instance.
   *
   * @param endpoint The endpoint of the genetic algorithm service
   */
  constructor(endpoint: string = 'http://localhost:5002/api/optimize') {
    this.endpoint = endpoint;
    this.isInitialized = false;
    this.isStarted = false;
    this.framework = new GeneticAlgorithmFramework();
    this.populationManager = new PopulationManager();
  }

  /**
   * Initializes the client.
   *
   * @returns A promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    console.log('Initializing Genetic Algorithm Client...');

    // Initialize the genetic algorithm framework
    await this.framework.initialize();

    // Initialize the population manager
    await this.populationManager.initialize();

    this.isInitialized = true;
    console.log('Genetic Algorithm Client initialized successfully');
  }

  /**
   * Starts the client.
   *
   * @returns A promise that resolves when startup is complete
   */
  async start(): Promise<void> {
    if (!this.isInitialized) {
      throw new Error('Genetic Algorithm Client must be initialized before starting');
    }

    console.log('Starting Genetic Algorithm Client...');

    // In a real implementation, this would start any background processes,
    // establish persistent connections, etc.

    // Register event listeners between framework and population manager
    this.setupEventListeners();

    this.isStarted = true;
    console.log('Genetic Algorithm Client started successfully');
  }

  /**
   * Stops the client.
   *
   * @returns A promise that resolves when shutdown is complete
   */
  async stop(): Promise<void> {
    if (!this.isStarted) {
      console.log('Genetic Algorithm Client is not started');
      return;
    }

    console.log('Stopping Genetic Algorithm Client...');

    // In a real implementation, this would clean up resources,
    // close connections, etc.

    this.isStarted = false;
    console.log('Genetic Algorithm Client stopped successfully');
  }

  /**
   * Optimizes parameters using genetic algorithms.
   *
   * @param params Optimization parameters
   * @returns Optimization result
   */
  async optimize(params: OptimizationRequest): Promise<GeneticAlgorithmResult> {
    if (!this.isInitialized || !this.isStarted) {
      throw new Error('Genetic Algorithm Client must be initialized and started before optimizing');
    }

    console.log(`Optimizing with fitness function: ${params.fitnessFunction}`);

    // Generate a unique request ID
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;

    // If useConfigId is provided, use existing configuration
    if (params.useConfigId) {
      return this.runOptimizationWithConfig(requestId, params);
    }

    // Check for preset optimization problems
    const preset = this.getPresetForFitnessFunction(params.fitnessFunction);
    if (preset) {
      return this.runOptimizationWithPreset(requestId, params, preset);
    }

    // Create a new problem configuration
    const config = this.createProblemConfiguration(params);

    // Register the configuration
    const configId = this.framework.registerProblemConfiguration(config);

    // Start the optimization run
    return this.startOptimizationRun(requestId, configId, params);
  }

  /**
   * Gets a preset problem configuration for a fitness function.
   *
   * @param fitnessFunction The fitness function
   * @returns Preset name or undefined
   */
  private getPresetForFitnessFunction(fitnessFunction: string): OptimizationPreset | undefined {
    // Map fitness function to preset
    const presetMappings: Record<string, OptimizationPreset> = {
      'stagflation_mitigation': OptimizationPreset.StagflationMitigation,
      'trade_balance_optimization': OptimizationPreset.TradeBalanceOptimization,
      'fiscal_policy_optimization': OptimizationPreset.FiscalPolicyOptimization,
      'monetary_policy_optimization': OptimizationPreset.MonetaryPolicyOptimization,
      'labor_market_optimization': OptimizationPreset.LaborMarketOptimization,
      'supply_chain_resilience': OptimizationPreset.SupplyChainResilience,
      'sectoral_competitive_analysis': OptimizationPreset.SectoralCompetitiveAnalysis,
      'infrastructure_investment_optimization': OptimizationPreset.InfrastructureInvestmentOptimization
    };

    return presetMappings[fitnessFunction];
  }

  /**
   * Runs optimization with an existing configuration.
   *
   * @param requestId The request ID
   * @param params Optimization parameters
   * @returns Optimization result
   */
  private async runOptimizationWithConfig(
    requestId: string,
    params: OptimizationRequest
  ): Promise<GeneticAlgorithmResult> {
    if (!params.useConfigId) {
      throw new Error('Configuration ID is required');
    }

    // Override algorithm options if provided
    const runOptions = this.extractRunOptions(params);

    // Get configuration to access parameters
    const config = this.framework.listConfigurations().find(
      conf => conf.id === params.useConfigId
    );

    if (!config) {
      throw new Error(`Configuration with ID ${params.useConfigId} not found`);
    }

    // Create population management options
    const populationOptions = this.createPopulationManagementOptions(params);

    // Start the run
    const runId = await this.framework.startRun(
      params.useConfigId,
      params.initialConditions,
      runOptions
    );

    // Store the run ID
    this.activeRuns.set(requestId, runId);

    // Get the parameters from the configuration
    const fullConfig = this.framework.getProblemConfiguration(params.useConfigId);
    if (!fullConfig) {
      throw new Error(`Full configuration with ID ${params.useConfigId} not found`);
    }

    // Create and initialize a population with the population manager
    const populationRunId = `pop_${runId}`;
    await this.populationManager.createPopulation(
      populationRunId,
      fullConfig.parameters,
      populationOptions
    );

    // Store the association between GA run and population
    this.runPopulations.set(runId, populationRunId);

    // If waitForCompletion is specified, wait for the run to complete
    if (params.waitForCompletion) {
      return this.waitForRunCompletion(runId, params.timeoutMs);
    }

    // Otherwise, return the current status
    const status = this.framework.getRunStatus(runId);

    // If already completed, return results
    if (status.status === AlgorithmRunStatus.Completed) {
      return this.framework.getRunResults(runId);
    }

    // If not completed, return a placeholder result
    return {
      runMetadata: status,
      solutions: [],
      problemSummary: {
        problemName: 'Optimization in progress',
        domainType: '',
        parametersOptimized: [],
        constraints: []
      },
      performanceMetrics: {
        totalRunTimeMs: 0,
        evaluationsPerSecond: 0,
        generationCount: 0,
        improvementRate: []
      }
    };
  }

  /**
   * Runs optimization with a preset configuration.
   *
   * @param requestId The request ID
   * @param params Optimization parameters
   * @param preset The preset to use
   * @returns Optimization result
   */
  private async runOptimizationWithPreset(
    requestId: string,
    params: OptimizationRequest,
    preset: OptimizationPreset
  ): Promise<GeneticAlgorithmResult> {
    // Get preset configuration ID
    const configId = this.framework.getPredefinedConfiguration(preset);

    if (!configId) {
      throw new Error(`Preset configuration ${preset} not found`);
    }

    // Override algorithm options if provided
    const runOptions = this.extractRunOptions(params);

    // Start the run
    const runId = await this.framework.startRun(
      configId,
      params.initialConditions,
      runOptions
    );

    // Store the run ID
    this.activeRuns.set(requestId, runId);

    // If waitForCompletion is specified, wait for the run to complete
    if (params.waitForCompletion) {
      return this.waitForRunCompletion(runId, params.timeoutMs);
    }

    // Otherwise, return the current status
    const status = this.framework.getRunStatus(runId);

    // If already completed, return results
    if (status.status === AlgorithmRunStatus.Completed) {
      return this.framework.getRunResults(runId);
    }

    // If not completed, return a placeholder result
    return {
      runMetadata: status,
      solutions: [],
      problemSummary: {
        problemName: 'Optimization in progress',
        domainType: '',
        parametersOptimized: [],
        constraints: []
      },
      performanceMetrics: {
        totalRunTimeMs: 0,
        evaluationsPerSecond: 0,
        generationCount: 0,
        improvementRate: []
      }
    };
  }

  /**
   * Creates a problem configuration from optimization parameters.
   *
   * @param params Optimization parameters
   * @returns Problem configuration
   */
  private createProblemConfiguration(params: OptimizationRequest): GeneticProblemConfiguration {
    // Set default domain if not provided
    const domain = this.mapDomain(params.domain || 'general');

    // Create parameters
    const parameters = params.parameters ?
      params.parameters.map(param => this.createParameter(param)) :
      this.getDefaultParameters(params.fitnessFunction, domain);

    // Create algorithm options
    const algorithmOptions = this.createAlgorithmOptions(params);

    // Create problem configuration
    const config: GeneticProblemConfiguration = {
      problemName: params.problemName || `${params.fitnessFunction} Optimization`,
      problemDescription: params.problemDescription || `Optimization problem for ${params.fitnessFunction}`,
      domainType: domain as any,
      parameters,
      fitnessFunction: params.fitnessFunction,
      fitnessObjectives: params.fitnessObjectives,
      constraints: params.constraints,
      algorithmOptions,
      saveHistory: params.saveHistory !== false,
      components: this.getRelevantComponents(params.fitnessFunction, domain)
    };

    return config;
  }

  /**
   * Maps a domain string to a valid domain type.
   *
   * @param domain The domain string
   * @returns Valid domain type
   */
  private mapDomain(domain: string): string {
    const domainMap: Record<string, string> = {
      'macroeconomic': 'macroeconomic',
      'macro': 'macroeconomic',
      'microeconomic': 'microeconomic',
      'micro': 'microeconomic',
      'monetary': 'monetary',
      'fiscal': 'fiscal',
      'international': 'trade',
      'trade': 'trade',
      'labor': 'labor',
      'general': 'multi_domain'
    };

    return domainMap[domain.toLowerCase()] || 'multi_domain';
  }

  /**
   * Creates a parameter from parameter info.
   *
   * @param paramInfo Parameter info
   * @returns Genetic parameter
   */
  private createParameter(paramInfo: any): any {
    // Map type string to GeneType
    const typeMap: Record<string, GeneType> = {
      'binary': GeneType.Binary,
      'integer': GeneType.Integer,
      'real': GeneType.Real,
      'nominal': GeneType.Nominal,
      'permutation': GeneType.Permutation,
      'tree': GeneType.Tree,
      'mixed': GeneType.Mixed
    };

    // Set default type if not provided
    const type = paramInfo.type ?
      typeMap[paramInfo.type.toLowerCase()] || GeneType.Real :
      GeneType.Real;

    // Create parameter
    return {
      name: paramInfo.name,
      type,
      min: paramInfo.min,
      max: paramInfo.max,
      precision: paramInfo.precision,
      options: paramInfo.options,
      defaultValue: paramInfo.defaultValue,
      mutable: true,
      description: paramInfo.description || `Parameter ${paramInfo.name}`
    };
  }

  /**
   * Gets default parameters for a fitness function and domain.
   *
   * @param fitnessFunction The fitness function
   * @param domain The domain
   * @returns Default parameters
   */
  private getDefaultParameters(fitnessFunction: string, domain: string): any[] {
    // Define default parameters based on fitness function and domain
    switch (fitnessFunction) {
      case 'stagflation_mitigation':
        return [
          {
            name: 'interest_rate_adjustment',
            type: GeneType.Real,
            min: -2,
            max: 2,
            precision: 0.25,
            defaultValue: 0,
            mutable: true,
            description: 'Interest rate adjustment in percentage points'
          },
          {
            name: 'fiscal_stimulus_percentage',
            type: GeneType.Real,
            min: 0,
            max: 5,
            precision: 0.1,
            defaultValue: 1.0,
            mutable: true,
            description: 'Fiscal stimulus as percentage of GDP'
          },
          {
            name: 'supply_side_reform_intensity',
            type: GeneType.Real,
            min: 0,
            max: 10,
            precision: 0.5,
            defaultValue: 3.0,
            mutable: true,
            description: 'Intensity of supply-side reforms (0-10 scale)'
          }
        ];

      case 'trade_balance_optimization':
        return [
          {
            name: 'tariff_rate_adjustment',
            type: GeneType.Real,
            min: -10,
            max: 10,
            precision: 0.5,
            defaultValue: 0,
            mutable: true,
            description: 'Tariff rate adjustment in percentage points'
          },
          {
            name: 'export_incentive_percentage',
            type: GeneType.Real,
            min: 0,
            max: 5,
            precision: 0.1,
            defaultValue: 1.0,
            mutable: true,
            description: 'Export incentives as percentage of value'
          }
        ];

      default:
        // Generic parameters
        return [
          {
            name: 'param1',
            type: GeneType.Real,
            min: 0,
            max: 1,
            precision: 0.01,
            defaultValue: 0.5,
            mutable: true,
            description: 'Parameter 1'
          },
          {
            name: 'param2',
            type: GeneType.Real,
            min: 0,
            max: 1,
            precision: 0.01,
            defaultValue: 0.5,
            mutable: true,
            description: 'Parameter 2'
          },
          {
            name: 'param3',
            type: GeneType.Real,
            min: 0,
            max: 1,
            precision: 0.01,
            defaultValue: 0.5,
            mutable: true,
            description: 'Parameter 3'
          }
        ];
    }
  }

  /**
   * Creates algorithm options from optimization parameters.
   *
   * @param params Optimization parameters
   * @returns Algorithm options
   */
  private createAlgorithmOptions(params: OptimizationRequest): GeneticAlgorithmOptions {
    // Map method strings to GeneticOperatorType
    const methodMap: Record<string, GeneticOperatorType> = {
      'tournament': GeneticOperatorType.TournamentSelection,
      'tournament_selection': GeneticOperatorType.TournamentSelection,
      'roulette': GeneticOperatorType.RouletteWheelSelection,
      'roulette_wheel': GeneticOperatorType.RouletteWheelSelection,
      'roulette_wheel_selection': GeneticOperatorType.RouletteWheelSelection,
      'rank': GeneticOperatorType.RankSelection,
      'rank_selection': GeneticOperatorType.RankSelection,
      'elitist': GeneticOperatorType.ElitistSelection,
      'elitist_selection': GeneticOperatorType.ElitistSelection,
      'single_point': GeneticOperatorType.SinglePointCrossover,
      'single_point_crossover': GeneticOperatorType.SinglePointCrossover,
      'two_point': GeneticOperatorType.TwoPointCrossover,
      'two_point_crossover': GeneticOperatorType.TwoPointCrossover,
      'uniform': GeneticOperatorType.UniformCrossover,
      'uniform_crossover': GeneticOperatorType.UniformCrossover,
      'blend': GeneticOperatorType.BlendCrossover,
      'blend_crossover': GeneticOperatorType.BlendCrossover,
      'gaussian': GeneticOperatorType.GaussianMutation,
      'gaussian_mutation': GeneticOperatorType.GaussianMutation,
      'swap': GeneticOperatorType.SwapMutation,
      'swap_mutation': GeneticOperatorType.SwapMutation,
      'inversion': GeneticOperatorType.InversionMutation,
      'inversion_mutation': GeneticOperatorType.InversionMutation,
      'boundary': GeneticOperatorType.BoundaryMutation,
      'boundary_mutation': GeneticOperatorType.BoundaryMutation,
      'adaptive': GeneticOperatorType.AdaptiveMutation,
      'adaptive_mutation': GeneticOperatorType.AdaptiveMutation
    };

    // Set selection method
    const selectionMethod = params.selectionMethod ?
      methodMap[params.selectionMethod.toLowerCase()] || GeneticOperatorType.TournamentSelection :
      GeneticOperatorType.TournamentSelection;

    // Set crossover method
    const crossoverMethod = params.crossoverMethod ?
      methodMap[params.crossoverMethod.toLowerCase()] || GeneticOperatorType.BlendCrossover :
      GeneticOperatorType.BlendCrossover;

    // Set mutation method
    const mutationMethod = params.mutationMethod ?
      methodMap[params.mutationMethod.toLowerCase()] || GeneticOperatorType.GaussianMutation :
      GeneticOperatorType.GaussianMutation;

    // Create algorithm options
    return {
      populationSize: params.populationSize || 100,
      selectionMethod,
      selectionParameters: { tournamentSize: 5 },
      crossoverMethod,
      crossoverRate: params.crossoverRate || 0.8,
      mutationMethod,
      mutationRate: params.mutationRate || 0.15,
      replacementMethod: GeneticOperatorType.ElitismReplacement,
      replacementParameters: { elitismPercentage: 0.1 },
      elitismCount: 5,
      terminationCriteria: [
        TerminationCriteria.MaxGenerations,
        TerminationCriteria.FitnessStagnation
      ],
      maxGenerations: params.maxGenerations || 100,
      stagnationLimit: 20,
      multiObjective: params.multiObjective || false,
      paretoFrontierSize: 10,
      constraintHandlingMethod: 'penalty',
      economicModelIntegration: true
    };
  }

  /**
   * Gets relevant components for a fitness function and domain.
   *
   * @param fitnessFunction The fitness function
   * @param domain The domain
   * @returns Relevant components
   */
  private getRelevantComponents(fitnessFunction: string, domain: string): FrameworkComponent[] {
    // Base components for all optimizations
    const components: FrameworkComponent[] = [
      FrameworkComponent.EconomicModelIntegration
    ];

    // Add multi-objective optimization for specific fitness functions
    if (
      fitnessFunction === 'stagflation_mitigation' ||
      fitnessFunction === 'trade_balance_optimization'
    ) {
      components.push(FrameworkComponent.MultiObjectiveOptimization);
    }

    // Add domain-specific components
    switch (domain) {
      case 'macroeconomic':
        components.push(FrameworkComponent.MacroeconomicStabilityEvaluation);
        break;

      case 'fiscal':
        components.push(FrameworkComponent.BudgetConstraintEnforcement);
        break;

      case 'trade':
        components.push(FrameworkComponent.DistributionalImpactAssessment);
        break;
    }

    // Add policy constraint enforcement if constraints are specified
    components.push(FrameworkComponent.PolicyConstraintEnforcement);

    return components;
  }

  /**
   * Extracts run options from optimization parameters.
   *
   * @param params Optimization parameters
   * @returns Run options
   */
  private extractRunOptions(params: OptimizationRequest): Partial<GeneticAlgorithmOptions> {
    const options: Partial<GeneticAlgorithmOptions> = {};

    // Extract options that can be overridden
    if (params.populationSize) {
      options.populationSize = params.populationSize;
    }

    if (params.maxGenerations) {
      options.maxGenerations = params.maxGenerations;
    }

    if (params.crossoverRate) {
      options.crossoverRate = params.crossoverRate;
    }

    if (params.mutationRate) {
      options.mutationRate = params.mutationRate;
    }

    if (params.multiObjective !== undefined) {
      options.multiObjective = params.multiObjective;
    }

    return options;
  }

  /**
   * Starts an optimization run.
   *
   * @param requestId The request ID
   * @param configId The configuration ID
   * @param params Optimization parameters
   * @returns Optimization result
   */
  private async startOptimizationRun(
    requestId: string,
    configId: string,
    params: OptimizationRequest
  ): Promise<GeneticAlgorithmResult> {
    // Start the run
    const runId = await this.framework.startRun(
      configId,
      params.initialConditions
    );

    // Store the run ID
    this.activeRuns.set(requestId, runId);

    // If waitForCompletion is specified, wait for the run to complete
    if (params.waitForCompletion) {
      return this.waitForRunCompletion(runId, params.timeoutMs);
    }

    // Otherwise, return the current status
    const status = this.framework.getRunStatus(runId);

    // If already completed, return results
    if (status.status === AlgorithmRunStatus.Completed) {
      return this.framework.getRunResults(runId);
    }

    // If not completed, return a placeholder result
    return {
      runMetadata: status,
      solutions: [],
      problemSummary: {
        problemName: 'Optimization in progress',
        domainType: '',
        parametersOptimized: [],
        constraints: []
      },
      performanceMetrics: {
        totalRunTimeMs: 0,
        evaluationsPerSecond: 0,
        generationCount: 0,
        improvementRate: []
      }
    };
  }

  /**
   * Waits for a run to complete.
   *
   * @param runId The run ID
   * @param timeoutMs Timeout in milliseconds
   * @returns Optimization result
   */
  private async waitForRunCompletion(
    runId: string,
    timeoutMs: number = 60000
  ): Promise<GeneticAlgorithmResult> {
    // Get initial status
    let status = this.framework.getRunStatus(runId);

    // Set timeout
    const startTime = Date.now();
    const checkInterval = 100; // ms
    const diversityCheckInterval = 5; // checks
    let checkCount = 0;

    // Get population run ID
    const populationRunId = this.runPopulations.get(runId);

    // Get problem configuration
    const configId = status.problemConfigId;
    const config = this.framework.getProblemConfiguration(configId);

    if (!config) {
      throw new Error(`Configuration with ID ${configId} not found`);
    }

    // Wait for completion
    while (
      status.status !== AlgorithmRunStatus.Completed &&
      status.status !== AlgorithmRunStatus.Failed &&
      status.status !== AlgorithmRunStatus.Cancelled &&
      Date.now() - startTime < timeoutMs
    ) {
      // Wait for check interval
      await new Promise(resolve => setTimeout(resolve, checkInterval));

      // Update status
      status = this.framework.getRunStatus(runId);

      // Check and manage population diversity periodically if population manager is used
      checkCount++;
      if (populationRunId && checkCount % diversityCheckInterval === 0) {
        try {
          // Check convergence status
          const convergenceStatus = this.populationManager.getConvergenceStatus(
            populationRunId,
            config.parameters
          );

          // If diversity is low, inject diversity
          if (convergenceStatus.diversityMeasure < 0.2) {
            await this.populationManager.manageDiversity(
              populationRunId,
              config.parameters
            );

            console.log(`Diversity injection applied to population ${populationRunId}`);
          }
        } catch (error) {
          console.warn(`Error checking population diversity: ${error}`);
        }
      }
    }

    // Get final results
    let result: GeneticAlgorithmResult;

    // If completed, get results and enhance with population statistics
    if (status.status === AlgorithmRunStatus.Completed) {
      result = this.framework.getRunResults(runId);

      // Enhance results with population evolution data if available
      if (populationRunId) {
        try {
          const evolutionHistory = this.populationManager.getEvolutionHistory(populationRunId);

          // Add evolution statistics to the result
          result.populationEvolutionStats = evolutionHistory;

          // Add diversity metrics to the convergence history
          if (result.convergenceHistory && evolutionHistory.length > 0) {
            result.convergenceHistory = result.convergenceHistory.map((entry, index) => {
              const matchingStats = evolutionHistory.find(stats => stats.generation === entry.generation);

              if (matchingStats) {
                return {
                  ...entry,
                  diversityMetrics: matchingStats.diversityMetrics
                };
              }

              return entry;
            });
          }
        } catch (error) {
          console.warn(`Error enhancing results with population data: ${error}`);
        }
      }

      return result;
    }

    // If failed or cancelled, throw error
    if (status.status === AlgorithmRunStatus.Failed) {
      throw new Error(`Run ${runId} failed`);
    }

    if (status.status === AlgorithmRunStatus.Cancelled) {
      throw new Error(`Run ${runId} was cancelled`);
    }

    // If timed out, throw error
    throw new Error(`Run ${runId} timed out after ${timeoutMs}ms`);
  }

  /**
   * Gets the status of an optimization run.
   *
   * @param requestId The request ID
   * @returns Run status
   */
  async getOptimizationStatus(requestId: string): Promise<any> {
    // Check if request exists
    if (!this.activeRuns.has(requestId)) {
      throw new Error(`Request with ID ${requestId} not found`);
    }

    // Get run ID
    const runId = this.activeRuns.get(requestId)!;

    // Get run status
    return this.framework.getRunStatus(runId);
  }

  /**
   * Gets the results of an optimization run.
   *
   * @param requestId The request ID
   * @returns Optimization result
   */
  async getOptimizationResults(requestId: string): Promise<GeneticAlgorithmResult> {
    // Check if request exists
    if (!this.activeRuns.has(requestId)) {
      throw new Error(`Request with ID ${requestId} not found`);
    }

    // Get run ID
    const runId = this.activeRuns.get(requestId)!;

    // Get run results
    return this.framework.getRunResults(runId);
  }

  /**
   * Cancels an optimization run.
   *
   * @param requestId The request ID
   * @returns Cancellation status
   */
  async cancelOptimization(requestId: string): Promise<any> {
    // Check if request exists
    if (!this.activeRuns.has(requestId)) {
      throw new Error(`Request with ID ${requestId} not found`);
    }

    // Get run ID
    const runId = this.activeRuns.get(requestId)!;

    // In a real implementation, this would cancel the run
    // For now, just return the status

    return {
      requestId,
      runId,
      status: 'cancelled',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Lists all active optimization runs.
   *
   * @returns List of active runs
   */
  listActiveRuns(): any[] {
    return Array.from(this.activeRuns.entries()).map(([requestId, runId]) => {
      const status = this.framework.getRunStatus(runId);

      return {
        requestId,
        runId,
        status: status.status,
        progress: Math.round((status.currentGeneration / (status.currentGeneration + 5)) * 100),
        startTime: status.startTime
      };
    });
  }

  /**
   * Lists available optimization presets.
   *
   * @returns List of presets
   */
  listPresets(): any[] {
    return Object.values(OptimizationPreset).map(preset => {
      const configId = this.framework.getPredefinedConfiguration(preset);

      return {
        preset,
        available: !!configId,
        configId
      };
    });
  }

  /**
   * Gets framework statistics.
   *
   * @returns Framework statistics
   */
  getFrameworkStatistics(): any {
    return {
      activeRuns: this.activeRuns.size,
      configs: this.framework.listConfigurations(),
      runs: this.framework.listRuns(),
      presets: this.listPresets()
    };
  }

  /**
   * Performs a health check on the client.
   *
   * @returns Health status
   */
  async healthCheck(): Promise<any> {
    // Get framework health status
    const frameworkStatus = this.framework.getHealthStatus();

    // Get population manager health status
    const populationManagerStatus = this.populationManager.getHealthStatus();

    // Basic health check
    const isHealthy = this.isInitialized &&
                     this.isStarted &&
                     frameworkStatus.state === HealthState.Healthy &&
                     populationManagerStatus.state === HealthState.Healthy;

    return {
      component: "genetic_algorithm",
      state: isHealthy ? HealthState.Healthy : HealthState.Unhealthy,
      message: isHealthy ? "Genetic Algorithm Client is healthy" : "Genetic Algorithm Client is not fully operational",
      timestamp: new Date().toISOString(),
      details: {
        initialized: this.isInitialized,
        started: this.isStarted,
        endpoint: this.endpoint,
        activeRuns: this.activeRuns.size,
        framework: frameworkStatus.details,
        populationManager: populationManagerStatus.details
      }
    };
  }

  /**
   * Sets up event listeners between the framework and population manager.
   */
  private setupEventListeners(): void {
    // In a real implementation, this would set up event listeners between
    // the framework and population manager to synchronize population evolution.
    // For now, we'll use direct method calls in the relevant places.
    console.log('Setting up event listeners between framework and population manager');
  }

  /**
   * Creates a population management options object from optimization parameters.
   *
   * @param params Optimization parameters
   * @returns Population management options
   */
  private createPopulationManagementOptions(params: OptimizationRequest): PopulationManagementOptions {
    // Map diversity strategy string to enum
    const diversityStrategyMap: Record<string, DiversityStrategy> = {
      'standard': DiversityStrategy.Standard,
      'enhanced': DiversityStrategy.EnhancedDiversity,
      'niched': DiversityStrategy.NichedConservation,
      'multi_population': DiversityStrategy.MultiPopulation,
      'adaptive': DiversityStrategy.AdaptiveImmigration,
      'speciation': DiversityStrategy.Speciation,
      'dynamic_niching': DiversityStrategy.DynamicNiching
    };

    // Map constraint strategy string to enum
    const constraintStrategyMap: Record<string, ConstraintStrategy> = {
      'penalty': ConstraintStrategy.PenaltyFunction,
      'repair': ConstraintStrategy.RepairOperator,
      'death': ConstraintStrategy.DeathPenalty,
      'separable': ConstraintStrategy.SeparableConstraint,
      'feasibility': ConstraintStrategy.FeasibilityRules,
      'stochastic': ConstraintStrategy.StochasticRanking
    };

    // Map initialization strategy string to enum
    const initializationStrategyMap: Record<string, InitializationStrategy> = {
      'random': InitializationStrategy.Random,
      'latin_hypercube': InitializationStrategy.LatinHypercube,
      'quasi_random': InitializationStrategy.QuasiRandom,
      'historical': InitializationStrategy.HistoricallyInformed,
      'gradient': InitializationStrategy.GradientBased,
      'knowledge_seeded': InitializationStrategy.KnowledgeSeeded
    };

    // Get strategy values from params or use defaults
    const diversityStrategy = params.diversityStrategy && diversityStrategyMap[params.diversityStrategy]
      ? diversityStrategyMap[params.diversityStrategy]
      : DiversityStrategy.EnhancedDiversity;

    const constraintStrategy = params.constraintStrategy && constraintStrategyMap[params.constraintStrategy]
      ? constraintStrategyMap[params.constraintStrategy]
      : ConstraintStrategy.RepairOperator;

    const initializationStrategy = params.initializationStrategy && initializationStrategyMap[params.initializationStrategy]
      ? initializationStrategyMap[params.initializationStrategy]
      : InitializationStrategy.HistoricallyInformed;

    // Create options
    return {
      populationSize: params.populationSize || 100,
      maxGenerations: params.maxGenerations || 100,
      elitismCount: 5,
      diversityStrategy,
      diversityThreshold: params.diversityThreshold || 0.3,
      nicheRadius: params.nicheRadius || 0.1,
      subpopulationCount: params.subpopulationCount || 3,
      immigrationRate: params.immigrationRate || 0.1,
      constraintStrategy,
      initializationStrategy,
      enableAdaptiveControl: params.enableAdaptiveControl || false,
      economicDomainParams: params.economicDomainParams || {}
    };
  }
}