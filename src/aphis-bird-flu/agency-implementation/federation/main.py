"""
Main Entry Point for Federation Hub

This module provides the entry point for running the Federation Hub as a standalone
service. It initializes all components and starts the FastAPI server.
"""

import logging
import os
import uvicorn
from api import api

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('federation.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the federation hub"""
    logger.info("Starting Federation Hub")
    
    # Get configuration from environment or use defaults
    host = os.environ.get("FEDERATION_HUB_HOST", "0.0.0.0")
    port = int(os.environ.get("FEDERATION_HUB_PORT", "8000"))
    
    # Log configuration
    logger.info(f"Federation Hub configured to run on {host}:{port}")
    
    # Start the FastAPI server
    uvicorn.run(api, host=host, port=port)

if __name__ == "__main__":
    main()