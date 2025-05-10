"""
Operations Domain Agent implementation for the MAC architecture.

This module provides the OperationsDomainAgent class, which specializes
in infrastructure, deployment, monitoring, and operational tasks.
"""

import logging
from typing import Any, Dict, List, Optional, Set

from mac.domains.base import DomainAgent
from mac.environment.state_store import StateStore
from mac.verification.checker import ExternalChecker
from mac.human_interface.interface import HumanQueryInterface


class OperationsDomainAgent(DomainAgent):
    """
    Operations Domain Agent for the MAC architecture.
    
    This agent specializes in operational tasks including:
    - Infrastructure management
    - Deployment and CI/CD
    - Monitoring and alerting
    - Performance optimization
    - Security operations
    - Disaster recovery
    
    Attributes:
        supported_platforms: Set of infrastructure platforms supported by this agent
        supported_tools: Set of operational tools supported by this agent
    """
    
    def __init__(
        self,
        name: str,
        state_store: StateStore,
        external_checker: ExternalChecker,
        human_interface: HumanQueryInterface,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Operations Domain Agent.
        
        Args:
            name: The name of the domain agent
            state_store: Reference to the shared state store
            external_checker: Reference to the external checker
            human_interface: Reference to the human query interface
            config: Domain-specific configuration
        """
        # Define operations-specific capabilities
        capabilities = {
            "infrastructure_management",
            "deployment",
            "monitoring",
            "performance_tuning",
            "security_operations",
            "disaster_recovery",
            "incident_response",
            "capacity_planning",
            "automation",
        }
        
        super().__init__(
            name=name,
            domain="operations",
            capabilities=capabilities,
            state_store=state_store,
            external_checker=external_checker,
            human_interface=human_interface,
            config=config,
        )
        
        # Operations-specific attributes
        self.supported_platforms = self.config.get("supported_platforms", {
            "aws", "azure", "gcp", "kubernetes", "docker", "on-premises"
        })
        self.supported_tools = self.config.get("supported_tools", {
            "terraform", "ansible", "jenkins", "github-actions", "prometheus", 
            "grafana", "elk", "datadog"
        })
        
        self.logger = logging.getLogger(f"mac.domains.operations.{name}")
        self.logger.info(f"Operations Domain Agent '{name}' initialized")
    
    async def _domain_specific_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform operations-specific analysis of a task.
        
        Analyzes the task to determine:
        - Required infrastructure platforms
        - Operational tools needed
        - Deployment considerations
        - Performance implications
        - Security impact
        - Monitoring requirements
        
        Args:
            task: The task to analyze
            
        Returns:
            Operations-specific analysis results
        """
        self.logger.info(f"Performing operations analysis for task: {task.get('id')}")
        
        # Extract task details
        task_type = task.get("type", "")
        task_description = task.get("description", "")
        task_context = task.get("context", {})
        
        # Initialize analysis result
        analysis = {
            "domain": "operations",
            "platforms_required": [],
            "tools_required": [],
            "services_affected": [],
            "operational_impact": "none",  # none, low, medium, high
            "security_implications": [],
            "estimated_effort": "medium",  # low, medium, high
            "operational_risks": [],
            "recommended_approach": "",
            "can_contribute": False,
        }
        
        # Determine if this is an operations task
        if any(keyword in task_description.lower() for keyword in 
               ["deploy", "infrastructure", "monitor", "performance", "security", 
                "incident", "scaling", "capacity", "backup", "recovery", "ci/cd",
                "automation", "cloud", "kubernetes", "docker", "terraform"]):
            analysis["can_contribute"] = True
        
        # If task is related to operations
        if "operations" in task_context or "infrastructure" in task_type.lower() or analysis["can_contribute"]:
            # Identify platforms from context
            for platform in self.supported_platforms:
                if platform in task_description.lower() or platform in str(task_context).lower():
                    if platform not in analysis["platforms_required"]:
                        analysis["platforms_required"].append(platform)
            
            # Identify tools from context
            for tool in self.supported_tools:
                if tool in task_description.lower() or tool in str(task_context).lower():
                    if tool not in analysis["tools_required"]:
                        analysis["tools_required"].append(tool)
            
            # Identify affected services
            service_indicators = task_context.get("services", [])
            if service_indicators:
                analysis["services_affected"] = service_indicators
            else:
                # Try to detect services from description
                services = self._identify_services(task_description, task_context)
                analysis["services_affected"] = services
            
            # Determine operational impact
            if "deployment" in task_description.lower() or "infrastructure" in task_description.lower():
                analysis["operational_impact"] = "medium"
                
                # Higher impact for core infrastructure
                core_infra = ["database", "network", "security", "production", "auth", "authentication"]
                if any(svc in str(analysis["services_affected"]).lower() for svc in core_infra):
                    analysis["operational_impact"] = "high"
            
            # Determine security implications
            if "security" in task_description.lower() or "vulnerability" in task_description.lower():
                analysis["security_implications"].append("security_review_required")
            
            if "authentication" in task_description.lower() or "authorization" in task_description.lower():
                analysis["security_implications"].append("auth_system_impact")
                
            if "database" in task_description.lower() or any("database" in svc.lower() for svc in analysis["services_affected"]):
                analysis["security_implications"].append("data_security_considerations")
                
            # Determine operational risks
            if analysis["operational_impact"] == "high":
                analysis["operational_risks"].append("service_disruption")
                
            if "migration" in task_description.lower() or "upgrade" in task_description.lower():
                analysis["operational_risks"].append("migration_complexity")
                
            if "scaling" in task_description.lower() or "performance" in task_description.lower():
                analysis["operational_risks"].append("performance_degradation")
        
            # Generate recommended approach
            analysis["recommended_approach"] = self._generate_recommended_approach(task, analysis)
        
        return analysis
    
    async def _domain_specific_execution(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform operations-specific execution of a task.
        
        This method implements the operations solution based on the prior analysis:
        - Infrastructure changes
        - Deployment processes
        - Monitoring configuration
        - Security implementations
        
        Args:
            task: The task to execute
            analysis: Previous analysis results
            
        Returns:
            Operations-specific execution results
        """
        self.logger.info(f"Executing operations task: {task.get('id')}")
        
        # Cannot contribute if analysis indicates so
        if not analysis.get("can_contribute", False):
            return {
                "domain": "operations",
                "success": False,
                "message": "Task is not applicable to operations domain",
                "artifacts": [],
            }
        
        # Initialize results
        results = {
            "domain": "operations",
            "success": False,
            "message": "",
            "artifacts": [],
            "infrastructure_changes": [],
            "deployment_actions": [],
            "monitoring_updates": [],
            "security_implementations": [],
        }
        
        try:
            # Task execution strategy based on task type and analysis
            task_type = task.get("type", "")
            
            # Infrastructure tasks
            if "infrastructure" in task_type.lower() or analysis.get("platforms_required"):
                infra_results = await self._implement_infrastructure_changes(task, analysis)
                results["infrastructure_changes"] = infra_results.get("changes", [])
                results["artifacts"].extend(infra_results.get("artifacts", []))
            
            # Deployment tasks
            if "deploy" in task_type.lower() or "ci/cd" in task_type.lower():
                deploy_results = await self._implement_deployment_actions(task, analysis)
                results["deployment_actions"] = deploy_results.get("actions", [])
                results["artifacts"].extend(deploy_results.get("artifacts", []))
            
            # Monitoring tasks
            if "monitor" in task_type.lower() or "observability" in task_type.lower():
                monitor_results = await self._implement_monitoring_updates(task, analysis)
                results["monitoring_updates"] = monitor_results.get("updates", [])
                results["artifacts"].extend(monitor_results.get("artifacts", []))
            
            # Security tasks
            if "security" in task_type.lower() or analysis.get("security_implications"):
                security_results = await self._implement_security_measures(task, analysis)
                results["security_implementations"] = security_results.get("implementations", [])
                results["artifacts"].extend(security_results.get("artifacts", []))
            
            # Mark task as successful
            results["success"] = True
            results["message"] = "Operations task executed successfully"
            
        except Exception as e:
            self.logger.error(f"Error executing operations task: {str(e)}", exc_info=True)
            results["success"] = False
            results["message"] = f"Error executing operations task: {str(e)}"
        
        return results
    
    async def _incorporate_human_feedback(
        self, results: Dict[str, Any], feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Incorporate human feedback into operations execution results.
        
        Args:
            results: Original execution results
            feedback: Human feedback
            
        Returns:
            Updated execution results
        """
        self.logger.info("Incorporating human feedback into operations results")
        
        updated_results = results.copy()
        
        # Extract feedback details
        feedback_content = feedback.get("content", {})
        approved = feedback.get("approved", False)
        comments = feedback.get("comments", "")
        
        if not approved:
            # Handle rejected results
            updated_results["success"] = False
            updated_results["message"] = f"Task execution rejected by operations reviewer. Comments: {comments}"
            
            # Apply specific feedback to infrastructure changes
            if "infrastructure_feedback" in feedback_content:
                infra_feedback = feedback_content["infrastructure_feedback"]
                updated_infra_changes = []
                for change in updated_results.get("infrastructure_changes", []):
                    change_id = change.get("id")
                    if change_id in infra_feedback:
                        change["definition"] = infra_feedback[change_id].get("updated_definition", change["definition"])
                        change["status"] = "updated_from_feedback"
                        change["feedback"] = infra_feedback[change_id].get("comments", "")
                    updated_infra_changes.append(change)
                updated_results["infrastructure_changes"] = updated_infra_changes
                
            # Apply deployment feedback
            if "deployment_feedback" in feedback_content:
                deploy_feedback = feedback_content["deployment_feedback"]
                updated_deploy_actions = []
                for action in updated_results.get("deployment_actions", []):
                    action_id = action.get("id")
                    if action_id in deploy_feedback:
                        action["steps"] = deploy_feedback[action_id].get("updated_steps", action["steps"])
                        action["status"] = "updated_from_feedback"
                        action["feedback"] = deploy_feedback[action_id].get("comments", "")
                    updated_deploy_actions.append(action)
                updated_results["deployment_actions"] = updated_deploy_actions
        else:
            # Handle approved results with optional improvements
            updated_results["message"] = "Task execution approved by operations reviewer"
            if comments:
                updated_results["message"] += f" with comments: {comments}"
        
        return updated_results
    
    # Helper methods
    def _identify_services(self, description: str, context: Dict[str, Any]) -> List[str]:
        """
        Identify affected services based on task description and context.
        
        Args:
            description: Task description
            context: Task context
            
        Returns:
            List of identified services
        """
        services = set()
        
        # Common service keywords to look for
        service_keywords = [
            "api", "auth", "database", "storage", "cache", "queue", "message", 
            "frontend", "backend", "web", "app", "service", "microservice",
            "gateway", "load balancer", "cdn", "analytics", "logging", "monitoring"
        ]
        
        # Extract service names from description and context
        description_lower = description.lower()
        context_str = str(context).lower()
        
        for keyword in service_keywords:
            # Check if the keyword is in the description or context
            if keyword in description_lower or keyword in context_str:
                # Extract the service name (keyword + adjacent words)
                services.add(keyword)
        
        # Check for specific service names in infrastructure files
        infra_files = context.get("infrastructure_files", [])
        for file in infra_files:
            file_name = file.get("name", "").lower()
            service_candidate = file_name.split(".")[0]
            if service_candidate and service_candidate not in ["terraform", "ansible", "deploy", "infra"]:
                services.add(service_candidate)
        
        return list(services)
    
    def _generate_recommended_approach(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a recommended approach for the operations task.
        
        Args:
            task: The task to generate a recommendation for
            analysis: Analysis results
            
        Returns:
            Recommended approach as a string
        """
        approach = []
        
        # Start with high-level approach based on task type
        task_type = task.get("type", "").lower()
        
        if "deployment" in task_type or "deploy" in task.get("description", "").lower():
            approach.append("1. Create deployment plan and checklist")
            approach.append("2. Set up CI/CD pipeline configuration")
            approach.append("3. Implement canary or blue-green deployment strategy")
            approach.append("4. Establish rollback procedure")
        
        elif "infrastructure" in task_type or "infrastructure" in task.get("description", "").lower():
            approach.append("1. Document current infrastructure state")
            approach.append("2. Design infrastructure changes with IaC templates")
            approach.append("3. Implement changes in staging environment")
            approach.append("4. Validate and promote to production")
        
        elif "monitoring" in task_type or "monitor" in task.get("description", "").lower():
            approach.append("1. Define key metrics and SLIs/SLOs")
            approach.append("2. Configure monitoring tools and dashboards")
            approach.append("3. Set up alerting rules and thresholds")
            approach.append("4. Document monitoring practices")
        
        elif "security" in task_type or "security" in task.get("description", "").lower():
            approach.append("1. Conduct security assessment of affected components")
            approach.append("2. Implement security controls and measures")
            approach.append("3. Perform security testing and validation")
            approach.append("4. Document security implementation")
        
        # Add platform-specific guidance
        if analysis.get("platforms_required"):
            platforms = ", ".join(analysis.get("platforms_required", []))
            approach.append(f"Target platforms: {platforms}")
        
        # Add tool-specific guidance
        if analysis.get("tools_required"):
            tools = ", ".join(analysis.get("tools_required", []))
            approach.append(f"Using tools: {tools}")
        
        # Add service-specific guidance
        if analysis.get("services_affected"):
            services = ", ".join(analysis.get("services_affected", []))
            approach.append(f"Services affected: {services}")
        
        # Add security guidance
        if analysis.get("security_implications"):
            implications = ", ".join(analysis.get("security_implications", []))
            approach.append(f"Security considerations: {implications}")
        
        # Add risk mitigation strategies
        if analysis.get("operational_risks"):
            risks = ", ".join(analysis.get("operational_risks", []))
            approach.append(f"Mitigate operational risks: {risks}")
            
            if "service_disruption" in analysis.get("operational_risks", []):
                approach.append("Implement with minimal service disruption, consider maintenance window")
        
        return "\n".join(approach)
    
    async def _implement_infrastructure_changes(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Implement infrastructure changes for the operations task.
        
        Args:
            task: The task to implement
            analysis: Analysis results
            
        Returns:
            Dictionary with infrastructure changes and artifacts
        """
        # This would call into component agents specialized in infrastructure
        # Simplified implementation for now
        return {
            "changes": [
                {
                    "id": f"infra_change_{i}",
                    "platform": platform,
                    "description": f"Infrastructure change for {platform}",
                    "definition": f"# Infrastructure as Code for {platform}\n# Would include actual IaC code here\n",
                    "status": "created",
                }
                for i, platform in enumerate(analysis.get("platforms_required", ["default_platform"]))
            ],
            "artifacts": [
                {
                    "type": "infrastructure_code",
                    "description": f"Infrastructure as Code for {task.get('id')}",
                    "path": f"infrastructure/{task.get('id')}/",
                }
            ]
        }
    
    async def _implement_deployment_actions(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Implement deployment actions for the operations task.
        
        Args:
            task: The task to implement
            analysis: Analysis results
            
        Returns:
            Dictionary with deployment actions and artifacts
        """
        # This would call into component agents specialized in deployment
        # Simplified implementation for now
        return {
            "actions": [
                {
                    "id": f"deploy_action_{i}",
                    "service": service,
                    "description": f"Deployment process for {service}",
                    "steps": [
                        f"1. Build {service} container",
                        f"2. Run tests for {service}",
                        f"3. Deploy {service} to staging",
                        f"4. Verify {service} in staging",
                        f"5. Deploy {service} to production"
                    ],
                    "status": "created",
                }
                for i, service in enumerate(analysis.get("services_affected", ["default_service"]))
            ],
            "artifacts": [
                {
                    "type": "deployment_plan",
                    "description": f"Deployment plan for {task.get('id')}",
                    "path": f"deployment/{task.get('id')}.md",
                },
                {
                    "type": "ci_cd_config",
                    "description": f"CI/CD configuration for {task.get('id')}",
                    "path": ".github/workflows/deploy.yml",
                }
            ]
        }
    
    async def _implement_monitoring_updates(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Implement monitoring updates for the operations task.
        
        Args:
            task: The task to implement
            analysis: Analysis results
            
        Returns:
            Dictionary with monitoring updates and artifacts
        """
        # This would call into component agents specialized in monitoring
        # Simplified implementation for now
        return {
            "updates": [
                {
                    "id": f"monitor_update_{i}",
                    "service": service,
                    "description": f"Monitoring configuration for {service}",
                    "metrics": [
                        f"{service}_requests_per_second",
                        f"{service}_error_rate",
                        f"{service}_latency_p95",
                        f"{service}_cpu_usage",
                        f"{service}_memory_usage"
                    ],
                    "alerts": [
                        f"{service}_high_error_rate",
                        f"{service}_high_latency"
                    ],
                    "status": "created",
                }
                for i, service in enumerate(analysis.get("services_affected", ["default_service"]))
            ],
            "artifacts": [
                {
                    "type": "monitoring_config",
                    "description": f"Monitoring configuration for {task.get('id')}",
                    "path": f"monitoring/{task.get('id')}.yml",
                },
                {
                    "type": "dashboard_config",
                    "description": f"Dashboard configuration for {task.get('id')}",
                    "path": f"dashboards/{task.get('id')}.json",
                }
            ]
        }
    
    async def _implement_security_measures(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Implement security measures for the operations task.
        
        Args:
            task: The task to implement
            analysis: Analysis results
            
        Returns:
            Dictionary with security implementations and artifacts
        """
        # This would call into component agents specialized in security
        # Simplified implementation for now
        return {
            "implementations": [
                {
                    "id": f"security_impl_{i}",
                    "area": implication.replace("_", " ").title(),
                    "description": f"Security implementation for {implication}",
                    "measures": [
                        f"1. Security scan for {implication}",
                        f"2. Implement security controls for {implication}",
                        f"3. Validate security measures for {implication}"
                    ],
                    "status": "created",
                }
                for i, implication in enumerate(analysis.get("security_implications", ["default_security"]))
            ],
            "artifacts": [
                {
                    "type": "security_doc",
                    "description": f"Security documentation for {task.get('id')}",
                    "path": f"security/{task.get('id')}.md",
                },
                {
                    "type": "security_checklist",
                    "description": f"Security checklist for {task.get('id')}",
                    "path": f"security/checklists/{task.get('id')}.yml",
                }
            ]
        }