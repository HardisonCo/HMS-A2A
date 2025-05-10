"""
Government Program Assistant Example

This example demonstrates how to create a Government Program Assistant agent
that helps civilians navigate government programs using the HMS-A2A framework
integrated with HMS-SVC program workflows.
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional

# HMS-A2A imports
from graph.react_agent import create_react_agent
from graph.a2a_tools import ToolRegistry

# Government agent imports
from gov_agents import (
    AgentFactory,
    AgencyRegistry,
    register_all_agencies_as_mcp_tools
)

# HMS-SVC integration imports
from integration import (
    register_hms_svc_tools,
    HMSSVCClient,
    ProgramWorkflow
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_program_assistant(
    agency_label: str = "SBA",  # Small Business Administration as default example
    base_url: str = "https://api.hms-svc.example.com",
    api_token: Optional[str] = None
):
    """Create a Government Program Assistant agent.
    
    This function creates a specialized agent that combines:
    1. Government agency knowledge (from gov_agents)
    2. Program workflow capabilities (from HMS-SVC)
    
    Args:
        agency_label: The government agency label (e.g., "SBA", "USDA")
        base_url: HMS-SVC API base URL
        api_token: HMS-SVC API token
        
    Returns:
        The configured agent
    """
    # 1. Set up the registry for tools
    registry = ToolRegistry()
    
    # 2. Create and register a civilian-facing government agent
    agency_registry = AgencyRegistry()
    civilian_agent = agency_registry.get_civilian_agent(agency_label)
    
    if not civilian_agent:
        logger.info(f"Creating new civilian agent for {agency_label}")
        civilian_agent = AgentFactory.create_civilian_agent(agency_label)
    
    # Register all agency tools with MCP
    gov_tools = register_all_agencies_as_mcp_tools()
    
    # 3. Set up HMS-SVC client and tools
    client = HMSSVCClient(base_url=base_url, api_token=api_token)
    workflow = ProgramWorkflow(client)
    
    # Register HMS-SVC tools
    hms_svc_tools = register_hms_svc_tools(registry, base_url, api_token)
    
    # 4. Create the Program Assistant agent
    system_message = f"""You are a {agency_label} Program Assistant. 
    
    Your job is to help civilians navigate {agency_label} programs and services.
    You can:
    1. Provide information about available programs
    2. Help users apply for programs
    3. Guide them through the application process
    4. Check the status of applications
    5. Assist with document submission
    
    Always be helpful, accurate, and respectful. When users need to follow a specific
    process, guide them through the steps one at a time. Use appropriate tools to
    create and manage program workflows.
    """
    
    agent = create_react_agent(
        name="program_assistant",
        registry=registry,
        system_message=system_message
    )
    
    return agent


async def example_loan_application_workflow(agent):
    """Example of creating and managing a loan application workflow.
    
    Args:
        agent: The Program Assistant agent
    """
    # 1. Create a new loan application program
    loan_program_result = await agent.execute_tool(
        "hms_svc_workflow", 
        action="create",
        name="Small Business Loan Application",
        description="Process for applying for an SBA-backed small business loan",
        protocols=[
            {
                "name": "Eligibility Pre-Screening",
                "description": "Determine initial eligibility for an SBA loan",
                "steps": [
                    {"type": "assessment", "module_id": "business_eligibility_assessment"},
                    {"type": "kpi", "module_id": "eligibility_score_tracker"}
                ]
            },
            {
                "name": "Document Collection",
                "description": "Collect required documentation for loan application",
                "steps": [
                    {"type": "document", "module_id": "business_plan_upload"},
                    {"type": "document", "module_id": "financial_statements_upload"},
                    {"type": "checkpoint", "module_id": "document_verification_checkpoint"}
                ]
            },
            {
                "name": "Application Review",
                "description": "Review and processing of the loan application",
                "steps": [
                    {"type": "assessment", "module_id": "credit_check_assessment"},
                    {"type": "assessment", "module_id": "financial_health_assessment"},
                    {"type": "nudge", "module_id": "review_status_notification"}
                ]
            }
        ]
    )
    
    # Get the created program ID
    program_id = loan_program_result.get("program", {}).get("id")
    
    # 2. Execute the first assessment step (eligibility)
    protocols_result = await agent.execute_tool(
        "hms_svc_protocol",
        action="list",
        program_id=program_id
    )
    
    # Get the first protocol ID
    protocol_id = protocols_result.get("protocols", [])[0].get("id")
    
    # Get the assessment step ID
    first_step_id = protocols_result.get("protocols", [])[0].get("steps", [])[0].get("id")
    
    # Execute the assessment module
    assessment_result = await agent.execute_tool(
        "hms_svc_workflow",
        action="execute_step",
        protocol_id=protocol_id,
        step_id=first_step_id,
        input_data={
            "business_name": "Example Small Business LLC",
            "years_in_operation": 3,
            "annual_revenue": 250000,
            "credit_score": 720,
            "loan_purpose": "Equipment purchase and working capital",
            "requested_amount": 150000
        }
    )
    
    # 3. Check workflow status
    workflow_status = await agent.execute_tool(
        "hms_svc_workflow",
        action="get_status",
        program_id=program_id
    )
    
    return workflow_status


async def example_conversation(agent):
    """Example conversation with the Program Assistant.
    
    Args:
        agent: The Program Assistant agent
    """
    # Initial user query
    user_query = "I'm interested in applying for a small business loan. Can you help me understand the process?"
    
    # Process the query
    response = await agent.process_message(user_query)
    print(f"User: {user_query}")
    print(f"Agent: {response.content}")
    
    # Follow-up question
    user_query = "What documents will I need to prepare for the application?"
    
    # Process the follow-up
    response = await agent.process_message(user_query)
    print(f"User: {user_query}")
    print(f"Agent: {response.content}")
    
    # Request to start the application
    user_query = "I'd like to start my application now. I run a small bakery that's been in business for 3 years."
    
    # Process the application request
    response = await agent.process_message(user_query)
    print(f"User: {user_query}")
    print(f"Agent: {response.content}")
    
    return response


async def main():
    """Main function to run the example."""
    # Get API credentials from environment (or use defaults for demo)
    base_url = os.environ.get("HMS_SVC_API_URL", "https://api.hms-svc.example.com")
    api_token = os.environ.get("HMS_SVC_API_TOKEN", "demo_token")
    
    # Create the Program Assistant agent
    agent = await create_program_assistant(
        agency_label="SBA",
        base_url=base_url,
        api_token=api_token
    )
    
    # Run example workflow
    workflow_status = await example_loan_application_workflow(agent)
    print("Workflow created with status:", workflow_status)
    
    # Run example conversation
    await example_conversation(agent)


if __name__ == "__main__":
    asyncio.run(main())