// Core genetic algorithm types
export interface Solution {
  genes: string[];
  fitness: number;
}

export type Population = Solution[];

export interface EvolutionMetrics {
  generation: number;
  bestFitness: number;
  averageFitness: number;
  worstFitness: number;
  populationSize: number;
  uniqueSolutionsCount: number;
  diversityScore: number;
  convergenceRate: number;
  generationsSinceImprovement: number;
}

export interface GeneticAlgorithmOptions {
  fitnessFunction: (solution: Solution) => number | Promise<number>;
  selectionStrategy: 'tournament' | 'roulette' | 'rank' | 'steady-state';
  crossoverRate: number;
  mutationRate: number;
  populationSize: number;
  elitismCount: number;
  maxGenerations: number;
  targetFitness: number;
  genePool?: string[];
  tournamentSize?: number;
  adaptiveParameters?: boolean;
}

export interface EvolutionOptions {
  generations?: number;
  progressCallback?: (metrics: EvolutionMetrics) => void;
}

export interface EvolutionResult {
  population: Population;
  generation: number;
  metrics: EvolutionMetrics;
}

export type OperatorType = 'selection' | 'crossover' | 'mutation';

export interface GeneticOperationStats {
  operatorType: OperatorType;
  operatorName: string;
  applyCount: number;
  successCount: number;
  fitnessImprovement: number;
}

// Recursive thinking types
export interface ThinkingStep {
  description: string;
  input: string;
  output: string;
  tokens: number;
  executionTime: number;
}

export interface RecursiveThinkingStats {
  input: string;
  steps: ThinkingStep[];
  totalTokens: number;
  executionTime: number;
  improvementScore: number;
}

export interface RefinementOptions {
  steps?: number;
  temperature?: number;
  constraintsEnabled?: boolean;
}

// Knowledge integration types
export interface Constraint {
  type: string;
  value: any;
  description?: string;
  severity: 'fatal' | 'warning' | 'suggestion';
}

export interface Fact {
  description: string;
  weight: number;
  keyGenes?: string[];
  conditions?: FactCondition[];
}

export interface FactCondition {
  type: 'presence' | 'absence' | 'position' | 'order';
  value: any;
}

export interface Pattern {
  pattern: string[];
  weight: number;
  description?: string;
  context?: PatternContext;
}

export interface PatternContext {
  preceding?: string[];
  following?: string[];
  position?: 'start' | 'middle' | 'end' | 'any';
}

export interface KnowledgeDomain {
  constraints: Constraint[];
  facts: Fact[];
  patterns: Pattern[];
  metadata: DomainMetadata;
}

export interface DomainMetadata {
  name: string;
  description: string;
  keywords: string[];
  version: string;
  lastUpdated: string;
  compatibility: string[];
}

export interface ConstraintResult {
  isValid: boolean;
  failedConstraints: Constraint[];
}

export interface DomainWeight {
  domainName: string;
  weight: number;
}

// Adaptive parameter system types
export * from './adaptive_types';

// WebSocket communication types
export interface WebSocketMessage {
  type: string;
  requestId?: string;
  timestamp: string;
  data?: any;
}

export type ResponseHandler = (response: any) => void;
export type ErrorHandler = (error: any) => void;

// Advanced operators types
export interface SelectionOperators {
  tournamentSelection: (population: Population, count: number, tournamentSize: number) => Solution[];
  rouletteWheelSelection: (population: Population, count: number) => Solution[];
  rankSelection: (population: Population, count: number) => Solution[];
  steadyStateSelection: (population: Population, count: number) => Solution[];
  elitism: (population: Population, count: number) => Solution[];
}

export interface CrossoverOperators {
  singlePointCrossover: (parent1: Solution, parent2: Solution) => [Solution, Solution];
  multiPointCrossover: (parent1: Solution, parent2: Solution, numPoints?: number) => [Solution, Solution];
  uniformCrossover: (parent1: Solution, parent2: Solution, swapProbability?: number) => [Solution, Solution];
  arithmeticCrossover: (parent1: Solution, parent2: Solution) => [Solution, Solution];
  semanticAwareCrossover: (
    parent1: Solution, 
    parent2: Solution, 
    semanticSimilarity: (gene1: string, gene2: string) => number
  ) => [Solution, Solution];
}

export interface MutationOperators {
  pointMutation: (solution: Solution, genePool: string[]) => Solution;
  swapMutation: (solution: Solution) => Solution;
  insertMutation: (solution: Solution, genePool: string[]) => Solution;
  deleteMutation: (solution: Solution) => Solution;
  scrambleMutation: (solution: Solution) => Solution;
  patternBasedMutation: (solution: Solution, patterns: Pattern[]) => Solution;
}