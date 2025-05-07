"""
Human Query Interface implementation for the MAC architecture.

The Human Query Interface provides mechanisms for human oversight and intervention,
enabling transparent decision inspection, feedback incorporation, and governance.
"""

from typing import Dict, Any, Optional, List, Callable
import logging
import asyncio
import time
import json
import os
from threading import Lock, Event
from uuid import uuid4

class HumanQueryInterface:
    """
    Human Query Interface for the MAC architecture.
    
    Provides mechanisms for human-in-the-loop intervention and oversight
    through various interface types (file, API, console).
    """
    
    def __init__(
        self, 
        interface_type: str = "file",
        interface_config: Optional[Dict[str, Any]] = None,
        auto_approve_timeout: Optional[float] = None
    ):
        """
        Initialize the Human Query Interface.
        
        Args:
            interface_type: Interface type ("file", "api", "console")
            interface_config: Interface-specific configuration
            auto_approve_timeout: Timeout after which queries are auto-approved (None for no timeout)
        """
        self.interface_type = interface_type
        self.interface_config = interface_config or {}
        self.auto_approve_timeout = auto_approve_timeout
        
        # Pending queries
        self.pending_queries = {}
        self.query_lock = Lock()
        
        # Set up logging
        self.logger = logging.getLogger("MAC.HumanInterface")
        
        # Set up interface
        if interface_type == "file":
            self._setup_file_interface()
        elif interface_type == "api":
            self._setup_api_interface()
        elif interface_type == "console":
            self._setup_console_interface()
        else:
            raise ValueError(f"Unsupported interface type: {interface_type}")
            
        self.logger.info(f"Initialized MAC Human Query Interface ({interface_type})")
    
    def _setup_file_interface(self) -> None:
        """Set up file-based interface."""
        # Get directory paths
        query_dir = self.interface_config.get("query_dir", "human_queries")
        response_dir = self.interface_config.get("response_dir", "human_responses")
        
        # Create directories if they don't exist
        for dir_path in [query_dir, response_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                
        self.query_dir = query_dir
        self.response_dir = response_dir
        
        self.logger.info(f"File interface set up with query directory: {query_dir}")
    
    def _setup_api_interface(self) -> None:
        """Set up API-based interface."""
        # Get API configuration
        self.api_endpoint = self.interface_config.get("api_endpoint", "http://localhost:5000/query")
        self.api_key = self.interface_config.get("api_key")
        self.api_timeout = self.interface_config.get("api_timeout", 30)
        
        # Import requests if available
        try:
            import requests
            self.requests = requests
        except ImportError:
            self.logger.error("Requests library not available for API interface")
            raise ImportError("Requests library required for API interface")
            
        self.logger.info(f"API interface set up with endpoint: {self.api_endpoint}")
    
    def _setup_console_interface(self) -> None:
        """Set up console-based interface."""
        # Console interface doesn't require special setup
        self.logger.info("Console interface set up")
    
    async def request_feedback(
        self, 
        query_type: str,
        query_content: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Request feedback from a human operator.
        
        Args:
            query_type: Type of query (e.g., "verification", "decision")
            query_content: Query content
            timeout: Timeout in seconds (overrides default auto_approve_timeout)
            
        Returns:
            Human feedback response or auto-response on timeout
        """
        # Generate unique query ID
        query_id = f"query_{uuid4().hex}"
        
        # Create query object
        query = {
            "id": query_id,
            "type": query_type,
            "content": query_content,
            "timestamp": time.time(),
            "status": "pending"
        }
        
        # Set timeout (use provided timeout or default)
        actual_timeout = timeout or self.auto_approve_timeout
        
        # Register query as pending
        with self.query_lock:
            self.pending_queries[query_id] = {
                "query": query,
                "response": None,
                "complete_event": Event(),
                "timeout": actual_timeout
            }
        
        # Submit query based on interface type
        if self.interface_type == "file":
            await self._submit_file_query(query)
        elif self.interface_type == "api":
            await self._submit_api_query(query)
        elif self.interface_type == "console":
            await self._submit_console_query(query)
            
        self.logger.info(f"Submitted query {query_id} of type {query_type}")
        
        # Wait for response with timeout
        pending_entry = self.pending_queries[query_id]
        if actual_timeout is None:
            # Wait indefinitely
            await asyncio.get_event_loop().run_in_executor(
                None, pending_entry["complete_event"].wait
            )
            
            # Response received
            with self.query_lock:
                response = pending_entry["response"]
                del self.pending_queries[query_id]
                
            self.logger.info(f"Received response for query {query_id}")
            return response
        else:
            # Wait with timeout
            try:
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, pending_entry["complete_event"].wait
                    ),
                    timeout=actual_timeout
                )
                
                # Response received
                with self.query_lock:
                    response = pending_entry["response"]
                    del self.pending_queries[query_id]
                    
                self.logger.info(f"Received response for query {query_id}")
                return response
                
            except asyncio.TimeoutError:
                # Timeout occurred
                with self.query_lock:
                    # Set default response for timeout
                    response = {
                        "id": query_id,
                        "status": "timeout",
                        "content": {
                            "decision": "auto_proceed",
                            "feedback": "Automatic response due to timeout"
                        },
                        "timestamp": time.time()
                    }
                    pending_entry["response"] = response
                    pending_entry["query"]["status"] = "timeout"
                    
                    # Clean up
                    del self.pending_queries[query_id]
                
                self.logger.warning(f"Timeout waiting for response to query {query_id}")
                return response
    
    async def _submit_file_query(self, query: Dict[str, Any]) -> None:
        """
        Submit a query via file interface.
        
        Args:
            query: Query object
        """
        query_path = os.path.join(self.query_dir, f"{query['id']}.json")
        
        # Write query to file
        with open(query_path, 'w') as f:
            json.dump(query, f, indent=2)
            
        # Start a background task to watch for response
        asyncio.create_task(self._watch_for_file_response(query['id']))
    
    async def _watch_for_file_response(self, query_id: str) -> None:
        """
        Watch for response to a file-based query.
        
        Args:
            query_id: Query ID
        """
        response_path = os.path.join(self.response_dir, f"{query_id}.json")
        
        # Wait for response file
        while True:
            # Check if query is still pending
            with self.query_lock:
                if query_id not in self.pending_queries:
                    return
            
            # Check for response file
            if os.path.exists(response_path):
                try:
                    with open(response_path, 'r') as f:
                        response = json.load(f)
                    
                    # Process response
                    with self.query_lock:
                        if query_id in self.pending_queries:
                            self.pending_queries[query_id]["response"] = response
                            self.pending_queries[query_id]["complete_event"].set()
                    
                    return
                except Exception as e:
                    self.logger.error(f"Error reading response file: {str(e)}")
            
            # Sleep before checking again
            await asyncio.sleep(1)
    
    async def _submit_api_query(self, query: Dict[str, Any]) -> None:
        """
        Submit a query via API interface.
        
        Args:
            query: Query object
        """
        # Start a background task for API call
        asyncio.create_task(self._make_api_call(query))
    
    async def _make_api_call(self, query: Dict[str, Any]) -> None:
        """
        Make API call and handle response.
        
        Args:
            query: Query object
        """
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            # Make API request using async
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.requests.post(
                    self.api_endpoint,
                    json=query,
                    headers=headers,
                    timeout=self.api_timeout
                )
            )
            
            # Process response
            if response.status_code == 200:
                response_data = response.json()
                
                # Update pending query
                with self.query_lock:
                    if query["id"] in self.pending_queries:
                        self.pending_queries[query["id"]]["response"] = response_data
                        self.pending_queries[query["id"]]["complete_event"].set()
            else:
                self.logger.error(f"API request failed: {response.status_code}")
                
                # Create error response
                error_response = {
                    "id": query["id"],
                    "status": "error",
                    "content": {
                        "decision": "auto_proceed",
                        "feedback": f"API error: {response.status_code}"
                    },
                    "timestamp": time.time()
                }
                
                # Update pending query
                with self.query_lock:
                    if query["id"] in self.pending_queries:
                        self.pending_queries[query["id"]]["response"] = error_response
                        self.pending_queries[query["id"]]["complete_event"].set()
                
        except Exception as e:
            self.logger.error(f"Error making API call: {str(e)}")
            
            # Create error response
            error_response = {
                "id": query["id"],
                "status": "error",
                "content": {
                    "decision": "auto_proceed",
                    "feedback": f"API error: {str(e)}"
                },
                "timestamp": time.time()
            }
            
            # Update pending query
            with self.query_lock:
                if query["id"] in self.pending_queries:
                    self.pending_queries[query["id"]]["response"] = error_response
                    self.pending_queries[query["id"]]["complete_event"].set()
    
    async def _submit_console_query(self, query: Dict[str, Any]) -> None:
        """
        Submit a query via console interface.
        
        Args:
            query: Query object
        """
        # Start a background task for console interaction
        asyncio.create_task(self._handle_console_query(query))
    
    async def _handle_console_query(self, query: Dict[str, Any]) -> None:
        """
        Handle console query interaction.
        
        Args:
            query: Query object
        """
        # Format the query for console display
        print("\n" + "="*80)
        print(f"HUMAN FEEDBACK REQUESTED - Query ID: {query['id']}")
        print(f"Type: {query['type']}")
        print("-"*80)
        print("Content:")
        
        for key, value in query['content'].items():
            print(f"  {key}: {value}")
        
        print("-"*80)
        print("Options: approve | reject | modify")
        print("="*80)
        
        # Get response using async
        decision = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("Decision: ").strip().lower()
        )
        
        feedback = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("Feedback: ").strip()
        )
        
        # Create response object
        response = {
            "id": query["id"],
            "status": "completed",
            "content": {
                "decision": decision,
                "feedback": feedback
            },
            "timestamp": time.time()
        }
        
        # Process response
        with self.query_lock:
            if query["id"] in self.pending_queries:
                self.pending_queries[query["id"]]["response"] = response
                self.pending_queries[query["id"]]["complete_event"].set()
    
    def check_response_needed(self, verification_result, task_metadata) -> bool:
        """
        Determine if human feedback is needed based on verification results.
        
        Args:
            verification_result: Result from External Checker
            task_metadata: Task metadata
            
        Returns:
            True if human feedback is needed, False otherwise
        """
        # Check verification confidence
        if verification_result.confidence < 0.7:
            return True
        
        # Check task criticality
        if task_metadata.get("criticality", "low") == "high":
            return True
        
        # Check for policy requirements
        if task_metadata.get("requires_human_approval", False):
            return True
        
        # Check if verification failed
        if not verification_result.is_valid:
            # For failed verifications, check if human review is required
            return task_metadata.get("review_failed_verifications", False)
        
        return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the Human Query Interface.
        
        Returns:
            Status information
        """
        with self.query_lock:
            pending_count = len(self.pending_queries)
            pending_queries = []
            
            for query_id, query_data in self.pending_queries.items():
                pending_queries.append({
                    "id": query_id,
                    "type": query_data["query"]["type"],
                    "timestamp": query_data["query"]["timestamp"]
                })
        
        return {
            "interface_type": self.interface_type,
            "pending_count": pending_count,
            "pending_queries": pending_queries
        }
    
    def cancel_query(self, query_id: str) -> bool:
        """
        Cancel a pending query.
        
        Args:
            query_id: Query ID
            
        Returns:
            True if query was cancelled, False if not found
        """
        with self.query_lock:
            if query_id not in self.pending_queries:
                return False
            
            # Create cancellation response
            response = {
                "id": query_id,
                "status": "cancelled",
                "content": {
                    "decision": "cancelled",
                    "feedback": "Query cancelled by system"
                },
                "timestamp": time.time()
            }
            
            # Update pending query
            self.pending_queries[query_id]["response"] = response
            self.pending_queries[query_id]["complete_event"].set()
            
            # Clean up
            del self.pending_queries[query_id]
        
        self.logger.info(f"Cancelled query {query_id}")
        return True


# Factory function for creating a Human Query Interface
def create_interface(config_path: Optional[str] = None) -> HumanQueryInterface:
    """
    Create and configure a Human Query Interface.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured HumanQueryInterface
    """
    # Load configuration if path provided
    config = {}
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading interface configuration: {str(e)}")
    
    # Get interface type and configuration
    interface_type = config.get("interface_type", "file")
    interface_config = config.get("interface_config", {})
    auto_approve_timeout = config.get("auto_approve_timeout")
    
    # Create interface
    interface = HumanQueryInterface(
        interface_type=interface_type,
        interface_config=interface_config,
        auto_approve_timeout=auto_approve_timeout
    )
    
    return interface