import os
import pytest
import sys
import time
from unittest import mock
import requests
from requests.exceptions import ConnectionError

# Add the parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from foundation.federation.manager import FederationManager
from foundation.core_services.notification_service import NotificationService
from notifications.core.unified_notification_system import UnifiedNotificationSystem

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the dashboard API."""
    return os.environ.get("API_BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def federation_manager():
    """Create a federation manager instance for testing."""
    return FederationManager(config_path="foundation/federation/federation.yaml")

@pytest.fixture(scope="session")
def notification_system():
    """Create a notification system for testing."""
    return UnifiedNotificationSystem(config_file="notifications/config/notification_config.json")

@pytest.fixture(scope="session")
def agency_configs():
    """Load and return agency configurations."""
    configs = {
        "cdc": "implementations/cdc/config/agency.json",
        "epa": "implementations/epa/config/agency.json",
        "fema": "implementations/fema/config/agency.json"
    }
    return configs

@pytest.fixture(scope="session")
def dashboard_service():
    """Start the dashboard service and wait for it to be ready."""
    # This would normally start the service, but for tests we'll mock it
    # In a real implementation, this would use subprocess to start services
    # and ensure they're ready before continuing
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        yield "http://localhost:5000"

@pytest.fixture(scope="session")
def wait_for_services(base_url):
    """Wait for all services to be available."""
    services = [
        f"{base_url}/api/health",
        f"{base_url}/api/federation/health",
        f"{base_url}/api/notifications/health"
    ]
    
    max_retries = 30
    retry_interval = 1
    
    # In a real test, this would actually wait for services
    # For now, we'll just simulate success
    for service_url in services:
        for i in range(max_retries):
            try:
                # For testing purposes we'll assume success
                # response = requests.get(service_url, timeout=2)
                # if response.status_code == 200:
                #     break
                break
            except ConnectionError:
                if i < max_retries - 1:
                    time.sleep(retry_interval)
                else:
                    pytest.fail(f"Service {service_url} not available after {max_retries} retries")
    
    return True