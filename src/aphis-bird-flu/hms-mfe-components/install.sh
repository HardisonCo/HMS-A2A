#!/bin/bash

# APHIS Bird Flu HMS-MFE Components Installation Script

# Configuration
HMS_MFE_DIR=${1:-"../../../SYSTEM-COMPONENTS/HMS-MFE"}
TARGET_COMPONENTS_DIR="$HMS_MFE_DIR/src/components/aphis"
TARGET_COMPOSABLES_DIR="$HMS_MFE_DIR/src/composables/aphis"

# Welcome message
echo "==================================================="
echo "APHIS Bird Flu HMS-MFE Components Installation"
echo "==================================================="
echo "Installing components to: $HMS_MFE_DIR"
echo

# Verify HMS-MFE directory exists
if [ ! -d "$HMS_MFE_DIR" ]; then
  echo "Error: HMS-MFE directory not found at $HMS_MFE_DIR"
  echo "Please provide the correct path to the HMS-MFE directory as an argument."
  echo "Example: ./install.sh /path/to/hms-mfe"
  exit 1
fi

# Create target directories
echo "Creating target directories..."
mkdir -p "$TARGET_COMPONENTS_DIR/tabs"
mkdir -p "$TARGET_COMPOSABLES_DIR"

# Copy component files
echo "Copying components..."
cp *.vue "$TARGET_COMPONENTS_DIR/"
cp tabs/*.vue "$TARGET_COMPONENTS_DIR/tabs/"
cp index.js "$TARGET_COMPONENTS_DIR/"

# Copy composable files
echo "Copying composables..."
cp composables/*.js "$TARGET_COMPOSABLES_DIR/"

# Update agency module mapping
echo "Updating agency module mapping..."
if [ -f "$HMS_MFE_DIR/agency.module.mapping.json" ]; then
  echo "Adding APHIS to agency module mapping..."
  # This is a simplified approach - in a real script, you would use jq or another tool
  # to properly modify the JSON file without potentially corrupting it
  echo "NOTE: Please manually add APHIS to the agency.module.mapping.json file"
  echo "Use the example in the README.md file for guidance."
else
  echo "Warning: agency.module.mapping.json not found. Please add APHIS manually."
fi

# Install dependencies
echo "Installing dependencies..."
cd "$HMS_MFE_DIR"
pnpm add mapbox-gl apexcharts vue3-apexcharts force-graph d3

# Update environment files
echo "Updating environment files..."
if [ ! -f "$HMS_MFE_DIR/.env.development" ]; then
  echo "Creating .env.development file..."
  echo "VITE_API_BASE_URL=http://localhost:8000" > "$HMS_MFE_DIR/.env.development"
  echo "VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here" >> "$HMS_MFE_DIR/.env.development"
else
  echo "NOTE: Please ensure your .env.development file contains the following variables:"
  echo "VITE_API_BASE_URL=http://localhost:8000"
  echo "VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here"
fi

if [ ! -f "$HMS_MFE_DIR/.env.production" ]; then
  echo "Creating .env.production file..."
  echo "VITE_API_BASE_URL=https://api.aphis.usda.gov-ai.co" > "$HMS_MFE_DIR/.env.production"
  echo "VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here" >> "$HMS_MFE_DIR/.env.production"
else
  echo "NOTE: Please ensure your .env.production file contains the following variables:"
  echo "VITE_API_BASE_URL=https://api.aphis.usda.gov-ai.co"
  echo "VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here"
fi

# Add import to main.js or main.ts
echo "Adding component registration to main file..."
MAIN_FILE=""
if [ -f "$HMS_MFE_DIR/src/main.ts" ]; then
  MAIN_FILE="$HMS_MFE_DIR/src/main.ts"
elif [ -f "$HMS_MFE_DIR/src/main.js" ]; then
  MAIN_FILE="$HMS_MFE_DIR/src/main.js"
else
  echo "Warning: Could not find main.ts or main.js file. Please register components manually."
fi

if [ -n "$MAIN_FILE" ]; then
  echo "Detected main file: $MAIN_FILE"
  echo "NOTE: Please add the following import to your main file:"
  echo "import { registerComponents } from './components/aphis';"
  echo "registerComponents(app);"
fi

# Create APHIS routes file
echo "Creating routes file..."
ROUTES_DIR="$HMS_MFE_DIR/src/router"
mkdir -p "$ROUTES_DIR"

if [ ! -f "$ROUTES_DIR/aphis.routes.js" ]; then
  cat > "$ROUTES_DIR/aphis.routes.js" << 'EOF'
/**
 * APHIS Bird Flu routes configuration
 */

// Import components
import { 
  SequenceAnalysisView, 
  TransmissionNetworkView, 
  DashboardView 
} from '@/components/aphis'

// APHIS Routes
const aphisRoutes = [
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

export default aphisRoutes
EOF
  echo "Created aphis.routes.js"
else
  echo "aphis.routes.js already exists. Not overwriting."
fi

# Final instructions
echo
echo "==================================================="
echo "Installation complete!"
echo "==================================================="
echo
echo "Next steps:"
echo "1. Add APHIS to the agency.module.mapping.json file"
echo "2. Update your main file to register the components"
echo "3. Import the APHIS routes in your router configuration"
echo "4. Set your Mapbox API token in the environment files"
echo "5. Rebuild the application"
echo
echo "For detailed instructions, refer to the README.md file"
echo "==================================================="

exit 0