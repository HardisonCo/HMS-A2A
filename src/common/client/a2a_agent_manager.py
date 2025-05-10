"""
A2A Agent Manager

This module provides management of A2A client connections.
"""

import asyncio
from typing import Dict, Optional, List, Any

from common.client.a2a_mcp_client import A2AClient
from common.client.a2a_config import AgentConfig, AgentEndpoint


class AgentManager:
    """Manager for A2A client connections."""
    
    def __init__(self):
        self.clients: Dict[str, A2AClient] = {}
        self.config = AgentConfig()
    
    async def initialize(self) -> None:
        """Initialize connections to all configured A2A endpoints."""
        endpoints = self.config.get_endpoints()
        
        for endpoint in endpoints:
            try:
                client = A2AClient(endpoint.url)
                # Test the connection
                await client.agent_card()
                self.clients[endpoint.id] = client
                print(f"Successfully connected to agent {endpoint.id} at {endpoint.url}")
            except Exception as error:
                print(f"Failed to connect to agent {endpoint.id} at {endpoint.url}: {error}")
    
    def get_client_by_id(self, id: str) -> Optional[A2AClient]:
        """Get a client by its ID."""
        return self.clients.get(id)
    
    def get_all_clients(self) -> Dict[str, A2AClient]:
        """Get all available clients."""
        return self.clients
    
    def get_endpoints(self) -> List[AgentEndpoint]:
        """Get all configured endpoints."""
        return self.config.get_endpoints()