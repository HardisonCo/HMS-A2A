use std::sync::Arc;
use warp::{Filter, Rejection, Reply};
use uuid::Uuid;
use serde::{Deserialize, Serialize};
use warp::http::StatusCode;

use crate::services::{AgencyServiceTrait, InMemoryAgencyService, EntityFilters};
use crate::models::AgencyEntity;

/// Agency API Controller
/// Provides HTTP endpoints for agency entity operations
/// Customize this controller to match your agency's API requirements
pub struct AgencyController {
    service: Arc<dyn AgencyServiceTrait>,
}

/// Request for creating a new entity
#[derive(Debug, Deserialize)]
pub struct CreateEntityRequest {
    pub name: String,
    pub description: Option<String>,
    pub classification: String,
    pub status: String,
    pub metadata: Option<serde_json::Value>,
}

/// Request for updating an entity
#[derive(Debug, Deserialize)]
pub struct UpdateEntityRequest {
    pub name: Option<String>,
    pub description: Option<String>,
    pub classification: Option<String>,
    pub status: Option<String>,
    pub metadata: Option<serde_json::Value>,
}

/// Filter query parameters for listing entities
#[derive(Debug, Deserialize)]
pub struct ListEntitiesQuery {
    pub classification: Option<String>,
    pub status: Option<String>,
    pub created_after: Option<String>,
    pub created_before: Option<String>,
}

/// API response wrapper
#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
}

impl AgencyController {
    /// Creates a new instance of the controller with the provided service
    pub fn new(service: Arc<dyn AgencyServiceTrait>) -> Self {
        Self { service }
    }
    
    /// Creates a new instance with the default in-memory service
    pub fn new_with_default_service() -> Self {
        Self {
            service: Arc::new(InMemoryAgencyService::new()),
        }
    }
    
    /// Creates all routes for the agency API
    pub fn routes(&self) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {
        let service = Arc::clone(&self.service);
        let base_path = warp::path("api").and(warp::path("agency"));
        
        let get_entity = base_path
            .and(warp::path("entities"))
            .and(warp::path::param::<String>())
            .and(warp::get())
            .and_then(move |id_str: String| {
                let service = Arc::clone(&service);
                async move {
                    let id = match Uuid::parse_str(&id_str) {
                        Ok(id) => id,
                        Err(_) => return Err(warp::reject::custom(ApiError::InvalidId)),
                    };
                    
                    match service.get_entity(id).await {
                        Ok(Some(entity)) => Ok(warp::reply::json(&ApiResponse {
                            success: true,
                            data: Some(entity),
                            error: None,
                        })),
                        Ok(None) => Ok(warp::reply::with_status(
                            warp::reply::json(&ApiResponse::<()> {
                                success: false,
                                data: None,
                                error: Some(format!("Entity with ID {} not found", id)),
                            }),
                            StatusCode::NOT_FOUND,
                        )),
                        Err(e) => Ok(warp::reply::with_status(
                            warp::reply::json(&ApiResponse::<()> {
                                success: false,
                                data: None,
                                error: Some(e),
                            }),
                            StatusCode::INTERNAL_SERVER_ERROR,
                        )),
                    }
                }
            });
            
        let list_entities = base_path
            .and(warp::path("entities"))
            .and(warp::get())
            .and(warp::query::<ListEntitiesQuery>())
            .and_then(move |query: ListEntitiesQuery| {
                let service = Arc::clone(&service);
                async move {
                    let filters = EntityFilters {
                        classification: query.classification,
                        status: query.status,
                        created_after: query.created_after.and_then(|date_str| {
                            chrono::DateTime::parse_from_rfc3339(&date_str)
                                .ok()
                                .map(|dt| dt.with_timezone(&chrono::Utc))
                        }),
                        created_before: query.created_before.and_then(|date_str| {
                            chrono::DateTime::parse_from_rfc3339(&date_str)
                                .ok()
                                .map(|dt| dt.with_timezone(&chrono::Utc))
                        }),
                    };
                    
                    match service.list_entities(Some(filters)).await {
                        Ok(entities) => Ok(warp::reply::json(&ApiResponse {
                            success: true,
                            data: Some(entities),
                            error: None,
                        })),
                        Err(e) => Ok(warp::reply::with_status(
                            warp::reply::json(&ApiResponse::<()> {
                                success: false,
                                data: None,
                                error: Some(e),
                            }),
                            StatusCode::INTERNAL_SERVER_ERROR,
                        )),
                    }
                }
            });
            
        // Other route handlers for create, update, delete, process, etc.
        // Add agency-specific endpoints here
        
        // Combine all routes
        get_entity.or(list_entities)
        
        // Add more routes here as needed
    }
}

/// Custom API errors
#[derive(Debug)]
pub enum ApiError {
    InvalidId,
    ValidationError(String),
    NotFound,
    InternalError(String),
}

impl warp::reject::Reject for ApiError {}

/// Converts a CreateEntityRequest to an AgencyEntity
impl From<CreateEntityRequest> for AgencyEntity {
    fn from(req: CreateEntityRequest) -> Self {
        let now = chrono::Utc::now();
        Self {
            id: Uuid::new_v4(),
            name: req.name,
            description: req.description,
            classification: req.classification,
            status: req.status,
            metadata: req.metadata.unwrap_or_else(|| serde_json::json!({})),
            created_at: now,
            updated_at: now,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use warp::test::request;
    
    #[tokio::test]
    async fn test_get_entity_endpoint() {
        let service = Arc::new(InMemoryAgencyService::new());
        
        // Create a test entity
        let entity = AgencyEntity::new(
            "Test Entity".to_string(),
            "Test Classification".to_string(),
            "Active".to_string(),
        );
        
        let id = entity.id;
        service.create_entity(entity).await.unwrap();
        
        // Create the controller with our test service
        let controller = AgencyController::new(service);
        
        // Test the GET endpoint
        let response = request()
            .method("GET")
            .path(&format!("/api/agency/entities/{}", id))
            .reply(&controller.routes())
            .await;
        
        assert_eq!(response.status(), 200);
        
        // Deserialize and check the response
        let response_body: ApiResponse<AgencyEntity> = serde_json::from_slice(response.body()).unwrap();
        assert!(response_body.success);
        assert!(response_body.data.is_some());
        
        let returned_entity = response_body.data.unwrap();
        assert_eq!(returned_entity.id, id);
        assert_eq!(returned_entity.name, "Test Entity");
    }
}