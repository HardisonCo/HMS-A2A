import { ref } from 'vue'
import { useApiClient } from './useApiClient'

/**
 * Composable for interacting with the Federation API
 * 
 * @returns {Object} API methods for federated data
 */
export function useFederationApi() {
  const { apiClient, isLoading: apiLoading, error: apiError } = useApiClient()
  
  // State
  const isLoading = ref(false)
  const error = ref(null)
  
  /**
   * Get federated data from multiple agencies
   * 
   * @param {Object} params - Query parameters
   * @param {Array} params.agencies - List of agency identifiers ('aphis', 'cdc', 'epa', 'fema')
   * @param {Object} params.filters - Optional filters
   * @param {string} params.filters.startDate - Optional start date (ISO format)
   * @param {string} params.filters.endDate - Optional end date (ISO format)
   * @param {string} params.filters.region - Optional region filter
   * @param {string} params.filters.subtype - Optional virus subtype filter
   * @param {string} params.filters.severity - Optional severity level filter
   * @returns {Promise<Object>} Federated dashboard data
   */
  async function getFederatedData(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { agencies, filters = {} } = params
      
      // Build query parameters
      const queryParams = {
        agencies: agencies.join(',')
      }
      
      if (filters.startDate) queryParams.start_date = filters.startDate
      if (filters.endDate) queryParams.end_date = filters.endDate
      if (filters.region) queryParams.region = filters.region
      if (filters.subtype) queryParams.subtype = filters.subtype
      if (filters.severity) queryParams.severity = filters.severity
      
      const response = await apiClient.get('/api/federation/dashboard', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get federated data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get federated map data from multiple agencies
   * 
   * @param {Object} params - Query parameters
   * @param {Array} params.agencies - List of agency identifiers ('aphis', 'cdc', 'epa', 'fema')
   * @param {Object} params.filters - Optional filters
   * @returns {Promise<Array>} Federated outbreak location data
   */
  async function getFederatedMapData(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { agencies, filters = {} } = params
      
      // Build query parameters
      const queryParams = {
        agencies: agencies.join(',')
      }
      
      if (filters.startDate) queryParams.start_date = filters.startDate
      if (filters.endDate) queryParams.end_date = filters.endDate
      if (filters.region) queryParams.region = filters.region
      if (filters.subtype) queryParams.subtype = filters.subtype
      if (filters.severity) queryParams.severity = filters.severity
      
      const response = await apiClient.get('/api/federation/map', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get federated map data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get federated genetic data from multiple agencies
   * 
   * @param {Object} params - Query parameters
   * @param {Array} params.agencies - List of agency identifiers ('aphis', 'cdc', 'epa', 'fema')
   * @param {string} params.subtype - Virus subtype
   * @param {Object} params.filters - Optional filters
   * @returns {Promise<Object>} Federated genetic data
   */
  async function getFederatedGeneticData(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { agencies, subtype, filters = {} } = params
      
      // Build query parameters
      const queryParams = {
        agencies: agencies.join(','),
        subtype
      }
      
      if (filters.startDate) queryParams.start_date = filters.startDate
      if (filters.endDate) queryParams.end_date = filters.endDate
      if (filters.region) queryParams.region = filters.region
      
      const response = await apiClient.get('/api/federation/genetic', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get federated genetic data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get federated cases from multiple agencies
   * 
   * @param {Object} params - Query parameters
   * @param {Array} params.agencies - List of agency identifiers ('aphis', 'cdc', 'epa', 'fema')
   * @param {Object} params.filters - Optional filters
   * @returns {Promise<Array>} Federated case data
   */
  async function getFederatedCases(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { agencies, filters = {} } = params
      
      // Build query parameters
      const queryParams = {
        agencies: agencies.join(',')
      }
      
      if (filters.startDate) queryParams.start_date = filters.startDate
      if (filters.endDate) queryParams.end_date = filters.endDate
      if (filters.region) queryParams.region = filters.region
      if (filters.subtype) queryParams.subtype = filters.subtype
      if (filters.severity) queryParams.severity = filters.severity
      
      const response = await apiClient.get('/api/federation/cases', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get federated cases'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get federated alerts from multiple agencies
   * 
   * @param {Object} params - Query parameters
   * @param {Array} params.agencies - List of agency identifiers ('aphis', 'cdc', 'epa', 'fema')
   * @param {Object} params.filters - Optional filters
   * @returns {Promise<Array>} Federated alert data
   */
  async function getFederatedAlerts(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { agencies, filters = {} } = params
      
      // Build query parameters
      const queryParams = {
        agencies: agencies.join(',')
      }
      
      if (filters.severity) queryParams.severity = filters.severity
      if (filters.type) queryParams.type = filters.type
      if (filters.activeOnly !== undefined) queryParams.active_only = filters.activeOnly
      
      const response = await apiClient.get('/api/federation/alerts', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get federated alerts'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get available agencies for federation
   * 
   * @returns {Promise<Array>} List of available agencies with their capabilities
   */
  async function getAvailableAgencies() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/api/federation/agencies')
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get available agencies'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Test federation connectivity with an agency
   * 
   * @param {string} agencyId - Agency identifier
   * @returns {Promise<Object>} Connectivity test result
   */
  async function testFederationConnectivity(agencyId) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get(`/api/federation/test/${agencyId}`)
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to test federation connectivity'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    getFederatedData,
    getFederatedMapData,
    getFederatedGeneticData,
    getFederatedCases,
    getFederatedAlerts,
    getAvailableAgencies,
    testFederationConnectivity,
    isLoading,
    error
  }
}