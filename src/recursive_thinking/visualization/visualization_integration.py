import json
import os
from typing import Dict, List, Any, Optional, Union
import threading
import time
from datetime import datetime
import websocket
import logging
from ..types import RecursiveThinkingStats, ThinkingStep
from .thinking_visualizer import ThinkingVisualizer, ThinkingProcessDiagram

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ThinkingVisualizationIntegration")

class ThinkingVisualizationIntegration:
    """
    Integration module for recursive thinking visualization
    
    Connects the recursive thinking system with the visualization components
    and provides real-time data streaming to the frontend visualization system.
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:3001", 
                 output_dir: str = "visualization_output",
                 auto_visualize: bool = True):
        """
        Initialize the visualization integration
        
        Args:
            websocket_url: URL for WebSocket server connection
            output_dir: Directory to save visualization files
            auto_visualize: Whether to automatically generate visualizations
        """
        self.websocket_url = websocket_url
        self.output_dir = output_dir
        self.auto_visualize = auto_visualize
        self.visualizer = ThinkingVisualizer(output_dir)
        self.diagram_generator = ThinkingProcessDiagram(output_dir)
        self.ws = None
        self.connected = False
        self.thinking_history: List[RecursiveThinkingStats] = []
        self.thinking_data_buffer: List[Dict[str, Any]] = []
        self.buffer_lock = threading.Lock()
        self.ws_thread = None
        self.buffer_process_thread = None
        self.running = False
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Start WebSocket connection
        self._start_websocket_connection()
    
    def _start_websocket_connection(self) -> None:
        """Start WebSocket connection in a separate thread"""
        def connect_ws():
            """WebSocket connection handler"""
            while self.running:
                try:
                    # Connect to WebSocket server
                    self.ws = websocket.WebSocketApp(
                        self.websocket_url,
                        on_open=self._on_ws_open,
                        on_message=self._on_ws_message,
                        on_error=self._on_ws_error,
                        on_close=self._on_ws_close
                    )
                    
                    logger.info(f"Connecting to WebSocket server at {self.websocket_url}")
                    self.ws.run_forever()
                    
                    # If we get here, the connection was closed
                    logger.info("WebSocket connection closed")
                    self.connected = False
                    
                    # Only try to reconnect if we're still running
                    if self.running:
                        logger.info("Attempting to reconnect in 5 seconds...")
                        time.sleep(5)
                except Exception as e:
                    logger.error(f"WebSocket connection error: {str(e)}")
                    time.sleep(5)
        
        def process_buffer():
            """Process the data buffer periodically"""
            while self.running:
                try:
                    # Process buffered data if connected
                    if self.connected and self.thinking_data_buffer:
                        with self.buffer_lock:
                            buffer_copy = self.thinking_data_buffer.copy()
                            self.thinking_data_buffer = []
                        
                        # Send buffered data
                        for data in buffer_copy:
                            try:
                                self.ws.send(json.dumps(data))
                                logger.debug(f"Sent buffered data: {data.get('type', 'unknown')}")
                            except Exception as e:
                                logger.error(f"Error sending buffered data: {str(e)}")
                                # Put back in buffer
                                with self.buffer_lock:
                                    self.thinking_data_buffer.append(data)
                except Exception as e:
                    logger.error(f"Buffer processing error: {str(e)}")
                
                # Sleep to avoid high CPU usage
                time.sleep(0.5)
        
        # Start threads
        self.running = True
        self.ws_thread = threading.Thread(target=connect_ws)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        self.buffer_process_thread = threading.Thread(target=process_buffer)
        self.buffer_process_thread.daemon = True
        self.buffer_process_thread.start()
    
    def _on_ws_open(self, ws) -> None:
        """WebSocket open event handler"""
        logger.info("WebSocket connection established")
        self.connected = True
    
    def _on_ws_message(self, ws, message) -> None:
        """WebSocket message event handler"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'ping':
                # Respond to ping with pong
                self.ws.send(json.dumps({'type': 'pong'}))
            elif msg_type == 'visualization_request':
                # Handle visualization request
                logger.info(f"Received visualization request: {data}")
                self._handle_visualization_request(data)
            else:
                logger.debug(f"Received WebSocket message: {msg_type}")
        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
    
    def _on_ws_error(self, ws, error) -> None:
        """WebSocket error event handler"""
        logger.error(f"WebSocket error: {str(error)}")
    
    def _on_ws_close(self, ws, close_status_code, close_msg) -> None:
        """WebSocket close event handler"""
        logger.info(f"WebSocket connection closed: {close_status_code}, {close_msg}")
        self.connected = False
    
    def _handle_visualization_request(self, data: Dict[str, Any]) -> None:
        """
        Handle visualization request from WebSocket
        
        Args:
            data: Request data from WebSocket
        """
        request_type = data.get('request')
        
        if request_type == 'metrics_summary':
            # Generate metrics summary and send back
            summary = self.visualizer.export_metrics_summary()
            response = {
                'type': 'metrics_summary_response',
                'data': summary,
                'requestId': data.get('requestId')
            }
            self.ws.send(json.dumps(response))
        
        elif request_type == 'thinking_process':
            # Generate thinking process visualization for specific process
            thinking_id = data.get('thinkingId', -1)
            if thinking_id >= 0 and thinking_id < len(self.thinking_history):
                # Create visualization
                fig = self.visualizer.visualize_thinking_process(thinking_id, save=True)
                
                # Generate diagram
                diagram_path = self.diagram_generator.generate_thinking_diagram(
                    self.thinking_history[thinking_id]
                )
                
                response = {
                    'type': 'thinking_process_response',
                    'status': 'success',
                    'message': f'Visualization generated and saved',
                    'requestId': data.get('requestId')
                }
            else:
                response = {
                    'type': 'thinking_process_response',
                    'status': 'error',
                    'message': f'Thinking process with ID {thinking_id} not found',
                    'requestId': data.get('requestId')
                }
            
            self.ws.send(json.dumps(response))
        
        elif request_type == 'metrics_dashboard':
            # Generate metrics dashboard visualization
            fig = self.visualizer.visualize_metrics_dashboard(save=True)
            
            response = {
                'type': 'metrics_dashboard_response',
                'status': 'success',
                'message': 'Metrics dashboard generated and saved',
                'requestId': data.get('requestId')
            }
            self.ws.send(json.dumps(response))
    
    def register_thinking_process(self, stats: RecursiveThinkingStats) -> None:
        """
        Register a new thinking process with the visualization system
        
        Args:
            stats: Statistics from a recursive thinking process
        """
        # Add to local history
        self.thinking_history.append(stats)
        
        # Add to visualizer
        self.visualizer.add_thinking_stats(stats)
        
        # Generate visualizations if auto-visualize is enabled
        if self.auto_visualize:
            self.visualizer.visualize_thinking_process(len(self.thinking_history) - 1, save=True)
            self.diagram_generator.generate_thinking_diagram(stats)
        
        # Send data to WebSocket if connected
        thinking_data = self._stats_to_dict(stats)
        data_to_send = {
            'type': 'thinkingData',
            'stats': thinking_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to buffer (will be sent when connected)
        with self.buffer_lock:
            self.thinking_data_buffer.append(data_to_send)
        
        # Log
        logger.info(f"Registered thinking process with {len(stats.steps)} steps")
    
    def _stats_to_dict(self, stats: RecursiveThinkingStats) -> Dict[str, Any]:
        """
        Convert RecursiveThinkingStats to dictionary for transmission
        
        Args:
            stats: RecursiveThinkingStats object
            
        Returns:
            Dictionary representation
        """
        steps_data = []
        for step in stats.steps:
            steps_data.append({
                'description': step.description,
                'input': step.input[:200] + ('...' if len(step.input) > 200 else ''),  # Truncate for transmission
                'output': step.output[:200] + ('...' if len(step.output) > 200 else ''),  # Truncate for transmission
                'tokens': step.tokens,
                'executionTime': step.executionTime
            })
        
        return {
            'input': stats.input[:200] + ('...' if len(stats.input) > 200 else ''),  # Truncate for transmission
            'steps': steps_data,
            'totalTokens': stats.totalTokens,
            'executionTime': stats.executionTime,
            'improvementScore': stats.improvementScore
        }
    
    def generate_metrics_dashboard(self) -> str:
        """
        Generate a metrics dashboard visualization
        
        Returns:
            Path to the generated visualization
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thinking_metrics_dashboard_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        self.visualizer.visualize_metrics_dashboard(save=True)
        self.visualizer.save_metrics_summary()
        
        return filepath
    
    def export_thinking_data(self, filename: Optional[str] = None) -> str:
        """
        Export all thinking data to a JSON file
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"thinking_data_export_{timestamp}.json"
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert thinking history to JSON-serializable format
        export_data = []
        for stats in self.thinking_history:
            export_data.append(self._stats_to_dict(stats))
        
        # Add metadata
        metadata = {
            'exportTimestamp': datetime.now().isoformat(),
            'totalThinkingProcesses': len(export_data),
            'metrics': self.visualizer.export_metrics_summary()
        }
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump({
                'metadata': metadata,
                'thinkingProcesses': export_data
            }, f, indent=2)
        
        logger.info(f"Exported thinking data to {filepath}")
        return filepath
    
    def shutdown(self) -> None:
        """Shut down the integration and close connections"""
        logger.info("Shutting down thinking visualization integration")
        self.running = False
        
        # Close WebSocket connection
        if self.ws:
            self.ws.close()
        
        # Wait for threads to terminate
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=2)
        
        if self.buffer_process_thread and self.buffer_process_thread.is_alive():
            self.buffer_process_thread.join(timeout=2)
        
        # Export data before shutdown
        self.export_thinking_data("final_thinking_data_export.json")
        
        logger.info("Thinking visualization integration shut down successfully")


class VisualizationWebSocketServer:
    """
    WebSocket server for visualization data
    
    Provides a WebSocket server that visualization clients can connect to
    for real-time updates of thinking and genetic algorithm data.
    """
    
    def __init__(self, host: str = "localhost", port: int = 3001):
        """
        Initialize the WebSocket server
        
        Args:
            host: Host to bind the server to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()
        self.running = False
        self.server_thread = None
        
        # Initialize logger
        self.logger = logging.getLogger("VisualizationWebSocketServer")
    
    def start(self) -> None:
        """Start the WebSocket server in a separate thread"""
        if self.running:
            self.logger.warning("WebSocket server is already running")
            return
        
        def run_server():
            """WebSocket server thread"""
            import asyncio
            import websockets
            
            async def handler(websocket, path):
                """Handle WebSocket connections"""
                # Register client
                self.clients.add(websocket)
                self.logger.info(f"Client connected: {websocket.remote_address}")
                
                try:
                    # Send welcome message
                    await websocket.send(json.dumps({
                        'type': 'welcome',
                        'message': 'Connected to Thinking Visualization WebSocket Server',
                        'timestamp': datetime.now().isoformat()
                    }))
                    
                    # Handle incoming messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self._handle_message(websocket, data)
                        except json.JSONDecodeError:
                            self.logger.warning(f"Received invalid JSON: {message}")
                        except Exception as e:
                            self.logger.error(f"Error handling message: {str(e)}")
                
                except websockets.exceptions.ConnectionClosed:
                    self.logger.info(f"Client disconnected: {websocket.remote_address}")
                except Exception as e:
                    self.logger.error(f"WebSocket error: {str(e)}")
                finally:
                    # Unregister client
                    self.clients.remove(websocket)
            
            async def ping_clients():
                """Send periodic pings to keep connections alive"""
                while self.running:
                    if self.clients:
                        ping_msg = json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})
                        disconnected = set()
                        
                        for client in self.clients:
                            try:
                                await client.send(ping_msg)
                            except Exception:
                                disconnected.add(client)
                        
                        # Remove disconnected clients
                        for client in disconnected:
                            self.clients.remove(client)
                    
                    await asyncio.sleep(30)  # Ping every 30 seconds
            
            async def serve():
                """Start the WebSocket server"""
                self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
                
                server = await websockets.serve(handler, self.host, self.port)
                self.server = server
                
                # Start ping task
                ping_task = asyncio.create_task(ping_clients())
                
                # Wait for server to close
                await server.wait_closed()
                
                # Cancel ping task
                ping_task.cancel()
                try:
                    await ping_task
                except asyncio.CancelledError:
                    pass
            
            # Set up asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the server
                loop.run_until_complete(serve())
            except Exception as e:
                self.logger.error(f"WebSocket server error: {str(e)}")
            finally:
                loop.close()
                self.running = False
                self.logger.info("WebSocket server stopped")
        
        # Start server thread
        self.running = True
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Wait for server to start
        time.sleep(1)
        self.logger.info("WebSocket server started")
    
    async def _handle_message(self, websocket, data: Dict[str, Any]) -> None:
        """
        Handle an incoming WebSocket message
        
        Args:
            websocket: WebSocket connection
            data: Message data
        """
        msg_type = data.get('type')
        
        if msg_type == 'pong':
            # Ignore pong responses
            pass
        elif msg_type == 'register':
            # Client registration
            client_info = data.get('client', {})
            self.logger.info(f"Client registered: {client_info.get('name', 'Unknown')}")
            
            # Send acknowledgement
            await websocket.send(json.dumps({
                'type': 'register_ack',
                'message': 'Registration successful',
                'timestamp': datetime.now().isoformat()
            }))
        else:
            self.logger.debug(f"Received message of type: {msg_type}")
    
    async def broadcast(self, data: Dict[str, Any]) -> None:
        """
        Broadcast data to all connected clients
        
        Args:
            data: Data to broadcast
        """
        if not self.clients:
            return
        
        message = json.dumps(data)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except Exception:
                # Mark for removal
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.clients.remove(client)
    
    def broadcast_sync(self, data: Dict[str, Any]) -> None:
        """
        Synchronous version of broadcast for use from non-async contexts
        
        Args:
            data: Data to broadcast
        """
        import asyncio
        
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run broadcast
        if loop.is_running():
            # Create a future and broadcast in a thread-safe way
            future = asyncio.run_coroutine_threadsafe(self.broadcast(data), loop)
            try:
                future.result(timeout=1)  # Wait up to 1 second
            except Exception as e:
                self.logger.error(f"Error in broadcast: {str(e)}")
        else:
            # Just run the coroutine
            loop.run_until_complete(self.broadcast(data))
    
    def send_thinking_data(self, stats: Union[RecursiveThinkingStats, Dict[str, Any]]) -> None:
        """
        Send thinking data to connected clients
        
        Args:
            stats: Thinking statistics to send
        """
        # Convert stats to dict if needed
        if isinstance(stats, RecursiveThinkingStats):
            # Create a simplified version for transmission
            steps_data = []
            for step in stats.steps:
                steps_data.append({
                    'description': step.description,
                    'tokens': step.tokens,
                    'executionTime': step.executionTime
                })
            
            stats_dict = {
                'input': stats.input[:100] + ('...' if len(stats.input) > 100 else ''),
                'steps': steps_data,
                'totalTokens': stats.totalTokens,
                'executionTime': stats.executionTime,
                'improvementScore': stats.improvementScore
            }
        else:
            stats_dict = stats
        
        # Create message
        message = {
            'type': 'thinkingData',
            'stats': stats_dict,
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast
        self.broadcast_sync(message)
    
    def stop(self) -> None:
        """Stop the WebSocket server"""
        self.logger.info("Stopping WebSocket server...")
        self.running = False
        
        if self.server:
            import asyncio
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Close server
            if hasattr(self.server, 'close'):
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(self.server.close(), loop)
                else:
                    loop.run_until_complete(self.server.close())
        
        # Wait for server thread to terminate
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        
        self.logger.info("WebSocket server stopped")


def create_visualization_integration(
    websocket_url: str = "ws://localhost:3001",
    output_dir: str = "visualization_output",
    auto_visualize: bool = True
) -> ThinkingVisualizationIntegration:
    """
    Create a visualization integration
    
    Args:
        websocket_url: URL for WebSocket server
        output_dir: Directory for output files
        auto_visualize: Whether to auto-generate visualizations
        
    Returns:
        ThinkingVisualizationIntegration instance
    """
    return ThinkingVisualizationIntegration(
        websocket_url=websocket_url,
        output_dir=output_dir,
        auto_visualize=auto_visualize
    )


def create_visualization_server(
    host: str = "localhost",
    port: int = 3001
) -> VisualizationWebSocketServer:
    """
    Create a visualization WebSocket server
    
    Args:
        host: Host to bind to
        port: Port to listen on
        
    Returns:
        VisualizationWebSocketServer instance
    """
    return VisualizationWebSocketServer(host=host, port=port)