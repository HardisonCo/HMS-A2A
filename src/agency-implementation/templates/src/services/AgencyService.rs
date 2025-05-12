use std::sync::Arc;
use async_trait::async_trait;
use tokio::sync::RwLock;
use uuid::Uuid;
use crate::models::AgencyEntity;

/// Defines the interface for agency entity operations
/// This trait can be implemented by different service providers
#[async_trait]
pub trait AgencyServiceTrait: Send + Sync {
    /// Retrieves an agency entity by ID
    async fn get_entity(&self, id: Uuid) -> Result<Option<AgencyEntity>, String>;
    
    /// Lists all entities matching optional filters
    async fn list_entities(&self, filters: Option<EntityFilters>) -> Result<Vec<AgencyEntity>, String>;
    
    /// Creates a new entity
    async fn create_entity(&self, entity: AgencyEntity) -> Result<AgencyEntity, String>;
    
    /// Updates an existing entity
    async fn update_entity(&self, id: Uuid, entity: AgencyEntity) -> Result<AgencyEntity, String>;
    
    /// Deletes an entity by ID
    async fn delete_entity(&self, id: Uuid) -> Result<bool, String>;
    
    /// Processes an entity according to agency-specific rules
    /// Customize this method to implement your agency's processing logic
    async fn process_entity(&self, id: Uuid) -> Result<ProcessingResult, String>;
}

/// Filter options for listing entities
/// Customize this struct to include agency-specific filtering options
#[derive(Debug, Clone, Default)]
pub struct EntityFilters {
    pub classification: Option<String>,
    pub status: Option<String>,
    pub created_after: Option<chrono::DateTime<chrono::Utc>>,
    pub created_before: Option<chrono::DateTime<chrono::Utc>>,
    
    // Add agency-specific filters here
}

/// Result of entity processing
/// Customize this struct to represent your agency's processing outcomes
#[derive(Debug, Clone)]
pub struct ProcessingResult {
    pub entity_id: Uuid,
    pub success: bool,
    pub status: String,
    pub message: Option<String>,
    pub result_data: Option<serde_json::Value>,
    pub processed_at: chrono::DateTime<chrono::Utc>,
}

/// Implementation of AgencyServiceTrait using in-memory storage
/// This is a simple example implementation that can be replaced with actual database or API integration
pub struct InMemoryAgencyService {
    entities: Arc<RwLock<Vec<AgencyEntity>>>,
}

impl InMemoryAgencyService {
    /// Creates a new instance of the in-memory agency service
    pub fn new() -> Self {
        Self {
            entities: Arc::new(RwLock::new(Vec::new())),
        }
    }
}

#[async_trait]
impl AgencyServiceTrait for InMemoryAgencyService {
    async fn get_entity(&self, id: Uuid) -> Result<Option<AgencyEntity>, String> {
        let entities = self.entities.read().await;
        Ok(entities.iter().find(|e| e.id == id).cloned())
    }
    
    async fn list_entities(&self, filters: Option<EntityFilters>) -> Result<Vec<AgencyEntity>, String> {
        let entities = self.entities.read().await;
        
        if let Some(filters) = filters {
            let mut filtered = entities.clone();
            
            // Apply filters
            if let Some(classification) = filters.classification {
                filtered.retain(|e| e.classification == classification);
            }
            
            if let Some(status) = filters.status {
                filtered.retain(|e| e.status == status);
            }
            
            if let Some(created_after) = filters.created_after {
                filtered.retain(|e| e.created_at >= created_after);
            }
            
            if let Some(created_before) = filters.created_before {
                filtered.retain(|e| e.created_at <= created_before);
            }
            
            // Add additional agency-specific filtering here
            
            Ok(filtered)
        } else {
            Ok(entities.clone())
        }
    }
    
    async fn create_entity(&self, entity: AgencyEntity) -> Result<AgencyEntity, String> {
        // Validate the entity
        entity.validate()?;
        
        let mut entities = self.entities.write().await;
        entities.push(entity.clone());
        Ok(entity)
    }
    
    async fn update_entity(&self, id: Uuid, updated_entity: AgencyEntity) -> Result<AgencyEntity, String> {
        // Validate the entity
        updated_entity.validate()?;
        
        let mut entities = self.entities.write().await;
        
        if let Some(index) = entities.iter().position(|e| e.id == id) {
            // Ensure the ID matches
            let mut entity_to_update = updated_entity;
            entity_to_update.id = id;
            entity_to_update.update();
            
            entities[index] = entity_to_update.clone();
            Ok(entity_to_update)
        } else {
            Err(format!("Entity with ID {} not found", id))
        }
    }
    
    async fn delete_entity(&self, id: Uuid) -> Result<bool, String> {
        let mut entities = self.entities.write().await;
        
        if let Some(index) = entities.iter().position(|e| e.id == id) {
            entities.remove(index);
            Ok(true)
        } else {
            Ok(false)
        }
    }
    
    async fn process_entity(&self, id: Uuid) -> Result<ProcessingResult, String> {
        // Get the entity
        let entity = match self.get_entity(id).await? {
            Some(e) => e,
            None => return Err(format!("Entity with ID {} not found", id)),
        };
        
        // This is where you would implement your agency-specific processing logic
        // Example implementation - replace with actual processing logic
        
        // Update the entity status after processing
        let mut updated_entity = entity.clone();
        updated_entity.status = "Processed".to_string();
        updated_entity.update();
        
        self.update_entity(id, updated_entity).await?;
        
        // Return processing result
        Ok(ProcessingResult {
            entity_id: id,
            success: true,
            status: "Processed".to_string(),
            message: Some("Entity successfully processed".to_string()),
            result_data: Some(serde_json::json!({ "processedData": "Example processed data" })),
            processed_at: chrono::Utc::now(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    async fn setup_test_service() -> InMemoryAgencyService {
        InMemoryAgencyService::new()
    }
    
    #[tokio::test]
    async fn test_create_and_get_entity() {
        let service = setup_test_service().await;
        
        let entity = AgencyEntity::new(
            "Test Entity".to_string(),
            "Test Classification".to_string(),
            "Active".to_string(),
        );
        
        let id = entity.id;
        let created = service.create_entity(entity).await.unwrap();
        
        assert_eq!(created.id, id);
        
        let retrieved = service.get_entity(id).await.unwrap().unwrap();
        assert_eq!(retrieved.id, id);
        assert_eq!(retrieved.name, "Test Entity");
    }
    
    #[tokio::test]
    async fn test_list_entities_with_filters() {
        let service = setup_test_service().await;
        
        // Create test entities
        for i in 0..5 {
            let classification = if i % 2 == 0 { "Type A" } else { "Type B" };
            let entity = AgencyEntity::new(
                format!("Entity {}", i),
                classification.to_string(),
                "Active".to_string(),
            );
            service.create_entity(entity).await.unwrap();
        }
        
        // Test listing all entities
        let all_entities = service.list_entities(None).await.unwrap();
        assert_eq!(all_entities.len(), 5);
        
        // Test filtering by classification
        let filters = EntityFilters {
            classification: Some("Type A".to_string()),
            ..Default::default()
        };
        
        let filtered_entities = service.list_entities(Some(filters)).await.unwrap();
        assert_eq!(filtered_entities.len(), 3);
        assert!(filtered_entities.iter().all(|e| e.classification == "Type A"));
    }
    
    #[tokio::test]
    async fn test_process_entity() {
        let service = setup_test_service().await;
        
        let entity = AgencyEntity::new(
            "Entity for Processing".to_string(),
            "Process Test".to_string(),
            "Pending".to_string(),
        );
        
        let id = entity.id;
        service.create_entity(entity).await.unwrap();
        
        let result = service.process_entity(id).await.unwrap();
        
        assert!(result.success);
        assert_eq!(result.entity_id, id);
        
        let processed_entity = service.get_entity(id).await.unwrap().unwrap();
        assert_eq!(processed_entity.status, "Processed");
    }
}