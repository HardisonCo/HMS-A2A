<template>
  <div class="dashboard-view">
    <!-- Header with filters and controls -->
    <div class="is-flex is-justify-content-space-between mb-4">
      <h2 class="title is-4">Bird Flu Surveillance Dashboard</h2>
      <div class="buttons">
        <VButton v-if="showFederationSelector" color="warning" @click="toggleFederationSelector">
          <VIcon icon="mdi:database-sync" class="mr-2" />
          <span>Federation</span>
        </VButton>
        <VButton color="info" @click="reloadData">
          <VIcon icon="mdi:refresh" class="mr-2" />
          <span>Refresh</span>
        </VButton>
        <VButton color="primary" @click="openFilterPanel">
          <VIcon icon="mdi:filter-variant" class="mr-2" />
          <span>Filter</span>
        </VButton>
      </div>
    </div>

    <!-- Federation Selector Modal -->
    <VModal :open="federationSelectorOpen" @close="toggleFederationSelector" title="Data Federation Sources">
      <div class="federation-controls mb-4">
        <h4 class="title is-5 mb-3">Select Agency Data Sources</h4>
        <div class="field">
          <VCheckbox v-model="dataSources.aphis" label="APHIS (Animal Health)" />
          <p class="help">Avian influenza surveillance in domestic and wild bird populations</p>
        </div>
        <div class="field">
          <VCheckbox v-model="dataSources.cdc" label="CDC (Human Health)" />
          <p class="help">Human case data and human-animal interface surveillance</p>
        </div>
        <div class="field">
          <VCheckbox v-model="dataSources.epa" label="EPA (Environmental)" />
          <p class="help">Environmental sampling and water monitoring data</p>
        </div>
        <div class="field">
          <VCheckbox v-model="dataSources.fema" label="FEMA (Response)" />
          <p class="help">Resource deployment and emergency response data</p>
        </div>
        <div class="mt-4">
          <VButton color="primary" @click="applyFederationSettings">
            Apply Settings
          </VButton>
        </div>
      </div>
    </VModal>

    <!-- Filter Panel Modal -->
    <VModal :open="filterPanelOpen" @close="closeFilterPanel" title="Filter Dashboard Data">
      <div class="filter-controls">
        <div class="columns is-multiline">
          <div class="column is-6">
            <VField label="Date Range">
              <VControl>
                <Datepicker
                  v-model="dateRange"
                  mode="range"
                  :max-date="new Date()"
                  :month-name-format="'long'"
                />
              </VControl>
            </VField>
          </div>
          <div class="column is-6">
            <VField label="Region">
              <VControl>
                <VSelect
                  v-model="selectedRegion"
                  :options="regionOptions"
                />
              </VControl>
            </VField>
          </div>
          <div class="column is-6">
            <VField label="Virus Subtype">
              <VControl>
                <VSelect
                  v-model="selectedSubtype"
                  :options="subtypeOptions"
                />
              </VControl>
            </VField>
          </div>
          <div class="column is-6">
            <VField label="Severity Level">
              <VControl>
                <VSelect
                  v-model="selectedSeverity"
                  :options="severityOptions"
                />
              </VControl>
            </VField>
          </div>
        </div>
        <div class="is-flex is-justify-content-flex-end mt-4">
          <VButton color="danger" class="mr-2" outlined @click="resetFilters">
            Reset
          </VButton>
          <VButton color="primary" @click="applyFilters">
            Apply Filters
          </VButton>
        </div>
      </div>
    </VModal>

    <!-- Quick Filters Bar -->
    <div class="quick-filters mb-4">
      <VCard class="p-2">
        <div class="is-flex is-flex-wrap-wrap is-align-items-center">
          <div class="mr-4 mb-2">
            <span class="has-text-weight-bold">Quick Filters:</span>
          </div>
          <div class="is-flex is-flex-wrap-wrap">
            <VButton
              size="small"
              class="mr-2 mb-2"
              :color="activeQuickFilter === 'last7days' ? 'primary' : 'light'"
              @click="applyQuickFilter('last7days')"
            >
              Last 7 Days
            </VButton>
            <VButton
              size="small"
              class="mr-2 mb-2"
              :color="activeQuickFilter === 'last30days' ? 'primary' : 'light'"
              @click="applyQuickFilter('last30days')"
            >
              Last 30 Days
            </VButton>
            <VButton
              size="small"
              class="mr-2 mb-2"
              :color="activeQuickFilter === 'h5n1' ? 'primary' : 'light'"
              @click="applyQuickFilter('h5n1')"
            >
              H5N1 Only
            </VButton>
            <VButton
              size="small"
              class="mr-2 mb-2"
              :color="activeQuickFilter === 'high' ? 'primary' : 'light'"
              @click="applyQuickFilter('high')"
            >
              High Severity
            </VButton>
            <VButton
              size="small"
              class="mr-2 mb-2"
              :color="activeQuickFilter === 'clear' ? 'primary' : 'light'"
              @click="applyQuickFilter('clear')"
            >
              Clear All
            </VButton>
          </div>
        </div>
      </VCard>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="has-text-centered my-6">
      <VLoader size="large" />
      <p class="mt-2">Loading dashboard data...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Summary Cards -->
      <div class="columns is-multiline mb-4">
        <div class="column is-3">
          <VCard class="summary-card">
            <div class="has-text-centered p-4">
              <div class="summary-icon">
                <VIcon icon="mdi:virus" size="large" color="danger" />
              </div>
              <h3 class="title is-4 mt-2">{{ dashboardData.totalCases }}</h3>
              <p class="subtitle is-6">Total Outbreaks</p>
              <div class="trend is-flex is-align-items-center is-justify-content-center" :class="getTrendClass(dashboardData.caseTrend)">
                <VIcon :icon="getTrendIcon(dashboardData.caseTrend)" size="small" class="mr-1" />
                <span>{{ dashboardData.caseTrend }}%</span>
              </div>
            </div>
          </VCard>
        </div>
        <div class="column is-3">
          <VCard class="summary-card">
            <div class="has-text-centered p-4">
              <div class="summary-icon">
                <VIcon icon="mdi:dna" size="large" color="warning" />
              </div>
              <h3 class="title is-4 mt-2">{{ dashboardData.sequencedCases }}</h3>
              <p class="subtitle is-6">Sequenced Samples</p>
              <div class="trend is-flex is-align-items-center is-justify-content-center" :class="getTrendClass(dashboardData.sequenceTrend)">
                <VIcon :icon="getTrendIcon(dashboardData.sequenceTrend)" size="small" class="mr-1" />
                <span>{{ dashboardData.sequenceTrend }}%</span>
              </div>
            </div>
          </VCard>
        </div>
        <div class="column is-3">
          <VCard class="summary-card">
            <div class="has-text-centered p-4">
              <div class="summary-icon">
                <VIcon icon="mdi:map-marker-alert" size="large" color="info" />
              </div>
              <h3 class="title is-4 mt-2">{{ dashboardData.affectedRegions }}</h3>
              <p class="subtitle is-6">Affected Regions</p>
              <div class="trend is-flex is-align-items-center is-justify-content-center" :class="getTrendClass(dashboardData.regionTrend)">
                <VIcon :icon="getTrendIcon(dashboardData.regionTrend)" size="small" class="mr-1" />
                <span>{{ dashboardData.regionTrend }}%</span>
              </div>
            </div>
          </VCard>
        </div>
        <div class="column is-3">
          <VCard class="summary-card">
            <div class="has-text-centered p-4">
              <div class="summary-icon">
                <VIcon icon="mdi:alert-circle" size="large" color="danger" />
              </div>
              <h3 class="title is-4 mt-2">{{ dashboardData.highRiskCases }}</h3>
              <p class="subtitle is-6">High Risk Cases</p>
              <div class="trend is-flex is-align-items-center is-justify-content-center" :class="getTrendClass(dashboardData.riskTrend)">
                <VIcon :icon="getTrendIcon(dashboardData.riskTrend)" size="small" class="mr-1" />
                <span>{{ dashboardData.riskTrend }}%</span>
              </div>
            </div>
          </VCard>
        </div>
      </div>

      <!-- Main Dashboard Grid -->
      <div class="columns is-multiline">
        <!-- Map View -->
        <div class="column is-8">
          <VCard class="mb-4">
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:map" class="mr-2" />
                Outbreak Map
              </div>
            </template>
            <div ref="mapContainer" class="map-container"></div>
          </VCard>
        </div>

        <!-- Recent Outbreaks -->
        <div class="column is-4">
          <VCard class="mb-4">
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:calendar-alert" class="mr-2" />
                Recent Outbreaks
              </div>
            </template>
            <div class="p-2">
              <VFlexTable
                :data="dashboardData.recentOutbreaks"
                :columns="outbreakColumns"
                :pagination="true"
                :itemsPerPage="5"
              >
                <template #cell-subtype="{ row }">
                  <VTag :color="getSubtypeColor(row.subtype)">{{ row.subtype }}</VTag>
                </template>
                <template #cell-severity="{ row }">
                  <VTag :color="getSeverityColor(row.severity)">{{ row.severity }}</VTag>
                </template>
              </VFlexTable>
            </div>
          </VCard>
        </div>

        <!-- Trend Analysis -->
        <div class="column is-6">
          <VCard class="mb-4">
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:chart-line" class="mr-2" />
                Outbreak Trends
              </div>
            </template>
            <div class="trend-chart-container p-2">
              <div ref="trendChartContainer" style="height: 300px;"></div>
            </div>
          </VCard>
        </div>

        <!-- Subtype Distribution -->
        <div class="column is-6">
          <VCard class="mb-4">
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:chart-pie" class="mr-2" />
                Virus Subtype Distribution
              </div>
            </template>
            <div class="distribution-chart-container p-2">
              <div ref="distributionChartContainer" style="height: 300px;"></div>
            </div>
          </VCard>
        </div>

        <!-- Alerts Panel -->
        <div class="column is-12">
          <VCard class="mb-4">
            <template #header>
              <div class="card-header-title">
                <VIcon icon="mdi:bell-alert" class="mr-2" />
                Active Alerts
                <VTag color="danger" class="ml-2">{{ dashboardData.alerts.length }}</VTag>
              </div>
            </template>
            <div class="p-2">
              <div v-if="dashboardData.alerts.length === 0" class="has-text-centered p-4">
                <p>No active alerts at this time.</p>
              </div>
              <div v-else>
                <div v-for="(alert, index) in dashboardData.alerts" :key="index" class="alert-item p-3 mb-2">
                  <div class="is-flex is-align-items-center">
                    <VIcon :icon="getAlertIcon(alert.type)" :color="getAlertColor(alert.type)" class="mr-3" />
                    <div>
                      <h5 class="is-size-5 mb-1">{{ alert.title }}</h5>
                      <p>{{ alert.description }}</p>
                      <div class="is-flex is-align-items-center mt-1">
                        <VTag :color="getAlertColor(alert.type)" size="small" class="mr-2">
                          {{ alert.type }}
                        </VTag>
                        <small class="has-text-grey">{{ formatDate(alert.date) }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </VCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import mapboxgl from 'mapbox-gl'
import ApexCharts from 'apexcharts'
import { useDashboardApi } from '@/composables/aphis/useDashboardApi'
import { useFederationApi } from '@/composables/aphis/useFederationApi'

// State
const federationSelectorOpen = ref(false)
const filterPanelOpen = ref(false)
const isLoading = ref(true)
const dashboardData = ref({
  totalCases: 0,
  sequencedCases: 0,
  affectedRegions: 0,
  highRiskCases: 0,
  caseTrend: 0,
  sequenceTrend: 0,
  regionTrend: 0,
  riskTrend: 0,
  recentOutbreaks: [],
  alerts: []
})

// Filter state
const dateRange = ref(null)
const selectedRegion = ref(null)
const selectedSubtype = ref(null)
const selectedSeverity = ref(null)
const activeQuickFilter = ref(null)

// Data source selection for federation
const dataSources = ref({
  aphis: true,
  cdc: false,
  epa: false,
  fema: false
})
const showFederationSelector = ref(true)

// Refs for containers
const mapContainer = ref(null)
const trendChartContainer = ref(null)
const distributionChartContainer = ref(null)

// Options for filters
const regionOptions = [
  { value: null, label: 'All Regions' },
  { value: 'northeast', label: 'Northeast' },
  { value: 'southeast', label: 'Southeast' },
  { value: 'midwest', label: 'Midwest' },
  { value: 'southwest', label: 'Southwest' },
  { value: 'west', label: 'West' },
  { value: 'northwest', label: 'Northwest' }
]

const subtypeOptions = [
  { value: null, label: 'All Subtypes' },
  { value: 'H5N1', label: 'H5N1' },
  { value: 'H7N9', label: 'H7N9' },
  { value: 'H9N2', label: 'H9N2' },
  { value: 'H5N8', label: 'H5N8' },
  { value: 'H5N6', label: 'H5N6' }
]

const severityOptions = [
  { value: null, label: 'All Severity Levels' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' }
]

// Table configuration
const outbreakColumns = [
  {
    label: 'Date',
    field: row => formatDate(row.date),
    width: '25%'
  },
  {
    label: 'Location',
    field: 'location',
    width: '25%'
  },
  {
    label: 'Subtype',
    field: 'subtype',
    width: '25%'
  },
  {
    label: 'Severity',
    field: 'severity',
    width: '25%'
  }
]

// Chart instances
let map = null
let trendChart = null
let distributionChart = null

// API clients
const { getDashboardData } = useDashboardApi()
const { getFederatedData } = useFederationApi()

// Computed
const currentFilters = computed(() => {
  return {
    startDate: dateRange.value && dateRange.value.start ? dateRange.value.start.toISOString() : null,
    endDate: dateRange.value && dateRange.value.end ? dateRange.value.end.toISOString() : null,
    region: selectedRegion.value,
    subtype: selectedSubtype.value,
    severity: selectedSeverity.value
  }
})

// Methods
async function loadDashboardData() {
  isLoading.value = true
  
  try {
    const filters = currentFilters.value
    
    // If data federation is enabled, use federated data
    if (Object.values(dataSources.value).some(v => v)) {
      const agencySources = Object.entries(dataSources.value)
        .filter(([_, enabled]) => enabled)
        .map(([agency]) => agency)
      
      dashboardData.value = await getFederatedData({
        agencies: agencySources,
        filters
      })
    } else {
      // Otherwise just load APHIS data
      dashboardData.value = await getDashboardData(filters)
    }
    
    // Initialize or update visualizations
    initMap()
    initTrendChart()
    initDistributionChart()
  } catch (err) {
    console.error('Failed to load dashboard data:', err)
  } finally {
    isLoading.value = false
  }
}

function toggleFederationSelector() {
  federationSelectorOpen.value = !federationSelectorOpen.value
}

function applyFederationSettings() {
  toggleFederationSelector()
  loadDashboardData()
}

function openFilterPanel() {
  filterPanelOpen.value = true
}

function closeFilterPanel() {
  filterPanelOpen.value = false
}

function applyFilters() {
  closeFilterPanel()
  activeQuickFilter.value = null
  loadDashboardData()
}

function resetFilters() {
  dateRange.value = null
  selectedRegion.value = null
  selectedSubtype.value = null
  selectedSeverity.value = null
  activeQuickFilter.value = null
}

function applyQuickFilter(filterName) {
  activeQuickFilter.value = filterName
  
  const now = new Date()
  
  // Reset all filters first
  resetFilters()
  activeQuickFilter.value = filterName
  
  // Apply the specific quick filter
  switch (filterName) {
    case 'last7days':
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(now.getDate() - 7)
      dateRange.value = { start: sevenDaysAgo, end: now }
      break
      
    case 'last30days':
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(now.getDate() - 30)
      dateRange.value = { start: thirtyDaysAgo, end: now }
      break
      
    case 'h5n1':
      selectedSubtype.value = 'H5N1'
      break
      
    case 'high':
      selectedSeverity.value = 'high'
      break
      
    case 'clear':
      // Already reset above
      activeQuickFilter.value = null
      break
  }
  
  loadDashboardData()
}

function reloadData() {
  loadDashboardData()
}

function initMap() {
  if (!mapContainer.value) return
  
  if (!map) {
    // Initialize map
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
    
    map = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/mapbox/light-v10',
      center: [-95.7129, 37.0902], // Center on US
      zoom: 3
    })
    
    map.on('load', () => {
      updateMapData()
    })
  } else {
    // Update existing map
    updateMapData()
  }
}

function updateMapData() {
  if (!map || !map.loaded() || !dashboardData.value.outbreakLocations) return
  
  // Remove old layers
  if (map.getSource('outbreaks')) {
    map.removeLayer('outbreak-heat')
    map.removeLayer('outbreak-points')
    map.removeSource('outbreaks')
  }
  
  // Add new data
  map.addSource('outbreaks', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: dashboardData.value.outbreakLocations.map(location => ({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [location.longitude, location.latitude]
        },
        properties: {
          id: location.id,
          subtype: location.subtype,
          severity: location.severity,
          cases: location.cases,
          date: location.date,
          location: location.name
        }
      }))
    }
  })
  
  // Add heatmap layer
  map.addLayer({
    id: 'outbreak-heat',
    type: 'heatmap',
    source: 'outbreaks',
    paint: {
      'heatmap-weight': [
        'interpolate',
        ['linear'],
        ['get', 'cases'],
        0, 0,
        10, 1
      ],
      'heatmap-intensity': 1,
      'heatmap-color': [
        'interpolate',
        ['linear'],
        ['heatmap-density'],
        0, 'rgba(0, 0, 255, 0)',
        0.2, 'rgba(0, 255, 255, 0.6)',
        0.4, 'rgba(0, 255, 0, 0.6)',
        0.6, 'rgba(255, 255, 0, 0.6)',
        0.8, 'rgba(255, 0, 0, 0.6)'
      ],
      'heatmap-radius': 20,
      'heatmap-opacity': 0.7
    }
  })
  
  // Add point layer
  map.addLayer({
    id: 'outbreak-points',
    type: 'circle',
    source: 'outbreaks',
    paint: {
      'circle-radius': [
        'interpolate',
        ['linear'],
        ['get', 'cases'],
        1, 5,
        10, 10,
        50, 15
      ],
      'circle-color': [
        'match',
        ['get', 'severity'],
        'high', '#ff3860',
        'medium', '#ffdd57',
        'low', '#48c774',
        '#3273dc'
      ],
      'circle-opacity': 0.8,
      'circle-stroke-width': 1,
      'circle-stroke-color': '#ffffff'
    }
  })
  
  // Add popup on click
  map.on('click', 'outbreak-points', (e) => {
    const properties = e.features[0].properties
    
    new mapboxgl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(`
        <h4>${properties.location}</h4>
        <p><strong>Date:</strong> ${formatDate(properties.date)}</p>
        <p><strong>Subtype:</strong> ${properties.subtype}</p>
        <p><strong>Cases:</strong> ${properties.cases}</p>
        <p><strong>Severity:</strong> ${properties.severity}</p>
      `)
      .addTo(map)
  })
  
  // Change cursor on hover
  map.on('mouseenter', 'outbreak-points', () => {
    map.getCanvas().style.cursor = 'pointer'
  })
  
  map.on('mouseleave', 'outbreak-points', () => {
    map.getCanvas().style.cursor = ''
  })
}

function initTrendChart() {
  if (!trendChartContainer.value || !dashboardData.value.trendData) return
  
  const options = {
    series: [
      {
        name: 'Outbreaks',
        data: dashboardData.value.trendData.map(item => item.count)
      }
    ],
    chart: {
      height: 300,
      type: 'line',
      toolbar: {
        show: false
      },
      zoom: {
        enabled: false
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth',
      width: 3
    },
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5
      }
    },
    xaxis: {
      categories: dashboardData.value.trendData.map(item => formatDate(item.date)),
      labels: {
        rotate: -45,
        style: {
          fontSize: '10px'
        }
      }
    },
    yaxis: {
      title: {
        text: 'Number of Outbreaks'
      }
    },
    tooltip: {
      x: {
        format: 'dd/MM/yy'
      }
    },
    colors: ['#3273dc']
  }
  
  if (trendChart) {
    trendChart.updateOptions(options)
  } else {
    trendChart = new ApexCharts(trendChartContainer.value, options)
    trendChart.render()
  }
}

function initDistributionChart() {
  if (!distributionChartContainer.value || !dashboardData.value.subtypeDistribution) return
  
  const subtypes = dashboardData.value.subtypeDistribution.map(item => item.subtype)
  const counts = dashboardData.value.subtypeDistribution.map(item => item.count)
  
  const options = {
    series: counts,
    chart: {
      height: 300,
      type: 'pie'
    },
    labels: subtypes,
    colors: [
      '#3273dc', // H5N1
      '#ff3860', // H7N9
      '#ffdd57', // H9N2
      '#48c774', // H5N8
      '#9c27b0', // H5N6
      '#607d8b'  // Other
    ],
    legend: {
      position: 'bottom'
    },
    responsive: [
      {
        breakpoint: 480,
        options: {
          chart: {
            width: '100%'
          },
          legend: {
            position: 'bottom'
          }
        }
      }
    ],
    tooltip: {
      y: {
        formatter: function(val) {
          return val + ' outbreaks'
        }
      }
    }
  }
  
  if (distributionChart) {
    distributionChart.updateOptions(options)
  } else {
    distributionChart = new ApexCharts(distributionChartContainer.value, options)
    distributionChart.render()
  }
}

// Helper functions
function formatDate(dateString) {
  if (!dateString) return 'Unknown'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

function getTrendClass(value) {
  if (value > 0) return 'is-trend-up'
  if (value < 0) return 'is-trend-down'
  return 'is-trend-neutral'
}

function getTrendIcon(value) {
  if (value > 0) return 'mdi:arrow-up'
  if (value < 0) return 'mdi:arrow-down'
  return 'mdi:minus'
}

function getSubtypeColor(subtype) {
  const colors = {
    'H5N1': 'primary',
    'H7N9': 'danger',
    'H9N2': 'warning',
    'H5N8': 'success',
    'H5N6': 'purple'
  }
  return colors[subtype] || 'info'
}

function getSeverityColor(severity) {
  const colors = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'success'
  }
  return colors[severity] || 'info'
}

function getAlertIcon(type) {
  const icons = {
    'outbreak': 'mdi:virus',
    'genetic': 'mdi:dna',
    'zoonotic': 'mdi:human',
    'transmission': 'mdi:network'
  }
  return icons[type] || 'mdi:alert-circle'
}

function getAlertColor(type) {
  const colors = {
    'outbreak': 'danger',
    'genetic': 'warning',
    'zoonotic': 'primary',
    'transmission': 'info'
  }
  return colors[type] || 'danger'
}

// Lifecycle hooks
onMounted(() => {
  loadDashboardData()
  
  // Handle window resize for charts
  const handleResize = () => {
    if (trendChart) trendChart.render()
    if (distributionChart) distributionChart.render()
    if (map) map.resize()
  }
  
  window.addEventListener('resize', handleResize)
  
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    
    // Clean up chart instances
    if (trendChart) trendChart.destroy()
    if (distributionChart) distributionChart.destroy()
    if (map) map.remove()
  })
})
</script>

<style scoped>
.dashboard-view {
  max-width: 1200px;
  margin: 0 auto;
}

.summary-card {
  height: 100%;
}

.summary-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 60px;
  height: 60px;
  margin: 0 auto;
  border-radius: 50%;
  background-color: rgba(50, 115, 220, 0.1);
}

.map-container {
  height: 400px;
  width: 100%;
  border-radius: 0 0 6px 6px;
}

.alert-item {
  border-left: 4px solid;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.alert-item:nth-child(odd) {
  background-color: rgba(0, 0, 0, 0.01);
}

.is-trend-up {
  color: #48c774;
}

.is-trend-down {
  color: #ff3860;
}

.is-trend-neutral {
  color: #7a7a7a;
}
</style>