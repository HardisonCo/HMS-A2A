<template>
  <div class="mutations-tab">
    <div class="mb-4">
      <h3 class="title is-5">Detected Mutations</h3>
      <p class="subtitle is-6">{{ mutations.length }} mutations identified in sequence</p>
    </div>

    <!-- Overview cards -->
    <div class="columns is-multiline mb-4">
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="feather:alert-triangle" class="mr-2" />
              Significant Mutations
            </div>
          </template>
          <div class="px-2">
            <ul>
              <li v-for="(mutation, index) in significantMutations" :key="index" class="py-2">
                <div class="is-flex is-align-items-center">
                  <VTag color="danger" class="mr-2">{{ mutation.mutation }}</VTag>
                  <span>{{ getSeverityText(mutation) }}</span>
                </div>
              </li>
              <li v-if="significantMutations.length === 0" class="py-2 has-text-grey">
                No significant mutations detected
              </li>
            </ul>
          </div>
        </VCard>
      </div>
      
      <div class="column is-6">
        <VCard>
          <template #header>
            <div class="card-header-title">
              <VIcon icon="feather:activity" class="mr-2" />
              Gene Distribution
            </div>
          </template>
          <div class="px-2">
            <VFlexTable :data="geneDistribution" :columns="geneColumns">
              <template #cell-percentage="{ row }">
                <VProgress
                  :value="row.percentage"
                  size="tiny"
                  :color="getMutationColorByPercentage(row.percentage)"
                >
                  {{ row.percentage.toFixed(1) }}%
                </VProgress>
              </template>
            </VFlexTable>
          </div>
        </VCard>
      </div>
    </div>

    <!-- Detailed mutations table -->
    <VCard>
      <template #header>
        <div class="card-header-title">
          <div class="is-flex is-align-items-center is-justify-content-space-between w-full">
            <div>
              <VIcon icon="feather:list" class="mr-2" />
              All Mutations
            </div>
            <div class="control is-flex">
              <VInput v-model="searchQuery" icon="feather:search" placeholder="Search mutations..." />
            </div>
          </div>
        </div>
      </template>
      
      <div class="card-content p-0">
        <VFlexTable
          :data="filteredMutations"
          :columns="mutationColumns"
          :pagination="true"
          :itemsPerPage="8"
        >
          <template #cell-mutation="{ row }">
            <VTag :color="getMutationColor(row)">{{ row.mutation }}</VTag>
          </template>
          
          <template #cell-significance="{ row }">
            <div>
              <div class="mb-1">
                <VTag v-if="row.significance.phenotype !== 'unknown'" size="small" color="info">
                  {{ row.significance.phenotype }}
                </VTag>
              </div>
              
              <div class="is-flex is-flex-wrap-wrap">
                <VTag
                  v-if="row.significance.drug_resistance"
                  size="small"
                  color="danger"
                  class="mr-1 mb-1"
                >
                  Drug Resistance
                </VTag>
                
                <VTag
                  v-if="row.significance.transmission !== 'unknown'"
                  size="small"
                  color="warning"
                  class="mr-1 mb-1"
                >
                  {{ row.significance.transmission }}
                </VTag>
                
                <VTag
                  v-if="row.significance.severity !== 'unknown'"
                  size="small"
                  color="danger"
                  class="mr-1 mb-1"
                >
                  {{ row.significance.severity }}
                </VTag>
              </div>
            </div>
          </template>
        </VFlexTable>
      </div>
    </VCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  mutations: {
    type: Array,
    required: true
  }
})

// State
const searchQuery = ref('')

// Computed
const significantMutations = computed(() => {
  return props.mutations.filter(mutation => {
    const sig = mutation.significance
    return sig.drug_resistance || 
      sig.transmission === 'increased' || 
      sig.severity === 'increased' ||
      sig.phenotype !== 'unknown'
  }).slice(0, 5) // Show top 5 for summary
})

const geneDistribution = computed(() => {
  const genes = {}
  
  // Count mutations per gene
  props.mutations.forEach(mutation => {
    const gene = mutation.gene || 'unknown'
    if (!genes[gene]) {
      genes[gene] = 0
    }
    genes[gene]++
  })
  
  // Convert to array with percentages
  return Object.entries(genes).map(([gene, count]) => {
    return {
      gene,
      count,
      percentage: (count / props.mutations.length) * 100
    }
  }).sort((a, b) => b.count - a.count)
})

const filteredMutations = computed(() => {
  if (!searchQuery.value) {
    return props.mutations
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.mutations.filter(mutation => {
    return mutation.mutation.toLowerCase().includes(query) || 
      mutation.gene.toLowerCase().includes(query) ||
      (mutation.significance.phenotype !== 'unknown' && 
       mutation.significance.phenotype.toLowerCase().includes(query))
  })
})

// Table configurations
const geneColumns = [
  {
    label: 'Gene',
    field: 'gene',
    width: '40%'
  },
  {
    label: 'Count',
    field: 'count',
    width: '20%'
  },
  {
    label: 'Percentage',
    field: 'percentage',
    width: '40%'
  }
]

const mutationColumns = [
  {
    label: 'Mutation',
    field: 'mutation',
    width: '15%'
  },
  {
    label: 'Position',
    field: 'position',
    width: '10%'
  },
  {
    label: 'Gene',
    field: 'gene',
    width: '10%'
  },
  {
    label: 'Change',
    field: (row) => `${row.reference} → ${row.alternate}`,
    width: '15%'
  },
  {
    label: 'Significance',
    field: 'significance',
    width: '50%'
  }
]

// Helper methods
function getMutationColor(mutation) {
  const sig = mutation.significance
  
  if (sig.drug_resistance) {
    return 'danger'
  }
  
  if (sig.transmission === 'increased' || sig.severity === 'increased') {
    return 'warning'
  }
  
  if (sig.phenotype !== 'unknown') {
    return 'info'
  }
  
  return 'primary'
}

function getMutationColorByPercentage(percentage) {
  if (percentage > 50) return 'danger'
  if (percentage > 30) return 'warning'
  if (percentage > 10) return 'info'
  return 'primary'
}

function getSeverityText(mutation) {
  const sig = mutation.significance
  const texts = []
  
  if (sig.drug_resistance) {
    texts.push('Drug resistance')
  }
  
  if (sig.transmission === 'increased') {
    texts.push('Increased transmission')
  }
  
  if (sig.severity === 'increased') {
    texts.push('Increased severity')
  }
  
  if (sig.phenotype !== 'unknown') {
    texts.push(sig.phenotype)
  }
  
  return texts.join(', ')
}
</script>

<style scoped>
.w-full {
  width: 100%;
}
</style>