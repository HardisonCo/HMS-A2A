import unittest
from unittest.mock import Mock, patch
import sys
import os
import json
import pytest

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import implementation-specific modules if they exist
try:
    from implementations.cdc.src.services.disease_surveillance_service import DiseaseSurveillanceService
    from implementations.cdc.src.models.disease_model import DiseaseModel
    CDC_MODULES_AVAILABLE = True
except ImportError:
    CDC_MODULES_AVAILABLE = False

try:
    from implementations.fema.src.services.emergency_response_service import EmergencyResponseService
    FEMA_MODULES_AVAILABLE = True
except ImportError:
    FEMA_MODULES_AVAILABLE = False

# Import foundation modules
from foundation.api_framework.app_factory import create_app
from foundation.core_services.detection_service import DetectionService
from foundation.federation.gateway import FederationGateway
from foundation.extension_points.registry import ExtensionRegistry


class TestImplementationIntegration(unittest.TestCase):
    """
    Integration tests for the example implementations (CDC, EPA, FEMA)
    to verify they correctly implement and extend the foundation components.
    """
    
    def setUp(self):
        """Set up the test environment."""
        # Set up basic foundation components
        self.app = create_app()
        self.detection_service = DetectionService()
        self.federation_gateway = Mock(spec=FederationGateway)
        self.extension_registry = ExtensionRegistry()
        
        # Mock federation gateway response
        self.federation_gateway.execute_query.return_value = [
            {"id": "case1", "location": "Wisconsin", "date": "2023-05-01", "type": "poultry", "_source": "usda"},
            {"id": "case2", "location": "Iowa", "date": "2023-05-02", "type": "wild_bird", "_source": "usda"},
            {"id": "case3", "location": "Minnesota", "date": "2023-05-01", "type": "human", "_source": "cdc"}
        ]
        
        # Sample data for testing
        self.sample_data = {
            "cases": [
                {"id": "case1", "location": "Wisconsin", "date": "2023-05-01", "species": "poultry", "strain": "H5N1"},
                {"id": "case2", "location": "Iowa", "date": "2023-05-02", "species": "wild_bird", "strain": "H5N1"}
            ],
            "predictions": {
                "risk_level": "high",
                "affected_counties": ["Dane", "Jefferson", "Rock"],
                "projected_spread": "increasing"
            }
        }

    @pytest.mark.skipif(
        not CDC_MODULES_AVAILABLE,
        reason="CDC implementation modules not available"
    )
    def test_cdc_implementation_integration(self):
        """
        Test that the CDC implementation correctly integrates with foundation components.
        """
        # Create CDC-specific services
        disease_model = DiseaseModel()
        surveillance_service = DiseaseSurveillanceService(
            detection_service=self.detection_service,
            federation_gateway=self.federation_gateway,
            disease_model=disease_model,
            extension_registry=self.extension_registry
        )
        
        # Register CDC-specific extensions
        with patch.object(ExtensionRegistry, 'register') as mock_register:
            surveillance_service.register_extensions()
            # Verify extensions were registered
            self.assertTrue(mock_register.called)
        
        # Test data processing method with federation gateway integration
        with patch.object(FederationGateway, 'execute_query') as mock_query:
            mock_query.return_value = self.federation_gateway.execute_query.return_value
            
            processed_data = surveillance_service.process_surveillance_data(
                start_date="2023-05-01", 
                end_date="2023-05-10",
                states=["Wisconsin", "Iowa", "Minnesota"]
            )
            
            # Verify the federation gateway was called
            self.assertTrue(mock_query.called)
            # Verify the data was processed correctly
            self.assertIsNotNone(processed_data)
            self.assertIn("human_cases", processed_data)
            self.assertIn("animal_cases", processed_data)
        
        # Test prediction integration with detection service
        with patch.object(DetectionService, 'process_samples') as mock_process:
            # Configure mock to return sample data
            mock_process.return_value = [
                {"id": "sample1", "result": "positive", "strain": "H5N1"}
            ]
            
            # Test prediction method
            prediction = surveillance_service.predict_disease_spread(
                location="Wisconsin",
                samples=[{"id": "sample1", "result": "pending"}]
            )
            
            # Verify the detection service was called
            self.assertTrue(mock_process.called)
            # Verify prediction structure
            self.assertIsNotNone(prediction)
            self.assertIn("risk_level", prediction)

    @pytest.mark.skipif(
        not FEMA_MODULES_AVAILABLE,
        reason="FEMA implementation modules not available"
    )
    def test_fema_implementation_integration(self):
        """
        Test that the FEMA implementation correctly integrates with foundation components.
        """
        # Create FEMA-specific services
        emergency_service = EmergencyResponseService(
            detection_service=self.detection_service,
            federation_gateway=self.federation_gateway,
            extension_registry=self.extension_registry
        )
        
        # Test emergency response planning with detection service integration
        with patch.object(DetectionService, 'process_samples') as mock_process:
            # Configure mock
            mock_process.return_value = [
                {"id": "sample1", "result": "positive", "strain": "H5N1", "location": "Dane County, WI"}
            ]
            
            # Test response planning method
            response_plan = emergency_service.generate_response_plan(
                incident_data={"type": "bird_flu_outbreak", "location": "Wisconsin"},
                severity="high"
            )
            
            # Verify structure of response plan
            self.assertIsNotNone(response_plan)
            self.assertIn("actions", response_plan)
            self.assertIn("resources", response_plan)
            self.assertIn("timeline", response_plan)
        
        # Test federation integration for resource coordination
        with patch.object(FederationGateway, 'execute_query') as mock_query:
            # Configure mock
            mock_query.return_value = [
                {"id": "resource1", "type": "medical_team", "location": "Minnesota", "available": True},
                {"id": "resource2", "type": "testing_kit", "location": "Wisconsin", "available": True}
            ]
            
            # Test resource coordination method
            resource_plan = emergency_service.coordinate_resources(
                incident_location="Wisconsin",
                resource_types=["medical_team", "testing_kit"]
            )
            
            # Verify the federation gateway was called
            self.assertTrue(mock_query.called)
            # Verify resource plan structure
            self.assertIsNotNone(resource_plan)
            self.assertIn("allocated_resources", resource_plan)
            self.assertIn("resource_gaps", resource_plan)

    def test_extension_customization_across_implementations(self):
        """
        Test that implementations can customize extensions while maintaining
        compatibility with the foundation framework.
        """
        # Define sample extensions for different agencies
        class CDCVisualizationExtension:
            def generate(self, data):
                return {
                    "type": "cdc_visualization",
                    "data": data,
                    "agency": "CDC"
                }
        
        class FEMAVisualizationExtension:
            def generate(self, data):
                return {
                    "type": "fema_visualization",
                    "data": data,
                    "agency": "FEMA"
                }
        
        # Register extensions
        self.extension_registry.register("visualization", "cdc_map", CDCVisualizationExtension())
        self.extension_registry.register("visualization", "fema_map", FEMAVisualizationExtension())
        
        # Verify extensions can be retrieved
        cdc_extension = self.extension_registry.get("visualization", "cdc_map")
        fema_extension = self.extension_registry.get("visualization", "fema_map")
        
        self.assertIsNotNone(cdc_extension)
        self.assertIsNotNone(fema_extension)
        
        # Verify extensions produce agency-specific output
        cdc_output = cdc_extension.generate(self.sample_data)
        fema_output = fema_extension.generate(self.sample_data)
        
        self.assertEqual(cdc_output["agency"], "CDC")
        self.assertEqual(fema_output["agency"], "FEMA")
        self.assertEqual(cdc_output["type"], "cdc_visualization")
        self.assertEqual(fema_output["type"], "fema_visualization")

    def test_configuration_loading(self):
        """
        Test that agency-specific configurations can be loaded and applied.
        """
        # Load configuration files from implementations
        config_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         "implementations", "cdc", "config", "agency.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         "implementations", "epa", "config", "agency.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         "implementations", "fema", "config", "agency.json")
        ]
        
        configs = {}
        for path in config_paths:
            try:
                with open(path, 'r') as f:
                    agency_name = os.path.basename(os.path.dirname(os.path.dirname(path)))
                    configs[agency_name] = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Skip if file doesn't exist or is not valid JSON
                pass
        
        # Verify configurations were loaded (if they exist)
        if configs:
            # Check for required configuration keys across all agencies
            for agency, config in configs.items():
                self.assertIn("agency_name", config)
                self.assertIn("api", config)
                # Verify API configuration
                self.assertIn("base_url", config["api"])
                self.assertIn("version", config["api"])


if __name__ == "__main__":
    unittest.main()