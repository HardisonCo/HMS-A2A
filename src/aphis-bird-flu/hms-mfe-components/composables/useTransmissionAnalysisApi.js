import { ref } from 'vue'
import { useApiClient } from './useApiClient'

/**
 * Composable for interacting with the Transmission Analysis API
 * 
 * @returns {Object} API methods for transmission analysis
 */
export function useTransmissionAnalysisApi() {
  const { apiClient, isLoading: apiLoading, error: apiError } = useApiClient()
  
  // State
  const isLoading = ref(false)
  const error = ref(null)
  
  /**
   * Analyze transmission network from cases
   * 
   * @param {Object} params - Analysis parameters
   * @param {number} params.temporalWindow - Maximum time window for links (days)
   * @param {number} params.spatialThreshold - Maximum distance for links (km)
   * @param {number} params.geneticThreshold - Maximum genetic distance (0-1)
   * @param {Array} [params.caseIds] - Optional case IDs to include (all cases if empty)
   * @returns {Promise<Object>} Comprehensive transmission analysis
   */
  async function analyzeTransmission(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { temporalWindow, spatialThreshold, geneticThreshold, caseIds } = params
      
      const response = await apiClient.post(
        '/api/genetic/transmission-dynamics',
        {
          temporal_window: temporalWindow,
          spatial_threshold: spatialThreshold,
          genetic_threshold: geneticThreshold,
          case_ids: caseIds || []
        }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to analyze transmission network'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Infer transmission network from cases
   * 
   * @param {Object} params - Analysis parameters
   * @param {Array} params.cases - List of case objects
   * @param {number} params.geneticThreshold - Maximum genetic distance (0-1)
   * @param {number} params.temporalWindow - Maximum time window (days)
   * @param {number} params.spatialThreshold - Maximum distance (km)
   * @returns {Promise<Object>} Transmission network
   */
  async function inferTransmissionNetwork(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { cases, geneticThreshold, temporalWindow, spatialThreshold } = params
      
      const response = await apiClient.post(
        '/api/genetic/transmission-network',
        {
          cases,
          genetic_threshold: geneticThreshold,
          temporal_window: temporalWindow,
          spatial_threshold: spatialThreshold
        }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to infer transmission network'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Assess transmission pattern from network
   * 
   * @param {Object} params - Analysis parameters
   * @param {Object} params.network - Transmission network from inferTransmissionNetwork
   * @returns {Promise<Object>} Pattern assessment
   */
  async function assessTransmissionPattern(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { network } = params
      
      const response = await apiClient.post(
        '/api/genetic/transmission-pattern',
        { network }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to assess transmission pattern'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Predict spread trajectory
   * 
   * @param {Object} params - Analysis parameters
   * @param {Object} params.network - Transmission network
   * @param {Array} params.cases - List of cases
   * @param {number} params.daysAhead - Days to predict ahead
   * @returns {Promise<Object>} Spread trajectory prediction
   */
  async function predictSpreadTrajectory(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { network, cases, daysAhead = 14 } = params
      
      const response = await apiClient.post(
        '/api/genetic/spread-trajectory',
        {
          network,
          cases,
          days_ahead: daysAhead
        }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to predict spread trajectory'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get case data for a specific region and date range
   * 
   * @param {Object} params - Query parameters
   * @param {string} params.region - Geographic region
   * @param {string} params.startDate - Start date (ISO format)
   * @param {string} params.endDate - End date (ISO format)
   * @returns {Promise<Array>} List of cases
   */
  async function getCaseData(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { region, startDate, endDate } = params
      
      const response = await apiClient.get(
        '/api/cases',
        {
          params: {
            region,
            start_date: startDate,
            end_date: endDate
          }
        }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get case data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get transmission clusters
   * 
   * @param {Object} params - Query parameters
   * @param {string} params.region - Optional geographic region filter
   * @param {string} params.startDate - Optional start date filter (ISO format)
   * @param {string} params.endDate - Optional end date filter (ISO format)
   * @param {number} params.minSize - Optional minimum cluster size
   * @returns {Promise<Array>} List of transmission clusters
   */
  async function getTransmissionClusters(params = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      const { region, startDate, endDate, minSize } = params
      
      const queryParams = {}
      if (region) queryParams.region = region
      if (startDate) queryParams.start_date = startDate
      if (endDate) queryParams.end_date = endDate
      if (minSize) queryParams.min_size = minSize
      
      const response = await apiClient.get(
        '/api/genetic/transmission-clusters',
        { params: queryParams }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get transmission clusters'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get mock data for demo purposes
   * 
   * @returns {Promise<Object>} Mock transmission data
   */
  async function getMockTransmissionData() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/api/genetic/mock-transmission-data')
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get mock transmission data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    analyzeTransmission,
    inferTransmissionNetwork,
    assessTransmissionPattern,
    predictSpreadTrajectory,
    getCaseData,
    getTransmissionClusters,
    getMockTransmissionData,
    isLoading,
    error
  }
}