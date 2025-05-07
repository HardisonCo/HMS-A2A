#!/usr/bin/env python
"""
Quick Run Chain of Recursive Thoughts Demo

This script provides a simple command-line runner for the CoRT deal negotiation demo.
It automates the setup and execution of the demo and provides options for customization.
"""

import argparse
import asyncio
import os
import logging
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Parse command line arguments
parser = argparse.ArgumentParser(description="Run the Chain of Recursive Thoughts Deal Demo")
parser.add_argument("--model", default="gemini-1.5-flash", help="LLM model to use")
parser.add_argument("--rounds", type=int, default=3, help="Maximum number of thinking rounds")
parser.add_argument("--alternatives", type=int, default=3, help="Number of alternatives per round")
parser.add_argument("--dynamic", action="store_true", help="Use dynamic rounds determination")
parser.add_argument("--detailed-logging", action="store_true", help="Enable detailed logging")
parser.add_argument("--output", default="cort_demo_results.json", help="Output file for full results")
parser.add_argument("--part", choices=["all", "evaluation", "comparison", "negotiation"], 
                    default="all", help="Which part of the demo to run")

args = parser.parse_args()

# Configure logging
log_level = logging.DEBUG if args.detailed_logging else logging.INFO
logging.basicConfig(level=log_level, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cort_demo_runner")

# Check for GOOGLE_API_KEY
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY environment variable not set.")
    print("Please set this environment variable before running the demo.")
    print("Example: export GOOGLE_API_KEY='your-api-key-here'")
    sys.exit(1)

# Import demo module and run selected parts
try:
    from examples.cort_deal_demo import DealDemo
    
    # Display configuration
    print("\n" + "="*80)
    print(" Chain of Recursive Thoughts Deal Demo Runner ".center(80, "="))
    print("="*80 + "\n")
    
    print("Configuration:")
    print(f"- Model: {args.model}")
    print(f"- Max rounds: {args.rounds}")
    print(f"- Alternatives per round: {args.alternatives}")
    print(f"- Dynamic rounds: {'Yes' if args.dynamic else 'No'}")
    print(f"- Detailed logging: {'Yes' if args.detailed_logging else 'No'}")
    print(f"- Demo parts to run: {args.part}")
    print(f"- Output file: {args.output}")
    
    print("\nInitializing demo...")
    
    # Create a customized run_demo function that only runs selected parts
    async def run_selected_demo(demo_instance):
        """Run only the selected parts of the demo."""
        # Import json for results saving
        import json
        
        # Store all results
        results = {}
        
        # Set up the sample deal
        print("Setting up sample deal: Healthcare Data Exchange Partnership")
        deal = demo_instance.setup_sample_deal()
        
        # Demo 1: Evaluate the entire deal
        if args.part in ["all", "evaluation"]:
            print("\n" + "-"*80)
            print(" Demo 1: Deal Evaluation ".center(80, "-"))
            print("-"*80 + "\n")
            
            print("Evaluating deal using CoRT as a Healthcare Compliance Officer...")
            evaluation_criteria = [
                {"name": "Regulatory Compliance", "description": "Does the deal meet all regulatory requirements including HIPAA, GDPR, and other relevant healthcare data regulations?"},
                {"name": "Data Security", "description": "How well does the deal address data security concerns and protect sensitive patient information?"},
                {"name": "Business Viability", "description": "Is the deal commercially viable for all parties involved?"},
                {"name": "Implementation Feasibility", "description": "Can the proposed solutions be implemented within the given constraints?"},
                {"name": "Long-term Sustainability", "description": "Does the deal support long-term partnership and ongoing compliance with evolving regulations?"}
            ]
            
            eval_result = demo_instance.evaluator.evaluate_deal(
                deal=deal,
                evaluator_role="Healthcare Compliance Officer",
                evaluation_criteria=evaluation_criteria
            )
            
            results["evaluation"] = eval_result
            
            print(f"\nEvaluation completed after {eval_result['rounds_completed']} recursive thinking rounds.")
            print("\nFinal Evaluation:")
            print(eval_result["evaluation"])
        
        # Demo 2: Compare solutions
        if args.part in ["all", "comparison"]:
            print("\n" + "-"*80)
            print(" Demo 2: Solution Comparison ".center(80, "-"))
            print("-"*80 + "\n")
            
            print("Comparing proposed solutions using CoRT as a Healthcare Technology Architect...")
            # Get the problem and solutions
            problem = list(deal.problems.values())[0]
            solutions = list(deal.solutions.values())
            
            comparison_criteria = [
                {"name": "Security", "description": "How effectively does the solution protect sensitive patient data?"},
                {"name": "Integration", "description": "How well does the solution integrate with existing hospital systems?"},
                {"name": "Scalability", "description": "Can the solution scale to accommodate growing data volumes and additional partners?"},
                {"name": "Cost-Efficiency", "description": "Is the solution cost-effective in both short and long-term?"},
                {"name": "Compliance", "description": "How well does the solution address regulatory compliance requirements?"}
            ]
            
            comparison_result = demo_instance.evaluator.compare_solutions(
                problem=problem,
                solutions=solutions,
                evaluator_role="Healthcare Technology Architect",
                comparison_criteria=comparison_criteria
            )
            
            results["comparison"] = comparison_result
            
            print(f"\nComparison completed after {comparison_result['rounds_completed']} recursive thinking rounds.")
            print("\nSolution Ranking:")
            for i, solution_id in enumerate(comparison_result["solution_ranking"]):
                # Find the solution name for this ID
                for solution in solutions:
                    if solution.id == solution_id:
                        print(f"#{i+1}: {solution.name}")
                        break
            
            print("\nFinal Comparison:")
            print(comparison_result["comparison"])
        
        # Demo 3: Negotiate transaction
        if args.part in ["all", "negotiation"]:
            print("\n" + "-"*80)
            print(" Demo 3: Transaction Negotiation ".center(80, "-"))
            print("-"*80 + "\n")
            
            print("Negotiating transaction terms using CoRT as a Healthcare Business Advisor...")
            # Get the transaction and players
            transaction = deal.transactions[0]
            from_player = deal.players[transaction.from_player]
            to_player = deal.players[transaction.to_player]
            
            negotiation_context = {
                "market_conditions": "Competitive market with several alternative technology providers",
                "hospital_budget_constraints": "Annual IT budget capped at $2M with 15% allocated to new initiatives",
                "tech_company_costs": "Development and maintenance costs estimated at $150K annually",
                "relationship_goal": "Establish long-term partnership with potential for expanded services",
                "regulatory_changes": "New healthcare data regulations expected within 18 months"
            }
            
            negotiation_result = demo_instance.evaluator.negotiate_transaction(
                transaction=transaction,
                from_player=from_player,
                to_player=to_player,
                negotiator_role="Healthcare Business Advisor",
                negotiation_context=negotiation_context
            )
            
            results["negotiation"] = negotiation_result
            
            print(f"\nNegotiation completed after {negotiation_result['rounds_completed']} recursive thinking rounds.")
            print("\nRecommended Adjustments:")
            for rec in negotiation_result["recommendations"]:
                print(f"- {rec}")
            
            print("\nFull Negotiation Analysis:")
            print(negotiation_result["negotiation"])
        
        # Save all results to file
        with open(args.output, "w") as f:
            # Convert to serializable format (remove nested objects)
            serializable_results = {}
            for key, value in results.items():
                serializable_results[key] = {k: v for k, v in value.items() 
                                           if k not in ["deal", "problem", "solutions", 
                                                      "transaction", "from_player", "to_player"]}
            
            json.dump(serializable_results, f, indent=2)
            print(f"\nFull results saved to {args.output}")
        
        # Print summary
        print("\n" + "="*80)
        print(" Demo Complete ".center(80, "="))
        print("="*80 + "\n")
        
        print("Chain of Recursive Thoughts enhances deal negotiations by:")
        print("1. Thoroughly considering multiple options before making decisions")
        print("2. Self-critiquing initial responses to find better alternatives")
        print("3. Dynamically adjusting thinking depth based on problem complexity")
        print("4. Providing transparent reasoning traces to build trust")
        print("5. Enabling more sophisticated deal evaluations and negotiations")
        
        print("\nThis approach helps specialized agents make better decisions through")
        print("structured collaboration and recursive reasoning about complex deals.")
    
    # Create and run the demo with custom settings
    demo = DealDemo()
    
    # Override the evaluator with custom settings
    from langchain_google_genai import ChatGoogleGenerativeAI
    from specialized_agents.collaboration.cort_deal_negotiator import CoRTDealEvaluator
    
    # Create a model with the specified configuration
    model = ChatGoogleGenerativeAI(model=args.model)
    
    # Create an LLM generator function
    def llm_generator(prompt):
        try:
            response = model.invoke(prompt).content
            return response
        except Exception as e:
            logger.error(f"Error in LLM generation: {e}")
            return f"Error generating response: {str(e)}"
    
    # Create a new evaluator with the specified parameters
    demo.evaluator = CoRTDealEvaluator(
        llm_generator=llm_generator,
        max_rounds=args.rounds,
        generate_alternatives=args.alternatives,
        dynamic_rounds=args.dynamic
    )
    
    # Run the selected parts of the demo
    asyncio.run(run_selected_demo(demo))
    
except Exception as e:
    logger.error(f"Error running demo: {e}", exc_info=True)
    print(f"Error running demo: {e}")
    print("For detailed error information, run with --detailed-logging")
    sys.exit(1)