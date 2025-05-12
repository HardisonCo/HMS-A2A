#!/usr/bin/env python3
"""
Federation Framework Service Runner.

This script provides a command-line entry point for running the federation services.
"""

import os
import sys
import argparse
import logging
import asyncio
import signal
import yaml
from typing import Dict, Any, Optional

from federation.manager import FederationManager
from federation.api import FederationAPI
from federation.gateway import GatewayServer
from federation.exceptions import ConfigurationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config = {}
    
    # Try environment variable if path not provided
    if not config_path:
        config_path = os.environ.get("FEDERATION_CONFIG")
    
    # Load from file if path provided
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f).get("federation", {})
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    # Apply environment variables
    for key, value in os.environ.items():
        if key.startswith("FEDERATION_"):
            # Convert FEDERATION_XXX_YYY to xxx.yyy
            config_key = key[len("FEDERATION_"):].lower().replace("_", ".")
            config_keys = config_key.split(".")
            
            # Navigate to the right level in the config
            current = config
            for k in config_keys[:-1]:
                current.setdefault(k, {})
                current = current[k]
            
            # Set the value
            current[config_keys[-1]] = value
    
    return config


async def run_services(args):
    """Run federation services."""
    # Load configuration
    config = load_config(args.config)
    
    # Get agency ID
    agency_id = args.agency_id or config.get("local_agency") or os.environ.get("FEDERATION_LOCAL_AGENCY")
    if not agency_id:
        raise ConfigurationError("No agency ID provided")
    
    # Initialize federation manager
    federation = FederationManager(
        local_agency_id=agency_id,
        **config
    )
    
    # Initialize services
    api = None
    gateway = None
    
    if args.api:
        # Start API server
        api = FederationAPI(federation)
        api_host = args.api_host or config.get("api", {}).get("host", "0.0.0.0")
        api_port = args.api_port or config.get("api", {}).get("port", 8080)
        logger.info(f"Starting API server on {api_host}:{api_port}")
        
        # This would normally start the API server in a separate task
        # For now, we'll just create it
        logger.info("API server ready")
    
    if args.gateway:
        # Start gateway server
        gateway = GatewayServer(federation)
        gateway_host = args.gateway_host or config.get("gateway", {}).get("host", "0.0.0.0")
        gateway_port = args.gateway_port or config.get("gateway", {}).get("port", 8585)
        
        # Start gateway in a background task
        await gateway.start(gateway_host, gateway_port)
    
    # Keep running until interrupted
    try:
        # This would normally start a proper event loop
        # For now, just wait for Ctrl+C
        logger.info("Federation services running, press Ctrl+C to stop")
        
        # Create shutdown event
        shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(shutdown(shutdown_event))
            )
        
        # Wait for shutdown
        await shutdown_event.wait()
        
    finally:
        # Cleanup
        if gateway:
            await gateway.stop()
        
        logger.info("Federation services stopped")


async def shutdown(shutdown_event):
    """Trigger graceful shutdown."""
    logger.info("Shutdown initiated")
    shutdown_event.set()


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Federation Framework Service Runner")
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--agency-id", "-a",
        help="Local agency ID"
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start API server"
    )
    
    parser.add_argument(
        "--api-host",
        help="API server host"
    )
    
    parser.add_argument(
        "--api-port", "-p",
        type=int,
        help="API server port"
    )
    
    parser.add_argument(
        "--gateway",
        action="store_true",
        help="Start gateway server"
    )
    
    parser.add_argument(
        "--gateway-host",
        help="Gateway server host"
    )
    
    parser.add_argument(
        "--gateway-port", "-g",
        type=int,
        help="Gateway server port"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Start services
    try:
        asyncio.run(run_services(args))
    except ConfigurationError as e:
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()