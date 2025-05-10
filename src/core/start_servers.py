#!/usr/bin/env python
"""
Start A2A Servers

This script starts the Currency Agent, Math Agent, and A2A MCP servers
required for the combined agent to function.
"""

import subprocess
import sys
import os
import signal
import time
import atexit

# Track the subprocesses
processes = []

def kill_processes():
    """Kill all spawned processes."""
    for process in processes:
        try:
            if process.poll() is None:  # If process is still running
                print(f"Terminating process PID {process.pid}...")
                process.terminate()
                process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"Force killing process PID {process.pid}...")
            process.kill()


def main():
    """Start the Currency, Math, and A2A MCP servers."""
    # Register the cleanup function
    atexit.register(kill_processes)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal. Shutting down servers...")
        kill_processes()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Path to the project root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    print("🚀 Starting A2A servers...")
    
    # Start Currency Agent on port 10000
    currency_process = subprocess.Popen(
        [sys.executable, "-m", "agent", "--host", "localhost", "--port", "10000"],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(currency_process)
    print(f"✅ Started Currency Agent (PID: {currency_process.pid}) on port 10000")
    
    # Give the first server a moment to start
    time.sleep(2)
    
    # Start Math Agent on port 10001
    math_process = subprocess.Popen(
        [sys.executable, "-m", "agent", "--host", "localhost", "--port", "10001"],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(math_process)
    print(f"✅ Started Math Agent (PID: {math_process.pid}) on port 10001")
    
    # Give the math server a moment to start
    time.sleep(2)
    
    # Start A2A MCP Server
    # Create environment with A2A endpoint configurations for external agents
    env = os.environ.copy()
    env["A2A_ENDPOINT_URLS"] = os.getenv("A2A_ENDPOINT_URLS", "http://localhost:41241")
    
    a2a_mcp_server_process = subprocess.Popen(
        [sys.executable, "-m", "common.server.a2a_mcp_server"],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env
    )
    processes.append(a2a_mcp_server_process)
    print(f"✅ Started A2A MCP Server (PID: {a2a_mcp_server_process.pid})")
    
    print("\n🌐 All servers are now running. Press Ctrl+C to shut down.")
    
    # Monitor the server outputs
    while all(process.poll() is None for process in processes):
        for process in processes:
            line = process.stdout.readline()
            if line:
                print(line, end='')
        time.sleep(0.1)
    
    # If we get here, one of the servers has stopped
    print("\n⚠️ One of the servers has stopped unexpectedly.")
    kill_processes()


if __name__ == "__main__":
    main()