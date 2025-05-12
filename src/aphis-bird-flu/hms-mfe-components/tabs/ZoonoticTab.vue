<template>
  <div class="zoonotic-tab">
    <div class="columns is-multiline">
      <!-- Zoonotic Risk Overview -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:virus" class="mr-2" />
              Zoonotic Risk Assessment
            </div>
          </template>
          <div class="p-4">
            <div class="mb-4 risk-level-indicator">
              <h5 class="is-size-6 has-text-weight-bold mb-2">Overall Risk Level:</h5>
              <div class="risk-gauge">
                <div class="risk-level" :class="`risk-level-${assessment.zoonotic_risk_level}`">
                  <span class="risk-text">{{ formatRiskLevel(assessment.zoonotic_risk_level) }}</span>
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <div class="is-flex is-align-items-center mb-2">
                <span class="is-size-6 has-text-weight-bold mr-2">Mammalian Adaptation Score:</span>
                <VProgress
                  :value="assessment.mammalian_adaptation_score * 100"
                  size="tiny"
                  :color="getAdaptationColor(assessment.mammalian_adaptation_score)"
                  class="flex-grow-1"
                >
                  {{ (assessment.mammalian_adaptation_score * 100).toFixed(0) }}%
                </VProgress>
              </div>
              <p class="help">
                This score indicates how well-adapted the virus is to mammalian hosts based on genetic markers.
              </p>
            </div>
            
            <div class="mb-3">
              <h5 class="is-size-6 has-text-weight-bold mb-2">Mammalian Adaptation Markers:</h5>
              <div v-if="assessment.mammalian_adaptation_markers.length > 0" class="tags">
                <VTag
                  v-for="(marker, index) in assessment.mammalian_adaptation_markers"
                  :key="index"
                  color="danger"
                >
                  {{ marker }}
                </VTag>
              </div>
              <p v-else class="has-text-grey">No mammalian adaptation markers detected</p>
              <p class="help mt-1">
                These genetic markers are associated with improved viral replication or transmission in mammals.
              </p>
            </div>
          </div>
        </VCard>
      </div>
      
      <!-- Transmission Risk -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:share-variant" class="mr-2" />
              Transmission Risk by Host
            </div>
          </template>
          <div class="p-4">
            <div ref="transmissionRiskChartContainer" class="transmission-risk-chart-container mb-3"></div>
            <p class="help">
              Estimated risk of efficient transmission in different host species based on genetic profile and historical data.
            </p>
            
            <div v-if="assessment.transmission_risk.human > 0.3" class="notification is-warning is-light mt-3">
              <div class="is-flex is-align-items-center">
                <VIcon icon="mdi:alert-circle" class="mr-2" />
                <strong>Elevated human transmission risk detected.</strong>
              </div>
            </div>
          </div>
        </VCard>
      </div>
      
      <!-- Historical Context -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:history" class="mr-2" />
              Historical Context
            </div>
          </template>
          <div class="p-4">
            <table class="table is-fullwidth">
              <tbody>
                <tr>
                  <td class="has-text-weight-bold">First Human Case:</td>
                  <td>{{ formatDate(assessment.history.first_human_case) }}</td>
                </tr>
                <tr>
                  <td class="has-text-weight-bold">Total Human Cases:</td>
                  <td>{{ assessment.history.total_human_cases.toLocaleString() }}</td>
                </tr>
                <tr>
                  <td class="has-text-weight-bold">Total Human Deaths:</td>
                  <td>{{ assessment.history.total_human_deaths.toLocaleString() }}</td>
                </tr>
                <tr>
                  <td class="has-text-weight-bold">Case Fatality Rate:</td>
                  <td>{{ (assessment.history.case_fatality_rate * 100).toFixed(1) }}%</td>
                </tr>
                <tr>
                  <td class="has-text-weight-bold">Sustained Human Transmission:</td>
                  <td>
                    <VTag :color="assessment.history.sustained_human_transmission ? 'danger' : 'success'">
                      {{ assessment.history.sustained_human_transmission ? 'Yes' : 'No' }}
                    </VTag>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <h5 class="is-size-6 has-text-weight-bold mt-3 mb-2">Major Outbreaks:</h5>
            <div v-if="assessment.history.major_outbreaks && assessment.history.major_outbreaks.length > 0">
              <div v-for="(outbreak, index) in assessment.history.major_outbreaks" :key="index" class="outbreak-item mb-2">
                <div class="is-flex is-align-items-center">
                  <span class="outbreak-year mr-2">{{ outbreak.year }}</span>
                  <span class="outbreak-location mr-2">{{ outbreak.location }}:</span>
                  <span class="outbreak-cases">{{ outbreak.cases }} cases</span>
                </div>
              </div>
            </div>
            <p v-else class="has-text-grey">No major outbreak data available</p>
          </div>
        </VCard>
      </div>
      
      <!-- Surveillance Recommendations -->
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:binoculars" class="mr-2" />
              Surveillance Recommendations
            </div>
            <VTag :color="getSurveillanceColor(assessment.surveillance_recommendation.priority)" class="mr-2">
              {{ formatValue(assessment.surveillance_recommendation.priority) }} Priority
            </VTag>
          </template>
          <div class="p-4">
            <div class="mb-3">
              <div class="is-flex is-align-items-center mb-1">
                <span class="is-size-6 has-text-weight-bold mr-2">Sampling Frequency:</span>
                <span>{{ formatValue(assessment.surveillance_recommendation.sampling_frequency) }}</span>
              </div>
              <div class="is-flex is-align-items-center mb-1">
                <span class="is-size-6 has-text-weight-bold mr-2">Geographic Focus:</span>
                <span>{{ formatValue(assessment.surveillance_recommendation.geographic_focus) }}</span>
              </div>
              <div class="is-flex is-align-items-center mb-1">
                <span class="is-size-6 has-text-weight-bold mr-2">Mammalian Surveillance:</span>
                <span>{{ formatValue(assessment.surveillance_recommendation.mammalian_surveillance) }}</span>
              </div>
            </div>
            
            <h5 class="is-size-6 has-text-weight-bold mb-2">Sentinel Species:</h5>
            <div class="tags">
              <VTag
                v-for="(species, index) in assessment.surveillance_recommendation.sentinel_species"
                :key="index"
                color="info"
              >
                {{ formatValue(species) }}
              </VTag>
            </div>
            
            <div v-if="assessment.zoonotic_risk_level === 'high'" class="notification is-danger is-light mt-3">
              <div class="is-flex is-align-items-center">
                <VIcon icon="mdi:alert-circle" class="mr-2" />
                <div>
                  <strong>Enhanced surveillance strongly recommended.</strong>
                  <p class="mt-1">Consider activating cross-agency response protocol.</p>
                </div>
              </div>
            </div>
          </div>
        </VCard>
      </div>
      
      <!-- One Health Recommendations -->
      <div class="column is-12">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="mdi:earth" class="mr-2" />
              One Health Recommendations
            </div>
          </template>
          <div class="p-4">
            <div class="columns is-multiline">
              <div class="column is-4">
                <h5 class="is-size-6 has-text-weight-bold mb-2">
                  <VIcon icon="mdi:account-group" class="mr-1" />
                  Human Health
                </h5>
                <ul class="recommendation-list">
                  <li v-if="assessment.zoonotic_risk_level === 'high'">
                    Alert healthcare providers about potential human cases
                  </li>
                  <li v-if="assessment.transmission_risk.human > 0.3">
                    Enhance surveillance at human-animal interface locations
                  </li>
                  <li>
                    {{ assessment.zoonotic_risk_level === 'high' ? 'Implement' : 'Consider' }} PPE recommendations for high-risk workers
                  </li>
                  <li>
                    Maintain awareness of clinical symptoms in at-risk populations
                  </li>
                </ul>
              </div>
              
              <div class="column is-4">
                <h5 class="is-size-6 has-text-weight-bold mb-2">
                  <VIcon icon="mdi:paw" class="mr-1" />
                  Animal Health
                </h5>
                <ul class="recommendation-list">
                  <li>
                    {{ assessment.zoonotic_risk_level === 'high' ? 'Implement' : 'Consider' }} enhanced biosecurity in poultry facilities
                  </li>
                  <li>
                    Monitor {{ getSentinelSpeciesString(assessment.surveillance_recommendation.sentinel_species) }} for early detection
                  </li>
                  <li v-if="assessment.transmission_risk.swine > 0.4">
                    Increase surveillance in swine populations
                  </li>
                  <li>
                    Review and update response protocols for positive cases
                  </li>
                </ul>
              </div>
              
              <div class="column is-4">
                <h5 class="is-size-6 has-text-weight-bold mb-2">
                  <VIcon icon="mdi:tree" class="mr-1" />
                  Environmental Factors
                </h5>
                <ul class="recommendation-list">
                  <li>
                    Monitor environmental conditions that favor transmission
                  </li>
                  <li>
                    Sample water bodies near poultry facilities in affected areas
                  </li>
                  <li>
                    Track migratory bird patterns in regions with active cases
                  </li>
                  <li v-if="assessment.zoonotic_risk_level === 'high'">
                    Consider temporary access restrictions to high-risk natural areas
                  </li>
                </ul>
              </div>
            </div>
            
            <div class="notification is-info is-light mt-3">
              <div class="is-flex is-align-items-center">
                <VIcon icon="mdi:information" class="mr-2" />
                <div>
                  <strong>Cross-agency coordination recommended.</strong>
                  <p class="mt-1">
                    This strain has characteristics that warrant a coordinated approach between animal health, public health, 
                    and environmental agencies.
                  </p>
                </div>
              </div>
            </div>
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
  assessment: {
    type: Object,
    required: true
  }
})

// State
const transmissionRiskChartContainer = ref(null)
let transmissionRiskChart = null

// Watch for changes in assessment to update the chart
watch(() => props.assessment, () => {
  initTransmissionRiskChart()
}, { deep: true })

// Lifecycle hooks
onMounted(() => {
  initTransmissionRiskChart()
})

// Methods
function initTransmissionRiskChart() {
  if (!transmissionRiskChartContainer.value || !props.assessment.transmission_risk) return
  
  const hosts = Object.keys(props.assessment.transmission_risk).map(host => formatValue(host))
  const risks = Object.values(props.assessment.transmission_risk).map(risk => (risk * 100).toFixed(1))
  
  // Chart colors based on risk levels
  const colors = Object.values(props.assessment.transmission_risk).map(risk => {
    if (risk > 0.7) return '#ff3860' // danger
    if (risk > 0.4) return '#ffdd57' // warning
    return '#48c774' // success
  })
  
  // Chart options
  const options = {
    series: [{
      name: 'Transmission Risk',
      data: risks
    }],
    chart: {
      type: 'bar',
      height: 250,
      toolbar: {
        show: false
      }
    },
    plotOptions: {
      bar: {
        horizontal: true,
        borderRadius: 4,
        distributed: true
      }
    },
    colors: colors,
    dataLabels: {
      enabled: false
    },
    xaxis: {
      categories: hosts,
      labels: {
        formatter: function(val) {
          return val + '%'
        }
      },
      max: 100
    },
    yaxis: {
      labels: {
        formatter: function(val) {
          return formatValue(val)
        }
      }
    },
    tooltip: {
      y: {
        formatter: function(val) {
          return val + '%'
        }
      }
    },
    legend: {
      show: false
    }
  }
  
  // Initialize chart
  if (transmissionRiskChart) {
    transmissionRiskChart.updateOptions(options)
  } else {
    transmissionRiskChart = new ApexCharts(transmissionRiskChartContainer.value, options)
    transmissionRiskChart.render()
  }
}

// Helper functions
function formatRiskLevel(level) {
  if (!level) return 'Unknown'
  return level.charAt(0).toUpperCase() + level.slice(1)
}

function formatValue(value) {
  if (!value) return 'Unknown'
  return value.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
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

function getAdaptationColor(score) {
  if (score > 0.6) return 'danger'
  if (score > 0.3) return 'warning'
  return 'success'
}

function getSurveillanceColor(priority) {
  if (!priority) return 'light'
  const colors = {
    'high': 'danger',
    'moderate': 'warning',
    'standard': 'info'
  }
  return colors[priority] || 'light'
}

function getSentinelSpeciesString(species) {
  if (!species || species.length === 0) return 'key species'
  if (species.length === 1) return formatValue(species[0])
  if (species.length === 2) return `${formatValue(species[0])} and ${formatValue(species[1])}`
  return `${formatValue(species[0])}, ${formatValue(species[1])}, and other species`
}
</script>

<style scoped>
.flex-grow-1 {
  flex-grow: 1;
}

.risk-gauge {
  background: linear-gradient(to right, #48c774, #ffdd57, #ff3860);
  height: 30px;
  border-radius: 15px;
  position: relative;
  overflow: hidden;
  margin-bottom: 10px;
}

.risk-level {
  position: absolute;
  top: 0;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.risk-level-low {
  background-color: rgba(72, 199, 116, 0.7);
  width: 33.3%;
  left: 0;
}

.risk-level-moderate {
  background-color: rgba(255, 221, 87, 0.7);
  width: 33.3%;
  left: 33.3%;
}

.risk-level-high {
  background-color: rgba(255, 56, 96, 0.7);
  width: 33.4%;
  left: 66.6%;
}

.transmission-risk-chart-container {
  height: 250px;
}

.outbreak-year {
  font-weight: bold;
  width: 50px;
}

.outbreak-location {
  width: 120px;
}

.recommendation-list {
  list-style-type: disc;
  padding-left: 20px;
  margin-bottom: 10px;
}

.recommendation-list li {
  margin-bottom: 5px;
}
</style>