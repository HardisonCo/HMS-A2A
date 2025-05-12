<template>
  <div class="integration-dashboard">
    <div class="dashboard-header">
      <h2 class="title">HMS Integration Dashboard</h2>
      <p class="subtitle">Manage documentation and publications across HMS components</p>
    </div>
    
    <div class="dashboard-metrics card">
      <div class="card-content">
        <h3>System Integration Status</h3>
        <div class="metrics-grid">
          <div class="metric-item">
            <div class="metric-icon" :class="{ active: hmsDocAvailable }">
              <i class="icon-doc"></i>
            </div>
            <div class="metric-content">
              <span class="metric-label">HMS-DOC</span>
              <span class="metric-value">{{ hmsDocAvailable ? 'Connected' : 'Disconnected' }}</span>
            </div>
          </div>
          
          <div class="metric-item">
            <div class="metric-icon" :class="{ active: hmsMfeAvailable }">
              <i class="icon-mfe"></i>
            </div>
            <div class="metric-content">
              <span class="metric-label">HMS-MFE</span>
              <span class="metric-value">{{ hmsMfeAvailable ? 'Connected' : 'Disconnected' }}</span>
            </div>
          </div>
          
          <div class="metric-item">
            <div class="metric-icon" :class="{ active: docPublications.length > 0 }">
              <i class="icon-docs"></i>
            </div>
            <div class="metric-content">
              <span class="metric-label">Doc Publications</span>
              <span class="metric-value">{{ docPublications.length }}</span>
            </div>
          </div>
          
          <div class="metric-item">
            <div class="metric-icon" :class="{ active: mfePublications.length > 0 }">
              <i class="icon-publications"></i>
            </div>
            <div class="metric-content">
              <span class="metric-label">MFE Publications</span>
              <span class="metric-value">{{ mfePublications.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="dashboard-actions card">
      <div class="card-content">
        <h3>Integrated Documentation Tools</h3>
        <div class="action-buttons">
          <button 
            class="btn btn-primary"
            :disabled="!canGenerateDocumentation"
            @click="generateComprehensiveDocumentation"
          >
            Generate Comprehensive Documentation
          </button>
          
          <button 
            class="btn btn-info"
            :disabled="!canExportToDoc"
            @click="exportToHmsDoc"
          >
            Export to HMS-DOC
          </button>
          
          <button 
            class="btn btn-success"
            :disabled="!canPublishToMfe"  
            @click="publishToHmsMfe"
          >
            Publish to HMS-MFE
          </button>
        </div>
      </div>
    </div>
    
    <div class="dashboard-tabs">
      <div class="tabs-header">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'doc' }"
          @click="activeTab = 'doc'"
        >
          HMS-DOC Publications
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'mfe' }"
          @click="activeTab = 'mfe'"
        >
          HMS-MFE Publications
        </button>
      </div>
      
      <div class="tab-content">
        <!-- HMS-DOC Publications Tab -->
        <div v-if="activeTab === 'doc'" class="doc-publications">
          <div v-if="isLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading HMS-DOC publications...</p>
          </div>
          
          <div v-else-if="docPublications.length === 0" class="empty-state">
            <p>No HMS-DOC publications found. Generate documentation to get started.</p>
          </div>
          
          <div v-else class="publications-list">
            <div v-for="(pub, index) in docPublications" :key="index" class="publication-item card">
              <div class="card-content">
                <h4 class="pub-title">{{ pub.project_name }}</h4>
                <div class="pub-meta">
                  <span class="pub-date">{{ formatDate(pub.timestamp) }}</span>
                  <span class="pub-status" :class="pub.status">{{ pub.status }}</span>
                </div>
                <p class="pub-path">{{ pub.output_path }}</p>
                <div class="pub-actions">
                  <button class="btn btn-sm btn-primary" @click="openDocPublication(pub)">
                    Open
                  </button>
                  <button class="btn btn-sm btn-info" @click="viewDocDetails(pub)">
                    Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- HMS-MFE Publications Tab -->
        <div v-if="activeTab === 'mfe'" class="mfe-publications">
          <div v-if="isLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading HMS-MFE publications...</p>
          </div>
          
          <div v-else-if="mfePublications.length === 0" class="empty-state">
            <p>No HMS-MFE publications found. Publish to HMS-MFE to get started.</p>
          </div>
          
          <div v-else class="publications-list">
            <div v-for="(pub, index) in mfePublications" :key="index" class="publication-item card">
              <div class="card-content">
                <h4 class="pub-title">{{ pub.title || 'Untitled Publication' }}</h4>
                <div class="pub-meta">
                  <span class="pub-date">{{ formatDate(pub.timestamp) }}</span>
                  <span class="pub-status" :class="pub.status">{{ pub.status }}</span>
                </div>
                <p class="pub-id">ID: {{ pub.publication_id }}</p>
                <div class="pub-actions">
                  <button class="btn btn-sm btn-primary" @click="openMfePublication(pub)">
                    Open in Writer
                  </button>
                  <button class="btn btn-sm btn-info" @click="viewMfeDetails(pub)">
                    Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Publication Details Modal -->
    <div class="modal" :class="{ 'is-active': isModalOpen }">
      <div class="modal-background" @click="closeModal"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Publication Details</p>
          <button class="delete" aria-label="close" @click="closeModal"></button>
        </header>
        <section class="modal-card-body">
          <div v-if="selectedPublication">
            <h4>{{ selectedPublication.project_name || selectedPublication.title || 'Publication Details' }}</h4>
            
            <div class="details-section">
              <h5>General Information</h5>
              <div class="detail-item">
                <span class="detail-label">Publication Date:</span>
                <span class="detail-value">{{ formatDate(selectedPublication.timestamp) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Status:</span>
                <span class="detail-value">{{ selectedPublication.status }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">System:</span>
                <span class="detail-value">{{ activeTab === 'doc' ? 'HMS-DOC' : 'HMS-MFE' }}</span>
              </div>
            </div>
            
            <div class="details-section">
              <h5>Publication Details</h5>
              <pre class="publication-json">{{ JSON.stringify(selectedPublication, null, 2) }}</pre>
            </div>
          </div>
        </section>
        <footer class="modal-card-foot">
          <button class="button" @click="closeModal">Close</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { clinicalTrialApi } from './clinical-trial-api'

// Component state
const activeTab = ref<'doc' | 'mfe'>('doc')
const isLoading = ref(false)
const docPublications = ref<any[]>([])
const mfePublications = ref<any[]>([])
const hmsDocAvailable = ref(false)
const hmsMfeAvailable = ref(true)
const isModalOpen = ref(false)
const selectedPublication = ref<any>(null)

// Integration status
const canGenerateDocumentation = computed(() => hmsDocAvailable.value && hmsMfeAvailable.value)
const canExportToDoc = computed(() => hmsDocAvailable.value)
const canPublishToMfe = computed(() => hmsMfeAvailable.value)

// Load publications on component mount
onMounted(async () => {
  await loadPublications()
  await checkIntegrationStatus()
})

// Format date for display
const formatDate = (dateString: string): string => {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// Load publications from storage or API
const loadPublications = async () => {
  isLoading.value = true
  
  try {
    // In a real implementation, these would be loaded from an API
    // For demonstration, we'll use mock data stored in localStorage
    
    const savedDocPubs = localStorage.getItem('hms_doc_publications')
    const savedMfePubs = localStorage.getItem('hms_mfe_publications')
    
    if (savedDocPubs) {
      docPublications.value = JSON.parse(savedDocPubs)
    }
    
    if (savedMfePubs) {
      mfePublications.value = JSON.parse(savedMfePubs)
    }
  } catch (error) {
    console.error('Error loading publications:', error)
  } finally {
    isLoading.value = false
  }
}

// Check if HMS-DOC and HMS-MFE are available
const checkIntegrationStatus = async () => {
  try {
    // For demonstration purposes, we'll use mock checks
    // In a real implementation, these would be API calls
    
    // Check HMS-DOC availability
    const docRootPath = '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-DOC'
    const mfeRootPath = '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE'
    
    // Simulate availability check - in reality would be an API call
    setTimeout(() => {
      hmsDocAvailable.value = true
      hmsMfeAvailable.value = true
    }, 1000)
  } catch (error) {
    console.error('Error checking integration status:', error)
  }
}

// Generate comprehensive documentation
const generateComprehensiveDocumentation = async () => {
  isLoading.value = true
  
  try {
    // This would call the backend API in a real implementation
    // For demonstration, we'll create a mock publication

    const newPublication = {
      project_name: `Comprehensive Crohns Documentation ${new Date().toLocaleDateString()}`,
      output_path: `/Users/arionhardison/Desktop/Codify/output/documentation/comprehensive-${Date.now()}`,
      timestamp: new Date().toISOString(),
      status: 'completed',
      documentation_info: {
        abstractions_count: 12,
        clinical_trials_count: 5,
        relationships_count: 18
      }
    }
    
    // Add to doc publications
    docPublications.value = [newPublication, ...docPublications.value]
    
    // Save to localStorage for persistence
    localStorage.setItem('hms_doc_publications', JSON.stringify(docPublications.value))
    
    // Simulate simultaneous MFE publication
    const mfePublication = {
      publication_id: `mfe-${Date.now()}`,
      title: `Clinical Trial Data for ${new Date().toLocaleDateString()}`,
      timestamp: new Date().toISOString(),
      status: 'published',
      writer_component: '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue',
      file_path: '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/json-server/data/publication.json'
    }
    
    // Add to mfe publications
    mfePublications.value = [mfePublication, ...mfePublications.value]
    
    // Save to localStorage for persistence
    localStorage.setItem('hms_mfe_publications', JSON.stringify(mfePublications.value))
    
    // Show success message
    alert('Comprehensive documentation generated successfully!')
  } catch (error) {
    console.error('Error generating documentation:', error)
    alert(`Error generating documentation: ${error}`)
  } finally {
    isLoading.value = false
  }
}

// Export to HMS-DOC
const exportToHmsDoc = async () => {
  isLoading.value = true
  
  try {
    // This would call the backend API in a real implementation
    // For demonstration, we'll create a mock publication
    
    const newPublication = {
      project_name: `Crohns Abstractions ${new Date().toLocaleDateString()}`,
      output_path: `/Users/arionhardison/Desktop/Codify/output/documentation/abstractions-${Date.now()}`,
      timestamp: new Date().toISOString(),
      status: 'completed',
      abstractions_count: 8,
      relationships_count: 12
    }
    
    // Add to doc publications
    docPublications.value = [newPublication, ...docPublications.value]
    
    // Save to localStorage for persistence
    localStorage.setItem('hms_doc_publications', JSON.stringify(docPublications.value))
    
    // Show success message
    alert('Exported to HMS-DOC successfully!')
  } catch (error) {
    console.error('Error exporting to HMS-DOC:', error)
    alert(`Error exporting to HMS-DOC: ${error}`)
  } finally {
    isLoading.value = false
  }
}

// Publish to HMS-MFE
const publishToHmsMfe = async () => {
  isLoading.value = true
  
  try {
    // This would call the backend API in a real implementation
    // For demonstration, we'll create a mock publication
    
    const newPublication = {
      publication_id: `mfe-${Date.now()}`,
      title: `Clinical Trial Publication ${new Date().toLocaleDateString()}`,
      timestamp: new Date().toISOString(),
      status: 'published',
      writer_component: '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/src/pages/sidebar/dashboards/writer.vue',
      file_path: '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE/json-server/data/publication.json'
    }
    
    // Add to mfe publications
    mfePublications.value = [newPublication, ...mfePublications.value]
    
    // Save to localStorage for persistence
    localStorage.setItem('hms_mfe_publications', JSON.stringify(mfePublications.value))
    
    // Show success message
    alert('Published to HMS-MFE successfully!')
  } catch (error) {
    console.error('Error publishing to HMS-MFE:', error)
    alert(`Error publishing to HMS-MFE: ${error}`)
  } finally {
    isLoading.value = false
  }
}

// Open a DOC publication
const openDocPublication = (publication: any) => {
  // In a real implementation, this would open the publication
  // For demonstration, we'll just show an alert
  alert(`Opening HMS-DOC publication at: ${publication.output_path}`)
}

// View DOC publication details
const viewDocDetails = (publication: any) => {
  selectedPublication.value = publication
  isModalOpen.value = true
}

// Open an MFE publication in the writer
const openMfePublication = (publication: any) => {
  // In a real implementation, this would open the writer with the publication
  // For demonstration, we'll just show an alert
  alert(`Opening HMS-MFE publication in writer: ${publication.writer_component}`)
}

// View MFE publication details
const viewMfeDetails = (publication: any) => {
  selectedPublication.value = publication
  isModalOpen.value = true
}

// Close the modal
const closeModal = () => {
  isModalOpen.value = false
}
</script>

<style scoped>
.integration-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 20px;
  text-align: center;
}

.dashboard-header .title {
  font-size: 24px;
  margin-bottom: 8px;
}

.dashboard-header .subtitle {
  color: #666;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.card-content {
  padding: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.metric-item {
  display: flex;
  align-items: center;
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.metric-icon.active {
  background-color: #4caf50;
  color: white;
}

.metric-content {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 12px;
  color: #666;
}

.metric-value {
  font-size: 16px;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  font-weight: bold;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background-color: #4285f4;
  color: white;
}

.btn-info {
  background-color: #34a853;
  color: white;
}

.btn-success {
  background-color: #fbbc05;
  color: black;
}

.dashboard-tabs {
  margin-top: 20px;
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: bold;
  opacity: 0.7;
}

.tab-btn.active {
  opacity: 1;
  border-bottom: 2px solid #4285f4;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4285f4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.publications-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.publication-item {
  border: 1px solid #e0e0e0;
}

.pub-title {
  font-size: 18px;
  margin-bottom: 10px;
}

.pub-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 12px;
}

.pub-status {
  padding: 2px 8px;
  border-radius: 12px;
  background-color: #f0f0f0;
}

.pub-status.completed,
.pub-status.published {
  background-color: #e6f4ea;
  color: #137333;
}

.pub-path,
.pub-id {
  font-size: 12px;
  color: #666;
  margin-bottom: 15px;
  word-break: break-all;
}

.pub-actions {
  display: flex;
  gap: 10px;
}

.modal {
  display: none;
}

.modal.is-active {
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 1000;
}

.modal-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.modal-card {
  position: relative;
  background-color: white;
  border-radius: 8px;
  width: 800px;
  max-width: 90%;
  max-height: 90%;
  display: flex;
  flex-direction: column;
}

.modal-card-head {
  padding: 15px 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-card-title {
  font-size: 18px;
  font-weight: bold;
}

.delete {
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 20px;
}

.modal-card-body {
  padding: 20px;
  overflow-y: auto;
}

.modal-card-foot {
  padding: 15px 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
}

.details-section {
  margin-bottom: 20px;
}

.details-section h5 {
  font-size: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 5px;
}

.detail-item {
  display: flex;
  margin-bottom: 5px;
}

.detail-label {
  font-weight: bold;
  width: 150px;
}

.publication-json {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>