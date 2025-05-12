import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from foundation.core_services.base_service import BaseService
from foundation.core_services.detection_service import DetectionService
from foundation.core_services.prediction_service import PredictionService
from foundation.core_services.notification_service import NotificationService


class TestServiceIntegration(unittest.TestCase):
    """
    Integration tests for the core services, verifying that the service 
    components work together correctly.
    """
    
    def setUp(self):
        """Set up the test environment."""
        # Create services with mocked dependencies
        self.detection_service = DetectionService()
        self.prediction_service = PredictionService()
        self.notification_service = NotificationService()
        
        # Set up mock data
        self.test_data = {
            "location": "Test County",
            "date": "2023-05-01",
            "samples": [
                {"id": "sample1", "result": "positive", "strain": "H5N1"},
                {"id": "sample2", "result": "negative", "strain": None}
            ]
        }
        
        # Configure mocks if needed
        if hasattr(self.detection_service, "database"):
            self.detection_service.database = Mock()
        
        if hasattr(self.prediction_service, "model"):
            self.prediction_service.model = Mock()
            self.prediction_service.model.predict.return_value = {
                "risk_level": "high",
                "probability": 0.85,
                "projected_cases": 120
            }

    @patch("foundation.core_services.notification_service.NotificationService.send_notification")
    def test_end_to_end_detection_prediction_notification(self, mock_send):
        """
        Test the integration between detection, prediction, and notification services.
        This simulates the full workflow of:
        1. Detecting a positive case
        2. Generating a prediction based on detection
        3. Sending a notification with the results
        """
        # 1. Detection Service processes data and identifies positive samples
        detection_results = self.detection_service.process_samples(self.test_data["samples"])
        
        # Validation
        self.assertIsNotNone(detection_results)
        self.assertTrue(any(sample.get("result") == "positive" for sample in detection_results))
        
        # 2. Prediction Service uses detection results to generate predictions
        prediction = self.prediction_service.generate_prediction(
            location=self.test_data["location"],
            date=self.test_data["date"],
            detection_data=detection_results
        )
        
        # Validation
        self.assertIsNotNone(prediction)
        self.assertIn("risk_level", prediction)
        
        # 3. Notification Service sends alert based on prediction
        self.notification_service.send_alert(
            location=self.test_data["location"],
            prediction=prediction,
            detection_data=detection_results
        )
        
        # Verify notification was sent with correct data
        mock_send.assert_called_once()
        call_args = mock_send.call_args[1]  # Get keyword arguments
        self.assertEqual(call_args.get("location"), self.test_data["location"])
        self.assertIn("prediction", call_args)
        self.assertIn("detection_data", call_args)

    def test_detection_service_integration(self):
        """Test that the detection service properly processes sample data."""
        result = self.detection_service.process_samples(self.test_data["samples"])
        
        # Verify correct processing
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        
        # Check specific processing of samples
        positive_samples = [s for s in result if s.get("result") == "positive"]
        self.assertEqual(len(positive_samples), 1)
        self.assertEqual(positive_samples[0].get("strain"), "H5N1")

    def test_prediction_service_integration(self):
        """Test that the prediction service generates predictions based on detection data."""
        detection_results = self.detection_service.process_samples(self.test_data["samples"])
        
        prediction = self.prediction_service.generate_prediction(
            location=self.test_data["location"],
            date=self.test_data["date"],
            detection_data=detection_results
        )
        
        # Verify prediction structure
        self.assertIsNotNone(prediction)
        self.assertIn("risk_level", prediction)
        self.assertIn("probability", prediction)
        
        # Verify prediction is influenced by detection data
        if prediction.get("risk_level") == "high":
            self.assertGreaterEqual(prediction.get("probability", 0), 0.7)


if __name__ == "__main__":
    unittest.main()