#!/usr/bin/env python3
"""
Federation Client Example.

This script demonstrates how to use the federation framework as a client.
"""

import os
import sys
import argparse
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from federation.manager import FederationManager
from federation.models import TrustLevel, SecurityClassification, SyncMode
from federation.exceptions import FederationError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_client_example(args):
    """Run client example."""
    # Initialize federation manager
    federation = FederationManager(
        local_agency_id="USDA-APHIS",
        config_path=args.config
    )
    
    # Register sample partner agencies
    federation.register_partner(
        agency_id="STATE-DOA-WA",
        endpoint="https://wa-agriculture.gov/federation",
        trust_level=TrustLevel.PARTNER,
        allowed_datasets=["outbreak_reports", "poultry_farm_status"]
    )
    
    federation.register_partner(
        agency_id="CDC",
        endpoint="https://cdc.gov/federation",
        trust_level=TrustLevel.TRUSTED,
        allowed_datasets=["human_exposure", "health_metrics"]
    )
    
    # Print registered partners
    print("\n=== Registered Partner Agencies ===")
    for agency in federation.list_partners():
        print(f"Agency: {agency.id}")
        print(f"  Endpoint: {agency.endpoint}")
        print(f"  Trust Level: {agency.trust_level}")
        print(f"  Allowed Datasets: {', '.join(agency.allowed_datasets)}")
        print()
    
    # Example 1: Execute a federated query
    print("\n=== Example 1: Federated Query ===")
    try:
        # Build and execute a query
        query_results = federation.query.build() \
            .select("outbreak_reports") \
            .where({"state": "WA", "date_range": "last_30_days"}) \
            .limit(10) \
            .execute()
        
        print(f"Query Results:")
        print(json.dumps(query_results, indent=2))
    except FederationError as e:
        print(f"Query error: {str(e)}")
    
    # Example 2: Create and execute a sync job
    print("\n=== Example 2: Data Synchronization ===")
    try:
        # Create sync job
        sync_job = federation.sync.create_job(
            target_agency="STATE-DOA-WA",
            datasets=["poultry_farm_status"],
            sync_mode=SyncMode.INCREMENTAL
        )
        
        print(f"Created Sync Job: {sync_job.job_id}")
        print(f"  Target Agency: {sync_job.target_agency}")
        print(f"  Datasets: {', '.join(sync_job.datasets)}")
        print(f"  Sync Mode: {sync_job.sync_mode}")
        print(f"  Status: {sync_job.status}")
        
        # Execute sync job
        federation.sync.execute_job(sync_job)
        print(f"Executing sync job...")
        
        # In a real application, we would wait for the job to complete
        # For this example, we'll just print the current status
        print(f"  New Status: {sync_job.status}")
    except FederationError as e:
        print(f"Sync error: {str(e)}")
    
    # Example 3: Create and apply a federation policy
    print("\n=== Example 3: Federation Policy ===")
    try:
        # Create a policy
        from federation.models import FederationPolicy, AccessRule
        
        policy = FederationPolicy(
            dataset="poultry_farm_status",
            security_classification=SecurityClassification.SENSITIVE,
            rules=[
                AccessRule(
                    agency_patterns=["STATE-DOA-*"],
                    role_patterns=["admin", "data_analyst"],
                    effect="ALLOW"
                ),
                AccessRule(
                    agency_patterns=["CDC"],
                    role_patterns=["health_officer"],
                    effect="ALLOW"
                )
            ],
            retention_period="90d",
            data_sovereignty=["US"]
        )
        
        # Apply policy
        federation.apply_policy("poultry_farm_status", policy)
        
        print(f"Applied policy for dataset: poultry_farm_status")
        print(f"  Classification: {policy.security_classification}")
        print(f"  Rules: {len(policy.rules)}")
        print(f"  Retention: {policy.retention_period}")
        print(f"  Data Sovereignty: {', '.join(policy.data_sovereignty)}")
    except FederationError as e:
        print(f"Policy error: {str(e)}")
    
    # Example 4: Register and validate a schema
    print("\n=== Example 4: Schema Registry ===")
    try:
        # Create a schema
        from federation.models import DatasetSchema
        
        schema = DatasetSchema(
            name="outbreak_reports",
            version="1.0.0",
            fields={
                "id": {
                    "type": "string",
                    "required": True,
                    "description": "Unique identifier for the report"
                },
                "report_date": {
                    "type": "string",
                    "format": "date-time",
                    "required": True,
                    "description": "Date and time of the report"
                },
                "location": {
                    "type": "object",
                    "required": True,
                    "description": "Geographic location of the outbreak",
                    "properties": {
                        "state": {"type": "string"},
                        "county": {"type": "string"},
                        "coordinates": {
                            "type": "object",
                            "properties": {
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"}
                            }
                        }
                    }
                },
                "disease_type": {
                    "type": "string",
                    "enum": ["H5N1", "H5N8", "H7N9", "OTHER"],
                    "required": True,
                    "description": "Type of avian influenza"
                },
                "affected_birds": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Number of affected birds"
                },
                "status": {
                    "type": "string",
                    "enum": ["SUSPECTED", "CONFIRMED", "CONTAINED", "RESOLVED"],
                    "required": True,
                    "description": "Status of the outbreak"
                }
            },
            security_classification=SecurityClassification.SENSITIVE,
            description="Schema for poultry disease outbreak reports",
            owner_agency="USDA-APHIS"
        )
        
        # Register schema
        federation.schema_registry.register_schema(schema)
        
        print(f"Registered schema: {schema.name} version {schema.version}")
        print(f"  Fields: {len(schema.fields)}")
        print(f"  Classification: {schema.security_classification}")
        
        # Validate sample data against schema
        sample_data = {
            "id": "OUT-2023-001",
            "report_date": "2023-05-15T10:30:00Z",
            "location": {
                "state": "WA",
                "county": "Yakima",
                "coordinates": {
                    "latitude": 46.6021,
                    "longitude": -120.5059
                }
            },
            "disease_type": "H5N1",
            "affected_birds": 150,
            "status": "CONFIRMED"
        }
        
        federation.schema_registry.validate_data(sample_data, "outbreak_reports")
        print("  Sample data validation: PASSED")
    except FederationError as e:
        print(f"Schema error: {str(e)}")
    
    print("\nFederation client example completed.")


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Federation Client Example")
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run example
    try:
        asyncio.run(run_client_example(args))
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()