/**
 * Knowledge Base Manager
 * 
 * Manages loading, querying, and updating knowledge bases for agents.
 */

import { AgentType } from '../communication/message';
import { KnowledgeQuery, KnowledgeResult, QueryType } from './knowledge_types';
import * as fs from 'fs/promises';
import * as path from 'path';

/**
 * Class that manages agent knowledge bases.
 */
export class KnowledgeBaseManager {
  private knowledgeBases: Map<string, any>;
  private knowledgeBasePath: string;
  
  /**
   * Creates a new KnowledgeBaseManager instance.
   * 
   * @param knowledgeBasePath Path to the knowledge base directory
   */
  constructor(knowledgeBasePath: string = '../../../agent_knowledge_base') {
    this.knowledgeBases = new Map<string, any>();
    this.knowledgeBasePath = knowledgeBasePath;
  }
  
  /**
   * Loads a knowledge base for an agent type.
   * 
   * @param agentType The agent type
   * @returns The loaded knowledge base
   */
  async loadKnowledgeBase(agentType: AgentType | string): Promise<any> {
    const agentTypeStr = typeof agentType === 'string' ? agentType : agentType.toString();
    
    // Check if already loaded
    if (this.knowledgeBases.has(agentTypeStr)) {
      return this.knowledgeBases.get(agentTypeStr);
    }
    
    try {
      // Construct file path
      const filename = `${this.getKnowledgeBaseFilename(agentTypeStr)}_kb.json`;
      const filePath = path.join(this.knowledgeBasePath, filename);
      
      // Load knowledge base from file
      const data = await fs.readFile(filePath, 'utf-8');
      const knowledgeBase = JSON.parse(data);
      
      // Store in memory
      this.knowledgeBases.set(agentTypeStr, knowledgeBase);
      
      console.log(`Loaded knowledge base for agent type: ${agentTypeStr}`);
      return knowledgeBase;
      
    } catch (error) {
      console.error(`Failed to load knowledge base for agent type: ${agentTypeStr}`, error);
      
      // Create an empty knowledge base as fallback
      const emptyKnowledgeBase = this.createEmptyKnowledgeBase(agentTypeStr);
      this.knowledgeBases.set(agentTypeStr, emptyKnowledgeBase);
      
      return emptyKnowledgeBase;
    }
  }
  
  /**
   * Queries a knowledge base for specific information.
   * 
   * @param agentType The agent type
   * @param query The knowledge query
   * @returns The query result
   */
  async queryKnowledgeBase(agentType: AgentType | string, query: KnowledgeQuery): Promise<KnowledgeResult> {
    const agentTypeStr = typeof agentType === 'string' ? agentType : agentType.toString();
    
    // Ensure knowledge base is loaded
    const knowledgeBase = await this.loadKnowledgeBase(agentTypeStr);
    
    // Process query based on type
    switch (query.type) {
      case QueryType.Concept:
        return this.queryConcept(knowledgeBase, query.id);
        
      case QueryType.Fact:
        return this.queryFact(knowledgeBase, query.id, query.domain);
        
      case QueryType.Rule:
        return this.queryRule(knowledgeBase, query.id, query.ruleType);
        
      case QueryType.Procedure:
        return this.queryProcedure(knowledgeBase, query.id, query.procedureType);
        
      case QueryType.Model:
        return this.queryModel(knowledgeBase, query.id, query.modelType);
        
      case QueryType.Resource:
        return this.queryResource(knowledgeBase, query.id, query.resourceType);
        
      default:
        throw new Error(`Unsupported query type: ${(query as any).type}`);
    }
  }
  
  /**
   * Updates a knowledge base with new information.
   * 
   * @param agentType The agent type
   * @param update The update to apply
   */
  async updateKnowledgeBase(agentType: AgentType | string, update: any): Promise<void> {
    const agentTypeStr = typeof agentType === 'string' ? agentType : agentType.toString();
    
    // Ensure knowledge base is loaded
    const knowledgeBase = await this.loadKnowledgeBase(agentTypeStr);
    
    // Apply updates
    for (const updateItem of update.updates) {
      switch (updateItem.operation) {
        case 'add':
          this.addKnowledgeItem(knowledgeBase, updateItem.path, updateItem.value);
          break;
          
        case 'update':
          this.updateKnowledgeItem(knowledgeBase, updateItem.path, updateItem.value);
          break;
          
        case 'delete':
          this.deleteKnowledgeItem(knowledgeBase, updateItem.path);
          break;
          
        default:
          throw new Error(`Unsupported update operation: ${updateItem.operation}`);
      }
    }
    
    // Update last_updated timestamp
    knowledgeBase.last_updated = new Date().toISOString();
    
    // Persist updated knowledge base
    await this.persistKnowledgeBase(agentTypeStr, knowledgeBase);
  }
  
  /**
   * Converts an agent type to a knowledge base filename.
   * 
   * @param agentType The agent type
   * @returns The filename for the knowledge base
   */
  private getKnowledgeBaseFilename(agentType: string): string {
    // Convert camelCase or snake_case to lowercase with underscores
    return agentType
      .replace(/([a-z])([A-Z])/g, '$1_$2')
      .toLowerCase();
  }
  
  /**
   * Creates an empty knowledge base structure.
   * 
   * @param agentType The agent type
   * @returns An empty knowledge base
   */
  private createEmptyKnowledgeBase(agentType: string): any {
    return {
      kb_version: "1.0",
      agent_type: agentType,
      last_updated: new Date().toISOString(),
      ontology: {
        concepts: [],
        relationships: [],
        taxonomies: []
      },
      facts: {
        core_facts: [],
        domain_facts: [],
        temporary_facts: []
      },
      rules: {
        inference_rules: [],
        constraint_rules: [],
        action_rules: []
      },
      procedures: {
        workflows: [],
        protocols: [],
        decision_trees: []
      },
      models: {
        embeddings: {},
        classifiers: {},
        generators: {}
      },
      external_resources: {
        apis: [],
        databases: [],
        file_systems: []
      }
    };
  }
  
  /**
   * Persists a knowledge base to disk.
   * 
   * @param agentType The agent type
   * @param knowledgeBase The knowledge base to persist
   */
  private async persistKnowledgeBase(agentType: string, knowledgeBase: any): Promise<void> {
    try {
      // Construct file path
      const filename = `${this.getKnowledgeBaseFilename(agentType)}_kb.json`;
      const filePath = path.join(this.knowledgeBasePath, filename);
      
      // Write to file
      await fs.writeFile(filePath, JSON.stringify(knowledgeBase, null, 2), 'utf-8');
      
      console.log(`Persisted knowledge base for agent type: ${agentType}`);
      
    } catch (error) {
      console.error(`Failed to persist knowledge base for agent type: ${agentType}`, error);
      throw error;
    }
  }
  
  /**
   * Queries a concept from a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param conceptId The concept ID
   * @returns The concept result
   */
  private queryConcept(knowledgeBase: any, conceptId: string): any {
    // Find the concept in the ontology
    const concept = knowledgeBase.ontology.concepts.find(
      (c: any) => c.id === conceptId
    );
    
    if (!concept) {
      throw new Error(`Concept not found: ${conceptId}`);
    }
    
    // Find relationships involving this concept
    const relationships = knowledgeBase.ontology.relationships.filter(
      (r: any) => r.source === conceptId || r.target === conceptId
    );
    
    return {
      id: concept.id,
      properties: concept.properties,
      relationships: relationships.map((r: any) => ({
        id: r.id,
        target: r.source === conceptId ? r.target : r.source,
        properties: r.properties
      }))
    };
  }
  
  /**
   * Queries a fact from a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param factId The fact ID
   * @param domain Optional domain filter
   * @returns The fact result
   */
  private queryFact(knowledgeBase: any, factId: string, domain?: string): any {
    // Check core facts
    let fact = knowledgeBase.facts.core_facts.find(
      (f: any) => f.id === factId
    );
    
    // Check domain facts if not found in core facts
    if (!fact && domain) {
      fact = knowledgeBase.facts.domain_facts.find(
        (f: any) => f.id === factId && (!domain || f.domain === domain)
      );
    }
    
    // Check domain facts without domain filter if still not found
    if (!fact && !domain) {
      fact = knowledgeBase.facts.domain_facts.find(
        (f: any) => f.id === factId
      );
    }
    
    // Check temporary facts if still not found
    if (!fact) {
      fact = knowledgeBase.facts.temporary_facts.find(
        (f: any) => f.id === factId
      );
    }
    
    if (!fact) {
      throw new Error(`Fact not found: ${factId}`);
    }
    
    return {
      id: fact.id,
      domain: fact.domain,
      content: fact.content,
      confidence: fact.confidence,
      source: fact.source
    };
  }
  
  /**
   * Queries a rule from a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param ruleId The rule ID
   * @param ruleType Optional rule type filter
   * @returns The rule result
   */
  private queryRule(knowledgeBase: any, ruleId: string, ruleType?: any): any {
    let rule;
    
    // If rule type is provided, check only that type
    if (ruleType) {
      const ruleTypeKey = `${ruleType}_rules`;
      rule = knowledgeBase.rules[ruleTypeKey]?.find(
        (r: any) => r.id === ruleId
      );
    } else {
      // Check all rule types
      for (const ruleTypeKey of Object.keys(knowledgeBase.rules)) {
        const foundRule = knowledgeBase.rules[ruleTypeKey]?.find(
          (r: any) => r.id === ruleId
        );
        
        if (foundRule) {
          rule = foundRule;
          ruleType = ruleTypeKey.replace('_rules', '');
          break;
        }
      }
    }
    
    if (!rule) {
      throw new Error(`Rule not found: ${ruleId}`);
    }
    
    return {
      id: rule.id,
      ruleType: ruleType,
      condition: rule.condition,
      conclusion: rule.conclusion,
      action: rule.action,
      parameters: rule.parameters
    };
  }
  
  /**
   * Queries a procedure from a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param procedureId The procedure ID
   * @param procedureType Optional procedure type filter
   * @returns The procedure result
   */
  private queryProcedure(knowledgeBase: any, procedureId: string, procedureType?: any): any {
    let procedure;
    
    // If procedure type is provided, check only that type
    if (procedureType) {
      procedure = knowledgeBase.procedures[procedureType + 's']?.find(
        (p: any) => p.id === procedureId
      );
    } else {
      // Check all procedure types
      for (const procedureTypeKey of Object.keys(knowledgeBase.procedures)) {
        const foundProcedure = knowledgeBase.procedures[procedureTypeKey]?.find(
          (p: any) => p.id === procedureId
        );
        
        if (foundProcedure) {
          procedure = foundProcedure;
          procedureType = procedureTypeKey.replace(/s$/, '');
          break;
        }
      }
    }
    
    if (!procedure) {
      throw new Error(`Procedure not found: ${procedureId}`);
    }
    
    return {
      id: procedure.id,
      procedureType: procedureType,
      steps: procedure.steps
    };
  }
  
  /**
   * Queries a model from a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param modelId The model ID
   * @param modelType Optional model type filter
   * @returns The model result
   */
  private queryModel(knowledgeBase: any, modelId: string, modelType?: any): any {
    let model;
    
    // If model type is provided, check only that type
    if (modelType) {
      model = knowledgeBase.models[modelType + 's']?.[modelId];
    } else {
      // Check all model types
      for (const modelTypeKey of Object.keys(knowledgeBase.models)) {
        const foundModel = knowledgeBase.models[modelTypeKey]?.[modelId];
        
        if (foundModel) {
          model = foundModel;
          modelType = modelTypeKey.replace(/s$/, '');
          break;
        }
      }
    }
    
    if (!model) {
      throw new Error(`Model not found: ${modelId}`);
    }
    
    return {
      id: modelId,
      modelType: modelType,
      ...model
    };
  }
  
  /**
   * Queries a resource from a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param resourceId The resource ID
   * @param resourceType Optional resource type filter
   * @returns The resource result
   */
  private queryResource(knowledgeBase: any, resourceId: string, resourceType?: string): any {
    let resource;
    
    // If resource type is provided, check only that type
    if (resourceType) {
      const resourceTypeKey = resourceType + 's';
      resource = knowledgeBase.external_resources[resourceTypeKey]?.find(
        (r: any) => r.id === resourceId
      );
    } else {
      // Check all resource types
      for (const resourceTypeKey of Object.keys(knowledgeBase.external_resources)) {
        const foundResource = knowledgeBase.external_resources[resourceTypeKey]?.find(
          (r: any) => r.id === resourceId
        );
        
        if (foundResource) {
          resource = foundResource;
          resourceType = resourceTypeKey.replace(/s$/, '');
          break;
        }
      }
    }
    
    if (!resource) {
      throw new Error(`Resource not found: ${resourceId}`);
    }
    
    return {
      id: resource.id,
      resourceType: resourceType!,
      endpoint: resource.endpoint,
      methods: resource.methods,
      authType: resource.auth_type
    };
  }
  
  /**
   * Adds a knowledge item to a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param path The path to add to
   * @param value The value to add
   */
  private addKnowledgeItem(knowledgeBase: any, path: string, value: any): void {
    const parts = path.split('.');
    let current = knowledgeBase;
    
    // Navigate to the parent object
    for (let i = 0; i < parts.length - 1; i++) {
      if (!(parts[i] in current)) {
        current[parts[i]] = {};
      }
      current = current[parts[i]];
    }
    
    // Add the value
    const lastPart = parts[parts.length - 1];
    
    if (Array.isArray(current[lastPart])) {
      current[lastPart].push(value);
    } else if (typeof current[lastPart] === 'object' && current[lastPart] !== null) {
      // For objects, merge the value
      current[lastPart] = { ...current[lastPart], ...value };
    } else {
      current[lastPart] = value;
    }
  }
  
  /**
   * Updates a knowledge item in a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param path The path to update
   * @param value The new value
   */
  private updateKnowledgeItem(knowledgeBase: any, path: string, value: any): void {
    const parts = path.split('.');
    let current = knowledgeBase;
    
    // Navigate to the parent object
    for (let i = 0; i < parts.length - 1; i++) {
      if (!(parts[i] in current)) {
        throw new Error(`Path not found: ${path}`);
      }
      current = current[parts[i]];
    }
    
    // Update the value
    const lastPart = parts[parts.length - 1];
    
    if (!(lastPart in current)) {
      throw new Error(`Path not found: ${path}`);
    }
    
    if (typeof current[lastPart] === 'object' && current[lastPart] !== null && 
        typeof value === 'object' && value !== null) {
      // For objects, merge the value
      current[lastPart] = { ...current[lastPart], ...value };
    } else {
      current[lastPart] = value;
    }
  }
  
  /**
   * Deletes a knowledge item from a knowledge base.
   * 
   * @param knowledgeBase The knowledge base
   * @param path The path to delete
   */
  private deleteKnowledgeItem(knowledgeBase: any, path: string): void {
    const parts = path.split('.');
    let current = knowledgeBase;
    
    // Navigate to the parent object
    for (let i = 0; i < parts.length - 1; i++) {
      if (!(parts[i] in current)) {
        throw new Error(`Path not found: ${path}`);
      }
      current = current[parts[i]];
    }
    
    // Delete the value
    const lastPart = parts[parts.length - 1];
    
    if (!(lastPart in current)) {
      throw new Error(`Path not found: ${path}`);
    }
    
    if (Array.isArray(current)) {
      current.splice(parseInt(lastPart), 1);
    } else {
      delete current[lastPart];
    }
  }
}