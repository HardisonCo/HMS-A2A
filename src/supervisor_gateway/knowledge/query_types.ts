/**
 * Query Types
 * 
 * This file defines common query types used by knowledge components
 * such as the Knowledge Graph, Domain Ontology, and Expert System.
 */

/**
 * Graph Query for Knowledge Graph
 */
export interface GraphQuery {
  type: 'node' | 'path' | 'pattern' | 'natural';
  content: {
    // Node query
    id?: string;
    type?: string;
    label?: string;
    filters?: Record<string, any>;
    include_edges?: boolean;
    
    // Path query
    source?: string;
    target?: string;
    max_depth?: number;
    edge_types?: string[];
    
    // Pattern query
    pattern?: string;
    
    // Natural language query
    question?: string;
  };
  limit?: number;
  offset?: number;
  order_by?: string;
  direction?: 'asc' | 'desc';
  include_metadata?: boolean;
}

/**
 * Ontology Query for Domain Ontology
 */
export interface OntologyQuery {
  type: 'concept' | 'relationship' | 'axiom' | 'natural';
  content: {
    // Concept query
    id?: string;
    name?: string;
    parent_concept?: string;
    include_relationships?: boolean;
    
    // Relationship query
    type?: string;
    concept?: string;
    include_concepts?: boolean;
    
    // Axiom query
    concept_id?: string;
    include_related?: boolean;
    
    // Natural language query
    question?: string;
  };
  limit?: number;
  offset?: number;
}

/**
 * Expert Query for Expert System
 */
export interface ExpertQuery {
  type: 'question' | 'problem' | 'recommendation' | 'natural';
  content: {
    // Question query
    question?: string;
    
    // Problem query
    problem?: string;
    context?: Record<string, any>;
    
    // Recommendation query
    situation?: string;
    parameters?: Record<string, any>;
    
    // Natural language query
    text?: string;
  };
  context?: Record<string, any>;
}