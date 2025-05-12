/**
 * Clinical Trial Publisher Components
 * 
 * This module exports components for publishing clinical trial data
 * and integrating with HMS-DOC and HMS-MFE.
 */

// Export main components
import ClinicalTrialPublisher from './ClinicalTrialPublisher.vue';
import IntegrationDashboard from './IntegrationDashboard.vue';

// Export API and services
import { clinicalTrialApi, ClinicalTrialApiService } from './clinical-trial-api';
import { useClinicalTrialApi } from './use-clinical-trial-api';
import { writerIntegrationService } from './writer-integration';

// Export types
export type { 
  Abstraction, 
  RelatedEntity, 
  ClinicalTrial, 
  Publication, 
  Visualization 
} from './clinical-trial-api';

// Export components and services
export {
  // Components
  ClinicalTrialPublisher,
  IntegrationDashboard,
  
  // API Services
  clinicalTrialApi,
  ClinicalTrialApiService,
  useClinicalTrialApi,
  writerIntegrationService
};

// Default export for easier imports
export default {
  ClinicalTrialPublisher,
  IntegrationDashboard
};