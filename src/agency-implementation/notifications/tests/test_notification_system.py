"""
Tests for the Unified Notification System
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

from ..core.unified_notification_system import UnifiedNotificationSystem
from ..models.alert import Alert, AlertSeverity, AlertStatus


@pytest.fixture
def mock_config():
    """Provide mock configuration for tests."""
    return {
        "federation": {
            "base_url": "http://localhost:8000/api",
            "api_key": "test_key",
        },
        "channels": {
            "email": {
                "type": "email",
                "enabled": True,
                "smtp_host": "smtp.example.com",
            },
            "sms": {
                "type": "sms",
                "enabled": True,
            },
        },
        "adapters": {
            "cdc": {
                "type": "cdc",
                "api_url": "https://api.cdc.gov/alerts",
                "api_key": "test_key",
            },
            "epa": {
                "type": "epa",
                "api_url": "https://api.epa.gov/alerts",
                "api_key": "test_key",
            },
        }
    }


@pytest.fixture
def sample_alerts():
    """Provide sample alerts for testing."""
    return [
        Alert(
            id="cdc-001",
            title="Disease Outbreak Alert",
            description="A new disease outbreak has been detected.",
            source="CDC",
            alert_type="disease_outbreak",
            severity=AlertSeverity.HIGH,
            status=AlertStatus.NEW,
            url="https://cdc.gov/alerts/001",
            created_at=datetime.utcnow() - timedelta(hours=1),
        ),
        Alert(
            id="epa-001",
            title="Air Quality Warning",
            description="Air quality has reached unhealthy levels in certain areas.",
            source="EPA",
            alert_type="air_quality_alert",
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.NEW,
            url="https://epa.gov/alerts/001",
            created_at=datetime.utcnow() - timedelta(hours=2),
        ),
        Alert(
            id="fema-001",
            title="Flood Warning",
            description="Flooding expected in coastal areas.",
            source="FEMA",
            alert_type="emergency_warning",
            severity=AlertSeverity.HIGH,
            status=AlertStatus.NEW,
            url="https://fema.gov/alerts/001",
            created_at=datetime.utcnow() - timedelta(hours=3),
            regions=["FL", "GA", "SC"],
        ),
    ]


@pytest.mark.asyncio
async def test_initialization(mock_config):
    """Test system initialization."""
    
    with patch('notifications.federation.federation_client.FederationClient') as mock_federation, \
         patch('notifications.channels.channel_manager.NotificationChannelManager') as mock_channel_manager:
        
        # Mock initialization methods
        mock_federation.return_value.initialize = AsyncMock(return_value=True)
        mock_channel_manager.return_value.initialize = AsyncMock(return_value=True)
        
        # Create notification system
        system = UnifiedNotificationSystem(mock_config)
        
        # Test initialization
        result = await system.initialize()
        assert result is True
        
        # Verify mocks were called
        mock_federation.return_value.initialize.assert_called_once()
        mock_channel_manager.return_value.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_collect_alerts(mock_config, sample_alerts):
    """Test alert collection from agencies."""
    
    with patch('notifications.federation.federation_client.FederationClient') as mock_federation, \
         patch('notifications.channels.channel_manager.NotificationChannelManager') as mock_channel_manager, \
         patch('notifications.adapters.cdc_adapter.CDCAlertAdapter') as mock_cdc_adapter, \
         patch('notifications.adapters.epa_adapter.EPAAlertAdapter') as mock_epa_adapter:
        
        # Mock initialization
        mock_federation.return_value.initialize = AsyncMock(return_value=True)
        mock_channel_manager.return_value.initialize = AsyncMock(return_value=True)
        
        # Mock adapter responses
        mock_cdc_adapter.return_value.get_alerts = AsyncMock(return_value=[sample_alerts[0]])
        mock_cdc_adapter.return_value.initialize = AsyncMock(return_value=True)
        
        mock_epa_adapter.return_value.get_alerts = AsyncMock(return_value=[sample_alerts[1]])
        mock_epa_adapter.return_value.initialize = AsyncMock(return_value=True)
        
        # Mock adapter registry to return our mocks
        with patch('notifications.adapters.alert_adapter.AlertAdapter.get_adapter') as mock_get_adapter:
            def side_effect(adapter_type):
                if adapter_type == "cdc":
                    return mock_cdc_adapter
                elif adapter_type == "epa":
                    return mock_epa_adapter
                return None
                
            mock_get_adapter.side_effect = side_effect
            
            # Create and initialize system
            system = UnifiedNotificationSystem(mock_config)
            await system.initialize()
            
            # Test collect_alerts
            alerts = await system.collect_alerts()
            
            # Verify results
            assert len(alerts) == 2
            assert any(a.source == "CDC" for a in alerts)
            assert any(a.source == "EPA" for a in alerts)
            
            # Verify mocks were called
            mock_cdc_adapter.return_value.get_alerts.assert_called_once()
            mock_epa_adapter.return_value.get_alerts.assert_called_once()


@pytest.mark.asyncio
async def test_prioritize_alerts(mock_config, sample_alerts):
    """Test alert prioritization."""
    
    with patch('notifications.federation.federation_client.FederationClient') as mock_federation, \
         patch('notifications.channels.channel_manager.NotificationChannelManager') as mock_channel_manager:
        
        # Mock initialization
        mock_federation.return_value.initialize = AsyncMock(return_value=True)
        mock_channel_manager.return_value.initialize = AsyncMock(return_value=True)
        
        # Create and initialize system
        system = UnifiedNotificationSystem(mock_config)
        await system.initialize()
        
        # Test prioritize_alerts
        prioritized = await system.prioritize_alerts(sample_alerts)
        
        # Verify results
        assert len(prioritized) == 3
        
        # First should be highest severity (HIGH) and newest
        assert prioritized[0].id == "cdc-001"
        assert prioritized[0].severity == AlertSeverity.HIGH
        
        # Second should be other HIGH severity alert but older
        assert prioritized[1].id == "fema-001"
        assert prioritized[1].severity == AlertSeverity.HIGH
        
        # Third should be MEDIUM severity
        assert prioritized[2].id == "epa-001"
        assert prioritized[2].severity == AlertSeverity.MEDIUM


@pytest.mark.asyncio
async def test_deduplicate_alerts(mock_config):
    """Test alert deduplication."""
    
    with patch('notifications.federation.federation_client.FederationClient') as mock_federation, \
         patch('notifications.channels.channel_manager.NotificationChannelManager') as mock_channel_manager:
        
        # Mock initialization
        mock_federation.return_value.initialize = AsyncMock(return_value=True)
        mock_channel_manager.return_value.initialize = AsyncMock(return_value=True)
        
        # Create and initialize system
        system = UnifiedNotificationSystem(mock_config)
        await system.initialize()
        
        # Create duplicate alerts
        alerts = [
            Alert(
                id="cdc-001",
                title="Disease Outbreak",
                source="CDC",
                alert_type="outbreak",
            ),
            Alert(
                id="cdc-002",
                title="Disease Outbreak",  # Same title
                source="CDC",              # Same source
                alert_type="outbreak",     # Same type
            ),
            Alert(
                id="epa-001",
                title="Air Quality Warning",
                source="EPA",
                alert_type="air_quality",
            ),
        ]
        
        # Test deduplication
        unique_alerts = await system._deduplicate_alerts(alerts)
        
        # Should have 2 unique alerts
        assert len(unique_alerts) == 2
        alert_ids = [a.id for a in unique_alerts]
        assert "cdc-001" in alert_ids
        assert "epa-001" in alert_ids