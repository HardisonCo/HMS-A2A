<template>
  <div class="lineage-tab">
    <div class="columns is-multiline">
      <!-- Lineage Information -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:family-tree" class="mr-2" />
              Lineage Information
            </div>
          </template>
          <div class="p-4">
            <div class="mb-3">
              <div class="is-flex is-align-items-center">
                <span class="is-size-6 has-text-weight-bold mr-2">Identified Lineage:</span>
                <VTag :color="getConfidenceColor(lineage.confidence)">
                  {{ formatLineageName(lineage.lineage) }}
                </VTag>
              </div>
              <p class="mt-1">
                <small>
                  Confidence: {{ (lineage.confidence * 100).toFixed(0) }}%
                </small>
              </p>
            </div>
            
            <div class="mb-3">
              <p class="is-size-6 has-text-weight-bold mb-1">Related Lineages:</p>
              <div class="tags">
                <VTag 
                  v-for="(relatedLineage, index) in lineage.related_lineages" 
                  :key="index"
                  color="light"
                >
                  {{ formatLineageName(relatedLineage) }}
                </VTag>
              </div>
            </div>
            
            <div class="mb-3">
              <p class="is-size-6 has-text-weight-bold mb-1">First Detected:</p>
              <p>{{ formatDate(lineage.first_detected) }}</p>
            </div>
            
            <div class="mb-3">
              <p class="is-size-6 has-text-weight-bold mb-1">Current Trend:</p>
              <div class="is-flex is-align-items-center">
                <VTag :color="getTrendColor(lineage.trend)">
                  {{ formatTrend(lineage.trend) }}
                </VTag>
                <span v-if="lineage.recent_expansion" class="ml-2">
                  <VIcon icon="mdi:alert" color="warning" size="small" class="mr-1" />
                  <small>Recent expansion detected</small>
                </span>
              </div>
            </div>
          </div>
        </VCard>
      </div>
      
      <!-- Defining Mutations -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:dna" class="mr-2" />
              Defining Mutations
            </div>
          </template>
          <div class="p-4">
            <p v-if="!lineage.defining_mutations || lineage.defining_mutations.length === 0" class="has-text-grey">
              No defining mutations available for this lineage
            </p>
            <ul v-else class="defining-mutations-list">
              <li v-for="(mutation, index) in lineage.defining_mutations" :key="index" class="mb-2">
                <div class="is-flex is-align-items-center">
                  <VTag color="primary" class="mr-2">{{ mutation }}</VTag>
                  <span class="has-text-grey-dark">{{ getMutationDescription(mutation) }}</span>
                </div>
              </li>
            </ul>
          </div>
        </VCard>
      </div>
      
      <!-- Geographic Distribution Map -->
      <div class="column is-12">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:map" class="mr-2" />
              Geographic Distribution
            </div>
          </template>
          <div ref="mapContainer" class="geographic-map"></div>
        </VCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import mapboxgl from 'mapbox-gl'

const props = defineProps({
  lineage: {
    type: Object,
    required: true
  }
})

// State
const mapContainer = ref(null)
let map = null

// Watch for changes in lineage data to update the map
watch(() => props.lineage, () => {
  initMap()
}, { deep: true })

// Lifecycle hooks
onMounted(() => {
  initMap()
})

// Methods
function initMap() {
  if (!mapContainer.value || !props.lineage.geographic_distribution) return
  
  if (!map) {
    // Initialize map
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
    
    map = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/mapbox/light-v10',
      center: [0, 20], // Center on world
      zoom: 1.5
    })
    
    map.on('load', () => {
      addDistributionLayer()
    })
  } else {
    // Update existing map
    if (map.loaded()) {
      updateDistributionLayer()
    } else {
      map.on('load', () => {
        updateDistributionLayer()
      })
    }
  }
}

function addDistributionLayer() {
  if (!map || !map.loaded()) return
  
  // Convert geographic distribution to features
  const features = Object.entries(props.lineage.geographic_distribution).map(([region, prevalence]) => {
    const coordinates = getRegionCoordinates(region)
    return {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [coordinates.lng, coordinates.lat]
      },
      properties: {
        region,
        prevalence
      }
    }
  })
  
  // Add source
  map.addSource('lineage-distribution', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features
    }
  })
  
  // Add heatmap layer
  map.addLayer({
    id: 'lineage-heatmap',
    type: 'heatmap',
    source: 'lineage-distribution',
    paint: {
      'heatmap-weight': [
        'interpolate',
        ['linear'],
        ['get', 'prevalence'],
        0, 0,
        1, 1
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
      'heatmap-radius': 30,
      'heatmap-opacity': 0.7
    }
  })
  
  // Add circle layer
  map.addLayer({
    id: 'lineage-circles',
    type: 'circle',
    source: 'lineage-distribution',
    paint: {
      'circle-radius': [
        'interpolate',
        ['linear'],
        ['get', 'prevalence'],
        0, 5,
        1, 25
      ],
      'circle-color': [
        'interpolate',
        ['linear'],
        ['get', 'prevalence'],
        0, '#3273dc',
        0.3, '#48c774',
        0.6, '#ffdd57',
        0.8, '#ff3860'
      ],
      'circle-opacity': 0.6,
      'circle-stroke-width': 1,
      'circle-stroke-color': '#ffffff'
    }
  })
  
  // Add popup on click
  map.on('click', 'lineage-circles', (e) => {
    const properties = e.features[0].properties
    
    new mapboxgl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(`
        <h4>${formatRegionName(properties.region)}</h4>
        <p><strong>Prevalence:</strong> ${(properties.prevalence * 100).toFixed(1)}%</p>
      `)
      .addTo(map)
  })
  
  // Change cursor on hover
  map.on('mouseenter', 'lineage-circles', () => {
    map.getCanvas().style.cursor = 'pointer'
  })
  
  map.on('mouseleave', 'lineage-circles', () => {
    map.getCanvas().style.cursor = ''
  })
}

function updateDistributionLayer() {
  if (!map || !map.loaded()) return
  
  // Remove old layers if they exist
  if (map.getSource('lineage-distribution')) {
    map.removeLayer('lineage-circles')
    map.removeLayer('lineage-heatmap')
    map.removeSource('lineage-distribution')
  }
  
  // Add new layers
  addDistributionLayer()
}

// Helper functions
function getRegionCoordinates(region) {
  // Map regions to approximate coordinates
  const regionCoordinates = {
    'Eastern_Asia': { lat: 35, lng: 115 },
    'Southeast_Asia': { lat: 10, lng: 106 },
    'Europe': { lat: 50, lng: 10 },
    'North_America': { lat: 40, lng: -100 },
    'South_America': { lat: -15, lng: -60 },
    'Africa': { lat: 0, lng: 20 },
    'South_Asia': { lat: 20, lng: 77 },
    'Middle_East': { lat: 30, lng: 45 },
    'Eastern_China': { lat: 32, lng: 120 },
    'Southern_China': { lat: 25, lng: 110 },
    'Taiwan': { lat: 23.5, lng: 121 },
    'Hong_Kong': { lat: 22.3, lng: 114.2 },
    'Vietnam': { lat: 16, lng: 108 },
    'unknown': { lat: 0, lng: 0 }
  }
  
  return regionCoordinates[region] || { lat: 0, lng: 0 }
}

function formatRegionName(region) {
  if (!region) return 'Unknown'
  return region.replace(/_/g, ' ')
}

function formatLineageName(lineage) {
  if (!lineage) return 'Unknown'
  return lineage.replace(/_/g, ' ').split(' ').map(word => {
    return word.charAt(0).toUpperCase() + word.slice(1)
  }).join(' ')
}

function formatDate(dateString) {
  if (!dateString || dateString === 'unknown') return 'Unknown'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function formatTrend(trend) {
  if (!trend) return 'Unknown'
  return trend.charAt(0).toUpperCase() + trend.slice(1)
}

function getConfidenceColor(confidence) {
  if (confidence > 0.7) return 'success'
  if (confidence > 0.4) return 'warning'
  return 'danger'
}

function getTrendColor(trend) {
  const colors = {
    'increasing': 'danger',
    'stable': 'info',
    'decreasing': 'success',
    'unknown': 'light'
  }
  return colors[trend] || 'light'
}

function getMutationDescription(mutation) {
  // In a real implementation, this would retrieve actual descriptions
  // from a mutation database. This is a simple placeholder.
  return 'Characteristic mutation for this lineage'
}
</script>

<style scoped>
.geographic-map {
  height: 400px;
  width: 100%;
  border-radius: 0 0 6px 6px;
}

.defining-mutations-list {
  list-style-type: none;
  padding-left: 0;
}
</style>