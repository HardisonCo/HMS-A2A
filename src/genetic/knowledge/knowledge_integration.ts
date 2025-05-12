/**
 * Knowledge Integration for Genetic Algorithms
 * 
 * This module integrates the knowledge base system with genetic algorithms
 * to provide domain-specific guidance for solution generation and evaluation.
 */

import * as path from 'path';
import * as fs from 'fs/promises';
import { KnowledgeBaseManager } from '../../supervisor_gateway/knowledge/knowledge_base_manager';
import { QueryType, RuleType, ProcedureType } from '../../supervisor_gateway/knowledge/knowledge_types';
import { GeneticConstraint } from '../genetic_repair_engine';

/**
 * Domain type for knowledge guidance
 */
export enum KnowledgeDomain {
  Error = 'error_handling',
  Performance = 'performance_optimization',
  Security = 'security',
  Code = 'code_quality',
  Architecture = 'architecture',
  Testing = 'testing',
}

/**
 * Type of knowledge to apply
 */
export enum KnowledgeApplier {
  Constraints = 'constraints',
  Initialization = 'initialization',
  Mutation = 'mutation',
  Crossover = 'crossover',
  FitnessBoost = 'fitness_boost',
}

/**
 * Knowledge constraint
 */
export interface KnowledgeConstraint {
  id: string;
  domain: KnowledgeDomain;
  type: 'must_contain' | 'must_not_contain' | 'min_length' | 'max_length';
  value: string | number;
  priority: number;
  description?: string;
}

/**
 * Knowledge pattern for genetic operations
 */
export interface KnowledgePattern {
  id: string;
  domain: KnowledgeDomain;
  applier: KnowledgeApplier;
  pattern: string | RegExp;
  replacement?: string;
  weight: number;
  description?: string;
}

/**
 * Knowledge guidance for genetic algorithms
 */
export interface KnowledgeGuidance {
  constraints: KnowledgeConstraint[];
  patterns: KnowledgePattern[];
  fitness_weights: Record<string, number>;
  mutation_weights: Record<string, number>;
  crossover_weights: Record<string, number>;
}

/**
 * Knowledge integration for genetic algorithms
 */
export class GeneticKnowledgeIntegration {
  private knowledgeBaseManager: KnowledgeBaseManager;
  private domainGuidance: Map<KnowledgeDomain, KnowledgeGuidance>;
  private isInitialized: boolean = false;
  
  /**
   * Constructor
   * @param knowledgeBasePath Path to the knowledge base
   */
  constructor(knowledgeBasePath: string = '../../../knowledge_store') {
    this.knowledgeBaseManager = new KnowledgeBaseManager(knowledgeBasePath);
    this.domainGuidance = new Map<KnowledgeDomain, KnowledgeGuidance>();
  }
  
  /**
   * Initialize knowledge integration
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    console.log('Initializing genetic knowledge integration');
    
    // Load knowledge for each domain
    for (const domain of Object.values(KnowledgeDomain)) {
      await this.loadDomainKnowledge(domain);
    }
    
    this.isInitialized = true;
    console.log('Genetic knowledge integration initialized successfully');
  }
  
  /**
   * Load domain-specific knowledge
   * @param domain Knowledge domain
   */
  private async loadDomainKnowledge(domain: KnowledgeDomain): Promise<void> {
    try {
      console.log(`Loading knowledge for domain: ${domain}`);
      
      // Initialize empty guidance
      const guidance: KnowledgeGuidance = {
        constraints: [],
        patterns: [],
        fitness_weights: {},
        mutation_weights: {},
        crossover_weights: {},
      };
      
      // Load constraints from rules
      const constraintRules = await this.loadRules(domain, RuleType.Constraint);
      for (const rule of constraintRules) {
        const constraint = this.convertRuleToConstraint(rule, domain);
        if (constraint) {
          guidance.constraints.push(constraint);
        }
      }
      
      // Load patterns from facts
      const domainFacts = await this.loadFacts(domain);
      for (const fact of domainFacts) {
        const pattern = this.convertFactToPattern(fact, domain);
        if (pattern) {
          guidance.patterns.push(pattern);
        }
      }
      
      // Load weights from models
      const weights = await this.loadWeights(domain);
      guidance.fitness_weights = weights.fitness_weights || {};
      guidance.mutation_weights = weights.mutation_weights || {};
      guidance.crossover_weights = weights.crossover_weights || {};
      
      // Store guidance
      this.domainGuidance.set(domain, guidance);
      
      console.log(`Loaded knowledge for domain ${domain}: ${guidance.constraints.length} constraints, ${guidance.patterns.length} patterns`);
      
    } catch (error) {
      console.error(`Error loading knowledge for domain ${domain}:`, error);
      // Create empty guidance as fallback
      this.domainGuidance.set(domain, {
        constraints: [],
        patterns: [],
        fitness_weights: {},
        mutation_weights: {},
        crossover_weights: {},
      });
    }
  }
  
  /**
   * Load rules from knowledge base
   * @param domain Knowledge domain
   * @param ruleType Rule type
   * @returns List of rules
   */
  private async loadRules(domain: KnowledgeDomain, ruleType: RuleType): Promise<any[]> {
    try {
      // First, try to query from the knowledge base manager
      const rules = [];
      const knowledgeBase = await this.knowledgeBaseManager.loadKnowledgeBase('genetic_engine');
      
      if (knowledgeBase && knowledgeBase.rules && knowledgeBase.rules[`${ruleType}_rules`]) {
        const domainRules = knowledgeBase.rules[`${ruleType}_rules`].filter(
          (rule: any) => rule.domain === domain
        );
        rules.push(...domainRules);
      }
      
      // If no rules found, try to load from file
      if (rules.length === 0) {
        const rulesFile = path.join(
          __dirname,
          '../../../knowledge_store/entities',
          `genetic_${domain}_${ruleType}_rules.json`
        );
        
        try {
          const fileContent = await fs.readFile(rulesFile, 'utf-8');
          const fileRules = JSON.parse(fileContent);
          if (Array.isArray(fileRules)) {
            rules.push(...fileRules);
          } else if (fileRules.properties && fileRules.properties.rules) {
            rules.push(...fileRules.properties.rules);
          }
        } catch (fileError) {
          // File not found, that's ok
        }
      }
      
      return rules;
    } catch (error) {
      console.error(`Error loading rules for domain ${domain}:`, error);
      return [];
    }
  }
  
  /**
   * Load facts from knowledge base
   * @param domain Knowledge domain
   * @returns List of facts
   */
  private async loadFacts(domain: KnowledgeDomain): Promise<any[]> {
    try {
      // First, try to query from the knowledge base manager
      const facts = [];
      const knowledgeBase = await this.knowledgeBaseManager.loadKnowledgeBase('genetic_engine');
      
      if (knowledgeBase && knowledgeBase.facts && knowledgeBase.facts.domain_facts) {
        const domainFacts = knowledgeBase.facts.domain_facts.filter(
          (fact: any) => fact.domain === domain
        );
        facts.push(...domainFacts);
      }
      
      // If no facts found, try to load from file
      if (facts.length === 0) {
        const factsFile = path.join(
          __dirname,
          '../../../knowledge_store/entities',
          `genetic_${domain}_facts.json`
        );
        
        try {
          const fileContent = await fs.readFile(factsFile, 'utf-8');
          const fileFacts = JSON.parse(fileContent);
          if (Array.isArray(fileFacts)) {
            facts.push(...fileFacts);
          } else if (fileFacts.properties && fileFacts.properties.facts) {
            facts.push(...fileFacts.properties.facts);
          }
        } catch (fileError) {
          // File not found, that's ok
        }
      }
      
      return facts;
    } catch (error) {
      console.error(`Error loading facts for domain ${domain}:`, error);
      return [];
    }
  }
  
  /**
   * Load weights from knowledge base
   * @param domain Knowledge domain
   * @returns Weights for genetic operations
   */
  private async loadWeights(domain: KnowledgeDomain): Promise<any> {
    try {
      // First, try to query from the knowledge base manager
      const knowledgeBase = await this.knowledgeBaseManager.loadKnowledgeBase('genetic_engine');
      
      if (knowledgeBase && knowledgeBase.models && knowledgeBase.models.weights) {
        const domainWeights = knowledgeBase.models.weights[domain];
        if (domainWeights) {
          return domainWeights;
        }
      }
      
      // If no weights found, try to load from file
      const weightsFile = path.join(
        __dirname,
        '../../../knowledge_store/entities',
        `genetic_${domain}_weights.json`
      );
      
      try {
        const fileContent = await fs.readFile(weightsFile, 'utf-8');
        const fileWeights = JSON.parse(fileContent);
        if (fileWeights.properties && fileWeights.properties.weights) {
          return fileWeights.properties.weights;
        }
        return fileWeights;
      } catch (fileError) {
        // File not found, return default weights
        return {
          fitness_weights: {},
          mutation_weights: {},
          crossover_weights: {},
        };
      }
    } catch (error) {
      console.error(`Error loading weights for domain ${domain}:`, error);
      return {
        fitness_weights: {},
        mutation_weights: {},
        crossover_weights: {},
      };
    }
  }
  
  /**
   * Convert a rule to a constraint
   * @param rule Rule to convert
   * @param domain Knowledge domain
   * @returns Knowledge constraint
   */
  private convertRuleToConstraint(rule: any, domain: KnowledgeDomain): KnowledgeConstraint | null {
    try {
      if (!rule.condition || !rule.conclusion) {
        return null;
      }
      
      // Parse the condition to determine the constraint type
      let type: 'must_contain' | 'must_not_contain' | 'min_length' | 'max_length';
      let value: string | number;
      
      if (rule.condition.includes('contains')) {
        type = 'must_contain';
        value = this.extractValueFromCondition(rule.condition, 'contains');
      } else if (rule.condition.includes('does not contain')) {
        type = 'must_not_contain';
        value = this.extractValueFromCondition(rule.condition, 'does not contain');
      } else if (rule.condition.includes('length >=')) {
        type = 'min_length';
        value = parseInt(this.extractValueFromCondition(rule.condition, 'length >='));
      } else if (rule.condition.includes('length <=')) {
        type = 'max_length';
        value = parseInt(this.extractValueFromCondition(rule.condition, 'length <='));
      } else {
        return null;
      }
      
      return {
        id: rule.id || `constraint_${Math.random().toString(36).substring(2, 11)}`,
        domain,
        type,
        value,
        priority: rule.priority || 1,
        description: rule.conclusion,
      };
    } catch (error) {
      console.error('Error converting rule to constraint:', error);
      return null;
    }
  }
  
  /**
   * Extract value from a condition string
   * @param condition Condition string
   * @param keyword Keyword to search for
   * @returns Extracted value
   */
  private extractValueFromCondition(condition: string, keyword: string): string {
    const parts = condition.split(keyword);
    if (parts.length < 2) {
      return '';
    }
    
    const valuePart = parts[1].trim();
    if (valuePart.startsWith('"') && valuePart.includes('"', 1)) {
      return valuePart.substring(1, valuePart.indexOf('"', 1));
    } else if (valuePart.startsWith("'") && valuePart.includes("'", 1)) {
      return valuePart.substring(1, valuePart.indexOf("'", 1));
    } else {
      // For numeric values or unquoted strings
      return valuePart.split(' ')[0].trim().replace(/[.,;:]$/, '');
    }
  }
  
  /**
   * Convert a fact to a pattern
   * @param fact Fact to convert
   * @param domain Knowledge domain
   * @returns Knowledge pattern
   */
  private convertFactToPattern(fact: any, domain: KnowledgeDomain): KnowledgePattern | null {
    try {
      if (!fact.content || !fact.properties) {
        return null;
      }
      
      const applier = this.determineApplier(fact.properties.usage || '');
      if (!applier) {
        return null;
      }
      
      return {
        id: fact.id || `pattern_${Math.random().toString(36).substring(2, 11)}`,
        domain,
        applier,
        pattern: fact.properties.pattern || fact.content,
        replacement: fact.properties.replacement,
        weight: fact.properties.weight || 1,
        description: fact.properties.description || fact.content,
      };
    } catch (error) {
      console.error('Error converting fact to pattern:', error);
      return null;
    }
  }
  
  /**
   * Determine the applier type from a usage string
   * @param usage Usage string
   * @returns Applier type
   */
  private determineApplier(usage: string): KnowledgeApplier | null {
    if (usage.includes('constraint')) {
      return KnowledgeApplier.Constraints;
    } else if (usage.includes('initialization')) {
      return KnowledgeApplier.Initialization;
    } else if (usage.includes('mutation')) {
      return KnowledgeApplier.Mutation;
    } else if (usage.includes('crossover')) {
      return KnowledgeApplier.Crossover;
    } else if (usage.includes('fitness')) {
      return KnowledgeApplier.FitnessBoost;
    } else {
      return null;
    }
  }
  
  /**
   * Get domain-specific constraints
   * @param domain Knowledge domain
   * @returns List of genetic constraints
   */
  getConstraints(domain: KnowledgeDomain): GeneticConstraint[] {
    if (!this.isInitialized) {
      throw new Error('Knowledge integration not initialized');
    }
    
    const guidance = this.domainGuidance.get(domain);
    if (!guidance) {
      return [];
    }
    
    return guidance.constraints.map(constraint => ({
      type: constraint.type,
      value: constraint.value,
    }));
  }
  
  /**
   * Get mutation patterns for a domain
   * @param domain Knowledge domain
   * @returns List of mutation patterns
   */
  getMutationPatterns(domain: KnowledgeDomain): KnowledgePattern[] {
    if (!this.isInitialized) {
      throw new Error('Knowledge integration not initialized');
    }
    
    const guidance = this.domainGuidance.get(domain);
    if (!guidance) {
      return [];
    }
    
    return guidance.patterns.filter(pattern => 
      pattern.applier === KnowledgeApplier.Mutation
    );
  }
  
  /**
   * Get initialization patterns for a domain
   * @param domain Knowledge domain
   * @returns List of initialization patterns
   */
  getInitializationPatterns(domain: KnowledgeDomain): KnowledgePattern[] {
    if (!this.isInitialized) {
      throw new Error('Knowledge integration not initialized');
    }
    
    const guidance = this.domainGuidance.get(domain);
    if (!guidance) {
      return [];
    }
    
    return guidance.patterns.filter(pattern => 
      pattern.applier === KnowledgeApplier.Initialization
    );
  }
  
  /**
   * Get crossover patterns for a domain
   * @param domain Knowledge domain
   * @returns List of crossover patterns
   */
  getCrossoverPatterns(domain: KnowledgeDomain): KnowledgePattern[] {
    if (!this.isInitialized) {
      throw new Error('Knowledge integration not initialized');
    }
    
    const guidance = this.domainGuidance.get(domain);
    if (!guidance) {
      return [];
    }
    
    return guidance.patterns.filter(pattern => 
      pattern.applier === KnowledgeApplier.Crossover
    );
  }
  
  /**
   * Get fitness boost patterns for a domain
   * @param domain Knowledge domain
   * @returns List of fitness boost patterns
   */
  getFitnessBoostPatterns(domain: KnowledgeDomain): KnowledgePattern[] {
    if (!this.isInitialized) {
      throw new Error('Knowledge integration not initialized');
    }
    
    const guidance = this.domainGuidance.get(domain);
    if (!guidance) {
      return [];
    }
    
    return guidance.patterns.filter(pattern => 
      pattern.applier === KnowledgeApplier.FitnessBoost
    );
  }
  
  /**
   * Apply knowledge-guided mutation to a solution
   * @param solution Solution to mutate
   * @param domain Knowledge domain
   * @returns Mutated solution
   */
  applyKnowledgeGuidedMutation(solution: string, domain: KnowledgeDomain): string {
    if (!this.isInitialized) {
      throw new Error('Knowledge integration not initialized');
    }
    
    const patterns = this.getMutationPatterns(domain);
    if (patterns.length === 0) {
      return solution;
    }
    
    // Apply a random pattern based on weights
    const totalWeight = patterns.reduce((sum, pattern) => sum + pattern.weight, 0);
    let randomValue = Math.random() * totalWeight;
    let selectedPattern: KnowledgePattern | null = null;
    
    for (const pattern of patterns) {
      randomValue -= pattern.weight;
      if (randomValue <= 0) {
        selectedPattern = pattern;
        break;
      }
    }
    
    if (!selectedPattern) {
      return solution;
    }
    
    // Apply the pattern
    return this.applyPattern(solution, selectedPattern);
  }
  
  /**
   * Apply a pattern to a solution
   * @param solution Solution to modify
   * @param pattern Pattern to apply
   * @returns Modified solution
   */
  private applyPattern(solution: string, pattern: KnowledgePattern): string {
    try {
      const patternStr = pattern.pattern.toString();
      
      if (pattern.replacement) {
        // Simple string replacement
        if (typeof pattern.pattern === 'string') {
          return solution.replace(pattern.pattern, pattern.replacement);
        }
        
        // Regex replacement
        if (pattern.pattern instanceof RegExp) {
          return solution.replace(pattern.pattern, pattern.replacement);
        }
        
        // Try to convert string to regex
        try {
          const flags = patternStr.match(/\/([gimuy]*)$/)?.[1] || '';
          const regex = new RegExp(
            patternStr.replace(/^\//, '').replace(new RegExp(`/${flags}$`), ''),
            flags
          );
          return solution.replace(regex, pattern.replacement);
        } catch (error) {
          // Fallback to string replacement
          return solution.replace(patternStr, pattern.replacement);
        }
      } else {
        // No replacement, just return the original solution
        return solution;
      }
    } catch (error) {
      console.error('Error applying pattern:', error);
      return solution;
    }
  }
  
  /**
   * Apply knowledge guidance to improve fitness evaluation
   * @param solution Solution to evaluate
   * @param baseFitness Base fitness score
   * @param domain Knowledge domain
   * @returns Adjusted fitness score
   */
  applyKnowledgeGuidedFitnessBoost(
    solution: string,
    baseFitness: number,
    domain: KnowledgeDomain
  ): number {
    if (!this.isInitialized) {
      throw new Error('Knowledge integration not initialized');
    }
    
    const patterns = this.getFitnessBoostPatterns(domain);
    if (patterns.length === 0) {
      return baseFitness;
    }
    
    let fitnessBoost = 0;
    
    // Check each pattern and add boost if matched
    for (const pattern of patterns) {
      if (this.doesPatternMatch(solution, pattern)) {
        fitnessBoost += pattern.weight;
      }
    }
    
    // Apply boost with diminishing returns
    return baseFitness + (fitnessBoost / (10 + fitnessBoost));
  }
  
  /**
   * Check if a pattern matches a solution
   * @param solution Solution to check
   * @param pattern Pattern to match
   * @returns True if pattern matches
   */
  private doesPatternMatch(solution: string, pattern: KnowledgePattern): boolean {
    try {
      if (typeof pattern.pattern === 'string') {
        return solution.includes(pattern.pattern);
      }
      
      if (pattern.pattern instanceof RegExp) {
        return pattern.pattern.test(solution);
      }
      
      // Try to convert string to regex
      const patternStr = pattern.pattern.toString();
      try {
        const flags = patternStr.match(/\/([gimuy]*)$/)?.[1] || '';
        const regex = new RegExp(
          patternStr.replace(/^\//, '').replace(new RegExp(`/${flags}$`), ''),
          flags
        );
        return regex.test(solution);
      } catch (error) {
        // Fallback to string matching
        return solution.includes(patternStr);
      }
    } catch (error) {
      console.error('Error matching pattern:', error);
      return false;
    }
  }
}