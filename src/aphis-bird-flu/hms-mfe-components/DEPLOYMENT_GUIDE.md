# APHIS Bird Flu HMS-MFE Deployment Guide

This guide provides detailed instructions for deploying the integrated APHIS Bird Flu tracking system with HMS-MFE.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
   - [Option 1: Docker Deployment](#option-1-docker-deployment)
   - [Option 2: Manual Deployment](#option-2-manual-deployment)
3. [Configuration](#configuration)
4. [Cross-Agency Federation Setup](#cross-agency-federation-setup)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have the following:

- **For Docker Deployment**:
  - Docker and Docker Compose installed
  - Access to the Docker registry
  - At least 2GB of free memory and 1GB of free disk space

- **For Manual Deployment**:
  - Node.js 20+
  - PNPM package manager
  - Access to the HMS-MFE repository
  - Access to the APHIS Bird Flu repository

- **For Both**:
  - Mapbox API key for map visualizations
  - APHIS API endpoints configured and accessible
  - Network connectivity between components

## Deployment Options

### Option 1: Docker Deployment

The Docker deployment is recommended for most environments as it encapsulates all dependencies and ensures consistent behavior.

1. **Clone the repositories**:
   ```bash
   git clone https://github.com/HardisonCo/HMS-MFE.git
   git clone https://github.com/HardisonCo/aphis-bird-flu.git
   ```

2. **Set up environment variables**:
   ```bash
   cd aphis-bird-flu/hms-mfe-components
   cp .env.example .env
   # Edit .env to add your Mapbox API key
   ```

3. **Start the containers**:
   ```bash
   docker-compose up -d
   ```

4. **Verify the deployment**:
   ```bash
   # Check if containers are running
   docker-compose ps
   
   # Check container logs
   docker-compose logs -f
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Mock API: http://localhost:8000
   - Federation Hub: http://localhost:9000

### Option 2: Manual Deployment

If you prefer to deploy without Docker, follow these steps:

1. **Clone the HMS-MFE repository**:
   ```bash
   git clone https://github.com/HardisonCo/HMS-MFE.git
   cd HMS-MFE
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```

3. **Copy APHIS Bird Flu components**:
   ```bash
   # Clone the APHIS Bird Flu repository
   git clone https://github.com/HardisonCo/aphis-bird-flu.git
   
   # Run the installation script
   cd aphis-bird-flu/hms-mfe-components
   chmod +x install.sh
   ./install.sh ../../HMS-MFE
   ```

4. **Configure environment variables**:
   ```bash
   cd ../../HMS-MFE
   
   # Create development environment file
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env.development
   echo "VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here" >> .env.development
   echo "VITE_FEDERATION_HUB_URL=http://localhost:9000" >> .env.development
   
   # Create production environment file
   echo "VITE_API_BASE_URL=https://api.aphis.usda.gov-ai.co" > .env.production
   echo "VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here" >> .env.production
   echo "VITE_FEDERATION_HUB_URL=https://federation.usda.gov-ai.co" >> .env.production
   ```

5. **Start the development server**:
   ```bash
   pnpm dev
   ```

6. **Build for production**:
   ```bash
   pnpm ssr:build
   pnpm ssr:start
   ```

7. **Start the mock API server** (for development):
   ```bash
   cd ../aphis-bird-flu/hms-mfe-components/mock-data
   npm install
   npm start
   ```

## Configuration

### Mapbox API Key

The application requires a Mapbox API key for map visualizations:

1. Sign up for a Mapbox account at https://mapbox.com
2. Create an API key with the following permissions:
   - Styles:read
   - Fonts:read
   - Maps:read
3. Add the API key to your environment files:
   - For Docker: Update the `MAPBOX_ACCESS_TOKEN` in `.env`
   - For manual: Update `VITE_MAPBOX_ACCESS_TOKEN` in `.env.development` and `.env.production`

### Agency Module Mapping

The system uses a mapping file to define agency routes. Ensure APHIS is included in the `agency.module.mapping.json` file:

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

### API Configuration

In production, configure the API endpoints in `.env.production`:

```
VITE_API_BASE_URL=https://api.aphis.usda.gov-ai.co
```

For custom API endpoints, update the composables in `src/composables/aphis/` to match your API structure.

## Cross-Agency Federation Setup

To enable cross-agency data sharing:

1. **Deploy the Federation Hub**:
   ```bash
   cd agency-implementation/foundation/federation
   docker build -t federation-hub .
   docker run -d -p 9000:9000 --name federation-hub federation-hub
   ```

2. **Configure agency connections**:
   Edit `agencies.json` in the Federation Hub to include all participating agencies:
   ```json
   [
     {
       "id": "aphis",
       "name": "APHIS",
       "description": "Animal and Plant Health Inspection Service",
       "apiEndpoint": "https://api.aphis.usda.gov-ai.co",
       "apiKey": "YOUR_API_KEY",
       "capabilities": ["genetic_analysis", "outbreak_monitoring"]
     },
     {
       "id": "cdc",
       "name": "CDC",
       "description": "Centers for Disease Control and Prevention",
       "apiEndpoint": "https://api.cdc.gov-ai.co",
       "apiKey": "CDC_API_KEY",
       "capabilities": ["human_surveillance", "outbreak_investigation"]
     }
   ]
   ```

3. **Enable federation in the APHIS components**:
   In the dashboard component, enable the federation selector to allow users to choose data sources.

## Monitoring and Maintenance

### Health Checks

All components include health endpoints for monitoring:

- HMS-MFE: `http://localhost:3000/health`
- Mock API: `http://localhost:8000/health`
- Federation Hub: `http://localhost:9000/health`

You can integrate these with your monitoring system for automated alerts.

### Logs

Access logs through Docker Compose:

```bash
# View all logs
docker-compose logs

# View logs for a specific service
docker-compose logs hms-mfe
docker-compose logs mock-api
docker-compose logs federation-hub

# Follow logs
docker-compose logs -f
```

### Updates

To update the components:

1. Pull the latest code:
   ```bash
   git pull
   ```

2. Rebuild the containers:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## Troubleshooting

### Common Issues

1. **Map Visualization Not Loading**:
   - Check that the Mapbox API key is correctly set
   - Verify network access to Mapbox services
   - Check browser console for errors

2. **API Connection Failures**:
   - Verify the API server is running
   - Check that the `VITE_API_BASE_URL` is set correctly
   - Ensure network connectivity between the frontend and API

3. **Federation Issues**:
   - Verify the Federation Hub is running
   - Check agency configurations in `agencies.json`
   - Ensure all participating agencies have proper API keys

4. **Container Startup Failures**:
   - Check container logs for error messages
   - Verify port availability (ports 3000, 8000, and 9000 must be free)
   - Ensure sufficient system resources

### Getting Help

If you encounter issues not covered here:

1. Check the HMS-MFE documentation
2. Review the APHIS Bird Flu system documentation
3. Open an issue on the repository
4. Contact the development team at support@hardisonco.com