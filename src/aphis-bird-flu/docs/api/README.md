# APHIS Bird Flu Tracking System: API Documentation

This document provides information about the APHIS Bird Flu Tracking System API endpoints, request/response formats, and usage examples.

## API Overview

The APHIS Bird Flu Tracking System exposes a RESTful API for interacting with its core services. The API provides access to the following key components:

1. **Adaptive Sampling** - Optimizing surveillance resource allocation
2. **Outbreak Detection** - Early detection of potential outbreaks
3. **Predictive Modeling** - Forecasting disease spread
4. **Notification System** - Alerting stakeholders
5. **Visualization Services** - Generating maps, charts, and dashboards
6. **Genetic Analysis** - Analyzing viral genetic sequences and transmission patterns

## Base URL

```
http://<server-address>:8000/api/v1
```

## Authentication

Authentication is required for all API endpoints. The API uses JWT (JSON Web Token) authentication with the following header:

```
Authorization: Bearer <token>
```

To obtain a token, use the authentication endpoint:

```
POST /auth/token
```

Request body:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2023-06-08T12:34:56.789Z",
  "components": {
    "api": "operational",
    "database": "operational",
    "predictive_models": "operational",
    "notification_services": "operational"
  }
}
```

### Adaptive Sampling

#### Allocate Surveillance Resources

```
POST /sampling/allocate
```

Request body:
```json
{
  "strategy": "response_adaptive",
  "sites": ["site_001", "site_002", "..."],
  "parameters": {
    "exploration_rate": 0.2,
    "recent_positive_weight": 1.5
  }
}
```

Response:
```json
{
  "allocation_id": "alloc_20230608_123456",
  "timestamp": "2023-06-08T12:34:56.789Z",
  "sites": {
    "site_001": 0.85,
    "site_002": 0.64,
    "...": "..."
  },
  "strategy": "response_adaptive",
  "metadata": {
    "exploration_rate": 0.2,
    "recent_positive_weight": 1.5
  }
}
```

### Outbreak Detection

#### Analyze Surveillance Data

```
POST /detection/analyze
```

Request body:
```json
{
  "methods": ["sprt", "group_sequential", "cusum", "spatial_scan"],
  "start_date": "2023-05-01T00:00:00Z",
  "end_date": "2023-06-01T00:00:00Z",
  "parameters": {
    "significance_level": 0.05,
    "cluster_size_limit": 50
  }
}
```

Response:
```json
{
  "analysis_id": "detect_20230608_123456",
  "timestamp": "2023-06-08T12:34:56.789Z",
  "signals": [
    {
      "region_id": "region_001",
      "signal_strength": 0.87,
      "p_value": 0.003,
      "detected_by": "group_sequential",
      "is_significant": true
    },
    "..."
  ],
  "clusters": [
    {
      "center": {"latitude": 40.7128, "longitude": -74.0060},
      "radius_km": 50.2,
      "case_count": 12,
      "p_value": 0.008,
      "regions": ["region_001", "region_002", "region_003"]
    },
    "..."
  ]
}
```

### Predictive Modeling

#### Generate Forecast

```
POST /prediction/forecast
```

Request body:
```json
{
  "days_ahead": 7,
  "models": ["distance_based", "network_based", "gaussian_process"],
  "use_ensemble": true,
  "parameters": {
    "environmental_factors": true,
    "migration_patterns": true
  }
}
```

Response:
```json
{
  "forecast_id": "forecast_20230608_123456",
  "timestamp": "2023-06-08T12:34:56.789Z",
  "days_ahead": 7,
  "regions": {
    "region_001": {
      "risk_score": 0.92,
      "predicted_cases": 8.5,
      "confidence_interval": [4.2, 12.8]
    },
    "...": "..."
  },
  "high_risk_regions": ["region_001", "region_005", "region_008"],
  "model_info": {
    "model": "ensemble",
    "components": ["distance_based", "network_based", "gaussian_process"]
  }
}
```

### Notification System

#### Send Outbreak Alert

```
POST /notifications/outbreak-alert
```

Request body:
```json
{
  "regions": [
    {"id": "region_001", "name": "King County, WA"},
    {"id": "region_002", "name": "Pierce County, WA"}
  ],
  "detection_time": "2023-06-08T09:30:00Z",
  "severity_level": "high",
  "details": {
    "virus_strain": "H5N1",
    "farm_type": "Commercial Poultry",
    "affected_birds": 25000
  }
}
```

Response:
```json
{
  "success": true,
  "timestamp": "2023-06-08T12:34:56.789Z",
  "channel_results": {
    "email": true,
    "sms": true,
    "webhook": true
  },
  "notification_id": "notification_20230608_123456"
}
```

#### Send Risk Prediction Alert

```
POST /notifications/risk-prediction-alert
```

Request body:
```json
{
  "high_risk_regions": [
    {
      "id": "region_003", 
      "name": "Skagit County, WA",
      "risk_score": 0.85,
      "predicted_cases": 3.2
    },
    {
      "id": "region_004",
      "name": "Whatcom County, WA",
      "risk_score": 0.78,
      "predicted_cases": 2.7
    }
  ],
  "forecast_date": "2023-06-08",
  "days_ahead": 7,
  "details": {
    "model_used": "ensemble",
    "confidence_level": "high"
  }
}
```

Response:
```json
{
  "success": true,
  "timestamp": "2023-06-08T12:34:56.789Z",
  "channel_results": {
    "email": true,
    "sms": true,
    "webhook": true
  },
  "notification_id": "notification_20230608_234567"
}
```

### Genetic Analysis

#### Analyze Genetic Sequence

```
POST /api/v1/genetic/sequences/analyze
```

Request body:
```json
{
  "sequence": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGCAAACAACTCGACAGAGCAGGTTGACACAATAATGGAAAAGAACGTTACTGTTACACATGCCCAAGACATACTGGAAAAGACACACA",
  "subtype": "H5N1",
  "gene": "HA"
}
```

Response:
```json
{
  "sequence_length": 1254,
  "subtype": "H5N1",
  "gene": "HA",
  "mutations": [
    {
      "position": 123,
      "reference": "A",
      "alternate": "T",
      "mutation": "A123T",
      "gene": "HA",
      "significance": {
        "phenotype": "increased virulence",
        "drug_resistance": false,
        "transmission": "increased",
        "severity": "moderate",
        "first_detected": "2022-05-15",
        "literature_refs": ["PMID:12345678"]
      }
    },
    "..."
  ],
  "lineage": {
    "lineage": "clade_2.3.4.4b",
    "confidence": 0.85,
    "related_lineages": ["clade_2.3.4.4a", "clade_2.3.4.4c"],
    "defining_mutations": ["T96I", "G54R", "T140K", "N220K", "N94H"],
    "geographic_distribution": {
      "Eastern_Asia": 0.85,
      "Southeast_Asia": 0.65,
      "Europe": 0.45,
      "North_America": 0.35,
      "Africa": 0.20
    },
    "first_detected": "2020-03-15",
    "recent_expansion": true,
    "trend": "increasing"
  },
  "antigenic_properties": "...",
  "zoonotic_potential": "...",
  "analysis_version": "1.0"
}
```

#### Identify Mutations

```
POST /api/v1/genetic/sequences/mutations
```

Request body:
```json
{
  "sequence_data": {
    "sequence": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGCAAACAACTCGACAGAGCAGGTTGACACAATAATGGAAAAGAACGTTACTGTTACACATGCCCAAGACATACTGGAAAAGACACACA",
    "subtype": "H5N1",
    "gene": "HA"
  }
}
```

Response:
```json
[
  {
    "position": 123,
    "reference": "A",
    "alternate": "T",
    "mutation": "A123T",
    "gene": "HA",
    "significance": {
      "phenotype": "increased virulence",
      "drug_resistance": false,
      "transmission": "increased",
      "severity": "moderate",
      "first_detected": "2022-05-15",
      "literature_refs": ["PMID:12345678"]
    }
  },
  "..."
]
```

#### Build Phylogenetic Tree

```
POST /api/v1/genetic/phylogenetic/tree
```

Request body:
```json
{
  "sequences": {
    "seq1": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGC",
    "seq2": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGCTACCATGC",
    "seq3": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAATTGATCAGATTTGCATTGGTTACCATGC"
  },
  "method": "upgma"
}
```

Response:
```json
{
  "method": "upgma",
  "root": {
    "id": "root",
    "children": ["seq1", "seq2", "seq3"]
  },
  "branch_lengths": {
    "root_seq1": 0.01,
    "root_seq2": 0.02,
    "seq2_seq3": 0.015
  },
  "topology": "tree_topology_data",
  "sequence_count": 3
}
```

#### Transmission Network Analysis

```
POST /api/v1/genetic/transmission/network
```

Request body:
```json
{
  "genetic_threshold": 0.05,
  "temporal_window": 30,
  "spatial_threshold": 100.0
}
```

Response:
```json
{
  "cases": 15,
  "links": [
    {
      "source": "case_001",
      "target": "case_002",
      "likelihood": 0.85,
      "days_apart": 7,
      "distance_km": 45.2,
      "genetic_distance": 0.03
    },
    "..."
  ],
  "network_metrics": {
    "node_count": 15,
    "edge_count": 12,
    "density": 0.057,
    "component_count": 2,
    "largest_component_size": 12
  },
  "clusters": [
    {
      "id": "cluster_1",
      "cases": ["case_001", "case_002", "case_003", "case_005", "case_007"],
      "metrics": {
        "size": 5,
        "edge_count": 4,
        "density": 0.27
      },
      "central_nodes": {
        "highest_in_degree": "case_002",
        "highest_betweenness": "case_001"
      }
    },
    "..."
  ],
  "index_cases": "...",
  "superspreaders": "..."
}
```

#### Assess Transmission Pattern

```
POST /api/v1/genetic/transmission/pattern
```

Request body:
```json
{
  "network": {
    "cases": 15,
    "links": [
      {
        "source": "case_001",
        "target": "case_002",
        "likelihood": 0.85,
        "days_apart": 7,
        "distance_km": 45.2,
        "genetic_distance": 0.03
      },
      "..."
    ],
    "network_metrics": "...",
    "clusters": "..."
  }
}
```

Response:
```json
{
  "pattern_type": "multiple_introductions",
  "geographic_focus": "regional",
  "temporal_pattern": "moderate",
  "transmission_intensity": "high",
  "superspreading_evidence": true,
  "intervention_recommendations": {
    "surveillance": [
      "Wild bird surveillance",
      "Import pathway monitoring",
      "Multi-jurisdictional coordination"
    ],
    "control": [
      "Border biosecurity enhancement",
      "Regional movement controls"
    ],
    "priority_level": "high"
  }
}
```

### Visualization Services

#### Generate Map

```
POST /visualizations/maps
```

Request body:
```json
{
  "map_type": "case_map",
  "start_date": "2023-05-01T00:00:00Z",
  "end_date": "2023-06-01T00:00:00Z",
  "region_level": "county",
  "title": "Avian Influenza Cases - May 2023",
  "width": 1200,
  "height": 900,
  "show_legend": true,
  "include_cases": true,
  "include_surveillance": false
}
```

Response:
```json
{
  "base64_image": "base64_encoded_image_data...",
  "case_count": 157,
  "date_range": {
    "min": "2023-05-01T00:00:00Z",
    "max": "2023-05-31T23:59:59Z"
  },
  "center": {
    "longitude": -98.5795,
    "latitude": 39.8283
  },
  "metadata": {
    "region_level": "county",
    "subtypes": ["H5N1", "H7N9", "H9N2"]
  }
}
```

#### Generate Risk Map

```
POST /visualizations/maps/risk
```

Request body:
```json
{
  "forecast_date": "2023-06-08",
  "days_ahead": 7,
  "title": "Avian Influenza Risk Forecast - Next 7 Days",
  "width": 1200,
  "height": 900,
  "show_legend": true
}
```

Response:
```json
{
  "base64_image": "base64_encoded_image_data...",
  "region_count": 58,
  "center": {
    "longitude": -98.5795,
    "latitude": 39.8283
  },
  "metadata": {
    "prediction_date": "2023-06-08",
    "days_ahead": 7,
    "risk_type": "categorical"
  }
}
```

#### Generate Chart

```
POST /visualizations/charts
```

Request body:
```json
{
  "chart_type": "case_trend",
  "days": 30,
  "title": "Avian Influenza Cases - Last 30 Days",
  "width": 800,
  "height": 500,
  "show_legend": true,
  "include_subtypes": true
}
```

Response:
```json
{
  "base64_image": "base64_encoded_image_data...",
  "total_cases": 257,
  "metadata": {
    "period_days": 30,
    "start_date": "2023-05-09",
    "end_date": "2023-06-08",
    "last_7d_cases": 43,
    "last_14d_cases": 98,
    "growth_rate": 0.25,
    "includes_subtypes": true
  }
}
```

#### Generate Dashboard

```
POST /visualizations/dashboard
```

Request body:
```json
{
  "days": 30,
  "include_charts": true,
  "include_maps": true
}
```

Response:
```json
{
  "summary": {
    "cases": {
      "total": 257,
      "last_7d": 43,
      "last_30d": 124,
      "by_subtype": {
        "H5N1": 158,
        "H7N9": 67,
        "H9N2": 32
      }
    },
    "surveillance": {
      "total_events": 1245,
      "last_7d": 112,
      "positive_rate": 0.086
    },
    "prediction": {
      "high_risk_regions": 3,
      "moderate_risk_regions": 7
    }
  },
  "charts": {
    "case_trend": {
      "base64_image": "base64_encoded_image_data...",
      "...": "..."
    },
    "subtype_distribution": {
      "base64_image": "base64_encoded_image_data...",
      "...": "..."
    }
  },
  "maps": {
    "case_map": {
      "base64_image": "base64_encoded_image_data...",
      "...": "..."
    },
    "risk_map": {
      "base64_image": "base64_encoded_image_data...",
      "...": "..."
    }
  }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request:

- **200 OK**: The request was successful
- **400 Bad Request**: The request was invalid or malformed
- **401 Unauthorized**: Authentication failed
- **403 Forbidden**: The authenticated user does not have permission to access the resource
- **404 Not Found**: The requested resource was not found
- **500 Internal Server Error**: An error occurred on the server

Error responses have the following format:

```json
{
  "error": "Detailed error message",
  "status_code": 400,
  "timestamp": "2023-06-08T12:34:56.789Z"
}
```

## Rate Limiting

API requests are subject to rate limiting to ensure the stability and performance of the system. The current rate limits are:

- **Standard endpoints**: 60 requests per minute
- **Resource-intensive endpoints** (e.g., generating visualizations): 10 requests per minute

Rate limit information is included in the response headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1623160496
```

## Pagination

For endpoints that return lists of resources, pagination is supported using the following query parameters:

- `page`: Page number (starting from 1)
- `limit`: Number of items per page (default: 20, max: 100)

Paginated responses include the following metadata:

```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 257,
    "total_pages": 13
  }
}
```

## Versioning

The API is versioned to ensure backward compatibility. The current version is `v1`, as reflected in the base URL.

## Cross-Origin Resource Sharing (CORS)

The API supports Cross-Origin Resource Sharing (CORS) for selected domains. If you need to access the API from a web application, contact the system administrator to add your domain to the allowed origins list.