/**
 * Economic Verification Framework
 *
 * A comprehensive framework for verifying economic theorems using multiple methods,
 * cross-validation, and confidence scoring. This framework integrates with the
 * TheoremProverClient but provides additional orchestration, strategy selection,
 * and verification analytics.
 */

import { 
  TheoremProverClient, 
  EconomicTheorem, 
  ProofMethodType, 
  VerificationResult, 
  ProofStep,
  CounterExample
} from './theorem_prover_client';

/**
 * Verification strategy configurations
 */
export enum VerificationStrategy {
  SingleMethod = 'single_method',   // Use a single verification method
  SequentialMethods = 'sequential_methods', // Try methods in sequence until success
  ParallelMethods = 'parallel_methods', // Try multiple methods in parallel
  AdaptiveStrategy = 'adaptive_strategy' // Choose method based on theorem characteristics
}

/**
 * Verification level settings
 */
export enum VerificationLevel {
  Basic = 'basic',           // Simple verification
  Standard = 'standard',     // Thorough verification
  Rigorous = 'rigorous',     // Highly detailed verification
  Exhaustive = 'exhaustive'  // Maximum verification effort
}

/**
 * Parameter settings for verification
 */
export interface VerificationParameters {
  timeLimit?: number;        // Maximum time for verification (ms)
  confidenceThreshold?: number; // Minimum confidence level required
  includeSensitivityAnalysis?: boolean; // Whether to include sensitivity analysis
  generateCounterExamples?: boolean; // Whether to generate counter-examples
  detailedProofRequired?: boolean; // Whether detailed proof steps are required
  crossValidationRequired?: boolean; // Whether cross-validation is required
}

/**
 * Extended verification result that includes additional metadata
 */
export interface EnhancedVerificationResult {
  // Basic verification result
  verified: boolean;
  confidence: number;
  theoremName: string;
  
  // Method information
  primaryMethod: ProofMethodType;
  secondaryMethods?: ProofMethodType[];
  
  // Detailed results
  methodResults: Map<ProofMethodType, VerificationResult>;
  
  // Cross-validation information
  crossValidated: boolean;
  crossValidationScore?: number;
  
  // Sensitivity analysis
  sensitivityAnalysis?: {
    robustToAssumptionChanges: boolean;
    criticalAssumptions: string[];
    stabilityScore: number;
  };
  
  // Verification analytics
  verificationProcess: {
    startTime: number;
    endTime: number;
    totalDuration: number;
    methodsDuration: Map<ProofMethodType, number>;
    attemptedMethods: ProofMethodType[];
    successfulMethods: ProofMethodType[];
    failedMethods: ProofMethodType[];
  };
  
  // Composite proof
  compositeProof?: {
    steps: ProofStep[];
    counterExamples: CounterExample[];
    limitations: string[];
    applicabilityConditions: string[];
  };
  
  // Recommendations
  recommendations?: {
    improvementSuggestions: string[];
    alternativeApproaches: string[];
    furtherResearch: string[];
  };
}

/**
 * Options for the verification process
 */
export interface VerificationOptions {
  strategy?: VerificationStrategy;
  level?: VerificationLevel;
  preferredMethods?: ProofMethodType[];
  parameters?: VerificationParameters;
  domainSpecificSettings?: Record<string, any>;
}

/**
 * The Verification Framework orchestrates the verification of economic theorems.
 */
export class VerificationFramework {
  private theoremProverClient: TheoremProverClient;
  private isInitialized: boolean = false;
  private verificationCache: Map<string, EnhancedVerificationResult> = new Map();
  
  /**
   * Creates a new VerificationFramework with a TheoremProverClient.
   * 
   * @param theoremProverClient The theorem prover client to use
   */
  constructor(theoremProverClient: TheoremProverClient) {
    this.theoremProverClient = theoremProverClient;
  }
  
  /**
   * Initializes the verification framework.
   * 
   * @returns A promise that resolves when initialization is complete
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      console.log('Verification Framework already initialized');
      return;
    }
    
    console.log('Initializing Verification Framework...');
    
    // Ensure the theorem prover client is initialized
    try {
      if (!this.theoremProverClient) {
        throw new Error('No TheoremProverClient provided');
      }
      
      // Setup verification cache
      this.verificationCache = new Map();
      
      this.isInitialized = true;
      console.log('Verification Framework initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Verification Framework:', error);
      throw error;
    }
  }
  
  /**
   * Verifies an economic theorem using the specified strategy, level, and parameters.
   * 
   * @param theorem The theorem to verify
   * @param options Verification options
   * @returns Enhanced verification result
   */
  async verifyTheorem(
    theorem: EconomicTheorem,
    options: VerificationOptions = {}
  ): Promise<EnhancedVerificationResult> {
    if (!this.isInitialized) {
      throw new Error('Verification Framework must be initialized before verifying theorems');
    }
    
    console.log(`Verifying theorem: ${theorem.name}`);
    
    // Set default options
    const strategy = options.strategy || VerificationStrategy.AdaptiveStrategy;
    const level = options.level || VerificationLevel.Standard;
    const parameters = options.parameters || {};
    
    // Check cache if enabled
    const cacheKey = this.generateCacheKey(theorem, strategy, level);
    if (this.verificationCache.has(cacheKey) && !parameters.timeLimit) {
      console.log(`Using cached verification result for theorem: ${theorem.name}`);
      return this.verificationCache.get(cacheKey)!;
    }
    
    // Initialize verification process tracking
    const verificationProcess = {
      startTime: Date.now(),
      endTime: 0,
      totalDuration: 0,
      methodsDuration: new Map<ProofMethodType, number>(),
      attemptedMethods: [],
      successfulMethods: [],
      failedMethods: []
    };
    
    // Determine appropriate verification strategy based on options
    let result: EnhancedVerificationResult;
    
    switch (strategy) {
      case VerificationStrategy.SingleMethod:
        result = await this.applySingleMethodStrategy(theorem, level, options);
        break;
      
      case VerificationStrategy.SequentialMethods:
        result = await this.applySequentialMethodsStrategy(theorem, level, options);
        break;
      
      case VerificationStrategy.ParallelMethods:
        result = await this.applyParallelMethodsStrategy(theorem, level, options);
        break;
      
      case VerificationStrategy.AdaptiveStrategy:
      default:
        result = await this.applyAdaptiveStrategy(theorem, level, options);
        break;
    }
    
    // Update verification process tracking
    verificationProcess.endTime = Date.now();
    verificationProcess.totalDuration = verificationProcess.endTime - verificationProcess.startTime;
    result.verificationProcess = verificationProcess;
    
    // Add recommendations if required
    if (level === VerificationLevel.Rigorous || level === VerificationLevel.Exhaustive) {
      result.recommendations = this.generateRecommendations(result, theorem);
    }
    
    // Cache the result
    this.verificationCache.set(cacheKey, result);
    
    return result;
  }
  
  /**
   * Strategy that uses a single verification method.
   * 
   * @param theorem The theorem to verify
   * @param level The verification level
   * @param options Verification options
   * @returns Enhanced verification result
   */
  private async applySingleMethodStrategy(
    theorem: EconomicTheorem,
    level: VerificationLevel,
    options: VerificationOptions
  ): Promise<EnhancedVerificationResult> {
    // Determine method to use
    const method = this.determinePreferredMethod(theorem, options.preferredMethods);
    
    // Track start time
    const startTime = Date.now();
    
    // Perform verification
    const basicResult = await this.theoremProverClient.verifyTheorem(theorem, {
      method: method,
      timeLimit: options.parameters?.timeLimit,
      useCache: true,
      generateCounterExamples: options.parameters?.generateCounterExamples
    });
    
    // Calculate method duration
    const methodDuration = Date.now() - startTime;
    
    // Create enhanced result
    const enhancedResult: EnhancedVerificationResult = {
      verified: basicResult.verified,
      confidence: basicResult.confidence,
      theoremName: basicResult.theoremName,
      primaryMethod: method,
      methodResults: new Map([[method, basicResult]]),
      crossValidated: false,
      verificationProcess: {
        startTime,
        endTime: Date.now(),
        totalDuration: methodDuration,
        methodsDuration: new Map([[method, methodDuration]]),
        attemptedMethods: [method],
        successfulMethods: basicResult.verified ? [method] : [],
        failedMethods: basicResult.verified ? [] : [method]
      },
      compositeProof: {
        steps: basicResult.proofSteps,
        counterExamples: basicResult.counterExamples,
        limitations: basicResult.limitations || [],
        applicabilityConditions: []
      }
    };
    
    return enhancedResult;
  }
  
  /**
   * Strategy that tries methods in sequence until a successful verification.
   * 
   * @param theorem The theorem to verify
   * @param level The verification level
   * @param options Verification options
   * @returns Enhanced verification result
   */
  private async applySequentialMethodsStrategy(
    theorem: EconomicTheorem,
    level: VerificationLevel,
    options: VerificationOptions
  ): Promise<EnhancedVerificationResult> {
    // Determine methods to try based on level
    const methods = this.getMethodsForLevel(level, options.preferredMethods);
    
    // Result tracking
    const methodResults = new Map<ProofMethodType, VerificationResult>();
    const methodsDuration = new Map<ProofMethodType, number>();
    const attemptedMethods: ProofMethodType[] = [];
    const successfulMethods: ProofMethodType[] = [];
    const failedMethods: ProofMethodType[] = [];
    
    // Try methods in sequence
    let verifiedResult: VerificationResult | null = null;
    let primaryMethod: ProofMethodType | null = null;
    
    for (const method of methods) {
      // Track start time
      const startTime = Date.now();
      attemptedMethods.push(method);
      
      try {
        // Perform verification with current method
        const result = await this.theoremProverClient.verifyTheorem(theorem, {
          method,
          timeLimit: options.parameters?.timeLimit,
          useCache: true,
          generateCounterExamples: options.parameters?.generateCounterExamples
        });
        
        // Store result
        methodResults.set(method, result);
        const duration = Date.now() - startTime;
        methodsDuration.set(method, duration);
        
        // Track success/failure
        if (result.verified) {
          successfulMethods.push(method);
          if (!verifiedResult) {
            verifiedResult = result;
            primaryMethod = method;
          }
        } else {
          failedMethods.push(method);
        }
        
        // Stop if verification succeeded and we're not in exhaustive mode
        if (result.verified && level !== VerificationLevel.Exhaustive) {
          break;
        }
      } catch (error) {
        console.error(`Error verifying theorem with method ${method}:`, error);
        failedMethods.push(method);
        methodsDuration.set(method, Date.now() - startTime);
      }
    }
    
    // Create enhanced result
    const enhancedResult: EnhancedVerificationResult = {
      verified: !!verifiedResult,
      confidence: verifiedResult?.confidence || 0,
      theoremName: theorem.name,
      primaryMethod: primaryMethod || methods[0],
      secondaryMethods: attemptedMethods.filter(m => m !== primaryMethod),
      methodResults,
      crossValidated: successfulMethods.length > 1,
      crossValidationScore: successfulMethods.length > 1 ? this.calculateCrossValidationScore(methodResults, successfulMethods) : undefined,
      verificationProcess: {
        startTime: Date.now(), // This will be updated by the calling method
        endTime: 0,            // This will be updated by the calling method
        totalDuration: 0,      // This will be updated by the calling method
        methodsDuration,
        attemptedMethods,
        successfulMethods,
        failedMethods
      },
      compositeProof: this.createCompositeProof(methodResults, theorem)
    };
    
    // Add sensitivity analysis for higher levels
    if (level === VerificationLevel.Rigorous || level === VerificationLevel.Exhaustive) {
      enhancedResult.sensitivityAnalysis = await this.performSensitivityAnalysis(theorem, methodResults);
    }
    
    return enhancedResult;
  }
  
  /**
   * Strategy that tries multiple methods in parallel.
   * 
   * @param theorem The theorem to verify
   * @param level The verification level
   * @param options Verification options
   * @returns Enhanced verification result
   */
  private async applyParallelMethodsStrategy(
    theorem: EconomicTheorem,
    level: VerificationLevel,
    options: VerificationOptions
  ): Promise<EnhancedVerificationResult> {
    // Determine methods to try based on level
    const methods = this.getMethodsForLevel(level, options.preferredMethods);
    
    // Track start time
    const startTime = Date.now();
    
    // Verify with all methods in parallel
    const verificationPromises = methods.map(method => {
      const methodStartTime = Date.now();
      return this.theoremProverClient.verifyTheorem(theorem, {
        method,
        timeLimit: options.parameters?.timeLimit,
        useCache: true,
        generateCounterExamples: options.parameters?.generateCounterExamples
      })
      .then(result => ({
        method,
        result,
        duration: Date.now() - methodStartTime,
        success: true
      }))
      .catch(error => ({
        method,
        result: null,
        duration: Date.now() - methodStartTime,
        success: false,
        error
      }));
    });
    
    // Wait for all verifications to complete
    const results = await Promise.all(verificationPromises);
    
    // Process results
    const methodResults = new Map<ProofMethodType, VerificationResult>();
    const methodsDuration = new Map<ProofMethodType, number>();
    const attemptedMethods: ProofMethodType[] = [];
    const successfulMethods: ProofMethodType[] = [];
    const failedMethods: ProofMethodType[] = [];
    
    for (const { method, result, duration, success } of results) {
      attemptedMethods.push(method);
      methodsDuration.set(method, duration);
      
      if (success && result) {
        methodResults.set(method, result);
        if (result.verified) {
          successfulMethods.push(method);
        } else {
          failedMethods.push(method);
        }
      } else {
        failedMethods.push(method);
      }
    }
    
    // Determine primary method (highest confidence among successful methods)
    let primaryMethod: ProofMethodType | null = null;
    let highestConfidence = 0;
    
    for (const method of successfulMethods) {
      const result = methodResults.get(method)!;
      if (result.confidence > highestConfidence) {
        highestConfidence = result.confidence;
        primaryMethod = method;
      }
    }
    
    // If no successful method, use the one with highest confidence
    if (!primaryMethod && methodResults.size > 0) {
      let highestConfidence = 0;
      for (const [method, result] of methodResults.entries()) {
        if (result.confidence > highestConfidence) {
          highestConfidence = result.confidence;
          primaryMethod = method;
        }
      }
    }
    
    // Default to first method if still no primary method
    if (!primaryMethod && methods.length > 0) {
      primaryMethod = methods[0];
    }
    
    // Create enhanced result
    const enhancedResult: EnhancedVerificationResult = {
      verified: successfulMethods.length > 0,
      confidence: primaryMethod ? (methodResults.get(primaryMethod)?.confidence || 0) : 0,
      theoremName: theorem.name,
      primaryMethod: primaryMethod || methods[0],
      secondaryMethods: attemptedMethods.filter(m => m !== primaryMethod),
      methodResults,
      crossValidated: successfulMethods.length > 1,
      crossValidationScore: successfulMethods.length > 1 ? this.calculateCrossValidationScore(methodResults, successfulMethods) : undefined,
      verificationProcess: {
        startTime,
        endTime: Date.now(),
        totalDuration: Date.now() - startTime,
        methodsDuration,
        attemptedMethods,
        successfulMethods,
        failedMethods
      },
      compositeProof: this.createCompositeProof(methodResults, theorem)
    };
    
    // Add sensitivity analysis for higher levels
    if (level === VerificationLevel.Rigorous || level === VerificationLevel.Exhaustive) {
      enhancedResult.sensitivityAnalysis = await this.performSensitivityAnalysis(theorem, methodResults);
    }
    
    return enhancedResult;
  }
  
  /**
   * Strategy that adapts the verification approach based on theorem characteristics.
   * 
   * @param theorem The theorem to verify
   * @param level The verification level
   * @param options Verification options
   * @returns Enhanced verification result
   */
  private async applyAdaptiveStrategy(
    theorem: EconomicTheorem,
    level: VerificationLevel,
    options: VerificationOptions
  ): Promise<EnhancedVerificationResult> {
    // Analyze theorem to determine best approach
    const theoremAnalysis = this.analyzeTheorem(theorem);
    
    // For simple theorems with clear structure, use direct proof
    if (theoremAnalysis.complexity < 0.3) {
      return this.applySingleMethodStrategy(
        theorem,
        level,
        { ...options, preferredMethods: [ProofMethodType.DirectProof] }
      );
    }
    
    // For empirical theorems, use historical evidence validation
    if (theoremAnalysis.empiricalNature > 0.7) {
      return this.applySingleMethodStrategy(
        theorem,
        level,
        { ...options, preferredMethods: [ProofMethodType.HistoricalEvidence] }
      );
    }
    
    // For theorems with moderate complexity, use sequential strategy
    if (theoremAnalysis.complexity >= 0.3 && theoremAnalysis.complexity < 0.7) {
      return this.applySequentialMethodsStrategy(theorem, level, options);
    }
    
    // For highly complex theorems, use parallel strategy
    return this.applyParallelMethodsStrategy(theorem, level, options);
  }
  
  /**
   * Analyzes a theorem to determine its characteristics.
   * 
   * @param theorem The theorem to analyze
   * @returns Analysis of the theorem
   */
  private analyzeTheorem(theorem: EconomicTheorem): {
    complexity: number;
    empiricalNature: number;
    formalStructure: number;
    domain: string;
  } {
    // Basic indicators
    const statementLength = theorem.statement.length;
    const variableCount = theorem.variables.length;
    const constraintCount = theorem.constraints.length;
    
    // Calculate complexity (0-1)
    const complexity = Math.min(1, (
      (statementLength / 500) * 0.3 +
      (variableCount / 10) * 0.3 +
      (constraintCount / 5) * 0.4
    ));
    
    // Assess empirical nature (0-1)
    const empiricalKeywords = [
      'data', 'empirical', 'evidence', 'statistical', 'observed',
      'history', 'historical', 'measured', 'correlation', 'trend'
    ];
    
    let empiricalScore = 0;
    const statementLower = theorem.statement.toLowerCase();
    for (const keyword of empiricalKeywords) {
      if (statementLower.includes(keyword)) {
        empiricalScore += 0.1;
      }
    }
    const empiricalNature = Math.min(1, empiricalScore);
    
    // Assess formal structure (0-1)
    const formalKeywords = [
      'if', 'then', 'implies', 'therefore', 'thus', 'necessarily',
      'equivalent', 'if and only if', 'contradiction', 'formally'
    ];
    
    let formalScore = 0;
    for (const keyword of formalKeywords) {
      if (statementLower.includes(keyword)) {
        formalScore += 0.1;
      }
    }
    const formalStructure = Math.min(1, formalScore);
    
    return {
      complexity,
      empiricalNature,
      formalStructure,
      domain: theorem.domain
    };
  }
  
  /**
   * Performs sensitivity analysis on a theorem by altering assumptions.
   * 
   * @param theorem The theorem to analyze
   * @param methodResults Results from different verification methods
   * @returns Sensitivity analysis results
   */
  private async performSensitivityAnalysis(
    theorem: EconomicTheorem,
    methodResults: Map<ProofMethodType, VerificationResult>
  ): Promise<{
    robustToAssumptionChanges: boolean;
    criticalAssumptions: string[];
    stabilityScore: number;
  }> {
    // Clone the theorem to avoid modifying the original
    const baseTheorem = { ...theorem };
    
    // Find critical assumptions by removing them one at a time
    const criticalAssumptions = [];
    const assumptionSensitivity = new Map<string, number>();
    
    // Get the most successful method
    let mostSuccessfulMethod: ProofMethodType | null = null;
    let highestConfidence = 0;
    
    for (const [method, result] of methodResults.entries()) {
      if (result.verified && result.confidence > highestConfidence) {
        mostSuccessfulMethod = method;
        highestConfidence = result.confidence;
      }
    }
    
    // If no successful method, use the one with highest confidence
    if (!mostSuccessfulMethod) {
      for (const [method, result] of methodResults.entries()) {
        if (result.confidence > highestConfidence) {
          mostSuccessfulMethod = method;
          highestConfidence = result.confidence;
        }
      }
    }
    
    // Use direct proof if still no method
    if (!mostSuccessfulMethod) {
      mostSuccessfulMethod = ProofMethodType.DirectProof;
    }
    
    // Test each assumption
    for (let i = 0; i < baseTheorem.assumptions.length; i++) {
      const assumption = baseTheorem.assumptions[i];
      
      // Create a version without this assumption
      const modifiedTheorem = { ...baseTheorem };
      modifiedTheorem.assumptions = [...baseTheorem.assumptions];
      modifiedTheorem.assumptions.splice(i, 1);
      
      // Try to verify the modified theorem
      const modifiedResult = await this.theoremProverClient.verifyTheorem(modifiedTheorem, {
        method: mostSuccessfulMethod,
        useCache: false // Ensure fresh verification
      });
      
      // Calculate sensitivity for this assumption
      const sensitivityScore = highestConfidence - modifiedResult.confidence;
      assumptionSensitivity.set(assumption, sensitivityScore);
      
      // If removing the assumption changes the verification outcome significantly
      if (sensitivityScore > 0.2) {
        criticalAssumptions.push(assumption);
      }
    }
    
    // Calculate overall stability score
    const sensitivityValues = Array.from(assumptionSensitivity.values());
    const averageSensitivity = sensitivityValues.reduce((sum, val) => sum + val, 0) /
                               Math.max(1, sensitivityValues.length);
    const stabilityScore = Math.max(0, 1 - averageSensitivity);
    
    return {
      robustToAssumptionChanges: stabilityScore > 0.7,
      criticalAssumptions,
      stabilityScore
    };
  }
  
  /**
   * Creates a composite proof from multiple verification results.
   * 
   * @param methodResults Results from different verification methods
   * @param theorem The original theorem
   * @returns Composite proof
   */
  private createCompositeProof(
    methodResults: Map<ProofMethodType, VerificationResult>,
    theorem: EconomicTheorem
  ): {
    steps: ProofStep[];
    counterExamples: CounterExample[];
    limitations: string[];
    applicabilityConditions: string[];
  } {
    // Gather all proof steps
    const allSteps: ProofStep[] = [];
    const allCounterExamples: CounterExample[] = [];
    const allLimitations: string[] = [];
    
    for (const result of methodResults.values()) {
      // Add proof steps with method identifier
      const stepsWithMethod = result.proofSteps.map(step => ({
        ...step,
        description: `[${result.method}] ${step.description}`
      }));
      allSteps.push(...stepsWithMethod);
      
      // Add counter-examples
      allCounterExamples.push(...result.counterExamples);
      
      // Add limitations
      if (result.limitations) {
        allLimitations.push(...result.limitations);
      }
    }
    
    // Infer applicability conditions from assumptions and theorem domain
    const applicabilityConditions = [
      "Assumes standard economic conditions",
      ...theorem.assumptions.map(a => `Requires ${a}`),
      `Domain: ${theorem.domain}`
    ];
    
    return {
      steps: this.deduplicateAndOrderProofSteps(allSteps),
      counterExamples: this.deduplicateCounterExamples(allCounterExamples),
      limitations: [...new Set(allLimitations)],
      applicabilityConditions
    };
  }
  
  /**
   * Deduplicates and orders proof steps into a coherent sequence.
   * 
   * @param steps All proof steps to organize
   * @returns Deduplicated and ordered steps
   */
  private deduplicateAndOrderProofSteps(steps: ProofStep[]): ProofStep[] {
    // Simple deduplication by conclusion
    const conclusionMap = new Map<string, ProofStep>();
    
    for (const step of steps) {
      if (!conclusionMap.has(step.conclusion) || 
          step.premises.length < conclusionMap.get(step.conclusion)!.premises.length) {
        conclusionMap.set(step.conclusion, step);
      }
    }
    
    // Collect deduplicated steps
    const dedupSteps = Array.from(conclusionMap.values());
    
    // Order steps to form a coherent proof
    const orderedSteps: ProofStep[] = [];
    const concludedStatements = new Set<string>();
    const remainingSteps = [...dedupSteps];
    
    // Add steps that don't depend on other steps
    const initialSteps = remainingSteps.filter(step => step.premises.length === 0);
    for (const step of initialSteps) {
      orderedSteps.push(step);
      concludedStatements.add(step.conclusion);
      remainingSteps.splice(remainingSteps.indexOf(step), 1);
    }
    
    // Add steps whose premises have been concluded
    let progress = true;
    while (progress && remainingSteps.length > 0) {
      progress = false;
      
      for (let i = 0; i < remainingSteps.length; i++) {
        const step = remainingSteps[i];
        const allPremisesConcluded = step.premises.every(premise => 
          concludedStatements.has(premise) || 
          orderedSteps.some(s => s.id === premise)
        );
        
        if (allPremisesConcluded) {
          orderedSteps.push(step);
          concludedStatements.add(step.conclusion);
          remainingSteps.splice(i, 1);
          progress = true;
          break;
        }
      }
    }
    
    // Add any remaining steps
    orderedSteps.push(...remainingSteps);
    
    return orderedSteps;
  }
  
  /**
   * Deduplicates counter-examples.
   * 
   * @param counterExamples All counter-examples to deduplicate
   * @returns Deduplicated counter-examples
   */
  private deduplicateCounterExamples(counterExamples: CounterExample[]): CounterExample[] {
    // Simple deduplication by description
    const deduplicatedExamples: CounterExample[] = [];
    const descriptions = new Set<string>();
    
    for (const example of counterExamples) {
      if (!descriptions.has(example.description)) {
        descriptions.add(example.description);
        deduplicatedExamples.push(example);
      }
    }
    
    return deduplicatedExamples;
  }
  
  /**
   * Calculates a cross-validation score based on successful methods.
   * 
   * @param methodResults Results from different verification methods
   * @param successfulMethods Methods that successfully verified the theorem
   * @returns Cross-validation score
   */
  private calculateCrossValidationScore(
    methodResults: Map<ProofMethodType, VerificationResult>,
    successfulMethods: ProofMethodType[]
  ): number {
    // Simple average of confidence scores from successful methods
    let totalConfidence = 0;
    for (const method of successfulMethods) {
      totalConfidence += methodResults.get(method)!.confidence;
    }
    
    return totalConfidence / successfulMethods.length;
  }
  
  /**
   * Generates recommendations based on verification results.
   * 
   * @param result Enhanced verification result
   * @param theorem The theorem being verified
   * @returns Recommendations
   */
  private generateRecommendations(
    result: EnhancedVerificationResult,
    theorem: EconomicTheorem
  ): {
    improvementSuggestions: string[];
    alternativeApproaches: string[];
    furtherResearch: string[];
  } {
    const improvementSuggestions: string[] = [];
    const alternativeApproaches: string[] = [];
    const furtherResearch: string[] = [];
    
    // Suggest improvements based on verification outcome
    if (!result.verified) {
      improvementSuggestions.push("Refine theorem statement to be more precise");
      improvementSuggestions.push("Consider adding additional assumptions");
      improvementSuggestions.push("Narrow the scope of the theorem");
    } else if (result.confidence < 0.8) {
      improvementSuggestions.push("Strengthen the theorem with more specific conditions");
      improvementSuggestions.push("Clarify relationships between variables");
    }
    
    // Suggest alternative approaches based on methods tried
    const allMethods = Object.values(ProofMethodType);
    const unusedMethods = allMethods.filter(m => !result.verificationProcess.attemptedMethods.includes(m));
    
    if (unusedMethods.length > 0) {
      for (const method of unusedMethods) {
        alternativeApproaches.push(`Try verification using ${method}`);
      }
    }
    
    // Suggest further research based on theorem complexity
    furtherResearch.push("Explore historical case studies that may validate the theorem");
    
    if (theorem.domain === 'Macroeconomics' || theorem.domain === 'Monetary_Economics') {
      furtherResearch.push("Investigate DSGE model simulations to test theorem predictions");
    }
    
    if (theorem.domain === 'Behavioral_Economics') {
      furtherResearch.push("Consider experimental validation of behavioral assumptions");
    }
    
    return {
      improvementSuggestions,
      alternativeApproaches,
      furtherResearch
    };
  }
  
  /**
   * Determines the preferred method based on theorem characteristics and options.
   * 
   * @param theorem The theorem to verify
   * @param preferredMethods User-preferred methods
   * @returns The preferred method
   */
  private determinePreferredMethod(
    theorem: EconomicTheorem,
    preferredMethods?: ProofMethodType[]
  ): ProofMethodType {
    // If user specified preferred methods, use the first one
    if (preferredMethods && preferredMethods.length > 0) {
      return preferredMethods[0];
    }
    
    // Analyze theorem
    const analysis = this.analyzeTheorem(theorem);
    
    // Choose method based on analysis
    if (analysis.empiricalNature > 0.6) {
      return ProofMethodType.HistoricalEvidence;
    }
    
    if (analysis.complexity > 0.7) {
      return ProofMethodType.HybridApproach;
    }
    
    if (analysis.formalStructure > 0.6) {
      return ProofMethodType.DirectProof;
    }
    
    // Default to model checking for moderate complexity
    return ProofMethodType.ModelChecking;
  }
  
  /**
   * Gets appropriate verification methods based on the verification level.
   * 
   * @param level The verification level
   * @param preferredMethods User-preferred methods
   * @returns Array of verification methods to try
   */
  private getMethodsForLevel(
    level: VerificationLevel,
    preferredMethods?: ProofMethodType[]
  ): ProofMethodType[] {
    // If user specified preferred methods, respect that order
    if (preferredMethods && preferredMethods.length > 0) {
      // For higher levels, add more methods
      if (level === VerificationLevel.Rigorous || level === VerificationLevel.Exhaustive) {
        return [...preferredMethods, ...Object.values(ProofMethodType)
          .filter(m => !preferredMethods.includes(m))];
      }
      
      return preferredMethods;
    }
    
    // Default method ordering by level
    switch (level) {
      case VerificationLevel.Basic:
        return [ProofMethodType.DirectProof];
      
      case VerificationLevel.Standard:
        return [
          ProofMethodType.DirectProof,
          ProofMethodType.ModelChecking,
          ProofMethodType.HistoricalEvidence
        ];
      
      case VerificationLevel.Rigorous:
        return [
          ProofMethodType.DirectProof,
          ProofMethodType.Contradiction,
          ProofMethodType.ModelChecking,
          ProofMethodType.HistoricalEvidence,
          ProofMethodType.HybridApproach
        ];
      
      case VerificationLevel.Exhaustive:
        return Object.values(ProofMethodType);
      
      default:
        return [ProofMethodType.DirectProof, ProofMethodType.ModelChecking];
    }
  }
  
  /**
   * Generates a cache key for a theorem and verification options.
   * 
   * @param theorem The theorem
   * @param strategy The verification strategy
   * @param level The verification level
   * @returns Cache key
   */
  private generateCacheKey(
    theorem: EconomicTheorem,
    strategy: VerificationStrategy,
    level: VerificationLevel
  ): string {
    return `${theorem.name}_${strategy}_${level}`;
  }
  
  /**
   * Gets verification metrics and statistics.
   * 
   * @returns Verification statistics
   */
  getVerificationStatistics(): {
    totalVerifications: number;
    successRate: number;
    averageConfidence: number;
    methodSuccessRates: Record<ProofMethodType, number>;
    domainSuccessRates: Record<string, number>;
  } {
    // Count total verifications
    const totalVerifications = this.verificationCache.size;
    
    // Calculate success rate and average confidence
    let successCount = 0;
    let totalConfidence = 0;
    
    // Method and domain tracking
    const methodSuccess = new Map<ProofMethodType, { success: number; total: number }>();
    const domainSuccess = new Map<string, { success: number; total: number }>();
    
    // Process all cached verifications
    for (const result of this.verificationCache.values()) {
      if (result.verified) {
        successCount++;
      }
      
      totalConfidence += result.confidence;
      
      // Track method success
      const method = result.primaryMethod;
      if (!methodSuccess.has(method)) {
        methodSuccess.set(method, { success: 0, total: 0 });
      }
      const methodStats = methodSuccess.get(method)!;
      methodStats.total++;
      if (result.verified) {
        methodStats.success++;
      }
      
      // Track domain success
      const domain = result.theoremName.split('_').pop() || 'unknown';
      if (!domainSuccess.has(domain)) {
        domainSuccess.set(domain, { success: 0, total: 0 });
      }
      const domainStats = domainSuccess.get(domain)!;
      domainStats.total++;
      if (result.verified) {
        domainStats.success++;
      }
    }
    
    // Calculate method success rates
    const methodSuccessRates: Record<ProofMethodType, number> = {} as Record<ProofMethodType, number>;
    for (const [method, stats] of methodSuccess.entries()) {
      methodSuccessRates[method] = stats.total > 0 ? stats.success / stats.total : 0;
    }
    
    // Calculate domain success rates
    const domainSuccessRates: Record<string, number> = {};
    for (const [domain, stats] of domainSuccess.entries()) {
      domainSuccessRates[domain] = stats.total > 0 ? stats.success / stats.total : 0;
    }
    
    return {
      totalVerifications,
      successRate: totalVerifications > 0 ? successCount / totalVerifications : 0,
      averageConfidence: totalVerifications > 0 ? totalConfidence / totalVerifications : 0,
      methodSuccessRates,
      domainSuccessRates
    };
  }
  
  /**
   * Clears the verification cache.
   */
  clearCache(): void {
    console.log('Clearing verification cache...');
    this.verificationCache.clear();
    console.log('Verification cache cleared');
  }
}