import { EvolutionMetrics, GeneticOperationStats, OperatorType } from './index';

/**
 * Context provided to parameter adjustment strategies
 */
export interface AdaptiveStrategyContext {
  /** Current evolution metrics */
  metrics: EvolutionMetrics;
  
  /** History of evolution metrics */
  metricHistory: EvolutionMetrics[];
  
  /** History of operation statistics */
  operationHistory: GeneticOperationStats[];
  
  /** Statistics for each operator type */
  operatorStats: Record<OperatorType, { 
    successRate: number; 
    improvementRate: number;
  }>;
  
  /** Population diversity score (0-1) */
  diversity: number;
  
  /** Convergence rate (0-1) */
  convergence: number;
  
  /** Generations since last improvement */
  stagnation: number;
}

/**
 * Function type for parameter adjustment strategies
 * @param currentValue Current parameter value
 * @param context Context information for adjustment
 * @returns New parameter value
 */
export type ParameterAdjustmentStrategy = (
  currentValue: number, 
  context: AdaptiveStrategyContext
) => number;

/**
 * Configuration for an adaptive parameter
 */
export interface AdaptiveParameterConfig {
  /** Parameter name */
  name: string;
  
  /** Default parameter value */
  defaultValue: number;
  
  /** Minimum allowed value */
  min: number;
  
  /** Maximum allowed value */
  max: number;
  
  /** Adjustment strategy */
  adjustmentStrategy: ParameterAdjustmentStrategy;
}

/**
 * Configuration for the adaptive parameter system
 */
export interface AdaptiveSystemConfig {
  /** Initial parameters configuration */
  parameters: AdaptiveParameterConfig[];
  
  /** Maximum history length to track */
  historyLimit?: number;
  
  /** Whether to enable self-tuning of parameters */
  enableSelfTuning?: boolean;
  
  /** Update frequency (updates per generation) */
  updateFrequency?: number;
}

/**
 * Snapshot of all adaptive parameters
 */
export interface ParameterSnapshot {
  /** Parameter values */
  parameters: Record<string, number>;
  
  /** Metrics at the time of snapshot */
  metrics?: EvolutionMetrics;
  
  /** Timestamp when snapshot was taken */
  timestamp: number;
  
  /** Generation of snapshot */
  generation: number;
}

/**
 * Configuration for adaptive operator selection
 */
export interface AdaptiveOperatorConfig {
  /** Operator name */
  name: string;
  
  /** Operator type */
  type: OperatorType;
  
  /** Initial selection probability */
  initialProbability: number;
  
  /** Minimum selection probability */
  minProbability: number;
  
  /** Maximum selection probability */
  maxProbability: number;
}

/**
 * Configuration for different operator selection methods
 */
export interface OperatorSelectionConfig {
  /** Method for selecting operators */
  method: 'probability' | 'roulette' | 'adaptive';
  
  /** Credit assignment mechanism */
  creditAssignment: 'improvement' | 'fitness' | 'pareto';
  
  /** Update frequency */
  updateFrequency: number;
  
  /** Learning rate for probability updates */
  learningRate: number;
}

/**
 * Controls for the adaptive parameter system
 */
export interface AdaptiveControls {
  /** Whether the adaptive system is enabled */
  enabled: boolean;
  
  /** Whether parameter snapshots are taken */
  snapshotsEnabled: boolean;
  
  /** Whether system events are logged */
  loggingEnabled: boolean;
  
  /** Level of parameter adaptation */
  adaptationLevel: 'none' | 'basic' | 'advanced' | 'experimental';
}

/**
 * Parameter adaptation event
 */
export interface ParameterAdaptationEvent {
  /** Parameter name */
  parameter: string;
  
  /** Old parameter value */
  oldValue: number;
  
  /** New parameter value */
  newValue: number;
  
  /** Reason for adjustment */
  reason: string;
  
  /** Metrics that influenced change */
  metrics: Partial<EvolutionMetrics>;
  
  /** Generation when adjustment occurred */
  generation: number;
  
  /** Timestamp of adjustment */
  timestamp: number;
}