<template>
  <div class="clinical-trial-publisher">
    <div class="columns">
      <div class="column is-8">
        <div class="columns is-multiline">
          <!--Header-->
          <div class="column is-12">
            <div class="illustration-header-2">
              <div class="header-image">
                <img
                  src="/images/illustrations/dashboards/lifestyle/reading.svg"
                  alt="Clinical Trial Publications"
                >
              </div>
              <div class="header-meta">
                <h3>Clinical Trial Publications</h3>
                <p>
                  Publish insights from clinical trials based on abstraction analysis.
                  Use the identified patterns to create more effective trial publications with
                  <strong>HMS-MFE Writer</strong> integration.
                </p>
                <VButton
                  light
                  outlined
                  icon="lucide:plus"
                  @click="createNewPublication"
                >
                  New Publication
                </VButton>
              </div>
            </div>
          </div>

          <!--Content-->
          <div class="column is-12">
            <div class="publication-stats">
              <!--Stat-->
              <div class="publication-stat">
                <span>Published Trials</span>
                <span class="dark-inverted">{{ stats.publishedTrials }}</span>
              </div>
              <!--Stat-->
              <div class="publication-stat">
                <span>Abstractions</span>
                <span class="dark-inverted">{{ stats.abstractionsCount }}</span>
              </div>
              <!--Stat-->
              <div class="publication-stat">
                <span>Relationships</span>
                <span class="dark-inverted">{{ stats.relationshipsCount }}</span>
              </div>
              <!--Stat-->
              <div class="publication-stat">
                <span>Biomarker Patterns</span>
                <span class="dark-inverted">{{ stats.biomarkerPatterns }}</span>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="api.isLoading" class="loading-container">
              <VLoader size="large" />
              <p class="mt-4">Loading data...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="api.error" class="error-container">
              <VMessage color="danger">
                <p>{{ api.error.message }}</p>
                <VButton size="small" @click="loadInitialData">Retry</VButton>
              </VMessage>
            </div>

            <div v-else class="content-container">
              <div class="key-abstractions" v-if="api.abstractions.length > 0">
                <!--Header-->
                <div class="key-abstractions-header">
                  <h3 class="dark-inverted">
                    Key Abstractions
                  </h3>
                  <a
                    class="action-link"
                    tabindex="0"
                    @click="viewAllAbstractions"
                  >View All</a>
                </div>

                <div class="key-abstractions-list">
                  <div class="columns is-multiline">
                    <div v-for="abstraction in api.abstractions.slice(0, 4)" :key="abstraction.id" class="column is-6">
                      <div 
                        class="abstraction-card" 
                        :class="{'is-selected': isAbstractionSelected(abstraction)}"
                        @click="toggleAbstractionSelection(abstraction)"
                      >
                        <h4 class="dark-inverted">{{ abstraction.name }}</h4>
                        <p>{{ abstraction.description }}</p>
                        <div class="abstraction-confidence">
                          <span>Confidence: {{ abstraction.confidence.toFixed(2) }}</span>
                          <span class="confidence-badge" :style="{background: getConfidenceColor(abstraction.confidence)}"></span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="key-relationships" v-if="abstractionRelationships.length > 0">
                <!--Header-->
                <div class="key-relationships-header">
                  <h3 class="dark-inverted">
                    Key Relationships
                  </h3>
                  <a
                    class="action-link"
                    tabindex="0"
                    @click="viewAllRelationships"
                  >View All</a>
                </div>

                <div class="key-relationships-list">
                  <div v-for="relationship in abstractionRelationships.slice(0, 5)" :key="relationship.source.id + relationship.target.id" class="relationship-item">
                    <div class="relationship-from">
                      <strong>{{ relationship.source.name }}</strong>
                    </div>
                    <div class="relationship-arrow">→</div>
                    <div class="relationship-to">
                      <strong>{{ relationship.target.name }}</strong>
                    </div>
                    <div class="relationship-label">
                      ({{ relationship.type }}: {{ relationship.strength.toFixed(2) }})
                    </div>
                  </div>
                </div>
              </div>

              <div class="clinical-trials" v-if="api.clinicalTrials.length > 0">
                <!--Header-->
                <div class="clinical-trials-header">
                  <h3 class="dark-inverted">
                    Clinical Trials
                  </h3>
                  <a
                    class="action-link"
                    tabindex="0"
                    @click="viewAllTrials"
                  >View All</a>
                </div>

                <div class="clinical-trials-list">
                  <div v-for="trial in api.clinicalTrials.slice(0, 3)" :key="trial.id" 
                    class="clinical-trial-item"
                    :class="{'is-selected': isTrialSelected(trial)}"
                    @click="toggleTrialSelection(trial)"
                  >
                    <div class="trial-header">
                      <h4 class="dark-inverted">{{ trial.title }}</h4>
                      <span class="trial-phase">Phase {{ trial.phase.replace('PHASE_', '') }}</span>
                    </div>
                    <p>{{ truncateDescription(trial.description) }}</p>
                    <div class="trial-meta">
                      <span class="trial-status" :class="trial.status.toLowerCase()">{{ formatTrialStatus(trial.status) }}</span>
                      <span class="trial-dates">{{ formatDate(trial.start_date) }} - {{ trial.end_date ? formatDate(trial.end_date) : 'Ongoing' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="action-panel" v-if="api.hasSelectedAbstractions || api.hasSelectedClinicalTrials">
                <h3 class="dark-inverted">Generate Publication</h3>
                <p>Selected {{ api.selectedAbstractions.length }} abstractions and {{ api.selectedClinicalTrials.length }} clinical trials</p>
                <div class="action-buttons">
                  <VButton
                    color="primary"
                    :disabled="!canGeneratePublication"
                    @click="generatePublication"
                  >
                    Generate Draft
                  </VButton>
                  <VButton
                    color="info"
                    :disabled="!canGeneratePublication"
                    @click="publishToHmsDoc"
                  >
                    Publish to HMS-DOC
                  </VButton>
                  <VButton
                    color="success"
                    :disabled="!canGeneratePublication"
                    @click="publishToHmsMfe"
                  >
                    Publish to HMS-MFE
                  </VButton>
                  <VButton
                    light
                    @click="api.clearSelections"
                  >
                    Clear Selection
                  </VButton>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!--Publication Feed-->
      <div class="column is-4">
        <div class="publications-feed">
          <!--Header-->
          <div class="publications-feed-header">
            <h3 class="dark-inverted">
              Recent Publications
            </h3>
            <a
              class="action-link"
              tabindex="0"
              @click="viewAllPublications"
            >View All</a>
          </div>

          <!-- Loading State -->
          <div v-if="api.isLoading" class="loading-container">
            <VLoader size="medium" />
            <p class="mt-2">Loading publications...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="api.publications.length === 0" class="empty-state">
            <p>No publications found. Create your first publication by selecting abstractions and clinical trials.</p>
          </div>

          <!--List-->
          <div v-else class="publications-feed-list">
            <div class="publications-feed-list-inner">
              <div v-for="publication in api.publications" :key="publication.id" class="publications-feed-item">
                <div class="featured-image">
                  <img
                    src="https://media.cssninja.io/content/photos/38.jpg"
                    alt="Publication Image"
                    @error.once="onImageError($event)"
                  >
                </div>
                <div class="featured-content">
                  <h4 class="dark-inverted">{{ publication.title }}</h4>
                  <p>{{ truncateText(publication.content, 120) }}</p>
                  <div class="publication-meta">
                    <span class="publication-date">{{ formatDate(publication.created_at) }}</span>
                    <span class="publication-status" :class="publication.status.toLowerCase()">{{ formatPublicationStatus(publication.status) }}</span>
                  </div>
                  <div class="publication-actions">
                    <VButton
                      size="small"
                      color="primary"
                      raised
                      @click="viewPublication(publication)"
                    >
                      View
                    </VButton>
                    <VButton
                      size="small"
                      light
                      @click="editPublication(publication)"
                    >
                      Edit
                    </VButton>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Publication Modal -->
    <VModal
      :open="isPublicationModalOpen"
      size="large"
      @close="closePublicationModal"
    >
      <template #content>
        <div class="modal-content">
          <div class="modal-card">
            <header class="modal-card-head">
              <h3>{{ currentModal === 'new' ? 'Create New Publication' : 'Edit Publication' }}</h3>
              <button
                class="modal-close-btn"
                @click="closePublicationModal"
              >
                <i class="iconify" data-icon="feather:x"></i>
              </button>
            </header>
            <div class="modal-card-body">
              <div class="field">
                <label>Title</label>
                <div class="control">
                  <input
                    type="text"
                    class="input"
                    v-model="editingPublication.title"
                    placeholder="Publication Title"
                  >
                </div>
              </div>
              
              <div class="field">
                <label>Content</label>
                <div class="control">
                  <VMarkdownEditor v-model="editingPublication.content" />
                  <div class="editor-actions mt-2">
                    <VButton
                      size="small"
                      color="info"
                      @click="importFromWriter"
                    >
                      Import from Writer
                    </VButton>
                  </div>
                </div>
              </div>
              
              <div class="field">
                <label>Status</label>
                <div class="control">
                  <div class="select is-fullwidth">
                    <select v-model="editingPublication.status">
                      <option value="DRAFT">Draft</option>
                      <option value="PUBLISHED">Published</option>
                      <option value="ARCHIVED">Archived</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div class="field">
                <label>Clinical Trials</label>
                <div class="control">
                  <div class="select is-multiple is-fullwidth">
                    <select multiple v-model="editingTrialIds">
                      <option 
                        v-for="trial in api.clinicalTrials" 
                        :key="trial.id" 
                        :value="trial.id"
                      >
                        {{ trial.title }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div class="field">
                <label>Abstractions</label>
                <div class="control">
                  <div class="select is-multiple is-fullwidth">
                    <select multiple v-model="editingAbstractionIds">
                      <option 
                        v-for="abstraction in api.abstractions" 
                        :key="abstraction.id" 
                        :value="abstraction.id"
                      >
                        {{ abstraction.name }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <footer class="modal-card-foot">
              <VButton
                color="primary"
                raised
                :loading="api.isLoading"
                @click="savePublication"
              >
                {{ currentModal === 'new' ? 'Create' : 'Update' }}
              </VButton>
              <VButton
                light
                @click="closePublicationModal"
              >
                Cancel
              </VButton>
            </footer>
          </div>
        </div>
      </template>
    </VModal>

    <!-- View Publication Modal -->
    <VModal
      :open="isViewModalOpen"
      size="large"
      @close="closeViewModal"
    >
      <template #content>
        <div class="modal-content">
          <div class="modal-card">
            <header class="modal-card-head">
              <h3>{{ selectedPublication.title }}</h3>
              <button
                class="modal-close-btn"
                @click="closeViewModal"
              >
                <i class="iconify" data-icon="feather:x"></i>
              </button>
            </header>
            <div class="modal-card-body">
              <div class="publication-view">
                <div class="featured-image">
                  <img src="https://media.cssninja.io/content/photos/38.jpg" alt="Publication Image">
                </div>
                
                <div class="publication-meta">
                  <div class="publication-dates">
                    <span><strong>Created:</strong> {{ formatDate(selectedPublication.created_at) }}</span>
                    <span><strong>Updated:</strong> {{ formatDate(selectedPublication.updated_at) }}</span>
                  </div>
                  <span class="publication-status" :class="selectedPublication.status?.toLowerCase()">
                    {{ formatPublicationStatus(selectedPublication.status) }}
                  </span>
                </div>
                
                <div class="publication-content">
                  <VMarkdownPreview :source="selectedPublication.content" />
                </div>
                
                <div class="publication-abstractions" v-if="selectedPublicationAbstractions.length">
                  <h4>Related Abstractions</h4>
                  <div class="tags">
                    <span 
                      v-for="abstraction in selectedPublicationAbstractions" 
                      :key="abstraction.id" 
                      class="tag is-primary"
                    >
                      {{ abstraction.name }}
                    </span>
                  </div>
                </div>
                
                <div class="publication-trials" v-if="selectedPublicationTrials.length">
                  <h4>Clinical Trials</h4>
                  <div class="tags">
                    <span 
                      v-for="trial in selectedPublicationTrials" 
                      :key="trial.id" 
                      class="tag is-info"
                    >
                      {{ trial.title }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <footer class="modal-card-foot">
              <VButton
                color="primary"
                @click="editPublication(selectedPublication)"
              >
                Edit
              </VButton>
              <VButton
                color="info"
                @click="openInWriter(selectedPublication)"
              >
                Open in Writer
              </VButton>
              <VButton
                light
                @click="closeViewModal"
              >
                Close
              </VButton>
            </footer>
          </div>
        </div>
      </template>
    </VModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useVueroContext } from '/@src/composables/vuero-context'
import { useClinicalTrialApi } from './use-clinical-trial-api'
import { type Abstraction, type ClinicalTrial, type Publication } from './clinical-trial-api'
import { writerIntegrationService } from './writer-integration'

// Initialize the API
const api = useClinicalTrialApi()

// Set page title
const pageTitle = useVueroContext<string>('page-title')
onMounted(() => {
  pageTitle.value = 'Clinical Trial Publications'
  // Load initial data
  loadInitialData()
})

// Default placeholder image handler
const onImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/images/placeholders/placeholder.png'
}

// Load initial data from the API
const loadInitialData = async () => {
  await Promise.all([
    api.loadAbstractions(),
    api.loadClinicalTrials(),
    api.loadPublications()
  ])
}

// Computed relationships from abstractions
const abstractionRelationships = computed(() => {
  const relationships: {
    source: Abstraction;
    target: Abstraction;
    type: string;
    strength: number;
  }[] = []

  api.abstractions.forEach(abstraction => {
    abstraction.related_entities.forEach(entity => {
      const targetAbstraction = api.abstractions.find(a => a.id === entity.id)
      if (targetAbstraction) {
        relationships.push({
          source: abstraction,
          target: targetAbstraction,
          type: entity.type,
          strength: entity.strength
        })
      }
    })
  })

  return relationships
})

// Statistics
const stats = computed(() => {
  return {
    publishedTrials: api.publications.length,
    abstractionsCount: api.abstractions.length,
    relationshipsCount: abstractionRelationships.value.length,
    biomarkerPatterns: api.abstractions.filter(a => a.type === 'BIOMARKER_PATTERN').length
  }
})

// Modal handling
const isPublicationModalOpen = ref(false)
const isViewModalOpen = ref(false)
const currentModal = ref<'new' | 'edit'>('new')
const selectedPublication = ref<Publication>({} as Publication)
const editingPublication = ref<Publication>({
  id: '',
  title: '',
  created_at: '',
  updated_at: '',
  status: 'DRAFT',
  content: '',
  author: '',
  clinical_trial_ids: [],
  abstraction_ids: [],
  visualization_ids: []
})
const editingTrialIds = ref<string[]>([])
const editingAbstractionIds = ref<string[]>([])

// Selected publication related data
const selectedPublicationAbstractions = computed(() => {
  if (!selectedPublication.value?.abstraction_ids?.length) return []
  return api.abstractions.filter(a => 
    selectedPublication.value.abstraction_ids.includes(a.id)
  )
})

const selectedPublicationTrials = computed(() => {
  if (!selectedPublication.value?.clinical_trial_ids?.length) return []
  return api.clinicalTrials.filter(t => 
    selectedPublication.value.clinical_trial_ids.includes(t.id)
  )
})

// Can generate publication check
const canGeneratePublication = computed(() => {
  return api.selectedAbstractions.length > 0 && api.selectedClinicalTrials.length > 0
})

// Helper functions
const truncateText = (text: string, maxLength: number): string => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const truncateDescription = (description: string): string => {
  return truncateText(description, 150)
}

const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatTrialStatus = (status: string): string => {
  return status.replace(/_/g, ' ').toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase())
}

const formatPublicationStatus = (status: string): string => {
  if (!status) return ''
  return status.toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase())
}

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return '#4CAF50'  // Green
  if (confidence >= 0.6) return '#2196F3'  // Blue
  if (confidence >= 0.4) return '#FF9800'  // Orange
  return '#F44336'  // Red
}

// Selection handling
const isAbstractionSelected = (abstraction: Abstraction): boolean => {
  return api.selectedAbstractions.some(a => a.id === abstraction.id)
}

const toggleAbstractionSelection = (abstraction: Abstraction): void => {
  api.toggleAbstractionSelection(abstraction)
}

const isTrialSelected = (trial: ClinicalTrial): boolean => {
  return api.selectedClinicalTrials.some(t => t.id === trial.id)
}

const toggleTrialSelection = (trial: ClinicalTrial): void => {
  api.toggleClinicalTrialSelection(trial)
}

// Publication actions
const createNewPublication = () => {
  currentModal.value = 'new'
  api.createEmptyPublication()
  editingPublication.value = { ...api.currentPublication.value } as Publication
  editingTrialIds.value = []
  editingAbstractionIds.value = []
  isPublicationModalOpen.value = true
}

const editPublication = (publication: Publication) => {
  currentModal.value = 'edit'
  editingPublication.value = { ...publication }
  editingTrialIds.value = [...publication.clinical_trial_ids]
  editingAbstractionIds.value = [...publication.abstraction_ids]
  isPublicationModalOpen.value = true
  isViewModalOpen.value = false
}

const savePublication = async () => {
  // Update IDs from selected values
  editingPublication.value.clinical_trial_ids = editingTrialIds.value
  editingPublication.value.abstraction_ids = editingAbstractionIds.value
  
  if (currentModal.value === 'new') {
    await api.createPublication(editingPublication.value)
  } else {
    await api.updatePublication(editingPublication.value.id, editingPublication.value)
  }
  
  isPublicationModalOpen.value = false
}

const viewPublication = (publication: Publication) => {
  selectedPublication.value = { ...publication }
  isViewModalOpen.value = true
}

const closePublicationModal = () => {
  isPublicationModalOpen.value = false
}

const closeViewModal = () => {
  isViewModalOpen.value = false
}

// Generate publication from selected abstractions and trials
const generatePublication = async () => {
  // Generate a draft based on selected abstractions and trials
  const result = await api.generatePublicationDraft({
    includeVisualizations: true,
    format: 'markdown'
  })

  if (result) {
    // Create a new publication with the generated content
    api.createEmptyPublication()
    if (api.currentPublication.value) {
      editingPublication.value = { ...api.currentPublication.value } as Publication
      editingPublication.value.content = result.content
      editingPublication.value.title = `Generated Publication (${new Date().toLocaleDateString()})`
      editingPublication.value.clinical_trial_ids = api.selectedClinicalTrials.map(t => t.id)
      editingPublication.value.abstraction_ids = api.selectedAbstractions.map(a => a.id)
      editingTrialIds.value = editingPublication.value.clinical_trial_ids
      editingAbstractionIds.value = editingPublication.value.abstraction_ids

      currentModal.value = 'new'
      isPublicationModalOpen.value = true
    }
  }
}

// Publish selected abstractions and relationships to HMS-DOC
const publishToHmsDoc = async () => {
  if (!canGeneratePublication.value) {
    alert('Please select at least one abstraction and one clinical trial')
    return
  }

  try {
    // Generate relationships between selected abstractions
    const relationships = generateRelationships(api.selectedAbstractions)

    // Call the API to export to HMS-DOC
    const result = await clinicalTrialApi.exportAbstractionsToDoc(
      api.selectedAbstractions,
      relationships,
      `Crohns-Abstractions-${new Date().toISOString().split('T')[0]}`
    )

    if (result && result.output_path) {
      alert(`Successfully published to HMS-DOC!\nDocumentation available at: ${result.output_path}`)
    } else {
      alert('Publication to HMS-DOC completed, but no output path was returned')
    }
  } catch (error) {
    console.error('Error publishing to HMS-DOC:', error)
    alert(`Failed to publish to HMS-DOC: ${error}`)
  }
}

// Generate relationships between abstractions for documentation
const generateRelationships = (abstractions: Abstraction[]) => {
  const relationships: any[] = []

  // Generate basic relationships based on related_entities
  abstractions.forEach((abstraction, index) => {
    abstraction.related_entities.forEach(entity => {
      // Find target abstraction
      const targetIndex = abstractions.findIndex(a => a.id === entity.id)
      if (targetIndex >= 0) {
        relationships.push({
          source: index,
          target: targetIndex,
          type: entity.type
        })
      }
    })
  })

  // If no relationships were found, create a simple chain
  if (relationships.length === 0 && abstractions.length > 1) {
    for (let i = 0; i < abstractions.length - 1; i++) {
      relationships.push({
        source: i,
        target: i + 1,
        type: 'Related to'
      })
    }
  }

  return relationships
}

// Publish selected clinical trials to HMS-MFE writer
const publishToHmsMfe = async () => {
  if (!canGeneratePublication.value) {
    alert('Please select at least one abstraction and one clinical trial')
    return
  }

  try {
    // Only publish the first selected trial for simplicity
    const trialData = api.selectedClinicalTrials[0]

    const writerPath = '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue'

    // Call the API to publish to HMS-MFE
    const result = await clinicalTrialApi.publishTrialToMfe(
      trialData,
      api.selectedAbstractions,
      writerPath
    )

    if (result && result.publication_info) {
      alert(`Successfully published to HMS-MFE writer!\n${JSON.stringify(result.publication_info, null, 2)}`)
    } else {
      alert('Publication to HMS-MFE completed, but no publication info was returned')
    }
  } catch (error) {
    console.error('Error publishing to HMS-MFE:', error)
    alert(`Failed to publish to HMS-MFE: ${error}`)
  }
}

// View all actions
const viewAllAbstractions = () => {
  // To be implemented - navigate to abstractions page
  console.log('View all abstractions')
}

const viewAllRelationships = () => {
  // To be implemented - navigate to relationships page
  console.log('View all relationships')
}

const viewAllPublications = () => {
  // To be implemented - navigate to publications page
  console.log('View all publications')
}

const viewAllTrials = () => {
  // To be implemented - navigate to trials page
  console.log('View all trials')
}

// Writer integration
const openInWriter = async (publication: Publication) => {
  const success = await writerIntegrationService.openInWriter(publication)
  if (!success) {
    // Show error notification - in a real implementation, this would use a toast notification
    alert('Failed to open in writer. Please try again.')
  }
  // Close the view modal
  closeViewModal()
}

// Mock function to simulate importing from the writer component
// In a real implementation, this would use IPC or browser messaging to communicate with the writer
const importFromWriter = async () => {
  // This simulates the data we might receive from the writer component
  const mockWriterData = {
    id: 'mock-writer-' + Date.now(),
    title: 'Content from HMS-MFE Writer',
    content: `## Clinical Trial Publication

This content was imported from the HMS-MFE Writer component at:
\`/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue\`

### Key Findings

- The trial demonstrated significant efficacy in patients with specific biomarkers
- Adverse events were minimal and consistent with safety profiles
- Stratification by genetic markers improved outcomes
- Adaptive trial design reduced time to completion by 15%

### Methodology

The trial utilized an adaptive design with biomarker-based stratification, allowing for more efficient patient allocation and interim analyses.

### Conclusion

The results suggest that the treatment is effective for patients with specific genetic markers, supporting the use of personalized medicine approaches in Crohn's disease.`,
    metadata: {
      abstractionIds: editingPublication.value.abstraction_ids,
      clinicalTrialIds: editingPublication.value.clinical_trial_ids,
      author: 'HMS-MFE Writer'
    }
  }

  // Import the data from the writer using our service
  const importedPublication = writerIntegrationService.importFromWriter(mockWriterData)

  // Update only the content and title, keeping other properties from our current editing state
  editingPublication.value.content = importedPublication.content
  editingPublication.value.title = importedPublication.title

  // Show success message
  alert('Content successfully imported from writer')
}
</script>

<style lang="scss">
.clinical-trial-publisher {
  .illustration-header-2 {
    display: flex;
    align-items: center;
    padding: 10px;
    border-radius: 16px;
    background: var(--primary);
    font-family: var(--font);
    box-shadow: var(--primary-box-shadow);

    .header-image {
      position: relative;
      height: 175px;
      width: 320px;

      img {
        position: absolute;
        top: 0;
        inset-inline-start: -40px;
        display: block;
        pointer-events: none;
      }
    }

    .header-meta {
      margin-inline-start: 0;
      padding-inline-end: 30px;

      h3 {
        color: var(--smoke-white);
        font-family: var(--font-alt);
        font-weight: 700;
        font-size: 1.3rem;
        max-width: 280px;
      }

      p {
        font-weight: 400;
        color: color-mix(in oklab, var(--smoke-white), black 2%);
        margin-bottom: 16px;
        max-width: 320px;
      }
    }
  }

  .publication-stats {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 1rem;
    margin-inline-start: -8px;
    margin-inline-end: -8px;

    .publication-stat {
      background: var(--white);
      border-radius: 8px;
      border: 1px solid var(--fade-grey);
      padding: 12px;
      margin: 8px;
      width: calc(25% - 16px);
      box-shadow: var(--light-box-shadow);

      span {
        display: block;

        &:first-child {
          font-family: var(--font-alt);
          font-size: 0.8rem;
          font-weight: 500;
          text-transform: uppercase;
          margin-bottom: 5px;
          color: var(--light-text);
        }

        &:nth-child(2) {
          font-family: var(--font);
          font-weight: 700;
          font-size: 1.8rem;
          color: var(--dark-text);
        }
      }
    }
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    text-align: center;
  }

  .error-container {
    padding: 20px 0;
  }

  .empty-state {
    padding: 30px;
    text-align: center;
    color: var(--light-text);
    border-radius: 8px;
    background: var(--widget-grey);
  }

  .key-abstractions, .key-relationships, .clinical-trials {
    background: var(--white);
    border-radius: 8px;
    border: 1px solid var(--fade-grey);
    padding: 20px;
    margin-bottom: 1rem;
    box-shadow: var(--light-box-shadow);

    &-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;

      h3 {
        font-family: var(--font-alt);
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--dark-text);
      }

      .action-link {
        font-size: 0.9rem;
      }
    }
  }

  .abstraction-card {
    padding: 15px;
    border-radius: 8px;
    background: var(--widget-grey);
    height: 100%;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    cursor: pointer;

    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--light-box-shadow);
    }

    &.is-selected {
      border-color: var(--primary);
      background: color-mix(in oklab, var(--primary), white 90%);
    }

    h4 {
      font-family: var(--font-alt);
      font-weight: 600;
      font-size: 1rem;
      color: var(--dark-text);
      margin-bottom: 8px;
    }

    p {
      font-size: 0.9rem;
      color: var(--light-text);
      margin-bottom: 8px;
    }

    .abstraction-confidence {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.8rem;
      color: var(--light-text);

      .confidence-badge {
        width: 10px;
        height: 10px;
        border-radius: 50%;
      }
    }
  }

  .relationship-item {
    display: flex;
    align-items: center;
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 8px;
    background: var(--widget-grey);

    .relationship-arrow {
      margin: 0 10px;
      font-size: 24px;
      color: var(--primary);
    }

    .relationship-label {
      margin-left: 10px;
      color: var(--light-text);
      font-size: 0.9rem;
    }
  }

  .clinical-trial-item {
    padding: 15px;
    border-radius: 8px;
    background: var(--widget-grey);
    margin-bottom: 15px;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    cursor: pointer;

    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--light-box-shadow);
    }

    &.is-selected {
      border-color: var(--primary);
      background: color-mix(in oklab, var(--primary), white 90%);
    }

    .trial-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      h4 {
        font-family: var(--font-alt);
        font-weight: 600;
        font-size: 1rem;
        color: var(--dark-text);
        margin-right: 10px;
      }

      .trial-phase {
        font-size: 0.8rem;
        background: var(--primary);
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        white-space: nowrap;
      }
    }

    p {
      font-size: 0.9rem;
      color: var(--light-text);
      margin-bottom: 10px;
    }

    .trial-meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.8rem;

      .trial-status {
        padding: 2px 8px;
        border-radius: 12px;
        text-transform: capitalize;

        &.recruiting {
          background: #4CAF50;
          color: white;
        }

        &.ongoing {
          background: #2196F3;
          color: white;
        }

        &.completed {
          background: #9E9E9E;
          color: white;
        }

        &.planned {
          background: #FF9800;
          color: white;
        }
      }

      .trial-dates {
        color: var(--light-text);
      }
    }
  }

  .action-panel {
    background: var(--white);
    border-radius: 8px;
    border: 1px solid var(--fade-grey);
    padding: 20px;
    margin-bottom: 1rem;
    box-shadow: var(--light-box-shadow);
    text-align: center;

    h3 {
      font-family: var(--font-alt);
      font-weight: 600;
      font-size: 1.1rem;
      color: var(--dark-text);
      margin-bottom: 10px;
    }

    p {
      margin-bottom: 15px;
    }

    .action-buttons {
      display: flex;
      justify-content: center;
      gap: 10px;
    }
  }

  .publications-feed {
    background: var(--widget-grey);
    padding: 30px;
    border-radius: 12px;

    &-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;

      h3 {
        font-family: var(--font-alt);
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--dark-text);
      }

      .action-link {
        font-size: 0.9rem;
      }
    }

    &-list {
      &-inner {
        .publications-feed-item {
          display: block;
          margin-bottom: 30px;

          .featured-image {
            height: 180px;
            overflow: hidden;
            border-start-start-radius: 18px;
            border-start-end-radius: 18px;

            img {
              display: block;
              width: 100%;
              height: 100%;
              object-fit: cover;
            }
          }

          .featured-content {
            position: relative;
            padding: 25px;
            border-radius: 18px;
            background: var(--white);
            margin-top: -40px;
            z-index: 1;

            h4 {
              font-family: var(--font-alt);
              font-size: 1rem;
              font-weight: 600;
              color: var(--dark-text);
              margin-bottom: 10px;
            }

            p {
              margin-bottom: 15px;
              font-size: 0.9rem;
            }

            .publication-meta {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 15px;
              font-size: 0.8rem;

              .publication-date {
                color: var(--light-text);
              }

              .publication-status {
                padding: 2px 8px;
                border-radius: 12px;
                text-transform: capitalize;

                &.draft {
                  background: #FFC107;
                  color: #333;
                }

                &.published {
                  background: #4CAF50;
                  color: white;
                }

                &.archived {
                  background: #9E9E9E;
                  color: white;
                }
              }
            }

            .publication-actions {
              display: flex;
              justify-content: flex-end;
              gap: 10px;
            }
          }
        }
      }
    }
  }

  .publication-view {
    .featured-image {
      width: 100%;
      max-height: 300px;
      overflow: hidden;
      margin-bottom: 20px;
      border-radius: 8px;

      img {
        width: 100%;
        object-fit: cover;
      }
    }

    .publication-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .publication-dates {
        display: flex;
        flex-direction: column;
        gap: 5px;
        font-size: 0.9rem;
        color: var(--light-text);
      }
      
      .publication-status {
        padding: 5px 10px;
        border-radius: 12px;
        text-transform: capitalize;
        font-size: 0.9rem;

        &.draft {
          background: #FFC107;
          color: #333;
        }

        &.published {
          background: #4CAF50;
          color: white;
        }

        &.archived {
          background: #9E9E9E;
          color: white;
        }
      }
    }

    .publication-content {
      margin-bottom: 20px;
    }

    .publication-abstractions, .publication-trials {
      margin-bottom: 20px;
      
      h4 {
        font-family: var(--font-alt);
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--dark-text);
        margin-bottom: 10px;
      }
      
      .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
      }
    }
  }
}

/* Dark mode styles */
.is-dark {
  .clinical-trial-publisher {
    .illustration-header-2 {
      background: var(--dark-sidebar);
      box-shadow: none;
    }

    .publication-stats {
      .publication-stat {
        background: var(--dark-sidebar);
        border-color: var(--dark-sidebar-light-6);
      }
    }

    .key-abstractions, .key-relationships, .clinical-trials, .action-panel {
      background: var(--dark-sidebar);
      border-color: var(--dark-sidebar-light-6);
    }

    .abstraction-card, .relationship-item, .clinical-trial-item {
      background: color-mix(in oklab, var(--dark-sidebar), white 8%);
    }

    .publications-feed {
      background: color-mix(in oklab, var(--dark-sidebar), white 8%);

      &-list-inner {
        .publications-feed-item {
          .featured-content {
            background: var(--dark-sidebar);
          }
        }
      }
    }
  }
}

/* Responsive styles */
@media only screen and (width <= 767px) {
  .clinical-trial-publisher {
    .illustration-header-2 {
      flex-direction: column;
      text-align: center;

      .header-image {
        height: auto;
        width: 100%;

        img {
          position: relative;
          width: 100%;
          max-width: 260px;
          margin: 0 auto;
          top: 0;
          inset-inline-start: 0;
          margin-top: -34px;
        }
      }

      .header-meta {
        padding: 20px;

        > p {
          max-width: 280px;
          margin-inline-start: auto;
          margin-inline-end: auto;
        }
      }
    }

    .publication-stats {
      .publication-stat {
        width: calc(50% - 16px);
        text-align: center;
      }
    }
  }
}
</style>