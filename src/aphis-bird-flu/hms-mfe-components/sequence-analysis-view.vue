<template>
  <div class="sequence-analysis">
    <!-- Header with action buttons -->
    <div class="is-flex is-justify-content-space-between mb-4">
      <h2 class="title is-4">Bird Flu Genetic Sequence Analysis</h2>
      <div class="buttons">
        <VButton color="primary" @click="loadDemoData">Load Demo Data</VButton>
        <VButton color="success" :disabled="!canAnalyze" @click="analyzeSequence">
          <span>Analyze Sequence</span>
          <VIcon icon="mdi:dna" class="ml-2" />
        </VButton>
      </div>
    </div>

    <!-- Input form -->
    <VCard class="mb-4">
      <div class="is-flex is-justify-content-space-between">
        <div class="mr-4 is-flex-grow-1">
          <VField label="Genetic Sequence">
            <VControl>
              <VTextarea
                v-model="sequenceData"
                rows="5"
                placeholder="Enter genetic sequence data here..."
              />
            </VControl>
          </VField>
        </div>
        <div class="is-flex-shrink-0" style="width: 200px">
          <VField label="Virus Subtype">
            <VControl>
              <VSelect
                v-model="selectedSubtype"
                :options="subtypeOptions"
              />
            </VControl>
          </VField>
          <VField label="Gene (Optional)">
            <VControl>
              <VSelect
                v-model="selectedGene"
                :options="geneOptions"
              />
            </VControl>
          </VField>
        </div>
      </div>
    </VCard>

    <!-- Results display (when available) -->
    <div v-if="isLoading" class="has-text-centered my-6">
      <VLoader size="large" />
      <p class="mt-2">Analyzing sequence...</p>
    </div>

    <div v-if="analysisResults && !isLoading">
      <VTabs type="boxed" :selected="activeTab" @tab-change="changeTab">
        <VTab label="Mutations" icon="mdi:chart-timeline-variant">
          <MutationsTab :mutations="analysisResults.mutations" />
        </VTab>
        <VTab label="Lineage" icon="mdi:family-tree">
          <LineageTab :lineage="analysisResults.lineage" />
        </VTab>
        <VTab label="Antigenic Properties" icon="mdi:shield-virus">
          <AntigenicTab :properties="analysisResults.antigenic_properties" />
        </VTab>
        <VTab label="Zoonotic Risk" icon="mdi:virus">
          <ZoonoticTab :assessment="analysisResults.zoonotic_potential" />
        </VTab>
      </VTabs>
    </div>

    <!-- Error display -->
    <VMessage v-if="error" color="danger" class="my-4">
      <p>{{ error }}</p>
    </VMessage>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGeneticAnalysisApi } from '@/composables/useGeneticAnalysisApi'
import MutationsTab from './tabs/MutationsTab.vue'
import LineageTab from './tabs/LineageTab.vue'
import AntigenicTab from './tabs/AntigenicTab.vue'
import ZoonoticTab from './tabs/ZoonoticTab.vue'

// State
const sequenceData = ref('')
const selectedSubtype = ref('H5N1')
const selectedGene = ref(null)
const analysisResults = ref(null)
const isLoading = ref(false)
const error = ref(null)
const activeTab = ref(0)

// Options for dropdowns
const subtypeOptions = [
  { value: 'H5N1', label: 'H5N1' },
  { value: 'H7N9', label: 'H7N9' },
  { value: 'H9N2', label: 'H9N2' }
]

const geneOptions = [
  { value: null, label: 'All genes' },
  { value: 'HA', label: 'Hemagglutinin (HA)' },
  { value: 'NA', label: 'Neuraminidase (NA)' },
  { value: 'PA', label: 'Polymerase (PA)' },
  { value: 'PB1', label: 'Polymerase Basic 1 (PB1)' },
  { value: 'PB2', label: 'Polymerase Basic 2 (PB2)' },
  { value: 'NP', label: 'Nucleoprotein (NP)' },
  { value: 'M', label: 'Matrix (M)' },
  { value: 'NS', label: 'Nonstructural (NS)' }
]

// API client
const { analyzeSequence: apiAnalyzeSequence } = useGeneticAnalysisApi()

// Computed
const canAnalyze = computed(() => {
  return sequenceData.value.trim().length > 0 && selectedSubtype.value
})

// Methods
async function analyzeSequence() {
  if (!canAnalyze.value) return

  isLoading.value = true
  error.value = null

  try {
    analysisResults.value = await apiAnalyzeSequence({
      sequence: sequenceData.value,
      subtype: selectedSubtype.value,
      gene: selectedGene.value
    })
    activeTab.value = 0 // Reset to first tab
  } catch (err) {
    error.value = err.message || 'Failed to analyze sequence'
    analysisResults.value = null
  } finally {
    isLoading.value = false
  }
}

function changeTab(tabIndex) {
  activeTab.value = tabIndex
}

function loadDemoData() {
  // Load demo data based on selected subtype
  const demoSequences = {
    'H5N1': 'ATGGAGAGAATAAAAGAACTAAGAGATCTAATGTCACAGTCCCGCACTCGCGAGATACTCACCAAAACCACTGTGGACCATATGGCCATAATCAAGAAGTACACATCGGGGAGACAGGAAAAGAACCCGTCACTTAGGATGAAATGGATGATGGCAATGAAATATCCAATCACTGCTGACAAAAGGATAACAGAAATGGTTCCGGAGAGAAATGAACAAGGACAAACTCTATGGAGTAAAATGAGTGATGCTGGATCAGATAGAGTGATGGTATCACCTTTGGCTGTAACATGGTGGAATAGGAATGGACCCGTGACAAATACGGTCCATTACCCAAAAG',
    'H7N9': 'ATGAACACTCAAATCCTGGTATTCGCTCTGATTGCGATCGCCTTTGCAGCAGTTTCTCTTCTTGACGTTGAATGGTCTTACATAGTTTATAATGCATTTAAGATCCAAAAAGATAACGATTGTCAAGATCTAACAACACTAAGCAGCGTCGACAAAGCACCAGTTAACAGTATTCTTCTGATTGATGGTCTCAGTGACCTAGATGGAGTGAAGCCTGTTAGAGACTTGATAGATTCTAGCTTTGGCAAAAGAGGACTAGCTGTAGGAAGAGGCAATGAATATGTTGCCAAACATGACAAAGAATTGACTAGAACTATCTGCAATGGGTG',
    'H9N2': 'ATGGAAACAGTCAAAATTCTACTTAATCTTGTAAACATTGCAGCAAGCAATGCAGGTTCACTTCTTCCAGGACATGCTACAGGACACAATAATAGTGACACTTGAATCTGGTACAGCAAACAGCAATGATCTGAGGGATTGTAGCAACATGCTGGCAGAATGCAATACACTATTTGCAAAGGGGAGGGAAACCAAGACAGAACTGCATACGGACAAGTTGACACAGTTGATACAACAATAACAAAGGATAATCAGCAATCCTGGCTATCCAATCAAGGGGAAACACCTGTTTTCTCGTCAAGAATCCGGGAAGCATTGGATTTTCTT'
  }

  sequenceData.value = demoSequences[selectedSubtype.value] || demoSequences['H5N1']
}
</script>

<style scoped>
.sequence-analysis {
  max-width: 1200px;
  margin: 0 auto;
}
</style>