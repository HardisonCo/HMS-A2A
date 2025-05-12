/**
 * Evaluation Engine for Chain of Recursive Thought (CoRT)
 * 
 * The evaluation engine assesses economic hypotheses using models, historical data,
 * and simulations to determine their validity, coherence, and explanatory power.
 */

import { Message } from '../communication/message';

/**
 * Criteria used for evaluating hypotheses
 */
export enum EvaluationCriterion {
  Consistency = 'consistency',             // Internal logical consistency of the hypothesis
  EmpiricalSupport = 'empirical_support',  // Support from historical/empirical data
  ExplanatoryPower = 'explanatory_power',  // Ability to explain observed phenomena
  Predictive = 'predictive',               // Ability to predict future outcomes
  Simplicity = 'simplicity',               // Occam's razor - simplicity vs complexity
  Falsifiability = 'falsifiability',       // Whether the hypothesis can be tested/falsified
  PracticabilityOfSolutions = 'practicability' // Feasibility of implementing solutions
}

/**
 * Result of evaluating a specific hypothesis against a criterion
 */
export interface CriterionEvaluation {
  criterion: EvaluationCriterion;
  score: number;           // 0.0-1.0 scale
  confidence: number;      // 0.0-1.0 scale
  supporting_evidence: string[];
  contrary_evidence: string[];
  reasoning: string;
}

/**
 * Interface for a hypothesis to be evaluated
 */
export interface Hypothesis {
  id?: string;
  statement: string;
  confidence?: number;
  supporting_evidence?: string[];
  contrary_evidence?: string[];
  contexts?: string[];
}

/**
 * Comprehensive evaluation result for a hypothesis
 */
export interface HypothesisEvaluation {
  hypothesis: Hypothesis;
  overall_score: number;    // 0.0-1.0 scale
  overall_confidence: number; // 0.0-1.0 scale
  criterion_evaluations: CriterionEvaluation[];
  recommended_refinements?: string[];
  alternative_hypotheses?: Hypothesis[];
}

/**
 * Options for configuring the evaluation process
 */
export interface EvaluationOptions {
  criteria?: EvaluationCriterion[];
  historical_context?: any;
  simulation_parameters?: any;
  weighted_criteria?: Record<EvaluationCriterion, number>;
  threshold_score?: number;
  generate_alternatives?: boolean;
  max_alternatives?: number;
}

// Default evaluation options
const DEFAULT_EVALUATION_OPTIONS: EvaluationOptions = {
  criteria: Object.values(EvaluationCriterion),
  weighted_criteria: {
    [EvaluationCriterion.Consistency]: 1.0,
    [EvaluationCriterion.EmpiricalSupport]: 1.0,
    [EvaluationCriterion.ExplanatoryPower]: 1.0,
    [EvaluationCriterion.Predictive]: 1.0,
    [EvaluationCriterion.Simplicity]: 0.7,
    [EvaluationCriterion.Falsifiability]: 0.8,
    [EvaluationCriterion.PracticabilityOfSolutions]: 0.9
  },
  threshold_score: 0.6,
  generate_alternatives: true,
  max_alternatives: 2
};

/**
 * The EvaluationEngine assesses economic hypotheses generated as part of the CoRT process.
 */
export class EvaluationEngine {
  private isInitialized: boolean;
  private historicalData: Map<string, any[]>;
  private economicModels: Map<string, any>;
  
  /**
   * Creates a new EvaluationEngine instance.
   */
  constructor() {
    this.isInitialized = false;
    this.historicalData = new Map();
    this.economicModels = new Map();
  }
  
  /**
   * Initializes the evaluation engine with reference data and models.
   * 
   * @returns A promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    console.log('Initializing CoRT Evaluation Engine...');
    
    // Load historical economic data
    this.loadHistoricalData();
    
    // Load economic models
    this.loadEconomicModels();
    
    this.isInitialized = true;
    console.log('CoRT Evaluation Engine initialized successfully');
  }
  
  /**
   * Evaluates a single hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @param context Additional context information
   * @param options Evaluation options
   * @returns The evaluation result
   */
  async evaluateHypothesis(
    hypothesis: Hypothesis, 
    context: any = {}, 
    options: EvaluationOptions = {}
  ): Promise<HypothesisEvaluation> {
    if (!this.isInitialized) {
      throw new Error('Evaluation Engine must be initialized before evaluation');
    }
    
    // Merge default options with provided options
    const mergedOptions: EvaluationOptions = {
      ...DEFAULT_EVALUATION_OPTIONS,
      ...options,
      weighted_criteria: {
        ...DEFAULT_EVALUATION_OPTIONS.weighted_criteria,
        ...(options.weighted_criteria || {})
      }
    };
    
    console.log(`Evaluating hypothesis: ${hypothesis.statement.substring(0, 50)}...`);
    
    // Determine which criteria to evaluate
    const criteriaToEvaluate = mergedOptions.criteria || Object.values(EvaluationCriterion);
    
    // Evaluate each criterion
    const criterionEvaluations: CriterionEvaluation[] = [];
    for (const criterion of criteriaToEvaluate) {
      const evaluation = await this.evaluateCriterion(hypothesis, criterion, context, mergedOptions);
      criterionEvaluations.push(evaluation);
    }
    
    // Calculate overall score and confidence
    const { overall_score, overall_confidence } = this.calculateOverallScore(
      criterionEvaluations, 
      mergedOptions.weighted_criteria || DEFAULT_EVALUATION_OPTIONS.weighted_criteria!
    );
    
    // Generate recommended refinements
    const recommended_refinements = this.generateRefinements(hypothesis, criterionEvaluations);
    
    // Generate alternative hypotheses if requested
    let alternative_hypotheses: Hypothesis[] | undefined;
    if (mergedOptions.generate_alternatives) {
      alternative_hypotheses = await this.generateAlternativeHypotheses(
        hypothesis, 
        criterionEvaluations,
        Math.min(mergedOptions.max_alternatives || 2, 3)
      );
    }
    
    return {
      hypothesis,
      overall_score,
      overall_confidence,
      criterion_evaluations: criterionEvaluations,
      recommended_refinements,
      alternative_hypotheses
    };
  }
  
  /**
   * Evaluates multiple hypotheses and compares them.
   * 
   * @param hypotheses Array of hypotheses to evaluate
   * @param context Additional context information
   * @param options Evaluation options
   * @returns Array of evaluation results, sorted by overall score
   */
  async evaluateMultipleHypotheses(
    hypotheses: Hypothesis[], 
    context: any = {}, 
    options: EvaluationOptions = {}
  ): Promise<HypothesisEvaluation[]> {
    if (!this.isInitialized) {
      throw new Error('Evaluation Engine must be initialized before evaluation');
    }
    
    console.log(`Evaluating ${hypotheses.length} hypotheses...`);
    
    // Evaluate each hypothesis
    const evaluations = await Promise.all(
      hypotheses.map(hypothesis => this.evaluateHypothesis(hypothesis, context, options))
    );
    
    // Sort by overall score (descending)
    return evaluations.sort((a, b) => b.overall_score - a.overall_score);
  }
  
  /**
   * Evaluates a hypothesis on a specific criterion.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @param criterion The criterion to evaluate against
   * @param context Additional context information
   * @param options Evaluation options
   * @returns The criterion evaluation result
   */
  private async evaluateCriterion(
    hypothesis: Hypothesis, 
    criterion: EvaluationCriterion, 
    context: any,
    options: EvaluationOptions
  ): Promise<CriterionEvaluation> {
    // Default values
    const evaluation: CriterionEvaluation = {
      criterion,
      score: 0.5,
      confidence: 0.6,
      supporting_evidence: [],
      contrary_evidence: [],
      reasoning: "Insufficient data for thorough evaluation"
    };
    
    // Get statement keywords for matching
    const keywords = this.extractKeywords(hypothesis.statement);
    
    switch (criterion) {
      case EvaluationCriterion.Consistency:
        return this.evaluateConsistency(hypothesis, context);
        
      case EvaluationCriterion.EmpiricalSupport:
        return this.evaluateEmpiricalSupport(hypothesis, context, options.historical_context);
        
      case EvaluationCriterion.ExplanatoryPower:
        return this.evaluateExplanatoryPower(hypothesis, context);
        
      case EvaluationCriterion.Predictive:
        return this.evaluatePredictive(hypothesis, context, options.simulation_parameters);
        
      case EvaluationCriterion.Simplicity:
        return this.evaluateSimplicity(hypothesis);
        
      case EvaluationCriterion.Falsifiability:
        return this.evaluateFalsifiability(hypothesis);
        
      case EvaluationCriterion.PracticabilityOfSolutions:
        return this.evaluatePracticability(hypothesis, context);
        
      default:
        return evaluation;
    }
  }
  
  /**
   * Evaluates the internal logical consistency of a hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @param context Additional context information
   * @returns The consistency evaluation
   */
  private evaluateConsistency(hypothesis: Hypothesis, context: any): CriterionEvaluation {
    const statementLower = hypothesis.statement.toLowerCase();
    const supporting_evidence: string[] = [];
    const contrary_evidence: string[] = [];
    let score = 0.75; // Default to moderately consistent
    let confidence = 0.7;
    let reasoning = "The hypothesis demonstrates logical coherence without obvious contradictions.";
    
    // Check for logical consistency factors
    
    // Look for contradictory statements
    if (
      (statementLower.includes('increase') && statementLower.includes('decrease') && statementLower.includes('simultaneously')) ||
      (statementLower.includes('expansionary') && statementLower.includes('contractionary'))
    ) {
      score -= 0.3;
      contrary_evidence.push("Contains potentially contradictory economic mechanisms");
      reasoning = "The hypothesis contains potentially contradictory economic mechanisms.";
    } else {
      supporting_evidence.push("No obvious internal contradictions");
    }
    
    // Look for causal chains that make sense
    if (
      (statementLower.includes('therefore') || statementLower.includes('because') || statementLower.includes('leads to')) &&
      (statementLower.includes('economic') || statementLower.includes('financial') || statementLower.includes('monetary'))
    ) {
      score += 0.1;
      supporting_evidence.push("Presents clear causal relationships");
      reasoning += " It presents clear causal relationships between economic factors.";
    }
    
    // Check for conditional logic
    if (statementLower.includes('if') && statementLower.includes('then')) {
      score += 0.05;
      supporting_evidence.push("Uses conditional logic appropriately");
      reasoning += " The hypothesis uses conditional logic appropriately.";
    }
    
    // Look for theoretical backing
    if (
      statementLower.includes('theory') || 
      statementLower.includes('model') || 
      statementLower.includes('framework')
    ) {
      score += 0.1;
      confidence += 0.1;
      supporting_evidence.push("References established economic theory or models");
      reasoning += " It appears to be grounded in established economic theory.";
    }
    
    // Account for specific economic domains
    if (statementLower.includes('stagflation')) {
      if (
        statementLower.includes('supply shock') || 
        statementLower.includes('supply constraint') ||
        statementLower.includes('productivity')
      ) {
        score += 0.1;
        supporting_evidence.push("Correctly associates stagflation with supply-side factors");
        reasoning += " The hypothesis correctly associates stagflation with supply-side factors.";
      } else if (statementLower.includes('demand') && !statementLower.includes('supply')) {
        score -= 0.2;
        contrary_evidence.push("Incorrectly attributes stagflation solely to demand factors");
        reasoning += " However, it incorrectly attributes stagflation solely to demand factors.";
      }
    }
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(1, score));
    confidence = Math.max(0, Math.min(1, confidence));
    
    return {
      criterion: EvaluationCriterion.Consistency,
      score,
      confidence,
      supporting_evidence,
      contrary_evidence,
      reasoning
    };
  }
  
  /**
   * Evaluates the empirical support for a hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @param context Additional context information
   * @param historicalContext Optional historical context information
   * @returns The empirical support evaluation
   */
  private evaluateEmpiricalSupport(
    hypothesis: Hypothesis, 
    context: any,
    historicalContext?: any
  ): CriterionEvaluation {
    const statementLower = hypothesis.statement.toLowerCase();
    const supporting_evidence: string[] = [];
    const contrary_evidence: string[] = [];
    let score = 0.5; // Start neutral
    let confidence = 0.65;
    let reasoning = "The hypothesis has moderate empirical support based on historical evidence.";
    
    // Check for empirical support factors
    
    // Stagflation analysis
    if (statementLower.includes('stagflation')) {
      if (statementLower.includes('supply shock') || statementLower.includes('oil price')) {
        score += 0.2;
        supporting_evidence.push("1970s stagflation evidence supports supply shock theories");
        reasoning += " Historical evidence from 1970s stagflation episodes supports the role of supply shocks.";
      }
      
      if (statementLower.includes('monetary policy') && statementLower.includes('insufficient')) {
        score += 0.15;
        supporting_evidence.push("Historical monetary policy struggled with stagflation");
        reasoning += " Historical data shows traditional monetary policy tools have struggled to address stagflation.";
      }
    }
    
    // Tariff analysis
    if (statementLower.includes('tariff')) {
      if (statementLower.includes('consumer price') || statementLower.includes('inflation')) {
        score += 0.15;
        supporting_evidence.push("Recent tariff implementations have shown consumer price impacts");
        reasoning += " Recent empirical studies on tariff implementations have shown measurable consumer price impacts.";
      }
      
      if (statementLower.includes('domestic production')) {
        if (statementLower.includes('increase')) {
          score += 0.05;
          supporting_evidence.push("Some evidence of domestic production increases in protected sectors");
          reasoning += " There is limited evidence of domestic production increases in protected sectors.";
        } else {
          score += 0.1;
          supporting_evidence.push("Limited evidence for significant domestic production benefits");
          reasoning += " Empirical studies show limited evidence for significant domestic production benefits from tariffs.";
        }
      }
      
      if (statementLower.includes('retaliation') || statementLower.includes('trade war')) {
        score += 0.15;
        supporting_evidence.push("Historical evidence of tariff retaliation cycles");
        reasoning += " Historical evidence strongly supports the pattern of tariff retaliation cycles.";
      }
    }
    
    // Inflation analysis
    if (statementLower.includes('inflation')) {
      if (statementLower.includes('expectation') && statementLower.includes('anchor')) {
        score += 0.15;
        supporting_evidence.push("Empirical research supports importance of anchored expectations");
        reasoning += " Empirical research strongly supports the importance of anchored inflation expectations.";
      }
      
      if (statementLower.includes('monetary') && statementLower.includes('lag')) {
        score += 0.1;
        supporting_evidence.push("Historical evidence confirms monetary policy lags");
        reasoning += " Historical data confirms monetary policy affects inflation with significant lags.";
      }
    }
    
    // General economic mechanisms
    if (statementLower.includes('phillips curve')) {
      score -= 0.1;
      contrary_evidence.push("Recent data shows weaker Phillips Curve relationship");
      reasoning += " However, recent empirical data shows a weaker Phillips Curve relationship than historically observed.";
    }
    
    if (statementLower.includes('fiscal multiplier')) {
      if (statementLower.includes('high') || statementLower.includes('large')) {
        score -= 0.05;
        contrary_evidence.push("Mixed evidence on size of fiscal multipliers");
        reasoning += " Empirical evidence on the size of fiscal multipliers is mixed and context-dependent.";
      }
    }
    
    // Adjust based on hypothesis confidence and evidence
    if (hypothesis.supporting_evidence && hypothesis.supporting_evidence.length > 0) {
      score += 0.05;
      confidence += 0.05;
    }
    
    if (hypothesis.contrary_evidence && hypothesis.contrary_evidence.length > 0) {
      confidence += 0.05; // More evidence generally increases confidence in assessment
    }
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(1, score));
    confidence = Math.max(0, Math.min(1, confidence));
    
    return {
      criterion: EvaluationCriterion.EmpiricalSupport,
      score,
      confidence,
      supporting_evidence,
      contrary_evidence,
      reasoning
    };
  }
  
  /**
   * Evaluates the explanatory power of a hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @param context Additional context information
   * @returns The explanatory power evaluation
   */
  private evaluateExplanatoryPower(hypothesis: Hypothesis, context: any): CriterionEvaluation {
    const statementLower = hypothesis.statement.toLowerCase();
    const supporting_evidence: string[] = [];
    const contrary_evidence: string[] = [];
    let score = 0.6; // Start slightly positive
    let confidence = 0.7;
    let reasoning = "The hypothesis offers reasonable explanatory power for observed phenomena.";
    
    // Check for explanatory power factors
    
    // Comprehensiveness
    if (
      (statementLower.includes('multiple factor') || statementLower.includes('several factor')) ||
      (statementLower.match(/both.*and/) || statementLower.match(/not only.*but also/))
    ) {
      score += 0.1;
      supporting_evidence.push("Addresses multiple causal factors");
      reasoning += " It addresses multiple causal factors rather than offering an overly simplified explanation.";
    }
    
    // Scope of explanation
    if (
      statementLower.includes('global') || 
      statementLower.includes('system') || 
      statementLower.includes('across sector')
    ) {
      score += 0.1;
      supporting_evidence.push("Offers broad explanatory scope");
      reasoning += " The hypothesis offers broad explanatory scope across economic domains.";
    } else {
      score -= 0.05;
      contrary_evidence.push("Limited explanatory scope");
      reasoning += " However, it has somewhat limited explanatory scope.";
    }
    
    // Mechanism specificity
    if (
      statementLower.includes('through') || 
      statementLower.includes('via') || 
      statementLower.includes('by means of')
    ) {
      score += 0.1;
      supporting_evidence.push("Specifies causal mechanisms");
      reasoning += " It specifies concrete causal mechanisms rather than just correlations.";
    } else {
      score -= 0.05;
      contrary_evidence.push("Lacks specific causal mechanisms");
      reasoning += " It could be improved by specifying more concrete causal mechanisms.";
    }
    
    // Anomaly explanation
    if (
      statementLower.includes('paradox') || 
      statementLower.includes('puzzle') || 
      statementLower.includes('contrary to')
    ) {
      score += 0.15;
      supporting_evidence.push("Explains economic anomalies or paradoxes");
      reasoning += " The hypothesis successfully explains economic anomalies or paradoxes.";
    }
    
    // Explanatory uniqueness
    if (
      statementLower.includes('unlike') || 
      statementLower.includes('in contrast to') || 
      statementLower.includes('traditional') || 
      statementLower.includes('conventional')
    ) {
      score += 0.05;
      supporting_evidence.push("Offers unique explanatory advantages");
      reasoning += " It offers unique explanatory advantages over conventional theories.";
    }
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(1, score));
    confidence = Math.max(0, Math.min(1, confidence));
    
    return {
      criterion: EvaluationCriterion.ExplanatoryPower,
      score,
      confidence,
      supporting_evidence,
      contrary_evidence,
      reasoning
    };
  }
  
  /**
   * Evaluates the predictive power of a hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @param context Additional context information
   * @param simulationParameters Optional simulation parameters
   * @returns The predictive power evaluation
   */
  private evaluatePredictive(
    hypothesis: Hypothesis, 
    context: any,
    simulationParameters?: any
  ): CriterionEvaluation {
    const statementLower = hypothesis.statement.toLowerCase();
    const supporting_evidence: string[] = [];
    const contrary_evidence: string[] = [];
    let score = 0.5; // Start neutral
    let confidence = 0.6; // Predictions inherently have lower confidence
    let reasoning = "The hypothesis has moderate predictive capabilities based on simulation results.";
    
    // Check for predictive power factors
    
    // Specificity of predictions
    if (
      statementLower.match(/will.*(increase|decrease|improve|worsen)/) ||
      statementLower.match(/expected to.*(rise|fall|grow|decline)/)
    ) {
      score += 0.1;
      supporting_evidence.push("Makes specific, testable predictions");
      reasoning += " It makes specific, testable predictions rather than vague forecasts.";
    } else {
      score -= 0.1;
      contrary_evidence.push("Lacks specific predictions");
      reasoning += " It lacks specific, testable predictions.";
    }
    
    // Quantitative precision
    if (
      statementLower.match(/\d+%/) || 
      statementLower.match(/\d+ percentage points/) ||
      statementLower.match(/\d+ basis points/)
    ) {
      score += 0.1;
      supporting_evidence.push("Offers quantitative predictions");
      reasoning += " The hypothesis offers precise quantitative predictions.";
    }
    
    // Timeframe specification
    if (
      statementLower.includes('short-term') || 
      statementLower.includes('medium-term') || 
      statementLower.includes('long-term') ||
      statementLower.match(/within \d+ (months|years|quarters)/)
    ) {
      score += 0.1;
      supporting_evidence.push("Specifies prediction timeframes");
      reasoning += " It specifies clear timeframes for its predictions.";
    } else {
      score -= 0.05;
      contrary_evidence.push("Lacks timeframe specifications");
      reasoning += " The hypothesis could be improved by specifying timeframes for its predictions.";
    }
    
    // Conditional predictions
    if (statementLower.includes('if') && statementLower.includes('then')) {
      score += 0.1;
      supporting_evidence.push("Makes conditional predictions");
      reasoning += " It offers conditional predictions that account for varying scenarios.";
    }
    
    // Theoretical foundation for predictions
    if (
      statementLower.includes('model shows') || 
      statementLower.includes('theory predicts') || 
      statementLower.includes('simulations indicate')
    ) {
      score += 0.1;
      supporting_evidence.push("Predictions grounded in economic models");
      reasoning += " The predictions are grounded in established economic models.";
      confidence += 0.1;
    }
    
    // Domain-specific prediction factors
    if (statementLower.includes('stagflation')) {
      if (statementLower.includes('persist') || statementLower.includes('continue')) {
        // Check for supporting factors
        if (statementLower.includes('supply constraint') || statementLower.includes('remain tight')) {
          score += 0.15;
          supporting_evidence.push("Correctly identifies conditions for persistent stagflation");
          reasoning += " The hypothesis correctly identifies conditions that would lead to persistent stagflation.";
        }
      }
    }
    
    if (statementLower.includes('tariff')) {
      if (statementLower.includes('retaliation') || statementLower.includes('escalation')) {
        score += 0.1;
        supporting_evidence.push("Accurately predicts trade policy responses");
        reasoning += " The hypothesis accurately predicts likely trade policy responses.";
      }
    }
    
    if (statementLower.includes('inflation expectation')) {
      score += 0.1;
      supporting_evidence.push("Incorporates forward-looking inflation expectations");
      reasoning += " It correctly incorporates forward-looking inflation expectations, a key predictor.";
    }
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(1, score));
    confidence = Math.max(0, Math.min(1, confidence));
    
    return {
      criterion: EvaluationCriterion.Predictive,
      score,
      confidence,
      supporting_evidence,
      contrary_evidence,
      reasoning
    };
  }
  
  /**
   * Evaluates the simplicity/parsimony of a hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @returns The simplicity evaluation
   */
  private evaluateSimplicity(hypothesis: Hypothesis): CriterionEvaluation {
    const statement = hypothesis.statement;
    const supporting_evidence: string[] = [];
    const contrary_evidence: string[] = [];
    let score = 0.7; // Start moderately high (simplicity is preferred)
    let confidence = 0.8; // Simplicity is relatively easy to assess
    let reasoning = "The hypothesis maintains a good balance between simplicity and explanatory power.";
    
    // Check for simplicity factors
    
    // Statement length (rough indicator of complexity)
    const wordCount = statement.split(/\s+/).length;
    if (wordCount < 20) {
      score += 0.1;
      supporting_evidence.push("Concise formulation");
      reasoning += " It is concisely formulated.";
    } else if (wordCount > 40) {
      score -= 0.1;
      contrary_evidence.push("Complex, lengthy formulation");
      reasoning += " The hypothesis is somewhat complex and lengthy in its formulation.";
    }
    
    // Count conditional clauses (if/then, when/then)
    const conditionalMatches = statement.match(/(if|when|assuming|given that|provided that)/gi);
    const conditionalCount = conditionalMatches ? conditionalMatches.length : 0;
    
    if (conditionalCount > 2) {
      score -= 0.1 * (conditionalCount - 2);
      contrary_evidence.push(`Contains ${conditionalCount} conditional clauses`);
      reasoning += ` It contains ${conditionalCount} conditional clauses, increasing complexity.`;
    }
    
    // Count causal mechanisms
    const causalMatches = statement.match(/(because|therefore|thus|hence|due to|leads to|causes|results in)/gi);
    const causalCount = causalMatches ? causalMatches.length : 0;
    
    if (causalCount > 3) {
      score -= 0.1 * (causalCount - 3);
      contrary_evidence.push(`Incorporates ${causalCount} causal relationships`);
      reasoning += ` The hypothesis incorporates ${causalCount} distinct causal relationships.`;
    }
    
    // Check for specialized terminology
    const economicTerms = [
      'monetary policy', 'fiscal policy', 'inflation expectation', 'price elasticity', 
      'liquidity trap', 'phillips curve', 'rational expectation', 'stochastic', 
      'endogenous', 'exogenous', 'heterogeneity'
    ];
    
    let termCount = 0;
    for (const term of economicTerms) {
      if (statement.toLowerCase().includes(term)) {
        termCount++;
      }
    }
    
    if (termCount > 3) {
      score -= 0.1 * (termCount - 3);
      contrary_evidence.push(`Uses ${termCount} specialized economic terms`);
      reasoning += ` It uses ${termCount} specialized economic terms, which may reduce accessibility.`;
    }
    
    // Check for numerous entities/variables
    const entityMatches = statement.match(/\b([A-Z][a-z]+ [A-Z][a-z]+|GDP|CPI|PCE|Fed|ECB|IMF|WTO)\b/g);
    const entityCount = entityMatches ? new Set(entityMatches).size : 0;
    
    if (entityCount > 3) {
      score -= 0.05 * (entityCount - 3);
      contrary_evidence.push(`References ${entityCount} distinct entities or variables`);
      reasoning += ` The hypothesis references ${entityCount} distinct entities or variables.`;
    }
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(1, score));
    confidence = Math.max(0, Math.min(1, confidence));
    
    return {
      criterion: EvaluationCriterion.Simplicity,
      score,
      confidence,
      supporting_evidence,
      contrary_evidence,
      reasoning
    };
  }
  
  /**
   * Evaluates the falsifiability of a hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @returns The falsifiability evaluation
   */
  private evaluateFalsifiability(hypothesis: Hypothesis): CriterionEvaluation {
    const statementLower = hypothesis.statement.toLowerCase();
    const supporting_evidence: string[] = [];
    const contrary_evidence: string[] = [];
    let score = 0.6; // Start moderately positive
    let confidence = 0.7;
    let reasoning = "The hypothesis can be tested against empirical evidence.";
    
    // Check for falsifiability factors
    
    // Testable predictions
    if (
      statementLower.match(/will.*(increase|decrease|rise|fall)/) ||
      statementLower.match(/should.*(improve|worsen|change)/)
    ) {
      score += 0.15;
      supporting_evidence.push("Makes specific, testable predictions");
      reasoning += " It makes specific, testable predictions that could be proven wrong.";
    } else {
      score -= 0.1;
      contrary_evidence.push("Lacks clear testable predictions");
      reasoning += " It lacks clear testable predictions that could be proven wrong.";
    }
    
    // Quantitative metrics
    if (
      statementLower.includes('percent') || 
      statementLower.includes('rate') || 
      statementLower.includes('index') ||
      statementLower.includes('level') ||
      statementLower.includes('ratio')
    ) {
      score += 0.1;
      supporting_evidence.push("References measurable economic metrics");
      reasoning += " The hypothesis references measurable economic metrics that can be objectively assessed.";
    } else {
      score -= 0.1;
      contrary_evidence.push("Lacks reference to measurable metrics");
      reasoning += " It could be improved by referencing specific measurable metrics.";
    }
    
    // Timeframe specification
    if (
      statementLower.includes('short-term') || 
      statementLower.includes('medium-term') || 
      statementLower.includes('long-term') ||
      statementLower.match(/within \d+ (months|years|quarters)/)
    ) {
      score += 0.1;
      supporting_evidence.push("Specifies timeframes for testing");
      reasoning += " It specifies clear timeframes when the predictions can be tested.";
    } else {
      score -= 0.05;
      contrary_evidence.push("Lacks timeframe specifications");
      reasoning += " The hypothesis lacks specific timeframes for testing its claims.";
    }
    
    // Specific conditions
    if (statementLower.includes('if') && statementLower.includes('then')) {
      score += 0.1;
      supporting_evidence.push("Specifies conditions under which predictions hold");
      reasoning += " It clearly specifies conditions under which the predictions should hold.";
    }
    
    // Check for unfalsifiable language
    const unfalsifiableTerms = [
      'eventually', 'in the long run', 'ultimately', 'tends to', 
      'generally', 'typically', 'usually', 'often', 
      'might', 'could', 'may', 'possibly'
    ];
    
    let unfalsifiableCount = 0;
    for (const term of unfalsifiableTerms) {
      if (statementLower.includes(term)) {
        unfalsifiableCount++;
      }
    }
    
    if (unfalsifiableCount > 2) {
      score -= 0.15;
      contrary_evidence.push(`Contains ${unfalsifiableCount} hedging or unfalsifiable terms`);
      reasoning += ` The hypothesis contains ${unfalsifiableCount} hedging or vague terms that make it difficult to falsify.`;
    }
    
    // Check for circularity or tautology
    if (
      statementLower.includes('by definition') ||
      statementLower.includes('necessarily') ||
      (statementLower.includes('if') && statementLower.includes('defined as'))
    ) {
      score -= 0.2;
      contrary_evidence.push("Contains potentially circular or tautological reasoning");
      reasoning += " It contains potentially circular or tautological reasoning that limits falsifiability.";
    }
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(1, score));
    confidence = Math.max(0, Math.min(1, confidence));
    
    return {
      criterion: EvaluationCriterion.Falsifiability,
      score,
      confidence,
      supporting_evidence,
      contrary_evidence,
      reasoning
    };
  }
  
  /**
   * Evaluates the practicability of implementing solutions from a hypothesis.
   * 
   * @param hypothesis The hypothesis to evaluate
   * @param context Additional context information
   * @returns The practicability evaluation
   */
  private evaluatePracticability(hypothesis: Hypothesis, context: any): CriterionEvaluation {
    const statementLower = hypothesis.statement.toLowerCase();
    const supporting_evidence: string[] = [];
    const contrary_evidence: string[] = [];
    let score = 0.5; // Start neutral
    let confidence = 0.6;
    let reasoning = "The hypothesis offers solutions with moderate practicability.";
    
    // Check if the hypothesis actually offers solutions
    if (
      !(statementLower.includes('should') || 
        statementLower.includes('recommend') || 
        statementLower.includes('proposal') ||
        statementLower.includes('policy') ||
        statementLower.includes('intervention') ||
        statementLower.includes('solution'))
    ) {
      return {
        criterion: EvaluationCriterion.PracticabilityOfSolutions,
        score: 0.5,
        confidence: 0.3,
        supporting_evidence: [],
        contrary_evidence: ["Hypothesis does not offer explicit solutions"],
        reasoning: "The hypothesis does not offer explicit solutions to evaluate for practicability."
      };
    }
    
    // Check for practicability factors
    
    // Implementation feasibility
    if (
      statementLower.includes('existing framework') || 
      statementLower.includes('established mechanism') ||
      statementLower.includes('existing institution')
    ) {
      score += 0.15;
      supporting_evidence.push("Utilizes existing frameworks or institutions");
      reasoning += " It utilizes existing frameworks or institutions rather than requiring new ones.";
    }
    
    // Political feasibility
    if (
      statementLower.includes('bipartisan') || 
      statementLower.includes('consensus') ||
      statementLower.includes('politically viable')
    ) {
      score += 0.15;
      supporting_evidence.push("Considers political feasibility");
      reasoning += " The proposal considers political feasibility.";
    } else if (
      statementLower.includes('radically') ||
      statementLower.includes('fundamental change') ||
      statementLower.includes('overhaul')
    ) {
      score -= 0.15;
      contrary_evidence.push("Proposes radical changes that may face significant resistance");
      reasoning += " It proposes radical changes that may face significant political resistance.";
    }
    
    // Resource requirements
    if (
      statementLower.includes('costly') ||
      statementLower.includes('expensive') ||
      statementLower.includes('significant resources')
    ) {
      score -= 0.1;
      contrary_evidence.push("Requires significant resources to implement");
      reasoning += " The proposal requires significant resources to implement.";
    } else if (
      statementLower.includes('low-cost') ||
      statementLower.includes('efficient') ||
      statementLower.includes('minimal resources')
    ) {
      score += 0.1;
      supporting_evidence.push("Requires minimal resources to implement");
      reasoning += " It requires minimal resources to implement.";
    }
    
    // Timeframe for implementation
    if (
      statementLower.includes('immediately') || 
      statementLower.includes('short-term') ||
      statementLower.includes('quickly')
    ) {
      score += 0.1;
      supporting_evidence.push("Can be implemented quickly");
      reasoning += " The solutions can be implemented quickly.";
    } else if (
      statementLower.includes('long-term') ||
      statementLower.includes('gradually') ||
      statementLower.includes('over time')
    ) {
      score -= 0.05;
      contrary_evidence.push("Requires extended implementation timeframe");
      reasoning += " The solutions require an extended implementation timeframe.";
    }
    
    // Stakeholder acceptance
    if (
      statementLower.includes('stakeholder') ||
      statementLower.includes('public support') ||
      statementLower.includes('industry acceptance')
    ) {
      score += 0.1;
      supporting_evidence.push("Considers stakeholder acceptance");
      reasoning += " The proposal considers stakeholder acceptance and support.";
    }
    
    // Domain-specific practicability
    if (statementLower.includes('monetary policy')) {
      score += 0.1;
      supporting_evidence.push("Central banks have established implementation mechanisms");
      reasoning += " Central banks have established mechanisms to implement monetary policy changes.";
    }
    
    if (statementLower.includes('fiscal policy') && !statementLower.includes('coordinated global')) {
      score += 0.05;
      supporting_evidence.push("Domestic fiscal policy has established implementation channels");
      reasoning += " Domestic fiscal policy has established implementation channels.";
    }
    
    if (statementLower.includes('global coordination') || statementLower.includes('international agreement')) {
      score -= 0.15;
      contrary_evidence.push("Requires difficult international coordination");
      reasoning += " The proposal requires difficult international coordination.";
    }
    
    if (statementLower.includes('tariff') && (statementLower.includes('reduction') || statementLower.includes('removal'))) {
      score += 0.1;
      supporting_evidence.push("Tariff adjustments are procedurally straightforward");
      reasoning += " Tariff adjustments are procedurally straightforward to implement.";
    }
    
    // Ensure score is within bounds
    score = Math.max(0, Math.min(1, score));
    confidence = Math.max(0, Math.min(1, confidence));
    
    return {
      criterion: EvaluationCriterion.PracticabilityOfSolutions,
      score,
      confidence,
      supporting_evidence,
      contrary_evidence,
      reasoning
    };
  }
  
  /**
   * Calculates an overall score based on criterion evaluations and weights.
   * 
   * @param evaluations Array of criterion evaluations
   * @param weights Weights for each criterion
   * @returns The overall score and confidence
   */
  private calculateOverallScore(
    evaluations: CriterionEvaluation[],
    weights: Record<EvaluationCriterion, number>
  ): { overall_score: number; overall_confidence: number } {
    let weightedScoreSum = 0;
    let weightSum = 0;
    let confidenceSum = 0;
    
    for (const evaluation of evaluations) {
      const weight = weights[evaluation.criterion] || 1.0;
      weightedScoreSum += evaluation.score * weight;
      weightSum += weight;
      confidenceSum += evaluation.confidence;
    }
    
    const overall_score = weightSum > 0 ? weightedScoreSum / weightSum : 0.5;
    const overall_confidence = evaluations.length > 0 ? confidenceSum / evaluations.length : 0.5;
    
    return {
      overall_score: Math.max(0, Math.min(1, overall_score)),
      overall_confidence: Math.max(0, Math.min(1, overall_confidence))
    };
  }
  
  /**
   * Generates refinement suggestions for a hypothesis based on evaluation results.
   * 
   * @param hypothesis The hypothesis being evaluated
   * @param evaluations Array of criterion evaluations
   * @returns Array of refinement suggestions
   */
  private generateRefinements(
    hypothesis: Hypothesis,
    evaluations: CriterionEvaluation[]
  ): string[] {
    const refinements: string[] = [];
    
    // Find the weakest criteria (lowest scores)
    const sortedEvaluations = [...evaluations].sort((a, b) => a.score - b.score);
    const weakestEvaluations = sortedEvaluations.slice(0, 2); // Focus on the two weakest
    
    for (const evaluation of weakestEvaluations) {
      switch (evaluation.criterion) {
        case EvaluationCriterion.Consistency:
          if (evaluation.score < 0.6) {
            refinements.push("Improve logical consistency by resolving potential contradictions in economic mechanisms.");
          }
          break;
          
        case EvaluationCriterion.EmpiricalSupport:
          if (evaluation.score < 0.6) {
            refinements.push("Strengthen empirical support by citing specific historical examples or economic data.");
          }
          break;
          
        case EvaluationCriterion.ExplanatoryPower:
          if (evaluation.score < 0.6) {
            refinements.push("Enhance explanatory power by addressing a broader range of economic phenomena.");
            refinements.push("Specify more concrete causal mechanisms to improve explanatory depth.");
          }
          break;
          
        case EvaluationCriterion.Predictive:
          if (evaluation.score < 0.6) {
            refinements.push("Improve predictive capabilities by making more specific, testable forecasts.");
            refinements.push("Include timeframes for predictions to enhance testability.");
          }
          break;
          
        case EvaluationCriterion.Simplicity:
          if (evaluation.score < 0.6) {
            refinements.push("Simplify the hypothesis by focusing on the most essential causal relationships.");
            refinements.push("Reduce specialized terminology to improve clarity and accessibility.");
          }
          break;
          
        case EvaluationCriterion.Falsifiability:
          if (evaluation.score < 0.6) {
            refinements.push("Improve falsifiability by specifying concrete economic metrics that would validate or invalidate the hypothesis.");
            refinements.push("Reduce hedging language and make more definitive claims that can be tested.");
          }
          break;
          
        case EvaluationCriterion.PracticabilityOfSolutions:
          if (evaluation.score < 0.6) {
            refinements.push("Enhance practicability by proposing solutions that work within existing policy frameworks.");
            refinements.push("Consider implementation constraints such as political feasibility and resource requirements.");
          }
          break;
      }
    }
    
    // Add general refinements based on hypothesis statement
    const statementLower = hypothesis.statement.toLowerCase();
    
    if (!statementLower.includes('because') && !statementLower.includes('due to')) {
      refinements.push("Explicitly state the causal mechanisms underlying the hypothesis.");
    }
    
    if (!statementLower.includes('data') && !statementLower.includes('evidence') && !statementLower.includes('research')) {
      refinements.push("Reference specific economic data or research that supports the hypothesis.");
    }
    
    // Limit to a reasonable number of refinements
    return refinements.slice(0, 4);
  }
  
  /**
   * Generates alternative hypotheses based on evaluation results.
   * 
   * @param hypothesis The original hypothesis
   * @param evaluations Array of criterion evaluations
   * @param maxAlternatives Maximum number of alternatives to generate
   * @returns Array of alternative hypotheses
   */
  private async generateAlternativeHypotheses(
    hypothesis: Hypothesis,
    evaluations: CriterionEvaluation[],
    maxAlternatives: number = 2
  ): Promise<Hypothesis[]> {
    const alternativeHypotheses: Hypothesis[] = [];
    const originalStatement = hypothesis.statement;
    const statementLower = originalStatement.toLowerCase();
    
    // Find the weakest criteria
    const sortedEvaluations = [...evaluations].sort((a, b) => a.score - b.score);
    const weakestCriterion = sortedEvaluations[0].criterion;
    
    // Generate alternatives based on domain and weakness
    
    // Handle stagflation hypotheses
    if (statementLower.includes('stagflation')) {
      if (weakestCriterion === EvaluationCriterion.EmpiricalSupport || weakestCriterion === EvaluationCriterion.ExplanatoryPower) {
        // Alternative emphasizing supply-side factors
        if (!statementLower.includes('supply shock') && !statementLower.includes('supply constraint')) {
          alternativeHypotheses.push({
            statement: "Stagflation is primarily driven by persistent supply constraints rather than demand factors, as evidenced by the concurrent rise in inflation and unemployment during supply shock episodes such as the 1970s oil crises. This explains why traditional demand-management tools have limited effectiveness in addressing stagflation.",
            supporting_evidence: [
              "Historical stagflation episodes coincided with major supply shocks",
              "Traditional monetary policy tools were less effective during these periods"
            ],
            contrary_evidence: [
              "Some stagflation episodes also featured expansionary policies"
            ]
          });
        }
        
        // Alternative emphasizing expectation channels
        if (!statementLower.includes('expectation')) {
          alternativeHypotheses.push({
            statement: "Stagflation persistence is significantly driven by the de-anchoring of inflation expectations, where supply shocks trigger an initial inflation surge that becomes self-reinforcing through wage-price spirals when expectations are not well-anchored by credible monetary policy.",
            supporting_evidence: [
              "Inflation expectations data from the 1970s shows de-anchoring",
              "Countries with stronger monetary policy credibility experienced less severe stagflation"
            ],
            contrary_evidence: [
              "Supply constraints were still the initial trigger in most cases"
            ]
          });
        }
      } else if (weakestCriterion === EvaluationCriterion.Predictive || weakestCriterion === EvaluationCriterion.Falsifiability) {
        // Alternative with more specific predictions
        alternativeHypotheses.push({
          statement: "If current supply chain constraints persist for another 6-12 months, we will observe stagflation characterized by inflation remaining above 4% while unemployment rises by 0.5-1.0 percentage points. This would be measurable through the misery index exceeding 10 by Q2 2023.",
          supporting_evidence: [
            "Current supply constraints remain unresolved",
            "Inflation expectations are becoming less anchored in recent survey data"
          ],
          contrary_evidence: [
            "Labor markets remain tight in many sectors",
            "Some supply constraints are beginning to ease"
          ]
        });
      }
    }
    
    // Handle tariff hypotheses
    else if (statementLower.includes('tariff')) {
      if (weakestCriterion === EvaluationCriterion.EmpiricalSupport || weakestCriterion === EvaluationCriterion.ExplanatoryPower) {
        // Alternative emphasizing distributional effects
        if (!statementLower.includes('distributional') && !statementLower.includes('sector')) {
          alternativeHypotheses.push({
            statement: "The economic impact of tariffs is highly uneven across sectors, creating concentrated benefits for import-competing industries but dispersed costs across consumers and downstream industries. This asymmetry explains why tariffs persist despite their typically negative overall economic impact.",
            supporting_evidence: [
              "Sector-specific data shows concentrated gains in protected industries",
              "Consumer price increases are typically diffuse across many products"
            ],
            contrary_evidence: [
              "Some tariffs may have broader strategic benefits beyond direct economic effects"
            ]
          });
        }
      } else if (weakestCriterion === EvaluationCriterion.PracticabilityOfSolutions) {
        // Alternative with more practical recommendations
        alternativeHypotheses.push({
          statement: "A strategic approach to tariff reduction would prioritize intermediate goods used in domestic manufacturing while maintaining tariffs on finished goods, implemented gradually over 24-36 months to allow for adjustment. This sequenced approach balances the benefits of reduced input costs with the need for adjustment time in protected industries.",
          supporting_evidence: [
            "Previous staged tariff reductions have shown better adjustment outcomes",
            "Intermediate goods tariffs have larger downstream effects"
          ],
          contrary_evidence: [
            "May still face political resistance from directly affected industries"
          ]
        });
      }
    }
    
    // Handle inflation hypotheses
    else if (statementLower.includes('inflation')) {
      if (weakestCriterion === EvaluationCriterion.Consistency || weakestCriterion === EvaluationCriterion.ExplanatoryPower) {
        // Alternative with different causal emphasis
        if (statementLower.includes('demand')) {
          alternativeHypotheses.push({
            statement: "Current inflation dynamics are primarily driven by supply-side constraints rather than excess demand, as evidenced by the concentrated nature of price increases in sectors affected by specific bottlenecks and capacity limitations. This explains why broad monetary tightening has had a lagged and limited effect.",
            supporting_evidence: [
              "Price increases concentrated in supply-constrained sectors",
              "Wage growth has lagged inflation in many sectors"
            ],
            contrary_evidence: [
              "Overall demand remains elevated by some measures",
              "Broad money supply growth preceded inflation surge"
            ]
          });
        } else {
          alternativeHypotheses.push({
            statement: "Current inflation is primarily demand-driven, resulting from the combination of expansionary fiscal and monetary policies that significantly increased aggregate demand while supply was still recovering. The breadth of price increases across sectors supports this demand-pull characterization.",
            supporting_evidence: [
              "Broad-based price increases across multiple sectors",
              "Significant expansion of money supply and fiscal stimulus preceded inflation"
            ],
            contrary_evidence: [
              "Specific supply constraints in key sectors like energy",
              "Lingering pandemic-related supply chain disruptions"
            ]
          });
        }
      } else if (weakestCriterion === EvaluationCriterion.Predictive) {
        // Alternative with more specific predictions
        alternativeHypotheses.push({
          statement: "If the central bank maintains its current tightening path, inflation will decline to within 1 percentage point of target within 12-18 months, but at the cost of increasing the unemployment rate by 1.0-1.5 percentage points. This can be measured through the PCE index and BLS unemployment data by Q2 2024.",
          supporting_evidence: [
            "Historical monetary policy lags typically range from 12-18 months",
            "Phillips curve relationships suggest this unemployment-inflation tradeoff"
          ],
          contrary_evidence: [
            "Supply-side improvements could reduce inflation with less unemployment impact",
            "Inflation expectations may be more anchored than in previous tightening cycles"
          ]
        });
      }
    }
    
    // Generate general alternative if not enough domain-specific ones
    if (alternativeHypotheses.length < maxAlternatives) {
      // Contrarian alternative - take opposing view
      const contrarian = this.generateContrarianHypothesis(hypothesis, evaluations);
      if (contrarian) {
        alternativeHypotheses.push(contrarian);
      }
      
      // Synthesis alternative - combine with other factors
      const synthesis = this.generateSynthesisHypothesis(hypothesis, evaluations);
      if (synthesis) {
        alternativeHypotheses.push(synthesis);
      }
    }
    
    return alternativeHypotheses.slice(0, maxAlternatives);
  }
  
  /**
   * Generates a contrarian hypothesis that takes an opposing view.
   * 
   * @param hypothesis The original hypothesis
   * @param evaluations Array of criterion evaluations
   * @returns A contrarian hypothesis or null
   */
  private generateContrarianHypothesis(
    hypothesis: Hypothesis,
    evaluations: CriterionEvaluation[]
  ): Hypothesis | null {
    const statement = hypothesis.statement;
    const statementLower = statement.toLowerCase();
    
    // Look for key claims to contradict
    if (statementLower.includes('primarily') || statementLower.includes('mainly')) {
      if (statementLower.includes('demand')) {
        return {
          statement: statement.replace(/primarily demand/i, "primarily supply-side constraints")
            .replace(/mainly demand/i, "mainly supply-side constraints"),
          supporting_evidence: [
            "Selective price increases in supply-constrained sectors",
            "Capacity utilization limitations in key industries"
          ],
          contrary_evidence: [
            "Broad money supply growth preceded inflation surge",
            "Unemployment rates remain relatively low"
          ]
        };
      } else if (statementLower.includes('supply')) {
        return {
          statement: statement.replace(/primarily supply/i, "primarily excess aggregate demand")
            .replace(/mainly supply/i, "mainly excess aggregate demand"),
          supporting_evidence: [
            "Broad-based price increases across multiple sectors",
            "Significant expansion of monetary and fiscal stimulus"
          ],
          contrary_evidence: [
            "Ongoing supply chain disruptions in key sectors",
            "Production capacity constraints in certain industries"
          ]
        };
      }
    }
    
    if (statementLower.includes('will increase') || statementLower.includes('will rise')) {
      return {
        statement: statement.replace(/will increase/i, "will remain stable or decrease")
          .replace(/will rise/i, "will remain stable or fall"),
        supporting_evidence: [
          "Countervailing factors may offset expected increases",
          "Historical precedents show resilience in similar scenarios"
        ],
        contrary_evidence: [
          "Current trend indicators suggest continued increases",
          "Structural factors point toward persistent pressures"
        ]
      };
    }
    
    if (statementLower.includes('will decrease') || statementLower.includes('will fall')) {
      return {
        statement: statement.replace(/will decrease/i, "will remain stable or increase")
          .replace(/will fall/i, "will remain stable or rise"),
        supporting_evidence: [
          "Underlying structural factors suggest persistent pressures",
          "Adaptive market behaviors may counteract expected decreases"
        ],
        contrary_evidence: [
          "Current trend indicators suggest continued decreases",
          "Policy interventions are designed to drive reductions"
        ]
      };
    }
    
    if (statementLower.includes('effective') || statementLower.includes('sufficient')) {
      return {
        statement: statement.replace(/effective/i, "insufficient")
          .replace(/sufficient/i, "inadequate"),
        supporting_evidence: [
          "Historical precedents show limited impact of similar approaches",
          "Structural constraints may limit policy effectiveness"
        ],
        contrary_evidence: [
          "Recent policy implementations have shown promising results",
          "Theoretical models suggest effectiveness under current conditions"
        ]
      };
    }
    
    if (statementLower.includes('ineffective') || statementLower.includes('insufficient')) {
      return {
        statement: statement.replace(/ineffective/i, "effective")
          .replace(/insufficient/i, "sufficient"),
        supporting_evidence: [
          "Recent policy implementations have shown promising results",
          "Theoretical models support effectiveness under current conditions"
        ],
        contrary_evidence: [
          "Historical precedents suggest limited impact",
          "Structural constraints may undermine effectiveness"
        ]
      };
    }
    
    // No clear contrarian angle found
    return null;
  }
  
  /**
   * Generates a synthesis hypothesis that combines the original with other factors.
   * 
   * @param hypothesis The original hypothesis
   * @param evaluations Array of criterion evaluations
   * @returns A synthesis hypothesis or null
   */
  private generateSynthesisHypothesis(
    hypothesis: Hypothesis,
    evaluations: CriterionEvaluation[]
  ): Hypothesis | null {
    const statement = hypothesis.statement;
    const statementLower = statement.toLowerCase();
    
    // Add expectation channels if not present
    if (!statementLower.includes('expectation')) {
      return {
        statement: `${statement} Furthermore, this effect is amplified by changes in market expectations, which create feedback loops that reinforce the initial economic impact through anticipatory behavior by firms and households.`,
        supporting_evidence: [
          "Survey data shows expectation shifts correlate with economic behavior",
          "Forward-looking indicators often precede fundamental changes"
        ],
        contrary_evidence: [
          "Some economic actors have limited information or rationality",
          "Institutional constraints may limit expectation-driven responses"
        ]
      };
    }
    
    // Add international dimension if not present
    if (!statementLower.includes('global') && !statementLower.includes('international')) {
      return {
        statement: `${statement} This dynamic is further complicated by international spillovers, as global supply chains and capital flows transmit economic shocks across borders, creating feedback effects that amplify the initial impact.`,
        supporting_evidence: [
          "Trade interconnectedness has increased economic correlations",
          "Capital flow data shows rapid transmission of economic shocks"
        ],
        contrary_evidence: [
          "Some economies maintain partial insulation from global shocks",
          "Policy autonomy remains possible in specific domains"
        ]
      };
    }
    
    // Add distributional dimension if not present
    if (!statementLower.includes('distribution') && !statementLower.includes('inequality')) {
      return {
        statement: `${statement} Importantly, these effects are not distributed uniformly, with significantly different impacts across income groups, sectors, and regions, which explains some of the divergent perspectives on optimal policy responses.`,
        supporting_evidence: [
          "Sectoral data shows heterogeneous impacts of economic shocks",
          "Income quintile analysis reveals divergent experiences of economic changes"
        ],
        contrary_evidence: [
          "Some economic policies have relatively uniform effects",
          "Certain metrics show convergent impacts across groups"
        ]
      };
    }
    
    // Add policy credibility dimension if not present
    if (!statementLower.includes('credibility') && !statementLower.includes('confidence')) {
      return {
        statement: `${statement} The effectiveness of policy responses critically depends on institutional credibility and market confidence, which serve as amplifiers or dampeners of implemented measures through their effect on compliance and expectation formation.`,
        supporting_evidence: [
          "Policy effectiveness correlates with institutional credibility metrics",
          "Market response data shows different reactions to similar policies from different sources"
        ],
        contrary_evidence: [
          "Some policies work through mechanical channels regardless of credibility",
          "Certain market segments show limited sensitivity to credibility factors"
        ]
      };
    }
    
    // No clear synthesis angle found
    return null;
  }
  
  /**
   * Extracts keywords from a statement for matching against references.
   * 
   * @param statement The statement to extract keywords from
   * @returns Array of extracted keywords
   */
  private extractKeywords(statement: string): string[] {
    const stopWords = new Set([
      'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'this', 'that', 'these', 'those',
      'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
      'did', 'to', 'from', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'by', 'for',
      'of', 'at', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
      'after', 'above', 'below', 'up', 'down', 'will', 'would', 'can', 'could', 'may', 'might',
      'must', 'should'
    ]);
    
    // Extract words, convert to lowercase, filter stop words
    const words = statement.toLowerCase().match(/\b\w+\b/g) || [];
    return words.filter(word => !stopWords.has(word) && word.length > 2);
  }
  
  /**
   * Loads historical economic data for reference.
   */
  private loadHistoricalData(): void {
    // In a real implementation, this would load data from databases or APIs
    
    // Mock implementation with some basic historical data
    this.historicalData.set('inflation', [
      { period: '1970s', value: 7.1, description: 'Period of stagflation with high inflation' },
      { period: '1980s', value: 5.6, description: 'Volcker disinflation period' },
      { period: '1990s', value: 3.0, description: 'Moderate inflation period' },
      { period: '2000s', value: 2.6, description: 'Low inflation period' },
      { period: '2010s', value: 1.8, description: 'Below-target inflation period' },
      { period: 'Current', value: 6.5, description: 'Post-pandemic inflationary period' }
    ]);
    
    this.historicalData.set('unemployment', [
      { period: '1970s', value: 6.2, description: 'Rising unemployment with stagflation' },
      { period: '1980s', value: 7.3, description: 'High unemployment during disinflation' },
      { period: '1990s', value: 5.8, description: 'Moderate unemployment' },
      { period: '2000s', value: 5.5, description: 'Varied unemployment with recession spike' },
      { period: '2010s', value: 6.9, description: 'Declining unemployment after recession' },
      { period: 'Current', value: 3.7, description: 'Low unemployment post-pandemic' }
    ]);
    
    this.historicalData.set('gdp_growth', [
      { period: '1970s', value: 3.2, description: 'Slowing growth during stagflation' },
      { period: '1980s', value: 3.1, description: 'Recovery after recession' },
      { period: '1990s', value: 3.4, description: 'Strong growth period' },
      { period: '2000s', value: 1.9, description: 'Slower growth with financial crisis' },
      { period: '2010s', value: 2.3, description: 'Moderate growth post-recession' },
      { period: 'Current', value: 2.1, description: 'Recovery from pandemic contraction' }
    ]);
    
    this.historicalData.set('tariffs', [
      { period: 'Pre-GATT', value: 20.0, description: 'High tariff period before trade agreements' },
      { period: 'GATT Era', value: 6.0, description: 'Declining tariffs under trade agreements' },
      { period: 'WTO Early', value: 5.0, description: 'Further tariff reductions under WTO' },
      { period: 'China Shock', value: 3.5, description: 'Low tariff period with China integration' },
      { period: 'Trade War', value: 7.5, description: 'Rising tariffs during trade disputes' },
      { period: 'Current', value: 6.0, description: 'Partial reversal of trade war increases' }
    ]);
  }
  
  /**
   * Loads economic models for use in evaluations.
   */
  private loadEconomicModels(): void {
    // In a real implementation, this would load model specifications
    
    // Mock implementation with placeholders for economic models
    this.economicModels.set('phillips_curve', {
      type: 'regression',
      variables: ['inflation', 'unemployment'],
      parameters: { slope: -0.5, intercept: 7.0 },
      description: 'Relationship between inflation and unemployment',
      fit_metrics: { r_squared: 0.65, p_value: 0.02 }
    });
    
    this.economicModels.set('is_lm', {
      type: 'equilibrium',
      variables: ['interest_rate', 'output', 'money_supply', 'fiscal_policy'],
      parameters: { is_slope: -0.8, lm_slope: 0.6 },
      description: 'Goods and money market equilibrium',
      fit_metrics: { r_squared: 0.73, p_value: 0.01 }
    });
    
    this.economicModels.set('trade_balance', {
      type: 'regression',
      variables: ['tariff_rate', 'exchange_rate', 'domestic_demand', 'foreign_demand'],
      parameters: { tariff_coefficient: -0.3, exchange_coefficient: 0.7 },
      description: 'Determinants of trade balance',
      fit_metrics: { r_squared: 0.68, p_value: 0.03 }
    });
    
    this.economicModels.set('inflation_expectations', {
      type: 'adaptive',
      variables: ['past_inflation', 'policy_credibility', 'output_gap'],
      parameters: { adaptive_weight: 0.7, credibility_impact: -0.5 },
      description: 'Formation of inflation expectations',
      fit_metrics: { r_squared: 0.82, p_value: 0.01 }
    });
  }
}