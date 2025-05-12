use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

/// AgencyEntity represents a core entity within an agency
/// Customize this model to represent your agency's primary data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgencyEntity {
    /// Unique identifier for the entity
    #[serde(default = "Uuid::new_v4")]
    pub id: Uuid,
    
    /// The name or title of the entity
    pub name: String,
    
    /// Description of the entity
    #[serde(default)]
    pub description: Option<String>,
    
    /// Classification or category of the entity
    /// Customize with enum specific to your agency
    pub classification: String,
    
    /// Status of the entity
    /// Customize with enum specific to your agency
    pub status: String,
    
    /// Metadata and additional properties
    /// Add agency-specific fields as needed
    #[serde(default)]
    pub metadata: serde_json::Value,
    
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    
    /// Last updated timestamp
    pub updated_at: DateTime<Utc>,
}

impl AgencyEntity {
    /// Creates a new AgencyEntity with default timestamps
    pub fn new(name: String, classification: String, status: String) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name,
            description: None,
            classification,
            status,
            metadata: serde_json::Value::Object(serde_json::Map::new()),
            created_at: now,
            updated_at: now,
        }
    }
    
    /// Updates the entity and sets the updated_at time
    pub fn update(&mut self) {
        self.updated_at = Utc::now();
    }
    
    /// Validates that the entity meets agency-specific requirements
    /// Customize this method to implement your agency's validation logic
    pub fn validate(&self) -> Result<(), String> {
        // Example validation logic - replace with agency-specific validation
        if self.name.is_empty() {
            return Err("Entity name cannot be empty".to_string());
        }
        
        // Add your agency-specific validation rules here
        
        Ok(())
    }
}

/// Implementation of From trait for converting to API response format
impl From<AgencyEntity> for serde_json::Value {
    fn from(entity: AgencyEntity) -> Self {
        serde_json::json!({
            "id": entity.id.to_string(),
            "name": entity.name,
            "description": entity.description,
            "classification": entity.classification,
            "status": entity.status,
            "metadata": entity.metadata,
            "createdAt": entity.created_at,
            "updatedAt": entity.updated_at,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_agency_entity() {
        let entity = AgencyEntity::new(
            "Test Entity".to_string(),
            "Test Classification".to_string(),
            "Active".to_string(),
        );
        
        assert_eq!(entity.name, "Test Entity");
        assert_eq!(entity.classification, "Test Classification");
        assert_eq!(entity.status, "Active");
        assert!(entity.description.is_none());
    }
    
    #[test]
    fn test_validate_entity() {
        let entity = AgencyEntity::new(
            "Test Entity".to_string(),
            "Test Classification".to_string(),
            "Active".to_string(),
        );
        
        assert!(entity.validate().is_ok());
        
        let invalid_entity = AgencyEntity::new(
            "".to_string(),
            "Test Classification".to_string(),
            "Active".to_string(),
        );
        
        assert!(invalid_entity.validate().is_err());
    }
}