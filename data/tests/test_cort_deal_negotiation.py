"""
Tests for Chain of Recursive Thoughts Deal Negotiation.

This module contains tests for the CoRT implementation specialized for deal negotiations.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.utils.recursive_thought import CoRTProcessor
from specialized_agents.collaboration.deals import Deal, Problem, Solution, Player, Transaction
from specialized_agents.collaboration.cort_deal_negotiator import CoRTDealEvaluator, CoRTDealTool
from specialized_agents.collaboration.cort_agent_adapter import CoRTAgentAdapter, enhance_agent_with_cort


class TestCoRTDealEvaluator(unittest.TestCase):
    """Tests for the CoRTDealEvaluator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LLM generator
        self.mock_llm = MagicMock()
        self.mock_llm.return_value = "Mock evaluation response"
        
        # Create a CoRT deal evaluator with the mock LLM
        self.evaluator = CoRTDealEvaluator(
            llm_generator=self.mock_llm,
            max_rounds=2,
            generate_alternatives=2,
            dynamic_rounds=False
        )
        
        # Set up a mock CoRT processor to replace the real one
        self.mock_processor = MagicMock()
        self.mock_processor.process.return_value = {
            "query": "Test query",
            "initial_response": "Initial response",
            "final_response": "Final response",
            "thinking_trace": [{"round": 0, "response": "Initial response"}],
            "rounds_completed": 2
        }
        self.evaluator.cort_processor = self.mock_processor
        
        # Create a sample deal
        self.deal = Deal(
            name="Test Deal",
            description="A test deal",
            participants=["player1", "player2"],
            deal_type="test"
        )
        
        # Add players
        self.player1 = Player(
            agent_id="player1",
            name="Player 1",
            role="seller"
        )
        self.player2 = Player(
            agent_id="player2",
            name="Player 2",
            role="buyer"
        )
        self.deal.add_player(self.player1)
        self.deal.add_player(self.player2)
        
        # Add a problem
        self.problem = Problem(
            name="Test Problem",
            description="A test problem"
        )
        self.deal.add_problem(self.problem)
        
        # Add solutions
        self.solution1 = Solution(
            name="Solution 1",
            description="A test solution",
            problem_id=self.problem.id,
            approach="Test approach",
            expected_outcomes=["Outcome 1", "Outcome 2"]
        )
        self.solution2 = Solution(
            name="Solution 2",
            description="Another test solution",
            problem_id=self.problem.id,
            approach="Another approach",
            expected_outcomes=["Outcome 3", "Outcome 4"]
        )
        self.deal.add_solution(self.solution1)
        self.deal.add_solution(self.solution2)
        
        # Add a transaction
        self.transaction = Transaction(
            name="Test Transaction",
            transaction_type="purchase",
            amount=100.0,
            from_player=self.player1.id,
            to_player=self.player2.id,
            currency="USD",
            description="A test transaction"
        )
        self.deal.add_transaction(self.transaction)
    
    def test_evaluate_deal(self):
        """Test evaluating a deal."""
        # Set up evaluation criteria
        criteria = [
            {"name": "Value", "description": "Does the deal create value?"},
            {"name": "Risk", "description": "What risks are associated with the deal?"}
        ]
        
        # Evaluate the deal
        result = self.evaluator.evaluate_deal(
            deal=self.deal,
            evaluator_role="Deal Analyst",
            evaluation_criteria=criteria
        )
        
        # Check that the CoRT processor was called with the right arguments
        self.mock_processor.process.assert_called_once()
        args, kwargs = self.mock_processor.process.call_args
        self.assertIn("query", kwargs)
        self.assertIn(self.deal.name, kwargs["query"])
        self.assertIn("Value", kwargs["query"])
        self.assertIn("Risk", kwargs["query"])
        self.assertIn("task_context", kwargs)
        self.assertEqual(kwargs["task_context"]["deal_id"], self.deal.id)
        self.assertEqual(kwargs["task_context"]["evaluator_role"], "Deal Analyst")
        
        # Check the result
        self.assertEqual(result["deal_id"], self.deal.id)
        self.assertEqual(result["deal_name"], self.deal.name)
        self.assertEqual(result["evaluator_role"], "Deal Analyst")
        self.assertEqual(result["evaluation"], "Final response")
        self.assertEqual(result["initial_evaluation"], "Initial response")
        self.assertEqual(result["rounds_completed"], 2)
        self.assertIn("timestamp", result)
    
    def test_compare_solutions(self):
        """Test comparing solutions."""
        # Set up comparison criteria
        criteria = [
            {"name": "Effectiveness", "description": "How effective is the solution?"},
            {"name": "Efficiency", "description": "How efficient is the solution?"}
        ]
        
        # Customize the mock response to include solution ranking
        self.mock_processor.process.return_value = {
            "query": "Test query",
            "initial_response": "Initial comparison",
            "final_response": "Final comparison with solution 1 ranked higher",
            "thinking_trace": [{"round": 0, "response": "Initial comparison"}],
            "rounds_completed": 2
        }
        
        # Compare the solutions
        result = self.evaluator.compare_solutions(
            problem=self.problem,
            solutions=[self.solution1, self.solution2],
            evaluator_role="Solution Architect",
            comparison_criteria=criteria
        )
        
        # Check that the CoRT processor was called with the right arguments
        self.mock_processor.process.assert_called_once()
        args, kwargs = self.mock_processor.process.call_args
        self.assertIn("query", kwargs)
        self.assertIn(self.problem.name, kwargs["query"])
        self.assertIn(self.solution1.name, kwargs["query"])
        self.assertIn(self.solution2.name, kwargs["query"])
        self.assertIn("Effectiveness", kwargs["query"])
        self.assertIn("Efficiency", kwargs["query"])
        self.assertIn("task_context", kwargs)
        self.assertEqual(kwargs["task_context"]["problem_id"], self.problem.id)
        self.assertEqual(kwargs["task_context"]["evaluator_role"], "Solution Architect")
        
        # Check the result
        self.assertEqual(result["problem_id"], self.problem.id)
        self.assertEqual(result["problem_name"], self.problem.name)
        self.assertEqual(result["evaluator_role"], "Solution Architect")
        self.assertEqual(result["comparison"], "Final comparison with solution 1 ranked higher")
        self.assertEqual(result["initial_comparison"], "Initial comparison")
        self.assertEqual(result["rounds_completed"], 2)
        self.assertIn("solution_ranking", result)
        self.assertIn("timestamp", result)
    
    def test_negotiate_transaction(self):
        """Test negotiating a transaction."""
        # Set up negotiation context
        context = {
            "market_conditions": "Competitive",
            "relationship_goal": "Long-term partnership"
        }
        
        # Customize the mock response to include recommendations
        self.mock_processor.process.return_value = {
            "query": "Test query",
            "initial_response": "Initial negotiation",
            "final_response": """
            Here is my negotiation analysis.
            
            Recommendations:
            - Lower the price by 10%
            - Add a satisfaction guarantee
            - Include quarterly reviews
            """,
            "thinking_trace": [{"round": 0, "response": "Initial negotiation"}],
            "rounds_completed": 2
        }
        
        # Negotiate the transaction
        result = self.evaluator.negotiate_transaction(
            transaction=self.transaction,
            from_player=self.player1,
            to_player=self.player2,
            negotiator_role="Mediator",
            negotiation_context=context
        )
        
        # Check that the CoRT processor was called with the right arguments
        self.mock_processor.process.assert_called_once()
        args, kwargs = self.mock_processor.process.call_args
        self.assertIn("query", kwargs)
        self.assertIn(self.transaction.name, kwargs["query"])
        self.assertIn(self.player1.name, kwargs["query"])
        self.assertIn(self.player2.name, kwargs["query"])
        self.assertIn("Competitive", kwargs["query"])
        self.assertIn("task_context", kwargs)
        self.assertEqual(kwargs["task_context"]["transaction_id"], self.transaction.id)
        self.assertEqual(kwargs["task_context"]["negotiator_role"], "Mediator")
        
        # Check the result
        self.assertEqual(result["transaction_id"], self.transaction.id)
        self.assertEqual(result["transaction_name"], self.transaction.name)
        self.assertEqual(result["from_player"], self.player1.name)
        self.assertEqual(result["to_player"], self.player2.name)
        self.assertEqual(result["negotiator_role"], "Mediator")
        self.assertIn("Lower the price by 10%", result["negotiation"])
        self.assertEqual(result["initial_negotiation"], "Initial negotiation")
        self.assertEqual(result["rounds_completed"], 2)
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 3)
        self.assertIn("timestamp", result)


class TestCoRTDealTool(unittest.TestCase):
    """Tests for the CoRTDealTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LLM generator
        self.mock_llm = MagicMock()
        
        # Create a CoRT deal tool with the mock LLM
        self.tool = CoRTDealTool(llm_generator=self.mock_llm)
        
        # Create a mock CoRT deal evaluator
        self.mock_evaluator = MagicMock()
        self.tool._evaluator = self.mock_evaluator
        
        # Set up a sample deal dictionary
        self.deal_dict = {
            "id": "deal-123",
            "name": "Test Deal",
            "description": "A test deal",
            "participants": ["player1", "player2"],
            "deal_type": "test",
            "problems": [],
            "solutions": [],
            "players": [],
            "transactions": []
        }
        
        # Set up a sample problem dictionary
        self.problem_dict = {
            "id": "problem-123",
            "name": "Test Problem",
            "description": "A test problem"
        }
        
        # Set up sample solution dictionaries
        self.solution_dicts = [
            {
                "id": "solution-1",
                "name": "Solution 1",
                "description": "A test solution",
                "problem_id": "problem-123",
                "approach": "Test approach",
                "expected_outcomes": ["Outcome 1", "Outcome 2"]
            },
            {
                "id": "solution-2",
                "name": "Solution 2",
                "description": "Another test solution",
                "problem_id": "problem-123",
                "approach": "Another approach",
                "expected_outcomes": ["Outcome 3", "Outcome 4"]
            }
        ]
        
        # Set up sample transaction and player dictionaries
        self.transaction_dict = {
            "id": "transaction-123",
            "name": "Test Transaction",
            "transaction_type": "purchase",
            "amount": 100.0,
            "from_player": "player-1",
            "to_player": "player-2",
            "currency": "USD",
            "description": "A test transaction"
        }
        
        self.player_dicts = {
            "player-1": {
                "id": "player-1",
                "agent_id": "player1",
                "name": "Player 1",
                "role": "seller"
            },
            "player-2": {
                "id": "player-2",
                "agent_id": "player2",
                "name": "Player 2",
                "role": "buyer"
            }
        }
    
    async def test_execute_evaluate_deal(self):
        """Test executing the evaluate_deal operation."""
        # Set up the mock evaluator to return a sample result
        self.mock_evaluator.evaluate_deal.return_value = {
            "deal_id": "deal-123",
            "deal_name": "Test Deal",
            "evaluator_role": "Deal Analyst",
            "evaluation": "Test evaluation",
            "initial_evaluation": "Initial evaluation",
            "thinking_trace": [],
            "rounds_completed": 2,
            "timestamp": datetime.now().isoformat()
        }
        
        # Set up the input arguments
        args = {
            "operation": "evaluate_deal",
            "deal": self.deal_dict,
            "evaluator_role": "Deal Analyst",
            "evaluation_criteria": [
                {"name": "Value", "description": "Does the deal create value?"}
            ]
        }
        
        # Execute the tool
        result = await self.tool.execute(args)
        
        # Check that the evaluator was called with the right arguments
        self.mock_evaluator.evaluate_deal.assert_called_once()
        call_args = self.mock_evaluator.evaluate_deal.call_args[1]
        self.assertEqual(call_args["evaluator_role"], "Deal Analyst")
        self.assertEqual(len(call_args["evaluation_criteria"]), 1)
        
        # Check the result
        self.assertEqual(result["deal_id"], "deal-123")
        self.assertEqual(result["deal_name"], "Test Deal")
        self.assertEqual(result["evaluation"], "Test evaluation")
    
    async def test_execute_compare_solutions(self):
        """Test executing the compare_solutions operation."""
        # Set up the mock evaluator to return a sample result
        self.mock_evaluator.compare_solutions.return_value = {
            "problem_id": "problem-123",
            "problem_name": "Test Problem",
            "evaluator_role": "Solution Architect",
            "comparison": "Test comparison",
            "initial_comparison": "Initial comparison",
            "thinking_trace": [],
            "rounds_completed": 2,
            "solution_ranking": ["solution-1", "solution-2"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Set up the input arguments
        args = {
            "operation": "compare_solutions",
            "problem": self.problem_dict,
            "solutions": self.solution_dicts,
            "evaluator_role": "Solution Architect",
            "comparison_criteria": [
                {"name": "Effectiveness", "description": "How effective is the solution?"}
            ]
        }
        
        # Execute the tool
        result = await self.tool.execute(args)
        
        # Check that the evaluator was called with the right arguments
        self.mock_evaluator.compare_solutions.assert_called_once()
        call_args = self.mock_evaluator.compare_solutions.call_args[1]
        self.assertEqual(call_args["evaluator_role"], "Solution Architect")
        self.assertEqual(len(call_args["comparison_criteria"]), 1)
        
        # Check the result
        self.assertEqual(result["problem_id"], "problem-123")
        self.assertEqual(result["problem_name"], "Test Problem")
        self.assertEqual(result["comparison"], "Test comparison")
        self.assertEqual(result["solution_ranking"], ["solution-1", "solution-2"])
    
    async def test_execute_negotiate_transaction(self):
        """Test executing the negotiate_transaction operation."""
        # Set up the mock evaluator to return a sample result
        self.mock_evaluator.negotiate_transaction.return_value = {
            "transaction_id": "transaction-123",
            "transaction_name": "Test Transaction",
            "from_player": "Player 1",
            "to_player": "Player 2",
            "negotiator_role": "Mediator",
            "negotiation": "Test negotiation",
            "initial_negotiation": "Initial negotiation",
            "thinking_trace": [],
            "rounds_completed": 2,
            "recommendations": ["Lower the price by 10%"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Set up the input arguments
        args = {
            "operation": "negotiate_transaction",
            "transaction": self.transaction_dict,
            "from_player": self.player_dicts["player-1"],
            "to_player": self.player_dicts["player-2"],
            "negotiator_role": "Mediator",
            "negotiation_context": {
                "market_conditions": "Competitive"
            }
        }
        
        # Execute the tool
        result = await self.tool.execute(args)
        
        # Check that the evaluator was called with the right arguments
        self.mock_evaluator.negotiate_transaction.assert_called_once()
        call_args = self.mock_evaluator.negotiate_transaction.call_args[1]
        self.assertEqual(call_args["negotiator_role"], "Mediator")
        self.assertEqual(call_args["negotiation_context"]["market_conditions"], "Competitive")
        
        # Check the result
        self.assertEqual(result["transaction_id"], "transaction-123")
        self.assertEqual(result["transaction_name"], "Test Transaction")
        self.assertEqual(result["negotiation"], "Test negotiation")
        self.assertEqual(result["recommendations"], ["Lower the price by 10%"])
    
    async def test_execute_invalid_operation(self):
        """Test executing an invalid operation."""
        # Set up the input arguments with an invalid operation
        args = {
            "operation": "invalid_operation"
        }
        
        # Check that the execution raises a ValueError
        with self.assertRaises(ValueError):
            await self.tool.execute(args)
    
    def test_format_result(self):
        """Test result formatting."""
        # Test formatting an evaluation result
        eval_result = {
            "deal_id": "deal-123",
            "deal_name": "Test Deal",
            "evaluator_role": "Deal Analyst",
            "evaluation": "Test evaluation",
            "rounds_completed": 2
        }
        
        content_parts = self.tool.format_result(eval_result)
        self.assertEqual(len(content_parts), 2)
        self.assertEqual(content_parts[0].content, eval_result)
        self.assertIn("Test Deal", content_parts[1].content)
        self.assertIn("Test evaluation", content_parts[1].content)


class TestCoRTAgentAdapter(unittest.TestCase):
    """Tests for the CoRTAgentAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock function for LLM generation
        self.mock_llm = MagicMock()
        self.mock_llm.return_value = "Mock response"
        
        # Create a CoRT agent adapter
        self.adapter = CoRTAgentAdapter(
            agent_domain="finance",
            agent_role="Financial Advisor",
            agent_expertise=["investment", "retirement"],
            llm_generator=self.mock_llm
        )
        
        # Replace the CoRT processor and deal evaluator with mocks
        self.mock_processor = MagicMock()
        self.mock_evaluator = MagicMock()
        self.adapter.cort_processor = self.mock_processor
        self.adapter.deal_evaluator = self.mock_evaluator
        
        # Create a mock function to enhance
        async def mock_function(*args, **kwargs):
            return {"result": "Original result"}
        
        self.mock_function = mock_function
    
    def test_enhance_function(self):
        """Test enhancing a function with CoRT."""
        # Set up the mock processor to return a sample result
        self.mock_processor.process.return_value = {
            "query": "Test prompt",
            "initial_response": "Original result",
            "final_response": "Enhanced result",
            "thinking_trace": [],
            "rounds_completed": 2
        }
        
        # Enhance the mock function
        enhanced_function = self.adapter.enhance_function(self.mock_function, "test_function")
        
        # Execute the enhanced function
        import asyncio
        result = asyncio.run(enhanced_function("arg1", kwarg1="value1"))
        
        # Check that the original function was called
        self.assertIn("original_result", result)
        self.assertEqual(result["original_result"]["result"], "Original result")
        
        # Check that the processor was called
        self.mock_processor.process.assert_called_once()
        
        # Check the enhanced result
        self.assertEqual(result["enhanced_result"], "Enhanced result")
        self.assertEqual(result["rounds_completed"], 2)
    
    def test_create_enhancement_prompt(self):
        """Test creating enhancement prompts."""
        # Test for evaluation function
        eval_prompt = self.adapter._create_enhancement_prompt(
            function_name="evaluate_deal",
            original_result={"score": 8, "notes": "Good deal"},
            context={"agent_role": "Financial Advisor"}
        )
        self.assertIn("evaluate", eval_prompt.lower())
        self.assertIn("Financial Advisor", eval_prompt)
        self.assertIn("score: 8", eval_prompt.lower())
        
        # Test for negotiation function
        negotiate_prompt = self.adapter._create_enhancement_prompt(
            function_name="negotiate_contract",
            original_result="Accept the offer",
            context={"agent_role": "Financial Advisor"}
        )
        self.assertIn("negotiat", negotiate_prompt.lower())
        self.assertIn("Financial Advisor", negotiate_prompt)
        self.assertIn("Accept the offer", negotiate_prompt)
    
    def test_deal_evaluation_function(self):
        """Test the deal evaluation function."""
        # Set up the mock evaluator to return a sample result
        self.mock_evaluator.evaluate_deal.return_value = {
            "deal_id": "deal-123",
            "deal_name": "Test Deal",
            "evaluator_role": "Financial Advisor",
            "evaluation": "Test evaluation",
            "initial_evaluation": "Initial evaluation",
            "thinking_trace": [],
            "rounds_completed": 2,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create a sample deal
        deal = Deal(
            name="Test Deal",
            description="A test deal",
            participants=["player1", "player2"]
        )
        
        # Call the deal evaluation function
        result = self.adapter.deal_evaluation_function(deal)
        
        # Check that the evaluator was called with the right arguments
        self.mock_evaluator.evaluate_deal.assert_called_once()
        call_args = self.mock_evaluator.evaluate_deal.call_args[1]
        self.assertEqual(call_args["deal"], deal)
        self.assertEqual(call_args["evaluator_role"], "Financial Advisor")
        
        # Check that the evaluation criteria were domain-specific
        criteria = call_args["evaluation_criteria"]
        self.assertEqual(len(criteria), 4)
        self.assertIn("finance", criteria[0]["name"].lower())
        
        # Check the result
        self.assertEqual(result["deal_id"], "deal-123")
        self.assertEqual(result["evaluation"], "Test evaluation")
    
    def test_enhance_agent_with_cort(self):
        """Test enhancing an agent with CoRT capabilities."""
        # Create a mock agent with some methods
        class MockAgent:
            def __init__(self):
                self.name = "Mock Agent"
            
            async def deal_method(self, arg1, arg2):
                return {"result": f"Deal result for {arg1} and {arg2}"}
            
            async def non_deal_method(self, arg):
                return {"result": f"Non-deal result for {arg}"}
        
        mock_agent = MockAgent()
        
        # Use the helper function to enhance the agent
        with patch('specialized_agents.collaboration.cort_agent_adapter.CoRTAgentAdapter') as mock_adapter_class:
            # Set up the mock adapter to return enhanced functions
            mock_adapter = MagicMock()
            mock_adapter_class.return_value = mock_adapter
            
            # Mock the enhance_function method
            async def mock_enhanced_function(*args, **kwargs):
                return {"enhanced": True, "original_args": args, "original_kwargs": kwargs}
            
            mock_adapter.enhance_function.return_value = mock_enhanced_function
            mock_adapter.deal_evaluation_function = lambda deal: {"deal_id": getattr(deal, "id", "unknown")}
            mock_adapter.solution_comparison_function = lambda problem, solutions: {"problem_id": getattr(problem, "id", "unknown")}
            mock_adapter.transaction_negotiation_function = lambda transaction, from_player, to_player: {"transaction_id": getattr(transaction, "id", "unknown")}
            
            # Call the helper function
            enhanced_methods = enhance_agent_with_cort(
                agent=mock_agent,
                domain="finance",
                role="Financial Advisor",
                expertise=["investment", "retirement"]
            )
            
            # Check that the adapter was created with the right parameters
            mock_adapter_class.assert_called_once()
            adapter_args = mock_adapter_class.call_args[1]
            self.assertEqual(adapter_args["agent_domain"], "finance")
            self.assertEqual(adapter_args["agent_role"], "Financial Advisor")
            self.assertEqual(adapter_args["agent_expertise"], ["investment", "retirement"])
            
            # Check that the deal method was enhanced
            self.assertIn("cort_deal_method", enhanced_methods)
            self.assertEqual(mock_adapter.enhance_function.call_count, 1)
            
            # Check that the standard evaluation functions were added
            self.assertIn("evaluate_deal_with_cort", enhanced_methods)
            self.assertIn("compare_solutions_with_cort", enhanced_methods)
            self.assertIn("negotiate_transaction_with_cort", enhanced_methods)


if __name__ == "__main__":
    unittest.main()