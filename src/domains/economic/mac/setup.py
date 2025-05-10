"""
Setup and integration module for the MAC (Multi-Agent Collaboration) architecture.

This module provides functions for initializing and connecting all components
of the MAC architecture, creating a fully functional multi-agent system.
"""

import os
import json
import logging
import asyncio
import argparse
from typing import Dict, List, Any, Optional

# MAC Imports
from mac.supervisor_agent import SupervisorAgent, create_supervisor
from mac.coordinator_agent import CoordinatorAgent, create_coordinator
from mac.economist_agent import EconomistAgent, create_economist
from mac.environment.state_store import StateStore
from mac.verification.checker import ExternalChecker, create_checker
from mac.human_interface.interface import HumanQueryInterface, create_interface
from mac.domains.factory import DomainAgentFactory
from mac.utils.config import load_config, create_default_config


async def setup_mac(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Set up the MAC architecture components.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary of MAC components
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("MAC.Setup")
    logger.info("Initializing MAC architecture")
    
    # Load or create configuration
    config = {}
    if config_path:
        if os.path.exists(config_path):
            config = load_config(config_path)
            logger.info(f"Loaded configuration from {config_path}")
        else:
            logger.warning(f"Configuration file not found: {config_path}")
            if input("Create default configuration? (y/n): ").lower() == 'y':
                create_default_config(config_path)
                config = load_config(config_path)
                logger.info(f"Created default configuration at {config_path}")
    
    try:
        # Create core components
        env_config = config.get("environment", {})
        state_store = StateStore(
            persistence_dir=env_config.get("persistence_dir", "mac_environment"),
            max_history_length=env_config.get("max_history_length", 1000),
            auto_persist=env_config.get("auto_persist", True)
        )
        logger.info("Created Environment/State Store")
        
        # Create External Checker
        external_checker = create_checker(config_path)
        logger.info("Created External Checker")
        
        # Create Human Interface
        human_interface = create_interface(config_path)
        logger.info("Created Human Query Interface")
        
        # Create domain agents through factory
        domain_agent_factory = DomainAgentFactory(
            state_store=state_store,
            external_checker=external_checker,
            human_interface=human_interface
        )
        
        # Create one instance of each domain agent
        domain_config = config.get("domains", {})
        domain_agents = await domain_agent_factory.create_all_domain_agents(
            config=domain_config
        )
        logger.info(f"Created {len(domain_agents)} domain agents")
        
        # Create supervisor, coordinator, and economist agents
        supervisor = create_supervisor(
            domain_agents=domain_agents,
            state_store=state_store,
            external_checker=external_checker,
            human_interface=human_interface,
            config_path=config_path
        )
        logger.info("Created Supervisor Agent")
        
        coordinator = create_coordinator(
            supervisor_agent=supervisor,
            state_store=state_store,
            human_interface=human_interface,
            config_path=config.get("coordinator_config_path")
        )
        logger.info("Created Coordinator Agent")
        
        economist = create_economist(
            supervisor_agent=supervisor,
            coordinator_agent=coordinator,
            state_store=state_store,
            human_interface=human_interface,
            config_path=config.get("economist_config_path"),
            econ_data_path=config.get("econ_data_path")
        )
        logger.info("Created Economist Agent")
        
        # Register domain agents with state store and supervisor
        for domain, agent in domain_agents.items():
            supervisor.register_domain_agent(domain, agent)
            
            # Register with economist for resource allocation
            await economist.register_agent(
                agent_id=f"{domain}_agent",
                capabilities=[c for c in await agent.get_capabilities()],
                resource_needs={"compute": 100.0, "memory": 200.0, "time": 1000.0}
            )
        
        # Connect components
        components = {
            "supervisor": supervisor,
            "coordinator": coordinator,
            "economist": economist,
            "state_store": state_store,
            "external_checker": external_checker,
            "human_interface": human_interface,
            "domain_agents": domain_agents,
            "domain_agent_factory": domain_agent_factory
        }
        
        logger.info("MAC architecture initialization complete")
        return components
        
    except Exception as e:
        logger.error(f"Error during MAC setup: {str(e)}")
        raise


async def create_github_demo(
    components: Dict[str, Any], 
    repository_url: str,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a GitHub issue resolution demo using the MAC architecture.
    
    Args:
        components: MAC components
        repository_url: GitHub repository URL
        config: Additional configuration
        
    Returns:
        Demo components
    """
    from mac.demo.github_demo import GitHubIssueDemo
    from mac.demo.github_service import GitHubService
    
    # Extract components
    supervisor = components["supervisor"]
    coordinator = components["coordinator"]
    economist = components["economist"]
    
    # Create GitHub service
    github_service = GitHubService(
        repository_url=repository_url,
        auth_token=config.get("github_token") if config else None
    )
    
    # Create demo
    demo = GitHubIssueDemo(
        supervisor=supervisor,
        coordinator=coordinator,
        economist=economist,
        github_service=github_service,
        config=config
    )
    
    return {
        "demo": demo,
        "github_service": github_service
    }


async def run_workflow_pomodoro(
    components: Dict[str, Any],
    task_description: str,
    domain: str = "development"
) -> Dict[str, Any]:
    """
    Run a complete workflow Pomodoro session for a task.
    
    Args:
        components: MAC components
        task_description: Description of the task
        domain: Primary domain for the task
        
    Returns:
        Workflow execution result
    """
    # Extract components
    supervisor = components["supervisor"]
    coordinator = components["coordinator"]
    economist = components["economist"]
    
    # Create a task
    from a2a.core import Task
    task = Task(
        id=f"task_{int(asyncio.get_event_loop().time() * 1000)}",
        description=task_description,
        domain=domain
    )
    
    # Calculate task value
    await economist.calculate_task_value(task.id, {"description": task_description, "domain": domain})
    
    # Start a session
    session = await coordinator.start_session(task.id)
    
    # Let the task go through the workflow phases
    result = await coordinator.coordinate_task_execution(
        task_id=task.id, 
        workflow_phase=coordinator.WorkflowPhase.DEVELOPMENT
    )
    
    # Execute the task with the supervisor
    task_result = await supervisor.execute_task(task)
    
    # End the session
    session_end = await coordinator.end_session(
        session_id=session["session_id"],
        journal={
            "decisions": [
                f"Executed task: {task_description}",
                f"Used domain: {domain}"
            ],
            "blockers": []
        }
    )
    
    # Update agent performance
    for domain_agent in components["domain_agents"].values():
        await economist.update_agent_performance(
            agent_id=f"{domain_agent.domain}_agent",
            task_id=task.id,
            performance_data={
                "status": task_result.status,
                "quality_score": 0.9,
                "execution_time": session_end["duration"],
                "expected_time": 3600,  # One hour
                "domain": domain
            }
        )
    
    # Distribute incentives
    for domain_agent in components["domain_agents"].values():
        await economist.distribute_incentives(
            agent_id=f"{domain_agent.domain}_agent",
            task_id=task.id
        )
    
    # Generate economic report
    economic_report = await economist.generate_economic_report()
    
    return {
        "task": task.to_dict(),
        "task_result": task_result.to_dict(),
        "session": session_end,
        "workflow_result": result,
        "economic_report": economic_report
    }


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Set up MAC architecture components")
    parser.add_argument("--config", help="Path to configuration file", default="mac_config.json")
    parser.add_argument("--create-config", action="store_true", help="Create default configuration if not exists")
    parser.add_argument("--run-demo", action="store_true", help="Run a demo task")
    parser.add_argument("--task", default="Implement a function to calculate factorial", help="Demo task description")
    parser.add_argument("--domain", default="development", help="Demo task domain")
    args = parser.parse_args()
    
    # Create default configuration if requested
    if args.create_config and not os.path.exists(args.config):
        create_default_config(args.config)
        print(f"Created default configuration at {args.config}")
    
    # Set up MAC components
    loop = asyncio.get_event_loop()
    try:
        components = loop.run_until_complete(setup_mac(args.config))
        print("MAC setup completed successfully")
        print(f"Components: {', '.join(components.keys())}")
        
        # Run demo if requested
        if args.run_demo:
            print(f"\nRunning demo task: {args.task}")
            result = loop.run_until_complete(run_workflow_pomodoro(
                components=components,
                task_description=args.task,
                domain=args.domain
            ))
            print(f"Task result: {result['task_result']['status']}")
            print(f"Session duration: {result['session']['duration']:.2f} seconds")
            print(f"Economic system health: {result['economic_report']['system_health']}")
        
        # Keep running until interrupted
        print("\nMAC system is running. Press Ctrl+C to exit")
        loop.run_forever()
        
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        loop.close()


if __name__ == "__main__":
    main()