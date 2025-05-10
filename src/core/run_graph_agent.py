#!/usr/bin/env python3
"""
Entry point script to run the graph agent with all available services.

This script checks that the required services are running, then launches the graph agent.
"""

import subprocess
import time
import os
import sys
import httpx
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_api_key():
    """Check if the API key is set and prompt for it if not."""
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        api_key = input("Please enter your Google API key: ")
        os.environ["GOOGLE_API_KEY"] = api_key

def check_service(host, port, service_name):
    """Check if a service is running at the specified host and port."""
    url = f"http://{host}:{port}/.well-known/agent.json"
    try:
        response = httpx.get(url, timeout=2.0)
        if response.status_code == 200:
            print(f"✅ {service_name} is running at {host}:{port}")
            return True
        else:
            print(f"❌ {service_name} returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {service_name} is not responding: {str(e)}")
        return False

def initialize_specialized_agents():
    """Initialize the specialized agents if they're not already running."""
    from specialized_agents.registry import AgentRegistry
    
    print("Initializing specialized agents...")
    registry = AgentRegistry()
    
    # Create an agriculture agent if it doesn't exist yet
    agriculture_agent_id = "agriculture_specialist"
    if agriculture_agent_id not in registry.get_all_agents():
        try:
            agriculture_agent = registry.create_agent("agriculture", "Specialist")
            print(f"✅ Created Agriculture Agent with {len(agriculture_agent.supported_standards)} supported standards")
        except Exception as e:
            print(f"❌ Failed to create Agriculture Agent: {str(e)}")
    else:
        print(f"✅ Agriculture Agent already initialized")
    
    # Create a telemedicine agent if it doesn't exist yet
    telemedicine_agent_id = "telemedicine_specialist"
    if telemedicine_agent_id not in registry.get_all_agents():
        try:
            telemedicine_agent = registry.create_agent("telemedicine", "Specialist")
            print(f"✅ Created Telemedicine Agent with {len(telemedicine_agent.supported_standards)} supported standards")
        except Exception as e:
            print(f"❌ Failed to create Telemedicine Agent: {str(e)}")
    else:
        print(f"✅ Telemedicine Agent already initialized")
    
    # Create a nutrition agent if it doesn't exist yet
    nutrition_agent_id = "nutrition_specialist"
    if nutrition_agent_id not in registry.get_all_agents():
        try:
            nutrition_agent = registry.create_agent("nutrition", "Specialist")
            print(f"✅ Created Nutrition Agent with {len(nutrition_agent.supported_standards)} supported standards")
        except Exception as e:
            print(f"❌ Failed to create Nutrition Agent: {str(e)}")
    else:
        print(f"✅ Nutrition Agent already initialized")
    
    # Add more specialized agents here as needed
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Run the Graph Agent with all available services")
    parser.add_argument("--skip-checks", action="store_true", help="Skip checking if services are running")
    parser.add_argument("--test", action="store_true", help="Run the agent in test mode")
    parser.add_argument("--query", type=str, help="Send a single query to the agent")
    
    args = parser.parse_args()
    
    # Check for API key
    check_api_key()
    
    # Check if the required services are running
    if not args.skip_checks:
        print("Checking if required services are running...")
        currency_service_running = check_service("localhost", 10000, "Currency Agent")
        math_service_running = check_service("localhost", 10001, "Math Agent")
        
        if not currency_service_running or not math_service_running:
            print("\n⚠️ One or more required services are not running.")
            choice = input("Do you want to continue anyway? (y/n): ")
            if choice.lower() != 'y':
                print("Exiting...")
                sys.exit(1)
    
    # Initialize specialized agents
    specialized_agents_initialized = initialize_specialized_agents()
    
    if not specialized_agents_initialized:
        print("\n⚠️ Failed to initialize specialized agents.")
        choice = input("Do you want to continue anyway? (y/n): ")
        if choice.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    # Construct the command to run the agent
    cmd = ["python", "-m", "graph.cli"]
    
    if args.test:
        cmd.append("--test")
    elif args.query:
        cmd.extend(["--query", args.query])
    
    # Run the agent
    print("\n🚀 Starting the Graph Agent with all available services...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()