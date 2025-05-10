"""
Visualization components for the MAC Demo.

This module provides visualization components for the MAC Demo,
including collaboration graphs, timelines, and state monitoring.
"""

import logging
import os
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from threading import Thread, Event

from a2a.core import TaskResult
from mac.environment.state_store import StateStore
from mac.utils.visualization import visualize_collaboration

class MACCollaborationVisualizer:
    """
    Visualizer for MAC collaboration.
    
    This class provides real-time visualization of MAC collaboration,
    including collaboration graphs, task timelines, and state monitoring.
    """
    
    def __init__(
        self,
        state_store: StateStore,
        output_dir: str = "visualizations",
        update_interval: float = 2.0,
        formats: List[str] = ["text", "mermaid"]
    ):
        """
        Initialize the MAC Collaboration Visualizer.
        
        Args:
            state_store: Environment/State Store
            output_dir: Directory to save visualizations
            update_interval: Interval between visualization updates (seconds)
            formats: List of visualization formats
        """
        self.state_store = state_store
        self.output_dir = output_dir
        self.update_interval = update_interval
        self.formats = formats
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("MAC.Demo.Visualizer")
        
        # Background thread for updates
        self.update_thread = None
        self.stop_event = Event()
        
        # Event listener ID
        self.listener_id = None
        
        self.logger.info(f"MAC Collaboration Visualizer initialized with output directory: {output_dir}")
    
    def start(self) -> bool:
        """
        Start the visualizer.
        
        Returns:
            True if started, False otherwise
        """
        if self.update_thread and self.update_thread.is_alive():
            self.logger.warning("Visualizer already running")
            return False
        
        # Reset stop event
        self.stop_event.clear()
        
        # Register event listener
        self.listener_id = self.state_store.on_state_change(self._on_state_change)
        
        # Start update thread
        self.update_thread = Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        self.logger.info("MAC Collaboration Visualizer started")
        return True
    
    def stop(self) -> None:
        """Stop the visualizer."""
        if not self.update_thread or not self.update_thread.is_alive():
            return
        
        # Signal thread to stop
        self.stop_event.set()
        
        # Remove event listener
        if self.listener_id is not None:
            self.state_store.remove_listener(self.listener_id)
            self.listener_id = None
        
        # Wait for thread to exit
        self.update_thread.join(timeout=5.0)
        
        self.logger.info("MAC Collaboration Visualizer stopped")
    
    def create_snapshot(self) -> Dict[str, str]:
        """
        Create a snapshot of visualizations.
        
        Returns:
            Dictionary mapping format names to file paths
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        snapshot_files = {}
        
        # Get current state
        with self.state_store.lock:
            tasks = self.state_store.state["tasks"]
            domains = [
                agent_data["metadata"]["domain"]
                for agent_id, agent_data in self.state_store.state["agents"].items()
                if agent_data["type"] == "domain"
            ]
        
        # Create visualizations in each format
        for format_type in self.formats:
            file_name = f"visualization_{timestamp}.{format_type}"
            file_path = os.path.join(self.output_dir, file_name)
            
            visualization = visualize_collaboration(
                tasks=tasks,
                domains=domains,
                format_type=format_type,
                output_file=file_path
            )
            
            snapshot_files[format_type] = file_path
            
        self.logger.info(f"Created visualization snapshot: {timestamp}")
        return snapshot_files
    
    def create_final_visualization(self, task_id: str, result: TaskResult) -> Dict[str, str]:
        """
        Create a final visualization for a completed task.
        
        Args:
            task_id: Task ID
            result: Task result
            
        Returns:
            Dictionary mapping format names to file paths
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        final_files = {}
        
        # Get current state
        with self.state_store.lock:
            tasks = self.state_store.state["tasks"]
            domains = [
                agent_data["metadata"]["domain"]
                for agent_id, agent_data in self.state_store.state["agents"].items()
                if agent_data["type"] == "domain"
            ]
        
        # Create directory for final visualizations
        final_dir = os.path.join(self.output_dir, f"final_{task_id}")
        os.makedirs(final_dir, exist_ok=True)
        
        # Create visualizations in each format
        for format_type in self.formats:
            file_name = f"final_visualization_{timestamp}.{format_type}"
            file_path = os.path.join(final_dir, file_name)
            
            visualization = visualize_collaboration(
                tasks=tasks,
                domains=domains,
                format_type=format_type,
                output_file=file_path
            )
            
            final_files[format_type] = file_path
        
        # Create result summary
        summary_path = os.path.join(final_dir, f"result_summary_{timestamp}.json")
        with open(summary_path, 'w') as f:
            json.dump({
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
                "metadata": result.metadata
            }, f, indent=2)
        
        final_files["summary"] = summary_path
        
        self.logger.info(f"Created final visualization for task {task_id}")
        return final_files
    
    def _update_loop(self) -> None:
        """Background thread for periodic visualization updates."""
        while not self.stop_event.is_set():
            try:
                # Create visualizations
                self.create_snapshot()
                
                # Wait for next update
                self.stop_event.wait(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in visualization update: {str(e)}")
                # Wait a bit before trying again
                self.stop_event.wait(5.0)
    
    def _on_state_change(self, event: Dict[str, Any]) -> None:
        """
        Handle state change events.
        
        Args:
            event: State change event
        """
        # React to specific events
        event_type = event.get("type")
        
        if event_type in ["task_completed", "task_synthesized"]:
            # Create a snapshot when a task is completed
            try:
                self.create_snapshot()
            except Exception as e:
                self.logger.error(f"Error creating snapshot on event {event_type}: {str(e)}")


# Factory function for creating a visualizer
def create_visualizer(
    state_store: StateStore,
    config_path: Optional[str] = None
) -> MACCollaborationVisualizer:
    """
    Create and configure a MAC Collaboration Visualizer.
    
    Args:
        state_store: Environment/State Store
        config_path: Path to configuration file
        
    Returns:
        Configured MACCollaborationVisualizer
    """
    # Load configuration if path provided
    config = {}
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading visualizer configuration: {str(e)}")
    
    # Get visualization configuration
    vis_config = config.get("visualization", {})
    output_dir = vis_config.get("output_dir", "visualizations")
    update_interval = vis_config.get("update_interval", 2.0)
    formats = vis_config.get("formats", ["text", "mermaid"])
    
    # Create visualizer
    visualizer = MACCollaborationVisualizer(
        state_store=state_store,
        output_dir=output_dir,
        update_interval=update_interval,
        formats=formats
    )
    
    return visualizer