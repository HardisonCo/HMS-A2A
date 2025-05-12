/**
 * Economic Strategy Optimizer
 * 
 * This module provides specialized optimization strategies for economic policy formulation.
 * It builds on the genetic algorithm framework to create domain-specific optimization
 * capabilities for various economic scenarios including stagflation, trade imbalance,
 * fiscal policy, and more.
 */

import { HealthState } from '../monitoring/health_types';
import { 
  GeneticAlgorithmClient, 
  OptimizationRequest, 
  OptimizationPreset 
} from './genetic_algorithm_client';
import {
  GeneticAlgorithmResult,
  GeneticParameter,
  GeneType,
  FrameworkComponent
} from './genetic_algorithm_framework';

/**
 * Economic problem domain types.
 */
export enum EconomicDomain {
  Macroeconomic = 'macroeconomic',
  Microeconomic = 'microeconomic',
  Fiscal = 'fiscal',
  Monetary = 'monetary',
  Trade = 'trade',
  Labor = 'labor',
  SupplyChain = 'supply_chain',
  Sectoral = 'sectoral',
  Infrastructure = 'infrastructure'
}

/**
 * Economic strategy types.
 */
export enum StrategyType {
  StagflationMitigation = 'stagflation_mitigation',
  TradeBalanceOptimization = 'trade_balance_optimization',
  FiscalPolicyOptimization = 'fiscal_policy_optimization',
  MonetaryPolicyOptimization = 'monetary_policy_optimization',
  InflationTargeting = 'inflation_targeting',
  LaborMarketOptimization = 'labor_market_optimization',
  EconomicGrowthMaximization = 'economic_growth_maximization',
  SupplyShockResilience = 'supply_shock_resilience',
  DemandStimulation = 'demand_stimulation',
  SectoralSubsidyOptimization = 'sectoral_subsidy_optimization',
  InfrastructureInvestmentOptimization = 'infrastructure_investment_optimization',
  TaxPolicyOptimization = 'tax_policy_optimization',
  RegionalDevelopmentStrategy = 'regional_development_strategy',
  WealthDistributionOptimization = 'wealth_distribution_optimization',
  EconomicCrisisResponse = 'economic_crisis_response',
  ResourceAllocationOptimization = 'resource_allocation_optimization'
}

/**
 * Strategy optimization result.
 */
export interface EconomicStrategyResult {
  strategyType: StrategyType;
  domain: EconomicDomain;
  result: GeneticAlgorithmResult;
  policyRecommendations: PolicyRecommendation[];
  economicOutcomes: EconomicOutcome[];
  sensitivityAnalysis?: SensitivityAnalysis;
  implementationPlan?: ImplementationPlan;
}

/**
 * Policy recommendation from optimization.
 */
export interface PolicyRecommendation {
  name: string;
  description: string;
  parameterValues: Record<string, any>;
  confidence: number;
  impact: Record<string, number>;
  timeframe: {
    implementationPeriodMonths: number;
    expectedOutcomeDelayMonths: number;
    effectiveDurationMonths: number;
  };
  prerequisites?: string[];
  alternatives?: Array<{
    name: string;
    tradeoffs: Record<string, number>;
  }>;
}

/**
 * Economic outcome prediction.
 */
export interface EconomicOutcome {
  metric: string;
  baseline: number;
  predicted: number;
  percentChange: number;
  confidenceInterval: [number, number];
  timeHorizonMonths: number;
}

/**
 * Sensitivity analysis of a strategy.
 */
export interface SensitivityAnalysis {
  parameters: Array<{
    name: string;
    elasticity: number;
    criticalThresholds: Array<{
      value: number;
      effect: string;
    }>;
  }>;
  externalFactors: Array<{
    name: string;
    impactLevel: 'low' | 'medium' | 'high';
    mitigationOptions?: string[];
  }>;
}

/**
 * Implementation plan for a strategy.
 */
export interface ImplementationPlan {
  phases: Array<{
    name: string;
    description: string;
    durationMonths: number;
    keyMilestones: string[];
    dependencies?: string[];
  }>;
  monitoringMetrics: string[];
  adjustmentTriggers: Array<{
    condition: string;
    action: string;
  }>;
}

/**
 * Options for strategy optimization.
 */
export interface StrategyOptimizationOptions {
  populationSize?: number;
  maxGenerations?: number;
  crossoverRate?: number;
  mutationRate?: number;
  selectionMethod?: string;
  constraints?: any[];
  timeHorizonMonths?: number;
  externalFactors?: Record<string, any>;
  regionalFocus?: string[];
  sectoralFocus?: string[];
  demographicFocus?: string[];
  riskTolerance?: 'low' | 'medium' | 'high';
  policyPriorities?: Record<string, number>;
  existingPolicies?: Record<string, any>;
  historicalDataWeight?: number;
  computeDetailedOutcomes?: boolean;
  computeSensitivityAnalysis?: boolean;
  createImplementationPlan?: boolean;
  waitForCompletion?: boolean;
  timeoutMs?: number;
}

/**
 * Economic strategy optimizer class.
 */
export class EconomicStrategyOptimizer {
  private gaClient: GeneticAlgorithmClient;
  private isInitialized: boolean = false;
  private predefinedStrategies: Map<StrategyType, PredefinedStrategy> = new Map();
  private domainParameters: Map<EconomicDomain, GeneticParameter[]> = new Map();
  private optimizationCache: Map<string, EconomicStrategyResult> = new Map();
  private activeOptimizations: Map<string, {
    strategyType: StrategyType;
    domain: EconomicDomain;
    requestId: string;
    startTime: string;
  }> = new Map();

  /**
   * Creates a new EconomicStrategyOptimizer instance.
   */
  constructor() {
    this.gaClient = new GeneticAlgorithmClient();
  }

  /**
   * Initializes the optimizer.
   */
  async initialize(): Promise<void> {
    console.log('Initializing Economic Strategy Optimizer...');

    // Initialize the genetic algorithm client
    await this.gaClient.initialize();
    await this.gaClient.start();

    // Initialize predefined strategies
    this.initializePredefinedStrategies();
    
    // Initialize domain parameters
    this.initializeDomainParameters();

    this.isInitialized = true;
    console.log('Economic Strategy Optimizer initialized successfully');
  }

  /**
   * Optimizes an economic strategy.
   * 
   * @param strategyType The type of strategy to optimize
   * @param domain The economic domain
   * @param options Optimization options
   * @returns The optimization result
   */
  async optimizeStrategy(
    strategyType: StrategyType,
    domain: EconomicDomain,
    options: StrategyOptimizationOptions = {}
  ): Promise<EconomicStrategyResult> {
    if (!this.isInitialized) {
      throw new Error('Economic Strategy Optimizer must be initialized first');
    }

    console.log(`Optimizing ${strategyType} strategy for ${domain} domain...`);

    // Generate a unique optimization ID
    const optimizationId = `opt_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;

    // Check if strategy type is supported
    if (!this.predefinedStrategies.has(strategyType)) {
      throw new Error(`Strategy type ${strategyType} is not supported`);
    }

    // Get predefined strategy
    const predefinedStrategy = this.predefinedStrategies.get(strategyType)!;

    // Check if domain is compatible with strategy
    if (!predefinedStrategy.compatibleDomains.includes(domain)) {
      throw new Error(`Domain ${domain} is not compatible with strategy ${strategyType}`);
    }

    // Create optimization request
    const request = this.createOptimizationRequest(strategyType, domain, options);

    // Store active optimization
    this.activeOptimizations.set(optimizationId, {
      strategyType,
      domain,
      requestId: '',
      startTime: new Date().toISOString()
    });

    try {
      // Run optimization
      const gaResult = await this.gaClient.optimize(request);

      // Store request ID
      this.activeOptimizations.get(optimizationId)!.requestId = gaResult.runMetadata.runId;

      // Process results
      const economicResult = this.processOptimizationResult(
        strategyType,
        domain,
        gaResult,
        options
      );

      // Cache result
      this.optimizationCache.set(optimizationId, economicResult);

      // Remove from active optimizations
      this.activeOptimizations.delete(optimizationId);

      return economicResult;
    } catch (error) {
      // Remove from active optimizations
      this.activeOptimizations.delete(optimizationId);

      // Re-throw error
      throw error;
    }
  }

  /**
   * Runs a predefined strategy.
   * 
   * @param strategyType The type of strategy to run
   * @param options Optimization options
   * @returns The strategy result
   */
  async runPredefinedStrategy(
    strategyType: StrategyType,
    options: StrategyOptimizationOptions = {}
  ): Promise<EconomicStrategyResult> {
    if (!this.isInitialized) {
      throw new Error('Economic Strategy Optimizer must be initialized first');
    }

    // Check if strategy type is supported
    if (!this.predefinedStrategies.has(strategyType)) {
      throw new Error(`Strategy type ${strategyType} is not supported`);
    }

    // Get predefined strategy
    const predefinedStrategy = this.predefinedStrategies.get(strategyType)!;

    // Use the primary domain for the strategy
    const domain = predefinedStrategy.primaryDomain;

    console.log(`Running predefined ${strategyType} strategy for ${domain} domain...`);

    // Run optimization with predefined settings
    return this.optimizeStrategy(strategyType, domain, {
      ...predefinedStrategy.defaultOptions,
      ...options
    });
  }

  /**
   * Gets a list of active optimizations.
   * 
   * @returns List of active optimizations
   */
  getActiveOptimizations(): Array<{
    id: string;
    strategyType: StrategyType;
    domain: EconomicDomain;
    startTime: string;
    elapsedTimeMs: number;
  }> {
    return Array.from(this.activeOptimizations.entries()).map(([id, info]) => ({
      id,
      strategyType: info.strategyType,
      domain: info.domain,
      startTime: info.startTime,
      elapsedTimeMs: Date.now() - new Date(info.startTime).getTime()
    }));
  }

  /**
   * Gets a list of supported strategy types.
   * 
   * @returns List of supported strategy types
   */
  getSupportedStrategyTypes(): Array<{
    type: StrategyType;
    name: string;
    description: string;
    compatibleDomains: EconomicDomain[];
  }> {
    return Array.from(this.predefinedStrategies.entries()).map(([type, strategy]) => ({
      type: type as StrategyType,
      name: strategy.name,
      description: strategy.description,
      compatibleDomains: strategy.compatibleDomains
    }));
  }

  /**
   * Gets a list of supported domains.
   * 
   * @returns List of supported domains
   */
  getSupportedDomains(): Array<{
    domain: EconomicDomain;
    name: string;
    description: string;
    parameterCount: number;
  }> {
    return Array.from(this.domainParameters.entries()).map(([domain, parameters]) => {
      // Get domain metadata
      const metadata = this.getDomainMetadata(domain);

      return {
        domain: domain as EconomicDomain,
        name: metadata.name,
        description: metadata.description,
        parameterCount: parameters.length
      };
    });
  }

  /**
   * Gets domain-specific parameters.
   * 
   * @param domain The economic domain
   * @returns List of parameters
   */
  getDomainParameters(domain: EconomicDomain): Array<{
    name: string;
    description: string;
    type: string;
    range?: [number, number];
    options?: any[];
  }> {
    if (!this.domainParameters.has(domain)) {
      throw new Error(`Domain ${domain} is not supported`);
    }

    return this.domainParameters.get(domain)!.map(param => ({
      name: param.name,
      description: param.description || '',
      type: param.type.toString(),
      range: param.min !== undefined && param.max !== undefined ? [param.min, param.max] : undefined,
      options: param.options
    }));
  }

  /**
   * Performs a health check.
   * 
   * @returns Health status
   */
  async healthCheck(): Promise<any> {
    const gaHealth = await this.gaClient.healthCheck();

    return {
      component: "economic_strategy_optimizer",
      state: this.isInitialized ? HealthState.Healthy : HealthState.Unhealthy,
      message: this.isInitialized ? 
        "Economic Strategy Optimizer is healthy" : 
        "Economic Strategy Optimizer is not initialized",
      timestamp: new Date().toISOString(),
      details: {
        initialized: this.isInitialized,
        activeOptimizations: this.activeOptimizations.size,
        cachedResults: this.optimizationCache.size,
        supportedStrategies: this.predefinedStrategies.size,
        supportedDomains: this.domainParameters.size,
        gaClient: gaHealth.details
      }
    };
  }

  /**
   * Creates an optimization request from strategy parameters.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @param options Optimization options
   * @returns Optimization request
   */
  private createOptimizationRequest(
    strategyType: StrategyType,
    domain: EconomicDomain,
    options: StrategyOptimizationOptions
  ): OptimizationRequest {
    // Get predefined strategy
    const predefinedStrategy = this.predefinedStrategies.get(strategyType)!;

    // Map strategy type to fitness function
    const fitnessFunction = strategyType;

    // Get domain parameters
    const parameters = this.domainParameters.get(domain)!.map(param => ({
      name: param.name,
      type: param.type.toString(),
      min: param.min,
      max: param.max,
      precision: param.precision,
      options: param.options,
      defaultValue: param.defaultValue
    }));

    // Create optimization request
    const request: OptimizationRequest = {
      fitnessFunction,
      domain,
      populationSize: options.populationSize || predefinedStrategy.defaultOptions.populationSize || 100,
      maxGenerations: options.maxGenerations || predefinedStrategy.defaultOptions.maxGenerations || 100,
      problemName: `${predefinedStrategy.name} Optimization`,
      problemDescription: predefinedStrategy.description,
      parameters,
      crossoverRate: options.crossoverRate || predefinedStrategy.defaultOptions.crossoverRate || 0.8,
      mutationRate: options.mutationRate || predefinedStrategy.defaultOptions.mutationRate || 0.15,
      selectionMethod: options.selectionMethod || predefinedStrategy.defaultOptions.selectionMethod,
      constraints: options.constraints || predefinedStrategy.constraints,
      multiObjective: true,
      fitnessObjectives: predefinedStrategy.objectives,
      saveHistory: true,
      waitForCompletion: options.waitForCompletion !== false,
      timeoutMs: options.timeoutMs || 60000
    };

    // Add preset if available
    const preset = this.mapStrategyTypeToPreset(strategyType);
    if (preset) {
      request.useConfigId = preset;
    }

    return request;
  }

  /**
   * Maps a strategy type to a preset.
   * 
   * @param strategyType The strategy type
   * @returns Preset name or undefined
   */
  private mapStrategyTypeToPreset(strategyType: StrategyType): string | undefined {
    // Map strategy type to preset
    const presetMappings: Record<StrategyType, OptimizationPreset> = {
      [StrategyType.StagflationMitigation]: OptimizationPreset.StagflationMitigation,
      [StrategyType.TradeBalanceOptimization]: OptimizationPreset.TradeBalanceOptimization,
      [StrategyType.FiscalPolicyOptimization]: OptimizationPreset.FiscalPolicyOptimization,
      [StrategyType.MonetaryPolicyOptimization]: OptimizationPreset.MonetaryPolicyOptimization,
      [StrategyType.LaborMarketOptimization]: OptimizationPreset.LaborMarketOptimization,
      [StrategyType.SupplyShockResilience]: OptimizationPreset.SupplyChainResilience,
      [StrategyType.SectoralSubsidyOptimization]: OptimizationPreset.SectoralCompetitiveAnalysis,
      [StrategyType.InfrastructureInvestmentOptimization]: OptimizationPreset.InfrastructureInvestmentOptimization
    } as Record<StrategyType, OptimizationPreset>;

    const preset = presetMappings[strategyType];
    if (preset) {
      // Get preset configuration ID
      return this.gaClient.listPresets().find(p => p.preset === preset)?.configId;
    }

    return undefined;
  }

  /**
   * Processes the result of an optimization.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @param gaResult The genetic algorithm result
   * @param options Optimization options
   * @returns Economic strategy result
   */
  private processOptimizationResult(
    strategyType: StrategyType,
    domain: EconomicDomain,
    gaResult: GeneticAlgorithmResult,
    options: StrategyOptimizationOptions
  ): EconomicStrategyResult {
    // Get best solutions
    const solutions = gaResult.solutions;

    // Create policy recommendations
    const policyRecommendations = this.createPolicyRecommendations(
      strategyType,
      domain,
      solutions,
      options
    );

    // Create economic outcomes
    const economicOutcomes = this.createEconomicOutcomes(
      strategyType,
      domain,
      solutions,
      options
    );

    // Create sensitivity analysis if requested
    let sensitivityAnalysis: SensitivityAnalysis | undefined;
    if (options.computeSensitivityAnalysis) {
      sensitivityAnalysis = this.createSensitivityAnalysis(
        strategyType,
        domain,
        solutions,
        gaResult,
        options
      );
    }

    // Create implementation plan if requested
    let implementationPlan: ImplementationPlan | undefined;
    if (options.createImplementationPlan) {
      implementationPlan = this.createImplementationPlan(
        strategyType,
        domain,
        policyRecommendations,
        options
      );
    }

    // Create strategy result
    return {
      strategyType,
      domain,
      result: gaResult,
      policyRecommendations,
      economicOutcomes,
      sensitivityAnalysis,
      implementationPlan
    };
  }

  /**
   * Creates policy recommendations from optimization solutions.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @param solutions The optimization solutions
   * @param options Optimization options
   * @returns Policy recommendations
   */
  private createPolicyRecommendations(
    strategyType: StrategyType,
    domain: EconomicDomain,
    solutions: any[],
    options: StrategyOptimizationOptions
  ): PolicyRecommendation[] {
    // Get best solution
    const bestSolution = solutions[0];
    if (!bestSolution) {
      return [];
    }

    // Get parameter values
    const parameterValues = bestSolution.decoded;

    // Get predefined strategy
    const predefinedStrategy = this.predefinedStrategies.get(strategyType)!;

    // Create policy recommendation from best solution
    const mainPolicy: PolicyRecommendation = {
      name: `Optimized ${predefinedStrategy.name}`,
      description: `${predefinedStrategy.description} optimized for ${domain} domain.`,
      parameterValues,
      confidence: 0.85, // Simulated confidence level
      impact: this.calculatePolicyImpact(strategyType, domain, parameterValues),
      timeframe: {
        implementationPeriodMonths: 3, // Sample values
        expectedOutcomeDelayMonths: 6,
        effectiveDurationMonths: 24
      }
    };

    // Create alternative policies from other solutions
    const alternatives: PolicyRecommendation[] = [];
    for (let i = 1; i < Math.min(3, solutions.length); i++) {
      const solution = solutions[i];
      const altValues = solution.decoded;
      
      alternatives.push({
        name: `Alternative ${predefinedStrategy.name} ${i}`,
        description: `Alternative ${i} for ${predefinedStrategy.name} in ${domain} domain.`,
        parameterValues: altValues,
        confidence: 0.85 - (i * 0.1), // Decreasing confidence
        impact: this.calculatePolicyImpact(strategyType, domain, altValues),
        timeframe: {
          implementationPeriodMonths: 3, // Sample values
          expectedOutcomeDelayMonths: 6,
          effectiveDurationMonths: 24
        },
        alternatives: [{
          name: 'Main Policy',
          tradeoffs: this.calculateTradeoffs(altValues, parameterValues)
        }]
      });
    }

    return [mainPolicy, ...alternatives];
  }

  /**
   * Calculates policy impact.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @param parameterValues The parameter values
   * @returns Impact record
   */
  private calculatePolicyImpact(
    strategyType: StrategyType,
    domain: EconomicDomain,
    parameterValues: Record<string, any>
  ): Record<string, number> {
    // Get predicted impact metrics based on strategy type
    const impactMetrics: Record<string, number> = {};

    // In a real implementation, this would use economic models to predict impacts
    // For now, use simulated values

    switch (strategyType) {
      case StrategyType.StagflationMitigation:
        impactMetrics['inflation_reduction'] = 0.3 + (parameterValues['interest_rate_adjustment'] || 0) * 0.2;
        impactMetrics['unemployment_reduction'] = 0.2 - (parameterValues['interest_rate_adjustment'] || 0) * 0.1;
        impactMetrics['gdp_growth'] = 0.1 + (parameterValues['fiscal_stimulus_percentage'] || 0) * 0.3;
        impactMetrics['supply_side_improvement'] = (parameterValues['supply_side_reform_intensity'] || 0) * 0.1;
        break;

      case StrategyType.TradeBalanceOptimization:
        impactMetrics['trade_balance_improvement'] = 0.2 + (parameterValues['export_incentive_percentage'] || 0) * 0.2;
        impactMetrics['domestic_price_impact'] = -0.1 + (parameterValues['tariff_rate_adjustment'] || 0) * 0.1;
        impactMetrics['supply_chain_resilience'] = (parameterValues['supply_chain_resilience_investment'] || 0) * 0.5;
        break;

      case StrategyType.FiscalPolicyOptimization:
        impactMetrics['budget_balance_improvement'] = 0.2 - (parameterValues['spending_adjustment_percentage'] || 0) * 0.5;
        impactMetrics['growth_stimulus'] = (parameterValues['infrastructure_investment'] || 0) * 0.4;
        impactMetrics['debt_sustainability'] = 0.3 - Math.abs(parameterValues['debt_target_adjustment'] || 0) * 0.1;
        break;

      default:
        // Generic impacts
        impactMetrics['economic_growth'] = 0.3;
        impactMetrics['inflation_impact'] = -0.1;
        impactMetrics['employment_impact'] = 0.2;
        break;
    }

    return impactMetrics;
  }

  /**
   * Calculates tradeoffs between policies.
   * 
   * @param policy1 First policy parameters
   * @param policy2 Second policy parameters 
   * @returns Tradeoff record
   */
  private calculateTradeoffs(
    policy1: Record<string, any>,
    policy2: Record<string, any>
  ): Record<string, number> {
    const tradeoffs: Record<string, number> = {};

    // Calculate differences between policies
    // In a real implementation, this would calculate actual tradeoffs
    // For now, use simulated values

    // For each parameter, calculate difference
    for (const key in policy1) {
      if (policy2.hasOwnProperty(key) && typeof policy1[key] === 'number' && typeof policy2[key] === 'number') {
        tradeoffs[key] = policy1[key] - policy2[key];
      }
    }

    // Calculate derived metrics
    tradeoffs['implementation_speed'] = Math.random() * 0.4 - 0.2; // -0.2 to 0.2
    tradeoffs['political_feasibility'] = Math.random() * 0.4 - 0.2; // -0.2 to 0.2
    tradeoffs['long_term_sustainability'] = Math.random() * 0.4 - 0.2; // -0.2 to 0.2

    return tradeoffs;
  }

  /**
   * Creates economic outcomes from optimization solutions.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @param solutions The optimization solutions
   * @param options Optimization options
   * @returns Economic outcomes
   */
  private createEconomicOutcomes(
    strategyType: StrategyType,
    domain: EconomicDomain,
    solutions: any[],
    options: StrategyOptimizationOptions
  ): EconomicOutcome[] {
    // Get best solution
    const bestSolution = solutions[0];
    if (!bestSolution) {
      return [];
    }

    // Get parameter values
    const parameterValues = bestSolution.decoded;

    // Get outcome metrics based on strategy type
    const outcomes: EconomicOutcome[] = [];

    // In a real implementation, this would use economic models to predict outcomes
    // For now, use simulated values

    // Calculate time horizon
    const timeHorizonMonths = options.timeHorizonMonths || 24;

    switch (strategyType) {
      case StrategyType.StagflationMitigation:
        outcomes.push(
          this.createOutcome('Inflation Rate', 8.5, 5.8, timeHorizonMonths),
          this.createOutcome('Unemployment Rate', 7.2, 6.5, timeHorizonMonths),
          this.createOutcome('GDP Growth', 0.5, 2.3, timeHorizonMonths),
          this.createOutcome('Manufacturing Output', 92.5, 97.8, timeHorizonMonths),
          this.createOutcome('Consumer Confidence', 65.2, 72.8, timeHorizonMonths)
        );
        break;

      case StrategyType.TradeBalanceOptimization:
        outcomes.push(
          this.createOutcome('Trade Balance (% of GDP)', -3.2, -1.8, timeHorizonMonths),
          this.createOutcome('Export Growth', 2.1, 4.8, timeHorizonMonths),
          this.createOutcome('Import Growth', 3.5, 2.7, timeHorizonMonths),
          this.createOutcome('Domestic Production', 100, 104.5, timeHorizonMonths),
          this.createOutcome('Foreign Direct Investment', 100, 112.3, timeHorizonMonths)
        );
        break;

      case StrategyType.FiscalPolicyOptimization:
        outcomes.push(
          this.createOutcome('Budget Deficit (% of GDP)', 4.8, 3.2, timeHorizonMonths),
          this.createOutcome('Public Debt (% of GDP)', 98.5, 95.2, timeHorizonMonths),
          this.createOutcome('GDP Growth', 1.5, 2.7, timeHorizonMonths),
          this.createOutcome('Tax Revenue (% of GDP)', 24.3, 25.1, timeHorizonMonths),
          this.createOutcome('Government Expenditure (% of GDP)', 29.1, 28.3, timeHorizonMonths)
        );
        break;

      default:
        // Generic outcomes
        outcomes.push(
          this.createOutcome('GDP Growth', 2.0, 2.8, timeHorizonMonths),
          this.createOutcome('Inflation Rate', 3.0, 2.5, timeHorizonMonths),
          this.createOutcome('Unemployment Rate', 5.0, 4.5, timeHorizonMonths)
        );
        break;
    }

    return outcomes;
  }

  /**
   * Creates an economic outcome.
   * 
   * @param metric The metric name
   * @param baseline The baseline value
   * @param predicted The predicted value
   * @param timeHorizonMonths The time horizon in months
   * @returns Economic outcome
   */
  private createOutcome(
    metric: string,
    baseline: number,
    predicted: number,
    timeHorizonMonths: number
  ): EconomicOutcome {
    const percentChange = ((predicted - baseline) / baseline) * 100;
    const confidenceInterval: [number, number] = [
      predicted - (Math.abs(predicted * 0.1)),
      predicted + (Math.abs(predicted * 0.1))
    ];

    return {
      metric,
      baseline,
      predicted,
      percentChange,
      confidenceInterval,
      timeHorizonMonths
    };
  }

  /**
   * Creates a sensitivity analysis.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @param solutions The optimization solutions
   * @param gaResult The genetic algorithm result
   * @param options Optimization options
   * @returns Sensitivity analysis
   */
  private createSensitivityAnalysis(
    strategyType: StrategyType,
    domain: EconomicDomain,
    solutions: any[],
    gaResult: GeneticAlgorithmResult,
    options: StrategyOptimizationOptions
  ): SensitivityAnalysis {
    // Get best solution
    const bestSolution = solutions[0];
    if (!bestSolution) {
      throw new Error('No solutions available for sensitivity analysis');
    }

    // Get parameter values
    const parameterValues = bestSolution.decoded;

    // Create parameter sensitivity
    const parameters: SensitivityAnalysis['parameters'] = [];
    
    for (const key in parameterValues) {
      // Calculate elasticity (simulated)
      const elasticity = Math.random() * 2; // 0 to 2

      // Create critical thresholds (simulated)
      const criticalThresholds: Array<{ value: number; effect: string }> = [];
      const baseValue = parameterValues[key];
      
      if (typeof baseValue === 'number') {
        criticalThresholds.push(
          { 
            value: baseValue * 0.5, 
            effect: 'Significant reduction in effectiveness' 
          },
          { 
            value: baseValue * 1.5, 
            effect: 'Diminishing returns begin' 
          }
        );
      }

      parameters.push({
        name: key,
        elasticity,
        criticalThresholds
      });
    }

    // Create external factors sensitivity
    const externalFactors: SensitivityAnalysis['externalFactors'] = [
      {
        name: 'Global Economic Growth',
        impactLevel: 'high',
        mitigationOptions: ['Targeted domestic stimulus', 'Export market diversification']
      },
      {
        name: 'Energy Prices',
        impactLevel: 'medium',
        mitigationOptions: ['Investment in energy efficiency', 'Development of alternative energy sources']
      },
      {
        name: 'Geopolitical Tensions',
        impactLevel: 'medium',
        mitigationOptions: ['Supply chain diversification', 'Strategic reserves buildup']
      }
    ];

    // For specific strategies, add domain-specific factors
    switch (strategyType) {
      case StrategyType.StagflationMitigation:
        externalFactors.push({
          name: 'Supply Chain Disruptions',
          impactLevel: 'high',
          mitigationOptions: ['Domestic production incentives', 'Inventory management reforms']
        });
        break;

      case StrategyType.TradeBalanceOptimization:
        externalFactors.push({
          name: 'Exchange Rate Fluctuations',
          impactLevel: 'high',
          mitigationOptions: ['Currency hedging programs', 'Export pricing strategies']
        });
        break;

      case StrategyType.FiscalPolicyOptimization:
        externalFactors.push({
          name: 'Interest Rate Changes',
          impactLevel: 'high',
          mitigationOptions: ['Debt term restructuring', 'Inflation-protected securities']
        });
        break;
    }

    return {
      parameters,
      externalFactors
    };
  }

  /**
   * Creates an implementation plan.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @param recommendations The policy recommendations
   * @param options Optimization options
   * @returns Implementation plan
   */
  private createImplementationPlan(
    strategyType: StrategyType,
    domain: EconomicDomain,
    recommendations: PolicyRecommendation[],
    options: StrategyOptimizationOptions
  ): ImplementationPlan {
    // Get first recommendation
    const recommendation = recommendations[0];
    if (!recommendation) {
      throw new Error('No recommendations available for implementation plan');
    }

    // Create implementation phases
    const phases: ImplementationPlan['phases'] = [];

    // Generic phases applicable to most strategies
    phases.push({
      name: 'Preparation',
      description: 'Stakeholder communication, resource allocation, and regulatory preparation',
      durationMonths: 2,
      keyMilestones: [
        'Stakeholder communication plan developed',
        'Initial resource allocation completed',
        'Regulatory requirements identified'
      ]
    });

    phases.push({
      name: 'Initial Implementation',
      description: 'Implementation of core policy elements',
      durationMonths: 3,
      keyMilestones: [
        'Core policy mechanisms established',
        'Initial roll-out to priority sectors',
        'Feedback collection system established'
      ],
      dependencies: ['Preparation']
    });

    phases.push({
      name: 'Full Deployment',
      description: 'Complete deployment across all sectors and regions',
      durationMonths: 4,
      keyMilestones: [
        'Full geographical coverage achieved',
        'All sector-specific adaptations implemented',
        'Support systems fully operational'
      ],
      dependencies: ['Initial Implementation']
    });

    phases.push({
      name: 'Monitoring and Adjustment',
      description: 'Continuous monitoring and adaptive management',
      durationMonths: 15,
      keyMilestones: [
        'First quarterly assessment completed',
        'Mid-term evaluation and adjustment',
        'Long-term effectiveness evaluation'
      ],
      dependencies: ['Full Deployment']
    });

    // Get strategy-specific monitoring metrics
    const monitoringMetrics = this.getStrategyMonitoringMetrics(strategyType, domain);

    // Create adjustment triggers
    const adjustmentTriggers: ImplementationPlan['adjustmentTriggers'] = [
      {
        condition: 'Inflation exceeds target by >1% for 2 consecutive quarters',
        action: 'Increase interest rates by 0.25-0.5%'
      },
      {
        condition: 'Unemployment increases by >0.5% for 2 consecutive quarters',
        action: 'Increase fiscal stimulus by 0.5% of GDP'
      },
      {
        condition: 'GDP growth falls below 1% for 2 consecutive quarters',
        action: 'Implement targeted sector stimulus packages'
      }
    ];

    // Add strategy-specific triggers
    switch (strategyType) {
      case StrategyType.StagflationMitigation:
        adjustmentTriggers.push({
          condition: 'Core inflation remains >5% despite 6 months of policy implementation',
          action: 'Intensify supply-side reforms and evaluate additional monetary tightening'
        });
        break;

      case StrategyType.TradeBalanceOptimization:
        adjustmentTriggers.push({
          condition: 'Trade deficit increases by >0.5% of GDP for 2 consecutive quarters',
          action: 'Intensify export promotion and evaluate targeted import substitution'
        });
        break;

      case StrategyType.FiscalPolicyOptimization:
        adjustmentTriggers.push({
          condition: 'Debt-to-GDP ratio increases by >2% in a single year',
          action: 'Implement targeted spending reductions and evaluation of revenue measures'
        });
        break;
    }

    return {
      phases,
      monitoringMetrics,
      adjustmentTriggers
    };
  }

  /**
   * Gets strategy-specific monitoring metrics.
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @returns List of monitoring metrics
   */
  private getStrategyMonitoringMetrics(
    strategyType: StrategyType,
    domain: EconomicDomain
  ): string[] {
    // Base metrics for all strategies
    const baseMetrics = [
      'GDP Growth Rate (quarterly)',
      'Inflation Rate (monthly)',
      'Unemployment Rate (monthly)',
      'Consumer Confidence Index (monthly)'
    ];

    // Strategy-specific metrics
    const specificMetrics: Record<StrategyType, string[]> = {
      [StrategyType.StagflationMitigation]: [
        'Core Inflation Rate (monthly)',
        'Manufacturing Output Index (monthly)',
        'Capacity Utilization Rate (monthly)',
        'Production Bottleneck Index (quarterly)',
        'Supply Chain Delivery Times (monthly)'
      ],
      [StrategyType.TradeBalanceOptimization]: [
        'Trade Balance (monthly)',
        'Export Volume Index (monthly)',
        'Import Price Index (monthly)',
        'Currency Exchange Rate (daily)',
        'Domestic Production Substitution Rate (quarterly)'
      ],
      [StrategyType.FiscalPolicyOptimization]: [
        'Budget Deficit (monthly)',
        'Public Debt to GDP Ratio (quarterly)',
        'Tax Revenue (monthly)',
        'Government Expenditure (monthly)',
        'Bond Yields (daily)'
      ],
      [StrategyType.MonetaryPolicyOptimization]: [
        'Interest Rates (daily)',
        'Money Supply M2 (monthly)',
        'Lending Growth Rate (monthly)',
        'Banking System Liquidity (weekly)',
        'Credit Default Rates (monthly)'
      ],
      [StrategyType.InflationTargeting]: [
        'Core Inflation Rate (monthly)',
        'Inflation Expectations Survey (quarterly)',
        'Wage Growth Rate (quarterly)',
        'Producer Price Index (monthly)',
        'Money Velocity (quarterly)'
      ],
      [StrategyType.LaborMarketOptimization]: [
        'Labor Force Participation Rate (monthly)',
        'Job Creation Rate (monthly)',
        'Wage Growth Rate (quarterly)',
        'Skills Gap Index (quarterly)',
        'Labor Productivity (quarterly)'
      ],
      [StrategyType.EconomicGrowthMaximization]: [
        'GDP Growth Rate (quarterly)',
        'Capital Formation (quarterly)',
        'Total Factor Productivity (annual)',
        'R&D Expenditure (quarterly)',
        'Business Formation Rate (monthly)'
      ],
      [StrategyType.SupplyShockResilience]: [
        'Supply Chain Disruption Index (monthly)',
        'Inventory-to-Sales Ratio (monthly)',
        'Commodity Price Volatility (daily)',
        'Production Bottleneck Index (quarterly)',
        'Strategic Reserves Levels (monthly)'
      ],
      [StrategyType.DemandStimulation]: [
        'Consumer Spending (monthly)',
        'Retail Sales (monthly)',
        'Consumer Credit Growth (monthly)',
        'Durable Goods Orders (monthly)',
        'Service Sector Activity Index (monthly)'
      ],
      [StrategyType.SectoralSubsidyOptimization]: [
        'Sectoral Output Growth (quarterly)',
        'Sectoral Employment (monthly)',
        'Sectoral Investment (quarterly)',
        'Sectoral Export Performance (quarterly)',
        'Subsidy Effectiveness Ratio (quarterly)'
      ],
      [StrategyType.InfrastructureInvestmentOptimization]: [
        'Public Investment Rate (quarterly)',
        'Infrastructure Quality Index (annual)',
        'Construction Activity Index (monthly)',
        'Project Completion Rate (quarterly)',
        'Infrastructure Capacity Utilization (quarterly)'
      ],
      [StrategyType.TaxPolicyOptimization]: [
        'Tax Revenue (monthly)',
        'Tax Compliance Rate (quarterly)',
        'Business Investment Response (quarterly)',
        'Income Inequality Measures (annual)',
        'Tax Efficiency Ratio (quarterly)'
      ],
      [StrategyType.RegionalDevelopmentStrategy]: [
        'Regional GDP Disparity Index (quarterly)',
        'Regional Employment Growth (monthly)',
        'Regional Investment Flows (quarterly)',
        'Population Migration Rates (quarterly)',
        'Regional Infrastructure Development (quarterly)'
      ],
      [StrategyType.WealthDistributionOptimization]: [
        'Gini Coefficient (annual)',
        'Median Household Income (quarterly)',
        'Wealth Quintile Ratios (annual)',
        'Financial Inclusion Metrics (quarterly)',
        'Social Mobility Indicators (annual)'
      ],
      [StrategyType.EconomicCrisisResponse]: [
        'Financial Stress Index (daily)',
        'Credit Default Rates (monthly)',
        'Business Closure Rate (monthly)',
        'Emergency Lending Activity (weekly)',
        'Crisis Response Deployment Rate (weekly)'
      ],
      [StrategyType.ResourceAllocationOptimization]: [
        'Resource Utilization Efficiency (quarterly)',
        'Sectoral Resource Allocation (quarterly)',
        'Resource Pricing (monthly)',
        'Resource Sustainability Metrics (quarterly)',
        'Resource Dependency Ratio (annual)'
      ]
    };

    // Combine base metrics with strategy-specific metrics
    return [...baseMetrics, ...specificMetrics[strategyType]];
  }

  /**
   * Initializes predefined strategies.
   */
  private initializePredefinedStrategies(): void {
    // Stagflation Mitigation
    this.predefinedStrategies.set(StrategyType.StagflationMitigation, {
      name: 'Stagflation Mitigation Strategy',
      description: 'Optimizes policy mix to address concurrent high inflation and economic stagnation',
      primaryDomain: EconomicDomain.Macroeconomic,
      compatibleDomains: [
        EconomicDomain.Macroeconomic,
        EconomicDomain.Monetary,
        EconomicDomain.Fiscal,
        EconomicDomain.SupplyChain
      ],
      objectives: [
        'inflation_reduction',
        'unemployment_reduction',
        'growth_impact',
        'implementation_feasibility'
      ],
      constraints: [
        {
          type: 'budget',
          maxPercentGDP: 3.0,
          description: 'Total fiscal measures cannot exceed 3% of GDP'
        },
        {
          type: 'policy_coherence',
          description: 'Monetary and fiscal policies must not counteract each other'
        }
      ],
      defaultOptions: {
        populationSize: 100,
        maxGenerations: 100,
        crossoverRate: 0.8,
        mutationRate: 0.15,
        selectionMethod: 'tournament',
        policyPriorities: {
          inflation_reduction: 0.4,
          unemployment_reduction: 0.3,
          growth_impact: 0.3
        },
        riskTolerance: 'medium',
        timeHorizonMonths: 24
      }
    });

    // Trade Balance Optimization
    this.predefinedStrategies.set(StrategyType.TradeBalanceOptimization, {
      name: 'Trade Balance Optimization Strategy',
      description: 'Optimizes policies to improve trade balance while minimizing negative impacts',
      primaryDomain: EconomicDomain.Trade,
      compatibleDomains: [
        EconomicDomain.Trade,
        EconomicDomain.Macroeconomic,
        EconomicDomain.SupplyChain
      ],
      objectives: [
        'trade_balance_improvement',
        'gdp_growth',
        'consumer_price_stability',
        'implementation_feasibility'
      ],
      constraints: [
        {
          type: 'wto_compliance',
          description: 'Policies must comply with WTO rules'
        },
        {
          type: 'domestic_impact',
          maxConsumerImpact: 2.0,
          description: 'Consumer price impact cannot exceed 2%'
        }
      ],
      defaultOptions: {
        populationSize: 80,
        maxGenerations: 80,
        crossoverRate: 0.75,
        mutationRate: 0.2,
        selectionMethod: 'rank',
        policyPriorities: {
          trade_balance_improvement: 0.5,
          gdp_growth: 0.25,
          consumer_price_stability: 0.25
        },
        riskTolerance: 'medium',
        timeHorizonMonths: 36
      }
    });

    // Fiscal Policy Optimization
    this.predefinedStrategies.set(StrategyType.FiscalPolicyOptimization, {
      name: 'Fiscal Policy Optimization Strategy',
      description: 'Optimizes fiscal policy parameters for economic growth and sustainability',
      primaryDomain: EconomicDomain.Fiscal,
      compatibleDomains: [
        EconomicDomain.Fiscal,
        EconomicDomain.Macroeconomic
      ],
      objectives: [
        'growth_impact',
        'debt_sustainability',
        'cyclical_stabilization',
        'implementation_feasibility'
      ],
      constraints: [
        {
          type: 'budget',
          maxDeficitPercentGDP: 3.0,
          description: 'Budget deficit cannot exceed 3% of GDP'
        },
        {
          type: 'debt',
          maxDebtPercentGDP: 60.0,
          description: 'Public debt cannot exceed 60% of GDP in the medium term'
        }
      ],
      defaultOptions: {
        populationSize: 60,
        maxGenerations: 60,
        crossoverRate: 0.8,
        mutationRate: 0.1,
        selectionMethod: 'roulette_wheel',
        policyPriorities: {
          growth_impact: 0.4,
          debt_sustainability: 0.4,
          cyclical_stabilization: 0.2
        },
        riskTolerance: 'low',
        timeHorizonMonths: 48
      }
    });

    // Monetary Policy Optimization
    this.predefinedStrategies.set(StrategyType.MonetaryPolicyOptimization, {
      name: 'Monetary Policy Optimization Strategy',
      description: 'Optimizes monetary policy for price stability and sustainable growth',
      primaryDomain: EconomicDomain.Monetary,
      compatibleDomains: [
        EconomicDomain.Monetary,
        EconomicDomain.Macroeconomic
      ],
      objectives: [
        'price_stability',
        'growth_support',
        'financial_stability',
        'implementation_feasibility'
      ],
      constraints: [
        {
          type: 'inflation_targeting',
          targetRange: [1.5, 2.5],
          description: 'Inflation target of 2% with ±0.5% tolerance'
        },
        {
          type: 'financial_stability',
          description: 'Must maintain financial system stability'
        }
      ],
      defaultOptions: {
        populationSize: 50,
        maxGenerations: 50,
        crossoverRate: 0.7,
        mutationRate: 0.1,
        selectionMethod: 'tournament',
        policyPriorities: {
          price_stability: 0.5,
          growth_support: 0.3,
          financial_stability: 0.2
        },
        riskTolerance: 'low',
        timeHorizonMonths: 36
      }
    });

    // Inflation Targeting
    this.predefinedStrategies.set(StrategyType.InflationTargeting, {
      name: 'Inflation Targeting Strategy',
      description: 'Optimizes policy mix to achieve target inflation rate',
      primaryDomain: EconomicDomain.Monetary,
      compatibleDomains: [
        EconomicDomain.Monetary,
        EconomicDomain.Macroeconomic
      ],
      objectives: [
        'inflation_target_achievement',
        'stability_of_expectations',
        'growth_impact',
        'implementation_feasibility'
      ],
      constraints: [
        {
          type: 'inflation_targeting',
          targetRange: [1.5, 2.5],
          description: 'Inflation target of 2% with ±0.5% tolerance'
        }
      ],
      defaultOptions: {
        populationSize: 50,
        maxGenerations: 50,
        crossoverRate: 0.7,
        mutationRate: 0.1,
        selectionMethod: 'tournament',
        policyPriorities: {
          inflation_target_achievement: 0.6,
          stability_of_expectations: 0.2,
          growth_impact: 0.2
        },
        riskTolerance: 'low',
        timeHorizonMonths: 24
      }
    });

    // Add other predefined strategies as needed
  }

  /**
   * Initializes domain parameters.
   */
  private initializeDomainParameters(): void {
    // Macroeconomic parameters
    this.domainParameters.set(EconomicDomain.Macroeconomic, [
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
      },
      {
        name: 'commodity_reserve_release',
        type: GeneType.Real,
        min: 0,
        max: 100,
        precision: 5,
        defaultValue: 0,
        mutable: true,
        description: 'Percentage of strategic commodity reserves to release'
      },
      {
        name: 'targeted_sector_count',
        type: GeneType.Integer,
        min: 0,
        max: 5,
        defaultValue: 2,
        mutable: true,
        description: 'Number of sectors to target with reforms'
      },
      {
        name: 'policy_sequencing',
        type: GeneType.Nominal,
        options: ['monetary_first', 'fiscal_first', 'simultaneous', 'supply_side_first'],
        defaultValue: 'monetary_first',
        mutable: true,
        description: 'Sequence of policy implementation'
      }
    ]);

    // Trade parameters
    this.domainParameters.set(EconomicDomain.Trade, [
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
      },
      {
        name: 'supply_chain_resilience_investment',
        type: GeneType.Real,
        min: 0,
        max: 2,
        precision: 0.05,
        defaultValue: 0.5,
        mutable: true,
        description: 'Supply chain resilience investment as percentage of GDP'
      },
      {
        name: 'strategic_sectors_count',
        type: GeneType.Integer,
        min: 0,
        max: 10,
        defaultValue: 3,
        mutable: true,
        description: 'Number of strategic sectors to focus on'
      },
      {
        name: 'trade_agreement_approach',
        type: GeneType.Nominal,
        options: ['bilateral', 'regional', 'multilateral', 'mixed'],
        defaultValue: 'mixed',
        mutable: true,
        description: 'Approach to trade agreements'
      }
    ]);

    // Fiscal parameters
    this.domainParameters.set(EconomicDomain.Fiscal, [
      {
        name: 'tax_rate_adjustment',
        type: GeneType.Real,
        min: -5,
        max: 5,
        precision: 0.25,
        defaultValue: 0,
        mutable: true,
        description: 'Tax rate adjustment in percentage points'
      },
      {
        name: 'spending_adjustment_percentage',
        type: GeneType.Real,
        min: -3,
        max: 3,
        precision: 0.1,
        defaultValue: 0,
        mutable: true,
        description: 'Government spending adjustment as percentage of GDP'
      },
      {
        name: 'infrastructure_investment',
        type: GeneType.Real,
        min: 0,
        max: 2,
        precision: 0.05,
        defaultValue: 0.5,
        mutable: true,
        description: 'Infrastructure investment as percentage of GDP'
      },
      {
        name: 'debt_target_adjustment',
        type: GeneType.Real,
        min: -10,
        max: 10,
        precision: 1,
        defaultValue: 0,
        mutable: true,
        description: 'Adjustment to debt-to-GDP target in percentage points'
      },
      {
        name: 'policy_phase_in_years',
        type: GeneType.Integer,
        min: 1,
        max: 5,
        defaultValue: 2,
        mutable: true,
        description: 'Years to phase in policy changes'
      }
    ]);

    // Monetary parameters
    this.domainParameters.set(EconomicDomain.Monetary, [
      {
        name: 'policy_rate_adjustment',
        type: GeneType.Real,
        min: -2,
        max: 2,
        precision: 0.25,
        defaultValue: 0,
        mutable: true,
        description: 'Policy interest rate adjustment in percentage points'
      },
      {
        name: 'reserve_requirement_adjustment',
        type: GeneType.Real,
        min: -5,
        max: 5,
        precision: 0.5,
        defaultValue: 0,
        mutable: true,
        description: 'Reserve requirement adjustment in percentage points'
      },
      {
        name: 'quantitative_easing_percentage',
        type: GeneType.Real,
        min: 0,
        max: 5,
        precision: 0.1,
        defaultValue: 0,
        mutable: true,
        description: 'Quantitative easing as percentage of GDP'
      },
      {
        name: 'forward_guidance_intensity',
        type: GeneType.Integer,
        min: 0,
        max: 5,
        defaultValue: 2,
        mutable: true,
        description: 'Forward guidance intensity (0-5 scale)'
      },
      {
        name: 'monetary_policy_framework',
        type: GeneType.Nominal,
        options: ['inflation_targeting', 'price_level_targeting', 'nominal_gdp_targeting', 'hybrid'],
        defaultValue: 'inflation_targeting',
        mutable: true,
        description: 'Monetary policy framework approach'
      }
    ]);

    // Add parameters for other domains as needed
  }

  /**
   * Gets domain metadata.
   * 
   * @param domain The economic domain
   * @returns Domain metadata
   */
  private getDomainMetadata(domain: EconomicDomain): {
    name: string;
    description: string;
  } {
    const metadata: Record<EconomicDomain, { name: string; description: string }> = {
      [EconomicDomain.Macroeconomic]: {
        name: 'Macroeconomic Policy',
        description: 'Broad economic policies affecting the entire economy'
      },
      [EconomicDomain.Microeconomic]: {
        name: 'Microeconomic Policy',
        description: 'Policies affecting specific markets, industries, or economic agents'
      },
      [EconomicDomain.Fiscal]: {
        name: 'Fiscal Policy',
        description: 'Government spending, taxation, and debt management policies'
      },
      [EconomicDomain.Monetary]: {
        name: 'Monetary Policy',
        description: 'Central bank policies affecting money supply, interest rates, and inflation'
      },
      [EconomicDomain.Trade]: {
        name: 'International Trade Policy',
        description: 'Policies affecting imports, exports, and international economic relations'
      },
      [EconomicDomain.Labor]: {
        name: 'Labor Market Policy',
        description: 'Policies affecting employment, wages, and workforce development'
      },
      [EconomicDomain.SupplyChain]: {
        name: 'Supply Chain Policy',
        description: 'Policies affecting production, logistics, and distribution networks'
      },
      [EconomicDomain.Sectoral]: {
        name: 'Sectoral Policy',
        description: 'Policies targeting specific economic sectors or industries'
      },
      [EconomicDomain.Infrastructure]: {
        name: 'Infrastructure Policy',
        description: 'Policies for physical and digital infrastructure development'
      }
    };

    return metadata[domain] || {
      name: domain,
      description: `Economic domain: ${domain}`
    };
  }
}

/**
 * Interface for predefined strategy.
 */
interface PredefinedStrategy {
  name: string;
  description: string;
  primaryDomain: EconomicDomain;
  compatibleDomains: EconomicDomain[];
  objectives: string[];
  constraints: any[];
  defaultOptions: StrategyOptimizationOptions;
}