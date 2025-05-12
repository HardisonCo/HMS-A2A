import { 
  EconomicFitnessFunctionRegistry,
  EconomicFitnessFunction, 
  EconomicScenario,
  PolicyParameterType,
  TimeHorizon,
  EvaluationResult,
  EconomicMetric
} from './economic_fitness_functions';
import { EconomicDomain, StrategyType } from './economic_strategy_optimizer';

/**
 * Represents the result of a fitness evaluation for an economic policy solution
 */
export interface FitnessEvaluationResult {
  /**
   * Unique identifier for this evaluation
   */
  evaluationId: string;
  
  /**
   * The overall fitness score (0-1, higher is better)
   */
  overallFitness: number;
  
  /**
   * Individual metric scores that contribute to the overall fitness
   */
  metricScores: Map<EconomicMetric, number>;
  
  /**
   * Detailed evaluation results for different aspects of the solution
   */
  evaluationDetails: EvaluationResult[];
  
  /**
   * The economic scenario this solution was evaluated against
   */
  scenario: EconomicScenario;
  
  /**
   * Implementation feasibility score (0-1, higher is more feasible)
   */
  implementationFeasibility: number;
  
  /**
   * Political feasibility score (0-1, higher is more politically feasible)
   */
  politicalFeasibility: number;
  
  /**
   * Timestamp when this evaluation was performed
   */
  evaluationTimestamp: string;
  
  /**
   * Any additional metadata relevant to this evaluation
   */
  metadata: Record<string, any>;
}

/**
 * Options for configuring the fitness evaluation
 */
export interface FitnessEvaluationOptions {
  /**
   * The economic scenario to evaluate against
   */
  scenario: EconomicScenario;
  
  /**
   * The time horizon to evaluate for
   */
  timeHorizon: TimeHorizon;
  
  /**
   * Weights for different metrics (keys are EconomicMetric values)
   */
  metricWeights?: Map<EconomicMetric, number>;
  
  /**
   * External constraints to consider during evaluation
   */
  constraints?: Record<string, any>;
  
  /**
   * Whether to use cached evaluations if available
   */
  useCache?: boolean;
  
  /**
   * Current economic indicators to use for the evaluation
   */
  currentIndicators?: Record<string, number>;
  
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
 * Service for evaluating the fitness of economic policy solutions.
 * This service integrates with the EconomicFitnessFunctionRegistry to
 * provide a unified interface for evaluating solutions across different
 * economic scenarios and policy types.
 */
export class FitnessEvaluationService {
  private static instance: FitnessEvaluationService;
  private registry: EconomicFitnessFunctionRegistry;
  private isInitialized: boolean = false;
  private evaluationCache: Map<string, FitnessEvaluationResult> = new Map();
  private defaultMetricWeights: Map<EconomicMetric, number> = new Map();
  
  /**
   * Private constructor to enforce singleton pattern
   */
  private constructor() {
    this.registry = EconomicFitnessFunctionRegistry.getInstance();
    this.initializeDefaultWeights();
  }
  
  /**
   * Gets the singleton instance of the FitnessEvaluationService
   * @returns The singleton instance
   */
  public static getInstance(): FitnessEvaluationService {
    if (!FitnessEvaluationService.instance) {
      FitnessEvaluationService.instance = new FitnessEvaluationService();
    }
    return FitnessEvaluationService.instance;
  }
  
  /**
   * Initializes the fitness evaluation service
   * @returns Promise that resolves when initialization is complete
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    // Ensure the registry is initialized
    await this.registry.initialize();
    
    // Perform any additional initialization
    // ...
    
    this.isInitialized = true;
    console.log('Fitness evaluation service initialized');
  }
  
  /**
   * Initializes the default metric weights
   */
  private initializeDefaultWeights(): void {
    // Set default weights for economic metrics
    this.defaultMetricWeights.set(EconomicMetric.GDP_GROWTH, 0.15);
    this.defaultMetricWeights.set(EconomicMetric.INFLATION, 0.15);
    this.defaultMetricWeights.set(EconomicMetric.UNEMPLOYMENT, 0.15);
    this.defaultMetricWeights.set(EconomicMetric.INTEREST_RATES, 0.10);
    this.defaultMetricWeights.set(EconomicMetric.GOVERNMENT_DEBT, 0.10);
    this.defaultMetricWeights.set(EconomicMetric.TRADE_BALANCE, 0.10);
    this.defaultMetricWeights.set(EconomicMetric.INCOME_EQUALITY, 0.10);
    this.defaultMetricWeights.set(EconomicMetric.PRODUCTIVITY, 0.05);
    this.defaultMetricWeights.set(EconomicMetric.CONSUMER_CONFIDENCE, 0.05);
    this.defaultMetricWeights.set(EconomicMetric.MARKET_VOLATILITY, 0.05);
  }
  
  /**
   * Evaluates the fitness of an economic policy solution
   * 
   * @param solution The economic policy solution to evaluate
   * @param options Options for the evaluation
   * @returns The evaluation result
   */
  public async evaluateFitness(
    solution: Record<string, any>,
    options: FitnessEvaluationOptions
  ): Promise<FitnessEvaluationResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    // Generate a cache key for this evaluation
    const cacheKey = this.generateCacheKey(solution, options);
    
    // Check if we have a cached result and should use it
    if (options.useCache && this.evaluationCache.has(cacheKey)) {
      return this.evaluationCache.get(cacheKey)!;
    }
    
    // Get the appropriate fitness function(s) for this scenario
    const fitnessFunctions = this.registry.getFitnessFunctionsForScenario(options.scenario);
    
    if (!fitnessFunctions || fitnessFunctions.length === 0) {
      throw new Error(`No fitness functions found for scenario: ${options.scenario}`);
    }
    
    // Prepare metric weights, using defaults for any missing weights
    const metricWeights = options.metricWeights || new Map(this.defaultMetricWeights);
    
    // Collect individual evaluation results
    const evaluationDetails: EvaluationResult[] = [];
    const metricScores = new Map<EconomicMetric, number>();
    let totalWeightedScore = 0;
    let totalWeight = 0;
    
    // Evaluate the solution using each applicable fitness function
    for (const fitnessFunction of fitnessFunctions) {
      const result = await fitnessFunction.evaluate(solution, {
        timeHorizon: options.timeHorizon,
        constraints: options.constraints || {},
        currentIndicators: options.currentIndicators || {}
      });
      
      evaluationDetails.push(result);
      
      // Accumulate weighted metric scores
      for (const [metric, score] of result.metricScores.entries()) {
        const weight = metricWeights.get(metric) || 0;
        if (weight > 0) {
          totalWeightedScore += score * weight;
          totalWeight += weight;
          
          // Store the individual metric score
          metricScores.set(metric, score);
        }
      }
    }
    
    // Calculate overall fitness score (normalized to 0-1)
    const overallFitness = totalWeight > 0 ? totalWeightedScore / totalWeight : 0;
    
    // Evaluate implementation and political feasibility
    const implementationFeasibility = this.evaluateImplementationFeasibility(solution, options);
    const politicalFeasibility = this.evaluatePoliticalFeasibility(solution, options);
    
    // Create the evaluation result
    const evaluationResult: FitnessEvaluationResult = {
      evaluationId: this.generateEvaluationId(),
      overallFitness,
      metricScores,
      evaluationDetails,
      scenario: options.scenario,
      implementationFeasibility,
      politicalFeasibility,
      evaluationTimestamp: new Date().toISOString(),
      metadata: {
        timeHorizon: options.timeHorizon,
        domainOptions: options.domainOptions || {}
      }
    };
    
    // Cache the result if caching is enabled
    if (options.useCache) {
      this.evaluationCache.set(cacheKey, evaluationResult);
    }
    
    return evaluationResult;
  }
  
  /**
   * Evaluates the implementation feasibility of a solution
   * 
   * @param solution The solution to evaluate
   * @param options Evaluation options
   * @returns Implementation feasibility score (0-1)
   */
  private evaluateImplementationFeasibility(
    solution: Record<string, any>,
    options: FitnessEvaluationOptions
  ): number {
    // Factors that affect implementation feasibility:
    // 1. Complexity of the solution
    // 2. Resource requirements
    // 3. Technical feasibility
    // 4. Regulatory barriers
    // 5. Time constraints
    
    // This would typically be a complex calculation based on the
    // specific parameters of the solution and the constraints of
    // the implementation environment
    
    // For simplicity, we'll use a heuristic approach here
    const complexityScore = this.evaluateComplexity(solution);
    const resourceScore = this.evaluateResourceRequirements(solution);
    const technicalScore = this.evaluateTechnicalFeasibility(solution);
    const regulatoryScore = this.evaluateRegulatoryFeasibility(solution, options);
    const timeConstraintScore = this.evaluateTimeConstraints(solution, options.timeHorizon);
    
    // Weight the factors according to their importance
    const weightedScore = (
      complexityScore * 0.25 +
      resourceScore * 0.2 +
      technicalScore * 0.2 +
      regulatoryScore * 0.2 +
      timeConstraintScore * 0.15
    );
    
    // Return normalized score (0-1)
    return Math.max(0, Math.min(1, weightedScore));
  }
  
  /**
   * Evaluates the political feasibility of a solution
   * 
   * @param solution The solution to evaluate
   * @param options Evaluation options
   * @returns Political feasibility score (0-1)
   */
  private evaluatePoliticalFeasibility(
    solution: Record<string, any>,
    options: FitnessEvaluationOptions
  ): number {
    // Factors that affect political feasibility:
    // 1. Public support
    // 2. Stakeholder alignment
    // 3. Political capital required
    // 4. Special interest opposition
    // 5. Ideological alignment with current administration
    
    // This would typically be a complex calculation based on the
    // specific parameters of the solution and the current political landscape
    
    // For simplicity, we'll use a heuristic approach here
    const publicSupportScore = this.evaluatePublicSupport(solution);
    const stakeholderScore = this.evaluateStakeholderAlignment(solution);
    const politicalCapitalScore = this.evaluatePoliticalCapital(solution);
    const specialInterestScore = this.evaluateSpecialInterestOpposition(solution);
    const ideologicalScore = this.evaluateIdeologicalAlignment(solution);
    
    // Weight the factors according to their importance
    const weightedScore = (
      publicSupportScore * 0.3 +
      stakeholderScore * 0.2 +
      politicalCapitalScore * 0.2 +
      specialInterestScore * 0.15 +
      ideologicalScore * 0.15
    );
    
    // Return normalized score (0-1)
    return Math.max(0, Math.min(1, weightedScore));
  }
  
  /**
   * Evaluates the complexity of a solution
   * @param solution The solution to evaluate
   * @returns Complexity score (0-1, higher means less complex = more feasible)
   */
  private evaluateComplexity(solution: Record<string, any>): number {
    // Count the number of parameters as a proxy for complexity
    const paramCount = Object.keys(solution).length;
    
    // More parameters generally means more complex
    // Scale inversely: fewer parameters = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - (paramCount / 20)));
  }
  
  /**
   * Evaluates the resource requirements of a solution
   * @param solution The solution to evaluate
   * @returns Resource score (0-1, higher means fewer resources needed = more feasible)
   */
  private evaluateResourceRequirements(solution: Record<string, any>): number {
    // Check for resource intensity indicators in the solution
    // This is a simplified heuristic approach
    
    let resourceIntensity = 0;
    
    // Look for budget parameters
    if (solution.budgetPercentGDP) {
      resourceIntensity += solution.budgetPercentGDP * 5; // Higher budget = more resources
    }
    
    // Look for implementation timeframe
    if (solution.implementationMonths) {
      resourceIntensity += solution.implementationMonths / 12; // Longer time = more resources
    }
    
    // Look for staff requirements
    if (solution.staffingLevel) {
      resourceIntensity += solution.staffingLevel * 0.2; // More staff = more resources
    }
    
    // Scale inversely: lower resource intensity = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - (resourceIntensity / 10)));
  }
  
  /**
   * Evaluates the technical feasibility of a solution
   * @param solution The solution to evaluate
   * @returns Technical feasibility score (0-1)
   */
  private evaluateTechnicalFeasibility(solution: Record<string, any>): number {
    // Check for technical complexity indicators
    // This is a simplified heuristic approach
    
    let technicalComplexity = 0;
    
    // Look for technology dependency
    if (solution.technologyDependency) {
      technicalComplexity += solution.technologyDependency * 0.3;
    }
    
    // Look for innovation requirements
    if (solution.innovationLevel) {
      technicalComplexity += solution.innovationLevel * 0.4;
    }
    
    // Look for integration complexity
    if (solution.integrationComplexity) {
      technicalComplexity += solution.integrationComplexity * 0.3;
    }
    
    // Scale inversely: lower technical complexity = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - (technicalComplexity / 5)));
  }
  
  /**
   * Evaluates the regulatory feasibility of a solution
   * @param solution The solution to evaluate
   * @param options Evaluation options
   * @returns Regulatory feasibility score (0-1)
   */
  private evaluateRegulatoryFeasibility(
    solution: Record<string, any>,
    options: FitnessEvaluationOptions
  ): number {
    // Check for regulatory barrier indicators
    // This is a simplified heuristic approach
    
    let regulatoryBarriers = 0;
    
    // Look for regulatory change requirements
    if (solution.regulatoryChangeLevel) {
      regulatoryBarriers += solution.regulatoryChangeLevel * 0.4;
    }
    
    // Look for legal constraints
    if (solution.legalConstraints) {
      regulatoryBarriers += solution.legalConstraints * 0.3;
    }
    
    // Look for international agreement dependencies
    if (solution.internationalAgreements) {
      regulatoryBarriers += solution.internationalAgreements * 0.3;
    }
    
    // Consider domain-specific regulatory factors
    if (options.domainOptions?.regulatoryEnvironment) {
      // Adjust based on current regulatory environment (0-1, higher means more regulatory barriers)
      regulatoryBarriers *= (1 + options.domainOptions.regulatoryEnvironment * 0.5);
    }
    
    // Scale inversely: lower regulatory barriers = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - (regulatoryBarriers / 5)));
  }
  
  /**
   * Evaluates the time constraints of a solution
   * @param solution The solution to evaluate
   * @param timeHorizon The time horizon for implementation
   * @returns Time constraint score (0-1)
   */
  private evaluateTimeConstraints(solution: Record<string, any>, timeHorizon: TimeHorizon): number {
    // Map the solution's implementation time to a score based on the desired time horizon
    const implementationMonths = solution.implementationMonths || 12; // Default to 1 year
    
    // Map time horizons to months
    const horizonMonths = {
      [TimeHorizon.IMMEDIATE]: 3,
      [TimeHorizon.SHORT_TERM]: 12,
      [TimeHorizon.MEDIUM_TERM]: 36,
      [TimeHorizon.LONG_TERM]: 60
    };
    
    const availableMonths = horizonMonths[timeHorizon];
    
    // Calculate how well the solution fits within the time horizon
    // If implementation time is less than available time, it's more feasible
    const timeFitRatio = implementationMonths / availableMonths;
    
    // Scale inversely: lower time fit ratio = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - timeFitRatio * 0.8));
  }
  
  /**
   * Evaluates the public support for a solution
   * @param solution The solution to evaluate
   * @returns Public support score (0-1)
   */
  private evaluatePublicSupport(solution: Record<string, any>): number {
    // This would typically involve a public opinion model
    // For simplicity, we'll use a heuristic approach
    
    let publicSupportLevel = 0.5; // Default to neutral
    
    // Look for public popularity factors
    if (solution.taxIncrease) {
      // Tax increases tend to be unpopular
      publicSupportLevel -= solution.taxIncrease * 0.1;
    }
    
    if (solution.publicBenefit) {
      // Direct public benefits increase support
      publicSupportLevel += solution.publicBenefit * 0.15;
    }
    
    if (solution.jobCreation) {
      // Job creation is generally popular
      publicSupportLevel += solution.jobCreation * 0.1;
    }
    
    // Return normalized score (0-1)
    return Math.max(0, Math.min(1, publicSupportLevel));
  }
  
  /**
   * Evaluates the stakeholder alignment for a solution
   * @param solution The solution to evaluate
   * @returns Stakeholder alignment score (0-1)
   */
  private evaluateStakeholderAlignment(solution: Record<string, any>): number {
    // This would typically involve a stakeholder analysis model
    // For simplicity, we'll use a heuristic approach
    
    let stakeholderAlignment = 0.5; // Default to neutral
    
    // Look for stakeholder impact factors
    if (solution.industryImpact) {
      // Industry impact can affect alignment (positive or negative)
      stakeholderAlignment += solution.industryImpact * 0.1;
    }
    
    if (solution.laborImpact) {
      // Labor impact can affect alignment
      stakeholderAlignment += solution.laborImpact * 0.1;
    }
    
    if (solution.consumerImpact) {
      // Consumer impact can affect alignment
      stakeholderAlignment += solution.consumerImpact * 0.1;
    }
    
    // Return normalized score (0-1)
    return Math.max(0, Math.min(1, stakeholderAlignment));
  }
  
  /**
   * Evaluates the political capital required for a solution
   * @param solution The solution to evaluate
   * @returns Political capital score (0-1, higher means less capital required = more feasible)
   */
  private evaluatePoliticalCapital(solution: Record<string, any>): number {
    // This would typically involve a political model
    // For simplicity, we'll use a heuristic approach
    
    let politicalCapitalRequired = 0.5; // Default to moderate
    
    // Look for factors that require political capital
    if (solution.controversyLevel) {
      // More controversial policies require more political capital
      politicalCapitalRequired += solution.controversyLevel * 0.2;
    }
    
    if (solution.executiveAction) {
      // Executive actions may require less legislative political capital
      politicalCapitalRequired -= solution.executiveAction * 0.1;
    }
    
    if (solution.bipartisanSupport) {
      // Bipartisan support reduces required political capital
      politicalCapitalRequired -= solution.bipartisanSupport * 0.2;
    }
    
    // Scale inversely: lower political capital required = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - politicalCapitalRequired));
  }
  
  /**
   * Evaluates the special interest opposition to a solution
   * @param solution The solution to evaluate
   * @returns Special interest opposition score (0-1, higher means less opposition = more feasible)
   */
  private evaluateSpecialInterestOpposition(solution: Record<string, any>): number {
    // This would typically involve a special interest group model
    // For simplicity, we'll use a heuristic approach
    
    let specialInterestOpposition = 0.4; // Default to moderate opposition
    
    // Look for factors that might trigger special interest opposition
    if (solution.regulationIncrease) {
      // Increased regulation often faces industry opposition
      specialInterestOpposition += solution.regulationIncrease * 0.15;
    }
    
    if (solution.marketDisruption) {
      // Market disruption can trigger incumbent opposition
      specialInterestOpposition += solution.marketDisruption * 0.15;
    }
    
    if (solution.subsidyChanges) {
      // Changes to subsidies can trigger opposition
      specialInterestOpposition += Math.abs(solution.subsidyChanges) * 0.1;
    }
    
    // Scale inversely: lower opposition = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - specialInterestOpposition));
  }
  
  /**
   * Evaluates the ideological alignment of a solution with current administration
   * @param solution The solution to evaluate
   * @returns Ideological alignment score (0-1)
   */
  private evaluateIdeologicalAlignment(solution: Record<string, any>): number {
    // This would typically involve a political ideology model
    // For simplicity, we'll assume a moderate administration (0.5 on a scale from 0=progressive to 1=conservative)
    const administrationPosition = 0.5;
    
    // Calculate the solution's ideological position
    let solutionPosition = 0.5; // Default to moderate
    
    if (solution.governmentRole) {
      // Higher values indicate larger government role (more progressive)
      solutionPosition -= (solution.governmentRole - 0.5) * 0.2;
    }
    
    if (solution.marketBased) {
      // Market-based solutions are more conservative
      solutionPosition += solution.marketBased * 0.2;
    }
    
    if (solution.redistributive) {
      // Redistributive policies are more progressive
      solutionPosition -= solution.redistributive * 0.2;
    }
    
    // Calculate alignment based on distance from administration position
    // Closer alignment = higher score
    const ideologicalDistance = Math.abs(solutionPosition - administrationPosition);
    
    // Scale inversely: lower distance = higher score (more feasible)
    return Math.max(0, Math.min(1, 1 - ideologicalDistance));
  }
  
  /**
   * Generates a cache key for an evaluation request
   * 
   * @param solution The solution being evaluated
   * @param options The evaluation options
   * @returns A string cache key
   */
  private generateCacheKey(
    solution: Record<string, any>,
    options: FitnessEvaluationOptions
  ): string {
    // Create a string representation of the solution and options
    const solutionStr = JSON.stringify(solution);
    const optionsStr = JSON.stringify({
      scenario: options.scenario,
      timeHorizon: options.timeHorizon,
      constraints: options.constraints,
      currentIndicators: options.currentIndicators,
      domainOptions: options.domainOptions
    });
    
    // Combine and hash (simple string concatenation for now)
    return `${solutionStr}|${optionsStr}`;
  }
  
  /**
   * Generates a unique evaluation ID
   * @returns A unique ID string
   */
  private generateEvaluationId(): string {
    return 'eval_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
  }
  
  /**
   * Maps an economic scenario to likely strategy types
   * 
   * @param scenario The economic scenario
   * @returns Array of relevant strategy types for this scenario
   */
  public mapScenarioToStrategyTypes(scenario: EconomicScenario): StrategyType[] {
    switch (scenario) {
      case EconomicScenario.STAGFLATION:
        return [StrategyType.StagflationMitigation];
        
      case EconomicScenario.RECESSION:
        return [StrategyType.RecessionResponse, StrategyType.FiscalPolicyOptimization];
        
      case EconomicScenario.TRADE_WAR:
        return [StrategyType.TradeBalanceOptimization, StrategyType.EconomicResilience];
        
      case EconomicScenario.INFLATION_SURGE:
        return [StrategyType.InflationControl, StrategyType.MonetaryPolicyOptimization];
        
      case EconomicScenario.DEPRESSION:
        return [
          StrategyType.RecessionResponse, 
          StrategyType.FiscalPolicyOptimization,
          StrategyType.EconomicStimulus
        ];
        
      case EconomicScenario.ASSET_BUBBLE:
        return [StrategyType.FinancialStability, StrategyType.MonetaryPolicyOptimization];
        
      case EconomicScenario.CURRENCY_CRISIS:
        return [StrategyType.FinancialStability, StrategyType.EconomicResilience];
        
      case EconomicScenario.SUPPLY_SHOCK:
        return [StrategyType.SupplyChainResilience, StrategyType.EconomicResilience];
        
      default:
        return [StrategyType.GeneralOptimization];
    }
  }
  
  /**
   * Maps a strategy type to relevant economic domains
   * 
   * @param strategyType The strategy type
   * @returns Array of relevant economic domains for this strategy
   */
  public mapStrategyTypeToDomains(strategyType: StrategyType): EconomicDomain[] {
    switch (strategyType) {
      case StrategyType.StagflationMitigation:
        return [EconomicDomain.Macroeconomic, EconomicDomain.Monetary, EconomicDomain.Fiscal];
        
      case StrategyType.TradeBalanceOptimization:
        return [EconomicDomain.Trade, EconomicDomain.Macroeconomic];
        
      case StrategyType.InflationControl:
        return [EconomicDomain.Monetary, EconomicDomain.Fiscal];
        
      case StrategyType.RecessionResponse:
        return [EconomicDomain.Fiscal, EconomicDomain.Monetary, EconomicDomain.Labor];
        
      case StrategyType.FiscalPolicyOptimization:
        return [EconomicDomain.Fiscal, EconomicDomain.Macroeconomic];
        
      case StrategyType.MonetaryPolicyOptimization:
        return [EconomicDomain.Monetary, EconomicDomain.Financial];
        
      case StrategyType.FinancialStability:
        return [EconomicDomain.Financial, EconomicDomain.Monetary];
        
      case StrategyType.EconomicResilience:
        return [
          EconomicDomain.Macroeconomic, 
          EconomicDomain.Trade, 
          EconomicDomain.Financial,
          EconomicDomain.Labor
        ];
        
      case StrategyType.EconomicStimulus:
        return [EconomicDomain.Fiscal, EconomicDomain.Labor];
        
      case StrategyType.SupplyChainResilience:
        return [EconomicDomain.Trade, EconomicDomain.Industrial];
        
      case StrategyType.WealthDistribution:
        return [EconomicDomain.Fiscal, EconomicDomain.Social];
        
      case StrategyType.SustainableDevelopment:
        return [EconomicDomain.Environmental, EconomicDomain.Industrial, EconomicDomain.Social];
        
      case StrategyType.GeneralOptimization:
        return [EconomicDomain.Macroeconomic];
        
      default:
        return [EconomicDomain.Macroeconomic];
    }
  }
  
  /**
   * Clears the evaluation cache
   */
  public clearCache(): void {
    this.evaluationCache.clear();
    console.log('Fitness evaluation cache cleared');
  }
  
  /**
   * Gets cached evaluation result if available
   * 
   * @param cacheKey The cache key
   * @returns The cached result or undefined if not found
   */
  public getCachedResult(cacheKey: string): FitnessEvaluationResult | undefined {
    return this.evaluationCache.get(cacheKey);
  }
  
  /**
   * Gets the total number of cached evaluations
   * @returns The cache size
   */
  public getCacheSize(): number {
    return this.evaluationCache.size;
  }
}