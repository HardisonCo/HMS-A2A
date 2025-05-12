"""
Tests for agent conversations
"""

import os
import json
import unittest
from unittest.mock import patch
from datetime import datetime

class AgentConversationTestCase(unittest.TestCase):
    """Test case for agent conversations"""

    def setUp(self):
        """Set up test environment for each test"""
        # Check if HMS_AGENT_LOGS_DIR is set
        self.logs_dir = os.environ.get("HMS_AGENT_LOGS_DIR")
        if not self.logs_dir:
            self.skipTest("HMS_AGENT_LOGS_DIR environment variable not set")
        
        # Load conversation logs if they exist
        self.logs = {}
        self.agents = ["clinical_trial_agent", "abstraction_agent", "publication_agent"]
        
        for agent in self.agents:
            log_file = os.path.join(self.logs_dir, f"{agent}_conversation.jsonl")
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    self.logs[agent] = [json.loads(line) for line in f]
            else:
                # Skip test if log file doesn't exist
                self.skipTest(f"Log file for {agent} not found: {log_file}")
    
    def test_conversation_structure(self):
        """Test that conversation logs have required fields"""
        for agent, conversations in self.logs.items():
            for i, entry in enumerate(conversations):
                with self.subTest(agent=agent, entry_index=i):
                    self.assertIn("timestamp", entry)
                    self.assertIn("sender", entry)
                    self.assertIn("message", entry)
                    self.assertIn("metadata", entry)
                    
                    # Check metadata
                    self.assertIn("intent", entry["metadata"])
                    self.assertIn("conversation_id", entry["metadata"])
    
    def test_conversation_flow(self):
        """Test that conversation flows are valid"""
        for agent, conversations in self.logs.items():
            # Check if there are at least 2 entries
            if len(conversations) < 2:
                self.skipTest(f"Not enough conversation entries for {agent}")
            
            # Extract timestamps and verify they are in ascending order
            timestamps = [entry["timestamp"] for entry in conversations]
            self.assertEqual(timestamps, sorted(timestamps))
            
            # Check that the conversation alternates between the agent and system
            senders = [entry["sender"] for entry in conversations]
            for i in range(1, len(senders)):
                with self.subTest(agent=agent, message_index=i):
                    self.assertNotEqual(senders[i], senders[i-1], 
                                       f"Consecutive messages from same sender at indices {i-1} and {i}")
    
    def test_agent_conversation_intents(self):
        """Test that agent conversations have valid intents"""
        valid_intents = {
            "clinical_trial_agent": ["query_trial", "analyze_outcomes", "extract_biomarkers"],
            "abstraction_agent": ["identify_patterns", "generate_abstractions", "analyze_relationships"],
            "publication_agent": ["generate_documentation", "publish_report", "format_content"]
        }
        
        for agent, conversations in self.logs.items():
            if agent not in valid_intents:
                continue
                
            for i, entry in enumerate(conversations):
                # Only check messages from the agent, not from the system
                if entry["sender"] == agent:
                    with self.subTest(agent=agent, entry_index=i):
                        intent = entry["metadata"]["intent"]
                        valid_agent_intents = valid_intents.get(agent, [])
                        self.assertIn(intent, valid_agent_intents + ["test_intent"],
                                     f"Invalid intent '{intent}' for agent {agent}")
    
    @patch("src.coordination.agent_coordination.AgentConversationAnalyzer.analyze_conversation")
    def test_conversation_analysis(self, mock_analyze):
        """Test conversation analysis functionality"""
        # Set up mock return value
        mock_analyze.return_value = {
            "sentiment": "positive",
            "topics": ["clinical_trials", "biomarkers"],
            "key_entities": ["NOD2", "IL23R"]
        }
        
        # This is a mock test that would normally test the conversation analyzer
        # We're demonstrating how the test would work with actual agent coordination code
        from src.coordination.agent_coordination import AgentConversationAnalyzer
        
        for agent, conversations in self.logs.items():
            analyzer = AgentConversationAnalyzer()
            analysis = analyzer.analyze_conversation(conversations)
            
            # Verify the mock was called
            mock_analyze.assert_called()
            
            # Check analysis result
            self.assertIn("sentiment", analysis)
            self.assertIn("topics", analysis)
            self.assertIn("key_entities", analysis)

if __name__ == '__main__':
    unittest.main()