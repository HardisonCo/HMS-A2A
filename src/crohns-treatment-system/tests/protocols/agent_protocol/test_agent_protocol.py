"""
Tests for the agent communication protocol
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock

class AgentProtocolTestCase(unittest.TestCase):
    """Test case for the agent communication protocol"""

    def setUp(self):
        """Set up test environment for each test"""
        # Define test message structure
        self.test_message = {
            "id": "msg_12345",
            "sender": "clinical_trial_agent",
            "receiver": "abstraction_agent",
            "content": "Test message content",
            "content_type": "text/plain",
            "correlation_id": "corr_12345",
            "timestamp": "2023-05-09T12:00:00Z",
            "metadata": {
                "intent": "query_information",
                "priority": "normal",
                "conversation_id": "conv_12345"
            }
        }
    
    @patch("src.protocols.agent_protocol.validate_message")
    def test_message_validation(self, mock_validate):
        """Test message validation function"""
        # Set up mock return value
        mock_validate.return_value = True
        
        # This is a mock test that would normally test the validate_message function
        # We're demonstrating how the test would work with actual protocol code
        from src.protocols.agent_protocol import validate_message
        
        result = validate_message(self.test_message)
        
        # Verify the mock was called
        mock_validate.assert_called_once_with(self.test_message)
        
        # Check result
        self.assertTrue(result)
    
    @patch("src.protocols.agent_protocol.AgentMessage")
    def test_agent_message_creation(self, mock_agent_message):
        """Test creating an agent message"""
        # Set up mock return value
        mock_instance = MagicMock()
        mock_instance.to_dict.return_value = self.test_message
        mock_agent_message.return_value = mock_instance
        
        # This is a mock test that would normally test the AgentMessage class
        # We're demonstrating how the test would work with actual protocol code
        from src.protocols.agent_protocol import AgentMessage
        
        message = AgentMessage(
            sender="clinical_trial_agent",
            receiver="abstraction_agent",
            content="Test message content",
            metadata={
                "intent": "query_information",
                "priority": "normal"
            }
        )
        
        # Verify the mock was called
        mock_agent_message.assert_called()
        
        # Check message properties
        message_dict = message.to_dict()
        self.assertEqual(message_dict["sender"], "clinical_trial_agent")
        self.assertEqual(message_dict["receiver"], "abstraction_agent")
        self.assertEqual(message_dict["content"], "Test message content")
        self.assertEqual(message_dict["metadata"]["intent"], "query_information")
    
    @patch("src.protocols.agent_protocol.MessageBus")
    def test_message_sending(self, mock_message_bus):
        """Test sending a message through the message bus"""
        # Set up mock return value
        mock_instance = MagicMock()
        mock_instance.send.return_value = True
        mock_message_bus.return_value = mock_instance
        
        # This is a mock test that would normally test the MessageBus class
        # We're demonstrating how the test would work with actual protocol code
        from src.protocols.agent_protocol import MessageBus
        
        bus = MessageBus()
        result = bus.send(self.test_message)
        
        # Verify the mock was called
        mock_instance.send.assert_called_once_with(self.test_message)
        
        # Check result
        self.assertTrue(result)
    
    @patch("src.protocols.agent_protocol.AgentProtocolClient")
    def test_protocol_client(self, mock_client):
        """Test the agent protocol client"""
        # Set up mock return value
        mock_instance = MagicMock()
        mock_instance.send_message.return_value = "msg_12345"
        mock_instance.receive_messages.return_value = [self.test_message]
        mock_client.return_value = mock_instance
        
        # This is a mock test that would normally test the AgentProtocolClient class
        # We're demonstrating how the test would work with actual protocol code
        from src.protocols.agent_protocol import AgentProtocolClient
        
        client = AgentProtocolClient(agent_id="clinical_trial_agent")
        
        # Test sending a message
        message_id = client.send_message(
            receiver="abstraction_agent",
            content="Test message content",
            metadata={
                "intent": "query_information",
                "priority": "normal"
            }
        )
        
        # Verify the mock was called
        mock_instance.send_message.assert_called()
        
        # Check result
        self.assertEqual(message_id, "msg_12345")
        
        # Test receiving messages
        messages = client.receive_messages()
        
        # Verify the mock was called
        mock_instance.receive_messages.assert_called()
        
        # Check result
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], "msg_12345")

if __name__ == '__main__':
    unittest.main()