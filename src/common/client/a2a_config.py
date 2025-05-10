"""
A2A Configuration

This module provides configuration management for A2A endpoints.
"""

import os
import uuid
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class AgentEndpoint(BaseModel):
    """Represents an A2A agent endpoint."""
    id: str  # UUID
    url: str


class AgentConfig:
    """Configuration for A2A client connections."""
    
    def __init__(self):
        self.endpoints: List[AgentEndpoint] = []
        self.load_endpoints()
    
    def load_endpoints(self) -> None:
        """Load endpoint configurations from environment variables."""
        endpoints_str = os.getenv("A2A_ENDPOINT_URLS")
        
        if not endpoints_str:
            # For backward compatibility, support single endpoint
            single_endpoint = os.getenv("A2A_ENDPOINT_URL")
            if single_endpoint:
                self.endpoints = [AgentEndpoint(
                    id=str(uuid.uuid4()),
                    url=single_endpoint
                )]
            return
        
        try:
            self.endpoints = [
                AgentEndpoint(
                    id=str(uuid.uuid4()),
                    url=url.strip()
                )
                for url in endpoints_str.split(",")
            ]
        except Exception as error:
            print(f"Failed to parse A2A_ENDPOINT_URLS: {error}")
            self.endpoints = []
    
    def get_endpoints(self) -> List[AgentEndpoint]:
        """Get all configured endpoints."""
        return self.endpoints
    
    def get_endpoint_by_id(self, id: str) -> Optional[AgentEndpoint]:
        """Get an endpoint by its ID."""
        for endpoint in self.endpoints:
            if endpoint.id == id:
                return endpoint
        return None
    
    def get_endpoint_by_url(self, url: str) -> Optional[AgentEndpoint]:
        """Get an endpoint by its URL."""
        for endpoint in self.endpoints:
            if endpoint.url == url:
                return endpoint
        return None