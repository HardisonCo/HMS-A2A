"""
Agriculture and Nutrition Agent Collaboration Example

This example demonstrates how the agriculture and nutrition agents can
collaborate on tasks that require expertise from both domains, such as
analyzing the nutritional impact of different farming practices.
"""

import asyncio
import json
from typing import Dict, Any, List

from specialized_agents.registry import AgentRegistry
from specialized_agents.collaboration import registry


async def run_nutritional_impact_analysis():
    """Run a collaborative analysis between agriculture and nutrition agents."""
    print("Setting up Agriculture and Nutrition agent collaboration...")
    
    # Get the agents
    agent_registry = AgentRegistry()
    agriculture_agent = agent_registry.create_agent("agriculture", "Specialist")
    nutrition_agent = agent_registry.create_agent("nutrition", "Specialist")
    
    print(f"Available agriculture tools: {agriculture_agent.get_available_mcp_tools()}")
    print(f"Available nutrition tools: {nutrition_agent.get_available_mcp_tools()}")
    
    # Start a collaboration session
    session_id = await agriculture_agent.start_collaboration(["agriculture", "nutrition"])
    print(f"Started collaboration session: {session_id}")
    
    # Step 1: Agriculture agent analyzes soil and crop management
    crop_data = {
        "cropType": "spinach",
        "acreage": 10.5,
        "location": "California Central Valley",
        "soilType": "sandy loam",
        "farmingSystem": "organic",
        "currentGrowthStage": "mature",
        "concerns": ["nutrient optimization", "maximizing nutritional content"]
    }
    
    print("\nAgriculture Agent: Analyzing crop management for nutritional optimization...")
    crop_result = await agriculture_agent.collaborate(
        session_id, 
        "crop_management", 
        crop_data
    )
    
    # Print a summary of the crop management results
    for part in crop_result:
        if part.get("type") == "text":
            print(f"\nAgriculture Agent Results Summary:\n{part['text'][:500]}...\n")
    
    # Step 2: Nutrition agent analyzes the nutritional value
    crop_name = crop_data["cropType"]
    farming_method = crop_data["farmingSystem"]
    
    nutrition_data = {
        "foodItem": crop_name,
        "productionMethod": farming_method,
        "portionSize": "100g",
        "processingMethod": "fresh",
        "populationGroup": "general",
    }
    
    print("Nutrition Agent: Analyzing nutritional value of crop...")
    nutrition_result = await nutrition_agent.collaborate(
        session_id, 
        "nutritional_assessment", 
        nutrition_data
    )
    
    # Print a summary of the nutritional assessment
    for part in nutrition_result:
        if part.get("type") == "text":
            print(f"\nNutrition Agent Results Summary:\n{part['text'][:500]}...\n")
    
    # Step 3: Nutrition agent generates a meal plan using the crop
    meal_plan_data = {
        "dietaryProfile": "balanced",
        "primaryIngredients": [crop_name],
        "restrictions": [],
        "calorieTarget": 2000,
        "mealsPerDay": 3,
        "dayCount": 1
    }
    
    print("Nutrition Agent: Generating meal plan using the crop...")
    meal_plan_result = await nutrition_agent.collaborate(
        session_id, 
        "meal_plan_generator", 
        meal_plan_data
    )
    
    # Print a summary of the meal plan
    for part in meal_plan_result:
        if part.get("type") == "text":
            print(f"\nNutrition Agent Meal Plan:\n{part['text'][:500]}...\n")
    
    # Step 4: Agriculture agent optimizes growing conditions for nutrition
    soil_data = {
        "soilSampleLocation": "California Central Valley",
        "cropType": crop_name,
        "previousCrops": ["lettuce", "kale"],
        "testingParameters": ["nitrogen", "phosphorus", "potassium", "micronutrients"]
    }
    
    print("Agriculture Agent: Analyzing soil for nutritional optimization...")
    soil_result = await agriculture_agent.collaborate(
        session_id, 
        "soil_analysis", 
        soil_data
    )
    
    # Print a summary of the soil analysis
    for part in soil_result:
        if part.get("type") == "text":
            print(f"\nAgriculture Agent Soil Analysis:\n{part['text'][:500]}...\n")
    
    print("\nCollaboration Results:")
    print("=====================")
    print(f"1. The Agriculture agent provided optimal growing conditions for {crop_name}")
    print(f"2. The Nutrition agent analyzed the nutritional value of {crop_name}")
    print(f"3. The Nutrition agent created meal plans incorporating {crop_name}")
    print(f"4. The Agriculture agent provided soil optimization for maximizing nutritional content")
    
    # Get the full collaboration context
    session = registry.get_collaboration_session(session_id)
    print("\nShared Context Developed During Collaboration:")
    print(json.dumps(session.shared_context, indent=2))


if __name__ == "__main__":
    asyncio.run(run_nutritional_impact_analysis())