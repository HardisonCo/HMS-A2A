"""
Chain of Recursive Thoughts Agent Adapter for Deal Negotiation

This module provides adapters to enhance any specialized agent with Chain of Recursive
Thoughts capabilities for deal negotiation and collaborative decision making.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Union
from langchain_google_genai import ChatGoogleGenerativeAI

from common.utils.recursive_thought import CoRTProcessor, get_recursive_thought_processor
from specialized_agents.collaboration.deals import Deal, Problem, Solution, Player, Transaction
from specialized_agents.collaboration.cort_deal_negotiator import CoRTDealEvaluator

# Configure logging
logger = logging.getLogger(__name__)


class CoRTAgentAdapter:
    """
    Adapter that enhances any specialized agent with CoRT capabilities for deals.
    
    This adapter integrates Chain of Recursive Thoughts into existing agents to
    improve their decision-making capabilities in complex collaborative scenarios.
    """
    
    def __init__(
        self, 
        agent_domain: str,
        agent_role: str = None,
        agent_expertise: List[str] = None,
        model_name: str = "gemini-1.5-flash",
        max_rounds: int = 3,
        generate_alternatives: int = 3,
        dynamic_rounds: bool = True,
        llm_generator: Callable[[str], str] = None
    ):
        """
        Initialize the CoRT Agent Adapter.
        
        Args:
            agent_domain: Domain of the agent (e.g., 'healthcare', 'financial')
            agent_role: Role of the agent (e.g., 'advisor', 'analyst')
            agent_expertise: List of agent expertise areas
            model_name: LLM model name to use
            max_rounds: Maximum thinking rounds
            generate_alternatives: Number of alternatives to generate per round
            dynamic_rounds: Whether to dynamically determine thinking depth
            llm_generator: Optional custom function for LLM generation
        """
        self.agent_domain = agent_domain
        self.agent_role = agent_role or f"{agent_domain.capitalize()} Specialist"
        self.agent_expertise = agent_expertise or []
        self.model_name = model_name
        self.max_rounds = max_rounds
        self.generate_alternatives = generate_alternatives
        self.dynamic_rounds = dynamic_rounds
        
        # Initialize LLM generator if not provided
        if llm_generator is None:
            # Create a Gemini model
            try:
                model = ChatGoogleGenerativeAI(model=model_name)
                
                # Create a generator function
                def default_generator(prompt: str) -> str:
                    """Generate a response using the Gemini model."""
                    try:
                        response = model.invoke(prompt).content
                        return response
                    except Exception as e:
                        logger.error(f"Error in LLM generation: {e}")
                        return f"Error generating response: {str(e)}"
                
                self.llm_generator = default_generator
                
            except Exception as e:
                logger.error(f"Error creating default LLM generator: {e}")
                raise ValueError(f"Could not create default LLM generator: {str(e)}")
        else:
            self.llm_generator = llm_generator
        
        # Initialize the CoRT processor
        self.cort_processor = CoRTProcessor(
            llm_generator=self.llm_generator,
            max_rounds=max_rounds,
            generate_alternatives=generate_alternatives,
            dynamic_rounds=dynamic_rounds
        )
        
        # Initialize the deal evaluator
        self.deal_evaluator = CoRTDealEvaluator(
            llm_generator=self.llm_generator,
            max_rounds=max_rounds,
            generate_alternatives=generate_alternatives,
            dynamic_rounds=dynamic_rounds
        )
    
    def enhance_function(
        self, 
        original_function: Callable, 
        function_name: str = None,
        prompt_instructions: Optional[str] = None
    ) -> Callable:
        """
        Enhance a function with Chain of Recursive Thoughts.
        
        This wraps an existing function to apply CoRT processing to its results,
        enabling more sophisticated reasoning.
        
        Args:
            original_function: The function to enhance
            function_name: Optional name for the function (for logging)
            prompt_instructions: Optional specific instructions for the enhancement
            
        Returns:
            Enhanced function with CoRT capabilities
        """
        function_name = function_name or original_function.__name__
        
        async def enhanced_function(*args, **kwargs):
            # Extract prompt_instructions from kwargs if provided
            local_prompt_instructions = kwargs.pop('prompt_instructions', prompt_instructions)
            
            # Execute the original function
            original_result = await original_function(*args, **kwargs)
            
            # Determine if this is a deal-related function
            is_deal_function = any(keyword in function_name.lower() for keyword in [
                "deal", "negotiat", "proposal", "solution", "problem", "transaction",
                "agreement", "contract", "partner", "collaborat"
            ])
            
            if not is_deal_function:
                # Not a deal function, return original result
                return original_result
            
            # Prepare context for CoRT processing
            context = {
                "agent_domain": self.agent_domain,
                "agent_role": self.agent_role,
                "agent_expertise": self.agent_expertise,
                "function_name": function_name,
                "args": args,
                "kwargs": kwargs
            }
            
            # Create a prompt for CoRT processing
            prompt = self._create_enhancement_prompt(
                function_name, 
                original_result, 
                context,
                local_prompt_instructions
            )
            
            # Process with CoRT
            cort_result = self.cort_processor.process(
                query=prompt,
                initial_response=str(original_result) if isinstance(original_result, (str, int, float, bool)) else None,
                task_context=context,
                prompt_instructions=local_prompt_instructions
            )
            
            # Return enhanced result
            enhanced_result = {
                "original_result": original_result,
                "enhanced_result": cort_result["final_response"],
                "thinking_trace": cort_result["thinking_trace"],
                "rounds_completed": cort_result["rounds_completed"]
            }
            
            logger.info(f"Enhanced function {function_name} with CoRT - {cort_result['rounds_completed']} rounds")
            
            return enhanced_result
        
        return enhanced_function
    
    def _create_enhancement_prompt(
        self, 
        function_name: str, 
        original_result: Any, 
        context: Dict[str, Any],
        prompt_instructions: Optional[str] = None
    ) -> str:
        """
        Create a prompt for enhancing function results with CoRT.
        
        Args:
            function_name: Name of the function
            original_result: Original function result
            context: Additional context
            prompt_instructions: Optional specific instructions for the enhancement
            
        Returns:
            Prompt for CoRT processing
        """
        # Format the original result for inclusion in the prompt
        if isinstance(original_result, (str, int, float, bool)):
            result_str = str(original_result)
        elif isinstance(original_result, dict):
            result_str = "\n".join([f"{k}: {v}" for k, v in original_result.items()])
        elif isinstance(original_result, list):
            result_str = "\n".join([str(item) for item in original_result])
        else:
            result_str = f"{type(original_result)}: {str(original_result)}"
        
        # Create a context description
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items() if k not in ["args", "kwargs"]])
        
        # Determine the type of enhancement based on function name
        if "evaluat" in function_name.lower():
            prompt_type = "evaluation"
            task_desc = "critically evaluate this result from multiple perspectives"
        elif "compar" in function_name.lower():
            prompt_type = "comparison"
            task_desc = "thoroughly compare the options and identify the best choice"
        elif "negotiat" in function_name.lower():
            prompt_type = "negotiation"
            task_desc = "analyze the negotiation options and recommend improvements"
        elif "proposal" in function_name.lower() or "solution" in function_name.lower():
            prompt_type = "proposal"
            task_desc = "enhance this proposal with additional insights and improvements"
        else:
            prompt_type = "general"
            task_desc = "improve this result through recursive critical thinking"
        
        # Create the prompt with optional instructions
        if prompt_instructions:
            prompt = f"""
            As a {self.agent_role} with expertise in {', '.join(self.agent_expertise or [self.agent_domain])},
            you are enhancing the results of a function called '{function_name}' with Chain of Recursive Thoughts.
            
            Your task is to {task_desc}.
            
            CONTEXT:
            {context_str}
            
            ORIGINAL RESULT:
            {result_str}
            
            SPECIAL INSTRUCTIONS:
            {prompt_instructions}
            
            For this {prompt_type} task:
            1. Analyze the original result critically
            2. Consider multiple alternative perspectives
            3. Identify strengths and weaknesses
            4. Generate improvements and enhancements
            5. Integrate the best ideas into a comprehensive response
            
            After multiple rounds of recursive thinking, provide an enhanced version of the result
            that demonstrates deeper analysis and more sophisticated reasoning.
            """
        else:
            prompt = f"""
            As a {self.agent_role} with expertise in {', '.join(self.agent_expertise or [self.agent_domain])},
            you are enhancing the results of a function called '{function_name}' with Chain of Recursive Thoughts.
            
            Your task is to {task_desc}.
            
            CONTEXT:
            {context_str}
            
            ORIGINAL RESULT:
            {result_str}
            
            For this {prompt_type} task:
            1. Analyze the original result critically
            2. Consider multiple alternative perspectives
            3. Identify strengths and weaknesses
            4. Generate improvements and enhancements
            5. Integrate the best ideas into a comprehensive response
            
            After multiple rounds of recursive thinking, provide an enhanced version of the result
            that demonstrates deeper analysis and more sophisticated reasoning.
            """
        
        return prompt
    
    def deal_evaluation_function(
        self,
        deal: Union[Deal, Dict[str, Any]],
        evaluation_criteria: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a deal using Chain of Recursive Thoughts.
        
        This function uses CoRT to perform a thorough evaluation of a deal from
        the perspective of the agent's domain and role.
        
        Args:
            deal: Deal to evaluate (either Deal object or dictionary)
            evaluation_criteria: Optional custom evaluation criteria
            
        Returns:
            Evaluation results with thinking trace
        """
        # Convert deal dict to Deal object if needed
        if isinstance(deal, dict):
            deal = Deal.from_dict(deal)
        
        # Use default criteria if not provided
        if evaluation_criteria is None:
            evaluation_criteria = [
                {"name": f"{self.agent_domain.capitalize()} Value", "description": f"Does the deal create value from a {self.agent_domain} perspective?"},
                {"name": "Risk Assessment", "description": f"What {self.agent_domain}-specific risks are associated with this deal?"},
                {"name": "Alignment with Standards", "description": f"Does the deal align with {self.agent_domain} industry standards and best practices?"},
                {"name": "Implementation Viability", "description": f"Is the deal viable to implement from a {self.agent_domain} perspective?"}
            ]
        
        # Evaluate the deal
        evaluation_result = self.deal_evaluator.evaluate_deal(
            deal=deal,
            evaluator_role=self.agent_role,
            evaluation_criteria=evaluation_criteria
        )
        
        return evaluation_result
    
    def solution_comparison_function(
        self,
        problem: Union[Problem, Dict[str, Any]],
        solutions: List[Union[Solution, Dict[str, Any]]],
        comparison_criteria: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compare solutions using Chain of Recursive Thoughts.
        
        This function uses CoRT to compare multiple solutions to a problem from
        the perspective of the agent's domain and role.
        
        Args:
            problem: Problem to solve (either Problem object or dictionary)
            solutions: Solutions to compare (either Solution objects or dictionaries)
            comparison_criteria: Optional custom comparison criteria
            
        Returns:
            Comparison results with thinking trace and ranked solutions
        """
        # Convert dicts to objects if needed
        if isinstance(problem, dict):
            problem = Problem.from_dict(problem)
        
        solution_objects = []
        for solution in solutions:
            if isinstance(solution, dict):
                solution_objects.append(Solution.from_dict(solution))
            else:
                solution_objects.append(solution)
        
        # Use default criteria if not provided
        if comparison_criteria is None:
            comparison_criteria = [
                {"name": f"{self.agent_domain.capitalize()} Effectiveness", "description": f"How effectively does the solution address the problem from a {self.agent_domain} perspective?"},
                {"name": "Domain-Specific Implementation", "description": f"How well can this solution be implemented within {self.agent_domain} constraints?"},
                {"name": "Industry Alignment", "description": f"How well does the solution align with {self.agent_domain} industry standards and practices?"},
                {"name": "Expertise Utilization", "description": "How effectively does the solution leverage available expertise?"}
            ]
        
        # Compare the solutions
        comparison_result = self.deal_evaluator.compare_solutions(
            problem=problem,
            solutions=solution_objects,
            evaluator_role=self.agent_role,
            comparison_criteria=comparison_criteria
        )
        
        return comparison_result
    
    def transaction_negotiation_function(
        self,
        transaction: Union[Transaction, Dict[str, Any]],
        from_player: Union[Player, Dict[str, Any]],
        to_player: Union[Player, Dict[str, Any]],
        negotiation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Negotiate a transaction using Chain of Recursive Thoughts.
        
        This function uses CoRT to negotiate transaction terms from the perspective
        of the agent's domain and role.
        
        Args:
            transaction: Transaction to negotiate (either Transaction object or dictionary)
            from_player: Sender player (either Player object or dictionary)
            to_player: Receiver player (either Player object or dictionary)
            negotiation_context: Optional additional context for negotiation
            
        Returns:
            Negotiation results with thinking trace and recommended adjustments
        """
        # Convert dicts to objects if needed
        if isinstance(transaction, dict):
            transaction = Transaction.from_dict(transaction)
        
        if isinstance(from_player, dict):
            from_player = Player.from_dict(from_player)
        
        if isinstance(to_player, dict):
            to_player = Player.from_dict(to_player)
        
        # Use default context if not provided
        if negotiation_context is None:
            negotiation_context = {
                f"{self.agent_domain}_considerations": f"Specific considerations from a {self.agent_domain} perspective",
                "industry_trends": f"Current trends in the {self.agent_domain} industry",
                "role_perspective": f"Negotiation considerations from a {self.agent_role} perspective"
            }
        
        # Negotiate the transaction
        negotiation_result = self.deal_evaluator.negotiate_transaction(
            transaction=transaction,
            from_player=from_player,
            to_player=to_player,
            negotiator_role=self.agent_role,
            negotiation_context=negotiation_context
        )
        
        return negotiation_result


def enhance_agent_with_cort(
    agent: Any,
    domain: str,
    role: Optional[str] = None,
    expertise: Optional[List[str]] = None,
    model_name: str = "gemini-1.5-flash",
    max_rounds: int = 3,
    generate_alternatives: int = 3,
    llm_generator: Optional[Callable[[str], str]] = None
) -> Dict[str, Callable]:
    """
    Enhance an agent with Chain of Recursive Thoughts capabilities for deals.
    
    This function takes an existing agent and adds CoRT-enhanced functions
    for deal evaluation, solution comparison, and transaction negotiation.
    
    Args:
        agent: The agent to enhance
        domain: Domain of the agent (e.g., 'healthcare', 'financial')
        role: Role of the agent (e.g., 'advisor', 'analyst')
        expertise: List of agent expertise areas
        model_name: LLM model name to use
        max_rounds: Maximum thinking rounds
        generate_alternatives: Number of alternatives to generate per round
        llm_generator: Optional custom function for LLM generation
        
    Returns:
        Dictionary of enhanced functions that can be added to the agent
    """
    # Create the adapter
    adapter = CoRTAgentAdapter(
        agent_domain=domain,
        agent_role=role,
        agent_expertise=expertise,
        model_name=model_name,
        max_rounds=max_rounds,
        generate_alternatives=generate_alternatives,
        llm_generator=llm_generator
    )
    
    # Enhance any existing deal-related methods on the agent
    enhanced_methods = {}
    
    # Look for deal-related methods on the agent
    for method_name in dir(agent):
        if method_name.startswith('_'):
            continue
        
        method = getattr(agent, method_name)
        if not callable(method):
            continue
        
        # Check if this is a deal-related method
        if any(keyword in method_name.lower() for keyword in [
            "deal", "negotiat", "proposal", "solution", "problem", "transaction",
            "agreement", "contract", "partner", "collaborat"
        ]):
            # Enhance the method
            enhanced_methods[f"cort_{method_name}"] = adapter.enhance_function(method, method_name)
    
    # Add standard deal evaluation functions
    enhanced_methods["evaluate_deal_with_cort"] = adapter.deal_evaluation_function
    enhanced_methods["compare_solutions_with_cort"] = adapter.solution_comparison_function
    enhanced_methods["negotiate_transaction_with_cort"] = adapter.transaction_negotiation_function
    
    return enhanced_methods