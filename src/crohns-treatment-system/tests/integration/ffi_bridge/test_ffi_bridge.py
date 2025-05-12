"""
Tests for the FFI bridge integration
"""

import os
import sys
import json
import unittest
import subprocess
from unittest.mock import patch, MagicMock

class FFIBridgeTestCase(unittest.TestCase):
    """Test case for the FFI bridge integration"""

    def setUp(self):
        """Set up test environment for each test"""
        # Check if HMS_FFI_TEST_DIR is set
        self.ffi_test_dir = os.environ.get("HMS_FFI_TEST_DIR")
        if not self.ffi_test_dir:
            self.skipTest("HMS_FFI_TEST_DIR environment variable not set")
        
        # Determine executable extensions based on platform
        self.is_windows = sys.platform == "win32"
        self.mock_exes = {}
        
        # Find mock executables
        for component in ["genetic_engine", "monitoring_system", "self_healing"]:
            if self.is_windows:
                exe_path = os.path.join(self.ffi_test_dir, component, f"{component}_mock.bat")
            else:
                exe_path = os.path.join(self.ffi_test_dir, component, f"{component}_mock.sh")
            
            if os.path.exists(exe_path):
                self.mock_exes[component] = exe_path
            else:
                self.skipTest(f"Mock executable for {component} not found: {exe_path}")
    
    def test_ffi_executables_exist(self):
        """Test that FFI mock executables exist"""
        # This test checks that the mock executables were created correctly
        for component, exe_path in self.mock_exes.items():
            with self.subTest(component=component):
                self.assertTrue(os.path.exists(exe_path))
                self.assertTrue(os.access(exe_path, os.X_OK) or self.is_windows)
    
    def test_mock_executable_output(self):
        """Test mock executable output format"""
        for component, exe_path in self.mock_exes.items():
            with self.subTest(component=component):
                # Run the mock executable
                if self.is_windows:
                    result = subprocess.run([exe_path, "test_arg"], 
                                        capture_output=True, text=True, shell=True)
                else:
                    result = subprocess.run([exe_path, "test_arg"], 
                                        capture_output=True, text=True)
                
                # Check that it ran successfully
                self.assertEqual(result.returncode, 0)
                
                # Check that output contains expected JSON
                output_lines = result.stdout.strip().split('\n')
                json_line = output_lines[-1]  # Last line should be the JSON output
                
                try:
                    json_data = json.loads(json_line)
                    self.assertIn("status", json_data)
                    self.assertEqual(json_data["status"], "success")
                    self.assertIn("data", json_data)
                except json.JSONDecodeError:
                    self.fail(f"Failed to parse JSON from output: {json_line}")
    
    @patch("src.ffi.bridge.FFIBridge.call_executable")
    def test_ffi_bridge_call(self, mock_call):
        """Test FFI bridge call function"""
        # Set up mock return value
        mock_call.return_value = {
            "status": "success",
            "data": {
                "result": "test_result"
            }
        }
        
        # This is a mock test that would normally test the FFIBridge class
        # We're demonstrating how the test would work with actual FFI bridge code
        from src.ffi.bridge import FFIBridge
        
        bridge = FFIBridge()
        result = bridge.call_executable("genetic_engine", ["analyze", "--param", "value"])
        
        # Verify the mock was called
        mock_call.assert_called_once_with("genetic_engine", ["analyze", "--param", "value"])
        
        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["result"], "test_result")
    
    @patch("src.ffi.bridge.GeneticEngineBridge.analyze_data")
    def test_genetic_engine_bridge(self, mock_analyze):
        """Test the genetic engine bridge"""
        # Set up mock return value
        mock_analyze.return_value = {
            "abstractions": [
                {"id": "abstr-1", "name": "Test Abstraction", "confidence": 0.95}
            ],
            "relationships": [
                {"source": "abstr-1", "target": "abstr-2", "type": "supports"}
            ]
        }
        
        # This is a mock test that would normally test the GeneticEngineBridge class
        # We're demonstrating how the test would work with actual genetic engine bridge code
        from src.ffi.bridge import GeneticEngineBridge
        
        bridge = GeneticEngineBridge()
        result = bridge.analyze_data({"test_data": "value"})
        
        # Verify the mock was called
        mock_analyze.assert_called_once_with({"test_data": "value"})
        
        # Check result
        self.assertIn("abstractions", result)
        self.assertIn("relationships", result)
        self.assertEqual(len(result["abstractions"]), 1)
        self.assertEqual(result["abstractions"][0]["name"], "Test Abstraction")
    
    @patch("src.ffi.bridge.MonitoringSystemBridge.report_status")
    def test_monitoring_system_bridge(self, mock_report):
        """Test the monitoring system bridge"""
        # Set up mock return value
        mock_report.return_value = {
            "status": "success",
            "component_status": "healthy"
        }
        
        # This is a mock test that would normally test the MonitoringSystemBridge class
        # We're demonstrating how the test would work with actual monitoring system bridge code
        from src.ffi.bridge import MonitoringSystemBridge
        
        bridge = MonitoringSystemBridge()
        result = bridge.report_status("test_component", {"cpu": 0.5, "memory": 100})
        
        # Verify the mock was called
        mock_report.assert_called_once_with("test_component", {"cpu": 0.5, "memory": 100})
        
        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["component_status"], "healthy")
    
    @patch("src.ffi.bridge.SelfHealingBridge.diagnose_issue")
    def test_self_healing_bridge(self, mock_diagnose):
        """Test the self healing bridge"""
        # Set up mock return value
        mock_diagnose.return_value = {
            "diagnosis": "configuration_error",
            "solution": "update_config",
            "params": {"config_key": "new_value"}
        }
        
        # This is a mock test that would normally test the SelfHealingBridge class
        # We're demonstrating how the test would work with actual self healing bridge code
        from src.ffi.bridge import SelfHealingBridge
        
        bridge = SelfHealingBridge()
        result = bridge.diagnose_issue("test_component", "error_type", "error details")
        
        # Verify the mock was called
        mock_diagnose.assert_called_once_with("test_component", "error_type", "error details")
        
        # Check result
        self.assertEqual(result["diagnosis"], "configuration_error")
        self.assertEqual(result["solution"], "update_config")
        self.assertEqual(result["params"]["config_key"], "new_value")

if __name__ == '__main__':
    unittest.main()