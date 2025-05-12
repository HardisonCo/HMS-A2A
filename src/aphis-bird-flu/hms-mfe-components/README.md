# APHIS Bird Flu HMS-MFE Components

This directory contains Vue.js components for integrating the APHIS Bird Flu Tracking System with the HMS-MFE architecture. These components are designed to be used in the HMS-MFE framework and provide interactive visualizations and analysis tools for avian influenza surveillance.

## Components Overview

### Main Components

1. **SequenceAnalysisView.vue**
   - Interactive component for analyzing viral genetic sequences
   - Identifies mutations, lineages, and zoonotic potential
   - Displays results in tabbed interface with visualizations

2. **TransmissionNetworkView.vue**
   - Visualizes transmission networks between cases
   - Provides tools for analyzing outbreak patterns
   - Includes interactive network graph visualization

3. **DashboardView.vue**
   - Comprehensive surveillance dashboard combining multiple data sources
   - Integrates mapping of cases, genetic analysis, and trends
   - Provides filtering and control options

### Supporting Components

1. **Tabs/** - Contains tab components for different analysis views:
   - **MutationsTab.vue** - Displays detailed mutation information
   - **LineageTab.vue** - Shows virus lineage and geographic distribution
   - **AntigenicTab.vue** - Visualizes antigenic properties and vaccine match
   - **ZoonoticTab.vue** - Displays zoonotic potential assessment

2. **Composables/** - Contains Vue composables for API integration:
   - **useApiClient.js** - Base API client with error handling and retries
   - **useGeneticAnalysisApi.js** - Services for genetic sequence analysis
   - **useTransmissionAnalysisApi.js** - Services for transmission analysis
   - **useDashboardApi.js** - Services for dashboard data
   - **useFederationApi.js** - Services for federated data

## Quick Start

The easiest way to integrate these components is to use the provided installation script:

```bash
# Navigate to the hms-mfe-components directory
cd /path/to/aphis-bird-flu/hms-mfe-components

# Run the installation script
chmod +x install.sh
./install.sh /path/to/hms-mfe
```

This script will:
1. Copy components to the HMS-MFE project
2. Install required dependencies
3. Create a routes file
4. Set up environment files
5. Provide instructions for final steps

## Development with Mock API

For development purposes, a mock API server is included:

```bash
# Navigate to the mock-data directory
cd /path/to/aphis-bird-flu/hms-mfe-components/mock-data

# Install dependencies
npm install

# Start the mock server
npm start
```

The mock server will run at http://localhost:8000 and provide endpoints that mimic the real API. It serves:
- Dashboard data (outbreaks, trends, alerts)
- Genetic analysis data (mutations, lineages, zoonotic risk)
- Transmission analysis data (networks, patterns, predictions)
- Federation endpoints for cross-agency integration

## Manual Integration with HMS-MFE

If you prefer to manually integrate the components, follow these steps:

### 1. Copy Components to HMS-MFE

Copy the component files to your HMS-MFE project:

```bash
# Create necessary directories
mkdir -p /path/to/hms-mfe/src/components/aphis
mkdir -p /path/to/hms-mfe/src/composables/aphis

# Copy components and composables
cp -r hms-mfe-components/*.vue /path/to/hms-mfe/src/components/aphis/
cp -r hms-mfe-components/tabs /path/to/hms-mfe/src/components/aphis/
cp -r hms-mfe-components/composables/*.js /path/to/hms-mfe/src/composables/aphis/
```

### 2. Register Routes

Update your HMS-MFE routing configuration to include APHIS Bird Flu routes. Add the following to your router configuration:

```javascript
// In your router configuration file
import SequenceAnalysisView from '@/components/aphis/SequenceAnalysisView.vue'
import TransmissionNetworkView from '@/components/aphis/TransmissionNetworkView.vue'
import DashboardView from '@/components/aphis/DashboardView.vue'

const routes = [
  // Other routes...

  // APHIS Bird Flu routes
  {
    path: '/aphis/surveillance',
    name: 'aphis-surveillance',
    component: DashboardView,
    meta: { title: 'Bird Flu Surveillance' }
  },
  {
    path: '/aphis/genetic',
    name: 'aphis-genetic',
    component: SequenceAnalysisView,
    meta: { title: 'Genetic Analysis' }
  },
  {
    path: '/aphis/transmission',
    name: 'aphis-transmission',
    component: TransmissionNetworkView,
    meta: { title: 'Transmission Analysis' }
  }
]
```

### 3. Update Agency Mapping

Update the agency module mapping in `agency.module.mapping.json` to include APHIS:

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

### 4. Configure Environment Variables

Create or update your environment configuration files to include API connection details:

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here

# .env.production
VITE_API_BASE_URL=https://api.aphis.usda.gov-ai.co
VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
```

### 5. Install Dependencies

These components require the following dependencies:

```bash
# Install dependencies
pnpm add axios force-graph d3 mapbox-gl apexcharts vue3-apexcharts
```

### 6. Build and Test

Build the HMS-MFE application with the new components:

```bash
pnpm build
```

## API Integration

The components expect the following API endpoints to be available:

### Dashboard API

- `GET /api/dashboard` - Get dashboard summary data
- `GET /api/dashboard/map` - Get outbreak map data
- `GET /api/dashboard/trends` - Get trend data
- `GET /api/dashboard/alerts` - Get alerts
- `GET /api/dashboard/recent` - Get recent outbreaks
- `GET /api/dashboard/subtypes` - Get virus subtype distribution

### Genetic Analysis API

- `POST /api/genetic/sequence/{subtype}` - Analyze genetic sequence
- `POST /api/genetic/mutations/{subtype}` - Identify mutations
- `POST /api/genetic/phylogenetic-tree/{subtype}` - Build phylogenetic tree
- `POST /api/genetic/compare/{subtype}` - Compare multiple sequences
- `POST /api/genetic/zoonotic-potential/{subtype}` - Assess zoonotic risk
- `POST /api/genetic/antigenic-properties/{subtype}` - Predict antigenic properties

### Transmission Analysis API

- `POST /api/genetic/transmission-dynamics` - Analyze transmission dynamics
- `POST /api/genetic/transmission-network` - Infer transmission network
- `POST /api/genetic/transmission-pattern` - Assess transmission pattern
- `POST /api/genetic/spread-trajectory` - Predict spread trajectory

### Federation API

- `GET /api/federation/dashboard` - Get federated dashboard data
- `GET /api/federation/agencies` - Get available agencies for federation
- `GET /api/federation/test/{agencyId}` - Test federation connectivity

## Component Communication

These components can communicate with each other using the following methods:

1. **Vuex State** - For managing shared application state
2. **Event Bus** - For component-to-component communication
3. **Props/Events** - For parent-child communication

## Cross-Agency Integration

These components can be integrated with data from other agencies through the federation components. To enable this:

1. Update the API composables to use the federation hub API
2. Configure the federation client in `useApiClient.js`
3. Add agency selection controls to the dashboard components

## Responsive Design

All components are designed to be responsive and work well on both desktop and mobile devices:

- Desktop: Full interactive visualizations and detailed data
- Tablet: Simplified visualizations with core functionality
- Mobile: Essential information and key metrics

## Performance Considerations

To ensure optimal performance:

1. Lazy-load components when possible
2. Use pagination for large data sets
3. Implement caching for API responses
4. Use web workers for intensive calculations
5. Optimize visualizations for performance

## Further Customization

These components can be customized by:

1. Modifying the component styles to match your HMS-MFE theme
2. Adding or removing tabs based on your specific needs
3. Extending the API composables to include additional functionality
4. Creating new visualization components using the same data sources