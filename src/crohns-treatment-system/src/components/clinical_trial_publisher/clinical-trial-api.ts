/**
 * Clinical Trial Publisher API Service
 * Provides integration between the ClinicalTrialPublisher Vue component and the backend API
 */

// Types for our API responses and requests
export interface Abstraction {
  id: string;
  name: string;
  description: string;
  confidence: number;
  type: string;
  source: string;
  related_entities: RelatedEntity[];
}

export interface RelatedEntity {
  id: string;
  name: string;
  type: string;
  strength: number;
  evidence: string[];
}

export interface ClinicalTrial {
  id: string;
  title: string;
  status: 'RECRUITING' | 'ONGOING' | 'COMPLETED' | 'PLANNED';
  phase: 'PHASE_1' | 'PHASE_2' | 'PHASE_3' | 'PHASE_4';
  start_date: string;
  end_date: string;
  description: string;
  inclusion_criteria: string[];
  exclusion_criteria: string[];
  biomarkers: string[];
  treatments: string[];
  outcomes: string[];
  abstraction_ids: string[];
}

export interface Publication {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  content: string;
  author: string;
  clinical_trial_ids: string[];
  abstraction_ids: string[];
  visualization_ids: string[];
}

export interface Visualization {
  id: string;
  title: string;
  description: string;
  type: 'RELATIONSHIP_GRAPH' | 'BIOMARKER_HEATMAP' | 'OUTCOME_COMPARISON';
  image_url: string;
  data_url: string;
  abstraction_ids: string[];
  clinical_trial_ids: string[];
}

/**
 * Clinical Trial API Service
 */
export class ClinicalTrialApiService {
  private baseUrl: string;

  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl;
  }

  /**
   * Helper method to perform API requests with proper error handling
   */
  private async request<T>(
    endpoint: string, 
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET', 
    data?: any
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
      }

      const result = await response.json();
      return result as T;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Get a list of abstractions with optional filtering
   */
  async getAbstractions(
    filter?: {type?: string, confidence?: number}
  ): Promise<Abstraction[]> {
    const queryParams = new URLSearchParams();
    if (filter?.type) queryParams.append('type', filter.type);
    if (filter?.confidence) queryParams.append('min_confidence', filter.confidence.toString());
    
    const endpoint = `/abstractions?${queryParams.toString()}`;
    return this.request<Abstraction[]>(endpoint);
  }

  /**
   * Get a single abstraction by ID
   */
  async getAbstraction(id: string): Promise<Abstraction> {
    return this.request<Abstraction>(`/abstractions/${id}`);
  }

  /**
   * Get a list of clinical trials with optional filtering
   */
  async getClinicalTrials(
    filter?: {status?: string, phase?: string}
  ): Promise<ClinicalTrial[]> {
    const queryParams = new URLSearchParams();
    if (filter?.status) queryParams.append('status', filter.status);
    if (filter?.phase) queryParams.append('phase', filter.phase);
    
    const endpoint = `/clinical-trials?${queryParams.toString()}`;
    return this.request<ClinicalTrial[]>(endpoint);
  }

  /**
   * Get a single clinical trial by ID
   */
  async getClinicalTrial(id: string): Promise<ClinicalTrial> {
    return this.request<ClinicalTrial>(`/clinical-trials/${id}`);
  }

  /**
   * Get clinical trials associated with a specific abstraction ID
   */
  async getTrialsByAbstraction(abstractionId: string): Promise<ClinicalTrial[]> {
    return this.request<ClinicalTrial[]>(`/abstractions/${abstractionId}/clinical-trials`);
  }

  /**
   * Get publications with optional filtering
   */
  async getPublications(
    filter?: {status?: string, author?: string}
  ): Promise<Publication[]> {
    const queryParams = new URLSearchParams();
    if (filter?.status) queryParams.append('status', filter.status);
    if (filter?.author) queryParams.append('author', filter.author);
    
    const endpoint = `/publications?${queryParams.toString()}`;
    return this.request<Publication[]>(endpoint);
  }

  /**
   * Get a single publication by ID
   */
  async getPublication(id: string): Promise<Publication> {
    return this.request<Publication>(`/publications/${id}`);
  }

  /**
   * Create a new publication
   */
  async createPublication(publication: Omit<Publication, 'id' | 'created_at' | 'updated_at'>): Promise<Publication> {
    return this.request<Publication>('/publications', 'POST', publication);
  }

  /**
   * Update an existing publication
   */
  async updatePublication(id: string, publication: Partial<Publication>): Promise<Publication> {
    return this.request<Publication>(`/publications/${id}`, 'PUT', publication);
  }

  /**
   * Delete a publication
   */
  async deletePublication(id: string): Promise<void> {
    return this.request<void>(`/publications/${id}`, 'DELETE');
  }

  /**
   * Get visualizations with optional filtering
   */
  async getVisualizations(
    filter?: {type?: string, abstract_id?: string}
  ): Promise<Visualization[]> {
    const queryParams = new URLSearchParams();
    if (filter?.type) queryParams.append('type', filter.type);
    if (filter?.abstract_id) queryParams.append('abstraction_id', filter.abstract_id);
    
    const endpoint = `/visualizations?${queryParams.toString()}`;
    return this.request<Visualization[]>(endpoint);
  }

  /**
   * Get a single visualization by ID
   */
  async getVisualization(id: string): Promise<Visualization> {
    return this.request<Visualization>(`/visualizations/${id}`);
  }

  /**
   * Generate a publication draft based on selected abstractions and clinical trials
   */
  async generatePublicationDraft(
    abstractionIds: string[],
    clinicalTrialIds: string[],
    options?: { 
      includeVisualizations?: boolean,
      format?: 'markdown' | 'html'
    }
  ): Promise<{content: string, visualizationIds: string[]}> {
    const queryParams = new URLSearchParams();
    if (options?.includeVisualizations !== undefined) {
      queryParams.append('include_visualizations', options.includeVisualizations.toString());
    }
    if (options?.format) {
      queryParams.append('format', options.format);
    }
    
    const endpoint = `/publications/generate-draft?${queryParams.toString()}`;
    return this.request(endpoint, 'POST', {
      abstraction_ids: abstractionIds,
      clinical_trial_ids: clinicalTrialIds
    });
  }

  /**
   * Run an abstraction analysis on specified clinical trials
   */
  async runAbstractionAnalysis(clinicalTrialIds: string[]): Promise<{
    task_id: string,
    status: string,
    estimated_completion_time: number
  }> {
    return this.request('/abstractions/analyze', 'POST', {
      clinical_trial_ids: clinicalTrialIds
    });
  }

  /**
   * Check the status of an analysis task
   */
  async checkAnalysisStatus(taskId: string): Promise<{
    task_id: string,
    status: string,
    progress: number,
    result_id?: string,
    error?: string
  }> {
    return this.request(`/abstractions/tasks/${taskId}`);
  }

  /**
   * Generate documentation for HMS-DOC from abstractions and relationships
   */
  async generateDocumentation(
    abstractionIds: string[],
    clinicalTrialIds: string[],
    relationships: any[],
    projectName?: string
  ): Promise<{documentation_info: any}> {
    return this.request('/doc-integration/generate-documentation', 'POST', {
      clinical_trials: clinicalTrialIds,
      abstractions: abstractionIds,
      relationships: relationships,
      project_name: projectName || 'Crohns-Treatment-Documentation'
    });
  }

  /**
   * Export abstractions to HMS-DOC
   */
  async exportAbstractionsToDoc(
    abstractions: any[],
    relationships: any[],
    projectName?: string
  ): Promise<{output_path: string}> {
    return this.request('/doc-integration/export-abstractions', 'POST', {
      abstractions: abstractions,
      relationships: relationships,
      project_name: projectName || 'Crohns-Treatment-Abstractions'
    });
  }

  /**
   * Publish clinical trial to HMS-MFE writer
   */
  async publishTrialToMfe(
    trialData: any,
    abstractions: any[],
    writerComponentPath?: string
  ): Promise<{publication_info: any}> {
    return this.request('/doc-integration/publish-trial', 'POST', {
      trial_data: trialData,
      abstractions: abstractions,
      writer_component_path: writerComponentPath
    });
  }
}

// Create a singleton instance of the service
export const clinicalTrialApi = new ClinicalTrialApiService();