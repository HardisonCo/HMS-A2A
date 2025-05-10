#!/usr/bin/env python
"""
Chain of Recursive Thoughts Deal Negotiation Demo

This script demonstrates how to use Chain of Recursive Thoughts for deal negotiations
and trades between specialized agents to make better decisions.
"""

import os
import sys
from pathlib import Path
import json
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cort_deal_demo")

# Load environment variables
load_dotenv()

from specialized_agents.collaboration.deals import Deal, Problem, Solution, Player, Transaction
from specialized_agents.collaboration.cort_deal_negotiator import CoRTDealEvaluator


class DealDemo:
    """Demo for Chain of Recursive Thoughts in deal negotiations."""
    
    def __init__(self):
        """Initialize the demo."""
        # Check for required environment variables
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize the LLM model
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        # Create an LLM generator function
        def llm_generator(prompt: str) -> str:
            try:
                response = self.model.invoke(prompt).content
                return response
            except Exception as e:
                logger.error(f"Error in LLM generation: {e}")
                return f"Error generating response: {str(e)}"
        
        self.llm_generator = llm_generator
        
        # Create the CoRT Deal Evaluator
        self.evaluator = CoRTDealEvaluator(
            llm_generator=self.llm_generator,
            max_rounds=3,
            generate_alternatives=3,
            dynamic_rounds=True
        )
    
    def setup_sample_deal(self) -> Deal:
        """Set up a sample deal with problems, solutions, and players."""
        # Create a new deal
        deal = Deal(
            name="Healthcare Data Exchange Partnership",
            description="A collaboration between healthcare providers and technology companies to develop a secure data exchange platform",
            participants=["healthcare_provider", "tech_company", "regulatory_compliance"],
            deal_type="joint_venture",
            domains=["healthcare", "technology", "data_privacy"]
        )
        
        # Create players
        hospital_player = Player(
            agent_id="hospital",
            name="General Hospital",
            role="healthcare_provider",
            player_type="organization",
            capabilities=["patient_data", "medical_expertise", "clinical_workflows"],
            domain_expertise=["healthcare", "patient_care", "medical_records"]
        )
        
        tech_player = Player(
            agent_id="techcorp",
            name="TechCorp Solutions",
            role="tech_company",
            player_type="organization",
            capabilities=["cloud_infrastructure", "software_development", "data_analytics"],
            domain_expertise=["technology", "software", "data_security"]
        )
        
        compliance_player = Player(
            agent_id="compliance_advisor",
            name="Regulatory Compliance Advisor",
            role="regulatory_compliance",
            player_type="agent",
            capabilities=["regulatory_knowledge", "compliance_assessment", "risk_analysis"],
            domain_expertise=["healthcare_regulations", "data_privacy", "HIPAA"]
        )
        
        # Add players to deal
        deal.add_player(hospital_player)
        deal.add_player(tech_player)
        deal.add_player(compliance_player)
        
        # Create a problem
        data_exchange_problem = Problem(
            name="Secure Healthcare Data Exchange",
            description="Design a secure system for exchanging sensitive healthcare data between providers and technology partners while maintaining regulatory compliance and patient privacy",
            problem_type="technical_and_compliance",
            domain="healthcare",
            complexity="high",
            urgency="medium",
            success_criteria=[
                "Meets HIPAA compliance requirements",
                "Supports real-time data exchange",
                "Maintains data integrity and security",
                "Provides audit trails for all access",
                "Scalable to multiple healthcare providers"
            ],
            constraints=[
                "Must comply with all relevant healthcare regulations",
                "Cannot store patient identifiable information in unencrypted format",
                "Must integrate with existing hospital systems",
                "Must complete initial implementation within 6 months"
            ]
        )
        
        # Add problem to deal and assign owner
        deal.add_problem(data_exchange_problem)
        deal.assign_problem_owner(data_exchange_problem.id, hospital_player.id)
        
        # Create solutions
        cloud_solution = Solution(
            name="Cloud-Based Healthcare Data Exchange Platform",
            description="A fully managed cloud platform for secure healthcare data exchange using FHIR standards and end-to-end encryption",
            problem_id=data_exchange_problem.id,
            domain="technology",
            solution_type="cloud_platform",
            approach="Build a cloud-native platform using FHIR APIs, with end-to-end encryption and comprehensive access controls",
            resource_requirements={
                "development_team": "10 engineers",
                "infrastructure": "AWS/Azure cloud services",
                "timeframe": "6 months for MVP"
            },
            estimated_effort="High",
            expected_outcomes=[
                "Secure data exchange between providers and technology partners",
                "Real-time access to patient data with proper authorization",
                "Comprehensive audit trails for compliance reporting",
                "Scalable architecture to support growing data volumes"
            ],
            proposed_by=tech_player.id,
            status="proposed"
        )
        
        hybrid_solution = Solution(
            name="Hybrid On-Premise/Cloud Data Exchange System",
            description="A hybrid system that keeps sensitive data on-premise at the hospital while providing secure cloud interfaces for partners",
            problem_id=data_exchange_problem.id,
            domain="healthcare_technology",
            solution_type="hybrid_system",
            approach="Develop on-premise data hubs at healthcare facilities connected to a cloud orchestration layer for secure partner access",
            resource_requirements={
                "development_team": "8 engineers",
                "infrastructure": "On-premise servers + cloud services",
                "timeframe": "8 months for MVP"
            },
            estimated_effort="Medium-High",
            expected_outcomes=[
                "Maximum data security with sensitive information staying on-premise",
                "Controlled partner access through secure APIs",
                "Compliance with strict regulatory requirements",
                "Lower cloud storage costs for large datasets"
            ],
            proposed_by=hospital_player.id,
            status="proposed"
        )
        
        # Add solutions to deal
        deal.add_solution(cloud_solution)
        deal.add_solution(hybrid_solution)
        
        # Create a transaction
        license_transaction = Transaction(
            name="Technology Licensing Agreement",
            transaction_type="licensing",
            amount=250000.00,
            from_player=hospital_player.id,
            to_player=tech_player.id,
            currency="USD",
            description="Annual licensing fee for the data exchange platform and associated services",
            terms=[
                "Annual renewal with 30-day notice for termination",
                "Includes up to 500TB of data transfer monthly",
                "24/7 technical support for critical issues",
                "Quarterly security audits and compliance reports"
            ],
            status="pending"
        )
        
        # Add transaction to deal
        deal.add_transaction(license_transaction)
        
        return deal
    
    async def run_demo(self):
        """Run the demonstration."""
        print("\n" + "="*80)
        print(" Chain of Recursive Thoughts Deal Negotiation Demo ".center(80, "="))
        print("="*80 + "\n")
        
        # Set up a sample deal
        print("Setting up sample deal: Healthcare Data Exchange Partnership")
        deal = self.setup_sample_deal()
        
        # Demo 1: Evaluate the entire deal
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
        
        eval_result = self.evaluator.evaluate_deal(
            deal=deal,
            evaluator_role="Healthcare Compliance Officer",
            evaluation_criteria=evaluation_criteria
        )
        
        print(f"\nEvaluation completed after {eval_result['rounds_completed']} recursive thinking rounds.")
        print("\nFinal Evaluation:")
        print(eval_result["evaluation"])
        
        # Demo 2: Compare solutions
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
        
        comparison_result = self.evaluator.compare_solutions(
            problem=problem,
            solutions=solutions,
            evaluator_role="Healthcare Technology Architect",
            comparison_criteria=comparison_criteria
        )
        
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
        
        negotiation_result = self.evaluator.negotiate_transaction(
            transaction=transaction,
            from_player=from_player,
            to_player=to_player,
            negotiator_role="Healthcare Business Advisor",
            negotiation_context=negotiation_context
        )
        
        print(f"\nNegotiation completed after {negotiation_result['rounds_completed']} recursive thinking rounds.")
        print("\nRecommended Adjustments:")
        for rec in negotiation_result["recommendations"]:
            print(f"- {rec}")
        
        print("\nFull Negotiation Analysis:")
        print(negotiation_result["negotiation"])
        
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


if __name__ == "__main__":
    # Run the demo
    try:
        demo = DealDemo()
        asyncio.run(demo.run_demo())
    except Exception as e:
        logger.error(f"Error running demo: {e}", exc_info=True)
        print(f"Error running demo: {e}")
        print("Make sure you have set the GOOGLE_API_KEY environment variable.")