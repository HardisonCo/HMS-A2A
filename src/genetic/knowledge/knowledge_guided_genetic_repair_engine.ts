/**
 * Knowledge-Guided Genetic Repair Engine
 * 
 * Extends the genetic repair engine with knowledge base integration
 * for domain-specific guidance.
 */

import { EnhancedHybridGeneticRepairEngine, EnhancedHybridGeneticSolution, HybridEngineConfig } from '../enhanced_hybrid_genetic_repair_engine';
import { GeneticConstraint, FitnessFunction } from '../genetic_repair_engine';
import { GeneticKnowledgeIntegration, KnowledgeDomain } from './knowledge_integration';

/**
 * Configuration for knowledge-guided genetic repair engine
 */
export interface KnowledgeGuidedConfig extends HybridEngineConfig {
  knowledgeBasePath?: string;
  domains?: KnowledgeDomain[];
  applyKnowledgeToFitness?: boolean;
  applyKnowledgeToMutation?: boolean;
}

/**
 * Extended solution with knowledge insights
 */
export interface KnowledgeGuidedSolution extends EnhancedHybridGeneticSolution {
  knowledgeDomains: KnowledgeDomain[];
  constraintMatches: number;
  fitnessBoosts: number;
  domainGuidanceStrength: number;
}

/**
 * Knowledge-guided genetic repair engine with domain-specific knowledge
 * integration for improved performance.
 */
export class KnowledgeGuidedGeneticRepairEngine extends EnhancedHybridGeneticRepairEngine {
  private knowledgeIntegration: GeneticKnowledgeIntegration;
  private domains: KnowledgeDomain[] = [];
  private applyKnowledgeToFitness: boolean = true;
  private applyKnowledgeToMutation: boolean = true;
  private isKnowledgeInitialized: boolean = false;
  
  /**
   * Initialize the knowledge-guided genetic repair engine
   */
  async initialize(config?: KnowledgeGuidedConfig): Promise<void> {
    // Initialize the base hybrid engine
    await super.initialize(config);
    
    if (this.isKnowledgeInitialized) return;
    
    console.log('Initializing Knowledge-Guided Genetic Repair Engine');
    
    // Set configuration
    if (config) {
      if (config.domains) {
        this.domains = config.domains;
      }
      if (config.applyKnowledgeToFitness !== undefined) {
        this.applyKnowledgeToFitness = config.applyKnowledgeToFitness;
      }
      if (config.applyKnowledgeToMutation !== undefined) {
        this.applyKnowledgeToMutation = config.applyKnowledgeToMutation;
      }
    }
    
    // Default to all domains if none specified
    if (this.domains.length === 0) {
      this.domains = Object.values(KnowledgeDomain);
    }
    
    // Initialize knowledge integration
    this.knowledgeIntegration = new GeneticKnowledgeIntegration(
      config?.knowledgeBasePath
    );
    await this.knowledgeIntegration.initialize();
    
    this.isKnowledgeInitialized = true;
    console.log('Knowledge-Guided Genetic Repair Engine initialized successfully');
    console.log(`Active knowledge domains: ${this.domains.join(', ')}`);
  }
  
  /**
   * Evolve a solution using the knowledge-guided approach
   */
  async knowledgeGuidedEvolve(
    candidateSolutions: string[],
    constraints: GeneticConstraint[] = [],
    fitnessFunction: FitnessFunction,
    problemDescription?: string
  ): Promise<KnowledgeGuidedSolution> {
    if (!this.isKnowledgeInitialized) {
      await this.initialize();
    }
    
    console.log(`Starting knowledge-guided evolution with ${candidateSolutions.length} initial candidates`);
    
    // Select relevant domains based on problem description if provided
    let relevantDomains = this.domains;
    if (problemDescription) {
      relevantDomains = this.selectRelevantDomains(problemDescription);
      console.log(`Selected relevant domains based on problem description: ${relevantDomains.join(', ')}`);
    }
    
    // Add knowledge-based constraints
    const knowledgeConstraints: GeneticConstraint[] = [];
    let constraintMatches = 0;
    
    for (const domain of relevantDomains) {
      const domainConstraints = this.knowledgeIntegration.getConstraints(domain);
      knowledgeConstraints.push(...domainConstraints);
    }
    
    // Merge user-provided and knowledge-based constraints
    const combinedConstraints = [...constraints];
    
    // Add only unique knowledge constraints
    for (const knowledgeConstraint of knowledgeConstraints) {
      const exists = combinedConstraints.some(c => 
        c.type === knowledgeConstraint.type && 
        c.value === knowledgeConstraint.value
      );
      
      if (!exists) {
        combinedConstraints.push(knowledgeConstraint);
        constraintMatches++;
      }
    }
    
    console.log(`Added ${constraintMatches} knowledge-based constraints`);
    
    // Create knowledge-enhanced fitness function
    const knowledgeEnhancedFitness = this.createKnowledgeEnhancedFitnessFunction(
      fitnessFunction,
      relevantDomains
    );
    
    // Run hybrid evolution with knowledge enhancement
    const hybridSolution = await super.enhancedEvolve(
      candidateSolutions,
      combinedConstraints,
      knowledgeEnhancedFitness
    );
    
    // Calculate domain guidance strength
    const domainGuidanceStrength = constraintMatches > 0 ? 
      (constraintMatches / (constraints.length + constraintMatches)) : 0;
    
    // Return knowledge-guided solution
    return {
      ...hybridSolution,
      knowledgeDomains: relevantDomains,
      constraintMatches,
      fitnessBoosts: this.fitnessBoosts,
      domainGuidanceStrength
    };
  }
  
  /**
   * Number of fitness boosts applied
   */
  private fitnessBoosts: number = 0;
  
  /**
   * Create a knowledge-enhanced fitness function
   * @param baseFitnessFunction Base fitness function
   * @param relevantDomains Relevant knowledge domains
   * @returns Enhanced fitness function
   */
  private createKnowledgeEnhancedFitnessFunction(
    baseFitnessFunction: FitnessFunction,
    relevantDomains: KnowledgeDomain[]
  ): FitnessFunction {
    // Reset fitness boosts counter
    this.fitnessBoosts = 0;
    
    return async (solution: string): Promise<number> => {
      // Calculate base fitness
      const baseFitness = await baseFitnessFunction(solution);
      
      // Apply knowledge-guided fitness boost if enabled
      if (this.applyKnowledgeToFitness) {
        let enhancedFitness = baseFitness;
        
        for (const domain of relevantDomains) {
          const boostedFitness = this.knowledgeIntegration.applyKnowledgeGuidedFitnessBoost(
            solution,
            enhancedFitness,
            domain
          );
          
          if (boostedFitness > enhancedFitness) {
            this.fitnessBoosts++;
            enhancedFitness = boostedFitness;
          }
        }
        
        return enhancedFitness;
      }
      
      return baseFitness;
    };
  }
  
  /**
   * Override the mutateSolution method to use knowledge-guided mutation
   * @param solution Solution to mutate
   * @returns Mutated solution
   */
  protected mutateSolution(solution: string): string {
    // Apply base mutation
    let mutatedSolution = super.mutateSolution(solution);
    
    // Apply knowledge-guided mutation if enabled
    if (this.isKnowledgeInitialized && this.applyKnowledgeToMutation) {
      for (const domain of this.domains) {
        mutatedSolution = this.knowledgeIntegration.applyKnowledgeGuidedMutation(
          mutatedSolution,
          domain
        );
      }
    }
    
    return mutatedSolution;
  }
  
  /**
   * Select relevant domains based on problem description
   * @param problemDescription Problem description
   * @returns List of relevant domains
   */
  private selectRelevantDomains(problemDescription: string): KnowledgeDomain[] {
    const relevantDomains: KnowledgeDomain[] = [];
    const lowerCaseDescription = problemDescription.toLowerCase();
    
    // Check for keywords related to each domain
    const domainKeywords: Record<KnowledgeDomain, string[]> = {
      [KnowledgeDomain.Error]: ['error', 'exception', 'crash', 'bug', 'fail', 'fix'],
      [KnowledgeDomain.Performance]: ['performance', 'slow', 'speed', 'optimization', 'efficient', 'faster'],
      [KnowledgeDomain.Security]: ['security', 'vulnerability', 'attack', 'secure', 'protect', 'auth'],
      [KnowledgeDomain.Code]: ['code', 'quality', 'refactor', 'clean', 'maintainable', 'readable'],
      [KnowledgeDomain.Architecture]: ['architecture', 'design', 'structure', 'pattern', 'component'],
      [KnowledgeDomain.Testing]: ['test', 'validation', 'verify', 'assert', 'check', 'coverage'],
    };
    
    // Add domains with matching keywords
    for (const [domain, keywords] of Object.entries(domainKeywords)) {
      for (const keyword of keywords) {
        if (lowerCaseDescription.includes(keyword)) {
          relevantDomains.push(domain as KnowledgeDomain);
          break;
        }
      }
    }
    
    // If no relevant domains found, return all domains
    if (relevantDomains.length === 0) {
      return this.domains;
    }
    
    return relevantDomains;
  }
}