"""
Tests for the CoRT-enhanced React Agent.

This module contains tests for the CoRT implementation integrated with the React Agent.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path
import json

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.cort_react_agent import CoRTReactAgent


class TestCoRTReactAgent(unittest.TestCase):
    """Tests for the CoRTReactAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the LLM model
        self.model_patcher = patch('langchain_google_genai.ChatGoogleGenerativeAI')
        self.mock_model_cls = self.model_patcher.start()
        
        # Configure the mock model
        self.mock_model = MagicMock()
        self.mock_model_cls.return_value = self.mock_model
        
        # Mock responses for the model
        self.mock_model.invoke.return_value = MagicMock(content="Mocked response")
        
        # Create a mock for the graph
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
        
        # Create a mock for the CoRT processor
        self.cort_processor_patcher = patch('common.utils.recursive_thought.get_recursive_thought_processor')
        self.mock_processor_fn = self.cort_processor_patcher.start()
        
        # Configure the mock processor
        self.mock_processor = MagicMock()
        self.mock_processor_fn.return_value = self.mock_processor
        
        # Configure process method to return a mock result
        self.mock_processor.process.return_value = {
            "query": "Test query",
            "initial_response": "Initial response",
            "final_response": "Enhanced response",
            "thinking_trace": [
                {"round": 0, "response": "Initial response"},
                {"round": 1, "alternatives": ["Alt 1", "Alt 2", "Alt 3"], "best_index": 1}
            ],
            "rounds_completed": 1
        }
        
        # Configure process_with_tools method to return a mock result
        self.mock_processor.process_with_tools.return_value = {
            "query": "Test query",
            "initial_response": "Initial response",
            "final_response": "Enhanced response with tools",
            "thinking_trace": [
                {"round": 0, "response": "Initial response"},
                {"round": 1, "alternatives": ["Alt 1", "Alt 2", "Alt 3"], "best_index": 1}
            ],
            "rounds_completed": 1,
            "tool_usage": [
                {"tool": "test_tool", "input": "test input", "output": "test output"}
            ]
        }
        
        # Create a mock for the environment
        self.env_patcher = patch('os.getenv')
        self.mock_getenv = self.env_patcher.start()
        self.mock_getenv.return_value = "mock-api-key"
        
        # Create a mock for the tools
        self.tools_patcher = patch.multiple(
            'graph.cort_react_agent',
            CurrencyTool=MagicMock(return_value=MagicMock(name="currency_tool")),
            MathTool=MagicMock(return_value=MagicMock(name="math_tool")),
            A2AMCPTool=MagicMock(return_value=MagicMock(name="a2a_mcp_tool")),
            SpecializedAgentTool=MagicMock(return_value=MagicMock(name="specialized_agent_tool"))
        )
        self.tools_patcher.start()
        
        # Initialize the agent
        self.agent = CoRTReactAgent(
            model_name="test-model",
            cort_max_rounds=2,
            cort_alternatives=2,
            cort_enabled_by_default=True
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.model_patcher.stop()
        self.graph_patcher.stop()
        self.cort_processor_patcher.stop()
        self.env_patcher.stop()
        self.tools_patcher.stop()
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        # Check that the model was initialized with the right model name
        self.mock_model_cls.assert_called_once_with(model="test-model")
        
        # Check that the graph was created
        self.mock_graph_fn.assert_called_once()
        
        # Check CoRT configuration
        self.assertEqual(self.agent.cort_max_rounds, 2)
        self.assertEqual(self.agent.cort_alternatives, 2)
        self.assertTrue(self.agent.cort_enabled_by_default)
    
    def test_invoke_with_cort(self):
        """Test invoking the agent with CoRT enabled."""
        # Invoke the agent
        result = self.agent.invoke(
            query="Test query",
            session_id="test-session",
            use_cort=True
        )
        
        # Check that the graph was invoked
        self.mock_graph.invoke.assert_called_once()
        
        # Check that the CoRT processor was used
        self.mock_processor.process.assert_called_once()
        
        # Check the result
        self.assertEqual(result["input"], "Test query")
        self.assertEqual(result["output"], "Enhanced response")
        self.assertEqual(result["initial_output"], "Agent response")
        self.assertTrue(result["cort_enabled"])
        self.assertEqual(result["rounds_completed"], 1)
        self.assertIn("thinking_trace", result)
    
    def test_invoke_without_cort(self):
        """Test invoking the agent with CoRT disabled."""
        # Invoke the agent
        result = self.agent.invoke(
            query="Test query",
            session_id="test-session",
            use_cort=False
        )
        
        # Check that the graph was invoked
        self.mock_graph.invoke.assert_called_once()
        
        # Check that the CoRT processor was not used
        self.mock_processor.process.assert_not_called()
        
        # Check the result
        self.assertEqual(result["input"], "Test query")
        self.assertEqual(result["output"], "Agent response")
        self.assertFalse(result["cort_enabled"])
        self.assertNotIn("rounds_completed", result)
        self.assertNotIn("thinking_trace", result)
    
    def test_invoke_with_tools(self):
        """Test invoking the agent with tools and CoRT."""
        # Configure the mock graph to include tool calls
        tool_call = MagicMock(name="test_tool", args="test input")
        tool_response = MagicMock(content="test output", name="test_tool")
        
        self.mock_graph.invoke.return_value = {
            "messages": [
                MagicMock(content="User query"),
                MagicMock(content="Calling tool", tool_calls=[tool_call]),
                tool_response,
                MagicMock(content="Agent response with tool", tool_calls=None)
            ]
        }
        
        # Invoke the agent
        result = self.agent.invoke_with_tools(
            query="Test query with tools",
            session_id="test-session",
            use_cort=True
        )
        
        # Check that the graph was invoked
        self.mock_graph.invoke.assert_called_once()
        
        # Check that the CoRT processor was used with tools
        self.mock_processor.process_with_tools.assert_called_once()
        
        # Check the result
        self.assertEqual(result["input"], "Test query with tools")
        self.assertEqual(result["output"], "Enhanced response with tools")
        self.assertTrue(result["cort_enabled"])
        self.assertEqual(result["rounds_completed"], 1)
        self.assertIn("thinking_trace", result)
        self.assertIn("tool_usage", result)
    
    def test_get_chat_history(self):
        """Test getting chat history."""
        # Configure the mock graph to return a state with messages
        state = MagicMock()
        state.values = {
            "messages": [
                MagicMock(spec="HumanMessage", content="User message 1"),
                MagicMock(spec="AIMessage", content="AI message 1"),
                MagicMock(spec="HumanMessage", content="User message 2"),
                MagicMock(spec="AIMessage", content="AI message 2")
            ]
        }
        self.mock_graph.get_state.return_value = state
        
        # Get chat history
        history = self.agent.get_chat_history("test-session")
        
        # Check the result
        self.assertEqual(len(history), 4)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "User message 1")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "AI message 1")


class TestCoRTReactAgentMissingAPI(unittest.TestCase):
    """Tests for handling missing API key."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the environment
        self.env_patcher = patch('os.getenv')
        self.mock_getenv = self.env_patcher.start()
        self.mock_getenv.return_value = None  # Simulate missing API key
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()
    
    def test_missing_api_key(self):
        """Test that initialization fails with proper error when API key is missing."""
        with self.assertRaises(ValueError) as context:
            CoRTReactAgent()
        
        self.assertIn("GOOGLE_API_KEY environment variable not set", str(context.exception))


if __name__ == "__main__":
    unittest.main()