#!/usr/bin/env python3
"""
Chain of Recursive Thoughts (CoRT) Basic Demo

This script demonstrates the basic functionality of the
Chain of Recursive Thoughts implementation.

Usage:
    python cort_basic_demo.py [--query QUERY] [--rounds ROUNDS] [--alternatives ALT]
"""

import argparse
import json
import os
import sys
from pathlib import Path
import logging

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from common.utils.recursive_thought import get_recursive_thought_processor
except ImportError:
    print("Error: Required modules not installed.")
    print("Please install with: pip install langchain langchain-google-genai google-generativeai")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_api_key():
    """Get the API key from environment or prompt user."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY environment variable not set.")
        api_key = input("Please enter your Google API key: ")
        if not api_key:
            print("No API key provided. Exiting.")
            sys.exit(1)
        os.environ["GOOGLE_API_KEY"] = api_key
    return api_key

def create_llm_generator():
    """Create an LLM generator function using Google Gemini."""
    # Get API key
    get_api_key()
    
    # Create the model
    try:
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        # Create a generator function
        def llm_generator(prompt):
            """Generate response from LLM."""
            logging.debug(f"Sending prompt: {prompt[:100]}...")
            try:
                response = model.invoke(prompt).content
                logging.debug(f"Received response: {response[:100]}...")
                return response
            except Exception as e:
                logging.error(f"Error generating response: {e}")
                return f"Error: {str(e)}"
        
        return llm_generator
    except Exception as e:
        logging.error(f"Error creating LLM: {e}")
        print(f"Error: Could not initialize LLM: {e}")
        sys.exit(1)

def demo_cort(query, rounds=3, alternatives=3, dynamic_rounds=True):
    """Run a Chain of Recursive Thoughts demo."""
    print(f"\n{'='*80}")
    print(f"Chain of Recursive Thoughts (CoRT) Demo".center(80))
    print(f"{'='*80}\n")
    
    print(f"Query: {query}")
    print(f"Max Rounds: {rounds}")
    print(f"Alternatives per round: {alternatives}")
    print(f"Dynamic rounds: {dynamic_rounds}")
    print(f"{'-'*80}\n")
    
    # Create the LLM generator
    llm_generator = create_llm_generator()
    
    # Create the CoRT processor
    processor = get_recursive_thought_processor(
        llm_fn=llm_generator,
        max_rounds=rounds,
        generate_alternatives=alternatives,
        dynamic_rounds=dynamic_rounds,
        detailed_logging=True
    )
    
    # Process the query
    print("Processing query with CoRT...\n")
    result = processor.process(query=query)
    
    # Display the results
    print(f"\n{'-'*80}")
    print("Results".center(80))
    print(f"{'-'*80}\n")
    
    print(f"Rounds completed: {result['rounds_completed']}")
    print(f"\nFinal response:\n{result['final_response']}")
    
    # Display thinking trace
    print(f"\n{'-'*80}")
    print("Thinking Trace".center(80))
    print(f"{'-'*80}\n")
    
    for i, round_data in enumerate(result["thinking_trace"]):
        round_num = round_data.get("round", i)
        if round_num == 0:
            print(f"Initial response:")
            print(f"{round_data.get('response', 'N/A')}")
        else:
            print(f"\nRound {round_num}:")
            alternatives = round_data.get("alternatives", [])
            best_index = round_data.get("best_index", 0)
            
            print(f"Generated {len(alternatives)} alternatives:")
            for j, alt in enumerate(alternatives):
                marker = "✓" if j == best_index else " "
                print(f"\n{marker} Alternative {j+1}:")
                print(f"{alt[:300]}{'...' if len(alt) > 300 else ''}")
    
    return result

def main():
    """Main function for the demo."""
    parser = argparse.ArgumentParser(description="Chain of Recursive Thoughts (CoRT) Demo")
    parser.add_argument(
        "--query", 
        default="What are the three most important considerations when designing a sustainable urban transportation system?",
        help="Query to process through CoRT"
    )
    parser.add_argument(
        "--rounds", 
        type=int, 
        default=3,
        help="Maximum number of thinking rounds"
    )
    parser.add_argument(
        "--alternatives", 
        type=int, 
        default=3,
        help="Number of alternatives to generate per round"
    )
    parser.add_argument(
        "--no-dynamic", 
        action="store_true",
        help="Disable dynamic round determination"
    )
    
    args = parser.parse_args()
    
    try:
        demo_cort(
            query=args.query,
            rounds=args.rounds,
            alternatives=args.alternatives,
            dynamic_rounds=not args.no_dynamic
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)

if __name__ == "__main__":
    main()