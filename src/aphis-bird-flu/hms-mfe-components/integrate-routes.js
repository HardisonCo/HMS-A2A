/**
 * Route Integration Script for HMS-MFE
 * 
 * This script integrates APHIS Bird Flu routes into the HMS-MFE router configuration.
 * Run this script after copying the components to HMS-MFE.
 */

const fs = require('fs');
const path = require('path');

// Configuration
const HMS_MFE_DIR = process.argv[2] || '../../../SYSTEM-COMPONENTS/HMS-MFE';
const ROUTER_FILE = path.join(HMS_MFE_DIR, 'src/router.ts');
const APHIS_ROUTES_FILE = path.join(HMS_MFE_DIR, 'src/router/aphis.routes.js');

// Check if router file exists
if (!fs.existsSync(ROUTER_FILE)) {
  console.error(`Error: Router file not found at ${ROUTER_FILE}`);
  console.error('Please provide the correct path to the HMS-MFE directory as an argument.');
  console.error('Example: node integrate-routes.js /path/to/hms-mfe');
  process.exit(1);
}

// Check if APHIS routes file exists
if (!fs.existsSync(APHIS_ROUTES_FILE)) {
  console.error(`Error: APHIS routes file not found at ${APHIS_ROUTES_FILE}`);
  console.error('Please ensure you have copied the aphis.routes.js file to the correct location.');
  process.exit(1);
}

// Read router file
let routerContent = fs.readFileSync(ROUTER_FILE, 'utf8');

// Check if APHIS routes are already imported
if (routerContent.includes('aphis.routes')) {
  console.log('APHIS routes are already imported. No changes needed.');
  process.exit(0);
}

// Find the import section
const importRegex = /import .+ from ['"].+['"]/g;
const lastImport = [...routerContent.matchAll(importRegex)].pop();

if (!lastImport) {
  console.error('Error: Could not find import section in router file.');
  process.exit(1);
}

// Add APHIS routes import after the last import
const aphisImport = "import aphisRoutes from './router/aphis.routes'";
routerContent = routerContent.replace(
  lastImport[0],
  `${lastImport[0]}\n${aphisImport}`
);

// Find the routes array
const routesRegex = /const routes\s*=\s*\[([\s\S]*?)\]/g;
const routesMatch = routesRegex.exec(routerContent);

if (!routesMatch) {
  console.error('Error: Could not find routes array in router file.');
  process.exit(1);
}

// Add APHIS routes to the routes array
const routesArray = routesMatch[0];
const routesClosingBracket = routesArray.lastIndexOf(']');
const routesContent = routesArray.substring(0, routesClosingBracket);

const updatedRoutesContent = `${routesContent}  ...aphisRoutes,\n]`;
routerContent = routerContent.replace(routesArray, updatedRoutesContent);

// Write the updated router file
fs.writeFileSync(ROUTER_FILE, routerContent);

console.log('APHIS routes have been successfully integrated into the HMS-MFE router configuration.');
console.log(`Updated router file: ${ROUTER_FILE}`);

// Create placeholder OutbreakDetailView.vue
const outbreakDetailViewPath = path.join(HMS_MFE_DIR, 'src/components/aphis/OutbreakDetailView.vue');
if (!fs.existsSync(outbreakDetailViewPath)) {
  const outbreakDetailViewContent = `<template>
  <div class="outbreak-detail">
    <h2 class="title is-4">Outbreak Detail</h2>
    <p>Detailed information about outbreak {{ $route.params.id }}</p>
    <p class="has-text-grey">This is a placeholder component. Implement with actual outbreak details.</p>
  </div>
</template>

<script setup>
// Outbreak detail implementation will go here
</script>`;

  fs.writeFileSync(outbreakDetailViewPath, outbreakDetailViewContent);
  console.log(`Created placeholder: ${outbreakDetailViewPath}`);
}

// Create placeholder AgencyIntegrationView.vue
const agencyIntegrationViewPath = path.join(HMS_MFE_DIR, 'src/components/aphis/AgencyIntegrationView.vue');
if (!fs.existsSync(agencyIntegrationViewPath)) {
  const agencyIntegrationViewContent = `<template>
  <div class="agency-integration">
    <h2 class="title is-4">Agency Integration</h2>
    <p>Federal agency integration management interface</p>
    <p class="has-text-grey">This is a placeholder component. Implement with actual agency integration features.</p>
  </div>
</template>

<script setup>
// Agency integration implementation will go here
</script>`;

  fs.writeFileSync(agencyIntegrationViewPath, agencyIntegrationViewContent);
  console.log(`Created placeholder: ${agencyIntegrationViewPath}`);
}

console.log('\nNext steps:');
console.log('1. Start the HMS-MFE application');
console.log('2. Navigate to /aphis/surveillance to access the APHIS Bird Flu dashboard');
console.log('3. Configure environment variables for API connections');