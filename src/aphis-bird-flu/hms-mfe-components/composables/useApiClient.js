import { ref, reactive, computed } from 'vue'
import axios from 'axios'

/**
 * Composable that provides a configured API client
 * 
 * @returns {Object} Configured API client and related state
 */
export function useApiClient() {
  // State
  const isLoading = ref(false)
  const error = ref(null)
  const retryCount = ref(0)
  
  // Create API client
  const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })
  
  // Request interceptor
  apiClient.interceptors.request.use(
    config => {
      isLoading.value = true
      error.value = null
      
      // Add auth token if available
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      
      return config
    },
    err => {
      isLoading.value = false
      error.value = err.message || 'Error preparing request'
      return Promise.reject(err)
    }
  )
  
  // Response interceptor
  apiClient.interceptors.response.use(
    response => {
      isLoading.value = false
      retryCount.value = 0
      return response
    },
    async err => {
      isLoading.value = false
      
      const originalRequest = err.config
      
      // Auto retry on network errors or 5xx server errors (max 3 attempts)
      if ((err.message.includes('network error') || (err.response && err.response.status >= 500)) && 
          retryCount.value < 3 && 
          !originalRequest._retry) {
        
        retryCount.value += 1
        originalRequest._retry = true
        
        // Exponential backoff
        const delay = Math.pow(2, retryCount.value) * 1000
        await new Promise(resolve => setTimeout(resolve, delay))
        
        return apiClient(originalRequest)
      }
      
      // Handle specific error types
      if (err.response) {
        // Server returned an error response
        const status = err.response.status
        const data = err.response.data
        
        if (status === 401) {
          // Unauthorized - clear auth state
          localStorage.removeItem('auth_token')
          window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        }
        
        error.value = data.message || `Server error (${status})`
      } else if (err.request) {
        // Request made but no response received
        error.value = 'No response from server'
      } else {
        // Error setting up request
        error.value = err.message || 'Request failed'
      }
      
      return Promise.reject(err)
    }
  )
  
  /**
   * Clear the current error
   */
  function clearError() {
    error.value = null
  }
  
  /**
   * Set a mock response handler for a specific endpoint (for testing)
   * 
   * @param {string} endpoint - API endpoint to mock
   * @param {Function} handler - Mock response handler function
   */
  function mockEndpoint(endpoint, handler) {
    if (import.meta.env.MODE === 'development' || import.meta.env.MODE === 'test') {
      apiClient.interceptors.request.use(
        config => {
          if (config.url === endpoint || config.url.startsWith(endpoint)) {
            return Promise.resolve({
              data: handler(config),
              status: 200,
              statusText: 'OK',
              headers: {},
              config
            })
          }
          return config
        },
        error => Promise.reject(error)
      )
    }
  }
  
  return {
    apiClient,
    isLoading,
    error,
    clearError,
    mockEndpoint
  }
}