use std::sync::Arc;
use std::env;
use warp::Filter;
use tokio::signal::ctrl_c;

// Import agency modules
mod models;
mod services;
mod api;
mod integrations;

use crate::api::AgencyController;
use crate::services::InMemoryAgencyService;
use crate::integrations::HmsApiIntegration;

/// Main entry point for the agency application
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logging
    env_logger::init();
    
    // Load configuration
    let config = load_configuration()?;
    log::info!("Agency configuration loaded: {}", config.agency_name);
    
    // Initialize the service
    let service = Arc::new(InMemoryAgencyService::new());
    log::info!("Agency service initialized");
    
    // Initialize HMS API integration
    let hms_api_integration = HmsApiIntegration::new(
        config.hms_api_url.clone(),
        config.api_key.clone(),
    )?;
    log::info!("HMS API integration initialized");
    
    // Register the agency with HMS API
    register_agency(&hms_api_integration, &config).await?;
    log::info!("Agency registered with HMS API");
    
    // Initialize API controller
    let controller = AgencyController::new(service);
    let routes = controller.routes();
    log::info!("Agency controller initialized");
    
    // Start the server
    let port = config.port;
    log::info!("Starting agency server on port {}", port);
    
    let (addr, server) = warp::serve(routes)
        .bind_with_graceful_shutdown(([0, 0, 0, 0], port), async {
            // Listen for Ctrl+C
            ctrl_c().await.expect("Failed to listen for ctrl-c");
            log::info!("Shutdown signal received, stopping server...");
        });
    
    log::info!("Agency server listening on {}", addr);
    
    // Start the server in a separate task
    tokio::spawn(server);
    
    // Keep the main task alive
    tokio::signal::ctrl_c().await?;
    log::info!("Agency server shutting down...");
    
    Ok(())
}

/// Agency configuration
struct AgencyConfig {
    agency_code: String,
    agency_name: String,
    port: u16,
    hms_api_url: String,
    api_key: String,
}

/// Loads agency configuration from environment or configuration file
fn load_configuration() -> Result<AgencyConfig, Box<dyn std::error::Error>> {
    // Load configuration from environment variables or config file
    // This is a simple example - replace with your agency's configuration loading logic
    
    let agency_code = env::var("AGENCY_CODE").unwrap_or_else(|_| "AGENCY".to_string());
    let agency_name = env::var("AGENCY_NAME").unwrap_or_else(|_| "Agency Name".to_string());
    let port = env::var("PORT")
        .unwrap_or_else(|_| "3000".to_string())
        .parse::<u16>()?;
    let hms_api_url = env::var("HMS_API_URL")
        .unwrap_or_else(|_| "https://api.hms.example.com".to_string());
    let api_key = env::var("API_KEY")
        .unwrap_or_else(|_| "default-api-key".to_string());
    
    Ok(AgencyConfig {
        agency_code,
        agency_name,
        port,
        hms_api_url,
        api_key,
    })
}

/// Registers the agency with HMS API
async fn register_agency(
    integration: &HmsApiIntegration,
    config: &AgencyConfig,
) -> Result<(), Box<dyn std::error::Error>> {
    // Create registration request
    let registration = integrations::AgencyRegistration {
        agency_code: config.agency_code.clone(),
        agency_name: config.agency_name.clone(),
        contact_email: env::var("CONTACT_EMAIL").unwrap_or_else(|_| "contact@example.com".to_string()),
        api_version: env!("CARGO_PKG_VERSION").to_string(),
        features: vec!["basic".to_string(), "notifications".to_string()],
    };
    
    // Register agency
    match integration.register_agency(registration).await {
        Ok(true) => {
            log::info!("Agency successfully registered with HMS API");
            Ok(())
        }
        Ok(false) => {
            log::warn!("Agency registration returned false");
            Err("Agency registration failed".into())
        }
        Err(e) => {
            log::error!("Agency registration error: {}", e);
            Err(e.into())
        }
    }
}