"""
Chain of Recursive Thoughts (CoRT) Specification Tests.

This module provides detailed specification tests to verify the CoRT implementation
meets the requirements and functions correctly.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.utils.recursive_thought import CoRTProcessor, get_recursive_thought_processor


class CoRTSpecifications(unittest.TestCase):
    """Specifications for the Chain of Recursive Thoughts implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LLM generator
        self.mock_llm = MagicMock()
        
        # Create a CoRT processor with the mock LLM
        self.processor = CoRTProcessor(
            llm_generator=self.mock_llm,
            max_rounds=2,
            generate_alternatives=2,
            dynamic_rounds=False,
            detailed_logging=False
        )
    
    def test_spec_1_process_with_prompt_instructions(self):
        """SPEC 1: Should correctly use provided prompt instructions."""
        # Reset the mock
        self.mock_llm.reset_mock()
        self.mock_llm.side_effect = [
            # For generating alternatives
            json.dumps(["Alternative 1", "Alternative 2"]),
            # For evaluating alternatives
            json.dumps({"best_index": 1})
        ]
        
        # Process with prompt_instructions
        self.processor.process(
            query="Test query",
            initial_response="Initial response",
            prompt_instructions="Important specific instructions"
        )
        
        # Check that prompt_instructions was included in the calls to the LLM
        call_args = self.mock_llm.call_args_list
        prompt_instructions_used = any(
            "Important specific instructions" in str(args[0]) 
            for args, kwargs in call_args
        )
        
        self.assertTrue(prompt_instructions_used, "Prompt instructions were not used in LLM calls")
    
    def test_spec_2_alternatives_simple_fallback(self):
        """SPEC 2: Should use simple alternatives generation as fallback."""
        # Reset the mock
        self.mock_llm.reset_mock()
        
        # First call fails with JSON error, second calls succeed
        self.mock_llm.side_effect = [
            "Not a JSON response",  # Main alternatives generation fails
            "Alternative 1",        # Simple alternative 1
            "Alternative 2",        # Simple alternative 2
            json.dumps({"best_index": 1})  # Evaluation succeeds
        ]
        
        # Process a query
        result = self.processor.process(
            query="Test query",
            initial_response="Initial response"
        )
        
        # Check that the simple alternatives function was used
        self.assertEqual(self.mock_llm.call_count, 4)
        
        # Check that the result contains alternatives
        self.assertGreater(
            len(result["thinking_trace"][1].get("alternatives", [])), 
            1, 
            "No alternatives were generated using fallback method"
        )
    
    def test_spec_3_handle_json_extraction_failures(self):
        """SPEC 3: Should handle JSON extraction failures gracefully."""
        # Reset the mock
        self.mock_llm.reset_mock()
        
        # Set up the mock to return invalid JSON
        self.mock_llm.side_effect = [
            "Not a JSON but has alternatives:\n1. First alternative\n2. Second alternative",
            "Evaluation with best response: 1"  # Text with a number indicating best response
        ]
        
        # Process a query
        result = self.processor.process(
            query="Test query",
            initial_response="Initial response"
        )
        
        # Check that processing completed despite JSON failures
        self.assertIn("final_response", result)
        self.assertIn("thinking_trace", result)
        self.assertEqual(result["rounds_completed"], 2)
    
    def test_spec_4_dynamic_rounds_determination(self):
        """SPEC 4: Should dynamically determine optimal number of rounds."""
        # Create a processor with dynamic rounds
        dynamic_processor = CoRTProcessor(
            llm_generator=self.mock_llm,
            max_rounds=5,
            generate_alternatives=2,
            dynamic_rounds=True
        )
        
        # Reset the mock
        self.mock_llm.reset_mock()
        
        # Set up the mock to suggest 3 rounds
        self.mock_llm.return_value = "For this query, 3 rounds would be appropriate."
        
        # Determine rounds
        rounds = dynamic_processor._determine_rounds("Complex query requiring multiple perspectives")
        
        # Should extract 3 from the response
        self.assertEqual(rounds, 3)
        
        # Reset and test with non-numeric response
        self.mock_llm.reset_mock()
        self.mock_llm.return_value = "This requires careful consideration."
        
        # Should default to max rounds
        rounds = dynamic_processor._determine_rounds("Complex query")
        self.assertEqual(rounds, 5)
    
    def test_spec_5_maintain_thinking_trace(self):
        """SPEC 5: Should maintain a complete thinking trace."""
        # Reset the mock
        self.mock_llm.reset_mock()
        
        # Set up the mock responses
        self.mock_llm.side_effect = [
            # For round 1
            json.dumps(["Alternative 1", "Alternative 2"]),
            json.dumps({"best_index": 1, "evaluations": [{"score": 7}, {"score": 9}]}),
            # For round 2
            json.dumps(["Alternative 3", "Alternative 4"]),
            json.dumps({"best_index": 0, "evaluations": [{"score": 8}, {"score": 6}]})
        ]
        
        # Process a query
        result = self.processor.process(
            query="Test query",
            initial_response="Initial response"
        )
        
        # Check the thinking trace structure
        trace = result["thinking_trace"]
        
        # Should have 3 entries: initial + 2 rounds
        self.assertEqual(len(trace), 3)
        
        # Initial entry
        self.assertEqual(trace[0]["round"], 0)
        self.assertEqual(trace[0]["response"], "Initial response")
        
        # Round 1
        self.assertEqual(trace[1]["round"], 1)
        self.assertIn("alternatives", trace[1])
        self.assertIn("best_index", trace[1])
        self.assertIn("evaluation", trace[1])
        
        # Round 2
        self.assertEqual(trace[2]["round"], 2)
        self.assertIn("alternatives", trace[2])
        self.assertIn("best_index", trace[2])
        self.assertIn("evaluation", trace[2])
    
    def test_spec_6_handle_llm_errors_gracefully(self):
        """SPEC 6: Should handle LLM errors gracefully."""
        # Reset the mock
        self.mock_llm.reset_mock()
        
        # Set up the mock to raise an exception
        self.mock_llm.side_effect = Exception("LLM Error")
        
        # Process a query
        result = self.processor.process(
            query="Test query",
            initial_response="Initial response"
        )
        
        # Should complete without raising an exception
        self.assertIn("final_response", result)
        self.assertEqual(result["final_response"], "Initial response")  # Should keep initial response
    
    def test_spec_7_extract_best_index_from_text(self):
        """SPEC 7: Should extract best index from unstructured text."""
        # Test with different text formats
        test_cases = [
            ("The best response is 2.", 1),  # Converting from 1-indexed to 0-indexed
            ("Response 1 score: 7, Response 2 score: 9", 1),  # Higher score
            ("I recommend alternative 2 because it's more comprehensive.", 1),
            ("Looking at all options, response #2 is best.", 1)
        ]
        
        for text, expected_index in test_cases:
            extracted = self.processor._extract_best_index_from_text(text, 3)
            self.assertEqual(
                extracted, 
                expected_index, 
                f"Failed to extract correct index from: {text}"
            )
    
    def test_spec_8_process_with_tools(self):
        """SPEC 8: Should integrate with tools correctly."""
        # Create mock tools and executor
        mock_tools = [MagicMock(), MagicMock()]
        mock_executor = MagicMock(return_value="Tool result")
        
        # Use patching to avoid actual processing
        with patch.object(self.processor, 'process') as mock_process:
            # Set up the mock to return a reasonable result
            mock_process.return_value = {
                "final_response": "Final response using tools",
                "thinking_trace": [{"round": 0, "response": "Initial"}]
            }
            
            # Process with tools
            result = self.processor.process_with_tools(
                query="What is 2+2?",
                tools=mock_tools,
                tool_executor=mock_executor
            )
            
            # Verify tool integration
            self.assertIn("tool_usage", result)
            self.assertIn("thinking_trace", result)
    
    def test_spec_9_helper_function(self):
        """SPEC 9: Helper function should create a correctly configured processor."""
        # Create a mock LLM function
        mock_llm_fn = MagicMock()
        
        # Get a processor using the helper function
        processor = get_recursive_thought_processor(
            llm_fn=mock_llm_fn,
            max_rounds=4,
            generate_alternatives=3,
            dynamic_rounds=True,
            detailed_logging=True
        )
        
        # Verify configuration
        self.assertEqual(processor.llm_generator, mock_llm_fn)
        self.assertEqual(processor.max_rounds, 4)
        self.assertEqual(processor.generate_alternatives, 3)
        self.assertTrue(processor.dynamic_rounds)
        self.assertTrue(processor.detailed_logging)
    
    def test_spec_10_extract_alternatives_from_text(self):
        """SPEC 10: Should extract alternatives from unstructured text."""
        # Test with different text formats
        test_cases = [
            # Numbered list
            ("""
            1. First alternative
            2. Second alternative
            """, 2),
            
            # Quoted text
            ("""
            Here are some options:
            "Alternative one"
            "Alternative two"
            """, 2),
            
            # Paragraphs
            ("""
            Alternative one.
            
            Alternative two.
            """, 2)
        ]
        
        for text, expected_count in test_cases:
            alternatives = self.processor._extract_alternatives_from_text(text)
            self.assertEqual(
                len(alternatives),
                expected_count,
                f"Failed to extract correct number of alternatives from text"
            )


if __name__ == "__main__":
    unittest.main()