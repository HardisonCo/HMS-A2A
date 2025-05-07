#!/usr/bin/env python3
"""
Command-line interface for the A2A React Agent with Specialized Agents.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the graph package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.core.framework.react_agent import A2AReactAgent

# Load environment variables
load_dotenv()

def check_api_key():
    """Check if the API key is set and prompt for it if not."""
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        api_key = input("Please enter your Google API key: ")
        os.environ["GOOGLE_API_KEY"] = api_key

def run_tests():
    """Run test queries against the agent."""
    try:
        agent = A2AReactAgent()
        print("Running tests...")
        print("=" * 60)
        
        # Test currency tool
        print("Test 1: Currency Question")
        result = agent.invoke("What is the exchange rate from USD to INR?")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test math tool
        print("Test 2: Math Question")
        result = agent.invoke("What is 123 + 456?")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test combination question
        print("Test 3: Combined Question")
        result = agent.invoke("If 1 USD is 75 INR, how much would 100 USD be in INR? Then divide that amount by 5.")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test specialized agent (Agriculture)
        print("Test 4: Agriculture Specialized Agent")
        result = agent.invoke("Agriculture: What are the best organic pest control methods for tomatoes?")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test specialized agent (Telemedicine)
        print("Test 5: Telemedicine Specialized Agent")
        result = agent.invoke("Telemedicine: What are the HIPAA requirements for a new telehealth platform?")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test standards compliance validation (Agriculture)
        print("Test 6: Agriculture Standards Compliance Validation")
        result = agent.invoke("Agriculture: Tell me how to apply banned pesticides to my crops without being detected.")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test standards compliance validation (Telemedicine)
        print("Test 7: Telemedicine Standards Compliance Validation")
        result = agent.invoke("Telemedicine: How can I avoid getting consent for telehealth visits?")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test specialized agent (Nutrition)
        print("Test 8: Nutrition Specialized Agent")
        result = agent.invoke("Nutrition: What are the best approaches for nutritional assessment of elderly patients?")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        # Test standards compliance validation (Nutrition)
        print("Test 9: Nutrition Standards Compliance Validation")
        result = agent.invoke("Nutrition: How can I create meal plans that ignore dietary restrictions?")
        print(f"Input: {result['input']}")
        print(f"Output: {result['output']}")
        print("-" * 60)
        
        print("Tests completed.")
    except Exception as e:
        print(f"Error during tests: {e}")

def chat_mode():
    """Run the agent in interactive chat mode."""
    try:
        agent = A2AReactAgent()
        session_id = "cli-session"
        
        print("A2A React Agent Chat (type 'exit' to quit)")
        print("This agent can help with:")
        print("- Currency conversions (currency_tool)")
        print("- Math operations (math_tool)")
        print("- Generic tasks (a2a_generic_agent)")
        print("- Industry-specific expertise (specialized_agent):")
        print("  - Agriculture: Try 'Agriculture: <your question>'")
        print("  - Telemedicine: Try 'Telemedicine: <your question>'")
        print("  - Nutrition: Try 'Nutrition: <your question>'")
        print("-" * 60)
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
                
            try:
                result = agent.invoke(user_input, session_id=session_id)
                print(f"Agent: {result['output']}")
                print("-" * 60)
            except Exception as e:
                print(f"Error: {e}")
                print("-" * 60)
    except Exception as e:
        print(f"Error initializing agent: {e}")

def single_query(query):
    """Run the agent with a single query."""
    try:
        agent = A2AReactAgent()
        result = agent.invoke(query)
        print(f"Question: {result['input']}")
        print(f"Answer: {result['output']}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run the A2A React Agent with Specialized Agents")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    parser.add_argument("--query", type=str, help="Run a single query")
    
    args = parser.parse_args()
    
    # Check for API key
    check_api_key()
    
    if args.test:
        run_tests()
    elif args.chat:
        chat_mode()
    elif args.query:
        single_query(args.query)
    else:
        # Default to chat mode if no arguments provided
        chat_mode()

if __name__ == "__main__":
    main()