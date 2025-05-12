/**
 * Integration with HMS-MFE Writer Component
 * 
 * This module provides integration with the HMS-MFE writer.vue component
 * located at: /Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue
 */

import { clinicalTrialApi, type Publication } from './clinical-trial-api';

/**
 * WriterIntegrationService provides methods to connect the ClinicalTrialPublisher 
 * with the HMS-MFE Writer component.
 */
export class WriterIntegrationService {
  private readonly writerComponentPath = '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue';
  
  /**
   * Open a publication in the HMS-MFE Writer component
   * 
   * @param publication The publication to open in the writer
   * @returns Promise indicating success or failure
   */
  async openInWriter(publication: Publication): Promise<boolean> {
    try {
      // In a real implementation, this would use an IPC mechanism to communicate with the writer
      // or use a browser-based navigation to the writer component with query parameters
      
      console.log(`Opening publication ${publication.id} in writer component at ${this.writerComponentPath}`);
      
      // Simulate success
      return true;
    } catch (error) {
      console.error('Failed to open publication in writer:', error);
      return false;
    }
  }
  
  /**
   * Export a publication to a format suitable for the HMS-MFE Writer component
   * 
   * @param publication The publication to export
   * @returns The exported publication data
   */
  exportForWriter(publication: Publication): Record<string, any> {
    return {
      id: publication.id,
      title: publication.title,
      content: publication.content,
      metadata: {
        abstractionIds: publication.abstraction_ids,
        clinicalTrialIds: publication.clinical_trial_ids,
        visualizationIds: publication.visualization_ids,
        author: publication.author,
        status: publication.status,
        createdAt: publication.created_at,
        updatedAt: publication.updated_at
      }
    };
  }
  
  /**
   * Import a publication from the HMS-MFE Writer component format
   * 
   * @param writerData The data from the writer component
   * @returns A publication object
   */
  importFromWriter(writerData: Record<string, any>): Publication {
    return {
      id: writerData.id || '',
      title: writerData.title || '',
      content: writerData.content || '',
      created_at: writerData.metadata?.createdAt || new Date().toISOString(),
      updated_at: writerData.metadata?.updatedAt || new Date().toISOString(),
      status: writerData.metadata?.status || 'DRAFT',
      author: writerData.metadata?.author || '',
      clinical_trial_ids: writerData.metadata?.clinicalTrialIds || [],
      abstraction_ids: writerData.metadata?.abstractionIds || [],
      visualization_ids: writerData.metadata?.visualizationIds || []
    };
  }
  
  /**
   * Save a publication from the HMS-MFE Writer component
   * 
   * @param writerData The data from the writer component
   * @returns The saved publication
   */
  async saveFromWriter(writerData: Record<string, any>): Promise<Publication | null> {
    try {
      const publication = this.importFromWriter(writerData);
      
      if (publication.id && publication.id !== 'new') {
        // Update existing publication
        return await clinicalTrialApi.updatePublication(publication.id, publication);
      } else {
        // Create new publication
        return await clinicalTrialApi.createPublication(publication);
      }
    } catch (error) {
      console.error('Failed to save publication from writer:', error);
      return null;
    }
  }
}

// Create a singleton instance of the service
export const writerIntegrationService = new WriterIntegrationService();