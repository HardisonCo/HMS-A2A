"""
Integration Tests for Chain of Recursive Thoughts.

This module contains integration tests to ensure that all CoRT components
work together correctly.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import asyncio

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.utils.recursive_thought import get_recursive_thought_processor
from graph.cort_react_agent import CoRTReactAgent
from specialized_agents.collaboration.cort_deal_negotiator import CoRTDealEvaluator
from specialized_agents.collaboration.cort_agent_adapter import CoRTAgentAdapter


class TestCoRTIntegration(unittest.TestCase):
    """Integration tests for CoRT components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the LLM model
        self.model_patcher = patch('langchain_google_genai.ChatGoogleGenerativeAI')
        self.mock_model_cls = self.model_patcher.start()
        
        # Configure the mock model
        self.mock_model = MagicMock()
        self.mock_model_cls.return_value = self.mock_model
        
        # Configure responses for the model
        self.mock_model.invoke.return_value = MagicMock(content="Mocked LLM response")
        
        # Environment setup
        self.env_patcher = patch('os.getenv')
        self.mock_getenv = self.env_patcher.start()
        self.mock_getenv.return_value = "mock-api-key"
        
        # Create a mock for graph components
        self.graph_patcher = patch('langgraph.prebuilt.create_react_agent')
        self.mock_graph_fn = self.graph_patcher.start()
        
        # Configure the mock graph
        self.mock_graph = MagicMock()
        self.mock_graph_fn.return_value = self.mock_graph
        
        # Configure the invoke method to return a mock response
        self.mock_graph.invoke.return_value = {
            "messages": [
                MagicMock(content="User query"),
                MagicMock(content="Agent response", tool_calls=None)
            ]
        }
        
        # Mock tools
        self.tools_patcher = patch.multiple(
            'graph.cort_react_agent',
            CurrencyTool=MagicMock(return_value=MagicMock(name="currency_tool")),
            MathTool=MagicMock(return_value=MagicMock(name="math_tool")),
            A2AMCPTool=MagicMock(return_value=MagicMock(name="a2a_mcp_tool")),
            SpecializedAgentTool=MagicMock(return_value=MagicMock(name="specialized_agent_tool"))
        )
        self.tools_patcher.start()
        
        # Create a simple LLM generator function for testing
        def test_llm_generator(prompt):
            return f"Response to: {prompt[:20]}..."
        
        self.llm_generator = test_llm_generator
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.model_patcher.stop()
        self.env_patcher.stop()
        self.graph_patcher.stop()
        self.tools_patcher.stop()
    
    def test_cort_processor_creation(self):
        """Test that the CoRT processor can be created and configured."""
        processor = get_recursive_thought_processor(
            llm_fn=self.llm_generator,
            max_rounds=3,
            generate_alternatives=3,
            dynamic_rounds=True
        )
        
        self.assertEqual(processor.max_rounds, 3)
        self.assertEqual(processor.generate_alternatives, 3)
        self.assertTrue(processor.dynamic_rounds)
        self.assertEqual(processor.llm_generator, self.llm_generator)
    
    def test_cort_react_agent_integration(self):
        """Test that the CoRT React agent can be created and used."""
        agent = CoRTReactAgent(
            model_name="test-model",
            cort_max_rounds=2,
            cort_alternatives=2
        )
        
        # Ensure the CoRT processor is initialized correctly
        processor = agent.cort_processor
        self.assertEqual(processor.max_rounds, 2)
        self.assertEqual(processor.generate_alternatives, 2)
        
        # Test invoking the agent
        result = agent.invoke("Test query", use_cort=True)
        self.assertIn("output", result)
        self.assertIn("thinking_trace", result)
    
    def test_cort_deal_evaluator_integration(self):
        """Test that the CoRT deal evaluator can be created and used."""
        evaluator = CoRTDealEvaluator(
            llm_generator=self.llm_generator,
            max_rounds=2,
            generate_alternatives=2
        )
        
        # Ensure the CoRT processor is initialized correctly
        self.assertEqual(evaluator.cort_processor.max_rounds, 2)
        self.assertEqual(evaluator.cort_processor.generate_alternatives, 2)
    
    def test_cort_agent_adapter_integration(self):
        """Test that the CoRT agent adapter can be created and used."""
        adapter = CoRTAgentAdapter(
            agent_domain="test_domain",
            agent_role="Test Role",
            agent_expertise=["test"],
            llm_generator=self.llm_generator
        )
        
        # Ensure the CoRT processor is initialized correctly
        self.assertEqual(adapter.cort_processor.llm_generator, self.llm_generator)
        
        # Test creating an enhancement prompt
        prompt = adapter._create_enhancement_prompt(
            function_name="test_function",
            original_result="test result",
            context={"test_key": "test_value"}
        )
        
        self.assertIn("test_function", prompt)
        self.assertIn("test result", prompt)
        self.assertIn("test_key: test_value", prompt)
    
    def test_end_to_end_integration(self):
        """Test basic end-to-end integration of CoRT components."""
        # Create the CoRT processor
        processor = get_recursive_thought_processor(
            llm_fn=self.llm_generator,
            max_rounds=2,
            generate_alternatives=2
        )
        
        # Process a simple query
        result = processor.process(
            query="Test integration query",
            initial_response="Initial response"
        )
        
        # Check the result structure
        self.assertIn("query", result)
        self.assertIn("initial_response", result)
        self.assertIn("final_response", result)
        self.assertIn("thinking_trace", result)
        self.assertIn("rounds_completed", result)
        
        # Check that thinking_trace has the right structure
        self.assertGreaterEqual(len(result["thinking_trace"]), 1)
        self.assertIn("round", result["thinking_trace"][0])
        
        # For rounds beyond the first, check for alternatives
        if len(result["thinking_trace"]) > 1:
            self.assertIn("alternatives", result["thinking_trace"][1])
            self.assertIn("best_index", result["thinking_trace"][1])


if __name__ == "__main__":
    unittest.main()