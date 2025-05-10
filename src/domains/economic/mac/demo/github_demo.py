"""
GitHub Issue Resolution Demo for the MAC architecture.

This module implements a demonstration of MAC capabilities for resolving
GitHub issues through multi-agent collaboration.
"""

import logging
import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4

from a2a.core import Task, TaskResult
from mac.supervisor_agent import SupervisorAgent
from mac.coordinator_agent import CoordinatorAgent
from mac.economist_agent import EconomistAgent
from mac.environment.state_store import StateStore
from mac.verification.checker import ExternalChecker
from mac.human_interface.interface import HumanQueryInterface
from mac.utils.config import load_config
from mac.demo.visualizer import MACCollaborationVisualizer
from mac.demo.github_service import GitHubService
from mac.domains.factory import DomainAgentFactory

class GitHubIssueDemo:
    """
    GitHub Issue Resolution Demo for the MAC architecture.
    
    This class demonstrates how the MAC model can be used to resolve GitHub issues
    through collaboration between specialized domain agents, with verification,
    economic optimization, and workflow management.
    """
    
    def __init__(
        self,
        supervisor = None,
        coordinator = None,
        economist = None,
        github_service = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the GitHub Issue Demo.
        
        Args:
            supervisor: Supervisor agent for task delegation
            coordinator: Coordinator agent for workflow management
            economist: Economist agent for resource allocation
            github_service: GitHub service for issue interaction
            config: Configuration dictionary
        """
        self.logger = logging.getLogger("MAC.Demo.GitHub")
        
        # Store provided components
        self.supervisor = supervisor
        self.coordinator = coordinator
        self.economist = economist
        self.github_service = github_service
        self.config = config or {}
        
        # Additional components
        self.state_store = None
        self.external_checker = None
        self.human_interface = None
        self.visualizer = None
        
        # Get state store from supervisor if available
        if self.supervisor:
            self.state_store = self.supervisor.state_store
            self.external_checker = self.supervisor.external_checker
            self.human_interface = self.supervisor.human_interface
        
        # Demo state
        self.initialized = bool(supervisor and coordinator and economist)
        self.demo_task_registry = {}
        
        # Create visualizer if state store is available
        if self.state_store:
            persistence_dir = self.config.get("persistence_dir", "mac_environment")
            self.visualizer = MACCollaborationVisualizer(
                state_store=self.state_store,
                output_dir=os.path.join(persistence_dir, "visualizations")
            )
        
        self.logger.info("GitHub Issue Demo initialized")
    
    async def run_demo(
        self, 
        issue_number: Optional[int] = None,
        issue_title: Optional[str] = None,
        issue_body: Optional[str] = None,
        create_issue: bool = False
    ) -> Dict[str, Any]:
        """
        Run the GitHub Issue Resolution Demo.
        
        Args:
            issue_number: GitHub issue number
            issue_title: Issue title (for creating new issue)
            issue_body: Issue body (for creating new issue)
            create_issue: Whether to create a new issue
            
        Returns:
            Result of the demo
        """
        if not self.initialized:
            return {"error": "Demo not initialized. Missing required components."}
        
        if not self.github_service:
            return {"error": "GitHub service not available."}
        
        # Get or create issue
        issue = None
        if create_issue and issue_title:
            self.logger.info(f"Creating new issue: {issue_title}")
            issue = await self.github_service.create_issue(
                title=issue_title,
                body=issue_body or "Created by MAC Demo"
            )
            if not issue:
                return {"error": "Failed to create issue"}
                
            issue_number = issue["number"]
            
        elif issue_number:
            self.logger.info(f"Fetching issue #{issue_number}")
            issue = await self.github_service.get_issue(issue_number)
            if not issue:
                return {"error": f"Issue #{issue_number} not found"}
                
        else:
            return {"error": "No issue specified"}
        
        # Start visualization
        if self.visualizer:
            self.visualizer.start()
        
        # Create task for MAC system
        task_id = f"github_issue_{issue_number}_{uuid4().hex[:8]}"
        task = Task(
            id=task_id,
            description=f"Resolve GitHub Issue #{issue_number}: {issue['title']}",
            metadata={
                "issue_number": issue_number,
                "issue_title": issue["title"],
                "issue_body": issue["body"],
                "issue_labels": issue.get("labels", []),
                "issue_url": issue.get("html_url", ""),
                "criticality": "medium"
            }
        )
        
        # Register task
        self.demo_task_registry[task_id] = {
            "issue": issue,
            "status": "created",
            "start_time": asyncio.get_event_loop().time()
        }
        
        try:
            # Calculate economic value of the task
            await self.economist.calculate_task_value(task_id, {
                "description": task.description,
                "domain": "development",  # Default domain
                "impact": "medium",
                "deficit_reduction": "medium"
            })
            
            # Start workflow session
            session = await self.coordinator.start_session(task_id, "github_demo_agent")
            
            # Let the task go through the workflow phases
            workflow_result = await self.coordinator.coordinate_task_execution(
                task_id=task_id, 
                workflow_phase=self.coordinator.WorkflowPhase.VERIFICATION
            )
            
            # Execute the task with the supervisor
            self.logger.info(f"Executing task {task_id}")
            result = await self.supervisor.execute_task(task)
            
            # End the session
            session_end = await self.coordinator.end_session(
                session_id=session["session_id"],
                journal={
                    "decisions": [
                        f"Executed GitHub issue resolution for #{issue_number}",
                        f"Issue title: {issue['title']}"
                    ],
                    "blockers": []
                }
            )
            
            # Update task registry
            self.demo_task_registry[task_id].update({
                "status": result.status,
                "result": result.result,
                "end_time": asyncio.get_event_loop().time(),
                "duration": asyncio.get_event_loop().time() - self.demo_task_registry[task_id]["start_time"],
                "workflow_result": workflow_result,
                "session_result": session_end
            })
            
            # Update agent performance metrics
            for domain, agent in self.supervisor.domain_agents.items():
                await self.economist.update_agent_performance(
                    agent_id=f"{domain}_agent",
                    task_id=task_id,
                    performance_data={
                        "status": result.status,
                        "quality_score": 0.9,
                        "execution_time": session_end["duration"],
                        "expected_time": 1800,  # 30 minutes
                        "domain": domain
                    }
                )
                
                # Distribute incentives
                await self.economist.distribute_incentives(
                    agent_id=f"{domain}_agent",
                    task_id=task_id
                )
            
            # Generate economic report
            economic_report = await self.economist.generate_economic_report()
            self.demo_task_registry[task_id]["economic_report"] = economic_report
            
            # Process result
            if result.status == "completed":
                # Comment on issue with result
                summary = self._generate_result_summary(result, economic_report)
                if "suggestions" in result.result:
                    suggested_resolution = result.result["suggestions"]
                    await self.github_service.add_comment(
                        issue_number=issue_number,
                        body=f"{summary}\n\n{suggested_resolution}"
                    )
                else:
                    await self.github_service.add_comment(
                        issue_number=issue_number,
                        body=summary
                    )
                
                # Create final visualization
                if self.visualizer:
                    visualization_path = self.visualizer.create_final_visualization(
                        task_id=task_id,
                        result=result
                    )
                    
                    # Add visualization to results
                    self.demo_task_registry[task_id]["visualization_path"] = visualization_path
            
            # Prepare demo result
            demo_result = {
                "task_id": task_id,
                "issue_number": issue_number,
                "status": result.status,
                "summary": self._generate_result_summary(result, economic_report),
                "duration": self.demo_task_registry[task_id]["duration"],
                "visualization_path": self.demo_task_registry[task_id].get("visualization_path"),
                "economic_health": economic_report["system_health"]
            }
            
            self.logger.info(f"Demo completed for issue #{issue_number}")
            return demo_result
            
        except Exception as e:
            self.logger.error(f"Error running demo: {str(e)}")
            return {"error": str(e)}
    
    def _generate_result_summary(
        self, 
        result: TaskResult, 
        economic_report: Dict[str, Any]
    ) -> str:
        """
        Generate a summary of the task result.
        
        Args:
            result: Task result
            economic_report: Economic system report
            
        Returns:
            Summary text
        """
        if result.status != "completed":
            return f"Task failed: {result.result.get('error', 'Unknown error')}"
        
        # Extract summary from result
        if "summary" in result.result:
            summary = result.result["summary"]
        else:
            # Generate basic summary
            summary = (
                f"# GitHub Issue Resolution by MAC\n\n"
                f"The Multi-Agent Collaboration (MAC) system has analyzed this issue "
                f"through specialized domain agents and external verification.\n\n"
                f"**Status:** {result.status}\n"
                f"**Confidence:** {result.metadata.get('confidence', 'N/A')}\n"
            )
        
        # Add economic and workflow information
        summary += (
            f"\n## MAC System Metrics\n\n"
            f"**Economic Health:** {economic_report['system_health']}\n"
            f"**Fairness Score:** {economic_report['economic_metrics']['fairness']:.2f}\n"
            f"**Efficiency Score:** {economic_report['economic_metrics']['efficiency']:.2f}\n"
            f"**Collaboration Score:** {economic_report['economic_metrics']['collaboration']:.2f}\n"
        )
        
        return summary
    
    async def get_demo_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the status of the demo.
        
        Args:
            task_id: Optional task ID to get specific task status
            
        Returns:
            Status information
        """
        if task_id:
            # Get specific task status
            if task_id in self.demo_task_registry:
                return {
                    "task_id": task_id,
                    "status": self.demo_task_registry[task_id]["status"],
                    "issue_number": self.demo_task_registry[task_id]["issue"]["number"],
                    "duration": self.demo_task_registry[task_id].get("duration", "In progress"),
                    "economic_health": self.demo_task_registry[task_id].get("economic_report", {}).get("system_health", "unknown")
                }
            else:
                return {"error": f"Task {task_id} not found"}
        else:
            # Get overall demo status
            return {
                "initialized": self.initialized,
                "active_tasks": len(self.demo_task_registry),
                "completed_tasks": sum(1 for task in self.demo_task_registry.values() if task.get("status") == "completed"),
                "task_ids": list(self.demo_task_registry.keys()),
                "has_supervisor": self.supervisor is not None,
                "has_coordinator": self.coordinator is not None,
                "has_economist": self.economist is not None
            }
    
    async def cleanup(self) -> None:
        """Clean up demo resources."""
        # Stop visualization
        if self.visualizer:
            self.visualizer.stop()
        
        # Persist final state
        if self.state_store:
            self.state_store.persist(
                path=os.path.join(
                    self.state_store.persistence_dir, 
                    "final_state.json"
                )
            )
        
        # Generate final economic report
        if self.economist:
            final_report = await self.economist.generate_economic_report()
            if self.state_store:
                self.state_store.record_economic_report(final_report)
            
        self.logger.info("Demo cleanup completed")