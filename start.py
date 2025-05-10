#!/usr/bin/env python3
"""
Unified Start Script for HMS-A2A

This script provides a unified way to start the HMS-A2A services with or without
Chain of Recursive Thoughts (CoRT) capabilities enabled.

Usage:
    python start.py [--service SERVICE] [--host HOST] [--port PORT] [--cort] [--test]
    
Services:
    all      - Start all services (default)
    a2a      - Start only the A2A service
    graph    - Start only the graph agent
    gov      - Start only the government agents
    
Options:
    --host   - Host to bind to (default: localhost)
    --port   - Starting port number (default: 10000, services use consecutive ports)
    --cort   - Enable Chain of Recursive Thoughts (optional)
    --test   - Run tests before starting services
"""

import os
import sys
import subprocess
import argparse
import unittest
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from multiprocessing import Process
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("start")

# Load environment variables
load_dotenv()

# Check if GOOGLE_API_KEY is set
if not os.getenv("GOOGLE_API_KEY"):
    logger.error("GOOGLE_API_KEY environment variable not set. Please set it before running.")
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set it with: export GOOGLE_API_KEY=your-api-key")
    sys.exit(1)


def find_tests() -> List[str]:
    """Find all test modules in the tests directory."""
    tests_dir = Path(__file__).parent / "tests"
    test_files = list(tests_dir.glob("test_*.py"))
    return [f"tests.{f.stem}" for f in test_files]


def run_tests(test_pattern: Optional[str] = None) -> bool:
    """Run the tests and return True if all pass."""
    logger.info("Running tests...")
    
    # Discover and load tests
    if test_pattern:
        test_suite = unittest.defaultTestLoader.loadTestsFromName(test_pattern)
    else:
        test_modules = find_tests()
        test_suite = unittest.TestSuite()
        for module in test_modules:
            try:
                suite = unittest.defaultTestLoader.loadTestsFromName(module)
                test_suite.addTest(suite)
            except ImportError as e:
                logger.warning(f"Could not import {module}: {e}")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return True if all tests pass
    return result.wasSuccessful()


def start_a2a_service(host: str, port: int, use_cort: bool = False) -> Process:
    """Start the A2A service."""
    logger.info(f"Starting A2A service on {host}:{port}...")
    
    # Create environment variables for the process
    env = os.environ.copy()
    env["HMS_A2A_USE_CORT"] = "1" if use_cort else "0"
    
    # Create the process
    process = Process(
        target=lambda: subprocess.run(
            [sys.executable, "-m", "finala2e", "--host", host, "--port", str(port)],
            env=env
        )
    )
    process.start()
    
    logger.info(f"A2A service started with process ID: {process.pid}")
    return process


def start_graph_agent(host: str, port: int, use_cort: bool = False) -> Process:
    """Start the graph agent."""
    logger.info(f"Starting graph agent on {host}:{port}...")
    
    # The command to run
    cmd = [sys.executable, "run_graph_agent.py"]
    
    # Add CoRT flag if enabled
    if use_cort:
        cmd.append("--cort")
    
    # Add host and port
    cmd.extend(["--host", host, "--port", str(port)])
    
    # Create the process
    process = Process(
        target=lambda: subprocess.run(cmd, env=os.environ.copy())
    )
    process.start()
    
    logger.info(f"Graph agent started with process ID: {process.pid}")
    return process


def start_government_agents(host: str, port: int, use_cort: bool = False) -> Process:
    """Start the government agents."""
    logger.info(f"Starting government agents on {host}:{port}...")
    
    # Create environment variables for the process
    env = os.environ.copy()
    env["HMS_A2A_USE_CORT"] = "1" if use_cort else "0"
    
    # The script to run for government agents
    cmd = [sys.executable, "examples/gov_program_assistant.py"]
    
    # Add host and port arguments if the script supports them
    cmd.extend(["--host", host, "--port", str(port)])
    
    # Create the process
    process = Process(
        target=lambda: subprocess.run(cmd, env=env)
    )
    process.start()
    
    logger.info(f"Government agents started with process ID: {process.pid}")
    return process


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start HMS-A2A services")
    parser.add_argument(
        "--service", 
        choices=["all", "a2a", "graph", "gov"], 
        default="all",
        help="Service to start (default: all)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=10000,
        help="Starting port number (default: 10000)"
    )
    parser.add_argument(
        "--cort",
        action="store_true",
        help="Enable Chain of Recursive Thoughts"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run tests before starting services"
    )
    
    args = parser.parse_args()
    
    # Banner
    print("\n" + "=" * 80)
    print(" HMS-A2A - Hierarchical Multi-agent System with Agent-to-Agent Protocol ".center(80, "="))
    print("=" * 80 + "\n")
    
    # System information
    print(f"Python: {sys.version.split()[0]}")
    print(f"CoRT: {'Enabled' if args.cort else 'Disabled'}")
    print(f"Service: {args.service}")
    print(f"Host: {args.host}")
    print(f"Starting Port: {args.port}")
    print()
    
    # Run tests if requested
    if args.test:
        if not run_tests():
            logger.error("Tests failed. Exiting.")
            sys.exit(1)
    
    # Start the requested services
    processes = []
    
    try:
        if args.service in ["all", "a2a"]:
            a2a_port = args.port
            processes.append(start_a2a_service(args.host, a2a_port, args.cort))
        
        if args.service in ["all", "graph"]:
            graph_port = args.port + 1 if args.service == "all" else args.port
            processes.append(start_graph_agent(args.host, graph_port, args.cort))
        
        if args.service in ["all", "gov"]:
            gov_port = args.port + 2 if args.service == "all" else args.port
            processes.append(start_government_agents(args.host, gov_port, args.cort))
        
        print("\n" + "-" * 80)
        print(" Services Started ".center(80, "-"))
        print("-" * 80 + "\n")
        
        # List of running services
        service_list = []
        port = args.port
        
        if args.service in ["all", "a2a"]:
            service_list.append(f"A2A Service: http://{args.host}:{port}/")
            port += 1
        
        if args.service in ["all", "graph"]:
            service_list.append(f"Graph Agent: http://{args.host}:{port}/")
            port += 1
        
        if args.service in ["all", "gov"]:
            service_list.append(f"Government Agents: http://{args.host}:{port}/")
        
        for service in service_list:
            print(f"- {service}")
        
        print("\nPress Ctrl+C to stop all services")
        
        # Wait for processes to complete
        for process in processes:
            process.join()
    
    except KeyboardInterrupt:
        print("\nShutting down services...")
        
        # Terminate all processes
        for process in processes:
            if process.is_alive():
                process.terminate()
        
        print("All services stopped.")
    
    except Exception as e:
        logger.error(f"Error starting services: {e}")
        
        # Terminate all processes
        for process in processes:
            if process.is_alive():
                process.terminate()
        
        sys.exit(1)


if __name__ == "__main__":
    main()