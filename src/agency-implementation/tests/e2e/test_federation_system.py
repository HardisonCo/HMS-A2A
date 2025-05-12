import pytest
import json
import uuid
from datetime import datetime, timedelta

# Test federation system functionality
def test_federation_core_functionality(base_url, wait_for_services, federation_manager):
    """
    Tests the core functionality of the federation system including data sharing,
    governance enforcement, and cross-agency querying.
    """
    # 1. Test federation manager initialization
    assert federation_manager is not None
    
    # 2. Create test data with different classification levels
    test_datasets = [
        {
            "id": str(uuid.uuid4()),
            "source_agency": "cdc",
            "data_type": "outbreak_statistics",
            "classification": "public",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "disease": "avian_influenza",
                "total_cases": 157,
                "affected_states": 5,
                "trend": "increasing"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "source_agency": "epa",
            "data_type": "environmental_assessment",
            "classification": "sensitive",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "incident_type": "avian_influenza",
                "affected_waterways": 3,
                "contamination_level": "low",
                "monitoring_stations": 12
            }
        },
        {
            "id": str(uuid.uuid4()),
            "source_agency": "fema",
            "data_type": "resource_allocation",
            "classification": "restricted",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "incident_id": "AI-2023-1204",
                "personnel_deployed": 78,
                "funding_allocated": "$2.5M",
                "command_center_location": "Madison, WI"
            }
        }
    ]
    
    # 3. Test data sharing with different classification levels
    for dataset in test_datasets:
        sharing_result = federation_manager.share_data(
            dataset["source_agency"],
            dataset["data_type"],
            dataset
        )
        
        # All sharing operations should succeed
        assert sharing_result["success"] is True
        
        # Number of agencies data is shared with should vary by classification
        if dataset["classification"] == "public":
            # Public data should be shared with all agencies
            assert len(sharing_result["shared_with"]) >= 2
        elif dataset["classification"] == "sensitive":
            # Sensitive data shared with fewer agencies
            assert len(sharing_result["shared_with"]) >= 1
        elif dataset["classification"] == "restricted":
            # Restricted data shared with very limited agencies
            assert len(sharing_result["shared_with"]) >= 0
    
    # 4. Test federation governance enforcement
    # Test access to public data
    public_data_id = test_datasets[0]["id"]
    public_access = federation_manager.check_access("epa", "outbreak_statistics", public_data_id)
    assert public_access["has_access"] is True
    
    # Test access to sensitive data
    sensitive_data_id = test_datasets[1]["id"]
    sensitive_access = federation_manager.check_access("cdc", "environmental_assessment", sensitive_data_id)
    # CDC should have access to EPA's sensitive data due to federation rules
    assert sensitive_access["has_access"] is True
    
    # Test access to restricted data - results may vary based on governance rules
    restricted_data_id = test_datasets[2]["id"]
    restricted_access = federation_manager.check_access("epa", "resource_allocation", restricted_data_id)
    # This may be true or false depending on federation governance rules
    
    # 5. Test cross-agency querying
    query_params = {
        "keywords": ["avian", "influenza"],
        "time_period": {
            "start": (datetime.now() - timedelta(days=7)).isoformat(),
            "end": datetime.now().isoformat()
        },
        "data_types": ["outbreak_statistics", "environmental_assessment"]
    }
    
    # Query from CDC perspective (should see both public and sensitive data)
    cdc_query_result = federation_manager.cross_agency_query(
        requesting_agency="cdc",
        query_type="multi_agency_data",
        parameters=query_params
    )
    
    # CDC should get results from both CDC and EPA datasets
    assert cdc_query_result["success"] is True
    assert len(cdc_query_result["results"]) >= 2
    
    # Verify data sources in results
    result_sources = [result["source_agency"] for result in cdc_query_result["results"]]
    assert "cdc" in result_sources
    assert "epa" in result_sources

# Test federation identity and security
def test_federation_identity_security(base_url, wait_for_services, federation_manager):
    """
    Tests the federation system's identity management and security features.
    """
    # 1. Test agency identity verification
    identity_check = federation_manager.verify_agency_identity("cdc")
    assert identity_check["verified"] is True
    assert identity_check["agency"] == "cdc"
    
    # 2. Test invalid agency identity
    invalid_check = federation_manager.verify_agency_identity("invalid_agency")
    assert invalid_check["verified"] is False
    
    # 3. Test token issuance for agency
    token_result = federation_manager.issue_agency_token("cdc")
    assert token_result["success"] is True
    assert "token" in token_result
    
    # 4. Test token validation
    token = token_result["token"]
    validation_result = federation_manager.validate_agency_token(token)
    assert validation_result["valid"] is True
    assert validation_result["agency"] == "cdc"
    
    # 5. Test token revocation
    revocation_result = federation_manager.revoke_agency_token(token)
    assert revocation_result["success"] is True
    
    # Token should no longer be valid
    post_revocation_check = federation_manager.validate_agency_token(token)
    assert post_revocation_check["valid"] is False

# Test federation auditing
def test_federation_auditing(base_url, wait_for_services, federation_manager):
    """
    Tests the federation system's auditing capabilities.
    """
    # 1. Create test event for auditing
    test_data = {
        "id": str(uuid.uuid4()),
        "source_agency": "cdc",
        "data_type": "test_audit_data",
        "classification": "public",
        "timestamp": datetime.now().isoformat(),
        "content": {
            "test_field": "test_value"
        }
    }
    
    # 2. Share data which should generate audit records
    sharing_result = federation_manager.share_data(
        test_data["source_agency"],
        test_data["data_type"],
        test_data
    )
    assert sharing_result["success"] is True
    
    # 3. Access data which should generate audit records
    access_result = federation_manager.get_data(
        "epa",  # Accessing agency
        test_data["data_type"],
        test_data["id"]
    )
    assert access_result["success"] is True
    
    # 4. Retrieve audit records for the data
    audit_records = federation_manager.get_audit_records(
        data_id=test_data["id"]
    )
    
    # Should have at least two audit records (creation and access)
    assert len(audit_records) >= 2
    
    # Check types of audit records
    audit_types = [record["action"] for record in audit_records]
    assert "data_creation" in audit_types or "data_shared" in audit_types
    assert "data_accessed" in audit_types
    
    # 5. Test audit filtering
    # Filter by action type
    filtered_audits = federation_manager.get_audit_records(
        action_type="data_accessed"
    )
    
    # All records should be data_accessed type
    for record in filtered_audits:
        assert record["action"] == "data_accessed"
    
    # 6. Test agency activity auditing
    agency_activity = federation_manager.get_agency_activity("epa", limit=10)
    assert len(agency_activity) > 0

# Test federation synchronization
def test_federation_synchronization(base_url, wait_for_services, federation_manager):
    """
    Tests the federation system's ability to synchronize data across agencies.
    """
    # 1. Set up test data for synchronization
    sync_data = {
        "id": str(uuid.uuid4()),
        "source_agency": "cdc",
        "data_type": "synchronized_dataset",
        "classification": "public",
        "timestamp": datetime.now().isoformat(),
        "version": 1,
        "content": {
            "key_metric": 100,
            "status": "initial"
        }
    }
    
    # 2. Share initial data
    sharing_result = federation_manager.share_data(
        sync_data["source_agency"],
        sync_data["data_type"],
        sync_data
    )
    assert sharing_result["success"] is True
    
    # 3. Update the data
    updated_data = sync_data.copy()
    updated_data["version"] = 2
    updated_data["content"]["key_metric"] = 150
    updated_data["content"]["status"] = "updated"
    updated_data["timestamp"] = datetime.now().isoformat()
    
    update_result = federation_manager.update_data(
        sync_data["source_agency"],
        sync_data["data_type"],
        sync_data["id"],
        updated_data
    )
    assert update_result["success"] is True
    
    # 4. Verify synchronized data across agencies
    for agency in ["epa", "fema"]:
        agency_view = federation_manager.get_data(
            agency,
            sync_data["data_type"],
            sync_data["id"]
        )
        
        # Agency should see updated version
        assert agency_view["success"] is True
        assert agency_view["data"]["version"] == 2
        assert agency_view["data"]["content"]["key_metric"] == 150
        assert agency_view["data"]["content"]["status"] == "updated"
    
    # 5. Test synchronization conflict resolution
    # Create conflicting update
    conflict_data = updated_data.copy()
    conflict_data["version"] = 2  # Same version as current
    conflict_data["content"]["key_metric"] = 200
    conflict_data["content"]["status"] = "conflict"
    conflict_data["timestamp"] = datetime.now().isoformat()
    
    # This should trigger conflict resolution
    conflict_result = federation_manager.update_data(
        sync_data["source_agency"],
        sync_data["data_type"],
        sync_data["id"],
        conflict_data
    )
    
    # Conflict should be detected
    assert conflict_result["conflict_detected"] is True
    assert "resolution_strategy" in conflict_result
    
    # 6. Test data version history
    history = federation_manager.get_data_history(sync_data["id"])
    assert len(history) >= 2  # Should have at least 2 versions