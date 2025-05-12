"""
Integration Coordinator

This module coordinates the integration between various components of the Crohn's Treatment System,
HMS-DOC, and HMS-MFE. It provides a high-level interface for managing documentation generation
and publication workflows.
"""

import os
import json
import logging
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .doc_integration_service import DocIntegrationService, create_doc_integration_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationCoordinator:
    """
    Coordinates integration between Crohn's Treatment System, HMS-DOC, and HMS-MFE.
    
    This class provides a high-level interface for:
    - Scheduling documentation generation tasks
    - Tracking integration status
    - Managing document and publication workflows
    - Coordinating between different HMS components
    """
    
    def __init__(self, doc_integration_service: DocIntegrationService = None):
        """
        Initialize the integration coordinator.
        
        Args:
            doc_integration_service: DocIntegrationService instance, created if not provided
        """
        self.doc_service = doc_integration_service or create_doc_integration_service()
        
        # Initialize publication tracking
        self.publication_history_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "publication_history.json"
        )
        self.publications = self._load_publication_history()
        
        # Task management
        self.tasks = {}
        self.task_lock = threading.Lock()
        
        # System status
        self.hms_doc_status = "disconnected"
        self.hms_mfe_status = "disconnected"
        self._update_system_status()
    
    def _load_publication_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load publication history from JSON file"""
        try:
            if os.path.exists(self.publication_history_file):
                with open(self.publication_history_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "hms_doc": [],
                    "hms_mfe": [],
                    "integrated": []
                }
        except Exception as e:
            logger.error(f"Error loading publication history: {e}")
            return {
                "hms_doc": [],
                "hms_mfe": [],
                "integrated": []
            }
    
    def _save_publication_history(self):
        """Save publication history to JSON file"""
        try:
            with open(self.publication_history_file, 'w') as f:
                json.dump(self.publications, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving publication history: {e}")
    
    def _update_system_status(self):
        """Check and update the connection status of HMS components"""
        # Check HMS-DOC status
        if os.path.exists(self.doc_service.doc_root_path):
            self.hms_doc_status = "connected"
        else:
            self.hms_doc_status = "disconnected"
        
        # Check HMS-MFE status
        if os.path.exists(self.doc_service.mfe_root_path):
            self.hms_mfe_status = "connected"
        else:
            self.hms_mfe_status = "disconnected"
    
    def get_system_status(self) -> Dict[str, str]:
        """
        Get the current status of HMS system components
        
        Returns:
            Dictionary with component status information
        """
        self._update_system_status()
        return {
            "hms_doc": self.hms_doc_status,
            "hms_mfe": self.hms_mfe_status,
            "timestamp": datetime.now().isoformat(),
            "doc_publications_count": len(self.publications["hms_doc"]),
            "mfe_publications_count": len(self.publications["hms_mfe"]),
            "integrated_publications_count": len(self.publications["integrated"])
        }
    
    def publish_to_hms_doc(self, 
                          abstractions: List[Dict[str, Any]], 
                          relationships: List[Dict[str, Any]],
                          project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Publish abstractions and relationships to HMS-DOC
        
        Args:
            abstractions: List of abstraction objects
            relationships: List of relationship objects
            project_name: Name for the project documentation
            
        Returns:
            Publication information
        """
        try:
            # Generate project name if not provided
            if not project_name:
                project_name = f"Crohns-Abstractions-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Export to HMS-DOC
            output_path = self.doc_service.export_abstractions_to_doc(
                abstractions=abstractions,
                relationships=relationships,
                project_name=project_name
            )
            
            # Create publication record
            publication = {
                "id": f"doc-{int(time.time())}",
                "project_name": project_name,
                "output_path": output_path,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "type": "hms_doc",
                "metadata": {
                    "abstractions_count": len(abstractions),
                    "relationships_count": len(relationships)
                }
            }
            
            # Update publication history
            self.publications["hms_doc"].append(publication)
            self._save_publication_history()
            
            logger.info(f"Published to HMS-DOC: {output_path}")
            return publication
            
        except Exception as e:
            logger.error(f"Error publishing to HMS-DOC: {e}")
            raise
    
    def publish_to_hms_mfe(self,
                         trial_data: Dict[str, Any],
                         abstractions: List[Dict[str, Any]],
                         writer_component_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Publish clinical trial data to HMS-MFE
        
        Args:
            trial_data: Clinical trial data
            abstractions: Related abstractions
            writer_component_path: Path to writer component
            
        Returns:
            Publication information
        """
        try:
            # Publish to HMS-MFE
            publication_info = self.doc_service.publish_clinical_trial(
                trial_data=trial_data,
                abstractions=abstractions,
                writer_component_path=writer_component_path
            )
            
            # Create publication record
            publication = {
                "id": publication_info["publication_id"],
                "title": trial_data.get("title", "Untitled Clinical Trial"),
                "timestamp": datetime.now().isoformat(),
                "status": "published",
                "type": "hms_mfe",
                "writer_component": publication_info["writer_component"],
                "file_path": publication_info["file_path"],
                "metadata": {
                    "trial_id": trial_data.get("id", ""),
                    "abstractions_count": len(abstractions)
                }
            }
            
            # Update publication history
            self.publications["hms_mfe"].append(publication)
            self._save_publication_history()
            
            logger.info(f"Published to HMS-MFE: {publication_info['file_path']}")
            return publication
            
        except Exception as e:
            logger.error(f"Error publishing to HMS-MFE: {e}")
            raise
    
    def generate_integrated_documentation(self,
                                        clinical_trials: List[Dict[str, Any]],
                                        abstractions: List[Dict[str, Any]],
                                        relationships: List[Dict[str, Any]],
                                        project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive documentation integrating HMS-DOC and HMS-MFE
        
        Args:
            clinical_trials: List of clinical trial data
            abstractions: List of abstraction objects
            relationships: List of relationship objects
            project_name: Name for the documentation project
            
        Returns:
            Integrated documentation information
        """
        try:
            # Generate project name if not provided
            if not project_name:
                project_name = f"Integrated-Documentation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Generate integrated documentation
            doc_info = self.doc_service.generate_integrated_documentation(
                clinical_trials=clinical_trials,
                abstractions=abstractions,
                relationships=relationships,
                project_name=project_name
            )
            
            # Create publication record
            publication = {
                "id": f"integrated-{int(time.time())}",
                "project_name": project_name,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "type": "integrated",
                "documentation_path": doc_info["documentation_path"],
                "published_trials": doc_info["published_trials"],
                "metadata": {
                    "clinical_trials_count": len(clinical_trials),
                    "abstractions_count": len(abstractions),
                    "relationships_count": len(relationships)
                }
            }
            
            # Update publication history
            self.publications["integrated"].append(publication)
            self._save_publication_history()
            
            logger.info(f"Generated integrated documentation: {doc_info['documentation_path']}")
            return publication
            
        except Exception as e:
            logger.error(f"Error generating integrated documentation: {e}")
            raise
    
    def get_publications(self, 
                        publication_type: Optional[str] = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get a list of publications
        
        Args:
            publication_type: Type of publications to retrieve (hms_doc, hms_mfe, integrated)
            limit: Maximum number of publications to return
            
        Returns:
            List of publication information
        """
        if publication_type and publication_type in self.publications:
            # Sort by timestamp (most recent first) and limit
            publications = sorted(
                self.publications[publication_type],
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )
            return publications[:limit]
        elif not publication_type:
            # Return all publications, sorted and limited
            all_publications = []
            for pub_type in self.publications:
                all_publications.extend(self.publications[pub_type])
            
            # Sort by timestamp (most recent first) and limit
            all_publications = sorted(
                all_publications,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )
            return all_publications[:limit]
        else:
            return []
    
    def get_publication_by_id(self, publication_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a publication by ID
        
        Args:
            publication_id: ID of the publication to retrieve
            
        Returns:
            Publication information if found, None otherwise
        """
        for pub_type in self.publications:
            for publication in self.publications[pub_type]:
                if publication.get("id") == publication_id:
                    return publication
        return None
    
    def schedule_documentation_task(self, 
                                   task_type: str,
                                   task_params: Dict[str, Any]) -> str:
        """
        Schedule a documentation task to run asynchronously
        
        Args:
            task_type: Type of task (publish_doc, publish_mfe, generate_integrated)
            task_params: Parameters for the task
            
        Returns:
            Task ID
        """
        task_id = f"{task_type}-{int(time.time())}"
        
        with self.task_lock:
            self.tasks[task_id] = {
                "id": task_id,
                "type": task_type,
                "params": task_params,
                "status": "scheduled",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "result": None,
                "error": None
            }
        
        # Start task in a background thread
        thread = threading.Thread(
            target=self._run_task,
            args=(task_id,),
            daemon=True
        )
        thread.start()
        
        return task_id
    
    def _run_task(self, task_id: str):
        """
        Run a scheduled task
        
        Args:
            task_id: ID of the task to run
        """
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            # Update task status
            with self.task_lock:
                self.tasks[task_id]["status"] = "running"
                self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            
            # Run the task based on type
            if task["type"] == "publish_doc":
                result = self.publish_to_hms_doc(**task["params"])
            elif task["type"] == "publish_mfe":
                result = self.publish_to_hms_mfe(**task["params"])
            elif task["type"] == "generate_integrated":
                result = self.generate_integrated_documentation(**task["params"])
            else:
                raise ValueError(f"Unknown task type: {task['type']}")
            
            # Update task with result
            with self.task_lock:
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
                self.tasks[task_id]["result"] = result
                
        except Exception as e:
            logger.error(f"Error running task {task_id}: {e}")
            
            # Update task with error
            with self.task_lock:
                self.tasks[task_id]["status"] = "failed"
                self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
                self.tasks[task_id]["error"] = str(e)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a scheduled task
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Task status information if found, None otherwise
        """
        with self.task_lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get a list of all tasks
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of task information
        """
        with self.task_lock:
            # Sort by updated_at (most recent first) and limit
            tasks = sorted(
                list(self.tasks.values()),
                key=lambda x: x.get("updated_at", ""),
                reverse=True
            )
            return tasks[:limit]

# Create a singleton instance for easy import
coordinator = IntegrationCoordinator()