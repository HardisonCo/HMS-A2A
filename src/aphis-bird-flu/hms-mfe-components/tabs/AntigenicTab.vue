<template>
  <div class="antigenic-tab">
    <div class="columns is-multiline">
      <!-- Antigenic Properties Overview -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:shield-virus" class="mr-2" />
              Antigenic Properties
            </div>
          </template>
          <div class="p-4">
            <div class="mb-3">
              <div class="is-flex is-align-items-center mb-2">
                <span class="is-size-6 has-text-weight-bold mr-2">Drift Score:</span>
                <VProgress
                  :value="properties.drift_score * 100"
                  size="tiny"
                  :color="getDriftColor(properties.drift_score)"
                  class="flex-grow-1"
                >
                  {{ (properties.drift_score * 100).toFixed(0) }}%
                </VProgress>
              </div>
              <p class="help">
                The antigenic drift score represents how much the virus has changed from the reference strain.
                Higher values indicate greater antigenic difference.
              </p>
            </div>
            
            <div class="mb-3">
              <div class="is-flex is-align-items-center">
                <span class="is-size-6 has-text-weight-bold mr-2">Antigenic Cluster:</span>
                <VTag :color="getClusterColor(properties.antigenic_cluster)">
                  {{ formatClusterName(properties.antigenic_cluster) }}
                </VTag>
              </div>
              <p class="mt-1 help">
                Antigenic cluster indicates the group of viruses with similar antigenic properties.
              </p>
            </div>
            
            <div class="mb-3">
              <div class="is-flex is-align-items-center">
                <span class="is-size-6 has-text-weight-bold mr-2">Key Antigenic Mutation:</span>
                <VTag :color="properties.has_key_antigenic_mutation ? 'warning' : 'light'">
                  {{ properties.has_key_antigenic_mutation ? 'Present' : 'Absent' }}
                </VTag>
              </div>
              <p class="mt-1 help">
                Key antigenic mutations can significantly impact immune recognition and vaccine effectiveness.
              </p>
            </div>
          </div>
        </VCard>
      </div>
      
      <!-- Vaccine Match -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:syringe" class="mr-2" />
              Vaccine Match
            </div>
          </template>
          <div class="p-4">
            <div class="mb-3">
              <div class="is-flex is-align-items-center">
                <span class="is-size-6 has-text-weight-bold mr-2">Overall Match:</span>
                <VProgress
                  :value="properties.vaccine_match * 100"
                  size="tiny"
                  :color="getVaccineMatchColor(properties.vaccine_match)"
                  class="flex-grow-1"
                >
                  {{ (properties.vaccine_match * 100).toFixed(0) }}%
                </VProgress>
              </div>
            </div>
            
            <h5 class="is-size-6 has-text-weight-bold mb-2">Predicted Effectiveness by Age Group:</h5>
            <div class="age-group-effectiveness mb-4">
              <div class="mb-2">
                <div class="is-flex is-align-items-center mb-1">
                  <span class="age-group-label">Children:</span>
                  <VProgress
                    :value="properties.vaccine_effectiveness_prediction.children * 100"
                    size="tiny"
                    :color="getVaccineMatchColor(properties.vaccine_effectiveness_prediction.children)"
                    class="flex-grow-1"
                  >
                    {{ (properties.vaccine_effectiveness_prediction.children * 100).toFixed(0) }}%
                  </VProgress>
                </div>
                <div class="is-flex is-align-items-center mb-1">
                  <span class="age-group-label">Adults:</span>
                  <VProgress
                    :value="properties.vaccine_effectiveness_prediction.adults * 100"
                    size="tiny"
                    :color="getVaccineMatchColor(properties.vaccine_effectiveness_prediction.adults)"
                    class="flex-grow-1"
                  >
                    {{ (properties.vaccine_effectiveness_prediction.adults * 100).toFixed(0) }}%
                  </VProgress>
                </div>
                <div class="is-flex is-align-items-center">
                  <span class="age-group-label">Elderly:</span>
                  <VProgress
                    :value="properties.vaccine_effectiveness_prediction.elderly * 100"
                    size="tiny"
                    :color="getVaccineMatchColor(properties.vaccine_effectiveness_prediction.elderly)"
                    class="flex-grow-1"
                  >
                    {{ (properties.vaccine_effectiveness_prediction.elderly * 100).toFixed(0) }}%
                  </VProgress>
                </div>
              </div>
              <p class="help">
                Predicted vaccine effectiveness varies by age group due to differences in immune response.
              </p>
            </div>
            
            <div v-if="properties.vaccine_match < 0.6" class="notification is-warning is-light">
              <div class="is-flex is-align-items-center">
                <VIcon icon="mdi:alert-circle" class="mr-2" />
                <strong>Vaccine update may be needed due to low match score.</strong>
              </div>
            </div>
          </div>
        </VCard>
      </div>
      
      <!-- Cross Reactivity -->
      <div class="column is-12">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:virus-outline" class="mr-2" />
              Cross Reactivity with Other Strains
            </div>
          </template>
          <div class="p-4">
            <div class="columns is-multiline">
              <div class="column is-6">
                <h5 class="is-size-6 has-text-weight-bold mb-2">Cross-Reactivity Profile:</h5>
                <div class="cross-reactivity-list">
                  <div v-for="(value, strain) in properties.cross_reactivity" :key="strain" class="mb-2">
                    <div class="is-flex is-align-items-center">
                      <span class="strain-label">{{ formatStrainName(strain) }}:</span>
                      <VProgress
                        :value="value * 100"
                        size="tiny"
                        :color="getCrossReactivityColor(value)"
                        class="flex-grow-1"
                      >
                        {{ (value * 100).toFixed(0) }}%
                      </VProgress>
                    </div>
                  </div>
                </div>
              </div>
              <div class="column is-6">
                <div ref="crossReactivityChartContainer" class="cross-reactivity-chart-container"></div>
              </div>
            </div>
            <p class="help mt-2">
              Cross-reactivity indicates how well antibodies against this strain recognize and neutralize other strains.
              Higher percentages indicate better cross-protection.
            </p>
          </div>
        </VCard>
      </div>
      
      <!-- Recommendations -->
      <div class="column is-12">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:clipboard-text" class="mr-2" />
              Recommendations
            </div>
          </template>
          <div class="p-4">
            <ul class="recommendations-list">
              <li v-if="properties.drift_score > 0.5" class="recommendation-item">
                <div class="is-flex is-align-items-start">
                  <VIcon icon="mdi:alert-circle" color="warning" class="mr-2 mt-1" />
                  <div>
                    <strong>Monitor for vaccine breakthrough:</strong> 
                    <span>High antigenic drift detected. Enhanced surveillance for vaccine breakthrough cases is recommended.</span>
                  </div>
                </div>
              </li>
              <li v-if="properties.has_key_antigenic_mutation" class="recommendation-item">
                <div class="is-flex is-align-items-start">
                  <VIcon icon="mdi:flask" color="info" class="mr-2 mt-1" />
                  <div>
                    <strong>Laboratory testing:</strong> 
                    <span>Key antigenic mutation detected. Additional laboratory testing with reference antisera is recommended.</span>
                  </div>
                </div>
              </li>
              <li v-if="properties.vaccine_match < 0.5" class="recommendation-item">
                <div class="is-flex is-align-items-start">
                  <VIcon icon="mdi:syringe" color="danger" class="mr-2 mt-1" />
                  <div>
                    <strong>Vaccine update consideration:</strong> 
                    <span>Low vaccine match detected. Consider updating vaccine strains for the next production cycle.</span>
                  </div>
                </div>
              </li>
              <li v-else-if="properties.vaccine_match < 0.7" class="recommendation-item">
                <div class="is-flex is-align-items-start">
                  <VIcon icon="mdi:syringe" color="warning" class="mr-2 mt-1" />
                  <div>
                    <strong>Continued monitoring:</strong> 
                    <span>Moderate vaccine match detected. Continue monitoring for further antigenic changes.</span>
                  </div>
                </div>
              </li>
              <li v-else class="recommendation-item">
                <div class="is-flex is-align-items-start">
                  <VIcon icon="mdi:check-circle" color="success" class="mr-2 mt-1" />
                  <div>
                    <strong>Good vaccine match:</strong> 
                    <span>Current vaccine should provide adequate protection against this strain.</span>
                  </div>
                </div>
              </li>
              <li class="recommendation-item">
                <div class="is-flex is-align-items-start">
                  <VIcon icon="mdi:eye" color="primary" class="mr-2 mt-1" />
                  <div>
                    <strong>Surveillance:</strong> 
                    <span>Continue genetic and antigenic surveillance to detect further evolution.</span>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </VCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import ApexCharts from 'apexcharts'

const props = defineProps({
  properties: {
    type: Object,
    required: true
  }
})

// State
const crossReactivityChartContainer = ref(null)
let crossReactivityChart = null

// Watch for changes in properties to update the chart
watch(() => props.properties, () => {
  initCrossReactivityChart()
}, { deep: true })

// Lifecycle hooks
onMounted(() => {
  initCrossReactivityChart()
})

// Methods
function initCrossReactivityChart() {
  if (!crossReactivityChartContainer.value || !props.properties.cross_reactivity) return
  
  const strains = Object.keys(props.properties.cross_reactivity).map(strain => formatStrainName(strain))
  const values = Object.values(props.properties.cross_reactivity).map(value => (value * 100).toFixed(1))
  
  // Chart options
  const options = {
    series: [{
      name: 'Cross-reactivity',
      data: values
    }],
    chart: {
      type: 'radar',
      height: 300,
      toolbar: {
        show: false
      }
    },
    xaxis: {
      categories: strains
    },
    yaxis: {
      max: 100,
      min: 0
    },
    fill: {
      opacity: 0.4
    },
    colors: ['#3273dc'],
    markers: {
      size: 4,
      colors: ['#3273dc'],
      strokeWidth: 2
    },
    tooltip: {
      y: {
        formatter: function(val) {
          return val + '%'
        }
      }
    }
  }
  
  // Initialize chart
  if (crossReactivityChart) {
    crossReactivityChart.updateOptions(options)
  } else {
    crossReactivityChart = new ApexCharts(crossReactivityChartContainer.value, options)
    crossReactivityChart.render()
  }
}

// Helper functions
function formatClusterName(cluster) {
  if (!cluster) return 'Unknown'
  return cluster.split('_').map(word => {
    return word.charAt(0).toUpperCase() + word.slice(1)
  }).join(' ')
}

function formatStrainName(strain) {
  if (!strain) return 'Unknown'
  return strain.split('_').join(' ')
}

function getDriftColor(score) {
  if (score > 0.7) return 'danger'
  if (score > 0.4) return 'warning'
  return 'success'
}

function getClusterColor(cluster) {
  if (!cluster) return 'light'
  if (cluster.includes('EU2020')) return 'warning'
  if (cluster.includes('original')) return 'success'
  return 'info'
}

function getVaccineMatchColor(match) {
  if (match < 0.4) return 'danger'
  if (match < 0.7) return 'warning'
  return 'success'
}

function getCrossReactivityColor(value) {
  if (value < 0.3) return 'danger'
  if (value < 0.6) return 'warning'
  return 'success'
}
</script>

<style scoped>
.flex-grow-1 {
  flex-grow: 1;
}

.age-group-label, .strain-label {
  width: 100px;
  font-size: 0.9rem;
  margin-right: 1rem;
}

.recommendations-list {
  list-style-type: none;
  padding-left: 0;
}

.recommendation-item {
  margin-bottom: 0.75rem;
}

.cross-reactivity-chart-container {
  height: 300px;
}
</style>