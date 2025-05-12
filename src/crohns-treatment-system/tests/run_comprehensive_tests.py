#!/usr/bin/env python
"""
Comprehensive Test Runner for HMS System Components

This test runner supports:
1. HMS component integration testing
2. FFI interface testing
3. System monitoring integration
4. Inter-component communication protocol testing
5. Agent conversation testing
"""

import os
import sys
import time
import json
import unittest
import subprocess
import logging
import argparse
import platform
import shutil
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("hms_test_runner")

# Constants
HMS_COMPONENTS = [
    "doc_integration", 
    "genetic_engine", 
    "a2a_integration",
    "ehr_sync", 
    "monitoring", 
    "ffi_bridge"
]

FFI_COMPONENTS = [
    "genetic_engine",
    "monitoring_system", 
    "self_healing"
]

COMMUNICATION_PROTOCOLS = [
    "agent_protocol",
    "component_protocol", 
    "message_bus"
]

class TestReport:
    """Test report container"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = 0
        self.skipped = 0
        self.component_results = {}
        self.failure_details = []
        self.error_details = []
    
    def add_result(self, component: str, result: unittest.TestResult):
        """Add test result for a component"""
        self.total_tests += result.testsRun
        self.passed_tests += result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        self.failed_tests += len(result.failures)
        self.errors += len(result.errors)
        self.skipped += len(result.skipped)
        
        # Store component-specific results
        self.component_results[component] = {
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped)
        }
        
        # Store failure and error details
        for test, failure in result.failures:
            self.failure_details.append({
                "component": component,
                "test": str(test),
                "details": failure
            })
            
        for test, error in result.errors:
            self.error_details.append({
                "component": component,
                "test": str(test),
                "details": error
            })
    
    def finalize(self):
        """Finalize the report"""
        self.end_time = datetime.now()
    
    def get_duration(self) -> str:
        """Get the test duration as a formatted string"""
        if self.end_time is None:
            duration = datetime.now() - self.start_time
        else:
            duration = self.end_time - self.start_time
        
        minutes, seconds = divmod(duration.total_seconds(), 60)
        return f"{int(minutes)}m {int(seconds)}s"
    
    def success(self) -> bool:
        """Return True if all tests passed"""
        return self.failed_tests == 0 and self.errors == 0
    
    def to_json(self) -> Dict[str, Any]:
        """Convert the report to a JSON-serializable dict"""
        return {
            "timestamp": self.start_time.isoformat(),
            "duration": self.get_duration(),
            "summary": {
                "total": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "errors": self.errors,
                "skipped": self.skipped
            },
            "components": self.component_results,
            "failures": self.failure_details,
            "errors": self.error_details
        }
    
    def save_to_file(self, filename: str):
        """Save the report to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.to_json(), f, indent=2)
    
    def print_summary(self):
        """Print a summary of the test results"""
        logger.info("=" * 80)
        logger.info(f"HMS TEST SUMMARY")
        logger.info("-" * 80)
        logger.info(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {self.get_duration()}")
        logger.info(f"Total tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.failed_tests}")
        logger.info(f"Errors: {self.errors}")
        logger.info(f"Skipped: {self.skipped}")
        logger.info("-" * 80)
        
        # Print component results
        logger.info("Component Results:")
        for component, results in self.component_results.items():
            status = "✅ PASS" if results["failed"] == 0 and results["errors"] == 0 else "❌ FAIL"
            logger.info(f"{component}: {status} - {results['passed']}/{results['total']} passed")
        
        logger.info("-" * 80)
        
        # Print failure summary
        if self.failed_tests > 0 or self.errors > 0:
            logger.info("Failure Summary:")
            
            if self.failed_tests > 0:
                logger.info(f"Failures ({self.failed_tests}):")
                for i, failure in enumerate(self.failure_details[:5]):  # Show first 5 failures
                    logger.info(f"  {i+1}. {failure['component']} - {failure['test']}")
                
                if len(self.failure_details) > 5:
                    logger.info(f"  ... and {len(self.failure_details) - 5} more failures")
            
            if self.errors > 0:
                logger.info(f"Errors ({self.errors}):")
                for i, error in enumerate(self.error_details[:5]):  # Show first 5 errors
                    logger.info(f"  {i+1}. {error['component']} - {error['test']}")
                
                if len(self.error_details) > 5:
                    logger.info(f"  ... and {len(self.error_details) - 5} more errors")
        
        logger.info("=" * 80)


class FFITestEnvironment:
    """Environment setup for FFI component testing"""
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.temp_dir = tempfile.mkdtemp(prefix="hms_ffi_test_")
        self.created_dirs = []
        self.mock_executables = {}
    
    def setup(self):
        """Set up the FFI test environment"""
        logger.info("Setting up FFI test environment")
        
        # Create directories for FFI components
        for component in FFI_COMPONENTS:
            component_dir = os.path.join(self.temp_dir, component)
            os.makedirs(component_dir, exist_ok=True)
            self.created_dirs.append(component_dir)
            
            # Create mock executables
            if platform.system() == "Windows":
                mock_exe = os.path.join(component_dir, f"{component}_mock.bat")
                with open(mock_exe, 'w') as f:
                    f.write("@echo off\n")
                    f.write("echo Mock FFI executable for %~n0\n")
                    f.write("echo Input: %*\n")
                    f.write("echo {\"status\": \"success\", \"data\": {\"test\": true}}\n")
            else:
                mock_exe = os.path.join(component_dir, f"{component}_mock.sh")
                with open(mock_exe, 'w') as f:
                    f.write("#!/bin/bash\n")
                    f.write("echo \"Mock FFI executable for $(basename $0)\"\n")
                    f.write("echo \"Input: $@\"\n")
                    f.write("echo '{\"status\": \"success\", \"data\": {\"test\": true}}'\n")
                os.chmod(mock_exe, 0o755)
                
            self.mock_executables[component] = mock_exe
    
    def cleanup(self):
        """Clean up the FFI test environment"""
        logger.info("Cleaning up FFI test environment")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class MonitoringTestEnvironment:
    """Environment setup for monitoring system testing"""
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.temp_dir = tempfile.mkdtemp(prefix="hms_monitoring_test_")
        self.monitor_process = None
        self.monitor_log = os.path.join(self.temp_dir, "monitor.log")
    
    def setup(self):
        """Set up the monitoring test environment"""
        logger.info("Setting up monitoring test environment")
        
        # Create monitoring configuration
        config_file = os.path.join(self.temp_dir, "monitor_config.json")
        with open(config_file, 'w') as f:
            json.dump({
                "interval": 1,
                "components": HMS_COMPONENTS,
                "log_file": self.monitor_log,
                "test_mode": True
            }, f, indent=2)
        
        # Start mock monitoring process
        mock_monitor_script = os.path.join(self.temp_dir, "mock_monitor.py")
        with open(mock_monitor_script, 'w') as f:
            f.write("""#!/usr/bin/env python
import time
import json
import sys
import os
import datetime

config_file = sys.argv[1]
with open(config_file, 'r') as f:
    config = json.load(f)

log_file = config['log_file']
interval = config['interval']

with open(log_file, 'w') as f:
    f.write(f"Mock monitoring started at {datetime.datetime.now().isoformat()}\\n")
    
    for _ in range(10):  # Run for 10 cycles
        status = {
            "timestamp": datetime.datetime.now().isoformat(),
            "components": {}
        }
        
        for component in config['components']:
            status['components'][component] = {
                "status": "healthy",
                "metrics": {
                    "cpu": 0.1,
                    "memory": 10.5,
                    "requests": 5
                }
            }
        
        f.write(json.dumps(status) + "\\n")
        f.flush()
        time.sleep(interval)

with open(log_file, 'a') as f:
    f.write(f"Mock monitoring completed at {datetime.datetime.now().isoformat()}\\n")
""")
            
        # Make executable on Unix systems
        if platform.system() != "Windows":
            os.chmod(mock_monitor_script, 0o755)
        
        # Start monitoring process
        logger.info("Starting mock monitoring process")
        if platform.system() == "Windows":
            self.monitor_process = subprocess.Popen(
                [sys.executable, mock_monitor_script, config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            self.monitor_process = subprocess.Popen(
                [mock_monitor_script, config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
    
    def cleanup(self):
        """Clean up the monitoring test environment"""
        logger.info("Cleaning up monitoring test environment")
        
        # Stop monitoring process if running
        if self.monitor_process:
            logger.info("Stopping mock monitoring process")
            self.monitor_process.terminate()
            try:
                self.monitor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.monitor_process.kill()
        
        # Delete temp directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class AgentConversationTestEnvironment:
    """Environment setup for agent conversation testing"""
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.temp_dir = tempfile.mkdtemp(prefix="hms_agent_test_")
        self.conversation_logs = {}
    
    def setup(self):
        """Set up the agent conversation test environment"""
        logger.info("Setting up agent conversation test environment")
        
        # Create mock conversation logs for testing
        agents = ["clinical_trial_agent", "abstraction_agent", "publication_agent"]
        
        for agent in agents:
            log_file = os.path.join(self.temp_dir, f"{agent}_conversation.jsonl")
            with open(log_file, 'w') as f:
                # Create a sample conversation with 5 messages
                for i in range(5):
                    entry = {
                        "timestamp": (datetime.now().timestamp() + i * 60),
                        "sender": agent if i % 2 == 0 else "system",
                        "message": f"Test message {i+1}",
                        "metadata": {
                            "intent": "test_intent",
                            "entities": ["test_entity_1", "test_entity_2"],
                            "conversation_id": f"conv_{agent}_{int(time.time())}"
                        }
                    }
                    f.write(json.dumps(entry) + "\n")
            
            self.conversation_logs[agent] = log_file
    
    def cleanup(self):
        """Clean up the agent conversation test environment"""
        logger.info("Cleaning up agent conversation test environment")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


def run_test_module(test_dir: str, module_pattern: str, verbosity: int = 1) -> unittest.TestResult:
    """
    Run tests in a specific module and return the result
    
    Args:
        test_dir: Directory containing tests
        module_pattern: Pattern to match test modules
        verbosity: Verbosity level for test output
        
    Returns:
        unittest.TestResult: Test results
    """
    test_suite = unittest.defaultTestLoader.discover(
        start_dir=test_dir,
        pattern=module_pattern
    )
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(test_suite)


def run_component_tests(
    root_dir: str, 
    component: str, 
    verbosity: int = 1,
    include_ffi: bool = False,
    include_monitoring: bool = False
) -> unittest.TestResult:
    """
    Run tests for a specific component
    
    Args:
        root_dir: Root directory of the project
        component: Component name
        verbosity: Verbosity level for test output
        include_ffi: Whether to include FFI tests
        include_monitoring: Whether to include monitoring tests
        
    Returns:
        unittest.TestResult: Test results
    """
    logger.info(f"Running tests for component: {component}")
    
    # Determine test directory
    test_dir = os.path.join(root_dir, "tests")
    component_dir = os.path.join(test_dir, "integration", component)
    
    if not os.path.exists(component_dir):
        logger.warning(f"Test directory not found for component: {component}")
        # Create an empty test result
        result = unittest.TestResult()
        return result
    
    # Run the component tests
    pattern = f"test_*.py"
    logger.info(f"Discovering tests in: {component_dir} with pattern: {pattern}")
    
    return run_test_module(component_dir, pattern, verbosity)


def run_communication_protocol_tests(
    root_dir: str, 
    protocol: str, 
    verbosity: int = 1
) -> unittest.TestResult:
    """
    Run tests for a specific communication protocol
    
    Args:
        root_dir: Root directory of the project
        protocol: Protocol name
        verbosity: Verbosity level for test output
        
    Returns:
        unittest.TestResult: Test results
    """
    logger.info(f"Running tests for protocol: {protocol}")
    
    # Determine test directory
    test_dir = os.path.join(root_dir, "tests", "protocols", protocol)
    
    if not os.path.exists(test_dir):
        logger.warning(f"Test directory not found for protocol: {protocol}")
        # Create an empty test result
        result = unittest.TestResult()
        return result
    
    # Run the protocol tests
    pattern = f"test_*.py"
    logger.info(f"Discovering tests in: {test_dir} with pattern: {pattern}")
    
    return run_test_module(test_dir, pattern, verbosity)


def run_agent_conversation_tests(
    root_dir: str,
    env: AgentConversationTestEnvironment,
    verbosity: int = 1
) -> unittest.TestResult:
    """
    Run tests for agent conversations
    
    Args:
        root_dir: Root directory of the project
        env: Agent conversation test environment
        verbosity: Verbosity level for test output
        
    Returns:
        unittest.TestResult: Test results
    """
    logger.info("Running agent conversation tests")
    
    # Set environment variables for test
    os.environ["HMS_AGENT_LOGS_DIR"] = env.temp_dir
    
    # Determine test directory
    test_dir = os.path.join(root_dir, "tests", "agents")
    
    if not os.path.exists(test_dir):
        logger.warning("Agent conversation test directory not found")
        # Create an empty test result
        result = unittest.TestResult()
        return result
    
    # Run the agent tests
    pattern = f"test_*.py"
    logger.info(f"Discovering tests in: {test_dir} with pattern: {pattern}")
    
    return run_test_module(test_dir, pattern, verbosity)


def run_comprehensive_tests(
    components: Optional[List[str]] = None,
    protocols: Optional[List[str]] = None,
    include_ffi: bool = False,
    include_monitoring: bool = False,
    include_agent_conversations: bool = False,
    parallel: bool = False,
    verbose: bool = False
) -> TestReport:
    """
    Run comprehensive tests for HMS components
    
    Args:
        components: List of components to test (tests all if None)
        protocols: List of protocols to test (tests all if None)
        include_ffi: Whether to include FFI tests
        include_monitoring: Whether to include monitoring tests
        include_agent_conversations: Whether to include agent conversation tests
        parallel: Whether to run tests in parallel
        verbose: Whether to show verbose output
        
    Returns:
        TestReport: Test report
    """
    # Start timer
    start_time = time.time()
    
    # Create test report
    report = TestReport()
    
    # Determine root directory of the project
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Set up environments if needed
    ffi_env = None
    monitor_env = None
    agent_env = None
    
    try:
        # Set up FFI environment if needed
        if include_ffi:
            ffi_env = FFITestEnvironment(root_dir)
            ffi_env.setup()
            # Set environment variable for FFI tests
            os.environ["HMS_FFI_TEST_DIR"] = ffi_env.temp_dir
        
        # Set up monitoring environment if needed
        if include_monitoring:
            monitor_env = MonitoringTestEnvironment(root_dir)
            monitor_env.setup()
            # Set environment variable for monitoring tests
            os.environ["HMS_MONITOR_LOG"] = monitor_env.monitor_log
        
        # Set up agent conversation environment if needed
        if include_agent_conversations:
            agent_env = AgentConversationTestEnvironment(root_dir)
            agent_env.setup()
        
        # Determine components to test
        if components is None:
            components_to_test = HMS_COMPONENTS
        else:
            components_to_test = components
        
        # Determine protocols to test
        if protocols is None:
            protocols_to_test = COMMUNICATION_PROTOCOLS
        else:
            protocols_to_test = protocols
        
        # Set verbosity level
        verbosity = 2 if verbose else 1
        
        # Run component tests
        if parallel and len(components_to_test) > 1:
            # Run component tests in parallel
            with ThreadPoolExecutor(max_workers=min(len(components_to_test), os.cpu_count() or 4)) as executor:
                future_to_component = {
                    executor.submit(
                        run_component_tests, 
                        root_dir, 
                        component, 
                        verbosity,
                        include_ffi,
                        include_monitoring
                    ): component for component in components_to_test
                }
                
                for future in as_completed(future_to_component):
                    component = future_to_component[future]
                    try:
                        result = future.result()
                        report.add_result(component, result)
                    except Exception as e:
                        logger.error(f"Error running tests for component {component}: {e}")
                        # Create an empty result with an error
                        result = unittest.TestResult()
                        result.errors.append((component, str(e)))
                        report.add_result(component, result)
        else:
            # Run component tests sequentially
            for component in components_to_test:
                result = run_component_tests(
                    root_dir, 
                    component, 
                    verbosity,
                    include_ffi,
                    include_monitoring
                )
                report.add_result(component, result)
        
        # Run protocol tests
        for protocol in protocols_to_test:
            result = run_communication_protocol_tests(root_dir, protocol, verbosity)
            report.add_result(f"protocol_{protocol}", result)
        
        # Run agent conversation tests if requested
        if include_agent_conversations and agent_env:
            result = run_agent_conversation_tests(root_dir, agent_env, verbosity)
            report.add_result("agent_conversations", result)
        
        # Finalize the report
        report.finalize()
        
        # Print test summary
        report.print_summary()
        
        # Save test report to file
        report_dir = os.path.join(root_dir, "test-reports")
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(report_dir, f"test_report_{timestamp}.json")
        report.save_to_file(report_file)
        
        logger.info(f"Test report saved to: {report_file}")
        
        return report
        
    finally:
        # Clean up environments
        if ffi_env:
            ffi_env.cleanup()
            # Clear environment variable
            if "HMS_FFI_TEST_DIR" in os.environ:
                del os.environ["HMS_FFI_TEST_DIR"]
        
        if monitor_env:
            monitor_env.cleanup()
            # Clear environment variable
            if "HMS_MONITOR_LOG" in os.environ:
                del os.environ["HMS_MONITOR_LOG"]
        
        if agent_env:
            agent_env.cleanup()
            # Clear environment variable
            if "HMS_AGENT_LOGS_DIR" in os.environ:
                del os.environ["HMS_AGENT_LOGS_DIR"]


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run comprehensive HMS tests")
    
    # Component selection
    parser.add_argument(
        "--components", 
        nargs="+", 
        choices=HMS_COMPONENTS + ["all"],
        help=f"Specific components to test: {', '.join(HMS_COMPONENTS)}, or 'all'"
    )
    
    # Protocol selection
    parser.add_argument(
        "--protocols", 
        nargs="+", 
        choices=COMMUNICATION_PROTOCOLS + ["all"],
        help=f"Specific protocols to test: {', '.join(COMMUNICATION_PROTOCOLS)}, or 'all'"
    )
    
    # FFI, monitoring, and agent conversation options
    parser.add_argument(
        "--ffi", 
        action="store_true", 
        help="Include FFI tests"
    )
    parser.add_argument(
        "--monitoring", 
        action="store_true", 
        help="Include monitoring tests"
    )
    parser.add_argument(
        "--agent-conversations", 
        action="store_true", 
        help="Include agent conversation tests"
    )
    
    # Execution options
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Show verbose output"
    )
    
    # Output options
    parser.add_argument(
        "--report-file", 
        type=str,
        help="Path to save the test report (default: test-reports/test_report_<timestamp>.json)"
    )
    
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    
    # Determine components to test
    components_to_test = None
    if args.components:
        if "all" in args.components:
            components_to_test = HMS_COMPONENTS
        else:
            components_to_test = args.components
    
    # Determine protocols to test
    protocols_to_test = None
    if args.protocols:
        if "all" in args.protocols:
            protocols_to_test = COMMUNICATION_PROTOCOLS
        else:
            protocols_to_test = args.protocols
    
    # Run the tests
    report = run_comprehensive_tests(
        components=components_to_test,
        protocols=protocols_to_test,
        include_ffi=args.ffi,
        include_monitoring=args.monitoring,
        include_agent_conversations=args.agent_conversations,
        parallel=args.parallel,
        verbose=args.verbose
    )
    
    # If a specific report file is requested, save the report there
    if args.report_file:
        report.save_to_file(args.report_file)
        logger.info(f"Test report saved to: {args.report_file}")
    
    # Exit with appropriate code for CI/CD pipelines
    sys.exit(0 if report.success() else 1)