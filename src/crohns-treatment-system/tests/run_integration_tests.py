#!/usr/bin/env python
"""
Test runner for all integration tests
"""

import os
import sys
import unittest
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_tests(test_modules=None, verbose=False):
    """
    Run integration tests and return the test result
    
    Args:
        test_modules: Optional list of test modules to run (e.g., ["doc_integration"])
        verbose: Whether to show verbose output
    
    Returns:
        unittest.TestResult: Test results
    """
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    integration_dir = os.path.join(tests_dir, "integration")
    
    # Start time
    start_time = datetime.now()
    logger.info("Starting integration tests at %s", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Create test suite
    suite = unittest.TestSuite()
    
    if test_modules:
        # Run only specified test modules
        for module in test_modules:
            module_dir = os.path.join(integration_dir, module)
            if os.path.isdir(module_dir):
                logger.info("Discovering tests in module: %s", module)
                module_tests = unittest.defaultTestLoader.discover(
                    start_dir=module_dir,
                    pattern='test_*.py'
                )
                suite.addTest(module_tests)
            else:
                logger.warning("Test module not found: %s", module)
    else:
        # Run all integration tests
        logger.info("Discovering all integration tests")
        
        # First, add tests directly in the integration directory
        suite.addTest(unittest.defaultTestLoader.discover(
            start_dir=integration_dir,
            pattern='test_*.py'
        ))
        
        # Then, add tests in subdirectories
        for item in os.listdir(integration_dir):
            item_path = os.path.join(integration_dir, item)
            if os.path.isdir(item_path) and not item.startswith('__'):
                logger.info("Discovering tests in module: %s", item)
                module_tests = unittest.defaultTestLoader.discover(
                    start_dir=item_path,
                    pattern='test_*.py'
                )
                suite.addTest(module_tests)
    
    # Create a test runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # Run the tests
    result = runner.run(suite)
    
    # End time and duration
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Log test results
    logger.info("Tests completed at %s", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("Total duration: %s", duration)
    logger.info("Ran %d tests", result.testsRun)
    
    if result.wasSuccessful():
        logger.info("All tests PASSED!")
    else:
        logger.error("Tests FAILED: %d errors, %d failures", 
                  len(result.errors), len(result.failures))
        
        if result.errors:
            logger.error("Errors:")
            for test, error in result.errors:
                logger.error("%s: %s", test, error)
                
        if result.failures:
            logger.error("Failures:")
            for test, failure in result.failures:
                logger.error("%s: %s", test, failure)
    
    return result

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run integration tests")
    parser.add_argument(
        "--modules", 
        nargs="+", 
        help="Specific test modules to run (e.g., doc_integration)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Show verbose output"
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    result = run_tests(args.modules, args.verbose)
    
    # Exit with appropriate code for CI/CD pipelines
    sys.exit(0 if result.wasSuccessful() else 1)