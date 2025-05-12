/**
 * APHIS Bird Flu routes configuration for HMS-MFE
 */

// Import components
import { 
  SequenceAnalysisView, 
  TransmissionNetworkView, 
  DashboardView 
} from '@/components/aphis'

/**
 * APHIS Routes
 * These routes provide access to the APHIS Bird Flu tracking system
 * functionality within the HMS-MFE framework.
 */
const aphisRoutes = [
  /**
   * Bird Flu Surveillance Dashboard
   * Comprehensive monitoring of outbreaks, trends, and alerts
   */
  {
    path: '/aphis/surveillance',
    name: 'aphis-surveillance',
    component: DashboardView,
    meta: { 
      title: 'Bird Flu Surveillance',
      description: 'Monitor avian influenza outbreaks, trends, and alerts',
      icon: 'mdi:virus',
      permission: 'aphis:view' 
    }
  },
  
  /**
   * Genetic Analysis
   * Analysis of viral genetic sequences for mutations and lineages
   */
  {
    path: '/aphis/genetic',
    name: 'aphis-genetic',
    component: SequenceAnalysisView,
    meta: { 
      title: 'Genetic Analysis',
      description: 'Analyze viral genetic sequences for mutations and lineages',
      icon: 'mdi:dna',
      permission: 'aphis:genetic' 
    }
  },
  
  /**
   * Transmission Analysis
   * Analysis of transmission networks and patterns
   */
  {
    path: '/aphis/transmission',
    name: 'aphis-transmission',
    component: TransmissionNetworkView,
    meta: { 
      title: 'Transmission Analysis',
      description: 'Analyze transmission networks and patterns',
      icon: 'mdi:share-variant',
      permission: 'aphis:transmission' 
    }
  },

  /**
   * Nested routes for specific details
   */
  {
    path: '/aphis/outbreak/:id',
    name: 'aphis-outbreak-detail',
    component: () => import('@/components/aphis/OutbreakDetailView.vue'),
    meta: { 
      title: 'Outbreak Detail',
      description: 'Detailed information about a specific outbreak',
      icon: 'mdi:microscope',
      permission: 'aphis:view' 
    }
  },

  /**
   * Federal agency integration routes
   */
  {
    path: '/aphis/agency-integration',
    name: 'aphis-agency-integration',
    component: () => import('@/components/aphis/AgencyIntegrationView.vue'),
    meta: { 
      title: 'Agency Integration',
      description: 'Manage integration with other federal agencies',
      icon: 'mdi:account-group',
      permission: 'aphis:admin' 
    }
  }
]

export default aphisRoutes