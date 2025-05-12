#!/usr/bin/env python3
"""
Launcher script for starting agency-specific API implementations of the
Adaptive Surveillance and Response System.

This script allows starting the API server for CDC, EPA, or FEMA implementations.
"""

import argparse
import os
import subprocess
import sys

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Start an agency-specific implementation of the Adaptive Surveillance and Response System"
    )
    
    parser.add_argument(
        "agency",
        choices=["cdc", "epa", "fema"],
        help="The agency implementation to start (cdc, epa, or fema)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind the server to (default depends on agency: CDC=8001, EPA=8002, FEMA=8003)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable automatic reload on code changes"
    )
    
    return parser.parse_args()

def get_default_port(agency):
    """Get the default port for an agency."""
    ports = {
        "cdc": 8001,
        "epa": 8002,
        "fema": 8003
    }
    return ports.get(agency.lower())

def main():
    """Main function to start the API server."""
    args = parse_arguments()
    
    # Get the agency and normalize to lowercase
    agency = args.agency.lower()
    
    # Get the port (use default if not specified)
    port = args.port or get_default_port(agency)
    
    # Build the API module path
    api_module = f"agency-implementation.{agency}.system-supervisors.api:app"
    
    # Build the command
    cmd = [
        "uvicorn",
        api_module,
        "--host", args.host,
        "--port", str(port)
    ]
    
    # Add reload flag if requested
    if args.reload:
        cmd.append("--reload")
    
    print(f"Starting {agency.upper()} Adaptive Surveillance and Response System API")
    print(f"API will be available at http://{args.host}:{port}")
    print(f"API documentation will be available at http://{args.host}:{port}/docs")
    
    # Run the command
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()