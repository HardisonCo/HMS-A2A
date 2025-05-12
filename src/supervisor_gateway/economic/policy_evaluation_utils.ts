import { 
  EconomicFitnessFunctionRegistry,
  EconomicScenario,
  TimeHorizon,
  EconomicMetric
} from './economic_fitness_functions';
import {
  FitnessEvaluationService,
  FitnessEvaluationOptions,
  FitnessEvaluationResult
} from './fitness_evaluation_service';
import { EconomicDomain, StrategyType } from './economic_strategy_optimizer';

/**
 * A policy solution to be evaluated
 */
export interface PolicySolution {
  /**
   * Unique identifier for this policy solution
   */
  id: string;
  
  /**
   * Name of the policy
   */
  name: string;
  
  /**
   * Description of the policy
   */
  description: string;
  
  /**
   * The economic domain this policy belongs to
   */
  domain: EconomicDomain;
  
  /**
   * The strategy type this policy implements
   */
  strategyType: StrategyType;
  
  /**
   * Map of policy parameter names to their values
   */
  parameters: Record<string, any>;
  
  /**
   * Expected time horizon for policy effects
   */
  timeHorizon: TimeHorizon;
  
  /**
   * Any constraints or limitations for this policy
   */
  constraints?: Record<string, any>;
  
  /**
   * Metadata about this policy
   */
  metadata?: Record<string, any>;
}

/**
 * Result of a policy evaluation
 */
export interface PolicyEvaluationResult {
  /**
   * The policy solution that was evaluated
   */
  policy: PolicySolution;
  
  /**
   * The fitness evaluation result
   */
  fitness: FitnessEvaluationResult;
  
  /**
   * Overall score normalized to 0-100 for easier interpretation
   */
  overallScore: number;
  
  /**
   * Detailed breakdown of scores by category
   */
  scores: {
    economic: number;       // Economic impact score
    implementation: number; // Implementation feasibility score
    political: number;      // Political feasibility score
    time: number;           // Time feasibility score
  };
  
  /**
   * Key strengths of this policy (aspects with highest scores)
   */
  strengths: string[];
  
  /**
   * Key weaknesses of this policy (aspects with lowest scores)
   */
  weaknesses: string[];
  
  /**
   * Timestamp of when this evaluation was performed
   */
  evaluationTimestamp: string;
}

/**
 * Options for policy evaluation
 */
export interface PolicyEvaluationOptions {
  /**
   * The economic scenario to evaluate against
   */
  scenario: EconomicScenario;
  
  /**
   * Current economic indicators
   */
  currentIndicators: Record<string, number>;
  
  /**
   * Whether to use cached evaluations if available
   */
  useCache?: boolean;
  
  /**
   * Custom weights for different metrics
   */
  metricWeights?: Map<EconomicMetric, number>;
  
  /**
   * Whether to include detailed metrics in the result
   */
  includeDetailedMetrics?: boolean;
  
  /**
   * Domain-specific evaluation options
   */
  domainOptions?: Record<string, any>;
}

/**
 * Helper class for evaluating economic policies using the fitness evaluation system.
 * This class provides a simpler interface for policy evaluation that abstracts away
 * the details of the fitness evaluation service.
 */
export class PolicyEvaluator {
  private static instance: PolicyEvaluator;
  private evaluationService: FitnessEvaluationService;
  private fitnessFunctionRegistry: EconomicFitnessFunctionRegistry;
  private isInitialized: boolean = false;
  
  /**
   * Private constructor to enforce singleton pattern
   */
  private constructor() {
    this.evaluationService = FitnessEvaluationService.getInstance();
    this.fitnessFunctionRegistry = EconomicFitnessFunctionRegistry.getInstance();
  }
  
  /**
   * Gets the singleton instance of the PolicyEvaluator
   * @returns The singleton instance
   */
  public static getInstance(): PolicyEvaluator {
    if (!PolicyEvaluator.instance) {
      PolicyEvaluator.instance = new PolicyEvaluator();
    }
    return PolicyEvaluator.instance;
  }
  
  /**
   * Initializes the policy evaluator
   * @returns Promise that resolves when initialization is complete
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    // Initialize the fitness function registry
    await this.fitnessFunctionRegistry.initialize();
    
    // Initialize the evaluation service
    await this.evaluationService.initialize();
    
    this.isInitialized = true;
    console.log('Policy evaluator initialized');
  }
  
  /**
   * Evaluates a single economic policy
   * 
   * @param policy The policy solution to evaluate
   * @param options Options for the evaluation
   * @returns The detailed policy evaluation result
   */
  public async evaluatePolicy(
    policy: PolicySolution,
    options: PolicyEvaluationOptions
  ): Promise<PolicyEvaluationResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    // Prepare fitness evaluation options
    const fitnessOptions: FitnessEvaluationOptions = {
      scenario: options.scenario,
      timeHorizon: policy.timeHorizon,
      metricWeights: options.metricWeights,
      constraints: policy.constraints,
      currentIndicators: options.currentIndicators,
      includeDetailedMetrics: options.includeDetailedMetrics,
      useCache: options.useCache,
      domainOptions: options.domainOptions
    };
    
    // Evaluate the fitness of the policy
    const fitnessResult = await this.evaluationService.evaluateFitness(
      policy.parameters,
      fitnessOptions
    );
    
    // Calculate category scores
    const economicScore = fitnessResult.overallFitness * 100;
    const implementationScore = fitnessResult.implementationFeasibility * 100;
    const politicalScore = fitnessResult.politicalFeasibility * 100;
    
    // Calculate time feasibility score based on time horizon alignment
    const timeScore = this.calculateTimeFeasibilityScore(policy, options) * 100;
    
    // Calculate overall score as weighted average of category scores
    const overallScore = (
      economicScore * 0.4 +
      implementationScore * 0.3 +
      politicalScore * 0.2 +
      timeScore * 0.1
    );
    
    // Identify strengths and weaknesses
    const strengths = this.identifyStrengths(fitnessResult);
    const weaknesses = this.identifyWeaknesses(fitnessResult);
    
    // Create the policy evaluation result
    const policyEvaluationResult: PolicyEvaluationResult = {
      policy: policy,
      fitness: fitnessResult,
      overallScore: Math.round(overallScore * 10) / 10, // Round to 1 decimal place
      scores: {
        economic: Math.round(economicScore * 10) / 10,
        implementation: Math.round(implementationScore * 10) / 10,
        political: Math.round(politicalScore * 10) / 10,
        time: Math.round(timeScore * 10) / 10
      },
      strengths: strengths,
      weaknesses: weaknesses,
      evaluationTimestamp: new Date().toISOString()
    };
    
    return policyEvaluationResult;
  }
  
  /**
   * Evaluates multiple policy solutions and ranks them
   * 
   * @param policies Array of policy solutions to evaluate
   * @param options Options for the evaluation
   * @returns Array of policy evaluation results, sorted by overall score (highest first)
   */
  public async evaluateAndRankPolicies(
    policies: PolicySolution[],
    options: PolicyEvaluationOptions
  ): Promise<PolicyEvaluationResult[]> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    // Evaluate each policy
    const evaluationPromises = policies.map(policy => 
      this.evaluatePolicy(policy, options)
    );
    
    // Wait for all evaluations to complete
    const results = await Promise.all(evaluationPromises);
    
    // Sort results by overall score (highest first)
    return results.sort((a, b) => b.overallScore - a.overallScore);
  }
  
  /**
   * Calculates the time feasibility score for a policy
   * 
   * @param policy The policy solution
   * @param options Evaluation options
   * @returns Time feasibility score (0-1)
   */
  private calculateTimeFeasibilityScore(
    policy: PolicySolution, 
    options: PolicyEvaluationOptions
  ): number {
    // This is a simplified time feasibility calculation
    // It compares the policy's time horizon with the scenario's typical timeframe
    
    // Map scenarios to their typical time horizons
    const scenarioTimeframes: Record<EconomicScenario, TimeHorizon> = {
      [EconomicScenario.STAGFLATION]: TimeHorizon.MEDIUM_TERM,
      [EconomicScenario.RECESSION]: TimeHorizon.SHORT_TERM,
      [EconomicScenario.INFLATION_SURGE]: TimeHorizon.SHORT_TERM,
      [EconomicScenario.DEPRESSION]: TimeHorizon.LONG_TERM,
      [EconomicScenario.TRADE_WAR]: TimeHorizon.MEDIUM_TERM,
      [EconomicScenario.ASSET_BUBBLE]: TimeHorizon.SHORT_TERM,
      [EconomicScenario.CURRENCY_CRISIS]: TimeHorizon.IMMEDIATE,
      [EconomicScenario.SUPPLY_SHOCK]: TimeHorizon.SHORT_TERM,
      [EconomicScenario.PRODUCTIVITY_SLUMP]: TimeHorizon.MEDIUM_TERM,
      [EconomicScenario.DEMOGRAPHIC_SHIFT]: TimeHorizon.LONG_TERM
    };
    
    // Get the typical time horizon for this scenario
    const scenarioTimeHorizon = scenarioTimeframes[options.scenario] || TimeHorizon.MEDIUM_TERM;
    
    // Map time horizons to numeric values
    const horizonValues = {
      [TimeHorizon.IMMEDIATE]: 1,
      [TimeHorizon.SHORT_TERM]: 2,
      [TimeHorizon.MEDIUM_TERM]: 3,
      [TimeHorizon.LONG_TERM]: 4
    };
    
    // Calculate the "distance" between the policy's time horizon and the scenario's typical timeframe
    const policyHorizonValue = horizonValues[policy.timeHorizon];
    const scenarioHorizonValue = horizonValues[scenarioTimeHorizon];
    const distance = Math.abs(policyHorizonValue - scenarioHorizonValue);
    
    // Map distance to a score (0-1)
    // 0 distance = perfect alignment = score 1
    // 3 distance = worst alignment = score 0.2
    return Math.max(0.2, 1 - (distance * 0.2667));
  }
  
  /**
   * Identifies the key strengths of a policy based on its fitness evaluation
   * 
   * @param fitnessResult The fitness evaluation result
   * @returns Array of strength descriptions
   */
  private identifyStrengths(fitnessResult: FitnessEvaluationResult): string[] {
    const strengths: string[] = [];
    
    // Check overall fitness
    if (fitnessResult.overallFitness > 0.7) {
      strengths.push('Strong overall economic impact');
    }
    
    // Check implementation feasibility
    if (fitnessResult.implementationFeasibility > 0.7) {
      strengths.push('High implementation feasibility');
    }
    
    // Check political feasibility
    if (fitnessResult.politicalFeasibility > 0.7) {
      strengths.push('Strong political feasibility');
    }
    
    // Check individual metrics
    for (const [metric, score] of fitnessResult.metricScores.entries()) {
      if (score > 0.7) {
        switch (metric) {
          case EconomicMetric.GDP_GROWTH:
            strengths.push('Positive impact on GDP growth');
            break;
          case EconomicMetric.INFLATION:
            strengths.push('Effective inflation control');
            break;
          case EconomicMetric.UNEMPLOYMENT:
            strengths.push('Positive employment effects');
            break;
          case EconomicMetric.TRADE_BALANCE:
            strengths.push('Improves trade balance');
            break;
          case EconomicMetric.GOVERNMENT_DEBT:
            strengths.push('Sustainable fiscal impact');
            break;
          case EconomicMetric.INCOME_EQUALITY:
            strengths.push('Positive distributional effects');
            break;
          case EconomicMetric.PRODUCTIVITY:
            strengths.push('Enhances productivity');
            break;
          case EconomicMetric.CONSUMER_CONFIDENCE:
            strengths.push('Boosts consumer confidence');
            break;
          // Add other metrics as needed
        }
      }
    }
    
    // Ensure we have at least some strengths
    if (strengths.length === 0) {
      // Find the highest scoring metric
      let highestMetric: EconomicMetric | null = null;
      let highestScore = 0;
      
      for (const [metric, score] of fitnessResult.metricScores.entries()) {
        if (score > highestScore) {
          highestScore = score;
          highestMetric = metric;
        }
      }
      
      if (highestMetric && highestScore > 0.5) {
        strengths.push(`Relatively strong performance on ${highestMetric.toString().replace('_', ' ').toLowerCase()}`);
      } else {
        strengths.push('Balanced approach with no major weaknesses');
      }
    }
    
    return strengths;
  }
  
  /**
   * Identifies the key weaknesses of a policy based on its fitness evaluation
   * 
   * @param fitnessResult The fitness evaluation result
   * @returns Array of weakness descriptions
   */
  private identifyWeaknesses(fitnessResult: FitnessEvaluationResult): string[] {
    const weaknesses: string[] = [];
    
    // Check overall fitness
    if (fitnessResult.overallFitness < 0.4) {
      weaknesses.push('Limited overall economic impact');
    }
    
    // Check implementation feasibility
    if (fitnessResult.implementationFeasibility < 0.4) {
      weaknesses.push('Challenging implementation requirements');
    }
    
    // Check political feasibility
    if (fitnessResult.politicalFeasibility < 0.4) {
      weaknesses.push('Significant political obstacles');
    }
    
    // Check individual metrics
    for (const [metric, score] of fitnessResult.metricScores.entries()) {
      if (score < 0.4) {
        switch (metric) {
          case EconomicMetric.GDP_GROWTH:
            weaknesses.push('Limited impact on economic growth');
            break;
          case EconomicMetric.INFLATION:
            weaknesses.push('Potential inflation concerns');
            break;
          case EconomicMetric.UNEMPLOYMENT:
            weaknesses.push('Limited employment benefits');
            break;
          case EconomicMetric.TRADE_BALANCE:
            weaknesses.push('May worsen trade imbalances');
            break;
          case EconomicMetric.GOVERNMENT_DEBT:
            weaknesses.push('Potential fiscal sustainability issues');
            break;
          case EconomicMetric.INCOME_EQUALITY:
            weaknesses.push('May increase income inequality');
            break;
          case EconomicMetric.PRODUCTIVITY:
            weaknesses.push('Limited productivity impact');
            break;
          case EconomicMetric.CONSUMER_CONFIDENCE:
            weaknesses.push('May not improve consumer confidence');
            break;
          // Add other metrics as needed
        }
      }
    }
    
    // Ensure we have at least some weaknesses
    if (weaknesses.length === 0) {
      // Find the lowest scoring metric
      let lowestMetric: EconomicMetric | null = null;
      let lowestScore = 1;
      
      for (const [metric, score] of fitnessResult.metricScores.entries()) {
        if (score < lowestScore) {
          lowestScore = score;
          lowestMetric = metric;
        }
      }
      
      if (lowestMetric && lowestScore < 0.6) {
        weaknesses.push(`Relatively weak performance on ${lowestMetric.toString().replace('_', ' ').toLowerCase()}`);
      } else {
        weaknesses.push('May require fine-tuning for specific economic conditions');
      }
    }
    
    return weaknesses;
  }
  
  /**
   * Creates a standard policy solution template for a given strategy type
   * 
   * @param strategyType The strategy type
   * @param domain The economic domain
   * @returns A policy solution template with default values
   */
  public createPolicySolutionTemplate(
    strategyType: StrategyType,
    domain: EconomicDomain
  ): PolicySolution {
    // Generate a unique ID
    const id = `policy_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    
    // Set default name and description based on strategy type
    let name = `${strategyType.toString().replace(/([A-Z])/g, ' $1').trim()} Policy`;
    let description = `A policy approach designed to address ${strategyType.toString().replace(/([A-Z])/g, ' $1').trim().toLowerCase()} challenges.`;
    
    // Set default time horizon based on strategy type
    let timeHorizon = TimeHorizon.MEDIUM_TERM;
    switch (strategyType) {
      case StrategyType.InflationControl:
      case StrategyType.RecessionResponse:
      case StrategyType.FinancialStability:
        timeHorizon = TimeHorizon.SHORT_TERM;
        break;
        
      case StrategyType.StagflationMitigation:
      case StrategyType.FiscalPolicyOptimization:
      case StrategyType.TradeBalanceOptimization:
        timeHorizon = TimeHorizon.MEDIUM_TERM;
        break;
        
      case StrategyType.SustainableDevelopment:
      case StrategyType.EconomicResilience:
      case StrategyType.MonetaryPolicyOptimization:
        timeHorizon = TimeHorizon.LONG_TERM;
        break;
    }
    
    // Create default parameters based on domain and strategy type
    const parameters: Record<string, any> = {};
    
    // Add common parameters for all policies
    parameters.implementationMonths = 12;
    parameters.budgetPercentGDP = 0.5;
    parameters.staffingLevel = 5;
    
    // Add domain-specific parameters
    switch (domain) {
      case EconomicDomain.Fiscal:
        parameters.taxRateAdjustment = 0;
        parameters.governmentSpendingChange = 0;
        parameters.deficitTargetPercent = 3.0;
        parameters.publicDebtTarget = 60.0;
        break;
        
      case EconomicDomain.Monetary:
        parameters.interestRateAdjustment = 0;
        parameters.moneySupplyGrowth = 2.0;
        parameters.reserveRequirements = 10.0;
        parameters.inflationTarget = 2.0;
        break;
        
      case EconomicDomain.Trade:
        parameters.tariffRateAdjustment = 0;
        parameters.exportIncentives = 5.0;
        parameters.tradeDealScope = 0.5;
        parameters.supplierDiversification = 0.5;
        break;
        
      case EconomicDomain.Labor:
        parameters.minimumWageAdjustment = 0;
        parameters.laborMarketFlexibility = 0.5;
        parameters.workerRetrainingFunding = 0.2;
        parameters.employmentProtection = 0.5;
        break;
        
      case EconomicDomain.Financial:
        parameters.capitalRequirements = 10.0;
        parameters.leverageRatio = 5.0;
        parameters.marketRegulationStrength = 0.5;
        parameters.consumptionProtection = 0.5;
        break;
    }
    
    // Add strategy-specific parameters
    switch (strategyType) {
      case StrategyType.StagflationMitigation:
        parameters.supplyChainReform = 0.5;
        parameters.energyPriceStabilization = 0.5;
        parameters.wageControlPolicy = 0.3;
        break;
        
      case StrategyType.TradeBalanceOptimization:
        parameters.currencyValuationTarget = 0;
        parameters.importSubstitution = 0.3;
        parameters.exportDiversification = 0.5;
        break;
        
      case StrategyType.InflationControl:
        parameters.priceControlsScope = 0.1;
        parameters.demandManagement = 0.5;
        parameters.inflationExpectationsManagement = 0.5;
        break;
    }
    
    // Create the policy solution template
    return {
      id,
      name,
      description,
      domain,
      strategyType,
      parameters,
      timeHorizon,
      constraints: {},
      metadata: {
        templateVersion: '1.0',
        createdAt: new Date().toISOString()
      }
    };
  }
  
  /**
   * Creates multiple policy variants by varying parameters
   * 
   * @param basePolicy The base policy to create variants from
   * @param parameterToVary The name of the parameter to vary
   * @param values Array of values to use for the parameter
   * @returns Array of policy variants
   */
  public createPolicyVariants(
    basePolicy: PolicySolution,
    parameterToVary: string,
    values: any[]
  ): PolicySolution[] {
    // Validate that the parameter exists in the base policy
    if (!(parameterToVary in basePolicy.parameters)) {
      throw new Error(`Parameter ${parameterToVary} not found in base policy`);
    }
    
    // Create a variant for each value
    return values.map((value, index) => {
      // Clone the base policy
      const variant: PolicySolution = {
        ...basePolicy,
        id: `${basePolicy.id}_variant_${index + 1}`,
        name: `${basePolicy.name} (Variant ${index + 1})`,
        parameters: { ...basePolicy.parameters },
        metadata: { ...basePolicy.metadata, isVariant: true, variantNumber: index + 1 }
      };
      
      // Update the parameter to vary
      variant.parameters[parameterToVary] = value;
      
      // Update the description to reflect the parameter change
      variant.description = `${basePolicy.description} This variant has ${parameterToVary} set to ${value}.`;
      
      return variant;
    });
  }
}