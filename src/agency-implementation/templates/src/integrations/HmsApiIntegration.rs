use async_trait::async_trait;
use reqwest::{Client, StatusCode};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::time::Duration;

/// Integration with HMS-API component
/// This provides standardized communication with the central HMS API
/// Customize this integration based on your agency's specific requirements
pub struct HmsApiIntegration {
    client: Client,
    base_url: String,
    api_key: String,
}

/// Response from HMS API operations
#[derive(Debug, Deserialize)]
pub struct HmsApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
}

/// Authentication tokens received from HMS API
#[derive(Debug, Deserialize)]
pub struct AuthTokens {
    pub access_token: String,
    pub refresh_token: String,
    pub expires_in: u64,
}

/// Agency registration data
#[derive(Debug, Serialize)]
pub struct AgencyRegistration {
    pub agency_code: String,
    pub agency_name: String,
    pub contact_email: String,
    pub api_version: String,
    pub features: Vec<String>,
}

/// Agency status update
#[derive(Debug, Serialize)]
pub struct AgencyStatusUpdate {
    pub agency_code: String,
    pub status: String,
    pub message: Option<String>,
    pub metrics: Option<serde_json::Value>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Service discovery response
#[derive(Debug, Deserialize)]
pub struct ServiceDiscovery {
    pub services: Vec<ServiceInfo>,
}

/// Service information
#[derive(Debug, Deserialize)]
pub struct ServiceInfo {
    pub name: String,
    pub url: String,
    pub version: String,
    pub status: String,
}

/// Agency notification
#[derive(Debug, Serialize)]
pub struct AgencyNotification {
    pub agency_code: String,
    pub event_type: String,
    pub severity: String,
    pub message: String,
    pub data: Option<serde_json::Value>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// HMS API integration trait
/// Defines the standard interface for HMS API communication
#[async_trait]
pub trait HmsApiIntegrationTrait: Send + Sync {
    /// Authenticates with HMS API and retrieves access tokens
    async fn authenticate(&self) -> Result<AuthTokens, String>;
    
    /// Registers this agency with HMS API
    async fn register_agency(&self, registration: AgencyRegistration) -> Result<bool, String>;
    
    /// Updates agency status in HMS API
    async fn update_status(&self, status_update: AgencyStatusUpdate) -> Result<bool, String>;
    
    /// Discovers available HMS services
    async fn discover_services(&self) -> Result<ServiceDiscovery, String>;
    
    /// Sends a notification to HMS API
    async fn send_notification(&self, notification: AgencyNotification) -> Result<bool, String>;
    
    /// Fetches configuration from HMS API
    async fn fetch_configuration(&self) -> Result<serde_json::Value, String>;
}

impl HmsApiIntegration {
    /// Creates a new instance of the HMS API integration
    pub fn new(base_url: String, api_key: String) -> Result<Self, String> {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .build()
            .map_err(|e| format!("Failed to create HTTP client: {}", e))?;
            
        Ok(Self {
            client,
            base_url,
            api_key,
        })
    }
    
    /// Creates a new instance for testing with mock values
    #[cfg(test)]
    pub fn new_mock() -> Self {
        Self {
            client: Client::new(),
            base_url: "https://api.example.com".to_string(),
            api_key: "test-api-key".to_string(),
        }
    }
}

#[async_trait]
impl HmsApiIntegrationTrait for HmsApiIntegration {
    async fn authenticate(&self) -> Result<AuthTokens, String> {
        let url = format!("{}/auth/token", self.base_url);
        
        let response = self.client
            .post(&url)
            .header("x-api-key", &self.api_key)
            .send()
            .await
            .map_err(|e| format!("Authentication request failed: {}", e))?;
            
        match response.status() {
            StatusCode::OK => {
                let auth_response: HmsApiResponse<AuthTokens> = response
                    .json()
                    .await
                    .map_err(|e| format!("Failed to parse authentication response: {}", e))?;
                    
                match auth_response.data {
                    Some(tokens) => Ok(tokens),
                    None => Err("Authentication response contained no token data".to_string()),
                }
            },
            StatusCode::UNAUTHORIZED => {
                Err("Invalid API key".to_string())
            },
            _ => {
                Err(format!("Authentication failed with status: {}", response.status()))
            }
        }
    }
    
    async fn register_agency(&self, registration: AgencyRegistration) -> Result<bool, String> {
        let tokens = self.authenticate().await?;
        let url = format!("{}/agencies/register", self.base_url);
        
        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", tokens.access_token))
            .json(&registration)
            .send()
            .await
            .map_err(|e| format!("Agency registration request failed: {}", e))?;
            
        match response.status() {
            StatusCode::OK | StatusCode::CREATED => {
                let register_response: HmsApiResponse<serde_json::Value> = response
                    .json()
                    .await
                    .map_err(|e| format!("Failed to parse registration response: {}", e))?;
                    
                Ok(register_response.success)
            },
            _ => {
                let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
                Err(format!("Registration failed with status {}: {}", response.status(), error_text))
            }
        }
    }
    
    async fn update_status(&self, status_update: AgencyStatusUpdate) -> Result<bool, String> {
        let tokens = self.authenticate().await?;
        let url = format!("{}/agencies/{}/status", self.base_url, status_update.agency_code);
        
        let response = self.client
            .put(&url)
            .header("Authorization", format!("Bearer {}", tokens.access_token))
            .json(&status_update)
            .send()
            .await
            .map_err(|e| format!("Status update request failed: {}", e))?;
            
        match response.status() {
            StatusCode::OK => {
                let update_response: HmsApiResponse<serde_json::Value> = response
                    .json()
                    .await
                    .map_err(|e| format!("Failed to parse status update response: {}", e))?;
                    
                Ok(update_response.success)
            },
            _ => {
                let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
                Err(format!("Status update failed with status {}: {}", response.status(), error_text))
            }
        }
    }
    
    async fn discover_services(&self) -> Result<ServiceDiscovery, String> {
        let tokens = self.authenticate().await?;
        let url = format!("{}/discovery/services", self.base_url);
        
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", tokens.access_token))
            .send()
            .await
            .map_err(|e| format!("Service discovery request failed: {}", e))?;
            
        match response.status() {
            StatusCode::OK => {
                let discovery_response: HmsApiResponse<ServiceDiscovery> = response
                    .json()
                    .await
                    .map_err(|e| format!("Failed to parse service discovery response: {}", e))?;
                    
                match discovery_response.data {
                    Some(services) => Ok(services),
                    None => Err("Service discovery response contained no data".to_string()),
                }
            },
            _ => {
                let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
                Err(format!("Service discovery failed with status {}: {}", response.status(), error_text))
            }
        }
    }
    
    async fn send_notification(&self, notification: AgencyNotification) -> Result<bool, String> {
        let tokens = self.authenticate().await?;
        let url = format!("{}/notifications", self.base_url);
        
        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", tokens.access_token))
            .json(&notification)
            .send()
            .await
            .map_err(|e| format!("Notification request failed: {}", e))?;
            
        match response.status() {
            StatusCode::OK | StatusCode::CREATED => {
                let notification_response: HmsApiResponse<serde_json::Value> = response
                    .json()
                    .await
                    .map_err(|e| format!("Failed to parse notification response: {}", e))?;
                    
                Ok(notification_response.success)
            },
            _ => {
                let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
                Err(format!("Notification failed with status {}: {}", response.status(), error_text))
            }
        }
    }
    
    async fn fetch_configuration(&self) -> Result<serde_json::Value, String> {
        let tokens = self.authenticate().await?;
        let url = format!("{}/config", self.base_url);
        
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", tokens.access_token))
            .send()
            .await
            .map_err(|e| format!("Configuration fetch request failed: {}", e))?;
            
        match response.status() {
            StatusCode::OK => {
                let config_response: HmsApiResponse<serde_json::Value> = response
                    .json()
                    .await
                    .map_err(|e| format!("Failed to parse configuration response: {}", e))?;
                    
                match config_response.data {
                    Some(config) => Ok(config),
                    None => Err("Configuration response contained no data".to_string()),
                }
            },
            _ => {
                let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
                Err(format!("Configuration fetch failed with status {}: {}", response.status(), error_text))
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockito::{mock, server_url};
    
    #[tokio::test]
    async fn test_authentication() {
        let mock_server = server_url();
        
        // Mock the authentication endpoint
        let _m = mock("POST", "/auth/token")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{
                "success": true,
                "data": {
                    "access_token": "mock-access-token",
                    "refresh_token": "mock-refresh-token",
                    "expires_in": 3600
                },
                "error": null
            }"#)
            .create();
            
        let integration = HmsApiIntegration::new(
            mock_server,
            "test-api-key".to_string(),
        ).unwrap();
        
        let result = integration.authenticate().await;
        
        assert!(result.is_ok());
        let tokens = result.unwrap();
        assert_eq!(tokens.access_token, "mock-access-token");
        assert_eq!(tokens.refresh_token, "mock-refresh-token");
        assert_eq!(tokens.expires_in, 3600);
    }
    
    #[tokio::test]
    async fn test_service_discovery() {
        let mock_server = server_url();
        
        // Mock the authentication endpoint
        let _auth_mock = mock("POST", "/auth/token")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{
                "success": true,
                "data": {
                    "access_token": "mock-access-token",
                    "refresh_token": "mock-refresh-token",
                    "expires_in": 3600
                },
                "error": null
            }"#)
            .create();
            
        // Mock the service discovery endpoint
        let _discovery_mock = mock("GET", "/discovery/services")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{
                "success": true,
                "data": {
                    "services": [
                        {
                            "name": "HMS-API",
                            "url": "https://api.example.com",
                            "version": "1.0.0",
                            "status": "active"
                        },
                        {
                            "name": "HMS-CDF",
                            "url": "https://cdf.example.com",
                            "version": "1.0.0",
                            "status": "active"
                        }
                    ]
                },
                "error": null
            }"#)
            .create();
            
        let integration = HmsApiIntegration::new(
            mock_server,
            "test-api-key".to_string(),
        ).unwrap();
        
        let result = integration.discover_services().await;
        
        assert!(result.is_ok());
        let discovery = result.unwrap();
        assert_eq!(discovery.services.len(), 2);
        assert_eq!(discovery.services[0].name, "HMS-API");
        assert_eq!(discovery.services[1].name, "HMS-CDF");
    }
}