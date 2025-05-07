"""
Development Domain Agent implementation for the MAC architecture.

This module provides the DevelopmentDomainAgent class, which specializes
in software development tasks, code analysis, architectural decisions,
and technical implementations.
"""

import logging
from typing import Any, Dict, List, Optional, Set

from mac.domains.base import DomainAgent
from mac.environment.state_store import StateStore
from mac.verification.checker import ExternalChecker
from mac.human_interface.interface import HumanQueryInterface


class DevelopmentDomainAgent(DomainAgent):
    """
    Development Domain Agent for the MAC architecture.
    
    This agent specializes in software development tasks including:
    - Code analysis and generation
    - Architectural decisions
    - Testing and quality assurance
    - Technical documentation
    - Performance optimization
    
    Attributes:
        supported_languages: Set of programming languages supported by this agent
        supported_frameworks: Set of frameworks and libraries supported by this agent
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
        Initialize the Development Domain Agent.
        
        Args:
            name: The name of the domain agent
            state_store: Reference to the shared state store
            external_checker: Reference to the external checker
            human_interface: Reference to the human query interface
            config: Domain-specific configuration
        """
        # Define development-specific capabilities
        capabilities = {
            "code_analysis",
            "code_generation",
            "code_review",
            "test_design",
            "architecture_design",
            "performance_optimization",
            "technical_documentation",
            "dependency_management",
            "build_integration",
        }
        
        super().__init__(
            name=name,
            domain="development",
            capabilities=capabilities,
            state_store=state_store,
            external_checker=external_checker,
            human_interface=human_interface,
            config=config,
        )
        
        # Development-specific attributes
        self.supported_languages = self.config.get("supported_languages", {
            "python", "javascript", "typescript", "rust", "go", "java", "c", "cpp"
        })
        self.supported_frameworks = self.config.get("supported_frameworks", {
            "react", "node", "django", "flask", "spring", "fastapi"
        })
        
        self.logger = logging.getLogger(f"mac.domains.development.{name}")
        self.logger.info(f"Development Domain Agent '{name}' initialized")
    
    async def _domain_specific_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform development-specific analysis of a task.
        
        Analyzes the task to determine:
        - Required programming languages and frameworks
        - Code components that need modification
        - Architectural implications
        - Testing requirements
        - Build and deployment considerations
        
        Args:
            task: The task to analyze
            
        Returns:
            Development-specific analysis results
        """
        self.logger.info(f"Performing development analysis for task: {task.get('id')}")
        
        # Extract task details
        task_type = task.get("type", "")
        task_description = task.get("description", "")
        task_context = task.get("context", {})
        
        # Initialize analysis result
        analysis = {
            "domain": "development",
            "languages_required": [],
            "frameworks_required": [],
            "components_affected": [],
            "architectural_impact": "none",  # none, low, medium, high
            "testing_requirements": [],
            "estimated_effort": "medium",  # low, medium, high
            "technical_risks": [],
            "recommended_approach": "",
            "can_contribute": False,
        }
        
        # Determine if this is a development task
        if any(keyword in task_description.lower() for keyword in 
               ["code", "implement", "develop", "fix", "bug", "feature", 
                "refactor", "performance", "architecture", "test"]):
            analysis["can_contribute"] = True
        
        # If task is related to code or implementation
        if "code" in task_context or "implementation" in task_type.lower():
            # Identify languages from context
            code_samples = task_context.get("code_samples", {})
            for lang, _ in code_samples.items():
                if lang in self.supported_languages:
                    if lang not in analysis["languages_required"]:
                        analysis["languages_required"].append(lang)
            
            # Identify frameworks from context
            for framework in self.supported_frameworks:
                if framework in task_description.lower() or framework in str(task_context).lower():
                    if framework not in analysis["frameworks_required"]:
                        analysis["frameworks_required"].append(framework)
            
            # Identify affected components
            file_paths = task_context.get("file_paths", [])
            analysis["components_affected"] = self._identify_components(file_paths)
            
            # Determine architectural impact
            if "architecture" in task_description.lower() or len(analysis["components_affected"]) > 3:
                analysis["architectural_impact"] = "medium"
                
                # Higher impact for core components
                core_components = ["core", "base", "foundation", "framework", "api"]
                if any(comp in str(analysis["components_affected"]).lower() for comp in core_components):
                    analysis["architectural_impact"] = "high"
            
            # Determine testing requirements
            if "bug" in task_description.lower() or "fix" in task_description.lower():
                analysis["testing_requirements"].append("regression_testing")
            
            if "new" in task_description.lower() or "feature" in task_description.lower():
                analysis["testing_requirements"].append("functional_testing")
                
            if "performance" in task_description.lower():
                analysis["testing_requirements"].append("performance_testing")
                
            # Determine technical risks
            if analysis["architectural_impact"] == "high":
                analysis["technical_risks"].append("architectural_complexity")
                
            if "dependency" in task_description.lower() or "upgrade" in task_description.lower():
                analysis["technical_risks"].append("dependency_management")
        
            # Generate recommended approach
            analysis["recommended_approach"] = self._generate_recommended_approach(task, analysis)
        
        return analysis
    
    async def _domain_specific_execution(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform development-specific execution of a task.
        
        This method implements the development solution based on the prior analysis:
        - Code implementation or modification
        - Test development
        - Documentation updates
        - Build integration
        
        Args:
            task: The task to execute
            analysis: Previous analysis results
            
        Returns:
            Development-specific execution results
        """
        self.logger.info(f"Executing development task: {task.get('id')}")
        
        # Cannot contribute if analysis indicates so
        if not analysis.get("can_contribute", False):
            return {
                "domain": "development",
                "success": False,
                "message": "Task is not applicable to development domain",
                "artifacts": [],
            }
        
        # Initialize results
        results = {
            "domain": "development",
            "success": False,
            "message": "",
            "artifacts": [],
            "code_changes": [],
            "tests_created": [],
            "documentation_updates": [],
            "build_integration": {},
        }
        
        try:
            # Task execution strategy based on task type and analysis
            task_type = task.get("type", "")
            
            # Code implementation tasks
            if "implementation" in task_type.lower() or "code" in task_type.lower():
                code_results = await self._implement_code_changes(task, analysis)
                results["code_changes"] = code_results.get("changes", [])
                results["artifacts"].extend(code_results.get("artifacts", []))
            
            # Testing tasks
            if "test" in task_type.lower() or "testing" in analysis.get("testing_requirements", []):
                test_results = await self._implement_tests(task, analysis, results["code_changes"])
                results["tests_created"] = test_results.get("tests", [])
                results["artifacts"].extend(test_results.get("artifacts", []))
            
            # Documentation updates
            doc_results = await self._update_documentation(task, analysis, results["code_changes"])
            results["documentation_updates"] = doc_results.get("updates", [])
            results["artifacts"].extend(doc_results.get("artifacts", []))
            
            # Build integration if needed
            if "build" in task_type.lower() or any("build" in comp for comp in analysis.get("components_affected", [])):
                build_results = await self._integrate_with_build(task, analysis, results["code_changes"])
                results["build_integration"] = build_results
                results["artifacts"].extend(build_results.get("artifacts", []))
            
            # Mark task as successful
            results["success"] = True
            results["message"] = "Development task executed successfully"
            
        except Exception as e:
            self.logger.error(f"Error executing development task: {str(e)}", exc_info=True)
            results["success"] = False
            results["message"] = f"Error executing development task: {str(e)}"
        
        return results
    
    async def _incorporate_human_feedback(
        self, results: Dict[str, Any], feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Incorporate human feedback into development execution results.
        
        Args:
            results: Original execution results
            feedback: Human feedback
            
        Returns:
            Updated execution results
        """
        self.logger.info("Incorporating human feedback into development results")
        
        updated_results = results.copy()
        
        # Extract feedback details
        feedback_content = feedback.get("content", {})
        approved = feedback.get("approved", False)
        comments = feedback.get("comments", "")
        
        if not approved:
            # Handle rejected results
            updated_results["success"] = False
            updated_results["message"] = f"Task execution rejected by human reviewer. Comments: {comments}"
            
            # Apply specific feedback to artifacts
            if "code_feedback" in feedback_content:
                code_feedback = feedback_content["code_feedback"]
                # Update code changes based on feedback
                updated_code_changes = []
                for change in updated_results.get("code_changes", []):
                    change_id = change.get("id")
                    if change_id in code_feedback:
                        change["content"] = code_feedback[change_id].get("updated_content", change["content"])
                        change["status"] = "updated_from_feedback"
                        change["feedback"] = code_feedback[change_id].get("comments", "")
                    updated_code_changes.append(change)
                updated_results["code_changes"] = updated_code_changes
                
            # Apply test feedback
            if "test_feedback" in feedback_content:
                test_feedback = feedback_content["test_feedback"]
                # Update tests based on feedback
                updated_tests = []
                for test in updated_results.get("tests_created", []):
                    test_id = test.get("id")
                    if test_id in test_feedback:
                        test["content"] = test_feedback[test_id].get("updated_content", test["content"])
                        test["status"] = "updated_from_feedback"
                        test["feedback"] = test_feedback[test_id].get("comments", "")
                    updated_tests.append(test)
                updated_results["tests_created"] = updated_tests
        else:
            # Handle approved results with optional improvements
            updated_results["message"] = "Task execution approved by human reviewer"
            if comments:
                updated_results["message"] += f" with comments: {comments}"
        
        return updated_results
    
    # Helper methods
    def _identify_components(self, file_paths: List[str]) -> List[str]:
        """
        Identify affected components based on file paths.
        
        Args:
            file_paths: List of file paths affected by the task
            
        Returns:
            List of identified components
        """
        components = set()
        
        for path in file_paths:
            parts = path.split("/")
            if len(parts) >= 2:
                # Typically, the first or second meaningful directory indicates the component
                component_candidates = parts[1:3]  # Take 2nd and 3rd parts as potential components
                for candidate in component_candidates:
                    # Skip common non-component directories
                    if candidate not in ["src", "tests", "docs", "bin", "scripts"]:
                        components.add(candidate)
        
        return list(components)
    
    def _generate_recommended_approach(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a recommended approach for the development task.
        
        Args:
            task: The task to generate a recommendation for
            analysis: Analysis results
            
        Returns:
            Recommended approach as a string
        """
        approach = []
        
        # Start with high-level approach based on task type
        task_type = task.get("type", "").lower()
        
        if "bug" in task_type or "fix" in task.get("description", "").lower():
            approach.append("1. Reproduce the issue in a test environment")
            approach.append("2. Identify root cause through code review and debugging")
            approach.append("3. Implement fix with appropriate tests")
            approach.append("4. Verify fix addresses the issue without side effects")
        
        elif "feature" in task_type or "implement" in task.get("description", "").lower():
            approach.append("1. Review requirements and acceptance criteria")
            approach.append("2. Design implementation approach")
            approach.append("3. Implement feature with test coverage")
            approach.append("4. Document the new functionality")
        
        elif "refactor" in task_type or "refactor" in task.get("description", "").lower():
            approach.append("1. Ensure comprehensive test coverage for affected code")
            approach.append("2. Implement refactoring incrementally")
            approach.append("3. Verify tests pass after each increment")
            approach.append("4. Document architectural changes if significant")
        
        # Add component-specific guidance
        if analysis.get("components_affected"):
            affected = ", ".join(analysis.get("components_affected", []))
            approach.append(f"Focus on the following components: {affected}")
        
        # Add language/framework-specific guidance
        if analysis.get("languages_required"):
            langs = ", ".join(analysis.get("languages_required", []))
            approach.append(f"Implement using: {langs}")
            
        if analysis.get("frameworks_required"):
            frameworks = ", ".join(analysis.get("frameworks_required", []))
            approach.append(f"Utilize frameworks: {frameworks}")
        
        # Add testing guidance
        if analysis.get("testing_requirements"):
            tests = ", ".join(analysis.get("testing_requirements", []))
            approach.append(f"Testing requirements: {tests}")
        
        # Add risk mitigation strategies
        if analysis.get("technical_risks"):
            risks = ", ".join(analysis.get("technical_risks", []))
            approach.append(f"Address technical risks: {risks}")
            
            if "architectural_complexity" in analysis.get("technical_risks", []):
                approach.append("Consider creating a design document for team review")
        
        return "\n".join(approach)
    
    async def _implement_code_changes(
        self, task: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Implement code changes for the development task.
        
        Args:
            task: The task to implement
            analysis: Analysis results
            
        Returns:
            Dictionary with code changes and artifacts
        """
        # This would call into component agents specialized in code implementation
        # Simplified implementation for now
        return {
            "changes": [
                {
                    "id": "code_change_1",
                    "file_path": f"path/to/{component}/implementation.py",
                    "description": f"Implemented solution for {task.get('id')}",
                    "content": "# Simulated code content would go here\n",
                    "status": "created",
                }
                for component in analysis.get("components_affected", ["default_component"])
            ],
            "artifacts": [
                {
                    "type": "code_implementation",
                    "description": f"Code implementation for {task.get('id')}",
                    "path": f"path/to/implementation/{task.get('id')}.py",
                }
            ]
        }
    
    async def _implement_tests(
        self, task: Dict[str, Any], analysis: Dict[str, Any], code_changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Implement tests for code changes.
        
        Args:
            task: The task being implemented
            analysis: Analysis results
            code_changes: Code changes that need tests
            
        Returns:
            Dictionary with tests and artifacts
        """
        # This would call into component agents specialized in testing
        # Simplified implementation for now
        return {
            "tests": [
                {
                    "id": f"test_{i}",
                    "file_path": f"tests/test_{change.get('file_path', 'default').split('/')[-1]}",
                    "description": f"Test for {change.get('description', 'change')}",
                    "content": "# Test code would go here\n",
                    "status": "created",
                }
                for i, change in enumerate(code_changes)
            ],
            "artifacts": [
                {
                    "type": "test_suite",
                    "description": f"Test suite for {task.get('id')}",
                    "path": f"tests/{task.get('id')}/",
                }
            ]
        }
    
    async def _update_documentation(
        self, task: Dict[str, Any], analysis: Dict[str, Any], code_changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update documentation for code changes.
        
        Args:
            task: The task being implemented
            analysis: Analysis results
            code_changes: Code changes that need documentation
            
        Returns:
            Dictionary with documentation updates and artifacts
        """
        # This would call into component agents specialized in documentation
        # Simplified implementation for now
        return {
            "updates": [
                {
                    "id": f"doc_{i}",
                    "file_path": f"docs/{change.get('file_path', 'default').split('/')[-1].replace('.py', '.md')}",
                    "description": f"Documentation for {change.get('description', 'change')}",
                    "content": "# Documentation content would go here\n",
                    "status": "created",
                }
                for i, change in enumerate(code_changes)
            ],
            "artifacts": [
                {
                    "type": "documentation",
                    "description": f"Documentation for {task.get('id')}",
                    "path": f"docs/{task.get('id')}.md",
                }
            ]
        }
    
    async def _integrate_with_build(
        self, task: Dict[str, Any], analysis: Dict[str, Any], code_changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Integrate changes with the build system.
        
        Args:
            task: The task being implemented
            analysis: Analysis results
            code_changes: Code changes to integrate
            
        Returns:
            Dictionary with build integration results and artifacts
        """
        # This would call into component agents specialized in build systems
        # Simplified implementation for now
        return {
            "build_command": f"build --target {task.get('id')}",
            "build_config_updates": [
                {
                    "file": "build.config.json",
                    "update": "{ \"newFeature\": true }"
                }
            ],
            "artifacts": [
                {
                    "type": "build_config",
                    "description": f"Build configuration for {task.get('id')}",
                    "path": "build.config.json",
                }
            ]
        }