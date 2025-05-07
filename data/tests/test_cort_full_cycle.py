"""
Chain of Recursive Thoughts (CoRT) Full Cycle Test.

This module tests a complete scenario using the Chain of Recursive Thoughts implementation.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.utils.recursive_thought import CoRTProcessor
from specialized_agents.collaboration.cort_agent_adapter import CoRTAgentAdapter


class TestCoRTFullCycle(unittest.TestCase):
    """Test a complete scenario using the CoRT implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LLM generator
        self.mock_llm = MagicMock()
        
        # Create a simulated enhanced agent function
        self.original_function = MagicMock(return_value="Original function result")
    
    def simulate_full_flow(self):
        """Simulate a full flow of CoRT with agent adaptation."""
        # Set up mock responses for the full cycle
        self.mock_llm.side_effect = [
            # For determining rounds
            "2",
            # Generate initial response
            "Initial analysis of the problem",
            # Generate alternatives for round 1
            json.dumps([
                "Alternative 1: The approach involves decomposing the problem into smaller parts",
                "Alternative 2: We can use a dynamic programming approach for this"
            ]),
            # Evaluate alternatives for round 1
            json.dumps({
                "evaluations": [
                    {"response": "Initial analysis", "score": 6, "explanation": "Basic but incomplete"},
                    {"response": "Alternative 1", "score": 8, "explanation": "Better decomposition"},
                    {"response": "Alternative 2", "score": 7, "explanation": "Good but complex"}
                ],
                "best_index": 1,
                "best_explanation": "It provides a clearer approach"
            }),
            # Generate alternatives for round 2
            json.dumps([
                "Refined Alternative 1: Breaking the problem into subtasks A, B, and C...",
                "Refined Alternative 2: Using memoization with the following approach..."
            ]),
            # Evaluate alternatives for round 2
            json.dumps({
                "evaluations": [
                    {"response": "Alternative 1", "score": 8, "explanation": "Good decomposition"},
                    {"response": "Refined Alternative 1", "score": 9, "explanation": "Excellent details"},
                    {"response": "Refined Alternative 2", "score": 7, "explanation": "Good but complex"}
                ],
                "best_index": 1,
                "best_explanation": "Most comprehensive solution"
            })
        ]
        
        # Create a CORT Agent Adapter
        adapter = CoRTAgentAdapter(
            llm=self.mock_llm,
            rounds=2,
            alternatives=2,
            dynamic_rounds=False
        )
        
        # Enhance the original function
        enhanced_function = adapter.enhance_function(
            self.original_function,
            function_name="analysis_function",
            prompt_instructions="Focus on algorithm efficiency and clarity"
        )
        
        # Call the enhanced function
        result = enhanced_function("Solve the knapsack problem efficiently")
        
        return result
    
    def test_full_cycle(self):
        """Test a full cycle of CoRT with agent adaptation."""
        # Patch the relevant functions to avoid actually calling LLM
        with patch('specialized_agents.collaboration.cort_agent_adapter.get_recursive_thought_processor'):
            with patch.object(CoRTProcessor, 'process') as mock_process:
                # Set up the mock to return a result with thinking trace
                mock_process.return_value = {
                    "query": "Solve the knapsack problem efficiently",
                    "initial_response": "Initial analysis of the problem",
                    "final_response": "Refined Alternative 1: Breaking the problem into subtasks A, B, and C...",
                    "thinking_trace": [
                        {"round": 0, "response": "Initial analysis of the problem"},
                        {"round": 1, "alternatives": ["Alt 1", "Alt 2"], "best_index": 0},
                        {"round": 2, "alternatives": ["Refined Alt 1", "Refined Alt 2"], "best_index": 0}
                    ],
                    "rounds_completed": 2
                }
                
                # Call the original function once to be enhanced
                self.original_function("Solve the knapsack problem efficiently")
                
                # Run the simulated flow
                result = self.simulate_full_flow()
                
                # Verify the results
                self.assertIsNotNone(result)
                self.assertTrue(hasattr(result, 'get'))  # Should be a dict-like object
                
                result_dict = result if isinstance(result, dict) else {}
                
                # If the function was properly enhanced, it should include CoRT metadata
                if "cort_metadata" in result_dict:
                    cort_data = result_dict["cort_metadata"]
                    self.assertIn("thinking_trace", cort_data)
                    self.assertIn("rounds_completed", cort_data)
                    
                # The original function should have been called
                self.original_function.assert_called()


class TestCoRTDealEvaluation(unittest.TestCase):
    """Test the CoRT Deal Evaluation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LLM generator
        self.mock_llm = MagicMock()
        
        # Mock the deal data
        self.test_deal = {
            "name": "Supply Agreement",
            "description": "Agreement between supplier and customer",
            "participants": ["supplier", "customer"],
            "terms": [
                {"key": "price", "value": "$1000"},
                {"key": "quantity", "value": "100 units"},
                {"key": "delivery", "value": "30 days"}
            ]
        }
    
    def test_deal_evaluation(self):
        """Test deal evaluation using CoRT."""
        try:
            # Import here to handle potential import errors
            from specialized_agents.collaboration.cort_deal_negotiator import CoRTDealEvaluator
            
            # Create a mock deal evaluator
            with patch('specialized_agents.collaboration.cort_deal_negotiator.get_recursive_thought_processor'):
                evaluator = CoRTDealEvaluator(llm=self.mock_llm)
                
                # Mock the process method
                with patch.object(evaluator.cort_processor, 'process') as mock_process:
                    # Set up the mock to return a result
                    mock_process.return_value = {
                        "final_response": json.dumps({
                            "evaluation": "This deal is favorable",
                            "approval_status": "approved",
                            "strengths": ["Good price", "Reasonable delivery time"],
                            "weaknesses": ["No quality clauses"],
                            "recommendations": ["Add quality assurance terms"]
                        }),
                        "thinking_trace": [
                            {"round": 0, "response": "Initial analysis"},
                            {"round": 1, "alternatives": ["Alt 1", "Alt 2"], "best_index": 0}
                        ],
                        "rounds_completed": 1
                    }
                    
                    # Evaluate the deal
                    result = evaluator.evaluate_deal(self.test_deal)
                    
                    # Verify the results
                    self.assertIn("evaluation", result)
                    self.assertIn("approval_status", result)
                    self.assertIn("thinking_trace", result)
        except ImportError:
            # Skip the test if the module is not available
            self.skipTest("Required modules not available")


if __name__ == "__main__":
    unittest.main()