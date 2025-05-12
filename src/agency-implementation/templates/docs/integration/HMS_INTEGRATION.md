# HMS Integration Guide

This guide provides detailed instructions for integrating your agency implementation with the HMS system components.

## Table of Contents

1. [Overview](#overview)
2. [Integration with HMS-API](#integration-with-hms-api)
3. [Integration with HMS-CDF](#integration-with-hms-cdf)
4. [Integration with HMS-DTA](#integration-with-hms-dta)
5. [Self-Healing Integration](#self-healing-integration)
6. [Deployment Integration](#deployment-integration)
7. [Monitoring Integration](#monitoring-integration)
8. [Troubleshooting](#troubleshooting)

## Overview

Each agency implementation must integrate with the broader HMS ecosystem. The primary integration points are:

1. **HMS-API**: Central API gateway for all HMS components
2. **HMS-CDF**: Collaborative Decision Framework for policy management
3. **HMS-DTA**: Data acquisition and transformation
4. **Self-Healing System**: Automatic issue detection and resolution
5. **Monitoring System**: Health monitoring and metrics

## Integration with HMS-API

HMS-API is the central API gateway and the primary integration point for all agency implementations.

### Registration

Your agency must register with HMS-API on startup:

```rust
let registration = AgencyRegistration {
    agency_code: config.agency_code.clone(),
    agency_name: config.agency_name.clone(),
    contact_email: "contact@example.com".to_string(),
    api_version: "1.0.0".to_string(),
    features: vec!["basic".to_string()],
};

hms_api_integration.register_agency(registration).await?;
```

### Authentication

All requests to HMS-API must be authenticated:

```rust
let tokens = hms_api_integration.authenticate().await?;
```

### Service Discovery

Discover other HMS services using the discovery endpoint:

```rust
let services = hms_api_integration.discover_services().await?;
```

### Status Updates

Regularly update your agency's status:

```rust
let status_update = AgencyStatusUpdate {
    agency_code: config.agency_code.clone(),
    status: "active".to_string(),
    message: Some("Agency running normally".to_string()),
    metrics: Some(serde_json::json!({ "requests": 100, "errors": 0 })),
    timestamp: chrono::Utc::now(),
};

hms_api_integration.update_status(status_update).await?;
```

### Event Subscriptions

Subscribe to relevant events:

```rust
// In your configuration
"eventSubscriptions": [
    "system.status",
    "policy.update"
]
```

Implement an event handler in your agency to process these events.

## Integration with HMS-CDF

The HMS-CDF component provides the Collaborative Decision Framework for policy management.

### Policy Access

Access policies relevant to your agency:

```rust
let hms_cdf_integration = HmsCdfIntegration::new(
    config.hms_cdf_url.clone(),
    tokens.access_token.clone(),
)?;

let policies = hms_cdf_integration.list_policies(Some("your-agency-domain")).await?;
```

### Debate Participation

Participate in policy debates:

```rust
let debate_comment = DebateComment {
    policy_id: policy_id,
    comment: "Agency perspective on this policy...".to_string(),
    position: "support".to_string(),
    evidence: Some(serde_json::json!({ "data": "Supporting evidence..." })),
};

hms_cdf_integration.add_debate_comment(debate_comment).await?;
```

### Vote Submission

Submit votes on policies:

```rust
let vote = PolicyVote {
    policy_id: policy_id,
    vote: "approve".to_string(),
    justification: "This policy aligns with agency goals...".to_string(),
};

hms_cdf_integration.submit_vote(vote).await?;
```

## Integration with HMS-DTA

The HMS-DTA component provides data acquisition and transformation services.

### Data Acquisition

Request data relevant to your agency:

```rust
let hms_dta_integration = HmsDtaIntegration::new(
    config.hms_dta_url.clone(),
    tokens.access_token.clone(),
)?;

let data_request = DataRequest {
    data_type: "your-data-type".to_string(),
    parameters: serde_json::json!({ "filter": "your-filter" }),
};

let data = hms_dta_integration.request_data(data_request).await?;
```

### Data Transformation

Request data transformations:

```rust
let transform_request = TransformRequest {
    data: raw_data,
    transformation: "your-transformation".to_string(),
    parameters: serde_json::json!({ "option": "value" }),
};

let transformed_data = hms_dta_integration.transform_data(transform_request).await?;
```

## Self-Healing Integration

The Self-Healing System enables automatic issue detection and resolution.

### Health Monitoring

Expose a health check endpoint:

```rust
let health_check = warp::path("health")
    .and(warp::get())
    .map(|| {
        warp::reply::json(&serde_json::json!({
            "status": "healthy",
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "version": env!("CARGO_PKG_VERSION")
        }))
    });
```

### Issue Reporting

Report issues to the Self-Healing System:

```rust
let issue_report = IssueReport {
    agency_code: config.agency_code.clone(),
    issue_type: "connection_error".to_string(),
    severity: "high".to_string(),
    description: "Unable to connect to external service".to_string(),
    context: serde_json::json!({ "service": "external-api", "attempts": 3 }),
    timestamp: chrono::Utc::now(),
};

self_healing_integration.report_issue(issue_report).await?;
```

### Circuit Breaker Integration

Implement circuit breakers for external dependencies:

```rust
let circuit_breaker = CircuitBreaker::new(
    "external-service".to_string(),
    CircuitBreakerConfig {
        failure_threshold: 5,
        reset_timeout: Duration::from_secs(30),
    },
);

// Use the circuit breaker
if circuit_breaker.is_closed().await {
    match external_service_call().await {
        Ok(result) => {
            circuit_breaker.report_success().await;
            Ok(result)
        }
        Err(e) => {
            circuit_breaker.report_failure().await;
            Err(e)
        }
    }
} else {
    Err("Circuit breaker open, skipping call".to_string())
}
```

## Deployment Integration

### Container Configuration

Your agency implementation should be containerized with the following:

```dockerfile
FROM rust:1.68 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bullseye-slim
COPY --from=builder /app/target/release/hms-agency /usr/local/bin/
EXPOSE 3000
CMD ["hms-agency"]
```

### Environment Variables

Provide the required environment variables:

```
AGENCY_CODE=YOUR_AGENCY_CODE
AGENCY_NAME=Your Agency Name
HMS_API_URL=https://api.hms.example.com
API_KEY=your-api-key
HMS_CDF_URL=https://cdf.hms.example.com
HMS_DTA_URL=https://dta.hms.example.com
SELF_HEALING_URL=https://healing.hms.example.com
MONITORING_URL=https://monitoring.hms.example.com
```

## Monitoring Integration

### Metrics Exposure

Expose metrics for monitoring:

```rust
let metrics_endpoint = warp::path("metrics")
    .and(warp::get())
    .map(|| {
        let metrics = collect_metrics();
        warp::reply::json(&metrics)
    });
```

### Logging Integration

Configure structured logging:

```rust
// Initialize logging with JSON format
let env = env_logger::Env::default()
    .filter_or("LOG_LEVEL", "info");
    
env_logger::Builder::from_env(env)
    .format(|buf, record| {
        let timestamp = chrono::Utc::now().to_rfc3339();
        let level = record.level();
        let target = record.target();
        let args = record.args();
        
        writeln!(
            buf,
            r#"{{"timestamp":"{timestamp}","level":"{level}","target":"{target}","message":"{args}"}}"#
        )
    })
    .init();
```

## Troubleshooting

### Common Integration Issues

1. **Authentication Failures**
   - Verify your API key is correct
   - Check token expiration
   - Ensure proper authorization headers

2. **Connection Issues**
   - Verify service URLs
   - Check network connectivity
   - Check firewall rules

3. **Data Format Issues**
   - Ensure request/response formats match the API specifications
   - Validate all data before sending

### Support Contacts

For integration support, contact:

- HMS-API Team: api-support@hms.example.com
- HMS-CDF Team: cdf-support@hms.example.com
- HMS-DTA Team: dta-support@hms.example.com
- Self-Healing Team: healing-support@hms.example.com
- HMS Support (general): support@hms.example.com