import pytest
import json
import uuid
from datetime import datetime, timedelta

# Test notification system core functionality
def test_notification_core_functionality(base_url, wait_for_services, notification_system):
    """
    Tests the core functionality of the unified notification system.
    """
    # 1. Test basic notification creation and sending
    test_notification = {
        "id": str(uuid.uuid4()),
        "event_type": "test_event",
        "source_agency": "cdc",
        "severity": "medium",
        "message": "This is a test notification",
        "channels": ["email", "sms", "console"],
        "recipients": ["test_group"],
        "metadata": {
            "test_id": "core_functionality_test"
        }
    }
    
    send_result = notification_system.send_notification(test_notification)
    
    # Verify notification was sent successfully
    assert send_result["success"] is True
    assert "notification_id" in send_result
    assert len(send_result["channels"]) > 0
    
    # 2. Test notification with attachments
    attachment_notification = {
        "id": str(uuid.uuid4()),
        "event_type": "attachment_test",
        "source_agency": "cdc",
        "severity": "medium",
        "message": "This is a test notification with attachments",
        "channels": ["email"],
        "recipients": ["test_group"],
        "attachments": [
            {
                "name": "report.pdf",
                "content_type": "application/pdf",
                "content": "dummy_base64_content"  # In a real test, this would be actual encoded content
            }
        ]
    }
    
    attachment_result = notification_system.send_notification(attachment_notification)
    
    # Verify notification with attachments was sent
    assert attachment_result["success"] is True
    assert "email" in attachment_result["channels"]
    
    # 3. Test notification templates
    template_notification = {
        "id": str(uuid.uuid4()),
        "event_type": "template_test",
        "template_id": "outbreak_alert",
        "source_agency": "cdc",
        "severity": "high",
        "template_data": {
            "disease": "avian_influenza",
            "location": "Dane County, Wisconsin",
            "case_count": 12,
            "contact_info": "800-555-0123"
        },
        "channels": ["email", "sms"],
        "recipients": ["health_officials", "emergency_responders"]
    }
    
    template_result = notification_system.send_notification(template_notification)
    
    # Verify template-based notification was sent
    assert template_result["success"] is True
    assert len(template_result["channels"]) > 0
    assert len(template_result["recipient_groups"]) > 0

# Test notification system channel functionality
def test_notification_channels(base_url, wait_for_services, notification_system):
    """
    Tests the notification system's ability to send through different channels.
    """
    # Base notification for testing different channels
    base_notification = {
        "id": str(uuid.uuid4()),
        "event_type": "channel_test",
        "source_agency": "cdc",
        "severity": "medium",
        "message": "This is a channel test notification",
        "recipients": ["test_group"]
    }
    
    # 1. Test email channel
    email_notification = base_notification.copy()
    email_notification["channels"] = ["email"]
    email_notification["email_subject"] = "Test Email Notification"
    
    email_result = notification_system.send_notification(email_notification)
    assert email_result["success"] is True
    assert "email" in email_result["channels"]
    
    # 2. Test SMS channel
    sms_notification = base_notification.copy()
    sms_notification["channels"] = ["sms"]
    sms_notification["id"] = str(uuid.uuid4())
    
    sms_result = notification_system.send_notification(sms_notification)
    assert sms_result["success"] is True
    assert "sms" in sms_result["channels"]
    
    # 3. Test webhook channel
    webhook_notification = base_notification.copy()
    webhook_notification["channels"] = ["webhook"]
    webhook_notification["id"] = str(uuid.uuid4())
    webhook_notification["webhook_endpoints"] = ["https://example.com/notifications"]
    
    webhook_result = notification_system.send_notification(webhook_notification)
    assert webhook_result["success"] is True
    assert "webhook" in webhook_result["channels"]
    
    # 4. Test console channel
    console_notification = base_notification.copy()
    console_notification["channels"] = ["console"]
    console_notification["id"] = str(uuid.uuid4())
    
    console_result = notification_system.send_notification(console_notification)
    assert console_result["success"] is True
    assert "console" in console_result["channels"]
    
    # 5. Test multi-channel notification
    multi_channel = base_notification.copy()
    multi_channel["channels"] = ["email", "sms", "console"]
    multi_channel["id"] = str(uuid.uuid4())
    
    multi_result = notification_system.send_notification(multi_channel)
    assert multi_result["success"] is True
    assert len(multi_result["channels"]) == 3
    assert "email" in multi_result["channels"]
    assert "sms" in multi_result["channels"]
    assert "console" in multi_result["channels"]

# Test notification system recipient targeting
def test_notification_recipients(base_url, wait_for_services, notification_system):
    """
    Tests the notification system's ability to target different recipient groups.
    """
    # Base notification for testing different recipient groups
    base_notification = {
        "id": str(uuid.uuid4()),
        "event_type": "recipient_test",
        "source_agency": "cdc",
        "severity": "medium",
        "message": "This is a recipient test notification",
        "channels": ["console"]  # Using console for easy testing
    }
    
    # 1. Test single recipient group
    single_group = base_notification.copy()
    single_group["recipients"] = ["health_officials"]
    
    single_result = notification_system.send_notification(single_group)
    assert single_result["success"] is True
    assert "health_officials" in single_result["recipient_groups"]
    
    # 2. Test multiple recipient groups
    multi_group = base_notification.copy()
    multi_group["id"] = str(uuid.uuid4())
    multi_group["recipients"] = ["health_officials", "emergency_responders", "public_health_agencies"]
    
    multi_result = notification_system.send_notification(multi_group)
    assert multi_result["success"] is True
    assert len(multi_result["recipient_groups"]) == 3
    assert "health_officials" in multi_result["recipient_groups"]
    assert "emergency_responders" in multi_result["recipient_groups"]
    assert "public_health_agencies" in multi_result["recipient_groups"]
    
    # 3. Test geographic targeting
    geo_targeted = base_notification.copy()
    geo_targeted["id"] = str(uuid.uuid4())
    geo_targeted["recipients"] = ["health_officials"]
    geo_targeted["geographic_targeting"] = {
        "state": "Wisconsin",
        "counties": ["Dane", "Milwaukee"]
    }
    
    geo_result = notification_system.send_notification(geo_targeted)
    assert geo_result["success"] is True
    assert "geographic_targeting" in geo_result
    assert geo_result["geographic_targeting"]["state"] == "Wisconsin"
    
    # 4. Test role-based targeting
    role_targeted = base_notification.copy()
    role_targeted["id"] = str(uuid.uuid4())
    role_targeted["recipients"] = ["health_officials"]
    role_targeted["role_targeting"] = ["field_coordinator", "lab_manager"]
    
    role_result = notification_system.send_notification(role_targeted)
    assert role_result["success"] is True
    assert "role_targeting" in role_result
    assert len(role_result["role_targeting"]) == 2

# Test notification system agency adapters
def test_agency_notification_adapters(base_url, wait_for_services, notification_system):
    """
    Tests the agency-specific notification adapters.
    """
    # Test notifications through each agency adapter
    agencies = ["cdc", "epa", "fema"]
    
    for agency in agencies:
        agency_notification = {
            "id": str(uuid.uuid4()),
            "event_type": f"{agency}_adapter_test",
            "source_agency": agency,
            "severity": "medium",
            "message": f"Testing {agency.upper()} notification adapter",
            "channels": ["console"],  # Using console for easy testing
            "recipients": ["test_group"]
        }
        
        adapter_result = notification_system.send_notification(agency_notification)
        
        # Verify agency adapter worked
        assert adapter_result["success"] is True
        assert adapter_result["source_agency"] == agency
    
    # Test cross-agency notification
    cross_agency = {
        "id": str(uuid.uuid4()),
        "event_type": "cross_agency_test",
        "source_agency": "cdc",
        "related_agencies": ["epa", "fema"],
        "severity": "high",
        "message": "Cross-agency notification test",
        "channels": ["console"],
        "recipients": ["health_officials", "emergency_responders"]
    }
    
    cross_result = notification_system.send_notification(cross_agency)
    
    # Verify cross-agency notification
    assert cross_result["success"] is True
    assert len(cross_result["related_agencies"]) == 2
    assert "epa" in cross_result["related_agencies"]
    assert "fema" in cross_result["related_agencies"]

# Test notification system federation integration
def test_notification_federation_integration(base_url, wait_for_services, notification_system, federation_manager):
    """
    Tests the integration between the notification system and federation components.
    """
    # 1. Create a notification that requires federation data
    federated_notification = {
        "id": str(uuid.uuid4()),
        "event_type": "federated_notification_test",
        "source_agency": "cdc",
        "severity": "high",
        "message": "Testing federation-notification integration",
        "channels": ["console"],
        "recipients": ["test_group"],
        "federation_data_id": str(uuid.uuid4()),  # Reference to data in federation system
        "include_federation_data": True
    }
    
    # 2. First create some federation data for the notification to reference
    federation_data = {
        "id": federated_notification["federation_data_id"],
        "source_agency": "cdc",
        "data_type": "outbreak_data",
        "classification": "public",
        "timestamp": datetime.now().isoformat(),
        "content": {
            "disease": "avian_influenza",
            "cases": 25,
            "location": "Wisconsin"
        }
    }
    
    # Share the data in the federation system
    federation_manager.share_data(
        federation_data["source_agency"],
        federation_data["data_type"],
        federation_data
    )
    
    # 3. Send the notification with federation data
    federation_result = notification_system.send_notification(federated_notification)
    
    # Verify federation integration
    assert federation_result["success"] is True
    assert "federation_data_included" in federation_result
    assert federation_result["federation_data_included"] is True
    
    # 4. Test notification based on federation event
    # Simulate a federation event
    federation_event = {
        "event_type": "new_shared_data",
        "data_id": str(uuid.uuid4()),
        "source_agency": "epa",
        "data_type": "environmental_alert",
        "timestamp": datetime.now().isoformat(),
        "recipients": ["cdc", "fema"]
    }
    
    # Create a notification from the federation event
    event_notification = notification_system.create_from_federation_event(federation_event)
    
    # Send the event notification
    event_result = notification_system.send_notification(event_notification)
    
    # Verify federation event notification
    assert event_result["success"] is True
    assert event_result["source"] == "federation"
    assert event_result["original_source_agency"] == "epa"

# Test notification system status and delivery tracking
def test_notification_status_tracking(base_url, wait_for_services, notification_system):
    """
    Tests the notification system's status and delivery tracking.
    """
    # 1. Send a notification for tracking
    tracking_notification = {
        "id": str(uuid.uuid4()),
        "event_type": "tracking_test",
        "source_agency": "cdc",
        "severity": "medium",
        "message": "This is a notification for status tracking",
        "channels": ["email", "sms"],
        "recipients": ["health_officials"],
        "require_delivery_tracking": True
    }
    
    send_result = notification_system.send_notification(tracking_notification)
    assert send_result["success"] is True
    
    notification_id = send_result["notification_id"]
    
    # 2. Get notification status
    status_result = notification_system.get_notification_status(notification_id)
    
    # Verify status tracking
    assert status_result["notification_id"] == notification_id
    assert "status" in status_result
    assert "channels" in status_result
    assert "email" in status_result["channels"]
    assert "sms" in status_result["channels"]
    
    # 3. Get detailed delivery status
    delivery_result = notification_system.get_delivery_details(notification_id)
    
    # Verify delivery details
    assert delivery_result["notification_id"] == notification_id
    assert "delivery_attempts" in delivery_result
    assert "successful_deliveries" in delivery_result
    assert "failed_deliveries" in delivery_result
    
    # 4. Get notification metrics
    time_range = {
        "start": (datetime.now() - timedelta(hours=1)).isoformat(),
        "end": datetime.now().isoformat()
    }
    
    metrics = notification_system.get_notification_metrics(time_range)
    
    # Verify metrics collection
    assert "total_sent" in metrics
    assert "by_channel" in metrics
    assert "by_agency" in metrics
    assert "by_severity" in metrics
    assert metrics["total_sent"] > 0