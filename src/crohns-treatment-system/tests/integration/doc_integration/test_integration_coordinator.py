"""
Tests for the IntegrationCoordinator module
"""

import os
import json
import unittest
import tempfile
import shutil
import time
from datetime import datetime
from unittest.mock import patch, MagicMock, PropertyMock

from src.coordination.doc_integration.doc_integration_service import DocIntegrationService
from src.coordination.doc_integration.integration_coordinator import IntegrationCoordinator

class IntegrationCoordinatorTestCase(unittest.TestCase):
    """Test case for the IntegrationCoordinator class"""

    def setUp(self):
        """Set up test environment for each test"""
        # Create temporary directories for HMS-DOC and HMS-MFE
        self.temp_doc_dir = tempfile.mkdtemp(prefix="test_hms_doc_")
        self.temp_mfe_dir = tempfile.mkdtemp(prefix="test_hms_mfe_")
        self.temp_output_dir = tempfile.mkdtemp(prefix="test_output_")
        
        # Create directories and files needed
        self._setup_mock_environment()
        
        # Create test data file path
        self.test_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         "data", "doc_integration_test_data.json")
        
        # Load test data
        with open(self.test_data_path, 'r') as f:
            self.test_data = json.load(f)
            
        # Create doc_integration_service
        self.doc_service = DocIntegrationService(
            doc_root_path=self.temp_doc_dir,
            mfe_root_path=self.temp_mfe_dir,
            output_dir=self.temp_output_dir
        )
        
        # Initialize IntegrationCoordinator with the service
        self.coordinator = IntegrationCoordinator(self.doc_service)
        
        # Ensure publication history file is empty
        if os.path.exists(self.coordinator.publication_history_file):
            os.remove(self.coordinator.publication_history_file)
            
        # Reset publications to empty
        self.coordinator.publications = {
            "hms_doc": [],
            "hms_mfe": [],
            "integrated": []
        }
        self.coordinator._save_publication_history()

    def _setup_mock_environment(self):
        """Set up mock environment for testing"""
        # Create Utils directory in HMS-DOC
        utils_dir = os.path.join(self.temp_doc_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        # Create standalone_generator.py in HMS-DOC/utils
        standalone_generator_path = os.path.join(utils_dir, "standalone_generator.py")
        with open(standalone_generator_path, 'w') as f:
            f.write("#!/usr/bin/env python\n# Mock generator script")
        os.chmod(standalone_generator_path, 0o755)
        
        # Create json-server/data directory in HMS-MFE
        json_server_dir = os.path.join(self.temp_mfe_dir, "json-server", "data")
        os.makedirs(json_server_dir, exist_ok=True)
        
        # Create writer.vue component in HMS-MFE
        pages_dir = os.path.join(self.temp_mfe_dir, "src", "pages", "sidebar", "dashboards")
        os.makedirs(pages_dir, exist_ok=True)
        with open(os.path.join(pages_dir, "writer.vue"), 'w') as f:
            f.write("<template>\n<div>Mock Writer Component</div>\n</template>")

    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.temp_doc_dir)
        shutil.rmtree(self.temp_mfe_dir)
        shutil.rmtree(self.temp_output_dir)
        
        # Remove publication history file if it exists
        if os.path.exists(self.coordinator.publication_history_file):
            os.remove(self.coordinator.publication_history_file)

    def test_init(self):
        """Test initialization of IntegrationCoordinator"""
        self.assertIsNotNone(self.coordinator.doc_service)
        self.assertIsInstance(self.coordinator.publications, dict)
        self.assertIn("hms_doc", self.coordinator.publications)
        self.assertIn("hms_mfe", self.coordinator.publications)
        self.assertIn("integrated", self.coordinator.publications)
        self.assertIsInstance(self.coordinator.tasks, dict)

    def test_get_system_status(self):
        """Test getting system status"""
        status = self.coordinator.get_system_status()
        
        # Check status structure
        self.assertIn("hms_doc", status)
        self.assertIn("hms_mfe", status)
        self.assertIn("timestamp", status)
        self.assertIn("doc_publications_count", status)
        self.assertIn("mfe_publications_count", status)
        self.assertIn("integrated_publications_count", status)
        
        # Check status values
        self.assertEqual(status["hms_doc"], "connected")
        self.assertEqual(status["hms_mfe"], "connected")
        self.assertEqual(status["doc_publications_count"], 0)
        self.assertEqual(status["mfe_publications_count"], 0)
        self.assertEqual(status["integrated_publications_count"], 0)

    @patch("src.coordination.doc_integration.doc_integration_service.DocIntegrationService.export_abstractions_to_doc")
    def test_publish_to_hms_doc(self, mock_export):
        """Test publishing to HMS-DOC"""
        # Mock export_abstractions_to_doc
        mock_export.return_value = os.path.join(self.temp_output_dir, "test-project")
        
        abstractions = self.test_data["abstractions"]
        relationships = self.test_data["relationships"]
        project_name = "Test-Project"
        
        result = self.coordinator.publish_to_hms_doc(
            abstractions=abstractions,
            relationships=relationships,
            project_name=project_name
        )
        
        # Check result structure
        self.assertIn("id", result)
        self.assertIn("project_name", result)
        self.assertIn("output_path", result)
        self.assertIn("timestamp", result)
        self.assertIn("status", result)
        self.assertIn("type", result)
        self.assertIn("metadata", result)
        
        # Check result values
        self.assertEqual(result["project_name"], project_name)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["type"], "hms_doc")
        self.assertEqual(result["metadata"]["abstractions_count"], len(abstractions))
        self.assertEqual(result["metadata"]["relationships_count"], len(relationships))
        
        # Check that the publication was added to the history
        self.assertEqual(len(self.coordinator.publications["hms_doc"]), 1)
        self.assertEqual(self.coordinator.publications["hms_doc"][0]["id"], result["id"])
        
        # Verify export_abstractions_to_doc was called
        mock_export.assert_called_once_with(
            abstractions=abstractions,
            relationships=relationships,
            project_name=project_name
        )

    @patch("src.coordination.doc_integration.doc_integration_service.DocIntegrationService.publish_clinical_trial")
    def test_publish_to_hms_mfe(self, mock_publish):
        """Test publishing to HMS-MFE"""
        # Mock publish_clinical_trial
        publication_id = "pub-123"
        file_path = os.path.join(self.temp_mfe_dir, "json-server", "data", f"publication_{publication_id}.json")
        writer_component = os.path.join(self.temp_mfe_dir, "src", "pages", "sidebar", "dashboards", "writer.vue")
        
        mock_publish.return_value = {
            "publication_id": publication_id,
            "file_path": file_path,
            "writer_component": writer_component,
            "status": "published",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "trial_id": "CROHNS-001",
                "abstractions_count": 2
            }
        }
        
        trial_data = self.test_data["clinical_trial"]
        abstractions = [a for a in self.test_data["abstractions"] if a["id"] in trial_data["abstraction_ids"]]
        
        result = self.coordinator.publish_to_hms_mfe(
            trial_data=trial_data,
            abstractions=abstractions
        )
        
        # Check result structure
        self.assertIn("id", result)
        self.assertIn("title", result)
        self.assertIn("timestamp", result)
        self.assertIn("status", result)
        self.assertIn("type", result)
        self.assertIn("writer_component", result)
        self.assertIn("file_path", result)
        self.assertIn("metadata", result)
        
        # Check result values
        self.assertEqual(result["id"], publication_id)
        self.assertEqual(result["title"], trial_data["title"])
        self.assertEqual(result["status"], "published")
        self.assertEqual(result["type"], "hms_mfe")
        self.assertEqual(result["writer_component"], writer_component)
        self.assertEqual(result["file_path"], file_path)
        self.assertEqual(result["metadata"]["trial_id"], trial_data["id"])
        
        # Check that the publication was added to the history
        self.assertEqual(len(self.coordinator.publications["hms_mfe"]), 1)
        self.assertEqual(self.coordinator.publications["hms_mfe"][0]["id"], publication_id)
        
        # Verify publish_clinical_trial was called
        mock_publish.assert_called_once_with(
            trial_data=trial_data,
            abstractions=abstractions,
            writer_component_path=None
        )

    @patch("src.coordination.doc_integration.doc_integration_service.DocIntegrationService.generate_integrated_documentation")
    def test_generate_integrated_documentation(self, mock_generate):
        """Test generating integrated documentation"""
        # Mock generate_integrated_documentation
        project_name = "Integrated-Test-Project"
        doc_path = os.path.join(self.temp_output_dir, project_name)
        published_trials = [{
            "publication_id": "pub-123",
            "file_path": "/some/path/publication.json",
            "writer_component": "/some/path/writer.vue",
            "status": "published",
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }]
        
        mock_generate.return_value = {
            "documentation_path": doc_path,
            "published_trials": published_trials,
            "project_name": project_name,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        clinical_trials = [self.test_data["clinical_trial"]]
        abstractions = self.test_data["abstractions"]
        relationships = self.test_data["relationships"]
        
        result = self.coordinator.generate_integrated_documentation(
            clinical_trials=clinical_trials,
            abstractions=abstractions,
            relationships=relationships,
            project_name=project_name
        )
        
        # Check result structure
        self.assertIn("id", result)
        self.assertIn("project_name", result)
        self.assertIn("timestamp", result)
        self.assertIn("status", result)
        self.assertIn("type", result)
        self.assertIn("documentation_path", result)
        self.assertIn("published_trials", result)
        self.assertIn("metadata", result)
        
        # Check result values
        self.assertEqual(result["project_name"], project_name)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["type"], "integrated")
        self.assertEqual(result["documentation_path"], doc_path)
        self.assertEqual(len(result["published_trials"]), len(published_trials))
        self.assertEqual(result["metadata"]["clinical_trials_count"], len(clinical_trials))
        self.assertEqual(result["metadata"]["abstractions_count"], len(abstractions))
        self.assertEqual(result["metadata"]["relationships_count"], len(relationships))
        
        # Check that the publication was added to the history
        self.assertEqual(len(self.coordinator.publications["integrated"]), 1)
        self.assertEqual(self.coordinator.publications["integrated"][0]["id"], result["id"])
        
        # Verify generate_integrated_documentation was called
        mock_generate.assert_called_once_with(
            clinical_trials=clinical_trials,
            abstractions=abstractions,
            relationships=relationships,
            project_name=project_name
        )

    def test_get_publications(self):
        """Test getting publications"""
        # Add some test publications
        self.coordinator.publications["hms_doc"].append({
            "id": "doc-1",
            "project_name": "Test-Project-1",
            "timestamp": "2023-05-09T12:00:00Z",
            "type": "hms_doc"
        })
        self.coordinator.publications["hms_doc"].append({
            "id": "doc-2",
            "project_name": "Test-Project-2",
            "timestamp": "2023-05-09T13:00:00Z",
            "type": "hms_doc"
        })
        self.coordinator.publications["hms_mfe"].append({
            "id": "mfe-1",
            "title": "Test Trial 1",
            "timestamp": "2023-05-09T14:00:00Z",
            "type": "hms_mfe"
        })
        
        # Test getting all publications
        all_pubs = self.coordinator.get_publications()
        self.assertEqual(len(all_pubs), 3)
        
        # Test getting publications by type
        doc_pubs = self.coordinator.get_publications(publication_type="hms_doc")
        self.assertEqual(len(doc_pubs), 2)
        
        mfe_pubs = self.coordinator.get_publications(publication_type="hms_mfe")
        self.assertEqual(len(mfe_pubs), 1)
        
        # Test getting publications with limit
        limited_pubs = self.coordinator.get_publications(limit=1)
        self.assertEqual(len(limited_pubs), 1)
        self.assertEqual(limited_pubs[0]["id"], "mfe-1")  # Should be the most recent

    def test_get_publication_by_id(self):
        """Test getting a publication by ID"""
        # Add a test publication
        pub_id = "doc-1"
        self.coordinator.publications["hms_doc"].append({
            "id": pub_id,
            "project_name": "Test-Project-1",
            "timestamp": "2023-05-09T12:00:00Z",
            "type": "hms_doc"
        })
        
        # Test getting an existing publication
        pub = self.coordinator.get_publication_by_id(pub_id)
        self.assertIsNotNone(pub)
        self.assertEqual(pub["id"], pub_id)
        
        # Test getting a non-existent publication
        non_existent_pub = self.coordinator.get_publication_by_id("non-existent")
        self.assertIsNone(non_existent_pub)

    def test_schedule_documentation_task(self):
        """Test scheduling a documentation task"""
        # Mock the internal task execution
        with patch.object(IntegrationCoordinator, '_run_task'):
            # Schedule a task
            task_type = "publish_doc"
            task_params = {
                "abstractions": self.test_data["abstractions"],
                "relationships": self.test_data["relationships"],
                "project_name": "Test-Project"
            }
            
            task_id = self.coordinator.schedule_documentation_task(task_type, task_params)
            
            # Check that the task was added to the tasks dict
            self.assertIn(task_id, self.coordinator.tasks)
            task = self.coordinator.tasks[task_id]
            
            # Check task structure
            self.assertEqual(task["id"], task_id)
            self.assertEqual(task["type"], task_type)
            self.assertEqual(task["params"], task_params)
            self.assertEqual(task["status"], "scheduled")
            self.assertIsNone(task["result"])
            self.assertIsNone(task["error"])

    def test_get_task_status(self):
        """Test getting task status"""
        # Add a test task
        task_id = "task-1"
        self.coordinator.tasks[task_id] = {
            "id": task_id,
            "type": "publish_doc",
            "status": "completed",
            "created_at": "2023-05-09T12:00:00Z",
            "updated_at": "2023-05-09T12:01:00Z",
            "result": {"some": "result"},
            "error": None
        }
        
        # Test getting an existing task
        task = self.coordinator.get_task_status(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["id"], task_id)
        self.assertEqual(task["status"], "completed")
        
        # Test getting a non-existent task
        non_existent_task = self.coordinator.get_task_status("non-existent")
        self.assertIsNone(non_existent_task)

    def test_get_all_tasks(self):
        """Test getting all tasks"""
        # Add some test tasks
        self.coordinator.tasks["task-1"] = {
            "id": "task-1",
            "type": "publish_doc",
            "status": "completed",
            "updated_at": "2023-05-09T12:01:00Z"
        }
        self.coordinator.tasks["task-2"] = {
            "id": "task-2",
            "type": "publish_mfe",
            "status": "running",
            "updated_at": "2023-05-09T12:02:00Z"
        }
        
        # Test getting all tasks
        tasks = self.coordinator.get_all_tasks()
        self.assertEqual(len(tasks), 2)
        
        # Test getting tasks with limit
        limited_tasks = self.coordinator.get_all_tasks(limit=1)
        self.assertEqual(len(limited_tasks), 1)
        self.assertEqual(limited_tasks[0]["id"], "task-2")  # Should be the most recent

    @patch("src.coordination.doc_integration.integration_coordinator.IntegrationCoordinator.publish_to_hms_doc")
    def test_run_task_publish_doc(self, mock_publish):
        """Test running a publish_doc task"""
        # Mock publish_to_hms_doc
        mock_result = {
            "id": "doc-1",
            "project_name": "Test-Project",
            "output_path": "/some/path",
            "status": "completed"
        }
        mock_publish.return_value = mock_result
        
        # Add a test task
        task_id = "task-1"
        task_type = "publish_doc"
        task_params = {
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Test-Project"
        }
        
        self.coordinator.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "params": task_params,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Run the task
        self.coordinator._run_task(task_id)
        
        # Check that the task was updated
        task = self.coordinator.tasks[task_id]
        self.assertEqual(task["status"], "completed")
        self.assertEqual(task["result"], mock_result)
        self.assertIsNone(task["error"])
        
        # Verify publish_to_hms_doc was called
        mock_publish.assert_called_once_with(**task_params)

    @patch("src.coordination.doc_integration.integration_coordinator.IntegrationCoordinator.publish_to_hms_mfe")
    def test_run_task_publish_mfe(self, mock_publish):
        """Test running a publish_mfe task"""
        # Mock publish_to_hms_mfe
        mock_result = {
            "id": "mfe-1",
            "title": "Test Trial",
            "status": "published"
        }
        mock_publish.return_value = mock_result
        
        # Add a test task
        task_id = "task-2"
        task_type = "publish_mfe"
        task_params = {
            "trial_data": self.test_data["clinical_trial"],
            "abstractions": [a for a in self.test_data["abstractions"] if a["id"] in self.test_data["clinical_trial"]["abstraction_ids"]]
        }
        
        self.coordinator.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "params": task_params,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Run the task
        self.coordinator._run_task(task_id)
        
        # Check that the task was updated
        task = self.coordinator.tasks[task_id]
        self.assertEqual(task["status"], "completed")
        self.assertEqual(task["result"], mock_result)
        self.assertIsNone(task["error"])
        
        # Verify publish_to_hms_mfe was called
        mock_publish.assert_called_once_with(**task_params)

    @patch("src.coordination.doc_integration.integration_coordinator.IntegrationCoordinator.generate_integrated_documentation")
    def test_run_task_generate_integrated(self, mock_generate):
        """Test running a generate_integrated task"""
        # Mock generate_integrated_documentation
        mock_result = {
            "id": "integrated-1",
            "project_name": "Integrated-Test-Project",
            "documentation_path": "/some/path",
            "status": "completed"
        }
        mock_generate.return_value = mock_result
        
        # Add a test task
        task_id = "task-3"
        task_type = "generate_integrated"
        task_params = {
            "clinical_trials": [self.test_data["clinical_trial"]],
            "abstractions": self.test_data["abstractions"],
            "relationships": self.test_data["relationships"],
            "project_name": "Integrated-Test-Project"
        }
        
        self.coordinator.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "params": task_params,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Run the task
        self.coordinator._run_task(task_id)
        
        # Check that the task was updated
        task = self.coordinator.tasks[task_id]
        self.assertEqual(task["status"], "completed")
        self.assertEqual(task["result"], mock_result)
        self.assertIsNone(task["error"])
        
        # Verify generate_integrated_documentation was called
        mock_generate.assert_called_once_with(**task_params)

    def test_run_task_unknown_type(self):
        """Test running a task with an unknown type"""
        # Add a test task with an unknown type
        task_id = "task-4"
        task_type = "unknown_type"
        
        self.coordinator.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "params": {},
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Run the task
        self.coordinator._run_task(task_id)
        
        # Check that the task was updated with an error
        task = self.coordinator.tasks[task_id]
        self.assertEqual(task["status"], "failed")
        self.assertIsNone(task["result"])
        self.assertIn("Unknown task type", task["error"])

    def test_run_task_exception(self):
        """Test running a task that raises an exception"""
        # Mock publish_to_hms_doc to raise an exception
        with patch.object(IntegrationCoordinator, 'publish_to_hms_doc') as mock_publish:
            mock_publish.side_effect = Exception("Test exception")
            
            # Add a test task
            task_id = "task-5"
            task_type = "publish_doc"
            
            self.coordinator.tasks[task_id] = {
                "id": task_id,
                "type": task_type,
                "params": {},
                "status": "scheduled",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "result": None,
                "error": None
            }
            
            # Run the task
            self.coordinator._run_task(task_id)
            
            # Check that the task was updated with an error
            task = self.coordinator.tasks[task_id]
            self.assertEqual(task["status"], "failed")
            self.assertIsNone(task["result"])
            self.assertEqual(task["error"], "Test exception")

if __name__ == '__main__':
    unittest.main()