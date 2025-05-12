import unittest
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from foundation.api_framework.app_factory import create_app
from foundation.api_framework.routers.router_factory import create_router
from foundation.api_framework.controllers.base_controller import BaseController


class TestAPIIntegration(unittest.TestCase):
    """
    Integration tests for the API framework, verifying that controllers, routers, 
    and the application factory work together correctly.
    """
    
    def setUp(self):
        """Set up the test environment."""
        # Create a mock controller
        self.mock_controller = Mock(spec=BaseController)
        self.mock_controller.get_all = Mock(return_value={"data": ["item1", "item2"]})
        self.mock_controller.get_by_id = Mock(return_value={"data": "item1"})
        self.mock_controller.create = Mock(return_value={"data": "new_item"})
        self.mock_controller.update = Mock(return_value={"data": "updated_item"})
        self.mock_controller.delete = Mock(return_value={"message": "Item deleted"})
        
        # Create router with the mock controller
        self.router = create_router("test", self.mock_controller)
        
        # Create app with the router
        self.app = create_app()
        self.app.include_router(self.router)
        
        # Create test client
        self.client = self.app.test_client() if hasattr(self.app, "test_client") else None

    @pytest.mark.skipif(
        "client is None", 
        reason="Test client not available, using mock framework"
    )
    def test_get_all_endpoint(self):
        """Test that the GET /test endpoint works correctly."""
        response = self.client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"data": ["item1", "item2"]}
        self.mock_controller.get_all.assert_called_once()

    @pytest.mark.skipif(
        "client is None", 
        reason="Test client not available, using mock framework"
    )
    def test_get_by_id_endpoint(self):
        """Test that the GET /test/{id} endpoint works correctly."""
        response = self.client.get("/test/1")
        assert response.status_code == 200
        assert response.json() == {"data": "item1"}
        self.mock_controller.get_by_id.assert_called_once_with("1")

    @pytest.mark.skipif(
        "client is None", 
        reason="Test client not available, using mock framework"
    )
    def test_create_endpoint(self):
        """Test that the POST /test endpoint works correctly."""
        response = self.client.post("/test", json={"name": "new_item"})
        assert response.status_code == 201
        assert response.json() == {"data": "new_item"}
        self.mock_controller.create.assert_called_once()

    @pytest.mark.skipif(
        "client is None", 
        reason="Test client not available, using mock framework"
    )
    def test_update_endpoint(self):
        """Test that the PUT /test/{id} endpoint works correctly."""
        response = self.client.put("/test/1", json={"name": "updated_item"})
        assert response.status_code == 200
        assert response.json() == {"data": "updated_item"}
        self.mock_controller.update.assert_called_once()

    @pytest.mark.skipif(
        "client is None", 
        reason="Test client not available, using mock framework"
    )
    def test_delete_endpoint(self):
        """Test that the DELETE /test/{id} endpoint works correctly."""
        response = self.client.delete("/test/1")
        assert response.status_code == 200
        assert response.json() == {"message": "Item deleted"}
        self.mock_controller.delete.assert_called_once_with("1")

    def test_router_creation(self):
        """Test that router creation works without app client."""
        # Since we might not have an actual framework test client
        # we can at least verify router and endpoints are created correctly
        assert self.router is not None
        assert hasattr(self.router, "routes") or hasattr(self.router, "endpoints")

    def test_app_creation(self):
        """Test that app creation works."""
        assert self.app is not None


if __name__ == "__main__":
    unittest.main()