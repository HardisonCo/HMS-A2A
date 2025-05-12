/**
 * Protocol Service
 * 
 * Handles protocol management, transformation, and integration with
 * CBER/CDER AI modules for the HMS-GOV frontend.
 */
class ProtocolService {
  /**
   * Create a new Protocol Service instance
   * 
   * @param {Object} options - Configuration options
   * @param {string} options.apiBaseUrl - Base URL for the HMS-GOV API
   * @param {string} options.hpcApiBaseUrl - Base URL for the HPC API
   * @param {string} options.cberAiEndpoint - Endpoint for CBER.ai API
   * @param {string} options.cderAiEndpoint - Endpoint for CDER.ai API
   * @param {Object} options.authService - Authentication service instance
   */
  constructor(options = {}) {
    this.apiBaseUrl = options.apiBaseUrl || '/api';
    this.hpcApiBaseUrl = options.hpcApiBaseUrl || '/api/hpc';
    this.cberAiEndpoint = options.cberAiEndpoint || 'https://cber.ai/api/v2';
    this.cderAiEndpoint = options.cderAiEndpoint || 'https://cder.ai/api/v1';
    this.authService = options.authService;
    
    // AI module configuration
    this.aiModules = {
      cber: {
        enabled: true,
        version: '2.1',
        endpoints: {
          modelService: `${this.cberAiEndpoint}/models`,
          predictionService: `${this.cberAiEndpoint}/predict`,
          trainingService: `${this.cberAiEndpoint}/train`
        },
        capabilities: [
          'biologicsQualityPrediction',
          'immunogenicityAnalysis',
          'processDevelopmentOptimization',
          'stabilityPrediction',
          'comparabilityAssessment'
        ]
      },
      cder: {
        enabled: true,
        version: '1.8',
        endpoints: {
          modelService: `${this.cderAiEndpoint}/models`,
          predictionService: `${this.cderAiEndpoint}/predict`,
          trainingService: `${this.cderAiEndpoint}/train`
        },
        capabilities: [
          'drugInteractionPrediction',
          'adverseEventPrediction',
          'pharmacokineticModeling',
          'doseOptimization',
          'efficacyPrediction'
        ]
      }
    };
  }
  
  /**
   * Get protocol headers for authenticated requests
   * 
   * @returns {Object} Headers object
   * @private
   */
  _getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    
    if (this.authService && this.authService.getToken) {
      headers['Authorization'] = `Bearer ${this.authService.getToken()}`;
    }
    
    return headers;
  }
  
  /**
   * Get all protocols
   * 
   * @param {Object} filters - Optional filters
   * @returns {Promise<Array>} Array of protocols
   */
  async getProtocols(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      queryParams.append(key, value);
    });
    
    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
    
    const response = await fetch(`${this.apiBaseUrl}/protocols${queryString}`, {
      method: 'GET',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching protocols: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || [];
  }
  
  /**
   * Get a specific protocol
   * 
   * @param {string|number} id - Protocol ID
   * @returns {Promise<Object>} Protocol data
   */
  async getProtocol(id) {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${id}`, {
      method: 'GET',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching protocol: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Create a new protocol
   * 
   * @param {Object} protocolData - Protocol data
   * @returns {Promise<Object>} Created protocol
   */
  async createProtocol(protocolData) {
    const response = await fetch(`${this.apiBaseUrl}/protocols`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify(protocolData)
    });
    
    if (!response.ok) {
      throw new Error(`Error creating protocol: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Update a protocol
   * 
   * @param {string|number} id - Protocol ID
   * @param {Object} protocolData - Protocol data
   * @returns {Promise<Object>} Updated protocol
   */
  async updateProtocol(id, protocolData) {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${id}`, {
      method: 'PUT',
      headers: this._getHeaders(),
      body: JSON.stringify(protocolData)
    });
    
    if (!response.ok) {
      throw new Error(`Error updating protocol: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Delete a protocol
   * 
   * @param {string|number} id - Protocol ID
   * @returns {Promise<boolean>} Success status
   */
  async deleteProtocol(id) {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${id}`, {
      method: 'DELETE',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error deleting protocol: ${response.statusText}`);
    }
    
    return true;
  }
  
  /**
   * Submit a protocol to HPC for processing
   * 
   * @param {string|number} id - Protocol ID
   * @param {Object} hpcOptions - HPC options
   * @returns {Promise<Object>} HPC job data
   */
  async submitProtocolToHPC(id, hpcOptions = {}) {
    const response = await fetch(`${this.hpcApiBaseUrl}/protocols/${id}/submit`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify({ hpcOptions })
    });
    
    if (!response.ok) {
      throw new Error(`Error submitting protocol to HPC: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Get HPC job status
   * 
   * @param {string} jobId - HPC job ID
   * @returns {Promise<Object>} Job status
   */
  async getHPCJobStatus(jobId) {
    const response = await fetch(`${this.hpcApiBaseUrl}/jobs/${jobId}`, {
      method: 'GET',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching HPC job status: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Cancel HPC job
   * 
   * @param {string} jobId - HPC job ID
   * @returns {Promise<boolean>} Success status
   */
  async cancelHPCJob(jobId) {
    const response = await fetch(`${this.hpcApiBaseUrl}/jobs/${jobId}`, {
      method: 'DELETE',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error cancelling HPC job: ${response.statusText}`);
    }
    
    return true;
  }
  
  /**
   * Initialize multi-institution data sharing
   * 
   * @param {string|number} id - Protocol ID
   * @param {Array} institutions - List of participating institutions
   * @returns {Promise<Object>} Data sharing initialization result
   */
  async initializeDataSharing(id, institutions) {
    const response = await fetch(`${this.hpcApiBaseUrl}/protocols/${id}/data-sharing`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify({ institutions })
    });
    
    if (!response.ok) {
      throw new Error(`Error initializing data sharing: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Configure AI module for a protocol
   * 
   * @param {string|number} id - Protocol ID
   * @param {string} aiModuleType - AI module type (cber.ai or cder.ai)
   * @param {Object} aiConfig - AI module configuration
   * @returns {Promise<Object>} AI module configuration result
   */
  async configureAIModule(id, aiModuleType, aiConfig = {}) {
    if (!['cber.ai', 'cder.ai'].includes(aiModuleType)) {
      throw new Error(`Invalid AI module type: ${aiModuleType}. Must be cber.ai or cder.ai.`);
    }
    
    const response = await fetch(`${this.hpcApiBaseUrl}/protocols/${id}/ai-module`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify({ aiModuleType, aiConfig })
    });
    
    if (!response.ok) {
      throw new Error(`Error configuring AI module: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Get available models from a specific AI module
   * 
   * @param {string} aiModuleType - AI module type (cber or cder)
   * @param {Object} filters - Optional filters
   * @returns {Promise<Array>} Available models
   */
  async getAIModels(aiModuleType, filters = {}) {
    if (!['cber', 'cder'].includes(aiModuleType)) {
      throw new Error(`Invalid AI module type: ${aiModuleType}. Must be cber or cder.`);
    }
    
    const moduleConfig = this.aiModules[aiModuleType];
    if (!moduleConfig || !moduleConfig.enabled) {
      throw new Error(`AI module ${aiModuleType} is not enabled or configured.`);
    }
    
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      queryParams.append(key, value);
    });
    
    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
    
    // Use fetch with CORS proxying via the backend
    const response = await fetch(`${this.apiBaseUrl}/ai-proxy/${aiModuleType}/models${queryString}`, {
      method: 'GET',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching AI models: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.models || [];
  }
  
  /**
   * Run a prediction using an AI model
   * 
   * @param {string} aiModuleType - AI module type (cber or cder)
   * @param {string} modelId - Model ID
   * @param {Object} inputData - Input data for prediction
   * @returns {Promise<Object>} Prediction result
   */
  async runPrediction(aiModuleType, modelId, inputData) {
    if (!['cber', 'cder'].includes(aiModuleType)) {
      throw new Error(`Invalid AI module type: ${aiModuleType}. Must be cber or cder.`);
    }
    
    const moduleConfig = this.aiModules[aiModuleType];
    if (!moduleConfig || !moduleConfig.enabled) {
      throw new Error(`AI module ${aiModuleType} is not enabled or configured.`);
    }
    
    // Use fetch with CORS proxying via the backend
    const response = await fetch(`${this.apiBaseUrl}/ai-proxy/${aiModuleType}/predict`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify({
        modelId,
        inputData
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error running prediction: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.prediction || {};
  }
  
  /**
   * Start model training for a protocol using AI module
   * 
   * @param {string|number} protocolId - Protocol ID
   * @param {string} aiModuleType - AI module type (cber or cder)
   * @param {Object} trainingConfig - Training configuration
   * @returns {Promise<Object>} Training job data
   */
  async startModelTraining(protocolId, aiModuleType, trainingConfig = {}) {
    if (!['cber', 'cder'].includes(aiModuleType)) {
      throw new Error(`Invalid AI module type: ${aiModuleType}. Must be cber or cder.`);
    }
    
    const moduleConfig = this.aiModules[aiModuleType];
    if (!moduleConfig || !moduleConfig.enabled) {
      throw new Error(`AI module ${aiModuleType} is not enabled or configured.`);
    }
    
    // Training is a long-running task, so we submit it through the HPC integration
    const response = await fetch(`${this.apiBaseUrl}/protocols/${protocolId}/ai-training`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify({
        aiModuleType: `${aiModuleType}.ai`,
        trainingConfig
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error starting model training: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Get IBD-specific protocol information
   * 
   * @param {string|number} protocolId - Protocol ID
   * @returns {Promise<Object>} IBD protocol data
   */
  async getIBDProtocolInfo(protocolId) {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${protocolId}/ibd-info`, {
      method: 'GET',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching IBD protocol info: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Update IBD-specific protocol settings
   * 
   * @param {string|number} protocolId - Protocol ID
   * @param {Object} ibdSettings - IBD-specific settings
   * @returns {Promise<Object>} Updated IBD protocol data
   */
  async updateIBDProtocolSettings(protocolId, ibdSettings) {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${protocolId}/ibd-settings`, {
      method: 'PUT',
      headers: this._getHeaders(),
      body: JSON.stringify(ibdSettings)
    });
    
    if (!response.ok) {
      throw new Error(`Error updating IBD protocol settings: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Get biomarker thresholds for a protocol
   * 
   * @param {string|number} protocolId - Protocol ID
   * @returns {Promise<Object>} Biomarker thresholds
   */
  async getBiomarkerThresholds(protocolId) {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${protocolId}/biomarker-thresholds`, {
      method: 'GET',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching biomarker thresholds: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Update biomarker thresholds for a protocol
   * 
   * @param {string|number} protocolId - Protocol ID
   * @param {Object} thresholds - Biomarker thresholds
   * @returns {Promise<Object>} Updated biomarker thresholds
   */
  async updateBiomarkerThresholds(protocolId, thresholds) {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${protocolId}/biomarker-thresholds`, {
      method: 'PUT',
      headers: this._getHeaders(),
      body: JSON.stringify({ thresholds })
    });
    
    if (!response.ok) {
      throw new Error(`Error updating biomarker thresholds: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Get protocol visualization data
   * 
   * @param {string|number} protocolId - Protocol ID
   * @param {string} visualizationType - Type of visualization
   * @returns {Promise<Object>} Visualization data
   */
  async getProtocolVisualization(protocolId, visualizationType = 'timeline') {
    const response = await fetch(`${this.apiBaseUrl}/protocols/${protocolId}/visualizations/${visualizationType}`, {
      method: 'GET',
      headers: this._getHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Error fetching protocol visualization: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || {};
  }
  
  /**
   * Check if a protocol has HPC capabilities
   * 
   * @param {Object} protocol - Protocol object
   * @returns {boolean} True if protocol has HPC capabilities
   */
  hasHPCCapabilities(protocol) {
    if (!protocol) return false;
    
    // Check for HPC keywords in protocol name or category
    const name = (protocol.name || '').toLowerCase();
    const category = (protocol.category?.name || '').toLowerCase();
    
    return name.includes('hpc') || 
           category.includes('hpc') || 
           (protocol.hpcIntegration && protocol.hpcIntegration.enabled === true);
  }
  
  /**
   * Check if a protocol is IBD-specific
   * 
   * @param {Object} protocol - Protocol object
   * @returns {boolean} True if protocol is IBD-specific
   */
  isIBDProtocol(protocol) {
    if (!protocol) return false;
    
    // Check for IBD keywords in protocol name or category
    const name = (protocol.name || '').toLowerCase();
    const category = (protocol.category?.name || '').toLowerCase();
    
    return name.includes('ibd') || 
           name.includes('crohn') || 
           name.includes('colitis') || 
           category.includes('ibd') || 
           category.includes('crohn');
  }
  
  /**
   * Check which AI module type is appropriate for a protocol
   * 
   * @param {Object} protocol - Protocol object
   * @returns {string|null} AI module type (cber, cder, or null)
   */
  getAppropriateAIModule(protocol) {
    if (!protocol) return null;
    
    // Check for CBER/CDER keywords in protocol name or category
    const name = (protocol.name || '').toLowerCase();
    const category = (protocol.category?.name || '').toLowerCase();
    
    if (name.includes('cber') || 
        name.includes('biologic') || 
        category.includes('cber') || 
        category.includes('biologic')) {
      return 'cber';
    }
    
    if (name.includes('cder') || 
        name.includes('pharma') || 
        name.includes('drug') || 
        category.includes('cder') || 
        category.includes('pharma')) {
      return 'cder';
    }
    
    // If protocol configuration has a specific AI module defined
    if (protocol.configuration && protocol.configuration.aiModule) {
      const moduleType = protocol.configuration.aiModule.type;
      if (moduleType === 'cber.ai') return 'cber';
      if (moduleType === 'cder.ai') return 'cder';
    }
    
    return null;
  }
  
  /**
   * Generate protocol AI insights
   * 
   * @param {Object} protocol - Protocol object
   * @returns {Promise<Object>} AI insights
   */
  async generateAIInsights(protocol) {
    const aiModuleType = this.getAppropriateAIModule(protocol);
    if (!aiModuleType) {
      throw new Error('No appropriate AI module found for this protocol');
    }
    
    const endpointPrefix = aiModuleType === 'cber' ? this.cberAiEndpoint : this.cderAiEndpoint;
    
    // Use CORS proxying through our backend
    const response = await fetch(`${this.apiBaseUrl}/ai-proxy/${aiModuleType}/insights`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify({
        protocol: {
          id: protocol.id,
          type: protocol.type,
          diseaseArea: protocol.diseaseArea || 'ibd',
          biomarkers: this.extractBiomarkers(protocol),
          endpoints: this.extractEndpoints(protocol)
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error generating AI insights: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.insights || {};
  }
  
  /**
   * Extract biomarkers from a protocol
   * 
   * @param {Object} protocol - Protocol object
   * @returns {Array} Array of biomarkers
   * @private
   */
  extractBiomarkers(protocol) {
    if (!protocol) return [];
    
    // Try to extract from different places in the protocol structure
    if (protocol.arms && Array.isArray(protocol.arms)) {
      // Extract biomarkers from arms
      const biomarkers = [];
      protocol.arms.forEach(arm => {
        if (arm.biomarkerStratification && Array.isArray(arm.biomarkerStratification)) {
          arm.biomarkerStratification.forEach(b => {
            // Only add unique biomarkers
            if (!biomarkers.find(existing => existing.name === b.biomarker)) {
              biomarkers.push({
                name: b.biomarker,
                criteria: b.criteria,
                category: b.category || 'unknown'
              });
            }
          });
        }
      });
      
      if (biomarkers.length > 0) {
        return biomarkers;
      }
    }
    
    // Try configuration biomarker thresholds
    if (protocol.configuration && protocol.configuration.biomarkerThresholds) {
      return Object.entries(protocol.configuration.biomarkerThresholds).map(([name, threshold]) => ({
        name,
        criteria: `>${threshold}`,
        category: this.guessBiomarkerCategory(name)
      }));
    }
    
    // Default IBD biomarkers if this is an IBD protocol
    if (this.isIBDProtocol(protocol)) {
      return [
        { name: 'fecal_calprotectin', criteria: '>250', category: 'inflammation' },
        { name: 'CRP', criteria: '>5', category: 'inflammation' },
        { name: 'CDAI', criteria: '≥220', category: 'clinical_activity' },
        { name: 'HBI', criteria: '≥7', category: 'clinical_activity' }
      ];
    }
    
    return [];
  }
  
  /**
   * Extract endpoints from a protocol
   * 
   * @param {Object} protocol - Protocol object
   * @returns {Object} Endpoints object
   * @private
   */
  extractEndpoints(protocol) {
    if (!protocol) return { primary: [], secondary: [] };
    
    // Try to extract from different places in the protocol structure
    if (protocol.primaryEndpoints || protocol.secondaryEndpoints) {
      return {
        primary: protocol.primaryEndpoints || [],
        secondary: protocol.secondaryEndpoints || []
      };
    }
    
    // Try from configuration
    if (protocol.configuration && protocol.configuration.endpointDefinitions) {
      return {
        primary: [protocol.configuration.endpointDefinitions.primaryEndpoint],
        secondary: protocol.configuration.endpointDefinitions.secondaryEndpoints || []
      };
    }
    
    // Default IBD endpoints if this is an IBD protocol
    if (this.isIBDProtocol(protocol)) {
      return {
        primary: ['clinical_remission_week_16'],
        secondary: [
          'mucosal_healing_week_16',
          'corticosteroid_free_remission_week_24',
          'fecal_calprotectin_normalization_week_8'
        ]
      };
    }
    
    return { primary: [], secondary: [] };
  }
  
  /**
   * Guess biomarker category based on name
   * 
   * @param {string} name - Biomarker name
   * @returns {string} Category
   * @private
   */
  guessBiomarkerCategory(name) {
    name = name.toLowerCase();
    
    if (name.includes('calprotectin') || 
        name.includes('lactoferrin') || 
        name === 'crp' || 
        name.includes('esr')) {
      return 'inflammation';
    }
    
    if (name === 'cdai' || name === 'hbi' || name.includes('score')) {
      return 'clinical_activity';
    }
    
    if (name.includes('il-') || 
        name.includes('il_') || 
        name.includes('tnf') || 
        name.includes('interferon')) {
      return 'cytokine';
    }
    
    if (name.includes('asca') || name.includes('anca')) {
      return 'serological';
    }
    
    if (name.includes('nod2') || 
        name.includes('atg16l1') || 
        name.includes('il23r')) {
      return 'genetic';
    }
    
    return 'unknown';
  }
}

// Export for both CommonJS and ES modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProtocolService;
} else {
  window.ProtocolService = ProtocolService;
}