"""
Supervisor Agent for the Multi-Agent Collaboration (MAC) Model.

This module implements the central orchestration component of the MAC architecture,
responsible for task delegation, monitoring, and results synthesis across domain agents.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
import logging
import time
import json
import asyncio
from uuid import uuid4

# A2A Imports
from a2a.core import Agent, Task, TaskResult
from graph.cort_react_agent import CoRTReactAgent

# MAC Imports
from mac.environment import StateStore
from mac.verification import ExternalChecker, VerificationResult
from mac.human_interface import HumanQueryInterface

class SupervisorAgent:
    """
    Supervisor Agent implementation for the MAC architecture.
    
    The Supervisor Agent is the central orchestrator in the MAC system, responsible for:
    1. Task decomposition and delegation to domain agents
    2. Monitoring task execution across domains
    3. Result synthesis from multiple domain contributions
    4. Verification through External Checker
    5. Human-in-the-loop escalation when necessary
    """
    
    def __init__(
        self, 
        name: str = "MAC-Supervisor",
        cort_depth: int = 3,
        domain_agents: Dict[str, Agent] = None,
        state_store: Optional[StateStore] = None,
        external_checker: Optional[ExternalChecker] = None,
        human_interface: Optional[HumanQueryInterface] = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the Supervisor Agent.
        
        Args:
            name: Name of the supervisor agent
            cort_depth: Maximum depth for recursive thought processes
            domain_agents: Dictionary of domain agents keyed by domain name
            state_store: Environment/State Store for persistent memory
            external_checker: Verification component for validating outputs
            human_interface: Interface for human-in-the-loop interactions
            config: Additional configuration parameters
        """
        self.name = name
        self.config = config or {}
        
        # Set up CoRT agent for enhanced reasoning
        self.cort_agent = CoRTReactAgent(
            use_cort=True,
            max_rounds=cort_depth,
            generate_alternatives=self.config.get("generate_alternatives", 2)
        )
        
        # Initialize components
        self.domain_agents = domain_agents or {}
        self.state_store = state_store
        self.external_checker = external_checker
        self.human_interface = human_interface
        
        # Task registry for tracking task execution
        self.task_registry = {}
        
        # Set up logging
        self.logger = logging.getLogger(f"MAC.{name}")
        self.logger.info(f"Initialized MAC Supervisor Agent: {name}")
        
        # Event listeners for monitoring
        self.event_listeners = {}
    
    def register_domain_agent(self, domain: str, agent: Agent) -> None:
        """
        Register a domain agent with the supervisor.
        
        Args:
            domain: Domain name (e.g., "development", "operations", "governance")
            agent: The domain agent to register
        """
        self.domain_agents[domain] = agent
        self.logger.info(f"Registered domain agent: {domain}")
        
        # Notify state store if available
        if self.state_store:
            self.state_store.register_agent(
                agent_id=f"{domain}_agent",
                agent_type="domain",
                metadata={"domain": domain}
            )
    
    def register_event_listener(self, event_type: str, callback: Callable) -> int:
        """
        Register a listener for specific event types.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
            
        Returns:
            Listener ID for later removal if needed
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        listener_id = len(self.event_listeners[event_type])
        self.event_listeners[event_type].append(callback)
        return listener_id
    
    def remove_event_listener(self, event_type: str, listener_id: int) -> None:
        """
        Remove a previously registered event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener_id: ID returned from register_event_listener
        """
        if event_type in self.event_listeners and 0 <= listener_id < len(self.event_listeners[event_type]):
            self.event_listeners[event_type].pop(listener_id)
    
    def _emit_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Emit an event to all registered listeners.
        
        Args:
            event_type: Type of event to emit
            event_data: Data associated with the event
        """
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": time.time()
        }
        
        # Notify listeners for this event type
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    listener(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener: {str(e)}")
        
        # Notify state store if available
        if self.state_store:
            self.state_store._publish_event(event_type, event_data)
    
    async def decompose_task(self, task: Task) -> List[Task]:
        """
        Decompose a complex task into subtasks using CoRT reasoning.
        
        Args:
            task: The main task to decompose
            
        Returns:
            List of subtasks with domain assignments
        """
        self.logger.info(f"Decomposing task {task.id}")
        
        # Use CoRT to generate an improved decomposition strategy
        decomposition_prompt = f"""
        Decompose the following task into optimal subtasks for different domains:
        
        TASK: {task.description}
        
        Available Domains:
        {list(self.domain_agents.keys())}
        
        For each subtask, specify:
        1. A clear description of what needs to be done
        2. Which domain should handle it
        3. Priority (high, medium, low)
        4. Dependencies on other subtasks (if any)
        5. Estimated complexity (high, medium, low)
        
        Return your decomposition as a JSON object with a 'subtasks' array.
        """
        
        # Create context for decomposition
        context = {
            "task": task.to_dict(), 
            "available_domains": list(self.domain_agents.keys())
        }
        
        # Run CoRT reasoning
        cort_response = await self.cort_agent.generate_response_with_cort(
            user_input=decomposition_prompt,
            context=context
        )
        
        # Extract JSON from response
        try:
            # Parse the CoRT response to extract JSON
            response_content = cort_response.get("content", "")
            json_part = self._extract_json(response_content)
            decomposition_result = json.loads(json_part)
        except Exception as e:
            self.logger.error(f"Failed to parse decomposition result: {str(e)}")
            # Fallback to simple decomposition
            decomposition_result = {"subtasks": [{
                "description": task.description,
                "domain": list(self.domain_agents.keys())[0] if self.domain_agents else "default",
                "priority": "medium",
                "dependencies": [],
                "estimated_complexity": "medium"
            }]}
        
        # Create subtask objects
        subtasks = []
        for i, subtask_data in enumerate(decomposition_result.get("subtasks", [])):
            subtask_id = f"{task.id}_sub_{i}_{uuid4().hex[:8]}"
            
            subtask = Task(
                id=subtask_id,
                description=subtask_data["description"],
                domain=subtask_data["domain"],
                parent_id=task.id,
                metadata={
                    "priority": subtask_data.get("priority", "medium"),
                    "dependencies": subtask_data.get("dependencies", []),
                    "estimated_complexity": subtask_data.get("estimated_complexity", "medium"),
                    "subtask_index": i
                }
            )
            subtasks.append(subtask)
        
        # Register decomposition in state store
        if self.state_store:
            self.state_store.record_task_decomposition(
                task_id=task.id, 
                subtask_ids=[st.id for st in subtasks]
            )
        
        # Record in task registry
        self.task_registry[task.id] = {
            "task": task,
            "subtasks": subtasks,
            "results": {},
            "status": "decomposed",
            "start_time": time.time()
        }
        
        # Emit event
        self._emit_event("task_decomposed", {
            "task_id": task.id,
            "subtask_count": len(subtasks),
            "subtask_ids": [st.id for st in subtasks]
        })
            
        self.logger.info(f"Decomposed task {task.id} into {len(subtasks)} subtasks")
        return subtasks
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON part from a text that might contain markdown and other content.
        
        Args:
            text: Text to extract JSON from
            
        Returns:
            JSON string
        """
        # Look for JSON between triple backticks
        import re
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        
        if json_match:
            return json_match.group(1)
        
        # If no triple backticks, try to find JSON-like structure
        json_match = re.search(r"(\{[\s\S]*\})", text)
        if json_match:
            return json_match.group(1)
        
        # Return the whole text as a fallback
        return text
    
    def assign_subtasks(self, subtasks: List[Task]) -> Dict[str, List[Task]]:
        """
        Assign subtasks to appropriate domain agents.
        
        Args:
            subtasks: List of subtasks to assign
            
        Returns:
            Dictionary mapping domain names to lists of tasks
        """
        assignments = {}
        
        # Group subtasks by domain
        for subtask in subtasks:
            domain = subtask.domain
            if domain not in assignments:
                assignments[domain] = []
            assignments[domain].append(subtask)
            
        # Update state store with assignments
        if self.state_store:
            for domain, domain_tasks in assignments.items():
                for task in domain_tasks:
                    self.state_store.assign_task(task.id, domain)
        
        # Emit event
        for domain, domain_tasks in assignments.items():
            self._emit_event("tasks_assigned", {
                "domain": domain,
                "task_count": len(domain_tasks),
                "task_ids": [task.id for task in domain_tasks]
            })
        
        self.logger.info(f"Assigned {len(subtasks)} subtasks to {len(assignments)} domains")
        return assignments
    
    async def execute_domain_tasks(self, assignments: Dict[str, List[Task]]) -> Dict[str, List[TaskResult]]:
        """
        Execute subtasks in their respective domains and collect results.
        
        Args:
            assignments: Dictionary mapping domain names to lists of tasks
            
        Returns:
            Dictionary mapping domain names to lists of task results
        """
        all_results = {}
        execution_tasks = []
        
        # Create async tasks for all domain executions
        for domain, tasks in assignments.items():
            if domain not in self.domain_agents:
                self.logger.warning(f"No agent registered for domain: {domain}")
                continue
                
            domain_agent = self.domain_agents[domain]
            
            # Create tasks for async execution
            for task in tasks:
                execution_tasks.append(self._execute_single_task(domain, domain_agent, task))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Task execution failed: {str(result)}")
                continue
                
            domain, task_result = result
            if domain not in all_results:
                all_results[domain] = []
            all_results[domain].append(task_result)
        
        return all_results
    
    async def _execute_single_task(self, domain: str, domain_agent: Agent, task: Task) -> Tuple[str, TaskResult]:
        """
        Execute a single task on a domain agent.
        
        Args:
            domain: Domain name
            domain_agent: Agent to execute the task
            task: Task to execute
            
        Returns:
            Tuple of (domain, task_result)
        """
        try:
            # Update task status
            if self.state_store:
                self.state_store.update_task_status(task.id, "in_progress")
            
            # Emit event
            self._emit_event("task_started", {
                "task_id": task.id,
                "domain": domain
            })
            
            # Execute task
            self.logger.info(f"Executing task {task.id} in domain {domain}")
            result = await domain_agent.execute_task(task)
            
            # Process result
            if self.state_store:
                self.state_store.update_task_status(task.id, "completed")
                self.state_store.record_task_result(task.id, result.to_dict())
            
            # Update task registry
            self.task_registry[task.parent_id]["results"][task.id] = result
            
            # Emit event
            self._emit_event("task_completed", {
                "task_id": task.id,
                "domain": domain
            })
            
            return domain, result
        
        except Exception as e:
            self.logger.error(f"Error executing task {task.id} in domain {domain}: {str(e)}")
            
            # Update status to failed
            if self.state_store:
                self.state_store.update_task_status(task.id, "failed")
            
            # Emit event
            self._emit_event("task_failed", {
                "task_id": task.id,
                "domain": domain,
                "error": str(e)
            })
            
            # Create failure result
            failure_result = TaskResult(
                task_id=task.id,
                status="failed",
                result={"error": str(e)},
                metadata={
                    "domain": domain,
                    "error_type": type(e).__name__
                }
            )
            
            # Update task registry
            self.task_registry[task.parent_id]["results"][task.id] = failure_result
            
            return domain, failure_result
    
    async def synthesize_results(self, domain_results: Dict[str, List[TaskResult]], task_id: str) -> TaskResult:
        """
        Synthesize results from multiple domain agents into a cohesive solution.
        
        Args:
            domain_results: Dictionary mapping domain names to lists of task results
            task_id: ID of the original task
            
        Returns:
            Synthesized task result
        """
        # Collect all subtask results
        all_subtask_results = []
        for domain_result_list in domain_results.values():
            all_subtask_results.extend(domain_result_list)
        
        # Check if we have any successful results
        successful_results = [r for r in all_subtask_results if r.status == "completed"]
        if not successful_results:
            self.logger.warning(f"No successful results to synthesize for task {task_id}")
            return TaskResult(
                task_id=task_id,
                status="failed",
                result={"error": "All subtasks failed"},
                metadata={
                    "failures": len(all_subtask_results)
                }
            )
        
        # Prepare synthesis prompt
        synthesis_prompt = f"""
        Synthesize these subtask results into a comprehensive solution for the original task.
        
        ORIGINAL TASK: {self.task_registry[task_id]["task"].description}
        
        SUBTASK RESULTS:
        """
        
        for i, result in enumerate(all_subtask_results):
            subtask = next((st for st in self.task_registry[task_id]["subtasks"] if st.id == result.task_id), None)
            if subtask:
                synthesis_prompt += f"\n\nSUBTASK {i+1}: {subtask.description}\n"
                synthesis_prompt += f"DOMAIN: {subtask.domain}\n"
                synthesis_prompt += f"STATUS: {result.status}\n"
                if result.status == "completed":
                    synthesis_prompt += f"RESULT: {json.dumps(result.result, indent=2)}\n"
                else:
                    synthesis_prompt += f"ERROR: {result.result.get('error', 'Unknown error')}\n"
        
        synthesis_prompt += """
        
        Synthesize these results into a cohesive solution. Your response should include:
        1. A summary of the overall solution
        2. Key components from each successful subtask
        3. Any adaptation needed due to failed subtasks
        4. Implementation considerations
        
        Return your synthesis as a JSON object with appropriate sections.
        """
        
        # Create context for synthesis
        synthesis_context = {
            "task_id": task_id,
            "task": self.task_registry[task_id]["task"].to_dict(),
            "subtask_results": [result.to_dict() for result in all_subtask_results]
        }
        
        # Run CoRT reasoning
        cort_response = await self.cort_agent.generate_response_with_cort(
            user_input=synthesis_prompt,
            context=synthesis_context
        )
        
        # Extract final result
        try:
            # Parse the CoRT response to extract JSON
            response_content = cort_response.get("content", "")
            json_part = self._extract_json(response_content)
            synthesis_result = json.loads(json_part)
        except Exception as e:
            self.logger.error(f"Failed to parse synthesis result: {str(e)}")
            # Create fallback result
            synthesis_result = {
                "summary": "Failed to synthesize results in structured format",
                "details": response_content
            }
        
        # Extract confidence from CoRT
        confidence = cort_response.get("metadata", {}).get("confidence", 0.8)
        
        # Create final result
        final_result = TaskResult(
            task_id=task_id,
            status="completed",
            result=synthesis_result,
            metadata={
                "cort_journal": cort_response.get("metadata", {}).get("journal", []),
                "subtask_results": [result.id for result in all_subtask_results],
                "confidence": confidence,
                "execution_time": time.time() - self.task_registry[task_id].get("start_time", 0)
            }
        )
        
        # Verify through external checker if available
        verification_result = None
        if self.external_checker:
            try:
                self.logger.info(f"Verifying result for task {task_id}")
                verification = await self.verify_result(final_result, self.task_registry[task_id]["task"])
                verification_result = verification
                
                if not verification.is_valid:
                    # Apply corrections if needed
                    final_result = await self._apply_corrections(final_result, verification, task_id)
            except Exception as e:
                self.logger.error(f"Error in verification: {str(e)}")
        
        # Update state store
        if self.state_store:
            self.state_store.record_task_synthesis(task_id, final_result.to_dict())
        
        # Emit event
        self._emit_event("task_synthesized", {
            "task_id": task_id,
            "verification": verification_result.to_dict() if verification_result else None
        })
        
        self.logger.info(f"Synthesized final result for task {task_id}")
        return final_result
    
    async def verify_result(self, result: TaskResult, task: Task) -> VerificationResult:
        """
        Verify a task result against its task definition.
        
        Args:
            result: The task result to verify
            task: The original task
            
        Returns:
            Verification result
        """
        if not self.external_checker:
            # Default to valid if no checker
            return VerificationResult(
                is_valid=True,
                confidence=0.5,
                feedback="No verification performed (no checker available)",
                suggestions=[]
            )
        
        verification = await self.external_checker.verify(result, task)
        
        # Check if human verification is needed
        if (self.human_interface and 
            self.human_interface.check_response_needed(verification, task.metadata)):
            
            # Request human feedback
            human_feedback = await self.request_human_verification(task, result, verification)
            
            # Update verification based on human feedback
            verification = self._update_verification_with_human_feedback(verification, human_feedback)
        
        return verification
    
    async def request_human_verification(
        self, 
        task: Task, 
        result: TaskResult, 
        verification: VerificationResult
    ) -> Dict[str, Any]:
        """
        Request human verification for a task result.
        
        Args:
            task: The original task
            result: The task result
            verification: The automated verification result
            
        Returns:
            Human feedback response
        """
        if not self.human_interface:
            return {
                "decision": "auto_approved",
                "feedback": "No human interface available"
            }
        
        # Create query content
        query_content = {
            "task": task.to_dict(),
            "result": result.to_dict(),
            "verification": verification.to_dict(),
            "criticality": task.metadata.get("criticality", "medium")
        }
        
        # Request feedback with timeout
        timeout = self.config.get("human_verification_timeout", 300)  # Default 5 minutes
        feedback = await self.human_interface.request_feedback(
            query_type="verification",
            query_content=query_content,
            timeout=timeout
        )
        
        return feedback.get("content", {})
    
    def _update_verification_with_human_feedback(
        self, 
        verification: VerificationResult, 
        human_feedback: Dict[str, Any]
    ) -> VerificationResult:
        """
        Update verification result with human feedback.
        
        Args:
            verification: The automated verification result
            human_feedback: Human feedback response
            
        Returns:
            Updated verification result
        """
        decision = human_feedback.get("decision", "").lower()
        
        if decision in ["approve", "approved"]:
            # Override verification to valid
            return VerificationResult(
                is_valid=True,
                confidence=1.0,  # Human verification has 100% confidence
                feedback=f"Human approved: {human_feedback.get('feedback', 'No feedback provided')}",
                suggestions=[]
            )
        elif decision in ["reject", "rejected"]:
            # Override verification to invalid
            suggestions = []
            if human_feedback.get("feedback"):
                suggestions = [human_feedback["feedback"]]
                
            return VerificationResult(
                is_valid=False,
                confidence=1.0,  # Human verification has 100% confidence
                feedback=f"Human rejected: {human_feedback.get('feedback', 'No feedback provided')}",
                suggestions=suggestions
            )
        elif decision in ["modify", "modified"]:
            # Suggest modifications
            suggestions = []
            if human_feedback.get("modifications"):
                if isinstance(human_feedback["modifications"], list):
                    suggestions = human_feedback["modifications"]
                else:
                    suggestions = [human_feedback["modifications"]]
                    
            return VerificationResult(
                is_valid=False,  # Needs modification
                confidence=1.0,  # Human verification has 100% confidence
                feedback=f"Human requested modifications: {human_feedback.get('feedback', 'No feedback provided')}",
                suggestions=suggestions
            )
        else:
            # Keep original verification but add human feedback
            verification.feedback += f"\nHuman feedback: {human_feedback.get('feedback', 'No feedback provided')}"
            return verification
    
    async def _apply_corrections(
        self, 
        result: TaskResult, 
        verification: VerificationResult, 
        task_id: str
    ) -> TaskResult:
        """
        Apply corrections to a result based on verification feedback.
        
        Args:
            result: The task result to correct
            verification: The verification result
            task_id: The original task ID
            
        Returns:
            Corrected task result
        """
        # Create correction prompt
        correction_prompt = f"""
        Revise the solution based on verification feedback.
        
        ORIGINAL TASK: {self.task_registry[task_id]["task"].description}
        
        CURRENT SOLUTION:
        {json.dumps(result.result, indent=2)}
        
        VERIFICATION FEEDBACK:
        {verification.feedback}
        
        SUGGESTED CORRECTIONS:
        {json.dumps(verification.suggestions, indent=2)}
        
        Please revise the solution to address all feedback and suggestions.
        Return your revised solution as a JSON object with the same structure as the original.
        """
        
        # Create context
        correction_context = {
            "original_result": result.to_dict(),
            "verification_feedback": verification.feedback,
            "correction_suggestions": verification.suggestions,
            "task": self.task_registry[task_id]["task"].to_dict()
        }
        
        # Run CoRT reasoning
        cort_response = await self.cort_agent.generate_response_with_cort(
            user_input=correction_prompt,
            context=correction_context
        )
        
        # Extract corrected result
        try:
            # Parse the CoRT response to extract JSON
            response_content = cort_response.get("content", "")
            json_part = self._extract_json(response_content)
            corrected_result = json.loads(json_part)
        except Exception as e:
            self.logger.error(f"Failed to parse correction result: {str(e)}")
            # Fallback to keeping original with a note
            corrected_result = result.result
            corrected_result["correction_note"] = "Failed to apply corrections: " + str(e)
        
        # Update result
        corrected_task_result = TaskResult(
            task_id=result.task_id,
            status=result.status,
            result=corrected_result,
            metadata={
                **result.metadata,
                "verification": verification.to_dict(),
                "corrections_applied": True,
                "correction_journal": cort_response.get("metadata", {}).get("journal", [])
            }
        )
        
        return corrected_task_result
    
    async def execute_task(self, task: Task) -> TaskResult:
        """
        Primary execution method for handling a task end-to-end.
        
        Args:
            task: The task to execute
            
        Returns:
            Task result
        """
        self.logger.info(f"Starting execution of task {task.id}")
        
        # Record task in state store
        if self.state_store:
            self.state_store.record_task(task.to_dict())
        
        # Emit event
        self._emit_event("task_execution_started", {
            "task_id": task.id,
            "description": task.description
        })
        
        try:
            # Decompose task into subtasks
            subtasks = await self.decompose_task(task)
            
            # Assign subtasks to domains
            assignments = self.assign_subtasks(subtasks)
            
            # Execute domain tasks
            domain_results = await self.execute_domain_tasks(assignments)
            
            # Synthesize results
            final_result = await self.synthesize_results(domain_results, task.id)
            
            # Emit completion event
            self._emit_event("task_execution_completed", {
                "task_id": task.id,
                "status": final_result.status
            })
            
            self.logger.info(f"Completed execution of task {task.id}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {str(e)}")
            
            # Update task status
            if self.state_store:
                self.state_store.update_task_status(task.id, "failed")
            
            # Emit event
            self._emit_event("task_execution_failed", {
                "task_id": task.id,
                "error": str(e)
            })
            
            # Return failure result
            return TaskResult(
                task_id=task.id,
                status="failed",
                result={"error": str(e)},
                metadata={
                    "error_type": type(e).__name__
                }
            )


# Factory function for creating supervisor
def create_supervisor(
    domain_agents: Dict[str, Agent] = None,
    state_store: Optional[StateStore] = None,
    external_checker: Optional[ExternalChecker] = None,
    human_interface: Optional[HumanQueryInterface] = None,
    config_path: Optional[str] = None
) -> SupervisorAgent:
    """
    Create and configure a Supervisor Agent.
    
    Args:
        domain_agents: Dictionary of domain agents
        state_store: Environment/State Store for persistent memory
        external_checker: Verification component
        human_interface: Human-in-the-loop interface
        config_path: Path to configuration file
        
    Returns:
        Configured SupervisorAgent
    """
    # Load configuration if path provided
    config = {}
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading supervisor configuration: {str(e)}")
    
    # Create supervisor
    supervisor = SupervisorAgent(
        name=config.get("name", "MAC-Supervisor"),
        cort_depth=config.get("cort_depth", 3),
        domain_agents=domain_agents or {},
        state_store=state_store,
        external_checker=external_checker,
        human_interface=human_interface,
        config=config
    )
    
    # Register state store with supervisor reference if needed
    if state_store:
        state_store.register_supervisor(supervisor)
    
    return supervisor