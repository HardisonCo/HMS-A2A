import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from foundation.extension_points.registry import ExtensionRegistry
from foundation.extension_points.base import ExtensionPoint
from foundation.extension_points.data_sources.api_based import APIDataSource
from foundation.extension_points.data_sources.file_based import FileDataSource
from foundation.extension_points.notification_channels.email import EmailNotificationChannel
from foundation.extension_points.notification_channels.webhook import WebhookNotificationChannel
from foundation.extension_points.predictive_models.disease_spread_model import DiseaseSpreadModel
from foundation.extension_points.visualization_components.choropleth_map import ChoroplethMap


class TestExtensionMechanisms(unittest.TestCase):
    """
    Integration tests for the extension point mechanisms, verifying that
    extension points can be registered, discovered, and used across the system.
    """
    
    def setUp(self):
        """Set up the test environment."""
        # Create a fresh registry for each test
        self.registry = ExtensionRegistry()
        
        # Create sample extension implementations
        self.api_source = APIDataSource(
            name="USDA APHIS API",
            base_url="https://api.aphis.usda.gov",
            auth_type="api_key"
        )
        
        self.file_source = FileDataSource(
            name="Local CSV Data",
            file_path="/data/bird_flu_reports.csv",
            format="csv"
        )
        
        self.email_channel = EmailNotificationChannel(
            name="Email Alerts",
            smtp_server="smtp.agency.gov",
            default_sender="alerts@agency.gov"
        )
        
        self.webhook_channel = WebhookNotificationChannel(
            name="Agency Webhook",
            endpoint_url="https://hooks.agency.gov/incoming",
            secret_key="test_secret"
        )
        
        self.disease_model = DiseaseSpreadModel(
            name="Avian Influenza Spread Model",
            model_type="compartmental",
            parameters={"transmission_rate": 0.8, "recovery_rate": 0.2}
        )
        
        self.map_component = ChoroplethMap(
            name="County-level Outbreak Map",
            geo_level="county",
            color_scale="YlOrRd"
        )

    def test_registry_extension_registration(self):
        """
        Test that extensions can be registered and retrieved by type.
        """
        # Register extensions
        self.registry.register("data_source", "api", self.api_source)
        self.registry.register("data_source", "file", self.file_source)
        self.registry.register("notification", "email", self.email_channel)
        self.registry.register("notification", "webhook", self.webhook_channel)
        self.registry.register("model", "disease_spread", self.disease_model)
        self.registry.register("visualization", "choropleth", self.map_component)
        
        # Verify extensions can be retrieved by type
        data_sources = self.registry.get_all("data_source")
        self.assertEqual(len(data_sources), 2)
        self.assertIn("api", data_sources)
        self.assertIn("file", data_sources)
        
        notifications = self.registry.get_all("notification")
        self.assertEqual(len(notifications), 2)
        
        models = self.registry.get_all("model")
        self.assertEqual(len(models), 1)
        
        visualizations = self.registry.get_all("visualization")
        self.assertEqual(len(visualizations), 1)

    def test_extension_access_by_id(self):
        """
        Test that specific extensions can be accessed by ID.
        """
        # Register extensions
        self.registry.register("data_source", "api", self.api_source)
        self.registry.register("notification", "email", self.email_channel)
        
        # Retrieve specific extensions
        api_extension = self.registry.get("data_source", "api")
        email_extension = self.registry.get("notification", "email")
        
        # Verify correct extensions are returned
        self.assertEqual(api_extension, self.api_source)
        self.assertEqual(email_extension, self.email_channel)
        
        # Verify non-existent extension returns None
        non_existent = self.registry.get("data_source", "non_existent")
        self.assertIsNone(non_existent)

    @patch("foundation.extension_points.data_sources.api_based.APIDataSource.fetch_data")
    @patch("foundation.extension_points.notification_channels.webhook.WebhookNotificationChannel.send")
    def test_extension_integration(self, mock_send, mock_fetch):
        """
        Test that extensions can be used together in an integrated workflow.
        """
        # Configure mocks
        mock_fetch.return_value = [
            {"county": "Dane", "state": "WI", "cases": 5, "date": "2023-05-01"},
            {"county": "Polk", "state": "WI", "cases": 2, "date": "2023-05-01"}
        ]
        mock_send.return_value = {"status": "success", "message": "Notification sent"}
        
        # Register extensions
        self.registry.register("data_source", "api", self.api_source)
        self.registry.register("notification", "webhook", self.webhook_channel)
        self.registry.register("model", "disease_spread", self.disease_model)
        self.registry.register("visualization", "choropleth", self.map_component)
        
        # Simulate integrated workflow:
        # 1. Fetch data using API data source
        api_source = self.registry.get("data_source", "api")
        data = api_source.fetch_data(endpoint="/avian-influenza/cases", params={"state": "WI"})
        
        # 2. Run disease model prediction
        model = self.registry.get("model", "disease_spread")
        prediction_results = model.predict(input_data=data)
        
        # 3. Create visualization
        visualization = self.registry.get("visualization", "choropleth")
        map_output = visualization.generate(data=prediction_results)
        
        # 4. Send notification with visualization
        notification = self.registry.get("notification", "webhook")
        notification_result = notification.send(
            title="New Bird Flu Prediction",
            message="New cases detected in Wisconsin counties",
            data=prediction_results,
            attachments=[map_output]
        )
        
        # Verify the workflow executed correctly
        mock_fetch.assert_called_once()
        mock_send.assert_called_once()
        self.assertEqual(notification_result["status"], "success")

    def test_custom_extension_registration(self):
        """
        Test that custom extensions can be dynamically created and registered.
        """
        # Create a custom extension class
        class CustomDataProcessor(ExtensionPoint):
            def __init__(self, name, processor_type):
                self.name = name
                self.processor_type = processor_type
                
            def process(self, data):
                return {"processed": True, "data": data, "type": self.processor_type}
        
        # Create instance and register
        custom_processor = CustomDataProcessor("Custom Processor", "anomaly_detection")
        self.registry.register("processor", "custom", custom_processor)
        
        # Retrieve and use custom extension
        retrieved_processor = self.registry.get("processor", "custom")
        self.assertIsNotNone(retrieved_processor)
        
        # Verify it works as expected
        result = retrieved_processor.process({"raw": "data"})
        self.assertTrue(result["processed"])
        self.assertEqual(result["type"], "anomaly_detection")

    def test_agency_specific_extensions(self):
        """
        Test that agency-specific extensions work with the core framework.
        """
        # Create agency-specific extension classes
        class CDCDataAdapter(ExtensionPoint):
            def __init__(self, name, data_format):
                self.name = name
                self.data_format = data_format
                
            def transform(self, data):
                return {
                    "agency": "CDC",
                    "format": self.data_format,
                    "transformed_data": data
                }
        
        class USDADataAdapter(ExtensionPoint):
            def __init__(self, name, species_filter):
                self.name = name
                self.species_filter = species_filter
                
            def transform(self, data):
                return {
                    "agency": "USDA",
                    "species_filter": self.species_filter,
                    "transformed_data": data
                }
        
        # Create and register agency extensions
        cdc_adapter = CDCDataAdapter("CDC Human Cases Adapter", "case_report")
        usda_adapter = USDADataAdapter("USDA Poultry Adapter", "poultry")
        
        self.registry.register("adapter", "cdc", cdc_adapter)
        self.registry.register("adapter", "usda", usda_adapter)
        
        # Verify both adapters are accessible
        adapters = self.registry.get_all("adapter")
        self.assertEqual(len(adapters), 2)
        
        # Test using both adapters in sequence
        cdc_result = self.registry.get("adapter", "cdc").transform({"original": "data"})
        usda_result = self.registry.get("adapter", "usda").transform(cdc_result)
        
        # Verify the composition works
        self.assertEqual(usda_result["agency"], "USDA")
        self.assertEqual(usda_result["transformed_data"]["agency"], "CDC")


if __name__ == "__main__":
    unittest.main()