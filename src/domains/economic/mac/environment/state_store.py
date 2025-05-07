"""
State Store implementation for the MAC architecture.

The StateStore provides persistent memory across agent interactions, including:
- Task tracking and history management
- Shared knowledge repository
- Event logging and notification
- State snapshotting and recovery
"""

from typing import Dict, Any, List, Optional, Callable
import json
import os
import time
import logging
import asyncio
from threading import Lock
from uuid import uuid4
import copy

class StateStore:
    """
    Environment/State Store for the MAC architecture.
    
    The StateStore provides persistent memory and state tracking for MAC operations,
    enabling consistent task tracking, history management, and shared knowledge
    across the system.
    """
    
    def __init__(self, 
                persistence_dir: Optional[str] = None,
                max_history_length: int = 1000,
                auto_persist: bool = True):
        """
        Initialize the Environment/State Store.
        
        Args:
            persistence_dir: Directory to store persistent state snapshots
            max_history_length: Maximum number of events to keep in history
            auto_persist: Whether to automatically persist state on updates
        """
        # Set up persistence directory
        self.persistence_dir = persistence_dir
        if persistence_dir and not os.path.exists(persistence_dir):
            os.makedirs(persistence_dir)
        
        self.max_history_length = max_history_length
        self.auto_persist = auto_persist
        
        # Initialize state
        self.state = {
            "tasks": {},            # Task data and metadata
            "agents": {},           # Agent registry
            "events": [],           # Event history
            "snapshots": {},        # State snapshots
            "knowledge": {}         # Shared knowledge repository
        }
        
        # Thread safety
        self.lock = Lock()
        
        # Event listeners
        self.event_listeners = []
        
        # Supervisor reference (set later)
        self.supervisor = None
        
        # Set up logging
        self.logger = logging.getLogger("MAC.StateStore")
        self.logger.info("Initialized MAC Environment/State Store")
    
    def register_supervisor(self, supervisor) -> None:
        """
        Register the supervisor agent with the state store.
        
        Args:
            supervisor: The MAC Supervisor Agent
        """
        self.supervisor = supervisor
    
    def register_agent(self, agent_id: str, agent_type: str, metadata: Dict[str, Any]) -> None:
        """
        Register an agent in the state store.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent (e.g., "supervisor", "domain", "component")
            metadata: Additional agent metadata
        """
        with self.lock:
            self.state["agents"][agent_id] = {
                "id": agent_id,
                "type": agent_type,
                "metadata": metadata,
                "registration_time": time.time()
            }
        
        self._publish_event("agent_registered", {
            "agent_id": agent_id,
            "agent_type": agent_type
        })
        
        self.logger.info(f"Registered agent {agent_id} of type {agent_type}")
    
    def record_task(self, task_data: Dict[str, Any]) -> None:
        """
        Record a new task in the state store.
        
        Args:
            task_data: Task data including ID, description, and metadata
        """
        task_id = task_data["id"]
        
        with self.lock:
            self.state["tasks"][task_id] = {
                "data": task_data,
                "status": "created",
                "created_at": time.time(),
                "updated_at": time.time(),
                "subtasks": [],
                "analysis": {},
                "results": None,
                "history": [{
                    "status": "created",
                    "timestamp": time.time()
                }]
            }
        
        self._publish_event("task_created", {
            "task_id": task_id,
            "description": task_data.get("description", "")
        })
        
        self.logger.info(f"Recorded task {task_id}")
        self._persist_if_enabled()
    
    def update_task_status(self, task_id: str, status: str) -> None:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task to update
            status: New status (e.g., "in_progress", "completed", "failed")
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to update unknown task {task_id}")
                return
                
            self.state["tasks"][task_id]["status"] = status
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": status,
                "timestamp": time.time()
            })
        
        self._publish_event("task_status_updated", {
            "task_id": task_id,
            "status": status
        })
        
        self.logger.info(f"Updated task {task_id} status to {status}")
        self._persist_if_enabled()
    
    def record_task_decomposition(self, task_id: str, subtask_ids: List[str]) -> None:
        """
        Record task decomposition details.
        
        Args:
            task_id: ID of the parent task
            subtask_ids: List of subtask IDs
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to record decomposition for unknown task {task_id}")
                return
                
            self.state["tasks"][task_id]["subtasks"] = subtask_ids
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "decomposed",
                "timestamp": time.time(),
                "subtasks": subtask_ids
            })
        
        self._publish_event("task_decomposed", {
            "task_id": task_id,
            "subtask_count": len(subtask_ids),
            "subtask_ids": subtask_ids
        })
        
        self.logger.info(f"Recorded decomposition of task {task_id} into {len(subtask_ids)} subtasks")
        self._persist_if_enabled()
    
    def assign_task(self, task_id: str, domain: str) -> None:
        """
        Record task assignment to a domain.
        
        Args:
            task_id: ID of the task to assign
            domain: Domain name to assign the task to
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to assign unknown task {task_id}")
                return
                
            self.state["tasks"][task_id]["domain"] = domain
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "assigned",
                "timestamp": time.time(),
                "domain": domain
            })
        
        self._publish_event("task_assigned", {
            "task_id": task_id,
            "domain": domain
        })
        
        self.logger.info(f"Assigned task {task_id} to domain {domain}")
        self._persist_if_enabled()
    
    def record_task_analysis(self, task_id: str, analysis: Dict[str, Any]) -> None:
        """
        Record domain analysis for a task.
        
        Args:
            task_id: ID of the task
            analysis: Analysis data from a domain agent
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to record analysis for unknown task {task_id}")
                return
                
            self.state["tasks"][task_id]["analysis"] = analysis
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "analyzed",
                "timestamp": time.time()
            })
        
        self._publish_event("task_analyzed", {
            "task_id": task_id
        })
        
        self.logger.info(f"Recorded analysis for task {task_id}")
        self._persist_if_enabled()
    
    def record_component_delegation(self, task_id: str, component: str, component_task_id: str) -> None:
        """
        Record delegation of a task to a component agent.
        
        Args:
            task_id: ID of the parent task
            component: Name of the component
            component_task_id: ID of the component-specific task
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to record delegation for unknown task {task_id}")
                return
                
            if "component_delegations" not in self.state["tasks"][task_id]:
                self.state["tasks"][task_id]["component_delegations"] = {}
                
            self.state["tasks"][task_id]["component_delegations"][component] = component_task_id
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "component_delegated",
                "timestamp": time.time(),
                "component": component,
                "component_task_id": component_task_id
            })
        
        self._publish_event("component_delegated", {
            "task_id": task_id,
            "component": component,
            "component_task_id": component_task_id
        })
        
        self.logger.info(f"Recorded delegation of task {task_id} to component {component}")
        self._persist_if_enabled()
    
    def record_component_result(self, component_task_id: str, result: Dict[str, Any]) -> None:
        """
        Record the result from a component agent.
        
        Args:
            component_task_id: ID of the component-specific task
            result: Result data from the component
        """
        with self.lock:
            task_id = None
            # Find the parent task
            for tid, task_data in self.state["tasks"].items():
                if "component_delegations" in task_data:
                    for comp, comp_id in task_data["component_delegations"].items():
                        if comp_id == component_task_id:
                            task_id = tid
                            break
                    if task_id:
                        break
            
            if not task_id:
                self.logger.warning(f"Could not find parent task for component task {component_task_id}")
                return
                
            if "component_results" not in self.state["tasks"][task_id]:
                self.state["tasks"][task_id]["component_results"] = {}
                
            self.state["tasks"][task_id]["component_results"][component_task_id] = result
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "component_result_received",
                "timestamp": time.time(),
                "component_task_id": component_task_id
            })
        
        self._publish_event("component_result_received", {
            "component_task_id": component_task_id
        })
        
        self.logger.info(f"Recorded result for component task {component_task_id}")
        self._persist_if_enabled()
    
    def record_domain_synthesis(self, task_id: str, domain: str, result: Dict[str, Any]) -> None:
        """
        Record domain-level synthesis result.
        
        Args:
            task_id: ID of the task
            domain: Domain name
            result: Synthesis result from the domain
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to record domain synthesis for unknown task {task_id}")
                return
                
            if "domain_results" not in self.state["tasks"][task_id]:
                self.state["tasks"][task_id]["domain_results"] = {}
                
            self.state["tasks"][task_id]["domain_results"][domain] = result
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "domain_synthesis_completed",
                "timestamp": time.time(),
                "domain": domain
            })
        
        self._publish_event("domain_synthesis_completed", {
            "task_id": task_id,
            "domain": domain
        })
        
        self.logger.info(f"Recorded domain synthesis for task {task_id} in domain {domain}")
        self._persist_if_enabled()
    
    def record_task_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Record the final result for a task.
        
        Args:
            task_id: ID of the task
            result: Final task result
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to record result for unknown task {task_id}")
                return
                
            self.state["tasks"][task_id]["results"] = result
            self.state["tasks"][task_id]["status"] = "completed"
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "completed",
                "timestamp": time.time()
            })
        
        self._publish_event("task_completed", {
            "task_id": task_id
        })
        
        self.logger.info(f"Recorded result for task {task_id}")
        self._persist_if_enabled()
    
    def record_task_synthesis(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Record the synthesized result from multiple domains.
        
        Args:
            task_id: ID of the task
            result: Synthesized result
        """
        with self.lock:
            if task_id not in self.state["tasks"]:
                self.logger.warning(f"Attempted to record synthesis for unknown task {task_id}")
                return
                
            self.state["tasks"][task_id]["results"] = result
            self.state["tasks"][task_id]["status"] = "synthesized"
            self.state["tasks"][task_id]["updated_at"] = time.time()
            self.state["tasks"][task_id]["history"].append({
                "status": "synthesized",
                "timestamp": time.time()
            })
        
        self._publish_event("task_synthesized", {
            "task_id": task_id
        })
        
        self.logger.info(f"Recorded synthesis for task {task_id}")
        self._persist_if_enabled()
    
    def add_shared_knowledge(self, key: str, value: Any, domain: Optional[str] = None) -> None:
        """
        Add or update shared knowledge in the repository.
        
        Args:
            key: Knowledge key
            value: Knowledge value
            domain: Optional domain to scope the knowledge (None for global)
        """
        with self.lock:
            if domain:
                if domain not in self.state["knowledge"]:
                    self.state["knowledge"][domain] = {}
                self.state["knowledge"][domain][key] = value
            else:
                # Global knowledge
                self.state["knowledge"][key] = value
        
        self._publish_event("knowledge_updated", {
            "key": key,
            "domain": domain
        })
        
        self.logger.info(f"Added shared knowledge: {key}" + (f" (domain: {domain})" if domain else ""))
        self._persist_if_enabled()
    
    def get_shared_knowledge(self, key: str, domain: Optional[str] = None, default: Any = None) -> Any:
        """
        Retrieve shared knowledge from the repository.
        
        Args:
            key: Knowledge key
            domain: Optional domain to scope the knowledge (None for global)
            default: Default value if key not found
            
        Returns:
            Knowledge value or default if not found
        """
        with self.lock:
            if domain:
                if domain in self.state["knowledge"]:
                    return self.state["knowledge"][domain].get(key, default)
                return default
            else:
                # Global knowledge
                return self.state["knowledge"].get(key, default)
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get all data for a specific task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task data or None if not found
        """
        with self.lock:
            return self.state["tasks"].get(task_id)
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of tasks with the specified status
        """
        with self.lock:
            return [
                task for task_id, task in self.state["tasks"].items()
                if task["status"] == status
            ]
    
    def get_tasks_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get all tasks assigned to a specific domain.
        
        Args:
            domain: Domain to filter by
            
        Returns:
            List of tasks assigned to the specified domain
        """
        with self.lock:
            return [
                task for task_id, task in self.state["tasks"].items()
                if task.get("domain") == domain
            ]
    
    def create_snapshot(self) -> str:
        """
        Create a snapshot of the current state.
        
        Returns:
            Snapshot ID
        """
        snapshot_id = f"snapshot_{uuid4().hex}"
        
        with self.lock:
            # Deep copy of current state
            snapshot = copy.deepcopy(self.state)
            
            # Store snapshot
            self.state["snapshots"][snapshot_id] = {
                "data": snapshot,
                "created_at": time.time()
            }
        
        self._publish_event("snapshot_created", {
            "snapshot_id": snapshot_id
        })
        
        self.logger.info(f"Created snapshot {snapshot_id}")
        self._persist_if_enabled()
        
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore state from a snapshot.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if snapshot_id not in self.state["snapshots"]:
                self.logger.warning(f"Attempted to restore unknown snapshot {snapshot_id}")
                return False
                
            # Restore state
            snapshot_data = self.state["snapshots"][snapshot_id]["data"]
            
            # Keep existing snapshots
            existing_snapshots = self.state["snapshots"]
            
            # Replace state with snapshot
            self.state = snapshot_data
            
            # Restore snapshots collection
            self.state["snapshots"] = existing_snapshots
        
        self._publish_event("snapshot_restored", {
            "snapshot_id": snapshot_id
        })
        
        self.logger.info(f"Restored snapshot {snapshot_id}")
        self._persist_if_enabled()
        
        return True
    
    def on_state_change(self, callback: Callable[[Dict[str, Any]], None]) -> int:
        """
        Register a listener for state changes.
        
        Args:
            callback: Function to call on state change
            
        Returns:
            Listener ID for later removal
        """
        listener_id = len(self.event_listeners)
        self.event_listeners.append(callback)
        return listener_id
    
    def remove_listener(self, listener_id: int) -> None:
        """
        Remove a state change listener.
        
        Args:
            listener_id: ID returned from on_state_change
        """
        if 0 <= listener_id < len(self.event_listeners):
            self.event_listeners.pop(listener_id)
    
    def _publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Publish an event to all listeners.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": time.time()
        }
        
        # Add to events log
        with self.lock:
            self.state["events"].append(event)
            
            # Trim events if necessary
            if len(self.state["events"]) > self.max_history_length:
                self.state["events"] = self.state["events"][-self.max_history_length:]
        
        # Notify listeners
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error in event listener: {str(e)}")
    
    def _persist_if_enabled(self) -> None:
        """Persist state to disk if auto_persist is enabled."""
        if not self.auto_persist or not self.persistence_dir:
            return
            
        # Create a timestamped backup path
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(self.persistence_dir, f"state-{timestamp}.json")
        
        # Write state to file
        with open(backup_path, 'w') as f:
            json.dump(self.state, f, indent=2)
        
        # Also update the latest version
        latest_path = os.path.join(self.persistence_dir, "state-latest.json")
        with open(latest_path, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def persist(self, path: Optional[str] = None) -> None:
        """
        Manually persist state to disk.
        
        Args:
            path: Optional path to save state (uses default if None)
        """
        if not self.persistence_dir and not path:
            self.logger.warning("No persistence directory configured")
            return
            
        save_path = path or os.path.join(self.persistence_dir, f"state-manual-{time.strftime('%Y%m%d-%H%M%S')}.json")
        
        with self.lock:
            with open(save_path, 'w') as f:
                json.dump(self.state, f, indent=2)
                
        self.logger.info(f"Manually persisted state to {save_path}")
    
    def load(self, path: str) -> bool:
        """
        Load state from disk.
        
        Args:
            path: Path to load state from
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(path):
            self.logger.error(f"State file not found: {path}")
            return False
            
        try:
            with open(path, 'r') as f:
                loaded_state = json.load(f)
                
            with self.lock:
                self.state = loaded_state
                
            self.logger.info(f"Loaded state from {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading state: {str(e)}")
            return False