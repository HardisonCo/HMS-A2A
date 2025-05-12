import { ref } from 'vue'
import { useApiClient } from './useApiClient'

/**
 * Composable for interacting with the Genetic Analysis API
 * 
 * @returns {Object} API methods for genetic analysis
 */
export function useGeneticAnalysisApi() {
  const { apiClient, isLoading: apiLoading, error: apiError } = useApiClient()
  
  // State
  const isLoading = ref(false)
  const error = ref(null)
  
  /**
   * Analyze a genetic sequence
   * 
   * @param {Object} params - Analysis parameters
   * @param {string} params.sequence - The genetic sequence data
   * @param {string} params.subtype - Virus subtype (e.g., H5N1)
   * @param {string|null} params.gene - Optional specific gene to analyze
   * @returns {Promise<Object>} Analysis results
   */
  async function analyzeSequence(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { sequence, subtype, gene } = params
      const queryParams = gene ? `?gene=${gene}` : ''
      
      const response = await apiClient.post(
        `/api/genetic/sequence/${subtype}${queryParams}`,
        { sequence_data: sequence }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to analyze sequence'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Identify mutations in a sequence
   * 
   * @param {Object} params - Analysis parameters
   * @param {string} params.sequence - The genetic sequence data
   * @param {string} params.subtype - Virus subtype
   * @param {string|null} params.gene - Optional specific gene
   * @returns {Promise<Array>} List of identified mutations
   */
  async function identifyMutations(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { sequence, subtype, gene } = params
      const queryParams = gene ? `?gene=${gene}` : ''
      
      const response = await apiClient.post(
        `/api/genetic/mutations/${subtype}${queryParams}`,
        { sequence_data: sequence }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to identify mutations'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Build a phylogenetic tree from multiple sequences
   * 
   * @param {Object} params - Analysis parameters
   * @param {Object} params.sequences - Dictionary mapping sequence IDs to sequences
   * @param {string} params.subtype - Virus subtype
   * @param {string} params.method - Tree construction method (upgma, nj, ml)
   * @returns {Promise<Object>} Phylogenetic tree data
   */
  async function buildPhylogeneticTree(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { sequences, subtype, method = 'upgma' } = params
      
      const response = await apiClient.post(
        `/api/genetic/phylogenetic-tree/${subtype}?method=${method}`,
        { sequences }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to build phylogenetic tree'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Compare multiple sequences
   * 
   * @param {Object} params - Analysis parameters
   * @param {Object} params.sequences - Dictionary mapping sequence IDs to sequences
   * @param {string} params.subtype - Virus subtype
   * @returns {Promise<Object>} Comparison results
   */
  async function compareSequences(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { sequences, subtype } = params
      
      const response = await apiClient.post(
        `/api/genetic/compare/${subtype}`,
        { sequences }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to compare sequences'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Assess zoonotic potential from mutations
   * 
   * @param {Object} params - Analysis parameters
   * @param {Array} params.mutations - List of mutations
   * @param {string} params.subtype - Virus subtype
   * @returns {Promise<Object>} Zoonotic risk assessment
   */
  async function assessZoonoticPotential(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { mutations, subtype } = params
      
      const response = await apiClient.post(
        `/api/genetic/zoonotic-potential/${subtype}`,
        { mutations }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to assess zoonotic potential'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Predict antigenic properties from mutations
   * 
   * @param {Object} params - Analysis parameters
   * @param {Array} params.mutations - List of mutations
   * @param {string} params.subtype - Virus subtype
   * @returns {Promise<Object>} Antigenic property predictions
   */
  async function predictAntigenicProperties(params) {
    isLoading.value = true
    error.value = null
    
    try {
      const { mutations, subtype } = params
      
      const response = await apiClient.post(
        `/api/genetic/antigenic-properties/${subtype}`,
        { mutations }
      )
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to predict antigenic properties'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    analyzeSequence,
    identifyMutations,
    buildPhylogeneticTree,
    compareSequences,
    assessZoonoticPotential,
    predictAntigenicProperties,
    isLoading,
    error
  }
}