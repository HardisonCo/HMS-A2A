/**
 * Knowledge Types
 * 
 * Defines the types and interfaces for the knowledge base system.
 */

/**
 * Enumeration of knowledge query types.
 */
export enum QueryType {
  Concept = 'concept',
  Fact = 'fact',
  Rule = 'rule',
  Procedure = 'procedure',
  Model = 'model',
  Resource = 'resource'
}

/**
 * Enumeration of rule types.
 */
export enum RuleType {
  Inference = 'inference',
  Constraint = 'constraint',
  Action = 'action'
}

/**
 * Enumeration of procedure types.
 */
export enum ProcedureType {
  Workflow = 'workflow',
  Protocol = 'protocol',
  DecisionTree = 'decision_tree'
}

/**
 * Enumeration of model types.
 */
export enum ModelType {
  Embedding = 'embedding',
  Classifier = 'classifier',
  Generator = 'generator'
}

/**
 * Interface for concept query.
 */
export interface ConceptQuery {
  type: QueryType.Concept;
  id: string;
}

/**
 * Interface for fact query.
 */
export interface FactQuery {
  type: QueryType.Fact;
  id: string;
  domain?: string;
}

/**
 * Interface for rule query.
 */
export interface RuleQuery {
  type: QueryType.Rule;
  id: string;
  ruleType?: RuleType;
}

/**
 * Interface for procedure query.
 */
export interface ProcedureQuery {
  type: QueryType.Procedure;
  id: string;
  procedureType?: ProcedureType;
}

/**
 * Interface for model query.
 */
export interface ModelQuery {
  type: QueryType.Model;
  id: string;
  modelType?: ModelType;
}

/**
 * Interface for resource query.
 */
export interface ResourceQuery {
  type: QueryType.Resource;
  id: string;
  resourceType?: string;
}

/**
 * Union type for all knowledge queries.
 */
export type KnowledgeQuery = 
  | ConceptQuery
  | FactQuery
  | RuleQuery
  | ProcedureQuery
  | ModelQuery
  | ResourceQuery;

/**
 * Interface for concept result.
 */
export interface ConceptResult {
  id: string;
  properties: Record<string, any>;
  relationships?: Array<{
    id: string;
    target: string;
    properties: Record<string, any>;
  }>;
}

/**
 * Interface for fact result.
 */
export interface FactResult {
  id: string;
  domain?: string;
  content: string;
  confidence?: number;
  source?: string;
}

/**
 * Interface for rule result.
 */
export interface RuleResult {
  id: string;
  ruleType: RuleType;
  condition: string;
  conclusion?: string;
  action?: string;
  parameters?: Record<string, any>;
}

/**
 * Interface for procedure result.
 */
export interface ProcedureResult {
  id: string;
  procedureType: ProcedureType;
  steps: Array<{
    id: string;
    action: string;
    parameters: Record<string, any>;
    nextStep?: string;
  }>;
}

/**
 * Interface for model result.
 */
export interface ModelResult {
  id: string;
  modelType: ModelType;
  version: string;
  features: string[];
  output: string;
  parameters?: Record<string, any>;
}

/**
 * Interface for resource result.
 */
export interface ResourceResult {
  id: string;
  resourceType: string;
  endpoint: string;
  methods: string[];
  authType?: string;
}

/**
 * Union type for all knowledge results.
 */
export type KnowledgeResult = 
  | ConceptResult
  | FactResult
  | RuleResult
  | ProcedureResult
  | ModelResult
  | ResourceResult;