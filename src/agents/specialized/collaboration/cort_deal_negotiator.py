"""
Chain of Recursive Thoughts Deal Negotiator

This module implements an enhanced deal negotiation system using Chain of Recursive Thoughts
to enable agents to thoroughly consider multiple options and make better decisions in
collaborative deal-making scenarios.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import uuid
import json
import networkx as nx

from common.utils.recursive_thought import CoRTProcessor, get_recursive_thought_processor
from specialized_agents.tools_base import StandardsCompliantTool, ContentPart, ToolMetadata
from specialized_agents.standards_validation import StandardsValidator
from specialized_agents.collaboration.deals import Deal, Problem, Solution, Player, Transaction
from specialized_agents.collaboration.deal_tools import DealTools

# Configure logging
logger = logging.getLogger(__name__)


class CoRTDealEvaluator:
    """
    Evaluates deals and proposals using Chain of Recursive Thoughts.
    
    This class enables recursive thinking and thorough evaluation of deal options,
    helping agents make better decisions in complex collaborative scenarios.
    """
    
    def __init__(
        self,
        llm_generator: callable,
        max_rounds: int = 3,
        generate_alternatives: int = 3,
        dynamic_rounds: bool = True
    ):
        """
        Initialize the CoRT Deal Evaluator.
        
        Args:
            llm_generator: Function that processes a prompt and returns a response
            max_rounds: Maximum thinking rounds
            generate_alternatives: Number of alternatives to generate per round
            dynamic_rounds: Whether to dynamically determine thinking depth
        """
        self.cort_processor = CoRTProcessor(
            llm_generator=llm_generator,
            max_rounds=max_rounds,
            generate_alternatives=generate_alternatives,
            dynamic_rounds=dynamic_rounds
        )
    
    def evaluate_deal(
        self,
        deal: Deal,
        evaluator_role: str,
        evaluation_criteria: List[Dict[str, Any]],
        prompt_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a deal using Chain of Recursive Thoughts.
        
        Args:
            deal: The deal to evaluate
            evaluator_role: Role of the agent evaluating the deal
            evaluation_criteria: List of criteria to evaluate against
            prompt_instructions: Optional specific instructions for the evaluation
            
        Returns:
            Evaluation results with thinking trace
        """
        # Create a query for CoRT processing
        criteria_text = "\n".join([
            f"- {criterion['name']}: {criterion['description']}" 
            for criterion in evaluation_criteria
        ])
        
        # Create a deal summary with safety checks for missing data
        try:
            players_summary = "\n".join([
                f"- {player.name} (Role: {player.role or 'Not specified'})" 
                for player in deal.players.values()
            ]) if deal.players else "No players specified"
            
            problems_summary = "\n".join([
                f"- {problem.name}: {problem.description}" 
                for problem in deal.problems.values()
            ]) if deal.problems else "No problems specified"
            
            solutions_summary = "\n".join([
                f"- {solution.name}: {solution.description}" 
                for solution in deal.solutions.values()
            ]) if deal.solutions else "No solutions specified"
            
            transactions_summary = "\n".join([
                f"- {transaction.name}: {transaction.transaction_type or 'Generic'} from {transaction.from_player} to {transaction.to_player}" 
                for transaction in deal.transactions
            ]) if deal.transactions else "No transactions specified"
        except AttributeError as e:
            # If there's an issue with accessing deal attributes, handle gracefully
            logger.warning(f"Error accessing deal attributes: {e}")
            players_summary = "Error loading players data"
            problems_summary = "Error loading problems data"
            solutions_summary = "Error loading solutions data"
            transactions_summary = "Error loading transactions data"
        
        deal_summary = f"""
        Deal: {deal.name}
        Description: {deal.description}
        Type: {getattr(deal, 'deal_type', 'Not specified')}
        Status: {getattr(deal, 'status', 'Not specified')}
        
        Players:
        {players_summary}
        
        Problems:
        {problems_summary}
        
        Solutions:
        {solutions_summary}
        
        Transactions:
        {transactions_summary}
        """
        
        # Build the query with optional instructions
        if prompt_instructions:
            query = f"""
            As a {evaluator_role}, evaluate the following deal thoroughly:
            
            {deal_summary}
            
            Evaluation Criteria:
            {criteria_text}
            
            Special Instructions:
            {prompt_instructions}
            
            For each criterion, analyze how well the deal meets the requirements.
            Consider both the strengths and weaknesses of the deal.
            Provide a comprehensive evaluation with specific examples and reasoning.
            Conclude with an overall assessment and whether you would approve this deal.
            """
        else:
            query = f"""
            As a {evaluator_role}, evaluate the following deal thoroughly:
            
            {deal_summary}
            
            Evaluation Criteria:
            {criteria_text}
            
            For each criterion, analyze how well the deal meets the requirements.
            Consider both the strengths and weaknesses of the deal.
            Provide a comprehensive evaluation with specific examples and reasoning.
            Conclude with an overall assessment and whether you would approve this deal.
            """
        
        # Process with CoRT
        result = self.cort_processor.process(
            query=query,
            task_context={
                "deal_id": deal.id,
                "evaluator_role": evaluator_role,
                "evaluation_criteria": evaluation_criteria
            },
            prompt_instructions=prompt_instructions
        )
        
        # Extract approval status from the evaluation
        approval_status = "Unknown"
        try:
            # Look for explicit approval/rejection language
            approval_patterns = [
                (r'(?:I|we)\s+(?:would|do)\s+approve', "Approved"),
                (r'(?:I|we)\s+(?:would|do)\s+recommend\s+approv(?:al|ing)', "Approved"),
                (r'(?:deal|it)\s+(?:is|appears)\s+(?:to be\s+)?approv(?:ed|able)', "Approved"),
                (r'(?:I|we)\s+(?:would|do)\s+not\s+approve', "Rejected"),
                (r'(?:I|we)\s+(?:would|do)\s+reject', "Rejected"),
                (r'(?:I|we)\s+(?:would|do)\s+not\s+recommend', "Rejected"),
                (r'(?:deal|it)\s+(?:should|must)\s+(?:be\s+)?reject(?:ed)?', "Rejected"),
                (r'(?:approve|approval)\s+with\s+(?:conditions|modifications)', "Conditionally Approved"),
                (r'(?:conditionally|partially)\s+approve', "Conditionally Approved")
            ]
            
            for pattern, status in approval_patterns:
                if re.search(pattern, result["final_response"], re.IGNORECASE):
                    approval_status = status
                    break
                    
            # If we didn't find explicit approval language, look for sentiment
            if approval_status == "Unknown":
                if any(word in result["final_response"].lower() for word in 
                      ["excellent", "outstanding", "strong", "robust", "comprehensive", "beneficial"]):
                    approval_status = "Likely Approved"
                elif any(word in result["final_response"].lower() for word in 
                        ["inadequate", "insufficient", "poor", "weak", "concerning", "problematic"]):
                    approval_status = "Likely Rejected"
        except Exception as e:
            logger.warning(f"Error extracting approval status: {e}")
        
        # Structure the result
        evaluation_result = {
            "deal_id": deal.id,
            "deal_name": deal.name,
            "evaluator_role": evaluator_role,
            "evaluation": result["final_response"],
            "initial_evaluation": result["initial_response"],
            "thinking_trace": result["thinking_trace"],
            "rounds_completed": result["rounds_completed"],
            "approval_status": approval_status,
            "timestamp": datetime.now().isoformat()
        }
        
        return evaluation_result
    
    def compare_solutions(
        self,
        problem: Problem,
        solutions: List[Solution],
        evaluator_role: str,
        comparison_criteria: List[Dict[str, Any]],
        prompt_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple solutions for a problem using Chain of Recursive Thoughts.
        
        Args:
            problem: The problem to evaluate solutions for
            solutions: List of solutions to compare
            evaluator_role: Role of the agent evaluating the solutions
            comparison_criteria: List of criteria to compare against
            prompt_instructions: Optional specific instructions for the comparison
            
        Returns:
            Comparison results with thinking trace and ranked solutions
        """
        # Create a query for CoRT processing
        criteria_text = "\n".join([
            f"- {criterion['name']}: {criterion['description']}" 
            for criterion in comparison_criteria
        ])
        
        # Create a problem summary
        problem_summary = f"""
        Problem: {problem.name}
        Description: {problem.description}
        Domain: {problem.domain or 'General'}
        Complexity: {problem.complexity or 'Medium'}
        Urgency: {problem.urgency or 'Medium'}
        Success Criteria: {', '.join(problem.success_criteria or ['Not specified'])}
        Constraints: {', '.join(problem.constraints or ['None specified'])}
        """
        
        # Create solution summaries
        solution_summaries = []
        for i, solution in enumerate(solutions):
            # Handle optional fields safely
            components = getattr(solution, 'components', [])
            implementation_steps = getattr(solution, 'implementation_steps', [])
            risks = getattr(solution, 'risks', [])
            expected_outcomes = getattr(solution, 'expected_outcomes', [])
            
            solution_summary = f"""
            Solution {i+1}: {solution.name}
            Description: {solution.description}
            Approach: {solution.approach or 'Not specified'}
            Estimated Effort: {solution.estimated_effort or 'Not specified'}
            Expected Outcomes: {', '.join(expected_outcomes) if expected_outcomes else 'Not specified'}
            Components: {len(components)}
            Implementation Steps: {len(implementation_steps)}
            Risks: {len(risks)}
            """
            solution_summaries.append(solution_summary)
        
        solutions_text = "\n\n".join(solution_summaries)
        
        # Build the comparison query, adding prompt instructions if provided
        if prompt_instructions:
            query = f"""
            As a {evaluator_role}, compare the following solutions for the given problem:
            
            {problem_summary}
            
            Solutions to Compare:
            {solutions_text}
            
            Comparison Criteria:
            {criteria_text}
            
            Special Instructions:
            {prompt_instructions}
            
            For each solution:
            1. Evaluate how well it addresses the problem
            2. Assess its feasibility, risks, and expected outcomes
            3. Compare it against the other solutions using the criteria provided
            
            Rank the solutions from best to worst, explaining your reasoning.
            Provide specific strengths and weaknesses for each solution.
            Conclude with a recommendation of which solution should be implemented.
            """
        else:
            query = f"""
            As a {evaluator_role}, compare the following solutions for the given problem:
            
            {problem_summary}
            
            Solutions to Compare:
            {solutions_text}
            
            Comparison Criteria:
            {criteria_text}
            
            For each solution:
            1. Evaluate how well it addresses the problem
            2. Assess its feasibility, risks, and expected outcomes
            3. Compare it against the other solutions using the criteria provided
            
            Rank the solutions from best to worst, explaining your reasoning.
            Provide specific strengths and weaknesses for each solution.
            Conclude with a recommendation of which solution should be implemented.
            """
        
        # Process with CoRT
        result = self.cort_processor.process(
            query=query,
            task_context={
                "problem_id": problem.id,
                "evaluator_role": evaluator_role,
                "comparison_criteria": comparison_criteria,
                "solution_ids": [solution.id for solution in solutions]
            },
            prompt_instructions=prompt_instructions
        )
        
        # Extract ranking from the result (we'll try to parse it)
        ranking = []
        try:
            # First try to extract a structured ranking from the response
            structured_ranking_pattern = re.compile(r'(?:Rankings?|Order|Recommendation).*?[\n:]+(.*?)(?:\n\n|\Z)', re.DOTALL | re.IGNORECASE)
            match = structured_ranking_pattern.search(result["final_response"])
            
            if match:
                ranking_text = match.group(1)
                # Look for solutions mentioned in the ranking text
                for solution in solutions:
                    if solution.name in ranking_text:
                        solution_id = solution.id
                        if solution_id not in ranking:
                            ranking.append(solution_id)
            
            # If we didn't find all solutions, fall back to the line-by-line approach
            if len(ranking) < len(solutions):
                lines = result["final_response"].split('\n')
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ["rank", "order", "recommendation", "best solution"]):
                        # Look at the next few lines for solutions mentioned by number or name
                        for j in range(i+1, min(i+15, len(lines))):
                            for k, solution in enumerate(solutions):
                                # Check if this line mentions this solution
                                if (f"Solution {k+1}" in lines[j] or 
                                    solution.name in lines[j] or 
                                    f"{k+1}." in lines[j] or
                                    f"{k+1})" in lines[j] or
                                    f"#{k+1}" in lines[j]):
                                    solution_id = solution.id
                                    if solution_id not in ranking:
                                        ranking.append(solution_id)
        except Exception as e:
            logger.warning(f"Failed to extract solution ranking: {str(e)}")
        
        # If we couldn't extract a ranking, include all solutions in original order
        if not ranking or len(ranking) < len(solutions):
            missing_solutions = [s.id for s in solutions if s.id not in ranking]
            ranking.extend(missing_solutions)
        
        # Structure the result
        comparison_result = {
            "problem_id": problem.id,
            "problem_name": problem.name,
            "evaluator_role": evaluator_role,
            "comparison": result["final_response"],
            "initial_comparison": result["initial_response"],
            "thinking_trace": result["thinking_trace"],
            "rounds_completed": result["rounds_completed"],
            "solution_ranking": ranking,
            "timestamp": datetime.now().isoformat()
        }
        
        return comparison_result
    
    def negotiate_transaction(
        self,
        transaction: Transaction,
        from_player: Player,
        to_player: Player,
        negotiator_role: str,
        negotiation_context: Dict[str, Any],
        prompt_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Negotiate a transaction between players using Chain of Recursive Thoughts.
        
        Args:
            transaction: The transaction to negotiate
            from_player: The sender player
            to_player: The receiver player
            negotiator_role: Role of the agent negotiating the transaction
            negotiation_context: Additional context for negotiation
            prompt_instructions: Optional specific instructions for the negotiation
            
        Returns:
            Negotiation results with thinking trace and recommended adjustments
        """
        # Create a query for CoRT processing with safety checks for missing data
        try:
            transaction_summary = f"""
            Transaction: {transaction.name}
            Type: {getattr(transaction, 'transaction_type', 'Not specified')}
            Amount: {getattr(transaction, 'amount', 'Not specified')} {getattr(transaction, 'currency', '')}
            From: {from_player.name} (Role: {getattr(from_player, 'role', 'Not specified')})
            To: {to_player.name} (Role: {getattr(to_player, 'role', 'Not specified')})
            Status: {getattr(transaction, 'status', 'Not specified')}
            Description: {transaction.description}
            Terms: {', '.join(getattr(transaction, 'terms', []) or ['Not specified'])}
            """
        except AttributeError as e:
            logger.warning(f"Error accessing transaction or player attributes: {e}")
            transaction_summary = f"""
            Transaction: {getattr(transaction, 'name', 'Unnamed transaction')}
            From: {getattr(from_player, 'name', 'Unknown')} 
            To: {getattr(to_player, 'name', 'Unknown')}
            Description: {getattr(transaction, 'description', 'No description available')}
            """
        
        # Create context summary
        context_summary = "\n".join([
            f"- {key}: {value}" for key, value in negotiation_context.items()
        ]) if negotiation_context else "No additional context provided"
        
        # Build the query with optional instructions
        if prompt_instructions:
            query = f"""
            As a {negotiator_role}, negotiate the following transaction between two parties:
            
            {transaction_summary}
            
            Negotiation Context:
            {context_summary}
            
            Special Instructions:
            {prompt_instructions}
            
            For this negotiation:
            1. Identify interests and priorities of both parties
            2. Analyze where there may be conflicts or misalignment
            3. Propose creative solutions that could benefit both parties
            4. Consider multiple alternatives to the current transaction terms
            5. Recommend fair adjustments to create a win-win outcome
            
            Approach this negotiation from multiple angles, considering various scenarios.
            For each potential solution, analyze its advantages and disadvantages.
            Conclude with specific recommendations to improve the transaction.
            """
        else:
            query = f"""
            As a {negotiator_role}, negotiate the following transaction between two parties:
            
            {transaction_summary}
            
            Negotiation Context:
            {context_summary}
            
            For this negotiation:
            1. Identify interests and priorities of both parties
            2. Analyze where there may be conflicts or misalignment
            3. Propose creative solutions that could benefit both parties
            4. Consider multiple alternatives to the current transaction terms
            5. Recommend fair adjustments to create a win-win outcome
            
            Approach this negotiation from multiple angles, considering various scenarios.
            For each potential solution, analyze its advantages and disadvantages.
            Conclude with specific recommendations to improve the transaction.
            """
        
        # Process with CoRT
        result = self.cort_processor.process(
            query=query,
            task_context={
                "transaction_id": transaction.id,
                "from_player_id": from_player.id,
                "to_player_id": to_player.id,
                "negotiator_role": negotiator_role,
                "negotiation_context": negotiation_context
            },
            prompt_instructions=prompt_instructions
        )
        
        # Extract recommendations with improved extraction
        recommendations = []
        try:
            # Try different extraction approaches
            
            # First, look for an explicit recommendations section
            recommendations_pattern = re.compile(
                r'(?:Recommendations?|Suggested\s+(?:Changes|Adjustments)|Proposed\s+Changes)(?:\s*:|(?:s\s*)?:\s*|[\n]+)(.*?)(?=(?:^\s*#)|(?:^\s*\d+\.)|(?:^\s*[A-Z][A-Za-z\s]+:)|$)',
                re.MULTILINE | re.DOTALL | re.IGNORECASE
            )
            
            match = recommendations_pattern.search(result["final_response"])
            if match:
                rec_section = match.group(1).strip()
                
                # Look for bullet points or numbered items in the section
                bullet_points = re.findall(r'[-*•]\s*(.*?)(?=\n\s*[-*•]|\n\n|\Z)', rec_section, re.DOTALL)
                if bullet_points:
                    recommendations.extend([bp.strip() for bp in bullet_points if bp.strip()])
                else:
                    # No bullet points found, try numbered items
                    numbered_items = re.findall(r'\d+\.\s*(.*?)(?=\n\s*\d+\.|\n\n|\Z)', rec_section, re.DOTALL)
                    if numbered_items:
                        recommendations.extend([ni.strip() for ni in numbered_items if ni.strip()])
                    else:
                        # No structured items found, use the whole section as one recommendation
                        # but split by newlines if it's long
                        if len(rec_section) > 100:  # arbitrary threshold
                            paragraphs = [p.strip() for p in rec_section.split('\n\n')]
                            recommendations.extend([p for p in paragraphs if p])
                        else:
                            recommendations.append(rec_section)
            
            # If no recommendations found, fall back to the original method
            if not recommendations:
                lines = result["final_response"].split('\n')
                in_recommendations = False
                for line in lines:
                    # Look for sections that might contain recommendations
                    if any(heading in line.lower() for heading in [
                        "recommend", "suggest", "proposed changes", "adjustments", "conclusion"
                    ]):
                        in_recommendations = True
                        continue
                    
                    # If we're in the recommendations section, collect bullet points
                    if in_recommendations and (line.strip().startswith('-') or 
                                               line.strip().startswith('*') or
                                               re.match(r'^\d+\.', line.strip())):
                        # Remove the bullet or number
                        if line.strip().startswith('-') or line.strip().startswith('*'):
                            recommendation = line.strip()[1:].strip()
                        else:  # Numbered item
                            recommendation = re.sub(r'^\d+\.', '', line.strip()).strip()
                            
                        if recommendation:
                            recommendations.append(recommendation)
                    elif in_recommendations and line.strip() and not line.strip().endswith(':'):
                        # This might be a non-bulleted recommendation in the section
                        recommendations.append(line.strip())
        except Exception as e:
            logger.warning(f"Failed to extract recommendations: {str(e)}")
        
        # Ensure recommendations are unique and non-empty
        recommendations = [rec for rec in recommendations if rec.strip()]
        recommendations = list(dict.fromkeys(recommendations))  # Remove duplicates while preserving order
        
        # Structure the result
        negotiation_result = {
            "transaction_id": transaction.id,
            "transaction_name": transaction.name,
            "from_player": from_player.name,
            "to_player": to_player.name,
            "negotiator_role": negotiator_role,
            "negotiation": result["final_response"],
            "initial_negotiation": result["initial_response"],
            "thinking_trace": result["thinking_trace"],
            "rounds_completed": result["rounds_completed"],
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        return negotiation_result


class CoRTDealTool(StandardsCompliantTool):
    """
    Standards-compliant tool for enhanced deal evaluation and negotiation using CoRT.
    
    This tool leverages Chain of Recursive Thoughts to enable more sophisticated
    deal evaluation, solution comparison, and transaction negotiation.
    """
    
    def __init__(self, llm_generator: callable = None):
        """
        Initialize the CoRT Deal Tool.
        
        Args:
            llm_generator: Function that processes a prompt and returns a response
        """
        super().__init__(
            name="cort_deal_evaluation",
            description="Evaluates deals, solutions, and transactions using Chain of Recursive Thoughts",
            input_schema=None,  # We'll validate inputs manually
            supported_standards=["CROSS_DOMAIN_COLLABORATION", "AGENT_COOPERATION", "DealFramework"],
            domain="Collaboration",
            metadata=ToolMetadata(
                title="CoRT Deal Evaluation Tool",
                read_only=True,
                destructive=False,
                idempotent=True,
                open_world=False,
                description="Chain of Recursive Thoughts deal evaluation and negotiation tool"
            )
        )
        
        self.llm_generator = llm_generator
        self._evaluator = None
        
        # Store standard deal tools for convenience
        self.deal_tools = DealTools()
    
    @property
    def evaluator(self) -> CoRTDealEvaluator:
        """Get the CoRT Deal Evaluator, creating it if needed."""
        if self._evaluator is None:
            if self.llm_generator is None:
                raise ValueError("No LLM generator provided for CoRT Deal Tool")
            
            self._evaluator = CoRTDealEvaluator(
                llm_generator=self.llm_generator,
                max_rounds=3,
                generate_alternatives=3,
                dynamic_rounds=True
            )
        
        return self._evaluator
    
    async def execute(self, args: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the CoRT Deal Tool.
        
        Args:
            args: Input arguments
            session_context: Optional session context
            
        Returns:
            Result of the operation
        """
        # Validate inputs
        if not isinstance(args, dict):
            raise ValueError("Arguments must be a dictionary")
        
        # Extract operation type
        operation = args.get("operation")
        if not operation:
            raise ValueError("Missing 'operation' field in arguments")
        
        # Execute the appropriate operation
        if operation == "evaluate_deal":
            return await self._evaluate_deal(args, session_context)
        elif operation == "compare_solutions":
            return await self._compare_solutions(args, session_context)
        elif operation == "negotiate_transaction":
            return await self._negotiate_transaction(args, session_context)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _evaluate_deal(self, args: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate a deal using CoRT.
        
        Args:
            args: Input arguments
            session_context: Optional session context
            
        Returns:
            Evaluation results
        """
        # Extract required fields
        deal_dict = args.get("deal")
        if not deal_dict:
            raise ValueError("Missing 'deal' field in arguments")
        
        evaluator_role = args.get("evaluator_role", "Deal Analyst")
        
        evaluation_criteria = args.get("evaluation_criteria", [
            {"name": "Value Creation", "description": "Does the deal create value for all participants?"},
            {"name": "Fairness", "description": "Is the deal fair to all participants?"},
            {"name": "Feasibility", "description": "Is the deal feasible to implement?"},
            {"name": "Risk", "description": "What risks are associated with the deal?"}
        ])
        
        # Get optional prompt instructions
        prompt_instructions = args.get("prompt_instructions")
        
        # Convert deal dict to Deal object
        deal = Deal.from_dict(deal_dict)
        
        # Evaluate the deal
        evaluation_result = self.evaluator.evaluate_deal(
            deal=deal,
            evaluator_role=evaluator_role,
            evaluation_criteria=evaluation_criteria,
            prompt_instructions=prompt_instructions
        )
        
        return evaluation_result
    
    async def _compare_solutions(self, args: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compare solutions using CoRT.
        
        Args:
            args: Input arguments
            session_context: Optional session context
            
        Returns:
            Comparison results
        """
        # Extract required fields
        problem_dict = args.get("problem")
        if not problem_dict:
            raise ValueError("Missing 'problem' field in arguments")
        
        solution_dicts = args.get("solutions", [])
        if not solution_dicts:
            raise ValueError("Missing or empty 'solutions' field in arguments")
        
        evaluator_role = args.get("evaluator_role", "Solution Architect")
        
        comparison_criteria = args.get("comparison_criteria", [
            {"name": "Effectiveness", "description": "How effectively does the solution address the problem?"},
            {"name": "Efficiency", "description": "How efficient is the solution in terms of resources and effort?"},
            {"name": "Innovation", "description": "How innovative is the solution?"},
            {"name": "Risk", "description": "What risks are associated with the solution?"}
        ])
        
        # Get optional prompt instructions
        prompt_instructions = args.get("prompt_instructions")
        
        # Convert dicts to objects
        problem = Problem.from_dict(problem_dict)
        solutions = [Solution.from_dict(solution_dict) for solution_dict in solution_dicts]
        
        # Compare the solutions
        comparison_result = self.evaluator.compare_solutions(
            problem=problem,
            solutions=solutions,
            evaluator_role=evaluator_role,
            comparison_criteria=comparison_criteria,
            prompt_instructions=prompt_instructions
        )
        
        return comparison_result
    
    async def _negotiate_transaction(self, args: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Negotiate a transaction using CoRT.
        
        Args:
            args: Input arguments
            session_context: Optional session context
            
        Returns:
            Negotiation results
        """
        # Extract required fields
        transaction_dict = args.get("transaction")
        if not transaction_dict:
            raise ValueError("Missing 'transaction' field in arguments")
        
        from_player_dict = args.get("from_player")
        if not from_player_dict:
            raise ValueError("Missing 'from_player' field in arguments")
        
        to_player_dict = args.get("to_player")
        if not to_player_dict:
            raise ValueError("Missing 'to_player' field in arguments")
        
        negotiator_role = args.get("negotiator_role", "Mediator")
        
        negotiation_context = args.get("negotiation_context", {})
        
        # Get optional prompt instructions
        prompt_instructions = args.get("prompt_instructions")
        
        # Convert dicts to objects
        transaction = Transaction.from_dict(transaction_dict)
        from_player = Player.from_dict(from_player_dict)
        to_player = Player.from_dict(to_player_dict)
        
        # Negotiate the transaction
        negotiation_result = self.evaluator.negotiate_transaction(
            transaction=transaction,
            from_player=from_player,
            to_player=to_player,
            negotiator_role=negotiator_role,
            negotiation_context=negotiation_context,
            prompt_instructions=prompt_instructions
        )
        
        return negotiation_result
    
    def format_result(self, result: Dict[str, Any]) -> List[ContentPart]:
        """
        Format the result for display.
        
        Args:
            result: Operation result
            
        Returns:
            List of content parts
        """
        # Create a data part with the full result
        data_part = ContentPart(
            type=ContentPart.ContentType.DATA,
            content=result
        )
        
        # Format a text summary based on the operation type
        if "evaluation" in result:
            # Deal evaluation result
            text_output = f"""
            Deal Evaluation: {result['deal_name']}
            Evaluator Role: {result['evaluator_role']}
            Rounds of Thought: {result['rounds_completed']}
            
            {result['evaluation']}
            """
        elif "comparison" in result:
            # Solution comparison result
            text_output = f"""
            Solution Comparison for Problem: {result['problem_name']}
            Evaluator Role: {result['evaluator_role']}
            Rounds of Thought: {result['rounds_completed']}
            Solution Ranking: {', '.join([f"#{i+1}: {sol_id}" for i, sol_id in enumerate(result['solution_ranking'])])}
            
            {result['comparison']}
            """
        elif "negotiation" in result:
            # Transaction negotiation result
            text_output = f"""
            Transaction Negotiation: {result['transaction_name']}
            From: {result['from_player']} To: {result['to_player']}
            Negotiator Role: {result['negotiator_role']}
            Rounds of Thought: {result['rounds_completed']}
            
            {result['negotiation']}
            
            Recommendations:
            {chr(10).join([f"- {rec}" for rec in result['recommendations']])}
            """
        else:
            # Generic result
            text_output = f"Operation completed with {result.get('rounds_completed', 0)} rounds of thought."
        
        text_part = ContentPart(
            type=ContentPart.ContentType.TEXT,
            content=text_output.strip()
        )
        
        return [data_part, text_part]


def register_cort_deal_tools(llm_generator: callable) -> List[str]:
    """
    Register CoRT deal tools and return their names.
    
    Args:
        llm_generator: Function that processes a prompt and returns a response
        
    Returns:
        List of registered tool names
    """
    from specialized_agents.collaboration.tool_registry import MCPToolRegistry
    
    # Create the CoRT deal tool
    cort_deal_tool = CoRTDealTool(llm_generator)
    
    # Register the tool
    registry = MCPToolRegistry()
    registry.register_tool(cort_deal_tool, ["*"])
    
    return [cort_deal_tool.name]