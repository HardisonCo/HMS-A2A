/**
 * APHIS Bird Flu HMS-MFE Components
 * 
 * This file exports all components and composables for easy importing
 */

// Main Components
export { default as SequenceAnalysisView } from './SequenceAnalysisView.vue'
export { default as TransmissionNetworkView } from './TransmissionNetworkView.vue'
export { default as DashboardView } from './DashboardView.vue'

// Tab Components
export { default as MutationsTab } from './tabs/MutationsTab.vue'
export { default as LineageTab } from './tabs/LineageTab.vue'

// Composables
export { useApiClient } from './composables/useApiClient'
export { useGeneticAnalysisApi } from './composables/useGeneticAnalysisApi'
export { useTransmissionAnalysisApi } from './composables/useTransmissionAnalysisApi'
export { useDashboardApi } from './composables/useDashboardApi'
export { useFederationApi } from './composables/useFederationApi'

/**
 * Register all components with Vue
 * 
 * @param {Object} app - Vue application instance
 */
export function registerComponents(app) {
  // Import all components
  const SequenceAnalysisView = require('./SequenceAnalysisView.vue').default
  const TransmissionNetworkView = require('./TransmissionNetworkView.vue').default
  const DashboardView = require('./DashboardView.vue').default
  const MutationsTab = require('./tabs/MutationsTab.vue').default
  const LineageTab = require('./tabs/LineageTab.vue').default
  
  // Register components globally
  app.component('AphisSequenceAnalysisView', SequenceAnalysisView)
  app.component('AphisTransmissionNetworkView', TransmissionNetworkView)
  app.component('AphisDashboardView', DashboardView)
  app.component('AphisMutationsTab', MutationsTab)
  app.component('AphisLineageTab', LineageTab)
}