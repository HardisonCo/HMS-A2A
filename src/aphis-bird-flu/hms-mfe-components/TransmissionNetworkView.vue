<template>
  <div class="transmission-network-view">
    <!-- Header with action buttons -->
    <div class="is-flex is-justify-content-space-between mb-4">
      <h2 class="title is-4">Bird Flu Transmission Network Analysis</h2>
      <div class="buttons">
        <VButton color="info" @click="loadDemoData">Load Demo Data</VButton>
        <VButton color="success" :disabled="!canAnalyze" @click="analyzeTransmission">
          <span>Analyze Network</span>
          <VIcon icon="mdi:network" class="ml-2" />
        </VButton>
      </div>
    </div>

    <!-- Parameter Controls -->
    <VCard class="mb-4">
      <div class="card-content">
        <div class="columns is-multiline">
          <div class="column is-4">
            <VField label="Temporal Window (days)">
              <VControl>
                <VInput
                  v-model="temporalWindow"
                  type="number"
                  min="1"
                  max="90"
                />
              </VControl>
              <p class="help">Maximum time between linked cases</p>
            </VField>
          </div>
          <div class="column is-4">
            <VField label="Spatial Threshold (km)">
              <VControl>
                <VInput
                  v-model="spatialThreshold"
                  type="number"
                  min="1"
                  max="500"
                />
              </VControl>
              <p class="help">Maximum distance between linked cases</p>
            </VField>
          </div>
          <div class="column is-4">
            <VField label="Genetic Threshold">
              <VControl>
                <VInput
                  v-model="geneticThreshold"
                  type="number"
                  min="0.01"
                  max="0.2"
                  step="0.01"
                />
              </VControl>
              <p class="help">Maximum genetic distance (0-1)</p>
            </VField>
          </div>
        </div>
      </div>
    </VCard>

    <!-- Results display (when available) -->
    <div v-if="isLoading" class="has-text-centered my-6">
      <VLoader size="large" />
      <p class="mt-2">Analyzing transmission network...</p>
    </div>

    <div v-if="analysisResults && !isLoading">
      <div class="columns mb-4">
        <!-- Pattern Assessment Card -->
        <div class="column is-4">
          <VCard>
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:chart-bubble" class="mr-2" />
                Transmission Pattern
              </div>
            </template>
            <div class="p-4">
              <div class="mb-4">
                <div class="is-flex is-align-items-center mb-2">
                  <span class="has-text-weight-bold mr-2">Pattern Type:</span>
                  <VTag :color="getPatternColor(patternAssessment.pattern_type)">
                    {{ formatPatternType(patternAssessment.pattern_type) }}
                  </VTag>
                </div>
                <div class="is-flex is-align-items-center mb-2">
                  <span class="has-text-weight-bold mr-2">Geographic Focus:</span>
                  <VTag :color="getGeographicColor(patternAssessment.geographic_focus)">
                    {{ formatValue(patternAssessment.geographic_focus) }}
                  </VTag>
                </div>
                <div class="is-flex is-align-items-center mb-2">
                  <span class="has-text-weight-bold mr-2">Temporal Pattern:</span>
                  <VTag :color="getTemporalColor(patternAssessment.temporal_pattern)">
                    {{ formatValue(patternAssessment.temporal_pattern) }}
                  </VTag>
                </div>
                <div class="is-flex is-align-items-center">
                  <span class="has-text-weight-bold mr-2">Transmission Intensity:</span>
                  <VTag :color="getIntensityColor(patternAssessment.transmission_intensity)">
                    {{ formatValue(patternAssessment.transmission_intensity) }}
                  </VTag>
                </div>
              </div>

              <div v-if="patternAssessment.superspreading_evidence" class="notification is-warning is-light">
                <div class="is-flex is-align-items-center">
                  <VIcon icon="mdi:alert-circle" class="mr-2" />
                  <strong>Superspreading evidence detected</strong>
                </div>
              </div>
            </div>
          </VCard>
        </div>

        <!-- Network Metrics Card -->
        <div class="column is-4">
          <VCard>
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:chart-line" class="mr-2" />
                Network Metrics
              </div>
            </template>
            <div class="p-4">
              <table class="table is-fullwidth">
                <tbody>
                  <tr>
                    <td class="has-text-weight-bold">Cases</td>
                    <td>{{ networkMetrics.node_count || 0 }}</td>
                  </tr>
                  <tr>
                    <td class="has-text-weight-bold">Links</td>
                    <td>{{ networkMetrics.edge_count || 0 }}</td>
                  </tr>
                  <tr>
                    <td class="has-text-weight-bold">Density</td>
                    <td>{{ formatNumber(networkMetrics.density) }}</td>
                  </tr>
                  <tr>
                    <td class="has-text-weight-bold">Components</td>
                    <td>{{ networkMetrics.component_count || 0 }}</td>
                  </tr>
                  <tr>
                    <td class="has-text-weight-bold">Largest Component</td>
                    <td>{{ networkMetrics.largest_component_size || 0 }} cases</td>
                  </tr>
                  <tr>
                    <td class="has-text-weight-bold">Avg Path Length</td>
                    <td>{{ formatNumber(networkMetrics.average_path_length) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </VCard>
        </div>

        <!-- Interventions Card -->
        <div class="column is-4">
          <VCard>
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:shield-alert" class="mr-2" />
                Recommended Interventions
              </div>
              <VTag :color="getInterventionColor(interventions.priority_level)" class="mr-2">
                {{ formatValue(interventions.priority_level) }} Priority
              </VTag>
            </template>
            <div class="p-4">
              <div class="mb-3">
                <h4 class="title is-6 mb-2">Surveillance</h4>
                <ul class="ml-4">
                  <li v-for="(item, index) in interventions.surveillance" :key="`surv-${index}`" class="mb-1">
                    <div class="is-flex is-align-items-center">
                      <VIcon icon="mdi:checkbox-marked-circle-outline" size="small" class="mr-1" />
                      {{ item }}
                    </div>
                  </li>
                </ul>
              </div>

              <div>
                <h4 class="title is-6 mb-2">Control Measures</h4>
                <ul class="ml-4">
                  <li v-for="(item, index) in interventions.control" :key="`ctrl-${index}`" class="mb-1">
                    <div class="is-flex is-align-items-center">
                      <VIcon icon="mdi:checkbox-marked-circle-outline" size="small" class="mr-1" />
                      {{ item }}
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </VCard>
        </div>
      </div>

      <!-- Network Visualization -->
      <VCard class="mb-4">
        <template #header>
          <div class="card-header-title">
            <VIcon icon="mdi:graph" class="mr-2" />
            Transmission Network Visualization
          </div>
        </template>
        <div ref="networkContainer" class="network-container"></div>
      </VCard>

      <!-- Bottom Cards -->
      <div class="columns">
        <!-- Potential Index Cases -->
        <div class="column is-6">
          <VCard>
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:source-branch" class="mr-2" />
                Potential Index Cases
              </div>
            </template>
            <div class="px-2">
              <VFlexTable :data="indexCases" :columns="indexColumns">
                <template #cell-index_score="{ row }">
                  <VProgress
                    :value="row.index_score * 100"
                    size="tiny"
                    :color="getScoreColor(row.index_score)"
                  >
                    {{ (row.index_score * 100).toFixed(0) }}%
                  </VProgress>
                </template>
              </VFlexTable>
            </div>
          </VCard>
        </div>

        <!-- Superspreaders -->
        <div class="column is-6">
          <VCard>
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:virus" class="mr-2" />
                Potential Superspreaders
              </div>
            </template>
            <div class="px-2">
              <VFlexTable :data="superspreaders" :columns="spreaderColumns">
                <template #cell-superspreader_score="{ row }">
                  <VProgress
                    :value="row.superspreader_score * 20"
                    size="tiny"
                    :color="getScoreColor(row.superspreader_score / 5)"
                  >
                    {{ row.superspreader_score.toFixed(1) }}
                  </VProgress>
                </template>
              </VFlexTable>
            </div>
          </VCard>
        </div>
      </div>
    </div>

    <!-- Error display -->
    <VMessage v-if="error" color="danger" class="my-4">
      <p>{{ error }}</p>
    </VMessage>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useTransmissionAnalysisApi } from '@/composables/useTransmissionAnalysisApi'

// State
const temporalWindow = ref(30)
const spatialThreshold = ref(100)
const geneticThreshold = ref(0.05)
const isLoading = ref(false)
const analysisResults = ref(null)
const error = ref(null)
const networkContainer = ref(null)
let networkChart = null

// API client
const { analyzeTransmission: apiAnalyzeTransmission } = useTransmissionAnalysisApi()

// Computed properties
const canAnalyze = computed(() => {
  return temporalWindow.value > 0 && spatialThreshold.value > 0 && geneticThreshold.value > 0
})

const networkMetrics = computed(() => {
  return analysisResults.value?.transmission_network?.network_metrics || {}
})

const patternAssessment = computed(() => {
  return analysisResults.value?.pattern_assessment || {}
})

const interventions = computed(() => {
  return patternAssessment.value?.intervention_recommendations || {
    surveillance: [],
    control: [],
    priority_level: 'standard'
  }
})

const indexCases = computed(() => {
  return (analysisResults.value?.transmission_network?.index_cases || []).slice(0, 5)
})

const superspreaders = computed(() => {
  return (analysisResults.value?.transmission_network?.superspreaders || []).slice(0, 5)
})

// Table configurations
const indexColumns = [
  {
    label: 'Case ID',
    field: 'case_id',
    width: '30%'
  },
  {
    label: 'Outbreak Size',
    field: 'outbreak_size',
    width: '25%'
  },
  {
    label: 'Index Score',
    field: 'index_score',
    width: '45%'
  }
]

const spreaderColumns = [
  {
    label: 'Case ID',
    field: 'case_id',
    width: '30%'
  },
  {
    label: 'Outgoing Links',
    field: 'outgoing_links',
    width: '25%'
  },
  {
    label: 'Score',
    field: 'superspreader_score',
    width: '45%'
  }
]

// Methods
async function analyzeTransmission() {
  if (!canAnalyze.value) return
  
  isLoading.value = true
  error.value = null
  
  try {
    analysisResults.value = await apiAnalyzeTransmission({
      temporalWindow: temporalWindow.value,
      spatialThreshold: spatialThreshold.value,
      geneticThreshold: geneticThreshold.value
    })
    
    // Create visualization after analysis is complete
    setTimeout(() => {
      renderNetworkVisualization()
    }, 100)
  } catch (err) {
    error.value = err.message || 'Failed to analyze transmission network'
    analysisResults.value = null
  } finally {
    isLoading.value = false
  }
}

function loadDemoData() {
  // Set default parameters
  temporalWindow.value = 30
  spatialThreshold.value = 100
  geneticThreshold.value = 0.05
  
  // Load demo data and analyze
  analyzeTransmission()
}

function renderNetworkVisualization() {
  if (!analysisResults.value || !networkContainer.value) return
  
  try {
    // Import visualization library dynamically
    import('force-graph').then(({ default: ForceGraph }) => {
      // Parse network data
      const network = analysisResults.value.transmission_network
      const nodes = []
      const nodeMap = new Map()
      const links = []
      
      // Create nodes
      network.cases.forEach(caseId => {
        const isIndex = network.index_cases.some(indexCase => indexCase.case_id === caseId)
        const isSuperSpreader = network.superspreaders.some(spreader => spreader.case_id === caseId)
        
        nodes.push({
          id: caseId,
          isIndex,
          isSuperSpreader
        })
        
        nodeMap.set(caseId, nodes.length - 1)
      })
      
      // Create links
      network.links.forEach(link => {
        links.push({
          source: link.source,
          target: link.target,
          value: link.likelihood,
          distance: link.distance_km,
          days: link.days_apart
        })
      })
      
      // Clear previous chart
      if (networkChart) {
        networkChart._destructor()
      }
      
      // Create force-directed graph
      networkContainer.value.innerHTML = ''
      networkChart = ForceGraph()(networkContainer.value)
        .width(networkContainer.value.offsetWidth)
        .height(600)
        .nodeId('id')
        .nodeVal(node => node.isSuperSpreader ? 8 : node.isIndex ? 6 : 4)
        .nodeLabel(node => `Case ID: ${node.id}${node.isIndex ? ' (Index)' : ''}${node.isSuperSpreader ? ' (Super-spreader)' : ''}`)
        .nodeColor(node => node.isIndex ? '#ff3860' : node.isSuperSpreader ? '#ffdd57' : '#3e8ed0')
        .linkWidth(link => link.value * 5)
        .linkLabel(link => `Likelihood: ${(link.value * 100).toFixed(0)}%, Distance: ${link.distance.toFixed(1)} km, Days: ${link.days}`)
        .linkDirectionalArrowLength(6)
        .linkDirectionalArrowRelPos(0.7)
        .graphData({ nodes, links })
    })
  } catch (err) {
    console.error('Failed to render network visualization:', err)
  }
}

// Helper functions
function formatPatternType(type) {
  return type.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

function formatValue(value) {
  if (!value) return 'Unknown'
  return value.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

function formatNumber(value) {
  if (value === undefined || value === null) return 'N/A'
  return typeof value === 'number' ? value.toFixed(2) : value
}

function getPatternColor(type) {
  const colors = {
    'common_source': 'info',
    'multiple_introductions': 'warning',
    'sustained_transmission': 'danger',
    'sporadic': 'primary'
  }
  return colors[type] || 'primary'
}

function getGeographicColor(focus) {
  const colors = {
    'local': 'info',
    'regional': 'warning',
    'widespread': 'danger'
  }
  return colors[focus] || 'primary'
}

function getTemporalColor(pattern) {
  const colors = {
    'rapid': 'danger',
    'moderate': 'warning',
    'extended': 'info'
  }
  return colors[pattern] || 'primary'
}

function getIntensityColor(intensity) {
  const colors = {
    'low': 'info',
    'moderate': 'warning',
    'high': 'danger'
  }
  return colors[intensity] || 'primary'
}

function getInterventionColor(level) {
  const colors = {
    'standard': 'info',
    'high': 'warning',
    'very high': 'danger'
  }
  return colors[level] || 'primary'
}

function getScoreColor(score) {
  if (score > 0.7) return 'danger'
  if (score > 0.4) return 'warning'
  return 'info'
}

// Responsive handling
onMounted(() => {
  if (networkContainer.value) {
    const resizeObserver = new ResizeObserver(() => {
      if (networkChart) {
        networkChart.width(networkContainer.value.offsetWidth)
      }
    })
    
    resizeObserver.observe(networkContainer.value)
  }
})

// Clean up on unmount
onUnmounted(() => {
  if (networkChart) {
    networkChart._destructor()
  }
})
</script>

<style scoped>
.transmission-network-view {
  max-width: 1200px;
  margin: 0 auto;
}

.network-container {
  height: 600px;
  width: 100%;
  background-color: #fafafa;
  border-radius: 0 0 6px 6px;
}
</style>