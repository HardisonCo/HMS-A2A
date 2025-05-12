/**
 * EHR Agent Implementation
 * 
 * This agent specializes in electronic health record (EHR) data handling with HIPAA compliance.
 * It provides secure access to patient data, handles medical record queries, and ensures
 * all operations comply with healthcare privacy and security regulations.
 */

import { BaseAgent } from './base_agent';
import { Message } from '../communication/message';
import { KnowledgeBaseManager } from '../knowledge/knowledge_base_manager';
import { Tool } from '../tools/tool_types';
import { MedicalDataHandler } from '../medical/medical_data_handler';
import { HIPAACompliance } from '../medical/hipaa_compliance';

/**
 * Specialized agent for electronic health record management with HIPAA compliance
 */
export class EHRAgent extends BaseAgent {
  private medicalDataHandler: MedicalDataHandler;
  private hipaaCompliance: HIPAACompliance;
  
  /**
   * Creates a new EHRAgent
   * 
   * @param id - Unique identifier for this agent
   * @param knowledgeBaseManager - The knowledge base manager for accessing domain knowledge
   * @param medicalDataHandler - Handler for medical data operations
   * @param hipaaCompliance - HIPAA compliance management
   */
  constructor(
    id: string, 
    knowledgeBaseManager: KnowledgeBaseManager,
    medicalDataHandler?: MedicalDataHandler,
    hipaaCompliance?: HIPAACompliance
  ) {
    super(id, 'ehr', knowledgeBaseManager);
    
    // Initialize medical data handler with default if not provided
    this.medicalDataHandler = medicalDataHandler || new MedicalDataHandler();
    
    // Initialize HIPAA compliance with default if not provided
    this.hipaaCompliance = hipaaCompliance || new HIPAACompliance();
    
    // Register specialized tools
    this.registerEHRTools();
  }
  
  /**
   * Registers EHR-specific tools
   */
  private registerEHRTools() {
    // Register patient data lookup tool
    this.registerTool({
      id: 'patient_data_lookup',
      name: 'Patient Data Lookup Tool',
      description: 'Securely retrieves patient data with HIPAA compliance',
      execute: async (params: any) => {
        // Validate authorization before proceeding
        const authorized = await this.hipaaCompliance.validateAuthorization(
          params.requesterId,
          params.authToken,
          params.patientId,
          params.dataType
        );
        
        if (!authorized) {
          throw new Error('Unauthorized access to patient data');
        }
        
        // Log the authorized access attempt
        await this.hipaaCompliance.logAccessAttempt({
          requesterId: params.requesterId,
          patientId: params.patientId,
          dataType: params.dataType,
          timestamp: new Date().toISOString(),
          successful: true,
          reason: params.reason || 'Data lookup request'
        });
        
        // Retrieve the data with appropriate filtering
        return this.medicalDataHandler.getPatientData(
          params.patientId,
          params.dataType,
          params.dateRange,
          params.filters
        );
      }
    });
    
    // Register medical record search tool
    this.registerTool({
      id: 'medical_record_search',
      name: 'Medical Record Search Tool',
      description: 'Searches medical records with controlled access and HIPAA compliance',
      execute: async (params: any) => {
        // Validate authorization for search operation
        const authorized = await this.hipaaCompliance.validateAuthorization(
          params.requesterId,
          params.authToken,
          null, // No specific patient ID for search operations
          'search'
        );
        
        if (!authorized) {
          throw new Error('Unauthorized access to search medical records');
        }
        
        // Log the search operation
        await this.hipaaCompliance.logAccessAttempt({
          requesterId: params.requesterId,
          patientId: null,
          dataType: 'search',
          timestamp: new Date().toISOString(),
          successful: true,
          reason: params.reason || 'Medical record search'
        });
        
        // Perform the search with appropriate filtering
        return this.medicalDataHandler.searchMedicalRecords(
          params.query,
          params.filters,
          params.pagination
        );
      }
    });
    
    // Register data access authorization tool
    this.registerTool({
      id: 'data_access_authorization',
      name: 'Data Access Authorization Tool',
      description: 'Validates and manages authorization for medical data access',
      execute: async (params: any) => {
        return this.hipaaCompliance.validateAndAuthorize(
          params.requesterId,
          params.patientId,
          params.dataType,
          params.purpose,
          params.accessDuration
        );
      }
    });
    
    // Register audit log tool
    this.registerTool({
      id: 'audit_log',
      name: 'Audit Log Tool',
      description: 'Retrieves audit logs for HIPAA compliance tracking',
      execute: async (params: any) => {
        // Validate that the requester has permission to view audit logs
        const authorized = await this.hipaaCompliance.canAccessAuditLogs(
          params.requesterId,
          params.authToken
        );
        
        if (!authorized) {
          throw new Error('Unauthorized access to audit logs');
        }
        
        // Retrieve the audit logs
        return this.hipaaCompliance.getAuditLogs(
          params.filters,
          params.dateRange,
          params.pagination
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
      // Log message receipt with careful handling of PHI
      this.logger.info(`EHRAgent received message: ${message.messageType} - ${message.content.query_type}`);
      
      // Verify basic authorization before processing (message-level)
      if (!await this.validateMessageAuthorization(message)) {
        return Message.createErrorResponse(
          message,
          this.id,
          this.type,
          'Unauthorized EHR access request'
        );
      }
      
      // Process based on query type
      switch (message.content.query_type) {
        case 'patient_data_request':
          return this.handlePatientDataRequest(message);
          
        case 'medical_record_search':
          return this.handleMedicalRecordSearch(message);
          
        case 'authorization_request':
          return this.handleAuthorizationRequest(message);
          
        case 'audit_log_request':
          return this.handleAuditLogRequest(message);
          
        case 'hipaa_compliance_check':
          return this.handleComplianceCheck(message);
          
        case 'data_integration_request':
          return this.handleDataIntegrationRequest(message);
          
        case 'multi_domain_analysis':
          return this.handleMultiDomainAnalysis(message);
          
        default:
          // Fall back to base agent processing for generic queries
          return super.processMessage(message);
      }
    } catch (error) {
      // Log error without PHI
      this.logger.error(`Error processing message in EHRAgent: ${error.message}`);
      
      // Create an error response
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Error processing message: ${error.message}`
      );
    }
  }
  
  /**
   * Validates basic authorization for the incoming message
   */
  private async validateMessageAuthorization(message: Message): Promise<boolean> {
    // Skip validation for certain message types
    if (message.messageType === 'system' || message.messageType === 'broadcast') {
      return true;
    }
    
    // Extract authorization information from message metadata
    const authToken = message.metadata?.auth_token;
    const requesterId = message.metadata?.requester_id || message.sender.id;
    
    // For non-patient specific requests, validate basic access rights
    if (!message.content.body?.patient_id) {
      return this.hipaaCompliance.validateBasicAccess(
        requesterId,
        authToken,
        message.content.query_type
      );
    }
    
    // For patient-specific requests, validate authorization
    return this.hipaaCompliance.validateAuthorization(
      requesterId,
      authToken,
      message.content.body.patient_id,
      message.content.query_type
    );
  }
  
  /**
   * Handles patient data requests
   */
  private async handlePatientDataRequest(message: Message): Promise<Message> {
    const { 
      patient_id,
      data_type,
      date_range,
      filters,
      reason
    } = message.content.body;
    
    // Validate required parameters
    if (!patient_id || !data_type) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Patient data request requires patient_id and data_type parameters'
      );
    }
    
    try {
      // Extract request metadata
      const requesterId = message.metadata?.requester_id || message.sender.id;
      const authToken = message.metadata?.auth_token;
      
      // Validate authorization for this specific data access
      const authorized = await this.hipaaCompliance.validateAuthorization(
        requesterId,
        authToken,
        patient_id,
        data_type
      );
      
      if (!authorized) {
        // Log unauthorized access attempt
        await this.hipaaCompliance.logAccessAttempt({
          requesterId,
          patientId: patient_id,
          dataType: data_type,
          timestamp: new Date().toISOString(),
          successful: false,
          reason: reason || 'Patient data request',
          details: 'Authorization validation failed'
        });
        
        return Message.createErrorResponse(
          message,
          this.id,
          this.type,
          'Unauthorized access to patient data'
        );
      }
      
      // Log authorized access
      await this.hipaaCompliance.logAccessAttempt({
        requesterId,
        patientId: patient_id,
        dataType: data_type,
        timestamp: new Date().toISOString(),
        successful: true,
        reason: reason || 'Patient data request'
      });
      
      // Retrieve patient data
      const patientData = await this.medicalDataHandler.getPatientData(
        patient_id,
        data_type,
        date_range,
        filters
      );
      
      // Apply minimum necessary principle to limit returned data
      const filteredData = this.hipaaCompliance.applyMinimumNecessaryPrinciple(
        patientData,
        data_type,
        requesterId,
        reason
      );
      
      // Return the filtered patient data
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { 
          patient_data: filteredData,
          access_metadata: {
            accessed_at: new Date().toISOString(),
            access_level: this.hipaaCompliance.getAccessLevel(requesterId, data_type),
            data_retention: this.hipaaCompliance.getRetentionPolicy(data_type)
          }
        }
      );
    } catch (error) {
      // Log error without PHI
      this.logger.error(`Error in patient data request: ${error.message}`);
      
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Patient data request error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles medical record search requests
   */
  private async handleMedicalRecordSearch(message: Message): Promise<Message> {
    const { 
      query,
      filters,
      pagination,
      reason
    } = message.content.body;
    
    // Validate required parameters
    if (!query) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Medical record search requires a query parameter'
      );
    }
    
    try {
      // Extract request metadata
      const requesterId = message.metadata?.requester_id || message.sender.id;
      const authToken = message.metadata?.auth_token;
      
      // Validate authorization for search capability
      const authorized = await this.hipaaCompliance.validateAuthorization(
        requesterId,
        authToken,
        null, // No specific patient for search
        'search'
      );
      
      if (!authorized) {
        // Log unauthorized search attempt
        await this.hipaaCompliance.logAccessAttempt({
          requesterId,
          patientId: null,
          dataType: 'search',
          timestamp: new Date().toISOString(),
          successful: false,
          reason: reason || 'Medical record search',
          details: 'Authorization validation failed'
        });
        
        return Message.createErrorResponse(
          message,
          this.id,
          this.type,
          'Unauthorized access to search medical records'
        );
      }
      
      // Log authorized search
      await this.hipaaCompliance.logAccessAttempt({
        requesterId,
        patientId: null,
        dataType: 'search',
        timestamp: new Date().toISOString(),
        successful: true,
        reason: reason || 'Medical record search'
      });
      
      // Perform the search
      const searchResults = await this.medicalDataHandler.searchMedicalRecords(
        query,
        filters,
        pagination
      );
      
      // Apply de-identification or filtering based on requester's access level
      const accessLevel = this.hipaaCompliance.getAccessLevel(requesterId, 'search');
      const filteredResults = this.hipaaCompliance.filterSearchResults(
        searchResults,
        accessLevel,
        requesterId
      );
      
      // Return the filtered search results
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { 
          search_results: filteredResults,
          total_matches: searchResults.total,
          pagination: {
            page: pagination?.page || 1,
            page_size: pagination?.page_size || 20,
            total_pages: Math.ceil(searchResults.total / (pagination?.page_size || 20))
          }
        }
      );
    } catch (error) {
      // Log error without PHI
      this.logger.error(`Error in medical record search: ${error.message}`);
      
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Medical record search error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles data access authorization requests
   */
  private async handleAuthorizationRequest(message: Message): Promise<Message> {
    const { 
      patient_id,
      data_type,
      purpose,
      duration
    } = message.content.body;
    
    // Validate required parameters
    if (!patient_id || !data_type || !purpose) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Authorization request requires patient_id, data_type, and purpose parameters'
      );
    }
    
    try {
      // Extract request metadata
      const requesterId = message.metadata?.requester_id || message.sender.id;
      
      // Process authorization request
      const authorizationResult = await this.hipaaCompliance.validateAndAuthorize(
        requesterId,
        patient_id,
        data_type,
        purpose,
        duration || '24h' // Default to 24 hours if not specified
      );
      
      // Log the authorization request
      await this.hipaaCompliance.logAccessAttempt({
        requesterId,
        patientId: patient_id,
        dataType: `authorize-${data_type}`,
        timestamp: new Date().toISOString(),
        successful: authorizationResult.authorized,
        reason: purpose,
        details: authorizationResult.details
      });
      
      // Return the authorization result
      if (authorizationResult.authorized) {
        return Message.createResponse(
          message,
          this.id,
          this.type,
          { 
            authorization: {
              authorized: true,
              auth_token: authorizationResult.auth_token,
              expires_at: authorizationResult.expires_at,
              access_level: authorizationResult.access_level,
              limitations: authorizationResult.limitations
            }
          }
        );
      } else {
        return Message.createResponse(
          message,
          this.id,
          this.type,
          { 
            authorization: {
              authorized: false,
              reason: authorizationResult.details,
              requirements: authorizationResult.requirements
            }
          }
        );
      }
    } catch (error) {
      // Log error without PHI
      this.logger.error(`Error in authorization request: ${error.message}`);
      
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Authorization request error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles audit log requests
   */
  private async handleAuditLogRequest(message: Message): Promise<Message> {
    const { 
      filters,
      date_range,
      pagination
    } = message.content.body;
    
    try {
      // Extract request metadata
      const requesterId = message.metadata?.requester_id || message.sender.id;
      const authToken = message.metadata?.auth_token;
      
      // Validate that the requester has permission to view audit logs
      const authorized = await this.hipaaCompliance.canAccessAuditLogs(
        requesterId,
        authToken
      );
      
      if (!authorized) {
        return Message.createErrorResponse(
          message,
          this.id,
          this.type,
          'Unauthorized access to audit logs'
        );
      }
      
      // Retrieve the audit logs
      const auditLogs = await this.hipaaCompliance.getAuditLogs(
        filters,
        date_range,
        pagination
      );
      
      // Return the audit logs
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { 
          audit_logs: auditLogs.logs,
          total_entries: auditLogs.total,
          pagination: {
            page: pagination?.page || 1,
            page_size: pagination?.page_size || 20,
            total_pages: Math.ceil(auditLogs.total / (pagination?.page_size || 20))
          }
        }
      );
    } catch (error) {
      this.logger.error(`Error in audit log request: ${error.message}`);
      
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Audit log request error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles HIPAA compliance check requests
   */
  private async handleComplianceCheck(message: Message): Promise<Message> {
    const { 
      check_type,
      data,
      system_id
    } = message.content.body;
    
    // Validate required parameters
    if (!check_type) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Compliance check requires a check_type parameter'
      );
    }
    
    try {
      // Extract request metadata
      const requesterId = message.metadata?.requester_id || message.sender.id;
      const authToken = message.metadata?.auth_token;
      
      // Validate authorization for compliance checks
      const authorized = await this.hipaaCompliance.validateBasicAccess(
        requesterId,
        authToken,
        'compliance_check'
      );
      
      if (!authorized) {
        return Message.createErrorResponse(
          message,
          this.id,
          this.type,
          'Unauthorized access to compliance check functionality'
        );
      }
      
      // Perform the appropriate compliance check
      let checkResult;
      
      switch (check_type) {
        case 'data_deidentification':
          checkResult = this.hipaaCompliance.checkDeidentification(data);
          break;
          
        case 'data_encryption':
          checkResult = this.hipaaCompliance.checkEncryption(data, system_id);
          break;
          
        case 'access_controls':
          checkResult = this.hipaaCompliance.checkAccessControls(system_id);
          break;
          
        case 'audit_controls':
          checkResult = this.hipaaCompliance.checkAuditControls(system_id);
          break;
          
        case 'transmission_security':
          checkResult = this.hipaaCompliance.checkTransmissionSecurity(system_id);
          break;
          
        default:
          return Message.createErrorResponse(
            message,
            this.id,
            this.type,
            `Unsupported compliance check type: ${check_type}`
          );
      }
      
      // Return the compliance check results
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { 
          compliance_check: {
            check_type,
            system_id: system_id || 'general',
            compliant: checkResult.compliant,
            details: checkResult.details,
            recommendations: checkResult.recommendations,
            check_date: new Date().toISOString()
          }
        }
      );
    } catch (error) {
      this.logger.error(`Error in compliance check: ${error.message}`);
      
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Compliance check error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles data integration requests
   */
  private async handleDataIntegrationRequest(message: Message): Promise<Message> {
    const { 
      source_system,
      data_type,
      integration_parameters,
      reason
    } = message.content.body;
    
    // Validate required parameters
    if (!source_system || !data_type) {
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        'Data integration request requires source_system and data_type parameters'
      );
    }
    
    try {
      // Extract request metadata
      const requesterId = message.metadata?.requester_id || message.sender.id;
      const authToken = message.metadata?.auth_token;
      
      // Validate authorization for data integration
      const authorized = await this.hipaaCompliance.validateAuthorization(
        requesterId,
        authToken,
        null, // No specific patient for system integration
        'data_integration'
      );
      
      if (!authorized) {
        return Message.createErrorResponse(
          message,
          this.id,
          this.type,
          'Unauthorized access to data integration functionality'
        );
      }
      
      // Log the integration request
      await this.hipaaCompliance.logAccessAttempt({
        requesterId,
        patientId: null,
        dataType: `integrate-${data_type}`,
        timestamp: new Date().toISOString(),
        successful: true,
        reason: reason || 'Data integration request',
        details: `Source system: ${source_system}`
      });
      
      // Perform the data integration
      const integrationResult = await this.medicalDataHandler.integrateData(
        source_system,
        data_type,
        integration_parameters
      );
      
      // Return the integration results
      return Message.createResponse(
        message,
        this.id,
        this.type,
        { 
          integration_result: {
            success: integrationResult.success,
            records_processed: integrationResult.records_processed,
            records_integrated: integrationResult.records_integrated,
            errors: integrationResult.errors,
            warnings: integrationResult.warnings,
            integration_id: integrationResult.integration_id,
            completion_time: integrationResult.completion_time
          }
        }
      );
    } catch (error) {
      this.logger.error(`Error in data integration request: ${error.message}`);
      
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Data integration error: ${error.message}`
      );
    }
  }
  
  /**
   * Handles multi-domain analysis requests
   */
  private async handleMultiDomainAnalysis(message: Message): Promise<Message> {
    try {
      // For multi-domain queries, we only provide relevant healthcare insights
      // without exposing PHI or sensitive medical data
      
      // Extract relevant analysis topics
      const { 
        question, 
        domains = [], 
        sectors = [] 
      } = message.content.body;
      
      // Determine if healthcare domain is requested
      const healthcareDomain = domains.some(d => 
        ['healthcare', 'medical', 'health', 'ehr'].includes(d.toLowerCase())
      ) || sectors.some(s => 
        ['healthcare', 'medical', 'health', 'hospital'].includes(s.toLowerCase())
      );
      
      if (!healthcareDomain) {
        // If healthcare isn't specifically requested, provide minimal generic response
        return Message.createResponse(
          message,
          this.id,
          this.type,
          {
            healthcare_impact: {
              general_insights: "Healthcare considerations may be relevant but weren't specifically requested in this analysis."
            }
          }
        );
      }
      
      // For healthcare domain analysis, provide general insights without PHI
      const healthcareAnalysis = {
        healthcare_impact: {
          sector_overview: "The healthcare sector operates under strict regulatory frameworks including HIPAA that govern data privacy and security.",
          data_considerations: "Healthcare data requires special handling with robust security, encryption, access controls, and audit mechanisms.",
          compliance_requirements: "Any systems handling healthcare data must implement physical, technical, and administrative safeguards.",
          integration_challenges: "Healthcare system integration requires careful planning to maintain data integrity and security."
        }
      };
      
      // Check if the question mentions specific healthcare topics
      const lowercaseQuestion = question.toLowerCase();
      
      if (lowercaseQuestion.includes('hipaa') || lowercaseQuestion.includes('compliance')) {
        healthcareAnalysis.healthcare_impact.compliance_focus = "HIPAA compliance requires risk analysis, managed access controls, training, incident procedures, and business associate agreements.";
      }
      
      if (lowercaseQuestion.includes('security') || lowercaseQuestion.includes('privacy')) {
        healthcareAnalysis.healthcare_impact.security_considerations = "Healthcare security best practices include encryption, access controls, regular audits, secure transmission, and continuous monitoring.";
      }
      
      if (lowercaseQuestion.includes('interoperability') || lowercaseQuestion.includes('integration')) {
        healthcareAnalysis.healthcare_impact.interoperability_insights = "Healthcare data interoperability is enhanced through standards like HL7, FHIR, and structured data formats while maintaining security.";
      }
      
      // Return the healthcare analysis
      return Message.createResponse(
        message,
        this.id,
        this.type,
        healthcareAnalysis
      );
    } catch (error) {
      this.logger.error(`Error in multi-domain analysis: ${error.message}`);
      
      return Message.createErrorResponse(
        message,
        this.id,
        this.type,
        `Multi-domain analysis error: ${error.message}`
      );
    }
  }
}