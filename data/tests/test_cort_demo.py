"""
Tests for the CoRT basic demo.

This module contains tests for the CoRT basic demo functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path
import json

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.cort_demo import CoRTBasicDemo


class TestCoRTBasicDemo(unittest.TestCase):
    """Tests for the CoRTBasicDemo class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the LLM model
        self.model_patcher = patch('langchain_google_genai.ChatGoogleGenerativeAI')
        self.mock_model_cls = self.model_patcher.start()
        
        # Configure the mock model
        self.mock_model = MagicMock()
        self.mock_model_cls.return_value = self.mock_model
        
        # Configure the invoke method to return a mock response
        self.mock_response = MagicMock()
        self.mock_response.content = "Mock response content"
        self.mock_model.invoke.return_value = self.mock_response
        
        # Create a mock for the CoRT processor
        self.processor_patcher = patch('common.utils.recursive_thought.get_recursive_thought_processor')
        self.mock_processor_fn = self.processor_patcher.start()
        
        # Configure the mock processor
        self.mock_processor = MagicMock()
        self.mock_processor_fn.return_value = self.mock_processor
        
        # Configure process method to return a mock result
        self.mock_processor.process.return_value = {
            "query": "Test query",
            "initial_response": "Initial response",
            "final_response": "Final response",
            "thinking_trace": [
                {"round": 0, "response": "Initial response"},
                {"round": 1, "alternatives": ["Alt 1", "Alt 2", "Alt 3"], "best_index": 1}
            ],
            "rounds_completed": 1
        }
        
        # Initialize environment variable patch
        self.env_patcher = patch('os.getenv')
        self.mock_getenv = self.env_patcher.start()
        self.mock_getenv.return_value = "mock-api-key"  # Simulate having the API key
        
        # Create the demo instance
        self.demo = CoRTBasicDemo(
            model_name="test-model",
            max_rounds=2,
            generate_alternatives=2,
            dynamic_rounds=True,
            detailed_logging=False
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.model_patcher.stop()
        self.processor_patcher.stop()
        self.env_patcher.stop()
    
    def test_initialization(self):
        """Test that the demo initializes correctly."""
        # Check that the mock was initialized with the right model name
        self.mock_model_cls.assert_called_once_with(model="test-model")
        
        # Check that the processor was initialized with the right parameters
        self.mock_processor_fn.assert_called_once()
        args, kwargs = self.mock_processor_fn.call_args
        self.assertEqual(kwargs['max_rounds'], 2)
        self.assertEqual(kwargs['generate_alternatives'], 2)
        self.assertTrue(kwargs['dynamic_rounds'])
        self.assertFalse(kwargs['detailed_logging'])
    
    def test_run_standard_examples(self):
        """Test running standard examples."""
        # Run the standard examples
        results = self.demo.run_standard_examples()
        
        # Check that the processor was called for each example
        self.assertEqual(self.mock_processor.process.call_count, 3)
        
        # Check that results dictionary has expected keys
        self.assertIn("Strategic Decision", results)
        self.assertIn("Complex Analysis", results)
        self.assertIn("Creative Writing", results)
        
        # Verify that context was passed correctly
        context_args = [call[1].get('task_context', {}) for call in self.mock_processor.process.call_args_list]
        domains = [ctx.get('domain', '') for ctx in context_args]
        self.assertIn("business_strategy", domains)
        self.assertIn("computer_science", domains)
        self.assertIn("creative_writing", domains)
    
    def test_run_with_custom_query(self):
        """Test running with a custom query."""
        # Run with a custom query
        result = self.demo.run_with_custom_query(
            query="Custom test query",
            context={"domain": "test_domain", "custom": "value"}
        )
        
        # Check that the processor was called with the right arguments
        self.mock_processor.process.assert_called_with(
            query="Custom test query",
            task_context={"domain": "test_domain", "custom": "value"}
        )
        
        # Check the result
        self.assertEqual(result["initial_response"], "Initial response")
        self.assertEqual(result["final_response"], "Final response")
        self.assertEqual(result["rounds_completed"], 1)
    
    def test_demonstrate_round_determination(self):
        """Test demonstrating round determination."""
        # Configure the mock processor's _determine_rounds method
        # Return different values based on complexity
        self.mock_processor._determine_rounds = MagicMock()
        self.mock_processor._determine_rounds.side_effect = [1, 2, 3]  # Simple, Moderate, Complex
        
        # Run the demonstration
        results = self.demo.demonstrate_round_determination()
        
        # Check that the method was called for each complexity level
        self.assertEqual(self.mock_processor._determine_rounds.call_count, 3)
        
        # Check the results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["complexity"], "Simple")
        self.assertEqual(results[0]["determined_rounds"], 1)
        self.assertEqual(results[1]["complexity"], "Moderate")
        self.assertEqual(results[1]["determined_rounds"], 2)
        self.assertEqual(results[2]["complexity"], "Complex")
        self.assertEqual(results[2]["determined_rounds"], 3)
    
    def test_error_handling(self):
        """Test error handling in LLM generation."""
        # Make the model.invoke method raise an exception
        self.mock_model.invoke.side_effect = Exception("Test error")
        
        # Create a new demo instance using the mock
        demo = CoRTBasicDemo(
            model_name="test-model",
            max_rounds=2,
            generate_alternatives=2
        )
        
        # Call the generator function directly to check error handling
        result = demo.llm_generator("Test prompt")
        
        # Verify that the error was handled and a meaningful message returned
        self.assertTrue(result.startswith("Error generating response:"))
        self.assertIn("Test error", result)


class TestCoRTDemoMissingAPI(unittest.TestCase):
    """Tests for handling missing API key."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create patches
        self.env_patcher = patch('os.getenv')
        self.mock_getenv = self.env_patcher.start()
        self.mock_getenv.return_value = None  # Simulate missing API key
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()
    
    def test_missing_api_key(self):
        """Test that initialization fails with proper error when API key is missing."""
        with self.assertRaises(ValueError) as context:
            CoRTBasicDemo()
        
        self.assertIn("GOOGLE_API_KEY environment variable is required", str(context.exception))


if __name__ == "__main__":
    unittest.main()