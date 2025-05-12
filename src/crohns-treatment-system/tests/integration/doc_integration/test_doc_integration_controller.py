"""
Tests for the DocumentationIntegrationController API endpoints
"""

import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from flask import Flask

from src.api_gateway.doc_integration_controller import doc_integration_bp, register_routes

class DocIntegrationControllerTestCase(unittest.TestCase):
    """Test case for the DocumentationIntegrationController API endpoints"""

    def setUp(self):
        """Set up test environment for each test"""
        # Create Flask test app
        self.app = Flask(__name__)
        register_routes(self.app)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # Create test data file path
        self.test_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         "data", "doc_integration_test_data.json")
        
        # Load test data
        with open(self.test_data_path, 'r') as f:
            self.test_data = json.load(f)

    def tearDown(self):
        """Clean up after each test"""
        pass

    @patch("src.coordination.doc_integration.doc_integration_service.DocIntegrationService.export_abstractions_to_doc")
    def test_export_abstractions(self, mock_export):
        """Test the export_abstractions endpoint"""
        # Mock export_abstractions_to_doc
        mock_export.return_value = "/some/path/to/output"
        
        # Prepare request data
        data = {
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Test-Project"
        }
        
        # Make API request
        response = self.client.post(
            "/api/doc-integration/export-abstractions",
            json=data,
            content_type="application/json"
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["message"], "Abstractions exported successfully")
        self.assertEqual(response_data["output_path"], "/some/path/to/output")
        self.assertEqual(response_data["project_name"], "Test-Project")
        
        # Verify export_abstractions_to_doc was called
        mock_export.assert_called_once_with(
            abstractions=self.test_data["abstractions"],
            relationships=self.test_data["relationships"],
            project_name="Test-Project"
        )

    @patch("src.coordination.doc_integration.doc_integration_service.DocIntegrationService.publish_clinical_trial")
    def test_publish_trial(self, mock_publish):
        """Test the publish_trial endpoint"""
        # Mock publish_clinical_trial
        publication_info = {
            "publication_id": "pub-123",
            "file_path": "/some/path/publication.json",
            "writer_component": "/some/path/writer.vue",
            "status": "published",
            "timestamp": "2023-05-09T12:00:00Z",
            "metadata": {
                "trial_id": "CROHNS-001",
                "abstractions_count": 2
            }
        }
        mock_publish.return_value = publication_info
        
        # Prepare request data
        data = {
            "trial_data": self.test_data["clinical_trial"],
            "abstractions": [a for a in self.test_data["abstractions"] if a["id"] in self.test_data["clinical_trial"]["abstraction_ids"]]
        }
        
        # Make API request
        response = self.client.post(
            "/api/doc-integration/publish-trial",
            json=data,
            content_type="application/json"
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["message"], "Clinical trial published successfully")
        self.assertEqual(response_data["publication_info"], publication_info)
        
        # Verify publish_clinical_trial was called
        mock_publish.assert_called_once_with(
            trial_data=self.test_data["clinical_trial"],
            abstractions=data["abstractions"],
            writer_component_path=None
        )

    @patch("src.coordination.doc_integration.doc_integration_service.DocIntegrationService.generate_integrated_documentation")
    def test_generate_documentation(self, mock_generate):
        """Test the generate_documentation endpoint"""
        # Mock generate_integrated_documentation
        doc_info = {
            "documentation_path": "/some/path/to/docs",
            "published_trials": [{
                "publication_id": "pub-123",
                "file_path": "/some/path/publication.json"
            }],
            "project_name": "Test-Project",
            "timestamp": "2023-05-09T12:00:00Z",
            "status": "completed"
        }
        mock_generate.return_value = doc_info
        
        # Prepare request data
        data = {
            "clinical_trials": [self.test_data["clinical_trial"]],
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Test-Project"
        }
        
        # Make API request
        response = self.client.post(
            "/api/doc-integration/generate-documentation",
            json=data,
            content_type="application/json"
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["message"], "Documentation generated successfully")
        self.assertEqual(response_data["documentation_info"], doc_info)
        
        # Verify generate_integrated_documentation was called
        mock_generate.assert_called_once_with(
            clinical_trials=data["clinical_trials"],
            abstractions=data["abstractions"],
            relationships=data["relationships"],
            project_name="Test-Project"
        )

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.get_system_status")
    def test_get_integration_status(self, mock_status):
        """Test the get_integration_status endpoint"""
        # Mock get_system_status
        status_info = {
            "hms_doc": "connected",
            "hms_mfe": "connected",
            "timestamp": "2023-05-09T12:00:00Z",
            "doc_publications_count": 5,
            "mfe_publications_count": 3,
            "integrated_publications_count": 2
        }
        mock_status.return_value = status_info
        
        # Make API request
        response = self.client.get("/api/doc-integration/status")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["data"], status_info)
        
        # Verify get_system_status was called
        mock_status.assert_called_once()

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.get_publications")
    def test_get_publications(self, mock_publications):
        """Test the get_publications endpoint"""
        # Mock get_publications
        publications = [
            {
                "id": "doc-1",
                "project_name": "Test-Project-1",
                "timestamp": "2023-05-09T12:00:00Z",
                "type": "hms_doc"
            },
            {
                "id": "mfe-1",
                "title": "Test Trial 1",
                "timestamp": "2023-05-09T13:00:00Z",
                "type": "hms_mfe"
            }
        ]
        mock_publications.return_value = publications
        
        # Make API request
        response = self.client.get("/api/doc-integration/publications?type=hms_doc&limit=10")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["data"], publications)
        
        # Verify get_publications was called
        mock_publications.assert_called_once_with("hms_doc", 10)

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.get_publication_by_id")
    def test_get_publication(self, mock_publication):
        """Test the get_publication endpoint"""
        # Mock get_publication_by_id
        publication = {
            "id": "doc-1",
            "project_name": "Test-Project-1",
            "timestamp": "2023-05-09T12:00:00Z",
            "type": "hms_doc"
        }
        mock_publication.return_value = publication
        
        # Make API request
        response = self.client.get("/api/doc-integration/publications/doc-1")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["data"], publication)
        
        # Verify get_publication_by_id was called
        mock_publication.assert_called_once_with("doc-1")

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.get_publication_by_id")
    def test_get_publication_not_found(self, mock_publication):
        """Test the get_publication endpoint for a non-existent publication"""
        # Mock get_publication_by_id to return None
        mock_publication.return_value = None
        
        # Make API request
        response = self.client.get("/api/doc-integration/publications/non-existent")
        
        # Check response
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "error")
        self.assertIn("Publication not found", response_data["message"])
        
        # Verify get_publication_by_id was called
        mock_publication.assert_called_once_with("non-existent")

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.get_all_tasks")
    def test_get_tasks(self, mock_tasks):
        """Test the get_tasks endpoint"""
        # Mock get_all_tasks
        tasks = [
            {
                "id": "task-1",
                "type": "publish_doc",
                "status": "completed",
                "created_at": "2023-05-09T12:00:00Z",
                "updated_at": "2023-05-09T12:01:00Z"
            },
            {
                "id": "task-2",
                "type": "publish_mfe",
                "status": "running",
                "created_at": "2023-05-09T12:02:00Z",
                "updated_at": "2023-05-09T12:02:00Z"
            }
        ]
        mock_tasks.return_value = tasks
        
        # Make API request
        response = self.client.get("/api/doc-integration/tasks?limit=10")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["data"], tasks)
        
        # Verify get_all_tasks was called
        mock_tasks.assert_called_once_with(10)

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.get_task_status")
    def test_get_task(self, mock_task):
        """Test the get_task endpoint"""
        # Mock get_task_status
        task = {
            "id": "task-1",
            "type": "publish_doc",
            "status": "completed",
            "created_at": "2023-05-09T12:00:00Z",
            "updated_at": "2023-05-09T12:01:00Z",
            "result": {"some": "result"},
            "error": None
        }
        mock_task.return_value = task
        
        # Make API request
        response = self.client.get("/api/doc-integration/tasks/task-1")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["data"], task)
        
        # Verify get_task_status was called
        mock_task.assert_called_once_with("task-1")

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.get_task_status")
    def test_get_task_not_found(self, mock_task):
        """Test the get_task endpoint for a non-existent task"""
        # Mock get_task_status to return None
        mock_task.return_value = None
        
        # Make API request
        response = self.client.get("/api/doc-integration/tasks/non-existent")
        
        # Check response
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "error")
        self.assertIn("Task not found", response_data["message"])
        
        # Verify get_task_status was called
        mock_task.assert_called_once_with("non-existent")

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.schedule_documentation_task")
    def test_schedule_export_abstractions(self, mock_schedule):
        """Test the schedule_export_abstractions endpoint"""
        # Mock schedule_documentation_task
        task_id = "task-1"
        mock_schedule.return_value = task_id
        
        # Prepare request data
        data = {
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Test-Project"
        }
        
        # Make API request
        response = self.client.post(
            "/api/doc-integration/schedule/export-abstractions",
            json=data,
            content_type="application/json"
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["message"], "Export task scheduled successfully")
        self.assertEqual(response_data["task_id"], task_id)
        
        # Verify schedule_documentation_task was called
        mock_schedule.assert_called_once_with("publish_doc", {
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Test-Project"
        })

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.schedule_documentation_task")
    def test_schedule_publish_trial(self, mock_schedule):
        """Test the schedule_publish_trial endpoint"""
        # Mock schedule_documentation_task
        task_id = "task-2"
        mock_schedule.return_value = task_id
        
        # Prepare request data
        data = {
            "trial_data": self.test_data["clinical_trial"],
            "abstractions": [a for a in self.test_data["abstractions"] if a["id"] in self.test_data["clinical_trial"]["abstraction_ids"]]
        }
        
        # Make API request
        response = self.client.post(
            "/api/doc-integration/schedule/publish-trial",
            json=data,
            content_type="application/json"
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["message"], "Publish task scheduled successfully")
        self.assertEqual(response_data["task_id"], task_id)
        
        # Verify schedule_documentation_task was called
        mock_schedule.assert_called_once_with("publish_mfe", {
            "trial_data": self.test_data["clinical_trial"],
            "abstractions": data["abstractions"]
        })

    @patch("src.coordination.doc_integration.integration_coordinator.coordinator.schedule_documentation_task")
    def test_schedule_integrated_documentation(self, mock_schedule):
        """Test the schedule_integrated_documentation endpoint"""
        # Mock schedule_documentation_task
        task_id = "task-3"
        mock_schedule.return_value = task_id
        
        # Prepare request data
        data = {
            "clinical_trials": [self.test_data["clinical_trial"]],
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Test-Project"
        }
        
        # Make API request
        response = self.client.post(
            "/api/doc-integration/schedule/integrated-documentation",
            json=data,
            content_type="application/json"
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["message"], "Integrated documentation task scheduled successfully")
        self.assertEqual(response_data["task_id"], task_id)
        
        # Verify schedule_documentation_task was called
        mock_schedule.assert_called_once_with("generate_integrated", {
            "clinical_trials": data["clinical_trials"],
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Test-Project"
        })

    def test_missing_required_fields_export_abstractions(self):
        """Test the export_abstractions endpoint with missing required fields"""
        # Prepare request data with missing fields
        data = {
            "abstractions": self.test_data["abstractions"]
            # Missing relationships
        }
        
        # Make API request
        response = self.client.post(
            "/api/doc-integration/export-abstractions",
            json=data,
            content_type="application/json"
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data["status"], "error")
        self.assertIn("Missing required fields", response_data["message"])

if __name__ == '__main__':
    unittest.main()