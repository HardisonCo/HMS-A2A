"""
Example of Deal-based Collaboration Between Specialized Agents

This example demonstrates how agents from different domains can collaborate
using the Deal framework to solve interdisciplinary problems.
"""
import json
import asyncio
from typing import Dict, List, Any

# Import deal framework components
from specialized_agents.collaboration import Deal, Problem, Solution, Player, Transaction
from specialized_agents.collaboration.deal_tools import DealTools

# Import domain-specific agents and tools
from specialized_agents.healthcare.tools import HealthcareTools
from specialized_agents.agriculture.tools import register_agriculture_tools
from specialized_agents.standards_validation import StandardsValidator


async def run_collaboration_example():
    """Run a complete example of deal-based collaboration."""
    print("Starting Deal-Based Collaboration Example")
    print("=========================================")
    
    # Create a deal for agriculture-healthcare collaboration
    deal = Deal(
        name="Nutrient Optimization for Healthcare Outcomes",
        description="Develop agricultural practices to optimize nutrient content in crops for specific health outcomes",
        domains=["agriculture", "healthcare", "nutrition"]
    )
    
    # Add players from different domains
    agriculture_agent = Player(
        name="AgriBot",
        role="agriculture_specialist",
        capabilities=["crop_management", "soil_analysis", "sustainable_farming"]
    )
    
    healthcare_agent = Player(
        name="MedicalAdvisor",
        role="healthcare_specialist",
        capabilities=["nutrition_analysis", "health_outcomes", "disease_prevention"]
    )
    
    nutrition_agent = Player(
        name="NutrientOptimizer",
        role="nutrition_specialist",
        capabilities=["nutrient_profiling", "dietary_analysis", "bioavailability"]
    )
    
    human_expert = Player(
        name="Dr. Johnson",
        role="project_supervisor",
        capabilities=["final_approval", "expert_knowledge", "research_design"]
    )
    
    # Add players to the deal
    deal.add_player(agriculture_agent)
    deal.add_player(healthcare_agent)
    deal.add_player(nutrition_agent)
    deal.add_player(human_expert)
    
    print(f"Deal '{deal.name}' created with {len(deal.get_players())} players")
    
    # Define the problem
    problem = Problem(
        name="Nutrient-Enhanced Crop Development",
        description="Develop agricultural practices that enhance specific nutrients in crops to address common nutrient deficiencies in the local population",
        constraints=[
            "Must use sustainable farming practices",
            "Must adhere to organic certification where possible",
            "Must consider local growing conditions",
            "Must prioritize nutrients with highest public health impact"
        ],
        success_criteria=[
            "Demonstrated increase in target nutrients",
            "Economically viable for farmers",
            "Compliant with all agricultural regulations",
            "Verified health benefits through literature review"
        ]
    )
    
    # Add problem to the deal and assign owner
    deal.add_problem(problem)
    deal.assign_problem_owner(problem.id, "AgriBot")
    
    print(f"Problem '{problem.name}' added and assigned to AgriBot")
    
    # Healthcare agent adds context about nutrient needs
    healthcare_feedback = {
        "target_nutrients": ["iron", "zinc", "vitamin A", "folate"],
        "deficiency_prevalence": {
            "iron": "High - 35% of population",
            "zinc": "Medium - 20% of population",
            "vitamin_a": "High - 40% of population",
            "folate": "Medium - 15% of population"
        },
        "health_impacts": {
            "iron": "Anemia, fatigue, poor cognitive development",
            "zinc": "Immune dysfunction, growth retardation",
            "vitamin_a": "Night blindness, immune suppression",
            "folate": "Neural tube defects, anemia"
        }
    }
    
    # Create a transaction to share healthcare data
    data_transaction = Transaction(
        transaction_type="data_sharing",
        sender="MedicalAdvisor",
        receiver="AgriBot",
        resources=healthcare_feedback,
        conditions=["Data to be used only for this project", "No personally identifiable information included"]
    )
    
    deal.add_transaction(data_transaction)
    
    print("Healthcare data shared with Agriculture agent")
    
    # Agriculture agent proposes a solution
    solution = Solution(
        name="Multi-Crop Nutrient Enhancement Strategy",
        description="A system of complementary crops with enhanced nutrient profiles through optimized soil composition and growing practices",
        approach="Combine soil amendments, crop selection, and harvest timing to maximize nutrient content while maintaining yield and taste",
        resources_needed=[
            "Soil testing equipment",
            "Specialized organic amendments",
            "Seed varieties high in target nutrients",
            "Controlled growing environment for testing"
        ],
        estimated_effort="6 months for pilot, 18 months for full implementation"
    )
    
    # Add solution and link to problem
    deal.add_solution(solution, problem.id, "AgriBot")
    
    print(f"Solution '{solution.name}' proposed by AgriBot")
    
    # Nutrition agent evaluates the solution
    # First, validate against standards
    validator = StandardsValidator()
    
    # Check for compliance with agricultural standards
    validator.validate_field(
        "farming_practices",
        "organic soil amendments with mineral supplementation",
        ["AgFS"]
    )
    
    # Check nutrient health claims for compliance
    validator.validate_field(
        "nutrient_health_claims",
        "iron-rich crops to address anemia",
        ["HIPAA", "AgFS"]
    )
    
    evaluation_result = {
        "meets_criteria": True,
        "standards_compliant": len(validator.get_violations()) == 0,
        "violations": validator.get_violations(),
        "strengths": [
            "Targets highest-impact nutrients",
            "Maintains crop yield while enhancing nutrients",
            "Uses sustainable approaches compatible with existing farm practices"
        ],
        "concerns": [
            "Bioavailability of nutrients needs verification",
            "Seasonal variation may affect nutrient consistency",
            "Need to verify no unintended consequences on other nutrients"
        ],
        "suggested_improvements": [
            "Add post-harvest handling protocols to preserve nutrients",
            "Include companion planting to enhance nutrient uptake",
            "Add monitoring system for soil mineral balance"
        ]
    }
    
    # Record the evaluation in the deal
    deal.evaluate_solution(
        solution_id=solution.id,
        evaluator="NutrientOptimizer",
        meets_criteria=evaluation_result["meets_criteria"],
        evaluation_notes=json.dumps(evaluation_result, indent=2),
        suggested_improvements=evaluation_result["suggested_improvements"]
    )
    
    print("Solution evaluated by Nutrition agent")
    
    # Create implementation plan transaction
    implementation_plan = {
        "phases": [
            {
                "name": "Initial Testing",
                "duration": "2 months",
                "activities": [
                    "Soil analysis",
                    "Crop variety selection",
                    "Controlled growing environment setup"
                ]
            },
            {
                "name": "Field Trials",
                "duration": "4 months",
                "activities": [
                    "Small-scale field implementation",
                    "Nutrient content monitoring",
                    "Adjustment of protocols based on results"
                ]
            },
            {
                "name": "Full Implementation",
                "duration": "12 months",
                "activities": [
                    "Farmer training",
                    "Scaled implementation",
                    "Outcome tracking",
                    "Health impact assessment"
                ]
            }
        ],
        "resource_allocation": {
            "AgriBot": ["soil management", "crop selection", "growing protocols"],
            "NutrientOptimizer": ["nutrient analysis", "bioavailability testing"],
            "MedicalAdvisor": ["health outcome monitoring", "dietary recommendations"]
        }
    }
    
    plan_transaction = Transaction(
        transaction_type="implementation_plan",
        sender="AgriBot",
        receiver="all",
        resources=implementation_plan,
        conditions=["Requires approval from all players", "Subject to adjustment based on testing results"]
    )
    
    deal.add_transaction(plan_transaction)
    
    print("Implementation plan shared with all players")
    
    # Human expert reviews and approves the plan
    human_approval = Transaction(
        transaction_type="approval",
        sender="Dr. Johnson",
        receiver="all",
        resources={
            "decision": "approved",
            "comments": "Excellent integration of agricultural and nutritional expertise. Ensure regular coordination meetings between domains during implementation.",
            "conditions": [
                "Monthly progress reports required",
                "Budget approval needed for each phase",
                "Ethics review for any human testing components"
            ]
        },
        conditions=[]
    )
    
    deal.add_transaction(human_approval)
    
    print("Plan approved by human expert")
    
    # Finalize the deal with human review
    deal_dict = DealTools.finalize_deal(
        deal_dict=deal.to_dict(),
        finalized_by="Dr. Johnson",
        require_human_review=True
    )
    
    print("Deal finalized, pending final human review")
    
    # Print a summary of the collaboration
    print("\nCollaboration Summary:")
    print("---------------------")
    print(f"Deal: {deal.name}")
    print(f"Players: {', '.join([p.name for p in deal.get_players()])}")
    print(f"Problems: {len(deal.get_problems())}")
    print(f"Solutions: {len(deal.get_solutions())}")
    print(f"Transactions: {len(deal.get_transactions())}")
    print("\nVisualization of the deal:")
    
    # Generate a visualization of the deal
    visualization = DealTools.visualize_deal(deal.to_dict(), format="text")
    print(visualization)
    
    return deal


if __name__ == "__main__":
    # Run the collaboration example
    asyncio.run(run_collaboration_example())