/**
 * Vue Composable for Clinical Trial API Services
 * Makes it easy to use the API in Vue components with reactive state
 */

import { ref, computed, watch } from 'vue';
import { 
  clinicalTrialApi, 
  type Abstraction, 
  type ClinicalTrial, 
  type Publication, 
  type Visualization 
} from './clinical-trial-api';

export function useClinicalTrialApi() {
  // Reactive state for loading status and errors
  const isLoading = ref(false);
  const error = ref<Error | null>(null);
  
  // Clear error when new requests are started
  const clearError = () => {
    error.value = null;
  };

  /**
   * Wrapper for API calls to handle loading and error states
   */
  const executeApiCall = async <T>(
    apiCall: () => Promise<T>,
    errorMessage = 'API request failed'
  ): Promise<T | null> => {
    clearError();
    isLoading.value = true;
    
    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err : new Error(`${errorMessage}: ${err}`);
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // Abstractions
  const abstractions = ref<Abstraction[]>([]);
  const selectedAbstractions = ref<Abstraction[]>([]);

  // Clinical Trials
  const clinicalTrials = ref<ClinicalTrial[]>([]);
  const selectedClinicalTrials = ref<ClinicalTrial[]>([]);

  // Publications
  const publications = ref<Publication[]>([]);
  const currentPublication = ref<Publication | null>(null);

  // Visualizations
  const visualizations = ref<Visualization[]>([]);
  const selectedVisualizations = ref<Visualization[]>([]);

  // Analysis task tracking
  const currentTaskId = ref<string | null>(null);
  const taskStatus = ref<string | null>(null);
  const taskProgress = ref<number>(0);

  // Computed properties
  const hasSelectedAbstractions = computed(() => selectedAbstractions.value.length > 0);
  const hasSelectedClinicalTrials = computed(() => selectedClinicalTrials.value.length > 0);
  const isPublicationReady = computed(() => 
    currentPublication.value !== null && 
    currentPublication.value.content.trim().length > 0
  );

  // API call functions with reactive state management

  /**
   * Load abstractions with optional filtering
   */
  const loadAbstractions = async (filter?: {type?: string, confidence?: number}) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.getAbstractions(filter),
      'Failed to load abstractions'
    );
    
    if (result) {
      abstractions.value = result;
    }
    
    return result;
  };

  /**
   * Load a single abstraction by ID
   */
  const loadAbstraction = async (id: string) => {
    return executeApiCall(
      () => clinicalTrialApi.getAbstraction(id),
      `Failed to load abstraction ${id}`
    );
  };

  /**
   * Load clinical trials with optional filtering
   */
  const loadClinicalTrials = async (filter?: {status?: string, phase?: string}) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.getClinicalTrials(filter),
      'Failed to load clinical trials'
    );
    
    if (result) {
      clinicalTrials.value = result;
    }
    
    return result;
  };

  /**
   * Load a single clinical trial by ID
   */
  const loadClinicalTrial = async (id: string) => {
    return executeApiCall(
      () => clinicalTrialApi.getClinicalTrial(id),
      `Failed to load clinical trial ${id}`
    );
  };

  /**
   * Load clinical trials associated with a specific abstraction
   */
  const loadTrialsByAbstraction = async (abstractionId: string) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.getTrialsByAbstraction(abstractionId),
      `Failed to load trials for abstraction ${abstractionId}`
    );
    
    if (result) {
      clinicalTrials.value = result;
    }
    
    return result;
  };

  /**
   * Load publications with optional filtering
   */
  const loadPublications = async (filter?: {status?: string, author?: string}) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.getPublications(filter),
      'Failed to load publications'
    );
    
    if (result) {
      publications.value = result;
    }
    
    return result;
  };

  /**
   * Load a single publication by ID
   */
  const loadPublication = async (id: string) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.getPublication(id),
      `Failed to load publication ${id}`
    );
    
    if (result) {
      currentPublication.value = result;
    }
    
    return result;
  };

  /**
   * Create a new publication
   */
  const createPublication = async (publication: Omit<Publication, 'id' | 'created_at' | 'updated_at'>) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.createPublication(publication),
      'Failed to create publication'
    );
    
    if (result) {
      // Add to publications list and set as current
      publications.value = [...publications.value, result];
      currentPublication.value = result;
    }
    
    return result;
  };

  /**
   * Update an existing publication
   */
  const updatePublication = async (id: string, publication: Partial<Publication>) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.updatePublication(id, publication),
      `Failed to update publication ${id}`
    );
    
    if (result) {
      // Update publications list and current publication
      publications.value = publications.value.map(p => 
        p.id === id ? result : p
      );
      
      if (currentPublication.value?.id === id) {
        currentPublication.value = result;
      }
    }
    
    return result;
  };

  /**
   * Delete a publication
   */
  const deletePublication = async (id: string) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.deletePublication(id),
      `Failed to delete publication ${id}`
    );
    
    if (result !== null) {
      // Remove from publications list
      publications.value = publications.value.filter(p => p.id !== id);
      
      // Clear current publication if it's the one deleted
      if (currentPublication.value?.id === id) {
        currentPublication.value = null;
      }
    }
    
    return result;
  };

  /**
   * Load visualizations with optional filtering
   */
  const loadVisualizations = async (filter?: {type?: string, abstract_id?: string}) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.getVisualizations(filter),
      'Failed to load visualizations'
    );
    
    if (result) {
      visualizations.value = result;
    }
    
    return result;
  };

  /**
   * Generate a publication draft based on selected abstractions and clinical trials
   */
  const generatePublicationDraft = async (options?: { 
    includeVisualizations?: boolean,
    format?: 'markdown' | 'html'
  }) => {
    // Extract IDs from selected items
    const abstractionIds = selectedAbstractions.value.map(a => a.id);
    const clinicalTrialIds = selectedClinicalTrials.value.map(c => c.id);
    
    if (abstractionIds.length === 0 || clinicalTrialIds.length === 0) {
      error.value = new Error('Please select at least one abstraction and one clinical trial');
      return null;
    }
    
    const result = await executeApiCall(
      () => clinicalTrialApi.generatePublicationDraft(
        abstractionIds, 
        clinicalTrialIds, 
        options
      ),
      'Failed to generate publication draft'
    );
    
    return result;
  };

  /**
   * Run an abstraction analysis on the selected clinical trials
   */
  const runAbstractionAnalysis = async () => {
    // Extract IDs from selected clinical trials
    const clinicalTrialIds = selectedClinicalTrials.value.map(c => c.id);
    
    if (clinicalTrialIds.length === 0) {
      error.value = new Error('Please select at least one clinical trial');
      return null;
    }
    
    const result = await executeApiCall(
      () => clinicalTrialApi.runAbstractionAnalysis(clinicalTrialIds),
      'Failed to start abstraction analysis'
    );
    
    if (result) {
      currentTaskId.value = result.task_id;
      taskStatus.value = result.status;
      
      // Set up polling for task status if it's not completed
      if (result.status !== 'COMPLETED' && result.status !== 'FAILED') {
        pollTaskStatus(result.task_id);
      }
    }
    
    return result;
  };

  /**
   * Check the status of an analysis task
   */
  const checkAnalysisStatus = async (taskId: string) => {
    const result = await executeApiCall(
      () => clinicalTrialApi.checkAnalysisStatus(taskId),
      `Failed to check analysis status for task ${taskId}`
    );
    
    if (result) {
      taskStatus.value = result.status;
      taskProgress.value = result.progress;
      
      // If the task is complete, reload abstractions
      if (result.status === 'COMPLETED' && result.result_id) {
        await loadAbstractions();
      }
    }
    
    return result;
  };

  /**
   * Poll for task status updates
   */
  const pollTaskStatus = (taskId: string) => {
    const pollInterval = 2000; // 2 seconds
    
    const poll = async () => {
      const status = await checkAnalysisStatus(taskId);
      
      if (status && (status.status === 'COMPLETED' || status.status === 'FAILED')) {
        // Task is done, stop polling
        return;
      }
      
      // Continue polling
      setTimeout(poll, pollInterval);
    };
    
    // Start polling
    setTimeout(poll, pollInterval);
  };

  /**
   * Select or deselect an abstraction
   */
  const toggleAbstractionSelection = (abstraction: Abstraction) => {
    const index = selectedAbstractions.value.findIndex(a => a.id === abstraction.id);
    
    if (index === -1) {
      selectedAbstractions.value.push(abstraction);
    } else {
      selectedAbstractions.value.splice(index, 1);
    }
  };

  /**
   * Select or deselect a clinical trial
   */
  const toggleClinicalTrialSelection = (trial: ClinicalTrial) => {
    const index = selectedClinicalTrials.value.findIndex(t => t.id === trial.id);
    
    if (index === -1) {
      selectedClinicalTrials.value.push(trial);
    } else {
      selectedClinicalTrials.value.splice(index, 1);
    }
  };

  /**
   * Select or deselect a visualization
   */
  const toggleVisualizationSelection = (visualization: Visualization) => {
    const index = selectedVisualizations.value.findIndex(v => v.id === visualization.id);
    
    if (index === -1) {
      selectedVisualizations.value.push(visualization);
    } else {
      selectedVisualizations.value.splice(index, 1);
    }
  };

  /**
   * Clear all selections
   */
  const clearSelections = () => {
    selectedAbstractions.value = [];
    selectedClinicalTrials.value = [];
    selectedVisualizations.value = [];
  };

  /**
   * Create a new empty publication
   */
  const createEmptyPublication = () => {
    currentPublication.value = {
      id: 'new', // Temporary ID, will be replaced by the server
      title: 'New Publication',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      status: 'DRAFT',
      content: '',
      author: '', // This should be filled with the current user
      clinical_trial_ids: [],
      abstraction_ids: [],
      visualization_ids: []
    };
  };

  return {
    // State
    isLoading,
    error,
    abstractions,
    selectedAbstractions,
    clinicalTrials,
    selectedClinicalTrials,
    publications,
    currentPublication,
    visualizations,
    selectedVisualizations,
    taskStatus,
    taskProgress,
    
    // Computed
    hasSelectedAbstractions,
    hasSelectedClinicalTrials,
    isPublicationReady,
    
    // Methods
    loadAbstractions,
    loadAbstraction,
    loadClinicalTrials,
    loadClinicalTrial,
    loadTrialsByAbstraction,
    loadPublications,
    loadPublication,
    createPublication,
    updatePublication,
    deletePublication,
    loadVisualizations,
    generatePublicationDraft,
    runAbstractionAnalysis,
    toggleAbstractionSelection,
    toggleClinicalTrialSelection,
    toggleVisualizationSelection,
    clearSelections,
    createEmptyPublication
  };
}