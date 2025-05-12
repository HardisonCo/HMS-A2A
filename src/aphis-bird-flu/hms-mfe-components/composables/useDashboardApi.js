import { ref } from 'vue'
import { useApiClient } from './useApiClient'

/**
 * Composable for interacting with the Dashboard API
 * 
 * @returns {Object} API methods for dashboard data
 */
export function useDashboardApi() {
  const { apiClient, isLoading: apiLoading, error: apiError } = useApiClient()
  
  // State
  const isLoading = ref(false)
  const error = ref(null)
  
  /**
   * Get dashboard data
   * 
   * @param {Object} filters - Optional filters
   * @param {string} filters.startDate - Optional start date (ISO format)
   * @param {string} filters.endDate - Optional end date (ISO format)
   * @param {string} filters.region - Optional region filter
   * @param {string} filters.subtype - Optional virus subtype filter
   * @param {string} filters.severity - Optional severity level filter
   * @returns {Promise<Object>} Dashboard data
   */
  async function getDashboardData(filters = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      const { startDate, endDate, region, subtype, severity } = filters
      
      // Build query parameters
      const params = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      if (region) params.region = region
      if (subtype) params.subtype = subtype
      if (severity) params.severity = severity
      
      const response = await apiClient.get('/api/dashboard', { params })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get dashboard data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get outbreak map data
   * 
   * @param {Object} filters - Optional filters
   * @param {string} filters.startDate - Optional start date (ISO format)
   * @param {string} filters.endDate - Optional end date (ISO format)
   * @param {string} filters.region - Optional region filter
   * @param {string} filters.subtype - Optional virus subtype filter
   * @param {string} filters.severity - Optional severity level filter
   * @returns {Promise<Array>} Outbreak location data
   */
  async function getOutbreakMapData(filters = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      const { startDate, endDate, region, subtype, severity } = filters
      
      // Build query parameters
      const params = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      if (region) params.region = region
      if (subtype) params.subtype = subtype
      if (severity) params.severity = severity
      
      const response = await apiClient.get('/api/dashboard/map', { params })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get outbreak map data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get trend data for a specific time period
   * 
   * @param {Object} params - Query parameters
   * @param {string} params.period - Time period (daily, weekly, monthly)
   * @param {string} params.startDate - Start date (ISO format)
   * @param {string} params.endDate - End date (ISO format)
   * @param {string} params.region - Optional region filter
   * @param {string} params.subtype - Optional virus subtype filter
   * @returns {Promise<Array>} Trend data
   */
  async function getTrendData(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { period, startDate, endDate, region, subtype } = params
      
      // Build query parameters
      const queryParams = {
        period,
        start_date: startDate,
        end_date: endDate
      }
      
      if (region) queryParams.region = region
      if (subtype) queryParams.subtype = subtype
      
      const response = await apiClient.get('/api/dashboard/trends', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get trend data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get alerts
   * 
   * @param {Object} params - Query parameters
   * @param {string} params.severity - Optional severity filter (all, high, medium, low)
   * @param {string} params.type - Optional alert type filter (outbreak, genetic, zoonotic, transmission)
   * @param {boolean} params.activeOnly - Whether to include only active alerts
   * @returns {Promise<Array>} Alerts
   */
  async function getAlerts(params = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      const { severity, type, activeOnly } = params
      
      // Build query parameters
      const queryParams = {}
      if (severity) queryParams.severity = severity
      if (type) queryParams.type = type
      if (activeOnly !== undefined) queryParams.active_only = activeOnly
      
      const response = await apiClient.get('/api/dashboard/alerts', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get alerts'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get recent outbreaks
   * 
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Maximum number of outbreaks to return
   * @param {string} params.region - Optional region filter
   * @param {string} params.subtype - Optional virus subtype filter
   * @returns {Promise<Array>} Recent outbreaks
   */
  async function getRecentOutbreaks(params = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      const { limit = 10, region, subtype } = params
      
      // Build query parameters
      const queryParams = { limit }
      if (region) queryParams.region = region
      if (subtype) queryParams.subtype = subtype
      
      const response = await apiClient.get('/api/dashboard/recent', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get recent outbreaks'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get virus subtype distribution
   * 
   * @param {Object} params - Query parameters
   * @param {string} params.startDate - Optional start date (ISO format)
   * @param {string} params.endDate - Optional end date (ISO format)
   * @param {string} params.region - Optional region filter
   * @returns {Promise<Array>} Subtype distribution data
   */
  async function getSubtypeDistribution(params = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      const { startDate, endDate, region } = params
      
      // Build query parameters
      const queryParams = {}
      if (startDate) queryParams.start_date = startDate
      if (endDate) queryParams.end_date = endDate
      if (region) queryParams.region = region
      
      const response = await apiClient.get('/api/dashboard/subtypes', { params: queryParams })
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get subtype distribution'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Get mock data for demo purposes
   * 
   * @returns {Promise<Object>} Mock dashboard data
   */
  async function getMockDashboardData() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/api/dashboard/mock')
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to get mock dashboard data'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    getDashboardData,
    getOutbreakMapData,
    getTrendData,
    getAlerts,
    getRecentOutbreaks,
    getSubtypeDistribution,
    getMockDashboardData,
    isLoading,
    error
  }
}