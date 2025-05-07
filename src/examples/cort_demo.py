#!/usr/bin/env python
"""
Chain of Recursive Thoughts (CoRT) Basic Demo

This script demonstrates the core CoRT processor with a simple example,
showing how it generates alternatives, evaluates them, and produces a
recursive thinking trace.
"""

import os
import sys
from pathlib import Path
import logging
import asyncio
from dotenv import load_dotenv
from pprint import pprint
from langchain_google_genai import ChatGoogleGenerativeAI

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cort_demo")

# Load environment variables
load_dotenv()

from common.utils.recursive_thought import get_recursive_thought_processor


class CoRTBasicDemo:
    """Basic demonstration of Chain of Recursive Thoughts."""
    
    def __init__(self, model_name="gemini-1.5-flash", max_rounds=3, 
                 generate_alternatives=3, dynamic_rounds=True, detailed_logging=False):
        """
        Initialize the demo with customizable parameters.
        
        Args:
            model_name: Name of the LLM model to use
            max_rounds: Maximum thinking rounds
            generate_alternatives: Number of alternatives to generate
            dynamic_rounds: Whether to dynamically determine rounds
            detailed_logging: Whether to enable detailed logging
        """
        # Check for required environment variables
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize the LLM model
        self.model = ChatGoogleGenerativeAI(model=model_name)
        
        # Create an LLM generator function
        def llm_generator(prompt: str) -> str:
            try:
                response = self.model.invoke(prompt).content
                return response
            except Exception as e:
                logger.error(f"Error in LLM generation: {e}")
                return f"Error generating response: {str(e)}"
        
        self.llm_generator = llm_generator
        
        # Create the CoRT processor
        self.processor = get_recursive_thought_processor(
            llm_fn=self.llm_generator,
            max_rounds=max_rounds,
            generate_alternatives=generate_alternatives,
            dynamic_rounds=dynamic_rounds,
            detailed_logging=detailed_logging
        )
    
    def run_standard_examples(self):
        """Run standard examples to demonstrate CoRT capabilities."""
        examples = [
            {
                "name": "Strategic Decision",
                "query": "What strategy should a small tech startup use to compete with established players in the AI market?",
                "context": {"domain": "business_strategy", "industry": "technology"}
            },
            {
                "name": "Complex Analysis",
                "query": "What are the potential impacts of quantum computing on cryptography and data security?",
                "context": {"domain": "computer_science", "complexity": "high"}
            },
            {
                "name": "Creative Writing",
                "query": "Write a short story about a robot that develops consciousness.",
                "context": {"domain": "creative_writing", "style": "science_fiction"}
            }
        ]
        
        results = {}
        
        for example in examples:
            print(f"\n{'-'*80}")
            print(f" Example: {example['name']} ".center(80, "-"))
            print(f"{'-'*80}\n")
            
            print(f"Query: {example['query']}")
            print(f"Processing with CoRT...\n")
            
            result = self.processor.process(
                query=example['query'],
                task_context=example['context']
            )
            
            results[example['name']] = result
            
            print(f"Processing completed after {result['rounds_completed']} rounds of thinking")
            print("\nInitial response:")
            print(f"{result['initial_response'][:300]}..." if len(result['initial_response']) > 300 else result['initial_response'])
            print("\nFinal response after CoRT:")
            print(f"{result['final_response'][:500]}..." if len(result['final_response']) > 500 else result['final_response'])
            
            # Show thinking trace summary
            print("\nThinking trace summary:")
            for round_data in result['thinking_trace']:
                if round_data['round'] == 0:
                    print(f"Round 0: Initial response")
                else:
                    alternatives_count = len(round_data.get('alternatives', []))
                    print(f"Round {round_data['round']}: Generated {alternatives_count} alternatives, selected #{round_data.get('best_index', 0)}")
        
        return results
    
    def run_with_custom_query(self, query, context=None):
        """
        Run CoRT with a custom query.
        
        Args:
            query: The query to process
            context: Optional context dictionary
            
        Returns:
            Processing result
        """
        print(f"\n{'-'*80}")
        print(f" Custom Query ".center(80, "-"))
        print(f"{'-'*80}\n")
        
        print(f"Query: {query}")
        print(f"Processing with CoRT...\n")
        
        result = self.processor.process(
            query=query,
            task_context=context or {}
        )
        
        print(f"Processing completed after {result['rounds_completed']} rounds of thinking")
        print("\nInitial response:")
        print(f"{result['initial_response'][:300]}..." if len(result['initial_response']) > 300 else result['initial_response'])
        print("\nFinal response after CoRT:")
        print(f"{result['final_response'][:500]}..." if len(result['final_response']) > 500 else result['final_response'])
        
        # Show thinking trace summary
        print("\nThinking trace summary:")
        for round_data in result['thinking_trace']:
            if round_data['round'] == 0:
                print(f"Round 0: Initial response")
            else:
                alternatives_count = len(round_data.get('alternatives', []))
                print(f"Round {round_data['round']}: Generated {alternatives_count} alternatives, selected #{round_data.get('best_index', 0)}")
        
        return result

    def demonstrate_round_determination(self):
        """
        Demonstrate how CoRT dynamically determines the appropriate number of rounds.
        """
        print(f"\n{'-'*80}")
        print(f" Dynamic Round Determination ".center(80, "-"))
        print(f"{'-'*80}\n")
        
        # Try with queries of varying complexity
        queries = [
            {
                "complexity": "Simple",
                "query": "What is the capital of France?",
                "expected_rounds": "1-2"
            },
            {
                "complexity": "Moderate",
                "query": "Explain the advantages and disadvantages of remote work.",
                "expected_rounds": "2-3"
            },
            {
                "complexity": "Complex",
                "query": "What are the ethical implications of artificial general intelligence and how should society prepare for its potential development?",
                "expected_rounds": "3+"
            }
        ]
        
        results = []
        
        for query_info in queries:
            print(f"\nDetermining rounds for {query_info['complexity']} query:")
            print(f"Query: {query_info['query']}")
            print(f"Expected rounds: {query_info['expected_rounds']}")
            
            # Create a dynamic round processor specifically for this test
            dynamic_processor = get_recursive_thought_processor(
                llm_fn=self.llm_generator,
                max_rounds=5,  # Higher max rounds to see variation
                dynamic_rounds=True,
                detailed_logging=False
            )
            
            # Determine rounds
            rounds = dynamic_processor._determine_rounds(query_info['query'])
            print(f"Determined rounds: {rounds}")
            
            results.append({
                "complexity": query_info['complexity'],
                "query": query_info['query'],
                "expected_rounds": query_info['expected_rounds'],
                "determined_rounds": rounds
            })
        
        return results


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the Chain of Recursive Thoughts Demo")
    parser.add_argument("--model", default="gemini-1.5-flash", help="LLM model to use")
    parser.add_argument("--rounds", type=int, default=3, help="Maximum thinking rounds")
    parser.add_argument("--alternatives", type=int, default=3, help="Number of alternatives per round")
    parser.add_argument("--dynamic", action="store_true", help="Use dynamic rounds determination", default=True)
    parser.add_argument("--detailed-logging", action="store_true", help="Enable detailed logging")
    parser.add_argument("--query", type=str, help="Custom query to process")
    parser.add_argument("--demo-type", choices=["standard", "custom", "rounds"], default="standard", 
                        help="Type of demo to run")
    
    args = parser.parse_args()
    
    # Run the demo
    try:
        demo = CoRTBasicDemo(
            model_name=args.model,
            max_rounds=args.rounds,
            generate_alternatives=args.alternatives,
            dynamic_rounds=args.dynamic,
            detailed_logging=args.detailed_logging
        )
        
        print("\n" + "="*80)
        print(" Chain of Recursive Thoughts (CoRT) Basic Demo ".center(80, "="))
        print("="*80 + "\n")
        
        print("Configuration:")
        print(f"- Model: {args.model}")
        print(f"- Max rounds: {args.rounds}")
        print(f"- Alternatives per round: {args.alternatives}")
        print(f"- Dynamic rounds: {'Yes' if args.dynamic else 'No'}")
        print(f"- Detailed logging: {'Yes' if args.detailed_logging else 'No'}")
        
        if args.demo_type == "standard":
            demo.run_standard_examples()
        elif args.demo_type == "custom" and args.query:
            demo.run_with_custom_query(args.query)
        elif args.demo_type == "rounds":
            demo.demonstrate_round_determination()
        else:
            if args.demo_type == "custom" and not args.query:
                print("Error: --query is required when using --demo-type=custom")
                sys.exit(1)
            demo.run_standard_examples()
        
        print("\n" + "="*80)
        print(" Demo Complete ".center(80, "="))
        print("="*80 + "\n")
        
        print("Benefits of Chain of Recursive Thoughts:")
        print("1. Generates and evaluates multiple alternatives")
        print("2. Improves responses through recursive self-critique")
        print("3. Adapts thinking depth to problem complexity")
        print("4. Provides transparent reasoning traces")
        print("5. Functions in various domains and tasks")
        
    except Exception as e:
        logger.error(f"Error running demo: {e}", exc_info=True)
        print(f"Error running demo: {e}")
        print("Make sure you have set the GOOGLE_API_KEY environment variable.")