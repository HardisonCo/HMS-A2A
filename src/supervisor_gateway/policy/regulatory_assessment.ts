/**
 * Regulatory Assessment
 * 
 * This class provides capabilities for assessing regulatory compliance of policy proposals,
 * finding relevant regulations, and analyzing regulatory frameworks.
 */

import { KnowledgeBaseManager } from '../knowledge/knowledge_base_manager';
import { PolicyProposal, PolicyDomain } from './policy_formulator';

/**
 * Regulation structure
 */
export interface Regulation {
  id: string;
  name: string;
  domain: string;
  description: string;
  requirements: {
    id: string;
    description: string;
    applicability_criteria: string;
    documentation_required: string;
  }[];
  enforcement: {
    authority: string;
    mechanisms: string[];
    penalties: string[];
  };
  metadata: {
    effective_date: string;
    last_updated: string;
    jurisdiction: string;
    source_url?: string;
  };
}

/**
 * Compliance assessment result
 */
export interface ComplianceAssessment {
  policy_id: string;
  policy_name: string;
  regulatory_frameworks: string[];
  compliance_status: 'compliant' | 'partially_compliant' | 'non_compliant' | 'undetermined';
  compliance_score: number;
  assessment_details: {
    framework: string;
    requirements_assessed: number;
    requirements_met: number;
    requirements_partially_met: number;
    requirements_not_met: number;
    critical_gaps: string[];
  }[];
  recommended_actions: string[];
  metadata: {
    assessment_date: string;
    assessment_method: string;
    assessor: string;
  };
}

/**
 * Regulatory Assessment class that handles compliance assessment and regulatory search
 */
export class RegulatoryAssessment {
  constructor(private knowledgeBaseManager: KnowledgeBaseManager) {}
  
  /**
   * Assesses the compliance of a policy proposal against regulatory frameworks
   * 
   * @param policy - The policy proposal to assess
   * @param frameworks - The regulatory frameworks to assess against
   * @returns A compliance assessment
   */
  async assessCompliance(
    policy: PolicyProposal,
    frameworks: string[] = ['default']
  ): Promise<ComplianceAssessment> {
    // Validate policy
    if (!policy.id || !policy.domain || !policy.goals) {
      throw new Error('Invalid policy proposal provided for compliance assessment');
    }
    
    // Get relevant regulations for each framework
    const frameworkAssessments = await Promise.all(
      frameworks.map(async framework => {
        return this.assessFrameworkCompliance(policy, framework);
      })
    );
    
    // Calculate overall compliance score
    const totalRequirements = frameworkAssessments.reduce((sum, a) => sum + a.requirements_assessed, 0);
    const metRequirements = frameworkAssessments.reduce((sum, a) => sum + a.requirements_met, 0);
    const partiallyMetRequirements = frameworkAssessments.reduce((sum, a) => sum + a.requirements_partially_met, 0);
    
    const complianceScore = totalRequirements > 0 
      ? (metRequirements + (partiallyMetRequirements * 0.5)) / totalRequirements 
      : 0;
    
    // Determine overall compliance status
    let complianceStatus: ComplianceAssessment['compliance_status'];
    if (complianceScore >= 0.9) {
      complianceStatus = 'compliant';
    } else if (complianceScore >= 0.6) {
      complianceStatus = 'partially_compliant';
    } else if (complianceScore > 0) {
      complianceStatus = 'non_compliant';
    } else {
      complianceStatus = 'undetermined';
    }
    
    // Generate recommended actions
    const recommendedActions = this.generateRecommendedActions(policy, frameworkAssessments);
    
    // Create the compliance assessment
    const complianceAssessment: ComplianceAssessment = {
      policy_id: policy.id,
      policy_name: policy.name,
      regulatory_frameworks: frameworks,
      compliance_status: complianceStatus,
      compliance_score: complianceScore,
      assessment_details: frameworkAssessments,
      recommended_actions: recommendedActions,
      metadata: {
        assessment_date: new Date().toISOString(),
        assessment_method: 'requirements-based-assessment',
        assessor: 'gov-policy-agent'
      }
    };
    
    return complianceAssessment;
  }
  
  /**
   * Finds regulations relevant to a domain and keywords
   * 
   * @param domain - The domain to search in
   * @param keywords - Keywords to search for
   * @returns An array of relevant regulations
   */
  async findRelevantRegulations(
    domain: string,
    keywords: string[]
  ): Promise<Regulation[]> {
    // Normalize domain
    const normalizedDomain = this.normalizeDomain(domain);
    
    // Get domain-specific regulations
    const regulations = await this.getDomainRegulations(normalizedDomain);
    
    // If no keywords, return all domain regulations
    if (!keywords || keywords.length === 0) {
      return regulations;
    }
    
    // Filter regulations by keywords
    const relevantRegulations = regulations.filter(regulation => {
      // Check regulation name
      if (keywords.some(keyword => regulation.name.toLowerCase().includes(keyword.toLowerCase()))) {
        return true;
      }
      
      // Check regulation description
      if (keywords.some(keyword => regulation.description.toLowerCase().includes(keyword.toLowerCase()))) {
        return true;
      }
      
      // Check regulation requirements
      if (regulation.requirements.some(req => 
        keywords.some(keyword => req.description.toLowerCase().includes(keyword.toLowerCase()))
      )) {
        return true;
      }
      
      return false;
    });
    
    // Sort regulations by relevance (number of keyword matches)
    relevantRegulations.sort((a, b) => {
      const aMatches = this.countKeywordMatches(a, keywords);
      const bMatches = this.countKeywordMatches(b, keywords);
      return bMatches - aMatches;
    });
    
    return relevantRegulations;
  }
  
  /**
   * Assesses compliance against a specific regulatory framework
   */
  private async assessFrameworkCompliance(
    policy: PolicyProposal,
    framework: string
  ): Promise<ComplianceAssessment['assessment_details'][0]> {
    // Get relevant regulations for the framework
    const regulations = await this.getFrameworkRegulations(framework, policy.domain);
    
    // Count requirements
    const totalRequirements = regulations.reduce((sum, reg) => sum + reg.requirements.length, 0);
    
    // If no requirements, return undetermined assessment
    if (totalRequirements === 0) {
      return {
        framework,
        requirements_assessed: 0,
        requirements_met: 0,
        requirements_partially_met: 0,
        requirements_not_met: 0,
        critical_gaps: [`No requirements found for framework: ${framework}`]
      };
    }
    
    // Assess each regulation requirement
    let requirementsMet = 0;
    let requirementsPartiallyMet = 0;
    let requirementsNotMet = 0;
    const criticalGaps: string[] = [];
    
    for (const regulation of regulations) {
      for (const requirement of regulation.requirements) {
        // Check if policy meets the requirement
        const requirementStatus = this.assessRequirementCompliance(policy, requirement);
        
        if (requirementStatus === 'met') {
          requirementsMet++;
        } else if (requirementStatus === 'partially_met') {
          requirementsPartiallyMet++;
          // Check if this is a critical requirement
          if (requirement.description.toLowerCase().includes('critical') || 
              requirement.description.toLowerCase().includes('mandatory') ||
              requirement.description.toLowerCase().includes('required')) {
            criticalGaps.push(`Partially met critical requirement in ${regulation.name}: ${requirement.description}`);
          }
        } else {
          requirementsNotMet++;
          // Check if this is a critical requirement
          if (requirement.description.toLowerCase().includes('critical') || 
              requirement.description.toLowerCase().includes('mandatory') ||
              requirement.description.toLowerCase().includes('required')) {
            criticalGaps.push(`Unmet critical requirement in ${regulation.name}: ${requirement.description}`);
          }
        }
      }
    }
    
    // Create assessment details
    return {
      framework,
      requirements_assessed: totalRequirements,
      requirements_met: requirementsMet,
      requirements_partially_met: requirementsPartiallyMet,
      requirements_not_met: requirementsNotMet,
      critical_gaps: criticalGaps
    };
  }
  
  /**
   * Assesses if a policy meets a specific requirement
   */
  private assessRequirementCompliance(
    policy: PolicyProposal,
    requirement: Regulation['requirements'][0]
  ): 'met' | 'partially_met' | 'not_met' {
    // Check if any policy measure directly addresses the requirement
    const directMeasure = policy.measures.find(measure => 
      this.containsSimilarContent(measure.description, requirement.description)
    );
    
    if (directMeasure) {
      return 'met';
    }
    
    // Check if any policy measure partially addresses the requirement
    const partialMeasure = policy.measures.find(measure => 
      this.containsPartialMatch(measure.description, requirement.description)
    );
    
    if (partialMeasure) {
      return 'partially_met';
    }
    
    // Check if any policy goal addresses the requirement
    const goalMatch = policy.goals.some(goal => 
      this.containsPartialMatch(goal, requirement.description)
    );
    
    if (goalMatch) {
      return 'partially_met';
    }
    
    return 'not_met';
  }
  
  /**
   * Generates recommended actions based on compliance assessment
   */
  private generateRecommendedActions(
    policy: PolicyProposal,
    frameworkAssessments: ComplianceAssessment['assessment_details']
  ): string[] {
    const recommendedActions: string[] = [];
    
    // Add actions for critical gaps
    const allCriticalGaps = frameworkAssessments.flatMap(a => a.critical_gaps);
    
    if (allCriticalGaps.length > 0) {
      recommendedActions.push('Address critical compliance gaps identified in the assessment');
      
      // Add specific actions for each framework with critical gaps
      for (const assessment of frameworkAssessments) {
        if (assessment.critical_gaps.length > 0) {
          recommendedActions.push(`Revise policy to address ${assessment.critical_gaps.length} critical requirements in ${assessment.framework} framework`);
        }
      }
    }
    
    // Add actions based on compliance scores
    const lowComplianceFrameworks = frameworkAssessments.filter(a => 
      a.requirements_assessed > 0 && a.requirements_met / a.requirements_assessed < 0.6
    );
    
    if (lowComplianceFrameworks.length > 0) {
      recommendedActions.push(`Conduct detailed compliance review for ${lowComplianceFrameworks.map(f => f.framework).join(', ')} frameworks`);
    }
    
    // Add documentation recommendation if needed
    const anyRequiresDocumentation = frameworkAssessments.some(a => 
      a.framework.toLowerCase().includes('documentation') || 
      a.critical_gaps.some(gap => gap.toLowerCase().includes('documentation'))
    );
    
    if (anyRequiresDocumentation) {
      recommendedActions.push('Enhance policy documentation to demonstrate compliance with regulatory requirements');
    }
    
    // Add general recommendation
    recommendedActions.push('Consult with compliance experts to validate assessment and address identified gaps');
    
    return recommendedActions;
  }
  
  /**
   * Gets domain-specific regulations
   */
  private async getDomainRegulations(domain: string): Promise<Regulation[]> {
    // Attempt to get regulations from knowledge base
    try {
      const knowledgeBase = await this.knowledgeBaseManager.getKnowledgeBase('gov');
      
      if (knowledgeBase) {
        // Extract regulations from knowledge base (implementation would depend on knowledge base structure)
        // This is a placeholder implementation
        return this.getMockRegulations(domain);
      }
    } catch (error) {
      console.error(`Error retrieving regulations from knowledge base for ${domain}:`, error);
    }
    
    // If knowledge base retrieval fails, return mock regulations
    return this.getMockRegulations(domain);
  }
  
  /**
   * Gets regulations for a specific framework
   */
  private async getFrameworkRegulations(framework: string, domain: string): Promise<Regulation[]> {
    // Get domain regulations
    const domainRegulations = await this.getDomainRegulations(domain);
    
    // Filter by framework (in a real implementation, this would use more sophisticated matching)
    if (framework.toLowerCase() === 'default') {
      return domainRegulations;
    }
    
    // Filter regulations by framework
    return domainRegulations.filter(regulation => 
      regulation.name.toLowerCase().includes(framework.toLowerCase()) ||
      regulation.description.toLowerCase().includes(framework.toLowerCase())
    );
  }
  
  /**
   * Counts the number of keyword matches in a regulation
   */
  private countKeywordMatches(regulation: Regulation, keywords: string[]): number {
    let matches = 0;
    
    // Check regulation name
    for (const keyword of keywords) {
      if (regulation.name.toLowerCase().includes(keyword.toLowerCase())) {
        matches++;
      }
    }
    
    // Check regulation description
    for (const keyword of keywords) {
      if (regulation.description.toLowerCase().includes(keyword.toLowerCase())) {
        matches++;
      }
    }
    
    // Check regulation requirements
    for (const requirement of regulation.requirements) {
      for (const keyword of keywords) {
        if (requirement.description.toLowerCase().includes(keyword.toLowerCase())) {
          matches++;
        }
      }
    }
    
    return matches;
  }
  
  /**
   * Checks if text contains similar content to a requirement
   */
  private containsSimilarContent(text: string, requirement: string): boolean {
    // Normalize text
    const normalizedText = text.toLowerCase();
    const normalizedRequirement = requirement.toLowerCase();
    
    // Check if text directly contains the requirement
    if (normalizedText.includes(normalizedRequirement)) {
      return true;
    }
    
    // Extract key phrases from requirement (simplified implementation)
    const keyPhrases = normalizedRequirement.split(/[.,;]/).map(p => p.trim()).filter(p => p.length > 0);
    
    // Check if text contains at least 70% of the key phrases
    const matchingPhrases = keyPhrases.filter(phrase => normalizedText.includes(phrase));
    return matchingPhrases.length >= keyPhrases.length * 0.7;
  }
  
  /**
   * Checks if text contains a partial match to a requirement
   */
  private containsPartialMatch(text: string, requirement: string): boolean {
    // Normalize text
    const normalizedText = text.toLowerCase();
    const normalizedRequirement = requirement.toLowerCase();
    
    // Extract key words from requirement (simple implementation)
    const requirementWords = normalizedRequirement.split(/\s+/).filter(w => w.length > 4);
    
    // Check if text contains at least 30% of the key words
    const matchingWords = requirementWords.filter(word => normalizedText.includes(word));
    return matchingWords.length >= requirementWords.length * 0.3;
  }
  
  /**
   * Normalizes a domain string to a standard format
   */
  private normalizeDomain(domain: string): string {
    domain = domain.toLowerCase().trim();
    
    // Check if domain matches any of the PolicyDomain values
    const domainValues = Object.values(PolicyDomain);
    for (const value of domainValues) {
      if (domain === value || domain.includes(value)) {
        return value;
      }
    }
    
    // If no match found, return general
    return PolicyDomain.GENERAL;
  }
  
  /**
   * Provides mock regulations for testing and development
   */
  private getMockRegulations(domain: string): Regulation[] {
    // Healthcare regulations
    if (domain === PolicyDomain.HEALTHCARE) {
      return [
        {
          id: 'reg-healthcare-1',
          name: 'Healthcare Data Protection Regulation',
          domain: PolicyDomain.HEALTHCARE,
          description: 'Regulations governing the protection and privacy of healthcare data.',
          requirements: [
            {
              id: 'req-healthcare-1-1',
              description: 'Implement secure data storage mechanisms for patient records.',
              applicability_criteria: 'All entities storing patient data',
              documentation_required: 'Data security compliance report'
            },
            {
              id: 'req-healthcare-1-2',
              description: 'Obtain explicit consent for data collection and processing.',
              applicability_criteria: 'All entities collecting patient data',
              documentation_required: 'Consent forms and procedures'
            },
            {
              id: 'req-healthcare-1-3',
              description: 'Provide data breach notification within 72 hours.',
              applicability_criteria: 'All healthcare providers',
              documentation_required: 'Breach notification protocol'
            }
          ],
          enforcement: {
            authority: 'Healthcare Data Protection Authority',
            mechanisms: ['Audits', 'Investigations', 'Compliance reports'],
            penalties: ['Monetary fines', 'Operational restrictions', 'Public notices']
          },
          metadata: {
            effective_date: '2023-01-01',
            last_updated: '2023-01-01',
            jurisdiction: 'Federal',
            source_url: 'https://example.gov/healthcare-data-regulation'
          }
        },
        {
          id: 'reg-healthcare-2',
          name: 'Healthcare Provider Standards',
          domain: PolicyDomain.HEALTHCARE,
          description: 'Regulations establishing standards for healthcare provider operations.',
          requirements: [
            {
              id: 'req-healthcare-2-1',
              description: 'Maintain appropriate staffing ratios for patient care.',
              applicability_criteria: 'All inpatient healthcare facilities',
              documentation_required: 'Staffing records and policies'
            },
            {
              id: 'req-healthcare-2-2',
              description: 'Implement quality assurance programs for patient care.',
              applicability_criteria: 'All healthcare providers',
              documentation_required: 'Quality assurance program documentation'
            },
            {
              id: 'req-healthcare-2-3',
              description: 'Provide regular staff training on updated procedures.',
              applicability_criteria: 'All healthcare providers',
              documentation_required: 'Training records and materials'
            }
          ],
          enforcement: {
            authority: 'Healthcare Standards Board',
            mechanisms: ['Certification inspections', 'Patient outcome monitoring', 'Complaint investigations'],
            penalties: ['Certification restrictions', 'Mandatory improvements', 'Operational limitations']
          },
          metadata: {
            effective_date: '2022-06-15',
            last_updated: '2022-06-15',
            jurisdiction: 'Federal',
            source_url: 'https://example.gov/healthcare-provider-standards'
          }
        }
      ];
    }
    // Economic regulations
    else if (domain === PolicyDomain.ECONOMIC) {
      return [
        {
          id: 'reg-economic-1',
          name: 'Fair Market Competition Regulation',
          domain: PolicyDomain.ECONOMIC,
          description: 'Regulations ensuring fair competition in markets and preventing monopolistic practices.',
          requirements: [
            {
              id: 'req-economic-1-1',
              description: 'Submit market share analysis for mergers and acquisitions.',
              applicability_criteria: 'Companies with significant market presence',
              documentation_required: 'Market analysis report'
            },
            {
              id: 'req-economic-1-2',
              description: 'Disclose pricing agreements with competitors.',
              applicability_criteria: 'All companies in regulated markets',
              documentation_required: 'Disclosure statements'
            },
            {
              id: 'req-economic-1-3',
              description: 'Maintain records of competitive practices for audit.',
              applicability_criteria: 'All companies in regulated markets',
              documentation_required: 'Competition practice records'
            }
          ],
          enforcement: {
            authority: 'Market Competition Commission',
            mechanisms: ['Market investigations', 'Compliance audits', 'Whistleblower reports'],
            penalties: ['Financial penalties', 'Restructuring orders', 'Operational restrictions']
          },
          metadata: {
            effective_date: '2021-10-30',
            last_updated: '2023-03-15',
            jurisdiction: 'Federal',
            source_url: 'https://example.gov/fair-market-competition'
          }
        },
        {
          id: 'reg-economic-2',
          name: 'Small Business Support Framework',
          domain: PolicyDomain.ECONOMIC,
          description: 'Regulatory framework for supporting small business growth and sustainability.',
          requirements: [
            {
              id: 'req-economic-2-1',
              description: 'Provide preferential procurement opportunities for small businesses.',
              applicability_criteria: 'Government agencies and large contractors',
              documentation_required: 'Procurement policies and records'
            },
            {
              id: 'req-economic-2-2',
              description: 'Offer simplified regulatory compliance for qualifying small businesses.',
              applicability_criteria: 'Regulatory agencies',
              documentation_required: 'Small business regulatory processes'
            },
            {
              id: 'req-economic-2-3',
              description: 'Establish small business support programs with funding allocations.',
              applicability_criteria: 'Economic development agencies',
              documentation_required: 'Program documentation and funding allocation'
            }
          ],
          enforcement: {
            authority: 'Small Business Administration',
            mechanisms: ['Program reviews', 'Compliance reporting', 'Stakeholder feedback'],
            penalties: ['Program funding adjustments', 'Compliance orders', 'Public reporting']
          },
          metadata: {
            effective_date: '2022-01-15',
            last_updated: '2022-01-15',
            jurisdiction: 'Federal',
            source_url: 'https://example.gov/small-business-framework'
          }
        }
      ];
    }
    // Education regulations
    else if (domain === PolicyDomain.EDUCATION) {
      return [
        {
          id: 'reg-education-1',
          name: 'Educational Institution Standards',
          domain: PolicyDomain.EDUCATION,
          description: 'Regulations establishing standards for educational institutions.',
          requirements: [
            {
              id: 'req-education-1-1',
              description: 'Maintain qualified teaching staff with appropriate certifications.',
              applicability_criteria: 'All educational institutions',
              documentation_required: 'Staff qualifications and certifications'
            },
            {
              id: 'req-education-1-2',
              description: 'Implement curriculum meeting educational standards.',
              applicability_criteria: 'All educational institutions',
              documentation_required: 'Curriculum documentation'
            },
            {
              id: 'req-education-1-3',
              description: 'Provide adequate facilities for educational activities.',
              applicability_criteria: 'All educational institutions',
              documentation_required: 'Facility assessment and maintenance records'
            }
          ],
          enforcement: {
            authority: 'Education Standards Board',
            mechanisms: ['Accreditation reviews', 'Student outcome assessments', 'Facility inspections'],
            penalties: ['Accreditation restrictions', 'Improvement mandates', 'Funding implications']
          },
          metadata: {
            effective_date: '2021-08-01',
            last_updated: '2023-02-15',
            jurisdiction: 'Federal and State',
            source_url: 'https://example.gov/education-institution-standards'
          }
        },
        {
          id: 'reg-education-2',
          name: 'Student Data Protection Framework',
          domain: PolicyDomain.EDUCATION,
          description: 'Regulations governing the protection and use of student data.',
          requirements: [
            {
              id: 'req-education-2-1',
              description: 'Implement secure storage of student records and information.',
              applicability_criteria: 'All educational institutions',
              documentation_required: 'Data security policies and implementation'
            },
            {
              id: 'req-education-2-2',
              description: 'Obtain parental consent for data collection from minors.',
              applicability_criteria: 'All educational institutions serving minors',
              documentation_required: 'Consent forms and procedures'
            },
            {
              id: 'req-education-2-3',
              description: 'Limit data sharing to authorized educational purposes.',
              applicability_criteria: 'All entities handling student data',
              documentation_required: 'Data sharing policies and agreements'
            }
          ],
          enforcement: {
            authority: 'Education Privacy Office',
            mechanisms: ['Data practice audits', 'Complaint investigations', 'Compliance reporting'],
            penalties: ['Remediation orders', 'Financial penalties', 'Operational restrictions']
          },
          metadata: {
            effective_date: '2022-01-15',
            last_updated: '2022-01-15',
            jurisdiction: 'Federal',
            source_url: 'https://example.gov/student-data-protection'
          }
        }
      ];
    }
    // Default regulations for other domains
    else {
      return [
        {
          id: `reg-${domain}-1`,
          name: `${this.capitalizeFirstLetter(domain)} Operational Standards`,
          domain: domain,
          description: `Regulations establishing standards for ${domain} operations.`,
          requirements: [
            {
              id: `req-${domain}-1-1`,
              description: `Implement quality assurance programs for ${domain} activities.`,
              applicability_criteria: `All ${domain} service providers`,
              documentation_required: 'Quality assurance program documentation'
            },
            {
              id: `req-${domain}-1-2`,
              description: `Maintain appropriate staffing for ${domain} functions.`,
              applicability_criteria: `All ${domain} service providers`,
              documentation_required: 'Staffing policies and records'
            },
            {
              id: `req-${domain}-1-3`,
              description: `Provide regular staff training on ${domain} procedures.`,
              applicability_criteria: `All ${domain} service providers`,
              documentation_required: 'Training documentation'
            }
          ],
          enforcement: {
            authority: `${this.capitalizeFirstLetter(domain)} Standards Authority`,
            mechanisms: ['Compliance audits', 'Certification inspections', 'Performance monitoring'],
            penalties: ['Certification restrictions', 'Improvement mandates', 'Operational limitations']
          },
          metadata: {
            effective_date: '2022-01-01',
            last_updated: '2022-01-01',
            jurisdiction: 'Federal',
            source_url: `https://example.gov/${domain}-standards`
          }
        },
        {
          id: `reg-${domain}-2`,
          name: `${this.capitalizeFirstLetter(domain)} Data Management Regulation`,
          domain: domain,
          description: `Regulations governing data management in the ${domain} sector.`,
          requirements: [
            {
              id: `req-${domain}-2-1`,
              description: `Implement secure data storage for ${domain} information.`,
              applicability_criteria: `All entities handling ${domain} data`,
              documentation_required: 'Data security policies and implementation'
            },
            {
              id: `req-${domain}-2-2`,
              description: `Obtain appropriate consent for ${domain} data collection.`,
              applicability_criteria: `All entities collecting ${domain} data`,
              documentation_required: 'Consent forms and procedures'
            },
            {
              id: `req-${domain}-2-3`,
              description: `Provide data breach notification for ${domain} information incidents.`,
              applicability_criteria: `All entities handling ${domain} data`,
              documentation_required: 'Breach notification protocols'
            }
          ],
          enforcement: {
            authority: `${this.capitalizeFirstLetter(domain)} Data Protection Office`,
            mechanisms: ['Data practice audits', 'Complaint investigations', 'Compliance reporting'],
            penalties: ['Remediation orders', 'Financial penalties', 'Operational restrictions']
          },
          metadata: {
            effective_date: '2022-06-01',
            last_updated: '2022-06-01',
            jurisdiction: 'Federal',
            source_url: `https://example.gov/${domain}-data-regulation`
          }
        }
      ];
    }
  }
  
  /**
   * Utility to capitalize the first letter of a string
   */
  private capitalizeFirstLetter(string: string): string {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
}