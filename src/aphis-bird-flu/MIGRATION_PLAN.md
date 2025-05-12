# HMS-MFE Migration Plan for APHIS Bird Flu Tracking System

This document outlines the comprehensive plan for migrating the APHIS Bird Flu Tracking System to the HMS-MFE (Micro Frontend) architecture. This migration will allow the system to be integrated with other agency implementations while maintaining its specialized functionality.

## 1. Current Architecture Assessment

### 1.1 APHIS Bird Flu System Architecture

The current APHIS Bird Flu system follows a system-supervisor architecture with:

- Domain-specific supervisors for animal health monitoring
- Core services including genetic analysis, outbreak detection, and visualization
- FastAPI-based backend exposing REST endpoints
- Server-rendered visualizations and dashboards
- Agency-specific implementations for CDC, EPA, and FEMA

### 1.2 HMS-MFE Architecture

HMS-MFE is built on:

- Vue 3 frontend with component-based architecture
- Micro-frontend approach allowing isolated agency modules
- Agency module mapping for routing configuration
- Docker-based deployment with SSR capabilities
- Shared UI component library with extensive documentation

## 2. Migration Strategy

### 2.1 Overall Approach

We will implement a phased migration strategy:

1. **Phase 1: Core Infrastructure** (Weeks 1-3)
   - Set up APHIS agency module in HMS-MFE
   - Configure routing and integration points
   - Create data access layer for API connectivity

2. **Phase 2: UI Component Migration** (Weeks 4-7)
   - Convert server-rendered visualizations to interactive components
   - Implement agency-specific dashboard views
   - Create reusable components for genetic analysis display

3. **Phase 3: Cross-Agency Integration** (Weeks 8-10)
   - Implement unified data federation components
   - Create cross-agency dashboard
   - Configure agency-specific access controls

4. **Phase 4: Testing & Deployment** (Weeks 11-12)
   - Comprehensive testing across all agency implementations
   - Performance optimization
   - Documentation and training
   - Production deployment

### 2.2 Agency Mapping Configuration

Add APHIS to the agency module mapping:

```json
{
  "label": "APHIS",
  "domain": "aphis.usda.gov-ai.co",
  "modules": ["Gov", "Analytics", "Assessments", "Visualization"],
  "routes": [
    {
      "path": "/dashboard/surveillance",
      "mfeUrl": "/aphis/surveillance",
      "purpose": "Bird flu outbreak monitoring and visualization"
    },
    {
      "path": "/dashboard/genetic",
      "mfeUrl": "/aphis/genetic",
      "purpose": "Genetic sequence analysis and transmission tracking"
    },
    {
      "path": "/dashboard/response",
      "mfeUrl": "/aphis/response",
      "purpose": "Response coordination and resource allocation"
    },
    {
      "path": "/article",
      "mfeUrl": "https://vuero.cssninja.io/sidebar/dashboards/writer",
      "purpose": "Outbreak notifications and public health bulletins"
    }
  ],
  "notes": "Monitors and responds to animal health threats with focus on zoonotic diseases and their transmission"
}
```

### 2.3 Data Access Strategy

1. Create API client services to interact with existing APHIS Bird Flu backend
2. Implement caching strategies for improved performance
3. Develop data transformation layers to convert API responses to component-friendly formats
4. Create mock data services for development and testing

## 3. Component Migration Plan

### 3.1 Dashboard Components

Convert the following server-rendered visualizations to Vue components:

1. **Outbreak Map Component**
   - Interactive choropleth map showing outbreak locations
   - Filterable by time period, severity, and strain type
   - Integration with Mapbox for enhanced visualization

2. **Genetic Analysis Dashboard**
   - Sequence similarity visualizations
   - Mutation tracking components
   - Phylogenetic tree visualization

3. **Resource Allocation Dashboard**
   - Resource deployment status visualization
   - Response team tracking
   - Effectiveness metrics display

### 3.2 Shared Components

Create reusable components for cross-agency use:

1. **Sequence Analysis Card**
   - Display genetic sequence data with highlighted mutations
   - Filterable view of sequence metadata
   - Exportable data in standard formats

2. **Alert Notification Component**
   - Real-time notifications for new outbreaks
   - Configurable severity indicators
   - Agency-specific notification preferences

3. **Transmission Network Graph**
   - Interactive network visualization of disease spread
   - Temporal controls for viewing spread over time
   - Filtering options for geographic and genetic factors

### 3.3 Component Example (Outbreak Map)

```vue
<template>
  <div class="outbreak-map-container">
    <VCard>
      <template #header>
        <div class="is-flex is-justify-content-space-between">
          <h3 class="title is-4">Bird Flu Outbreak Map</h3>
          <div class="controls">
            <VSelect v-model="selectedTimeRange" :options="timeRangeOptions" />
            <VSelect v-model="selectedStrainType" :options="strainTypes" />
          </div>
        </div>
      </template>
      <div class="map-container" ref="mapContainer"></div>
      <div class="legend">
        <div v-for="(item, index) in legendItems" :key="index" class="legend-item">
          <span class="color-box" :style="{ backgroundColor: item.color }"></span>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </VCard>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import mapboxgl from 'mapbox-gl'
import { useOutbreakData } from '@/composables/outbreak-data'

// Component state
const mapContainer = ref(null)
const selectedTimeRange = ref('last30Days')
const selectedStrainType = ref('all')

// Options for filters
const timeRangeOptions = [
  { value: 'last7Days', label: 'Last 7 Days' },
  { value: 'last30Days', label: 'Last 30 Days' },
  { value: 'last90Days', label: 'Last 90 Days' },
  { value: 'lastYear', label: 'Last Year' }
]

const strainTypes = [
  { value: 'all', label: 'All Strains' },
  { value: 'h5n1', label: 'H5N1' },
  { value: 'h7n9', label: 'H7N9' },
  { value: 'h9n2', label: 'H9N2' }
]

// Legend configuration
const legendItems = [
  { color: '#f03b20', label: 'Severe Outbreak (>10 cases)' },
  { color: '#feb24c', label: 'Moderate Outbreak (3-10 cases)' },
  { color: '#ffeda0', label: 'Low Outbreak (1-2 cases)' }
]

// Data loading
const { data: outbreakData, loading, error } = useOutbreakData(selectedTimeRange, selectedStrainType)

// Map initialization
let map = null
onMounted(() => {
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
  
  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/light-v10',
    center: [-95.7129, 37.0902],
    zoom: 3
  })
  
  map.on('load', () => {
    loadMapData()
  })
})

// Update map when filters change
watch([selectedTimeRange, selectedStrainType], () => {
  if (map && map.loaded()) {
    loadMapData()
  }
})

function loadMapData() {
  // Implementation for loading data to map
  // This would display the outbreak data with appropriate styling
}
</script>

<style scoped>
.map-container {
  height: 480px;
  width: 100%;
  border-radius: 6px;
}

.legend {
  margin-top: 10px;
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.color-box {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
}
</style>
```

## 4. Cross-Agency Integration

### 4.1 Federation Integration

Implement the following federation components in HMS-MFE:

1. **Federation Hub Client**
   - Vue service for communicating with federation backend
   - Authentication and authorization handling
   - Query management for cross-agency data access

2. **SharedDataProvider Component**
   - Vue context provider for sharing federation data across components
   - Reactive data synchronization
   - Status tracking for multi-agency operations

3. **Agency Selector Component**
   - UI for selecting agency data sources
   - Permission management integration
   - Data source configuration interface

### 4.2 Unified Dashboard

Create a unified dashboard that integrates data from CDC, EPA, FEMA, and APHIS:

1. **Combined Outbreak View**
   - Integrated map showing human cases (CDC) and animal cases (APHIS)
   - Timeline correlation between cases
   - Environmental factors overlay (EPA data)

2. **Resource Coordination Panel**
   - FEMA resource deployment status
   - CDC public health team allocations
   - APHIS response team coordination

3. **Notification Integration**
   - Centralized alert inbox 
   - Role-based filtered notifications
   - Cross-agency communication log

## 5. API Integration Strategy

### 5.1 API Client Implementation

Create Vue composables for API access:

```javascript
// src/composables/useGeneticAnalysis.js
import { ref, computed } from 'vue'
import apiClient from '@/utils/api-client'

export function useGeneticAnalysis(sequenceId) {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  const loadSequenceData = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get(`/api/genetic/sequence/${sequenceId}`)
      data.value = response.data
    } catch (err) {
      error.value = err.message || 'Failed to load sequence data'
    } finally {
      loading.value = false
    }
  }
  
  // Computed properties for commonly used data transformations
  const mutationCount = computed(() => {
    if (!data.value) return 0
    return data.value.mutations?.length || 0
  })
  
  const similarityScore = computed(() => {
    if (!data.value || !data.value.referenceComparison) return null
    return data.value.referenceComparison.similarityScore
  })
  
  // Load data initially if sequenceId is provided
  if (sequenceId) {
    loadSequenceData()
  }
  
  return {
    data,
    loading,
    error,
    mutationCount,
    similarityScore,
    loadSequenceData
  }
}
```

### 5.2 Environment Configuration

Configure API endpoints for different environments:

```javascript
// .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_ACCESS_TOKEN=pk.your_development_token
VITE_ENABLE_MOCK_DATA=true

// .env.production
VITE_API_BASE_URL=https://api.aphis.usda.gov-ai.co
VITE_MAPBOX_ACCESS_TOKEN=pk.your_production_token
VITE_ENABLE_MOCK_DATA=false
```

## 6. Deployment Strategy

### 6.1 Docker Configuration

Update the Dockerfile to include APHIS-specific configuration:

```dockerfile
FROM bitnami/node:20 AS build
WORKDIR /app

# APHIS-specific environment variables
ARG VITE_API_BASE_URL=""
ARG VITE_MAPBOX_ACCESS_TOKEN=""
ARG VITE_FEDERATION_HUB_URL=""

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json ./
RUN pnpm install --no-lockfile

COPY . .
RUN VITE_API_BASE_URL=$VITE_API_BASE_URL \
  VITE_MAPBOX_ACCESS_TOKEN=$VITE_MAPBOX_ACCESS_TOKEN \
  VITE_FEDERATION_HUB_URL=$VITE_FEDERATION_HUB_URL \
  NODE_OPTIONS=--max-old-space-size=6144 \
  pnpm ssr:build

FROM bitnami/node:20 AS prod
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json ./
RUN pnpm install --no-lockfile --prod

COPY --from=build /app/dist ./dist
COPY --from=build /app/json-server ./json-server
COPY --from=build /app/server ./server

EXPOSE 3000 8080

ENV NODE_ENV=production

CMD ["pnpm", "ssr:start"]
```

### 6.2 CI/CD Pipeline

Implement CI/CD pipeline with the following stages:

1. **Build**
   - Static code analysis
   - Build HMS-MFE with APHIS components
   - Create Docker image

2. **Test**
   - Unit tests for components
   - Integration tests for API connectivity
   - End-to-end tests for critical workflows

3. **Deploy**
   - Stage environment deployment
   - Smoke tests
   - Production deployment with blue/green approach

## 7. Timeline and Resources

### 7.1 Implementation Timeline

| Phase | Timeframe | Key Deliverables |
|-------|-----------|------------------|
| Phase 1: Core Infrastructure | Weeks 1-3 | APHIS agency module, routing, data access layer |
| Phase 2: UI Component Migration | Weeks 4-7 | Dashboard components, genetic analysis views, visualization components |
| Phase 3: Cross-Agency Integration | Weeks 8-10 | Federation components, unified dashboard, notification integration |
| Phase 4: Testing & Deployment | Weeks 11-12 | Comprehensive testing, documentation, production deployment |

### 7.2 Resource Requirements

| Resource Type | Quantity | Role |
|---------------|----------|------|
| Frontend Developer | 2 | Vue component development, HMS-MFE integration |
| Backend Developer | 1 | API integration, data transformation services |
| DevOps Engineer | 1 | CI/CD pipeline, Docker configuration |
| QA Engineer | 1 | Testing strategies, automation |
| Project Manager | 1 | Coordination, timeline management |

## 8. Risk Management

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| API compatibility issues | High | Medium | Create adapter layer, comprehensive API testing |
| Performance degradation | Medium | Medium | Implement caching, optimize rendering, lazy load components |
| Data synchronization issues | High | Medium | Implement robust error handling, retry mechanisms |
| Security vulnerabilities | High | Low | Comprehensive security review, proper authentication |
| User experience disruption | Medium | Medium | Phased rollout, feature flagging, user feedback collection |

## 9. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Page Load Performance | < 2 seconds | Lighthouse reports, real user monitoring |
| API Response Integration | < 500ms | Backend monitoring, client-side timing |
| Cross-Agency Data Synchronization | < 5 second delay | Backend logging, real-time event tracking |
| User Satisfaction | > 85% approval | User surveys, feedback collection |
| Development Velocity | 2-week sprint cycle | Sprint completion rate, story point velocity |

## 10. Future Enhancements

1. **Offline Capabilities**
   - Implement service worker for offline access to critical data
   - Local storage synchronization for field operations

2. **Mobile Optimization**
   - Responsive design refinement for field use
   - Progressive Web App (PWA) implementation

3. **AI-Enhanced Analysis**
   - Predictive outbreak modeling integration
   - Automated genetic sequence analysis suggestions

4. **Extended Agency Integration**
   - Additional USDA component integration
   - International agency data sharing capabilities

## 11. Appendix

### 11.1 Technical Resources

- HMS-MFE Documentation: [HMS-MFE README](/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/README.md)
- APHIS Bird Flu API Documentation: [API Documentation](/Users/arionhardison/Desktop/Codify/aphis-bird-flu/API_DOCUMENTATION.md)
- Federation Framework Documentation: [Federation README](/Users/arionhardison/Desktop/Codify/agency-implementation/foundation/federation/README.md)

### 11.2 Related Documents

- Federal Agency Implementation Plan: [Implementation Plan](/Users/arionhardison/Desktop/Codify/aphis-bird-flu/FEDERAL_AGENCY_IMPLEMENTATION_PLAN.md)
- System Overview: [System Overview](/Users/arionhardison/Desktop/Codify/aphis-bird-flu/SYSTEM_OVERVIEW.md)
- Quick Start Guide: [Quick Start Guide](/Users/arionhardison/Desktop/Codify/aphis-bird-flu/QUICK_START_GUIDE.md)