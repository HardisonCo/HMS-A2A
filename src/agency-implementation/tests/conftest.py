import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def mock_api_client():
    """Create a mock API client for testing."""
    client = Mock()
    client.get.return_value = {"status": "success", "data": []}
    client.post.return_value = {"status": "success", "id": "new_id"}
    client.put.return_value = {"status": "success", "id": "updated_id"}
    client.delete.return_value = {"status": "success"}
    return client


@pytest.fixture
def sample_detection_data():
    """Sample detection data for testing."""
    return [
        {
            "id": "sample1",
            "location": {
                "county": "Dane",
                "state": "Wisconsin",
                "coordinates": {"lat": 43.0731, "lng": -89.4012}
            },
            "date": "2023-05-01",
            "type": "poultry",
            "result": "positive",
            "strain": "H5N1"
        },
        {
            "id": "sample2",
            "location": {
                "county": "Jefferson",
                "state": "Wisconsin",
                "coordinates": {"lat": 43.0056, "lng": -88.7741}
            },
            "date": "2023-05-02",
            "type": "wild_bird",
            "result": "positive",
            "strain": "H5N1"
        },
        {
            "id": "sample3",
            "location": {
                "county": "Dane",
                "state": "Wisconsin",
                "coordinates": {"lat": 43.0731, "lng": -89.4012}
            },
            "date": "2023-05-03",
            "type": "human",
            "result": "negative",
            "strain": None
        }
    ]


@pytest.fixture
def mock_federation_gateway():
    """Create a mock federation gateway for testing."""
    gateway = Mock()
    gateway.execute_query.return_value = [
        {"id": "case1", "location": "Wisconsin", "date": "2023-05-01", "type": "poultry", "_source": "usda"},
        {"id": "case2", "location": "Iowa", "date": "2023-05-02", "type": "wild_bird", "_source": "usda"},
        {"id": "case3", "location": "Minnesota", "date": "2023-05-01", "type": "human", "_source": "cdc"}
    ]
    return gateway


@pytest.fixture
def mock_extension_registry():
    """Create a mock extension registry for testing."""
    registry = Mock()
    
    # Configure the registry to return mock extensions
    data_source = Mock()
    data_source.fetch_data.return_value = [{"id": "data1"}, {"id": "data2"}]
    
    notification = Mock()
    notification.send.return_value = {"status": "success"}
    
    model = Mock()
    model.predict.return_value = {"prediction": "data"}
    
    visualization = Mock()
    visualization.generate.return_value = {"type": "image", "data": "base64_content"}
    
    # Configure get method
    def get_side_effect(extension_type, extension_id):
        if extension_type == "data_source" and extension_id == "api":
            return data_source
        elif extension_type == "notification" and extension_id == "email":
            return notification
        elif extension_type == "model" and extension_id == "disease":
            return model
        elif extension_type == "visualization" and extension_id == "map":
            return visualization
        return None
    
    registry.get.side_effect = get_side_effect
    
    # Configure get_all method
    def get_all_side_effect(extension_type):
        if extension_type == "data_source":
            return {"api": data_source, "file": Mock()}
        elif extension_type == "notification":
            return {"email": notification, "webhook": Mock()}
        elif extension_type == "model":
            return {"disease": model}
        elif extension_type == "visualization":
            return {"map": visualization}
        return {}
    
    registry.get_all.side_effect = get_all_side_effect
    
    return registry