#!/usr/bin/env python3
"""
WebSocket Server for Recursive Thinking Module

Provides a WebSocket interface to the recursive thinking capabilities
for more efficient communication with TypeScript components.
"""

import os
import sys
import json
import time
import argparse
import asyncio
import logging
import threading
import traceback
import websockets
from typing import Dict, List, Any, Optional, Callable

# Add necessary path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import recursive thinking modules
from recursive_thinking.enhanced_recursive_thinking import EnhancedRecursiveThinkingChat
from recursive_thinking.genetic_adapter import GeneticRecursiveAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("websocket_server")

# Message types
class MessageType:
    INITIALIZE = 'initialize'
    EVOLVE = 'evolve'
    REFINE = 'refine'
    EVALUATE = 'evaluate'
    RESULT = 'result'
    ERROR = 'error'
    PROGRESS = 'progress'
    CLOSE = 'close'

class WebSocketServer:
    """WebSocket server for the recursive thinking module."""
    
    def __init__(self, port: int = 8765, verbose: bool = False):
        """
        Initialize the WebSocket server.
        
        Args:
            port: WebSocket server port
            verbose: Enable verbose logging
        """
        self.port = port
        self.verbose = verbose
        self.stop_event = threading.Event()
        
        # Initialize components
        self.recursive_thinking = None
        self.genetic_adapter = None
        
        # Set logging level
        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            
        logger.info(f"Initializing WebSocket server on port {port}")
    
    async def initialize_components(self, api_key: str = None):
        """Initialize the recursive thinking components."""
        try:
            # Get API key from environment if not provided
            api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("API key is required. Set OPENROUTER_API_KEY environment variable or provide in initialization.")
            
            # Initialize recursive thinking
            self.recursive_thinking = EnhancedRecursiveThinkingChat(api_key=api_key)
            
            # Initialize genetic adapter
            self.genetic_adapter = GeneticRecursiveAdapter(api_key=api_key)
            
            logger.info("Components initialized successfully")
            return {"status": "success"}
        except Exception as e:
            error_msg = f"Failed to initialize components: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    async def handle_message(self, websocket, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming messages from clients.
        
        Args:
            websocket: WebSocket connection
            message_data: Message data
            
        Returns:
            Response message
        """
        message_type = message_data.get('type')
        message_id = message_data.get('id')
        payload = message_data.get('payload', {})
        
        logger.debug(f"Received message: type={message_type}, id={message_id}")
        
        # Initialize necessary components first
        if not self.recursive_thinking or not self.genetic_adapter:
            if message_type != MessageType.INITIALIZE:
                api_key = payload.get('api_key') or os.environ.get("OPENROUTER_API_KEY")
                await self.initialize_components(api_key)
        
        try:
            # Handle different message types
            if message_type == MessageType.INITIALIZE:
                result = await self.initialize_components(payload.get('api_key'))
                return self.create_response(MessageType.RESULT, message_id, result)
                
            elif message_type == MessageType.EVOLVE:
                # Extract parameters
                candidates = payload.get('candidates', [])
                constraints = payload.get('constraints', [])
                recursion_rounds = payload.get('recursion_rounds', 2)
                
                # Progress reporting function
                async def report_progress(progress_data):
                    """Send progress updates to the client."""
                    progress_msg = self.create_response(
                        MessageType.PROGRESS, 
                        message_id, 
                        progress_data
                    )
                    await websocket.send(json.dumps(progress_msg))
                
                # Create a wrapper to handle verbose output
                original_verbose = self.verbose
                if original_verbose:
                    # Set up progress reporting
                    def progress_callback(data):
                        asyncio.create_task(report_progress(data))
                    
                    # Inject progress callback
                    evolution_result = await self.run_hybrid_evolve(
                        candidates, 
                        constraints, 
                        payload.get('fitness_function', 'default'),
                        recursion_rounds,
                        progress_callback
                    )
                else:
                    # Run without progress reporting
                    evolution_result = await self.run_hybrid_evolve(
                        candidates, 
                        constraints, 
                        payload.get('fitness_function', 'default'),
                        recursion_rounds
                    )
                
                return self.create_response(MessageType.RESULT, message_id, evolution_result)
                
            elif message_type == MessageType.REFINE:
                # Extract parameters
                solution = payload.get('solution', '')
                constraints = payload.get('constraints', [])
                
                # Run refinement
                refined_solution = await self.run_refinement(solution, constraints)
                
                return self.create_response(MessageType.RESULT, message_id, refined_solution)
                
            elif message_type == MessageType.EVALUATE:
                # Extract parameters
                solutions = payload.get('solutions', [])
                
                # Run evaluation
                evaluation_results = await self.run_evaluation(
                    solutions, 
                    payload.get('fitness_function', 'default')
                )
                
                return self.create_response(MessageType.RESULT, message_id, evaluation_results)
                
            elif message_type == MessageType.CLOSE:
                self.stop_event.set()
                return self.create_response(MessageType.RESULT, message_id, {"status": "closing"})
                
            else:
                raise ValueError(f"Unknown message type: {message_type}")
                
        except Exception as e:
            error_message = f"Error handling message: {str(e)}"
            logger.error(f"{error_message}\n{traceback.format_exc()}")
            return self.create_response(MessageType.ERROR, message_id, {
                "message": error_message,
                "traceback": traceback.format_exc()
            })
    
    async def run_hybrid_evolve(
        self, 
        candidates: List[str], 
        constraints: List[Dict], 
        fitness_function: str, 
        recursion_rounds: int = 2,
        progress_callback: Callable = None
    ) -> Dict[str, Any]:
        """
        Run hybrid evolution with progress reporting.
        
        Args:
            candidates: Candidate solutions
            constraints: Constraints for solution validation
            fitness_function: Fitness function identifier
            recursion_rounds: Number of recursive thinking rounds
            progress_callback: Optional callback for progress reporting
            
        Returns:
            Evolution result
        """
        # For now, we'll use a mock implementation since we don't have
        # direct communication with the TypeScript fitness function yet
        def mock_fitness_function(solution):
            """Mock fitness function that gives higher scores to longer solutions."""
            # This is just a placeholder - would need WebSocket-based evaluation
            # for real integration with TypeScript fitness functions
            length_score = min(len(solution) / 1000, 0.5)  # Max 0.5 for length
            
            # Some rudimentary scoring based on common patterns in good solutions
            quality_score = 0
            
            # Check for error handling
            if "try" in solution and "catch" in solution:
                quality_score += 0.1
            
            # Check for comments
            if "/**" in solution or "//" in solution:
                quality_score += 0.1
            
            # Check for modular design
            if "function" in solution or "class" in solution:
                quality_score += 0.1
            
            # Check for error checking
            if "if" in solution and ("error" in solution.lower() or "exception" in solution.lower()):
                quality_score += 0.1
            
            # Check for return statements
            if "return" in solution:
                quality_score += 0.1
            
            return length_score + quality_score
        
        logger.info(f"Starting hybrid evolution with {len(candidates)} candidates and {recursion_rounds} rounds")
        
        # Set up progress monitoring
        if progress_callback:
            # Create a custom genetic adapter with progress reporting
            class ProgressReportingAdapter(GeneticRecursiveAdapter):
                def hybrid_evolve(self, *args, **kwargs):
                    original_verbose = kwargs.get('verbose', True)
                    
                    # Override verbose parameter
                    def custom_print(*args, **kwargs):
                        # Capture the progress information
                        progress_data = ' '.join(str(arg) for arg in args)
                        # Send progress update
                        if progress_callback:
                            asyncio.create_task(progress_callback({
                                "message": progress_data,
                                "timestamp": time.time()
                            }))
                    
                    # Call the original method but capture its output
                    result = super().hybrid_evolve(*args, **kwargs)
                    return result
            
            # Use the custom adapter
            adapter = ProgressReportingAdapter(api_key=self.recursive_thinking.api_key)
        else:
            # Use the standard adapter
            adapter = self.genetic_adapter
        
        try:
            # Run the hybrid evolution
            result = adapter.hybrid_evolve(
                candidates,
                constraints,
                "mock_fitness",  # This is just a placeholder for now
                recursion_rounds=recursion_rounds,
                verbose=True
            )
            
            logger.info(f"Hybrid evolution completed with fitness: {result.get('fitness', 0)}")
            return result
        except Exception as e:
            logger.error(f"Error in hybrid evolution: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def run_refinement(self, solution: str, constraints: List[Dict]) -> Dict[str, Any]:
        """
        Run solution refinement.
        
        Args:
            solution: Solution to refine
            constraints: Constraints for solution validation
            
        Returns:
            Refined solution
        """
        logger.info(f"Starting solution refinement")
        
        try:
            # Convert constraints to a format the recursive thinking can use
            thinking_constraints = []
            if constraints:
                for constraint in constraints:
                    thinking_constraints.append({
                        "type": constraint.get("type", ""),
                        "value": constraint.get("value", "")
                    })
            
            # Run the refinement
            result = self.recursive_thinking.refine_solution(
                solution, 
                thinking_constraints, 
                verbose=self.verbose
            )
            
            return {
                "solution": result,
                "original": solution
            }
        except Exception as e:
            logger.error(f"Error in solution refinement: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def run_evaluation(self, solutions: List[str], fitness_function: str) -> Dict[str, Any]:
        """
        Run solution evaluation.
        
        Args:
            solutions: Solutions to evaluate
            fitness_function: Fitness function identifier
            
        Returns:
            Evaluation results
        """
        logger.info(f"Starting evaluation of {len(solutions)} solutions")
        
        try:
            # For now, use mock evaluation - would need WebSocket callbacks for real integration
            results = []
            for solution in solutions:
                # Use a simple length-based fitness as a placeholder
                length_score = min(len(solution) / 1000, 0.5)
                quality_score = 0.3 if "function" in solution else 0
                results.append({
                    "solution": solution,
                    "fitness": length_score + quality_score
                })
            
            return {
                "results": results
            }
        except Exception as e:
            logger.error(f"Error in solution evaluation: {str(e)}\n{traceback.format_exc()}")
            raise
    
    def create_response(self, message_type: str, message_id: str, payload: Any) -> Dict[str, Any]:
        """
        Create a response message.
        
        Args:
            message_type: Message type
            message_id: Message ID
            payload: Message payload
            
        Returns:
            Response message
        """
        return {
            "type": message_type,
            "id": message_id,
            "payload": payload,
            "timestamp": time.time()
        }
    
    async def handler(self, websocket, path):
        """
        Handle WebSocket connections.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                # Process the message
                try:
                    message_data = json.loads(message)
                    response = await self.handle_message(websocket, message_data)
                    await websocket.send(json.dumps(response))
                    
                    # Check if we should close the server
                    if self.stop_event.is_set():
                        logger.info("Closing server due to client request")
                        break
                        
                except json.JSONDecodeError:
                    error_response = {
                        "type": MessageType.ERROR,
                        "id": "server_error",
                        "payload": {"message": "Invalid JSON message"},
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(error_response))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {websocket.remote_address}")
            
        except Exception as e:
            logger.error(f"Error handling connection: {str(e)}\n{traceback.format_exc()}")
    
    async def run_server(self):
        """Run the WebSocket server."""
        logger.info(f"Starting WebSocket server on port {self.port}")
        
        # Start the server
        async with websockets.serve(self.handler, "localhost", self.port):
            # Print a message that the server is running (for TypeScript to detect)
            print(f"WebSocket server running on port {self.port}")
            sys.stdout.flush()
            
            # Run until the stop event is set
            while not self.stop_event.is_set():
                await asyncio.sleep(1)
    
    def start(self):
        """Start the WebSocket server in the current thread."""
        try:
            asyncio.run(self.run_server())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {str(e)}\n{traceback.format_exc()}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="WebSocket server for recursive thinking")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket server port")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    # Create and start the server
    server = WebSocketServer(port=args.port, verbose=args.verbose)
    server.start()

if __name__ == "__main__":
    main()