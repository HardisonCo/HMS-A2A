const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();
const port = 8000;

// Enable CORS
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Load mock data
const dashboardData = JSON.parse(fs.readFileSync(path.join(__dirname, 'dashboard.json'), 'utf8'));
const geneticData = JSON.parse(fs.readFileSync(path.join(__dirname, 'genetic.json'), 'utf8'));
const transmissionData = JSON.parse(fs.readFileSync(path.join(__dirname, 'transmission.json'), 'utf8'));

// Dashboard API endpoints
app.get('/api/dashboard', (req, res) => {
  console.log('GET /api/dashboard');
  res.json(dashboardData);
});

app.get('/api/dashboard/map', (req, res) => {
  console.log('GET /api/dashboard/map');
  res.json(dashboardData.outbreakLocations);
});

app.get('/api/dashboard/trends', (req, res) => {
  console.log('GET /api/dashboard/trends');
  res.json(dashboardData.trendData);
});

app.get('/api/dashboard/alerts', (req, res) => {
  console.log('GET /api/dashboard/alerts');
  res.json(dashboardData.alerts);
});

app.get('/api/dashboard/recent', (req, res) => {
  console.log('GET /api/dashboard/recent');
  res.json(dashboardData.recentOutbreaks);
});

app.get('/api/dashboard/subtypes', (req, res) => {
  console.log('GET /api/dashboard/subtypes');
  res.json(dashboardData.subtypeDistribution);
});

app.get('/api/dashboard/mock', (req, res) => {
  console.log('GET /api/dashboard/mock');
  res.json(dashboardData);
});

// Genetic API endpoints
app.post('/api/genetic/sequence/:subtype', (req, res) => {
  console.log(`POST /api/genetic/sequence/${req.params.subtype}`);
  
  // Clone genetic data and adjust subtype if needed
  const data = JSON.parse(JSON.stringify(geneticData));
  data.subtype = req.params.subtype;
  
  // Add gene if provided
  if (req.query.gene) {
    data.gene = req.query.gene;
  }
  
  res.json(data);
});

app.post('/api/genetic/mutations/:subtype', (req, res) => {
  console.log(`POST /api/genetic/mutations/${req.params.subtype}`);
  
  // Get mutations for the given subtype
  res.json(geneticData.mutations);
});

app.post('/api/genetic/phylogenetic-tree/:subtype', (req, res) => {
  console.log(`POST /api/genetic/phylogenetic-tree/${req.params.subtype}`);
  
  // Mock phylogenetic tree data
  res.json({
    method: req.query.method || 'upgma',
    root: {
      id: 'root',
      children: ['seq1', 'seq2', 'seq3', 'seq4', 'seq5']
    },
    branch_lengths: {
      'root_seq1': 0.01,
      'root_seq2': 0.02,
      'seq2_seq3': 0.005,
      'seq3_seq4': 0.01,
      'root_seq5': 0.03
    },
    topology: 'mock_topology_for_demonstration',
    sequence_count: 5
  });
});

app.post('/api/genetic/compare/:subtype', (req, res) => {
  console.log(`POST /api/genetic/compare/${req.params.subtype}`);
  
  // Mock sequence comparison data
  res.json({
    sequence_count: Object.keys(req.body.sequences || {}).length,
    average_length: 1500,
    pairwise_distances: {
      'seq1_seq2': 0.05,
      'seq1_seq3': 0.07,
      'seq2_seq3': 0.03
    },
    most_similar_pair: {
      ids: ['seq2', 'seq3'],
      distance: 0.03
    },
    least_similar_pair: {
      ids: ['seq1', 'seq3'],
      distance: 0.07
    },
    unique_mutations: {
      'seq1': ['A123G', 'T156A'],
      'seq2': ['G223C'],
      'seq3': ['T96I']
    },
    shared_mutations: ['E627K', 'D701N'],
    analysis_timestamp: new Date().toISOString()
  });
});

app.post('/api/genetic/zoonotic-potential/:subtype', (req, res) => {
  console.log(`POST /api/genetic/zoonotic-potential/${req.params.subtype}`);
  
  // Return zoonotic potential from the genetic data
  res.json(geneticData.zoonotic_potential);
});

app.post('/api/genetic/antigenic-properties/:subtype', (req, res) => {
  console.log(`POST /api/genetic/antigenic-properties/${req.params.subtype}`);
  
  // Return antigenic properties from the genetic data
  res.json(geneticData.antigenic_properties);
});

// Transmission API endpoints
app.post('/api/genetic/transmission-dynamics', (req, res) => {
  console.log('POST /api/genetic/transmission-dynamics');
  
  // Return full transmission analysis
  res.json(transmissionData);
});

app.post('/api/genetic/transmission-network', (req, res) => {
  console.log('POST /api/genetic/transmission-network');
  
  // Return just the transmission network
  res.json(transmissionData.transmission_network);
});

app.post('/api/genetic/transmission-pattern', (req, res) => {
  console.log('POST /api/genetic/transmission-pattern');
  
  // Return just the pattern assessment
  res.json(transmissionData.pattern_assessment);
});

app.post('/api/genetic/spread-trajectory', (req, res) => {
  console.log('POST /api/genetic/spread-trajectory');
  
  // Return just the trajectory prediction
  res.json(transmissionData.trajectory_prediction);
});

// Federation API endpoints
app.get('/api/federation/dashboard', (req, res) => {
  console.log('GET /api/federation/dashboard');
  
  // Get agencies from query params
  const agencies = (req.query.agencies || '').split(',');
  console.log(`Requested agencies: ${agencies.join(', ')}`);
  
  // Return the dashboard data with a federation note
  const federated = JSON.parse(JSON.stringify(dashboardData));
  federated.federationNote = `Federated data from ${agencies.join(', ')}`;
  
  res.json(federated);
});

app.get('/api/federation/agencies', (req, res) => {
  console.log('GET /api/federation/agencies');
  
  // Return available agencies
  res.json([
    {
      id: 'aphis',
      name: 'APHIS',
      description: 'Animal and Plant Health Inspection Service',
      capabilities: ['genetic_analysis', 'outbreak_monitoring', 'response_coordination']
    },
    {
      id: 'cdc',
      name: 'CDC',
      description: 'Centers for Disease Control and Prevention',
      capabilities: ['human_surveillance', 'outbreak_investigation', 'public_health_response']
    },
    {
      id: 'epa',
      name: 'EPA',
      description: 'Environmental Protection Agency',
      capabilities: ['environmental_monitoring', 'water_quality', 'air_quality']
    },
    {
      id: 'fema',
      name: 'FEMA',
      description: 'Federal Emergency Management Agency',
      capabilities: ['emergency_response', 'disaster_management', 'resource_coordination']
    }
  ]);
});

// Start the server
app.listen(port, () => {
  console.log(`Mock API server listening at http://localhost:${port}`);
  console.log(`Available endpoints:`);
  console.log(`- GET  /api/dashboard`);
  console.log(`- GET  /api/dashboard/map`);
  console.log(`- GET  /api/dashboard/trends`);
  console.log(`- GET  /api/dashboard/alerts`);
  console.log(`- GET  /api/dashboard/recent`);
  console.log(`- GET  /api/dashboard/subtypes`);
  console.log(`- POST /api/genetic/sequence/:subtype`);
  console.log(`- POST /api/genetic/mutations/:subtype`);
  console.log(`- POST /api/genetic/phylogenetic-tree/:subtype`);
  console.log(`- POST /api/genetic/compare/:subtype`);
  console.log(`- POST /api/genetic/zoonotic-potential/:subtype`);
  console.log(`- POST /api/genetic/antigenic-properties/:subtype`);
  console.log(`- POST /api/genetic/transmission-dynamics`);
  console.log(`- POST /api/genetic/transmission-network`);
  console.log(`- POST /api/genetic/transmission-pattern`);
  console.log(`- POST /api/genetic/spread-trajectory`);
  console.log(`- GET  /api/federation/dashboard`);
  console.log(`- GET  /api/federation/agencies`);
});