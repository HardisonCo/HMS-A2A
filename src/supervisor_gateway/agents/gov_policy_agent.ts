/**
 * Gov Policy Agent Implementation
 * 
 * This agent specializes in government policy analysis, formulation, and regulatory compliance.
 * It handles policy queries, regulatory assessment, and provides policy recommendations.
 */

import { BaseAgent } from './base_agent';
import { Message } from '../communication/message';
import { KnowledgeBaseManager } from '../knowledge/knowledge_base_manager';
import { PolicyFormulator } from '../policy/policy_formulator';
import { RegulatoryAssessment } from '../policy/regulatory_assessment';
import { Tool } from '../tools/tool_types';

/**
 * Specialized agent for government policy analysis and formulation
 */
export class GovPolicyAgent extends BaseAgent {
  private policyFormulator: PolicyFormulator;
  private regulatoryAssessment: RegulatoryAssessment;
  
  /**
   * Creates a new GovPolicyAgent
   * 
   * @param id - Unique identifier for this agent
   * @param knowledgeBaseManager - The knowledge base manager for accessing domain knowledge
   */
  constructor(
    id: string, 
    knowledgeBaseManager: KnowledgeBaseManager,
    policyFormulator?: PolicyFormulator,
    regulatoryAssessment?: RegulatoryAssessment
  ) {
    super(id, 'gov', knowledgeBaseManager);
    
    // Initialize policy formulator with default if not provided
    this.policyFormulator = policyFormulator || new PolicyFormulator(knowledgeBaseManager);
    
    // Initialize regulatory assessment with default if not provided
    this.regulatoryAssessment = regulatoryAssessment || new RegulatoryAssessment(knowledgeBaseManager);
    
    // Register specialized tools
    this.registerPolicyTools();
  }
  
  /**
   * Registers policy-specific tools
   */
  private registerPolicyTools() {
    // Register policy formulation tool
    this.registerTool({
      id: 'policy_formulation',
      name: 'Policy Formulation Tool',
      description: 'Creates policy proposals based on specific goals and constraints',
      execute: async (params: any) => {
        return this.policyFormulator.createPolicy(
          params.domain,
          params.goals,
          params.constraints
        );
      }
    });
    
    // Register regulatory assessment tool
    this.registerTool({
      id: 'regulatory_assessment',
      name: 'Regulatory Assessment Tool',
      description: 'Evaluates policy proposals for regulatory compliance',
      execute: async (params: any) => {
        return this.regulatoryAssessment.assessCompliance(
          params.policyProposal,
          params.regulatoryFrameworks
        );
      }
    });
    
    // Register regulatory search tool
    this.registerTool({
      id: 'regulatory_search',
      name: 'Regulatory Search Tool',
      description: 'Searches for relevant regulations based on keywords',
      execute: async (params: any) => {
        return this.regulatoryAssessment.findRelevantRegulations(
          params.domain,
          params.keywords
        );
      }
    });
  }
  
  /**
   * Process incoming messages directed to this agent
   * 
   * @param message - The message to process
   * @returns A response message
   */
  async processMessage(message: Message): Promise<Message> {
    try {
      // Log message receipt
      this.logger.info(`GovPolicyAgent received message: ${message.messageType} - ${message.content.query_type}`);
      
      // Process based on query type
      switch (message.content.query_type) {
        case 'policy_formulation':
          return this.handlePolicyFormulation(message);
          
        case 'regulatory_assessment':
          return this.handleRegulatoryAssessment(message);
          
        case 'policy_analysis':
          return this.handlePolicyAnalysis(message);
          
        case 'regulatory_search':
          return this.handleRegulatorySearch(message);
          
        case 'multi_domain_analysis':
          return this.handleMultiDomainAnalysis(message);
          
        default:
          // Fall back to base agent processing for generic queries
          return super.processMessage(message);
      }
    } catch (error) {
      this.logger.error(`Error processing message in GovPolicyAgent: ${error.message}`);
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Error processing message: ${error.message}`
      );
    }
  }
  
  /**
   * Handles policy formulation requests
   */
  private async handlePolicyFormulation(message: Message): Promise<Message> {
    const { domain, goals, constraints } = message.content.body;
    
    // Validate required parameters
    if (!domain || !goals) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Policy formulation requires domain and goals parameters'
      );
    }
    
    try {
      // Generate policy proposal
      const policyProposal = await this.policyFormulator.createPolicy(
        domain,
        goals,
        constraints || []
      );
      
      // If requested, assess regulatory compliance
      if (message.content.body.assess_compliance) {
        const frameworks = message.content.body.regulatory_frameworks || ['default'];
        const complianceAssessment = await this.regulatoryAssessment.assessCompliance(
          policyProposal,
          frameworks
        );
        
        // Return policy proposal with compliance assessment
        return Message.createResponse(
          message,
          this.id,
          this.type,
          {
            policy_proposal: policyProposal,
            compliance_assessment: complianceAssessment
          }
        );
      }
      
      // Return just the policy proposal
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { policy_proposal: policyProposal }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Policy formulation error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles regulatory assessment requests
   */
  private async handleRegulatoryAssessment(message: Message): Promise<Message> {
    const { policy_proposal, regulatory_frameworks } = message.content.body;
    
    // Validate required parameters
    if (!policy_proposal) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Regulatory assessment requires a policy_proposal parameter'
      );
    }
    
    try {
      // Perform regulatory assessment
      const complianceAssessment = await this.regulatoryAssessment.assessCompliance(
        policy_proposal,
        regulatory_frameworks || ['default']
      );
      
      // Return compliance assessment
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { compliance_assessment: complianceAssessment }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Regulatory assessment error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles policy analysis requests
   */
  private async handlePolicyAnalysis(message: Message): Promise<Message> {
    const { policy, analysis_dimensions } = message.content.body;
    
    // Validate required parameters
    if (!policy) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Policy analysis requires a policy parameter'
      );
    }
    
    try {
      // Analyze policy across requested dimensions
      const dimensions = analysis_dimensions || ['effectiveness', 'cost', 'implementation_complexity'];
      const analysis = await this.policyFormulator.analyzePolicy(policy, dimensions);
      
      // Return policy analysis
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { policy_analysis: analysis }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Policy analysis error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles regulatory search requests
   */
  private async handleRegulatorySearch(message: Message): Promise<Message> {
    const { domain, keywords } = message.content.body;
    
    // Validate required parameters
    if (!domain || !keywords || !keywords.length) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Regulatory search requires domain and keywords parameters'
      );
    }
    
    try {
      // Find relevant regulations
      const regulations = await this.regulatoryAssessment.findRelevantRegulations(
        domain,
        keywords
      );
      
      // Return found regulations
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { regulations }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Regulatory search error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles multi-domain analysis requests by providing policy and regulatory implications
   */
  private async handleMultiDomainAnalysis(message: Message): Promise<Message> {
    try {
      // Extract relevant content for policy analysis
      const { question, sectors = [], domains = [] } = message.content.body;
      
      // Determine relevant policy domains
      const policyDomains = domains.filter(d => 
        ['policy', 'government', 'regulation', 'legal', 'compliance'].includes(d.toLowerCase())
      );
      
      // If no policy domains specified but likely needs policy analysis
      const needsPolicyAnalysis = policyDomains.length > 0 || 
        question.toLowerCase().includes('policy') ||
        question.toLowerCase().includes('regulation') ||
        question.toLowerCase().includes('government');
      
      if (!needsPolicyAnalysis) {
        // Not enough policy context for detailed analysis
        return Message.createResponse(
          message,
          this.id,
          this.type,
          { 
            policy_implications: ["Insufficient policy context for detailed analysis"],
            regulatory_implications: {} 
          }
        );
      }
      
      // Get the relevant policies and regulations
      const keywords = this.extractKeywords(question);
      const relevantDomains = sectors.length > 0 ? sectors : ['general'];
      
      // Generate policy implications
      const policyImplications = await Promise.all(
        relevantDomains.map(async (domain) => {
          try {
            const regulations = await this.regulatoryAssessment.findRelevantRegulations(
              domain,
              keywords
            );
            
            return {
              domain,
              regulations: regulations.slice(0, 3), // Top 3 most relevant
              implications: await this.policyFormulator.analyzePolicyImplications(
                domain,
                question,
                keywords
              )
            };
          } catch (error) {
            this.logger.error(`Error analyzing policy implications for domain ${domain}: ${error.message}`);
            return {
              domain,
              regulations: [],
              implications: ["Error analyzing policy implications"]
            };
          }
        })
      );
      
      // Format regulatory implications
      const regulatoryImplications = {
        newRegulations: policyImplications.flatMap(p => 
          p.implications.filter(i => i.toLowerCase().includes('new') || i.toLowerCase().includes('create'))
        ),
        legislativeChanges: policyImplications.flatMap(p => 
          p.implications.filter(i => i.toLowerCase().includes('amend') || i.toLowerCase().includes('change'))
        ),
        complianceRequirements: policyImplications.flatMap(p => 
          p.implications.filter(i => i.toLowerCase().includes('comply') || i.toLowerCase().includes('requirement'))
        )
      };
      
      // Return the policy implications
      return Message.createResponse(
        message,
        this.id,
        this.type,
        {
          policy_implications: policyImplications,
          regulatory_implications: regulatoryImplications
        }
      );
    } catch (error) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Multi-domain analysis error: ${error.message}`
      );
    }
  }
  
  /**
   * Extracts relevant keywords from a question for policy analysis
   */
  private extractKeywords(question: string): string[] {
    // Simple keyword extraction implementation
    const keywords = [];
    
    // Extract words that might be relevant to policy
    const policyTerms = [
      'policy', 'regulation', 'law', 'compliance', 'legal', 'government',
      'federal', 'state', 'local', 'agency', 'statute', 'rule', 'bill',
      'act', 'amendment', 'reform', 'legislation', 'requirement'
    ];
    
    // Split question into words and check for policy terms
    const words = question.toLowerCase().split(/\s+/);
    for (const word of words) {
      if (policyTerms.includes(word)) {
        keywords.push(word);
      }
    }
    
    // Extract noun phrases (simple implementation)
    const phrases = question.match(/\b(?:[A-Z][a-z]* )+(?:Act|Policy|Regulation|Law|Bill|Reform|Legislation)\b/g);
    if (phrases) {
      keywords.push(...phrases);
    }
    
    // If no specific keywords found, use general terms
    if (keywords.length === 0) {
      keywords.push('policy', 'regulation');
    }
    
    return [...new Set(keywords)]; // Remove duplicates
  }
}